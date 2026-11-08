# NABD Build Loop: Fixed Goal Spec (v1, 8 Nov 2026)

Every builder and reviewer agent reads this first. Only the coordinator edits it, and records every change in the changelog.

## Objective
Turn NABD (see docs/SPEC.md) into a **winning-calibre, working, reproducible submission** for the Future Health Digital Innovation Challenge 2026 (Statement 06). The prototype is due 20 Nov and is judged 20–30 Nov. Registration is due 10 Nov.

## Environment facts (checked 8 Nov)
- **Reachable:** GitHub (git clone works) and PyPI.
- **Blocked:** Hugging Face, WHO, CDC and Delphi from the shell. WebFetch can sometimes reach WHO/CDC pages.
- **Hardware:** no GPU; 2 CPUs; 7 GB RAM.
- **Consequences:**
  - Chronos-2 weights can't be downloaded here. Build its wrapper so it runs on the user's laptop/Colab and is skipped cleanly here, recorded as `NOT RUN HERE` and never faked.
  - All live data fetches must also have a `--cached` path that uses data/raw.
- **Python packages installed:** pandas, numpy, statsmodels, scipy, pandera, duckdb, streamlit, fastapi, uvicorn, pytest, pyyaml.

## Repo layout (each workstream writes only to its own dirs)
- `adapters/` and `data/`: data workstream
- `models/`, `eval/`, `results/`, `docs/PROTOCOL.md`: modelling workstream
- `app/`, `playbook/`, `tests/test_app*`: app workstream
- `research/`, `pitch/`: evidence and pitch workstream
- `docs/`: shared. Append, never overwrite another's file.

## PASS GATES (the loop stops when ALL pass and the reviewer panel finds no CRITICAL)
- **G1 Protocol integrity.** `docs/PROTOCOL.md` exists and is committed BEFORE any test-season result is computed; its git commit hash and SHA-256 are recorded in `docs/FREEZE.md`. Test seasons are 2024/25 and 2025/26 on US-A. Tuning uses ≤2023/24 only. Any later change goes in `docs/DEVIATIONS.md`.
- **G2 Reproducible pipeline.** `make all` (or `python -m eval.run_all --cached`) runs end-to-end from a clean checkout with cached data: data → models → backtest → results tables and figures. Runtime is under 30 min on 2 CPUs. Seeds are fixed.
- **G3 Primary endpoint computed honestly.** NABD-ensemble (without Chronos here) vs FluSight-ensemble and FluSight-baseline on US state flu admissions. Use vintage-correct inputs (only data available at each forecast date), the same truth for every model, and relative WIS with a block-bootstrap 95% CI. Report non-inferiority (margin 1.15) as met or not met, with no spin. Report per-season and per-horizon tables plus coverage.
- **G4 UAE track.** Leave-one-season-out positivity forecasts for RSV and flu vs persistence and seasonal-analog baselines, with n=4 stated. Plus a working `ledger_issue` round from cached data with a hash.
- **G5 Working app.** The Streamlit app runs locally: bilingual (AR/EN) forecast card, fan charts, data-freshness badge, playbook action, Approve/Modify/Dismiss with a reason, append-only JSONL audit, "SIMULATED" watermark on simulated layers, a ledger "receipt" view, and a feed-removal toggle. The FastAPI `/forecast` endpoint returns a valid JSON schema.
- **G6 Tests.** `pytest` passes: adapters reject person-level fields; vintage rule (no future data leaks into any forecast; a test must fail if leakage is injected); WIS implementation matches a known reference value; the audit log is append-only.
- **G7 Evidence.** At least 1 VERIFIED, sourced figure for UAE/Abu Dhabi winter respiratory burden (hospitalisations, paediatric RSV burden, ED pressure, or similar); otherwise it is explicitly reported as not found. Draft letter-of-interest and playbook-review emails. A T&C summary if retrievable.
- **G8 Pitch.** `pitch/`: final abstract, a 10-slide deck script with real numbers filled in from `results/` (no placeholders left except clearly marked live-ledger items), a 3-minute demo script, judge Q&A prep (top 15 hostile questions with answers).
- **G9 Honesty.** Every number in the pitch traces to a file in `results/` or a cited source. No claim of an Abu Dhabi operational result. Simulated items are labelled.

## Rules for all agents
- No fabricated results. If something can't run, say so and leave a runnable path for the user.
- Prefer WebSearch/WebFetch over the browser. Open your own tab only if essential.
- Quote no more than 15 words from any one source. Tag claims VERIFIED (URL) / UNVERIFIED.
- Never register, submit, post or email on the user's behalf.
- Commit your work with clear messages (git is initialised in /home/claude/fhdic/nabd). Commit only your own dirs.
- End your run by appending a short entry to `docs/BUILD-LOG.md`: what you built, which gates you advanced, and what is open.

## Changelog
- v1 8 Nov: created.
- v1.1 8 Nov: INTERFACE CONTRACT (all workstreams).
  - Forecast files use the FluSight hub quantile format, CSV columns: `reference_date,target,horizon,target_end_date,location,output_type,output_type_id,value,model`. US targets: `wk inc flu hosp`. UAE: location `ARE`, targets `wk flu pos pct sentinel` and `wk rsv pos pct sentinel`. Quantiles: the FluSight set (0.01,0.025,0.05,0.1,...,0.9,0.95,0.975,0.99).
  - Output paths:
    - `results/forecasts/<model>/<reference_date>.csv` (US)
    - `results/uae/forecasts/<model>/<reference_date>.csv`
    - `results/tables/*.csv`, `results/figures/*.png`, `results/SUMMARY.md` (headline numbers, machine-readable `results/summary.json`)
    - `ledger/<UTC>_<model>.csv` + `.sha256`
  - The app reads ONLY these paths and must fall back to labelled demo data if they're missing.
- v1.2 8 Nov (from the evidence workstream, research/tc.md): the official Statement 06 requirements add two gates.
  - **G10 Alert-performance metrics (req 5):** for an alert layer derived from the forecasts (pre-specified threshold rule, documented in PROTOCOL.md or DEVIATIONS.md if added after freeze), report alert lead time, sensitivity, PPV, false alarms per location-season, data latency, and behaviour under missing feeds (feed-dropout test). Do this on US (state admissions surges) and on UAE (n=4, descriptive). It must be honest that onset lead ≈ parity with census rules (per the probe).
  - **G11 Alert explainability (req 2):** each alert/card shows the drivers (signals, locations, time windows) that drove it: feed-removal deltas and/or per-feature contributions, rendered in the app.
  - T&C facts: team 1–5, one team per person; a working prototype, technical docs and an assumptions/dependencies/limitations statement are due 20 Nov; all data sources must be declared; existing prototypes allowed with maturity stated; IP stays with the team, with a 6-month right of first refusal to the organiser for an exclusive licence.
  - Pitch tone: DoH said in Sep 2026 that this season looks similar to the previous two, so pitch VARIABILITY and planning value, not crisis.
