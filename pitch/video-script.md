# NABD: 3-minute submission video (shot list + voiceover), round 3

**Rules:**
- Every spoken number traces to `research/claims-ledger.md`. The stop list in `research/positioning.md` §4.6 is binding.
- Shots marked ⟦IF BUILT⟧ are cut (and the voiceover line with them) if the feature isn't in the app on 19 Nov.
- Record the app at 1920×1080, English UI, with an Arabic toggle shot.
- Voiceover runs about 145 words a minute; it is 336 words in total (counted), about 2:20, which leaves room for on-screen pauses.
- **Evidence order (v1.6):** Gulf test → ledger → US benchmark → UAE parity.

| # | Time | Shot (screen) | Voiceover |
|---|---|---|---|
| 1 | 0:00–0:12 | Black → the pulse line draws, then opens into a forecast fan. Title: **NABD نبض**. | "Every winter, two viruses, RSV and influenza, arrive in Abu Dhabi's children's wards together." |
| 2 | 0:12–0:35 | Season-shape chart: 4 UAE seasons overlaid from WHO FluNet. Callouts: "Flu peak: wk 45, wk 45, **February**, **October**" and "RSV peak: wk 41–47". ⟦IF BUILT: app season-shape panel⟧ | "No two seasons share a shape. In WHO's UAE lab data, flu spiked above forty per cent in October 2025. The year before, it plateaued for five months and peaked in February. At one Abu Dhabi hospital, Tawam, RSV put 2,189 young children in hospital in five years." |
| 3 | 0:35–0:50 | Layer diagram: Tableegh · UMOC · Rasid = *detect*, then an empty **forecast** box, then *operate*. | "Abu Dhabi already detects. But nobody publicly answers the question a ward lead asks every Monday: how big will the next three weeks be, and how sure are you?" |
| 4 | 0:50–1:20 | **App: Weekly card.** The lag badge, the fan chart with the dashed persistence line, the horizons *nowcast → +2.5 wk*. ⟦IF BUILT: exceedance probabilities⟧. Toggle to Arabic for 2 s. | "NABD answers that. Each week it turns WHO surveillance into calibrated RSV and flu forecasts, in Arabic and English. The dashed line is what you'd get by carrying last week forward. We always show it, so nobody trusts us blindly." |
| 5 | 1:20–1:35 | **Why-this-forecast panel**, then the playbook action → type a name → **Approve** with a reason → the hash-chained audit line appears. | "You can see exactly which signals moved the forecast. The system proposes an action; a named person decides, and every decision is chained into a tamper-evident log." |
| 6 | 1:35–2:00 | **GCC test page:** the result chart and country × season grid; the losses highlighted. | "Then we tested it blind. We froze the method, locked the test plan, and only then opened Oman, Qatar and Saudi data nobody on the team had seen. It cut error against 'next week equals this week' by about nine per cent for flu and twenty for RSV. Every loss is on the page." |
| 7 | 2:00–2:12 | **Ledger page:** rounds R0 and R1 with hashes. ⟦IF DONE: anchor receipt⟧ | "Every forecast is hashed and published before WHO releases the answer, so our track record can't be rewritten." |
| 8 | 2:12–2:35 | **US proof page:** the red **NOT MET** badge, then the league chart. | "In the US we held ourselves to the CDC's FluSight ensemble with a test frozen in advance, and missed our bar: 1.22 against 1.15. Among individual CDC-hub models we ranked seventh of twenty-one in 2024/25, and fell to the baseline in 2025/26. We show the season we lost." |
| 9 | 2:35–2:45 | **About page:** the real / simulated / not-built table. | "On the UAE's own short record we tie with persistence, and our multi-signal version didn't help. That's why the ledger runs every week." |
| 10 | 2:45–3:00 | Pilot timeline: **12 weeks · one hospital · aggregate counts · shadow mode**. End card: *To sense is to predict.* | "Give us one hospital's aggregate counts for twelve weeks, in shadow mode. If we don't beat your own census, you walk away. To sense is to predict. NABD is how Abu Dhabi checks the prediction." |

**Word count check:** the voiceover is 336 words (counted by script). Trim shot 3 or 9 first if the take runs over 3:00.

**Never in the video:**
- "early warning" or "earlier than";
- "RSV is climbing";
- crisis language;
- E1 numbers;
- the UAE "7 of 8" claim;
- v2 as an improvement;
- Chronos-2;
- weather, ED or wastewater as inputs;
- SEHA operational numbers.

**Recording checklist:**
1. `streamlit run app/streamlit_app.py` with the newest ledger round issued.
2. Clear the audit log or use a demo approver name.
3. Show the lag badge with today's real value.
4. Freeze the take date in the video description.
