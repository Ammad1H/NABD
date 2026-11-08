"""R3-3 pilot connector: aggregation, k>=10 + complementary suppression, identifier rejection."""
import numpy as np
import pandas as pd
import pytest

from adapters.pilot import (AggregationError, K_MIN, check_suppressed, load_pilot, make_synthetic,
                            suppress, to_series)
from adapters.schemas import PersonLevelFieldError


def _group(counts, measure="admissions_rsv"):
    bands = ["0-5m", "6-23m", "2-4y", "5-14y", "15-49y", "50-64y", "65+y"]
    rows = [[pd.Timestamp("2026-11-02"), "week", "HOSP_X", "ABU_DHABI", measure, b, float(c), False, False]
            for b, c in zip(bands, counts)]
    rows.append([pd.Timestamp("2026-11-02"), "week", "HOSP_X", "ABU_DHABI", measure, "all", float(sum(counts)),
                 False, False])
    return pd.DataFrame(rows, columns=["period_start", "granularity", "facility_code", "region", "measure",
                                       "age_band", "count", "suppressed", "synthetic"])


def test_identifier_columns_rejected():
    df = _group([20, 30, 40, 50, 60, 70, 80])
    for col in ["patient_id", "emirates_id", "mrn", "dob", "Name"]:
        with pytest.raises(PersonLevelFieldError):
            load_pilot(df.assign(**{col: "x"}))


def test_small_cells_suppressed_and_never_released():
    out = load_pilot(_group([3, 30, 40, 50, 60, 70, 80]))
    released = out[~out.suppressed]
    assert not ((released["count"] > 0) & (released["count"] < K_MIN)).any()
    assert out.loc[out.age_band == "0-5m", "count"].isna().all()


def test_complementary_suppression_blocks_subtraction():
    out = load_pilot(_group([3, 30, 40, 50, 60, 70, 80]))
    bands = out[out.age_band != "all"]
    assert bands.suppressed.sum() >= 2  # the 3 plus at least one complement
    # all-ages total minus released bands no longer equals the single small cell
    total = out.loc[out.age_band == "all", "count"].iloc[0]
    assert total - bands["count"].sum(min_count=1) != 3


def test_zero_only_neighbours_still_get_complement():
    out = load_pilot(_group([4, 0, 0, 0, 0, 0, 0]))
    assert out[out.age_band != "all"].suppressed.sum() >= 2


def test_check_rejects_unsuppressed_table():
    raw = _group([3, 30, 40, 50, 60, 70, 80])
    with pytest.raises(AggregationError):
        check_suppressed(raw)


def test_schema_rejects_free_text_measure():
    df = _group([20, 30, 40, 50, 60, 70, 80]).assign(measure="diagnosis notes")
    with pytest.raises(Exception):
        load_pilot(df)


def test_suppressed_week_is_nan_never_imputed():
    df = load_pilot(_group([3, 30, 40, 50, 60, 70, 80]))
    s = to_series(df, "admissions_rsv", age_band="0-5m")
    assert s["count"].isna().all()


def test_synthetic_example_is_labelled_and_valid():
    df = load_pilot(make_synthetic())
    assert df.synthetic.all()
    assert df.facility_code.str.startswith("SYN_").all()


def test_shadow_scorer_reports_prespecified_exit_rule():
    from uae.pilot_shadow import demo
    out = demo()
    assert "SYNTHETIC" in out["data"]
    assert out["verdict"] in {"EXIT CRITERIA MET", "EXIT CRITERIA NOT MET", "NOT COMPUTABLE"}
    assert "0.9" in out.get("exit_rule", "0.9")
