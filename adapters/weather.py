"""Abu Dhabi weather adapter (NOAA GHCN-Daily station AE000041217, Abu Dhabi Intl).

Modes:
  --fetch   NOAA NCEI Access Data Service (daily-summaries) -> weekly means. Run locally; the cloud
            sandbox blocks NOAA hosts (checked 8 Nov 2026: ncei.noaa.gov, the noaa-ghcn-pds S3 mirror,
            bulk.meteostat.net and open-meteo all blocked; the NCEI API via WebFetch returned 0 rows
            for this station for 2025-26, so the station's recent coverage itself is UNVERIFIED).
  --cached  data/raw/weather_ad_weekly.csv if present (real=True only if produced by --fetch).

If no real file exists, load() returns a PLACEHOLDER climatology with real=False. Placeholder rows
are NOT REAL and must never be used in scored results; uae/ models do not use weather at all in R1.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from adapters.schemas import WEATHER_WEEKLY, reject_person_level

ROOT = Path(__file__).resolve().parents[1]
CACHED = ROOT / "data" / "raw" / "weather_ad_weekly.csv"
NCEI = ("https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries"
        "&stations=AE000041217&startDate={start}&endDate={end}&dataTypes=TAVG,TMAX&format=csv&units=metric")


def _weekly(daily: pd.DataFrame) -> pd.DataFrame:
    reject_person_level(daily, "weather")
    daily = daily.rename(columns=str.upper)
    daily["DATE"] = pd.to_datetime(daily["DATE"])
    w = daily.set_index("DATE")[["TAVG", "TMAX"]].astype(float).resample("W-SUN").mean()
    out = pd.DataFrame({"week_end": w.index.astype("datetime64[ns]"), "tavg_c": w.TAVG.values,
                        "tmax_c": w.TMAX.values, "real": True})
    return WEATHER_WEEKLY.validate(out)


def placeholder(start="2022-01-02", end="2027-06-27") -> pd.DataFrame:
    """Smooth sinusoidal climatology, labelled NOT REAL (real=False). For UI layout only."""
    idx = pd.date_range(start, end, freq="W-SUN")
    doy = idx.day_of_year.values
    tavg = 28.0 + 7.5 * np.sin(2 * np.pi * (doy - 110) / 365.25)
    out = pd.DataFrame({"week_end": idx.astype("datetime64[ns]"), "tavg_c": tavg, "tmax_c": tavg + 6.0, "real": False})
    return WEATHER_WEEKLY.validate(out)


def load(mode: str = "cached") -> pd.DataFrame:
    if mode == "fetch":
        today = pd.Timestamp.today().date()
        daily = pd.read_csv(NCEI.format(start="2020-01-01", end=today))
        w = _weekly(daily)
        w.to_csv(CACHED, index=False)
        return w
    if CACHED.exists():
        w = pd.read_csv(CACHED, parse_dates=["week_end"])
        w["week_end"] = w.week_end.astype("datetime64[ns]")
        return WEATHER_WEEKLY.validate(w)
    return placeholder()


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--cached", action="store_true")
    g.add_argument("--fetch", action="store_true")
    a = ap.parse_args()
    w = load("fetch" if a.fetch else "cached")
    print(f"rows={len(w)} real={bool(w.real.all())} range={w.week_end.min().date()}..{w.week_end.max().date()}")


if __name__ == "__main__":
    main()
