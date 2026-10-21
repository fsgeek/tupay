#!/usr/bin/env python3
# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2, L1, L2, L3
"""Audit retained X2 receipts and raw records; run from repository root."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2
BASE = Path('impl/evidence-x2')
TAGS = 'C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2'

# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F2.1, F2.2
clauses = (['C1.1']*3 + ['C1.2']*3 + ['C1.3']*3 + ['C1.4']*3
           + ['C2.1']*3 + ['C2.2']*3 + ['C1.1']*2 + ['C1.2']*2
           + ['C1.3']*2 + ['C1.4']*2 + ['C2.1']*2 + ['C2.2']*2)

# derives: C1.1, C1.3, C2.2, F2.1, F2.2
manifest = []
acks = []
faults = []
progress = []
p17_replies = []
results = {}
run_counts = {}

# derives: C1.1, C1.3, C2.2, F2.1, F2.2
for receipt in ['all-initial', 'all', 'mutations']:
    lines = (BASE/'logs'/f'{receipt}.txt').read_text().splitlines()
    count = 0
    for line in lines:
        if 'schedule=' not in line:
            continue
        match = re.match(r'(PASS|FAIL [A-Z0-9.]+|UNEXPLAINED.*?) schedule=(\S+) seed=(\d+).*?trace=(\S+)', line)
        assert match, line
        verdict, schedule, seed, relative = match.groups()
        seed = int(seed)
        assert seed in (1, 2, 3)
        if receipt != 'mutations':
            assert verdict == 'PASS', line
        else:
            expected = clauses[int(schedule[1:])-1]
            assert verdict == 'FAIL '+expected, line
        assert (receipt, schedule, seed) not in results
        results[receipt, schedule, seed] = verdict
        path = Path('impl')/relative
        meta = path.with_suffix('.meta.json')
        for artifact in (path, meta):
            manifest.append((receipt, schedule, seed, str(artifact), hashlib.sha256(artifact.read_bytes()).hexdigest()))
        events = [json.loads(row) for row in path.read_text().splitlines()]
        evidence = json.loads(meta.read_text())
        if receipt != 'mutations':
            assert evidence['schedule_completed'], path
        by_ref = {(e['proc'], e['seq']): e for e in events}
        assert len(by_ref) == len(events)
        first_grant = next(e for e in events if e['event'] == 'Grant')
        old_grantor, old_holder = first_grant['proc'], first_grant['client']
        # Raw fault expectations are written directly from the shared inputs,
        # independently of the implementation's compiler/expansion helpers.
        for e in events:
            if e['event'] == 'Fault':
                if e.get('heal'):
                    assert e.get('links') == [], (path, e)
                if e.get('cell') in ('F2.1', 'F2.2') and not e.get('heal'):
                    links = [tuple(p) for p in e['links']]
                    assert len(set(links)) == len(links) and all(a != b for a, b in links)
                    num = int(schedule[1:])
                    followers = [n for n in ['n1', 'n2', 'n3'] if n != old_grantor]
                    expected = set()
                    if num in (19, 25):
                        expected = {(old_grantor, min(followers)), (min(followers), old_grantor)}
                    elif num in (20, 26):
                        expected = {(n, old_grantor) for n in followers}
                    elif num in (21, 27):
                        expected = {(a, b) for n in followers for a, b in [(old_grantor, n), (n, old_grantor)]}
                    elif num in (22, 28):
                        expected = {(n, old_holder) for n in ['n1', 'n2', 'n3']}
                    elif num in (23, 29):
                        expected = {(old_holder, 's'), ('s', old_holder)}
                    elif num in (24, 30):
                        expected = {('s', old_holder)}
                    assert set(links) == expected, (path, e, expected)
                    faults.append((receipt, schedule, seed, e['cell'], json.dumps(e['links'], separators=(',', ':'))))
            if e['event'] not in ('WriteAck', 'ReadAck'):
                continue
            answer = e['answers']
            ref = answer['proc'], answer['seq']
            attempt = by_ref[ref]
            assert attempt['event'] == ('WriteAttempt' if e['event'] == 'WriteAck' else 'ReadAttempt')
            assert all(e.get(k) == attempt.get(k) for k in ('client', 'key', 'token'))
            pending = [(x['proc'], x['seq']) for x in e['causes']]
            seen = set()
            while pending:
                r = pending.pop()
                if r in seen:
                    continue
                seen.add(r)
                pending.extend((x['proc'], x['seq']) for x in by_ref[r]['causes'])
            assert ref in seen
            decisions = [by_ref[x['proc'], x['seq']] for x in e['causes']
                         if by_ref[x['proc'], x['seq']]['event'] in ('WriteAccept','WriteReject','ReadAccept','ReadReject')]
            for d in decisions:
                original = [by_ref[x['proc'], x['seq']] for x in d['causes']
                            if by_ref[x['proc'], x['seq']]['event'] in ('WriteAttempt','ReadAttempt')]
                assert len(original) == 1 and (original[0]['proc'], original[0]['seq']) == ref
            acks.append((receipt, schedule, seed, e['event'], f"{e['proc']}:{e['seq']}", f'{ref[0]}:{ref[1]}'))
        if receipt != 'mutations' and schedule in ('P23','P24'):
            assert not any(e['event']=='WriteAck' and e['client']==old_holder for e in events)
        if receipt != 'mutations' and schedule in ('P29','P30'):
            assert not any(e['event']=='ReadAck' and e['client']==old_holder for e in events)
            assert any(e['event']=='ReadAck' and e['client']=='c2' and e['outcome']=='served' for e in events)
        if receipt != 'mutations' and schedule == 'P17':
            attempts = [e for e in events if e['event']=='ReadAttempt']
            original = attempts[0]
            original_ref = (original['proc'], original['seq'])
            late = [e for e in events if e['event']=='ReadAck' and
                    (e['answers']['proc'],e['answers']['seq'])==original_ref]
            healed = next(e for e in events if e.get('heal'))
            heal_ref = (healed['proc'],healed['seq'])
            for ack in late:
                stack = [(x['proc'],x['seq']) for x in ack['causes']]
                past = set()
                while stack:
                    ref = stack.pop()
                    if ref in past: continue
                    past.add(ref)
                    stack += [(x['proc'],x['seq']) for x in by_ref[ref]['causes']]
                assert heal_ref in past, (path, ack)
            lost = attempts[1]
            lost_ref = (lost['proc'],lost['seq'])
            assert not any(e['event']=='ReadAccept' and
                           any((r['proc'],r['seq'])==lost_ref for r in e['causes']) for e in events)
            p17_replies.append((receipt,seed,f'{original_ref[0]}:{original_ref[1]}',len(late),'true','true'))
        if schedule in ('P25','P26'):
            grants = [e for e in events if e['event']=='Grant' and e['client']=='c2']
            progress.append((receipt, schedule, seed, old_grantor,
                             ','.join(e['proc']+':'+str(e['grantor_term'])+':'+str(e['token']) for e in grants) or 'none',
                             len(evidence.get('progress_horizons') or [])))
        count += 1
    assert count == (90 if receipt == 'mutations' else 93), (receipt, count)
    run_counts[receipt] = count

# derives: C1.1, C1.3, C1.4, C2.2, F2.1, F2.2
for name, header, rows in [
    ('p17-replies.tsv', 'receipt\tseed\tfirst_attempt\tfirst_attempt_acks\theal_precedes_ack\tsecond_attempt_lost', p17_replies),
    ('manifest.tsv', 'receipt\tschedule\tseed\tpath\tsha256', manifest),
    ('ack-answers.tsv', 'receipt\tschedule\tseed\tevent\tack\tanswers', acks),
    ('fault-links.tsv', 'receipt\tschedule\tseed\tcell\tlinks', faults),
    ('progress.tsv', 'receipt\tschedule\tseed\tfirst_grantor\tc2_grantor:term:token\thorizons', progress),
]:
    with (BASE/name).open('w') as f:
        f.write('# derives: '+TAGS+'\n'+header+'\n')
        for row in rows:
            f.write('\t'.join(map(str, row))+'\n')

# Verify allowed shared inputs are byte-identical to their committed contents.
# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2
inputs = [Path(x) for x in ['AGENTS.md','docs/briefs/x2-adapt-impl.md','contract/v2.md','failure-model/v2.md','tests/pairs-v3.md','testbed/schedule-format.md','observe/schema.md']]
inputs += sorted(Path('testbed/schedules').glob('*.yaml'))
assert len(inputs) == 38
with (BASE/'shared-inputs.tsv').open('w') as f:
    f.write('# derives: '+TAGS+'\npath\tsha256\tunchanged_from_HEAD\n')
    for path in inputs:
        current = path.read_bytes()
        committed = subprocess.check_output(['git','show','HEAD:'+str(path)])
        assert current == committed, path
        f.write(f'{path}\t{hashlib.sha256(current).hexdigest()}\ttrue\n')

# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F2.1, F2.2
with (BASE/'per-seed.tsv').open('w') as f:
    f.write('# derives: '+TAGS+'\nschedule\tseed\tbaseline\tmutation\n')
    for schedule in [f'P{i}' for i in range(1,31)]+['false-suspicion-v1']:
        for seed in (1,2,3):
            f.write(f"{schedule}\t{seed}\t{results['all',schedule,seed]}\t{results.get(('mutations',schedule,seed),'—')}\n")
print(f'AUDIT PASS runs={run_counts} files={len(manifest)} acks={len(acks)} link_faults={len(faults)} shared_inputs={len(inputs)}')
