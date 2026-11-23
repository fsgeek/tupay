#!/usr/bin/env python3
"""SMR line: revise merged inputs v1 into v2 under the steward's second dispositions, by one family (run two in parallel).
usage: smr-input-revise.py <model-id> <out-dir>   (OPENROUTER_API_KEY in the environment; sent only in this request)
derives: fourteenth's acceptance decision 3 (the steward disposes, two families draft); DISPOSITIONS-2.md's stop rule.
Inputs: the paper's text, v1 (merge/qwen/merged.md), Kimi's check of v1, DISPOSITIONS-2.md. All stay in ../tupay-private/smr."""
import json, os, sys, hashlib, urllib.request, pathlib
S = pathlib.Path('/home/tony/projects/tupay-private/smr')
model, out = sys.argv[1], pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
files = [('DECISIONS (binding)', S / 'DISPOSITIONS-2.md'),
         ('REVIEW OF VERSION 1', S / 'check/kimi/check.md'),
         ('VERSION 1', S / 'merge/qwen/merged.md'),
         ('THE PAPER (text extraction)', S / 'paper.txt')]
task = """Below are a research paper, version 1 of the inputs derived from it for a verification workflow (service contract, failure model, environment, design obligations, design checks, test interface), an independent review of version 1, and a set of binding DECISIONS on that review.

Write version 2: the complete document, not a list of changes. Independent model and implementation teams will work from the paper and version 2 alone, and one shared suite of schedules in version 2's format will run against both.

Rules:
1. Apply the DECISIONS exactly. Where they state a principle, write the concrete text that realises it: schemas, algorithms, defaults and rules precise enough that two engineers would build the same harness.
2. Keep every element of version 1 that the decisions do not change, with its id. New elements get new ids continuing each series (never reuse an id; an element removed from the shared suite keeps its id and says so).
3. Each element keeps its quote from the paper and a `sources:` line; add `revised: <review finding ids>; decision <ids>` to every element you change.
4. Do not weaken any guarantee the paper states and do not add environment guarantees the paper does not state. Where the review asks for either, leave the paper's text standing and record the tension as a paper question.
5. The test interface must include: the device and its crash-state construction (deterministic, as decided); the harness calls an implementation must accept (including the background call and logical time); injection by crash-point sweeps; the per-sector safety oracle; self-describing data; scoring and result kinds; geometry, units, defaults and format; model capability declarations; and one complete example schedule that sweeps crash points over a workload reaching eviction or GC, with its expected results stated.
6. End with: KNOWN LIMITS (each clause or element not tested by the shared suite, with the review finding that put it there); PAPER QUESTIONS (carried and new); OPEN (anything the decisions require that you could not specify, saying why; empty if none).

Be complete rather than brief."""
packet = task + ''.join(f'\n\n===== {t} =====\n' + p.read_text() for t, p in files)
(out / 'packet.md').write_text(packet)
h = hashlib.sha256(packet.encode()).hexdigest()[:16]
if os.environ.get('DRY'): print(len(packet), 'chars; packet sha256', h, '(dry run)'); sys.exit()
req = {'model': model, 'messages': [{'role': 'user', 'content': packet}], 'temperature': 0}
if os.environ.get('REASONING_MAX'): req['reasoning'] = {'max_tokens': int(os.environ['REASONING_MAX'])}
r = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(req).encode(),
    headers={'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'})
resp = json.load(urllib.request.urlopen(r, timeout=3600))
(out / 'response.json').write_text(json.dumps(resp, indent=1))
(out / 'v2.md').write_text(resp['choices'][0]['message']['content'] or '')
print(len(packet), 'chars; packet sha256', h, '; model', resp.get('model'), '; finish', resp['choices'][0].get('finish_reason'), '; usage', resp.get('usage'))
