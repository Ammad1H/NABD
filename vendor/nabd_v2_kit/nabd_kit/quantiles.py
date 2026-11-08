"""Quantile-forecast utilities shared by the kit.

Convention used everywhere: a forecast is an array whose LAST axis holds the
values at `levels` (strictly increasing, symmetric around 0.5, including 0.5).
"""
from __future__ import annotations

import numpy as np

# The 23 FluSight quantile levels. Check the current season's
# hub-config/tasks.json in the FluSight hub before relying on this.
FLUSIGHT_LEVELS = np.array([
    0.01, 0.025, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50,
    0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 0.975, 0.99,
])


def check_levels(levels) -> np.ndarray:
    """Validate quantile levels for interval-based scoring (WIS)."""
    lv = np.asarray(levels, dtype=float)
    if lv.ndim != 1 or lv.size < 3 or lv.size % 2 == 0:
        raise ValueError("levels must be 1-D with an odd number (>= 3) of entries")
    if np.any(np.diff(lv) <= 0):
        raise ValueError("levels must be strictly increasing")
    if lv[0] <= 0.0 or lv[-1] >= 1.0:
        raise ValueError("levels must lie strictly inside (0, 1)")
    if not np.allclose(lv, 1.0 - lv[::-1]):
        raise ValueError("levels must be symmetric: each tau needs a 1 - tau partner")
    if not np.isclose(lv[lv.size // 2], 0.5):
        raise ValueError("levels must include the median (0.5)")
    return lv


def sort_quantiles(q) -> np.ndarray:
    """Remove quantile crossing by sorting along the last axis."""
    return np.sort(np.asarray(q, dtype=float), axis=-1)


def median_index(levels) -> int:
    lv = check_levels(levels)
    return lv.size // 2


def _cdf_one(q: np.ndarray, lv: np.ndarray, x: float) -> float:
    """P(Y <= x) for one quantile forecast, linear between quantiles.

    Ties (e.g. many zero quantiles for low counts) keep the largest level at the
    tied value, so the CDF is right-continuous. Outside the outermost quantiles
    the value is clipped to [lv[0], lv[-1]]: the forecast says nothing finer.
    """
    qs = np.sort(q)
    uq = np.unique(qs)
    taus = np.array([lv[qs <= v].max() for v in uq])
    if uq.size == 1:
        return float(lv[0] if x < uq[0] else lv[-1])
    return float(np.interp(x, uq, taus, left=lv[0], right=lv[-1]))


def cdf_at(q, levels, x) -> np.ndarray:
    """Vectorised P(Y <= x). q: (n, L) or (L,); x: scalar or (n,)."""
    lv = check_levels(levels)
    q2 = np.atleast_2d(np.asarray(q, dtype=float))
    xs = np.broadcast_to(np.asarray(x, dtype=float), (q2.shape[0],))
    return np.array([_cdf_one(q2[i], lv, xs[i]) for i in range(q2.shape[0])])


def exceedance_prob(q, levels, threshold) -> np.ndarray:
    """P(Y > threshold), clipped to [1 - levels[-1], 1 - levels[0]].

    Report values at the clip as "<1%" or ">99%", never as exact numbers.
    """
    return 1.0 - cdf_at(q, levels, threshold)
