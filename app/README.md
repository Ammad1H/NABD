# NABD app

```bash
pip install -r requirements-app.txt
streamlit run app/streamlit_app.py          # UI on :8501
uvicorn app.api:app --port 8000              # API on :8000, OpenAPI docs at /docs
pytest tests/test_app_audit.py tests/test_app_cardcheck.py -q   # audit, playbook, API, G14 card checks, all pages EN/AR
python app/take_screenshots.py               # PNGs of every page into app/screenshots/ (needs playwright + chromium)
docker compose up --build                    # both services (audit log persists in app/audit/)
```

## Pages and the files they read (docs/BUILD-SPEC.md v1.1–v1.4)

| Page | Reads | If missing |
|---|---|---|
| Weekly card | latest live round `ledger/<UTC>_<model>.csv`, else `results/uae/forecasts/`; explanations from `results/uae/explain/<issue_date>_<target>.csv` | Forecasts fall back to **DEMO DATA** with a banner. Explanations show "not yet computed". |
| Alerts | `results/tables/alerts_us.csv`, `latency_us.csv`, `dropout_us.csv`; `results/uae/tables/alert*.csv` | "not yet computed" |
| US proof | `results/summary.json` (`primary_verdict` / `primary_text`, else `primary.non_inferiority`), `results/tables/*.csv`, `results/figures/`, league tables `results/tables/league*.csv` | "not yet computed" |
| GCC out-of-sample | `results/gcc/summary.json`, `results/gcc/tables/*.csv`, figures | "not yet computed" |
| Ledger receipt | `ledger/*.csv` + `.sha256` | DEMO with a banner |
| Feed removal | `results/uae/tables/ablation.csv` (feed, metric, full, without, delta) | "not yet computed" |
| Workforce | synthetic only | always shown as **SIMULATED** |
| About | builds a live real / simulated / not built table from which files exist | n/a |

Results panels never show demo numbers. Exploratory analyses (E1) appear only inside an expander labelled
EXPLORATORY.

## The weekly card cannot contradict itself (G14)

`app/cardcheck.py` builds every card:
- **Direction facts.** P(rise), P(fall), P(stable) at the first target week after issue come from the forecast
  quantiles, using vendor `nabd_kit.card`.
- **Playbook band.** Chosen by level (median) and forecast path: rising if the furthest median is at least 1.15× the
  last value, falling if it is at most 0.87× the last value.
- **Consistency check.** `card_problems` re-derives everything. Any contradiction blocks the action and the approval
  form, for example:
  - a "rising" band with a falling path or a `likely_down` label;
  - a falling band with `likely_up`;
  - a tier-3 surge band where P(above the high-pressure level) is below 30%.

  `tests/test_app_cardcheck.py` includes a deliberately contradictory card that must fail.

The observed change since the previous week is shown as a separate fact. It never drives the band.

## Horizons

Horizons are measured from the issue date to the **middle** of each target week: nowcast, +0.5, +1.5 and +2.5 wk.
This follows docs/SPEC.md §5.1.

Note: the ledger metadata (`ledger/*.meta.json`) currently uses an end-of-week convention (+1.0, +2.0, +3.0). The
data workstream should align the labels. The forecast values are unaffected.

## Governance

- **Approval.** Each decision needs a named approver and a reason code. `OTHER` requires a note, and `MODIFY`
  requires the modified action text.
- **Audit log.** Decisions go to `app/audit/audit.jsonl`, which is append-only and SHA-256 hash-chained.
  `verify_chain` detects edits, deletions, insertions and reordering.
- **Playbook v0.2** (`playbook/playbook.yaml`) is **ILLUSTRATIVE**, pending clinical and public-health review.
  - Bands are keyed on level and trajectory, and include falling and plateau bands.
  - It is schema-validated, and bands must not overlap.
  - A band named "rising" may fire only on a rising trend.
- **Workforce page.** Fully **SIMULATED**. It uses additive secret sharing across 3 servers plus k-anonymity
  suppression at the employer level, and it feeds no forecast.

Screenshots: `app/screenshots/`.
