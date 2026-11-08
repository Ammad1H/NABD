"""Verify the scored GCC FluNet file against the official WHO xMart API (run locally; blocked in the build sandbox).

    python -m adapters.gcc_verify            # fetch OMN, QAT, SAU, BHR, KWT from xMart and compare row by row

Exit code 0 = every row of data/raw/flunet_gcc.csv matches the official API (deviation G1 can be fully closed).
Exit code 1 = differences found: the GCC result must be re-scored under the SAME lock (python -m uae.gcc --score),
and the differences logged in docs/DEVIATIONS.md.
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCORED = ROOT / "data" / "raw" / "flunet_gcc.csv"
COUNTRIES = ["OMN", "QAT", "SAU", "BHR", "KWT"]
COLS = ["COUNTRY_CODE", "ISO_YEAR", "ISO_WEEK", "ORIGIN_SOURCE", "SPEC_PROCESSED_NB", "INF_ALL", "RSV"]
KEY = ["COUNTRY_CODE", "ISO_YEAR", "ISO_WEEK", "ORIGIN_SOURCE"]


def official(country: str) -> pd.DataFrame:
    url = ("https://xmart-api-public.who.int/FLUMART/VIW_FNT?$format=csv"
           f"&$select={','.join(COLS)}&$filter=COUNTRY_CODE%20eq%20%27{country}%27")
    return pd.read_csv(url)


def compare(scored: pd.DataFrame, live: pd.DataFrame) -> pd.DataFrame:
    """Rows of `scored` whose values differ from (or are missing in) `live`."""
    m = scored.merge(live, on=KEY, how="left", suffixes=("", "_live"), indicator=True)
    diff = m["_merge"] != "both"
    for c in ["SPEC_PROCESSED_NB", "INF_ALL", "RSV"]:
        a, b = m[c], m[c + "_live"]
        diff |= ~((a == b) | (a.isna() & b.isna()))
    return m[diff]


def main():
    scored = pd.read_csv(SCORED)
    live = pd.concat([official(c) for c in COUNTRIES], ignore_index=True)
    bad = compare(scored, live)
    print(f"scored rows={len(scored)}  official rows={len(live)}  differing/missing={len(bad)}")
    if len(bad):
        print(bad.head(20).to_string(index=False))
        return 1
    print("identical: deviation G1 can be fully closed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
