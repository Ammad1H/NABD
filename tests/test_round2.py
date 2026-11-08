"""Round-2 checks: scorer agreement with the vendored kit, the D6 bootstrap, and summary keys."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "nabd_v2_kit"))
from nabd_kit import quantiles as kq, scoring as ksc  # noqa: E402

from eval.wis import QUANTILES, wis  # noqa: E402


def test_wis_matches_independent_kit():
    rng = np.random.default_rng(1)
    q = np.sort(rng.gamma(2, 50, size=(500, 23)), axis=1)
    y = rng.gamma(2, 50, size=500)
    assert np.allclose(kq.FLUSIGHT_LEVELS, QUANTILES)
    assert np.max(np.abs(wis(q, y) - ksc.wis(q, y, kq.FLUSIGHT_LEVELS))) < 1e-9


def test_circular_block_bootstrap_deterministic_and_brackets_estimate():
    from eval.round2 import circular_block_ci
    refs = np.repeat(pd.date_range("2024-11-23", periods=20, freq="7D"), 5)
    rng = np.random.default_rng(0)
    a, b = rng.uniform(1, 2, 100), rng.uniform(1, 2, 100) * 1.2
    r1 = circular_block_ci(a, b, refs, 4, nboot=300)
    r2 = circular_block_ci(a, b, refs, 4, nboot=300)
    assert r1 == r2 and r1[1] <= r1[0] <= r1[2]


def test_summary_has_verdict_keys_and_flags_exploratory():
    s = json.loads((ROOT / "results" / "summary.json").read_text())
    assert s["primary_verdict"] in ("MET", "NOT MET")
    assert s["primary_verdict"] == s["primary"]["non_inferiority"]
    assert "primary_text" in s
    if "exploratory" in s:
        assert s["exploratory"]["exploratory"] is True
