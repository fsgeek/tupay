#!/bin/bash
# Steward runs of a replay implementation at first-version (registration "Runs"): shared scenarios and mutations,
# seeds 1-3, ten repetitions, from a scratch clone, under the memory cap.
# usage: replay-impl-runs.sh <author-checkout> <scratch-dir> <out-dir>
# derives: experiments/replay-prereg.md "Runs", "Labels"; docs/steward-practice.md (ten repetitions; memory cap)
set -euo pipefail
A=$1; S=$2; O=$(realpath -m "$3")
[ -e "$S" ] && { echo "exists: $S"; exit 1; }
git clone -q "$A" "$S"; git -C "$S" checkout -q first-version; mkdir -p "$O"
git -C "$S" rev-parse HEAD > "$O/commit.txt"
cap() { systemd-run --user --scope -q -p MemoryMax=24G -p MemorySwapMax=0 "$@"; }
cd "$S"
for r in $(seq 1 10); do
  for f in replay/scenarios/S*.yaml; do
    n=$(basename "$f" .yaml); rc=0; cap impl/run.sh "$f" --seeds 3 > "$O/.one" 2>&1 || rc=$?
    sed "s|^|rep=$r scenario=$n |" "$O/.one" >> "$O/shared.txt"; echo "rep=$r scenario=$n RUNNER-EXIT $rc" >> "$O/shared.txt"
  done
  rc=0; cap impl/run.sh --mutations --seeds 3 > "$O/.one" 2>&1 || rc=$?
  sed "s|^|rep=$r |" "$O/.one" >> "$O/mutations.txt"; echo "rep=$r RUNNER-EXIT $rc" >> "$O/mutations.txt"
done
rm -f "$O/.one"; date -u +%FT%TZ > "$O/end.txt"
