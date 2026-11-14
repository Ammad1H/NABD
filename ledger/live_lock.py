"""Lock for the prospective UAE test (docs/PREREG-LIVE.md)."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "nabd_v2_kit"))
from nabd_kit.prereg import assert_locked, lock  # noqa: E402

LOCK = ROOT / "docs" / "LOCK-LIVE.json"
PLAN = ["docs/PREREG-LIVE.md"]
CODE = ["ledger/live_test.py", "ledger/live_lock.py", "ledger/issue.py", "ledger/score.py", "pool/live.py",
        "pool/models.py", "pool/features.py", "pool/harness.py", "uae/models.py", "uae/scoring.py"]
DATA = "data/raw/flunet_pool_dev.sha256"


def config() -> dict:
    return dict(first_round=2, last_target_week_end="2027-03-28", final_scoring_from="2027-04-15",
                bootstrap=dict(B=2000, seed=0, block=4), models=["NABD-Pool", "NABD-UAE-v1", "persistence"],
                pool_model=json.loads((ROOT / "pool" / "model_config.json").read_text()))


def make():
    os.chdir(ROOT)
    return lock(LOCK, PLAN, CODE, config(), DATA, label="PREREG-LIVE (prospective UAE test, before W45 was published)",
                hypotheses=["H-live: UAE influenza rel WIS NABD-Pool / NABD-UAE-v1 < 1 with round-bootstrap 95% upper bound < 1"])


def check() -> str:
    os.chdir(ROOT)
    return assert_locked(LOCK, PLAN, CODE, config(), DATA)


if __name__ == "__main__":
    print(make()["digest"]["root"] if sys.argv[1:] == ["lock"] else check())
