"""Weekly calendar features (Ramadan, Eid, school terms and holidays).

Scheduled holidays are announced before they happen, so using them at forecast
time is not leakage. Official UAE dates for Ramadan and the Eids follow moon
sighting and can differ by a day or two from any computed calendar: for the
locked model, replace `islamic_events` output with the official dates.

`islamic_events` uses the arithmetic (tabular) Islamic calendar, accurate to
about +/-2 days against Umm al-Qura dates. Good enough for weekly features and
for spotting the Ramadan calendar collision; not good enough to publish dates.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

_ISLAMIC_EPOCH_JD = 1948439.5  # tabular (civil) epoch, as in Fourmilab's converter


def tabular_hijri_to_gregorian(year: int, month: int, day: int) -> pd.Timestamp:
    jd = (day + math.ceil(29.5 * (month - 1)) + (year - 1) * 354
          + math.floor((3 + 11 * year) / 30) + _ISLAMIC_EPOCH_JD - 1)
    return pd.to_datetime(jd, unit="D", origin="julian").normalize()


def hijri_years_covering(first_greg_year: int, last_greg_year: int) -> list[int]:
    lo = int((first_greg_year - 622) * 33 / 32) - 1
    hi = int((last_greg_year - 622) * 33 / 32) + 2
    return list(range(lo, hi + 1))


def islamic_events(hijri_years, eid_fitr_days: int = 3, eid_adha_days: int = 4) -> pd.DataFrame:
    """Approximate Gregorian spans for Ramadan, Eid al-Fitr and Eid al-Adha."""
    rows = []
    for y in hijri_years:
        r0 = tabular_hijri_to_gregorian(y, 9, 1)
        f0 = tabular_hijri_to_gregorian(y, 10, 1)
        a0 = tabular_hijri_to_gregorian(y, 12, 10)
        rows.append({"name": "ramadan", "start": r0, "end": f0 - pd.Timedelta(days=1), "hijri_year": y})
        rows.append({"name": "eid_al_fitr", "start": f0,
                     "end": f0 + pd.Timedelta(days=eid_fitr_days - 1), "hijri_year": y})
        rows.append({"name": "eid_al_adha", "start": a0,
                     "end": a0 + pd.Timedelta(days=eid_adha_days - 1), "hijri_year": y})
    return pd.DataFrame(rows)


def weekly_event_features(week_end_dates, events: pd.DataFrame, week_days: int = 7,
                          max_weeks_since: int = 12) -> pd.DataFrame:
    """Per week ending on each date: share of days inside each named event, and
    whole weeks since the most recent end of that event (capped).

    events: columns name, start, end (inclusive dates).
    """
    weeks = pd.to_datetime(pd.Series(week_end_dates)).dt.normalize().reset_index(drop=True)
    ev = events.copy()
    ev["start"] = pd.to_datetime(ev["start"]).dt.normalize()
    ev["end"] = pd.to_datetime(ev["end"]).dt.normalize()
    out = pd.DataFrame({"week_end": weeks})
    for name, g in ev.groupby("name", sort=True):
        starts = g["start"].to_numpy()
        ends = g["end"].to_numpy()
        frac, since = [], []
        for we in weeks:
            days = pd.date_range(we - pd.Timedelta(days=week_days - 1), we, freq="D").to_numpy()
            inside = ((days[:, None] >= starts[None, :]) & (days[:, None] <= ends[None, :])).any(axis=1)
            frac.append(float(inside.mean()))
            ended = ends[ends <= np.datetime64(we)]
            if ended.size:
                gap_days = (np.datetime64(we) - ended.max()) / np.timedelta64(1, "D")
                since.append(int(min(gap_days // 7, max_weeks_since)))
            else:
                since.append(max_weeks_since)
        out[f"frac_{name}"] = frac
        out[f"weeks_since_{name}"] = since
    return out
