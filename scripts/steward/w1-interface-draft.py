#!/usr/bin/env python3
"""W1 amendment A2: the shared test interface for the backup line, drafted in parallel by two families with no W1 role.
usage: w1-interface-draft.py <model-id> <out-dir>   (OPENROUTER_API_KEY in the environment; sent only in this request)
derives: W1 § Hold-outs and § Measures 5 (schedules run against every implementation and model); AGENTS.md rules 2 and 5;
acceptance decision 3 of the fourteenth steward (inputs drafted by other families, in parallel; the steward disposes).
No steward hypotheses: the task states what the interface must make possible, never a suspected design or defect.
The drafter has no tools. Its inputs are those the hold-out author gets: the prose contract (author-facing copy) and the binding."""
import json, os, sys, hashlib, urllib.request, pathlib
T = pathlib.Path('/home/tony/projects/tupay')
model, out = sys.argv[1], pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
files = [('THE CONTRACT AND FAILURE MODEL', T / 'experiments/W1/inputs/contract-P.md'),
         ('THE BINDING (maps the contract roles to machines and values)', T / 'docs/backup/binding-tupay.md')]
task = """You are designing a shared test interface for a backup service. The contract and failure model below are fixed; do not change them, and do not design the service itself.

Several independent teams will each build an implementation of this contract, and some will also write a formal model (for example in TLA+). One test suite of "schedules" must run, unchanged, against every implementation and every model. A schedule is a scripted scenario: what happens to the sources, which failure-model cells (BF1.x) are injected and when, and what must be observed. Your interface is the only thing the teams share besides the contract, so whatever it leaves unspecified, each team will decide differently.

The interface must make the following possible:
1. Time. The contract's parameters are hours and days (see the binding's values). A schedule covering several weeks must run in minutes. Say how time is given to an implementation, and how clock steps on one host are expressed (the contract measures ages on each host's own clock).
2. Hosts and roles. Every role the contract names (source host, store, restore host, freshness checker, notice channel) must exist in a test, on one machine, without root. Say what each is in a test and how an implementation is told where it is.
3. Fault injection. Every BF1 cell in the failure model must be injectable by the test harness, without the implementation's cooperation beyond what the interface requires. For each cell, say how it is injected and how it ends.
4. Observation. Everything a schedule's assertions need must be observable from outside the implementation: in particular, the notice channel's record (which clause a notice names, and when it arrived), snapshot marks, and whether a snapshot is recoverable. Say what is recorded, where, and in what format.
5. Assertions. Every assertion in a schedule carries a tag naming the contract clause it checks, written `derives: B1.x` (or the id it checks). Each schedule states a fixed scoring horizon: a fixed time after its last injected event, at which recoverability is judged.
6. Models. The same schedule text must be readable by a formal model's own schedule runner. Say which parts of a schedule a model must accept, and how a model reports that it cannot express a schedule.
7. Prescription. The contract prescribes no protocol and no tooling. Your interface must not prescribe any either, beyond what injection and observation strictly need. Where you must constrain an implementation (for example, to read time from the harness), say so, and say why the constraint is needed.

Write the interface as a specification another engineer could implement a harness from, with:
- a schedule format (grammar or schema, with one complete example schedule that injects at least two cells);
- the implementation-side contract (what an implementation must expose or obey, and nothing more);
- the harness's obligations;
- a list headed OPEN CHOICES: every point where the contract or binding leaves the interface's design open and you chose one option. For each, give the options you saw and why you chose yours.
- a list headed CONTRACT QUESTIONS: any place where you could not design injection or observation because the contract itself is unclear. Quote the text. Do not resolve these yourself.
Be concrete and complete rather than brief."""
parts = [task] + [f'\n\n===== {t} ({p.name}) =====\n' + p.read_text() for t, p in files]
packet = ''.join(parts); (out / 'packet.md').write_text(packet)
h = hashlib.sha256(packet.encode()).hexdigest()[:16]
if os.environ.get('DRY'): print(len(packet), 'chars; packet sha256', h, '(dry run)'); sys.exit()
req = {'model': model, 'messages': [{'role': 'user', 'content': packet}], 'temperature': 0}
if os.environ.get('REASONING_MAX'): req['reasoning'] = {'max_tokens': int(os.environ['REASONING_MAX'])}   # GLM attempt 1 spent all output on reasoning (2026-11-23)
r = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(req).encode(),
    headers={'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'})
resp = json.load(urllib.request.urlopen(r, timeout=3600))
(out / 'response.json').write_text(json.dumps(resp, indent=1))
(out / 'draft.md').write_text(resp['choices'][0]['message']['content'] or '')
print(len(packet), 'chars; packet sha256', h, '; model', resp.get('model'), '; usage', resp.get('usage'))
