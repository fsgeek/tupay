#!/usr/bin/env python3
"""W2: count the CONTRACT QUESTIONS in one cell, mechanically (W2 pre-registration, fix for Kimi's finding 1).
usage: w2-count.py <cell-dir>   prints JSON {"status": "complete"|"missing", "q": n, "items": [first 80 chars of each]}
derives: experiments/W2-prereg.md § Count. Frozen at registration; changing it is a new version, logged.
Rules, applied in order:
 1. Source: if <cell-dir>/continuation.md exists, the section is taken from it; otherwise from draft.md.
 2. Section: from the first line whose text, after stripping leading '#', '*', digits, '.', and spaces, begins with
    "CONTRACT QUESTIONS" (case-insensitive), up to the next markdown heading line ('#' at column 0), a line of only
    '---' or '***' followed by a heading, or the end of the text. A heading of any level inside the section that does
    not start with "CONTRACT QUESTIONS" ends it.
 3. Items: a line at column 0 (no leading space) that starts with a number followed by '.' or ')' and a space, or with
    '- ', '* ' or '+ ', is one item. Indented lines and nested lists are not counted. Duplicates are counted as written.
 4. Status: "missing" if no section is found; otherwise "complete", with q = the count (which may be 0).
"""
import json, pathlib, re, sys
d = pathlib.Path(sys.argv[1])
src = d / "continuation.md" if (d / "continuation.md").exists() else d / "draft.md"
lines = src.read_text().splitlines() if src.exists() else []
def is_cq(l):
    return re.sub(r"^[#*\d.\s]+", "", l).upper().startswith("CONTRACT QUESTIONS")
start = next((i for i, l in enumerate(lines) if is_cq(l)), None)
if start is None:
    print(json.dumps({"status": "missing", "q": None, "items": [], "source": src.name})); sys.exit(0)
items = []
for l in lines[start + 1:]:
    if l.startswith("#") and not is_cq(l): break
    if re.match(r"^(\d+[.)]\s|[-*+]\s)", l): items.append(l[:80])
print(json.dumps({"status": "complete", "q": len(items), "items": items, "source": src.name}))
