#!/usr/bin/env python3
# derives: F1.1, F1.2, F1.3 (schedule compiler: testbed/schedule-format.md -> TLC configuration)
"""Compile a fault schedule (testbed/schedule-format.md v1) into a TLC model.

Usage: compile.py <schedule.yaml> <outdir> [--lease <Lease.tla>]

Writes into <outdir>:
  MC.tla        EXTENDS Lease; defines the constants (processes, Steps, EndTrig, bounds)
  MC.cfg        safety invariants C1_1..C1_3 and liveness C1_4 (the checking run)
  Witness.cfg   invariant NotEnded: a violation is a trace that completes the schedule
  Done.cfg      invariant NotDone: weaker witness (end trigger fired, not quiescent)
  schedule.json the parsed schedule, for the exporter

The environment actions in the model are reachable only through the compiled Steps
sequence, so each fault is enabled exactly where the schedule enables it.
A schedule naming an action outside the failure model is rejected (exit 2).
"""
import json
import shutil
import sys
from pathlib import Path

import yaml

# derives: F1.1, F1.2, F1.3 -- the only fault actions the failure model contains, by cell
FAULTS = {
    "F1.1": {"crash", "restart"},
    "F1.2": {"partition", "heal"},
    "F1.3": {"pause", "resume"},
}
# derives: C1.1, C1.2, C1.3 -- observable events of contract/v1.md, plus `start`
EVENTS = {"start", "Request", "Grant", "WriteAttempt", "WriteAccept", "WriteReject", "WriteAck"}
# derives: C1.1, C1.2, C1.3 -- fields each event carries (filters must name one of these)
EVENT_FIELDS = {
    "Request": {"client", "key"},
    "Grant": {"client", "key", "token", "lifetime", "grantor_term"},
    "WriteAttempt": {"client", "key", "token", "value", "grantor_term"},
    "WriteAccept": {"key", "token", "highest_before", "grantor_term"},
    "WriteReject": {"key", "token", "highest_before", "grantor_term"},
    "WriteAck": {"client", "key", "token", "outcome"},
}
ALIASES = {"grantor", "holder", "rest"}


class ScheduleError(Exception):
    pass


def tla(v):
    # derives: F1.1, F1.2, F1.3 -- render a YAML scalar/collection as a TLA+ value
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return '"' + v.replace('"', '\\"') + '"'
    if isinstance(v, (set, frozenset)):
        return "{" + ", ".join(sorted(tla(x) for x in v)) + "}"
    if isinstance(v, list):
        return "<<" + ", ".join(tla(x) for x in v) + ">>"
    if isinstance(v, dict):
        return "[" + ", ".join(f"{k} |-> {tla(x)}" for k, x in v.items()) + "]"
    raise ScheduleError(f"cannot render {v!r}")


def trigger(t, procs):
    # derives: F1.1, F1.2, F1.3 -- a trigger is `start` or {event: E, field: value, ...}
    if t == "start":
        return {"event": "start"}
    if not isinstance(t, dict) or "event" not in t:
        raise ScheduleError(f"bad trigger {t!r}")
    ev = t["event"]
    if ev not in EVENTS or ev == "start":
        raise ScheduleError(f"trigger names unknown event {ev!r}")
    out = {"event": ev}
    for k, v in t.items():
        if k == "event":
            continue
        if k not in EVENT_FIELDS[ev]:
            raise ScheduleError(f"event {ev} has no field {k!r}")
        if k == "client" and v not in procs["clients"]:
            raise ScheduleError(f"unknown client {v!r}")
        if k == "outcome" and v not in ("accepted", "rejected"):
            raise ScheduleError(f"outcome must be accepted|rejected, got {v!r}")
        out[k] = v
    return out


def proc_name(x, procs, allowed):
    # derives: F1.1, F1.2, F1.3
    if x in ALIASES - {"rest"} or x in allowed:
        return x
    raise ScheduleError(f"unknown or ill-typed process {x!r}")


def action(d, procs):
    # derives: C1.2, C1.4, F1.1, F1.2, F1.3 -- one step's action; rejects anything not in the model
    if not isinstance(d, dict):
        raise ScheduleError(f"bad action {d!r}")
    allp = set(procs["lease"]) | set(procs["clients"]) | set(procs["storage"])
    clients = set(procs["clients"])
    if "cell" in d:
        cell = d["cell"]
        if cell not in FAULTS:
            raise ScheduleError(f"cell {cell!r} is not in failure-model/v1.md")
        keys = set(d) - {"cell"}
        if len(keys) != 1:
            raise ScheduleError(f"fault step must name exactly one action: {d!r}")
        (verb,) = keys
        if verb not in FAULTS[cell]:
            raise ScheduleError(f"action {verb!r} does not belong to cell {cell}")
        arg = d[verb]
        if verb in ("crash", "restart"):
            return {"kind": verb, "p": proc_name(arg, procs, allp)}
        if verb in ("pause", "resume"):
            if arg == "grantor":
                raise ScheduleError("only clients can be paused (F1.3 is a holder pause)")
            return {"kind": verb, "p": proc_name(arg, procs, clients)}
        if verb == "heal":
            if arg is not True:
                raise ScheduleError("heal must be `heal: true`")
            return {"kind": "heal"}
        if verb == "partition":
            if not (isinstance(arg, list) and len(arg) == 2):
                raise ScheduleError("partition needs exactly two sides (complete bipartition)")
            sides = []
            for side in arg:
                if not isinstance(side, list) or not side:
                    raise ScheduleError(f"bad partition side {side!r}")
                for x in side:
                    if x != "rest":
                        proc_name(x, procs, allp)
                sides.append(set(side))
            if "rest" in sides[0] and "rest" in sides[1]:
                raise ScheduleError("`rest` may appear on one side only")
            if "rest" not in sides[0] | sides[1]:
                named = {x for x in sides[0] | sides[1] if x not in ALIASES}
                if not (ALIASES & (sides[0] | sides[1])) and named != allp:
                    raise ScheduleError("partition without `rest` must name every process")
            return {"kind": "partition", "a": sides[0], "b": sides[1]}
    if set(d) - {"request", "write", "value", "token"}:
        raise ScheduleError(f"action not in schedule format v1: {d!r}")
    if "request" in d:
        if set(d) != {"request"}:
            raise ScheduleError(f"bad request {d!r}")
        return {"kind": "request", "p": proc_name(d["request"], procs, clients)}
    if "write" in d:
        if "value" not in d:
            raise ScheduleError("write needs a value")
        tokspec = d.get("token")
        if tokspec not in (None, "stale"):
            raise ScheduleError(f"write token must be omitted or `stale`, got {tokspec!r}")
        return {"kind": "write", "p": proc_name(d["write"], procs, clients),
                "v": str(d["value"]), "stale": tokspec == "stale"}
    raise ScheduleError(f"unknown action {d!r}")


def tla_step(st, trig):
    # derives: F1.1, F1.2, F1.3 -- every step record gets the same fields (TLC compares them)
    rec = {"kind": st["kind"], "p": st.get("p", "none"), "v": st.get("v", "none"),
           "stale": st.get("stale", False), "a": set(st.get("a", set())),
           "b": set(st.get("b", set())), "trig": trig}
    return tla(rec)


def compile_schedule(path, outdir, lease):
    # derives: F1.1, F1.2, F1.3
    doc = yaml.safe_load(Path(path).read_text())
    for k in ("schedule", "processes", "steps", "end"):
        if k not in doc:
            raise ScheduleError(f"missing `{k}`")
    procs = doc["processes"]
    if len(procs.get("lease", [])) != 3 or len(procs.get("clients", [])) != 2 \
            or len(procs.get("storage", [])) != 1:
        raise ScheduleError("model is fixed at 3 lease nodes, 2 clients, 1 storage")
    steps = []
    for i, s in enumerate(doc["steps"], 1):
        if set(s) != {"at", "do"}:
            raise ScheduleError(f"step {i}: needs exactly `at` and `do`")
        steps.append((action(s["do"], procs), trigger(s["at"], procs)))
    end = trigger(doc["end"], procs)
    bound = int((doc.get("bound") or {}).get("events", 200))
    nfault = sum(1 for a, _ in steps if a["kind"] in ("crash", "partition", "restart", "heal"))
    max_term = 2 + 2 * nfault          # elections happen only when no reachable leader exists
    max_dups = 1

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    shutil.copy(lease, outdir / "Lease.tla")
    lines = [
        "---- MODULE MC ----",
        f"\\* derives: {', '.join(map(str, doc.get('derives', [])))} -- compiled from {Path(path).name}",
        "EXTENDS Lease",
        "\\* derives: C1.1, C1.4",
        f"MCNodes == {tla(set(procs['lease']))}",
        "\\* derives: C1.2, C1.3, C1.4",
        f"MCClients == {tla(set(procs['clients']))}",
        "\\* derives: C1.2, C1.3",
        f"MCStore == {tla(procs['storage'][0])}",
        "\\* derives: F1.1, F1.2, F1.3",
        "MCSteps == <<",
        ",\n".join("    " + tla_step(a, t) for a, t in steps),
        ">>",
        "\\* derives: F1.1, F1.2, F1.3",
        f"MCEnd == {tla(end)}",
        "====",
    ]
    (outdir / "MC.tla").write_text("\n".join(lines) + "\n")
    consts = (
        "CONSTANTS\n"
        "  Nodes <- MCNodes\n  Clients <- MCClients\n  Store <- MCStore\n"
        '  Key = "k"\n  Lifetime = 1\n  Steps <- MCSteps\n  EndTrig <- MCEnd\n'
        f"  MaxTerm = {max_term}\n  MaxDups = {max_dups}\n"
        "SPECIFICATION Spec\n"
    )
    (outdir / "MC.cfg").write_text(
        "\\* derives: C1.1, C1.2, C1.3, C1.4\n" + consts +
        "INVARIANT TypeOK C1_1 C1_2 C1_3 TermHeadroom\nPROPERTY C1_4\n")
    (outdir / "Witness.cfg").write_text(
        "\\* derives: F1.1, F1.2, F1.3\n" + consts + "INVARIANT NotEnded\n")
    (outdir / "Done.cfg").write_text(
        "\\* derives: F1.1, F1.2, F1.3\n" + consts + "INVARIANT NotDone\n")
    meta = {"schedule": doc["schedule"], "derives": doc.get("derives", []),
            "processes": procs, "bound": bound, "max_term": max_term, "max_dups": max_dups,
            "steps": [{"do": s["do"], "at": s["at"]} for s in doc["steps"]], "end": doc["end"]}
    (outdir / "schedule.json").write_text(json.dumps(meta, indent=1, default=list))
    return meta


def main(argv):
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    lease = Path(__file__).with_name("Lease.tla")
    if "--lease" in argv:
        lease = Path(argv[argv.index("--lease") + 1])
    try:
        compile_schedule(argv[1], argv[2], lease)
    except ScheduleError as e:
        print(f"schedule rejected: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
