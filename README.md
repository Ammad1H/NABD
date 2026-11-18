# NABD (نبض, "pulse"): the next three weeks of RSV and flu for Abu Dhabi, with a human sign-off

**Statement 06 · Population and Workforce Health Early Warning** · [Live page](https://ammad1h.github.io/NABD/) (no login) · [NABD in plain words](pitch/NABD-in-plain-words.md)

**Who uses it.** A hospital bed and roster manager, a public-health duty officer or an immunisation lead, each week of the respiratory season.

**What they get.** One Arabic/English card: the chance that RSV and influenza positivity cross each pressure threshold, from a nowcast to about 2.5 weeks after issue, and one proposed action per role. A named person approves, modifies or dismisses it with a reason, and every decision goes into a hash-chained log.

**Why it matters.** UAE influenza peaked in October one season and in February the season before. One Abu Dhabi hospital (Tawam) admitted 2,189 children aged five or under with RSV in 2018–22. Planning from last week's numbers or last year's pattern misses those shifts.

**Why trust it.**
- **18 held-out countries, plan locked before their data were downloaded:** a model trained across countries' WHO records had 23% less influenza forecast error than each country's own-record model (0.767, 95% CI 0.681–0.832), better in all 18.
- **The UAE's own seasons (development check, not a confirmatory test):** the same pooled model, forward in time with the UAE left out of its fit, had a relative error of 0.77 against repeating last week (95% CI 0.70–0.86), better in both scored seasons. The UAE's own-record model only ties last week over four seasons (1.00). [`results/pool/uae_devcheck/`](results/pool/uae_devcheck/SUMMARY.md)
- **Where it falls short, it says so.** Against the CDC's combined forecast in the US it missed its own pre-set bar (1.22 against 1.15). In a two-week roster decision it cannot yet be told apart from "repeat last week".
- **The confirmatory UAE test runs forward.** Each forecast file is hashed before WHO publishes the week it covers, and the test that will judge the pooled model on the UAE was locked on 14 Nov 2026 (self-attested in git until anchored; see Timestamps below).

**The ask.** One hospital, 12 weeks, aggregate weekly counts, shadow mode, with the exit test set in advance ([`docs/PILOT-DATA-SPEC.md`](docs/PILOT-DATA-SPEC.md)).

## Evidence, reported in full (numbers from `results/`)

| What | Result | Status |
|---|---|---|
| **Borrowed-strength test** on 18 held-out countries (`docs/PREREG-POOL.md`; plan locked before download, model locked before any held-out row was extracted; scored once) | A model pooled across countries (NABD-Pool) vs each country's own-record model, influenza relative WIS **0.767 (95% CI 0.681–0.832)**: primary criterion met, better in 18 of 18 countries. Short-history country-seasons: 0.624 (0.540–0.705). vs last-week persistence: 0.879 (0.850–0.901) | `results/pool/SUMMARY.md`; deviation P1 |
| Foundation-model benchmark (post hoc, exploratory): `amazon/chronos-2` zero-shot on the same held-out forecasts | Level with NABD-Pool: 1.026 (0.993–1.055). Both beat the own-record model by about a fifth (Chronos-2 0.787). The gain from borrowing is not specific to our model | `results/fm/SUMMARY.md`; deviation W1 |
| Prospective UAE test on the live ledger (`docs/PREREG-LIVE.md`, locked 14 Nov 2026) | Pooled vs own-record model, season 2026/27; first round R2 hashed before WHO published week 45; **no result yet**, final assessment on or after 15 April 2027 | `ledger/LIVE-TEST.md` |
| Test of the frozen UAE method on Oman, Qatar and Saudi Arabia (`docs/PREREG-GCC.md`, locked in git before their data were downloaded) | Influenza relative WIS vs last-week persistence **0.914 (95% CI 0.843–0.983)**: primary criterion met. vs a past-season (analog) baseline: 0.536 (secondary). RSV vs persistence: 0.798 (secondary; not robust to country clustering, see docs/REVIEW-R3-audit.md #9) | `results/gcc/SUMMARY.md`; deviations G1, G1b, C2, C3 in `docs/DEVIATIONS.md` |
| US benchmark against the CDC FluSight ensemble (`docs/PROTOCOL.md`, frozen before test-season scoring) | Relative WIS **1.22 (95% CI 1.01–1.52)**: **non-inferiority NOT MET**. Among individual hub models: 7th of 21 (2024/25), 19th of 25 (2025/26) | `results/SUMMARY.md` |
| UAE's own record, forward-in-time check | v1 vs persistence ≈ 1.00 (parity) on a short four-season record | `results/uae/SUMMARY.md` |
| UAE development check, pooled model (post hoc, NON-CONFIRMATORY: UAE was a development country) | Forward in time, UAE left out of the pooled fit, influenza 2024/25–2025/26: vs persistence **0.772 (95% CI 0.698–0.861)**, better in both seasons (0.84, 0.71); vs UAE own-record v1 0.868 (0.752–0.996), v1 better in 2025/26 | `results/pool/uae_devcheck/SUMMARY.md`; deviation S7 |
| Decision replays (post hoc, exploratory): a pre-declared roster rule applied to the frozen forecasts | Gulf influenza: 8.0 mismatch weeks a season vs 20.8 for the past-season pattern; a tie with last week (8.0). Held-out countries, pooled model: 10.5 vs 12.3 for the own-record model (difference −1.81, 95% CI −3.00 to −0.72); not distinguishable from last week (11.1) | `results/replay/SUMMARY.md`; `results/replay/pool/SUMMARY.md`; deviations V1, V2 |
| UAE v2 multi-signal challenger (`docs/PROTOCOL-UAE-v2.md`, locked before scoring) | No improvement over v1 (1.06) | `results/uae/SUMMARY.md` |

**Timestamps.** All locks, freezes and ledger rounds are git commits made by the author (a solo entrant), so they are self-attested **until they are anchored by an outside service** (OpenTimestamps / RFC 3161 / Zenodo). Anchoring status: see `anchors/`. If that folder is absent, nothing has been anchored yet. How to anchor: `docs/PUBLISH.md`.

**How this was built.** One entrant, with AI coding assistance (Claude Code) for code and documents, all directed and reviewed by the entrant. Files named `docs/REVIEW-*` and the two reviewer notes in `research/` are simulated reviews written by an AI assistant in separate sessions; each says so at the top. No human or external party has reviewed NABD yet.

## Quick start
```bash
pip install -r requirements-dev.txt
python -m web.build && python -m http.server 8600 --directory web/dist   # the presentation front-end (static, Arabic/English): http://localhost:8600
streamlit run app/streamlit_app.py           # the analyst workbench: audited approvals, planner, every table
pytest -q                                     # full test suite
python -m eval.run_all --fetch                # US back-test (clones the CDC hub at the pinned commit)
python -m uae.backtest_v2 --cached && python -m uae.gcc --score   # UAE v2 and GCC (GCC refuses to score unless the lock verifies)
python -m replay.run && python -m replay.pool_replay              # decision replays (post hoc; read-only on the locked forecasts)
python -m pool.uae_devcheck && python -m eval.gcc_robustness      # UAE development check (S7) and GCC robustness, from committed scores
```

## Where things are
- `docs/TECHNICAL.md`: architecture, models, protocols, results, limitations
- `docs/PROTOCOL*.md`, `docs/PREREG-GCC.md`, `docs/FREEZE.md`, `docs/LOCK-*.json`: pre-specified plans and locks
- `docs/DEVIATIONS.md`: every deviation and correction, appended and never edited
- `web/`: the static presentation front-end; `python -m web.build` regenerates `web/dist/` from the results and ledger files (no number is typed by hand)
- `fm/`, `results/fm/`: the zero-shot foundation-model benchmark (optional `requirements-fm.txt`)
- `pitch/story.md`: the current narrative and 3-minute voiceover
- `pitch/submission/`: the filled challenge template (`build_deck.py`), form answers, a test walkthrough and hosting steps
- `pool/`, `results/pool/`: the pooled model and its held-out test; `replay/`, `results/replay/`: decision replays
- `ledger/`: hashed forecast rounds and scoring (`ledger/README.md`)
- `docs/PILOT-DATA-SPEC.md`: what a hospital would share for a shadow pilot (aggregate, suppressed)
- `docs/DEPLOYMENT-PLAN.md`: status against the six Statement 06 requirements, the pilot week by week, and how NABD would run in service
- `docs/RUNBOOK.md`, `docs/PUBLISH.md`: weekly operations, publishing and anchoring

## Data and licence
Code: MIT (`LICENSE`). Data: WHO FluNet (public-health, non-commercial use with attribution) and the CDC FluSight hub; see the data terms in `LICENSE`. No personal or patient-level data is used anywhere.
