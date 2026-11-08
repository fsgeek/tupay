#!/bin/bash
# derives: handoff 2026-11-07 "First, before anything else" (the channel sweep, as a command); log 2026-11-07 "five
# recorded cases" (four stopped at available-not-retrieved; rules failed, a mechanism held). Run by the steward's
# SessionStart hook (.claude/settings.local.json, untracked, so no author checkout carries it). Lives in docs/steward/,
# which author checkouts exclude. Prints what arrived in each channel since this script last printed it.
P=/home/tony/projects; T=$P/tupay; C=$T/tmp/channel-sweep; mkdir -p "$C"
since() { [ -f "$C/$1" ] && echo "-newer $C/$1"; }
echo "== tupay channel sweep $(date -u +%FT%H:%MZ) (new since the last sweep; a session-start hook printed this)"
for ch in "adversary-inbox:$T/docs/adversary/inbox" "episode-requests:$P/episode/docs/requests" \
          "episode-judging:$P/episode/judging" "eidolon-requests:$P/eidolon/docs/requests"; do
  n=${ch%%:*}; d=${ch#*:}
  new=$(find "$d" -type f ! -name .keep $(since "$n") 2>/dev/null | sort)
  [ -n "$new" ] && { echo "-- $n:"; echo "$new" | sed "s|$P/||"; } || echo "-- $n: nothing new"
  touch "$C/$n"
done
last=$(cat "$C/plaza-seq" 2>/dev/null || echo 239)
rows=$(cd $P/hamutay && timeout 60 uv run -q python -m hamutay.plaza read --since-seq $((last+1)) --posts 2>/dev/null)
if [ -n "$rows" ]; then
  echo "-- plaza posts after seq $last:"
  echo "$rows" | python3 -c 'import json,sys
for l in sys.stdin:
  r=json.loads(l); t=" ".join(r["text"].split()); print("  [%s] %s: %s" % (r["seq"], r["from"], t[:400]))
  open(sys.argv[1],"w").write(str(r["seq"]))' "$C/plaza-seq"
else echo "-- plaza: nothing after seq $last (or unreadable: check plaza_status)"; fi
