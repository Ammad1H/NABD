"""Season Replay page and landing view (final stretch S3)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import data_io  # noqa: E402


def test_replay_loader_and_default_by_rule():
    summ, W, truth = data_io.load_replay()
    assert summ and W is not None and truth is not None
    assert set(W.threshold_kind) == {"playbook"}
    locs = [c for c in ["OMN", "QAT", "SAU", "ARE"] if c in set(W.location)]
    assert locs[0] == "OMN"                                    # DEVIATIONS V1i: default set by rule
    assert W[(W.location == "OMN") & (W.target == "wk flu pos pct")].season.max() == 2025
    h = data_io.replay_headline(summ, "flu")
    assert h["n"] == 12 and h["vs_pattern"]["diff_per_season"] < 0


def test_losing_seasons_are_selectable():
    _, W, _ = data_io.load_replay()
    w = W[(W.horizon == 2) & W.model.isin(["NABD", "persistence"])]
    s = w.groupby(["location", "target", "season", "model"]).mismatch.sum().unstack()
    assert (s["NABD"] > s["persistence"]).any()              # seasons where NABD did worse are in the list


@pytest.mark.parametrize("lang", ["en", "ar"])
def test_replay_page_slider_and_selectors(lang):
    pytest.importorskip("streamlit.testing.v1")
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=60)
    at.run()
    at.sidebar.radio[0].set_value(lang)
    at.sidebar.radio[1].set_value("nav_replay")
    at.run()
    assert not at.exception
    assert at.selectbox[0].value == "OMN" and at.selectbox[2].value == 2025
    for k in (1, at.slider[0].max):
        at.slider[0].set_value(k)
        at.run()
        assert not at.exception, (lang, k, [e.value for e in at.exception])
    at.selectbox[0].set_value("ARE")
    at.run()
    assert not at.exception


def test_landing_buttons_navigate():
    pytest.importorskip("streamlit.testing.v1")
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=60)
    at.run()
    assert at.sidebar.radio[1].value == "nav_home" and len(at.metric) >= 3
    at.button[0].click()
    at.run()
    assert not at.exception and at.sidebar.radio[1].value == "nav_replay"
