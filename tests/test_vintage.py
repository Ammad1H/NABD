"""Leakage control (BUILD-SPEC G6, PROTOCOL §2)."""
import numpy as np
import pandas as pd
import pytest

from models import data
from models.engine import prepare

pytestmark = pytest.mark.skipif(not (data.HUB / "target-data" / "time-series.csv").exists(),
                                reason="needs the CDC hub clone (python -m eval.run_all --fetch)")


def test_vintage_rule_deadline():
    R = pd.Timestamp("2025-12-06")
    v = data.vintage_for(R)
    assert v <= R - pd.Timedelta(days=3)
    later = [x for x in data.vintages() if v < x <= R - pd.Timedelta(days=3)]
    assert not later


def test_no_data_after_cutoff():
    for R in ["2023-11-18", "2024-12-14", "2025-12-06"]:
        w, meta = data.series_as_of(R)
        assert w.columns.max() <= pd.Timestamp(R) - pd.Timedelta(days=7)


def test_injected_future_point_does_not_change_forecast(monkeypatch):
    """Inject an absurd value at R (a future week) into the raw series; inputs must be unchanged."""
    R = pd.Timestamp("2025-12-06")
    base = prepare(R)
    ts = data.time_series().copy()
    v = data.vintage_for(R)
    fut = pd.DataFrame({"as_of": [v] * 2, "target_end_date": [R, R - pd.Timedelta(days=3)],
                        "location": ["US", "06"], "observation": [1e9, 1e9]})
    poisoned = pd.concat([ts, fut], ignore_index=True)
    data._vintage_wide.cache_clear()
    monkeypatch.setattr(data, "time_series", lambda: poisoned)
    try:
        P2 = prepare(R)
        assert np.array_equal(base.Y, P2.Y), "future data leaked into model inputs"
    finally:
        data._vintage_wide.cache_clear()


def test_leak_detector_fires_when_cutoff_removed(monkeypatch):
    """Negative control: if the cutoff were R instead of R-7, the injected point WOULD enter."""
    R = pd.Timestamp("2025-12-06")
    ts = data.time_series().copy()
    v = data.vintage_for(R)
    fut = pd.DataFrame({"as_of": [v], "target_end_date": [R - pd.Timedelta(days=7) + pd.Timedelta(days=7)],
                        "location": ["US"], "observation": [1e9]})
    poisoned = pd.concat([ts, fut], ignore_index=True)
    data._vintage_wide.cache_clear()
    monkeypatch.setattr(data, "time_series", lambda: poisoned)
    try:
        w = data._vintage_wide(v)
        assert (w.loc["US"] >= 1e9).any()          # it is in the raw vintage...
        w2, _ = data.series_as_of(R)
        assert not (w2.loc["US"] >= 1e9).any()     # ...but the R-7 cutoff removes it
    finally:
        data._vintage_wide.cache_clear()
