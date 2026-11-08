# UAE track: leave-one-season-out results (PRELIMINARY)

Data: WHO FluNet UAE sentinel, latest week **2026-W44** (`data/raw/flunet_are.csv`). Design: leave-one-season-out over **n = 4 test seasons** (2022/23–2025/26), 1-week simulated publication lag, horizons relative to reference date: -1 = nowcast, 0 = +0.5 wk, 1 = +1.5 wk, 2 = +2.5 wk after issue.

**Honest caveats:** n = 4 seasons; 2022/23 is low-volume; LOSO trains on later seasons when testing earlier ones; bootstrap CIs resample reference dates and do not capture between-season uncertainty; FluNet revisions are not reproduced.

## Relative WIS (NABD-UAE-v1 / baseline; < 1 means NABD better), 95% block-bootstrap CI

| Comparison | All 4 seasons | Excluding 2022/23 |
|---|---|---|
| flu_vs_persistence | 0.76 [0.703, 0.825] (n dates=190) | 0.76 [0.694, 0.834] |
| flu_vs_seasonal-analog | 0.702 [0.647, 0.766] (n dates=190) | 0.638 [0.586, 0.698] |
| rsv_vs_persistence | 0.789 [0.721, 0.864] (n dates=190) | 0.816 [0.729, 0.914] |
| rsv_vs_seasonal-analog | 0.699 [0.656, 0.751] (n dates=190) | 0.661 [0.613, 0.715] |

## Seasons (of 4) in which NABD-UAE-v1 had lower mean WIS

- flu: vs persistence 4/4, vs seasonal analog 4/4
- rsv: vs persistence 3/4, vs seasonal analog 4/4

## Mean WIS and coverage by model

| series   | model           |   mean_wis |   n |   cov50 |   cov95 |
|:---------|:----------------|-----------:|----:|--------:|--------:|
| flu      | NABD-UAE-v1     |      2.04  | 756 |   0.554 |   0.964 |
| flu      | persistence     |      2.676 | 760 |   0.525 |   0.939 |
| flu      | seasonal-analog |      2.897 | 764 |   0.45  |   0.763 |
| rsv      | NABD-UAE-v1     |      1.508 | 756 |   0.519 |   0.958 |
| rsv      | persistence     |      1.905 | 760 |   0.499 |   0.961 |
| rsv      | seasonal-analog |      2.14  | 764 |   0.38  |   0.717 |

## Mean WIS by season

| series   |   season |   NABD-UAE-v1 |   persistence |   seasonal-analog |
|:---------|---------:|--------------:|--------------:|------------------:|
| flu      |     2022 |         2.312 |         3.001 |             2.379 |
| flu      |     2023 |         1.518 |         2.117 |             2.166 |
| flu      |     2024 |         2.427 |         2.593 |             4.707 |
| flu      |     2025 |         1.92  |         3.007 |             2.327 |
| rsv      |     2022 |         1.274 |         1.802 |             1.364 |
| rsv      |     2023 |         1.36  |         1.958 |             1.644 |
| rsv      |     2024 |         1.428 |         2.011 |             2.306 |
| rsv      |     2025 |         1.957 |         1.844 |             3.23  |

## RSV peak-week absolute error (weeks), origins 1–4 weeks before the observed peak

| model           |    1 |    2 |    3 |    4 |
|:----------------|-----:|-----:|-----:|-----:|
| NABD-UAE-v1     | 1.25 | 1.25 | 1.5  | 1.25 |
| persistence     | 0    | 2.25 | 3.75 | 5.25 |
| seasonal-analog | 1    | 1.5  | 2    | 2.5  |

Peak-week metric is descriptive only (4 seasons × 4 origins).
