# GCC out-of-sample test of the frozen UAE method (G12)

**Pre-registered** in `docs/PREREG-GCC.md` and locked (`docs/LOCK-GCC.json`) **before any GCC data were downloaded**. The lock is self-attested in local git; outside anchoring is still to be done by the user. Design: **forward-in-time**: at the start of each season the model is refitted on that country's own earlier seasons only, with no UAE data and no pooling across countries. Data: WHO FluNet (finalised values, no vintages), so the results are **retrospective, revised data**. Data source deviation G1: WHO's full export via a public mirror, verified against the official API.

## PRIMARY (influenza, NABD-UAE-v1 method vs persistence, pooled): **MET**

Relative WIS **0.914 (95% CI 0.843–0.983; 12 country-seasons, 2214 cells)**. Pre-registered criterion: < 1 with 95% upper bound < 1.

## Secondary

| Comparison | Relative WIS |
|---|---|
| flu_NABD-UAE-v1_vs_seasonal-analog | 0.536 (95% CI 0.464–0.616; 12 country-seasons, 2214 cells) |
| flu_NABD-UAE-v2-GCC_vs_persistence | 0.92 (95% CI 0.85–0.987; 12 country-seasons, 2214 cells) |
| flu_NABD-UAE-v2-GCC_vs_NABD-UAE-v1 | 1.006 (95% CI 0.995–1.021; 12 country-seasons, 2214 cells) |
| rsv_NABD-UAE-v1_vs_persistence | 0.798 (95% CI 0.719–0.894; 10 country-seasons, 1795 cells) |
| rsv_NABD-UAE-v1_vs_seasonal-analog | 0.685 (95% CI 0.605–0.781; 10 country-seasons, 1795 cells) |
| rsv_NABD-UAE-v2-GCC_vs_persistence | 0.796 (95% CI 0.714–0.895; 10 country-seasons, 1795 cells) |
| rsv_NABD-UAE-v2-GCC_vs_NABD-UAE-v1 | 0.998 (95% CI 0.992–1.003; 10 country-seasons, 1795 cells) |

Country-seasons where v1 beat persistence: {'flu': '9/12', 'rsv': '9/10'}.

## Every country (losses included)

| series   | country   |   NABD-UAE-v1 |   NABD-UAE-v2-GCC |   persistence |   seasonal-analog |   v1/persistence |   v1/analog |
|:---------|:----------|--------------:|------------------:|--------------:|------------------:|-----------------:|------------:|
| flu      | OMN       |         3.972 |             3.965 |         4.291 |             6.924 |            0.926 |       0.574 |
| flu      | QAT       |         2.211 |             2.274 |         2.368 |             4.959 |            0.934 |       0.446 |
| flu      | SAU       |         2.033 |             2.026 |         2.327 |             3.424 |            0.874 |       0.594 |
| rsv      | OMN       |         1.168 |             1.171 |         1.47  |             1.629 |            0.794 |       0.717 |
| rsv      | QAT       |         1.303 |             1.296 |         1.784 |             1.95  |            0.731 |       0.668 |
| rsv      | SAU       |         1.116 |             1.112 |         1.026 |             1.688 |            1.088 |       0.662 |

### Per country-season

| series   | country   |   season |   NABD-UAE-v1 |   NABD-UAE-v2-GCC |   persistence |   seasonal-analog | v1_beats_persistence   |
|:---------|:----------|---------:|--------------:|------------------:|--------------:|------------------:|:-----------------------|
| flu      | OMN       |     2022 |          3.75 |              3.74 |          3.49 |              9.1  | False                  |
| flu      | OMN       |     2023 |          2.61 |              2.62 |          3.23 |              3.8  | True                   |
| flu      | OMN       |     2024 |          5.64 |              5.61 |          5.45 |              9.41 | False                  |
| flu      | OMN       |     2025 |          3.67 |              3.67 |          4.87 |              4.81 | True                   |
| flu      | QAT       |     2022 |          3.06 |              3.27 |          3.31 |              5.24 | True                   |
| flu      | QAT       |     2023 |          1.92 |              1.92 |          1.92 |              4.93 | False                  |
| flu      | QAT       |     2024 |          1.94 |              1.96 |          1.97 |              4.27 | True                   |
| flu      | QAT       |     2025 |          1.92 |              1.94 |          2.27 |              5.39 | True                   |
| flu      | SAU       |     2022 |          1.99 |              1.97 |          2.31 |              2.29 | True                   |
| flu      | SAU       |     2023 |          2.06 |              2.07 |          2.22 |              3.21 | True                   |
| flu      | SAU       |     2024 |          2.08 |              2.02 |          2.13 |              4.21 | True                   |
| flu      | SAU       |     2025 |          2    |              2.05 |          2.64 |              3.99 | True                   |
| rsv      | OMN       |     2022 |          1.27 |              1.27 |          1.53 |              1.92 | True                   |
| rsv      | OMN       |     2023 |          1.26 |              1.26 |          1.52 |              1.73 | True                   |
| rsv      | OMN       |     2024 |          1.18 |              1.19 |          1.53 |              1.23 | True                   |
| rsv      | OMN       |     2025 |          0.96 |              0.95 |          1.3  |              1.64 | True                   |
| rsv      | QAT       |     2022 |          1.46 |              1.44 |          1.88 |              1.87 | True                   |
| rsv      | QAT       |     2023 |          1.09 |              1.07 |          1.85 |              1.3  | True                   |
| rsv      | QAT       |     2024 |          1.33 |              1.33 |          1.84 |              1.84 | True                   |
| rsv      | QAT       |     2025 |          1.33 |              1.34 |          1.57 |              2.78 | True                   |
| rsv      | SAU       |     2024 |          0.75 |              0.73 |          0.86 |              0.85 | True                   |
| rsv      | SAU       |     2025 |          1.47 |              1.48 |          1.19 |              2.49 | False                  |

## Inclusion (pre-registered rule applied mechanically)

| country   | series   | origin   | scored_seasons           |
|:----------|:---------|:---------|:-------------------------|
| OMN       | flu      | TOTAL    | [2022, 2023, 2024, 2025] |
| OMN       | rsv      | TOTAL    | [2022, 2023, 2024, 2025] |
| QAT       | flu      | TOTAL    | [2022, 2023, 2024, 2025] |
| QAT       | rsv      | TOTAL    | [2022, 2023, 2024, 2025] |
| BHR       | flu      | SENTINEL | [2024]                   |
| BHR       | rsv      | SENTINEL | []                       |
| KWT       | flu      | TOTAL    | [2025]                   |
| KWT       | rsv      | TOTAL    | []                       |
| SAU       | flu      | SENTINEL | [2022, 2023, 2024, 2025] |
| SAU       | rsv      | SENTINEL | [2024, 2025]             |

Included for the primary analysis (≥ 2 scored flu seasons): **OMN, QAT, SAU**. Bahrain (1 scored flu season) and Kuwait (1) were excluded by the rule; their results are not used. OMN and QAT report a single undifferentiated stream (TOTAL), so the non-sentinel block of v2-GCC is never active and v2-GCC ≈ v1.

## How to read it

- The method designed on UAE data, frozen, and then run blind on three other Gulf countries' surveillance beat 'next week = this week' by about 9% for influenza and 20% for RSV, and beat the seasonal-average baseline by much more. Losses: flu in Oman 2022/23 and 2024/25, flu in Qatar 2023/24 (a tie), and RSV in Saudi Arabia 2025/26.
- This is the project's first blind, pre-registered test the method passed. It is still retrospective on revised data, n = 3 countries, and n ≈ 4 seasons each.
- Coverage, flu: 95% intervals cover 0.96 (v1). RSV: 0.83, so RSV intervals are too narrow outside the UAE.
