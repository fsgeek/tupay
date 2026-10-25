#!/usr/bin/env python3
"""D1 phase 1: merge packet, agreed merges, and the registered order. derives: experiments/D1/design.md draft 3, phase 1.

usage:
  d1-phase1.py packet <phase0-dir>                         print the merge packet (Recognised and report sections removed)
  d1-phase1.py order <phase0-dir> <merge-a.json> <merge-b.json> <beacon-outputValue-hex>   print the ordered cells

Enumerations are <phase0-dir>/<run>/enumeration.md for the runs codex-1, codex-2, grok-1, grok-2; entry ids are
written <run>:E<n>. A merge (one Gemini instance's answer) is JSON {"groups": [[id, ...], ...]}: each group a set of
entries stating the same obligation; an entry may appear in several groups; an entry in no group is its own.
Written 2026-10-25 after the Codex lists existed and before any list was read by the steward or a merger.
Rules, from the design:
- A group is accepted iff both merges contain exactly that set of entries. Every entry in no accepted group is a cell
  of its own (Fable 10: disagreements stay unmerged). A cell's members are its entries.
- Cell ids D1, D2, ... in order of their first member (runs in the order above, then E number).
- Order: (0) cells with a verified quotation in any member (quote-check VERIFIED or SPLIT) before cells with none;
  (1) silent descending, as the mean over members of each entry's percentile rank within its own enumeration
  (fraction of that list rated lower, plus half the fraction rated equal); (2) detectable no < partly < yes, the most
  common among members, ties to the less detectable; (3) earliest source, the minimum numeric section tuple over
  members (front matter or unparsable = (0,)); (4) sha256(beacon outputValue || cell id), ascending.
- Sensitivity (reported, not used): the order with (1) replaced by the members' maximum raw rating.
"""
import hashlib, json, re, sys
from collections import Counter
from pathlib import Path

RUNS = ['codex-1', 'codex-2', 'grok-1', 'grok-2']
DET = {'no': 0, 'partly': 1, 'yes': 2}


def entries(d):
    out = {}
    for run in RUNS:
        text = (Path(d) / run / 'enumeration.md').read_text(encoding='utf-8')
        body = re.split(r'^## ', text, flags=re.M)[0]          # everything before the first level-2 section
        qc = {}
        q = Path(d) / run / 'quote-check.txt'
        if q.exists():
            for line in q.read_text().splitlines():
                m = re.match(r'(E\d+) (\w+)$', line)
                if m: qc[m.group(1)] = m.group(2)
        parts = re.split(r'^### (E\d+)\s*$', body, flags=re.M)
        for eid, blk in zip(parts[1::2], parts[2::2]):
            f = {}
            for m in re.finditer(r'^- (\w[\w-]*):\s*(.*(?:\n(?!- \w)(?!###).*)*)', blk, flags=re.M):
                f[m.group(1)] = ' '.join(m.group(2).split())
            sil = re.match(r'\s*([1-5])', f.get('silent', ''))
            det = re.match(r'\s*(yes|partly|no)\b', f.get('detectable', ''))
            sec = re.search(r'§\s*([0-9]+(?:\.[0-9]+)*)', f.get('source', ''))
            out[f'{run}:{eid}'] = dict(run=run, n=int(eid[1:]), fields=f, silent=int(sil.group(1)) if sil else None,
                                       det=det.group(1) if det else 'no',
                                       sec=tuple(int(x) for x in sec.group(1).split('.')) if sec else (0,),
                                       verified=qc.get(eid) in ('VERIFIED', 'SPLIT'))
    return out


def packet(d):
    es = entries(d)
    keep = ['contract', 'source', 'stated', 'violation', 'at-risk', 'detectable']   # no ratings, no basis
    lines = []
    for k, e in es.items():
        lines.append(f'### {k}')
        lines += [f'- {f}: {e["fields"].get(f, "")}' for f in keep]
        lines.append('')
    return '\n'.join(lines)


def order(d, ma, mb, beacon):
    es = entries(d)
    ga = {frozenset(g) for g in json.load(open(ma))['groups']}
    gb = {frozenset(g) for g in json.load(open(mb))['groups']}
    unknown = set().union(*ga, *gb) - set(es)
    if unknown: sys.exit(f'merge names unknown entries: {sorted(unknown)[:5]}')
    accepted = [g for g in ga & gb if len(g) > 1]
    covered = set().union(*accepted) if accepted else set()
    cells = accepted + [frozenset([k]) for k in es if k not in covered]
    key_first = lambda g: min((RUNS.index(es[k]['run']), es[k]['n']) for k in g)
    cells.sort(key=key_first)
    pr = {}
    for run in RUNS:
        vals = [e['silent'] for e in es.values() if e['run'] == run and e['silent'] is not None]
        for k, e in es.items():
            if e['run'] == run and e['silent'] is not None:
                pr[k] = (sum(v < e['silent'] for v in vals) + 0.5 * sum(v == e['silent'] for v in vals)) / len(vals)
    rows = []
    for i, g in enumerate(cells, 1):
        cid = f'D{i}'
        sil = [pr[k] for k in g if k in pr]
        dets = Counter(es[k]['det'] for k in g)
        top = max(dets.values()); det = min((DET[x] for x, c in dets.items() if c == top))
        rows.append(dict(id=cid, members=sorted(g, key=lambda k: (RUNS.index(es[k]['run']), es[k]['n'])),
                         verified=any(es[k]['verified'] for k in g), silent=sum(sil) / len(sil) if sil else 0.0,
                         silent_max=max((es[k]['silent'] or 0) for k in g), det=det, sec=min(es[k]['sec'] for k in g),
                         tie=hashlib.sha256((beacon + cid).encode()).hexdigest()))
    main = sorted(rows, key=lambda r: (not r['verified'], -r['silent'], r['det'], r['sec'], r['tie']))
    sens = sorted(rows, key=lambda r: (not r['verified'], -r['silent_max'], r['det'], r['sec'], r['tie']))
    return dict(accepted_groups=len(accepted), cells=len(cells),
                order=[{k: (list(v) if isinstance(v, tuple) else v) for k, v in r.items()} for r in main],
                sensitivity_order=[r['id'] for r in sens])


if __name__ == '__main__':
    if sys.argv[1] == 'packet': print(packet(sys.argv[2]))
    elif sys.argv[1] == 'order': print(json.dumps(order(*sys.argv[2:6]), indent=1))
    else: sys.exit(__doc__)
