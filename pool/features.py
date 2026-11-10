"""Per-country series and forward-in-time feature tables for NABD-Pool.

Every feature at origin t of season s uses only (a) the country's own rows with week_end <= t and
(b) the country's own qualifying seasons BEFORE s (for its past-season pattern). The target is the
within-season logit change y[t+h] - y[t]. The same table serves training (development countries,
seasons before S) and prediction (the target country, season S).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from pool import config as C
from uae.gcc import SER, choose_series, qualifying, tidy
from uae.models import H, climatology, logit

FEATS_G = ["y0", "dy1", "dy2", "slope3", "anom", "dclim", "runmax_gap", "wk_in_season", "ph_sin", "ph_cos",
           "abslat", "south", "logspec", "dlogspec", "n_own", "h"]
FEATS_L = ["dy1", "anom", "dclim", "dlogspec"]      # the local v1 method's own features


def country_series(d: pd.DataFrame, country: str, key: str):
    """Returns (origin_label, frame, qualifying dict) or (None, None, None)."""
    origin, s = choose_series(d, country)
    if s is None or len(s) == 0:
        return None, None, None
    pos = s[SER[key]]
    x = s[["week_end", "iso_year", "iso_week", "season", "specimens"]].copy()
    x["pos"] = pos
    x["y"] = logit((pos + 0.5) / (s.specimens + 1.0))
    x.loc[pos.isna() | s.specimens.isna() | (s.specimens <= 0), "y"] = np.nan
    x["logspec"] = np.log(s.specimens.clip(lower=1))
    x["season"] = x.season.astype(int)
    x = x.reset_index(drop=True)
    return origin, x, qualifying(s, SER[key])


def own_train_seasons(q: dict, S: int, truncate: int | None = None) -> list[int]:
    tr = sorted(k for k, ok in q.items() if ok and k < S and k not in C.EXCLUDE_TRAINING_SEASONS)
    return tr[-truncate:] if truncate else tr


def feature_table(x: pd.DataFrame, q: dict, country: str, truncate: int | None = None,
                  seasons=None) -> pd.DataFrame:
    """One row per (origin index i, horizon h) for every qualifying season of this country."""
    lat = C.LAT[country]
    out = []
    y = x.y.values
    for S in sorted(k for k, ok in q.items() if ok):
        if seasons is not None and S not in seasons:
            continue
        tr = own_train_seasons(q, S, truncate)
        clim = climatology(x, tr) if tr else None
        idx = np.where(x.season.values == S)[0]
        if len(idx) == 0:
            continue
        first = idx[0]
        for i in idx:
            if np.isnan(y[i]):
                continue
            same1 = i - 1 >= first
            same2 = i - 2 >= first
            dy1 = y[i] - y[i - 1] if same1 else np.nan
            dy2 = y[i - 1] - y[i - 2] if same2 else np.nan
            slope3 = (y[i] - y[i - 2]) / 2 if same2 else np.nan
            seg = y[first:i + 1]
            runmax_gap = y[i] - np.nanmax(seg)
            w = int(x.iso_week.iloc[i])
            cw = clim.get(w, np.nan) if clim is not None else np.nan
            ph = 2 * np.pi * (((w - 1) + (26 if lat < 0 else 0)) % 52) / 52.0
            dls = x.logspec.iloc[i] - x.logspec.iloc[i - 1] if same1 else np.nan
            for h in H:
                j = i + h
                if j >= len(x) or x.season.iloc[j] != S:
                    continue
                tw = clim.get(int(x.iso_week.iloc[j]), np.nan) if clim is not None else np.nan
                out.append(dict(country=country, season=S, i=i, origin=x.week_end.iloc[i], h=h,
                                y0=y[i], dy1=dy1, dy2=dy2, slope3=slope3, anom=y[i] - cw, dclim=tw - cw,
                                runmax_gap=runmax_gap, wk_in_season=i - first, ph_sin=np.sin(ph),
                                ph_cos=np.cos(ph), abslat=abs(lat), south=float(lat < 0),
                                logspec=x.logspec.iloc[i], dlogspec=dls, n_own=float(len(tr)),
                                target=y[j] - y[i],
                                obs=(x.pos.iloc[j] / x.specimens.iloc[j] * 100) if not np.isnan(y[j]) else np.nan))
    return pd.DataFrame(out)


def load(path, countries, key="flu"):
    """Returns {country: dict(origin=, x=, q=)} for countries with any data."""
    d = tidy(pd.read_csv(path))
    res = {}
    for c in countries:
        if c not in set(d.country):
            continue
        origin, x, q = country_series(d, c, key)
        if x is None:
            continue
        res[c] = dict(origin=origin, x=x, q=q)
    return res
