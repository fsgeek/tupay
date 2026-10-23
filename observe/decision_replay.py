#!/usr/bin/env python3
"""Steward's decision-replay check (observe/schema.md v5 addendum, draft 3).
derives: C3.1, C3.2, C3.3, C3.5, C3.6, F3.2, F3.3 (decision inputs; validity of each decision from its inputs;
voting promises; decisions a function of their recorded inputs across runs)

usage: decision_replay.py <trace.jsonl>...   (every trace of one side: all schedules, seeds and repetitions)

Part 1, validity, per trace.
  storage    accept/serve iff token >= ledger; a served read returns stored_value; the record matches its inputs.
  Grant      its counted Agreed records name distinct eligible voters forming a majority of `members` (denominator the
             whole membership); token > sealed_token; sealed_token equals the trace's highest_token for config_epoch.
  ConfigCommitted (decided) of epoch e+1: counted by majorities of e and of its members; highest_token at least every
             reported_token counted from e. C3.1: one decided commit per epoch, each after its predecessor's record.
  C3.6       on each voter's own Vote records in (inc, seq) order: no grant vote under e after a configuration vote of
             a higher epoch in the same incarnation; no two configuration votes for one epoch with different members.
Part 2, function of inputs (C3.5), across all traces: decisions of one kind with equal inputs (each ref replaced by
the content of the record it names, recursively; member lists as sets) must have equal outcomes.

Stated limits. Eligibility needs "a request sent after the amnesia": the amnesia Fault and the operator's ReconfigSend
are compared in file order, which on an implementation side is the testbed's collection order. Everything else that
needs an order uses one process's own (inc, seq).
Exit status 1 if anything is reported.
"""
import json, sys
from collections import defaultdict

STORAGE = {'WriteAccept', 'WriteReject', 'ReadAccept', 'ReadReject'}
IDENT = {'proc', 'inc', 'seq', 'causes', 'run', 'side'}


def key(r):
    return (r['proc'], r.get('inc', 0), r['seq'])


def rkey(ref):
    return (ref['proc'], ref.get('inc', 0), ref['seq'])


def load(path):
    return [json.loads(l) for l in open(path) if l.strip()]


def inmap(r):
    return {i['name']: i.get('value') for i in r.get('inputs', [])}


def is_decision(r):
    return r['event'] in STORAGE or r['event'] in ('Grant', 'ReconfigRefused') or \
        (r['event'] == 'ConfigCommitted' and r.get('decided') is True)


def norm(v, field=None):
    if isinstance(v, dict):
        return {k: norm(x, k) for k, x in sorted(v.items())}
    if isinstance(v, list) and field == 'members':
        return sorted(v)
    if isinstance(v, list):
        return [norm(x) for x in v]
    return v


def canon(r, recs, depth=0):
    """The decision's inputs as a canonical string, each ref replaced by the referenced record's content."""
    items = []
    for i in r.get('inputs', []):
        item = {'name': i['name'], 'value': norm(i.get('value'), i['name'])}
        if 'ref' in i and depth < 6:
            t = recs.get(rkey(i['ref']))
            item['ref'] = None if t is None else \
                {k: norm(v, k) for k, v in sorted(t.items()) if k not in IDENT and k != 'inputs'} | \
                ({'inputs': canon(t, recs, depth + 1)} if 'inputs' in t else {})
        items.append(json.dumps(item, sort_keys=True))
    return json.dumps(sorted(items))


def outcome(r):
    e = r['event']
    if e in STORAGE:
        return ('storage', (e, json.dumps(r.get('value')) if e == 'ReadAccept' else None))
    if e == 'Grant':
        return ('Grant', (r.get('token'), r.get('client'), r.get('config_epoch'), r.get('grantor_term')))
    if e == 'ConfigCommitted':
        return ('ConfigCommitted', (r.get('epoch'), tuple(sorted(r.get('members', []))), r.get('highest_token')))
    return ('ReconfigRefused', (r.get('reason'),))


def validity(path, recs):
    bad = []
    by = {key(r): (i, r) for i, r in enumerate(recs)}
    sealed, members_of = {}, {}
    for r in recs:
        if r['event'] == 'ConfigCommitted':
            sealed.setdefault(r['epoch'], r.get('highest_token', 0))
            members_of.setdefault(r['epoch'], set(r.get('members', [])))

    def eligible(voter, inc):
        if inc == 0:
            return True
        amn = [i for i, r in enumerate(recs) if r['event'] == 'Fault' and r.get('restart') == voter and r.get('amnesia')]
        if len(amn) < inc:
            return False
        start = amn[inc - 1]
        sent = {r.get('request_id') for r in recs[start:] if r['event'] == 'ReconfigSend'}
        return any(r['event'] == 'ConfigCommitted' and voter in r.get('members', []) and r.get('request_id') in sent
                   for r in recs[start:])

    def counted(r):
        out = []
        for i in r.get('inputs', []):
            if i['name'] == 'agreed' and 'ref' in i:
                hit = by.get(rkey(i['ref']))
                if hit and hit[1]['event'] == 'Agreed':
                    out.append(hit[1])
        return out

    def majority(ags, members):
        got = {a['voter'] for a in ags if a['voter'] in members and eligible(a['voter'], a.get('voter_incarnation', 0))}
        return len(got) * 2 > len(members), got

    decided_epochs = defaultdict(list)
    for i, r in enumerate(recs):
        if not is_decision(r):
            continue
        tag = f"{path}: {r['proc']}#{r.get('inc', 0)}.{r['seq']} {r['event']}"
        if 'inputs' not in r:
            bad.append(f"{tag}: no inputs"); continue
        m, e = inmap(r), r['event']
        if e in STORAGE:
            tok, led = m.get('token'), m.get('ledger')
            if tok is None or led is None:
                bad.append(f"{tag}: storage inputs lack token or ledger"); continue
            if tok != r.get('token') or led != r.get('highest_before'):
                bad.append(f"{tag}: record disagrees with its inputs")
            if (e in ('WriteAccept', 'ReadAccept')) != (tok >= led):
                bad.append(f"{tag}: outcome contradicts token {tok} vs ledger {led}")
            if e == 'ReadAccept' and r.get('value') != m.get('stored_value'):
                bad.append(f"{tag}: served value is not stored_value")
        elif e == 'Grant':
            mem, ep, st = m.get('members'), m.get('config_epoch'), m.get('sealed_token')
            if mem is None or ep is None or st is None or ep != r.get('config_epoch'):
                bad.append(f"{tag}: grant inputs lack members/config_epoch/sealed_token or disagree with the record"); continue
            ok, got = majority(counted(r), set(mem))
            if not ok:
                bad.append(f"{tag}: counted eligible voters {sorted(got)} are not a majority of {sorted(mem)}")
            if st != sealed.get(ep):
                bad.append(f"{tag}: sealed_token {st} is not the trace's highest_token {sealed.get(ep)} for epoch {ep}")
            if not r.get('token', 0) > st:
                bad.append(f"{tag}: token {r.get('token')} does not exceed sealed_token {st}")
        elif e == 'ConfigCommitted':
            ep = r['epoch']
            decided_epochs[ep].append(i)
            old = members_of.get(ep - 1)
            if old is None or not any(x['event'] == 'ConfigCommitted' and x['epoch'] == ep - 1 for x in recs[:i]):
                bad.append(f"{tag}: no record of epoch {ep - 1} before this commit (C3.1)"); continue
            ags = counted(r)
            ok_old, got_old = majority(ags, old)
            ok_new, _ = majority(ags, set(r.get('members', [])))
            if not (ok_old and ok_new):
                bad.append(f"{tag}: not counted by majorities of epoch {ep - 1} and epoch {ep}")
            rep = [a.get('reported_token', 0) or 0 for a in ags if a['voter'] in got_old]
            if rep and r.get('highest_token', 0) < max(rep):
                bad.append(f"{tag}: highest_token {r.get('highest_token')} below a reported token {max(rep)}")
    for ep, idx in decided_epochs.items():
        if len(idx) > 1:
            bad.append(f"{path}: epoch {ep} decided {len(idx)} times (C3.1)")
    votes = defaultdict(list)
    for r in recs:
        if r['event'] == 'Vote':
            votes[(r['proc'], r.get('inc', 0))].append(r)
    for (v, inc), vs in votes.items():
        top, by_epoch = -1, {}
        for r in sorted(vs, key=lambda x: x['seq']):
            p = r.get('proposal', {})
            if 'members' in p:
                ms = tuple(sorted(p['members']))
                if by_epoch.setdefault(p.get('epoch'), ms) != ms:
                    bad.append(f"{path}: {v}#{inc} voted for two configurations of epoch {p.get('epoch')} (C3.6)")
                top = max(top, p.get('epoch', -1))
            elif r.get('config_epoch', -1) < top:
                bad.append(f"{path}: {v}#{inc}.{r['seq']} voted for a grant under epoch {r.get('config_epoch')} "
                           f"after voting for epoch {top} (C3.6)")
    return bad


def main(paths):
    bad, groups = [], defaultdict(lambda: defaultdict(list))
    for p in paths:
        recs = load(p)
        bad += validity(p, recs)
        idx = {key(r): r for r in recs}
        for r in recs:
            if is_decision(r) and 'inputs' in r:
                kind, out = outcome(r)
                groups[(kind, canon(r, idx))][out].append(f"{p}:{r['proc']}#{r.get('inc', 0)}.{r['seq']}")
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
