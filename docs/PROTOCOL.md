# NABD Pre-registered Evaluation Protocol: US-A (state weekly flu admissions)

Version 1.0 · written 8 Nov 2026 · frozen before any test-season score is computed (see docs/FREEZE.md).
Changes after the freeze are made ONLY via docs/DEVIATIONS.md, with date and reason.

## 1. Data
- **Source:** CDC FluSight forecast hub, github.com/cdcepi/FluSight-forecast-hub, commit `d03574028ece110013c6284d3012ac4bef03ded7` (cloned 8 Nov 2026 into `external/hub`).
- **Target:** `wk inc flu hosp` = weekly count of new laboratory-confirmed influenza hospital admissions (NHSN), by location.
- **Locations:** all 53 hub locations (50 states, DC, PR and `US` national), as they appear in `target-data/time-series.csv`.
- **Real-time data:** `target-data/time-series.csv`, which holds 102 `as_of` vintages from 2023-09-23 to 2026-11-04.
  - Saturday-labelled vintages (to Jul 2025) contain data through `target_end_date = as_of`.
  - Wednesday-labelled vintages (from Jul 2025) contain data through `as_of − 4 days`.
- **Comparators:** `model-output/FluSight-ensemble/` and `model-output/FluSight-baseline/` (90 rounds each, 23 quantiles).

## 2. Vintage rule (leakage control)
For a forecast with reference date R (a Saturday):
1. Select the vintage V = the largest `as_of` ≤ R − 3 days (the Wednesday forecast deadline).
2. Use only rows of V with `target_end_date` ≤ R − 7 days.
3. If V's latest week is earlier than R − 7 (a missing vintage), use it as is: the model then forecasts from older data. Every such round is flagged in `results/tables/vintage_flags.csv`.
4. No other data source enters the US models. In particular, no final-truth data and no comparator forecasts are used as inputs.

This rule reproduces the FluSight setting: at the Wednesday deadline, data through the previous Saturday (R − 7) are available.

## 3. Forecast tasks
- **Horizons** h = 0, 1, 2, 3, meaning target weeks ending R + 7h. Relative to the last observed week (R − 7) these are 1–4 steps ahead. Relative to the Wednesday issue date they are +0.5 to +3.5 weeks. Horizon −1 is not scored.
- **Output:** 23 quantiles {0.01, 0.025, 0.05, 0.10, 0.15, …, 0.90, 0.95, 0.975, 0.99}, on the count scale, non-negative and monotone.

## 4. Seasons and reference dates
- **Tuning season (the only data used for any model choice):** 2023/24, all hub reference dates 2023-10-14 … 2024-05-04 (30 dates). Tuning truth = vintage `as_of` 2024-11-16 (the data that would have been available at the start of the first test season).
- **Test season 1 (2024/25):** hub reference dates 2024-11-23 … 2025-05-31.
- **Test season 2 (2025/26):** hub reference dates 2025-11-22 … 2026-05-30.
- Off-season and 2026/27 rounds are not part of the primary analysis.
- **One frozen configuration** (`models/config.yaml`) is applied to both test seasons. There is no re-tuning between test seasons.

## 5. Truth
- **Primary:** final truth = the latest vintage (`as_of` 2026-11-04) value for each (location, target_end_date).
- **Sensitivity:** first-release truth = the value in the earliest vintage that contains the (location, target_end_date).
- All compared models are scored against the same truth.

## 6. Scoring
- **WIS.** For quantile set Q with median and K = 11 central intervals, WIS(F, y) = (1 / (K + 0.5)) · [0.5·|y − m| + Σ_k (α_k / 2) · IS_{α_k}(F, y)], with IS_α = (u − l) + (2/α)(l − y)·1{y < l} + (2/α)(y − u)·1{y > u}. This equals (2 / |Q|) · Σ_{τ∈Q} PL_τ(q_τ, y) with pinball loss PL_τ(q, y) = (1{y < q} − τ)(q − y), i.e. 2 × the mean pinball loss over the 23 levels. Both forms are implemented and tested to agree.
- **Common-cell rule.** A (reference_date, location, horizon) cell is scored only if ALL models in a comparison have a complete 23-quantile forecast and truth exists. Cell coverage (scored / possible) is reported.
- **Relative WIS (primary metric)** = Σ WIS(NABD-ensemble) / Σ WIS(comparator), the ratio of sums over common cells.
- **Uncertainty.** Block bootstrap over reference dates: resample reference dates with replacement (each draw takes all locations × horizons of that date), B = 2000, numpy seed 20261108. Report the 2.5th and 97.5th percentiles.
- **Interval coverage** of the 50% and 95% central intervals.

## 7. Endpoints
- **PRIMARY:** NABD-ensemble is non-inferior to FluSight-ensemble on US-A. The upper bound of the 95% bootstrap CI of relative WIS (NABD-ensemble / FluSight-ensemble), pooled over both test seasons, all 53 locations and h = 0–3, is < 1.15. The verdict is reported as MET or NOT MET.
- **SECONDARY** (reported regardless of outcome):
  - S1: relative WIS vs FluSight-baseline (persistence) < 1, pooled.
  - S2: 95% interval coverage in [0.90, 0.98]; 50% coverage reported.
  - S3: per-season and per-horizon relative WIS vs both comparators.
  - S4: the primary analysis repeated with first-release truth.
  - S5: each NABD member vs FluSight-ensemble (member contribution); Chronos-2 is reported as NOT RUN where its weights are unavailable.
  - S6: WIS on the log scale, log(y + 1) applied to truth and quantiles, as a scale-robust check.
  - S7: the national location (`US`) reported separately.

## 8. NABD model definitions (the families are fixed here; numeric choices come from the grid in §9)
All models see only the vintage-filtered series y_{l,t} for location l up to t0 = R − 7. They work on z = log(y + 1).

- **Shared point model ("damped pooled log-linear growth"):**
  - local slope g_loc = OLS slope of z over the last w weeks;
  - national slope g_nat = the same for location `US`;
  - seasonal slope g_sea = mean national log-growth at the same epiweek in previous seasons available in the vintage (0 if none);
  - combined g = (1 − λ_n − λ_s)·g_loc + λ_n·g_nat + λ_s·g_sea, clipped to ±g_max;
  - level L = the OLS fitted value at t0 (level = "fit") or the last observation z_{t0} (level = "last");
  - log-forecast at step s = h + 1: ẑ_s = L + g·Σ_{i=1..s} φ^i;
  - point μ_s = exp(ẑ_s) − 1.
- **Member 1, NABD-GLM:** a negative-binomial (NB2) predictive distribution with mean μ_s and dispersion r_l estimated per location by method of moments from the local log-linear fit residuals over the last 8 weeks (floored), with variance inflated by c^s. Quantiles come from the NB distribution (scipy).
- **Member 2, NABD-EEQ (empirical error quantiles):** the same point-model family with its own (w, φ, λ) setting. Quantiles are q_τ = (μ_s + 1)·exp(e_{τ,s}) − 1, where e_{τ,s} is the empirical τ-quantile of rolling-origin log-errors at step s. These are computed within the same vintage from origins in the last H weeks, pooled over locations.
- **Member 3, NABD-Chronos2:** Chronos-2 (amazon/chronos-2) with past covariates when weights are available. Where unavailable (this build environment), it is NOT RUN and excluded from the ensemble. This is recorded in the outputs.
- **NABD-ensemble:** the quantile-wise mean (Vincentisation) of the available members. Then optional multiplicative interval widening about the median by a factor k (k = 1 means none) fitted on 2023/24. Quantiles are sorted and floored at 0.
- **ACI:** online adaptive widening is part of the design. For this frozen v1 run the only calibration is the fixed widening factor k chosen on 2023/24 (decision recorded in config.yaml).

## 9. Tuning (2023/24 only)
- **Grids:**
  - w ∈ {3, 4, 5, 6}
  - φ ∈ {0.6, 0.75, 0.9, 1.0}
  - λ_n ∈ {0, 0.25, 0.5}
  - λ_s ∈ {0, 0.25}
  - level ∈ {fit, last}
  - g_max ∈ {0.5, 1.0}
  - GLM inflation c ∈ {1.0, 1.25, 1.5, 2.0}
  - EEQ history H ∈ {26, 52, 104}
  - ensemble widening k ∈ {0.8, 0.9, 1.0, 1.1, 1.25}
- **Selection criterion:** minimum total WIS over all 2023/24 cells (53 locations × 30 dates × h 0–3) against tuning truth. Members are tuned first (the point-model grid is shared), then k is tuned for the ensemble.
- Selected values are written to `models/config.yaml` with the tuning WIS table, and committed before the test run.

## 10. Execution order
1. Commit this protocol and record docs/FREEZE.md.
2. Tune on 2023/24 and commit models/config.yaml.
3. Run the test seasons ONCE.
4. Score and report every endpoint above, whatever the outcome.
5. If the primary endpoint is NOT MET, no re-tuning on test seasons is allowed. Any post-hoc analysis is labelled EXPLORATORY in docs/DEVIATIONS.md.

## 11. Reproducibility
`python -m eval.run_all --cached`, or `make all`, reruns steps 2–4 from the hub clone with fixed seeds. Outputs go to `results/`, following the BUILD-SPEC interface contract.
