"""Tune NABD members on the 2023/24 season only (PROTOCOL §9). Writes models/config.yaml.

Truth for tuning = vintage as_of 2024-11-16 (PROTOCOL §4). No test-season data are touched.
"""
from __future__ import annotations

import itertools
import json
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from models.data import season_dates, truth_as_of
from models.engine import eeq_member, glm_member, point_t0, prepare
from models.members import vincent, widen
from models.point import PointCfg
from eval.wis import coverage, wis

ROOT = Path(__file__).resolve().parents[1]
TUNE_TRUTH_ASOF = "2024-11-16"

GRID_POINT = dict(w=[3, 4, 5, 6], phi=[0.6, 0.75, 0.9, 1.0], lam_n=[0.0, 0.25, 0.5],
                  lam_s=[0.0, 0.25], level=["fit", "last"], g_max=[0.5, 1.0])
GRID_C = [1.0, 1.25, 1.5, 2.0]
GRID_H = [26, 52, 104]
GRID_STRATA = ["pooled", "level3"]        # 'level3' added pre-test: Deviation D1
GRID_K = [0.8, 0.9, 1.0, 1.1, 1.25]


def point_grid() -> list[PointCfg]:
    keys = list(GRID_POINT)
    return [PointCfg(**dict(zip(keys, v))) for v in itertools.product(*GRID_POINT.values())]


_TRUTH = None


def _truth_matrix(P) -> tuple[np.ndarray, np.ndarray]:
    global _TRUTH
    if _TRUTH is None:
        t = truth_as_of(TUNE_TRUTH_ASOF)
        _TRUTH = {(l, d): v for l, d, v in zip(t.location, t.target_end_date, t.truth)}
    tg = P.target_end_dates()
    y = np.array([[_TRUTH.get((l, d), np.nan) for d in tg] for l in P.locs])
    return y, np.isfinite(y)


def _score_date(R) -> dict:
    P = prepare(R)
    y, m = _truth_matrix(P)
    yy = np.where(m, y, 0.0)
    out = {"glm": {}, "eeq": {}, "n": int(m.sum())}
    for i, cfg in enumerate(point_grid()):
        pre = point_t0(P, cfg)
        for c in GRID_C:
            q = glm_member(P, cfg, c, pre[0])
            out["glm"][(i, c)] = float((wis(q, yy) * m).sum())
        for H in GRID_H:
            for st in GRID_STRATA:
                q = eeq_member(P, cfg, H, pre, st)
                out["eeq"][(i, H, st)] = float((wis(q, yy) * m).sum())
    return out


def _ens_date(args) -> dict:
    R, gcfg, c, ecfg, H, st = args
    P = prepare(R)
    y, m = _truth_matrix(P)
    yy = np.where(m, y, 0.0)
    qg = glm_member(P, gcfg, c)
    qe = eeq_member(P, ecfg, H, None, st)
    res = {}
    for k in GRID_K:
        q = widen(vincent([qg, qe]), k)
        res[k] = (float((wis(q, yy) * m).sum()), float((coverage(q, yy, 0.5) * m).sum()),
                  float((coverage(q, yy, 0.95) * m).sum()))
    res["n"] = int(m.sum())
    res["glm"] = float((wis(qg, yy) * m).sum())
    res["eeq"] = float((wis(qe, yy) * m).sum())
    return res


def main(procs: int = 2) -> dict:
    t0 = time.time()
    dates = season_dates("2023/24")
    grid = point_grid()
    with Pool(procs) as pool:
        per_date = pool.map(_score_date, dates)
    glm_tot, eeq_tot = {}, {}
    for d in per_date:
        for k, v in d["glm"].items():
            glm_tot[k] = glm_tot.get(k, 0.0) + v
        for k, v in d["eeq"].items():
            eeq_tot[k] = eeq_tot.get(k, 0.0) + v
    gbest = min(glm_tot, key=glm_tot.get)
    ebest = min(eeq_tot, key=eeq_tot.get)
    gcfg, c = grid[gbest[0]], gbest[1]
    ecfg, H, st = grid[ebest[0]], ebest[1], ebest[2]
    with Pool(procs) as pool:
        ens = pool.map(_ens_date, [(R, gcfg, c, ecfg, H, st) for R in dates])
    n = sum(e["n"] for e in ens)
    k_tab = {k: sum(e[k][0] for e in ens) for k in GRID_K}
    kbest = min(k_tab, key=k_tab.get)
    out_dir = ROOT / "results" / "tables"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for (i, cc), v in glm_tot.items():
        rows.append({"member": "glm", **grid[i].__dict__, "c": cc, "H": None, "strata": None, "wis_total": v})
    for (i, HH, ss), v in eeq_tot.items():
        rows.append({"member": "eeq", **grid[i].__dict__, "c": None, "H": HH, "strata": ss, "wis_total": v})
    pd.DataFrame(rows).sort_values(["member", "wis_total"]).to_csv(out_dir / "tuning_members_2023-24.csv", index=False)
    pd.DataFrame([{"k": k, "wis_total": v, "cov50": sum(e[k][1] for e in ens) / n,
                   "cov95": sum(e[k][2] for e in ens) / n} for k, v in k_tab.items()]).to_csv(
        out_dir / "tuning_ensemble_k_2023-24.csv", index=False)
    cfg = {
        "frozen_for": "PROTOCOL v1.0 (docs/FREEZE.md)",
        "tuned_on": "2023/24 reference dates 2023-10-14..2024-05-04 (30); truth vintage as_of 2024-11-16",
        "n_cells_tuning": n,
        "glm": {**gcfg.__dict__, "c": c, "wis_total_2023_24": glm_tot[gbest]},
        "eeq": {**ecfg.__dict__, "H": H, "strata": st, "wis_total_2023_24": eeq_tot[ebest]},
        "ensemble": {"combine": "vincentisation (quantile mean) of available members", "k": kbest,
                     "wis_total_2023_24": k_tab[kbest],
                     "members_wis_total_2023_24": {"glm": sum(e["glm"] for e in ens), "eeq": sum(e["eeq"] for e in ens)}},
        "chronos2": "wrapper present (models/chronos2.py); NOT RUN in build environment; excluded from ensemble",
        "aci": "not used in v1 frozen run; fixed widening k only (PROTOCOL §8)",
        "tuning_runtime_sec": round(time.time() - t0, 1),
    }
    import os
    out_cfg = Path(os.environ.get("NABD_CONFIG_OUT", ROOT / "models" / "config.yaml"))
    if out_cfg == ROOT / "models" / "config.yaml":
        cfg["notes"] = ["Selected values w=3, lam_n=0.5, g_max=0.5 and GLM c=2.0 sit on grid edges; the grid is kept as pre-registered (no extension).",
                        "Frozen before any test-season forecast was produced."]
    out_cfg.write_text(yaml.safe_dump(cfg, sort_keys=False))
    print(json.dumps(cfg, indent=1, default=str))
    return cfg


if __name__ == "__main__":
    main()
