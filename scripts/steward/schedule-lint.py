#!/usr/bin/env python3
"""Steward's static lint for shared schedules against testbed/schedule-format.md (v2.2 and the v3, v4, v5 addenda).
derives: testbed/schedule-format.md (A1, A2, R1 to R3, L1, T1, E1); tests/pairs-v4.md (pair name = derivation tag)

usage: uv run --with pyyaml python3 scripts/steward/schedule-lint.py <schedule.yaml>...

A lint, not a compiler: it checks what can be decided from the text (shape, derivation against the pairs file,
cells matching actions, A2's crash and restart order for named processes, R1's request ids, names and operators,
R2's whole ticks, R3's amnesia after a crash, selectors only after a request, known trigger events, the end).
It cannot check that a liveness schedule leaves its premise's set connected (L3); that is read by hand, and every
C1.4 or C3.4 schedule's comment must say which set stays connected. Its selector rule asks only for an earlier
`request`, weaker than A1's "after a Grant can have occurred" (P58's first version passed with a grantor selector
meant before any grant); read selectors by hand too. Exit status 1 if anything is reported.
"""
import re, sys
from fractions import Fraction
from pathlib import Path
import yaml

PAIRS = Path(__file__).resolve().parents[2] / 'tests' / 'pairs-v4.md'
SEL = {'grantor', 'holder', 'non-grantor', 'non-member', 'rest'}
EVENTS = {'Request', 'Grant', 'WriteAttempt', 'WriteAccept', 'WriteReject', 'WriteAck', 'ReadAttempt', 'ReadAccept',
          'ReadReject', 'ReadAck', 'Fault', 'Agree', 'Agreed', 'ConfigCommitted', 'ReconfigSend', 'ReconfigRequest',
          'ReconfigRefused', 'ReconfigAck', 'Overflow'}
CELL_OF = {'crash': 'F1.1', 'restart': 'F1.1', 'partition': 'F1.2', 'pause': 'F1.3', 'resume': 'F1.3', 'cut': 'F2.1',
           'drop': 'F2.2', 'reconfigure': 'F3.1', 'clock': 'F3.2'}


def pairs():
    out = {}
    for m in re.finditer(r'^\| (P\d+) \| ([^|]+) \|', PAIRS.read_text(), re.M):
        out[m.group(1)] = {x.strip() for x in m.group(2).split(',')}
    return out


def lint(path, known):
    bad, d = [], yaml.safe_load(Path(path).read_text())
    say = lambda msg: bad.append(f"{path}: {msg}")
    name = d.get('schedule')
    if name != Path(path).stem:
        say(f"schedule name {name} is not the file name")
    if name in known and set(d.get('derives', [])) != known[name]:
        say(f"derives {d.get('derives')} is not the pairs file's {sorted(known[name])}")
    for k in ('processes', 'steps', 'end', 'bound'):
        if k not in d:
            say(f"missing {k}")
    pr = d.get('processes', {})
    lease, clients, storage = pr.get('lease', []), pr.get('clients', []), pr.get('storage', [])
    config, ops = pr.get('config', lease), pr.get('operators', ['op'])
    if not set(config) <= set(lease):
        say(f"config {config} is not a subset of lease")
    procs = set(lease) | set(clients) | set(storage) | set(ops)
    life = d.get('lifetime', 1)
    if not isinstance(life, int) or life < 1:
        say(f"lifetime {life} is not a positive whole number of ticks")
    crashed, ids, requested, crashed_ng = set(), set(), False, False

    def target(x, what, allow=SEL - {'rest', 'non-member'}):
        if x not in procs and x not in allow:
            say(f"{what}: {x} is neither a process nor an allowed selector")
        if x in SEL - {'rest'} and not requested:   # rest is static (Rule A1): fixed by the other side, not by a grant
            say(f"{what}: selector {x} before any request")

    for i, st in enumerate(d.get('steps', []), 1):
        at, do = st.get('at'), st.get('do', {})
        if at != 'start':
            if not isinstance(at, dict) or at.get('event') not in EVENTS:
                say(f"step {i}: unknown trigger {at}")
        acts = [k for k in do if k not in ('cell', 'to', 'id', 'operator', 'value', 'token', 'step', 'amnesia')]
        if len(acts) != 1:
            say(f"step {i}: not exactly one action in {do}"); continue
        a, v = acts[0], do[acts[0]]
        cell = do.get('cell')
        if a in ('request', 'write', 'read'):
            if cell:
                say(f"step {i}: workload action with a cell")
            target(v, f"step {i} {a}", allow={'holder'})
            requested |= a == 'request'
            continue
        if a == 'heal':
            if cell not in ('F1.2', 'F2.1', 'F2.2'):
                say(f"step {i}: heal under {cell}")
            continue
        want = 'F3.3' if a == 'restart' and do.get('amnesia') else CELL_OF.get(a)
        if cell != want:
            say(f"step {i}: {a} under cell {cell}, expected {want}")
        if a == 'crash':
            target(v, f"step {i} crash")
            if v in crashed:
                say(f"step {i}: crash of {v}, already crashed (A2)")
            if v == 'non-grantor':
                crashed_ng = True
            crashed.add(v)
        elif a == 'restart':
            if v == 'non-grantor':
                if not crashed_ng:
                    say(f"step {i}: restart non-grantor with no earlier crash non-grantor (A1 v2.2)")
            elif v not in crashed:
                say(f"step {i}: restart of {v}, which is not crashed (A2{', R3' if do.get('amnesia') else ''})")
            if do.get('amnesia') and v not in lease and v != 'non-grantor':
                say(f"step {i}: amnesic restart of {v}, not a lease node (R3)")
            crashed.discard(v)
        elif a == 'reconfigure':
            if not isinstance(v, list) or any(x in SEL for x in v):
                say(f"step {i}: reconfigure members must be a list of names, not selectors (R1)")
            to = do.get('to')
            if to not in lease and to not in ('grantor', 'non-grantor', 'non-member'):
                say(f"step {i}: reconfigure to {to}, not a lease node or allowed selector (R1)")
            elif to in SEL and to != 'non-member' and not requested:
                say(f"step {i}: selector {to} before any request")
            rid = do.get('id')
            if rid is None or rid in ids:
                say(f"step {i}: request id {rid} missing or not unique (R1)")
            ids.add(rid)
            if do.get('operator', 'op') not in ops:
                say(f"step {i}: operator {do.get('operator')} not in operators")
        elif a == 'clock':
            target(v, f"step {i} clock")
            ticks = Fraction(str(do.get('step', 0))) * life
            if ticks.denominator != 1:
                say(f"step {i}: clock step {do.get('step')} x lifetime {life} is not a whole number of ticks (R2)")
        elif a in ('cut', 'drop'):
            for pair in v:
                for x in pair:
                    target(x, f"step {i} {a}", allow=SEL - {'rest', 'non-member'})
        elif a == 'partition':
            for side in v:
                for x in side:
                    target(x, f"step {i} partition", allow=SEL - {'non-member'})
        elif a in ('pause', 'resume'):
            if v in lease or v in storage:
                say(f"step {i}: {a} of {v}, not a client (A2)")
    end = d.get('end')
    if end != 'quiescent' and not (isinstance(end, dict) and end.get('event') in EVENTS):
        say(f"end {end} is neither quiescent nor an event trigger (E1)")
    return bad


def main(paths):
    known, bad = pairs(), []
    for p in paths:
        bad += lint(p, known)
    for line in bad:
        print('LINT', line)
    print(f"schedule-lint: {len(paths)} schedules, {len(bad)} reports")
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
