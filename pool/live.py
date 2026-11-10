"""Live NABD-Pool forecast for the UAE ledger (challenger). Uses the locked configuration
(pool/model_config.json), fitted on all development-country seasons before the current one."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from pool import config as C
from pool import harness as Hn
from pool.features import feature_table, load, own_train_seasons
from pool.locks import MODEL_CONFIG
from pool.models import Q, ensemble_percent
from pool.score import member_spec
from uae.gcc import SER, qualifying
from uae.models import H, NabdUAE, logit

ROOT = Path(__file__).resolve().parents[1]
NAME = "NABD-Pool"


@lru_cache(maxsize=4)
def _dev(key: str):
    return load(ROOT / "data" / "raw" / "flunet_pool_dev.csv", C.DEV, key)


def forecast(s: pd.DataFrame, key: str, country: str = "ARE") -> dict:
    """s = adapters.flunet.sentinel_series(raw). Returns {h: 23 percent quantiles} for h = 1..4 data weeks
    after the last published week, or {} if the origin has no usable data."""
    cfg = json.loads(MODEL_CONFIG.read_text())
    pos = s[SER[key]]
    x = s[["week_end", "iso_year", "iso_week", "season", "specimens"]].copy()
    x["pos"] = pos
    x["y"] = logit((pos + 0.5) / (s.specimens + 1.0))
    x.loc[pos.isna() | s.specimens.isna() | (s.specimens <= 0), "y"] = np.nan
    x["logspec"] = np.log(s.specimens.clip(lower=1))
    x = x.reset_index(drop=True)
    i = int(x.dropna(subset=["y"]).index.max())
    cur = int(x.season.iloc[i])
    q = {k: v for k, v in qualifying(s, SER[key]).items() if k < cur}
    fut = pd.DataFrame({"week_end": [x.week_end.iloc[i] + pd.Timedelta(weeks=h) for h in H]})
    iso = [t.isocalendar() for t in fut.week_end]
    fut["iso_year"], fut["iso_week"] = [c[0] for c in iso], [c[1] for c in iso]
    fut["season"] = np.where(fut.iso_week >= 27, fut.iso_year, fut.iso_year - 1)
    xx = pd.concat([x.iloc[: i + 1], fut], ignore_index=True)
    xx["season"] = xx.season.astype(int)
    ev = feature_table(xx, {**q, cur: True}, country, seasons=[cur])
    ev = ev[ev.i == i].reset_index(drop=True)
    if ev.empty:
        return {}
    tr_own = own_train_seasons(q, cur)
    fitted = {(country, cur): (NabdUAE(xx, tr_own), len(tr_own))} if len(tr_own) >= 2 else {}
    D = _dev(key)
    mem = []
    for m in cfg["members"]:
        spec = member_spec(m)
        T = Hn.train_table(D, spec["relaxed"])
        mem.append(np.vstack(Hn.pool_forecasts(spec, T[T.season < cur], ev, fitted, {**D}).qv.values))
    arr = ensemble_percent(mem) if len(mem) > 1 else mem[0]
    return {int(h): arr[j] for j, h in enumerate(ev.h) if not np.isnan(arr[j]).any()}
