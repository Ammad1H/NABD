"""Schema validation and band lookup for playbook/playbook.yaml."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

PLAYBOOK_PATH = Path(__file__).with_name("playbook.yaml")
REQUIRED_ROLES = {"hospital_ops", "adphc_duty"}
REQUIRED_LANGS = {"en", "ar"}


class PlaybookError(ValueError):
    pass


def load_playbook(path: Path | str = PLAYBOOK_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        pb = yaml.safe_load(f)
    validate_playbook(pb)
    return pb


def validate_playbook(pb: dict[str, Any]) -> None:
    """Raise PlaybookError if the playbook does not meet the schema."""
    if not isinstance(pb, dict):
        raise PlaybookError("playbook must be a mapping")
    for key in ("version", "status", "review", "roles", "reason_codes", "bands"):
        if key not in pb:
            raise PlaybookError(f"missing top-level key: {key}")
    if pb["status"] not in {"ILLUSTRATIVE", "REVIEWED"}:
        raise PlaybookError("status must be ILLUSTRATIVE or REVIEWED")
    if pb["status"] == "REVIEWED" and not pb["review"].get("reviewed"):
        raise PlaybookError("status REVIEWED requires review.reviewed = true")
    if set(pb["roles"]) != REQUIRED_ROLES:
        raise PlaybookError(f"roles must be exactly {sorted(REQUIRED_ROLES)}")
    for role, names in pb["roles"].items():
        if not REQUIRED_LANGS <= set(names):
            raise PlaybookError(f"role {role} needs en and ar names")
    codes = [rc.get("code") for rc in pb["reason_codes"]]
    if len(codes) != len(set(codes)) or not codes:
        raise PlaybookError("reason codes must be non-empty and unique")
    for rc in pb["reason_codes"]:
        if not REQUIRED_LANGS <= set(rc):
            raise PlaybookError(f"reason code {rc.get('code')} needs en and ar")
    ids = set()
    for b in pb["bands"]:
        for key in ("id", "target", "location", "horizon_label", "lower", "upper", "tier", "actions"):
            if key not in b:
                raise PlaybookError(f"band missing {key}: {b.get('id')}")
        if b["id"] in ids:
            raise PlaybookError(f"duplicate band id {b['id']}")
        ids.add(b["id"])
        if not float(b["lower"]) < float(b["upper"]):
            raise PlaybookError(f"band {b['id']}: lower must be < upper")
        if b["tier"] not in (1, 2, 3):
            raise PlaybookError(f"band {b['id']}: tier must be 1, 2 or 3")
        if set(b["actions"]) != REQUIRED_ROLES:
            raise PlaybookError(f"band {b['id']}: actions needed for both roles")
        for role, text in b["actions"].items():
            if not REQUIRED_LANGS <= set(text):
                raise PlaybookError(f"band {b['id']} role {role}: en and ar required")
    # Non-overlap per (target, location, horizon_label)
    groups: dict[tuple, list] = {}
    for b in pb["bands"]:
        groups.setdefault((b["target"], b["location"], b["horizon_label"]), []).append(b)
    for key, bands in groups.items():
        bands = sorted(bands, key=lambda x: float(x["lower"]))
        for a, c in zip(bands, bands[1:]):
            if float(a["upper"]) > float(c["lower"]):
                raise PlaybookError(f"overlapping bands for {key}: {a['id']} / {c['id']}")


def match_band(pb: dict[str, Any], target: str, location: str, value: float,
               horizon_label: str = "+1.5 wk") -> dict[str, Any] | None:
    for b in pb["bands"]:
        if (b["target"] == target and b["location"] == location
                and b["horizon_label"] == horizon_label
                and float(b["lower"]) <= value < float(b["upper"])):
            return b
    return None


if __name__ == "__main__":
    pb = load_playbook()
    print(f"playbook {pb['version']} OK ({len(pb['bands'])} bands, status {pb['status']})")
