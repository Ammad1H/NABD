"""Zero-shot foundation-model benchmark on the S1 held-out cells (DEVIATIONS W1; POST HOC, EXPLORATORY).

  python3 -m fm.benchmark            # needs: pip install torch chronos-forecasting, and Hugging Face access

Reads the stored S1 forecasts (results/pool/tables/forecasts_heldout.csv.gz) and the locked series
(pool.features.load); writes results/fm/. No S1 model is refitted.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from pool import config as C
from pool import harness as Hn
from pool.features import load
from uae.models import QUANTILES, expit

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "results" / "pool" / "tables"
OUT = ROOT / "results" / "fm"
MODEL_ID = "amazon/chronos-2"
FM, FM_PCT, ENS, POOLM, LOCAL = "Chronos-2 (zero-shot)", "Chronos-2 (zero-shot, percent input)", "Pool+FM", "NABD-Pool", "NABD-UAE-v1"
Q = [float(q) for q in QUANTILES]
QCOLS = [f"q{q:g}" for q in Q]


def stored() -> tuple[pd.DataFrame, pd.DataFrame]:
    """S1 forecasts (qv arrays) and the evaluation frame, restricted to the S1 common cells."""
    W = pd.read_csv(POOL / "forecasts_heldout.csv.gz").dropna(subset=QCOLS + ["obs"])
    S = pd.read_csv(POOL / "scores_long.csv", usecols=Hn.KEYS + ["n_own"]).drop_duplicates(Hn.KEYS)
    W = W.merge(S, on=Hn.KEYS)
    ev = W[Hn.KEYS + ["obs", "origin", "n_own"]].drop_duplicates(Hn.KEYS)
    fc = W[Hn.KEYS + ["model"]].copy()
    fc["qv"] = list(W[QCOLS].values)
    return fc, ev


def chronos_forecasts(ev: pd.DataFrame, scale: str, batch: int = 64) -> tuple[pd.DataFrame, str]:
    """One zero-shot forecast per origin; context = the country's own series up to the origin."""
    import torch
    from chronos import Chronos2Pipeline
    from huggingface_hub import model_info
    rev = model_info(MODEL_ID).sha
    pipe = Chronos2Pipeline.from_pretrained(MODEL_ID, revision=rev, device_map="cpu")
    D = load(ROOT / "data" / "raw" / "flunet_pool_held.csv", sorted(ev.country.unique()))
    origins = ev[["country", "season", "i"]].drop_duplicates().reset_index(drop=True)
    ctx = []
    for r in origins.itertuples():
        x = D[r.country]["x"]
        if scale == "logit":
            s = x.y.values[: r.i + 1]
        else:
            s = np.where(np.isnan(x.y.values), np.nan, x.pos.values / x.specimens.values * 100)[: r.i + 1]
        first = int(np.argmax(~np.isnan(s)))              # drop leading missing weeks only
        ctx.append(torch.tensor(s[first:], dtype=torch.float32))
    rows = []
    for b in range(0, len(ctx), batch):
        qs, _ = pipe.predict_quantiles(ctx[b:b + batch], prediction_length=4, quantile_levels=Q)
        for k, q in enumerate(qs):
            v = np.sort(q[0].numpy().astype(float), axis=-1)            # (4, 23)
            v = 100 * expit(v) if scale == "logit" else np.clip(v, 0, 100)
            o = origins.iloc[b + k]
            for h in range(1, 5):
                rows.append(dict(country=o.country, season=int(o.season), i=int(o.i), h=h, qv=v[h - 1]))
    fc = pd.DataFrame(rows)
    fc["model"] = FM if scale == "logit" else FM_PCT
    return fc.merge(ev[Hn.KEYS], on=Hn.KEYS), rev


def endpoints(sc: pd.DataFrame, a: str) -> dict:
    out = {}
    for b in [POOLM, LOCAL, "persistence", "seasonal-analog"]:
        if a == b:
            continue
        out[f"vs_{b}"] = Hn.rel(sc, a, b)
        out[f"vs_{b}_short_history"] = Hn.rel(sc[sc.n_own <= C.SHORT_HISTORY_MAX_OWN_SEASONS], a, b)
    out["by_horizon_vs_NABD-Pool"] = {int(h): round(float(g[g.model == a].wis.sum() / g[g.model == POOLM].wis.sum()), 4)
                                      for h, g in sc.groupby("h")} if a != POOLM else {}
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fc, ev = stored()
    sc0, _ = Hn.score(fc, ev)
    chk = Hn.rel(sc0, POOLM, LOCAL)
    assert abs(chk["rel_wis"] - 0.767) < 0.002, f"rescored Pool vs local = {chk['rel_wis']}, expected 0.767 (W1d)"
    f_logit, rev = chronos_forecasts(ev, "logit")
    f_pct, _ = chronos_forecasts(ev, "percent")
    pool = fc[fc.model == POOLM].merge(f_logit[Hn.KEYS + ["qv"]], on=Hn.KEYS, suffixes=("", "_fm"))
    ens = pool[Hn.KEYS].copy()
    ens["qv"] = [np.sort((a + b) / 2) for a, b in zip(pool.qv, pool.qv_fm)]
    ens["model"] = ENS
    allf = pd.concat([fc, f_logit, f_pct, ens], ignore_index=True)
    sc, _ = Hn.score(allf, ev)
    sc.to_csv(OUT / "scores_long.csv.gz", index=False)
    wide = f_logit[Hn.KEYS].copy()
    wide[QCOLS] = np.round(np.vstack(f_logit.qv.values), 3)
    wide.to_csv(OUT / "forecasts_chronos2_heldout.csv.gz", index=False)
    summ = dict(status="POST HOC, EXPLORATORY (DEVIATIONS W1). Not a confirmatory result.", model=MODEL_ID,
                weights_revision=rev, check_w1d=chk, n_cells_common=int((sc.model == POOLM).sum()),
                n_countries=int(sc.country.nunique()),
                coverage={m: dict(cov50=round(float(g.cov50.mean()), 3), cov95=round(float(g.cov95.mean()), 3))
                          for m, g in sc.groupby("model")},
                mean_wis={m: round(float(g.wis.mean()), 4) for m, g in sc.groupby("model")},
                results={m: endpoints(sc, m) for m in [FM, FM_PCT, ENS]})
    pc = sc.groupby(["country", "model"]).wis.mean().unstack()
    pc["chronos/pool"], pc["ens/pool"] = pc[FM] / pc[POOLM], pc[ENS] / pc[POOLM]
    pc.round(4).reset_index().to_csv(OUT / "per_country.csv", index=False)
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1, default=float))
    write_summary(summ, pc)
    print((OUT / "SUMMARY.md").read_text())


def _r(d):
    return f"{d['rel_wis']:.3f} (95% CI {d['ci95'][0]:.3f}–{d['ci95'][1]:.3f}; {d['unit_wins']} countries better)"


def write_summary(s: dict, pc: pd.DataFrame):
    R = s["results"]
    L = ["# Zero-shot foundation-model benchmark on the held-out countries (influenza)", "",
         "_POST HOC and EXPLORATORY (DEVIATIONS W1, declared before computing). The S1 forecasts are unchanged and their "
         "accuracy was already known. Not a confirmatory result and not a UAE result._", "",
         f"Model: `{s['model']}` (revision `{s['weights_revision'][:12]}`), zero-shot, univariate, no fine-tuning. Each "
         "forecast sees only the country's own series up to the forecast origin. Same cells, same score (WIS) and same "
         f"country-clustered bootstrap as S1: {s['n_cells_common']:,} forecasts in {s['n_countries']} countries. "
         f"Check: the stored S1 forecasts rescore to Pool vs local = {s['check_w1d']['rel_wis']:.3f}.", "",
         "Relative WIS below 1 means the first model had less error.", "",
         "| Comparison | Relative WIS | Short-history stratum |", "|---|---|---|"]
    for m, lab in [(FM, "Chronos-2 zero-shot"), (ENS, "Pool+FM (equal-weight average of NABD-Pool and Chronos-2)"),
                   (FM_PCT, "Chronos-2 zero-shot, percent input (sensitivity)")]:
        for b, bl in [(POOLM, "NABD-Pool"), (LOCAL, "own-record model (local v1)"), ("persistence", "last week carried forward")]:
            L.append(f"| {lab} vs {bl} | {_r(R[m]['vs_' + b])} | {_r(R[m]['vs_' + b + '_short_history'])} |")
    L += ["", "| Model | Mean WIS (pp) | 50% coverage | 95% coverage |", "|---|---|---|---|"]
    for m in [POOLM, FM, ENS, FM_PCT, LOCAL, "persistence", "seasonal-analog"]:
        L.append(f"| {m} | {s['mean_wis'][m]:.3f} | {s['coverage'][m]['cov50']:.2f} | {s['coverage'][m]['cov95']:.2f} |")
    L += ["", "By horizon (1–4 data weeks), relative WIS vs NABD-Pool: Chronos-2 "
          + ", ".join(f"{v:.3f}" for v in R[FM]["by_horizon_vs_NABD-Pool"].values()) + "; Pool+FM "
          + ", ".join(f"{v:.3f}" for v in R[ENS]["by_horizon_vs_NABD-Pool"].values()) + ".", "",
          "## Every country (mean WIS; ratio below 1 = better than NABD-Pool)", "",
          "| Country | NABD-Pool | Chronos-2 | Pool+FM | Chronos-2 / Pool | Pool+FM / Pool |", "|---|---|---|---|---|---|"]
    for c, r in pc.sort_values("ens/pool").iterrows():
        L.append(f"| {c} | {r[POOLM]:.2f} | {r[FM]:.2f} | {r[ENS]:.2f} | {r['chronos/pool']:.2f} | {r['ens/pool']:.2f} |")
    L += ["", "## Limits",
          "- Post hoc: declared after the S1 scores were known; the equal-weight ensemble is a hypothesis for a new locked test, not a finding.",
          "- The foundation model's pretraining data may include public epidemiological series; we cannot rule out overlap.",
          "- Finalised FluNet data; positivity, not hospital load."]
    (OUT / "SUMMARY.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
