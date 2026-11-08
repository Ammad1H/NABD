"""UAE school calendar / holidays as a known-future covariate.

Source table: data/raw/uae_calendar.csv (hand-entered). 2026/27 rows VERIFIED from Gulf News' report of the
Ministry of Education unified calendar:
  https://gulfnews.com/living-in-uae/education/uae-school-calendar-2026-27-term-dates-and-holidays-1.500637553
Earlier winter-break rows are APPROXIMATE (verified=False) and must not be presented as fact.
There is no fetch mode: calendars are announced documents, re-entered by hand when updated.
"""
from pathlib import Path

import pandas as pd

from adapters.schemas import CALENDAR, reject_person_level

ROOT = Path(__file__).resolve().parents[1]
CACHED = ROOT / "data" / "raw" / "uae_calendar.csv"


def load(mode: str = "cached") -> pd.DataFrame:
    c = pd.read_csv(CACHED, parse_dates=["start", "end"])
    reject_person_level(c, "calendar")
    for col in ["start", "end"]:
        c[col] = c[col].astype("datetime64[ns]")
    c["school_closed"] = c.school_closed.astype(bool)
    c["verified"] = c.verified.astype(bool)
    return CALENDAR.validate(c)


def weekly_school_closed(weeks: pd.DatetimeIndex, verified_only: bool = True) -> pd.Series:
    """Fraction of school days (Mon-Fri) closed in each ISO week ending on the given Sundays."""
    c = load()
    if verified_only:
        c = c[c.verified]
    c = c[c.school_closed]
    out = []
    for we in weeks:
        days = pd.date_range(we - pd.Timedelta(days=6), we - pd.Timedelta(days=2))  # Mon..Fri
        closed = sum(any((c.start <= d) & (c.end >= d)) for d in days)
        out.append(closed / 5.0)
    return pd.Series(out, index=weeks, name="school_closed_frac")


if __name__ == "__main__":
    print(load())
