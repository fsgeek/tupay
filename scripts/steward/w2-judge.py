#!/usr/bin/env python3
"""W2: the judge's matching for one family, and I(form) computed mechanically (fix for Kimi's finding 2).
usage: w2-judge.py <family> <F-cell-dir> <P-cell-dir> <list1-form F|P> <out-dir>   (OPENROUTER_API_KEY in the environment)
derives: experiments/W2-prereg.md § Matching. Frozen at registration; changing it is a new version, logged.
Judge: cohere/command-a-plus, temperature 0, one call; if the reply is not valid JSON in the schema, one retry with the
identical request; if that also fails, the family is "judge-failed" (W2-2 then treats it as not evaluable).
Algorithm:
 - The items of each list are those w2-count.py finds (numbered 1..n in that order), given to the judge with the full
   text of each item (the item line and its continuation lines up to the next item or section end).
 - The judge returns, for every item of each list: grounded (true/false) and matches (item numbers in the other list).
 - A pair (a in list 1, b in list 2) is matched if either side names the other (symmetric union).
 - An item is unmatched if it is in no matched pair. I(form) for this family = grounded and unmatched items of the
   list holding that form. Ungrounded items count in neither I.
"""
import json, os, re, sys, hashlib, pathlib, subprocess, urllib.request
T = pathlib.Path('/home/tony/projects/tupay')
fam, fdir, pdir, l1form, out = sys.argv[1], pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3]), sys.argv[4], pathlib.Path(sys.argv[5])
out.mkdir(parents=True, exist_ok=True)
def items(cell):
    src = cell / "continuation.md" if (cell / "continuation.md").exists() else cell / "draft.md"
    lines = src.read_text().splitlines()
    is_cq = lambda l: re.sub(r"^[#*\d.\s]+", "", l).upper().startswith("CONTRACT QUESTIONS")
    s = next(i for i, l in enumerate(lines) if is_cq(l)); cur, res = None, []
    for l in lines[s + 1:]:
        if l.startswith("#") and not is_cq(l): break
        if re.match(r"^(\d+[.)]\s|[-*+]\s)", l):
            cur = [l]; res.append(cur)
        elif cur is not None: cur.append(l)
    return ["\n".join(x).strip() for x in res]
cells = {"F": fdir, "P": pdir}; texts = {"F": T / "experiments/W1/inputs/contract-F.md", "P": T / "experiments/W1/inputs/contract-P.md"}
l2form = "P" if l1form == "F" else "F"
L = {1: items(cells[l1form]), 2: items(cells[l2form])}
task = """You are a judge. Below are two contract texts, Contract 1 and Contract 2. They are meant to impose the same obligations in two different written forms. Below them are two lists of questions that independent readers raised about them: List 1 was raised about Contract 1, and List 2 about Contract 2.

For every item in each list, decide:
- "grounded": true if the item concerns text that is actually present in its own list's contract (a quotation from it, or a clear reference to a clause, term or cell that it contains); false otherwise.
- "matches": the numbers of the items in the OTHER list that raise the same underlying contract issue (the same open point about the same obligation, term or cell), even if worded differently or quoting the other form's wording. An empty list if none.

Answer with JSON only, exactly in this schema, covering every item number of both lists:
{"list1": [{"n": 1, "grounded": true, "matches": [3]}, ...], "list2": [{"n": 1, "grounded": true, "matches": []}, ...]}"""
packet = (task + "\n\n===== CONTRACT 1 =====\n" + texts[l1form].read_text() + "\n\n===== CONTRACT 2 =====\n" + texts[l2form].read_text()
          + "\n\n===== LIST 1 =====\n" + "\n\n".join(f"[{i+1}] {t}" for i, t in enumerate(L[1]))
          + "\n\n===== LIST 2 =====\n" + "\n\n".join(f"[{i+1}] {t}" for i, t in enumerate(L[2])))
(out / "packet.md").write_text(packet)
def ask():
    req = {"model": "cohere/command-a-plus", "messages": [{"role": "user", "content": packet}], "temperature": 0}
    r = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(req).encode(),
        headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"], "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r, timeout=3600))
def parse(resp):
    t = resp["choices"][0]["message"].get("content") or ""
    t = t[t.find("{"): t.rfind("}") + 1]; j = json.loads(t)
    for k, n in (("list1", len(L[1])), ("list2", len(L[2]))):
        assert sorted(x["n"] for x in j[k]) == list(range(1, n + 1)), f"{k} does not cover 1..{n}"
        for x in j[k]: assert isinstance(x["grounded"], bool) and isinstance(x["matches"], list)
    return j
result = None
for attempt in (1, 2):
    resp = ask(); (out / f"response-{attempt}.json").write_text(json.dumps(resp, indent=1))
    try: result = parse(resp); break
    except Exception as e: (out / f"parse-error-{attempt}.txt").write_text(str(e))
if result is None:
    s = {"family": fam, "status": "judge-failed"}
else:
    pairs = {(x["n"], m) for x in result["list1"] for m in x["matches"]} | {(m, x["n"]) for x in result["list2"] for m in x["matches"]}
    m1 = {a for a, b in pairs}; m2 = {b for a, b in pairs}
    g1 = {x["n"] for x in result["list1"] if x["grounded"]}; g2 = {x["n"] for x in result["list2"] if x["grounded"]}
    I = {l1form: len(g1 - m1), l2form: len(g2 - m2)}
    s = {"family": fam, "status": "ok", "list1": l1form, "n": {l1form: len(L[1]), l2form: len(L[2])},
         "grounded": {l1form: len(g1), l2form: len(g2)}, "matched_pairs": len(pairs), "I": I}
(out / "summary.json").write_text(json.dumps(s, indent=1)); print(json.dumps(s))
