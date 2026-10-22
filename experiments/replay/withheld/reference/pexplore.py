#!/usr/bin/env python3
"""Parallel, level-synchronous breadth-first explorer over explorer.py's model and scenario driver.

States are partitioned among W forked workers by hash(state) % W. Each worker keeps its visited set as
64-bit fingerprints (hash(state)) -> (parent fingerprint, event counter), as TLC does; traces are rebuilt
by re-executing from the initial state along the recorded fingerprints.

derives: J1.1, J1.3, J1.4, G1.1, G1.2, G1.3, G1.4

Usage: pexplore.py SCENARIO.yaml SPEC|GATED [--maxe E] [--maxl L] [--maxm M] [--maxt T] [--nodup]
                   [--workers W] [--max-states S] [--max-seconds X] [--json out.json]
"""
import argparse, json, multiprocessing as mp, sys, time, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import explorer as X

PRUNE_KEYS = ('epoch', 'timeouts', 'journal', 'bound', 'settle')


def successors(model, st, cnt, prunes):
    """Yield (next_state, next_counter, move_label, events)."""
    nsteps = len(model.scen.steps)
    sc = st[3]
    done = sc[0] >= nsteps
    moves = [(mv, None) for mv in model.system_moves(st)]
    if sc[1] is not None:
        moves.append((('action', sc[1]), sc[1]))
    for mv, act in moves:
        try:
            c = model.apply_system(st, mv) if act is None else model.apply_action(st, act)
            if c is None:
                continue
            fr = c.freeze()
        except X.Pruned as p:
            prunes[str(p)] += 1
            continue
        for nsc in X.scen_after(model, sc, c.events, act, fr[0]):
            ndone = nsc[0] >= nsteps
            ncnt = len(c.events) if (ndone and not done) else cnt + len(c.events)
            nst = (fr[0], fr[1], fr[2], nsc, fr[3], fr[4], fr[5], fr[6])
            yield nst, ncnt, (mv if act is None else ('action', act)), c.events


def classify(model, st, cnt, stats):
    """Record stats for a state being expanded; return True if it should be expanded."""
    nsteps = len(model.scen.steps)
    sc, viol = st[3], st[6]
    done = sc[0] >= nsteps
    stats['max_step'] = max(stats['max_step'], sc[0])
    if done:
        stats['complete'] += 1
        stats['max_settle'] = max(stats['max_settle'], cnt)
        if viol is not None:
            stats['fails'].setdefault(viol[0], hash(st))
            return False
        if cnt >= model.scen.settle:
            stats['prunes']['settle'] += 1
            return False
    else:
        stats['max_before'] = max(stats['max_before'], cnt)
        if viol is not None:
            stats['ncviol'].setdefault(viol[0], hash(st))
        if cnt >= model.scen.bound:
            stats['prunes']['bound'] += 1
            return False
    return True


def new_stats():
    return {'max_step': 0, 'complete': 0, 'max_settle': 0, 'max_before': 0, 'fails': {}, 'ncviol': {},
            'prunes': {k: 0 for k in PRUNE_KEYS}, 'expanded': 0, 'new': 0}


def worker(p, W, model, inboxes, cmdq, resq):
    visited = {}
    frontier = []
    init = model.initial()
    if hash(init) % W == p:
        visited[hash(init)] = (0, 0)
        frontier.append((init, 0))
    while True:
        cmd = cmdq.get()
        if cmd[0] == 'expand':
            stats = new_stats()
            out = [[] for _ in range(W)]
            for st, cnt in frontier:
                pf = hash(st)
                rec = visited.get(pf)
                if rec is not None and rec[1] < cnt:
                    continue  # superseded by a lower counter
                if not classify(model, st, cnt, stats):
                    continue
                stats['expanded'] += 1
                for nst, ncnt, _, _ in successors(model, st, cnt, stats['prunes']):
                    out[hash(nst) % W].append((nst, ncnt, pf))
            for d in range(W):
                inboxes[d].put(out[d])
            out = None
            newf = []
            for _ in range(W):
                batch = inboxes[p].get()
                for nst, ncnt, pf in batch:
                    f = hash(nst)
                    rec = visited.get(f)
                    if rec is None or rec[1] > ncnt:
                        visited[f] = (pf, ncnt)
                        newf.append((nst, ncnt))
            frontier = newf
            stats['new'] = len(newf)
            stats['visited'] = len(visited)
            resq.put(stats)
        elif cmd[0] == 'parent':
            rec = visited.get(cmd[1])
            resq.put(rec)
        elif cmd[0] == 'stop':
            return


def rebuild_trace(model, chain):
    """chain: list of fingerprints from init to target. Re-execute to recover labels and events."""
    st = model.initial()
    assert hash(st) == chain[0]
    cnt = 0
    lines = ['init']
    prunes = {k: 0 for k in PRUNE_KEYS}
    for f in chain[1:]:
        for nst, ncnt, mv, evs in successors(model, st, cnt, prunes):
            if hash(nst) == f:
                line = X.fmt_move(mv)
                if evs:
                    line += '  => ' + '; '.join(X.fmt_ev(e) for e in evs)
                lines.append(line)
                st, cnt = nst, ncnt
                break
        else:
            lines.append('<trace reconstruction failed: fingerprint not reproduced>')
            break
    return lines, st


def run(path, variant, maxe, maxl, maxm, maxt, dup, W, max_states, max_seconds):
    scen = X.Scenario(path)
    model = X.Model(scen, variant == 'GATED', maxe, maxl, maxm, maxt, dup)
    ctx = mp.get_context('fork')
    inboxes = [ctx.Queue() for _ in range(W)]
    cmdqs = [ctx.Queue() for _ in range(W)]
    resqs = [ctx.Queue() for _ in range(W)]
    procs = [ctx.Process(target=worker, args=(p, W, model, inboxes, cmdqs[p], resqs[p]), daemon=True)
             for p in range(W)]
    for pr in procs:
        pr.start()
    t0 = time.time()
    tot = new_stats()
    tot['visited'] = 1
    level = 0
    truncated = None
    while True:
        for q in cmdqs:
            q.put(('expand',))
        newtotal = 0
        visited = 0
        for q in resqs:
            s = q.get()
            for k in ('max_step', 'max_settle', 'max_before'):
                tot[k] = max(tot[k], s[k])
            tot['complete'] += s['complete']
            tot['expanded'] += s['expanded']
            for k in PRUNE_KEYS:
                tot['prunes'][k] += s['prunes'][k]
            for k, v in s['fails'].items():
                tot['fails'].setdefault(k, v)
            for k, v in s['ncviol'].items():
                tot['ncviol'].setdefault(k, v)
            newtotal += s['new']
            visited += s['visited']
        tot['visited'] = visited
        level += 1
        el = time.time() - t0
        print('level %d visited %d frontier %d complete %d max_step %d %.0fs' %
              (level, visited, newtotal, tot['complete'], tot['max_step'], el), file=sys.stderr, flush=True)
        if tot['fails']:
            break
        if newtotal == 0:
            break
        if visited > max_states:
            truncated = 'states'
            break
        if el > max_seconds:
            truncated = 'time'
            break
    dt = time.time() - t0

    def chain_to(f):
        chain = [f]
        while True:
            cmdqs[f % W].put(('parent', f))
            rec = resqs[f % W].get()
            if rec is None or rec[0] == 0:
                break
            f = rec[0]
            chain.append(f)
            if len(chain) > 10000:
                break
        return list(reversed(chain))

    res = {'scenario': scen.name, 'path': path, 'variant': variant,
           'bounds': {'max_epoch': maxe, 'max_journal': maxl, 'max_inflight': maxm, 'max_timeouts': maxt,
                      'duplication': dup, 'max_states': max_states, 'max_seconds': max_seconds,
                      'settle': scen.settle, 'bound_events': scen.bound},
           'workers': W, 'states': tot['visited'], 'expanded': tot['expanded'], 'levels': level,
           'complete_states': tot['complete'], 'max_step_reached': tot['max_step'], 'nsteps': len(scen.steps),
           'prunes': tot['prunes'], 'max_events_before_done': tot['max_before'],
           'max_settle_events': tot['max_settle'], 'seconds': round(dt, 1),
           'exhausted': truncated is None and not tot['fails'],
           'fingerprint_collision_probability_approx': tot['visited'] ** 2 / 2.0 ** 65}
    if tot['fails']:
        clause = sorted(tot['fails'])[0]
        res['outcome'] = 'FAIL ' + clause
        res['all_fail_clauses'] = sorted(tot['fails'])
        lines, st = rebuild_trace(model, chain_to(tot['fails'][clause]))
        res['violation'] = st[6][1] if st[6] else None
        res['trace'] = lines
    elif truncated:
        res['outcome'] = 'UNEXPLAINED bound'
        res['truncated_by'] = truncated
    elif tot['complete'] == 0:
        res['outcome'] = 'UNEXPLAINED steps'
    else:
        res['outcome'] = 'PASS'
    if tot['ncviol']:
        res['violations_in_noncompleting_behaviours'] = {}
        for k, f in tot['ncviol'].items():
            lines, st = rebuild_trace(model, chain_to(f))
            res['violations_in_noncompleting_behaviours'][k] = {'why': st[6][1] if st[6] else None, 'trace': lines}
    for q in cmdqs:
        q.put(('stop',))
    for pr in procs:
        pr.join(timeout=5)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('scenario')
    ap.add_argument('variant', choices=['SPEC', 'GATED'])
    ap.add_argument('--maxe', type=int, default=3)
    ap.add_argument('--maxl', type=int, default=3)
    ap.add_argument('--maxm', type=int, default=1)
    ap.add_argument('--maxt', type=int, default=3)
    ap.add_argument('--nodup', action='store_true')
    ap.add_argument('--workers', type=int, default=32)
    ap.add_argument('--max-states', type=int, default=2_000_000_000)
    ap.add_argument('--max-seconds', type=float, default=3600)
    ap.add_argument('--json')
    a = ap.parse_args()
    res = run(a.scenario, a.variant, a.maxe, a.maxl, a.maxm, a.maxt, not a.nodup, a.workers,
              a.max_states, a.max_seconds)
    if a.json:
        with open(a.json, 'w') as f:
            json.dump(res, f, indent=1)
    show = {k: v for k, v in res.items() if k not in ('trace', 'violations_in_noncompleting_behaviours')}
    print(json.dumps(show))
    if 'trace' in res:
        print('violation:', res['violation'])
        print('\n'.join('  ' + x for x in res['trace']))
    for k, v in res.get('violations_in_noncompleting_behaviours', {}).items():
        print('non-completing violation', k, v['why'])


if __name__ == '__main__':
    main()
