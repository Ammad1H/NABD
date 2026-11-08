"""Scoring for quantile forecasts, written independently as a cross-check.

Run NABD's own scorer and this one on the same forecasts; they should agree to
floating-point precision. A disagreement is an integrity finding, whichever is
wrong.

References: Bracher et al. 2021 (WIS and its decomposition); Cramer et al. 2022
(pairwise relative WIS); Diebold & Mariano 1995 with the Harvey, Leybourne &
Newbold 1997 small-sample correction.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from .quantiles import check_levels, sort_quantiles


def pinball(q, y, levels) -> np.ndarray:
    """Quantile (pinball) loss per level: rho_tau(y - q)."""
    lv = np.asarray(levels, dtype=float)
    q = np.asarray(q, dtype=float)
    yy = np.asarray(y, dtype=float)[..., None]
    return np.where(yy >= q, lv * (yy - q), (1.0 - lv) * (q - yy))


def wis(q, y, levels) -> np.ndarray:
    """Weighted interval score.

    For K central intervals plus the median, WIS equals the sum of pinball losses
    over all 2K + 1 levels divided by (K + 1/2). Quantiles are sorted first.
    """
    lv = check_levels(levels)
    qs = sort_quantiles(q)
    k = (lv.size - 1) / 2.0
    return pinball(qs, y, lv).sum(axis=-1) / (k + 0.5)


def wis_components(q, y, levels):
    """Split WIS into (dispersion, overprediction, underprediction).

    The three parts sum to WIS exactly. Overprediction means the forecast was too
    high (truth below the lower bounds); underprediction means too low.
    """
    lv = check_levels(levels)
    qs = sort_quantiles(q)
    y = np.asarray(y, dtype=float)
    n_lv = lv.size
    k = (n_lv - 1) // 2
    lower = qs[..., :k]
    upper = qs[..., ::-1][..., :k]  # pairs levels[i] with levels[n_lv - 1 - i]
    alpha = 2.0 * lv[:k]
    yy = y[..., None]
    med = qs[..., k]
    norm = k + 0.5
    dispersion = (alpha / 2.0 * (upper - lower)).sum(axis=-1) / norm
    over = (np.clip(lower - yy, 0.0, None).sum(axis=-1)
            + 0.5 * np.clip(med - y, 0.0, None)) / norm
    under = (np.clip(yy - upper, 0.0, None).sum(axis=-1)
             + 0.5 * np.clip(y - med, 0.0, None)) / norm
    return dispersion, over, under


def interval_hit(q, y, levels, coverage: float) -> np.ndarray:
    """True where y falls inside the central interval of nominal `coverage`."""
    lv = check_levels(levels)
    lo_level = (1.0 - coverage) / 2.0
    i = np.where(np.isclose(lv, lo_level))[0]
    j = np.where(np.isclose(lv, 1.0 - lo_level))[0]
    if i.size == 0 or j.size == 0:
        raise ValueError(f"levels do not contain a {coverage:.0%} central interval")
    qs = sort_quantiles(q)
    y = np.asarray(y, dtype=float)
    return (y >= qs[..., i[0]]) & (y <= qs[..., j[0]])


def pairwise_relative_wis(scores: pd.DataFrame, keys, model_col: str = "model",
                          score_col: str = "wis", baseline: str | None = None) -> pd.DataFrame:
    """Relative WIS by pairwise tournament (Cramer et al. 2022).

    theta_ij = mean WIS_i / mean WIS_j over the forecasts both models made;
    theta_i = geometric mean of theta_ij over all M models (self ratio = 1);
    rel_wis = theta_i / theta_baseline. With two models this reduces to the
    plain ratio of mean WIS over their overlap.
    """
    wide = scores.pivot_table(index=list(keys), columns=model_col,
                              values=score_col, aggfunc="mean")
    models = list(wide.columns)
    m = len(models)
    rows = []
    for a in models:
        acc = 0.0
        n_overlap = []
        for b in models:
            if a == b:
                continue
            both = wide[[a, b]].dropna()
            if both.empty:
                raise ValueError(f"no overlapping forecasts for {a} and {b}")
            acc += np.log(both[a].mean() / both[b].mean())
            n_overlap.append(len(both))
        rows.append({"model": a, "theta": float(np.exp(acc / m)),
                     "min_overlap": int(min(n_overlap)) if n_overlap else 0})
    out = pd.DataFrame(rows)
    if baseline is not None:
        if baseline not in models:
            raise ValueError(f"baseline {baseline!r} not among models")
        base = float(out.loc[out["model"] == baseline, "theta"].iloc[0])
        out["rel_wis"] = out["theta"] / base
        out = out.sort_values("rel_wis")
    return out.reset_index(drop=True)


def block_bootstrap_ratio(df: pd.DataFrame, a_col: str, b_col: str, time_col: str,
                          block_len: int = 4, n_boot: int = 2000, ci: float = 0.95,
                          seed: int = 0, group_col: str | None = None) -> dict:
    """Moving-block bootstrap CI for sum(a) / sum(b) (ratio of mean scores).

    Rows are first summed per time point (keeping all locations and horizons of
    one reference date together), then contiguous blocks of `block_len` time
    points are resampled. With `group_col` (e.g. season) no block crosses groups.
    Pre-register block_len; do not tune it after seeing the CI.
    """
    keys = [group_col, time_col] if group_col else [time_col]
    agg = df.groupby(keys, sort=True)[[a_col, b_col]].sum().reset_index()
    a = agg[a_col].to_numpy(float)
    b = agg[b_col].to_numpy(float)
    groups = agg[group_col].to_numpy() if group_col else np.zeros(len(agg))
    starts = []
    for g in pd.unique(groups):
        idx = np.where(groups == g)[0]
        span = max(len(idx) - block_len + 1, 1)
        starts.extend(idx[:span].tolist())
    starts = np.array(starts)
    n = len(agg)
    n_blocks = int(np.ceil(n / block_len))
    rng = np.random.default_rng(seed)
    ratios = np.empty(n_boot)
    for r in range(n_boot):
        chosen = rng.choice(starts, size=n_blocks, replace=True)
        idx = np.concatenate([np.arange(s, min(s + block_len, n)) for s in chosen])[:n]
        ratios[r] = a[idx].sum() / b[idx].sum()
    lo, hi = np.quantile(ratios, [(1 - ci) / 2, 1 - (1 - ci) / 2])
    return {"ratio": float(a.sum() / b.sum()), "lo": float(lo), "hi": float(hi),
            "n_time_points": int(n), "block_len": int(block_len), "n_boot": int(n_boot)}


def dm_test(d, h: int = 1) -> dict:
    """Diebold-Mariano test on a loss-differential series d_t = L_A,t - L_B,t.

    Uses the HLN small-sample correction and a t(T-1) reference. Order d by time
    and aggregate to one value per reference date before calling. Negative mean
    means A had lower loss.
    """
    d = np.asarray(d, dtype=float)
    t_len = d.size
    if t_len < 3:
        raise ValueError("need at least 3 time points")
    dbar = d.mean()
    gamma = [np.sum((d[k:] - dbar) * (d[:t_len - k] - dbar)) / t_len for k in range(h)]
    var = (gamma[0] + 2.0 * sum(gamma[1:])) / t_len
    if var <= 0:
        return {"mean_diff": float(dbar), "stat": float("nan"), "p_value": float("nan")}
    stat = dbar / np.sqrt(var)
    stat *= np.sqrt((t_len + 1 - 2 * h + h * (h - 1) / t_len) / t_len)
    p = 2.0 * (1.0 - stats.t.cdf(abs(stat), df=t_len - 1))
    return {"mean_diff": float(dbar), "stat": float(stat), "p_value": float(p), "T": int(t_len)}
