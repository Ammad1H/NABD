# NABD: Abu Dhabi impact case (independent reviewer, 9 Nov 2026)

**Purpose.** This note sets out a defensible, conservatively quantified answer to one question: *what changes if NABD runs for one winter season in Abu Dhabi?* It also tests the pain-point framing and maps stakeholder pull. The reviewer did not build NABD.

**Tags**
- **VERIFIED (URL)**: read at the URL in this pass (9 Nov 2026), or in the team's logged 8 Nov pass where marked "(repo pass)".
- **VERIFIED (repo: path)**: reproducible from a committed repo file.
- **DERIVED**: arithmetic on VERIFIED inputs, shown inline.
- **ASSUMPTION / UNVERIFIED**: not sourced.

For claim purposes, DERIVED and ASSUMPTION both count as **UNVERIFIED**. Quotes are kept under 15 words.

---

## 0. Bottom line

- **Per Tawam-sized paediatric hospital, one RSV season:** about **0 to 375 RSV bed-days of planning mismatch avoided**, central **about 85**. That is:
  - **0 to about 190 nurse shifts** better matched, central about 40;
  - plus **about 5 to 55 bed-days** for paediatric influenza.
- **The lower bound is zero.** NABD's UAE forward-in-time error reductions have CIs that touch or cross zero.
- **Emirate-wide:** about **0 to 2,250 RSV bed-days** under an *unverified* 3–6× hospital multiplier.
- **Earlier onset warning: none claimable.** Median onset lead is 0 weeks.
- **Sickness absence avoided: not knowable** from public data.
- The value that is *robustly* supported is narrower but real. **Planning from last year's pattern mis-sizes in-season RSV by about 40% at 2–3 weeks ahead.** A forecast that cuts that error by 13–25% (UAE, exploratory) to 46% (GCC, locked test, all weeks) is worth a 12-week shadow pilot to convert positivity into beds.

---

## 1. Abu Dhabi context (2025–26 primary sources)

### 1.1 Strategy, AI policy, initiative goals
| Fact | Tag |
|---|---|
| Future Health 2026 theme is "To Sense is to Predict"; the shift framed is reactive to proactive | VERIFIED (repo pass): https://www.doh.gov.ae/en/news/a-global-initiative-by-abu-dhabi-reveals-2026-theme-as-to-sense-is-to-predict |
| Challenge launched 15 Oct 2026. Curated by DoH; founding partners PureHealth, M42, Institute for Healthier Living AD, Mubadala Bio; co-creators MBZUAI, Inception42, Microsoft. Population Health focus area: "help identify emerging health risks" | VERIFIED: https://www.uniindia.com/business-wire-india/future-health-launches-global-challenge-to-move-health-innovation-towards-real-world-application-102/214940 |
| DoH Undersecretary Dr Noura Al Ghaithi: "turn that intelligence into action that improves people's health" | VERIFIED (same URL) |
| DoH AI governance: Policy on AI in Healthcare (30 Apr 2018) and a **Responsible AI Standard (2025)** with transparency and explainability requirements; regular audits reported to DoH | VERIFIED: https://www.ibanet.org/ai-healthcare-regulation-uae (article 11 May 2026) |
| DoH–Microsoft Population Health Intelligence platform: initial focus obesity and cancer; infectious disease not mentioned | VERIFIED (sponsored advertorial, 16 Oct 2026): https://www.thenationalnews.com/advertorial/2026/10/16/prevention-becomes-predictive-how-abu-dhabi-is-learning-to-read-health-risks-before-symptoms-appear/ |

### 1.2 Surveillance and data flows
| Fact | Tag |
|---|---|
| **Tableegh**: "automated digital disease notification platform" working with **Malaffi**. Uses ICD-10 codes and lab-confirmed results; notifications "generated in real time"; "flags unusual patterns or spikes" | VERIFIED: https://www.doh.gov.ae/en/programs-initiatives/PHP |
| **UMOC**: "early warning system that predicts potential outbreaks and diseases" from current alerts and historical data. No mention of bed or capacity management | VERIFIED (25 Feb 2025): https://www.doh.gov.ae/en/news/khaled-bin-mohamed-reviews-umoc-ecosystem-in-ad |
| ADPHC **National Influenza Surveillance Programme** collects and sequences samples to identify strains (Dr Faisal Al Ahbabi, Exec. Director, Communicable Diseases Sector). Free flu vaccine at 130+ facilities until Mar 2026 | VERIFIED (3 Nov 2025): https://en.aletihad.ae/amp/news/uae/4618613/free-flu-vaccine-available-at-over-130-abu-dhabi-health-faci |
| ADPHC 2025/26 campaign: **350,000+ vaccinated** (162,761 in 2022/23). Early-season flu admissions mostly among unvaccinated people (no counts). "ADPHC is monitoring early-season data" | VERIFIED (19 Jan 2026): https://www.mediaoffice.abudhabi/en/health/abu-dhabi-public-health-centre-vaccinates-350000-plus-people-as-part-of-2025-2026-annual-seasonal-influenza-campaign/ |
| DoH published emirate influenza notifications historically: **15,994 (2017) vs 6,774 (2016)**, a 2.4× year-to-year swing | VERIFIED: https://doh.gov.ae/-/media/Feature/Resources/AbuDhabiHealthStatistics.ashx |
| No current public weekly UAE flu case data ("exact data for flu cases in the UAE is not available") | VERIFIED (repo pass, 14 Jan 2026): https://www.thenationalnews.com/news/uae/2026/01/14/uae-influenza-season-flu-shot-preventive-tips |
| 2026/27 national campaign covers flu + RSV + pneumonia. DoH Surveillance and Outbreak Response (Dr Mahra Alhosani): activity "similar to the previous two seasons". Seasonal respiratory illness generally runs Sep–Mar | VERIFIED (16 Sep 2026): https://www.khaleejtimes.com/lifestyle/health/flu-campaign-2026-27-expanded-changes-explained |
| Public statement of a *forecasting need* (size or duration of the season) by DoH, ADPHC or SEHA | **NOT FOUND.** The closest is UMOC's outbreak *prediction* and Al Ghaithi's "intelligence into action". Do not claim a stated need |

### 1.3 RSV immunisation
| Fact | Tag |
|---|---|
| DoH Circular 37/2026 adds **nirsevimab and clesrovimab** to Abu Dhabi's childhood programme; one dose per season; window **1 Sep–1 Mar**; "starting with 2025-2026" | VERIFIED (secondary only, 3 Oct 2026): https://www.zavis.ai/intelligence/uae-respiratory-vaccine-season-2026. Primary PDF blocked by robots.txt: https://www.doh.gov.ae/-/media/Feature/Resources/Circulars/2026/37--2026.ashx (**UNVERIFIED first-hand**) |
| AD eligibility (as summarised): infants **born in the RSV season** whose mother was not vaccinated, was vaccinated <14 days before birth, or has unknown status; high-risk 8–19-month-olds in their second season get nirsevimab | VERIFIED (secondary, Sanofi Campus, Jul 2026): https://pro.campus.sanofi/ae/respiratory-syncytial-virus/articles/rsv-prevention-guidelines-in-uae |
| HARMONIE trial: nirsevimab cut RSV hospital admissions by **83%** vs standard care (>8,000 infants) | VERIFIED: https://research.uhs.nhs.uk/news/baby-rsv-hospitalisations-fall-by-83-percent-in-trial |
| Abu Dhabi nirsevimab **coverage achieved** in 2025/26 | **NOT FOUND / UNVERIFIED** |

### 1.4 Capacity
| Fact | Tag |
|---|---|
| PureHealth UAE: **24 hospitals, about 5,000 licensed beds, 28,000+ UAE employees**; group 250K inpatient volume (+22%); "predictive workforce planning" listed (p. 44) | VERIFIED: https://purehealth.ae/wp-content/uploads/2026/03/PureHealth_Integrated-Annual-Report_2025_EN.pdf |
| Emirate **paediatric beds (2016 baseline, DoH capacity plan):** 1,186 of 3,452 acute overnight beds (34%); **55 PICU**; 338 NICU. **70%** occupancy is the planning norm | VERIFIED (2018 document; old): https://www.doh.gov.ae/-/media/Files/Investors/160823-New-Capacity-PlanShare.ashx |
| Current (2025–26) emirate paediatric bed count | **NOT FOUND** |
| Planned additions: SKMC Centre of Excellence (100 long-term paediatric beds) and the new women's and newborns' hospital (90 children's beds, opening 2027) | VERIFIED (11 Jan 2024): https://www.mediaoffice.abudhabi/en/health/khaled-bin-mohamed-bin-zayed-approves-establishment-of-medical-city-in-abu-dhabi-dedicated-to-women-and-childrens-health/ |
| Average length of stay (2017): Tawam 5.6 d; SKMC 8.9 d; Corniche 4.1 d | VERIFIED: https://doh.gov.ae/-/media/Feature/Resources/AbuDhabiHealthStatistics.ashx |
| Abu Dhabi population **4,135,985** (end-2024, +7.5%) | VERIFIED: https://scad.gov.ae/w/abu-dhabi-population-in-2024-grows-7-5-to-reach-4-14m. Workforce figure conflicts with the repo (3.4M vs 2.76M); **UNVERIFIED**, re-check before quoting |
| Abu Dhabi ED winter volumes, paediatric occupancy, SEHA surge figures | **NOT FOUND** (consistent with `research/burden.md`) |

### 1.5 Burden anchors
| Fact | Tag |
|---|---|
| Tawam (Al Ain), children ≤5, 2018–22: 15,326 children tested; **2,189 RSV-associated hospitalisations**, **60.2% in 2021–22**; infants <6 mo mean stay **5.8 d**; positivity 11%, 11%, 2.9%, 16%, 6.1% | VERIFIED: https://research.uaeu.ac.ae/en/publications/epidemiological-characterization-and-seasonality-of-respiratory-s/ |
| → about 438 admissions a year on average; about **290/yr in 2018–20** vs **about 659/yr in 2021–22** (a 2.3× swing) | DERIVED (2,189 × 0.398 / 3; 2,189 × 0.602 / 2) |
| Paediatric flu at Tawam 2012–17: 1,392 lab-confirmed; **33.5% admitted**; 8% PICU | VERIFIED (repo pass): https://pmc.ncbi.nlm.nih.gov/articles/PMC8596947 → about 78 flu admissions/yr, DERIVED |
| Dubai RSV claims: 22% of under-2s hospitalised; mean stay about 4 d; **median cost US$2,241** per hospitalisation | VERIFIED (repo pass, abstract): https://doaj.org/article/84cafb89b1744634800aad5def791c1d → about US$560 per bed-day, DERIVED (2,241 / 4) |

### 1.6 Season shape (WHO FluNet UAE sentinel, weeks with ≥20 specimens)
Recomputed by the reviewer from `data/raw/flunet_are.csv`; matches `research/positioning.md` §1.1. **VERIFIED (repo: data/raw/flunet_are.csv)**.

| Season | RSV first week ≥10% (Monday) | RSV weeks ≥10% | RSV peak (wk) | Flu peak (wk) |
|---|---|---|---|---|
| 2022/23 | wk 35 (29 Aug 2022) | 7 | 20.4% (41→42) | 35.6% (45) |
| 2023/24 | wk 38 (18 Sep 2023) | 9 | 24.5% (41) | 27.3% (45) |
| 2024/25 | **wk 30 (22 Jul 2024)** | **14** | 29.8% (41) | 28.0% (**wk 7, Feb**) |
| 2025/26 | **wk 42 (13 Oct 2025)** | 13 | 23.1% (47) | 40.6% (42) |
| 2026/27 (to wk 44) | wk 42 (12 Oct 2026) | 3 so far | 15.6% (43) | 40.1% (40) |

**What this shows:**
- **RSV duration doubled (7 → 14 weeks)**, and onset ranged across about 12 weeks.
- The RSV *peak* week is stable (wk 41–43 in 4 of 5 seasons).
- The 2026/27 flu peak nearly repeats 2025/26.

---

## 2. Mechanism: what NABD changes, and the evidence for each link

| Link | Evidence | Strength |
|---|---|---|
| (a) Planners need a 1–3-week view of RSV/flu load for rosters and beds | Plausible; LOS 4–6 d means admissions occupy beds for about a week. No public AD statement of the planning method | ASSUMPTION (to verify in conversations, §5) |
| (b) The default comparator is last year's pattern or last week | Not documented for SEHA | ASSUMPTION |
| (c) **How wrong last year's pattern is, in season, at 2–3 weeks ahead** | Forward-in-time UAE folds (2023/24–2025/26), horizons +2/+3 wk after last data, weeks with RSV ≥10% / flu ≥20%: seasonal-analog median absolute error = **38.9% of the observed level (RSV)** and **38.2% (flu)**. Persistence: 44.5% (RSV), 30.7% (flu). n = 70 RSV / 48 flu cells | VERIFIED (repo: `uae/backtest_v2.py` forward design; reviewer computation, POST HOC, reproduction in Appendix) |
| (d) How much NABD v1 cuts that error | Same cells; error reduction = 1 − (v1 error / comparator error). **Vs last year's pattern:** RSV **12.9% less error** (95% CI −0.3% to 26.8%, so the CI touches 0); flu **24.7% less** (8.4% to 36.9%). **Vs last week:** RSV 23.9% less (−3.5% to 44.0%); flu 6.2% less (−30.0% to 28.2%). All weeks, WIS: UAE v1 vs analog 0.824 flu / 0.855 RSV (CIs include 1 under the moving block); **GCC locked test v1 vs analog 0.536 (0.464–0.616)**; v1 vs persistence 0.914 (0.843–0.983) | VERIFIED (repo: results/uae/posthoc/SUMMARY.md, results/gcc/SUMMARY.md); in-season figures are reviewer POST HOC, date-cluster bootstrap over reference dates, B = 2,000 |
| (e) Positivity error maps proportionally to admissions and bed error | **Untested.** This is the biggest gap and is exactly the pilot's question. The nirsevimab rollout (83% efficacy among immunised infants) may change admissions per unit positivity from 2025/26 onward | ASSUMPTION |
| (f) Planners act on the forecast | Unknown; a shadow pilot does not test it | ASSUMPTION |

---

## 3. Estimate: one RSV season, one Tawam-sized paediatric hospital

**Model:** mismatch bed-days avoided = A × L × s × m × r. Every term is in the table.

| Term | Low | Central | High | Tag |
|---|---|---|---|---|
| A: RSV admissions ≤5 y per year | 290 | 438 | 659 | DERIVED from VERIFIED Tawam figures |
| L: mean LOS (days) | 4.0 | 4.5 | 5.8 | VERIFIED bounds (Dubai about 4; Tawam <6 mo 5.8); central is an ASSUMPTION |
| A × L: RSV bed-days per year | 1,160 | 1,970 | 3,822 | DERIVED |
| s: share of bed-days in weeks with RSV ≥10% | 0.7 | 0.8 | 0.9 | ASSUMPTION |
| m: in-season planning error with last year's pattern | 0.389 | 0.41 | 0.435 | VERIFIED (repo, reviewer POST HOC; all folds vs ≥2-training-season folds) |
| → bed-day mismatch per season under last year's pattern | 316 | 646 | 1,496 | DERIVED |
| r: NABD error reduction vs last year's pattern | **0** | 0.13 | 0.25 | Bounded by the CI in §2(d); high end ≈ flu point estimate and RSV upper CI; GCC 0.46 not used (all-week WIS, other countries) |
| **Mismatch bed-days avoided** | **0** | **≈ 85** | **≈ 375** | DERIVED |
| Average beds mis-sized avoided per in-season day (7–14 wk) | 0 | ≈ 1 | ≈ 4–8 | DERIVED |
| Nurse shifts better matched (1:4 ratio, 2 × 12 h shifts → 0.5 shifts per bed-day) | 0 | ≈ 40 | ≈ 190 | ratio is an ASSUMPTION (UNVERIFIED for AD) |
| Bed-day cost scale of the mismatch (US$560 per bed-day) | 0 | ≈ US$47k | ≈ US$210k | DERIVED. **This is not a cash saving.** It sizes the resource mis-planned; the realisable value (agency premiums, avoided boarding or cancelled electives) is unknown |
| Paediatric flu add-on (about 78 admissions/yr; LOS 3–5 d ASSUMPTION; r 0.08–0.37) | ≈ 5 | — | ≈ 55 bed-days | DERIVED/ASSUMPTION |

**Emirate-wide scaling (weakest row).**
- Tawam's share of emirate paediatric RSV admissions is **unknown**. The emirate had 1,186 paediatric acute beds in 2016, and Tawam's paediatric bed count is not public.
- Using **3–6 Tawam-equivalents (ASSUMPTION)** gives about **0 to 2,250 RSV bed-days**, central about 250–500, and about 0 to 1,100 nurse shifts.
- Present this as illustrative only.

**Other impact channels**

| Channel | What can be said |
|---|---|
| Earlier targeted messaging | **No onset-lead claim.** Median onset lead is 0 wk (US, diagnostic); the UAE alert table is retired. What NABD can support is *stand-down* and *escalate* calls on size, via exceedance probabilities. Value not quantifiable |
| Immunisation programme | In 2024/25, RSV was ≥10% from **22 Jul 2024**, about 6 weeks before the 1 Sep window. In 2022/23 the crossing week began 29 Aug (borderline). This is **policy evidence from the season-shape record, not from forecasting**. NABD's record does not predict onset |
| Staff sickness absence / lost workdays | **Not knowable.** No credible UAE respiratory-absence figure exists (repo §1.6); PureHealth's 28,000+ UAE staff is the only denominator. Only an HR aggregate in the pilot can measure it |
| Severe incidents (PICU, deaths) | Not estimable. Paediatric flu PICU rate 8% (Tawam 2012–17) is context only |

**What is not knowable before a pilot:**
1. The positivity → admissions → occupied-beds mapping at any AD hospital.
2. Current planning practice and its actual error.
3. Whether managers change rosters or beds on a forecast.
4. The 2025/26+ effect of nirsevimab on admissions. This is a **structural break** that makes last year's calendar *less* reliable, and it also requires NABD to be recalibrated on hospital counts.
5. Absence rates.
6. The cash value of a bed-day of mismatch.

---

## 4. Pain-point framing: tested against the evidence

| Candidate framing | Supporting evidence | Evidence against / risk | Verdict |
|---|---|---|---|
| **A. "Season timing and shape change from year to year"** (current) | Flu peak wk 45 → wk 7 (Feb) → wk 42; RSV duration 7–14 wk; DoH 2016→2017 flu notifications 2.4× | The RSV peak week is stable (wk 41–43 in 4/5 seasons); the 2026/27 flu almost repeats 2025/26; DoH says this season is "similar to the previous two". A DoH judge can rebut it from NABD's own bulletin (REVIEW-R4 J1) | Defensible but soft. It invites "seasons do repeat" |
| **B. "Abu Dhabi has detection but no forecast layer"** | Tableegh is detection; PHIF is chronic-focused; no public UAE respiratory forecast found | **UMOC's own DoH copy says it "predicts potential outbreaks"**; the ADPHC 2024 AI epidemic-prediction tender exists. It reads as a knock on DoH systems | Reject as the headline. Use only as positioning ("a scored forecast feed UMOC/Tableegh can host") |
| **C. "RSV immunisation window vs actual RSV onset"** | 2024/25 onset 22 Jul vs 1 Sep window; AD eligibility keyed to "born in the RSV season" | One clear season in four (2022 borderline); NABD cannot predict onset (0-wk lead), so it invites the wrong question; eligibility details are secondary-source only | Keep as a policy-evidence fact on the season-shape slide, not the headline |
| **D. "Paediatric surge planning is done on last year's calendar"** | The *cost* is measurable: in-season 2–3-wk error with last year's pattern ≈ **39–44%** of level (RSV); NABD's strongest evidence is against exactly this comparator (GCC 0.536 locked; UAE in-season 13% less error for RSV / 25% less for flu) | That SEHA *actually* plans this way is **unverified**. Stated as fact it is a claim about practice the team cannot source | **Best, if stated conditionally** and merged with the duration facts |

### Recommended single framing (merges D with the strongest facts from A)
> **"In Abu Dhabi the RSV season has run 7 weeks in one season and 14 in another, and started anywhere from late July to mid-October. Planned from last year's pattern, a 2–3-week-ahead estimate missed in-season RSV levels by about 40%. NABD is a scored forecast of how big and how long, built to cut that error."**

**Supporting facts:**
- RSV ≥10% duration 7/9/14/13 weeks, and first crossing wk 30–42 [VERIFIED repo data].
- Last year's pattern in-season error of 38.9–43.5% [reviewer POST HOC, repo].
- GCC locked test: 46% less error than past-season patterns, and 9% less than last week [results/gcc].
- Tawam: 2,189 RSV admissions, swinging 290–659 a year; LOS 5.8 d for infants under 6 months [VERIFIED].

**Guardrails:**
- Say "if planned from", not "is planned from", until a SEHA conversation confirms it.
- The 40% is positivity error, not bed error.
- Pair it with "vs last week, UAE parity", which the team already discloses.

---

## 5. Stakeholder pull

### 5.1 Likely champions (named roles are VERIFIED where a URL is given)
| Who | Why they'd champion it | Tag |
|---|---|---|
| **DoH Surveillance and Outbreak Response** (Director Dr Mahra Alhosani) | Briefs on whether the season is "as expected"; a scored size/duration forecast is a briefing tool | VERIFIED role: Khaleej Times 16 Sep 2026 (URL §1.2) |
| **ADPHC Communicable Diseases Sector** (Exec. Director Dr Faisal Al Ahbabi) | Runs the National Influenza Surveillance Programme and the campaign timing | VERIFIED role: Aletihad 3 Nov 2025 (URL §1.2) |
| **Tawam / UAEU paediatric infectious-disease authors** (senior author of the RSV seasonality study) | Own the AD RSV seasonality evidence; natural clinical reviewer for the playbook | VERIFIED authorship (repo burden.md; UAEU record URL §1.5) |
| **SEHA paediatric operations at SKMC and Tawam** (bed and roster managers) | The Monday decision owner; the 12-week shadow-pilot partner | Role exists; individuals UNVERIFIED |
| **PureHealth workforce planning** | Annual report lists "predictive workforce planning" (p. 44) | VERIFIED (URL §1.4) |
| **UMOC** | Already runs AI early warning; NABD is a scored feed it could host | VERIFIED (URL §1.2) |

### 5.2 The words a DoH or SEHA person would use
Use the system's own vocabulary:
- "early warning", "surge preparedness / capacity planning", "bed management", "rostering", "health system resilience";
- "turn intelligence into action" (Al Ghaithi, VERIFIED);
- "to sense is to predict" (theme, VERIFIED);
- "similar to the previous two seasons" (Alhosani, VERIFIED);
- "responsible AI / explainability / audit" (DoH Responsible AI Standard 2025, VERIFIED).

Avoid "WIS", "quantile" and "pre-registration" in stakeholder-facing lines.

### 5.3 Pull statements to *seek* in real conversations
These are **HYPOTHETICAL.** They are written so the team knows what to ask for. **Never present them as real quotes or attribute them to anyone.**

1. **(Paediatric bed/roster manager, SEHA)**: *HYPOTHETICAL*: "If on Monday I can see the chance that RSV pushes us past our surge line in the next three weeks, I can open overflow beds and book extra nurses a week earlier, not on the day."
2. **(DoH/ADPHC surveillance)**: *HYPOTHETICAL*: "Tableegh tells us what is happening now. For provider briefings we need an honest estimate of how big and how long this season will run, with its track record attached."
3. **(Immunisation programme / paediatric ID)**: *HYPOTHETICAL*: "A year-by-year record of when RSV actually starts, against our 1 September window, is evidence we can use for catch-up and messaging timing."

**Questions that test the pull** (each closes an UNVERIFIED link in §2):
- "How do you size winter paediatric beds today?" tests link (b).
- "What weekly paediatric respiratory counts could you share in aggregate?" tests link (e).
- "What would you have done differently in Oct 2025 with a 3-week view?" tests link (f).

---

## Appendix: reproducing the in-season error figures (§2c–d)
Run from the repo root (read-only; writes to /tmp):
```python
import pandas as pd
from adapters import flunet
from uae.backtest_v2 import FWD_SEASONS, run_design, fwd_train, common
raw = flunet.load('cached'); s = flunet.sentinel_series(raw)
fsc, _ = run_design(raw, s, FWD_SEASONS, fwd_train)
c = common(fsc, ['NABD-UAE-v1','persistence','seasonal-analog','NABD-UAE-v2'])
c = c[c.model != 'NABD-UAE-v2']; c['ae'] = (c['median'] - c.obs).abs()
# in-season: RSV obs >= 10, flu obs >= 20; horizons 1, 2; error % = sum(ae)/sum(obs) by model
# reduction = 1 - sum(ae_v1)/sum(ae_comparator); CI: bootstrap over reference_date, B=2000, seed 0
```
**Status:** POST HOC, computed by the reviewer after all results were visible. Exploratory, not a claim of the locked protocols.
