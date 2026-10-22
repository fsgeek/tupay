#!/bin/bash
# After the reveal: K1 v4 and hold-outs H1-H4 against one artifact at first-version, from a fresh scratch clone,
# under the memory cap. Models: each once. Implementations: K1 seeds 1-200 once; hold-outs seeds 1-3, ten repetitions.
# usage: replay-reveal-runs.sh <author-checkout> <scratch-dir> <out-dir> <model|impl>
# derives: experiments/replay-prereg.md "Runs", "K1 (fidelity check)", "Hold-outs"
set -uo pipefail
A=$1; S=$2; O=$(realpath -m "$3"); SIDE=$4; W=/home/tony/projects/tupay/experiments/replay/withheld
[ -e "$S" ] && { echo "exists: $S"; exit 1; }
git clone -q "$A" "$S"; git -C "$S" checkout -q first-version; mkdir -p "$O" "$S/replay/revealed"
cp "$W/K1v4.yaml" "$S/replay/revealed/K1.yaml"; cp "$W"/holdout/H*.yaml "$S/replay/revealed/"
git -C "$S" rev-parse HEAD > "$O/commit.txt"; cd "$S"; date -u +%FT%TZ > "$O/start.txt"
cap() { systemd-run --user --scope -q -p MemoryMax=24G -p MemorySwapMax=0 "$@"; }
for f in K1 H1 H2 H3 H4; do
  if [ "$SIDE" = model ]; then
    echo "$f $(cap "$SIDE"/run.sh replay/revealed/$f.yaml 2>"$O/$f.err" | tail -1)" >> "$O/results.txt"
  elif [ "$f" = K1 ]; then
    cap impl/run.sh replay/revealed/K1.yaml --seeds 200 > "$O/K1.txt" 2>"$O/K1.err"; echo "exit $?" >> "$O/K1.txt"
  else
    for r in $(seq 1 10); do cap impl/run.sh replay/revealed/$f.yaml --seeds 3 2>>"$O/$f.err" | sed "s|^|rep=$r |; s| observe=[^ ]*||" >> "$O/$f.txt"; done
  fi
done
date -u +%FT%TZ > "$O/end.txt"
