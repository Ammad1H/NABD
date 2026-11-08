# Hack2skill FHDIC rules, FAQ and Statement 06 requirements (read 8 Nov 2026)

Read-only via Claude in Chrome from https://hack2skill.com/event/futurehealthchallenge/ (FAQ accordion, Challenge 06 tab) and https://hack2skill.com/event/futurehealthchallenge/tnc (Terms and Conditions). Quotes are kept under 15 words; everything else is paraphrased. Not legal advice.

## FAQ (event page) — VERIFIED
| Item | What it says |
|---|---|
| Team size | One to five members; members can be in different countries |
| Multiple entries | **No.** Each person can be on one team only |
| Eligibility | Open worldwide. Team leads and award recipients must be **18+ by the submission deadline**. Getting employer or institution permission is the participant's responsibility |
| Data | Organisers provide **no data, not even synthetic data**. Use only data you have the right to use, **declare every source**, and avoid unnecessary personal data |
| Existing product | Allowed (ideas, existing solutions, early prototypes). You must **state current maturity and what you will build during the Challenge** |
| What to submit | A working prototype by **20 Nov**, with technical documentation and a clear statement of **assumptions, dependencies and limitations**. "Full requirements are shared when you register." |
| IP (FAQ) | You retain full ownership of your IP (but see the T&C right of first refusal below) |
| Prizes | USD 50k / 35k / 20k for the top three; winners present at GITEX on 7–11 Dec. Selected solutions get a readiness assessment and a potential pathway beyond the Challenge |
| Technology | No platform, model or device is mandatory |
| Live sessions | Every Thursday, recorded |

## Terms and Conditions (tnc page) — VERIFIED, key clauses
- **IP: right of first refusal.** Participants grant the Organiser a right of first refusal on any **exclusive** licence or acquisition of submitted materials (software, source code, docs, data, concepts) for **6 months after the Hackathon**. If a third party makes an offer, the Organiser has 30 days to match it.
  - **Implication:** an open-source licence (MIT/Apache, non-exclusive) for the public repo appears compatible, because the ROFR covers exclusive deals. Any exclusive commercial deal (e.g. with a hospital group) before about June 2027 must first be offered to the Organiser. Confirm with the organisers if a deal is in view.
- **Publicity.** The Organiser may publish and disclose submitted ideas in any medium worldwide, free of charge. **Don't put anything confidential in the submission.**
- **Originality and copyright.** Participants warrant that they own the submission or hold sufficient rights; no third-party or confidential content. This matters for data licences: WHO FluNet terms (public-health, non-commercial), CDC data (public domain), and the hub's MIT licence. Declare them all.
- **Engagement.** Team members must take part at checkpoints on the site or communication channels (Slack/Discord/WhatsApp, etc.). **Non-engagement can disqualify the whole team.**
- **Pitch format (generic Hack2skill clause).** Shortlisted teams may get about **7 minutes of demo plus 3 minutes of Q&A**. The event page shows no shortlist stage, so treat this as a possible finale/GITEX format.
- **Judging.** Criteria may change; the Organiser's and judges' decisions are final.
- **Prizes.** Taxes are the winner's responsibility; paid within 60 days; a "TDS" deduction clause is boilerplate.
- **Photo/video.** Organiser may use participant likeness for 10 years.
- **Conflict of interest:** **no clause found** covering employees or students of the co-creators (MBZUAI, Microsoft, Inception/G42). Searching the T&C for conflict/employee/affiliate terms found only the liability release. The FAQ puts institutional permission on the participant. **Action:** check whether MBZUAI has its own policy on student participation in sponsor-run competitions, and if in doubt email support+fhdic@hack2skill.com.
- **Open-source requirement:** none found.
- **Video length / deck format:** not specified publicly ("full requirements shared when you register").

## Statement 06: the official requirement list (read from the Challenge 06 tab) — VERIFIED
Core question, paraphrased: combine population, environmental, service and workplace signals to spot emerging risks earlier and support timely, targeted prevention. The organisers ask for a warning that is early enough to change action, specific enough to be useful, and calibrated to avoid alert fatigue. They note that geolocation completeness can limit interpretation.

| # | Requirement (organiser heading) | What it asks | NABD status / gap |
|---|---|---|---|
| 1 | Multi-signal surveillance | ≥2 materially different signal types (clinical/service + environmental/workplace/community) | Met: clinical lab + ED syndromic + weather + calendar/testing volume |
| 2 | Explainable anomaly detection | Detect a rising risk / cluster / deviation from baseline and **show which signals, locations and time periods contributed** | **Partial gap.** SPEC has a feed-removal ablation but no per-alert attribution card. Needs an alert explanation view (signal contributions, locations, weeks) |
| 3 | Actionable decision support | Proportionate preventive action, **responsible role named**, evidence and assumptions shown | Met by the playbook card; make sure it names the role and shows assumptions |
| 4 | Privacy-preserving views | Aggregation, small-cell suppression, role-based access, no individual employment/disciplinary use | Aggregate-only; **add small-cell suppression + RBAC demo** (cheap) |
| 5 | Operational validation | Back-test and report **lead time, sensitivity, PPV, false alarms, data latency, behaviour when inputs are missing** | **Important gap.** SPEC's primary endpoint is WIS. The judges' own checklist asks for surge-alert metrics. Report alert metrics (lead, sensitivity, PPV, false alarms per season) for a pre-registered surge definition, plus latency and missing-feed degradation. The `lead_time_probe.py` design already has most of this |
| 6 | Health and resilience impact | Earlier intervention, fewer severe incidents/occupational illness, **reduced sickness absence and lost workdays**, better policy evidence | Partial: hospital-load impact story; workforce/absence part is simulated only |

**Coordinator flag:** requirements 2 and 5 should be added to G3/G5 (alert metrics and per-alert explanation). Otherwise judges using the organiser's checklist will mark NABD down on operational validation even if the WIS result is strong.
