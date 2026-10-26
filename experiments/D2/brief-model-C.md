# Brief: model Episode's log and recovery, and the contracts it relies on (condition C, v1)

You have: `source/episode-1992.txt` (*The Episode File System*, USENIX Winter 1992; the PDF beside it is the same text); `source/episode/`, the Episode file system's source as released in OSF DCE 1.2.2, whose log and recovery are `source/episode/logbuf/`; `GUARANTEES.md`, the guarantees the sources make for the log and recovery (extracted by two other readers); and `CELLS.md`, environment contracts the log and recovery rely on (obligations on things outside `logbuf`), enumerated from these sources by other readers and given to you in a fixed order. TLC is at `$TLA2TOOLS`. You have no web access and need none. Your work must stay under 24 GB of memory; your session ends at six hours' wall clock, whatever state it is in.

## Task
1. Write a TLA+ model of the log and recovery **as the source implements them**; where the paper and the source disagree, follow the source and record the disagreement. Include every defence the sources describe or the code implements that bears on the guarantees.
2. State the guarantees of `GUARANTEES.md` that your model can express as invariants or properties.
3. Take the cells in `CELLS.md` in order. For each cell you can express, add an environment action that violates its contract, and run, for that cell, **two checks**: (a) **honest environment** (the contract kept): the guarantees hold; (b) **defence removed**: with the model's defence against this violation removed, the violation breaks a guarantee. If the model has no defence against the violation, the cell is **unguarded**: record it, with the guarantee its violation breaks; it is not a finding.
4. A **finding** is a cell, or any other violation of an obligation on something outside `logbuf`, that breaks a guarantee **with the model's defences in place**, while the honest-environment check holds. Report each one in the schema below, with its counterexample.
5. Rank your findings, most serious first, by your own judgement of their consequence for a running file system.

## Finding schema (exact; a script reads it)
```
### F<n>
- violated: <the obligation on something outside logbuf that the run violates; the CELLS.md id if it is one, else "new">
- mechanism: <how the violation, through the log and recovery's own steps, leads to the failure, in two to four sentences>
- effect: <what the file system, its users or operators see; the GUARANTEES.md id it breaks>
- defence: <the defence the model includes, and why it does not cover this>
- counterexample: <the path of the TLC trace file in this checkout>
- confidence: <high | medium | low> — <one line>
```

## Rules
- **Commit as you go**: the model, each check's output, and each finding as soon as you have it. Only what is committed when the session ends counts.
- Before building, commit `PREDICTIONS.md`: how many findings you expect and which cells you expect to be unguarded. Never edit it; amend additively.
- If a check's result looks wrong, say so; do not change the model to make a guarantee hold or fail without naming the source line the old model misread.
- Bounds: state, for every check, the bounds it ran at and what the violation needs the model to reach (the sizes and counts of everything the run involves); a check that cannot reach that is reported as such, not as a result.
- Write `REPORT.md` at the end: cells modelled, unguarded, findings, cells not reached (with the reason), disagreements between paper and source, and your declared limitations.
