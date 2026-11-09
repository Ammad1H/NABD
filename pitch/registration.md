# Registration text: FINAL for 10 Nov 2026 (revised by coordinator after the R3 audit: no 'published'/'blind' claims until anchored; RSV GCC secondary dropped from headline; 'calibrated' → 'probabilistic')

Rules this text obeys (BUILD-SPEC v1.3 CLAIM RULE):
- It describes only (a) what is built and scored in this repo, or (b) items marked "in build for 20 Nov" that are in the round-2 plan.
- Every number traces to `results/` or `research/burden.md`. See `research/claims-ledger.md`.
- Word counts are measured by `pitch/wordcount.py`; the output is pasted at the bottom.

**Statement:** 06, Population and Workforce Health Early Warning (Population Health focus area)

**Title (≤ 100 characters):**
NABD: An Open RSV and Flu Forecasting Hub for Abu Dhabi, Tested Across the Gulf

**One-liner:**
UAE respiratory seasons change timing and shape from year to year, and to our knowledge no one publishes a forecast. NABD is an open hub issuing probabilistic RSV and influenza forecasts up to three weeks ahead, with human-approved actions and a tamper-evident forecast record.

---

## Solution summary (≤ 100 words)
<!-- WC:summary -->
NABD is an open RSV and influenza forecasting hub for Abu Dhabi. It turns WHO FluNet surveillance into probabilistic forecasts up to three weeks ahead. A bilingual Arabic/English card proposes a proportionate action for a named role; a person approves, modifies or dismisses it, and a hash-chained audit log records the decision. Every forecast round is hashed before its outcome exists. In a test on Oman, Qatar and Saudi Arabia, specified and locked before their data were downloaded, the method cut influenza forecast error by 9% against last-week persistence and 46% against past-season patterns.
<!-- /WC -->

## Abstract (≤ 50 words)
<!-- WC:a50 -->
To our knowledge, no one publishes respiratory forecasts for the UAE. NABD is an open RSV and influenza forecasting hub for Abu Dhabi: probabilistic forecasts up to three weeks ahead, a bilingual card whose actions a named officer approves, a tamper-evident record, and a locked test on three Gulf countries.
<!-- /WC -->

## Abstract (≤ 150 words)
<!-- WC:a150 -->
Every winter RSV and influenza send young children to Abu Dhabi's hospitals, but their timing and shape change yearly: UAE influenza has peaked anywhere from October to February, and the RSV peak has moved across six weeks. One Abu Dhabi hospital recorded 2,189 RSV admissions of young children in 2018–2022. The UAE publishes no current weekly flu case counts and, to our knowledge, no respiratory forecasts. NABD is an open forecasting hub. It turns WHO FluNet surveillance into probabilistic RSV and influenza forecasts up to three weeks ahead; a bilingual card proposes an action that a named officer must approve, with a tamper-evident log. In a test on Oman, Qatar and Saudi Arabia, locked before their data were downloaded, the method cut influenza forecast error by 9% against last-week persistence and 46% against past-season patterns. We also benchmark NABD against the CDC FluSight ensemble and report every result, including shortfalls.
<!-- /WC -->

## Abstract (≤ 300 words)
<!-- WC:a300 -->
Every winter, respiratory syncytial virus (RSV) and influenza send young children to Abu Dhabi's hospitals, but their timing and shape change from year to year. UAE influenza has peaked anywhere from October to February, while the RSV peak has moved across six weeks. One Abu Dhabi tertiary hospital recorded 2,189 RSV admissions of children aged five or under over 2018–2022. The UAE publishes no current weekly influenza counts and, to our knowledge, no respiratory forecasts, so planners see last week, not the weeks ahead.

NABD ("pulse"), an open forecasting hub, turns WHO FluNet UAE surveillance into probabilistic forecasts of RSV and influenza positivity up to three weeks ahead. A bilingual card shows the forecast range, the chance of crossing pressure thresholds, data freshness and a proportionate playbook action for a named role. Only a person can approve, modify or dismiss it, and a hash-chained audit log records every decision. Each forecast round is hashed before its outcome exists.

Evidence: in a test on Oman, Qatar and Saudi Arabia, specified and locked before their data were downloaded, the frozen method cut influenza forecast error by 9% against last-week persistence (primary criterion met) and 46% against past-season patterns. In the UAE's own short record, a forward-in-time check shows parity with persistence, which is why we keep a live forecast ledger. In the United States, NABD missed our pre-set bar against the CDC FluSight ensemble; among individual hub models it ranked 7th of 21 in 2024/25 and 19th of 25 in 2025/26.

Also built: a weekly bilingual bulletin; a hospital winter planner that translates the forecast into beds and nurse shifts at risk (scenario, from the hospital's own inputs); and an aggregate-data connector for a hospital pilot. In build for 20 November: publishing and externally timestamping the forecast ledger.

All data are aggregate.
<!-- /WC -->

---

## Current maturity and what we will build (the FAQ asks for this)
**Maturity today (9 Nov): working prototype, version 1.**
- **Built and scored:**
  - data adapters with privacy guards;
  - the UAE forecasting model (v1), with a four-season retrospective and a forward-in-time check (parity with persistence on the UAE's short record);
  - a multi-signal UAE challenger (v2), evaluated under a locked protocol (no improvement over v1; reported);
  - a test of the frozen method on Oman, Qatar and Saudi Arabia, specified and locked in git before their data were downloaded (influenza primary criterion met; Bahrain and Kuwait excluded by the pre-set data rule; lock to be externally timestamped);
  - per-signal explanations of each UAE forecast and a feed-removal test;
  - the US forecasting model, with a pre-registered back-test against the CDC FluSight ensemble (primary bar not met; reported);
  - the bilingual Streamlit decision card with approval and a hash-chained audit;
  - a FastAPI endpoint;
  - a weekly bilingual (Arabic/English) bulletin PDF generated from each forecast round;
  - a hospital winter planner (beds, nurse shifts at risk and roster gap, cost in AED), labelled scenario, with an occupational-health role in the playbook;
  - an aggregate-data pilot connector with k ≥ 10 small-cell suppression (`docs/PILOT-DATA-SPEC.md`);
  - hashed forecast ledger rounds R0 and R1 with a Merkle manifest, not yet published or externally anchored;
  - 140+ automated tests.
- **By 20 Nov:** publishing and externally timestamping the forecast ledger, plus the video and final technical documentation (the deck exists).
- **Not in scope for 20 Nov:** Abu Dhabi hospital or district data (requires a pilot partner), a live employer-absence feed (simulated design only), and the foundation-model member (the wrapper exists; weights were unavailable in our build environment).

## Data sources (the T&C asks for every source to be declared)
| Source | Used for | Status | Licence / terms |
|---|---|---|---|
| WHO FluNet (xMart `VIW_FNT`), United Arab Emirates, sentinel and non-sentinel | UAE model inputs and truth | Used | WHO terms: public-health, non-commercial use, with citation |
| CDC FluSight forecast hub (`cdcepi/FluSight-forecast-hub`): target data (NHSN state influenza admissions, real-time versions) and the FluSight-ensemble / FluSight-baseline forecasts | US benchmark | Used | Hub MIT; underlying US Government data |
| UAE Ministry of Education academic calendars (verified seasons) and Ramadan/Eid dates | UAE v2 challenger covariates | Used | Public fact |
| WHO FluNet: Oman, Qatar, Saudi Arabia (Bahrain, Kuwait screened out) | Pre-registered out-of-sample test | Used (downloaded after the test plan was locked; WHO full export via a public mirror; spot-checked against the official API, with full verification pending) | WHO terms as above |
| NOAA GHCN-Daily, Abu Dhabi International (AE000041217) | Weather covariate | Planned; not used in v1 (blocked in our build environment) | Public domain |
| Synthetic employer sickness-absence counts | Workforce module demo | Simulated, labelled | Generated by the team |
| Published studies (Tawam Hospital RSV and paediatric influenza; Dubai RSV claims) and ADPHC, DoH and press releases | Burden context only | Cited | Fair-use citation |

No personal or patient-level data is used anywhere.

## Team
⟨Names (1–5), lead aged 18+, MBZUAI⟩. Fill in before submitting. Check MBZUAI's own policy on sponsor-run competitions; the T&C has no conflict-of-interest clause.

---
## Measured word counts (pitch/wordcount.py)
```
summary: 94 words (limit 100) OK
a50: 50 words (limit 50) OK
a150: 150 words (limit 150) OK
a300: 300 words (limit 300) OK
```
