#!/usr/bin/python3
"""Run S1..S8 and K1v3 against SPEC and GATED with the reference explorer (fexp), with a ladder of
bounds: the first that exhausts (or FAILs) is the reported outcome; every attempt is recorded.
derives: J1.1, J1.3, J1.4 (driver for run.py)."""
import json, os, subprocess, sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SCEN = [os.path.join(ROOT, 'replay', 'scenarios', 'S%d.yaml' % k) for k in range(1, 9)] + \
       [os.path.join(ROOT, 'tmp', 'replay', 'K1v3.yaml')]
E, T, SETTLE = 3, 3, 2


def ladder(path):
    """Bounds to try in order; k = Elected triggers in the scenario. T_pre: timeouts before every step
    is taken; T: timeouts in all (so T - T_pre after); lost: deliverable replies that may be lost."""
    d = yaml.safe_load(open(path))
    k = sum(1 for s in d['steps'] if s['at'] != 'start' and s['at'].get('event') == 'Elected')
    out = []
    if k + 2 <= T:
        out.append(dict(maxt=k + 2, maxtpre=k + 1, maxlost=1, limit=180))
    out.append(dict(maxt=min(T, k + 1), maxtpre=k, maxlost=1, limit=300))
    out.append(dict(maxt=min(T, k + 1), maxtpre=k, maxlost=0, limit=300))
    out.append(dict(maxt=k, maxtpre=k, maxlost=0, limit=300))
    return out


def main():
    only = sys.argv[1:]
    rows = []
    for path in SCEN:
        nm = os.path.basename(path)[:-5]
        if only and nm not in only:
            continue
        for var in ('SPEC', 'GATED'):
            attempts = []
            for i, b in enumerate(ladder(path)):
                out = os.path.join(HERE, 'results', '%s_%s_%d.json' % (nm, var, i))
                cmd = ['/usr/bin/python3', os.path.join(HERE, 'run.py'), path, var, '--maxe', str(E), '--maxt', str(b['maxt']),
                       '--maxtpre', str(b['maxtpre']), '--maxlost', str(b['maxlost']), '--settle', str(SETTLE),
                       '--workers', '64', '--bits', '31', '--limit', str(b['limit']), '--tag', '_final%d' % i,
                       '--json', out]
                p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                with open(os.path.join(HERE, 'logs', '%s_%s_%d.log' % (nm, var, i)), 'w') as f:
                    f.write(p.stdout)
                r = json.load(open(out))
                attempts.append(r)
                print('%s %s attempt %d %s: %s %s distinct=%s %.0fs' % (nm, var, i, b, r['outcome'],
                      r.get('note'), r.get('distinct'), r.get('seconds', 0)), flush=True)
                if r['outcome'] != 'UNEXPLAINED bound':
                    break
            rows.append({'scenario': nm, 'variant': var, 'final': attempts[-1], 'attempts': attempts})
    json.dump(rows, open(os.path.join(HERE, 'results', 'summary%s.json' % ('_' + '_'.join(only) if only else '')), 'w'), indent=1)
    print('\n| scenario | variant | outcome | bounds E,T,T_pre,J,lost,settle | distinct states | exhausted | s | peak RSS GB |')
    print('|---|---|---|---|---|---|---|---|')
    for r in rows:
        f = r['final']
        b = f['bounds']
        print('| %s | %s | %s | %d,%d,%d,%d,%d,%d | %s | %s | %.0f | %.1f |' % (
            r['scenario'], r['variant'], f['outcome'], b['maxe'], b['maxt'], b['maxtpre'], b['maxj'], b['maxlost'],
            b['settle'], f.get('distinct'), f.get('exhausted'), f.get('seconds', 0), (f.get('peak_rss_kb') or 0) / 1048576))


if __name__ == '__main__':
    main()
