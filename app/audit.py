"""Append-only, hash-chained audit log for human decisions on playbook actions.

Each record carries `prev_hash` (the previous record's `hash`) and its own `hash`,
which is the SHA-256 of the canonical JSON of the record without `hash`. Editing,
deleting or reordering any line breaks the chain and `verify_chain` reports where.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_AUDIT = Path(__file__).parent / "audit" / "audit.jsonl"
GENESIS = "0" * 64
DECISIONS = {"APPROVE", "MODIFY", "DISMISS"}


class AuditError(ValueError):
    pass


def _canonical(rec: dict[str, Any]) -> bytes:
    return json.dumps(rec, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _hash(rec_without_hash: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical(rec_without_hash)).hexdigest()


def read_records(path: Path | str = DEFAULT_AUDIT) -> list[dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return []
    out = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def last_hash(path: Path | str = DEFAULT_AUDIT) -> str:
    recs = read_records(path)
    return recs[-1]["hash"] if recs else GENESIS


def append_decision(*, approver: str, role: str, decision: str, reason_code: str,
                    band_id: str, proposed_action: str, forecast_ref: dict[str, Any],
                    note: str = "", modified_action: str | None = None,
                    playbook_version: str = "", path: Path | str = DEFAULT_AUDIT,
                    valid_reason_codes: set[str] | None = None) -> dict[str, Any]:
    """Validate and append one decision. Returns the written record."""
    if not approver or not approver.strip():
        raise AuditError("a named approver is required")
    if decision not in DECISIONS:
        raise AuditError(f"decision must be one of {sorted(DECISIONS)}")
    if not reason_code:
        raise AuditError("a reason code is required")
    if valid_reason_codes is not None and reason_code not in valid_reason_codes:
        raise AuditError(f"unknown reason code {reason_code}")
    if reason_code == "OTHER" and not note.strip():
        raise AuditError("reason OTHER requires a note")
    if decision == "MODIFY" and not (modified_action and modified_action.strip()):
        raise AuditError("MODIFY requires the modified action text")
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    recs = read_records(p)
    rec = {
        "seq": len(recs) + 1,
        "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "approver": approver.strip(),
        "role": role,
        "decision": decision,
        "reason_code": reason_code,
        "note": note.strip(),
        "band_id": band_id,
        "proposed_action": proposed_action,
        "modified_action": (modified_action or "").strip() or None,
        "forecast_ref": forecast_ref,
        "playbook_version": playbook_version,
        "prev_hash": recs[-1]["hash"] if recs else GENESIS,
    }
    rec["hash"] = _hash(rec)
    # Append-only: open in "a" mode, never rewrite.
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())
    return rec


def verify_chain(path: Path | str = DEFAULT_AUDIT) -> tuple[bool, str]:
    """Return (ok, message). Detects edits, deletions, insertions and reordering."""
    recs = read_records(path)
    prev = GENESIS
    for i, rec in enumerate(recs, start=1):
        body = {k: v for k, v in rec.items() if k != "hash"}
        if rec.get("seq") != i:
            return False, f"sequence break at line {i} (seq={rec.get('seq')})"
        if rec.get("prev_hash") != prev:
            return False, f"chain break at line {i}: prev_hash does not match"
        if _hash(body) != rec.get("hash"):
            return False, f"record {i} was modified (hash mismatch)"
        prev = rec["hash"]
    return True, f"chain intact ({len(recs)} records)"
