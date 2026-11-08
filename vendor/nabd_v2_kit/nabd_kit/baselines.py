"""Reference baselines.

`flat_baseline` is in the spirit of the FluSight flat baseline: the median is
the last observed value and the spread comes from the empirical, symmetrised
distribution of past h-step changes. It is not a byte-exact replica of the CDC's
baseline; for the US comparison keep using the hub's own baseline forecasts.
"""
from __future__ import annotations

import numpy as np

from .quantiles import check_levels


def flat_baseline(history, levels, horizons=(1, 2, 3, 4), min_changes: int = 8,
                  symmetrize: bool = True, nonneg: bool = True) -> np.ndarray:
    """Quantile forecasts of shape (len(horizons), L) from a 1-D history.

    Uses only `history` (data up to the reference week). With fewer than
    `min_changes` past h-step changes the forecast collapses to the last value.
    """
    lv = check_levels(levels)
    y = np.asarray(history, dtype=float)
    y = y[~np.isnan(y)]
    if y.size == 0:
        raise ValueError("empty history")
    last = y[-1]
    out = np.empty((len(horizons), lv.size))
    for i, h in enumerate(horizons):
        h = int(h)
        if h <= 0:
            out[i] = last
            continue
        d = y[h:] - y[:-h] if y.size > h else np.array([])
        if d.size < min_changes:
            d = np.zeros(1)
        if symmetrize:
            d = np.concatenate([d, -d])
        qs = last + np.quantile(d, lv)
        if nonneg:
            qs = np.clip(qs, 0.0, None)
        out[i] = np.sort(qs)
    return out
