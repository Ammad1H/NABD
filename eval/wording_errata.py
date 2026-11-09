"""Wording errata for summaries written by LOCKED generators (docs/DEVIATIONS.md C9).

uae/gcc.py and uae/backtest_v2.py are covered by plan locks (docs/LOCK-GCC.json, docs/LOCK-UAE-v2.json), so their
text cannot be edited without breaking the lock. This script applies fixed, wording-only replacements to their
outputs. It never touches a number: `check()` asserts that the multiset of numbers in each file is unchanged.

Run after any rerun of a locked generator (idempotent):
  python3 -m eval.wording_errata
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ERRATA = {
    "results/gcc/SUMMARY.md": [
        ("Data source deviation G1: WHO's full export via a public mirror, verified against the official API.",
         "Data source deviation G1: WHO's full export via a public mirror; 419/419 overlapping UAE rows identical to our "
         "official-API cache and 23/23 Gulf rows spot-checked against the official API; full re-pull pending "
         "(docs/DEVIATIONS.md G1, G1b, C2)."),
        ("- The method designed on UAE data, frozen, and then run blind on three other Gulf countries' surveillance beat "
         "'next week = this week' by about 9% for influenza and 20% for RSV, and beat the seasonal-average baseline by "
         "much more.",
         "- The method designed on UAE data, frozen, and then run out of sample on three other Gulf countries' "
         "surveillance (plan locked in our git before download; self-attested until anchored) beat 'next week = this "
         "week' by about 9% for influenza (the pre-registered primary), and beat the seasonal-average baseline by much "
         "more. RSV is a secondary outcome (about 20% vs persistence; its country-clustered interval includes 1 and its "
         "95% coverage is 0.83)."),
        ("- This is the project's first blind, pre-registered test the method passed.",
         "- This is the project's first out-of-sample test, with the plan locked before download, that the method "
         "passed."),
    ],
    "results/uae/SUMMARY-v2.md": [
        ("## By horizon (LOSO; horizon relative to reference date: -1 nowcast … 2 = +2.5 wk after issue)",
         "## By horizon (LOSO; h = -1 … 2 are targets L+1 … L+4 after the last published week L; in the live product "
         "these are labelled by week-ending date and nowcast / +1 / +2 / +3 wk after issue)"),
        ("## Surge-onset alerts (pre-declared rule; descriptive, n = 4 seasons per series)",
         "## Surge-onset alerts (pre-declared rule; descriptive, n = 4 seasons per series; RETIRED as evidence)\n\n"
         "> These counts use the **leave-one-season-out** design, in which the model is trained on later seasons. That "
         "design is retired as evidence (docs/DEVIATIONS.md U1; research/claims-ledger.md D4/F18). Shown for "
         "transparency only; do not cite the '3/3'."),
    ],
}

NUM = re.compile(r"\d+(?:\.\d+)?")
NUM_EXEMPT = {"results/uae/SUMMARY-v2.md": {"2.5", "0.5", "1.5"}}  # removed horizon labels, not results


def numbers(text: str, exempt=frozenset()) -> list[str]:
    return sorted(n for n in NUM.findall(text) if n not in exempt)


def apply(root: Path = ROOT) -> dict:
    changed = {}
    for rel, pairs in ERRATA.items():
        p = root / rel
        if not p.exists():
            continue
        txt = p.read_text(encoding="utf-8")
        new = txt
        for old, rep in pairs:
            if rep in new:
                continue
            new = new.replace(old, rep)
        if new != txt:
            p.write_text(new, encoding="utf-8")
            changed[rel] = (txt, new)
    return changed


def check(before: str, after: str, rel: str) -> None:
    """Every number that was in the original text is still there (errata may add citation numbers, never drop)."""
    ex = NUM_EXEMPT.get(rel, set())
    b, a = numbers(before, ex), numbers(after, ex)
    missing = list(b)
    for n in a:
        if n in missing:
            missing.remove(n)
    if missing:
        raise AssertionError(f"{rel}: numbers removed by errata: {missing}")


def main() -> int:
    changed = apply()
    for rel, (b, a) in changed.items():
        check(b, a, rel)
        print(f"errata applied: {rel}")
    if not changed:
        print("errata: nothing to change (already applied)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
