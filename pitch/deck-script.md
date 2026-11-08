# NABD: 10-slide deck script

⟦RESULT: …⟧ slots come from `results/summary.json` and `results/figures/`. Every number on a slide must trace to `results/` or `research/burden.md` (G9). Speaker notes are about 40 words each.

---

### 1. Title
- **On slide:** NABD (نبض, "pulse"): calibrated RSV and flu surge forecasts for Abu Dhabi hospitals. Statement 06 · MBZUAI · ⟨team names⟩.
- **Visual:** a pulse line morphing into a forecast fan chart.
- **Notes:** "Every winter, RSV and flu reach Abu Dhabi's hospitals together, and never on the same schedule. NABD tells a hospital how big and how long the next weeks will be, and publishes every forecast before the outcome, so you can check us."

### 2. The problem: no two seasons are alike
- **On slide:** UAE RSV peak in weeks 42, 41, 41 and 47 (WHO FluNet). Tawam (Al Ain): 2,189 RSV admissions of children aged 5 and under over 2018–22, with yearly positivity from 2.9% to 16%. Dubai: 22% of infants with RSV hospitalised, under 2% with known risk factors.
- **Visual:** four seasons of UAE RSV positivity overlaid; small burden callouts with citations.
- **Notes:** "The load is large, it falls on previously healthy infants, and its timing and size vary every year. Abu Dhabi doesn't publish flu case counts, so planners work from last week's numbers."

### 3. What we tested first: *when* vs *how big*
- **On slide:** two bars.
  - (a) Onset: forecast-based alarms were no earlier than a hospital's own census threshold (155 US state-seasons).
  - (b) Size: calibrated forecasts cut 0–3-week error 21–36% vs carrying the census forward (CDC archive, 3 seasons).
- **Visual:** a parity bar next to a gain bar.
- **Notes:** "We started by trying to break our own idea. Forecasting doesn't tell you *when* a surge starts any better than your census does. It does tell you *how big*. So that's all we claim."

### 4. NABD: signals → calibrated forecast → approved action
- **On slide:** inputs:
  - clinical: WHO FluNet UAE, US NHSN;
  - service/geospatial: NSSP ED share;
  - environmental: Abu Dhabi weather;
  - administrative: school calendar, testing volume;
  - occupational: secure-aggregation design, SIMULATED.

  These feed a GLM + foundation model (ablated) → quantile ensemble → online calibration → bilingual card → named approver → audit log.
- **Visual:** architecture strip.
- **Notes:** "Five signal families, an interpretable core, a foundation model we ablate rather than trust, and calibration on every series. The output is a card a duty officer approves, never an automatic action."

### 5. Statement 06, requirement by requirement
- **On slide:** table of the six official requirements → artefact → real or simulated: multi-signal ✓; explainable alerts (signal, location and week contributions) ✓; decision support with named role ✓; privacy (aggregate, small-cell suppression, RBAC) ✓; operational validation (lead time, sensitivity, PPV, false alarms, latency, missing feeds) ⟦RESULT⟧; impact (scenario) ✓.
- **Visual:** checklist table with real/simulated tags.
- **Notes:** "This is the organisers' own checklist. Where something is simulated, the slide says so."

### 6. Proof I: as good as the CDC's best?
- **On slide:**
  - NABD vs CDC FluSight ensemble, vintage-correct, 2 test seasons × 53 locations: relative WIS ⟦RESULT⟧ [95% CI ⟦RESULT⟧]; non-inferiority margin 1.15 ⟦RESULT: met/not met⟧.
  - vs baseline: ⟦RESULT⟧.
  - Coverage: 50% ⟦RESULT⟧, 95% ⟦RESULT⟧.
  - Protocol frozen ⟦RESULT: date, hash⟧.
- **Visual:** relative-WIS forest plot by season and horizon.
- **Notes:** "We fixed the bar before testing, against the strongest public benchmark in respiratory forecasting, using only data available at the time. Here is the result, including the horizons where we lose."

### 7. Proof II: UAE and the public receipt
- **On slide:**
  - UAE leave-one-season-out: WIS vs persistence ⟦RESULT⟧ and vs seasonal analog ⟦RESULT⟧ (n=4 seasons, descriptive).
  - Surge-alert metrics: lead ⟦RESULT⟧, sensitivity ⟦RESULT⟧, PPV ⟦RESULT⟧, false alarms per season ⟦RESULT⟧.
  - Live ledger: ⟦LIVE: rounds issued, points scored, coverage so far⟧, first round ⟨date⟩, hash ⟨…⟩.
- **Visual:** a ledger table with green and red cells; GitHub commit screenshot.
- **Notes:** "In the UAE we're honest about four seasons. What we add is a forward record: every forecast was committed before WHO published the answer."

### 8. Responsible by design
- **On slide:**
  - aggregate data only (schema rejects person-level fields);
  - named approver plus audit log;
  - honest horizons and freshness badge;
  - SIMULATED watermarks;
  - automation-bias guard (persistence shown alongside);
  - WHO non-commercial terms respected;
  - no employment or disciplinary use.
- **Visual:** the card with annotations.
- **Notes:** "Nothing leaves the system without a person approving it, and the system never pretends to know more than its data allows."

### 9. Pilot, positioning and business model
- **On slide:**
  - Pilot: 12-week shadow on one SEHA hospital's aggregate paediatric admissions; exit at rel. WIS < 0.9 vs own census.
  - Positioning: a feed for ADPHC's platform and PHIF; a Rasid wastewater covariate offer; upstream of 72-hour command-centre tools.
  - Revenue: hospital operations licence (own data); public-health feed.
- **Visual:** a layer diagram (detection → NABD → operations).
- **Notes:** "We plug into what Abu Dhabi already bought. The first step costs the hospital nothing; if we don't beat its own census by 10%, it walks away."

### 10. Team, 90 days, ask
- **On slide:**
  - Team roles.
  - 90-day plan: shadow pilot, playbook review, RSV/COVID extension, GCC adapters.
  - **Ask:** one hospital shadow partner plus an ADPHC data conversation.
  - ⟨Letter of interest, if obtained⟩.
- **Visual:** timeline.
- **Notes:** "We're asking for one hospital, twelve weeks, aggregate counts. Our track record is public and grows every week, whatever you decide."
