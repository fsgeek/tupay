I'll read the five draft inputs and review them for defects as the brief requires.I have the five drafts; next I’ll cross-check clauses, cells, observables, and pairs for conflicting readings.# Review of the X3 draft inputs

Defects ranked by how much they would change what the two authors build. Each names a place, why it is a defect, a scenario where one exists, and a repair.

---

## 1. Epoch 0 is never “committed”, so the first grant and the first reconfiguration are forbidden

**Where.** `contract/v3.md`, term **Committed** (“records the decision once (`ConfigCommitted` with `decided: true`)”; “current configuration is the committed configuration with the highest epoch that the node has recorded”); events (“every initial member records [epoch 0] with `decided` false”; “`decided` is true only … exactly once per epoch **above 0**”); C3.7; C3.1.

**Why.** A configuration is committed only when some node records `decided: true`. Epoch 0 is recorded only with `decided: false`, and `decided: true` is forbidden for epoch 0. A node that has recorded only those epoch-0 lines therefore has no current configuration. C3.7 issues a grant only under the decider’s current configuration. C3.1 commits epoch 1 only after epoch 0.

**Scenario.** Three initial members start and emit `ConfigCommitted` epoch 0, `decided: false`. A client requests a grant. Author A treats the deployment membership as already current and grants under epoch 0. Author B finds no `decided: true` record, so C3.7 forbids every grant, C1.4 is unsatisfiable, and C3.1 forbids epoch 1 as well.

**Repair.** State that the initial configuration is committed at epoch 0 by the deployment, recorded by each initial member with `decided: false` and no predecessor; that a node’s current configuration is the highest-epoch `ConfigCommitted` it has recorded (epoch 0 included); and that “at most one configuration per epoch” for epoch 0 means that unique initial membership. Keep `decided: true` unique per epoch above 0.

---

## 2. C1.4 and C3.4 promise progress after amnesia that has destroyed every eligible majority

**Where.** `contract/v3.md` C1.4 under v3 and C3.4(b); `failure-model/v3.md` F3.3 and “After the last fault”; `testbed/schedule-format.md` Rule R3 (“a schedule may make C1.4’s or C3.4’s premise unsatisfiable”).

**Why.** Amnesic members stay in every denominator and their new agreements are ineligible until re-admission. The liveness premises ask only that a majority of the configuration be **up and connected**. Rule R3 claims those premises then become unsatisfiable. They do not: the nodes are up. Re-admission itself needs an eligible majority of the old configuration (C3.8), so a cluster that has lost that majority cannot re-admit its way out.

**Scenario.** Config `{n1,n2,n3}`. `n1` and `n2` crash, restart amnesic, and heal. All three, storage, and a requester stay connected; no reconfiguration is pending. C1.4’s premise holds. At most one eligible agreement exists (`n3`), so no grant and no re-admission commit is possible. The same hole for a singleton configuration whose only member is replaced on disk.

**Repair.** Add to both liveness premises that a majority of the configuration’s members have eligible current incarnations (incarnation 0 or already re-admitted). State that a schedule in which that fails simply does not trigger C1.4 or C3.4(b). Single-node disk replacement then has no liveness promise, which is honest.

---

## 3. Re-admission, eligibility, and “counted” form a loop; the eligibility sentence also parses two ways

**Where.** `contract/v3.md` **Re-admission**, **Eligible agreement**, **Agreement** / `Agreed` (“when it counts that agreement”); `observe/schema.md` v5 evidence check (“each pair in its `readmits` has an `Agreed` for this proposal among its counted records”); `tests/pairs-v4.md` P63 (“names it in `readmits` only if its new incarnation’s agreement was counted for that commit”).

**Why.** Two independent problems.

Eligibility: “counts toward a majority of configuration X only if its node is a member of X and its incarnation is 0, or was re-admitted …”. Reading (A): `(member ∧ inc=0) ∨ re-admitted`. A re-admitted node then counts toward a majority of a configuration that omitted it. Reading (B): `member ∧ (inc=0 ∨ re-admitted)`. That is the intended quorum rule. Both are grammatical.

Re-admission: incarnation i of n is re-admitted by a commit that lists n if the decider recorded an `Agreed` from that incarnation for that proposal. Eligibility excludes “the commit being decided”, so that `Agreed` is ineligible for this commit’s majorities. The schema still requires it “among its counted records”. `Agreed` is defined as recorded “when it counts that agreement”, and `counted_toward` lists epochs whose majority it is counted toward. Authors who put only eligible votes in `agreed` can never fill `readmits`. Authors who put ineligible votes in `agreed` with empty `counted_toward` can.

**Scenario.** `{n1,n2,n3}`, `n3` amnesic. Operator asks for the same three members, which is the only way to re-admit `n3` without changing membership. Majority of old and new is two eligible votes from `n1` and `n2`. `n3` agrees as incarnation 1. Author A records that `Agreed`, sets `counted_toward: []`, lists `[n3,1]` in `readmits`, and later counts `n3` for grants. Author B refuses to record an ineligible `Agreed`, omits `readmits`, and `n3` is stuck in the denominator forever. Author C, on reading (A), later counts `n3` toward a majority of a configuration that has already removed it.

**Repair.** Parenthesize eligibility: member of X **and** (incarnation 0 **or** re-admitted by a commit of epoch ≤ X’s epoch other than the commit being decided). Split “recorded `Agreed`” from “counted toward a majority”. Allow `counted_toward: []` as re-admission evidence. Say that `readmits` is exactly the set of `[node, incarnation]` pairs for which such an `Agreed` exists, the node is in the new membership, and incarnation > 0.

---

## 4. C3.5 is vacuous for grants and commits once `ref` is expanded

**Where.** `contract/v3.md` C3.5 (“a record’s own identity, a sequence number, or any value chosen to be unique to one run is not an input”); `observe/schema.md` v5 equality (“inputs compared as name-value sets with each `ref` replaced by the record it names, recursively”); grant and commit input lists, which always include `agreed` by `ref`.

**Why.** The clause forbids identity as an input so that two runs can share inputs and be forced to share outcomes. The check then substitutes each `ref` with the whole record, which still carries `(proc, inc, seq)`. Those triples differ as soon as one extra `Agree` or retransmission shifts numbering. Equal grant inputs then never occur, and “equal inputs ⇒ equal outcomes” holds vacuously. Storage decisions have no `ref`s, so the clause still has force there. The steward’s mutation (a) on synthetic traces can still fire; live impl traces with retries almost never will.

**Scenario.** Two impl runs of the same schedule. Each issues a first grant counted by `{n1,n2}` with `last_token=0`. Run 2 retried an `Agree`, so those `Agreed` refs are `(n1,0,4)` rather than `(n1,0,3)`. Recursive equality treats the inputs as different. Run 2 may emit a different token or consult an unrecorded clock; part 3 stays quiet.

**Repair.** Compare inputs as name–value sets on the JSON `value`s; treat `ref` as provenance for the evidence check only. If content equality of referenced records is wanted, compare the referenced event’s contract fields (proposal, token, members, …) and drop `(proc, inc, seq)`. Keep the existing ban on unique-per-run values as inputs.

---

## 5. C1.1(b) is a global invariant no grantor can enforce locally; the configuration proposal does not carry a token high-water; C3.7 only needs a majority of the already-committed config

**Where.** `contract/v3.md` C1.1 made precise (b); C3.7; **The grantor’s protocol** (“what carries C1.1 across a configuration change is the artifact’s protocol”); proposal shape `(epoch, members, request id)` with no token; joint configurations “are not configurations here and have no epoch”; `observe/schema.md` v5 part 2.

**Why.** After epoch 1 is committed, a node that has not learned it still has epoch 0 as current and, under C3.7, may issue a grant under epoch 0 if it can collect an eligible majority of epoch 0. C1.1(b) still requires every epoch-1 token to exceed every epoch-0 token, including those issued after the epoch-1 grant. The old grantor does not see the new tokens. Completely disjoint membership makes (c) (shared voter) empty, so only (b) links the two token spaces. During an in-progress reconfiguration the committed current config is still e, so C3.7 allows grants on a majority of e alone while new members have not seen those grants.

**Scenario.** `{n1,n2,n3}` reconfigures to `{n4,n5,n6}`. Joint work is internal. `n1,n2` issue token 10 under epoch 0. Epoch 1 then commits. New leader `n4` has not installed the old log, grants token 1 under epoch 1. C1.1(b) fails. A second path: epoch 1 is committed; `n1` is partitioned before learning it, still holds a majority of the old three because the other two have not yet refused old-config grants; `n1` issues token 20 under epoch 0 after `n4` has issued token 11 under epoch 1.

**Repair.** Make the local rule explicit: a node that has agreed to a configuration of epoch e+1 must not agree to a later grant under epoch ≤ e; a grant under epoch e+1 may be decided only once the decider’s recorded inputs include a last-token at least as large as every token in counted agreements under epoch e. Put that high-water in the configuration proposal (and in decided-commit `inputs`) so disjoint membership still carries C1.1. State that while a reconfiguration is pending, grant evidence is the same joint evidence C3.8 uses, or that grants are forbidden until e+1 is committed.

---

## 6. Non-member receivers have a closed, invented reconfiguration protocol; P61 allows a refusal C3.4 forbids

**Where.** F3.1 (send to any lease node, member or not); C3.4(a)–(b) (refusal reasons are only `invalid`, `busy`, `superseded`; the receiver must drive the request; “no new agreement protocol is to be invented”); P61 (“sent to a non-member, which forwards or refuses it”).

**Why.** A valid request sent to a non-member is not `invalid` (the set names lease nodes). The receiver must keep it pending and, if C3.4(b)’s clique is up, get it committed or superseded, then ack. Published Raft reconfiguration starts at the leader of the current configuration. Forwarding plus “the original non-member remains the receiver who must learn the commit and ack” is extra protocol. P61’s “or refuses” names a fourth reason.

**Scenario.** `lease: [n1,n2,n3,n4]`, `config: [n1,n2,n3]`. Operator sends “membership `{n1,n2,n4}`” to `n4`. Author A forwards to `n1` and keeps the request pending at `n4` until `n4` learns the commit. Author B refuses immediately as not-a-member (P61). Author C has `n4` start an election in a configuration it is not in. All three can cite the inputs.

**Repair.** Strike “or refuses” from P61. Add one sentence: a non-member (or follower) receiver records the request, forwards it to a member of its current configuration if it has one, otherwise waits to learn one, and remains the process that eventually records `ConfigCommitted`/`ReconfigRefused` and answers the operator. Keep the refusal set closed.

---

## 7. The C3.7/C3.8 evidence check trusts self-reported membership

**Where.** `observe/schema.md` v5 part 1: a grant’s counted `Agreed` “form a majority of its `members` (C3.7)”; a decided commit “is counted by eligible majorities of e and of its own `members`”.

**Why.** C3.7 requires a majority of the decider’s **current configuration**. The check uses the `members` list the decider wrote. Same for `old_members` on a commit.

**Scenario.** Current config `{n1,n2,n3}`. `n1` records a `Grant` with `members: [n1]`, `config_epoch: 0`, and only its own `Agreed`. Majority of `[n1]` is one. The check passes. C3.7 is violated.

**Repair.** For a grant under epoch e, `members` must equal the unique committed membership of e (epoch 0: the schedule’s `config`; e>0: the unique `decided: true` `ConfigCommitted` of epoch e). For a commit of e+1, `old_members` must equal that membership of e, and `members` must equal the named request’s set.

---

## 8. F3.3’s amnesic knowledge is too small to implement C3.4(a) or to use L

**Where.** F3.3 (“knows only its own identity, the initial configuration’s members, and that it has lost its state”); C3.4(a) (`invalid` if the set names a process that is not a lease node); lifetime L “fixed by the deployment”; P33 (reconfig sent to the amnesic node).

**Why.** `invalid` is defined against the full `processes.lease` list, which can be larger than the initial configuration. An amnesic node is forbidden to know that list, and is not given L.

**Scenario.** Initial `{n1,n2,n3}`, extra lease node `n4`. `n2` restarts amnesic. Operator sends `{n1,n2,n4}` to `n2`. Author A, following F3.3, does not know `n4` as a lease node and refuses `invalid`. Author B was given the deployment’s full lease list at restart and proceeds. C3.4(a) is then a different function of the same request.

**Repair.** F3.3: after amnesia the node is given the deployment (its identity, the full lease-node list, the initial configuration, L) and a flag that this start is amnesic. Durable grant/config/agreement state is gone.

---

## 9. Learners must name the decider’s `(proc, inc, seq)`; published catch-up does not carry it

**Where.** `contract/v3.md` `ConfigCommitted` (“the message by which it learned carries that record’s identity”); `observe/schema.md` v5 (“a `ConfigCommitted` with `decided: false` for an epoch above 0 names the decided record … whose identity the message that taught it carries”).

**Why.** A process can fill `causes` only from its own state plus messages it received. Raft snapshots and bulk log install carry committed membership, not the steward’s record id of the unique `decided: true` line.

**Scenario.** `n4` is added, catches up from a snapshot on `n2`. `n4` can record epoch, members, request id, readmits. It cannot honestly name `(n1, 0, 42)`, the decider `n1`’s record, unless the snapshot format is extended in a way no published protocol specifies.

**Repair.** For `decided: false` above epoch 0, require that `(epoch, members, request_id, readmits)` equal the unique `decided: true` record of that epoch. Make naming that record in `causes` obligatory only when the teaching message carried `(proc, inc, seq)`.

---

## 10. C3.4’s `superseded` is defined as “a higher epoch was committed **while it was pending**”

**Where.** C3.4(b); **Pending** (amnesia ends pending); P33.

**Why.** An amnesic receiver that has forgotten epoch 1 will try to commit its new request as epoch 1. Epoch 1 is already committed, so C3.1 forbids a second configuration for that epoch. The existing epoch 1 was committed **before** this request became pending, so the parenthetical `superseded` condition is false. The receiver also cannot “give up” for any other reason.

**Scenario.** Epoch 1 committed. `n2` agreed, then amnesic-restarts. Operator sends a new request to `n2`. `n2`’s current view is epoch 0. It proposes epoch 1 again. Other nodes refuse the duplicate. `n2` has no allowed refusal reason until some epoch 2 commits “while pending”. If the rest of the cluster is quiet, the request stays pending forever even though C3.4(b)’s connectivity premise holds.

**Repair.** `superseded` means a committed epoch exists that the receiver cannot overwrite with this request: any committed epoch ≥ the epoch this request would occupy, whether committed before or during pending. An amnesic receiver that learns of such an epoch refuses `superseded` (and may then accept a retry as a later epoch).

---

## 11. A commit may name a request id and a different member set

**Where.** C3.8 (operator told success “only for the request whose id the commit names”); C3.4(b) (“the request is eventually committed”); decided-commit inputs include `request_id` and `requested_members`; outcomes include `members` as a set.

**Why.** Nothing requires `members == requested_members` for that id. C3.5 only requires that equal inputs produce equal members. An artifact that always drops the receiver, or always inserts itself, is a function.

**Scenario.** Operator asks `{n1,n2,n4}`. The leader commits `{n1,n2,n3,n4}` under that id (it “kept itself”). The operator is told success. C3.8 holds. Whether C3.4’s “the request” committed is a matter of taste.

**Repair.** A `ConfigCommitted` that names `request_id` r has `members` equal as a set to r’s requested members. `invalid` remains the only way a requested set fails to become a configuration.

---

## 12. F1.3 pause duration fights C3.5’s non-waiting grants and F3.2

**Where.** `testbed/schedule-format.md` v1 pause rule (resume triggered by a later `Grant`) and Rule R2 (“a pause must still outlast L in run time”); `contract/v3.md` Lifetime (a grantor may issue a new grant while an earlier one is unexpired); F3.2.

**Why.** A later `Grant` is no longer evidence that L of run time has passed: the grantor may not wait, or its clock may have jumped forward. Compilers that take R2 literally reject the v1 trigger pattern; compilers that take the v1 trigger literally allow a pause of length 0 under v3.

**Scenario.** `c1` holds a grant. Pause `c1`. The grantor, which does not wait, immediately grants `c2`. Resume is triggered by that `Grant`. Run time elapsed is near 0.

**Repair.** Keep the v1 trigger as a convenience, and define F1.3’s duration in run time independently of grants: the matching `resume` is taken only after L of run time since `pause`, with clocks of other processes free to jump in between. Drop the claim that a later `Grant` can only happen after expiry.

---

## 13. `grantor_term` uniqueness across configurations is an untested term

**Where.** `contract/v3.md` **Grantor term** (“no two leadership periods share a term, across configurations as well”); configuration proposal omits a term high-water; decision-replay check is silent on terms.

**Why.** Tokens are carried across configs only by C1.1(b). Terms have the same problem and no clause. A disjoint new configuration that restarts terms at 1 satisfies every clause and reuses `grantor_term`.

**Scenario.** Epoch 0’s grantor used term 1. Epoch 1’s new members never saw that term, elect a leader at term 1, grant. Two leadership periods share a term. Provenance still chains through `causes`, so the schema does not complain.

**Repair.** Either retire uniqueness as a wish, or add it to the replay check (no two `Grant`s share `(grantor_term)` unless they share a leadership period) and carry a term high-water with the configuration, as in defect 5.

---

## 14. Clock steps are reals; time between schedule steps is unspecified

**Where.** F3.2 (“jump … by any amount”; “between steps, every clock advances at the rate of run time”); Rule R2 (`step × L`, “any real number”); C3.4/C1.4 “for long enough”.

**Why.** TLA+ authors will pick a discrete time domain; Go authors will pick `time.Duration`. How much `now` advances between two schedule actions is left open, so a grantor that waits for expiry may or may not grant between the same two steps depending on how time is ticked.

**Scenario.** Grant at t=0, wait L, next step is `request: c2` with no clock fault. Model author A inserts ticks until expiry and grants before the request is answered. Model author B only advances time on F3.2 steps, so expiry never comes unless the schedule jumps the clock. Both are faithful to “between steps, every clock advances at the rate of run time.”

**Repair.** Fix a discrete time unit (1 = L, or 1 = the schedule’s `lifetime` tick). State that, after the last fault, the model may advance every clock by any positive number of units between actions, and must explore advances that cross recorded `last_grant_at + L` deadlines; the impl’s simulated clocks do the same. Forbid non-integer `step` in schedules, or require rational steps with a declared denominator.

---

## 15. Smaller ambiguities that will still split implementations

**`Overflow(proc, what)`.** `what` is undefined. Name the domain (`token` | `term` | `epoch` | `inc`).

**`invalid` vs `busy`.** A second request that is also empty can be either. Order the reasons: `invalid` first, then `busy`, then `superseded`.

**Operator.** Used as a process in F3.1, C3.8, and the schedule; never listed under Terms. Add it next to Client.

**Amnesic first record.** Schema: “every initial member’s first record is `ConfigCommitted` for epoch 0”. Unclear whether that repeats at incarnation 1. If it does, the node resurrects epoch 0 as current (ghost elections). Say: incarnation 0 of an initial member starts with that record; a later incarnation records nothing until it learns a committed configuration, and cannot grant or decide until re-admitted.

**`Agreed` once per (node, incarnation, proposal) vs joint consensus.** A node in both old and new is two roles in Raft joint consensus and one `Agreed` with `counted_toward: [e, e+1]` here. Say that explicitly.

**C3.5 extra input names.** “Names outside the fixed list are reported.” Unclear whether that is `UNEXPLAINED` or a note. If the README justifies the name, accept it in equality; otherwise fail the trace.

**Rule L3’s “current configuration”.** The contract’s term is per-node; L3 redefines it as the highest `decided: true` in the **trace**. That is the right reading for premises; say “the globally committed configuration” and stop reusing “current”.

**Client `seq` after F1.1 restart.** v5 identity is `(proc, inc, seq)` with `inc=0` for clients and “seq never repeats within one [incarnation]”. Clients have no durable records. A restarted client that starts `seq` at 0 collides. Give clients an incarnation that bumps on every restart, or allow client `seq` to restart because run-scoped process identity is `(proc, run)`.

**F1.1 vs operators.** Crash-stop names lease nodes, clients, and storage. A schedule that crashes `op` is either rejected or an unmodelled fault. Say operators do not crash, or add them to F1.1.

**P40’s prose.** “Majorities of both configurations stay connected” omits the receiver. A compiler that partitions the receiver as the “follower of the old configuration” will write a schedule whose comment claims C3.4(b) and whose L3 premise is false. Name the receiver as part of the connected set.

---

# Schedule expected to break the most artifacts

Start three initial members and two non-members; grant `c1` and let it write; then, before that grant expires on anyone’s clock, send two different reconfiguration requests that both remove the current grantor, one to the grantor and one to a non-member, with the two requested sets overlapping but not equal; while both are unanswered, jump the grantor’s clock backward by several lifetimes, crash one old-majority node and restart it amnesic, and cut that amnesic node away from the non-member receiver; after one of the two requests commits, let the removed grantor (still up, possibly still on epoch 0 in its own view) and a member of the new configuration both try to grant, have `c1` write with the old token, send a same-membership reconfiguration to the amnesic node to re-admit it, and finally request a grant for `c2` from a clique that is up and connected but whose eligible majority may already have been destroyed. Artifacts will split on whether epoch 0 was ever current, whether the non-member may refuse, which request occupies epoch 1, whether the old grantor’s post-commit grant exists and with what token, whether the amnesic vote is recordable in `readmits`, and whether C1.4 still applies.
