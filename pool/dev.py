"""Model selection for NABD-Pool on DEVELOPMENT countries only (PREREG-POOL section 6).

Forward-in-time with the target country left out of the pooled fit: countries are split into 5 fixed folds
(sorted ISO code, index mod 5); for evaluation season S and fold f the pooled model is fitted on the other
folds' rows with season < S and forecasts fold f's countries in season S.

  python3 -m pool.dev --run        # fits members, writes results/pool/dev/ and pool/model_config.json
"""
from __future__ import annotations

import argparse
import itertools
import json
import pickle
import time
from pathlib import Path

import numpy as np
import pandas as pd

from pool import config as C
from pool import harness as Hn
from pool.features import load
from pool.locks import check_lock1
from pool.models import Q, ensemble_percent

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "pool" / "dev"
CACHE = Path("/tmp/pool_dev_members.pkl")
NFOLD = 5
MEMBER_SPECS = {
    "G_relaxed": dict(members=["G"], relaxed=True),
    "G_strict": dict(members=["G"], relaxed=False),
    "G_relaxed_deep": dict(members=["G"], relaxed=True, gbm=dict(max_iter=300, learning_rate=0.03, max_leaf_nodes=31)),
    "K_relaxed": dict(members=["K"], relaxed=True),
    **{f"L_relaxed_k{k}": dict(members=["L"], relaxed=True, k=k) for k in (1, 2, 4, 8, float("inf"))},
    **{f"L_strict_k{k}": dict(members=["L"], relaxed=False, k=k) for k in (4, float("inf"))},
}


def crossfit(spec, D, tables, ev, fitted):
    T = tables[spec["relaxed"]]
    countries = sorted(D)
    fold = {c: j % NFOLD for j, c in enumerate(countries)}
    out = np.full((len(ev), len(Q)), np.nan)
    for S in C.EVAL_SEASONS:
        for f in range(NFOLD):
            idx = np.where((ev.season.values == S) & (ev.country.map(fold).values == f))[0]
            if len(idx) == 0:
                continue
            tr = T[(T.season < S) & (T.country.map(fold) != f)]
            fc = Hn.pool_forecasts(spec, tr, ev.iloc[idx].reset_index(drop=True), fitted, D)
            out[idx] = np.vstack(fc.qv.values)
    return out


def evaluate(name, arr, ev, loc):
    fc = ev[Hn.KEYS].copy()
    fc["model"] = "NABD-Pool"
    fc["qv"] = list(arr)
    sc, _ = Hn.score(pd.concat([fc, loc], ignore_index=True), ev)
    r = dict(candidate=name)
    for b in ("NABD-UAE-v1", "persistence", "seasonal-analog"):
        x = Hn.rel(sc, "NABD-Pool", b, B=500)
        r[f"vs_{b}"] = x["rel_wis"]
        r[f"vs_{b}_ci"] = x["ci95"]
        r[f"wins_{b}"] = x["unit_wins"]
    short = sc[sc.n_own <= C.SHORT_HISTORY_MAX_OWN_SEASONS]
    r["short_vs_v1"] = Hn.rel(short, "NABD-Pool", "NABD-UAE-v1", B=200)["rel_wis"]
    cov = sc[sc.model == "NABD-Pool"]
    r["cov50"], r["cov95"], r["n_cells"] = round(cov.cov50.mean(), 3), round(cov.cov95.mean(), 3), len(cov)
    return r, sc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    check_lock1()
    D = load(ROOT / "data" / "raw" / "flunet_pool_dev.csv", C.DEV)
    tables = {True: Hn.train_table(D, True), False: Hn.train_table(D, False)}
    ev = Hn.eval_table(D)
    loc, fitted = Hn.local_forecasts(D)
    members = pickle.loads(CACHE.read_bytes()) if CACHE.exists() else {}
    for name, spec in MEMBER_SPECS.items():
        if name in members:
            continue
        t = time.time()
        members[name] = crossfit(spec, D, tables, ev, fitted)
        CACHE.write_bytes(pickle.dumps(members))
        print(name, f"{time.time() - t:.0f}s", flush=True)
    rows, scs = [], {}
    for name, arr in members.items():
        r, scs[name] = evaluate(name, arr, ev, loc)
        rows.append(r)
    tab = pd.DataFrame(rows)
    # ensembles: best G, best L, K; a member is admitted only if it beats persistence on development data
    best = {p: tab[tab.candidate.str.startswith(p)].sort_values("vs_NABD-UAE-v1").candidate.iloc[0] for p in "GLK"}
    admitted = [n for n in best.values() if float(tab.set_index("candidate").loc[n, "vs_persistence"]) < 1]
    for k in (2, 3):
        for combo in itertools.combinations(admitted, k):
            nm = "ENS(" + "+".join(combo) + ")"
            r, scs[nm] = evaluate(nm, ensemble_percent([members[c] for c in combo]), ev, loc)
            rows.append(r)
    tab = pd.DataFrame(rows).sort_values("vs_NABD-UAE-v1").reset_index(drop=True)
    OUT.mkdir(parents=True, exist_ok=True)
    tab.to_csv(OUT / "selection.csv", index=False)
    win = tab.candidate.iloc[0]
    combo = win[4:-1].split("+") if win.startswith("ENS(") else [win]
    cfg = dict(chosen=win, selection_rule="lowest pooled relative WIS vs local v1 on development countries, "
               "forward-in-time, 5-fold country-held-out; ensemble members admitted only if they beat persistence",
               members=[dict(name=c, **{k: (v if v != float("inf") else "inf") for k, v in MEMBER_SPECS[c].items()})
                        for c in combo],
               dev_result={k: tab.iloc[0][k] for k in ("vs_NABD-UAE-v1", "vs_persistence", "vs_seasonal-analog",
                                                        "short_vs_v1", "cov50", "cov95")})
    (ROOT / "pool" / "model_config.json").write_text(json.dumps(cfg, indent=1, default=str) + "\n")
    scs[win].to_csv(OUT / "scores_chosen.csv", index=False)
    per = scs[win].groupby(["country", "model"]).wis.mean().unstack()
    per["pool/v1"] = per["NABD-Pool"] / per["NABD-UAE-v1"]
    per["pool/persistence"] = per["NABD-Pool"] / per["persistence"]
    per.round(4).to_csv(OUT / "per_country_chosen.csv")
    print(tab.to_string())
    print("CHOSEN:", win)


if __name__ == "__main__":
    main()
