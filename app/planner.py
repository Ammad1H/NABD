"""Hospital winter planner: SCENARIO arithmetic joining the RSV forecast to beds and the hospital's own workforce.

Everything here is a labelled SCENARIO. No Abu Dhabi hospital data are used. The only sourced defaults are:
- 2,189 RSV admissions of children <=5 at Tawam Hospital over 2018-2022 (research/burden.md), i.e. 438/year;
- length of stay 4-6 days (research/positioning.md [S1][S3]);
- US$2,241 median RSV hospitalisation cost, Dubai insurance claims (research/positioning.md [S3]);
- AED peg 3.6725 per US$ (UAE Central Bank fixed rate).
Bed counts, nursing headcount, shifts and the staff-absence rate are the HOSPITAL'S OWN inputs (or the
SIMULATED secure-aggregation module); no absence statistic is presented as a fact.

Scaling rules (shown on the page):
    weekly RSV admissions_q = annual admissions x RSV positivity_q / sum of weekly RSV positivity over an average season
    weekly absence rate_q   = average weekly absence rate x driver index_q
where the absence DRIVER INDEX is chosen by the user (default "both"):
    "rsv":  RSV positivity_q / average weekly RSV positivity
    "flu":  flu positivity_q / average weekly flu positivity
    "both": 0.5 x RSV index_q + 0.5 x flu index_q  (equal weights; quantiles averaged level by level, which assumes
            the two move together, so the 10-90% range is wider than if they were independent)
Adult staff respiratory absence is plausibly driven more by influenza than by paediatric RSV, so "rsv" alone is
offered but not the default. A week at average activity reproduces the hospital's own averages.
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


def season_reference(observed: pd.DataFrame, series: str = "rsv") -> tuple[float, int]:
    """(sum of weekly positivity over an average complete season, number of complete seasons) for `series`."""
    sf = data_io.season_frame(observed, series)
    cur = sf.season.max()
    complete = sf[sf.season != cur].groupby("season").value.sum()
    return float(complete.mean()), int(len(complete))


DRIVERS = ("both", "flu", "rsv")
DRIVER_LABEL = {"both": "flu and RSV (equal weight)", "flu": "influenza", "rsv": "RSV"}


def _index_matrix(observed: pd.DataFrame, fc_rsv: pd.DataFrame, fc_flu: pd.DataFrame | None,
                  driver: str) -> pd.DataFrame:
    """Absence driver index (positivity / its seasonal average) per target week × FluSight level."""
    if driver not in DRIVERS:
        raise ValueError(f"absence_driver must be one of {DRIVERS}")
    parts = []
    if driver in ("rsv", "both"):
        s, _ = season_reference(observed, "rsv")
        parts.append(_wide(fc_rsv) / (s / 52.0))
    if driver in ("flu", "both"):
        if fc_flu is None or fc_flu.empty:
            raise ValueError("absence_driver '%s' needs the influenza forecast (fc_flu)" % driver)
        s, _ = season_reference(observed, "flu")
        parts.append(_wide(fc_flu) / (s / 52.0))
    if len(parts) == 1:
        return parts[0]
    common = parts[0].index.intersection(parts[1].index)
    return 0.5 * parts[0].loc[common] + 0.5 * parts[1].loc[common]


def winter_plan(observed: pd.DataFrame, fc_rsv: pd.DataFrame, issue: dt.date, *, annual_admissions: float,
                los_days: float, beds: int, nurses: int, absence_rate_avg: float | None,
                shifts_per_nurse_week: float, spare_shifts_week: float, cost_usd: float,
                meta: dict | None = None, fc_flu: pd.DataFrame | None = None,
                absence_driver: str = "both") -> pd.DataFrame:
    """One row per future target week with 10% / 50% / 90% scenario values. All numbers are SCENARIO.

    Beds and cost follow the RSV forecast (paediatric RSV admissions). Staff absence follows the chosen driver
    index (default "both", which needs `fc_flu`)."""
    season_sum, n_seasons = season_reference(observed, "rsv")
    avg_pos = season_sum / 52.0
    w = _wide(fc_rsv)
    idx = None
    if absence_rate_avg is not None and nurses:
        idx = _index_matrix(observed, fc_rsv, fc_flu, absence_driver)
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
            "week": data_io.week_ending_label(d),
            "weeks after issue": data_io.horizon_label(d, issue),
            "RSV positivity forecast % (10–50–90)": f"{q[0.1]:.1f} – {q[0.5]:.1f} – {q[0.9]:.1f}",
            "RSV admissions / week": f"{adm[0.1]:.0f} – {adm[0.5]:.0f} – {adm[0.9]:.0f}",
            "RSV beds occupied (avg)": f"{occ[0.1]:.0f} – {occ[0.5]:.0f} – {occ[0.9]:.0f}",
            "% of paediatric respiratory beds": (f"{100 * occ[0.1] / beds:.0f}% – {100 * occ[0.5] / beds:.0f}% – "
                                                 f"{100 * occ[0.9] / beds:.0f}%") if beds else "n/a",
            "cost of RSV admissions (AED)": (f"{adm[0.1] * cost_usd * AED_PER_USD:,.0f} – "
                                             f"{adm[0.5] * cost_usd * AED_PER_USD:,.0f} – "
                                             f"{adm[0.9] * cost_usd * AED_PER_USD:,.0f}"),
        }
        if idx is not None and ted in idx.index:
            ir = idx.loc[ted]
            iq = {k: float(ir[k]) for k in (0.1, 0.5, 0.9)}
            wf = workforce_scenario(iq, nurses=nurses, absence_rate_avg=absence_rate_avg,
                                    shifts_per_nurse_week=shifts_per_nurse_week, spare_shifts_week=spare_shifts_week)
            ivec = np.array([float(ir[round(float(x), 3)]) for x in FLUSIGHT_LEVELS])
            p_gap = (float(exceedance_prob(ivec, FLUSIGHT_LEVELS, wf["index_star"])[0])
                     if np.isfinite(wf["index_star"]) else 0.0)
            row.update({
                WF_COLS[0]: " – ".join(f"{wf['absent'][k]:.1f}" for k in (0.1, 0.5, 0.9)),
                WF_COLS[1]: " – ".join(f"{wf['shifts'][k]:.0f}" for k in (0.1, 0.5, 0.9)),
                WF_COLS[2]: " – ".join(f"{wf['gap'][k]:.0f}" for k in (0.1, 0.5, 0.9)),
                WF_COLS[3]: _fmt_p(p_gap),
            })
            for k, lab in ((0.1, "q10"), (0.5, "q50"), (0.9, "q90")):  # numeric copies for tests / export
                row[f"_shifts_{lab}"] = wf["shifts"][k]
                row[f"_gap_{lab}"] = wf["gap"][k]
                row[f"_index_{lab}"] = iq[k]
            row["_p_gap"] = p_gap
        rows.append(row)
    out = pd.DataFrame(rows)
    out.attrs.update(season_sum=season_sum, n_seasons=n_seasons, avg_pos=avg_pos,
                     absence_driver=absence_driver if idx is not None else None)
    return out


WF_COLS = ["expected absent nurses (respiratory)", "nurse shifts at risk / week",
           "net roster gap after bank/float (shifts)", "P(roster gap > 0)"]
DEMAND_COLS = ["week", "weeks after issue", "RSV positivity forecast % (10–50–90)", "RSV admissions / week",
               "RSV beds occupied (avg)", "% of paediatric respiratory beds", "cost of RSV admissions (AED)"]


def workforce_scenario(index_q: dict, *, nurses: int, absence_rate_avg: float,
                       shifts_per_nurse_week: float, spare_shifts_week: float) -> dict:
    """SCENARIO arithmetic (assumptions shown on the page): absence rate = average rate × driver index
    (index 1 = an average week); shifts at risk = absent nurses × shifts per nurse;
    net gap = max(shifts at risk − bank/float shifts, 0)."""
    rate = {k: absence_rate_avg * v for k, v in index_q.items()}
    absent = {k: nurses * v for k, v in rate.items()}
    shifts = {k: v * shifts_per_nurse_week for k, v in absent.items()}
    gap = {k: max(v - spare_shifts_week, 0.0) for k, v in shifts.items()}
    denom = nurses * absence_rate_avg * shifts_per_nurse_week  # gap > 0  <=>  index > index_star
    index_star = spare_shifts_week / denom if denom > 0 else np.inf
    return {"absent": absent, "shifts": shifts, "gap": gap, "index_star": index_star}


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
