"""Tests for the app workstream: audit chain, playbook schema, API schema (gate G5/G6)."""
import copy
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import audit  # noqa: E402
from playbook.validate import PlaybookError, load_playbook, match_band, validate_playbook  # noqa: E402

CODES = {"AGREE_FORECAST", "OTHER", "DATA_QUALITY"}


def _append(path, **kw):
    args = dict(approver="Dr Test", role="hospital_ops", decision="APPROVE", reason_code="AGREE_FORECAST",
                band_id="rsv_rising", proposed_action="Pre-warn ED", forecast_ref={"median": 14.2},
                playbook_version="0.1.0", path=path, valid_reason_codes=CODES)
    args.update(kw)
    return audit.append_decision(**args)


# ---------------------------------------------------------------- audit
def test_chain_intact_and_linked(tmp_path):
    p = tmp_path / "a.jsonl"
    r1 = _append(p)
    r2 = _append(p, decision="DISMISS", reason_code="DATA_QUALITY")
    assert r1["prev_hash"] == audit.GENESIS
    assert r2["prev_hash"] == r1["hash"]
    ok, msg = audit.verify_chain(p)
    assert ok, msg


def test_append_only_preserves_existing_bytes(tmp_path):
    p = tmp_path / "a.jsonl"
    _append(p)
    before = p.read_bytes()
    _append(p)
    after = p.read_bytes()
    assert after.startswith(before)
    assert len(audit.read_records(p)) == 2


@pytest.mark.parametrize("tamper", ["edit", "delete", "reorder", "insert"])
def test_tampering_detected(tmp_path, tamper):
    p = tmp_path / "a.jsonl"
    for _ in range(3):
        _append(p)
    lines = p.read_text().splitlines()
    if tamper == "edit":
        rec = json.loads(lines[1]); rec["decision"] = "DISMISS"; lines[1] = json.dumps(rec, sort_keys=True)
    elif tamper == "delete":
        del lines[1]
    elif tamper == "reorder":
        lines[0], lines[1] = lines[1], lines[0]
    else:
        lines.insert(1, lines[0])
    p.write_text("\n".join(lines) + "\n")
    ok, _ = audit.verify_chain(p)
    assert not ok


@pytest.mark.parametrize("kw", [dict(approver="  "), dict(decision="MAYBE"), dict(reason_code=""),
                                dict(reason_code="NOT_A_CODE"), dict(reason_code="OTHER", note=""),
                                dict(decision="MODIFY", modified_action="")])
def test_invalid_decisions_rejected(tmp_path, kw):
    with pytest.raises(audit.AuditError):
        _append(tmp_path / "a.jsonl", **kw)
    assert not (tmp_path / "a.jsonl").exists() or audit.read_records(tmp_path / "a.jsonl") == []


# ---------------------------------------------------------------- playbook
def test_playbook_valid_and_illustrative():
    pb = load_playbook()
    assert pb["status"] == "ILLUSTRATIVE" and pb["review"]["reviewed"] is False
    assert match_band(pb, "wk rsv pos pct sentinel", "ARE", 15.6)["id"] == "rsv_rising"
    assert match_band(pb, "wk rsv pos pct sentinel", "ARE", 25)["tier"] == 3


@pytest.mark.parametrize("mutate", [
    lambda pb: pb.pop("bands"),
    lambda pb: pb["bands"][0]["actions"].pop("adphc_duty"),
    lambda pb: pb["bands"][0]["actions"]["hospital_ops"].pop("ar"),
    lambda pb: pb["bands"][1].update(lower=5),             # overlaps rsv_low
    lambda pb: pb.update(status="REVIEWED"),               # reviewed flag still false
    lambda pb: pb["bands"].append(copy.deepcopy(pb["bands"][0])),  # duplicate id
])
def test_playbook_schema_rejects_bad(mutate):
    pb = load_playbook()
    mutate(pb)
    with pytest.raises(PlaybookError):
        validate_playbook(pb)


# ---------------------------------------------------------------- API
def test_api_schema():
    from fastapi.testclient import TestClient
    from app.api import app
    c = TestClient(app)
    h = c.get("/health")
    assert h.status_code == 200 and h.json()["status"] == "ok"
    r = c.get("/forecast", params={"location": "ARE", "target": "wk rsv pos pct sentinel"})
    assert r.status_code == 200
    body = r.json()
    assert {"location", "target", "unit", "model", "reference_date", "demo", "forecasts"} <= set(body)
    assert body["unit"] == "percent" and len(body["forecasts"]) >= 1
    for f in body["forecasts"]:
        qs = [q["quantile"] for q in f["quantiles"]]
        vals = [q["value"] for q in f["quantiles"]]
        assert qs == sorted(qs) and vals == sorted(vals), "quantiles must be monotone"
        assert f["horizon_label"] == "nowcast" or f["horizon_label"].startswith("+")
    assert c.get("/forecast", params={"location": "USA"}).status_code == 404
    assert c.get("/forecast", params={"target": "bogus"}).status_code == 422
    assert "/forecast" in c.get("/openapi.json").json()["paths"]


def test_workforce_suppression():
    from app.workforce import secure_aggregate, synthetic_employers
    emp = synthetic_employers(60)
    table, _ = secure_aggregate(emp, k=10)
    for _, row in table.iterrows():
        n = int((emp.district == row.district).sum())
        if n >= 10:
            assert row.released and row.resp_absent_total == int(emp[emp.district == row.district].resp_absent.sum())
        else:
            assert not row.released and pd.isna(row.resp_absent_total)
