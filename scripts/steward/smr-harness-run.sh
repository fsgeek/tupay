#!/bin/bash
# Launch the SMR reference-harness author (Grok) in the sandbox, from a COPY of scripts/steward taken at launch.
# usage: smr-harness-run.sh <family>   (checkout from smr-harness-checkout.sh; run under the harness's tracked background)
# derives: steward-practice "Never edit a script a run is executing" (rule 25: failed three times as a memory rule; its
# mechanism, a launcher that runs from a copy, is first built here); "Authors run sandboxed"; "hard memory cap";
# d2-model-run.sh (the same Grok invocation, six-hour and 24 GB limits enforced by systemd).
set -uo pipefail
F=$1; C=$HOME/projects/tupay-smr-harness-$F; R=$HOME/projects/tupay-private/smr/harness/run-$F
[ -d "$C" ] || { echo "no checkout: $C"; exit 1; }; [ -e "$R" ] && { echo "exists: $R"; exit 1; }
mkdir -p "$R"; cp -a "$HOME/projects/tupay/scripts/steward" "$R/steward-copy"
sha256sum "$R"/steward-copy/author-sandbox.sh "$R"/steward-copy/egress-grok.allow "$R"/steward-copy/egress-proxy.py > "$R/launch-copy.sha256"
PROMPT="Read BRIEF.md in this checkout and do what it says."
cd "$HOME/projects/tupay"; date -u +%FT%TZ > "$R/start.txt"; rc=0
systemd-run --user --scope -q -p RuntimeMaxSec=6h -p MemoryMax=24G -p MemorySwapMax=0 \
  "$R/steward-copy/author-sandbox.sh" "$C" grok --single "$PROMPT" --output-format streaming-json --always-approve \
  > "$R/transcript.jsonl" 2> "$R/stderr.txt" || rc=$?
echo $rc > "$R/exit.txt"; date -u +%FT%TZ > "$R/end.txt"; echo "smr-harness-$F exit $rc"
