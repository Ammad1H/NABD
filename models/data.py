"""Data access for the US-A track: vintage-correct series from the CDC FluSight hub.

The vintage rule (PROTOCOL §2) lives in `vintage_for` and `series_as_of`. Nothing here
reads final truth for model inputs; truth is accessed only via `final_truth`/`first_release_truth`,
which are used by the scoring code.
"""
from __future__ import annotations

import functools
import os
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
HUB = Path(os.environ.get("NABD_HUB", ROOT / "external" / "hub"))
TARGET = "wk inc flu hosp"
QUANTILES = np.array([0.01, 0.025, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5,
                      0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.975, 0.99])
HORIZONS = [0, 1, 2, 3]


@functools.lru_cache(maxsize=1)
def time_series() -> pd.DataFrame:
    t = pd.read_csv(HUB / "target-data" / "time-series.csv", dtype={"location": str},
                    usecols=["as_of", "target", "target_end_date", "location", "observation"])
    t = t[t.target == TARGET].drop(columns="target")
    # vintage 2026-05-27 contains exact duplicate rows (identical values); drop them
    t = t.drop_duplicates(["as_of", "location", "target_end_date"], keep="last")
    t["as_of"] = pd.to_datetime(t["as_of"])
    t["target_end_date"] = pd.to_datetime(t["target_end_date"])
    return t


@functools.lru_cache(maxsize=1)
def vintages() -> list[pd.Timestamp]:
    return sorted(time_series().as_of.unique())


@functools.lru_cache(maxsize=1)
def locations() -> list[str]:
    locs = sorted(time_series().location.unique())
    # keep 'US' last for readability
    return [l for l in locs if l != "US"] + ["US"]


def vintage_for(reference_date) -> pd.Timestamp:
    """PROTOCOL §2: largest as_of <= R - 3 days."""
    R = pd.Timestamp(reference_date)
    cands = [v for v in vintages() if v <= R - pd.Timedelta(days=3)]
    if not cands:
        raise ValueError(f"no vintage available for reference date {R.date()}")
    return cands[-1]


@functools.lru_cache(maxsize=256)
def _vintage_wide(as_of: pd.Timestamp) -> pd.DataFrame:
    t = time_series()
    v = t[t.as_of == as_of].pivot(index="location", columns="target_end_date", values="observation")
    return v.reindex(locations())


def series_as_of(reference_date) -> tuple[pd.DataFrame, dict]:
    """Return the vintage-filtered wide matrix (locations x weeks, ending <= R-7) and metadata.

    Missing values (a few off-season 2024 cells) are linearly interpolated within each
    location and then forward/back-filled; this uses only data inside the same vintage.
    """
    R = pd.Timestamp(reference_date)
    v_date = vintage_for(R)
    w = _vintage_wide(v_date)
    cutoff = R - pd.Timedelta(days=7)
    w = w.loc[:, w.columns <= cutoff]
    # regular weekly grid
    full = pd.date_range(w.columns.min(), w.columns.max(), freq="7D")
    w = w.reindex(columns=full)
    w = w.T.interpolate(limit_direction="both").T.ffill(axis=1).bfill(axis=1).fillna(0.0)
    last = w.columns.max()
    meta = {
        "reference_date": R.date().isoformat(),
        "vintage_as_of": v_date.date().isoformat(),
        "last_week": last.date().isoformat(),
        "expected_last_week": cutoff.date().isoformat(),
        "stale_weeks": int((cutoff - last).days // 7),
    }
    return w.clip(lower=0), meta


@functools.lru_cache(maxsize=1)
def final_truth() -> pd.DataFrame:
    """PROTOCOL §5 primary truth: latest vintage value per (location, target_end_date)."""
    t = time_series()
    latest = t.as_of.max()
    f = t[t.as_of == latest][["location", "target_end_date", "observation"]].dropna()
    return f.rename(columns={"observation": "truth"})


@functools.lru_cache(maxsize=1)
def first_release_truth() -> pd.DataFrame:
    """PROTOCOL §5 sensitivity truth: value in the earliest vintage containing the cell."""
    t = time_series().dropna(subset=["observation"]).sort_values("as_of")
    f = t.groupby(["location", "target_end_date"], as_index=False).first()
    return f[["location", "target_end_date", "observation"]].rename(columns={"observation": "truth"})


def truth_as_of(as_of) -> pd.DataFrame:
    """Truth taken from a specific vintage (used for tuning truth, PROTOCOL §4)."""
    t = time_series()
    f = t[t.as_of == pd.Timestamp(as_of)][["location", "target_end_date", "observation"]].dropna()
    return f.rename(columns={"observation": "truth"})


def hub_reference_dates() -> list[pd.Timestamp]:
    d = sorted(f[:10] for f in os.listdir(HUB / "model-output" / "FluSight-ensemble") if f.endswith(".csv"))
    return [pd.Timestamp(x) for x in d]


def season_dates(season: str) -> list[pd.Timestamp]:
    windows = {
        "2023/24": ("2023-10-14", "2024-05-04"),
        "2024/25": ("2024-11-23", "2025-05-31"),
        "2025/26": ("2025-11-22", "2026-05-30"),
    }
    a, b = (pd.Timestamp(x) for x in windows[season])
    # every Saturday in the window (NABD forecasts every round; common-cell rule handles
    # rounds where a comparator is missing)
    return list(pd.date_range(a, b, freq="7D"))


def load_comparator(model: str, reference_date) -> pd.DataFrame | None:
    R = pd.Timestamp(reference_date)
    p = HUB / "model-output" / model / f"{R.date().isoformat()}-{model}.csv"
    if not p.exists():
        return None
    d = pd.read_csv(p, dtype={"location": str, "output_type_id": str})
    d = d[(d.target == TARGET) & (d.output_type == "quantile")]
    d = d[d.horizon.isin(HORIZONS)].copy()
    d["horizon"] = d.horizon.astype(int)
    d["q"] = d.output_type_id.astype(float)
    return d[["location", "horizon", "target_end_date", "q", "value"]]
