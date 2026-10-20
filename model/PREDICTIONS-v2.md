# Model-side predictions, round 2 (format v2, shared schedules, P10 fix)

derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3; format v2 T1, T2, T3, A1, A2, E1, E2

Additive to `PREDICTIONS.md`, which is not edited. Committed after reading the shared
schedules in `testbed/schedules/`, format v2 and `model/evidence/P10-cross-run-counterexample.txt`,
and before any change to the model, compiler or runner and before any TLC run in this round.
Scoring is unchanged: a prediction is met when `run.sh` prints exactly the predicted verdict.

## Unadapted model (commit as received) on the shared schedules
- Every shared schedule uses `end: quiescent`, which the v1 compiler rejects, so every run would print
  `UNEXPLAINED schedule rejected: ...`. I will not run this; it is stated so that the adaptation is visibly needed.
- With `end` hand-patched, the P10 shared schedule would print `FAIL C1_4`. This is the defect the judge found,
  and I accept the judge's reading of the lasso.

## Adapted and fixed model (what `run.sh --all` will be scored against)
| Schedule | Predicted | Note |
|---|---|---|
| P1 | PASS | |
| P2 | PASS | |
| P3 | PASS | |
| P4 | PASS | |
| P5 | PASS | |
| P6 | PASS | |
| P7 | PASS | |
| P8 | PASS | |
| P9 | PASS | |
| P10 | PASS | only with the fix (a leader brings a lagging follower into its term) |
| P11 | PASS | relies on the step-4 `request: c1` event satisfying step 5's `{event: Request, client: c1}` trigger, armed by that same action (see the interpretation of T1 below); under the strictest reading, P11 would print `UNEXPLAINED end unreachable` |
| P12 | PASS | |
| false-suspicion-v1 | PASS | observed, not judged |

Planned interpretation of T1: an action's own event is emitted after its own arming moment, so the event that step *i*−1's action emits can satisfy step *i*'s trigger. This matches what I did in v1.

## Mutations on the shared schedules
| Mutation | Still fails on the shared schedule? | Predicted |
|---|---|---|
| P1 maxTok lost on restart | yes | FAIL C1_1 |
| P2 grant without majority confirmation | yes | FAIL C1_1 |
| P3 no token increment | yes | FAIL C1_1 |
| P4 ledger reset on storage restart | yes | FAIL C1_2 |
| P5 comparison skipped | yes | FAIL C1_2 |
| P6 ledger not advanced on accept | yes | FAIL C1_2 |
| P7 ack on receipt, before the decision | yes | FAIL C1_3 |
| P8 client cut off from storage presumes success | yes | FAIL C1_3 |
| P9 ack with the current token counted as success | yes (c1's stale write uses its current token 1 and is rejected) | FAIL C1_3 |
| P10 unanimity election | yes (n1 is crashed from the start) | FAIL C1_4 |
| P11 one-shot request consumed at grant issue | **no**: no grant reply crosses the cut in shared P11 | PASS if left in place, so it will be re-placed |
| P12 grantor waits for the holder's release | yes | FAIL C1_4 |

**Re-placement of P11.** The new break is that a request made while the requester cannot reach a majority of lease nodes is lost and never retried, the client still waits, and after the heal the new grantor never learns of it. The break is in `DoRequest`, on C1.4's path from request to grant, and it is specific to partitions. Prediction for the re-placed P11 mutation: `FAIL C1_4`.
