#!/usr/bin/env python3
"""Adversarial review of the X3 support audit's mapping by a family that has never seen tupay's material.
usage: review.py <model-id> <out-dir>   (OPENROUTER_API_KEY in the environment; the key goes to this one call only)
derives: experiments/X3-prereg.md departure 3; log 2026-10-27 "more families offered" item 1; steward practice
"Read the inputs as an outsider would". The packet is built here from committed files by a fixed list, inline,
with no steward hypothesis about what is wrong; the reviewer has no tools, so the packet is all it sees."""
import json, os, re, sys, hashlib, urllib.request, pathlib
T = pathlib.Path('/home/tony/projects/tupay'); S = pathlib.Path.home() / 'projects/tupay-x3-score'
model, out = sys.argv[1], pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
prereg = (T / 'experiments/X3-prereg.md').read_text()
reg = next(l for l in prereg.splitlines() if l.startswith('3. **The support audit is registered**'))
files = [('the registration\'s audit paragraph (experiments/X3-prereg.md)', None, reg),
         ('reach-table generator', T / 'scripts/steward/reach-table.py', None),
         ('needed reach, shared schedules', T / 'experiments/X3/reach.md', None),
         ('needed reach, hold-outs', T / 'experiments/X3/holdout/reach.md', None),
         ('the audit mapping', T / 'scripts/steward/x3-audit/MAPPING.md', None),
         ('the audit probe builder', T / 'scripts/steward/x3-audit/probe.py', None),
         ('the audit driver', T / 'scripts/steward/x3-audit/audit.sh', None),
         ('arm A model', S / 'armA-model/model/Lease.tla', None), ('arm A compiler', S / 'armA-model/model/compile.py', None),
         ('arm R model', S / 'armR-model/model-regen/Lease.tla', None), ('arm R compiler', S / 'armR-model/model-regen/compile.py', None),
         ('arm R TLC wrapper', S / 'armR-model/model-regen/tlc.sh', None)]
task = """You are reviewing, adversarially, a support audit for bounded model checks. Two TLA+ models (arm A, arm R) were written by other authors; each checks a set of fault schedules. Before any PASS of a schedule is scored, the audit must show that the model's checked state space (at the author's bounds) contains a state meeting every floor of that schedule's row in the needed-reach table. The audit's tooling (mapping, probe builder, driver) is given below, with the registration text it implements and both models and their compilers.

Find defects. In particular, for each column of the reach table and each model, say whether the mapping's TLA+ expression really counts what the generator's column counts; and look for any way the audit could report SUPPORT when the checked space does not contain such a state, report NO-SUPPORT when it does, or apply VACUOUS where the model does in fact represent the quantity (or fail to apply it where it does not). Also check that the probe runs at the author's bounds and spec, and whether any departure from the author's configuration (for example a deadlock check turned off, or a different spec formula) changes the set of reachable states. Check the mutant: can it say no for the right reason?

Report a numbered list of findings, each: severity (blocking / significant / minor), the file and line or expression, what is wrong, and a concrete case (a schedule id and a state or trace) where it changes a verdict, if you can give one. If you find nothing wrong in an area, say so in one line. Do not suggest how the experiment should be scored; judge only whether the audit does what the registration says."""
parts = [task]
for title, p, text in files:
    body = text if text is not None else p.read_text()
    parts.append(f'\n\n===== {title}' + (f' ({p.name})' if p else '') + ' =====\n' + body)
packet = ''.join(parts)
(out / 'packet.md').write_text(packet)
req = {'model': model, 'messages': [{'role': 'user', 'content': packet}], 'temperature': 0}
r = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(req).encode(),
    headers={'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'})
resp = json.load(urllib.request.urlopen(r, timeout=3600))
(out / 'response.json').write_text(json.dumps(resp, indent=1))
(out / 'review.md').write_text(resp['choices'][0]['message']['content'])
print(len(packet), 'chars; packet sha256', hashlib.sha256(packet.encode()).hexdigest()[:16], '; model', resp.get('model'), '; usage', resp.get('usage'))
