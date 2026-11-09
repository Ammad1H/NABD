"""G14: every weekly card must be consistent; a contradictory card must fail the check.

Also checks issue-relative horizon labels and that the app pages render in EN and AR without exceptions.
"""
import copy
import datetime as dt
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import cardcheck, data_io  # noqa: E402
from playbook.validate import load_playbook, validate_playbook, PlaybookError  # noqa: E402

LEVELS = cardcheck.FLUSIGHT_LEVELS
Z = np.array([-2.326, -1.960, -1.645, -1.282, -1.036, -0.842, -0.674, -0.524, -0.385, -0.253, -0.126, 0.0,
              0.126, 0.253, 0.385, 0.524, 0.674, 0.842, 1.036, 1.282, 1.645, 1.960, 2.326])
ISSUE = dt.date(2026, 11, 8)
TARGET = "wk rsv pos pct sentinel"


def _fc(medians, sd=1.0):
    rows = []
    for i, m in enumerate(medians):
        ted = ISSUE + dt.timedelta(weeks=i)  # first row = nowcast (ends on the issue date)
        for q, z in zip(LEVELS, Z):
            rows.append({"target_end_date": ted, "q": float(q), "value": max(0.0, m + sd * z)})
    return pd.DataFrame(rows)


def _obs(prev, last):
    return pd.Series([prev, last])


@pytest.fixture(scope="module")
def pb():
    return load_playbook()


def test_horizon_labels_issue_relative():
    assert data_io.horizon_label(ISSUE, ISSUE) == "nowcast"
    assert data_io.horizon_label(ISSUE + dt.timedelta(weeks=1), ISSUE) == "+1 wk after issue"
    assert data_io.horizon_label(ISSUE + dt.timedelta(weeks=3), ISSUE) == "+3 wk after issue"
    d = ISSUE + dt.timedelta(weeks=1)
    assert data_io.display_horizon(d, ISSUE).startswith(data_io.week_ending_label(d) + " (")


def test_falling_forecast_never_gets_rising_band(pb):
    res = cardcheck.build_card(pb, TARGET, "ARE", _fc([15, 13, 11, 9]), _obs(16, 15.6), ISSUE)
    assert res.trend == "falling"
    assert "rising" not in res.band["id"]
    assert res.problems == [] and res.renderable


def test_rising_forecast_gets_rising_band(pb):
    res = cardcheck.build_card(pb, TARGET, "ARE", _fc([13, 15, 17, 19]), _obs(11, 12), ISSUE)
    assert res.trend == "rising" and res.band["id"] == "rsv_elevated_rising"
    assert res.problems == [] and res.renderable


def test_contradictory_card_label_fails(pb):
    """A hand-edited card that claims 'likely_up' while the forecast falls must be caught."""
    fc = _fc([15, 12, 10, 8], sd=0.5)
    res = cardcheck.build_card(pb, TARGET, "ARE", fc, _obs(16, 15.6), ISSUE)
    assert res.problems == []
    bad = replace(res.kit, forecast_key="likely_up", action_key="watch_closely")
    res_bad = copy.copy(res)
    res_bad.kit = bad
    q = cardcheck._qvec(res.level_row)
    problems = cardcheck.card_problems(res_bad, q)
    assert problems, "a contradictory card must fail the consistency check"
    res_bad.problems = problems
    assert not res_bad.renderable


def test_rising_band_with_falling_path_fails(pb):
    """Pairing a 'rising' band with a falling forecast path is a contradiction."""
    fc = _fc([15, 12, 10, 8], sd=0.5)
    res = cardcheck.build_card(pb, TARGET, "ARE", fc, _obs(16, 15.6), ISSUE)
    rising = next(b for b in pb["bands"] if b["id"] == "rsv_elevated_rising")
    probs = cardcheck.band_consistency(rising, res.kit, res.path_medians, res.last_value, res.p_high)
    assert any("rising trend" in p for p in probs)


def test_surge_band_needs_exceedance(pb):
    fc = _fc([15, 12, 10, 8], sd=0.5)
    res = cardcheck.build_card(pb, TARGET, "ARE", fc, _obs(16, 15.6), ISSUE)
    surge = next(b for b in pb["bands"] if b["id"] == "rsv_high_rising")
    probs = cardcheck.band_consistency(surge, res.kit, [16, 18, 20], 15.6, p_high=0.05)
    assert any("tier-3" in p for p in probs)


def test_live_round_cards_are_consistent(pb):
    obs = data_io.load_uae_observed()
    fc, _, meta, _ = data_io.load_uae_forecasts(obs)
    issue = dt.date.fromisoformat(str(meta["issue_date"]))
    for col, target in data_io.UAE_TARGETS.items():
        res = cardcheck.build_card(pb, target, "ARE", fc[fc.target == target], obs[col], issue)
        assert res.problems == [], (col, res.problems)


def test_validator_rejects_rising_band_on_falling_trend(pb):
    bad = copy.deepcopy(pb)
    b = next(x for x in bad["bands"] if x["id"] == "rsv_elevated_rising")
    b["trend"] = ["rising", "falling"]
    with pytest.raises(PlaybookError):
        validate_playbook(bad)


@pytest.mark.parametrize("lang", ["en", "ar"])
def test_all_pages_render(lang):
    pytest.importorskip("streamlit.testing.v1")
    from streamlit.testing.v1 import AppTest
    pages = ["nav_card", "nav_shape", "nav_scenario", "nav_planner", "nav_gcc", "nav_ledger", "nav_us", "nav_alerts", "nav_ablation",
             "nav_workforce", "nav_about"]
    for p in pages:
        at = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=60)
        at.run()
        at.sidebar.radio[0].set_value(lang)
        at.sidebar.radio[1].set_value(p)
        at.run()
        assert not at.exception, (lang, p, [e.value for e in at.exception])


# ---------------------------------------------------------------- round 3: exceedance-driven bands (R3-1, G14)
def test_band_follows_exceedance_not_median(pb):
    """Median below 10% but a wide forecast with >=30% chance of crossing 10% -> elevated band, not low."""
    fc = _fc([9, 9.2, 9.4, 9.5], sd=3.0)
    res = cardcheck.build_card(pb, TARGET, "ARE", fc, _obs(9, 9.0), ISSUE)
    assert res.max_p[10.0] >= 0.30 and res.level == 10.0
    assert res.band["lower"] == 10 and res.problems == []


def test_narrow_low_forecast_stays_low(pb):
    fc = _fc([5, 5, 5, 5], sd=0.5)
    res = cardcheck.build_card(pb, TARGET, "ARE", fc, _obs(5, 5.0), ISSUE)
    assert res.level == 0.0 and res.band["id"] == "rsv_low" and res.problems == []


def test_overcall_band_fails(pb):
    """An elevated band when P(> 10%) is tiny is a contradiction."""
    fc = _fc([5, 5, 5, 5], sd=0.5)
    res = cardcheck.build_card(pb, TARGET, "ARE", fc, _obs(5, 5.0), ISSUE)
    elevated = next(b for b in pb["bands"] if b["id"] == "rsv_elevated_plateau")
    probs = cardcheck.band_consistency(elevated, res.kit, res.path_medians, res.last_value, res.p_high,
                                       res.max_p, res.p_act)
    assert any("chance of exceeding" in p for p in probs)


def test_undercall_band_fails(pb):
    """A low band when P(> 20%) >= 30% is an under-call."""
    fc = _fc([24, 25, 26, 27], sd=2.0)
    res = cardcheck.build_card(pb, TARGET, "ARE", fc, _obs(22, 23.0), ISSUE)
    assert res.level == 20.0 and res.band["tier"] == 3 and res.problems == []
    low = next(b for b in pb["bands"] if b["id"] == "rsv_low")
    probs = cardcheck.band_consistency(low, res.kit, res.path_medians, res.last_value, res.p_high,
                                       res.max_p, res.p_act)
    assert any("under-calls" in p for p in probs)


def test_exceedance_clipped_display():
    assert cardcheck.fmt_p(0.01) == "<1%" and cardcheck.fmt_p(0.99) == ">99%" and cardcheck.fmt_p(0.4) == "40%"


def test_scenario_is_proportional_and_labelled():
    obs = data_io.load_uae_observed()
    fc, _, meta, _ = data_io.load_uae_forecasts(obs)
    issue = dt.date.fromisoformat(str(meta["issue_date"]))
    rsv = fc[fc.target == data_io.UAE_TARGETS["rsv"]]
    a = data_io.rsv_scenario(obs, rsv, issue, 400, 4.0, 1000)
    b = data_io.rsv_scenario(obs, rsv, issue, 800, 4.0, 1000)
    assert a.attrs["n_seasons"] >= 3 and len(a) >= 1
    first = lambda s: float(s.split(" ")[-1].rstrip(")"))  # noqa: E731  median admissions
    assert abs(first(b.iloc[0]["scenario admissions / week"]) - 2 * first(a.iloc[0]["scenario admissions / week"])) <= 1
    src = (ROOT / "app" / "streamlit_app.py").read_text()
    assert "SCENARIO · NOT A FORECAST OF ADMISSIONS" in src


def test_season_frame_aligns_on_week27():
    obs = data_io.load_uae_observed()
    s = data_io.season_frame(obs, "rsv")
    assert s.x.min() >= 0 and s.x.max() < 54
    assert s.season.nunique() >= 4


def test_no_retired_claim_in_app():
    for f in (ROOT / "app").glob("*.py"):
        txt = f.read_text()
        assert "7 of 8" not in txt and "7/8" not in txt, f
