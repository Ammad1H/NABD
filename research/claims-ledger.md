# Claims ledger (G9 instrument), round 3

Every factual claim used in `pitch/` (registration, deck, demo, video, one-pager, Q&A, assumptions) or `docs/TECHNICAL.md` → its source → its status. **If a claim isn't in this table, it can't go on a slide.**

**Status key:**
- **R**: computed in this repo (file).
- **V**: VERIFIED external source (URL in `research/positioning-sources.md` or `research/burden.md`).
- **S**: secondary source.
- **P**: pending (in build; cut the line if it isn't produced).
- **X**: banned.
- **RET**: retired (true in its file, but no longer allowed as headline evidence).

Evidence order (BUILD-SPEC v1.6): **(1)** blind Gulf test → **(2)** public ledger → **(3)** US CDC benchmark and league → **(4)** UAE record at parity.

## A. Gulf out-of-sample test (G12): headline evidence

| # | Claim (as worded in pitch) | Used in | Source | Status |
|---|---|---|---|---|
| A1 | Plan (countries, inclusion rule, pass bar) locked before any OMN/QAT/BHR/KWT/SAU data were downloaded | registration, deck 5, demo, video, one-pager, Q&A 1/4 | `docs/PREREG-GCC.md`; `docs/LOCK-GCC.json`; commits 91005ce (lock, 12:08:47Z) → d013228 (data, 12:10:18Z) | R (self-attested in local git until anchored) |
| A2 | Influenza: frozen v1 method vs persistence 0.914 (95% CI 0.843–0.983), pre-set bar met | all | `results/gcc/SUMMARY.md` PRIMARY | R |
| A3 | "about 9% (flu) and 20% (RSV) less error than next-week-equals-this-week" | registration, deck 5, demo, video, one-pager | 1 − 0.914 = 8.6%; 1 − 0.798 = 20.2% (`results/gcc/SUMMARY.md`) | R |
| A4 | RSV 0.798 (0.719–0.894) | all | `results/gcc/SUMMARY.md` secondary | R |
| A5 | vs seasonal analog: flu 0.536, RSV 0.685 | deck 5, Q&A 1 | `results/gcc/SUMMARY.md` | R |
| A6 | Won 9/12 flu and 9/10 RSV country-seasons; losses OMN flu 2022/23 and 2024/25, QAT flu 2023/24 (tie), SAU RSV 2025/26 | deck 5, demo, Q&A 2, limitations | `results/gcc/SUMMARY.md` per-country-season table | R |
| A7 | Bahrain and Kuwait excluded by the pre-set rule (1 scorable flu season each) | deck 5, Q&A 3 | `results/gcc/SUMMARY.md` inclusion table; `docs/PREREG-GCC.md` §3 | R |
| A8 | RSV 95% coverage 0.83 (too narrow); flu 0.96 | deck 5, Q&A 21, limitations | `results/gcc/SUMMARY.md` "How to read it" | R |
| A9 | Forward-in-time, each country's own earlier seasons only, no UAE data | deck 5, Q&A 1 | `docs/PREREG-GCC.md` §4 | R |
| A10 | Retrospective on revised data; data via a public mirror of WHO's full export, verified against the official API | deck 5, limitations, Q&A 4/5 | `results/gcc/SUMMARY.md`; `docs/DEVIATIONS.md` (G1) | R |
| A11 | v1 chosen as primary after UAE v2 and forward-in-time results were known (disclosed) | Q&A 4, limitations | `docs/PREREG-GCC.md` §1 | R |

## B. Public ledger

| # | Claim | Used in | Source | Status |
|---|---|---|---|---|
| B1 | Every round is hashed before WHO publishes the target week; R0 issued 8 Nov 06:51 UTC, R1 8 Nov 12:12 UTC (v1, v2, persistence), Merkle manifest | deck 6, demo, video, one-pager | `ledger/`, `ledger/rounds/2026-11-08T1212Z_R1` | R |
| B2 | Scored rounds as of 8 Nov: 0 | deck 6, demo | `ledger/SCOREBOARD.md` | R (refresh on the day) |
| B3 | Outside-anchored timestamp | deck 6, registration (in build) | `ledger/ANCHOR.md` + the team's receipt | P |

## C. US benchmark (CDC FluSight hub)

| # | Claim | Used in | Source | Status |
|---|---|---|---|---|
| C1 | NABD v1 vs CDC FluSight ensemble rel. WIS 1.22 (95% CI 1.01–1.52), margin 1.15, NOT MET | deck 7, demo, video, Q&A 10, limitations, one-pager | `results/SUMMARY.md` PRIMARY | R |
| C2 | 2024/25 1.03 (0.89–1.25); 2025/26 1.52 (1.09–2.03) | deck 7, Q&A 12 | `results/SUMMARY.md` S3 | R |
| C3 | vs FluSight baseline 0.82 (0.66–1.02); CDC ensemble vs baseline 0.67 | Q&A 14, limitations | `results/SUMMARY.md` S1, ref row | R |
| C4 | 11,660 forecasts, 53 locations, 2 seasons, horizons 0–3, 55 reference dates | deck 7 | `results/SUMMARY.md` | R |
| C5 | Protocol frozen 8 Nov 06:47 UTC before any test score, commit ac16901, SHA-256 2846533f… | deck 7, Q&A 16 | `docs/FREEZE.md` | R (self-attested; no anchor before results) |
| C6 | League, single models: 7th of 21 in 2024/25 (0.693; CDC ensemble 0.673); 19th of 25 in 2025/26 (0.997, level with the baseline) | registration (implicitly via "report shortfalls"), deck 7, demo, video, Q&A 11, limitations, one-pager | `results/tables/league_table.csv`; `results/SUMMARY.md` D7; method declared before computing (D7, D11) | R |
| C7 | Including ensembles: 13th of 41 (2024/25), 40th of 46 (2025/26) | Q&A 11 | same | R |
| C8 | Per-location wins vs ensemble: 18/53 (2024/25), 0/53 (2025/26) | Q&A 12, limitations | `results/SUMMARY.md` D6; `results/tables/per_location_wins.csv` | R |
| C9 | Excluding the national series: 1.198 (CI 1.014–1.449), still NOT MET; national share 46.0% (NABD), 44.9% (ensemble) | deck 7, Q&A 13, limitations | `results/SUMMARY.md` D6; `results/tables/excl_national.csv`, `national_share.csv` | R |
| C10 | Block bootstrap (L=4) primary CI 0.979–1.573; verdict unchanged | TECHNICAL | `results/tables/sensitivity_block_bootstrap.csv` | R |
| C11 | By as-of phase vs ensemble: rising 1.27, flat 0.97, falling 1.29; under-prediction the largest WIS component | Q&A 12, TECHNICAL | `results/SUMMARY.md` D10; `results/tables/phase_decomposition.csv` | R (descriptive) |
| C12 | Relative economic value: NABD above the CDC ensemble at cost/loss ≤ 0.1, about equal at 0.2, below at ≥ 0.3 | TECHNICAL, Q&A (optional) | `results/SUMMARY.md` REV table; `results/tables/rev_curves.csv` | R (descriptive, no CIs) |
| C13 | Coverage: 95% 0.92 vs ensemble 0.86; 50% 0.48 vs 0.52 | Q&A 21 | `results/SUMMARY.md` S2 | R |
| C14 | Scorer cross-check: our WIS equals an independent implementation exactly on all cells | Q&A 20, limitations, TECHNICAL | `results/tables/scorer_crosscheck.csv`; DEVIATIONS D9 | R |
| C15 | Median onset lead 0 weeks for every rule, including the CDC's | deck 8, Q&A 17, limitations | `results/tables/alerts_us.csv` | R (diagnostic, D5) |
| C16 | US PPV at 3/100k: NABD 0.65/0.76; CDC ensemble 0.41/0.67; census 0.60/0.46 (2024/25 / 2025/26) | deck 8, Q&A 18 | `results/tables/alerts_us.csv` | R (diagnostic: thresholds informed by pre-freeze probes) |
| C17 | 2024/25 timely sensitivity at 3/100k: census 0.55 vs NABD 0.33 | Q&A (caveat) | `results/tables/alerts_us.csv` | R |
| C18 | One missing week ×1.41 error; two weeks ×1.82 | deck 8, Q&A 19, limitations | `results/tables/dropout_us.csv` | R |
| C19 | US median input age at issue: 4 days | deck 9 | `results/tables/latency_us.csv` | R |
| C20 | The CDC FluSight hub accepts non-US teams (a Canadian team, UGuelph, submits); a PR is due Wednesdays 11 PM ET | Q&A (optional) | `docs/FLUSIGHT-PARTICIPATION.md` | R/V (nothing submitted) |

## D. UAE's own record

| # | Claim | Used in | Source | Status |
|---|---|---|---|---|
| D1 | Forward-in-time, v1 vs persistence: 1.002 (flu), 1.002 (RSV), i.e. parity | registration (a300), deck 8, demo, video, Q&A 6, limitations | `results/uae/SUMMARY-v2.md` forward-in-time table | R |
| D2 | Multi-signal v2 worse than v1: pooled 1.059 (moving-block CI 1.016–1.111); locked protocol, retrospective | deck 8, Q&A 7, limitations, TECHNICAL | `results/uae/SUMMARY-v2.md`; `docs/PROTOCOL-UAE-v2.md`; `docs/LOCK-UAE-v2.json` | R |
| D3 | Feed removal: dropping non-sentinel or calendar inputs did not hurt (small improvement); testing volume ≈ no effect; removing climatology hurt most | deck 8, Q&A 7, limitations | `results/uae/tables/ablation.csv` | R |
| D4 | UAE flu alerts: v1 caught 3/3 onsets, PPV 3/3, 0 false alarms (census rule 2/3); RSV ≈ 1/3 for every rule | deck 8, Q&A 18, limitations | `results/uae/tables/alerts_uae.csv` | R (diagnostic; n = 3 onsets) |
| D5 | Missing latest week raises UAE mean WIS by 0.14–0.26 percentage points; a missing non-sentinel week triggers an automatic fallback sub-model | Q&A 19, limitations | `results/uae/tables/ablation.csv` | R |
| D6 | Exact per-signal contributions per forecast (linear model) | deck 4/9, demo, video, TECHNICAL | `results/uae/explain/`; tests (contributions sum to the predictor) | R |
| D7 | UAE lag 7 days for W44 on 8 Nov | Q&A 23, limitations, deck 9 | `data/raw/PROVENANCE.md` | R |
| D8 | The leakage test caught and fixed a real LOSO boundary leak in the first build | Q&A 20 | `results/uae/SUMMARY.md` integrity note; commit 463ab09 | R |
| D9 | LOSO vs persistence flu 0.76, RSV 0.78; "7 of 8 season-series" | — | `results/uae/SUMMARY.md` | **RET** (trains on later seasons; may appear only as a footnote next to D1) |

## E. Problem and context

| # | Claim | Used in | Source | Status |
|---|---|---|---|---|
| E1 | Season-shape table: flu peak 35.6% wk45 / 27.3% wk45 / 28.0% wk7 (Feb) / 40.6% wk42; RSV peak 20.4% wk42 / 24.5% wk41 / 29.8% wk41 / 23.1% wk47; first RSV ≥10% wk 35 / 38 / 30 / 42 (2022/23–2025/26) | registration, deck 2, demo, video, one-pager | `research/positioning.md` §1.1 ([DATA], `data/raw/flunet_are.csv`, weeks with ≥20 specimens) | R |
| E2 | 2024/25 flu: 11 weeks ≥20%, Nov→Mar plateau; "flu peaked anywhere from October to February" | registration, deck 2, video | same | R |
| E3 | "RSV peak has moved across six weeks" (wk 41 → 47) | registration | same | R |
| E4 | Tawam: 2,189 RSV admissions of children ≤5, 2018–22; positivity 2.9% → 16%; infants <6 months mean stay 5.8 days | registration, deck 2, demo, video, one-pager | `research/positioning.md` §1.2 [S1]; `research/burden.md` #1 | V |
| E5 | Dubai: 22% of under-2s with RSV hospitalised; <2% had a known risk factor; median cost US$2,241 | deck 2, one-pager | [S3]; `research/burden.md` #3 | V (abstract) |
| E6 | Tawam paediatric flu 2012–17: 33.5% admitted, 8% PICU | video (optional) | [S2]; `research/burden.md` | V (older data; say so) |
| E7 | UAE flu case data not publicly available (The National, Jan 2026) | registration, deck 2, one-pager | [S6] | V |
| E8 | No public calibrated RSV/flu forecast found for the UAE or GCC ("to our knowledge") | registration, deck 1/3, one-pager | `research/positioning.md` §1.7; `research/competitors.md` | V (absence of evidence; always say "to our knowledge" or "no public") |
| E9 | Tableegh: Malaffi-linked near-real-time notifications | deck 3, demo, Q&A 24 | [S12] | V |
| E10 | UMOC: AI early warning predicting potential outbreaks | deck 3, Q&A 24 | [S13] | V |
| E11 | Rasid: wastewater monitoring (ADQCC + G42 Healthcare) | deck 3, Q&A 24 | [S20] | V |
| E12 | ADPHC 2024 tender scope: outbreak detection, dashboard, travel; awardee unknown | Q&A 24 | `research/competitors.md` | V (scope) |
| E13 | GE CareIntellect-class tools: up to 72 h from inside-hospital data | Q&A 25 | `research/competitors.md` | V |
| E14 | DoH: this season's activity similar to the previous two | deck 2 notes, Q&A curveball | [S7]; `research/burden.md` #8 | V |
| E15 | ADPHC vaccinated 350,000+ in 2025/26 | optional | [S5] | V |
| E16 | Abu Dhabi infant RSV immunisation window 1 Sep–1 Mar; RSV ≥10% before 1 Sep in 2 of 4 seasons | Q&A curveball only (context) | [S4] secondary; [DATA] | S / R |
| E17 | No conflict-of-interest clause in the T&C | Q&A curveball | `research/tc.md` | V |
| E18 | Future Health 2026 theme "To Sense is to Predict"; reactive → proactive | video, deck 10 | [S25] | V |

## F. Banned (X)

| # | Claim | Why |
|---|---|---|
| F1 | "NABD performs better during surges" (E1 exploratory) | Defined using realised truth; DEVIATIONS E1 |
| F2 | The CDC ensemble's 21–36% gain presented as NABD's | Not ours |
| F3 | ED, NSSP, weather or wastewater as inputs; Chronos-2 or ACI as active | Not built/run (`models/config.yaml`, `results/uae/SUMMARY-v2.md`) |
| F4 | "Pre-registered" applied to the UAE v1 numbers | Design-stage |
| F5 | Any Abu Dhabi hospital or operational result; SEHA bed or ED numbers | None exists |
| F6 | v2 "improves" on v1 | 1.059 (worse) |
| F7 | "Early warning of onset" / "earlier than" | Median lead 0 weeks |
| F8 | "RSV is climbing" / crisis framing | W44 10.5%; DoH "similar to previous two" |
| F9 | Workforce-absence figures | None credible; module SIMULATED |
| F10 | "Predicts the nirsevimab window" | Context only |
| F11 | "The only" without "to our knowledge"; the CDC ensemble "pools about 40 models" | Unverified count. Use the league counts (41 / 46 ranked models) instead |
| F12 | "Blind" without the caveats (self-attested lock; v1 chosen after UAE results) | `docs/PREREG-GCC.md` §1 |
