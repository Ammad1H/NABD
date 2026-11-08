"""Shadow-pilot scorer (SPEC §5.6): how NABD would be judged on a partner hospital's own counts.

Pre-specified exit criteria (docs/SPEC.md §5.6, docs/PILOT-DATA-SPEC.md §6):
  * primary: relative WIS of 1–3-week-ahead weekly admission forecasts vs persistence of the
    hospital's OWN census, ratio of sums over all scored weeks, must be < 0.9;
  * calibration: empirical coverage of the 80% central interval within [0.70, 0.90].

This module is method code. `demo()` runs it on the SYNTHETIC example only, to show the
mechanics; its numbers are NOT evidence about NABD and must never be quoted.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from uae.models import QUANTILES
from uae.scoring import wis

Q = np.array(QUANTILES)
I80 = (QUANTILES.index(0.1), QUANTILES.index(0.9))
EXIT_REL_WIS = 0.9
EXIT_COV80 = (0.70, 0.90)


def persistence_quantiles(y: np.ndarray, t: int, h: int, window: int = 8) -> np.ndarray | None:
    """Own-census persistence: last value + empirical h-step changes from the trailing window."""
    if t - window - h < 0 or np.isnan(y[t]):
        return None
    past = y[: t + 1]
    deltas = (past[h:] - past[:-h])[-window:]
    deltas = deltas[~np.isnan(deltas)]
    if len(deltas) < 4:
        return None
    return np.maximum(0, y[t] + np.quantile(deltas - np.median(deltas), Q))


def loglinear_quantiles(y: np.ndarray, t: int, h: int, window: int = 4, damp: float = 0.7) -> np.ndarray | None:
    """A simple damped log-linear trend with empirical log-error quantiles: a stand-in forecaster
    for the mechanics demo (the pilot would plug in NABD's frozen model here)."""
    if t < window + 8 or np.isnan(y[t - window + 1: t + 1]).any():
        return None
    ly = np.log1p(y[: t + 1])
    slope = np.polyfit(np.arange(window), ly[-window:], 1)[0]
    steps = sum(damp ** k for k in range(1, h + 1))
    med = ly[-1] + slope * steps
    errs = []
    for s in range(window + h, t - h + 1):
        sl = np.polyfit(np.arange(window), ly[s - window + 1: s + 1], 1)[0]
        errs.append(ly[s + h] - (ly[s] + sl * steps))
    if len(errs) < 4:
        return None
    return np.maximum(0, np.expm1(med + np.quantile(errs, Q)))


def shadow_score(weekly: pd.DataFrame, forecaster=loglinear_quantiles, horizons=(1, 2, 3),
                 start: int = 12) -> dict:
    """weekly: DataFrame(week_end, count). Returns the pre-specified pilot metrics and the exit verdict."""
    y = weekly["count"].to_numpy(float)
    rows = []
    for t in range(start, len(y)):
        for h in horizons:
            if t + h >= len(y) or np.isnan(y[t + h]):
                continue
            qf, qp = forecaster(y, t, h), persistence_quantiles(y, t, h)
            if qf is None or qp is None:
                continue
            obs = y[t + h]
            rows.append(dict(t=t, h=h, wis_f=wis(Q, qf, obs), wis_p=wis(Q, qp, obs),
                             in80=bool(qf[I80[0]] <= obs <= qf[I80[1]])))
    r = pd.DataFrame(rows)
    if r.empty:
        return {"n": 0, "verdict": "NOT COMPUTABLE"}
    rel = float(r.wis_f.sum() / r.wis_p.sum())
    cov = float(r.in80.mean())
    met = rel < EXIT_REL_WIS and EXIT_COV80[0] <= cov <= EXIT_COV80[1]
    return {"n": int(len(r)), "rel_wis_vs_own_census": round(rel, 3), "coverage80": round(cov, 3),
            "exit_rule": f"rel WIS < {EXIT_REL_WIS} and 80% coverage in {EXIT_COV80}",
            "verdict": "EXIT CRITERIA MET" if met else "EXIT CRITERIA NOT MET"}


def demo():
    """Mechanics only, on the SYNTHETIC example. Not evidence."""
    from adapters.pilot import load_pilot, make_synthetic, to_series
    df = load_pilot(make_synthetic())
    s = to_series(df, "admissions_rsv")
    out = shadow_score(s)
    out["data"] = "SYNTHETIC (adapters.pilot.make_synthetic); mechanics demo only, not evidence"
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
