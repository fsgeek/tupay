#!/usr/bin/env python3
"""SMR line: contract, failure model, design obligations and test interface, drafted together from the paper alone,
in parallel by two families with no SMR author role. The steward disposes of the drafts.
usage: smr-input-draft.py <model-id> <out-dir>   (OPENROUTER_API_KEY in the environment; sent only in this request)
derives: seed workflow steps 1 and 2; fourteenth steward's acceptance decision 3 (inputs drafted by other families in
parallel; the steward disposes); fifteenth steward's acceptance decision 2 (the interface is drafted with the contract,
not after: the backup line found its contract untestable at the first attempt to derive tests, log 2026-11-23 18:57Z).
No steward hypotheses (practice rule 18): the task states what the inputs must make possible, never a suspected defect.
The paper's text and every output stay in ../tupay-private/smr (the author's code is unreleased; never pushed).
The drafter has no tools. Its only input is the paper's text (pdftotext of the PDF, sha256 244aa410...)."""
import json, os, sys, hashlib, urllib.request, pathlib
PAPER = pathlib.Path('/home/tony/projects/tupay-private/smr/paper.txt')
model, out = sys.argv[1], pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
task = """You are drafting the inputs for a verification workflow, working from one research paper alone (its text is below; tables and figures were flattened by text extraction).

The paper describes host-side translation layers for host-managed SMR drives, each a Linux device mapper that exports a block device: Host-Hybrid (Section 3) and Host-LS (Section 4). Later, independent teams will work from the paper and from your inputs, without the authors' code. One team writes a formal model (for example in TLA+); another writes an implementation. One shared suite of test schedules must then run, unchanged, against both. Whatever your inputs leave unspecified, each team will decide differently, and their results will not be comparable.

Draft all of the following, together, so that they are consistent with each other.

A. SERVICE CONTRACT. The properties of the exported block device that the paper states or that its design is said to provide. Give each clause an id (SC1.1, SC1.2, ...), and say whether it holds for Host-Hybrid, Host-LS or both. Each clause states one obligation, cites the section (and quotes the sentence) it derives from, and names the observation by which a test could decide whether it held. The contract is about correctness and progress, not performance numbers; a progress property is a clause only if the paper states one. A property the paper does not state is not a clause: put it under G.

B. FAILURE MODEL. The faults the contract must hold under, ids SF1.1, SF1.2, ..., each citing the paper. Include the faults the paper places out of scope, marked as out of scope, with its reason quoted.

C. ENVIRONMENT. What the device and host beneath the translation layer are assumed to guarantee, as the paper states it, ids SE1.1, ... A team's model and implementation may rely on these and on nothing else.

D. DESIGN OBLIGATIONS. The mechanisms the paper prescribes, which a model or implementation must follow to count as this design rather than some other block device: for example, its data structures, their placement on disk or in memory, and the procedures that use them. Ids SD1.1, ..., each quoting the paper. Where the paper names a mechanism but does not fully specify it, say what is unspecified.

E. TEST INTERFACE. How one schedule, written once, runs against a model and against an implementation:
  1. Device. No SMR hardware and no root: say what the device beneath is in a test, which of its behaviours the harness controls, and how it is represented.
  2. Injection. For every SF cell in scope: how the harness injects it and how it ends, without the implementation's cooperation beyond what the interface requires.
  3. Observation. Everything an assertion needs must be observable from outside the implementation. Say what is recorded, where, and in what format.
  4. Schedule format: a grammar or schema, and one complete example schedule that injects at least two cells. Every assertion carries a tag naming the clause it checks, written `derives: SC1.x`.
  5. Models: which parts of a schedule a model must accept, and how a model reports that it cannot express a schedule.
  6. Prescription: constrain the implementation only where injection or observation strictly needs it, and say why each constraint is needed.

F. OPEN CHOICES. Every point where the paper leaves your design of A to E open and you chose one option: the options you saw, and why you chose yours.

G. PAPER QUESTIONS. Every place where the paper is unclear, inconsistent or silent on something A to E needs. Quote the text. Do not resolve them yourself. Include properties a user of a block device would reasonably expect that the paper neither states nor disclaims.

Be concrete and complete rather than brief. Use the ids exactly as given."""
paper = PAPER.read_text()
packet = task + '\n\n===== THE PAPER (text extraction) =====\n' + paper
(out / 'packet.md').write_text(packet)
h = hashlib.sha256(packet.encode()).hexdigest()[:16]
if os.environ.get('DRY'): print(len(packet), 'chars; packet sha256', h, '(dry run)'); sys.exit()
req = {'model': model, 'messages': [{'role': 'user', 'content': packet}], 'temperature': 0}
if os.environ.get('REASONING_MAX'): req['reasoning'] = {'max_tokens': int(os.environ['REASONING_MAX'])}   # GLM attempt 1 on 2026-11-23 spent all output on reasoning
r = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(req).encode(),
    headers={'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'})
resp = json.load(urllib.request.urlopen(r, timeout=3600))
(out / 'response.json').write_text(json.dumps(resp, indent=1))
(out / 'draft.md').write_text(resp['choices'][0]['message']['content'] or '')
print(len(packet), 'chars; packet sha256', h, '; model', resp.get('model'), '; finish', resp['choices'][0].get('finish_reason'), '; usage', resp.get('usage'))
