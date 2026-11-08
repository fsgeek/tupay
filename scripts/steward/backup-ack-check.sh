#!/bin/bash
# derives: backup contract B1.1/B1.6 (an acknowledged snapshot stays acknowledged); Qwen review of draft 2, finding 10.
# Runs backup.sh on a tiny fake tree to a throwaway directory on wam-nuc, with the remote status-log target made
# unwritable, so the final log copy fails after "ok". Pass: the snapshot survives on both sides and the log's last
# line is ok. Mutant: the script before 2026-11-08 (trap still armed) must FAIL. usage: backup-ack-check.sh [backup.sh]
set -uo pipefail
SB=${1:-$(dirname "$(realpath "$0")")/backup.sh}
W=$(mktemp -d); RR="backups/tupay-ackcheck-$(date -u +%s)-$$"
trap 'rm -rf "$W"; ssh -o BatchMode=yes wam-nuc "chmod -R u+w $RR 2>/dev/null; rm -rf $RR"' EXIT
P=$W/projects; mkdir -p $P/tupay $P/tupay-private $P/tupay-homes/a; git -C $P/tupay init -q
git -C $P/tupay -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit -q --allow-empty -m x; echo hi > $P/tupay-private/f; echo t > $P/tupay-homes/a/t
ssh -o BatchMode=yes wam-nuc "mkdir -p $RR/backup-log.jsonl && chmod 500 $RR/backup-log.jsonl"
PROJECTS=$P LOCAL_ROOT=$W/local REMOTE_ROOT=$RR bash "$SB" >$W/out 2>&1; rc=$?
TS=$(grep -o '"run":"[^"]*"' $W/local/backup-log.jsonl | tail -1 | cut -d'"' -f4)
last=$(tail -1 $W/local/backup-log.jsonl | grep -o '"status":"[a-z]*"')
lo=$([ -d $W/local/$TS ] && echo yes || echo no); re=$(ssh -o BatchMode=yes wam-nuc "test -d $RR/$TS && echo yes || echo no")
echo "rc=$rc last=$last local=$lo remote=$re"
grep -q '"status":"ok"' $W/local/backup-log.jsonl || { echo "FAIL: never reached ok (vacuous)"; cat $W/out; exit 1; }
[ "$last" = '"status":"ok"' ] && [ $lo = yes ] && [ $re = yes ] && echo "ok: acknowledged snapshot kept" || { echo "FAIL: acknowledged snapshot deleted or contradicted"; exit 1; }
