# NABD نبض: an open RSV and flu forecasting hub for Abu Dhabi, tested across the Gulf

**Future Health Digital Innovation Challenge 2026 · Statement 06 · ⟨team⟩, MBZUAI**

---

**The Monday problem.** Every winter week, Abu Dhabi's paediatric bed managers and public-health officers plan the next three weeks of RSV and flu. Their defaults are last week's numbers and last year's pattern, but UAE seasons don't repeat:
- **Flu** peaked at **40.6% in October** 2025, after a **five-month plateau that peaked in February** the season before. The RSV peak moved between weeks 41 and 47 (WHO FluNet UAE, our computation).
- **One Abu Dhabi hospital (Tawam, SEHA)** admitted **2,189 children aged ≤5 with RSV** in 2018–22, and infants under six months stayed **5.8 days** on average.
- **Dubai claims data:** 22% of under-2s with RSV were hospitalised, and <2% had a known risk factor.
- **No public data or forecast:** UAE flu case data is not public, and to our knowledge **no public respiratory forecast exists for the UAE**.

**Who decides, and what a wrong call costs.**
- **Hospital operations** (surge roster, beds, elective deferral): over-staffing as the wave turns, or boarding at the peak.
- **ADPHC/DoH surveillance** (advisories, briefings): too late or too often.
- **The immunisation programme** (campaign and catch-up timing): a fixed window against a moving epidemic.

**The solution.** NABD is the forecast layer built to sit on top of Abu Dhabi's detection systems (Tableegh/Malaffi, UMOC, Rasid).
- **Forecasts:** WHO FluNet surveillance → probabilistic RSV and flu forecasts, nowcast to +2.5 weeks after issue, with coverage reported.
- **The card:** a bilingual Arabic/English card shows the **chance of crossing each pressure threshold** and the direction of the forecast. It always shows the last-week baseline alongside, plus exact per-signal explanations.
- **Human decision:** it proposes a playbook action for a named role. **Only a person approves**, and a hash-chained log records it. Contradictory cards are blocked.
- **Workforce:** a hospital view translates the wave into its own beds and staff, as a labelled SCENARIO ⟦IF BUILT: hospital winter planner, in AED⟧. The employer-absence path is a secure-aggregation design (k ≥ 10), SIMULATED.
- **Privacy:** aggregate data only. Person-level fields are rejected by design, with k ≥ 10 suppression for pilot data. No individual or employment use.

**The evidence, all of it** (files in our repo):

| Test | Result |
|---|---|
| **Gulf out-of-sample test**: Oman, Qatar, Saudi Arabia; plan locked before their data were downloaded; forward in time | **Influenza: 46% less forecast error than planning from past-season patterns** (0.536, pre-registered secondary), and **9% less than last week carried forward** (0.914, 95% CI 0.843–0.983, **pre-registered primary met**). Won 9 of 12 country-seasons; losses shown. RSV is secondary and less robust. |
| **US stress test vs the CDC FluSight ensemble** (frozen protocol) | **Missed our bar** (1.22 vs a 1.15 margin). Among individual CDC-hub models: **7th of 21** (2024/25) and **19th of 25** (2025/26). |
| **UAE's own record** (forward in time) | Parity with last week (1.002). UAE sentinel data start in 2022; our post-hoc reading is that the method needs more seasons of history. Multi-signal v2 didn't help (1.059). |
| **Forecast ledger** | Every round is hashed before WHO publishes the target week. As of 8 Nov: one round (data through W44), 0 weeks scored. ⟦IF DONE: public at ⟨URL⟩, anchored ⟨date⟩⟧ |

*Retrospective analyses use revised WHO data. Locks are self-attested git commits until anchored outside the team. Alert metrics are diagnostic. At the US primary threshold onset lead is 0 weeks, so NABD forecasts **size and duration**, not "earlier".*

**Why Abu Dhabi, why now.**
- Future Health's theme is "To Sense is to Predict".
- The national campaign has expanded to flu + RSV + pneumonia, and infant RSV antibodies are in the Abu Dhabi programme.
- The Gulf CDC is building regional surveillance.
- A FluNet-native method that beat last-week persistence in three Gulf countries (9 of 12 influenza country-seasons) fits a regional hub, starting in Abu Dhabi.

**The ask: a 12-week shadow pilot.**
- One hospital's aggregate weekly paediatric respiratory counts (`docs/PILOT-DATA-SPEC.md`), with no change to care.
- Exit criterion, set in advance: relative error < 0.9 vs the hospital's own census carried forward.
- Plus an ADPHC data conversation, a clinician review of the playbook, and Rasid's wastewater signal tested as an input and published either way.

**Business (hypothesis).**
- A public-health forecast-feed licence per country per season, and a hospital-operations seat per facility, running on the hospital's own data. WHO data are used only for the public feed and evaluation (non-commercial terms).
- Open, non-exclusive code licence. Any exclusive deal goes to the organiser first for 6 months (T&C).

**Contact:** ⟨name, email⟩ · Repository: ⟦IF DONE: ⟨public URL⟩⟧ · Ledger: ⟦IF DONE: ⟨public URL⟩⟧
