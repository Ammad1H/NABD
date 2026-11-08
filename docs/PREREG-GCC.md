# Pre-registration: frozen UAE method, GCC out-of-sample test (G12)

Filled from `vendor/nabd_v2_kit/templates/PREREG_GCC_HOLDOUT.md` on 8 Nov 2026 by the data/UAE workstream, BEFORE any data for the holdout countries were downloaded. Locked with kit `prereg.lock` into `docs/LOCK-GCC.json` (this file + `uae/gcc.py`, `uae/models.py`, `uae/models_v2.py`, `uae/features_v2.py`, `uae/scoring.py` + config) and committed; `python3 -m uae.gcc --score` calls `assert_locked` and refuses to score otherwise. Edits after locking go only in section 10.

## 1. Exposure declaration
Has anyone on the team looked at FluNet data for any candidate country? **No, as far as the records show.**
- Searched: git history of this repo, `data/raw/`, and the idea-loop folder `/home/claude/fhdic/loop` for OMN, QAT, BHR, KWT or SAU FluNet use. Only matches: an R1 ideator note that the WHO API "covers SAU, OMN, QAT, KWT, BHR" (no data), and judge text recommending this test.
- FluNet data used so far by the project: ARE (UAE) and USA only.
- General background knowledge (e.g. that Gulf influenza seasons tend to peak in the northern-hemisphere winter) is not data exposure but is acknowledged.
- **Known at lock time:** UAE v2 LOSO results (v2 did not beat v1; see results/uae/SUMMARY-v2.md) and the UAE forward-in-time sensitivity (v1 ≈ persistence forward-in-time). The choice of v1 as the primary method below was made after those UAE results were known. It follows the R2 judges' recommendation (written before v2 existed) to externally validate "the frozen NABD-UAE-v1", and v1 is the frozen headline model of the public ledger.

## 2. What is frozen
- Code: `uae/gcc.py` and the model files listed above at the lock commit; LOCK.json Merkle root recorded in docs/FREEZE.md.
- **Primary method: NABD-UAE-v1** (uae/models.py, frozen as is), applied to each country's own series.
- **Secondary method: NABD-UAE-v2-GCC** = v2 (uae/models_v2.py) with the signals available outside the UAE: sentinel (or total) positivity, testing volume, non-sentinel positivity where the country reports both streams, Ramadan (tabular calendar). **Dropped (UAE-specific): the UAE school calendar** (`school_win` set to 0, contributing nothing). No other signal may be added later.

## 3. Data and inclusion rules (decided before download)
- Source: WHO FluNet, public xMart OData endpoint `VIW_FNT` (columns COUNTRY_CODE, ISO_YEAR, ISO_WEEK, ORIGIN_SOURCE, SPEC_PROCESSED_NB, INF_ALL, RSV), ISO_YEAR ≥ 2015, pulled after the lock via WebFetch (the shell is blocked) into `data/raw/flunet_gcc.csv`, with a SHA-256 and date recorded in data/raw/PROVENANCE.md.
- Pathogens: influenza total (INF_ALL) **primary**; RSV **secondary** where reported.
- Target: weekly % positive (positives / specimens processed).
- Series per country: SENTINEL if the sentinel stream has ≥ 3 qualifying evaluation seasons; otherwise all origins summed (TOTAL).
- **Qualifying season** (ISO wk 27 → wk 26): specimens > 0 and positives reported in ≥ 80% of 52 weeks AND median weekly specimens ≥ 20.
- An evaluation season is scored if it qualifies and the country has ≥ 2 qualifying earlier training seasons (2020/21 excluded from training). A country is included if ≥ 2 flu evaluation seasons are scored.
- Candidate countries: Oman, Qatar, Bahrain, Kuwait, Saudi Arabia (GCC). Other EMRO countries are **not** part of this test.

## 4. Procedure
- Evaluation seasons 2022/23, 2023/24, 2024/25, 2025/26. **Forward-in-time:** at the start of each evaluation season the models are fitted on that country's own qualifying seasons before it (no pooling across countries, no UAE data). Every week of the season is an origin; forecasts use data through the origin only, horizons 1–4 data weeks (issue-relative nowcast, +0.5, +1.5, +2.5 weeks with a 1-week simulated publication lag), exactly as in the UAE track.
- Data are finalised FluNet values (no vintages exist); results are labelled "retrospective, revised data".

## 5. Comparators
- Persistence (uae/models.py `Persistence`, trained on the same seasons).
- Tougher baseline: seasonal analog / climatology (uae/models.py `Analog`).

## 6. Metrics and uncertainty
- **Primary:** relative WIS of NABD-UAE-v1 vs persistence for influenza, pooled over included countries, seasons, origins and horizons (ratio of summed WIS on cells common to all four models).
- Secondary: vs seasonal analog; v2-GCC vs persistence and vs v1; per country; per country-season wins; RSV; 50% and 95% coverage.
- CI: bootstrap over country-seasons, B = 2000, seed = 0.

## 7. Success criterion (confirmatory)
Pooled influenza relative WIS (v1 vs persistence) < 1 AND 95% CI upper bound < 1 → "MET"; otherwise "NOT MET".

## 8. Reporting rules
Every included country is reported, losses included, in one table (`results/gcc/`). The inclusion table lists excluded countries and why. No country, season or horizon is dropped after scoring.

## 9. Sign-off
Data/UAE build agent for the NABD team, 8 Nov 2026. Outside anchors: **not yet** (OpenTimestamps and RFC 3161 servers are blocked from the build sandbox). The user should run `vendor/nabd_v2_kit/scripts/anchor.sh docs/lock_gcc/MANIFEST.sha256` locally and publish; until then the lock time is self-attested (local git).

## 10. Deviations log (empty at lock)
| Date | Deviation | Reason | Effect on interpretation |
| --- | --- | --- | --- |
