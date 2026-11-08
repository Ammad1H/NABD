# NABD: Assumptions, dependencies and limitations

Required by the Challenge submission rules (FAQ: a working prototype with "technical documentation and a clear statement of assumptions, dependencies and limitations"; see `research/tc.md`). This statement is part of the submission. Status as of 8 Nov 2026; update on 19–20 Nov.

## 1. What NABD v1 is, exactly
- **UAE model (NABD-UAE-v1):**
  - **What it forecasts:** weekly sentinel RSV and influenza positivity, at the nowcast and +0.5, +1.5 and +2.5 weeks after issue.
  - **Inputs:** WHO FluNet UAE sentinel positivity and testing volume only.
  - **Method:** a pooled linear growth model on the logit scale with a seasonal-climatology term, and intervals from nested out-of-season residuals.
  - Source: `uae/models.py`.
- **US model (NABD-ensemble v1):**
  - **What it forecasts:** weekly state influenza admissions (NHSN), +0.5 to +3.5 weeks after issue.
  - **Inputs:** admissions only.
  - **Method:** an equal-weight quantile average of a damped log-linear negative-binomial GLM and an empirical error-quantile model.
  - **Tuning:** on 2023/24 only (`models/config.yaml`).
- **Decision layer:**
  - the bilingual Streamlit card;
  - an ILLUSTRATIVE playbook mapping forecast bands to proposed actions for named roles;
  - Approve / Modify / Dismiss with a reason;
  - a hash-chained, append-only audit log;
  - a FastAPI endpoint.
- **Ledger:** hashed forecast rounds (`ledger/`).

## 2. Assumptions
- **A1.** WHO FluNet UAE sentinel positivity is a usable indicator of community RSV and influenza activity. It is laboratory surveillance from sentinel sites, not hospital load, and testing practice can change.
- **A2.** Publication lag is roughly 7–11 days. It was measured at 7 days on 8 Nov (`data/raw/PROVENANCE.md`). Horizons are defined relative to the issue date on this basis.
- **A3.** First-release FluNet values may be revised. The UAE retrospective uses latest-revised values (no vintages exist), which flatters it relative to live use.
- **A4.** Hospital load in Abu Dhabi moves with community positivity closely enough for a positivity forecast to be decision-relevant. This is **untested**: it is the pilot's question.
- **A5.** The US benchmark (NHSN admissions, CDC FluSight hub) is a fair stress test of the method, but not of UAE performance.
- **A6.** Playbook thresholds and actions are placeholders until reviewed by clinicians and public-health officials.

## 3. Dependencies
- **D1. Data:**
  - WHO FluNet (public-health, non-commercial terms);
  - CDC FluSight hub (MIT; US Government data);
  - UAE Ministry of Education calendar (public).
  - NOAA weather is planned but not used: it was blocked in our build environment.
- **D2. Software:** Python 3.10+, pandas, numpy, scipy, statsmodels, streamlit and fastapi (see `requirements-app.txt`). It runs on a laptop CPU.
- **D3. Foundation model:** Chronos-2 needs Hugging Face access and ideally a GPU. Its wrapper exists, but it was **not run** and is excluded from every reported result.
- **D4. For the pilot:** one hospital's aggregate daily or weekly paediatric/ED counts and admissions, under a data-sharing agreement. There is no patient-level data.
- **D5. For an outside timestamp:** a public repository and an external anchor (OpenTimestamps, Zenodo or OSF), which the team must create.

## 4. Limitations (stated plainly)
1. **The US primary test was NOT MET.** Relative WIS against the CDC FluSight ensemble was 1.22 (95% CI 1.01–1.52), against a pre-registered margin of 1.15.
   - NABD was worse than the ensemble in every state when pooled, and in all of them in 2025/26.
   - Against the naive baseline, 0.82 (0.66–1.02) is not a convincing win.
   - Sources: `results/SUMMARY.md`, `docs/REVIEW-R2-audit.md`.
2. **UAE evidence is thin and retrospective.**
   - There are only 4 seasons, and the design was settled with all four visible (design-stage, not pre-registered).
   - The leave-one-season-out folds train on later seasons when testing earlier ones.
   - RSV lost to persistence in 2025/26, the only fold that is forward in time.
3. **No Abu Dhabi hospital, district or daily data.** NABD makes no Abu Dhabi operational claim.
4. **No earlier onset warning.** Median onset lead is 0 weeks for every rule tested, including the CDC ensemble's (`results/tables/alerts_us.csv`).
   - The alert thresholds were informed by probes that touched the test seasons before the freeze (`docs/DEVIATIONS.md` D3, D5).
   - The alert metrics are therefore diagnostic only.
5. **Single-signal v1.** One missing input week raises US error 1.41-fold, and two weeks 1.82-fold (`results/tables/dropout_us.csv`). The multi-signal UAE v2 is in build.
6. **Simulated workforce module.** The employer sickness-absence feed is a secure-aggregation design demonstrated on synthetic data, and it is watermarked SIMULATED. The workforce half of Statement 06 is only partly met.
7. **Self-attested timestamps until anchored.** Protocol and ledger hashes are local git commits until the team publishes and anchors them externally.
8. **Prior exposure.** Exploratory probes on 5 Nov touched the US test seasons before the protocol freeze. This is disclosed in `docs/DEVIATIONS.md` (D5).
9. **The WHO FluNet licence** is non-commercial. A commercial hospital product would need to run on the hospital's own data.
10. **Generalisation beyond the UAE is untested** until the GCC out-of-sample test reports ⟦RESULT: results/gcc/ (G12)⟧.

## 5. What would change these conclusions
- A locked UAE method that beats persistence on other Gulf countries' unseen data (G12).
- Prospective ledger scores during 2026/27.
- A shadow pilot on one hospital's counts, judged on pre-set exit criteria.
