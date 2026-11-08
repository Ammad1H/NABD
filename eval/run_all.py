"""End-to-end US-A pipeline (BUILD-SPEC G2): tune (2023/24) -> forecast test seasons -> score.

    python -m eval.run_all --cached            # uses the local hub clone in external/hub
    python -m eval.run_all --cached --skip-tune  # reuse the committed models/config.yaml (default for reruns)
    python -m eval.run_all --fetch             # (re)clone the CDC FluSight hub first

Fixed seeds; runtime ~10 min on 2 CPUs (tuning ~5 min, forecasting ~2 min, scoring ~1 min).
"""
from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB_URL = "https://github.com/cdcepi/FluSight-forecast-hub.git"
HUB_SHA = "d03574028ece110013c6284d3012ac4bef03ded7"


def fetch_hub():
    hub = ROOT / "external" / "hub"
    if not hub.exists():
        hub.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--filter=blob:none", "--sparse", HUB_URL, str(hub)], check=True)
        subprocess.run(["git", "-C", str(hub), "sparse-checkout", "set", "target-data", "hub-config",
                        "model-output/FluSight-ensemble", "model-output/FluSight-baseline"], check=True)
    subprocess.run(["git", "-C", str(hub), "checkout", "-q", HUB_SHA], check=False)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--cached", action="store_true", help="use existing external/hub clone")
    g.add_argument("--fetch", action="store_true", help="clone the hub if missing (pinned commit)")
    ap.add_argument("--retune", action="store_true", help="re-run 2023/24 tuning (overwrites models/config.yaml)")
    ap.add_argument("--skip-tune", action="store_true", help="(default) reuse frozen models/config.yaml")
    ap.add_argument("--with-chronos", action="store_true")
    ap.add_argument("--skip-league", action="store_true", help="skip the D7 league table (needs hub model-output checkout or cache)")
    ap.add_argument("--procs", type=int, default=2)
    a = ap.parse_args()
    t0 = time.time()
    if a.fetch or not (ROOT / "external" / "hub").exists():
        fetch_hub()
    from eval import alerts, backtest, score, tune
    if a.retune or not (ROOT / "models" / "config.yaml").exists():
        tune.main(a.procs)
    backtest.main(procs=a.procs, with_chronos=a.with_chronos)
    score.main()
    alerts.main()
    import runpy; runpy.run_module('eval.exploratory', run_name='__main__')
    from eval import round2   # D6/D7/D9/D10 (declared in docs/DEVIATIONS.md); league uses cache or hub model-output
    round2.main(skip_league=a.skip_league)
    print(f"run_all done in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
