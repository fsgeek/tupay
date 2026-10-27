# Judge task: tupay X3, arm A, hold-out H11

You are the judge. You belong to a model family that wrote neither side. Work only from the text below; do not read files, run commands or search, and do not look for anything else.

Background: in each of two arms, a TLA+ model and an implementation were written independently, by different model families, from the same inputs (contract v3, failure model v3, the schedule format and the observe schema, all given below). Arm A adapted earlier artifacts; arm R wrote new ones. The steward ran each side on shared schedules and on hold-out schedules (H11 to H14) that no author saw. A side reports PASS, FAIL <clause>, or UNEXPLAINED <reason> for a schedule.

**Item.** Schedule H11. Arm A's model reports PASS; arm A's implementation reports UNEXPLAINED with the runner message shown (it did not run the schedule). The question is whether the schedule is valid under the inputs, whether the implementation's refusal is correct under them, and where the locus of the difference is.

Excerpts, by a fixed rule: an arm's READMEs as the sections named in their headings below; TLC output as its lines starting "Error:", its exception lines and its statistics lines (a counterexample's behaviour, where there is one, is given as a trace file). Everything else is whole.

Answer in JSON, one object: `verdict` "explained" or "unexplained"; `genuine_violation` "yes" if the run as reported shows a violation of a contract clause under the inputs as written, "no" if it does not (a premise does not hold, or a checker or runner misjudged), "not applicable" if no side claims a violation, or "undetermined"; `locus` "model", "implementation", "inputs" (the contract or failure model underdetermine the behaviour), "interface" (the schedule format or schema underdetermines it), "both", or "none"; `mechanism` in one or two sentences, or "none"; `evidence` citing specific records, states, lines or README entries; `reasoning`; `what_would_settle_it`. Be concrete and brief. Do not propose fixes. Do not assume either side is at fault; agreement between sides is not evidence of correctness, and disagreement is not evidence that either is wrong.

Every file follows, inline.

===== FILE: inputs/contract-v3.md =====
# Service contract v3: the grantor's membership changes

**DRAFT 5, not registered.** Drafted 2026-10-23 by the fifth steward for change experiment X3; drafts 2 and 3 after two input reviews; drafts 4 and 5 by the sixth steward after a third and a fourth (`experiments/X3/input-review/`; dispositions in the log). Nothing here is an input until X3's pre-registration commits it.

Version 3. v2 (`contract/v2.md`) and v1 are unchanged and their clause ids keep their meaning. v3 is **additive**: it adds a locus (configuration), terms, clauses and observable events, and makes precise, for v3, terms that v1 and v2 left open ("made precise"). No earlier clause is retired. This file is self-contained: everything a reader needs from v1 and v2 is restated below, verbatim where marked.

## Terms (v1 and v2, restated verbatim)
- **Key:** one protected key. **Lease nodes:** processes that together act as the grantor. **Storage:** the service holding the key's value and the fence ledger (the highest token it has accepted for the key). **Client:** a process that requests a grant and, while it believes it holds one, writes to and reads from storage.
- **Grant:** the grantor's reply to a request, a token (an integer) and a lifetime; a client holding an unexpired grant is a holder.
- **Write:** a client's request to storage carrying a value and a token; storage accepts or rejects it. **Ack:** the reply that reaches the client; "told a write succeeded" means the client received an ack of acceptance.
- **Read:** a client's request to storage to return the key's current value, carrying a token. Storage either serves it, returning the value it currently holds, or rejects it. A client "is given a value" when it receives an ack of a served read carrying that value.

## Terms made precise for v3
- **Storage** is one process with one fence ledger and one stored value. (F1.1's "storage replica" means this process.)
- **Initial state.** Before any write the ledger is 0 and the stored value is absent (`null`). Tokens are positive integers, so every token exceeds the initial ledger.
- **Integers do not wrap.** Tokens, terms and epochs are unbounded integers. An implementation whose representation would overflow records `Overflow(proc, what)`, `what` one of `token`, `term`, `epoch`, `incarnation`, and issues nothing further, never a wrapped value.
- **Lifetime.** Every grant has the same lifetime `L`, a positive length of run time fixed by the deployment. Expiry is the grantor's concern, measured on the deciding node's own clock (`failure-model/v3.md`, F3.2). A client's belief about expiry decides nothing the contract checks: clients write and read when the workload tells them to. The contract does not require leases to be exclusive: a grantor may issue a new grant while an earlier one is unexpired, since fencing (below) is what protects storage. A grantor that does wait for expiry before granting consults its clock, and records the reading and whatever it compared it with as inputs of the grant (C3.5).
- **Grantor term** (`grantor_term`): a positive integer identifying one leadership period of the grantor; no two leadership periods share a term, across configurations as well, so two grants carrying one term are decided by the same incarnation of the same node. When a term begins, and how it is chosen, is the grantor's protocol's (below). It is carried with the token on every write and read, and recorded on those events (below).
- **Outcomes.** A write's outcome is `accepted` or `rejected`; a read's is `served` or `rejected`; a reconfiguration's is `committed` or `refused`.

## Terms (new in v3)
- **Operator:** a process that sends reconfiguration requests and receives their answers. It is not a lease node, client or storage; links to and from it obey the failure model, and it does not crash.
- **Configuration:** a non-empty set of lease nodes, identified by a **configuration epoch** (a non-negative integer). The **initial configuration** has epoch 0 and is fixed by the deployment. Lease nodes outside every configuration may exist, up and connected, and may later be added.
- **Reconfiguration request:** a message from an operator to one lease node (the **receiver**), carrying a request id chosen by the operator and a set of process names (which may be empty, or name processes that are not lease nodes; such a request is refused as `invalid`). It obeys the link rules of the failure model like any message.
- **Committed:** the initial configuration (epoch 0) is committed by the deployment; it has no predecessor and no deciding node. A configuration of a higher epoch is committed when a lease node has decided, irrevocably, that it supersedes its predecessor; the deciding node records the decision once (`ConfigCommitted` with `decided: true`). The **committed configuration of epoch e** is the initial one for e = 0 and the decided one otherwise. A node's **current configuration** is the committed configuration with the highest epoch that the node has recorded (epoch 0 included). A change from epoch e to e+1 may pass through internal states (such as Raft's joint configuration); they are not configurations here and have no epoch.
- **The grantor's protocol.** How lease nodes agree on grants and on configurations is not prescribed here. Each artifact follows a **published** protocol for agreement and for changing membership (for example Raft with joint consensus, or a published Paxos variant with reconfiguration), adapted only as this contract requires, and names it, with a citation, in its README, together with how it handles an amnesic restart (failure model, F3.3). No new agreement protocol is to be invented. Whatever the protocol, every grant and every commit records the evidence below, and that evidence is what the clauses check; the evidence C3.7 and C3.8 require is a floor, not a recipe, and a protocol that needs more (for example joint majorities while a change is in progress) records what it counted. A receiver that is not the node its protocol lets start a change (a non-member, or a follower) records the request, passes it to a member of its current configuration that can, and remains the node that records the outcome and answers the operator.
- **Agreement:** a lease node's acceptance of a proposal, in the sense its protocol gives that word (in Raft, a node's acknowledgement of the log entry carrying the proposal). A proposal is a grant (client, token, lifetime, configuration epoch) or a configuration (epoch, members, request id). The node records its agreement (`Agree`); the node that decides records each agreement it receives for the proposal (`Agreed`), and says which majorities, if any, it counts it toward (`counted_toward`). Recording an agreement is not counting it.
- **Incarnation:** a lease node's incarnation starts at 0 and increases by one at each amnesic restart (failure model, F3.3). An ordinary restart keeps the incarnation.
- **Re-admission.** Incarnation i > 0 of node n is re-admitted by the commit of a configuration that lists n, provided the deciding node recorded an `Agreed` from incarnation i of n for that very proposal (which shows that incarnation existed before the decision); that `Agreed` is not counted toward the commit (`counted_toward: []`). The commit's `readmits` is exactly the set of `[n, i]` with i > 0, n in the new membership and such an `Agreed` recorded. Re-admission is thus a recorded fact that any node learning of the commit learns with it. To re-admit without changing membership, an operator requests the same members.
- **Eligible agreement.** An `Agreed` may count toward a majority of configuration X only if its node is a member of X **and** (its incarnation is 0 **or** that incarnation was re-admitted by a commit of an epoch at most X's epoch, other than the commit being decided). A member is **eligible** in X if its latest incarnation would be. An agreement made by an earlier incarnation and delivered late is judged by that earlier incarnation.
- **Majority of a configuration:** eligible agreements from more than half of all its members. The denominator is the whole membership: an amnesic member, re-admitted or not, stays in it until a committed configuration omits it. This is the only definition of a majority in this contract, the failure model and the schedule format; every use refers to it.
- **Pending.** A reconfiguration request is pending at its receiver from when the receiver records it (`ReconfigRequest`) until the receiver records its commit, its refusal, or a commit of any higher epoch, or the receiver restarts amnesic. It is pending nowhere else.

## Clauses (v1 and v2, restated verbatim)
- **C1.1** Each grant carries a token strictly greater than every token previously granted for the key.
- **C1.2** Storage accepts a write only if its token is at least the highest token storage has accepted for the key, and on acceptance records that token as the new highest.
- **C1.3** A client is told a write succeeded only after storage accepted it.
- **C1.4** (liveness) If a majority of lease nodes and storage stay up and connected to each other and to some requester for long enough, that requester eventually obtains a grant.
- **C2.1** Storage serves a read only if its token is at least the highest token storage has accepted for the key. Serving a read does not change the highest accepted token.
- **C2.2** A client is given a value only after storage served the read that returned it, and the value given is the value storage held when it served the read.

### How v1 and v2 read under v3 (made precise; no clause changes)
- **Storage decides deterministically.** Storage accepts a write **if and only if** its token is at least the ledger, and on acceptance stores the write's value (an equal token replaces the value); it serves a read **if and only if** its token is at least the ledger, returning the stored value. C1.2 and C2.1 permit this rule; C3.5 needs a rule, and v3 fixes this one.
- **C1.1 across configurations.** "Every token previously granted" means under every configuration. Since no clock orders events at different processes, "previously" is read through agreements: (a) no two `Grant` records carry the same token; (b) a grant under a higher configuration epoch carries a higher token than every grant under a lower one; (c) if one node's agreements to grants g and h were both counted, and its agreement to g comes before its agreement to h in its own sequence, then h's token exceeds g's. A grant whose reply reaches its client late is not thereby later.
- **Fencing.** A newer grant does not by itself stop an older holder: storage rejects the older holder only once a write with a newer token has been accepted (a served read does not move the ledger: C2.1). This is v1's meaning; F1.3 is the case it exists for.
- **C1.4 under v3.** "A majority of lease nodes" means a majority (as defined above) of the configuration with the highest committed epoch. The premise holds only after the last fault of the run (failure model, "After the last fault"), only if more than half of that configuration's members are eligible in it (so a majority of eligible agreements can exist), and only while no reconfiguration request is pending at any lease node that is up.

## Clauses (new in v3)
Ids C3.2, C3.3 and C3.6 were used by drafts 1 to 3 for a voting protocol written into this contract; they are retired and are not reused. C3.7 and C3.8 replace C3.2 and C3.3 at the level of evidence.
- **C3.1** Epoch e+1 is committed only after epoch e, and at most one configuration is committed for any epoch.
- **C3.7** (grant evidence) A grant is issued under exactly one configuration, the deciding node's current configuration when it decides, records that configuration's epoch, and is issued only after the deciding node has recorded eligible agreements to that grant from a majority of that configuration.
- **C3.8** (commit evidence) Configuration epoch e+1 is committed only after the deciding node has recorded eligible agreements to it from a majority of the committed configuration of epoch e and from a majority of the members of e+1; one agreement from a node in both counts toward both (`counted_toward: [e, e+1]`). The members of e+1 are exactly, as a set, those of the request whose id the commit names. An operator is told a reconfiguration succeeded only for the request whose id the commit names, and only after that commit.
- **C3.4** (liveness) Two duties. (a) The receiver refuses a request as `invalid` (its set is empty or names a process that is not a lease node) or else as `busy` (an earlier request is still pending at the same receiver; the earlier one is never refused on account of the later) when it records it, checking in that order, with no premise but that it stays up. (b) If, after the last fault, a request is pending at its receiver, more than half of the members of the configuration with the highest committed epoch are eligible in it, and the receiver, a majority of that configuration and a majority of the requested set stay up and connected to each other for long enough, the request is eventually committed or refused as `superseded` (the epoch it would occupy is already committed to another configuration, whether before or while it was pending; a receiver that learns this refuses, and the operator may send it again). In every case, (a)'s `invalid` and `busy` refusals included, if the operator also stays connected to the receiver, it is eventually told the outcome (`ReconfigAck`). There is no other refusal reason: a receiver cannot give up on a request it is still holding.
- **C3.5** (reconstructibility) Every decision the service records is a function of the inputs recorded with it: in any two runs of the same artifact, two decisions of the same kind whose recorded inputs are equal have equal outcomes. A decision that consulted anything it did not record (a clock read, a random draw, a scheduling accident, the iteration order of an unordered collection) violates C3.5 when that input changes the outcome. Inputs are named values from the list fixed in `observe/schema.md` (v5 addendum); a record's own identity, a sequence number, or any value chosen to be unique to one run is not an input.

C3.1, C3.5, C3.7 and C3.8 are safety clauses; C3.4 is liveness. What carries C1.1 across a configuration change is the artifact's protocol; C1.1, read as above, is what is checked.

## Observable events (v1 and v2, restated verbatim)
`Request(client, key)`; `Grant(client, key, token, lifetime, grantor_term)`; `WriteAttempt(client, key, token, value)`; `WriteAccept(key, token, highest_before)` and `WriteReject(key, token, highest_before)` recorded by storage; `WriteAck(client, key, token, outcome)` recorded by the client; `ReadAttempt(client, key, token)`; `ReadAccept(key, token, highest_before, value)` and `ReadReject(key, token, highest_before)` recorded by storage; `ReadAck(client, key, token, outcome, value)` recorded by the client, `value` present only when `outcome` is `served`. Each is recorded by the process that produces it, with that process's own sequence number; there is no cross-process clock.

## Observable events (new or extended in v3)
- The eight write and read events above also carry `grantor_term` (the term carried with the token).
- `Grant` gains `config_epoch`.
- `Agree(node, incarnation, proposal)` recorded by a lease node when it agrees to a proposal. `proposal` is the whole proposal: for a grant, client, token, lifetime and `config_epoch`; for a configuration, epoch, members and request id.
- `Agreed(decider, node, node_incarnation, proposal, counted_toward)` recorded only by the deciding node, once per (node, incarnation, proposal), when it receives that agreement (its own included); `counted_toward` lists the configuration epochs whose majority it is counted toward (one for a grant; e, e+1 or both for a commit of e+1; empty for an agreement recorded but not counted, such as re-admission evidence). A node in both e and e+1 has one `Agreed`, with both epochs.
- `ConfigCommitted(node, epoch, members, request_id, readmits, decided)` recorded by every lease node when it learns that a configuration is committed; `decided` is true only at the node that decided the commit, exactly once per epoch above 0; `readmits` lists the `[node, incarnation]` pairs it re-admits (empty if none). Every member of the initial configuration records it for epoch 0 when its incarnation 0 first starts, with `request_id` null, `readmits` empty and `decided` false; a later incarnation records nothing for epoch 0 and learns its configuration from others. A node that learns of a commit it did not decide records the same epoch, members, request id and readmits as the decided record, and names that record in its causes when the message by which it learned carried its identity.
- `ReconfigSend(operator, request_id, to, members)` recorded by the operator when it sends; `ReconfigRequest(operator, request_id, members)` recorded by the receiver.
- `ReconfigRefused(node, request_id, reason, epoch)` recorded by the receiver when it refuses; `epoch` is the superseding epoch for `superseded` and null otherwise.
- `ReconfigAck(operator, request_id, outcome, epoch)` recorded by the operator on receipt. The reply carries the identity of the receiver's own `ConfigCommitted` (decided or not) or `ReconfigRefused` record, which the ack names in its causes. If the outcome is `committed`, the receiver's record agrees in epoch, members and request id with the one decided record for that epoch.
- **Decision inputs (C3.5).** Every decision record carries the inputs it consulted, as named values, in the format of `observe/schema.md`, v5 addendum.

## Out of scope in v3
One key. Quorums are majorities of one configuration, or, for a configuration commit (C3.8), majorities of the old and the new one; no other quorum system. No agreement protocol of the artifact's own invention. How clients find the current configuration is the artifact's choice. No delegated tokens; no ledger rollback; no cryptography.

===== FILE: inputs/failure-model-v3.md =====
# Failure model v3: membership changes on real machines

**DRAFT 5, not registered.** Drafted 2026-10-23 by the fifth steward for change experiment X3; drafts 2 and 3 after two input reviews; drafts 4 and 5 by the sixth steward after a third and a fourth (`experiments/X3/input-review/`). Nothing here is an input until X3's pre-registration commits it.

Version 3. v2 and v1 are unchanged and their cell ids keep their meaning. v3 is **additive**: it adds an authority locus (configuration) and three cells. No earlier cell is retired. This file is self-contained: everything a reader needs from v1 and v2 is restated below, verbatim where marked.

A failure model is an **environment** (what the world can do) applied to **authority loci** (where a grant, a token, or a decision lives). A test cell is one environmental fault applied during one transition.

## Authority loci
v1's, unchanged:
- **Holder:** the client that believes it has an unexpired grant.
- **Grantor:** the lease leader of the moment, identified by `grantor_term`.
- **Fence ledger:** storage's highest accepted token for the key.

New in v3:
- **Configuration:** the committed membership of the grantor and its epoch (`contract/v3.md`). Configuration is the authority to grant authority. A node that has not learned of a newer configuration still holds, in its own view, authority under the old one; a node removed from the configuration may stay up and keep its state.

## Links (v2, restated verbatim)
Between every ordered pair of distinct processes (p, q) there is a **link p→q**, which is either up or down. A message p sends to q is delivered (possibly reordered or duplicated, never corrupted) only if p→q is up when it is sent; a message sent while p→q is down is lost, not delayed. A link's state changes only by a fault step and by a heal. A message's fate is fixed when it is sent: a message sent while p→q is up is delivered (it may arrive late, reordered, after p→q has gone down); a message sent while p→q is down is never delivered, even if the link comes back up.

**Connected.** Two processes p and q are *connected* while both p→q and q→p are up. A set of processes is *connected to each other* while every two of its members are connected. Connection is direct: p and q are not connected because both are connected to some r.

## Cells
v1's, restated verbatim:
- **F1.1 Crash-stop.** Any lease node, client, or storage replica stops without warning. It may later restart with whatever it had durably recorded and nothing else. A restarted client has no grant.
- **F1.2 Complete partition.** The processes are split into two sides. No message crosses between sides until the partition heals. Any bipartition is allowed, including one that isolates the current grantor from the other lease nodes while leaving it connected to a holder, or that isolates a holder from the grantor while leaving it connected to storage. Partitions heal; messages sent across the cut during the partition are lost, not delayed.
- **F1.3 Holder pause.** A client holding a grant is paused for longer than the grant's lifetime, then resumes and continues as if no time had passed. This is the case fencing tokens exist for.
  (v3 reading: "as if no time had passed" describes the paused process's state, which is frozen; its clock is not, F3.2.)

v2's, restated verbatim:
- **F2.1 Partial partition.** Any set of links goes down in both directions, whether or not the result is a bipartition. Connectivity may become non-transitive: p and q connected, q and r connected, p and r not. In the vocabulary of links, F1.2 is the special case in which the down links are exactly those between two sides.
- **F2.2 Simplex link failure.** Any set of links goes down in one direction only: p→q down while q→p stays up. A process may then hear from a peer it cannot answer, or be heard by a peer it cannot hear.
- **Heal.** A heal restores every link, whichever cells took them down.

New in v3:
- **F3.1 Reconfiguration under faults.** An operator may send a reconfiguration request to any lease node, member or not, at any step, including while any other cell is in effect, and may send another before the first is answered, to the same node or a different one. A request may add nodes, remove nodes (including the current grantor and the receiver), or both. A request is a message: it obeys the link rules above, so it is lost if the operator's link to the receiver is down when it is sent. A request is not a fault: it moves no "last fault".
- **F3.2 Clock step.** Time is counted in integer **ticks** of run time; a lifetime `L` is a whole number of ticks. A process's local clock reads ticks, and may jump forward or backward by any whole number of ticks at any step, including while the process is paused. Between steps, every clock advances at the rate of run time, by any number of ticks the run lets pass (a model explores every number, including those that carry a clock past a recorded deadline); clocks of different processes are otherwise unrelated. A decision that consults a clock consults this clock. A paused process's clock keeps advancing while it is paused.
- **F3.3 Amnesia.** A lease node may restart with no durable state at all (its disk replaced). It knows only what the deployment gives every node (its own identity, every lease node's name, the initial configuration's members, and `L`) and that it has lost its state (it can tell an amnesic restart from its first start, as an operator who replaced a disk knows). Everything it had recorded is gone. It begins a new **incarnation** (`contract/v3.md`). Its agreements are not eligible, and so count toward no majority, until it is re-admitted (`contract/v3.md`, "Re-admission": a commit of a configuration listing it, whose decider recorded this incarnation's agreement to that configuration); agreements made by an earlier incarnation, if delivered late, are judged by that earlier incarnation. It stays in the denominator of every majority (`contract/v3.md`, "Majority of a configuration").

Faults compose: a schedule may apply several cells in one run, and link failures accumulate until a heal.

## After the last fault
Liveness clauses (C1.4, C3.4) promise progress only **after the last fault** of the run: after the last crash, restart, partition, cut, drop, pause, resume, clock step or amnesic restart (a heal is not a fault; reconfiguration requests are not faults). From then on, a message between two connected processes is delivered within a bound that the processes do not know, and every clock advances at the rate of run time. Without this, no artifact could keep a liveness clause: delay is otherwise unbounded and clock readings are not evidence. Safety clauses hold at every point of every run, with no such assumption.

## Not in v3
Byzantine behaviour. More than one storage process. Ledger rollback or storage restored from backup. Partial loss of durable state (a restart that keeps some of what was recorded and loses the rest). Links that delay rather than lose. Any quorum system but majorities of one configuration (or of the old and the new, for a configuration commit), as `contract/v3.md` defines them. Operators who lie about the configuration they requested.

## What counts as an unknown category
Every safety clause of `contract/v3.md` (C1.1 to C1.3, C2.1, C2.2, C3.1, C3.5, C3.7, C3.8) must hold in every run of these cells, and every liveness clause (C1.4, C3.4) in every run whose schedule satisfies its premise; a cell never excuses a violation. When a violation is observed, it is a **known category** if a judge can attribute its mechanism to the effect of a cell in the run (that suggests further tests of that cell), and an **unknown category** otherwise (that revises this failure model). It is reported as **unexplained** until a judge discriminates. It is not assumed to be the implementation's fault.

## Changelog
- v3 (2026-10-23, draft 5): configuration locus; F3.1, F3.2, F3.3; "after the last fault"; unknown category restated. Reason: X3, the grantor's membership changes, on machines whose clocks step and whose disks are replaced; drafts 2 to 5 after four input reviews (draft 4: re-admission is a recorded fact; the F1.3 reading; clause list follows the contract; draft 5: integer ticks; what an amnesic node is given).

===== FILE: inputs/schedule-format.md =====
# Fault schedule format v2.2 (shared interface)

v2.2 fixed 2026-10-21 after X1 (one clarification, listed in the changelog). v2.1 fixed 2026-10-21 (two clarifications). v2 fixed 2026-10-20 by the steward, after M1's cross-run. v1 is kept as `schedule-format-v1.md`; nothing in it is removed. v2 adds the rules that v1 left open and that the judge named (M1 result, D2 and D3). Every schedule compiler derives from this file; a compiler that implements v1 is stale under v2.

## Shape (unchanged from v1)
```yaml
schedule: <name>                 # unique; used as the run id
derives: [F1.2, C1.2]            # cells and clauses this schedule exercises
processes:
  lease: [n1, n2, n3]
  clients: [c1, c2]
  storage: [s]
steps:                           # applied in order; each waits for its trigger
  - at: <trigger>
    do: <action>
end: <trigger>                   # see "End of a run"
bound: {events: 200}             # safety bound for both sides
```

## Triggers
A trigger is `start` or an observable event from `contract/v1.md` with optional field filters:
```yaml
at: start
at: {event: Grant, client: c1}
at: {event: WriteAck, client: c2, outcome: accepted}
at: {event: WriteReject}
```

**Rule T1, arming (new in v2; settles D2).** Step 1's trigger is armed at the start of the run. Step *i*'s trigger (*i* > 1) is armed at the moment step *i*−1's action is taken. A trigger matches only events emitted **after** it was armed. An event emitted before the trigger was armed never satisfies it, however well it matches. `start` fires the moment it is armed. **(v2.1)** The events that step *i*−1's own action emits synchronously (its `Request`, `WriteAttempt` or `Fault`) count as emitted after step *i*'s trigger was armed, so a step may be triggered by the event its predecessor produced. Both authors read v2 this way; v2.1 says it.

**Rule T2, taking the action.** Once a step's trigger has fired, the action is taken at some later point. The model side explores every such point; the impl side samples one. The next step's trigger is not armed until the action is taken, so no two steps are ever pending at once.

**Rule T3, waiting workload.** A workload action (`request`, `write`) whose client is crashed or paused waits until the client is running. A `request` by a client that already has a request outstanding waits until that request is answered. A `write` by a client that holds no token waits until it holds one, except `token: stale`, which waits until the client has a superseded token.

## Actions (unchanged from v1 except as marked)
Workload:
```yaml
do: {request: c1}
do: {write: c1, value: v1}                # with the client's current token
do: {write: c1, value: v2, token: stale}  # with the client's most recent token that is lower than the highest token granted so far
```
Faults, one per cell:
```yaml
do: {cell: F1.1, crash: n2}
do: {cell: F1.1, restart: n2}
do: {cell: F1.2, partition: [[grantor, c1, s], [rest]]}
do: {cell: F1.2, heal: true}
do: {cell: F1.3, pause: c1}
do: {cell: F1.3, resume: c1}
```
A `pause` must outlast the grant's lifetime: the matching `resume` must be triggered by an event that can only happen after expiry (a later `Grant` to another client, or an ack of a write made under a later grant).

**Rule A1, aliases (new in v2; settles D3).** `grantor`, `holder` and `rest` are process selectors and may appear **wherever a process name may appear**: as the target of `crash`, `restart`, `pause`, `resume`, `request` and `write`, and as members of a partition side. `grantor` is the node that issued the most recent `Grant` event; `holder` is the client that received it; `rest` is every process not named on the other side of the same partition. Aliases are resolved at the moment the step's trigger fires. A schedule that uses `grantor` or `holder` before any `Grant` can have occurred is rejected by the compiler. **(v2.1)** A fourth selector, `non-grantor`, means a lease node other than `grantor` that is up at the moment the trigger fires. The model side explores every such node; the impl side picks the lowest-numbered one. It exists because leadership before the first `Grant` is not observable, so "crash a follower" can only be said after a grant. **(v2.2)** `restart: non-grantor` names the node that the most recent `crash: non-grantor` crashed, whether or not it is a non-grantor at the moment of the restart; a schedule with `restart: non-grantor` and no earlier `crash: non-grantor` is rejected. All four fresh-arm authors in X1 read v2.1 this way and flagged that the text did not say it.

**Rule A2, crash and restart.** `restart` of a process that is not crashed, `crash` of a process already crashed, `pause` of a paused client, `resume` of a running client, and `pause` of a lease node or storage are all rejected by the compiler.

## End of a run
**Rule E1 (new in v2).** `end:` is either an event trigger, armed when the last step's action is taken and matched by Rule T1, or the word `quiescent`. `quiescent` means: every step has been applied and no request, write or ack is in flight and no client is waiting for a grant, with crashed and paused processes not counted. On the model side `quiescent` is a state predicate; on the impl side it is a bounded wait for in-flight work, after which an unanswered request is reported through the liveness checker, not as `end` unreachable. The shared schedules use `quiescent` unless the end must be a specific event.

**Rule E2.** A clause violation witnessed before the end is a `FAIL` whether or not the end is reached. `UNEXPLAINED end unreachable` is reported only when no violation was witnessed.

## Rules carried from v1
- A schedule may not name an action the failure model does not contain; the compiler rejects it.
- Nondeterminism the schedule leaves open (message order within a side, delay between trigger and action) is explored by TLC and sampled by the impl. A pass on one side and a failure on the other is a divergence, not a bug on either side.
- **Schedules live in `testbed/schedules/<name>.yaml` and nowhere else.** Both runners resolve a name there. The authors' private schedule sets from M1 are kept under their own directories as history and are no longer run.

## Changelog
- v2.2 (2026-10-21): `restart: non-grantor` defined. Reason: X1 result, residues.
- v2.1 (2026-10-21): T1 clarified for a predecessor's own events; `non-grantor` selector. Reasons: M1 result, round 2 residues. Shared P10 rewritten to use it.
- v2 (2026-10-20): T1 arming, T2, T3, A1 aliases, A2, E1 `quiescent`, E2; schedules shared. Reasons: M1 result D2 and D3.

## v3 addendum (2026-10-21, for contract v2; additive)
One workload action is added. Everything else in v2.1 is unchanged.
```yaml
do: {read: c1}                 # c1 reads the key with its current token
do: {read: c1, token: stale}   # with its most recent token lower than the highest granted so far
```
Rule T3 applies to `read` as it does to `write`. Triggers may name the new events `ReadAttempt`, `ReadAccept`, `ReadReject` and `ReadAck` (with `outcome: served` or `rejected`). Changelog: v3 (2026-10-21): `read` action and the four read events. Reason: X1, contract v2.

## v4 addendum (2026-10-21, for failure model v2; additive)
Two fault actions are added, one per new cell. Everything above is unchanged; a compiler that implements v3 and not v4 is stale only for schedules that name F2.1 or F2.2.
```yaml
do: {cell: F2.1, cut: [[n1, n3], [grantor, c2]]}    # each listed link goes down in both directions
do: {cell: F2.2, drop: [[n2, grantor], [n3, grantor]]}  # messages from the first to the second are lost; the reverse direction is untouched
do: {cell: F2.1, heal: true}                          # restores every link (also {cell: F2.2, heal: true} and {cell: F1.2, heal: true})
```
**Rule L1, links.** Each entry of `cut` or `drop` is a pair of process names or selectors. `grantor`, `holder` and `non-grantor` are allowed and are resolved as Rule A1 says, at the moment the step's trigger fires; `rest` is not allowed in a link, since it is defined only against a partition side. A pair whose two ends resolve to the same process is ignored, so `[n1, grantor]` is safe whichever node is the grantor. Taking down a link that is already down is allowed and changes nothing. A selector names one process per pair; to reach both followers write the pairs out (`[[grantor, n1], [grantor, n2], [grantor, n3]]` reaches exactly the two that are not the grantor).

**Rule L2, accumulation.** Link failures from `cut`, `drop` and F1.2 `partition` accumulate. A `heal`, whatever cell it names, restores every link. There is no partial heal.

**Rule L3, the premise of C1.4.** Whether a run's schedule satisfies C1.4's premise is read with "connected" as `failure-model/v2.md` defines it: both directions of the direct link up. A schedule whose comment claims a requester "should eventually get a grant" must leave a majority of lease nodes, storage and that requester connected to each other for the rest of the run after its last fault. The premise is read **literally**: it names no grantor, so the majority need not include the grantor of the moment, and the requester need not be connected to it. If the premise holds, the requester must eventually obtain a grant by whatever route the artifact provides; how a request reaches a node that can grant, and how the grant comes back, is the artifact's business. **A requester** is a client that has taken a `request` step and has not yet received a grant in answer to it; a request or a grant lost on a down link does not end the client's standing as a requester.

**Rule E1, extended to reads.** In `quiescent`, "no request, write or ack is in flight" includes reads and read acks. The v3 addendum should have said so and did not.

**Rule E3, the bound.** A run that reaches `bound` before its end is reported `UNEXPLAINED bound`, never `PASS`. It is `FAIL C1.4` only if the side's liveness check witnesses the violation (on the model side a counterexample to the liveness property; on the impl side the liveness checker's report under Rule E1).

**Rule T3, unchanged and restated.** A `write` or `read` does not wait for an earlier unanswered `write` or `read` by the same client; only `request` waits for its own answer. A client that serialises its operations must not wait for ever on a reply that was lost.

Triggers may name `Fault` records for the new actions as for the old. Changelog: v4 (2026-10-21): `cut`, `drop`, L1 to L3, E1 extended to reads, E3, T3 restated. Reason: X2, failure model v2; the E1 gap, the readings in L3, E3 and T3 came from review of the inputs before any author started.

## v5 addendum (DRAFT 5, 2026-10-23, for contract v3 and failure model v3; additive; not an input until X3 registers)
**Processes.** `processes` gains two optional keys. `config` lists the initial configuration (epoch 0) and must be a subset of `lease`; if absent it is all of `lease`. Lease nodes in `lease` and not in `config` exist, up and connected, as non-members. `operators` lists operator processes (default `[op]`); operators are not lease nodes, clients or storage, and links to and from them obey F1.2, F2.1 and F2.2 like any process's. **Lifetime.** `lifetime: <n>` (optional, default 1) sets `L` as a whole number of ticks (`failure-model/v3.md`, F3.2); clock steps are written in units of `L` and must come to a whole number of ticks.
```yaml
processes:
  lease: [n1, n2, n3, n4, n5]
  config: [n1, n2, n3]
  clients: [c1, c2]
  storage: [s]
  operators: [op]
```
Three actions are added, one per new cell:
```yaml
do: {cell: F3.1, reconfigure: [n1, n2, n4], to: n2, id: r1}   # op sends request r1 naming these members to n2
do: {cell: F3.2, clock: n1, step: -2}                          # n1's clock jumps back by 2 L (signed; step × lifetime an integer)
do: {cell: F3.3, restart: n2, amnesia: true}                   # n2, which must be crashed, restarts with no durable state
```
**Rule R1, reconfiguration requests.** `to` names the receiver: any lease node, member or not, or a selector (`grantor`, `non-grantor`, and the new `non-member`, a lease node not in the configuration of the latest `decided: true` commit, or of epoch 0 before any; read against the configuration of the highest-epoch `ConfigCommitted` with `decided: true` in the trace, or epoch 0 before any; resolved as `non-grantor` is: the model side explores every choice, the implementation side takes the lowest-numbered). `id` is the request id the operator uses, unique within the schedule. The members listed are process names, not selectors. The operator is `op` unless the step says `operator: <name>`. A `reconfigure` does not wait for an earlier one to be answered (F3.1). The request is a message from the operator: it is lost if the link from the operator to the receiver is down when it is sent. A request whose set is empty or names a non-lease process is allowed (C3.4(a)'s `invalid`). A `reconfigure` step emits the operator's `ReconfigSend`, never a `Fault`, and is not a fault.
**Rule R2, clocks.** A clock step changes only the named process's clock, by `step × L` ticks. A `pause` (F1.3) must still outlast `L` in run time, as v1 says; the paused process's clock keeps advancing. Under v3 a later `Grant` is no evidence that `L` has passed (a grantor need not wait, and its clock may jump), so a `resume` is taken no earlier than `L` ticks of run time after its `pause`, whatever its trigger.
**Rule R3, amnesia.** `restart` with `amnesia: true` is allowed only for a crashed lease node. There is no bound on how many nodes may be amnesic: an amnesic incarnation's agreement counts toward no majority until it is re-admitted, while the node stays in every denominator (`contract/v3.md`, "Majority of a configuration"), so a schedule may leave fewer than a majority of a configuration's members eligible; then C1.4's and C3.4(b)'s premises are false (they require an eligible majority to exist) and those clauses promise nothing.
**Rule L3, extended (C1.4 and C3.4 premises).** Under contract v3 both premises are read only **after the last fault** (`failure-model/v3.md`). In a premise, "the configuration" is the **globally committed configuration**: the one of the highest-epoch `ConfigCommitted` with `decided: true` in the trace, or epoch 0 before any (not any one node's current configuration); "majority" is the contract's single definition, and both premises also require more than half of its members to be eligible. C1.4's premise holds only while no reconfiguration request is pending (at its receiver, as `contract/v3.md` defines it) at any lease node that is up. C3.4(b)'s premise for a request holds if the request is still pending at its receiver after the last fault (a copy destroyed by an amnesic restart creates no duty) and, for the rest of the run, its receiver, a majority of the current configuration and a majority of the requested set stay up and connected to each other; C3.4(a) needs only that the receiver stays up; either duty to tell the operator holds if the operator also stays connected to the receiver. A schedule comment that claims progress must leave such a set connected.
**Rule T1, extended.** The events a step's own action emits synchronously include `ReconfigSend` and the `Fault` records of `clock` and amnesic `restart`, so a step may be triggered by them.
**Rule E1, extended.** In `quiescent`, nothing is in flight also means no reconfiguration request is pending at a receiver that is up and no `ReconfigAck` is in flight.
Triggers may name `ReconfigSend`, `ReconfigRequest`, `ConfigCommitted` (with `epoch`, `members` or `request_id` filters), `ReconfigRefused` (with `reason`), `ReconfigAck` (with `outcome`), `Agreed`, and `Fault` records for the new actions. Triggers may also name `Agree`. Changelog: v5 (2026-10-23, draft 4): `config`, `operators`, `lifetime`, `reconfigure`, `clock`, `restart ... amnesia`, R1 to R3, L3, T1 and E1 extended. Reason: X3; drafts 2 to 4 after three input reviews.

===== FILE: inputs/observe-schema.md =====
# Observability schema v1 (shared interface)

Fixed 2026-10-20 by the steward. `derives: C1.1, C1.2, C1.3, F1.1, F1.2, F1.3` (every clause and cell: this layer is what lets an unexplained failure be traced).

Both sides emit the same record, one JSON object per line, into `observe/<run>.jsonl`. The model side emits it from a TLC trace; the impl side emits it live.

## Record
```json
{"proc": "s", "seq": 17, "event": "WriteAccept",
 "key": "k", "token": 4, "highest_before": 3,
 "grantor_term": 2,
 "causes": [{"proc": "c1", "seq": 9}],
 "run": "false-suspicion-v1", "side": "impl"}
```
- `proc`, `seq`: the emitting process and its own counter. There is no cross-process clock and no wall-clock field in the record. Impl implementations may keep wall time in a separate file for humans; it is never used for ordering.
- `event` and its fields: exactly the observable events in `contract/v1.md`.
- `grantor_term`: on `Grant`, the term of the grantor that issued it; on `WriteAttempt`, `WriteAccept`, `WriteReject`, the term carried with the token. This is how a consequence is traced to the authority that produced it.
- `highest_before`: on storage decisions, the fence ledger's value when the decision was taken. The decision must be explainable from `token` and `highest_before` alone.
- `causes`: the records this one is a consequence of, by `(proc, seq)`. A `WriteAccept` causes the `WriteAttempt`; a `WriteAttempt` causes the `Grant` whose token it uses; a `WriteAck` causes the storage decision. A fault step from the schedule is recorded too, as an event `Fault` from `proc: "env"` with the step's action as fields, so a trace can show which fault preceded a consequence.

## The provenance question a trace must answer
For every `WriteAccept` and `WriteReject`: which `Grant`, from which `grantor_term`, produced the token presented, and what was the ledger when storage decided. If a trace cannot answer that for some decision, the observability layer has failed its own test, independently of the contract.

## v2 addendum (2026-10-21, for contract v2; additive)
The four read events from `contract/v2.md` are recorded with the same fields as their write counterparts, plus `value` on `ReadAccept` and on a served `ReadAck`. `causes` for a `ReadAccept` or `ReadReject` names the `ReadAttempt`; a `ReadAttempt` names the `Grant` whose token it uses; a `ReadAck` names the storage decision. The provenance question extends to reads: for every `ReadAccept` and `ReadReject`, which `Grant` and `grantor_term` produced the token, and what was the ledger when storage decided. `observe/provenance_check.py` is extended by the steward to check read decisions too.

## v3 addendum (2026-10-21, after X1; additive)
`WriteAck` and `ReadAck` carry a field `answers: {proc, seq}` naming the `WriteAttempt` or `ReadAttempt` they answer. It is redundant with `causes` (the storage decision, which in turn names the attempt) and is required anyway, so that a retried request's acks can be told apart without a traversal. Reason: the X1 regenerate-arm model author reported that without it a wrong ack is indistinguishable from a late one except through `causes`; tessera's finding E-02 (a timed-out signing request answered after its retry, two valid signatures for one presentation, nothing in the record naming which was which) is the same mechanism in a real service, cited from `docs/requests/2026-10-21-from-tessera-evidence-offer.md`. `observe/provenance_check.py` checks that `answers` names an attempt in the trace and that the ack's `causes` chain reaches the same attempt.

## v4 addendum (2026-10-21, for failure model v2; additive)
A `Fault` record for an F2.1 `cut` or F2.2 `drop` carries `links: [[from, to], ...]`, the **directed** links the step took down after selectors were resolved and self-pairs removed (a `cut` of `[a, b]` is recorded as `[a, b]` and `[b, a]`). A heal's `Fault` record carries `links: []` and `heal: true`. **Grants and retransmission.** A `Grant` record is a grant: each one is subject to C1.1 and must carry a token strictly greater than every earlier `Grant` record's. A grantor that re-sends a grant it has already recorded (because the reply may have been lost) does not record a second `Grant`; the resend is a retransmission, like a duplicate delivered by the network, and the client that receives it records nothing new. An artifact that instead issues a fresh grant records a new `Grant` with a higher token. Nothing else changes: the provenance question is the same, and `observe/provenance_check.py` needs no change, because link faults decide only which messages arrive, not where a token came from.

## v5 addendum (DRAFT 5, 2026-10-23, for contract v3 and failure model v3; additive; not an input until X3 registers)
`derives: C1.1, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3`
**Identity.** A record is identified by `(proc, inc, seq)`: `inc` is the emitting lease node's incarnation (`contract/v3.md`); for any other process it is the number of times that process has restarted (a client keeps no durable records, so this is what keeps its identities distinct). `seq` restarts at 0 in each incarnation and never repeats within one, across ordinary restarts too: a process that restarts recovers it as greater than any it used before (keep it durable, or recover it from the durable records). Every v5 record carries `inc`; a reference (`causes`, `answers`, `ref`) to a lease node's record names all three. Records from v1 to v4 without `inc` are read as `inc: 0`.
**New events.** `Agree`, `Agreed`, `ConfigCommitted`, `ReconfigSend`, `ReconfigRequest`, `ReconfigRefused`, `ReconfigAck`, `Overflow`, with the fields `contract/v3.md` names; `Grant` gains `config_epoch`, and the eight write and read events carry `grantor_term`. Every initial member's first record is `ConfigCommitted` for epoch 0 with `decided: false`. An operator's send is `ReconfigSend`, never a `Fault`; a request is not a fault. F3.2 is a `Fault` with `clock: proc, step` (signed, in units of `L`); F3.3 a `Fault` with `restart: proc, amnesia: true`.
**Causes, made obligatory where a reply carries an identity.** A `ReconfigAck` names in `causes` the receiver's own `ConfigCommitted` or `ReconfigRefused` record, whose identity the reply carries. An `Agreed` names the node's `Agree`, whose identity the agreement message carries. A `ConfigCommitted` with `decided: false` for an epoch above 0 agrees with the decided record for that epoch in epoch, members, request id and readmits, and names it in `causes` when the message that taught it carried its identity (a protocol that teaches by snapshot need not).
**Decision records and their inputs** (`derives: C3.5, F3.2`). The decision records are `Grant`; `WriteAccept`, `WriteReject`, `ReadAccept`, `ReadReject`; `ConfigCommitted` with `decided: true`; `ReconfigRefused`. Each carries `inputs`: a list of `{"name": <string>, "value": <JSON>}` items, optionally with `"ref": {"proc", "inc", "seq"}` when the value came from an earlier record. **The names are fixed:**
- storage decisions: `token`, `ledger`, `stored_value`, and for writes `value`;
- grants: `agreed` (each counted `Agreed`, by `ref`), `members` and `config_epoch` (the configuration counted against), `grantor_term` (the term the decider holds), `last_token` (the highest token the decider knew to be granted or agreed, by `ref` where it came from a record), and, if the grantor waits on its clock, `clock` and `last_grant_at`;
- decided commits: `agreed`, `old_members`, `old_epoch`, `request_id`, `requested_members`;
- refusals: `request_id`, `requested_members`, and for `busy` the pending request (`pending`, by `ref`), for `superseded` the commit (`commit`, by `ref`);
- any decision that reads a clock: `clock` (as read).
An artifact may add a name only if it states in its README which decision consults it and why the outcome may depend on it; a name neither fixed nor so declared is reported as invalid. A record's own identity, a sequence number, a request id used only as a label, or any value chosen to be unique to one run is never an input. A field the decision chose (a grant's token, a commit's `readmits`) is an outcome; listing it among the inputs does not make it one.
**The rule.** Every input a decision consults is recorded in `inputs` or is forbidden. A decision may not depend on anything else: unrecorded wall time, the iteration order of an unordered map, goroutine scheduling, an unrecorded random draw.
**The decision-replay check** (steward-built in `observe/`, validated with its mutation pair before any author starts). Three parts, over every trace of a side:
1. *Evidence*, per decision, from its inputs and the trace: storage decisions against v3's rule; a `Grant`'s counted `Agreed` records name distinct nodes, are eligible for its configuration (`contract/v3.md`, "Eligible agreement", re-admission read from decided `ConfigCommitted` records' `readmits`) and form a majority of its `members` (C3.7), and those `members` equal, as a set, the committed configuration of its `config_epoch` (the epoch-0 records for 0, the decided record otherwise), never only what the decider wrote; a decided `ConfigCommitted` of epoch e+1 is counted by eligible majorities of e and of its own `members` (C3.8), its `old_members` equal the committed configuration of e and its `members` the set of the request it names (from that request's `ReconfigRequest` or `ReconfigSend`); and its `readmits` is exactly the set of `[node, inc > 0]` in its `members` with an `Agreed` for this proposal among its recorded inputs; C3.1: at most one decided `ConfigCommitted` per epoch, and epochs committed in order.
2. *C1.1 without a global order*, and terms: no two `Grant` records share a token; a grant under a higher `config_epoch` has a higher token than every grant under a lower one; for each node, over its `Agree` records for grants that some `Grant` counted, in its own `(inc, seq)` order, tokens strictly increase; two `Grant` records with one `grantor_term` were decided by the same `(proc, inc)`.
3. *Function of inputs* (C3.5), across every run of the side: decisions of one kind whose inputs are equal have equal outcomes. Equality: inputs compared as name-value sets with each `ref` replaced by the content of the record it names, recursively, **without** that record's identity (`proc`, `inc`, `seq`, `causes`), so renumbering by a retransmission does not make equal inputs unequal; member lists compared as sets. Outcomes: `Grant`, token, client, `config_epoch`; storage, the event and for reads the value; decided `ConfigCommitted`, epoch, members as a set, `readmits` as a set; `ReconfigRefused`, reason. Each group with unequal outcomes is reported `UNEXPLAINED inputs`.
Mutation pair: on synthetic traces, (a) two runs whose grants have equal inputs and different tokens must fail part 3, and with equal tokens pass; (b) a grant counted by a minority, (c) a commit counted by the new majority only, (d) an amnesic incarnation counted before re-admission, each must fail part 1; (e) two grants with one token, (f) a node whose counted agreements to grants decrease in token, (g) two grants with one term from different deciders, each must fail part 2; (h) a grant counted against a `members` list that is not the committed configuration, (i) a commit whose members differ from its request's, (j) a commit whose `readmits` omits a recorded re-admission agreement, each must fail part 1; and the legitimate counterpart of each must pass.
**Measure, not requirement.** For small fixed schedules, the number of model behaviours consistent with an observed trace's projection onto this schema, per schema version: how much each field narrows the set of executions consistent with what was observed, which is the seed's definition of this layer.

===== FILE: arm A model/README.md, its X3 section (lines 11 to 356) without its tables of mutations and results (lines 133 to 336; each item gives the run's own verdict lines) =====
## X3 adapt arm (contract v3, failure model v3: a changing membership)
derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F1.1, F1.2, F1.3, F2.1, F2.2, F3.1, F3.2, F3.3; format v5 addendum (config, operators, lifetime, reconfigure, clock, restart amnesia, R1-R3, L3, T1, E1); observe v5 addendum; pairs v4

Additive. Nothing that derives from a v1 or v2 clause or cell is retired; where an earlier interpretation no longer holds, it is named below under "Contradicted", the earlier text is left as it was, and this section says what replaces it. The predictions and their one amendment are in `PREDICTIONS-x3.md` (committed before any change to the model; amendment 1 after the new mutations ran, and says so).

Written only from `contract/v3.md`, `failure-model/v3.md`, `tests/pairs-v4.md`, `testbed/schedule-format.md`, `observe/schema.md`, `observe/decision_replay.py` and its test traces, `testbed/schedules/`, `AGENTS.md`, the X3 brief and this directory.

### The protocol followed
- **Raft with joint consensus.** Diego Ongaro and John Ousterhout, "In Search of an Understandable Consensus Algorithm", USENIX ATC 2014, section 6 (cluster membership changes); Diego Ongaro, "Consensus: Bridging Theory and Practice", PhD thesis, Stanford University, 2014, chapter 4 (catching up new servers, removing the current leader, disruptive servers, arbitrary changes using joint consensus), and the Pre-Vote and leader step-down mechanisms of the same thesis. (Section numbers are from memory; I had no access to the texts in this session.)
- **Level of abstraction.** The previous author's: a leader per term; an election in which a majority promises a fresh term and the new leader adopts the most recent state of its quorum (this replaces Raft's "log at least as up-to-date" check, as before); a grant decided in one step with the majority's agreement. The X2 mechanisms are Raft's: voter stickiness is Pre-Vote, `CheckQuorum` is the leader stepping down without a majority's heartbeat responses, `Join` is the leader's AppendEntries bringing a follower into its term.
- **Membership change.** A leader of epoch e takes a pending request and decides epoch e+1 in one step, counted by eligible agreements from a majority of e's members and from a majority of the requested members, one agreement for a node in both (Raft's C_old,new rule). Every node that agreed keeps the proposal durably (`jprop`, Raft's joint entry in its log). An election adopts the newest configuration its voters know, including such a kept proposal, and its quorum must be an eligible majority of that configuration (Raft: a server uses the newest configuration in its log). New servers are caught up before they count: a node agrees to a change only once it has recorded the leader's configuration history (thesis, catching up new servers). A leader that a commit removes steps down in that step (thesis, removing the current leader).
- **Amnesia (F3.3).** Raft assumes stable storage and has no rule for a lost disk. I follow the rule of Tushar Chandra, Robert Griesemer and Joshua Redstone, "Paxos Made Live: An Engineering Perspective", PODC 2007 (section on disk corruption, numbered 5.1 from memory): a replica that lost its state rebuilds it and takes no part in decisions until the protocol has brought it back. In Raft's terms the amnesic node is a non-voting member: it may be joined into the leader's term, learn the configuration and agree to a change, but its votes and agreements count toward no majority until a commit re-admits it. Its re-admission is the contract's: a commit of a configuration that lists it, whose decider recorded this incarnation's agreement to that very proposal (`counted_toward: []`). It stays in every denominator.
- **Where I adapted it to the contract.**
  1. The contract's commit of e+1 is Raft's commit of C_old,new; Raft's later C_new entry is taken to follow at once (one step), so there is no joint phase in which grants need both majorities.
  2. An agreement and the decision that counts it are one step. So every agreement recorded in a trace was counted (or is re-admission evidence), and every kept proposal is a decided one. That is how the model records exactly one decided `ConfigCommitted` per epoch: a later leader that adopts a kept proposal records it as learned (`decided: false`), never decides it again. In Raft a new leader would commit an inherited entry indirectly, and an implementation must still decide who records the single decided record; the atomic step sidesteps that question, which is a limitation (below).
  3. A request targets the epoch after its receiver's current one when the receiver records it; a leader commits it only at that epoch; another commit of that epoch supersedes it (C3.4). Raft has no request ids or refusals.
  4. Eligibility applies to votes as well as to agreements (an amnesic incarnation does not vote until re-admitted).
  5. A receiver that is not the leader holds the request, it reaches the leader directly or through one lease node (as a client's request does, FR.1), and the receiver records the outcome when it learns the commit, and answers.
  6. The grantor does not wait for expiry, so no decision reads a clock (contract v3 "Lifetime" allows this).

### What changed in `Lease.tla` (and why)
Required by the meaning of the new clauses and cells:
- **Lease nodes and configurations** (C3.1, C3.7, F3.1). `Nodes` is any set the schedule names (up to six), `Init0` the initial members. `cfg[n]` is the committed configurations n has recorded, by epoch (record: epoch, members, request id, the incarnations its commit re-admits, decider); `Cur(n)` is n's current configuration. `MajOf(Q, M)` replaces `Majority(Q)`: more than half of M, the whole membership as denominator. `Majority(Q)` counted against the three fixed nodes and derived from C1.1, C1.4; it is not retired as an idea, it is now `MajOf(Q, Init0)` before any change.
- **Elections** (C1.1, C1.4, C3.1, C3.7, F3.1, F3.3). `Elect` adopts the newest configuration history in its quorum (`Adopt`), and its quorum must be an eligible majority of that configuration. The X2 rules (voter stickiness, the direct link for votes) are kept.
- **Grants** (C1.1, C3.5, C3.7, F3.1, F3.3). `Grant` counts eligible agreements from a majority of the leader's current configuration; the leader must itself be an eligible member. The `grants` history records the epoch, the members counted against, the counted [node, incarnation] pairs and the last token the leader knew; the token is last_token + 1.
- **Configuration change** (C3.1, C3.4, C3.5, C3.8, F3.1, F3.3). New actions `Commit(l, x)`, `LearnConfig(n, m)`, `RecvReconfig(m)`, `ReplyOp(x, a)` and the workload step `DoReconfig`. New variables `cfg`, `jprop`, `pend`, `owed`, `rcMsgs`, `opMsgs`, `commits`, `refusals`, `opTold`.
- **Amnesia** (F3.3, C3.7, C3.8, C1.1). `inc[n]`, the incarnation; `AmnesicRestart(n)` loses `promised`, `maxTok`, `cfg` (back to the deployment's epoch 0, unrecorded), `jprop`, `pend`, `owed`. `Crash` and `Restart` keep their v1 meaning for ordinary restarts, and now also clear a node's early timers and the requests in flight to it.
- **Clocks** (F3.2). `off[p]` (clock reading minus run time, in ticks) and `early[n]`; `ClockStep(p, s)`. See "Clocks" below.
- **Decision inputs** (C3.5). Storage decisions also record the stored value; grants, commits and refusals record their inputs (`grants`, `commits`, `refusals`).
- **Properties.** `C1_1` is v3's reading of C1.1; `C3_1`, `C3_7`, `C3_8`, `C3_5`, `TermUnique`; `Good(c)` is C1.4's v3 premise; `GoodR(x)` and `C3_4`; the terminal-state forms `C1_4T`, `C3_4T` and the progress measure `Progress` (see "Liveness"). The v1 reading is kept as `C1_1order`.
- **Quiescent** (format v5 E1): no request in flight to an up receiver, none pending at an up receiver, no reply owed over an up link.
- **Event bookkeeping** (mechanical). `lastEv` is a sequence: one step may emit several records (a grant with its agreements; a learned commit with a refusal). `Internal` emits nothing (before X3 it recorded the step's name, which only multiplied states). `View` (every variable but `lastEv`) is the fingerprinted view; `lastEv` is output only.

Mechanical propagation, no change of meaning: every existing action's frame names the new variables; `Resolve`, `SideOf`, `StepLinks`, `Resolved`, `DoStep` take the `non-member` choice; `Emit` and `ScheduleStep` record `trigNM`; `NGChoices` treats an amnesic `restart: non-grantor` as a restart.

### Abstractions (named)
1. **Agreement and decision in one step** (grants as before; commits new). An agreement that is never counted is not modelled, nor is a decision made later than its agreements. Every behaviour of the model is a behaviour of the protocol; the converse does not hold.
2. **C_old,new and C_new in one step** (adaptation 1).
3. **One heartbeat reaches every follower whose link is up, in one step** (`Join(n)`). X2's `Join(n, q)` joined one node per step; the set of reachable promises is the same, the intermediate states are not explored. The leader replicates to the members of its current configuration and to the members of a request for its next epoch (`JoinScope`).
4. **A reply to an operator is received in the step it is sent** (`ReplyOp`). It is sent only over an up link, so its fate is the one the failure model fixes; only the delay is not explored. Operators never crash and no clause depends on that delay. `opMsgs` is therefore always empty.
5. **A commit is learned one epoch at a time, from any node that has recorded it, by** a member of the configuration it commits, a receiver holding a request, or a node a pending request names. A node a commit removed need not learn of it.
6. **Clocks** (below): no recorded decision reads a clock; a clock's effect is on timers only.
7. As before: one-hop relays through lease nodes; a relay forwards atomically; the election's adoption from its quorum instead of Raft's log comparison; `MaxDups = 1` duplicated delivery, of writes and reads only.

### Clocks (F3.2)
- No recorded decision of the unmutated model reads a clock: grants do not wait for expiry, storage decides on token and ledger only, commits and refusals on agreements and requests. So no decision records `clock` or `last_grant_at`, and C3.5 has no clock input to miss.
- Timers do read clocks. The model's failure detector is untimed ("hears no leader"), so a timer may fire at any point once its condition holds. A **forward** step on a running lease node may additionally fire its timers early: `early[n]` lets n stand for election or vote although it hears a leader, and lets a leader give up its quorum (`CheckQuorum`). Acting on it resets it. A **backward** step only delays timers, which the untimed detector already allows, so it enables nothing new; it changes only `off`.
- `off[p]` is kept so that the record of a run is complete and so that mutations can read a clock; no unmutated action reads it.
- Because of this, every step size is represented: any forward step on a lease node sets the same flag; every backward step and every step on a client, storage or operator changes nothing but `off`. The model needs no bound on step sizes, and a schedule with steps of other sizes reaches the same states.
- Format v5 R2 ("a resume is taken no earlier than L ticks after its pause") is not enforced: time is abstract, and a resume may be taken at any later point. The model explores a superset of the behaviours R2 allows.

### What is checked, and in what order
- **Unmutated runs** check, in this order: `TypeOK`, `C1_1`, `C1_2`, `C1_3`, `C2_1`, `C2_2`, `C3_1`, `C3_7`, `C3_8`, `C3_5`, `TermUnique`, `C1_4T`, `C3_4T` (only if the schedule has requests), `C1_1order`, `TermHeadroom`, and the action property `Progress`. A state that violates several reports the first. `C1_1order` and `TermHeadroom` print `UNEXPLAINED`, never `FAIL`.
- **`C1_1`**, v3's reading: (a) no two grants carry one token; (b) a grant under a higher epoch carries a higher token than every grant under a lower one; (c) each node's counted agreements to grants, in its own order (incarnations included), carry increasing tokens.
- **`C3_7`** checks each grant against the *globally* committed configuration of its epoch (the decided commit, not what the decider believed), with eligibility read from decided commits' re-admissions.
- **`C3_8`** checks each decided commit's counted agreements against the committed configuration of the previous epoch and its own members (eligibility by re-admissions other than this commit's), that its members are its request's, and that every `committed` an operator was told names a decided commit of that request and epoch, at the moment it is told.
- **`C3_5`** checks that every recorded decision's outcome is the model's fixed rule applied to the inputs recorded with it (grants: token = last_token + 1; storage: accept or serve iff token ≥ ledger, a served read returns stored_value; commits: epoch = old_epoch + 1, members = requested_members, readmits = the recorded agreements of incarnations above 0 in the new membership; refusals: invalid, then busy, then superseded, from their inputs). A fixed function of the recorded inputs implies C3.5's statement about any two runs. `observe/decision_replay.py` is also run over every observe file (`run.sh --replay`, and at the end of `--all`).
- **Mutation runs check the pair's own clause** (with `TypeOK`, `TermHeadroom`, and `Progress` for a liveness clause). Under v3 a break on one clause's path often violates another first; P2's (a grant without a majority) violates C3.7 in the very state the grant is issued, before any token repeats. The question a pair asks is whether its clause's check catches the break. For the three C3.5 pairs the replay is run on the counterexample together with the unmutated witness of the same schedule and must report it.

### Liveness, checked at terminal states
TLC's liveness search was impractical here: with more than eighty weak-fairness conditions it explored P46 at about 13,000 states a minute. The model's liveness clauses are checked instead as follows.
- **`Progress`**, an action property checked on every transition: each step but stuttering strictly increases `Measure`, lexicographically. The components, in order: the schedule position; each node's promise; the number of non-leaders; the grants; each client's request phase; the storage decisions; the commits; each node's recorded configurations; and, decreasing, the acks queued and in flight, the read acks, the requests in flight, each node's owed replies. Each protocol action raises one component and leaves every earlier one unchanged or raised. TLC checks this; a deliberately cyclic variant of the model violates it.
- So the state graph has no cycle but stuttering, and every behaviour that satisfies `Fairness` ends stuttering in a state where no fair step (`FairNext`) is enabled; and every path to such a state, stuttering there, satisfies `Fairness`. Hence C1.4 and C3.4 hold under `Fairness` iff at every reachable such state each premise implies its conclusion: `C1_4T` and `C3_4T`. A violation is a trace to that state, which is a genuine counterexample to the temporal property.
- `<>[]Good(c)` at a terminal state is `Good(c)` there; "after the last fault" is automatic, because a terminal state comes after every schedule step.
- If `Progress` fails on some run, `run.sh` re-checks the invariants without it, runs the acyclicity search `Acyclic` (no fairness), and if a cycle exists falls back to TLC's own liveness check of `C1_4` and `C3_4` under `Spec`. It never did.

### Fairness (X3): every condition, and what justifies it
The rule is the brief's (as in X2). The liveness verdicts rest on exactly the conditions of `Fairness`, i.e. on weak fairness of each action of `FairNext`; every one is below or in the X2 table.

| Condition | Enabled when | Justification |
|---|---|---|
| X2's conditions on `Elect(n)`, `StepDown(n)`, `CheckQuorum(n)`, `Grant`, `Resend`, deliveries, storage, `ScheduleStep` | as in X2 | as in X2 (README "Fairness (X2)"). X3: `Elect` and `CheckQuorum` may also be enabled by `early[n]`, the node's own timer. |
| `WF(Join(n))` (was `WF(Join(n, q))`) | leader n, some node in its scope lagging, with n→q up | n's message over up links. C1.4 (P10 fix), C3.4 (new members). |
| `WF(\E x : Commit(l, x))` **(new)** | leader l, eligible member; a pending request reaches it over up links (direct or one hop); eligible majorities of old and new, connected to l both ways, promised to its term and caught up | l's own state and messages over up links (the forwarded request, round-trip agreements). C3.4. |
| `WF(\E m : LearnConfig(n, m))` **(new)** | some m that recorded the next commit has m→n up | a message over an up link. C3.4, C1.4. |
| `WF(\E m \in rcMsgs : RecvReconfig(m))` **(new)** | a request in flight to an up receiver | sent while its link was up, so delivered (failure model v2/v3 "Links"). C3.4(a). |
| `WF(\E a \in owed[x] : ReplyOp(x, a))` **(new)** | x up, owing a reply, x→op up | x's own state and an up link. C3.4. |

No condition requires hearing a peer across a link that is down. The duplicated deliveries (`StorageDecide(m, TRUE)`, `StorageRead(m, TRUE)`) are not fair, as before; a duplicate is enabled only when its fair twin is.

### Compiler, exporter, runner (mechanical propagation of format v5 and observe v5)
- **Compiler.** `processes` takes 1 to 6 lease nodes, a `config` subset (default all), at least one client, exactly one storage, and `operators` (default `[op]`); `lifetime` (default 1). It accepts `{cell: F3.1, reconfigure, to, id, operator}` (`to` a lease node, `grantor`, `non-grantor` or `non-member`; members are names, possibly not lease nodes), `{cell: F3.2, clock, step}` (step × lifetime must be whole ticks), `{cell: F3.3, restart, amnesia: true}` (only a crashed lease node; `restart: non-grantor` names the node `crash: non-grantor` crashed). It rejects reused request ids, unknown operators, selectors among members, crashing an operator. Triggers may name every new event; `ConfigCommitted` filters on epoch, members (as a set), request_id, decided; `ReconfigRefused` on reason; `ReconfigAck` on outcome; `Agree` and `Agreed` take no filter (in this model they occur in the step that counts them); `Fault` filters on cell, amnesia, or `<action>: <target>`. `MaxTerm` counts reconfigure, clock and amnesic restart steps as fault steps. It writes reach probes (`Reach_*.cfg`).
- **Exporter.** Identity is `(proc, inc, seq)`: a lease node's `inc` is its incarnation, any other process's the number of times it has restarted; `seq` starts at 0 in each incarnation and continues across a lease node's ordinary restart. Every initial member's first record is its epoch-0 `ConfigCommitted`. A grant step becomes `Agree` (by each counted node, with its incarnation), `Agreed` (by the decider, naming the `Agree`, `counted_toward` [epoch]) and `Grant` (with `config_epoch` and `inputs`); a commit step the same, with `counted_toward` [e], [e+1], both, or [] for re-admission evidence, then the decided `ConfigCommitted` with `readmits` and `inputs`. A learned commit names the decided record in `causes`. `ReconfigSend`, `ReconfigRequest`, `ReconfigRefused` (with inputs), `ReconfigAck` (naming the receiver's own record). The eight write and read events carry `grantor_term`; storage decisions carry `inputs`. Clock faults carry `clock` and `step` in units of L; amnesic restarts `restart` and `amnesia: true`. Partition fault records list operators among the processes.
- **Decision inputs.** Only the schema's fixed names are used: storage `token`, `ledger`, `stored_value`, `value` (writes); grants `agreed` (by ref), `members`, `config_epoch`, `grantor_term`, `last_token` (no ref: it is the leader's own count, adopted from its quorum, not a record); commits `agreed`, `old_members`, `old_epoch`, `request_id`, `requested_members`; refusals `request_id`, `requested_members`, `pending` (busy, by ref to the pending request's `ReconfigRequest`), `commit` (superseded, by ref to the receiver's record of the superseding epoch). No `clock` or `last_grant_at`: no decision reads a clock. No extra names.
- **Runner.** `run.sh` resolves any schedule in `testbed/schedules/`. `--all` runs the 59 shared schedules (P31 last), then the mutations, then the replay over every unmutated observe file. `--mutations`, `--mutation=P1,P2`, `--reach=P31,...`, `--replay`. Defaults: `/opt/tlaplus/tla2tools.jar` (override `TLA2TOOLS=`), Java 21, `TLC_WORKERS=8`, `TLC_HEAP=8g`. TLC output is streamed to `model/.work/<run>/*.out`.

### Interpretations (X3)
**New**
- **X3.1, the protocol and its abstraction.** As above ("The protocol followed", "Abstractions").
- **X3.2, the target epoch and "pending".** A request is recorded with the epoch after its receiver's current one as its target. "Until the receiver records ... a commit of any higher epoch" is read as: of an epoch at least the target. When the receiver records that epoch's commit, the request is its commit (if the commit names it) or is refused as `superseded` in the same step, with `epoch` the target; either way the receiver then owes the operator the outcome.
- **X3.3, an amnesic node's configuration.** It knows the deployment's epoch 0 but records nothing for it (contract v3); until it learns, it uses epoch 0 to target and forward a request. So a request sent to an amnesic node that has not learned epoch 1 targets epoch 1 (P33), and is superseded if epoch 1 is already committed.
- **X3.4, readmits.** The commit's `readmits` lists every recorded agreement of an incarnation above 0 by a node in the new membership, including one already re-admitted earlier. The contract's sentence is read with the replay's check.
- **X3.5, eligibility of votes.** An election counts only eligible members of the configuration it adopts. The contract defines eligibility for agreements; votes are the protocol's, and an amnesic vote is exactly what Paxos Made Live forbids.
- **X3.6, a removed node.** A node a commit removes need not learn of it; it hears the new leader (heartbeats reach every node whose link is up), so it does not disrupt it. A removed leader steps down at the commit.
- **X3.7, `non-grantor` and `non-member`.** `non-grantor` is any up lease node other than the grantor, members or not (format v2.1 A1 read literally under v5); `non-member` is any lease node outside the globally committed configuration when the trigger fires. The model explores every choice of both.
- **X3.8, messages to a crashed receiver.** A request sent to a crashed receiver is lost, and requests in flight to a node that crashes are lost with its inbox (as storage's inbox, interpretation 14). A pending request and owed replies are durable across an ordinary restart and lost on an amnesic one.
- **X3.9, `ReconfigAck`'s epoch.** The committed epoch for `committed`, the superseding epoch for `superseded`, null for `invalid` and `busy`.
- **X3.10, Agree and Agreed triggers.** They fire on the step that counts the agreement (P53: c1's grant step; P58: c2's grant step). "The change and c2's grant in progress together" (P58) is not explored.
- **X3.11, the reach of a check.** For each schedule the model's space must contain what the schedule needs; this is demonstrated, not argued, by reach probes (see "Reach").

**Extended**
- **3 (time abstract).** Clocks are offsets with an early-timer flag; still no waiting for expiry, now explicitly allowed by contract v3.
- **5 (grantor abstraction).** Quorums are eligible majorities of the newest configuration known; elections adopt configurations as they adopt tokens.
- **7 (grant retries)** and **FR.2.** Unchanged in behaviour; the `Grant` record now carries its configuration epoch and inputs.
- **14 (crash).** An amnesic restart loses everything durable; an ordinary restart keeps it, as before.
- **17 (C1.4's condition).** The majority is of eligible members of the globally committed configuration, more than half of whose members must be eligible, and no request may be pending at an up lease node.
- **20 (observe records).** `inc` on every record; v5's new records and `inputs`.
- **R2.2 (E1 in flight).** Extended to requests, pending requests and owed replies (format v5 E1).
- **R2.5 (`Join`).** One heartbeat joins every lagging follower in scope whose link is up.
- **X2.2 (voter stickiness).** A voter whose timer fired early (forward clock step) may vote although it hears a leader.
- **X2.3 (CheckQuorum).** It counts eligible members of the leader's current configuration; a removed or ineligible leader steps down; an early timer may fire it.
- **FR.1 (relay).** A receiver's request reaches the leader the same way, directly or through one lease node.
- **19 (witnesses).** Still the shortest trace that completes the schedule and quiesces; it is one sample. For example, P45's witness commits r1 without re-admitting n2 (the shortest way); the re-admitting commit is reachable (probe `readmit`).

**Contradicted**
- **12 (process names), "A schedule that is not exactly 3 lease nodes, 2 clients and 1 storage is rejected"**, and **TLC bounds, "Topology. Fixed at 3 lease nodes, 2 clients, 1 storage and 1 key"**: under format v5 a schedule names its lease nodes (up to six here), its initial configuration and its operators. Replaced by the compiler rules above. One key and one storage remain.
- **Model summary, "C1_1: tokens strictly increase along the grant sequence"**, and the comment on `C1_1`: contract v3 reads "previously" without a global order. The model's total order is still checked as `C1_1order`, whose violation alone would print `UNEXPLAINED` (it never did); `C1_1` is v3's three-part reading.
- **20, "`seq` is per process"**: under observe v5 it is per process and incarnation, from 0.
- **Model summary, "Grant: the leader issues token `ltok + 1` only when a majority that is still promised to its term confirms it"** and **5, "Election and grant quorums may be any majority subset"**: still true with "majority" meaning an eligible majority of the current configuration (contract v3 "Majority of a configuration"), not of three fixed nodes. Every subset is still explored.
- **Fairness (X2), "`WF(Join(n, q))`"**: replaced by `WF(Join(n))` (abstraction 3).
- **"How to run"**: "Java 11, `/home/tony/projects/tlaplus/tla2tools.jar`" and "all 13 schedules, then all 12 mutations" describe round 1; see "Runner" above.

[lines 133 to 336, "Mutations (X3)" and "Results (X3)", omitted by rule]
### Files (X3, in addition to "Files")
| File | What | derives |
|---|---|---|
| `PREDICTIONS-x3.md` | X3 predictions, amendment 1 (P49 re-placed), outcome | every clause and cell of X3 |
| `evidence/x3-run-all.txt` | the final `run.sh --all`: its stdout, then each run's statistics line | all |
| `evidence/x3-run-P31.txt` | P31's own run (stdout, statistics, TLC's summary) | C3.1, F3.1 |
| `evidence/x3-reach.txt` | `run.sh --reach` for all 59 schedules | reach |
| `observe/decision-replay.txt` | the replay over the 59 unmutated observe files | C3.5, C1.1, C3.1, C3.7, C3.8 |
| `observe/P43-mutation-replay.txt`, `P44-`, `P45-` | the replay on each C3.5 mutation's counterexample with the unmutated witness | C3.5 |
| `mutations/P49a/Lease.tla` | the superseded P49 break, kept as a record | C1.2, F3.1 |

### Observations (not judgements)
- `observe/provenance_check.py` keys records by `(proc, seq)`. Under observe v5, storage's `seq` starts again at 0 after a restart, in a new `inc`, so in P4, P13 and P16 that check finds an ack whose `answers` names an attempt it cannot reach, though the `(proc, inc, seq)` chain reaches it. The exporter's own self-check (the same question, with `inc`) found no problem in any run.
- **State counts of P1-P30, false-suspicion-v1 and H7-H10** changed from X2 although their behaviour did not: `lastEv` is no longer fingerprinted, internal steps emit nothing, and one heartbeat joins every lagging follower. The verdicts are unchanged.
- **Witnesses are one sample.** P45's commits r1 without re-admitting n2 (the shortest way; the re-admitting commit is reachable, probe `readmit`). P58's `{event: Agreed}` trigger fires on c2's grant step, so r1 is sent after c2's grant (X3.10). P61's r2 goes to n3 after r1 committed, and is refused `superseded` because n3 recorded it against epoch 0.
- **Old observe files.** Every observe file in `observe/` is from the final runs; files of X2's mutations that no longer exist were overwritten by this round's.

### Wall-clock
Started 2026-10-25 20:30 UTC (the inputs were committed 20:29 UTC); predictions committed 20:52; first adapted version 21:52; final `run.sh --all` 23:30 to 00:31; P31 alone 00:31 to 01:29 UTC. About five hours in all.


===== FILE: arm A impl/README.md, its X3 sections (line 1150 to the end) =====
## X3 adaptation — initial outcomes and semantic corrections

<!-- derives: C1.1, C3.1, C3.4, C3.7, C3.8, F3.1, F3.3 -->
Prerequisite predictions are committed at fe12a32 (OTS 795c1ce). Initial P1
seed 1 passes. Initial P45 panics when a retained leader sends a heartbeat with
commit 3 to the empty restarted node (last index 0); its partial trace is retained.
Initial P46 is UNEXPLAINED on seeds 1–3 (`cannot step as peer not found`), and
P61 is UNEXPLAINED on seeds 1–3 (pending request fails to quiesce). These outcomes
inform the next corrections; predictions are unchanged. F3.3 was misread by
allowing ordinary protocol heartbeat processing before snapshot recovery; recover
through a Raft snapshot before ordinary RPCs. F3.1/C3.4 forwarding was misread
as requiring a direct link to the leader: relay through other lease nodes.
Etcd's ErrStepPeerNotFound on late responses from a removed peer is a discarded
protocol message, not an operational fault. No correctness attribution to a model
or cross-artifact comparison is made; those divergences remain unexplained.

<!-- derives: C1.4, C3.7, F3.1 -->
Outcome-informed continuation: after the first corrections P45 and P61 pass all
three seeds, while P46 fails C1.4 on all three. A diagnostic sidecar shows all six
nodes have applied the leave-joint entry (7) and learned epoch 1, but removed n1
remains leader and its heartbeats prevent elections among n4–n6. The integration
omitted etcd's `StepDownOnRemoval` option; enable it to implement C1.4 after leader
removal. This is a named F3.1/C1.4 misreading, not schedule-specific tuning.
Decision replay of the three retained representative traces reports zero invalid
records and zero input conflicts. These are interim outcomes, not final scores.

<!-- derives: C1.1, C1.4, C3.5, C3.7, F1.3, F3.2, F3.3 -->
The first 59-schedule sweep records 21 UNEXPLAINED pause-window cells and three
compiler rejections (P48, P51, P54); raw receipts and traces are retained. The
compiler incorrectly required a concrete name before freezing `non-grantor` for
amnesia and omitted `amnesia` from Fault trigger filters (F3.3/R3). The lifetime
integration incorrectly equated the format's tick with one internal scheduler
substep: all replies take at least eight substeps, so a one-tick lease expired
before delivery. A deployment tick is now 40 internal substeps (the previous
one-lifetime duration), and emitted lifetime and clock readings use whole ticks.
Packet and action ordering within a tick remains deterministic. This restores
the existing F1.3 workload policy without changing L in any shared input.
The old global run-time wait is also contradicted by F3.2: grantor expiry waits
must use its own stepped clock and record clock/last_grant_at. Each node now does
that; the separate harness pause barrier enforces the run-time F1.3 duration.
These corrections are outcome-informed, and predictions are unchanged.

<!-- derives: C1.1, C1.4, C3.5, C3.7, F3.1, F3.2, F3.3 -->
The second baseline sweep passes all 177 seed cells. The first mutation sweep
kills 51/56 across all seeds: the clock mutations sometimes read a clock that
happens to preserve the outcome; P46's token-reset guard misses newly elected
nodes; R2 reaches the event bound before its progress horizon because v5 adds
agreement events. These are retained misses, not kills. Outcome-informed mutation
amendment: force three adjacent duplicate write deliveries in the C3.5 mutation
mode to exercise the omitted fine-grained clock input on both parities; this is
allowed network duplication, and the baseline is unchanged. Track the actual
highest agreed token (including its source Agree) rather than only own grants,
which also puts P46's reset back on the enforcing path. For R2, retain/retransmit
an already issued grant for the same request at its issuer (schema v4), instead
of continuously issuing fresh grants while the reply is lost. A new leader can
still issue a higher token. The liveness horizon and event bound are unchanged.
Two unit fixture failures reflect fixed membership and event-count assumptions;
they are extended with explicit membership and synthetic agreement evidence.

<!-- derives: C1.4, C2.2, C3.4, F1.1, F1.3, F2.2, F3.2 -->
The third unit run finds P30 seed 2's old mutation is bypassed when the reply's
local preparation ends after healing. Extend its wrong-value break to the normal
served-reply delivery path after the relevant link fault, keeping its lost-reply
break too (P29 similarly). No baseline behavior changes. Review also found that
progress certificates must wait for the schedule's last fault, rather than
certify a temporary pre-fault stable period (v3 L3). Compiler-known remaining
faults now gate both certificates. Under that meaning P10's mutation must allow
the intermediate grant before the final grantor crash, then suppress progress;
P12 must allow issuance to trigger resume, then break receipt of c2's reply, so
its failed requester is witnessed after the final resume. These mutation
replacements are outcome-informed; the expected clauses and horizons stay fixed.

<!-- derives: C1.4, F1.3, F3.1, F3.2, F3.3 -->
The second mutation sweep kills 52/56 across all seeds. P52–P54 suppressed the
initial grant before their last-fault triggers, so no after-last-fault duty was
witnessed. Their breaks now activate on a committed configuration, a clock step,
or an amnesic restart respectively. P12 broke relaying but left direct delivery
intact; its replacement drops that reply before either send. These are explicit
outcome-informed enforcing-path corrections, with all prior misses retained.

## X3 protocol, interpretation extensions and declared limits

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F1.1, F1.3, F2.1, F2.2, F3.1, F3.2, F3.3 -->
86. **Published protocol, extended membership.** Follow Ongaro and Ousterhout,
    *In Search of an Understandable Consensus Algorithm*, extended version,
    sections 5 and 6, <https://raft.github.io/raft.pdf>, through the existing
    pinned etcd Raft v3.6.0 library. `ConfChangeV2` explicitly enters joint
    consensus and explicitly leaves it; the leave entry must commit under both
    majorities before the contract epoch is decided. Initial membership is the
    deployment's `config`, not all existing nodes. Up to six lease nodes exist.
    Interpretations 26/81's fixed-voter assumption is contradicted; their
    initialized-before-start barrier remains. The contract epoch labels the final
    configuration, never the internal joint state. Removed leaders step down.
87. **Agreement adaptation.** A persisted full-proposal entry emits `Agree`.
    Each actual append acknowledgement carries the identities of entries its
    sender persisted. A decider emits `Agreed` only on receiving that metadata
    (its own durable append included), deduplicated by node/incarnation/proposal.
    Grants contain received agreement refs; configuration commits contain the
    leave-entry evidence, old/new memberships and request inputs. Log indices
    allocate tokens, including gaps for configuration/no-op entries. `last_token`
    names the highest locally agreed/granted token and its source Agree.
    This extends 7/15: v3 safety uses agreement order and epochs, not a required
    total causal grant order. The observer's previous-grant edge remains extra
    provenance, never allocation authority.
88. **Amnesia extends ordinary durability (4/81).** Ordinary restarts retain
    Raft state, issuer reply cache, configuration, pending receiver state and
    observer sequence. An amnesic restart discards them, increments incarnation,
    and starts empty. Recovery uses a connected leader's Raft snapshot; normal
    RPC processing waits for it. Until a later commit re-admits that incarnation,
    its vote responses and append acknowledgements cannot supply a Raft quorum.
    Its persisted agreements can be carried as uncounted re-admission evidence.
    A commit's readmits exactly lists these received new-incarnation agreements.
    Instrumentation identity is not recovered grant authority. Snapshot transfer
    and volatile recovery detection are harness adapters to the published Raft
    protocol; they do not reconstruct lost state from the observation log.
89. **Clock and workload interpretation.** Deployment L defaults to one tick;
    one tick contains 40 deterministic scheduler substeps. Emitted L and local
    clock readings are in ticks. F3.2 changes a process's clock offset by the
    exact whole number `step * L`; it does not move scheduler time. A grantor
    that has issued before waits using its own local clock, records clock and
    last_grant_at, and still uses Raft for token allocation. This contradicts
    13/80/83's fixed emitted lifetime/global expiry wait. Workload reads/writes
    use actual held tokens regardless of the client's expiry belief. The F1.3
    pause barrier remains in run time and permits resume only after L, regardless
    of any Grant trigger or clock step. No extra decision-input names are used.
90. **Reconstruction and scoring.** Storage records token, ledger, stored_value
    (initially null), and write value before updating. Equal-token writes replace
    the value, and reads never move the ledger. Every read/write event carries
    the original term. Identities and references include incarnation; client
    ordinary restarts increment their observer incarnation, lease ordinary
    restarts retain theirs. The supplied decision_replay.py checks each v5 trace;
    a separate aggregate run checks equal-input outcomes across all final traces.
    Bounded liveness certificates include receiver-local pending requests and
    are emitted only after all schedule faults have happened. Their topology,
    membership, eligibility and pending state are independently reconstructed
    from the raw trace. Invalid/busy are decided at receipt, in that order.
91. **Declared limits.** This remains bounded, deterministic, in-process Raft,
    not real disk/OS durability or exhaustive network exploration. Snapshot
    recovery waits for a live reachable leader. The implementation does not
    promise progress with an ineligible majority. Long schedules may exceed
    event/trigger/progress bounds; operator outcome delivery and grant receipt
    use harness scheduling, and elapsed horizon certificates remain trusted.
    Receiver amnesia or leadership loss after entering joint consensus but before
    leaving it may strand the harness's active request correlation: such shapes
    can fail C3.4 or C1.4 even when a later eligible majority is connected. The
    current adapter does not reclaim every abandoned joint transition. Request
    forwarding samples immediate hop-by-hop relays on up bidirectional links;
    it does not explore every directed multihop route or every hop delay.
    Repeated re-admission of one name with late acknowledgements from older
    incarnations can be conservatively blocked by the latest-incarnation gate.
    Uint64 bounds stop the affected issuer with Overflow before token, term,
    epoch or incarnation wrap; these enormous limits are not exercised by shared
    schedules. These are declared limitations, not excuses for a shared failure
    or proof of safety on all unseen schedules. No model artifact was read.


## X3 adapted-version result

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F1.1, F1.2, F1.3, F2.1, F2.2, F3.1, F3.2, F3.3 -->
[RESULTS-x3.md](RESULTS-x3.md) is the current result. All 59 shared schedules pass
seeds 1–3 at ten repetitions per seed: 1,770 PASS, no flaky cells, and one
canonical trace/sidecar variant per cell. All 56 mutations (24 new pairs, 30
retained pairs, R1/R2) fail their intended clauses at all three seeds: 168 kills.
Both required commands exit 0. Aggregate replay of all final baseline traces has
zero invalid records and zero equal-input conflicts. The three clock mutation
aggregates produce actual equal-input/different-outcome conflicts. Go tests and
vet pass. Raw traces, sidecars, adverse intermediate outcomes, commands and hashes
are committed under evidence-x3; none of the old records or predictions is rewritten.

The declared limitations in interpretations 91 and the result remain material:
interrupted joint transitions can strand request correlation and violate later
liveness; snapshot recovery needs a live leader; some directed multihop routes
and delay patterns are unexamined; bounded horizons and receipt certificates are
not unbounded proofs. Further compiler limits: a rest selector that resolves
only to crashed lease nodes is statically rejected for amnesic restart, and an
explicit invalid lifetime 0 is defaulted to 1. No shared schedule uses these
shapes. The final report does not claim general correctness beyond its evidence.

===== FILE: schedule H11.yaml =====
schedule: H11
derives: [C3.4, F1.2, F3.1, F3.2]
processes:
  lease: [n1, n2, n3]
  clients: [c1]
  storage: [s]
  operators: [op]
lifetime: 1
steps:
  # derives: C3.4, F1.2, F3.1, F3.2. The receiver is cut off from every other lease node. A valid request is recorded there, and only then a request that names storage. The invalid refusal has to happen while the valid request is still pending. After the links are restored, a one-lifetime clock step is the last fault, and the valid request has to commit.
  - {at: start, do: {cell: F1.2, partition: [[n1, op], [rest]]}}
  - {at: {event: Fault}, do: {cell: F3.1, reconfigure: [n1, n2, n3], to: n1, id: r1}}
  - {at: {event: ReconfigRequest}, do: {cell: F3.1, reconfigure: [n1, s], to: n1, id: r2}}
  - {at: {event: ReconfigRefused, reason: invalid}, do: {cell: F1.2, heal: true}}
  - {at: {event: Fault}, do: {cell: F3.2, clock: n1, step: 1}}
end: quiescent
bound: {events: 400}

===== FILE: arm A model: steward run, verdict lines for H11 =====
schedule=H11 # H11: 2674 distinct states, depth 18, max_term 12, 4 s, progress measure holds, observe -> model/observe/H11.jsonl
schedule=H11 PASS
schedule=H11 RUNNER-EXIT 0 SECONDS 4

===== FILE: arm A implementation: steward run, verdict lines for H11 (one line per repetition) =====
schedule=H11 UNEXPLAINED need 1..6 lease nodes, 2 clients, 1 storage schedule=H11
schedule=H11 RUNNER-EXIT 1 SECONDS 1
