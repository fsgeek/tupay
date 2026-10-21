# Model-side predictions, round 2.1 (format v2.1: T1 clarified, `non-grantor` selector)

derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3; format v2.1 T1, A1

Additive. `PREDICTIONS.md` and `PREDICTIONS-v2.md` are not edited. Committed after reading the v2.1 brief, the format diff and the rewritten `testbed/schedules/P10.yaml`, and before any change or TLC run in this round. Scoring is unchanged.

## Unadapted model (v2, as merged)
- The rewritten P10 would print `UNEXPLAINED schedule rejected: unknown or ill-typed process 'non-grantor'`. I will not run this.
- The other twelve schedules are unchanged, and I predict the same verdicts as in round 2.

## Adapted model
| Schedule | Predicted |
|---|---|
| P1 .. P9, P11, P12 | PASS |
| P10 (rewritten) | PASS |
| false-suspicion-v1 | PASS (observed, not judged) |

- **T1 clarification.** No behaviour change: the rule is my reading R2.1. Only the tags change.
- **Rewritten P10 without the round-2 fix.** It still exposes the defect: `FAIL C1_4`. The route is a non-maximal election {x, y}, then a grant, then `crash: non-grantor` takes the other member, and the third node never joins the term. I will run this once as a discrimination check, using the fixed model with only `Join` removed.

## Mutations
| Mutation | Predicted on the shared schedules |
|---|---|
| P1, P2, P3 | FAIL C1_1 |
| P4, P5, P6 | FAIL C1_2 |
| P7, P8, P9 | FAIL C1_3 |
| P10 unanimity election | FAIL C1_4. The first two grants still succeed: one leader, with two promised nodes up. After the follower returns and the grantor crashes, no election can be unanimous. |
| P11, P12 | FAIL C1_4 |

No mutation needs re-placing.
