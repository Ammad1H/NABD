# Judge Q&A prep, round 2: hostile questions with answers that trace to files

**Rules:**
- Every number cites a file in `results/` or `research/`. Don't improvise a number on stage.
- ⟦RESULT: file⟧ marks an output still in build. If it isn't there on the day, say "in build" and don't guess.
- Keep each answer under about 30 seconds.

**Two numbers to know cold:**
- **US primary:** NABD v1 vs the CDC FluSight ensemble, relative WIS **1.22 (95% CI 1.01–1.52)**, margin 1.15: **NOT MET** (`results/summary.json` → `primary`).
- **UAE:** NABD-UAE-v1 vs carrying the latest week forward, relative WIS **flu 0.76, RSV 0.78**, better in **7 of 8** season-series. Four seasons, retrospective, design-stage, not pre-registered (`results/uae/SUMMARY.md`).

---

## A. The result we lost

**1. "You didn't meet your own bar against the CDC. Why are you here?"**
- Because we set the bar at the best forecaster there is, froze the test before running it, and are showing you the loss. NABD v1 scored 1.22 against the CDC FluSight ensemble (CI 1.01–1.52); the bar was an upper bound below 1.15 (`results/SUMMARY.md`).
- The ensemble pools about 40 US teams. Nothing like it exists for the UAE, where the alternative today is no forecast at all.
- The US test is how you know our UAE numbers weren't tuned until they looked good.

**2. "Be specific: where did it lose?"**
- 2024/25: 1.03 (0.89–1.25), level with the ensemble on the point estimate.
- 2025/26: 1.52 (1.09–2.03) (`results/SUMMARY.md`, rows S3).
- **Failure mode:** overshoot after the peak. In Feb 2025 the median for Texas and California ran well above the truth as the wave turned (`results/figures/fan_chart_CA_TX_h1.png`). We found this after the test, so it is a hypothesis for v2, not a claim.

**3. "Your metric includes the national US series. Isn't that hiding something?"**
- It's the protocol's metric, and we don't hide what it implies. The national series is about 46% of NABD's error.
- On states alone, NABD is still worse than the ensemble: per state it loses in every location pooled, and in all 52 in 2025/26 (sensitivity analysis ⟦RESULT: results/tables/sensitivity_* (D6)⟧; first measured in `docs/REVIEW-R2-audit.md` item 6).
- No state-level framing rescues v1, and we don't try.

**4. "Did NABD even beat the naive baseline in the US?"**
- On average yes, but not convincingly: relative WIS 0.82 vs the FluSight baseline, CI 0.66–1.02, so the interval touches no improvement. 2024/25 was 0.69 (0.57–0.81); 2025/26 was 1.00 (`results/SUMMARY.md`).
- For scale, the CDC ensemble scored 0.67 against the same baseline on the same cells. That is the gap we have to close.

**5. "Isn't your 'better during surges' result just spin?"**
- We don't claim it. That split (E1) was defined using the truth, after the fact, and NABD's gain there comes from wider intervals, not a better trend (`docs/DEVIATIONS.md`, E1).
- It's labelled exploratory and appears in no headline.

**6. "Will you tweak the model and re-run until it passes?"**
- No. The protocol was frozen before any test score (`docs/FREEZE.md`, commit `ac16901`). Every change since is logged in `docs/DEVIATIONS.md`, including that early probes had touched the test seasons before the freeze (D5).
- Any v2 is judged only on forecasts made after it is locked.

## B. Thin evidence

**7. "Four UAE seasons is nothing."**
- Agreed: n = 4, retrospective, design-stage, not pre-registered. RSV lost to persistence in 2025/26, the only fold that is genuinely forward in time (`results/uae/SUMMARY.md`, season table).
- So the frozen UAE method goes through two tests we can't tune for:
  - other Gulf countries' WHO data, with the test plan locked before download ⟦RESULT: results/gcc/ (G12)⟧;
  - the live weekly ledger, published before outcomes exist (`ledger/`).

**8. "You have no Abu Dhabi hospital data."**
- Correct, and we claim no Abu Dhabi operational result. WHO FluNet positivity is surveillance, not bed load.
- Hospital load is the pilot question: a 12-week shadow run on one hospital's aggregate counts, with exit criteria set in advance (`pitch/assumptions-limitations.md`).

**9. "Lead time is zero. Where's the early warning?"**
- Correct: median onset lead is 0 weeks for every rule, ours, the CDC ensemble's and a simple census threshold (`results/tables/alerts_us.csv`).
- Forecasts don't tell you *when* a wave starts sooner than your own census. What we offer is fewer false alarms and a calibrated range for the coming weeks.

**10. "Then what does the alert layer buy us? Alert fatigue?"**
- Precision. At 3 per 100k, the share of NABD alerts followed by a real onset was 0.65 (2024/25) and 0.76 (2025/26), against 0.41 and 0.67 for the CDC ensemble and 0.60 and 0.46 for a census rule (`results/tables/alerts_us.csv`).
- **Caveats:**
  - Sensitivity is mixed. In 2024/25 the census rule caught more onsets on time (0.55 vs 0.33).
  - The rule's thresholds were informed by probes that touched the test seasons (`docs/DEVIATIONS.md` D3, D5), so treat these as diagnostic, not proof.
- UAE alert metrics: ⟦RESULT: results/uae/ alert table (G10)⟧.

**11. "What happens when a data feed is late?"**
- It degrades, and we measured it: one missing week raises US error 1.41-fold, two weeks 1.82-fold (`results/tables/dropout_us.csv`).
- The card shows a data-freshness badge with the exact lag, so nobody acts on stale data unknowingly.
- v1 is single-signal, so there is no other feed to fall back on yet. That is what the multi-signal UAE v2 is for ⟦RESULT: results/uae/tables/ablation.csv⟧.

## C. Method

**12. "How do you know the back-test doesn't leak?"**
- Each US forecast uses only the hub data version available by the Wednesday deadline before its reference date. The hub's versions are not weekly; where one is missing we fall back to the previous version and flag it (`results/tables/vintage_flags.csv`).
- A test injects future data and must fail (`tests/test_vintage.py`). The UAE test caught and fixed a real leak in our first build (`results/uae/SUMMARY.md`, integrity note).
- NABD and the ensemble are scored on the same cells against the same truth.

**13. "How are your intervals calibrated?"**
- No online conformal adjustment in v1. Intervals come from the negative-binomial dispersion and empirical log-error quantiles, tuned on 2023/24 only, with a fixed widening factor (`models/config.yaml`).
- **Result:** 95% coverage 0.92 vs the ensemble's 0.86; 50% coverage 0.48 vs 0.52 (`results/summary.json` → S2).

**14. "Is there any 'AI' here beyond a GLM?"**
- v1 is deliberately simple, statistical and auditable: a damped log-linear GLM plus an empirical-quantile ensemble.
- The Chronos-2 foundation-model wrapper exists but was not run (weights unavailable in our build environment; `results/summary.json` → chronos2), so we claim nothing from it.
- What's hard here isn't the model class. It's leakage-free evaluation, calibration and a public record.

**15. "Your UAE horizons say up to three weeks, but WHO data is about 10 days late."**
- That's why horizons are labelled from the issue date: nowcast, +0.5, +1.5 and +2.5 weeks, and every ledger row carries the label.
- Measured lag on 8 Nov: 7 days for week 44 (`data/raw/PROVENANCE.md`).

## D. Positioning and business

**16. "ADPHC already tendered an AI epidemic-prediction platform, and G42 runs Rasid. Why you?"**
- The 2024 tender covers outbreak detection, dashboards and travel signals. Rasid is wastewater monitoring. Both answer "is something emerging?" (`research/competitors.md`).
- NABD answers "how big will the known seasonal RSV and flu wave be over the next weeks, and how good has this forecast been?". It is a feed either platform can host.
- **Rasid offer:** we'd add its wastewater signal as an input and publish whether it helps.

**17. "GE's CareIntellect already predicts census."**
- Up to 72 hours, from inside-hospital data. We forecast weeks ahead from community surveillance the hospital can't see. Complementary, not competing (`research/competitors.md`).

**18. "WHO FluNet is non-commercial. Isn't your business blocked?"**
- No. FluNet powers the public-health feed and the evaluation only. A commercial hospital product would run on the hospital's own aggregate data and not redistribute FluNet.
- Every source is declared (`pitch/registration.md`, Data sources).

**19. "Who pays, and why would SEHA say yes?"**
- Hospital operations, for winter bed and roster planning, and the public-health side for a regional forecast feed.
- The first step is a 12-week shadow run on aggregate counts. Nothing changes in patient care, and success is pre-defined as beating the hospital's own census carried forward.
- **Honest status:** no letter of interest yet.

**20. "Why does a Gulf test matter?"**
- It's the only way to turn n = 4 into real evidence quickly. We lock the method and test plan, then download other Gulf countries' WHO data nobody on the team has seen, and report every country, losses included ⟦RESULT: results/gcc/ (G12)⟧.
- If it holds up, the same engine is a GCC forecasting hub; if not, we say so.

**21. "What's defensible? Anyone can fit a GLM."**
- A competitor can copy the model in a weekend. They can't copy a dated public track record, a frozen protocol with its deviation log, leakage-tested data adapters, or the approval and audit workflow a hospital signs off on.
- The record gets more valuable every week it runs.

## Curveballs
- **"Is this season unusual?"** DoH said in September that activity looks similar to the previous two seasons (`research/burden.md`, item 8). NABD's value is in normal-but-variable years, not in a crisis story.
- **"Do you use patient data?"** No. Aggregates only; adapters reject person-level fields, and a test checks it (`tests/test_adapters.py`).
- **"Conflict of interest? MBZUAI is a co-creator."** The T&C has no conflict clause (`research/tc.md`). Institutional permission is ours to get: ⟨team confirms status⟩.
- **"Are the timestamps real?"** Today they are git commits we made ourselves. Outside anchors (OpenTimestamps / Zenodo) are in build ⟦RESULT: ledger/ANCHOR.md⟧. Until they exist, say "self-attested".
