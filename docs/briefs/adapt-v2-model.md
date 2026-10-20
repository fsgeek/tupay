# Brief: model author, adaptation to schedule format v2 (and the P10 verdict)

You are the same author as before, or a successor with the same access. Your access list is unchanged: the three inputs, `testbed/schedule-format.md` (now v2; v1 is kept beside it), `testbed/schedules/` (new, shared, the only schedules that count), `observe/schema.md`, `AGENTS.md`, this brief, and `model/`. The `impl/` directory has been removed from your checkout on purpose; do not restore it or look for it. Do not read `docs/` beyond this brief.

## What changed and why
M1's cross-run showed that each author had written its own schedules and that none matched. The steward has now fixed the format (rules T1, T2, T3, A1, A2, E1, E2 in `testbed/schedule-format.md`) and written one shared set of thirteen schedules. Your compiler derives from the format; under v2 it is stale until adapted. Your private `model/schedules/` stays as history but is no longer run.

## The judge's verdict on P10 (explained, locus: model)
On a schedule that crashes a non-leader before the first grant, TLC finds a liveness violation of C1_4. The judge's reading of the lasso: n3 is elected leader of term 1 by the non-maximal majority {n1, n3}, so `promised = [n1 |-> 1, n2 |-> 0, n3 |-> 1]`; n1 then crashes; c1 requests. `Grant(n3, c1)` needs a majority already promised to term 1, which no longer exists. `Elect(n2)` is disabled because n2 can see an up, connected leader whose term is at least n2's promise. `StepDown(n3)` is disabled because nobody has promised higher. The model has no action by which a leader brings a lagging follower into its term, so it stutters forever with a majority, storage and the requester all up and connected. The TLC counterexample is in `model/evidence/P10-cross-run-counterexample.txt`. The shared `P10.yaml` now begins with exactly this case.

This is yours to fix in `model/`. Do not weaken `C1_4`, the fairness conditions, or the failure-model actions to make it pass. Record what you changed and why as an interpretation.

## What to do, in order
1. Commit your predictions first: for each of the thirteen shared schedules, your predicted verdict before adapting; for each mutation, whether it will still fail on the shared schedule, and if not, where you will re-place it.
2. Adapt `compile.py`, `run.py` and `Lease.tla` to v2. `run.sh <name>` resolves only `testbed/schedules/<name>.yaml`. `end: quiescent` per E1.
3. Fix the P10 defect.
4. Re-place any mutation that no longer fails on its shared schedule; every mutation must fail on its pair's shared schedule, on the enforcing path of the clause.
5. Run `run.sh --all`. Record the outcome. If a prediction was wrong, say so additively; do not edit the prediction.
6. Update `model/README.md`: new interpretations, the fix, the v2 changes, each tagged. Tag elements that derive from a v2 rule with `derives: ... ; format v2 T1` style notes in addition to clauses and cells.
7. Commit the adapted version. Report: commit hash, per-schedule results, mutation results, what you changed for the fix, wall-clock time.
