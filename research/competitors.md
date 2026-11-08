# Competitive landscape and positioning (8 Nov 2026)

VERIFIED means read on the cited page today, or verified by an earlier review round where noted.

## Abu Dhabi public-sector landscape
| Player | What it does | Status | NABD positioning |
|---|---|---|---|
| **ADPHC AI epidemic-prediction tender** (Jul 2024) | Platform to flag emerging outbreaks in real time from local and international trends plus travel patterns. Includes a surveillance dashboard (demographics, clusters, food/water/animal/vector factors) and automated early-warning alerts. https://agbi.com/health/2024/07/abu-dhabi-launches-ai-tender-to-predict-epidemic-threats | VERIFIED scope. **Awardee not found** after searching news, tender coverage and partner announcements (G42/Presight/Core42/IBM). No public award notice | That platform answers *"is a new outbreak emerging?"* (detection, novel threats). NABD answers *"how big will the known seasonal RSV/flu wave be at my hospital in 1–3 weeks?"* (load forecasting). It complements the tender: a calibrated forecast feed plus accountability protocol the platform can host. Ask organisers or DoH at Q&A who runs it |
| **DoH–Microsoft Population Health Intelligence (PHIF)**; unveiled at GITEX 2025 as an AI population-health intelligence platform | Population risk prediction, mainly chronic disease (obesity, cancer, cardiometabolic) | VERIFIED (R4/R6 reviews; DoH and Abu Dhabi Media Office pages) | Different horizon and disease class. NABD is a short-horizon respiratory-season feed. Pitch: "a module PHIF could host" |
| **Rasid** (ADQCC + G42 Healthcare) | Wastewater monitoring with AI early warning | VERIFIED (R2-J3) | Partner, not rival. Offer: add Rasid's RSV/flu wastewater signal as a covariate and publish the skill gain. Never claim a "missing layer" |
| **ADPHC seasonal flu campaign** | Prevention; 350k+ vaccinated in 2025–26 | VERIFIED | NABD supports the hospitals that absorb what prevention misses |

## Hospital capacity forecasting (commercial)
| Product | What it forecasts | Horizon | Relevance |
|---|---|---|---|
| **GE HealthCare CareIntellect for Operations** (launched 15–16 Sep 2026; AWS Marketplace; first sites Queen's Health and Duke) | Census, staffing, ED boarding, discharges, transfers; recommends throughput actions. https://hlth.com/insights/news/ge-healthcare-launches-careintellect-to-predict-hospital-capacity-constraints | **Up to 72 hours**, from inside-hospital data | VERIFIED. The incumbent category for *operational* capacity. NABD sits upstream: **1–3 weeks**, driven by community epidemic signals the hospital can't see in its own EHR. The two are complementary, and NABD's forecast could feed a 72-hour tool. This is also a judge-proofing line: "we're not rebuilding a command centre" |
| Generic vendors (H2O.ai hospital capacity simulator, BigBear.ai digital twins, John Snow Labs content, etc.) | Capacity simulation / predictive analytics | Varies | Found in search; not evaluated (UNVERIFIED depth). None found with a UAE respiratory forecast or a public forecast track record |
| GCC "AI health platform" sites (e.g. a riayacare page claiming 2.5M+ GCC records) | Unclear | — | UNVERIFIED and low credibility (site built with a no-code tool). Ignore |

## Respiratory forecasting (public-health)
| Player | What | Relevance |
|---|---|---|
| **CDC FluSight hub** (US) | Ensemble of about 40 models forecasting state flu admissions weekly; public archive with real-time vintages | Our **benchmark**, not a competitor. No UAE coverage. VERIFIED (hub cloned 5 Nov) |
| WHO FluNet | Weekly UAE lab surveillance (counts and positivity), about 10–11 days lag | Our data source; no forecasts |
| UAE / GCC | **No public calibrated RSV + flu forecast found** for the UAE or GCC | The gap. The National (Jan 2026) notes UAE flu case data is not publicly available |

## Competitor entries in this challenge (from the 5 Nov loop review)
- At least 8 public Statement 06 repos, mostly heat/workforce dashboards on **simulated** data (R1-C). One already has an alert-card design.
- NABD's edge:
  - real data;
  - real-time-vintage (leakage-free) back-test against the CDC ensemble;
  - pre-registered evaluation;
  - a public, hash-stamped forecast ledger;
  - honest negative findings.

## One-paragraph positioning (for slide 9 / Q&A)
Abu Dhabi already has a detection layer (the ADPHC platform, Rasid), a population risk layer (PHIF) and, at hospitals, short-horizon operations tools (the 72-hour command-centre class). What's missing is a calibrated **1–3-week forecast of the seasonal RSV/flu load**, with a public track record. It links what surveillance sees to what a bed manager must decide this week. NABD is that link, built to plug into the platforms Abu Dhabi has already bought.
