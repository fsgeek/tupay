#!/usr/bin/env python3
"""Adversarial review of D2's scoring by a family that has never seen tupay's material.
usage: d2-review.py <model-id> <out-dir>   (OPENROUTER_API_KEY in the environment; the key goes to this one call only)
derives: steward practice "Before publication, a non-steward family reviews the scoring adversarially against
the registration and the evidence"; tenth handoff, next item 1. Modelled on scripts/steward/x3-audit/review.py.
Packet, built here from committed files by a fixed list, inline; the reviewer has no tools. Excerpting rules:
the log contributes only the entries whose headings are listed in LOG_HEADS (the ones that change D2's judges,
denominator or registered rulings); the mapping contributes, per id, only author/kind/enumerator/scored (the
findings' text is in the findings packet); the cell packets themselves are left out (each judge's ruling quotes
the cell it rules on), as is the rows packet (the rulings carry each row's reason). Everything else is whole."""
import json, os, sys, hashlib, urllib.request, pathlib
T = pathlib.Path('/home/tony/projects/tupay'); D = T / 'experiments/D2'; P = D / 'phase3'; J = P / 'judges'
model, out = sys.argv[1], pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
LOG_HEADS = ['2026-10-27: more families offered', '2026-10-29: Episode had answered the follow-up',
             '2026-10-29: D2 judges: harness failures', '2026-10-29: D2 judges Gemini and GLM: rulings in',
             "2026-11-02: Episode's D2 rulings recorded"]
log, keep, cur = (T / 'docs/seed-log.md').read_text().split('\n## '), [], None
for e in log:
    if any(e.startswith(h) for h in LOG_HEADS):
        keep.append('## ' + e.strip())
assert len(keep) == len(LOG_HEADS), [h for h in LOG_HEADS if not any(k.startswith('## ' + h) for k in keep)]
m = json.loads((P / 'mapping.json').read_text())
slim = {'findings': {k: {x: v[x] for x in ('author', 'label', 'scored', 'author_status')} for k, v in m['findings'].items()},
        'rows': {k: {x: v[x] for x in ('kind', 'enumerator', 'section')} for k, v in m['rows'].items()}}
files = [('the registration (experiments/D2/design.md)', D / 'design.md', None),
         ('log entries that change judges, denominator or rulings (excerpt by heading)', None, '\n\n'.join(keep)),
         ('the findings packet as sent to the judges, with GUARANTEES.md and the sealed analysis v2', J / 'findings/packet-sent.md', None),
         ('mapping from opaque id to author (excerpt: author, label, scored, author_status; rows: kind, enumerator)', None, json.dumps(slim, indent=1)),
         ('Episode ruling: findings', J / 'episode/findings.json', None),
         ('Gemini ruling: findings', J / 'findings/gemini/ruling.json', None),
         ('GLM ruling (beside): findings', J / 'findings/glm-2/ruling.json', None)]
for pk in ('cells-1', 'cells-2', 'cells-3'):
    files.append((f'Episode ruling: {pk}', J / f'episode/{pk}.json', None))
    if pk == 'cells-2':
        files.append(('Gemini cells-2: NO registered ruling (both runs unparseable); mechanical repair, beside only', J / 'cells-2/gemini-2/ruling-repaired-beside.json', None))
    else:
        files.append((f'Gemini ruling: {pk}', J / f'{pk}/gemini/ruling.json', None))
    files.append((f'GLM ruling (beside): {pk}', J / f'{pk}/glm-2/ruling.json', None))
files += [('Episode ruling: rows', J / 'episode/rows.json', None), ('Gemini ruling: rows', J / 'rows/gemini/ruling.json', None),
          ('GLM ruling (beside): rows', J / 'rows/glm-2/ruling.json', None),
          ('Episode README for its rulings (its summary, packet defects, correction)', J / 'episode/README.md', None),
          ('the scoring script', T / 'scripts/steward/d2-score.py', None),
          ('the script output', D / 'score/score.json', None),
          ('the draft result under review', T / 'experiments/D2-result.md', None)]
task = """You are reviewing, adversarially, the scoring of a pre-registered experiment (D2) before it is published. The registration (design.md) fixed the predictions, denominators and judging rules before any outcome existed; later log entries changed the judges and the denominator, and are included. Three judges ruled blind on opaque ids; the mapping from id to author is given. A script computes the score; its output and a draft result are given, with every ruling.

Find defects. In particular: does the script implement each prediction (D2-1 to D2-5, D2-2g, P0-4) exactly as the registration words it, including the denominator, the comment split, the "holds only under both registered judges" rule, the treatment of the missing Gemini cells-2 ruling, and the leakage rule? Recompute every number in the draft's tables from the rulings and check it. Does the draft state anything the evidence does not support, omit anything the registration says must be reported, or present a reading beside the score as if it were the score? Is any rule applied that the registration does not contain? Are the 'reading beside' claims (especially readings 1 and 2) correct as stated?

Report a numbered list of findings, each: severity (blocking / significant / minor), where (file, prediction or table cell), what is wrong, and the evidence (ids, rulings). If an area is correct, say so in one line. Do not propose new predictions or rescore by rules the registration lacks."""
parts = [task]
for title, p, text in files:
    body = text if text is not None else p.read_text()
    parts.append(f'\n\n===== {title}' + (f' ({p.name})' if p else '') + ' =====\n' + body)
packet = ''.join(parts)
(out / 'packet.md').write_text(packet)
if os.environ.get('DRY'):
    print(len(packet), 'chars; packet sha256', hashlib.sha256(packet.encode()).hexdigest()[:16], '(dry run, not sent)'); sys.exit()
req = {'model': model, 'messages': [{'role': 'user', 'content': packet}], 'temperature': 0}
r = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(req).encode(),
    headers={'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'})
resp = json.load(urllib.request.urlopen(r, timeout=3600))
(out / 'response.json').write_text(json.dumps(resp, indent=1))
(out / 'review.md').write_text(resp['choices'][0]['message']['content'] or '')
print(len(packet), 'chars; packet sha256', hashlib.sha256(packet.encode()).hexdigest()[:16], '; model', resp.get('model'), '; usage', resp.get('usage'))
