#!/usr/bin/env python3
"""Score D2 phase 3 by the registration (experiments/D2/design.md, "Predictions for phase 3").

Written by the eleventh steward 2026-11-03 and committed before its first run. Rules, each from
the design or the log, and nowhere else:

Judges (log 2026-10-27 18:40Z, 2026-10-29 06:23Z and 06:26Z): Episode (judges/episode/<packet>.json)
and Gemini (judges/<packet>/gemini/ruling.json) are registered; a prediction holds only if it
holds under both. GLM (judges/<packet>/glm-2/ruling.json, its one rerun) is reported beside.
Gemini has no registered ruling on cells-2 (both runs failed to parse); its mechanical repair
(gemini-2/ruling-repaired-beside.json) is reported beside, never as the registered ruling. Under
Gemini, the registered cell outcomes therefore come from cells-1 and cells-3 only, stated as such.

Denominators (design; log 2026-10-29 05:31Z): Episode's answer came after phase 0, so the scored
denominator is all seven sealed bugs (E1-E7); the four environment-contract bugs (E2-E5) are
reported beside. Comment split from the sealed file v2's own counts: comment E2, E3, E5, E6;
no comment E1, E4, E7 (beside: comment E2, E3, E5; none E4).

D2-1  fraction of denominator bugs whose contract some cell names: comment group > no-comment
      group, strictly.
D2-2  at least one sealed bug is a "match" among the scored findings of at least one model
      author. D2-2g beside: Grok's authors only. A Recognised row (kind "recognised") matching
      a sealed bug is a leakage flag and voids D2-2 for that enumerator family's lists; reported.
D2-3  in each family separately, condition C's scored findings reach (match or partial) more
      distinct sealed bugs than condition N's. One prediction "in each family": holds only if
      it holds for both families.
D2-4  at least four denominator bugs have their contract named by some cell (if the
      denominator is under five, all but one).
D2-5  Claude C reaches (match or partial) more distinct sealed bugs than Grok C.
P0-4  (phase 0, judged here) at least one Recognised row names a sealed bug.
Precision per author: findings judged match, and match or partial, over scored findings; both
are reported, neither is chosen as primary (the design says "matched").
A finding matching several bugs counts for each (design).
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "experiments/D2/phase3"
J = ROOT / "judges"
ALL7 = ["E1", "E2", "E3", "E4", "E5", "E6", "E7"]
ENV4 = ["E2", "E3", "E4", "E5"]
COMMENT = {"E2", "E3", "E5", "E6"}
AUTHORS = ["model-c-claude", "model-n-claude", "model-c-grok", "model-n-grok"]
CELL_PACKETS = ["cells-1", "cells-2", "cells-3"]


def load(p):
    return json.load(open(p))


def ruling(judge, packet, beside_repair=False):
    """Return the parsed ruling list for (judge, packet), or None if there is no ruling."""
    if judge == "episode":
        p = J / "episode" / f"{packet}.json"
    elif judge == "gemini":
        if packet == "cells-2":
            if not beside_repair:
                return None
            p = J / "cells-2" / "gemini-2" / "ruling-repaired-beside.json"
        else:
            p = J / packet / "gemini" / "ruling.json"
    elif judge == "glm":
        p = J / packet / "glm-2" / "ruling.json"
    key = "cells" if packet.startswith("cells") else packet
    return load(p)[key]


def cells_named(judge, beside_repair=False):
    named, missing = set(), []
    for pk in CELL_PACKETS:
        r = ruling(judge, pk, beside_repair)
        if r is None:
            missing.append(pk)
            continue
        for c in r:
            named.update(c.get("names_contract_of") or [])
    return named, missing


def frac(bugs, named):
    return sum(b in named for b in bugs), len(bugs)


def score(judge, mapping, beside_repair=False):
    out = {"judge": judge, "beside_repair": beside_repair}
    # cells
    named, missing = cells_named(judge, beside_repair)
    out["cells_missing_packets"] = missing
    out["bugs_named_by_cells"] = sorted(named)
    for label, den in (("seven", ALL7), ("env4", ENV4)):
        c = [b for b in den if b in COMMENT]
        n = [b for b in den if b not in COMMENT]
        fc, fn = frac(c, named), frac(n, named)
        d21 = (fc[0] / fc[1]) > (fn[0] / fn[1]) if fc[1] and fn[1] else None
        k = sum(b in named for b in den)
        need = 4 if len(den) >= 5 else len(den) - 1
        out[f"D2-1[{label}]"] = {"comment": fc, "no_comment": fn, "holds": d21}
        out[f"D2-4[{label}]"] = {"named": k, "of": len(den), "need": need, "holds": k >= need}
    # findings
    fr = {f["id"]: f for f in ruling(judge, "findings")}
    per = {a: {"scored": 0, "match": 0, "match_or_partial": 0, "bugs_match": set(), "bugs_reach": set(),
               "flagged_confirmed_property": 0} for a in AUTHORS}
    for fid, meta in mapping["findings"].items():
        if not meta.get("scored"):
            continue
        a, r = meta["author"], fr[fid]
        p = per[a]
        p["scored"] += 1
        bugs = r.get("bugs") or []
        if r["ruling"] == "match":
            p["match"] += 1
            p["bugs_match"].update(bugs)
        if r["ruling"] in ("match", "partial"):
            p["match_or_partial"] += 1
            p["bugs_reach"].update(bugs)
        if r.get("flag_confirmed_property"):
            p["flagged_confirmed_property"] += 1
    out["per_author"] = {a: {**{k: v for k, v in p.items() if not isinstance(v, set)},
                             "bugs_match": sorted(p["bugs_match"]), "bugs_reach": sorted(p["bugs_reach"]),
                             "precision_match": f"{p['match']}/{p['scored']}",
                             "precision_match_or_partial": f"{p['match_or_partial']}/{p['scored']}"}
                         for a, p in per.items()}
    # rows: found by reading, leakage
    rr = {r["id"]: r for r in ruling(judge, "rows")}
    found, leak = [], []
    for rid, meta in mapping["rows"].items():
        m = rr[rid].get("matches") or []
        if m:
            found.append({"row": rid, "kind": meta["kind"], "enumerator": meta["enumerator"], "bugs": m})
            if meta["kind"] == "recognised":
                leak.append({"row": rid, "enumerator": meta["enumerator"], "bugs": m})
    out["rows_found_by_reading"] = found
    out["leakage_flags"] = leak
    leak_fams = {l["enumerator"].split("-")[0] for l in leak}
    out["P0-4"] = {"holds": bool(leak), "recognised_rows_matching": leak}
    # D2-2: voided for a family whose enumeration lists leaked
    fam = lambda a: a.split("-")[-1]
    def any_match(authors):
        return any(per[a]["match"] > 0 for a in authors)
    out["D2-2"] = {"holds": any_match(AUTHORS), "voided_for_families_with_leakage": sorted(leak_fams)}
    out["D2-2g"] = {"holds": any_match(["model-c-grok", "model-n-grok"])}
    d23 = {}
    for f in ("claude", "grok"):
        c, n = len(per[f"model-c-{f}"]["bugs_reach"]), len(per[f"model-n-{f}"]["bugs_reach"])
        d23[f] = {"C": c, "N": n, "holds": c > n}
    out["D2-3"] = {**d23, "holds": all(v["holds"] for v in d23.values())}
    cc, gc = len(per["model-c-claude"]["bugs_reach"]), len(per["model-c-grok"]["bugs_reach"])
    out["D2-5"] = {"claude_C": cc, "grok_C": gc, "holds": cc > gc}
    return out


def main():
    mapping = load(ROOT / "mapping.json")
    res = {"registered": [score("episode", mapping), score("gemini", mapping)],
           "beside": [score("gemini", mapping, beside_repair=True), score("glm", mapping)]}
    preds = ["D2-1[seven]", "D2-2", "D2-3", "D2-4[seven]", "D2-5", "P0-4"]
    verdict = {}
    for p in preds:
        e, g = (r[p]["holds"] for r in res["registered"])
        verdict[p] = {"episode": e, "gemini": g, "holds_under_both": bool(e and g)}
    res["verdict"] = verdict
    json.dump(res, sys.stdout, indent=1, default=sorted)
    print()


if __name__ == "__main__":
    main()
