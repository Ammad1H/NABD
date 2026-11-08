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
