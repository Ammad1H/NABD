# Pre-registration: prospective UAE test of the pooled model on the live ledger (season 2026/27)

Written 14 Nov 2026, before WHO published UAE week 2026-W45 and before any NABD-Pool forecast for the UAE had been issued on the ledger. Locked with the kit `prereg.lock` (`docs/LOCK-LIVE.json`): this plan + the issue, scoring and model code listed in `ledger/live_lock.py` + the pooled model's configuration. After the lock this file is not edited; deviations go in `docs/DEVIATIONS.md` (L-series). The lock time is self-attested in local git until anchored outside the team.

## 1. Why
The borrowed-strength test (S1) was confirmatory for 18 held-out countries, not for the UAE: UAE data had been seen, so the UAE figure (pooled / own-record 0.87) is non-confirmatory. The only way to get confirmatory UAE evidence is forward in real time. This plan fixes that test before its first data point exists.

## 2. Hypothesis
**H-live.** For UAE sentinel influenza positivity in the 2026/27 season, forecasts from the pooled model (NABD-Pool, lock #2 configuration, `pool/live.py`) have lower WIS than forecasts from the own-record model (NABD-UAE-v1, `uae/models.py`) issued in the same rounds from the same data.

## 3. What is already known (exposure)
- UAE FluNet data through 2026-W44, and every retrospective UAE result in `results/`.
- Rounds R0 and R1 (8 Nov 2026) carry no pooled forecast and are **excluded**.
- No pooled UAE ledger forecast and no W45 value existed when this was written.

## 4. Rounds
- A round is issued by `python -m ledger.weekly --fetch --with-pool` (or `ledger.issue --with-pool`) each time WHO publishes a new UAE sentinel week, starting with **R2 on 14 Nov 2026** (data through 2026-W44).
- Each round hashes three forecasts made from the same data: NABD-UAE-v1, NABD-Pool, persistence (NABD-UAE-v2 is also hashed and reported, not part of the hypothesis). Horizons: 1–4 data weeks after the last published week.
- Included rounds: every round from R2 whose target weeks end on or before **Sunday 28 March 2027**, whose files pass the SHA-256 check, and that contains all three models. Missed weeks (no round issued) are listed, never back-filled.
- Integrity rule: a round should be committed (and, once the repository is public, pushed and anchored) before WHO publishes its first target week. Rounds for which that cannot be shown are flagged in the report and excluded in a sensitivity analysis.

## 5. Models are frozen
No change to `uae/models.py`, `pool/` or `pool/model_config.json` during the test. NABD-Pool is refitted each round on the development-country data in `data/raw/flunet_pool_dev.csv` (unchanged) plus the UAE's own data to the origin, exactly as `pool/live.py` does now. Any change of method is a new model name and a logged deviation; the hypothesis is assessed on the frozen pair only.

## 6. Truth and scoring
- Truth: UAE sentinel positivity (INF_ALL or RSV / SPEC_PROCESSED_NB × 100) from the official WHO FluNet xMart API.
- **Final scoring:** the first pull on or after **15 April 2027** (revised values). Interim scoring uses whatever is published at the time and is labelled interim.
- Score: WIS on the 23 quantiles (`uae/scoring.py`), on cells where all three models have a forecast and the target is published. Implementation: `ledger/live_test.py`.

## 7. Endpoints
- **Primary:** relative WIS, NABD-Pool / NABD-UAE-v1, influenza, summed over all included rounds and horizons. 95% CI by bootstrap over rounds (B = 2000, seed 0). **MET if the ratio is below 1 and the upper bound is below 1; otherwise NOT MET.** Assessed once, at final scoring.
- **Key secondaries (same statistic):** (1) RSV; (2) NABD-Pool / persistence, influenza and RSV; (3) NABD-UAE-v1 / persistence.
- **Other:** by horizon; 50% and 95% interval coverage; a moving-block bootstrap over rounds (block length 4) as a sensitivity, because consecutive rounds share target weeks.
- **Power, stated in advance:** at most about 19 weekly rounds remain in the window. Intervals will be wide; "NOT MET" with a ratio below 1 is a likely outcome and will be reported as such.

## 8. Interim looks
The scoreboard is public by design, so interim numbers are visible every week. They are descriptive only: no model change, no early stopping, no claim. At the hackathon submission (20 Nov 2026) at most one or two target weeks will be scored.

## 9. Reporting
Every included and excluded round is listed with the reason. The result is reported whichever way it falls, including by horizon and by pathogen.

## 10. Sign-off
NABD team build, 14 Nov 2026. Self-attested until `scripts/anchor_all.sh` is run and the repository is pushed.
