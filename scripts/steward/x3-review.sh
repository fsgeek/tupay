#!/bin/bash
# Adversarial review of the X3 result draft by Gemini (agy in a deny-all workspace), one run.
# usage: x3-review.sh <packet.md> <out-dir>
# derives: steward practice "Before publication, a non-steward family reviews the scoring adversarially"; X3 owed item (7)
set -uo pipefail
P=$(realpath "$1"); G=$(realpath -m "$2"); SD=$(dirname "$(realpath "$0")"); [ -e "$G" ] && { echo "exists: $G"; exit 1; }
"$SD/d1-agy-workspace.sh" "$G" >/dev/null; sha256sum "$P" > "$G/packet.sha256"
python3 -c 'import json,sys; print(json.dumps({"event":"user","message":{"role":"user","content":open(sys.argv[1]).read()}}))' "$P" > "$G/stdin.jsonl"
date -u +%FT%TZ > "$G/start.txt"
(cd "$G" && exec agy --print='' --input-format stream-json --output-format stream-json --disable-slash-commands < stdin.jsonl > transcript.jsonl 2> stderr.txt) &
A=$!
for _ in $(seq 1800); do kill -0 $A 2>/dev/null || break; grep -q '"event": *"result"' "$G/transcript.jsonl" 2>/dev/null && { sleep 5; kill $A 2>/dev/null; echo "killed after result event" >> "$G/stderr.txt"; break; }; sleep 2; done
kill -9 $A 2>/dev/null; date -u +%FT%TZ > "$G/end.txt"
python3 - "$G" <<'PY'
import json, re, sys, os
G = sys.argv[1]; tools = 0; resp = ''
for l in open(f'{G}/transcript.jsonl'):
    try: r = json.loads(l)
    except ValueError: continue
    if (r.get('step_update') or {}).get('step_type') == 'tool': tools += 1
    if r.get('event') == 'result': resp = r['result'].get('response', '')
open(f'{G}/response.md', 'w').write(resp)
m = re.search(r'\{.*\}', resp, flags=re.S)
try: j = json.loads(m.group(0)) if m else None
except ValueError: j = None
json.dump(j, open(f'{G}/review.json', 'w'), indent=1)
d = os.path.getsize(f'{G}/.agents/denied.jsonl') if os.path.exists(f'{G}/.agents/denied.jsonl') else 0
print(f'gemini: tool steps {tools}, denied bytes {d}, parsed {j is not None}, findings {len((j or {}).get("findings", []))}, headline_holds {(j or {}).get("headline_holds")}')
PY
