#!/usr/bin/env bash
# Restore drill: run ON THE RESTORE HOST (binding v2: tupay-restore@pundit), with S not in the data path.
# Fetches snapshot <run> from R with the restore host's own read-only key, checks its manifest, clones the
# bundle, runs git fsck, and prints HEAD and the time taken. Leaves the copy in ~/drill-<run>.
# derives: B1.8, B1.19, T4, T10, T11. First run 2026-11-22 (tupay log), started from S and again from wam-vector.
# Usage: bash restore-drill.sh <run>   (e.g. 20261122T111803Z)
set -euo pipefail
SNAP=$1; D=~/drill-$SNAP; rm -rf "$D"; mkdir -p "$D"; cd "$D"
R='ssh -i ~/.ssh/tupay-restore-wam-nuc -o IdentitiesOnly=yes -o BatchMode=yes'
t0=$(date +%s)
rsync -a -e "$R" tony@192.168.111.160:$SNAP/ snap/
t1=$(date +%s)
cd snap && sha256sum --quiet -c MANIFEST.sha256 && echo "manifest: ok ($(wc -l < MANIFEST.sha256) entries)"
cd .. && git clone -q snap/tupay.bundle tupay 2>&1 | tail -2
cd tupay && git fsck --no-progress --full 2>&1 | { grep -v '^dangling' || true; } | head -3; echo "fsck: done"
echo "refs: $(git for-each-ref refs/remotes | wc -l) remote branches"; git log -1 --format='HEAD %h %ad %s' --date=iso-strict
t2=$(date +%s); echo "fetch ${t1}-${t0}=$((t1-t0))s, total $((t2-t0))s"; du -sh "$D"
