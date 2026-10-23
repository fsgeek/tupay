#!/bin/bash
# Check an author sandbox from inside it, before the author starts. usage: sandbox-check.sh <checkout> <codex|grok>
# derives: AGENTS.md rule 4; log 2026-10-23 "author isolation"
# PASS needs: the checkout readable and its harness credential present; none of Tony's other state, the main
# repository, other checkouts or Windows visible; the public repository unreachable through the proxy; no route
# around the proxy. Tony's harness configs are recognised by hash. Mutation pair (run by the steward with the check): EXTRA_RO=/home/tony/.ssh, and
# EGRESS=--learn, must each FAIL.
set -uo pipefail
CO=$1; H=$2; SD=$(dirname "$(realpath "$0")")
# harnesses write their own config.toml and state into the author's HOME, so Tony's files are found by content, not path
HASHES=$(sha256sum ~/.codex/config.toml ~/.codex/history.jsonl ~/.grok/config.toml ~/.grok/settings_cache.json ~/.claude.json \
  ~/.gitconfig 2>/dev/null | awk '{print $1}' | tr '\n' ' ')
sed -e "s/__H__/$H/" -e "s/__HASHES__/$HASHES/" <<'EOF' | PROBE=1 "$SD/author-sandbox.sh" "$CO" "$H" -s
fail=0
bad() { echo "FAIL $*"; fail=1; }
[ -r AGENTS.md ] || bad "checkout not readable"
[ -s ~/.__H__/auth.json ] || bad "harness credential missing"
# the main repository exists inside only as the mount point of its .venv (the OTS client); anything else there is a leak
[ "$(ls -A /home/tony/projects/tupay 2>/dev/null)" = .venv ] || bad "main repository holds more than .venv"
# a path is visible if it is a file or a non-empty directory (an empty one is a mount point left by a bind)
seen() { [ -f "$1" ] || [ -n "$(ls -A "$1" 2>/dev/null)" ]; }
for f in /home/tony/projects/khipumaq /home/tony/projects/qhaway /home/tony/.claude /home/tony/.claude.json \
         /home/tony/.ssh /home/tony/.gnupg /home/tony/.config /home/tony/.codex/memories \
         /home/tony/.grok/sessions/%2Fhome%2Ftony%2Fprojects%2Ftupay-replay-D-model \
         /home/tony/.grok/memory-v2 /home/tony/.gitconfig /mnt/c /mnt/wsl/docker-desktop /run/user/1000; do
  seen "$f" && bad "visible: $f"; done
for d in /home/tony/projects/*; do [ "$d" = /home/tony/projects/tlaplus ] || [ "$d" = /home/tony/projects/tupay ] || [ "${PWD#$d}" != "$PWD" ] || bad "visible: $d"; done
for x in $(find ~ \( -path ~/.nvm -o -path ~/node_modules -o -path ~/go -o -path ~/.local -o -path ~/projects \) -prune -o -type f -size -64M ! -name auth.json -exec sha256sum {} + 2>/dev/null | awk '{print $1":"$2}'); do
  case " __HASHES__ " in *" ${x%%:*} "*) bad "Tony's file present: ${x#*:}";; esac; done
c=$(curl -s -m 10 -o /dev/null -w '%{http_code}' https://github.com/fsgeek/tupay); [ "$c" = 000 ] || bad "github through proxy: $c"
curl -s -m 5 --noproxy '*' -o /dev/null https://140.82.112.3 && bad "direct route to an address"
getent hosts github.com >/dev/null && bad "direct DNS"
[ $fail = 0 ] && echo PASS
exit $fail
EOF
