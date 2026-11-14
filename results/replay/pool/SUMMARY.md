# Decision replay of the pooled model on the held-out countries (influenza)

_POST HOC and EXPLORATORY (DEVIATIONS V2, declared before computing). The forecasts are the locked S1 held-out forecasts, unchanged; their accuracy had already been seen. Not a confirmatory result._

Rule (same as DEVIATIONS V1b): each week, for the week about two weeks after issue, roster surge capacity if the forecast gives at least a 30% chance that positivity exceeds the threshold T. A *missed* week is a surge week that was not rostered; a *wasted* week was rostered without a surge; mismatch = missed + wasted.

## Primary threshold: country-relative (75th percentile of the country's own earlier seasons)

36 country-seasons in 18 countries; 488 surge weeks out of 1585 decision weeks.

- vs own-record model (local v1): **10.5 vs 12.3** mismatch weeks a season (difference -1.81; 95% CI -3.00 to -0.72 resampling country-seasons, -2.63 to -0.88 resampling countries; pooled better in 23, tied in 6, worse in 7 of 36).
  Missed surge weeks a season: 2.7 vs 2.2; wasted surge weeks: 7.8 vs 10.1.
- vs last week carried forward: **10.5 vs 11.1** mismatch weeks a season (difference -0.56; 95% CI -1.42 to +0.31 resampling country-seasons, -1.33 to +0.14 resampling countries; pooled better in 19, tied in 5, worse in 12 of 36).
  Missed surge weeks a season: 2.7 vs 2.2; wasted surge weeks: 7.8 vs 8.9.
- vs past-season pattern: **10.5 vs 16.6** mismatch weeks a season (difference -6.11; 95% CI -8.25 to -4.06 resampling country-seasons, -7.91 to -3.37 resampling countries; pooled better in 27, tied in 2, worse in 7 of 36).
  Missed surge weeks a season: 2.7 vs 6.9; wasted surge weeks: 7.8 vs 9.7.

| Rule input | Missed / season | Wasted / season | Mismatch / season | Brier |
|---|---|---|---|---|
| pooled model (NABD-Pool) | 2.7 | 7.8 | 10.5 | 0.133 |
| own-record model (local v1) | 2.2 | 10.1 | 12.3 | 0.154 |
| last week carried forward | 2.2 | 8.9 | 11.1 | 0.141 |
| past-season pattern | 6.9 | 9.7 | 16.6 | 0.228 |
| always-roster | 0.0 | 30.5 | 30.5 | 0.690 |
| never-roster | 13.6 | 0.0 | 13.6 | 0.310 |
| perfect-foresight | 0.0 | 0.0 | 0.0 | 0.000 |

Short-history stratum (≤ 2 own earlier seasons; 14 country-seasons): pooled 12.6 vs local 15.7 mismatch weeks a season (difference -3.14; 95% CI -5.64 to -1.00).

## Secondary threshold: the playbook's 15% (written for UAE levels)

36 country-seasons in 18 countries; 603 surge weeks out of 1585 decision weeks.

- vs own-record model (local v1): **9.8 vs 12.9** mismatch weeks a season (difference -3.11; 95% CI -4.67 to -1.72 resampling country-seasons, -4.89 to -1.60 resampling countries; pooled better in 23, tied in 8, worse in 5 of 36).
  Missed surge weeks a season: 1.5 vs 1.5; wasted surge weeks: 8.3 vs 11.4.
- vs last week carried forward: **9.8 vs 11.2** mismatch weeks a season (difference -1.42; 95% CI -2.53 to -0.42 resampling country-seasons, -2.50 to -0.69 resampling countries; pooled better in 19, tied in 7, worse in 10 of 36).
  Missed surge weeks a season: 1.5 vs 1.7; wasted surge weeks: 8.3 vs 9.5.
- vs past-season pattern: **9.8 vs 14.9** mismatch weeks a season (difference -5.11; 95% CI -7.44 to -3.08 resampling country-seasons, -7.98 to -2.39 resampling countries; pooled better in 27, tied in 5, worse in 4 of 36).
  Missed surge weeks a season: 1.5 vs 5.0; wasted surge weeks: 8.3 vs 9.9.

| Rule input | Missed / season | Wasted / season | Mismatch / season | Brier |
|---|---|---|---|---|
| pooled model (NABD-Pool) | 1.5 | 8.3 | 9.8 | 0.123 |
| own-record model (local v1) | 1.5 | 11.4 | 12.9 | 0.147 |
| last week carried forward | 1.7 | 9.5 | 11.2 | 0.132 |
| past-season pattern | 5.0 | 9.9 | 14.9 | 0.220 |
| always-roster | 0.0 | 27.3 | 27.3 | 0.617 |
| never-roster | 16.8 | 0.0 | 16.8 | 0.383 |
| perfect-foresight | 0.0 | 0.0 | 0.0 | 0.000 |

Short-history stratum (≤ 2 own earlier seasons; 14 country-seasons): pooled 9.4 vs local 14.7 mismatch weeks a season (difference -5.36; 95% CI -7.93 to -2.93).

## Other horizons and trigger probabilities (primary threshold; pooled minus local v1, mismatch weeks a season)

| Target week | p* | Pooled | Local v1 | Difference (95% CI, country-seasons) |
|---|---|---|---|---|
| L+1 | 0.30 | 7.3 | 12.8 | -5.44 (-8.14 to -3.06) |
| L+2 | 0.30 | 8.9 | 13.6 | -4.67 (-7.28 to -2.28) |
| L+3 | 0.30 | 10.5 | 12.3 | -1.81 (-3.00 to -0.72) |
| L+3 | 0.20 | 12.8 | 16.2 | -3.42 (-5.22 to -1.75) |
| L+3 | 0.50 | 8.1 | 10.0 | -1.92 (-2.81 to -1.14) |
| L+4 | 0.30 | 11.4 | 13.2 | -1.75 (-3.00 to -0.58) |

## Every country-season (primary threshold; mismatch weeks)

| Country | Season | Decision weeks | Surge weeks | Pooled | Local v1 | Last week | Past-season pattern |
|---|---|---|---|---|---|---|---|
| BGD | 2025/26 | 45 | 11 | 11 | 13 | 13 | 12 |
| CRI | 2024/25 | 40 | 15 | 12 | 11 | 10 | 20 |
| CRI | 2025/26 | 48 | 5 | 3 | 8 | 8 | 15 |
| ECU | 2024/25 | 48 | 14 | 7 | 14 | 11 | 11 |
| ECU | 2025/26 | 45 | 16 | 13 | 14 | 12 | 12 |
| EGY | 2023/24 | 48 | 28 | 14 | 19 | 11 | 25 |
| EGY | 2024/25 | 48 | 7 | 4 | 4 | 5 | 16 |
| EGY | 2025/26 | 48 | 19 | 7 | 8 | 8 | 7 |
| ETH | 2024/25 | 46 | 19 | 26 | 24 | 27 | 19 |
| GHA | 2024/25 | 42 | 10 | 15 | 29 | 23 | 22 |
| GHA | 2025/26 | 45 | 11 | 12 | 8 | 12 | 11 |
| IDN | 2022/23 | 41 | 9 | 14 | 18 | 17 | 21 |
| IDN | 2023/24 | 45 | 11 | 15 | 17 | 16 | 20 |
| IDN | 2024/25 | 48 | 7 | 6 | 9 | 9 | 20 |
| IDN | 2025/26 | 48 | 11 | 5 | 5 | 5 | 27 |
| IRN | 2025/26 | 33 | 6 | 6 | 7 | 5 | 10 |
| KEN | 2025/26 | 38 | 15 | 21 | 21 | 22 | 19 |
| LKA | 2025/26 | 32 | 15 | 15 | 16 | 14 | 14 |
| MYS | 2022/23 | 48 | 26 | 13 | 18 | 11 | 16 |
| MYS | 2023/24 | 48 | 14 | 18 | 21 | 16 | 27 |
| MYS | 2024/25 | 48 | 22 | 9 | 10 | 11 | 21 |
| MYS | 2025/26 | 48 | 10 | 6 | 6 | 6 | 23 |
| NPL | 2024/25 | 46 | 17 | 9 | 7 | 11 | 13 |
| NPL | 2025/26 | 48 | 4 | 10 | 9 | 12 | 19 |
| PAK | 2024/25 | 37 | 22 | 17 | 15 | 15 | 17 |
| PER | 2025/26 | 48 | 1 | 7 | 11 | 3 | 19 |
| PHL | 2023/24 | 36 | 0 | 8 | 14 | 3 | 15 |
| PHL | 2024/25 | 48 | 17 | 19 | 20 | 24 | 18 |
| PHL | 2025/26 | 37 | 21 | 6 | 6 | 4 | 19 |
| PRY | 2022/23 | 48 | 11 | 12 | 10 | 10 | 22 |
| PRY | 2023/24 | 33 | 9 | 2 | 3 | 3 | 3 |
| PRY | 2024/25 | 48 | 11 | 1 | 1 | 1 | 4 |
| PRY | 2025/26 | 48 | 33 | 5 | 6 | 5 | 22 |
| SEN | 2025/26 | 38 | 17 | 10 | 11 | 11 | 7 |
| VNM | 2024/25 | 42 | 9 | 10 | 19 | 13 | 14 |
| VNM | 2025/26 | 48 | 15 | 10 | 11 | 11 | 18 |

## Limits
- Post hoc: the accuracy of these forecasts was known before this replay was declared.
- Positivity thresholds, not hospital load; a mismatch week is a rule outcome, not a measured cost.
- Finalised FluNet data; no real-time versions exist. RSV not replayed (quantiles not saved by the locked run).
- The declaration was written before computing but committed together with these results (DEVIATIONS V2 note).
