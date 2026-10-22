#!/usr/bin/env python3
"""Replay attribution: does a J1.1 or J1.5 violation in a trace arise from configurations?

derives: J1.1, J1.5, G1.4 (replay/contract.md v3); experiments/replay-prereg.md "Attribution"

Reads one observe file (replay/observe.md: one JSON record per line, per-member `seq`,
no cross-member clock). Finds violations of J1.1 and J1.5 and labels each one:
  configuration  the decisions involved counted majorities of different configurations
  mechanics      they did not (an error in the artifact's own mechanics)
A violation fires a detection route only if it is configuration-attributed.

Inference rules, fixed before any author run (the trace does not record a member's
current epoch, so the epoch in which a commit happened has to be inferred):
- A member's configuration at one of its records is the `config` of its latest
  ConfigInEffect at or before that record (by its own seq); before any, the scenario's
  initial configuration (passed with --initial).
- A Committed record by member M at seq s defines a commit decision only if M has an
  Elected record before s; its epoch e is that Elected's epoch and its configuration is
  M's configuration at s. Committed records with no earlier Elected of the same member
  are followers learning a commit and define nothing.
- J1.1: two Elected records with the same epoch and different members. Configuration-
  attributed iff their `config` fields differ.
- J1.5(a): a commit decision for the entry at index i (identified by the (epoch, kind,
  payload) of M's journal at i at seq s) in epoch e, and an Elected record of a member C
  with epoch > e whose journal at that record has no such entry at i. Configuration-
  attributed iff the commit decision's configuration differs from that Elected's config.
- J1.5(b): a Truncated(member X, from_index f) where f <= X's commit index (the largest
  index of X's own Committed records before it). The truncation's coordinator is the
  proc of the first cause of the Truncated record; configuration-attributed iff that
  coordinator's configuration at the cited record differs from the configuration of
  any commit decision for an index >= f, else mechanics.
usage: attribution.py <trace.jsonl> --initial m1,m2,m3,m4   prints one line per violation,
then a summary line; exit 0.
"""
import argparse, json
from collections import defaultdict


def load(path):
    recs = [json.loads(l) for l in open(path) if l.strip()]
    byproc = defaultdict(list)
    for r in recs:
        if r.get('proc') != 'env':
            byproc[r['proc']].append(r)
    for p in byproc:
        byproc[p].sort(key=lambda r: r['seq'])
    return byproc


def cfg(x):
    return tuple(sorted(x)) if x is not None else None


def config_at(recs, seq, initial):
    c = initial
    for r in recs:
        if r['seq'] > seq:
            break
        if r['event'] == 'ConfigInEffect':
            c = cfg(r['config'])
    return c


def journal_at(recs, seq):
    j = {}
    for r in recs:
        if r['seq'] > seq:
            break
        if r['event'] == 'Appended':
            j[r['index']] = (r['epoch'], r['kind'], json.dumps(r.get('payload'), sort_keys=True))
        elif r['event'] == 'Truncated':
            for i in [i for i in j if i >= r['from_index']]:
                del j[i]
    return j


def analyse(byproc, initial):
    out = []
    elected = [(p, r) for p in byproc for r in byproc[p] if r['event'] == 'Elected']
    # J1.1
    byepoch = defaultdict(list)
    for p, r in elected:
        byepoch[r['epoch']].append((p, r))
    for e, lst in byepoch.items():
        for a in range(len(lst)):
            for b in range(a + 1, len(lst)):
                (pa, ra), (pb, rb) = lst[a], lst[b]
                if pa != pb:
                    lab = 'configuration' if cfg(ra['config']) != cfg(rb['config']) else 'mechanics'
                    out.append(('J1.1', lab, f'epoch {e}: {pa}@{ra["seq"]} {cfg(ra["config"])} and {pb}@{rb["seq"]} {cfg(rb["config"])}'))
    # commit decisions
    commits = []
    for p, recs in byproc.items():
        for r in recs:
            if r['event'] != 'Committed':
                continue
            prior = [x for x in recs if x['event'] == 'Elected' and x['seq'] < r['seq']]
            if not prior:
                continue
            j = journal_at(recs, r['seq'])
            if r['index'] not in j:
                continue
            commits.append({'proc': p, 'seq': r['seq'], 'index': r['index'], 'entry': j[r['index']],
                            'epoch': prior[-1]['epoch'], 'config': config_at(recs, r['seq'], initial)})
    # J1.5(a)
    for c in commits:
        for p, r in elected:
            if r['epoch'] > c['epoch']:
                jj = journal_at(byproc[p], r['seq'])
                if jj.get(c['index']) != c['entry']:
                    lab = 'configuration' if c['config'] != cfg(r['config']) else 'mechanics'
                    out.append(('J1.5(a)', lab, f'index {c["index"]} committed by {c["proc"]}@{c["seq"]} in epoch {c["epoch"]} under {c["config"]}; {p}@{r["seq"]} elected in epoch {r["epoch"]} under {cfg(r["config"])} without it'))
    # J1.5(b)
    for p, recs in byproc.items():
        for r in recs:
            if r['event'] != 'Truncated':
                continue
            ci = max([x['index'] for x in recs if x['event'] == 'Committed' and x['seq'] < r['seq']], default=0)
            if r['from_index'] > ci:
                continue
            causes = r.get('causes') or []
            ccfg = None
            if causes:
                cp, cs = causes[0]['proc'], causes[0]['seq']
                ccfg = config_at(byproc.get(cp, []), cs, initial)
            rel = [c['config'] for c in commits if c['index'] >= r['from_index']]
            lab = 'configuration' if ccfg is not None and any(x != ccfg for x in rel) else 'mechanics'
            out.append(('J1.5(b)', lab, f'{p}@{r["seq"]} truncated from {r["from_index"]} at commit index {ci}; truncating coordinator config {ccfg}; commit configs {sorted(set(rel))}'))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('trace')
    ap.add_argument('--initial', required=True, help='comma-separated initial configuration')
    a = ap.parse_args()
    v = analyse(load(a.trace), cfg(a.initial.split(',')))
    for clause, lab, detail in v:
        print(f'{clause} {lab}: {detail}')
    n = sum(1 for x in v if x[1] == 'configuration')
    print(f'SUMMARY {a.trace}: {len(v)} violations, {n} configuration-attributed, {len(v) - n} mechanics-attributed')


if __name__ == '__main__':
    main()
