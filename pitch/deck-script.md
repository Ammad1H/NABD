# NABD: 12-slide deck script (round 4, BUILD-SPEC v1.7, impact first)

> **Narrative order superseded on 14 Nov 2026 by `pitch/story.md` (v3: borrowed strength first).** Slide contents below stay valid; add slide 7b and use the v3 order.

**Rules:**
- Every number traces to `results/`, `data/raw/` or `research/`. See `research/claims-ledger.md`; a claim that isn't in the ledger can't go on a slide.
- `research/positioning.md` §4.6 (the stop list) and the BUILD-SPEC v1.7 BANNED list are binding.
- ⟦IF BUILT: …⟧ marks a round-4 output being built in parallel (winter planner, bulletin, public repo/anchor). If it is missing on 19 Nov, **cut the line**; never estimate it.
- **Order (v1.7):**
  - pain → who decides weekly and what a wrong call costs → NABD;
  - then evidence: Gulf test (46% vs past-season patterns, a pre-registered secondary; 9% vs last-week persistence, the pre-registered primary, met) → US "missed our bar; 7th of 21" → UAE parity caveat;
  - then the pilot ask, with the live ledger.
- **The three numbers to say out loud:** **2,189** · **46%** · **7th of 21**. Don't speak 1.22, 1.002 or 1.059; show them on the slide.

**Headline (slide 1 and the video's last line):**
> **UAE respiratory seasons change timing and shape from year to year, and to our knowledge no one publishes a forecast of the next three weeks. NABD is an open RSV and flu forecasting hub for Abu Dhabi, tested out of sample across the Gulf.**

---

### 1. Title
- **On slide:** NABD (نبض, "pulse"): an open RSV and flu forecasting hub for Abu Dhabi. Statement 06 · Ammad Hassan (solo entrant) · MBZUAI.
- **Visual:** a pulse line opening into a forecast fan.
- **Notes (≈25 words):** "Every winter Monday, someone in Abu Dhabi decides how much RSV and flu to prepare for. NABD gives them a checkable range for the next three weeks."

### 2. The pain: a Monday decision, made with last year's pattern
- **Problem statement (on slide, 40 words; adapted from `docs/REVIEW-R3-judges.md` §2 within the stop list):**
  > Every winter week, Abu Dhabi's paediatric bed managers and public-health officers plan the next three weeks of RSV and flu. Their defaults are last week's numbers and last year's pattern, but UAE seasons change timing and shape from year to year, you can't know in advance which you'll get, and no checkable forecast exists.
- **Visual:** the influenza season-shape overlay (`results/uae/season_shape_flu.png`, from `eval/deck_figures.py`): every UAE season from WHO FluNet, aligned at ISO week 27, with 2024/25 (plateau) and 2025/26 (spike) highlighted.
- **Callouts** (WHO FluNet UAE sentinel, our computation, `research/positioning.md` §1.1):
  - flu peaked at **40.6% in week 42** (Oct 2025); the season before, it ran a five-month plateau that peaked in **week 7 (Feb 2025)**;
  - RSV peak height ranged **20% to 30%** (2022/23–2025/26). Some seasons look alike (this season's flu peak is close to last season's); the point is that you can't know in advance which shape you'll get.
- **Notes (≈40 words):** "Plan this winter from last winter and you're wrong on timing and size. That's not a crisis claim: DoH says this season looks like the last two. It's the normal state of UAE respiratory seasons, and it recurs every year."

### 3. The burden behind the curve
- **On slide:**
  - **2,189**: RSV admissions of children aged ≤5 at one Abu Dhabi hospital (Tawam, SEHA), 2018–22. Infants under 6 months stayed **5.8 days** on average [S1].
  - Dubai claims, 2014–23: **22%** of under-2s with RSV were hospitalised, and **<2%** had a known risk factor, so you can't pick the at-risk children from a list. Median admission cost **US$2,241** [S3].
  - The UAE publishes no flu case counts ("exact data … not available", The National, Jan 2026 [S6]).
- **Small print:** the Tawam data straddle COVID-19 (2020–21); positivity ranged 2.9% → 16% by year.
- **Notes:** "Two thousand one hundred and eighty-nine children, at one hospital, in five years. The youngest stay nearly six days, so every admission occupies a bed for most of a week."

### 4. Who decides each week, and what a wrong call costs
| Who | Weekly decision | Today's tools | Cost of a wrong call |
|---|---|---|---|
| **SEHA/PureHealth paediatric ops** (ED, wards, PICU) | Surge roster, bed opening and elective deferral for the next 1–3 weeks | Own census (looks back); ≤72 h command-centre tools | Over-staffing as the wave turns, or boarding at the peak. RSV stays of 4–6 days keep beds occupied |
| **ADPHC / DoH surveillance** (duty officer, UMOC) | Advisories, provider briefings, "is this season as expected?" | Tableegh notifications, UMOC early warning, WHO reporting | Advisories after the surge, or too many (alert fatigue); no probabilistic "how big" to brief hospitals with |
| **Immunisation programme** | Campaign timing, catch-up messaging, stock | A fixed window (infant RSV 1 Sep–1 Mar, secondary source [S4]); vaccine arrival dates | In 2 of 4 seasons RSV was already ≥10% positive before 1 Sep (context, not a prediction) |

- **Source:** `research/positioning.md` §2.
- **Notes:** "Three desks, one question: how big will the next three weeks be, and how sure are you?"

### 5. The gap: Abu Dhabi detects well; the forecast layer is missing
- **On slide:**
  - Tableegh (Malaffi-linked notifications), UMOC (AI early warning) and Rasid (wastewater) **detect**.
  - **Missing**, to our knowledge, is a public, checkable answer to "how big will the next three weeks be, and how sure are we?"
- **Visual:** a layer diagram, detect → **forecast** → operate. NABD sits in the middle layer, labelled "built to plug into them; consumes Tableegh-shaped aggregate counts".
- **Notes:** "We don't replace anything Abu Dhabi runs. NABD is the forecast layer between surveillance and the bed manager."

### 6. NABD: what runs today
- **Built:**
  - WHO FluNet UAE → NABD-UAE-v1, a linear growth model on the logit of sentinel positivity with a seasonal term and testing volume. It produces **probabilistic forecasts with coverage reported**, from the nowcast to +3 weeks after issue, labelled by target week (skill measured at a conservative 11-day publication lag).
  - The bilingual Arabic/English card shows:
    - the **chance of crossing each pressure threshold** and the forecast direction;
    - the persistence line, always shown alongside;
    - exact per-signal "why this forecast" contributions.
  - A playbook action for a named role → **Approve / Modify / Dismiss** with a reason → a hash-chained audit. A card that contradicts itself is blocked and can't render.
  - The season-shape page, the paediatric bed-days SCENARIO page and the pilot data connector (`docs/PILOT-DATA-SPEC.md`: aggregate weekly counts, k ≥ 10 suppression).
- **In build for 20 Nov:**
  - the weekly bilingual bulletin (built);
  - the hospital winter planner (built);
  - ⟦IF DONE⟧ the public repo and externally timestamped ledger.
- **Visual:** `app/screenshots/01_weekly_card_en.png` plus the architecture strip.
- **Notes:** "Version one is deliberately simple and auditable. On Monday the bed manager reads one line: the chance RSV crosses your threshold next week, and whether it's heading up or down."

### 7. Evidence I: tested out of sample on three Gulf countries
- **Title:** *"We froze the method, locked the test plan, then downloaded Oman, Qatar and Saudi data."*
- **On slide (two bars per comparison, influenza):**
  - **vs planning from past-season patterns:** **46% less forecast error.** Relative WIS 0.536 (95% CI 0.464–0.616); below 0.6 in each of the three countries. *Pre-registered secondary.*
  - **vs last-week carry-forward (persistence):** **9% less error.** 0.914 (95% CI 0.843–0.983). *Pre-registered primary: MET.* It survives dropping any one country (0.904–0.929) and a country-clustered bootstrap (0.841–0.984) (`docs/REVIEW-R3-audit.md` §0).
  - **Wins and losses:** won 9 of 12 flu country-seasons. **Losses shown:** Oman 2022/23 and 2024/25; Qatar 2023/24 a tie.
- **Small print, same size:**
  - retrospective on revised WHO data;
  - n = 3 countries, ≈4 seasons each;
  - forward in time (each country's own earlier seasons only);
  - the plan was locked in our local git 90 s before the data commit; it is self-attested ⟦IF DONE: "anchored ⟨date⟩, after the result"⟧;
  - the method was chosen after the UAE results;
  - Bahrain and Kuwait were excluded by the pre-set data rule;
  - RSV is a secondary outcome (vs persistence 0.798, but its country-clustered interval crosses 1, and its intervals are too narrow outside the UAE: 95% coverage 0.83).
- **Visual:** `results/gcc/gcc_flu_two_comparators.png` (per country and pooled: vs past-season pattern and vs persistence; influenza only).
- **Source:** `results/gcc/SUMMARY.md`; `docs/PREREG-GCC.md`.
- **Notes (≈35 words):** "This is the test we couldn't tune for. Against the planner's default, last season's pattern, it cut influenza error by forty-six per cent. Against carrying last week forward, nine per cent, which met our pre-set bar. Every loss is on the slide."

### 7b. Evidence I-b: borrowed strength (new, 14 Nov; not yet in the Slides artifact)
- **Title:** *"A short record is the UAE's problem. Borrowing other countries' seasons fixes it, in 18 countries we had never looked at."*
- **On slide (influenza):**
  - **Pooled model vs each country's own-record model:** **23% less forecast error.** Relative WIS 0.767 (95% CI 0.681–0.832). *Pre-registered primary: MET.* Better in 18 of 18 countries.
  - **Where the record was short (≤ 2 earlier seasons):** **38% less.** 0.624 (0.540–0.705). *Pre-registered secondary.*
  - **vs last week carried forward:** 12% less (0.879, 0.850–0.901), in all 18; the own-record model lost to it on the same cells (1.145).
- **Small print, same size:**
  - 36 countries named in advance, 18 met the pre-set data rules, all 18 shown;
  - plan locked before download and model locked before any held-out row was extracted, in our local git; self-attested ⟦IF DONE: "anchored ⟨date⟩, after the result"⟧;
  - retrospective on revised WHO data; positivity, not hospital load;
  - nothing here is a confirmatory UAE result (UAE data had been seen); the pooled model runs on the ledger as a challenger;
  - roster rule replayed on the same forecasts (post hoc): 10.5 mismatch weeks a season vs 12.3 for the own-record model, but no clear gain over last week carried forward (11.1), and slightly more missed surge weeks (2.7 vs 2.2).
- **Visual:** `results/pool/fig_forest_pool_vs_local.png` (per country) and `results/pool/fig_skill_vs_own_seasons.png`.
- **Source:** `results/pool/SUMMARY.md`; `docs/PREREG-POOL.md`; `results/replay/pool/SUMMARY.md`.
- **Notes (≈40 words):** "On the UAE's own four seasons we only tie. So we asked: can a country with a short record borrow from the rest of the world? We locked the plan, then tested on eighteen countries we'd never opened. Twenty-three per cent less error, in every one."

### 8. Evidence II: we set our bar at the CDC's best and missed it
- **Title:** *"We set our bar at the CDC's best. NABD v1 missed it, and here is exactly where."*
- **On slide:**
  - Protocol frozen before any test score (`docs/FREEZE.md`; self-attested). Only real-time data versions; 11,660 forecasts across 53 US locations and two seasons.
  - Relative WIS vs the CDC FluSight ensemble **1.22 (95% CI 1.01–1.52)**, against a bar of < 1.15: **NOT MET**, in red, by us.
  - **Among individual CDC-hub models**, scored the same way (method declared before computing):
    - **7th of 21 single models in 2024/25** (13th of 41 including ensembles);
    - **19th of 25 in 2025/26** (40th of 46), level with the baseline.
  - Excluding the national series still fails (1.198).
- **Visual:** `results/figures/fig2_league_table.png`. **Slide title** uses single models, with the all-models rank in brackets so it matches the figure's own titles. Add `results/figures/fig1_rel_wis_season_horizon.png` with the 1.15 margin line.
- **Source:** `results/SUMMARY.md` (PRIMARY, S3, D6, D7); `results/tables/league_table.csv`.
- **Notes (≈30 words):** "There's no UAE hub to compare against, so we went to the hardest public bar there is. One season we sat seventh of twenty-one; the next we fell to the baseline. We're showing you the season we lost."

### 9. Evidence III: the UAE's own record, and what we don't claim
- **On slide:**
  - **The UAE's own record is at parity.** Trained only on earlier seasons, v1 vs persistence = **1.002** (flu and RSV) (`results/uae/SUMMARY-v2.md`).
  - **Why, in our reading (post hoc):** UAE sentinel data in FluNet start in 2022. The fold trained on one season lost badly (flu WIS 4.75 vs 2.21). With ≥2 training seasons, flu won both folds (2.54 vs 2.66; 1.94 vs 3.08), and RSV split (`results/uae/v2/tables/forward_wis_by_season.csv`). The Gulf countries had history from 2015.
  - **More signals didn't help:** multi-signal v2 was worse than v1 (**1.059**, CI 1.016–1.111) under a locked protocol. It stays a challenger.
  - **Lead is on size, not onset:**
    - US median onset lead is 0 weeks at the primary threshold (3/100k) for every rule, the CDC's included.
    - Every rule had **0 false alarms** at that threshold. NABD's first alerts were less often late (2024/25: 9 late, vs 13 for the CDC ensemble and 19 for a census rule), but the census rule caught more onsets in time that season (28 vs 17 of 51).
    - In 2025/26 NABD caught 29 of 52 in time, vs 24 for the census rule.
    - All alert metrics are diagnostic (`results/tables/alerts_us.csv`, `alerts_us_detail.csv`).
- **Notes:** "We report what didn't work as plainly as what did. On the UAE's short record we tie, and that's exactly why we run a live, hashed ledger."

### 10. Workforce: from the population wave to the hospital's own constraints
- **On slide:**
  - **App page "Hospital winter planner (SCENARIO)"** Takes NABD's forecast and the hospital's **own** inputs (annual paediatric RSV admissions, length of stay, beds, nursing headcount, and a baseline winter sickness-absence rate the hospital's HR sets). Shows, per horizon:
    - scenario bed-days and % of ward capacity;
    - a scenario staff-absence range;
    - the net roster gap, in AED.
  - Adds an **occupational-health role** to the playbook (vaccination push, sick-leave flexibility, post-break cover).
  - **Every number is labelled SCENARIO.** We cite no UAE absence statistic, because none credible exists publicly (`research/positioning.md` §1.6).
  - **Employer data path:** a secure-aggregation design (k ≥ 10 employers) on synthetic counts, watermarked **SIMULATED** (`app/workforce.py`). It shows how real absence counts would enter without exposing any employer or worker.
  - **Use limitation:** no individual, employment or disciplinary use. Aggregate only.
- **Visual:** `app/screenshots/04b_winter_planner.png`.
- **Notes:** "Statement 06 is population *and* workforce. We forecast the wave and translate it into the hospital's two constraints, beds and staff, using the hospital's own numbers. We don't fake absence data that doesn't exist."

### 11. Statement 06, requirement by requirement, and responsible by design
| Requirement | Status |
|---|---|
| Multi-signal | Built and scored: lab positivity (sentinel and non-sentinel), testing volume, school and Ramadan calendars (v2). Fusion **didn't help** (1.059), so we ship the lab-plus-climatology model that works, and v2 runs in the ledger as a challenger |
| Explainable detection | Built: exact per-signal contributions per forecast (`results/uae/explain/`); feed-removal test (`results/uae/tables/ablation.csv`) |
| Decision support | Built: exceedance-probability bands, actions for named roles, approval with a reason code, consistency gate. Playbook ILLUSTRATIVE pending clinical review |
| Privacy | Built: aggregate only; person-level fields rejected (tested); k ≥ 10 complementary suppression in the pilot connector |
| Operational validation | Built (diagnostic): lead, sensitivity, PPV, false alarms (US + UAE); latency (US median input age 4 days; UAE lag 7 days on 8 Nov); missing-feed behaviour |
| Health and resilience impact | Bed-days SCENARIO; hospital winter planner (built). A pilot hypothesis, not a result |

- **Also:** persistence always shown (automation-bias guard); freshness badge; WHO non-commercial terms respected.
- **Visual:** the checklist with built / scored / simulated tags, beside `app/screenshots/11_about.png`.

### 12. The ask: one hospital, twelve weeks, and a ledger that keeps score
- **Pilot:** a 12-week shadow run on one hospital's aggregate weekly paediatric respiratory counts (`docs/PILOT-DATA-SPEC.md`). No change to care. Exit criterion set in advance: relative WIS < 0.9 vs the hospital's own census carried forward.
- **Live ledger:**
  - Every forecast round is hashed before its target week is published.
  - **Status 8 Nov:** one forecast round (data through W44), re-issued with the v2 challenger; 0 weeks scored (`ledger/SCOREBOARD.md`).
  - ⟦LIVE: N weeks scored on the day⟧
  - ⟦IF DONE: "public at ⟨URL⟩, anchored ⟨date⟩"⟧
- **Ask:** one hospital partner (SEHA/PureHealth or a private group), an ADPHC data conversation, and a clinician to review the playbook. ⟨letter of interest, if obtained⟩
- **90 days:** the shadow pilot; the ledger scored all season; Rasid's wastewater signal tested as an input and published either way; more Gulf countries.
- **Business (hypothesis):**
  - a public-health forecast-feed licence per country per season;
  - a hospital-operations seat per facility, running on the hospital's own data;
  - WHO data only for the public feed and evaluation.
  - Open, non-exclusive licence. Any exclusive deal goes to the organiser first for 6 months (T&C ROFR, `research/tc.md`).
- **Notes:** "One hospital, twelve weeks, aggregate counts. If we don't beat your own census, you walk away, and our record stays on file either way. To sense is to predict. NABD is how Abu Dhabi checks the prediction."

---

**Never on any slide** (BUILD-SPEC v1.3/v1.6/v1.7; positioning.md §4.6):
- "published", "public" or "outside-anchored" for the ledger until it is;
- "blind" (use "out-of-sample, plan locked before download"); "verified row-for-row";
- "fewer false alarms"; "calibrated" without qualification;
- "nobody publishes" without "to our knowledge";
- the UAE "3/3 onsets" (retired LOSO design); the retired UAE LOSO 0.76/0.78 or "7 of 8";
- RSV Gulf as a headline;
- E1 "better during surges"; "near-parity with the CDC"; the CDC ensemble's 21–36% presented as NABD's;
- Chronos-2 or ACI as active; ED, weather or wastewater as inputs; v2 as an improvement;
- "early warning of onset"; "RSV is climbing"; crisis framing;
- SEHA bed or ED numbers; workforce-absence figures; "fills Abu Dhabi's paediatric beds";
- "predicts the nirsevimab window"; "pre-registered" for the UAE v1 numbers.
