"""Run the frozen NABD configuration on the test seasons ONCE (PROTOCOL §10.3).

Writes forecast files in the interface-contract format:
    results/forecasts/<model>/<reference_date>.csv
Models written: NABD-GLM, NABD-EEQ, NABD-ensemble (and NABD-Chronos2 only if it actually ran).
"""
from __future__ import annotations

import argparse
import json
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from models import chronos2
from models.data import QUANTILES, season_dates
from models.engine import eeq_member, glm_member, point_t0, prepare
from models.members import vincent, widen
from models.point import PointCfg

ROOT = Path(__file__).resolve().parents[1]
FC = ROOT / "results" / "forecasts"
TEST_SEASONS = ["2024/25", "2025/26"]
POINT_KEYS = ["w", "phi", "lam_n", "lam_s", "level", "g_max"]


def load_config() -> dict:
    return yaml.safe_load((ROOT / "models" / "config.yaml").read_text())


def _to_long(q: np.ndarray, P, model: str) -> pd.DataFrame:
    L, S, Q = q.shape
    tg = P.target_end_dates()
    loc = np.repeat(P.locs, S * Q)
    h = np.tile(np.repeat(np.arange(S), Q), L)
    qq = np.tile(QUANTILES, L * S)
    return pd.DataFrame({
        "reference_date": P.R.date().isoformat(),
        "target": "wk inc flu hosp",
        "horizon": h,
        "target_end_date": [tg[i].date().isoformat() for i in h],
        "location": loc,
        "output_type": "quantile",
        "output_type_id": qq,
        "value": q.reshape(-1),
        "model": model,
    })


def forecast_date(args) -> dict:
    R, cfg, with_chronos = args
    P = prepare(R)
    g = cfg["glm"]; e = cfg["eeq"]; k = cfg["ensemble"]["k"]
    gcfg = PointCfg(**{x: g[x] for x in POINT_KEYS})
    ecfg = PointCfg(**{x: e[x] for x in POINT_KEYS})
    qg = glm_member(P, gcfg, g["c"])
    qe = eeq_member(P, ecfg, e["H"], None, e["strata"])
    members = {"NABD-GLM": qg, "NABD-EEQ": qe}
    if with_chronos and chronos2.available():
        qc = chronos2.chronos_quantiles(P.Y)
        if qc is not None:
            members["NABD-Chronos2"] = qc
    ens = widen(vincent(list(members.values())), k)
    out = dict(members)
    out["NABD-ensemble"] = ens
    for name, q in out.items():
        d = FC / name
        d.mkdir(parents=True, exist_ok=True)
        _to_long(q, P, name).to_csv(d / f"{P.R.date().isoformat()}.csv", index=False)
    return {**P.meta, "members": list(members)}


def main(dates=None, procs: int = 2, with_chronos: bool = False, seasons=TEST_SEASONS) -> pd.DataFrame:
    cfg = load_config()
    if dates is None:
        dates = [d for s in seasons for d in season_dates(s)]
    t0 = time.time()
    with Pool(procs) as pool:
        metas = pool.map(forecast_date, [(R, cfg, with_chronos) for R in dates])
    flags = pd.DataFrame(metas)
    (ROOT / "results" / "tables").mkdir(parents=True, exist_ok=True)
    flags.to_csv(ROOT / "results" / "tables" / "vintage_flags.csv", index=False)
    print(f"forecast {len(dates)} dates in {time.time()-t0:.1f}s; chronos: {chronos2.STATUS}")
    return flags


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-chronos", action="store_true")
    ap.add_argument("--procs", type=int, default=2)
    a = ap.parse_args()
    main(procs=a.procs, with_chronos=a.with_chronos)
