"""DEVIATIONS S7 (UAE development check) and the committed GCC robustness reproduction (claims ledger A5)."""
import json
from pathlib import Path

from eval import gcc_robustness as gr
from pool import uae_devcheck as ud

ROOT = Path(__file__).resolve().parents[1]


def test_uae_devcheck_matches_pool_summary():
    """The restated UAE ratios must equal the 'already-seen countries' figures written by the locked pool run."""
    res = ud.main()
    per = {r.split(",")[0]: r.split(",") for r in (ROOT / "results/pool/dev/per_country_chosen.csv").read_text().splitlines()}
    head = per["country"]
    are = dict(zip(head, per["ARE"]))
    assert abs(res["overall"]["NABD-Pool / persistence"]["rel_wis"] - float(are["pool/persistence"])) < 1e-3
    assert abs(res["overall"]["NABD-Pool / NABD-UAE-v1"]["rel_wis"] - float(are["pool/v1"])) < 1e-3
    assert res["seasons"] == [2024, 2025] and res["cells"] == 388


def test_uae_devcheck_reported_both_ways_and_labelled():
    s = json.loads((ROOT / "results/pool/uae_devcheck/summary.json").read_text())
    assert "NON-CONFIRMATORY" in s["status"]
    # the season the own-record model won is reported, not hidden
    assert s["by_season"]["2025"]["NABD-Pool / NABD-UAE-v1"] > 1
    md = (ROOT / "results/pool/uae_devcheck/SUMMARY.md").read_text().lower()
    assert "non-confirmatory" in md and "not confirmatory" in md


def test_gcc_robustness_reproduces_audit_numbers():
    res = gr.main()
    f = res["flu"]
    assert f["pooled"] == 0.914
    assert (min(f["leave_one_country_out"].values()), max(f["leave_one_country_out"].values())) == (0.904, 0.929)
    assert f["two_stage_bootstrap_ci95"][1] < 1          # flu verdict robust to country clustering
    assert res["rsv"]["two_stage_bootstrap_ci95"][1] > 1  # RSV is not, which is why it is never headlined


def test_claims_using_uae_devcheck_carry_the_label():
    for rel in ["README.md", "pitch/story.md", "pitch/submission/form-answers.md"]:
        txt = (ROOT / rel).read_text(encoding="utf-8").lower()
        if "0.77" in txt:
            assert "development check" in txt, rel
        assert "proven in the uae" not in txt.replace('never says "proven in the uae"', ""), rel
