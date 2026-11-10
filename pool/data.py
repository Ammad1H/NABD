"""Streamed, filtered download of WHO FluNet rows from the pinned GitHub mirror of WHO's full export.

The export is read from the network stream and filtered in memory; only rows for the requested countries
are written. Held-out countries can be requested only after lock #2 verifies (enforced here).

  python3 -m pool.data --stage dev       # after lock #1: development countries -> data/raw/flunet_pool_dev.csv
  python3 -m pool.data --stage held      # after lock #2: held-out countries   -> data/raw/flunet_pool_held.csv
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import subprocess
import sys
from pathlib import Path

from pool import config as C
from pool.locks import check_lock1, check_lock2

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
EXPORT_PATH = "historical_data/VIW_FNT_20261003.csv"
FILES = {"dev": RAW / "flunet_pool_dev.csv", "held": RAW / "flunet_pool_held.csv"}


class HeldOutGuard(RuntimeError):
    pass


def allowed_countries(stage: str) -> list[str]:
    """The ONLY place that maps a stage to countries. 'held' requires lock #2."""
    if stage == "dev":
        check_lock1()
        return list(C.DEV)
    if stage == "held":
        try:
            check_lock2()
        except Exception as e:  # missing or broken lock
            raise HeldOutGuard(f"held-out rows may not be extracted before lock #2 verifies: {e}") from e
        return list(C.HELD)
    raise ValueError(stage)


def stream_filter(countries, out_path: Path, lines=None) -> dict:
    """Filter the export stream to `countries`. `lines` (an iterable of text lines) is for tests."""
    keep = set(countries)
    h = hashlib.sha256()
    proc = None
    if lines is None:
        url = C.MIRROR_URL.format(path=EXPORT_PATH)
        proc = subprocess.Popen(["curl", "-sS", "-L", "--fail", url], stdout=subprocess.PIPE)
        raw = proc.stdout

        def gen():
            for b in raw:
                h.update(b)
                yield b.decode("utf-8", errors="replace")
        lines = gen()
    rd = csv.DictReader(lines)
    n_in = n_out = 0
    with open(out_path, "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=C.COLUMNS)
        wr.writeheader()
        for row in rd:
            n_in += 1
            if row.get("COUNTRY_CODE") in keep and int(row.get("ISO_YEAR") or 0) >= C.MIN_YEAR:
                wr.writerow({k: row.get(k, "") for k in C.COLUMNS})
                n_out += 1
    if proc is not None:
        if proc.wait() != 0:
            raise RuntimeError("download failed")
    return dict(rows_in=n_in, rows_out=n_out, export_sha256=h.hexdigest())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["dev", "held"], required=True)
    a = ap.parse_args()
    countries = allowed_countries(a.stage)
    out = FILES[a.stage]
    info = stream_filter(countries, out)
    if not info["export_sha256"].startswith(C.EXPORT_SHA256_PREFIX):
        out.unlink()
        raise RuntimeError(f"export hash {info['export_sha256'][:16]} does not match the pinned export")
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    out.with_suffix(".sha256").write_text(f"{sha}  {out.name}\n")
    print(info, "file sha256", sha)


if __name__ == "__main__":
    main()
