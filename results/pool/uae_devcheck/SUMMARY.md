# UAE development check: the pooled model on the UAE's own seasons (POST HOC, NON-CONFIRMATORY)

_Declared in `docs/DEVIATIONS.md` S7. Restates numbers already in `results/pool/SUMMARY.md` ("already-seen countries") with a per-season split, a per-horizon split and a confidence interval. Nothing is refitted._

**How these forecasts were made.** Forward in time: to forecast UAE season S, the pooled model was fitted only on other countries (the UAE's fold left out) and only on seasons before S. The UAE contributes only its own past weeks and earlier seasons as inputs at each forecast date, the same information the UAE's own-record model gets.

**Why it is not confirmatory.** UAE data were part of the development set used to choose the pooled model's configuration (one of 45 development countries), and the author had seen UAE data before. The confirmatory UAE test is prospective and locked (`docs/PREREG-LIVE.md`); its result is due after 15 April 2027.

Influenza, UAE sentinel series, seasons 2024/25, 2025/26, 100 forecast weeks x 4 horizons = 388 forecasts. Relative WIS below 1 means less error than the comparator. 95% CI: moving-block bootstrap over forecast weeks within season (blocks of 4, B = 2000, seed 0).

## Headline

- Pooled model vs last week carried forward: **0.772 (95% CI 0.698–0.861)**, i.e. about 23% less error.
- Pooled model vs the UAE's own-record model (v1): 0.868 (95% CI 0.752–0.996).
- For reference, own-record model vs last week on the same forecasts: 0.890 (95% CI 0.716–1.126).

## By season (relative WIS vs last week carried forward)

| Season | Pooled | Own-record v1 | Past-season pattern | Pooled / v1 |
|---|---|---|---|---|
| 2024/25 | 0.841 | 1.180 | 1.815 | 0.712 |
| 2025/26 | 0.713 | 0.639 | 0.941 | 1.116 |

Reading: the pooled model had less error than last week in both seasons. The own-record model swung from worse than last week to better than it, and beat the pooled model in the second season.

## By horizon (data weeks ahead; relative WIS vs last week)

| Horizon | Pooled | Own-record v1 | Past-season pattern |
|---|---|---|---|
| 1 | 0.901 | 1.081 | 1.901 |
| 2 | 0.837 | 0.946 | 1.493 |
| 3 | 0.743 | 0.838 | 1.231 |
| 4 | 0.679 | 0.788 | 1.035 |

## Interval coverage (target 0.50 / 0.95)

| Model | 50% | 95% |
|---|---|---|
| Pooled model (NABD-Pool) | 0.57 | 0.99 |
| UAE own-record model (v1) | 0.47 | 0.94 |
| Last week carried forward | 0.49 | 0.95 |
| Past-season pattern | 0.29 | 0.55 |

## Limits

- Two seasons, one country; a week-block bootstrap cannot capture season-to-season variation.
- Finalised (revised) FluNet data; positivity, not hospital load.
- These cells differ from `results/uae/SUMMARY-v2.md` (the v1 parity result, 1.002): that analysis also scores 2023/24, when the UAE had one earlier season and v1 lost heavily; the pool harness needs two own earlier seasons, so 2023/24 is not scored here.
- Never a headline without the words "development check, not a confirmatory test".
