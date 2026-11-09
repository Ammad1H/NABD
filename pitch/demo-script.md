# NABD demo script (3:00), round 4 (impact first, BUILD-SPEC v1.7)

**Rules:**
- Show only what runs. Beats marked ⟦IF BUILT: …⟧ / ⟦IF DONE: …⟧ depend on round-4 work. If it's missing on 19 Nov, **skip the beat** and don't narrate it.
- The stop list (`research/positioning.md` §4.6) and the v1.7 BANNED list are binding.
- Extended beats [+] are for a 7-minute finale format.
- **Launch:** `streamlit run app/streamlit_app.py` (see `app/README.md`).
- **Pages:** Weekly card · Season shape · Bed-days scenario · Hospital winter planner · GCC out-of-sample · Ledger receipt · US proof · Alerts · Feed removal · Workforce (simulated) · About.

| Time | Screen | Say (approx.) |
|---|---|---|
| 0:00–0:25 | **Season shape** page (RSV, then the influenza toggle) | "Every winter week, a paediatric bed manager and a public-health duty officer in Abu Dhabi plan the next three weeks of RSV and flu. Their defaults are last week's numbers and last year's pattern. But look: flu peaked in October 2025 and in February the season before, and the RSV peak moved six weeks. One Abu Dhabi hospital admitted two thousand one hundred and eighty-nine young children with RSV in five years. To our knowledge, no one gives these desks a checkable forecast." |
| 0:25–1:05 | **Weekly card (EN, then the AR toggle):** lag badge, fan chart, forecasts labelled by week ending, *nowcast / +1 / +2 / +3 wk after issue*, persistence line, **exceedance table** and direction | "This is this week's card. WHO publishes about a week late, so the first horizon is a nowcast, and the card says so. This line is what the bed manager reads: the chance RSV positivity crosses the playbook thresholds in each of the next weeks, and which way it's heading. Today that's 'elevated, falling', so no surge roster, and plan stand-down if next week confirms it. The dashed line is last week carried forward. We always show it, so nobody trusts us blindly." |
| | **Why this forecast** panel | "These are the terms that moved this forecast, and by how much. The model is linear, so they add up exactly to the forecast." |
| | Playbook action, **Approve** with a reason code → the audit line appears | "The system proposes; a named person decides. Every decision is chained into a log that shows if anyone edits it later. A card that contradicts itself can't render." |
| 1:05–1:20 | **Hospital winter planner** | "For the hospital, the wave becomes its own constraints, beds and staff, in AED, from its own inputs. It's labelled a scenario, because it is one." |
| 1:20–1:55 | **GCC out-of-sample** page | "Then the test we couldn't tune for. We froze the method, locked the plan, and only then downloaded Oman, Qatar and Saudi data. Against planning from past-season patterns, influenza forecast error fell forty-six per cent. Against last week carried forward, nine per cent, interval 0.84 to 0.98, which met our pre-set bar. And here are the losses: Oman twice, a tie in Qatar." |
| 1:55–2:20 | **US proof** page (red NOT MET badge, league table) | "In the US we held ourselves to the CDC's FluSight ensemble with a frozen test. We missed our bar. Among individual CDC-hub models we placed seventh of twenty-one in 2024/25, and fell to the baseline in 2025/26. We show you the season we lost." |
| 2:20–2:35 | **About** page: real / simulated / not built | "On the UAE's own short record, forward in time, we tie with last week, and our multi-signal version didn't help. UAE sentinel data only start in 2022; with two seasons of history, flu won both later folds. That's our reading, after the fact, so the ledger tests it forward." |
| 2:35–3:00 | **Ledger receipt** → pilot slide | "Every forecast round is hashed before WHO publishes the answer: today one round, nothing scored yet ⟦IF DONE: and it's public at ⟨URL⟩, anchored ⟨date⟩⟧. Give us one hospital's aggregate counts for twelve weeks in shadow mode. If we don't beat your own census, you walk away." |

[+] **Extended beats (7-minute format):**
- **Alerts page (30 s):** "At the primary threshold, onset lead is zero weeks for every rule, the CDC's too, and every rule had zero false alarms. NABD's alerts were less often late, but a simple census rule caught more onsets in time in 2024/25. Diagnostic only."
- **Feed removal (20 s):** removing the non-sentinel or calendar inputs didn't make forecasts worse. We say so, and v2 stays a challenger.
- **Leakage test (30 s):** run `pytest tests/test_vintage.py` live, plus the deliberate-leak test that must fail.
- **Lock guard (20 s):** edit one line of `uae/gcc.py`, rerun `python3 -m uae.gcc --score`, and show it refuse (`GoalpostError`). Revert afterwards.
- **Workforce module (20 s):** secure aggregation across ≥10 employers on synthetic data, with the SIMULATED watermark visible. No individual or employment use.
- **Weekly bulletin (15 s):** the bilingual PDF for the round, showing the approval status and audit hash.

**Do not demo or say:**
- "blind"; "fewer false alarms"; "published" for the ledger before it is;
- the UAE "3/3 onsets"; RSV Gulf as a headline; Chronos-2; any E1 number;
- the UAE LOSO 0.76/0.78; v2 as better; "early warning";
- an ED, weather or wastewater feed (there is none).

**Fallbacks:**
- If a live fetch fails, use the cached build, with the badge showing "cached ⟨date⟩".
- If the app crashes, play the recorded video.
