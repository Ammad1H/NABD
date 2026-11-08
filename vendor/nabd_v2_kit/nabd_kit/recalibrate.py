"""Recalibration methods for quantile forecasts.

* `GroupedRecalibrator`: per group (e.g. as-of phase x horizon), a blend weight
  between the model and a reference forecast (usually persistence) and an
  interval-spread scale, all fitted by minimising mean WIS on DEVELOPMENT data
  only. Few parameters (2-3 per group), so low overfitting risk, but they must
  still be locked before any test score.
* `QuantileTracker`: online calibration by quantile tracking (Angelopoulos,
  Candes & Tibshirani 2023): per quantile level, an additive offset on a
  fourth-root scale nudged after each truth arrives, pooled across locations
  within a group (e.g. horizon). This is a real "online calibration" feature.
"""
from __future__ import annotations

import json

import numpy as np

from .ensemble import quantile_average
from .quantiles import check_levels, sort_quantiles
from .scoring import wis


def _mean_wis(q, y, levels) -> float:
    return float(np.mean(wis(q, y, levels)))


def apply_spread(q, levels, s_lo: float, s_hi: float | None = None,
                 nonneg: bool = True) -> np.ndarray:
    """Scale distances from the median: lower side by s_lo, upper side by s_hi."""
    lv = check_levels(levels)
    qs = sort_quantiles(q)
    k = lv.size // 2
    m = qs[..., k:k + 1]
    s_hi = s_lo if s_hi is None else s_hi
    scale = np.where(lv < 0.5, s_lo, s_hi)
    out = m + scale * (qs - m)
    if nonneg:
        out = np.clip(out, 0.0, None)
    return np.sort(out, axis=-1)


def fit_spread(q, y, levels, grid=None, asymmetric: bool = False,
               nonneg: bool = True) -> dict:
    """Grid-search the spread scale(s) that minimise mean WIS.

    WIS is a sum of per-level pinball losses, so the lower and upper scales are
    separable and the asymmetric fit is two 1-D searches.
    """
    lv = check_levels(levels)
    grid = np.linspace(0.5, 2.0, 31) if grid is None else np.asarray(grid, dtype=float)
    lower, upper = lv < 0.5, lv > 0.5

    def side_loss(s, mask):
        qq = apply_spread(q, lv, s, s, nonneg)
        yy = np.asarray(y, dtype=float)[..., None]
        pin = np.where(yy >= qq, lv * (yy - qq), (1 - lv) * (qq - yy))
        return float(pin[..., mask].sum(axis=-1).mean())

    if asymmetric:
        s_lo = float(grid[int(np.argmin([side_loss(s, lower) for s in grid]))])
        s_hi = float(grid[int(np.argmin([side_loss(s, upper) for s in grid]))])
    else:
        scores = [_mean_wis(apply_spread(q, lv, s, s, nonneg), y, lv) for s in grid]
        s_lo = s_hi = float(grid[int(np.argmin(scores))])
    return {"s_lo": s_lo, "s_hi": s_hi,
            "wis": _mean_wis(apply_spread(q, lv, s_lo, s_hi, nonneg), y, lv)}


def fit_blend_weight(qa, qb, y, levels, grid=None) -> dict:
    """Weight w on forecast A (1 - w on B) minimising mean WIS of the average."""
    lv = check_levels(levels)
    grid = np.linspace(0.0, 1.0, 21) if grid is None else np.asarray(grid, dtype=float)
    scores = [_mean_wis(quantile_average([qa, qb], [w, 1.0 - w]), y, lv) for w in grid]
    i = int(np.argmin(scores))
    return {"w": float(grid[i]), "wis": float(scores[i])}


class GroupedRecalibrator:
    """Blend-then-spread recalibration fitted separately per group.

    fit(qa, qb, y, groups): qa = model quantiles (n, L), qb = reference quantiles
    (n, L), y = truth (n,), groups = (n,) string keys such as "falling|h2".
    Groups with fewer than `min_n` rows use the pooled fit. Unknown groups at
    transform time also use the pooled fit.
    """

    POOLED = "__pooled__"

    def __init__(self, levels, w_grid=None, s_grid=None, min_n: int = 50,
                 spread: bool = True, asymmetric: bool = False, nonneg: bool = True):
        self.levels = check_levels(levels)
        self.w_grid = w_grid
        self.s_grid = s_grid
        self.min_n = int(min_n)
        self.spread = spread
        self.asymmetric = asymmetric
        self.nonneg = nonneg
        self.params_: dict = {}

    def _fit_one(self, qa, qb, y) -> dict:
        before = _mean_wis(qa, y, self.levels)
        bw = fit_blend_weight(qa, qb, y, self.levels, self.w_grid)
        qbl = quantile_average([qa, qb], [bw["w"], 1.0 - bw["w"]])
        if self.spread:
            sp = fit_spread(qbl, y, self.levels, self.s_grid, self.asymmetric, self.nonneg)
        else:
            sp = {"s_lo": 1.0, "s_hi": 1.0, "wis": bw["wis"]}
        return {"w": bw["w"], "s_lo": sp["s_lo"], "s_hi": sp["s_hi"], "n": int(len(y)),
                "train_wis_model": before, "train_wis_after": sp["wis"]}

    def fit(self, qa, qb, y, groups):
        qa, qb = np.asarray(qa, float), np.asarray(qb, float)
        y, groups = np.asarray(y, float), np.asarray(groups).astype(str)
        pooled = self._fit_one(qa, qb, y)
        self.params_ = {self.POOLED: dict(pooled, source="pooled")}
        for g in np.unique(groups):
            mask = groups == g
            if mask.sum() >= self.min_n:
                self.params_[g] = dict(self._fit_one(qa[mask], qb[mask], y[mask]), source="group")
            else:
                self.params_[g] = dict(pooled, n=int(mask.sum()), source="pooled-fallback")
        return self

    def transform(self, qa, qb, groups) -> np.ndarray:
        if not self.params_:
            raise RuntimeError("fit() first, or load locked params with from_json()")
        qa, qb = np.asarray(qa, float), np.asarray(qb, float)
        groups = np.asarray(groups).astype(str)
        out = np.empty_like(qa)
        for g in np.unique(groups):
            p = self.params_.get(g, self.params_[self.POOLED])
            mask = groups == g
            qbl = quantile_average([qa[mask], qb[mask]], [p["w"], 1.0 - p["w"]])
            out[mask] = apply_spread(qbl, self.levels, p["s_lo"], p["s_hi"], self.nonneg)
        return out

    def to_json(self) -> str:
        """Serialise the fitted parameters so they can be hashed into a lock."""
        return json.dumps({"levels": self.levels.tolist(), "params": self.params_,
                           "nonneg": self.nonneg}, sort_keys=True, indent=1)

    @classmethod
    def from_json(cls, text: str) -> "GroupedRecalibrator":
        d = json.loads(text)
        obj = cls(d["levels"], nonneg=d.get("nonneg", True))
        obj.params_ = d["params"]
        return obj


class QuantileTracker:
    """Online calibration by quantile tracking, pooled within groups.

    adjust(q, group) -> the quantiles to ISSUE. update(issued_q, y, group) when
    the truth for previously issued forecasts arrives (delayed by the horizon).
    The offset for level tau moves by lr * scale * mean(tau - 1{y <= q_issued}),
    which settles where the empirical coverage of each level equals tau. `scale`
    is an EWMA of the absolute median error on the transformed scale, so `lr` is
    unit-free. Pre-register lr; do not tune it on test data.
    """

    def __init__(self, levels, lr: float = 0.1, power: float = 0.25, ewma: float = 0.1):
        self.levels = check_levels(levels)
        self.lr, self.power, self.ewma = float(lr), float(power), float(ewma)
        self.offsets: dict = {}
        self.scale: dict = {}
        self.n_updates: dict = {}

    def _f(self, x):
        return np.power(np.clip(np.asarray(x, float), 0.0, None), self.power)

    def _g(self, z):
        return np.power(np.clip(np.asarray(z, float), 0.0, None), 1.0 / self.power)

    def adjust(self, q, group: str) -> np.ndarray:
        b = self.offsets.get(str(group), np.zeros(self.levels.size))
        return np.sort(self._g(self._f(sort_quantiles(q)) + b), axis=-1)

    def update(self, issued_q, y, group: str) -> None:
        group = str(group)
        z = self._f(np.atleast_2d(issued_q))
        zy = self._f(np.atleast_1d(y))[:, None]
        hit = (zy <= z).astype(float)
        grad = (self.levels[None, :] - hit).mean(axis=0)
        k = self.levels.size // 2
        mae = float(np.mean(np.abs(zy[:, 0] - z[:, k])))
        prev = self.scale.get(group)
        sc = mae if prev is None else (1 - self.ewma) * prev + self.ewma * mae
        self.scale[group] = sc
        self.offsets[group] = self.offsets.get(group, np.zeros(self.levels.size)) + self.lr * sc * grad
        self.n_updates[group] = self.n_updates.get(group, 0) + 1

    def state(self) -> dict:
        return {g: {"offsets": v.tolist(), "scale": self.scale.get(g),
                    "n_updates": self.n_updates.get(g, 0)} for g, v in self.offsets.items()}
