#!/usr/bin/env python3
"""Judge packet for one arm-D shared-scenario divergence (model PASS vs implementation UNEXPLAINED).
Excerpt rule (stated in the packet): trace records of types Scheduled, MessageLost, AppendAcknowledged are dropped
and counted; every other record is kept verbatim. Author text: every README paragraph that names the scenario.
derives: docs/steward-practice.md "Running and judging"; experiments/replay-prereg.md "Labels" (divergence)."""
import json, re, subprocess, sys, collections
scen, seed, trace = sys.argv[1], sys.argv[2], sys.argv[3]
R = '/home/tony/projects/tupay'
def show(repo, path): return subprocess.run(['git', '-C', repo, 'show', 'first-version:' + path], capture_output=True, text=True).stdout
def paras(text, word): return '\n\n'.join(p for p in text.split('\n\n') if re.search(r'\b%s\b' % word, p))
drop = {'Scheduled', 'MessageLost', 'AppendAcknowledged'}; kept, dropped = [], collections.Counter()
for l in open(trace):
    r = json.loads(l)
    if r.get('event') in drop: dropped[r['event']] += 1
    else: kept.append(l.rstrip())
out = [f"""You are judging a divergence between two independently written artifacts of the same specification. A TLA+ model and a Go implementation were each built from the inputs below, by authors who never saw each other's work. On shared scenario {scen}, their labels differ: the **model** reports **PASS** (every step taken, no clause violated, within the model's stated bounds), and the **implementation** reports **UNEXPLAINED steps** (the scenario's bound was reached before every step was taken) on the seed(s) stated below. Neither side reports a contract violation.

Decide, from the inputs alone, which of these holds, and say why with quotes:
(A) the implementation's behaviour is permitted by the specification and the model's PASS depends on a choice the inputs leave open (name the choice);
(B) the implementation misreads an input (name the clause, cell or sentence);
(C) the model misreads an input (name it);
(D) the evidence does not discriminate.
End with JSON: {{"verdict": "A|B|C|D", "choice_or_clause": "...", "reason": "..."}}.
""",
"# Inputs (frozen)"] + [f"## {p}\n```\n{open(R + '/' + p).read()}\n```" for p in
 ['replay/contract.md', 'replay/failure-model.md', 'replay/scenario-format.md', 'replay/observe.md', f'replay/scenarios/{scen}.yaml', 'replay/spec-D.md']]
out += ["# Labels", open(sys.argv[4]).read(),
 "# What each author wrote about this scenario (README paragraphs naming it, at the scored version)",
 "## Model author", paras(show(R + '/../tupay-replay-D-model', 'model/README.md'), scen),
 "## Implementation author", paras(show(R + '/../tupay-replay-D-impl', 'impl/README.md'), scen),
 f"# Implementation trace, seed {seed} (observe format)",
 f"Excerpt rule: records of type Scheduled, MessageLost and AppendAcknowledged are omitted (counts: {dict(dropped)}); every other record is kept verbatim, in order.",
 "```", *kept, "```"]
print('\n\n'.join(out))
