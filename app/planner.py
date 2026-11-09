"""Hospital winter planner: SCENARIO arithmetic joining the RSV forecast to beds and the hospital's own workforce.

Everything here is a labelled SCENARIO. No Abu Dhabi hospital data are used. The only sourced defaults are:
- 2,189 RSV admissions of children <=5 at Tawam Hospital over 2018-2022 (research/burden.md), i.e. 438/year;
- length of stay 4-6 days (research/positioning.md [S1][S3]);
- US$2,241 median RSV hospitalisation cost, Dubai insurance claims (research/positioning.md [S3]);
- AED peg 3.6725 per US$ (UAE Central Bank fixed rate).
Bed counts, nursing headcount, shifts and the staff-absence rate are the HOSPITAL'S OWN inputs (or the
SIMULATED secure-aggregation module); no absence statistic is presented as a fact.

Scaling rule (the same one the bed-days scenario uses, shown on the page):
    weekly admissions_q = annual admissions x positivity_q / sum of weekly positivity over an average season
    weekly absence rate_q = average weekly absence rate x positivity_q / average weekly positivity
so a week at average positivity reproduces the hospital's own averages.
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor" / "nabd_v2_kit"
for _p in (ROOT, VENDOR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from nabd_kit.quantiles import FLUSIGHT_LEVELS, exceedance_prob  # noqa: E402

from app import data_io  # noqa: E402

AED_PER_USD = 3.6725
SOURCED_DEFAULTS = {
    "annual_admissions": 438,      # Tawam 2,189 / 5 years
    "los_days": 4.0,               # conservative end of 4-6 days
    "cost_usd": 2241,              # Dubai claims median
}


def _wide(fc_rsv: pd.DataFrame) -> pd.DataFrame:
    w = fc_rsv.pivot_table(index="target_end_date", columns="q", values="value").sort_index()
    w.columns = [round(float(c), 3) for c in w.columns]
    return w


def season_reference(observed: pd.DataFrame) -> tuple[float, int]:
    """(sum of weekly RSV positivity over an average complete season, number of complete seasons)."""
    sf = data_io.season_frame(observed, "rsv")
    cur = sf.season.max()
    complete = sf[sf.season != cur].groupby("season").value.sum()
    return float(complete.mean()), int(len(complete))


def winter_plan(observed: pd.DataFrame, fc_rsv: pd.DataFrame, issue: dt.date, *, annual_admissions: float,
                los_days: float, beds: int, nurses: int, absence_rate_avg: float | None,
                shifts_per_nurse_week: float, spare_shifts_week: float, cost_usd: float,
                meta: dict | None = None) -> pd.DataFrame:
    """One row per future target week with 10% / 50% / 90% scenario values. All numbers are SCENARIO."""
    season_sum, n_seasons = season_reference(observed)
    avg_pos = season_sum / 52.0
    w = _wide(fc_rsv)
    rows = []
    for ted, r in w.iterrows():
        d = pd.Timestamp(ted).date()
        if data_io.horizon_weeks(d, issue) <= 0:
            continue
        q = {k: float(r[k]) for k in (0.1, 0.5, 0.9)}
        adm = {k: annual_admissions * v / season_sum for k, v in q.items()}
        bed_days = {k: v * los_days for k, v in adm.items()}
        occ = {k: v / 7.0 for k, v in bed_days.items()}
        row = {
            "target_end_date": d,
            "horizon": data_io.display_horizon(d, issue, meta),
            "RSV positivity forecast % (10–50–90)": f"{q[0.1]:.1f} – {q[0.5]:.1f} – {q[0.9]:.1f}",
            "RSV admissions / week": f"{adm[0.1]:.0f} – {adm[0.5]:.0f} – {adm[0.9]:.0f}",
            "RSV beds occupied (avg)": f"{occ[0.1]:.0f} – {occ[0.5]:.0f} – {occ[0.9]:.0f}",
            "% of paediatric respiratory beds": (f"{100 * occ[0.1] / beds:.0f}% – {100 * occ[0.5] / beds:.0f}% – "
                                                 f"{100 * occ[0.9] / beds:.0f}%") if beds else "n/a",
            "cost of RSV admissions (AED)": (f"{adm[0.1] * cost_usd * AED_PER_USD:,.0f} – "
                                             f"{adm[0.5] * cost_usd * AED_PER_USD:,.0f} – "
                                             f"{adm[0.9] * cost_usd * AED_PER_USD:,.0f}"),
        }
        if absence_rate_avg is not None and nurses:
            rate = {k: absence_rate_avg * v / avg_pos for k, v in q.items()}
            absent = {k: nurses * v for k, v in rate.items()}
            shifts = {k: v * shifts_per_nurse_week for k, v in absent.items()}
            gap = {k: v - spare_shifts_week for k, v in shifts.items()}
            # gap > 0  <=>  positivity > p_star (gap is increasing in positivity)
            denom = nurses * absence_rate_avg * shifts_per_nurse_week / avg_pos
            p_star = spare_shifts_week / denom if denom > 0 else np.inf
            qvec = np.array([float(r[round(float(x), 3)]) for x in FLUSIGHT_LEVELS])
            p_gap = float(exceedance_prob(qvec, FLUSIGHT_LEVELS, p_star)[0]) if np.isfinite(p_star) else 0.0
            row.update({
                "nurses absent (respiratory)": f"{absent[0.1]:.1f} – {absent[0.5]:.1f} – {absent[0.9]:.1f}",
                "nurse shifts at risk / week": f"{shifts[0.1]:.0f} – {shifts[0.5]:.0f} – {shifts[0.9]:.0f}",
                "net roster gap (shifts)": f"{gap[0.1]:+.0f} – {gap[0.5]:+.0f} – {gap[0.9]:+.0f}",
                "P(roster gap > 0)": _fmt_p(p_gap),
            })
        rows.append(row)
    out = pd.DataFrame(rows)
    out.attrs.update(season_sum=season_sum, n_seasons=n_seasons, avg_pos=avg_pos)
    return out


def simulated_absence_rate(table: pd.DataFrame) -> float | None:
    """Weekly respiratory absence rate from the SIMULATED secure-aggregation module (released cells only)."""
    rel = table[table.released]
    if rel.empty or rel.staff_total.sum() == 0:
        return None
    return float(rel.resp_absent_total.sum() / rel.staff_total.sum())


def _fmt_p(p: float) -> str:
    if p <= 0.01 + 1e-9:
        return "<1%"
    if p >= 0.99 - 1e-9:
        return ">99%"
    return f"{p:.0%}"
