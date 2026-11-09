"""POST HOC (declared in docs/DEVIATIONS.md U6 before computing): UAE NABD-UAE-v1 vs "last year's pattern"
(the seasonal analog), forward-in-time.

Same design, common-cell rule and resampler as the locked UAE-v2 evaluation's forward-in-time sensitivity
(uae/backtest_v2.py). Exploratory: never replaces the GCC primary.

  python3 -m uae.posthoc_analog --cached
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from adapters import flunet
from uae.backtest_v2 import FWD_SEASONS, ROOT, common, fwd_train, rel, run_design
from uae.models import SERIES

OUT = ROOT / "results" / "uae" / "posthoc"
A, B = "NABD-UAE-v1", "seasonal-analog"
MODELS = ["NABD-UAE-v1", "NABD-UAE-v2", "persistence", "seasonal-analog"]
FIRST_SEASON = 2022  # first UAE sentinel season in FluNet; training seasons = test season - FIRST_SEASON


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cached", action="store_true")
    ap.parse_args()
    raw = flunet.load("cached")
    s = flunet.sentinel_series(raw)
    fsc, _ = run_design(raw, s, FWD_SEASONS, fwd_train)
    fcc = common(fsc, MODELS)
    OUT.mkdir(parents=True, exist_ok=True)

    pooled = {series: rel(fcc, A, B, series) for series in SERIES}
    folds = (fcc[fcc.model.isin([A, B])]
             .pivot_table(index=["series", "season"], columns="model", values="wis", aggfunc="mean")
             .reset_index())
    folds["n_training_seasons"] = folds.season - FIRST_SEASON
    folds["ratio_v1_over_analog"] = folds[A] / folds[B]
    folds["v1_better"] = folds[A] < folds[B]
    folds = folds[["series", "season", "n_training_seasons", A, B, "ratio_v1_over_analog", "v1_better"]]
    folds.round(4).to_csv(OUT / "uae_v1_vs_analog_forward_by_fold.csv", index=False)

    by_hist = {}
    for series in SERIES:
        x = fcc[fcc.series == series].copy()
        x["n_hist"] = (x.season - FIRST_SEASON).map(lambda n: "1" if n <= 1 else ">=2")
        by_hist[series] = {h: rel(x[x.n_hist == h], A, B) for h in ["1", ">=2"]}

    summary = dict(label="POST HOC / exploratory (DEVIATIONS U6)", design="forward-in-time, seasons " +
                   ",".join(map(str, FWD_SEASONS)), comparison=f"{A} / {B} (relative WIS; <1 = v1 better)",
                   pooled=pooled, by_training_history=by_hist,
                   folds_v1_better=f"{int(folds.v1_better.sum())}/{len(folds)}")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")

    L = ["# POST HOC: UAE v1 vs last year's pattern (seasonal analog), forward-in-time",
         "",
         "Declared before computing in docs/DEVIATIONS.md U6. **Exploratory, not confirmatory**: per-fold means were "
         "already visible in results/uae/v2/tables/forward_wis_by_season.csv. Relative WIS < 1 means v1 had less error.",
         "",
         "| Series | Pooled v1/analog | 95% CI (date cluster) | 95% CI (moving block L=4) | cells |",
         "|---|---|---|---|---|"]
    for series in SERIES:
        p = pooled[series]
        L.append(f"| {series} | {p['rel_wis']} | {p['ci95_date_cluster'][0]}–{p['ci95_date_cluster'][1]} | "
                 f"{p['ci95_moving_block_L4'][0]}–{p['ci95_moving_block_L4'][1]} | {p['n_cells']} |")
    L += ["", "**By training history** (training seasons available to the forward-in-time fit):", "",
          "| Series | 1 training season | ≥2 training seasons |", "|---|---|---|"]
    for series in SERIES:
        h = by_hist[series]
        f = lambda r: "n/a" if r is None else f"{r['rel_wis']} ({r['ci95_date_cluster'][0]}–{r['ci95_date_cluster'][1]})"
        L.append(f"| {series} | {f(h['1'])} | {f(h['>=2'])} |")
    L += ["", "**Per fold:**", "", "| Series | Test season | Training seasons | v1 WIS | analog WIS | ratio | v1 better |",
          "|---|---|---|---|---|---|---|"]
    for r in folds.itertuples(index=False):
        L.append(f"| {r.series} | {r.season} | {r.n_training_seasons} | {getattr(r, '_3'):.3f} | {getattr(r, '_4'):.3f} | "
                 f"{r.ratio_v1_over_analog:.3f} | {'yes' if r.v1_better else 'no'} |")
    um = folds.groupby("series")[[A, B]].mean()
    L += ["", f"v1 beat the analog in {summary['folds_v1_better']} folds.",
          "Caution: pooling over cells weights seasons by their number of scored cells. The unweighted average of the "
          "per-season mean WIS is " + "; ".join(f"{k} v1 {um.loc[k, A]:.2f} vs analog {um.loc[k, B]:.2f}" for k in um.index)
          + ". The moving-block CIs above include 1.",
          "Reading (post hoc): with one training season the UAE model has almost no history to learn a seasonal shape; "
          "the Gulf test countries had flu history from 2015. This is an explanation, not a tested hypothesis."]
    (OUT / "SUMMARY.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
