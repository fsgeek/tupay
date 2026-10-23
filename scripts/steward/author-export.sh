#!/bin/bash
# Bring an author's work out of its sandbox as data. usage: author-export.sh <checkout> <codex|grok> <dest-clone> <allowed-signers>
# derives: AGENTS.md rule 4; log 2026-10-23 "author isolation"; automated security review of author-sandbox.sh
# The author can write its checkout's .git (config, hooks, attributes), so host git must never run there: core.fsmonitor,
# gpg.ssh.program, diff.external, a pager or a filter driver planted by the author would execute outside the sandbox.
# The bundle is made inside the sandbox; the host only fetches from the bundle file into a fresh repository whose
# config is the steward's, then verifies every commit's signature there.
set -euo pipefail
CO=$(realpath "$1"); H=$2; DEST=$3; AS=$(realpath "$4"); SD=$(dirname "$(realpath "$0")")
B=$CO/.tupay-export.bundle
echo 'git bundle create .tupay-export.bundle --all' | PROBE=1 "$SD/author-sandbox.sh" "$CO" "$H" -s
cp "$B" "$DEST.bundle.tmp"   # a regular file read as data; nothing of the checkout's .git is consulted from here on
[ -e "$DEST" ] && { echo "exists: $DEST"; exit 1; }
git init -q "$DEST"
G=(git -C "$DEST" -c core.hooksPath=/dev/null -c gpg.ssh.allowedSignersFile="$AS")
"${G[@]}" bundle verify "$DEST.bundle.tmp" >/dev/null
"${G[@]}" fetch -q "$DEST.bundle.tmp" '+refs/heads/*:refs/remotes/author/*'
mv "$DEST.bundle.tmp" "$DEST.bundle"
echo "signatures (G good, N none, B/U/E bad or unknown):"
"${G[@]}" log --format='%h %G? %s' --remotes=author
