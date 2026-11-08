# Registration text: FINAL for 10 Nov 2026 (round 2)

Rules this text obeys (BUILD-SPEC v1.3 CLAIM RULE):
- It describes only (a) what is built and scored in this repo, or (b) items marked "in build for 20 Nov" that are in the round-2 plan.
- Every number traces to `results/` or `research/burden.md`. See `research/claims-ledger.md`.
- Word counts are measured by `pitch/wordcount.py`; the output is pasted at the bottom.

**Statement:** 06, Population and Workforce Health Early Warning (Population Health focus area)

**Title (≤ 100 characters):**
NABD: An Open RSV and Flu Forecasting Hub for Abu Dhabi, Held to the CDC's Standard

**One-liner:**
The UAE publishes no respiratory forecasts. NABD is an open forecasting hub that issues calibrated RSV and influenza forecasts up to three weeks ahead, routes each proposed action to a named human approver, and keeps a public, tamper-evident record of every forecast.

---

## Solution summary (≤ 100 words)
<!-- WC:summary -->
NABD is an open RSV and influenza forecasting hub for Abu Dhabi. It turns WHO FluNet UAE surveillance into calibrated forecasts up to three weeks ahead. A bilingual Arabic/English card proposes a proportionate action for a named role, a person approves, modifies or dismisses it, and a hash-chained audit log records the decision. Every forecast round is hashed and published before its outcome exists. In a four-season retrospective, NABD's UAE model beat carrying the latest week forward in 7 of 8 season-series. We also benchmark it, in public and with all results reported, against the CDC FluSight ensemble.
<!-- /WC -->

## Abstract (≤ 50 words)
<!-- WC:a50 -->
The UAE publishes no respiratory forecasts. NABD is an open RSV and influenza forecasting hub for Abu Dhabi: calibrated forecasts up to three weeks ahead from WHO surveillance, a bilingual card whose actions a named officer approves, and a tamper-evident public record, benchmarked openly against the CDC FluSight ensemble.
<!-- /WC -->

## Abstract (≤ 150 words)
<!-- WC:a150 -->
RSV and influenza reach Abu Dhabi's hospitals every winter, but never on a fixed calendar. One Abu Dhabi tertiary hospital admitted 2,189 young children with RSV over 2018–2022, while yearly positivity swung from 2.9% to 16%. The UAE publishes no flu case counts and no respiratory forecasts. NABD fills that gap with an open forecasting hub. It turns WHO FluNet surveillance into calibrated RSV and influenza forecasts up to three weeks ahead. A bilingual card proposes an action that a named officer must approve, and a tamper-evident log records every decision. In a four-season retrospective, the UAE model beat carrying the latest week forward in 7 of 8 season-series. We benchmark NABD publicly against the CDC FluSight ensemble and report every result. In build for 20 November: a multi-signal UAE model with per-signal explanations, alert metrics, a test on other Gulf countries' data, and an externally timestamped forecast ledger.
<!-- /WC -->

## Abstract (≤ 300 words)
<!-- WC:a300 -->
Every winter, respiratory syncytial virus (RSV) and influenza reach Abu Dhabi's emergency and paediatric services together, but never on a fixed calendar. In the last four UAE seasons, sentinel RSV positivity peaked anywhere between ISO weeks 41 and 47. One Abu Dhabi tertiary hospital admitted 2,189 children aged five or under with RSV over 2018–2022, while yearly positivity swung from 2.9% to 16%. The UAE publishes no influenza case counts and no respiratory forecasts, so planners see last week, not the coming weeks.

NABD ("pulse") is an open respiratory forecasting hub for Abu Dhabi. It turns WHO FluNet UAE surveillance (laboratory positivity and testing volume) into calibrated probabilistic forecasts of RSV and influenza positivity up to three weeks ahead. A bilingual Arabic/English card shows the forecast range, data freshness and a proportionate playbook action for a named role, such as a hospital bed manager or a public-health duty officer. Only a person can approve, modify or dismiss it, and a hash-chained audit log records every decision. Each forecast round is hashed and published before its outcome exists, so the track record cannot be edited afterwards.

In a four-season retrospective, NABD's UAE model beat carrying the latest week forward in 7 of 8 season-series. We hold NABD to the CDC's standard in public: a pre-registered US test against the CDC FluSight ensemble, using only data available at each forecast date, with every result reported, including where version 1 falls short.

In build for 20 November:
- a multi-signal UAE model (non-sentinel surveillance, testing volume, school calendar) with per-signal explanations of each forecast;
- surge-alert lead time, sensitivity, precision and false alarms;
- a test of the frozen method on other Gulf countries' WHO data;
- an externally timestamped forecast ledger.

All data are aggregate; no individual is tracked.
<!-- /WC -->

---

## Current maturity and what we will build (the FAQ asks for this)
**Maturity today (8 Nov): working prototype, version 1.**
- **Built and scored:**
  - data adapters with privacy guards;
  - the UAE forecasting model, with a four-season retrospective;
  - the US forecasting model, with a pre-registered back-test against the CDC FluSight ensemble (primary bar not met; reported);
  - the bilingual Streamlit decision card with approval and a hash-chained audit;
  - a FastAPI endpoint;
  - a hashed forecast ledger round, not yet published;
  - 50+ automated tests.
- **Built during the Challenge (by 20 Nov):** the items listed "in build" above, plus the deck, video and technical documentation.
- **Not in scope for 20 Nov:** Abu Dhabi hospital or district data (requires a pilot partner), a live employer-absence feed (simulated design only), and the foundation-model member (the wrapper exists; weights were unavailable in our build environment).

## Data sources (the T&C asks for every source to be declared)
| Source | Used for | Status | Licence / terms |
|---|---|---|---|
| WHO FluNet (xMart `VIW_FNT`), United Arab Emirates, sentinel and non-sentinel | UAE model inputs and truth | Used | WHO terms: public-health, non-commercial use, with citation |
| CDC FluSight forecast hub (`cdcepi/FluSight-forecast-hub`): target data (NHSN state influenza admissions, real-time versions) and the FluSight-ensemble / FluSight-baseline forecasts | US benchmark | Used | Hub MIT; underlying US Government data |
| UAE Ministry of Education 2026/27 academic calendar (as reported by Gulf News) | UAE v2 covariate | In build | Public fact |
| WHO FluNet, other GCC/EMRO countries | Out-of-sample test | In build (to be downloaded after the test plan is locked) | WHO terms as above |
| NOAA GHCN-Daily, Abu Dhabi International (AE000041217) | Weather covariate | Planned; not used in v1 (blocked in our build environment) | Public domain |
| Synthetic employer sickness-absence counts | Workforce module demo | Simulated, labelled | Generated by the team |
| Published studies (Tawam Hospital RSV and paediatric influenza; Dubai RSV claims) and ADPHC, DoH and press releases | Burden context only | Cited | Fair-use citation |

No personal or patient-level data is used anywhere.

## Team
⟨Names (1–5), lead aged 18+, MBZUAI⟩. Fill in before submitting. Check MBZUAI's own policy on sponsor-run competitions; the T&C has no conflict-of-interest clause.

---
## Measured word counts (pitch/wordcount.py)
```
summary: 98 words (limit 100) OK
a50: 49 words (limit 50) OK
a150: 149 words (limit 150) OK
a300: 293 words (limit 300) OK
```
