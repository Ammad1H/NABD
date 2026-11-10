"""Decision replay (DEVIATIONS V1): engine arithmetic and consistency of the committed results."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from replay import engine as E  # noqa: E402

Q = [0.1, 0.25, 0.5, 0.75, 0.9]


def _fc(model, vals_by_week):
    rows = []
    for k, vals in enumerate(vals_by_week):
        for q, v in zip(Q, vals):
            rows.append(dict(reference_date=f"2024-01-{7*k+1:02d}", target="wk flu pos pct", horizon=2,
                             target_end_date=f"2024-02-{7*k+1:02d}", location="XXX", output_type="quantile",
                             output_type_id=q, value=v, model=model, season=2023))
    return pd.DataFrame(rows)


def test_rule_missed_and_wasted():
    hi, lo = [16, 18, 20, 22, 24], [1, 2, 3, 4, 5]
    F = pd.concat([_fc("A", [hi, hi, lo, lo]), _fc("B", [lo, lo, lo, lo])])
    truth = pd.DataFrame(dict(location="XXX", target="wk flu pos pct",
                              target_end_date=[f"2024-02-{7*k+1:02d}" for k in range(4)], value=[20, 5, 20, 5]))
    th = pd.DataFrame(dict(location=["XXX"], target=["wk flu pos pct"], season=[2023], T=[15.0]))
    D = E.add_references(E.decisions(E.exceedance(F, th), truth))
    S = E.per_season(D).set_index("model")
    assert (S.loc["A", ["missed", "wasted", "mismatch"]] == [1, 1, 2]).all()      # hit, wasted, missed, correct
    assert (S.loc["B", ["missed", "wasted"]] == [2, 0]).all()
    assert S.loc["perfect-foresight", "mismatch"] == 0
    assert S.loc["always-roster", "wasted"] == 2 and S.loc["never-roster", "missed"] == 2


def test_common_cells_only():
    hi = [16, 18, 20, 22, 24]
    F = pd.concat([_fc("A", [hi, hi]), _fc("B", [hi])])
    truth = pd.DataFrame(dict(location="XXX", target="wk flu pos pct",
                              target_end_date=["2024-02-01", "2024-02-08"], value=[20, 20]))
    th = pd.DataFrame(dict(location=["XXX"], target=["wk flu pos pct"], season=[2023], T=[15.0]))
    D = E.decisions(E.exceedance(F, th), truth)
    assert len(D) == 2 and set(D.target_end_date) == {"2024-02-01"}


def test_committed_results_consistent():
    out = ROOT / "results" / "replay"
    s = json.loads((out / "summary.json").read_text())
    assert "POST HOC" in s["status"] and s["rule"]["p_star"] == 0.30
    W = pd.read_csv(out / "tables" / "weekly_decisions.csv.gz")
    w = W[(W.threshold_kind == "playbook") & (W.horizon == 2) & W.location.isin(["OMN", "QAT", "SAU"])]
    for ser, tgt, n in [("flu", "wk flu pos pct", 12), ("rsv", "wk rsv pos pct", 10)]:
        r = s["results"][f"GCC|{ser}|playbook|p30|h2"]
        assert r["n_country_seasons"] == n
        for m in ["NABD", "past-season-pattern", "persistence"]:
            x = w[(w.target == tgt) & (w.model == m)]
            assert int(x.missed.sum()) == r["totals"][m]["missed"]
            assert int(x.wasted.sum()) == r["totals"][m]["wasted"]
        d = r["NABD_minus_past-season-pattern_mismatch"]
        assert np.isclose(d["diff_per_season"], d["mean_a"] - d["mean_b"], atol=0.01)


def test_summary_states_losses_and_scenario():
    t = (ROOT / "results" / "replay" / "SUMMARY.md").read_text()
    for must in ["POST HOC", "not cash saved", "No advantage over simply carrying last week forward",
                 "missed more RSV surge weeks"]:
        assert must in t
