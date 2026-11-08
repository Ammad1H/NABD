"""UAE positivity forecasters.

All models work on the logit of sentinel positivity with a continuity correction
p = (positives + 0.5) / (specimens + 1), and output FluSight-style quantiles in PERCENT.

Information rule (simulated publication lag): a forecast issued for last-published week L uses ONLY
rows with week_end <= week_end(L). Targets are L+1..L+4 (data horizons h=1..4). With WHO's ~7-11 day lag,
L+1 has already ended at issue (nowcast); L+2..L+4 end about +0.5, +1.5, +2.5 weeks after issue.

Models
- persistence:   median = last observed logit; spread = empirical h-step logit changes in training seasons.
- analog:        seasonal climatology: training-season values at the target ISO week (+/-1 week).
- nabd_uae:      pooled linear growth model per horizon h, fitted on training seasons:
                   y[t+h]-y[t] = a + b*(y[t]-y[t-1]) + c*(y[t]-clim[t]) + d*(clim[t+h]-clim[t]) + e*dlogspec[t]
                 where clim is the training-season mean logit by ISO week (circularly smoothed) and dlogspec is the
                 1-week change in log specimens processed (testing-volume covariate). Predictive quantiles come from
                 residuals obtained by NESTED leave-one-season-out within the training seasons (out-of-sample spread).
"""
import numpy as np
import pandas as pd

QUANTILES = [0.01, 0.025, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5,
             0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.975, 0.99]
H = (1, 2, 3, 4)
SERIES = {"flu": ("flu_pos", "wk flu pos pct sentinel"), "rsv": ("rsv_pos", "wk rsv pos pct sentinel")}


def logit(p):
    return np.log(p / (1 - p))


def expit(x):
    return 1 / (1 + np.exp(-x))


def prepare(s: pd.DataFrame, key: str) -> pd.DataFrame:
    """s = adapters.flunet.sentinel_series(...). Returns frame with y (logit) and helpers."""
    pos = s[SERIES[key][0]]
    d = s[["week_end", "iso_year", "iso_week", "season", "specimens"]].copy()
    d["pos"] = pos
    d["y"] = logit((pos + 0.5) / (s.specimens + 1.0))
    d.loc[pos.isna() | s.specimens.isna(), "y"] = np.nan
    d["logspec"] = np.log(s.specimens.clip(lower=1))
    return d.reset_index(drop=True)


def climatology(d: pd.DataFrame, train_seasons) -> pd.Series:
    """Mean logit by ISO week (1..53) over training seasons, circularly smoothed (+/-2 weeks)."""
    t = d[d.season.isin(train_seasons)].dropna(subset=["y"])
    m = t.groupby("iso_week").y.mean().reindex(range(1, 54))
    m.loc[53] = m.loc[53] if not np.isnan(m.loc[53]) else m.loc[52]
    arr = np.r_[m.values[-2:], m.values, m.values[:2]]
    arr = pd.Series(arr).interpolate(limit_direction="both").values
    sm = np.convolve(arr, np.ones(5) / 5, mode="valid")
    return pd.Series(sm, index=range(1, 54))


def _features(d: pd.DataFrame, clim: pd.Series, h: int) -> pd.DataFrame:
    y = d.y
    cw = d.iso_week.map(clim)
    tw = d.iso_week.shift(-h).map(clim)
    f = pd.DataFrame({
        "dy1": y - y.shift(1),
        "anom": y - cw,
        "dclim": tw - cw,
        "dlogspec": d.logspec - d.logspec.shift(1),
        "target": y.shift(-h) - y,
        "season": d.season,
        "tseason": d.season.shift(-h),
    })
    return f


def _fit(F: pd.DataFrame):
    F = F.dropna()
    F = F[F.season == F.tseason]
    X = np.c_[np.ones(len(F)), F[["dy1", "anom", "dclim", "dlogspec"]].values]
    beta, *_ = np.linalg.lstsq(X, F.target.values, rcond=None)
    return beta


def _pred(beta, row) -> float:
    x = np.r_[1.0, row[["dy1", "anom", "dclim", "dlogspec"]].values.astype(float)]
    return float(x @ beta)


class NabdUAE:
    name = "NABD-UAE-v1"

    def __init__(self, d: pd.DataFrame, train_seasons):
        self.d = d
        self.train = list(train_seasons)
        self.clim = climatology(d, self.train)
        self.beta, self.resid = {}, {}
        for h in H:
            F = _features(d, self.clim, h)
            self.beta[h] = _fit(F[F.season.isin(self.train)])
            # nested LOSO residuals within training seasons
            res = []
            for s_out in self.train:
                inner = [s for s in self.train if s != s_out]
                if not inner:
                    continue
                c_in = climatology(d, inner)
                Fin = _features(d, c_in, h)
                b = _fit(Fin[Fin.season.isin(inner)])
                G = Fin[(Fin.season == s_out) & (Fin.tseason == s_out)].dropna()
                if len(G):
                    X = np.c_[np.ones(len(G)), G[["dy1", "anom", "dclim", "dlogspec"]].values]
                    res.extend(list(G.target.values - X @ b))
            self.resid[h] = np.asarray(res)

    def predict(self, i: int):
        """Quantiles (logit) for targets i+h, using rows <= i only. Returns {h: array(len(QUANTILES))}."""
        out = {}
        d = self.d.iloc[: i + 1]  # information rule
        for h in H:
            F = _features(pd.concat([d, self.d.iloc[i + 1:i + 1 + h][["week_end", "iso_year", "iso_week", "season"]]],
                                    ignore_index=True), self.clim, h)
            row = F.iloc[i]
            if row[["dy1", "anom", "dclim", "dlogspec"]].isna().any():
                out[h] = None
                continue
            mu = d.y.iloc[i] + _pred(self.beta[h], row)
            out[h] = mu + np.quantile(self.resid[h], QUANTILES)
        return out


class Persistence:
    name = "persistence"

    def __init__(self, d, train_seasons):
        self.d = d
        self.deltas = {}
        t = d[d.season.isin(train_seasons)]
        for h in H:
            dl = (t.y.shift(-h) - t.y)[t.season.shift(-h) == t.season].dropna()
            self.deltas[h] = dl.values

    def predict(self, i):
        y0 = self.d.y.iloc[i]
        if np.isnan(y0):
            return {h: None for h in H}
        return {h: y0 + np.quantile(self.deltas[h], QUANTILES) - np.median(self.deltas[h]) for h in H}


class Analog:
    name = "seasonal-analog"

    def __init__(self, d, train_seasons):
        self.d = d
        self.t = d[d.season.isin(train_seasons)].dropna(subset=["y"])

    def predict(self, i):
        out = {}
        for h in H:
            j = i + h
            if j >= len(self.d):
                out[h] = None
                continue
            w = int(self.d.iso_week.iloc[j])
            diff = (self.t.iso_week - w + 26) % 52 - 26
            vals = self.t.y[diff.abs() <= 1].values
            out[h] = np.quantile(vals, QUANTILES) if len(vals) >= 3 else None
        return out


MODELS = [NabdUAE, Persistence, Analog]
