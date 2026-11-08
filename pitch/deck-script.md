# NABD: 10-slide deck script (round 2, headline per BUILD-SPEC v1.3)

**Rules:**
- Every number traces to `results/` or `research/burden.md` (G9); see `research/claims-ledger.md`.
- ⟦RESULT: file⟧ marks an output still in build. If it is missing on 19 Nov, the slide line is cut, never estimated.
- If `research/positioning.md` exists, slides 2 and 9 should draw their problem and value language from it ⟦check before final⟧.

**Headline (slide 1 and the video's first line):**
> **The UAE has no respiratory forecasting hub. NABD is one: calibrated RSV and flu forecasts with a public, tamper-evident track record, held to the CDC's standard.**

---

### 1. Title
- **On slide:** NABD (نبض, "pulse"). An open RSV and flu forecasting hub for Abu Dhabi, held to the CDC's standard. Statement 06 · ⟨team⟩ · MBZUAI.
- **Visual:** pulse line turning into a forecast fan.
- **Notes (≈40 words):** "Every winter, RSV and flu reach Abu Dhabi's hospitals together, and never on the same calendar. The UAE publishes no forecast of what's coming. NABD is that forecast, with a public record of every call it has made."

### 2. The problem: same viruses, different winter every year
- **On slide:**
  - UAE sentinel RSV peaked in ISO weeks **42, 41, 41, 47** (2022–2025; WHO FluNet, `data/raw/flunet_are.csv`).
  - Tawam Hospital, Al Ain: **2,189** RSV admissions of children aged ≤5 over 2018–22; yearly positivity **2.9% → 16%**.
  - Dubai: **22%** of under-2s with RSV hospitalised; **<2%** had a known risk factor.
  - The UAE publishes no flu case counts.
- **Visual:** four UAE RSV seasons overlaid, with three cited callouts.
- **Notes:** "The burden is real, it lands on previously healthy infants, and its timing moves every year. DoH says this season looks like the last two: normal, but variable. Planners still only see last week."
- **Sources:** `research/burden.md` items 1, 3, 6, 8.

### 3. The gap: Abu Dhabi has detection layers, but no seasonal forecast
- **On slide:**
  - ADPHC's 2024 AI platform tender (outbreak detection);
  - Rasid (wastewater);
  - DoH–Microsoft population-health intelligence (chronic risk);
  - 72-hour hospital command-centre tools.
  - **Missing:** a calibrated, weeks-ahead RSV/flu forecast with a public track record.
- **Visual:** layer diagram (detect → **forecast** → operate), with NABD in the middle layer.
- **Notes:** "We're not rebuilding what Abu Dhabi bought. We're the forecast layer between surveillance and the bed manager, built to plug into those platforms."
- **Source:** `research/competitors.md`.

### 4. NABD v1: what's built today
- **On slide:** WHO FluNet UAE (positivity + testing volume) → linear growth model on the logit scale with a seasonal term → calibrated quantiles (nowcast, +0.5, +1.5, +2.5 wk) → bilingual card → playbook action for a named role → **Approve / Modify / Dismiss** → hash-chained audit → hashed ledger round.
- **Second row, "in build for 20 Nov":**
  - multi-signal UAE v2 (non-sentinel, testing volume, school calendar) with per-signal explanations;
  - UAE alert metrics;
  - Gulf out-of-sample test;
  - outside-anchored ledger.
- **Visual:** architecture strip. Built in solid, in-build in outline, SIMULATED workforce module in grey.
- **Notes:** "Version one is deliberately simple and auditable. What's solid on the slide runs today; what's outlined is being built and will be marked exactly that way in our submission."

### 5. Statement 06, requirement by requirement
- **On slide (organiser's checklist → status):**

| Requirement | Status |
|---|---|
| Multi-signal | v1 lab + testing volume; v2 ⟦RESULT: results/uae/tables/ablation.csv⟧ |
| Explainable detection | ⟦RESULT: results/uae/explain/⟧ |
| Decision support with named role | built (ILLUSTRATIVE playbook) |
| Privacy | aggregate only, person-level fields rejected, simulated k-anonymous workforce aggregation |
| Operational validation | US alerts built, UAE ⟦RESULT: G10 UAE table⟧; latency 4-day input age (US); missing-feed ×1.41 / ×1.82 |
| Impact | pilot hypothesis, not a result |

- **Visual:** checklist with built / in build / simulated tags.
- **Notes:** "This is the organisers' own checklist. We show where we're complete, where we're in build, and where we're simulated."
- **Sources:** `research/tc.md`, `results/tables/latency_us.csv`, `results/tables/dropout_us.csv`.

### 6. Proof I: the UAE (headline evidence)
- **On slide:**
  - Against carrying the latest week forward: relative WIS **flu 0.76 (0.70–0.82)**, **RSV 0.78 (0.71–0.87)**. Better in **7 of 8** season-series (flu 4/4, RSV 3/4).
  - Against a seasonal-average forecast: **flu 0.70**, **RSV 0.69**.
  - Caveat in the same font size: *4 seasons · retrospective · design-stage, not pre-registered · RSV lost the most recent season.*
  - ⟦RESULT: results/gcc/ (G12)⟧. If it lands: "Frozen method, locked plan, other Gulf countries' data nobody had seen: ⟨result, every country shown⟩."
- **Visual:** UAE back-test chart (`results/uae/figures/uae_backtest.png`), with the season-win grid beside it.
- **Notes:** "In the UAE there's no ensemble to beat, because there's no forecast at all. Against what a planner would otherwise do, NABD cut error by about a quarter. Four seasons is thin, which is why we're testing it on other Gulf countries' data, locked in advance."
- **Source:** `results/uae/SUMMARY.md`.

### 7. Stress test against the CDC: **NOT MET**
- **Title:** *"We set our bar at the CDC's best. NABD v1 missed it, and here is exactly where."*
- **On slide:**
  - Protocol frozen 8 Nov, before any test score (`docs/FREEZE.md`, commit `ac16901`, SHA-256 `2846533f…`). Real-time data only.
  - **11,660** forecasts across 53 US locations, 2 seasons and horizons 0–3.
  - Relative WIS vs the CDC FluSight ensemble (pools about 40 teams): **1.22 (95% CI 1.01–1.52)**. Bar: upper bound < 1.15. **NOT MET** (written in red by the team).
  - 2024/25: **1.03** (0.89–1.25). 2025/26: **1.52** (1.09–2.03).
  - vs naive baseline: **0.82** (0.66–1.02); the CDC ensemble: 0.67.
  - Failure mode, found after the test (a hypothesis, not a claim): overshoot after the peak.
  - ⟦RESULT: league table (D7) → "Among N individual CDC-hub models scored the same way, v1 ranks k"; method declared before computing⟧.
- **Visual:** forest plot by season and horizon with a red margin line at 1.15 (`results/figures/rel_wis_by_horizon.png`, or the round-2 figure pack).
- **Notes (≈25 s):** "In the US, use the CDC ensemble: in 2024/25 we came close; in 2025/26 we didn't. We froze this test before running it, and we're showing you the season we lost. That's why you can believe our UAE numbers."
- **Source:** `results/SUMMARY.md`.

### 8. What the miss taught us, and how you can check us
- **On slide:**
  - **No early onset warning:** median onset lead was 0 weeks for every rule, including the CDC's. So we don't sell "earlier".
  - **Fewer false alarms:** at 3 per 100k, the share of NABD alerts followed by a real onset was 0.65 / 0.76 (2024/25 / 2025/26), vs 0.41 / 0.67 for the CDC ensemble and 0.60 / 0.46 for a census rule. *Diagnostic: the thresholds were informed by pre-freeze probes (DEVIATIONS D5).*
  - **Missing data hurts:** a 1-week gap raises error ×1.41, so v2 adds independent signals.
  - **How you check us:** a public hashed ledger, outside timestamps ⟦RESULT: ledger/ANCHOR.md⟧, and the deviation log.
- **Visual:** small PPV bars with the 0-week lead stated beside them; ledger "receipt" screenshot.
- **Notes:** "The organisers asked for warnings calibrated to avoid alert fatigue. Our alerts were right more often, but not earlier, and we say both. Every forecast we issue from here is hashed before the answer exists."
- **Sources:** `results/tables/alerts_us.csv`, `results/tables/dropout_us.csv`, `docs/DEVIATIONS.md`.

### 9. Responsible by design, and how it plugs in
- **On slide:**
  - Aggregate only (schema rejects person-level fields; tested).
  - A named approver for every action, with a hash-chained audit.
  - Freshness badge and issue-relative horizons.
  - Persistence forecast always shown alongside (automation-bias guard).
  - SIMULATED watermark on the workforce module.
  - WHO non-commercial terms respected.
  - Plugs in as a feed for ADPHC's platform and the DoH population-health platform; Rasid offer: add wastewater as an input and publish whether it helps.
- **Visual:** annotated card screenshot (`app/screenshots/`).
- **Notes:** "Nothing leaves NABD without a person approving it. It never claims more than its data allows, and it's built to sit inside the platforms Abu Dhabi already runs."

### 10. Pilot, ask and 90 days
- **On slide:**
  - **Pilot:** 12-week shadow run on one hospital's aggregate paediatric/ED admissions. Exit criterion, set in advance: relative WIS < 0.9 vs the hospital's own census carried forward. No change to care.
  - **Ask:** one hospital partner plus an ADPHC data conversation.
  - **90 days:** shadow pilot, playbook review by clinicians and public health, the Gulf hub extension, a prospective ledger scored all season.
  - Business: a hospital-operations licence (own data); a public-health feed.
  - ⟨letter of interest, if obtained⟩
- **Visual:** timeline.
- **Notes:** "One hospital, twelve weeks, aggregate counts. If we don't beat your own census, you walk away, and our track record stays public either way."

---

**Never on any slide** (BUILD-SPEC v1.3 / judges' list):
- E1 "better during surges";
- "near-parity with the CDC" (pooled);
- 2024/25 alone as a headline;
- the CDC ensemble's 21–36% gain presented as NABD's;
- Chronos-2 or ACI as active;
- ED or weather inputs as used in v1;
- "pre-registered" for the UAE v1 numbers.
