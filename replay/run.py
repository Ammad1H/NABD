"""Run the declared decision replay (DEVIATIONS V1) and write results/replay/.

  python3 -m replay.run                         # replays the three frozen models
  python3 -m replay.run --extra path/to/model.csv[.gz] [--name NABD-Pool]   # also replay another model
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from replay import engine as E

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "replay"
MAIN = "NABD"
COMPARATORS = ["past-season-pattern", "persistence"]
SER = {"wk flu pos pct": "flu", "wk rsv pos pct": "rsv"}
GCC = ["OMN", "QAT", "SAU"]
AED_PER_BED_DAY = 560 * 3.6725          # US$560 (Dubai claims, median US$2,241 over about 4 d) x peg


def thresholds(F, kind):
    cs = F[["location", "target", "season"]].drop_duplicates()
    if kind == "playbook":
        cs["T"] = cs.target.map(E.PLAYBOOK_T)
        return cs
    th = pd.read_csv(OUT / "thresholds_country_q75.csv")
    th["target"] = th.series.map({v: k for k, v in SER.items()})
    return cs.merge(th[["location", "target", "season", "T"]], on=["location", "target", "season"])


def uae_surge_weeks(T=10.0):
    """Weeks per complete season with UAE sentinel RSV positivity > T (V1h input n). From data/raw/flunet_are.csv."""
    from uae import gcc
    raw = pd.read_csv(ROOT / "data" / "raw" / "flunet_are.csv")
    raw["COUNTRY_CODE"] = "ARE"
    s = gcc.weekly_series(gcc.tidy(raw), "ARE", "SENTINEL")
    s = s[(s.specimens >= 20)]
    s["pct"] = s.rsv_pos / s.specimens * 100
    n = s[s.season.between(2022, 2025)].groupby("season").apply(lambda g: int((g.pct > T).sum()))
    return {int(k): int(v) for k, v in n.items()}


def aed_scenario(diff: dict) -> dict:
    """V1h: Tawam-sized paediatric unit, RSV. Scale of resource mis-planned, NOT a cash saving."""
    n = uae_surge_weeks()
    nv = sorted(n.values())
    cases = {"low": dict(AL=1160, s=0.7, n=max(nv)), "central": dict(AL=1970, s=0.8, n=float(np.mean(nv))),
             "high": dict(AL=3822, s=0.9, n=min(nv))}
    avoided = {"low": -diff["ci95"][1], "central": -diff["diff_per_season"], "high": -diff["ci95"][0]}
    out = dict(inputs=dict(uae_rsv_weeks_over_10pct_by_season=n, aed_per_bed_day=round(AED_PER_BED_DAY),
                           cases=cases), mismatch_weeks_avoided_per_season=avoided, by_case={})
    for c, v in cases.items():
        per_week = v["AL"] * v["s"] / v["n"] - v["AL"] * (1 - v["s"]) / (52 - v["n"])
        bd = avoided[c] * per_week
        out["by_case"][c] = dict(misplanned_bed_days_per_mismatch_week=round(per_week, 1),
                                 bed_days_per_season=round(bd), aed_per_season=int(round(bd * AED_PER_BED_DAY, -3)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extra", nargs="*", default=[])
    a = ap.parse_args()
    paths = sorted((OUT / "forecasts").glob("*.csv.gz")) + [Path(p) for p in a.extra]
    F = E.load_forecasts(paths)
    truth = pd.read_csv(OUT / "truth.csv")
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    summ = dict(status="POST HOC, EXPLORATORY (DEVIATIONS V1). Scenario, not a confirmatory result.",
                rule=dict(p_star=E.P_STAR, primary_horizon="+2 wk after issue (target week L+3)",
                          playbook_T=E.PLAYBOOK_T), results={})
    weekly_all = []
    for kind in ["playbook", "country_q75"]:
        Ex = E.exceedance(F, thresholds(F, kind))
        for p in ([0.30, 0.20, 0.50] if kind == "playbook" else [0.30]):
            D = E.add_references(E.decisions(Ex, truth, p))
            D["threshold_kind"], D["p_star"] = kind, p
            S = E.per_season(D)
            S["threshold_kind"], S["p_star"] = kind, p
            S.to_csv(OUT / "tables" / f"per_season_{kind}_p{int(p*100)}.csv", index=False)
            if p == 0.30:
                weekly_all.append(D)
            for scope, locs in [("GCC", GCC), ("UAE_posthoc_n2", ["ARE"])]:
                for tgt, ser in SER.items():
                    for h in sorted(S.horizon.unique()):
                        s = S[S.location.isin(locs) & (S.target == tgt) & (S.horizon == h)]
                        if s.empty:
                            continue
                        key = f"{scope}|{ser}|{kind}|p{int(p*100)}|h{h}"
                        tot = s.groupby("model")[["weeks", "surge_weeks", "missed", "wasted", "mismatch"]].sum()
                        r = dict(n_country_seasons=int(s[s.model == MAIN].shape[0]), totals=tot.to_dict("index"),
                                 brier=s.groupby("model").brier.mean().round(4).to_dict())
                        for c in COMPARATORS:
                            for col in ["mismatch", "missed", "wasted"]:
                                r[f"{MAIN}_minus_{c}_{col}"] = E.paired_diff(s, MAIN, c, col)
                        extra = [m for m in s.model.unique() if m not in
                                 [MAIN, *COMPARATORS, "always-roster", "never-roster", "perfect-foresight"]]
                        for m in extra:
                            r[f"{m}_minus_{MAIN}_mismatch"] = E.paired_diff(s, m, MAIN, "mismatch")
                        summ["results"][key] = r
    W = pd.concat(weekly_all, ignore_index=True)
    W.round(4).to_csv(OUT / "tables" / "weekly_decisions.csv.gz", index=False)
    prim = summ["results"].get(f"GCC|rsv|playbook|p30|h{E.PRIMARY_H}")
    if prim and prim.get(f"{MAIN}_minus_past-season-pattern_mismatch"):
        summ["aed_scenario_rsv_tawam_sized_unit"] = aed_scenario(prim[f"{MAIN}_minus_past-season-pattern_mismatch"])
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1, default=int))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if "mismatch" in kk or kk == "totals"}
                      for k, v in summ["results"].items() if k.endswith("p30|h2")}, indent=1, default=int))
    print(json.dumps(summ.get("aed_scenario_rsv_tawam_sized_unit"), indent=1, default=int))


if __name__ == "__main__":
    main()
