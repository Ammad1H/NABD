"""Per-reference-date forecasting engine for the US-A track.

`prepare(R)` builds the vintage-correct log matrix once; `member_quantiles` evaluates members for
any configuration. Everything is computed from `series_as_of(R)` only (PROTOCOL §2).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .data import series_as_of
from .members import eeq_errors, eeq_quantiles, eeq_quantiles_stratified, glm_quantiles, nb_dispersion
from .point import PointCfg, point_forecasts, seasonal_slope


@dataclass
class Prepared:
    R: pd.Timestamp
    Y: np.ndarray            # (L, T) counts up to t0 = R-7
    Z: np.ndarray            # log1p(Y)
    locs: list[str]
    dates: pd.DatetimeIndex
    nat_idx: int
    sea: np.ndarray
    r: np.ndarray            # NB size per location
    meta: dict

    def target_end_dates(self) -> list[pd.Timestamp]:
        return [self.R + pd.Timedelta(days=7 * h) for h in range(4)]


def prepare(R, drop_weeks: int = 0) -> Prepared:
    """drop_weeks > 0 simulates a delayed feed (robustness diagnostic only; default 0)."""
    w, meta = series_as_of(R)
    if drop_weeks:
        w = w.iloc[:, :-drop_weeks]
        meta = {**meta, "stale_weeks": meta["stale_weeks"] + drop_weeks,
                "last_week": w.columns.max().date().isoformat(), "simulated_dropout_weeks": drop_weeks}
    Y = w.to_numpy(dtype=float)
    Z = np.log1p(Y)
    locs = list(w.index)
    nat = locs.index("US")
    sea = seasonal_slope(Z[nat], None)
    r = nb_dispersion(Z)
    return Prepared(pd.Timestamp(R), Y, Z, locs, w.columns, nat, sea, r, meta)


def point_t0(P: Prepared, cfg: PointCfg) -> tuple[np.ndarray, np.ndarray]:
    """Return (zhat for h=0..3 at origin t0, all-origin forecasts for steps 1..4)."""
    k = P.meta["stale_weeks"]
    zall = point_forecasts(P.Z, P.nat_idx, cfg, P.sea)
    if k == 0:
        return zall[:, -1, :], zall
    # Stale vintage: targets are steps k+1..k+4 ahead. Use the damped form directly.
    from .point import slopes_and_levels
    slope, fit_level = slopes_and_levels(P.Z, cfg.w)
    g_nat = slope[P.nat_idx]
    g = (1 - cfg.lam_n - cfg.lam_s) * slope[:, -1] + cfg.lam_n * g_nat[-1] + cfg.lam_s * P.sea[-1]
    g = np.clip(g, -cfg.g_max, cfg.g_max)
    lvl = fit_level[:, -1] if cfg.level == "fit" else P.Z[:, -1]
    damp = np.cumsum(cfg.phi ** np.arange(1, 4 + k + 1))[k:]
    return lvl[:, None] + g[:, None] * damp[None, :], zall


def glm_member(P: Prepared, cfg: PointCfg, c: float, zt0=None) -> np.ndarray:
    if zt0 is None:
        zt0, _ = point_t0(P, cfg)
    return glm_quantiles(zt0, P.r, c)


def eeq_member(P: Prepared, cfg: PointCfg, H: int, pre=None, strata: str = "pooled") -> np.ndarray:
    if pre is None:
        zt0, zall = point_t0(P, cfg)
    else:
        zt0, zall = pre
    if strata == "level3":
        return eeq_quantiles_stratified(P.Z, zall, H, zt0, stale=P.meta["stale_weeks"])
    errs = eeq_errors(P.Z, zall, H)
    if P.meta["stale_weeks"]:
        # stale: errors at step s+k approximated by the largest available step's distribution
        errs = errs[min(P.meta["stale_weeks"], 3):] + [errs[-1]] * min(P.meta["stale_weeks"], 3)
    return eeq_quantiles(zt0, errs)
