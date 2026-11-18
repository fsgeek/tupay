#!/usr/bin/env python3
"""Outside-family review before W1 is registered: (A) is the prose arm obligation-equivalent to draft 7,
clause by clause; (B) an adversarial reading of the W1 pre-registration draft.
usage: w1-review.py <model-id> <out-dir>   (OPENROUTER_API_KEY in the environment; sent only in this request)
derives: steward practice "Read the inputs as an outsider would"; twelfth handoff, next item 1; log 2026-11-18.
No steward hypotheses: the task names kinds of defect, never a suspected one. The reviewer has no tools,
and its family (Kimi) takes no other role in W1."""
import json, os, sys, hashlib, urllib.request, pathlib
T = pathlib.Path('/home/tony/projects/tupay')
model, out = sys.argv[1], pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
files = [('ARM F: the four-part contract (draft 7), the treatment arm, fixed', T / 'docs/backup/contract-draft-7.md'),
         ('the binding both arms share', T / 'docs/backup/binding-tupay.md'),
         ('ARM P: the prose arm, meant to carry the same obligations', T / 'docs/backup/contract-prose-arm-draft-1.md'),
         ('the W1 pre-registration draft under review', T / 'experiments/W1-prereg-draft-2.md')]
task = """You are an outside reviewer for an experiment that has not yet been registered. Two contracts for one backup service are meant to carry the same obligations in two forms: ARM F (a four-part controlled form) and ARM P (plain prose). Separate implementation and formal-model authors will build from each. The W1 pre-registration says how the arms will be compared.

Part A, equivalence. For every clause and defined-term id in ARM F, check whether ARM P imposes the same obligation: the same actor, the same condition, the same deadline or parameter, the same effect under each failure cell, the same reporting. List every difference of obligation (missing, added, weaker, stronger, or changed in scope), quoting both texts. Differences of wording alone are not findings. ARM F is fixed; for each difference, say what ARM P would need to change. Also list any id present in one and absent in the other.

Part B, the pre-registration, read adversarially. Kinds of defect to look for, not suspicions: a prediction that cannot fail, or that the design makes likely whatever the truth; a measure or classification that leaves room to choose after seeing outcomes; a confound that would explain the predicted result without the treatment; a threshold or scoring rule that is ambiguous; information that could reach an author or judge and bias them; a stated limit that is in fact disqualifying; anything in the baseline comparison that is unfair in a way the text does not admit. Say plainly if, in your judgment, the experiment as designed cannot answer its question, and why.

Report numbered findings, each with: part (A or B), severity (blocking / significant / minor), where (id or section), what is wrong, and why (quote the text). One-line suggested fix per finding. If an area is sound, say so in one line."""
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
