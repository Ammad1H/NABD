#!/usr/bin/env bash
# Anchor a manifest outside the team: OpenTimestamps (Bitcoin) + RFC 3161 (FreeTSA).
# Needs network. Usage: scripts/anchor.sh path/to/MANIFEST.sha256
set -euo pipefail
f="${1:?usage: scripts/anchor.sh path/to/MANIFEST.sha256}"
dir="$(dirname "$f")"

if command -v ots >/dev/null 2>&1; then
  ots stamp "$f"
  echo "OpenTimestamps proof: $f.ots (pending; run 'ots upgrade $f.ots' in a few hours)"
else
  echo "ots not found: pip install opentimestamps-client, then rerun" >&2
fi

openssl ts -query -data "$f" -no_nonce -sha512 -cert -out "$dir/manifest.tsq"
curl -sS -H "Content-Type: application/timestamp-query" \
     --data-binary "@$dir/manifest.tsq" https://freetsa.org/tsr -o "$dir/manifest.tsr"
echo "RFC 3161 response: $dir/manifest.tsr"
echo "Verify with FreeTSA's cacert.pem and tsa.crt (download from freetsa.org):"
echo "  openssl ts -verify -in $dir/manifest.tsr -queryfile $dir/manifest.tsq -CAfile cacert.pem -untrusted tsa.crt"
echo "Then publish the manifest, .ots and .tsr files (GitHub release mirrored to Zenodo, or OSF)."
