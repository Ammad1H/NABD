"""Slide-ready figures drawn only from committed results (round 5). No new analysis.

  python3 -m eval.deck_figures
Writes:
  results/gcc/gcc_flu_two_comparators.png   (per-country + pooled influenza relative WIS vs past-season pattern
                                              and vs persistence; pooled 95% CIs from results/gcc/summary.json)
  results/uae/season_shape_flu.png          (WHO FluNet UAE sentinel influenza positivity by season, aligned at
                                              ISO week 27; 2024/25 and 2025/26 highlighted)
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DARK, TEAL, LIGHT, RUST, GREY = "#0F3D3E", "#1F7A7A", "#7FB3AE", "#B5482F", "#6B7A80"


def gcc_two_comparators(out=ROOT / "results" / "gcc" / "gcc_flu_two_comparators.png"):
    pc = pd.read_csv(ROOT / "results" / "gcc" / "tables" / "per_country.csv")
    f = pc[pc.series == "flu"].set_index("country")
    res = json.loads((ROOT / "results" / "gcc" / "summary.json").read_text())["results"]
    pa, pp = res["flu_NABD-UAE-v1_vs_seasonal-analog"], res["PRIMARY_flu_v1_vs_persistence"]
    names = {"OMN": "Oman", "QAT": "Qatar", "SAU": "Saudi Arabia"}
    labels = [names.get(c, c) for c in f.index] + ["Pooled"]
    va = list(f["v1/analog"]) + [pa["rel_wis"]]
    vp = list(f["v1/persistence"]) + [pp["rel_wis"]]
    fig, ax = plt.subplots(figsize=(10, 5.6), dpi=200)
    x = list(range(len(labels)))
    w = 0.38
    ax.bar([i - w / 2 for i in x], va, w, color=DARK, label="vs past-season pattern (pre-registered secondary)")
    ax.bar([i + w / 2 for i in x], vp, w, color=LIGHT, label="vs last week carried forward (pre-registered primary)")
    for i, (a, b) in enumerate(zip(va, vp)):
        if i == len(labels) - 1:   # pooled: labels inside the bars so the CI whiskers stay readable
            ax.text(i - w / 2, a - 0.14, f"{a:.2f}", ha="center", va="top", fontsize=13, color="white", fontweight="bold")
            ax.text(i + w / 2, b - 0.10, f"{b:.2f}", ha="center", va="top", fontsize=13, color=DARK, fontweight="bold")
            continue
        ax.text(i - w / 2, a + 0.02, f"{a:.2f}", ha="center", va="bottom", fontsize=13, color=DARK, fontweight="bold")
        ax.text(i + w / 2, b + 0.02, f"{b:.2f}", ha="center", va="bottom", fontsize=13, color="#33424A")
    k = len(labels) - 1
    for xpos, r in ((k - w / 2, pa), (k + w / 2, pp)):
        lo, hi = r["ci95"]
        ax.errorbar([xpos], [r["rel_wis"]], yerr=[[r["rel_wis"] - lo], [hi - r["rel_wis"]]], fmt="none", ecolor=RUST,
                    capsize=6, lw=2)
    ax.axhline(1.0, color=GREY, lw=1.5, ls="--")
    ax.text(k + 0.62, 1.01, "1 = no better", ha="right", va="bottom", fontsize=12, color=GREY)
    ax.set_xticks(x, labels, fontsize=15)
    ax.set_ylim(0, 1.25)
    ax.set_ylabel("Influenza forecast error, NABD ÷ comparator\n(relative WIS; lower is better)", fontsize=13)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(loc="upper left", fontsize=12, frameon=False)
    ax.set_title("Out-of-sample influenza test: Oman, Qatar, Saudi Arabia (pooled bars: 95% CI)", fontsize=14,
                 color=DARK, loc="left")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return out


def season_shape_flu(out=ROOT / "results" / "uae" / "season_shape_flu.png"):
    import sys
    sys.path.insert(0, str(ROOT))
    from app import data_io
    obs = data_io.load_uae_observed()
    sf = data_io.season_frame(obs, "flu")
    fig, ax = plt.subplots(figsize=(11, 5.6), dpi=200)
    cur = sf.season.max()
    hi = {"2024/25": RUST, "2025/26": DARK}
    for season, g in sf.groupby("season"):
        g = g.sort_values("x")
        lab = f"{season}/{str(season + 1)[-2:]}"
        col = hi.get(lab, "#B9C6C3")
        lw = 3.0 if lab in hi else 1.6
        if season == cur:
            col, lw = TEAL, 3.0
            lab = f"{lab} (this season, so far)"
        ax.plot(g["x"], g["value"], color=col, lw=lw, label=lab)
    ax.set_xlabel("weeks since ISO week 27", fontsize=13)
    ax.set_ylabel("influenza positivity, sentinel (%)", fontsize=13)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(fontsize=11, frameon=False, loc="upper right")
    ax.set_title("UAE influenza, WHO FluNet sentinel: a months-long plateau (2024/25) vs a sharp spike (2025/26)",
                 fontsize=13, color=DARK, loc="left")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    return out


if __name__ == "__main__":
    print(gcc_two_comparators())
    print(season_shape_flu())
