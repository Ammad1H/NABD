# PUBLISH: make NABD checkable (about 15 minutes, on your laptop)

Until you do this, every "locked before", "frozen" and "ledger" claim is **self-attested**: it rests on commits we made ourselves. These steps make the claims checkable by anyone. Do them **in this order**, ideally before the 10 Nov registration and certainly before the 20 Nov submission. Every script supports `DRY_RUN=1`; the dry-run outputs from the build sandbox are recorded at the bottom.

Prerequisites: git, Python ≥ 3.11, the GitHub CLI (`gh`) and a GitHub account. `pip install -r requirements-dev.txt opentimestamps-client`.

## 1. Verify the GCC data against WHO (2 min). Do this first
```bash
python -m adapters.gcc_verify        # pulls OMN, QAT, SAU, BHR, KWT from the official WHO xMart API and compares every row
```
Exit 0 means every row of `data/raw/flunet_gcc.csv` matches the official API. Append a row to `docs/DEVIATIONS.md` (GCC section) recording "full official re-pull: N/N rows identical, <UTC time you observed>", and commit. Exit 1 means differences: **stop**, re-score under the same lock (`python -m uae.gcc --score`), and log every difference before publishing anything.

## 2. Tests and the integrity checks (2 min)
```bash
pytest -q
python -c "from eval import run_all; print(run_all.assert_hub_pinned())"   # needs external/hub; skip if you haven't cloned it
```

## 3. Public repo with full history (3 min)
```bash
scripts/prepare_public_repo.sh            # clean clone with history -> ../nabd-public, plus size/licence/secret/banned-claim checks
gh auth login                             # once
gh repo create <your-github-user>/nabd --public --source ../nabd-public --remote origin --push
```
- Full history is pushed on purpose: the lock and freeze commits are part of the evidence.
- Review the script's "banned-claim scan" and "email" output before pushing.
- Pushing makes the commit **contents** public. Commit **times** are still self-attested, which is what step 4 fixes.

## 4. Anchor everything outside the team (3 min, plus one upgrade a few hours later)
```bash
cd ../nabd-public
scripts/anchor_all.sh                     # verifies manifests, builds anchors/<UTC>_all bundle (all locks, freeze, ledger, git HEAD), stamps with OpenTimestamps + FreeTSA
git add anchors docs/lock_* ledger/rounds && git commit -m "Outside anchors" && git push
# a few hours later (Bitcoin confirmation):
for f in $(git ls-files '*.ots'); do ots upgrade "$f"; done; git commit -am "OTS upgrade" && git push
```
- Optional but recommended: in GitHub, **Settings → Integrations → Zenodo**, then create a GitHub release. Zenodo archives it with a DOI and a dated record.
- Post the bundle Merkle root, the git HEAD and the repo URL publicly (LinkedIn/X).
- **What this proves:** the files existed no later than the anchor time. It does **not** backdate anything. Say "locked in git on 8 Nov; externally timestamped on ⟨date⟩".
- After this, and only after it, the pitch may say "published" and "externally timestamped" (update `pitch/` and the app wording).

## 5. Public app (Streamlit Community Cloud, 3 min)
1. https://share.streamlit.io → New app → choose `<your-github-user>/nabd`, branch `main`, main file `app/streamlit_app.py`.
2. Advanced settings → Python 3.12 or 3.13. It installs the root `requirements.txt`, and `.streamlit/config.toml` sets the theme.
3. Note: Cloud storage is **ephemeral and public**. Anyone can click Approve/Dismiss, and the audit log resets on restart. Present it as a demo, not as operational records.
4. Put the URL in the README, the registration/submission text and the one-pager.

Local alternative: `docker compose up --build` (app on :8501, API on :8000).

## 6. CDC FluSight hub, Wednesday 11 Nov (optional; your decision)
```bash
scripts/flusight_wednesday.sh 2026-11-14   # live hub clone (external/hub-live), frozen v1 forecast, validation against the LIVE tasks.json
```
- The research pipeline stays on the **pinned** hub (`external/hub`); only this script uses the live clone (via `NABD_HUB`).
- Fill every `PLACEHOLDER` in `results/flusight_draft/NABD-v1.yml` and keep **`designated_model: false`** (v1 did not meet non-inferiority).
- Fork the hub, add the metadata and forecast files, and open a PR with the text in `docs/FLUSIGHT-PR.md`. The hub's own validation Action is authoritative; `eval/flusight_validate.py` re-implements its main checks.
- Run it after the hub's Wednesday target-data update. If the script prints `stale weeks: 1`, the new week isn't in yet; wait and re-run.

## 7. Weekly from then on
See `docs/RUNBOOK.md` (`python -m ledger.weekly`), then `scripts/anchor_all.sh` for each new round, before WHO publishes its first target week.

---
## Dry-run record (build sandbox, 2026-11-08, no network to WHO/OpenTimestamps; GitHub reachable)
- `eval/run_all.assert_hub_pinned()` → `d03574028ece110013c6284d3012ac4bef03ded7` (pinned).
- `scripts/flusight_wednesday.sh 2026-11-14` (**live** hub clone; hub `main` was at `d0357402`, 2026-11-06): wrote `results/flusight_draft/2026-11-14-NABD-v1.csv`, 4,876 rows, sha256 `e77fdace…3add`. Vintage 2026-11-04, data through 2026-10-31, **stale weeks: 1** (that week's data were not yet in the hub on 8 Nov; re-run on Wednesday). Validator: file PASS; metadata FAIL only on PLACEHOLDER values (expected).
- `DRY_RUN=1 scripts/anchor_all.sh`: all 3 existing manifests verify intact; bundle of 28 files built (Merkle root `4883429d…83f1` at HEAD `01f7d2f`; the real run will differ because HEAD changes). 4 stamp commands printed.
- `scripts/prepare_public_repo.sh`: see the output recorded in docs/BUILD-LOG.md (round 4, ops).
