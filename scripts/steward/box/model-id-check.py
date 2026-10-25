#!/usr/bin/env python3
"""Every model turn in a Claude Code stream-json transcript must be the pinned model. usage: model-id-check.py <transcript.jsonl> [model]
derives: sixth handoff, owed item 2 (Tony's $500 lesson: nothing may switch underneath)
Reports each assistant message whose message.model differs, and the init line's model; exit 1 on any difference or
on no assistant message at all (a transcript with nothing to check is not a pass)."""
import json, sys
path, want = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else 'claude-opus-5-5')
n, bad = 0, []
for i, line in enumerate(open(path), 1):
    try: r = json.loads(line)
    except ValueError: continue
    if r.get('type') == 'system' and r.get('subtype') == 'init' and r.get('model') != want:
        bad.append(f"line {i}: init model {r.get('model')}")
    if r.get('type') == 'assistant':
        n += 1; m = r.get('message', {}).get('model')
        if m != want: bad.append(f"line {i}: assistant model {m}")
for b in bad: print(b)
print(f"{path}: {n} assistant messages, {len(bad)} not {want}")
sys.exit(1 if bad or n == 0 else 0)
