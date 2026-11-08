# NABD: 10-slide deck script (round 3, BUILD-SPEC v1.6 evidence order)

**Rules:**
- Every number traces to `results/`, `data/raw/` or `research/` (G9). See `research/claims-ledger.md`; a claim that isn't in the ledger can't go on a slide.
- `research/positioning.md` §4.6 (the stop list) is binding.
- ⟦IF BUILT: file⟧ marks a round-3 output still in build. If the file is missing on 19 Nov, **cut the line**; never estimate it.
- **Evidence order (v1.6):**
  1. the blind Gulf test;
  2. the public, anchored ledger;
  3. the US CDC benchmark and league placement;
  4. the UAE's own record is at parity, which is why the ledger exists.

**Headline (slide 1 and the video's last line):**
> **No two UAE respiratory seasons share a shape, and nobody publishes a forecast. NABD is an open RSV and flu forecasting hub for Abu Dhabi, tested blind across the Gulf and scored in public.**

---

### 1. Title
- **On slide:** NABD (نبض, "pulse"): an open RSV and flu forecasting hub for Abu Dhabi, tested blind across the Gulf. Statement 06 · ⟨team⟩ · MBZUAI.
- **Visual:** a pulse line turning into a forecast fan.
- **Notes (≈35 words):** "Every winter RSV and flu fill Abu Dhabi's children's beds. The seasons never repeat, and nobody publishes a forecast. NABD is that forecast, and every call it makes is on a public record."

### 2. The problem: same viruses, a different winter every year
- **On slide** (WHO FluNet UAE sentinel, our computation, `research/positioning.md` §1.1):

| Season | Flu peak | RSV peak | First week RSV ≥10% |
|---|---|---|---|
| 2022/23 | 35.6%, wk 45 | 20.4%, wk 42 | wk 35 |
| 2023/24 | 27.3%, wk 45 | 24.5%, wk 41 | wk 38 |
| 2024/25 | 28.0%, **wk 7 (Feb)**, 11 weeks ≥20% | **29.8%**, wk 41 | **wk 30** |
| 2025/26 | **40.6%, wk 42** | 23.1%, **wk 47** | wk 42 |

- **Callouts:**
  - Tawam Hospital (SEHA), Al Ain: **2,189** RSV admissions of children aged ≤5, 2018–22. Infants under 6 months stayed **5.8 days** on average.
  - Dubai: **22%** of under-2s with RSV were hospitalised, and **<2%** had a known risk factor.
  - "Exact data for flu cases in the UAE is not available" (The National, Jan 2026).
- **Visual:** the season-shape overlay (4 UAE seasons). Use ⟦IF BUILT: app season-shape panel screenshot⟧, else a static chart from `data/raw/flunet_are.csv`.
- **Notes:** "Flu spiked above forty per cent in October one year and plateaued for five months into February the year before. Plan this winter from last winter's calendar and you're wrong on timing and size. DoH says this season looks like the last two: normal, and still variable."
- **Sources:** `research/positioning.md` §1.1–1.3; `research/burden.md` items 1, 3, 6, 8.

### 3. The gap: Abu Dhabi senses well, but nobody forecasts the season
- **On slide:**
  - Tableegh (Malaffi-linked notifications), UMOC (AI early warning), Rasid (wastewater) and the DoH risk profile (chronic disease) all **detect**.
  - **Missing:** a calibrated, checkable answer to "how big will the next 1–3 weeks of RSV and flu be, and how sure are we?"
- **Visual:** a layer diagram, detect → **forecast** → operate, with NABD in the middle layer and "built to plug into them" written under it.
- **Notes:** "We aren't replacing what Abu Dhabi runs. We're the forecast layer between surveillance and the bed manager, and it consumes the same shape of data Tableegh already produces."
- **Sources:** `research/positioning.md` §0, §3; `research/competitors.md`.

### 4. NABD today: what runs
- **Solid strip (built):** WHO FluNet UAE → NABD-UAE-v1, a linear growth model on the logit of sentinel positivity with a seasonal term and testing volume → calibrated quantiles (nowcast, +0.5, +1.5, +2.5 weeks after issue) → bilingual Arabic/English card → playbook action for a named role → **Approve / Modify / Dismiss** with a reason → hash-chained audit → hashed ledger round.
- **Also built:**
  - exact per-signal "why this forecast" contributions (`results/uae/explain/`);
  - a feed-removal test (`results/uae/tables/ablation.csv`);
  - a multi-signal challenger, v2;
  - US and UAE alert metrics;
  - card consistency checks, so no contradictory card can render.
- **Outline strip, in build for 20 Nov:**
  - ⟦IF BUILT⟧ threshold-exceedance probabilities and a season-shape view on the card;
  - ⟦IF BUILT: docs/PILOT-DATA-SPEC.md⟧ an aggregate-data connector for a hospital pilot;
  - ⟦IF DONE: anchor receipt⟧ outside-timestamped ledger.
- **Grey:** the workforce module (SIMULATED).
- **Visual:** the architecture strip plus the card screenshot (`app/screenshots/01_weekly_card_en.png`).
- **Notes:** "Version one is deliberately simple and auditable. Everything solid on this slide runs today."

### 5. Proof I: tested blind on three Gulf countries (headline evidence)
- **Title:** *"We froze the method, locked the test, then opened data nobody on the team had seen."*
- **On slide:**
  - The plan (countries, inclusion rule, pass bar) was locked **before** any Oman, Qatar, Saudi, Bahrain or Kuwait data were downloaded. It ran forward in time: each season learns only from that country's earlier seasons (`docs/PREREG-GCC.md`).
  - **Influenza:** relative WIS vs "next week = this week" **0.914 (95% CI 0.843–0.983)**. Pre-set bar: upper bound < 1. **MET.** It won **9 of 12** country-seasons.
  - **RSV:** **0.798 (0.719–0.894)**, winning **9 of 10**. Against a seasonal-average forecast: 0.536 (flu), 0.685 (RSV).
  - **Losses, shown:** flu in Oman 2022/23 and 2024/25, a tie in Qatar 2023/24, and RSV in Saudi Arabia 2025/26. Bahrain and Kuwait were excluded by the pre-set rule (1 scorable season each).
  - **Small print, same size:** retrospective (revised WHO data) · n = 3 countries × ≈4 seasons · lock self-attested in local git ⟦IF DONE: "anchored ⟨date⟩"⟧ · RSV intervals too narrow outside the UAE (95% coverage 0.83).
- **Visual:** `results/gcc/gcc_v1_vs_persistence.png` and a country × season win grid.
- **Notes:** "This is the test we couldn't tune for. It beat what a planner would otherwise do by about nine per cent for flu and twenty for RSV, and we show every country, losses included."
- **Source:** `results/gcc/SUMMARY.md`.

### 6. Proof II: the public ledger, so you can check us every week
- **On slide:**
  - Every forecast round is hashed and published **before** WHO releases the answer. Round R0 was issued 8 Nov 06:51 UTC and R1 8 Nov 12:12 UTC (v1 headline, v2 challenger, persistence), with a Merkle manifest.
  - **Scored rounds as of 8 Nov: 0.** No target week has been published yet (`ledger/SCOREBOARD.md`). ⟦LIVE: scoreboard on the day⟧
  - Outside timestamp: ⟦IF DONE: OpenTimestamps/Zenodo receipt⟧, else "self-attested until anchored".
  - Every protocol lock and deviation is logged (`docs/FREEZE.md`, `docs/DEVIATIONS.md`).
- **Visual:** ledger receipt screenshot (`app/screenshots/06_ledger.png`).
- **Notes:** "A track record can't be backdated. It's the one thing a competitor can't copy, and it grows every Monday."

### 7. Proof III: stress test against the CDC, **NOT MET**
- **Title:** *"We set our bar at the CDC's best. NABD v1 missed it, and here is exactly where."*
- **On slide:**
  - Protocol frozen 8 Nov before any test score (`docs/FREEZE.md`, commit `ac16901`). Real-time data only. **11,660** forecasts across 53 US locations, two seasons and horizons 0–3.
  - Relative WIS vs the CDC FluSight ensemble **1.22 (95% CI 1.01–1.52)**. Bar: upper bound < 1.15. **NOT MET** (in red, by us).
  - **Among individual CDC-hub models**, scored the same way (method declared before computing):
    - **7th of 21 in 2024/25**: 0.693 vs baseline; the CDC ensemble scored 0.673;
    - **19th of 25 in 2025/26**: 0.997, level with the baseline.
  - By season vs the ensemble: 2024/25 **1.03**, 2025/26 **1.52**.
  - Excluding the national series still fails: 1.198.
- **Visual:** `results/figures/fig1_rel_wis_season_horizon.png` (red margin line at 1.15) and `results/figures/fig2_league_table.png`.
- **Notes (≈25 s):** "There's no UAE hub to compare against, so we went to the hardest public bar there is. In 2024/25 we sat seventh of twenty-one individual models. In 2025/26 we fell to the baseline. We froze this test, so we're showing you the season we lost."
- **Source:** `results/SUMMARY.md` (PRIMARY, S3, D6, D7).

### 8. What we learned, and what we don't claim
- **On slide:**
  - **The UAE's own record is at parity.** Trained only on earlier seasons, v1 vs persistence = **1.002** for flu and RSV. Four seasons is too short to learn UAE season shapes, which is why the Gulf test and the ledger matter (`results/uae/SUMMARY-v2.md`).
  - **More signals didn't help.** The multi-signal v2 (non-sentinel, school breaks, Ramadan, testing volume) was **worse than v1: 1.059** (CI 1.016–1.111), under a locked protocol. It stays a challenger and is never presented as an improvement.
  - **No early onset warning.** Median onset lead is **0 weeks** for every US rule, the CDC's included. We sell *how big and how long*, not *earlier*.
  - **Fewer false alarms (diagnostic).** US precision at 3/100k: NABD **0.65 / 0.76** vs CDC ensemble 0.41 / 0.67. UAE flu: 3/3 onsets caught, 0 false alarms, n = 3 onsets. Thresholds came from earlier probes, so these are diagnostic only.
  - **Missing data:** one missing week ×1.41 error (US). A missing non-sentinel week triggers an automatic fallback (UAE).
- **Visual:** `results/figures/fig3_wis_decomposition.png` (small) plus three icon rows.
- **Notes:** "We report what didn't work as plainly as what did. That's what lets a regulator trust the rest."
- **Sources:** `results/uae/SUMMARY-v2.md`, `results/uae/tables/alerts_uae.csv`, `results/tables/alerts_us.csv`, `results/tables/dropout_us.csv`.

### 9. Statement 06, requirement by requirement, and responsible by design
| Requirement | Status |
|---|---|
| Multi-signal | Built: lab positivity, testing volume, non-sentinel, school and Ramadan calendars (v2). Scored: it didn't beat v1 (reported) |
| Explainable detection | Built: exact per-signal contributions per forecast (`results/uae/explain/`) and feed removal (`ablation.csv`) |
| Decision support | Built: playbook action for a named role, approval with a reason code, card consistency checks. Playbook ILLUSTRATIVE pending clinical review |
| Privacy | Built: aggregate only; schemas reject person-level fields (tested); simulated k-anonymous workforce aggregation |
| Operational validation | Built: alert lead, sensitivity, PPV and false alarms (US + UAE, diagnostic); latency (US median input age 4 days; UAE lag 7 days); missing-feed behaviour |
| Health and resilience impact | Pilot hypothesis, not a result. ⟦IF BUILT: bed-days SCENARIO translator⟧ |

- **Also:** persistence is always shown next to the forecast (automation-bias guard); a freshness badge; WHO non-commercial terms respected.
- **Visual:** the checklist with built / scored / simulated / in-build tags, beside `app/screenshots/09_about.png`.
- **Notes:** "This is the organisers' own checklist. We mark where we're complete, where it's simulated, and where it didn't help."

### 10. Pilot, ask and 90 days
- **Pilot:** a 12-week shadow run on one hospital's aggregate paediatric/ED respiratory counts ⟦IF BUILT: per `docs/PILOT-DATA-SPEC.md`⟧. Exit criterion, set in advance: relative WIS < 0.9 vs the hospital's own census carried forward. No change to care.
- **Ask:** one hospital partner (SEHA/PureHealth or a private group) and an ADPHC data conversation.
- **90 days:**
  - the shadow pilot;
  - clinician and public-health review of the playbook;
  - the ledger scored all season;
  - a Rasid wastewater input tested and published either way;
  - the Gulf extension.
- **Business:** a hospital-operations licence on the hospital's own data, plus a public-health feed.
- ⟨letter of interest, if obtained⟩
- **Visual:** timeline.
- **Notes:** "One hospital, twelve weeks, aggregate counts. If we don't beat your own census, you walk away, and our record stays public either way. To sense is to predict. NABD is how Abu Dhabi checks the prediction."

---

**Never on any slide** (BUILD-SPEC v1.3/v1.6; positioning.md §4.6):
- the retired UAE LOSO "0.76/0.78" or "7 of 8" as a headline;
- E1 "better during surges";
- "near-parity with the CDC";
- 2024/25 alone as a headline;
- the CDC ensemble's 21–36% gain presented as NABD's;
- Chronos-2 or ACI as active;
- ED or weather as inputs;
- v2 as an improvement;
- "early warning of onset";
- "RSV is climbing";
- crisis framing;
- SEHA bed or ED numbers;
- workforce-absence figures;
- "predicts the nirsevimab window";
- "pre-registered" for the UAE v1 numbers;
- "the only" without "to our knowledge".
