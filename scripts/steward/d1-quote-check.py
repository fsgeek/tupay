#!/usr/bin/env python3
"""Check every `source` quotation of a D1 enumeration against the dissertation text.
usage: d1-quote-check.py <enumeration.md> [source.txt]     prints one line per entry; exit 0 always (a report, not a gate)
derives: experiments/D1/design.md draft 3, phase 0 "Quotation check"; Fable review finding 11
Normalisation: lower case; curly quotes and dashes to plain; line-break hyphenation joined; every run of whitespace one
space. VERIFIED: the quotation is a substring. SPLIT: it splits at a word boundary into two pieces of at least three
words, each a substring, the second starting within 600 characters after the first ends (a page header or figure
residue between them). UNVERIFIED otherwise, or MISSING when the entry has no quotation."""
import re, sys
ENUM = sys.argv[1]
SRC = sys.argv[2] if len(sys.argv) > 2 else __file__.rsplit('/', 3)[0] + '/experiments/D1/source/OngaroPhD.txt'
def norm(s):
    s = s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    s = s.replace('–', '-').replace('—', '-').replace('ﬁ', 'fi').replace('ﬂ', 'fl')
    s = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', s)
    return re.sub(r'\s+', ' ', s).strip().lower()
text = norm(open(SRC, encoding='utf-8').read())
entries = re.split(r'^### (E\d+)\s*$', open(ENUM, encoding='utf-8').read(), flags=re.M)
counts = {}
for eid, body in zip(entries[1::2], entries[2::2]):
    m = re.search(r'^- source:.*?"(.+)"\s*$', body, flags=re.M)
    if not m: status = 'MISSING'
    else:
        q = norm(m.group(1).replace('…', ' ').replace('...', ' '))
        status = 'UNVERIFIED'
        if q in text: status = 'VERIFIED'
        else:
            w = q.split(' ')
            for i in range(3, len(w) - 2):
                a, b = ' '.join(w[:i]), ' '.join(w[i:])
                ia = text.find(a)
                while ia >= 0:
                    ib = text.find(b, ia + len(a))
                    if 0 <= ib - (ia + len(a)) <= 600: status = 'SPLIT'; break
                    ia = text.find(a, ia + 1)
                if status == 'SPLIT': break
    counts[status] = counts.get(status, 0) + 1
    print(f'{eid} {status}')
n = sum(counts.values())
ok = counts.get('VERIFIED', 0) + counts.get('SPLIT', 0)
print(f'{ENUM}: {n} entries, {ok} verified ({100 * ok // max(n, 1)}%), ' + ', '.join(f'{k} {v}' for k, v in sorted(counts.items())))
