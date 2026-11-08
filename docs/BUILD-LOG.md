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
