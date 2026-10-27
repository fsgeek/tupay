#!/bin/bash
# Judge one X3 packet: Gemini (registered judge; agy in a deny-all workspace) and Kimi (second reading, reported beside,
# never instead; log 2026-10-27 "more families offered"). Neither sees the other's ruling.
# usage: run.sh <packet.md> <out-dir>
# derives: experiments/X3-prereg.md measure 2; steward practice "Running and judging"; log 2026-10-27 "D2 phase 1 merges
# run; agy hung after its answer" (an agy run is finished when its result event is in the transcript; kill it then)
set -uo pipefail
P=$(realpath "$1"); O=$(realpath -m "$2"); SD=$(dirname "$(realpath "$0")"); [ -e "$O" ] && { echo "exists: $O"; exit 1; }
mkdir -p "$O"; cp "$P" "$O/packet.md"; G=$O/gemini
"$SD/../d1-agy-workspace.sh" "$G" >/dev/null
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
json.dump(j, open(f'{G}/ruling.json', 'w'), indent=1)
d = os.path.getsize(f'{G}/.agents/denied.jsonl') if os.path.exists(f'{G}/.agents/denied.jsonl') else 0
print(f'gemini: tool steps {tools}, denied bytes {d}, parsed {j is not None}', (j or {}).get('verdict'), (j or {}).get('locus'))
PY
K=$O/kimi; mkdir -p "$K"; date -u +%FT%TZ > "$K/start.txt"
python3 - "$P" "$K" <<'PY'
import json, os, re, sys, urllib.request
P, K = sys.argv[1:]; model = 'moonshotai/kimi-k3.1-pro'
req = {'model': model, 'messages': [{'role': 'user', 'content': open(P).read()}], 'temperature': 0}
r = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(req).encode(),
    headers={'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'})
resp = json.load(urllib.request.urlopen(r, timeout=3600)); json.dump(resp, open(f'{K}/response.json', 'w'), indent=1)
txt = resp['choices'][0]['message']['content']; open(f'{K}/response.md', 'w').write(txt)
m = re.search(r'\{.*\}', txt, flags=re.S)
try: j = json.loads(m.group(0)) if m else None
except ValueError: j = None
json.dump(j, open(f'{K}/ruling.json', 'w'), indent=1)
print(f'kimi ({resp.get("model")}): parsed {j is not None}', (j or {}).get('verdict'), (j or {}).get('locus'), 'usage', (resp.get('usage') or {}).get('cost'))
PY
date -u +%FT%TZ > "$K/end.txt"
