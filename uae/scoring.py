"""Weighted interval score (WIS) for quantile forecasts, following Bracher et al. (2021),
as used by the CDC FluSight hub. WIS = (1/(K+0.5)) * (0.5*|y-m| + sum_k (alpha_k/2) * IS_alpha_k)."""
import numpy as np


def wis(quantiles, values, y):
    q = np.asarray(quantiles, float)
    v = np.sort(np.asarray(values, float))
    med = v[np.argmin(np.abs(q - 0.5))]
    total = 0.5 * abs(y - med)
    lowers = q[q < 0.5]
    K = 0
    for lo in lowers:
        hi = 1 - lo
        j_lo = np.argmin(np.abs(q - lo))
        j_hi = np.argmin(np.abs(q - hi))
        if abs(q[j_hi] - hi) > 1e-9:
            continue
        alpha = 2 * lo
        l, u = v[j_lo], v[j_hi]
        IS = (u - l) + (2 / alpha) * max(l - y, 0) + (2 / alpha) * max(y - u, 0)
        total += (alpha / 2) * IS
        K += 1
    return total / (K + 0.5)


def covered(quantiles, values, y, level):
    q = np.asarray(quantiles, float)
    v = np.sort(np.asarray(values, float))
    lo, hi = (1 - level) / 2, 1 - (1 - level) / 2
    l = v[np.argmin(np.abs(q - lo))]
    u = v[np.argmin(np.abs(q - hi))]
    return bool(l <= y <= u)
