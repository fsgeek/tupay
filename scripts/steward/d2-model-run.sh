#!/bin/bash
# One D2 phase 2 Grok model author, in the sandbox, under the design's limits. usage: d2-model-run.sh <c|n>
# derives: experiments/D2/design.md draft 2, "Phase 2" (six hours, 24 GB, enforced by systemd; transcripts outside the repository)
# The checkout comes from d2-checkouts.sh model-<c|n> grok; the Claude authors run on the box (box-launch.sh) instead.
set -uo pipefail
m=$1; n=model-$m-grok; P=$HOME/projects/tupay-private/D2/phase2/$n; C=$HOME/projects/tupay-d2-$n
[ -e "$P" ] && { echo "exists: $P"; exit 1; }; mkdir -p "$P"
PROMPT="Read BRIEF.md in this checkout and do what it says."
cd "$HOME/projects/tupay"; date -u +%FT%TZ > "$P/start.txt"; rc=0
systemd-run --user --scope -q -p RuntimeMaxSec=6h -p MemoryMax=24G -p MemorySwapMax=0 \
  scripts/steward/author-sandbox.sh "$C" grok --single "$PROMPT" --output-format streaming-json --always-approve \
  > "$P/transcript.jsonl" 2> "$P/stderr.txt" || rc=$?
echo $rc > "$P/exit.txt"; date -u +%FT%TZ > "$P/end.txt"; echo "$n exit $rc"
