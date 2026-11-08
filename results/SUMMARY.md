# NABD US-A results (pre-registered; PROTOCOL v1.0)

**PRIMARY:** NABD-ensemble vs CDC FluSight-ensemble: relative WIS **1.223** (95% CI 1.011–1.521), margin 1.15: **non-inferiority NOT MET**. 11660 cells, 55 reference dates, 2024/25 + 2025/26, 53 locations, h0–3, final truth.

**S1:** vs FluSight-baseline (persistence): relative WIS **0.816** (95% CI 0.655–1.023).

**S2:** NABD 50% coverage 0.480, 95% coverage 0.918 (FluSight-ensemble 0.522 / 0.861).

Chronos-2: NOT RUN in the build environment (weights blocked); excluded from the ensemble.

## All endpoints

| Analysis | A | B | cells | rel. WIS | 95% CI | cov50 A | cov95 A |
|---|---|---|---|---|---|---|---|
| PRIMARY pooled (final truth) | NABD-ensemble | FluSight-ensemble | 11660 | 1.223 | 1.011–1.521 | 0.48 | 0.92 |
| S1 pooled vs baseline | NABD-ensemble | FluSight-baseline | 11660 | 0.816 | 0.655–1.023 | 0.48 | 0.92 |
| ref: FluSight-ensemble vs baseline | FluSight-ensemble | FluSight-baseline | 11660 | 0.667 | 0.580–0.754 | 0.52 | 0.86 |
| S3 season 2024/25 | NABD-ensemble | FluSight-ensemble | 5724 | 1.026 | 0.885–1.255 | 0.52 | 0.93 |
| S3 season 2024/25 vs baseline | NABD-ensemble | FluSight-baseline | 5724 | 0.690 | 0.566–0.807 | 0.52 | 0.93 |
| S3 season 2025/26 | NABD-ensemble | FluSight-ensemble | 5936 | 1.516 | 1.093–2.026 | 0.44 | 0.91 |
| S3 season 2025/26 vs baseline | NABD-ensemble | FluSight-baseline | 5936 | 0.998 | 0.668–1.485 | 0.44 | 0.91 |
| S3 horizon 0 | NABD-ensemble | FluSight-ensemble | 2915 | 1.074 | 0.921–1.268 | 0.48 | 0.92 |
| S3 horizon 0 vs baseline | NABD-ensemble | FluSight-baseline | 2915 | 0.769 | 0.656–0.919 | 0.48 | 0.92 |
| S3 horizon 1 | NABD-ensemble | FluSight-ensemble | 2915 | 1.228 | 1.009–1.513 | 0.47 | 0.91 |
| S3 horizon 1 vs baseline | NABD-ensemble | FluSight-baseline | 2915 | 0.823 | 0.647–1.065 | 0.47 | 0.91 |
| S3 horizon 2 | NABD-ensemble | FluSight-ensemble | 2915 | 1.264 | 1.007–1.622 | 0.48 | 0.92 |
| S3 horizon 2 vs baseline | NABD-ensemble | FluSight-baseline | 2915 | 0.830 | 0.645–1.081 | 0.48 | 0.92 |
| S3 horizon 3 | NABD-ensemble | FluSight-ensemble | 2915 | 1.246 | 0.991–1.630 | 0.48 | 0.92 |
| S3 horizon 3 vs baseline | NABD-ensemble | FluSight-baseline | 2915 | 0.816 | 0.623–1.085 | 0.48 | 0.92 |
| S4 first-release truth | NABD-ensemble | FluSight-ensemble | 11660 | 1.295 | 1.055–1.590 | 0.51 | 0.93 |
| S5 member NABD-GLM | NABD-GLM | FluSight-ensemble | 11660 | 1.315 | 1.063–1.680 | 0.47 | 0.86 |
| S5 member NABD-EEQ | NABD-EEQ | FluSight-ensemble | 11660 | 1.198 | 1.006–1.440 | 0.42 | 0.90 |
| S6 log-scale WIS | NABD-ensemble | FluSight-ensemble | 11660 | 1.225 | 1.147–1.321 | 0.48 | 0.92 |
| S6 log-scale WIS vs baseline | NABD-ensemble | FluSight-baseline | 11660 | 0.762 | 0.702–0.831 | 0.48 | 0.92 |
| S7 national (US) | NABD-ensemble | FluSight-ensemble | 220 | 1.254 | 1.011–1.598 | 0.43 | 0.92 |

## All models on common cells

| Model | cells | mean WIS | rel. vs FS-ensemble | rel. vs FS-baseline | cov50 | cov95 |
|---|---|---|---|---|---|---|
| NABD-ensemble | 11660 | 177.8 | 1.223 | 0.816 | 0.48 | 0.92 |
| NABD-GLM | 11660 | 191.2 | 1.315 | 0.877 | 0.47 | 0.86 |
| NABD-EEQ | 11660 | 174.1 | 1.198 | 0.799 | 0.42 | 0.90 |
| FluSight-ensemble | 11660 | 145.4 | 1.000 | 0.667 | 0.52 | 0.86 |
| FluSight-baseline | 11660 | 218.0 | 1.500 | 1.000 | 0.38 | 0.79 |

Figures: results/figures/rel_wis_by_horizon.png, coverage.png, fan_chart_CA_TX_h1.png.
Relative WIS here = ratio of sums (CI: block bootstrap over reference dates, B=2000, seed 20261108). The overview table uses ratio of means on all-model common cells, so it can differ slightly from pairwise rows.
