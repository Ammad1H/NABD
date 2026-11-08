# Registration text (for 10 Nov). No result claims; burden figures VERIFIED (see research/burden.md)

**Statement:** 06, Population and Workforce Health Early Warning (Population Health)

**Title:** NABD: Calibrated RSV and Flu Surge Forecasts for Abu Dhabi Hospitals

**One-liner:** NABD fuses surveillance, ED, environmental and administrative signals into calibrated 1–3-week RSV and flu surge forecasts. A named officer approves each recommended action, and every forecast is publicly timestamped before its outcome is known.

**Maturity statement** (the FAQ asks for current maturity and what will be built):
Concept, pre-registered evaluation protocol and data pipelines in progress. Preliminary analyses on public data are complete. During the Challenge we will build the forecasting ensemble, the vintage-correct back-test, the UAE track, the bilingual decision card with approval and audit, and the public forecast ledger.

---

## Abstract, 50 words
NABD forecasts the size and duration of RSV and influenza surges for Abu Dhabi, fusing clinical, emergency-department, environmental and administrative signals into calibrated forecasts. A bilingual card proposes staffing and bed actions that a named officer approves. Every forecast is publicly timestamped and benchmarked, using only data available at the time, against the CDC FluSight ensemble.

## Abstract, 150 words
RSV and influenza reach Abu Dhabi's hospitals together every winter, but their timing and size vary: one Abu Dhabi tertiary hospital recorded 2,189 RSV admissions of young children over five years, with yearly positivity ranging from 2.9% to 16%. NABD ("pulse") is a population early-warning system for Statement 06. It fuses five kinds of signal into calibrated forecasts of the size of the next one to three weeks:
- clinical (WHO FluNet UAE laboratory data; US hospital admissions);
- emergency-department syndromic;
- geospatial;
- environmental (weather);
- administrative (school calendar, testing volume).

A bilingual card explains what drove each forecast and proposes playbook actions that a named officer must approve, with a full audit trail. Our evaluation is pre-registered:
- non-inferiority to the CDC FluSight ensemble on US data, using only the data available at each forecast date;
- UAE retrospective skill against persistence;
- surge-alert lead time, sensitivity and false alarms.

Every live forecast is committed publicly before its outcome exists. All data are aggregate.

## Abstract, 300 words
Every winter, respiratory syncytial virus (RSV) and influenza converge on Abu Dhabi's emergency and paediatric services, but not on a fixed calendar. In the last four UAE seasons, sentinel RSV positivity peaked anywhere between ISO weeks 41 and 47. At one Abu Dhabi tertiary hospital, 2,189 children aged five or under were admitted with RSV over 2018–2022, and yearly positivity ranged from 2.9% to 16%. In Dubai, about one in five infants with RSV was hospitalised, and fewer than 2% had a known risk factor. Hospitals need to know how large and how long the coming weeks will be, but public surveillance mostly describes the past.

NABD ("pulse") responds to Statement 06 by fusing signals where real data exist:
- clinical: WHO FluNet UAE laboratory surveillance; US hospital admissions;
- service and geospatial: emergency-department syndromic data by region;
- environmental: Abu Dhabi weather;
- administrative: school calendar, testing volume.

An occupational sickness-absence feed is delivered as a privacy-preserving secure-aggregation design on clearly labelled synthetic data. An interpretable statistical core and a time-series foundation model are combined into a calibrated quantile ensemble, with horizons reported honestly relative to publication lags. A bilingual (Arabic/English) card shows forecasts, the signals, weeks and regions that drove them, and data freshness. It proposes playbook actions, such as surge rosters, bed opening and advisories, that only a named approver can release, and every decision is audited.

Our evaluation is pre-registered before testing:
- non-inferiority to the CDC FluSight ensemble on US data, using only the data available at each forecast date;
- UAE retrospective skill against persistence (four seasons, stated as such);
- surge-alert lead time, sensitivity, positive predictive value and false alarms;
- behaviour when inputs are missing.

Every live forecast is committed publicly before its outcome exists. NABD uses aggregate data only, plugs into existing public-health platforms, and proposes a 12-week shadow pilot on one hospital's aggregate admissions.

---
Word counts (measured): 50-word = 56; 150-word = 160; 300-word = 310. Trim the last clause of each if the form enforces hard limits.
