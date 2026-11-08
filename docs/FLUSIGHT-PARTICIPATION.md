# Can NABD submit live forecasts to the CDC FluSight hub? (round-2 note, 8 Nov 2026)

**Short answer:** Very likely yes. The hub README states no nationality or affiliation restriction, and a non-US academic team already submits (University of Guelph, Canada: `model-output/UGuelph-CompositeCurve`, `UGuelphensemble-GRYPHON`). Submission is a GitHub pull request that runs automated validation. **This is the user's decision. Nothing has been submitted.** Questions go to the CDC FluSight team at flusight@cdc.gov, the contact in the hub README.

Sources: the README, `model-output/README.md`, `model-metadata/README.md` and `hub-config/model-metadata-schema.json` of `cdcepi/FluSight-forecast-hub`, read at pinned commit `d035740…` on 8 Nov 2026.

## What the hub requires (2026/27 season)
- **Challenge period:** 7 Oct 2026 to 26 May 2027.
- **Deadline:** every **Wednesday 11 PM US Eastern** (Thursday 08:00 GST). The `reference_date` is the following Saturday.
- **Primary target:** `wk inc flu hosp`, quantile forecasts for horizons 0–3 (the epiweek ending on the reference date and the 3 following weeks). Horizon −1 is optional and unscored. Values must be **integers**, using the 23 standard quantile levels.
- **Locations:** national plus 50 states, DC and PR. Partial location or horizon coverage is allowed.
- **Optional targets:** ED-visit proportion, rate-trend categories, peak week and peak incidence. All other targets are optional.
- **Files:**
  - forecasts: `model-output/<team>-<model>/<reference_date>-<team>-<model>.csv` (or parquet);
  - metadata: `model-metadata/<team>-<model>.yml`.
  - Team and model abbreviations: letters, digits, `_` or `+` only; no hyphens; at most 15–16 characters.
- **Required metadata fields:** team_name, team_abbr, model_name, model_abbr, model_contributors (name, affiliation and email for each), license (one of CC0-1.0, CC-BY-4.0, …), designated_model, data_inputs, methods (≤200 characters), methods_long, ensemble_of_models, ensemble_of_hub_models, website_url.
- **Ensemble designation:** `designated_model: true` makes a model eligible for the CDC ensemble. Teams may designate up to two methodologically distinct models.

## What is prepared here (drafts, not submitted)
- `results/flusight_draft/NABD-v1.yml`: metadata draft with placeholders the user must fill: team name/abbr, contributor names and emails, repo URL. We recommend `designated_model: false`, because v1 did **not** meet non-inferiority against the FluSight-ensemble (results/SUMMARY.md), so offering it to the CDC ensemble would be inappropriate.
- `results/flusight_draft/2026-11-14-NABD-v1.csv`: a **draft** for reference date Sat 14 Nov 2026, due Wed 11 Nov 23:00 ET. It comes from **frozen v1** (models/config.yaml) using the newest vintage in our pinned clone (as_of 2026-11-04, data through 2026-10-31), so it is **one week stale**. 53 locations × horizons 0–3 × 23 quantiles, integer values, quantiles non-decreasing. **Regenerate it on Wednesday after the hub's target-data update.** Do not submit this stale draft.

## Steps if the user decides to submit
1. Fork `cdcepi/FluSight-forecast-hub` on GitHub.
2. Fill the metadata placeholders. Copy the file to `model-metadata/<team>-<model>.yml`.
3. Each Wednesday, after the hub's target data update (around midday ET):
   - pull the hub (`git -C external/hub pull`, unpinned, for the live round);
   - regenerate the forecast with the frozen v1 config:
     `python -m eval.flusight_round --reference-date <Saturday> --team <team> --model <model>`. It writes a hub-format file with integer values and checks that quantiles never cross. It prints the vintage used and how many weeks stale it is, plus the file's SHA-256.
   - copy the file to `model-output/<team>-<model>/<reference_date>-<team>-<model>.csv`;
   - open a pull request and wait for the validations to pass.
4. Hash each submitted file into the NABD public ledger, so the CDC hub's timestamp (merged PR) and our own record corroborate each other. A merged PR on the CDC's repository is an outside timestamp the team does not control.

## Why it is worth doing (and the caveat)
- **For:** the hub publicly timestamps and independently scores every submission. That is the strongest "held to the CDC's standard in public" evidence a student team can get. Only about one or two scored rounds (14 and 21 Nov reference dates) would exist before judging ends on 30 Nov.
- **Caveat:** v1's retrospective record says it will probably score worse than the CDC ensemble. That is fine to show only if presented as accountability, not as a performance claim. Do not submit a model that has not been locked (a v2 must be pre-registered first; see docs/PREREG-US-V2.md).
