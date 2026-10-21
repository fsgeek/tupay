# Model-side predictions, X2 routing fix (after scoring)

derives: C1.1, C1.4, F2.1, F2.2; format v4 L3; observe v4 addendum ("Grants and retransmission"); pairs v3

Additive. The earlier prediction files are not edited. Committed after reading `docs/briefs/fix-x2-routing.md` and H7-H10, and before any change to the model or any TLC run in this round. Scoring is unchanged.

## The defect, as I read it
My X2 interpretations X2.4 (a grant is issued only to a requester the grantor is connected to) and X2.5 (no forwarding) misread format v4 Rule L3 and failure model v2's F2.1 and F2.2.
- Under L3, C1.4's premise can hold through the followers while the requester cannot exchange messages with the grantor. In H9 this is a two-way cut, F2.1.
- In H8 the grantor hears the request but cannot answer it (F2.2). The model refused to record a `Grant`, so the crash step, which fires on that `Grant` event, never fired.
- X2.5 already named the H9 shape as a limit of the model. The judge's verdict is that it is a violation, not a limit.

## Plan, fixed before predicting
- **One-hop relay through a lease node.**
  - `ReqRoute(c, n)`: c→n is up, or some up lease node f has c→f and f→n up.
  - `RepRoute(n, c)`: the same in the other direction.
  - A request, which is retried, reaches the leader by either route. A grant reply goes back by either route, and its fate is fixed when the leader sends it.
  - Why one hop is enough: a leader that keeps its place has, by CheckQuorum, a majority it is connected to. That majority shares a member f with the majority in C1.4's premise, and f is connected to both the leader and the requester.
- **A grant that cannot be delivered is still recorded.**
  - `Grant(n, c)` needs only that the request reaches n. The reply is put in flight only if `RepRoute(n, c)` holds; otherwise it is lost, but the `Grant` is still recorded (H8).
  - To keep the model finite, and as observe v4 describes, a leader issues at most one grant per request it hears, per term. `Resend(n, c)` retransmits the same token, with no new `Grant` record, while the request is still outstanding and a reply route exists.
  - A new leader issues a fresh grant with a higher token.
  - Two new variables: `rq` (a per-client request counter) and `issued` (a history of the grants each leader issued, keyed by term). A node never leads the same term twice, so their loss on a crash need not be modelled.
- **Fairness.** `WF(Resend(n, c))` is added. Its enablement depends only on the leader's own record and on links that are up.
- **Stale tags.**
  - `run.py`: the header (it still says "P1-P12 and M1") and `mutations()` (it names only P1-P12).
  - `mutate.py`: the docstring ("twelve") and the tag on `build()`.

## Schedules (35)
| Schedule | Predicted | Note |
|---|---|---|
| P1 .. P30, false-suspicion-v1 | PASS | Under bipartitions, a relay route exists exactly when a direct one does, so v1 behaviour is unchanged. P19-P30 never need a relay. State counts may change slightly because of the new variables. |
| H7 | PASS | No lease-node routing is involved. |
| H8 | PASS | The grantor hears c2 directly. The reply goes through a follower (n→f→c2 is up), so it is delivered and the crash step fires on the `Grant`. After the crash, c2 holds t2 and writes; its write is accepted with `highest_before = t1`, and c1's stale read is rejected. |
| H9 | PASS | The request and the grant both go through a follower. |
| H10 | PASS | The deaf follower cannot form a connected quorum: the other follower still hears the grantor and refuses (stickiness). The grantor keeps its majority and grants c2 directly. |

Before the fix, H8 and H9 would print `FAIL C1_4`, as scored in X2. I will keep that evidence by running the pre-fix model on them first and saving the counterexamples under `model/evidence/`.

## Mutations (30)
All are unchanged in intent: P1-P3, P19 and P20 `FAIL C1_1`; P4-P6, P21 and P22 `FAIL C1_2`; P7-P9, P23 and P24 `FAIL C1_3`; P10-P12, P25 and P26 `FAIL C1_4`; P13-P15, P27 and P28 `FAIL C2_1`; P16-P18, P29 and P30 `FAIL C2_2`.
- The texts that replace whole definitions gain the new variables in their `UNCHANGED` lists. This is mechanical.
- No new mutation is required: no pair was added. I will also check that removing the relay brings back `FAIL C1_4` on H9 and H8. That is a check, not a registered mutation.

## Interpretations expected to change
- **X2.4**: contradicted. Replaced by "recorded when heard, delivered by route, retransmitted by the same leader".
- **X2.5**: contradicted. Replaced by the one-hop relay through a lease node.
- **7 (grant retries)**: extended. The same leader retransmits the same token; only a new leader issues a fresh one.
- **Fairness table**: extended with `WF(Resend)`, and `Grant`'s enablement is restated in terms of routes.
