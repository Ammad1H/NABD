# Anchoring NABD's locks and ledger rounds outside the team

Local git timestamps are **self-attested**: anyone can rewrite them. A lock or a forecast round counts as "made before the outcome" only once a third party has timestamped its hash. The build sandbox cannot reach any timestamp service (OpenTimestamps calendars and freetsa.org were refused on 8 Nov 2026), so **you (Ammad) must do this on your laptop**. It takes about 10 minutes the first time.

## What to anchor (one `MANIFEST.sha256` per item; each lists file hashes plus a Merkle root)
| Item | Manifest | Merkle root |
|---|---|---|
| UAE v2 protocol lock (before v2 scoring) | `docs/lock_uae_v2/MANIFEST.sha256` | `5ad8e85e7a60…` |
| GCC pre-registration lock (before GCC download) | `docs/lock_gcc/MANIFEST.sha256` | `b52c5d5ed326…` |
| Ledger round R1 (NABD-UAE-v1 headline, v2 challenger, persistence) | `ledger/rounds/2026-11-08T1212Z_R1/MANIFEST.sha256` | `f1fffc0bc1cf…` |
| Every later round | `ledger/rounds/<UTC>_<round>/MANIFEST.sha256` | printed by `ledger.issue` |

Anchoring later than a lock was made does not backdate it: the anchor proves the files existed *no later than* the anchor time. Anchor each new round **before** its first target week is published by WHO.

## Steps (laptop with internet)
```bash
pip install opentimestamps-client               # once
cd nabd
# 1) verify that nothing changed since the manifest was written
PYTHONPATH=vendor/nabd_v2_kit python3 -m nabd_kit.ledger verify docs/lock_uae_v2/MANIFEST.json --base .
# 2) anchor: OpenTimestamps (Bitcoin) + RFC 3161 (FreeTSA)
bash vendor/nabd_v2_kit/scripts/anchor.sh docs/lock_uae_v2/MANIFEST.sha256
bash vendor/nabd_v2_kit/scripts/anchor.sh docs/lock_gcc/MANIFEST.sha256
bash vendor/nabd_v2_kit/scripts/anchor.sh ledger/rounds/2026-11-08T1212Z_R1/MANIFEST.sha256
# 3) a few hours later, complete the Bitcoin attestation
ots upgrade docs/lock_uae_v2/MANIFEST.sha256.ots   # etc. for each .ots
# 4) publish: commit the .ots/.tsr files, push to a PUBLIC GitHub repo, then create a GitHub release
#    mirrored to Zenodo (DOI) or upload the manifests to an OSF project. Post the Merkle roots publicly.
git add docs/lock_* ledger/rounds && git commit -m "Outside anchors for locks and ledger R1" && git push
```

## Weekly ledger cadence (after WHO publishes a new UAE week, usually ~7–11 days after it ends)
```bash
python3 -m adapters.flunet --fetch --save        # refresh data/raw/flunet_are.csv from WHO xMart
python3 -m ledger.score --fetch                  # score earlier rounds whose target weeks are now published
python3 -m ledger.issue --fetch --round R2       # new round: v1 headline, v2 challenger, persistence
bash vendor/nabd_v2_kit/scripts/anchor.sh ledger/rounds/<UTC>_R2/MANIFEST.sha256
git add ledger results/uae/explain && git commit -m "Ledger R2" && git push
```

## How a judge verifies
1. Clone the public repo and run `nabd_kit.ledger verify` on a manifest: every file hash matches.
2. `ots verify MANIFEST.sha256.ots` shows the Bitcoin block time; `openssl ts -verify …` checks the FreeTSA token.
3. Compare that time with the publication date of the WHO week being forecast.
