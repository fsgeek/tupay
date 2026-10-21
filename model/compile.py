#!/usr/bin/env python3
# derives: F1.1, F1.2, F1.3, F2.1, F2.2, C2.1, C2.2; format v4 (cut, drop, L1, L2); v3 (read); v2.1 T1, A1; v2 T2, T3, A2, E1, E2 (schedule compiler)
"""Compile a fault schedule (testbed/schedule-format.md v2) into a TLC model.

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

# derives: F1.1, F1.2, F1.3, F2.1, F2.2 -- the only fault actions the failure model contains, by cell
FAULTS = {
    "F1.1": {"crash", "restart"},
    "F1.2": {"partition", "heal"},
    "F1.3": {"pause", "resume"},
    "F2.1": {"cut", "heal"},     # derives: F2.1; format v4 cut, L2 (a heal under any cell restores every link)
    "F2.2": {"drop", "heal"},    # derives: F2.2; format v4 drop, L2
}
# derives: C1.1, C1.2, C1.3 -- observable events of contract/v1.md, plus `start`
EVENTS = {"start", "Request", "Grant", "WriteAttempt", "WriteAccept", "WriteReject", "WriteAck",
          # derives: C2.1, C2.2; format v3 -- contract v2's read events
          "ReadAttempt", "ReadAccept", "ReadReject", "ReadAck"}
# derives: C1.1, C1.2, C1.3 -- fields each event carries (filters must name one of these)
EVENT_FIELDS = {
    "Request": {"client", "key"},
    "Grant": {"client", "key", "token", "lifetime", "grantor_term"},
    "WriteAttempt": {"client", "key", "token", "value", "grantor_term"},
    "WriteAccept": {"key", "token", "highest_before", "grantor_term"},
    "WriteReject": {"key", "token", "highest_before", "grantor_term"},
    "WriteAck": {"client", "key", "token", "outcome"},
    # derives: C2.1, C2.2; format v3
    "ReadAttempt": {"client", "key", "token", "grantor_term"},
    "ReadAccept": {"key", "token", "highest_before", "grantor_term", "value"},
    "ReadReject": {"key", "token", "highest_before", "grantor_term"},
    "ReadAck": {"client", "key", "token", "outcome", "value"},
}
# derives: C1.3, C2.2; format v3 -- outcome values per ack event
OUTCOMES = {"WriteAck": ("accepted", "rejected"), "ReadAck": ("served", "rejected")}
ALIASES = {"grantor", "holder", "rest", "non-grantor"}   # non-grantor: format v2.1 A1


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
        if k == "outcome" and v not in OUTCOMES[ev]:
            raise ScheduleError(f"{ev} outcome must be one of {OUTCOMES[ev]}, got {v!r}")
        out[k] = v
    return out


def proc_name(x, procs, allowed, aliases=("grantor", "holder")):
    # derives: F1.1, F1.2, F1.3; format v2 A1 -- a process name, or an alias where one may stand
    if x in aliases or x in allowed:
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
            raise ScheduleError(f"cell {cell!r} is not in failure-model/v2.md")
        keys = set(d) - {"cell"}
        if len(keys) != 1:
            raise ScheduleError(f"fault step must name exactly one action: {d!r}")
        (verb,) = keys
        if verb not in FAULTS[cell]:
            raise ScheduleError(f"action {verb!r} does not belong to cell {cell}")
        arg = d[verb]
        if verb in ("crash", "restart"):
            # derives: F1.1; format v2.1 A1 -- non-grantor is a lease-node selector
            return {"kind": verb, "p": proc_name(arg, procs, allp, ("grantor", "holder", "non-grantor"))}
        if verb in ("pause", "resume"):
            if arg == "grantor" or arg in set(procs["lease"]) | set(procs["storage"]):
                raise ScheduleError("A2: only clients can be paused or resumed")
            return {"kind": verb, "p": proc_name(arg, procs, clients, ("holder",))}
        if verb == "heal":
            if arg is not True:
                raise ScheduleError("heal must be `heal: true`")
            # derives: F1.2, F2.1, F2.2; format v4 L2 -- every heal restores every link; the cell
            # it names is kept only for the Fault record
            return {"kind": "heal", "cell": cell}
        if verb in ("cut", "drop"):
            # derives: F2.1 (cut), F2.2 (drop); format v4 L1 -- a list of pairs of process names or
            # the selectors grantor, holder, non-grantor; `rest` is not allowed in a link
            if not (isinstance(arg, list) and arg):
                raise ScheduleError(f"{verb} needs a non-empty list of pairs")
            pairs = []
            for e in arg:
                if not (isinstance(e, list) and len(e) == 2):
                    raise ScheduleError(f"L1: each {verb} entry is a pair, got {e!r}")
                for x in e:
                    if x == "rest":
                        raise ScheduleError("L1: `rest` is not allowed in a link")
                    proc_name(x, procs, allp, ("grantor", "holder", "non-grantor"))
                pairs.append((e[0], e[1]))
            return {"kind": verb, "l": pairs, "cell": cell}
        if verb == "partition":
            if not (isinstance(arg, list) and len(arg) == 2):
                raise ScheduleError("partition needs exactly two sides (complete bipartition)")
            sides = []
            for side in arg:
                if not isinstance(side, list) or not side:
                    raise ScheduleError(f"bad partition side {side!r}")
                for x in side:
                    if x != "rest":
                        proc_name(x, procs, allp, ("grantor", "holder", "non-grantor"))
                sides.append(set(side))
            if "rest" in sides[0] and "rest" in sides[1]:
                raise ScheduleError("`rest` may appear on one side only")
            if "rest" not in sides[0] | sides[1]:
                named = {x for x in sides[0] | sides[1] if x not in ALIASES}
                if not (ALIASES & (sides[0] | sides[1])) and named != allp:
                    raise ScheduleError("partition without `rest` must name every process")
            return {"kind": "partition", "a": sides[0], "b": sides[1]}
    if set(d) - {"request", "write", "read", "value", "token"}:
        raise ScheduleError(f"action not in schedule format v1: {d!r}")
    if "request" in d:
        if set(d) != {"request"}:
            raise ScheduleError(f"bad request {d!r}")
        return {"kind": "request", "p": proc_name(d["request"], procs, clients, ("holder",))}
    if "read" in d:
        # derives: C2.1, C2.2; format v3 -- read with the current or a stale token
        if set(d) - {"read", "token"}:
            raise ScheduleError(f"bad read {d!r}")
        tokspec = d.get("token")
        if tokspec not in (None, "stale"):
            raise ScheduleError(f"read token must be omitted or `stale`, got {tokspec!r}")
        return {"kind": "read", "p": proc_name(d["read"], procs, clients, ("holder",)),
                "stale": tokspec == "stale"}
    if "write" in d:
        if "value" not in d:
            raise ScheduleError("write needs a value")
        tokspec = d.get("token")
        if tokspec not in (None, "stale"):
            raise ScheduleError(f"write token must be omitted or `stale`, got {tokspec!r}")
        return {"kind": "write", "p": proc_name(d["write"], procs, clients, ("holder",)),
                "v": str(d["value"]), "stale": tokspec == "stale"}
    raise ScheduleError(f"unknown action {d!r}")


def static_checks(steps, procs):
    # derives: F1.1, F1.3; format v2 A1, A2 -- reject what can be decided without running:
    # an alias used before any Grant can have occurred (no earlier request step), and
    # crash/restart/pause/resume of a process in the wrong state. An alias target is
    # tracked as "maybe" for every process it could denote; the model's own guards make
    # a step that is illegal at run time wait rather than act.
    lease, clients = set(procs["lease"]), set(procs["clients"])
    allp = lease | clients | set(procs["storage"])
    down, maybe_down = set(), set()          # crashed for sure / possibly crashed
    paused, maybe_paused = set(), set()
    requested = False
    ng_down = False
    for i, (a, _) in enumerate(steps, 1):
        names = {a.get("p")} | set(a.get("a", ())) | set(a.get("b", ())) \
            | {x for e in a.get("l", ()) for x in e}   # derives: F2.1, F2.2; format v4 L1 (A1 applies)
        if names & {"grantor", "holder", "non-grantor"} and not requested:
            raise ScheduleError(f"A1: step {i} uses grantor/holder/non-grantor before any Grant can have occurred")
        k, p = a["kind"], a.get("p")
        # derives: F1.1; format v2.2 A1 (restart: non-grantor is the node the most recent
        # crash: non-grantor crashed; rejected without an earlier one), v2.1 A1, v2 A2 -- restart: non-grantor needs an earlier,
        # not yet restarted, crash: non-grantor; crash: non-grantor is always of an up node
        if p == "non-grantor":
            if k == "crash":
                ng_down = True
                maybe_down |= lease
            elif k == "restart":
                if not ng_down:
                    raise ScheduleError(f"A2: step {i} restarts non-grantor, but no crash: non-grantor is outstanding")
                ng_down = False
            continue
        if k == "request":
            requested = True
        if k in ("crash", "restart"):
            cands = lease if p == "grantor" else clients if p == "holder" else {p}
            if k == "crash":
                if len(cands) == 1 and cands <= down:
                    raise ScheduleError(f"A2: step {i} crashes {p}, already crashed")
                if len(cands) == 1:
                    down |= cands
                    if p in clients:
                        paused.discard(p)
                        maybe_paused.discard(p)
                else:
                    maybe_down |= cands
            else:
                if not (cands & (down | maybe_down)):
                    raise ScheduleError(f"A2: step {i} restarts {p}, which is not crashed")
                if len(cands) == 1:
                    down -= cands
                    maybe_down -= cands
        if k in ("pause", "resume"):
            cands = clients if p == "holder" else {p}
            if k == "pause":
                if len(cands) == 1 and cands <= paused:
                    raise ScheduleError(f"A2: step {i} pauses {p}, already paused")
                if len(cands) == 1:
                    paused |= cands
                else:
                    maybe_paused |= cands
            else:
                if not (cands & (paused | maybe_paused)):
                    raise ScheduleError(f"A2: step {i} resumes {p}, which is running")
                if len(cands) == 1:
                    paused -= cands
                    maybe_paused -= cands
    return True


def tla_step(st, trig):
    # derives: F1.1, F1.2, F1.3, F2.1, F2.2 -- every step record gets the same fields (TLC compares
    # them); `l` is the link list of a cut/drop (a set of <<x, y>> pairs), `cell` names the heal's cell
    rec = {"kind": st["kind"], "p": st.get("p", "none"), "v": st.get("v", "none"),
           "stale": st.get("stale", False), "a": set(st.get("a", set())),
           "b": set(st.get("b", set())), "trig": trig, "cell": st.get("cell", "none")}
    links = "{" + ", ".join(sorted(f"<<{tla(x)}, {tla(y)}>>" for x, y in st.get("l", ()))) + "}"
    return tla(rec)[:-1] + f", l |-> {links}]"


def compile_schedule(path, outdir, lease):
    # derives: F1.1, F1.2, F1.3, F2.1, F2.2
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
    # derives: format v2 E1 -- `quiescent` or an event trigger
    end = {"event": "quiescent"} if doc["end"] == "quiescent" else trigger(doc["end"], procs)
    static_checks(steps, procs)
    bound = int((doc.get("bound") or {}).get("events", 200))
    # derives: C1.1, C1.4, F2.1, F2.2 -- cut and drop count as fault steps for the term bound
    nfault = sum(1 for a, _ in steps
                 if a["kind"] in ("crash", "partition", "restart", "heal", "cut", "drop"))
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
        "\\* derives: F1.1, F1.2, F1.3, F2.1, F2.2",
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
        "\\* derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2\n" + consts +
        "INVARIANT TypeOK C1_1 C1_2 C1_3 C2_1 C2_2 TermHeadroom\nPROPERTY C1_4\n")
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
