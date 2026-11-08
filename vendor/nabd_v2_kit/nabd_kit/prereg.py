"""Pre-registration locks with a mechanical goalpost guard.

lock() hashes the analysis plan, the model code, the configuration (canonical
JSON, so key order does not matter) and an optional data manifest into a
LOCK.json. assert_locked() recomputes everything at scoring time and raises
GoalpostError if anything differs, so a confirmatory score cannot be computed
for a model that changed after the lock. Anchor LOCK.json outside the team the
moment it is written (scripts/anchor.sh).
"""
from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path

from .ledger import merkle_root, sha256_bytes, sha256_file


class GoalpostError(RuntimeError):
    """Raised when the thing being scored is not the thing that was locked."""


def canonical_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _digest(plan_files, code_files, config, data_manifest) -> dict:
    files = {str(Path(p).as_posix()): sha256_file(p) for p in [*plan_files, *code_files]}
    parts = {"files": dict(sorted(files.items())), "config": sha256_bytes(canonical_json(config))}
    if data_manifest is not None:
        parts["data_manifest"] = sha256_file(data_manifest)
    leaves = [*parts["files"].values(), parts["config"]] + (
        [parts["data_manifest"]] if "data_manifest" in parts else [])
    parts["root"] = merkle_root(leaves)
    return parts


def lock(out_path, plan_files, code_files, config: dict, data_manifest=None,
         label: str = "", hypotheses: list | None = None) -> dict:
    rec = {"schema": "nabd-lock/1", "label": label,
           "locked_utc_self_attested": _dt.datetime.now(_dt.timezone.utc).isoformat(),
           "hypotheses": hypotheses or [], "config": config,
           "digest": _digest(plan_files, code_files, config, data_manifest)}
    Path(out_path).write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    return rec


def assert_locked(lock_path, plan_files, code_files, config: dict, data_manifest=None) -> str:
    rec = json.loads(Path(lock_path).read_text())
    now = _digest(plan_files, code_files, config, data_manifest)
    then = rec["digest"]
    diffs = []
    for f in sorted(set(then["files"]) | set(now["files"])):
        if then["files"].get(f) != now["files"].get(f):
            diffs.append(f"file differs or missing: {f}")
    if then["config"] != now["config"]:
        diffs.append("config differs from the locked config")
    if then.get("data_manifest") != now.get("data_manifest"):
        diffs.append("data manifest differs")
    if diffs:
        raise GoalpostError("not the locked analysis: " + "; ".join(diffs))
    return then["root"]
