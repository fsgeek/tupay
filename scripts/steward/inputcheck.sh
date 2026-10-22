#!/bin/bash
# Standalone input check for one author checkout, run before the author starts.
# usage: inputcheck.sh <checkout> <brief-path> <holdout-SHA256SUMS>... -- <forbidden-path>...
# derives: docs/steward-practice.md "Before an author starts" (X1 Amendments B and C; X2 errors 3 and 4)
set -uo pipefail
C=$1; BRIEF=$2; shift 2; SUMS=(); while [ $# -gt 0 ] && [ "$1" != -- ]; do SUMS+=("$1"); shift; done; shift || true
bad=0
[ -f "$C/$BRIEF" ] || { echo "MISSING brief $BRIEF"; bad=1; }
for f in $(grep -o '`[A-Za-z0-9/._-]*\.\(md\|yaml\)`' "$C/$BRIEF" | tr -d '`' | sort -u); do
  case "$f" in docs/seed*.md|*-regen/*|*/README.md|README.md) continue;; esac
  [ -e "$C/$f" ] || [ -e "$C/testbed/$f" ] || [ -e "$C/testbed/schedules/$f" ] || { echo "brief names missing: $f"; bad=1; }; done
for f in "$@" CLAUDE.md docs/steward docs/seed-log.md docs/handoff; do [ -e "$C/$f" ] && { echo "FORBIDDEN present: $f"; bad=1; }; done
for h in $(sha256sum "$C"/testbed/schedules/* | awk '{print $1}'); do
  for s in "${SUMS[@]}"; do grep -q "$h" "$s" && { echo "HOLD-OUT hash present: $h"; bad=1; }; done; done
[ -x "$C/scripts/hooks/post-commit" ] || { echo "MISSING scripts/hooks/post-commit (no timestamps)"; bad=1; }
[ "$(git -C "$C" config commit.gpgsign)" = true ] || { echo "signing not configured"; bad=1; }
echo "schedules: $(ls "$C"/testbed/schedules | wc -l)"
[ $bad = 0 ] && echo OK || echo "CHECK FAILED"
