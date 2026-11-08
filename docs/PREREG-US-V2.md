# DRAFT pre-registration: NABD US v2, prospective 2026/27 test (NOT LOCKED)

Status: **draft for the user**, written 8 Nov 2026 by the round-2 modelling builder. Not locked, anchored or built. It follows the vendored kit template `vendor/nabd_v2_kit/templates/PREREG_US_V2.md`. It is optional and serves integrity only: before 30 Nov only about 1–2 rounds (reference dates 14 and 21 Nov) can be scored, so v2 cannot produce evidence in time for judging. **v1 keeps running unchanged alongside v2.** A v2 must never be scored retrospectively on 2024/25–2025/26 as a claim: those seasons are now development data.

## 1. Frozen spec (to fill in, then lock)
- **v2** = `GroupedRecalibrator( quantile_average([members]) )`, all from vendor/nabd_v2_kit. Candidate members:
  - v1 (NABD-ensemble, frozen);
  - `GlobalQuantileGBM` on NHSN state admissions, with `source` = NHSN only unless ILINet/NSSP vintages are added;
  - flat baseline (`baselines.flat_baseline`).
- **Development seasons:** 2023/24, 2024/25 and 2025/26 (all already seen). Use vintage-correct inputs throughout (`models.data.series_as_of`).
- **Member-inclusion rule (development seasons only, fixed before fitting):** drop any member whose pooled development relative WIS vs FluSight-baseline is > 1.0. Weights are equal.
- **Recalibrator:** groups = as-of phase (kit `phase.asof_log_slope`, window 3, band 0.1, offset 1.0) × horizon, with `min_n` = 200. Fit on development forecasts only, then save `to_json()` and hash it into the lock.
- **Live online calibration:** `QuantileTracker`, lr 0.1, groups = horizon. Updates only when truth exists.
- **Guardrail:** `CalibrationMonitor`, window 8, `fallback_rel_wis` 1.25 vs FluSight-baseline. In fallback, the headline is the baseline forecast, with a banner.
- **Recorded in the lock:** code commit, LOCK.json Merkle root, and the hub commit for the GBM training data.

## 2. Hypotheses (prospective 2026/27; reference dates from the first after the lock to 2027-05-29)
- **H1 (primary):** relative WIS of v2 vs the CDC FluSight-ensemble ≤ 1.15. This is the same bar v1 missed.
- **H2:** in as-of rising weeks, v2/ensemble < 1. This tests, prospectively, the question v1's exploratory finding E1 raised.
- **H3:** v2 improves on v1 (v2/v1 < 1).

## 3. Data
- **Truth:** hub target data as published 4 weeks after each target week. Final-release truth is a sensitivity analysis.
- **Inputs:** only data available at each Wednesday deadline.

## 4. Analysis
- Pairwise relative WIS on the overlap of forecasts.
- **CI:** circular moving-block bootstrap over reference dates (block 4, B 2000, seed 20261108), as in D6/D11.
- **Sensitivity analyses** (never primary): without the national series; per state; WIS decomposition by phase.

## 5. Interim looks
Weekly scores are published as descriptive. No confirmatory claim before the season ends. v2 is not changed during the season; a fix becomes v3 with its own lock.

## 6. Lock procedure (before the first v2 forecast)
1. Fill every field above.
2. Run `prereg.lock(LOCK.json, [this file], [code files], config, data_manifest)` and `python -m nabd_kit.ledger build lock_us_v2/ ...`.
3. Commit, push to the public repo, and anchor `MANIFEST.sha256` outside the team (OSF/Zenodo/OpenTimestamps; `vendor/nabd_v2_kit/scripts/anchor.sh`).
4. Call `prereg.assert_locked(...)` at the top of the v2 scoring script.

## 7. Deviations log (empty at lock)
| Date | Deviation | Reason | Effect on interpretation |
| --- | --- | --- | --- |
