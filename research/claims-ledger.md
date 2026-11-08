# Claims ledger (G9 instrument)

Every factual claim used in `pitch/` (registration, deck, demo, Q&A, assumptions) → its source → its status. If a claim isn't in this table, it can't go on a slide.

**Status key:**
- **R** = computed in this repo (file).
- **V** = VERIFIED external source (URL in `research/`).
- **S** = secondary source.
- **P** = pending (in build; the slot must be cut if it isn't produced).
- **X** = banned.

| # | Claim (as worded in pitch) | Used in | Source | Status |
|---|---|---|---|---|
| 1 | US primary: NABD v1 vs CDC FluSight ensemble rel. WIS 1.22 (95% CI 1.01–1.52), margin 1.15, NOT MET | deck 7, Q&A 1, limitations | `results/summary.json` → primary; `results/SUMMARY.md` | R |
| 2 | 2024/25: 1.03 (0.89–1.25); 2025/26: 1.52 (1.09–2.03) | deck 7, Q&A 2 | `results/SUMMARY.md` S3 rows | R |
| 3 | vs FluSight baseline 0.82 (0.66–1.02); 2024/25 0.69 (0.57–0.81); 2025/26 1.00 | deck 7, Q&A 4 | `results/SUMMARY.md` S1/S3 | R |
| 4 | CDC ensemble vs baseline 0.67 on the same cells | deck 7, Q&A 4 | `results/SUMMARY.md` "ref" row | R |
| 5 | 11,660 forecasts; 53 locations; 55 reference dates | deck 7 | `results/summary.json` | R |
| 6 | Coverage: 95% 0.92 vs ensemble 0.86; 50% 0.48 vs 0.52 | Q&A 13 | `results/summary.json` → S2 | R |
| 7 | Protocol frozen 8 Nov 06:47 UTC, commit ac16901, SHA-256 2846533f… | deck 7, Q&A 6 | `docs/FREEZE.md` | R (self-attested until anchored) |
| 8 | The national series is ~46% of NABD's WIS; worse than the ensemble in 52/52 state-level locations pooled, 0/52 better in 2025/26 | Q&A 3, limitations | `docs/REVIEW-R2-audit.md` item 6; to be reproduced in `results/tables/` (D6) | R (audit); P (repo table) |
| 9 | Overshoot after the peak (TX, CA, Feb 2025) | deck 7, Q&A 2 | `results/figures/fan_chart_CA_TX_h1.png`; judges' review | R (descriptive, post hoc) |
| 10 | UAE vs persistence: flu 0.76 (0.70–0.82), RSV 0.78 (0.71–0.87); 7 of 8 season-series (flu 4/4, RSV 3/4) | registration, deck 6, Q&A | `results/uae/SUMMARY.md` | R (retrospective, design-stage) |
| 11 | UAE vs seasonal analog: flu 0.70, RSV 0.69 | deck 6 | `results/uae/SUMMARY.md` | R |
| 12 | RSV lost to persistence in 2025/26 (1.97 vs 1.84 mean WIS) | deck 6, Q&A 7, limitations | `results/uae/SUMMARY.md` season table | R |
| 13 | UAE RSV peak ISO weeks 42, 41, 41, 47 (2022–2025) | registration, deck 2, demo | `data/raw/flunet_are.csv` (recomputed 8 Nov: 20.4/24.5/29.8/23.1%) | R |
| 14 | Median onset lead 0 weeks for every rule | deck 8, Q&A 9, limitations | `results/tables/alerts_us.csv` | R (diagnostic, D5) |
| 15 | PPV at T=3: NABD 0.65/0.76, CDC ens 0.41/0.67, census 0.60/0.46 (2024/25 / 2025/26) | deck 8, Q&A 10 | `results/tables/alerts_us.csv` | R (diagnostic: thresholds informed by pre-freeze probes, D5) |
| 16 | 2024/25 sensitivity: census 0.55 vs NABD 0.33 | Q&A 10 | `results/tables/alerts_us.csv` | R |
| 17 | One missing week ×1.41 error; two weeks ×1.82 | deck 5/8, Q&A 11, limitations | `results/tables/dropout_us.csv` | R |
| 18 | US input age at issue: median 4 days | deck 5 | `results/tables/latency_us.csv` | R |
| 19 | UAE lag 7 days for W44 on 8 Nov | Q&A 15, limitations | `data/raw/PROVENANCE.md` | R |
| 20 | Leakage test caught and fixed a real LOSO boundary leak | Q&A 12 | `results/uae/SUMMARY.md` integrity note; commit 463ab09 | R |
| 21 | Tawam: 2,189 RSV admissions of children aged ≤5, 2018–22; positivity 2.9% → 16% | registration, deck 2, demo | `research/burden.md` #1 (J Infect Public Health 2025) | V |
| 22 | Dubai: 22% of under-2s with RSV hospitalised; <2% had known risk factors | deck 2 | `research/burden.md` #3 | V (abstract) |
| 23 | The UAE publishes no flu case counts | registration, deck 2 | `research/burden.md` #6 (The National, Jan 2026) | V |
| 24 | "The UAE publishes no respiratory forecasts" / "has no forecasting hub" | registration, deck 1 | `research/competitors.md` ("No public calibrated RSV + flu forecast found for the UAE or GCC") | V (as an absence-of-evidence statement; say "no public") |
| 25 | DoH: this season similar to the previous two | Q&A curveball, deck 2 notes | `research/burden.md` #8 (Khaleej Times, Sep 2026) | V |
| 26 | ADPHC 2024 tender = outbreak detection, dashboard, travel; awardee unknown | deck 3, Q&A 16 | `research/competitors.md` | V (scope); awardee unknown |
| 27 | Rasid = wastewater monitoring (ADQCC + G42 Healthcare) | deck 3, Q&A 16 | `research/competitors.md` | V |
| 28 | GE CareIntellect forecasts up to 72 hours from inside-hospital data | Q&A 17 | `research/competitors.md` | V |
| 29 | CDC FluSight ensemble pools "about 40" models | deck 7 | judges' review; SPEC | S: say "dozens of teams" if it is not re-verified |
| 30 | Abu Dhabi infant RSV immunisation window 1 Sep–1 Mar | (context only, not on slides) | `research/burden.md` #7 | S |
| 31 | No conflict-of-interest clause in the T&C | Q&A curveball | `research/tc.md` | V |
| 32 | Multi-signal UAE v2 with per-signal explanations | registration (in build), deck 4/5 | ⟦results/uae/explain/, results/uae/tables/ablation.csv⟧ | P |
| 33 | UAE alert metrics | registration (in build), deck 5, Q&A 10 | ⟦results/uae/ alert table⟧ | P |
| 34 | Gulf out-of-sample result | registration (in build), deck 6, Q&A 20 | ⟦results/gcc/⟧ | P |
| 35 | Outside-anchored ledger | registration (in build), deck 8 | ⟦ledger/ANCHOR.md + the team's anchor⟧ | P |
| 36 | League-table rank among hub models | deck 7 | ⟦results/tables/league* (D7)⟧ | P |
| 37 | "NABD performs better during surges" (E1) | — | `docs/DEVIATIONS.md` E1 | X |
| 38 | "CDC ensemble cut error 21–36%" as NABD's gain | — | audit item 13 | X (only ever as the ensemble's, and not needed) |
| 39 | ED, NSSP or weather as v1 inputs; Chronos-2 or ACI as active | — | `models/config.yaml`, audit item 1 | X |
| 40 | "Pre-registered" applied to the UAE v1 numbers | — | audit item 9 | X |
| 41 | Any Abu Dhabi hospital or operational result | — | none exists | X |
