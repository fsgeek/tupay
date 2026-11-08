#!/bin/bash
# derives: practice "Credentials are copied in, never bind-mounted"; handoff 2026-11-07 (stale copies in tupay-homes).
# Checks that author-sandbox.sh removes its credential copy at exit, and keeps it only when a rotated token could not be
# written back. usage: sandbox-cred-check.sh [path to author-sandbox.sh]. Mutation pair: the pre-2026-11-08 script
# (git show 82414a6:scripts/steward/author-sandbox.sh), placed in a copy of scripts/steward/ so its proxy and relay
# resolve, must FAIL case 1 and only case 1 (run 2026-11-08: it does). Tony's credential is never modified: case 2
# corrupts only the sandbox copy, which fails the shape check, so nothing is written back.
set -uo pipefail
SB=${1:-$(dirname "$(realpath "$0")")/author-sandbox.sh}
W=$(mktemp -d); mkdir -p "$W/co"; trap 'rm -rf "$W"' EXIT
COPY=$W/tupay-homes/co/.codex/auth.json; ORIG=$(sha256sum < /home/tony/.codex/auth.json); fail=0
PROBE=1 EGRESS=/dev/null bash "$SB" "$W/co" codex -c 'test -s ~/.codex/auth.json && touch seen' >/dev/null 2>&1
[ -e "$W/co/seen" ] || { echo "FAIL: the sandbox never saw its copy (vacuous)"; fail=1; }
if [ -e "$COPY" ]; then echo "FAIL case 1: copy left after a normal run"; fail=1; else echo "ok case 1: copy removed"; fi
PROBE=1 EGRESS=/dev/null bash "$SB" "$W/co" codex -c 'echo corrupt >> ~/.codex/auth.json' >/dev/null 2>&1
if [ -e "$COPY" ]; then echo "ok case 2: unwritten rotation kept"; else echo "FAIL case 2: unwritten rotation deleted"; fail=1; fi
[ "$(sha256sum < /home/tony/.codex/auth.json)" = "$ORIG" ] && echo "ok: Tony's credential unchanged" || { echo "FAIL: Tony's credential changed"; fail=1; }
exit $fail
