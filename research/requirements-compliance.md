# Statement 06 requirements: compliance review of NABD (independent reviewer, 9 Nov 2026)

**Scope.** This file maps every official Statement 06 requirement, the cross-cutting asks in the statement text, and the FAQ/T&C submission rules to concrete evidence in this repo. Each gets a verdict (**MET / PARTIAL / UNMET**) and the smallest change that would make it fully MET. The reviewer did not build NABD.

**Source of the requirement wording.**
- The wording below is the wording recorded in `research/tc.md`, read by the team via Claude in Chrome on 8 Nov 2026.
- `tc.md` records organiser **headings** literally and **paraphrases** the body text, with quotes kept under 15 words.
- **Re-fetch attempted 9 Nov; it failed.** WebFetch of `https://hack2skill.com/event/futurehealthchallenge/` hit a 302 redirect loop (https → http), and a curl fetch was refused by the egress proxy (403). So the literal body text could **not** be re-confirmed in this pass.
- **Action for the team:** open the Challenge 06 tab while logged in, and paste the exact requirement text and any scoring rubric into `tc.md`. The FAQ says "full requirements are shared when you register", so the logged-in brief may carry criteria that are not public.

**Official evaluation criteria (weights):** **not public / UNVERIFIED.**
- The public launch release lists the three focus areas and prizes but no evaluation criteria (Business Wire via UniIndia, 15 Oct 2026: https://www.uniindia.com/business-wire-india/future-health-launches-global-challenge-to-move-health-innovation-towards-real-world-application-102/214940).
- The T&C say judging criteria may change (`tc.md`).
- The six criteria used in `docs/REVIEW-R*` (Impact, Technical depth, Working demo & evidence, Responsible AI, Scalability, Commercial/pilot) are the **team's own mock rubric, not the organiser's**. Do not cite them as official.
- In the absence of a published rubric, the six organiser requirement headings plus the three qualities named in the statement text below are the best available proxy.

**Date check (UNRESOLVED).**
- The launch release gives an application **deadline of "15th November 2026"** (UniIndia, URL above).
- `tc.md` says the prototype is due **20 Nov**, and the team's registration target is 10 Nov.
- Confirm which deadline applies to which deliverable on the logged-in page.

---

## A. Statement 06 requirements (organiser headings as recorded in `tc.md`)

| # | Requirement (heading; paraphrase from tc.md) | Concrete evidence in repo | Verdict | What would make it fully MET |
|---|---|---|---|---|
| 1 | **Multi-signal surveillance**: at least 2 materially different signal types (clinical/service + environmental/workplace/community) | **Headline model v1** (`uae/models.py`) uses one signal family: WHO FluNet lab surveillance. Its features are positivity, momentum, climatology and testing volume, all derived from the same lab stream (`docs/TECHNICAL.md` §4.1, §6.2 feed-removal table). **v2** adds non-sentinel lab data plus the school calendar and Ramadan. The calendar is an administrative/community covariate, it is known in advance, and it *hurt* slightly (−0.050 / −0.040 pp in the ablation, 1.059 v2/v1). **Weather:** NOT USED (blocked; `TECHNICAL.md` §3). **Workplace:** SIMULATED employer absence (`app/workforce.py`). **ED syndromic:** not in any model; it exists only as a pilot schema field (`docs/PILOT-DATA-SPEC.md` §1). | **PARTIAL** | (a) Run `adapters/weather.py --fetch` locally (NOAA GHCN AE000041217). Add temperature/humidity (and PM10/dust if obtainable) to the v2 challenger as an *evaluated* second signal type, reported even if it doesn't help. (b) On the card, show a "signals in use" panel that names each real and simulated feed and its measured contribution. (c) **Correct `tc.md` row 1**, which says "Met: clinical lab + ED syndromic + weather". Two of those three are not used. A judge reading the repo will catch this. |
| 2 | **Explainable anomaly detection**: detect a rising risk, cluster or deviation from baseline, and show **which signals, locations and time periods contributed** | **Signals:** exact per-term decomposition of each v1 forecast (`uae/explain_v1.py`, tested to sum exactly; shown on the card). **Deviation from baseline:** the `anom` term ("distance from the usual level for this week of the year"), plus a season-shape page showing every season aligned at ISO wk 27. **Time periods:** momentum (last week) and climatology (target week) terms; feed-removal ablation. **Locations: none.** All UAE inputs are national FluNet. The pilot schema has a `region` field (ABU_DHABI / AL_AIN / AL_DHAFRA), but it only exists in the synthetic file. | **PARTIAL** (signals and time: yes; locations: no) | (a) Add an explicit card line: "Location resolution: UAE national only (WHO FluNet has no sub-national data); region-level view requires partner data (PILOT-DATA-SPEC)". The statement itself flags geolocation completeness, so declaring the limit is part of compliance. (b) Show a region breakdown driven by `data/pilot/SYNTHETIC_pilot_example.csv`, watermarked SIMULATED, to prove the explanation view handles locations. (c) Optionally use the three GCC countries as a "locations" panel with real data. |
| 3 | **Actionable decision support**: proportionate preventive action, **responsible role named**, evidence and assumptions shown | `playbook/playbook.yaml` v0.4.0 has three named roles: hospital bed and roster manager, ADPHC duty officer, and occupational-health officer, in AR and EN. Bands key off exceedance probability and direction. `app/cardcheck.py` blocks contradictory cards (test included). Approve, Modify or Dismiss each needs a reason code, logged in a hash-chained `app/audit/audit.jsonl`. The persistence baseline is shown alongside, as is data freshness. The planner shows its assumptions. | **MET** (with a caveat: the playbook is ILLUSTRATIVE and unreviewed) | Get one named ADPHC or SEHA reviewer to comment on playbook v0.4.0 and log it in the repo. Until then, keep the ILLUSTRATIVE label. Note: `docs/REVIEW-R4.md` J1 said the Arabic card still carries English explanations and captions. Close that before the demo, or the "bilingual" claim is PARTIAL. |
| 4 | **Privacy-preserving views**: aggregation, small-cell suppression, **role-based access**, no individual employment or disciplinary use | **Aggregation:** all inputs are weekly aggregates. `adapters/schemas.reject_person_level` rejects person-level columns (tested). **Small-cell suppression:** k ≥ 10 primary plus complementary suppression in the pilot connector (`adapters/pilot.py`, `check_suppressed`, `tests/test_pilot.py`). The employer secure aggregation uses k ≥ 10 employers (`app/workforce.py`, SIMULATED). **No employment use:** stated in `TECHNICAL.md` §7 ("aggregate only, with no individual or worker-level data in any path"). **Role-based access: NOT BUILT.** The card's role is a self-selected dropdown (`app/streamlit_app.py` l.395). There is no authentication and no role-gated views. | **PARTIAL** (RBAC missing) | (a) Minimal RBAC: a `roles.yaml` mapping role → visible pages and data (e.g. occupational-health sees only released district absence; the public view sees no pilot data), enforced by a login stub (`streamlit-authenticator`, or a signed token in the demo), plus one test that a role cannot open another role's page. This is about half a day of work. (b) Put a "Prohibited uses: individual monitoring, employment or disciplinary decisions" line on the card and the bulletin. |
| 5 | **Operational validation**: back-test and report **lead time, sensitivity, PPV, false alarms, data latency, behaviour when inputs are missing** | **US (pre-registered back-test; alert metrics DIAGNOSTIC):** median onset lead 0 wk for every rule; 0 false alarms for every rule; PPV NABD 0.65/0.76; timely detections 17/51 and 29/52 (`results/SUMMARY.md`, `TECHNICAL.md` §6.3). Latency: median input age 4 d (`results/tables/latency_us.csv`). Dropout: one missing week ×1.41 WIS, two weeks ×1.82 (`dropout_us.csv`). **UAE:** alert table **RETIRED**, because it came from the LOSO design (trains on later seasons). There is **no forward-in-time UAE or GCC alert table**. Missing latest week: +0.14–0.26 pp WIS. FluNet lag 7 d measured, 11 d used. | **PARTIAL** (the product geography has no valid alert metrics) | (a) Compute a **forward-in-time alert table for UAE and GCC** at pre-declared thresholds (the playbook thresholds: RSV ≥10%, flu ≥20% / 15–30%). Declare it in DEVIATIONS *before* computing. Report lead, sensitivity, PPV, false alarms per season and per country-season, vs the persistence/census rule; the 12 GCC flu country-seasons give more onsets than n = 3. Report parity if that is the result. (b) A UAE latency row (FluNet publication lag per week) and a UAE feed-dropout row, in the same format as the US tables. |
| 6 | **Health and resilience impact**: earlier intervention, fewer severe incidents or occupational illness, **reduced sickness absence and lost workdays**, better policy evidence | **Earlier intervention:** not supported (0-week onset lead), and the team correctly says so. **Severe incidents:** no outcome data. **Sickness absence / lost workdays:** SIMULATED module only. No UAE absence figure exists (`research/positioning.md` §1.6). **Bed load:** the hospital winter planner is a SCENARIO on user inputs (`app/planner.py`). **Policy evidence:** a season-shape record and the RSV onset vs 1 Sep immunisation window [DATA]. **Quantified impact case:** none until this review (see `research/impact-case.md`). | **PARTIAL (weak)** | Cannot be fully MET before 20 Nov without partner data. The closest achievable: (a) adopt `research/impact-case.md` (sourced inputs, ranges, explicit unknowns) in the deck and docs; (b) make the 12-week shadow pilot measure the impact quantities directly: weekly bed-day planning error vs the hospital's current method, roster changes made, and staff respiratory absence (aggregate, k ≥ 10) if HR agrees; (c) frame the workforce impact as "staff-shift mismatch from bed-load mis-sizing" (derivable) rather than "absence reduced" (not measurable). |

### Cross-cutting qualities named in the statement text (paraphrased in tc.md)

| Quality | Evidence | Verdict | Fix |
|---|---|---|---|
| Warning **early enough to change action** | Onset lead is 0 wk (US, diagnostic); the UAE alert table is retired. NABD gives 1–3-week **size/duration** forecasts, not earlier onset. | PARTIAL | Pitch it as "early enough to resize": a 1–3-week roster horizon. Show the forward-in-time alert table from req 5. |
| **Specific enough** to be useful | National sentinel positivity, not hospital admissions or regions. | PARTIAL | Pilot connector already built. Show a SIMULATED hospital-count view and say plainly that positivity is not beds. |
| **Calibrated to avoid alert fatigue** | 95% coverage: UAE flu 0.965 / RSV 0.953 (LOSO), GCC flu 0.96, GCC RSV **0.83** (too narrow), US 0.92. US false alarms 0. Card blocks contradictory alerts. | MET for flu; PARTIAL for RSV outside UAE | State the RSV under-coverage on the card when serving GCC, or widen RSV intervals (conformal recalibration via `vendor/nabd_v2_kit/nabd_kit/recalibrate.py`) as a declared v1.1. |
| **Geolocation completeness** limits interpretation | Not addressed explicitly. | PARTIAL | See req 2(a). |

---

## B. FAQ / T&C submission rules (from `tc.md`)

| Rule | Evidence | Verdict | Fix |
|---|---|---|---|
| Working prototype by the deadline | Streamlit card, FastAPI, ledger, bulletin, 147 tests (`TECHNICAL.md` §9) | MET | — |
| Technical documentation | `docs/TECHNICAL.md` | MET | Refresh on 19–20 Nov as planned |
| Clear statement of assumptions, dependencies, limitations | `pitch/assumptions-limitations.md`; `TECHNICAL.md` §10 | MET | — |
| State current maturity and what will be built | `pitch/registration.md` "Current maturity" | MET | — |
| Declare every data source; only data you have rights to | Registration data table (WHO, CDC hub, MoE calendar, mirror of the WHO export, synthetic) | MET | The WHO FluNet licence is **non-commercial**. Keep the "business" slide consistent: the commercial product runs on partner data. |
| No unnecessary personal data | Person-level guard, aggregates only | MET | — |
| Team lead 18+; team of 1–5; one team per person | `registration.md` team block is still a placeholder (⟨Names…⟩) | **UNMET (pending)** | Fill in before submitting |
| Institutional permission (participant's responsibility) | Flagged as open in `tc.md` (MBZUAI is a co-creator) | **UNMET (pending)** | Get written MBZUAI confirmation. The T&C has no conflict-of-interest clause, but MBZUAI is a challenge co-creator (UniIndia release) |
| No confidential content (organiser may publish) | Public data only | MET | — |
| Checkpoint engagement (non-engagement can disqualify) | Process item | Not assessable | Attend Thursday sessions and log attendance |

---

## C. Claim-hygiene findings that touch compliance (fix before submission)

1. **`tc.md` req 1 says "ED syndromic + weather" are used. Neither is.** This must be corrected (see A1).
2. **"The UAE publishes no flu case counts"** (`registration.md` a150/a300, `burden.md` §6) is **too absolute.**
   - DoH's *Abu Dhabi Health Statistics 2017* published **15,994 notified seasonal-influenza cases in 2017 (6,774 in 2016)**. VERIFIED: https://doh.gov.ae/-/media/Feature/Resources/AbuDhabiHealthStatistics.ashx
   - Say instead: "no current weekly public case counts". The Jan 2026 *The National* quote ("exact data for flu cases in the UAE is not available") supports the narrower claim.
3. **Workforce figure conflict.** `positioning.md` [S16] says the Abu Dhabi workforce is 2.76M. A 9 Nov fetch of the SCAD release (https://scad.gov.ae/w/abu-dhabi-population-in-2024-grows-7-5-to-reach-4-14m) returned "more than 3.4 million" in the workforce (+9.1%). UNVERIFIED which figure is right. Re-read the release before quoting either number.
4. **"Detection but no forecast layer" is contradicted by DoH's own copy.** UMOC "includes an early warning system that predicts potential outbreaks" (VERIFIED: https://www.doh.gov.ae/en/news/khaled-bin-mohamed-reviews-umoc-ecosystem-in-ad). Keep the current "to our knowledge, no one *publishes*…" wording, and never "no forecast exists".
5. The one-pager line "Their defaults are last week's numbers and last year's pattern" is an **unverified claim about SEHA practice**. Make it conditional ("If you plan from…"), or verify it in a stakeholder conversation (`impact-case.md` §5).

## D. Priority order (judge impact ÷ effort, before 20 Nov)
1. Correct the A1 wording and the C2 claim. Minutes.
2. Minimal RBAC plus a prohibited-uses line (A4). About half a day.
3. Forward-in-time UAE+GCC alert table, declared first (A5). About 1 day; reuses `uae/alerts.py`.
4. "Location resolution" line plus a SIMULATED region view (A2). About half a day.
5. Weather as an evaluated second signal type (A1). About 1 day if the fetch works locally.
6. Adopt `impact-case.md` in the deck (A6). About half a day.
