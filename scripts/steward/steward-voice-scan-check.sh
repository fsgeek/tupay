#!/bin/bash
# Mutation pair for steward-voice-scan.sh: a clean control passes; each planted sentence must hit.
# derives: AGENTS.md rule 5; practice rule 18
set -uo pipefail
S="$(dirname "$(realpath "$0")")/steward-voice-scan.sh"; d=$(mktemp -d); trap 'rm -rf "$d"' EXIT; bad=0
printf 'B1.1 A run copies every source.\nCommit your predictions first.\n' > "$d/clean.md"
"$S" "$d/clean.md" >/dev/null && echo "as expected (pass): clean control" || { echo "WRONG: clean control hit"; bad=1; }
for s in "The steward expects it to raise three things unprompted." "We suspect the checker misses this." \
         "Our hypothesis is that slow shrinkage is missed." "This schedule is likely to fail on arm N." "The steward's hypothesis: B1.15 is weak."; do
  printf '%s\n' "$s" > "$d/m.md"
  "$S" "$d/m.md" >/dev/null && { echo "WRONG (no hit): $s"; bad=1; } || echo "as expected (hit): $s"
done
[ $bad = 0 ] && echo "steward-voice-scan: all 6 cases as expected" || { echo "steward-voice-scan: case(s) wrong"; exit 1; }
