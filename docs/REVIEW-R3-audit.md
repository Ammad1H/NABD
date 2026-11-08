# REVIEW R3: Integrity and reproducibility audit (independent)

Auditor: independent reviewer agent, 8 Nov 2026 (UTC). Repo HEAD audited: `6993236`. FluSight hub pin: `d03574028ece110013c6284d3012ac4bef03ded7`.
This file is the only file written to the repo. All reruns were done in a scratch clone (`/tmp/r3`, hub symlinked). Audit scripts are in `/tmp/r3audit/` and were not committed.

## 0. What I ran and what held up

| Check | Result |
|---|---|
| **US lock order** (git) | `ac16901` PROTOCOL (06:47:00Z) → `fd8608b` config (06:56:04Z) → `e6333d1` first result (06:58:01Z). PROTOCOL.md still has a single commit and SHA-256 `2846533f…` (= FREEZE.md). |
| **UAE v2 lock order** | `da045ee` protocol + code (12:03:09Z) → `b2ee6ca` LOCK (12:03:43Z; LOCK-UAE-v2.json mtime 12:03:10). The earliest v2 output file has mtime 12:04:19 (`results/uae/v2/tables/scores_long_common.csv`) and the last 12:06:39. That fits a 2.5-minute run started after the lock (my rerun took 2 min 27 s). Locked files are unchanged since the lock. |
| **GCC lock order** | `edee709` prereg + code (12:08:46Z) → `91005ce` LOCK (12:08:47Z) → mirror clone (reflog epoch 1794139780 = 12:09:40Z) → `/tmp/flunet_mirror/gcc_extract.csv` (12:09:52) → `data/raw/flunet_gcc.csv` (12:10:18) → `d013228` data commit (12:10:18Z) → `63611e6` result (12:12:02Z). The GCC-locked files are byte-unchanged since `91005ce`, and `uae.gcc --score` passes `assert_locked`. |
| **GCC exposure search** (filesystem) | `find / -xdev` for FluNet, VIW_FNT and GCC files, plus a grep for OMN/QAT/SAU/BHR/KWT/Oman/Qatar/Saudi/Bahrain/Kuwait in `/home/claude/fhdic/loop`, `nabd-pack`, `data/` and `/tmp`. No GCC country data exist anywhere with an mtime before 12:09:40Z. Text mentions found: loop/R1-B (API coverage note), R3/R4 (a Qatar University MoCA paper, unrelated) and research/positioning.md:86 (Saudi ICU news for Oct 2026, a season outside the test). Before the lock, `/tmp/gcc_selftest/` (12:08:16) holds **ARE-only** output. See finding 13. |
| **GCC data fidelity** | `data/raw/flunet_gcc.csv` (sha256 `24f3445a…`) equals the mirror's `VIW_FNT_20261003.csv` (sha256 `2ad479fa…`) filtered to the 5 countries, ISO_YEAR ≥ 2015 and the 7 columns: 2431/2431 rows, 0 differing cells. The mirror's ARE rows match our WebFetch-sourced `flunet_are.csv` on **419/419 rows, 0 differing cells** (independently confirmed). |
| **`python -m eval.run_all --cached`** (115 s) | Every `results/tables/*`, `results/figures/*`, `results/forecasts/**` and `alerts_summary.json` file is **byte-identical**, including the D7 league table rebuilt from the hub. `summary.json` differs only in key order. `SUMMARY.md` **loses its 61-line Round-2 section** (finding 14). |
| **`python -m uae.backtest --cached`** (12 s), **`python -m uae.backtest_v2 --cached`** (2 min 27 s), **`python -m uae.gcc --score`** (67 s) | Every output under `results/uae/**` and `results/gcc/**` is **byte-identical**. |
| **`pytest -q`** | **120 passed**; vendored kit tests 26/26 passed. |
| **Headline numbers vs regenerated files** | US 1.223 (1.011–1.521) NOT MET; S1 0.816; league 7/21 (0.693) and 19/25 (0.997); national share 46.0%; excl. national 1.198; UAE forward v1/persistence 1.002/1.002; v2/v1 LOSO 1.059 (1.016–1.111); GCC flu 0.914 (0.843–0.983) MET, RSV 0.798 (0.719–0.894), wins 9/12 and 9/10. **All match** the three SUMMARYs, TECHNICAL.md and the pitch. |
| **GCC leak test** (`/tmp/r3audit/leak_gcc.py`) | 2,112 cases (OMN, QAT and SAU × flu/RSV × every scored season × 6 random origins × 4 models × 4 horizons). Every value after the origin (y, z, positives, specimens, non-sentinel) was scaled and shifted at random. **0 forecasts changed.** Positive control: perturbing y at the origin changes the forecast. Training sets are the country's own qualifying seasons before S, excluding 2020. There is no pooling with UAE data and no cross-season normalisation (per-week logit only). Climatology, persistence deltas and analog pools come from training seasons only. **No leak.** |
| **UAE v2 and forward-in-time design** | `fwd_train` = seasons < test. v2 `_row` blanks every surveillance column after the origin. NS uses t−1. Calendar features are shifted target-week values from the school calendar (verified=True rows, announced before the season; the 2022/23 winter break was reported 5 Dec 2022) and a tabular Ramadan calendar. Known-future holds. The existing tests (`test_v2_forecast_unchanged_when_future_surveillance_altered`, `test_calendar_features_are_known_future_only`) pass. **No leak** found. |
| **GCC robustness** (`/tmp/r3audit/gcc_sens.py`) | Flu: leave-one-country-out 0.904–0.929; by horizon −1/0/1/2 = 0.999/0.958/0.898/0.855; two-stage (country → season) bootstrap 0.841–0.984; within-country-season moving block (L = 4) 0.855–0.985. **The flu verdict is robust.** RSV: two-stage bootstrap **0.712–1.026** (crosses 1); SAU RSV 1.088 (see finding 9). |
| **App** (Streamlit AppTest, all 10 pages) | 0 exceptions. The NOT MET verdict is visible (R2 C3 fixed). |

## 1. Gate table

| Gate | Verdict | Evidence |
|---|---|---|
| G1 Protocol integrity | **PARTIAL** | All three locks precede their results in git and in file mtimes, and the hashes verify. But every lock is self-attested in local git with no outside anchor. DEVIATIONS D8(d) claims a hub-pin fix that does not exist (finding 5). DEVIATIONS G1b carries a timestamp later than its own commit (finding 6). |
| G2 Reproducible pipeline | **PASS** (caveats) | Byte-identical tables, figures and forecasts for US, UAE v1, UAE v2 and GCC. Runtime is 2–5 min per entry point. The hand-written SUMMARY Round-2 section is not regenerated (finding 14), and the league table silently falls back to the committed CSV when hub model output and the cache are absent (finding 15). |
| G3 Primary endpoint honest | **PASS** | 1.223 (1.011–1.521), NOT MET, reproduced exactly. D6 sensitivities and D9 cross-check reproduced. |
| G4 UAE track | **PASS** | LOSO (n = 4) and forward-in-time are reported. R0 and R1 hashes verify (`sha256sum -c`), and the Merkle manifest is present. R0 and R1 are `public: false`. |
| G5 Working app | **PASS** | 10/10 pages render with no exception. Bilingual card, audit, ledger and feed-removal pages are present. Docker was not built in this audit. |
| G6 Tests | **PASS** | 120/120 plus kit 26/26, with leak-injection positive controls for US, UAE v1 and UAE v2. Gap: no future-perturbation test for the GCC scorer (finding 16). |
| G7 Evidence | **PASS** | Unchanged from R2; Tawam figures were verified in R2. |
| G8 Pitch | **PARTIAL** | Real numbers are filled in. But ⟦IF BUILT⟧ markers remain on items already built, one screenshot path does not exist, and the team placeholders are still open (finding 17). |
| G9 Honesty | **FAIL** | False statements in the registration and TECHNICAL.md: the ledger is called "published" and "public"; the GCC data are said to be "verified row-for-row". "Blind" is used without the caveats the team's own F12 requires. "Nobody publishes a forecast" lacks the "to our knowledge" that E8 requires. "Fewer false alarms" is mislabelled. UAE alert claims rest on the retired LOSO design (findings 1–4, 7, 8). |
| G10 Alert metrics | **PARTIAL** | US and UAE are computed and labelled diagnostic. The UAE alerts come only from the LOSO design that trains on later seasons, and "false alarm"/"precision" are misdescribed (findings 7, 8). |
| G11 Explainability | **PASS** | Exact linear contributions for v1 (live) and v2 (`results/uae/explain/`, the sum-to-median test passes). The refit ablation and missing-feed tests are real. |
| G12 GCC holdout | **PASS** (with disclosed caveats) | Locked before download (as far as git, mtimes and the reflog show). Inclusion is applied mechanically, and every country is reported. No leak. The data are WHO's export via a mirror; extraction is verified exactly and the ARE overlap is exact. The official-API check is 23 rows via WebFetch, not a full re-pull (finding 2). |
| G13 Phase diagnostics | **PASS** | D10 tables and figures were reproduced byte-identical and declared before computing (`712341c`, before `0c9e27f`). |
| G14 Card consistency | **PASS** | `tests/test_app_cardcheck.py` (over-call, under-call, contradictory-band, live-round cards) passes, and the card is gated in the app. |

## 2. Status of R2 audit findings

| Status | R2 findings |
|---|---|
| Fixed | C1, C2, C3; M4 (D5); M6 (D6); M7 (E1 reinterpreted, banned); M8 (D6 L=4/6); M9 (U1, LOSO retired); M11 (explain + ablation); M12 (UAE alerts, see finding 7); M13 (stop list); m17, m18, m19 (U4); m23 (screenshots retaken); m25 and m26 (D8b/c) |
| Disclosed but open | M5: no outside anchor yet; FREEZE addendum is honest |
| Not fixed despite being logged as fixed | **m14** (hub pin): finding 5 |
| Still open | m16: `eval/tune.py:135` note is still hard-coded. m20: no later-vintage (revision) injection test. m22: `pitch/outreach.md:17` still cites "2.9% to 16%" without the 2020–21 pandemic caveat. m24: `flunet_are.csv` is still WebFetch-sourced, although the mirror now corroborates it at 419/419. **m27: `docs/SPEC.md:80` still says "Most competing 06 entries are simulated; ours is real, pre-registered and timestamped" and lists "Chronos-2 as an ensemble member, ablated".** |

## 3. Findings

### CRITICAL

**1. CRITICAL: the registration, TECHNICAL.md, deck, video and one-pager say forecast rounds are "published" in a "public" record. Nothing has been published or anchored.**
- **Where:**
  - pitch/registration.md:14 ("a public, tamper-evident record"), :20 and :37 ("Every forecast round is hashed and published before its outcome exists"), :25 ("a tamper-evident public record");
  - docs/TECHNICAL.md:13;
  - pitch/deck-script.md:79;
  - pitch/video-script.md:18 ("hashed and published … so our track record can't be rewritten");
  - pitch/one-pager.md:26 (row "**Public** forecast ledger");
  - pitch/qa.md:163 ("a dated, outside-anchored track record").
- **Evidence:**
  - Both ledger metas say `"public": false`, "Not public until committed, pushed to a public repo, and the hash is posted" (ledger/2026-11-08T0651Z_NABD-UAE-v1.meta.json, …1212Z…).
  - registration.md:63 itself says "not yet published or externally anchored".
  - FREEZE.md: "External anchoring: NOT done".
  - All commits are by a single local author (`NABD build <nabd-build@local>`). A local git history can be rewritten, so "can't be rewritten" is false today.
  - The registration is due 10 Nov and becomes a declared fact to the organiser.
- **Fix:**
  - Either push the repo and anchor `ledger/rounds/2026-11-08T1212Z_R1/MANIFEST.sha256` (ledger/ANCHOR.md) **before** submitting the registration,
  - or reword everywhere to: "Every forecast round is hashed and committed before its outcome exists; the record will be public and externally timestamped from ⟨date⟩."
  - Change one-pager:26 to "Forecast ledger (local; public from ⟨date⟩)", and qa:163 to "an outside-anchored track record (from ⟨date⟩)".
  - Add "published/public" to the claims-ledger as status P until the anchor exists.

**2. CRITICAL: the GCC data are said to be "verified row-for-row against the official WHO API". Only 23 GCC rows were checked, through a channel the team itself calls untrustworthy.**
- **Where:**
  - pitch/qa.md:40 ("checked row-for-row against the official WHO API");
  - docs/TECHNICAL.md:81 ("verified row-for-row … 7/7 OMN rows");
  - weaker overstatements of the same claim: pitch/registration.md:74, pitch/assumptions-limitations.md:38, results/gcc/SUMMARY.md:3, research/claims-ledger.md:28 (A10).
- **Evidence:**
  - DEVIATIONS G1/G1b: 7 + 16 = **23 of 2,431** GCC rows were checked against xMart through WebFetch. G1b itself says WebFetch "passes content through a summarising model, so it is not a trustworthy channel for bulk data".
  - No raw WebFetch responses are stored.
  - `adapters/gcc_verify.py` (the real full check) has never been run. xMart is blocked (I confirmed CONNECT 403).
  - What *is* strong is the 419/419 ARE overlap between the mirror and an independently obtained file, which I reproduced exactly.
  - TECHNICAL.md:81 is also stale ("7/7"; G1b says 23/23).
- **Fix:** replace with "WHO's full export (3 Oct 2026) obtained via a public GitHub mirror; it matches our independently fetched UAE rows exactly (419/419) and 23/23 spot-checked GCC rows; a full official re-pull (`python -m adapters.gcc_verify`) is pending". Better: run `gcc_verify` on a laptop before 10 Nov, commit its stdout and the xMart CSV hash, and only then say "verified against the official API (full re-pull, ⟨date⟩)".

### MAJOR

**3. MAJOR: "blind" and "pre-registered" appear in the registration title and summaries without the caveats the team's own banned-claims list requires (F12).**
- **Where:**
  - pitch/registration.md:11 (title "Tested Blind Across the Gulf"), :20, :25, :30, :39;
  - deck-script.md:14, :19, :66 ("data nobody on the team had seen");
  - video-script.md:17;
  - demo-script.md:15;
  - one-pager.md:1;
  - app/streamlit_app.py:69 (sidebar "Blind GCC test … locked before download") and :744.
- **Evidence:** research/claims-ledger.md:116 (F12) bans "Blind" without "(self-attested lock; v1 chosen after UAE results)". A sceptical reviewer can say:
  - (a) the lock is a local commit made 1 s after the plan commit and 91 s before the data, with no outside anchor;
  - (b) "blind" in forecasting usually means prospective, but this is a retrospective test on revised data;
  - (c) the primary method was chosen after seeing UAE forward-in-time parity;
  - (d) "nobody on the team had seen" the data is asserted, not shown. PREREG §1 itself says "No, as far as the records show", and human team members' prior exposure (e.g. WHO dashboards) cannot be checked from the repo.
- **Fix:**
  - Title: "…, With a Pre-Specified Out-of-Sample Test Across the Gulf".
  - Body: "In an out-of-sample test on Oman, Qatar and Saudi Arabia, with the plan locked (self-attested, local git) before their data were downloaded, …".
  - Replace "nobody on the team had seen" with "that our records show no one on the team had used".
  - Apply the same wording to the app sidebar, About page, deck, video and demo. Anchor the GCC lock now and say "anchored ⟨date⟩, after the result".

**4. MAJOR: "nobody publishes a forecast" and "The UAE publishes no respiratory forecasts" lack the "to our knowledge" that claims-ledger E8 requires.**
- **Where:**
  - pitch/registration.md:14, :25, :30;
  - deck-script.md:14 and :21;
  - demo-script.md:11;
  - app/streamlit_app.py:738–739 ("nobody in the UAE publishes a forecast").
- **Evidence:**
  - research/claims-ledger.md:89: "absence of evidence; always say 'to our knowledge'".
  - The positioning source supports only "exact data for flu cases … not available" [S6] and that UMOC runs an AI early-warning layer [S13]. An Abu Dhabi DoH judge may know of internal forecasting.
  - The stop list also forbids implying that UMOC or Tableegh are inadequate (positioning.md:189).
- **Fix:** "…and, to our knowledge, no public forecast exists" (the one-pager.md:11 wording is already correct; copy it).

**5. MAJOR: DEVIATIONS D8(d) says hub-pin enforcement was added. It wasn't (R2 m14 is still open).**
- **Where:** docs/DEVIATIONS.md (D8(d): "run_all now fails if `external/hub` is not at the pinned commit"); eval/run_all.py:22–28 and :42–43.
- **Evidence:**
  - `fetch_hub()` still runs `checkout HUB_SHA` with `check=False`, and there is no `rev-parse` assertion anywhere in the repo (grep).
  - With `--cached` and an existing hub, `fetch_hub()` is never called, so a hub at any commit is used silently. Truth and FluSight forecasts would change without warning.
  - A deviation log that records a fix that doesn't exist undermines every other entry.
- **Fix:**
  - In `run_all.main()`, unconditionally run `subprocess.check_output(["git","-C",hub,"rev-parse","HEAD"]).strip() == HUB_SHA`, else `sys.exit(…)`. Set `check=True`.
  - Add a test that monkeypatches HUB_SHA and expects failure.
  - Amend D8(d) by appending a dated correction row; do not edit the original.

**6. MAJOR: DEVIATIONS G1b records a check "re-checked 8 Nov 18:40 UTC" in a commit made at 18:30:36 UTC.**
- **Where:** docs/DEVIATIONS.md, G1b row, added in `06b3426` (committer date 2026-11-08T18:30:36Z).
- **Evidence:**
  - The text names a time ten minutes after the commit that introduced it. Either the time is wrong or the commit date was set by hand. Both are damaging in a document whose whole value rests on self-attested timestamps.
  - G1b also calls WebFetch untrustworthy for bulk data, yet uses WebFetch for the 16 "live" rows, with no stored responses.
- **Fix:** append a dated correction row giving the real check time and how it was obtained. Store the raw responses for the 23 spot-checked rows under `data/raw/verify/` with their URLs and fetch times. Never write a time you did not observe.

**7. MAJOR: "fewer false alarms" and "precision (how often an alert is real)" misdescribe the US alert results. Every rule had 0 false alarms at 3/100k.**
- **Where:**
  - deck-script.md:105 (heading "Fewer false alarms");
  - qa.md:110 ("share of alerts followed by a real onset");
  - app/streamlit_app.py:347;
  - demo-script.md:22;
  - TECHNICAL.md:265.
- **Evidence:**
  - results/tables/alerts_us.csv: `false_alarm_loc_seasons` = 0 for NABD, the CDC ensemble and census, in both seasons, at T = 3.
  - The PPV gap comes entirely from **late** first alerts (issued after the onset week). My breakdown of alerts_us_detail.csv at T = 3, 2024/25:

    | Rule | Timely alerts | Late alerts | No alert |
    |---|---|---|---|
    | NABD | 17 | 9 | 25 |
    | CDC ensemble | 9 | 13 | 29 |
    | census | 28 | 19 | 4 |

  - NABD's higher PPV coexists with fewer timely detections than the census rule (sensitivity 0.33 vs 0.55).
  - The stop list allows "fewer false alarms (PPV) only as far as results/ supports it" (positioning.md:178). The data do not support it.
- **Fix:**
  - Rename to "fewer late alerts": "Of NABD's first alerts, 65% came before onset (CDC ensemble 41%), but NABD alerted in fewer locations; the census rule caught more onsets in time (2024/25: 28 vs 17 of 51)."
  - Drop "false alarm" wording from the deck, Q&A and app.

**8. MAJOR: the UAE alert claims ("3/3 onsets caught, 0 false alarms") come from the retired LOSO design.**
- **Where:**
  - deck-script.md:105;
  - qa.md:115;
  - demo-script.md:22;
  - research/claims-ledger.md:71 (D4);
  - assumptions-limitations.md:67.
- **Evidence:**
  - `uae/backtest_v2.py` computes the alerts on `sc`, the LOSO scores, where models train on *later* seasons.
  - The team retired LOSO skill numbers as headline evidence for exactly that reason (BUILD-SPEC v1.6; claims-ledger D9).
  - No forward-in-time alert table exists.
  - n = 3 onsets, and the thresholds came from probes that saw these seasons (U2).
- **Fix:** compute the alert table on the forward-in-time scores (`fsc`). Log the addition as a UAE deviation before computing, and label it exploratory. Until then, drop the UAE alert line from the deck, demo and Q&A, or label it "LOSO (trains on later seasons), n = 3".

**9. MAJOR: the RSV "20%" sits in the headline sentence beside the pre-registered result, but it is secondary and fragile.**
- **Where:**
  - registration.md:20, :30, :39;
  - deck-script.md:70 and :74;
  - video-script.md:17;
  - demo-script.md:15;
  - one-pager.md:25.
- **Evidence:**
  - PREREG-GCC §6–7: the success criterion is flu only; RSV is secondary.
  - A two-stage (country → season) bootstrap gives RSV **0.712–1.026**; the registered country-season bootstrap gives 0.719–0.894 and ignores clustering within 3 countries.
  - SAU RSV lost (1.088), only 2 SAU RSV seasons were scored, and RSV 95% coverage is 0.83.
  - Flu, by contrast, is robust: two-stage 0.841–0.984, leave-one-country-out 0.904–0.929.
- **Fix:** "…cut error by about 9% for influenza (pre-registered primary, met); RSV, a secondary outcome, 20% (intervals too narrow outside the UAE)." Add the two-stage bootstrap as a labelled sensitivity in results/gcc and in DEVIATIONS (G2).

**10. MAJOR: "calibrated" is used unqualified in the registration and TECHNICAL.md, but the project's own results show miscalibration.**
- **Where:**
  - registration.md:14, :20, :25, :30, :37;
  - TECHNICAL.md:13;
  - video-script.md:15;
  - one-pager.md:16;
  - app About (streamlit_app.py:739).
- **Evidence:**
  - GCC RSV 95% coverage 0.83 (results/gcc/tables/coverage.csv).
  - US 50% coverage 0.48 and 95% coverage 0.92 (acceptable).
  - US relative WIS by as-of phase shows under-prediction as the largest component (42%).
- **Fix:** use "probabilistic forecasts with published coverage" or "calibration checked and reported (95% coverage: US 0.92; Gulf flu 0.96, RSV 0.83)".

**11. MAJOR: the registration's "up to three weeks ahead" and the "+0.5/+1.5/+2.5 wk" labels in the deck, app and TECHNICAL.md disagree with each other and with the ledger.**
- **Where:**
  - registration.md:14, :20, :25, :30, :37 ("up to three weeks ahead");
  - TECHNICAL.md:102 and qa.md:141 ("every ledger row carries that label");
  - deck-script.md:50;
  - assumptions-limitations.md:7.
- **Evidence:**
  - R0 and R1 metas label the horizons "+1.0 / +2.0 / +3.0 wk after issue" (ledger/*.meta.json), because live issue was L_end + 7 days.
  - The backtests (and therefore all skill numbers) assume issue at L_end + 11 days, i.e. +0.5/+1.5/+2.5.
  - RUNBOOK admits R0/R1 "predate the issue-relative convention".
  - Also, the nowcast target week (ending 2026-11-08) had not ended at issue 06:51Z, despite the label "already ended at issue".
- **Fix:**
  - Say "nowcast to +2.5 weeks after issue (skill measured at an 11-day lag)" in the registration.
  - Correct TECHNICAL.md:102 and qa.md:141 to "rounds from R2 on carry that label; R0/R1 carry +1/+2/+3".
  - Fix the "already ended" label logic for issue dates inside the target week.

### MINOR

**12. MINOR: the "registered cluster CI" column in the SUMMARY Round-2 table does not equal the registered CIs.**
- **Where:** results/SUMMARY.md, Round-2 table; results/tables/sensitivity_block_bootstrap.csv.
- **Evidence:**
  - S1: 0.654–1.028 vs the registered 0.655–1.023 (endpoints.csv).
  - S3 2024/25: 0.886–1.244 vs 0.885–1.255.
  - S3 2025/26: 1.081–2.012 vs 1.093–2.026.
  - Only PRIMARY matches. The resampling scheme differs from `eval/score.py`.
- **Fix:** take the column from endpoints.csv, or relabel it "cluster CI (round-2 resampler)".

**13. MINOR: the GCC exposure declaration omits two items known before the lock.**
- **Where:** docs/PREREG-GCC.md §1.
- **Evidence:**
  - (a) The `--selftest` run on ARE at 12:08:16 printed a full primary readout (ARE: 0.887, CI 0.63–1.188, "NOT MET"). PREREG.md was last modified at 12:08:37, after that output.
  - (b) research/positioning.md:86 (committed 12:00:44, before the lock) cites Saudi Oct-2026 ICU news. That season is outside the test, so it does not affect the result. But the declaration says the repo search found only the R1 note and judge text.
- **Fix:** append both to DEVIATIONS (GCC section) as disclosures. PREREG cannot be edited without breaking the lock.

**14. MINOR (G2): the results/SUMMARY.md Round-2 section is hand-written and is deleted by `make all`.**
- **Evidence:** commit `b155a1c` added it by hand. `eval/round2.update_summary` writes only summary.json. My rerun removed 61 lines (league 7/21, 19/25, D6, D10, REV), which the pitch cites as `results/SUMMARY.md (D6, D7)`. The numbers do match the regenerated tables.
- **Fix:** generate the section in `round2.update_summary`, and add a test that `run_all` leaves SUMMARY.md unchanged.

**15. MINOR: the league table can "reproduce" without recomputing.**
- **Where:** eval/round2.py:536–540 and :262–265.
- **Evidence:**
  - If hub model output is absent and `data/cache/` is empty (a clean clone after a sparse `fetch_hub`), the code reads the committed `league_table.csv` and prints nothing.
  - If the cache exists, NABD's league WIS comes from the stale pickle, not the current forecasts.
- **Fix:** print "LEAGUE NOT RECOMPUTED (using committed table)" and mark it in summary.json. Key the cache on a hash of the NABD forecasts plus HUB_SHA.

**16. MINOR (G6): there is no future-perturbation test for the GCC scorer.** Only the lock-refusal test exists (tests/test_uae_v2.py:95). My `/tmp/r3audit/leak_gcc.py` (2,112 cases, 0 changes, plus a positive control) can be ported as-is on the ARE file, so the test doesn't depend on GCC data in CI.

**17. MINOR (G8): stale placeholders and wrong paths in the pitch.**
- deck-script.md:58–60 and :119, and registration.md:41–45, still mark exceedance probabilities, season shape, PILOT-DATA-SPEC, the bed-days scenario and "surge-alert metrics" as "in build". All of these exist, and the app's About page marks them REAL.
- deck-script.md:122 cites `app/screenshots/09_about.png`; the file is `11_about.png`.
- TECHNICAL.md:315 says "98 tests"; there are 120.
- registration.md:82 still has the team placeholder.
- **Fix:** sync everything to HEAD.

**18. MINOR: app text inconsistencies.**
- app/streamlit_app.py:533 says the test runs on "GCC/EMRO countries", but PREREG §3 says "Other EMRO countries are **not** part of this test".
- :796 says "FluNet about 10–11 days", but PROVENANCE measured 7 days.
- data/raw/PROVENANCE.md says "earlier winter breaks approximate (verified=False)", but every break row in uae_calendar.csv is now verified=True (U3).
- **Fix:** correct the wording.

**19. MINOR: onset-lead statements are slightly overgeneralised.**
- "Median onset lead is 0 weeks for every US rule" (deck-script.md:104, qa.md:106, assumptions-limitations.md:64) is true at T = 3 only. The census rule has 0.5 weeks at T = 2 in 2024/25.
- one-pager.md:30 "Onset lead is 0 weeks" is unqualified, while UAE flu shows +1.43 weeks for both v1 and census (alerts_uae.csv).
- **Fix:** say "at the primary threshold (3/100k)" and "US".

**20. MINOR: the Gulf generalisation is overstated.**
- one-pager.md:36 ("shown to transfer across GCC countries … make Abu Dhabi the regional hub") and deck-script.md:74 ("beat what a planner would otherwise do").
- Evidence: n = 3 countries. Two of them (OMN, QAT) use TOTAL (mixed-origin) streams, not sentinel like the UAE. Persistence is a statistical baseline, not shown to be planners' practice.
- **Fix:** "beat last-week persistence in 3 Gulf countries (9/12 flu country-seasons)"; drop "shown to transfer".

**21. MINOR: the problem framing drifts toward the stop list.**
- registration.md:30 and :35 say RSV and flu "fill Abu Dhabi's paediatric beds" or "emergency and paediatric services". There is no source for bed or ED load, and the stop list forbids ED and bed-occupancy claims and crisis framing (positioning.md:186–187).
- **Fix:** "Every winter RSV and influenza drive paediatric admissions in Abu Dhabi (e.g. 2,189 RSV admissions of children ≤5 at Tawam, 2018–22)".

**22. MINOR: R2 items still open.** m16, m20, m22 (outreach.md:17), m24, and m27 (docs/SPEC.md:80, which would be visible if the repo is made public). See §2. Fix as R2 proposed. Delete or source SPEC.md:80, which still claims Chronos-2 is an ablated ensemble member.

## 4. Judge-facing risk summary (what a sceptic will say)

1. **"Pre-registered" means a commit you made yourselves.**
   - All locks are local, single-author commits, often seconds apart (GCC plan 12:08:46 → lock 12:08:47 → data 12:10:18 → result 12:12:02).
   - The deviation log contains a time later than its own commit (finding 6) and a fix that isn't in the code (finding 5).
   - Mitigation: anchor every lock manifest now, state the anchor date as *after* results, and fix findings 5 and 6 before the repo goes public.
2. **"Blind" on revised, retrospective data, with a method picked after the UAE results.**
   - Disclosed in PREREG §1 but missing from the title and summaries (finding 3).
   - Prefer "pre-specified out-of-sample".
3. **"Data via a GitHub mirror."**
   - Defensible: the extract equals the mirror exactly, and the mirror equals an independently fetched UAE file on 419/419 rows.
   - But "row-for-row against the official API" is false (finding 2).
   - Run `adapters.gcc_verify` locally before 10 Nov.
4. **"n = 3 countries."**
   - The flu result survives leave-one-country-out (0.904–0.929) and a country-clustered bootstrap (0.841–0.984); say so.
   - RSV does not survive clustering; demote it (finding 9).
5. **"The UAE model ties persistence at home."** This is honestly stated everywhere I checked. Keep it.

## 5. Scratch artefacts (not committed)
- `/tmp/r3audit/leak_gcc.py`: future-perturbation leak test, GCC scorer.
- `/tmp/r3audit/posctl.py`: positive control and Qatar series check.
- `/tmp/r3audit/gcc_sens.py`: GCC sensitivity analyses (by horizon, leave-one-country-out, two-stage and moving-block bootstraps).
- `/tmp/r3audit/mirror_check.py`: GCC extract vs mirror, and the 419/419 ARE overlap.
- `/tmp/r3audit/apptest.py`: AppTest over all app pages.
- Scratch clone: `/tmp/r3`.
