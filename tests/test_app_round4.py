"""Build round 4 (app): plain band labels, ledger-consistent horizon labels, winter-planner arithmetic."""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import cardcheck, data_io, planner  # noqa: E402
from playbook.validate import PlaybookError, load_playbook, validate_playbook  # noqa: E402


def test_every_band_has_plain_label_and_all_roles():
    pb = load_playbook()
    assert "occupational_health" in pb["roles"]
    for b in pb["bands"]:
        for lang in ("en", "ar"):
            lab = cardcheck.band_label(b, lang)
            assert lab and lab != b["id"] and "_" not in lab
        assert set(b["actions"]) == set(pb["roles"])


def test_validator_rejects_missing_label():
    pb = load_playbook()
    bad = json.loads(json.dumps(pb))
    del bad["bands"][0]["label"]
    with pytest.raises(PlaybookError):
        validate_playbook(bad)


def test_card_horizon_labels_match_ledger_round():
    rounds = data_io.ledger_round_files()
    if not rounds:
        pytest.skip("no ledger round")
    fc, pers, meta, demo = data_io.load_uae_forecasts()
    assert not demo
    meta_file = ROOT / "ledger" / (meta["round_file"][:-4] + ".meta.json")
    m = json.loads(meta_file.read_text())
    issue = dt.date.fromisoformat(meta["issue_date"])
    for h in m["horizons"]:
        lab = data_io.display_horizon(h["target_end_date"], issue, meta)
        if float(h["weeks_ahead_of_issue"]) <= 0:
            assert lab == "nowcast"
        else:
            assert lab == f"+{float(h['weeks_ahead_of_issue']):g} wk"


def _flat_forecast(issue: dt.date, value: float) -> pd.DataFrame:
    from nabd_kit.quantiles import FLUSIGHT_LEVELS
    rows = []
    for k in range(1, 4):
        d = issue + dt.timedelta(days=7 * k)
        for q in FLUSIGHT_LEVELS:
            rows.append({"target_end_date": d, "q": float(q), "value": value * (0.5 + float(q))})
    return pd.DataFrame(rows)


def test_planner_reproduces_hospital_averages_at_average_positivity():
    obs = data_io.load_uae_observed()
    season_sum, _ = planner.season_reference(obs)
    avg = season_sum / 52
    issue = dt.date(2026, 11, 8)
    fc = _flat_forecast(issue, avg)   # median == average positivity
    plan = planner.winter_plan(obs, fc, issue, annual_admissions=520, los_days=4.0, beds=40, nurses=100,
                               absence_rate_avg=0.02, shifts_per_nurse_week=4, spare_shifts_week=0, cost_usd=1000)
    med_adm = float(plan["RSV admissions / week"].iloc[0].split(" – ")[1])
    assert med_adm == pytest.approx(10, abs=0.5)          # 520 / 52
    med_abs = float(plan["nurses absent (respiratory)"].iloc[0].split(" – ")[1])
    assert med_abs == pytest.approx(2.0, abs=0.05)         # 100 x 2%
    assert plan["P(roster gap > 0)"].iloc[0] == ">99%"     # no spare shifts -> any absence is a gap


def test_planner_hides_workforce_without_hr_figure():
    obs = data_io.load_uae_observed()
    issue = dt.date(2026, 11, 8)
    plan = planner.winter_plan(obs, _flat_forecast(issue, 10), issue, annual_admissions=438, los_days=4, beds=40,
                               nurses=80, absence_rate_avg=None, shifts_per_nurse_week=4, spare_shifts_week=10,
                               cost_usd=2241)
    assert not any("absent" in c or "roster" in c for c in plan.columns)
    assert "cost of RSV admissions (AED)" in plan.columns


def test_planner_gap_probability_falls_with_more_cover():
    obs = data_io.load_uae_observed()
    issue = dt.date(2026, 11, 8)
    fc = _flat_forecast(issue, 10)
    ps = []
    for spare in (0, 20, 60, 400):
        plan = planner.winter_plan(obs, fc, issue, annual_admissions=438, los_days=4, beds=40, nurses=100,
                                   absence_rate_avg=0.03, shifts_per_nurse_week=4, spare_shifts_week=spare, cost_usd=0)
        s = plan["P(roster gap > 0)"].iloc[0]
        ps.append(1.0 if s == ">99%" else 0.0 if s == "<1%" else float(s.rstrip("%")) / 100)
    assert all(a >= b for a, b in zip(ps, ps[1:])) and ps[0] > ps[-1]


def test_no_banned_wording_in_app_text():
    banned = ["blind", "nobody in the uae publishes", "calibrated rsv", "how often an alert is real",
              "outside-anchored", "row-for-row", "fewer false alarms"]
    for f in ["app/streamlit_app.py", "app/i18n.py", "app/api.py", "bulletin/make_bulletin.py"]:
        txt = (ROOT / f).read_text(encoding="utf-8").lower()
        for w in banned:
            assert w not in txt, (f, w)
