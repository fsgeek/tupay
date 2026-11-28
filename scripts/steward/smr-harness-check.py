#!/usr/bin/env python3
"""SMR line: an outside check of the reference harness CODE against inputs v3, by a family with no SMR author role.
usage: smr-harness-check.py <model-id> <harness-tree> <out-dir>   (OPENROUTER_API_KEY in the environment)
derives: fifteenth steward's harness decision (one harness author, so an outside reader checks it against v3; log
2026-11-28); DISPOSITIONS-3.md C-3 (the document governs; a difference is a harness defect). The tree is the signed
export, read as data. The reader gets v3, its known limits and the harness; not the drafts, dispositions or foresight."""
import json, os, sys, hashlib, urllib.request, pathlib
S = pathlib.Path('/home/tony/projects/tupay-private/smr')
model, tree, out = sys.argv[1], pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
docs = [('THE DOCUMENT (inputs v3; it governs)', S / 'inputs-v3.md'), ('KNOWN LIMITS OF THE DOCUMENT', S / 'KNOWN-LIMITS-v3.md')]
mine = ['PROTOCOL.md', 'README.md', 'HARNESS-DEFECTS.md'] + sorted(str(p.relative_to(tree)) for p in tree.rglob('*')
        if p.is_file() and p.suffix in ('.py', '.json', '.sh') and not str(p.relative_to(tree)).startswith(('inputs/', 'timestamps/')))
task = """Below is a document that specifies a test harness's semantics for a storage translation layer (the document governs), its known limits, and a harness written as code from it, with the harness's protocol, README and defect log. Independent teams will build a formal model and an implementation against this harness.

Review the CODE against the DOCUMENT. Report each finding with: an id (H1, H2, ...), file and line or function, the document clause, a quote of each, what differs, and a severity: BLOCKING (the harness would score a correct artifact as failing, pass a broken one, or two teams following PROTOCOL.md could not interoperate), SIGNIFICANT, or MINOR.

Check at least, and report on each explicitly even when you find nothing:
1. Crash-state construction: does the code construct every durable state the document admits, and only those (durable subsets, sector granularity, the no-hole rule, resets, outstanding commands, seeded selection)?
2. The per-sector safety oracle: does the code accept every outcome the document permits and reject every one it forbids?
3. Sweeps, result kinds and scoring: do they match the document, including NOT_REACHED, ERROR and UNSUPPORTED?
4. Determinism: can a run's result depend on anything the schedule does not fix?
5. The harness's own mutation pair: is it strong enough? Name a broken translation layer it would wrongly PASS, if one exists, and say which crash states its selftest never exercises.
6. PROTOCOL.md: could an implementation team and a formal-model team each build a compatible artifact from it and the document alone?
7. Does the code or its README encode any expected outcome for a design under test (the known limits forbid this)?

End with a count of findings by severity."""
parts = [task] + [f'\n\n===== {t} =====\n' + p.read_text() for t, p in docs]
parts += [f'\n\n===== HARNESS FILE {r} =====\n' + (tree / r).read_text(errors='replace') for r in mine if (tree / r).exists()]
packet = ''.join(parts); (out / 'packet.md').write_text(packet)
h = hashlib.sha256(packet.encode()).hexdigest()[:16]
if os.environ.get('DRY'): print(len(packet), 'chars;', len(mine), 'harness files; packet sha256', h, '(dry run)'); sys.exit()
req = {'model': model, 'messages': [{'role': 'user', 'content': packet}], 'temperature': 0}
r = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(req).encode(),
    headers={'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'})
resp = json.load(urllib.request.urlopen(r, timeout=3600))
(out / 'response.json').write_text(json.dumps(resp, indent=1))
(out / 'check.md').write_text(resp['choices'][0]['message']['content'] or '')
print(len(packet), 'chars; packet sha256', h, '; model', resp.get('model'), '; finish', resp['choices'][0].get('finish_reason'), '; usage', resp.get('usage'))
