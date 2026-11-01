#!/bin/bash
# Build one X3 measure 10 chooser checkout from an arm side's exported artifact (no git history), and fill its caches.
# usage: setup.sh <adapt|regen> <impl|model>     -> ~/projects/tupay-x3-recon-<arm>-<side>
# derives: X3 prereg measure 10; steward practice "Authors run sandboxed"; log 2026-11-01 "X3 measure 9: planter setup"
set -euo pipefail
A=$1; S=$2; P=$HOME/projects; E=$P/tupay-x3-export-$A-$S; C=$P/tupay-x3-recon-$A-$S; AH=$P/tupay-homes/$(basename "$C")
SD=$(dirname "$(realpath "$0")")
[ -e "$C" ] && { echo "exists: $C"; exit 1; }
mkdir -p "$C"; git -C "$E" archive author/main | tar -x -C "$C"
cp "$SD/BRIEF.md" "$C/BRIEF.md"
rm -f "$C/CLAUDE.md"; rm -rf "$C/scripts/hooks"
( cd "$C" && find . -type f ! -name BRIEF.md -print0 | sort -z | xargs -0 sha256sum ) > "$P/tupay-private/X3/recon/$A-$S.base.sha256"
mkdir -p "$AH/go" "$AH/.cache"
if [ -f "$C/go.mod" ] || [ -f "$C/impl/go.mod" ] || [ -f "$C/impl-regen/go.mod" ]; then d=$C; [ -f "$C/impl/go.mod" ] && d=$C/impl; [ -f "$C/impl-regen/go.mod" ] && d=$C/impl-regen
  (cd "$d" && GOMODCACHE=$AH/go/pkg/mod GOFLAGS=-mod=mod go mod download all); fi
UV_CACHE_DIR=$AH/.cache/uv uv run --no-project --with pyyaml==6.0.3 python -c 'import yaml' >/dev/null
echo "$C ready; base hashes in tupay-private/X3/recon/$A-$S.base.sha256"
