# Model-side predictions (pre-registered before any TLC run)

derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 (pairs P1 to P12 and the M1 false-suspicion run)

Committed before the model exists and before any TLC run. Amendments are additive and say whether an outcome informed them.

## Scoring
`model/run.sh <schedule>` prints `PASS`, `FAIL <invariant>`, or `UNEXPLAINED <reason>`.
A prediction is met when the printed verdict equals the predicted one exactly.
`model/run.sh --mutations` is met when every mutation prints `FAIL` naming the invariant listed below.
Any other verdict is reported as a miss, not re-explained after the fact.

## Unmutated model
| Run | Predicted |
|---|---|
| P1 .. P12 | PASS |
| false-suspicion-v1 | PASS (observed, not judged; the observe file must let every WriteAccept/WriteReject be traced to a Grant and grantor_term) |

## Mutations (one break each, on the enforcing path)
| Mutation | Break | Predicted |
|---|---|---|
| P1 | lease nodes do not durably record the highest token issued; it is lost on crash | FAIL C1_1 |
| P2 | the grantor issues a grant without confirmation from a majority of lease nodes | FAIL C1_1 |
| P3 | the grantor reissues its last token instead of incrementing | FAIL C1_1 |
| P4 | storage's fence ledger is volatile: reset to 0 on restart | FAIL C1_2 |
| P5 | storage accepts without comparing the token to the ledger | FAIL C1_2 |
| P6 | storage does not record the accepted token as the new highest | FAIL C1_2 |
| P7 | storage acks acceptance on receipt, before deciding; the decision is volatile | FAIL C1_3 |
| P8 | a client cut off from storage presumes its outstanding write succeeded | FAIL C1_3 |
| P9 | a client records any ack carrying its current token as success, ignoring the outcome | FAIL C1_3 |
| P10 | election requires every lease node rather than a majority | FAIL C1_4 |
| P11 | a grant consumes the request when issued, so a reply lost in a partition is never reissued | FAIL C1_4 |
| P12 | the grantor will not grant to another client until the previous holder releases (expiry ignored) | FAIL C1_4 |
