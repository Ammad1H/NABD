"""Loaders for the NABD app. Read ONLY interface-contract paths (docs/BUILD-SPEC.md v1.1).

Every loader returns (data, is_demo). When a contract file is missing it falls back to
app.demo_data, and the UI must show the DEMO DATA banner whenever is_demo is True.
"""
from __future__ import annotations

import datetime as dt
import glob
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from app import demo_data

ROOT = Path(__file__).resolve().parents[1]
RAW_FLUNET = ROOT / "data" / "raw" / "flunet_are_webfetch.csv"
RESULTS = ROOT / "results"
LEDGER = ROOT / "ledger"

UAE_TARGETS = {"flu": "wk flu pos pct sentinel", "rsv": "wk rsv pos pct sentinel"}
PRIMARY_MODEL_PREFS = ["NABD-ensemble", "NABD-GLM", "NABD-baseline-v0"]
PERSISTENCE_NAMES = ["persistence", "Persistence", "UAE-persistence"]
FLUNET_LAG_DAYS = 11  # documented ~10-11 day publication lag (docs/SPEC.md §2)


def iso_week_end(year: int, week: int) -> dt.date:
    return dt.date.fromisocalendar(int(year), int(week), 7)


# ---------------------------------------------------------------- observed UAE
def load_uae_observed(path: Path = RAW_FLUNET) -> pd.DataFrame:
    """Weekly UAE sentinel positivity (percent) from cached WHO FluNet."""
    d = pd.read_csv(path)
    d = d[d.ORIGIN_SOURCE == "SENTINEL"]
    d = d.groupby(["ISO_YEAR", "ISO_WEEK"], as_index=False)[["SPEC_PROCESSED_NB", "INF_ALL", "RSV"]].sum(min_count=1)
    d = d.sort_values(["ISO_YEAR", "ISO_WEEK"]).reset_index(drop=True)
    d["week_end"] = [iso_week_end(y, w) for y, w in zip(d.ISO_YEAR, d.ISO_WEEK)]
    d["flu"] = 100 * d.INF_ALL / d.SPEC_PROCESSED_NB
    d["rsv"] = 100 * d.RSV / d.SPEC_PROCESSED_NB
    d["specimens"] = d.SPEC_PROCESSED_NB
    return d[["ISO_YEAR", "ISO_WEEK", "week_end", "specimens", "flu", "rsv"]]


def freshness(observed: pd.DataFrame, today: dt.date | None = None) -> dict:
    today = today or dt.datetime.now(dt.timezone.utc).date()
    last = observed.dropna(subset=["flu"]).iloc[-1]
    lag = (today - last.week_end).days
    return {"last_week": f"{int(last.ISO_YEAR)}-W{int(last.ISO_WEEK):02d}",
            "last_week_end": last.week_end.isoformat(), "lag_days": int(lag),
            "expected_lag_days": FLUNET_LAG_DAYS, "stale": lag > FLUNET_LAG_DAYS + 7}


def horizon_label(target_end: dt.date, issue: dt.date) -> str:
    wk = round((target_end - issue).days / 7, 1)
    return "nowcast" if wk <= 0 else f"+{wk:g} wk"


# ---------------------------------------------------------------- UAE forecasts
def _latest_forecast(model_dir: Path) -> tuple[pd.DataFrame | None, str | None]:
    files = sorted(model_dir.glob("*.csv"))
    if not files:
        return None, None
    f = files[-1]
    return pd.read_csv(f), f.stem


def _normalise_quantiles(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "output_type" in df:
        df = df[df.output_type == "quantile"]
    df["q"] = df["output_type_id"].astype(float)
    df["target_end_date"] = pd.to_datetime(df["target_end_date"]).dt.date
    # Contract says percent; guard against fractions written by mistake.
    for t in df.target.unique():
        m = df.target == t
        if "pct" in t and df.loc[m, "value"].max() <= 1.0:
            df.loc[m, "value"] = df.loc[m, "value"] * 100
    return df


def load_uae_forecasts(observed: pd.DataFrame | None = None):
    """Return (primary_df, persistence_df, meta, is_demo). Quantile frames in contract format."""
    observed = observed if observed is not None else load_uae_observed()
    base = RESULTS / "uae" / "forecasts"
    primary = persist = None
    meta: dict = {}
    if base.exists():
        dirs = {p.name: p for p in base.iterdir() if p.is_dir()}
        for name in PRIMARY_MODEL_PREFS + sorted(dirs):
            if name in dirs and name not in PERSISTENCE_NAMES:
                df, ref = _latest_forecast(dirs[name])
                if df is not None:
                    primary = _normalise_quantiles(df)
                    meta.update(model=name, reference_date=ref)
                    break
        for name in PERSISTENCE_NAMES:
            if name in dirs:
                df, _ = _latest_forecast(dirs[name])
                if df is not None:
                    persist = _normalise_quantiles(df)
                    break
    if primary is None:
        p, pe, m = demo_data.uae_forecasts(observed)
        return p, pe, m, True
    if persist is None:
        persist = demo_data.persistence_from_observed(observed, primary)
        meta["persistence_source"] = "computed in-app from last observed value (not a results/ file)"
    return primary, persist, meta, False


# ---------------------------------------------------------------- US proof
def load_us_summary():
    p = RESULTS / "summary.json"
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return json.load(f), False
    return demo_data.us_summary(), True


def load_us_tables() -> tuple[dict[str, pd.DataFrame], bool]:
    tables = {}
    for f in sorted(glob.glob(str(RESULTS / "tables" / "*.csv"))):
        name = Path(f).stem
        if "ablation" in name:
            continue
        try:
            tables[name] = pd.read_csv(f)
        except Exception:  # noqa: BLE001 - a malformed table should not crash the app
            continue
    if tables:
        return tables, False
    return {"rel_wis_by_season_horizon (DEMO)": demo_data.us_rel_wis_table()}, True


def load_ablation() -> tuple[pd.DataFrame, bool]:
    files = sorted(glob.glob(str(RESULTS / "tables" / "ablation*.csv")))
    if files:
        return pd.read_csv(files[-1]), False
    return demo_data.ablation_table(), True


def list_figures() -> list[Path]:
    return sorted((RESULTS / "figures").glob("*.png")) if (RESULTS / "figures").exists() else []


# ---------------------------------------------------------------- ledger
def _git_commit_time(path: Path) -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%cI", "--", str(path)],
                             capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or None
    except Exception:  # noqa: BLE001
        return None


def _normalise_ledger(df: pd.DataFrame) -> pd.DataFrame:
    """Accept the contract format or the legacy ledger_issue.py format."""
    if {"output_type_id", "target_end_date"} <= set(df.columns):
        out = _normalise_quantiles(df)
        out = out.rename(columns={"q": "quantile"})
    else:  # legacy: series,target_week,quantile,value (fractions)
        out = df.copy()
        out["target"] = out.series.map(lambda s: UAE_TARGETS["rsv"] if "rsv" in s else UAE_TARGETS["flu"])
        out["target_end_date"] = out.target_week.map(
            lambda s: iso_week_end(*map(int, s.split("-W"))))
        out["quantile"] = out["quantile"].astype(float)
        out["value"] = out["value"].astype(float) * 100
    return out[["target", "target_end_date", "quantile", "value"]]


def load_ledger(observed: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.DataFrame, bool]:
    """Return (rounds, scored, is_demo).

    rounds: one row per ledger file with recorded vs recomputed hash and git commit time.
    scored: per round x target x week, realised value vs the 10-90% band where observed.
    """
    observed = observed if observed is not None else load_uae_observed()
    files = sorted(f for f in LEDGER.glob("*.csv")) if LEDGER.exists() else []
    if not files:
        r, s = demo_data.ledger(observed)
        return r, s, True
    rounds, scored = [], []
    obs = observed.set_index("week_end")
    for f in files:
        sha_file = f.with_suffix(".sha256")
        recorded = sha_file.read_text().split()[0] if sha_file.exists() else None
        if recorded is None and (LEDGER / "LEDGER.md").exists():
            for line in (LEDGER / "LEDGER.md").read_text().splitlines():
                if f.name in line:
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    recorded = next((p for p in parts if len(p) == 64), None)
        actual = hashlib.sha256(f.read_bytes()).hexdigest()
        rounds.append({"round_file": f.name, "issued_utc": f.name.split("_")[0],
                       "sha256": actual, "recorded_sha256": recorded,
                       "hash_matches": (recorded == actual) if recorded else None,
                       "git_commit_time": _git_commit_time(f)})
        try:
            led = _normalise_ledger(pd.read_csv(f))
        except Exception:  # noqa: BLE001
            continue
        for (target, ted), g in led.groupby(["target", "target_end_date"]):
            qv = dict(zip(g["quantile"].round(3), g["value"]))
            lo, med, hi = qv.get(0.1), qv.get(0.5), qv.get(0.9)
            col = "rsv" if "rsv" in target else "flu"
            realised = obs[col].get(ted) if ted in obs.index else np.nan
            inside = None if pd.isna(realised) or lo is None else bool(lo <= realised <= hi)
            scored.append({"round_file": f.name, "target": target, "target_week_end": ted,
                           "q10": lo, "median": med, "q90": hi,
                           "realised": None if pd.isna(realised) else round(float(realised), 2),
                           "inside_80pct_band": inside})
    return pd.DataFrame(rounds), pd.DataFrame(scored), False
