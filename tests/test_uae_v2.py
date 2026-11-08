"""Tests for UAE v2, explanations, calendar features, and the GCC / v2 locks."""
import copy
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vendor" / "nabd_v2_kit"))

from nabd_kit.prereg import GoalpostError, assert_locked  # noqa: E402

from adapters import flunet  # noqa: E402
from uae.features_v2 import prepare_v2, ramadan_weekly, school_break_weekly  # noqa: E402
from uae.models import QUANTILES  # noqa: E402
from uae.models_v2 import NabdUAEv2  # noqa: E402


@pytest.fixture(scope="module")
def raw():
    return flunet.load("cached")


@pytest.fixture(scope="module")
def d_rsv(raw):
    return prepare_v2(raw, "rsv")


def test_explain_contributions_sum_to_median_logit(d_rsv):
    m = NabdUAEv2(d_rsv, [2022, 2023, 2025, 2026])
    idx = list(d_rsv.index[d_rsv.season == 2024][5:40:7])
    checked = 0
    for i in idx:
        for h, v in m.predict_detail(i).items():
            if v is None:
                continue
            med = v["q"][QUANTILES.index(0.5)]
            assert abs(v["explain"].contribution.sum() - med) < 1e-9
            # linear predictor = last observed + intercept + sum beta*x (excluding the residual offset)
            ex = v["explain"]
            lin = ex[ex.feature != "residual_median_offset"].contribution.sum()
            off = ex[ex.feature == "residual_median_offset"].contribution.iloc[0]
            assert abs(lin + off - med) < 1e-9
            checked += 1
    assert checked > 0


def test_v2_forecast_unchanged_when_future_surveillance_altered(d_rsv):
    m = NabdUAEv2(d_rsv, [2022, 2023, 2025, 2026])
    i = int(d_rsv.index[d_rsv.season == 2024][25])
    base = m.predict(i)
    d2 = d_rsv.copy()
    rng = np.random.default_rng(1)
    for c in ["y", "z", "logspec"]:
        d2.loc[d2.index > i, c] = rng.normal(size=(d2.index > i).sum())
    m.d = d2  # same fitted coefficients; only the data visible at prediction time change
    alt = m.predict(i)
    for h in base:
        if base[h] is not None:
            assert np.allclose(base[h], alt[h])


def test_v2_detects_injected_leak(d_rsv):
    """Sanity check of the test above: altering data AT the origin must change the forecast."""
    m = NabdUAEv2(d_rsv, [2022, 2023, 2025, 2026])
    i = int(d_rsv.index[d_rsv.season == 2024][25])
    base = m.predict(i)
    d2 = d_rsv.copy()
    d2.loc[i, "y"] = d2.loc[i, "y"] + 1.0
    m.d = d2
    alt = m.predict(i)
    assert any(base[h] is not None and not np.allclose(base[h], alt[h]) for h in base)


def test_calendar_features_are_known_future_only(raw):
    d = prepare_v2(raw, "flu", extend_weeks=4)
    # future weeks (no surveillance data) still have calendar features, computed from dates alone
    fut = d.tail(4)
    assert fut.y.isna().all()
    assert fut.school_break.notna().all() and fut.ramadan.notna().all()
    # features depend only on the dates: recomputing from the date column alone reproduces them
    assert np.allclose(school_break_weekly(d.week_end).values, d.school_break.values, equal_nan=True)
    assert np.allclose(ramadan_weekly(d.week_end).values, d.ramadan.values)


def test_unverified_calendar_period_is_missing_not_zero():
    import pandas as pd
    w = pd.Series(pd.to_datetime(["2019-12-22", "2026-12-20"]))
    sb = school_break_weekly(w)
    assert np.isnan(sb.iloc[0]) and sb.iloc[1] == 1.0


def test_gcc_scorer_refuses_without_valid_lock(monkeypatch):
    import uae.gcc as g
    assert assert_locked(g.LOCK, g.PLAN, g.CODE, g.CONFIG, None)  # current state verifies
    bad = copy.deepcopy(g.CONFIG)
    bad["countries"] = bad["countries"] + ["IRN"]
    with pytest.raises(GoalpostError):
        assert_locked(g.LOCK, g.PLAN, g.CODE, bad, None)
    monkeypatch.setattr(g, "CONFIG", bad)
    monkeypatch.setattr(sys, "argv", ["gcc", "--score"])
    with pytest.raises(GoalpostError):
        g.main()


def test_v2_backtest_refuses_without_valid_lock(monkeypatch):
    import uae.backtest_v2 as b
    assert b.check_lock()
    bad = copy.deepcopy(b.CONFIG)
    bad["alert_T"] = {"flu": 10.0, "rsv": 10.0}
    monkeypatch.setattr(b, "CONFIG", bad)
    with pytest.raises(GoalpostError):
        b.check_lock()
