# Borrowed strength: NABD-Pool on held-out countries (confirmatory)

_Held-out countries, forward-in-time, revised FluNet data; plan locked before download (lock #1), model locked before any held-out row was extracted (lock #2)._

Plan: `docs/PREREG-POOL.md`. Lock #1 (plan and country lists) was made before any new data were downloaded; lock #2 (model, configuration, development data) was made before any held-out row was extracted. Both locks are self-attested in local git until externally timestamped. Scored once.

## Primary (influenza): **MET**
- Pooled model vs each country's own-record model (local v1), relative WIS: **0.767 (95% CI 0.681–0.832; 18/18 countries better)**. Below 1 means the pooled model had less error.
- Held-out countries listed: 36; included by the pre-set data rules: **18** (BGD, CRI, ECU, EGY, ETH, GHA, IDN, IRN, KEN, LKA, MYS, NPL, PAK, PER, PHL, PRY, SEN, VNM).
- Chosen model (development countries only): `ENS(G_relaxed+L_relaxed_k8)`.

## Key secondaries
1. Short-history stratum (country-seasons with ≤ 2 own earlier seasons): 0.624 (95% CI 0.540–0.705; 14/14 countries better).
2. Simulated short record (every country cut to its last 2 seasons): 0.640 (95% CI 0.592–0.692; 18/18 countries better).
3. Pooled vs persistence: 0.879 (95% CI 0.850–0.901; 18/18 countries better). Pooled vs past-season pattern: 0.571 (95% CI 0.518–0.624; 18/18 countries better).
   For reference, local v1 vs persistence on the same cells: 1.145 (95% CI 1.055–1.283; 4/18 countries better).

## Other secondaries
- EMRO only: 0.640 (95% CI 0.565–0.822; 3/3 countries better). Other regions: 0.785 (95% CI 0.702–0.847; 15/15 countries better).
- Geometric mean of per-country ratios: 0.721. Country-seasons where pooled beat local: 35/36.
- By horizon (1–4 data weeks), pooled vs local: {'1': 0.6486, '2': 0.6986, '3': 0.8492, '4': 0.8771}.
- Coverage (50% / 95% intervals): NABD-Pool: 0.54 / 0.96; NABD-UAE-v1: 0.65 / 0.96; persistence: 0.55 / 0.95; seasonal-analog: 0.37 / 0.65.
- RSV (secondary; 13 countries: AFG, BGD, CRI, ECU, GEO, IDN, KAZ, MYS, NPL, PAK, PER, PHL, PRY): pooled vs local 0.789 (95% CI 0.705–0.860; 12/13 countries better); vs persistence 0.845 (95% CI 0.811–0.888; 11/13 countries better).

## Every included country (influenza, mean WIS in percentage points)

| Country | Pooled | Local v1 | Persistence | Past-season pattern | Pooled / local | Pooled / persistence |
|---|---|---|---|---|---|---|
| PER | 1.73 | 4.25 | 1.74 | 2.93 | 0.41 | 1.00 |
| BGD | 3.15 | 6.67 | 3.76 | 8.27 | 0.47 | 0.84 |
| EGY | 1.98 | 3.51 | 2.18 | 3.92 | 0.56 | 0.91 |
| SEN | 4.30 | 6.51 | 4.84 | 6.78 | 0.66 | 0.89 |
| GHA | 2.96 | 4.25 | 3.31 | 4.37 | 0.70 | 0.90 |
| ETH | 2.98 | 4.28 | 3.47 | 3.76 | 0.70 | 0.86 |
| KEN | 3.37 | 4.76 | 3.61 | 5.31 | 0.71 | 0.94 |
| PAK | 3.35 | 4.54 | 3.97 | 5.60 | 0.74 | 0.84 |
| CRI | 2.39 | 3.20 | 2.84 | 6.09 | 0.75 | 0.84 |
| ECU | 3.15 | 4.17 | 3.79 | 4.56 | 0.76 | 0.83 |
| MYS | 2.01 | 2.54 | 2.32 | 4.54 | 0.79 | 0.87 |
| PHL | 2.97 | 3.71 | 3.11 | 5.37 | 0.80 | 0.96 |
| LKA | 5.63 | 6.96 | 7.20 | 7.80 | 0.81 | 0.78 |
| IRN | 2.94 | 3.57 | 3.41 | 4.13 | 0.82 | 0.86 |
| VNM | 6.14 | 7.20 | 6.66 | 9.52 | 0.85 | 0.92 |
| NPL | 2.48 | 2.81 | 3.38 | 4.31 | 0.88 | 0.73 |
| PRY | 2.50 | 2.77 | 2.78 | 4.86 | 0.90 | 0.90 |
| IDN | 4.75 | 5.05 | 5.30 | 7.49 | 0.94 | 0.90 |

## Excluded held-out countries (pre-set rules, applied mechanically)

- AFG: no qualifying evaluation season
- DJI: no rows in the export (ISO_YEAR >= 2015)
- IRQ: no qualifying evaluation season
- JOR: no qualifying evaluation season
- LBN: fewer than 2 qualifying earlier seasons
- LBY: no qualifying evaluation season
- MAR: no qualifying evaluation season
- PSE: no qualifying evaluation season
- SOM: fewer than 2 qualifying earlier seasons
- SDN: no qualifying evaluation season
- SYR: no qualifying evaluation season
- TUN: no qualifying evaluation season
- YEM: no qualifying evaluation season
- ISR: no qualifying evaluation season
- GEO: no qualifying evaluation season
- ARM: no qualifying evaluation season
- KAZ: no qualifying evaluation season
- UZB: no qualifying evaluation season

## Already-seen countries (NON-CONFIRMATORY)
These countries were in the development set and their data had been seen before this test. Figures come from development cross-fitting, with the country left out of the pooled fit. They are not evidence for H1.

- ARE: pooled / local v1 = 0.87; pooled / persistence = 0.77
- OMN: pooled / local v1 = 0.95; pooled / persistence = 0.87
- QAT: pooled / local v1 = 0.94; pooled / persistence = 0.87
- SAU: pooled / local v1 = 0.94; pooled / persistence = 0.82

## Limits
- Finalised (revised) FluNet data; no real-time versions exist.
- Positivity, not hospital load. The season boundary (ISO week 27) is a northern-hemisphere convention applied to all countries.
- Deviation P1 (relaxed rule for the pooled model's training rows) was declared before any pooled fit; see `docs/DEVIATIONS.md`.
