#!/usr/bin/env bash
# Anchor EVERY lock, freeze and ledger manifest outside the team in one go (OpenTimestamps + RFC 3161).
#
#   scripts/anchor_all.sh            # laptop with internet: builds a bundle manifest and stamps everything
#   DRY_RUN=1 scripts/anchor_all.sh  # no network: builds the bundle in a temp dir and prints what would be stamped
#
# What it does:
#  1. verifies every existing manifest (nothing changed since it was written);
#  2. builds anchors/<UTC>_all/MANIFEST.{json,sha256}: a Merkle bundle over the US protocol + freeze + frozen
#     config, the UAE-v2 and GCC protocols and locks, all ledger rounds, and the current git HEAD;
#  3. stamps the bundle and each existing manifest with OpenTimestamps (Bitcoin) and FreeTSA (RFC 3161).
# An anchor proves the files existed NO LATER than the anchor time; it cannot backdate anything.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="vendor/nabd_v2_kit${PYTHONPATH:+:$PYTHONPATH}"
STAMP="$(date -u +%Y-%m-%dT%H%MZ)"
HEAD="$(git rev-parse HEAD)"
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo "WARNING: uncommitted changes to tracked files; commit first so the anchored HEAD matches the files." >&2
fi

echo "== 1. verify existing manifests"
for m in docs/lock_*/MANIFEST.json ledger/rounds/*/MANIFEST.json; do
  [[ -f "$m" ]] || continue
  printf '%s: ' "$m"; python3 -m nabd_kit.ledger verify "$m" --base .
done

echo "== 2. bundle manifest"
PATHS=(docs/PROTOCOL.md docs/FREEZE.md models/config.yaml docs/PROTOCOL-UAE-v2.md docs/PREREG-GCC.md
       docs/LOCK-UAE-v2.json docs/LOCK-UAE-v2.data-manifest.txt docs/LOCK-GCC.json docs/DEVIATIONS.md)
for f in docs/lock_*/MANIFEST.sha256 ledger/rounds/*/MANIFEST.sha256 ledger/*.csv ledger/*.sha256 ledger/*.meta.json; do
  [[ -f "$f" ]] && PATHS+=("$f")
done
if [[ "${DRY_RUN:-0}" == "1" ]]; then OUT="$(mktemp -d)/${STAMP}_all"; else OUT="anchors/${STAMP}_all"; fi
python3 - "$OUT" "$HEAD" "${PATHS[@]}" <<'PY'
import sys
from nabd_kit import ledger
out, head, paths = sys.argv[1], sys.argv[2], sys.argv[3:]
m = ledger.build_manifest(paths, ".", meta={"git_head": head, "purpose": "NABD outside anchor bundle"})
mj, ms = ledger.write_manifest(m, out)
print(f"bundle: {ms}  files={len(m['files'])}  merkle_root={m['merkle_root']}  git_head={head}")
PY

echo "== 3. stamp"
TARGETS=("$OUT/MANIFEST.sha256")
for f in docs/lock_*/MANIFEST.sha256 ledger/rounds/*/MANIFEST.sha256; do [[ -f "$f" ]] && TARGETS+=("$f"); done
for t in "${TARGETS[@]}"; do
  if [[ "${DRY_RUN:-0}" == "1" ]]; then
    echo "[dry-run] would run: bash vendor/nabd_v2_kit/scripts/anchor.sh $t"
  else
    bash vendor/nabd_v2_kit/scripts/anchor.sh "$t"
  fi
done

cat <<MSG

Done. Next:
  git add anchors docs/lock_* ledger/rounds && git commit -m "Outside anchors ${STAMP}" && git push
  In a few hours: for f in \$(git ls-files '*.ots'); do ots upgrade "\$f"; done; then commit and push again.
  Post publicly (LinkedIn/X/README): the bundle Merkle root printed above, the git HEAD ${HEAD}, and the repo URL.
  Optional: create a GitHub release and mint a Zenodo DOI (GitHub-Zenodo integration) for a citable, dated archive.
MSG
