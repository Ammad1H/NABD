"""Decision replay of the S1 held-out forecasts (DEVIATIONS V2, post hoc)."""
import json
from pathlib import Path

import pandas as pd
import pytest

from replay import engine as E
from replay import pool_replay as PR

OUT = Path(__file__).resolve().parents[1] / "results" / "replay" / "pool"
pytestmark = pytest.mark.skipif(not (OUT / "summary.json").exists(), reason="pool replay not run yet")


def test_forecast_file_matches_locked_scores():
    chk = PR.check_against_scores()
    assert chk["cells"] > 20000 and chk["max_abs_diff"] <= 5.0001e-4


def test_contract_conversion_keeps_horizon_convention():
    F, truth = PR.contract_forecasts()
    assert set(F.horizon.unique()) == {0, 1, 2, 3}          # h - 1, as in replay.regen
    assert set(F.model.unique()) == {PR.MAIN, *PR.COMPARATORS}
    one = F[(F.horizon == E.PRIMARY_H)].iloc[0]
    assert (pd.Timestamp(one.target_end_date) - pd.Timestamp(one.reference_date)).days == 14   # target week L+3
    assert not truth.duplicated(["location", "target_end_date"]).any()


def test_summary_matches_per_season_table():
    summ = json.loads((OUT / "summary.json").read_text())
    S = pd.read_csv(OUT / "per_season_country_q75_p30.csv")
    S = S[S.horizon == E.PRIMARY_H]
    r = summ["results"][f"country_q75|p30|h{E.PRIMARY_H}"]
    d = r[f"{PR.MAIN}_minus_{PR.LOCAL}_mismatch"]
    a, b = S[S.model == PR.MAIN].mismatch.mean(), S[S.model == PR.LOCAL].mismatch.mean()
    assert d["n_country_seasons"] == 36 and r["n_countries"] == 18
    assert abs(d["diff_per_season"] - (a - b)) < 1e-3
    assert d["ci95"][0] <= d["diff_per_season"] <= d["ci95"][1]
    # same cells for every model; references behave as defined
    assert S.groupby("model").weeks.sum().nunique() == 1
    assert S[S.model == "perfect-foresight"].mismatch.sum() == 0
    assert (S[S.model == "never-roster"].missed == S[S.model == "never-roster"].surge_weeks).all()


def test_thresholds_use_no_evaluation_season_data():
    th = pd.read_csv(OUT / "thresholds_country_q75.csv")
    assert (th.n_train_seasons >= 2).all() and th["T"].between(0, 100).all()
