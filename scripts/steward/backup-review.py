#!/usr/bin/env python3
"""Outside-family review of the backup contract draft, for defects, before the prose arm is derived or anything registered.
usage: backup-review.py <model-id> <out-dir>   (OPENROUTER_API_KEY in the environment; sent only in this one request)
derives: steward practice "Read the inputs as an outsider would"; log 2026-11-08 "backup contract draft 2", next.
Packet: the draft whole, and backup.sh whole (the rung below, which section 9 makes claims about). No steward
hypotheses: the task names kinds of defect, never a suspected one. The reviewer has no tools."""
import json, os, sys, hashlib, urllib.request, pathlib
T = pathlib.Path('/home/tony/projects/tupay')
model, out = sys.argv[1], pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
files = [('the contract draft under review', T / 'docs/backup/contract-draft-2.md'),
         ('the existing script, the "rung below" (section 9 makes claims about it)', T / 'scripts/steward/backup.sh')]
task = """You are reviewing, adversarially, a draft service contract and failure model for a backup service, before any implementation author sees it. Authors will build from it; a formal model and an implementation will be tested against it; failure cells will be injected.

Find defects in it. Kinds of defect to look for, not suspicions: a term used in more than one meaning or undefined; a clause that cannot be satisfied, or is satisfied vacuously; two clauses that contradict; a clause whose obligation depends on an unstated assumption; an interpretation record that does not match its clause; a (clause x failure cell) effect in section 5 that is wrong, or a pair marked H (holds, by omission) that does not in fact hold; a failure a backup service of this shape plausibly meets that no cell names; a parameter whose derivation does not follow; a claim in section 9 about the script that the script contradicts; anything that prescribes a protocol when it says it does not.

Report a numbered list of findings, each with: severity (blocking / significant / minor), where (id or section), what is wrong, and why (quote the text). If an area is sound, say so in one line. Do not rewrite the contract; a one-line suggested fix per finding is enough."""
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
