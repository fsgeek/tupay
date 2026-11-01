#!/usr/bin/env python3
"""Tally X3 measures 6 and 7 from the raters' ratings.json files (tenth steward, 2026-11-01).
derives: X3 prereg measures 6, 7, X3-9; log 2026-11-01 "X3 measures 6 and 7: raters and packets, before any rating"
usage: tally.py <runs-dir>    (expects <runs-dir>/<m6|m7>-<impl|model>/<rater>/ratings.json)
Measure 6: propagation fraction = units labelled P / units, per rater; agreement and Cohen's kappa between raters.
Measure 7: entries CONTRADICTED with already_contradicted_before false (contradicted by this change), and
entries CONTRADICTED with it true (own column, per the registration); impl also on 77 (excluding the eight
workflow or result entries listed in experiments/X3/measure7-denominators.md: 24, 27, 28, 42, 48, 66, 73, 74).
"""
import json, os, sys
R = sys.argv[1]; RATERS = ('deepseek', 'kimi'); EXCL = {'24', '27', '28', '42', '48', '66', '73', '74'}

def load(m, s, r):
    p = f'{R}/{m}-{s}/{r}-2/ratings.json'   # a rerun after a harness failure, if any, is the rater's answer
    if not os.path.exists(p): p = f'{R}/{m}-{s}/{r}/ratings.json'
    if not os.path.exists(p): return None
    j = json.load(open(p)); return j['ratings'] if j else None

def kappa(a, b, labels):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(l) / n) * (b.count(l) / n) for l in labels)
    return po, (po - pe) / (1 - pe) if pe < 1 else float('nan')

for s in ('impl', 'model'):
    rs = {r: load('m6', s, r) for r in RATERS}
    print(f'## m6 {s}')
    lab = {}
    for r, v in rs.items():
        if v is None: print(f'  {r}: missing'); continue
        d = {x['unit']: x['label'].strip().upper()[:1] for x in v}; lab[r] = d
        p = sum(1 for x in d.values() if x == 'P'); print(f'  {r}: P {p}/{len(d)} = {p/len(d):.3f}')
    if len(lab) == 2:
        u = sorted(set(lab['deepseek']) & set(lab['kimi'])); a = [lab['deepseek'][k] for k in u]; b = [lab['kimi'][k] for k in u]
        po, k = kappa(a, b, ('C', 'P')); print(f'  agreement {po:.3f} on {len(u)}, kappa {k:.3f}; disagree: {[k_ for k_ in u if lab["deepseek"][k_] != lab["kimi"][k_]]}')
for s in ('impl', 'model'):
    print(f'## m7 {s}')
    ver = {}
    for r in RATERS:
        v = load('m7', s, r)
        if v is None: print(f'  {r}: missing'); continue
        d = {str(x['entry']).replace('impl ', '').replace('model ', '').strip(): x for x in v}; ver[r] = d
        new = sorted(k for k, x in d.items() if x['verdict'] == 'CONTRADICTED' and not x.get('already_contradicted_before'))
        old = sorted(k for k, x in d.items() if x['verdict'] == 'CONTRADICTED' and x.get('already_contradicted_before'))
        ext = sum(1 for x in d.values() if x['verdict'] == 'EXTENDED')
        line = f'  {r}: contradicted by X3 {len(new)}/{len(d)} {new}; contradicted, flagged before {len(old)} {old}; extended {ext}'
        if s == 'impl': line += f'; on 77: {len([k for k in new if k not in EXCL])}'
        print(line)
    if len(ver) == 2:
        u = sorted(set(ver['deepseek']) & set(ver['kimi']))
        a = [ver['deepseek'][k]['verdict'] for k in u]; b = [ver['kimi'][k]['verdict'] for k in u]
        po, k = kappa(a, b, ('CONTRADICTED', 'EXTENDED', 'UNCHANGED')); print(f'  agreement {po:.3f} on {len(u)}, kappa {k:.3f}')
