"""UAE leave-one-season-out backtest (sentinel flu and RSV positivity).

Run:  python3 -m uae.backtest --cached          (uses data/raw/flunet_are.csv)
      python3 -m uae.backtest --fetch           (live WHO xMart; run locally)

Test seasons: 2022/23, 2023/24, 2024/25, 2025/26 (season Y = ISO wk27 of Y .. wk26 of Y+1), n = 4.
For each test season, models are trained on ALL other seasons (incl. the partial 2021/22 and the partial
current 2026/27 season up to its last published week). This is leave-one-season-out, not a forward-in-time
test, and is stated as such. Origins: every week L in the test season whose four targets L+1..L+4 lie in the
same season. Issue date is taken as week_end(L) + 11 days (simulated WHO lag); reference_date (Sunday) is
week_end(L) + 14 days, so FluSight-style horizons are -1 (nowcast), 0, 1, 2.

Outputs
  results/uae/forecasts/<model>/<reference_date>.csv   (interface-contract format)
  results/uae/tables/scores_long.csv, wis_by_model.csv, wis_by_season.csv, coverage.csv, rsv_peak_week.csv
  results/uae/figures/uae_backtest.png
  results/uae/summary.json, results/uae/SUMMARY.md
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from adapters import flunet
from uae.models import MODELS, QUANTILES, SERIES, H, prepare, expit
from uae.scoring import wis, covered

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "uae"
TEST_SEASONS = [2022, 2023, 2024, 2025]
# Horizon h = target week L+2+h, where L is the last published week (h = -1 is L+1, the nowcast). In the live
# product these targets are labelled by week-ending date and "nowcast / +1 / +2 / +3 wk after issue"
# (7-day publication lag); skill here is measured at a conservative 11-day lag (docs/DEVIATIONS.md C8).
HORIZON_LABEL = {-1: "L+1 (nowcast)", 0: "L+2", 1: "L+3", 2: "L+4"}


def run(mode="cached", write_forecasts=True):
    s = flunet.sentinel_series(flunet.load(mode))
    all_seasons = sorted(s.season.dropna().unique().astype(int))
    rows, fc_rows = [], []
    for key, (_, target_name) in SERIES.items():
        d = prepare(s, key)
        for test in TEST_SEASONS:
            train = [x for x in all_seasons if x != test]
            models = [M(d, train) for M in MODELS]
            idx = d.index[(d.season == test)]
            for i in idx:
                if i + 4 >= len(d) or d.season.iloc[i + 4] != test:
                    continue
                L_end = d.week_end.iloc[i]
                ref = (L_end + pd.Timedelta(days=14)).date()
                for m in models:
                    pq = m.predict(i)
                    for h in H:
                        if pq.get(h) is None:
                            continue
                        vals = 100 * expit(np.sort(pq[h]))
                        tgt_end = d.week_end.iloc[i + h]
                        fh = h - 2  # FluSight-style horizon relative to reference_date
                        y_obs = d.pos.iloc[i + h] / d.specimens.iloc[i + h] * 100 if not np.isnan(d.y.iloc[i + h]) else np.nan
                        for q, v in zip(QUANTILES, vals):
                            fc_rows.append((m.name, str(ref), target_name, fh, str(tgt_end.date()), "ARE",
                                            "quantile", q, round(float(v), 4)))
                        if not np.isnan(y_obs):
                            rows.append(dict(model=m.name, series=key, season=test, reference_date=str(ref),
                                             horizon=fh, target_end_date=str(tgt_end.date()), obs=y_obs,
                                             median=float(vals[QUANTILES.index(0.5)]),
                                             wis=wis(QUANTILES, vals, y_obs),
                                             cov50=covered(QUANTILES, vals, y_obs, 0.5),
                                             cov95=covered(QUANTILES, vals, y_obs, 0.95),
                                             specimens=float(d.specimens.iloc[i + h])))
    scores = pd.DataFrame(rows)
    fc = pd.DataFrame(fc_rows, columns=["model", "reference_date", "target", "horizon", "target_end_date", "location",
                                        "output_type", "output_type_id", "value"])
    if write_forecasts:
        for (m, ref), g in fc.groupby(["model", "reference_date"]):
            p = OUT / "forecasts" / m
            p.mkdir(parents=True, exist_ok=True)
            g[["reference_date", "target", "horizon", "target_end_date", "location", "output_type", "output_type_id",
               "value", "model"]].to_csv(p / f"{ref}.csv", index=False)
    return s, scores, fc


def bootstrap_rel(scores, model, ref_model, series, n_boot=2000, seed=20261108):
    """Relative WIS (sum model / sum ref) with block bootstrap over reference dates."""
    a = scores[(scores.model == model) & (scores.series == series)]
    b = scores[(scores.model == ref_model) & (scores.series == series)]
    m = a.merge(b, on=["season", "reference_date", "horizon"], suffixes=("_a", "_b"))
    g = m.groupby("reference_date")[["wis_a", "wis_b"]].sum()
    rel = g.wis_a.sum() / g.wis_b.sum()
    rng = np.random.default_rng(seed)
    ids = np.arange(len(g))
    boots = []
    for _ in range(n_boot):
        k = rng.choice(ids, len(ids), replace=True)
        boots.append(g.wis_a.values[k].sum() / g.wis_b.values[k].sum())
    lo, hi = np.quantile(boots, [0.025, 0.975])
    return float(rel), float(lo), float(hi), int(len(g))


def peak_week_error(s, fc, scores):
    """RSV peak timing: for origins 1-4 weeks before the observed peak, predicted peak week =
    argmax over (observed positivity up to L, model medians for L+1..L+4). Error in weeks, absolute."""
    out = []
    d = prepare(s, "rsv")
    d["pct"] = d.pos / d.specimens * 100
    med = fc[(fc.target == "wk rsv pos pct sentinel") & (fc.output_type_id == 0.5)]
    for test in TEST_SEASONS:
        ds = d[d.season == test].dropna(subset=["pct"])
        pk_i = ds.pct.idxmax()
        pk_week = d.week_end.loc[pk_i]
        for lead in (1, 2, 3, 4):
            i = pk_i - lead
            L_end = d.week_end.iloc[i]
            ref = str((L_end + pd.Timedelta(days=14)).date())
            obs = ds[ds.week_end <= L_end].set_index("week_end").pct
            for mname, g in med[med.reference_date == ref].groupby("model"):
                path = pd.concat([obs, g.set_index(pd.to_datetime(g.target_end_date)).value])
                pred_pk = path.idxmax()
                out.append(dict(model=mname, season=test, weeks_before_peak=lead,
                                true_peak=str(pk_week.date()), pred_peak=str(pred_pk.date()),
                                abs_err_wk=abs((pred_pk - pk_week).days) / 7))
    return pd.DataFrame(out)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--cached", action="store_true")
    g.add_argument("--fetch", action="store_true")
    ap.add_argument("--no-forecast-files", action="store_true")
    a = ap.parse_args()
    s, scores, fc = run("fetch" if a.fetch else "cached", write_forecasts=not a.no_forecast_files)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    scores.to_csv(OUT / "tables" / "scores_long.csv", index=False)
    # audit m18: per-model / per-season / per-horizon tables on cells common to all models
    k = ["series", "season", "reference_date", "horizon"]
    nmod = scores.groupby(k).model.nunique()
    keep = nmod[nmod == scores.model.nunique()].index
    scores = scores.set_index(k).loc[keep].reset_index()

    by_model = scores.groupby(["series", "model"]).agg(mean_wis=("wis", "mean"), n=("wis", "size"),
                                                         cov50=("cov50", "mean"), cov95=("cov95", "mean")).reset_index()
    by_model.to_csv(OUT / "tables" / "wis_by_model.csv", index=False)
    by_season = scores.pivot_table(index=["series", "season"], columns="model", values="wis", aggfunc="mean").reset_index()
    by_season.to_csv(OUT / "tables" / "wis_by_season.csv", index=False)
    by_h = scores.pivot_table(index=["series", "horizon"], columns="model", values="wis", aggfunc="mean").reset_index()
    by_h.to_csv(OUT / "tables" / "wis_by_horizon.csv", index=False)
    cov = scores.groupby(["series", "model", "horizon"])[["cov50", "cov95"]].mean().reset_index()
    cov.to_csv(OUT / "tables" / "coverage.csv", index=False)
    pk = peak_week_error(s, fc, scores)
    pk.to_csv(OUT / "tables" / "rsv_peak_week.csv", index=False)

    rel = {}
    for series in SERIES:
        for ref in ["persistence", "seasonal-analog"]:
            r, lo, hi, n = bootstrap_rel(scores, "NABD-UAE-v1", ref, series)
            rel[f"{series}_vs_{ref}"] = dict(rel_wis=round(r, 3), ci95=[round(lo, 3), round(hi, 3)], n_reference_dates=n)
    rel_ex22 = {}
    sc22 = scores[scores.season != 2022]
    for series in SERIES:
        for ref in ["persistence", "seasonal-analog"]:
            r, lo, hi, n = bootstrap_rel(sc22, "NABD-UAE-v1", ref, series)
            rel_ex22[f"{series}_vs_{ref}"] = dict(rel_wis=round(r, 3), ci95=[round(lo, 3), round(hi, 3)], n_reference_dates=n)

    # season-level wins
    wins = {}
    for series in SERIES:
        bs = by_season[by_season.series == series]
        wins[series] = {ref: int((bs["NABD-UAE-v1"] < bs[ref]).sum()) for ref in ["persistence", "seasonal-analog"]}

    pk_sum = pk.groupby("model").abs_err_wk.mean().round(2).to_dict() if len(pk) else {}
    last = s.dropna(subset=["specimens"]).iloc[-1]
    summary = dict(
        generated_from="data/raw/flunet_are.csv" if not a.fetch else "WHO xMart live",
        latest_sentinel_week=f"{int(last.iso_year)}-W{int(last.iso_week):02d}",
        test_seasons=["2022/23", "2023/24", "2024/25", "2025/26"], n_seasons=4,
        design="leave-one-season-out; 1-week simulated publication lag; horizons -1(nowcast),0,1,2 rel. reference date",
        rel_wis_nabd=rel, rel_wis_nabd_excluding_2022_23=rel_ex22,
        seasons_nabd_better=wins,
        mean_wis=by_model.round(3).to_dict(orient="records"),
        rsv_peak_week_mae_wk=pk_sum,
        caveats=["n=4 test seasons; CIs reflect week-to-week variability only, not between-season uncertainty",
                 "2022/23 sentinel volumes are low (tens of specimens/week early in 2022)",
                 "LOSO uses later seasons for training when testing earlier ones (not forward-in-time)",
                 "Revisions to FluNet values are not reproduced (no vintages available)"],
    )
    summary["label"] = "RETROSPECTIVE, design-stage, NOT pre-registered (docs/DEVIATIONS.md U1); common cells (U4)"
    sj = OUT / "summary.json"
    if sj.exists():  # keep the v2 section written by uae.backtest_v2
        old = json.loads(sj.read_text())
        if "v2" in old:
            summary["v2"] = old["v2"]
    sj.write_text(json.dumps(summary, indent=2))
    make_figure(s, scores)
    write_summary_md(summary, by_model, by_season, pk)
    print(json.dumps({k: summary[k] for k in ["latest_sentinel_week", "rel_wis_nabd", "seasons_nabd_better",
                                              "rsv_peak_week_mae_wk"]}, indent=1))


def make_figure(s, scores):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    for ax, key, col in [(axes[0], "flu", "flu_pos"), (axes[1], "rsv", "rsv_pos")]:
        pct = s[col] / s.specimens * 100
        ax.plot(s.week_end, pct, color="black", lw=1.2, label="observed (WHO FluNet, UAE sentinel)")
        sc = scores[(scores.series == key) & (scores.model == "NABD-UAE-v1") & (scores.horizon == 0)]
        ax.plot(pd.to_datetime(sc.target_end_date), sc["median"], color="#1f77b4", lw=1, alpha=0.8,
                label="NABD-UAE-v1 median, target L+2 (1 wk after issue in the live product), LOSO")
        ax.set_ylabel(f"{key.upper()} positivity %")
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(alpha=0.3)
    axes[0].set_title("UAE sentinel positivity and leave-one-season-out NABD-UAE forecasts (n=4 test seasons)")
    fig.tight_layout()
    fig.savefig(OUT / "figures" / "uae_backtest.png", dpi=130)


def write_summary_md(summary, by_model, by_season, pk):
    L = ["# UAE track: leave-one-season-out results (PRELIMINARY)", "",
         f"Data: WHO FluNet UAE sentinel, latest week **{summary['latest_sentinel_week']}** (`data/raw/flunet_are.csv`). "
         "Design: leave-one-season-out over **n = 4 test seasons** (2022/23–2025/26), 1-week simulated publication lag, "
         "horizons h = -1, 0, 1, 2 are the 1st–4th weeks after the last published week L (L+1 = nowcast … L+4); in the live "
         "product they are labelled by week-ending date and 'nowcast / +1 / +2 / +3 wk after issue'; skill is measured at a "
         "conservative 11-day lag.", "",
         "**Honest caveats:** n = 4 seasons; 2022/23 is low-volume; LOSO trains on later seasons when testing earlier ones; "
         "bootstrap CIs resample reference dates and do not capture between-season uncertainty; FluNet revisions are not reproduced.", "",
         "## Relative WIS (NABD-UAE-v1 / baseline; < 1 means NABD better), 95% block-bootstrap CI", "",
         "| Comparison | All 4 seasons | Excluding 2022/23 |", "|---|---|---|"]
    for k, v in summary["rel_wis_nabd"].items():
        e = summary["rel_wis_nabd_excluding_2022_23"][k]
        L.append(f"| {k} | {v['rel_wis']} [{v['ci95'][0]}, {v['ci95'][1]}] (n dates={v['n_reference_dates']}) | "
                 f"{e['rel_wis']} [{e['ci95'][0]}, {e['ci95'][1]}] |")
    L += ["", "## Seasons (of 4) in which NABD-UAE-v1 had lower mean WIS", ""]
    for k, v in summary["seasons_nabd_better"].items():
        L.append(f"- {k}: vs persistence {v['persistence']}/4, vs seasonal analog {v['seasonal-analog']}/4")
    L += ["", "## Mean WIS and coverage by model", "", by_model.round(3).to_markdown(index=False), "",
          "## Mean WIS by season", "", by_season.round(3).to_markdown(index=False), "",
          "## RSV peak-week absolute error (weeks), origins 1–4 weeks before the observed peak", ""]
    if len(pk):
        L.append(pk.groupby(["model", "weeks_before_peak"]).abs_err_wk.mean().unstack().round(2).to_markdown())
    L += ["", "Peak-week metric is descriptive only (4 seasons × 4 origins).", "",
          "## Integrity note", "",
          "These v1 numbers are **retrospective, design-stage, not pre-registered**: NABD-UAE-v1 was designed with all "
          "four seasons visible and re-run after a leak fix (463ab09; docs/DEVIATIONS.md U1). All tables use cells common "
          "to all three models (U4). The out-of-sample tests of the UAE method are the GCC test (plan locked before download; "
          "self-attested until anchored) "
          "(results/gcc/SUMMARY.md) and the prospective ledger. v2 results: results/uae/SUMMARY-v2.md.", "",
          "`tests/test_adapters.py::test_forecast_unchanged_when_future_data_altered` caught a leave-one-season-out "
          "boundary leak in the first build (lag features of a training season's first week reached into the held-out "
          "season); it was fixed by masking cross-season lags in `uae/models.py::_features`, changing relative WIS by "
          "<= 0.01. A companion test confirms the detector fires when a leak is injected.", ""]
    (OUT / "SUMMARY.md").write_text("\n".join(L))


if __name__ == "__main__":
    main()
