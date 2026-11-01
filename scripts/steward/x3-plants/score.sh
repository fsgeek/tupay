#!/bin/bash
# X3 measure 9 scoring for one plant: verify the witness FAILs the planted copy, then run the arm's shipped suite
# (the 59 shared schedules; implementations at 3 seeds x 10 repetitions) on the planted copy.
# usage: score.sh <adapt|regen> <impl|model> <clause> <scratch> <out>
# derives: X3 prereg measure 9, X3-6; log 2026-11-01 "X3 measure 9: planter setup"
set -euo pipefail
A=$1; S=$2; CL=$3; SC=$4; O=$(realpath -m "$5"); P=$HOME/projects; E=$P/tupay-x3-export-$A-$S; PL=$P/tupay-private/X3/plants/$A-$S
case $A-$S in adapt-impl) D=impl;; adapt-model) D=model;; regen-impl) D=impl-regen;; regen-model) D=model-regen;; esac
[ -e "$SC" ] && { echo "exists: $SC"; exit 1; }; [ -e "$O" ] && { echo "exists: $O"; exit 1; }; mkdir -p "$O"
git init -q "$SC"; git -C "$SC" fetch -q "$E" refs/remotes/author/main:refs/heads/author; git -C "$SC" checkout -q author
# the planted files: every file whose hash differs from the base, except PLANT.md and WITNESS.yaml
C=$P/tupay-x3-plant-$A-$S
(cd "$C" && find . -type f ! -name BRIEF.md -print0 | sort -z | xargs -0 sha256sum) > "$O/after.sha256"
diff <(sort -k2 "$PL/../$A-$S.base.sha256") <(sort -k2 "$O/after.sha256") | awk '/^>/{print $3}' \
  | grep -v -x -e ./PLANT.md -e ./WITNESS.yaml | grep -v '/observe/' > "$O/planted-files.txt" || true
while read -r f; do cp "$C/$f" "$SC/$f"; done < "$O/planted-files.txt"
cp "$C/WITNESS.yaml" "$SC/testbed/schedules/WITNESS.yaml"
git -C "$SC" diff --stat > "$O/planted-diffstat.txt"
export TLA2TOOLS=${TLA2TOOLS:-$HOME/projects/tlaplus/tla2tools.jar}
export PATH="$HOME/projects/tupay-x3-score/.pyenv/bin:$PATH"
if [ "$A-$S" = adapt-impl ]; then (cd "$SC/impl" && GOFLAGS=-mod=mod GOMODCACHE="$PWD/.cache/mod" /usr/local/go/bin/go mod download) > "$O/setup.txt" 2>&1; fi
cap() { systemd-run --user --scope -q -p MemoryMax=24G -p MemorySwapMax=0 "$@"; }
ARGS=""; [ "$S" = impl ] && ARGS="--seeds 3 --reps 10"
cd "$SC"; date -u +%FT%TZ > "$O/start.txt"
rc=0; cap "$D/run.sh" WITNESS $ARGS > "$O/witness.txt" 2>&1 || rc=$?; echo "RUNNER-EXIT $rc" >> "$O/witness.txt"
NAMES="$(seq 1 33 | sed 's/^/P/') $(seq 40 54 | sed 's/^/P/') $(seq 58 63 | sed 's/^/P/') false-suspicion-v1 H7 H8 H9 H10"
for n in $NAMES; do rc=0; cap "$D/run.sh" "$n" $ARGS > "$O/.one" 2>&1 || rc=$?
  sed "s|^|schedule=$n |" "$O/.one" >> "$O/suite.txt"; echo "schedule=$n RUNNER-EXIT $rc" >> "$O/suite.txt"; done
date -u +%FT%TZ > "$O/end.txt"
w=$(grep -c "FAIL.*$CL" "$O/witness.txt" || true); s=$(grep -c "FAIL.*$CL" "$O/suite.txt" || true); f=$(grep -c "FAIL" "$O/suite.txt" || true)
echo "witness FAIL $CL lines: $w | suite FAIL $CL lines: $s | suite FAIL lines (any): $f" | tee "$O/summary.txt"
