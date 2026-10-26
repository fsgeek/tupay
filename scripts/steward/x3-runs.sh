#!/bin/bash
# X3 registered steward runs, one side of one arm: the 59 shared schedules and the four hold-outs, then the side's
# mutations, from a fresh clone of the author's exported bundle, under the memory cap.
# usage: x3-runs.sh <armA|armR> <impl|model> <scratch-dir> <out-dir>
# derives: experiments/X3-prereg.md measures 1(a) to 1(c), "Liveness rules" (ten repetitions at each of three seeds);
#          docs/steward-practice.md (scratch worktrees; hold-outs enter scratch copies only; memory cap; ten repetitions)
# Verdicts here are the side's own. The registered conditions applied afterwards (decision replay parts 1 and 2 by the
# steward's copy of observe/decision_replay.py, provenance, support audits, the judge) read the traces this keeps.
# Run it from a copy, never from the file a run is executing (practice).
set -euo pipefail
ARM=$1; SIDE=$2; S=$3; O=$(realpath -m "$4")
T=$(git -C "$(dirname "$(realpath "$0")")" rev-parse --show-toplevel)
case $ARM-$SIDE in
  armA-impl) B=adapt-impl; D=impl ;;  armA-model) B=adapt-model; D=model ;;
  armR-impl) B=regen-impl; D=impl-regen ;; armR-model) B=regen-model; D=model-regen ;;
  *) echo "bad arm or side"; exit 1 ;;
esac
[ -e "$S" ] && { echo "exists: $S"; exit 1; }
[ -e "$O" ] && { echo "exists: $O"; exit 1; }
git clone -q "$T/experiments/X3/$ARM/$SIDE/$B.bundle" "$S"; mkdir -p "$O"
git -C "$S" rev-parse HEAD > "$O/commit.txt"
# hold-outs: verified against the committed hashes, then copied into this scratch clone only
(cd "$T" && sha256sum -c --quiet experiments/X3/holdout/SHA256SUMS) || { echo "hold-out hash mismatch"; exit 1; }
for h in H11 H12 H13 H14; do cp "$T/experiments/X3/holdout/$h.yaml" "$S/testbed/schedules/$h.yaml"; done
cmp -s "$T/observe/decision_replay.py" "$S/observe/decision_replay.py" && echo same > "$O/decision_replay-vs-main.txt" \
  || echo DIFFERENT > "$O/decision_replay-vs-main.txt"
export TLA2TOOLS=${TLA2TOOLS:-$HOME/projects/tlaplus/tla2tools.jar}
export PATH="$HOME/projects/tupay-x3-score/.pyenv/bin:$PATH"   # arm R impl's runner is plain python3 and needs pyyaml
{ echo "TLA2TOOLS=$TLA2TOOLS $(sha256sum "$TLA2TOOLS" | cut -c1-16)"; java -version 2>&1 | head -1; nproc; } > "$O/env.txt"
if [ "$B" = adapt-impl ]; then   # its run.sh reads modules only from impl/.cache/mod, filled here as the sandbox's was
  (cd "$S/impl" && GOFLAGS=-mod=mod GOMODCACHE="$PWD/.cache/mod" /usr/local/go/bin/go mod download) >> "$O/setup.txt" 2>&1
fi
cap() { systemd-run --user --scope -q -p MemoryMax=24G -p MemorySwapMax=0 "$@"; }
NAMES="$(seq 1 33 | sed 's/^/P/') $(seq 40 54 | sed 's/^/P/') $(seq 58 63 | sed 's/^/P/') false-suspicion-v1 H7 H8 H9 H10 H11 H12 H13 H14"
ARGS=""; [ "$SIDE" = impl ] && ARGS="--seeds 3 --reps 10"
cd "$S"; date -u +%FT%TZ > "$O/start.txt"
for n in $NAMES; do rc=0; s=$(date +%s); cap "$D/run.sh" "$n" $ARGS > "$O/.one" 2>&1 || rc=$?
  sed "s|^|schedule=$n |" "$O/.one" >> "$O/schedules.txt"
  echo "schedule=$n RUNNER-EXIT $rc SECONDS $(( $(date +%s) - s ))" >> "$O/schedules.txt"; done
date -u +%FT%TZ > "$O/schedules-end.txt"
rc=0; cap "$D/run.sh" --mutations $ARGS > "$O/mutations.txt" 2>&1 || rc=$?
echo "RUNNER-EXIT $rc" >> "$O/mutations.txt"
rm -f "$O/.one"; date -u +%FT%TZ > "$O/end.txt"
