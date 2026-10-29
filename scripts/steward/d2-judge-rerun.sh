#!/bin/bash
# One fresh rerun of a D2 judge whose first answer did not parse (a harness failure, not an outcome; log 2026-10-29
# "D2 judges: harness failures rerun"). The packet sent is the first run's packet-sent.md, unchanged (hash checked).
# usage: d2-judge-rerun.sh <gemini|glm> <judge-dir>     -> <judge-dir>/<judge>-2/
# derives: experiments/D2/design.md draft 2, phase 3 step 3; scripts/steward/d2-judge.sh
set -uo pipefail
J=$1; O=$(realpath "$2"); SD=$(dirname "$(realpath "$0")"); P=$O/packet-sent.md
[ "$(sha256sum < "$P" | cut -d' ' -f1)" = "$(cat "$O/packet-sent.sha256")" ] || { echo "packet changed"; exit 1; }
D=$O/$J-2; [ -e "$D" ] && { echo "exists: $D"; exit 1; }
if [ "$J" = gemini ]; then
  "$SD/d1-agy-workspace.sh" "$D" >/dev/null
  python3 -c 'import json,sys; print(json.dumps({"event":"user","message":{"role":"user","content":open(sys.argv[1]).read()}}))' "$P" > "$D/stdin.jsonl"
  date -u +%FT%TZ > "$D/start.txt"
  (cd "$D" && exec agy --print='' --input-format stream-json --output-format stream-json --disable-slash-commands < stdin.jsonl > transcript.jsonl 2> stderr.txt) &
  A=$!
  for _ in $(seq 1800); do kill -0 $A 2>/dev/null || break; grep -q '"event": *"result"' "$D/transcript.jsonl" 2>/dev/null && { sleep 5; kill $A 2>/dev/null; break; }; sleep 2; done
  kill -9 $A 2>/dev/null; wait $A 2>/dev/null; date -u +%FT%TZ > "$D/end.txt"
  python3 - "$D" <<'PY'
import json, re, sys
D = sys.argv[1]; resp = ''
for l in open(f'{D}/transcript.jsonl'):
    try: r = json.loads(l)
    except ValueError: continue
    if r.get('event') == 'result': resp = r['result'].get('response', '')
open(f'{D}/response.md', 'w').write(resp); m = re.search(r'\{.*\}', resp, flags=re.S)
try: j = json.loads(m.group(0)) if m else None
except ValueError: j = None
json.dump(j, open(f'{D}/ruling.json', 'w'), indent=1)
print('gemini-2 parsed', j is not None, 'items', sum(len(v) for v in (j or {}).values() if isinstance(v, list)))
PY
else
  mkdir -p "$D"; date -u +%FT%TZ > "$D/start.txt"
  python3 - "$P" "$D" <<'PY'
import json, os, re, sys, urllib.request
P, D = sys.argv[1:]
req = {'model': 'z-ai/glm-5.3-prime', 'messages': [{'role': 'user', 'content': open(P).read()}], 'temperature': 0,
       'max_tokens': 65536, 'reasoning': {'max_tokens': 24000}}
r = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(req).encode(),
    headers={'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'})
resp = json.load(urllib.request.urlopen(r, timeout=3600)); json.dump(resp, open(f'{D}/response.json', 'w'), indent=1)
c = resp['choices'][0]; txt = c['message'].get('content') or ''; open(f'{D}/response.md', 'w').write(txt)
m = re.search(r'\{.*\}', txt, flags=re.S)
try: j = json.loads(m.group(0)) if m else None
except ValueError: j = None
json.dump(j, open(f'{D}/ruling.json', 'w'), indent=1)
print('glm-2 finish', c.get('finish_reason'), 'parsed', j is not None, 'items', sum(len(v) for v in (j or {}).values() if isinstance(v, list)), 'cost', (resp.get('usage') or {}).get('cost'))
PY
  date -u +%FT%TZ > "$D/end.txt"
fi
