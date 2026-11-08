#!/usr/bin/env bash
# Prepare a clean, checkable public copy of the NABD repo WITH its full git history (the lock/freeze
# commits are part of the evidence, so an archive without history is not enough).
#
#   scripts/prepare_public_repo.sh [OUT_DIR]      # default OUT_DIR: ../nabd-public
#
# Never pushes. It clones only COMMITTED files (external/, data/cache/ and other gitignored paths never
# leave), then checks size, licence, secrets and banned claims, and prints the exact push commands.
set -euo pipefail
cd "$(dirname "$0")/.."
SRC="$PWD"
OUT="${1:-$(dirname "$SRC")/nabd-public}"
ERR=0
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo "WARNING: uncommitted changes to tracked files will NOT be in the public copy. Commit them first." >&2
fi
OUT_ABS="$(cd "$(dirname "$OUT")" && pwd)/$(basename "$OUT")"
case "$OUT_ABS" in
  "$SRC"|"$SRC"/*|"$HOME"|"/"|"$(dirname "$SRC")") echo "Refusing to delete $OUT_ABS (unsafe OUT_DIR)" >&2; exit 2;;
esac
if [[ -e "$OUT_ABS" && ! -d "$OUT_ABS/.git" ]]; then echo "Refusing: $OUT_ABS exists and is not a previous public clone" >&2; exit 2; fi
rm -rf "$OUT_ABS"
git clone -q --no-local "$SRC" "$OUT"
git -C "$OUT" remote remove origin
echo "== clean clone: $OUT  (HEAD $(git -C "$OUT" rev-parse --short HEAD), $(git -C "$OUT" rev-list --count HEAD) commits)"

echo "== size"
du -sh "$OUT" | sed 's/^/  total (incl. .git): /'
du -sh "$OUT/.git" | sed 's/^/  .git: /'
BIG=$(cd "$OUT" && git ls-files -z | xargs -0 -I{} find {} -maxdepth 0 -size +50M 2>/dev/null || true)
if [[ -n "$BIG" ]]; then echo "  WARNING: files over 50 MB (GitHub warns; hard limit 100 MB):"; echo "$BIG" | sed 's/^/    /'; fi
HUGE=$(cd "$OUT" && git ls-files -z | xargs -0 -I{} find {} -maxdepth 0 -size +95M 2>/dev/null || true)
if [[ -n "$HUGE" ]]; then echo "  ERROR: files over 95 MB cannot be pushed to GitHub:"; echo "$HUGE"; ERR=1; fi
echo "  results/forecasts is $(du -sh "$OUT/results/forecasts" | cut -f1): kept (needed to verify the US scores without re-running; regenerate with 'python -m eval.run_all --fetch')"

echo "== licence"
for f in LICENSE README.md; do
  if [[ -f "$OUT/$f" ]]; then echo "  ok: $f"; else echo "  ERROR: $f missing"; ERR=1; fi
done

echo "== secrets scan (tracked files)"
PAT='(BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|ghp_[A-Za-z0-9]{20,}|github_pat_|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|xox[bap]-|api[_-]?key *[:=] *["'"'"'][A-Za-z0-9]{12,})'
if (cd "$OUT" && git grep -nIE "$PAT" -- . ':!scripts/prepare_public_repo.sh') ; then
  echo "  ERROR: possible secrets above"; ERR=1
else
  echo "  none found"
fi
EM=$(cd "$OUT" && git grep -nIoE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' -- . ':!vendor' | grep -v -E 'noreply|example|PLACEHOLDER|nabd-build@local' || true)
if [[ -n "$EM" ]]; then echo "  REVIEW: email addresses in tracked files (remove personal ones if unintended):"; echo "$EM" | head -20 | sed 's/^/    /'; fi

echo "== banned-claim scan (BUILD-SPEC v1.7; review each hit, fix wording before publishing)"
CLAIMS='verified row-for-row|fewer false alarms|outside-anchored|externally anchored|3/3 onsets|nobody publishes|is published|publicly timestamped'
(cd "$OUT" && git grep -nIiE "$CLAIMS" -- pitch app docs/TECHNICAL.md docs/SPEC.md README.md research/positioning.md 2>/dev/null \
   | grep -v -iE 'banned|stop[- ]list|do not claim|not yet|until|never|BANNED' | head -40 | sed 's/^/  /') || true
echo "  (also check the word 'blind' and 'calibrated' in context; see research/positioning.md 'What NOT to claim')"

echo "== internal documents you may choose to keep private (they are in history; deciding now is easier than rewriting later)"
(cd "$OUT" && ls docs/REVIEW-*.md pitch/outreach.md 2>/dev/null | sed 's/^/  /') || true
echo "  Keeping the reviews public is defensible (they show the audit trail); outreach drafts name roles, not people."

echo "== placeholders still to fill"
(cd "$OUT" && git grep -nI 'PLACEHOLDER\|⟨' -- pitch results/flusight_draft README.md 2>/dev/null | head -15 | sed 's/^/  /') || true

cat <<MSG

Next (manual; see docs/PUBLISH.md):
  gh auth login                                   # once
  gh repo create <your-github-user>/nabd --public --source "$OUT" --remote origin --push
  # then, from the public copy, anchor everything outside the team:
  cd "$OUT" && pip install opentimestamps-client && scripts/anchor_all.sh && git add anchors docs/lock_* ledger/rounds && git commit -m "Outside anchors" && git push
MSG
exit $ERR
