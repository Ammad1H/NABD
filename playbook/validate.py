"""Schema validation, trend classification and band lookup for playbook/playbook.yaml.

v0.3 (round 3): a band is selected by the EFFECTIVE LEVEL and the forecast TRAJECTORY.
- Effective level = the highest tier threshold T with max over future target weeks of
  P(value > T) >= p_act (default 0.30), read from the issued forecast quantiles; 0 if none.
- Trajectory = median at the furthest horizon vs the last observed value (classify_trend).
This guarantees the card never proposes a "rising" action while the forecast median falls, and
never proposes an elevated or surge action unless the forecast gives it a material chance.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

import numpy as np
import yaml

PLAYBOOK_PATH = Path(__file__).with_name("playbook.yaml")
REQUIRED_ROLES = {"hospital_ops", "adphc_duty", "occupational_health"}
REQUIRED_LANGS = {"en", "ar"}
TRENDS = ("rising", "plateau", "falling")
DEFAULT_RULES = {"rising_if_ratio_at_least": 1.15, "falling_if_ratio_at_most": 0.87}
DEFAULT_P_ACT = 0.30


class PlaybookError(ValueError):
    pass


def load_playbook(path: Path | str = PLAYBOOK_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        pb = yaml.safe_load(f)
    validate_playbook(pb)
    return pb


def _trend_set(b: dict[str, Any]) -> set[str]:
    tr = b.get("trend", ["any"])
    if isinstance(tr, str):
        tr = [tr]
    return set(TRENDS) if "any" in tr else set(tr)


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
    rules = (pb.get("rules") or {}).get("trend", DEFAULT_RULES)
    dec = (pb.get("rules") or {}).get("decision")
    if dec is not None and not 0 < float(dec.get("p_act", DEFAULT_P_ACT)) < 1:
        raise PlaybookError("rules.decision.p_act must be in (0, 1)")
    if not float(rules["falling_if_ratio_at_most"]) < 1 < float(rules["rising_if_ratio_at_least"]):
        raise PlaybookError("trend rule must satisfy falling_if_ratio_at_most < 1 < rising_if_ratio_at_least")
    ids = set()
    for b in pb["bands"]:
        for key in ("id", "target", "location", "horizon_label", "lower", "upper", "tier", "actions", "trend"):
            if key not in b:
                raise PlaybookError(f"band missing {key}: {b.get('id')}")
        if b["id"] in ids:
            raise PlaybookError(f"duplicate band id {b['id']}")
        ids.add(b["id"])
        tr = b["trend"] if isinstance(b["trend"], list) else [b["trend"]]
        if not tr or not set(tr) <= set(TRENDS) | {"any"}:
            raise PlaybookError(f"band {b['id']}: trend must be a list of rising/plateau/falling/any")
        if "rising" in b["id"] and set(tr) != {"rising"}:
            raise PlaybookError(f"band {b['id']}: a band named 'rising' may only fire on a rising trend")
        if not float(b["lower"]) < float(b["upper"]):
            raise PlaybookError(f"band {b['id']}: lower must be < upper")
        if b["tier"] not in (1, 2, 3):
            raise PlaybookError(f"band {b['id']}: tier must be 1, 2 or 3")
        if set(b["actions"]) != REQUIRED_ROLES:
            raise PlaybookError(f"band {b['id']}: actions needed for every role {sorted(REQUIRED_ROLES)}")
        lab = b.get("label")
        if not isinstance(lab, dict) or not REQUIRED_LANGS <= set(lab) or not all(str(lab[x]).strip() for x in REQUIRED_LANGS):
            raise PlaybookError(f"band {b['id']}: plain-language label with en and ar required")
        for role, text in b["actions"].items():
            if not REQUIRED_LANGS <= set(text):
                raise PlaybookError(f"band {b['id']} role {role}: en and ar required")
    # Non-overlap per (target, location, horizon_label) in level x trend.
    groups: dict[tuple, list] = {}
    for b in pb["bands"]:
        groups.setdefault((b["target"], b["location"], b["horizon_label"]), []).append(b)
    for key, bands in groups.items():
        for i, a in enumerate(bands):
            for c in bands[i + 1:]:
                level_overlap = float(a["lower"]) < float(c["upper"]) and float(c["lower"]) < float(a["upper"])
                if level_overlap and _trend_set(a) & _trend_set(c):
                    raise PlaybookError(f"overlapping bands for {key}: {a['id']} / {c['id']}")


def classify_trend(path_medians: Sequence[float], last_observed: float,
                   pb: dict[str, Any] | None = None) -> tuple[str, float]:
    """Trend of the forecast path: median at the furthest horizon / last observed value.

    Returns (trend, ratio). With a non-positive last observation, falls back to the first
    vs last forecast median.
    """
    rules = ((pb or {}).get("rules") or {}).get("trend", DEFAULT_RULES)
    meds = [float(m) for m in path_medians if m is not None and np.isfinite(m)]
    if not meds:
        raise ValueError("no forecast medians")
    base = float(last_observed) if last_observed is not None and np.isfinite(last_observed) and last_observed > 0 \
        else meds[0]
    ratio = meds[-1] / base if base > 0 else 1.0
    if ratio >= float(rules["rising_if_ratio_at_least"]):
        return "rising", ratio
    if ratio <= float(rules["falling_if_ratio_at_most"]):
        return "falling", ratio
    return "plateau", ratio


def select_band(pb: dict[str, Any], target: str, location: str, level: float, trend: str,
                horizon_label: str = "level horizon") -> dict[str, Any] | None:
    for b in pb["bands"]:
        if (b["target"] == target and b["location"] == location and b["horizon_label"] == horizon_label
                and float(b["lower"]) <= level < float(b["upper"]) and trend in _trend_set(b)):
            return b
    return None


def match_band(pb: dict[str, Any], target: str, location: str, value: float,
               horizon_label: str = "level horizon", trend: str | None = None) -> dict[str, Any] | None:
    """Backward-compatible lookup. Without a trend, only trend-agnostic ('any') bands can match."""
    for b in pb["bands"]:
        if not (b["target"] == target and b["location"] == location and b["horizon_label"] == horizon_label
                and float(b["lower"]) <= value < float(b["upper"])):
            continue
        if trend is None and _trend_set(b) == set(TRENDS):
            return b
        if trend is not None and trend in _trend_set(b):
            return b
    return None


def p_act(pb: dict[str, Any] | None) -> float:
    dec = ((pb or {}).get("rules") or {}).get("decision") or {}
    return float(dec.get("p_act", DEFAULT_P_ACT))


def tier_thresholds(pb: dict[str, Any], target: str, location: str,
                    horizon_label: str = "level horizon") -> list[float]:
    """Sorted band lower bounds above zero for one target: the tier thresholds (e.g. RSV 10, 20)."""
    return sorted({float(b["lower"]) for b in pb["bands"]
                   if b["target"] == target and b["location"] == location
                   and b["horizon_label"] == horizon_label and float(b["lower"]) > 0})


def effective_level(max_probs: dict[float, float], p_threshold: float) -> float:
    """Highest threshold T with max_h P(Y_h > T) >= p_threshold; 0.0 if none."""
    hits = [T for T, p in max_probs.items() if p >= p_threshold]
    return max(hits) if hits else 0.0


def prob_exceed(quantiles: dict[float, float], threshold: float) -> float:
    """P(Y > threshold) by linear interpolation of the predictive CDF between quantile levels.

    Outside the quantile range the tail probability is bounded by the outermost level
    (e.g. reported as <= 0.01 or >= 0.99), never extrapolated.
    """
    qs = sorted((float(k), float(v)) for k, v in quantiles.items())
    levels = np.array([q for q, _ in qs])
    values = np.array([v for _, v in qs])
    values = np.maximum.accumulate(values)  # enforce monotone quantiles
    if threshold <= values[0]:
        return float(1 - levels[0])
    if threshold >= values[-1]:
        return float(1 - levels[-1])
    cdf = float(np.interp(threshold, values, levels))
    return 1 - cdf


if __name__ == "__main__":
    pb = load_playbook()
    print(f"playbook {pb['version']} OK ({len(pb['bands'])} bands, status {pb['status']})")
