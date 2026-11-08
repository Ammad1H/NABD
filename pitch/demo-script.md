# NABD demo script (3:00), round 3 (v1.6 evidence order)

**Rules:**
- Show only what runs. Beats marked ⟦IF BUILT: …⟧ depend on round-3 outputs; if they're missing on 19 Nov, **skip the beat** and don't narrate it.
- The stop list in `research/positioning.md` §4.6 is binding.
- Extended beats [+] are for a 7-minute finale format.
- Launch: `streamlit run app/streamlit_app.py` (see `app/README.md`). Pages: Weekly card · Alerts · US proof · GCC test · Ledger · Feed removal · Workforce (SIMULATED) · About.

| Time | Screen | Say (approx.) |
|---|---|---|
| 0:00–0:25 | ⟦IF BUILT: season-shape panel⟧, else a static overlay of 4 UAE seasons from `data/raw/flunet_are.csv` | "In WHO's own UAE lab data, flu spiked above forty per cent in October 2025. The year before, it plateaued for five months and peaked in February. RSV peaked anywhere from week 41 to 47. One Abu Dhabi hospital admitted 2,189 young children with RSV in five years. Nobody publishes a forecast." |
| 0:25–1:10 | **Weekly card (EN, then the AR toggle):** last published week, lag badge, fan chart, horizons *nowcast / +0.5 / +1.5 / +2.5 wk*, persistence line alongside. ⟦IF BUILT: exceedance probabilities + trend arrow⟧ | "This is this week's card. WHO publishes about a week late, so the first horizon is a nowcast, and the card says so. The dashed line is what you'd guess by carrying last week forward. We always show it, so nobody trusts us blindly." ⟦IF BUILT:⟧ "This number is the chance RSV positivity crosses the surge threshold in each of the next weeks." |
| | **Why this forecast** panel (`results/uae/explain/`) | "These are the signals that moved this forecast, and by how much. The model is linear, so the contributions add up exactly to the forecast. This is not a guess." |
| | Playbook action for **bed and roster manager**. Enter a name, choose **Approve** with a reason code; the audit line appears with its hash | "The system proposes; a named person decides. Every decision is chained into a log that shows if anyone edits it later. A card that contradicts itself can't even render." |
| 1:10–1:45 | **GCC test page** (headline evidence) | "We froze the method, locked the test plan, then opened Oman, Qatar and Saudi data nobody on the team had seen. Against 'next week equals this week' it cut error by about nine per cent for flu (CI 0.84 to 0.98) and twenty per cent for RSV. Here are the losses too: Oman twice, a tie in Qatar, and Saudi RSV last season." |
| 1:45–2:05 | **Ledger page:** rounds R0 and R1 with hashes; scoreboard | "Every forecast is hashed before WHO publishes the answer. As of today nothing has been scored yet, because the target weeks haven't been published. ⟦IF DONE:⟧ The timestamp is held outside our team. ⟦else:⟧ The timestamps are self-attested until we anchor them." |
| 2:05–2:35 | **US proof page** (red NOT MET badge, league table) | "In the US we held ourselves to the CDC's FluSight ensemble with a frozen test: 1.22 against a bar of 1.15. Not met. Among individual CDC-hub models we placed seventh of twenty-one in 2024/25, and fell to the baseline in 2025/26. We show you the season we lost." |
| 2:35–2:45 | **About page:** real / simulated / not built | "In the UAE's own short record, forward in time, we tie with persistence, and our multi-signal version didn't help. That's exactly why the ledger runs every week." |
| 2:45–3:00 | Pilot slide | "Give us one hospital's aggregate counts for twelve weeks in shadow mode. If we don't beat your own census carried forward, you walk away, and our record stays public either way." |

[+] **Extended beats (7-minute format):**
- **Alerts page (30 s):** onset lead is 0 weeks for every rule; precision is where NABD differs (US 0.65/0.76 vs CDC 0.41/0.67; UAE flu 3/3 caught, 0 false alarms, n = 3 onsets). Say "diagnostic".
- **Feed removal (20 s):** removing non-sentinel or calendar data didn't make forecasts worse. We say so, and v2 stays a challenger.
- **Leakage test (30 s):** run `pytest tests/test_vintage.py` live, plus the deliberate-leak test that must fail.
- **Lock guard (20 s):** edit one line of `uae/gcc.py`, rerun `python3 -m uae.gcc --score`, and show it refuse (`GoalpostError`). Revert afterwards.
- **Workforce module (20 s):** k-anonymous aggregation on synthetic data, with the SIMULATED watermark visible.
- ⟦IF BUILT⟧ **Bed-days scenario (20 s):** "This is a scenario, not a forecast of admissions: with your baseline, here is the range of RSV bed-days at stake."

**Do not demo:**
- Chronos-2;
- any E1 number;
- the UAE LOSO 0.76/0.78 as a headline;
- v2 as better;
- "early warning";
- an ED or weather feed (there is none).

**Fallbacks:**
- If a live fetch fails, use the cached build with the badge showing "cached ⟨date⟩".
- If the app crashes, play the recorded video.
