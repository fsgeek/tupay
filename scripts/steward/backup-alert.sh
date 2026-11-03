#!/usr/bin/env bash
# Called by systemd OnFailure for tupay's backup units: post the failure to the plaza as
# guest:tupay, where Tony and tupay's next steward session will see it.
# PLAZA overrides the posting command (tests use a stand-in, so nothing reaches the plaza).
set -euo pipefail
unit="${1:-unknown}"
LOG="${LOG:-/home/tony/backups/tupay/backup-log.jsonl}"
PLAZA="${PLAZA:-/home/tony/projects/hamutay/deploy/ayllu-plaza}"
f="$(mktemp)"; trap 'rm -f "$f"' EXIT
{ echo "tupay (automated, from systemd unit $unit): tupay's backup to wam-nuc needs attention."
  echo "Most recent status lines:"
  tail -n 2 "$LOG" 2>/dev/null || echo "(no backup log at $LOG)"
  /home/tony/projects/tupay/scripts/steward/backup-check.sh 2>&1 || true
  echo "Script: tupay scripts/steward/backup.sh. Written by a script, not a steward session. Nothing is owed by anyone but tupay's steward."; } > "$f"
cd /home/tony/projects/hamutay
"$PLAZA" send --by guest:tupay --to plaza --carrier script --text-file "$f" >/dev/null
