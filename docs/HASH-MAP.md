# Commit hash map (14 Nov 2026)

Before the first push, the commit messages of six commits were edited to remove tool-attribution trailer lines. No file content changed (tree hashes are identical), but the commit hashes did. Documents in this repo that cite the old hashes refer to the new ones as follows.

| Old hash | New hash | Commit |
|---|---|---|
| f4c6195 | b182430 | DEVIATIONS V1: decision replay declared before computing |
| 218adf5 | c9ea363 | PREREG-POOL lock #1 |
| 4f805f5 | 9fffdf1 | S2 decision replay |
| b056375 | 2a004a3 | Pool: P1 declared; development-country data |
| f39e5ba | 6c9aa3b | S3 demo: landing, Season Replay page |
| 6db6928 | 123ea6a | PREREG-POOL lock #2 |

The locks themselves do not depend on commit hashes: each `docs/LOCK-*.json` holds a Merkle root over file contents, which is unchanged. All timestamps before the first push are self-attested.
