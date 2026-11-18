"""UAE development check, restated (DEVIATIONS S7, post hoc, NON-CONFIRMATORY).

Reads only the committed development scores `results/pool/dev/scores_chosen.csv` written by `pool.dev`
(forward-in-time: for evaluation season S the pooled model is fitted on other folds' countries, seasons < S;
the UAE's fold is left out of the fit). Nothing is refitted; no forecast, model or lock changes.

  python3 -m pool.uae_devcheck      # writes results/pool/uae_devcheck/{SUMMARY.md,summary.json}
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "results" / "pool" / "dev" / "scores_chosen.csv"
OUT = ROOT / "results" / "pool" / "uae_devcheck"
MODELS = ["NABD-Pool", "NABD-UAE-v1", "persistence", "seasonal-analog"]
LABEL = {"NABD-Pool": "Pooled model (NABD-Pool)", "NABD-UAE-v1": "UAE own-record model (v1)",
         "persistence": "Last week carried forward", "seasonal-analog": "Past-season pattern"}
B, SEED, BLOCK = 2000, 0, 4


def wide(country: str = "ARE") -> pd.DataFrame:
    s = pd.read_csv(SRC)
    s = s[s.country == country]
    w = s.pivot_table(index=["season", "i", "h"], columns="model", values="wis").dropna()
    assert set(MODELS) <= set(w.columns), w.columns
    return w


def ratio(w: pd.DataFrame, a: str, b: str) -> float:
    return float(w[a].sum() / w[b].sum())


def block_ci(w: pd.DataFrame, a: str, b: str) -> list[float]:
    """Moving-block bootstrap over forecast origins within each season (all horizons of an origin kept
    together; blocks of 4 consecutive origins), B = 2000, seed 0."""
    rng = np.random.default_rng(SEED)
    per = w.groupby(level=["season", "i"])[[a, b]].sum()
    seasons = {S: g.droplevel(0).sort_index() for S, g in per.groupby(level="season")}
    stats = []
    for _ in range(B):
        num = den = 0.0
        for g in seasons.values():
            n = len(g)
            nb = int(np.ceil(n / BLOCK))
            starts = rng.integers(0, max(n - BLOCK + 1, 1), nb)
            idx = np.concatenate([np.arange(s0, min(s0 + BLOCK, n)) for s0 in starts])[:n]
            num += g[a].values[idx].sum()
            den += g[b].values[idx].sum()
        stats.append(num / den)
    return [round(float(np.quantile(stats, 0.025)), 3), round(float(np.quantile(stats, 0.975)), 3)]


def main() -> dict:
    w = wide()
    raw = pd.read_csv(SRC)
    are = raw[raw.country == "ARE"]
    res = dict(source=str(SRC.relative_to(ROOT)), status="POST HOC, NON-CONFIRMATORY (DEVIATIONS S7)",
               cells=int(len(w)), seasons=sorted(int(s) for s in w.index.get_level_values(0).unique()),
               origins=int(w.groupby(level=["season", "i"]).ngroups), horizons_data_weeks=[1, 2, 3, 4])
    res["overall"] = {}
    for a, b in [("NABD-Pool", "persistence"), ("NABD-Pool", "NABD-UAE-v1"),
                 ("NABD-UAE-v1", "persistence"), ("NABD-Pool", "seasonal-analog")]:
        res["overall"][f"{a} / {b}"] = dict(rel_wis=round(ratio(w, a, b), 3), ci95=block_ci(w, a, b))
    res["by_season"] = {str(S): {m: round(ratio(g, m, "persistence"), 3) for m in MODELS}
                        | {"NABD-Pool / NABD-UAE-v1": round(ratio(g, "NABD-Pool", "NABD-UAE-v1"), 3)}
                        for S, g in w.groupby(level="season")}
    res["by_horizon_vs_persistence"] = {str(h): {m: round(ratio(g, m, "persistence"), 3) for m in MODELS}
                                        for h, g in w.groupby(level="h")}
    res["coverage"] = {m: dict(cov50=round(float(are[are.model == m].cov50.mean()), 2),
                               cov95=round(float(are[are.model == m].cov95.mean()), 2)) for m in MODELS}
    res["mean_wis_pp"] = {m: round(float(w[m].mean()), 3) for m in MODELS}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(res, indent=1) + "\n")
    (OUT / "SUMMARY.md").write_text(render(res))
    return res


def render(r: dict) -> str:
    o = r["overall"]
    pp, pv, vp = o["NABD-Pool / persistence"], o["NABD-Pool / NABD-UAE-v1"], o["NABD-UAE-v1 / persistence"]
    L = ["# UAE development check: the pooled model on the UAE's own seasons (POST HOC, NON-CONFIRMATORY)", "",
         "_Declared in `docs/DEVIATIONS.md` S7. Restates numbers already in `results/pool/SUMMARY.md` "
         "(\"already-seen countries\") with a per-season split, a per-horizon split and a confidence interval. "
         "Nothing is refitted._", "",
         "**How these forecasts were made.** Forward in time: to forecast UAE season S, the pooled model was "
         "fitted only on other countries (the UAE's fold left out) and only on seasons before S. The UAE "
         "contributes only its own past weeks and earlier seasons as inputs at each forecast date, the same "
         "information the UAE's own-record model gets.", "",
         "**Why it is not confirmatory.** UAE data were part of the development set used to choose the pooled "
         "model's configuration (one of 45 development countries), and the author had seen UAE data before. "
         "The confirmatory UAE test is prospective and locked (`docs/PREREG-LIVE.md`); its result is due after "
         "15 April 2027.", "",
         f"Influenza, UAE sentinel series, seasons {', '.join(f'{s}/{(s + 1) % 100:02d}' for s in r['seasons'])}, "
         f"{r['origins']} forecast weeks x 4 horizons = {r['cells']} forecasts. Relative WIS below 1 means less "
         "error than the comparator. 95% CI: moving-block bootstrap over forecast weeks within season "
         "(blocks of 4, B = 2000, seed 0).", "",
         "## Headline", "",
         f"- Pooled model vs last week carried forward: **{pp['rel_wis']:.3f} (95% CI {pp['ci95'][0]:.3f}–"
         f"{pp['ci95'][1]:.3f})**, i.e. about {round(100 * (1 - pp['rel_wis']))}% less error.",
         f"- Pooled model vs the UAE's own-record model (v1): {pv['rel_wis']:.3f} "
         f"(95% CI {pv['ci95'][0]:.3f}–{pv['ci95'][1]:.3f}).",
         f"- For reference, own-record model vs last week on the same forecasts: {vp['rel_wis']:.3f} "
         f"(95% CI {vp['ci95'][0]:.3f}–{vp['ci95'][1]:.3f}).", "",
         "## By season (relative WIS vs last week carried forward)", "",
         "| Season | Pooled | Own-record v1 | Past-season pattern | Pooled / v1 |", "|---|---|---|---|---|"]
    for S, d in r["by_season"].items():
        s = int(S)
        L.append(f"| {s}/{(s + 1) % 100:02d} | {d['NABD-Pool']:.3f} | {d['NABD-UAE-v1']:.3f} | "
                 f"{d['seasonal-analog']:.3f} | {d['NABD-Pool / NABD-UAE-v1']:.3f} |")
    L += ["", "Reading: the pooled model had less error than last week in both seasons. The own-record model "
          "swung from worse than last week to better than it, and beat the pooled model in the second season.",
          "", "## By horizon (data weeks ahead; relative WIS vs last week)", "",
          "| Horizon | Pooled | Own-record v1 | Past-season pattern |", "|---|---|---|---|"]
    for h, d in r["by_horizon_vs_persistence"].items():
        L.append(f"| {h} | {d['NABD-Pool']:.3f} | {d['NABD-UAE-v1']:.3f} | {d['seasonal-analog']:.3f} |")
    L += ["", "## Interval coverage (target 0.50 / 0.95)", "", "| Model | 50% | 95% |", "|---|---|---|"]
    for m, c in r["coverage"].items():
        L.append(f"| {LABEL[m]} | {c['cov50']:.2f} | {c['cov95']:.2f} |")
    L += ["", "## Limits", "",
          "- Two seasons, one country; a week-block bootstrap cannot capture season-to-season variation.",
          "- Finalised (revised) FluNet data; positivity, not hospital load.",
          "- These cells differ from `results/uae/SUMMARY-v2.md` (the v1 parity result, 1.002): that "
          "analysis also scores 2023/24, when the UAE had one earlier season and v1 lost heavily; the pool "
          "harness needs two own earlier seasons, so 2023/24 is not scored here.",
          "- Never a headline without the words \"development check, not a confirmatory test\".", ""]
    return "\n".join(L)


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
