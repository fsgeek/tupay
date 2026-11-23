#!/usr/bin/env python3
"""W1 amendment A2: one outside check of the merged backup test interface (testbed/backup/interface-v1.md).
usage: w1-interface-check.py <model-id> <out-dir>   (OPENROUTER_API_KEY in the environment; sent only in this request)
derives: steward practice "Read the inputs as an outsider would"; acceptance decision 3 (the steward disposes, an outside
family checks); W1 § Hold-outs. The checker is Kimi, W1's reviewer, which takes no author, hold-out or judging role.
No steward hypotheses: the task names kinds of defect, never a suspected one. The steward's dispositions are not sent,
so the check reads the interface on its own terms. The drafters' contract questions are sent, because the check is asked
whether any of them makes a cell uninjectable or an assertion unscorable."""
import json, os, sys, hashlib, urllib.request, pathlib
T = pathlib.Path('/home/tony/projects/tupay')
model, out = sys.argv[1], pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
glm = (T / 'experiments/W1/interface/glm/draft.md').read_text()
cq_glm = glm[glm.index('## CONTRACT QUESTIONS'):glm.index('### Appendix A')]
cq_mistral = (T / 'experiments/W1/interface/mistral/continuation.md').read_text()
files = [('THE CONTRACT AND FAILURE MODEL', (T / 'experiments/W1/inputs/contract-P.md').read_text()),
         ('THE BINDING', (T / 'docs/backup/binding-tupay.md').read_text()),
         ('THE INTERFACE UNDER CHECK', (T / 'testbed/backup/interface-v1.md').read_text()),
         ('CONTRACT QUESTIONS RAISED BY ONE DRAFTER (unresolved)', cq_glm),
         ('CONTRACT QUESTIONS RAISED BY THE OTHER DRAFTER (unresolved)', cq_mistral)]
task = """You are an outside checker. Below are a contract and failure model for a backup service (fixed), its binding (fixed), and a shared test interface that several independent teams will use: some write implementations, some write formal models, and one writes test schedules without seeing any implementation. The same schedule text must run unchanged against all of them. Two drafters raised the contract questions at the end; they are unresolved on purpose, because the interface must not choose a reading of the contract for the teams.

Check the interface for defects of these kinds (kinds, not suspicions):
1. Injection: a failure-model cell (BF1.x) that cannot be injected as specified, or whose injection does not match the cell's text, or that needs the implementation's cooperation beyond what the interface requires.
2. Observation and scoring: an assertion a schedule would need, for some clause, that the vocabulary cannot express or the harness cannot score from what it records; a predicate whose definition does not match the clause it would test.
3. Readings: a place where the interface itself picks one reading of the contract where the contract permits several, so that a correct implementation following another permitted reading would fail. Use the contract questions here: for each, say whether the interface as written lets an assertion accept every permitted reading, or forces one.
4. Prescription: a constraint on implementations that injection or observation does not strictly need, or that favours one design over another the contract permits.
5. Determinism and portability: anything that would make the same schedule produce different verdicts on two correct harness implementations, or that a TLA+ model's runner could not reasonably read.
6. Internal consistency: contradictions between sections; undefined terms; examples that do not match the grammar.

Report numbered findings, each with: kind (1 to 6), severity (blocking / significant / minor), where (section), what is wrong, and why (quote the text). One-line suggested fix per finding. Blocking means: W1's schedules cannot be written or scored fairly unless it is fixed. If you find nothing of a kind, say so for that kind."""
parts = [task] + [f'\n\n===== {t} =====\n' + body for t, body in files]
packet = ''.join(parts); (out / 'packet.md').write_text(packet)
h = hashlib.sha256(packet.encode()).hexdigest()[:16]
if os.environ.get('DRY'): print(len(packet), 'chars; packet sha256', h, '(dry run)'); sys.exit()
req = {'model': model, 'messages': [{'role': 'user', 'content': packet}], 'temperature': 0}
r = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(req).encode(),
    headers={'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'})
resp = json.load(urllib.request.urlopen(r, timeout=3600))
(out / 'response.json').write_text(json.dumps(resp, indent=1))
c = resp['choices'][0]
(out / 'check.md').write_text(c['message'].get('content') or '')
print(len(packet), 'chars; packet sha256', h, '; model', resp.get('model'), '; finish', c.get('finish_reason'), '; cost', resp.get('usage', {}).get('cost'))
