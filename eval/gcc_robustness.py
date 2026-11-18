"""GCC influenza robustness checks, committed and reproducible (claims ledger A5; DEVIATIONS S8).

The R3 review agent ran these from uncommitted scratch scripts. This file recomputes them from the committed
per-cell scores `results/gcc/tables/scores_long.csv` (no refit, no new data):
  - leave-one-country-out: the pooled relative WIS with each of OMN, QAT, SAU dropped in turn;
  - two-stage cluster bootstrap: resample countries, then seasons within each drawn country (B = 2000, seed 0);
  - by horizon.

  python3 -m eval.gcc_robustness     # writes results/gcc/robustness.json and results/gcc/ROBUSTNESS.md
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "results" / "gcc" / "tables" / "scores_long.csv"
A, BASE = "NABD-UAE-v1", "persistence"
B, SEED = 2000, 0


def cells(series: str) -> pd.DataFrame:
    s = pd.read_csv(SRC)
    s = s[(s.series == series) & s.model.isin([A, BASE])]
    w = s.pivot_table(index=["country", "season", "origin", "horizon"], columns="model", values="wis").dropna()
    return w.reset_index()


def ratio(w: pd.DataFrame) -> float:
    return float(w[A].sum() / w[BASE].sum())


def two_stage(w: pd.DataFrame) -> list[float]:
    rng = np.random.default_rng(SEED)
    cs = w.groupby(["country", "season"])[[A, BASE]].sum()
    by_c = {c: g.droplevel(0) for c, g in cs.groupby(level="country")}
    countries = sorted(by_c)
    stats = []
    for _ in range(B):
        num = den = 0.0
        for c in rng.choice(countries, len(countries), replace=True):
            g = by_c[c]
            k = rng.integers(0, len(g), len(g))
            num += g[A].values[k].sum()
            den += g[BASE].values[k].sum()
        stats.append(num / den)
    return [round(float(np.quantile(stats, .025)), 3), round(float(np.quantile(stats, .975)), 3)]


def run(series: str) -> dict:
    w = cells(series)
    return dict(cells=int(len(w)), pooled=round(ratio(w), 3),
                leave_one_country_out={c: round(ratio(w[w.country != c]), 3) for c in sorted(w.country.unique())},
                two_stage_bootstrap_ci95=two_stage(w),
                by_horizon={int(h): round(ratio(g), 3) for h, g in w.groupby("horizon")})


def main() -> dict:
    res = dict(source=str(SRC.relative_to(ROOT)), comparison=f"{A} / {BASE}", flu=run("flu"), rsv=run("rsv"))
    out = ROOT / "results" / "gcc"
    (out / "robustness.json").write_text(json.dumps(res, indent=1) + "\n")
    f, r = res["flu"], res["rsv"]
    lo = min(f["leave_one_country_out"].values()), max(f["leave_one_country_out"].values())
    md = ["# GCC test: robustness checks (committed reproduction of the R3 review's scratch reruns)", "",
          "_Recomputed from `results/gcc/tables/scores_long.csv` by `eval/gcc_robustness.py`. No refit. "
          "These are sensitivity checks on a locked result, not new endpoints._", "",
          f"**Influenza** (frozen v1 method vs last week carried forward): pooled {f['pooled']:.3f}.",
          f"- Leave one country out: {lo[0]:.3f}–{lo[1]:.3f} "
          f"({', '.join(f'without {c} {v:.3f}' for c, v in f['leave_one_country_out'].items())}).",
          f"- Two-stage bootstrap (countries, then seasons; B = {B}, seed {SEED}): 95% CI "
          f"{f['two_stage_bootstrap_ci95'][0]:.3f}–{f['two_stage_bootstrap_ci95'][1]:.3f}.",
          f"- By horizon: {', '.join(f'{h}: {v:.3f}' for h, v in f['by_horizon'].items())}.", "",
          f"**RSV** (secondary): pooled {r['pooled']:.3f}; two-stage bootstrap 95% CI "
          f"{r['two_stage_bootstrap_ci95'][0]:.3f}–{r['two_stage_bootstrap_ci95'][1]:.3f}; leave one country out "
          f"{', '.join(f'without {c} {v:.3f}' for c, v in r['leave_one_country_out'].items())}.", "",
          "With three countries, a country-level bootstrap is coarse; read the intervals as a stress test.", ""]
    (out / "ROBUSTNESS.md").write_text("\n".join(md))
    return res


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
