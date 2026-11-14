"""The static web front-end must show exactly what the results files say (web/build.py)."""
import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not (ROOT / "results" / "pool" / "summary.json").exists(), reason="results not computed")


@pytest.fixture(scope="module")
def data():
    from web import build
    d = build.build()
    js = (build.DIST / "data.js").read_text(encoding="utf-8")
    assert js.startswith("window.NABD = ") and "NaN" not in js and "Infinity" not in js
    assert json.loads(js[len("window.NABD = "):].rstrip().rstrip(";")) == json.loads(json.dumps(d))
    return d


def test_headline_is_the_designated_model_and_challenger_is_separate(data):
    cur = data["current"]
    assert cur["headline"] == "NABD-UAE-v1" and not cur["demo"]
    assert set(cur["cards"]) >= {"NABD-UAE-v1"} and "persistence" not in cur["cards"]
    for series in ("rsv", "flu"):
        fan = cur["forecasts"]["NABD-UAE-v1"][series]
        assert len(fan) == 4 and all(r["q"]["0.1"] <= r["q"]["0.5"] <= r["q"]["0.9"] for r in fan)


def test_evidence_numbers_equal_the_summary_files(data):
    pool = json.loads((ROOT / "results" / "pool" / "summary.json").read_text())
    assert data["evidence"]["pool"]["primary"] == pool["PRIMARY_flu_pool_vs_local_v1"]
    assert data["evidence"]["pool"]["verdict"] == pool["PRIMARY_verdict"]
    assert len(data["evidence"]["pool"]["per_country"]) == pool["n_included"]
    us = json.loads((ROOT / "results" / "summary.json").read_text())
    assert data["evidence"]["us"]["verdict"] == us["primary_verdict"] == "NOT MET"      # the loss is on the page
    fm = ROOT / "results" / "fm" / "summary.json"
    if fm.exists():
        f = json.loads(fm.read_text())
        assert data["evidence"]["fm"]["fm_vs_pool"] == f["results"]["Chronos-2 (zero-shot)"]["vs_NABD-Pool"]


def test_embedded_ledger_files_hash_to_the_recorded_values(data):
    led = data["ledger"]
    assert led["rounds"], "no ledger rounds exported"
    for r in led["rounds"]:
        assert hashlib.sha256(led["files"][r["file"]].encode("utf-8")).hexdigest() == r["sha256"], r["file"]


def test_replay_units_and_bilingual_names(data):
    assert {u["source"] for u in data["replay"]} == {"gulf", "heldout"}
    for u in data["replay"]:
        n = len(u["te"])
        assert len(u["obs"]) == n and all(len(m["roster"]) == n for m in u["models"].values())
        assert u["location"] in data["countries"] and data["countries"][u["location"]]["ar"]


def test_page_sources_have_no_banned_wording():
    src = "\n".join((ROOT / "web" / "src" / f).read_text(encoding="utf-8") for f in ("app.js", "index.html")).lower()
    for banned in ("blind test", "verified row-for-row", "fewer false alarms", "early warning of onset", "nobody publishes"):
        assert banned not in src, banned
