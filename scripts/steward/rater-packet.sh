#!/bin/bash
# Builds the blind Grok rater packet for one replay author (registration step 6).
# usage: rater-packet.sh <checkout> <concerns-commit> <source-file>:<from>-<to> ...   (writes to stdout)
# derives: experiments/replay-prereg.md "Classification", "Recognition: R4"; experiments/replay/rater-instructions.md
set -euo pipefail
C=$1; PRE=$2; shift 2
MAIN=$(cd "$(dirname "$0")/../.." && pwd)
sect() { awk -v h="$2" '$0 ~ "^## "{p=($0=="## "h)} p' <<<"$1"; }
for README in "$C"/model/README.md "$C"/impl/README.md; do [ -f "$README" ] && break; done; R=${README#$C/}
BEFORE=$(git -C "$C" show "$PRE:$R"); AFTER=$(git -C "$C" show "first-version:$R")
cat "$MAIN/experiments/replay/rater-instructions.md"
echo; echo "---"; echo "# Material"
echo "## README sections as committed before the first run (commit $PRE)"; sect "$BEFORE" Choices; sect "$BEFORE" Concerns
echo; echo "## README section at first-version ($(git -C "$C" rev-parse --short 'first-version^{commit}'))"; sect "$AFTER" "Concerns after running"
echo; echo "## Source of the configuration-change path (at first-version)"
for s in "$@"; do f=${s%%:*}; r=${s#*:}; echo "### $f lines $r"; echo '```'; git -C "$C" show "first-version:$f" | sed -n "${r/-/,}p"; echo '```'; done
