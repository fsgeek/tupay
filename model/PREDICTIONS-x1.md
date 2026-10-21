# Model-side predictions, X1 adapt arm (contract v2: fenced reads)

derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3; format v3 (read), observe v2 addendum

Additive. The earlier prediction files are not edited. Committed after reading the X1 brief, `contract/v2.md`, `tests/pairs-v2.md`, the format v3 addendum, the observe v2 addendum and P13-P18, and before any change or TLC run in this arm. Scoring is unchanged.

## Plan, fixed before predicting
- **Reads.** A read is modelled like a write.
  1. A `read` step sends a read message carrying the client's token, and a read id (the step index).
  2. Storage decides: it serves iff `token >= highest`, returns its current value, and does not touch the ledger.
  3. A queued ack is sent in a separate step, and the client records `ReadAck`.
- **New invariants.** Both are stated over history:
  - `C2_1`: every served read's token is at least every token accepted by a write before it, and the read decision leaves storage's ledger unchanged.
  - `C2_2`: every value a client was given has an earlier serve decision for the same client, token and read, with the same value, and that value equals what storage held at the decision.

## Schedules (19)
| Schedule | Predicted |
|---|---|
| P1 .. P12 | PASS (unchanged schedules; reads only add variables that these schedules never use) |
| false-suspicion-v1 | PASS |
| P13 | PASS |
| P14 | PASS |
| P15 | PASS |
| P16 | PASS |
| P17 | PASS |
| P18 | PASS |

## Mutations (18)
**P1-P12.** All are unchanged and fail as before: P1-P3 `FAIL C1_1`, P4-P6 `FAIL C1_2`, P7-P9 `FAIL C1_3`, P10-P12 `FAIL C1_4`. Each one still sits on its v1 clause's enforcing path; reads do not change those paths.

**New mutations, named here before running:**
| Mutation | Break (on C2.x's enforcing path) | Predicted |
|---|---|---|
| P13 | the fence ledger is volatile: storage restarts with `highest = 0`. This is the same locus as P4, since a read is fenced by the same ledger; it is exercised on the read path. | FAIL C2_1 |
| P14 | storage serves reads without comparing the token to the ledger | FAIL C2_1 |
| P15 | storage serves a read whose token is one below the ledger (a "grace" for the immediately preceding holder, whose lease has just expired) | FAIL C2_1 |
| P16 | storage acks "served", with the value it holds, on receipt of a read, before its volatile decision | FAIL C2_2 |
| P17 | a client cut off from storage presumes its outstanding read was served, with the value of a write it was told succeeded | FAIL C2_2 |
| P18 | storage fills a read ack's value when it sends the ack, not when it serves the read, so a late ack carries a newer value | FAIL C2_2 |

**Expected gap.** No mutation breaks C2.1's second sentence, "serving a read does not change the highest accepted token". On these schedules, a read that raised the ledger could only raise it to the reader's own token, which is never above the ledger at that point. `C2_1` checks that sentence anyway.
