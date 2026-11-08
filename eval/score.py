"""Score test-season forecasts and report every endpoint in PROTOCOL §7.

Outputs: results/tables/*.csv, results/figures/*.png, results/summary.json, results/SUMMARY.md
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from models.data import (QUANTILES, final_truth, first_release_truth, load_comparator,
                         season_dates)
from eval.wis import coverage, wis

ROOT = Path(__file__).resolve().parents[1]
FC = ROOT / "results" / "forecasts"
TAB = ROOT / "results" / "tables"
FIG = ROOT / "results" / "figures"
SEED = 20261108
B = 2000
MARGIN = 1.15
SEASONS = ["2024/25", "2025/26"]
NABD = ["NABD-ensemble", "NABD-GLM", "NABD-EEQ"]
COMP = ["FluSight-ensemble", "FluSight-baseline"]


def _season_of(ref: pd.Timestamp) -> str:
    for s in SEASONS:
        d = season_dates(s)
        if d[0] <= ref <= d[-1]:
            return s
    return "other"


def load_model(model: str, dates) -> pd.DataFrame:
    """Return wide frame indexed by (reference_date, location, horizon) with 23 quantile columns."""
    parts = []
    for R in dates:
        if model in COMP:
            d = load_comparator(model, R)
            if d is None:
                continue
            d = d.assign(reference_date=R)
        else:
            p = FC / model / f"{R.date().isoformat()}.csv"
            if not p.exists():
                continue
            d = pd.read_csv(p, dtype={"location": str})
            d = d.rename(columns={"output_type_id": "q"})
            d["reference_date"] = pd.Timestamp(R)
        d["q"] = d["q"].astype(float).round(3)
        parts.append(d[["reference_date", "location", "horizon", "q", "value"]])
    df = pd.concat(parts)
    w = df.pivot_table(index=["reference_date", "location", "horizon"], columns="q", values="value", aggfunc="first")
    w = w.reindex(columns=np.round(QUANTILES, 3))
    w = w.dropna()                                    # complete 23-quantile forecasts only
    return w


def attach_truth(idx: pd.MultiIndex, truth: pd.DataFrame) -> np.ndarray:
    t = {(l, d): v for l, d, v in zip(truth.location, truth.target_end_date, truth.truth)}
    return np.array([t.get((l, r + pd.Timedelta(days=7 * int(h))), np.nan) for r, l, h in idx])


def boot_ratio(a: np.ndarray, b: np.ndarray, refs: np.ndarray, rng) -> tuple[float, float, float]:
    u, inv = np.unique(refs, return_inverse=True)
    sa = np.bincount(inv, weights=a, minlength=len(u))
    sb = np.bincount(inv, weights=b, minlength=len(u))
    est = sa.sum() / sb.sum()
    draws = rng.integers(0, len(u), size=(B, len(u)))
    r = sa[draws].sum(1) / sb[draws].sum(1)
    return float(est), float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))


def compare(models: dict, A: str, Bm: str, truth: pd.DataFrame, filt=None, log=False, seed_off=0):
    idx = models[A].index.intersection(models[Bm].index)
    if filt is not None:
        idx = idx[filt(idx)]
    y = attach_truth(idx, truth)
    ok = np.isfinite(y)
    idx, y = idx[ok], y[ok]
    qa = models[A].loc[idx].to_numpy(float)
    qb = models[Bm].loc[idx].to_numpy(float)
    if log:
        qa, qb, y = np.log1p(qa), np.log1p(qb), np.log1p(y)
    wa, wb = wis(qa, y), wis(qb, y)
    refs = np.array([r for r, _, _ in idx])
    est, lo, hi = boot_ratio(wa, wb, refs, np.random.default_rng(SEED + seed_off))
    return {"A": A, "B": Bm, "n_cells": int(len(idx)), "n_dates": int(len(np.unique(refs))),
            "wis_A": float(wa.mean()), "wis_B": float(wb.mean()), "rel_wis": est, "ci_lo": lo, "ci_hi": hi,
            "cov50_A": float(coverage(qa, y, 0.5).mean()), "cov95_A": float(coverage(qa, y, 0.95).mean()),
            "cov50_B": float(coverage(qb, y, 0.5).mean()), "cov95_B": float(coverage(qb, y, 0.95).mean())}


def main() -> dict:
    TAB.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)
    dates = [d for s in SEASONS for d in season_dates(s)]
    models = {m: load_model(m, dates) for m in NABD + COMP if (m in COMP or (FC / m).exists())}
    ft, fr = final_truth(), first_release_truth()
    possible = len(dates) * 53 * 4

    rows = []
    def add(tag, A, Bm, truth=ft, filt=None, log=False, off=0):
        r = compare(models, A, Bm, truth, filt, log, off); r["analysis"] = tag; rows.append(r); return r

    prim = add("PRIMARY pooled (final truth)", "NABD-ensemble", "FluSight-ensemble")
    s1 = add("S1 pooled vs baseline", "NABD-ensemble", "FluSight-baseline", off=1)
    add("ref: FluSight-ensemble vs baseline", "FluSight-ensemble", "FluSight-baseline", off=2)
    for i, s in enumerate(SEASONS):
        f = (lambda s: (lambda idx: np.array([_season_of(r) == s for r, _, _ in idx])))(s)
        add(f"S3 season {s}", "NABD-ensemble", "FluSight-ensemble", filt=f, off=10 + i)
        add(f"S3 season {s} vs baseline", "NABD-ensemble", "FluSight-baseline", filt=f, off=20 + i)
    for h in range(4):
        f = (lambda h: (lambda idx: np.array([int(hh) == h for _, _, hh in idx])))(h)
        add(f"S3 horizon {h}", "NABD-ensemble", "FluSight-ensemble", filt=f, off=30 + h)
        add(f"S3 horizon {h} vs baseline", "NABD-ensemble", "FluSight-baseline", filt=f, off=40 + h)
    add("S4 first-release truth", "NABD-ensemble", "FluSight-ensemble", truth=fr, off=50)
    for j, m in enumerate(["NABD-GLM", "NABD-EEQ"]):
        add(f"S5 member {m}", m, "FluSight-ensemble", off=60 + j)
    add("S6 log-scale WIS", "NABD-ensemble", "FluSight-ensemble", log=True, off=70)
    add("S6 log-scale WIS vs baseline", "NABD-ensemble", "FluSight-baseline", log=True, off=71)
    fus = lambda idx: np.array([l == "US" for _, l, _ in idx])
    add("S7 national (US)", "NABD-ensemble", "FluSight-ensemble", filt=fus, off=80)
    tab = pd.DataFrame(rows)
    cols = ["analysis", "A", "B", "n_cells", "n_dates", "rel_wis", "ci_lo", "ci_hi", "wis_A", "wis_B",
            "cov50_A", "cov95_A", "cov50_B", "cov95_B"]
    tab[cols].to_csv(TAB / "endpoints.csv", index=False)

    # all-models common-cell overview
    idx = None
    for m in models.values():
        idx = m.index if idx is None else idx.intersection(m.index)
    y = attach_truth(idx, ft); ok = np.isfinite(y); idx, y = idx[ok], y[ok]
    ov = []
    for name, m in models.items():
        q = m.loc[idx].to_numpy(float)
        ov.append({"model": name, "n_cells": len(idx), "mean_wis": float(wis(q, y).mean()),
                   "cov50": float(coverage(q, y, 0.5).mean()), "cov95": float(coverage(q, y, 0.95).mean())})
    ov = pd.DataFrame(ov)
    ens_w = ov.set_index("model").loc["FluSight-ensemble", "mean_wis"]
    base_w = ov.set_index("model").loc["FluSight-baseline", "mean_wis"]
    ov["rel_wis_vs_FluSight_ensemble"] = ov.mean_wis / ens_w
    ov["rel_wis_vs_FluSight_baseline"] = ov.mean_wis / base_w
    ov.to_csv(TAB / "overview_common_cells.csv", index=False)

    # cell coverage
    cc = pd.DataFrame([{"model": n, "complete_cells": len(m), "possible": possible,
                        "share": len(m) / possible} for n, m in models.items()])
    cc.to_csv(TAB / "cell_coverage.csv", index=False)

    verdict = "MET" if prim["ci_hi"] < MARGIN else "NOT MET"
    s2_ok = 0.90 <= prim["cov95_A"] <= 0.98
    summary = {
        "protocol": "docs/PROTOCOL.md v1.0 (frozen; see docs/FREEZE.md)",
        "primary": {"comparison": "NABD-ensemble / FluSight-ensemble, pooled 2024/25+2025/26, 53 locations, h0-3, final truth",
                    "rel_wis": prim["rel_wis"], "ci95": [prim["ci_lo"], prim["ci_hi"]], "margin": MARGIN,
                    "non_inferiority": verdict, "n_cells": prim["n_cells"], "n_dates": prim["n_dates"]},
        "S1_vs_baseline": {"rel_wis": s1["rel_wis"], "ci95": [s1["ci_lo"], s1["ci_hi"]],
                           "better_than_baseline": s1["ci_hi"] < 1.0},
        "S2_coverage": {"cov50": prim["cov50_A"], "cov95": prim["cov95_A"], "cov95_in_0.90_0.98": bool(s2_ok),
                        "flusight_ensemble_cov50": prim["cov50_B"], "flusight_ensemble_cov95": prim["cov95_B"]},
        "primary_verdict": verdict,
        "primary_text": (f"Pre-registered primary endpoint {verdict}: NABD v1 relative WIS vs the CDC FluSight-ensemble = "
                         f"{prim['rel_wis']:.2f} (95% CI {prim['ci_lo']:.2f}-{prim['ci_hi']:.2f}); the non-inferiority "
                         f"margin was {MARGIN}."),
        "chronos2": "NOT RUN HERE (weights unavailable in build environment)",
        "tables": "results/tables/endpoints.csv, overview_common_cells.csv, cell_coverage.csv, vintage_flags.csv",
    }
    (ROOT / "results" / "summary.json").write_text(json.dumps(summary, indent=1))
    _figures(models, tab, ft)
    _summary_md(summary, tab, ov)
    print(json.dumps(summary, indent=1))
    return summary


def _figures(models, tab, ft):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    # 1. relative WIS by horizon
    h = tab[tab.analysis.str.match(r"S3 horizon \d$")]
    hb = tab[tab.analysis.str.match(r"S3 horizon \d vs baseline")]
    fig, ax = plt.subplots(figsize=(6, 3.6))
    x = np.arange(4)
    for d, lab, off in [(h, "vs FluSight-ensemble", -0.12), (hb, "vs FluSight-baseline", 0.12)]:
        ax.errorbar(x + off, d.rel_wis, yerr=[d.rel_wis - d.ci_lo, d.ci_hi - d.rel_wis], fmt="o", capsize=3, label=lab)
    ax.axhline(1.0, color="grey", lw=0.8); ax.axhline(MARGIN, color="red", lw=0.8, ls="--", label="non-inferiority margin 1.15")
    ax.set_xticks(x, [f"h{i}" for i in x]); ax.set_ylabel("relative WIS (NABD-ensemble / comparator)")
    ax.set_title("NABD-ensemble, US state flu admissions, 2024/25-2025/26"); ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(FIG / "rel_wis_by_horizon.png", dpi=150); plt.close(fig)

    # 2. coverage
    ov = pd.read_csv(TAB / "overview_common_cells.csv")
    fig, ax = plt.subplots(figsize=(6, 3.4))
    xi = np.arange(len(ov))
    ax.bar(xi - 0.2, ov.cov50, 0.4, label="50% interval"); ax.bar(xi + 0.2, ov.cov95, 0.4, label="95% interval")
    ax.axhline(0.5, color="C0", ls=":"); ax.axhline(0.95, color="C1", ls=":")
    ax.set_xticks(xi, ov.model, rotation=20, fontsize=7); ax.set_ylim(0, 1); ax.set_ylabel("empirical coverage")
    ax.set_title("Interval coverage (common cells)"); ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(FIG / "coverage.png", dpi=150); plt.close(fig)

    # 3. example fan charts (h=1) for two states
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    tmap = ft.set_index(["location", "target_end_date"]).truth
    for ax, loc, name in zip(axes, ["06", "48"], ["California", "Texas"]):
        for mname, col in [("NABD-ensemble", "C3"), ("FluSight-ensemble", "C0")]:
            m = models[mname]
            sub = m[(m.index.get_level_values(1) == loc) & (m.index.get_level_values(2) == 1)]
            t = pd.DatetimeIndex([r + pd.Timedelta(days=7) for r in sub.index.get_level_values(0)])
            # break the band at the off-season gap so seasons are not joined
            seg = np.concatenate([[0], np.cumsum(np.diff(t.values).astype("timedelta64[D]").astype(int) > 7)])
            for k_, sgi in enumerate(np.unique(seg)):
                mm = seg == sgi
                ax.fill_between(t[mm], sub[0.025][mm], sub[0.975][mm], color=col, alpha=0.15)
                ax.fill_between(t[mm], sub[0.25][mm], sub[0.75][mm], color=col, alpha=0.3)
                ax.plot(t[mm], sub[0.5][mm], color=col, lw=1, label=f"{mname} (h1)" if k_ == 0 else None)
        tr = tmap.loc[loc]
        tr = tr[(tr.index >= pd.Timestamp("2024-11-01")) & (tr.index <= pd.Timestamp("2026-06-15"))]
        ax.plot(tr.index, tr.values, "k.", ms=3, label="final truth")
        ax.set_title(f"{name}: 1-week-ahead forecasts (50%/95% bands)", fontsize=9); ax.legend(fontsize=6)
        import matplotlib.dates as mdates
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y")); ax.tick_params(axis="x", labelsize=7)
        ax.set_ylabel("weekly flu admissions")
    fig.tight_layout(); fig.savefig(FIG / "fan_chart_CA_TX_h1.png", dpi=150); plt.close(fig)


def _summary_md(s, tab, ov):
    p = s["primary"]
    lines = [
        "# NABD US-A results (pre-registered; PROTOCOL v1.0)", "",
        f"**PRIMARY:** NABD-ensemble vs CDC FluSight-ensemble: relative WIS **{p['rel_wis']:.3f}** "
        f"(95% CI {p['ci95'][0]:.3f}–{p['ci95'][1]:.3f}), margin {p['margin']}: **non-inferiority {p['non_inferiority']}**. "
        f"{p['n_cells']} cells, {p['n_dates']} reference dates, 2024/25 + 2025/26, 53 locations, h0–3, final truth.", "",
        f"**S1:** vs FluSight-baseline (persistence): relative WIS **{s['S1_vs_baseline']['rel_wis']:.3f}** "
        f"(95% CI {s['S1_vs_baseline']['ci95'][0]:.3f}–{s['S1_vs_baseline']['ci95'][1]:.3f}).", "",
        f"**S2:** NABD 50% coverage {s['S2_coverage']['cov50']:.3f}, 95% coverage {s['S2_coverage']['cov95']:.3f} "
        f"(FluSight-ensemble {s['S2_coverage']['flusight_ensemble_cov50']:.3f} / {s['S2_coverage']['flusight_ensemble_cov95']:.3f}).", "",
        "Chronos-2: NOT RUN in the build environment (weights blocked); excluded from the ensemble.", "",
        "## All endpoints", "",
        "| Analysis | A | B | cells | rel. WIS | 95% CI | cov50 A | cov95 A |", "|---|---|---|---|---|---|---|---|",
    ]
    for _, r in tab.iterrows():
        lines.append(f"| {r.analysis} | {r.A} | {r.B} | {r.n_cells} | {r.rel_wis:.3f} | {r.ci_lo:.3f}–{r.ci_hi:.3f} | {r.cov50_A:.2f} | {r.cov95_A:.2f} |")
    lines += ["", "## All models on common cells", "", "| Model | cells | mean WIS | rel. vs FS-ensemble | rel. vs FS-baseline | cov50 | cov95 |",
              "|---|---|---|---|---|---|---|"]
    for _, r in ov.iterrows():
        lines.append(f"| {r.model} | {r.n_cells} | {r.mean_wis:.1f} | {r.rel_wis_vs_FluSight_ensemble:.3f} | {r.rel_wis_vs_FluSight_baseline:.3f} | {r.cov50:.2f} | {r.cov95:.2f} |")
    lines += ["", "Figures: results/figures/rel_wis_by_horizon.png, coverage.png, fan_chart_CA_TX_h1.png.",
              "Relative WIS here = ratio of sums (CI: block bootstrap over reference dates, B=2000, seed 20261108). "
              "The overview table uses ratio of means on all-model common cells, so it can differ slightly from pairwise rows."]
    (ROOT / "results" / "SUMMARY.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
