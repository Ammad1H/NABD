"""Validate a CDC FluSight hub submission file (and optional model metadata) against the hub's own config.

    python -m eval.flusight_validate results/flusight_draft/2026-11-14-NABD-v1.csv \
        [--metadata results/flusight_draft/NABD-v1.yml] [--hub external/hub-live] [--today 2026-11-11]

This is a Python re-implementation of the main hubValidations checks (file name, columns, task IDs,
required quantile levels, value ranges, quantile monotonicity, duplicates, submission window), read from
`<hub>/hub-config/tasks.json` and `model-metadata-schema.json`. It is NOT the official validator: the
hub's GitHub Action (hubValidations) runs on the pull request and is authoritative. Exit code 0 = no
errors found; 1 = errors.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
COLS = ["reference_date", "target", "horizon", "target_end_date", "location", "output_type", "output_type_id", "value"]
NAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-([A-Za-z0-9_+]{1,16})-([A-Za-z0-9_+]{1,16})\.csv$")


def _opts(spec):
    if spec is None:
        return None
    return (spec.get("required") or []) + (spec.get("optional") or [])


def _round(tasks: dict, reference_date: str) -> dict | None:
    for r in tasks["rounds"]:
        for mt in r["model_tasks"]:
            o = _opts(mt["task_ids"].get("reference_date"))
            if o and reference_date in o:
                return r
    return None


def validate(path: Path, hub: Path, today: dt.date | None = None) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    m = NAME_RE.match(path.name)
    if not m:
        return [f"file name {path.name!r} must be <YYYY-MM-DD>-<team_abbr>-<model_abbr>.csv"], warnings
    ref = m.group(1)
    rdate = dt.date.fromisoformat(ref)
    if rdate.weekday() != 5:
        errors.append(f"reference_date {ref} is not a Saturday")
    tasks = json.loads((hub / "hub-config" / "tasks.json").read_text())
    rnd = _round(tasks, ref)
    if rnd is None:
        errors.append(f"reference_date {ref} is not an allowed round in {hub}/hub-config/tasks.json "
                      f"(is the hub clone up to date?)")
        return errors, warnings
    due = rnd.get("submissions_due") or {}
    if today and due.get("relative_to") == "reference_date":
        start = rdate + dt.timedelta(days=due["start"])
        end = rdate + dt.timedelta(days=due["end"])
        if not (start <= today <= end):
            warnings.append(f"today {today} is outside the submission window {start}..{end} "
                            f"(hub deadline is Wednesday 11 PM US Eastern; check the hub README)")
    d = pd.read_csv(path, dtype={"location": str, "output_type_id": str})
    if list(d.columns) != COLS:
        errors.append(f"columns must be exactly {COLS}, got {list(d.columns)}")
        return errors, warnings
    if (d.reference_date.astype(str) != ref).any():
        errors.append("reference_date column must equal the date in the file name on every row")
    if d.duplicated(["target", "horizon", "location", "output_type", "output_type_id"]).any():
        errors.append("duplicate rows for the same task and output_type_id")
    by_target = {mt["task_ids"]["target"]["optional"][0] if mt["task_ids"]["target"].get("optional")
                 else mt["task_ids"]["target"]["required"][0]: mt for mt in rnd["model_tasks"]}
    for tgt, g in d.groupby("target"):
        mt = by_target.get(tgt)
        if mt is None:
            errors.append(f"target {tgt!r} not in this round's tasks")
            continue
        ti = mt["task_ids"]
        hz = _opts(ti.get("horizon"))
        if hz is not None and not set(g.horizon.astype(int)).issubset(set(hz)):
            errors.append(f"{tgt}: horizons {sorted(set(g.horizon))} not within allowed {hz}")
        locs = _opts(ti.get("location"))
        bad = sorted(set(g.location) - set(locs or []))
        if bad:
            errors.append(f"{tgt}: unknown locations {bad[:10]}")
        ted = pd.to_datetime(g.target_end_date)
        exp = pd.to_datetime(g.reference_date) + pd.to_timedelta(g.horizon.astype(int) * 7, unit="D")
        if (ted != exp).any():
            errors.append(f"{tgt}: target_end_date must equal reference_date + 7*horizon days")
        for ot, gg in g.groupby("output_type"):
            spec = mt["output_type"].get(ot)
            if spec is None:
                errors.append(f"{tgt}: output_type {ot!r} not allowed")
                continue
            vals = pd.to_numeric(gg.value, errors="coerce")
            if vals.isna().any():
                errors.append(f"{tgt}/{ot}: non-numeric values")
            vs = spec.get("value", {})
            if "minimum" in vs and (vals < vs["minimum"]).any():
                errors.append(f"{tgt}/{ot}: values below minimum {vs['minimum']}")
            if "maximum" in vs and (vals > vs["maximum"]).any():
                errors.append(f"{tgt}/{ot}: values above maximum {vs['maximum']}")
            if ot == "quantile":
                req = [float(x) for x in spec["output_type_id"].get("required") or []]
                for (loc, h), q in gg.groupby(["location", "horizon"]):
                    have = sorted(float(x) for x in q.output_type_id)
                    levels_ok = len(have) == len(req) and np.allclose(sorted(req), have)
                    if not levels_ok:
                        errors.append(f"{tgt}: location {loc} horizon {h} quantile levels {len(have)} != required {len(req)}")
                        break
                    v = q.assign(l=q.output_type_id.astype(float)).sort_values("l").value.astype(float).to_numpy()
                    if (np.diff(v) < 0).any():
                        errors.append(f"{tgt}: location {loc} horizon {h} quantiles are not non-decreasing")
                        break
        if mt["output_type"].get("quantile", {}).get("is_required") and "quantile" not in set(g.output_type):
            errors.append(f"{tgt}: required output_type 'quantile' missing")
        nloc = g.location.nunique()
        if nloc < len(locs or []):
            warnings.append(f"{tgt}: {nloc} of {len(locs)} locations submitted (allowed, but check it is intended)")
    return errors, warnings


def validate_metadata(path: Path, hub: Path) -> list[str]:
    import yaml
    errs = []
    meta = yaml.safe_load(path.read_text())
    schema = json.loads((hub / "hub-config" / "model-metadata-schema.json").read_text())
    try:
        import jsonschema
        v = jsonschema.Draft7Validator(schema)
        errs += [f"metadata: {e.message}" for e in v.iter_errors(meta)]
    except ImportError:
        errs += [f"metadata: missing required field {k}" for k in schema.get("required", []) if k not in meta]
    txt = path.read_text()
    if "PLACEHOLDER" in txt:
        errs.append("metadata: PLACEHOLDER values remain (team name, contributors, email, URLs, citation)")
    if meta.get("designated_model") is not False:
        errs.append("metadata: designated_model should be false (v1 did not meet non-inferiority; see results/SUMMARY.md)")
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--metadata")
    ap.add_argument("--hub", default=os.environ.get("NABD_HUB", str(ROOT / "external" / "hub")))
    ap.add_argument("--today", default=None, help="YYYY-MM-DD (default: today's UTC date)")
    a = ap.parse_args(argv)
    today = dt.date.fromisoformat(a.today) if a.today else dt.datetime.now(dt.timezone.utc).date()
    errors, warnings = validate(Path(a.file), Path(a.hub), today)
    if a.metadata:
        errors += validate_metadata(Path(a.metadata), Path(a.hub))
    for w in warnings:
        print("WARNING:", w)
    for e in errors:
        print("ERROR:", e)
    print("RESULT:", "PASS (no errors; the hub's own hubValidations Action is authoritative)" if not errors
          else f"FAIL ({len(errors)} error(s))")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
