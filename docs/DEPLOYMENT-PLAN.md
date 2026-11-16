# NABD: from prototype to a service the UAE can rely on

**Status of this document: a plan.** It separates what exists and is tested today from what would be built with a partner. Nothing here is a result. Written 16 Nov 2026.

## 1. The goal

Give the people who plan paediatric respiratory capacity and public-health advice in the UAE a weekly forecast they can check, challenge and act on, built on the UAE's own surveillance records and held to the evidence standard used by the leading forecasting hubs. NABD adds a forecast layer to systems the UAE already runs. It does not replace any of them.

## 2. Where it stands against the Statement 06 brief

| # | Requirement | Status | Evidence | What closes the gap |
|---|---|---|---|---|
| 1 | Multi-signal surveillance | Partly met | Headline model: laboratory positivity and testing volume. A challenger with non-sentinel data, school breaks and Ramadan did not improve it (reported) | Hospital counts through the pilot connector; wastewater tested as an input and published either way |
| 2 | Explainable anomaly detection | Partly met | Every forecast decomposes exactly into its inputs, each tied to a signal and a period (`results/uae/explain/`, shown on the page) | A sub-national feed; WHO data are national only |
| 3 | Actionable decision support | Met | One action per named role, chance shown, named approver with a reason, hash-chained log | Clinical and public-health review of thresholds and wording |
| 4 | Privacy-preserving views | Partly met | Aggregates only; person-level fields rejected; counts below ten suppressed with complementary suppression (tested) | Sign-in and role-based access in the hosted pilot |
| 5 | Operational validation | Met | Sensitivity 80%, predictive value 58% at a two-week horizon on 36 held-out seasons (post hoc, DEVIATIONS V3); data delay, missing-input behaviour and coverage reported | The same table on the hospital's own counts |
| 6 | Health and resilience impact | Scenario only | Fewer mis-rostered weeks than the own-record model in replay; bed and cost figures are labelled scenarios | The pilot, judged on a pass mark fixed in advance |

## 3. What exists today

- Weekly forecast rounds on WHO data, each sealed with a SHA-256 before WHO publishes the week (`ledger/`).
- Two models on the ledger: the own-record headline model and the pooled challenger, with a forward UAE test locked on 14 Nov 2026 (`docs/PREREG-LIVE.md`).
- The decision card, consistency check, approval step and hash-chained log (`app/`), in Arabic and English.
- The pilot connector, suppression rules and shadow scorer (`adapters/pilot.py`, `uae/pilot_shadow.py`, `tests/test_pilot.py`), run so far on a synthetic file only.
- A public page, a workbench, an API endpoint and a weekly bulletin.

## 4. The pilot, week by week

**Before week 1 (four to eight weeks).** A data-sharing note with one hospital naming purpose, retention and deletion. The partner confirms its export meets ADHICS and that data stay in the UAE. A clinician and a public-health officer review the playbook thresholds and wording. The partner's ethics office decides whether the evaluation needs review. The checklist is in `docs/PILOT-DATA-SPEC.md` section 4.

**Each week of the twelve.**

| Day | Step | Who |
|---|---|---|
| Monday | The hospital exports last week's totals in the agreed table: counts by measure and age band, nothing about individuals | Hospital data owner |
| Monday | The connector checks the schema, rejects any person-level column, suppresses counts below ten and refuses a table that still leaks one | NABD, automatic |
| Monday | Forecasts for the next three weeks are produced and sealed before the next export exists | NABD, automatic |
| Tuesday | The card goes to the hospital's operations lead and, with agreement, the public-health duty officer. In shadow mode nobody acts on it | Named recipients |
| Following weeks | Each forecast is scored against the count that later arrives, beside the hospital's own count carried forward | NABD, automatic |

**After week 12.** One assessment against the pass mark fixed before any data were seen: forecast error below 0.9 of the hospital's own census carried forward, and 80% ranges that contain 70 to 90% of outcomes. If the mark is missed the hospital walks away and the record stays on file.

## 5. Running in service

**Data flow.** Hospital or health-authority systems export weekly totals. NABD never connects to Malaffi or Tableegh directly in the pilot. Hosting is in the UAE.

**Access.** Three roles, matching the playbook: hospital operations, public-health duty officer, occupational health. Each sees the card and the actions for its role. Sign-in and role-based access are to be built for the hosted pilot; the current page is public and holds only public data.

**Changing a model.** A new model first runs beside the headline model on the sealed ledger and is judged by a test written and locked in advance. The pooled model is in that position now. Proposed rule for service: the headline model changes only if that test is met, and the change is recorded with its evidence.

**Monitoring.** Every round is scored when its week is published. Three numbers are tracked: error against repeating last week, coverage of the 80% and 95% ranges, and data age. A card whose forecast, direction and action disagree is blocked. A stale feed is shown as stale on the card.

**When things go wrong.**

| Failure | What happens |
|---|---|
| The weekly export is late or missing | The card shows the data age; forecasts widen; in the US test one missing week raised error 1.41-fold, so the card says so instead of hiding it |
| A table arrives with an identifier or a small count | It is refused before anything is stored |
| The model drifts | Weekly scoring shows it within weeks; the fall-back is the repeat-last-week forecast, which is always displayed beside the model |
| A card contradicts itself | It is blocked and nothing is proposed |

**People.** NABD proposes and a named officer decides. Every decision carries a name and a reason in a chained log. Nothing is sent automatically. Nothing concerns an individual patient or worker.

## 6. Scale

1. **More hospitals in Abu Dhabi**, each scored against its own census.
2. **A read-only feed for public-health teams**: the API endpoint and the weekly bulletin, hosted where the authority chooses.
3. **Other emirates and the Gulf.** The own-record method has already been tested out of sample in Oman, Qatar and Saudi Arabia, and the pooled model on 18 other countries.

WHO data are used under public-health, non-commercial terms. Any commercial service would run on a partner's own data.

## 7. What would stop it

- The pilot misses its pass mark.
- The locked UAE test, due on or after 15 April 2027, is not met. That would keep the own-record model as the headline and send the pooled model back to development.
- A partner's disclosure rules make weekly counts too sparse to forecast.

Each of these outcomes would be published.

## 8. What is needed from a partner

One hospital's weekly totals for twelve weeks, a named data owner, a clinician and a public-health officer for two review sessions on the playbook, and a hosting location inside the UAE.
