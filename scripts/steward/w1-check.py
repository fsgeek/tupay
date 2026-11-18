#!/usr/bin/env python3
"""Outside-family CHECK of the fixes made for Kimi's W1 review (not a new review round): are findings 1-26
resolved, and did the fixes introduce new defects? usage: w1-check.py <model-id> <out-dir>   (OPENROUTER_API_KEY in the environment; sent only in this request)
derives: docs/backup/review/kimi-w1/DISPOSITIONS.md ("the patch is checked once more"); log 2026-11-18.
No steward hypotheses: the task names kinds of defect, never a suspected one. The reviewer has no tools,
and its family (Kimi) takes no other role in W1."""
import json, os, sys, hashlib, urllib.request, pathlib
T = pathlib.Path('/home/tony/projects/tupay')
model, out = sys.argv[1], pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
files = [('YOUR EARLIER REVIEW (26 findings)', T / 'docs/backup/review/kimi-w1/review.md'),
         ('THE DISPOSITIONS (what was decided for each finding)', T / 'docs/backup/review/kimi-w1/DISPOSITIONS.md'),
         ('ARM F: the four-part contract (draft 7), fixed, unchanged', T / 'docs/backup/contract-draft-7.md'),
         ('the binding, unchanged', T / 'docs/backup/binding-tupay.md'),
         ('ARM P, NEW: prose arm draft 2', T / 'docs/backup/contract-prose-arm-draft-2.md'),
         ('THE CHANGE to the prose arm: unified diff from draft 1 to draft 2', T / 'tmp/w1-check/prose-1-to-2.diff'),
         ('W1 pre-registration, NEW: draft 3 (replaces draft 2, which you reviewed)', T / 'experiments/W1-prereg-draft-3.md')]
task = """You reviewed these documents before; your review and the dispositions are included. The steward has since changed the prose arm (ARM P draft 2; the diff is included) and rewritten the pre-registration (W1 draft 3). This is a check of those changes, not a new review.

1. For each of your findings 1-26: is it resolved by the change described in its disposition? Answer resolved / partly / not resolved, quoting the new text. Where the disposition chose a different remedy from the one you suggested, judge whether that remedy resolves the finding.
2. Did any change introduce a NEW difference of obligation between ARM P and ARM F, or a new defect in ARM P? Check every hunk of the diff against ARM F. Quote both texts.
3. Did W1 draft 3 introduce new defects of the kinds your review looked for (an outcome that cannot fail, room to choose after seeing outcomes, a confound, an ambiguous scoring rule, a leak, a disqualifying limit, an unfair comparison)? Pay particular attention to the new arm N and to the decision tree, which are new text.

Report numbered items, each with: severity (blocking / significant / minor), where, what, why (quote), and a one-line fix. End with one line: whether, in your judgment, the prose arm is now obligation-equivalent to ARM F, and whether W1 draft 3 is fit to register as an exploratory pilot."""
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
