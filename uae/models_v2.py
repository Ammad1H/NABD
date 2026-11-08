"""NABD-UAE-v2: multi-signal linear growth model on the logit of sentinel positivity.

Specification (frozen in docs/PROTOCOL-UAE-v2.md):

  y[t+h] - y[t] = b0 + b1*dy1 + b2*anom + b3*dclim + b4*dlogspec            (v1 core; TV + CLIM blocks)
                       + b5*ns_dy1 + b6*ns_gap                                (NS block, non-sentinel stream)
                       + b7*school_win + b8*ram_win                           (CAL block, known-future)

  dy1      = y[t] - y[t-1]                        (momentum; same season only)
  anom     = y[t] - clim[week t]                  (deviation from the seasonal baseline)
  dclim    = clim[week t+h] - clim[week t]        (expected seasonal drift to the target week)
  dlogspec = logspec[t] - logspec[t-1]            (testing-volume change; same season only)
  ns_dy1   = z[t-1] - z[t-2]                      (non-sentinel momentum, lagged one extra week)
  ns_gap   = z[t-1] - y[t-1]                      (non-sentinel minus sentinel level, same week)
  school_win = mean school-break fraction over target weeks t+1..t+h   (known-future)
  ram_win    = mean Ramadan fraction over target weeks t+1..t+h        (known-future)

Fitted by ordinary least squares per (series, horizon h in 1..4) on training seasons, exactly as v1.
Missing-feed behaviour: when NS features are not available at the origin (non-sentinel stream absent
or late), the model falls back to the nested sub-model without the NS block, fitted on all training rows.
When the calendar is unknown for a target week (outside verified calendars), CAL falls back likewise.
Predictive quantiles: median = y[t] + x.b + quantile(residuals), residuals from nested leave-one-season-
out within the training seasons for the sub-model actually used (out-of-sample spread), as in v1.

Because the model is linear, the median logit decomposes EXACTLY into
  last observed y[t] + intercept + sum_k b_k * x_k + median residual offset,
which is what results/uae/explain/ reports (G11).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from uae.models import H, QUANTILES, climatology

BLOCKS = {
    "CORE": ["dy1"],
    "CLIM": ["anom", "dclim"],
    "TV": ["dlogspec"],
    "NS": ["ns_dy1", "ns_gap"],
    "CAL": ["school_win", "ram_win"],
}
FULL = ("CORE", "CLIM", "TV", "NS", "CAL")


def features_v2(d: pd.DataFrame, clim: pd.Series, h: int) -> pd.DataFrame:
    y, z = d.y, d.z
    same1 = d.season == d.season.shift(1)
    same2 = same1 & (d.season == d.season.shift(2))
    cw = d.iso_week.map(clim)
    tw = d.iso_week.shift(-h).map(clim)
    sb = d.school_break
    rm = d.ramadan
    school_win = sum(sb.shift(-k) for k in range(1, h + 1)) / h
    ram_win = sum(rm.shift(-k) for k in range(1, h + 1)) / h
    return pd.DataFrame({
        "dy1": (y - y.shift(1)).where(same1),
        "anom": y - cw,
        "dclim": tw - cw,
        "dlogspec": (d.logspec - d.logspec.shift(1)).where(same1),
        "ns_dy1": (z.shift(1) - z.shift(2)).where(same2),
        "ns_gap": (z.shift(1) - y.shift(1)).where(same1),
        "school_win": school_win,
        "ram_win": ram_win,
        "target": y.shift(-h) - y,
        "season": d.season,
        "tseason": d.season.shift(-h),
    })


def cols_for(blocks) -> list[str]:
    return [c for b in FULL if b in blocks for c in BLOCKS[b]]


def _fit(F: pd.DataFrame, cols):
    G = F.dropna(subset=cols + ["target"])
    G = G[G.season == G.tseason]
    X = np.c_[np.ones(len(G)), G[cols].values]
    beta, *_ = np.linalg.lstsq(X, G.target.values, rcond=None)
    return beta, len(G)


class NabdUAEv2:
    name = "NABD-UAE-v2"

    def __init__(self, d: pd.DataFrame, train_seasons, blocks=FULL, name=None):
        self.d = d
        self.train = list(train_seasons)
        self.blocks = tuple(blocks)
        if name:
            self.name = name
        self.clim = climatology(d, self.train)
        # candidate sub-models, richest first; each is used only if its inputs exist at the origin
        cands = [self.blocks]
        for drop in (("NS",), ("CAL",), ("NS", "CAL")):
            sub = tuple(b for b in self.blocks if b not in drop)
            if sub not in cands:
                cands.append(sub)
        self.cands = cands
        self.fits = {}  # (sub, h) -> dict(beta, cols, resid, n)
        for h in H:
            F = features_v2(d, self.clim, h)
            Ftr = F[F.season.isin(self.train)]
            for sub in cands:
                cols = cols_for(sub)
                beta, n = _fit(Ftr, cols)
                self.fits[(sub, h)] = dict(beta=beta, cols=cols, n=n, resid=self._nested_resid(cols, h))

    def _nested_resid(self, cols, h):
        res = []
        for s_out in self.train:
            inner = [s for s in self.train if s != s_out]
            if not inner:
                continue
            c_in = climatology(self.d, inner)
            Fin = features_v2(self.d, c_in, h)
            b, n = _fit(Fin[Fin.season.isin(inner)], cols)
            if n <= len(cols) + 1:
                continue
            G = Fin[(Fin.season == s_out) & (Fin.tseason == s_out)].dropna(subset=cols + ["target"])
            if len(G):
                X = np.c_[np.ones(len(G)), G[cols].values]
                res.extend(list(G.target.values - X @ b))
        return np.asarray(res)

    def _row(self, i: int, h: int, drop_ns: bool = False):
        """Features at origin i using rows <= i for surveillance data (information rule) and
        known-future calendar values for target weeks."""
        d = self.d.copy()
        d.loc[d.index > i, ["y", "z", "pos", "logspec", "ns_pos", "ns_spec"]] = np.nan
        if drop_ns:
            d["z"] = np.nan
        F = features_v2(d.iloc[: i + 1 + h], self.clim, h)
        return F.iloc[i]

    def predict_detail(self, i: int, drop_ns: bool = False):
        """{h: dict(q=quantiles(logit), sub=blocks used, explain=DataFrame)} or {h: None}."""
        out = {}
        y0 = self.d.y.iloc[i]
        for h in H:
            if np.isnan(y0):
                out[h] = None
                continue
            row = self._row(i, h, drop_ns=drop_ns)
            chosen = None
            for sub in self.cands:
                f = self.fits[(sub, h)]
                if len(f["resid"]) < 10 or f["n"] <= len(f["cols"]) + 1:
                    continue
                if not row[f["cols"]].isna().any():
                    chosen = (sub, f)
                    break
            if chosen is None:
                out[h] = None
                continue
            sub, f = chosen
            x = row[f["cols"]].values.astype(float)
            lin = float(f["beta"][0] + x @ f["beta"][1:])
            rq = np.quantile(f["resid"], QUANTILES)
            q = y0 + lin + rq
            med_off = float(rq[QUANTILES.index(0.5)])
            ex = [("last_observed_logit", y0, 1.0, y0), ("intercept", 1.0, f["beta"][0], f["beta"][0])]
            ex += [(c, float(v), float(b), float(v * b)) for c, v, b in zip(f["cols"], x, f["beta"][1:])]
            ex += [("residual_median_offset", 1.0, med_off, med_off)]
            exdf = pd.DataFrame(ex, columns=["feature", "value", "beta", "contribution"])
            out[h] = dict(q=q, sub="+".join(sub), explain=exdf)
        return out

    def predict(self, i: int):
        det = self.predict_detail(i)
        return {h: (None if v is None else v["q"]) for h, v in det.items()}
