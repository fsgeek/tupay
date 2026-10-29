#!/usr/bin/env python3
"""D2 phase 3, step 2: the judge packets, built from the frozen heads by rule, with opaque ids shuffled by the beacon.
usage: d2-phase3.py <beacon-pulse.json> <out-dir> <mapping-out>     (mapping-out outside the public repository)
derives: experiments/D2/design.md draft 2, "Phase 3" steps 2 to 4; log 2026-10-28 "D2 phase 3 step 1: the freeze"
The steward does not read what this script reads. Rules, stated again in every packet:
- Findings: every `### ` block of each author's FINDINGS.md at its frozen head, in the schema's fields; the author's
  heading words other than its number (e.g. "draft") kept as `author_status`; the counterexample path omitted (it
  names a checkout); a CELLS.md id in a finding replaced by that cell's opaque id, and a trailing "new" removed;
  each author's first ten by its own order are the scored set (here every author has at most ten).
- Cells: every `### ` block of CELLS.md, whole, under an opaque id.
- Rows: every list item or paragraph of experiments/D2/phase0/recognised-and-reports.md under a heading, the
  enumerator's name removed, kind "recognised" (under a "Recognised" heading) or "report" (any other heading).
- Opaque ids: within each kind, items sorted by sha256(beacon outputValue || source label); ids numbered in that order.
- Split for size (agy reads about 120k characters): one packet of findings (with GUARANTEES.md and every cell a
  finding names), three of cells, one of rows."""
import hashlib, json, re, subprocess, sys
from pathlib import Path
T = Path('/home/tony/projects/tupay'); H = Path.home() / 'projects'
beacon = json.load(open(sys.argv[1]))['pulse']; bv = beacon['outputValue']
out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True); mapping_out = Path(sys.argv[3])
AUTHORS = ['model-c-claude', 'model-n-claude', 'model-c-grok', 'model-n-grok']

def blocks(text):   # '### ' heading -> body lines
    out, cur = [], None
    for l in text.splitlines():
        if l.startswith('### '):
            cur = [l[4:].strip(), []]; out.append(cur)
        elif cur is not None and l.startswith(('# ', '## ')):
            cur = None
        elif cur is not None:
            cur[1].append(l)
    return out

def fields(lines):
    f, key = {}, None
    for l in lines:
        m = re.match(r'^- ([a-z_]+):\s?(.*)$', l)
        if m: key = m.group(1); f[key] = m.group(2)
        elif key and l.strip(): f[key] += ' ' + l.strip()
    return f

order = lambda labels: sorted(labels, key=lambda s: hashlib.sha256((bv + s).encode()).hexdigest())

cells = blocks((T / 'experiments/D2/CELLS.md').read_text())
cell_ids = {h.split()[0]: f'C{n:03d}' for n, h in enumerate(order([c[0].split()[0] for c in cells]), 1)}
cell_text = {h.split()[0]: '\n'.join(b).strip() for h, b in cells}

def recell(s):
    s = re.sub(r'\b(D\d+)\b', lambda m: cell_ids.get(m.group(1), m.group(1)), s)
    return re.sub(r'[;,]?\s*"?new"?\s*$', '', s)

findings = []
for a in AUTHORS:
    head = (T / f'experiments/D2/phase3/freeze/{a}/head.txt').read_text().strip()
    r = subprocess.run(['git', '-C', str(H / f'tupay-d2-export-{a}'), 'show', f'{head}:FINDINGS.md'], capture_output=True, text=True)
    if r.returncode: continue   # an author without FINDINGS.md has no findings
    for k, (h, b) in enumerate(blocks(r.stdout), 1):
        f = fields(b); words = [w for w in re.sub(r'\(.*?\)', '', h).replace('-', ' ').split() if not re.fullmatch(r'F?\d+', w) and w != 'F']
        named = sorted(set(re.findall(r'\bD\d+\b', h + ' ' + f.get('violated', ''))))
        findings.append({'label': f'{a}#{k}', 'author': a, 'rank': k, 'scored': k <= 10, 'heading': h,
                         'author_status': ' '.join(words) or None, 'named_cells': named,
                         'violated': recell(f.get('violated', '')), 'mechanism': recell(f.get('mechanism', '')),
                         'effect': recell(f.get('effect', '')), 'defence': recell(f.get('defence', '')),
                         'confidence': f.get('confidence', '')})
fid = {l: f'F{n:02d}' for n, l in enumerate(order([f['label'] for f in findings]), 1)}

rows, top, sec = [], None, None
para = []
def flush():
    global para
    t = ' '.join(x.strip() for x in para).strip()
    if t and top and sec: rows.append({'label': f'{top}/{sec}/{len(rows)}', 'enumerator': top, 'section': sec,
                                       'kind': 'recognised' if 'recognised' in sec.lower() else 'report', 'text': t})
    para = []
for l in (T / 'experiments/D2/phase0/recognised-and-reports.md').read_text().splitlines():
    if l.startswith('# '): flush(); top = l[2:].strip(); sec = None
    elif l.startswith('## '): flush(); sec = l[3:].strip()
    elif re.match(r'^\s*([-*]|\d+\.)\s', l): flush(); para = [re.sub(r'^\s*([-*]|\d+\.)\s', '', l)]
    elif not l.strip(): flush()
    else: para.append(l)
flush()
names = {r['enumerator'] for r in rows}
for r in rows:
    for n in names: r['text'] = r['text'].replace(n, '[an enumerator]')
rid = {l: f'R{n:02d}' for n, l in enumerate(order([r['label'] for r in rows]), 1)}

CRIT = """Episode's criteria (fixed by Episode's steward 2026-10-26, before any list existed): a finding is a **match** for a sealed bug if it has the same violated contract, the same mechanism and the same class of effect; **partial** if it has the contract and one of the other two, or the right mechanism under a different contract; **no match** otherwise. A finding that claims a violation contradicting one of the sealed file's confirmed properties is **flagged** (name the property). A finding about the sealed file's open item is **unresolved**. A finding may match several bugs."""
HEAD = """# D2 judge packet {part}: Episode's log and recovery, against the sealed analysis

You are a judge. Work only from the text in this packet; do not read files, run commands or search.

Context: a component's log and recovery (`logbuf` in the Episode file system, OSF DCE 1.2.2) relies on contracts from the layers around it. Independent readers enumerated those contracts ("cells"); independent model authors then wrote TLA+ models and reported **findings**: violations of an obligation outside `logbuf` that break a stated guarantee of the log and recovery with the model's defences in place. A separate analysis, done before any of this and sealed, lists bugs, confirmed properties and an open item; it is given to you {sealed}. Items carry opaque ids; you are not told who wrote them. Packets are split by size by a stated rule; this one is part {part}.

{crit}

{task}

Answer with one JSON object only, as specified. Be concrete and brief; cite the sealed file's bug ids and the item's own words. Do not propose fixes. Disagreement with the sealed analysis is allowed: say so in `reason`.
"""
def dump(name, part, task, body, schema):
    s = HEAD.format(part=part, crit=CRIT, task=task + '\n\nAnswer schema: ' + schema, sealed='{SEALED_WHERE}') + body
    (out / f'{name}.md').write_text(s); return len(s)

def fblock(f):
    s = f"\n### {fid[f['label']]}\n" + (f"- author_status: {f['author_status']}\n" if f['author_status'] else '')
    return s + ''.join(f'- {k}: {f[k]}\n' for k in ('violated', 'mechanism', 'effect', 'defence', 'confidence'))
named = sorted({c for f in findings for c in f['named_cells']}, key=lambda c: cell_ids[c])
body = ('\n## Findings\n' + ''.join(fblock(f) for f in sorted(findings, key=lambda f: fid[f['label']]))
        + '\n## Cells named by a finding\n' + ''.join(f'\n### {cell_ids[c]}\n{cell_text[c]}\n' for c in named)
        + '\n## GUARANTEES.md (the guarantees findings cite as G<n>)\n' + (T / 'experiments/D2/GUARANTEES.md').read_text())
sizes = {'findings': dump('findings', '1 of 5 (findings)', 'For **each finding**, rule against the sealed bugs.', body,
         '{"findings": [{"id": "F..", "ruling": "match|partial|no match|unresolved", "bugs": ["<sealed bug id>", ...], "flag_confirmed_property": "<property id or null>", "reason": "<two to four sentences>"}]}')}
cs = sorted(cells, key=lambda c: cell_ids[c[0].split()[0]]); third = -(-len(cs) // 3)
for p in range(3):
    part = cs[p * third:(p + 1) * third]
    body = '\n## Cells\n' + ''.join(f"\n### {cell_ids[h.split()[0]]}\n{cell_text[h.split()[0]]}\n" for h, _ in part)
    sizes[f'cells-{p + 1}'] = dump(f'cells-{p + 1}', f'{p + 2} of 5 (cells, {p + 1} of 3)',
        'For **each cell**: does it name the violated contract that the sealed file records for some bug? Binary per cell; list the bugs if yes. A cell is a contract, not a finding; mechanism and effect do not matter here.', body,
        '{"cells": [{"id": "C...", "names_contract_of": ["<sealed bug id>", ...], "reason": "<one sentence>"}]}  (empty list for no)')
body = '\n## Rows\n' + ''.join(f"\n### {rid[r['label']]} ({r['kind']})\n{r['text']}\n" for r in sorted(rows, key=lambda r: rid[r['label']]))
sizes['rows'] = dump('rows', '5 of 5 (recognised lines and report notes)',
    'These rows are what the enumerators wrote outside their enumerations: "recognised" lines (things they said they recognised from prior knowledge) and "report" notes. For **each row**: does it match a sealed bug (same contract and mechanism)? A match here is found by reading, not by the workflow.', body,
    '{"rows": [{"id": "R..", "matches": ["<sealed bug id>", ...], "reason": "<one sentence>"}]}  (empty list for no)')
mapping = {'beacon': {k: beacon[k] for k in ('pulseIndex', 'timeStamp', 'outputValue')},
           'findings': {fid[f['label']]: f for f in findings}, 'cells': {v: k for k, v in cell_ids.items()},
           'rows': {rid[r['label']]: r for r in rows}}
mapping_out.write_text(json.dumps(mapping, indent=1, sort_keys=True))
print(json.dumps({'sizes': sizes, 'findings': len(findings), 'cells': len(cells), 'rows': len(rows),
                  'rows_by_kind': {k: sum(r['kind'] == k for r in rows) for k in ('recognised', 'report')},
                  'mapping_sha256': hashlib.sha256(mapping_out.read_bytes()).hexdigest()}))
