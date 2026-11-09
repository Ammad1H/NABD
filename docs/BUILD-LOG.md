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

## Positioning workstream, round 2 (8 Nov 2026)
- Wrote research/positioning.md (single source for the pain point and value story) and research/positioning-sources.md (S1–S29, each with status).
- New verified anchors:
  - Season-shape table from WHO FluNet UAE [DATA]: flu peaked wk 45/45/wk 7 (Feb)/42 at 27–41% positivity; the 2024/25 season was a 5-month plateau. RSV peaked wk 41–47; RSV first reached ≥10% before 1 Sep in 2 of 4 seasons.
  - Abu Dhabi's existing sensing layer (Tableegh/Malaffi, UMOC AI early warning) means NABD is positioned as the forecast layer on top.
  - DoH says this season is "similar to previous two", so pitch variability, not crisis.
  - The MoHAP climate adaptation plan 2026–31 names respiratory disease and early warnings.
  - School break dates 14 Dec–3 Jan.
- Chosen problem statement (40 words), "only we" claim (with "to our knowledge"), moat, NOT MET reframing, stop list.
- Ranked solution improvements:
  1. Exceedance probability + direction on the card.
  2. Season-shape panel.
  3. Tableegh-ready pilot data spec.
  4. Bed-days SCENARIO translator.
  5. GCC panel.
- Not found: Abu Dhabi ED/bed series, a UAE flu hospitalisation estimate, a credible UAE absence figure, any public UAE/GCC respiratory forecast.

## Round 2 — US modelling (replacement builder), 8 Nov 2026
- **Vendored** the remaining nabd_v2_kit modules, tests and examples verbatim from the Project. Kit tests: 26/26 pass.
- **D9 scorer cross-check: PASS.** Our WIS equals the independent kit WIS exactly (max diff 0.0) on all cells for NABD, the FluSight-ensemble and the FluSight-baseline, with no crossing quantiles.
- **D6 (declared earlier):**
  - **Primary circular block bootstrap (L=4):** 1.223 (CI 0.979–1.573). L=6 gives 0.965–1.553. **Still NOT MET.**
  - **National series share of WIS:** NABD 46.0%, ensemble 44.9%.
  - **Excluding US:** 1.198 (cluster CI 1.014–1.449). S1 excluding US: 0.818 (0.675–0.998).
  - **Per-location wins vs ensemble:** 18/53 (2024/25), 0/53 (2025/26), 0/53 pooled. Vs baseline: 49/53, 18/53 and 47/53.
- **D7 league table** (D11 fixes the implementation; 80 hub models sparse-fetched, about 1.2 GB):
  - NABD v1 rank 13/41 in 2024/25 (rel 0.693; the CDC ensemble is 12th at 0.673) and 40/46 in 2025/26 (rel 1.007).
  - Single models only: 7/21 and 19/25.
- **D10 / G13 (descriptive):**
  - **Relative WIS vs ensemble by as-of phase:** rising 1.27, flat 0.97, falling 1.29.
  - **Decision value at +2.5 wk (≥3/100k):** NABD is higher than the CDC ensemble at low cost-loss ratios (C/L 0.02–0.1: 0.08/0.22/0.37 vs −0.13/0.11/0.26), about equal at 0.2, and lower at ≥0.3. No CIs.
- **Figure pack:** results/figures/fig1–fig4.
- **summary.json:** gains `primary_verdict`, `primary_text`, `round2`, and `exploratory` (flagged).
- **Pipeline:** run_all now calls eval.round2, with `--skip-league` available.
- **FluSight:** docs/FLUSIGHT-PARTICIPATION.md. Non-US teams already submit (U. Guelph). Drafts (not submitted): metadata YAML, a stale draft 2026-11-14 file, and `eval/flusight_round.py`.
- **docs/PREREG-US-V2.md:** draft only. US v2 is not built, not locked and not scored.
- **Open:** the user decides on the FluSight submission and on whether to lock US v2. external/hub is now a no-cone sparse checkout (run_all's pin check still applies).

## App, round 2 (replacement agent), 8 Nov
- **G14:** `app/cardcheck.py` builds every weekly card.
  - Direction facts come from vendor `nabd_kit.card` (P rise/fall/stable).
  - The playbook band is chosen by level and forecast path.
  - `card_problems` re-derives the card. A contradiction blocks the action and the approval form.
  - The live round now gives `rsv_elevated_falling` / `flu_elevated_falling`; the old "rsv_rising" contradiction is gone.
  - `tests/test_app_cardcheck.py` includes contradictory cards that must fail.
- **Playbook v0.2** (trajectory-aware, with falling/plateau bands) now validates: `*_not_rising` was renamed `*_steady_or_falling`.
- **US proof:** red NOT MET badge from `primary_verdict` / `primary_text`, plus the S1 line and the endpoints table.
  - League table: NABD v1 ranks 13/41 (2024/25) and 40/46 (2025/26), all models included.
  - Sensitivity, G13 diagnostics and EXPLORATORY (E1) sections sit in labelled expanders.
- **New pages:**
  - **Alerts** (US D3 metrics flagged diagnostic per D5; UAE alerts).
  - **GCC out-of-sample:** verdict, included countries and season wins, all read from results/gcc.
  - **Feed removal:** reads `results/uae/tables/ablation.csv` and reports feeds that did not help (NS, CAL, TV) honestly.
  - **"Why this forecast":** `results/uae/explain`, with plain-language feature names and leave-one-out percentage-point effects.
- **Data and labels:**
  - Results panels show "not yet computed" and never demo numbers. Demo data remains only for the card and ledger fallbacks, behind a banner.
  - Horizons are issue-relative to the middle of the target week (nowcast/+0.5/+1.5/+2.5).
  - About page: a live real / simulated / not-built table.
- **Tests and tooling:** `tests/test_app_audit.py` + `tests/test_app_cardcheck.py`: 31 pass, including all 8 pages rendering in EN and AR. Screenshots of all 9 views were regenerated with `app/take_screenshots.py`.
- **Open:**
  - No explain file exists for the live issue date (2026-11-08). The card shows the latest LOSO example, labelled. The data agent should write `results/uae/explain/2026-11-08_*`.
  - The ledger meta still labels horizons with the end-of-week convention (+1.0/+2.0/+3.0).
  - Docker is still unbuilt (no daemon).

## Round 2: data/UAE workstream (replacement agent), 8 Nov 2026
**Built**
- **UAE v2 (real multi-signal):** sentinel positivity, testing volume, NON-SENTINEL positivity (+1 wk lag), verified MoE school winter/spring breaks 2021/22–2026/27 (sources per row), Ramadan (kit tabular calendar).
  - Weather omitted: every 2026 source is blocked, and a GitHub ERA5 mirror ends 2025-12-31.
  - Protocol `docs/PROTOCOL-UAE-v2.md` locked by kit prereg (`docs/LOCK-UAE-v2.json`, f745efc2…; manifest 5ad8e85e…) **before** scoring, then scored once.
  - **v2 did NOT beat v1:** pooled 1.059 (moving-block 1.016–1.111); flu 1.049, RSV 1.073. v2 vs persistence 0.815.
  - **Ablation:** CLIM helps (+0.57 / +0.26 WIS when removed); NS (−0.09/−0.08) and CAL (−0.05/−0.04) *hurt* (overfitting on ~4 seasons); TV ≈ 0.
- **Forward-in-time sensitivity (new, honest):** v1 vs persistence = 1.002 for both flu and RSV. The v1 LOSO advantage depends on training with later seasons.
- **Explanations (G11):** exact per-term contributions for every LOSO issue date and the live round, in `results/uae/explain/<issue_date>_<target>.csv`.
- **Feed removal and missing feeds (G10):** `results/uae/tables/ablation.csv`.
  - NS dropped at forecast time → automatic fallback sub-model.
  - Latest sentinel week missing → WIS +0.14–0.26.
- **UAE alerts (G10, diagnostic, n=4):** `results/uae/tables/alerts_uae.csv`. Flu: v1 3/3 sensitivity, PPV 3/3, 0 false alarms, median lead 1.4 wk; census rule 2/3. RSV: weak for all rules (1/3).
- **G12 GCC out-of-sample:**
  - `docs/PREREG-GCC.md` locked (`docs/LOCK-GCC.json`, 741b36a9…) before any GCC download.
  - Data: WHO's full FluNet export via a public mirror, verified against the official API (deviation G1).
  - **PRIMARY MET:** flu, frozen v1 method vs persistence, 0.914 (0.843–0.983), OMN/QAT/SAU, forward-in-time, 9/12 country-seasons won. RSV 0.798 (0.719–0.894). BHR and KWT excluded by the rule.
  - `results/gcc/`.
- **Ledger R1:** v1 headline + v2 challenger + persistence, with a kit Merkle manifest (f1fffc0b…). `data_through` is now per series (m19). R0 has been scored: no target weeks published yet. `ledger/ANCHOR.md` has the user steps for OpenTimestamps/FreeTSA/Zenodo; anchoring is blocked from the sandbox.
- **v1 reporting fixes:** common cells (m18); the integrity note is now generated, not hand-written (m17); labelled retrospective / not pre-registered (M9, U1).
- **Tests:** tests/test_uae_v2.py (7) covers explain sums, no-future-data, the leak detector, known-future calendar, unverified calendar = NaN, and refusal by the GCC and v2 scorers without a valid lock. 30/30 pass together with test_adapters.

**Gates advanced:** G4 (UAE track + locked v2), G10 (UAE alert metrics, missing-feed behaviour), G11 (exact explanations), G12 (done, MET).
**Open:**
- Outside anchors (user).
- Weather (user, `adapters/weather.py --fetch` locally).
- Re-pull GCC from xMart locally before publication.
- v2 must not be marketed as an improvement.
- Pitch should lead with GCC + live ledger, not UAE LOSO (which the forward-in-time test shows ≈ persistence).
- After this commit, ledger/issue.py gained a live-explain writer. The R1 v2 forecast file was re-generated in a temp dir and reproduces byte-for-byte (sha 2e7979c4…).

## Round 3: pitch and docs (retry after rate limit), 8 Nov
- Committed the previous attempt's qa.md rewrite after checking it against results/ (GCC first, UAE parity, league line, v2 challenger, alerts diagnostic).
- Rewrote deck-script (v1.6 evidence order: GCC → ledger → US/league → UAE parity), demo-script, and assumptions-limitations; rebuilt research/claims-ledger.md (sections A–F; LOSO 7/8 = RET; "about 40 models" banned in favour of league counts).
- New: docs/TECHNICAL.md (mermaid architecture, model equations, protocol and lock provenance table, results tables, reproducibility, governance, limitations, deviations), pitch/video-script.md (336-word voiceover), pitch/one-pager.md.
- ⟦IF BUILT⟧ slots remain for round-3 app items (exceedance probabilities, season-shape panel, bed-days scenario), PILOT-DATA-SPEC and the anchor receipt. Cut them if absent on 19 Nov.
- Not touched: pitch/registration.md (final, coordinator c887edc).

## Round 3, data (retry), 8 Nov 2026
- **Ledger:**
  - issue-relative horizon labels (nowcast/+0.5/+1.5/+2.5 wk) in round metadata, matching the card;
  - an EXACT v1 (headline) per-signal explanation for the live issue date (`results/uae/explain/2026-11-08_*`), tested to match the hashed R1 median; the v2 explanation moved to `explain/challenger_v2/`;
  - `ledger.issue --explain-only` writes no ledger files;
  - `ledger.weekly`: one idempotent command that scores and issues only when there is a new WHO week (tested).
- **R3-3 pilot:**
  - `docs/PILOT-DATA-SPEC.md`: Tableegh/Malaffi context, ADHICS and the DoH AI policy cited; governance checklist; pre-specified exit criteria.
  - `adapters/pilot.py`: strict aggregate schema, k≥10 + complementary suppression, identifier rejection, no back-imputation.
  - A SYNTHETIC weekly example, the `uae/pilot_shadow.py` scorer, and tests.
  - Finding: daily RSV admission counts are fully suppressed at k=10, so the spec asks for weekly aggregates.
- **GCC data:**
  - The official xMart API is blocked from the shell, so a full re-pull isn't possible here.
  - Spot check extended to 16 more official rows (QAT, SAU, OMN), 16/16 identical; cumulative 23/23 (DEVIATIONS G1b). No re-score.
  - `adapters/gcc_verify.py` lets the user close G1 locally.
- **docs/RUNBOOK.md:** weekly ledger, FluSight, app, pilot and pre-publish checks, with a dry-run record.
- **Tests:** 120 passed.

## Round 3, app (retry), 8 Nov
- **R3-1:** playbook v0.3. The card's band comes from exceedance probabilities: the highest tier threshold with max over future target weeks of P(Y > T) ≥ 30%, from the issued quantiles (kit `quantiles.exceedance_prob`), crossed with the forecast-path trend.
  - The card shows P(> each threshold) per horizon (<1% / >99% at the clip) and the observed 3-week as-of trend (kit `phase`), which is context only.
  - G14 adds over-call and under-call contradiction checks, with tests.
- **R3-2:** a Season shape page. All complete UAE seasons are aligned on ISO wk 27, with this season and NABD's fan overlaid, plus a per-season peak/onset table.
- **R3-4:** a Bed-days SCENARIO page, permanently labelled "not a forecast of admissions".
  - Sourced defaults: 438/yr from Tawam (2,189 over 5 years), LOS 4.0 days (sourced range 4–6), cost US$2,241 from the Dubai claims.
  - The proportional-to-positivity assumption is shown and labelled unvalidated.
- **v1.6 evidence order:**
  - A sidebar "Evidence, in order" box on every page, read live from the results files: GCC blind test, then ledger, then US NOT MET with league ranks, then UAE forward-in-time parity.
  - The US page leads its UAE section with forward-in-time parity; LOSO is labelled context only.
  - The About page is rewritten with positioning.md's do-not-claim list, a real/simulated/not-built table and the new card rules.
- **Fix:** the explain caption names the model from the file (the live file is v1).
- **Tests and screenshots:** 120/120 tests pass, all 10 pages render in EN and AR, and 11 screenshots were regenerated.

## Round 4: pitch and docs (8 Nov)
- **Restructured to put impact first (BUILD-SPEC v1.7):**
  - Files: deck-script (12 slides), video-script (401 words, about 2:46), demo-script, one-pager.
  - Order: Monday decision + season shape → 2,189 burden → who decides and the cost of a wrong call → gap → NABD → Gulf test (46% vs past-season patterns, secondary; 9% vs persistence, primary) → CDC "missed our bar; 7th of 21 (13th of 41 incl. ensembles)" → UAE parity, with the post-hoc training-history reading → workforce slide → requirements → ask + ledger.
- **R3 audit fixes across pitch/ and TECHNICAL.md** (registration.md untouched):
  - Ledger: no "published/public/anchored" (it is one round re-issued; 0 scored).
  - Removed: "blind", "verified row-for-row", "fewer false alarms", unqualified "calibrated".
  - "To our knowledge" added; RSV demoted to secondary (clustered CI crosses 1); UAE "3/3 onsets" retired.
  - Horizon labels: R0/R1 = +1/+2/+3, later rounds issue-relative.
  - The hub-pin enforcement claim was removed from TECHNICAL.md.
  - The 2.9%→16% pandemic caveat was added in outreach.
- **qa.md:** all 10 of the judges' hardest questions answered first, plus workforce, data sovereignty, Gulf CDC, pricing hypothesis and ROFR. US alert late/timely counts were recomputed from `results/tables/alerts_us_detail.csv`.
- **outreach.md:** personalised to the Tawam RSV study (UAEU Pediatrics; Dr Alsuwaidi per the publication record; the corresponding author must be confirmed) and to DoH/ADPHC surveillance (public channels only). Bodies are 125–143 words.
- **Claims ledger:** rewritten to v1.7, with new sections G (workforce/business) and F13–F18 bans.
- **Open:** winter planner, bulletin and public repo/anchor are ⟦IF BUILT/IF DONE⟧ slots, so cut them on 19 Nov if they are absent. `docs/SPEC.md:80` (R2 m27) is outside the pitch scope and still needs fixing.

## Round 4: ops & integrity (2026-11-08)
- Audit R3 fixes, appended as DEVIATIONS C1–C7:
  - hub-pin enforcement implemented and tested (C1; D8(d) had claimed it falsely);
  - G1b time withdrawn, and the proxy refusal re-observed at 19:00:36Z (C2);
  - GCC exposure disclosures (C3);
  - SUMMARY Round-2 section now generated, with CI columns relabelled (C4);
  - league cache keyed on forecasts + hub SHA, with a status flag (C5);
  - GCC future-perturbation test with a positive control (C6);
  - ledger R0/R1 described as byte-identical, legacy labels documented (C7).
- Publish package:
  - docs/PUBLISH.md; scripts/prepare_public_repo.sh (full-history clean clone, plus size/licence/secret/banned-claim checks); scripts/anchor_all.sh (verify all manifests, bundle Merkle manifest, OTS + RFC 3161);
  - scripts/flusight_wednesday.sh (live hub clone via NABD_HUB) with eval/flusight_validate.py (re-implements the main hubValidations checks against tasks.json and the metadata schema) and docs/FLUSIGHT-PR.md;
  - .streamlit/config.toml, requirements.txt (app) and requirements-dev.txt; LICENSE (MIT code + data terms); root README.md.
- Dry runs: hub pin OK; the FluSight script on the LIVE hub wrote and validated the 2026-11-14 draft (file PASS; metadata only has placeholders left; stale weeks 1 on 8 Nov, so re-run Wed); anchor_all dry-run verified 3/3 manifests and built a 28-file bundle; prepare_public_repo produced a 110 MB clone with no secrets and flagged overclaims in docs/SPEC.md and research/positioning.md (not in this workstream's scope).
- Tests: 142 passed.

## Round 4 app finish (9 Nov)
- Winter planner: separate Demand and Workforce tables. Workforce columns: expected absent nurses, nurse shifts at risk, net roster gap after bank/float (floored at 0), P(gap > 0), at 10–50–90%. The arithmetic lives in `planner.workforce_scenario`, with tests for consistency and for hiding the table when no rate is given.
- One horizon convention everywhere (`data_io.display_horizon`): the primary label is the target week-ending date; the secondary is "nowcast / +N wk after issue", equal to the hashed R0/R1 `weeks_ahead_of_issue` (tested row by row). The +0.5/+1.5/+2.5 midpoint labels are removed from the card, bulletin, API, planner, bed-days, explain selector and tests. The API adds `weeks_after_issue` and `week_ending_label`.
- Plain band names in the audit table. The explain selector is labelled by week ending, and the bars have more height to stop label overlap. The banned-wording scan of app/ and bulletin/ found no hits (remaining "pre-registered" uses refer to the locked US/GCC protocols).
- Bulletin regenerated (2 pages; sha256 995aa28a…); all screenshots regenerated. 144 tests pass.

## Round 5: consistency sweep + targeted fixes (9 Nov)
- **DEVIATIONS:** U6 (post hoc UAE v1 vs seasonal analog, declared before computing), C8 (one horizon convention; supersedes C7's last clause) and C9 (wording errata for locked-generator outputs).
- **U6 result** (`results/uae/posthoc/`, exploratory):
  - pooled v1/analog: flu 0.824 (date-cluster 0.73–0.96; moving-block 0.66–1.13), RSV 0.855 (0.77–0.95; 0.72–1.03);
  - ≥2 training seasons: flu 0.607, RSV 0.675 (4/4 folds won); 1 training season: flu 2.56, RSV 1.39 (both lost);
  - unweighted flu parity (3.08 vs 3.08).
- **Banned/retired-claim sweep** across the app, pitch, TECHNICAL, the claims ledger and positioning.md (§0/§4/§6 wording superseded). Generated summaries:
  - UAE v1 and US round2 generators fixed and regenerated (labels only; summary.json values identical);
  - the GCC and UAE-v2 outputs (locked generators) are fixed by `eval/wording_errata.py`, with a numbers-preserved test.
- **App:**
  - About and season-shape wording;
  - LOSO UAE alert table labelled retired;
  - honest ledger count;
  - plain GCC labels;
  - every explain bar described, with a mean-reversion gloss;
  - planner absence driver flu/RSV/both (default both) + tests;
  - Streamlit toolbar minimal; screenshots retaken.
- **Deck** (live artifact): pain slide → flu season-shape chart + "timing and shape change from year to year"; slide 6 → Monday line + exceedance table; slide 7 → two-comparator Gulf chart (`eval/deck_figures.py`); slide 8 de-cluttered; slide 9 → post hoc analog card replaces the US card; slide 10 → workforce scenario callout; slides 5/11/12 wording.
- **Publish scan** extended to results/ and bulletin/, plus new banned terms.
- **Tests:** 147 pass.
