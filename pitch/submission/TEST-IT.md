# Test NABD yourself: what to do, and what you should see

Everything below was run on 15 Nov 2026 on this laptop. Run the commands from the project folder.

## 1. One-minute health check
```bash
.venv/bin/python -m pytest -q
```
Expect the last line to read `157 passed` (plus some warnings). Any `failed` is a real problem.

## 2. The web page (what a judge will open)
```bash
.venv/bin/python -m web.build && .venv/bin/python -m http.server 8600 --directory web/dist
```
Open http://localhost:8600 and try these (if the second command says the address is already in use, the page is already being served: just open the link):

| Do this | Expect |
|---|---|
| Look at the top panel "This week in the UAE" | RSV 10.5% and Influenza 26.9% (last published week, 2026-W44), "ledger round R2" |
| Press العربية (top right) | The whole page flips right-to-left in Arabic; press English to return |
| Press ◐ | Light and dark theme switch |
| "This week's card": press Influenza, then "Pooled challenger" | The chart changes; a note says the hashed headline is still the own-record model |
| In "A named person decides", press "Record the decision" with the name empty | A red message: no decision is recorded without a name |
| Type any name, choose Modify, press "Record the decision" | An entry "#1 · Modified · your name" with a timestamp and a hash appears in the session log |
| "Decisions": press "▶ Play the season" | Bangladesh 2025/26 plays week by week; the four tallies count missed and wasted weeks |
| "The ledger": press "Verify all" | Nine green "✓ matches": your browser recomputed each file's SHA-256 |
| "All results" | Seven cards, including the US one marked "Bar not met" (1.22) |

## 3. The tamper test (shows the hashes mean something)
```bash
cp ledger/2026-11-14T1947Z_NABD-Pool.csv /tmp/tampered.csv && echo "x" >> /tmp/tampered.csv
shasum -a 256 ledger/2026-11-14T1947Z_NABD-Pool.csv /tmp/tampered.csv
```
Expect the first hash to start `cf8a86c7febec589…` (the value recorded in `ledger/2026-11-14T1947Z_NABD-Pool.sha256`) and the second to be completely different.

## 4. The weekly ledger command (safe to run any time)
```bash
.venv/bin/python -m ledger.weekly --cached --no-issue
```
Expect `"latest_round": "R2"`, `"latest_published_week": "2026-W44"`, `"scored_rows": 0`, `"issued": null`, then "No new FluNet week since the last round". When WHO publishes week 45, run `.venv/bin/python -m ledger.weekly --fetch --with-pool`: `scored_rows` becomes greater than 0 and a round R3 is issued.

## 5. The locked UAE test
```bash
.venv/bin/python -m ledger.live_test --cached
.venv/bin/python -m ledger.live_test --cached --final
```
The first prints `"status": "INTERIM (descriptive only)"`, `"rounds_issued": ["R2"]`, `"scored_cells_per_model": 0`. The second must refuse: "final assessment is not allowed before 2027-04-15".

## 6. The analyst workbench
```bash
.venv/bin/streamlit run app/streamlit_app.py
```
Opens at http://localhost:8501. On "Weekly card" the model shown is `NABD-UAE-v1`. Submit the approval form without a name: an error. With a name: "recorded · #N" and the entry appears under the audit log, which reports the hash chain as valid. "Borrowed strength (18 countries)" shows the green MET banner with 0.767.

## 7. The API
```bash
.venv/bin/uvicorn app.api:app --port 8000
```
- http://localhost:8000/health returns `{"status":"ok","observed_last_week":"2026-W44","forecast_source":"results"}`.
- http://localhost:8000/forecast?target=wk%20rsv%20pos%20pct%20sentinel returns model `NABD-UAE-v1`, issue date `2026-11-14`, four target weeks with 23 quantiles each (the first week's median is about 12.4%).
- An unknown target returns HTTP 422 with the list of valid targets.
