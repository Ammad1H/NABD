> **SUPERSEDED (8 Nov 2026).** This is the original concept spec from 5 Nov. Several claims in it (e.g. Chronos-2 as a tested ensemble member, ED/weather fusion, 'early warning of onset') were never built or were retired after testing. The current, checked description is `docs/TECHNICAL.md`; claims are governed by `research/claims-ledger.md` and BUILD-SPEC v1.7.

# NABD: Final Winning Spec (Statement 06: Population and Workforce Health Early Warning)

**Future Health Digital Innovation Challenge 2026.** Round 7 of the idea loop. Built from R5-Y and fixed against the R6 judges (J1 public health, J2 AI/tech, J3 partnerships). Date: 5 Nov 2026.

**Status labels used throughout:**
- **[RESULT-PRELIM]**: computed today on real public data with the scripts in this folder. It is preliminary, so re-run before submission.
- **[DATA]**: re-derived today from the cached WHO FluNet file `data/flunet_are_webfetch.csv`.
- **[TARGET]**: pre-registered aim, not yet achieved.
- **[VERIFIED]** / **[UNVERIFIED]**: source status.

*Nabd (نبض) = pulse.*

> **Status update, Sun 8 Nov 2026 (supersedes the 6–7 Nov items in §10–11).** The plan assumed a 6 Nov start. Compressed path:
> - **Today (8 Nov):** create the public repo; run `ledger_issue.py --fetch`, then push and post the hash (first UAE round). Clone the FluSight hub and run the two probes to reproduce the preliminary numbers. Confirm team names and roles.
> - **Mon 9 Nov:** freeze `PROTOCOL.md` at 23:59 GST, and hash and push it. **BrainDrift gate (18:00 GST): it effectively defaults to NABD unless the HRS data is already downloaded with ≥400 events.**
> - **Tue 10 Nov:** register with title option 1 and the 150-word abstract (§9). Swap "since 6 November" for the actual first-ledger date.
> - **11–20 Nov:** follow §10 from Wed 11 Nov unchanged; the 7–8 Nov model work moves into 11–12 Nov. Expected ledger counts at submission fall slightly (about 4–6 UAE points rather than 6).
> - **Coordinator check (8 Nov):** recomputing from `results/ensemble_vs_persistence.csv` confirms the CDC ensemble's relative WIS against persistence of 0.64–0.79 (21–36% lower error) across the three complete seasons (2023/24–2025/26), h=0–3. The partial 2026/27 season reads 0.52–0.61 on few rows, so it is excluded. This is the **CDC ensemble's** skill, used to motivate the "size, not timing" framing. It is **not** NABD's result.

---

## 0. Flaw → fix ledger (all R6 CRITICAL/MAJOR/MINOR on NABD)

| # | Judge(s) | Flaw | Fix in this spec | Status |
|---|---|---|---|---|
| 1 | J2 CRITICAL (conditional) | **Leakage risk:** the backtest might use final NHSN truth as model input while the CDC ensemble only had real-time data | **Verified today:** the FluSight hub publishes **102 weekly real-time vintages** of the target data in `target-data/time-series.csv` (`as_of` from 2023-09-23 to 2026-11-04; both targets) plus 96 archived snapshots in `auxiliary-data/target-data-archive/`. NABD's retrospective inputs at each reference date come **only** from the vintage available then (rule in §5.3). NABD and the ensemble are scored against the **same** truth (final release as primary, first release as sensitivity). Missing vintage weeks fall back to the previous vintage (less information, which is conservative) and are logged | **FIXED** [VERIFIED by clone, 5 Nov] |
| 2 | J2 MAJOR | Success bar too low (beating FluSight-baseline is trivial) | Primary endpoint = **non-inferiority to the CDC FluSight-ensemble**: the upper 95% bootstrap bound of relative WIS (NABD/ensemble) is < **1.15**. Beating the baseline is only secondary (§5) | **FIXED** |
| 3 | J1, J2 MAJOR | "1–4 week" horizon overstated given the ~10–11-day WHO lag | Horizons are now stated **relative to the issue date**. UAE: *nowcast, +0.5, +1.5, +2.5 weeks*. US FluSight: *+0.5 to +3.5 weeks*. `ledger_issue.py` now writes `weeks_ahead_of_issue` and a `horizon_label` per row. Tested: the wk 44 target prints as "nowcast (already ended)" | **FIXED** |
| 4 | J1 MINOR (FAILED spot-check) | "RSV passed 10% in wks 30–34 in 2023 and 2024" | Re-derived [DATA]: first week ≥10% sentinel RSV was **wk 35 (2022), wk 38 (2023), wk 30 (2024), wk 42 (2025), wk 42 (2026)**. So it was before ISO wk 36 (≈1 Sep) in **2 of 4** complete seasons. The claim is restated as that and kept as context only | **FIXED** |
| 5 | J1, J2, J3 MAJOR | National sentinel positivity ≠ ED or bed load; lead over the hospital's own census never tested | **Tested today on the US analogue** [RESULT-PRELIM], with two findings that reshape the pitch: **(a) Onset timing:** a forecast rule on real-time public data did **not** warn earlier than a hospital's own-census threshold rule at matched premature-alarm rates (median lead about 1–2 weeks for both; `lead_time_probe.py`). **(b) Size over the next 0–3 weeks:** the CDC ensemble's real-time forecasts cut error **21–36%** against carrying the census forward (FluSight-baseline is persistence), with better 50% coverage, in each of 3 seasons (`ensemble_vs_persistence.py`). **Pitch changed accordingly:** NABD does not claim to tell a hospital *when* a surge starts (its census does that). It forecasts *how big and how long* (beds and staff), which is where forecasts measurably beat the census. The pilot test is pre-specified on the hospital's own counts (§5.6) and is **untested for Abu Dhabi at submission**, as stated | **FIXED** (US evidence real; AD untested and stated) |
| 6 | J1, J3 MAJOR; J2 MINOR | Workforce/occupational signal decorative (CPS monthly national; variable unverified) | **CPS dropped.** The occupational family is presented honestly as a **designed and simulated** feed: employer sickness-absence counts via k-anonymous secure aggregation. It is labelled simulated, with a pilot test plan. Four of the five Statement 06 signal families are real (§2). No decorative real-data claim remains | **FIXED** (honest partial) |
| 7 | J3 MAJOR | Paediatric-ED pressure / "SEHA staffs by calendar" claim unverified | **Removed.** No unverified claim about SEHA operations remains. Replaced by verifiable facts: the UAE RSV peak week varies (41–47) and RSV is rising now [DATA]; Abu Dhabi runs an infant nirsevimab programme (window 1 Sep–1 Mar) [secondary source]. Operational burden is a **pilot question** | **FIXED** |
| 8 | J1, J2, J3 MAJOR | Live ledger thin; not statistical evidence | Re-framed as an **integrity device** ("we can't move the goalposts"), shown as a sidebar. Statistical evidence comes from the retrospective vintage-correct backtest. Exact expected counts are in §5.5 | **FIXED** |
| 9 | J2 MAJOR | Construct mismatch: UAE positivity ≠ load | UAE claims are stated strictly as **positivity-forecast skill**. Load claims only appear for the US (admissions, ED %) and the AD pilot (hospital counts) | **FIXED** |
| 10 | J2 MAJOR | ACI calibration fitted on US counts and applied to UAE positivity | ACI runs **online on each target series itself**. On UAE (n=4 seasons) the calibration warm-up is stated, and UAE intervals are reported both with and without ACI | **FIXED** |
| 11 | J2 MINOR | "6-week RSV shift" rests on one outlier season; ≥20% surge threshold chosen post hoc | Wording: "peak week ranged 41–47; one season (2025) late". The surge Brier score is **dropped** as a UAE metric (uninformative at n=4) | **FIXED** |
| 12 | J1 MINOR | Use the FluSight ED target | Added: **`wk inc flu prop ed visits`** (NSSP) is a second US target. Vintages exist from 2025-12-17 [VERIFIED]. It is the ED-aligned target for the ops story | **FIXED** |
| 13 | J2 MINOR | NHSN gap mid-2024; short training history | Training uses 2022/23–2023/24 plus vintages. The gap (vintages 2024-04-27 → 2024-11-16) is stated. The 2024/25 early-season reference dates use the last available vintage and are flagged | **ACCEPTED** (stated) |
| 14 | J3 MAJOR | Buyer may have already bought (ADPHC 2024 tender; DoH–Microsoft PHIF) | Position NABD as **a forecast model plus pre-registered accountability protocol that feeds any platform**. The commercial user is hospital operations (which the tender did not target). Tender awardee still **UNVERIFIED**; ask at Q&A | **MITIGATED** |
| 15 | J3 | No AD buyer contact | 48-hour action: request a one-paragraph letter of interest from one SEHA/SSMC paediatric/ED lead or an MBZUAI-linked clinician (§11) | **OPEN** (team action) |

**Still unfixable before 20 Nov:**
- no Abu Dhabi hospital, district or daily data;
- UAE retrospective covers n=4 seasons;
- the playbook has not been reviewed by an official;
- the WHO FluNet licence is non-commercial (handled in §6);
- NABD may not reach non-inferiority to the CDC ensemble (pre-registered and reported either way).

---

## 1. One-page summary

**Problem.** Every winter, RSV and flu land on Abu Dhabi's hospitals together, but not on a fixed calendar.
- The UAE RSV peak came in ISO week 42, 41, 41 and **47** over the last four seasons.
- This season flu peaked at about 40% positivity (wk 40), and RSV is climbing behind it: 6.1% → 12.9% → 15.6% in wks 41–43 [DATA].
- Hospitals need to know **how big and how long** the next two to four weeks will be, to staff beds and rosters. Surveillance today describes the past week.

**Insight (from our own tests, real data).**
- **When a surge starts, a hospital's own census is enough.** On US state data, a forecast-based alarm was no earlier than a simple census threshold at the same false-alarm rate [RESULT-PRELIM], and in the UAE classic detectors already flag onsets.
- **The size of the next 0–3 weeks is where forecasting pays.** On three US seasons of archived real-time forecasts, a calibrated ensemble cut error by **21–36%** compared with carrying today's count forward, with better-calibrated intervals [RESULT-PRELIM, our analysis of CDC hub archives].
- **No one publishes calibrated RSV + flu forecasts for the UAE.** NABD does.

**Solution.**
- **Fused signals.** NABD fuses clinical (WHO FluNet UAE lab; US NHSN admissions), clinical-service and geospatial (US NSSP ED % by state and sub-state), environmental (Abu Dhabi weather) and administrative (school calendar, testing volume) signals into **calibrated quantile forecasts**:
  - for the UAE: RSV and flu positivity, nowcast to +2.5 weeks;
  - for the US: admissions and ED %, +0.5 to +3.5 weeks.
- **Weekly card.** Every week a bilingual (AR/EN) card shows fan charts, drivers, data freshness and a **playbook action that a named officer must approve** before anything happens. The occupational feed is a designed, simulated secure-aggregation module.

**Proof at submission.**
1. **Retrospective, vintage-correct backtest** on 2 US seasons × 53 locations against the CDC FluSight-ensemble. The **primary endpoint is non-inferiority** (rel. WIS upper 95% CI < 1.15) [TARGET].
2. **UAE retrospective** positivity-forecast skill vs persistence/analog baselines, n=4 seasons, shown as such [TARGET].
3. **A public, hash-stamped forecast ledger** from the first round (8–9 Nov), scored as WHO and CDC data arrive. Integrity, not statistics.
4. **Two published negative or neutral findings** that make the claims trustworthy: onset detection is solved, and forecasts beat census only for size.

**Impact.**
- **Hospital operations:** forecast-based bed and roster planning for the RSV + flu season.
- **Public health:** a calibrated feed plus accountability protocol that ADPHC's existing platform or PHIF can host.
- **Pilot:** 12-week shadow mode on one hospital's aggregate paediatric/ED counts, with exit criteria pre-specified (§5.6).

**Why us.** An MBZUAI team with time-series and foundation-model capability (Chronos-2 as an ensemble member, ablated), forecasting-hub-grade evaluation discipline, and a bilingual UI. We are physically near ADPHC, SEHA and SSMC for a shadow pilot. Most competing 06 entries are simulated; ours is real, pre-registered and timestamped.

---

## 2. Statement 06 requirement → artefact mapping

Statement 06 core: *"Fuse clinical, administrative, geospatial, environmental and occupational signals for near-real-time monitoring, prediction and automated prevention triggers."* (The official sub-requirement list is not in 01-statements.md; this maps the core sentence.)

| Requirement element | Built artefact at 20 Nov | Real / simulated |
|---|---|---|
| Clinical signals | WHO FluNet UAE sentinel + non-sentinel (flu, RSV, specimens); US NHSN state flu admissions (FluSight target, vintaged) | **Real** |
| Administrative signals | UAE academic calendar (2026/27 start 31 Aug [VERIFIED]); public holidays; **testing volume** (specimens processed) as a process covariate; US school-holiday indicators | **Real** |
| Geospatial signals | US NSSP ED % by state and **sub-state HSA** (rdmq-nq56) map; FluSight 53-location panel. AD district map | US **real**; AD district **simulated, labelled** |
| Environmental signals | NOAA GHCN-Daily Abu Dhabi Intl (temperature, humidity) as covariates; ERA5 optional | **Real** |
| Occupational signals | Employer sickness-absence feed via k-anonymous secure aggregation (k ≥ 10 employers; no single employer visible); synthetic data; pilot test plan | **Simulated, labelled** (honest gap) |
| Fusion | GLM with covariates + Chronos-2 (past and known-future covariates) + quantile ensemble; feed-removal ablation reports what each signal adds | Real (method) |
| Near-real-time monitoring | Weekly cadence; data-freshness badge with exact lag (FluNet ~10–11 days; NSSP weekly on Fridays; NHSN prelim Wed / official Fri [VERIFIED hub README]). Stated honestly as **weekly, lagged** | Real; limitation stated |
| Prediction | Calibrated quantile forecasts with horizons relative to issue date; non-inferiority test vs the CDC ensemble | Real |
| Automated prevention triggers (human-approved) | Versioned YAML playbook keyed to forecast bands → approve/modify/dismiss → append-only JSONL audit | Real (software); playbook content **illustrative, pending review** |
| Population *and workforce* | Population: real. Workforce: designed module plus secure-aggregation demo on synthetic data | Partial, stated |

---

## 3. Why it wins, judge by judge, and differentiation

**Public-health judge (DoH/ADPHC).**
- Real UAE data, honest horizons, and claims limited to what the data supports (positivity skill).
- A named-officer approval step, and aggregate-only data.
- The feed slots into the platform they already bought instead of competing with it.
- The two disclosed null or neutral findings show epidemiological maturity rather than hype.

**AI/tech judge (Microsoft / G42 / MBZUAI).**
- Vintage-correct backtest against the field's strongest public benchmark, with a pre-registered non-inferiority margin and bootstrap CIs.
- Foundation-model ablation reported even if null.
- Online conformal calibration on each series.
- The leakage question is answered by the data structure (102 vintages), not by assertion.

**Partnerships judge (PureHealth / M42 / Mubadala Bio).**
- Answers the buyer's killer question with data instead of a slide: *"What does your forecast tell me that my census doesn't?"* The answer: not *when*, but *how big and how long*, where forecasts cut error by about a third in the US archive.
- Clear 12-week shadow pilot with an exit metric on the hospital's own counts.
- The commercial product runs on the hospital's own data, so the WHO non-commercial terms don't apply.

**Differentiation:**

| Existing thing | What it does | NABD relationship |
|---|---|---|
| **Rasid** (ADQCC + G42 Healthcare) [VERIFIED] | Wastewater monitoring and AI early warning | Different layer (environmental sensing vs hospital-load forecasting). Integration offer: "add your RSV/flu wastewater signal as a covariate; we publish the skill gain." Never framed as a gap |
| **ADPHC 2024 AI epidemic-prediction tender** [VERIFIED tender exists; awardee UNVERIFIED] | Outbreak flagging / dashboard platform | NABD is a model plus protocol that the platform can host. We sell neither dashboard nor alerting engine |
| **DoH–Microsoft PHIF** [VERIFIED] | Population health intelligence; stated focus on chronic disease risk | Complementary: a respiratory-season load forecast feed |
| **CDC FluSight** | US forecasting hub | Our benchmark, not a competitor; no UAE coverage |
| **Visible 06 competitor repos** (R1-C: ≥8, mostly heat/workforce, simulated) | Simulated dashboards and alert cards | NABD: real data, vintage-correct, pre-registered, timestamped |

---

## 4. Architecture (minimal 10-day stack) and data

**Stack.**
- Python 3.11 throughout.
- `pandas`/`duckdb` for data.
- `statsmodels` (NegBin/binomial GLM).
- **Chronos-2** (`amazon/chronos-2`, Apache-2.0, ~120M parameters, covariate support [VERIFIED R4-J2]) run on a laptop GPU or Colab.
- ACI (simple numpy implementation).
- `scoringutils`-equivalent WIS in numpy (already in `ensemble_vs_persistence.py`).
- **Streamlit** app (AR/EN) for the card, map, ledger scoreboard and approve/dismiss → JSONL audit.
- **FastAPI** `/forecast` endpoint with OpenAPI.
- Docker Compose.
- A public GitHub repo for the ledger.
- No Kubernetes, Kafka or Keycloak in the build. Production path described only.

**Pipelines.**
- `adapters/` with one file per source and schema checks (pandera). The schema rejects any person-level field.
- `models/`: glm, chronos2, ensemble, aci.
- `eval/`: vintage-correct backtest, WIS, coverage, bootstrap.
- `ledger/`: frozen rounds plus SHA-256.

| Source | Use | Access (verified route) | Licence |
|---|---|---|---|
| WHO FluNet (xMart `VIW_FNT`, ARE) | UAE flu/RSV positivity, specimens | Public OData API; pulled 5 Nov [VERIFIED; R4-J2 reproduced live] | WHO terms: public-health and non-commercial use [VERIFIED R2-J1] |
| CDC FluSight hub `target-data/time-series.csv` | US targets with **real-time vintages** (`as_of`), NHSN admissions and NSSP ED % | GitHub `cdcepi/FluSight-forecast-hub` (cloned 5 Nov) [VERIFIED] | Hub MIT; underlying US Gov data |
| FluSight `model-output/FluSight-ensemble`, `FluSight-baseline` | Benchmarks (90 rounds each) | Same repo [VERIFIED] | Same |
| NSSP ED trajectories (rdmq-nq56) | Sub-state HSA ED % map, RSV ED % | data.cdc.gov [VERIFIED R6-J1] | US Gov |
| NOAA GHCN-Daily AE000041217 (Abu Dhabi Intl) | Weather covariates | NOAA [VERIFIED 27 Oct log] | Public domain |
| UAE academic calendar | Known-future covariate | Gulf News report of MoE calendar [VERIFIED start date] | Fact |
| Chronos-2 weights | FM ensemble member | Hugging Face `amazon/chronos-2` [VERIFIED R4-J2] | Apache-2.0 |
| Employer absence (AD) | Occupational design | Synthetic | Own |

---

## 5. Pre-registered evaluation protocol

Freeze by **Mon 9 Nov 23:59 GST**: commit `PROTOCOL.md`, publish its SHA-256 alongside the ledger, and change nothing afterwards except via a logged `DEVIATIONS.md`.

### 5.1 Targets
- **US-A:** `wk inc flu hosp` (NHSN state weekly flu admissions), horizons h = 0–3 relative to the FluSight reference date. That is **+0.5 to +3.5 weeks after issue**. 53 locations.
- **US-B:** `wk inc flu prop ed visits` (NSSP), same horizons. The secondary target, aligned to ED operations.
- **UAE:** sentinel RSV positivity and flu positivity, ISO weeks L+1…L+4, where L is the last published week. Relative to issue these are **nowcast, +0.5, +1.5, +2.5 weeks**.

### 5.2 Models compared
- NABD-GLM, NABD-Chronos-2 and the **NABD-ensemble (primary)**.
- Baselines: FluSight-baseline (persistence), FluSight-ensemble (US), seasonal-naive/analog (`baseline-v0`, UAE), persistence (UAE).

### 5.3 Vintages (the leakage fix)
For a US forecast with reference date R (a Saturday), NABD may use only the vintage with the **largest `as_of` ≤ R − 3 days** (the Wednesday submission deadline). Within that vintage it may use only rows with `target_end_date` ≤ R − 7.
- Where no vintage exists for that week, use the previous one and flag the round. Known gaps: 2024-11-16 → 2024-11-30, 2024-12-14, 2025-01-11, 2025-01-25, and 2025-09-24 → 2025-11-12.
- Covariates use their own vintages where these exist (NSSP vintages from 2025-12-17). Otherwise they are lagged by their documented release delay. Weather and calendar have no revision.
- UAE: no FluNet vintages exist, so replay with a **simulated 1-week publication lag** and state that revisions are not reproduced.

### 5.4 Metrics and endpoints
- **Splits:**
  - US: train/tune ≤ 2023/24 (vintages from 2023-09-23); test 2024/25 and 2025/26.
  - UAE: leave-one-season-out over 2022/23–2025/26. Sensitivity analysis excludes the low-volume 2022/23.
- **Metrics:** WIS on the FluSight quantile set; relative WIS (geometric-mean pairwise or ratio of sums; ratio of sums is primary, as in `ensemble_vs_persistence.py`); 50% and 95% interval coverage; for UAE RSV, peak-week absolute error.
- **PRIMARY (US-A):** NABD-ensemble is **non-inferior to FluSight-ensemble**. The upper bound of the 95% block-bootstrap CI (resampling reference dates) of rel. WIS (NABD/ensemble), pooled over both test seasons and h = 0–3, must be **< 1.15**.
- **SECONDARY:**
  - (a) rel. WIS vs FluSight-baseline < 1 (expected; most hub models achieve it);
  - (b) 95% coverage within 90–98%;
  - (c) US-B ED % rel. WIS vs ensemble (2025/26 only, reported);
  - (d) UAE WIS better than persistence and analog at the +0.5 and +1.5 wk horizons (n=4; descriptive CIs);
  - (e) feed-removal ablation (Δ WIS per signal family);
  - (f) Chronos-2 contribution (Δ WIS ensemble with vs without).
- **Truth:** final release (latest vintage) is primary for both NABD and the comparators. First release is a sensitivity analysis. CDC warns the latest week can be under 80% complete.
- **Reporting:** all results, including failures, by season and horizon.

### 5.5 Live ledger (integrity device; not an endpoint)
Rounds are committed and pushed before their targets exist, with the hash posted publicly.

| Stream | First issue | Scored by 20 Nov | Scored by 30 Nov | Assumption |
|---|---|---|---|---|
| UAE (flu + RSV) | 6 Nov | **6** (2 target weeks × 2 series, plus R2's wk 45) | **12** | FluNet lag about 10–11 days (wk 43 visible 5 Nov) [ESTIMATED]; if about 14 days, ~2 by 20 Nov |
| US-A FluSight format | Wed 11 Nov 23:00 ET | **53** (1 target week) | **159** | NHSN prelim Wed / official Fri |

### 5.6 Abu Dhabi pilot test (pre-specified; UNTESTED at submission)
- **Setting:** 12-week shadow on one hospital's aggregate daily paediatric ED visits and RSV/flu admissions.
- **Primary measure:** WIS of 7–21-day admission forecasts vs **persistence of the hospital's own census**. US analogue: the ensemble reduced error 21–36% vs persistence [RESULT-PRELIM].
- **Secondary measures:**
  - onset alarm lead vs the census threshold at matched premature-alarm rate (expected: parity, per the US probe);
  - absolute error in bed-days over the next 14 days;
  - whether national FluNet positivity adds skill beyond the hospital's own series (ablation).
- **Exit criteria:** rel. WIS < 0.9 vs own-census persistence, and 80% coverage within 70–90%.

### 5.7 Preliminary results already produced (US analogue; [RESULT-PRELIM])

| Probe | What | Result |
|---|---|---|
| `lead_time_probe.py` | Onset alarm: census threshold (final data, 0 lag) vs growth-forecast rule (real-time vintage), 155 state-seasons, T = 2/3/5 per 100k | At premature ≤10% and miss ≤10%: median lead census **2.0 / 2.0 / 1.0 wk** vs forecast **2.0 / 1.0 / 2.0 wk**. Useful 1–4-wk alarms: census 84–92% vs forecast 74–80%. **No onset advantage for the forecast.** |
| `ensemble_vs_persistence.py` | FluSight-ensemble vs FluSight-baseline (persistence), both real-time, final truth | rel. WIS **0.72–0.78 (2023/24), 0.66–0.79 (2024/25), 0.64–0.69 (2025/26)** across h0–h3, with 95% bootstrap CIs all below 0.9. 50% coverage: ensemble 45–57% vs persistence 26–49% |
| ED % vs admissions | Lag of max correlation of weekly log-growth, by state | Lag 0 in 41–67% of states, lag 1 in 20–49% (2023/24: 34 and 10 of 51; 2024/25: 21 and 25; 2025/26: 28 and 20). Median r 0.59–0.69. ED % moves **with or ≤1 week ahead of** admissions |
| UAE re-derivation [DATA] | Sentinel onset, flu ≥15% for 2 weeks | 2022: 41 · 2023: 41 · 2024: 42 · 2025: 38 · 2026: **33**. RSV peak 42/41/41/47 at 20.4/24.5/29.8/23.1%. 2026 RSV wk 41–43: 6.1/12.9/15.6% (61/392). Non-sentinel flu ≥15%: 40/42/40/**34** |

---

## 6. Responsible AI and governance

- **Aggregate only.** Adapters reject person-level fields (schema test in CI), and every input is a weekly or daily aggregate.
- **Human approval.** No playbook action leaves the system without a named approver: a hospital bed-manager for ops actions, an ADPHC duty officer for public actions. Approve, modify or dismiss decisions are written to an append-only audit log with reason codes.
- **Honesty in the UI.**
  - Horizons are labelled relative to the issue date.
  - A freshness badge shows the data lag.
  - Simulated layers carry a permanent "SIMULATED" watermark.
  - The UAE n=4 caveat sits on the panel.
- **Licence handling.** WHO FluNet is used for public-health evaluation and the non-commercial public-health feed only. The commercial hospital product runs on the hospital's own data and does not redistribute FluNet. WHO is never presented as an endorser.
- **Failure modes and mitigations:**
  - Feed outage: forecast falls back to the remaining feeds, and the widened interval is shown.
  - Testing-mix shift distorts positivity: specimen volume is used as a covariate, and a banner appears when volume changes by more than 30% week on week.
  - Model drift: ACI online recalibration, plus a weekly coverage monitor that triggers a review if 80% coverage falls below 65% over 6 weeks.
  - Automation bias: the card always shows the persistence forecast next to NABD's, and approval requires a reason.
- **Equity.** Forecasts are population-level. The pilot reports paediatric vs adult performance separately.

---

## 7. Demo script (3 min) and the 60-second judge moment

Nothing below is claimed until it exists. `⟨…⟩` = placeholder filled by real output on 19–20 Nov.

- **0:00–0:30, the problem.** "RSV peaked in week 42, 41, 41 and then 47 in the last four UAE seasons. This year flu peaked at 40% in week 40, and RSV is climbing behind it." (Chart from FluNet [DATA].)
- **0:30–1:00, what we learned first (honesty beat).** "We tested whether forecasting beats a hospital's own census at spotting *when* a surge starts. It doesn't, so we don't sell that. We tested whether it beats the census at saying *how big* the next three weeks will be. In the CDC's own archives, good forecasts cut that error by about a third." (Two bars from the probes [RESULT-PRELIM].)
- **1:00–1:45, the 60-second judge moment.**
  1. Open the live card: "Issued ⟨date⟩. RSV forecast for week ⟨…⟩: median ⟨…⟩%, 80% band ⟨…⟩." The horizons read *nowcast / +0.5 / +1.5 / +2.5 weeks*.
  2. Click **"Show the receipt"**: the GitHub commit from 6 Nov, the hash, and WHO's published values for the weeks that have since come in, landing inside or outside our band ⟨result⟩.
  3. The playbook suggests ⟨action⟩. The judge clicks **Approve** and the audit-log line appears.
  4. Toggle **"remove ED-syndromic feed"** to show the change in interval width on the US panel ⟨Δ⟩.
- **1:45–2:30, the proof.** US scoreboard: NABD vs CDC FluSight-ensemble, vintage-correct, 2 seasons × 53 locations: rel. WIS ⟨x⟩ [CI ⟨…⟩], non-inferiority margin 1.15 **met / not met ⟨…⟩**. UAE retrospective: ⟨WIS vs persistence⟩, labelled n=4 seasons.
- **2:30–3:00, the pilot.** "Give us one hospital's aggregate paediatric admissions for 12 weeks in shadow mode. If we don't beat your own census carried forward by 10%, you've lost nothing." (Exit criteria on screen.)

---

## 8. Pitch narrative (5 sentences) and 10-slide outline

> **SUPERSEDED, do not quote.** The wording in this section predates the tests. "Calibrated", "publicly timestamped", signal "fusion" and the SEHA framing are on the stop list in `research/claims-ledger.md` section F. The current narrative is `pitch/story.md`.

1. Every winter RSV and flu hit Abu Dhabi's hospitals together, but not on a calendar: the UAE RSV peak has landed anywhere from week 41 to week 47, and this year it is rising right behind a 40% flu peak.
2. We tested what forecasting can and cannot do. A hospital's own census already tells it *when* a surge starts, but calibrated forecasts tell it *how big and how long*, cutting error by about a third against carrying today's count forward in the CDC's own archives.
3. NABD fuses lab, ED, geospatial, environmental and administrative signals into calibrated RSV and flu forecasts with honest horizons, and turns them into staffing and bed actions that a named officer approves.
4. Every forecast has been publicly timestamped since ⟨first ledger date⟩ November, and our method is tested, vintage-correct, against the CDC's FluSight ensemble with a pre-registered bar, with all results shown, including where we lose.
5. One SEHA hospital can run NABD in shadow mode on its own aggregate counts for 12 weeks, and ADPHC's existing platform can host the same feed.

**Slides:**
1. Title + one-liner.
2. Problem: the variable RSV-on-flu season (UAE data).
3. What we tested: *when* vs *how big* (two probe results).
4. NABD: signals → calibrated forecast → approved action (architecture).
5. Statement 06 mapping (real vs simulated).
6. Proof I: vintage-correct non-inferiority vs the CDC ensemble ⟨result⟩.
7. Proof II: UAE retrospective (n=4) + the live ledger "receipt".
8. Responsible AI: aggregate-only, human approval, honesty UI, licence.
9. Pilot and business model: hospital shadow pilot (exit metric), ADPHC feed, Rasid integration offer.
10. Team, 90-day plan, ask.

---

## 9. Registration-form drafts (no result claims; targets labelled)

**Title options:**
1. **NABD: Calibrated RSV and Flu Surge Forecasts for Abu Dhabi Hospitals**
2. NABD: From Surveillance Signals to Approved Surge Actions
3. NABD: Sense, Predict, Prepare: Respiratory Season Forecasting with a Public Track Record

**One-liners:**
- NABD turns lab, ED, environmental and administrative signals into calibrated 1–3-week RSV and flu surge forecasts that hospitals and public-health officers can act on, with every forecast publicly timestamped.
- Not "when will the surge start", which a hospital's census already shows, but "how big and how long": calibrated forecasts plus a human-approved playbook.

**Abstract, 50 words:**
NABD forecasts the size and duration of RSV and influenza surges for Abu Dhabi, fusing clinical, ED, geospatial, environmental and administrative signals into calibrated forecasts. A bilingual card proposes staffing and bed actions that a named officer approves. Forecasts are publicly timestamped and benchmarked, vintage-correct, against the CDC FluSight ensemble.

**Abstract, 150 words:**
RSV and influenza reach Abu Dhabi's hospitals together each winter, but timing and size vary. The UAE RSV peak has ranged from ISO week 41 to 47 in recent seasons. NABD (Arabic for "pulse") is a population early-warning system for Statement 06. It fuses clinical (WHO FluNet UAE lab data, US hospital admissions), clinical-service and geospatial (ED syndromic data by region), environmental (weather) and administrative (school calendar, testing volume) signals. It produces calibrated quantile forecasts with horizons stated honestly relative to data lags. A bilingual card shows forecasts, drivers and data freshness, and proposes playbook actions that require approval by a named officer, with a full audit trail. Our evaluation is pre-registered. The target is non-inferiority to the CDC FluSight ensemble on vintage-correct US data, plus UAE retrospective skill against persistence. Every live forecast is committed publicly before its outcome exists. All data are aggregate; no individual is tracked.

**Abstract, 300 words:**
Every winter, respiratory syncytial virus (RSV) and influenza converge on Abu Dhabi's emergency and paediatric services, but not on a fixed calendar. In the last four UAE seasons, sentinel RSV positivity peaked anywhere from ISO week 41 to week 47. In 2026 RSV is rising directly behind an influenza peak of about 40% positivity. Hospitals need to know how large and how long the next weeks will be, and surveillance mostly describes the past.

NABD ("pulse") responds to Statement 06 by fusing five signal types where real data exist:
- clinical: WHO FluNet UAE flu and RSV laboratory surveillance, US NHSN hospital admissions;
- clinical-service and geospatial: US syndromic ED data by state and sub-state region;
- environmental: Abu Dhabi weather;
- administrative: school calendar, testing volume.

The occupational feed is delivered as a privacy-preserving secure-aggregation design, demonstrated on clearly labelled synthetic data. An interpretable statistical core and a time-series foundation model are combined into a calibrated quantile ensemble. Horizons are reported honestly relative to publication lags. A bilingual (Arabic/English) card shows forecasts, drivers and data freshness, and proposes playbook actions (surge rosters, bed opening, advisories) that only a named human approver can release, with every decision audited.

Our design starts from tests on public data. A hospital's own census already signals when a surge begins, so NABD focuses on forecasting magnitude and duration. Our evaluation is pre-registered before testing. The primary target is non-inferiority to the CDC FluSight ensemble on vintage-correct US data across two seasons and 53 locations. Secondary targets are UAE retrospective skill against persistence (four seasons, stated as such) and a feed-removal ablation. Every live forecast since ⟨first ledger date⟩ November 2026 is committed publicly before its outcome exists. NABD uses aggregate data only and can feed existing public-health platforms. Our proposed pilot is a 12-week shadow deployment on one hospital's aggregate admissions, with pre-specified exit criteria.

(Note for the form: the "1–3-week" wording in the one-liner refers to issue-relative horizons of up to +2.5 weeks (UAE) and +3.5 weeks (US). Keep it, or say "up to three weeks".)

**Team roles (placeholders):** ⟨Ammad: lead, data and ledger⟩ · ⟨Member 2: models and calibration⟩ · ⟨Member 3: app and API⟩ · ⟨Member 4: pitch, playbook, clinical liaison⟩.

---

## 10. Day-by-day build plan (6–20 Nov)

Roles: **D** = data and ledger, **M** = models and evaluation, **A** = app and API, **P** = pitch, playbook and outreach.

| Date | Deliverables (owner) | Cut-line if behind |
|---|---|---|
| **Fri 6 Nov** | Create public repo; `python3 ledger_issue.py --fetch` → push **UAE R1** and post the hash (D). Run `lead_time_probe.py --fetch` and `ensemble_vs_persistence.py` locally to reproduce [RESULT-PRELIM] (M). Register HRS (the BrainDrift contingency, 5 min) (D). Outreach email for a letter of interest (P) | — |
| Sat 7 Nov | Vintage-aware US loader (§5.3) + FluSight quantile writer (M); FluNet/GHCN/calendar adapters with schema checks (D) | — |
| Sun 8 Nov | NABD-GLM v1 US + UAE; first vintage-correct backtest pass on 2023/24 tune data (M); write `PROTOCOL.md` (M+P) | — |
| **Mon 9 Nov** | **Freeze `PROTOCOL.md` 23:59 GST** + hash (M). **BrainDrift gate, 18:00 GST:** if HRS is downloaded *and* the event count is ≥400, the team may reconsider; otherwise NABD is final (all) | Gate defaults to NABD |
| **Tue 10 Nov** | **Register** with title + abstract (§9) (P). Chronos-2 wiring with covariates (M) | Chronos covariates → univariate |
| **Wed 11 Nov** | **Issue US-A U1 by 23:00 ET** (Thu 08:00 GST) (M+D). Streamlit skeleton (A) | — |
| Thu 12 Nov | Full vintage-correct test 2024/25–2025/26: NABD vs ensemble and baseline + bootstrap (M); NSSP HSA map (A) | HSA map → state |
| Fri 13 Nov | **UAE R2** once FluNet wk 44 appears (check daily) (D); score R1 wk 44 (D); ACI per series (M) | — |
| Sat–Sun 14–15 Nov | UAE leave-one-season-out (M); feed-removal ablation (M); card AR/EN + approve → audit (A); playbook YAML (P) | Arabic on secondary screens |
| Mon 16 Nov | US-B ED % target run (M); simulated secure-aggregation absence module (A); `/forecast` API (A) | Absence module → slide only |
| Tue 17 Nov | Model card, README, limitations (M+P); deck v1 (P); playbook review request sent (P) | — |
| **Wed 18 Nov** | **Issue US-A U2** (M+D); score U1 when NHSN updates (D); demo rehearsal (all) | — |
| Thu 19 Nov | Fill demo placeholders with real outputs; 3-min video; deck final (P+A) | — |
| **Fri 20 Nov** | **UAE R3** if wk 45 is published (D); final scoreboard refresh; **submit** (all) | — |
| 21–30 Nov | Keep pushing rounds and scored points; judges see a growing, dated record | — |

---

## 11. Risks, residual weaknesses, and the next 48 hours

**Residual weaknesses (honest):**
1. **No Abu Dhabi hospital, district or daily data.** Every AD operational claim is a pilot hypothesis.
2. **UAE retrospective covers n=4 seasons** (2022/23 is low-volume). Skill CIs will be wide.
3. **Non-inferiority to the CDC ensemble may fail** (margin 1.15). The pitch survives because it is pre-registered and reported, but the headline weakens.
4. **The foundation-model gain may be null.** The visible AI is then the calibrated multi-signal ensemble.
5. **The live ledger counts are small** (about 6 UAE and 53 US scored at submission). It is an integrity device only.
6. **The occupational signal is simulated.** Fit with the "workforce" half of Statement 06 is partial.
7. **Buyer overlap:** the ADPHC tender awardee is unknown and PHIF exists.
8. **The playbook has not been reviewed** by a clinician or official.
9. **FluNet is non-commercial.** This is handled, but a judge may still ask.
10. **Release-day lags** (FluNet, NHSN) are estimates.

**Ammad, next 48 hours (by end of Sat 7 Nov):**
1. **Create the public GitHub repo** (e.g. `nabd-forecasts`). Run `python3 ledger_issue.py --fetch`, then commit, push and post the SHA-256 publicly. Do this **today, 6 Nov**: every day of delay costs scored points.
2. **Run locally:** `python3 lead_time_probe.py --fetch` and `python3 ensemble_vs_persistence.py <hub-clone>` to reproduce the preliminary results. Optionally run `python3 backtest_probe.py --fetch --ilinet --sens`.
3. **Register for RAND HRS** (free, about 1 day). This keeps the BrainDrift contingency alive for the 9 Nov gate.
4. **Confirm the team:** names and the four roles (D/M/A/P), and who can commit to the Wed 23:00 ET US rounds.
5. **Outreach:** send a short request for a shadow-pilot letter of interest to one SEHA/SSMC paediatric ED or bed-management lead, or to an MBZUAI-linked clinician. Also ask one public-health or clinical contact to review the playbook.
6. **Read the hack2skill T&C** for IP, multiple-entry and conflict-of-interest clauses (MBZUAI is a co-creator).

---

## 12. Sources

| Source | URL | Status |
|---|---|---|
| CDC FluSight forecast hub (targets, 102 `as_of` vintages, archive, ensemble and baseline outputs, metadata) | https://github.com/cdcepi/FluSight-forecast-hub | VERIFIED (cloned 5 Nov 2026) |
| FluSight-baseline method (persistence) | hub `model-metadata/FluSight-baseline.yml` | VERIFIED |
| CDC FluSight 2025–26 evaluation (33 of 39 models beat baseline) | https://www.cdc.gov/flu-forecasting/evaluation/2025-2026-report.html | VERIFIED by R6-J2; not re-fetched (tool limit) |
| WHO FluNet xMart API (ARE) | https://xmart-api-public.who.int/FLUMART/VIW_FNT | VERIFIED (data cached; R4-J2 live match) |
| WHO data terms | https://www.who.int/about/policies/publishing/data-policy/terms-and-conditions | VERIFIED R2-J1 |
| NSSP ED trajectories rdmq-nq56 | https://catalog.data.gov/dataset/nssp-emergency-department-visit-trajectories-by-state-and-sub-state-regions-covid-19-flu-r | VERIFIED R6-J1 |
| NHSN hospital respiratory reporting | https://cdc.gov/nhsn/psc/hospital-respiratory-reporting.html | VERIFIED (hub README) |
| Delphi Epidata (alternative vintages) | https://cmu-delphi.github.io/delphi-epidata/api/fluview | VERIFIED (doc) |
| Chronos-2 | https://huggingface.co/amazon/chronos-2 | VERIFIED R4-J2 |
| UAE 2026–27 academic year start | https://gulfnews.com/uae/education/uae-sets-august-31-start-for-20262027-academic-year-1.500528465 | VERIFIED |
| Abu Dhabi nirsevimab window (secondary) | https://pro.campus.sanofi/ae/respiratory-syncytial-virus/articles/rsv-prevention-guidelines-in-uae | VERIFIED secondary; DoH circular 37/2026 UNVERIFIED |
| UAE RSV budget-impact (context) | https://www.ispor.org/heor-resources/presentations-database/presentation-cti/ispor-europe-2026/poster-session-3-4/budget-impact-of-rsvpref-maternal-vaccine-and-nirsevimab-monoclonal-antibody-to-protect-infants-in-uae-against-respiratory-syncytial-virus | UNVERIFIED content |
| Rasid (ADQCC) | https://mediaoffice.abudhabi/en/economy/abu-dhabi-quality-and-conformity-council-implements-rasid-wastewater-monitoring-platform | VERIFIED R2-J3 |
| ADPHC AI epidemic tender (Jul 2024) | https://www.agbi.com/health/2024/07/abu-dhabi-launches-ai-tender-to-predict-epidemic-threats/ | VERIFIED exists; awardee UNVERIFIED |
| DoH–Microsoft PHIF | https://www.doh.gov.ae/en/news/doh-signs-a-memorandum-of-understanding-with-microsoft-to-create-an-ai-powered-phif- | VERIFIED R4/R6 |
| DoH population health intelligence platform (GITEX 2025) | https://www.mediaoffice.abudhabi/en/health/department-of-health-abu-dhabi-unveils-worlds-1st-ai-powered-population-health-intelligence-platform-at-gitex-global-2025/ | VERIFIED R4 |
| ADPHC seasonal flu campaign 2025–26 | https://www.mediaoffice.abudhabi/en/health/abu-dhabi-public-health-centre-vaccinates-350000-plus-people-as-part-of-2025-2026-annual-seasonal-influenza-campaign/ | VERIFIED R4 |

**Scripts and outputs in this folder:**
- `lead_time_probe.py` → `results/lead_time_probe.csv`
- `ensemble_vs_persistence.py` → `results/ensemble_vs_persistence.csv`
- `ledger_issue.py` (issue-relative horizons added)
- `backtest_probe.py` (UAE onset probe, unchanged)
- `data/flusight/time-series.csv` (hub snapshot, 5 Nov)
- `RUN-ME.md`
