# Decision replay: what a roster rule would have done with the frozen forecasts

**POST HOC and EXPLORATORY (DEVIATIONS V1, declared and committed before computing, commit f4c6195).** The forecasts are the frozen Gulf forward-in-time forecasts of G12, regenerated with full quantiles and checked equal to the locked scores (12,027 cells, differences below 1e-14). Their accuracy had already been seen. This is a scenario about decisions, not a confirmatory result and not a measured saving.

**Rule (fixed in advance).** Each week, for the target week two weeks after issue: roster surge capacity if the forecast gives at least a 30% chance (the playbook's `p_act`) that positivity passes the playbook tier (flu 15%, RSV 10%). A *missed* week is a surge week with no roster; a *wasted* week is a roster with no surge. The same rule is applied to every forecaster.

## Headline (Gulf: Oman, Qatar, Saudi Arabia; playbook thresholds; p* = 0.30; +2 weeks after issue)

| Pathogen | Country-seasons | Forecaster | Missed | Wasted | Mismatch weeks | Per season |
|---|---|---|---|---|---|---|
| Influenza | 12 | NABD | 19 | 77 | 96 | 8.0 |
| Influenza | 12 | Past-season pattern | 25 | 224 | 249 | 20.8 |
| Influenza | 12 | Last week (persistence) | 19 | 77 | 96 | 8.0 |
| Influenza | 12 | never-roster | 184 | 0 | 184 | 15.3 |
| Influenza | 12 | always-roster | 0 | 369 | 369 | 30.8 |
| RSV | 10 | NABD | 16 | 40 | 56 | 5.6 |
| RSV | 10 | Past-season pattern | 11 | 60 | 71 | 7.1 |
| RSV | 10 | Last week (persistence) | 13 | 61 | 74 | 7.4 |
| RSV | 10 | never-roster | 71 | 0 | 71 | 7.1 |
| RSV | 10 | always-roster | 0 | 377 | 377 | 37.7 |

- **Influenza, NABD vs past-season pattern:** 8.0 vs 20.8 mismatch weeks a season; difference -12.75 (95% CI -16.7 to -9.3); NABD better in 12, tied in 0, worse in 0 of 12 country-seasons. Almost all of the gain is fewer wasted surge weeks.
- **Influenza, NABD vs last week:** 8.0 vs 8.0 mismatch weeks a season; difference +0.00 (95% CI -1.2 to +1.2); NABD better in 6, tied in 1, worse in 5 of 12 country-seasons. **No advantage over simply carrying last week forward** under this rule.
- **RSV, NABD vs past-season pattern:** 5.6 vs 7.1 mismatch weeks a season; difference -1.50 (95% CI -3.0 to +0.1); NABD better in 6, tied in 2, worse in 2 of 10 country-seasons. The interval includes zero, and **NABD missed more RSV surge weeks than the pattern did** (16 vs 11); it wasted fewer (40 vs 60).
- **RSV, NABD vs last week:** 5.6 vs 7.4 mismatch weeks a season; difference -1.80 (95% CI -2.9 to -0.7); NABD better in 8, tied in 1, worse in 1 of 10 country-seasons.

## Where NABD loses or ties (playbook thresholds, +2 weeks)

- Not better than past-season pattern: OMN 2023/24 RSV (10 vs 8); OMN 2024/25 RSV (10 vs 7); SAU 2024/25 RSV (0 vs 0); SAU 2025/26 RSV (5 vs 5).
- Not better than last week: OMN 2022/23 flu (9 vs 7); OMN 2024/25 flu (10 vs 9); QAT 2022/23 flu (10 vs 10); QAT 2024/25 flu (15 vs 12); SAU 2022/23 flu (14 vs 13); SAU 2024/25 flu (8 vs 4); OMN 2023/24 RSV (10 vs 8); SAU 2024/25 RSV (0 vs 0).
- Saudi Arabia RSV 2024/25 had no week above 10%, so every forecaster scored zero mismatches there.

## Sensitivity (declared; never the headline)

| Setting | Flu: NABD minus pattern (95% CI) | Flu: NABD minus last week | RSV: NABD minus pattern | RSV: NABD minus last week |
|---|---|---|---|---|
| Headline | -12.75 (-16.7 to -9.3) | +0.00 (-1.2 to +1.2) | -1.50 (-3.0 to +0.1) | -1.80 (-2.9 to -0.7) |
| p* = 0.20 | -16.25 (-20.1 to -12.8) | +0.00 (-1.4 to +1.2) | -3.10 (-4.5 to -1.6) | -1.80 (-3.3 to -0.4) |
| p* = 0.50 | -6.33 (-9.5 to -3.1) | -1.92 (-3.1 to -1.0) | -0.80 (-2.9 to +0.9) | -1.10 (-2.4 to +0.0) |
| Country-relative threshold (own 75th percentile) | -5.42 (-7.8 to -3.4) | -0.17 (-2.1 to +1.8) | -2.90 (-5.2 to -0.9) | -1.90 (-3.3 to -0.6) |
| Nowcast week | -15.67 (-19.1 to -12.6) | -0.50 (-1.6 to +0.5) | -2.90 (-4.8 to -0.9) | +0.00 (-0.6 to +0.7) |
| +1 week | -14.00 (-17.7 to -10.7) | +0.17 (-0.5 to +0.8) | -1.60 (-3.0 to -0.1) | -0.50 (-1.6 to +0.6) |
| +3 weeks | -10.75 (-14.7 to -7.2) | +0.75 (-1.1 to +2.4) | -1.00 (-2.8 to +0.8) | -2.70 (-3.6 to -1.7) |

## UAE folds (POST HOC, n = 2 seasons, descriptive only)

- Influenza: mismatch weeks over two seasons: NABD 20, past-season pattern 25, last week 24 (NABD missed 10, last week missed 3).
- RSV: mismatch weeks over two seasons: NABD 17, past-season pattern 21, last week 13 (NABD missed 11, last week missed 1).
- On the UAE's two folds NABD **missed far more surge weeks than last week did** and wasted fewer. Two seasons cannot support a claim either way.

## AED scenario for a Tawam-sized paediatric unit (RSV only; SCENARIO, not a saving)

AED a season = mismatch weeks avoided (NABD vs past-season pattern, RSV) x mis-planned bed-days per mismatch week x AED 2,057 per bed-day.

| Case | Weeks avoided a season | Mis-planned bed-days per mismatch week | Bed-days a season | AED a season |
|---|---|---|---|---|
| low | -0.1 | 48.8 | -5 | -10,000 |
| central | +1.5 | 137.1 | 206 | 423,000 |
| high | +3.0 | 482.9 | 1,449 | 2,979,000 |

**Read this as a range from about zero to about AED 3 million, central about AED 0.4 million.** The low case is slightly negative because the interval for weeks avoided includes zero.

Assumptions, all visible:
- RSV bed-days a year 1,160 / 1,970 / 3,822 (Tawam study 2,189 admissions over five years; length of stay 4.0 / 4.5 / 5.8 days).
- Share of bed-days in surge weeks 0.7 / 0.8 / 0.9 (ASSUMPTION).
- Surge weeks a season 14 / 10.75 / 7: UAE sentinel weeks with RSV above 10% in 2022/23–2025/26 ({'2022': 7, '2023': 9, '2024': 14, '2025': 13}).
- AED 2,057 a bed-day = US$560 (Dubai claims median US$2,241 over about 4 days) x 3.6725.
- Gulf-country mismatch rates transfer to an Abu Dhabi hospital (ASSUMPTION).
- Positivity tiers map to bed pressure; one mismatch week mis-plans one week of the surge increment (ASSUMPTION).
- The bed-day figure is the scale of resource mis-planned. **It is not cash saved.**
- No influenza AED figure: there is no sourced paediatric flu bed-day cost.

## Files

- `forecasts/*.csv.gz`: the frozen forecasts with all 23 quantiles (contract format).
- `truth.csv`, `thresholds_country_q75.csv`.
- `tables/weekly_decisions.csv.gz`: every weekly decision. `tables/per_season_*.csv`: per country-season.
- Reproduce: `python3 -m replay.regen && python3 -m replay.run && python3 -m replay.report`. Another model: `python3 -m replay.run --extra its_forecasts.csv` (contract format).
