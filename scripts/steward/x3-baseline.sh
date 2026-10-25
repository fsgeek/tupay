#!/bin/bash
# X3 measure 5 baseline: the 35 shared schedules that predate X3 (P1 to P30, false-suspicion-v1, H7 to H10), run on
# main's model and implementation at one commit, from a scratch clone, under the memory cap.
# usage: x3-baseline.sh <commit> <scratch-dir> <out-dir>
# derives: experiments/X3-prereg.md measure 5; docs/steward-practice.md (ten repetitions; memory cap)
# PASS here is the side's own verdict: main's artifacts predate schema v5's decision records, so the decision-replay
# condition of 1(a) would fail every one of their decisions and make the baseline vacuous (stated at registration).
# Implementation: a schedule passes only if all ten repetitions of all three seeds pass. Model: TLC once per schedule.
set -euo pipefail
C=$1; S=$2; O=$(realpath -m "$3")
[ -e "$S" ] && { echo "exists: $S"; exit 1; }
git clone -q "$(git rev-parse --show-toplevel)" "$S"; git -C "$S" checkout -q "$C"; mkdir -p "$O"
git -C "$S" rev-parse HEAD > "$O/commit.txt"; date -u +%FT%TZ > "$O/start.txt"
ln -s "$(git rev-parse --show-toplevel)/.venv" "$S/.venv"
cap() { systemd-run --user --scope -q -p MemoryMax=24G -p MemorySwapMax=0 "$@"; }
NAMES="$(seq 1 30 | sed 's/^/P/') false-suspicion-v1 H7 H8 H9 H10"
cd "$S"
for n in $NAMES; do rc=0; cap model/run.sh "$n" > "$O/.one" 2>&1 || rc=$?
  sed "s|^|schedule=$n |" "$O/.one" >> "$O/model.txt"; echo "schedule=$n RUNNER-EXIT $rc" >> "$O/model.txt"; done
for r in $(seq 1 10); do for n in $NAMES; do rc=0; cap impl/run.sh "$n" --seeds 3 > "$O/.one" 2>&1 || rc=$?
  sed "s|^|rep=$r schedule=$n |" "$O/.one" >> "$O/impl.txt"; echo "rep=$r schedule=$n RUNNER-EXIT $rc" >> "$O/impl.txt"; done; done
rm -f "$O/.one"; date -u +%FT%TZ > "$O/end.txt"
