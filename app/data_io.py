"""Loaders for the NABD app. Read ONLY interface-contract paths (docs/BUILD-SPEC.md v1.1).

Every loader returns (data, is_demo). When a contract file is missing it falls back to
app.demo_data, and the UI must show the DEMO DATA banner whenever is_demo is True.
"""
from __future__ import annotations

import datetime as dt
import glob
import hashlib
import json
import re
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from app import demo_data

ROOT = Path(__file__).resolve().parents[1]
RAW_FLUNET_CANDIDATES = [ROOT / "data" / "raw" / "flunet_are.csv",            # refreshed by the data workstream
                         ROOT / "data" / "raw" / "flunet_are_webfetch.csv"]    # original 5 Nov copy
RAW_FLUNET = next((p for p in RAW_FLUNET_CANDIDATES if p.exists()), RAW_FLUNET_CANDIDATES[-1])
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


def horizon_weeks(target_end: dt.date, issue: dt.date) -> float:
    """Weeks from the issue date to the MIDDLE of the target week, rounded to 0.5.

    A target week ending 7 days after issue is mostly in the future: its midpoint is +0.5 wk.
    This matches the issue-relative horizons in docs/SPEC.md §5.1 (nowcast, +0.5, +1.5, +2.5 wk).
    """
    mid = pd.Timestamp(target_end) - pd.Timedelta(days=3.5)
    wk = (mid - pd.Timestamp(issue)).total_seconds() / (7 * 86400)
    return round(wk * 2) / 2


def horizon_label(target_end: dt.date, issue: dt.date) -> str:
    wk = horizon_weeks(target_end, issue)
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


ROUND_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{4}Z)_(.+)\.csv$")


def ledger_round_files() -> list[Path]:
    """Ledger forecast rounds only (`<UTC>_<model>.csv`), not scores or helper files."""
    if not LEDGER.exists():
        return []
    return sorted(f for f in LEDGER.glob("*.csv") if ROUND_RE.match(f.name))


def _round_issue_date(stamp: str) -> dt.date:
    return dt.date.fromisoformat(stamp[:10])


def load_uae_forecasts(observed: pd.DataFrame | None = None):
    """Return (primary_df, persistence_df, meta, is_demo). Quantile frames in contract format.

    Source priority for the weekly card:
      1. the latest LIVE ledger round (ledger/<UTC>_<model>.csv); issue date = round timestamp;
      2. the latest retrospective forecast in results/uae/forecasts/<model>/ (labelled retrospective);
      3. DEMO data.
    meta["issue_date"] is the date horizons are measured from.
    """
    observed = observed if observed is not None else load_uae_observed()
    meta: dict = {}
    primary = persist = None
    rounds = ledger_round_files()
    if rounds:
        by_stamp: dict[str, dict[str, Path]] = {}
        for f in rounds:
            stamp, model = ROUND_RE.match(f.name).groups()
            by_stamp.setdefault(stamp, {})[model] = f
        for stamp in sorted(by_stamp, reverse=True):
            models = by_stamp[stamp]
            name = next((m for m in PRIMARY_MODEL_PREFS if m in models), None) or next(
                (m for m in sorted(models) if m not in PERSISTENCE_NAMES), None)
            if name is None:
                continue
            primary = _normalise_quantiles(pd.read_csv(models[name]))
            pname = next((m for m in PERSISTENCE_NAMES if m in models), None)
            if pname:
                persist = _normalise_quantiles(pd.read_csv(models[pname]))
            sha = hashlib.sha256(models[name].read_bytes()).hexdigest()
            meta.update(model=name, source="live ledger round", round_file=models[name].name,
                        sha256=sha, reference_date=str(primary.reference_date.iloc[0]),
                        issue_date=_round_issue_date(stamp).isoformat())
            break
    base = RESULTS / "uae" / "forecasts"
    if primary is None and base.exists():
        dirs = {p.name: p for p in base.iterdir() if p.is_dir()}
        for name in PRIMARY_MODEL_PREFS + sorted(dirs):
            if name in dirs and name not in PERSISTENCE_NAMES:
                df, ref = _latest_forecast(dirs[name])
                if df is not None:
                    primary = _normalise_quantiles(df)
                    meta.update(model=name, source="retrospective (latest file in results/uae/forecasts)",
                                reference_date=ref, issue_date=ref)
                    for pn in PERSISTENCE_NAMES:
                        if pn in dirs and (dirs[pn] / f"{ref}.csv").exists():
                            persist = _normalise_quantiles(pd.read_csv(dirs[pn] / f"{ref}.csv"))
                    break
    if primary is None:
        p, pe, m = demo_data.uae_forecasts(observed)
        m["issue_date"] = m["reference_date"]
        m["source"] = "DEMO"
        return p, pe, m, True
    if persist is None:
        persist = demo_data.persistence_from_observed(observed, primary)
        meta["persistence_source"] = "computed in-app from last observed value (not a results/ file)"
    return primary, persist, meta, False


def load_uae_summary():
    p = RESULTS / "uae" / "summary.json"
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return None


def load_uae_tables() -> dict[str, pd.DataFrame]:
    out = {}
    for f in sorted(glob.glob(str(RESULTS / "uae" / "tables" / "*.csv"))):
        try:
            out[Path(f).stem] = pd.read_csv(f)
        except Exception:  # noqa: BLE001
            continue
    return out


# ---------------------------------------------------------------- US proof
def load_us_summary() -> dict | None:
    """results/summary.json, or None if not yet computed (never demo numbers)."""
    return _read_json(RESULTS / "summary.json")


def load_us_tables() -> dict[str, pd.DataFrame]:
    """All CSV tables in results/tables/ (empty dict = not yet computed; never demo numbers)."""
    tables = {}
    for f in sorted(glob.glob(str(RESULTS / "tables" / "*.csv"))):
        name = Path(f).stem
        try:
            tables[name] = pd.read_csv(f)
        except Exception:  # noqa: BLE001 - a malformed table should not crash the app
            continue
    return tables


def _read_csv(path: Path) -> pd.DataFrame | None:
    try:
        return pd.read_csv(path) if path.exists() else None
    except Exception:  # noqa: BLE001
        return None


def _read_json(path: Path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return None


def load_uae_ablation() -> pd.DataFrame | None:
    """results/uae/tables/ablation.csv (contract v1.3: feed, metric, full, without, delta). None = not computed."""
    return _read_csv(RESULTS / "uae" / "tables" / "ablation.csv")


def load_uae_explain(issue_date: str | None = None) -> tuple[dict[str, pd.DataFrame], str | None]:
    """Per-signal contributions (contract v1.3: results/uae/explain/<issue_date>_<target>.csv,
    columns horizon, feature, value, contribution, unit).

    Returns ({'rsv'|'flu': frame}, issue_date_used). Prefers the card's issue date, else the latest.
    """
    d = RESULTS / "uae" / "explain"
    if not d.exists():
        return {}, None
    files = sorted(d.glob("*.csv"))
    dates = sorted({f.name[:10] for f in files if re.match(r"\d{4}-\d{2}-\d{2}", f.name)})
    if not dates:
        return {}, None
    use = issue_date if issue_date in dates else dates[-1]
    out = {}
    for f in files:
        if not f.name.startswith(use):
            continue
        key = "rsv" if "rsv" in f.name.lower() else "flu" if "flu" in f.name.lower() else None
        df = _read_csv(f)
        if key and df is not None:
            out[key] = df
    return out, use


def load_alerts() -> dict[str, pd.DataFrame]:
    """US alert metrics (results/tables/alerts_us*.csv, latency/dropout) and UAE alert metrics
    (results/uae/tables/alert*.csv). Empty dict entries are simply absent."""
    out = {}
    for f in sorted((RESULTS / "tables").glob("*.csv")) if (RESULTS / "tables").exists() else []:
        if f.stem.startswith(("alerts_us", "latency_us", "dropout_us")):
            df = _read_csv(f)
            if df is not None:
                out["US " + f.stem] = df
    ut = RESULTS / "uae" / "tables"
    for f in sorted(ut.glob("alert*.csv")) if ut.exists() else []:
        df = _read_csv(f)
        if df is not None:
            out["UAE " + f.stem] = df
    return out


def load_league() -> tuple[dict[str, pd.DataFrame], list[Path]]:
    """League table vs individual CDC FluSight hub models (DEVIATIONS D7), if computed."""
    tabs = {}
    t = RESULTS / "tables"
    for f in sorted(t.glob("league*.csv")) if t.exists() else []:
        df = _read_csv(f)
        if df is not None:
            tabs[f.stem] = df
    figs = sorted((RESULTS / "figures").glob("league*.png")) if (RESULTS / "figures").exists() else []
    return tabs, figs


def load_gcc() -> tuple[dict | None, dict[str, pd.DataFrame], list[Path]]:
    """GCC out-of-sample test (BUILD-SPEC G12): results/gcc/{summary.json, tables/*.csv, figures/*.png}."""
    g = RESULTS / "gcc"
    summary = _read_json(g / "summary.json")
    tabs = {}
    for f in sorted((g / "tables").glob("*.csv")) if (g / "tables").exists() else []:
        df = _read_csv(f)
        if df is not None:
            tabs[f.stem] = df
    figs = sorted((g / "figures").glob("*.png")) if (g / "figures").exists() else []
    if not figs and g.exists():
        figs = sorted(g.glob("*.png"))
    return summary, tabs, figs


def us_verdict(summary: dict | None) -> tuple[str | None, str | None]:
    """(verdict, text) shown verbatim: summary.json `primary_verdict`/`primary_text` (contract v1.3),
    falling back to primary.non_inferiority from the frozen run."""
    if not summary:
        return None, None
    v = summary.get("primary_verdict") or (summary.get("primary") or {}).get("non_inferiority")
    txt = summary.get("primary_text")
    if txt is None and isinstance(summary.get("primary"), dict):
        p = summary["primary"]
        ci = p.get("ci95") or [None, None]
        if p.get("rel_wis") is not None:
            txt = (f"{p.get('comparison', 'NABD-ensemble / FluSight-ensemble')}: relative WIS {p['rel_wis']:.3f} "
                   f"(95% CI {ci[0]:.3f}–{ci[1]:.3f}); non-inferiority margin {p.get('margin')}.")
    return v, txt


def list_figures(sub: str = "") -> list[Path]:
    d = RESULTS / sub / "figures" if sub else RESULTS / "figures"
    return sorted(d.glob("*.png")) if d.exists() else []


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
    files = ledger_round_files()
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
        stamp, model = ROUND_RE.match(f.name).groups()
        rounds.append({"round_file": f.name, "model": model, "issued_utc": stamp,
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
