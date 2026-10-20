# Brief: implementation author, adaptation to schedule format v2

You are the same author as before, or a successor with the same access. Your access list is unchanged: the three inputs, `testbed/schedule-format.md` (now v2; v1 is kept beside it), `testbed/schedules/` (new, shared, the only schedules that count), `observe/schema.md`, `AGENTS.md`, this brief, and `impl/`. The `model/` directory has been removed from your checkout on purpose; do not restore it or look for it. Do not read `docs/` beyond this brief.

## What changed and why
M1's cross-run showed that each author had written its own schedules and that none matched. The steward has now fixed the format (rules T1, T2, T3, A1, A2, E1, E2 in `testbed/schedule-format.md`) and written one shared set of thirteen schedules at the repository root, `testbed/schedules/`. Your compiler derives from the format; under v2 it is stale until adapted. Your private `impl/testbed/schedules/` stays as history but is no longer run. The cross-run found no defect in the implementation; the verdicts on the three divergences placed them in the model and in the format.

Two of the v2 rules change your compiler's behaviour: T1 (a trigger matches only events emitted after it was armed; it is not sticky) and A1 (`grantor`, `holder`, `rest` are valid wherever a process name is). E1 adds `end: quiescent`.

## What to do, in order
1. Commit your predictions first: for each of the thirteen shared schedules, your predicted verdict per seed before adapting; for each mutation, whether it will still fail on the shared schedule, and if not, where you will re-place it.
2. Adapt the compiler and runner to v2. `impl/run.sh <name>` resolves only `<repo>/testbed/schedules/<name>.yaml` (one directory above `impl/`). `end: quiescent` per E1, with your bounded wait and the liveness checker as E1 describes.
3. Re-place any mutation that no longer fails on its shared schedule; every mutation must fail on its pair's shared schedule, on the enforcing path of the clause.
4. Run `impl/run.sh --all --seeds 3` and `--mutations --seeds 3`. Record the outcome. If a prediction was wrong, say so additively; do not edit the prediction.
5. Update `impl/README.md`: new interpretations and the v2 changes, each tagged. Tag elements that derive from a v2 rule with the rule id beside the clauses and cells.
6. Commit the adapted version. Report: commit hash, per-seed results, mutation results, wall-clock time.

Your git is unsandboxed this time, in a full clone; stay inside it.
