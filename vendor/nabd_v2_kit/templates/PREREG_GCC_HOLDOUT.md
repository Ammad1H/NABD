# Pre-registration: UAE v2 method, GCC/EMRO out-of-sample test

Fill every bracket BEFORE anyone downloads data for the holdout countries.
Lock with `prereg.lock`, build the manifest, anchor it (`scripts/anchor.sh`),
then publish to OSF or Zenodo. Edits after anchoring go only in section 10.

## 1. Exposure declaration
Has anyone on the team looked at FluNet data for any candidate country?
[No / Yes: who, which countries, what they saw]

## 2. What is frozen
- Code commit: [hash]; LOCK.json Merkle root: [root]
- Model: UAE v2 exactly as locked on [date], including hyperparameters
- Signals used outside the UAE: [list]. Dropped because unavailable outside
  the UAE: [e.g. UAE school calendar]. No other signal may be added later.

## 3. Data and inclusion rules (decided before download)
- Source: WHO FluNet [file or endpoint], pulled on [date], manifest hash [hash]
- Pathogens: [influenza total / A / B], [RSV where reported]
- Target: [weekly % positive, primary], [positives, secondary]
- A country-season is included if: [e.g. tests reported in >= 80% of weeks AND
  median weekly specimens >= N]. A country is included if it has [>= 4]
  included seasons.
- Candidate countries, in order: [Oman, Qatar, Bahrain, Kuwait, Saudi Arabia,
  then other EMRO], decided by the rule above, not by inspection.

## 4. Procedure
- Rolling origin, every week from [season week w0 to w1]; horizons [1-4] weeks
- At each origin the method is refitted on that country's own data up to the
  origin only. No pooling across holdout countries. [or: pre-specified pooling]
- Data are finalized FluNet values (no vintages exist); results are labelled
  "retrospective, revised data".

## 5. Comparators
- Persistence (flat baseline, `baselines.flat_baseline`)
- Tougher baseline: [seasonal climatology / auto-ETS on fourth-root scale]

## 6. Metrics and uncertainty
- Primary: relative WIS of UAE-v2 method vs persistence, pooled over included
  countries, horizons and origins (ratio of mean WIS)
- Secondary: vs the tougher baseline; per country; 50% and 90% coverage
- CI: [season-block] bootstrap, B = [2000], seed = [0]

## 7. Success criterion (confirmatory)
[Pooled relative WIS vs persistence < 1 AND 95% CI upper bound < 1]

## 8. Reporting rules
Every included country is reported, losses included, in one table. No country,
season or horizon is dropped after scoring.

## 9. Sign-off
[Names, date]. Outside anchors: [.ots file], [.tsr file], [OSF/Zenodo link]

## 10. Deviations log (empty at lock)
| Date | Deviation | Reason | Effect on interpretation |
| --- | --- | --- | --- |
