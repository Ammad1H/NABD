# NABD app

```bash
pip install -r requirements-app.txt
streamlit run app/streamlit_app.py          # UI on :8501
uvicorn app.api:app --port 8000              # API on :8000, OpenAPI docs at /docs
pytest tests/test_app_audit.py -q            # audit chain, playbook schema, API schema, workforce suppression
docker compose up --build                    # both services (audit log persists in app/audit/)
```

**Data sources.** The app reads only interface-contract paths (docs/BUILD-SPEC.md v1.1):
- Weekly card: latest live round in `ledger/<UTC>_<model>.csv`, then `results/uae/forecasts/`, then DEMO data.
- US proof: `results/summary.json` and `results/tables/`.
- UAE retrospective: `results/uae/`.
- Feed removal: `results/tables/ablation*.csv`.

Any fallback shows a **DEMO DATA** banner. Demo tables contain no numbers, so they can't be mistaken for results.

**Governance features.**
- Each decision needs a named approver and a reason code. `OTHER` requires a note, and `MODIFY` requires the modified action text.
- Decisions go to `app/audit/audit.jsonl`, which is append-only and SHA-256 hash-chained. `verify_chain` detects edits, deletions, insertions and reordering.
- The playbook (`playbook/playbook.yaml`) is **ILLUSTRATIVE** pending clinical and public-health review. It is schema-validated, and bands must not overlap.
- The workforce page is fully **SIMULATED**. It uses additive secret sharing across 3 servers, plus k-anonymity suppression at the employer level.

Screenshots: `app/screenshots/`.
