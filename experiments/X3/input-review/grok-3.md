I'll start by reading REVIEW-BRIEF.md and following its instructions.I'll read the five input files next, then review them for ambiguities, contradictions, and impossible or vacuous clauses.I'll read all five input files in full so the review is based on the actual text.I’ve got the five inputs. Next I’ll cross-check the new clauses, cells, and events against each other for contradictory readings.The v3 inputs leave two faithful authors with different protocols, and a few clause combinations that cannot all be kept. Defects are ranked by how much they would change what those authors build.

## 1. Re-addition eligibility is a global predicate the grantor cannot evaluate (C3.2, C3.5, F3.3, schema part 1)

**Where.** Contract “Eligible vote”; F3.3; schema decision-replay part 1 (“votes were eligible”).

**Why.** A vote from incarnation *i* > 0 counts only if “a configuration listing the node was committed from a request **sent after** the amnesia that began that incarnation.” Send time of `ReconfigSend` and amnesia time are environment facts. A lease node sees the request when it arrives, the incarnation on the `Vote` message, and commits it has recorded. Link rules allow a request sent **before** amnesia to be delivered **after** restart. The same local picture (new incarnation, request in hand, commit listing the node) is eligible on one history and ineligible on another.

C3.2 requires the decider to count only eligible votes. C3.5 requires that count to be a function of inputs the decider consulted. The replay checker has the whole trace and will reject a Grant that counted an ineligible `Agreed`.

**Scenario.** Operator sends r1 listing n2. n2 then crash-stops and returns with empty disk (incarnation 1). r1 is delivered to a member and epoch 1 commits listing n2. n2 votes in incarnation 1. F3.3 marks those votes ineligible (request sent before amnesia). A grantor that treats “I have a commit listing n2, vote carries inc 1” as re-added counts them and fails replay. A grantor that never counts inc > 0 until it has seen both the env amnesia and the operator send is using records it never received.

**Repair.** Make re-addition a local, recorded fact. For example: incarnation *i* of *n* is re-added when a configuration that lists *n* is committed **and** this incarnation of *n* recorded a `Vote` or `ReconfigRequest` for that configuration. Put that rule in “Eligible vote” and in F3.3. If the intent is that only a post-amnesia **operator** send re-adds, put the incarnation (or a generation) on the request so every node judging the vote can see it.

---

## 2. A failed configuration vote poisons epoch e+1 forever (C3.6, C3.1, C1.4, C3.4)

**Where.** C3.6 (“never votes for two different configurations for the same epoch”; no grant under e after a vote for a higher-epoch configuration); C3.1 (e+1 only after e); C3.4 (`unavailable` allowed at any time).

**Why.** Epochs increase only on **commit**. A `Vote` for members A at epoch 1, if that commit never happens, still consumes epoch 1 for that voter and still forbids grant votes under epoch 0. The voter cannot vote for members B at epoch 1, cannot jump to epoch 2, and cannot grant under the current configuration. `Vote` carries no `grantor_term` / ballot, so a later leadership period cannot supersede the attempt. `unavailable` after votes have been cast is the explicit way to abandon the attempt.

**Scenario.** Three members. Operator sends r1 = {n1,n2,n4} to n1. n2 records a configuration `Vote` for epoch 1. n1 then records `ReconfigRefused(unavailable)` (allowed). After the last fault a requester is connected to a majority of epoch 0. n2 will not vote for a grant under 0. No epoch-1 configuration is committed, so no one can grant under 1. C1.4’s premise holds and no grant can be issued. A second request r2 with a different set cannot collect a majority of epoch 0 for epoch 1 either, so C3.4 dies on the same poison.

**Repair.** Restrict C3.6’s “one configuration per epoch” to **committed** configurations, or allow a later ballot (put `grantor_term` or a ballot on `Vote`) to replace an uncommitted proposal for the same epoch. Say that `unavailable` is only legal **before** the receiver has counted a configuration vote for that request. Tie `grantor_term` to configuration proposals the same way it is tied to grants.

---

## 3. C3.6 does not order grant votes; the C1.1 sketch does not cover concurrent or delayed issuance

**Where.** C3.6; C3.2; the paragraph after C3.6 that claims C3.2+C3.3+C3.6 carry C1.1 across a change.

**Why.** C3.6 stops a voter from voting for two **configurations** of one epoch and from voting for a grant under e **after** a higher-epoch configuration vote. It allows two grant votes under the same epoch, including two proposals that both use `sealed_token+1`. The sketch only shows that a **later commit** seals tokens of grant votes that already happened. It does not stop:

- two nodes, each collecting a majority for a grant at the same token;
- a leader that already has a majority for token T under epoch 0 from **issuing** that `Grant` after epoch 1 has committed and a newer grant has been issued.

C3.2 still permits the delayed issue: the old leader’s current configuration is 0 until it **records** a later `ConfigCommitted`.

**Scenario.** Epoch 0 seals `highest_token=0`. n1 collects a majority for a grant to c1 with token 1 and does not yet emit `Grant`. Epoch 1 commits, sealing at least 1. n2 grants c2 token 2 under epoch 1; c2’s write is accepted. n1, which has not learned of epoch 1, now emits `Grant(c1, token=1)`. C1.1 fails in every ordering where token 2 is the earlier `Grant` record. A second split: n1 and n3 both propose token 1 to different clients; C3.6 lets a voter accept both; both grants issue with token 1.

**Repair.** Add to C3.6: a node votes for a grant token T only if T is strictly greater than every token it has already voted for. Add to C3.2: a grant may be issued only while the deciding node’s current configuration is still the one named in the counted votes, and only if those votes are of the same `grantor_term` as the grant. State C1.1 over the set of `Grant` records (tokens strictly unique and a later `config_epoch` carries a strictly larger token), independent of cross-process emission order.

---

## 4. “The configuration it votes under” is undefined for a C3.3 joint vote

**Where.** “Eligible vote”; `Vote(..., proposal, config_epoch, ...)`; C3.3.

**Why.** Eligibility requires the sender, when the vote was sent, to be a member of “the configuration it votes under.” A C3.3 vote is agreement to epoch e+1 **and** is counted toward a majority of e **and** a majority of e+1. `Vote` has a single `config_epoch` plus a proposal that itself contains an epoch. Old-only members (in e, not in e+1) are members of one of those sets. New-only members are members of the other. A node in the intersection would need one vote counted twice or two `Vote` records.

**Scenario.** Epoch 0 is {n1,n2,n3}. Requested set is {n3,n4,n5}. n1 is old-only, n4 is new-only, n3 is in both. Author A sets `config_epoch` to the proposal (e+1): n1’s vote is ineligible (n1 ∉ e+1), so a majority of e is impossible. Author B sets `config_epoch` to the voter’s current epoch e: n4’s vote is ineligible, so a majority of e+1 is impossible. Author C emits two `Vote`s per intersecting node and collides with C3.6 if those are read as two configurations.

**Repair.** Split the event: `Vote` for a configuration names **which** membership the vote is counted toward (`under_epoch` / `under_members`), and the proposal (new epoch, members, request id) separately. Say that a node in the intersection may be counted toward both majorities from a single `Vote`. State eligibility against the membership the vote is counted toward.

---

## 5. C3.4 is vacuous for `unavailable`, `invalid`, and `busy`

**Where.** C3.4; Pending; Rule L3.

**Why.** Three independent holes:

- **`unavailable`.** Pending ends when the receiver records “its refusal.” `unavailable` is a refusal, “allowed at any time.” After that the request is no longer pending, so C3.4’s premise is false. An artifact that records `ReconfigRequest` and immediately `ReconfigRefused(unavailable)` never has a request pending “for long enough.” P40–P42 check “committed or refused” and pass this artifact.
- **`invalid`.** C3.4’s premise needs a majority of the requested set. Majority of the empty set (more than half of zero) does not exist. A request that names a process that is not in `lease` may name a client, storage, the operator, or a name with no process, which cannot be “up and connected.” There is no liveness duty to refuse `invalid`.
- **`busy`.** Same majority-clique premise for a local comparison of two request ids at one node.

**Scenario.** After the last fault, op sends a valid reconfig to n1 with majorities connected. n1 always refuses `unavailable`. C3.4 never fires. Same run with members `[]`: the invalid request sits unanswered forever, still legal under C3.4.

**Repair.** Pending ends only on commit of **this** `request_id`, on `superseded`/`invalid`/`busy`, or on amnesia. `unavailable` is a non-terminal nack; the request stays pending. Require `invalid` and `busy` as local refusals with no majority premise, as soon as the receiver has recorded `ReconfigRequest`. Keep the clique premise for commit and `superseded` only.

---

## 6. Pending at the receiver only, plus C3.6, leaves C1.4 on during a reconfiguration that members are already voting for

**Where.** C1.4 made precise; Pending (“pending nowhere else”); Rule L3; F3.1 / P37 (receiver may be a non-member).

**Why.** C1.4 is suspended only while a reconfig is pending **at a member of the current majority**. A request sent to a non-member is pending only there. If that non-member forwards into the cluster, members vote for epoch e+1 (needed for C3.3/C3.4) and C3.6 then forbids grant votes under e, while C3.2 still forbids grants under e+1 until the commit is recorded. C1.4 remains in force.

**Scenario.** {n1,n2,n3} plus non-member n4. Client requests a grant. Operator sends a valid reconfig to n4. n4 forwards; n1 and n2 vote for epoch 1. The requester, storage, and {n1,n2,n3} stay connected. C1.4’s extra pending clause is false (pending is at n4). Until epoch 1 commits, nobody can legally issue a grant.

If epoch 1 then commits, a grant under 1 can still satisfy C1.4 (defect 2 is the permanent version of this window). Authors will still split: one suspends granting on any in-flight reconfig they hear about (and fails C1.4 on this schedule); one keeps granting (and hits defect 3).

**Repair.** Suspend C1.4 while **any** reconfiguration request is pending at **any** lease node, or while any member of the current configuration has a configuration `Vote` for an epoch that is not yet committed. State that a non-member receiver must either refuse locally (`invalid`/`unavailable` under the repaired C3.4) or become the decider without locking grant votes until commit.

---

## 7. C3.5 is optional in practice; `grantor_term` is an outcome without a fixed input

**Where.** C3.5; schema “Other inputs the artifact names in its README”; Grant outcomes in replay part 2; `ConfigCommitted.highest_term`.

**Why.** Extra inputs are allowed. Putting `seq`, a nonce, or a unique request id in every `inputs` list makes two decisions never compare equal, so part 2 never reports `UNEXPLAINED inputs`. The mutation (unrecorded clock or map order) is invisible for the same reason.

Separately, part 2’s Grant outcome includes `grantor_term`, and the fixed grant inputs are counted `Agreed`s, `members`, `config_epoch`, `sealed_token`. Those do not determine a term. `highest_term` on `ConfigCommitted` is never defined, is not a C3.5 outcome, and has no clause.

**Scenario.** Two runs, same votes, same sealed token. Artifact A assigns `grantor_term=1` on the first grant of each epoch. Artifact B increments a durable term on every election, so the same grant is term 3. Equal fixed inputs, unequal outcomes, `UNEXPLAINED inputs`. Artifact C adds `"term": 3` to inputs in one run and `"term": 1` in the other; part 2 passes and C3.5 says nothing.

**Repair.** Fix the allowed input names. Forbid identity and nonce fields. Add `grantor_term` (and the prior term record it came from, by `ref`) to the fixed grant inputs, or drop `grantor_term` from the outcome tuple. Define `highest_term` as the highest `grantor_term` sealed by that commit, parallel to `highest_token`, and include it in C3.3 and in replay.

---

## 8. Majority after amnesia is defined three ways

**Where.** Contract “Majority of a configuration” (denominator = whole membership); F3.3 (“The denominator of every majority still counts it”); Rule L3 / R3 (“not counting amnesic members not re-added”, “counts toward no majority”).

**Why.** L3 can be read as dropping amnesic nodes from the **denominator** of C1.4’s premise. The contract and F3.3 keep them in the denominator and drop only their votes from the numerator. For two members with one amnesic, the contract needs two eligible votes (impossible, and R3 correctly says the premise may fail). An L3 reading that “does not count” the amnesic node asks for a majority of the remaining one node, so C1.4 would still apply.

**Repair.** One sentence in all three places: an amnesic incarnation contributes no eligible vote; it remains in the denominator of every configuration of which it is a member until a later configuration that omits it is committed. C1.4/C3.4 premises use that same majority.

---

## 9. Several event fields cannot be produced from local state, or cannot be produced unambiguously

**Where.** `ConfigCommitted.highest_term`; `Agreed` “once per voter”; `ReconfigAck` causes (“receiver's `ConfigCommitted` (decided)”); follower `ConfigCommitted` causes; replay “the `ConfigCommitted` for its `config_epoch` in the trace”; `(proc, inc, seq)` after an ordinary restart.

**Why.**

- `highest_term` has no meaning (see 7). Authors will fill 0, the decider’s term, or the max reported term.
- “Once per voter” does not say per proposal, per epoch, or per incarnation. A second grant needs a second `Agreed` for the same voter.
- If n2 received r1 and n1 decided the commit, n2’s `ConfigCommitted` has `decided: false`. The ack rule names “the receiver's `ConfigCommitted` (decided)”. C3.3/C3.4 still require the operator to be told of a commit that happened elsewhere.
- A follower must name “the record by which it learned the commit.” There is no learn/replicate event. Authors will point at the leader’s decided record or invent an unschematized message.
- Several `ConfigCommitted` rows share an epoch (every learner). Replay needs a canonical one (`decided: true`).
- `seq` restarts only on **amnesic** restart. F1.1 ordinary restart keeps `inc`. If `seq` is not durable, `(proc, inc, seq)` collides; if it is durable, every observability record is in the durable state F1.1 restores.

**Repair.** Define `highest_term`. Say `Agreed` is once per `(voter, incarnation, proposal)`. Let `ReconfigAck` name the receiver’s own commit or refusal row (`decided` true or false), and require that if the outcome is `committed`, that row’s `(epoch, members, request_id, highest_token)` equals the unique `decided: true` row for that epoch. Use that decided row as canonical in replay. Say a follower’s cause is that decided row (or an `Agreed` of the commit). Require `seq` to be part of the durable incarnation state, recovered as last-durable+1.

---

## 10. Lifetime and clocks do not constrain grants, so F3.2 splits the authors

**Where.** Terms “Lifetime”; Fencing; F3.2; C1.4; P32, P35, P44, P47, P53.

**Why.** Expiry is “the grantor’s concern.” No clause requires waiting L before the next grant. Overlapping holders are already how fencing works. An artifact that never reads a clock satisfies C1.1–C3.6 under F3.2 except for C3.5 bookkeeping. An artifact that implements exclusive expiry will stall across backward jumps (P53) and will put `clock` in grant inputs (P44). Both are faithful; they will diverge on every F3.2 pair.

**Repair.** If exclusive leases are required: a grantor issues a grant only when its own clock is at least L after the issue time of the last grant it has recorded, and that issue time and clock reading are grant inputs. If overlapping grants are required: drop L from the Grant event for v3, and treat F3.2 as applying only to whatever clock the artifact documents.

---

## 11. Schedule-format gaps that change which runs even exist

**Where.** v5 addendum: Rule E1, Rule T1, Rule L3 vs C3.4; `non-member`; quiescent.

**Why.** `quiescent` still means no request/write/read/ack in flight. A pending reconfig with no client work matches `end: quiescent` before C3.4 can be judged. T1’s synchronous list is `Request`, `WriteAttempt`, `Fault`; a following step triggered on `ReconfigSend` is armable only if that list is read as examples. “Committed” in C3.1/C3.3 is global; “current configuration” is per node; L3’s “current configuration” for C1.4/C3.4 is the latest `decided: true` (or epoch 0). That last reading should be explicit.

**Repair.** Extend quiescent to: no pending `ReconfigRequest` at any live receiver and no in-flight `ReconfigAck`. Add `ReconfigSend` (and the F3.2/F3.3 `Fault` records) to T1’s synchronous list. In L3, name the configuration as that of the highest-epoch `ConfigCommitted` with `decided: true` in the trace, else epoch 0.

---

## 12. Pairs that enforce a stronger protocol than the contract

**Where.** P34 (“none of whose counted members had learned of a newer one” — C3.6 is about **voting**, not learning); P36 (forbids counting a still-eligible ignorant member, and counting pre-amnesia votes that F3.3 still calls eligible); P33 (“no epoch is committed twice” vs C3.1’s “at most one configuration”); P40–P42 (accept `unavailable`).

These will fail a contract-faithful artifact, or pass a vacuous one (defect 5). Align the pair text with the repaired clauses.

---

## Smaller items (would not change the protocol shape)

- **Who may decide a commit.** “Committed when **the grantor** has decided” vs C3.3, which only requires the two majorities. P34 sends removal to the grantor; P37 sends to a non-member that “forwards or refuses.” Pick one: only a node that issued the current `grantor_term` records `decided: true`, or any node that collected the two majorities may.
- **Leadership period** is unnamed except as `grantor_term`. Say when a new term starts (at least: each `Grant` and each decided `ConfigCommitted` carries a term unique among leadership periods, including across epochs).
- F1.3 “continues as if no time had passed” vs F3.2 “a paused process’s clock keeps advancing.” Process state is frozen; the clock is not. One sentence.
- Schema cites `docs/requests/2026-10-22-from-yupi-consistent-executions.md`, which is outside the author inputs. Harmless if it stays “measure, not requirement.”
- Integer overflow must “record a failure” with no such event. Say: emit nothing further; the run ends `UNEXPLAINED bound` or a named `Overflow` record.

---

## Schedule expected to break most artifacts

Start with three members and two connected outsiders. Let client A obtain a grant whose votes are collected at the current grantor but whose `Grant` is not yet issued. Send one reconfiguration that replaces that grantor with the two outsiders, addressed to an outsider, and immediately send a different membership to a follower. Cut the old grantor from one member, leave it connected to a voter that already agreed to A’s token, and step the old grantor’s clock backward by several lifetimes. Crash a voter of the first reconfiguration and bring it back with an empty disk; then deliver a reconfiguration that was sent before that crash, listing the amnesic node. After some new membership commits, have the new side grant client B a higher token and accept B’s write. Then let the old grantor emit A’s delayed grant and let A write. Artifacts will split on whether the outsider-pending reconfig may lock grant votes, whether the delayed post-amnesia request re-adds anyone, whether token 1 may still be issued after token 2 exists, and whether the second membership can ever be committed or must be refused `unavailable` and poison the epoch.
