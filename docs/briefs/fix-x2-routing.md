# Brief: both authors, the X2 routing fix (after scoring)

Same access list as your X2 brief; the other side's directory, `experiments/` and the steward's docs are absent on purpose. Four schedules that were hold-outs in X2 are now shared: `testbed/schedules/H7.yaml` to `H10.yaml`. Nothing else in the inputs changed.

**The verdict.** In X2 your artifact failed C1.4 on H8 and H9. A judge from a third model family found both to be genuine violations, by one mechanism: a leader that keeps its lease-node quorum but cannot exchange messages with the requester, while nothing relays the request through followers and nothing replaces the leader. CheckQuorum keeps the leader; followers that hear it never elect; C1.4's premise holds through the followers (format Rule L3: the majority need not include the grantor, and the requester need not reach it; how a request reaches a node that can grant, and how the grant comes back, is the artifact's business). On H8 your artifact also declines to record a `Grant` it cannot deliver, so the schedule's crash step never fires; the premise already holds after the earlier fault.

Fix your artifact so that it meets C1.4 on these shapes. How is yours to choose; record the choice as an interpretation, with the clause and cell it derives from. Also fix any stale derivation tag you find (the model's runner has one at the top of `model/run.py`).

**Order.** Predictions first, committed: the verdict for all thirty-five shared schedules and every mutation, and which interpretations you expect to change. Then the fix, then a run of everything, README additively, adapted-version commit. Report: commit hash, results, interpretations (new, extended, contradicted), wall-clock time, and **declared limitations**: any shape of schedule you believe your artifact would still fail, and why you left it.

If the unmutated artifact fails a shared schedule, that is a result: record it and keep the evidence; do not change the artifact to make it pass without naming the clause or cell the old behaviour misread. The steward may run your artifact on schedules you have not seen, under any name.
