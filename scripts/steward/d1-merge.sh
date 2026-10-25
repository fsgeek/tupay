#!/bin/bash
# Run one D1 phase 1 merge: a fresh agy (Gemini) in its own deny-all workspace, the packet inline.
# usage: d1-merge.sh <phase0-dir> <out-dir>     (out-dir must not exist; run twice, into two out-dirs, for A and B)
# derives: experiments/D1/design.md draft 3, phase 1 "Merge"; log 2026-10-25 "a workspace hook denies every agy tool"
set -euo pipefail
P0=$(realpath "$1"); O=$(realpath -m "$2"); SD=$(dirname "$(realpath "$0")"); MAIN=$(dirname "$(dirname "$SD")")
[ -e "$O" ] && { echo "exists: $O"; exit 1; }
"$SD/d1-agy-workspace.sh" "$O" >/dev/null
{ cat "$MAIN/experiments/D1/brief-merge.md"; python3 "$SD/d1-phase1.py" packet "$P0"; } > "$O/packet.md"
date -u +%FT%TZ > "$O/start.txt"
# the packet goes on stdin (a single argv string is capped at 128 KiB; four lists come near it); format probed 2026-10-25
python3 -c 'import json,sys; print(json.dumps({"event":"user","message":{"role":"user","content":open(sys.argv[1]).read()}}))' "$O/packet.md" > "$O/stdin.jsonl"
(cd "$O" && agy --print='' --input-format stream-json --output-format stream-json --disable-slash-commands < stdin.jsonl > transcript.jsonl 2> stderr.txt) || echo "agy exit $?" >> "$O/stderr.txt"
date -u +%FT%TZ > "$O/end.txt"
python3 - "$O" <<'PY'
import json, re, sys
O = sys.argv[1]; tools = 0; resp = ''
for l in open(f'{O}/transcript.jsonl'):
    try: r = json.loads(l)
    except ValueError: continue
    su = r.get('step_update') or {}
    if su.get('step_type') == 'tool': tools += 1
    if r.get('event') == 'result': resp = r['result'].get('response', '')
m = re.search(r'\{.*\}', resp, flags=re.S)
json.dump(json.loads(m.group(0)) if m else {'groups': []}, open(f'{O}/merge.json', 'w'), indent=1)
import os
denied = os.path.getsize(f'{O}/.agents/denied.jsonl') if os.path.exists(f'{O}/.agents/denied.jsonl') else 0
print(f'{O}: tool steps {tools}, denied bytes {denied}, groups {len(json.load(open(f"{O}/merge.json"))["groups"])}, parsed {bool(m)}')
PY
