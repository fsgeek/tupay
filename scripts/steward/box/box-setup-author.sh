#!/bin/bash
# One-time, idempotent: the box author's signing identity and an OTS client it can run. From the host.
# usage: box-setup-author.sh <allowed-signers-file> [host]
# derives: AGENTS.md rules 3 and 4; scripts/steward/author-signing-key.sh (its box counterpart); sixth handoff, owed item 2
# The author gets its own throwaway ed25519 key in its own home: its only authority is "the box's author". The public
# half is appended to <allowed-signers-file> here, committed with the registration, so its commits verify on the host
# and a commit signed anywhere else does not. The OTS client is installed by root into /opt/ots (the author has no
# route to PyPI); the calendars are on the proxy's allowlist, so the author's own post-commit hook stamps its commits.
set -euo pipefail
AS=$1; H=${2:-ubuntu26-test}
ssh -o BatchMode=yes "$H" '[ -x /opt/ots/bin/ots ] || { sudo -n uv venv -q /opt/ots && sudo -n env VIRTUAL_ENV=/opt/ots uv pip install -q opentimestamps-client; }'
ssh -o BatchMode=yes "$H" 'sudo -n -iu tupay-author bash -s' <<'AUTHOR'
set -e; K=$HOME/.tupay-sign/key; mkdir -p "$HOME/.tupay-sign"
[ -e "$K" ] || ssh-keygen -q -t ed25519 -N '' -C tupay-author-box -f "$K"
git config --global user.name 'tupay-author (box)'; git config --global user.email tupay-author@ubuntu26-test
git config --global gpg.format ssh; git config --global user.signingkey "$K"; git config --global commit.gpgsign true
git config --global init.defaultBranch main
echo "tupay-author@ubuntu26-test namespaces=\"git\" $(cut -d' ' -f1,2 "$K.pub") tupay-author-box" > "$HOME/.tupay-sign/allowed_signers"
git config --global gpg.ssh.allowedSignersFile "$HOME/.tupay-sign/allowed_signers"
AUTHOR
LINE=$(ssh -o BatchMode=yes "$H" 'sudo -n cat /home/tupay-author/.tupay-sign/allowed_signers')
grep -qxF "$LINE" "$AS" 2>/dev/null || echo "$LINE" >> "$AS"
echo "box author key: $(echo "$LINE" | cut -d' ' -f3,4)"
