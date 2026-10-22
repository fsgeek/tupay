#!/bin/bash
# Steward runs of a replay model at first-version: shared scenarios once, mutations once, and --explore with the
# author's bounds, from a scratch clone, under the memory cap; --explore limited to 4 h wall-clock (log 2026-10-22).
# usage: replay-model-runs.sh <author-checkout> <scratch-dir> <out-dir> <scenarios|explore>
# derives: experiments/replay-prereg.md "Runs" (models once; --explore at first-version with stated bounds)
set -uo pipefail
A=$1; S=$2; O=$(realpath -m "$3"); WHAT=$4
mkdir -p "$O"
[ -e "$S" ] || { git clone -q "$A" "$S" && git -C "$S" checkout -q first-version; }
git -C "$S" rev-parse HEAD > "$O/commit.txt"; cd "$S"
cap() { systemd-run --user --scope -q -p MemoryMax=24G -p MemorySwapMax=0 "$@"; }
date -u +%FT%TZ > "$O/$WHAT.start"
if [ "$WHAT" = scenarios ]; then
  for f in replay/scenarios/S*.yaml; do echo "$(basename $f .yaml) $(cap model/run.sh "$f" 2>"$O/$(basename $f .yaml).err" | tail -1)" >> "$O/shared.txt"; done
  cap model/run.sh --mutations > "$O/mutations.txt" 2> "$O/mutations.err"; echo "exit $?" >> "$O/mutations.txt"
else
  timeout --signal=TERM --kill-after=60 4h systemd-run --user --scope -q -p MemoryMax=24G -p MemorySwapMax=0 model/run.sh --explore > "$O/explore.txt" 2> "$O/explore.err"; echo "exit $?" >> "$O/explore.txt"
fi
date -u +%FT%TZ > "$O/$WHAT.end"
