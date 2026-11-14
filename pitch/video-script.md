# NABD: 3-minute submission video (shot list + voiceover), round 4 (impact first, BUILD-SPEC v1.7)

> **Superseded on 14 Nov 2026 by the v3 voiceover in `pitch/story.md`.** Kept for the shot list and the "never" list, which still bind.

**Rules:**
- Every spoken number traces to `research/claims-ledger.md`. The stop list (`research/positioning.md` §4.6) and the v1.7 BANNED list are binding.
- Shots marked ⟦IF BUILT⟧ / ⟦IF DONE⟧ are cut, along with their voiceover line, if the feature isn't real on 19 Nov.
- Record the app at 1920×1080 with the English UI, plus one Arabic toggle shot. Hide Streamlit's "Deploy" chrome.
- Voiceover runs about 145 words a minute. The target is ≤ 420 words (about 2:50).
- **Order:** pain → who decides → NABD → Gulf test → CDC benchmark → UAE caveat → ask with the ledger.
- **Numbers spoken:** 2,189 · 46% · seventh of twenty-one (plus "nine per cent", once).

| # | Time | Shot (screen) | Voiceover |
|---|---|---|---|
| 1 | 0:00–0:12 | Black → the pulse line draws and opens into a forecast fan. Title: **NABD نبض**. | "Every winter, RSV and influenza reach Abu Dhabi's children's wards together, and every week someone has to decide how much to prepare for." |
| 2 | 0:12–0:35 | **App: Season shape page:** UAE seasons overlaid (WHO FluNet), then the influenza toggle. Callouts: "Flu peak: week 42 (Oct 2025) · week 7 (Feb 2025)" and "RSV peak: week 41–47". | "But the timing and shape change from year to year, and you can't know in advance which shape you'll get. In WHO's UAE lab data, flu spiked above forty per cent in October 2025. The season before, it plateaued for five months and peaked in February. One Abu Dhabi hospital, Tawam, recorded two thousand one hundred and eighty-nine RSV admissions of young children in five years." |
| 3 | 0:35–0:50 | Three role cards: **bed manager**, **ADPHC duty officer**, **immunisation programme**. Then the layer diagram: Tableegh · UMOC · Rasid = *detect* → **forecast** → *operate*. | "A bed manager, a public-health duty officer, an immunisation lead: each plans the next three weeks from last week's numbers and last year's pattern. Abu Dhabi detects outbreaks well. To our knowledge, no one gives these desks a checkable forecast of how big the next three weeks will be." |
| 4 | 0:50–1:20 | **App: Weekly card.** The lag badge, the fan with the dashed persistence line, then the exceedance table (RSV P > 10% / > 20%; flu P > 15% / > 30%) and the direction. Toggle to Arabic for 2 s. | "NABD does. Each week it turns WHO surveillance into probabilistic RSV and flu forecasts, in Arabic and English, up to three weeks after issue, each forecast labelled by the week it covers. The card gives the chance of crossing each pressure threshold, and which way it's heading. The dashed line is last week carried forward. We always show it." |
| 5 | 1:20–1:35 | **Why-this-forecast panel**, then the playbook action → type a name → **Approve** with a reason → the hash-chained audit line appears. | "You see exactly which signals moved the forecast. NABD proposes an action. A named person decides, and every decision goes into a tamper-evident log." |
| 6 | 1:35–1:45 | **Hospital winter planner (SCENARIO)**: bed-days, % of ward, nurse shifts at risk and cost in AED; staff absence follows flu and RSV. | "For the hospital, it translates the wave into its own constraints, beds and staff, as a labelled scenario using the hospital's own numbers." |
| 7 | 1:45–2:10 | **GCC test page:** two bars (vs past seasons, vs last week), then the country × season grid with losses highlighted. | "Then we tested it out of sample. We froze the method, locked the plan, and only then downloaded Oman, Qatar and Saudi data. Against planning from past seasons, it cut influenza forecast error by forty-six per cent. Against last week carried forward, nine per cent, which met our pre-set bar. Every loss is on the page." |
| 8 | 2:10–2:30 | **US proof page:** the red **NOT MET** badge, then the league chart. | "In the US we set our bar at the CDC's FluSight ensemble, froze the test, and missed it. Among individual CDC-hub models we ranked seventh of twenty-one in one season, and fell to the baseline the next. We show the season we lost." |
| 9 | 2:30–2:42 | **About page:** the real / simulated / not-built table. | "On the UAE's own short record we tie with last week, and our multi-signal version didn't help. That's why every forecast now goes into a hashed ledger, scored week by week." |
| 10 | 2:42–3:00 | **Ledger page** ⟦IF DONE: with the public URL and anchor receipt⟧ → pilot card: **12 weeks · one hospital · aggregate counts · shadow mode**. End card: *To sense is to predict.* | "Give us one hospital's aggregate counts for twelve weeks, in shadow mode. If we don't beat your own census, you walk away, and the record stays on file either way. To sense is to predict. NABD is how Abu Dhabi checks the prediction." |

**Word count:** the voiceover above is 401 words (whitespace tokens, counted by script on 8 Nov), about 2:46 at 145 words a minute. If the take runs over 3:00, trim shot 6 first, then shot 9.

**Never in the video:**
- "blind"; "published" or "public" for the ledger before it is; "early warning" or "earlier than"; "fewer false alarms";
- "calibrated" without qualification; "nobody publishes" without "to our knowledge";
- "RSV is climbing"; crisis language; "fills Abu Dhabi's beds";
- E1 numbers; the UAE "7 of 8" or "3/3 onsets"; RSV Gulf as a headline; v2 as an improvement;
- Chronos-2; weather, ED or wastewater as inputs; SEHA operational numbers; any absence statistic.

**Recording checklist:**
1. `streamlit run app/streamlit_app.py` with the newest ledger round issued.
2. Use a demo approver name, and clear the audit log afterwards.
3. Show the lag badge with today's real value.
4. Put the take date in the video description, and ⟦IF DONE⟧ the public repo URL.
