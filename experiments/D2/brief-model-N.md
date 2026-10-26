# Brief: model Episode's log and recovery (condition N, v1)

You have: `source/episode-1992.txt` (*The Episode File System*, USENIX Winter 1992; the PDF beside it is the same text); `source/episode/`, the Episode file system's source as released in OSF DCE 1.2.2, whose log and recovery are `source/episode/logbuf/`; and `GUARANTEES.md`, the guarantees the sources make for the log and recovery (extracted by two other readers). TLC is at `$TLA2TOOLS`. You have no web access and need none. Your work must stay under 24 GB of memory; your session ends at six hours' wall clock, whatever state it is in.

## Task
1. Write a TLA+ model of the log and recovery **as the source implements them**; where the paper and the source disagree, follow the source and record the disagreement. Include every defence the sources describe or the code implements that bears on the guarantees.
2. State the guarantees of `GUARANTEES.md` that your model can express as invariants or properties.
3. Find what breaks them. Check first that the guarantees hold in the model as written (**honest environment**: everything outside `logbuf` behaves as the log and recovery need it to). Then look for runs in which something outside `logbuf` (anything it calls, that calls it, or that it runs on, including an operator) behaves in a way the sources do not rule out, and a guarantee fails **with the model's defences in place**. For each such run, also check that removing the defence you think matters changes the outcome; if the model has no defence against it, record the run as **unguarded**: it is not a finding.
4. A **finding** is such a run that breaks a guarantee with the model's defences in place, while the honest-environment check holds. Report each one in the schema below, with its counterexample.
5. Rank your findings, most serious first, by your own judgement of their consequence for a running file system.

## Finding schema (exact; a script reads it)
```
### F<n>
- violated: <the obligation on something outside logbuf that the run violates, in one sentence>
- mechanism: <how the violation, through the log and recovery's own steps, leads to the failure, in two to four sentences>
- effect: <what the file system, its users or operators see; the GUARANTEES.md id it breaks>
- defence: <the defence the model includes, and why it does not cover this>
- counterexample: <the path of the TLC trace file in this checkout>
- confidence: <high | medium | low> — <one line>
```

## Rules
- **Commit as you go**: the model, each check's output, and each finding as soon as you have it. Only what is committed when the session ends counts.
- Before building, commit `PREDICTIONS.md`: how many findings you expect. Never edit it; amend additively.
- If a check's result looks wrong, say so; do not change the model to make a guarantee hold or fail without naming the source line the old model misread.
- Bounds: state, for every check, the bounds it ran at and what the violation needs the model to reach (the sizes and counts of everything the run involves); a check that cannot reach that is reported as such, not as a result.
- Write `REPORT.md` at the end: what you modelled, unguarded runs, findings, disagreements between paper and source, and your declared limitations.
