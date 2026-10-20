#!/usr/bin/env python3
"""Steward's independent check of the observability layer.
derives: C1.1, C1.2, C1.3, F1.1, F1.2, F1.3 (observe/schema.md: the provenance question)

For every WriteAccept and WriteReject in an observe file: follow `causes`
backwards and require that the chain reaches a Grant whose token equals the
decision's token, and that grantor_term on the decision equals that Grant's.
Also require highest_before to be present. Prints one line per file.
"""
import json, sys, glob

def check(path):
    recs = {}
    order = []
    for line in open(path):
        line = line.strip()
        if not line: continue
        r = json.loads(line)
        recs[(r['proc'], r['seq'])] = r
        order.append(r)
    decisions = [r for r in order if r['event'] in ('WriteAccept', 'WriteReject')]
    bad = []
    for d in decisions:
        if 'highest_before' not in d: bad.append((d, 'no highest_before')); continue
        seen, stack, found = set(), list(d.get('causes', [])), None
        while stack:
            c = stack.pop(); k = (c['proc'], c['seq'])
            if k in seen: continue
            seen.add(k)
            r = recs.get(k)
            if r is None: bad.append((d, f'dangling cause {k}')); break
            if r['event'] == 'Grant' and r.get('token') == d.get('token'):
                found = r; break
            stack.extend(r.get('causes', []))
        if found is None:
            if not any(b[0] is d for b in bad): bad.append((d, 'no Grant with this token reachable'))
        elif found.get('grantor_term') != d.get('grantor_term'):
            bad.append((d, f"term mismatch: decision {d.get('grantor_term')} grant {found.get('grantor_term')}"))
    return len(decisions), bad

tot = 0
for path in sys.argv[1:]:
    n, bad = check(path)
    tot += len(bad)
    status = 'OK' if not bad else 'FAIL'
    print(f'{status} {path}: {n} decisions, {len(bad)} untraceable')
    for d, why in bad[:5]:
        print(f'   {d["event"]} proc={d["proc"]} seq={d["seq"]} token={d.get("token")}: {why}')
sys.exit(1 if tot else 0)
