#!/usr/bin/python3
"""Scenario driver for the reference model tla/F.tla (validation tool, not an experimental artifact).

derives: J1.1, J1.3, J1.4, G1.1, G1.2, G1.3, G1.4

Compiles a scenario (replay/scenario-format.md) into a TLC model of spec F (SPEC or GATED variant),
runs TLC under the mandatory memory cap, and reports PASS, FAIL <clause> (with a short trace),
UNEXPLAINED steps or UNEXPLAINED bound.

Two TLC runs per scenario and variant:
  reach : invariant NotDone. A violation is a behaviour that takes every step (shortest, BFS).
          No violation over the whole bounded space => UNEXPLAINED steps.
  safety: invariants Done => J1.1 / J1.3 / J1.4(a) / J1.4(b). A violation => FAIL <clause>.
          Exhausted with none => PASS (within the stated bounds). Wall-clock limit hit => UNEXPLAINED bound.
  any   : (optional, diagnostic) the clauses without the Done guard.

usage: run.py SCENARIO.yaml SPEC|GATED [--maxe 3] [--maxt 3] [--maxj N] [--settle 4]
              [--modes reach,safety] [--workers 32] [--limit 600] [--json out.json]
"""
import argparse, json, os, re, subprocess, sys, time

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
TLA = os.path.join(HERE, 'tla')
JAR = os.path.expanduser('~/projects/tlaplus/tla2tools.jar')
CAP = ['systemd-run', '--user', '--scope', '-q', '-p', 'MemoryMax=24G', '-p', 'MemorySwapMax=0']
MEMBERS = ['m1', 'm2', 'm3', 'm4', 'm5']
SELECTORS = ('coordinator', 'follower', 'crashed')


# ------------------------------------------------------------------ scenario compilation
def q(s):
    return '"%s"' % s


def tla_val(v):
    if isinstance(v, bool):
        return 'TRUE' if v else 'FALSE'
    if isinstance(v, int):
        return str(v)
    return q(str(v))


def trig_tla(at):
    if at == 'start' or at == {'event': 'start'}:
        return '[event |-> "start"]'
    if not isinstance(at, dict) or 'event' not in at:
        raise SystemExit('scenario rejected: bad trigger %r' % (at,))
    return '[' + ', '.join('%s |-> %s' % (k, tla_val(v)) for k, v in at.items()) + ']'


def name(x):
    if x in MEMBERS or x in SELECTORS:
        return x
    raise SystemExit('scenario rejected: unknown member %r' % (x,))


def act_tla(do):
    op = t = at = None
    links, cmd = [], ''
    if 'add' in do or 'remove' in do:
        op = 'add' if 'add' in do else 'remove'
        t, at = name(do[op]), name(do['at'])
    elif 'command' in do:
        op, cmd, at = 'command', str(do['command']), name(do['at'])
    elif 'crash' in do or 'restart' in do:
        op = 'crash' if 'crash' in do else 'restart'
        t = name(do[op])
    elif 'cut' in do or 'drop' in do:
        op = 'cut' if 'cut' in do else 'drop'
        links = [(name(a), name(b)) for a, b in do[op]]
    elif 'heal' in do:
        op = 'heal'
    else:
        raise SystemExit('scenario rejected: unknown action %r' % (do,))
    return '[op |-> %s, t |-> %s, at |-> %s, cmd |-> %s, links |-> {%s}]' % (
        q(op), q(t or 'none'), q(at or 'none'), q(cmd), ', '.join('<<%s, %s>>' % (q(a), q(b)) for a, b in links))


def load(path):
    with open(path) as f:
        d = yaml.safe_load(f)
    crashed_ok = False
    for s in d['steps']:
        if 'crashed' in json.dumps(s['do']) and not crashed_ok:
            raise SystemExit('scenario rejected: crashed selector before any crash step')
        if 'crash' in s['do']:
            crashed_ok = True
    return d


def needed_journal(d, gated):
    """A journal-length bound that admits every step: entries the steps themselves append,
    plus (GATED) one no-op per election the steps need, plus one spare election."""
    n = sum(1 for s in d['steps'] if any(k in s['do'] for k in ('command', 'add', 'remove')))
    elections = 1 + sum(1 for s in d['steps'] if s['at'] != 'start' and s['at'].get('event') == 'Elected')
    return n + (elections if gated else 0)


def compile_model(d, variant, b, mode, workdir):
    mod = 'MC'
    steps = ' ,\n    '.join('[at |-> %s, act |-> %s]' % (trig_tla(s['at']), act_tla(s['do'])) for s in d['steps'])
    tla = '---- MODULE %s ----\nEXTENDS F\n' % mod
    tla += 'MCSteps == <<\n    %s >>\n' % steps
    tla += 'MCInit == {%s}\n' % ', '.join(q(x) for x in d['initial'])
    tla += 'MCGated == %s\nMCMaxE == %d\nMCMaxT == %d\nMCMaxJ == %d\nMCSettle == %d\n' % (
        'TRUE' if variant == 'GATED' else 'FALSE', b['maxe'], b['maxt'], b['maxj'], b['settle'])
    tla += 'MCDepth == %s\n====\n' % ('TRUE' if not b.get('depth') else 'TLCGet("level") <= %d' % b['depth'])
    inv = {'reach': ['NotDone'],
           'safety': ['InvJ11', 'InvJ13', 'InvJ14a', 'InvJ14b'],
           'any': ['AnyJ11', 'AnyJ13', 'AnyJ14a', 'AnyJ14b']}[mode]
    cfg = ('CONSTANTS\n  Steps <- MCSteps\n  Init0 <- MCInit\n  Gated <- MCGated\n  MaxE <- MCMaxE\n'
           '  MaxT <- MCMaxT\n  MaxJ <- MCMaxJ\n  Settle <- MCSettle\nSPECIFICATION Spec\n'
           'INVARIANTS %s\nCONSTRAINT MCDepth\nCHECK_DEADLOCK FALSE\n' % ' '.join(inv))
    os.makedirs(workdir, exist_ok=True)
    with open(os.path.join(workdir, mod + '.tla'), 'w') as f:
        f.write(tla)
    with open(os.path.join(workdir, mod + '.cfg'), 'w') as f:
        f.write(cfg)
    src = os.path.join(TLA, 'F.tla')
    with open(src) as f, open(os.path.join(workdir, 'F.tla'), 'w') as g:
        g.write(f.read())
    return mod


def run_tlc(workdir, mod, workers, limit):
    cmd = CAP + ['/usr/bin/time', '-v', 'timeout', str(limit),
                 'java', '-Xmx10g', '-Xss16m', '-XX:MaxDirectMemorySize=6g', '-XX:+UseParallelGC',
                 '-cp', JAR, 'tlc2.TLC', '-workers', str(workers), '-fpmem', '0.04',
                 '-metadir', os.path.join(workdir, 'states'), '-cleanup', '-nowarning',
                 '-config', mod + '.cfg', mod + '.tla']
    t0 = time.time()
    p = subprocess.run(cmd, cwd=workdir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    dt = time.time() - t0
    out = p.stdout
    with open(os.path.join(workdir, 'tlc.out'), 'w') as f:
        f.write(out)
    m = re.search(r'Maximum resident set size \(kbytes\): (\d+)', out)
    rss = int(m.group(1)) if m else None
    return out, p.returncode, dt, rss


# ------------------------------------------------------------------ TLA+ value parser (TLC output)
TOK = re.compile(r'\s*(<<|>>|\|->|:>|@@|\.\.|[\[\]{}(),]|"(?:[^"\\]|\\.)*"|-?\d+|[A-Za-z_][A-Za-z0-9_]*)')


def tokenize(s):
    pos, out = 0, []
    s = s.strip()
    while pos < len(s):
        m = TOK.match(s, pos)
        if not m:
            raise ValueError('cannot tokenize at %r' % s[pos:pos + 40])
        out.append(m.group(1))
        pos = m.end()
    return out


class P:
    def __init__(self, toks):
        self.t, self.i = toks, 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def eat(self, x=None):
        tok = self.t[self.i]
        if x is not None and tok != x:
            raise ValueError('expected %s got %s' % (x, tok))
        self.i += 1
        return tok

    def value(self):
        v = self.atom()
        if self.peek() == ':>':          # function  a :> b @@ c :> d
            fn = {}
            while True:
                self.eat(':>')
                fn[v] = self.atom()
                if self.peek() == '@@':
                    self.eat('@@')
                    v = self.atom()
                else:
                    break
            return fn
        return v

    def atom(self):
        tok = self.eat()
        if tok == '(':
            v = self.value()
            self.eat(')')
            return v
        if tok == '<<':
            items = []
            while self.peek() != '>>':
                items.append(self.value())
                if self.peek() == ',':
                    self.eat(',')
            self.eat('>>')
            return tuple(items)
        if tok == '{':
            items = []
            while self.peek() != '}':
                items.append(self.value())
                if self.peek() == ',':
                    self.eat(',')
            self.eat('}')
            return frozenset(items) if all(isinstance(x, (str, int, tuple)) for x in items) else items
        if tok == '[':
            rec = {}
            while self.peek() != ']':
                k = self.eat()
                self.eat('|->')
                rec[k] = self.value()
                if self.peek() == ',':
                    self.eat(',')
            self.eat(']')
            return rec
        if tok.startswith('"'):
            return tok[1:-1]
        if tok == 'TRUE':
            return True
        if tok == 'FALSE':
            return False
        if re.fullmatch(r'-?\d+', tok):
            n = int(tok)
            if self.peek() == '..':
                self.eat('..')
                m = int(self.eat())
                return frozenset(range(n, m + 1))
            return n
        raise ValueError('unexpected token %r' % tok)


def parse_val(s):
    return P(tokenize(s)).value()


def parse_trace(out):
    """Return list of (action label, {var: value}) from a TLC error trace."""
    states = []
    lines = out.splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r'^State (\d+): (.*)$', lines[i])
        if m:
            label = m.group(2)
            i += 1
            buf = []
            while i < len(lines) and lines[i].strip() != '' and not lines[i].startswith('State '):
                buf.append(lines[i])
                i += 1
            text = '\n'.join(buf)
            vs = {}
            for part in re.split(r'^/\\ ', text, flags=re.M):
                part = part.strip()
                if not part:
                    continue
                k, _, v = part.partition(' = ')
                vs[k.strip()] = parse_val(v)
            states.append((label, vs))
        else:
            i += 1
    return states


# ------------------------------------------------------------------ trace rendering
def jr_s(J):
    return '[' + ' '.join(ent_s(e) for e in J) + ']'


def ent_s(e):
    if e['isc']:
        return 'e%d:cfg{%s}' % (e['ep'], ','.join(sorted(e['mem'])))
    return 'e%d:%s' % (e['ep'], e['cmd'])


def cfg_idx(J):
    for k in range(len(J), 0, -1):
        if J[k - 1]['isc']:
            return k
    return 0


def cfg_of(J, init):
    k = cfg_idx(J)
    return sorted(J[k - 1]['mem']) if k else sorted(init)


def diff_events(i, a, b, init):
    J, K = a['jr'], b['jr']
    cp = 0
    while cp < min(len(J), len(K)) and J[cp] == K[cp]:
        cp += 1
    ev = []
    if a['role'] != 'C' and b['role'] == 'C':
        ev.append('Elected(%s, epoch=%d, config={%s})' % (i, b['ep'], ','.join(cfg_of(J, init))))
    if cp < len(J):
        ev.append('Truncated(%s, from=%d, removed %s)' % (i, cp + 1, jr_s(J[cp:])))
    for k in range(cp, len(K)):
        ev.append('Appended(%s, %d, %s)' % (i, k + 1, ent_s(K[k])))
    if cfg_idx(J) != cfg_idx(K) or (cfg_idx(K) > cp):
        ev.append('ConfigInEffect(%s, {%s}, %d)' % (i, ','.join(cfg_of(K, init)), cfg_idx(K)))
    for k in range(a['ci'] + 1, b['ci'] + 1):
        ev.append('Committed(%s, %d, e%d)' % (i, k, K[k - 1]['ep']))
    if a['ch']['ph'] == 'commit' and b['ch']['op'] == 'none' and b['up'] and b['ci'] >= a['ch']['idx']:
        ev.append('ChangeReplied(%s, %s %s, ok)' % (i, a['ch']['op'], a['ch']['t']))
    if a['ch']['ph'] == 'catch' and b['ch']['op'] == 'none' and b['role'] == 'C' and a['ep'] == b['ep']:
        ev.append('ChangeReplied(%s, %s %s, timeout)' % (i, a['ch']['op'], a['ch']['t']))
    notes = []
    if a['ep'] != b['ep']:
        notes.append('epoch %d->%d' % (a['ep'], b['ep']))
    if a['role'] != b['role'] and not (b['role'] == 'C'):
        notes.append({'F': 'follower', 'L': 'candidate', 'C': 'coordinator'}[b['role']])
    if a['vf'] != b['vf'] and b['vf'] != 'none':
        notes.append('votes for %s' % b['vf'])
    return ev, notes


def msg_s(m):
    s = '%s %s->%s e%d' % (m['ty'], m['src'], m['dst'], m['ep'])
    if m['ty'] == 'RV':
        s += ' last=(%d,e%d)' % (m['a'], m['b'])
    elif m['ty'] == 'RVR':
        s += ' %s' % ('grant' if m['ok'] else 'refuse')
    elif m['ty'] == 'AE':
        s += ' prev=(%d,e%d) %s ci=%d' % (m['a'], m['b'], jr_s(m['ents']), m['ci'])
    elif m['ty'] == 'AER':
        s += ' %s' % (('ok match=%d' % m['a']) if m['ok'] else 'fail')
    return s


def act_s(p):
    op = p['op']
    if op in ('add', 'remove'):
        return '%s %s at %s' % (op, p['t'], p['at'])
    if op == 'command':
        return 'command %s at %s' % (p['cmd'], p['at'])
    if op in ('crash', 'restart'):
        return '%s %s' % (op, p['t'])
    if op in ('cut', 'drop'):
        return '%s %s' % (op, ' '.join('%s-%s' % tuple(l) for l in sorted(p['links'])))
    return op


def render(states, init):
    out = []
    for n in range(1, len(states)):
        label, b = states[n]
        a = states[n - 1][1]
        lab = re.match(r'<(\w+)', label)
        lab = lab.group(1) if lab else label
        parts = []
        if b['stp'] > a['stp']:
            parts.append('STEP %d: %s' % (a['stp'], act_s(a['pend'])))
            p = a['pend']
            if p['op'] in ('add', 'remove') and a['st'][p['at']]['up']:
                parts.append('ChangeRequested(%s, %s %s)' % (p['at'], p['op'], p['t']))
                if b['st'][p['at']] == a['st'][p['at']]:
                    r = a['st'][p['at']]
                    parts.append('ChangeReplied(%s, %s)' % (p['at'], 'not coordinator' if r['role'] != 'C' else 'rejected'))
        else:
            parts.append(lab)
        ev_all = []
        for i in sorted(b['st']):
            if a['st'][i] != b['st'][i]:
                ev, notes = diff_events(i, a['st'][i], b['st'][i], init)
                ev_all += ev
                if notes:
                    parts.append('%s: %s' % (i, ', '.join(notes)))
        sent = [m for m in b['msgs'] if m not in a['msgs']]
        if lab == 'Deliver' and b['stp'] == a['stp']:
            # the delivered message is not printed by TLC; show the receiver's reply instead
            pass
        if sent:
            parts.append('sends ' + '; '.join(msg_s(m) for m in sent))
        if ev_all:
            parts.append('=> ' + '; '.join(ev_all))
        if b['pend'] != a['pend'] and b['pend']['op'] != 'none' and b['stp'] == a['stp']:
            parts.append('[step %d fires: %s]' % (b['stp'], act_s(b['pend'])))
        if b['stp'] > a['stp'] and b['pend']['op'] != 'none':
            parts.append('[step %d fires: %s]' % (b['stp'], act_s(b['pend'])))
        if b.get('down') != a.get('down'):
            parts.append('down links now: %s' % (' '.join('%s>%s' % tuple(l) for l in sorted(b['down'])) or 'none'))
        out.append('%3d. %s' % (n, ' | '.join(parts)))
    last = states[-1][1]
    out.append('final journals: ' + '; '.join('%s%s %s ci=%d %s' % (
        i, '' if last['st'][i]['up'] else '(down)', last['st'][i]['role'], last['st'][i]['ci'], jr_s(last['st'][i]['jr']))
        for i in sorted(last['st'])))
    return out


def violation_detail(inv, last):
    if inv in ('InvJ14a', 'AnyJ14a'):
        for r in last['elec']:
            for c in last['comm']:
                j = r['j']
                if c['e'] < r['e'] and not (len(j) >= c['idx'] and j[c['idx'] - 1] == c['ent']):
                    return ('J1.4(a): %s elected in epoch %d with journal %s, lacking %s at index %d, '
                            'committed by a coordinator in epoch %d' % (r['m'], r['e'], jr_s(j), ent_s(c['ent']), c['idx'], c['e']))
    if inv in ('InvJ11', 'AnyJ11'):
        by = {}
        for r in last['elec']:
            by.setdefault(r['e'], set()).add(r['m'])
        return 'J1.1: ' + '; '.join('epoch %d: %s' % (e, sorted(s)) for e, s in by.items() if len(s) > 1)
    if inv in ('InvJ14b', 'AnyJ14b'):
        return 'J1.4(b): a member removed an entry from an index at which it was committed (see Truncated above)'
    if inv in ('InvJ13', 'AnyJ13'):
        return 'J1.3: a configuration entry does not differ from its predecessor by exactly one member'
    return inv


CLAUSE = {'InvJ11': 'J1.1', 'InvJ13': 'J1.3', 'InvJ14a': 'J1.4', 'InvJ14b': 'J1.4',
          'AnyJ11': 'J1.1', 'AnyJ13': 'J1.3', 'AnyJ14a': 'J1.4', 'AnyJ14b': 'J1.4'}


def summarize(out):
    s = {}
    m = re.findall(r'([\d,]+) states generated, ([\d,]+) distinct states found, ([\d,]+) states left on queue', out)
    if m:
        g, dct, ql = m[-1]
        s['generated'], s['distinct'], s['left'] = (int(x.replace(',', '')) for x in (g, dct, ql))
    m = re.search(r'depth of the complete state graph search is (\d+)', out)
    if m:
        s['depth'] = int(m.group(1))
    return s


def one(path, variant, b, mode, workers, limit, tag):
    d = load(path)
    workdir = os.path.join(HERE, 'runs', '%s_%s_%s%s' % (d['scenario'] if d['scenario'] != 'K1' else 'K1v3',
                                                         variant, mode, tag))
    mod = compile_model(d, variant, b, mode, workdir)
    out, rc, dt, rss = run_tlc(workdir, mod, workers, limit)
    res = {'mode': mode, 'seconds': round(dt, 1), 'peak_rss_kb': rss}
    res.update(summarize(out))
    m = re.search(r'Invariant (\w+) is violated', out)
    if m:
        inv = m.group(1)
        res['violated'] = inv
        try:
            states = parse_trace(out)
            res['trace'] = render(states, d['initial'])
            res['trace_len'] = len(states) - 1
            res['detail'] = violation_detail(inv, states[-1][1])
            res['all_steps_taken'] = states[-1][1]['stp'] > len(d['steps'])
        except Exception as e:  # keep the raw output for inspection
            res['trace_error'] = repr(e)
    elif 'Model checking completed. No error has been found.' in out:
        res['exhausted'] = True
    elif rc == 124 or 'Terminated' in out or rc in (-9, 137, 143):
        res['killed'] = 'wall-clock limit %ds (rc %d)' % (limit, rc)
    else:
        res['error'] = out[-3000:]
    return res


def outcome(results, nsteps):
    r, s = results.get('reach'), results.get('safety')
    if s and s.get('violated'):
        return 'FAIL %s' % CLAUSE[s['violated']]
    if r and r.get('exhausted'):
        return 'UNEXPLAINED steps'
    if r and not r.get('violated'):
        return 'UNEXPLAINED bound'  # reachability probe did not finish
    if s and s.get('exhausted'):
        return 'PASS'
    return 'UNEXPLAINED bound'


# ------------------------------------------------------------------ fexp engine (Rust port of tla/F.tla)
FEXP = os.path.join(HERE, 'fexp', 'target', 'release', 'fexp')
MCODE = {m: i for i, m in enumerate(MEMBERS)}
MCODE.update({'coordinator': 10, 'follower': 11, 'crashed': 12})
STATUS = {'ok': 1, 'timeout': 2, 'not coordinator': 3, 'busy': 4, 'invalid': 5}
ACODE = {'add': 1, 'remove': 2, 'command': 3, 'crash': 4, 'restart': 5, 'cut': 6, 'drop': 7, 'heal': 8}


def fexp_input(d):
    cmds = []
    lines = ['init %d' % sum(1 << MCODE[m] for m in d['initial'])]
    for s in d['steps']:
        at = s['at']
        if at == 'start':
            t = 'start'
        else:
            t = at['event']
            for k, v in at.items():
                if k == 'event':
                    continue
                if k in ('member', 'target'):
                    v = MCODE[v]
                elif k == 'kind':
                    v = {'command': 0, 'config': 1}[v]
                elif k == 'status':
                    v = STATUS[v]
                elif k == 'op':
                    v = {'add': 1, 'remove': 2}[v]
                t += ' %s=%d' % (k, int(v))
        do = s['do']
        op = [k for k in do if k in ACODE][0]
        a = {'op': ACODE[op], 't': 255, 'at': 255, 'cmd': 0, 'links': ''}
        if op in ('add', 'remove', 'crash', 'restart'):
            a['t'] = MCODE[name(do[op])]
        if 'at' in do:
            a['at'] = MCODE[name(do['at'])]
        if op == 'command':
            if do['command'] not in cmds:
                cmds.append(str(do['command']))
            a['cmd'] = 1 + cmds.index(str(do['command']))
        if op in ('cut', 'drop'):
            a['links'] = ','.join('%d:%d' % (MCODE[name(x)], MCODE[name(y)]) for x, y in do[op])
        lines.append('step %s | op=%d t=%d at=%d cmd=%d links=%s' % (t, a['op'], a['t'], a['at'], a['cmd'], a['links']))
    if cmds:
        lines.insert(1, 'cmds ' + ' '.join(cmds))
    return '\n'.join(lines) + '\n'


def run_fexp(path, variant, b, threads, limit, bits, tag, fail='11,13,14a,14b', noprune=False):
    d = load(path)
    nm = d['scenario'] if d['scenario'] != 'K1' else 'K1v3'
    workdir = os.path.join(HERE, 'runs', 'fexp_%s_%s%s' % (nm, variant, tag))
    os.makedirs(workdir, exist_ok=True)
    inp = os.path.join(workdir, 'scenario.txt')
    with open(inp, 'w') as f:
        f.write(fexp_input(d))
    cmd = CAP + ['/usr/bin/time', '-v', FEXP, inp, variant, '--maxe', str(b['maxe']), '--maxt', str(b['maxt']),
                 '--maxj', str(b['maxj']), '--settle', str(b['settle']), '--threads', str(threads),
                 '--bits', str(bits), '--limit', str(limit), '--fail', fail, '--maxlost', str(b.get('maxlost', 255)), '--maxtpre', str(b.get('maxtpre') or b['maxt'])] + (['--noprune'] if noprune else [])
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    with open(os.path.join(workdir, 'out.txt'), 'w') as f:
        f.write(p.stdout)
    with open(os.path.join(workdir, 'err.txt'), 'w') as f:
        f.write(p.stderr)
    res = {'scenario': d['scenario'], 'path': path, 'variant': variant, 'bounds': b, 'engine': 'fexp'}
    m = re.search(r'Maximum resident set size \(kbytes\): (\d+)', p.stderr)
    res['peak_rss_kb'] = int(m.group(1)) if m else None
    m = re.search(r'STATS distinct=(\d+) done_states=(\d+) seconds=([\d.]+) exhausted=(\w+) reason=(.*)', p.stdout)
    if m:
        res.update(distinct=int(m.group(1)), done_states=int(m.group(2)), seconds=float(m.group(3)),
                   exhausted=m.group(4) == 'true', reason=m.group(5))
    m = re.search(r'^RESULT (.*)$', p.stdout, re.M)
    res['outcome'] = m.group(1) if m else 'ERROR rc=%d %s' % (p.returncode, p.stderr[-500:])
    res['trace'] = [l[6:] for l in p.stdout.splitlines() if l.startswith('TRACE ')]
    res['trace_len'] = next((l for l in p.stdout.splitlines() if l.startswith('TRACE_LEN')), None)
    res['note'] = [l for l in p.stdout.splitlines() if l.startswith('NOTE')]
    res['witness'] = {}
    for l in p.stdout.splitlines():
        m = re.match(r'^WIT(\d) (.*)$', l)
        if m:
            res['witness'].setdefault(['J1.1', 'J1.3', 'J1.4(a)', 'J1.4(b)', "J1.4(b')"][int(m.group(1))], []).append(m.group(2))
    res['fail_clauses'] = fail
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('scenario')
    ap.add_argument('variant', choices=['SPEC', 'GATED'])
    ap.add_argument('--maxe', type=int, default=3)
    ap.add_argument('--maxt', type=int, default=3)
    ap.add_argument('--maxj', type=int, default=None)
    ap.add_argument('--settle', type=int, default=4)
    ap.add_argument('--depth', type=int, default=None, help='BFS depth bound (transitions)')
    ap.add_argument('--modes', default='reach,safety')
    ap.add_argument('--workers', type=int, default=32)
    ap.add_argument('--limit', type=int, default=600)
    ap.add_argument('--tag', default='')
    ap.add_argument('--json')
    ap.add_argument('--engine', default='fexp', choices=['fexp', 'tlc'])
    ap.add_argument('--bits', type=int, default=30)
    ap.add_argument('--fail', default='11,13,14a,14b', help="flags that make a FAIL (14k = diagnostic J1.4(b'))")
    ap.add_argument('--noprune', action='store_true')
    ap.add_argument('--maxtpre', type=int, default=None, help='bound: timeouts before every step is taken')
    ap.add_argument('--maxlost', type=int, default=255, help='bound: deliverable replies that are lost')
    a = ap.parse_args()
    d = load(a.scenario)
    b = {'maxe': a.maxe, 'maxt': a.maxt, 'settle': a.settle, 'depth': a.depth, 'maxlost': a.maxlost, 'maxtpre': a.maxtpre,
         'maxj': a.maxj if a.maxj is not None else needed_journal(d, a.variant == 'GATED')}
    if a.engine == 'fexp':
        res = run_fexp(a.scenario, a.variant, b, a.workers, a.limit, a.bits, a.tag, a.fail, a.noprune)
        print('OUTCOME %s %s: %s  %s' % (d['scenario'], a.variant, res['outcome'],
              json.dumps({k: res.get(k) for k in ('distinct', 'done_states', 'seconds', 'exhausted', 'reason', 'peak_rss_kb')})))
        for l in res['trace'] + res['note']:
            print('  ' + l)
        if a.json:
            os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
            with open(a.json, 'w') as f:
                json.dump(res, f, indent=1)
        return
    results = {}
    for mode in a.modes.split(','):
        results[mode] = one(a.scenario, a.variant, b, mode, a.workers, a.limit, a.tag)
        r = results[mode]
        print('[%s %s %s] %s' % (d['scenario'], a.variant, mode,
                                 json.dumps({k: v for k, v in r.items() if k not in ('trace', 'error')})), flush=True)
        if 'error' in r:
            print(r['error'])
        if mode == 'reach' and r.get('exhausted'):
            break  # no behaviour takes every step: UNEXPLAINED steps
    res = {'scenario': d['scenario'], 'path': a.scenario, 'variant': a.variant, 'bounds': b,
           'outcome': outcome(results, len(d['steps'])), 'runs': results}
    print('OUTCOME %s %s: %s' % (d['scenario'], a.variant, res['outcome']))
    s = results.get('safety', {})
    if s.get('violated'):
        print('  ' + s.get('detail', ''))
        print('\n'.join('  ' + x for x in s.get('trace', [])))
    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
        with open(a.json, 'w') as f:
            json.dump(res, f, indent=1, default=lambda o: sorted(o) if isinstance(o, frozenset) else str(o))


if __name__ == '__main__':
    main()
