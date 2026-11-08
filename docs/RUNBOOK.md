# NABD weekly operations runbook

Who runs this: the team (Ammad), on a laptop with internet access. The build sandbox can't reach WHO, the CDC hub's live updates or the timestamp services.

Rule: **nothing is posted, pushed or submitted automatically.** Every public act is a command you type.

---

## 0. One-time setup

```bash
git clone <your public repo> nabd && cd nabd
pip install -r requirements-app.txt pandas numpy scipy statsmodels pandera pyyaml pytest   # + opentimestamps-client
python -m pytest -q                       # everything passes before you touch live data
```

Anchor the existing locks and round R1 once, following `ledger/ANCHOR.md`: UAE v2 lock, GCC lock and ledger R1.

## 1. UAE ledger: every week, after WHO publishes a new UAE week (usually 7–11 days after the week ends)

```bash
python -m adapters.flunet --fetch --save         # refresh data/raw/flunet_are.csv from WHO xMart
python -m ledger.weekly --cached                 # score past rounds; issue R<n+1> ONLY if a newer week exists
```

`ledger.weekly` is **idempotent**. It prints the latest round, its `data_through` week, the newest published week, and whether it issued a round. Running it twice in a row never creates a duplicate round. Use `--no-issue` to score only.

If it issued a round, the commands to type next are printed:

```bash
git add ledger results/uae/explain && git commit -m "ledger R<n>" && git push
bash vendor/nabd_v2_kit/scripts/anchor.sh ledger/rounds/<UTC>_R<n>/MANIFEST.sha256
# a few hours later: ots upgrade ledger/rounds/<UTC>_R<n>/MANIFEST.sha256.ots ; commit + push the .ots/.tsr
```

Then post the round's Merkle root publicly (pitch/outreach.md has the template). **Anchor before WHO publishes the first target week**, or the round proves nothing.

**What gets written:** forecast CSVs for v1 (headline), v2 (challenger) and persistence, each with a `.sha256` and a `.meta.json` (horizons labelled nowcast/+0.5/+1.5/+2.5 wk from the issue date, matching the card). Also written: a Merkle manifest in `ledger/rounds/`, and the per-signal explanation of the v1 forecast in `results/uae/explain/<issue_date>_<target>.csv` (v2's goes in `challenger_v2/`). The scoreboard is `ledger/SCOREBOARD.md`.

Note: the R0 and R1 `.meta.json` files predate the issue-relative horizon convention, which started in round 3. They are hashed and are left unchanged. The forecast values and target weeks are unaffected.

To regenerate explanation files only (no ledger write): `python -m ledger.issue --cached --round R<n> --explain-only --issue-date YYYY-MM-DD`.

## 2. CDC FluSight hub: Wednesdays, only if you decide to submit (`docs/FLUSIGHT-PARTICIPATION.md`)

Deadline: Wednesday 11 PM US Eastern (Thursday 08:00 GST); `reference_date` = the following Saturday.

```bash
git -C external/hub checkout main && git -C external/hub pull        # live hub data (unpinned)
python -m eval.flusight_round --reference-date <Saturday> --team <TEAM> --model <MODEL>
# copy the CSV into your fork of cdcepi/FluSight-forecast-hub under model-output/<TEAM>-<MODEL>/ and open a PR
```

Submit frozen v1 as `designated_model: false` (it missed non-inferiority). Never change v1 mid-season; a fix becomes a new, separately locked model.

## 3. App and API (demo or judging)

```bash
streamlit run app/streamlit_app.py      # UI on :8501
uvicorn app.api:app --port 8000          # API on :8000, docs at /docs
```

## 4. Pilot partner data (when a partner shares an export)

```bash
python -m adapters.pilot validate path/to/partner_export.csv   # schema, k>=10 + complementary suppression
```

Follow the governance checklist in `docs/PILOT-DATA-SPEC.md` §4 before any real file is copied. Partner data never goes into the public repo.

## 5. Before publishing the repo (one time)

```bash
python -m adapters.gcc_verify      # compare the scored GCC file with the official WHO API; exit 1 = re-score under the same lock
python -m adapters.weather --fetch # optional: real Abu Dhabi weather (not used by any scored model yet)
python -m eval.run_all --cached    # US pipeline reproduces committed results
python -m pytest -q
```

## 6. Dry run record (sandbox, 8 Nov 2026, cached data)

```
$ python -m ledger.weekly --cached
{"scored_rows": 0, "excluded_files": [], "latest_round": "R1",
 "latest_round_data_through": "2026-W44", "latest_published_week": "2026-W44", "issued": null}
No new FluNet week since the last round: nothing issued (idempotent).
$ python -m ledger.weekly --cached        # second run: identical output, no new files
$ python -m adapters.pilot validate data/pilot/SYNTHETIC_pilot_example.csv
OK: 624 rows, 278 cells suppressed (k=10), synthetic=True
```

Scored rows = 0 is expected: no target week of R0 or R1 (issued with data through 2026-W44) has been published by WHO yet.
