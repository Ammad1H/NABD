"""Run every test_* function in tests/test_kit.py without needing pytest."""
from __future__ import annotations

import importlib.util
import sys
import time
import traceback
from pathlib import Path

here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("test_kit", here / "test_kit.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

tests = [(n, f) for n, f in vars(mod).items() if n.startswith("test_") and callable(f)]
failed = 0
t0 = time.time()
for name, fn in tests:
    try:
        fn()
        print(f"PASS  {name}")
    except Exception:  # noqa: BLE001
        failed += 1
        print(f"FAIL  {name}")
        traceback.print_exc()
print(f"\n{len(tests) - failed}/{len(tests)} passed in {time.time() - t0:.1f}s")
sys.exit(1 if failed else 0)
