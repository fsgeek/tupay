#!/bin/bash
# Input check for one replay author checkout, run before the author starts.
# usage: inputcheck-replay.sh <checkout> <D|F> <model|impl> <withheld-hash>...
# derives: docs/steward-practice.md "Before an author starts"; log 2026-10-21 "the checkouts leak through git history"
set -uo pipefail
C=$1; ARM=$2; SIDE=$3; shift 3; bad=0; OTHER=D; [ "$ARM" = D ] && OTHER=F
for f in AGENTS.md "docs/briefs/replay-$ARM-$SIDE.md" replay/contract.md replay/failure-model.md replay/scenario-format.md \
  replay/observe.md "replay/spec-$ARM.md"; do [ -f "$C/$f" ] || { echo "MISSING $f"; bad=1; }; done
[ "$(ls "$C"/replay/scenarios/*.yaml | wc -l)" = 8 ] || { echo "scenario count is not 8"; bad=1; }
for f in "replay/spec-$OTHER.md" docs/seed-log.md docs/seed.md experiments tmp model impl; do
  [ -e "$C/$f" ] && { echo "FORBIDDEN present: $f"; bad=1; }; done
[ "$(git -C "$C" rev-list --all | wc -l)" -le 2 ] || { echo "history has more than the initial commit and its stamp"; bad=1; }
[ "$(git -C "$C" rev-list --max-parents=0 --all | wc -l)" = 1 ] || { echo "more than one root commit"; bad=1; }
objs=$(git -C "$C" rev-list --all --objects | awk '{print $2}' | grep -v '^$')
echo "$objs" | grep -q "spec-$OTHER\|seed-log\|fidelity\|K1" && { echo "FORBIDDEN path in history"; bad=1; }
for h in "$@"; do grep -rq "$h" "$C" --exclude-dir=.git && { echo "withheld hash present: $h"; bad=1; }; done
if [ "$ARM" = F ]; then grep -rqiE "raft|ongaro|logcabin" "$C/replay" "$C/docs" && { echo "arm F names the source"; bad=1; }; fi
[ -x "$C/scripts/hooks/post-commit" ] || { echo "MISSING scripts/hooks/post-commit"; bad=1; }
[ -x "$C/.venv/bin/ots" ] || { echo "MISSING .venv/bin/ots (no timestamps)"; bad=1; }
[ "$(git -C "$C" config commit.gpgsign)" = true ] || { echo "signing not configured"; bad=1; }
[ -n "$(ls "$C"/timestamps 2>/dev/null)" ] || { echo "initial commit was not stamped"; bad=1; }
[ $bad = 0 ] && echo OK || echo "CHECK FAILED"
