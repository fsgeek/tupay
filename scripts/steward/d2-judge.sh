#!/bin/bash
# D2 phase 3 judges other than Episode's steward: Gemini (registered; agy in a deny-all workspace, killed after its result
# event) and GLM (beside, never instead; log 2026-10-27 "more families offered"). The sealed file is appended to the packet
# here, from Episode's commit, so the steward never reads it. Neither judge sees another's ruling.
# usage: d2-judge.sh <packet.md> <out-dir>
# derives: experiments/D2/design.md draft 2, phase 3 step 3; log 2026-10-29 "D2 phase 3 step 2"
set -uo pipefail
P=$(realpath "$1"); O=$(realpath -m "$2"); SD=$(dirname "$(realpath "$0")"); [ -e "$O" ] && { echo "exists: $O"; exit 1; }
SEALED_SHA=227d250888122a852f8b477dee3c6ff2fd0975d339ad341d85a4ef6f6b7b9698
mkdir -p "$O"; S=$(git -C "$HOME/projects/episode" show 7eeb027:sealed/2026-10-26-tupay-D2-findings.md) || exit 1
[ "$(printf '%s\n' "$S" | sha256sum | cut -d' ' -f1)" = "$SEALED_SHA" ] || { echo "sealed hash mismatch"; exit 1; }
{ sed 's/{SEALED_WHERE}/at the end of this packet, under "The sealed analysis"/' "$P"; printf '\n## The sealed analysis (sealed 2026-10-26, before any list existed)\n\n%s\n' "$S"; } > "$O/packet-sent.md"
sha256sum "$O/packet-sent.md" | cut -d' ' -f1 > "$O/packet-sent.sha256"; G=$O/gemini
"$SD/d1-agy-workspace.sh" "$G" >/dev/null
python3 -c 'import json,sys; print(json.dumps({"event":"user","message":{"role":"user","content":open(sys.argv[1]).read()}}))' "$O/packet-sent.md" > "$G/stdin.jsonl"
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
print(f'gemini: tool steps {tools}, denied bytes {d}, parsed {j is not None}, items {sum(len(v) for v in (j or {}).values() if isinstance(v, list))}')
PY
K=$O/glm; mkdir -p "$K"; date -u +%FT%TZ > "$K/start.txt"
python3 - "$O/packet-sent.md" "$K" <<'PY'
import json, os, re, sys, urllib.request
P, K = sys.argv[1:]; model = 'z-ai/glm-5.3-prime'
req = {'model': model, 'messages': [{'role': 'user', 'content': open(P).read()}], 'temperature': 0}
r = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(req).encode(),
    headers={'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'})
resp = json.load(urllib.request.urlopen(r, timeout=3600)); json.dump(resp, open(f'{K}/response.json', 'w'), indent=1)
txt = resp['choices'][0]['message']['content'] or ''; open(f'{K}/response.md', 'w').write(txt)
m = re.search(r'\{.*\}', txt, flags=re.S)
try: j = json.loads(m.group(0)) if m else None
except ValueError: j = None
json.dump(j, open(f'{K}/ruling.json', 'w'), indent=1)
print(f'glm ({resp.get("model")}): parsed {j is not None}, items {sum(len(v) for v in (j or {}).values() if isinstance(v, list))}, cost {(resp.get("usage") or {}).get("cost")}')
PY
date -u +%FT%TZ > "$K/end.txt"
