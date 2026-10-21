# Model-side predictions, X2 adapt arm (failure model v2: partial and simplex partitions)

derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2; format v4 (cut, drop, L1-L3, E1, E3, T3); observe v4 addendum; pairs v3 (P1-P30)

Additive. The earlier prediction files are not edited. Committed after reading the X2 brief, `contract/v2.md`, `failure-model/v2.md`, `tests/pairs-v3.md`, the format v4 addendum, the observe v4 addendum, the 31 shared schedules and this directory, and before any change to the model or any TLC run in this arm. Scoring is unchanged: a schedule's verdict is the one line `run.sh` prints; a mutation counts as working only if it prints `FAIL <its clause>`.

## Plan, fixed before predicting
- **Links replace sides.** `sideA` (one side of a bipartition) cannot express F2.1 or F2.2. It is replaced by `down`, the set of directed links that are down. `Link(p, q)` means p→q is up. `Conn(p, q)`, "connected", becomes both directions of the direct link up (failure model v2). F1.2 `partition` adds every crossing pair in both directions; `cut` adds each listed pair in both directions; `drop` adds each listed pair in the listed direction; any `heal` empties `down` (L2).
- **A message's fate is fixed when it is sent.** Every send checks the one directed link it uses, at the moment of sending: a write or read checks client→storage, an ack checks storage→client. A message already in flight is no longer dropped when a link goes down. This contradicts my v1 interpretation 13 (a partition dropped in-flight messages whose endpoints ended up on different sides).
- **The abstract grantor, link by link.**
  - Hearing a leader is directional: node n hears leader m iff m→n is up. `Elect(n)` needs that n hears no current leader.
  - A vote and a grant confirmation are round trips, so the quorum members must be connected to the candidate or leader (both directions).
  - **Voter stickiness (new).** A node votes only if it hears no current leader itself (a pre-vote check). Under v1 this is a no-op in every case that matters: a node that cannot hear the leader is on the far side of a bipartition, and so is every node it can reach. Under F2.1 it is what keeps the cut-off follower in P19 and P25 from disrupting a grantor that still has a majority. Without it, elections through the middle node can cycle, and the term bound would end the run as UNEXPLAINED.
  - **Quorum check (new, `CheckQuorum(n)`).** A leader that is not connected to a majority (itself included) steps down. Under F2.2 (P20, P26) the followers still hear a grantor that cannot hear them, so without this nobody would ever elect.
  - `StepDown(n)` needs to hear the node with the higher promise (q→n up). `Join(n, q)` needs only n→q.
  - `Grant(n, c)` is taken only when n and c are connected. A grant sent into a down link is not modelled (interpretation in the README).
- **C1.4's premise (L3).** `Good(c)`: storage and c are up, c is not paused, c and storage are connected, and some majority Q of up lease nodes is pairwise connected and connected to storage and to c. Under v1 bipartitions this is equivalent to the old `Good(c)`.
- **Fairness.** The same weak fairness as before, plus `WF(CheckQuorum(n))`. The README will name every condition and its justification under the brief's rule.
- **Compiler.** `cut` (F2.1), `drop` (F2.2), `heal` under F1.2, F2.1 and F2.2. Selectors `grantor`, `holder`, `non-grantor` are allowed in a link; `rest` is rejected (L1). Self-pairs are dropped at run time (L1). `MaxTerm` counts `cut` and `drop` steps as fault steps.
- **Exporter.** A `cut` or `drop` Fault record carries `links`, the directed links taken down after resolving selectors and removing self-pairs. Every heal record carries `links: []` and `heal: true`.

## Schedules (31)
| Schedule | Predicted | Note |
|---|---|---|
| P1 .. P18 | PASS | Removing in-flight drops only removes behaviours, so safety cannot newly fail. Stickiness and CheckQuorum change no v1 liveness outcome. State counts will change. |
| false-suspicion-v1 | PASS | |
| P19 | PASS | One leader throughout. Stickiness keeps the cut-off follower from electing through the middle node. |
| P20 | PASS | The grantor steps down by CheckQuorum; n2 or n3 is elected and grants. |
| P21 | PASS | The cut grantor cannot confirm; the other two elect; c1's stale write is rejected. |
| P22 | PASS | |
| P23 | PASS | c1 may still be told v1 succeeded, if the ack was sent before the cut; v1 was accepted, so that is not a violation. |
| P24 | PASS | |
| P25 | PASS | The grantor keeps its majority with the middle node (Join if needed); the cut-off follower cannot elect. |
| P26 | PASS | Depends on CheckQuorum under weak fairness. Without it, this would be FAIL C1_4. |
| P27 | PASS | |
| P28 | PASS | |
| P29 | PASS | As P23: a read ack sent before the cut may still be delivered. |
| P30 | PASS | |

## Mutations (30)
**P1-P18.** Unchanged breaks, re-applied mechanically. `Restart` replacements name `down` instead of `sideA`. P18's anchor changes from `Conn(Store, a.c)` to `Link(Store, a.c)`. P8, P11 and P17 keep `Conn`, which now means "connected"; on their bipartition schedules this is the same as before. Predicted as before: P1-P3 `FAIL C1_1`, P4-P6 `FAIL C1_2`, P7-P9 `FAIL C1_3`, P10-P12 `FAIL C1_4`, P13-P15 `FAIL C2_1`, P16-P18 `FAIL C2_2`.

**New mutations, named here before running:**
| Mutation | Break (on the clause's enforcing path) | Predicted |
|---|---|---|
| P19 | A voter that still hears the leader lends its vote to a candidate without promising the new term (a pre-vote counted as a vote). The cut-off follower is elected through the middle node, which stays promised to the old term. The old grantor keeps confirming grants through it, and once the new leader brings the middle node into its term, it grants from a stale token. | FAIL C1_1 |
| P20 | A newly elected leader starts from its own durable `maxTok`, not the highest over its quorum. On P20 the only leadership change is the one the F2.2 step-down causes. Not specific to F2.2, like P3. | FAIL C1_1 |
| P21 | Storage defers to a grantor it can still reach: it accepts a token below the ledger when the node that issued it is connected to storage and still believes it leads. On P21 the cut grantor reaches storage and may not yet have stepped down. | FAIL C1_2 |
| P22 | Storage keeps the fence per client (the highest token accepted from that writer), not per key. The old holder, which hears no lease node, presents its own old token. Not specific to F2.2. | FAIL C1_2 |
| P23 | A client that has lost only its storage link, and still reaches a lease node, presumes its outstanding writes succeeded. This is v1's transitive reasoning: a real partition would have cut it from the lease nodes too. | FAIL C1_3 |
| P24 | A client that can send to storage but hears nothing back presumes its outstanding writes succeeded, possibly before storage decides. | FAIL C1_3 |
| P25 | The grantor will not grant while any lease node is unreachable: it waits for the whole configuration. Under F2.1, progress depends on the majority sufficing. | FAIL C1_4 |
| P26 | CheckQuorum counts the followers the grantor can send to, not the ones it is connected to. The P26 grantor therefore never steps down, the followers keep hearing it, and nobody elects. | FAIL C1_4 |
| P27 | The read counterpart of P21: storage serves a read below the ledger when the token's grantor is connected to storage and still believes it leads. | FAIL C2_1 |
| P28 | The read counterpart of P22: storage fences reads per client. | FAIL C2_1 |
| P29 | A client that has lost only its storage link, and still reaches a lease node, answers its outstanding read from its cache: the value it last read, or `"none"` if it has read nothing. | FAIL C2_2 |
| P30 | A client that can send to storage but hears nothing back presumes its outstanding read was served, with the value of the last write it was told succeeded, possibly before storage serves it. | FAIL C2_2 |

**Risks named before running.**
- **P19's mutation may print UNEXPLAINED (MaxTerm bound) instead of FAIL C1_1.** The mutated voters also let elections cycle. TLC stops at the first violated invariant in breadth-first order, so if the term bound is reached at a shallower depth than the duplicate token, the run is UNEXPLAINED. I expect the duplicate token at a depth of about 7 after the cut, and the bound needs about 5 more elections of about 3 steps each.
- **P26 and P20 rest on `WF(CheckQuorum)`.** I expect to justify it under the brief's rule: its enablement depends only on the leader's own state, a timer that runs out because it has not heard from a majority. It does not require hearing anything over a down link.

## Previous interpretations expected to change
- **13 (messages)**: contradicted. A message in flight is not dropped when a link goes down later.
- **17 (C1.4's condition)**: extended. "Connected" is direct and bidirectional, and the majority must be pairwise connected (L3).
- **5 (grantor abstraction)**: extended. "Cannot reach a leader" becomes "does not hear a leader" (directional). Voters apply the same check (new), and CheckQuorum is new.
- **R2.5 (Join)**: extended. It needs only the leader→node link.
- **7 (grant retries)**: extended. A grant is issued only to a connected requester.
- **12 (compiler rejections)**: extended. F2.1 and F2.2 are accepted; `rest` in a link is rejected.
- **20 (Fault records)**: extended with `links` and the heal record.
- **R2.2 (E1 "in flight")**: extended. A message sent on an up link stays in flight after the link goes down. A message sent on a down link is never in flight.
- **TLC bound on terms**: extended. `MaxTerm` counts `cut` and `drop`.

## Outcome (appended after the runs; the predictions above are unedited)
- **Schedules.** All 31 print `PASS`, as predicted. State counts are in the README X2 section. P3, P4, P6, P7, P9, P10, P12, P13, P15, P16 and P18 have exactly their X1 state counts (P10 reports depth 16, not 15). The others changed, as expected, because in-flight messages survive partitions and because of CheckQuorum.
- **Mutations.** All 30 print `FAIL` on the predicted clause: P1-P3, P19 and P20 `C1_1`; P4-P6, P21 and P22 `C1_2`; P7-P9, P23 and P24 `C1_3`; P10-P12, P25 and P26 `C1_4`; P13-P15, P27 and P28 `C2_1`; P16-P18, P29 and P30 `C2_2`.
- **Named risk, P19.** It did not materialise. The duplicate token was found at depth 12, before the term bound. The route was as predicted: n3, cut from n1, was elected in term 2 through n2, and granted token 2 again.
- **Partial miss, P21.** The counterexample's stale accept is c1's v1 write delivered a second time (the `MaxDups = 1` duplicate), not its v3 write. It is still the predicted break, storage deferring to a grantor it can reach. The route differs from the one I described.
- **Interpretations.** Each one I listed changed as predicted. Not predicted, and added in the README: X2.4 (grants go only to a connected requester, an under-approximation under F2.2), X2.5 (no forwarding: a limit on C1.4 under L3 that no shared schedule exercises), X2.6 and X2.7.
