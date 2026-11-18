# NABD: Judge Panel Review, Round 3 (8 Nov 2026)

> **What this file is.** A simulated review written by an AI assistant in a separate session, asked to act as a panel of challenge judges (public health, AI, partnerships). No human reviewer, government official or company employee wrote, saw or endorsed it. It is kept because the fixes it prompted are traceable in `docs/DEVIATIONS.md`.

**Panel.** J1 is a senior public-health official (DoH/ADPHC). J2 is a principal AI/ML scientist (Microsoft/G42/MBZUAI). J3 is a partnerships and venture lead (PureHealth/M42). Each judge scored independently; the scores were then merged. None of us built NABD. Round 2 (docs/REVIEW-R2-judges.md) scored an earlier version at about 5.3/10.

**Inspected.**
- pitch/: registration.md, one-pager.md, deck-script.md, demo-script.md, video-script.md, qa.md
- research/: positioning.md, burden.md, tc.md
- docs/: TECHNICAL.md, PILOT-DATA-SPEC.md, RUNBOOK.md, PREREG-GCC.md
- results/: SUMMARY.md, gcc/SUMMARY.md, uae/SUMMARY.md, uae/SUMMARY-v2.md
- figures: fig2_league_table.png, uae_v2_overview.png, gcc_v1_vs_persistence.png
- app/screenshots/01–11 (all 11 viewed)
- ledger/ (files and SCOREBOARD), playbook/playbook.yaml, data/raw/flunet_gcc.csv and flunet_are.csv (date ranges)
- `pytest --collect-only` (120 tests collected)

---

## 0. What changed since round 2, and what we found that the team's documents don't say

### Fixed since R2 (credit given)
| R2 finding | Status now |
|---|---|
| Claims not backed by code (fusion, ACI, attributions, the CDC's 21–36%) | **Fixed.** A binding stop list (positioning §4.6) is followed in the registration, deck, video and Q&A. The About page lists what NABD does *not* claim. |
| Card recommended a surge roster on a falling forecast | **Fixed.** Bands now come from exceedance probability × forecast path, and a consistency gate (`cardcheck.py`) blocks contradictory cards. Screenshot 01 shows `rsv_elevated_falling` → "Step down: no surge roster needed". |
| "Drivers are not attributions" | **Fixed.** Exact additive per-term contributions of the linear model are shown on the card. |
| No external validation; UAE n = 4 | **Largely fixed.** The blind GCC test was pre-registered and locked before download. Primary **MET**: 0.914 (0.843–0.983). |
| NOT MET without context | **Fixed.** A pre-declared league table places NABD 7th of 21 single models (2024/25) and 19th of 25 (2025/26). |
| No real non-lab signal in a scored model | **Partly fixed.** v2 (non-sentinel, testing volume, school breaks, Ramadan) was built and scored under a lock. It did not help (1.059), and that is reported. |
| UAE alert metrics, missing-feed behaviour, latency | **Fixed** (diagnostic labels throughout). |
| No Abu Dhabi value or pilot path | **Partly fixed.** There is now a season-shape panel, a bed-days SCENARIO page, and a pilot data spec with k = 10 complementary suppression, an ADHICS checklist and pre-set exit criteria. |

### Still open from R2
- **Nothing is public or anchored yet:** no pushed repo, no OpenTimestamps/Zenodo receipt, no FluSight PR.
- No letter of interest (LOI) and no clinician review of the playbook (`reviewed: false`).
- The workforce module is still SIMULATED and "feeds no forecast".
- There is no hosted demo URL. The screenshots show Streamlit's local "Deploy" chrome, and Docker has never been built.

### New findings (ranked by how much they would cost on the day)

1. **The headline comparator doesn't match the problem statement.**
   - The problem the team sells is: "Plan this winter from last winter's calendar and you're wrong" (deck slide 2, demo 0:00, positioning §1.1).
   - The baseline that encodes "last winter's calendar" is the **seasonal analog**. Against it, the blind Gulf test gives **0.536 for flu (−46%) and 0.685 for RSV (−31%)**, both pre-registered secondaries with CIs well below 1.
   - The pitch instead headlines the 9% gain over *persistence*, a different (and harder-to-explain) baseline.
   - This is the cheapest, largest improvement available, and it isn't spin: the analog comparison was declared in PREREG-GCC §5–6 before download.
2. **The UAE "parity" result has a structural explanation the team never states.**
   - UAE sentinel data in FluNet start in **2022** (`flunet_are.csv`: sentinel 2022–2026, non-sentinel 2023–2026). So the first forward-in-time UAE fold (2023/24) was trained on **one season**, and it is the fold that loses badly: flu WIS 4.75 vs persistence 2.21.
   - In the two folds with ≥2 training seasons, v1 beats persistence on flu in both: 2.54 vs 2.66 and 1.94 vs 3.08. RSV is split: it wins 2024/25 (1.32 vs 2.14) and loses 2025/26 (2.30 vs 1.89).
   - The GCC countries had training history back to 2015.
   - The coherent story: "the method needs a few seasons of history; with it, it won blind in three Gulf countries; the UAE now has four seasons, and the ledger tests it live." This must be labelled *post hoc*. It is still the honest answer to J2's sharpest question, and it isn't in qa.md.
3. **The ledger is one forecast issued twice.**
   - R0 (06:51Z) and R1 (12:12Z) have byte-identical v1 and persistence hashes (`2691894e…`, `6347b067…`; screenshot 06), with data through W44 in both.
   - The sidebar's "5 hashed round file(s)" overstates it. J2 will read this as padding.
   - Say "1 forecast round (W44 data), re-issued with the v2 challenger; 0 weeks scored".
4. **The league-table figure contradicts the spoken number.**
   - fig2's titles say "**rank 13 of 41**" and "**rank 40 of 46**". The deck and video say "7th of 21" and "19th of 25".
   - Both are true (all models vs single models only). But a judge who reads "40 of 46" on the slide while hearing "19 of 25" will assume spin.
   - Pick one denominator for the slide title and put the other in the caption.
5. **The Arabic card is about half English.** Screenshot 02 has these in English:
   - the explanation bullets ("pushed the forecast down…");
   - the playbook band line;
   - the issue/model/hash line;
   - the horizon selector;
   - the chart captions;
   - the column headers "week end" and "+0.5 wk";
   - the exceedance caption.

   A DoH judge who toggles Arabic will notice within seconds. "Bilingual" is one of the pitch claims.
6. **The "Why this forecast" chart shows 3 bars but only 2 labels** (screenshot 01). One explanation also reads as a contradiction: "Change over the last published week pushed the forecast **up**" while the week **fell** from 15.6% to 10.5%. That is mean-reversion via the anomaly and momentum coefficients, and it needs a one-line plain-language gloss or it looks like a bug.
7. **The bed-days scenario prices the pain small, and in the wrong currency.**
   - It shows 26–121 bed-days and US$14.7k–68k per week for a Tawam-sized hospital.
   - For J3 that is not a business, and the 4.6× range shows the forecast is too wide to staff from.
   - It needs AED, a "share of a ward" framing, and above all a *decision* comparison (see §5, change 7).
8. **Workforce, half of the statement title, is still disconnected.** The page itself says "feeds no forecast", and qa.md has **no** workforce question at all.
9. **Statement-06 language drift.** The registration says "up to three weeks ahead"; the card says +2.5 weeks after issue. This is a minor inconsistency, but J2 will check it.
10. **The Alerts page undersells a UAE number.** v1 caught 3/3 UAE flu onsets with a median lead of **+1.4 weeks**, but the census rule had the same lead (1.43), so this is parity, not an advantage. The "median lead about 0 weeks" headline is US-only. State both explicitly, so nobody thinks the UAE result was hidden or inflated.

---

## 1. Scores by role (1–10)

### J1: Senior public-health official, DoH/ADPHC
| Axis | Score | R2 | One-line reason |
|---|---|---|---|
| Impact | 6 | 5 | Season-shape panel makes UAE variability undeniable in 5 seconds. Still national sentinel positivity, with no emirate, district or load figure and no lead time. |
| Technical depth / novelty | 6 | 5 | The pre-registered blind Gulf transfer is unusual and relevant to the Gulf CDC agenda. The model is still a 5-term regression. |
| Working demo & evidence | 7 | 4 | The card is coherent (exceedance, direction and action agree), the named-approver flow works and the evidence is in order. Arabic is half-translated and there is no hosted URL. |
| Responsible AI | 8 | 8 | Aggregate only, k = 10 complementary suppression, an ADHICS and DoH AI-policy checklist, and a hash-chained audit. The playbook is still unreviewed, with no RBAC view and no "no employment/disciplinary use" line in the app. |
| Scalability / deployment | 7 | 6 | The pilot data spec maps onto what Tableegh/Malaffi already hold, and FluNet-native transfer is measured. There is no hosting or ADPHC integration path beyond CSV export. |
| Commercial / pilot | 5 | 5 | The shadow-pilot design is exemplary. Nobody in Abu Dhabi has agreed to it. |

**J1 verdict.** I could now hand this card to a duty officer without embarrassment, which I couldn't in R2. But I still can't name the Abu Dhabi colleague who has looked at it. And the workforce half of my statement is a watermark. **Finalist, not winner.**

### J2: Principal AI/ML scientist, Microsoft/G42/MBZUAI
| Axis | Score | R2 | One-line reason |
|---|---|---|---|
| Impact | 5 | 5 | Forward-in-time parity on the target country is still the product's weak point. 9% over persistence is modest. |
| Technical depth / novelty | 5 | 4 | The evaluation infrastructure is ~8/10: locks, `assert_locked`, scorer cross-check, leakage tests that fire. The modelling is ~3/10: v2's extra signals hurt and there is no foundation model. |
| Working demo & evidence | 7 | 6 | The blind GCC test with a mechanical inclusion rule and losses shown is the most credible evidence in the folder. It is undercut by self-attested locks and a ledger that is one forecast issued twice. |
| Responsible AI | 8 | 7 | Claims now match code, which is the R2 fix that mattered most. |
| Scalability / deployment | 7 | 6 | The method transferred to three countries without tuning. Deterministic, 120 tests, FastAPI. |
| Commercial / pilot | 4 | 4 | Still untested on any count series of hospital scale (the US track is state-level). |

**J2 verdict.** This is the best-evaluated entry I'll read. It is not the best model. If the repo and anchors are public before I score it, I'd move evidence to 8. If they aren't, "pre-registered" is the team's word against my prior. **Finalist.**

### J3: Partnerships / venture lead, PureHealth/M42
| Axis | Score | R2 | One-line reason |
|---|---|---|---|
| Impact | 5 | 5 | The bed-days page prices the pain at about US$15–68k a week per hospital. That isn't a reason to buy, and it isn't in AED. |
| Technical depth / novelty | 5 | 5 | The defensible asset is the dated track record, and today it is one unscored round. |
| Working demo & evidence | 6 | 5 | Polished and coherent. "The CDC beat you" is now answered with a league table. |
| Responsible AI | 7 | 7 | Governance a PureHealth compliance team could adopt as-is. |
| Scalability / deployment | 6 | 6 | A Gulf roll-out is plausible. There is no EHR/HIS integration story beyond aggregate CSV, and the 72-hour command-centre tools own the ops seat. |
| Commercial / pilot | 3 | 3 | No LOI, no named champion, no price, a WHO non-commercial dependency and a 6-month organiser right of first refusal (ROFR). Nothing changed here. |

**J3 verdict.** The deck still ends in an ask with nobody on the other side of it. One letter from a Tawam or SKMC paediatrician would move me +2 on commercial and +1 on impact. **Neither top-3 nor a strong finalist from my seat.**

### Merged
| Axis | J1 | J2 | J3 | Mean | R2 mean |
|---|---|---|---|---|---|
| Impact | 6 | 5 | 5 | 5.3 | 5.0 |
| Technical depth / novelty | 6 | 5 | 5 | 5.3 | 4.7 |
| Working demo & evidence | 7 | 7 | 6 | 6.7 | 5.0 |
| Responsible AI | 8 | 8 | 7 | 7.7 | 7.3 |
| Scalability / deployment | 7 | 7 | 6 | 6.7 | 6.0 |
| Commercial / pilot | 5 | 4 | 3 | 4.0 | 4.0 |
| **Overall** | 6.5 | 6.0 | 5.3 | **≈ 5.9** | ≈ 5.3 |

**Verdict: a likely finalist or shortlist entry (top ~5–8% of about 400), but not a likely top 3 as it stands.**

- **Why finalist:**
  - It has a real working prototype on real data.
  - Its pre-registered blind test was passed.
  - Its responsible-AI design is unusually complete.
  - It discloses failures with a discipline that most simulated-dashboard entries can't match.
- **Why not top 3:** the organisers' order is "Impact first. Then proof that it works." NABD still leads with proof.
  - Impact is the lowest-scoring axis after commercial.
  - There is no Abu Dhabi partner.
  - The comparator in the headline doesn't match the pain.
  - The statement's workforce half is simulated.
  - The verifiability that the whole story rests on (public repo, anchors, scored ledger weeks) isn't in place yet.
- **The path to the top 3 is concrete:** changes 1–6 in §5. If they land, especially the partner letter, the panel's estimate is **6.8–7.2**. That is a genuine top-3 contender, at roughly 25–35% from here vs about 10% now.

---

## 2. The pain point and the problem statement

### Is it compelling, and is it specific to Abu Dhabi?
**Partly.**
- **What works:**
  - The variability is real, it comes from the UAE's own WHO data, and it is shown visually (season-shape panel): flu peaked in Oct 2025 vs Feb 2025, and the RSV peak ranged from week 41 to week 47.
  - The Tawam figure (2,189 RSV admissions of children ≤5) is Abu Dhabi emirate data.
  - The RSV-before-1-September fact (2 of 4 seasons) is sharp and local.
- **What doesn't:**
  1. FluNet UAE is **national** surveillance, not Abu Dhabi.
  2. The Tawam data are 2018–22 and straddle COVID.
  3. DoH itself says this season is normal.
  4. "Nobody publishes a forecast" describes a missing product, not harm. A DoH judge will ask "so what goes wrong today?"
  5. The decision-maker is implied, not named.
  6. The comparator mismatch (finding 1).

### Is the problem statement right?
It names the right phenomenon (season-shape variability) but frames the gap as supply ("no forecast") rather than a decision that goes wrong. It also omits the planner's actual default, "last year's calendar", which is precisely what NABD beats by 31–46% blind.

### Rewrite (40 words, for registration and slide 2)
> **Every winter Monday, Abu Dhabi's paediatric bed managers and public-health officers commit capacity for the next three weeks using last year's calendar. But UAE seasons don't repeat: flu peaked in October one year, February the year before. Nobody gives them a checkable range.**

### Rewrite (spoken, about 20 seconds)
> "Every Monday from September to March, a bed manager at a SEHA hospital and a duty officer at ADPHC decide how much winter to prepare for. Their tools are last week's numbers and last year's calendar. In the UAE, both mislead. Flu peaked in October 2025 and in February the season before. RSV's peak has moved six weeks. One Abu Dhabi hospital admitted 2,189 young children with RSV in five years. Nobody gives these people a calibrated, checkable range for the next three weeks. NABD does."

Then the evidence line that closes the loop:

> "Tested blind on three Gulf countries, it cut error by 46% for flu against planning from past seasons, and beat last-week carry-forward too."

---

## 3. The evidence story

### Is the current order persuasive or confusing?
**Persuasive in parts; confusing as a sequence.** The current order is Gulf → ledger → US → UAE parity.

- **Ledger as #2** is a promise ("0 scored rounds"), sandwiched between two pieces of evidence. It deflates momentum.
- **UAE parity as #4** ends the evidence section on the weakest result, with no explanation.
- **The headline numbers are relative WIS vs persistence (0.914)**, which needs two sentences of explanation and doesn't map to the stated pain.
- **Three different baselines appear in 90 seconds:** persistence, the CDC ensemble and "the baseline". Judges lose the thread.

### Recommended exact order (deck slides 5–8; demo 1:10–2:45)
1. **Blind Gulf test, framed against the pain.**
   - "Against planning from past seasons: −46% flu, −31% RSV."
   - "Against last-week carry-forward: −9% flu (pre-registered primary, MET), −20% RSV."
   - Show the losses.
   - Label: pre-registered primary and secondary, retrospective revised data.
2. **CDC benchmark: calibration of trust.**
   - "We put the same discipline against the world's hardest public bar. We missed our margin (1.22), and here is where we sit among the CDC's own models: 7th of 21 in 2024/25, at baseline in 2025/26."
   - One slide, one figure, one consistent denominator.
3. **The UAE's own record: the honest caveat, with its explanation.**
   - "On the UAE's own data we tie, because UAE sentinel data only start in 2022. The fold trained on one season lost; with ≥2 seasons of history it won flu in both folds and split RSV." (Post hoc; say so.)
   - "That's why the next item exists."
4. **Live ledger, merged into the pilot ask as the forward-looking close.**
   - "Every forecast is hashed and anchored before WHO publishes. Here are the first N weeks scored ⟨on the day⟩."
   - "Give us one hospital and the ledger runs on your census."

### The 3 numbers a judge should remember
1. **2,189**: RSV admissions of children ≤5 at one Abu Dhabi hospital in five years (the pain).
2. **46%**: less forecast error than planning from past seasons, in a blind, pre-registered test on three Gulf countries. Pair it verbally with "and it beat last-week carry-forward too, 0.91, CI below 1", so J2 hears the primary endpoint.
3. **7th of 21**: NABD v1's rank among the CDC FluSight hub's single models in 2024/25. Say "after missing our own CDC bar" in the same sentence; that is where the honesty premium is banked.

**Drop from spoken numbers:** 1.22 (show it on the slide in red, say "missed", don't say the number), 1.002, 1.059, PPV decimals, 11,660, the CI bounds beyond the one above.

---

## 4. Gaps against the official Statement 06 requirements (research/tc.md)

| # | Requirement | Status now | Gap | Severity |
|---|---|---|---|---|
| 1 | Multi-signal surveillance (≥2 materially different signal types) | v2 combines lab (sentinel and non-sentinel), testing volume and an administrative calendar (school, Ramadan). It was scored and did not help. The card's model, v1, is lab-only. | The calendar is arguably "community/administrative", but no environmental or workplace signal is scored. The deployed model is single-source by design. Defensible only if pitched as "we tested fusion; it didn't help; we ship what works". Weather is still not retrieved even though `adapters/weather.py --fetch` works on a laptop. | **MAJOR** |
| 2 | Explainable anomaly detection (signals, locations, time periods) | Exact per-term contributions, including the deviation-from-seasonal-baseline term, with week windows | No **location** dimension (national only). The anomaly isn't presented as a detection ("this week is X above the usual for week 44"). Chart label bug and the counterintuitive sign. | **MINOR** (signals and time) / **MAJOR** (locations; mitigated by the organisers' own geolocation caveat and the pilot spec's region field) |
| 3 | Actionable decision support (proportionate action, named role, evidence, assumptions) | Exceedance-driven bands, two named roles, reason codes, consistency gate, rules shown on the About page | Playbook `reviewed: false` and thresholds are placeholders. Assumptions are on the About page, not on the card. Only two roles; nothing for employers, schools or the immunisation programme. | **MAJOR** (a single clinician or public-health review flips this to MINOR) |
| 4 | Privacy-preserving views (aggregation, small-cell suppression, RBAC, no employment/disciplinary use) | Aggregate only; person-level fields rejected (tested); k = 10 plus complementary suppression in the pilot spec and the workforce module | No RBAC demo (duty-officer vs bed-manager view). The "no individual employment/disciplinary use" statement is not in the app or the playbook. | **MINOR** |
| 5 | Operational validation (lead, sensitivity, PPV, false alarms, latency, missing inputs) | All reported for the US and UAE, labelled diagnostic | Content is complete. The pitch should state the UAE flu lead (+1.4 wk, equal to census) next to the US 0. | **MINOR** |
| 6 | Health and resilience impact (earlier intervention, fewer severe incidents, **reduced sickness absence and lost workdays**) | Bed-days SCENARIO (crude, in US$) | No decision-value demonstration. Absence and lost workdays are entirely simulated and disconnected from the forecast. | **MAJOR** |
| Core | "Early enough to change action" | Median onset lead 0 (US); UAE flu +1.4 wk equals census | Horizons reach +2.5 weeks of *magnitude*, which is lead time on size, not onset. The pitch doesn't say this. | **MAJOR** (framing fixable) |
| Core | "Specific enough to be useful" | National, with a +1-week 80% band of 4.6–21.4% | Exceedance probabilities help, but the band is still 4.6× wide. No emirate or facility view without a partner. | **MAJOR** |
| Core | "Calibrated to avoid alert fatigue" | 95% coverage US 0.92 / GCC flu 0.96; 0 false alarms in UAE flu; US PPV 0.65/0.76 | GCC RSV coverage is 0.83 (too narrow), and that is disclosed. | Strength |
| Title | "Population **and Workforce**" | Workforce SIMULATED; "feeds no forecast" | Half the statement title has no connection to the product, and qa.md has no answer for it. | **MAJOR** |
| Submission | Working prototype judged directly | Local Streamlit only; Docker never built | **If judges can't open it, it isn't judged as working.** | **CRITICAL** |
| Submission | Declared data, assumptions and limitations | Done (registration table, TECHNICAL §10, assumptions-limitations.md) | Team names and contact are still placeholders; MBZUAI permission is unconfirmed. | **CRITICAL** until filled (registration closes 10 Nov) |
| Integrity | "Pre-registered", "public ledger" | Self-attested local git | Repo not pushed; no anchors; no FluSight PR. The whole evidence story rests on verifiability. | **CRITICAL** |

---

## 5. What to build or change in the remaining ~11 days, ranked by expected score gain ÷ effort

Gains are panel estimates on the merged 1–10 scale.

### 1. Re-anchor the headline to the pain (pitch, 2 h, by 10 Nov)
**Gain +0.3 to +0.4 merged (impact, evidence).**
- **Registration abstracts:** replace "cut forecast error against last-week persistence by 9% … 20%" with "cut forecast error by 46% (flu) and 31% (RSV) against planning from past seasons, and beat last-week carry-forward (pre-registered primary met)". Re-run `pitch/wordcount.py`.
- **Adopt the §2 problem statement**, and name the two roles in the first sentence.
- **Slide 5:** a two-bar visual per virus (vs past seasons, vs last week), both labelled pre-registered.
- **Fix the league-figure title:** "7th of 21 single models (13th of 41 incl. ensembles)", and "19th of 25 (40th of 46)".
- **Ledger wording:** "1 forecast round (data through W44), re-issued with the v2 challenger".
- **Horizon wording:** "up to +2.5 weeks after issue" everywhere.
- **Guard:** analog numbers must carry "pre-registered secondary". Never call them the primary.

### 2. Make it verifiable and clickable (data + app, 1 day, by 11 Nov)
**Gain +0.4 merged (J2 evidence +1, J1 demo +0.5). This is CRITICAL-gap removal.**
- Push the repo publicly with full history, under an Apache-2.0 or MIT licence (compatible with the ROFR because the licence is non-exclusive).
- Run `anchor.sh` on four manifests: the US freeze, the UAE-v2 lock, the GCC lock and ledger R1. Commit the `.ots` files. Then post the Merkle roots to a Zenodo DOI. **Describe every anchor as made after the results existed** (FREEZE addendum).
- Deploy the app to a public host (Streamlit Community Cloud or a HF Space) with cached data, and put the URL in the registration, the one-pager and the video description.
- Submit the FluSight hub PR for reference date 14 Nov (due Wed 11 Nov, 23:00 ET), with `designated_model: false`. Fill the placeholders in `results/flusight_draft/NABD-v1.yml`.
- Issue ledger R2 as soon as WHO publishes W45, and anchor it the same day. On 19 Nov, re-issue and score; show "N realised weeks, M inside 80% band" whatever they are.

### 3. One Abu Dhabi clinical partner letter, plus a playbook review (pitch / team lead, start 9 Nov, land by 17 Nov)
**Gain +0.5 to +0.7 merged (J3 commercial +2, J1 commercial and decision support +1). It is the single largest lever, but it is uncertain.**
- **Targets, in order:**
  1. The authors of the Tawam/UAEU RSV study (the team's own burden anchor; last-listed author Alsuwaidi A.R.; check who the corresponding author is before writing). They have a published interest in exactly this seasonality.
  2. SKMC or SSMC paediatrics.
  3. CCAD.
  4. MBZUAI's existing health partners via faculty.

  Use `pitch/outreach.md`.
- **The letter (one paragraph, non-binding):**
  - interest in a 12-week shadow evaluation after the Challenge;
  - weekly aggregate counts per `docs/PILOT-DATA-SPEC.md`;
  - no change to care;
  - a named clinical reviewer.
- **Separately, ask one paediatrician or public-health physician** to review `playbook.yaml` (30 minutes). Record `reviewed_by` and the date. Change "ILLUSTRATIVE" to "reviewed by ⟨role⟩, pending pilot".
- **Fallback if no letter:** a quoted email from any Abu Dhabi clinician confirming the Monday decision exists, with permission to quote. Never imply an endorsement that wasn't given.

### 4. Weekly bilingual bulletin, generated from each ledger round (app, 1 day, by 15 Nov)
**Gain +0.3 merged (J1 impact and demo; tangible).**
- `python -m app.bulletin --round Rn` writes a one-page PDF, Arabic and English side by side. Model it on WHO EMRO/ECDC ERVISS weekly summaries. Do **not** call it "ADPHC format": we haven't seen theirs.
- **Header:** epi week, issue date, data through, WHO lag, ledger round hash and anchor status.
- **Two tiles (RSV, flu):**
  - last value and 3-week trend;
  - median and 80% range at +0.5/+1.5/+2.5 wk;
  - P(> tier thresholds);
  - a direction word ("falling / uncertain / rising").
- **Context:** a sparkline of this season vs the last 4, with the onset and peak weeks of prior seasons.
- **Action per role,** with the approver name, decision, reason code and audit hash. If not yet approved, show "PROPOSED, NOT APPROVED".
- **Track record:** the last N scored weeks, coverage, and relative WIS vs both baselines.
- **Footer:** limitations (national sentinel positivity ≠ admissions; playbook status) and the "no individual or employment use" line.
- The demo shows the PDF landing; the video gets a 3-second shot.

### 5. Hospital-ops view that joins demand and the hospital's own workforce (app + pitch, 1 day, by 16 Nov)
**Gain +0.3 merged (it answers the "workforce" half, req 6, and J3's "what would I do Monday").**
- **One page, "Hospital winter planner (SCENARIO)":**
  - **Inputs (editable, defaults labelled illustrative):**
    - annual paediatric RSV admissions;
    - LOS;
    - paediatric respiratory beds;
    - nursing headcount;
    - baseline winter respiratory sickness-absence rate. The default is a placeholder "set by partner HR", with **no invented UAE figure**.
  - **Outputs per horizon:**
    - scenario bed-days generated (the current arithmetic);
    - **% of ward capacity**;
    - scenario staff-absence range, scaled by the same positivity forecast;
    - a **net roster gap** band;
    - P(gap > 0).
  - Show it in **AED** (state the conversion rate used).
- **Playbook:** add an `occupational_health` role (employer and hospital HR) with tiered actions: vaccination push, sick-leave flexibility reminder, post-school-break cover planning (14 Dec – 3 Jan break per [S8]). Bilingual.
- **Link the secret-shared workforce aggregation** as the *pilot data path* for real absence counts, so the simulated page explains how the forecast's workforce input would become real.
- **Labels:** SCENARIO / SIMULATED on every number. No absence statistic is cited as fact.
- **Is this enough for "workforce"?** For a top-3 entry, yes, provided it is framed as "population forecast → workforce consequence" and not as a second product. A real employer-absence model isn't achievable or verifiable in 11 days. Don't try.

### 6. Demo polish that removes visible defects (app, half a day, by 14 Nov)
**Gain +0.2 merged.**
- Full Arabic coverage of the card: explanations, band line, captions, table headers, horizon labels.
- Fix the explanation chart labels (3 bars, 3 labels).
- Add a one-line gloss for mean reversion ("RSV is above its usual level for this week, so the model expects it to drift back").
- Rename the GCC table rows to human labels.
- State the US 0-week and UAE +1.4-week leads together on the Alerts page.
- Add an RBAC toggle: a duty-officer view (no hospital scenario) vs a bed-manager view.
- Add the "no individual or employment use" line to the card footer.
- Hide the "Deploy" chrome.
- Fix the deck's `09_about.png` reference (the file is `11_about.png`).

### 7. Decision-value back-test on the GCC seasons: "what would planning with NABD have cost vs last year's calendar?" (modelling, 4–6 h, by 15 Nov)
**Gain +0.2 to +0.3 (impact for J1 and J3). Medium risk.**
- **Declare the method in DEVIATIONS before computing:**
  - On the GCC forward-in-time forecasts already scored, the decision is "open surge capacity in week t+2 if P(> threshold) ≥ p".
  - Compare NABD exceedance vs analog vs persistence on hits, misses and false openings at matched thresholds, and on relative economic value across cost/loss ratios. The US version of this already exists (REV).
- Report it as a pre-declared exploratory analysis. If NABD loses, report that too.
- This turns "46% less error" into "fewer wasted surge weeks".

### 8. Explain UAE parity with a pre-declared training-history analysis (modelling, 2–3 h, by 13 Nov)
**Gain +0.1 to +0.2 (it de-risks J2's hardest question).**
- Declare it in DEVIATIONS first. Then, for GCC country-seasons, plot relative WIS vs the number of training seasons, and place the UAE folds on the same axes.
- If the dose-response holds, Q&A answer 6 has a principled basis. If it doesn't, drop the explanation and say so.

### 9. Optional, only if 1–6 are done
- **Weather (NOAA GHCN, Abu Dhabi) as a pre-registered v3 challenger** in the ledger (no retrospective claim). It is the only environmental signal that would answer req 1 literally. Gain is small, and it is low priority given v2's null result.
- **Chronos-2 zero-shot** on the GCC series as a declared exploratory comparison. It answers "where's the AI?", but only if it runs without fuss on a laptop.

### Don't spend time on
- More US work, a US v2, re-tuning v1, or recalibrating GCC RSV intervals post hoc.
- Polishing the secret-sharing demo.
- A third language.
- Any "early warning of onset" framing.

---

## 6. The 10 hardest live Q&A questions, and whether pitch/qa.md answers them

| # | Question | qa.md coverage | Verdict and fix |
|---|---|---|---|
| 1 | "Your product ties with 'next week = this week' on the UAE, the one place you want to deploy. Why should Abu Dhabi use it?" | #6, #8 | **Weak.** It concedes without explaining. Add the training-history fact (UAE sentinel data start 2022; the one-season fold lost; flu won both later folds while RSV split, post hoc). Then the blind Gulf result, then the ledger. |
| 2 | "Persistence is a straw man. Planners use last year's pattern. How do you do against that?" | Number buried in #1 | **Missing as a framed answer.** Answer: "Against past-season planning: −46% flu, −31% RSV, blind and pre-registered." It should be the headline (§3). |
| 3 | "The band is 4.6–21.4%. What does my bed manager actually do differently on Monday?" | Not answered | **Missing.** Walk through the card: P(> 10%) = 51% at +0.5 wk, falling path → "no surge roster; plan stand-down if confirmed next week". The value is not over-staffing into a declining wave. Add a 2-sentence worked example. |
| 4 | "Statement 06 is *early warning*. Lead time is zero. Isn't this the wrong statement?" | #17 | **Partial.** Honest, but with no positive reframe. Add: "Our lead is on *size*, up to +2.5 weeks, not onset. In UAE flu we caught 3 of 3 onsets 1.4 weeks ahead, the same as a threshold rule, with zero false alarms. Onset is already covered by Tableegh and UMOC; magnitude isn't." |
| 5 | "Who in Abu Dhabi has looked at this? Has any clinician reviewed the playbook?" | #27 ("no LOI yet") | **Weak**, and it can only be fixed by doing change 3. |
| 6 | "Half the statement is *workforce*. Where is it?" | **Not in qa.md** | **Missing.** Answer after change 5: "We forecast the population wave and translate it into the hospital's own two constraints, beds and staff. The employer-absence feed is designed (secure aggregation, k ≥ 10) and simulated; we don't fake absence data that doesn't exist publicly in the UAE." |
| 7 | "National sentinel positivity isn't hospital load. What evidence links the two?" | #9 | **Partial.** Add: "Our US track runs on hospital *admissions* (NHSN), with the same discipline. The 12-week pilot's secondary endpoint tests exactly this link on the hospital's census, with the exit criterion set now." |
| 8 | "Your 'pre-registration' is a local git commit you made yourselves. Why believe the Gulf test was blind?" | #4 and a curveball | **Partial.** It is honest today. After change 2 the answer is: "Anchored ⟨date⟩ (after results, disclosed); the GCC lock commit precedes the data commit by 90 s; the FluSight PR is CDC-timestamped; the ledger rounds were anchored before WHO published." |
| 9 | "Your multi-signal model got *worse*. Doesn't that fail requirement 1?" | #7 | **Partial.** It is factual but defensive. Add the framing: "We tested fusion under a lock and it didn't help on four seasons. Shipping it anyway would be the irresponsible choice. It runs in the ledger as a challenger, and Rasid's wastewater signal is the next input to test, published either way." |
| 10 | "Who pays, how much, and how do WHO's non-commercial terms and the organiser's right of first refusal not kill this?" | #26, #27 | **Weak.** There is no price. Add a pricing hypothesis: a public-health feed licence per country per season, and a hospital-ops seat per facility, with an order-of-magnitude figure stated as a hypothesis. Add the ROFR line from tc.md: "non-exclusive open licence; any exclusive deal goes to the organiser first until about June 2027". |

**Also expect:**
- "Why not the Gulf CDC or WHO EMRO?" (#24 is partial; add "complementary, FluNet-native, transferable").
- "Data sovereignty?" (PILOT-DATA-SPEC §4 covers ADHICS and in-country hosting, but it isn't in qa.md; add a 3-line answer).
- "What's the MBZUAI-level novelty?" (#22 is honest but thin; the answer is "transfer under pre-registration plus a public, anchored scoring ledger", not the model).

**Overall Q&A grade:** strong on integrity questions (#4, #10–16, #20). Weak on the questions an Abu Dhabi official or buyer asks first: what to do Monday, who has seen it, workforce, and who pays. With 3 minutes of Q&A, those questions come first.
