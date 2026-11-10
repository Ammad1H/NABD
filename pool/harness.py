"""Forward-in-time evaluation harness shared by development selection and the confirmatory test."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "nabd_v2_kit"))
from nabd_kit.gbm_global import GlobalQuantileGBM  # noqa: E402
from nabd_kit.scoring import interval_hit, wis as kit_wis  # noqa: E402

from pool import config as C  # noqa: E402
from pool.features import feature_table, own_train_seasons  # noqa: E402
from pool.models import Q, PoolGBM, PoolLinear, ensemble_percent, to_percent  # noqa: E402
from uae.models import Analog, H, NabdUAE, Persistence, expit  # noqa: E402

KEYS = ["country", "season", "i", "h"]


def relaxed_q(x: pd.DataFrame) -> dict:
    """P1 relaxed training-row rule: >= 20 reported weeks and median specimens (reported weeks) >= 20."""
    q = {}
    for s, g in x.groupby("season"):
        rep = g[(g.specimens > 0) & g.y.notna()]
        q[int(s)] = bool(len(rep) >= 20 and rep.specimens.median() >= 20)
    return q


def train_table(D: dict, relaxed: bool) -> pd.DataFrame:
    """Pooled training rows from every country in D (the caller filters countries and seasons)."""
    parts = []
    for c, v in D.items():
        q = relaxed_q(v["x"]) if relaxed else v["q"]
        f = feature_table(v["x"], q, c)
        if len(f):
            parts.append(f)
    t = pd.concat(parts, ignore_index=True)
    return t[~t.season.isin(C.EXCLUDE_TRAINING_SEASONS)]


def scored_seasons(v: dict, truncate=None) -> list[int]:
    return [S for S in C.EVAL_SEASONS if v["q"].get(S, False)
            and len(own_train_seasons(v["q"], S)) >= C.MIN_TRAINING_SEASONS]


def eval_table(D: dict, truncate=None) -> pd.DataFrame:
    parts = []
    for c, v in D.items():
        ss = scored_seasons(v)
        if ss:
            f = feature_table(v["x"], v["q"], c, truncate=truncate, seasons=ss)
            parts.append(f[f.obs.notna()])
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def local_forecasts(D: dict, truncate=None):
    """Local v1, persistence and analog for every scored country-season.
    Returns (long frame of percent quantiles keyed by KEYS+model, {(country, season): fitted NabdUAE})."""
    rows, fitted = [], {}
    for c, v in D.items():
        x = v["x"]
        for S in scored_seasons(v):
            tr = own_train_seasons(v["q"], S, truncate)
            models = [NabdUAE(x, tr), Persistence(x, tr), Analog(x, tr)]
            fitted[(c, S)] = (models[0], len(tr))
            for i in x.index[x.season == S]:
                if np.isnan(x.y.iloc[i]):
                    continue
                for m in models:
                    pq = m.predict(i)
                    for h in H:
                        if pq.get(h) is None or i + h >= len(x) or x.season.iloc[i + h] != S:
                            continue
                        rows.append((c, S, i, h, m.name, 100 * expit(np.sort(pq[h]))))
    df = pd.DataFrame(rows, columns=KEYS + ["model", "qv"])
    return df, fitted


def pool_forecasts(spec: dict, train: pd.DataFrame, ev: pd.DataFrame, fitted: dict, D: dict) -> pd.DataFrame:
    """Fit the pooled model(s) in `spec` on `train` and forecast every row of `ev`.
    spec = dict(members=[...], gbm={...}, k=..., ...). Returns KEYS + model + qv (percent)."""
    members = {}
    if "G" in spec["members"]:
        g = PoolGBM(**spec.get("gbm", {})).fit(train)
        members["G"] = to_percent(g.predict_logit(ev))
    if "L" in spec["members"]:
        lm = PoolLinear(k=spec.get("k", 4.0)).fit(train)
        out = np.full((len(ev), len(Q)), np.nan)
        for (c, S), idx in ev.groupby(["country", "season"]).indices.items():
            loc, n = fitted.get((c, S), (None, 0))
            out[idx] = lm.predict_logit(ev.iloc[idx], loc, n)
        members["L"] = to_percent(out)
    if "K" in spec["members"]:
        members["K"] = kit_member(spec, train, ev, D)
    arr = ensemble_percent([members[m] for m in spec["members"]]) if len(members) > 1 else \
        members[spec["members"][0]]
    res = ev[KEYS].copy()
    res["model"] = "NABD-Pool"
    res["qv"] = list(arr)
    extra = []
    if spec.get("keep_members"):
        for k, a in members.items():
            r = ev[KEYS].copy()
            r["model"] = f"member-{k}"
            r["qv"] = list(a)
            extra.append(r)
    return pd.concat([res] + extra, ignore_index=True)


def kit_member(spec, train, ev, D) -> np.ndarray:
    """Kit GlobalQuantileGBM on % positivity. Trained on the same country-seasons as `train`."""
    tr_keys = set(map(tuple, train[["country", "season"]].drop_duplicates().values))
    parts = []
    for (c, S) in tr_keys:
        x = D[c]["x"] if c in D else None
        if x is None:
            continue
        g = x[x.season == S]
        parts.append(pd.DataFrame({"location": f"{c}|{S}", "date": g.week_end,
                                   "value": g.pos / g.specimens.where(g.specimens > 0) * 100}))
    m = GlobalQuantileGBM(Q, horizons=H, per_100k=False, min_scale_points=10,
                          gbm_params=spec.get("kit_gbm", {})).fit(pd.concat(parts, ignore_index=True))
    out = np.full((len(ev), len(Q)), np.nan)
    pos = {k: j for j, k in enumerate(map(tuple, ev[KEYS].values))}
    for (c, S), g in ev.groupby(["country", "season"]):
        x = D[c]["x"]
        s = x[x.season == S]
        hist = pd.DataFrame({"location": f"{c}|{S}", "date": s.week_end,
                             "value": s.pos / s.specimens.where(s.specimens > 0) * 100})
        for i in sorted(g.i.unique()):
            p = m.predict(hist, x.week_end.iloc[i])
            for _, r in p.iterrows():
                j = pos.get((c, S, i, int(r.horizon)))
                if j is not None:
                    out[j] = r.iloc[5:].to_numpy(float)
    return out


def score(fc: pd.DataFrame, ev: pd.DataFrame) -> pd.DataFrame:
    """WIS and coverage per forecast, on cells common to all models present."""
    m = fc.merge(ev[KEYS + ["obs", "origin", "n_own"]], on=KEYS)
    qv = np.vstack(m.qv.values)
    ok = ~np.isnan(qv).any(axis=1)
    m, qv = m[ok].copy(), qv[ok]
    m["wis"] = kit_wis(qv, m.obs.values, Q)
    m["cov50"] = interval_hit(qv, m.obs.values, Q, 0.5)
    m["cov95"] = interval_hit(qv, m.obs.values, Q, 0.95)
    m["median"] = qv[:, 11]
    n = m.groupby(KEYS).model.nunique()
    keep = n[n == m.model.nunique()].index
    m = m.set_index(KEYS).loc[keep].reset_index()
    return m.drop(columns=["qv"]), fc


def rel(sc: pd.DataFrame, a: str, b: str, B=None, seed=None, unit="country"):
    """Ratio of summed WIS a/b with a cluster bootstrap over `unit`."""
    B = B or C.BOOTSTRAP["B"]
    seed = C.BOOTSTRAP["seed"] if seed is None else seed
    A = sc[sc.model == a].groupby(unit).wis.sum()
    Bv = sc[sc.model == b].groupby(unit).wis.sum().reindex(A.index)
    if len(A) == 0:
        return None
    r = A.sum() / Bv.sum()
    rng = np.random.default_rng(seed)
    a_, b_ = A.values, Bv.values
    bs = [a_[k].sum() / b_[k].sum() for k in (rng.integers(0, len(a_), len(a_)) for _ in range(B))]
    return dict(rel_wis=round(float(r), 4), ci95=[round(float(np.quantile(bs, .025)), 4),
                                                  round(float(np.quantile(bs, .975)), 4)],
                n_units=int(len(A)), n_cells=int((sc.model == a).sum()),
                mean_log_ratio=round(float(np.exp(np.mean(np.log(a_ / b_)))), 4),
                unit_wins=f"{int((a_ < b_).sum())}/{len(a_)}")
