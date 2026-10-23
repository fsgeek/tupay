#!/usr/bin/env python3
"""Steward's decision-replay check (observe/schema.md v5 addendum, draft 2).
derives: C3.1, C3.2, C3.3, C3.5, F3.2, F3.3 (decision inputs; validity of each decision from its inputs; decisions a
function of their recorded inputs across runs)

usage: decision_replay.py <trace.jsonl>...   (every trace of one side: all schedules, seeds and repetitions)

Part 1, validity, per trace: each decision record is checked against its own `inputs`.
  storage    accept/serve iff token >= ledger; a served read returns stored_value; the record's token and
             highest_before match its inputs.
  Grant      the Agreed records it cites by ref are by distinct voters forming a majority of the `members` input,
             not counting amnesic voters not re-added; no counted voter had recorded ConfigCommitted for an epoch above
             `config_epoch` earlier in the trace; config_epoch matches the record.
  ConfigCommitted (decided: true) of epoch e+1: cited voters form majorities of configuration e (from the trace's
             ConfigCommitted for e) and of its own members.
Part 2, function of inputs (C3.5), across all traces: decisions of one kind with equal inputs (name-value sets, refs
ignored) must have equal outcomes. Each conflicting group is UNEXPLAINED inputs.

"Earlier in the trace" is the trace file's order. On the model side that is the behaviour's order; on an
implementation side it is the order in which the testbed collected records, which the schema does not promise is
causal. A voter's ConfigCommitted that the file places before its agreement but that happened after it would be
reported falsely; the judge reads any Part 1 stale-voter report with that in mind.
Exit status 1 if anything is reported.
"""
import json, sys
from collections import defaultdict

STORAGE = {'WriteAccept', 'WriteReject', 'ReadAccept', 'ReadReject'}


def load(path):
    out = []
    for line in open(path):
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def inmap(r):
    return {i['name']: i.get('value') for i in r.get('inputs', [])}


def canon(r):
    return frozenset((i['name'], json.dumps(i.get('value'), sort_keys=True)) for i in r.get('inputs', []))


def outcome(r):
    e = r['event']
    if e in STORAGE:
        return ('storage', (e, json.dumps(r.get('value'), sort_keys=True) if e == 'ReadAccept' else None))
    if e == 'Grant':
        return ('Grant', (r.get('token'), r.get('client')))
    if e == 'ConfigCommitted':
        return ('ConfigCommitted', (r.get('epoch'), tuple(sorted(r.get('members', [])))))
    if e == 'ReconfigRefused':
        return ('ReconfigRefused', (r.get('reason'),))
    return None


def is_decision(r):
    return r['event'] in STORAGE or r['event'] in ('Grant', 'ReconfigRefused') or \
        (r['event'] == 'ConfigCommitted' and r.get('decided') is True)


def validity(path, recs):
    bad = []
    by_key = {(r['proc'], r['seq']): (i, r) for i, r in enumerate(recs)}
    configs = {}                                  # epoch -> members, first seen
    for r in recs:
        if r['event'] == 'ConfigCommitted' and r.get('epoch') not in configs:
            configs[r['epoch']] = set(r.get('members', []))

    def amnesic_not_readded(node, at):
        last = None
        for i, r in enumerate(recs[:at]):
            if r['event'] == 'Fault' and r.get('restart') == node and r.get('amnesia'):
                last = i
        if last is None:
            return False
        sends = {r.get('request_id') for r in recs[last:at] if r['event'] == 'ReconfigSend'}
        return not any(r['event'] == 'ConfigCommitted' and node in r.get('members', []) and r.get('request_id') in sends
                       for r in recs[last:at])

    def voters(i, r):
        vs, refs = [], [x['ref'] for x in r.get('inputs', []) if 'ref' in x]
        for ref in refs:
            hit = by_key.get((ref['proc'], ref['seq']))
            if hit and hit[1]['event'] == 'Agreed':
                vs.append((hit[0], hit[1]))
        return vs

    def majority(vs, members, at):
        # the denominator is the whole membership; an amnesic voter not re-added is simply not counted
        got = {a['voter'] for _, a in vs if a['voter'] in members and not amnesic_not_readded(a['voter'], at)}
        return len(got) * 2 > len(members), got

    for i, r in enumerate(recs):
        if not is_decision(r):
            continue
        tag = f"{path}: {r['proc']}#{r['seq']} {r['event']}"
        if 'inputs' not in r:
            bad.append(f"{tag}: no inputs"); continue
        m = inmap(r)
        e = r['event']
        if e in STORAGE:
            tok, led = m.get('token'), m.get('ledger')
            if tok is None or led is None:
                bad.append(f"{tag}: storage inputs lack token or ledger"); continue
            if tok != r.get('token') or led != r.get('highest_before'):
                bad.append(f"{tag}: record disagrees with its inputs")
            ok = tok >= led
            if (e in ('WriteAccept', 'ReadAccept')) != ok:
                bad.append(f"{tag}: outcome contradicts token {tok} vs ledger {led}")
            if e == 'ReadAccept' and r.get('value') != m.get('stored_value'):
                bad.append(f"{tag}: served value is not stored_value")
        elif e == 'Grant':
            members, ep = m.get('members'), m.get('config_epoch')
            if members is None or ep is None or ep != r.get('config_epoch'):
                bad.append(f"{tag}: grant inputs lack members/config_epoch or disagree with the record"); continue
            vs = voters(i, r)
            ok, got = majority(vs, set(members), i)
            if not ok:
                bad.append(f"{tag}: counted voters {sorted(got)} are not a majority of {sorted(members)}")
            for j, a in vs:
                v = a['voter']
                if any(x['event'] == 'ConfigCommitted' and x['proc'] == v and x.get('epoch', -1) > ep for x in recs[:j]):
                    bad.append(f"{tag}: voter {v} had recorded a configuration above epoch {ep}")
        elif e == 'ConfigCommitted':
            ep = r.get('epoch')
            if ep == 0:
                continue
            old = configs.get(ep - 1)
            vs = voters(i, r)
            if old is None:
                bad.append(f"{tag}: no ConfigCommitted for epoch {ep - 1} in the trace"); continue
            ok_old, _ = majority(vs, old, i)
            ok_new, _ = majority(vs, set(r.get('members', [])), i)
            if not (ok_old and ok_new):
                bad.append(f"{tag}: not agreed by majorities of epoch {ep - 1} and epoch {ep}")
    return bad


def main(paths):
    bad, groups = [], defaultdict(lambda: defaultdict(list))
    for p in paths:
        recs = load(p)
        bad += validity(p, recs)
        for r in recs:
            if is_decision(r) and 'inputs' in r:
                kind, out = outcome(r)
                groups[(kind, canon(r))][out].append(f"{p}:{r['proc']}#{r['seq']}")
    conflicts = [(k, v) for k, v in groups.items() if len(v) > 1]
    for line in bad:
        print('INVALID', line)
    for (kind, _), outs in conflicts:
        print(f"UNEXPLAINED inputs {kind}: equal inputs, {len(outs)} outcomes: " +
              '; '.join(f"{o} at {w[0]}" for o, w in outs.items()))
    print(f"decision-replay: {len(paths)} traces, {len(bad)} invalid, {len(conflicts)} UNEXPLAINED inputs")
    return 1 if bad or conflicts else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
