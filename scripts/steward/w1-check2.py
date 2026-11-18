#!/usr/bin/env python3
"""Outside-family SECOND and last CHECK (stop rule, log 2026-11-18), of W1 draft 4's fixes for Kimi's first check (not a new review round): are findings 1-26
resolved, and did the fixes introduce new defects? usage: w1-check2.py <model-id> <out-dir>   (OPENROUTER_API_KEY in the environment; sent only in this request)
derives: docs/backup/review/kimi-w1/DISPOSITIONS.md ("the patch is checked once more"); log 2026-11-18.
No steward hypotheses: the task names kinds of defect, never a suspected one. The reviewer has no tools,
and its family (Kimi) takes no other role in W1."""
import json, os, sys, hashlib, urllib.request, pathlib
T = pathlib.Path('/home/tony/projects/tupay')
model, out = sys.argv[1], pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
files = [('YOUR FIRST CHECK (of W1 draft 3)', T / 'docs/backup/review/kimi-w1/check-1.md'),
         ('THE CHANGE: unified diff from W1 draft 3 to draft 4', T / 'tmp/w1-check2/w1-3-to-4.diff'),
         ('W1 pre-registration, NEW: draft 4', T / 'experiments/W1-prereg-draft-4.md'),
         ('ARM F (draft 7), for reference on clause semantics', T / 'docs/backup/contract-draft-7.md')]
task = """You checked W1 draft 3 before; that check is included. The steward has written draft 4 (the diff is included). This is the last check before registration: after it, only blocking items will be fixed, and anything else becomes a stated limit.

1. For each item of your check that was partly resolved or new (19, 21, 26, 27, 28, 29, 30, 31, 32): is it resolved by draft 4? Answer resolved / partly / not resolved, quoting the new text.
2. Did draft 4's changes introduce NEW defects of the kinds you looked for (an outcome that cannot fail, room to choose after seeing outcomes, a confound, an ambiguous or undeterminable scoring rule, a leak, a disqualifying limit, an unfair comparison)? Check every hunk of the diff.

Report numbered items with severity (blocking / significant / minor), where, what, why (quote), and a one-line fix. Use blocking only for something that would leave a registered prediction unscorable or decidable after outcomes are seen. End with one line: whether W1 draft 4 is fit to register as an exploratory pilot."""
parts = [task] + [f'\n\n===== {t} ({p.name}) =====\n' + p.read_text() for t, p in files]
packet = ''.join(parts); (out / 'packet.md').write_text(packet)
h = hashlib.sha256(packet.encode()).hexdigest()[:16]
if os.environ.get('DRY'): print(len(packet), 'chars; packet sha256', h, '(dry run)'); sys.exit()
req = {'model': model, 'messages': [{'role': 'user', 'content': packet}], 'temperature': 0}
r = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(req).encode(),
    headers={'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'})
resp = json.load(urllib.request.urlopen(r, timeout=3600))
(out / 'response.json').write_text(json.dumps(resp, indent=1))
(out / 'review.md').write_text(resp['choices'][0]['message']['content'] or '')
print(len(packet), 'chars; packet sha256', h, '; model', resp.get('model'), '; usage', resp.get('usage'))
