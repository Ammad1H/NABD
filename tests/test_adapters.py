"""Adapter and UAE-track integrity tests (gate G6, adapter part)."""
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from adapters import flunet, weather, calendar
from adapters.schemas import reject_person_level, PersonLevelFieldError, FLUNET_WEEKLY
from uae.models import NabdUAE, Persistence, Analog, prepare, H

ROOT = Path(__file__).resolve().parents[1]


# --- privacy guard -------------------------------------------------------------------------------
@pytest.mark.parametrize("col", ["patient_id", "Name", "emirates_id", "DOB", "mrn", "employee id", "email", "PatientID"])
def test_person_level_columns_rejected(col):
    df = pd.DataFrame({"week_end": ["2026-11-01"], col: ["x"]})
    with pytest.raises(PersonLevelFieldError):
        reject_person_level(df, "test")


def test_aggregate_columns_allowed():
    df = pd.DataFrame({"week_end": [1], "specimens": [10], "flu_pos": [2], "location_id": ["ARE"]})
    assert reject_person_level(df, "test") is df


def test_flunet_adapter_rejects_person_level_raw():
    raw = pd.read_csv(ROOT / "data/raw/flunet_are.csv").head(5)
    raw["patient_name"] = "x"
    with pytest.raises(PersonLevelFieldError):
        flunet._tidy(raw)


# --- schemas -------------------------------------------------------------------------------------
def test_flunet_cached_validates_and_is_current():
    d = flunet.load("cached")
    FLUNET_WEEKLY.validate(d)
    s = d[d.origin == "SENTINEL"]
    assert s.week_end.max() >= pd.Timestamp("2026-11-01")
    assert (s.flu_pos.fillna(0) <= s.specimens).all()


def test_flunet_schema_rejects_impossible_counts():
    raw = pd.read_csv(ROOT / "data/raw/flunet_are.csv").head(3).copy()
    raw.loc[raw.index[0], "INF_ALL"] = raw.loc[raw.index[0], "SPEC_PROCESSED_NB"] + 10
    with pytest.raises(Exception):
        flunet._tidy(raw)


def test_weather_placeholder_is_labelled_not_real():
    w = weather.load("cached")
    if not (ROOT / "data/raw/weather_ad_weekly.csv").exists():
        assert not w.real.any()


def test_calendar_verified_rows_have_sources():
    c = calendar.load()
    assert c[c.verified].source.str.startswith("http").all()


# --- information rule: no future data in UAE forecasts -------------------------------------------
@pytest.fixture(scope="module")
def series():
    return flunet.sentinel_series(flunet.load("cached"))


@pytest.mark.parametrize("Model", [NabdUAE, Persistence, Analog])
@pytest.mark.parametrize("key", ["flu", "rsv"])
def test_forecast_unchanged_when_future_data_altered(series, Model, key):
    """A forecast issued at week i must not change if any value AFTER week i is changed."""
    d = prepare(series, key)
    train = [2022, 2023, 2024, 2026]   # test season 2025 held out
    i = int(d.index[(d.season == 2025) & (d.iso_week == 45)][0])
    m1 = Model(d, train)
    p1 = m1.predict(i)
    d2 = d.copy()
    # corrupt everything after the issue week in the TEST season (the training seasons are fixed inputs)
    after = (d2.index > i) & (d2.season == 2025)
    d2.loc[after, ["y", "pos", "logspec", "specimens"]] = d2.loc[after, ["y", "pos", "logspec", "specimens"]] * 3 + 7
    m2 = Model(d2, train)
    p2 = m2.predict(i)
    for h in H:
        if p1[h] is None:
            assert p2[h] is None
        else:
            np.testing.assert_allclose(p1[h], p2[h], rtol=0, atol=1e-12)


def test_leakage_detector_fires_on_injected_leak(series):
    """Sanity check of the test itself: a model that peeks at y[i+h] must be caught."""
    d = prepare(series, "rsv")
    i = int(d.index[(d.season == 2025) & (d.iso_week == 45)][0])

    class Leaky(Persistence):
        def predict(self, i):
            return {h: np.full(23, self.d.y.iloc[i + h]) for h in H}

    p1 = Leaky(d, [2022]).predict(i)
    d2 = d.copy()
    d2.loc[d2.index > i, "y"] += 1.0
    p2 = Leaky(d2, [2022]).predict(i)
    assert any(not np.allclose(p1[h], p2[h]) for h in H)


def test_test_season_excluded_from_training_climatology(series):
    d = prepare(series, "flu")
    m = NabdUAE(d, [2022, 2023, 2024])
    d2 = d.copy()
    d2.loc[d2.season == 2025, "y"] += 5
    m2 = NabdUAE(d2, [2022, 2023, 2024])
    np.testing.assert_allclose(m.clim.values, m2.clim.values)


# --- ledger integrity ----------------------------------------------------------------------------
def test_ledger_hashes_match():
    files = [p for p in (ROOT / "ledger").glob("*.csv") if p.name != "scores.csv"]
    assert files, "no ledger round issued"
    for p in files:
        sha = p.with_suffix(".sha256").read_text().split()[0]
        assert sha == hashlib.sha256(p.read_bytes()).hexdigest()
