"""Confirmatory scoring of NABD-Pool on held-out countries (PREREG-POOL sections 5, 8, 9).

  python3 -m pool.score --selftest   # code check on development data only (5 dev countries play 'held-out')
  python3 -m pool.score --confirm    # refuses unless locks #1 and #2 verify; scores data/raw/flunet_pool_held.csv
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from pool import config as C
from pool import harness as Hn
from pool.features import load
from pool.locks import MODEL_CONFIG, check_lock2
from pool.models import Q, ensemble_percent

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "pool"
RAW = ROOT / "data" / "raw"
MODELS = ["NABD-Pool", "NABD-UAE-v1", "persistence", "seasonal-analog"]


def member_spec(m: dict) -> dict:
    s = {k: v for k, v in m.items() if k != "name"}
    if s.get("k") == "inf":
        s["k"] = float("inf")
    return s


def run(cfg, D_dev, D_tgt, truncate=None, exclude_from_train=()):
    """Forward-in-time forecasts for every scored country-season in D_tgt. Returns (scores, forecasts, ev)."""
    ev = Hn.eval_table(D_tgt, truncate=truncate)
    if ev.empty:
        return pd.DataFrame(), pd.DataFrame(), ev
    loc, fitted = Hn.local_forecasts(D_tgt, truncate=truncate)
    tables = {}
    arr = np.full((len(ev), len(Q)), np.nan)
    D_all = {**D_dev, **D_tgt}
    for S in C.EVAL_SEASONS:
        idx = np.where(ev.season.values == S)[0]
        if len(idx) == 0:
            continue
        evS = ev.iloc[idx].reset_index(drop=True)
        mem = []
        for m in cfg["members"]:
            spec = member_spec(m)
            if spec["relaxed"] not in tables:
                tables[spec["relaxed"]] = Hn.train_table(D_dev, spec["relaxed"])
            T = tables[spec["relaxed"]]
            tr = T[(T.season < S) & (~T.country.isin(list(exclude_from_train)))]
            mem.append(np.vstack(Hn.pool_forecasts(spec, tr, evS, fitted, D_all).qv.values))
        arr[idx] = ensemble_percent(mem) if len(mem) > 1 else mem[0]
    fc = ev[Hn.KEYS].copy()
    fc["model"] = "NABD-Pool"
    fc["qv"] = list(arr)
    fc = pd.concat([fc, loc], ignore_index=True)
    sc, _ = Hn.score(fc, ev)
    return sc, fc, ev


def inclusion(D, countries) -> pd.DataFrame:
    rows = []
    for c in countries:
        if c not in D:
            rows.append(dict(country=c, series="none", qualifying_seasons="", scored_seasons="", included=False,
                             reason="no rows in the export (ISO_YEAR >= 2015)"))
            continue
        v = D[c]
        qs = [k for k, ok in v["q"].items() if ok]
        ss = Hn.scored_seasons(v)
        rows.append(dict(country=c, series=v["origin"], qualifying_seasons=" ".join(map(str, qs)),
                         scored_seasons=" ".join(map(str, ss)), included=len(ss) >= C.MIN_SCORED_EVAL_SEASONS,
                         reason="" if ss else ("no qualifying evaluation season" if not any(
                             v["q"].get(S) for S in C.EVAL_SEASONS) else "fewer than 2 qualifying earlier seasons")))
    return pd.DataFrame(rows)


def endpoints(sc: pd.DataFrame) -> dict:
    res = {}
    if sc.empty:
        return res
    for b in MODELS[1:]:
        res[f"pool_vs_{b}"] = Hn.rel(sc, "NABD-Pool", b)
    res["v1_vs_persistence"] = Hn.rel(sc, "NABD-UAE-v1", "persistence")
    short = sc[sc.n_own <= C.SHORT_HISTORY_MAX_OWN_SEASONS]
    res["short_history_pool_vs_v1"] = Hn.rel(short, "NABD-Pool", "NABD-UAE-v1") if len(short) else None
    for nm, lst in (("EMRO", C.HELD_EMRO), ("other_regions", C.HELD_OTHER)):
        x = sc[sc.country.isin(lst)]
        res[f"{nm}_pool_vs_v1"] = Hn.rel(x, "NABD-Pool", "NABD-UAE-v1") if len(x) else None
    res["by_horizon_pool_vs_v1"] = {int(h): Hn.rel(g, "NABD-Pool", "NABD-UAE-v1", B=500)["rel_wis"]
                                    for h, g in sc.groupby("h")}
    res["coverage"] = sc.groupby("model")[["cov50", "cov95"]].mean().round(3).to_dict(orient="index")
    cs = sc.groupby(["country", "season", "model"]).wis.sum().unstack()
    res["country_season_wins_pool_vs_v1"] = f"{int((cs['NABD-Pool'] < cs['NABD-UAE-v1']).sum())}/{len(cs)}"
    return res


def tables(sc, out: Path, tag: str):
    out.mkdir(parents=True, exist_ok=True)
    per = sc.groupby(["country", "model"]).wis.mean().unstack()
    per["pool/v1"] = per["NABD-Pool"] / per["NABD-UAE-v1"]
    per["pool/persistence"] = per["NABD-Pool"] / per["persistence"]
    per["pool/analog"] = per["NABD-Pool"] / per["seasonal-analog"]
    per["n_cells"] = sc[sc.model == "NABD-Pool"].groupby("country").size()
    per.round(4).to_csv(out / f"per_country_{tag}.csv")
    cs = sc.groupby(["country", "season", "model"]).wis.mean().unstack()
    cs["pool_beats_v1"] = cs["NABD-Pool"] < cs["NABD-UAE-v1"]
    cs["n_own"] = sc.groupby(["country", "season"]).n_own.first()
    cs.round(4).to_csv(out / f"per_country_season_{tag}.csv")
    return per, cs


def figures(sc, sc_trunc, primary, out: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    teal, red, slate = "#1f6f6b", "#c0392b", "#44546a"
    per = sc.groupby(["country", "model"]).wis.sum().unstack()
    r = (per["NABD-Pool"] / per["NABD-UAE-v1"]).sort_values()
    fig, ax = plt.subplots(figsize=(9, max(4, 0.32 * len(r) + 1.6)))
    ax.hlines(range(len(r)), 1, r.values, color=[teal if v < 1 else red for v in r.values], lw=3)
    ax.plot(r.values, range(len(r)), "o", color=slate, ms=5)
    ax.axvline(1, color="grey", lw=1)
    ax.plot([primary["rel_wis"]], [-1.2], "D", color="black", ms=9)
    ax.hlines(-1.2, primary["ci95"][0], primary["ci95"][1], color="black", lw=2)
    ax.set_yticks(list(range(len(r))) + [-1.2])
    ax.set_yticklabels(list(r.index) + ["ALL (95% CI)"], fontsize=10)
    ax.set_xlabel("forecast error (WIS): pooled model / own-record model   (< 1 = pooled is better)", fontsize=11)
    ax.set_title("Held-out countries: pooled model vs each country's own-record model (influenza)", fontsize=12)
    fig.tight_layout()
    fig.savefig(out / "fig_forest_pool_vs_local.png", dpi=150)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    g = sc.assign(bin=sc.n_own.clip(upper=6).astype(int))
    xs, ys = [], []
    for b, x in g.groupby("bin"):
        w = x.groupby("model").wis.sum()
        xs.append(b)
        ys.append(w["NABD-Pool"] / w["NABD-UAE-v1"])
    ax.plot(xs, ys, "o-", color=teal, lw=2, label="natural history length")
    if sc_trunc is not None and len(sc_trunc):
        w = sc_trunc.groupby("model").wis.sum()
        ax.plot([2], [w["NABD-Pool"] / w["NABD-UAE-v1"]], "s", color=red, ms=10,
                label="every country cut to its last 2 seasons")
    ax.axhline(1, color="grey", lw=1)
    ax.set_xticks(xs)
    ax.set_xticklabels([str(b) if b < 6 else "6+" for b in xs])
    ax.set_xlabel("number of the country's own earlier seasons available", fontsize=11)
    ax.set_ylabel("WIS: pooled / own-record  (< 1 = pooled better)", fontsize=11)
    ax.set_title("Does borrowing help most when a country's own record is short?", fontsize=12)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "fig_skill_vs_own_seasons.png", dpi=150)
    plt.close(fig)


def save_forecasts(fc, ev, path):
    m = fc.merge(ev[Hn.KEYS + ["origin", "obs"]], on=Hn.KEYS)
    qv = np.vstack(m.qv.values)
    out = m.drop(columns=["qv"])
    for j, q in enumerate(Q):
        out[f"q{q:g}"] = np.round(qv[:, j], 3)
    out.to_csv(path, index=False)


def confirm(selftest=False):
    cfg = json.loads(MODEL_CONFIG.read_text())
    D_dev_all = load(RAW / "flunet_pool_dev.csv", C.DEV)
    if selftest:
        held_list = ["CAN", "NOR", "THA", "QAT", "CHN"]
        D_tgt = {c: D_dev_all[c] for c in held_list}
        D_dev = {c: v for c, v in D_dev_all.items() if c not in held_list}
        out, label = Path("/tmp/pool_selftest"), "SELFTEST on development data (code check only)"
        root = "selftest"
    else:
        root = check_lock2()
        held_list = C.HELD
        D_tgt = load(RAW / "flunet_pool_held.csv", C.HELD)
        D_dev = D_dev_all
        out, label = OUT, ("Held-out countries, forward-in-time, revised FluNet data; plan locked before download "
                           "(lock #1), model locked before any held-out row was extracted (lock #2)")
    (out / "tables").mkdir(parents=True, exist_ok=True)
    inc = inclusion(D_tgt, held_list)
    inc.to_csv(out / "tables" / "inclusion.csv", index=False)
    D_tgt = {c: v for c, v in D_tgt.items() if len(Hn.scored_seasons(v)) >= C.MIN_SCORED_EVAL_SEASONS}
    sc, fc, ev = run(cfg, D_dev, D_tgt)
    summ = dict(label=label, lock2_root=root, chosen_model=cfg["chosen"], included_countries=sorted(D_tgt),
                n_included=len(D_tgt))
    if sc.empty:
        summ["PRIMARY_verdict"] = "NOT ASSESSABLE (no held-out country met the inclusion rules)"
        (out / "summary.json").write_text(json.dumps(summ, indent=1, default=str))
        return summ
    sc.to_csv(out / "tables" / "scores_long.csv", index=False)
    save_forecasts(fc, ev, out / "tables" / "forecasts_heldout.csv.gz")
    res = endpoints(sc)
    p = res["pool_vs_NABD-UAE-v1"]
    summ["PRIMARY_flu_pool_vs_local_v1"] = p
    summ["PRIMARY_verdict"] = "MET" if (p["rel_wis"] < 1 and p["ci95"][1] < 1) else "NOT MET"
    summ["secondary"] = res
    tables(sc, out / "tables", "flu")
    # key secondary 2: simulated short record
    sc_t, _, _ = run(cfg, D_dev, D_tgt, truncate=C.TRUNCATE_TO_SEASONS)
    if len(sc_t):
        sc_t.to_csv(out / "tables" / "scores_long_truncated.csv", index=False)
        summ["simulated_short_record"] = {f"pool_vs_{b}": Hn.rel(sc_t, "NABD-Pool", b) for b in MODELS[1:]}
        tables(sc_t, out / "tables", "flu_truncated")
    figures(sc, sc_t, p, out)
    # RSV secondary (same chosen configuration, fitted on development RSV series)
    try:
        key = "rsv"
        Dd = load(RAW / "flunet_pool_dev.csv", C.DEV, key)
        Dt_all = ({c: Dd[c] for c in held_list if c in Dd} if selftest
                  else load(RAW / "flunet_pool_held.csv", C.HELD, key))
        if selftest:
            Dd = {c: v for c, v in Dd.items() if c not in held_list}
        Dt = {c: v for c, v in Dt_all.items() if len(Hn.scored_seasons(v)) >= C.MIN_SCORED_EVAL_SEASONS}
        inclusion(Dt_all, held_list).to_csv(out / "tables" / "inclusion_rsv.csv", index=False)
        if Dt:
            sc_r, _, _ = run(cfg, Dd, Dt)
            sc_r.to_csv(out / "tables" / "scores_long_rsv.csv", index=False)
            summ["rsv"] = dict(included=sorted(Dt), **endpoints(sc_r))
            tables(sc_r, out / "tables", "rsv")
        else:
            summ["rsv"] = dict(included=[], note="no held-out country qualified on RSV")
    except Exception as e:  # RSV is secondary; a failure is reported, not hidden
        summ["rsv"] = dict(error=repr(e))
    (out / "summary.json").write_text(json.dumps(summ, indent=1, default=str))
    return summ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    a = ap.parse_args()
    s = confirm(selftest=a.selftest) if (a.selftest or a.confirm) else None
    print(json.dumps(s, indent=1, default=str))


if __name__ == "__main__":
    main()
