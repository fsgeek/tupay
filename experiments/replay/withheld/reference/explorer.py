#!/usr/bin/env python3
"""Reference explicit-state explorer for replay/spec-F.md, with a scenario driver.

Validation tool for the replay inputs (not an experimental artifact).
derives: J1.1, J1.3, J1.4, G1.1, G1.2, G1.3, G1.4 (contract v2, failure model v1)

Variants:
  SPEC  : spec F exactly as written.
  GATED : SPEC plus (i) a new coordinator appends one no-op command entry on
          election, (ii) a coordinator does not append a configuration entry
          (step 3/4 of add, step 2/3 of remove) until its commitIndex covers an
          entry of its current epoch.

Usage: explorer.py SCENARIO.yaml SPEC|GATED [--maxe 3] [--maxl 3] [--maxm 30]
                   [--max-states N] [--json out.json]
"""
import argparse, json, subprocess, sys, time
from collections import deque

N = 5
NAMES = ['m1', 'm2', 'm3', 'm4', 'm5']
IDX = {n: i for i, n in enumerate(NAMES)}
ALL = (1 << N) - 1

# member tuple fields
UP, EP, VOTED, JR, ROLE, CI, VOTES, NXT, MI, CH = range(10)
FOLLOWER, CANDIDATE, COORD = 0, 1, 2


def popcount(x):
    return bin(x).count('1')


def mask_names(m):
    return [NAMES[i] for i in range(N) if m >> i & 1]


def cfg_of(journal, init):
    """(config mask, index of the config entry or 0 for initial)."""
    for k in range(len(journal) - 1, -1, -1):
        e = journal[k]
        if e[1]:
            return e[2], k + 1
    return init, 0


def majority(count, cfg):
    return count * 2 > popcount(cfg)


class Pruned(Exception):
    pass


# ---------------------------------------------------------------- scenario
def load_yaml(path):
    try:
        import yaml  # noqa
        with open(path) as f:
            return yaml.safe_load(f)
    except ImportError:
        out = subprocess.check_output(
            ['/usr/bin/python3', '-c',
             'import sys,yaml,json;print(json.dumps(yaml.safe_load(open(sys.argv[1]))))', path])
        return json.loads(out)


SELECTORS = ('coordinator', 'follower', 'crashed')


class Scenario:
    def __init__(self, path):
        d = load_yaml(path)
        self.name = d['scenario']
        self.init = 0
        for n in d['initial']:
            self.init |= 1 << IDX[n]
        self.steps = d['steps']
        self.settle = d['end']['settle']
        self.bound = d['bound']['events']
        # static check: 'crashed' before any crash step
        seen_crash = False
        for s in self.steps:
            if 'crashed' in json.dumps(s['do']) and not seen_crash:
                raise SystemExit('scenario rejected: crashed selector before any crash step')
            if 'crash' in s['do']:
                seen_crash = True


def trig_match(at, ev):
    if at == 'start' or not isinstance(at, dict):
        return False
    for k, v in at.items():
        if k == 'event':
            if ev['event'] != v:
                return False
        else:
            if k not in ev:
                return False
            if k == 'config':
                if sorted(ev[k]) != sorted(v):
                    return False
            elif ev[k] != v:
                return False
    return True


def resolve(do, lastE, lastC, members):
    """Return list of resolved actions (several when 'follower' is used), or None if rejected."""
    uses_f = 'follower' in json.dumps(do)
    fchoices = [None]
    if uses_f:
        fchoices = [i for i in range(N) if members[i][UP] and i != lastE]

    def r(x, f):
        if x == 'coordinator':
            if lastE < 0:
                raise ValueError('coordinator before any Elected')
            return lastE
        if x == 'crashed':
            if lastC < 0:
                raise ValueError('crashed before any crash')
            return lastC
        if x == 'follower':
            return f
        return IDX[x]

    out = []
    for f in fchoices:
        (op, arg), = [(k, v) for k, v in do.items() if k != 'at'] if len(do) <= 2 else [None]
        if op in ('add', 'remove'):
            out.append((op, r(arg, f), r(do['at'], f)))
        elif op == 'command':
            out.append(('command', arg, r(do['at'], f)))
        elif op in ('crash', 'restart'):
            out.append((op, r(arg, f)))
        elif op in ('cut', 'drop'):
            links = []
            for a, b in arg:
                a, b = r(a, f), r(b, f)
                if a != b:
                    links.append((a, b))
            out.append((op, tuple(links)))
        elif op == 'heal':
            out.append(('heal',))
        else:
            raise ValueError('unknown action %r' % (do,))
    return out


def fmt_action(a):
    if a[0] in ('add', 'remove'):
        return '%s %s at %s' % (a[0], NAMES[a[1]], NAMES[a[2]])
    if a[0] == 'command':
        return 'command %s at %s' % (a[1], NAMES[a[2]])
    if a[0] in ('crash', 'restart'):
        return '%s %s' % (a[0], NAMES[a[1]])
    if a[0] in ('cut', 'drop'):
        return '%s %s' % (a[0], ' '.join('%s-%s' % (NAMES[x], NAMES[y]) for x, y in a[1]))
    return a[0]


# ---------------------------------------------------------------- model
class Ctx:
    """Mutable successor under construction."""
    __slots__ = ('_mem', 'dirty', '_msgs', 'msgs_dirty', 'down', '_gE', '_gC', 'gdirty', 'viol', 'events', 'model', 'tmo')

    def __init__(self, model, st):
        mem, msgs, down, scen, ghostE, ghostC, viol, tmo = st
        self.tmo = tmo
        self.model = model
        self._mem = list(mem)
        self.dirty = 0
        self._msgs = msgs
        self.msgs_dirty = False
        self.down = down
        self._gE = ghostE
        self._gC = ghostC
        self.gdirty = False
        self.viol = viol
        self.events = []

    class _MemView:
        __slots__ = ('c',)

        def __init__(self, c):
            self.c = c

        def __getitem__(self, i):
            c = self.c
            if not (c.dirty >> i & 1):
                m = list(c._mem[i])
                if m[NXT] is not None:
                    m[NXT] = list(m[NXT])
                    m[MI] = list(m[MI])
                c._mem[i] = m
                c.dirty |= 1 << i
            return c._mem[i]

    @property
    def mem(self):
        return Ctx._MemView(self)

    @property
    def msgs(self):
        if not self.msgs_dirty:
            self._msgs = set(self._msgs)
            self.msgs_dirty = True
        return self._msgs

    def _g(self):
        if not self.gdirty:
            self._gE = dict(self._gE)
            self._gC = dict(self._gC)
            self.gdirty = True

    @property
    def ghostE(self):
        self._g()
        return self._gE

    @property
    def ghostC(self):
        self._g()
        return self._gC

    def emit(self, **ev):
        self.events.append(ev)

    def violate(self, clause, why):
        if self.viol is None:
            self.viol = (clause, why)

    def link_up(self, a, b):
        return not (self.down >> (a * N + b) & 1)

    def send(self, msg):
        src, dst = msg[1], msg[2]
        if src == dst or not self.link_up(src, dst):
            return  # lost (G1.3)
        if len(self._msgs) >= self.model.maxm and msg not in self._msgs:
            return  # in-flight bound reached: the message is lost (an instance of G1.2)
        self.msgs.add(msg)

    def cfg(self, i):
        return cfg_of(self.mem[i][JR], self.model.init)[0]

    # -- journal changes on member i, with events and J1.3/J1.4b checks
    def append(self, i, entry):
        m = self.mem[i]
        if len(m[JR]) >= self.model.maxl:
            raise Pruned('journal')
        before = cfg_of(m[JR], self.model.init)
        m[JR] = m[JR] + (entry,)
        idx = len(m[JR])
        self.emit(event='Appended', member=NAMES[i], index=idx, epoch=entry[0],
                  kind='config' if entry[1] else 'command',
                  payload=mask_names(entry[2]) if entry[1] else entry[2])
        if entry[1]:
            prev = before[0]
            diff = prev ^ entry[2]
            if popcount(diff) != 1:  # J1.3
                self.violate('J1.3', '%s journal index %d config %s follows %s' %
                             (NAMES[i], idx, mask_names(entry[2]), mask_names(prev)))
            self.emit(event='ConfigInEffect', member=NAMES[i], config=mask_names(entry[2]), index=idx)

    def truncate(self, i, frm):
        m = self.mem[i]
        before = cfg_of(m[JR], self.model.init)
        for k in range(frm, len(m[JR]) + 1):  # J1.4(b)
            e = m[JR][k - 1]
            if (k, e) in self.ghostC:
                self.violate('J1.4', '(b) %s removes committed entry %s at index %d (committed in epoch %d)' %
                             (NAMES[i], fmt_entry(e), k, self.ghostC[(k, e)]))
        m[JR] = m[JR][:frm - 1]
        self.emit(event='Truncated', member=NAMES[i], from_index=frm)
        after = cfg_of(m[JR], self.model.init)
        if after != before:
            self.emit(event='ConfigInEffect', member=NAMES[i], config=mask_names(after[0]), index=after[1])

    def set_commit(self, i, new):
        m = self.mem[i]
        if new <= m[CI]:
            return
        old = m[CI]
        m[CI] = new
        for k in range(old + 1, new + 1):
            self.emit(event='Committed', member=NAMES[i], index=k, epoch=m[JR][k - 1][0])

    def step_down(self, i):
        m = self.mem[i]
        if m[ROLE] == COORD and m[CH] is not None:
            op, t = m[CH][0], m[CH][1]
            self.emit(event='ChangeReplied', member=NAMES[i], op=op, target=NAMES[t], status='not coordinator')
        m[ROLE] = FOLLOWER
        m[VOTES] = 0
        m[NXT] = None
        m[MI] = None
        m[CH] = None

    def observe_epoch(self, i, e):
        m = self.mem[i]
        if e > m[EP]:
            m[EP] = e
            m[VOTED] = -1
            self.step_down(i)

    # -- coordinator commitment rule (applied whenever matchIndex/journal/config change)
    def commit_rule(self, i):
        m = self.mem[i]
        if m[ROLE] != COORD:
            return
        cfg = self.cfg(i)
        J = m[JR]
        last = len(J)
        best = 0
        for n in range(last, m[CI], -1):
            if J[n - 1][0] != m[EP]:
                continue
            cnt = 0
            for j in range(N):
                if cfg >> j & 1:
                    if j == i:
                        cnt += 1
                    elif m[MI][j] >= n:
                        cnt += 1
            if majority(cnt, cfg):
                best = n
                break
        if best:
            e = m[EP]
            for k in range(1, best + 1):
                key = (k, J[k - 1])
                if key not in self.ghostC or self.ghostC[key] > e:
                    self.ghostC[key] = e
                    # J1.4(a) against coordinators already elected in higher epochs
                    for ep2, (who, jr) in self.ghostE.items():
                        if ep2 > e and not (len(jr) >= k and jr[k - 1] == J[k - 1]):
                            self.violate('J1.4', '(a) %s committed %s at index %d in epoch %d but %s was elected in epoch %d without it' %
                                         (NAMES[i], fmt_entry(J[k - 1]), k, e, NAMES[who], ep2))
            self.set_commit(i, best)
        self.check_change_done(i)

    def check_change_done(self, i):
        m = self.mem[i]
        ch = m[CH]
        if m[ROLE] == COORD and ch is not None and ch[2] == 'commit' and m[CI] >= ch[3]:
            m[CH] = None
            self.emit(event='ChangeReplied', member=NAMES[i], op=ch[0], target=NAMES[ch[1]], status='ok')
            if ch[0] == 'remove' and ch[1] == i:
                self.step_down(i)

    def become_coord(self, i):
        m = self.mem[i]
        e = m[EP]
        m[ROLE] = COORD
        m[VOTES] = 0
        last = len(m[JR])
        m[NXT] = [last + 1] * N
        m[MI] = [0] * N
        m[CH] = None
        # J1.1
        if e in self.ghostE and self.ghostE[e][0] != i:
            self.violate('J1.1', '%s and %s both coordinator in epoch %d' % (NAMES[self.ghostE[e][0]], NAMES[i], e))
        else:
            self.ghostE[e] = (i, m[JR])
        # J1.4(a)
        for (k, ent), ce in self.ghostC.items():
            if ce < e and not (len(m[JR]) >= k and m[JR][k - 1] == ent):
                self.violate('J1.4', '(a) %s elected in epoch %d without committed %s at index %d (committed in epoch %d)' %
                             (NAMES[i], e, fmt_entry(ent), k, ce))
        self.emit(event='Elected', member=NAMES[i], epoch=e, config=mask_names(self.cfg(i)))
        if self.model.gated:
            self.append(i, (e, False, 'noop'))
        self.commit_rule(i)

    def freeze(self):
        mem = self._mem
        if self.dirty:
            for i in range(N):
                if self.dirty >> i & 1:
                    m = mem[i]
                    if m[NXT] is not None:
                        m[NXT] = tuple(m[NXT])
                        m[MI] = tuple(m[MI])
                    mem[i] = tuple(m)
        msgs = frozenset(self._msgs) if self.msgs_dirty else self._msgs
        if self.gdirty:
            gE = tuple(sorted(self._gE.items()))
            gC = tuple(sorted(self._gC.items(), key=repr))
        else:
            gE, gC = self._gE, self._gC
        return tuple(mem), msgs, self.down, gE, gC, self.viol, self.tmo


def fmt_entry(e):
    if e[1]:
        return '<ep%d config {%s}>' % (e[0], ','.join(mask_names(e[2])))
    return '<ep%d %s>' % (e[0], e[2])


class Model:
    def __init__(self, scen, gated, maxe, maxl, maxm, maxt, dup):
        self.maxt, self.dup = maxt, dup
        self.scen = scen
        self.init = scen.init
        self.gated = gated
        self.maxe, self.maxl, self.maxm = maxe, maxl, maxm

    def initial(self):
        mem = tuple((1, 0, -1, (), FOLLOWER, 0, 0, None, None, None) for _ in range(N))
        # state: (mem, msgs, down, scen, ghostE, ghostC, viol); scen = (step, fired, lastE, lastC)
        step, fired = 0, None
        if self.scen.steps and self.scen.steps[0]['at'] == 'start':
            acts = resolve(self.scen.steps[0]['do'], -1, -1, mem)
            fired = acts[0]  # 'start' with a 'follower' selector is not handled; none of the inputs need it
        return (mem, frozenset(), 0, (step, fired, -1, -1), (), (), None, 0)

    # ---- system transitions
    def system_moves(self, st):
        mem, msgs = st[0], st[1]
        for i in range(N):
            m = mem[i]
            if not m[UP]:
                continue
            if m[ROLE] != COORD:
                yield ('timeout', i)
            if m[ROLE] == CANDIDATE:
                for j in range(N):
                    if j != i and cfg_of(m[JR], self.init)[0] >> j & 1:
                        yield ('resend_ballot', i, j)
            if m[ROLE] == COORD:
                targets = cfg_of(m[JR], self.init)[0]
                if m[CH] is not None and m[CH][2] == 'catch':
                    targets |= 1 << m[CH][1]
                for j in range(N):
                    if j != i and targets >> j & 1:
                        yield ('extend', i, j)
                if m[CH] is not None and m[CH][2] == 'catch':
                    yield ('catchup_timeout', i)
                if m[CH] is not None and m[CH][2] == 'ready':
                    yield ('proceed', i)
        for msg in msgs:
            yield ('drop_msg', msg)  # G1.2 loss of an in-flight message
            if mem[msg[2]][UP] and not (st[2] >> (msg[1] * N + msg[2]) & 1):
                yield ('deliver', msg)
                if self.dup:
                    yield ('deliver_keep', msg)  # G1.2 duplication: delivered, a copy stays in flight

    def apply_system(self, st, mv):
        c = Ctx(self, st)
        kind = mv[0]
        if kind == 'timeout':
            i = mv[1]
            m = c.mem[i]
            if m[EP] + 1 > self.maxe:
                raise Pruned('epoch')
            if c.tmo + 1 > self.maxt:
                raise Pruned('timeouts')
            c.tmo += 1
            m[EP] += 1
            m[VOTED] = i
            m[ROLE] = CANDIDATE
            m[VOTES] = 1 << i
            cfg = c.cfg(i)
            J = m[JR]
            lidx, lep = len(J), (J[-1][0] if J else 0)
            for j in range(N):
                if j != i and cfg >> j & 1:
                    c.send(('RV', i, j, m[EP], lidx, lep))
            if majority(popcount(m[VOTES] & cfg), cfg):
                c.become_coord(i)
        elif kind == 'resend_ballot':
            i, j = mv[1], mv[2]
            m = c.mem[i]
            J = m[JR]
            msg = ('RV', i, j, m[EP], len(J), (J[-1][0] if J else 0))
            if msg in c._msgs or not c.link_up(i, j):
                return None
            c.send(msg)
        elif kind == 'extend':
            i, j = mv[1], mv[2]
            m = c.mem[i]
            J = m[JR]
            prev = m[NXT][j] - 1
            prevep = J[prev - 1][0] if prev >= 1 else 0
            msg = ('AE', i, j, m[EP], prev, prevep, J[prev:], m[CI])
            if msg in c._msgs or not c.link_up(i, j):
                return None
            c.send(msg)
        elif kind == 'catchup_timeout':
            i = mv[1]
            ch = c.mem[i][CH]
            c.mem[i][CH] = None
            c.emit(event='ChangeReplied', member=NAMES[i], op=ch[0], target=NAMES[ch[1]], status='timeout')
        elif kind == 'proceed':
            i = mv[1]
            m = c.mem[i]
            cfg, cidx = cfg_of(m[JR], self.init)
            if cidx > m[CI]:
                return None  # previous configuration entry not yet committed
            if self.gated and not any(m[JR][k][0] == m[EP] for k in range(m[CI])):
                return None  # GATED: commitIndex must cover an entry of the current epoch
            op, t = m[CH][0], m[CH][1]
            new = cfg | (1 << t) if op == 'add' else cfg & ~(1 << t)
            c.append(i, (m[EP], True, new))
            m[CH] = (op, t, 'commit', len(m[JR]))
            c.commit_rule(i)
        elif kind == 'drop_msg':
            c.msgs.discard(mv[1])
        elif kind == 'deliver':
            c.msgs.discard(mv[1])
            self.deliver(c, mv[1])
        elif kind == 'deliver_keep':
            self.deliver(c, mv[1])
        return c

    def deliver(self, c, msg):
        typ, src, dst, e = msg[0], msg[1], msg[2], msg[3]
        i = dst
        c.observe_epoch(i, e)
        m = c.mem[i]
        if typ == 'RV':
            _, _, _, _, lidx, lep = msg
            if e < m[EP]:
                c.send(('RVR', i, src, m[EP], False))
                return
            J = m[JR]
            mylidx, mylep = len(J), (J[-1][0] if J else 0)
            uptodate = lep > mylep or (lep == mylep and lidx >= mylidx)
            grant = m[VOTED] in (-1, src) and uptodate
            if grant:
                m[VOTED] = src
            c.send(('RVR', i, src, m[EP], grant))
        elif typ == 'RVR':
            granted = msg[4]
            if m[ROLE] == CANDIDATE and e == m[EP] and granted:
                m[VOTES] |= 1 << src
                cfg = c.cfg(i)
                if majority(popcount(m[VOTES] & cfg), cfg):
                    c.become_coord(i)
        elif typ == 'AE':
            _, _, _, _, prev, prevep, ents, ccommit = msg
            if e < m[EP]:
                c.send(('AER', i, src, m[EP], False, 0))
                return
            if m[ROLE] != FOLLOWER:
                c.step_down(i)  # candidate hears from a coordinator of epoch >= its own
            J = m[JR]
            if prev > 0 and not (len(J) >= prev and J[prev - 1][0] == prevep):
                c.send(('AER', i, src, m[EP], False, 0))
                return
            for k, ent in enumerate(ents):
                idx = prev + 1 + k
                J = m[JR]
                if idx <= len(J):
                    if J[idx - 1][0] != ent[0]:
                        c.truncate(i, idx)
                        c.append(i, ent)
                else:
                    c.append(i, ent)
            if ccommit > m[CI]:
                c.set_commit(i, min(ccommit, prev + len(ents)))
            c.send(('AER', i, src, m[EP], True, prev + len(ents)))
        elif typ == 'AER':
            ok, match = msg[4], msg[5]
            if m[ROLE] != COORD or e != m[EP]:
                return
            if ok:
                m[MI][src] = match
                m[NXT][src] = match + 1
                ch = m[CH]
                if ch is not None and ch[2] == 'catch' and src == ch[1] and match >= ch[3]:
                    m[CH] = (ch[0], ch[1], 'ready', 0)
                c.commit_rule(i)
            else:
                m[NXT][src] = max(1, m[NXT][src] - 1)

    # ---- environment (scenario action)
    def apply_action(self, st, a):
        c = Ctx(self, st)
        op = a[0]
        if op in ('add', 'remove'):
            t, at = a[1], a[2]
            m = c.mem[at]
            if not m[UP]:
                pass  # request to a stopped member: no reply, no event
            else:
                c.emit(event='ChangeRequested', member=NAMES[at], op=op, target=NAMES[t])
                cfg = c.cfg(at)
                if m[ROLE] != COORD:
                    c.emit(event='ChangeReplied', member=NAMES[at], op=op, target=NAMES[t], status='not coordinator')
                elif m[CH] is not None:
                    c.emit(event='ChangeReplied', member=NAMES[at], op=op, target=NAMES[t], status='busy')
                elif (op == 'add') == bool(cfg >> t & 1):
                    c.emit(event='ChangeReplied', member=NAMES[at], op=op, target=NAMES[t], status='invalid')
                elif op == 'add':
                    m[CH] = ('add', t, 'catch', len(m[JR]))
                else:
                    m[CH] = ('remove', t, 'ready', 0)
        elif op == 'command':
            at = a[2]
            m = c.mem[at]
            if m[UP] and m[ROLE] == COORD:
                c.append(at, (m[EP], False, a[1]))
                c.commit_rule(at)
        elif op == 'crash':
            m = c.mem[a[1]]
            if m[UP]:
                m[UP] = 0
                m[ROLE] = FOLLOWER
                m[CI] = 0
                m[VOTES] = 0
                m[NXT] = m[MI] = m[CH] = None
        elif op == 'restart':
            m = c.mem[a[1]]
            if not m[UP]:
                m[UP] = 1
        elif op == 'cut':
            for x, y in a[1]:
                c.down |= 1 << (x * N + y)
                c.down |= 1 << (y * N + x)
        elif op == 'drop':
            for x, y in a[1]:
                c.down |= 1 << (x * N + y)
        elif op == 'heal':
            c.down = 0
        return c


# ---------------------------------------------------------------- driver
def scen_after(model, scen, events, action_taken, mem):
    """Advance scenario state over the emitted events. Returns list of new scen tuples."""
    step, fired, lastE, lastC = scen
    steps = model.scen.steps
    if action_taken is not None:
        step += 1
        fired = None
        if action_taken[0] == 'crash':
            lastC = action_taken[1]
    outs = [(step, fired, lastE, lastC)]
    for ev in events:
        new = []
        for (s, f, le, lc) in outs:
            if ev['event'] == 'Elected':
                le = IDX[ev['member']]
            if s < len(steps) and f is None and trig_match(steps[s]['at'], ev):
                for a in resolve(steps[s]['do'], le, lc, mem):
                    new.append((s, a, le, lc))
            else:
                new.append((s, f, le, lc))
        outs = new
    return outs


def run(path, variant, maxe, maxl, maxm, maxt, dup, max_states, verbose=False):
    scen = Scenario(path)
    model = Model(scen, variant == 'GATED', maxe, maxl, maxm, maxt, dup)
    nsteps = len(scen.steps)
    init = model.initial()
    # visited: key -> (parent_key, label, counter, events)
    # counter = events so far (before all steps are taken) or events since the last action (after)
    visited = {init: (None, ('init',), 0, ())}
    q = deque([init])
    prunes = {'epoch': 0, 'timeouts': 0, 'journal': 0, 'bound': 0, 'settle': 0}
    complete_states = 0
    max_step = 0
    fails = {}          # clause -> key (first completing violating state)
    noncomplete_viol = {}  # clause -> key (violation seen in a state that has not taken every step)
    maxcount = [0, 0]
    t0 = time.time()
    truncated = False
    while q:
        if len(visited) > max_states:
            truncated = True
            break
        st = q.popleft()
        cnt = visited[st][2]
        mem, msgs, down, sc, gE, gC, viol, tmo = st
        done = sc[0] >= nsteps
        max_step = max(max_step, sc[0])
        if done:
            complete_states += 1
            if viol is not None:
                fails.setdefault(viol[0], st)
                continue  # nothing more to learn from this behaviour
            if cnt >= scen.settle:
                prunes['settle'] += 1
                continue
        else:
            if viol is not None:
                noncomplete_viol.setdefault(viol[0], st)
            if cnt >= scen.bound:
                prunes['bound'] += 1
                continue
        moves = []
        for mv in model.system_moves(st):
            moves.append((mv, None))
        if sc[1] is not None:
            moves.append((('action', sc[1]), sc[1]))
        for mv, act in moves:
            try:
                if act is None:
                    c = model.apply_system(st, mv)
                else:
                    c = model.apply_action(st, act)
                if c is None:
                    continue
                fr = c.freeze()
            except Pruned as p:
                prunes[str(p)] += 1
                continue
            for nsc in scen_after(model, sc, c.events, act, fr[0]):
                ndone = nsc[0] >= nsteps
                if ndone and not done:
                    ncnt = len(c.events)  # the last action's own events count toward settle
                else:
                    ncnt = cnt + len(c.events)
                nst = (fr[0], fr[1], fr[2], nsc, fr[3], fr[4], fr[5], fr[6])
                old = visited.get(nst)
                if old is None or old[2] > ncnt:
                    visited[nst] = (st, mv if act is None else ('action', act), ncnt, tuple(c.events))
                    q.append(nst)
                    k = 1 if ndone else 0
                    maxcount[k] = max(maxcount[k], ncnt)
    dt = time.time() - t0
    res = {'scenario': scen.name, 'path': path, 'variant': variant,
           'bounds': {'max_epoch': maxe, 'max_journal': maxl, 'max_inflight': maxm, 'max_timeouts': maxt,
                      'duplication': dup, 'max_states': max_states,
                      'settle': scen.settle, 'bound_events': scen.bound},
           'states': len(visited), 'complete_states': complete_states, 'max_step_reached': max_step,
           'nsteps': nsteps, 'prunes': prunes, 'max_events_before_done': maxcount[0],
           'max_settle_events': maxcount[1], 'seconds': round(dt, 1), 'exhausted': not truncated}
    if fails:
        clause = sorted(fails)[0]
        res['outcome'] = 'FAIL ' + clause
        res['all_fail_clauses'] = sorted(fails)
        st = fails[clause]
        res['violation'] = st[6][1]
        res['trace'] = trace(visited, st)
    elif truncated:
        res['outcome'] = 'UNEXPLAINED bound'
    elif complete_states == 0:
        res['outcome'] = 'UNEXPLAINED steps'
    else:
        res['outcome'] = 'PASS'
    if noncomplete_viol:
        res['violations_in_noncompleting_behaviours'] = {
            k: {'why': v[6][1], 'trace': trace(visited, v)} for k, v in noncomplete_viol.items()}
    return res


def fmt_ev(ev):
    e = dict(ev)
    name = e.pop('event')
    return name + '(' + ', '.join('%s=%s' % (k, v) for k, v in e.items()) + ')'


def fmt_move(mv):
    if mv[0] == 'init':
        return 'init'
    if mv[0] == 'action':
        return 'STEP ACTION: ' + fmt_action(mv[1])
    if mv[0] in ('deliver', 'deliver_keep', 'drop_msg'):
        msg = mv[1]
        t = msg[0]
        s = mv[0] + ' %s %s->%s ep%d' % (t, NAMES[msg[1]], NAMES[msg[2]], msg[3])
        if t == 'RV':
            s += ' last=(%d,ep%d)' % (msg[4], msg[5])
        elif t == 'RVR':
            s += ' granted=%s' % msg[4]
        elif t == 'AE':
            s += ' prev=(%d,ep%d) entries=[%s] commit=%d' % (msg[4], msg[5], ' '.join(fmt_entry(x) for x in msg[6]), msg[7])
        elif t == 'AER':
            s += ' success=%s match=%d' % (msg[4], msg[5])
        return s
    return ' '.join([mv[0]] + [NAMES[x] if isinstance(x, int) else str(x) for x in mv[1:]])


def trace(visited, st):
    out = []
    while st is not None:
        parent, mv, cnt, evs = visited[st]
        line = fmt_move(mv)
        if evs:
            line += '  => ' + '; '.join(fmt_ev(e) for e in evs)
        out.append(line)
        st = parent
    return list(reversed(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('scenario')
    ap.add_argument('variant', choices=['SPEC', 'GATED'])
    ap.add_argument('--maxe', type=int, default=3)
    ap.add_argument('--maxl', type=int, default=3)
    ap.add_argument('--maxm', type=int, default=4)
    ap.add_argument('--maxt', type=int, default=3)
    ap.add_argument('--nodup', action='store_true')
    ap.add_argument('--max-states', type=int, default=5_000_000)
    ap.add_argument('--json')
    a = ap.parse_args()
    res = run(a.scenario, a.variant, a.maxe, a.maxl, a.maxm, a.maxt, not a.nodup, a.max_states)
    if a.json:
        with open(a.json, 'w') as f:
            json.dump(res, f, indent=1)
    show = {k: v for k, v in res.items() if k not in ('trace', 'violations_in_noncompleting_behaviours')}
    print(json.dumps(show))
    if 'trace' in res:
        print('\n'.join('  ' + x for x in res['trace']))
    for k, v in res.get('violations_in_noncompleting_behaviours', {}).items():
        print('non-completing violation', k, v['why'])


if __name__ == '__main__':
    main()
