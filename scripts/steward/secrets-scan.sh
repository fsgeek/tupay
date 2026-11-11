#!/bin/bash
# derives: backup contract AI1.5 (draft 4; Codex review finding 8): a reproducible detector for credentials entering a
# snapshot. usage: secrets-scan.sh <git-range>   e.g. secrets-scan.sh <prev-head>..<head>   (exit 1 on a hit)
#          secrets-scan.sh --files <dir>        scans regular files under dir
# Prints only the file, line number and pattern name of each hit, never the matched text.
# Pattern set v1 (2026-11-11): the set used for the 2026-11-03 scan, with names. Changing it is a new version.
# Mutation pair: secrets-scan-check.sh (planted fixtures of each pattern must hit; a clean control must not).
set -uo pipefail
PATS=(
  'openrouter:sk-or-v1-[A-Za-z0-9]{20,}'
  'openai:sk-(proj-)?[A-Za-z0-9_-]{32,}'
  'xai:xai-[A-Za-z0-9]{20,}'
  'github:gh[pousr]_[A-Za-z0-9]{30,}'
  'aws:AKIA[0-9A-Z]{16}'
  'google:AIza[0-9A-Za-z_-]{30,}'
  'oauth-field:"(access|refresh|id)_token"[[:space:]]*:[[:space:]]*"[^"]{20,}'
  'jwt:eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.'
  'private-key:-----BEGIN [A-Z ]*PRIVATE KEY'
  'bearer:Bearer [A-Za-z0-9._-]{20,}'
)
hit=0
if [ "${1:-}" = --files ]; then
  while IFS= read -r -d '' f; do
    for p in "${PATS[@]}"; do grep -q -I -E -e "${p#*:}" "$f" 2>/dev/null && { echo "HIT ${p%%:*}: $f"; hit=1; }; done
  done < <(find "$2" -type f -print0)
else
  r=$1
  while IFS= read -r c; do
    for p in "${PATS[@]}"; do
      git show --format= --unified=0 "$c" | grep '^+' | grep -q -I -E -e "${p#*:}" && { echo "HIT ${p%%:*}: commit $c"; hit=1; }
    done
  done < <(git rev-list "$r")
fi
[ $hit = 0 ] && echo "secrets-scan v1: no hit" ; exit $hit
