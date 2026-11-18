# NABD: the story (v4, 18 Nov 2026). Current narrative order for the deck, video and web front-end

Every number is in `research/claims-ledger.md` (sections A–H). The stop list and BANNED list still bind. This file supersedes the *order* in `deck-script.md` and `video-script.md`; their slide contents stay valid. v4 changes from v3: the opening sentence matches the web headline (no "borrows the world's"), and a UAE beat (claims ledger H6, development check) is added before the foundation-model line.

## The one sentence
**NABD gives the people who plan the UAE's respiratory season one checkable forecast a week: a model that learns season shapes from many countries' WHO records, tested under lock on 18 countries, ahead of "repeat last week" on the UAE's own recent seasons (a development check), and now running forward on a hashed ledger.**

## The four numbers to say out loud
**2,189** (RSV admissions of children ≤5 at one Abu Dhabi hospital, 2018–22) · **23%** (less influenza forecast error than a country's own-record model, held-out countries) · **18 of 18** · **0.77** (pooled model vs repeating last week on the UAE's own 2024/25 and 2025/26 seasons; always said with "development check").

## The arc (eight beats)
1. **The Monday decision.** Every winter week a bed manager, a duty officer and an immunisation lead plan the next three weeks from last week's numbers and last year's pattern. UAE seasons change timing and shape from year to year (flu peaked in October one year and February the year before).
2. **The measured obstacle.** The UAE has four seasons of sentinel data. A model fitted to that record only ties "repeat last week" (1.002). NABD shows that result; it is why the rest exists.
3. **The idea: learn from more seasons than one country has.** One model learns how respiratory seasons rise, peak and fade across 46 countries' WHO FluNet histories. A country brings only what it has; the model supplies the rest.
4. **The proof.** Plan locked before download, model locked before extraction, scored once, on 18 countries the author had never looked at: 23% less forecast error than the own-record model, better in every country, 38% where the record was short. It also beat "repeat last week" in all 18 (12% less).
5. **Back to the UAE (development check).** Forecasting the UAE's last two seasons forward in time, with the UAE left out of the model's training: relative error 0.77 against repeating last week, better in both seasons. Not confirmatory, because UAE data helped choose the model; that is why the confirmatory test runs live (beat 8).
6. **The cross-check.** A general foundation model (Chronos-2, zero-shot) lands level with NABD's pooled model on the held-out countries and shows the same gain over the own-record model. (Post hoc.)
7. **What it does and does not change.** Replayed through a fixed roster rule: fewer mis-rostered weeks than the own-record model (10.5 vs 12.3 a season) and far fewer than planning from past seasons (16.6); no clear gain over "repeat last week" at that horizon. In the US the bar was the CDC's combined forecast, and NABD missed it (7th of 21 single models one season).
8. **Live, and bound in advance.** The pooled model now forecasts the UAE on a hashed ledger, with a prospective test locked before its first data point. Each week one proposed action, approved by a named person, logged. The ask: one hospital, twelve weeks, aggregate counts, shadow mode.

## 3-minute voiceover (v4)

| # | Time | Screen | Voiceover |
|---|---|---|---|
| 1 | 0:00–0:15 | Web front-end hero: the pulse line, this week's RSV and flu tiles | "Every winter, RSV and influenza reach Abu Dhabi's children's wards together. One hospital, Tawam, admitted two thousand one hundred and eighty-nine young children with RSV in five years. And every Monday, someone decides how much to prepare." |
| 2 | 0:15–0:33 | Season-shape view, flu toggle | "They plan from last week and last year. But UAE seasons change shape: flu peaked in October one year, in February the year before. And a model built only on the UAE's four seasons just ties repeating last week." |
| 3 | 0:33–0:48 | How it works; "learning across countries" | "So NABD learns from more seasons than one country has. One model learns how respiratory seasons rise, peak and fade across forty-six countries' WHO data." |
| 4 | 0:48–1:12 | Forest plot: 18 countries, all left of the line | "The plan was locked, then the model. Only then were eighteen unseen countries opened. Twenty-three per cent less forecast error than each country's own-record model. Better in eighteen of eighteen." |
| 5 | 1:12–1:32 | Results card: "The UAE's own seasons, pooled model (development check)" | "Back to the UAE. Forecasting its last two seasons forward in time, with the UAE left out of training, the pooled model beat repeating last week in both. That is a development check, not proof, so the real test runs live." |
| 6 | 1:32–1:42 | Benchmark card: pooled model and Chronos-2 | "An off-the-shelf foundation model lands level with ours on the same test. Learning across countries works, whichever model does it." |
| 7 | 1:42–2:05 | Weekly card: chances, proposed action, Approve, audit line; Arabic toggle | "Each week NABD turns that into one card, in Arabic and English: the chance of crossing each pressure threshold, and one proposed action. A named person approves it, and the decision is logged. Nothing is sent without a human." |
| 8 | 2:05–2:22 | Honest panel: roster replay; US NOT MET badge | "NABD shows what it does not do. In a roster replay it beats the own-record model, but not simply repeating last week. Against the CDC's combined forecast in the US, it missed its own bar." |
| 9 | 2:22–2:42 | Ledger: round R2, Verify all in the browser; "prospective test locked" | "So the UAE test runs forward. Every forecast is fingerprinted before WHO publishes the week it covers, and the test that will judge it is already locked." |
| 10 | 2:42–3:00 | Pilot card; end card *To sense is to predict.* | "Give NABD one hospital's aggregate counts for twelve weeks, in shadow mode. If it does not beat the hospital's own census, the hospital walks away. To sense is to predict. NABD." |

Never in the video: everything on the `video-script.md` "never" list, except that Chronos-2 may now be named **only** as the post hoc benchmark of beat 6 ("level with", never "beaten"), and never as an input to NABD. Beat 5 never says "proven in the UAE", "UAE result" or "validated"; it always says "development check".
