# UAE v2 (multi-signal): results

**RETROSPECTIVE.** Protocol `docs/PROTOCOL-UAE-v2.md` was written, committed and locked (`docs/LOCK-UAE-v2.json`, Merkle root `f745efc2c618c7d6…`) before any v2 score was computed, but v1 results on the same seasons had already been seen. n = 4 test seasons. WIS is in percentage points of positivity; relative WIS < 1 favours the first model.

Signals: sentinel positivity; testing volume (sentinel specimens); non-sentinel positivity (lag +1 wk); school winter/spring breaks (verified calendars); Ramadan (tabular calendar, +/-2 days).

Weather: OMITTED: no reachable source for 2026 (NOAA/Open-Meteo/Meteostat blocked; a third-party ERA5 mirror ends 2025-12-31). Run adapters.weather --fetch locally; weather is not in v2.

## Leave-one-season-out (primary), common cells across v1, v2, persistence, analog

| Series | Comparison | Relative WIS (95% CIs) |
|---|---|---|
| flu | NABD-UAE-v2_vs_NABD-UAE-v1 | 1.049 (date-cluster 1.015–1.084; moving-block 0.996–1.113; n=740) |
| flu | NABD-UAE-v2_vs_persistence | 0.797 (date-cluster 0.737–0.86; moving-block 0.711–0.886; n=740) |
| flu | NABD-UAE-v2_vs_seasonal-analog | 0.737 (date-cluster 0.667–0.819; moving-block 0.621–0.878; n=740) |
| flu | NABD-UAE-v1_vs_persistence | 0.76 (date-cluster 0.701–0.824; moving-block 0.668–0.853; n=740) |
| flu | NABD-UAE-v1_vs_seasonal-analog | 0.703 (date-cluster 0.647–0.77; moving-block 0.604–0.818; n=740) |
| rsv | NABD-UAE-v2_vs_NABD-UAE-v1 | 1.073 (date-cluster 1.032–1.117; moving-block 1.021–1.141; n=740) |
| rsv | NABD-UAE-v2_vs_persistence | 0.84 (date-cluster 0.756–0.936; moving-block 0.72–0.999; n=740) |
| rsv | NABD-UAE-v2_vs_seasonal-analog | 0.742 (date-cluster 0.687–0.805; moving-block 0.656–0.85; n=740) |
| rsv | NABD-UAE-v1_vs_persistence | 0.783 (date-cluster 0.711–0.867; moving-block 0.677–0.91; n=740) |
| rsv | NABD-UAE-v1_vs_seasonal-analog | 0.691 (date-cluster 0.646–0.74; moving-block 0.613–0.775; n=740) |
| pooled | NABD-UAE-v2_vs_NABD-UAE-v1 | 1.059 (date-cluster 1.031–1.087; moving-block 1.016–1.111; n=1480) |
| pooled | NABD-UAE-v2_vs_persistence | 0.815 (date-cluster 0.767–0.867; moving-block 0.739–0.892; n=1480) |
| pooled | NABD-UAE-v1_vs_persistence | 0.769 (date-cluster 0.729–0.814; moving-block 0.704–0.826; n=1480) |

Season wins (lower mean WIS): {"v2_vs_v1": {"flu": "1/4", "rsv": "0/4"}, "v2_vs_persistence": {"flu": "4/4", "rsv": "3/4"}, "v1_vs_persistence": {"flu": "4/4", "rsv": "3/4"}}

## Forward-in-time sensitivity (train only on earlier seasons; test 2023/24–2025/26)

| Series | Comparison | Relative WIS |
|---|---|---|
| flu | NABD-UAE-v2_vs_NABD-UAE-v1 | 1.118 (date-cluster 1.079–1.159; moving-block 1.057–1.199; n=470) |
| flu | NABD-UAE-v2_vs_persistence | 1.12 (date-cluster 1.011–1.247; moving-block 0.947–1.354; n=470) |
| flu | NABD-UAE-v1_vs_persistence | 1.002 (date-cluster 0.896–1.129; moving-block 0.821–1.236; n=470) |
| rsv | NABD-UAE-v2_vs_NABD-UAE-v1 | 1.073 (date-cluster 1.038–1.109; moving-block 1.017–1.14; n=564) |
| rsv | NABD-UAE-v2_vs_persistence | 1.075 (date-cluster 0.946–1.217; moving-block 0.86–1.343; n=564) |
| rsv | NABD-UAE-v1_vs_persistence | 1.002 (date-cluster 0.892–1.129; moving-block 0.809–1.217; n=564) |

| series   |   season |   NABD-UAE-v1 |   NABD-UAE-v2 |   persistence |   seasonal-analog |
|:---------|---------:|--------------:|--------------:|--------------:|------------------:|
| flu      |     2023 |         4.746 |         5.337 |         2.214 |             1.852 |
| flu      |     2024 |         2.544 |         2.547 |         2.659 |             4.504 |
| flu      |     2025 |         1.938 |         2.446 |         3.075 |             2.884 |
| rsv      |     2023 |         2.502 |         2.494 |         2.073 |             1.804 |
| rsv      |     2024 |         1.315 |         1.318 |         2.137 |             1.475 |
| rsv      |     2025 |         2.296 |         2.745 |         1.887 |             3.873 |

## By horizon (LOSO; horizon relative to reference date: -1 nowcast … 2 = +2.5 wk after issue)

| series   |   horizon |   NABD-UAE-v1 |   NABD-UAE-v2 |   persistence |   seasonal-analog |   NABD-UAE-v1/persistence |   NABD-UAE-v2/persistence |
|:---------|----------:|--------------:|--------------:|--------------:|------------------:|--------------------------:|--------------------------:|
| flu      |        -1 |         1.652 |         1.723 |         1.846 |             2.908 |                     0.895 |                     0.934 |
| flu      |         0 |         1.943 |         2.048 |         2.381 |             2.913 |                     0.816 |                     0.86  |
| flu      |         1 |         2.195 |         2.294 |         2.998 |             2.918 |                     0.732 |                     0.765 |
| flu      |         2 |         2.395 |         2.518 |         3.551 |             2.908 |                     0.674 |                     0.709 |
| rsv      |        -1 |         1.292 |         1.244 |         1.369 |             2.201 |                     0.943 |                     0.908 |
| rsv      |         0 |         1.517 |         1.606 |         1.777 |             2.194 |                     0.853 |                     0.903 |
| rsv      |         1 |         1.54  |         1.744 |         2.104 |             2.152 |                     0.732 |                     0.829 |
| rsv      |         2 |         1.643 |         1.837 |         2.401 |             2.118 |                     0.684 |                     0.765 |

## By season (LOSO)

| series   |   season |   NABD-UAE-v1 |   NABD-UAE-v2 |   persistence |   seasonal-analog |
|:---------|---------:|--------------:|--------------:|--------------:|------------------:|
| flu      |     2022 |         2.295 |         2.297 |         2.973 |             2.366 |
| flu      |     2023 |         1.522 |         1.629 |         2.151 |             2.13  |
| flu      |     2024 |         2.431 |         2.338 |         2.621 |             4.764 |
| flu      |     2025 |         1.952 |         2.329 |         3.049 |             2.354 |
| rsv      |     2022 |         1.264 |         1.288 |         1.85  |             1.415 |
| rsv      |     2023 |         1.338 |         1.362 |         1.923 |             1.642 |
| rsv      |     2024 |         1.405 |         1.529 |         2.021 |             2.291 |
| rsv      |     2025 |         1.969 |         2.23  |         1.854 |             3.269 |

## Feed removal and missing-feed behaviour (`results/uae/tables/ablation.csv`)

| feed                                       | series   | metric                |   full |   without |   delta |   n_cells | kind                                                     |
|:-------------------------------------------|:---------|:----------------------|-------:|----------:|--------:|----------:|:---------------------------------------------------------|
| NS                                         | flu      | mean WIS (pct points) | 2.1457 |    2.0571 | -0.0886 |       740 | refit without block (LOSO)                               |
| NS                                         | rsv      | mean WIS (pct points) | 1.6074 |    1.5322 | -0.0753 |       740 | refit without block (LOSO)                               |
| CAL                                        | flu      | mean WIS (pct points) | 2.1457 |    2.0959 | -0.0498 |       740 | refit without block (LOSO)                               |
| CAL                                        | rsv      | mean WIS (pct points) | 1.6074 |    1.5675 | -0.0399 |       740 | refit without block (LOSO)                               |
| TV                                         | flu      | mean WIS (pct points) | 2.1457 |    2.1394 | -0.0063 |       740 | refit without block (LOSO)                               |
| TV                                         | rsv      | mean WIS (pct points) | 1.6074 |    1.6066 | -0.0008 |       740 | refit without block (LOSO)                               |
| CLIM                                       | flu      | mean WIS (pct points) | 2.1457 |    2.7124 |  0.5667 |       740 | refit without block (LOSO)                               |
| CLIM                                       | rsv      | mean WIS (pct points) | 1.6074 |    1.8651 |  0.2577 |       740 | refit without block (LOSO)                               |
| NS (missing at forecast time)              | flu      | mean WIS (pct points) | 2.1457 |    2.0571 | -0.0886 |       740 | feed dropped at prediction; automatic fallback sub-model |
| NS (missing at forecast time)              | rsv      | mean WIS (pct points) | 1.6074 |    1.5322 | -0.0753 |       740 | feed dropped at prediction; automatic fallback sub-model |
| latest sentinel week missing (NABD-UAE-v1) | flu      | mean WIS (pct points) | 1.9496 |    2.1925 |  0.2429 |       540 | stale origin (t-1, horizon+1)                            |
| latest sentinel week missing (NABD-UAE-v1) | rsv      | mean WIS (pct points) | 1.457  |    1.5929 |  0.1359 |       540 | stale origin (t-1, horizon+1)                            |
| latest sentinel week missing (NABD-UAE-v2) | flu      | mean WIS (pct points) | 2.0441 |    2.3062 |  0.2621 |       540 | stale origin (t-1, horizon+1)                            |
| latest sentinel week missing (NABD-UAE-v2) | rsv      | mean WIS (pct points) | 1.5401 |    1.7618 |  0.2217 |       540 | stale origin (t-1, horizon+1)                            |

## Sub-model actually used by v2 (fallback when a feed is missing)

| series   |   season | submodel            |   n |
|:---------|---------:|:--------------------|----:|
| flu      |     2022 | CORE+CLIM+TV+CAL    | 156 |
| flu      |     2022 | CORE+CLIM+TV+NS+CAL |  24 |
| flu      |     2023 | CORE+CLIM+TV+CAL    |  40 |
| flu      |     2023 | CORE+CLIM+TV+NS+CAL | 148 |
| flu      |     2024 | CORE+CLIM+TV+CAL    |   4 |
| flu      |     2024 | CORE+CLIM+TV+NS+CAL | 184 |
| flu      |     2025 | CORE+CLIM+TV+CAL    |   4 |
| flu      |     2025 | CORE+CLIM+TV+NS+CAL | 184 |
| rsv      |     2022 | CORE+CLIM+TV+CAL    | 160 |
| rsv      |     2022 | CORE+CLIM+TV+NS+CAL |  20 |
| rsv      |     2023 | CORE+CLIM+TV+CAL    |  44 |
| rsv      |     2023 | CORE+CLIM+TV+NS+CAL | 144 |
| rsv      |     2024 | CORE+CLIM+TV+CAL    |   4 |
| rsv      |     2024 | CORE+CLIM+TV+NS+CAL | 184 |
| rsv      |     2025 | CORE+CLIM+TV+CAL    |   4 |
| rsv      |     2025 | CORE+CLIM+TV+NS+CAL | 184 |

## Surge-onset alerts (pre-declared rule; descriptive, n = 4 seasons per series)

| model                         | series   |   n_eligible |   n_onsets | sensitivity   | ppv   |   false_alarms |   premature |   late_or_missed |   median_lead_wk |
|:------------------------------|:---------|-------------:|-----------:|:--------------|:------|---------------:|------------:|-----------------:|-----------------:|
| NABD-UAE-v1                   | flu      |            3 |          3 | 3/3           | 3/3   |              0 |           0 |                0 |             1.43 |
| NABD-UAE-v1                   | rsv      |            3 |          3 | 1/3           | 1/2   |              0 |           0 |                2 |            -2.57 |
| NABD-UAE-v2                   | flu      |            3 |          3 | 2/3           | 2/2   |              0 |           0 |                1 |             2.43 |
| NABD-UAE-v2                   | rsv      |            3 |          3 | 1/3           | 1/3   |              0 |           0 |                2 |            -0.57 |
| NABD-UAE-v2 (NS feed dropped) | flu      |            3 |          3 | 3/3           | 3/3   |              0 |           0 |                0 |             1.43 |
| NABD-UAE-v2 (NS feed dropped) | rsv      |            3 |          3 | 1/3           | 1/2   |              0 |           0 |                2 |            -2.57 |
| census rule (persistence)     | flu      |            3 |          3 | 2/3           | 2/3   |              0 |           0 |                1 |             1.43 |
| census rule (persistence)     | rsv      |            3 |          3 | 1/3           | 1/3   |              0 |           1 |                1 |             0.43 |

Thresholds T (flu 15%, RSV 10%) and the 0.6·T census fraction were set from earlier exploratory work that saw these seasons (disclosed in DEVIATIONS); alert metrics are diagnostic only.

## Caveats

- n=4 test seasons; descriptive
- LOSO trains on later seasons; forward-in-time sensitivity reported
- non-sentinel stream starts 2023-W15, so 2022/23 and early 2023/24 use the fallback sub-model
- revisions to FluNet values are not reproduced (no vintages)
