"""WHO FluNet adapter for the UAE (country code ARE).

Modes:
  --cached  read data/raw/flunet_are.csv (refreshed copy; see data/raw/PROVENANCE.md)
  --fetch   pull from the public WHO xMart OData API (blocked in the cloud sandbox; works locally)

Output: tidy weekly aggregate table validated against adapters.schemas.FLUNET_WEEKLY.
Season convention: ISO week 27 of year Y through ISO week 26 of Y+1 is season Y.
"""
import argparse
import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd

from adapters.schemas import FLUNET_WEEKLY, reject_person_level

ROOT = Path(__file__).resolve().parents[1]
CACHED = ROOT / "data" / "raw" / "flunet_are.csv"
URL = ("https://xmart-api-public.who.int/FLUMART/VIW_FNT?$format=csv"
       "&$filter=COUNTRY_CODE%20eq%20%27ARE%27%20and%20ISO_YEAR%20ge%202020"
       "&$select=ISO_YEAR,ISO_WEEK,ORIGIN_SOURCE,SPEC_PROCESSED_NB,INF_ALL,RSV")


def iso_week_end(y: int, w: int) -> pd.Timestamp:
    return pd.Timestamp(dt.date.fromisocalendar(int(y), int(w), 7))


def _tidy(raw: pd.DataFrame) -> pd.DataFrame:
    reject_person_level(raw, "FluNet")
    d = raw.rename(columns={"ISO_YEAR": "iso_year", "ISO_WEEK": "iso_week", "ORIGIN_SOURCE": "origin",
                            "SPEC_PROCESSED_NB": "specimens", "INF_ALL": "flu_pos", "RSV": "rsv_pos"})
    d = d[["iso_year", "iso_week", "origin", "specimens", "flu_pos", "rsv_pos"]].copy()
    d = d.groupby(["iso_year", "iso_week", "origin"], as_index=False).sum(min_count=1)
    for c in ["specimens", "flu_pos", "rsv_pos"]:
        d[c] = d[c].astype(float)
    d["iso_year"] = d.iso_year.astype(int)
    d["iso_week"] = d.iso_week.astype(int)
    d["origin"] = d.origin.astype(str)
    d["week_end"] = pd.to_datetime([iso_week_end(y, w) for y, w in zip(d.iso_year, d.iso_week)]).astype("datetime64[ns]")
    d["season"] = np.where(d.iso_week >= 27, d.iso_year, d.iso_year - 1).astype(int)
    d = d.sort_values(["origin", "week_end"]).reset_index(drop=True)
    return FLUNET_WEEKLY.validate(d)


def load(mode: str = "cached", path: Path | None = None) -> pd.DataFrame:
    if mode == "fetch":
        raw = pd.read_csv(URL)
    else:
        raw = pd.read_csv(path or CACHED)
    return _tidy(raw)


def sentinel_series(d: pd.DataFrame) -> pd.DataFrame:
    """Sentinel-only weekly series with positivity columns, on a complete weekly index."""
    s = d[d.origin == "SENTINEL"].set_index("week_end").sort_index()
    idx = pd.date_range(s.index.min(), s.index.max(), freq="7D")
    s = s.reindex(idx)
    s.index.name = "week_end"
    s["flu_pct"] = s.flu_pos / s.specimens
    s["rsv_pct"] = s.rsv_pos / s.specimens
    iso = [ts.isocalendar() for ts in s.index]
    s["iso_year"] = [c[0] for c in iso]
    s["iso_week"] = [c[1] for c in iso]
    s["season"] = np.where(s.iso_week >= 27, s.iso_year, s.iso_year - 1)
    return s.drop(columns=["origin"]).reset_index()


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--cached", action="store_true")
    g.add_argument("--fetch", action="store_true")
    ap.add_argument("--save", action="store_true", help="with --fetch: overwrite data/raw/flunet_are.csv")
    a = ap.parse_args()
    mode = "fetch" if a.fetch else "cached"
    if mode == "fetch" and a.save:
        raw = pd.read_csv(URL)
        raw.to_csv(CACHED, index=False)
    d = load(mode)
    last = d[d.origin == "SENTINEL"].iloc[-1]
    print(f"rows={len(d)}  latest sentinel week={last.iso_year}-W{last.iso_week:02d} (ends {last.week_end.date()})")


if __name__ == "__main__":
    main()
