#!/usr/bin/env python3
# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2, L3, E1
"""Audit all ten repetitions, canonical execution identity and raw provenance."""
from pathlib import Path
from collections import Counter, defaultdict
import copy
import csv
import hashlib
import json
import re
import subprocess

# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2
BASE=Path('impl/evidence-timing')
TAGS='C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2'
CLAUSES=(['C1.1']*3+['C1.2']*3+['C1.3']*3+['C1.4']*3+['C2.1']*3+['C2.2']*3+
         ['C1.1']*2+['C1.2']*2+['C1.3']*2+['C1.4']*2+['C2.1']*2+['C2.2']*2)
manifest=[]
replays=[]
ack_rows=[]
receipt_rows=[]
witness_rows=[]
cells=defaultdict(list)

# derives: C1.4, F1.1, F1.2, F1.3, F2.1, F2.2
for mode in ('all','mutations'):
    for repetition in range(1,11):
        count=0
        log=BASE/'logs'/f'{mode}-{repetition:02d}.txt'
        for line in log.read_text().splitlines():
            if 'schedule=' not in line:continue
            match=re.match(r'(PASS|FAIL \S+|UNEXPLAINED.*?) schedule=(\S+) seed=(\d+).*?trace=(\S+)',line)
            assert match,line
            verdict,schedule,seed,relative=match.groups();seed=int(seed)
            selected=re.search(r' mutation=(\S+)',line)
            mutation=selected.group(1) if selected else 'baseline'
            expected='PASS' if mode=='all' else 'FAIL '+('C1.4' if mutation in ('R1','R2') else CLAUSES[int(mutation[1:])-1])
            assert verdict==expected,line
            path=Path('impl')/relative;meta=path.with_suffix('.meta.json')
            for artifact in (path,meta):
                manifest.append((mode,repetition,schedule,seed,mutation,str(artifact),hashlib.sha256(artifact.read_bytes()).hexdigest()))
            events=[json.loads(x) for x in path.read_text().splitlines()]
            evidence=json.loads(meta.read_text())
            assert evidence['clock']['version']=='timing-v1' and evidence['clock']['seed']==seed
            assert evidence['clock']['logical_ms']>=0
            normalized=[{k:v for k,v in e.items() if k!='run'} for e in events]
            canonical=json.dumps({'events':normalized,'evidence':evidence},sort_keys=True,separators=(',',':')).encode()
            digest=hashlib.sha256(canonical).hexdigest()
            key=(mode,schedule,seed,mutation)
            cells[key].append((repetition,verdict,digest))
            replays.append((mode,repetition,schedule,seed,mutation,verdict,digest,str(path)))
            by_ref={(e['proc'],e['seq']):e for e in events}
            assert len(by_ref)==len(events)
            ref=lambda r:(r['proc'],r['seq'])
            # Independent send-state reconstruction from clock-free Fault records.
            ids=['n1','n2','n3','c1','c2','s']
            state={'up':dict.fromkeys(ids,True),'gen':dict.fromkeys(ids,1),'down':set(),'paused':set()}
            states={('',0):copy.deepcopy(state)}
            for fault in sorted((e for e in events if e['event']=='Fault'),key=lambda e:e['seq']):
                if fault.get('crash'):
                    p=fault['crash'];state['up'][p]=False;state['paused'].discard(p)
                    if p.startswith('c'):state['gen'][p]+=1
                if fault.get('restart'):
                    p=fault['restart'];state['up'][p]=True
                    if p.startswith('n'):state['gen'][p]+=1
                if fault.get('partition'):
                    for a in fault['partition'][0]:
                        for b in fault['partition'][1]:state['down'].update(((a,b),(b,a)))
                state['down'].update(tuple(p) for p in fault.get('links',[]))
                if fault.get('heal'):assert fault['links']==[];state['down'].clear()
                if fault.get('pause'):state['paused'].add(fault['pause'])
                if fault.get('resume'):state['paused'].discard(fault['resume'])
                states[ref(fault)]=copy.deepcopy(state)
            completed=set()
            for delivery in evidence.get('grant_deliveries',[]):
                request,grant=by_ref[ref(delivery['request'])],by_ref[ref(delivery['grant'])]
                assert request['event']=='Request' and grant['event']=='Grant'
                assert request['client']==grant['client'] and delivery['request'] in grant['causes']
                assert ref(request) not in completed;completed.add(ref(request))
                at_receipt=states[ref(delivery['received_after'])];client=request['client']
                assert at_receipt['up'][client] and client not in at_receipt['paused']
                assert at_receipt['gen'][client]==delivery['client_generation']
                for field,start,end in [('request_hops',client,grant['proc']),('reply_hops',grant['proc'],client)]:
                    hops=delivery[field];assert hops and hops[0]['from']==start and hops[-1]['to']==end
                    for i,hop in enumerate(hops):
                        st=states[ref(hop['fault'])];a,b=hop['from'],hop['to']
                        assert a!=b and st['up'][a] and st['up'][b] and (a,b) not in st['down']
                        assert st['gen'][a]==hop['from_generation'] and st['gen'][b]==hop['to_generation']
                        assert hop['fault']['seq']<=delivery['received_after']['seq']
                        if i:
                            previous=hops[i-1]
                            assert previous['to']==a and a.startswith('n')
                            assert previous['to_generation']==hop['from_generation']
                            assert previous['fault']['seq']<=hop['fault']['seq']
                receipt_rows.append((mode,repetition,schedule,seed,mutation,f"{request['proc']}:{request['seq']}",f"{grant['proc']}:{grant['seq']}",grant['token']))
            wrong_reads=[]
            for event in events:
                if event['event'] not in ('WriteAck','ReadAck'):continue
                answer=by_ref[ref(event['answers'])]
                assert answer['event']==('WriteAttempt' if event['event']=='WriteAck' else 'ReadAttempt')
                assert all(event.get(k)==answer.get(k) for k in ('client','key','token'))
                pending=[ref(r) for r in event['causes']];past=set()
                while pending:
                    r=pending.pop()
                    if r in past:continue
                    past.add(r);pending.extend(ref(x) for x in by_ref[r]['causes'])
                assert ref(answer) in past
                for parent in event['causes']:
                    decision=by_ref[ref(parent)]
                    if decision['event'] in ('WriteAccept','WriteReject','ReadAccept','ReadReject'):
                        attempts=[by_ref[ref(r)] for r in decision['causes'] if by_ref[ref(r)]['event'] in ('WriteAttempt','ReadAttempt')]
                        assert len(attempts)==1 and ref(attempts[0])==ref(answer)
                        if event['event']=='ReadAck' and event['outcome']=='served' and decision['event']=='ReadAccept' and event['value']!=decision['value']:
                            wrong_reads.append((event,decision))
                ack_rows.append((mode,repetition,schedule,seed,mutation,event['event'],f"{event['proc']}:{event['seq']}",f"{answer['proc']}:{answer['seq']}"))
            if mode=='all':
                assert evidence['schedule_completed']
                assert {ref(e) for e in events if e['event']=='Request'}==completed
                if schedule=='P18':
                    assert any(e.get('pause')=='c1' for e in events) and any(e.get('resume')=='c1' for e in events)
                    assert not wrong_reads
                    witness_rows.append((mode,repetition,schedule,seed,mutation,'valid-pause-and-original-snapshot'))
                if schedule in ('P29','P30'):
                    assert not any(e['event']=='ReadAck' and e['client']=='c1' for e in events)
                    assert any(e['event']=='ReadAck' and e['client']=='c2' and e['outcome']=='served' for e in events)
                    witness_rows.append((mode,repetition,schedule,seed,mutation,'lost-c1-reply-and-served-c2-after-heal'))
                if schedule=='H8':
                    issued=[e for e in events if e['event']=='Grant' and e['client']=='c2'];assert len(issued)>=2
                    lost=issued[0]
                    received=[d for d in evidence['grant_deliveries'] if by_ref[ref(d['request'])]['client']=='c2']
                    assert len(received)==1
                    actual=by_ref[ref(received[0]['grant'])]
                    assert actual['token']>lost['token'] and actual['proc']!=lost['proc']
                    witness_rows.append((mode,repetition,schedule,seed,mutation,'lost-issuance-and-higher-token-recovery'))
                if schedule=='H9':
                    d=next(d for d in evidence['grant_deliveries'] if by_ref[ref(d['request'])]['client']=='c2')
                    assert len(d['request_hops'])>=2 and len(d['reply_hops'])>=2
                    witness_rows.append((mode,repetition,schedule,seed,mutation,'request-and-reply-relayed'))
            elif mutation in ('P18','P29','P30'):
                assert wrong_reads,(path,'mutation did not actually corrupt an accepted snapshot')
                witness_rows.append((mode,repetition,schedule,seed,mutation,'actual-ack-value-differs-from-served-snapshot'))
            elif mutation in ('R1','R2'):
                grants=[e for e in events if e['event']=='Grant' and e['client']=='c2']
                assert (len(grants)>0 if mutation=='R2' else not grants)
                assert not any(by_ref[ref(d['request'])]['client']=='c2' for d in evidence.get('grant_deliveries',[]))
                assert evidence['progress_horizons']
                witness_rows.append((mode,repetition,schedule,seed,mutation,'qualified-pending-request-not-received'))
            count+=1
        assert count==(105 if mode=='all' else 96),(mode,repetition,count)

# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2
assert len(cells)==201
counts=[]
for key,values in sorted(cells.items()):
    assert len(values)==10 and {v[0] for v in values}==set(range(1,11)),key
    outcomes=Counter(v[1] for v in values);hashes={v[2] for v in values}
    assert len(outcomes)==1,(key,'FLAKY VERDICTS',outcomes)
    assert len(hashes)==1,(key,'DIVERGENT EXECUTION',hashes)
    verdict=next(iter(outcomes))
    counts.append((*key,verdict,outcomes[verdict],len(outcomes),len(hashes),next(iter(hashes))))

# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2
for name,header,rows in [
 ('manifest.tsv','mode repetition schedule seed mutation path sha256',manifest),
 ('replay-hashes.tsv','mode repetition schedule seed mutation verdict canonical_sha256 trace',replays),
 ('cell-counts.tsv','mode schedule seed mutation verdict count distinct_verdicts distinct_executions canonical_sha256',counts),
 ('ack-answers.tsv','mode repetition schedule seed mutation event ack answers',ack_rows),
 ('grant-deliveries.tsv','mode repetition schedule seed mutation request grant token',receipt_rows),
 ('mechanism-witnesses.tsv','mode repetition schedule seed mutation witness',witness_rows),
]:
    with (BASE/name).open('w') as f:
        f.write('# derives: '+TAGS+'\n'+header.replace(' ','\t')+'\n')
        for row in rows:f.write('\t'.join(map(str,row))+'\n')

# Verify all allowed shared inputs are untouched and bind source/version evidence.
# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2
inputs=[Path(x) for x in ['AGENTS.md','docs/briefs/fix-timing-impl.md','contract/v2.md','failure-model/v2.md','tests/pairs-v3.md','testbed/schedule-format.md','observe/schema.md']]+sorted(Path('testbed/schedules').glob('*.yaml'))
assert len(inputs)==42
with (BASE/'shared-inputs.tsv').open('w') as f:
    f.write('# derives: '+TAGS+'\npath\tsha256\tunchanged_from_HEAD\n')
    for path in inputs:
        current=path.read_bytes();committed=subprocess.check_output(['git','show','HEAD:'+str(path)])
        assert current==committed,path
        f.write(f'{path}\t{hashlib.sha256(current).hexdigest()}\ttrue\n')
with (BASE/'source-sha256.tsv').open('w') as f:
    f.write('# derives: '+TAGS+'\npath\tsha256\n')
    for path in sorted(Path('impl').glob('*.go'))+[Path('impl/go.mod'),Path('impl/go.sum'),Path('impl/run.sh')]:
        f.write(f'{path}\t{hashlib.sha256(path.read_bytes()).hexdigest()}\n')
print(f'AUDIT PASS runs={len(replays)} cells={len(cells)} flaky_cells=0 divergent_execution_cells=0 files={len(manifest)} grant_receipts={len(receipt_rows)} acks={len(ack_rows)} shared_inputs={len(inputs)}')
