"""Pilot data connector (R3-3): aggregate hospital / DoH counts for a 12-week shadow pilot.

What a partner shares is ONE table of aggregate counts (docs/PILOT-DATA-SPEC.md). This module
enforces, before anything reaches a model:

  1. no person-level field (adapters.schemas.reject_person_level, same guard as every NABD input);
  2. a strict schema (pandera): only the allowed aggregate columns and vocabularies, no free text;
  3. small-cell suppression: any count 1..K-1 (K = 10 by default) is suppressed; and
  4. complementary suppression: within each (period, facility, measure) group, if exactly one
     age-band cell is suppressed, the next-smallest non-zero cell is also suppressed, so a
     suppressed value cannot be recovered by subtracting from the all-ages total.

Suppressed counts become NaN with suppressed=True; they are never imputed back to a number.
`load_pilot(path)` returns the cleaned table; `to_series()` turns it into the weekly series a model
uses. Nothing here touches the frozen v1/v2 models.

CLI:
  python -m adapters.pilot validate data/pilot/SYNTHETIC_pilot_example.csv
  python -m adapters.pilot synthetic   # (re)writes the clearly-labelled synthetic example
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pandera.pandas as pa

from adapters.schemas import reject_person_level

ROOT = Path(__file__).resolve().parents[1]
K_MIN = 10

AGE_BANDS = ["0-5m", "6-23m", "2-4y", "5-14y", "15-49y", "50-64y", "65+y", "all"]
MEASURES = ["ed_visits_ari", "ed_visits_ili", "admissions_ari", "admissions_rsv", "admissions_flu",
            "lab_tests_rsv", "lab_pos_rsv", "lab_tests_flu", "lab_pos_flu", "occupied_beds_paeds_resp"]
GRANULARITY = ["day", "week"]

PILOT_SCHEMA = pa.DataFrameSchema(
    {
        "period_start": pa.Column("datetime64[ns]"),
        "granularity": pa.Column(str, pa.Check.isin(GRANULARITY)),
        "facility_code": pa.Column(str, pa.Check.str_matches(r"^[A-Z0-9_]{2,16}$")),   # opaque partner code
        "region": pa.Column(str, pa.Check.isin(["ABU_DHABI", "AL_AIN", "AL_DHAFRA", "ALL"])),
        "measure": pa.Column(str, pa.Check.isin(MEASURES)),
        "age_band": pa.Column(str, pa.Check.isin(AGE_BANDS)),
        "count": pa.Column(float, pa.Check.ge(0), nullable=True),
        "suppressed": pa.Column(bool),
        "synthetic": pa.Column(bool),
    },
    strict=True,
    unique=["period_start", "granularity", "facility_code", "region", "measure", "age_band"],
)


class AggregationError(ValueError):
    """Raised when a shared table is not an aggregate of the declared shape."""


def suppress(df: pd.DataFrame, k: int = K_MIN) -> pd.DataFrame:
    """Primary (1..k-1) and complementary suppression across age bands. Returns a copy."""
    d = df.copy()
    if "suppressed" not in d:
        d["suppressed"] = False
    small = d["count"].notna() & (d["count"] > 0) & (d["count"] < k)
    d.loc[small, "suppressed"] = True
    keys = ["period_start", "granularity", "facility_code", "region", "measure"]
    for _, g in d[d.age_band != "all"].groupby(keys):  # noqa: B007 (key tuple used below)
        sup = g[g.suppressed]
        if len(sup) == 1:
            # suppress the next-smallest released age band (prefer non-zero; else any, incl. a zero);
            # if there is no other band, suppress the all-ages total instead.
            rest = g[~g.suppressed].sort_values("count")
            cand = rest[rest["count"] > 0]
            cand = cand if len(cand) else rest
            if len(cand):
                d.loc[cand.index[0], "suppressed"] = True
            else:
                tot = d[(d.age_band == "all")]
                for kk, vv in zip(keys, _):
                    tot = tot[tot[kk] == vv]
                d.loc[tot.index, "suppressed"] = True
    d.loc[d.suppressed, "count"] = np.nan
    return d


def check_suppressed(df: pd.DataFrame, k: int = K_MIN) -> None:
    """Assert no released count is in 1..k-1 and no group has exactly one suppressed age band."""
    released = df[~df.suppressed]
    bad = released[(released["count"] > 0) & (released["count"] < k)]
    if len(bad):
        raise AggregationError(f"{len(bad)} released cell(s) below k={k}")
    keys = ["period_start", "granularity", "facility_code", "region", "measure"]
    sub = df[df.age_band != "all"]
    singles = sub.groupby(keys).suppressed.sum()
    if (singles == 1).any():
        raise AggregationError("a group has exactly one suppressed age band (complementary suppression missing)")


def load_pilot(path_or_df, k: int = K_MIN, apply_suppression: bool = True) -> pd.DataFrame:
    df = pd.read_csv(path_or_df) if not isinstance(path_or_df, pd.DataFrame) else path_or_df.copy()
    reject_person_level(df, source="pilot")
    if "period_start" in df:
        df["period_start"] = pd.to_datetime(df["period_start"])
    for c in ("suppressed", "synthetic"):
        if c in df:
            df[c] = df[c].astype(bool)
    if "count" in df:
        df["count"] = df["count"].astype(float)
    if apply_suppression:
        df = suppress(df, k)
    df = PILOT_SCHEMA.validate(df)
    check_suppressed(df, k)
    return df


def to_series(df: pd.DataFrame, measure: str, facility: str | None = None, age_band: str = "all") -> pd.DataFrame:
    """Weekly series (week_end Sunday) for one measure; days are summed to ISO weeks.
    Weeks containing a suppressed cell are NaN (never imputed)."""
    d = df[(df.measure == measure) & (df.age_band == age_band)]
    if facility:
        d = d[d.facility_code == facility]
    d = d.assign(week_end=d.period_start + pd.to_timedelta((6 - d.period_start.dt.weekday) % 7, unit="D"))
    g = d.groupby("week_end").agg(count=("count", lambda x: x.sum(min_count=len(x))),
                                  any_suppressed=("suppressed", "any")).reset_index()
    g.loc[g.any_suppressed, "count"] = np.nan
    return g


def make_synthetic(seed: int = 7, weeks: int = 26, granularity: str = "week") -> pd.DataFrame:
    """A clearly labelled SYNTHETIC example: one fictional facility, daily counts, invented shapes.
    Not derived from any real hospital. Used only to exercise the connector and tests."""
    rng = np.random.default_rng(seed)
    days = pd.date_range("2026-07-06", periods=7 * weeks, freq="D")
    t = np.arange(len(days))
    rows = []
    shares = {"0-5m": .12, "6-23m": .22, "2-4y": .2, "5-14y": .18, "15-49y": .14, "50-64y": .07, "65+y": .07}
    for measure, base, peak in [("ed_visits_ari", 60, 140), ("admissions_rsv", 3, 14), ("admissions_flu", 2, 9)]:
        lam_all = base + peak * np.exp(-0.5 * ((t - 120) / 18) ** 2)
        for i, day in enumerate(days):
            total = 0
            for band, s in shares.items():
                c = int(rng.poisson(lam_all[i] * s))
                total += c
                rows.append([day, "day", "SYN_HOSP_A", "ABU_DHABI", measure, band, float(c), False, True])
            rows.append([day, "day", "SYN_HOSP_A", "ABU_DHABI", measure, "all", float(total), False, True])
    df = pd.DataFrame(rows, columns=["period_start", "granularity", "facility_code", "region", "measure",
                                     "age_band", "count", "suppressed", "synthetic"])
    if granularity == "week":  # weekly aggregates (Monday start) keep low-count measures above k
        df["period_start"] = df.period_start - pd.to_timedelta(df.period_start.dt.weekday, unit="D")
        df = (df.groupby(["period_start", "facility_code", "region", "measure", "age_band"], as_index=False)
                .agg(count=("count", "sum")))
        df["granularity"], df["suppressed"], df["synthetic"] = "week", False, True
        df = df[["period_start", "granularity", "facility_code", "region", "measure", "age_band", "count",
                 "suppressed", "synthetic"]]
    return df


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m adapters.pilot")
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate")
    v.add_argument("path")
    v.add_argument("--k", type=int, default=K_MIN)
    sub.add_parser("synthetic")
    a = ap.parse_args(argv)
    if a.cmd == "synthetic":
        out = ROOT / "data" / "pilot" / "SYNTHETIC_pilot_example.csv"
        out.parent.mkdir(parents=True, exist_ok=True)
        make_synthetic().to_csv(out, index=False)
        print(f"wrote {out.relative_to(ROOT)} (SYNTHETIC, not real data)")
        return 0
    df = load_pilot(a.path, k=a.k)
    print(f"OK: {len(df)} rows, {int(df.suppressed.sum())} cells suppressed (k={a.k}), "
          f"synthetic={bool(df.synthetic.all())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
