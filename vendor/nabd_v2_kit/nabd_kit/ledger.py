"""Forecast ledger: hash everything a lock or a weekly forecast covers.

A manifest lists every file with its SHA-256 and size, plus a Merkle root over
the file hashes (ordered by relative path; pairs hashed as SHA-256(left||right)
on raw bytes; an odd node is paired with itself). The MANIFEST.sha256 file is in
`sha256sum` format, and it is the file to timestamp outside the team
(OpenTimestamps, RFC 3161, Zenodo): see scripts/anchor.sh.

The `created_utc` field is self-attested. Only the outside anchor proves when
the manifest existed.

CLI:
  python -m nabd_kit.ledger build OUT_DIR PATH [PATH ...]
  python -m nabd_kit.ledger verify OUT_DIR/MANIFEST.json
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

CHUNK = 1 << 20


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_csv_bytes(df: pd.DataFrame, sort_cols=None, float_format: str = "%.10g") -> bytes:
    """Deterministic CSV bytes for a forecast table (sorted rows and columns)."""
    d = df.copy()
    d = d[sorted(d.columns)]
    cols = list(sort_cols) if sort_cols else list(d.columns)
    d = d.sort_values(cols, kind="mergesort").reset_index(drop=True)
    return d.to_csv(index=False, float_format=float_format, lineterminator="\n").encode("utf-8")


def merkle_root(hex_hashes) -> str:
    level = [bytes.fromhex(h) for h in hex_hashes]
    if not level:
        return sha256_bytes(b"")
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [hashlib.sha256(level[i] + level[i + 1]).digest() for i in range(0, len(level), 2)]
    return level[0].hex()


def _expand(paths) -> list[Path]:
    files = []
    for p in map(Path, paths):
        if p.is_dir():
            files.extend(sorted(x for x in p.rglob("*") if x.is_file() and "__pycache__" not in x.parts))
        elif p.is_file():
            files.append(p)
        else:
            raise FileNotFoundError(p)
    return files


def build_manifest(paths, base_dir=".", meta: dict | None = None) -> dict:
    base = Path(base_dir).resolve()
    entries = []
    for f in _expand(paths):
        rel = f.resolve().relative_to(base).as_posix()
        entries.append({"path": rel, "sha256": sha256_file(f), "bytes": f.stat().st_size})
    entries.sort(key=lambda e: e["path"])
    return {"schema": "nabd-ledger/1", "created_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "base_dir": str(base), "files": entries,
            "merkle_root": merkle_root([e["sha256"] for e in entries]), "meta": meta or {}}


def write_manifest(manifest: dict, out_dir) -> tuple[Path, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    mj = out / "MANIFEST.json"
    mj.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    ms = out / "MANIFEST.sha256"
    lines = [f"{e['sha256']}  {e['path']}" for e in manifest["files"]]
    lines.append(f"{manifest['merkle_root']}  MERKLE_ROOT")
    ms.write_text("\n".join(lines) + "\n")
    return mj, ms


def verify_manifest(manifest_json, base_dir=None) -> list[str]:
    """Re-hash every listed file. Returns problems; an empty list means intact."""
    m = json.loads(Path(manifest_json).read_text())
    base = Path(base_dir or m["base_dir"])
    problems = []
    for e in m["files"]:
        f = base / e["path"]
        if not f.is_file():
            problems.append(f"missing: {e['path']}")
        elif sha256_file(f) != e["sha256"]:
            problems.append(f"changed: {e['path']}")
    if merkle_root([e["sha256"] for e in m["files"]]) != m["merkle_root"]:
        problems.append("merkle root does not match the listed hashes")
    return problems


def _main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m nabd_kit.ledger")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("out_dir")
    b.add_argument("paths", nargs="+")
    b.add_argument("--base", default=".")
    v = sub.add_parser("verify")
    v.add_argument("manifest")
    v.add_argument("--base", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "build":
        mj, ms = write_manifest(build_manifest(a.paths, a.base), a.out_dir)
        root = json.loads(mj.read_text())["merkle_root"]
        print(f"wrote {mj} and {ms}\nmerkle root {root}\nnext: scripts/anchor.sh {ms}")
        return 0
    problems = verify_manifest(a.manifest, a.base)
    print("\n".join(problems) if problems else "intact: every file matches the manifest")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(_main())
