# REVIEW R5: gap-finding panel. What would a top-3 Statement 06 entry show that NABD doesn't? (9 Nov 2026)

> **What this file is.** A simulated review written by an AI assistant in a separate session, asked to act as a gap reviewer. No human reviewer, government official or company employee wrote, saw or endorsed it. It is kept because the fixes it prompted are traceable in `docs/DEVIATIONS.md`.

**Panel.** J1 is a DoH/ADPHC public-health official. J2 is an AI scientist (Microsoft/G42/MBZUAI). J3 is a partnerships lead (PureHealth/M42). None of us built NABD.

**Brief.** This is not another integrity audit. R2–R4 did that well, and round 5 closed most of R4's sweep items. This round asks one question: **against the entries most likely to finish top 3, where does NABD lose points?** We don't repeat R4 items except where a gap depends on them. Those are cross-referenced as "R4 §x".

**Read.**
- pitch/: registration, one-pager, deck-script, video-script, qa, plus the 12 deck slides (`pitch/deck/project/slides/*.html`, text extracted)
- research/: positioning.md, tc.md, competitors.md
- docs/: TECHNICAL, STATUS, REVIEW-R3-judges, REVIEW-R4
- results/: SUMMARY.md, gcc/SUMMARY.md, uae/SUMMARY-v2.md, uae/posthoc/SUMMARY.md
- all 14 screenshots, including both bulletin pages (bulletin/out PDF as rendered)
- `vendor/nabd_v2_kit/nabd_kit/gbm_global.py`; `git log` (round 5 commits 22c945d → 019d653); `git remote -v` (empty); `anchors/` (absent); `playbook.yaml` (`reviewed: false`)

---

## 0. The competitive frame: what we benchmark against

1. **This edition is three focus areas competing for three prizes.**
   - The 2026 Digital Innovation Challenge runs Fertility, Population Health and Wellbeing under "To Sense is to Predict". Three finalists share USD 105k at GITEX, and selected solutions "may be considered for further validation and possible incubation, piloting, and scale" ([intlbm, 15 Oct 2026](https://intlbm.com/2026/10/15/future-health-unveils-global-challenge-to-boost-health-innovation/)).
   - So NABD isn't only competing with other Statement 06 entries. It is competing with polished consumer-facing Wellbeing and Fertility demos. **Demo legibility and a felt "so what" matter more than in a pure surveillance track.**
2. **The previous Future Health Challenge (with MIT Solve, May 2026) rewarded deployment and quantified field outcomes.**
   - ThinkMD (top award): decision support used by 9,000+ frontline workers in 885 facilities; flagged symptom patterns before a cholera outbreak in Zambia.
   - VectorCam: AI mosquito surveillance; data completeness rose from about 60% to over 90% in field evaluations.
   - Huna: blood-test cancer-risk AI; pilots screened 500,000+ patients ([pulse2](https://pulse2.com/future-health-challenge-awards-300000-for-early-detection-and-population-health-sensing-solutions/)).
   - **Read-across:** the same organiser picked entries with *a number that says what changed in the world*. NABD's numbers say how accurate the forecast was, not what changed.
3. **The DoH's own flagship sets the vocabulary judges will use.**
   - The DoH–Microsoft Population Health Intelligence platform (GITEX 2025) is a "digital twin" that integrates clinical, lifestyle and environmental data, predicts trends and **simulates the potential impact of interventions**, with geospatial simulation. Its initial focus is obesity and cancer, with no respiratory component ([Abu Dhabi Media Office](https://www.mediaoffice.abudhabi/en/health/department-of-health-abu-dhabi-unveils-worlds-1st-ai-powered-population-health-intelligence-platform-at-gitex-global-2025/)).
   - Microsoft and DoH judges will look for: multi-source, geospatial, "what if we act", and how it plugs into PHI.
4. **The season context is benign.**
   - The DoH Director of Surveillance says activity "has so far remained similar to the previous two seasons". The 2026/27 campaign now covers flu, RSV and pneumonia, with maternal RSV vaccination and infant monoclonals ([Khaleej Times](https://www.khaleejtimes.com/lifestyle/health/flu-campaign-2026-27-expanded-changes-explained)).
   - So the live card will show "stand down" all through judging (it already does: 51%, falling). **The live product has no dramatic moment to show, so the demo has to create one honestly** (gap G2).
5. **What the state of the art looks like to J2.**
   - Hierarchical pooling across locations is now standard. INFLAenza, a Bayesian spatio-temporal model with a seasonal effect shared across states, ranked 4th of 24 in 2023/24 FluSight and was the top individual model, 4.1% behind the ensemble ([medRxiv 2025](https://www.medrxiv.org/content/10.1101/2025.03.03.25323259.full.pdf)).
   - Time-series foundation models are being benchmarked on epidemic data. Fine-tuned numerical models (PatchTST and similar) beat zero-shot Chronos at 2–4 weeks, and pretraining on related series helps ([arXiv 2606.19560](https://arxiv.org/pdf/2606.19560)).
   - **Read-across:** "we pool across neighbours to fix short history" is a recognised, honest move. "We ran a foundation model zero-shot" isn't a story by itself.
6. **What a plausible top-3 Statement 06 entry shows** (our composite, not a known team):
   - (a) real multi-source signals, including environmental (heat or dust) and a real workplace signal;
   - (b) a map, with locations;
   - (c) a demo moment where the system flags something before it happens;
   - (d) a quantified "what changes": admissions, sick days, AED;
   - (e) a named Abu Dhabi partner or advisor and a team slide;
   - (f) Arabic throughout.

   NABD leads clearly on (g) evidence discipline and (h) responsible AI. It is behind on (a)–(f).

   **Note:** competitors.md found at least 8 public Statement 06 repos, mostly heat/workforce dashboards on simulated data. Any one of them that adds a real weather feed and one real employer is a better *statement fit* than NABD on the workforce half.

---

## 1. Scores (1–10)

The six criteria match R3/R4. Half points are allowed. Round-5 fixes are credited: the banned-claim sweep, the LOSO label, one horizon convention, the flu season-shape figure, the two-comparator Gulf chart, the UAE vs analog post hoc analysis, and the Monday line on slide 6.

| Criterion | J1 DoH/ADPHC | J2 AI scientist | J3 PureHealth/M42 | Mean | R4 mean |
|---|---|---|---|---|---|
| Impact | 6 | 5.5 | 5 | **5.5** | 6.3 |
| Technical depth / novelty | 6 | 5 | 5 | **5.3** | 5.5 |
| Working demo & evidence | 7.5 | 7 | 6.5 | **7.0** | 6.8 |
| Responsible AI | 8 | 8 | 7.5 | **7.8** | 7.8 |
| Scalability / deployment | 6.5 | 7 | 6 | **6.5** | 6.7 |
| Commercial / pilot | 5 | 4 | 3.5 | **4.2** | 4.2 |
| **Unweighted, per judge** | **6.5** | **6.1** | **5.6** | **6.1** | 6.2 |
| **Impact-first weighted*** | 6.5 | 6.0 | 5.6 | **6.0** | — |

\*Weights reflect "Impact first. Then proof that it works": Impact 30%, demo & evidence 25%, technical 15%, and 10% each for responsible AI, scalability and commercial.

**Why our impact score is lower than R4's (5.5 vs 6.3).** R4 scored impact against NABD's own earlier versions. We score it against the frame in §0.
- NABD quantifies *burden* (2,189 admissions) and *forecast error* (−46%), but never *what changes* if Abu Dhabi runs it.
- Its live card says "stand down".
- Its onset lead is 0 weeks.
- Its target is national positivity, not load.
- No judge leaves the room able to repeat "NABD would have saved X".

**Verdict: merged ≈ 6.1 (impact-weighted 6.0).**
- **Standing:** a likely finalist on evidence quality, but not top-3. Panel estimate: about 15% for top 3 as it stands, against a top-3 bar we put at about 7.3–7.6.
- **R4 preconditions not yet done:**
  - registration placeholders (due **10 Nov**);
  - public repo, anchors and hosted app (R4 C2);
  - ≥2 scored ledger weeks (R4 TEAM #5).

  Without them, every gain below is capped, because judges can't open what they're scoring.
- **With those plus the five changes in §3,** the panel estimate is **7.2–7.6**, about 35–40% for top 3.

### Per-judge one-liners
- **J1:** "I believe the forecast. I can't tell what Abu Dhabi gains, and on the workforce half of my statement I'm looking at a watermark. Where is the environmental signal the MoHAP climate plan asked for? Where are the locations?"
- **J2:**
  - "The evaluation is the best in the pile. The model is a five-term OLS on logits, from an MBZUAI team, in a challenge MBZUAI co-created. Your own kit ships a Flusion-style global quantile GBM (`vendor/nabd_v2_kit/nabd_kit/gbm_global.py`) that you've never run on the Gulf.
  - Your diagnosis of the UAE parity is 'too little history', and pooling across countries is the textbook fix. You never tried it."
- **J3:**
  - "No team slide, no names, no advisor, no price, no partner.
  - The planner's own output says the gap is zero to one shift. You've built a careful instrument and haven't shown me the bill it saves."

---

## 2. Gap list

Severity reflects expected merged-score loss against a top-3 competitor: CRITICAL ≥ 0.4, HIGH 0.2–0.4, MEDIUM 0.1–0.2. Effort assumes the current team; "BUILD" can be done in the repo, and "TEAM" needs real-world action.

### G1. CRITICAL: no quantified "what changes in Abu Dhabi if NABD runs"
**Why it costs points.**
- Impact is weighted first. The pitch's chain stops one link short: burden → forecast error → **(missing: decisions changed → bed-days, shifts, AED)**.
- The 46% is an error ratio. A DoH official can't brief upward with it, and J3 can't price it.
- The bed-days and planner pages are SCENARIO arithmetic on *one* forecast. They show size, not *value relative to what the planner does today*.
- The relative-economic-value machinery already exists for the US (D10, `eval/round2.py:384`). It was never pointed at the Gulf, where NABD actually wins.

**Fix (BUILD; modelling + pitch; 1–1.5 days). A decision-value back-test plus a transparent Abu Dhabi impact estimate.**
1. **Declare it first** (DEVIATIONS row "V1, decision value, declared before computing"). Fix in that row: the thresholds (the playbook's flu 15/30% and RSV 10/20%), the decision rule and the cost ratios.
2. **Re-emit the quantiles.** Rerun the *frozen* GCC forward-in-time forecasts with the full quantile set written out. `results/gcc/tables/scores_long.csv` keeps only the median and WIS, but the same code with no refit choices can write quantiles.
3. **Decision rule.** The decision is "activate surge roster for week t+k if P(Y > T) ≥ p\*". Apply the same rule to the NABD, seasonal-analog ("last year's pattern") and persistence forecasts.
4. **Report, per country-season and pooled:**
   - surge weeks correctly called;
   - missed surge weeks;
   - wasted surge weeks;
   - Brier score and its skill vs the analog;
   - relative economic value over cost/loss ratios 0.05–0.5 (Richardson 2000; the code exists).
   - Also run it on the UAE ≥2-training-season folds, labelled POST HOC.
5. **Impact translation (ESTIMATE, every input on screen and sourced or marked illustrative):**
   - Formula: (wasted surge weeks avoided × surge cost) + (missed surge weeks avoided × boarding cost) for a Tawam-scale paediatric unit.
   - Surge cost = bank shifts × AED shift rate. Boarding cost = excess bed-days × AED.
   - The output is one sentence for slide 1, the video and the registration's a300 at resubmission. Template: *"Over 12 out-of-sample Gulf flu seasons, a surge rule driven by NABD instead of last year's pattern missed N fewer surge weeks and wasted M fewer per season. For a Tawam-scale unit that is about AED A–B a season (estimate; assumptions shown)."*
6. **If the result is weak, say so.** Then headline the stand-down value: "knowing when *not* to surge". Never tune p\* after seeing the result; fix it in the declaration (e.g. p\* = 0.3, the playbook's own value).

**Why this beats more modelling.** It converts the strongest evidence NABD has (Gulf, 0.536 vs analog) into the currency judges score first.

### G2. HIGH: the demo has no "wow moment", and the live season won't give one
**Why it costs points.**
- Judges test the prototype directly (20–30 Nov). What they'll see:
  - a dense Streamlit page with four tables;
  - an evidence sidebar in small print;
  - a card that says "51%, falling, no surge roster".
- The DoH has said this season looks like the last two (§0.4), so nothing dramatic will happen live.
- Wellbeing and Fertility entries will demo a personal, visual moment.
- NABD's most persuasive fact, that it beat last year's pattern by 46% out of sample, is a bar chart on page 5.

**Fix (BUILD; app; 1 day). A "Season replay" page, placed first in the navigation.**
- **Slider:** scrub through the issue weeks of a season. Use a GCC out-of-sample season (forward-in-time, plan locked), selectable for **every** included country-season, losses included. Add the UAE 2024/25 and 2025/26 folds, labelled POST HOC.
- **Each step shows:**
  - the Monday card NABD *would* have issued (band, action, P(exceed));
  - what "last year's pattern" and "last week" would have implied;
  - truth revealed up to that week only.
- **Running tally (from G1):** right calls, missed surges, wasted surges, NABD vs analog.
- **Default view:** the most recent complete season for the pooled set, *not* a hand-picked win. Write the default choice into the DEVIATIONS row from G1.
- **Polish (same day):** a "Monday view" landing (one bilingual sentence per role, the fan chart, one action), with tables collapsed behind "details". Move the evidence sidebar into a tab.

**Demo-script beat:** "Here is Qatar, 2023/24, a season our model never saw. Watch what the card said each Monday, and what last year's pattern would have told you."

### G3. HIGH: AI depth is thin for an AI-university team, and the obvious honest upgrade is sitting unused
**Why it costs points.**
- **What runs today:**
  - the headline model is a 5-term pooled linear regression on logit positivity;
  - the multi-signal challenger hurt (1.059);
  - Chronos-2 was not run;
  - the US ensemble is two damped-growth members.
- J2 will score technical depth at about 5 whatever the evaluation quality. The challenge is co-created by MBZUAI, Microsoft and Inception42.
- **NABD's own diagnosis points straight at a fix it never tried:**
  - UAE parity comes from short history (sentinel data from 2022; the 1-season fold lost 4.75 vs 2.21; ≥2 seasons beat the analog 4/4, post hoc);
  - **pooling across countries** is the standard remedy (§0.5);
  - the vendored `GlobalQuantileGBM` is explicitly built for "several countries' FluNet series".
- **There is a clean place to test it:** PREREG-GCC §24 says "Other EMRO countries are **not** part of this test". Their FluNet data have never been downloaded, so a second locked holdout is still available.

**Fix (BUILD; modelling; 2–3 days; honest-risk: it may not help).** NABD-POOL is the challenger, evaluated under a new lock.
1. **Members:**
   - **(a) Partial-pooling v1.** Country-level coefficients shrunk toward a Gulf mean by empirical Bayes or a small NumPyro/PyMC model. The seasonal-shape term is a shared climatology plus a country offset. This targets the cold-start problem directly.
   - **(b) `GlobalQuantileGBM`.** Trained across all available FluNet series (GCC + UAE, fourth-root scaled), with **lagged neighbour activity** as features, respecting each country's publication lag at issue. This adds a "locations" dimension (Statement 06 req. 2) and a genuine early-warning hypothesis: do Gulf neighbours lead the UAE, given 95M DXB passengers a year?
   - **(c) Optional.** Chronos-2 or TimesFM zero-shot as a member, run on a team laptop (the wrapper `models/chronos2.py` exists). Report it, but don't headline it.
2. **Lock** `docs/PREREG-EMRO.md` *before download*:
   - the same inclusion rule as GCC;
   - candidates: Egypt, Jordan, Morocco, Tunisia, Lebanon, Iraq, Iran, Pakistan, Afghanistan, Libya, Syria, Yemen (as available);
   - **primary:** pooled flu rel. WIS of NABD-POOL vs v1 < 1 with upper bound < 1;
   - **secondary:** vs analog and persistence; the UAE 1-training-season fold (cold-start mechanism test, labelled retrospective).
3. **Ship the result either way.** A pass → POOL becomes a ledger challenger and the headline technical slide: "a Gulf-pooled model that fixes cold start, tested on N untouched countries". A fail → one line in "what didn't work". **Never re-score GCC as a claim:** it's development data now.
4. **Time-box:** if the lock isn't done by 13 Nov, drop (a) and run (b) only.

### G4. HIGH: Statement 06 asks for environmental, service and workplace signals plus locations, and NABD has none of them for real
**Why it costs points.**
- The organiser's own requirement list (research/tc.md):
  - **#1 multi-signal** (clinical/service + environmental/workplace/community);
  - **#2 "which signals, locations and time periods contributed"**;
  - **#6 "reduced sickness absence and lost workdays"**.
- **What NABD's scored inputs are:** one country's lab positivity, testing volume and calendars.
  - Weather is "planned, blocked in our build environment". That reason won't survive on a team laptop.
  - There is no location dimension; the forecast is UAE-national.
  - Workforce is a SIMULATED secret-sharing demo that "feeds no forecast" (screenshot 10).
- **Threat:** a competing heat/workforce dashboard that wires in real weather and one real employer will win J1's statement-fit points outright, even with a weaker model.

**Fix (BUILD; data + app; 1 day; plus TEAM below).**
1. **Environmental.**
   - Pull Open-Meteo/ERA5 temperature and humidity, plus the Open-Meteo air-quality API (PM10, dust, CAMS-based), for Abu Dhabi, Al Ain and Dubai, 2022→now, on a team laptop. Commit the CSV with provenance.
   - Show it as a context strip on the card. Run a **pre-declared feed test** (the same ablation as v2) and report it even if it's null.
   - Cite the MoHAP Health Sector Climate Adaptation Plan 2026–31 (positioning §3.3) on the slide.
2. **Community.**
   - Google Trends, UAE, weekly: Arabic and English symptom terms (e.g. انفلونزا, "flu symptoms") and a **workplace proxy** ("sick leave" / إجازة مرضية).
   - Pre-declare a lead-lag correlation vs FluNet UAE. This is a real, public, non-lab signal that needs no partner.
3. **Locations.**
   - A Gulf map page with each country's current band (data already in `flunet_gcc.csv`) and, from G3(b), the neighbour-lead result.
   - This answers req. #2's "locations" honestly at the country level, while stating that emirate or district resolution needs Tableegh aggregates.
4. **TEAM, real workforce feed (uncertain, cheap to ask).**
   - Ask MBZUAI HR or the campus clinic, and one or two employers the team can reach, for **aggregate weekly respiratory sick-leave or clinic-visit counts for 2023–2026**, with small-cell suppression (< 5 → suppressed).
   - **One real series** turns "SIMULATED" into "one real employer feed, n = 1, descriptive". Plot it against the flu forecast on the planner page.
   - Owner: team lead. Effort: 2–3 emails; answer by 16 Nov.
   - **This is the single cheapest way to stop losing the workforce half of the statement.**

### G5. HIGH: team and credibility signals are missing
**Why it costs points.**
- **No team slide exists** (12 slides: cover → ask).
- `⟨team⟩` and `⟨contact⟩` placeholders remain on the cover, the ask slide, the one-pager (×2) and the deck-script, and **registration is due 10 Nov**.
- No named advisor, no clinician, and `playbook.yaml reviewed: false`.
- Previous winners brought thousands of users (§0.2). A student team has to borrow credibility, and NABD hasn't borrowed any.
- J3 can't take a partnership forward without a counterparty, and J1 can't vouch for a playbook nobody in Abu Dhabi has read.

**Fix (TEAM; team lead; 2–5 days elapsed, about 4 h of effort).**
1. Fill names and contact today (R4 C1).
2. **Recruit one named MBZUAI faculty advisor** (machine-learning or healthcare-AI faculty). Ask: 30 minutes, permission to list their name and role, and a read of the G3 pre-registration.
3. **One clinical or public-health advisor:** outreach A1/A2 (Tawam RSV authors, SKMC/SSMC paediatrics) or any UAE-licensed paediatrician or epidemiologist the team knows. Ask for a playbook review recorded as `reviewed_by: <role>, <date>`.
4. **Add slide 1b, "Team".** For each person: name, programme, role on NABD, one relevant credential, plus advisors with permission. Put the team line on the cover.

**Never** imply an endorsement that wasn't given.

### G6. MEDIUM: the business model is a hypothesis with no buyer, price or ROI
**Why it costs points.**
- Slide 12 says only "forecast-feed licence per country per season; hospital seat".
- There is no price, no cost to serve, no first buyer, and no route past the WHO non-commercial clause beyond one sentence.
- J3 scores commercial at 3.5–4. This is NABD's lowest axis in every round (R2–R4).

**Fix (BUILD; pitch; 3 h; depends on G1 for the number).** One block on slide 12 and the one-pager:
- **Public layer:** open and free (WHO data). Funded as a DoH/ADPHC R&D pilot, or as a Gulf CDC regional module. Say *"a respiratory module the DoH–Microsoft PHI platform can host"*; the Microsoft judge will hear that.
- **Hospital layer:** a seat per facility per season, running on the hospital's own aggregates (no WHO commercial use). Price it **as a fraction of the G1 estimated value**, e.g. "≤ 10% of the estimated AED A–B a season". Cost to serve: CPU-minutes a week plus one analyst-day a week a season.
- **First buyer and why:** one SEHA/PureHealth paediatric unit, the shadow pilot; or a private group with recorded record flu-like visits (Burjeel, positioning §1.3).
- **Moat:** the dated, externally timestamped track record. Only true once anchored (R4 C2).

### G7. MEDIUM: scalability is asserted, not demonstrated
**Why it costs points.** "More Gulf countries" is one line on slide 12. The method *has* already run on four countries, but the demo shows only the UAE.

**Fix (BUILD; app + API; 0.5 day).**
- A **country selector** on the weekly card. Live forecasts for Oman, Qatar and Saudi Arabia (and the EMRO countries after G3), produced by the same frozen code with config only.
- Show "N countries · X s per country on a laptop · one config file".
- Expose `/forecast?country=` in the FastAPI.
- Optional: a FHIR R4 `MeasureReport` export of each weekly forecast. Malaffi is FHIR-based, and the export turns "built to plug into Tableegh" into a concrete artefact.

### G8. MEDIUM: Arabic and localisation are still partial where judges will look
**Why it costs points.**
- **Deck:** English except the title glyphs.
- **Video:** English voice only, no Arabic subtitles.
- **Arabic card (screenshot 02):** English in
  - the "why this forecast" sentences;
  - the observed-trend line;
  - the chart caption;
  - the week selector;
  - the "Issued … model … source" line;
  - the whole evidence sidebar.
- **Bulletin Arabic page:** English axis labels and legend.
- A DoH judge who toggles Arabic sees a half-translated product, and "bilingual" is a headline claim. R4 §2.3 flagged this. It is still open, so we raise its severity because the competitive frame is national-programme judges.

**Fix (BUILD + TEAM; 0.5 day + 1 h native review).**
- Route the remaining strings through `app/i18n.py`.
- Render Arabic chart labels in the bulletin with an Arabic-capable font (Noto Naskh/Kufi) and `arabic_reshaper` + `python-bidi`.
- Add Arabic SRT subtitles to the video and an Arabic one-pager.
- A native speaker on the team checks the terminology (e.g. نسبة الإيجابية, عتبة) against ADPHC press releases.

### G9. MEDIUM: "early enough to change action" is conceded, not measured differently
**Why it costs points.**
- The statement wants a warning "early enough to change action". NABD (rightly) says it has 0 weeks of onset lead and forecasts "size and duration".
- But it never *measures* size and duration value: peak timing, peak height, or the week the wave turns (the stand-down signal the live card is giving right now).
- So the concession is the only thing the judge hears.

**Fix (BUILD; modelling; 0.5 day; fold into G1's declaration).** Pre-declare, on the GCC out-of-sample seasons:
- **(i) Stand-down lead:** weeks of warning before positivity falls below T (P(below T at +2) ≥ 0.7), vs the analog and persistence.
- **(ii) Peak-height error and peak-week error** at 1–3 weeks before the peak.

If (i) shows real lead, the honest headline becomes "NABD tells you when to stop surging, N weeks earlier than last year's pattern". That matches this season's live card.

### G10. LOW–MEDIUM: positivity is not load, and nothing in the demo bridges it
**Why it costs points.** Every planner number rests on "admissions ∝ positivity ÷ seasonal sum" (screenshot 04b), which is unvalidated. J1 will ask whether positivity tracks admissions in Abu Dhabi.

**Fix (BUILD; research; 2 h).** Show the one public bridge available: the Tawam study's annual positivity (2.9% → 16%) against its admissions by year [S1], or any published UAE series pairing positivity and admissions. Label it "the pilot's first question". Don't build a model on it.

### Considered and NOT recommended
- **Intervention simulator ("what if the campaign starts two weeks earlier").** PHI does this, but NABD has no transmission model. Building one in 10 days would invite exactly the overclaim the team has worked to remove.
- **More feature fusion in v2.** It already failed under lock (1.059).
- **US v2.** It can't produce evidence before judging (PREREG-US-V2 says so).
- **Re-scoring GCC with a new model as a claim.** That data is development data now.

---

## 3. The five highest-yield changes (expected merged gain ÷ effort)

**Preconditions (R4, not repeated here; without them the gains below are capped):**
- registration filled and submitted **10 Nov**;
- repo public + anchored + app hosted (R4 C2, PUBLISH §1–5);
- ledger rounds for W45/W46 issued, and scored by 19 Nov.

| Rank | Type | Change | Gap | Owner | Effort | Deadline | Expected gain |
|---|---|---|---|---|---|---|---|
| **1** | **BUILD** | **Decision-value back-test + Abu Dhabi impact estimate**: surge-rule replay on 12 GCC flu seasons (plus the UAE ≥2-season folds, post hoc); Brier skill, missed/wasted surge weeks and REV vs last year's pattern; AED translation with every assumption on screen; one impact sentence on slides 1/12, the video and the one-pager. Declared in DEVIATIONS before computing. | G1 (+G9) | Modelling → pitch | 1–1.5 d | 13 Nov | **+0.4–0.5** |
| **2** | **TEAM** | **Credibility package**: team slide with names; one named MBZUAI faculty advisor; one clinician or epidemiologist playbook review (`reviewed_by`); placeholders filled. | G5 | Team lead | ~4 h effort, 2–5 d elapsed | Ask today; land by 17 Nov | **+0.3–0.4** |
| **3** | **BUILD** | **Season-replay demo + Monday landing view**: scrub any out-of-sample Gulf season and see the card each Monday vs last year's pattern, with a running tally from #1. Tables collapsed; evidence in a tab. | G2 | App | 1 d | 15 Nov | **+0.3** |
| **4** | **TEAM** | **One real workforce feed**: aggregate weekly respiratory sick-leave or clinic counts (2023–26, suppressed < 5) from MBZUAI HR/clinic or one reachable employer, plotted against the flu forecast on the planner page; "n = 1, descriptive". | G4 | Team lead | 2–3 emails + 2 h of wiring | Ask today; use if it arrives by 16 Nov | **+0.25** if obtained (≈ +0.1 expected) |
| **5** | **BUILD** | **NABD-POOL on a new locked EMRO holdout**: a partial-pooling v1 plus a `GlobalQuantileGBM` with lagged neighbour activity; `PREREG-EMRO.md` locked before download; the UAE cold-start fold as the mechanism test; reported either way. | G3 (+G4 locations) | Modelling | 2–3 d | Lock 12 Nov, result 16 Nov | **+0.3** (J2 technical +1.5) |

**Next, if capacity remains (in order):**
- G4 environmental and community feeds plus the Gulf map (1 d, +0.2);
- G8 Arabic completion plus subtitles (0.5 d, +0.1–0.15);
- G6 business block, once #1 gives the number (3 h, +0.15);
- G7 country selector and API (0.5 d, +0.1).

**Sequencing:**
- **9–10 Nov:**
  - submit the registration;
  - send the asks for #2 and #4;
  - write the #1 and #5 declarations.
- **11–13 Nov:**
  - publish and anchor (R4);
  - #1 computed;
  - EMRO lock and download.
- **14–16 Nov:** #3 built on #1's outputs; #5 scored.
- **17–19 Nov:**
  - deck, video and one-pager updated with the impact sentence, the team slide and the POOL result (pass or fail);
  - ledger weeks scored;
  - screenshots retaken.

**Panel estimate if the preconditions and changes 1–3 and 5 land:** merged ≈ 7.2. With #2's clinician and #4's real workforce feed both landing: ≈ 7.5–7.6, inside the plausible top-3 band.

---

## Sources (web, read 9 Nov 2026)
- Future Health Digital Innovation Challenge 2026 launch (focus areas, prizes, co-creators): https://intlbm.com/2026/10/15/future-health-unveils-global-challenge-to-boost-health-innovation/
- Future Health Challenge (MIT Solve edition) winners and traction: https://pulse2.com/future-health-challenge-awards-300000-for-early-detection-and-population-health-sensing-solutions/
- Earlier edition scope (prototype minimum; forecasting, surveillance, decision support): https://www.khaleejtimes.com/lifestyle/health/abu-dhabi-future-health-challenge-healthcare-systems-technology-300000-prize
- DoH–Microsoft Population Health Intelligence platform: https://www.mediaoffice.abudhabi/en/health/department-of-health-abu-dhabi-unveils-worlds-1st-ai-powered-population-health-intelligence-platform-at-gitex-global-2025/
- 2026/27 UAE respiratory campaign; DoH quote on the season: https://www.khaleejtimes.com/lifestyle/health/flu-campaign-2026-27-expanded-changes-explained
- INFLAenza hierarchical model (FluSight 2023/24 rank): https://www.medrxiv.org/content/10.1101/2025.03.03.25323259.full.pdf
- Time-series foundation models for epidemic forecasting: https://arxiv.org/pdf/2606.19560
- Could not be read: the Zawya and WAM launch and winners pages (robots or empty content).
