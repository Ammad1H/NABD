"""Borrowed-strength test guards (docs/PREREG-POOL.md)."""
import io
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pool import config as C
from pool import data as pdata
from pool import locks
from pool.features import FEATS_G, feature_table, load

ROOT = Path(__file__).resolve().parents[1]
DEV = ROOT / "data" / "raw" / "flunet_pool_dev.csv"


def test_country_sets_disjoint_and_seen_countries_never_held_out():
    assert not set(C.DEV) & set(C.HELD)
    assert set(C.ALREADY_SEEN) <= set(C.DEV)
    assert len(C.HELD) == 36


def test_lock1_verifies():
    assert len(locks.check_lock1()) == 64


def test_dev_file_has_no_held_out_rows():
    d = pd.read_csv(DEV, usecols=["COUNTRY_CODE"])
    assert set(d.COUNTRY_CODE) <= set(C.DEV)


def test_held_out_extraction_refused_without_lock2(monkeypatch, tmp_path):
    monkeypatch.setattr(locks, "LOCK2", tmp_path / "missing.json")
    with pytest.raises(pdata.HeldOutGuard):
        pdata.allowed_countries("held")


def test_scorer_refuses_without_lock2(monkeypatch, tmp_path):
    from pool import score
    monkeypatch.setattr(locks, "LOCK2", tmp_path / "missing.json")
    with pytest.raises(Exception):
        score.confirm(selftest=False)


def test_scorer_refuses_if_model_changed_after_lock2(monkeypatch, tmp_path):
    """Positive control for the goalpost guard: a changed model config must break lock #2."""
    if not locks.LOCK2.exists():
        pytest.skip("lock #2 not made yet")
    import json
    cfg = json.loads(locks.MODEL_CONFIG.read_text())
    cfg["chosen"] = "something else"
    alt = tmp_path / "model_config.json"
    alt.write_text(json.dumps(cfg))
    monkeypatch.setattr(locks, "MODEL_CONFIG", alt)
    with pytest.raises(Exception):
        locks.check_lock2()


def test_stream_filter_keeps_only_requested_countries(tmp_path):
    hdr = ",".join(C.COLUMNS + ["OTHER"])
    lines = [hdr, "ARE,2024,1,SENTINEL,100,10,2,x", "EGY,2024,1,SENTINEL,100,10,2,x",
             "USA,2014,1,SENTINEL,100,10,2,x", "USA,2024,2,SENTINEL,50,5,1,x"]
    out = tmp_path / "f.csv"
    info = pdata.stream_filter(["ARE", "USA"], out, lines=io.StringIO("\n".join(lines)))
    got = pd.read_csv(out)
    assert set(got.COUNTRY_CODE) == {"ARE", "USA"} and len(got) == 2 and info["rows_in"] == 4


@pytest.fixture(scope="module")
def are():
    return load(DEV, ["ARE"])["ARE"]


def test_features_use_no_future_data_with_positive_control(are):
    x, q = are["x"].copy(), are["q"]
    S = 2024
    base = feature_table(x, q, "ARE", seasons=[S])
    idx = x.index[x.season == S]
    cut = idx[len(idx) // 2]
    fut = x.copy()
    fut.loc[fut.index > cut + 4, ["y", "logspec"]] += 3.0          # change only weeks after every target of `cut`
    fut.loc[fut.season > S, ["y"]] += 1.0                           # and every later season
    f2 = feature_table(fut, q, "ARE", seasons=[S])
    a = base[base.i <= cut][FEATS_G + ["target"]].to_numpy(float)
    b = f2[f2.i <= cut][FEATS_G + ["target"]].to_numpy(float)
    assert np.allclose(a, b, equal_nan=True)                        # nothing leaked
    past = x.copy()
    past.loc[past.index == cut - 1, "y"] += 3.0                     # positive control: change the past
    f3 = feature_table(past, q, "ARE", seasons=[S])
    c = f3[f3.i == cut][FEATS_G].to_numpy(float)
    assert not np.allclose(base[base.i == cut][FEATS_G].to_numpy(float), c, equal_nan=True)


def test_pooled_training_rows_are_strictly_before_the_evaluation_season(are):
    from pool import harness as Hn
    T = Hn.train_table({"ARE": are}, relaxed=True)
    S = 2024
    tr = T[T.season < S]
    assert tr.origin.max() < are["x"].week_end[are["x"].season == S].min()
    assert not set(tr.season) & set(C.EXCLUDE_TRAINING_SEASONS)


def test_live_pool_forecast_for_the_uae_ledger():
    """The challenger issues 23 ordered percent quantiles per horizon from cached data."""
    if not locks.LOCK2.exists():
        pytest.skip("lock #2 not made yet")
    from adapters import flunet
    from pool.live import forecast
    s = flunet.sentinel_series(flunet.load("cached"))
    pf = forecast(s, "flu")
    assert set(pf) == {1, 2, 3, 4}
    for v in pf.values():
        assert len(v) == 23 and np.all(np.diff(v) >= 0) and 0 <= v[0] and v[-1] <= 100


def test_confirmatory_summary_matches_scores():
    import json
    p = ROOT / "results" / "pool" / "summary.json"
    if not p.exists():
        pytest.skip("confirmatory test not run yet")
    from pool import harness as Hn
    s = json.loads(p.read_text())
    sc = pd.read_csv(ROOT / "results" / "pool" / "tables" / "scores_long.csv")
    r = Hn.rel(sc, "NABD-Pool", "NABD-UAE-v1")
    assert r["rel_wis"] == s["PRIMARY_flu_pool_vs_local_v1"]["rel_wis"]
    assert set(sc.country) <= set(C.HELD) and set(sc.country) == set(s["included_countries"])
