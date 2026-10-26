#!/usr/bin/env python3
"""Check every `source` quotation of a D2 enumeration against the paper's text or the cited source file.
usage: d2-quote-check.py <enumeration.md> <paper.txt> <source-root>   one line per entry; exit 0 always (a report)
derives: experiments/D2/design.md draft 1, phase 0 "Quotation check" (D1's checker extended to <path>:<line>)
A `§...` citation is checked against the paper as D1's checker does (VERIFIED as a substring, SPLIT across a page
header, UNVERIFIED, MISSING). A `<path>:<line>` citation is checked in <source-root>/<path>: VERIFIED if the quotation
is a substring of the normalised text of lines line-20 to line+20, so a line number a little off or a quotation
spanning a line break still counts; UNVERIFIED if it is not there, or the file does not exist. Normalisation as D1:
lower case; curly quotes and dashes plain; line-break hyphenation joined; every run of whitespace one space."""
import os, re, sys
ENUM, PAPER, ROOT = sys.argv[1], sys.argv[2], sys.argv[3]
WINDOW = 20
def norm(s):
    s = s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    s = s.replace('–', '-').replace('—', '-').replace('ﬁ', 'fi').replace('ﬂ', 'fl')
    s = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', s)
    return re.sub(r'\s+', ' ', s).strip().lower()
paper = norm(open(PAPER, encoding='utf-8', errors='replace').read())
def in_paper(q):
    if q in paper: return 'VERIFIED'
    w = q.split(' ')
    for i in range(3, len(w) - 2):
        a, b = ' '.join(w[:i]), ' '.join(w[i:])
        ia = paper.find(a)
        while ia >= 0:
            ib = paper.find(b, ia + len(a))
            if 0 <= ib - (ia + len(a)) <= 600: return 'SPLIT'
            ia = paper.find(a, ia + 1)
    return 'UNVERIFIED'
def in_file(path, line, q):
    full = os.path.normpath(os.path.join(ROOT, path))
    if not full.startswith(os.path.normpath(ROOT) + os.sep) or not os.path.isfile(full): return 'UNVERIFIED'
    lines = open(full, encoding='utf-8', errors='replace').read().split('\n')
    lo, hi = max(0, line - 1 - WINDOW), min(len(lines), line + WINDOW)
    return 'VERIFIED' if q in norm('\n'.join(lines[lo:hi])) else 'UNVERIFIED'
entries = re.split(r'^### ([EG]\d+)\s*$', open(ENUM, encoding='utf-8').read(), flags=re.M)
counts = {}
for eid, body in zip(entries[1::2], entries[2::2]):
    # a quotation may wrap; an unnumbered section is cited by its heading in quotation marks, §"Heading"
    m = re.search(r'^- source:\s*(§\s*"[^"\n]*"|[^"\n]*?)\s*"(.+?)"\s*$', body, flags=re.M | re.S)
    if not m: status = 'MISSING'
    else:
        cite, q = m.group(1), norm(m.group(2).replace('…', ' ').replace('...', ' '))
        c = re.match(r'`?([\w./+-]+):(\d+)`?$', cite)
        status = in_file(c.group(1), int(c.group(2)), q) if c else in_paper(q)
    counts[status] = counts.get(status, 0) + 1
    print(f'{eid} {status}')
n = sum(counts.values())
ok = counts.get('VERIFIED', 0) + counts.get('SPLIT', 0)
print(f'{ENUM}: {n} entries, {ok} verified ({100 * ok // max(n, 1)}%), ' + ', '.join(f'{k} {v}' for k, v in sorted(counts.items())))
