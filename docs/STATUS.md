# NABD status, 14 Nov 2026 (final stretch)

**Where it stands.** The prototype runs end to end from a clean checkout: `pip install -r requirements-dev.txt`, `pytest -q` (145 tests pass, none skipped, with the CDC hub cloned by `python -m eval.run_all --fetch`), `streamlit run app/streamlit_app.py`. Submission is due 20 Nov.

| Item | State on 14 Nov |
|---|---|
| S1 borrowed-strength test (the science) | **Done, primary MET**: pooled model vs own-record model 0.767 (0.681–0.832) on 18 held-out countries (`results/pool/SUMMARY.md`; TECHNICAL §6.4) |
| S2 Gulf decision replay | Done, post hoc (`results/replay/SUMMARY.md`) |
| S3 Start-here landing and Season Replay page | Done |
| S4 decision replay of the pooled model on the held-out countries | Done, post hoc (DEVIATIONS V2; `results/replay/pool/SUMMARY.md`): better than the own-record model, not distinguishable from last week carried forward |
| Live ledger | R0/R1 issued 8 Nov on data through 2026-W44. **WHO had not published W45 on 14 Nov** (official API checked), so 0 weeks are scored and no new round is due. Next: `python -m ledger.weekly --fetch --with-pool` once W45 appears |
| Outside anchoring, public repo, deployed app | **Not done** (user-only steps below). Every lock and ledger time is still self-attested |
| Deck (Slides artifact) and video | Not yet synced with S1/S4; `pitch/deck-script.md` slide 7b and `pitch/qa.md` carry the wording |
| Portability fixes (14 Nov) | `scikit-learn` and the bulletin packages added to `requirements-dev.txt`; bulletin fonts fall back to matplotlib's DejaVu; deprecated pandas calls removed; leakage tests skip cleanly without the hub clone |

The round-4 gate table and the user-only steps below are unchanged except where noted.

---

## Gate table after build round 4 (ops & integrity), 2026-11-08

Gate verdicts take the R3 audit (docs/REVIEW-R3-audit.md) and apply the round-4 ops changes. Pitch and app work from the other round-4 workstreams may move G8 and G9 further; re-check them with `scripts/prepare_public_repo.sh` (banned-claim scan).

| Gate | Status | Evidence / what changed in round 4 |
|---|---|---|
| G1 Protocol integrity | **PARTIAL** | All three protocols (US, UAE-v2, GCC) are committed and locked before their results (R3 audit). **They are still self-attested.** `scripts/anchor_all.sh` stamps everything in one go once you run it (docs/PUBLISH.md §4). Disclosures C2 and C3 have been appended. |
| G2 Reproducible pipeline | PASS | `run_all` now **enforces the hub pin** (C1). The SUMMARY Round-2 section is **generated** and tested against the tables (C4). The league table recomputes or says it did not (C5). |
| G3 Primary endpoint honest | PASS | NOT MET, 1.22 (1.01–1.52); unchanged. |
| G4 UAE track | PASS | v1 forward-in-time parity; v2 no better than v1; both reported. |
| G5 Working app | PASS | Root `requirements.txt` and `.streamlit/config.toml` are ready for Streamlit Cloud (PUBLISH §5). |
| G6 Tests | PASS | 147 tests pass (round 5). New: hub pin (3), GCC future-perturbation with a positive control (3), SUMMARY generation (1), FluSight validator (4). |
| G7 Evidence | PASS | unchanged |
| G8 Pitch | PARTIAL | Pitch workstream. Placeholders remain (team name, repo URL, anchor date). |
| G9 Honesty | **PARTIAL** | Registration fixed (coordinator). The `prepare_public_repo.sh` scan still finds overclaims in **docs/SPEC.md** (old concept spec: "publicly timestamped", "fusing … ED, geospatial … signals", "calibrated") and **research/positioning.md** ("Nobody publishes…", "every forecast is published"). Fix or mark these as superseded **before the repo goes public**. |
| G10 Alert metrics | PARTIAL | The US metrics are diagnostic (D5). The UAE "3/3 onsets" comes from the retired LOSO design. |
| G11 Explainability | PASS | |
| G12 GCC out-of-sample | PASS | Influenza primary met. Data verification is **spot-check only** (C2); the full official re-pull is PUBLISH §1. |
| G13 Diagnostics | PASS | |
| G14 Card consistency | PASS | |

## What only you (the user) can do, in order. Details in docs/PUBLISH.md
1. `python -m adapters.gcc_verify`: full official WHO check of the GCC data (blocked in the sandbox).
2. `scripts/prepare_public_repo.sh`, then `gh repo create … --public --push`.
3. `scripts/anchor_all.sh`, commit the `.ots`/`.tsr` files, push; run `ots upgrade` a few hours later. Optional: a Zenodo DOI.
4. Deploy the app on Streamlit Community Cloud. It is a public, ephemeral demo, so the audit log isn't real records.
5. Optional: `scripts/flusight_wednesday.sh 2026-11-14` on **Wed 11 Nov**, after the hub data update. Fill the metadata placeholders, keep `designated_model: false`, and open a PR with docs/FLUSIGHT-PR.md.
6. Only after 2–3: change "not yet public" to "public at ⟨URL⟩, externally timestamped ⟨date⟩" in pitch/ and the app.
