"""The FluSight validator must pass the draft file and catch broken ones (crossing, missing levels, bad name)."""
from pathlib import Path

import pandas as pd
import pytest

from eval import flusight_validate as fv

ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / "external" / "hub"
DRAFT = ROOT / "results" / "flusight_draft" / "2026-11-14-NABD-v1.csv"
pytestmark = pytest.mark.skipif(not (HUB / "hub-config" / "tasks.json").exists() or not DRAFT.exists(),
                                reason="needs the hub clone and the draft file")


def test_draft_passes():
    errors, _ = fv.validate(DRAFT, HUB)
    assert errors == []


def test_crossing_quantiles_fail(tmp_path):
    d = pd.read_csv(DRAFT, dtype={"location": str, "output_type_id": str})
    i = d.index[(d.output_type_id == "0.99")][0]
    d.loc[i, "value"] = 0  # top quantile below the rest -> crossing
    p = tmp_path / DRAFT.name
    d.to_csv(p, index=False)
    errors, _ = fv.validate(p, HUB)
    assert any("non-decreasing" in e for e in errors)


def test_missing_level_fails(tmp_path):
    d = pd.read_csv(DRAFT, dtype={"location": str, "output_type_id": str})
    d = d[~((d.location == d.location.iloc[0]) & (d.horizon == 0) & (d.output_type_id == "0.5"))]
    p = tmp_path / DRAFT.name
    d.to_csv(p, index=False)
    errors, _ = fv.validate(p, HUB)
    assert any("quantile levels" in e for e in errors)


def test_bad_name_fails(tmp_path):
    p = tmp_path / "forecast.csv"
    p.write_text("x")
    errors, _ = fv.validate(p, HUB)
    assert errors and "file name" in errors[0]
