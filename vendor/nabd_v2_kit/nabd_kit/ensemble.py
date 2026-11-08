"""Small quantile ensembles.

One model against a ~30-model ensemble is structurally disadvantaged. A quantile
average of a few diverse members is the cheapest structural fix. Lock the member
list and weights before any test score is computed.
"""
from __future__ import annotations

import numpy as np


def quantile_average(forecasts, weights=None) -> np.ndarray:
    """Weighted average of quantile functions (Vincentization). Same shapes in."""
    arr = np.stack([np.asarray(f, dtype=float) for f in forecasts], axis=0)
    if weights is None:
        w = np.full(arr.shape[0], 1.0 / arr.shape[0])
    else:
        w = np.asarray(weights, dtype=float)
        if w.shape != (arr.shape[0],) or np.any(w < 0) or w.sum() <= 0:
            raise ValueError("weights must be non-negative, one per forecast")
        w = w / w.sum()
    return np.sort(np.tensordot(w, arr, axes=1), axis=-1)


def quantile_median(forecasts) -> np.ndarray:
    """Per-level median across forecasts (the FluSight ensemble's rule)."""
    arr = np.stack([np.asarray(f, dtype=float) for f in forecasts], axis=0)
    return np.sort(np.median(arr, axis=0), axis=-1)
