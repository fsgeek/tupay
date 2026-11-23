#!/usr/bin/env python3
"""SMR line: the outside check of merged inputs v1, by a fourth family with no SMR role.
usage: smr-input-check.py <model-id> <merged.md> <out-dir>   (OPENROUTER_API_KEY in the environment)
derives: steward-practice "Read the inputs as an outsider would" (a non-steward family reviews inputs before
registration); fourteenth's acceptance decision 3. The checker gets the paper and the merged document only, not the
drafts or the steward's dispositions, so it judges the document as an author would receive it."""
import json, os, sys, hashlib, urllib.request, pathlib
S = pathlib.Path('/home/tony/projects/tupay-private/smr')
model, merged, out = sys.argv[1], pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
task = """Below are a research paper and a document derived from it: the service contract, failure model, environment, design obligations, design checks and test interface that two independent teams (one writing a formal model, one writing an implementation) will work from. They will have only the paper and this document. A shared suite of test schedules, written in the document's format, will run against both.

Review the document for defects. Answer from the paper and the document alone. For each finding give: an id (K1, K2, ...), the element id(s) it concerns, a quote, what is wrong, and a severity: BLOCKING (a team cannot build or test from the document, or two teams would build incompatible things, or a test would score a correct artifact as failing), SIGNIFICANT, or MINOR.

Check at least these, and report on each explicitly even when you find nothing:
1. Fidelity: does any element claim more, or less, than the paper's quoted sentence supports?
2. Observability: is every contract clause decidable through the test interface as written? Name any that is not.
3. Environment completeness: for each environment clause, can the test device produce every behaviour that clause admits? Where it cannot, no schedule can observe whether an artifact relies on more than the environment guarantees. Where the device produces behaviour the environment does not admit, a correct artifact could fail.
4. Assertions: does any assertion form reject a behaviour the paper permits, or accept one it forbids?
5. Determinism and scoring: can a schedule's outcome depend on anything the schedule does not fix (timing, thread scheduling, a choice left to the harness)? Is every scoring rule defined?
6. Consistency: do ids, cross-references and sections agree with each other?
7. Completeness: is anything an engineer needs to build the harness, the model or the implementation missing?

End with a count of findings by severity."""
packet = task + '\n\n===== THE DOCUMENT =====\n' + merged.read_text() + '\n\n===== THE PAPER (text extraction) =====\n' + (S / 'paper.txt').read_text()
(out / 'packet.md').write_text(packet)
h = hashlib.sha256(packet.encode()).hexdigest()[:16]
if os.environ.get('DRY'): print(len(packet), 'chars; packet sha256', h, '(dry run)'); sys.exit()
req = {'model': model, 'messages': [{'role': 'user', 'content': packet}], 'temperature': 0}
r = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(req).encode(),
    headers={'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'})
resp = json.load(urllib.request.urlopen(r, timeout=3600))
(out / 'response.json').write_text(json.dumps(resp, indent=1))
(out / 'check.md').write_text(resp['choices'][0]['message']['content'] or '')
print(len(packet), 'chars; packet sha256', h, '; model', resp.get('model'), '; finish', resp['choices'][0].get('finish_reason'), '; usage', resp.get('usage'))
