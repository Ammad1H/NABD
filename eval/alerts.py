"""Alert-layer metrics (BUILD-SPEC G10; rule pre-specified in docs/DEVIATIONS.md D3) and the
feed-dropout robustness diagnostic. US-A only; the UAE alert part belongs to the UAE workstream.

Outputs: results/tables/alerts_us.csv, alerts_us_detail.csv, latency_us.csv, dropout_us.csv,
         results/alerts_summary.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from models.data import HUB, QUANTILES, final_truth, load_comparator, season_dates, series_as_of
from models.engine import eeq_member, glm_member, prepare
from models.members import vincent, widen
from models.point import PointCfg
from eval.wis import wis

ROOT = Path(__file__).resolve().parents[1]
FC = ROOT / "results" / "forecasts"
TAB = ROOT / "results" / "tables"
SEASONS = ["2024/25", "2025/26"]
TS = [2.0, 3.0, 5.0]
PRIMARY_T = 3.0
CENSUS_FRAC = 0.6
WINDOW = 4


def populations() -> pd.Series:
    f = pd.read_csv(HUB / "target-data" / "target-hospital-admissions.csv", dtype={"location": str})
    f = f[(f.weekly_rate > 0) & (f.value > 0)]
    return (f.value / f.weekly_rate * 1e5).groupby(f.location).median()


def _nabd_h1_median(R) -> pd.Series:
    p = FC / "NABD-ensemble" / f"{pd.Timestamp(R).date().isoformat()}.csv"
    d = pd.read_csv(p, dtype={"location": str})
    d = d[(d.horizon == 1) & (np.isclose(d.output_type_id, 0.5))]
    return d.set_index("location").value


def _fs_h1_median(R) -> pd.Series | None:
    d = load_comparator("FluSight-ensemble", R)
    if d is None:
        return None
    d = d[(d.horizon == 1) & (np.isclose(d.q, 0.5))]
    return d.set_index("location").value


def alert_metrics() -> tuple[pd.DataFrame, pd.DataFrame]:
    pop = populations()
    ft = final_truth()
    tr = ft.set_index(["location", "target_end_date"]).truth
    rows, detail = [], []
    for season in SEASONS:
        dates = season_dates(season)
        last_obs = {R: series_as_of(R)[0].iloc[:, -1] for R in dates}
        fc = {"NABD-ensemble": {R: _nabd_h1_median(R) for R in dates},
              "FluSight-ensemble": {R: _fs_h1_median(R) for R in dates}}
        for T in TS:
            for loc in pop.index:
                if loc not in last_obs[dates[0]].index:
                    continue
                thr = T * pop[loc] / 1e5
                eligible = last_obs[dates[0]][loc] < thr
                # onset: first week W >= first reference date with truth >= thr at W and W+7
                onset = None
                weeks = pd.date_range(dates[0], dates[-1] + pd.Timedelta(days=21), freq="7D")
                for W in weeks:
                    a, b = tr.get((loc, W), np.nan), tr.get((loc, W + pd.Timedelta(days=7)), np.nan)
                    if a >= thr and b >= thr:
                        onset = W
                        break
                for rule in ["NABD-ensemble", "FluSight-ensemble", "census"]:
                    first = None
                    for R in dates:
                        lo = last_obs[R][loc]
                        if lo >= thr:
                            continue
                        if rule == "census":
                            fire = lo >= CENSUS_FRAC * thr
                        else:
                            m = fc[rule][R]
                            if m is None or loc not in m.index:
                                continue
                            fire = m[loc] >= thr
                        if fire:
                            first = R
                            break
                    lead = (onset - first).days / 7 if (onset is not None and first is not None) else np.nan
                    detail.append({"season": season, "T_per_100k": T, "location": loc, "rule": rule,
                                   "eligible": bool(eligible), "onset_week": onset, "first_alert_R": first, "lead_weeks": lead})
    det = pd.DataFrame(detail)
    for (season, T, rule), g in det[det.eligible].groupby(["season", "T_per_100k", "rule"]):
        on = g[g.onset_week.notna()]
        alerts = g[g.first_alert_R.notna()]
        timely = on[(on.lead_weeks >= 0) & (on.lead_weeks <= WINDOW)]
        premature = on[on.lead_weeks > WINDOW]
        missed = on[on.first_alert_R.isna() | (on.lead_weeks < 0)]
        fa = g[g.onset_week.isna() & g.first_alert_R.notna()]
        ppv_num = alerts[(alerts.lead_weeks >= 0) & (alerts.lead_weeks <= WINDOW)]
        rows.append({"season": season, "T_per_100k": T, "rule": rule,
                     "eligible_loc_seasons": len(g), "ineligible_already_above": int((~det[(det.season == season) & (det.T_per_100k == T) & (det.rule == rule)].eligible).sum()),
                     "onsets": len(on), "sensitivity_lead0to4": len(timely) / len(on) if len(on) else np.nan,
                     "premature_gt4": len(premature) / len(on) if len(on) else np.nan,
                     "missed_or_late": len(missed) / len(on) if len(on) else np.nan,
                     "median_lead_weeks_timely": float(timely.lead_weeks.median()) if len(timely) else np.nan,
                     "false_alarm_loc_seasons": len(fa),
                     "false_alarms_per_loc_season": len(fa) / len(g),
                     "ppv": len(ppv_num) / len(alerts) if len(alerts) else np.nan})
    return pd.DataFrame(rows), det


def latency() -> pd.DataFrame:
    f = pd.read_csv(TAB / "vintage_flags.csv")
    f["input_age_at_issue_days"] = 4 + 7 * f.stale_weeks       # data through R-7, issued Wed R-3
    return pd.DataFrame([{
        "rounds": len(f), "stale_rounds": int((f.stale_weeks > 0).sum()),
        "median_input_age_at_issue_days": float(f.input_age_at_issue_days.median()),
        "max_input_age_at_issue_days": int(f.input_age_at_issue_days.max()),
        "forecast_horizons_after_issue_weeks": "+0.5, +1.5, +2.5, +3.5",
        "note": "US NHSN: week ending Saturday R-7 is available by the Wednesday deadline R-3 (4 days). "
                "Stale rounds = missing hub vintage; model forecasts from older data (PROTOCOL §2.3)."}])


def dropout(drop_weeks=(1, 2)) -> pd.DataFrame:
    cfg = yaml.safe_load((ROOT / "models" / "config.yaml").read_text())
    keys = ["w", "phi", "lam_n", "lam_s", "level", "g_max"]
    g, e, k = cfg["glm"], cfg["eeq"], cfg["ensemble"]["k"]
    gc, ec = PointCfg(**{x: g[x] for x in keys}), PointCfg(**{x: e[x] for x in keys})
    ft = final_truth()
    tmap = {(l, d): v for l, d, v in zip(ft.location, ft.target_end_date, ft.truth)}
    dates = [d for s in SEASONS for d in season_dates(s)]
    res = {d: [0.0, 0.0, 0] for d in (0,) + tuple(drop_weeks)}
    fs_sum = 0.0
    for R in dates:
        fs = load_comparator("FluSight-ensemble", R)
        if fs is None:
            continue
        fsw = fs.pivot_table(index=["location", "horizon"], columns="q", values="value")
        for d in res:
            P = prepare(R, drop_weeks=d)
            q = widen(vincent([glm_member(P, gc, g["c"]), eeq_member(P, ec, e["H"], None, e["strata"])]), k)
            tg = P.target_end_dates()
            for i, loc in enumerate(P.locs):
                for h in range(4):
                    y = tmap.get((loc, tg[h]), np.nan)
                    if not np.isfinite(y) or (loc, h) not in fsw.index:
                        continue
                    res[d][0] += float(wis(q[i, h][None, :], np.array([y]))[0])
                    res[d][2] += 1
                    if d == 0:
                        fs_sum += float(wis(fsw.loc[(loc, h)].to_numpy()[None, :], np.array([y]))[0])
    base = res[0][0]
    return pd.DataFrame([{"dropped_weeks": d, "cells": v[2], "nabd_wis_total": v[0],
                          "rel_to_no_dropout": v[0] / base, "rel_to_FluSight_ensemble": v[0] / fs_sum}
                         for d, v in res.items()])


def main():
    TAB.mkdir(parents=True, exist_ok=True)
    tab, det = alert_metrics()
    tab.to_csv(TAB / "alerts_us.csv", index=False)
    det.to_csv(TAB / "alerts_us_detail.csv", index=False)
    lat = latency(); lat.to_csv(TAB / "latency_us.csv", index=False)
    dr = dropout(); dr.to_csv(TAB / "dropout_us.csv", index=False)
    prim = tab[tab.T_per_100k == PRIMARY_T]
    out = {"rule": "docs/DEVIATIONS.md D3 (pre-specified before test-season forecasts)",
           "primary_T_per_100k": PRIMARY_T,
           "by_rule_pooled": prim.groupby("rule")[["onsets", "sensitivity_lead0to4", "premature_gt4", "missed_or_late",
                                                   "median_lead_weeks_timely", "false_alarm_loc_seasons", "ppv"]].mean().round(3).to_dict(orient="index"),
           "latency": lat.iloc[0].to_dict(), "dropout": dr.round(4).to_dict(orient="records")}
    (ROOT / "results" / "alerts_summary.json").write_text(json.dumps(out, indent=1, default=str))
    print(tab.round(3).to_string()); print(lat.to_string()); print(dr.round(3).to_string())


if __name__ == "__main__":
    main()
