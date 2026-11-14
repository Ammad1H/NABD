# NABD (نبض, "pulse"): open RSV and influenza forecasts for Abu Dhabi


NABD turns WHO FluNet surveillance into probabilistic weekly forecasts of RSV and influenza positivity, from a nowcast to about 2.5 weeks after issue. A bilingual (Arabic/English) card proposes a proportionate action for a named role, and only a person can approve, modify or dismiss it. Every decision goes into a hash-chained audit log. Each forecast round is hashed before its outcome exists.

## Evidence, reported in full (numbers from `results/`)

| What | Result | Status |
|---|---|---|
| **Borrowed-strength test** on 18 held-out countries (`docs/PREREG-POOL.md`; plan locked before download, model locked before any held-out row was extracted; scored once) | A model pooled across countries (NABD-Pool) vs each country's own-record model, influenza relative WIS **0.767 (95% CI 0.681–0.832)**: primary criterion met, better in 18 of 18 countries. Short-history country-seasons: 0.624 (0.540–0.705). vs last-week persistence: 0.879 (0.850–0.901) | `results/pool/SUMMARY.md`; deviation P1 |
| Test of the frozen UAE method on Oman, Qatar and Saudi Arabia (`docs/PREREG-GCC.md`, locked in git before their data were downloaded) | Influenza relative WIS vs last-week persistence **0.914 (95% CI 0.843–0.983)**: primary criterion met. vs a past-season (analog) baseline: 0.536 (secondary). RSV vs persistence: 0.798 (secondary; not robust to country clustering, see docs/REVIEW-R3-audit.md #9) | `results/gcc/SUMMARY.md`; deviations G1, G1b, C2, C3 in `docs/DEVIATIONS.md` |
| US benchmark against the CDC FluSight ensemble (`docs/PROTOCOL.md`, frozen before test-season scoring) | Relative WIS **1.22 (95% CI 1.01–1.52)**: **non-inferiority NOT MET**. Among individual hub models: 7th of 21 (2024/25), 19th of 25 (2025/26) | `results/SUMMARY.md` |
| UAE's own record, forward-in-time check | v1 vs persistence ≈ 1.00 (parity) on a short four-season record | `results/uae/SUMMARY.md` |
| Decision replays (post hoc, exploratory): a pre-declared roster rule applied to the frozen forecasts | Gulf influenza: 8.0 mismatch weeks a season vs 20.8 for the past-season pattern; a tie with last week (8.0). Held-out countries, pooled model: 10.5 vs 12.3 for the own-record model (difference −1.81, 95% CI −3.00 to −0.72); not distinguishable from last week (11.1) | `results/replay/SUMMARY.md`; `results/replay/pool/SUMMARY.md`; deviations V1, V2 |
| UAE v2 multi-signal challenger (`docs/PROTOCOL-UAE-v2.md`, locked before scoring) | No improvement over v1 (1.06) | `results/uae/SUMMARY.md` |

**Timestamps.** All locks, freezes and ledger rounds are git commits made by the team, so they are self-attested **until they are anchored outside the team** (OpenTimestamps / RFC 3161 / Zenodo). Anchoring status: see `anchors/`. If that folder is absent, nothing has been anchored yet. How to anchor: `docs/PUBLISH.md`.

## Quick start
```bash
pip install -r requirements-dev.txt
streamlit run app/streamlit_app.py           # the decision card and evidence pages
pytest -q                                     # full test suite
python -m eval.run_all --fetch                # US back-test (clones the CDC hub at the pinned commit)
python -m uae.backtest_v2 --cached && python -m uae.gcc --score   # UAE v2 and GCC (GCC refuses to score unless the lock verifies)
python -m replay.run && python -m replay.pool_replay              # decision replays (post hoc; read-only on the locked forecasts)
```

## Where things are
- `docs/TECHNICAL.md`: architecture, models, protocols, results, limitations
- `docs/PROTOCOL*.md`, `docs/PREREG-GCC.md`, `docs/FREEZE.md`, `docs/LOCK-*.json`: pre-specified plans and locks
- `docs/DEVIATIONS.md`: every deviation and correction, appended and never edited
- `pool/`, `results/pool/`: the pooled model and its held-out test; `replay/`, `results/replay/`: decision replays
- `ledger/`: hashed forecast rounds and scoring (`ledger/README.md`)
- `docs/PILOT-DATA-SPEC.md`: what a hospital would share for a shadow pilot (aggregate, suppressed)
- `docs/RUNBOOK.md`, `docs/PUBLISH.md`: weekly operations, publishing and anchoring

## Data and licence
Code: MIT (`LICENSE`). Data: WHO FluNet (public-health, non-commercial use with attribution) and the CDC FluSight hub; see the data terms in `LICENSE`. No personal or patient-level data is used anywhere.
