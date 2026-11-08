# Judge Q&A prep, round 3: hostile questions with answers that trace to files

**Rules:**
- Every number cites a file in `results/`, `research/` or `docs/`. Never improvise a number on stage.
- ⟦IF BUILT: file⟧ marks something still in build. If it isn't there on the day, say "in build" and stop.
- Keep each answer under about 30 seconds.
- **Evidence order (BUILD-SPEC v1.6):** (1) blind Gulf test → (2) public, anchored ledger → (3) US CDC benchmark and league placement → (4) the UAE record is at parity, which is why the ledger exists.
- The stop list in `research/positioning.md` §4.6 is binding.

**Numbers to know cold:**
- **Blind Gulf test (G12), primary MET:** frozen UAE method vs "next week = this week" (persistence), influenza, Oman + Qatar + Saudi Arabia, forward-in-time. Relative WIS **0.914 (95% CI 0.843–0.983)**, 9 of 12 country-seasons won. RSV **0.798 (0.719–0.894)**, 9 of 10 (`results/gcc/SUMMARY.md`).
- **US primary, NOT MET:** NABD v1 vs the CDC FluSight ensemble, relative WIS **1.22 (95% CI 1.01–1.52)**, margin 1.15 (`results/SUMMARY.md`).
- **US league (pairwise relative WIS vs FluSight-baseline, single models only):** **7th of 21 in 2024/25** (0.693), **19th of 25 in 2025/26** (0.997) (`results/tables/league_table.csv`).
- **UAE own record, forward-in-time:** v1 vs persistence **1.002 (flu), 1.002 (RSV)**, i.e. parity (`results/uae/SUMMARY-v2.md`).

---

## A. The blind Gulf test (our headline evidence)

**1. "What exactly did you test on the Gulf?"**
- We froze the UAE method and wrote the test plan, including country inclusion rules and the pass bar, before downloading any other Gulf country's WHO data (`docs/PREREG-GCC.md`, locked in `docs/LOCK-GCC.json`).
- Then we ran it forward in time: each season, the model learns only from that country's earlier seasons.
- **Influenza:** 0.914 vs persistence (CI 0.843–0.983), so the pre-set bar (upper bound < 1) is **MET**.
- **RSV:** 0.798 (0.719–0.894).
- **Against a seasonal-average forecast:** 0.536 (flu) and 0.685 (RSV) (`results/gcc/SUMMARY.md`).

**2. "Where did it lose?"**
- **Influenza:** Oman 2022/23 and 2024/25, plus a tie in Qatar 2023/24.
- **RSV:** Saudi Arabia 2025/26 (`results/gcc/SUMMARY.md`, per country-season table).
- **Calibration:** RSV intervals are too narrow outside the UAE, with 95% coverage of 0.83. We report that.

**3. "Why only three countries?"**
- The inclusion rule was set before download: at least 2 scorable influenza seasons with enough weekly testing.
- Bahrain and Kuwait each had one scorable season, so the rule excluded them. Their results are not used (`results/gcc/SUMMARY.md`, inclusion table).

**4. "How blind was 'blind'? You chose v1 after seeing UAE results."**
- **True, and disclosed.** We picked v1 as the primary method after the UAE v2 and forward-in-time results were known. The exposure declaration says so (`docs/PREREG-GCC.md` §1).
- **Nobody on the team had looked at the Gulf countries' data.** We searched our repo and notes for prior use and found none (same section).
- **The lock is self-attested.** It is a local git commit made about 1.5 minutes before the data commit (`docs/FREEZE.md`; commits `91005ce` then `d013228`).
- **Data provenance:** the data came from WHO's full export through a public mirror and were checked row-for-row against the official WHO API (deviation G1).

**5. "Retrospective data. Isn't this just a back-test?"**
- **Yes.** These are revised FluNet values, so it is retrospective, and every result says so.
- **What makes it more than a back-test:** the countries were unseen and the plan was fixed before download.
- **The truly prospective evidence** is the public ledger, which grows every week (`ledger/`).

## B. The UAE's own record

**6. "Your UAE model only ties with 'next week = this week'. Why should Abu Dhabi care?"**
- **On the UAE's own four seasons, forward in time, it ties:** 1.002 for both flu and RSV (`results/uae/SUMMARY-v2.md`).
- **The earlier 0.76/0.78 figures are retired.** They came from leave-one-season-out folds that trained on later seasons.
- **Four seasons is too short to learn the UAE's season shapes.** That's why we tested the method on Gulf neighbours with longer records, where it beat persistence, and why we publish every live forecast.
- The value we claim is a calibrated range with a checkable record. We don't claim a proven UAE edge.

**7. "Did the multi-signal version help?"**
- **No.** UAE v2 adds non-sentinel lab data, testing volume, school breaks and Ramadan, under a protocol locked before scoring.
- **It was worse than v1:** pooled 1.059 (moving-block CI 1.016–1.111) (`results/uae/SUMMARY-v2.md`).
- **Feed removal:** dropping non-sentinel data or the calendar slightly improved v2. Testing volume made no difference. Removing the seasonal climatology term hurt the most (`results/uae/tables/ablation.csv`).
- **What we do with it:** v2 runs alongside v1 in the ledger as a challenger. It is not the headline.

**8. "Four seasons is nothing."**
- **Agreed:** n = 4, and v1 was designed with all four visible (`results/uae/SUMMARY.md`, integrity note).
- **The two tests we can't tune for** are the Gulf test above and the live ledger.

**9. "No Abu Dhabi hospital data?"**
- **Correct.** WHO FluNet positivity is laboratory surveillance, not bed load, and we claim no Abu Dhabi operational result.
- **The pilot is how we find out:** a 12-week shadow run on one hospital's aggregate counts, with exit criteria set in advance (`pitch/assumptions-limitations.md`).

## C. The US stress test

**10. "You didn't meet your own bar against the CDC. Why are you here?"**
- **We set the bar at the best public forecaster and froze the test first.** NABD v1 scored 1.22 vs the CDC FluSight ensemble (CI 1.01–1.52) against a 1.15 margin: NOT MET (`results/SUMMARY.md`).
- **There is nothing comparable in the UAE.** Locally, the alternative is no forecast at all.
- **Our losses are on the record,** which is how you know our other numbers weren't tuned until they looked good.

**11. "Where does that put you among real forecasters?"**
- **Method:** we declared it before computing. It is pairwise relative WIS against the FluSight baseline, scored on cells common to the models, for hub models with at least 50% coverage (`docs/DEVIATIONS.md` D7, D11).
- **2024/25:** 7th of 21 single models (0.693). The CDC ensemble scored 0.673.
- **2025/26:** 19th of 25 single models (0.997), level with the baseline (`results/tables/league_table.csv`).
- **Including ensembles:** 13th of 41 and 40th of 46.

**12. "Be specific: where did it lose?"**
- **By season:** 2024/25 1.03 (0.89–1.25); 2025/26 1.52 (1.09–2.03).
- **By state:** NABD beat the ensemble in 18 of 53 locations in 2024/25 and in 0 of 53 in 2025/26 (`results/SUMMARY.md`, D6).
- **By phase, assigned at forecast time:** relative WIS 1.27 rising, 0.97 flat, 1.29 falling. Under-prediction is the largest error component (`results/SUMMARY.md`, D10).

**13. "The national series dominates your metric."**
- **The protocol defines the metric, so we report it as is.** The national series is 46.0% of NABD's WIS and 44.9% of the ensemble's.
- **Excluding it changes nothing:** 1.198 (CI 1.014–1.449), still NOT MET (`results/SUMMARY.md`, D6).

**14. "Did NABD even beat the naive baseline in the US?"**
- **On average yes, but not convincingly:** 0.82 (0.66–1.02). The CDC ensemble scored 0.67 on the same cells (`results/SUMMARY.md`).

**15. "Isn't 'better during surges' just spin?"**
- **We don't claim it.** That split (E1) used the realised truth, and its gain came from wider intervals.
- It is exploratory, and it appears in no headline (`docs/DEVIATIONS.md` E1).

**16. "Will you tweak and re-run until it passes?"**
- **No.** The protocol was frozen before any test score (`docs/FREEZE.md`, commit `ac16901`), and every change since is in `docs/DEVIATIONS.md`.
- **We disclose that early probes touched the test seasons before the freeze** (D5).
- **Any US v2 is judged only on forecasts made after it is locked** (`docs/PREREG-US-V2.md`, draft).

## D. Early warning and alerts

**17. "Lead time is zero. Where's the early warning?"**
- **Correct.** In the US, the median onset lead is 0 weeks for every rule: ours, the CDC ensemble's and a census threshold (`results/tables/alerts_us.csv`).
- **We don't sell "earlier".** We sell how big and how long, with a calibrated range.

**18. "Then what do the alerts buy? Alert fatigue?"**
- **US precision** (share of alerts followed by a real onset, at 3 per 100k, 2024/25 / 2025/26):
  - NABD 0.65 / 0.76;
  - CDC ensemble 0.41 / 0.67;
  - census rule 0.60 / 0.46.
- **UAE** (n = 4 seasons, descriptive):
  - influenza: NABD caught 3/3 onsets with 3/3 precision and 0 false alarms, against 2/3 for a census rule;
  - RSV: about 1/3 for every rule (`results/uae/tables/alerts_uae.csv`).
- **Caveat:** alert thresholds were informed by probes that had seen these seasons, so all alert metrics are diagnostic (`docs/DEVIATIONS.md` D3, D5; `docs/PROTOCOL-UAE-v2.md` §1).

**19. "What happens when a feed is late?"**
- **US:** one missing week raises error 1.41-fold (`results/tables/dropout_us.csv`).
- **UAE:** a missing latest week raises mean WIS by 0.14–0.26 percentage points. A missing non-sentinel week makes v2 fall back automatically to a smaller sub-model (`results/uae/tables/ablation.csv`).
- **The card shows a freshness badge with the exact lag.**

## E. Method

**20. "How do you know nothing leaks?"**
- **US:** each forecast uses only the hub data version available by the Wednesday deadline.
- **Tests:** a test injects future data and must fail (`tests/test_vintage.py`). The UAE test caught and fixed a real leak in our first build (`results/uae/SUMMARY.md`, integrity note).
- **Scorer check:** our WIS matches an independent implementation exactly on every cell (D9).
- **Locks:** UAE v2 and the Gulf scorer refuse to run if the locked code or plan changed (`assert_locked`).

**21. "How are your intervals calibrated?"**
- **US:** 95% coverage 0.92 vs the ensemble's 0.86 (`results/summary.json`). There is no online conformal step in v1; intervals use a fixed widening factor tuned on 2023/24.
- **Gulf:** influenza 95% coverage 0.96; RSV 0.83, which is too narrow (`results/gcc/SUMMARY.md`).

**22. "Is there any AI here beyond regression?"**
- **v1 is deliberately simple and auditable.** The Chronos-2 foundation-model wrapper exists but was not run, because its weights were unavailable in our build environment, so we claim nothing from it (`results/summary.json`).
- **The hard part is the rest:** leakage-free evaluation, calibration, transfer across countries, and a public record.

**23. "Your horizons say up to three weeks, but WHO data is about 10 days late."**
- **Horizons count from the issue date:** nowcast, +0.5, +1.5 and +2.5 weeks, and every ledger row carries the label. The measured lag on 8 Nov was 7 days for W44 (`data/raw/PROVENANCE.md`).

## F. Positioning and business

**24. "Abu Dhabi already has Tableegh, UMOC, Rasid and an ADPHC AI tender. Why you?"**
- **Those answer "is something emerging?"**: Tableegh notifies, UMOC runs early warning, Rasid watches wastewater, and the 2024 tender scope is outbreak detection.
- **NABD answers "how big will the known seasonal RSV and flu wave be over the next weeks, and how good has this forecast been?"** It is a feed they can host (`research/positioning.md` §3; `research/competitors.md`).
- **Rasid offer:** add its wastewater signal as an input and publish whether it helps.

**25. "Hospital command-centre tools already predict census."**
- **They work from inside-hospital data, up to about 72 hours ahead.** We forecast weeks ahead from community surveillance the hospital can't see. The two are complementary (`research/competitors.md`).

**26. "WHO FluNet is non-commercial. Is your business blocked?"**
- **No.** FluNet powers the public-health feed and the evaluation. A hospital product would run on the hospital's own aggregate data. Every source is declared (`pitch/registration.md`).

**27. "Who pays, and why would SEHA say yes?"**
- **Who pays:** hospital operations for winter bed and roster planning, and public health for a regional feed.
- **First step:** a 12-week shadow run on aggregate counts with no change to care. Success, defined in advance, is beating the hospital's own census carried forward.
- **Honest status:** no letter of interest yet.

**28. "What's defensible? Anyone can fit a regression."**
- **Not copyable:**
  - a dated, outside-anchored track record;
  - frozen protocols with their deviation logs;
  - a method already tested blind on three Gulf countries;
  - the approval and audit workflow a hospital signs off on.
- **The record gets more valuable every week it runs.**

## Curveballs
- **"Is this season unusual?"** DoH said in September that activity looks similar to the previous two seasons (`research/burden.md` #8). We sell variability, not crisis.
- **"Do you use patient data?"** No. We use aggregates only, the adapters reject person-level fields, and a test checks this (`tests/test_adapters.py`).
- **"Conflict of interest? MBZUAI is a co-creator."** The T&C has no conflict clause (`research/tc.md`). Institutional permission is ours to confirm: ⟨team status⟩.
- **"Are the timestamps real?"** Today they are local git commits we made ourselves. Outside anchors (OpenTimestamps, Zenodo) are set up in `ledger/ANCHOR.md` ⟦IF DONE: anchor receipt⟧. Until then, say "self-attested".
- **"Does NABD predict when to start infant RSV immunisation?"** No. The fact that RSV passed 10% before 1 Sep in 2 of 4 seasons is context from WHO data (`research/positioning.md` §1.4), not a prediction.
