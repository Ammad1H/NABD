"""Tests for nabd_kit. Run: python tests/run_tests.py (or pytest if installed)."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nabd_kit import (calendar_features, card, decision, ledger, monitor, phase,  # noqa: E402
                      prereg, quantiles, recalibrate, scoring, synth)
from nabd_kit.baselines import flat_baseline  # noqa: E402
from nabd_kit.ensemble import quantile_average, quantile_median  # noqa: E402
from nabd_kit.gbm_global import GlobalQuantileGBM, qcols  # noqa: E402

LV = quantiles.FLUSIGHT_LEVELS
RNG = np.random.default_rng(42)


def _normal_q(mu, sd, levels=LV):
    mu = np.atleast_1d(mu)[:, None]
    sd = np.atleast_1d(sd)[:, None]
    return mu + sd * stats.norm.ppf(levels)[None, :]


# ---------------- quantiles ----------------
def test_check_levels_rejects_bad_sets():
    for bad in ([0.1, 0.5], [0.1, 0.4, 0.9], [0.5, 0.25, 0.75], [0.0, 0.5, 1.0]):
        try:
            quantiles.check_levels(bad)
        except ValueError:
            continue
        raise AssertionError(f"accepted bad levels {bad}")
    assert quantiles.check_levels(LV).size == 23


def test_cdf_exceedance_and_ties():
    q = _normal_q(100.0, 10.0)
    assert abs(quantiles.exceedance_prob(q, LV, 100.0)[0] - 0.5) < 1e-9
    p = quantiles.exceedance_prob(np.repeat(q, 3, axis=0), LV, [90.0, 100.0, 110.0])
    assert p[0] > p[1] > p[2]
    zeros = np.zeros((1, LV.size))
    assert quantiles.cdf_at(zeros, LV, 0.0)[0] == LV[-1]
    assert quantiles.exceedance_prob(q, LV, 1e9)[0] == 1 - LV[-1]


# ---------------- scoring ----------------
def test_wis_hand_example():
    lv = [0.25, 0.5, 0.75]
    assert abs(scoring.wis([[1.0, 2.0, 3.0]], [4.0], lv)[0] - 2.5 / 1.5) < 1e-12


def test_wis_equals_interval_formula():
    q = np.sort(RNG.normal(50, 15, size=(200, LV.size)), axis=1)
    y = RNG.normal(50, 20, size=200)
    k = (LV.size - 1) // 2
    total = 0.5 * np.abs(y - q[:, k])
    for i in range(k):
        a = 2 * LV[i]
        lo, hi = q[:, i], q[:, LV.size - 1 - i]
        interval = (hi - lo) + 2 / a * np.clip(lo - y, 0, None) + 2 / a * np.clip(y - hi, 0, None)
        total += a / 2 * interval
    assert np.allclose(total / (k + 0.5), scoring.wis(q, y, LV))


def test_wis_components_sum_to_wis():
    q = np.sort(RNG.normal(30, 8, size=(300, LV.size)), axis=1)
    y = RNG.normal(30, 12, size=300)
    d, o, u = scoring.wis_components(q, y, LV)
    assert np.allclose(d + o + u, scoring.wis(q, y, LV))
    assert (o[y < q[:, 0]] > 0).all() and (u[y > q[:, -1]] > 0).all()


def test_interval_hit_nominal_coverage():
    y = RNG.normal(0, 1, 20000)
    q = _normal_q(np.zeros_like(y), np.ones_like(y))
    assert abs(scoring.interval_hit(q, y, LV, 0.5).mean() - 0.5) < 0.02
    assert abs(scoring.interval_hit(q, y, LV, 0.9).mean() - 0.9) < 0.01


def test_pairwise_relative_wis():
    keys = pd.DataFrame({"loc": np.repeat(range(10), 5), "date": np.tile(range(5), 10)})
    a = keys.assign(model="A", wis=RNG.uniform(1, 2, 50))
    b = keys.assign(model="B", wis=RNG.uniform(2, 3, 50))
    c = keys.assign(model="C", wis=RNG.uniform(1.5, 2.5, 50))
    two = scoring.pairwise_relative_wis(pd.concat([a, b]), ["loc", "date"], baseline="B")
    ratio = a["wis"].mean() / b["wis"].mean()
    assert abs(two.loc[two.model == "A", "rel_wis"].iloc[0] - ratio) < 1e-12
    three = scoring.pairwise_relative_wis(pd.concat([a, b, c]), ["loc", "date"], baseline="B")
    assert abs(three.loc[three.model == "B", "rel_wis"].iloc[0] - 1.0) < 1e-12
    assert list(three.model)[0] == "A"


def test_block_bootstrap_ratio():
    df = pd.DataFrame({"date": np.repeat(range(40), 6), "a": RNG.uniform(1, 2, 240),
                       "b": RNG.uniform(1, 2, 240) * 1.3})
    r1 = scoring.block_bootstrap_ratio(df, "a", "b", "date", n_boot=500, seed=1)
    r2 = scoring.block_bootstrap_ratio(df, "a", "b", "date", n_boot=500, seed=1)
    assert r1 == r2 and r1["lo"] < r1["ratio"] < r1["hi"] and r1["hi"] < 1.0


def test_dm_test():
    better = scoring.dm_test(RNG.normal(-0.5, 1, 60), h=2)
    same = scoring.dm_test(RNG.normal(0, 1, 60) - 0.0, h=2)
    assert better["p_value"] < 0.01 and better["mean_diff"] < 0
    assert same["p_value"] > 0.001


# ---------------- phase ----------------
def test_asof_slope_ignores_future():
    y = np.array([10, 12, 15, 19, 24, 30, 31, 30, 25, 20], float)
    s1 = phase.asof_log_slope(y, window=3)
    y2 = y.copy()
    y2[6:] = 1000.0
    s2 = phase.asof_log_slope(y2, window=3)
    assert np.allclose(s1[:6], s2[:6], equal_nan=True) and np.isnan(s1[:2]).all()
    lab = phase.classify(s1, band=0.1)
    assert lab[4] == "rising" and lab[-1] == "falling" and lab[0] == "unknown"


def test_realized_phase_nowcast_unknown():
    lab = phase.realized_phase([10, 10], [20, 20], [0, 2])
    assert lab[0] == "unknown" and lab[1] == "rising"


# ---------------- baselines / ensemble ----------------
def test_flat_baseline_and_ensembles():
    hist = np.array([5, 7, 6, 9, 12, 10, 14, 13, 15, 18, 16, 20], float)
    fb = flat_baseline(hist, LV, horizons=(1, 2))
    assert np.allclose(fb[:, LV.size // 2], hist[-1]) and (fb >= 0).all()
    assert (np.diff(fb, axis=1) >= 0).all()
    qa, qb = _normal_q(10, 2), _normal_q(20, 4)
    assert np.allclose(quantile_average([qa, qb], [1, 0]), qa)
    assert np.allclose(quantile_median([qa, qb, qb]), qb)


# ---------------- recalibration ----------------
def test_spread_fit_recovers_scale():
    y = RNG.normal(100, 10, 3000)
    narrow = _normal_q(np.full(3000, 100.0), np.full(3000, 5.0))
    assert np.allclose(recalibrate.apply_spread(narrow, LV, 1.0), narrow)
    fit = recalibrate.fit_spread(narrow, y, LV)
    assert 1.8 <= fit["s_lo"] <= 2.2
    asym = recalibrate.fit_spread(narrow, y, LV, asymmetric=True)
    assert 1.7 <= asym["s_lo"] <= 2.3 and 1.7 <= asym["s_hi"] <= 2.3


def test_grouped_recalibrator_and_json_roundtrip():
    n = 600
    y = RNG.normal(50, 5, n)
    biased = _normal_q(np.full(n, 60.0), np.full(n, 2.0))   # too high and too narrow
    ref = _normal_q(np.full(n, 50.0), np.full(n, 6.0))
    groups = np.where(np.arange(n) % 2, "falling|h1", "flat|h1")
    rc = recalibrate.GroupedRecalibrator(LV, min_n=100).fit(biased, ref, y, groups)
    out = rc.transform(biased, ref, groups)
    assert scoring.wis(out, y, LV).mean() < scoring.wis(biased, y, LV).mean()
    rc2 = recalibrate.GroupedRecalibrator.from_json(rc.to_json())
    assert np.allclose(rc2.transform(biased, ref, groups), out)
    unknown = rc.transform(biased[:5], ref[:5], ["rising|h3"] * 5)
    assert unknown.shape == (5, LV.size)


def test_quantile_tracker_improves_coverage():
    trk = recalibrate.QuantileTracker(LV, lr=0.2)
    hits_before, hits_after = [], []
    for week in range(80):
        y = RNG.normal(100, 10, 30)
        raw = _normal_q(np.full(30, 120.0), np.full(30, 4.0))   # biased high, too narrow
        issued = trk.adjust(raw, "h1")
        if week >= 60:
            hits_before.append(scoring.interval_hit(raw, y, LV, 0.5).mean())
            hits_after.append(scoring.interval_hit(issued, y, LV, 0.5).mean())
        trk.update(issued, y, "h1")
    assert np.mean(hits_after) > np.mean(hits_before) + 0.2
    assert abs(np.mean(hits_after) - 0.5) < 0.15


# ---------------- global GBM ----------------
def test_gbm_global_fit_predict_no_leak():
    world = synth.make_world(n_locations=6, n_seasons=4, seed=3)
    train = world[world.season < 3]
    lv5 = np.array([0.05, 0.25, 0.5, 0.75, 0.95])
    model = GlobalQuantileGBM(lv5, horizons=(1, 2), gbm_params={"max_iter": 40}).fit(train)
    ref = world[world.season == 3].date.iloc[20]
    hist = world[world.date <= ref + pd.Timedelta(weeks=10)]
    p1 = model.predict(hist, ref)
    tampered = hist.copy()
    tampered.loc[tampered.date > ref, "value"] = 1e7
    p2 = model.predict(tampered, ref)
    q1, q2 = p1[qcols(lv5)].to_numpy(), p2[qcols(lv5)].to_numpy()
    assert len(p1) == 12 and np.allclose(q1, q2)
    assert (np.diff(q1, axis=1) >= 0).all() and (q1 >= 0).all()


# ---------------- decision ----------------
def test_relative_economic_value_edges():
    o = RNG.uniform(size=500) < 0.3
    alphas = [0.1, 0.2, 0.5]
    assert np.allclose(decision.relative_economic_value(o.astype(float), o, alphas), 1.0)
    clim = np.full(500, o.mean())
    assert np.allclose(decision.relative_economic_value(clim, o, alphas), 0.0)
    noisy = np.clip(o * 0.6 + RNG.uniform(0, 0.4, 500), 0, 1)
    v = decision.relative_economic_value(noisy, o, alphas)
    assert ((v > 0) & (v <= 1)).all()
    c = decision.contingency(noisy, o, 0.5)
    assert c["hits"] + c["misses"] == int(o.sum())


def test_alert_lead_times():
    y = [1, 2, 3, 5, 9, 15, 20]
    p = [0.0, 0.1, 0.4, 0.7, 0.9, 0.95, 0.99]
    r = decision.alert_lead_times(p, y, threshold=9, p_alert=0.6, max_lead=3)
    assert r["event_week"] == 4 and r["first_alert_week"] == 3 and r["lead"] == 1


# ---------------- card ----------------
def test_card_never_contradicts_forecast():
    for _ in range(300):
        last = float(RNG.uniform(5, 500))
        q = _normal_q(last * RNG.uniform(0.5, 1.6), last * RNG.uniform(0.05, 0.5))[0]
        q = np.clip(q, 0, None)
        cap = float(last * RNG.uniform(0.8, 2.0))
        c = card.make_card(last * RNG.uniform(0.6, 1.4), last, q, LV, horizon=2, capacity=cap)
        assert card.check_card(c, q, LV, capacity=cap) == []
    q = _normal_q(50.0, 5.0)[0]
    c = card.make_card(80.0, 100.0, q, LV, horizon=2, capacity=150.0)
    assert c.observed_key == "up" and c.forecast_key == "likely_down"
    c.forecast_key, c.action_key = "likely_up", "prepare_surge"
    assert len(card.check_card(c, q, LV, capacity=150.0)) >= 2


# ---------------- monitor ----------------
def test_monitor_fallback_and_ok():
    mon = monitor.CalibrationMonitor(LV, window=4, min_points=20)
    for wk in range(4):
        y = RNG.normal(100, 10, 30)
        good = _normal_q(np.full(30, 100.0), np.full(30, 10.0))
        mon.add_week(wk, good, y, q_ref=good * 1.0)
    assert mon.status()["state"] == "ok"
    mon2 = monitor.CalibrationMonitor(LV, window=4, min_points=20)
    for wk in range(4):
        y = RNG.normal(100, 10, 30)
        bad = _normal_q(np.full(30, 160.0), np.full(30, 3.0))
        ref = _normal_q(np.full(30, 100.0), np.full(30, 10.0))
        mon2.add_week(wk, bad, y, q_ref=ref)
    st = mon2.status()
    assert st["state"] == "fallback" and st["rel_wis"] > 1.25


# ---------------- ledger / prereg ----------------
def test_ledger_build_verify_tamper():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        (base / "src").mkdir()
        (base / "src" / "model.py").write_text("ALPHA = 1\n")
        (base / "plan.md").write_text("primary metric: relative WIS\n")
        df = pd.DataFrame({"location": ["US", "01"], "q0.5": [1.0, 2.0]})
        (base / "fc.csv").write_bytes(ledger.canonical_csv_bytes(df, ["location"]))
        m = ledger.build_manifest([base / "src", base / "plan.md", base / "fc.csv"], base)
        mj, ms = ledger.write_manifest(m, base / "lock")
        assert ledger.verify_manifest(mj) == [] and "MERKLE_ROOT" in ms.read_text()
        (base / "src" / "model.py").write_text("ALPHA = 2\n")
        assert any("changed" in p for p in ledger.verify_manifest(mj))
        assert ledger._main(["verify", str(mj)]) == 1
    assert ledger.canonical_csv_bytes(df.iloc[::-1], ["location"]) == ledger.canonical_csv_bytes(df, ["location"])


def test_prereg_goalpost_guard():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        plan, code = base / "plan.md", base / "model.py"
        plan.write_text("H1: relative WIS vs persistence < 1\n")
        code.write_text("W = 0.5\n")
        cfg = {"band": 0.1, "levels": 23}
        prereg.lock(base / "LOCK.json", [plan], [code], cfg, label="uae-v2")
        assert prereg.assert_locked(base / "LOCK.json", [plan], [code], {"levels": 23, "band": 0.1})
        try:
            prereg.assert_locked(base / "LOCK.json", [plan], [code], {"band": 0.2, "levels": 23})
            raise AssertionError("changed config was accepted")
        except prereg.GoalpostError:
            pass
        code.write_text("W = 0.6\n")
        try:
            prereg.assert_locked(base / "LOCK.json", [plan], [code], cfg)
            raise AssertionError("changed code was accepted")
        except prereg.GoalpostError:
            pass


# ---------------- calendar ----------------
def test_tabular_hijri_close_to_known_dates():
    known = {(1444, 9, 1): "2023-03-23", (1445, 9, 1): "2024-03-11", (1446, 9, 1): "2025-03-01",
             (1444, 10, 1): "2023-04-21", (1445, 10, 1): "2024-04-10", (1446, 10, 1): "2025-03-30",
             (1444, 12, 10): "2023-06-28", (1445, 12, 10): "2024-06-16", (1446, 12, 10): "2025-06-06"}
    for (y, m, d), g in known.items():
        diff = abs((calendar_features.tabular_hijri_to_gregorian(y, m, d) - pd.Timestamp(g)).days)
        assert diff <= 2, (y, m, d, diff)


def test_weekly_event_features():
    ev = pd.DataFrame({"name": ["ramadan"], "start": ["2024-03-11"], "end": ["2024-04-09"]})
    weeks = pd.date_range("2024-03-02", periods=8, freq="7D")
    f = calendar_features.weekly_event_features(weeks, ev)
    assert f.frac_ramadan.iloc[1] == 0.0 and f.frac_ramadan.iloc[3] == 1.0
    assert abs(f.frac_ramadan.iloc[2] - 6 / 7) < 1e-12          # Mar 10-16: 6 days inside
    assert abs(f.frac_ramadan.iloc[6] - 3 / 7) < 1e-12          # Apr 7-13: ends Apr 9
    assert f.weeks_since_ramadan.iloc[7] == 1
    after = f[f.week_end > pd.Timestamp("2024-04-09")]
    assert (after.weeks_since_ramadan <= 12).all() and after.frac_ramadan.max() < 1
    ev2 = calendar_features.islamic_events(calendar_features.hijri_years_covering(2026, 2030))
    starts = ev2[ev2.name == "ramadan"].start
    assert ((starts.dt.year == 2029) & (starts.dt.month == 1)).any()
    json.dumps(f.astype(str).to_dict())


def test_gbm_multi_source_and_unseen_series():
    world = synth.make_world(n_locations=5, n_seasons=4, seed=11)
    aux = world.assign(source="ili", value=world["value"] * 3.0)        # a second, rescaled source
    main = world.assign(source="nhsn")
    train = pd.concat([aux[aux.season < 3], main[main.season < 3]], ignore_index=True)
    lv5 = np.array([0.05, 0.25, 0.5, 0.75, 0.95])
    model = GlobalQuantileGBM(lv5, horizons=(1, 2), gbm_params={"max_iter": 30}).fit(train)
    ref = world[world.season == 3].date.iloc[15]
    full = pd.concat([aux, main], ignore_index=True)
    p = model.predict(full, ref, target_source="nhsn")
    assert set(p.source) == {"nhsn"} and len(p) == 10
    unseen = world[world.location == "L00"].assign(location="NEW", source="nhsn")
    p_new = model.predict(unseen, ref)
    assert len(p_new) == 2 and np.isfinite(p_new[qcols(lv5)].to_numpy()).all()
    too_short = unseen[unseen.date > ref - pd.Timedelta(weeks=5)]
    assert model.predict(too_short, ref).empty           # not enough history to scale: skipped


def test_card_without_capacity_and_tracker_state():
    q = _normal_q(100.0, 3.0)[0]
    c = card.make_card(100.0, 100.0, q, LV, horizon=1)
    assert c.p_exceed is None and c.action_key == "routine" and c.forecast_key == "likely_stable"
    trk = recalibrate.QuantileTracker(LV)
    trk.update(_normal_q(100.0, 3.0), [150.0], "h1")
    st = trk.state()["h1"]
    assert st["n_updates"] == 1 and len(st["offsets"]) == LV.size and st["offsets"][-1] > 0
