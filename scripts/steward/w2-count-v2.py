#!/usr/bin/env python3
"""W2: count the CONTRACT QUESTIONS in one cell, mechanically. VERSION 2 (W2 amendment A1, 2026-11-23, informed by the
GLM-F outcome: v1 missed a heading with a letter label, "## F. CONTRACT QUESTIONS", and items written "**Q1. ...**").
v1 is w2-count.py, unchanged, and its score is the registered one; v2's is reported beside it.
usage: w2-count.py <cell-dir>   prints JSON {"status": "complete"|"missing", "q": n, "items": [first 80 chars of each]}
derives: experiments/W2-prereg.md § Count. Frozen at registration; changing it is a new version, logged.
Rules, applied in order:
 1. Source (v2): if continuation.md exists and the drafted reply did not end normally (finish_reason other than
    "stop") or has no section, the section comes from continuation.md. Otherwise from draft.md, and an existing
    continuation is reported as "continuation-unneeded" and not used.
 2. Section: from the first line whose text, after stripping leading '#', '*', digits, '.', and spaces, begins with
    "CONTRACT QUESTIONS" (case-insensitive), up to the next markdown heading line ('#' at column 0), a line of only
    '---' or '***' followed by a heading, or the end of the text. (v2) A leading label of up to three letters or digits
    followed by '.' or ')' is stripped before the test, so "## F. CONTRACT QUESTIONS" and "# 11. CONTRACT QUESTIONS" match. A heading of any level inside the section that does
    not start with "CONTRACT QUESTIONS" ends it.
 3. Items: a line at column 0 (no leading space) that starts with a number followed by '.' or ')' and a space, or with
    '- ', '* ' or '+ ', is one item; (v2) so is a line at column 0 starting with '**' and then an optional 'Q' and a
    number followed by '.' or ')' (for example "**Q1. ...**" or "**3. ...**"). Indented lines and nested lists are not counted. Duplicates are counted as written.
 4. Status: "missing" if no section is found; otherwise "complete", with q = the count (which may be 0).
"""
import json, pathlib, re, sys
d = pathlib.Path(sys.argv[1])
def is_cq(l):
    t = re.sub(r"^[#*\s]+", "", l); t = re.sub(r"^[A-Za-z0-9]{1,3}[.)]\s*", "", t); t = re.sub(r"^[*\s]+", "", t)
    return t.upper().startswith("CONTRACT QUESTIONS")
def section(f):
    if not f.exists(): return None, []
    L = f.read_text().splitlines(); return next((i for i, l in enumerate(L) if is_cq(l)), None), L
def finished(d):   # did the drafted reply end normally? (the last of response-rerun.json / response.json)
    for n in ("response-rerun.json", "response.json"):
        if (d / n).exists(): return json.load(open(d / n))["choices"][0].get("finish_reason") == "stop"
    return True
note = None
start, lines = section(d / "draft.md"); src = d / "draft.md"
if (d / "continuation.md").exists():
    if start is None or not finished(d):
        start, lines = section(d / "continuation.md"); src = d / "continuation.md"
    else: note = "continuation-unneeded"
if start is None:
    print(json.dumps({"status": "missing", "q": None, "items": [], "source": src.name})); sys.exit(0)
items = []
for l in lines[start + 1:]:
    if l.startswith("#") and not is_cq(l): break
    if re.match(r"^(\d+[.)]\s|[-*+]\s|\*\*Q?\d+[.)])", l): items.append(l[:80])
print(json.dumps({"status": "complete", "q": len(items), "items": items, "source": src.name, "note": note}))
