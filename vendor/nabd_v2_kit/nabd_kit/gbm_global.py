"""Global gradient-boosted quantile model, in the spirit of Flusion.

Design (after Ray, Wang, Wolfinger & Reich, "Flusion", 2024): ONE model per
quantile level, trained jointly across all locations and, optionally, across
several surveillance sources (e.g. ILINet, FluSurv-NET and NHSN histories for
the US, or several countries' FluNet series), on a fourth-root, per-series
scaled signal. Each row predicts the change from the reference week at one
horizon, from lags, local Taylor (level / slope / curvature) features, season
timing and the horizon itself. Pooling many series gives the model many more
rises, peaks and declines than one short series can.

This is not Flusion's code and not a replica of its exact feature set. It uses
scikit-learn's HistGradientBoostingRegressor so it runs without LightGBM.

Leakage rules built in:
* predict() drops every row dated after the reference date before doing anything.
* per-series scales come from the training data (fit) or, for series unseen in
  fit, from that series' own history up to the reference date.
* extra feature columns are taken at the reference week as given: the caller
  must make sure they were knowable then (lag them if in doubt).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from .quantiles import check_levels

DEFAULT_GBM = dict(max_iter=200, learning_rate=0.05, max_leaf_nodes=15,
                   min_samples_leaf=40, l2_regularization=1.0,
                   early_stopping=False, random_state=0)


def qcols(levels) -> list[str]:
    return [f"q{float(t):g}" for t in levels]


class GlobalQuantileGBM:
    """Global quantile GBM over many series.

    Input frame columns: location, date, value (>= 0); optional: pop (enables
    rates per 100k), source (several data sources pooled), and any columns
    named in `extra_features`.
    """

    def __init__(self, levels, horizons=(1, 2, 3, 4), power: float = 0.25,
                 eps: float = 0.01, n_lags: int = 4, taylor_windows=(4, 6),
                 extra_features=(), scale_q: float = 0.9, min_scale_points: int = 20,
                 gbm_params: dict | None = None, per_100k: bool = True):
        self.levels = check_levels(levels)
        self.horizons = tuple(int(h) for h in horizons)
        self.power, self.eps = float(power), float(eps)
        self.n_lags = int(n_lags)
        self.taylor_windows = tuple(int(w) for w in taylor_windows)
        self.extra_features = tuple(extra_features)
        self.scale_q = float(scale_q)
        self.min_scale_points = int(min_scale_points)
        self.gbm_params = dict(DEFAULT_GBM, **(gbm_params or {}))
        self.per_100k = per_100k
        self.models_: dict = {}
        self.scales_: dict = {}
        self.sources_: list = []
        self.feature_names_: list = []

    # ---------- preparation ----------
    def _series(self, df: pd.DataFrame):
        need = {"location", "date", "value"}
        missing = need - set(df.columns)
        if missing:
            raise ValueError(f"missing columns: {sorted(missing)}")
        d = df.copy()
        d["date"] = pd.to_datetime(d["date"])
        if "source" not in d.columns:
            d["source"] = "main"
        d["source"] = d["source"].astype(str)
        d["location"] = d["location"].astype(str)
        for (src, loc), g in d.groupby(["source", "location"], sort=True):
            g = g.sort_values("date").drop_duplicates("date", keep="last")
            grid = pd.date_range(g["date"].iloc[0], g["date"].iloc[-1], freq="7D")
            if not g["date"].isin(grid).all():
                raise ValueError(f"series {src}|{loc}: dates are not on a 7-day grid")
            g = g.set_index("date").reindex(grid)
            g.index.name = "date"
            yield src, loc, g

    def _transform(self, g: pd.DataFrame) -> np.ndarray:
        v = g["value"].to_numpy(dtype=float)
        if self.per_100k and "pop" in g.columns:
            pop = g["pop"].ffill().bfill().to_numpy(dtype=float)
            v = v / pop * 1e5
        return np.power(np.clip(v, 0.0, None) + self.eps, self.power)

    def _scale_from(self, z: np.ndarray) -> float | None:
        z = z[~np.isnan(z)]
        if z.size < self.min_scale_points:
            return None
        return float(max(np.quantile(z, self.scale_q), 1e-6))

    def _features(self, s: np.ndarray, dates: pd.DatetimeIndex, g: pd.DataFrame,
                  src_code: int) -> dict:
        n = s.size
        feats = {}
        for j in range(self.n_lags):
            lag = np.full(n, np.nan)
            lag[j:] = s[: n - j] if j else s
            feats[f"lag{j}"] = lag
        d1 = np.full(n, np.nan)
        d1[1:] = s[1:] - s[:-1]
        d2 = np.full(n, np.nan)
        d2[2:] = s[2:] - s[:-2]
        feats["d1"], feats["d2"] = d1, d2
        for w in self.taylor_windows:
            coef = np.full((n, 3), np.nan)
            if n >= w:
                x = np.arange(-(w - 1), 1, dtype=float)
                pinv = np.linalg.pinv(np.vstack([np.ones(w), x, x ** 2]).T)
                coef[w - 1:] = np.lib.stride_tricks.sliding_window_view(s, w) @ pinv.T
            feats[f"t{w}_level"], feats[f"t{w}_slope"], feats[f"t{w}_curv"] = coef.T
        doy = dates.dayofyear.to_numpy(dtype=float)
        feats["woy_sin"] = np.sin(2 * np.pi * doy / 365.25)
        feats["woy_cos"] = np.cos(2 * np.pi * doy / 365.25)
        feats["source"] = np.full(n, src_code, dtype=float)
        for c in self.extra_features:
            feats[c] = g[c].to_numpy(dtype=float) if c in g.columns else np.full(n, np.nan)
        return feats

    # ---------- fit / predict ----------
    def fit(self, df: pd.DataFrame) -> "GlobalQuantileGBM":
        blocks, targets = [], []
        series = list(self._series(df))
        self.sources_ = sorted({src for src, _, _ in series})
        for src, loc, g in series:
            z = self._transform(g)
            sc = self._scale_from(z)
            if sc is None:
                continue
            self.scales_[(src, loc)] = sc
            s = z / sc
            feats = self._features(s, g.index, g, self.sources_.index(src))
            for h in self.horizons:
                tgt = np.full(s.size, np.nan)
                tgt[: s.size - h] = s[h:] - s[: s.size - h]
                ok = ~np.isnan(tgt) & ~np.isnan(s)
                if not ok.any():
                    continue
                blk = pd.DataFrame({k: v[ok] for k, v in feats.items()})
                blk["horizon"] = float(h)
                blocks.append(blk)
                targets.append(tgt[ok])
        if not blocks:
            raise ValueError("no training rows: series too short or empty")
        X = pd.concat(blocks, ignore_index=True)
        y = np.concatenate(targets)
        self.feature_names_ = list(X.columns)
        cat = np.array([c == "source" for c in self.feature_names_])
        for tau in self.levels:
            m = HistGradientBoostingRegressor(loss="quantile", quantile=float(tau),
                                              categorical_features=cat if len(self.sources_) > 1 else None,
                                              **self.gbm_params)
            m.fit(X.to_numpy(dtype=float), y)
            self.models_[float(tau)] = m
        self.n_train_rows_ = int(len(y))
        return self

    def predict(self, df_hist: pd.DataFrame, reference_date, target_source: str | None = None) -> pd.DataFrame:
        """Quantile forecasts at `reference_date` for every series with data on it.

        Rows dated after reference_date are dropped first. Returns one row per
        (source, location, horizon) with quantile columns named by `qcols`.
        """
        if not self.models_:
            raise RuntimeError("fit() first")
        ref = pd.Timestamp(reference_date)
        d = df_hist[pd.to_datetime(df_hist["date"]) <= ref]
        rows, metas, bases = [], [], []
        for src, loc, g in self._series(d):
            if target_source is not None and src != target_source:
                continue
            if g.index[-1] != ref or np.isnan(g["value"].iloc[-1]):
                continue
            z = self._transform(g)
            sc = self.scales_.get((src, loc)) or self._scale_from(z)
            if sc is None:
                continue
            s = z / sc
            code = self.sources_.index(src) if src in self.sources_ else -1
            feats = self._features(s, g.index, g, code)
            last = {k: v[-1] for k, v in feats.items()}
            pop = float(g["pop"].ffill().iloc[-1]) if (self.per_100k and "pop" in g.columns) else None
            for h in self.horizons:
                rows.append(dict(last, horizon=float(h)))
                metas.append({"source": src, "location": loc, "reference_date": ref, "horizon": h,
                              "target_date": ref + pd.Timedelta(weeks=h)})
                bases.append((s[-1], sc, pop))
        cols = ["source", "location", "reference_date", "horizon", "target_date"] + qcols(self.levels)
        if not rows:
            return pd.DataFrame(columns=cols)
        X = pd.DataFrame(rows)[self.feature_names_].to_numpy(dtype=float)
        change = np.column_stack([self.models_[float(t)].predict(X) for t in self.levels])
        s_last = np.array([b[0] for b in bases])[:, None]
        scale = np.array([b[1] for b in bases])[:, None]
        s_hat = np.sort(s_last + change, axis=1)
        rate = np.clip(np.power(np.clip(s_hat * scale, 0.0, None), 1.0 / self.power) - self.eps, 0.0, None)
        pops = np.array([np.nan if b[2] is None else b[2] for b in bases])[:, None]
        value = np.where(np.isnan(pops), rate, rate * pops / 1e5)
        out = pd.concat([pd.DataFrame(metas), pd.DataFrame(value, columns=qcols(self.levels))], axis=1)
        return out[cols]
