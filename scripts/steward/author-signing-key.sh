#!/bin/bash
# Give an author checkout its own signing key, in place of Tony's GPG key. usage: author-signing-key.sh <checkout> <allowed-signers-file>
# derives: AGENTS.md rule 4; log 2026-10-23 "author isolation"
# An author in the sandbox cannot reach Tony's gpg-agent, and should not: that key is Tony's identity, and an agent
# that can sign with it holds his authority. Each author gets a throwaway ed25519 key in its sandbox home, whose only
# authority is "this checkout's author". The public half goes into <allowed-signers-file>, committed with the
# registration, so author commits verify with gpg.ssh.allowedSignersFile and a commit signed elsewhere does not.
set -euo pipefail
CO=$(realpath "$1"); AS=$2; NAME=$(basename "$CO")
AH=$(dirname "$CO")/tupay-homes/$NAME; K=$AH/.tupay-sign/key
mkdir -p "$(dirname "$K")"
[ -e "$K" ] || ssh-keygen -q -t ed25519 -N '' -C "tupay-author-$NAME" -f "$K"
git -C "$CO" config gpg.format ssh
git -C "$CO" config user.signingkey "/home/tony/.tupay-sign/key"   # the path inside the sandbox, where $AH is HOME
git -C "$CO" config commit.gpgsign true
git -C "$CO" config gpg.ssh.allowedSignersFile "/home/tony/.tupay-sign/allowed_signers"
EMAIL=$(git -C "$CO" config --get user.email)
LINE="$EMAIL namespaces=\"git\" $(cut -d' ' -f1,2 "$K.pub") tupay-author-$NAME"
echo "$LINE" > "$AH/.tupay-sign/allowed_signers"
grep -qxF "$LINE" "$AS" 2>/dev/null || echo "$LINE" >> "$AS"
echo "$NAME: $(ssh-keygen -lf "$K.pub")"
