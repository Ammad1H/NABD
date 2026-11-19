"""The live WHO snapshot is separate from the locked one (data/raw/flunet_are.csv, pinned by docs/lock_uae_v2)."""
from pathlib import Path

import pandas as pd

from app import data_io
from ledger import weekly

ROOT = Path(__file__).resolve().parents[1]


def test_app_prefers_live_snapshot_and_never_the_locked_path_for_writes():
    assert data_io.RAW_FLUNET_CANDIDATES[0].name == "flunet_are_live.csv"
    assert weekly.LIVE.name == "flunet_are_live.csv"
    assert weekly.LIVE != ROOT / "data" / "raw" / "flunet_are.csv"


def test_save_live_snapshot_writes_only_the_live_file(tmp_path, monkeypatch):
    locked = ROOT / "data" / "raw" / "flunet_are.csv"
    before = locked.read_bytes()
    src = tmp_path / "who.csv"
    raw = pd.read_csv(locked)
    pd.concat([raw, pd.DataFrame([{"ISO_YEAR": 2026, "ISO_WEEK": 45, "ORIGIN_SOURCE": "SENTINEL",
                                   "SPEC_PROCESSED_NB": 443, "INF_ALL": 90, "RSV": 102}])]).to_csv(src, index=False)
    monkeypatch.setattr(weekly.flunet, "URL", str(src))
    monkeypatch.setattr(weekly, "LIVE", tmp_path / "flunet_are_live.csv")
    out = weekly.save_live_snapshot()
    assert locked.read_bytes() == before
    obs = data_io.load_uae_observed(out)
    assert (int(obs.ISO_YEAR.iloc[-1]), int(obs.ISO_WEEK.iloc[-1])) == (2026, 45)



def test_cached_weekly_run_reads_the_live_snapshot_and_restores_the_locked_path(tmp_path, monkeypatch):
    live = tmp_path / "flunet_are_live.csv"
    live.write_bytes((ROOT / "data" / "raw" / "flunet_are.csv").read_bytes())
    monkeypatch.setattr(weekly, "LIVE", live)
    seen = {}
    monkeypatch.setattr(weekly, "_run", lambda mode, a, w: seen.setdefault("src", weekly.flunet.CACHED))
    locked = weekly.flunet.CACHED
    weekly.run("cached")
    assert seen["src"] == live and weekly.flunet.CACHED == locked
