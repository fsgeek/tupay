#!/usr/bin/env python3
"""One outside review of the W2 pre-registration draft before registration (steward practice: read the inputs as an
outsider would; stop rule: one review, then only blocking items are fixed, without a further check).
usage: w2-review.py <model-id> <out-dir>   (OPENROUTER_API_KEY in the environment)
derives: steward practice "Read the inputs as an outsider would"; log 2026-11-23 (W2 to be registered)."""
import json, os, sys, hashlib, urllib.request, pathlib, re
T = pathlib.Path('/home/tony/projects/tupay')
model, out = sys.argv[1], pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
src = (T / 'scripts/steward/w1-interface-draft.py').read_text()
drafter_task = src[src.index('task = """') + 10: src.index('"""', src.index('task = """') + 10)]
task = """You are an outside reviewer of a pre-registration that has not yet been registered. Read it adversarially. Kinds of defect to look for, not suspicions: a prediction that cannot fail, or that the design makes likely whatever the truth; a measure whose count can be steered after outcomes are seen; a confound that makes the two forms' cells not comparable; a scoring rule that is ambiguous or incomplete; a missing rule for a case that will plausibly occur. Report numbered findings, each with severity (blocking / significant / minor), where, what is wrong, why (quote the text), and a one-line fix. Blocking means: the experiment cannot be scored fairly unless it is fixed. If you find nothing blocking, say so."""
parts = [task, '\n\n===== THE PRE-REGISTRATION DRAFT =====\n', (T / 'experiments/W2-prereg.md').read_text(),
         '\n\n===== THE DRAFTERS\' TASK TEXT (sent unchanged to every cell, followed by one contract form and the binding) =====\n', drafter_task]
packet = ''.join(parts); (out / 'packet.md').write_text(packet)
h = hashlib.sha256(packet.encode()).hexdigest()[:16]
req = {'model': model, 'messages': [{'role': 'user', 'content': packet}], 'temperature': 0}
r = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(req).encode(),
    headers={'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'})
resp = json.load(urllib.request.urlopen(r, timeout=3600)); (out / 'response.json').write_text(json.dumps(resp, indent=1))
c = resp['choices'][0]; (out / 'review.md').write_text(c['message'].get('content') or '')
print(len(packet), 'chars; sha256', h, '; finish', c.get('finish_reason'), '; cost', resp.get('usage', {}).get('cost'))
