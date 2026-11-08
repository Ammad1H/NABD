# NABD نبض: an open RSV and flu forecasting hub for Abu Dhabi, tested blind across the Gulf

**Future Health Digital Innovation Challenge 2026 · Statement 06 · ⟨team⟩, MBZUAI**

---

**The problem.** Every winter RSV and influenza fill Abu Dhabi's paediatric beds, but no two seasons share a shape.
- In WHO's UAE lab data, flu peaked at **40.6% in October** (2025/26), after a **five-month plateau that peaked in February** the year before.
- The RSV peak moved between weeks 41 and 47.
- One Abu Dhabi hospital, Tawam (SEHA), admitted **2,189 children aged ≤5 with RSV** in 2018–22; infants under six months stayed **5.8 days** on average.
- UAE flu case data is not public, and to our knowledge **no public respiratory forecast exists for the UAE**.

**The gap.** Abu Dhabi already *detects*: Tableegh/Malaffi notifications, UMOC early warning, Rasid wastewater. What's missing is a calibrated, checkable answer to *how big will the next 1–3 weeks be, and how sure are we?*

**The solution.** NABD is the forecast layer built to sit on top of those systems.
- WHO FluNet surveillance → calibrated RSV and flu forecasts (nowcast to +2.5 weeks after issue).
- A bilingual Arabic/English card shows the persistence baseline alongside, plus exact per-signal explanations.
- It proposes a playbook action for a named role. **Only a person approves**, and a hash-chained log records it.
- Aggregate data only; person-level fields are rejected by design.

**The evidence, all of it** (files in our repo):

| Test | Result |
|---|---|
| **Blind Gulf test** (Oman, Qatar, Saudi Arabia; plan locked before their data were downloaded; forward in time) | Flu **0.914** (95% CI 0.843–0.983) relative error vs "next week = this week": **pre-set bar met**. RSV **0.798**. Won 9/12 and 9/10 country-seasons; losses shown. |
| **Public forecast ledger** | Every round hashed before WHO publishes the answer: R0 and R1 issued 8 Nov ⟦IF DONE: externally anchored⟧ |
| **US stress test vs the CDC FluSight ensemble** (frozen protocol) | **NOT MET**: 1.22 vs a 1.15 margin. Among individual CDC-hub models: **7th of 21** (2024/25), **19th of 25** (2025/26). |
| **UAE's own 4 seasons** (forward in time) | Parity with persistence (1.002). Multi-signal v2 didn't help (1.059). This is why the live ledger exists. |

*Retrospective analyses use revised WHO data. Locks are self-attested git commits until anchored. Alert metrics are diagnostic. Onset lead is 0 weeks, so we forecast **size and duration**, not "earlier".*

**Why Abu Dhabi, why now.**
- Future Health's theme, "To Sense is to Predict".
- The flu + RSV + pneumonia campaign has expanded, and infant RSV antibodies are in the Abu Dhabi programme.
- The Gulf CDC is building regional surveillance.
- A FluNet-native method shown to transfer across GCC countries can make Abu Dhabi the regional hub.

**The ask: a 12-week shadow pilot.**
- One hospital's aggregate paediatric/ED respiratory counts, no change to care.
- Exit criterion, set in advance: relative error < 0.9 vs the hospital's own census carried forward.
- Plus an ADPHC data conversation, and a Rasid wastewater input tested and published either way.

**Business.**
- A hospital-operations licence running on the hospital's own data.
- A public-health forecast feed. WHO data are used only for the public feed and evaluation (non-commercial terms).

**Contact:** ⟨name, email⟩ · Repository: ⟨public URL⟩ · Ledger: ⟨public URL⟩
