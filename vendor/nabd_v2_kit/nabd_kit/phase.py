"""Epidemic phase labels.

Two different things, never to be mixed up:

* `asof_log_slope` + `classify` use only data up to the reference week. Safe as
  a model input, a blending group, or a pre-registered stratum.
* `realized_phase` uses the truth at the target week. Evaluation only: it peeks
  at the future, so it can describe where a model failed but cannot steer one.

Pre-register `window`, `band` and `offset`; do not tune them on test seasons.
"""
from __future__ import annotations

import numpy as np

RISING, FLAT, FALLING, UNKNOWN = "rising", "flat", "falling", "unknown"


def asof_log_slope(y, window: int = 3, offset: float = 1.0) -> np.ndarray:
    """Least-squares slope of log(y + offset) over the last `window` weeks.

    Element t uses y[t - window + 1 .. t] only. NaN until enough history, or when
    any value in the window is missing.
    """
    ly = np.log(np.asarray(y, dtype=float) + offset)
    n = ly.size
    out = np.full(n, np.nan)
    if n < window:
        return out
    x = np.arange(window) - (window - 1) / 2.0
    denom = float((x ** 2).sum())
    segs = np.lib.stride_tricks.sliding_window_view(ly, window)
    slopes = (segs - segs.mean(axis=1, keepdims=True)) @ x / denom
    out[window - 1:] = slopes
    return out


def classify(slope, band: float = 0.1) -> np.ndarray:
    """Map weekly log-slopes to rising / flat / falling (unknown for NaN).

    band = 0.1 means about +/-10.5% per week.
    """
    s = np.asarray(slope, dtype=float)
    lab = np.where(s > band, RISING, np.where(s < -band, FALLING, FLAT)).astype(object)
    lab[np.isnan(s)] = UNKNOWN
    return lab


def realized_phase(y_ref, y_target, horizon, band: float = 0.1,
                   offset: float = 1.0) -> np.ndarray:
    """EVALUATION ONLY: phase from the realized change reference -> target week.

    Uses future data. Horizons <= 0 (nowcasts) get 'unknown'.
    """
    h = np.asarray(horizon, dtype=float)
    yr = np.asarray(y_ref, dtype=float)
    yt = np.asarray(y_target, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        g = (np.log(yt + offset) - np.log(yr + offset)) / np.where(h > 0, h, np.nan)
    return classify(g, band=band)
