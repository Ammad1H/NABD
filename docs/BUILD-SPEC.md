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
- v1.3 8 Nov: R2 REVIEW RESULT. Audit (docs/REVIEW-R2-audit.md): G1 PARTIAL, G2 PASS, G3 PASS, G4 PASS, G5 PARTIAL, G6 PASS, G7 PASS, G8 FAIL, G9 FAIL, G10 PARTIAL, G11 FAIL; 3 CRITICAL, all claim/app mismatches. Judges (docs/REVIEW-R2-judges.md): about 5.3/10, not top-3 as is. Decisions for build round 2:
  - **HEADLINE (fixed):** "The UAE has no respiratory forecasting hub. NABD is one, held to the CDC's standard in public." The UAE track is the product proof. US NOT MET is shown plainly on its own slide ("We set our bar at the CDC's best. v1 missed it, and here is exactly where."). E1 is never used as a claim; at most it's an exploratory footnote.
  - **CLAIM RULE (G9, hard):** the pitch/registration may only describe (a) what is built and scored, or (b) items explicitly labelled "in build, by 20 Nov" that ARE in the round-2 build plan. Nothing else. Drop the foundation-model claim (Chronos-2 "optional, run off-sandbox, results reported only if run"), ACI unless built and scored, ED/geospatial inputs for NABD unless built.
  - **UAE v2 (true multi-signal):** before computing any v2 score, write docs/PROTOCOL-UAE-v2.md (signals, model, LOSO, metrics, alert rule), commit it and hash it in FREEZE.md. It must be labelled "retrospective, protocol declared before scoring v2; v1 results already seen". Signals: sentinel + NON-SENTINEL FluNet (real), testing volume, school calendar (where verified), weather if obtainable (else omitted, not faked). Outputs: exact per-signal contributions (G11) and a real feed-removal ablation.
  - **G10 UAE:** a pre-declared alert rule on UAE series: lead, sensitivity, PPV, false alarms (n=4, descriptive), and missing-feed behaviour.
  - **US fixes:** disclose pre-freeze probes in DEVIATIONS; moving-block bootstrap as a sensitivity analysis; state the national-series share and per-state win counts; a league table vs individual hub models with the method declared in DEVIATIONS before computing; check FluSight hub participation rules for a prospective v1 submission (report only, don't submit).
  - **Contracts (new):** results/uae/explain/<issue_date>_<target>.csv (horizon, feature, value, contribution, unit) and results/uae/tables/ablation.csv (feed, metric, full, without, delta). summary.json gains a key `primary_verdict` ("MET"/"NOT MET") and `primary_text`.
  - **Pitch:** registration text is final by 9 Nov 20:00 GST (it is due 10 Nov).
- v1.4 8 Nov: KIT + NEW EVIDENCE TRACK + POSITIONING.
  - **Kit:** vendor/nabd_v2_kit (see VENDORED.md) is third-party code. Use it, but cross-check first: kit WIS vs our WIS on v1 and the CDC ensemble must agree to 1e-9; log the result in docs/DEVIATIONS.md either way.
  - **G12 GCC out-of-sample test (new, highest-value evidence):** freeze the UAE v2 method, then test it on OTHER GCC/EMRO countries' WHO FluNet data that nobody on the team has looked at. Fill vendor template PREREG_GCC_HOLDOUT.md as docs/PREREG-GCC.md, with an exposure declaration (the coordinator and loop agents have used ARE and USA FluNet only; the data agent must check its own history and declare honestly), inclusion rules decided before download, lock (prereg.lock) + manifest + commit, and only THEN download and score. Report every country, losses included. Purpose: shows the method generalises across the Gulf, which supports a "GCC respiratory forecasting hub" scale story.
  - **G13 Phase diagnostics (descriptive):** WIS decomposition (dispersion/over/under) by as-of phase and horizon for v1 US, and the national series alone. Plus decision value: relative economic value curves for NABD vs persistence vs the CDC ensemble on one pre-declared event definition.
  - **G14 Card consistency:** card.check_card (kit) or equivalent runs in tests on every generated card; no contradictory card can render.
  - **US v2 (optional, integrity only):** if time allows after G12, fill PREREG_US_V2 as docs/PREREG-US-V2.md, lock it, and provide forecasts for prospective 2026/27 reference dates only. No retrospective v2 claims.
  - **Positioning workstream (new):** research/positioning.md is the single source for the pain point and value story; pitch/ must draw from it.
