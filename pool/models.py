"""NABD-Pool candidates. All work on the logit of positivity and predict the within-season change
y[t+h] - y[t]; outputs are FluSight-style quantiles in PERCENT.

G  PoolGBM     one gradient-boosted quantile model per level (scikit-learn HistGradientBoosting, as in the
               kit's GlobalQuantileGBM / Flusion design), all horizons and countries in one fit, features FEATS_G.
L  PoolLinear  partial pooling of the local v1 method: v1's linear form with coefficients fitted on pooled
               development rows, shrunk towards the country's own v1 fit with weight n/(n+k) (n = own seasons).
K  kit GlobalQuantileGBM on % positivity (wrapped in pool/harness.py).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from pool.features import FEATS_G, FEATS_L
from uae.models import QUANTILES, expit

Q = np.asarray(QUANTILES)


def to_percent(logit_q: np.ndarray) -> np.ndarray:
    return 100.0 * expit(np.sort(logit_q, axis=-1))


class PoolGBM:
    name = "NABD-Pool-G"

    def __init__(self, max_iter=150, learning_rate=0.06, max_leaf_nodes=15, min_samples_leaf=40,
                 l2_regularization=1.0, levels=None, seed=0):
        self.params = dict(max_iter=max_iter, learning_rate=learning_rate, max_leaf_nodes=max_leaf_nodes,
                           min_samples_leaf=min_samples_leaf, l2_regularization=l2_regularization,
                           early_stopping=False, random_state=seed)
        self.levels = np.asarray(levels if levels is not None else QUANTILES, float)
        self.models = {}

    def fit(self, train: pd.DataFrame):
        t = train.dropna(subset=["target", "y0"])
        X = t[FEATS_G].to_numpy(float)
        y = t.target.to_numpy(float)
        for tau in self.levels:
            m = HistGradientBoostingRegressor(loss="quantile", quantile=float(tau), **self.params)
            self.models[float(tau)] = m.fit(X, y)
        self.n_train = len(t)
        return self

    def predict_logit(self, rows: pd.DataFrame) -> np.ndarray:
        X = rows[FEATS_G].to_numpy(float)
        ch = np.column_stack([self.models[float(t)].predict(X) for t in self.levels])
        ch = np.sort(ch, axis=1)
        if len(self.levels) != len(Q):       # interpolate the quantile function to the 23 FluSight levels
            ch = np.vstack([np.interp(Q, self.levels, r) for r in ch])
        return rows.y0.to_numpy(float)[:, None] + ch


class PoolLinear:
    name = "NABD-Pool-L"

    def __init__(self, k=4.0):
        self.k = float(k)
        self.beta, self.rq = {}, {}

    def fit(self, train: pd.DataFrame):
        for h, g in train.groupby("h"):
            g = g.dropna(subset=FEATS_L + ["target"])
            X = np.c_[np.ones(len(g)), g[FEATS_L].to_numpy(float)]
            b, *_ = np.linalg.lstsq(X, g.target.to_numpy(float), rcond=None)
            self.beta[int(h)] = b
            self.rq[int(h)] = np.quantile(g.target.to_numpy(float) - X @ b, Q)
        return self

    def predict_logit(self, rows: pd.DataFrame, local=None, n_own: int = 0) -> np.ndarray:
        """local = fitted uae.models.NabdUAE for the target country (or None). Rows with missing v1
        features give NaN (dropped by the common-cell rule, exactly as for local v1)."""
        out = np.full((len(rows), len(Q)), np.nan)
        w = n_own / (n_own + self.k) if (local is not None and np.isfinite(self.k)) else 0.0
        for j, (_, r) in enumerate(rows.iterrows()):
            h = int(r.h)
            x = np.r_[1.0, r[FEATS_L].to_numpy(float)]
            if np.isnan(x).any():
                continue
            b, rq = self.beta[h], self.rq[h]
            if w > 0:
                b = w * local.beta[h] + (1 - w) * b
                rq = w * np.quantile(local.resid[h], Q) + (1 - w) * rq
            out[j] = r.y0 + x @ b + rq
        return out


def ensemble_percent(members) -> np.ndarray:
    """Quantile average (Vincentization) of member forecasts in percent; NaN if any member is NaN."""
    return np.sort(np.mean(np.stack(members, axis=0), axis=0), axis=-1)
