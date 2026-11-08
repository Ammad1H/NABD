# PROTOCOL-UAE-v2: multi-signal UAE forecaster, evaluation plan

Version 1.0, written 8 Nov 2026 by the data/UAE workstream. Locked with `vendor/nabd_v2_kit` `prereg.lock` into `docs/LOCK-UAE-v2.json` (plan + code + config + data manifest) and committed **before any v2 score is computed**. `uae/backtest_v2.py` calls `assert_locked` and refuses to score if anything changed.

> **Status label (must accompany every v2 number): RETROSPECTIVE.** v1 (NABD-UAE-v1) results on these same four seasons had already been seen by the team when this protocol was written. The protocol fixes the v2 design and analysis before v2 is scored, but it is not a blind test. The blind tests of the UAE method are (a) the GCC out-of-sample test (`docs/PREREG-GCC.md`) and (b) the prospective public ledger.

## 1. Exposure and what was done before the lock
- Seen: all UAE sentinel FluNet data 2022-W01…2026-W44, all v1 LOSO results (results/uae, commits 969c82c, 463ab09), the US results.
- Seen during design, not scored: non-sentinel FluNet rows (they were in the cached file since 8 Nov; never used in any model or score before this lock).
- The school calendar (data/raw/uae_calendar.csv) was verified from news reports of the MoE/Cabinet calendars on 8 Nov before this lock; rows and URLs are in the file.
- One smoke run (`--smoke`) fitted v2 on four seasons and built features for one origin; it computed no score and printed no forecast-vs-truth comparison.
- Alert thresholds (flu 15%, RSV 10%) and the census fraction 0.6 come from earlier exploratory probes (eval/backtest_probe.py, US rule D3) that saw these seasons. Alert metrics are therefore **diagnostic only**.

## 2. Signals (all weekly, aggregate, public or announced)
| Block | Feature(s) | Source | Availability at origin t |
|---|---|---|---|
| CORE | dy1 = y[t] − y[t−1] | WHO FluNet ARE sentinel positivity (logit, continuity-corrected) | through t |
| CLIM | anom = y[t] − clim(week t); dclim = clim(week t+h) − clim(week t) | training-season climatology of the same series (v1 definition) | known |
| TV | dlogspec = Δ log sentinel specimens | WHO FluNet sentinel SPEC_PROCESSED_NB | through t |
| NS | ns_dy1 = z[t−1] − z[t−2]; ns_gap = z[t−1] − y[t−1] | WHO FluNet ARE **non-sentinel** positivity, same pathogen (from 2023-W15) | through **t−1** (one extra week of lag, as observed in FluNet publication) |
| CAL | school_win = mean MoE winter/spring break fraction over target weeks t+1..t+h; ram_win = mean Ramadan fraction over t+1..t+h | data/raw/uae_calendar.csv (verified rows, winter/spring breaks only; mid-terms excluded because not verified for all seasons); Ramadan from the kit's tabular Islamic calendar (±2 days) | known-future |

Weather is **not** in v2: no source covering 2026 is reachable from the build environment (NOAA, Open-Meteo, Meteostat blocked; a third-party ERA5 mirror on GitHub ends 2025-12-31). `adapters/weather.py --fetch` remains for local use; adding weather later would be a new model (v3) with its own lock.

## 3. Model (frozen)
Per series (flu, RSV) and data horizon h ∈ {1,2,3,4}, ordinary least squares on training seasons:
`y[t+h] − y[t] = b0 + Σ_k b_k x_k`, with x = CORE+CLIM+TV+NS+CAL (9 features + intercept), exactly as implemented in `uae/models_v2.py`. Lag features never cross a season boundary (same rule as v1 after the 463ab09 fix). Predictive quantiles (FluSight 23 levels) = y[t] + x·b + quantiles of residuals from nested leave-one-season-out within the training seasons for the sub-model used.

**Missing-feed behaviour (pre-declared):** sub-models are fitted for {full, −NS, −CAL, −NS−CAL}. At each origin the richest sub-model whose inputs are all present is used (e.g. before 2023-W15, or when the non-sentinel week is late, the −NS sub-model). The sub-model used is logged per forecast. No imputation.

**Explanations (G11):** the median logit = y[t] + b0 + Σ b_k x_k + median residual offset, exactly. `results/uae/explain/<issue_date>_<target>.csv` lists every term (feature, value, beta, contribution in logit units, and the leave-one-term-out percentage-point effect).

## 4. Evaluation design
- **Primary (LOSO):** test seasons 2022/23, 2023/24, 2024/25, 2025/26 (season = ISO wk 27 → wk 26); train on all other seasons (incl. partial 2021/22 and partial 2026/27). Same origins, information rule and 1-week simulated publication lag as v1 (issue = week_end(t) + 11 days; reference date = week_end(t) + 14 days; horizons −1 nowcast, 0, 1, 2 relative to reference date).
- **Sensitivity (forward-in-time):** test 2023/24, 2024/25, 2025/26, training only on earlier seasons. Reported for v1 and v2.
- **Comparators:** NABD-UAE-v1 (frozen as is), persistence, seasonal analog (v1 definitions).
- **Cells:** only (series, season, reference date, horizon) cells where all four models have a scored forecast (fixes audit m18).

## 5. Metrics and uncertainty
- WIS on the percent scale (uae/scoring.py, Bracher et al. 2021), 50%/95% coverage.
- Relative WIS = Σ WIS(A) / Σ WIS(B) on common cells, per series and pooled.
- CIs: (i) date-cluster bootstrap (v1 method), (ii) **moving-block bootstrap of reference dates, block length 4, within season, B = 2000, seed 20261108** (kit `block_bootstrap_ratio`). The moving-block CI is the preferred interval.
- Season wins per series; per-horizon and per-season tables.

## 6. Pre-declared comparisons and how they are read
- **H1 (v2 vs v1):** relative WIS v2/v1 per series and pooled. "v2 improves" only if the pooled point estimate < 1 AND the moving-block 95% upper bound < 1. Otherwise reported as "no demonstrated improvement". Either way the result is published.
- **H2 (v2 vs persistence):** reported per series with CIs.
- No decision depends on the result: **NABD-UAE-v1 stays the frozen headline model of the public ledger; v2 is issued alongside it as the challenger** from ledger round R1 onwards, whatever H1 shows.

## 7. Feed removal, missing feeds and alerts
- **Ablation (refit):** v2 refitted without each block in {NS, CAL, TV, CLIM}; mean WIS on cells common with full v2; delta = without − full (positive = the feed helps). Written to `results/uae/tables/ablation.csv` (contract columns feed, metric, full, without, delta). Null or negative deltas are reported as findings.
- **Missing at forecast time:** (a) NS dropped at prediction (forces the fallback sub-model); (b) latest sentinel week missing (origin t−1 with horizon h+1 for targets t+1..t+3), for v1 and v2.
- **Alert rule (descriptive, n = 4 seasons per series):** onset = first week from ISO wk 27 with sentinel positivity ≥ T for two consecutive weeks (T_flu 15%, T_RSV 10%); eligible series-season if the first 4 weeks are < T. Forecast rule: alert at origin t if the median for target t+2 (+0.5 wk after issue) ≥ T and observed at t < T. Census rule: observed at t in [0.6·T, T). First alert per series-season only. Report lead (weeks from issue to onset week end), sensitivity (0 ≤ lead ≤ 4), PPV, false alarms, premature and late/missed, for v1, v2, v2 with the NS feed dropped, and the census rule (`uae/alerts.py`).

## 8. Reporting rules
Everything in sections 5–7 is reported in `results/uae/SUMMARY-v2.md`, `results/uae/v2/summary.json` and tables, losses included, with the RETROSPECTIVE label. No season, horizon or series is dropped after scoring. Any change after the lock is a deviation in `docs/DEVIATIONS.md` (UAE section) and makes affected numbers exploratory.
