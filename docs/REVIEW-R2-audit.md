# REVIEW R2: Integrity and reproducibility audit (independent)

Auditor: independent reviewer agent, 8 Nov 2026 (UTC). Repo HEAD audited: `4675687`. Hub: `d03574028ece110013c6284d3012ac4bef03ded7`.
Scope: freeze integrity, reproduction, leakage, scoring, gates G1–G11, overclaims. The only file written to the repo is this one. All reruns were done in scratch clones under /tmp.

## 0. What I ran and what held up

| Check | Result |
|---|---|
| `git log`/`git show`: PROTOCOL.md (`ac16901`, 06:47:00Z) before config (`fd8608b`, 06:56:04Z) before any test result (`e6333d1`, 06:58:01Z) | Order holds. PROTOCOL.md has exactly one commit. Current SHA-256 = FREEZE.md value `2846533f…`. No result file in git before `e6333d1`. |
| Clean clone + hub symlink, `python -m eval.run_all --cached` (22 s) | `results/SUMMARY.md`, `summary.json`, `tables/endpoints.csv`, `alerts_us.csv`, `exploratory_phase.csv`, `dropout_us.csv`, `alerts_summary.json` and all `results/forecasts/**` are **byte-identical** to the committed files. |
| Truly clean clone (no `external/`), `run_all --cached` (clones the hub, 30 s) | Byte-identical headline files. |
| `run_all --cached --retune` (4.5 min) | `models/config.yaml` reproduced exactly (only `tuning_runtime_sec` differs). |
| `python -m uae.backtest --cached` (12 s) | `summary.json`, `scores_long.csv`, `wis_by_season.csv` and forecasts are byte-identical. `SUMMARY.md` differs only because a hand-written "Integrity note" is lost on regeneration (see m4). |
| `pytest -q` | 52 passed. |
| Vintage rule vs CDC reality | For 6 rounds (2024-01-13 … 2026-02-14), the vintage the rule picks reproduces the FluSight-baseline h0 median (the real-time last value) in **100%** of locations. The hub README says pre-2025-07-05 `as_of` = reference date of the release; the empirical match shows the rule is right anyway. |
| Adversarial US leak test (`/tmp/audit/leak_us.py`): every vintage with `as_of > R−3` multiplied by 7 and shifted by +12345; `final_truth()` replaced by a function that raises | 7/7 test dates unchanged; final truth never touched. Positive control (perturb the chosen vintage) changes the forecast. **No leak.** |
| Adversarial UAE leak test (`/tmp/audit/leak_uae.py`): 240 (series × season × model × origin) cases, all held-out-season values after the origin randomised, training set = all other seasons (as in the backtest) | 0 changes. **No leak** within the LOSO design. |
| WIS | `eval/wis.py` matches Bracher et al. (2021): weights w0 = 1/2 and w_k = α_k/2, divided by (K + ½) with K = 11. The pinball identity 2·Σ PL / 23 is algebraically exact (checked by hand). Quantile set = the FluSight 23. |
| Common cells / fairness | Pairwise intersection of complete 23-quantile cells; same final truth for all models. 55 of 56 dates scored (hub has no 2025-01-25 round). NABD is *disadvantaged* in the 5 stale rounds, where the hub archive lacks the vintage CDC teams actually had. The comparison is fair. |
| D4 duplicate claim | Verified: only vintage 2026-05-27 has duplicates (23,850 rows), with 0 conflicting keys. |
| G7 spot-check | Tawam RSV figures (2,189 hospitalisations; 15,326 children; 2.9%/16% positivity; 5.8 days) confirmed on the UAEU research record. |

## 1. Gate table

| Gate | Verdict | Evidence |
|---|---|---|
| G1 Protocol integrity | **PARTIAL** | The order, hash and single protocol commit are verified, and D1–D4 are logged. But the pre-freeze test-season exposure is undisclosed (M1), and the freeze is anchored only in local git, with no public timestamp (M2). |
| G2 Reproducible pipeline | **PASS** | Byte-identical regeneration from a clean clone in 22–30 s; retune reproduces config. Minor robustness gaps in m1–m2. |
| G3 Primary endpoint honest | **PASS** | 1.223 (1.011–1.521), NOT MET. Vintage, truth and common cells verified. Concentration (M3) and bootstrap dependence (M5) are reporting gaps, not errors. |
| G4 UAE track | **PASS (with caveats)** | LOSO n = 4 is stated; the ledger R0 hash verifies. The UAE design is not pre-registered and uses revised data (M6). R0 is `public: false`. |
| G5 Working app | **PARTIAL** | The app renders with 0 exceptions. The US proof page **does not display the verdict** (C3). The feed-removal page shows DEMO placeholders. Docker was not built. |
| G6 Tests | **PASS** | 52/52 pass. Gaps: no later-vintage (revision) injection test; the negative control does not exercise the forecast path; the WIS reference is a hand-made toy (m7, m8). |
| G7 Evidence | **PASS** | burden.md has verified sources (spot-checked); emails are drafted; tc.md exists. |
| G8 Pitch | **FAIL** | deck-script.md, demo-script.md and qa.md still contain ⟦RESULT⟧ slots for results that exist. Some prepared answers are false (C2). |
| G9 Honesty | **FAIL** | The registration text, deck and Q&A claim signals, models and features that are not in the shipped system (C1, C2). |
| G10 Alert metrics | **PARTIAL** | The US part is done and reproduces. The UAE part is missing. The rule was shaped by a test-season probe (M1). |
| G11 Explainability | **FAIL** | The card's "drivers" are self-labelled "descriptive context, not model attributions". No feed-removal deltas or per-feature contributions are rendered. The ablation page is DEMO (M8). |

## 2. Findings

### CRITICAL

**1. CRITICAL: the registration text and deck claim inputs and models that NABD does not have.**
- **Where:**
  - pitch/registration.md:7, :15, :18–23, :35–41, :43;
  - pitch/deck-script.md:25–34 (slide 4) and :37 (slide 5).
- **What is claimed:**
  - "fuses surveillance, ED, environmental and administrative signals";
  - "five kinds of signal … emergency-department syndromic; geospatial; environmental (weather)";
  - "fusing signals where real data exist: … ED syndromic data by region; Abu Dhabi weather";
  - "a time-series foundation model are combined into a calibrated quantile ensemble";
  - "card shows … the signals, weeks and regions that drove them";
  - "online calibration";
  - "multi-signal ✓; explainable alerts (signal, location and week contributions) ✓".
- **Evidence:**
  - The US models (models/engine.py:234–247) use only NHSN admissions (`series_as_of`).
  - The UAE model (uae/models.py:13–16) uses only FluNet positivity and testing volume.
  - No adapter or model reads NSSP/ED data. Weather is a NOT-REAL placeholder (data/raw/PROVENANCE.md; adapters/weather.py). The school calendar enters no model.
  - Chronos-2 is NOT RUN (config.yaml `chronos2:`). ACI is not used (config.yaml `aci:`; PROTOCOL §8 l.73).
  - The drivers panel is labelled "not model attributions" (app/streamlit_app.py:157).
  - pitch/registration.md:43 says the evaluation is "pre-registered", which covers UAE skill and surge alerts. Only US-A was pre-registered. D3 was added after the freeze, and there is no UAE protocol.
- **Why it matters:** the registration is due 10 Nov and goes to the organiser. The "all data sources must be declared" T&C makes this a declared-sources misstatement.
- **Fix:** rewrite to what exists:
  - US: NHSN admissions only (damped log-linear GLM + empirical-quantile ensemble).
  - UAE: FluNet positivity + testing volume.
  - ED, weather and school-calendar signals: "planned / adapter scaffolded, not used in v1".
  - Chronos-2: "wrapper, not evaluated".
  - Drivers: "descriptive context".
  - "Pre-registered" applies to the US non-inferiority test only.

**2. CRITICAL: prepared judge answers are false or contradict the NOT MET result.**
- **Q&A #11 (pitch/qa.md:40):** says intervals are calibrated "through online adaptive conformal adjustment on each target series". This contradicts models/config.yaml (`aci: not used in v1 frozen run; fixed widening k only`) and PROTOCOL.md:73. The true answer: the NB dispersion and the empirical log-error quantiles are tuned on 2023/24, plus a fixed widening k = 1.1.
- **Q&A #8 (qa.md:31):** "Matching it within a margin … shows the method transfers". NABD did **not** match within the margin (1.223 > 1.15 even at the point estimate).
- **Q&A #2 (qa.md:11):** claims US results "on US admissions and ED share". There is no ED-share track (US-B is not implemented).
- **Q&A #6 (qa.md:25):** "102 weekly real-time versions". The 102 vintages are not weekly: there are gaps, e.g. 2024-04-27 → 2024-11-16.
- **Fix:**
  - Rewrite #8 around the actual result: 1.223 (1.011–1.521); worse than the ensemble in every state (see M3); 95% coverage 0.918; vs baseline 0.816 (CI to 1.023).
  - Fix #11 and #2 as above.
  - Fill every ⟦RESULT⟧ from results/summary.json.

**3. CRITICAL: the app's US proof page never shows the primary verdict.**
- **Where:** app/streamlit_app.py:213–216.
- **What happens:** the code looks for a key containing "verdict" in results/summary.json. The real file has `primary.non_inferiority` and no "verdict" key, so the card is skipped. The page text (l.211–212) still says "The verdict below is shown **verbatim**". The JSON is rendered collapsed (`expanded=False`).
- **Evidence:** AppTest on the "US proof" page: "NOT MET" appears in no markdown element; both `st.json` blocks are collapsed.
- **Related:** the About page (l.321) still says non-inferiority "may fail". The US proof table list also shows `exploratory_phase` (E1, rising-phase 0.893) with no EXPLORATORY label.
- **Why it matters:** in the judged artefact, the negative primary result is effectively hidden while an outcome-conditioned favourable number is shown.
- **Fix:**
  - Read `summary["primary"]` and render a card: "relative WIS 1.223 (95% CI 1.011–1.521), margin 1.15: NOT MET".
  - Change l.321 to "Non-inferiority was NOT MET (see US proof)".
  - Label or omit exploratory_phase.
  - Add an AppTest asserting "NOT MET" is visible.

### MAJOR

**4. MAJOR: pre-freeze exposure to the test seasons is not disclosed (G1, G10).**
- **Where:**
  - docs/FREEZE.md:11;
  - docs/DEVIATIONS.md:7 (D3, "Test results seen? No");
  - eval/lead_time_probe.py:35–37 and :117–121;
  - eval/ensemble_vs_persistence.py;
  - docs/SPEC.md:30 and :224–225.
- **Evidence:**
  - Before the freeze (scaffold commit `6c925cd`, 06:43Z), the team ran probes over 2024/25 and 2025/26. One scored the FluSight-ensemble vs baseline per season and horizon.
  - The other evaluated a log-linear growth forecaster: the same family as the NABD point model, 3-week window, and the tuned w = 3. It swept census fractions 0.3–1.0 and forecast thresholds on test-season truth with T = 2/3/5.
  - D3 later fixed exactly T ∈ {2, 3, 5}, the 2-consecutive-week onset, the 4-week window and census fraction 0.6.
  - FREEZE.md's statement ("no test-season score of any NABD model") is literally true but incomplete.
- **Fix:** add a DEVIATIONS/FREEZE "Prior exposure" entry. It should list both probes, the seasons they touched, that the point-model family and the D3 thresholds were chosen after seeing them, and that the census fraction came from a sweep that included the test seasons. Mark G10 US alert metrics as "rule informed by test-season probe".

**5. MAJOR: the freeze is unverifiable by a third party.**
- **Where:** docs/FREEZE.md; git metadata.
- **Evidence:**
  - All 20 commits share one author, "NABD build <nabd-build@local>", and span 06:43:32–07:04:37Z (21 min). PROTOCOL and FREEZE carry the same second.
  - Commit dates are self-asserted, and nothing was pushed or timestamped externally before results existed. FREEZE.md itself says the team "should push".
  - The ordering is plausible: the tune runtime (281.7 s) fits the a1c76e1 → fd8608b gap, and R0 meta (06:51:11) fits 463ab09 (06:51:29). But it cannot be proven.
- **Fix:**
  - Call it an "internal pre-registration (local git)" in the pitch, not "publicly timestamped".
  - Push now and record that the public anchor post-dates the results.
  - For the 2026/27 ledger and any v2 protocol, push or OpenTimestamp *before* issuing.

**6. MAJOR: the primary metric is dominated by the national series, and NABD loses in every state.**
- **Where:** results/SUMMARY.md:3; eval/score.py:147; my analysis `/tmp/audit/mbb.py`.
- **Evidence:**
  - The `US` location (the sum of the states, so double-counted) contributes **46%** of NABD's total WIS and **51%** of its excess WIS over the FluSight-ensemble.
  - States-only (exploratory): 1.198 (date-bootstrap 1.015–1.44).
  - Per-location ratio of WIS sums: NABD is worse than the FluSight-ensemble in **52/52** state-level locations. The best is NH at 1.007; the median is 1.217. By season: 18/52 better in 2024/25, **0/52** in 2025/26.
- **Why it matters:** this is the protocol's metric, so no deviation is needed. But it undercuts any "competitive" framing and belongs in SUMMARY.md.
- **Fix:** add an EXPLORATORY row (E2) with states-only relative WIS and the per-location win count. State it in the pitch.

**7. MAJOR: E1 "better than the ensemble during surges" is outcome-conditioned, and its own table contradicts the stated mechanism.**
- **Where:** docs/DEVIATIONS.md:14; docs/BUILD-LOG.md:90 and :103; eval/exploratory.py:17–18.
- **Evidence:**
  - Phases are defined from realised truth vs the last observation. Any model with wider or upper-skewed intervals looks good in "rising" and bad in "falling" cells.
  - In rising cells, NABD's median log-bias is **−0.921**, worse than the FluSight-ensemble's −0.748 (results/tables/exploratory_phase.csv). So "NABD's damped-trend core does well in surges" is not what the numbers show; the WIS gain comes from interval width.
  - The CI uses the i.i.d.-date bootstrap (see M5).
- **Fix:**
  - Remove "better than the ensemble during surges" from the defensible-claims list (BUILD-LOG:103) and from any slide.
  - Reword E1's interpretation to cite the bias column.
  - If it is kept at all, describe it as hypothesis-generating only.

**8. MAJOR: the bootstrap ignores serial dependence, so CIs on favourable claims are optimistic.**
- **Where:**
  - eval/score.py:67–74 (`boot_ratio`);
  - uae/backtest.py:84–98;
  - PROTOCOL.md:44 (calls single-date resampling a "block bootstrap").
- **Evidence:**
  - Adjacent reference dates share 3 of 4 target weeks.
  - A within-season moving-block bootstrap gives: primary 0.99–1.57 at L = 4 and 0.995–1.63 at L = 6, vs 1.011–1.521 reported; S1 0.607–1.035 at L = 4.
  - The verdict is unchanged (the point estimate is above 1.15). But the UAE CIs (e.g. 0.70–0.82) and the E1 CI are narrower than warranted.
- **Fix:** keep the protocol analysis, and add a labelled sensitivity with a moving-block bootstrap (L = 4, within season) for primary, S1, E1 and UAE. Rename "block bootstrap" to "cluster (date) bootstrap" in SUMMARY.md and the app.

**9. MAJOR: the UAE skill figures come from a design-stage retrospective with optimistic biases, but are presented alongside "pre-registered".**
- **Where:** uae/backtest.py:6–11; uae/models.py:10–17; results/uae/SUMMARY.md:3–5; pitch/registration.md:43–46.
- **Evidence:**
  - There is no UAE protocol or freeze. The features, the ±2-week climatology smoothing, the continuity correction and the testing-volume covariate were chosen with all four seasons visible. The model was revised and re-run after a leak fix (463ab09).
  - LOSO trains on future seasons, including partial 2026/27.
  - Inputs are latest-revised FluNet values, not vintages (stated in SUMMARY caveats).
  - Relative WIS pools the nowcast horizon (−1).
  - These figures are honest as labelled in results/uae, but not as "pre-registered" in the registration text.
- **Fix:** label them "retrospective, design-stage, not pre-registered". Report per-horizon relative WIS (vs persistence: flu 0.90/0.82/0.73/0.67, RSV 0.94/0.85/0.73/0.68 for h −1..2). Pre-register a frozen NABD-UAE-v1 for the live 2026/27 ledger.

**10. MAJOR: G8 is incomplete, and the demo script promises features that don't exist.**
- **Where:**
  - pitch/deck-script.md:37, :43–46, :52–54;
  - pitch/demo-script.md:9–14;
  - pitch/qa.md:11, :17, :28, :34, :40.
- **Evidence:**
  - ⟦RESULT⟧ slots remain although results/ is complete.
  - demo-script.md:10 "Click **Explain** … which signals, weeks and regions drove this forecast": no such view exists.
  - demo-script.md:14 "Toggle **remove ED feed** … interval widens by ⟦RESULT⟧": no ED feed exists, and the feed-removal page is DEMO.
- **Fix:**
  - Fill the slots from results/summary.json, results/tables/alerts_us.csv and results/uae/summary.json.
  - Replace the Explain/ED beats with what exists: the freshness badge, persistence overlay, approve/audit flow, and the 1–2-week input-delay result from dropout_us.csv (WIS ×1.41 / ×1.82).

**11. MAJOR: G11 (explainability) is not implemented.**
- **Where:** app/streamlit_app.py:106–118, :157, :276–291; app/demo_data.py:91–97.
- **Evidence:**
  - The drivers are last-3-weeks values, testing-volume change, historical peak weeks and a calendar line. None comes from the model.
  - The ablation page reads `results/tables/ablation*.csv`, which does not exist, so it shows placeholders for feeds no model uses (NSSP, weather, school calendar).
  - `results/tables/dropout_us.csv` exists but is not rendered.
- **Fix:** for NABD-UAE-v1 (linear in 4 features), render per-feature contributions `beta_h · x` for each card. Run a real UAE feature-removal ablation (drop `dlogspec`, drop `dclim`/climatology) into `results/uae/tables/ablation.csv`. Wire dropout_us.csv into the page. Remove demo feeds that don't exist.

**12. MAJOR: G10 UAE alert metrics are missing.**
- **Where:** docs/DEVIATIONS.md:7 ("UAE alert part belongs to the UAE workstream"); there is no alert code in uae/.
- **Fix:** pre-specify the UAE onset rule first (e.g. positivity ≥ 15% for two consecutive weeks, as in eval/backtest_probe.py:13–15), log it as a deviation, then report descriptive lead/sensitivity/PPV/false alarms for n = 4.

**13. MAJOR: the headline "21–36%" belongs to the CDC ensemble, and it and "155 state-seasons" do not trace to results/.**
- **Where:** pitch/deck-script.md:19–20; pitch/qa.md:17; docs/SPEC.md:224–225.
- **Evidence:**
  - Re-running eval/ensemble_vs_persistence.py reproduces FluSight-ensemble/baseline 0.64–0.79 by season × horizon. That is the CDC ensemble, not NABD. NABD's own figure is 0.816 (0.655–1.023).
  - The probe outputs (`eval/results/*.csv`) are not committed.
  - lead_time_probe.py reads `eval/data/flusight/time-series.csv`, which is not in the repo, so "155 state-seasons" cannot be regenerated as shipped.
- **Fix:**
  - Say "the CDC ensemble cut error 21–36% vs persistence; NABD cut it 18% (CI includes 0%)".
  - Point the probes at `external/hub`, write outputs to `results/probes/`, and commit them.

### MINOR

**14. MINOR: `--cached` can fetch, and the hub pin is not enforced.**
- **Where:** eval/run_all.py:28 and :42–43; .gitignore:4.
- **Evidence:** `external/` is git-ignored, so a clean checkout with `--cached` clones from GitHub. `checkout HUB_SHA` runs with `check=False`, and an existing cached hub is never verified, so a different hub version would silently change the truth and the results.
- **Fix:** use `check=True`, and assert `git -C external/hub rev-parse HEAD == HUB_SHA` (or hash `time-series.csv`) before scoring. Make `--cached` fail if the hub is missing.

**15. MINOR: the protocol's rerun description does not match run_all.** PROTOCOL.md:97 says run_all reruns steps 2–4, but tuning is skipped unless `--retune` (eval/run_all.py:45). Fix: correct the wording in a DEVIATIONS note, or document `make retune`.

**16. MINOR: tuning notes are hard-coded.** eval/tune.py:135 writes the "grid edges w=3 …" note whatever values are selected. Fix: generate the note from the selected values.

**17. MINOR: regenerating the UAE summary deletes a hand-written note.** The "Integrity note" in results/uae/SUMMARY.md:55–56 was added by hand, so regeneration removes it (a reproduction diff). Fix: emit it from `write_summary_md`.

**18. MINOR: UAE per-model and per-season tables mix cell sets.** uae/backtest.py:138–142 averages over different cells: NABD 1480, persistence 1520, analog 1528. NABD skips season-start origins. I recomputed on common cells: all season-win counts and conclusions are unchanged. Fix: restrict to common cells.

**19. MINOR: the ledger's data-through week is overwritten.** At ledger/issue.py:72, `data_through` is overwritten inside the per-series loop, so the RSV value is written for both series. Fix: store it per series.

**20. MINOR: the vintage tests miss revisions and have a weak negative control.**
- **Where:** tests/test_vintage.py:24–58.
- **Evidence:** the tests only inject future weeks into the *same* vintage. Nothing checks that later vintages (revisions or final truth) cannot enter. The negative control never shows the forecast-level test failing.
- **Fix:** add the later-vintage perturbation test (`/tmp/audit/leak_us.py` logic) and a positive control that patches the cutoff to R and asserts the forecast test fails.

**21. MINOR: the WIS reference test is a hand-made toy.** tests/test_wis.py:13–20 uses a 3-quantile example. Fix: add one fixed 23-quantile case whose WIS was computed with `scoringutils` / hubEvals and stored as a constant.

**22. MINOR: the burden figures span a COVID year.**
- **Where:** pitch/deck-script.md:13; pitch/registration.md:18 and :33.
- **Evidence:** "positivity from 2.9% to 16%" runs from 2020 (COVID NPI year) to 2021 (rebound). A public-health judge will attribute the swing to the pandemic, not normal variability. The UAE RSV peak weeks 42/41/41/47 do check out against data/raw/flunet_are.csv.
- **Fix:** add "(2020–21, pandemic-affected)", or lead with the peak-week spread.

**23. MINOR: the proof screenshot shows DEMO data.** app/screenshots/02_proof.png was committed (93f5862, 06:57:41Z) before results existed (06:58:01Z), so it shows DEMO. Fix: retake it after fixing C3.

**24. MINOR: the cached UAE data have no machine provenance.** data/raw/flunet_are.csv came in via WebFetch, with the W43/W44 rows hand-added (PROVENANCE.md). Fix: run `python -m adapters.flunet --fetch --save` locally, diff, and commit before submission.

**25. MINOR: interpolation creates smooth values over a reporting gap.** models/data.py:78 linearly interpolates 17 weeks (2024-05-18 … 2024-10-05) for 3 locations. These artificially smooth values feed the EEQ error pool (H = 104). Fix: mask interpolated cells from `eeq_*` error pools, or log the choice as a D-entry.

**26. MINOR: the seasonal slope's implementation is undocumented.** models/point.py:49–64 computes g_sea from row offsets 52/104 and the following 4-week growth. PROTOCOL §8 says "same epiweek in previous seasons". Fix: document the interpretation in DEVIATIONS (as D2 does).

**27. MINOR: an unsupported comparative claim.** docs/SPEC.md:80 says "Most competing 06 entries are simulated", with no source. Fix: delete it or source it.

**28. MINOR: "lead 0" needs explaining.** results/tables/alerts_us.csv: median lead 0 means the onset week ends on R, i.e. about 3 days after the Wednesday issue. Fix: say "≈ +0.5 week" in the pitch. Do not call it early warning; the alert sensitivity of NABD (0.33) is below the census rule (0.55) in 2024/25.

## 3. Scratch artefacts (not committed)
`/tmp/audit/leak_us.py`, `/tmp/audit/leak_uae.py`, `/tmp/audit/mbb.py`; clean clones `/tmp/nabd_clean`, `/tmp/nabd_fetch`, `/tmp/nabd_retune`.
