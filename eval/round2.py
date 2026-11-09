"""Round-2 analyses for the US-A track. Every analysis here was declared in docs/DEVIATIONS.md
before it was computed:

  D6  sensitivity: circular moving-block bootstrap (L=4, L=6 check), national-series share,
      results excluding the national series, per-location wins
  D7  league table among individual CDC FluSight hub models (pairwise relative WIS)
  D9  scorer cross-check vs the vendored independent implementation (nabd_v2_kit)
  D10 G13 diagnostics: WIS decomposition by as-of phase x horizon; relative economic value
  D11 implementation details for D6/D7

None of these changes the PRIMARY endpoint or its verdict (PROTOCOL v1.0, docs/FREEZE.md).

Outputs: results/tables/{sensitivity_block_bootstrap,national_share,excl_national,
         per_location_wins,league_table,league_cells_summary,scorer_crosscheck,
         phase_decomposition,phase_decomposition_US,rev_curves}.csv
         results/figures/{fig1_rel_wis_season_horizon,fig2_league_table,
         fig3_wis_decomposition,fig4_rev}.png
         results/summary.json (adds keys; see `update_summary`)

Run:  python -m eval.round2            (uses the hub clone in external/hub)
      python -m eval.round2 --fetch-league  (first time: sparse-checkout all hub models' test-season files, ~1.2 GB)
      python -m eval.round2 --skip-league   (if other hub models are not checked out and no cache exists)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from models.data import HUB, QUANTILES, TARGET, final_truth, season_dates, series_as_of
from eval.score import SEASONS, attach_truth, boot_ratio, load_model, MARGIN, SEED
from eval.wis import wis

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "nabd_v2_kit"))
from nabd_kit import decision as kdec  # noqa: E402
from nabd_kit import phase as kphase  # noqa: E402
from nabd_kit import quantiles as kq  # noqa: E402
from nabd_kit import scoring as ksc  # noqa: E402

TAB = ROOT / "results" / "tables"
FIG = ROOT / "results" / "figures"
CACHE = ROOT / "data" / "cache"
B = 2000
N_LOC = 53


# ---------------------------------------------------------------- helpers
def season_of(r) -> str:
    for s in SEASONS:
        d = season_dates(s)
        if d[0] <= r <= d[-1]:
            return s
    return "other"


def cells(models: dict, A: str, Bm: str, filt=None):
    """Common cells of A and B with final truth; returns idx, y, wis_A, wis_B, qA, qB."""
    idx = models[A].index.intersection(models[Bm].index)
    if filt is not None:
        idx = idx[filt(idx)]
    y = attach_truth(idx, final_truth())
    ok = np.isfinite(y)
    idx, y = idx[ok], y[ok]
    qa, qb = models[A].loc[idx].to_numpy(float), models[Bm].loc[idx].to_numpy(float)
    return idx, y, wis(qa, y), wis(qb, y), qa, qb


def circular_block_ci(wa, wb, refs, L, seed=SEED, nboot=B):
    """D6/D11(a): stratified (by season) circular moving-block bootstrap over reference dates."""
    refs = pd.to_datetime(pd.Series(refs))
    df = pd.DataFrame({"r": refs.values, "a": wa, "b": wb})
    per = df.groupby("r")[["a", "b"]].sum().sort_index()
    seas = np.array([season_of(r) for r in per.index])
    rng = np.random.default_rng(seed)
    groups = []
    for s in pd.unique(seas):
        m = seas == s
        groups.append((per.a.to_numpy()[m], per.b.to_numpy()[m]))
    est = per.a.sum() / per.b.sum()
    draws = np.empty(nboot)
    for k in range(nboot):
        sa = sb = 0.0
        for a, b in groups:
            n = len(a)
            nb = int(np.ceil(n / L))
            starts = rng.integers(0, n, size=nb)
            idx = ((starts[:, None] + np.arange(L)[None, :]) % n).ravel()[:n]
            sa += a[idx].sum()
            sb += b[idx].sum()
        draws[k] = sa / sb
    return float(est), float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def populations() -> pd.Series:
    f = pd.read_csv(HUB / "target-data" / "target-hospital-admissions.csv", dtype={"location": str})
    f = f[(f.weekly_rate > 0) & (f.value > 0)]
    return (f.value / f.weekly_rate * 1e5).groupby(f.location).median()


# ---------------------------------------------------------------- D9
def scorer_crosscheck(models) -> pd.DataFrame:
    rows = []
    for m in ["NABD-ensemble", "FluSight-ensemble", "FluSight-baseline"]:
        idx = models[m].index
        y = attach_truth(idx, final_truth())
        ok = np.isfinite(y)
        q = models[m].loc[idx[ok]].to_numpy(float)
        ours = wis(q, y[ok])
        kit = ksc.wis(q, y[ok], kq.FLUSIGHT_LEVELS)
        crossing = int((np.diff(q, axis=1) < -1e-12).any(axis=1).sum())
        tol = 1e-9 * np.maximum(1.0, np.abs(ours))
        diff = np.abs(ours - kit)
        rows.append({"model": m, "cells": int(ok.sum()), "max_abs_diff": float(diff.max()),
                     "cells_over_tol": int((diff > tol).sum()), "cells_with_crossing_quantiles": crossing,
                     "pass": bool((diff <= tol).all())})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- D6
def d6(models):
    out = {}
    is_season = lambda s: (lambda idx: np.array([season_of(r) == s for r, _, _ in idx]))
    specs = [("PRIMARY pooled", "NABD-ensemble", "FluSight-ensemble", None),
             ("S1 pooled vs baseline", "NABD-ensemble", "FluSight-baseline", None)]
    for s in SEASONS:
        specs += [(f"S3 season {s}", "NABD-ensemble", "FluSight-ensemble", is_season(s)),
                  (f"S3 season {s} vs baseline", "NABD-ensemble", "FluSight-baseline", is_season(s))]
    rows = []
    for tag, A, Bm, f in specs:
        idx, y, wa, wb, _, _ = cells(models, A, Bm, f)
        refs = np.array([r for r, _, _ in idx])
        e, lo, hi = boot_ratio(wa, wb, refs, np.random.default_rng(SEED))
        r = {"analysis": tag, "A": A, "B": Bm, "cells": len(idx), "rel_wis": e,
             "cluster_ci_lo": lo, "cluster_ci_hi": hi}
        for L in (4, 6):
            _, l2, h2 = circular_block_ci(wa, wb, refs, L)
            r[f"block{L}_ci_lo"], r[f"block{L}_ci_hi"] = l2, h2
        rows.append(r)
    # E1 (EXPLORATORY): same realised-phase split as eval/exploratory.py
    idx, y, wa, wb, _, _ = cells(models, "NABD-ensemble", "FluSight-ensemble")
    dates = sorted({r for r, _, _ in idx})
    last = {R: series_as_of(R)[0].iloc[:, -1] for R in dates}
    lo_ = np.array([last[r][l] for r, l, _ in idx])
    ratio = (y + 1) / (lo_ + 1)
    ph = np.where(ratio > 1.25, "rising", np.where(ratio < 0.8, "falling", "flat"))
    refs = np.array([r for r, _, _ in idx])
    for p in ["rising", "flat", "falling"]:
        m = ph == p
        e, lo, hi = boot_ratio(wa[m], wb[m], refs[m], np.random.default_rng(99))
        r = {"analysis": f"E1 EXPLORATORY realised phase={p}", "A": "NABD-ensemble", "B": "FluSight-ensemble",
             "cells": int(m.sum()), "rel_wis": e, "cluster_ci_lo": lo, "cluster_ci_hi": hi}
        for L in (4, 6):
            _, l2, h2 = circular_block_ci(wa[m], wb[m], refs[m], L)
            r[f"block{L}_ci_lo"], r[f"block{L}_ci_hi"] = l2, h2
        rows.append(r)
    blk = pd.DataFrame(rows)
    blk["exploratory"] = blk.analysis.str.startswith("E1")
    blk.to_csv(TAB / "sensitivity_block_bootstrap.csv", index=False)
    out["block"] = blk

    # national share + excluding US
    idx, y, wa, wb, _, _ = cells(models, "NABD-ensemble", "FluSight-ensemble")
    us = np.array([l == "US" for _, l, _ in idx])
    _, _, wa_b, wbase, _, _ = cells(models, "NABD-ensemble", "FluSight-baseline")
    sh = pd.DataFrame([{"model": "NABD-ensemble", "share_of_total_WIS_from_US": wa[us].sum() / wa.sum()},
                       {"model": "FluSight-ensemble", "share_of_total_WIS_from_US": wb[us].sum() / wb.sum()}])
    sh.to_csv(TAB / "national_share.csv", index=False)
    out["national_share"] = sh
    rows = []
    for tag, A, Bm in [("PRIMARY excl. US national", "NABD-ensemble", "FluSight-ensemble"),
                       ("S1 excl. US national", "NABD-ensemble", "FluSight-baseline")]:
        f = lambda ix: np.array([l != "US" for _, l, _ in ix])
        ix, yy, a, b, _, _ = cells(models, A, Bm, f)
        refs = np.array([r for r, _, _ in ix])
        e, lo, hi = boot_ratio(a, b, refs, np.random.default_rng(SEED))
        _, l4, h4 = circular_block_ci(a, b, refs, 4)
        rows.append({"analysis": tag, "A": A, "B": Bm, "cells": len(ix), "rel_wis": e,
                     "cluster_ci_lo": lo, "cluster_ci_hi": hi, "block4_ci_lo": l4, "block4_ci_hi": h4})
    ex = pd.DataFrame(rows)
    ex.to_csv(TAB / "excl_national.csv", index=False)
    out["excl_us"] = ex

    # per-location wins
    rows = []
    for Bm in ["FluSight-ensemble", "FluSight-baseline"]:
        ix, yy, a, b, _, _ = cells(models, "NABD-ensemble", Bm)
        d = pd.DataFrame({"season": [season_of(r) for r, _, _ in ix], "location": [l for _, l, _ in ix], "a": a, "b": b})
        g = d.groupby(["season", "location"])[["a", "b"]].sum()
        g["ratio"] = g.a / g.b
        for s, gs in g.groupby(level=0):
            rows.append({"comparator": Bm, "season": s, "locations": len(gs), "nabd_wins": int((gs.ratio < 1).sum()),
                         "median_ratio": float(gs.ratio.median())})
        all_ = d.groupby("location")[["a", "b"]].sum()
        rows.append({"comparator": Bm, "season": "pooled", "locations": len(all_),
                     "nabd_wins": int((all_.a / all_.b < 1).sum()), "median_ratio": float((all_.a / all_.b).median())})
    w = pd.DataFrame(rows)
    w.to_csv(TAB / "per_location_wins.csv", index=False)
    out["wins"] = w
    return out


# ---------------------------------------------------------------- D7
def fetch_league_files():
    """Sparse-checkout (no-cone) every hub model's files for the test-season reference dates only
    (about 1.2 GB), keeping target-data, hub-config, model-metadata and the two comparators."""
    import subprocess
    files = subprocess.run(["git", "-C", str(HUB), "ls-tree", "-r", "--name-only", "HEAD", "model-output/"],
                           capture_output=True, text=True, check=True).stdout.split()
    dates = {d.date().isoformat() for s in SEASONS for d in season_dates(s)}
    pats = ["/target-data/", "/hub-config/", "/model-output/FluSight-ensemble/", "/model-output/FluSight-baseline/",
            "/model-metadata/", "/README.md"]
    pats += ["/" + f for f in files if f.endswith(".csv") and f.split("/")[-1][:10] in dates]
    subprocess.run(["git", "-C", str(HUB), "sparse-checkout", "set", "--no-cone", "--stdin"],
                   input="\n".join(pats), text=True, check=True)


def _ensemble_flags() -> dict:
    flags = {}
    for p in (HUB / "model-metadata").glob("*.y*ml"):
        try:
            d = yaml.safe_load(p.read_text())
            flags[p.stem] = bool(d.get("ensemble_of_models", False))
        except Exception:  # noqa: BLE001
            flags[p.stem] = None
    return flags


def _load_hub_any(model: str, dates) -> pd.DataFrame | None:
    parts = []
    for R in dates:
        p = HUB / "model-output" / model / f"{R.date().isoformat()}-{model}.csv"
        if not p.exists():
            continue
        try:
            d = pd.read_csv(p, dtype={"location": str, "output_type_id": str},
                            usecols=["location", "horizon", "target", "output_type", "output_type_id", "value"])
        except Exception:  # noqa: BLE001
            continue
        d = d[(d.target == TARGET) & (d.output_type == "quantile") & (d.horizon.isin([0, 1, 2, 3]))]
        if d.empty:
            continue
        d = d.assign(q=pd.to_numeric(d.output_type_id, errors="coerce").round(3), reference_date=R)
        parts.append(d[["reference_date", "location", "horizon", "q", "value"]])
    if not parts:
        return None
    df = pd.concat(parts)
    df["horizon"] = df.horizon.astype(int)
    w = df.pivot_table(index=["reference_date", "location", "horizon"], columns="q", values="value", aggfunc="first")
    w = w.reindex(columns=np.round(QUANTILES, 3)).dropna()
    return w


def league_cache_key() -> str:
    """Cache key = sha256 over the NABD-ensemble forecast files + the pinned hub SHA (audit R3 #15)."""
    import hashlib
    from eval.run_all import HUB_SHA
    h = hashlib.sha256(HUB_SHA.encode())
    for f in sorted((ROOT / "results" / "forecasts" / "NABD-ensemble").glob("*.csv")):
        h.update(f.name.encode()); h.update(f.read_bytes())
    return h.hexdigest()[:16]


def league(models) -> tuple[pd.DataFrame, pd.DataFrame]:
    flags = _ensemble_flags()
    hub_models = sorted(p.name for p in (HUB / "model-output").iterdir() if p.is_dir())
    cache = CACHE / f"league_cell_wis_{league_cache_key()}.pkl"
    ft = final_truth()
    if cache.exists():
        scores = pd.read_pickle(cache)
    else:
        rows = []
        for s in SEASONS:
            dates = season_dates(s)
            for m in hub_models + ["NABD-ensemble"]:
                w = models[m].loc[[r for r in models[m].index if season_of(r[0]) == s]] if m == "NABD-ensemble" \
                    else _load_hub_any(m, dates)
                if w is None or len(w) == 0:
                    continue
                y = attach_truth(w.index, ft)
                ok = np.isfinite(y)
                ww = wis(w.to_numpy(float)[ok], y[ok])
                ix = w.index[ok]
                rows.append(pd.DataFrame({"season": s, "model": m, "reference_date": [r for r, _, _ in ix],
                                          "location": [l for _, l, _ in ix], "horizon": [h for _, _, h in ix], "wis": ww}))
        scores = pd.concat(rows, ignore_index=True)
        CACHE.mkdir(parents=True, exist_ok=True)
        scores.to_pickle(cache)
    out, summ = [], []
    for s in SEASONS:
        possible = len(season_dates(s)) * N_LOC * 4
        sc = scores[scores.season == s]
        cov = sc.groupby("model").size() / possible
        incl = cov[cov >= 0.5].index.tolist()
        summ.append({"season": s, "possible_cells": possible, "models_with_any": int(cov.size),
                     "models_included": len(incl), "nabd_included": "NABD-ensemble" in incl})
        for variant, mods in [("all included", incl),
                              ("excluding ensembles", [m for m in incl if m == "NABD-ensemble" or flags.get(m) is False or m == "FluSight-baseline"])]:
            t = ksc.pairwise_relative_wis(sc[sc.model.isin(mods)], ["reference_date", "location", "horizon"],
                                          baseline="FluSight-baseline")
            t["rank"] = np.arange(1, len(t) + 1)
            t["n_models"] = len(t)
            t["season"], t["variant"] = s, variant
            t["coverage"] = t.model.map(cov)
            t["ensemble_of_models"] = t.model.map(lambda m: False if m == "NABD-ensemble" else flags.get(m))
            out.append(t)
    lt = pd.concat(out, ignore_index=True)
    lt.to_csv(TAB / "league_table.csv", index=False)
    sm = pd.DataFrame(summ)
    sm.to_csv(TAB / "league_cells_summary.csv", index=False)
    return lt, sm


# ---------------------------------------------------------------- D10 / G13
def g13(models):
    names = ["NABD-ensemble", "FluSight-ensemble", "FluSight-baseline"]
    idx = models[names[0]].index
    for m in names[1:]:
        idx = idx.intersection(models[m].index)
    y = attach_truth(idx, final_truth())
    ok = np.isfinite(y)
    idx, y = idx[ok], y[ok]
    dates = sorted({r for r, _, _ in idx})
    ph = {}
    for R in dates:
        w = series_as_of(R)[0]
        last3 = w.iloc[:, -3:].to_numpy(float)
        for i, loc in enumerate(w.index):
            sl = kphase.asof_log_slope(last3[i], window=3, offset=1.0)[-1]
            ph[(R, loc)] = kphase.classify(np.array([sl]), band=0.1)[0]
    phase_lab = np.array([ph.get((r, l), "unknown") for r, l, _ in idx])
    hz = np.array([h for _, _, h in idx])
    locs = np.array([l for _, l, _ in idx])
    comp = {}
    for m in names:
        q = models[m].loc[idx].to_numpy(float)
        d, o, u = ksc.wis_components(q, y, kq.FLUSIGHT_LEVELS)
        comp[m] = (wis(q, y), d, o, u, q)

    def table(mask_all, tag):
        rows = []
        for p in ["rising", "flat", "falling", "unknown", "ALL"]:
            for h in [0, 1, 2, 3, "ALL"]:
                m = mask_all.copy()
                if p != "ALL":
                    m &= phase_lab == p
                if h != "ALL":
                    m &= hz == h
                if m.sum() == 0:
                    continue
                ens = comp["FluSight-ensemble"][0][m].sum()
                for name in names:
                    w_, d_, o_, u_, _ = comp[name]
                    tot = w_[m].sum()
                    rows.append({"subset": tag, "phase": p, "horizon": h, "model": name, "cells": int(m.sum()),
                                 "mean_wis": float(w_[m].mean()), "rel_wis_vs_FS_ensemble": float(tot / ens),
                                 "share_dispersion": float(d_[m].sum() / tot), "share_over": float(o_[m].sum() / tot),
                                 "share_under": float(u_[m].sum() / tot)})
        return pd.DataFrame(rows)

    allm = np.ones(len(idx), bool)
    pdc = table(allm, "all locations")
    pdc.to_csv(TAB / "phase_decomposition.csv", index=False)
    pus = table(locs == "US", "US national only")
    pus.to_csv(TAB / "phase_decomposition_US.csv", index=False)

    # REV
    pop = populations()
    thr = np.array([3.0 * pop.get(l, np.nan) / 1e5 for l in locs])
    alphas = [0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7]
    rows = []
    for subset, mask in [("h2 (primary)", hz == 2), ("all horizons (secondary)", np.ones(len(idx), bool))]:
        mask = mask & np.isfinite(thr)
        ev = y[mask] >= thr[mask]
        for name in names:
            q = comp[name][4][mask]
            p = np.array([kq.exceedance_prob(q[i:i + 1], kq.FLUSIGHT_LEVELS, thr[mask][i])[0] for i in range(len(q))])
            for env in (False, True):
                v = kdec.relative_economic_value(p, ev, alphas, envelope=env)
                for a, vv in zip(alphas, v):
                    rows.append({"subset": subset, "model": name, "curve": "envelope (potential)" if env else "act if p>alpha (primary)",
                                 "alpha": a, "REV": float(vv), "cases": int(mask.sum()), "base_rate": float(ev.mean())})
    rev = pd.DataFrame(rows)
    rev.to_csv(TAB / "rev_curves.csv", index=False)
    return pdc, pus, rev


# ---------------------------------------------------------------- figures
def figures(models, lt, pdc, rev):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 12})
    FIG.mkdir(parents=True, exist_ok=True)
    col = {"FluSight-ensemble": "#1f77b4", "FluSight-baseline": "#7f7f7f", "NABD-ensemble": "#d62728"}

    # fig1: rel WIS by season x horizon with block CIs, vs ensemble and baseline
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
    for ax, s in zip(axes, SEASONS):
        for k, (Bm, lab, off) in enumerate([("FluSight-ensemble", "vs CDC FluSight-ensemble", -0.12),
                                           ("FluSight-baseline", "vs FluSight-baseline (persistence)", 0.12)]):
            est, los, his = [], [], []
            for h in range(4):
                f = (lambda s, h: (lambda ix: np.array([season_of(r) == s and int(hh) == h for r, _, hh in ix])))(s, h)
                ix, y, a, b, _, _ = cells(models, "NABD-ensemble", Bm, f)
                e, lo, hi = circular_block_ci(a, b, np.array([r for r, _, _ in ix]), 4, nboot=1000)
                est.append(e); los.append(lo); his.append(hi)
            x = np.arange(4) + off
            est, los, his = map(np.array, (est, los, his))
            ax.errorbar(x, est, yerr=[est - los, his - est], fmt="o", capsize=4, ms=8, color=col[Bm], label=lab)
        ax.axhline(1.0, color="black", lw=0.8)
        ax.axhline(MARGIN, color="red", lw=1.2, ls="--", label="pre-registered margin 1.15")
        ax.set_xticks(range(4), ["h0", "h1", "h2", "h3"])
        ax.set_title(f"Season {s}")
        ax.set_xlabel("FluSight horizon (target week ends h weeks after the reference date)")
    axes[0].set_ylabel("relative WIS (NABD / comparator)\n<1 = NABD better")
    axes[1].legend(fontsize=10, loc="upper left")
    fig.suptitle("NABD v1 vs CDC benchmarks, US state flu admissions (95% block-bootstrap CIs)", fontsize=13)
    fig.tight_layout()
    fig.savefig(FIG / "fig1_rel_wis_season_horizon.png", dpi=160)
    plt.close(fig)

    # fig2: league table
    if lt is not None:
        fig, axes = plt.subplots(1, 2, figsize=(13, 7))
        for ax, s in zip(axes, SEASONS):
            t = lt[(lt.season == s) & (lt.variant == "all included")].sort_values("rel_wis")
            c = ["#d62728" if m == "NABD-ensemble" else "#1f77b4" if m == "FluSight-ensemble" else
                 "#7f7f7f" if m == "FluSight-baseline" else ("#9ecae1" if t.ensemble_of_models.iloc[i] else "#c7c7c7")
                 for i, m in enumerate(t.model)]
            ax.barh(range(len(t)), t.rel_wis, color=c)
            ax.set_yticks(range(len(t)), [m if m in col else "" for m in t.model], fontsize=10)
            ax.invert_yaxis()
            ax.axvline(1.0, color="black", lw=0.8)
            r = int(t.loc[t.model == "NABD-ensemble", "rank"].iloc[0]) if (t.model == "NABD-ensemble").any() else None
            ax.set_title(f"{s}: NABD rank {r} of {len(t)}" if r else f"{s}: NABD not included")
            ax.set_xlabel("relative WIS vs FluSight-baseline (pairwise; <1 better)")
        fig.suptitle("NABD v1 among CDC FluSight hub models (light blue = multi-model ensembles; grey = single models)", fontsize=12)
        fig.tight_layout()
        fig.savefig(FIG / "fig2_league_table.png", dpi=160)
        plt.close(fig)

    # fig3: WIS decomposition by as-of phase
    t = pdc[(pdc.horizon == "ALL") & (pdc.phase.isin(["rising", "flat", "falling"]))]
    fig, ax = plt.subplots(figsize=(11, 5))
    xs, labels = [], []
    x = 0
    for p in ["rising", "flat", "falling"]:
        for m in ["NABD-ensemble", "FluSight-ensemble", "FluSight-baseline"]:
            r = t[(t.phase == p) & (t.model == m)].iloc[0]
            mw = r.mean_wis
            ax.bar(x, mw * r.share_dispersion, color="#9ecae1")
            ax.bar(x, mw * r.share_over, bottom=mw * r.share_dispersion, color="#fdae6b")
            ax.bar(x, mw * r.share_under, bottom=mw * (r.share_dispersion + r.share_over), color="#a1d99b")
            xs.append(x); labels.append(f"{ {'NABD-ensemble': 'NABD', 'FluSight-ensemble': 'CDC ensemble', 'FluSight-baseline': 'CDC baseline'}[m]}\n{p}")
            x += 1
        x += 0.6
    ax.set_xticks(xs, labels, fontsize=9)
    ax.set_ylabel("mean WIS (weekly admissions)")
    from matplotlib.patches import Patch
    ax.legend([Patch(color="#9ecae1"), Patch(color="#fdae6b"), Patch(color="#a1d99b")],
              ["dispersion (interval width)", "overprediction", "underprediction"], fontsize=10)
    ax.set_title("Where the error comes from, by epidemic phase known at forecast time (as-of, 3-wk slope)")
    fig.tight_layout()
    fig.savefig(FIG / "fig3_wis_decomposition.png", dpi=160)
    plt.close(fig)

    # fig4: REV
    r = rev[(rev.subset == "h2 (primary)")]
    fig, ax = plt.subplots(figsize=(8, 5))
    for m in ["NABD-ensemble", "FluSight-ensemble", "FluSight-baseline"]:
        p = r[(r.model == m) & (r.curve.str.startswith("act"))]
        e = r[(r.model == m) & (r.curve.str.startswith("envelope"))]
        ax.plot(p.alpha, p.REV, "o-", color=col[m], label=f"{m}")
        ax.plot(e.alpha, e.REV, ":", color=col[m], alpha=0.7)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xscale("log")
    ax.set_xlabel("cost of acting / loss if unprepared (C/L)")
    ax.set_ylabel("relative economic value (1 = perfect, 0 = no better than base rate)")
    ax.set_ylim(-0.5, 1)
    ax.set_title(f"Decision value: surge ≥3/100k at FluSight horizon 2 (base rate {r.base_rate.iloc[0]:.0%}); dotted = best trigger")
    ax.legend(fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "fig4_rev.png", dpi=160)
    plt.close(fig)


# ---------------------------------------------------------------- summary
def update_summary(d6o, lt, sm, xc, pdc, rev):
    p = ROOT / "results" / "summary.json"
    s = json.loads(p.read_text())
    pr = s["primary"]
    s["primary_verdict"] = pr["non_inferiority"]
    s["primary_text"] = (f"Pre-registered primary endpoint {pr['non_inferiority']}: NABD v1 relative WIS vs the CDC "
                         f"FluSight-ensemble = {pr['rel_wis']:.2f} (95% CI {pr['ci95'][0]:.2f}-{pr['ci95'][1]:.2f}); "
                         f"the non-inferiority margin was {pr['margin']}. NABD v1 is less accurate than the CDC "
                         f"ensemble on US state flu admissions in 2024/25-2025/26.")
    blk = d6o["block"].set_index("analysis")
    r2 = {"declared_in": "docs/DEVIATIONS.md D6, D7, D9, D10, D11 (declared before computing)",
          "sensitivity_block_bootstrap_L4": {k: [round(blk.loc[k, "rel_wis"], 3), round(blk.loc[k, "block4_ci_lo"], 3),
                                                 round(blk.loc[k, "block4_ci_hi"], 3)]
                                             for k in blk.index if not k.startswith("E1")},
          "sensitivity_block_bootstrap_L6_primary": [round(blk.loc["PRIMARY pooled", "block6_ci_lo"], 3),
                                                      round(blk.loc["PRIMARY pooled", "block6_ci_hi"], 3)],
          "national_share_of_WIS": d6o["national_share"].set_index("model").share_of_total_WIS_from_US.round(3).to_dict(),
          "excl_US_national": d6o["excl_us"].set_index("analysis")[["rel_wis", "cluster_ci_lo", "cluster_ci_hi",
                                                                     "block4_ci_lo", "block4_ci_hi"]].round(3).to_dict(orient="index"),
          "per_location_wins": d6o["wins"].to_dict(orient="records"),
          "scorer_crosscheck": xc.to_dict(orient="records")}
    if lt is not None:
        nab = lt[lt.model == "NABD-ensemble"][["season", "variant", "rank", "n_models", "rel_wis"]]
        r2["league_table"] = nab.round(3).to_dict(orient="records")
        r2["league_cells_summary"] = sm.to_dict(orient="records")
    r2["g13_phase_rel_wis_vs_FS_ensemble"] = (pdc[(pdc.horizon == "ALL") & (pdc.model == "NABD-ensemble")]
                                              .set_index("phase").rel_wis_vs_FS_ensemble.round(3).to_dict())
    rv = rev[(rev.subset == "h2 (primary)") & (rev.curve.str.startswith("act"))]
    r2["g13_rev_h2_primary"] = {m: dict(zip(g.alpha, g.REV.round(3))) for m, g in rv.groupby("model")}
    s["round2"] = r2
    ex = blk[blk.index.str.startswith("E1")]
    s["exploratory"] = {"exploratory": True,
                        "note": "E1 splits test cells by REALISED phase (uses future truth). Hypothesis-generating only; "
                                "must never be used as a claim. See docs/DEVIATIONS.md E1.",
                        "E1_rel_wis_by_realised_phase": {k.split("=")[-1]: [round(v.rel_wis, 3), round(v.block4_ci_lo, 3),
                                                                            round(v.block4_ci_hi, 3)] for k, v in ex.iterrows()}}
    p.write_text(json.dumps(s, indent=1, default=str))
    return s


ROUND2_HEADER = "## Round 2: sensitivity analyses and context"


def _f(x, n=3):
    return f"{x:.{n}f}"


def render_summary_section(d6o, lt, xc, pdc, rev, league_status) -> str:
    """Markdown for results/SUMMARY.md's Round-2 section, generated from the tables (audit R3 #14).

    The 'registered CI' column is read from results/tables/endpoints.csv (eval/score.py's registered
    resampler); 'cluster CI (round-2 resampler)' is this module's re-computation, which differs slightly
    (audit R3 #12). Both are shown and labelled.
    """
    ep = pd.read_csv(TAB / "endpoints.csv")
    ep["key"] = ep.analysis.str.replace(" (final truth)", "", regex=False)
    reg = ep.set_index("key")[["ci_lo", "ci_hi"]]
    blk = d6o["block"]
    L = [f"{ROUND2_HEADER} (declared before computing: docs/DEVIATIONS.md D6, D7, D9, D10, D11)", "",
         "*Generated by `eval/round2.py`; do not edit by hand.*", "",
         "None of these changes the pre-registered PRIMARY verdict: **NOT MET**.", "",
         "**D6 sensitivity: circular moving-block bootstrap (L=4; L=6 check), relative WIS with 95% CIs:**", "",
         "| Analysis | rel. WIS | registered CI (endpoints.csv) | cluster CI (round-2 resampler) | block L=4 CI | block L=6 CI |",
         "|---|---|---|---|---|---|"]
    for _, r in blk.iterrows():
        name = r.analysis + (" *(EXPLORATORY, realised phase; not a claim)*" if r.exploratory else "")
        rc = f"{_f(reg.loc[r.analysis,'ci_lo'])}–{_f(reg.loc[r.analysis,'ci_hi'])}" if r.analysis in reg.index else "n/a"
        L.append(f"| {name} | {_f(r.rel_wis)} | {rc} | {_f(r.cluster_ci_lo)}–{_f(r.cluster_ci_hi)} | "
                 f"{_f(r.block4_ci_lo)}–{_f(r.block4_ci_hi)} | {_f(r.block6_ci_lo)}–{_f(r.block6_ci_hi)} |")
    sh = d6o["national_share"].set_index("model").share_of_total_WIS_from_US
    L += ["", f"**National series share of total WIS:** NABD {sh['NABD-ensemble']*100:.1f}%, "
              f"FluSight-ensemble {sh['FluSight-ensemble']*100:.1f}%.", ""]
    for _, r in d6o["excl_us"].iterrows():
        L.append(f"- {r.analysis}: rel. WIS {_f(r.rel_wis)} (cluster CI {_f(r.cluster_ci_lo)}–{_f(r.cluster_ci_hi)}; "
                 f"block L=4 {_f(r.block4_ci_lo)}–{_f(r.block4_ci_hi)})")
    L += ["", "**Per-location wins (NABD WIS sum < comparator's, by location × season):**", ""]
    for _, r in d6o["wins"].iterrows():
        L.append(f"- vs {r.comparator}, {r.season}: {r.nabd_wins}/{r.locations} locations (median ratio {r.median_ratio:.2f})")
    L += ["", f"**D7 league table (pairwise relative WIS vs FluSight-baseline, Cramer et al. 2022; models with ≥50% of "
              f"possible cells).** Status: {league_status}.", ""]
    if lt is not None:
        for s in SEASONS:
            for v in ["all included", "excluding ensembles"]:
                q = lt[(lt.season == s) & (lt.variant == v) & (lt.model == "NABD-ensemble")]
                if len(q):
                    q = q.iloc[0]
                    L.append(f"- {s}, {v}: NABD rank **{int(q['rank'])} of {int(q.n_models)}** (rel. WIS {_f(q.rel_wis)})")
        for s in SEASONS:
            q = lt[(lt.season == s) & (lt.variant == "all included") & (lt.model == "FluSight-ensemble")]
            if len(q):
                q = q.iloc[0]
                L.append(f"  - for reference, CDC FluSight-ensemble {s}: rank {int(q['rank'])} of {int(q.n_models)} "
                         f"(rel. WIS {_f(q.rel_wis)})")
        L += ["", "NABD-ensemble combines only NABD's own two members, so it is not flagged as a multi-model ensemble (D11d)."]
    L += ["", "**D10 / G13 (descriptive): relative WIS vs FluSight-ensemble by as-of phase (3-week slope at forecast "
              "time), all horizons:**", ""]
    q = pdc[(pdc.horizon.astype(str) == "ALL") & (pdc.model == "NABD-ensemble") & (pdc.subset == "all locations")]
    for _, r in q.iterrows():
        L.append(f"- {r.phase}: {_f(r.rel_wis_vs_FS_ensemble)} over {int(r.cells)} cells (NABD WIS shares: dispersion "
                 f"{r.share_dispersion*100:.0f}% / over {r.share_over*100:.0f}% / under {r.share_under*100:.0f}%)")
    rv = rev[(rev.subset == "h2 (primary)") & (rev.curve.str.startswith("act"))]
    alphas = sorted(rv.alpha.unique())
    L += ["", "**Relative economic value** (event ≥3/100k at FluSight horizon h2, the target week ending 2 weeks after the reference date; act when p > C/L; 1 = perfect, 0 = base "
              "rate; no CIs computed, descriptive):", "",
          "| model | " + " | ".join(f"C/L={a:g}" for a in alphas) + " |", "|---|" + "---|" * len(alphas)]
    for m, g in rv.groupby("model"):
        d = dict(zip(g.alpha, g.REV))
        L.append(f"| {m} | " + " | ".join(f"{d[a]:.2f}" for a in alphas) + " |")
    ok = bool(xc["pass"].all())
    L += ["", "Figures (slide-ready): results/figures/fig1_rel_wis_season_horizon.png, fig2_league_table.png, "
              "fig3_wis_decomposition.png, fig4_rev.png.",
          f"Scorer cross-check (D9): {'PASS' if ok else 'FAIL'}. Our WIS vs an independent implementation "
          f"(max abs diff {xc.max_abs_diff.max():.1e} over {int(xc.cells.sum())} cells).", ""]
    return "\n".join(L)


def write_summary_section(d6o, lt, xc, pdc, rev, league_status) -> None:
    p = ROOT / "results" / "SUMMARY.md"
    t = p.read_text() if p.exists() else ""
    i = t.find(ROUND2_HEADER)
    head = (t[:i].rstrip() + "\n\n") if i >= 0 else (t.rstrip() + "\n\n")
    p.write_text(head + render_summary_section(d6o, lt, xc, pdc, rev, league_status))


def main(skip_league=False, fetch_league=False):
    if fetch_league:
        fetch_league_files()
    TAB.mkdir(parents=True, exist_ok=True)
    dates = [d for s in SEASONS for d in season_dates(s)]
    models = {m: load_model(m, dates) for m in ["NABD-ensemble", "FluSight-ensemble", "FluSight-baseline"]}
    xc = scorer_crosscheck(models)
    xc.to_csv(TAB / "scorer_crosscheck.csv", index=False)
    print(xc.to_string())
    d6o = d6(models)
    print(d6o["block"].round(3).to_string()); print(d6o["national_share"]); print(d6o["excl_us"].round(3)); print(d6o["wins"])
    lt = sm = None
    have_hub = (HUB / "model-output").exists() and sum(1 for _ in (HUB / "model-output").iterdir()) > 2
    have_cache = (CACHE / f"league_cell_wis_{league_cache_key()}.pkl").exists()
    if not skip_league and (have_hub or have_cache):
        lt, sm = league(models)
        league_status = "recomputed"
        print(lt[lt.model.isin(["NABD-ensemble", "FluSight-ensemble", "FluSight-baseline"])].round(3).to_string())
        print(sm)
    elif (TAB / "league_table.csv").exists():
        lt, sm = pd.read_csv(TAB / "league_table.csv"), pd.read_csv(TAB / "league_cells_summary.csv")
        league_status = "NOT RECOMPUTED (using committed results/tables/league_table.csv)"
        print("LEAGUE NOT RECOMPUTED (using committed table): hub model-output not checked out and no "
              "matching cache. Run `python -m eval.round2 --fetch-league` to recompute.")
    else:
        league_status = "not available"
    pdc, pus, rev = g13(models)
    print(pdc[pdc.horizon == "ALL"].round(3).to_string())
    print(rev[rev.subset == "h2 (primary)"].round(3).to_string())
    figures(models, lt, pdc, rev)
    s = update_summary(d6o, lt, sm, xc, pdc, rev)
    s["round2"]["league_status"] = league_status
    (ROOT / "results" / "summary.json").write_text(json.dumps(s, indent=1, default=str))
    write_summary_section(d6o, lt, xc, pdc, rev, league_status)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-league", action="store_true")
    ap.add_argument("--fetch-league", action="store_true", help="sparse-checkout all hub models' test-season files first")
    a = ap.parse_args()
    main(a.skip_league, a.fetch_league)
