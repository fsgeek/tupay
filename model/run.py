#!/usr/bin/env python3
# derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3; format v2 E1, E2 (checking runs for P1-P12 and M1)
"""Driver behind model/run.sh.

  run.py <schedule-name>   check the model on one schedule; print PASS | FAIL <inv> | UNEXPLAINED <why>
  run.py --mutations       regenerate and check every mutation on its pair's schedule;
                           every one must print FAIL <the pair's clause>
  run.py --all             every schedule, then every mutation
"""
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WORK = HERE / ".work"
OBS = HERE / "observe"
JAR = os.environ.get("TLA2TOOLS", "/home/tony/projects/tlaplus/tla2tools.jar")
sys.path.insert(0, str(HERE))
import compile as compiler  # noqa: E402
import export as exporter  # noqa: E402
import mutate  # noqa: E402

# derives: C1.1-C1.4, C2.1, C2.2, F2.1, F2.2 -- every shared schedule (P13-P18 added for contract v2, P19-P30 for failure model v2)
ORDER = [f"P{i}" for i in range(1, 31)] + ["false-suspicion-v1"]


def find_schedule(name):
    # derives: F1.1, F1.2, F1.3; format v2 "Schedules live in testbed/schedules/<name>.yaml and
    # nowhere else" -- model/schedules/ (M1) is history and is never run
    p = ROOT / "testbed" / "schedules" / f"{name}.yaml"
    return p if p.exists() else None


def tlc(dirp, cfg):
    # derives: C1.1, C1.2, C1.3, C1.4
    jtmp = WORK / "jtmp"
    jtmp.mkdir(parents=True, exist_ok=True)
    cmd = ["java", f"-Djava.io.tmpdir={jtmp}", "-XX:+UseParallelGC", "-cp", JAR, "tlc2.TLC",
           "-deadlock", "-cleanup", "-workers", os.environ.get("TLC_WORKERS", "4"),
           "-metadir", str(dirp / "states"), "-config", cfg, "MC.tla"]
    r = subprocess.run(cmd, cwd=dirp, capture_output=True, text=True)
    out = r.stdout + r.stderr
    (dirp / (cfg.replace(".cfg", "") + ".out")).write_text(out)
    return out


def verdict(out):
    # derives: C1.1, C1.2, C1.3, C1.4 -- classify TLC's output
    m = re.search(r"Invariant (\w+) is violated", out)
    if m and m.group(1) == "TermHeadroom":
        return "UNEXPLAINED", "MaxTerm bound reached; raise it before reading this run"
    if m:
        return "FAIL", m.group(1)
    if "Temporal properties were violated" in out:
        return "FAIL", "C1_4"
    if "Model checking completed. No error has been found." in out:
        return "PASS", None
    err = re.search(r"^Error: (.*)$", out, re.M)
    return "UNEXPLAINED", ("TLC: " + err.group(1)) if err else "TLC produced no verdict"


def stats(out):
    m = re.search(r"([\d,]+) states generated, ([\d,]+) distinct states found", out)
    d = re.search(r"depth of the complete state graph search is (\d+)", out)
    return (m.group(2) if m else "?"), (d.group(1) if d else "?")


def check(name, lease=None, run_id=None, quiet=False):
    # derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
    path = find_schedule(name)
    if path is None:
        return f"UNEXPLAINED no schedule named {name}"
    run_id = run_id or path.stem
    dirp = WORK / run_id
    try:
        meta = compiler.compile_schedule(path, dirp, lease or (HERE / "Lease.tla"))
    except compiler.ScheduleError as e:
        return f"UNEXPLAINED schedule rejected: {e}"
    out = tlc(dirp, "MC.cfg")
    v, inv = verdict(out)
    distinct, depth = stats(out)
    OBS.mkdir(exist_ok=True)
    obs = OBS / f"{run_id}.jsonl"
    note = ""
    if v == "PASS":
        # observe file from a witness that completes the schedule
        wout = tlc(dirp, "Witness.cfg")
        if "Invariant NotEnded is violated" not in wout:
            wout = tlc(dirp, "Done.cfg")
            if "Invariant NotDone is violated" not in wout:
                return f"UNEXPLAINED end unreachable ({distinct} states, no violation witnessed)"
            note = " (witness not quiescent)"
        trace = wout
    elif v == "FAIL":
        trace = out
    else:
        return f"UNEXPLAINED {inv}"
    recs, problems, loop = exporter.export(trace, {**meta, "processes": meta["processes"]}, run_id)
    if recs is None:
        return f"UNEXPLAINED exporter found no trace"
    with open(obs, "w") as f:
        for r in recs:
            f.write(__import__("json").dumps(r) + "\n")
    if not quiet:
        print(f"# {run_id}: {distinct} distinct states, depth {depth}, max_term {meta['max_term']},"
              f" observe -> {obs.relative_to(ROOT)}{note}"
              + (f", liveness lasso ({loop})" if loop else ""), file=sys.stderr)
    if v == "PASS" and problems:
        return "UNEXPLAINED provenance: " + "; ".join(problems)
    return "PASS" if v == "PASS" else f"FAIL {inv}"


def mutations():
    # derives: P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11, P12
    mutate.main()
    ok = True
    for pair, _, expected, desc, _ in mutate.MUTATIONS:
        res = check(pair, lease=HERE / "mutations" / pair / "Lease.tla",
                    run_id=f"{pair}-mutation")
        good = res == f"FAIL {expected}"
        ok &= good
        print(f"{pair} mutation: {res}" + ("" if good else f"   <-- expected FAIL {expected}"))
    return ok


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    if argv[1] == "--mutations":
        return 0 if mutations() else 1
    if argv[1] == "--all":
        ok = True
        for n in ORDER:
            res = check(n)
            print(f"{n}: {res}")
            ok &= res == "PASS"
        ok &= mutations()
        return 0 if ok else 1
    res = check(argv[1])
    print(res)
    return 0 if res == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
