#!/bin/bash
# Send one X3 rater packet to one OpenRouter model; write response.json, response.md, ratings.json.
# usage: rate.sh <packet.md> <model> <out-dir>
# derives: X3 prereg measures 6 and 7; log 2026-11-01 "X3 measures 6 and 7: raters and packets, before any rating"
set -euo pipefail
P=$(realpath "$1"); M=$2; O=$3; [ -e "$O" ] && { echo "exists: $O"; exit 1; }; mkdir -p "$O"
sha256sum "$P" > "$O/packet.sha256"; date -u +%FT%TZ > "$O/start.txt"
python3 - "$P" "$M" "$O" <<'PY'
import json, os, re, sys, urllib.request
P, M, O = sys.argv[1:]
req = {'model': M, 'messages': [{'role': 'user', 'content': open(P).read()}], 'temperature': 0, 'max_tokens': int(os.environ.get('MAXTOK', 40000))}
if os.environ.get('REASON'): req['reasoning'] = {'max_tokens': int(os.environ['REASON'])}
r = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(req).encode(),
    headers={'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'})
resp = json.load(urllib.request.urlopen(r, timeout=3600)); json.dump(resp, open(f'{O}/response.json', 'w'), indent=1)
ch = resp['choices'][0]; txt = ch['message'].get('content') or ''; open(f'{O}/response.md', 'w').write(txt)
m = re.search(r'\{.*\}', txt, flags=re.S)
try: j = json.loads(m.group(0)) if m else None
except ValueError: j = None
json.dump(j, open(f'{O}/ratings.json', 'w'), indent=1)
n = len((j or {}).get('ratings', []))
print(f'{M}: finish {ch.get("finish_reason")}, parsed {j is not None}, {n} ratings, cost {(resp.get("usage") or {}).get("cost")}')
PY
date -u +%FT%TZ > "$O/end.txt"
