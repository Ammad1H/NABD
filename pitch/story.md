# NABD: the story (v3, 14 Nov 2026). Current narrative order for the deck, video and web front-end

Every number is in `research/claims-ledger.md` (sections A–H). The stop list and BANNED list still bind. This file supersedes the *order* in `deck-script.md` and `video-script.md`; their slide contents stay valid.

## The one sentence
**The UAE's record is too short to forecast from alone, so NABD borrows the world's: one model trained across countries' WHO seasons, tested under lock on 18 countries we had never opened, and now running on a hashed ledger for the UAE.**

## The three numbers to say out loud
**2,189** (RSV admissions of children ≤5 at one Abu Dhabi hospital, 2018–22) · **23%** (less influenza forecast error than a country's own-record model, 18 of 18 held-out countries; 38% where the record is short) · **18 of 18**.

## The arc (seven beats)
1. **The Monday decision.** Every winter week a bed manager, a duty officer and an immunisation lead plan the next three weeks from last week's numbers and last year's pattern. UAE seasons change timing and shape from year to year (flu peaked in October one year and February the year before).
2. **The obstacle we measured.** The UAE has four seasons of sentinel data. A model fitted to that record only ties "repeat last week" (1.002). We show that result; it is why the rest exists.
3. **The idea: borrowed strength.** One model learns how respiratory seasons rise, peak and fade across 46 countries' WHO FluNet histories. A country brings only what it has; the model supplies the rest.
4. **The proof.** Plan locked before download, model locked before extraction, scored once, on 18 countries the author had never looked at: 23% less forecast error than the own-record model, better in every country, 38% where the record was short. It also beat "repeat last week" in all 18 (12% less).
5. **The cross-check.** A general foundation model (Chronos-2, zero-shot) lands level with ours and shows the same gain over the own-record model. Two unrelated ways of borrowing, one answer. (Post hoc.)
6. **What it does and does not change.** Replayed through a fixed roster rule: fewer mis-rostered weeks than the own-record model (10.5 vs 12.3 a season) and far fewer than planning from past seasons (16.6); no clear gain over "repeat last week" at that horizon, and slightly more missed surge weeks. We say both. In the US we set our bar at the CDC's combined forecast and missed it (7th of 21 single models one season).
7. **Live, and bound in advance.** The pooled model now forecasts the UAE on a hashed ledger, with a prospective test locked before its first data point. Each week one proposed action, approved by a named person, logged. The ask: one hospital, twelve weeks, aggregate counts, shadow mode.

## 3-minute voiceover (v3)

| # | Time | Screen | Voiceover |
|---|---|---|---|
| 1 | 0:00–0:15 | Web front-end hero: the pulse line, this week's RSV and flu fans | "Every winter, RSV and influenza reach Abu Dhabi's children's wards together. One hospital, Tawam, admitted two thousand one hundred and eighty-nine young children with RSV in five years. And every Monday, someone decides how much to prepare." |
| 2 | 0:15–0:35 | Season-shape view, flu toggle | "They plan from last week and last year. But UAE seasons change shape: flu peaked in October one year, in February the year before. And the UAE has only four seasons of sentinel data. We tested forecasting from that record alone. It only ties repeating last week." |
| 3 | 0:35–0:55 | "Borrowed strength" explainer: 46 countries flowing into one model | "So NABD borrows. One model learns how respiratory seasons rise, peak and fade across forty-six countries' WHO data. A country brings only what it has." |
| 4 | 0:55–1:25 | Forest plot: 18 countries, all left of the line | "We locked the plan, locked the model, then opened eighteen countries we had never looked at. Twenty-three per cent less forecast error than each country's own-record model. Better in eighteen of eighteen. Thirty-eight per cent where the record was short, which is the UAE's position." |
| 5 | 1:25–1:40 | Benchmark strip: pooled model and Chronos-2 side by side | "A general foundation model, used off the shelf, lands level with ours and shows the same gain. Two unrelated ways of borrowing, one answer." |
| 6 | 1:40–2:05 | Weekly card: fan, exceedance chances, proposed action, Approve, audit line; Arabic toggle | "Each week NABD turns that into one card, in Arabic and English: the chance of crossing each pressure threshold, and one proposed action. A named person approves it, and the decision is logged. Nothing is sent without a human." |
| 7 | 2:05–2:25 | Honest panel: roster replay bars; US NOT MET badge | "We show what it does not do. Replayed through a roster rule it beats the own-record model, but not simply repeating last week. Against the CDC's combined forecast in the US, we missed our own bar." |
| 8 | 2:25–2:45 | Ledger: round R2, hash verified in the browser; "prospective test locked" | "So the UAE test runs forward. Every forecast is hashed before WHO publishes the week it covers, and the test that will judge it is already locked." |
| 9 | 2:45–3:00 | Pilot card; end card *To sense is to predict.* | "Give us one hospital's aggregate counts for twelve weeks, in shadow mode. If we don't beat your own census, you walk away. To sense is to predict. NABD." |

Never in the video: everything on the `video-script.md` "never" list, except that Chronos-2 may now be named **only** as the post hoc benchmark of beat 5 ("level with", never "beaten"), and never as an input to NABD.
