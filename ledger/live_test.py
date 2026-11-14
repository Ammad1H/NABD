"""Prospective UAE test of NABD-Pool vs NABD-UAE-v1 on the live ledger (docs/PREREG-LIVE.md).

  python3 -m ledger.live_test --cached        # interim, on data/raw (or --fetch for the official API)
  python3 -m ledger.live_test --fetch --final # the one final assessment (on or after 15 Apr 2027)

Writes ledger/LIVE-TEST.md and ledger/live_test.json. Refuses to run if the lock does not verify.
"""
import argparse
import datetime as dt
import json
from pathlib import Path

import numpy as np
import pandas as pd

from adapters import flunet
from ledger.score import TARGET_COL, verify
from uae.models import QUANTILES
from uae.scoring import covered, wis

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "ledger"
POOL, LOCAL, PERS = "NABD-Pool", "NABD-UAE-v1", "persistence"
MODELS = [POOL, LOCAL, PERS]
FIRST_ROUND, LAST_TARGET, FINAL_FROM = 2, pd.Timestamp("2027-03-28"), dt.date(2027, 4, 15)
B, SEED, BLOCK = 2000, 0, 4
SER = {"wk flu pos pct sentinel": "influenza", "wk rsv pos pct sentinel": "RSV"}


def rounds() -> tuple[dict, list]:
    """{round_label: {model: csv}} for rounds >= R2 with all three models and valid hashes; plus exclusions."""
    by, excl = {}, []
    for m in sorted(LEDGER.glob("*.meta.json")):
        meta = json.loads(m.read_text())
        lab = meta.get("round", "")
        if not lab.startswith("R") or int(lab[1:]) < FIRST_ROUND:
            continue
        csv = m.with_name(m.name.replace(".meta.json", ".csv"))
        if not verify(csv):
            excl.append((lab, csv.name, "hash mismatch or missing"))
            continue
        by.setdefault(lab, {})[meta["model"]] = csv
    for lab in list(by):
        miss = [x for x in MODELS if x not in by[lab]]
        if miss:
            excl.append((lab, "", "missing model(s): " + ", ".join(miss)))
            del by[lab]
    return by, excl


def score_cells(mode: str) -> pd.DataFrame:
    s = flunet.sentinel_series(flunet.load(mode)).set_index("week_end")
    by, _ = rounds()
    rows = []
    for lab, files in by.items():
        for model in MODELS:
            f = pd.read_csv(files[model])
            for (tgt, h, te), g in f.groupby(["target", "horizon", "target_end_date"]):
                te_ts = pd.Timestamp(te)
                if te_ts > LAST_TARGET or te_ts not in s.index:
                    continue
                r = s.loc[te_ts]
                if not (r.specimens > 0) or np.isnan(r[TARGET_COL[tgt]]):
                    continue
                obs = 100 * r[TARGET_COL[tgt]] / r.specimens
                g = g.sort_values("output_type_id")
                q, v = g.output_type_id.values.astype(float), g.value.values.astype(float)
                rows.append(dict(round=lab, model=model, target=tgt, horizon=int(h), target_end_date=te, obs=obs,
                                 wis=wis(q, v, obs), cov50=covered(q, v, obs, 0.5), cov95=covered(q, v, obs, 0.95)))
    sc = pd.DataFrame(rows)
    if sc.empty:
        return sc
    k = ["round", "target", "horizon"]
    n = sc.groupby(k).model.nunique()
    return sc.set_index(k).loc[n[n == len(MODELS)].index].reset_index()


def rel(sc: pd.DataFrame, a: str, b: str) -> dict | None:
    A = sc[sc.model == a].groupby("round").wis.sum()
    Bv = sc[sc.model == b].groupby("round").wis.sum().reindex(A.index)
    if len(A) == 0 or Bv.sum() == 0:
        return None
    a_, b_ = A.values, Bv.values
    rng = np.random.default_rng(SEED)
    bs = [a_[k].sum() / b_[k].sum() for k in (rng.integers(0, len(a_), len(a_)) for _ in range(B))]
    out = dict(rel_wis=round(float(a_.sum() / b_.sum()), 4), n_rounds=int(len(a_)), n_cells=int((sc.model == a).sum()),
               ci95=[round(float(np.quantile(bs, .025)), 4), round(float(np.quantile(bs, .975)), 4)])
    if len(a_) >= 2 * BLOCK:                                   # moving-block sensitivity (rounds are ordered)
        order = sorted(A.index, key=lambda x: int(x[1:]))
        a_o, b_o = A.loc[order].values, Bv.loc[order].values
        starts = np.arange(len(a_o) - BLOCK + 1)
        mb = []
        for _ in range(B):
            idx = np.concatenate([np.arange(st, st + BLOCK) for st in rng.choice(starts, int(np.ceil(len(a_o) / BLOCK)))])[: len(a_o)]
            mb.append(a_o[idx].sum() / b_o[idx].sum())
        out["ci95_moving_block"] = [round(float(np.quantile(mb, .025)), 4), round(float(np.quantile(mb, .975)), 4)]
    return out


def run(mode="cached", final=False) -> dict:
    from ledger.live_lock import check
    root = check()
    today = dt.datetime.now(dt.timezone.utc).date()
    if final and today < FINAL_FROM:
        raise SystemExit(f"final assessment is not allowed before {FINAL_FROM} (PREREG-LIVE section 6)")
    by, excl = rounds()
    sc = score_cells(mode)
    out = dict(plan="docs/PREREG-LIVE.md", lock_root=root, status="FINAL" if final else "INTERIM (descriptive only)",
               as_of_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), data_mode=mode,
               rounds_issued=sorted(by, key=lambda x: int(x[1:])), excluded=[list(e) for e in excl],
               scored_cells_per_model=0 if sc.empty else int((sc.model == POOL).sum()), results={})
    if not sc.empty:
        sc.to_csv(LEDGER / "live_test_scores.csv", index=False)
        for tgt, name in SER.items():
            g = sc[sc.target == tgt]
            if g.empty:
                continue
            out["results"][name] = {
                "pool_vs_local": rel(g, POOL, LOCAL), "pool_vs_persistence": rel(g, POOL, PERS),
                "local_vs_persistence": rel(g, LOCAL, PERS),
                "by_horizon_pool_vs_local": {int(h): round(float(x[x.model == POOL].wis.sum() / x[x.model == LOCAL].wis.sum()), 4)
                                             for h, x in g.groupby("horizon") if x[x.model == LOCAL].wis.sum() > 0},
                "coverage": {m: dict(cov50=round(float(x.cov50.mean()), 3), cov95=round(float(x.cov95.mean()), 3))
                             for m, x in g.groupby("model")}}
        p = (out["results"].get("influenza") or {}).get("pool_vs_local")
        if final and p:
            out["PRIMARY_verdict"] = "MET" if p["rel_wis"] < 1 and p["ci95"][1] < 1 else "NOT MET"
    (LEDGER / "live_test.json").write_text(json.dumps(out, indent=1))
    L = ["# Prospective UAE test: pooled model vs own-record model on the live ledger", "",
         f"Plan: `docs/PREREG-LIVE.md` (lock root `{root[:16]}…`, self-attested until anchored). **{out['status']}**, "
         f"as of {out['as_of_utc']}.", "",
         f"Rounds issued under the plan: {', '.join(out['rounds_issued']) or 'none yet'}. "
         f"Scored forecasts per model: {out['scored_cells_per_model']}.", ""]
    if not out["results"]:
        L.append("No target week of an included round has been published by WHO yet. Nothing to report.")
    for name, r in out["results"].items():
        L += [f"## {name.capitalize()}", "", "| Comparison | Relative WIS | 95% CI (rounds resampled) | Rounds | Forecasts |", "|---|---|---|---|---|"]
        for key, lab in [("pool_vs_local", "Pooled / own-record" + (" (PRIMARY)" if name == "influenza" else "")),
                         ("pool_vs_persistence", "Pooled / last week"), ("local_vs_persistence", "Own-record / last week")]:
            d = r[key]
            if d:
                L.append(f"| {lab} | {d['rel_wis']:.3f} | {d['ci95'][0]:.3f}–{d['ci95'][1]:.3f} | {d['n_rounds']} | {d['n_cells']} |")
        L.append("")
    if "PRIMARY_verdict" in out:
        L.append(f"**Primary (influenza, pooled / own-record): {out['PRIMARY_verdict']}.**")
    elif out["results"]:
        L.append("_Interim numbers are descriptive. The hypothesis is assessed once, at final scoring (on or after 15 April 2027)._")
    if excl:
        L += ["", "Excluded: " + "; ".join(f"{a} {b} ({c})" for a, b, c in excl)]
    (LEDGER / "LIVE-TEST.md").write_text("\n".join(L) + "\n")
    return out


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--cached", action="store_true")
    g.add_argument("--fetch", action="store_true")
    ap.add_argument("--final", action="store_true")
    a = ap.parse_args()
    print(json.dumps(run("fetch" if a.fetch else "cached", a.final), indent=1))


if __name__ == "__main__":
    main()
