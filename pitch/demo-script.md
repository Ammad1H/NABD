# NABD demo script (3:00)

Refined from SPEC §7. Nothing is claimed until it exists; ⟦RESULT⟧/⟦LIVE⟧ slots are filled from `results/` and `ledger/` on 19–20 Nov. If the finale format gives 7 minutes (the generic T&C clause), use the extended beats marked [+].

| Time | Screen | Say (approx.) |
|---|---|---|
| 0:00–0:25 | FluNet chart: four UAE seasons of RSV positivity; Tawam/Dubai burden callouts | "RSV peaked in week 42, 41, 41, then 47. One Abu Dhabi hospital admitted 2,189 young children with RSV in five years, and positivity swung five-fold year to year. Hospitals plan from last week's numbers." |
| 0:25–0:55 | Two bars: onset parity; size gain 21–36% | "We tested our own idea first. Forecasts don't tell a hospital *when* a surge starts any better than its census. They do tell it *how big*, with about a third less error in the CDC's own archive. So that's what NABD does." |
| 0:55–1:40 | **Live card (AR/EN toggle)**: issued ⟦LIVE: date⟧; RSV forecast for week ⟦…⟧, median ⟦…⟧%, 80% band ⟦…⟧; horizons *nowcast/+0.5/+1.5/+2.5 wk*; freshness badge | "This is this week's card. The horizons are labelled honestly: WHO publishes ten days late, so the first one is a nowcast." |
| | Click **Explain** | "Here's which signals, weeks and regions drove this forecast" ⟦the per-alert attribution view⟧. |
| | Click **Show the receipt** | "This forecast was committed to GitHub on ⟦date⟧, hash ⟦…⟧, before WHO published the answer. Here's where the truth landed" ⟦inside/outside band⟧. |
| | Playbook suggests ⟦action⟧ for role ⟦bed manager⟧. Judge clicks **Approve** and enters a reason; an audit line appears | "Nothing happens without a named person approving it, and every decision is logged." |
| 1:40–2:20 | US scoreboard: forest plot, NABD vs CDC ensemble | "Against the CDC's ensemble, using only data available at the time, two seasons and 53 locations: relative WIS ⟦RESULT⟧, CI ⟦RESULT⟧. The non-inferiority bar we froze on ⟦date⟧ was ⟦RESULT: met/not met⟧. Surge alerts: lead ⟦RESULT⟧, PPV ⟦RESULT⟧, false alarms ⟦RESULT⟧ per season." |
| | Toggle **remove ED feed** | "Take away one feed and the interval widens by ⟦RESULT⟧. The card degrades visibly instead of failing silently." |
| 2:20–2:45 | Privacy view: aggregate map with small cells suppressed; SIMULATED watermark on the workforce layer | "Aggregate only, small cells suppressed, role-based views. The workforce feed is simulated, and labelled as such." |
| 2:45–3:00 | Pilot slide | "Give us one hospital's aggregate paediatric admissions for twelve weeks in shadow mode. If we don't beat your own census by 10%, you've lost nothing, and our track record stays public either way." |

[+] Extended beats (if 7 minutes):
- the vintage rule plus the leakage test failing on purpose (30 s);
- UAE leave-one-season-out table (30 s);
- Chronos-2 ablation (20 s);
- business model and the Rasid / ADPHC fit (40 s).

**Fallbacks:**
- If live data fetch fails, use the cached build. The badge reads "cached ⟨date⟩"; never hide it.
- If the app crashes, play the recorded 3-minute video.
