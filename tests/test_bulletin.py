"""Bulletin (BUILD round 4): deterministic bytes, two pages, required content, never 'ADPHC format'."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("reportlab")
pytest.importorskip("arabic_reshaper")
pytest.importorskip("bidi")

from bulletin import make_bulletin as mb  # noqa: E402


@pytest.fixture(scope="module")
def pdf_bytes():
    if not mb.round_stamps():
        pytest.skip("no ledger round")
    return mb.build_pdf_bytes("latest")


def test_deterministic(pdf_bytes):
    assert mb.build_pdf_bytes("latest") == pdf_bytes


def test_two_pages_and_content(pdf_bytes):
    pypdf = pytest.importorskip("pypdf")
    import io
    r = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    assert len(r.pages) == 2
    en = r.pages[0].extract_text()
    for needle in ("NABD weekly respiratory forecast bulletin", "P(>", "PROPOSED, NOT APPROVED",
                   "What this bulletin is not", "ILLUSTRATIVE playbook", "not an official DoH or ADPHC product"):
        assert needle in en, needle
    rd = mb.load_round(mb.round_stamps()[-1])
    assert rd["sha256"] in en.replace("\n", "")


def test_never_called_adphc_format():
    src = (ROOT / "bulletin" / "make_bulletin.py").read_text(encoding="utf-8")
    assert "ADPHC format" not in src


def test_observed_truncated_to_round(pdf_bytes):
    rd = mb.load_round(mb.round_stamps()[-1])
    obs = mb.observed_as_of(rd["meta"])
    last = f"{int(obs.ISO_YEAR.iloc[-1])}-W{int(obs.ISO_WEEK.iloc[-1]):02d}"
    assert last == min((rd["meta"].get("data_through_week") or {"x": last}).values())
