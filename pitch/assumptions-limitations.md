# NABD: Assumptions, dependencies and limitations

Required by the Challenge submission rules (FAQ: a working prototype with "technical documentation and a clear statement of assumptions, dependencies and limitations"; see `research/tc.md`). This statement is part of the submission. Status as of 8 Nov 2026 (round 4); update on 19–20 Nov. Full method detail is in `docs/TECHNICAL.md`.

## 1. What NABD is, exactly
- **UAE headline model: NABD-UAE-v1** (`uae/models.py`, frozen at commit da045ee).
  - **Forecasts:** weekly sentinel RSV and influenza positivity, from the nowcast to +3 weeks after issue, each forecast labelled by its target week-ending date (skill measured at a conservative 11-day publication lag). The hashed R0/R1 rounds use the same convention (DEVIATIONS C8).
  - **Inputs:** WHO FluNet UAE sentinel positivity and testing volume.
  - **Method:** a pooled linear growth model on the logit scale with a seasonal-climatology term. Intervals come from nested out-of-season residuals.
- **UAE challenger: NABD-UAE-v2** (`uae/models_v2.py`, locked protocol `docs/PROTOCOL-UAE-v2.md`).
  - **Inputs:** v1 plus non-sentinel positivity, the school winter/spring breaks and Ramadan. It falls back to a smaller sub-model when a feed is missing.
  - **Status:** it ran alongside v1 in the ledger and was **worse than v1** retrospectively.
- **US benchmark model: NABD-ensemble v1** (`models/`, `docs/PROTOCOL.md`).
  - **Forecasts:** weekly state influenza admissions (NHSN), FluSight horizons 0–3 (target weeks ending 0–3 weeks after the Saturday reference date).
  - **Inputs:** admissions only.
  - **Method:** an equal-weight quantile average of a damped log-linear negative-binomial GLM and an empirical error-quantile model, tuned on 2023/24 only.
- **Decision layer:**
  - a bilingual Streamlit card that always shows persistence alongside the forecast;
  - exact per-signal explanations;
  - an ILLUSTRATIVE playbook for named roles;
  - Approve / Modify / Dismiss with a reason;
  - a card consistency check, so contradictory cards can't render;
  - a hash-chained, append-only audit log;
  - a FastAPI endpoint.
- **Ledger:** one forecast round (data through W44), issued as R0 and re-issued as R1 with the v2 challenger. The v1 and persistence files are byte-identical across the two. Hashed, with a Merkle manifest (`ledger/`). As of 8 Nov, 0 weeks have been scored, because no target week has been published. It is **not yet public or externally anchored**.

## 2. Assumptions
- **A1. Surveillance as a signal.** WHO FluNet sentinel positivity is a usable indicator of community RSV and influenza activity in the UAE and in the Gulf test countries. It is laboratory surveillance, not hospital load, and testing practice can change.
- **A2. Publication lag.** WHO's lag is about 7–11 days; it was measured at 7 days on 8 Nov (`data/raw/PROVENANCE.md`). Horizons are defined relative to the issue date on that basis.
- **A3. Data revisions.** First-release FluNet values may be revised. The UAE and Gulf retrospectives use revised values (no vintages exist), which flatters them relative to live use. The ledger is the live test.
- **A4. Positivity and hospital load.** Hospital load in Abu Dhabi moves with community positivity closely enough for a positivity forecast to be decision-relevant. This is **untested** and is the pilot's question.
- **A5. Scope of the US benchmark.** The US benchmark (NHSN admissions, CDC FluSight hub) is a fair stress test of forecasting method and discipline. It is not a test of UAE performance.
- **A6. The playbook.** Thresholds and actions are placeholders until reviewed by clinicians and public-health officials.
- **A7. Gulf countries' data.** The Gulf test assumes their FluNet reporting is comparable enough for a frozen method to transfer. Oman and Qatar report a single combined stream rather than separate sentinel data.

## 3. Dependencies
- **D1. Data:**
  - WHO FluNet: UAE, Oman, Qatar and Saudi Arabia. Public-health, non-commercial terms. The Gulf data are WHO's full export (3 Oct 2026), obtained via a public mirror. They match our independently fetched UAE rows exactly (419/419) and 23/23 spot-checked Gulf rows. A full official re-pull (`python -m adapters.gcc_verify`) is pending (deviations G1, G1b).
  - CDC FluSight hub: MIT licence; US Government data.
  - UAE Ministry of Education calendars and Ramadan dates: public.
  - NOAA/ERA5 weather is planned but not used, because it was blocked in our build environment.
- **D2. Software:** Python 3.10+, pandas, numpy, scipy, statsmodels, streamlit and fastapi (`requirements-app.txt`). It runs on a laptop CPU. The third-party kit `vendor/nabd_v2_kit` was cross-checked: its WIS matches ours exactly (`results/tables/scorer_crosscheck.csv`).
- **D3. Foundation model:** Chronos-2 needs Hugging Face access and ideally a GPU. Its wrapper exists, but it was **not run** and is excluded from every reported result.
- **D4. For the pilot:** one hospital's aggregate weekly paediatric respiratory counts, under a data-sharing agreement, per `docs/PILOT-DATA-SPEC.md` (enforced aggregation, k ≥ 10 complementary suppression, identifiers rejected). No patient-level data.
- **D5. For an outside timestamp:** a public repository and an external anchor (OpenTimestamps, Zenodo or OSF), which the author must create (`ledger/ANCHOR.md`).

## 4. Limitations (stated plainly)
1. **The US primary test was NOT MET.** Relative WIS against the CDC FluSight ensemble was 1.22 (95% CI 1.01–1.52), against a pre-registered margin of 1.15.
   - Per location, NABD beat the ensemble in 18 of 53 locations in 2024/25 and in 0 of 53 in 2025/26.
   - Excluding the national series still fails (1.198).
   - Against the naive baseline, 0.82 (0.66–1.02) is not a convincing win.
   - Among individual hub models it ranked 7th of 21 in 2024/25, but 19th of 25 in 2025/26, level with the baseline (`results/SUMMARY.md`).
2. **The UAE's own record shows no edge.** Trained only on earlier seasons, v1 ties with persistence (1.002 for flu and RSV).
   - The earlier leave-one-season-out figures (0.76/0.78) trained on later seasons and are retired as headline evidence.
   - n = 4 seasons, and v1 was designed with all four visible (`results/uae/SUMMARY-v2.md`).
3. **More signals did not help.** The multi-signal v2 was worse than v1 (1.059, CI 1.016–1.111). Removing non-sentinel or calendar inputs did not hurt.
4. **The Gulf test is retrospective and small.**
   - It covers 3 countries with about 4 seasons each, on revised data.
   - The influenza bar was met: 0.914 (0.843–0.983).
   - It lost in 3 of 12 flu country-seasons and 1 of 10 RSV.
   - RSV is a secondary outcome. Its country-clustered interval crosses 1 (0.712–1.026), and its intervals are too narrow outside the UAE (95% coverage 0.83).
   - The influenza result survives dropping any one country (0.904–0.929) and a country-clustered bootstrap (0.841–0.984) (`docs/REVIEW-R3-audit.md` §0).
   - The lock is a local git commit, self-attested until anchored. We describe the test as "out-of-sample, plan locked before download", not "blind".
   - v1 was chosen as the primary method after the UAE v2 and forward-in-time results were known. This is disclosed (`docs/PREREG-GCC.md` §1).
5. **No Abu Dhabi hospital, district or daily data.** NABD makes no Abu Dhabi operational claim.
6. **No earlier onset warning.** At the US primary threshold (3 per 100k), median onset lead is 0 weeks for every rule tested, including the CDC ensemble's. Every rule had 0 false alarms there. NABD's higher precision reflects fewer *late* alerts, not fewer false ones, and a census rule caught more onsets in time in 2024/25 (28 vs 17 of 51).
   - Alert thresholds were informed by probes that saw the test seasons (`docs/DEVIATIONS.md` D3, D5; `docs/PROTOCOL-UAE-v2.md` §1).
   - All alert metrics are diagnostic only.
   - UAE alert metrics come from the leave-one-season-out design (which trains on later seasons) and cover only 3 onsets per series. We don't cite them.
7. **Missing data hurts.** One missing input week raises US error 1.41-fold, and two weeks 1.82-fold. In the UAE, a missing latest week raises mean WIS by 0.14–0.26 percentage points.
8. **The workforce module is simulated.** The employer sickness-absence feed is a secure-aggregation design on synthetic data, watermarked SIMULATED. No credible UAE respiratory-absence figure was found. The hospital winter planner translates the forecast into the hospital's own beds and staff, using hospital-supplied inputs (staff absence follows flu and RSV by default), and every number is labelled SCENARIO. The workforce half of Statement 06 is met only as a designed path and a scenario, not as a scored forecast of absence.
9. **Timestamps are self-attested until anchored.** Protocol locks (US, UAE v2, Gulf) and ledger hashes are local git commits. Nothing was externally anchored before results existed, and any later anchor must be described that way.
10. **Prior exposure.** Exploratory probes on 5 Nov touched the US test seasons before the protocol freeze (D5).
11. **The WHO FluNet licence** is non-commercial. A commercial hospital product would run on the hospital's own data.

## 5. What would change these conclusions
- Prospective ledger scores through 2026/27, anchored by an outside service.
- A shadow pilot on one hospital's counts, judged on its pre-set exit criterion (relative WIS < 0.9 vs the census carried forward).
- A prospective US v2, locked before its first forecast (`docs/PREREG-US-V2.md`, draft).
- Weather, wastewater (Rasid) or hospital signals added as a new locked version, published whether or not they help.
