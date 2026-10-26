#!/usr/bin/env python3
"""D2 phases 0a and 1: merge packets, agreed merges, GUARANTEES.md, and the registered order.
derives: experiments/D2/design.md draft 2, "Phase 0a" and "Phase 1" (D1's d1-phase1.py, with D1's tier 3 dropped)

usage:
  d2-phase.py packet-g <phase0a-dir>                      merge packet of the two guarantee lists (report removed)
  d2-phase.py guarantees <phase0a-dir> <merge-a.json> <merge-b.json>   print GUARANTEES.md
  d2-phase.py packet-e <phase0-dir>                       merge packet of the four enumerations (no ratings, basis,
                                                          Recognised or report sections)
  d2-phase.py order <phase0-dir> <merge-a.json> <merge-b.json> <beacon-outputValue-hex>   the ordered cells (JSON)
  d2-phase.py cells <phase0-dir> <order.json>             print CELLS.md

Guarantee lists are <phase0a-dir>/<run>/guarantees.md for runs codex, grok (ids <run>:G<n>); enumerations are
<phase0-dir>/<run>/enumeration.md for codex-1, codex-2, grok-1, grok-2 (ids <run>:E<n>). A merge is JSON
{"groups": [[id, ...], ...]}. Written 2026-10-26, before any list existed.
Rules, from the design:
- A group is accepted iff both merges contain exactly that set of ids.
- Guarantees: an accepted group is kept iff it holds ids from both runs; GUARANTEES.md lists kept groups as G1, G2, ...
  in the order of their first codex member's number, each with every member's guarantee and source, unedited.
- Cells: every entry in no accepted group is a cell of its own; ids D1, D2, ... by first member (runs in the order
  above, then E number). Order: (0) a verified quotation in any member first; (1) silent descending, as the mean over
  members of each entry's percentile rank within its own list; (2) detectable no < partly < yes, the most common
  among members, ties to the less detectable; (3) sha256(beacon outputValue || cell id) ascending. D1's tier
  "earliest source" is not used (D2 design draft 2, review finding 9).
- CELLS.md gives each cell, in order, its members' contract, source, violation, at-risk, detectable and silent fields.
"""
import hashlib, json, re, sys
from collections import Counter
from pathlib import Path

G_RUNS, E_RUNS = ['codex', 'grok'], ['codex-1', 'codex-2', 'grok-1', 'grok-2']
DET = {'no': 0, 'partly': 1, 'yes': 2}


def parse(path, letter):
    text = Path(path).read_text(encoding='utf-8')
    body = re.split(r'^## ', text, flags=re.M)[0]          # everything before the first level-2 section
    parts = re.split(rf'^### ({letter}\d+)\s*$', body, flags=re.M)
    out = []
    for eid, blk in zip(parts[1::2], parts[2::2]):
        f = {}
        for m in re.finditer(r'^- (\w[\w-]*):\s*(.*(?:\n(?!- \w)(?!###).*)*)', blk, flags=re.M):
            f[m.group(1)] = ' '.join(m.group(2).split())
        out.append((eid, f))
    return out


def qc(path):
    r = {}
    if Path(path).exists():
        for line in Path(path).read_text().splitlines():
            m = re.match(r'([EG]\d+) (\w+)$', line)
            if m: r[m.group(1)] = m.group(2)
    return r


def load(d, runs, fname, letter):
    es = {}
    for run in runs:
        q = qc(Path(d) / run / 'quote-check.txt')
        for eid, f in parse(Path(d) / run / fname, letter):
            sil = re.match(r'\s*([1-5])', f.get('silent', ''))
            det = re.match(r'\s*(yes|partly|no)\b', f.get('detectable', ''))
            es[f'{run}:{eid}'] = dict(run=run, n=int(eid[1:]), fields=f, silent=int(sil.group(1)) if sil else None,
                                      det=det.group(1) if det else 'no', verified=q.get(eid) in ('VERIFIED', 'SPLIT'))
    return es


def packet(es, keep):
    lines = []
    for k, e in es.items():
        lines.append(f'### {k}')
        lines += [f'- {f}: {e["fields"].get(f, "")}' for f in keep]
        lines.append('')
    return '\n'.join(lines)


def accepted(es, ma, mb):
    ga = {frozenset(g) for g in json.load(open(ma))['groups']}
    gb = {frozenset(g) for g in json.load(open(mb))['groups']}
    unknown = set().union(*ga, *gb) - set(es)
    if unknown: sys.exit(f'merge names unknown entries: {sorted(unknown)[:5]}')
    return [g for g in ga & gb if len(g) > 1]


def guarantees(d, ma, mb):
    es = load(d, G_RUNS, 'guarantees.md', 'G')
    kept = [g for g in accepted(es, ma, mb) if {es[k]['run'] for k in g} == set(G_RUNS)]
    kept.sort(key=lambda g: min(es[k]['n'] for k in g if es[k]['run'] == 'codex'))
    out = ['# GUARANTEES.md: what the log and recovery guarantee', '',
           'Extracted from the paper and the source by two readers independently; kept where both found the same '
           'guarantee. Each guarantee is given as each reader stated it, unedited.', '']
    for i, g in enumerate(kept, 1):
        out.append(f'### G{i}')
        for k in sorted(g, key=lambda k: (G_RUNS.index(es[k]['run']), es[k]['n'])):
            out.append(f'- guarantee: {es[k]["fields"].get("guarantee", "")}')
            out.append(f'  source: {es[k]["fields"].get("source", "")}')
        out.append('')
    return '\n'.join(out)


def order(d, ma, mb, beacon):
    es = load(d, E_RUNS, 'enumeration.md', 'E')
    acc = accepted(es, ma, mb)
    covered = set().union(*acc) if acc else set()
    cells = acc + [frozenset([k]) for k in es if k not in covered]
    cells.sort(key=lambda g: min((E_RUNS.index(es[k]['run']), es[k]['n']) for k in g))
    pr = {}
    for run in E_RUNS:
        vals = [e['silent'] for e in es.values() if e['run'] == run and e['silent'] is not None]
        for k, e in es.items():
            if e['run'] == run and e['silent'] is not None:
                pr[k] = (sum(v < e['silent'] for v in vals) + 0.5 * sum(v == e['silent'] for v in vals)) / len(vals)
    rows = []
    for i, g in enumerate(cells, 1):
        cid = f'D{i}'
        sil = [pr[k] for k in g if k in pr]
        dets = Counter(es[k]['det'] for k in g)
        top = max(dets.values()); det = min(DET[x] for x, c in dets.items() if c == top)
        rows.append(dict(id=cid, members=sorted(g, key=lambda k: (E_RUNS.index(es[k]['run']), es[k]['n'])),
                         verified=any(es[k]['verified'] for k in g), silent=sum(sil) / len(sil) if sil else 0.0,
                         silent_max=max((es[k]['silent'] or 0) for k in g), det=det,
                         tie=hashlib.sha256((beacon + cid).encode()).hexdigest()))
    main = sorted(rows, key=lambda r: (not r['verified'], -r['silent'], r['det'], r['tie']))
    sens = sorted(rows, key=lambda r: (not r['verified'], -r['silent_max'], r['det'], r['tie']))
    return dict(accepted_groups=len(acc), cells=len(cells), order=main, sensitivity_order=[r['id'] for r in sens])


def cells_md(d, order_json):
    es = load(d, E_RUNS, 'enumeration.md', 'E')
    keep = ['contract', 'source', 'violation', 'at-risk', 'detectable', 'silent']
    out = ['# CELLS.md: environment contracts of the log and recovery, in a fixed order', '',
           'Enumerated from the paper and the source by other readers; a cell with several statements is one contract '
           'stated by several readers. Take them in this order.', '']
    for r in json.load(open(order_json))['order']:
        out.append(f'### {r["id"]}')
        for k in r['members']:
            out += [f'- {f}: {es[k]["fields"].get(f, "")}' for f in keep]
            out.append('')
    return '\n'.join(out)


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'packet-g': print(packet(load(a[1], G_RUNS, 'guarantees.md', 'G'), ['guarantee', 'source', 'stated']))
    elif a[0] == 'guarantees': print(guarantees(*a[1:4]))
    elif a[0] == 'packet-e':
        print(packet(load(a[1], E_RUNS, 'enumeration.md', 'E'),
                     ['contract', 'source', 'stated', 'violation', 'at-risk', 'detectable']))
    elif a[0] == 'order': print(json.dumps(order(*a[1:5]), indent=1))
    elif a[0] == 'cells': print(cells_md(a[1], a[2]))
    else: sys.exit(__doc__)
