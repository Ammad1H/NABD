"""Prospective UAE test (docs/PREREG-LIVE.md): lock, round discovery and scoring arithmetic."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from adapters import flunet
from ledger import live_lock, live_test

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not (ROOT / "docs" / "LOCK-LIVE.json").exists(), reason="live test not locked yet")


def test_lock_verifies():
    assert len(live_lock.check()) == 64


def test_r0_r1_excluded_and_r2_has_all_models():
    by, excl = live_test.rounds()
    assert "R0" not in by and "R1" not in by and "R2" in by
    assert set(live_test.MODELS) <= set(by["R2"])


def test_scoring_with_a_simulated_published_week(monkeypatch, tmp_path):
    """Pretend WHO published one more week: only horizon-1 cells are scored, on common cells, with a valid ratio."""
    real = flunet.sentinel_series(flunet.load("cached"))
    nxt = real.iloc[[-1]].copy()
    nxt["week_end"] = nxt.week_end + pd.Timedelta(days=7)
    nxt[["specimens", "flu_pos", "rsv_pos"]] = [[400.0, 90.0, 44.0]]
    monkeypatch.setattr(flunet, "sentinel_series", lambda d: pd.concat([real, nxt], ignore_index=True))
    monkeypatch.setattr(live_test, "LEDGER", live_test.LEDGER)
    sc = live_test.score_cells("cached")
    r2 = sc[sc["round"] == "R2"]
    assert set(r2.model) == set(live_test.MODELS)
    assert r2.groupby("model").size().nunique() == 1 and (r2.groupby("model").size() == 2).all()   # flu + RSV, one week
    assert np.isclose(r2[r2.target.str.contains("flu")].obs.iloc[0], 22.5)
    d = live_test.rel(r2[r2.target.str.contains("flu")], live_test.POOL, live_test.LOCAL)
    assert d["n_rounds"] == 1 and d["rel_wis"] > 0


def test_final_assessment_is_refused_before_the_date():
    with pytest.raises(SystemExit):
        live_test.run("cached", final=True)
    # run() with final=True must not have written a verdict
    assert "PRIMARY_verdict" not in json.loads((ROOT / "ledger" / "live_test.json").read_text())
