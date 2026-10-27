#!/bin/bash
# X3 support audit: one model side, one schedule. Is a state meeting every floor of the schedule's registered reach
# row in the side's checked space, at the side's own bounds?
# usage: audit.sh <A|R> <schedule-id> <outdir>      env: MUTANT=1 (anti-theater: an unreachable epochs floor; must
#        give NO-SUPPORT), SPLIT=1 (after NO-SUPPORT, probe each floor alone, to say which), AUDIT_TIMEOUT seconds
#        (default 0 = none; a run stopped by it is ERROR), TLA2TOOLS, AUDIT_CLONE_A / AUDIT_CLONE_R (clone roots)
# derives: experiments/X3-prereg.md Departure 3 (probe method: TLC at the author's stated bounds, an invariant negating
#          a state that meets every floor of the row; passes iff violated; "no support"; "vacuous by design") and
#          measure 1(a); experiments/X3/reach.md and holdout/reach.md (floors); scripts/steward/x3-runs.sh (how the
#          sides were run: the side's own compiler and cfg, no flags); docs/steward-practice.md (memory cap)
# Verdict (last line of <outdir>/verdict.txt, also printed):
#   SUPPORT      TLC reports NoFloor violated (trace length = states in TLC's trace)
#   NO-SUPPORT   TLC completed the search and NoFloor held (or a structural floor exceeds the compiled constants)
#   VACUOUS      the row needs a quantity the side does not model; the modelled floors are probed and reported beside it
#   ERROR        anything else (compile rejection, TLC error, time limit)
# Writes only into <outdir>; the clone is read (and checked unwritten afterwards with find -newer).
set -uo pipefail
SIDE=${1:?side A or R}; SID=${2:?schedule id}; O=$(realpath -m "${3:?outdir}")
HERE=$(dirname "$(realpath "$0")")
[ -e "$O" ] && { echo "exists: $O"; exit 1; }
mkdir -p "$O"; : > "$O/.start-marker"
JAR=${TLA2TOOLS:-$HOME/projects/tlaplus/tla2tools.jar}
case $SIDE in
  A) CLONE=${AUDIT_CLONE_A:-$HOME/projects/tupay-x3-score/armA-model} ;;
  R) CLONE=${AUDIT_CLONE_R:-$HOME/projects/tupay-x3-score/armR-model} ;;
  *) echo "side must be A or R"; exit 1 ;;
esac
{ echo "side=$SIDE schedule=$SID mutant=${MUTANT:-0}"; echo "clone=$CLONE commit=$(git -C "$CLONE" rev-parse HEAD)"
  echo "TLA2TOOLS=$JAR $(sha256sum "$JAR" | cut -c1-16)"; java -version 2>&1 | head -1
  echo "audit.sh $(sha256sum "$0" | cut -c1-16) probe.py $(sha256sum "$HERE/probe.py" | cut -c1-16)"; } > "$O/env.txt"

verdict() { echo "VERDICT side=$SIDE schedule=$SID mutant=${MUTANT:-0}${BESIDE:+ BESIDE=$BESIDE} $*" | tee -a "$O/verdict.txt"; }

if ! PYTHONDONTWRITEBYTECODE=1 uv run -q --no-project --with pyyaml==6.0.3 python -B "$HERE/probe.py" \
     "$SIDE" "$SID" "$O" "${MUTANT:-0}" > "$O/probe.json" 2> "$O/probe.err"; then
  verdict "ERROR compile: $(tail -1 "$O/probe.err")"; exit 0
fi
FLAGS=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["flags"])' "$O/probe.json")
SMISS=$(python3 -c 'import json,sys; print("; ".join(json.load(open(sys.argv[1]))["structural_miss"]))' "$O/probe.json")
VAC=$(python3 -c 'import json,sys; print(", ".join(json.load(open(sys.argv[1]))["vacuous"]))' "$O/probe.json")

# one TLC run on Probe.tla with invariant $1; prints "<result> <trace-length> <distinct> <seconds>"
run_tlc() {
  local inv=$1 cfg=Probe.cfg log="$O/tlc-$1.out" t0 rc=0
  if [ "$inv" != NoFloor ]; then cfg=Probe-$inv.cfg; sed "s/^INVARIANT NoFloor$/INVARIANT $inv/" "$O/tlc/Probe.cfg" > "$O/tlc/$cfg"; fi
  mkdir -p "$O/jtmp"; t0=$(date +%s)
  ( cd "$O/tlc" && timeout "${AUDIT_TIMEOUT:-0}" systemd-run --user --scope -q -p MemoryMax=12G -p MemorySwapMax=0 \
      java -Xmx8g -XX:+UseParallelGC -Djava.io.tmpdir="$O/jtmp" -cp "$JAR" tlc2.TLC $FLAGS -workers 8 \
      -metadir "$O/states-$inv" -config "$cfg" Probe ) > "$log" 2>&1 || rc=$?
  local secs=$(( $(date +%s) - t0 )) res
  local distinct; distinct=$(grep -oE '[0-9,]+ distinct states found' "$log" | tail -1 | cut -d' ' -f1)
  if grep -q "Invariant $inv is violated" "$log"; then res=VIOLATED
  elif grep -q "Model checking completed. No error has been found." "$log"; then res=HOLDS
  elif [ $rc -eq 124 ]; then res=TIMEOUT
  else res=ERROR; fi
  echo "$res $(grep -cE '^State [0-9]+:' "$log") ${distinct:-?} $secs"
}

if [ -n "$SMISS" ]; then
  verdict "NO-SUPPORT structural: $SMISS"
else
  read -r RES LEN DIST SECS < <(run_tlc NoFloor)
  case $RES in
    VIOLATED) V="SUPPORT trace=$LEN states=$DIST seconds=$SECS" ;;
    HOLDS)    V="NO-SUPPORT search complete, distinct=$DIST seconds=$SECS" ;;
    TIMEOUT)  V="ERROR time limit ${AUDIT_TIMEOUT}s, distinct=$DIST" ;;
    *)        V="ERROR TLC: $(grep -m1 -E '^Error|Exception' "$O/tlc-NoFloor.out" | cut -c1-200) seconds=$SECS" ;;
  esac
  if [ "$RES" = HOLDS ] && [ "${SPLIT:-0}" = 1 ]; then
    for c in $(python3 -c 'import json,sys; print(" ".join(json.load(open(sys.argv[1]))["used"]))' "$O/probe.json"); do
      read -r r l d s < <(run_tlc "AuditNo_$c"); echo "split $c: $r trace=$l distinct=$d seconds=$s" >> "$O/split.txt"
    done
    V="$V; split: $(tr '\n' ';' < "$O/split.txt")"
  fi
  if [ -n "$VAC" ]; then verdict "VACUOUS not modelled: $VAC; modelled floors (vacuous ones by step position): $V"
  else verdict "$V"; fi
fi
rm -rf "$O"/states-* "$O/jtmp"
W=$(find "$CLONE" -newer "$O/.start-marker" -print 2>/dev/null | head -5)
[ -n "$W" ] && echo "WARNING: files in the clone changed during the run: $W" | tee -a "$O/verdict.txt"
exit 0
