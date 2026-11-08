"""UAE v2 evaluation, exactly as frozen in docs/PROTOCOL-UAE-v2.md (locked: docs/LOCK-UAE-v2.json).

Run (from repo root):
  python3 -m uae.backtest_v2 --cached            # scores; refuses to run unless the lock verifies
  python3 -m uae.backtest_v2 --cached --smoke    # fits models on one season and builds features only;
                                                 # computes NO score (used once, pre-lock, to catch crashes)

RETROSPECTIVE: v1 results were already seen when this protocol was written. Labelled as such everywhere.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "nabd_v2_kit"))

from nabd_kit.prereg import assert_locked  # noqa: E402
from nabd_kit.scoring import block_bootstrap_ratio  # noqa: E402

from adapters import flunet  # noqa: E402
from uae import alerts  # noqa: E402
from uae.models import Analog, H, NabdUAE, Persistence, QUANTILES, SERIES, expit, prepare  # noqa: E402
from uae.models_v2 import FULL, NabdUAEv2  # noqa: E402
from uae.scoring import covered, wis  # noqa: E402

OUT = ROOT / "results" / "uae"
V2 = OUT / "v2"
LOCK = ROOT / "docs" / "LOCK-UAE-v2.json"
PLAN = [ROOT / "docs" / "PROTOCOL-UAE-v2.md"]
CODE = [ROOT / p for p in ["uae/models.py", "uae/models_v2.py", "uae/features_v2.py", "uae/backtest_v2.py",
                           "uae/alerts.py", "uae/scoring.py", "adapters/flunet.py", "adapters/calendar.py"]]
DATA = [ROOT / "data" / "raw" / "flunet_are.csv", ROOT / "data" / "raw" / "uae_calendar.csv"]
CONFIG = dict(model="NABD-UAE-v2", blocks=list(FULL), horizons=list(H), quantiles=QUANTILES,
              test_seasons=[2022, 2023, 2024, 2025], forward_test_seasons=[2023, 2024, 2025],
              ns_extra_lag_weeks=1, alert_T={"flu": 15.0, "rsv": 10.0}, census_frac=0.6,
              alert_target_data_horizon=2, bootstrap=dict(B=2000, seed=20261108, block_len=4, within="season"),
              ablation_drop=["NS", "CAL", "TV", "CLIM"], stale_week_test_horizons=[1, 2, 3])
TEST_SEASONS = CONFIG["test_seasons"]
FWD_SEASONS = CONFIG["forward_test_seasons"]
SLUG = {"flu": "flu_pos_pct_sentinel", "rsv": "rsv_pos_pct_sentinel"}


def data_manifest_path() -> Path:
    """Data manifest (sha256 of each raw input), regenerated deterministically for the lock check."""
    sys.path.insert(0, str(ROOT / "vendor" / "nabd_v2_kit"))
    from nabd_kit.ledger import sha256_file
    p = ROOT / "docs" / "LOCK-UAE-v2.data-manifest.txt"
    p.write_text("".join(f"{sha256_file(f)}  {f.relative_to(ROOT).as_posix()}\n" for f in DATA))
    return p


def check_lock():
    return assert_locked(LOCK, [str(p.relative_to(ROOT)) for p in PLAN], [str(p.relative_to(ROOT)) for p in CODE],
                         CONFIG, str(data_manifest_path().relative_to(ROOT)))


def origins(d, season):
    return [i for i in d.index[d.season == season] if i + 4 < len(d) and d.season.iloc[i + 4] == season]


def obs_pct(d, j):
    return d.pos.iloc[j] / d.specimens.iloc[j] * 100 if not np.isnan(d.y.iloc[j]) else np.nan


def score_rows(model_name, key, season, d, i, qd, extra=None):
    rows = []
    L_end = d.week_end.iloc[i]
    ref = str((L_end + pd.Timedelta(days=14)).date())
    issue = str((L_end + pd.Timedelta(days=11)).date())
    for h in H:
        if qd.get(h) is None:
            continue
        vals = 100 * expit(np.sort(qd[h]))
        y = obs_pct(d, i + h)
        rec = dict(model=model_name, series=key, season=season, reference_date=ref, issue_date=issue,
                   origin=i, h_data=h, horizon=h - 2, target_end_date=str(d.week_end.iloc[i + h].date()),
                   obs=y, median=float(vals[QUANTILES.index(0.5)]), q=vals)
        if not np.isnan(y):
            rec.update(wis=wis(QUANTILES, vals, y), cov50=covered(QUANTILES, vals, y, 0.5),
                       cov95=covered(QUANTILES, vals, y, 0.95))
        if extra and h in extra:
            rec.update(extra[h])
        rows.append(rec)
    return rows


def run_design(raw, s, seasons, train_fn, v2_blocks=FULL, with_baselines=True, drop_ns=False, explain=False,
               v2_name="NABD-UAE-v2"):
    rows, ex_rows = [], []
    for key in SERIES:
        d1 = prepare(s, key)
        from uae.features_v2 import prepare_v2
        d2 = prepare_v2(raw, key)
        assert (d1.week_end.values == d2.week_end.values).all()
        for test in seasons:
            train = train_fn(d1, test)
            v2 = NabdUAEv2(d2, train, blocks=v2_blocks, name=v2_name)
            ms = [NabdUAE(d1, train), Persistence(d1, train), Analog(d1, train)] if with_baselines else []
            for i in origins(d1, test):
                for m in ms:
                    rows += score_rows(m.name, key, test, d1, i, m.predict(i))
                det = v2.predict_detail(i, drop_ns=drop_ns)
                qd = {h: (None if v is None else v["q"]) for h, v in det.items()}
                extra = {h: dict(submodel=v["sub"]) for h, v in det.items() if v is not None}
                rows += score_rows(v2.name, key, test, d2, i, qd, extra)
                if explain:
                    L_end = d2.week_end.iloc[i]
                    for h, v in det.items():
                        if v is None:
                            continue
                        e = v["explain"].copy()
                        total = e.contribution.sum()
                        e["pp_effect_loo"] = [100 * expit(total) - 100 * expit(total - c)
                                              if f not in ("last_observed_logit",) else np.nan
                                              for f, c in zip(e.feature, e.contribution)]
                        e.insert(0, "horizon", h - 2)
                        e["unit"] = "logit"
                        e["series"] = key
                        e["target"] = SERIES[key][1]
                        e["submodel"] = v["sub"]
                        e["median_pct"] = 100 * expit(total)
                        e["issue_date"] = str((L_end + pd.Timedelta(days=11)).date())
                        e["target_end_date"] = str(d2.week_end.iloc[i + h].date())
                        e["design"] = "LOSO retrospective"
                        ex_rows.append(e)
    return pd.DataFrame(rows), (pd.concat(ex_rows, ignore_index=True) if ex_rows else None)


def loso_train(d, test):
    return [x for x in sorted(d.season.dropna().unique().astype(int)) if x != test]


def fwd_train(d, test):
    return [x for x in sorted(d.season.dropna().unique().astype(int)) if x < test]


def common(sc, models):
    k = ["series", "season", "reference_date", "horizon"]
    sc = sc[sc.model.isin(models) & sc.wis.notna()]
    cnt = sc.groupby(k).model.nunique()
    keep = cnt[cnt == len(models)].index
    return sc.set_index(k).loc[keep].reset_index()


def rel(sc, a, b, series=None, seed=20261108):
    x = sc if series is None else sc[sc.series == series]
    k = ["series", "season", "reference_date", "horizon"]
    m = x[x.model == a].merge(x[x.model == b], on=k, suffixes=("_a", "_b"))
    if m.empty:
        return None
    g = m.groupby(["season", "reference_date"])[["wis_a", "wis_b"]].sum().reset_index()
    r = g.wis_a.sum() / g.wis_b.sum()
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(2000):
        kk = rng.integers(0, len(g), len(g))
        boots.append(g.wis_a.values[kk].sum() / g.wis_b.values[kk].sum())
    mb = block_bootstrap_ratio(g, "wis_a", "wis_b", "reference_date", block_len=4, n_boot=2000, seed=seed,
                               group_col="season")
    return dict(rel_wis=round(float(r), 3),
                ci95_date_cluster=[round(float(np.quantile(boots, .025)), 3), round(float(np.quantile(boots, .975)), 3)],
                ci95_moving_block_L4=[round(mb["lo"], 3), round(mb["hi"], 3)],
                n_cells=int(len(m)), n_reference_dates=int(len(g)))


def season_wins(sc, a, b):
    out = {}
    for series in SERIES:
        x = sc[sc.series == series].groupby(["season", "model"]).wis.mean().unstack()
        out[series] = f"{int((x[a] < x[b]).sum())}/{len(x)}"
    return out


def alert_eval(raw, s, sc_full, sc_dropns):
    onsets = []
    al = []
    for key in SERIES:
        d = prepare(s, key)
        ot = alerts.onset_table(d, key, TEST_SEASONS)
        onsets.append(ot)
        T = alerts.T[key]
        pct = d.pos / d.specimens * 100
        for test in TEST_SEASONS:
            for i in origins(d, test):
                issue = str((d.week_end.iloc[i] + pd.Timedelta(days=11)).date())
                p = pct.iloc[i]
                if np.isnan(p):
                    continue
                if CONFIG["census_frac"] * T <= p < T:
                    al.append(dict(model="census rule (persistence)", series=key, season=test, issue_date=issue))
                for name, sc in (("NABD-UAE-v1", sc_full), ("NABD-UAE-v2", sc_full),
                                 ("NABD-UAE-v2 (NS feed dropped)", sc_dropns)):
                    mname = "NABD-UAE-v2" if name.startswith("NABD-UAE-v2") else name
                    r = sc[(sc.model == mname) & (sc.series == key) & (sc.origin == i) &
                           (sc.h_data == CONFIG["alert_target_data_horizon"])]
                    if len(r) and r["median"].iloc[0] >= T and p < T:
                        al.append(dict(model=name, series=key, season=test, issue_date=issue))
    on = pd.concat(onsets, ignore_index=True)
    ev = alerts.evaluate(pd.DataFrame(al), on)
    return on, ev, alerts.summarise(ev)


def stale_week(raw, s):
    """Missing latest sentinel week: forecast target t+h from origin t-1 at horizon h+1 vs origin t at h."""
    rows = []
    for key in SERIES:
        d1 = prepare(s, key)
        from uae.features_v2 import prepare_v2
        d2 = prepare_v2(raw, key)
        for test in TEST_SEASONS:
            train = loso_train(d1, test)
            ms = {"NABD-UAE-v1": (NabdUAE(d1, train), d1), "NABD-UAE-v2": (NabdUAEv2(d2, train), d2)}
            for name, (m, d) in ms.items():
                for i in origins(d1, test):
                    if i - 1 < 0 or d.season.iloc[i - 1] != test:
                        continue
                    fresh, stale = m.predict(i), m.predict(i - 1)
                    for h in CONFIG["stale_week_test_horizons"]:
                        y = obs_pct(d, i + h)
                        if fresh.get(h) is None or stale.get(h + 1) is None or np.isnan(y):
                            continue
                        rows.append(dict(model=name, series=key, season=test, h_data=h,
                                         wis_fresh=wis(QUANTILES, 100 * expit(np.sort(fresh[h])), y),
                                         wis_stale=wis(QUANTILES, 100 * expit(np.sort(stale[h + 1])), y)))
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--cached", action="store_true")
    g.add_argument("--fetch", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    raw = flunet.load("fetch" if a.fetch else "cached")
    s = flunet.sentinel_series(raw)
    if a.smoke:
        from uae.features_v2 import prepare_v2
        for key in SERIES:
            d2 = prepare_v2(raw, key)
            m = NabdUAEv2(d2, [2023, 2024, 2025, 2026])
            det = m.predict_detail(int(d2.index[d2.season == 2022][10]))
            print(key, "features ok; submodels:", sorted({v["sub"] for v in det.values() if v}),
                  "explain sums ok:", all(abs(v["explain"].contribution.sum() - v["q"][11]) < 1e-9
                                          for v in det.values() if v))
        print("SMOKE ONLY: no score computed")
        return
    root = check_lock()
    print("lock verified, merkle root", root)
    for p in (V2 / "tables", V2 / "figures", OUT / "explain", OUT / "tables"):
        p.mkdir(parents=True, exist_ok=True)

    sc, ex = run_design(raw, s, TEST_SEASONS, loso_train, explain=True)
    models = ["NABD-UAE-v1", "NABD-UAE-v2", "persistence", "seasonal-analog"]
    cc = common(sc, models)
    cc.drop(columns=["q"]).to_csv(V2 / "tables" / "scores_long_common.csv", index=False)
    res = {}
    for series in SERIES:
        res[series] = {f"{x}_vs_{y}": rel(cc, x, y, series) for x, y in
                       [("NABD-UAE-v2", "NABD-UAE-v1"), ("NABD-UAE-v2", "persistence"),
                        ("NABD-UAE-v2", "seasonal-analog"), ("NABD-UAE-v1", "persistence"),
                        ("NABD-UAE-v1", "seasonal-analog")]}
    res["pooled"] = {f"{x}_vs_{y}": rel(cc, x, y) for x, y in
                     [("NABD-UAE-v2", "NABD-UAE-v1"), ("NABD-UAE-v2", "persistence"), ("NABD-UAE-v1", "persistence")]}
    by_h = cc.pivot_table(index=["series", "horizon"], columns="model", values="wis", aggfunc="mean").reset_index()
    for b in ["NABD-UAE-v1", "NABD-UAE-v2"]:
        by_h[f"{b}/persistence"] = by_h[b] / by_h["persistence"]
    by_h.round(4).to_csv(V2 / "tables" / "wis_by_horizon.csv", index=False)
    by_s = cc.pivot_table(index=["series", "season"], columns="model", values="wis", aggfunc="mean").reset_index()
    by_s.round(4).to_csv(V2 / "tables" / "wis_by_season.csv", index=False)
    cov = cc.groupby(["series", "model"])[["cov50", "cov95"]].mean().round(3).reset_index()
    cov.to_csv(V2 / "tables" / "coverage.csv", index=False)
    sub_use = sc[sc.model == "NABD-UAE-v2"].groupby(["series", "season", "submodel"]).size().reset_index(name="n")
    sub_use.to_csv(V2 / "tables" / "submodel_use.csv", index=False)
    wins = {"v2_vs_v1": season_wins(cc, "NABD-UAE-v2", "NABD-UAE-v1"),
            "v2_vs_persistence": season_wins(cc, "NABD-UAE-v2", "persistence"),
            "v1_vs_persistence": season_wins(cc, "NABD-UAE-v1", "persistence")}

    # explain files (contract): results/uae/explain/<issue_date>_<target>.csv
    for (issue, key), gx in ex.groupby(["issue_date", "series"]):
        gx.to_csv(OUT / "explain" / f"{issue}_{SLUG[key]}.csv", index=False)
    contrib = ex[~ex.feature.isin(["last_observed_logit", "intercept", "residual_median_offset"])]
    contrib.assign(abs_c=contrib.contribution.abs()).groupby(["series", "feature"]).abs_c.mean().round(4) \
        .reset_index(name="mean_abs_contribution_logit").to_csv(V2 / "tables" / "mean_abs_contribution.csv", index=False)

    # forward-in-time sensitivity
    fsc, _ = run_design(raw, s, FWD_SEASONS, fwd_train)
    fcc = common(fsc, models)
    fwd = {series: {f"{x}_vs_{y}": rel(fcc, x, y, series) for x, y in
                    [("NABD-UAE-v2", "NABD-UAE-v1"), ("NABD-UAE-v2", "persistence"), ("NABD-UAE-v1", "persistence")]}
           for series in SERIES}
    fwd_s = fcc.pivot_table(index=["series", "season"], columns="model", values="wis", aggfunc="mean").reset_index()
    fwd_s.round(4).to_csv(V2 / "tables" / "forward_wis_by_season.csv", index=False)

    # ablation (refit without each block) on cells common with full v2
    ab_rows = []
    full = sc[(sc.model == "NABD-UAE-v2") & sc.wis.notna()]
    for blk in CONFIG["ablation_drop"]:
        blocks = tuple(b for b in FULL if b != blk)
        asc, _ = run_design(raw, s, TEST_SEASONS, loso_train, v2_blocks=blocks, with_baselines=False,
                            v2_name=f"v2-without-{blk}")
        k = ["series", "season", "reference_date", "horizon"]
        m = full.merge(asc[asc.wis.notna()], on=k, suffixes=("_f", "_w"))
        for series, gm in m.groupby("series"):
            ab_rows.append(dict(feed=blk, series=series, metric="mean WIS (pct points)",
                                full=round(gm.wis_f.mean(), 4), without=round(gm.wis_w.mean(), 4),
                                delta=round(gm.wis_w.mean() - gm.wis_f.mean(), 4), n_cells=len(gm),
                                kind="refit without block (LOSO)"))
    # missing NS feed at prediction time (fallback sub-model)
    dsc, _ = run_design(raw, s, TEST_SEASONS, loso_train, with_baselines=False, drop_ns=True)
    k = ["series", "season", "reference_date", "horizon"]
    m = full.merge(dsc[dsc.wis.notna()], on=k, suffixes=("_f", "_w"))
    for series, gm in m.groupby("series"):
        ab_rows.append(dict(feed="NS (missing at forecast time)", series=series, metric="mean WIS (pct points)",
                            full=round(gm.wis_f.mean(), 4), without=round(gm.wis_w.mean(), 4),
                            delta=round(gm.wis_w.mean() - gm.wis_f.mean(), 4), n_cells=len(gm),
                            kind="feed dropped at prediction; automatic fallback sub-model"))
    st = stale_week(raw, s)
    for (model, series), gm in st.groupby(["model", "series"]):
        ab_rows.append(dict(feed=f"latest sentinel week missing ({model})", series=series,
                            metric="mean WIS (pct points)", full=round(gm.wis_fresh.mean(), 4),
                            without=round(gm.wis_stale.mean(), 4),
                            delta=round(gm.wis_stale.mean() - gm.wis_fresh.mean(), 4), n_cells=len(gm),
                            kind="stale origin (t-1, horizon+1)"))
    ab = pd.DataFrame(ab_rows)
    ab.to_csv(OUT / "tables" / "ablation.csv", index=False)

    # alerts
    dsc2 = dsc.copy()
    on, ev, alsum = alert_eval(raw, s, sc, dsc2)
    on.to_csv(V2 / "tables" / "alert_onsets.csv", index=False)
    ev.to_csv(V2 / "tables" / "alerts_detail.csv", index=False)
    alsum.to_csv(OUT / "tables" / "alerts_uae.csv", index=False)

    summary = dict(
        protocol="docs/PROTOCOL-UAE-v2.md", lock="docs/LOCK-UAE-v2.json", lock_merkle_root=root,
        label="RETROSPECTIVE; protocol declared and locked before any v2 score; v1 results had already been seen",
        latest_sentinel_week=f"{int(s.dropna(subset=['specimens']).iloc[-1].iso_year)}-W"
                             f"{int(s.dropna(subset=['specimens']).iloc[-1].iso_week):02d}",
        n_seasons=4, design="leave-one-season-out (primary); forward-in-time (sensitivity, 3 seasons)",
        rel_wis_loso=res, season_wins_loso=wins, rel_wis_forward_in_time=fwd,
        coverage=cov.to_dict(orient="records"), alerts=alsum.to_dict(orient="records"),
        ablation=ab.to_dict(orient="records"), signals=["sentinel positivity", "testing volume (sentinel specimens)",
                                                        "non-sentinel positivity (lag +1 wk)",
                                                        "school winter/spring breaks (verified calendars)",
                                                        "Ramadan (tabular calendar, +/-2 days)"],
        weather="OMITTED: no reachable source for 2026 (NOAA/Open-Meteo/Meteostat blocked; a third-party ERA5 "
                "mirror ends 2025-12-31). Run adapters.weather --fetch locally; weather is not in v2.",
        caveats=["n=4 test seasons; descriptive", "LOSO trains on later seasons; forward-in-time sensitivity reported",
                 "non-sentinel stream starts 2023-W15, so 2022/23 and early 2023/24 use the fallback sub-model",
                 "revisions to FluNet values are not reproduced (no vintages)"])
    (V2 / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    sj = OUT / "summary.json"
    base = json.loads(sj.read_text()) if sj.exists() else {}
    base["v2"] = {"summary": "results/uae/v2/summary.json", "markdown": "results/uae/SUMMARY-v2.md",
                  "rel_wis_loso_pooled": res["pooled"], "label": summary["label"]}
    sj.write_text(json.dumps(base, indent=2))
    write_md(summary, by_h, by_s, alsum, ab, sub_use, fwd_s)
    make_figure(by_h, ab)
    print(json.dumps({k: summary[k] for k in ["rel_wis_loso", "season_wins_loso"]}, indent=1))


def _fmt(r):
    if not r:
        return "n/a"
    return (f"{r['rel_wis']} (date-cluster {r['ci95_date_cluster'][0]}–{r['ci95_date_cluster'][1]}; "
            f"moving-block {r['ci95_moving_block_L4'][0]}–{r['ci95_moving_block_L4'][1]}; n={r['n_cells']})")


def write_md(summary, by_h, by_s, alsum, ab, sub_use, fwd_s):
    L = ["# UAE v2 (multi-signal): results", "",
         "**RETROSPECTIVE.** Protocol `docs/PROTOCOL-UAE-v2.md` was written, committed and locked "
         f"(`docs/LOCK-UAE-v2.json`, Merkle root `{summary['lock_merkle_root'][:16]}…`) before any v2 score was "
         "computed, but v1 results on the same seasons had already been seen. n = 4 test seasons. "
         "WIS is in percentage points of positivity; relative WIS < 1 favours the first model.", "",
         "Signals: " + "; ".join(summary["signals"]) + ".", "", f"Weather: {summary['weather']}", "",
         "## Leave-one-season-out (primary), common cells across v1, v2, persistence, analog", "",
         "| Series | Comparison | Relative WIS (95% CIs) |", "|---|---|---|"]
    for series, d in summary["rel_wis_loso"].items():
        for k, r in d.items():
            L.append(f"| {series} | {k} | {_fmt(r)} |")
    L += ["", "Season wins (lower mean WIS): " + json.dumps(summary["season_wins_loso"]), "",
          "## Forward-in-time sensitivity (train only on earlier seasons; test 2023/24–2025/26)", "",
          "| Series | Comparison | Relative WIS |", "|---|---|---|"]
    for series, d in summary["rel_wis_forward_in_time"].items():
        for k, r in d.items():
            L.append(f"| {series} | {k} | {_fmt(r)} |")
    L += ["", fwd_s.round(3).to_markdown(index=False), "",
          "## By horizon (LOSO; horizon relative to reference date: -1 nowcast … 2 = +2.5 wk after issue)", "",
          by_h.round(3).to_markdown(index=False), "", "## By season (LOSO)", "", by_s.round(3).to_markdown(index=False),
          "", "## Feed removal and missing-feed behaviour (`results/uae/tables/ablation.csv`)", "",
          ab.to_markdown(index=False), "", "## Sub-model actually used by v2 (fallback when a feed is missing)", "",
          sub_use.to_markdown(index=False), "",
          "## Surge-onset alerts (pre-declared rule; descriptive, n = 4 seasons per series)", "",
          alsum.to_markdown(index=False), "",
          "Thresholds T (flu 15%, RSV 10%) and the 0.6·T census fraction were set from earlier exploratory "
          "work that saw these seasons (disclosed in DEVIATIONS); alert metrics are diagnostic only.", "",
          "## Caveats", ""] + [f"- {c}" for c in summary["caveats"]]
    (OUT / "SUMMARY-v2.md").write_text("\n".join(L) + "\n")


def make_figure(by_h, ab):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    for series, mk in (("flu", "o"), ("rsv", "s")):
        x = by_h[by_h.series == series]
        for b, ls in (("NABD-UAE-v1", "--"), ("NABD-UAE-v2", "-")):
            axes[0].plot(x.horizon, x[f"{b}/persistence"], ls, marker=mk, label=f"{series.upper()} {b}")
    axes[0].axhline(1, color="grey", lw=0.8)
    axes[0].set_xticks([-1, 0, 1, 2], ["nowcast", "+0.5 wk", "+1.5 wk", "+2.5 wk"])
    axes[0].set_ylabel("mean WIS / persistence (lower is better)")
    axes[0].set_title("UAE LOSO (retrospective, n=4 seasons)")
    axes[0].legend(fontsize=8)
    a2 = ab[ab.kind.str.startswith("refit")]
    lab = [f"{r.feed}\n{r.series}" for r in a2.itertuples()]
    axes[1].barh(lab, a2.delta, color=["#2b7a78" if v > 0 else "#c0392b" for v in a2.delta])
    axes[1].axvline(0, color="grey", lw=0.8)
    axes[1].set_xlabel("WIS change when the feed is removed (+ = feed helps)")
    axes[1].set_title("Feed-removal ablation (v2, LOSO)")
    fig.tight_layout()
    fig.savefig(V2 / "figures" / "uae_v2_overview.png", dpi=130)


if __name__ == "__main__":
    main()
