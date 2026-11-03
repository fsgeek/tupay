#!/usr/bin/env bash
# Daily: fail (and so alert, via OnFailure) unless backup.sh's newest status line is ok and
# younger than MAX_AGE_H hours. Catches a timer that silently stopped as well as a failed run.
set -euo pipefail
LOG="${LOG:-/home/tony/backups/tupay/backup-log.jsonl}"
MAX_AGE_H="${MAX_AGE_H:-36}"
python3 - "$LOG" "$MAX_AGE_H" <<'PY'
import json, sys, datetime as d
log, max_h = sys.argv[1], float(sys.argv[2])
try:
    last = json.loads(open(log).read().strip().splitlines()[-1])
except Exception as e:
    sys.exit(f"no readable backup log: {e}")
age = (d.datetime.now(d.timezone.utc) - d.datetime.fromisoformat(last["finished"].replace("Z", "+00:00"))).total_seconds() / 3600
if last["status"] != "ok" or age > max_h:
    sys.exit(f"stale or failed: {last['status']} at {last['finished']} ({age:.1f} h)")
print(f"ok: {last['run']} ({age:.1f} h old)")
PY
