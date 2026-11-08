# NABD demo script (3:00), round 2

**Rules:**
- Show only what runs.
- Beats marked ⟦IF BUILT: file⟧ depend on round-2 outputs. If the file is missing on 19 Nov, **skip the beat**; don't narrate it.
- Use the extended beats marked [+] if the finale format gives 7 minutes (the generic T&C clause).
- Launch: `streamlit run app/streamlit_app.py` (see `app/README.md`).

| Time | Screen | Say (approx.) |
|---|---|---|
| 0:00–0:25 | Four UAE RSV seasons overlaid (FluNet), with Tawam and Dubai callouts | "RSV peaked in week 42, then 41, 41 and 47. One Abu Dhabi hospital admitted 2,189 young children with RSV in five years, and positivity swung five-fold between years. The UAE publishes no forecast, so planners work from last week's numbers." |
| 0:25–1:15 | **Weekly card (EN, then the AR toggle):** last published week, lag badge ("7 days"), fan chart, horizons *nowcast / +0.5 / +1.5 / +2.5 wk*, persistence line alongside | "This is this week's card. WHO publishes about a week late, so the first horizon is a nowcast, and the card says so. The dashed line is what you'd guess by carrying last week forward. We always show it, so nobody trusts us blindly." |
| | ⟦IF BUILT: results/uae/explain/⟧ **Why this forecast** panel | "These are the signals that moved this forecast, and by how much. This is exact, not a guess: the model is linear, so each contribution adds up to the forecast." |
| | Playbook action for **bed and roster manager**. Enter a name, choose **Approve** with a reason code; the audit line appears with its hash | "The system proposes; a named person decides. Every decision is chained into a log that shows if anyone edits it later." |
| 1:15–1:45 | **Ledger receipt page:** round R0, issued ⟦LIVE: date⟧, SHA-256 shown; ⟦IF SCORED: realised week inside/outside the band⟧ | "This forecast was hashed before WHO published the answer. ⟦If scored:⟧ here's where the truth landed. ⟦If anchored:⟧ the timestamp is held outside our team." |
| 1:45–2:25 | **UAE proof, then US proof** (red NOT MET badge) | "In the UAE, against carrying last week forward, NABD cut error by about a quarter and won 7 of 8 season-series: four seasons, retrospective. In the US we held ourselves to the CDC's ensemble with a frozen test, scoring 1.22 against a bar of 1.15. We missed it, and we show where." |
| 2:25–2:45 | ⟦IF BUILT: results/gcc/⟧ **Gulf panel**, else the **Alerts** panel | Gulf: "Same frozen method, other Gulf countries' data, plan locked before download: ⟨result, every country⟩." Alerts: "Our alerts weren't earlier than anyone's, but they were right more often." |
| 2:45–3:00 | Pilot slide | "Give us one hospital's aggregate admissions for twelve weeks in shadow mode. If we don't beat your own census by 10%, you walk away, and our record stays public either way." |

[+] Extended beats (7-minute format):
- **Leakage test (30 s):** run `pytest tests/test_vintage.py` live, plus the deliberate-leak test that must fail.
- **Missing-feed behaviour (20 s):** `results/tables/dropout_us.csv` shows ×1.41 for one missing week, and why v2 adds independent signals.
- **Workforce module (20 s):** k-anonymous aggregation on synthetic data, with the SIMULATED watermark visible.
- **Plug-in story (30 s):** the ADPHC platform, the DoH population-health platform, the Rasid offer.

**Do not demo:**
- an "Explain" view if the explain files aren't there;
- a "remove ED feed" toggle (there is no ED feed);
- Chronos-2;
- any exploratory (E1) number.

**Fallbacks:**
- If a live fetch fails, use the cached build, with the badge showing "cached ⟨date⟩".
- If the app crashes, play the recorded video.
