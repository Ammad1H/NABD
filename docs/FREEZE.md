# Protocol freeze record

| Item | Value |
|---|---|
| File | docs/PROTOCOL.md (v1.0) |
| Git commit containing the frozen protocol | `ac169016b59e284056b646f1b9661c4b4d24d78a` |
| SHA-256 of docs/PROTOCOL.md | `2846533f0a60d640d8a06dd57f828b76d370dda0a85a6779b37b4e360c26fe4c` |
| Frozen at (UTC) | 2026-11-08T06:47:00Z |
| FluSight hub commit used | `d03574028ece110013c6284d3012ac4bef03ded7` |

At the time of this freeze, no test-season (2024/25, 2025/26) score of any NABD model has been computed.
For a public timestamp, the team should push this repo (or post the SHA-256 above) before results are shown.
Later changes are allowed only via docs/DEVIATIONS.md.

## Addendum (round 2, 8 Nov 2026)
- **Prior exposure:** before this freeze, probes touched the test seasons (see DEVIATIONS D5). No NABD model was scored on them, but the point-model family and the D3 alert thresholds were chosen with that exposure.
- **Anchoring:** this freeze is an *internal pre-registration in local git* (single author, commits 06:43–07:04Z on 8 Nov). Nothing was pushed or externally timestamped before results existed. Any public anchor (GitHub push, OSF or Zenodo, FluSight PR) post-dates the results and must be described that way. Future protocols (v2, the live ledger) must be externally anchored **before** issuing.

## UAE track (data/UAE workstream, round 2)
- **NABD-UAE-v1 frozen as-is** for the prospective public ledger (judges' fix: "freeze v1 as is"). Code: uae/models.py at commit da045ee (sha256 e7a2843c6e6128a0…). v1 was designed with all four UAE seasons visible; its LOSO numbers are **retrospective, design-stage, not pre-registered** (audit M9).
- **PROTOCOL-UAE-v2 v1.0 locked** 2026-11-08T12:03:43Z (self-attested, local): `docs/LOCK-UAE-v2.json` (kit prereg.lock; plan + 8 code files + config + data manifest), Merkle root `f745efc2c618c7d6…`. Anchorable manifest `docs/lock_uae_v2/MANIFEST.sha256`, Merkle root `5ad8e85e7a609653…`. Committed before any v2 score. `uae/backtest_v2.py` calls `assert_locked` and refuses to score otherwise.
- **External anchoring: NOT done.** OpenTimestamps calendars and freetsa.org are blocked from the build sandbox (tested 2026-11-08T12:03:43Z). The user must run `vendor/nabd_v2_kit/scripts/anchor.sh docs/lock_uae_v2/MANIFEST.sha256` locally and push; until then the lock time is self-attested and must be described that way.
