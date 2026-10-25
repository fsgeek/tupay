# Packet: the X3 inputs


---

# Contract v3 (`contract/v3.md`)

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
- **Fencing.** A newer grant does not by itself stop an older holder: storage rejects the older holder only once a write or read with a newer token has been accepted or served. This is v1's meaning; F1.3 is the case it exists for.
- **C1.4 under v3.** "A majority of lease nodes" means a majority (as defined above) of the configuration with the highest committed epoch. The premise holds only after the last fault of the run (failure model, "After the last fault"), only if more than half of that configuration's members are eligible in it (so a majority of eligible agreements can exist), and only while no reconfiguration request is pending at any lease node that is up.

## Clauses (new in v3)
Ids C3.2, C3.3 and C3.6 were used by drafts 1 to 3 for a voting protocol written into this contract; they are retired and are not reused. C3.7 and C3.8 replace C3.2 and C3.3 at the level of evidence.
- **C3.1** Epoch e+1 is committed only after epoch e, and at most one configuration is committed for any epoch.
- **C3.7** (grant evidence) A grant is issued under exactly one configuration, the deciding node's current configuration when it decides, records that configuration's epoch, and is issued only after the deciding node has recorded eligible agreements to that grant from a majority of that configuration.
- **C3.8** (commit evidence) Configuration epoch e+1 is committed only after the deciding node has recorded eligible agreements to it from a majority of the committed configuration of epoch e and from a majority of the members of e+1; one agreement from a node in both counts toward both (`counted_toward: [e, e+1]`). The members of e+1 are exactly, as a set, those of the request whose id the commit names. An operator is told a reconfiguration succeeded only for the request whose id the commit names, and only after that commit.
- **C3.4** (liveness) Two duties. (a) The receiver refuses a request as `invalid` (its set is empty or names a process that is not a lease node) or else as `busy` (an earlier request is still pending at the same receiver; the earlier one is never refused on account of the later) when it records it, checking in that order, with no premise but that it stays up. (b) If, after the last fault, a request is pending at its receiver, more than half of the members of the configuration with the highest committed epoch are eligible in it, and the receiver, a majority of that configuration and a majority of the requested set stay up and connected to each other for long enough, the request is eventually committed or refused as `superseded` (the epoch it would occupy is already committed to another configuration, whether before or while it was pending; a receiver that learns this refuses, and the operator may send it again). In either case, if the operator also stays connected to the receiver, it is eventually told which (`ReconfigAck`). There is no other refusal reason: a receiver cannot give up on a request it is still holding.
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


---

# Failure model v3 (`failure-model/v3.md`)

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


---

# Schedule format (with addenda v3, v4, v5) (`testbed/schedule-format.md`)

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


---

# Observability schema (with addenda) (`observe/schema.md`)

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


---

# Pairs v4 (`tests/pairs-v4.md`)

# Paired tests v4: the shared (clause × cell) list for contract v3 under failure model v3

**DRAFT 5, not registered.** Drafted 2026-10-23 for X3; P44, P50 and P51 reworded after the second input review; draft 4 after the third: P34 to P39 and P55 to P57 retired with the clauses they derived from (C3.2, C3.3, C3.6), P58 to P63 added for C3.7 and C3.8, P33 and P40 to P42 aligned with the contract; draft 5 after the fourth: P40 to P42, P61 and P63 reworded. Self-contained: P1 to P30 from `pairs-v3.md` are restated with id and wording unchanged; P31 to P33, P40 to P54 and P58 to P63 are added. Pair ids P34 to P39 and P55 to P57 were used by drafts 1 to 3 and are retired, not reused. Every pair name is the derivation tag for both halves and both mutations.

**Which crossings are pairs, and why (registered with X3).** Every new clause (C3.1, C3.4, C3.5, C3.7, C3.8) crossed with every new cell (F3.1 to F3.3), and C1.1, C1.2 and C1.4 crossed with every new cell: 24 pairs. Not paired: C1.3, C2.1 and C2.2 crossed with F3.x, because a storage decision depends only on the token presented and the ledger, which membership does not touch, and a storage decision that consults a clock is caught by P44 (C3.5 under F3.2); and C3.x crossed with F1.x or F2.x on their own, because F3.1 schedules apply reconfiguration while those cells are in effect. The full cross would add 58 pairs (eleven clauses by eight cells, less the thirty existing); the steward judged that cost larger than what the further 34 would discriminate. Hold-out authors are told nothing beyond this file and may aim at what the cut leaves out, which tests it.

| Pair | Derives | What the pair checks |
|---|---|---|
| P1 | C1.1, F1.1 | Grantor nodes crash and restart; tokens still strictly increase across grantor incarnations. |
| P2 | C1.1, F1.2 | Grantor partitioned from its peers; two grantor incarnations may exist; tokens still strictly increase. |
| P3 | C1.1, F1.3 | Holder paused past lifetime; the next grant's token exceeds the paused holder's. |
| P4 | C1.2, F1.1 | Storage crashes and restarts; a write with a stale token is still rejected afterwards. |
| P5 | C1.2, F1.2 | Holder cut off from grantor but connected to storage; after a new grant is accepted, the old holder's writes are rejected. |
| P6 | C1.2, F1.3 | Paused holder resumes and writes; rejected if a newer token has been accepted. |
| P7 | C1.3, F1.1 | Client or storage crashes between accept and ack; no client is told success for a write storage did not accept. |
| P8 | C1.3, F1.2 | Ack lost in a partition; the client is not told success. |
| P9 | C1.3, F1.3 | Paused client receives a late ack; it refers to a write storage actually accepted. |
| P10 | C1.4, F1.1 | A minority of lease nodes crash; a requester still eventually gets a grant. |
| P11 | C1.4, F1.2 | Partition heals; a requester on the majority side eventually gets a grant. |
| P12 | C1.4, F1.3 | Holder paused past lifetime; another requester eventually gets a grant. |
| P13 | C2.1, F1.1 | Storage crashes and restarts after accepting a newer token; a read with a stale token is still rejected afterwards. |
| P14 | C2.1, F1.2 | Holder cut off from the grantor but connected to storage; after a newer token's write is accepted, the old holder's read is rejected. |
| P15 | C2.1, F1.3 | Paused holder resumes and reads; rejected if a newer token has been accepted. |
| P16 | C2.2, F1.1 | Storage crashes between serving a read and the ack, or the client crashes after the serve; no client is given a value storage did not serve, and the value given is the one served. |
| P17 | C2.2, F1.2 | Read ack lost in a partition; the client is not given a value; a later served read's value matches storage. |
| P18 | C2.2, F1.3 | Paused client receives a late read ack; it refers to a read storage served and carries the value served. |
| P19 | C1.1, F2.1 | After the first grant, the link between the grantor and one follower is cut both ways; the cut-off follower may start elections through the node both still reach; every later grant's token exceeds every earlier one. |
| P20 | C1.1, F2.2 | The grantor can send to the other lease nodes but not hear them; whether it keeps acting or a new grantor emerges, tokens still strictly increase. |
| P21 | C1.2, F2.1 | The grantor is cut from the other lease nodes only, still reaching both clients and storage (not a bipartition); after the new holder's write is accepted, the old holder's write is rejected. |
| P22 | C1.2, F2.2 | The old holder can send to everyone but hears nothing from the lease nodes; after the new holder's write is accepted, the old holder's write is rejected. |
| P23 | C1.3, F2.1 | Only the holder–storage link is cut, after storage accepts; the client is not told success for that write or a later one that never arrives. |
| P24 | C1.3, F2.2 | Storage hears the holder but its replies to the holder are lost; writes may be accepted, and the client is not told success for any of them. |
| P25 | C1.4, F2.1 | After the first grant, the link between the grantor and one follower is cut both ways and stays cut; the grantor, the other follower, storage and a requester stay connected; the requester eventually gets a grant. |
| P26 | C1.4, F2.2 | After the first grant, the grantor stops hearing the other lease nodes but they still hear it; the two followers, storage and a requester stay connected; the requester eventually gets a grant. |
| P27 | C2.1, F2.1 | As P21, with a read: the old holder's read after the new holder's accepted write is rejected. |
| P28 | C2.1, F2.2 | As P22, with a read: the old holder, hearing nothing from the lease nodes, reads after the new holder's accepted write and is rejected. |
| P29 | C2.2, F2.1 | Only the holder–storage link is cut, after storage serves a read; the client is not given a value; after the heal a served read's value matches storage. |
| P30 | C2.2, F2.2 | Storage hears the holder's read but its reply is lost; the client is not given a value; after the heal a served read's value matches storage. |
| P31 | C3.1, F3.1 | Two reconfiguration requests naming different member sets arrive at different members before either is answered; committed epochs strictly increase and no epoch has two configurations. |
| P32 | C3.1, F3.2 | The grantor's clock jumps back by several lifetimes while a reconfiguration is in progress; committed epochs strictly increase and no epoch has two configurations. |
| P33 | C3.1, F3.3 | After a configuration is committed, a member that agreed to it crashes and restarts amnesic, and a reconfiguration request is sent to it; at most one configuration is committed for any epoch, and epochs are committed in order. |
| P40 | C3.4, F3.1 | A reconfiguration adds two nodes and removes one while a follower of the old configuration, not the receiver, is partitioned away; the receiver and majorities of both configurations stay connected; the request is eventually committed or refused as `superseded`. |
| P41 | C3.4, F3.2 | Every lease node's clock jumps back once during a reconfiguration; the receiver and majorities of both configurations stay connected; the request is eventually committed or refused as `superseded`. |
| P42 | C3.4, F3.3 | A minority member restarts amnesic during a reconfiguration that does not re-admit it; the receiver and majorities of both configurations stay connected; the request is eventually committed or refused as `superseded`. |
| P43 | C3.5, F3.1 | Reconfiguration under a partial partition; every recorded decision (grant, storage decision, configuration commit) is re-derivable from its recorded inputs. |
| P44 | C3.5, F3.2 | The grantor's clock jumps around a grant's expiry, back then forward, while another client requests; every recorded decision is a function of its recorded inputs, clock readings included. |
| P45 | C3.5, F3.3 | An amnesic restart followed by its re-admission by reconfiguration; every recorded decision is re-derivable from its recorded inputs. |
| P46 | C1.1, F3.1 | The grantor is removed and replaced by nodes that were never members; the first grant under the new configuration carries a token greater than every token granted under the old one. |
| P47 | C1.1, F3.2 | The grantor's clock jumps back by several lifetimes between two grants; tokens still strictly increase. |
| P48 | C1.1, F3.3 | A minority member restarts amnesic and the grantor then crashes; tokens granted afterwards still exceed every earlier token. |
| P49 | C1.2, F3.1 | A holder of a grant under the old configuration is cut off from the lease nodes but not from storage while a reconfiguration commits and a new holder is granted and writes; the old holder's later write is rejected. |
| P50 | C1.2, F3.2 | A holder's clock jumps back by several lifetimes; after a newer holder's write is accepted, the old holder's write is rejected (what the old holder believes about expiry decides nothing). |
| P51 | C1.2, F3.3 | After an amnesic restart of a minority member, a new holder is granted and its write is accepted; then the previous holder's write is rejected. |
| P52 | C1.4, F3.1 | After a reconfiguration that removes the grantor is committed and answered, a majority of the new configuration, storage and a requester stay connected; the requester eventually gets a grant. |
| P53 | C1.4, F3.2 | After clock jumps on every lease node, a majority, storage and a requester stay connected; the requester eventually gets a grant. |
| P54 | C1.4, F3.3 | After a minority member restarts amnesic, a majority, storage and a requester stay connected; the requester eventually gets a grant. |
| P58 | C3.7, F3.1 | A reconfiguration removes the grantor, sent to the grantor itself; every grant is issued under its decider's current configuration and counted by eligible agreements from a majority of the configuration it names. |
| P59 | C3.7, F3.2 | A node removed by a committed reconfiguration stays up and its clock jumps forward past every lifetime; every grant is counted by eligible agreements from a majority of the configuration it names, and every grant after the commit carries a token greater than every earlier one. |
| P60 | C3.7, F3.3 | A configuration change is committed; one member that agreed to it restarts amnesic and is not re-admitted; no grant counts an agreement of its new incarnation. |
| P61 | C3.8, F3.1 | A reconfiguration request is sent to a non-member, which passes it to a member and stays the receiver; any commit is counted by eligible majorities of the old and the new configuration, and the operator is told success only for the request a commit names. |
| P62 | C3.8, F3.2 | The clock of the node that received a reconfiguration request jumps forward before the commit; the operator is not told success before the commit, and the commit is counted by majorities of both configurations. |
| P63 | C3.8, F3.3 | The node that received a reconfiguration request crashes before answering and restarts amnesic; the operator is told success only for a committed configuration; a later commit that lists the node names it in `readmits` exactly when the decider recorded its new incarnation's agreement to that commit (recorded, not counted toward it). |

## Mutation pairs
Each pair has a deliberately broken model and a deliberately broken implementation on the clause's enforcing path, named before running. P1 to P18's mutations are unchanged unless an author finds that one no longer sits on the enforcing path, in which case it is re-placed and the change is recorded. For P25 and P26 (liveness), the mutation must break the mechanism by which the artifact makes progress under that cell, so that the mutated artifact fails C1.4 on the pair's shared schedule; if the unmutated artifact already fails, say so: the pair then has no working half to mutate, and that is a finding, not a gap to paper over.
For P31 to P63 the same rule applies. For C3.5 pairs, the mutation makes one decision consult an input it does not record (on the model side, a decision guarded by a variable absent from the emitted record; on the implementation side, an unrecorded clock read or map iteration), and the decision-replay check must report it.

## Changelog
- v4 (2026-10-23, draft 4): P31 to P33, P40 to P54, P58 to P63 (P34 to P39 and P55 to P57 retired in draft 4); P1 to P30 restated. Reason: X3, contract v3 and failure model v3.
- v3 (2026-10-21): P19 to P30; P1 to P18 restated. Reason: X2, failure model v2.


---

# Example schedule (P58) (`testbed/schedules/P58.yaml`)

schedule: P58
derives: [C3.7, F3.1]
processes:
  lease: [n1, n2, n3, n4, n5, n6]
  config: [n1, n2, n3]
  clients: [c1, c2]
  storage: [s]
steps:
  # derives: P58 (C3.7, F3.1). After c1's grant, c2 requests; as soon as an agreement to c2's grant is counted (owed by C3.7), a request replacing every old member, the grantor among them, is sent to the grantor itself (the node that issued c1's grant), so the change and c2's grant are in progress together; c1 requests again after the commit; every grant is issued under its decider's current configuration and counted by eligible agreements from a majority of the configuration it names.
  - {at: start, do: {request: c1}}
  - {at: {event: Grant, client: c1}, do: {request: c2}}
  - {at: {event: Agreed}, do: {cell: F3.1, reconfigure: [n4, n5, n6], to: grantor, id: r1}}
  - {at: {event: ConfigCommitted, request_id: r1, decided: true}, do: {request: c1}}
end: quiescent
bound: {events: 400}
