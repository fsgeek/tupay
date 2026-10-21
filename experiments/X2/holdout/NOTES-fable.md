# Hold-out schedules H7, H8, H9: notes for the steward

Written from `packet.md` only (contract v2, failure model v2, pairs v3, schedule format v2.2 with v3 and v4 addenda, example P25). Nothing else was read.

Conventions used in all three: the process shape from the format (`n1..n3`, `c1`, `c2`, `s`), `bound: {events: 200}`, aliases resolved per Rule A1/L1. Values are symbolic (`v1..v4`). Tokens are written here as `t1 < t2 < ...` in grant order; the artifacts choose the integers.

---

## H7: a read is not a fence

**Targets.** C2.1 (both sentences, especially "serving a read does not change the highest accepted token"), C1.2 (acceptance is decided against the ledger, and only acceptance moves it), C2.2 (the final value), C1.3 (ack lost on a simplex link), under F1.3 (holder paused past lifetime) composed with F2.2 (`s->c1` down, `c1->s` up).

**Sequence.** c1 granted t1, writes v1 (ledger t1), paused. c2 granted t2 (the resume is triggered by that Grant, which satisfies the pause rule's own list). c2 reads: must be served with `highest_before = t1`, value v1. Then `s->c1` is dropped and c1 writes v2 with its stale token t1. Storage's decision on that write is the crux: the ledger is still t1, so `highest_before` must be t1 and, since t1 >= t1, the write is accepted. c1 never receives that ack. c2 then writes v3 (accepted, `highest_before = t1`, ledger -> t2); heal; c1 writes v4 with t1 -> rejected with `highest_before = t2`; c2 reads -> served, value v3.

**C1.4 premise after the last fault.** The last fault step is the heal; afterwards every link is up and nothing is crashed, so the premise holds trivially. No liveness claim is made beyond the steps being reachable; the end is `{event: ReadAck, client: c2}` rather than `quiescent` because Rule E1's definition of `quiescent` enumerates requests, writes and acks and was not updated by the v3 addendum to mention reads (see ambiguities, item 6).

**What a correct artifact must do.**
1. `ReadAccept(t2, highest_before = t1, v1)` and `ReadAck(c2, served, v1)` for c2's first read.
2. For c1's stale write of v2: a storage decision whose `highest_before` is t1. The letter of C1.2 ("only if") permits a `WriteReject` here, but a reject with `highest_before = t1` is a divergence to be explained, and a decision with `highest_before = t2` (or any `WriteReject` whose `highest_before` is a token no `WriteAccept` has carried) is a violation of C2.1's second sentence and of the ledger's definition.
3. No `WriteAck(c1, accepted)` reaches c1 while `s->c1` is down (messages are lost, not delayed). A retry by c1 that is accepted before c2's write, with its ack lost too, is fine; a retry after c2's accepted write must be rejected.
4. `WriteAccept(t2, highest_before = t1)` for c2's v3, then `WriteReject(t1, highest_before = t2)` for c1's v4 and `WriteAck(c1, rejected)`.
5. The final read: `ReadAccept(t2, t2, v3)`, `ReadAck(c2, served, v3)`.

**Mistake it is meant to catch.** Three, all plausible in careful work:
- Storage implements the read path by reusing the write path's "ledger := max(ledger, token)" step, or a "read establishes the fence" optimisation. Every shared pair with a read (P13-P18, P27-P30) has a newer *write* accepted before the stale read, so bumping on read is invisible to all 30 pairs.
- The grantor pushes the new token to storage on grant (so stale writes die immediately). Same signature: `highest_before = t2` with no accepted t2 write.
- A checker (either side) that encodes P3/P6/P15's intuition as "a paused holder's post-resume write is rejected", instead of "rejected iff a newer token has been accepted". H7 exercises the branch where it has not.
The F2.2 drop makes c1 blind to the outcome, so a client that infers "my write failed, the fence must have moved" and acts on it (for example, re-requesting with a new grant, or reporting success on a timeout) is also visible.

**P(at least one of two careful authors fails) = 0.45.**

---

## H8: a grant nobody received

**Targets.** C1.1 (strict increase across a token that was recorded but never delivered, and across a grantor incarnation), C1.4 (recovery of a lost request/grant without a new `request` step), C1.2 and C2.1 (the new holder's write is accepted; the old holder's stale read is rejected), under F2.2 (`grantor->c2` down only) composed with F1.1 (grantor crash-stop, no restart).

**Sequence.** c1 granted t1, writes v1. `grantor->c2` dropped. c2 requests; the request arrives (c2->grantor is up). The grantor records `Grant(c2, t2)`; the message is lost. On that Grant event the grantor crashes and stays down. The two remaining lease nodes elect among themselves. c2's `write: c2` waits under Rule T3 until c2 holds a token, so the write's `WriteAccept` is the liveness witness. Then c1 reads with t1 -> rejected.

**C1.4 premise after the last fault.** The last fault is the crash. The only down link is the crashed node's `n_g->c2`; every link among the other two lease nodes, storage and c2 is up in both directions, and all of them stay up. A majority of lease nodes (2 of 3), storage and the requester c2 are therefore connected to each other for the rest of the run: the premise holds and c2 must eventually obtain a grant. Note that it must do so with no further `request` action in the schedule: the only `request: c2` was answered by a grant that was lost.

**What a correct artifact must do.**
1. `Grant(c2, t2, grantor_term = T1)` recorded by the first grantor; no `Grant` received by c2 at that point (c2 holds nothing; a `write: c2` cannot proceed).
2. Eventually a second `Grant(c2, t3, grantor_term = T2)` with t3 > t2 and T2 > T1, recorded by a different node. (See ambiguity item 2: if the steward rules that a resend of the same grant is not a new grant, then t3 = t2 is acceptable only when the artifact's record identifies it as a retransmission; a fresh `Grant` record with token <= t2 is a C1.1 violation.)
3. `WriteAccept(t3, highest_before = t1)` and `WriteAck(c2, accepted)`.
4. `ReadReject(t1, highest_before = t3)` and `ReadAck(c1, rejected)`.
5. No `Grant` with a token <= t2 after the crash, whichever node leads.

**Mistake it is meant to catch.**
- Reply-before-replicate in the grantor: the Grant event is recorded when the grant is sent; if the grant reaches the followers only afterwards, the crash (which the model side places at every point after the trigger) can hit before replication, and the new leader reissues t2. In P1/P2 the client receives the grant, so an author can convince themselves that an undelivered token "does not count" and still pass every shared pair.
- No client-side retry of a lost request/grant. P8/P17 lose acks of writes and reads; P11 heals a partition; none of the 30 pairs forces a requester whose single request was answered into a void to recover on its own. A model with a one-shot `Request` message has no path to a grant here and fails its own liveness check; an implementation with a one-shot request stalls the same way. This is the "both wrong in the same way" case.
- A new leader that believes c2 already holds t2 for its full lifetime and therefore refuses c2's retries until the lifetime runs out passes (C1.4 says "for long enough"), but one that refuses forever ("you already hold a grant") fails.
- Checker side: a liveness check that only fires on a `request` step, not on "a client without a grant that has requested".

**P(at least one of two careful authors fails) = 0.5.**

---

## H9: connected is direct, and the grantor need not be in it

**Targets.** C1.4 under F2.1, with the "connected" definition of failure model v2 and Rule L3 read literally.

**Sequence.** c1 granted t1. The direct link between the grantor and c2 is cut both ways and stays cut. c2 requests. Nothing else happens.

**C1.4 premise after the last fault.** The last (and only) fault is the cut. Afterwards: the two non-grantor lease nodes are connected to each other, to storage and to c2 (no link among those four was touched). That is a majority of lease nodes, storage and the requester, up and connected to each other, so the premise holds and c2 must eventually be granted. The grantor is also still connected to both followers, so it keeps its leadership: nothing provokes an election.

**What a correct artifact must do.** Deliver a `Grant(c2, t2)` with t2 > t1 and have c2 receive it, by some path that does not use the grantor<->c2 link: a follower that forwards requests to the leader and relays the grant back, a leader that routes replies through a follower, a leadership transfer to a node c2 can reach, or an election design in which the followers notice. The clause does not say how. (A design where c2 contacts a follower, is *redirected* to the leader and then cannot reach it does not satisfy C1.4 here.)

**Mistake it is meant to catch.** The default in nearly every leader-based design: clients talk to the leader, directly, and followers at most redirect. Every shared liveness pair (P10-P12, P25, P26) leaves the requester connected to the node that ends up leading. H9 is the case where the leader is healthy with respect to its peers and unreachable only by the requester. Both authors plausibly build the default and both plausibly fail, and the model side may additionally pass by abstraction (a TLA+ model that treats "the grantor" as a single locus guarded by "connected to a majority" grants c2 without ever modelling who carries the message), which would produce a model-pass/impl-fail divergence rather than a shared failure.

This schedule is also deliberately a test of the inputs: if the steward's intent was that the requester must be connected to the leader (or to the grantor's majority including the grantor), the premise as written says otherwise, and H9 will show that the contract and the authors' reading have parted company (ambiguity item 1). Either outcome is informative; a result on H9 should be scored against whichever reading the steward fixes *before* the run, in writing.

**P(at least one of two careful authors fails) = 0.7.** (Lower, perhaps 0.5, if the steward amends C1.4 to name the grantor; then the schedule's premise no longer holds and H9 should be retired, not reinterpreted.)

---

## Ambiguities and contradictions found in the inputs

Listed in order of how much they matter to the hold-outs.

1. **C1.4's premise does not mention the grantor.** "A majority of lease nodes and storage stay up and connected to each other and to some requester" is satisfied by a majority that excludes the current leader, while the leader keeps its majority through the same nodes (H9). Under v1's transitive connectivity this could not happen; under v2 it can. The steward should state whether (a) the premise is literal (H9 is a legitimate test of request routing), or (b) the majority must include the node that will issue the grant, or (c) the requester must be connected to the grantor of the moment. Rule L3 restates the literal reading and so does not settle it.

2. **Retransmitted grants and C1.1.** `Grant(...)` is "recorded by the process that produces it"; a grantor that re-sends a grant to a client whose copy was lost (H8) produces a second `Grant` record with an equal token. C1.1 says "strictly greater than every token previously granted", so the literal reading makes the resend a violation. Network duplication (allowed on up links) is different: one record, two deliveries. The steward should say whether a grant is identified by its token or by its record.

3. **What is "a requester" after its request is lost?** C1.4 does not say whether the obligation covers a client whose only request vanished on a down link (H8). If the obligation is only to requests that arrive, a one-shot client is compliant; if it covers the client's intent to be granted, retry is mandatory. Related: Rule T3's "a request by a client that already has a request outstanding waits until that request is answered" has no answer when the request was lost, so a second `request` step for the same client can be unsatisfiable; neither H8 nor H9 issues one.

4. **The pause rule assumes grants are exclusive, but no clause says so.** The format says a `resume` "must be triggered by an event that can only happen after expiry (a later `Grant` to another client, ...)". Nothing in C1.1-C1.4 or C2.x forbids a grantor from granting to c2 while c1's grant is unexpired; a grantor that grants eagerly is contract-compliant, and then `Grant c2` does not imply expiry. H7 relies on the format's reading (resume at `Grant c2`). Also, the parenthetical list is either exhaustive or illustrative; the v3 addendum added reads but did not say whether a `ReadAck` under a later grant qualifies.

5. **`holder` after a lost grant.** Rule A1 defines `holder` as "the client that received" the most recent `Grant`. If the grant was lost (H8), the most recent Grant event has no receiver, so `holder` resolves to nothing, or to the previous holder, or to the addressee; the format does not say. Neither hold-out uses `holder`, for this reason. Likewise `grantor` can resolve to a crashed node; `restart: grantor` is then well-defined only if no newer Grant has occurred by the time the trigger fires, which the schedule cannot guarantee under Rule T2. A `restart` counterpart for `crash: grantor` (as v2.2 gave `non-grantor`) would remove the problem.

6. **Rule E1's `quiescent` predates reads.** It lists "no request, write or ack is in flight"; a read in flight is not named, so on the impl side a run may be declared quiescent with a read outstanding. H7 and H8 end on an explicit `ReadAck` for that reason.

7. **"Only if" everywhere, with no obligation to accept or serve.** C1.2, C2.1 and C2.2 are necessary conditions; C1.4 covers grants only. A storage that rejects every write and read satisfies every clause. The shared pairs impose acceptance implicitly, through triggers like `WriteAck ... accepted`; the hold-outs do the same. The steward may want a clause (or a testbed rule) that a write or read whose token is at least the ledger is accepted or served when storage is up and reached, otherwise "rejected" results are unexplained by design.

8. **Liveness evaluation on the model side is unspecified.** Rule E1 says how the impl side reports an unanswered request (through the liveness checker) but not how the model side decides C1.4: a temporal property under what fairness? Weak fairness on a client retry action, or on message delivery, is an author's choice that decides H8 and H9 and is invisible in the schedule. The pre-registration should name the fairness assumptions.

9. **`Fault` records as triggers.** The format says triggers "may name `Fault` records for the new actions as for the old", but no `Fault` event is defined in the contract's observable events, and its fields (cell, action, targets) are not given. Not used here.

10. **"Reordered" versus "not delayed".** Failure model v2 excludes "links that delay rather than lose" and fixes a message's fate at send, yet allows reordering on an up link, which is a form of delay. A message sent on an up link just before a `cut` is therefore delivered after the cut (fate fixed at send); whether delivery may occur *while* the link is down is something the two authors could read differently.

11. **F1.1 says "storage replica".** There is one storage process `s` in the shape; "replica" suggests replication the shape does not have. Harmless, but an implementation author may read it as licence for a storage design the model does not have.

12. **`non-grantor` in a link pair.** Rule L1 allows it, resolved to one node (impl: lowest-numbered; model: every). A `cut` listing `non-grantor` twice (for two different followers) cannot be expressed; `[[grantor, n2], [grantor, n3]]` with the ignore rule reaches both followers but only because the pair whose ends coincide is dropped. Worth saying explicitly, since schedules that need "the other follower" will otherwise be written wrong.

13. **`token: stale` is defined from the grantor's view.** "Lower than the highest token granted so far" is global knowledge; a client cannot know it. Fine for a testbed, but with lost grants (H8) "granted so far" includes a token no client holds, which is the reading the hold-outs rely on.

---

# Post-fix

Written against `packet-v2.md` (contract v2, failure model v2 with the fate-at-send sentence, pairs v3, schedule format v2.2 with v3/v4 addenda including L1 pairs-written-out, L3 literal reading and "requester", E1 extended to reads, E3, T3 restated, and observe/schema.md v1 to v4). Only that file and my own files were read.

## Re-estimates

| Schedule | Before | After | What moved it |
|---|---|---|---|
| H7 | 0.45 | 0.40 | Nothing in the fixes names H7's crux (a served read, or a grant, does not move the ledger; a paused holder's write is accepted when no newer token has been *accepted*); the small drop is because restated T3 now tells authors to handle a lost write ack, which removes the minor client-side branch of the trap. |
| H8 | 0.50 | 0.25 | Both of H8's cruxes are now stated: L3 says a lost request or grant does not end the client's standing as a requester (so retry is mandated), and schema v4 says a re-send is not a new `Grant` and a fresh grant carries a higher token (so the lost-token branch of C1.1 is spelled out). What is left is reply-before-replicate under a crash placed between the `Grant` record and its replication, and the successor-incarnation question in item P4 below. |
| H9 | 0.70 | 0.30 | L3 now states H9's premise reading verbatim (majority need not include the grantor, requester need not be connected to it, routing is the artifact's business). Authors who read it will build forwarding; what remains is getting the *return* path right under a both-ways cut (a follower that forwards the request but whose leader replies directly still fails), and the model-side abstraction mismatch that produces a model-pass/impl-fail divergence rather than a shared failure. |

## H10: the deaf follower

**Targets.** C1.4 under F2.2 applied among lease nodes in the direction no shared pair uses: one follower cannot hear the grantor (`grantor->non-grantor` down) while it can still send to the grantor and is connected both ways to the other follower, storage and both clients. C1.1 and C1.2 ride along through the witness write.

**Sequence.** c1 granted t1, writes v1 (ledger t1). Drop `grantor->nA`. c2 requests. `write: c2` waits for c2's token (Rule T3) and must be accepted with `highest_before = t1`. End `quiescent`.

**C1.4 premise after the last fault.** The only fault is the drop. Afterwards the grantor and the other follower nB are connected (both directions up), nA and nB are connected, and both of those majorities are connected to storage and to c2; everything stays up. The premise holds, so c2 must eventually obtain a grant, on every behaviour the model admits and within the impl's liveness window.

**What a correct artifact must do.** Keep, or re-establish and keep, a grantor that c2 can reach, long enough to process c2's request, despite a node that never hears a leader. Concretely, one of: (a) a candidate needs more than its own timeout to disturb the leader (pre-vote or an equivalent "does a majority also miss the leader" check: nA's pre-vote reaches nB, which has a leader, and is refused; the grantor keeps its quorum through nB and grants c2); (b) the deaf node is allowed to win and then stays leader (it hears nB and both clients; its heartbeats reach the old grantor, which follows it); (c) any other design under which the behaviour "nA bumps the term, the old grantor steps down, the old grantor wins the next election, nA cannot hear it and bumps the term again" is not an admissible infinite behaviour. Then `Grant(c2, t2)` with t2 > t1, `WriteAccept(t2, highest_before = t1)`, `WriteAck(c2, accepted)`.

**Mistake it is meant to catch.** Plain leader election with "step down on any higher term" and no pre-vote, which is the textbook default. On the branch where nA's log is current, nA wins with nB's vote and the run passes; on the branch where the old grantor keeps winning the elections nA provokes (it is connected to nB, and nA votes for it too, since nA->grantor is up), the leader is deposed on every one of nA's timeouts and the model side has an infinite behaviour with no grant to c2. That is a counterexample to C1.4 by the letter unless the model's fairness assumptions exclude it, and whether they do is exactly the thing item (8) asked the briefs to name. The impl side, with randomised timeouts, most likely converges on nB and passes, or spends its liveness window in churn and reports through E1/E3. So H10's expected signature is a model/impl divergence or an `UNEXPLAINED bound`, not a clean shared FAIL. Nothing in the fixed inputs mentions a follower that cannot hear its leader: P20 and P26 point the simplex failure the other way (grantor deaf to followers), P25 cuts both ways, and no pair has a node that can depose a leader it cannot hear.

**Satisfiability.** Every step fires on the pass branch: Grant c1, WriteAck c1 accepted, Grant c2 (from whichever node ends up granting; nA, nB and the original grantor are all connected to c2). `non-grantor` in the drop is one process per pair (Rule L1); the impl picks the lowest-numbered follower, the model explores both, and the schedule is symmetric in that choice.

**P(at least one of two careful authors fails) = 0.40.** Counted as "fails" if either side's liveness check witnesses the violation or the run ends `UNEXPLAINED bound` with no grant to c2.

## Why not the other residue candidates

- *Exclusive grants are never promised.* True and still unfixed (item 4), but a hold-out cannot score it: an eager grantor and a lease-respecting grantor are both compliant, and the pause rule's "resume at a later Grant" is the only place the assumption bites. Worth fixing in the format (say what `pause` means for an eager grantor), not worth a schedule.
- *A message sent before a cut, delivered after.* Now stated in the failure model. The consequences that remain untelegraphed are delivery to a process that crashed and restarted in between, and arrival after a heal, which are defects (P2 below), not author traps.
- *`holder` after a lost grant.* Still undefined (item 5). A schedule that uses it would be ambiguous in the compiler, which tests the format rather than the authors.

## New defects in the fixed inputs

P1. **Obtaining a grant is not an observable event.** `Grant` is recorded by the grantor when it sends; schema v4 says a client receiving a retransmission "records nothing new", which implies clients record something on first receipt, but no such event exists in the contract or schema. C1.4's conclusion ("obtains a grant") is therefore not directly witnessable from the trace; H8, H9 and H10 use the client's next `WriteAttempt` with the new token as the witness, and the liveness checker must do the same or be given a receipt event (`GrantAck(client, key, token)`, say). Rule L3's "a requester ... has not yet received a grant" has the same gap.

P2. **Late delivery versus crash and heal.** The new sentence fixes a message's fate at send and allows late arrival after the link goes down. It does not say whether a message sent to q while q was up is delivered to q after q crashes and restarts (F1.1), nor whether "late" can extend past a heal. A model that drops a crashed process's inbox and an implementation whose TCP connection survives a restart will differ here; it should be settled either way.

P3. **"Not in v2: links that delay rather than lose" now sits beside "it may arrive late, reordered".** The intent is clear (delay is not a *fault*) but the two sentences read as a contradiction to a fresh author; one clause saying "ordinary delivery may be arbitrarily late; a fault never delays" would remove it.

P4. **Retransmission by a successor incarnation.** Schema v4 permits "a grantor that re-sends a grant it has already recorded". In H8 the node that recorded the grant is dead; the new leader holds the entry in its replicated log but did not record the `Grant`. Whether it may retransmit t2 (no new record) or must issue t3 (new record) is not said. Both readings are defensible and the two authors may pick different ones; the checker needs a ruling.

P5. **The bound is side-dependent.** `bound: {events: 200}` counts events, and restated T3 now obliges clients to retry rather than wait for ever. Every retry is a fresh `WriteAttempt`/`ReadAttempt`/`Request` record on the impl side, while the model may fold retries into one message or explore them lazily; the impl can hit the bound (E3: `UNEXPLAINED bound`) on a run the model finishes. The bound should either exclude retries and `Fault` records or be stated per side. Also: whether `Fault` records from `proc: "env"` count toward the bound is not said.

P6. **The liveness claim lives in a comment.** Rule L3 keys the premise check to "a schedule whose comment claims" a grant; a compiler cannot check a comment, and a schedule with no comment and a C1.4 derivation tag is in limbo. A field (`claims: [C1.4]`, or reading it off `derives`) would make the check mechanical.

P7. **Rule A1 `holder` still says "the client that received it".** Unchanged residue, now sharpened by schema v4: a retransmitted grant is received but recorded by nobody, so a compiler that resolves `holder` from the trace has nothing to resolve it from. Resolving `holder` to the `client` field of the most recent `Grant` record (the addressee, whether or not it received it) would be consistent with P1 and with how `grantor` is resolved.

P8. **Failure model v2 changelog lost its reason.** The reason for v2 formerly cited `docs/seed.md` and now says "the parameter change held out in v1's 'Not in v1'"; harmless, noted only because the project's discipline is that reasons are traceable.
