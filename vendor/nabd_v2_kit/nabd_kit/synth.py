"""Synthetic data for testing the kit's MECHANICS.

Nothing computed on this data says anything about NABD or about real
influenza or RSV. Do not quote numbers from it in a pitch, deck or Q&A.

`make_world` draws asymmetric seasonal curves (faster rise, slower fall) per
location with shared season severity, plus negative-binomial noise.
`momentum_forecast` is a deliberately naive trend follower: it extrapolates
the last two weeks' log growth, which overshoots at peaks and invents trends in
noisy flat periods - a known defect for the recalibration code to work on.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from .quantiles import check_levels


def make_world(n_locations: int = 20, n_seasons: int = 8, weeks_per_season: int = 52,
               seed: int = 0, start: str = "2015-10-03") -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n_weeks = n_seasons * weeks_per_season
    dates = pd.date_range(start, periods=n_weeks, freq="7D")
    pops = np.exp(rng.normal(np.log(5e6), 0.8, n_locations))
    loc_int = np.exp(rng.normal(0.0, 0.3, n_locations))
    sev = np.exp(rng.normal(0.0, 0.4, n_seasons))
    peak = rng.normal(17.0, 2.5, n_seasons)
    rows = []
    w = np.arange(weeks_per_season, dtype=float)
    for li in range(n_locations):
        shift = rng.normal(0.0, 1.5)
        for s in range(n_seasons):
            mu = peak[s] + shift + rng.normal(0.0, 0.7)
            sd_rise, sd_fall = rng.uniform(2.5, 4.0), rng.uniform(3.5, 6.0)
            sd = np.where(w < mu, sd_rise, sd_fall)
            rate = 0.3 + 6.0 * sev[s] * loc_int[li] * np.exp(-0.5 * ((w - mu) / sd) ** 2)
            lam = rate * pops[li] / 1e5
            k = 50.0
            obs = rng.poisson(rng.gamma(k, lam / k))
            for i in range(weeks_per_season):
                rows.append((f"L{li:02d}", dates[s * weeks_per_season + i], float(obs[i]),
                             float(pops[li]), s, i))
    return pd.DataFrame(rows, columns=["location", "date", "value", "pop", "season", "week_in_season"])


def momentum_forecast(history, levels, horizons=(1, 2, 3, 4), base_sd: float = 0.15) -> np.ndarray:
    """Naive trend follower on log(y + 1). Returns (len(horizons), L)."""
    lv = check_levels(levels)
    ly = np.log(np.asarray(history, dtype=float) + 1.0)
    g = float(np.mean(np.diff(ly[-3:]))) if ly.size >= 3 else 0.0
    z = stats.norm.ppf(lv)
    out = np.empty((len(horizons), lv.size))
    for i, h in enumerate(horizons):
        sd = base_sd * np.sqrt(h) + 0.05 * h
        out[i] = np.clip(np.exp(ly[-1] + g * h + z * sd) - 1.0, 0.0, None)
    return out
