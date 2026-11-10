"""Lock definitions for the borrowed-strength test (docs/PREREG-POOL.md)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "nabd_v2_kit"))
from nabd_kit.prereg import assert_locked, lock  # noqa: E402

from pool import config as C  # noqa: E402

LOCK1 = ROOT / "docs" / "LOCK-POOL-1.json"
LOCK2 = ROOT / "docs" / "LOCK-POOL-2.json"
PLAN = ["docs/PREREG-POOL.md"]
CODE1 = ["pool/config.py", "uae/models.py", "uae/scoring.py", "uae/gcc.py"]
CODE2 = CODE1 + ["pool/__init__.py", "pool/locks.py", "pool/data.py", "pool/features.py", "pool/models.py",
                 "pool/harness.py", "pool/dev.py", "pool/score.py"]
MODEL_CONFIG = ROOT / "pool" / "model_config.json"
DEV_MANIFEST = "data/raw/flunet_pool_dev.sha256"


def config1() -> dict:
    return {k: getattr(C, k) for k in ["DEV", "HELD_EMRO", "HELD_OTHER", "EVAL_SEASONS", "EXCLUDE_TRAINING_SEASONS",
                                       "MIN_YEAR", "QUALIFY", "SENTINEL_MIN_QUALIFYING_EVAL_SEASONS",
                                       "MIN_TRAINING_SEASONS", "MIN_SCORED_EVAL_SEASONS",
                                       "SHORT_HISTORY_MAX_OWN_SEASONS", "TRUNCATE_TO_SEASONS", "BOOTSTRAP",
                                       "MIRROR_URL", "EXPORT_SHA256_PREFIX", "COLUMNS", "LAT"]}


def config2() -> dict:
    return dict(design=config1(), model=json.loads(MODEL_CONFIG.read_text()))


def make_lock1():
    import os
    os.chdir(ROOT)
    return lock(LOCK1, PLAN, CODE1, config1(), None, label="PREREG-POOL lock #1 (plan + lists, before any new download)",
                hypotheses=["H1: pooled rel WIS vs local v1 < 1 with country-clustered 95% upper bound < 1"])


def check_lock1() -> str:
    import os
    os.chdir(ROOT)
    return assert_locked(LOCK1, PLAN, CODE1, config1(), None)


def make_lock2():
    import os
    os.chdir(ROOT)
    return lock(LOCK2, PLAN, CODE2, config2(), DEV_MANIFEST,
                label="PREREG-POOL lock #2 (model + config + dev data, before any held-out row)")


def check_lock2() -> str:
    import os
    os.chdir(ROOT)
    check_lock1()
    return assert_locked(LOCK2, PLAN, CODE2, config2(), DEV_MANIFEST)


if __name__ == "__main__":
    if sys.argv[1] == "lock1":
        print(make_lock1()["digest"]["root"])
    elif sys.argv[1] == "lock2":
        print(make_lock2()["digest"]["root"])
    elif sys.argv[1] == "check":
        print(check_lock1()); print(check_lock2())
