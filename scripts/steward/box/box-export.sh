#!/bin/bash
# Bring a box author's work back as data and verify every commit's signature here. From the host.
# usage: box-export.sh <checkout-name> <dest-clone> <allowed-signers> [host]
# derives: AGENTS.md rule 4; scripts/steward/author-export.sh (its box counterpart)
# The bundle is made on the box by the author's own git (root's git must not run in a checkout the author can write:
# a planted core.fsmonitor or filter would run as root). Here it is a file read as data into a fresh repository
# whose config is the steward's, as author-export.sh does. The run directory (transcript, stderr, prompt) comes too.
set -euo pipefail
NAME=$1; DEST=$2; AS=$(realpath "$3"); H=${4:-ubuntu26-test}
[ -e "$DEST" ] && { echo "exists: $DEST"; exit 1; }
ssh -o BatchMode=yes "$H" "sudo -n -iu tupay-author bash -c 'cd ~/projects/$NAME && git bundle create -q ~/runs/$NAME/export.bundle --all'"
mkdir -p "$DEST.run"
ssh -o BatchMode=yes "$H" "sudo -n tar -C /home/tupay-author/runs/$NAME -cf - ." | tar -xf - -C "$DEST.run"
git init -q "$DEST"
G=(git -C "$DEST" -c core.hooksPath=/dev/null -c gpg.ssh.allowedSignersFile="$AS")
"${G[@]}" bundle verify "$DEST.run/export.bundle" >/dev/null
"${G[@]}" fetch -q "$DEST.run/export.bundle" '+refs/heads/*:refs/remotes/author/*'
echo "signatures (G good, N none, B/U/E bad or unknown):"
"${G[@]}" log --format='%h %G? %s' --remotes=author
python3 "$(dirname "$(realpath "$0")")/model-id-check.py" "$DEST.run/transcript.jsonl"
