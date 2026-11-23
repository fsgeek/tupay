#!/usr/bin/env python3
"""W2: run one cell (family x form) of the census. Fixes for Kimi's findings 3, 4 and 5 (uniform policy, fixed words).
usage: w2-cell.py <model-id> <F|P> <out-dir>   (OPENROUTER_API_KEY in the environment; REASONING_MAX for GLM, as in GLM-P)
derives: experiments/W2-prereg.md § Design. Frozen at registration; changing it is a new version, logged.
The task string is read from w1-interface-draft.py (unchanged since 9de78d2), and the packet is built exactly as there,
with the contract file swapped. Policy, the same for every cell:
 1. One call (temperature 0; no max_tokens; reasoning capped only where REASONING_MAX is set).
 2. If the reply's content is empty: one full rerun with the identical request (GLM-P had this, as its second attempt).
 3. If w2-count.py then finds no CONTRACT QUESTIONS section: one continuation, in CONT's exact words, as a second turn;
    its reply is saved as continuation.md, and w2-count.py reads the section from it.
 4. Otherwise nothing further. A cell still without a section is "missing".
"""
import json, os, sys, hashlib, urllib.request, pathlib, subprocess
T = pathlib.Path('/home/tony/projects/tupay')
model, form, out = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
CONT = 'Your reply was cut off by a transport error at the heading "# 11. CONTRACT QUESTIONS". Write that section only, as the task asked: each place where you could not design injection or observation because the contract itself is unclear, with the text quoted, unresolved. Do not repeat or revise sections 0 to 10.'
# CONT is the exact text the steward sent for Mistral-P on 2026-11-23. That request was not saved, only its response
# (experiments/W1/interface/mistral/continuation-response.json); the words are copied from the command that sent it.
# Its section numbers (11, 0 to 10) fit Mistral-P's draft; they are kept unchanged for every cell (known limit 5).
src = (T / 'scripts/steward/w1-interface-draft.py').read_text()
task = src[src.index('task = """') + 10: src.index('"""', src.index('task = """') + 10)]
cf = T / f'experiments/W1/inputs/contract-{form}.md'
files = [('THE CONTRACT AND FAILURE MODEL', cf), ('THE BINDING (maps the contract roles to machines and values)', T / 'docs/backup/binding-tupay.md')]
packet = ''.join([task] + [f'\n\n===== {t} ({p.name}) =====\n' + p.read_text() for t, p in files])
(out / 'packet.md').write_text(packet)
def call(msgs):
    req = {'model': model, 'messages': msgs, 'temperature': 0}
    if os.environ.get('REASONING_MAX'): req['reasoning'] = {'max_tokens': int(os.environ['REASONING_MAX'])}
    r = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(req).encode(),
        headers={'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(r, timeout=3600))
log = []
msgs = [{'role': 'user', 'content': packet}]
resp = call(msgs); (out / 'response.json').write_text(json.dumps(resp, indent=1))
content = resp['choices'][0]['message'].get('content') or ''; log.append(('first', resp['choices'][0].get('finish_reason'), len(content), resp.get('usage', {}).get('cost')))
if not content.strip():
    resp = call(msgs); (out / 'response-rerun.json').write_text(json.dumps(resp, indent=1))
    content = resp['choices'][0]['message'].get('content') or ''; log.append(('rerun', resp['choices'][0].get('finish_reason'), len(content), resp.get('usage', {}).get('cost')))
(out / 'draft.md').write_text(content)
cnt = json.loads(subprocess.run([sys.executable, str(T / 'scripts/steward/w2-count.py'), str(out)], capture_output=True, text=True).stdout)
if cnt['status'] == 'missing' and content.strip():
    r2 = call(msgs + [{'role': 'assistant', 'content': content}, {'role': 'user', 'content': CONT}])
    (out / 'continuation-response.json').write_text(json.dumps(r2, indent=1))
    c2 = r2['choices'][0]['message'].get('content') or ''; (out / 'continuation.md').write_text(c2)
    log.append(('continuation', r2['choices'][0].get('finish_reason'), len(c2), r2.get('usage', {}).get('cost')))
    cnt = json.loads(subprocess.run([sys.executable, str(T / 'scripts/steward/w2-count.py'), str(out)], capture_output=True, text=True).stdout)
s = {'model': model, 'form': form, 'packet_sha256': hashlib.sha256(packet.encode()).hexdigest(), 'calls': log, 'status': cnt['status'], 'q': cnt['q']}
(out / 'cell.json').write_text(json.dumps(s, indent=1)); print(json.dumps(s))
