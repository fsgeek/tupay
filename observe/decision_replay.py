#!/usr/bin/env python3
"""Steward's decision-replay check (observe/schema.md v5 addendum, draft 4).
derives: C1.1, C3.1, C3.5, C3.7, C3.8, F3.2, F3.3 (decision inputs; evidence for each decision from its inputs;
C1.1 without a global order; decisions a function of their recorded inputs across runs)

usage: decision_replay.py [--extra-inputs a,b] <trace.jsonl>...   (every trace of one side: all schedules, seeds and
repetitions; --extra-inputs names the input names the artifact's README declares)

Part 1, evidence, per trace.
  storage    accept/serve iff token >= ledger; a served read returns stored_value; the record matches its inputs.
  Grant      its counted Agreed records name distinct nodes whose agreements are eligible for its configuration and
             form a majority of `members` (denominator the whole membership) (C3.7).
  ConfigCommitted (decided) of epoch e+1: counted by eligible majorities of e and of its members (C3.8); every
             [node, inc] in `readmits` has an Agreed from that incarnation among its counted records. C3.1: one
             decided commit per epoch, each after a record of its predecessor.
  Eligibility: incarnation 0, or re-admitted by a decided commit of an epoch at most the configuration's, other than
             the commit being checked (contract/v3.md, "Eligible agreement").
  Input names outside the schema's fixed list (and --extra-inputs) are reported.
Part 2, C1.1 without a global order, per trace: no token granted twice; a grant under a higher config_epoch carries a
higher token than every grant under a lower one; each node's Agree records for counted grant proposals, in its own
(inc, seq) order, carry strictly increasing tokens.
Part 3, function of inputs (C3.5), across all traces: decisions of one kind with equal inputs (each ref replaced by
the content of the record it names, recursively; member lists as sets) must have equal outcomes.

Stated limits. An Agree is matched to the Agreed that counted it by (node, incarnation, proposal), not by causes.
Part 1's "after a record of its predecessor" uses file order, which on an implementation side is collection order;
everything else that needs an order uses one process's own (inc, seq).
Exit status 1 if anything is reported.
"""
import json, sys
from collections import defaultdict

STORAGE = {'WriteAccept', 'WriteReject', 'ReadAccept', 'ReadReject'}
IDENT = {'proc', 'inc', 'seq', 'causes', 'run', 'side'}
FIXED = {'token', 'ledger', 'stored_value', 'value', 'agreed', 'members', 'config_epoch', 'grantor_term', 'last_token',
         'clock', 'last_grant_at', 'old_members', 'old_epoch', 'request_id', 'requested_members', 'pending', 'commit'}
SETS = {'members', 'old_members', 'requested_members', 'readmits'}


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
    if isinstance(v, list) and field in SETS:
        return sorted(json.dumps(x, sort_keys=True) for x in v)
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
        return ('Grant', (r.get('token'), r.get('client'), r.get('config_epoch')))
    if e == 'ConfigCommitted':
        return ('ConfigCommitted', (r.get('epoch'), tuple(sorted(r.get('members', []))),
                                    tuple(sorted(tuple(x) for x in r.get('readmits', [])))))
    return ('ReconfigRefused', (r.get('reason'),))


def prop_key(p):
    return json.dumps(norm(p), sort_keys=True)


def evidence(path, recs, allowed):
    bad = []
    by = {key(r): r for r in recs}
    members_of, readmitted = {}, []   # readmitted: (epoch, node, inc, record key of the commit)
    for r in recs:
        if r['event'] == 'ConfigCommitted':
            members_of.setdefault(r['epoch'], set(r.get('members', [])))
            if r.get('decided'):
                readmitted += [(r['epoch'], n, i, key(r)) for n, i in r.get('readmits', [])]

    def eligible(node, inc, epoch, deciding):
        return inc == 0 or any(n == node and i == inc and ep <= epoch and k != deciding for ep, n, i, k in readmitted)

    def counted(r):
        out = []
        for i in r.get('inputs', []):
            if i['name'] == 'agreed' and 'ref' in i:
                hit = by.get(rkey(i['ref']))
                if hit and hit['event'] == 'Agreed':
                    out.append(hit)
        return out

    def majority(ags, members, epoch, deciding):
        got = {a['node'] for a in ags
               if a['node'] in members and eligible(a['node'], a.get('node_incarnation', 0), epoch, deciding)}
        return len(got) * 2 > len(members), got

    decided_epochs = defaultdict(list)
    for i, r in enumerate(recs):
        if not is_decision(r):
            continue
        tag = f"{path}: {r['proc']}#{r.get('inc', 0)}.{r['seq']} {r['event']}"
        if 'inputs' not in r:
            bad.append(f"{tag}: no inputs"); continue
        for name in sorted({x['name'] for x in r['inputs']} - allowed):
            bad.append(f"{tag}: input name {name} outside the fixed list")
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
            mem, ep = m.get('members'), m.get('config_epoch')
            if mem is None or ep is None or ep != r.get('config_epoch'):
                bad.append(f"{tag}: grant inputs lack members/config_epoch or disagree with the record"); continue
            ok, got = majority(counted(r), set(mem), ep, key(r))
            if not ok:
                bad.append(f"{tag}: counted eligible nodes {sorted(got)} are not a majority of {sorted(mem)} (C3.7)")
        elif e == 'ConfigCommitted':
            ep = r['epoch']
            decided_epochs[ep].append(i)
            old = members_of.get(ep - 1)
            if old is None or not any(x['event'] == 'ConfigCommitted' and x['epoch'] == ep - 1 for x in recs[:i]):
                bad.append(f"{tag}: no record of epoch {ep - 1} before this commit (C3.1)"); continue
            ags = counted(r)
            ok_old, _ = majority(ags, old, ep - 1, key(r))
            ok_new, _ = majority(ags, set(r.get('members', [])), ep, key(r))
            if not (ok_old and ok_new):
                bad.append(f"{tag}: not counted by majorities of epoch {ep - 1} and epoch {ep} (C3.8)")
            for n, inc in r.get('readmits', []):
                if not any(a['node'] == n and a.get('node_incarnation', 0) == inc for a in ags):
                    bad.append(f"{tag}: readmits {n}#{inc} without an Agreed from it for this proposal")
    for ep, idx in decided_epochs.items():
        if len(idx) > 1:
            bad.append(f"{path}: epoch {ep} decided {len(idx)} times (C3.1)")
    # Part 2: C1.1 without a global order
    grants = [r for r in recs if r['event'] == 'Grant']
    seen = defaultdict(int)
    for g in grants:
        seen[g.get('token')] += 1
    for tok, n in seen.items():
        if n > 1:
            bad.append(f"{path}: token {tok} granted {n} times (C1.1)")
    for g in grants:
        for h in grants:
            if g.get('config_epoch', 0) < h.get('config_epoch', 0) and not h.get('token', 0) > g.get('token', 0):
                bad.append(f"{path}: grant under epoch {h.get('config_epoch')} with token {h.get('token')} "
                           f"not above epoch {g.get('config_epoch')}'s token {g.get('token')} (C1.1)")
    counted_props = set()
    for g in grants:
        for a in counted(g):
            counted_props.add((a['node'], a.get('node_incarnation', 0), prop_key(a.get('proposal', {}))))
    agrees = defaultdict(list)
    for r in recs:
        if r['event'] == 'Agree' and 'token' in r.get('proposal', {}) and \
                (r['node'], r.get('incarnation', 0), prop_key(r['proposal'])) in counted_props:
            agrees[r['node']].append(r)
    for node, rs in agrees.items():
        top = None
        for r in sorted(rs, key=lambda x: (x.get('inc', 0), x['seq'])):
            t = r['proposal']['token']
            if top is not None and t <= top:
                bad.append(f"{path}: {node}#{r.get('inc', 0)} agreed to token {t} after token {top} (C1.1)")
            top = t if top is None else max(top, t)
    return bad


def main(argv):
    allowed = set(FIXED)
    if argv[:1] == ['--extra-inputs']:
        allowed |= set(argv[1].split(',')); argv = argv[2:]
    bad, groups = [], defaultdict(lambda: defaultdict(list))
    for p in argv:
        recs = load(p)
        bad += evidence(p, recs, allowed)
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
    print(f"decision-replay: {len(argv)} traces, {len(bad)} invalid, {len(conflicts)} UNEXPLAINED inputs")
    return 1 if bad or conflicts else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
