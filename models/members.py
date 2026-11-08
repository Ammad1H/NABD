"""NABD ensemble members (PROTOCOL §8)."""
from __future__ import annotations

import numpy as np
from scipy.stats import nbinom

from .data import QUANTILES
from .point import STEPS, slopes_and_levels


def nb_dispersion(Z: np.ndarray, fit_w: int = 8, r_min: float = 1.0, r_max: float = 1000.0) -> np.ndarray:
    """Per-location NB size r from residuals of a local log-linear fit over the last fit_w weeks.

    For NB, Var(log(y+1)) ~ 1/(mu+1) + 1/r, so 1/r ~ var(resid) - mean(1/(mu+1)).
    """
    L, T = Z.shape
    w = min(fit_w, T)
    seg = Z[:, -w:]
    j = np.arange(w) - (w - 1) / 2.0
    b = (seg * j).sum(1) / np.sum(j ** 2)
    a = seg.mean(1)
    fit = a[:, None] + b[:, None] * j[None, :]
    resid = seg - fit
    var = resid.var(axis=1, ddof=2) if w > 2 else np.zeros(L)
    mu = np.expm1(fit).clip(min=0)
    inv_r = var - np.mean(1.0 / (mu + 1.0), axis=1)
    inv_r = np.clip(inv_r, 1.0 / r_max, 1.0 / r_min)
    return 1.0 / inv_r


def glm_quantiles(zhat_t0: np.ndarray, r: np.ndarray, c: float) -> np.ndarray:
    """NB2 predictive quantiles. zhat_t0: (L, STEPS) log-point forecasts at origin t0.

    Variance is inflated by c**s while keeping the mean. Returns (L, STEPS, 23).
    """
    mu = np.expm1(zhat_t0).clip(min=1e-6)                       # (L, S)
    s = np.arange(1, STEPS + 1)[None, :]
    base_var = mu + mu ** 2 / r[:, None]
    var = base_var * (c ** s)
    extra = var - mu                                              # mu^2 / r'
    extra = np.maximum(extra, 1e-9)
    r2 = mu ** 2 / extra
    p = r2 / (r2 + mu)
    q = nbinom.ppf(QUANTILES[None, None, :], r2[:, :, None], p[:, :, None])
    q = np.nan_to_num(q, nan=0.0, posinf=np.nanmax(mu) * 10)
    return np.maximum.accumulate(q, axis=2)


def eeq_errors(Z: np.ndarray, zhat_all: np.ndarray, H: int) -> np.ndarray:
    """Rolling-origin log-errors at each step from origins in the last H weeks (within vintage).

    zhat_all: (L, T, STEPS) point forecasts at every origin. Returns list per step of pooled errors.
    """
    L, T, S = zhat_all.shape
    t0 = T - 1
    errs = []
    for s in range(1, S + 1):
        lo = max(0, t0 - H - s + 1)
        hi = t0 - s                     # last origin whose target (o+s) is observed
        if hi < lo:
            errs.append(np.zeros(1))
            continue
        o = np.arange(lo, hi + 1)
        e = Z[:, o + s] - zhat_all[:, o, s - 1]
        e = e[np.isfinite(e)]
        errs.append(e if e.size else np.zeros(1))
    return errs


def eeq_quantiles(zhat_t0: np.ndarray, errs: list[np.ndarray]) -> np.ndarray:
    out = np.empty(zhat_t0.shape + (len(QUANTILES),))
    for s, e in enumerate(errs):
        eq = np.quantile(e, QUANTILES)
        out[:, s, :] = np.expm1(zhat_t0[:, s][:, None] + eq[None, :])
    return np.maximum.accumulate(out.clip(min=0), axis=2)


LEVEL_EDGES = np.log1p([20.0, 200.0])   # strata: <=20, 20-200, >200 weekly admissions


def eeq_quantiles_stratified(Z: np.ndarray, zhat_all: np.ndarray, H: int, zhat_t0: np.ndarray,
                             min_n: int = 50, stale: int = 0) -> np.ndarray:
    """EEQ with errors pooled within level strata (level = log1p count at the origin).

    Deviation D1 (pre-test, see docs/DEVIATIONS.md): pooled log-errors mix small-count states
    (large log noise) with large ones; stratifying by current level keeps the family
    'empirical error quantiles pooled over locations' but pools within comparable levels.
    """
    L, T, S = zhat_all.shape
    t0 = T - 1
    cur = np.digitize(Z[:, t0], LEVEL_EDGES)
    out = np.empty((L, S, len(QUANTILES)))
    for j in range(1, S + 1):
        s = min(j + stale, S)        # error step used for output step j (stale vintage -> longer)
        lo = max(0, t0 - H - s + 1)
        hi = t0 - s
        if hi < lo:
            out[:, j - 1, :] = np.expm1(zhat_t0[:, j - 1])[:, None]
            continue
        o = np.arange(lo, hi + 1)
        e = Z[:, o + s] - zhat_all[:, o, s - 1]           # (L, n_o)
        st = np.digitize(Z[:, o], LEVEL_EDGES)             # stratum at origin
        ok = np.isfinite(e)
        pooled = np.quantile(e[ok], QUANTILES) if ok.any() else np.zeros(len(QUANTILES))
        for k in range(3):
            m = ok & (st == k)
            eq = np.quantile(e[m], QUANTILES) if m.sum() >= min_n else pooled
            idx = cur == k
            out[idx, j - 1, :] = np.expm1(zhat_t0[idx, j - 1][:, None] + eq[None, :])
    return np.maximum.accumulate(out.clip(min=0), axis=2)


def widen(q: np.ndarray, k: float) -> np.ndarray:
    """Multiplicative widening of all quantiles about the median by factor k."""
    if k == 1.0:
        return q
    med = q[..., [11]]
    out = med + k * (q - med)
    return np.maximum.accumulate(out.clip(min=0), axis=-1)


def vincent(members: list[np.ndarray]) -> np.ndarray:
    return np.maximum.accumulate(np.mean(members, axis=0), axis=-1)
