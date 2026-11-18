# NABD: Judge Panel Review, Round 2 (8 Nov 2026)

> **What this file is.** A simulated review written by an AI assistant in a separate session, asked to act as a panel of challenge judges (public health, AI, partnerships). No human reviewer, government official or company employee wrote, saw or endorsed it. It is kept because the fixes it prompted are traceable in `docs/DEVIATIONS.md`.

**Panel.** J1 is a senior public-health official (DoH/ADPHC). J2 is a principal AI/ML scientist (Microsoft/G42/MBZUAI). J3 is a partnerships and venture lead (PureHealth/M42). Each judge scored independently, and the views were then merged. None of us built NABD.

**Inspected.** docs/SPEC.md, BUILD-SPEC.md, PROTOCOL.md, FREEZE.md, DEVIATIONS.md and BUILD-LOG.md; results/SUMMARY.md, summary.json, alerts_summary.json, tables/*, figures/* (all 3 PNGs viewed) and uae/*; app/screenshots/* (all 5 viewed) and app/README.md; research/burden.md, tc.md and competitors.md; pitch/registration.md, deck-script.md, demo-script.md and qa.md; and the code in models/, uae/, adapters/, playbook/ and ledger/, plus the git log.

---

## 0. What we found that the team's own documents do not say

Read this first. Several of these findings contradict the team's own status claims.

1. **No scored model fuses signals.**
   - The US model is admissions-only. PROTOCOL §2.4 says "No other data source enters the US models."
   - The UAE model (`uae/models.py`) uses sentinel positivity, the change in specimen volume, and a climatology built from the same series.
   - Weather is a sinusoidal placeholder labelled NOT REAL; NOAA was never retrieved.
   - NSSP ED data is not ingested anywhere.
   - The school calendar appears only as a line of text on the card.
   - Yet the registration abstract, the deck (slide 4) and SPEC §1 all say NABD "fuses" clinical, ED, geospatial, environmental and administrative signals. research/tc.md marks Statement 06 requirement 1 as "Met". On the scored artefacts it is **not met**.
2. **The pitch's "size" argument uses the CDC's numbers, not NABD's.**
   - The "21–36% less error than the census" claim (slide 3, demo 0:25, Q&A #4) is the **CDC ensemble's** gain over persistence.
   - NABD's own US gain over persistence is 0.816 with a 95% CI of 0.655–1.023, so S1 is formally not met (`better_than_baseline: false`).
   - In 2025/26 NABD **equals** persistence: 0.998 (0.668–1.485).
   - A judge who reads results/summary.json will see that the central value proposition was borrowed.
3. **The registration text claims features that do not exist.** It says "A bilingual card explains what drove each forecast" and lists "the signals, weeks and regions that drove them". The card itself says "Drivers (descriptive context, not model attributions)", and the Feed-removal page shows DEMO because no `ablation*.csv` exists.
4. **Q&A #11 claims online adaptive conformal calibration. It was not used.** config.yaml says `aci: not used in v1 frozen run; fixed widening k only`. Q&A #8 ("Matching it within a margin…") is now false.
5. **The weekly card contradicts its own action.**
   - RSV fell from 15.6% to 10.5% (W43 to W44), and the NABD median declines 12.4 → 10.1 → 8.4 → 7.4.
   - The card still fires **"Tier 2 · band rsv_rising"** and asks the bed manager to "Confirm surge roster for the next 2 weeks".
   - The cause: `playbook.yaml` bands are level-only (10–20%) but named for a direction.
   - A DoH judge will spot this within 10 seconds of opening the demo.
6. **"RSV is climbing behind it" is stale.** It appears in SPEC §1, the demo script and the deck notes, but W44 sentinel RSV is 10.5% (36/342), down from 15.6%.
7. **The 80% band at +1 week is 4.6–21.4% RSV positivity.** That band is about 4.6 times wider at the top than at the bottom, so no one can staff a roster from it. The card does not show any decision-relevant quantity, such as the probability of exceeding a threshold.
8. **Lead time is zero.** For every rule (NABD, FluSight-ensemble and census), the median lead of timely alerts is **0 weeks**, and pooled sensitivity is lower for NABD than for the census (0.446 vs 0.505). The theme is "To Sense is to Predict", and the organisers ask for warnings "early enough to change action". This is the most damaging number in the folder after the primary result. The pitch says "lead parity" but never puts the 0 on a slide.
9. **"Pre-registration" is self-attested.**
   - The protocol was committed at 06:47Z and test results at about 07:00Z the same morning, in a **local, unpushed** repo.
   - Git commit times are author-set, so no third party can verify the order.
   - Ledger R0 is also unpublished ("not public" in the git log).
   - As of today the honesty headline rests on the team's word.
10. **The UAE track was never pre-registered.** PROTOCOL covers only US-A. The UAE leave-one-season-out (LOSO) design trains on *later* seasons when testing earlier ones. The only fold that is truly forward in time (2025/26, trained on 2022–24) is the one where **RSV loses to persistence** (WIS 1.97 vs 1.84), and it is the late-peak season (week 47) that the pitch uses to show variability.
11. **Post-peak overshoot is severe and operationally costly.** fan_chart_CA_TX_h1.png shows NABD h1 medians of about 4,400 (CA) and about 5,000 (TX) in Feb 2025 when truth was about 2,500–2,800, with 95% upper bounds of 11–12k. A bed manager acting on that would over-staff by roughly 2× at exactly the moment the wave turns.
12. **Missing data hurts badly.** One week of missing input raises WIS 1.41-fold, and two weeks 1.82-fold. Because the model is univariate there is no other feed to fall back on, so the SPEC §6 promise ("forecast falls back to the remaining feeds") is not implemented.

What is genuinely strong:
- The vintage-correct back-test against the hardest public benchmark, with a frozen protocol, logged deviations and a leakage test that fires when a leak is injected. The test also caught a real LOSO leak.
- Results are reported in full, including the failure.
- Alert **PPV**: NABD 0.71 vs 0.54 for FluSight-ensemble and 0.53 for census, with 0 false-alarm location-seasons. This directly answers the organisers' "calibrated to avoid alert fatigue".
- 95% coverage of 0.92 vs the ensemble's 0.86.
- UAE skill over persistence and seasonal analog in 7 of 8 season-series.
- A hash-chained audit log, named-approver workflow, SIMULATED watermarks, bilingual UI and a reproducible `make all` that runs in 22 s.

---

## 1. Scores by role (1–10)

### J1: Senior public-health official, DoH/ADPHC

| Axis | Score | Reason |
|---|---|---|
| Impact | 5 | The problem is real and the burden evidence is solid (Tawam: 2,189 RSV admissions; Dubai: 22% of infants hospitalised). But the output is national sentinel positivity with a +1-week 80% band of 4.6–21.4%, with no emirate, district or load figure, and DoH itself says this season is normal. |
| Technical depth / novelty | 5 | The evaluation discipline is above anything we usually see from student teams. The model is a damped trend that I could not explain to a minister as "AI". |
| Working demo & evidence | 4 | The card works and is bilingual. But it recommends a surge roster while forecasting decline, its "drivers" are explicitly not attributions, and the US proof page dumps tuning tables with the verdict hidden in a collapsed JSON. |
| Responsible AI | 8 | Aggregate-only data, a named approver with reason codes, a hash-chained audit, SIMULATED watermarks, honest freshness and horizons. Points lost: the playbook has not been reviewed and there is no role-based access control (RBAC) view. |
| Scalability / deployment | 6 | Built on FluNet, so in principle it works for any FluNet country. It is weekly and lagged, Docker was never built, and there is no integration path with the ADPHC platform or PHIF beyond a claim. |
| Commercial path / pilot | 5 | The shadow-pilot design with pre-specified exit criteria is exactly right. But there is no data partner, no letter of interest (LOI), and overlap with the 2024 ADPHC tender is unresolved. |

**J1 verdict.** Responsible and careful, but it does not yet tell my duty officer anything they can act on this week. The one action it does show is wrong for the data on screen. Zero-week lead undercuts the "early warning" label. **Not top 3 as it stands.**

### J2: Principal AI/ML scientist, Microsoft/G42/MBZUAI

| Axis | Score | Reason |
|---|---|---|
| Impact | 5 | Calibrated forecasting where no hub exists is a legitimate gap. But the US evidence shows the model is not better than persistence (CI up to 1.02), so the UAE "size" value is still unproven. |
| Technical depth / novelty | 4 | A damped pooled log-linear trend with NB and empirical quantiles, plus a 5-term linear regression for the UAE. There is no foundation model (not run), no ACI, and no covariates. The infrastructure (vintages, bootstrap, leakage tests) is about 8/10; the modelling is about 3/10. |
| Working demo & evidence | 6 | Primary 1.22 (1.01–1.52), NOT MET, reported straight. That credit is offset because S1 is not met, 2025/26 equals persistence, the UAE track was not pre-registered and its LOSO uses future seasons, and E1 conditions on truth (it describes a momentum model; it is not a finding). |
| Responsible AI | 7 | Leakage control is exemplary. Points lost because the pitch overclaims fusion, ACI and explainability that the code does not have. That gap is a responsible-AI problem in its own right. |
| Scalability / deployment | 6 | Deterministic, fast (22 s), and a FastAPI endpoint is in place. The model would transfer to other FluNet series, but none was tested. |
| Commercial path / pilot | 4 | No hospital-level model or data exists. The pilot assumes a method that has only been tested at state or national level. |

**J2 verdict.** This is the most honest entry I will read this year, and honesty is necessary but not sufficient. I would rank it top-quartile on rigour and bottom-half on modelling. The moment I find "fuses five signal families" in the abstract and an admissions-only model in the code, the honesty premium disappears. **Not top 3 unless the claims and code are reconciled and some real modelling depth appears.**

### J3: Partnerships / venture lead, PureHealth/M42

| Axis | Score | Reason |
|---|---|---|
| Impact | 5 | Nothing quantifies bed-days, agency-staff cost or avoided boarding in AED. "How big and how long" is the right question, but it is never priced. |
| Technical depth / novelty | 5 | Credible team process. I cannot tell from the deck what the defensible technology is, and the "dated track record" moat is days old and not yet public. |
| Working demo & evidence | 5 | A polished bilingual card. My first question will be "the CDC beat you, so why would SEHA buy this?", and the deck has no prepared answer beyond "we're honest". |
| Responsible AI | 7 | Strong governance story that a PureHealth compliance team could adopt. The WHO non-commercial licence is handled but will still come up. |
| Scalability / deployment | 6 | A GCC FluNet roll-out is plausible and cheap but has not been shown. There is no EHR or HIS integration story, and the 72-hour tools (GE CareIntellect) own the hospital-ops seat. |
| Commercial path / pilot | 3 | No LOI, no named champion, no price, no unit economics. The buyer is unclear across ADPHC's tender, PHIF and hospital ops. SEHA is our own subsidiary, and nobody there has been asked. |

**J3 verdict.** I'd take a coffee meeting, not a pilot, on this deck. One letter from a SEHA, SSMC or Cleveland Clinic Abu Dhabi clinician plus a bed-days-at-stake slide would move me two points. **Not top 3.**

### Merged panel verdict

| Axis | J1 | J2 | J3 | Mean |
|---|---|---|---|---|
| Impact | 5 | 5 | 5 | 5.0 |
| Technical depth / novelty | 5 | 4 | 5 | 4.7 |
| Working demo & evidence | 4 | 6 | 5 | 5.0 |
| Responsible AI | 8 | 7 | 7 | 7.3 |
| Scalability / deployment | 6 | 6 | 6 | 6.0 |
| Commercial path / pilot | 5 | 4 | 3 | 4.0 |
| **Overall** | | | | **≈5.3** |

**Not a likely top-3 as it stands.** On rigour and responsible AI it is probably in the top 10–15% of about 400 entries, most of which are simulated dashboards, so a finalist or shortlist place is plausible. Top 3 is unlikely for three reasons:
- **Impact comes first in the criteria, and impact is NABD's weakest axis.** There is no load figure, no Abu Dhabi number, no price, and a median lead of 0 weeks.
- **The proof cuts against the product.** NABD lost the primary endpoint, and its "size beats census" claim belongs to the CDC.
- **Several public claims are not backed by the code.** Fusion, explainability and ACI are claimed but not built. For an entry whose differentiator is honesty, that is the fastest way to lose.

There is a narrow path to top 3 by 20 Nov. It needs: claims reconciled with code; at least one real non-lab signal in a scored UAE model; real per-forecast attributions; independent public timestamps; and one named Abu Dhabi clinical partner. The probability is low-to-moderate, and it depends heavily on the LOI.

---

## 2. How to present the NOT MET primary result

### Headline recommendation
**Don't make the honest benchmark discipline the headline.** Discipline is a property of the team, not an impact, and "Impact first" is the organisers' first criterion. **Don't make E1 the headline either.** It is post hoc, conditions on truth, and J2 will read it as rescuing a loss.

Headline (slide 1 and the one-liner):
> **"The UAE has no respiratory forecasting hub. NABD is one: calibrated RSV and flu forecasts with a public, tamper-evident track record, held to the CDC's standard."**

- The **product proof** is UAE skill, stated with its limits:
  - "Beat carrying last week forward in 7 of 8 season-series (flu 4/4, RSV 3/4), with roughly 22–24% lower forecast error (WIS) pooled. Four seasons only, and RSV lost in the most recent season."
  - Then the external-validation result (Fix 7), if it lands.
- The **credibility proof** is the US stress test, NOT MET included. It is the evidence that the UAE numbers were not tuned until they looked good.
- The **alert-fatigue proof** is PPV 0.71 vs 0.54 (CDC ensemble) and 0.53 (census), with 0 false-alarm location-seasons. This maps directly onto the organisers' wording "calibrated to avoid alert fatigue". **Disclose the 0-week median lead next to it**, because hiding it would be the larger risk.

### Slide placement (replaces deck slides 6–7)
1. Title
2. Problem
3. *When* vs *how big*. **Fix:** label the 21–36% as "the CDC ensemble's gain over persistence (not ours)".
4. Architecture. **Fix:** mark which signals are live in which model.
5. Statement 06 checklist
6. **Proof I: UAE** (headline evidence)
7. **Stress test vs the CDC: NOT MET** (below)
8. **What the miss taught us, and how we'll be checked**: the v2 pre-registration hash, the FluSight-hub submission, the ledger
9. Responsible AI
10. Pilot and ask

Placing NOT MET at position 7, after the UAE result and before the forward plan, makes it read as calibration of trust, not as the verdict on the entry. **Never put it on the last slide or leave it out of the video.**

### Slide 7 wording (use verbatim or near it)
**Title:** *"We set our bar at the CDC's best. NABD v1 missed it, and here is exactly where."*

- Frozen 8 Nov 06:47 UTC, before any test score (SHA-256 `2846533f…`, posted publicly ⟨date⟩). Real-time data only: 53 US locations × 2 seasons × 4 horizons = 11,660 forecasts.
- Error relative to the CDC FluSight ensemble (pools about 40 models): **1.22** (95% CI 1.01–1.52). Our bar was an upper bound below 1.15. **NOT MET.**
- 2024/25: **1.03** (0.89–1.25), level with the ensemble on the point estimate. 2025/26: **1.52** (1.09–2.03).
- Failure mode: overshoot after the peak (chart: Texas, Feb 2025). *We found this after the fact; it is a hypothesis, not a claim.*
- ⟦If Fix 4 is done:⟧ Among ⟨N⟩ individual CDC-hub models scored the same way, NABD v1 ranks ⟨k⟩. *This comparison was declared before we computed it.*
- **Visual:** a forest plot by season and horizon, with the 1.15 margin as a red line and "NOT MET" written in red **by the team**.

**Speaker note (about 25 s):** *"In the US, use the CDC ensemble: it pools about forty teams, and in 2024/25 we came close to it. In 2025/26 we didn't. We froze this test before running it and we're showing you the season we lost. That's why you can believe our UAE numbers, where there is no ensemble to lose to, because there is no forecast at all."*

### Q&A lines to prepare (new)
- **"Your model didn't even significantly beat persistence in the US. Why trust it in the UAE?"** Pooled, the CI touches 1.02; in 2024/25 it was 0.69 (0.57–0.81), and in 2025/26 it equalled persistence. In the UAE it won 7 of 8 season-series, but four seasons is thin. That's why the frozen UAE model is being tested on other countries' FluNet data and in public every week.
- **"Lead time is zero. Where is the early warning?"** Onset lead is at parity with the census for every method, including the CDC's. We don't sell onset. We sell fewer false alarms (PPV 0.71 vs 0.53) and the size of the next 3 weeks. *Only say "size" if Fix 3/7 numbers support it; otherwise say "calibrated range".*

### Things that would look like spin (do not do)
- Moving the margin.
- Promoting S6 log-scale (vs baseline 0.76, CI 0.70–0.83) or 2024/25 alone to headline.
- Quoting E1's 0.893 without "post hoc, defined with hindsight".
- Saying "near-parity with the CDC" for the pooled result.
- Dropping the 2025/26 row.
- Re-tuning on the test seasons and showing it as "v1.1".

---

## 3. Improving before 20 Nov without p-hacking: what is credible and what moves goalposts

| Proposal | Verdict | Conditions / why |
|---|---|---|
| **Pre-register NABD-v2 now and evaluate it prospectively on 2026/27 rounds after the freeze** | **Credible, but it is integrity, not evidence.** | The hub season started 7 Oct; the first round NABD can forecast blind is reference date 14 Nov (due Wed 11 Nov 23:00 ET). By 20 Nov about 53 cells will be scored, and by 30 Nov about 150–160 (1–2 reference dates). That has no power to test non-inferiority. **Requirements:** hash the v2 spec and post it to a **third party** (OSF registration, Zenodo DOI, or a public PR) *before* the 11 Nov round. Run **v1 unchanged alongside v2**. Fix the primary comparison now (v2 vs FluSight-ensemble, same margin, same truth rule). Do not score v2 on the 2024/25–2025/26 test seasons except as a labelled "contaminated, post hoc" line. |
| **Submit frozen v1 (and v2) to the CDC FluSight hub itself** | **The strongest credibility move available. Do it.** | The CDC then holds the timestamp and does the scoring, which removes "self-attested" from the story. **Unverified:** hub team-registration, metadata and model-designation rules; read `model-metadata/README` in the full hub before 11 Nov. Even if the PR is never merged, a public PR time-stamps the forecast. |
| **Stack or augment the CDC ensemble for the US** | **Goalpost-moving if built and shown on the test seasons. Credible as positioning only.** | Building "NABD+ensemble" after E1 showed NABD complements the ensemble in rising phases is choosing the analysis after seeing the result. And it is irrelevant to the UAE, where no ensemble exists. Keep the *positioning* ("in the US, use the hub; NABD brings hub-grade forecasting where none exists") and skip the stack. At most, one exploratory appendix line: an equal-weight average, no tuned weights, declared in DEVIATIONS before computing. |
| **Regime-aware switching from E1, as a pre-registered v2 hypothesis** | **Credible only if the regime signal is real-time and v2 is judged prospectively. Otherwise it is textbook forking paths.** | E1 defines phases using truth, so a real v2 needs a real-time turning-point signal, such as a negative second difference in local log-growth, or damping that increases with deceleration, fixed in the pre-registration. Expect it to give back part of the rising-phase gain. Present it as "what we'll learn this season", never as a result. J2 will check that v2 was not tuned on 2024/25–2025/26. If any tuning used those seasons, say so on the slide. |
| **Run Chronos-2 on a laptop or Colab** | **Credible.** | Running it as a standalone member (S5) is within the protocol, which anticipated it. Adding it to the primary ensemble is a post-freeze change: report that as a logged deviation and sensitivity analysis, never as the new primary. Report it even if the gain is null. |
| **Pre-declared league-table context: score every individual CDC-hub model the same way and place NABD v1 among them** | **Credible and high value. Our addition.** | This does not change NABD's numbers; it changes the reference frame, which is how the field judges a model. **Requirements:** declare the method (pairwise relative WIS per Cramer et al.; minimum-coverage rule; same truth) in DEVIATIONS as D5 before cloning the full model-output. Report the rank whatever it is. **Risk:** in 2025/26 NABD equalled the baseline, and the CDC says 33 of 39 models beat the baseline that season, so NABD may rank in the bottom sixth for 2025/26. Pre-commit to showing it anyway. |
| **External validation of the frozen NABD-UAE-v1 on other FluNet countries (GCC: KSA, QAT, OMN, KWT, BHR; plus the cached US FluNet 2015–19 and 2022–26)** | **Credible and high value. Our addition.** | The config is frozen and these countries were never seen. **Requirements:** hash a short UAE-PROTOCOL first, listing the country list, the data-sufficiency exclusion rule (e.g. ≥3 seasons with ≥20 specimens/week), and the criterion (rel. WIS vs persistence < 1 and season win count). This turns n=4 into n=4×K and makes "GCC-ready" a measured claim. |
| **Add covariates (NOAA weather, school calendar, non-sentinel FluNet) to a UAE v2** | **Credible if v1 stays the headline UAE number.** | v2's LOSO runs on seasons the team has already seen, so label it "development". Its formal tests are the external countries and the prospective ledger. Report the feed-removal Δ even if it is null; a null weather effect is a finding. |
| **Freeze a UAE protocol at all** | **Required.** | The UAE track is currently unprotected. Freeze v1 as-is for the prospective ledger. Disclose in BUILD-LOG how many UAE model variants were tried before v1. |

---

## 4. Gaps against the official Statement 06 requirements (research/tc.md)

| # | Requirement | Gap | Severity |
|---|---|---|---|
| 1 | Multi-signal surveillance (≥2 materially different signal types) | No scored model uses a non-lab signal. US: admissions only (PROTOCOL §2.4). UAE: positivity, specimen volume (the same lab system) and its own climatology. Weather is a NOT-REAL placeholder, NSSP is not ingested, and the calendar is text only. tc.md's "Met" is wrong. | **CRITICAL** |
| 2 | Explainable anomaly detection (show the signals, locations and time periods that contributed) | The card says "descriptive context, not model attributions". There is no anomaly or deviation-from-baseline view, and the ablation page shows DEMO. The UAE model is linear, so exact additive attributions are free and simply not computed. There is no location dimension in the UAE and no state-contribution view in the US. | **CRITICAL** |
| 3 | Actionable decision support (proportionate action, named role, evidence and assumptions shown) | Roles are named. But the band logic is level-only and contradicts the forecast (`rsv_rising` fires on a falling median). There is no exceedance probability, the card shows no assumptions or evidence, the thresholds are illustrative, and the playbook is unreviewed. | **MAJOR** |
| 4 | Privacy-preserving views (aggregation, small-cell suppression, RBAC, no employment/disciplinary use) | Aggregation is in place, and small-cell suppression exists on the simulated workforce page. There is **no RBAC view**. The no-disciplinary-use statement is on a slide but not in the app. | **MINOR** |
| 5 | Operational validation (lead time, sensitivity, PPV, false alarms, latency, missing inputs) | The US part is done. But median lead is **0 weeks** for all rules, NABD's sensitivity is below the census, and the UAE alert metrics are not done (G10 UAE part open). Missing inputs cause 1.41–1.82-fold WIS degradation with no fallback feed. | **MAJOR** |
| 6 | Health and resilience impact (earlier intervention, fewer severe incidents, less sickness absence and fewer lost workdays) | No quantified impact (bed-days, cost, absence). The workforce half of the statement *title* is simulated and **disconnected** from the forecasts: absence is not predicted from positivity or linked to the card. | **MAJOR** |
| Core | "Early enough to change action" | Median lead is 0 weeks, and the horizons sit on a 7–11-day lag. | **MAJOR** |
| Core | "Specific enough to be useful" | National positivity only; the +1-week 80% band spans 4.6–21.4%; no emirate or district view. | **MAJOR** |
| Core | "Calibrated to avoid alert fatigue" | **A strength:** PPV 0.71, 0 false-alarm location-seasons, 95% coverage 0.92 (US) and 0.95–0.97 (UAE). Under-used in the pitch. | none (exploit it) |
| Core | Geolocation completeness | The UAE has no sub-national data. Stated, but not shown in the UI. | **MINOR** |
| Submission | Assumptions, dependencies and limitations statement; declare data sources | An About & limitations page exists. It needs a single LIMITATIONS.md that matches the code (fusion and ACI status), plus a data and licence declaration (WHO non-commercial). | **MINOR** |

---

## 5. Ranked top-10 fix list for the next build round

Score impacts are panel estimates on the 1–10 axes above. "+1 J2-evidence" means about one point on J2's Working demo & evidence score.

| Rank | Fix | Owner | Deadline | Expected impact |
|---|---|---|---|---|
| 1 | **Claims sweep before registration closes on 10 Nov.** Rewrite the registration abstracts, deck slides 3–4, demo script, Q&A #4/#8/#11 and SPEC §1 so every claim matches the code: "US: admissions-only stress test. UAE v1: lab positivity + testing volume + seasonal baseline. Weather, calendar and ED are being added in v2." Label 21–36% as the CDC ensemble's. Remove ACI and "explains what drove each forecast" until Fixes 3 and 5 exist. Replace "RSV is climbing" with the W44 picture. Tick G9 only after a line-by-line trace. | pitch | **10 Nov** | Prevents the honesty premium collapsing: protects about 2 points on J2 tech/RAI and about 1 on every J1 axis. The registration text is irreversible. |
| 2 | **Independent timestamps.** Push the repo with full history today. Post the PROTOCOL and ledger SHA-256s to a third party (OSF registration or Zenodo DOI). Write the freeze as "self-attested locally 06:47Z; publicly posted ⟨date⟩". **Submit frozen v1 (+ the v2 pre-registration) to the FluSight hub for reference date 14 Nov** (due Wed 11 Nov 23:00 ET) after verifying the participation rules. Issue UAE ledger rounds publicly each week. | modelling + data-UAE | **11 Nov** | +1–2 J2-evidence; turns "discipline" from a claim into a fact; adds a CDC-scored forward record by 30 Nov. |
| 3 | **Real explainability (req 2).** For each UAE forecast, compute exact additive contributions from the linear model (momentum `dy1`, anomaly vs seasonal baseline `anom`, seasonal drift `dclim`, testing volume `dlogspec`, plus the v2 covariates). Show the `anom` term as the deviation-from-baseline anomaly score with week windows. Add a US state-contribution map for the national forecast. Replace "descriptive context". | app + modelling | 14 Nov | Closes a CRITICAL requirement; +1 J1-demo, +1 J2-tech; makes the demo's "Explain" beat real. |
| 4 | **At least one materially different real signal in a scored UAE model (req 1).** Fetch NOAA GHCN on a laptop; add the MoE school calendar as a known-future covariate and non-sentinel FluNet as a second clinical stream. Pre-register UAE-v2 (hash) before running LOSO. Produce real `ablation*.csv` so the Feed-removal page shows real Δs, including nulls. Keep v1 as the headline UAE number. | data-UAE + modelling | 15 Nov | Closes a CRITICAL requirement; +1 J1-impact, +1 J2-tech; the feed-dropout fallback becomes real. |
| 5 | **Pre-declared CDC-hub league table (D5).** Score every individual hub model on 2024/25–2025/26 with pairwise relative WIS on common cells, then place NABD v1 by season. Declare the method before cloning; report the rank whatever it is. | modelling | 13 Nov | Reframes NOT MET in the field's own terms. +1 J2-evidence if mid-pack or better; even a poor 2025/26 rank, shown openly, holds credibility. |
| 6 | **One Abu Dhabi clinical or operational champion.** A one-paragraph LOI or shadow-pilot interest letter from a SEHA, SSMC, CCAD or MBZUAI-affiliated clinician, plus a playbook review by one clinician or public-health officer. Add a pricing hypothesis (public-health feed licence per country; hospital-ops seat) and note the 6-month right of first refusal (ROFR). | pitch | 17 Nov | The largest single J3 lever: +2 commercial if obtained, +1 J1-commercial. Without it J3 stays at 3–4. |
| 7 | **External validation of the frozen NABD-UAE-v1** on GCC FluNet sentinel series and the cached US FluNet, under a hashed UAE-PROTOCOL (country list, sufficiency rule, criterion). Report season win counts per country. | modelling + data-UAE | 16 Nov | +1 J2-evidence, +1–2 scalability (all judges); "GCC-ready" becomes a measured claim. It could also fail, so report it either way. |
| 8 | **Rebuild the US proof page and deck slides 6–8** around Section 2: a NOT MET verdict banner at the top, a forest plot by season and horizon, the fan chart, an alert table (PPV, sensitivity, **lead = 0**). Remove the tuning tables and the raw JSON. Deck order: UAE proof → stress test → v2 and FluSight submission → ledger. | app + pitch | 18 Nov | +1 demo for all judges; NOT MET lands as credibility, not collapse. |
| 9 | **Decision logic and operational translation.** Drive the playbook bands by exceedance probability and direction (e.g. P(RSV > 15% within 2 weeks) ≥ 0.3 *and* a rising median) rather than level alone. Show the assumptions on the card. Add a clearly labelled **SCENARIO** translator from positivity to illustrative paediatric RSV bed-days for a Tawam-sized hospital (about 440 RSV admissions/yr, mean LOS 5.8 d, from burden.md). Link the simulated absence module to the forecast (expected respiratory absence per 1,000 staff), labelled SIMULATED. | app + pitch | 17 Nov | Fixes a demo-killing contradiction; +1 J1-impact/demo, +1 J3-impact; partly addresses req 6. |
| 10 | **Close the remaining validation items.** UAE alert metrics (req 5, descriptive, n=4) and a UAE feed-dropout test. Chronos-2 on a laptop or Colab as an S5 member (US) and zero-shot (UAE); any ensemble inclusion is a logged deviation. Add an RBAC demo (duty-officer vs bed-manager views). Write LIMITATIONS.md matching the code. | modelling + app | 19 Nov | Closes the MAJOR req 5 UAE gap and the MINOR req 4 gap; +0.5–1 J2-tech (the "where's the AI" question); limits downside at Q&A. |

**Expected merged effect** if fixes 1–5 and 8–9 land, and 6 lands too: the panel mean rises from about 5.3 to about 6.5–7. That is a credible finalist and a plausible top-3 contender. Without Fix 6 (an Abu Dhabi champion) the ceiling is about 6.3, because the commercial axis caps the J3 score.

**Do not spend time on:** re-tuning v1, stacking on the US test seasons, making E1 a headline, the wider BrainDrift contingency, or further workforce-simulation polish beyond linking it to the forecast.
