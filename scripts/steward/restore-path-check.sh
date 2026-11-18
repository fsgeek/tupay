#!/usr/bin/env bash
# Daily: fail (and so alert, via OnFailure) unless the restore host can still reach R by its own
# key and see the newest acknowledged snapshot there.
# derives: B1.19, T4, T11 (a restore runs on the restore host with S unavailable, so the restore host
# needs its own path to R); found missing 2026-11-13 and again 2026-11-18 after the box was rolled back
# to a June checkpoint (tupay log). backup-check.sh checks that backups are made; this checks that
# the place a restore runs can still get at them.
# Overrides for the mutation pair (restore-path-check-check.sh): BOX, KEY, R, LOG, SNAP.
set -euo pipefail
BOX="${BOX:-ubuntu26-test}"
KEY="${KEY:-~/.ssh/tupay-restore-wam-nuc}"          # a path on the restore host, not on S
R="${R:-tony@192.168.111.160}"                       # R as the restore host reaches it
LOG="${LOG:-/home/tony/backups/tupay/backup-log.jsonl}"
SNAP="${SNAP:-$(python3 - "$LOG" <<'PY'
import json, sys
ok = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
ok = [e for e in ok if e.get("status") == "ok"]
print(ok[-1]["run"] if ok else "")
PY
)}"
[ -n "$SNAP" ] || { echo "fail: no acknowledged snapshot in $LOG"; exit 1; }
out="$(timeout 60 ssh -o BatchMode=yes -o ConnectTimeout=10 "$BOX" \
  "rsync -e 'ssh -i $KEY -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=10' $R:$SNAP/ 2>&1" 2>&1)" \
  || { echo "fail: restore host $BOX could not list $SNAP at R: $(echo "$out" | tail -n 2 | tr '\n' ' ')"; exit 1; }
grep -q 'MANIFEST.sha256' <<<"$out" || { echo "fail: $SNAP at R, as seen from $BOX, has no MANIFEST.sha256"; exit 1; }
echo "ok: restore host $BOX reaches R and sees $SNAP"
