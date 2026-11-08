"""Input assembly for NABD-UAE-v2 (multi-signal). See docs/PROTOCOL-UAE-v2.md.

Signals, all weekly and aggregate (no person-level data):
  - sentinel positivity (WHO FluNet ARE, SENTINEL): flu and RSV        [clinical, lab]
  - specimens processed, sentinel (testing volume)                     [administrative/process]
  - NON-SENTINEL positivity (WHO FluNet ARE, NONSENTINEL), same pathogen [clinical, second surveillance stream]
  - UAE school winter/spring breaks (MoE/Cabinet calendars, verified)   [administrative, known-future]
  - Ramadan days (tabular Islamic calendar via vendor kit, +/-2 days)   [calendar, known-future]

Information rule (simulated publication lag, declared in the protocol):
  At an origin whose last published SENTINEL week is t, non-sentinel data are used only through t-1
  (FluNet non-sentinel rows have appeared about one week later than sentinel rows; e.g. on 8 Nov 2026
  sentinel ran to 2026-W44, non-sentinel to 2026-W43). Calendar features are known-future by construction.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "nabd_v2_kit"))

from nabd_kit.calendar_features import hijri_years_covering, islamic_events, weekly_event_features  # noqa: E402

from adapters import calendar as cal  # noqa: E402
from adapters import flunet  # noqa: E402
from uae.models import SERIES, logit  # noqa: E402

BREAK_KEYS = ("Winter break", "Spring break")  # mid-terms excluded (not verified for all seasons)


def school_break_weekly(week_end: pd.Series) -> pd.Series:
    """Fraction of Mon-Fri school days inside a verified winter/spring break, per ISO week (ending Sunday).

    Weeks before the first verified calendar row (Dec 2021) and after the last are NaN (unknown, not 0)."""
    c = cal.load()
    c = c[c.verified & c.school_closed & c.event.str.startswith(BREAK_KEYS)]
    first = pd.Timestamp("2021-09-01")   # earliest season with a verified break (2021/22)
    last = pd.Timestamp("2027-07-02")    # end of the last verified school year (2026/27)
    out = []
    for we in pd.to_datetime(week_end):
        if we < first or we > last:
            out.append(np.nan)
            continue
        days = pd.date_range(we - pd.Timedelta(days=6), we - pd.Timedelta(days=2))  # Mon..Fri
        closed = sum(bool(((c.start <= d) & (c.end >= d)).any()) for d in days)
        out.append(closed / 5.0)
    return pd.Series(out, index=week_end.index, name="school_break")


def ramadan_weekly(week_end: pd.Series) -> pd.Series:
    we = pd.to_datetime(week_end)
    ev = islamic_events(hijri_years_covering(int(we.min().year) - 1, int(we.max().year) + 1))
    ev = ev[ev.name == "ramadan"]
    f = weekly_event_features(we.values, ev)
    return pd.Series(f["frac_ramadan"].values, index=week_end.index, name="ramadan")


def nonsentinel_series(raw: pd.DataFrame, week_end: pd.Series) -> pd.DataFrame:
    """Non-sentinel positives/specimens aligned to the sentinel weekly index (NaN where absent)."""
    ns = raw[raw.origin == "NONSENTINEL"].set_index("week_end")[["specimens", "flu_pos", "rsv_pos"]]
    ns = ns.reindex(pd.to_datetime(week_end))
    ns.index = week_end.index
    return ns


def prepare_v2(raw: pd.DataFrame, key: str, extend_weeks: int = 0) -> pd.DataFrame:
    """Frame indexed like uae.models.prepare (sentinel weekly index), with v2 columns added.

    extend_weeks > 0 appends future calendar weeks (no surveillance data) so that known-future
    calendar features exist for the targets of the last origin (used by the live ledger)."""
    s = flunet.sentinel_series(raw)
    if extend_weeks:
        last = s.week_end.max()
        fut = pd.DataFrame({"week_end": [last + pd.Timedelta(weeks=k) for k in range(1, extend_weeks + 1)]})
        iso = [t.isocalendar() for t in fut.week_end]
        fut["iso_year"] = [c[0] for c in iso]
        fut["iso_week"] = [c[1] for c in iso]
        fut["season"] = np.where(fut.iso_week >= 27, fut.iso_year, fut.iso_year - 1)
        s = pd.concat([s, fut], ignore_index=True)
    pos_col = SERIES[key][0]
    pos = s[pos_col]
    d = s[["week_end", "iso_year", "iso_week", "season", "specimens"]].copy()
    d["pos"] = pos
    d["y"] = logit((pos + 0.5) / (s.specimens + 1.0))
    d.loc[pos.isna() | s.specimens.isna(), "y"] = np.nan
    d["logspec"] = np.log(s.specimens.clip(lower=1))
    ns = nonsentinel_series(raw, d.week_end)
    d["ns_pos"] = ns[pos_col].values
    d["ns_spec"] = ns["specimens"].values
    d["z"] = logit((d.ns_pos + 0.5) / (d.ns_spec + 1.0))
    d.loc[d.ns_pos.isna() | d.ns_spec.isna(), "z"] = np.nan
    d["school_break"] = school_break_weekly(d.week_end).values
    d["ramadan"] = ramadan_weekly(d.week_end).values
    d["season"] = d.season.astype(int)
    return d.reset_index(drop=True)
