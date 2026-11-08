"""Produce a CDC FluSight hub submission file from FROZEN NABD v1 (models/config.yaml).

    python -m eval.flusight_round --reference-date 2026-11-14 --team NABD --model v1 [--out DIR]

Uses only the newest hub vintage with as_of <= reference_date - 3 days (PROTOCOL §2 rule), so run it
on Wednesday after the hub target-data update, with an UNPINNED, freshly pulled hub clone
(`git -C external/hub checkout main && git -C external/hub pull`). It prints the vintage used and
how stale the data are. Output: <out>/<reference_date>-<team>-<model>.csv in hub format (integer values).
Nothing is submitted: copying the file into a fork of cdcepi/FluSight-forecast-hub and opening a PR
is a manual decision (docs/FLUSIGHT-PARTICIPATION.md).
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

from eval.backtest import POINT_KEYS, _to_long, load_config
from models.engine import eeq_member, glm_member, prepare
from models.members import vincent, widen
from models.point import PointCfg

ROOT = Path(__file__).resolve().parents[1]


def make(reference_date: str, team: str, model: str, out: Path) -> Path:
    R = pd.Timestamp(reference_date)
    if R.dayofweek != 5:
        raise ValueError("reference_date must be a Saturday")
    cfg = load_config()
    g, e, k = cfg["glm"], cfg["eeq"], cfg["ensemble"]["k"]
    P = prepare(R)
    qg = glm_member(P, PointCfg(**{x: g[x] for x in POINT_KEYS}), g["c"])
    qe = eeq_member(P, PointCfg(**{x: e[x] for x in POINT_KEYS}), e["H"], None, e["strata"])
    d = _to_long(widen(vincent([qg, qe]), k), P, "NABD-ensemble").drop(columns="model")
    d["value"] = np.round(d["value"]).astype(int)
    d["output_type_id"] = d["output_type_id"].map(lambda x: f"{x:g}")
    w = d.pivot_table(index=["location", "horizon"], columns="output_type_id", values="value")
    assert (np.diff(w[sorted(w.columns, key=float)].to_numpy(), axis=1) >= 0).all(), "quantile crossing"
    out.mkdir(parents=True, exist_ok=True)
    p = out / f"{R.date().isoformat()}-{team}-{model}.csv"
    d.to_csv(p, index=False)
    print(f"wrote {p}  rows={len(d)}  sha256={hashlib.sha256(p.read_bytes()).hexdigest()}")
    print(f"vintage used: {P.meta['vintage_as_of']} (data through {P.meta['last_week']}; "
          f"stale weeks: {P.meta['stale_weeks']}) -- if stale > 0, the hub has not published this week's data yet")
    return p


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference-date", required=True)
    ap.add_argument("--team", default="NABD")
    ap.add_argument("--model", default="v1")
    ap.add_argument("--out", default=str(ROOT / "results" / "flusight_draft"))
    a = ap.parse_args()
    make(a.reference_date, a.team, a.model, Path(a.out))
