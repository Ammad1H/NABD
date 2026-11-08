# NABD build log

## 2026-11-08: Data & UAE workstream (build round 1)
**Built**
- `adapters/` (FluNet UAE, weather, calendar) with pandera schemas and a person-level field guard.
- FluNet refreshed to **2026-W44** (sentinel 342/92/36).
- `uae/`: NABD-UAE-v1 pooled growth + seasonal-prior + testing-volume model, persistence, seasonal analog, WIS.
- `uae/backtest.py`: LOSO, n=4, writing to `results/uae/`.
- `ledger/issue.py` and `ledger/score.py` (hash verification) and `ledger/README.md`. **R0 issued 06:51 UTC, not public.**
- `tests/test_adapters.py`: 23 passing, including a future-data invariance test and a positive control. That test caught and forced a fix of a LOSO boundary leak.

**Gates**
- **G4:** met for the cloud build.
- **G6:** adapter and leakage parts met.

**Results (PRELIMINARY, n=4).** Relative WIS of NABD-UAE-v1:
- flu: 0.76 [0.70, 0.82] vs persistence, 0.70 vs analog;
- RSV: 0.78 [0.71, 0.87] vs persistence, 0.69 vs analog.

NABD-UAE-v1 beat persistence in flu 4/4 seasons and RSV 3/4 (it loses on RSV 2025/26). RSV peak-week MAE is 1.4 wk vs 2.8 for persistence.

**Open**
- Weather is not retrieved (all NOAA hosts blocked). Placeholder is labelled real=False and unused; the user runs `python3 -m adapters.weather --fetch`.
- Past-year school calendars are unverified.
- R0 must be pushed publicly by the user.
- The W44 RSV drop may be a reporting artefact.
- The modelling workstream's US track is separate (not in this workstream's scope).

## B1 evidence & pitch workstream (8 Nov)
- **Built:**
  - research/burden.md (G7: 8 verified burden items; best is Tawam RSV, 2,189 admissions of children aged 5 and under 2018–22, positivity 2.9–16%, JIPH 2025);
  - research/competitors.md (ADPHC tender scope verified, awardee not found; GE CareIntellect is 72 h, in-hospital);
  - research/tc.md (FAQ + T&C + the official Statement 06 requirement list);
  - pitch/outreach.md, qa.md, deck-script.md, demo-script.md, registration.md.
- **Gates:** G7 PASS (burden verified; emails drafted; T&C summarised). G8 groundwork done, with ⟦RESULT⟧ slots still to fill from results/.
- **COORDINATOR FLAGS:**
  1. The official Statement 06 req. 5 asks for lead time, sensitivity, PPV, false alarms, data latency and missing-input behaviour. Req. 2 asks alerts to show contributing signals, locations and time periods. Add both to the G3/G5 scope.
  2. The T&C grant the Organiser a 6-month right of first refusal on exclusive licences. An open-source licence for the repo looks compatible.
  3. There is no conflict-of-interest clause; MBZUAI's own policy should be checked.
  4. Team engagement at checkpoints is mandatory (disqualification risk).
  5. DoH said in Sep 2026 that activity is similar to the previous two seasons, so don't pitch it as a crisis.
- **Open:**
  - the DoH Circular 37/2026 PDF (robots-blocked, so read it in a browser);
  - fill the ⟦RESULT⟧ slots after the modelling run;
  - abstract word counts run slightly over (56/160/310), so trim if the form enforces limits.

## App workstream, round 1 (8 Nov)
- **Built:**
  - `playbook/playbook.yaml` (v0.1.0, ILLUSTRATIVE; 7 bands, 2 roles, EN/AR) with `playbook/validate.py`, a schema validator with an overlap check.
  - `app/audit.py`: append-only SHA-256 hash-chained JSONL.
  - `app/data_io.py`: contract-only loaders. The live ledger round is preferred, then retrospective, then DEMO.
  - `app/demo_data.py`: number-free demo tables.
  - `app/workforce.py`: SIMULATED additive secret sharing with k-anonymity.
  - `app/streamlit_app.py`, bilingual (EN/AR RTL), with 6 pages.
  - `app/api.py`: FastAPI `/forecast` and `/health`, with OpenAPI.
  - Dockerfile, docker-compose.yml, requirements-app.txt and app/README.md.
- **Verified:**
  - `pytest tests/test_app_audit.py`: 21 passed.
  - AppTest renders all 6 pages × 2 languages with no exceptions.
  - Live `streamlit run` returns 200 and `/forecast` serves the R0 ledger round. Horizons are measured from the issue date: nowcast, then +1 to +3 wk.
  - 5 screenshots in `app/screenshots/`.
- **Gates:** G5 is met, except the US proof panel still shows DEMO until `results/summary.json` and `results/tables/` exist. The audit part of G6 is met.
- **Open:**
  - The Docker image was not built, because there is no Docker daemon in the sandbox.
  - Playbook thresholds are placeholders pending review.
  - Ablation shows DEMO until `results/tables/ablation*.csv` exists.
  - The weekly card's driver panel is descriptive context, not model attributions.

## Round 1: Modelling workstream (8 Nov 2026)

**Built**
- **Data and vintages:** `models/data.py` (vintage rule PROTOCOL §2; exact duplicate rows in vintage 2026-05-27 dropped, D4).
- **Point model:** `models/point.py` (damped pooled log-linear growth).
- **Members:** `models/members.py` (NB GLM, EEQ with level strata, D1), with stale-vintage handling (D2) and feed-dropout (diagnostic only) in `models/engine.py`.
- **Chronos-2 wrapper:** `models/chronos2.py`. NOT RUN here because Hugging Face is blocked.
- **Evaluation:** `eval/{wis,tune,backtest,score,alerts,exploratory,run_all}.py`, `Makefile`.
- **Tests:** `tests/test_wis.py` (interval form = pinball form, hand-computed example, point mass) and `tests/test_vintage.py` (vintage deadline, cutoff, injected future point does not leak, negative control).
- **Protocol:** `docs/PROTOCOL.md` frozen at commit `ac16901`, SHA-256 `2846533f…`, 06:47Z (`docs/FREEZE.md`). Pre-test deviations D1, D2 and D3 (alert rule, before any test forecast); D4 (data bug, before scoring). Exploratory E1 is labelled.
- **Config:** `models/config.yaml` was tuned on 2023/24 only. Re-running tuning reproduces it exactly.

**Results (single test run, frozen config)** in `results/SUMMARY.md`, `results/summary.json`, `results/tables/*`, `results/figures/*`:
- **PRIMARY:** NABD-ensemble vs FluSight-ensemble, rel. WIS **1.223 (95% CI 1.011–1.521)**. Non-inferiority (margin 1.15) is **NOT MET**.
  - 2024/25: 1.026 (0.885–1.255).
  - 2025/26: 1.516 (1.093–2.026).
- **S1:** vs FluSight-baseline 0.816 (0.655–1.023). The point estimate is below 1, but the CI includes 1.
- **S2:** 95% coverage 0.918 (FluSight-ensemble 0.861); 50% coverage 0.480.
- **Members:** EEQ 1.198, GLM 1.315. Log-scale 1.225 (1.147–1.321). First-release truth 1.295.
- **G10 US alerts** (`results/tables/alerts_us.csv`, T = 3 per 100k): timely-alert sensitivity (lead 0–4 wk) NABD 0.33 / 0.56 vs FluSight-ensemble 0.18 / 0.54 vs census 0.55 / 0.46 (2024/25 / 2025/26). PPV NABD 0.65 / 0.76 vs FS 0.41 / 0.67 vs census 0.60 / 0.46. Median lead of timely alerts is 0 weeks for all rules (lead parity, as the probe predicted). There were no false-alarm location-seasons at T = 3.
- **Latency:** inputs are 4 days old at issue (11 days in 5 stale rounds). Feed dropout of 1 week raises WIS ×1.41; 2 weeks ×1.82.
- **E1 (exploratory):** in rising phases NABD beats the FluSight-ensemble at 0.893 (0.821–0.984). It loses in flat or falling phases at 1.86–1.96.

**Gates:**
- **G1 PASS:** protocol frozen before any test score; deviations logged.
- **G2 PASS:** `python -m eval.run_all --cached` takes 22 s with the frozen config; about 4.5 min with `--retune`. Deterministic.
- **G3 PASS (computed honestly):** the verdict is NOT MET.
- **G6 (vintage and WIS parts) PASS:** 52/52 tests pass repo-wide.
- **G10:** the US part is done. The UAE part is not mine.

**Open**
- Chronos-2 must run on a laptop or Colab: `NABD_CHRONOS=1 python -m eval.backtest --with-chronos`, then `python -m eval.score`. Its contribution is unknown. Adding it to the primary ensemble would be a post-freeze change and must be logged as a deviation.
- A v2 member aware of turning points (from E1) should be pre-registered for the prospective 2026/27 ledger only.
- `results/forecasts/` is about 64 MB in git. Consider Git LFS or zipping before pushing.
- The pitch must say plainly that NABD did not match the CDC ensemble. Defensible claims are: beats persistence (point estimate; CI touches 1), better 95% calibration, and better than the ensemble during surges (exploratory).

## Round 2: pitch workstream (8 Nov)
- **registration.md (FINAL for 10 Nov):** v1.3 headline. Word counts measured by `pitch/wordcount.py`: summary 98/100, a50 49/50, a150 149/150, a300 293/300. Every in-build item is labelled. Data-source table and maturity statement included (T&C). Audit CRITICAL 1 fixed.
- **qa.md:** rewritten as 21 questions plus curveballs. Audit CRITICAL 2 fixed (ACI, "matched the ensemble", the ED track, "102 weekly"). Every answer cites a results file.
- **assumptions-limitations.md:** new (T&C requirement).
- **deck-script.md / demo-script.md:** rewritten to the v1.3 headline. Slide 7 NOT MET wording follows the judges. Numbers are filled from results/. Pending ⟦RESULT⟧ slots name their exact files (UAE v2 explain/ablation, UAE alerts, GCC, league table, anchor). The demo drops the non-existent Explain and ED-toggle beats unless built (audit MAJOR 10).
- **research/claims-ledger.md:** new; 41 claims with source and status. Banned claims listed (audit MAJOR 13, E1).
- **outreach.md A2:** corrected wording.
- **Open:**
  - research/positioning.md did not exist at the end of this run; slides 2 and 3 should be re-checked against it.
  - The pending slots must be filled or cut on 19 Nov.
  - The team names and the MBZUAI permission status are still unfilled.
