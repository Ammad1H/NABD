"""DEMO data for the NABD app, used ONLY when interface-contract files are missing.

Demo forecasts are built from the REAL cached UAE history with a toy random-walk on the
log-odds scale. They are not NABD model output; the UI shows a DEMO DATA banner whenever
any of these are used.
"""
from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd

QUANTILES = [0.01, 0.025, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5,
             0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.975, 0.99]
UAE_TARGETS = {"flu": "wk flu pos pct sentinel", "rsv": "wk rsv pos pct sentinel"}
_Z = {q: z for q, z in zip(QUANTILES, np.round(
    [-2.326, -1.960, -1.645, -1.282, -1.036, -0.842, -0.674, -0.524, -0.385, -0.253, -0.126, 0.0,
     0.126, 0.253, 0.385, 0.524, 0.674, 0.842, 1.036, 1.282, 1.645, 1.960, 2.326], 3))}


def _logit(p):
    p = np.clip(p, 0.5, 99.5) / 100
    return np.log(p / (1 - p))


def _expit(x):
    return 100 / (1 + np.exp(-x))


def _quantile_rows(ref: dt.date, target: str, last_end: dt.date, centre_logit: float,
                   slope: float, sd_step: float, model: str) -> list[dict]:
    rows = []
    for h in range(1, 5):
        ted = last_end + dt.timedelta(weeks=h)
        centre = centre_logit + slope * h
        sd = sd_step * np.sqrt(h)
        for q in QUANTILES:
            rows.append(dict(reference_date=ref.isoformat(), target=target, horizon=h,
                             target_end_date=ted, location="ARE", output_type="quantile",
                             output_type_id=q, value=round(float(_expit(centre + _Z[q] * sd)), 2),
                             model=model, q=q))
    return rows


def uae_forecasts(observed: pd.DataFrame):
    obs = observed.dropna(subset=["flu"])
    last = obs.iloc[-1]
    last_end = last.week_end
    ref = last_end + dt.timedelta(days=11)
    prim, pers = [], []
    for col, target in UAE_TARGETS.items():
        x = _logit(obs[col].values[-6:])
        slope = float(np.clip((x[-1] - x[-3]) / 2, -0.4, 0.4)) * 0.6
        sd = float(np.std(np.diff(_logit(obs[col].values)))) or 0.3
        prim += _quantile_rows(ref, target, last_end, x[-1], slope, sd, "DEMO-random-walk")
        pers += _quantile_rows(ref, target, last_end, x[-1], 0.0, sd * 1.1, "DEMO-persistence")
    meta = {"model": "DEMO-random-walk (not NABD output)", "reference_date": ref.isoformat()}
    return pd.DataFrame(prim), pd.DataFrame(pers), meta


def persistence_from_observed(observed: pd.DataFrame, primary: pd.DataFrame) -> pd.DataFrame:
    obs = observed.dropna(subset=["flu"])
    last_end = obs.iloc[-1].week_end
    ref = dt.date.fromisoformat(str(primary.reference_date.iloc[0]))
    rows = []
    for col, target in UAE_TARGETS.items():
        sd = float(np.std(np.diff(_logit(obs[col].values)))) or 0.3
        rows += _quantile_rows(ref, target, last_end, _logit(obs[col].values[-1:])[0], 0.0, sd, "persistence")
    return pd.DataFrame(rows)


def us_summary() -> dict:
    return {
        "DEMO": True,
        "note": "DEMO placeholder. The real verdict appears here once results/summary.json exists.",
        "primary_endpoint": "NABD-ensemble vs FluSight-ensemble, relative WIS, non-inferiority margin 1.15",
        "non_inferiority_verdict": "NOT YET COMPUTED (demo)",
        "rel_wis_vs_ensemble": None, "rel_wis_vs_ensemble_ci95": [None, None],
        "rel_wis_vs_baseline": None,
    }


def us_rel_wis_table() -> pd.DataFrame:
    rng = np.random.default_rng(7)
    rows = []
    for season in ["2024/25", "2025/26"]:
        for h in range(4):
            rows.append({"season": season, "horizon": h,
                         "rel_wis_vs_ensemble (DEMO)": round(float(1.0 + rng.normal(0.05, 0.04)), 3),
                         "rel_wis_vs_baseline (DEMO)": round(float(0.8 + rng.normal(0, 0.04)), 3)})
    return pd.DataFrame(rows)


def ablation_table() -> pd.DataFrame:
    return pd.DataFrame({
        "feed_removed": ["none (full)", "ED syndromic (NSSP)", "weather", "school calendar", "testing volume"],
        "rel_wis_vs_full (DEMO)": [1.00, 1.06, 1.01, 1.02, 1.03],
        "mean_80pct_interval_width_change_pct (DEMO)": [0.0, 9.0, 1.5, 2.5, 4.0],
    })


def ledger(observed: pd.DataFrame):
    obs = observed.dropna(subset=["flu"])
    rounds = pd.DataFrame([{"round_file": "DEMO_round.csv", "issued_utc": "DEMO", "sha256": "0" * 64,
                            "recorded_sha256": None, "hash_matches": None,
                            "git_commit_time": None}])
    last = obs.iloc[-3]
    scored = []
    for col, target in UAE_TARGETS.items():
        for k in (1, 2):
            r = obs.iloc[-3 + k]
            v = float(last[col])
            scored.append({"round_file": "DEMO_round.csv", "target": target, "target_week_end": r.week_end,
                           "q10": round(v * 0.7, 2), "median": round(v, 2), "q90": round(v * 1.4, 2),
                           "realised": round(float(r[col]), 2),
                           "inside_80pct_band": bool(v * 0.7 <= r[col] <= v * 1.4)})
    return rounds, pd.DataFrame(scored)
