#!/bin/bash
# derives: practice "Credentials are copied in, never bind-mounted"; handoff 2026-11-07 (stale copies in tupay-homes).
# Checks that author-sandbox.sh removes its credential copy at exit, and keeps it only when a rotated token could not be
# written back, and never follows a symlink the author planted in its home. usage: sandbox-cred-check.sh [script].
# Mutants, each run from a copy of scripts/steward/ so its proxy and relay resolve (run 2026-11-08, both as stated):
#   82414a6's script (no removal) must FAIL case 1 only; e4b43df's (unguarded removal) must FAIL case 3 only.
# Tony's credential is never modified: case 2 corrupts only the sandbox copy (the shape check refuses write-back), and
# case 3's decoy is a byte-identical copy of it in this script's temporary directory, removed on exit.
set -uo pipefail
SB=${1:-$(dirname "$(realpath "$0")")/author-sandbox.sh}
W=$(mktemp -d); mkdir -p "$W/co"; trap 'rm -rf "$W"' EXIT
COPY=$W/tupay-homes/co/.codex/auth.json; ORIG=$(sha256sum < /home/tony/.codex/auth.json); fail=0
PROBE=1 EGRESS=/dev/null bash "$SB" "$W/co" codex -c 'test -s ~/.codex/auth.json && touch seen' >/dev/null 2>&1
[ -e "$W/co/seen" ] || { echo "FAIL: the sandbox never saw its copy (vacuous)"; fail=1; }
if [ -e "$COPY" ]; then echo "FAIL case 1: copy left after a normal run"; fail=1; else echo "ok case 1: copy removed"; fi
PROBE=1 EGRESS=/dev/null bash "$SB" "$W/co" codex -c 'echo corrupt >> ~/.codex/auth.json' >/dev/null 2>&1
if [ -e "$COPY" ]; then echo "ok case 2: unwritten rotation kept"; else echo "FAIL case 2: unwritten rotation deleted"; fail=1; fi
# case 3: the author replaces its .codex with a symlink to a decoy outside its home (never Tony's real file); on the host
# the decoy must survive the exit. Mutant for this case: e4b43df's script (unguarded rm), which must FAIL it.
mkdir -p "$W/decoy"; install -m 600 /home/tony/.codex/auth.json "$W/decoy/auth.json"   # same bytes as Tony's: the real attack's shape
PROBE=1 EGRESS=/dev/null bash "$SB" "$W/co" codex -c "rm -rf ~/.codex && ln -s $W/decoy ~/.codex" >/dev/null 2>&1
[ -L "$W/tupay-homes/co/.codex" ] || { echo "FAIL case 3: symlink not planted (vacuous)"; fail=1; }
if [ -e "$W/decoy/auth.json" ]; then echo "ok case 3: planted symlink not followed"; else echo "FAIL case 3: deleted through a planted symlink"; fail=1; fi
rm -f "$W/tupay-homes/co/.codex"
[ "$(sha256sum < /home/tony/.codex/auth.json)" = "$ORIG" ] && echo "ok: Tony's credential unchanged" || { echo "FAIL: Tony's credential changed"; fail=1; }
exit $fail
