"""Wording errata for locked-generator summaries (DEVIATIONS C9): banned wording gone, numbers preserved."""
import subprocess
from pathlib import Path

from eval import wording_errata as we

ROOT = Path(__file__).resolve().parents[1]
BANNED = ["run blind", "first blind", "verified against the official api", "+2.5 wk after issue"]


def test_current_summaries_clean():
    for rel in we.ERRATA:
        txt = (ROOT / rel).read_text(encoding="utf-8").lower()
        for b in BANNED:
            assert b not in txt, (rel, b)


def test_errata_preserve_numbers_on_original_text(tmp_path):
    """Re-apply the errata to the committed pre-errata text (from git) and check that no number is dropped."""
    for rel in we.ERRATA:
        try:
            orig = subprocess.check_output(["git", "-C", str(ROOT), "show", f"63611e6:{rel}" if "gcc" in rel
                                            else f"da045ee:{rel}"], text=True, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            orig = (ROOT / rel).read_text(encoding="utf-8")
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(orig, encoding="utf-8")
        changed = we.apply(tmp_path)
        if rel in changed:
            b, a = changed[rel]
            we.check(b, a, rel)
        assert we.apply(tmp_path) == {}  # idempotent
