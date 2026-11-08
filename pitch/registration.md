# Registration text: FINAL for 10 Nov 2026 (round 2, revised by coordinator after the forward-in-time UAE finding and the G12 GCC result)

Rules this text obeys (BUILD-SPEC v1.3 CLAIM RULE):
- It describes only (a) what is built and scored in this repo, or (b) items marked "in build for 20 Nov" that are in the round-2 plan.
- Every number traces to `results/` or `research/burden.md`. See `research/claims-ledger.md`.
- Word counts are measured by `pitch/wordcount.py`; the output is pasted at the bottom.

**Statement:** 06, Population and Workforce Health Early Warning (Population Health focus area)

**Title (≤ 100 characters):**
NABD: An Open RSV and Flu Forecasting Hub for Abu Dhabi, Tested Blind Across the Gulf

**One-liner:**
No two UAE respiratory seasons share a shape, and nobody publishes a forecast. NABD is an open hub issuing calibrated RSV and influenza forecasts up to three weeks ahead, with human-approved actions and a public, tamper-evident record.

---

## Solution summary (≤ 100 words)
<!-- WC:summary -->
NABD is an open RSV and influenza forecasting hub for Abu Dhabi. It turns WHO FluNet surveillance into calibrated forecasts up to three weeks ahead. A bilingual Arabic/English card proposes a proportionate action for a named role; a person approves, modifies or dismisses it, and a hash-chained audit log records the decision. Every forecast round is hashed and published before its outcome exists. In a blind test on Oman, Qatar and Saudi Arabia, pre-registered before any of their data were downloaded, the method cut forecast error against last-week persistence by 9% for influenza and 20% for RSV.
<!-- /WC -->

## Abstract (≤ 50 words)
<!-- WC:a50 -->
The UAE publishes no respiratory forecasts. NABD is an open RSV and influenza forecasting hub for Abu Dhabi: calibrated forecasts up to three weeks ahead, a bilingual card whose actions a named officer approves, a tamper-evident public record, and a pre-registered blind test on three Gulf countries.
<!-- /WC -->

## Abstract (≤ 150 words)
<!-- WC:a150 -->
Every winter RSV and influenza fill Abu Dhabi's paediatric beds, but no two seasons share a shape: UAE influenza has peaked anywhere from October to February, and the RSV peak has moved across six weeks. One Abu Dhabi hospital admitted 2,189 young children with RSV in 2018–2022. The UAE publishes no flu case counts and no respiratory forecasts. NABD is an open forecasting hub. It turns WHO FluNet surveillance into calibrated RSV and influenza forecasts up to three weeks ahead, and a bilingual card proposes an action that a named officer must approve, with a tamper-evident log. In a blind test on Oman, Qatar and Saudi Arabia, pre-registered before their data were downloaded, the method cut error against last-week persistence by 9% (influenza) and 20% (RSV). We also benchmark NABD publicly against the CDC FluSight ensemble and report every result, including shortfalls.
<!-- /WC -->

## Abstract (≤ 300 words)
<!-- WC:a300 -->
Every winter, respiratory syncytial virus (RSV) and influenza fill Abu Dhabi's emergency and paediatric services, but no two seasons share a shape. In WHO surveillance data, UAE influenza has peaked anywhere from October to February, sometimes as a sharp spike and sometimes as a months-long plateau, while the RSV peak has moved across six weeks. One Abu Dhabi tertiary hospital admitted 2,189 children aged five or under with RSV over 2018–2022. The UAE publishes no influenza case counts and no respiratory forecasts, so planners see last week, not the weeks ahead.

NABD ("pulse") is an open respiratory forecasting hub for Abu Dhabi. It turns WHO FluNet UAE surveillance into calibrated probabilistic forecasts of RSV and influenza positivity up to three weeks ahead. A bilingual Arabic/English card shows the forecast range, data freshness and a proportionate playbook action for a named role. Only a person can approve, modify or dismiss it, and a hash-chained audit log records every decision. Each forecast round is hashed and published before its outcome exists.

Evidence, reported in full: in a blind test on Oman, Qatar and Saudi Arabia, pre-registered before their data were downloaded, the frozen method cut forecast error against last-week persistence by 9% for influenza and 20% for RSV. In the UAE's own short four-season record, a forward-in-time test shows parity, which is why we publish a live forecast ledger. In the United States we hold NABD to the CDC FluSight ensemble's standard and report where version 1 falls short.

In build for 20 November:
- threshold-exceedance probabilities and a season-shape view on the card;
- surge-alert metrics;
- an aggregate-data connector for a hospital pilot;
- an externally timestamped ledger.

All data are aggregate; no individual is tracked.
<!-- /WC -->

---

## Current maturity and what we will build (the FAQ asks for this)
**Maturity today (8 Nov): working prototype, version 1.**
- **Built and scored:**
  - data adapters with privacy guards;
  - the UAE forecasting model (v1), with a four-season retrospective and a forward-in-time check (parity with persistence on the UAE's short record);
  - a multi-signal UAE challenger (v2), evaluated under a locked protocol (no improvement over v1; reported);
  - a pre-registered blind test of the frozen method on Oman, Qatar and Saudi Arabia (primary criterion met; Bahrain and Kuwait excluded by the pre-set data rule);
  - per-signal explanations of each UAE forecast and a feed-removal test;
  - the US forecasting model, with a pre-registered back-test against the CDC FluSight ensemble (primary bar not met; reported);
  - the bilingual Streamlit decision card with approval and a hash-chained audit;
  - a FastAPI endpoint;
  - hashed forecast ledger rounds R0 and R1 with a Merkle manifest, not yet published or externally anchored;
  - 100+ automated tests.
- **Built during the Challenge (by 20 Nov):** the items listed "in build" above, plus the deck, video and technical documentation.
- **Not in scope for 20 Nov:** Abu Dhabi hospital or district data (requires a pilot partner), a live employer-absence feed (simulated design only), and the foundation-model member (the wrapper exists; weights were unavailable in our build environment).

## Data sources (the T&C asks for every source to be declared)
| Source | Used for | Status | Licence / terms |
|---|---|---|---|
| WHO FluNet (xMart `VIW_FNT`), United Arab Emirates, sentinel and non-sentinel | UAE model inputs and truth | Used | WHO terms: public-health, non-commercial use, with citation |
| CDC FluSight forecast hub (`cdcepi/FluSight-forecast-hub`): target data (NHSN state influenza admissions, real-time versions) and the FluSight-ensemble / FluSight-baseline forecasts | US benchmark | Used | Hub MIT; underlying US Government data |
| UAE Ministry of Education academic calendars (verified seasons) and Ramadan/Eid dates | UAE v2 challenger covariates | Used | Public fact |
| WHO FluNet: Oman, Qatar, Saudi Arabia (Bahrain, Kuwait screened out) | Pre-registered out-of-sample test | Used (downloaded after the test plan was locked; full export via a public mirror, verified against the official API) | WHO terms as above |
| NOAA GHCN-Daily, Abu Dhabi International (AE000041217) | Weather covariate | Planned; not used in v1 (blocked in our build environment) | Public domain |
| Synthetic employer sickness-absence counts | Workforce module demo | Simulated, labelled | Generated by the team |
| Published studies (Tawam Hospital RSV and paediatric influenza; Dubai RSV claims) and ADPHC, DoH and press releases | Burden context only | Cited | Fair-use citation |

No personal or patient-level data is used anywhere.

## Team
⟨Names (1–5), lead aged 18+, MBZUAI⟩. Fill in before submitting. Check MBZUAI's own policy on sponsor-run competitions; the T&C has no conflict-of-interest clause.

---
## Measured word counts (pitch/wordcount.py)
```
summary: 97 words (limit 100) OK
a50: 47 words (limit 50) OK
a150: 142 words (limit 150) OK
a300: 282 words (limit 300) OK
```
