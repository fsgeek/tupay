#!/usr/bin/env python3
"""Synthetic traces for observe/decision_replay.py (schema v5 draft 3). derives: observe/schema.md v5 "Mutation pair".
Writes <case>/trace.jsonl for every case below; expected.txt says what each must produce."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
M, M1 = ["n1", "n2", "n3"], ["n1", "n2", "n4"]

def cc(p, s, ep, mem, rid=None, ht=0, dec=False, inputs=None, inc=0):
    r = {"proc": p, "inc": inc, "seq": s, "event": "ConfigCommitted", "node": p, "epoch": ep, "members": mem,
         "request_id": rid, "highest_token": ht, "highest_term": 1, "decided": dec}
    if inputs is not None: r["inputs"] = inputs
    return r
def vote(p, s, prop, ep, rep=None, inc=0):
    r = {"proc": p, "inc": inc, "seq": s, "event": "Vote", "voter": p, "incarnation": inc, "proposal": prop, "config_epoch": ep}
    if rep is not None: r["reported_token"] = rep
    return r
def ag(p, s, voter, ep, prop, vinc=0, rep=None):
    return {"proc": p, "inc": 0, "seq": s, "event": "Agreed", "decider": p, "voter": voter, "voter_incarnation": vinc,
            "proposal": prop, "config_epoch": ep, "reported_token": rep}
def ref(p, s): return {"proc": p, "inc": 0, "seq": s}
def grant(p, s, tok, cl, ep, mem, agreed, sealed=0):
    inp = [{"name": "members", "value": mem}, {"name": "config_epoch", "value": ep}, {"name": "sealed_token", "value": sealed}]
    inp += [{"name": "agreed", "value": v, "ref": ref(p, q)} for v, q in agreed]
    return {"proc": p, "inc": 0, "seq": s, "event": "Grant", "client": cl, "key": "k", "token": tok, "lifetime": 1,
            "grantor_term": 1, "config_epoch": ep, "inputs": inp}
def wacc(s, tok, led, ev="WriteAccept"):
    return {"proc": "s", "inc": 0, "seq": s, "event": ev, "key": "k", "token": tok, "highest_before": led, "grantor_term": 1,
            "inputs": [{"name": "token", "value": tok}, {"name": "ledger", "value": led}, {"name": "value", "value": "v"}]}
amn = lambda node: {"proc": "env", "inc": 0, "seq": 50, "event": "Fault", "restart": node, "amnesia": True}
send = lambda rid, mem, s=1: {"proc": "op", "inc": 0, "seq": s, "event": "ReconfigSend", "operator": "op", "request_id": rid, "to": "n1", "members": mem}

base = [cc(n, 0, 0, M) for n in M]
P = {"client": "c1", "token": 1, "lifetime": 1, "config_epoch": 0}
P2 = {"client": "c2", "token": 2, "lifetime": 1, "config_epoch": 0}
g_ok = [vote("n1", 1, P, 0), vote("n2", 1, P, 0), ag("n1", 2, "n1", 0, P), ag("n1", 3, "n2", 0, P),
        grant("n1", 4, 1, "c1", 0, M, [("n1", 2), ("n2", 3)]), wacc(1, 1, 0)]
C = {"epoch": 1, "members": M1, "request_id": "r1"}
cases = {}
cases["pass-a"] = base + g_ok
cases["pass-b"] = base + g_ok
nd = [dict(r) for r in base + g_ok]; nd[7] = dict(nd[7], token=2)
cases["nondet"] = nd
# same voter names as pass-a's grant, so the name-value pairs are equal; only the Agreed records the refs name differ
cases["refs-differ"] = base + [vote("n1", 1, P2, 0), vote("n2", 1, P2, 0), ag("n1", 2, "n1", 0, P2), ag("n1", 3, "n2", 0, P2),
                               grant("n1", 4, 2, "c2", 0, M, [("n1", 2), ("n2", 3)])]
cases["minority"] = base + [ag("n1", 2, "n1", 0, P), grant("n1", 3, 1, "c1", 0, M, [("n1", 2)])]
cases["storage-bad"] = base + [wacc(1, 1, 2)]
cases["c36-violation"] = base + [vote("n2", 1, C, 0, rep=0), vote("n2", 2, P, 0)]
cases["pass-c36-order"] = base + [vote("n2", 1, P, 0), vote("n2", 2, C, 0, rep=1)]
cases["c36-two-configs"] = base + [vote("n2", 1, C, 0, rep=0), vote("n2", 2, dict(C, members=["n2", "n3", "n5"]), 0, rep=0)]
cases["amnesic-voter"] = base + [amn("n2"), ag("n1", 2, "n1", 0, P), ag("n1", 3, "n2", 0, P, vinc=1),
                                 grant("n1", 4, 1, "c1", 0, M, [("n1", 2), ("n2", 3)])]
P1 = dict(P, config_epoch=1)
cases["pass-amnesic-readded"] = base + [amn("n2"), send("r2", M), cc("n1", 5, 1, M, rid="r2"),
                                        ag("n1", 6, "n1", 1, P1), ag("n1", 7, "n2", 1, P1, vinc=1),
                                        grant("n1", 8, 1, "c1", 1, M, [("n1", 6), ("n2", 7)])]
NEW = ["n4", "n5", "n6"]; CN = {"epoch": 1, "members": NEW, "request_id": "r1"}
def commit(voters, ht, s=10):
    ags = [ag("n1", s + k, v, 0 if v in M else 1, CN, rep=rp) for k, (v, rp) in enumerate(voters)]
    inp = [{"name": "agreed", "value": a["voter"], "ref": ref("n1", a["seq"])} for a in ags]
    return [send("r1", NEW)] + ags + [cc("n1", s + 9, 1, NEW, rid="r1", ht=ht, dec=True, inputs=inp)]
cases["commit-new-only"] = base + commit([("n4", None), ("n5", None)], 0)
cases["pass-commit-both"] = base + commit([("n2", 3), ("n3", 1), ("n4", None), ("n5", None)], 3)
cases["seal-low"] = base + commit([("n2", 3), ("n3", 1), ("n4", None), ("n5", None)], 0)
cases["double-decided"] = base + commit([("n2", 3), ("n3", 1), ("n4", None), ("n5", None)], 3) + \
    commit([("n2", 3), ("n3", 1), ("n4", None), ("n5", None)], 3, s=30)[1:]
P1n = {"client": "c1", "token": 3, "lifetime": 1, "config_epoch": 1}
cases["grant-below-seal"] = base + commit([("n2", 5), ("n3", 1), ("n4", None), ("n5", None)], 5) + \
    [ag("n4", 1, "n4", 1, P1n), ag("n4", 2, "n5", 1, P1n), grant("n4", 3, 3, "c1", 1, NEW, [("n4", 1), ("n4", 2)], sealed=5)]
for name, recs in cases.items():
    os.makedirs(f"{D}/{name}", exist_ok=True)
    with open(f"{D}/{name}/trace.jsonl", "w") as f:
        f.write("".join(json.dumps(r) + "\n" for r in recs))
