"""Shared point model: damped, pooled log-linear growth (PROTOCOL §8).

Vectorised over locations and forecast origins. Input Z is log(y+1) with shape (L, T);
the national series is the row named 'US'. All quantities at origin o use Z[:, :o+1] only.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

STEPS = 4  # s = h + 1 for h = 0..3


@dataclass(frozen=True)
class PointCfg:
    w: int = 4
    phi: float = 0.9
    lam_n: float = 0.0
    lam_s: float = 0.0
    level: str = "fit"   # 'fit' or 'last'
    g_max: float = 1.0


def _ols_coeffs(w: int) -> np.ndarray:
    j = np.arange(w) - (w - 1) / 2.0
    return j / np.sum(j ** 2)


def slopes_and_levels(Z: np.ndarray, w: int) -> tuple[np.ndarray, np.ndarray]:
    """OLS slope and fitted end-value over the trailing window of length w ending at each origin.

    Returns arrays of shape (L, T); origins with fewer than w points are NaN.
    """
    L, T = Z.shape
    slope = np.full((L, T), np.nan)
    level = np.full((L, T), np.nan)
    if T >= w:
        win = sliding_window_view(Z, w, axis=1)            # (L, T-w+1, w)
        c = _ols_coeffs(w)
        s = win @ c
        m = win.mean(axis=2)
        slope[:, w - 1:] = s
        level[:, w - 1:] = m + s * (w - 1) / 2.0
    return slope, level


def seasonal_slope(z_nat: np.ndarray, dates: np.ndarray) -> np.ndarray:
    """Mean national log-growth over the 4 weeks following the same date 1 and 2 years earlier.

    Uses only values strictly before each origin (they are >= 48 weeks in the past). 0 if none.
    """
    T = len(z_nat)
    out = np.zeros(T)
    for o in range(T):
        vals = []
        for k in (52, 104):
            a = o - k
            b = a + 4
            if a >= 0 and b < o:
                vals.append((z_nat[b] - z_nat[a]) / 4.0)
        out[o] = np.mean(vals) if vals else 0.0
    return out


def point_forecasts(Z: np.ndarray, nat_idx: int, cfg: PointCfg, sea: np.ndarray | None = None) -> np.ndarray:
    """Log-scale point forecasts for steps 1..4 at every origin. Shape (L, T, STEPS)."""
    slope, fit_level = slopes_and_levels(Z, cfg.w)
    g_nat = slope[nat_idx][None, :]
    if sea is None:
        sea = seasonal_slope(Z[nat_idx], None)
    g = (1 - cfg.lam_n - cfg.lam_s) * slope + cfg.lam_n * g_nat + cfg.lam_s * sea[None, :]
    g = np.clip(g, -cfg.g_max, cfg.g_max)
    lvl = fit_level if cfg.level == "fit" else Z
    damp = np.cumsum(cfg.phi ** np.arange(1, STEPS + 1))  # sum_{i=1..s} phi^i
    return lvl[:, :, None] + g[:, :, None] * damp[None, None, :]
