#!/bin/bash
# Run one X3 measure 9 planter (Grok, sandboxed, 2 h, 24 GB). usage: run.sh <adapt|regen> <impl|model>
# derives: X3 prereg measure 9; log 2026-11-01 "X3 measure 9: planter setup"
set -uo pipefail
A=$1; S=$2; P=$HOME/projects; C=$P/tupay-x3-plant-$A-$S; O=$P/tupay-private/X3/plants/$A-$S
[ -e "$O" ] && { echo "exists: $O"; exit 1; }; mkdir -p "$O"
cd "$P/tupay"; date -u +%FT%TZ > "$O/start.txt"; rc=0
systemd-run --user --scope -q -p RuntimeMaxSec=2h -p MemoryMax=24G -p MemorySwapMax=0 \
  scripts/steward/author-sandbox.sh "$C" grok --single "Read BRIEF.md in this directory and do what it says." \
  --output-format streaming-json --always-approve > "$O/transcript.jsonl" 2> "$O/stderr.txt" || rc=$?
echo $rc > "$O/exit.txt"; date -u +%FT%TZ > "$O/end.txt"; echo "plant $A-$S exit $rc"
