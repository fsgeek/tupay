#!/usr/bin/env python3
"""Generate W1's author-facing contract copies mechanically (W1-prereg.md, "Author-facing copies"; finding S1).

derives: W1 S1 (author-facing copies from normative sections only), practice rule 18 (no steward hypotheses to authors)

Rule, applied by line, never by judgement:
  arm F (contract-draft-7.md): drop the history preamble (from the line after the title through the line before
    "**Scope of prescription.**"), drop sections "## 7." and "## 8." whole; keep everything else byte-identical.
  arms P and N (contract-prose-arm-draft-2.md): drop the header paragraph (the text between the title and the first
    "## " heading); keep everything else byte-identical.
  both: the title line is replaced by one neutral title, the same for every arm, because titles are not normative and
    the originals name the arm ("four-part form", "for the comparison arm") and a stale status ("not registered").
Writes experiments/W1/inputs/{contract-F.md,contract-P.md,omitted.json} and prints sha256 of each output.
"""
import hashlib, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
TITLE = "# Verified backup: contract and failure model\n"
SRC_F = ROOT / "docs/backup/contract-draft-7.md"
SRC_P = ROOT / "docs/backup/contract-prose-arm-draft-2.md"
OUT = ROOT / "experiments/W1/inputs"

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def arm_f(lines):
    omitted = ["(title line, replaced by the neutral title)", "(history preamble: drafts 5 to 7)"]
    scope = next(i for i, l in enumerate(lines) if l.startswith("**Scope of prescription.**"))
    out = [TITLE, "\n"] + lines[scope:]
    res, skip = [], False
    for l in out:
        if l.startswith("## "):
            skip = l.startswith("## 7.") or l.startswith("## 8.")
            if skip: omitted.append(l.strip())
        if not skip: res.append(l)
    return res, omitted

def arm_p(lines):
    first = next(i for i, l in enumerate(lines) if l.startswith("## "))
    return [TITLE, "\n"] + lines[first:], ["(title line, replaced by the neutral title)", "(header paragraph)"]

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    f, of = arm_f(SRC_F.read_text().splitlines(keepends=True))
    p, op = arm_p(SRC_P.read_text().splitlines(keepends=True))
    (OUT / "contract-F.md").write_text("".join(f)); (OUT / "contract-P.md").write_text("".join(p))
    meta = {"sources": {"F": [str(SRC_F.relative_to(ROOT)), sha(SRC_F)], "P": [str(SRC_P.relative_to(ROOT)), sha(SRC_P)]},
            "omitted": {"F": of, "P": op}}
    (OUT / "omitted.json").write_text(json.dumps(meta, indent=1) + "\n")
    for n in ("contract-F.md", "contract-P.md", "omitted.json"): print(sha(OUT / n), f"experiments/W1/inputs/{n}")

if __name__ == "__main__": sys.exit(main())
