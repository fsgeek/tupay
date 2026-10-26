#!/bin/bash
# Launch a model author on the box (ubuntu26-test) as tupay-author, detached, from the host.
# usage: box-launch.sh <checkout-name> <prompt-file> [host]
#   the checkout is /home/tupay-author/projects/<checkout-name> on the box (box-push.sh puts it there)
# derives: AGENTS.md rule 4; log 2026-10-23 "the model-author box built and checked"; sixth handoff, owed item 2
# The pinned model, no web tools, no RemoteTrigger (it starts a cloud agent with its own network, past the proxy),
# no MCP (account connectors included: ENABLE_CLAUDEAI_MCP_SERVERS=false and
# --strict-mcp-config), telemetry off, every route out through the proxy, which the nft rule makes the only one.
# bypassPermissions lets the author run commands unattended; the network layer, not the permission prompt, is what
# holds (box-check.sh proves it before each launch). A 24 GB memory cap, no swap, so a runaway check cannot take
# the host's dynamic memory. The transcript is stream-json, read afterwards by model-id-check.py (Tony's $500 lesson).
set -euo pipefail
NAME=$1; PROMPT=$2; H=${3:-ubuntu26-test}; SD=$(dirname "$(realpath "$0")")
"$SD/box-check.sh" "$H" >/dev/null || { echo "box-check failed; not launching"; "$SD/box-check.sh" "$H"; exit 1; }
CO=/home/tupay-author/projects/$NAME; RUN=/home/tupay-author/runs/$NAME
ssh -o BatchMode=yes "$H" "sudo -n test -d $CO && ! sudo -n test -e $RUN" || { echo "no checkout $CO, or $RUN exists"; exit 1; }
# one author's material at a time: another arm's checkout or run in the same home is readable by this author
# (2026-10-26: arm R launched with arm A's checkout and run still present, for 13 s; log)
others=$(ssh -o BatchMode=yes "$H" "sudo -n ls -A /home/tupay-author/projects /home/tupay-author/runs 2>/dev/null | grep -v -x -e '' -e '/home/tupay-author/projects:' -e '/home/tupay-author/runs:' -e '$NAME' || true")
[ -z "$others" ] || { echo "other material in the author home, remove it first: $others"; exit 1; }
ssh -o BatchMode=yes "$H" "sudo -n -u tupay-author mkdir -p $RUN && sudo -n -u tupay-author tee $RUN/prompt.txt >/dev/null" < "$PROMPT"
P=http://127.0.0.1:3128
ssh -o BatchMode=yes "$H" "sudo -n systemd-run --unit=tupay-author-$NAME --uid=tupay-author --gid=tupay-author \
  --working-directory=$CO -p MemoryMax=24G -p MemorySwapMax=0 \
  -p StandardInput=file:$RUN/prompt.txt -p StandardOutput=file:$RUN/transcript.jsonl -p StandardError=file:$RUN/stderr.txt \
  --setenv=HOME=/home/tupay-author --setenv=USER=tupay-author --setenv=PATH=/usr/local/bin:/usr/bin:/bin \
  --setenv=HTTPS_PROXY=$P --setenv=https_proxy=$P --setenv=HTTP_PROXY=$P --setenv=http_proxy=$P \
  --setenv=NO_PROXY=localhost,127.0.0.1 --setenv=DISABLE_TELEMETRY=1 --setenv=DISABLE_ERROR_REPORTING=1 \
  --setenv=CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 --setenv=ENABLE_CLAUDEAI_MCP_SERVERS=false --setenv=UV_OFFLINE=1 \
  /usr/local/bin/claude -p --model claude-opus-5-5 --disallowedTools WebSearch WebFetch RemoteTrigger --strict-mcp-config \
  --permission-mode bypassPermissions --output-format stream-json --verbose"
date -u +%Y-%m-%dT%H:%M:%SZ | sed "s/^/launched tupay-author-$NAME at /"
