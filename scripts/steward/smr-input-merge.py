#!/usr/bin/env python3
"""SMR line: merge the two drafted inputs under the steward's dispositions, by a third family with no SMR role.
usage: smr-input-merge.py <model-id> <out-dir>   (OPENROUTER_API_KEY in the environment; sent only in this request)
derives: fourteenth steward's acceptance decision 3 (the steward disposes; it does not write the merged inputs, whose
steward-written versions carried the next defect in eight rounds running); fifteenth's acceptance decision 2.
Inputs: the paper's text, both drafts, DISPOSITIONS.md. Everything stays in ../tupay-private/smr (never pushed)."""
import json, os, sys, hashlib, urllib.request, pathlib
S = pathlib.Path('/home/tony/projects/tupay-private/smr')
model, out = sys.argv[1], pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
files = [('DISPOSITIONS (binding decisions)', S / 'DISPOSITIONS.md'),
         ('DRAFT G', S / 'drafts/glm/draft.md'),
         ('DRAFT M', S / 'drafts/mistral/draft.md'),
         ('THE PAPER (text extraction)', S / 'paper.txt')]
task = """Two independent drafts (G and M) of the inputs for a verification workflow were written from the research paper below. A set of DISPOSITIONS decides how they combine. Your job is to write the single merged document, version 1, that independent model and implementation teams will work from. They will have the paper and your document, and nothing else.

Rules:
1. Follow the DISPOSITIONS exactly. Where they adopt one draft's text, carry it over faithfully. Where they state a rule or a generalisation, apply it.
2. Add nothing that is in neither draft nor the dispositions. If a point that the dispositions or a section needs is covered by neither, write it as an item headed OPEN, saying what is missing; do not invent it.
3. Give every element a fresh id: contract SC1.1, SC1.2, ...; failure model SF1.1, ...; environment SE1.1, ...; design obligations SD1.1, ...; design checks DC1.1, ... Each element states which design it applies to (Host-Hybrid, Host-LS, or both), quotes the paper sentence it derives from, and ends with a line `sources: G <ids>; M <ids>; disposition <n>` naming what it was merged from.
4. Every contract clause names the observation through the test interface that decides it. Every design check names the device-log observation that decides it and the SD obligation it derives from.
5. The test interface must be complete enough that an engineer could build the harness from it: the device (including the crash behaviour in disposition 7), injection for every in-scope SF cell and how it ends, observation and its format, the schedule format (schema plus one complete example schedule that injects at least two cells and uses an OLD_OR_NEW expectation), model capability declarations, and the constraints on implementations, each with its reason.
6. Sections, in order: A. SERVICE CONTRACT; B. FAILURE MODEL; C. ENVIRONMENT; D. DESIGN OBLIGATIONS; E. DESIGN CHECKS; F. TEST INTERFACE; G. OPEN CHOICES (each draft's choices that survive the dispositions, plus any the merge forced, with options and reasons); H. PAPER QUESTIONS (the deduplicated union, each with its quote); I. OPEN (gaps you found; empty if none).
7. Do not mention the dispositions' reasoning in the merged document beyond the `sources:` lines; the document must stand on its own for a reader who has only the paper.

Be complete rather than brief."""
packet = task + ''.join(f'\n\n===== {t} =====\n' + p.read_text() for t, p in files)
(out / 'packet.md').write_text(packet)
h = hashlib.sha256(packet.encode()).hexdigest()[:16]
if os.environ.get('DRY'): print(len(packet), 'chars; packet sha256', h, '(dry run)'); sys.exit()
req = {'model': model, 'messages': [{'role': 'user', 'content': packet}], 'temperature': 0}
r = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(req).encode(),
    headers={'Authorization': 'Bearer ' + os.environ['OPENROUTER_API_KEY'], 'Content-Type': 'application/json'})
resp = json.load(urllib.request.urlopen(r, timeout=3600))
(out / 'response.json').write_text(json.dumps(resp, indent=1))
(out / 'merged.md').write_text(resp['choices'][0]['message']['content'] or '')
print(len(packet), 'chars; packet sha256', h, '; model', resp.get('model'), '; finish', resp['choices'][0].get('finish_reason'), '; usage', resp.get('usage'))
