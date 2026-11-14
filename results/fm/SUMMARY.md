# Zero-shot foundation-model benchmark on the held-out countries (influenza)

_POST HOC and EXPLORATORY (DEVIATIONS W1, declared before computing). The S1 forecasts are unchanged and their accuracy was already known. Not a confirmatory result and not a UAE result._

Model: `amazon/chronos-2` (revision `29ec3766d36d`), zero-shot, univariate, no fine-tuning. Each forecast sees only the country's own series up to the forecast origin. Same cells, same score (WIS) and same country-clustered bootstrap as S1: 6,410 forecasts in 18 countries. Check: the stored S1 forecasts rescore to Pool vs local = 0.767.

Relative WIS below 1 means the first model had less error.

| Comparison | Relative WIS | Short-history stratum |
|---|---|---|
| Chronos-2 zero-shot vs NABD-Pool | 1.026 (95% CI 0.993–1.055; 5/18 countries better) | 1.011 (95% CI 0.929–1.075; 6/14 countries better) |
| Chronos-2 zero-shot vs own-record model (local v1) | 0.787 (95% CI 0.689–0.861; 18/18 countries better) | 0.630 (95% CI 0.507–0.753; 14/14 countries better) |
| Chronos-2 zero-shot vs last week carried forward | 0.901 (95% CI 0.864–0.932; 18/18 countries better) | 0.887 (95% CI 0.824–0.937; 13/14 countries better) |
| Pool+FM (equal-weight average of NABD-Pool and Chronos-2) vs NABD-Pool | 0.985 (95% CI 0.963–1.002; 10/18 countries better) | 0.973 (95% CI 0.923–1.011; 7/14 countries better) |
| Pool+FM (equal-weight average of NABD-Pool and Chronos-2) vs own-record model (local v1) | 0.755 (95% CI 0.662–0.827; 18/18 countries better) | 0.606 (95% CI 0.500–0.710; 14/14 countries better) |
| Pool+FM (equal-weight average of NABD-Pool and Chronos-2) vs last week carried forward | 0.865 (95% CI 0.832–0.891; 18/18 countries better) | 0.853 (95% CI 0.803–0.897; 13/14 countries better) |
| Chronos-2 zero-shot, percent input (sensitivity) vs NABD-Pool | 1.024 (95% CI 0.989–1.060; 6/18 countries better) | 1.014 (95% CI 0.926–1.088; 6/14 countries better) |
| Chronos-2 zero-shot, percent input (sensitivity) vs own-record model (local v1) | 0.786 (95% CI 0.686–0.860; 18/18 countries better) | 0.632 (95% CI 0.507–0.760; 14/14 countries better) |
| Chronos-2 zero-shot, percent input (sensitivity) vs last week carried forward | 0.900 (95% CI 0.864–0.929; 18/18 countries better) | 0.889 (95% CI 0.823–0.938; 13/14 countries better) |

| Model | Mean WIS (pp) | 50% coverage | 95% coverage |
|---|---|---|---|
| NABD-Pool | 3.117 | 0.54 | 0.96 |
| Chronos-2 (zero-shot) | 3.196 | 0.49 | 0.95 |
| Pool+FM | 3.069 | 0.52 | 0.96 |
| Chronos-2 (zero-shot, percent input) | 3.193 | 0.48 | 0.96 |
| NABD-UAE-v1 | 4.063 | 0.65 | 0.96 |
| persistence | 3.547 | 0.55 | 0.95 |
| seasonal-analog | 5.458 | 0.37 | 0.65 |

By horizon (1–4 data weeks), relative WIS vs NABD-Pool: Chronos-2 0.991, 1.011, 1.032, 1.057; Pool+FM 0.973, 0.981, 0.986, 0.995.

## Every country (mean WIS; ratio below 1 = better than NABD-Pool)

| Country | NABD-Pool | Chronos-2 | Pool+FM | Chronos-2 / Pool | Pool+FM / Pool |
|---|---|---|---|---|---|
| BGD | 3.15 | 2.36 | 2.51 | 0.75 | 0.80 |
| PER | 1.73 | 1.46 | 1.57 | 0.84 | 0.91 |
| MYS | 2.01 | 1.87 | 1.86 | 0.93 | 0.93 |
| EGY | 1.98 | 2.06 | 1.88 | 1.04 | 0.95 |
| ETH | 2.98 | 2.97 | 2.85 | 1.00 | 0.95 |
| PHL | 2.97 | 2.91 | 2.89 | 0.98 | 0.97 |
| GHA | 2.96 | 2.99 | 2.91 | 1.01 | 0.98 |
| PRY | 2.50 | 2.62 | 2.48 | 1.04 | 0.99 |
| IDN | 4.75 | 4.80 | 4.70 | 1.01 | 0.99 |
| KEN | 3.37 | 3.46 | 3.35 | 1.03 | 0.99 |
| IRN | 2.94 | 3.01 | 2.94 | 1.02 | 1.00 |
| ECU | 3.15 | 3.32 | 3.16 | 1.05 | 1.00 |
| SEN | 4.30 | 4.62 | 4.32 | 1.08 | 1.01 |
| CRI | 2.39 | 2.65 | 2.41 | 1.11 | 1.01 |
| VNM | 6.14 | 6.59 | 6.28 | 1.07 | 1.02 |
| NPL | 2.48 | 2.75 | 2.55 | 1.11 | 1.03 |
| PAK | 3.35 | 3.83 | 3.51 | 1.14 | 1.05 |
| LKA | 5.63 | 6.48 | 5.92 | 1.15 | 1.05 |

## Limits
- Post hoc: declared after the S1 scores were known; the equal-weight ensemble is a hypothesis for a new locked test, not a finding.
- The foundation model's pretraining data may include public epidemiological series; we cannot rule out overlap.
- Finalised FluNet data; positivity, not hospital load.
