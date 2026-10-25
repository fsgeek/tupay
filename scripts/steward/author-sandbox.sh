#!/bin/bash
# Run an author's harness in a bubblewrap sandbox that sees only its checkout, the toolchains, and the harness's own
# credential. usage: [PROBE=1] [EGRESS=<allowlist>|--learn] [EXTRA_RO=<path>] author-sandbox.sh <checkout> <codex|grok> [harness args...]
# derives: AGENTS.md rule 4; docs/steward-practice.md "Author isolation"; log 2026-10-22 "what reaches an author's harness"
# Two separate guards. Configuration: HOME is a per-author directory, so none of Tony's Claude, Codex or Grok
# configuration (MCP servers, plugins, hooks, memories, history) loads. Access: only the paths bound below exist
# inside, so the log, other checkouts, khipumaq and ~/.ssh cannot be read by absolute path either.
# Python packages: uv runs offline from the author home's own cache, which the steward fills on the host before launch
# (UV_CACHE_DIR=<author home>/.cache/uv uv run --with <pin> ...); probe 2026-10-23: empty cache fails, filled one works.
# Network: the sandbox has none of its own (--unshare-net). Its only way out is an HTTPS CONNECT proxy on a unix
# socket (egress-proxy.py, outside), reached through a relay inside (sandbox-relay.py), which allows the hosts in
# scripts/steward/egress-<harness>.allow and logs every attempt to <author home>/egress.log. Without it, a plain
# curl from the author's shell reached the public repository and its log (probe, 2026-10-23).
# The credential is copied in and, if the harness rotated it, written back after the run. Until 2026-10-25 it was
# bind-mounted, to keep a refreshing copy from invalidating Tony's login; that did the harm it meant to prevent: a
# refresh rotates the token at the provider, and the harness saves by renaming over auth.json, which a bind-mounted
# file refuses (EBUSY), so the new token was lost and Tony's Grok login died (log 2026-10-25, "the sandbox killed
# Tony's Grok login"). Write-back happens only if Tony's file is unchanged since the copy (else a concurrent run
# already rotated it, and this run's copy is stale) and the new file is JSON with the same top-level keys. The author
# can read its own copy of its harness credential; nothing else of Tony's.
set -euo pipefail
CO=$(realpath "$1"); H=$2; shift 2
U=/home/tony; MAIN=$U/projects/tupay
AH=$(dirname "$CO")/tupay-homes/$(basename "$CO")   # the author's HOME; its transcripts land here
mkdir -p "$AH/.codex" "$AH/.grok" "$AH/.cache" "$AH/go"
NODE=$(dirname "$(dirname "$(readlink -f "$(command -v node)")")")
GROKBIN=$(readlink -f "$U/.grok/bin/grok")
SD=$(dirname "$(realpath "$0")"); EG=${EGRESS:-$SD/egress-$H.allow}
SOCKDIR=$(mktemp -d); python3 "$SD/egress-proxy.py" "$SOCKDIR/egress.sock" "$AH/egress.log" "$EG" & PROXY=$!
trap 'kill $PROXY 2>/dev/null; rm -rf "$SOCKDIR"' EXIT
for _ in $(seq 50); do [ -S "$SOCKDIR/egress.sock" ] && break; sleep 0.1; done
args=(--unshare-net --unshare-pid --unshare-ipc --unshare-uts --die-with-parent --new-session --clearenv
  --ro-bind /usr /usr --symlink usr/bin /bin --symlink usr/sbin /sbin --symlink usr/lib /lib --symlink usr/lib64 /lib64
  --ro-bind /etc /etc --ro-bind /mnt/wsl/resolv.conf /mnt/wsl/resolv.conf
  --proc /proc --dev /dev --tmpfs /tmp
  --bind "$AH" "$U"
  --ro-bind "$NODE" "$NODE"
  --ro-bind "$U/projects/tlaplus/tla2tools.jar" "$U/projects/tlaplus/tla2tools.jar"
  --ro-bind "$MAIN/.venv" "$MAIN/.venv" --ro-bind "$U/.local/share/uv/python" "$U/.local/share/uv/python"
  --ro-bind "$U/.local/bin/uv" "$U/.local/bin/uv"
  --ro-bind "$U/go/pkg/mod/cache/download" /opt/gomodcache
  --bind "$CO" "$CO" --chdir "$CO"
  ${EXTRA_RO:+--ro-bind "$EXTRA_RO" "$EXTRA_RO"}   # steward's mutation of the check only: plant one forbidden path
  --bind "$SOCKDIR" /run/egress --ro-bind "$SD/sandbox-relay.py" /opt/sandbox-relay.py
  --setenv HTTPS_PROXY http://127.0.0.1:3128 --setenv https_proxy http://127.0.0.1:3128
  --setenv HTTP_PROXY http://127.0.0.1:3128 --setenv http_proxy http://127.0.0.1:3128
  --setenv ALL_PROXY http://127.0.0.1:3128 --setenv NO_PROXY localhost,127.0.0.1 --setenv no_proxy localhost,127.0.0.1
  --setenv HOME "$U" --setenv USER tony --setenv TERM "${TERM:-xterm}" --setenv LANG C.UTF-8
  --setenv PATH "$NODE/bin:/usr/local/go/bin:$U/.local/bin:/usr/bin"
  --setenv UV_OFFLINE 1 --setenv GOMODCACHE "$U/go/pkg/mod" --setenv GOPROXY file:///opt/gomodcache --setenv GOSUMDB off --setenv GOFLAGS -modcacherw)   # go.sum still verifies
case $H in
  codex) args+=(--ro-bind "$U/node_modules/@openai" "$U/node_modules/@openai")
         # account-side tools reach past the file sandbox (codex_apps: GitHub, mail, SharePoint; web; browsers), so off
         cmd=("$NODE/bin/node" "$U/node_modules/@openai/codex/bin/codex.js" -c 'web_search="disabled"')
         for f in apps plugins remote_plugin browser_use browser_use_external in_app_browser computer_use image_generation \
                  skill_mcp_dependency_install tool_suggest; do cmd+=(-c "features.$f=false"); done ;;
  grok)  args+=(--ro-bind "$GROKBIN" /opt/grok
                --setenv GROK_CLAUDE_AGENTS_ENABLED 0 --setenv GROK_CLAUDE_HOOKS_ENABLED 0 --setenv GROK_CLAUDE_MCPS_ENABLED 0
                --setenv GROK_CLAUDE_RULES_ENABLED 0 --setenv GROK_CLAUDE_SKILLS_ENABLED 0 --setenv GROK_WORKFLOWS 0)
         # --trust loads AGENTS.md (author checkouts hold no .grok/). An allowlist of internal tool IDs: X search, media
         # and workflows run on xAI's side, past the proxy, and a denylist by shown name removed nothing (2026-10-23)
         cmd=(/opt/grok --trust --disable-web-search --tools \
           run_terminal_cmd,read_file,write,search_replace,list_dir,grep,todo_write,task,get_task_output,wait_tasks,kill_task) ;;
  *) echo "harness: codex|grok" >&2; exit 2 ;;
esac
CRED=$U/.$H/auth.json; ACRED=$AH/.$H/auth.json
[ -s "$CRED" ] || { echo "no credential at $CRED (log in on the host first)" >&2; exit 2; }
mkdir -p "$(dirname "$ACRED")"; install -m 600 "$CRED" "$ACRED"; ORIG=$(sha256sum < "$CRED")
[ -n "${PROBE:-}" ] && cmd=(bash)   # PROBE=1: a shell in the same sandbox, for the steward's access probes
# the relay starts first; the harness waits for its port
bwrap "${args[@]}" bash -c '/usr/bin/python3 /opt/sandbox-relay.py /run/egress/egress.sock & for _ in $(seq 50); do
  (exec 3<>/dev/tcp/127.0.0.1/3128) 2>/dev/null && break; sleep 0.1; done; exec "$@"' relay "${cmd[@]}" "$@" && rc=0 || rc=$?
if [ -s "$ACRED" ] && [ "$(sha256sum < "$ACRED")" != "$ORIG" ]; then
  if [ "$(sha256sum < "$CRED")" = "$ORIG" ] && python3 -c 'import json,sys; a,b=(json.load(open(f)) for f in sys.argv[1:]); sys.exit(0 if isinstance(a,dict) and a.keys()==b.keys() else 1)' "$ACRED" "$CRED"; then
    install -m 600 "$ACRED" "$CRED.tupay-new" && mv "$CRED.tupay-new" "$CRED" && echo "author-sandbox: rotated $H credential written back" >&2
  else echo "author-sandbox: $H credential rotated in the sandbox but not written back (Tony's changed meanwhile, or shape differs); copy kept at $ACRED" >&2; fi
fi
exit $rc
