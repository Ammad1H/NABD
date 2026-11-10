# REVIEW R4: final judge panel and integrity audit (9 Nov 2026)

**Panel.** J1 is a senior public-health official (DoH/ADPHC). J2 is a principal AI scientist (Microsoft/G42/MBZUAI). J3 is a partnerships lead (PureHealth/M42). A is an independent integrity auditor. None of us built NABD. R3 scored it about 5.9 (docs/REVIEW-R3-judges.md, docs/REVIEW-R3-audit.md).

**Inspected.**
- pitch/: registration, deck (`pitch/deck/project/slides/*.html`, 12 slides, plus deck.json), deck-script, video-script, demo-script, one-pager, qa, outreach
- docs/: TECHNICAL, STATUS, PUBLISH, PILOT-DATA-SPEC, DEVIATIONS (C1–C7), BUILD-SPEC v1.7
- research/: positioning.md, claims-ledger.md
- results/: SUMMARY.md, gcc/SUMMARY.md, uae/SUMMARY-v2.md, `uae/v2/tables/forward_wis_by_season.csv`, `gcc/tables/coverage.csv`, fig2
- all 14 app screenshots, including 04b and 12_bulletin_p1/p2
- bulletin/out/ PDF; app/planner.py; .streamlit/config.toml; playbook.yaml; the FluSight draft yml; ledger/rounds

**Runs.** All runs were in a scratch clone (`/tmp/r4`, with the hub and cache symlinked), so nothing in the repo changed except this file.
- `python3 -m pytest -q`: **144 passed** (86 s).
- `python -m eval.run_all --cached`: exit 0 in 92 s. Every tracked output is **byte-identical** except `results/summary.json`, where only the key order changed. The generated SUMMARY Round-2 section now survives (R3 #14 fixed). The hub pin is enforced (R3 #5 fixed).

---

## 0. What changed since R3

**Fixed (credit given).**
- The pitch is impact-first: pain → deciders → gap → NABD → evidence → ask.
- The headline comparator now matches the pain: 46% vs past-season patterns (secondary), 9% vs persistence (primary).
- Every R3 banned phrase has been removed from the registration, deck, video and one-pager.
- The "fewer false alarms" claim was replaced by the late-alert breakdown.
- The RSV Gulf result is demoted to secondary.
- The UAE parity result now has its post-hoc training-history explanation.
- The ledger is described as "one round, re-issued; 0 scored" in the deck and one-pager.
- The league denominators are bracketed on slide 8.
- Hub-pin enforcement, the G1b time correction, the GCC exposure disclosures, the generated SUMMARY section, the keyed league cache and the GCC leak test have all landed (DEVIATIONS C1–C6).
- **New and good:** the bilingual bulletin PDF (with a "What this bulletin is not" box and PROPOSED, NOT APPROVED status), the hospital winter planner (AED, occupational-health role, SCENARIO/SIMULATED labels throughout), and the publish package (PUBLISH.md, anchor_all, flusight_wednesday and its validator).

**Not done: the real-world items.**
- No public repo (`git remote -v` is empty).
- No anchors (`anchors/` doesn't exist).
- No deployment.
- No full GCC re-pull.
- No FluSight PR; the yml still has PLACEHOLDERs.
- Playbook `reviewed: false`.
- No letter of interest.
- No ledger round since R1 (only `ledger/rounds/2026-11-08T1212Z_R1`), so 0 weeks are scored.
- The team name and contact are blank in the registration, which is **due tomorrow (10 Nov)**.

**New problems found in R4.** Details in §2 and §3.
1. **Horizon convention split.**
   - The app, bulletin, TECHNICAL:102, registration and deck slide 6 now say "+1/+2/+3 wk after issue" (commit 640003a).
   - The one-pager, video, demo, Q&A, outreach, assumptions and claims ledger still say "+2.5 wk" or "+0.5/+1.5/+2.5".
   - The demo narration would contradict the screen.
2. **Banned or retired claims are still visible in the app, which is the thing judges open.**
   - The About page says "RSV and influenza fill Abu Dhabi's children's beds" (F5), and the video's shot 9 films that page.
   - The Alerts page shows the retired LOSO UAE table, "NABD-UAE-v1 flu 3/3 … median lead 1.43" (F18), with no LOSO label.
3. **A hidden weakness that J2 can find from a file the deck cites.**
   - On the UAE's own forward-in-time record, v1 vs the **seasonal analog** (the "last year's pattern" the pitch sells against) is about parity for flu. The unweighted mean of the season means is 3.08 vs 3.08 (our computation from `forward_wis_by_season.csv`), and v1 lost 2023/24 to the analog (4.75 vs 1.85).
   - With ≥2 training seasons, though, v1 beat the analog in **all 4** UAE folds:
     - flu 2.54 vs 4.50 and 1.94 vs 2.88;
     - RSV 1.31 vs 1.47 and 2.30 vs 3.87.
   - This supports the story if the team reports it first (post hoc). It hurts if a judge computes it.
4. **The pain claim contradicts the team's own bulletin.**
   - "No two seasons share a shape", yet this season's flu peak (40.1%, wk 40) almost repeats last season's (40.6%, wk 42), and the bulletin's season-shape panel shows it.
   - The RSV peak fell in wk 41–43 in 4 of 5 seasons. The "six-week" spread comes from one season (2025/26, wk 47).
   - A DoH judge will say "seasons do repeat". The defensible claim is that **you cannot know in advance which shape you will get**: 2024/25 plateau vs 2025/26 spike, RSV peak height 15.6–29.8%.
5. **The planner scales nurse sickness absence by the RSV forecast** (`app/planner.py:13`, `_wide(fc_rsv)`). Adult staff respiratory absence is driven mainly by influenza, not paediatric RSV, and J1 will spot this. The planner's output (net roster gap 0–0–2 shifts; P(gap > 0) 11–19%) also tells the "workforce" story as "no problem".
6. **The pilot exit criterion is a bar NABD has never cleared on flu.**
   - The criterion is relative WIS < 0.9 vs census persistence (slide 12, PILOT-DATA-SPEC §6).
   - Flu results so far: GCC flu 0.914, UAE 1.002, US vs baseline 0.816 with a CI that crosses 1.
   - It is honest, but J3 will read it as "designed to walk away".

---

## 1. Scores (1–10) and verdict

The six criteria are the same as R3. Half points are allowed.

| Criterion | J1 DoH/ADPHC | J2 AI scientist | J3 partnerships | Mean | R3 mean |
|---|---|---|---|---|---|
| Impact | 7 | 6 | 6 | **6.3** | 5.3 |
| Technical depth / novelty | 6 | 5.5 | 5 | **5.5** | 5.3 |
| Working demo & evidence | 7 | 7 | 6.5 | **6.8** | 6.7 |
| Responsible AI | 8 | 8 | 7.5 | **7.8** | 7.7 |
| Scalability / deployment | 7 | 7 | 6 | **6.7** | 6.7 |
| Commercial / pilot | 5 | 4 | 3.5 | **4.2** | 4.0 |
| **Per judge** | **6.7** | **6.25** | **5.75** | **≈ 6.2** | ≈ 5.9 |

**J1 (DoH/ADPHC).**
- **Gains:** "A Monday decision, made with last year's pattern" and the deciders table are what I'd write myself. The bulletin is the first artefact I could imagine landing in a duty officer's inbox; its "what this is not" box is exactly right.
- **Losses:**
  - Your own bulletin shows this flu season repeating last season's shape.
  - The planner ties nurse absence to RSV.
  - The Arabic card still carries English explanations, the evidence box, the trend line and the captions (screenshot 02).
  - The About page uses wording you yourselves banned.
- Still no Abu Dhabi colleague has reviewed the playbook. **Finalist.**

**J2 (AI scientist).**
- **Gains:** the comparator now matches the problem and the integrity bookkeeping is better: C1–C7, a reproducible run_all, 144 tests.
- **Unchanged:**
  - The model is a 5-term regression.
  - "Pre-registered" is still the team's own git.
  - The ledger is still one unscored round.
  - The UAE vs-analog parity sits in a file the deck cites, unreported.
- I'd move evidence to 8 if the repo, the anchors, ≥2 scored ledger weeks and the FluSight PR exist on judging day. **Finalist.**

**J3 (PureHealth/M42).**
- **Gains:** AED, an occupational-health role and a business hypothesis are on the ask slide.
- **Still missing:** a counterparty, a price figure, and a planner output that shows a problem worth paying for. "Gap 0–2 shifts" is not a purchase reason.
- One signed line from a Tawam/SKMC paediatrician remains the biggest lever. **Borderline finalist.**

**Verdict: a likely finalist (top ~3–5% of about 400), but not yet a likely top-3. Panel estimate: about 15–20% for top-3 as it stands.**
- **Why finalist:**
  - It has a working, reproducible prototype on real data.
  - It passed a locked out-of-sample Gulf test against the comparator that matches the pain.
  - Its disclosure discipline and responsible-AI design are unusual.
  - The bulletin is tangible.
- **Why not top-3:**
  - Nothing is externally verifiable yet, and the whole story rests on verifiability.
  - No Abu Dhabi clinician or partner is attached.
  - The app judges will open still shows two banned claims and a half-English Arabic card.
  - The workforce half is weakly modelled.
- **With R4 items 1–5 done** (§4), the panel estimate is **6.9–7.3**, about 35% for top-3. The partner letter is worth about half of that gain.

---

## 2. Integrity audit

### 2.1 CRITICAL

| # | Finding | Where | Fix |
|---|---|---|---|
| C1 | **The registration is due tomorrow with open placeholders, and it under-reports maturity.** (a) The team and MBZUAI-permission line is unfilled (`pitch/registration.md:82`). (b) The bulletin, the winter planner and the pilot connector are built (connector a0e2766; bulletin and planner 661b472/2199490), but :41–45 lists them "In build for 20 Nov" and the maturity list (:54–64) omits them. (c) The title and :14/:20/:25/:37 say "open hub" with no public repo. | registration.md:11, :14, :20, :25, :41–45, :54–64, :82 | Fill the team and contact. Move the bulletin, planner and connector into "Built and scored"; keep only "publishing and externally timestamping the ledger" in build. Either push the repo before submitting (PUBLISH §1–3) or change "open" to "open-source-licensed". Re-run wordcount.py. |
| C2 | **Nothing a judge can click or verify exists.** There is no public repo, no anchors, no hosted app, and the Docker image has never been built. Prototypes are "judged directly"; if judges can't open it, it isn't judged as working. Every "locked before download" is still self-attested. | `git remote -v` empty; no `anchors/`; STATUS.md "What only you can do" 1–4 | PUBLISH.md §1–5 by 11 Nov, **after** the §2.2 sweep (pushing first would publish M1–M5). |

### 2.2 MAJOR (fix before the repo goes public; most take minutes)

| # | Finding | Where | Fix |
|---|---|---|---|
| M1 | **F5 banned phrase in the app**, and it is filmed in video shot 9 | app/streamlit_app.py:892 "RSV and influenza fill Abu Dhabi's children's beds"; video-script.md:21 films the About page | "…drive paediatric admissions in Abu Dhabi (e.g. 2,189 RSV admissions of children ≤5 at Tawam, 2018–22)" |
| M2 | **F18 / D4 retired claim shown in the app.** The Alerts page renders `results/uae/tables/alerts_uae.csv` (v1 flu 3/3, PPV 3/3, lead 1.43). It is computed on LOSO scores (`uae/backtest_v2.py:336`, `alert_eval(raw, s, sc, …)`, where `sc` = LOSO), and its only label is "n = 4 seasons, descriptive" | app/streamlit_app.py:439–444; screenshot 08 | Label it "LOSO design (models trained on later seasons); retired as evidence", or compute the forward-in-time table (`fsc`) under a DEVIATIONS entry declared first. Deck slide 11 ("false alarms (US and UAE)", req.html:13) must then say "US; UAE descriptive (LOSO)". |
| M3 | **Banned wording in a results file the deck cites as its source** (slide 7 footer → results/gcc/SUMMARY.md) | results/gcc/SUMMARY.md:3 ("verified against the official API", F14), :80 ("run blind", F12; "20% for RSV" in the headline sentence, F17), :81 ("first blind, pre-registered test") | Hand-edit to the A11 and F12 wording: "WHO full export via a public mirror; 419/419 UAE rows identical, 23/23 Gulf rows spot-checked; full re-pull pending" and "out-of-sample, plan locked before download (self-attested)". Add `results/` and the word `blind` to the CLAIMS scan in scripts/prepare_public_repo.sh:52–53. |
| M4 | **Horizon convention contradicts itself across artefacts.** The app, bulletin, TECHNICAL:102, registration and deck slide 6 say "+1/+2/+3 wk after issue", or "three weeks". The others say "+2.5". | one-pager.md:19; video-script.md:16 ("two and a half weeks past issue"); demo-script.md:13 (narrates "+0.5/+1.5/+2.5" over a screen showing +1/+2/+3); qa.md:45, :183–185; outreach.md:21; assumptions-limitations.md:7; deck-script.md:59; claims-ledger.md:46 (B5), :88 (D11); DEVIATIONS C7 ("from R2 on use issue-relative labels") | One sentence everywhere: "nowcast to +3 weeks after issue (forecasts labelled by target week; skill measured at a conservative 11-day lag)". Append a DEVIATIONS row superseding C7. |
| M5 | **Q&A #3 quotes the wrong thresholds** for flu. The card and bulletin use P(>15%) = 94% and P(>30%) = 27%; qa.md says P(>10%) and P(>20%). It also says "+0.5 weeks" and "playbook v0.3" (the app is v0.4.0-illustrative). | qa.md:38–42; claims-ledger.md:88 | Correct to "flu P(>15%) 94%, P(>30%) 27% at +1 wk after issue; playbook v0.4.0 (illustrative)". |
| M6 | **Positioning text the repo will publish still overclaims.** STATUS.md itself flags this. | research/positioning.md:21 and :129/:155/:159/:220 ("calibrated"); :146 ("fill Abu Dhabi's children's beds", "Nobody publishes"); :220 ("published *before* the outcome exists") | Mark §6 as SUPERSEDED (pointing to pitch/), or reword it. |
| M7 | **Workforce arithmetic uses the wrong virus.** Staff absence = HR average × RSV positivity ÷ mean RSV positivity. | app/planner.py:13, :43–51 | Drive absence from the **influenza** forecast, or label the choice as an assumption with a toggle. Make the HR-entered rate the default and SIMULATED the opt-in. |

### 2.3 MINOR

- App sidebar says "Live forecast ledger: 5 hashed round file(s)" on every page (streamlit_app.py:94), while the deck says "one round, re-issued". Say "1 forecast round (W44 data), issued twice; 0 weeks scored". R3 #3 is still open in the app.
- About page:
  - "FluNet about 10–11 days" (:952), while 7 days was measured (bulletin "Lag at issue: 7 days");
  - "Card rules (playbook v0.3)" (:955), while the card shows v0.4.0.
- Streamlit "Deploy" chrome appears in all 14 screenshots. `.streamlit/config.toml` lacks `[client] toolbarMode = "minimal"` (R3 #6 open).
- The GCC page shows raw row keys (`PRIMARY_flu_v1_vs_persistence`, `rsv_NABD-UAE-v2-GCC_vs_NABD-UAE-v1`). Use human labels.
- Card "Why this forecast":
  - The chart has 4 bars but there are 3 bullets (testing volume is unexplained).
  - "Change over the last published week pushed the forecast up" while the week fell 15.6 → 10.5. The mean-reversion gloss R3 asked for is still missing.
- Arabic card: the explanation bullets, evidence sidebar, "Observed trend" line, chart caption, week selector, "Issued … model … source" line, context bullets and the "Page" label are English. On the bulletin's Arabic page, the chart axes and legend are English.
- Planner screenshot (04b) crops off the AED column, yet deck slide 10 claims "cost in AED".
- Test counts: STATUS.md says 142 and TECHNICAL.md:339 says 120; the actual count is 144.
- ⟦IF BUILT⟧ markers remain on built items: deck-script.md:67–68, :118, :126, :137; one-pager.md:22; video-script.md:18; demo-script.md:16, :28; qa.md:61. Claims ledger G1/G6 (:117, :122) are still status **P**, but they are built, so set them to R.
- registration.md:20/:30 gives "46% against past-season patterns" without "(pre-registered secondary)". The v1.7 guard asks for the label; it fits in the 300-word abstract.
- registration.md:14/:25 "tamper-evident record": a local hash chain is tamper-evident to third parties, but not against the team rewriting git. Add "(externally timestamped from ⟨date⟩)" once anchored.
- Deck slide 5 says "reads Tableegh-shaped aggregate counts". The connector reads NABD's own spec (PILOT-DATA-SPEC), and no Tableegh schema has been seen. Say "reads the aggregate weekly counts Tableegh already produces (spec in PILOT-DATA-SPEC)".
- Deck slide 9 says "Gulf countries had history from 2015". That holds for flu (all three) but not for RSV: SAU RSV starts in 2019 (flunet_gcc.csv). That is consistent with SAU RSV being the one loss, which is a point for the story.

### 2.4 Claim tracing: numbers on the deck, registration, one-pager and video

Every headline number traces correctly:

| Claim | Source |
|---|---|
| 0.536 (0.464–0.616) | gcc/SUMMARY |
| 0.914 (0.843–0.983) | gcc/SUMMARY |
| 9/12, losses OMN 22/23 and 24/25, QAT 23/24 tie | per-country-season table |
| 1.22 (1.01–1.52) | SUMMARY PRIMARY |
| 7/21, 13/41, 19/25, 40/46 | league_table and fig2 |
| 1.002/1.002 | uae/SUMMARY-v2:35, :38 |
| 4.75 vs 2.21; 2.54/2.66; 1.94/3.08 | forward_wis_by_season |
| 1.059 (1.016–1.111) | UAE v2 |
| 28 vs 17 of 51; 29 vs 24 of 52 | alerts_us × 51/52 |
| 40.6% wk 42 2025; 28.0% wk 7 2025 | flunet_are.csv, recomputed |
| RSV wk 41–47 | season table |
| 2,189; 5.8 d; 22%/<2%/US$2,241 | burden.md [S1][S3] |
| 11,660 forecasts, 53 locations | SUMMARY |
| LOO 0.904–0.929; clustered 0.841–0.984 | R3 audit reruns. Their scripts were **never committed** (/tmp/r3audit), so they are not reproducible from the repo; port `gcc_sens.py` into `eval/` before citing them publicly. |

No untraced number was found in the deck, registration, one-pager or video. The mismatches are §2.2 M4/M5 and §2.3.

### 2.5 Gate table

| Gate | R4 verdict | Evidence |
|---|---|---|
| G1 Protocol integrity | **PARTIAL** | All locks precede results. C1 (hub pin), C2 (G1b time) and C3 (exposure) are corrected by append-only rows. Still self-attested: no anchors, no public history. |
| G2 Reproducible pipeline | **PASS** | run_all --cached 92 s; every output byte-identical except summary.json key order; SUMMARY section generated; league cache keyed. |
| G3 Primary endpoint honest | **PASS** | NOT MET 1.22 (1.01–1.52), shown in red in the deck, app and one-pager. |
| G4 UAE track | **PASS** (caveat) | Forward-in-time parity reported. The ledger has R0/R1 only; R2 isn't issued, and 0 weeks are scored. UAE v1 vs analog forward-in-time is not reported (§0 item 3). |
| G5 Working app | **PASS locally / FAIL for judging** | 12 pages render (screenshots). Not deployed; Docker never built. |
| G6 Tests | **PASS** | 144/144, including the hub pin, GCC future perturbation with a positive control, SUMMARY generation and the FluSight validator. |
| G7 Evidence | **PASS** | Burden figures sourced; unchanged. |
| G8 Pitch | **PARTIAL** | Placeholders (team, contact, URL); stale ⟦IF BUILT⟧ markers; horizon split (M4); wrong thresholds in Q&A (M5). |
| G9 Honesty | **PARTIAL** | The pitch artefacts are clean. The app (M1, M2), results/gcc/SUMMARY.md (M3) and positioning.md (M6) still carry banned or retired claims. |
| G10 Alert metrics | **PARTIAL** | US metrics are complete and diagnostic. UAE metrics exist only on the retired LOSO design and are shown unlabelled. |
| G11 Explainability | **PASS** (minor) | Exact contributions shown. 4 bars with 3 bullets; no mean-reversion gloss. |
| G12 GCC holdout | **PASS** (caveat) | Primary MET; robust for flu. Data spot-checked only; the full re-pull is pending; SUMMARY wording overclaims (M3). |
| G13 Phase diagnostics | **PASS** | Unchanged; reproduced. |
| G14 Card consistency | **PASS** | cardcheck is tested. The bulletin carries the same bands, all marked PROPOSED, NOT APPROVED. |

---

## 3. The deck, slide by slide (`pitch/deck/project/slides/`)

**Overall.**
- The story order is right (v1.7), the three spoken numbers are present, every loss is on a slide, and the speaker notes are tight.
- **Main problems:**
  - (1) Two slides carry visuals that don't show the slide's headline number (2 and 7).
  - (2) Slides 7, 9 and 12 are too dense for spoken delivery: about 120–150 words each, plus 24-px small print.
  - (3) No slide shows the one Monday line big enough to read: P(RSV > 10%) next week = 51%, falling → "no surge roster".
  - (4) The screenshots are tall app pages shrunk to thumbnails (slides 6 and 10), so they are illegible.

| # | Slide | Clarity | Density | Story | Numbers |
|---|---|---|---|---|---|
| 1 | cover | Clear. "tested out of sample across the Gulf" is the right hook | Light | Good | ⟨team⟩ placeholder at :9 |
| 2 | pain | Strong headline | OK (≈70 words) | **Mismatch:** the bullets are about *flu* peaks (40.6% wk 42; wk 7 plateau) but the image is the **RSV** overlay (alt :16). On that RSV chart, 4 of 5 seasons peak in wk 41–43, which undercuts "seasons don't repeat". | The numbers are correct, but use the **flu** overlay with 2024/25 (plateau) and 2025/26 (spike) highlighted. Reword to "you can't know in advance which shape you'll get", because 2026/27 flu repeats 2025/26 (40.1% wk 40 vs 40.6% wk 42), and a DoH judge will have seen it. |
| 3 | burden | 2,189 lands | OK | Good | It mixes Abu Dhabi (Tawam) with Dubai claims; tag each "Abu Dhabi" or "Dubai" in the card title. The "no flu case counts" line is orphaned in the cost card; move it to slide 5. US$ here vs AED on slide 10: pick AED (US$ in brackets). |
| 4 | deciders | Clear table | **Heavy**: 4 columns × 3 rows at 26 px (about 110 words) | Good, but it doesn't say who the *primary* user is | "RSV stays of 4–6 days" traces to [S1][S3]. Bold the bed-manager row, and grey the immunisation row as "context". |
| 5 | gap | Clean diagram | Light | Good: complements, doesn't replace | "Tableegh-shaped" overclaims (§2.3). |
| 6 | nabd | The title is the best line in the deck | 5 bullets plus 2 **illegible** card screenshots (a 2,000-px page shrunk to 487 px) | This should be the "aha" slide, and it isn't | Replace the screenshots with one crop of the exceedance table and action box, and set "51% chance RSV > 10% next week · falling → no surge roster" at 60 px. "Nowcast to 3 weeks after issue" matches the app; the one-pager, video and demo must follow (M4). |
| 7 | gulf | Strong title | **Too dense**: 46% + 9% + wins/losses + a 60-word 24-px caveat line + chart | **The 46% has no visual.** The chart is v1 vs **persistence** by country (the 9%), and it puts SAU RSV in red on a flu slide. | Numbers match gcc/SUMMARY. Replace with a two-bar-per-country chart (vs past-season / vs last week, flu only). Cut the caveats to 3 short tokens: "retrospective · plan locked in our git before download · n = 3 countries", and leave the rest to Q&A. |
| 8 | cdc | Clear: NOT MET badge plus 7th of 21 | Two figures. fig1 at 600×240 is unreadable | Good honesty beat | 7/21 (13/41) and 19/25 (40/46) match fig2's titles, which still use the all-model ranks (R3 #4 half-fixed). Drop fig1. Say "at the baseline", not "level"; NABD is 1.007, just behind the baseline. |
| 9 | uae | Four cards, about 150 words | **Too dense** | **Confusing:** card 4 ("lead on size") is **US** alert data on a slide titled "The UAE's own record" | Numbers are correct. Move card 4 to backup or Q&A. Add the post-hoc fact that helps: with ≥2 training seasons, v1 beat the past-season analog in 4/4 UAE folds (forward_wis_by_season.csv), labelled post hoc. |
| 10 | workforce | Good headline | Bullets OK; the planner screenshot tables are unreadable | The visual tells J3 "gap 0–2 shifts", i.e. no problem | AED is claimed but cropped out of the image. The absence is RSV-driven (M7). Show one row: "+1 wk: 9–43% of paediatric resp. beds; nurse shifts at risk 3–12; P(roster gap) 19%", with the HR rate entered. |
| 11 | req | Good checklist plus a bulletin thumbnail (tangible) | OK | Good | "false alarms (US and UAE)" (:13) leans on the retired UAE LOSO table (M2). |
| 12 | ask | Clear structure | **Heavy**: three cards + a 90-day line + business, about 150 words | There is no counterparty, and the business line has no number | "< 0.9 vs your own census carried forward" is a bar NABD has never cleared for flu (§0 item 6). Either add the planner-relevant comparator ("and vs your own last-season pattern") or say on the slide why 0.9 is the bar. Fill ⟨team⟩ and ⟨contact⟩. Add a letter or quote line if obtained. |

**Missing slide or beat:** a 10-second worked example of Monday. It already exists as Q&A #3; promote it onto slide 6.

---

## 4. Top 8 improvements for the last ~10 days (ranked by score gain ÷ effort)

The ranks are global. Real-world TEAM actions and BUILD items are listed separately. Gains are merged-score estimates.

### 4a. TEAM: real-world actions (only the people can do these)

| Rank | Action | Owner | Spec | Deadline | Gain | Effort |
|---|---|---|---|---|---|---|
| **1** | **Registration fix and submit** | Team lead | Apply C1: fill name and contact; move the bulletin, planner and connector to "built"; label 46% "pre-registered secondary" in a300; "open" only if pushed; wordcount.py. Confirm MBZUAI permission. | **10 Nov** | Avoids a CRITICAL (+0.1) | 45 min |
| **2** | **Verify → publish → anchor → deploy, in this order, after build item 3** | Team lead (laptop) | PUBLISH.md §1 `adapters.gcc_verify` (log N/N in DEVIATIONS) → §3 `prepare_public_repo.sh` then `gh repo create --public --push` → §4 `anchor_all.sh`, commit the .ots, `ots upgrade` a few hours later, Zenodo DOI → §5 Streamlit Cloud. Put the URL in the one-pager, deck slide 12 and the video description. Say "locked in git on 8 Nov; externally timestamped ⟨date⟩, after the results". | 11 Nov | **+0.4** (J2 evidence +1; removes the G5 judging FAIL) | 2 h |
| **4** | **Clinician playbook review plus a letter of interest** | Team lead and the MBZUAI faculty contact | Send outreach.md A1 (Tawam authors; confirm the corresponding author first) and A2 (SKMC/SSMC paediatrics) **today**. Ask for (a) a 30-min review of `playbook.yaml`, recorded as `reviewed_by: ⟨role⟩, ⟨date⟩`, and (b) one non-binding line of interest in the 12-week shadow pilot. Fallback: a quoted email confirming the Monday decision exists, with permission. Never imply an endorsement. | Land by 17 Nov | **+0.5–0.7** (J3 commercial +2; J1 decision support) | 3–6 h of outreach; uncertain |
| **5** | **Grow the live ledger and score it** | Data owner | `python -m ledger.weekly` as soon as WHO's W45 data are in; anchor the round **before** W46 publishes; repeat for W46. On 19 Nov, score R0/R1/R2 against the published weeks and put "N weeks scored, M inside the 80% band" on slide 12 and the bulletin, whatever the result. Plus (optional) the FluSight PR on **Wed 11 Nov** (`scripts/flusight_wednesday.sh 2026-11-14`, `designated_model: false`): an external, CDC-timestamped forecast. | W45 by ~12 Nov; FluSight 11 Nov 23:00 ET | +0.2 (+0.1 with FluSight) | 30 min/week; FluSight 1–2 h |

### 4b. BUILD: can be done in the repo

| Rank | Item | Owner | Spec | Deadline | Gain | Effort |
|---|---|---|---|---|---|---|
| **3** | **Pre-publication consistency and banned-claim sweep** (must precede TEAM #2) | Pitch + app | Fix M1–M6 and every MINOR in §2.3 in one commit: About :892, :952, :955; Alerts LOSO label; sidebar :94; results/gcc/SUMMARY.md :3/:80/:81; positioning.md §6 marked superseded; one horizon sentence across all 9 files plus a DEVIATIONS row superseding C7; qa.md :38–42 thresholds; remove the ⟦IF BUILT⟧ markers; claims-ledger G1/G6 → R; test counts; `toolbarMode = "minimal"`; human labels on the GCC page. Extend the prepare_public_repo CLAIMS regex with `blind|fill.*beds|calibrated` and add `results/`. Then retake the screenshots. | 11 Nov (before the push) | **+0.25** | 3 h |
| **6** | **Deck visual fixes** | Pitch | Slide 2: flu overlay, with the claim reworded to "can't know which shape". Slide 6: a large Monday line plus a crop of the exceedance table. Slide 7: a new figure `results/gcc/gcc_flu_two_comparators.png` (per country: v1/analog and v1/persistence bars, CIs pooled, flu only). Slide 8: drop fig1; regenerate fig2 with the single-model rank in the title. Slide 9: move the US card out. Slides 10 and 12: single-row callouts; ask-slide criterion note. | 13 Nov | +0.2 | 3 h |
| **7** | **UAE v1 vs seasonal analog, forward in time, plus the training-history plot** (declared in DEVIATIONS **before** computing) | Modelling | Pooled relative WIS v1/analog for flu and RSV (date-cluster bootstrap, as in SUMMARY-v2), the per-fold table, and a scatter of relative WIS vs the number of training seasons for the 12 GCC flu country-seasons plus the UAE folds. Label it POST HOC / exploratory. If the ≥2-season pattern holds (4/4 UAE folds beat the analog), it goes on slide 9 and in Q&A #1; if the pooled flu ratio is ≈1, say so. | 14 Nov | +0.15 (defuses J2's sharpest computation) | 2–3 h |
| **8** | **Planner: workforce that means something** | App | Drive staff absence from the **flu** forecast (or a declared flu + RSV weighting) and make "Enter my HR figure" the default, with SIMULATED as the opt-in. Add a column "extra agency/bank shifts to book (AED)" so the gap is priced. Show the AED column in the screenshot. Keep every label SCENARIO. Add a Q&A line: "why flu drives staff absence". | 15 Nov | +0.15 | 3 h |

**Next, if time remains (not in the top 8):**
- Full Arabic coverage of the card and the bulletin charts (+0.1, 3 h).
- GCC decision-value back-test, "wasted surge weeks vs last year's pattern", declared first (+0.2, 5 h, medium risk).
- Port `/tmp/r3audit/gcc_sens.py` into `eval/` so the robustness numbers cited on slide 7 are reproducible from the repo (+0.05, 1 h).

**Don't spend time on:** model changes, US v2, retuning, Chronos-2, weather, or more secret-sharing polish.
