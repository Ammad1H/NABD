# Submission form: answers to paste (deadline 20 Nov 2026, 22:29 IST = 20:59 GST)

Counts are characters including spaces, measured by `python pitch/submission/count.py`.

## Challenges
Select the option for **Statement 06: Population and Workforce Health Early Warning**.

## Solution summary (limit 2000)
<!-- F:summary -->
NABD (نبض, "pulse") forecasts how high RSV and influenza will go in the UAE over the next three weeks, and how sure it is, then turns each forecast into one proposed action that a named person must approve.

The problem. Every winter week, hospital bed managers and public-health officers plan from last week's numbers and last year's pattern. But UAE seasons change timing and shape each year, and a model built on the UAE's four seasons of sentinel data alone only ties "repeat last week" (1.00).

The idea: borrowed strength. One model learns how respiratory seasons rise, peak and fade across 46 countries' WHO FluNet records; a country brings only its recent weeks. The test plan was locked, then the model, before the test data were opened. On 18 countries never examined before, the pooled model had 23% less influenza forecast error than each country's own-record model (0.767, 95% CI 0.681–0.832), better in 18 of 18. On the UAE's own last two seasons, forecast forward with the UAE left out of training, it beat "repeat last week" in both (0.77, 95% CI 0.70–0.86): a development check, not a confirmatory test. An off-the-shelf foundation model (Chronos-2) lands level with it on the held-out test.

What the user sees. A bilingual Arabic/English weekly card: the chance of crossing each pressure threshold, one proposed action per role (hospital operations, ADPHC duty officer, occupational health), and an approval step that records a name and a reason in a hash-chained log. Every forecast file is hashed before WHO publishes the week it covers.

What NABD does not claim. An Abu Dhabi hospital result, earlier detection of surge onset, or a confirmatory UAE result. In the US NABD missed its bar against the CDC's combined forecast (1.22 against 1.15). A forward UAE test is locked and reports after 15 April 2027. Aggregate data only.

The ask. A 12-week shadow pilot on one hospital's aggregate weekly counts, with the exit test set in advance.
<!-- /F -->

## Solution stage
Choose the option closest to **working prototype** (functional software, tested on public data, not yet piloted with a hospital). Do not choose a "pilot" or "deployed" stage.

## What has been built during the challenge? (limit 1500)
<!-- F:built -->
Built between 5 and 20 November 2026 by one person:
- Data adapters for WHO FluNet (the UAE and 81 other countries) and the CDC FluSight hub, with schema checks that reject person-level fields.
- Four forecasting models: a UAE own-record model (the hashed headline), a multi-signal variant, a US ensemble, and NABD-Pool, a model pooled across countries.
- Four evaluations whose plans were locked by hash before the data were opened (held-out countries, Gulf, US benchmark, UAE multi-signal), a foundation-model benchmark, two decision replays and a locked forward UAE test.
- A forecast ledger: three rounds so far, each file with a SHA-256 and a Merkle manifest; scoring runs when WHO publishes.
- The decision layer: thresholds, chance of exceedance, one proposed action per role, a gate that blocks contradictory cards, and a hash-chained approve / modify / dismiss log.
- Two front-ends: a static Arabic/English web page generated from the result files (season replay, hash check in the browser) and a Streamlit workbench (hospital winter planner, PDF bulletin, every table), plus a FastAPI /forecast endpoint.
- 163 automated tests, technical documentation, a deviations log, a claims ledger and a pilot data specification.
Not built: any Abu Dhabi hospital data feed (pilot only). The employer-absence feed is simulated and labelled as such.
<!-- /F -->

## Technology type
Tick: **Machine learning**, **Software application**, **Analytics**. Leave AI agent, Wearable, Sensor, Connected device and Other hardware unticked.

## Prototype / Deployment Link
`https://ammad1h.github.io/NABD/` once it is live (see `HOSTING.md`). It must open without a login before you submit; the deck prints this address and `https://github.com/Ammad1H/NABD`.

## Upload your solution deck
`pitch/submission/NABD-submission-deck.pdf` (PDF, under 5 MB).

## Conflict of interest
You told me on 15 Nov 2026 that you are an MBZUAI student with no employment or contract. On that basis none of the five listed situations applies as worded, so the matching answer is **"None"**. Slide 14 of the deck still discloses the MBZUAI affiliation. If you receive a stipend or scholarship under a contract with MBZUAI, ask the organisers before ticking "None" (see `HOSTING.md`).

## Software, hardware or both
**Software**.

## Demo video link
Record from the web page using the voiceover in `pitch/story.md`; upload unlisted to YouTube or to Google Drive with "anyone with the link can view"; under 3 minutes.
