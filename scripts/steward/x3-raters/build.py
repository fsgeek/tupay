#!/usr/bin/env python3
"""Build X3 measure 6 and measure 7 rater packets (tenth steward, 2026-11-01).

derives: X3 prereg measures 6 and 7; steward practice "Measure 6 ruling", "Measure 7 raters do not see the
adapting author's labels"; log 2026-11-01 "X3 measures 6 and 7: raters and packets, before any rating".

usage: build.py <out-dir>
Reads arm A's exported repositories (~/projects/tupay-x3-export-adapt-{impl,model}, ref author/main) as data.
Inputs given to raters are taken from each side's inputs commit (the root), i.e. exactly what the author had.
Excluded from every packet, by rule: commit messages; the README at any commit after the inputs commit (the
adapting author's labels); generated files (model/mutations/<pair>/*, written by mutate.py); non-code files;
the steward's at-risk list for measure 7; every steward hypothesis.
"""
import os, subprocess, sys

HOME = os.path.expanduser('~/projects')
CODE = ('.go', '.tla', '.py', '.sh')
INPUTS = ['contract/v3.md', 'failure-model/v3.md', 'testbed/schedule-format.md', 'observe/schema.md', 'tests/pairs-v4.md']
MODEL_IDS = ('1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 R2.1 R2.2 R2.3 R2.4 R2.5 R2.1-a R2.1-b '
             'X1.1 X1.2 X1.3 X1.4 X1.5 X1.6 X1.7 X1.8 V22.1 X2.1 X2.2 X2.3 X2.4 X2.5 X2.6 X2.7 FR.1 FR.2').split()
IMPL_IDS = [str(i) for i in range(1, 86)]

def git(repo, *a):
    return subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True, check=True).stdout

def keep(f):
    return f.endswith(CODE) and '/mutations/' not in f

def side(s):
    repo = f'{HOME}/tupay-x3-export-adapt-{s}'
    root = git(repo, 'rev-list', '--max-parents=0', 'author/main').split()[0]
    return repo, root

def inputs_block(repo, root):
    out = ['# The inputs the author worked from (as in its checkout)']
    for p in INPUTS:
        try:
            out += [f'## `{p}`', '````', git(repo, 'show', f'{root}:{p}'), '````']
        except subprocess.CalledProcessError:
            out += [f'## `{p}`: not present in this checkout']
    return '\n'.join(out)

M6 = '''# Rating task: measure 6 (propagation or conceptual), one rater, independent

You are rating changes an author made to an existing artifact when its inputs changed (a service contract and a
failure model moved from version 2 to version 3; the full version 3 inputs are below). Each **unit** is one file
as changed by one commit. Commit messages are withheld.

**The ruling you apply (fixed before any rating):** a unit is **conceptual** (C) iff it makes a choice the inputs
leave open: choosing between behaviours the inputs permit, or reading an ambiguous input. Implementing an
unambiguous prescription of the inputs, however much code it takes, is **propagation** (P). A unit that does
both is C. Judge from the diff and the inputs only; code comments are the author's and may be wrong.

Answer with one JSON object and nothing after it:
{"ratings": [{"unit": "U01", "label": "C" or "P", "reason": "one or two sentences naming the open choice, or the prescription implemented"}, ...]}
Every unit below gets exactly one entry.
'''

M7 = '''# Rating task: measure 7 (interpretations contradicted), one rater, independent

An author kept a README listing its **interpretations** of earlier inputs. The inputs then changed (service
contract and failure model to version 3, given in full below) and the author adapted its code. You get the
README **as it was before the change** and the **code diff** of the adaptation. You do not get the author's
updated README, on purpose: judge from the diff, not from the author's account of it.

For each listed entry of the old README (ids as numbered or labelled there), give one verdict:
- **CONTRADICTED**: the adapted code now handles some situation the entry makes a claim about differently from
  what the entry says.
- **EXTENDED**: every claim the entry makes still holds, and the diff changed the element the entry describes so
  that it also covers situations new in version 3.
- **UNCHANGED**: neither.
Also give **already_contradicted_before**: true iff the old README itself already marks the entry superseded,
contradicted or replaced (then judge the verdict only on whether this diff changes its status again).
Read entries as written; take a named set literally.

Answer with one JSON object and nothing after it:
{"ratings": [{"entry": "<id>", "verdict": "CONTRADICTED" | "EXTENDED" | "UNCHANGED", "already_contradicted_before": true | false, "reason": "one or two sentences citing the diff"}, ...]}
Every listed id gets exactly one entry.
'''

def m6(s):
    repo, root = side(s)
    units, n = [], 0
    for c in git(repo, 'rev-list', '--reverse', 'author/main').split()[1:]:
        for f in git(repo, 'diff-tree', '--no-commit-id', '-r', '--name-only', c).split():
            if keep(f):
                n += 1
                d = git(repo, 'diff', f'{c}^', c, '--', f)
                units.append((f'U{n:02d}', c[:7], f, d))
    body = [M6, inputs_block(repo, root), '# Units']
    for u, c, f, d in units:
        body += [f'## {u}: `{f}`', '````diff', d, '````']
    key = '\n'.join(f'{u} {c} {f}' for u, c, f, _ in units)
    return '\n'.join(body), key

def m7(s):
    repo, root = side(s)
    ids = MODEL_IDS if s == 'model' else IMPL_IDS
    files = [f for f in git(repo, 'diff', '--name-only', root, 'author/main').split() if keep(f)]
    diff = git(repo, 'diff', root, 'author/main', '--', *files)
    body = [M7, '# Entries to rate', ', '.join(ids), '', inputs_block(repo, root),
            f'# The README before the change (`{s}/README.md` at the inputs commit)', '````',
            git(repo, 'show', f'{root}:{s}/README.md'), '````', '# The code diff of the adaptation', '````diff', diff, '````']
    return '\n'.join(body), ' '.join(ids)

if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for s in ('impl', 'model'):
        for name, fn in (('m6', m6), ('m7', m7)):
            text, key = fn(s)
            open(f'{out}/{name}-{s}.md', 'w').write(text)
            open(f'{out}/{name}-{s}.key.txt', 'w').write(key + '\n')
            print(f'{name}-{s}: {len(text):,} chars')
