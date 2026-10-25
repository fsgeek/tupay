#!/bin/bash
# A workspace for one D1 phase 1 merge: agy runs there with a workspace PreToolUse hook that denies every tool call
# (search_web runs headless without permission, so permissions alone do not keep agy off the web; log 2026-10-25).
# usage: d1-agy-workspace.sh <dir>     then: cd <dir> && agy -p "<packet>" --output-format stream-json --disable-slash-commands
# derives: experiments/D1/design.md draft 3, phase 1 "Merge"; Fable review finding 10
# Proven 2026-10-25 by three probes (search_web, a shell curl, read_url_content; the last two with
# --dangerously-skip-permissions): each tool step ended ERROR, "denied by a pre-tool hook". Every denied call is
# appended to <dir>/.agents/denied.jsonl; a merge transcript with any tool step, or a non-empty denied.jsonl, is reported.
set -euo pipefail
W=$(realpath -m "$1"); [ -e "$W" ] && { echo "exists: $W"; exit 1; }
mkdir -p "$W/.agents"
cat > "$W/.agents/deny-all.sh" <<'H'
#!/bin/bash
cat >> "$(dirname "$0")/denied.jsonl"; echo >> "$(dirname "$0")/denied.jsonl"
echo '{"decision":"deny","reason":"D1 merge: no tools; answer from the prompt alone."}'
H
chmod +x "$W/.agents/deny-all.sh"
printf '{\n  "d1-deny-all": {\n    "PreToolUse": [\n      { "matcher": ".*", "hooks": [ { "command": "%s/.agents/deny-all.sh" } ] }\n    ]\n  }\n}\n' "$W" > "$W/.agents/hooks.json"
echo "$W"
