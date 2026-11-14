# Claims ledger (G9 instrument), round 4

Every factual claim used in `pitch/` (registration, deck, demo, video, one-pager, Q&A, outreach, assumptions) or `docs/TECHNICAL.md` → its source → its status. **If a claim isn't in this table, it can't go on a slide.**

**Status key:**
- **R**: computed in this repo (file).
- **V**: VERIFIED external source (URL in `research/positioning-sources.md` or `research/burden.md`).
- **S**: secondary source.
- **P**: pending (in build; cut the line if it isn't produced).
- **X**: banned.
- **RET**: retired (true in its file, but no longer allowed as evidence).
- **H**: a hypothesis, labelled as such where used.

**Order (BUILD-SPEC v1.7):**
- impact first;
- then the Gulf test (**46%** vs past-season patterns, a pre-registered secondary; **9%** vs persistence, the primary, met) → US "missed our bar; **7th of 21**" → UAE parity caveat → live ledger as the pilot ask.

Numbers to remember: **2,189 · 46% · 7th of 21**.

## A. Gulf out-of-sample test (G12): headline evidence

| # | Claim (as worded in pitch) | Used in | Source | Status |
|---|---|---|---|---|
| A1 | Plan (countries, inclusion rule, comparators, pass bar) locked before any OMN/QAT/BHR/KWT/SAU data were downloaded | registration, deck 7, demo, video, one-pager, Q&A 8/11 | `docs/PREREG-GCC.md`; `docs/LOCK-GCC.json`; commits 91005ce (lock, 12:08:47Z) → d013228 (data, 12:10:18Z); independent audit `docs/REVIEW-R3-audit.md` §0 | R (self-attested local git until anchored; say "locked in our git", never "blind") |
| A2 | Influenza, frozen v1 method vs persistence: 0.914 (95% CI 0.843–0.983), pre-registered primary MET | all | `results/gcc/SUMMARY.md` PRIMARY | R |
| A3 | "9% less influenza forecast error than last week carried forward" | registration, deck 7, demo, video, one-pager | 1 − 0.914 = 8.6% (`results/gcc/SUMMARY.md`) | R |
| A4 | Influenza vs seasonal analog ("past-season patterns"): 0.536 (0.464–0.616), i.e. **46%** less error; a pre-registered secondary; below 0.6 in each country (OMN 0.574, QAT 0.446, SAU 0.594) | registration, deck 7, demo, video, one-pager, Q&A 2 | `results/gcc/SUMMARY.md` secondary and per-country tables; comparator defined in `docs/PREREG-GCC.md` §5 (seasonal analog/climatology) | R (always label "pre-registered secondary") |
| A5 | Influenza robustness: leave-one-country-out 0.904–0.929; country-clustered bootstrap 0.841–0.984 | deck 7, Q&A 11, limitations | `docs/REVIEW-R3-audit.md` §0 (independent audit reruns; scripts not committed) | R (audit) |
| A6 | Won 9/12 influenza country-seasons; losses OMN 2022/23 and 2024/25, QAT 2023/24 (tie) | deck 7, demo, Q&A 12, one-pager | `results/gcc/SUMMARY.md` per-country-season table | R |
| A7 | RSV is secondary: vs persistence 0.798 (0.719–0.894, registered bootstrap); country-clustered 0.712–1.026 (crosses 1); 95% coverage 0.83; SAU RSV 1.088 | Q&A 13, deck 7 small print, limitations | `results/gcc/SUMMARY.md`; `docs/REVIEW-R3-audit.md` finding 9 | R (**never** a headline) |
| A8 | RSV vs seasonal analog 0.685 (0.605–0.781) | Q&A 2 only | `results/gcc/SUMMARY.md` | R (secondary; not headlined) |
| A9 | Bahrain and Kuwait excluded by the pre-set rule (1 scorable influenza season each) | deck 7, Q&A 14 | `results/gcc/SUMMARY.md` inclusion table; `docs/PREREG-GCC.md` §3 | R |
| A10 | Forward in time, each country's own earlier seasons only, no UAE data, no pooling | deck 7, Q&A 11 | `docs/PREREG-GCC.md` §4; audit leak test (2,112 cases, 0 changes) | R |
| A11 | Data = WHO's full export (3 Oct 2026) via a public mirror; matches our independently fetched UAE rows exactly (419/419) and 23/23 spot-checked Gulf rows; full official re-pull pending | Q&A 16, limitations, TECHNICAL | `docs/DEVIATIONS.md` G1, G1b; `docs/REVIEW-R3-audit.md` §0 | R (**never** "verified row-for-row") |
| A12 | v1 chosen as primary after UAE v2 and forward-in-time results were known (disclosed) | Q&A 15, limitations, deck 7 small print | `docs/PREREG-GCC.md` §1 | R |
| A13 | "Our records show no one on the team had used the Gulf countries' data before" | Q&A 15 | `docs/PREREG-GCC.md` §1; audit filesystem search (`docs/REVIEW-R3-audit.md` §0) | R (records only; human exposure not checkable) |

## B. Forecast ledger

| # | Claim | Used in | Source | Status |
|---|---|---|---|---|
| B1 | Every round is hashed before WHO publishes the target week | deck 12, demo, video, one-pager | `ledger/`; `ledger/rounds/2026-11-08T1212Z_R1` | R |
| B2 | As of 8 Nov: **one forecast round** (data through W44), issued as R0 and re-issued as R1 with the v2 challenger. The v1 and persistence files are byte-identical (`2691894e…`, `6347b067…`) | deck 12, demo, one-pager, Q&A | `ledger/*.sha256` | R |
| B3 | 0 weeks scored | deck 12, demo | `ledger/SCOREBOARD.md` | R (refresh on the day) |
| B4 | The ledger is public, outside-anchored, or can't be rewritten | — | `ledger/ANCHOR.md` + the team's receipt | **P** (use only after the push and anchor; until then say "hashed and committed locally") |
| B5 | One horizon convention: target week-ending date + "+N wk after issue", the same as the hashed R0/R1 rounds (DEVIATIONS C8) | Q&A 25, TECHNICAL, limitations | `docs/RUNBOOK.md`; `ledger/*.meta.json` | R |

## C. US benchmark (CDC FluSight hub)

| # | Claim | Used in | Source | Status |
|---|---|---|---|---|
| C1 | NABD v1 vs the CDC FluSight ensemble: rel. WIS 1.22 (95% CI 1.01–1.52), margin 1.15, NOT MET ("missed our bar") | deck 8, demo, video, Q&A 18, limitations, one-pager | `results/SUMMARY.md` PRIMARY | R |
| C2 | 2024/25 1.03 (0.89–1.25); 2025/26 1.52 (1.09–2.03) | Q&A 19 | `results/SUMMARY.md` S3 | R |
| C3 | vs FluSight baseline 0.82 (0.66–1.02); CDC ensemble vs baseline 0.67 | limitations | `results/SUMMARY.md` S1, ref row | R |
| C4 | 11,660 forecasts, 53 locations, 2 seasons, horizons 0–3, 55 reference dates | deck 8 | `results/SUMMARY.md` | R |
| C5 | Protocol frozen before any test score, commit ac16901, SHA-256 2846533f… | deck 8, Q&A 21 | `docs/FREEZE.md` | R (self-attested) |
| C6 | League, single models: **7th of 21** in 2024/25 (0.693; CDC ensemble 0.673); **19th of 25** in 2025/26 (level with the baseline) | registration, deck 8, demo, video, Q&A 18, limitations, one-pager | `results/tables/league_table.csv`; method declared before computing (D7, D11) | R |
| C7 | Including ensembles: 13th of 41 (2024/25), 40th of 46 (2025/26). Must accompany C6 whenever `fig2_league_table.png` is shown (its titles use these denominators) | deck 8, Q&A 18 | same | R |
| C8 | Per-location wins vs the ensemble: 18/53 (2024/25), 0/53 (2025/26) | Q&A 19, limitations | `results/SUMMARY.md` D6 | R |
| C9 | Excluding the national series: 1.198 (1.014–1.449), still NOT MET; national share 46.0% | deck 8, Q&A 20 | `results/SUMMARY.md` D6 | R |
| C10 | Block bootstrap (L=4) primary CI 0.979–1.573; verdict unchanged | TECHNICAL | `results/tables/sensitivity_block_bootstrap.csv` | R |
| C11 | By as-of phase vs the ensemble: rising 1.27, flat 0.97, falling 1.29; under-prediction the largest component | Q&A 19, TECHNICAL | `results/SUMMARY.md` D10 | R (descriptive) |
| C12 | Relative economic value: NABD above the CDC ensemble at cost/loss ≤ 0.1, about equal at 0.2, below at ≥ 0.3 | TECHNICAL | `results/tables/rev_curves.csv` | R (descriptive, no CIs) |
| C13 | Coverage: 95% 0.92 vs the ensemble's 0.86; 50% 0.48 vs 0.52 | Q&A 23 | `results/SUMMARY.md` S2 | R |
| C14 | Scorer cross-check: our WIS equals an independent implementation exactly | Q&A 22, TECHNICAL | `results/tables/scorer_crosscheck.csv`; D9 | R |
| C15 | At the primary threshold (3/100k), median onset lead is 0 weeks for every rule, including the CDC's | deck 9, Q&A 4, limitations | `results/tables/alerts_us.csv` | R (diagnostic, D5; always say "at 3/100k") |
| C16 | Every rule had 0 false alarms at 3/100k | deck 9, Q&A 4, limitations | `results/tables/alerts_us.csv` (`false_alarm_loc_seasons` = 0) | R |
| C17 | First alerts issued after onset ("late"), 2024/25 at 3/100k: NABD 9, CDC ensemble 13, census 19. Timely detections: census 28 vs NABD 17 of 51 (2024/25); NABD 29 vs census 24 of 52 (2025/26) | deck 9, Q&A 4, limitations | `results/tables/alerts_us_detail.csv` (counts recomputed 8 Nov; matches `docs/REVIEW-R3-audit.md` finding 7) | R (diagnostic) |
| C18 | PPV at 3/100k: NABD 0.65/0.76; ensemble 0.41/0.67; census 0.60/0.46. Describe as "fewer late alerts", **never** "fewer false alarms" | TECHNICAL | `results/tables/alerts_us.csv` | R (diagnostic) |
| C19 | One missing week ×1.41 error; two weeks ×1.82 | limitations | `results/tables/dropout_us.csv` | R |
| C20 | US median input age at issue: 4 days | deck 11 | `results/tables/latency_us.csv` | R |
| C21 | The CDC FluSight hub accepts non-US teams; a PR is due Wednesdays 11 PM ET | Q&A (optional) | `docs/FLUSIGHT-PARTICIPATION.md` | R/V (nothing submitted) |

## D. UAE's own record

| # | Claim | Used in | Source | Status |
|---|---|---|---|---|
| D1 | Forward in time, v1 vs persistence: 1.002 (flu), 1.002 (RSV), i.e. parity | registration, deck 9, demo, video, Q&A 1, limitations, one-pager | `results/uae/SUMMARY-v2.md` | R |
| D2 | Multi-signal v2 worse than v1: 1.059 (1.016–1.111); locked protocol; retrospective | deck 9/11, Q&A 9, limitations | `results/uae/SUMMARY-v2.md`; `docs/LOCK-UAE-v2.json` | R |
| D3 | Feed removal: dropping non-sentinel or calendar slightly improved v2; testing volume ≈ 0; climatology helps most | Q&A 9, limitations | `results/uae/tables/ablation.csv` | R |
| D4 | UAE influenza alerts "3/3 onsets, 0 false alarms" | — | `results/uae/tables/alerts_uae.csv` (LOSO design) | **RET** (LOSO trains on later seasons; n = 3) |
| D5 | Missing latest week raises UAE mean WIS by 0.14–0.26 pp; a missing non-sentinel week triggers a fallback sub-model | limitations | `results/uae/tables/ablation.csv` | R |
| D6 | Exact per-signal contributions per forecast (linear model) | deck 6/11, demo, video, TECHNICAL | `results/uae/explain/`; tests | R |
| D7 | UAE lag 7 days for W44 on 8 Nov | Q&A 25, deck 11 | `data/raw/PROVENANCE.md` | R |
| D8 | The leakage test caught and fixed a real LOSO boundary leak in the first build | Q&A 22 | `results/uae/SUMMARY.md`; commit 463ab09 | R |
| D9 | LOSO vs persistence flu 0.76, RSV 0.78; "7 of 8 season-series" | — | `results/uae/SUMMARY.md` | **RET** |
| D10 | Training-history reading (POST HOC): UAE sentinel data start in 2022. The 2023/24 forward fold (1 training season) lost (flu WIS 4.75 vs persistence 2.21). With ≥2 seasons, flu won both folds (2.54 vs 2.66; 1.94 vs 3.08); RSV split (1.31 vs 2.14 won; 2.30 vs 1.89 lost) | deck 9, Q&A 1, demo, one-pager | `results/uae/v2/tables/forward_wis_by_season.csv`; `data/raw/flunet_are.csv` | R (always say "post hoc", "our reading") |
| D11 | Card, 8 Nov round, week ending 15 Nov (+1 wk after issue): RSV P(>10%) 51%, P(>20%) 13%; flu P(>15%) 94%, P(>30%) 27%; both "elevated, falling" | Q&A 3, demo | `app/screenshots/01_weekly_card_en.png`; app round-3 report | R |

## E. Problem and context

| # | Claim | Used in | Source | Status |
|---|---|---|---|---|
| E1 | Season-shape table (flu and RSV peaks and onsets by season, 2022/23–2025/26) | deck 2, demo, video, one-pager | `research/positioning.md` §1.1 ([DATA]) | R |
| E2 | "Flu peaked at 40.6% in October 2025 after a five-month plateau that peaked in February the season before"; "RSV peak moved between weeks 41 and 47 / across six weeks" | registration, deck 2, video, demo, one-pager | same | R |
| E3 | Problem framing: "bed managers and public-health officers plan the next three weeks; their defaults are last week's numbers and last year's pattern" | deck 2, demo, video, one-pager | `research/positioning.md` §2 (stakeholder table: "own census (looks back)", "fixed calendar window"); `docs/REVIEW-R3-judges.md` §2 | H/V (a characterisation of available tools, not a survey; never quantify it) |
| E4 | Tawam: 2,189 RSV admissions of children ≤5, 2018–22; infants <6 months mean stay 5.8 days; positivity 2.9% → 16% (period includes pandemic years) | registration, deck 3, demo, video, one-pager, outreach | [S1]; `research/burden.md` #1 | V |
| E5 | Dubai claims: 22% of under-2s with RSV hospitalised; <2% with a known risk factor; median cost US$2,241 | deck 3, one-pager, Q&A 10 | [S3] | V (abstract) |
| E6 | Tawam paediatric flu 2012–17: 33.5% admitted, 8% PICU | optional | [S2] | V (older data) |
| E7 | UAE flu case data not publicly available (The National, Jan 2026) | registration, deck 3, one-pager | [S6] | V |
| E8 | No public respiratory forecast for the UAE or GCC, **"to our knowledge"** | registration, deck 1/5, video, demo, one-pager | `research/positioning.md` §1.7 | V (absence of evidence; the qualifier is mandatory) |
| E9–E11 | Tableegh (Malaffi-linked notifications), UMOC (AI early warning), Rasid (wastewater) | deck 5, video, Q&A 26 | [S12], [S13], [S20] | V |
| E12 | ADPHC 2024 tender scope: outbreak detection; awardee unknown | Q&A 26 | `research/competitors.md` | V |
| E13 | Command-centre tools: up to about 72 h from inside-hospital data | deck 4, Q&A 27 | `research/competitors.md` | V |
| E14 | DoH: this season's activity similar to the previous two | deck 2 notes, Q&A curveball | [S7] | V |
| E15 | Dr Mahra Alhosani, DoH Director of Surveillance and Outbreak Response, gave the Sep 2026 update | outreach B | [S7] | V |
| E16 | Infant RSV window 1 Sep–1 Mar; RSV ≥10% before 1 Sep in 2 of 4 seasons | deck 4, Q&A curveball (context) | [S4] secondary; [DATA] | S / R |
| E17 | No conflict-of-interest clause; IP stays with the team; 6-month organiser right of first refusal on exclusive deals | deck 12, Q&A 10, one-pager | `research/tc.md` | V |
| E18 | Future Health 2026 theme "To Sense is to Predict" | video, deck 12, one-pager | [S25] | V |
| E19 | Gulf CDC regional system at the pilot stage, with ARI as a weekly-reported pilot disease | Q&A 29, one-pager | [S23] | V |
| E20 | Tawam study authors and units (UAEU Department of Pediatrics, Institute of Public Health); a contact address in the citation metadata for Dr Ahmed R. Alsuwaidi | outreach A1 | UAEU publication record (fetched 8 Nov) | V (confirm the corresponding author on the journal page before sending) |

## G. Workforce and business

| # | Claim | Used in | Source | Status |
|---|---|---|---|---|
| G1 | Hospital winter planner: hospital-supplied inputs → scenario bed-days, % of ward, staff-absence range, roster gap in AED; occupational-health playbook role | deck 10, video 6, demo, Q&A 6, one-pager | `app/planner.py`; `app/screenshots/04b_winter_planner.png`; staff absence follows flu and RSV by default (round 5) | R (scenario) |
| G2 | Bed-days SCENARIO page (sourced inputs: 2,189/5 years, LOS, US$2,241) | deck 6/10/11 | `app/screenshots/04_bed_days_scenario.png` | R (scenario, not a forecast) |
| G3 | Employer-absence secure aggregation (k ≥ 10 employers), synthetic data, SIMULATED | deck 10, Q&A 6, one-pager | `app/workforce.py`; `app/screenshots/10_workforce_simulated.png` | R (simulated) |
| G4 | No credible public UAE respiratory sickness-absence figure | deck 10, Q&A 6, limitations | `research/positioning.md` §1.6 | V |
| G5 | Pricing: a public-health feed licence per country per season; a hospital seat per facility; the seat should cost less than a handful of avoided admissions | deck 12, Q&A 10, one-pager | business hypothesis | H |
| G6 | Weekly bilingual bulletin PDF per ledger round | deck 6, demo [+] | `bulletin/make_bulletin.py`; `bulletin/out/`; `app/screenshots/12_bulletin_p1.png` | R |

## H. Borrowed-strength test (S1) and decision replays (S2, S4)

| # | Claim (as worded in pitch) | Used in | Source | Status |
|---|---|---|---|---|
| H1 | Plan and country lists locked before any new country's data were downloaded; model locked before any held-out row was extracted; scored once | deck 7b, one-pager, Q&A | `docs/PREREG-POOL.md`; `docs/LOCK-POOL-1.json`, `docs/LOCK-POOL-2.json`; `docs/FREEZE.md` | R (self-attested local git until anchored; never "blind") |
| H2 | Influenza, model pooled across countries vs each country's own-record model: 0.767 (95% CI 0.681–0.832), pre-registered primary MET, better in 18 of 18 held-out countries; "23% less forecast error" | deck 7b, one-pager, Q&A, README | `results/pool/SUMMARY.md` primary (1 − 0.767) | R |
| H3 | Where the country's own record was short (≤ 2 earlier seasons): 0.624 (0.540–0.705), "38% less error"; every country cut to 2 seasons: 0.640 | deck 7b, one-pager, Q&A | `results/pool/SUMMARY.md` key secondaries 1–2 | R (secondary; say "short record, the UAE's position", never "in the UAE") |
| H4 | Pooled vs last week carried forward: 0.879 (0.850–0.901), 18 of 18; the own-record model on the same cells: 1.145 | deck 7b, Q&A | `results/pool/SUMMARY.md` secondary 3 | R |
| H5 | 36 countries named in advance, 18 met the pre-set data rules; all 18 reported | deck 7b small print, Q&A | `results/pool/SUMMARY.md` inclusion and exclusion lists | R |
| H6 | UAE with the pooled model: 0.87 vs local v1, 0.77 vs persistence | Q&A only, with the label | `results/pool/SUMMARY.md` "already-seen countries" | R (**NON-CONFIRMATORY**: UAE data were seen; never a headline) |
| H7 | Roster rule replayed on the held-out countries (post hoc): pooled 10.5 mismatch weeks a season vs 12.3 for the own-record model (−1.81, 95% CI −3.00 to −0.72) and 16.6 for the past-season pattern | deck 7b small print, Q&A | `results/replay/pool/SUMMARY.md`; DEVIATIONS V2 | R (POST HOC; always with H8) |
| H8 | Under that rule the pooled model is not distinguishable from last week carried forward (10.5 vs 11.1; −0.56, −1.42 to +0.31) and missed slightly more surge weeks than the own-record model (2.7 vs 2.2 a season) | wherever H7 is used | same | R (must accompany H7) |
| H9 | "The pooled model is NABD's live UAE model" / any pooled-model claim about UAE hospital load | — | Pool is an opt-in ledger challenger; v1 is the hashed headline | X |

## F. Banned (X)

| # | Claim | Why |
|---|---|---|
| F1 | "NABD performs better during surges" (E1 exploratory) | Defined using realised truth; DEVIATIONS E1 |
| F2 | The CDC ensemble's 21–36% gain presented as NABD's | Not ours |
| F3 | ED, NSSP, weather or wastewater as inputs; Chronos-2 or ACI as active | Not built or run |
| F4 | "Pre-registered" applied to the UAE v1 numbers | Design-stage |
| F5 | Any Abu Dhabi hospital or operational result; SEHA bed or ED numbers; "RSV/flu fill Abu Dhabi's paediatric beds" | None exists (`docs/REVIEW-R3-audit.md` finding 21) |
| F6 | v2 "improves" on v1 | 1.059 (worse) |
| F7 | "Early warning of onset" / "earlier than" | Median lead 0 weeks |
| F8 | "RSV is climbing" / crisis framing | DoH says the season is similar to the previous two |
| F9 | Workforce-absence figures | None credible |
| F10 | "Predicts the nirsevimab window" | Context only |
| F11 | "The only" or "nobody publishes" without "to our knowledge"; the CDC ensemble "pools about 40 models" | Absence of evidence; unverified count |
| F12 | "Blind" | Self-attested lock; v1 chosen after UAE results; retrospective. Say "out-of-sample, plan locked before download" |
| F13 | "Published", "public" or "outside-anchored" for the ledger, or "can't be rewritten" | Not true until the push and anchor (B4) |
| F14 | GCC data "verified row-for-row against the official WHO API" | Only 23 rows spot-checked (A11) |
| F15 | "Fewer false alarms" | All rules had 0 false alarms at 3/100k; the PPV gap comes from late alerts (C16–C18) |
| F16 | "Calibrated" without qualification | GCC RSV coverage 0.83; say "probabilistic, coverage reported" |
| F17 | RSV Gulf "20%" in a headline | Secondary; clustered CI crosses 1 (A7) |
| F18 | UAE "3/3 onsets caught" | Retired LOSO design (D4) |
