"""Score past ledger rounds against FluNet weeks published since issue.

Usage:  python3 -m ledger.score --cached     (or --fetch locally to pull the newest weeks first)
Writes ledger/scores.csv and ledger/SCOREBOARD.md. Only rows whose target week is now published are scored.
Integrity check: every ledger CSV's SHA-256 is recomputed and compared with its .sha256 file; a mismatch is
reported and that file is excluded (a tampered round is never scored).
"""
import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

from adapters import flunet
from uae.models import QUANTILES
from uae.scoring import wis, covered

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "ledger"
TARGET_COL = {"wk flu pos pct sentinel": "flu_pos", "wk rsv pos pct sentinel": "rsv_pos"}


def verify(csv: Path) -> bool:
    sha = csv.with_suffix(".sha256")
    if not sha.exists():
        return False
    return sha.read_text().split()[0] == hashlib.sha256(csv.read_bytes()).hexdigest()


def score(mode="cached"):
    s = flunet.sentinel_series(flunet.load(mode)).set_index("week_end")
    rows, bad = [], []
    for csv in sorted(LEDGER.glob("*.csv")):
        if csv.name == "scores.csv":
            continue
        if not verify(csv):
            bad.append(csv.name)
            continue
        f = pd.read_csv(csv)
        for (tgt, te), g in f.groupby(["target", "target_end_date"]):
            t = pd.Timestamp(te)
            if t not in s.index or np.isnan(s.loc[t, TARGET_COL[tgt]]) or np.isnan(s.loc[t, "specimens"]):
                continue
            y = s.loc[t, TARGET_COL[tgt]] / s.loc[t, "specimens"] * 100
            g = g.sort_values("output_type_id")
            q, v = g.output_type_id.values, g.value.values
            rows.append(dict(file=csv.name, model=g.model.iloc[0], target=tgt, horizon=int(g.horizon.iloc[0]),
                             target_end_date=te, observed=round(y, 2), median=float(v[np.argmin(abs(q - 0.5))]),
                             wis=round(wis(q, v, y), 3), in50=covered(q, v, y, 0.5), in95=covered(q, v, y, 0.95)))
    sc = pd.DataFrame(rows)
    sc.to_csv(LEDGER / "scores.csv", index=False)
    md = ["# NABD ledger scoreboard", "", f"Scored rows: {len(sc)}. Tampered/unhashed files excluded: {bad or 'none'}.", ""]
    if len(sc):
        md.append(sc.to_markdown(index=False))
    else:
        md.append("No target week of any issued round has been published yet.")
    (LEDGER / "SCOREBOARD.md").write_text("\n".join(md) + "\n")
    return sc, bad


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--cached", action="store_true")
    g.add_argument("--fetch", action="store_true")
    a = ap.parse_args()
    sc, bad = score("fetch" if a.fetch else "cached")
    print(f"scored rows={len(sc)} excluded={bad}")


if __name__ == "__main__":
    main()
