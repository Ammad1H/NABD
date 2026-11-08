"""One idempotent weekly command for the live ledger.

    python -m ledger.weekly --fetch      # live: pull WHO FluNet, score past rounds, issue a round only if new data
    python -m ledger.weekly --cached     # dry run on data/raw

Steps:
  1. Load FluNet UAE (live or cached).
  2. Score every hashed ledger file against whatever target weeks have been published
     (ledger/score.py; it rewrites scores.csv and SCOREBOARD.md each time, so it is idempotent).
  3. Compare the newest published week with the data_through_week of the newest issued round.
     If a newer week exists, issue the next round (R<n+1>) with its Merkle manifest and the v1
     explanation files; otherwise do nothing. Running it twice in a row never creates a duplicate round.
  4. Print the git and anchor commands. Nothing is pushed or posted automatically.
"""
import argparse
import json
from pathlib import Path

from adapters import flunet
from ledger import score as scorer
from ledger.issue import issue

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "ledger"


def latest_round():
    """(round_label, max data_through_week string) of the newest issued round, or (None, None)."""
    best = (None, None, "")
    for m in LEDGER.glob("*.meta.json"):
        meta = json.loads(m.read_text())
        dt_weeks = meta.get("data_through_week")
        wk = max(dt_weeks.values()) if isinstance(dt_weeks, dict) else str(dt_weeks)
        if meta.get("issued_utc", "") > best[2]:
            best = (meta.get("round"), wk, meta.get("issued_utc", ""))
    return best[0], best[1]


def latest_published_week(mode):
    s = flunet.sentinel_series(flunet.load(mode))
    s = s.dropna(subset=["specimens"])
    last = s.iloc[-1]
    return f"{int(last.iso_year)}-W{int(last.iso_week):02d}"


def next_label(label):
    if not label or not label.startswith("R"):
        return "R0"
    return f"R{int(label[1:]) + 1}"


def run(mode="cached", allow_issue=True):
    sc, bad = scorer.score(mode)
    rnd, through = latest_round()
    pub = latest_published_week(mode)
    out = {"scored_rows": int(len(sc)), "excluded_files": bad, "latest_round": rnd,
           "latest_round_data_through": through, "latest_published_week": pub, "issued": None}
    if allow_issue and (through is None or pub > through):
        label = next_label(rnd)
        written = issue(mode, label)
        out["issued"] = label
        out["files"] = [str(p.relative_to(ROOT)) for p, _ in written]
    return out


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--cached", action="store_true")
    g.add_argument("--fetch", action="store_true")
    ap.add_argument("--no-issue", action="store_true", help="score only; never issue a round")
    a = ap.parse_args()
    out = run("fetch" if a.fetch else "cached", allow_issue=not a.no_issue)
    print(json.dumps(out, indent=2))
    if out["issued"]:
        rd = sorted((LEDGER / "rounds").glob(f"*_{out['issued']}"))[-1]
        print(f"\nNext (by hand): git add ledger results/uae/explain && git commit -m 'ledger {out['issued']}' && git push\n"
              f"Then anchor: bash vendor/nabd_v2_kit/scripts/anchor.sh {rd.relative_to(ROOT)}/MANIFEST.sha256 "
              f"(see ledger/ANCHOR.md) and post the Merkle root.")
    else:
        print("\nNo new FluNet week since the last round: nothing issued (idempotent).")


if __name__ == "__main__":
    main()
