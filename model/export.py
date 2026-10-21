#!/usr/bin/env python3
# derives: C1.1, C1.2, C1.3, C2.1, C2.2, F1.1, F1.2, F1.3 (trace exporter: TLC trace -> observe/schema.md records, incl. v2 addendum)
"""Turn a TLC trace (witness or counterexample) into observe/schema.md records.

Usage: export.py <tlc-output.txt> <schedule.json> <out.jsonl> <run-id>

Reads the `lastEv` variable of every state in the first trace printed by TLC.
Each observable event becomes one JSON line; `Fault` steps are emitted from
proc "env". Internal protocol steps (elections, deliveries) are not observable
events and are not emitted. Lines are written in trace order; `seq` is per process.

Exit status: 0 if every WriteAccept/WriteReject can be traced to a Grant and its
grantor_term (the schema's provenance question), 3 if not, 4 if no trace found.
"""
import json
import re
import sys


# ---------------------------------------------------------------- TLA+ values
# derives: C1.1, C1.2, C1.3 -- a small parser for the values TLC prints
class P:
    def __init__(self, s):
        self.s, self.i = s, 0

    def ws(self):
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1

    def peek(self, t):
        self.ws()
        return self.s.startswith(t, self.i)

    def eat(self, t):
        self.ws()
        if not self.s.startswith(t, self.i):
            raise ValueError(f"expected {t!r} at {self.s[self.i:self.i + 40]!r}")
        self.i += len(t)

    def value(self):
        return self.atom()

    def atom(self):
        self.ws()
        c = self.s[self.i]
        if c == '"':
            j = self.i + 1
            out = []
            while self.s[j] != '"':
                if self.s[j] == "\\":
                    j += 1
                out.append(self.s[j])
                j += 1
            self.i = j + 1
            return "".join(out)
        if c == "[":
            self.eat("[")
            rec = {}
            if self.peek("]"):
                self.eat("]")
                return rec
            while True:
                self.ws()
                m = re.compile(r"[A-Za-z_][A-Za-z0-9_]*").match(self.s, self.i)
                key = m.group(0)
                self.i = m.end()
                self.eat("|->")
                rec[key] = self.value()
                if self.peek(","):
                    self.eat(",")
                    continue
                self.eat("]")
                return rec
        if c == "{":
            self.eat("{")
            items = []
            if not self.peek("}"):
                while True:
                    items.append(self.value())
                    if self.peek(","):
                        self.eat(",")
                        continue
                    break
            self.eat("}")
            return ("set", items)
        if self.s.startswith("<<", self.i):
            self.eat("<<")
            items = []
            if not self.peek(">>"):
                while True:
                    items.append(self.value())
                    if self.peek(","):
                        self.eat(",")
                        continue
                    break
            self.eat(">>")
            return items
        if c == "(":
            self.eat("(")
            fn = {}
            while True:
                k = self.value()
                self.eat(":>")
                fn[json.dumps(k)] = self.value()
                if self.peek("@@"):
                    self.eat("@@")
                    continue
                break
            self.eat(")")
            return fn
        m = re.compile(r"-?\d+").match(self.s, self.i)
        if m:
            self.i = m.end()
            return int(m.group(0))
        for lit, val in (("TRUE", True), ("FALSE", False)):
            if self.s.startswith(lit, self.i):
                self.i += len(lit)
                return val
        raise ValueError(f"cannot parse at {self.s[self.i:self.i + 40]!r}")


def parse_tla(s):
    return P(s).value()


# ---------------------------------------------------------------- TLC output
# derives: C1.1, C1.2, C1.3 -- split TLC's printed trace into states
def trace_states(text):
    """Return (states, loop) where states is a list of {var: raw} and loop is the
    1-based state a liveness lasso returns to (or 'stutter'), else None."""
    states, cur, var, loop = [], None, None, None
    for line in text.splitlines():
        m = re.match(r"^State \d+: Back to state:? ?(\d+)?", line)
        if m:
            loop = int(m.group(1)) if m.group(1) else "back"
            cur = None
            continue
        if re.match(r"^State \d+: Stuttering", line):
            loop = "stutter"
            cur = None
            continue
        if re.match(r"^State \d+:", line):
            cur = {}
            states.append(cur)
            var = None
            continue
        if cur is None:
            continue
        m = re.match(r"^/\\ (\w+) = (.*)$", line)
        if m:
            var = m.group(1)
            cur[var] = m.group(2)
        elif line.strip() == "":
            var = None
        elif var is not None:
            cur[var] += " " + line.strip()
    return states, loop


# ---------------------------------------------------------------- records
CONTRACT_FIELDS = {
    "Request": ["client", "key"],
    "Grant": ["client", "key", "token", "lifetime", "grantor_term"],
    "WriteAttempt": ["client", "key", "token", "value", "grantor_term"],
    "WriteAccept": ["key", "token", "highest_before", "grantor_term"],
    "WriteReject": ["key", "token", "highest_before", "grantor_term"],
    "WriteAck": ["client", "key", "token", "outcome"],
    # derives: C2.1, C2.2; observe v2 addendum -- read events, fields as their write counterparts
    "ReadAttempt": ["client", "key", "token", "grantor_term"],
    "ReadAccept": ["key", "token", "highest_before", "value", "grantor_term"],
    "ReadReject": ["key", "token", "highest_before", "grantor_term"],
    "ReadAck": ["client", "key", "token", "outcome"],   # + value when served
}


def export(tlc_text, sched, run):
    # derives: C1.1, C1.2, C1.3, F1.1, F1.2, F1.3
    states, loop = trace_states(tlc_text)
    if not states:
        return None, ["no trace in TLC output"], loop
    procs = sched["processes"]
    allp = set(procs["lease"]) | set(procs["clients"]) | set(procs["storage"])
    storage = procs["storage"][0]
    seqs, out = {}, []
    last = {}  # index for causes
    problems = []

    def emit(proc, event, fields, causes):
        seqs[proc] = seqs.get(proc, 0) + 1
        rec = {"proc": proc, "seq": seqs[proc], "event": event}
        rec.update(fields)
        rec["causes"] = causes
        rec["run"] = run
        rec["side"] = "model"
        out.append(rec)
        return {"proc": proc, "seq": seqs[proc]}

    for st in states:
        if "lastEv" not in st:
            continue
        ev = parse_tla(st["lastEv"])
        e = ev.get("event")
        if e in ("Init", "Internal"):
            continue
        if e == "Fault":
            f = {"cell": ev["cell"]}
            act = ev["action"]
            if act == "partition":
                a = sorted(ev["sideA"][1])
                f["partition"] = [a, sorted(allp - set(a))]
            elif act == "heal":
                f["heal"] = True
            else:
                f[act] = ev["target"]
            emit("env", "Fault", f, [])
            continue
        fields = {k: ev[k] for k in CONTRACT_FIELDS[e]}
        if e == "ReadAck" and ev["outcome"] == "served":
            fields["value"] = ev["value"]   # derives: C2.2 -- value only on a served ReadAck
        if e == "Request":
            ref = emit(ev["client"], e, fields, [])
            last[("req", ev["client"])] = ref
        elif e == "Grant":
            causes = [last[("req", ev["client"])]] if ("req", ev["client"]) in last else []
            ref = emit(ev["node"], e, fields, causes)
            last[("grant", ev["token"], ev["grantor_term"])] = ref
        elif e == "WriteAttempt":
            g = last.get(("grant", ev["token"], ev["grantor_term"]))
            ref = emit(ev["client"], e, fields, [g] if g else [])
            last[("att", ev["client"], ev["token"], ev["value"])] = (ref, g)
        elif e in ("WriteAccept", "WriteReject"):
            a = last.get(("att", ev["client"], ev["token"], ev["value"]))
            ref = emit(storage, e, fields, [a[0]] if a else [])
            last[("dec", ev["client"], ev["token"], ev["value"])] = ref
            if not a or not a[1]:
                problems.append(f"{e} seq {ref['seq']} (token {ev['token']}) has no traceable Grant")
        elif e == "ReadAttempt":
            # derives: C2.1; observe v2 -- a ReadAttempt names the Grant whose token it uses
            g = last.get(("grant", ev["token"], ev["grantor_term"]))
            ref = emit(ev["client"], e, fields, [g] if g else [])
            last[("ratt", ev["client"], ev["rid"])] = (ref, g)
        elif e in ("ReadAccept", "ReadReject"):
            # derives: C2.1, C2.2; observe v2 -- a read decision names the ReadAttempt
            a = last.get(("ratt", ev["client"], ev["rid"]))
            ref = emit(storage, e, fields, [a[0]] if a else [])
            last[("rdec", ev["client"], ev["rid"])] = ref
            if not a or not a[1]:
                problems.append(f"{e} seq {ref['seq']} (token {ev['token']}) has no traceable Grant")
        elif e == "ReadAck":
            # derives: C2.2; observe v2 -- a ReadAck names the storage decision
            d = last.get(("rdec", ev["client"], ev["rid"]))
            ref = emit(ev["client"], e, fields, [d] if d else [])
            if not d and ev["outcome"] == "served":
                problems.append(f"ReadAck served at {ref} has no storage decision")
        elif e == "WriteAck":
            d = last.get(("dec", ev["client"], ev["token"], ev["value"]))
            ref = emit(ev["client"], e, fields, [d] if d else [])
            if not d and ev["outcome"] == "accepted":
                problems.append(f"WriteAck accepted at {ref} has no storage decision")
    return out, problems, loop


def main(argv):
    if len(argv) != 5:
        print(__doc__, file=sys.stderr)
        return 2
    text = open(argv[1]).read()
    sched = json.load(open(argv[2]))
    recs, problems, loop = export(text, sched, argv[4])
    if recs is None:
        print("export: " + problems[0], file=sys.stderr)
        return 4
    with open(argv[3], "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    if len([r for r in recs if r["proc"] != "env"]) > sched.get("bound", 200):
        print(f"export: trace exceeds bound of {sched['bound']} events", file=sys.stderr)
    if loop is not None:
        print(f"export: liveness lasso, loops back to {loop}", file=sys.stderr)
    for p in problems:
        print("export: provenance: " + p, file=sys.stderr)
    return 3 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
