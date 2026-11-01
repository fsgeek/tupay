#!/usr/bin/env python3
"""X3 measure 4, the residue procedure, mechanised (tenth steward, 2026-11-01).

derives: X3 prereg measure 4 (X2 prereg measure 4's fixed procedure, X3 terms).

Usage: residue.py <export-repo> [ref]   (ref defaults to author/main)
Reads the side's diff from its inputs commit (the root commit of ref) to ref,
with `git show`, as data. Nothing in the repository is executed.

(i)   A code file in the diff that mentions a term in a non-comment line must
      carry a `derives:` tag naming one of the term's ids anywhere in the file.
      Each (file, term) without one is a CANDIDATE; the registered exclusions
      (TLC .cfg files, generated files, YAML key names a compiler parses, Go
      configuration structs that hold no membership, Unix-time code) need a
      reading, so candidates are listed for the steward to dispose of in
      writing, never dropped by this script beyond file-type exclusions.
(ii)  Tags that name a list or range of pairs/schedules are listed for reading
      against what the element runs.
(iii) Tags naming a retired id (C3.2, C3.3, C3.6, P34-P39, P55-P57) are counted.
"""
import re, subprocess, sys

TERMS = {  # term -> (pattern on a code line, ids that satisfy it)
    'reconfig': (r'reconfig', {'F3.1', 'C3.4', 'C3.8'}),
    'config/epoch': (r'config|epoch', {'C3.1', 'C3.7', 'C3.8', 'F3.1'}),
    'clock': (r'clock', {'F3.2', 'C3.5'}),
    'amnesia/incarnation': (r'amnesi|incarnation', {'F3.3'}),
}
CODE = ('.go', '.tla', '.py', '.sh')
EXCLUDE_TYPE = ('.cfg',)
RETIRED = {'C3.2', 'C3.3', 'C3.6'} | {f'P{n}' for n in list(range(34, 40)) + list(range(55, 58))}
COMMENT = re.compile(r'^\s*(//|#|\\\*|\(\*|\*|--)')
ID = re.compile(r'\b([CF]\d+\.\d+|P\d+|H\d+)\b')
LIST = re.compile(r'\bP\d+\s*(-|to|–|\.\.)\s*P?\d+|\bP\d+(\s*,\s*P\d+){2,}')

def git(repo, *a):
    return subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True, check=True).stdout

def tags(text):
    ids = set()
    for line in text.splitlines():
        i = line.find('derives:')
        if i >= 0:
            ids |= set(ID.findall(line[i:]))
    return ids

def main(repo, ref='author/main'):
    root = git(repo, 'rev-list', '--max-parents=0', ref).split()[0]
    files = [f for f in git(repo, 'diff', '--name-only', '--diff-filter=AM', root, ref).split('\n') if f]
    cand, lists, retired = [], [], []
    for f in files:
        if f.endswith(EXCLUDE_TYPE) or not f.endswith(CODE):
            continue
        text = git(repo, 'show', f'{ref}:{f}')
        have = tags(text)
        for line in text.splitlines():
            if 'derives:' in line and LIST.search(line):
                lists.append((f, line.strip()[:200]))
        for r in sorted(have & RETIRED):
            retired.append((f, r))
        code = [l for l in text.splitlines() if not COMMENT.match(l)]
        for term, (pat, ids) in TERMS.items():
            hits = [l for l in code if re.search(pat, l, re.I)]
            if hits and not (have & ids):
                cand.append((f, term, len(hits), hits[0].strip()[:120]))
    print(f'repo {repo} ref {ref} root {root[:7]}: {len(files)} files in diff')
    print(f'(i) candidates: {len(cand)}')
    for c in cand:
        print('  CAND', c[0], '|', c[1], '|', c[2], 'lines | e.g.', c[3])
    print(f'(ii) list/range tags for reading: {len(lists)}')
    for l in lists:
        print('  LIST', l[0], '|', l[1])
    print(f'(iii) retired ids: {len(retired)}')
    for r in retired:
        print('  RETIRED', r[0], '|', r[1])

if __name__ == '__main__':
    main(*sys.argv[1:])
