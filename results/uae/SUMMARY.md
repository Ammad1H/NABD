# UAE track: leave-one-season-out results (PRELIMINARY)

Data: WHO FluNet UAE sentinel, latest week **2026-W44** (`data/raw/flunet_are.csv`). Design: leave-one-season-out over **n = 4 test seasons** (2022/23–2025/26), 1-week simulated publication lag, horizons relative to reference date: -1 = nowcast, 0 = +0.5 wk, 1 = +1.5 wk, 2 = +2.5 wk after issue.

**Honest caveats:** n = 4 seasons; 2022/23 is low-volume; LOSO trains on later seasons when testing earlier ones; bootstrap CIs resample reference dates and do not capture between-season uncertainty; FluNet revisions are not reproduced.

## Relative WIS (NABD-UAE-v1 / baseline; < 1 means NABD better), 95% block-bootstrap CI

| Comparison | All 4 seasons | Excluding 2022/23 |
|---|---|---|
| flu_vs_persistence | 0.76 [0.701, 0.824] (n dates=186) | 0.755 [0.689, 0.832] |
| flu_vs_seasonal-analog | 0.703 [0.647, 0.77] (n dates=186) | 0.639 [0.589, 0.701] |
| rsv_vs_persistence | 0.783 [0.711, 0.867] (n dates=186) | 0.813 [0.727, 0.913] |
| rsv_vs_seasonal-analog | 0.691 [0.646, 0.74] (n dates=186) | 0.654 [0.608, 0.708] |

## Seasons (of 4) in which NABD-UAE-v1 had lower mean WIS

- flu: vs persistence 4/4, vs seasonal analog 4/4
- rsv: vs persistence 3/4, vs seasonal analog 4/4

## Mean WIS and coverage by model

| series   | model           |   mean_wis |   n |   cov50 |   cov95 |
|:---------|:----------------|-----------:|----:|--------:|--------:|
| flu      | NABD-UAE-v1     |      2.046 | 740 |   0.555 |   0.965 |
| flu      | persistence     |      2.694 | 740 |   0.524 |   0.939 |
| flu      | seasonal-analog |      2.912 | 740 |   0.451 |   0.764 |
| rsv      | NABD-UAE-v1     |      1.498 | 740 |   0.516 |   0.953 |
| rsv      | persistence     |      1.913 | 740 |   0.503 |   0.962 |
| rsv      | seasonal-analog |      2.166 | 740 |   0.378 |   0.716 |

## Mean WIS by season

| series   |   season |   NABD-UAE-v1 |   persistence |   seasonal-analog |
|:---------|---------:|--------------:|--------------:|------------------:|
| flu      |     2022 |         2.295 |         2.973 |             2.366 |
| flu      |     2023 |         1.522 |         2.151 |             2.13  |
| flu      |     2024 |         2.431 |         2.621 |             4.764 |
| flu      |     2025 |         1.952 |         3.049 |             2.354 |
| rsv      |     2022 |         1.264 |         1.85  |             1.415 |
| rsv      |     2023 |         1.338 |         1.923 |             1.642 |
| rsv      |     2024 |         1.405 |         2.021 |             2.291 |
| rsv      |     2025 |         1.969 |         1.854 |             3.269 |

## RSV peak-week absolute error (weeks), origins 1–4 weeks before the observed peak

| model           |    1 |    2 |    3 |    4 |
|:----------------|-----:|-----:|-----:|-----:|
| NABD-UAE-v1     | 1.25 | 1.25 | 1.75 | 1.25 |
| persistence     | 0    | 2.25 | 3.75 | 5.25 |
| seasonal-analog | 1    | 1.5  | 2    | 2.5  |

Peak-week metric is descriptive only (4 seasons × 4 origins).

## Integrity note

These v1 numbers are **retrospective, design-stage, not pre-registered**: NABD-UAE-v1 was designed with all four seasons visible and re-run after a leak fix (463ab09; docs/DEVIATIONS.md U1). All tables use cells common to all three models (U4). The blind tests of the UAE method are the GCC out-of-sample test (results/gcc/SUMMARY.md) and the prospective ledger. v2 results: results/uae/SUMMARY-v2.md.

`tests/test_adapters.py::test_forecast_unchanged_when_future_data_altered` caught a leave-one-season-out boundary leak in the first build (lag features of a training season's first week reached into the held-out season); it was fixed by masking cross-season lags in `uae/models.py::_features`, changing relative WIS by <= 0.01. A companion test confirms the detector fires when a leak is injected.
