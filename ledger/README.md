# NABD public forecast ledger

**Purpose:** an integrity device. Every UAE forecast is frozen and hashed *before* its target week is published by WHO, so nobody (including us) can move the goalposts. It is **not** the statistical evidence; that is the retrospective backtest in `results/`.

## Issue a round
```bash
python3 -m ledger.issue --fetch --round R1      # locally: pulls the newest WHO FluNet UAE week first
# (cloud sandbox: python3 -m ledger.issue --cached --round R0 uses data/raw/flunet_are.csv)
git add ledger && git commit -m "NABD ledger round R1" && git push    # to a PUBLIC repo
```
Then post the SHA-256 printed (also in `ledger/LEDGER.md`) publicly, e.g. on LinkedIn/X with the repo link. **The public commit time is the timestamp.** A round that has not been pushed is not public, and its timestamp proves nothing.

From R1, each round writes files for `NABD-UAE-v1` (**headline**, frozen as-is), `NABD-UAE-v2` (**challenger**, locked by docs/LOCK-UAE-v2.json) and the `persistence` baseline, plus a round manifest `rounds/<UTC>_<round>/MANIFEST.{json,sha256}` (SHA-256 of every file plus a Merkle root; anchor it outside the team as described in `ANCHOR.md`) and an exact explanation of the live v2 forecast in `results/uae/explain/<issue_date>_<target>.csv`. Per model:
- `<UTC>_<model>.csv`: FluSight-style quantiles (percent positivity), interface-contract columns;
- `<UTC>_<model>.sha256`: hash of the CSV;
- `<UTC>_<model>.meta.json`: issue time, the data-through week, and issue-relative horizon labels.

Horizons follow FluSight conventions relative to `reference_date` (= the Sunday two weeks after the last published week L):
- `-1` = target week L+1 (nowcast: the target week may still be in progress at issue time, e.g. R0/R1 were issued on the Sunday that ends it);
- `0` = about +0.5 wk after issue;
- `1` = about +1.5 wk;
- `2` = about +2.5 wk.

## Score past rounds
```bash
python3 -m ledger.score --fetch      # or --cached
```
This recomputes every file's SHA-256 against its `.sha256`. Mismatched or unhashed files are **excluded**, never scored. It then scores rows whose target week WHO has since published (WIS, 50%/95% interval hits) and writes `ledger/scores.csv` and `ledger/SCOREBOARD.md`.

## Cadence
WHO FluNet published UAE sentinel week 2026-W44 by 8 Nov 2026 (about 7 days after the week ended). Re-issue weekly as soon as a new week appears. Never edit an issued file; issue a new round instead.

## Status of R0 (8 Nov 2026, 06:51 UTC)
- Issued from the cached copy, with data through **2026-W44**. **Not yet public**: it becomes public when the user pushes it.
- Caveat: W44 is a first release. Sentinel RSV dropped from 15.6% (W43) to 10.5% (W44, 36/342), which may partly reflect incomplete reporting. The model takes the value at face value.


## Known facts about the first rounds (audit R3 #11, ledger honesty)
- **R0 (2026-11-08 06:51Z) and R1 (2026-11-08 12:12Z) are the same forecast issued twice.** The `NABD-UAE-v1` and `persistence` CSVs of R0 and R1 are byte-identical (`cmp` returns no difference): both use data through 2026-W44 and the frozen v1 model, so re-issuing changes nothing. R1 adds the `NABD-UAE-v2` challenger file and a round manifest. Describe the ledger as **one forecast round (issued twice), plus a v2 challenger**, not as two independent rounds.
- **Horizon labels in R0/R1 metadata are legacy.** Their `.meta.json` files say "+1.0 / +2.0 / +3.0 wk" and "nowcast (target week already ended at issue)". Those files are hashed, so they are left unchanged. The skill numbers (backtests) assume issue at L_end + 11 days, which gives the issue-relative labels nowcast / +0.5 / +1.5 / +2.5 wk. Rounds issued from R2 onward carry the issue-relative labels (`ledger/issue.py: horizon_label`). The nowcast target week of R0/R1 (ending 2026-11-08) had **not** ended at issue (06:51Z and 12:12Z that Sunday).
- **Nothing here is public yet.** Every round has `public: false` until the repo is pushed and the manifests are anchored (docs/PUBLISH.md).
