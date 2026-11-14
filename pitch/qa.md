# Judge Q&A prep, round 4: hostile questions with answers that trace to files

**Rules:**
- Every number cites a file in `results/`, `research/` or `docs/`. Never improvise a number on stage.
- ⟦IF BUILT: …⟧ / ⟦IF DONE: …⟧ mark round-4 work in progress. If it isn't there on the day, say "in build" and stop.
- Keep each answer under about 30 seconds.
- **Order (BUILD-SPEC v1.7):** impact first; then the Gulf test (46% vs past-season patterns, secondary; 9% vs persistence, primary, met) → US "missed our bar; 7th of 21" → UAE parity caveat → live ledger as the pilot ask.
- The stop list (`research/positioning.md` §4.6) and the v1.7 BANNED list are binding. Never say: "published" or "public" ledger (until it is), "blind", "verified row-for-row", "fewer false alarms", unqualified "calibrated", "nobody publishes" without "to our knowledge", or the UAE "3/3 onsets".

**Numbers to know cold:**
- **2,189:** RSV admissions of children ≤5 at Tawam (SEHA), 2018–22 [S1] (`research/burden.md` #1).
- **Gulf test, flu** (`results/gcc/SUMMARY.md`):
  - vs seasonal analog (past-season patterns) **0.536 (0.464–0.616)**, i.e. **−46%** (pre-registered secondary);
  - vs persistence **0.914 (0.843–0.983)**, i.e. **−9%** (pre-registered primary, MET); 9 of 12 country-seasons won.
- **US** (`results/SUMMARY.md`; `results/tables/league_table.csv`):
  - vs CDC FluSight ensemble **1.22 (1.01–1.52)**, margin 1.15: **NOT MET**;
  - league, single models: **7th of 21** (2024/25), **19th of 25** (2025/26).
- **UAE own record, forward in time:** v1 vs persistence **1.002** (flu and RSV) (`results/uae/SUMMARY-v2.md`).

---

## A. The ten questions judges will ask first (from `docs/REVIEW-R3-judges.md` §6)

**1. "Your product ties with 'next week = this week' on the UAE, the one place you want to deploy. Why should Abu Dhabi use it?"**
- **The record:** on the UAE's own data, forward in time, v1 ties with persistence: 1.002 (`results/uae/SUMMARY-v2.md`).
- **Our reading, post hoc, so labelled:** UAE sentinel data in FluNet start in 2022.
  - The first forward fold (2023/24) trained on one season and lost badly: flu WIS 4.75 vs 2.21.
  - With ≥2 training seasons, flu won both folds (2.54 vs 2.66; 1.94 vs 3.08), and RSV split (1.31 vs 2.14 won; 2.30 vs 1.89 lost) (`results/uae/v2/tables/forward_wis_by_season.csv`).
- **The Gulf countries had history from 2015.** There, with the method frozen and the plan locked before download, it beat past-season patterns by 46% and last week by 9% for influenza.
- **The UAE now has four seasons**, and the live ledger tests that forward, every week.

**2. "Persistence is a straw man. Planners use last year's pattern. How do you do against that?"**
- **Influenza:** against a seasonal-analog forecast (training-season values at the target week; `docs/PREREG-GCC.md` §5), 0.536 (95% CI 0.464–0.616), i.e. 46% less error. This was a pre-registered secondary comparison, and it held below 0.6 in each of Oman, Qatar and Saudi Arabia.
- **RSV:** 0.685 (0.605–0.781). It is secondary and less robust, so we don't headline it (`results/gcc/SUMMARY.md`).
- **The primary bar** was the harder baseline, last week carried forward: 0.914, met.

**3. "The 80% band is 4.6–21.4%. What does my bed manager actually do differently on Monday?"**
- **They read one line, not the band.** In the 8 Nov round, for the week ending 15 Nov (+1 wk after issue), the card shows:
  - RSV: P(> 10%) = 51%, P(> 20%) = 13%, forecast path falling;
  - flu: P(> 15%) = 94%, P(> 30%) = 27%, falling (flu thresholds are 15% and 30%).
- **The playbook output:** "elevated, falling". For the bed manager that means no surge roster; plan stand-down of extra paediatric capacity if next week confirms the decline (`app/screenshots/01_weekly_card_en.png`; `playbook/playbook.yaml` v0.4.0, illustrative).
- **The value is not over-staffing into a declining wave**, and not under-preparing for a rising one.

**4. "Statement 06 is early warning. Your lead time is zero. Wrong statement?"**
- **Our lead is on size, not onset:** a range up to +3 weeks after issue, each forecast labelled by its target week (skill measured at a conservative 11-day lag).
- **Onset in the US:** at the primary threshold (3 per 100k), median onset lead is 0 weeks for every rule, the CDC ensemble's included (`results/tables/alerts_us.csv`).
- **Onset detection is already Tableegh and UMOC's job** in Abu Dhabi. How big the wave gets, and for how long, is the gap.
- **Alerts at 3 per 100k** (diagnostic, because the thresholds were informed by pre-freeze probes, `docs/DEVIATIONS.md` D3, D5):
  - every rule had 0 false alarms;
  - NABD's first alerts were less often late;
  - a simple census threshold caught more onsets in time in 2024/25 (28 vs 17 of 51), and NABD caught more in 2025/26 (29 vs 24 of 52) (`results/tables/alerts_us_detail.csv`).

**5. "Who in Abu Dhabi has looked at this? Has a clinician reviewed the playbook?"**
- **Honest status:** ⟨as of the day: no letter of interest yet / letter from …⟩.
- **The playbook is marked ILLUSTRATIVE** until a clinician and a public-health reviewer sign it off.
- **Requests are out:** to the Tawam RSV study authors (UAEU Department of Pediatrics) and to an ADPHC surveillance contact (`pitch/outreach.md`).
- **We won't imply an endorsement** we haven't been given.

**6. "Half the statement is *workforce*. Where is it?"**
- **We forecast the population wave and translate it into the hospital's two constraints, beds and staff.**
- The winter-planner page works from the hospital's own admissions, length of stay, beds, nursing headcount and the winter sickness-absence baseline its HR sets. It shows scenario bed-days, % of ward capacity, a staff-absence range and the net roster gap in AED, with an occupational-health role in the playbook.
- **Every number is labelled SCENARIO.**
- **The employer path is designed, not live:** a secure aggregation of sickness-absence counts across ≥10 employers, demonstrated on synthetic data and watermarked SIMULATED (`app/workforce.py`).
- **We don't fake absence data.** No credible public UAE respiratory-absence figure exists (`research/positioning.md` §1.6).
- **No individual, employment or disciplinary use.**

**7. "National sentinel positivity isn't hospital load. What evidence links the two?"**
- **None yet for Abu Dhabi, and we claim none.**
- **The same discipline runs on real hospital admissions in the US:** NHSN state admissions, where NABD ranked 7th of 21 single models in 2024/25 (`results/tables/league_table.csv`).
- **The pilot's job is to test the link on the hospital's own census,** with the exit criterion set now: relative WIS < 0.9 vs census carried forward (`docs/PILOT-DATA-SPEC.md`).

**8. "Your 'pre-registration' is a local git commit you made yourselves. Why believe the Gulf test?"**
- **The lock is self-attested today.**
- **What the record shows:**
  - the Gulf plan lock (`91005ce`, 12:08:47 UTC) precedes the data commit (`d013228`, 12:10:18 UTC);
  - the scorer refuses to run if any locked file changed (`assert_locked`);
  - an independent audit found no Gulf data anywhere in the workspace before the lock, and no leakage in the scorer (`docs/REVIEW-R3-audit.md` §0).
- ⟦IF DONE⟧ **The manifests were anchored on ⟨date⟩, after the result.** We say "after" because it is.
- **From now on, the live ledger is anchored before WHO publishes each target week.**

**9. "Your multi-signal model got *worse*. Doesn't that fail requirement 1?"**
- **We tested fusion under a locked protocol:** non-sentinel lab data, testing volume, school breaks and Ramadan.
- **It didn't help on four seasons:** 1.059 (CI 1.016–1.111) (`results/uae/SUMMARY-v2.md`). Removing non-sentinel or calendar inputs slightly *improved* it (`results/uae/tables/ablation.csv`).
- **We ship what works.** Shipping the worse model to tick a box would be the irresponsible choice.
- **v2 keeps running in the ledger as a challenger**, and Rasid's wastewater signal is the next input to test, published either way.

**10. "Who pays, how much, and don't WHO's non-commercial terms and the organiser's right of first refusal kill this?"**
- **Pricing hypothesis, not a quote:**
  - a public-health forecast-feed licence per country per season;
  - a hospital-operations seat per facility.
  - The bar for a hospital seat is that it costs less than a handful of avoided paediatric admissions per season. The median RSV admission cost is US$2,241 in Dubai claims data [S3].
- **WHO data:** FluNet powers only the public-health feed and the evaluation. A hospital product runs on the hospital's own aggregate data.
- **Right of first refusal:** the code is under an open, non-exclusive licence. Any *exclusive* deal must first go to the organiser for 6 months after the Hackathon (T&C ROFR, `research/tc.md`).

---

## B. The Gulf test (our headline evidence)

**11. "What exactly did you test on the Gulf?"**
- **Setup:** we froze the UAE method, then wrote and locked the plan: country inclusion rules, comparators and the pass bar. Only then did we download Oman, Qatar, Saudi Arabia, Bahrain and Kuwait data (`docs/PREREG-GCC.md`; `docs/LOCK-GCC.json`).
- **Forward in time:** each season learns only from that country's own earlier seasons. There is no UAE data and no pooling.
- **Influenza results:**
  - primary, vs persistence: 0.914 (0.843–0.983), **met**;
  - secondary, vs seasonal analog: 0.536.
- **Robustness:** leave-one-country-out gives 0.904–0.929; a country-clustered bootstrap gives 0.841–0.984 (`docs/REVIEW-R3-audit.md` §0).

**12. "Where did it lose?"**
- **Influenza:** Oman 2022/23 and 2024/25, and a tie in Qatar 2023/24.
- **RSV:** Saudi Arabia 2025/26 (1.088 for the country) (`results/gcc/SUMMARY.md`).

**13. "And RSV?"**
- **It is a secondary outcome:** 0.798 vs persistence on the registered country-season bootstrap.
- **Clustered by country, its interval crosses 1** (0.712–1.026), and its 95% interval coverage is 0.83, which is too narrow (`docs/REVIEW-R3-audit.md` finding 9; `results/gcc/SUMMARY.md`).
- **So we don't headline it.**

**14. "Why only three countries?"**
- The inclusion rule was set before download. Bahrain and Kuwait each had one scorable influenza season, so the rule excluded them (`results/gcc/SUMMARY.md`).
- Oman and Qatar report a combined stream rather than separate sentinel data, and we note that (`pitch/assumptions-limitations.md` A7).

**15. "Was it really blind? You chose v1 after seeing the UAE results."**
- **True, and disclosed** (`docs/PREREG-GCC.md` §1). We call it *out-of-sample with the plan locked before download*, not "blind".
- **Our records show no one on the team had used the Gulf countries' data before.** An independent filesystem and git search found none (`docs/REVIEW-R3-audit.md` §0).

**16. "The data came from a GitHub mirror?"**
- **What it is:** WHO's full FluNet export (3 Oct 2026), obtained through a public mirror.
- **Cross-checks:** it matches our independently fetched UAE rows exactly (419/419), and 23 of 23 spot-checked Gulf rows (`docs/DEVIATIONS.md` G1, G1b).
- **A full official re-pull** is pending, via `python -m adapters.gcc_verify` (`docs/RUNBOOK.md`). ⟦IF DONE: "re-pulled ⟨date⟩, identical"⟧

**17. "Retrospective data. Isn't this just a back-test?"**
- **Yes:** these are revised FluNet values, so it is retrospective.
- **What makes it more than an ordinary back-test:** the countries were unseen and the plan was fixed before download.
- **The truly prospective test** is the live ledger.

## B2. Borrowed strength (S1) and the decision replays

**"Your UAE result is only a tie. Why should we believe this works here?"**
- On the UAE's own record it is a tie (1.002), and we say so. The UAE has four seasons of sentinel data, and the own-record method needs more.
- So we tested the fix on countries we had never opened: a model pooled across countries' WHO histories vs each country's own-record model. **0.767 (95% CI 0.681–0.832), better in 18 of 18; 0.624 where the record was short** (`results/pool/SUMMARY.md`). Plan locked before download, model locked before extraction, scored once.
- For the UAE itself the pooled model reads 0.87 vs the own-record model, but **that figure is non-confirmatory** (we had already seen UAE data). The confirmatory UAE evidence can only come from the live ledger, where the pooled model now runs as a challenger.

**"18 of 36 countries. Did you drop the ones that looked bad?"**
- No. The inclusion rules (reporting completeness, specimen volume, at least two earlier seasons) were fixed in the locked plan before any of those countries' data existed on our disk, and applied mechanically. The summary lists all 18 exclusions with the reason; most had no qualifying evaluation season.

**"Does less forecast error change a decision?"**
- Partly, and we show both sides. Replaying a fixed roster rule on the same held-out forecasts (post hoc): the pooled model had **10.5 mismatch weeks a season vs 12.3** for the own-record model (−1.81, 95% CI −3.00 to −0.72) and 16.6 for the past-season pattern.
- But against simply carrying last week forward it was **not distinguishable** (11.1; −0.56, CI −1.42 to +0.31), and it missed slightly more surge weeks than the own-record model (2.7 vs 2.2 a season) while wasting fewer (`results/replay/pool/SUMMARY.md`).
- That is why the pilot's exit criterion is set against the hospital's own census carried forward.

## C. The US stress test

**18. "You didn't meet your own bar against the CDC. Why are you here?"**
- **We set the bar at the best public forecaster and froze the test first:** 1.22 (1.01–1.52) vs a 1.15 margin, NOT MET (`results/SUMMARY.md`).
- **Among individual CDC-hub models:**
  - 2024/25: 7th of 21 (0.693; the CDC ensemble scored 0.673);
  - 2025/26: 19th of 25 (level with the baseline).
  - Including ensembles: 13th of 41 and 40th of 46 (`results/tables/league_table.csv`).
- **Our losses are on the record,** which is how you know the other numbers weren't tuned until they looked good.

**19. "Be specific: where did it lose?"**
- **By season:** 2024/25 1.03; 2025/26 1.52.
- **By location:** it beat the ensemble in 18 of 53 locations in 2024/25 and in 0 of 53 in 2025/26 (`results/SUMMARY.md` D6).
- **By as-of phase:** 1.27 rising, 0.97 flat, 1.29 falling. Under-prediction is the largest error component (D10).

**20. "The national series dominates your metric."**
- It is 46.0% of NABD's WIS. Excluding it: 1.198 (1.014–1.449), still NOT MET (D6).

**21. "Will you tweak and re-run until it passes?"**
- **No.** The protocol was frozen before any test score (`docs/FREEZE.md`), and every change since is in `docs/DEVIATIONS.md`.
- **Disclosed:** early probes touched the US test seasons before the freeze (D5).
- **Any US v2 is judged only prospectively,** after a lock (`docs/PREREG-US-V2.md`, draft).

## D. Method

**22. "How do you know nothing leaks?"**
- **US vintage rule:** each forecast uses only the hub data version available at the Wednesday deadline. A test injects future data and must fail (`tests/test_vintage.py`).
- **UAE:** the leakage test caught and fixed a real boundary leak in our first build (`results/uae/SUMMARY.md`).
- **Gulf scorer:** an independent audit perturbed every post-origin value in 2,112 cases, and 0 forecasts changed (`docs/REVIEW-R3-audit.md` §0).
- **Scorer cross-check:** our WIS equals an independent implementation exactly (D9).

**23. "Are your intervals calibrated?"**
- **We check and report coverage; it isn't perfect.**
- **95% intervals actually contain the outcome:**
  - US: 0.92 for NABD vs 0.86 for the ensemble (`results/summary.json`);
  - Gulf influenza: 0.96;
  - Gulf RSV: 0.83, which is too narrow (`results/gcc/SUMMARY.md`).
- **v1 uses no online conformal step.**

**24. "Is there any AI here beyond regression?"**
- **v1 is deliberately simple and auditable.** The Chronos-2 wrapper exists but was not run (no weights in our build environment), so we claim nothing from it.
- **The hard parts:**
  - leakage-free, vintage-correct evaluation;
  - transfer to three countries under a locked plan;
  - a hashed forecast record;
  - an approval workflow with consistency checks.
- **The MBZUAI-level contribution** is that evaluation and transfer discipline, not the model.

**25. "Your horizons say three weeks, but WHO data are late."**
- **Forecasts run from the nowcast to +3 weeks after issue, each labelled by its target week-ending date,** with skill measured at a conservative 11-day publication lag. The measured lag on 8 Nov was 7 days (`data/raw/PROVENANCE.md`).
- **One convention everywhere:** the card, bulletin, API, planner and ledger all label by week ending, with "+1/+2/+3 wk after issue" as the secondary label, the same as the hashed R0/R1 rounds (`docs/DEVIATIONS.md` C8).

## E. Positioning, governance and business

**26. "Abu Dhabi already has Tableegh, UMOC, Rasid and an ADPHC AI tender. Why you?"**
- **Those answer "is something emerging?"**
- **NABD answers "how big will the known seasonal RSV and flu wave be over the next weeks, and how good has this forecast been?"** It is a feed they can host (`research/positioning.md` §3; `research/competitors.md`).
- **Rasid:** we offer to add its wastewater signal as an input and publish whether it helps.

**27. "Hospital command-centre tools already predict census."**
- **They work from inside-hospital data, up to about 72 hours ahead.** We forecast weeks ahead from community surveillance (`research/competitors.md`). The two are complementary.

**28. "Data sovereignty?"**
- **Aggregate weekly counts only.** No identifiers, with k ≥ 10 complementary suppression enforced by the connector's schema.
- **Built for in-country hosting**, with an ADHICS / DoH data-standards checklist (`docs/PILOT-DATA-SPEC.md` §4).
- **Nothing person-level enters any path** (`tests/test_adapters.py`).

**29. "Why not leave this to the Gulf CDC or WHO EMRO?"**
- **Complementary.** The Gulf CDC's regional system is at the pilot stage, with acute respiratory infection as a weekly-reported pilot disease [S23].
- **NABD is FluNet-native and has transferred to three Gulf countries under a locked test.** It is a forecast layer any regional system can consume.

**30. "What's defensible? Anyone can fit a regression."**
- **What can't be copied:**
  - a dated forecast record that can't be backdated, once it is anchored outside the team ⟦IF DONE⟧;
  - frozen protocols with their deviation logs;
  - a method tested out of sample on three Gulf countries;
  - the approval and audit workflow a hospital signs off on.

## Curveballs
- **"Is this season unusual?"** DoH said in September that activity looks similar to the previous two seasons [S7]. We sell recurring variability, not crisis.
- **"Do you use patient data?"** No. We use aggregates only, the adapters reject person-level fields, and a test checks this.
- **"Conflict of interest? MBZUAI is a co-creator."** The T&C has no conflict clause (`research/tc.md`). Institutional permission: ⟨team status⟩.
- **"Does NABD predict when to start infant RSV immunisation?"** No. RSV passing 10% before 1 Sep in 2 of 4 seasons is context from WHO data, not a prediction [S4 secondary; DATA].
- **"Is the ledger public?"** ⟦IF DONE: "Yes, at ⟨URL⟩, anchored ⟨date⟩."⟧ Otherwise: "Not yet. It is hashed and committed locally, and it will be public and externally timestamped from ⟨date⟩."
