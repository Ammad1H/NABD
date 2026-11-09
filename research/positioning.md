# NABD: Why this matters to Abu Dhabi and Future Health (positioning, v1)

> **Status (9 Nov 2026, round 5).** This is the round-2 research note. Its *evidence* (§1–3) stands. Its *wording* (§0, §4, §6) is **superseded** by `pitch/registration.md` and BUILD-SPEC v1.7: say "timing and shape change from year to year" (not "no two seasons share a shape" / "never repeat"), "probabilistic, coverage reported" (not "calibrated"), "to our knowledge, no one publishes", "hashed before the outcome exists; to be externally timestamped" (not "published"), and never "fill Abu Dhabi's children's beds". Lines below are reworded where they would be quoted.


Owner: positioning workstream (BUILD-SPEC v1.4). Compiled 8 Nov 2026. This is the **single source** for the pain point and value story; pitch/ draws from here.

Labels used throughout:
- **VERIFIED**: read on the cited page in this pass or a logged earlier pass. URLs are in `research/positioning-sources.md`; IDs in [brackets] point to it.
- **[DATA]**: our own computation on WHO FluNet UAE sentinel data (`data/raw/flunet_are.csv`, weeks with ≥20 specimens).
- **SCENARIO**: illustrative arithmetic, never a claim.
- **UNVERIFIED**: not checked.

Quotes are kept under 15 words.

---

## 0. The pitch in one breath

Abu Dhabi already **detects**. Tableegh turns lab results into near-real-time notifications [S12]. UMOC runs an AI early-warning layer [S13]. Rasid watches wastewater [S20]. DoH scores every resident's chronic-disease risk [S14].

What nobody provides, publicly or with a checkable track record, is the answer to the question a paediatric ward lead and a public-health duty officer both face every week in winter: **how big will the next 1–3 weeks of RSV and flu be, and how sure are we?** That question is hard in the UAE for two reasons. Its seasons change timing and shape from year to year ([DATA] §1.1), and its case counts are not public [S6].

NABD is that forecast layer: probabilistic (coverage reported), bilingual, human-approved, and scored on a hashed record that is to be externally timestamped. The US stress test shows we hold it to the hardest public bar there is.

---

## 1. The pain, quantified (VERIFIED unless marked)

### 1.1 No two UAE seasons look alike [DATA, WHO FluNet UAE sentinel]

| Season | Flu peak (positivity, ISO week) | Flu weeks ≥20% (span) | RSV peak (positivity, week) | First week RSV ≥10% |
|---|---|---|---|---|
| 2022/23 | 35.6%, wk 45 | 8 (wk 27→47) | 20.4%, wk 42 | wk 35 |
| 2023/24 | 27.3%, wk 45 | 8 (wk 41→48) | 24.5%, wk 41 | wk 38 |
| 2024/25 | 28.0%, **wk 7 (Feb)** | **11 (Nov→Mar)** | **29.8%**, wk 41 | **wk 30** |
| 2025/26 | **40.6%, wk 42** | 9 (wk 39→47) | 23.1%, **wk 47** | wk 42 |
| 2026/27 (to wk 44) | 40.1%, wk 40 (so far) | 10 (wk 35→44, ongoing) | 15.6%, wk 43 (so far) | wk 42 |

**What it means:**
- **Flu changes shape completely from year to year.** In 2024/25 it ran as a five-month plateau at about 20–28% that peaked in February. In 2025/26 it was a sharp October spike above 40%.
- **RSV moves too.** Its peak landed between wk 41 and wk 47, and its first ≥10% week ranged from late July (wk 30) to mid-October (wk 42).
- **A planner using "last year" as the template would have been wrong in both timing and size.** This is the core pain. It is shown with Abu Dhabi's own published lab data, not with anecdote.

**Caveat:** this is sentinel positivity (share of tests positive), not admissions. Testing volume changes too; NABD uses it as a covariate.

### 1.2 The burden behind the curve (Abu Dhabi emirate first)

1. **Tawam Hospital, Al Ain (SEHA), 2018–22** [S1]:
   - **2,189 RSV hospitalisations** of children aged ≤5 at one hospital in five years.
   - Infants under 6 months had the longest stays (mean **5.8 days**).
   - Annual positivity swung **2.9% → 16%**.
   - Derived: about 440 admissions a year on average, but highly uneven across years.
   - Tawam is a SEHA facility (domain tawam.seha.ae [S1b]).
2. **Paediatric influenza at Tawam, 2012–17** [S2]:
   - Among 1,392 children with lab-confirmed flu, **33.5% were admitted** and **8% went to PICU**.
   - Only about 10% had been vaccinated.
   - Older data; say so.
3. **Dubai paediatric RSV, insurance claims 2014–23** [S3]:
   - **22% of under-2s with RSV were hospitalised**, and **fewer than 2% had a known risk factor**. Burden is population-wide; you cannot pick the at-risk children from a list.
   - Median hospitalisation cost **US$2,241**; total for under-2s **US$9.8M**.
4. **Influenza cost, Dubai insured adults with comorbidities** [S15]:
   - Modelled 5-year management cost of **AED 1.26 billion** without vaccination.
   - Scope is narrow (one insured cohort, modelled), so use it only as an order-of-magnitude cost signal.

### 1.3 The 2025/26 season, as clinicians described it
- **Burjeel Medical City, Abu Dhabi:** flu-like outpatient visits were "among the highest since tracking began". 2025 could be "one of the worst seasons in over a decade" (consultant, The National, Jan 2026 [S6]).
- **Same article:** "exact data for flu cases in the UAE is not available" [S6]. **This is the information gap.**
- **After winter break (Jan 2025):** paediatricians reported children with fever and cough had **doubled** versus pre-holiday [S9]. Anecdotal, from clinics; use as colour, not data.
- **After school reopening on 31 Aug 2026:** paediatricians described a resurgence about two weeks after return. Flu vaccines arrived **later than in the previous two seasons** [S10].
  - Meanwhile 2026/27 flu positivity was already ≥20% from wk 35 [DATA].
  - **The vaccine-timing mismatch this season is visible in the data.**
- **Dubai, Dec 2025:** a "significant increase" in visits after the National Day holidays, attributed to gatherings and travel; respiratory illness was the main driver [S11].

### 1.4 Prevention is scaling, and the season still varies
- **Flu campaign:** ADPHC vaccinated **350,000+** in 2025/26, up from 162,761 in 2022/23 [S5].
- **Campaign scope:** the 2026/27 national campaign now covers **flu + RSV + pneumonia** [S7].
- **DoH view of this season:** Dr Mahra Alhosani (DoH Director of Surveillance and Outbreak Response) said activity so far is "similar to the previous two seasons" [S7].
  - **Pitch implication:** sell *recurring variability*, not a crisis.
- **Infant RSV antibodies:** nirsevimab and clesrovimab were added to Abu Dhabi's childhood programme (DoH Circular 37/2026); the season window is **1 Sep–1 Mar** [S4, secondary source; the primary PDF could not be fetched].
- **[DATA] RSV vs the window:** RSV positivity first reached ≥10% **before 1 Sep (≈ wk 35) in 2 of 4 complete seasons** (wk 30 in 2024, wk 35 in 2022).
  - A calendar window and a moving epidemic are not the same thing.
  - This is policy evidence, **not** a claim that NABD predicts onset (§4.5).

### 1.5 Scale and exposure
- **Population:** Abu Dhabi reached **4.14 million** at end-2024 (+7.5% in a year); the workforce grew 9.1% to 2.76 million [S16].
  - A fast-growing, mobile population changes the denominator every season.
- **Travel:** Dubai International handled a record **95.2 million** passengers in 2025 [S17]. Doctors link travel to imported flu waves, including off-season southern-hemisphere flu in July 2025 [S18].
- **Regionally (Saudi Arabia, Oct 2026):** the Saudi ministry reported a **30% rise in ICU admissions** linked to seasonal respiratory infections over three weeks, "within expected seasonal levels" [S19].

### 1.6 Workforce and schools (Statement 06's "workforce" half)
- **Schools:** UAE school winter break runs **14 Dec 2026 – 3 Jan 2027**; classes resume 4 Jan [S8]. Paediatricians repeatedly link post-break returns to case rises [S9][S10].
  - **This is a known-future covariate NABD can use honestly.**
- **Workforce absence:** no current, credible UAE figure for respiratory sickness absence was found.
  - The only hit, a 2021 Bayzat payroll analysis of Dubai employees (20→23 sick days a year), is COVID-era and not respiratory-specific [S21]. **Do not use it.**
  - The workforce module stays SIMULATED and labelled as such.

### 1.7 Not found (state honestly)
- Abu Dhabi ED winter volumes, paediatric bed occupancy, or SEHA surge numbers. The DoH open-data dashboards carry beds per 1,000 but no seasonal series [S22].
- A UAE national influenza hospitalisation estimate.
- Any public respiratory **forecast** for the UAE or GCC: none found in this or earlier passes ([S6], competitors.md).
  - The Gulf CDC's regional system is at the pilot stage, with ARI as a weekly-reported pilot disease.
  - Its experts flag timeliness, data quality and standardisation as concerns [S23].

---

## 2. Who feels it, and what they decide every week

| Stakeholder | Weekly decision in season | Timing | What they use today | Cost of being wrong |
|---|---|---|---|---|
| **DoH / ADPHC** (surveillance and outbreak response; UMOC) | Escalate advisories and campaign messaging; brief providers; decide whether this season is "as expected" | Weekly; the duty officer every day | Tableegh notifications (Malaffi-integrated) [S12]; UMOC AI early warning [S13]; WHO FluNet reporting; clinician signals | Advisories too late (after the surge) or too often (alert fatigue); no calibrated "how big" to brief hospitals with |
| **SEHA / PureHealth hospital operations** (paediatric ED, wards, PICU) | Surge roster, bed opening, elective deferral, agency staff, isolation capacity for the next 1–3 weeks | Weekly roster cycle; 1–3 weeks ahead | Own census (looks back); short-horizon ops tools, e.g. the 72-hour command-centre class (GE CareIntellect, competitors.md) | Over-staffing at the turn of the wave, or corridor care and boarding at the peak. Paediatric RSV stays are 4–6 days [S1][S3], so beds stay occupied for days after admission |
| **Immunisation programme** (DoH/ADPHC: flu campaign, infant RSV antibodies, maternal RSV) | Push or extend campaigns; catch-up messaging; stock allocation | Pre-season and monthly | Fixed calendar window (1 Sep–1 Mar) [S4]; vaccine arrival dates [S10] | Protection that arrives after RSV is already ≥10% (2 of 4 seasons, [DATA]) |
| **M42 / Rasid** (wastewater, G42 Healthcare) | Interpret wastewater signals | Weekly | Wastewater AI early warning [S20] | A signal without a calibrated clinical-load translation. Partner, not rival: offered as an NABD covariate |
| **Private groups** (Cleveland Clinic AD, NMC, Burjeel, Mediclinic) | Same as SEHA ops, plus outpatient and urgent-care staffing | Weekly | Own data only | As SEHA. Burjeel AD reported record outpatient flu-like visits in 2025/26 [S6] |
| **Insurers** (Daman, Thiqa coverage) | Seasonal claims reserving; vaccine coverage | Monthly | Claims history | Mis-reserved seasonal claims. Dubai under-2 RSV admissions alone cost US$9.8M over the study period [S3] |
| **Schools / ADEK; employers** | Infection-control messaging; exclusion reminders; staffing cover | Weekly in season; around breaks | Illness-exclusion policies (ADEK) [S24] | Outbreaks after breaks. Absence costs are unquantified in the UAE (§1.6) |

**Top 3 for the pitch:** (1) SEHA/PureHealth paediatric operations; (2) ADPHC/DoH surveillance and UMOC; (3) the immunisation programme.

---

## 3. Why now, why Abu Dhabi

1. **The theme.** "To Sense is to Predict" (Future Health, 16 Mar 2026) frames the shift as **reactive → proactive**. It includes **population-level sensing** of "biological markers, community behaviours, and environmental conditions" [S25]. Its impact areas include **Health System Resilience**.
   - The release mentions no respiratory or outbreak use case, and the Oct 2026 summit coverage was dominated by genomics and chronic disease [S26][S27]. **The theme is open for infectious-disease forecasting.**
2. **Abu Dhabi has already built the sensing layer:**
   - Malaffi-linked **Tableegh** turns ICD-10 codes and lab results into near-real-time notifications for "early detection of outbreaks" [S12].
   - **UMOC** (Feb 2025) runs an AI early-warning system that "predicts potential outbreaks" [S13].
   - **Rasid** handles wastewater [S20].
   - The **DoH patient risk profile** covers 14 chronic diseases for all residents [S14].
   - **The missing link** is a *probabilistic, evaluated, operational forecast of seasonal load* that sits between detection and the bed manager.
3. **Policy is moving to seasons and climate:**
   - The national campaign expanded to RSV + pneumonia [S7].
   - Infant RSV antibodies are in the Abu Dhabi programme [S4].
   - MoHAP's **Health Sector Climate Adaptation Plan 2026–2031** (announced at the Future Health Summit, Oct 2026) names respiratory disease and dust, and commits to early-warning systems that combine health and environmental data [S28].
4. **Trust is the open question.**
   - Health Policy Watch's summit coverage asked who owns the data and who is left out. It noted that nearly nine in ten UAE residents are foreign nationals [S27].
   - An open protocol, aggregate-only data and a public track record directly answer that critique.
5. **Abu Dhabi has a regional opportunity.**
   - The Gulf CDC is building unified surveillance and lists ARI as a pilot disease, but timeliness and standardisation remain open [S23].
   - A FluNet-native forecasting method that is shown to transfer across GCC countries (G12) fits the region's own trajectory, with Abu Dhabi as the hub.

---

## 4. Positioning

### 4.1 Problem statement (chosen, 40 words)
> **Every winter, RSV and flu drive paediatric admissions in Abu Dhabi, and their timing and shape change from year to year: flu peaked in October one year and plateaued for five months the next. To our knowledge, no one publishes a forecast of how big or how long.** *(Reworded in round 5; the original wording is retired.)*

**Alternatives, ranked:**
1. *(Detection-gap framing)* "Abu Dhabi can already see an outbreak start. It still cannot see how big the next three weeks will be. Hospitals plan winter from last year's calendar, and the UAE's seasons change timing and shape from year to year." (Strong for the DoH judge. It risks sounding like a knock on Tableegh/UMOC, so pair it with "built to plug into them".)
2. *(Trust framing)* "Health AI in the Gulf asks for trust it hasn't earned. NABD publishes every forecast before the outcome exists, so Abu Dhabi can check us, week by week." (Strong for the AI judge, weaker on impact. Use as the closing line, not the opener.)
3. *(Prevention-timing framing)* "Abu Dhabi now protects infants against RSV from 1 September. In two of the last four seasons RSV was already circulating before then." (Sharp and true [DATA]. It invites the question "can you predict onset?", and our honest answer is no better than the census. Keep it as a slide-2 fact, not the headline.)

### 4.2 Value proposition for the top 3 stakeholders
- **SEHA/PureHealth paediatric ops:** "Each Monday you get the probability that RSV/flu pressure exceeds your surge threshold in each of the next three weeks, with a reason code and a named-approver workflow. Shadow-pilot it on your own aggregate counts for 12 weeks. The exit test is whether it beats your census carried forward."
- **ADPHC/DoH (surveillance, UMOC):** "A probabilistic forecast feed (coverage reported) for Tableegh/Malaffi-derived counts, with a pre-registered evaluation protocol and a public ledger. It can be audited in the same way regardless of which vendor platform hosts it."
- **Immunisation programme:** "A season-shape evidence base (onset, peak and duration, by year) and a live view of where this season sits against them. Use it for catch-up and messaging timing."

### 4.3 The "only we" claim (defensible)
> **"To our knowledge, NABD is the first open respiratory forecast for the UAE. It is probabilistic (coverage reported) and bilingual, and every forecast is hashed before the outcome exists (to be externally timestamped). It is held to the same test the US CDC applies to its own forecasting hub."**

"To our knowledge" is required: we searched (§1.7) and found none. Never say "the only" without that qualifier.

### 4.4 Moat (honest)
1. **A dated track record.** Every week the public ledger grows, and a copycat cannot backdate it. It must be anchored outside the team (OSF/Zenodo/OpenTimestamps) to count.
2. **Open protocol and vintage-correct evaluation harness.** This is reusable for any FluNet country, and it is the procurement-grade evidence a regulator needs. DoH's AI regulations bind any company using Abu Dhabi population data in AI [S29].
3. **GCC generalisation (G12, pending).** A frozen method tested on GCC countries nobody on the team has looked at. If it holds, "Gulf hub" becomes a measured claim; if it fails, we report that.
4. **Deployment fit.** The model consumes the same shape of data Tableegh already produces (lab-confirmed counts by week, optionally by age band or district). The pilot needs a data-sharing agreement, not new sensing.
5. **MBZUAI link.** Local ML capacity for model upkeep, Arabic-first UI, in-country hosting.

### 4.5 Reframing the US NOT MET inside the story
> "There is no forecasting hub in the UAE to compare against, so we went to the hardest public bar in the world: the US CDC's FluSight ensemble of about 40 models, using only the data each forecaster had in real time. We froze the test before running it. NABD v1 missed our margin: 1.22 relative error, 95% CI 1.01–1.52. We publish exactly where it failed, which is why our UAE numbers can be trusted."

Placement: after the UAE proof and before the forward plan (deck slide 7), per the judges' review. **Never** lead with it, hide it, or quote E1 as a rescue.

### 4.6 What NOT to claim (stop list)
- **Do not say "early warning of onset".**
  - Median onset lead is 0 weeks for every rule, including the CDC's (results/).
  - Say "how big and how long", and "fewer false alarms" (PPV), only as far as results/ supports it.
- **Do not cite "21–36% less error than the census" as ours.** That figure is the CDC ensemble's gain over persistence.
  - NABD's US figure is 0.816 (CI 0.655–1.023) and is not significant.
- **Do not claim fusion of ED, weather or geospatial signals** in any scored model until UAE v2 is scored.
  - The US model is admissions-only.
  - Weather is not retrieved unless the data agent confirms it.
- **Do not claim ACI, the foundation model or per-forecast attributions** until they are built and scored.
- **Do not say "RSV is climbing".** Week 44 dropped to 10.5% (first release, possibly incomplete); always cite the current week.
- **Do not frame this season as a crisis.** DoH says it is similar to the last two [S7].
- **Do not claim SEHA operational numbers, ED volumes or bed occupancy.** None are public.
- **Do not use workforce-absence figures.** None are credible; the module stays SIMULATED.
- **Do not imply Tableegh or UMOC are inadequate.** Say "NABD adds the forecast layer they can host".
- **Do not claim NABD predicts the nirsevimab window.** The RSV-vs-window fact is [DATA] context only.
- **Do not cite the DoH circular as read first-hand.** Say "as summarised by [S4]".

---

## 5. Solution improvements implied by the pain (ranked by judge impact ÷ effort)

| Rank | Improvement | Why the pain demands it | Owner | Effort |
|---|---|---|---|---|
| 1 | **Exceedance probability + direction on the card.** "P(RSV positivity > tier threshold in wk +1/+2/+3)" plus a trend arrow from the forecast median. Drive playbook bands from both. | Turns a wide band (4.6–21.4%) into a decision. Fixes the "rsv_rising on a falling forecast" contradiction. Answers req 3 | app + modelling | Low (quantiles → CDF; the kit has `exceedance_prob`) |
| 2 | **Season-shape panel:** "this season vs the last 4". Onset week, peak week, peak height and weeks above threshold for flu and RSV (table §1.1), with the live forecast overlaid. | Makes the core pain visible in 5 seconds using Abu Dhabi's own data. Supports the immunisation-programme value proposition | app (reads data/raw) | Low |
| 3 | **Tableegh/Malaffi-ready data contract + pilot data spec.** A one-page `docs/PILOT-DATA-SPEC.md`: weekly lab-confirmed flu/RSV counts by age band (0–1, 1–4, 5–14, 15–64, 65+) and optionally district, from Tableegh. Small-cell suppression (k≥10). An adapter stub, plus a synthetic demo labelled SIMULATED. | Shows the deployment path into DoH's existing systems: "no new sensing, one data-sharing agreement". Answers req 4 (privacy) and the J3 buyer question | data-UAE + pitch | Low–medium |
| 4 | **Paediatric bed-days SCENARIO translator** for a Tawam-sized hospital. Inputs from verified figures: about 440 RSV admissions/yr average [S1], LOS 4–6 days [S1][S3], median cost US$2,241 [S3]. It maps forecast quantiles into an illustrative "bed-days at stake" band, permanently labelled SCENARIO. | Prices the pain for the PureHealth/M42 judge (Commercial was 4.0). Partially addresses req 6 | app + pitch | Low |
| 5 | **GCC out-of-sample panel (G12)**, already in plan. | Turns n=4 into n=4×K and makes "Gulf hub" measurable. Fits the Gulf CDC trajectory [S23] | data-UAE + app | Medium |
| 6 | **Arabic/English weekly bulletin (PDF)** auto-generated from the card for the ADPHC duty officer: forecast, exceedance probabilities, season-shape context, data freshness, approved action, audit hash. | A tangible artefact a DoH judge can picture landing in their inbox on Monday. Bilingual by default | app | Low–medium |
| 7 | **School-calendar covariate + post-break flag.** Winter break 14 Dec–3 Jan, resume 4 Jan [S8]; reopening 31 Aug. Known-future only. | Clinicians report post-break rises [S9][S10]. An honest, verifiable driver for req 1 (an administrative signal) | data-UAE (UAE v2) | Low, but only if PROTOCOL-UAE-v2 is not yet frozen; otherwise list it for v3 |
| 8 | **Immunisation-timing context view.** RSV first-≥10% week by season vs the 1 Sep window, and flu ≥20% onset vs reported vaccine arrival. Labelled "context, not a prediction". | Gives the programme an evidence base and matches "health-focused prevention" [S25]. Must not be dressed up as onset prediction | app | Low |
| 9 | **Dust/air-quality covariate (v3).** | Hooks to MoHAP's climate adaptation plan [S28]. Data access is likely blocked here, so declare it as roadmap only | data-UAE | Medium–high; roadmap |

---

## 6. Ready-to-use text

### 6.1 Spoken "why it matters" opener (about 90 seconds, about 210 words)
> "Every winter, two viruses, RSV and influenza, arrive in Abu Dhabi's children's wards together. At one Abu Dhabi hospital, Tawam, RSV alone put more than two thousand young children in hospital in five years. The youngest stayed nearly six days each.
>
> Here's the problem. No two UAE seasons look alike. In WHO's own UAE lab data, flu spiked above forty per cent positivity in October one year. The year before, it crawled along for five months and peaked in February. RSV has peaked anywhere from mid-October to late November. If you plan this winter from last winter's calendar, you're wrong on timing *and* size.
>
> Abu Dhabi already senses brilliantly. Tableegh flags notifiable cases in near-real time, and UMOC watches for outbreaks. But nobody, publicly, answers the question a ward lead asks every Monday: how big will the next three weeks be, and how sure are you?
>
> NABD answers that. It produces probabilistic RSV and flu forecasts in Arabic and English, every action is approved by a named officer, and every forecast is hashed *before* the outcome exists. We tested ourselves against the hardest public benchmark in the world, the US CDC's forecasting hub, and we'll show you exactly where we fell short.
>
> To sense is to predict. NABD is how Abu Dhabi checks the prediction."

*(Facts: [S1], [DATA] §1.1, [S12], [S13]. "Brilliantly" is rhetorical; keep or drop it.)*

### 6.2 One-paragraph executive summary (registration / solution description, 119 words)
> Every winter RSV and influenza strain Abu Dhabi's paediatric services, and their timing and shape change from year to year. In WHO's UAE laboratory data, flu peaked above 40% positivity in October one year and plateaued for five months into February the year before, and the UAE publishes no forecast of either. NABD is an open, bilingual forecasting layer that turns surveillance data into probabilistic 1–3-week forecasts of RSV and flu activity, with a named-officer approval workflow and a hashed track record (to be externally timestamped). It is built to sit on the sensing Abu Dhabi already has (Tableegh/Malaffi, UMOC, Rasid) rather than replace it. Its evaluation is pre-registered and held to the US CDC FluSight standard, with results reported in full, including where it falls short.

*(The pitch workstream must reconcile this with the CLAIM RULE and the abstract word limits. "1–3-week" should be read as issue-relative horizons up to +2.5 weeks (UAE).)*

---

## 7. Open items for other workstreams
- **app:** implement ranks 1, 2, 4, 6, 8 of §5; fix the contradictory band.
- **data-UAE:** rank 3 (pilot data spec + adapter stub); rank 7 only if PROTOCOL-UAE-v2 is not yet frozen; G12.
- **pitch:** adopt §4.1, §4.3, §4.5 and §4.6 verbatim; use §6.1 for the video opener; reconcile §6.2 with registration word counts.
- **Team (user):** open DoH Circular 37/2026 in a browser to confirm nirsevimab eligibility and the window first-hand; seek one SEHA/SSMC/CCAD clinician letter (the J3 lever).
