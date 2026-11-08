"""results/SUMMARY.md's Round-2 section must be exactly what eval/round2.py generates from the committed
tables (audit R3 #14): no hand-written numbers, and rerunning `make all` leaves it unchanged."""
import json
from pathlib import Path

import pandas as pd

from eval import round2

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / "results" / "tables"


def test_round2_section_matches_tables():
    d6o = {"block": pd.read_csv(TAB / "sensitivity_block_bootstrap.csv"),
           "national_share": pd.read_csv(TAB / "national_share.csv"),
           "excl_us": pd.read_csv(TAB / "excl_national.csv"),
           "wins": pd.read_csv(TAB / "per_location_wins.csv")}
    lt = pd.read_csv(TAB / "league_table.csv")
    xc = pd.read_csv(TAB / "scorer_crosscheck.csv")
    pdc = pd.read_csv(TAB / "phase_decomposition.csv")
    rev = pd.read_csv(TAB / "rev_curves.csv")
    status = json.loads((ROOT / "results" / "summary.json").read_text())["round2"]["league_status"]
    expected = round2.render_summary_section(d6o, lt, xc, pdc, rev, status)
    text = (ROOT / "results" / "SUMMARY.md").read_text()
    i = text.find(round2.ROUND2_HEADER)
    assert i >= 0, "Round-2 section missing from results/SUMMARY.md"
    assert text[i:].rstrip() == expected.rstrip(), "SUMMARY.md Round-2 section differs from the generated text"
