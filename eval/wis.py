"""Weighted interval score (PROTOCOL §6). Two equivalent implementations, tested to agree."""
from __future__ import annotations

import numpy as np

QUANTILES = np.array([0.01, 0.025, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5,
                      0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.975, 0.99])


def wis_pinball(q: np.ndarray, y: np.ndarray, taus: np.ndarray = QUANTILES) -> np.ndarray:
    """WIS = (2/|Q|) * sum_tau PL_tau. q: (..., 23), y: (...)."""
    y = np.asarray(y, dtype=float)[..., None]
    pl = ((y < q).astype(float) - taus) * (q - y)
    return 2.0 * pl.sum(-1) / len(taus)


def wis_interval(q: np.ndarray, y: np.ndarray, taus: np.ndarray = QUANTILES) -> np.ndarray:
    """Bracher et al. (2021) interval form with K central intervals plus the median."""
    y = np.asarray(y, dtype=float)
    K = (len(taus) - 1) // 2
    med = q[..., K]
    total = 0.5 * np.abs(y - med)
    for k in range(K):
        alpha = 2 * taus[k]
        lo, hi = q[..., k], q[..., len(taus) - 1 - k]
        IS = (hi - lo) + (2 / alpha) * (lo - y) * (y < lo) + (2 / alpha) * (y - hi) * (y > hi)
        total = total + (alpha / 2) * IS
    return total / (K + 0.5)


def coverage(q: np.ndarray, y: np.ndarray, level: float) -> np.ndarray:
    lo_tau = (1 - level) / 2
    i = int(np.argmin(np.abs(QUANTILES - lo_tau)))
    j = len(QUANTILES) - 1 - i
    y = np.asarray(y, dtype=float)
    return ((y >= q[..., i]) & (y <= q[..., j])).astype(float)


wis = wis_pinball
