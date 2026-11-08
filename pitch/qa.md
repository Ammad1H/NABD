# Judge Q&A prep: the 15 most hostile questions

Drawn from the loop's blind judge rounds (R4/R6: public health, AI/tech, partnerships). ⟦RESULT: …⟧ = fill from `results/summary.json`; never improvise a number. Keep each answer under about 30 seconds.

## Public-health judge (DoH/ADPHC)

**1. "ADPHC already bought an AI epidemic-prediction platform. Why do we need you?"**
That tender targets detection: flagging new outbreaks from trends and travel data. NABD does something different. It forecasts how big the known seasonal RSV and flu wave will be at a hospital over the next 1–3 weeks, and publishes its track record. It is a feed that platform can host, not a replacement.

**2. "National sentinel positivity isn't hospital load. How does this help an ED?"**
Agreed. That's why our UAE claims are strictly about positivity-forecast skill. Load claims are made only where we have load data: on US admissions and ED share, we ⟦RESULT: rel. WIS vs FluSight ensemble⟧. For Abu Dhabi, load forecasting is a pre-specified 12-week shadow test on one hospital's aggregate counts, with exit criteria fixed in advance.

**3. "Four UAE seasons is nothing. Why should we trust the UAE results?"**
We don't ask you to. The UAE results are labelled n=4 and descriptive. The statistical evidence comes from two US test seasons across 53 locations, using only the data available at each forecast date. The live ledger adds a forward record you can audit.

**4. "Your onset detection is no earlier than our census. So what is the warning?"**
Correct, and we tested it ourselves: forecasting doesn't beat a hospital's census at spotting *when* a surge starts. Where it pays is *how big and how long*. In the CDC archive, calibrated forecasts cut error 21–36% compared with carrying the census forward. That is the decision a bed manager can't make from today's count. On the organiser's alert metrics, our pre-registered surge alert gets ⟦RESULT: lead time / sensitivity / PPV / false alarms per season⟧.

**5. "Where is the workforce half of Statement 06?"**
It's designed but simulated: a secure-aggregation sick-absence feed where no single employer is visible, demonstrated on labelled synthetic data. We refused to put a decorative "real" signal in its place. A pilot with an employer consortium would supply the data.

## AI / technical judge (Microsoft / G42 / MBZUAI)

**6. "How do you know your back-test isn't leaking?"**
The CDC hub publishes 102 weekly real-time versions of the data. Each forecast uses only the latest version as of the Wednesday before its reference date. A unit test injects future data and must fail. The ensemble and NABD are scored against the same truth.

**7. "Beating the FluSight baseline is trivial. What's your real bar?"**
We agree, so it's secondary. The primary endpoint is non-inferiority to the **CDC ensemble**: the upper 95% bootstrap bound of relative WIS below 1.15, frozen in `PROTOCOL.md` (hash ⟦RESULT: protocol sha⟧) before testing. Result: ⟦RESULT: met / not met, rel. WIS [CI]⟧.

**8. "If you don't beat the CDC ensemble, what's the point?"**
The ensemble pools about 40 US teams and doesn't exist for the UAE. Matching it within a margin, as a small team using public signals, shows the method transfers. Being honest when we fall short is part of the product: a forecast you can audit.

**9. "Is the foundation model doing anything?"**
We report it as an ablation, ⟦RESULT: Δ WIS with/without Chronos-2⟧. If it adds nothing, we say so, and the calibrated statistical ensemble carries the result. *(Note: Chronos-2 weights could not be downloaded in our build environment, so this row may read "run locally".)*

**10. "Your horizons say '1–3 weeks', but WHO data is 10 days late."**
That's why our horizons are labelled relative to the issue date. UAE: nowcast, +0.5, +1.5 and +2.5 weeks. US: +0.5 to +3.5 weeks. Every ledger row carries these labels.

**11. "How are intervals calibrated?"**
Through online adaptive conformal adjustment on each target series, with reported 50% and 95% coverage: ⟦RESULT: coverage⟧. The coverage monitor triggers a review if 80% coverage stays below 65% for six weeks.

## Partnerships / investor judge (PureHealth / M42 / Mubadala Bio)

**12. "Who pays, and why would SEHA say yes?"**
Hospital operations pay: the bed and rostering decisions made every winter. The first step costs nothing: a 12-week shadow on aggregate counts. Success means beating the hospital's own census carried forward by 10% or more. Nothing changes in patient care.

**13. "GE's CareIntellect already predicts census. Why you?"**
It forecasts up to 72 hours from inside-hospital data. We forecast 1–3 weeks from community epidemic signals the hospital can't see. The two are complementary, and our forecast can feed a 72-hour tool.

**14. "WHO FluNet is non-commercial. Isn't your business blocked?"**
No. FluNet powers the public-health feed and the evaluation only. The commercial hospital product runs on the hospital's own aggregate data and does not redistribute FluNet. We declare every data source, as the Challenge requires.

**15. "What's defensible? Anyone can fit a GLM."**
A competitor can copy the model in a weekend. They can't copy a dated public track record, the pre-registered protocol, the vintage-correct adapters, or the approval and audit workflow a hospital signs off on. That track record grows every week we run.

## Bonus: likely curveballs
- *"Is this season unusual?"* DoH says activity is similar to the previous two seasons. NABD's value is in normal-but-variable years, not crises.
- *"Do you use any patient data?"* No. Aggregates only. Adapters reject person-level fields; there is a test for it.
- *"Conflict of interest? MBZUAI is a co-creator."* No conflict clause in the T&C. Institutional permission is our responsibility, and ⟨confirm status⟩.
