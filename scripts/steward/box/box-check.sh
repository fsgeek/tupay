#!/bin/bash
# The steward's check of the model-author box (ubuntu26-test), run from the host before each launch.
# usage: box-check.sh [host]     exit 1 on any FAIL
# derives: AGENTS.md rule 4; log 2026-10-23 "launch gap 2"; docs/steward-practice.md "Authors run sandboxed"
# What must hold: the author (tupay-author) has no route out but the proxy; the proxy is not in learn mode and allows
# only egress-claude.allow; a direct connection and DNS fail; the public repository is denied through the proxy; the
# API is reachable through it; the author's home holds no ssh keys, no MCP server, no installed plugin, and its
# settings deny WebSearch, WebFetch and RemoteTrigger, and no earlier session's history is there to read.
H=${1:-ubuntu26-test}
ssh -o BatchMode=yes "$H" 'bad=0; ok(){ echo "ok   $1"; }; no(){ echo "FAIL $1"; bad=1; }
A="sudo -n -iu tupay-author"
sudo -n nft list table inet tupay_author 2>/dev/null | grep -q "skuid 1001 log prefix \"tupay-author-deny \" drop" && ok "nft drop rule for uid 1001" || no "nft drop rule for uid 1001 missing"
systemctl cat tupay-egress-proxy 2>/dev/null | grep "^ExecStart=/" | tail -1 | grep -q -- "--learn" && no "proxy in learn mode" || ok "proxy not in learn mode"
systemctl is-active -q tupay-egress-proxy tupay-egress-relay && ok "proxy and relay active" || no "proxy or relay not active"
$A curl -sS -m 6 -o /dev/null https://github.com 2>/dev/null && no "direct egress open" || ok "direct egress blocked"
$A getent hosts github.com >/dev/null && no "DNS open" || ok "DNS blocked"
c=$($A curl -sS -m 8 -o /dev/null -w "%{http_code}" -x http://127.0.0.1:3128 https://github.com/fsgeek/tupay 2>/dev/null); [ "$c" = 200 ] && no "github reachable via proxy" || ok "github denied via proxy"
c=$($A curl -sS -m 8 -o /dev/null -w "%{http_code}" -x http://127.0.0.1:3128 https://api.anthropic.com/ 2>/dev/null); [ "$c" != 000 ] && ok "api reachable via proxy ($c)" || no "api unreachable via proxy"
sudo -n bash -c "test -e /home/tupay-author/.claude/history.jsonl || test -n \"\$(ls -A /home/tupay-author/.claude/projects 2>/dev/null)\"" && no "earlier sessions in author home" || ok "no earlier sessions in author home"
sudo -n test -e /home/tupay-author/.ssh && no "author home has .ssh" || ok "no .ssh in author home"
m=$(sudo -n python3 -c "import json;print(len(json.load(open(\"/home/tupay-author/.claude.json\")).get(\"mcpServers\",{})))" 2>/dev/null || echo 0); [ "$m" = 0 ] && ok "no MCP servers" || no "$m MCP servers configured"
sudo -n test -s /home/tupay-author/.claude/plugins/installed_plugins.json && sudo -n grep -q "\"plugins\": *{ *[^} ]" /home/tupay-author/.claude/plugins/installed_plugins.json && no "plugins installed" || ok "no plugins installed"
sudo -n python3 -c "import json,sys;d=set(json.load(open(\"/home/tupay-author/.claude/settings.json\")).get(\"permissions\",{}).get(\"deny\",[]));sys.exit(0 if {\"WebSearch\",\"WebFetch\",\"RemoteTrigger\"}<=d else 1)" && ok "WebSearch, WebFetch, RemoteTrigger denied in settings" || no "web tools or RemoteTrigger not denied in settings"
exit $bad'
