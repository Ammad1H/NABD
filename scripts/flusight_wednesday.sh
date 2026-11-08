#!/usr/bin/env bash
# One command for the weekly CDC FluSight hub file from FROZEN NABD v1. Run on Wednesday (US Eastern),
# after the hub's target-data update and before the 11 PM ET deadline.
#
#   scripts/flusight_wednesday.sh 2026-11-14            # reference date = the Saturday after this Wednesday
#   DRY_RUN=1 scripts/flusight_wednesday.sh 2026-11-14  # no network: uses the pinned local hub (stale data, for testing only)
#
# It never submits anything. It writes results/flusight_draft/<date>-NABD-v1.csv, validates it against the
# LIVE hub's tasks.json, and prints the PR steps. Submitting is your decision (docs/PUBLISH.md §5).
set -euo pipefail
REF="${1:?usage: scripts/flusight_wednesday.sh <reference_date YYYY-MM-DD (a Saturday)>}"
cd "$(dirname "$0")/.."
LIVE=external/hub-live
if [[ "${DRY_RUN:-0}" == "1" ]]; then
  echo "[dry-run] using the pinned hub external/hub (data are NOT current; do not submit this file)"
  LIVE=external/hub
else
  if [[ ! -d "$LIVE/.git" ]]; then
    git clone --filter=blob:none --sparse https://github.com/cdcepi/FluSight-forecast-hub.git "$LIVE"
    git -C "$LIVE" sparse-checkout set target-data hub-config model-output/FluSight-ensemble model-output/FluSight-baseline
  fi
  git -C "$LIVE" checkout -q main
  git -C "$LIVE" pull -q --ff-only
  echo "live hub at $(git -C "$LIVE" rev-parse --short HEAD) ($(git -C "$LIVE" log -1 --format=%cI))"
fi
# The research pipeline stays on the pinned hub (external/hub); only this script uses the live clone.
NABD_HUB="$PWD/$LIVE" python3 -m eval.flusight_round --reference-date "$REF" --team NABD --model v1 --out results/flusight_draft
NABD_HUB="$PWD/$LIVE" python3 -m eval.flusight_validate "results/flusight_draft/${REF}-NABD-v1.csv" \
  --metadata results/flusight_draft/NABD-v1.yml --hub "$LIVE" || true
cat <<MSG

Next (manual, only if you decide to participate; see docs/PUBLISH.md §5):
  1. Fork https://github.com/cdcepi/FluSight-forecast-hub and clone your fork.
  2. First time only: copy results/flusight_draft/NABD-v1.yml to model-metadata/NABD-v1.yml
     (fill every PLACEHOLDER; keep designated_model: false).
  3. Copy results/flusight_draft/${REF}-NABD-v1.csv to model-output/NABD-v1/${REF}-NABD-v1.csv
  4. Commit, push, and open a PR using the text in docs/FLUSIGHT-PR.md. The hub's validation Action must pass.
  5. Record the PR URL and the file SHA-256 in ledger/LEDGER.md.
MSG
