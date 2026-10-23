#!/usr/bin/env python3
"""Synthetic traces for observe/decision_replay.py (schema v5 draft 4). derives: observe/schema.md v5 "Mutation pair".
Writes <case>/trace.jsonl for every case below; expected.txt says what each must produce."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
M, NEW = ["n1", "n2", "n3"], ["n4", "n5", "n6"]

def ref(p, s, inc=0): return {"proc": p, "inc": inc, "seq": s}
def cc(p, s, ep, mem, rid=None, dec=False, inputs=None, readmits=()):
    r = {"proc": p, "inc": 0, "seq": s, "event": "ConfigCommitted", "node": p, "epoch": ep, "members": mem,
         "request_id": rid, "readmits": [list(x) for x in readmits], "decided": dec}
    if inputs is not None: r["inputs"] = inputs
    return r
def agree(p, s, prop, inc=0):
    return {"proc": p, "inc": inc, "seq": s, "event": "Agree", "node": p, "incarnation": inc, "proposal": prop}
def ag(p, s, node, prop, toward, ninc=0):
    return {"proc": p, "inc": 0, "seq": s, "event": "Agreed", "decider": p, "node": node, "node_incarnation": ninc,
            "proposal": prop, "counted_toward": toward}
def grant(p, s, tok, cl, ep, mem, agreed, extra=()):
    inp = [{"name": "members", "value": mem}, {"name": "config_epoch", "value": ep}, {"name": "grantor_term", "value": 1},
           {"name": "last_token", "value": tok - 1}]
    inp += [{"name": "agreed", "value": v, "ref": ref(p, q)} for v, q in agreed] + list(extra)
    return {"proc": p, "inc": 0, "seq": s, "event": "Grant", "client": cl, "key": "k", "token": tok, "lifetime": 1,
            "grantor_term": 1, "config_epoch": ep, "inputs": inp}
def wacc(s, tok, led, ev="WriteAccept"):
    return {"proc": "s", "inc": 0, "seq": s, "event": ev, "key": "k", "token": tok, "highest_before": led, "grantor_term": 1,
            "inputs": [{"name": "token", "value": tok}, {"name": "ledger", "value": led}, {"name": "value", "value": "v"}]}
amn = lambda node: {"proc": "env", "inc": 0, "seq": 50, "event": "Fault", "restart": node, "amnesia": True}
def commit(p, s, ep, mem, rid, old, agreed, readmits=()):
    """agreed: (node, node_incarnation, counted_toward); old: members of ep-1."""
    prop = {"epoch": ep, "members": mem, "request_id": rid}
    ags = [ag(p, s + k, n, prop, tw, ninc=i) for k, (n, i, tw) in enumerate(agreed)]
    inp = [{"name": "old_members", "value": old}, {"name": "old_epoch", "value": ep - 1},
           {"name": "request_id", "value": rid}, {"name": "requested_members", "value": mem}]
    inp += [{"name": "agreed", "value": a["node"], "ref": ref(p, a["seq"])} for a in ags]
    return ags + [cc(p, s + 9, ep, mem, rid=rid, dec=True, inputs=inp, readmits=readmits)]

base = [cc(n, 0, 0, M) for n in M]
P = {"client": "c1", "token": 1, "lifetime": 1, "config_epoch": 0}
P2 = {"client": "c2", "token": 2, "lifetime": 1, "config_epoch": 0}
g_ok = [agree("n1", 1, P), agree("n2", 1, P), ag("n1", 2, "n1", P, [0]), ag("n1", 3, "n2", P, [0]),
        grant("n1", 4, 1, "c1", 0, M, [("n1", 2), ("n2", 3)]), wacc(1, 1, 0)]
cases = {}
cases["pass-a"] = base + g_ok
cases["pass-b"] = base + g_ok
nd = [dict(r) for r in base + g_ok]; nd[7] = dict(nd[7], token=2)
cases["nondet"] = nd
# same node names as pass-a's grant, so the name-value pairs are equal; only the Agreed records the refs name differ
cases["refs-differ"] = base + [agree("n1", 1, P2), agree("n2", 1, P2), ag("n1", 2, "n1", P2, [0]), ag("n1", 3, "n2", P2, [0]),
                               grant("n1", 4, 1, "c2", 0, M, [("n1", 2), ("n2", 3)])]
cases["minority"] = base + [ag("n1", 2, "n1", P, [0]), grant("n1", 3, 1, "c1", 0, M, [("n1", 2)])]
cases["storage-bad"] = base + [wacc(1, 1, 2)]
cases["commit-new-only"] = base + commit("n1", 10, 1, NEW, "r1", M, [("n4", 0, [1]), ("n5", 0, [1])])
both = [("n2", 0, [0]), ("n3", 0, [0]), ("n4", 0, [1]), ("n5", 0, [1])]
cases["pass-commit-both"] = base + commit("n1", 10, 1, NEW, "r1", M, both)
cases["double-decided"] = base + commit("n1", 10, 1, NEW, "r1", M, both) + commit("n1", 30, 1, NEW, "r1", M, both)
cases["amnesic-voter"] = base + [amn("n2"), ag("n1", 2, "n1", P, [0]), ag("n1", 3, "n2", P, [0], ninc=1),
                                 grant("n1", 4, 1, "c1", 0, M, [("n1", 2), ("n2", 3)])]
# epoch 1 keeps the members of epoch 0; n2#1's agreement is recorded (not counted: n1 and n3 make both majorities)
readd = commit("n1", 10, 1, M, "r2", M, [("n1", 0, [0, 1]), ("n3", 0, [0, 1]), ("n2", 1, [])], readmits=[("n2", 1)])
P1 = dict(P, config_epoch=1)
cases["pass-amnesic-readmitted"] = base + [amn("n2")] + readd + \
    [ag("n1", 30, "n1", P1, [1]), ag("n1", 31, "n2", P1, [1], ninc=1), grant("n1", 32, 1, "c1", 1, M, [("n1", 30), ("n2", 31)])]
cases["readmit-self-count"] = base + [amn("n2")] + \
    commit("n1", 10, 1, M, "r2", M, [("n1", 0, [0, 1]), ("n2", 1, [0, 1])], readmits=[("n2", 1)])
cases["readmits-without-agreed"] = base + [amn("n2")] + \
    commit("n1", 10, 1, M, "r2", M, [("n1", 0, [0, 1]), ("n3", 0, [0, 1])], readmits=[("n2", 1)])
cases["dup-token"] = base + g_ok[:5] + [ag("n3", 1, "n3", P2, [0]), ag("n3", 2, "n2", P2, [0]),
                                        grant("n3", 3, 1, "c2", 0, M, [("n3", 1), ("n3", 2)])]
# n2 agrees to token 2 (counted by n3's grant), then to token 1 (counted by n1's grant), in its own order
cases["agree-decreasing"] = base + [agree("n2", 1, P2), agree("n2", 2, P), ag("n3", 1, "n3", P2, [0]), ag("n3", 2, "n2", P2, [0]),
                                    grant("n3", 3, 2, "c2", 0, M, [("n3", 1), ("n3", 2)]),
                                    ag("n1", 2, "n1", P, [0]), ag("n1", 3, "n2", P, [0]), grant("n1", 4, 1, "c1", 0, M, [("n1", 2), ("n1", 3)])]
cases["pass-agree-order"] = base + [agree("n2", 1, P), agree("n2", 2, P2), ag("n1", 2, "n1", P, [0]), ag("n1", 3, "n2", P, [0]),
                                    grant("n1", 4, 1, "c1", 0, M, [("n1", 2), ("n1", 3)]),
                                    ag("n3", 1, "n3", P2, [0]), ag("n3", 2, "n2", P2, [0]), grant("n3", 3, 2, "c2", 0, M, [("n3", 1), ("n3", 2)])]
P1lo = dict(P, config_epoch=1)
cases["epoch-lower-token"] = base + [ag("n3", 1, "n3", P2, [0]), ag("n3", 2, "n2", P2, [0]),
                                     grant("n3", 3, 2, "c2", 0, M, [("n3", 1), ("n3", 2)])] + \
    commit("n1", 10, 1, M, "r3", M, [("n1", 0, [0, 1]), ("n3", 0, [0, 1])]) + \
    [ag("n1", 30, "n1", P1lo, [1]), ag("n1", 31, "n3", P1lo, [1]), grant("n1", 32, 1, "c1", 1, M, [("n1", 30), ("n1", 31)])]
cases["unknown-input"] = base + g_ok[:4] + [grant("n1", 4, 1, "c1", 0, M, [("n1", 2), ("n2", 3)],
                                                   extra=[{"name": "nonce", "value": 7}])]
for name, recs in cases.items():
    os.makedirs(f"{D}/{name}", exist_ok=True)
    with open(f"{D}/{name}/trace.jsonl", "w") as f:
        f.write("".join(json.dumps(r) + "\n" for r in recs))
