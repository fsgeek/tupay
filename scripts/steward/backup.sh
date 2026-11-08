#!/usr/bin/env bash
# Nightly backup of tupay's unreplicated record to wam-nuc (a physically separate machine).
# Modelled on hamutay/deploy/backup-records.sh. Before 2026-11-03 nothing backed these up
# (Tony, eleventh steward's acceptance): 200+ unpushed commits, tupay-private/, author homes.
#
# What: (1) tupay's repository as a git bundle of every ref (a consistent snapshot of a live
# repository; rsync of .git is not), checked with `git bundle verify`; (2) tupay-private/
# (sealed and licence-restricted material, author transcripts); (3) tupay-homes/ (author
# transcripts, egress logs) WITHOUT credentials or caches: auth.json, .credentials.json and
# anything named *credential* are excluded, so no harness token leaves this host.
# How: snapshot (hard-linked against the previous run) -> MANIFEST.sha256 -> rsync to wam-nuc
# (hard-linked there) -> verify the remote manifest -> prune to KEEP runs each side -> one JSON
# status line in backup-log.jsonl here and on wam-nuc. Nothing is written under any source.
set -euo pipefail
PROJECTS="${PROJECTS:-/home/tony/projects}"
REPO="$PROJECTS/tupay"
LOCAL_ROOT="${LOCAL_ROOT:-/home/tony/backups/tupay}"
REMOTE="${REMOTE:-wam-nuc}"
REMOTE_ROOT="${REMOTE_ROOT:-backups/tupay}"
KEEP="${KEEP:-14}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$LOCAL_ROOT/$TS"
LOG="$LOCAL_ROOT/backup-log.jsonl"
STAGE="start"
RQ="$(printf %q "$REMOTE_ROOT")"
runs() { find "$1" -mindepth 1 -maxdepth 1 -type d -name '20*Z' 2>/dev/null | sort; }

umask 077
mkdir -p "$LOCAL_ROOT"
status() {  # status <ok|failed> <stage> [extra-json-fields]
  local line
  line="{\"run\":\"$TS\",\"status\":\"$1\",\"stage\":\"$2\",\"finished\":\"$(date -u +%FT%TZ)\"${3:+,$3}}"
  echo "$line" >> "$LOG"
  echo "$line"
}
# A failed run leaves nothing behind, so it never counts among the KEEP good runs.
trap 'status failed "$STAGE"; rm -rf "$OUT"; ssh -o BatchMode=yes "$REMOTE" "rm -rf $RQ/$TS" 2>/dev/null || true; exit 1' ERR

STAGE="source"
[ -d "$REPO/.git" ] && [ -d "$PROJECTS/tupay-private" ] && [ -d "$PROJECTS/tupay-homes" ]
PREV="$(runs "$LOCAL_ROOT" | tail -n 1)"
mkdir -p "$OUT"

STAGE="bundle"
# Read-only on the repository: bundle create and verify write only to $OUT.
git -C "$REPO" bundle create "$OUT/tupay.bundle" --all 2>/dev/null
git -C "$REPO" bundle verify "$OUT/tupay.bundle" >/dev/null 2>&1
HEAD="$(git -C "$REPO" rev-parse HEAD)"

STAGE="private"
rsync -a ${PREV:+--link-dest="$PREV/tupay-private"} "$PROJECTS/tupay-private/" "$OUT/tupay-private/"

STAGE="homes"
rsync -a ${PREV:+--link-dest="$PREV/tupay-homes"} \
  --exclude='auth.json' --exclude='.credentials.json' --exclude='*credential*' \
  --exclude='.cache/' --exclude='go/pkg/' --exclude='.npm/' --exclude='node_modules/' \
  "$PROJECTS/tupay-homes/" "$OUT/tupay-homes/"

STAGE="no-credentials"
# Belt and braces: the copy must hold no credential file, whatever the excludes missed.
# (Not `! find | grep`: a negated pipeline is exempt from set -e and could never fail the run.)
if find "$OUT" \( -name 'auth.json' -o -name '.credentials.json' -o -name '*credential*' \) -print -quit | grep -q .; then
  echo "credential file in the copy" >&2; false
fi

STAGE="manifest"
( cd "$OUT" && find . -type f ! -name MANIFEST.sha256 -print0 | sort -z | xargs -0 -r sha256sum > MANIFEST.sha256 )
SIZE="$(du -sb "$OUT" | cut -f1)"
FILES="$(wc -l < "$OUT/MANIFEST.sha256")"

STAGE="copy"
ssh -o BatchMode=yes "$REMOTE" "mkdir -p $RQ && chmod 700 $RQ"
RPREV="$(ssh -o BatchMode=yes "$REMOTE" "find $RQ -mindepth 1 -maxdepth 1 -type d -name '20*Z' | sort | tail -n 1")"
rsync -a --protect-args ${RPREV:+--link-dest="../$(basename "$RPREV")"} "$OUT/" "$REMOTE:$REMOTE_ROOT/$TS/"

STAGE="verify-remote"
# git bundle verify needs a repository; use a throwaway bare one (the bundle is complete, so
# it has no prerequisites to resolve).
ssh -o BatchMode=yes "$REMOTE" "cd $RQ/$TS && test -s MANIFEST.sha256 && sha256sum --quiet -c MANIFEST.sha256 && V=\$(mktemp -d) && git init -q --bare \$V && git -C \$V bundle verify \$PWD/tupay.bundle >/dev/null 2>&1; r=\$?; rm -rf \$V; exit \$r"

STAGE="prune"
runs "$LOCAL_ROOT" | head -n -"$KEEP" | xargs -r -d '\n' rm -rf
ssh -o BatchMode=yes "$REMOTE" "find $RQ -mindepth 1 -maxdepth 1 -type d -name '20*Z' | sort | head -n -$KEEP | xargs -r -d '\n' rm -rf"

STAGE="done"
# Once ok is written the snapshot is acknowledged: no later failure may delete it or append a contradicting "failed"
# (Qwen's review of backup draft 2, finding 10, 2026-11-08: the trap stayed armed over the log copy below).
trap - ERR
status ok done "\"head\":\"$HEAD\",\"bytes\":$SIZE,\"files\":$FILES,\"remote\":\"$REMOTE:$REMOTE_ROOT/$TS\""
rsync -a --protect-args "$LOG" "$REMOTE:$REMOTE_ROOT/backup-log.jsonl" ||
  { echo "backup: snapshot $TS is ok; copying the status log to $REMOTE failed" >&2; exit 3; }
