"""Foundation-model benchmark outputs (DEVIATIONS W1, post hoc). Reads stored results only; no torch needed."""
import json
from pathlib import Path

import pandas as pd
import pytest

OUT = Path(__file__).resolve().parents[1] / "results" / "fm"
pytestmark = pytest.mark.skipif(not (OUT / "summary.json").exists(), reason="fm benchmark not run")


def test_rescoring_check_and_common_cells():
    s = json.loads((OUT / "summary.json").read_text())
    assert abs(s["check_w1d"]["rel_wis"] - 0.767) < 0.002
    sc = pd.read_csv(OUT / "scores_long.csv.gz")
    assert sc.groupby("model").size().nunique() == 1 and sc.model.nunique() == 7
    assert sc.country.nunique() == 18


def test_summary_ratios_match_scores():
    s = json.loads((OUT / "summary.json").read_text())
    sc = pd.read_csv(OUT / "scores_long.csv.gz")
    w = sc.groupby("model").wis.sum()
    assert abs(w["Chronos-2 (zero-shot)"] / w["NABD-Pool"] - s["results"]["Chronos-2 (zero-shot)"]["vs_NABD-Pool"]["rel_wis"]) < 1e-3
    assert abs(w["Pool+FM"] / w["NABD-Pool"] - s["results"]["Pool+FM"]["vs_NABD-Pool"]["rel_wis"]) < 1e-3
