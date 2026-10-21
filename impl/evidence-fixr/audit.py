#!/usr/bin/env python3
# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2, L3
"""Audit FixR receipts, identities, directed hop evidence and shared-input hashes."""
from pathlib import Path
import copy
import csv
import hashlib
import json
import re
import subprocess

# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2
BASE=Path('impl/evidence-fixr')
TAGS='C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2'
CLAUSES=(['C1.1']*3+['C1.2']*3+['C1.3']*3+['C1.4']*3+['C2.1']*3+['C2.2']*3+
         ['C1.1']*2+['C1.2']*2+['C1.3']*2+['C1.4']*2+['C2.1']*2+['C2.2']*2)
manifest=[]
results=[]
deliveries=[]
acks=[]
holdouts=[]
mutation_witnesses=[]
prediction_misses=[]

# derives: C1.4, F1.1, F1.2, F1.3, F2.1, F2.2
for mode in ('all-initial','mutations-initial','all','mutations'):
    count=0
    for line in (BASE/'logs'/f'{mode}.txt').read_text().splitlines():
        if 'schedule=' not in line: continue
        match=re.match(r'(PASS|FAIL \S+|UNEXPLAINED.*?) schedule=(\S+) seed=(\d+).*?trace=(\S+)',line)
        assert match,line
        verdict,schedule,seed,relative=match.groups();seed=int(seed)
        mutation_match=re.search(r' mutation=(\S+)',line)
        mutation=mutation_match.group(1) if mutation_match else ''
        expected='PASS' if not mutation else 'FAIL '+('C1.4' if mutation in ('R1','R2') else CLAUSES[int(mutation[1:])-1])
        if verdict!=expected:prediction_misses.append((mode,schedule,mutation or "baseline",seed,expected,verdict))
        key=(mode,schedule,mutation,seed)
        assert not any(r[:4]==key for r in results),key
        results.append((*key,verdict))
        path=Path('impl')/relative;meta=path.with_suffix('.meta.json')
        for artifact in (path,meta):
            manifest.append((mode,schedule,mutation or 'baseline',seed,str(artifact),hashlib.sha256(artifact.read_bytes()).hexdigest()))
        events=[json.loads(x) for x in path.read_text().splitlines()]
        evidence=json.loads(meta.read_text())
        by_ref={(e['proc'],e['seq']):e for e in events}
        assert len(by_ref)==len(events)
        reference=lambda r:(r['proc'],r['seq'])
        # Reconstruct each state at an env Fault, independently of the Go checker.
        ids=['n1','n2','n3','c1','c2','s']
        state={'up':dict.fromkeys(ids,True),'gen':dict.fromkeys(ids,1),'down':set(),'paused':set()}
        states={('',0):copy.deepcopy(state)}
        for e in sorted((e for e in events if e['event']=='Fault'),key=lambda e:e['seq']):
            if e.get('crash'):
                proc=e['crash'];state['up'][proc]=False;state['paused'].discard(proc)
                if proc.startswith('c'):state['gen'][proc]+=1
            if e.get('restart'):
                proc=e['restart'];state['up'][proc]=True
                if proc.startswith('n'):state['gen'][proc]+=1
            if e.get('partition'):
                for a in e['partition'][0]:
                    for b in e['partition'][1]:state['down'].update(((a,b),(b,a)))
            state['down'].update(tuple(p) for p in e.get('links',[]))
            if e.get('heal'):
                assert e['links']==[]
                state['down'].clear()
            if e.get('pause'):state['paused'].add(e['pause'])
            if e.get('resume'):state['paused'].discard(e['resume'])
            states[reference(e)]=copy.deepcopy(state)
        seen=set()
        for d in evidence.get('grant_deliveries',[]):
            request,grant=by_ref[reference(d['request'])],by_ref[reference(d['grant'])]
            assert request['event']=='Request' and grant['event']=='Grant'
            assert request['client']==grant['client'] and reference(request) not in seen
            assert d['request'] in grant['causes']
            seen.add(reference(request))
            at_receipt=states[reference(d['received_after'])]
            client=request['client']
            assert at_receipt['up'][client] and client not in at_receipt['paused']
            assert at_receipt['gen'][client]==d['client_generation']
            for field,start,end in [('request_hops',client,grant['proc']),('reply_hops',grant['proc'],client)]:
                hops=d[field];assert hops and hops[0]['from']==start and hops[-1]['to']==end
                for i,h in enumerate(hops):
                    st=states[reference(h['fault'])];a,b=h['from'],h['to']
                    assert a!=b and st['up'][a] and st['up'][b] and (a,b) not in st['down']
                    assert st['gen'][a]==h['from_generation'] and st['gen'][b]==h['to_generation']
                    assert h['fault']['seq']<=d['received_after']['seq']
                    if i:
                        prev=hops[i-1]
                        assert prev['to']==a and a.startswith('n')
                        assert prev['to_generation']==h['from_generation']
                        assert prev['fault']['seq']<=h['fault']['seq']
            deliveries.append((mode,schedule,mutation or 'baseline',seed,
                               f"{request['proc']}:{request['seq']}",f"{grant['proc']}:{grant['seq']}",grant['token'],
                               '>'.join([d['request_hops'][0]['from']]+[h['to'] for h in d['request_hops']]),
                               '>'.join([d['reply_hops'][0]['from']]+[h['to'] for h in d['reply_hops']])))
        for e in events:
            if e['event'] not in ('WriteAck','ReadAck'):continue
            answer=by_ref[reference(e['answers'])]
            assert answer['event']==('WriteAttempt' if e['event']=='WriteAck' else 'ReadAttempt')
            assert all(e.get(f)==answer.get(f) for f in ('client','key','token'))
            stack=[reference(r) for r in e['causes']];past=set()
            while stack:
                r=stack.pop()
                if r in past:continue
                past.add(r);stack.extend(reference(x) for x in by_ref[r]['causes'])
            assert reference(answer) in past
            for r in e['causes']:
                decision=by_ref[reference(r)]
                if decision['event'] in ('WriteAccept','WriteReject','ReadAccept','ReadReject'):
                    attempts=[by_ref[reference(x)] for x in decision['causes'] if by_ref[reference(x)]['event'] in ('ReadAttempt','WriteAttempt')]
                    assert len(attempts)==1 and reference(attempts[0])==reference(answer)
            acks.append((mode,schedule,mutation or 'baseline',seed,e['event'],f"{e['proc']}:{e['seq']}",f"{answer['proc']}:{answer['seq']}"))
        if mode.startswith('all'):
            assert evidence['schedule_completed'] if verdict=='PASS' else not evidence['schedule_completed']
            requests={reference(e) for e in events if e['event']=='Request'}
            assert requests==seen,(path,'missing delivery certificate')
            if schedule=='H8':
                issued=[e for e in events if e['event']=='Grant' and e['client']=='c2']
                assert len(issued)>=2
                lost=issued[0]
                receipt=next(d for d in evidence['grant_deliveries'] if d['request']==next(r for r in lost['causes'] if by_ref[reference(r)]['event']=='Request'))
                actual=by_ref[reference(receipt['grant'])]
                assert receipt['grant']!={'proc':lost['proc'],'seq':lost['seq']} and actual['token']>lost['token']
                assert any(e.get('crash')==lost['proc'] for e in events)
                assert any(e['event']=='WriteAttempt' and e['client']=='c2' and e['token']==actual['token'] for e in events)
                holdouts.append((mode,schedule,seed,'lost_issued_token',lost['token'],'recovered_token',actual['token']))
            if schedule=='H9':
                receipt=next(d for d in evidence['grant_deliveries'] if by_ref[reference(d['request'])]['client']=='c2')
                assert len(receipt['request_hops'])>=2 and len(receipt['reply_hops'])>=2
                holdouts.append((mode,schedule,seed,'request_hops',len(receipt['request_hops']),'reply_hops',len(receipt['reply_hops'])))
            if schedule=='H7':
                first=next(e for e in events if e['event']=='Grant' and e['client']=='c1')
                reads=[e for e in events if e['event']=='ReadAccept']
                assert reads[0]['highest_before']==first['token']
                accepted=[e for e in events if e['event']=='WriteAccept']
                old_writes=[e for e in accepted if e['token']==first['token']]
                assert len(old_writes)>=2 and old_writes[-1]['highest_before']==first['token']
                final=next(e for e in reversed(events) if e['event']=='ReadAck' and e['client']=='c2')
                assert final['value']=='v3' and final['outcome']=='served'
                holdouts.append((mode,schedule,seed,'read_fence',reads[0]['highest_before'],'final_read',final['value']))
            if schedule=='H10':
                first=next(e for e in events if e['event']=='Grant' and e['client']=='c1')
                later=next(e for e in events if e['event']=='Grant' and e['client']=='c2')
                assert later['token']>first['token']
                assert any(e['event']=='WriteAck' and e['client']=='c2' and e['outcome']=='accepted' for e in events)
                holdouts.append((mode,schedule,seed,'first_token',first['token'],'later_token',later['token']))
        if mutation in ('R1','R2'):
            grants=[e for e in events if e['event']=='Grant' and e['client']=='c2']
            assert not any(by_ref[reference(d['request'])]['client']=='c2' for d in evidence.get('grant_deliveries',[]))
            assert evidence['progress_horizons'] and not evidence['schedule_completed']
            assert len(grants)>0 if mutation=='R2' else len(grants)==0
            mutation_witnesses.append((mode,mutation,schedule,seed,len(grants),0,evidence['progress_horizons'][0]['budget_ms']))
        count+=1
    assert count==(105 if mode.startswith('all') else 96),(mode,count)

# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2
for filename,header,rows in [
 ('prediction-misses.tsv','mode schedule mutation seed expected actual',prediction_misses),
 ('manifest.tsv','mode schedule mutation seed path sha256',manifest),
 ('per-seed.tsv','mode schedule mutation seed verdict',results),
 ('grant-deliveries.tsv','mode schedule mutation seed request grant token request_route reply_route',deliveries),
 ('ack-answers.tsv','mode schedule mutation seed event ack answers',acks),
 ('holdout-witnesses.tsv','mode schedule seed kind1 value1 kind2 value2',holdouts),
 ('routing-mutations.tsv','mode mutation schedule seed c2_issued_grants c2_delivered_grants budget_ms',mutation_witnesses),
]:
    with (BASE/filename).open('w') as f:
        f.write('# derives: '+TAGS+'\n'+header.replace(' ','\t')+'\n')
        for row in rows:f.write('\t'.join(map(str,row))+'\n')

# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2
inputs=[Path(x) for x in ['AGENTS.md','docs/briefs/fix-x2-routing.md','contract/v2.md','failure-model/v2.md','tests/pairs-v3.md','testbed/schedule-format.md','observe/schema.md']]+sorted(Path('testbed/schedules').glob('*.yaml'))
assert len(inputs)==42
with (BASE/'shared-inputs.tsv').open('w') as f:
    f.write('# derives: '+TAGS+'\npath\tsha256\tunchanged_from_HEAD\n')
    for path in inputs:
        current=path.read_bytes();committed=subprocess.check_output(['git','show','HEAD:'+str(path)])
        assert current==committed,path
        f.write(f'{path}\t{hashlib.sha256(current).hexdigest()}\ttrue\n')
print(f'AUDIT PASS runs={len(results)} files={len(manifest)} grant_receipts={len(deliveries)} acks={len(acks)} shared_inputs={len(inputs)} prediction_misses={len(prediction_misses)}')
