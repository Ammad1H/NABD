# Pre-registration: "borrowed strength" (NABD-Pool), confirmatory test on held-out countries

Written 10 Nov 2026 by the S1 science workstream, BEFORE any FluNet data beyond the seven already-seen countries were downloaded. Two locks protect it (kit `prereg.lock`):
- **Lock #1** (`docs/LOCK-POOL-1.json`): this plan + `pool/config.py` (country lists, rules) + the frozen local-method code it reuses (`uae/models.py`, `uae/scoring.py`, `uae/gcc.py`). Made before any new download.
- **Lock #2** (`docs/LOCK-POOL-2.json`): this plan + all `pool/` code + the chosen model configuration + the development-data manifest. Made after model selection on development countries and BEFORE any held-out row is extracted.
`python3 -m pool.score --confirm` calls `assert_locked` on both and refuses to run otherwise. After lock #1 this file is not edited; deviations go in `docs/DEVIATIONS.md` (section 11).

## 1. Hypothesis
**H1.** For influenza positivity in countries the model has never been fitted on, a model pooled across many countries' WHO FluNet histories (NABD-Pool) forecasts better than a model fitted only to the country's own record (the frozen NABD-UAE-v1 method).
Motivation, known at lock time: on the UAE's own 4-season record v1 only ties persistence forward-in-time, and wins against the past-season pattern only when it has two or more training seasons (results/uae). In the GCC test v1 beat persistence by 9% (results/gcc).

## 2. Exposure declaration
- FluNet data downloaded or examined by the project so far: **ARE, USA, OMN, QAT, SAU, BHR, KWT only** (`data/raw/` holds only these; the GCC download streamed WHO's full export from a GitHub mirror and kept only the five GCC countries' rows).
- No row for any other country has been read, plotted, summarised or scored by anyone on the project, as far as git history, `data/raw/` and the working folders show.
- General background knowledge is acknowledged (temperate countries peak in winter, tropical countries have weaker or double seasons, the 2020/21 season was suppressed by COVID-19 measures).
- The seven seen countries are in the development set, never in the confirmatory set.

## 3. Country sets (fixed in `pool/config.py`, lock #1)
- **Development (46):** countries named from general knowledge as having long-running national influenza surveillance in the Americas, Europe, Western Pacific, South-East Asia and Africa, plus the seven already-seen countries. List: `pool.config.DEV`.
- **Confirmatory held-out (36):** every WHO Eastern Mediterranean Region member not in the development set (16: AFG, DJI, EGY, IRN, IRQ, JOR, LBN, LBY, MAR, PAK, PSE, SOM, SDN, SYR, TUN, YEM), plus 20 pre-named countries from other regions (ISR, GEO, ARM, KAZ, UZB, BGD, LKA, NPL, IDN, VNM, PHL, MYS, KEN, GHA, SEN, ETH, PER, ECU, CRI, PRY). List: `pool.config.HELD`.
- Lists were written without looking at any FluNet metadata for these countries. Data quality is unknown; the mechanical rules in section 4 decide inclusion after download.

## 4. Data and inclusion rules (same as the GCC test unless stated)
- Source: WHO FluNet full export `VIW_FNT_20261003.csv` as mirrored in the public GitHub repo used for the GCC test, pinned to the same commit. Columns COUNTRY_CODE, ISO_YEAR, ISO_WEEK, ORIGIN_SOURCE, SPEC_PROCESSED_NB, INF_ALL, RSV; ISO_YEAR ≥ 2015.
- **Download discipline:** the export is streamed and filtered in memory. Stage A (after lock #1) writes only development-country rows to disk. Stage B (after lock #2) writes held-out rows. The full export is never written to disk; the code path for held-out extraction calls `assert_locked` on lock #2 first.
- Target: weekly % positive for influenza (INF_ALL / SPEC_PROCESSED_NB), primary. RSV secondary where reported.
- Series per country: SENTINEL if the sentinel stream has ≥ 3 qualifying evaluation seasons, else all origins summed.
- Qualifying season (ISO week 27 → week 26, for every country regardless of hemisphere): specimens > 0 and positives reported in ≥ 80% of 52 weeks AND median weekly specimens ≥ 20.
- A held-out evaluation season is scored if it qualifies and the country has ≥ 2 qualifying earlier own seasons (2020/21 excluded), because the local method cannot be fitted on fewer. A country is included if ≥ 1 influenza evaluation season is scored.
- Known limitation, accepted in advance: the week-27 season boundary is a northern-hemisphere convention. It is applied to every model alike.

## 5. Procedure (forward-in-time)
- Evaluation seasons 2022/23, 2023/24, 2024/25, 2025/26. Every week of an evaluation season is an origin. Forecasts use data through the origin only. Horizons: 1–4 data weeks after the last published week (nowcast and +1, +2, +3 weeks after issue with a one-week simulated publication lag), exactly as in the GCC test.
- **NABD-Pool** for evaluation season S is fitted on development countries' qualifying seasons before S (2020/21 excluded). It is **never fitted on any held-out country's evaluation season**. Its inputs for a held-out country come from that country's own data up to the origin. A candidate may also use the held-out country's own qualifying seasons before S (partial pooling), which is the same information the local method uses.
- **Local method:** NABD-UAE-v1 (`uae/models.py`, frozen), fitted per country on its own qualifying seasons before S.
- Data are finalised FluNet values (no vintages exist); results are labelled "retrospective, revised data".

## 6. Model selection (development countries only)
- Candidates: (K) the kit `GlobalQuantileGBM` on % positivity; (G) a gradient-boosted quantile model of the logit change with cross-country features (own lags and growth, anomaly from own past-season pattern, season phase, absolute latitude and hemisphere, testing volume and its change, number of own prior seasons); (L) a partial-pooling logit-linear model (v1's form with coefficients pooled across development countries and shrunk towards the country's own fit); and quantile-average ensembles of these.
- Selection: forward-in-time on development countries with the target country left out of the fit (grouped folds), on evaluation seasons 2022/23–2025/26. The candidate with the lowest pooled relative WIS against local v1 is chosen. An ensemble member is admitted only if it beats persistence on development data.
- All tuning uses development countries only. The chosen model, its hyperparameters and the code are hashed in lock #2 before any held-out row exists on disk.

## 7. Comparators
Local NABD-UAE-v1; persistence; seasonal analog (past-season pattern). All from `uae/models.py`, fitted on the country's own prior qualifying seasons.

## 8. Endpoints
- **Primary (confirmatory):** relative WIS of NABD-Pool vs local v1 for influenza, pooled over all included held-out countries, seasons, origins and horizons (ratio of summed WIS on cells common to all four models). 95% CI by country-clustered bootstrap (resample countries, B = 2000, seed 0). **Success ("MET"): ratio < 1 and CI upper bound < 1.** Otherwise "NOT MET".
- **Key secondaries (in this order):**
  1. *Short-history stratum:* the same ratio restricted to country-seasons where the country has ≤ 2 own qualifying prior seasons.
  2. *Simulated short record:* the whole test re-run with every model allowed to see only the country's last 2 qualifying seasons before S (local v1 fitted on those 2; Pool's own-history inputs computed from those 2). This puts every held-out country in the UAE's position.
  3. NABD-Pool vs persistence, and vs seasonal analog.
- **Other secondaries:** EMRO-only and other-regions-only ratios; mean of per-country log ratios; per-country and per-country-season wins; per horizon; 50% and 95% coverage; RSV (all of the above) where a country qualifies on RSV.
- **Non-confirmatory (already-seen countries):** NABD-Pool vs v1 on ARE and on OMN, QAT, SAU, with the target country left out of the pooled fit. Labelled as non-confirmatory everywhere.

## 9. Reporting rules
Every held-out country appears in the inclusion table with the reason if excluded. Every included country is reported, losses included. No country, season or horizon is dropped after scoring. The confirmatory scoring is run once.

## 10. Sign-off
S1 science build agent for the NABD team, 10 Nov 2026. Outside anchors: not possible from the build sandbox; lock times are self-attested in local git until the user runs `scripts/anchor_all.sh` and pushes.

## 11. Deviations
Logged in `docs/DEVIATIONS.md` (P-series), because editing this file would break the locks.
