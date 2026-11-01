# Rating task: measure 6 (propagation or conceptual), one rater, independent

You are rating changes an author made to an existing artifact when its inputs changed (a service contract and a
failure model moved from version 2 to version 3; the full version 3 inputs are below). Each **unit** is one file
as changed by one commit. Commit messages are withheld.

**The ruling you apply (fixed before any rating):** a unit is **conceptual** (C) iff it makes a choice the inputs
leave open: choosing between behaviours the inputs permit, or reading an ambiguous input. Implementing an
unambiguous prescription of the inputs, however much code it takes, is **propagation** (P). A unit that does
both is C. Judge from the diff and the inputs only; code comments are the author's and may be wrong.

Answer with one JSON object and nothing after it:
{"ratings": [{"unit": "U01", "label": "C" or "P", "reason": "one or two sentences naming the open choice, or the prescription implemented"}, ...]}
Every unit below gets exactly one entry.

# The inputs the author worked from (as in its checkout)
## `contract/v3.md`
````
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

````
## `failure-model/v3.md`
````
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

````
## `testbed/schedule-format.md`
````
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

````
## `observe/schema.md`
````
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

````
## `tests/pairs-v4.md`
````
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

````
# Units
## U01: `model/Lease.tla`
````diff
diff --git a/model/Lease.tla b/model/Lease.tla
index f69b542..41819cc 100644
--- a/model/Lease.tla
+++ b/model/Lease.tla
@@ -1,21 +1,32 @@
 -------------------------------- MODULE Lease --------------------------------
-\* derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2
+\* derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F1.1, F1.2, F1.3, F2.1, F2.2, F3.1, F3.2, F3.3
 \* (contract v2 / X1: reads are fenced; read elements are tagged C2.x)
 \* (failure model v2 / X2: connectivity is a set of directed links; elements that represent
 \*  connectivity are tagged F2.1, F2.2 as well as the v1 cell they still derive from)
-\* Lease service with fencing tokens: 3 lease nodes (the grantor), 2 clients,
-\* one storage service, one key. The grantor is abstract: a leader per term,
-\* elected by a majority; a grant is issued only with a majority's confirmation.
-\* The environment (F1.1-F1.3, F2.1, F2.2) and the workload are driven by a compiled
+\* (contract v3, failure model v3 / X3: the grantor's membership changes. Lease nodes are any
+\*  number the schedule names (up to six); configurations have epochs and change by a request
+\*  from an operator; clocks step; a lease node may restart with no durable state. Elements
+\*  the change invalidated (fixed lease nodes, the grant decision, restart keeping durable
+\*  state) now also derive from C3.x and F3.x and say so; README "X3 adapt arm".)
+\* Lease service with fencing tokens: lease nodes (the grantor), clients, one storage
+\* process, operators, one key. The grantor is abstract Raft with joint consensus
+\* (README, X3 "Protocol"): a leader per term, elected by an eligible majority of the newest
+\* configuration its voters know; a grant or a configuration commit is decided in one step
+\* together with the eligible agreements it counts.
+\* The environment (F1.1-F1.3, F2.1, F2.2, F3.1-F3.3) and the workload are driven by a compiled
 \* schedule: Steps is a sequence of step records, applied in order.
 EXTENDS Integers, Sequences, FiniteSets, TLC
 
 CONSTANTS
-    Nodes,      \* derives: C1.1, C1.4 -- the three lease nodes
-    Clients,    \* derives: C1.2, C1.3, C1.4 -- the two clients
+    Nodes,      \* derives: C1.1, C1.4, C3.7, F3.1 -- the lease nodes (members or not; X3: any number up to six)
+    Init0,      \* derives: C3.1, C3.7, C3.8, F3.1; format v5 `config` -- members of the initial configuration (epoch 0)
+    Clients,    \* derives: C1.2, C1.3, C1.4 -- the clients
     Store,      \* derives: C1.2, C1.3 -- the storage service (one process)
+    Ops,        \* derives: C3.4, C3.8, F3.1; format v5 `operators` -- the operators
     Key,        \* derives: C1.1, C1.2 -- the single protected key
-    Lifetime,   \* derives: C1.1, F1.3 -- abstract grant lifetime, reported on Grant only
+    Lifetime,   \* derives: C1.1, F1.3, F3.2 -- L in ticks (format v5 `lifetime`), reported on Grant only
+    ReqSets,    \* derives: C3.8 -- request id -> the set of names it requests (from the schedule)
+    Receivers,  \* derives: C3.4 -- lease nodes that may receive a request (bounds the C3.4 quantifier)
     Steps,      \* derives: F1.1, F1.2, F1.3 -- compiled schedule steps
     EndTrig,    \* derives: F1.1, F1.2, F1.3 -- compiled end trigger
     MaxTerm,    \* derives: C1.1, C1.4 -- bound on grantor terms (state-space bound)
@@ -29,8 +40,8 @@ VARIABLES
                 \* down: <<p, q>> \in down means p->q is down. Empty when healed. Replaces v1's
                 \* sideA, which could only express a bipartition (README, X2).
     \* --- grantor (derives: C1.1, C1.4)
-    promised,   \* derives: C1.1, F1.1 -- durable: highest term node n has voted for
-    maxTok,     \* derives: C1.1, F1.1 -- durable: highest token node n has confirmed
+    promised,   \* derives: C1.1, F1.1, F3.3 -- durable (lost on amnesia): highest term node n has voted for
+    maxTok,     \* derives: C1.1, F1.1, F3.3 -- durable (lost on amnesia): highest token node n has agreed to
     leader,     \* derives: C1.1, C1.4 -- volatile: n believes it is the grantor
     term,       \* derives: C1.1 -- volatile: the term n leads (meaningful when leader[n])
     ltok,       \* derives: C1.1 -- volatile: leader's last issued token
@@ -52,40 +63,77 @@ VARIABLES
     stval,      \* derives: C1.2 -- durable key value
     toAck,      \* derives: C1.3, F1.1 -- volatile: decided writes whose ack is not yet sent
     \* --- history (ghost) variables used only by invariants and the exporter
-    grants,     \* derives: C1.1 -- sequence of every grant issued
+    grants,     \* derives: C1.1, C3.5, C3.7 -- sequence of every grant issued, with its recorded inputs
     \* --- routing fix (derives: C1.1, C1.4, F2.1, F2.2; format v4 L3; observe v4 "Grants and retransmission")
     rq,         \* derives: C1.4 -- rq[c]: number of requests c has made (identifies the current request)
     issued,     \* derives: C1.1, C1.4, F2.2 -- grants each leader issued, [n, c, r, t, g]: leader n in
                 \* term g answered c's request r with token t. Volatile in a real node, but keyed by
                 \* term, and a node never leads the same term twice, so its loss on crash is not modelled
-    decisions,  \* derives: C1.2, C1.3 -- sequence of every storage decision
+    decisions,  \* derives: C1.2, C1.3, C3.5 -- sequence of every storage decision
     told,       \* derives: C1.3 -- set of writes clients were told succeeded
     \* --- schedule driver (derives: F1.1, F1.2, F1.3)
     pc,         \* derives: F1.1, F1.2, F1.3 -- index of the next schedule step
     fired,      \* derives: F1.1, F1.2, F1.3 -- trigger of step pc has held since step pc-1
     trigG,      \* derives: F1.2, F1.3 -- most recent grant at trigger time (resolves grantor/holder)
     trigNG,     \* derives: F1.1; format v2.1 A1 -- lease nodes other than grantor up at trigger time
+    trigNM,     \* derives: F3.1; format v5 R1 -- lease nodes outside the globally committed configuration at trigger time
     ngDown,     \* derives: F1.1; format v2.2 A1, v2.1 A1 -- node crashed by the most recent `crash: non-grantor`
-    lastEv,     \* derives: C1.1, C1.2, C1.3, C2.1, C2.2 -- the event emitted by the last step (for the exporter)
+    lastEv,     \* derives: C1.1, C1.2, C1.3, C2.1, C2.2, C3.5 -- the events the last step emitted, a sequence
+                \* (X3: one step may emit several, e.g. a grant with its agreements; README X3)
     \* --- reads (contract v2; derives: C2.1, C2.2)
     readMsgs,   \* derives: C2.1, F1.2 -- reads in flight, client -> storage
     rToAck,     \* derives: C2.2, F1.1 -- volatile: decided reads whose ack is not yet sent
     rAckMsgs,   \* derives: C2.2, F1.2 -- read acks in flight, storage -> client
     awaitingR,  \* derives: C2.2 -- reads c has sent and not yet had acked
-    rdecisions, \* derives: C2.1, C2.2 -- history: every storage read decision
-    given       \* derives: C2.2 -- history: every value a client was given
-
-\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -- all state variables
+    rdecisions, \* derives: C2.1, C2.2, C3.5 -- history: every storage read decision
+    given,      \* derives: C2.2 -- history: every value a client was given
+    \* --- configuration locus (contract v3, failure model v3; derives: C3.1, C3.4, C3.7, C3.8, F3.1, F3.3)
+    inc,        \* derives: C3.7, C3.8, F3.3 -- inc[n]: n's incarnation (+1 at each amnesic restart)
+    cfg,        \* derives: C3.1, C3.7, F3.1, F3.3 -- cfg[n]: the committed configurations n has recorded,
+                \* by epoch (cfg[n][e+1] is epoch e); durable, lost on amnesia (then only the
+                \* deployment's epoch 0, unrecorded)
+    jprop,      \* derives: C3.1, C3.8, F3.1, F3.3 -- jprop[n]: a configuration n agreed to and has not yet
+                \* recorded as committed (Raft's C_old,new entry in its log); durable, lost on amnesia
+    pend,       \* derives: C3.4, F3.1 -- pend[x]: the request pending at receiver x; durable, lost on amnesia
+    owed,       \* derives: C3.4, C3.8 -- owed[x]: outcomes x owes an operator; durable, lost on amnesia
+    rcMsgs,     \* derives: C3.4, F3.1 -- reconfiguration requests in flight, operator -> receiver
+    opMsgs,     \* derives: C3.4, C3.8 -- replies in flight, receiver -> operator (X3: empty in this model, a reply
+                \* is received in the step it is sent: ReplyOp; kept for the frame and for Owes)
+    commits,    \* derives: C3.1, C3.5, C3.8 -- history: every decided commit, with its recorded inputs
+    refusals,   \* derives: C3.4, C3.5 -- history: every refusal, with its recorded inputs
+    opTold,     \* derives: C3.8 -- history: every outcome an operator was told
+    \* --- clocks and agreement history (derives: C1.1, F3.2)
+    off,        \* derives: F3.2 -- off[p]: p's clock reading minus run time, in ticks (environment state;
+                \* changed only by clock steps; read by no decision of the unmutated model)
+    early,      \* derives: C1.4, F3.2 -- early[n]: a forward clock step fired n's timers before they would
+                \* have fired in run time (an election or quorum timeout), until n acts on it
+    agreeLog    \* derives: C1.1 -- history: agreeLog[n], n's counted grant agreements in its own order
+
+\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, C3.x, F3.x -- all state variables
 vars == <<up, paused, down, promised, maxTok, leader, term, ltok, reqs,
           pending, tok, myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups,
-          highest, stval, toAck, grants, rq, issued, decisions, told, pc, fired, trigG, trigNG, ngDown, lastEv,
-          readMsgs, rToAck, rAckMsgs, awaitingR, rdecisions, given>>
+          highest, stval, toAck, grants, rq, issued, decisions, told, pc, fired, trigG, trigNG, trigNM, ngDown, lastEv,
+          readMsgs, rToAck, rAckMsgs, awaitingR, rdecisions, given,
+          inc, cfg, jprop, pend, owed, rcMsgs, opMsgs, commits, refusals, opTold, off, early, agreeLog>>
+
+\* derives: C1.1, C1.2, C1.3, C3.x (state-space bound; README X3 "Bounds") -- the fingerprinted view: every
+\* variable but lastEv. lastEv is output only (no action reads it unprimed; triggers are matched on
+\* lastEv' in the step that emits it), so two states that differ only in it have the same futures.
+View == <<up, paused, down, promised, maxTok, leader, term, ltok, reqs,
+          pending, tok, myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups,
+          highest, stval, toAck, grants, rq, issued, decisions, told, pc, fired, trigG, trigNG, trigNM, ngDown,
+          readMsgs, rToAck, rAckMsgs, awaitingR, rdecisions, given,
+          inc, cfg, jprop, pend, owed, rcMsgs, opMsgs, commits, refusals, opTold, off, early, agreeLog>>
 
 \* derives: C2.1, C2.2 -- the read variables, for UNCHANGED in actions that do not touch reads
 rvars == <<readMsgs, rToAck, rAckMsgs, awaitingR, rdecisions, given>>
+\* derives: C3.1, C3.4, C3.7, C3.8, F3.1, F3.3 -- the configuration locus, for UNCHANGED in actions that do not touch it
+kvars == <<inc, cfg, jprop, pend, owed, rcMsgs, opMsgs, commits, refusals, opTold>>
+\* derives: C1.1, F3.2 -- clocks and the agreement history
+xvars == <<off, early, agreeLog>>
 
-\* derives: F1.1, F1.2 -- every process
-Procs == Nodes \cup Clients \cup {Store}
+\* derives: F1.1, F1.2, F3.1 -- every process (X3: operators are processes; their links obey F1.2, F2.x)
+Procs == Nodes \cup Clients \cup {Store} \cup Ops
 
 \* derives: C1.2, F1.3 -- "no token"
 NoTok == [t |-> 0, g |-> 0]
@@ -104,8 +152,10 @@ Conn(p, q) == Link(p, q) /\ Link(q, p)
 \* derives: F2.1; format v4 cut -- each listed link in both directions
 BothWays(L) == L \cup {<<x[2], x[1]>> : x \in L}
 
-\* derives: C1.1, C1.4 -- majority of lease nodes
-Majority(Q) == 2 * Cardinality(Q) > Cardinality(Nodes)
+\* derives: C1.1, C1.4, C3.7, C3.8 (contract v3 "Majority of a configuration") -- Q holds more than half
+\* of the members M; the denominator is the whole membership. (X3: replaces v1's Majority(Q), which
+\* counted against the three fixed lease nodes; README X3.)
+MajOf(Q, M) == 2 * Cardinality(Q \cap M) > Cardinality(M)
 
 \* derives: C1.1, F1.2, F1.3 -- most recent Grant ("grantor" = its node, "holder" = its client)
 LastGrant == IF grants = <<>> THEN [node |-> "none", client |-> "none"]
@@ -114,35 +164,109 @@ LastGrant == IF grants = <<>> THEN [node |-> "none", client |-> "none"]
 \* derives: C1.1 -- highest token ever granted
 MaxGranted == Max({grants[i].token : i \in 1..Len(grants)})
 
+\* ---------------------------------------------------------------------------
+\* Configurations (contract v3; derives: C3.1, C3.7, C3.8, F3.1, F3.3)
+\* A configuration record: epoch, members, request id, the [node, incarnation] pairs its commit
+\* re-admits, and its decider.
+\* derives: C3.1, F3.1 -- the initial configuration, committed by the deployment
+Init0Rec == [ep |-> 0, mem |-> Init0, rid |-> "none", rdm |-> {}, by |-> "none"]
+\* derives: C3.1, F3.3 -- "no configuration" (an empty jprop slot)
+NoConf == [ep |-> -1, mem |-> {}, rid |-> "none", rdm |-> {}, by |-> "none"]
+\* derives: C3.4 -- "no pending request"
+NoPend == [rid |-> "none", mem |-> {}, op |-> "none", tgt |-> -1]
+
+\* derives: C3.7, F3.1 -- n's current configuration: the committed one with the highest epoch it has recorded
+Cur(n) == cfg[n][Len(cfg[n])]
+\* derives: C3.7, F3.1
+CurEp(n) == Len(cfg[n]) - 1
+\* derives: C3.7, C3.8, F3.3 -- the incarnations re-admitted by the commits in history H
+RdmOf(H) == UNION {H[i].rdm : i \in 1..Len(H)}
+\* derives: C3.7, C3.8, F3.3 (contract v3 "Eligible agreement") -- q's current incarnation may count in a
+\* configuration with members M, given the re-admissions R known: q is a member, and its incarnation
+\* is 0 or re-admitted
+EligIn(q, M, R) == q \in M /\ (inc[q] = 0 \/ <<q, inc[q]>> \in R)
+\* derives: C3.7, F3.3 -- q may count in n's current configuration, as n knows it
+Elig(q, n) == EligIn(q, Cur(n).mem, RdmOf(cfg[n]))
+
+\* derives: C3.1, C1.1, F3.1, F3.3 -- the configuration history a leader elected by Q adopts: the longest
+\* history in Q, extended by a configuration some voter agreed to for the next epoch. (Every
+\* agreement to a configuration in this model was counted in the step that decided it, so such a
+\* proposal is committed; the leader records it as learned. Raft: the leader's log holds the
+\* C_old,new entry, Leader Completeness; README X3 "adaptations".)
+Adopt(Q) ==
+    LET l == CHOOSE q \in Q : \A p \in Q : Len(cfg[p]) <= Len(cfg[q])
+        H == cfg[l]
+        J == {q \in Q : jprop[q].ep = Len(H)} IN
+    IF J = {} THEN H ELSE Append(H, jprop[CHOOSE q \in J : TRUE])
+
+\* derives: C3.1, C3.4, C3.8 -- the globally committed configuration (format v5 L3): the decided commit
+\* with the highest epoch, or epoch 0 before any
+GLatest == IF commits = <<>> THEN Init0Rec
+           ELSE commits[CHOOSE i \in 1..Len(commits) :
+                          \A j \in 1..Len(commits) : commits[j].rec.ep <= commits[i].rec.ep].rec
+\* derives: C3.7, C3.8, F3.3 -- incarnations re-admitted by decided commits of epoch <= e, other than commit x
+GRdm(e, x) == UNION {commits[i].rec.rdm : i \in {j \in 1..Len(commits) : commits[j].rec.ep <= e /\ j # x}}
+\* derives: C1.4, C3.4, F3.3 -- q is eligible in the globally committed configuration (its latest incarnation)
+GElig(q) == EligIn(q, GLatest.mem, GRdm(GLatest.ep, 0))
+\* derives: C3.7, C3.8 -- the committed configuration of epoch e (NoConf if none)
+GCfgAt(e) == IF e = 0 THEN Init0Rec
+             ELSE IF \E i \in 1..Len(commits) : commits[i].rec.ep = e
+                  THEN commits[CHOOSE i \in 1..Len(commits) : commits[i].rec.ep = e].rec
+                  ELSE NoConf
+\* derives: C3.4, F3.1; format v5 R1 -- lease nodes outside the globally committed configuration
+NonMembers == Nodes \ GLatest.mem
+
 \* ---------------------------------------------------------------------------
 \* Schedule triggers
 \* derives: F1.1, F1.2, F1.3
 Trig(i) == IF i <= Len(Steps) THEN Steps[i].trig ELSE EndTrig
 \* derives: F1.1, F1.2, F1.3
 IsStart(T) == T.event = "start"
-\* derives: F1.1, F1.2, F1.3; format v2.1 T1 -- an event matches a trigger: same event and every
-\* filter field equal. Only events emitted while the trigger is armed are ever offered to it
-\* (Emit and ScheduleStep), which is T1's "matches only events emitted after it was armed".
-\* `quiescent` (E1) is a state predicate, never matched by an event.
-Matches(T, e) == /\ T.event \notin {"start", "quiescent"}
-                 /\ e.event = T.event
-                 /\ \A f \in (DOMAIN T) \ {"event"} : f \in DOMAIN e /\ e[f] = T[f]
+\* derives: F1.1, F1.2, F1.3; format v2.1 T1 -- every filter field of trigger T equals record r's
+FOK(T, r) == \A f \in (DOMAIN T) \ {"event"} : f \in DOMAIN r /\ r[f] = T[f]
+\* derives: F1.1, F1.2, F1.3, F3.1; format v2.1 T1, v5 -- an event the model emits matches a trigger.
+\* X3: a decided commit (`Commit`) and a learned one (`Learn`) are the schema's ConfigCommitted with
+\* decided true and false; a refusal is ReconfigRefused; a grant or commit step carries the Agree
+\* and Agreed records of the agreements it counted.
+Match1(T, e) ==
+    \/ /\ T.event \notin {"ConfigCommitted", "ReconfigRefused", "Agree", "Agreed"}
+       /\ e.event = T.event /\ FOK(T, e)
+    \/ /\ T.event = "ConfigCommitted" /\ e.event = "Commit"
+       /\ FOK(T, [epoch |-> e.rec.ep, members |-> e.rec.mem, request_id |-> e.rec.rid,
+                  decided |-> TRUE, node |-> e.node])
+    \/ /\ T.event = "ConfigCommitted" /\ e.event = "Learn"
+       /\ \E i \in 1..Len(e.recs) :
+            FOK(T, [epoch |-> e.recs[i].ep, members |-> e.recs[i].mem, request_id |-> e.recs[i].rid,
+                    decided |-> FALSE, node |-> e.node])
+    \/ /\ T.event = "ReconfigRefused" /\ e.event = "Refused" /\ FOK(T, e)
+    \/ /\ T.event \in {"Agree", "Agreed"} /\ e.event \in {"Grant", "Commit"}
+\* derives: F1.1, F1.2, F1.3; format v2.1 T1 -- some event of the sequence evs matches trigger T. Only
+\* events emitted while the trigger is armed are ever offered to it (Emit and ScheduleStep), which is
+\* T1's "matches only events emitted after it was armed". `quiescent` (E1) is a state predicate.
+Matches(T, evs) == /\ T.event \notin {"start", "quiescent"}
+                   /\ \E i \in 1..Len(evs) : Match1(T, evs[i])
 
 \* derives: C1.1, C1.2, C1.3, F1.1, F1.2, F1.3
-\* Protocol step emitting event e: record it, and advance the current trigger.
-\* Must be the last conjunct of an action (uses grants').
-Emit(e) == /\ lastEv' = e
-           /\ fired' = (fired \/ Matches(Trig(pc), e))
-           /\ trigG' = IF ~fired /\ Matches(Trig(pc), e) THEN LastGrant' ELSE trigG
-           /\ trigNG' = IF ~fired /\ Matches(Trig(pc), e)
-                        THEN {n \in Nodes : up'[n]} \ {LastGrant'.node} ELSE trigNG
-           /\ UNCHANGED <<pc, ngDown>>
-
-\* derives: C1.1, C1.4 -- internal (non-observable) protocol step
-Internal(what, p) == Emit([event |-> "Internal", what |-> what, proc |-> p])
+\* Protocol step emitting the events evs: record them, and advance the current trigger.
+\* Must be the last conjunct of an action (uses grants', up').
+Emit(evs) == /\ lastEv' = evs
+             /\ fired' = (fired \/ Matches(Trig(pc), evs))
+             /\ trigG' = IF ~fired /\ Matches(Trig(pc), evs) THEN LastGrant' ELSE trigG
+             /\ trigNG' = IF ~fired /\ Matches(Trig(pc), evs)
+                          THEN {n \in Nodes : up'[n]} \ {LastGrant'.node} ELSE trigNG
+             /\ trigNM' = IF ~fired /\ Matches(Trig(pc), evs)
+                          THEN Nodes \ (IF commits' = <<>> THEN Init0Rec
+                                        ELSE commits'[CHOOSE i \in 1..Len(commits') :
+                                               \A j \in 1..Len(commits') : commits'[j].rec.ep <= commits'[i].rec.ep].rec).mem
+                          ELSE trigNM
+             /\ UNCHANGED <<pc, ngDown>>
+
+\* derives: C1.1, C1.4 -- internal (non-observable) protocol step. X3: it emits nothing (the
+\* round-1 to X2 model recorded the internal step's name, which only multiplied states).
+Internal(what, p) == Emit(<<>>)
 
 \* ---------------------------------------------------------------------------
-\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
+\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, C3.x, F3.x
 Init ==
     /\ up = [p \in Procs |-> TRUE]
     /\ paused = [c \in Clients |-> FALSE]
@@ -173,6 +297,7 @@ Init ==
     /\ fired = IsStart(Trig(1))
     /\ trigG = [node |-> "none", client |-> "none"]
     /\ trigNG = Nodes
+    /\ trigNM = Nodes \ Init0      \* derives: F3.1; format v5 R1
     /\ ngDown = "none"
     /\ readMsgs = {}       \* derives: C2.1
     /\ rToAck = {}         \* derives: C2.2
@@ -180,10 +305,25 @@ Init ==
     /\ awaitingR = [c \in Clients |-> {}]   \* derives: C2.2
     /\ rdecisions = <<>>   \* derives: C2.1, C2.2
     /\ given = {}          \* derives: C2.2
-    /\ lastEv = [event |-> "Init"]
+    /\ lastEv = <<[event |-> "Init"]>>
+    \* derives: C3.1, C3.4, C3.7, C3.8, F3.1, F3.3 -- every node knows the deployment's epoch 0
+    /\ inc = [n \in Nodes |-> 0]
+    /\ cfg = [n \in Nodes |-> <<Init0Rec>>]
+    /\ jprop = [n \in Nodes |-> NoConf]
+    /\ pend = [n \in Nodes |-> NoPend]
+    /\ owed = [n \in Nodes |-> {}]
+    /\ rcMsgs = {}
+    /\ opMsgs = {}
+    /\ commits = <<>>
+    /\ refusals = <<>>
+    /\ opTold = {}
+    /\ off = [p \in Procs |-> 0]          \* derives: F3.2
+    /\ early = [n \in Nodes |-> FALSE]    \* derives: F3.2
+    /\ agreeLog = [n \in Nodes |-> <<>>]  \* derives: C1.1
 
 \* ===========================================================================
-\* Grantor (abstract): leader per term, majority election, majority-confirmed grants
+\* Grantor (abstract Raft with joint consensus): leader per term, eligible-majority election
+\* over the newest configuration the voters know, majority-counted grants and commits
 \* ===========================================================================
 
 \* derives: C1.1, C1.4, F1.2, F2.1, F2.2 -- node x hears a current leader: an up leader m
@@ -191,23 +331,65 @@ Init ==
 \* A leader hears itself.
 HearsLeader(x) == \E m \in Nodes : up[m] /\ Link(m, x) /\ leader[m] /\ term[m] >= promised[x]
 
-\* derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
+\* ---------------------------------------------------------------------------
+\* Learning a commit at a receiver (derives: C3.4, C3.8, F3.1). When node x's configuration
+\* history becomes H and reaches the epoch its pending request targets, the request is no
+\* longer pending: it is x's commit if H's configuration of that epoch names it, else it is
+\* superseded (contract v3 C3.4(b)). Either way x owes the operator the outcome.
+\* derives: C3.4, F3.1
+Res(x, H) == pend[x] # NoPend /\ Len(H) - 1 >= pend[x].tgt
+\* derives: C3.4, C3.8, F3.1
+ResCommitted(x, H) == H[pend[x].tgt + 1].rid = pend[x].rid
+\* derives: C3.4, F3.1
+NewPend(x, H) == IF Res(x, H) THEN NoPend ELSE pend[x]
+\* derives: C3.4, C3.8, F3.1
+NewOwed(x, H) == IF Res(x, H)
+                 THEN owed[x] \cup {[op |-> pend[x].op, rid |-> pend[x].rid,
+                                     outcome |-> IF ResCommitted(x, H) THEN "committed" ELSE "refused",
+                                     ep |-> pend[x].tgt, x |-> x]}
+                 ELSE owed[x]
+\* derives: C3.4, C3.5, F3.1 -- the refusal decision, with its recorded inputs
+NewRefusals(x, H) == IF Res(x, H) /\ ~ResCommitted(x, H)
+                     THEN Append(refusals, [x |-> x, rid |-> pend[x].rid, mem |-> pend[x].mem,
+                                            reason |-> "superseded", pin |-> "none", cin |-> pend[x].tgt])
+                     ELSE refusals
+\* derives: C3.4, F3.1 -- the ReconfigRefused event, if any
+ResEv(x, H) == IF Res(x, H) /\ ~ResCommitted(x, H)
+               THEN <<[event |-> "Refused", node |-> x, request_id |-> pend[x].rid, reason |-> "superseded",
+                       epoch |-> pend[x].tgt, members |-> pend[x].mem, pending |-> "none"]>>
+               ELSE <<>>
+\* derives: C3.1, F3.1 -- the ConfigCommitted (decided: false) events of the epochs x learns
+LearnEv(x, H) == IF Len(H) > Len(cfg[x])
+                 THEN <<[event |-> "Learn", node |-> x, recs |-> SubSeq(H, Len(cfg[x]) + 1, Len(H))]>>
+                 ELSE <<>>
+
+\* derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, C3.1, C3.7, F3.1, F3.2, F3.3
 \* A node that hears no leader of a term at least its own promise starts an election;
-\* a majority Q (up, connected to n both ways: a vote is a round trip) promises a fresh
-\* term; the new leader learns the highest token any member of Q confirmed.
+\* a quorum Q (up, connected to n both ways: a vote is a round trip) promises a fresh
+\* term; the new leader learns the highest token any member of Q agreed to.
 \* X2: each voter must itself hear no current leader (voter stickiness, a pre-vote check).
 \* derives: C1.4, F2.1 -- under F2.1 a follower cut off from a grantor that still has a
 \* majority can reach a node that still hears it; the voter refuses, so the cut-off
 \* follower cannot disrupt the grantor (P19, P25). Under v1 bipartitions every node a
 \* candidate could reach was on its side and heard no leader either.
+\* X3 (derives: C3.1, C3.7, F3.1, F3.3): the leader adopts the newest configuration history its
+\* voters know (Adopt), and Q must be an eligible majority of that configuration, every voter an
+\* eligible member of it (Raft: a server uses the latest configuration in its log; an amnesic
+\* incarnation does not vote until re-admitted, Paxos Made Live 5.1). It records what it learned.
+\* derives: F3.2 -- a node whose timer fired early (forward clock step) may stand or vote although it
+\* hears a leader; standing or voting resets its timer.
 Elect(n) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
     /\ up[n] /\ ~leader[n]
-    /\ ~HearsLeader(n)
+    /\ ~HearsLeader(n) \/ early[n]
     /\ \E Q \in SUBSET {q \in Nodes : up[q] /\ Conn(n, q)} :
+        LET H == Adopt(Q)
+            X == H[Len(H)]
+            R == RdmOf(H) IN
         /\ n \in Q
-        /\ Majority(Q)
-        /\ \A q \in Q : ~HearsLeader(q)   \* derives: C1.4, F2.1 -- voter stickiness
+        /\ \A q \in Q : EligIn(q, X.mem, R)         \* derives: C3.7, F3.3
+        /\ MajOf(Q, X.mem)
+        /\ \A q \in Q : ~HearsLeader(q) \/ early[q]   \* derives: C1.4, F2.1, F3.2 -- voter stickiness
         /\ LET t == 1 + Max({promised[q] : q \in Q}) IN
            /\ t <= MaxTerm
            /\ promised' = [q \in Nodes |-> IF q \in Q THEN t ELSE promised[q]]
@@ -215,15 +397,24 @@ Elect(n) ==
                                          ELSE IF q \in Q THEN FALSE ELSE leader[q]]
            /\ term' = [term EXCEPT ![n] = t]
            /\ ltok' = [ltok EXCEPT ![n] = Max({maxTok[q] : q \in Q})]
-    /\ UNCHANGED <<up, paused, down, maxTok, reqs, pending, tok, myToks, awaiting,
-                   grantMsgs, writeMsgs, ackMsgs, dups, highest, stval, toAck,
-                   grants, rq, issued, decisions, told>>
-    /\ Internal("Elect", n)
+        /\ early' = [q \in Nodes |-> IF q \in Q THEN FALSE ELSE early[q]]
+        /\ cfg' = [cfg EXCEPT ![n] = H]
+        /\ jprop' = [jprop EXCEPT ![n] = IF @.ep <= Len(H) - 1 THEN NoConf ELSE @]
+        /\ pend' = [pend EXCEPT ![n] = NewPend(n, H)]
+        /\ owed' = [owed EXCEPT ![n] = NewOwed(n, H)]
+        /\ refusals' = NewRefusals(n, H)
+        /\ UNCHANGED <<up, paused, down, maxTok, reqs, pending, tok, myToks, awaiting,
+                       grantMsgs, writeMsgs, ackMsgs, dups, highest, stval, toAck,
+                       grants, rq, issued, decisions, told>>
+        /\ UNCHANGED <<inc, rcMsgs, opMsgs, commits, opTold, off, agreeLog>>
+        /\ Emit(LearnEv(n, H) \o ResEv(n, H))
 
 \* derives: C1.1, C1.4, F1.2, F2.2 -- a leader that hears a node promised to a higher term steps
 \* down (it needs only q->n: the higher promise reaches it in q's message)
 StepDown(n) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars  \* derives: C3.x -- configuration untouched
+    /\ UNCHANGED xvars
     /\ up[n] /\ leader[n]
     /\ \E q \in Nodes : up[q] /\ Link(q, n) /\ promised[q] > term[n]
     /\ leader' = [leader EXCEPT ![n] = FALSE]
@@ -234,6 +425,10 @@ StepDown(n) ==
                    toAck, grants, rq, issued, decisions, told>>
     /\ Internal("StepDown", n)
 
+\* derives: C3.8, F3.1 -- the nodes leader n replicates to: its configuration's members and the members a
+\* request for its next epoch names
+JoinScope(n) == Cur(n).mem \cup UNION {pend[x].mem : x \in {y \in Nodes : pend[y].tgt = CurEp(n) + 1}}
+
 \* derives: C1.4, F1.1, F1.2, F2.2 -- the P10 fix (judge's verdict, locus: model).
 \* X2: it needs only the link n->q (the leader's message reaches q).
 \* A leader brings a reachable, up, lagging node into its term: the node raises its
@@ -243,28 +438,44 @@ StepDown(n) ==
 \* enabled either: C1.4 fails with a majority, storage and the requester all up and
 \* connected. Raising a promise is always safe here: promises only grow, and a grant
 \* still needs a majority promised to exactly the leader's term.
-Join(n, q) ==
+\* X3 (derives: C3.8, F3.1, F3.3): the leader replicates to the members of its current configuration
+\* and, once a request for the next epoch is pending, to the members it requests (Raft thesis
+\* 4.2.1: new servers are caught up as non-voting members); an amnesic member is joined like any
+\* other, and its agreements count only if eligible One heartbeat reaches every such node whose
+\* link from the leader is up, in one step (README X3 "Abstractions"; before X3, one node per step).
+Join(n) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
-    /\ up[n] /\ leader[n] /\ up[q] /\ q # n
-    /\ Link(n, q)
-    /\ promised[q] < term[n]
-    /\ promised' = [promised EXCEPT ![q] = term[n]]
-    /\ leader' = [leader EXCEPT ![q] = FALSE]
+    /\ UNCHANGED kvars  \* derives: C3.x -- configuration untouched
+    /\ UNCHANGED xvars
+    /\ up[n] /\ leader[n]
+    /\ LET J == {q \in JoinScope(n) : up[q] /\ q # n /\ Link(n, q) /\ promised[q] < term[n]} IN
+       /\ J # {}
+       /\ promised' = [q \in Nodes |-> IF q \in J THEN term[n] ELSE promised[q]]
+       /\ leader' = [q \in Nodes |-> IF q \in J THEN FALSE ELSE leader[q]]
     /\ UNCHANGED <<up, paused, down, maxTok, term, ltok, reqs, pending, tok, myToks,
                    awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
                    toAck, grants, rq, issued, decisions, told>>
-    /\ Internal("Join", q)
+    /\ Internal("Join", n)
 
 \* derives: C1.4, F2.2, F2.1, F1.2 -- the quorum check (new in X2). A leader that is not
 \* connected (both ways) to a majority of up lease nodes, itself included, stops leading.
 \* Under F2.2 the followers may still hear a grantor that cannot hear them; their
 \* failure detector then never fires and, without this, nobody would ever elect (P26).
 \* Under v1 it only lets a grantor isolated in a minority stop sooner.
+\* X3 (derives: C1.4, C3.7, F3.1, F3.2, F3.3): the majority is of eligible members of the leader's
+\* current configuration; a leader that is no longer an eligible member of it steps down (Raft
+\* thesis 4.2.2, a removed leader steps down once the change is committed); and a forward clock
+\* step may fire the quorum timer early (a spurious step-down).
 CheckQuorum(n) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED <<off, agreeLog>>
     /\ up[n] /\ leader[n]
-    /\ ~Majority({q \in Nodes : up[q] /\ Conn(n, q)})
+    /\ \/ ~Elig(n, n)
+       \/ ~MajOf({q \in Nodes : up[q] /\ Conn(n, q) /\ Elig(q, n)}, Cur(n).mem)
+       \/ early[n]
     /\ leader' = [leader EXCEPT ![n] = FALSE]
+    /\ early' = [early EXCEPT ![n] = FALSE]
     /\ UNCHANGED <<up, paused, down, promised, maxTok, term, ltok, reqs, pending, tok, myToks,
                    awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
                    toAck, grants, rq, issued, decisions, told>>
@@ -280,43 +491,60 @@ ReqRoute(c, n) == Link(c, n) \/ \E f \in Nodes : up[f] /\ Link(c, f) /\ Link(f,
 \* one up lease node; its fate is fixed when n sends it (the relay forwards at once)
 RepRoute(n, c) == Link(n, c) \/ \E f \in Nodes : up[f] /\ Link(n, f) /\ Link(f, c)
 
-\* derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2; format v4 L3; observe v4 "Grants and retransmission"
+\* derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, C3.5, C3.7, F3.1, F3.3; format v4 L3; observe v4, v5
 \* The leader issues a grant to a requester whose request reaches it (ReqRoute), once a
-\* majority still promised to its term, and connected to it (a confirmation is a round
-\* trip), durably confirms the token. The Grant is recorded whether or not the reply can
+\* majority still promised to its term, and connected to it (an agreement is a round
+\* trip), durably agrees to the token. The Grant is recorded whether or not the reply can
 \* be delivered (F2.2: a grantor may hear a requester it cannot answer, H8); the reply is in
 \* flight only if RepRoute holds when it is sent. A leader answers each request at most once
 \* per term; a lost reply is retransmitted by Resend (no new Grant record).
+\* X3 (C3.7): the grant is issued under the leader's current configuration and counted by eligible
+\* agreements from a majority of it; the leader must itself be an eligible member. The record
+\* carries its configuration epoch and its inputs (C3.5): the counted agreements, the members and
+\* epoch counted against, the term, and the last token the leader knew (`last_token`); the
+\* token is last_token + 1. No clock is read.
 Grant(n, c) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED <<off, early>>
     /\ up[n] /\ leader[n]
+    /\ Elig(n, n)                                       \* derives: C3.7, F3.1, F3.3
     /\ c \in reqs
     /\ ReqRoute(c, n)
     /\ ~\E m \in grantMsgs : m.c = c
     /\ ~\E x \in issued : x.n = n /\ x.g = term[n] /\ x.c = c /\ x.r = rq[c]
-    /\ \E Q \in SUBSET {q \in Nodes : up[q] /\ Conn(n, q) /\ promised[q] = term[n]} :
+    /\ \E Q \in SUBSET {q \in Nodes : up[q] /\ Conn(n, q) /\ promised[q] = term[n] /\ Elig(q, n)} :
         /\ n \in Q
-        /\ Majority(Q)
-        /\ LET k == ltok[n] + 1 IN
+        /\ MajOf(Q, Cur(n).mem)                         \* derives: C3.7
+        /\ LET k == ltok[n] + 1
+               ag == {<<q, inc[q]>> : q \in Q} IN
            /\ maxTok' = [q \in Nodes |-> IF q \in Q THEN Max({maxTok[q], k}) ELSE maxTok[q]]
            /\ ltok' = [ltok EXCEPT ![n] = k]
            /\ grantMsgs' = IF RepRoute(n, c)
                            THEN grantMsgs \cup {[n |-> n, c |-> c, t |-> k, g |-> term[n]]}
                            ELSE grantMsgs
            /\ issued' = issued \cup {[n |-> n, c |-> c, r |-> rq[c], t |-> k, g |-> term[n]]}
-           /\ grants' = Append(grants, [token |-> k, term |-> term[n], node |-> n, client |-> c])
+           /\ grants' = Append(grants, [token |-> k, term |-> term[n], node |-> n, client |-> c,
+                                        ninc |-> inc[n], ep |-> CurEp(n), cep |-> CurEp(n),
+                                        mem |-> Cur(n).mem, ag |-> ag, lt |-> ltok[n]])
+           /\ agreeLog' = [q \in Nodes |-> IF q \in Q THEN Append(agreeLog[q], [i |-> inc[q], t |-> k])
+                                           ELSE agreeLog[q]]   \* derives: C1.1
            /\ UNCHANGED rq
            /\ UNCHANGED <<up, paused, down, promised, leader, term, reqs, pending, tok,
                           myToks, awaiting, writeMsgs, ackMsgs, dups, highest, stval,
                           toAck, decisions, told>>
-           /\ Emit([event |-> "Grant", client |-> c, key |-> Key, token |-> k,
-                    lifetime |-> Lifetime, grantor_term |-> term[n], node |-> n])
+           /\ Emit(<<[event |-> "Grant", client |-> c, key |-> Key, token |-> k,
+                      lifetime |-> Lifetime, grantor_term |-> term[n], node |-> n, ninc |-> inc[n],
+                      config_epoch |-> CurEp(n), members |-> Cur(n).mem, last_token |-> ltok[n],
+                      agreed |-> ag]>>)
 
 \* derives: C1.4, F2.1, F2.2; observe v4 "Grants and retransmission" -- the leader retransmits
 \* the grant it already issued for c's current request, while the request still reaches it
 \* and a reply route exists. Not a new grant: no Grant record, same token.
 Resend(n, c) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ up[n] /\ leader[n]
     /\ c \in reqs
     /\ ReqRoute(c, n) /\ RepRoute(n, c)
@@ -332,6 +560,8 @@ Resend(n, c) ==
 \* derives: C1.4, F1.3 -- a (running, unpaused) client receives a grant reply
 RecvGrant(m) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ m \in grantMsgs
     /\ up[m.c] /\ ~paused[m.c]
     /\ grantMsgs' = grantMsgs \ {m}
@@ -345,16 +575,159 @@ RecvGrant(m) ==
                    writeMsgs, ackMsgs, dups, highest, stval, toAck, grants, rq, issued, decisions, told>>
     /\ Internal("RecvGrant", m.c)
 
+\* ===========================================================================
+\* Configuration change (contract v3, failure model F3.1; Raft joint consensus, README X3)
+\* ===========================================================================
+
+\* derives: C3.4, F2.1, F2.2, F3.1; format v4 L3 -- a receiver passes its pending request to the leader
+\* directly or through one up lease node (as a client's request, FR.1)
+FwdRoute(x, l) == Link(x, l) \/ \E f \in Nodes : up[f] /\ Link(x, f) /\ Link(f, l)
+
+\* derives: C3.8, F3.1 -- nodes in M that can agree to leader l's configuration proposal: up, connected
+\* to l, promised to its term, and caught up to l's configuration history (Raft thesis 4.2.1: a
+\* new server is caught up before it counts)
+Agreeable(l, M) == {q \in M \cap Nodes : up[q] /\ Conn(l, q) /\ promised[q] = term[l]
+                                         /\ Len(cfg[q]) = Len(cfg[l])}
+
+\* derives: C3.1, C3.5, C3.8, F3.1, F3.3; contract v3 "Re-admission"
+\* Leader l decides the request pending at receiver x as the next epoch: eligible agreements
+\* from a majority of its current configuration (Qo) and of the requested set (Qn), one
+\* agreement for a node in both. Amnesic incarnations in the requested set that agree (Rr) are
+\* recorded, not counted, and re-admitted. Everyone who agreed keeps the proposal and the
+\* leader's token count (the joint entry and the log before it). The decision and the
+\* agreements are one step (README X3). If x = l, its request is resolved at once.
+Commit(l, x) ==
+    LET r == pend[x]
+        e == CurEp(l)
+        Old == Cur(l)
+        R == RdmOf(cfg[l]) IN
+    /\ UNCHANGED rvars
+    /\ UNCHANGED <<inc, rcMsgs, opMsgs, opTold, xvars>>
+    /\ up[l] /\ leader[l] /\ Elig(l, l)
+    /\ up[x] /\ r # NoPend
+    /\ x = l \/ FwdRoute(x, l)
+    /\ r.tgt = e + 1
+    /\ \E Qo \in SUBSET {q \in Agreeable(l, Old.mem) : EligIn(q, Old.mem, R)},
+          Qn \in SUBSET {q \in Agreeable(l, r.mem) : EligIn(q, r.mem, R)},
+          Rr \in SUBSET {q \in Agreeable(l, r.mem) : inc[q] > 0 /\ <<q, inc[q]>> \notin R} :
+        /\ l \in Qo
+        /\ Qo \cap r.mem = Qn \cap Old.mem
+        /\ MajOf(Qo, Old.mem) /\ MajOf(Qn, r.mem)
+        /\ LET A == Qo \cup Qn \cup Rr
+               X == [ep |-> e + 1, mem |-> r.mem, rid |-> r.rid,
+                     rdm |-> {<<q, inc[q]>> : q \in {p \in A : inc[p] > 0 /\ p \in r.mem}}, by |-> l]
+               H == Append(cfg[l], X)
+               ago == {<<q, inc[q]>> : q \in Qo}
+               agn == {<<q, inc[q]>> : q \in Qn}
+               agr == {<<q, inc[q]>> : q \in Rr} IN
+           /\ cfg' = [cfg EXCEPT ![l] = H]
+           /\ jprop' = [q \in Nodes |-> IF q \in A \ {l} THEN X ELSE jprop[q]]
+           /\ maxTok' = [q \in Nodes |-> IF q \in A THEN Max({maxTok[q], ltok[l]}) ELSE maxTok[q]]
+           /\ commits' = Append(commits, [rec |-> X, ago |-> ago, agn |-> agn, agr |-> agr,
+                                          old |-> Old.mem, oep |-> e, req |-> r.mem, node |-> l,
+                                          ninc |-> inc[l]])
+           /\ pend' = [pend EXCEPT ![l] = NewPend(l, H)]
+           /\ owed' = [owed EXCEPT ![l] = NewOwed(l, H)]
+           /\ refusals' = NewRefusals(l, H)
+           \* derives: C3.7, F3.1 -- a leader the commit removes steps down with it (Raft thesis 4.2.2)
+           /\ leader' = [leader EXCEPT ![l] = l \in r.mem]
+           /\ UNCHANGED <<up, paused, down, promised, term, ltok, reqs, pending, tok,
+                          myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
+                          toAck, grants, rq, issued, decisions, told>>
+           /\ Emit(<<[event |-> "Commit", node |-> l, ninc |-> inc[l], rec |-> X, ago |-> ago,
+                      agn |-> agn, agr |-> agr, old |-> Old.mem, oep |-> e, req |-> r.mem]>>
+                   \o ResEv(l, H))
+
+\* derives: C3.1, C3.4, F3.1, F3.3 -- node n learns the next committed configuration from m, which has
+\* recorded it, over the link m->n (Raft: the leader's AppendEntries; here any node that has it
+\* may teach it, which is safe because it is committed). An amnesic node learns its
+\* configuration this way (contract v3: "learns its configuration from others").
+LearnConfig(n, m) ==
+    /\ UNCHANGED rvars
+    /\ UNCHANGED <<inc, rcMsgs, opMsgs, commits, opTold, xvars>>
+    /\ up[n] /\ up[m] /\ n # m /\ Link(m, n)
+    /\ Len(cfg[m]) > Len(cfg[n])
+    \* derives: C3.4, F3.1 -- m teaches a commit to the members of the configuration it commits, to a
+    \* receiver holding a request (the answer to its forwarding), and to a node a pending request
+    \* names (catch-up, Raft thesis 4.2.1); a node the commit removed need not learn of it
+    /\ \/ n \in cfg[m][Len(cfg[n]) + 1].mem
+       \/ pend[n] # NoPend
+       \/ \E x \in Nodes : n \in pend[x].mem
+    /\ LET H == Append(cfg[n], cfg[m][Len(cfg[n]) + 1]) IN
+       /\ cfg' = [cfg EXCEPT ![n] = H]
+       /\ jprop' = [jprop EXCEPT ![n] = IF @.ep <= Len(H) - 1 THEN NoConf ELSE @]
+       /\ pend' = [pend EXCEPT ![n] = NewPend(n, H)]
+       /\ owed' = [owed EXCEPT ![n] = NewOwed(n, H)]
+       /\ refusals' = NewRefusals(n, H)
+       /\ UNCHANGED <<up, paused, down, promised, maxTok, leader, term, ltok, reqs, pending, tok,
+                      myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
+                      toAck, grants, rq, issued, decisions, told>>
+       /\ Emit(LearnEv(n, H) \o ResEv(n, H))
+
+\* derives: C3.4, C3.5, F3.1; contract v3 C3.4(a) -- receiver x records a request it receives and, in
+\* this order, refuses it as `invalid` (empty, or naming a non-lease process) or `busy` (another
+\* request pending here; the earlier one is kept), else holds it pending, targeting the epoch
+\* after its current one.
+RecvReconfig(m) ==
+    LET x == m.to IN
+    /\ UNCHANGED rvars
+    /\ UNCHANGED <<inc, cfg, jprop, opMsgs, commits, opTold, xvars>>
+    /\ m \in rcMsgs /\ up[x]
+    /\ rcMsgs' = rcMsgs \ {m}
+    /\ LET inval == m.mem = {} \/ ~(m.mem \subseteq Nodes)
+           busy == ~inval /\ pend[x] # NoPend
+           req == [event |-> "ReconfigRequest", node |-> x, operator |-> m.op, request_id |-> m.rid,
+                   members |-> m.mem] IN
+       IF inval \/ busy
+       THEN /\ owed' = [owed EXCEPT ![x] = @ \cup {[op |-> m.op, rid |-> m.rid, outcome |-> "refused",
+                                                    ep |-> -1, x |-> x]}]
+            /\ refusals' = Append(refusals, [x |-> x, rid |-> m.rid, mem |-> m.mem,
+                                             reason |-> IF inval THEN "invalid" ELSE "busy",
+                                             pin |-> IF inval THEN "none" ELSE pend[x].rid, cin |-> -1])
+            /\ UNCHANGED pend
+            /\ UNCHANGED <<up, paused, down, promised, maxTok, leader, term, ltok, reqs, pending, tok,
+                           myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
+                           toAck, grants, rq, issued, decisions, told>>
+            /\ Emit(<<req, [event |-> "Refused", node |-> x, request_id |-> m.rid,
+                            reason |-> IF inval THEN "invalid" ELSE "busy", epoch |-> -1,
+                            members |-> m.mem, pending |-> IF inval THEN "none" ELSE pend[x].rid]>>)
+       ELSE /\ pend' = [pend EXCEPT ![x] = [rid |-> m.rid, mem |-> m.mem, op |-> m.op, tgt |-> CurEp(x) + 1]]
+            /\ UNCHANGED <<owed, refusals>>
+            /\ UNCHANGED <<up, paused, down, promised, maxTok, leader, term, ltok, reqs, pending, tok,
+                           myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
+                           toAck, grants, rq, issued, decisions, told>>
+            /\ Emit(<<req>>)
+
+\* derives: C3.4, C3.8, F2.1, F2.2 -- receiver x sends an outcome it owes the operator, and the operator
+\* (which never crashes) is told it. The reply is sent only over an up link x->op (a send on a down
+\* link is lost and x keeps owing it); its receipt is taken in the same step (README X3
+\* "Abstractions": nothing in the contract depends on that delay).
+ReplyOp(x, a) ==
+    /\ UNCHANGED rvars
+    /\ UNCHANGED <<inc, cfg, jprop, pend, rcMsgs, opMsgs, commits, refusals, xvars>>
+    /\ up[x] /\ a \in owed[x]
+    /\ Link(x, a.op)
+    /\ owed' = [owed EXCEPT ![x] = @ \ {a}]
+    /\ opTold' = opTold \cup {[op |-> a.op, rid |-> a.rid, outcome |-> a.outcome, ep |-> a.ep]}
+    /\ UNCHANGED <<up, paused, down, promised, maxTok, leader, term, ltok, reqs, pending, tok,
+                   myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
+                   toAck, grants, rq, issued, decisions, told>>
+    /\ Emit(<<[event |-> "ReconfigAck", operator |-> a.op, request_id |-> a.rid, outcome |-> a.outcome,
+               epoch |-> a.ep, node |-> x]>>)
+
 \* ===========================================================================
 \* Storage
 \* ===========================================================================
 
-\* derives: C1.2, C1.3, F1.1
-\* Storage decides a write: accept iff token >= ledger; on accept the token becomes
-\* the ledger. The ack is queued (volatile) and sent by SendAck. dup = TRUE models a
-\* duplicated delivery (the message stays in flight), bounded by MaxDups.
+\* derives: C1.2, C1.3, F1.1, C3.5 -- storage decides a write: accept iff token >= ledger (contract v3:
+\* "storage decides deterministically"); on accept the token becomes the ledger and the value is
+\* stored. The ack is queued (volatile) and sent by SendAck. dup = TRUE models a duplicated
+\* delivery (the message stays in flight), bounded by MaxDups. X3: the decision records its
+\* inputs (token, ledger, stored value, value); it reads no clock.
 StorageDecide(m, dup) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ up[Store]
     /\ m \in writeMsgs
     /\ dup => dups < MaxDups
@@ -365,18 +738,20 @@ StorageDecide(m, dup) ==
        /\ writeMsgs' = IF dup THEN writeMsgs ELSE writeMsgs \ {m}
        /\ dups' = IF dup THEN dups + 1 ELSE dups
        /\ decisions' = Append(decisions, [token |-> m.t, hb |-> highest, outcome |-> out,
-                                          client |-> m.c, value |-> m.v, term |-> m.g])
+                                          client |-> m.c, value |-> m.v, term |-> m.g, sv |-> stval])
        /\ toAck' = toAck \cup {[c |-> m.c, t |-> m.t, g |-> m.g, v |-> m.v, outcome |-> out]}
        /\ UNCHANGED <<up, paused, down, promised, maxTok, leader, term, ltok, reqs,
                       pending, tok, myToks, awaiting, grantMsgs, ackMsgs, grants, rq, issued, told>>
-       /\ Emit([event |-> IF acc THEN "WriteAccept" ELSE "WriteReject", key |-> Key,
-                token |-> m.t, highest_before |-> highest, grantor_term |-> m.g,
-                client |-> m.c, value |-> m.v])
+       /\ Emit(<<[event |-> IF acc THEN "WriteAccept" ELSE "WriteReject", key |-> Key,
+                  token |-> m.t, highest_before |-> highest, grantor_term |-> m.g,
+                  client |-> m.c, value |-> m.v, stored_value |-> stval]>>)
 
 \* derives: C1.3, F1.1, F1.2, F2.1, F2.2 -- storage sends a queued ack (lost if the link
 \* storage->client is down or the client is down, at the moment it is sent)
 SendAck(a) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ up[Store]
     /\ a \in toAck
     /\ toAck' = toAck \ {a}
@@ -390,6 +765,8 @@ SendAck(a) ==
 \* and is told the write's outcome exactly as the ack states it.
 RecvAck(a) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ a \in ackMsgs
     /\ up[a.c] /\ ~paused[a.c]
     /\ ackMsgs' = ackMsgs \ {a}
@@ -401,9 +778,9 @@ RecvAck(a) ==
             /\ UNCHANGED <<up, paused, down, promised, maxTok, leader, term, ltok, reqs,
                            pending, tok, myToks, grantMsgs, writeMsgs, dups, highest,
                            stval, toAck, grants, rq, issued, decisions>>
-            /\ Emit([event |-> "WriteAck", client |-> a.c, key |-> Key, token |-> a.t,
-                     outcome |-> IF a.outcome = "accept" THEN "accepted" ELSE "rejected",
-                     value |-> a.v, grantor_term |-> a.g])
+            /\ Emit(<<[event |-> "WriteAck", client |-> a.c, key |-> Key, token |-> a.t,
+                       outcome |-> IF a.outcome = "accept" THEN "accepted" ELSE "rejected",
+                       value |-> a.v, grantor_term |-> a.g]>>)
        ELSE /\ UNCHANGED <<up, paused, down, promised, maxTok, leader, term, ltok, reqs,
                            pending, tok, myToks, awaiting, grantMsgs, writeMsgs, dups,
                            highest, stval, toAck, grants, rq, issued, decisions, told>>
@@ -413,11 +790,13 @@ RecvAck(a) ==
 \* Schedule steps: workload (derives from the contract) and faults (one per cell)
 \* ===========================================================================
 
-\* derives: F1.1, F1.2, F1.3; format v2.1 A1 -- resolve "grantor"/"holder"/"non-grantor" at trigger time
-\* format v2.1 A1: `non-grantor` resolves to ng, one of the candidates chosen by ScheduleStep
-Resolve(x, ng) == IF x = "grantor" THEN trigG.node
-                  ELSE IF x = "holder" THEN trigG.client
-                  ELSE IF x = "non-grantor" THEN ng ELSE x
+\* derives: F1.1, F1.2, F1.3; format v2.1 A1, v5 R1 -- resolve "grantor"/"holder"/"non-grantor"/"non-member"
+\* at trigger time. format v2.1 A1: `non-grantor` resolves to ng, one of the candidates chosen by
+\* ScheduleStep; format v5 R1: `non-member` resolves to nm, likewise
+Resolve(x, ng, nm) == IF x = "grantor" THEN trigG.node
+                      ELSE IF x = "holder" THEN trigG.client
+                      ELSE IF x = "non-grantor" THEN ng
+                      ELSE IF x = "non-member" THEN nm ELSE x
 
 \* derives: C1.2, F1.3 -- the client's most recent superseded token (lower than the highest granted)
 StaleTok(c) ==
@@ -428,6 +807,8 @@ StaleTok(c) ==
 \* a grant does not issue a second request; the step waits until it is not waiting)
 DoRequest(c) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ up[c] /\ ~paused[c]
     /\ ~pending[c]
     /\ pending' = [pending EXCEPT ![c] = TRUE]
@@ -436,13 +817,15 @@ DoRequest(c) ==
     /\ UNCHANGED <<up, paused, down, promised, maxTok, leader, term, ltok, tok, myToks,
                    awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval, toAck,
                    grants, issued, decisions, told>>
-    /\ lastEv' = [event |-> "Request", client |-> c, key |-> Key]
+    /\ lastEv' = <<[event |-> "Request", client |-> c, key |-> Key]>>
 
 \* derives: C1.2, C1.3, F1.3, F2.1, F2.2 -- workload: client writes with its current (or stale)
 \* token; the write is lost if client->storage is down when it is sent
 DoWrite(c, v, stale) ==
     LET k == IF stale THEN StaleTok(c) ELSE tok[c] IN
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ up[c] /\ ~paused[c]
     /\ k.t > 0
     /\ writeMsgs' = IF Link(c, Store) /\ up[Store]
@@ -452,17 +835,32 @@ DoWrite(c, v, stale) ==
     /\ UNCHANGED <<up, paused, down, promised, maxTok, leader, term, ltok, reqs, pending,
                    tok, myToks, grantMsgs, ackMsgs, dups, highest, stval, toAck,
                    grants, rq, issued, decisions, told>>
-    /\ lastEv' = [event |-> "WriteAttempt", client |-> c, key |-> Key, token |-> k.t,
-                  value |-> v, grantor_term |-> k.g]
+    /\ lastEv' = <<[event |-> "WriteAttempt", client |-> c, key |-> Key, token |-> k.t,
+                    value |-> v, grantor_term |-> k.g]>>
+
+\* derives: C3.4, F3.1; format v5 R1 -- an operator sends a reconfiguration request to receiver x. It is a
+\* message: lost if o->x is down (or x is down) when it is sent. Not a fault.
+DoReconfig(o, rid, mem, x) ==
+    /\ UNCHANGED rvars
+    /\ UNCHANGED <<inc, cfg, jprop, pend, owed, opMsgs, commits, refusals, opTold, xvars>>
+    /\ x \in Nodes
+    /\ rcMsgs' = IF Link(o, x) /\ up[x] THEN rcMsgs \cup {[op |-> o, rid |-> rid, mem |-> mem, to |-> x]}
+                 ELSE rcMsgs
+    /\ UNCHANGED <<up, paused, down, promised, maxTok, leader, term, ltok, reqs, pending, tok,
+                   myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
+                   toAck, grants, rq, issued, decisions, told>>
+    /\ lastEv' = <<[event |-> "ReconfigSend", operator |-> o, request_id |-> rid, to |-> x, members |-> mem]>>
 
 \* ===========================================================================
 \* Reads (contract v2, X1)
 \* ===========================================================================
 
-\* derives: C2.1, C2.2, F1.1 -- storage decides a read: serve iff token >= ledger, returning
+\* derives: C2.1, C2.2, F1.1, C3.5 -- storage decides a read: serve iff token >= ledger, returning
 \* the value it holds; the ledger is not changed. The ack is queued (volatile).
 \* dup = TRUE models a duplicated delivery (bounded by MaxDups, shared with writes).
 StorageRead(m, dup) ==
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ up[Store]
     /\ m \in readMsgs
     /\ dup => dups < MaxDups
@@ -481,14 +879,17 @@ StorageRead(m, dup) ==
        /\ rToAck' = rToAck \cup {[c |-> m.c, t |-> m.t, g |-> m.g, r |-> m.r,
                                   outcome |-> out, v |-> val]}
        /\ Emit(IF srv
-                THEN [event |-> "ReadAccept", key |-> Key, token |-> m.t, highest_before |-> highest,
-                      value |-> val, grantor_term |-> m.g, client |-> m.c, rid |-> m.r]
-                ELSE [event |-> "ReadReject", key |-> Key, token |-> m.t, highest_before |-> highest,
-                      grantor_term |-> m.g, client |-> m.c, rid |-> m.r])
+                THEN <<[event |-> "ReadAccept", key |-> Key, token |-> m.t, highest_before |-> highest,
+                        value |-> val, grantor_term |-> m.g, client |-> m.c, rid |-> m.r,
+                        stored_value |-> stval]>>
+                ELSE <<[event |-> "ReadReject", key |-> Key, token |-> m.t, highest_before |-> highest,
+                        grantor_term |-> m.g, client |-> m.c, rid |-> m.r, stored_value |-> stval]>>)
 
 \* derives: C2.2, F1.1, F1.2, F2.1, F2.2 -- storage sends a queued read ack (lost if the link
 \* storage->client is down or the client is down, at the moment it is sent)
 SendReadAck(a) ==
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ up[Store]
     /\ a \in rToAck
     /\ rToAck' = rToAck \ {a}
@@ -502,6 +903,8 @@ SendReadAck(a) ==
 \* derives: C2.2, F1.3 -- a client receives an ack for a read it is awaiting and is given
 \* exactly the value the ack carries (only when the ack says served)
 RecvReadAck(a) ==
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ a \in rAckMsgs
     /\ up[a.c] /\ ~paused[a.c]
     /\ rAckMsgs' = rAckMsgs \ {a}
@@ -515,10 +918,10 @@ RecvReadAck(a) ==
             /\ given' = IF a.outcome = "served"
                         THEN given \cup {[c |-> a.c, t |-> a.t, r |-> a.r, v |-> a.v]} ELSE given
             /\ Emit(IF a.outcome = "served"
-                     THEN [event |-> "ReadAck", client |-> a.c, key |-> Key, token |-> a.t,
-                           outcome |-> "served", value |-> a.v, grantor_term |-> a.g, rid |-> a.r]
-                     ELSE [event |-> "ReadAck", client |-> a.c, key |-> Key, token |-> a.t,
-                           outcome |-> "rejected", grantor_term |-> a.g, rid |-> a.r])
+                     THEN <<[event |-> "ReadAck", client |-> a.c, key |-> Key, token |-> a.t,
+                             outcome |-> "served", value |-> a.v, grantor_term |-> a.g, rid |-> a.r]>>
+                     ELSE <<[event |-> "ReadAck", client |-> a.c, key |-> Key, token |-> a.t,
+                             outcome |-> "rejected", grantor_term |-> a.g, rid |-> a.r]>>)
        ELSE /\ UNCHANGED <<awaitingR, given>>
             /\ Internal("DropReadAck", a.c)
 
@@ -526,6 +929,8 @@ RecvReadAck(a) ==
 \* (or stale) token; waits as for a write. The read id is the schedule step index.
 DoRead(c, stale) ==
     LET k == IF stale THEN StaleTok(c) ELSE tok[c] IN
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ up[c] /\ ~paused[c]
     /\ k.t > 0
     /\ readMsgs' = IF Link(c, Store) /\ up[Store]
@@ -536,12 +941,16 @@ DoRead(c, stale) ==
     /\ UNCHANGED <<up, paused, down, promised, maxTok, leader, term, ltok, reqs, pending,
                    tok, myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
                    toAck, grants, rq, issued, decisions, told>>
-    /\ lastEv' = [event |-> "ReadAttempt", client |-> c, key |-> Key, token |-> k.t,
-                  grantor_term |-> k.g, rid |-> pc]
+    /\ lastEv' = <<[event |-> "ReadAttempt", client |-> c, key |-> Key, token |-> k.t,
+                    grantor_term |-> k.g, rid |-> pc]>>
 
 \* derives: F1.1 -- crash-stop: volatile state lost, durable state kept, messages to p lost
+\* X3 (derives: F1.1, F3.2, C3.4): a lease node's timers restart with it (early cleared), and
+\* reconfiguration requests in flight to it are lost with its inbox; its pending request and
+\* owed replies are durable.
 Crash(p) ==
     /\ up[p]
+    /\ p \notin Ops   \* derives: C3.4 -- an operator does not crash (contract v3 "Operator")
     /\ up' = [up EXCEPT ![p] = FALSE]
     /\ IF p \in Nodes
        THEN /\ leader' = [leader EXCEPT ![p] = FALSE]
@@ -550,6 +959,8 @@ Crash(p) ==
             /\ UNCHANGED <<paused, reqs, pending, tok, myToks, awaiting, grantMsgs,
                            writeMsgs, ackMsgs, toAck>>
             /\ UNCHANGED <<readMsgs, rToAck, rAckMsgs, awaitingR>>
+            /\ early' = [early EXCEPT ![p] = FALSE]
+            /\ rcMsgs' = {m \in rcMsgs : m.to # p}
        ELSE IF p \in Clients
        THEN /\ paused' = [paused EXCEPT ![p] = FALSE]
             /\ reqs' = reqs \ {p}
@@ -564,6 +975,7 @@ Crash(p) ==
             /\ rAckMsgs' = {a \in rAckMsgs : a.c # p}
             /\ awaitingR' = [awaitingR EXCEPT ![p] = {}]
             /\ UNCHANGED <<readMsgs, rToAck>>
+            /\ UNCHANGED <<early, rcMsgs>>
        ELSE \* storage
             /\ writeMsgs' = {}
             /\ toAck' = {}
@@ -573,19 +985,58 @@ Crash(p) ==
             /\ readMsgs' = {}
             /\ rToAck' = {}
             /\ UNCHANGED <<rAckMsgs, awaitingR>>
+            /\ UNCHANGED <<early, rcMsgs>>
     /\ UNCHANGED <<down, promised, maxTok, dups, highest, stval, grants, rq, issued, decisions, told>>
     /\ UNCHANGED <<rdecisions, given>>
-    /\ lastEv' = [event |-> "Fault", cell |-> "F1.1", action |-> "crash", target |-> p]
+    /\ UNCHANGED <<inc, cfg, jprop, pend, owed, opMsgs, commits, refusals, opTold, off, agreeLog>>
+    /\ lastEv' = <<[event |-> "Fault", cell |-> "F1.1", action |-> "crash", target |-> p]>>
 
 \* derives: F1.1 -- restart with durable state only (a restarted client has no grant)
 Restart(p) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ ~up[p]
     /\ up' = [up EXCEPT ![p] = TRUE]
     /\ UNCHANGED <<paused, down, promised, maxTok, leader, term, ltok, reqs, pending, tok,
                    myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
                    toAck, grants, rq, issued, decisions, told>>
-    /\ lastEv' = [event |-> "Fault", cell |-> "F1.1", action |-> "restart", target |-> p]
+    /\ lastEv' = <<[event |-> "Fault", cell |-> "F1.1", action |-> "restart", target |-> p]>>
+
+\* derives: F3.3, C3.7, C3.8, C1.1; format v5 R3 -- amnesic restart of a crashed lease node: a new
+\* incarnation with no durable state. It keeps what the deployment gives every node (its name,
+\* the lease nodes, the initial configuration, L): its configuration history is the deployment's
+\* epoch 0, unrecorded. Its pending request and owed replies are gone (contract v3 "Pending").
+AmnesicRestart(n) ==
+    /\ UNCHANGED rvars
+    /\ UNCHANGED <<rcMsgs, opMsgs, commits, refusals, opTold, xvars>>
+    /\ n \in Nodes /\ ~up[n]
+    /\ up' = [up EXCEPT ![n] = TRUE]
+    /\ inc' = [inc EXCEPT ![n] = @ + 1]
+    /\ promised' = [promised EXCEPT ![n] = 0]
+    /\ maxTok' = [maxTok EXCEPT ![n] = 0]
+    /\ cfg' = [cfg EXCEPT ![n] = <<Init0Rec>>]
+    /\ jprop' = [jprop EXCEPT ![n] = NoConf]
+    /\ pend' = [pend EXCEPT ![n] = NoPend]
+    /\ owed' = [owed EXCEPT ![n] = {}]
+    /\ UNCHANGED <<paused, down, leader, term, ltok, reqs, pending, tok,
+                   myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
+                   toAck, grants, rq, issued, decisions, told>>
+    /\ lastEv' = <<[event |-> "Fault", cell |-> "F3.3", action |-> "restart", target |-> n, amnesia |-> TRUE]>>
+
+\* derives: F3.2, C1.4; format v5 R2 -- p's clock steps by s ticks (s = step x L). A forward step on a
+\* running lease node may fire its timers early; a backward step only delays them, which the
+\* untimed failure detector (HearsLeader) already allows, so it enables nothing new.
+ClockStep(p, s) ==
+    /\ UNCHANGED rvars
+    /\ UNCHANGED kvars
+    /\ UNCHANGED agreeLog
+    /\ off' = [off EXCEPT ![p] = @ + s]
+    /\ early' = IF p \in Nodes /\ s > 0 /\ up[p] THEN [early EXCEPT ![p] = TRUE] ELSE early
+    /\ UNCHANGED <<up, paused, down, promised, maxTok, leader, term, ltok, reqs, pending, tok,
+                   myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
+                   toAck, grants, rq, issued, decisions, told>>
+    /\ lastEv' = <<[event |-> "Fault", cell |-> "F3.2", action |-> "clock", target |-> p, step |-> s]>>
 
 \* derives: F1.2, F2.1 -- complete bipartition: every link between the two sides goes down in
 \* both directions (F2.1: "F1.2 is the special case in which the down links are exactly
@@ -594,67 +1045,79 @@ Restart(p) ==
 \* fixed when it is sent). This replaces v1 interpretation 13 (README, X2).
 Partition(A) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched (in-flight reads keep their fate)
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ A # {} /\ A # Procs
     /\ down' = down \cup {x \in Procs \X Procs : (x[1] \in A) # (x[2] \in A)}
     /\ UNCHANGED <<up, paused, promised, maxTok, leader, term, ltok, reqs, pending, tok,
                    myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
                    toAck, grants, rq, issued, decisions, told>>
-    /\ lastEv' = [event |-> "Fault", cell |-> "F1.2", action |-> "partition", sideA |-> A]
+    /\ lastEv' = <<[event |-> "Fault", cell |-> "F1.2", action |-> "partition", sideA |-> A]>>
 
 \* derives: F2.1; format v4 cut, L1, L2 -- partial partition: each listed link goes down in both
 \* directions (L is the listed pairs, already resolved, self-pairs removed)
 Cut(L) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ down' = down \cup BothWays(L)
     /\ UNCHANGED <<up, paused, promised, maxTok, leader, term, ltok, reqs, pending, tok,
                    myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
                    toAck, grants, rq, issued, decisions, told>>
-    /\ lastEv' = [event |-> "Fault", cell |-> "F2.1", action |-> "cut", pairs |-> L, links |-> BothWays(L)]
+    /\ lastEv' = <<[event |-> "Fault", cell |-> "F2.1", action |-> "cut", pairs |-> L, links |-> BothWays(L)]>>
 
 \* derives: F2.2; format v4 drop, L1, L2 -- simplex link failure: each listed link goes down in
 \* the listed direction only (L is already resolved, self-pairs removed)
 Drop(L) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ down' = down \cup L
     /\ UNCHANGED <<up, paused, promised, maxTok, leader, term, ltok, reqs, pending, tok,
                    myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
                    toAck, grants, rq, issued, decisions, told>>
-    /\ lastEv' = [event |-> "Fault", cell |-> "F2.2", action |-> "drop", pairs |-> L, links |-> L]
+    /\ lastEv' = <<[event |-> "Fault", cell |-> "F2.2", action |-> "drop", pairs |-> L, links |-> L]>>
 
 \* derives: F1.2, F2.1, F2.2; format v4 L2 -- a heal, whichever cell it names, restores every
 \* link; lost messages stay lost
 Heal(cell) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ down' = {}
     /\ UNCHANGED <<up, paused, promised, maxTok, leader, term, ltok, reqs, pending, tok,
                    myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
                    toAck, grants, rq, issued, decisions, told>>
-    /\ lastEv' = [event |-> "Fault", cell |-> cell, action |-> "heal", target |-> "all"]
+    /\ lastEv' = <<[event |-> "Fault", cell |-> cell, action |-> "heal", target |-> "all"]>>
 
 \* derives: F1.3 -- holder pause: the client takes no steps; the rest of the world proceeds
 Pause(c) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ up[c] /\ ~paused[c]
     /\ paused' = [paused EXCEPT ![c] = TRUE]
     /\ UNCHANGED <<up, down, promised, maxTok, leader, term, ltok, reqs, pending, tok,
                    myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
                    toAck, grants, rq, issued, decisions, told>>
-    /\ lastEv' = [event |-> "Fault", cell |-> "F1.3", action |-> "pause", target |-> c]
+    /\ lastEv' = <<[event |-> "Fault", cell |-> "F1.3", action |-> "pause", target |-> c]>>
 
 \* derives: F1.3 -- resume as if no time had passed (the client keeps its old token)
 Resume(c) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ paused[c]
     /\ paused' = [paused EXCEPT ![c] = FALSE]
     /\ UNCHANGED <<up, down, promised, maxTok, leader, term, ltok, reqs, pending, tok,
                    myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
                    toAck, grants, rq, issued, decisions, told>>
-    /\ lastEv' = [event |-> "Fault", cell |-> "F1.3", action |-> "resume", target |-> c]
+    /\ lastEv' = <<[event |-> "Fault", cell |-> "F1.3", action |-> "resume", target |-> c]>>
 
 \* derives: F1.2 -- the side of a partition step, after resolving grantor/holder/rest
-SideOf(st, ng) ==
-    LET a == {Resolve(x, ng) : x \in st.a \ {"rest"}}
-        b == {Resolve(x, ng) : x \in st.b \ {"rest"}} IN
+SideOf(st, ng, nm) ==
+    LET a == {Resolve(x, ng, nm) : x \in st.a \ {"rest"}}
+        b == {Resolve(x, ng, nm) : x \in st.b \ {"rest"}} IN
     IF "rest" \in st.a THEN Procs \ b ELSE a
 
 \* derives: F2.1, F2.2; format v4 L1 -- the names in a step's link list (both ends of every pair)
@@ -662,62 +1125,70 @@ LinkNames(st) == {e[1] : e \in st.l} \cup {e[2] : e \in st.l}
 
 \* derives: F2.1, F2.2; format v4 L1 -- the directed links a `cut`/`drop` step names, selectors
 \* resolved, self-pairs removed (a pair whose ends resolve to one process is ignored)
-StepLinks(st, ng) == {<<Resolve(e[1], ng), Resolve(e[2], ng)>> : e \in st.l}
-                     \ {<<p, p>> : p \in Procs}
+StepLinks(st, ng, nm) == {<<Resolve(e[1], ng, nm), Resolve(e[2], ng, nm)>> : e \in st.l}
+                         \ {<<p, p>> : p \in Procs}
 
 \* derives: F1.1, F1.2, F1.3, F2.1, F2.2; format v2 A1, v4 L1 -- every alias in the step resolved
 \* to a process (an alias that names no Grant yet leaves the step waiting; the compiler
 \* rejects the statically detectable cases)
-Resolved(st, ng) == /\ st.p = "none" \/ Resolve(st.p, ng) \in Procs
-                    /\ \A x \in (st.a \cup st.b) \ {"rest"} : Resolve(x, ng) \in Procs
-                    /\ \A x \in LinkNames(st) : Resolve(x, ng) \in Procs
+Resolved(st, ng, nm) == /\ st.p = "none" \/ Resolve(st.p, ng, nm) \in Procs
+                        /\ \A x \in (st.a \cup st.b) \ {"rest"} : Resolve(x, ng, nm) \in Procs
+                        /\ \A x \in LinkNames(st) : Resolve(x, ng, nm) \in Procs
 
-\* derives: C1.2, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2; format v2 A1, T3, v4 cut, drop -- the effect of one schedule step
+\* derives: C1.2, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, F3.1, F3.2, F3.3; format v2 A1, T3, v4 cut, drop, v5 -- the effect of one schedule step
 \* (each workload action's own guard makes it wait as T3 requires)
-DoStep(st, ng) ==
-    /\ Resolved(st, ng)
-    /\ CASE st.kind = "request"   -> DoRequest(Resolve(st.p, ng))
-      [] st.kind = "write"     -> DoWrite(Resolve(st.p, ng), st.v, st.stale)
-      [] st.kind = "read"      -> DoRead(Resolve(st.p, ng), st.stale)   \* derives: C2.1, C2.2
-      [] st.kind = "crash"     -> Crash(Resolve(st.p, ng))
-      [] st.kind = "restart"   -> Restart(Resolve(st.p, ng))
-      [] st.kind = "partition" -> Partition(SideOf(st, ng))
+DoStep(st, ng, nm) ==
+    /\ Resolved(st, ng, nm)
+    /\ CASE st.kind = "request"   -> DoRequest(Resolve(st.p, ng, nm))
+      [] st.kind = "write"     -> DoWrite(Resolve(st.p, ng, nm), st.v, st.stale)
+      [] st.kind = "read"      -> DoRead(Resolve(st.p, ng, nm), st.stale)   \* derives: C2.1, C2.2
+      [] st.kind = "crash"     -> Crash(Resolve(st.p, ng, nm))
+      [] st.kind = "restart"   -> Restart(Resolve(st.p, ng, nm))
+      [] st.kind = "partition" -> Partition(SideOf(st, ng, nm))
       [] st.kind = "heal"      -> Heal(st.cell)                          \* derives: F1.2, F2.1, F2.2
-      [] st.kind = "cut"       -> Cut(StepLinks(st, ng))                \* derives: F2.1
-      [] st.kind = "drop"      -> Drop(StepLinks(st, ng))               \* derives: F2.2
-      [] st.kind = "pause"     -> Pause(Resolve(st.p, ng))
-      [] st.kind = "resume"    -> Resume(Resolve(st.p, ng))
+      [] st.kind = "cut"       -> Cut(StepLinks(st, ng, nm))            \* derives: F2.1
+      [] st.kind = "drop"      -> Drop(StepLinks(st, ng, nm))           \* derives: F2.2
+      [] st.kind = "pause"     -> Pause(Resolve(st.p, ng, nm))
+      [] st.kind = "resume"    -> Resume(Resolve(st.p, ng, nm))
+      [] st.kind = "reconfig"  -> DoReconfig(st.op, st.rid, st.mem, Resolve(st.p, ng, nm))   \* derives: F3.1
+      [] st.kind = "clock"     -> ClockStep(Resolve(st.p, ng, nm), st.s)                   \* derives: F3.2
+      [] st.kind = "amnesia"   -> AmnesicRestart(Resolve(st.p, ng, nm))                     \* derives: F3.3
 
 \* derives: F1.1; format v2.1 A1 -- candidate resolutions of `non-grantor` for step st
-\* format v2.1 T1: the next trigger is offered lastEv', the event this step's own action emitted
+\* format v2.1 T1: the next trigger is offered lastEv', the events this step's own action emitted
 \* synchronously, so a step may be triggered by its predecessor's own event.
 \* format v2.1 A1: `non-grantor` is explored over every candidate (the lease nodes other than
 \* grantor that were up when the trigger fired); `restart: non-grantor` names the node the most
 \* recent `crash: non-grantor` crashed, whether or not it is a non-grantor now (format v2.2 A1).
 \* derives: F2.1, F2.2; format v4 L1 -- `non-grantor` may also stand in a link
+\* derives: F3.3; format v5 R3 -- an amnesic restart of `non-grantor` is a restart (names ngDown)
 NGChoices(st) ==
     IF "non-grantor" \notin ({st.p} \cup st.a \cup st.b \cup LinkNames(st)) THEN {"none"}
-    ELSE IF st.kind = "restart" THEN {ngDown}
+    ELSE IF st.kind \in {"restart", "amnesia"} THEN {ngDown}
     ELSE trigNG
+\* derives: F3.1; format v5 R1 -- candidate resolutions of `non-member` (every one is explored)
+NMChoices(st) ==
+    IF "non-member" \notin ({st.p} \cup st.a \cup st.b \cup LinkNames(st)) THEN {"none"} ELSE trigNM
 
 \* derives: F1.1, F1.2, F1.3; format v2.1 T1, A1 -- apply step pc once its trigger has held; arm the next trigger
 ScheduleStep ==
     /\ pc <= Len(Steps)
     /\ fired
-    /\ \E ng \in NGChoices(Steps[pc]) :
-        /\ DoStep(Steps[pc], ng)
+    /\ \E ng \in NGChoices(Steps[pc]), nm \in NMChoices(Steps[pc]) :
+        /\ DoStep(Steps[pc], ng, nm)
         /\ ngDown' = IF Steps[pc].kind = "crash" /\ Steps[pc].p = "non-grantor" THEN ng ELSE ngDown
     /\ pc' = pc + 1
     /\ fired' = (IsStart(Trig(pc + 1)) \/ Matches(Trig(pc + 1), lastEv'))
     /\ trigG' = IF fired' THEN LastGrant ELSE trigG
     /\ trigNG' = IF fired' THEN {n \in Nodes : up'[n]} \ {LastGrant.node} ELSE trigNG
+    /\ trigNM' = IF fired' THEN NonMembers ELSE trigNM
 
 \* ===========================================================================
-\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2
+\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, C3.x, F3.x
 Protocol ==
     \/ \E n \in Nodes : Elect(n) \/ StepDown(n)
     \/ \E n \in Nodes : CheckQuorum(n)   \* derives: C1.4, F2.2
-    \/ \E n, q \in Nodes : Join(n, q)
+    \/ \E n \in Nodes : Join(n)
     \/ \E n \in Nodes, c \in Clients : Grant(n, c)
     \/ \E n \in Nodes, c \in Clients : Resend(n, c)   \* derives: C1.4, F2.2
     \/ \E m \in grantMsgs : RecvGrant(m)
@@ -727,6 +1198,10 @@ Protocol ==
     \/ \E m \in readMsgs, d \in BOOLEAN : StorageRead(m, d)   \* derives: C2.1, C2.2
     \/ \E a \in rToAck : SendReadAck(a)                       \* derives: C2.2
     \/ \E a \in rAckMsgs : RecvReadAck(a)                     \* derives: C2.2
+    \/ \E l, x \in Nodes : Commit(l, x)                       \* derives: C3.1, C3.8, F3.1
+    \/ \E n, m \in Nodes : LearnConfig(n, m)                  \* derives: C3.1, C3.4, F3.1
+    \/ \E m \in rcMsgs : RecvReconfig(m)                      \* derives: C3.4, F3.1
+    \/ \E x \in Nodes : \E a \in owed[x] : ReplyOp(x, a)      \* derives: C3.4, C3.8
 
 \* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
 Next == Protocol \/ ScheduleStep
@@ -736,10 +1211,11 @@ Next == Protocol \/ ScheduleStep
 \* X2: every condition is named, with its justification, in README "Fairness (X2)". Each
 \* protocol action's enablement depends only on the acting process's own state and on
 \* messages over links that are up; none requires hearing a peer over a down link.
+\* X3: the new conditions are named in README "Fairness (X3)", with the same justification.
 Fairness ==
     /\ \A n \in Nodes : WF_vars(Elect(n)) /\ WF_vars(StepDown(n))
     /\ \A n \in Nodes : WF_vars(CheckQuorum(n))  \* derives: C1.4, F2.2 (own timer only)
-    /\ \A n, q \in Nodes : WF_vars(Join(n, q))  \* derives: C1.4, F1.1 (P10 fix)
+    /\ \A n \in Nodes : WF_vars(Join(n))  \* derives: C1.4, F1.1 (P10 fix)
     /\ \A n \in Nodes, c \in Clients : WF_vars(Grant(n, c))
     /\ \A n \in Nodes, c \in Clients : WF_vars(Resend(n, c))  \* derives: C1.4, F2.2 (routing fix)
     /\ WF_vars(\E m \in grantMsgs : RecvGrant(m))
@@ -749,6 +1225,10 @@ Fairness ==
     /\ WF_vars(\E m \in readMsgs : StorageRead(m, FALSE))   \* derives: C2.1, C2.2
     /\ WF_vars(\E a \in rToAck : SendReadAck(a))            \* derives: C2.2
     /\ WF_vars(\E a \in rAckMsgs : RecvReadAck(a))          \* derives: C2.2
+    /\ \A l \in Nodes : WF_vars(\E x \in Nodes : Commit(l, x))        \* derives: C3.4, F3.1
+    /\ \A n \in Nodes : WF_vars(\E m \in Nodes : LearnConfig(n, m))   \* derives: C3.4, C1.4, F3.1
+    /\ WF_vars(\E m \in rcMsgs : RecvReconfig(m))                     \* derives: C3.4
+    /\ \A x \in Nodes : WF_vars(\E a \in owed[x] : ReplyOp(x, a))     \* derives: C3.4
     /\ WF_vars(ScheduleStep)
 
 \* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
@@ -765,9 +1245,25 @@ TypeOK ==
     /\ down \subseteq (Procs \X Procs)   \* derives: F2.1, F2.2
     /\ highest \in Nat
     /\ pc \in 1..(Len(Steps) + 1)
-
-\* derives: C1.1 -- each grant's token is strictly greater than every earlier grant's
-C1_1 == \A i, j \in 1..Len(grants) : i < j => grants[i].token < grants[j].token
+    /\ \A n \in Nodes : Len(cfg[n]) >= 1   \* derives: C3.1
+
+\* derives: C1.1 (contract v3, "C1.1 across configurations") -- v3's reading, without a global order:
+\* (a) no two grants carry one token; (b) a grant under a higher configuration epoch carries a higher
+\* token than every grant under a lower one; (c) each node's counted agreements to grants, in its own
+\* order, carry strictly increasing tokens.
+C1_1 == /\ \A i, j \in 1..Len(grants) : i # j => grants[i].token # grants[j].token
+        /\ \A i, j \in 1..Len(grants) : grants[i].ep < grants[j].ep => grants[i].token < grants[j].token
+        /\ \A n \in Nodes : \A i, j \in 1..Len(agreeLog[n]) : i < j => agreeLog[n][i].t < agreeLog[n][j].t
+
+\* derives: C1.1 (v1 reading, kept; README X3) -- each grant's token is strictly greater than every
+\* earlier grant's in the model's total order. Not v3's reading: a violation of this alone is reported
+\* UNEXPLAINED, not FAIL.
+C1_1order == \A i, j \in 1..Len(grants) : i < j => grants[i].token < grants[j].token
+
+\* derives: C1.1, C3.7 (contract v3 "Grantor term") -- two grants with one term were decided by the same
+\* incarnation of the same node
+TermUnique == \A i, j \in 1..Len(grants) :
+                grants[i].term = grants[j].term => grants[i].node = grants[j].node /\ grants[i].ninc = grants[j].ninc
 
 \* derives: C1.2 -- storage accepts only tokens >= every token it accepted before
 \* (stated over the decision history, not over storage's own ledger variable, so a
@@ -803,14 +1299,87 @@ C2_2 == \A x \in given : \E i \in 1..Len(rdecisions) :
           /\ rdecisions[i].value = x.v
           /\ rdecisions[i].held = x.v
 
-\* derives: C1.4, F2.1, F2.2; format v4 L3 -- C1.4's premise, read literally with "connected" as
-\* failure model v2 defines it (direct, both directions): a majority Q of lease nodes and
+\* derives: C3.1 -- epoch e+1 is committed only after epoch e, and at most one configuration is committed
+\* (decided) for any epoch
+C3_1 == \A i \in 1..Len(commits) :
+          /\ \A j \in 1..Len(commits) : j # i => commits[j].rec.ep # commits[i].rec.ep
+          /\ commits[i].rec.ep >= 1
+          /\ commits[i].rec.ep = 1 \/ \E j \in 1..(i - 1) : commits[j].rec.ep = commits[i].rec.ep - 1
+
+\* derives: C3.7, C3.8, F3.3 -- the nodes of a set of [node, incarnation] agreements; an agreement is
+\* eligible in configuration X given the re-admissions R
+NodesOf(S) == {a[1] : a \in S}
+EligAg(a, X, R) == a[1] \in X.mem /\ (a[2] = 0 \/ a \in R)
+
+\* derives: C3.7 -- every grant is issued under its decider's current configuration, records that
+\* epoch, names the committed configuration of that epoch (not only what the decider believed), and
+\* is counted by eligible agreements, one per node, from a majority of it
+C3_7 == \A i \in 1..Len(grants) :
+          LET g == grants[i]
+              X == GCfgAt(g.ep) IN
+          /\ g.ep = g.cep
+          /\ X # NoConf
+          /\ g.mem = X.mem
+          /\ Cardinality(NodesOf(g.ag)) = Cardinality(g.ag)
+          /\ \A a \in g.ag : EligAg(a, X, GRdm(g.ep, 0))
+          /\ MajOf(NodesOf(g.ag), X.mem)
+
+\* derives: C3.8 -- every decided commit of e+1 is counted by eligible agreements from a majority of the
+\* committed configuration of e and from a majority of its own members (eligibility by re-admissions
+\* other than this commit's), and its members are exactly its request's; an operator is told
+\* success only for a request a commit names, at that commit's epoch, and only after it
+C3_8 == /\ \A i \in 1..Len(commits) :
+             LET c == commits[i]
+                 Old == GCfgAt(c.rec.ep - 1) IN
+             /\ Old # NoConf
+             /\ \A a \in c.ago : EligAg(a, Old, GRdm(c.rec.ep - 1, i))
+             /\ \A a \in c.agn : EligAg(a, c.rec, GRdm(c.rec.ep, i))
+             /\ MajOf(NodesOf(c.ago), Old.mem)
+             /\ MajOf(NodesOf(c.agn), c.rec.mem)
+             /\ c.rec.rid \in DOMAIN ReqSets /\ c.rec.mem = ReqSets[c.rec.rid]
+        /\ \A t \in opTold : t.outcome = "committed" =>
+             \E i \in 1..Len(commits) : commits[i].rec.rid = t.rid /\ commits[i].rec.ep = t.ep
+
+\* derives: C3.4, C3.5 -- the refusal rule, from a refusal's recorded inputs (contract v3 C3.4: invalid,
+\* then busy; superseded when the commit is an input)
+RefuseRule(f) == IF f.mem = {} \/ ~(f.mem \subseteq Nodes) THEN "invalid"
+                 ELSE IF f.pin # "none" THEN "busy"
+                 ELSE IF f.cin >= 0 THEN "superseded" ELSE "none"
+\* derives: C3.5 -- every recorded decision's outcome is the model's fixed rule applied to the inputs
+\* recorded with it, so two decisions of a kind with equal recorded inputs have equal outcomes (in
+\* any two runs). Grants: token = last_token + 1 (client and epoch are inputs). Storage: accept or
+\* serve iff token >= ledger; a served read returns stored_value. Decided commits: epoch =
+\* old_epoch + 1, members = requested_members, readmits = the recorded agreements of incarnations
+\* above 0 in the new membership. Refusals: RefuseRule.
+C3_5 == /\ \A i \in 1..Len(grants) : grants[i].token = grants[i].lt + 1
+        /\ \A i \in 1..Len(decisions) :
+             (decisions[i].outcome = "accept") = (decisions[i].token >= decisions[i].hb)
+        /\ \A i \in 1..Len(rdecisions) :
+             /\ (rdecisions[i].outcome = "served") = (rdecisions[i].token >= rdecisions[i].hb)
+             /\ rdecisions[i].outcome = "served" => rdecisions[i].value = rdecisions[i].held
+        /\ \A i \in 1..Len(commits) :
+             LET c == commits[i] IN
+             /\ c.rec.ep = c.oep + 1
+             /\ c.rec.mem = c.req
+             /\ c.rec.rdm = {a \in c.ago \cup c.agn \cup c.agr : a[2] > 0 /\ a[1] \in c.req}
+        /\ \A i \in 1..Len(refusals) : refusals[i].reason = RefuseRule(refusals[i])
+
+\* derives: C3.4, F3.1 -- no reconfiguration request is pending at a lease node that is up
+NoPending == \A x \in Nodes : up[x] => pend[x] = NoPend
+
+\* derives: C1.4, F2.1, F2.2, C3.7, F3.1, F3.3; format v4 L3, v5 L3 -- C1.4's premise, read literally with
+\* "connected" as failure model v2 defines it (direct, both directions): a majority Q of lease nodes and
 \* storage are up and connected to each other, and connected to client c, which is up and
 \* not paused. Q need not contain the grantor. Under v1 bipartitions this is the old Good(c).
+\* X3 (contract v3 "C1.4 under v3"): the majority is of eligible members of the globally committed
+\* configuration, more than half of whose members are eligible, and no request is pending at an up
+\* lease node. "After the last fault" is the <>[] of C1_4.
 Good(c) == /\ up[Store] /\ up[c] /\ ~paused[c]
            /\ Conn(c, Store)
-           /\ \E Q \in SUBSET Nodes :
-                /\ Majority(Q)
+           /\ NoPending
+           /\ MajOf({q \in Nodes : GElig(q)}, GLatest.mem)
+           /\ \E Q \in SUBSET {q \in Nodes : GElig(q)} :
+                /\ MajOf(Q, GLatest.mem)
                 /\ \A q \in Q : up[q] /\ Conn(q, Store) /\ Conn(q, c)
                 /\ \A q, r \in Q : Conn(q, r)
 
@@ -818,6 +1387,42 @@ Good(c) == /\ up[Store] /\ up[c] /\ ~paused[c]
 \* requester eventually stops waiting (obtains a grant)
 C1_4 == \A c \in Clients : (<>[]Good(c)) => [](pending[c] => <>(~pending[c]))
 
+\* derives: C3.4, F3.1, F3.3; format v5 L3 -- C3.4(b)'s premise for the request pending at x: x is up;
+\* more than half of the globally committed configuration's members are eligible; and x, an eligible
+\* majority of that configuration and an eligible majority of the requested set are up and connected
+\* to each other
+GoodR(x) == pend[x] # NoPend =>
+              /\ up[x]
+              /\ MajOf({q \in Nodes : GElig(q)}, GLatest.mem)
+              /\ \E Q1 \in SUBSET {q \in Nodes : GElig(q) /\ up[q]},
+                    Q2 \in SUBSET {q \in Nodes : EligIn(q, pend[x].mem, GRdm(GLatest.ep, 0)) /\ up[q]} :
+                   /\ MajOf(Q1, GLatest.mem) /\ MajOf(Q2, pend[x].mem)
+                   /\ \A p, q \in Q1 \cup Q2 \cup {x} : Conn(p, q)
+\* derives: C3.4 -- an outcome x owes operator o, or has sent it and o has not yet received it
+Owes(x, o) == (\E a \in owed[x] : a.op = o) \/ (\E a \in opMsgs : a.op = o /\ a.x = x)
+\* derives: C3.4 -- (b): a request pending at x under the premise is eventually committed or refused
+\* superseded (its pending ends; this model ends it no other way, amnesia aside); and every
+\* duty to tell: if x stays up and connected to o, o is eventually told what x owes it.
+\* (a)'s `invalid`/`busy` refusals are recorded in the step that records the request.
+C3_4 == /\ \A x \in Receivers : (<>[]GoodR(x)) => [](pend[x] # NoPend => <>(pend[x] = NoPend))
+        /\ \A x \in Receivers, o \in Ops :
+             (<>[](up[x] /\ Conn(x, o))) => [](Owes(x, o) => <>~Owes(x, o))
+
+\* derives: C1.4, C3.4 (README X3 "Liveness, checked at terminal states") -- the state graph of this model
+\* has no cycle but stuttering (Acyclic, checked on every run). Then every weakly fair behaviour
+\* ends stuttering in a state where no step is enabled, and C1_4 and C3_4 hold iff at every such
+\* reachable state each premise implies its conclusion. These invariants say that; ENABLED is
+\* evaluated only where a premise holds and its conclusion does not.
+C1_4T == (\E c \in Clients : Good(c) /\ pending[c]) => ENABLED <<Next>>_vars
+\* derives: C3.4
+C3_4T == (\/ \E x \in Receivers : GoodR(x) /\ pend[x] # NoPend
+          \/ \E x \in Receivers, o \in Ops : up[x] /\ Conn(x, o) /\ Owes(x, o)) => ENABLED <<Next>>_vars
+\* derives: C1.4, C3.4 -- the spec without fairness, for the acyclicity check
+SpecNF == Init /\ [][Next]_vars
+\* derives: C1.4, C3.4 -- every behaviour eventually stops changing the fingerprinted state, i.e. the
+\* state graph has no cycle other than stuttering (a violation is a lasso through a real cycle)
+Acyclic == <>[][UNCHANGED View]_View
+
 \* derives: C1.1, C1.4 -- bound check: no election ever reaches the last allowed term,
 \* so MaxTerm never constrains a behaviour (run.sh reports a violation as UNEXPLAINED)
 TermHeadroom == \A n \in Nodes : promised[n] < MaxTerm
@@ -827,7 +1432,7 @@ TermHeadroom == \A n \in Nodes : promised[n] < MaxTerm
 \* and no client waiting for a grant, with crashed and paused processes not counted
 \* (a message counts as in flight when its receiver is running)
 Active(c) == up[c] /\ ~paused[c]
-\* derives: F1.1, F1.2, F1.3; format v2 E1
+\* derives: F1.1, F1.2, F1.3, C3.4; format v2 E1, v5 E1
 Quiescent == /\ \A m \in grantMsgs : ~Active(m.c)
              /\ writeMsgs = {} \/ ~up[Store]
              /\ \A a \in ackMsgs : ~Active(a.c)
@@ -836,6 +1441,10 @@ Quiescent == /\ \A m \in grantMsgs : ~Active(m.c)
              /\ readMsgs = {} \/ ~up[Store]                      \* derives: C2.1; format v2 E1
              /\ \A a \in rAckMsgs : ~Active(a.c)                  \* derives: C2.2; format v2 E1
              /\ \A a \in rToAck : ~up[Store] \/ ~Active(a.c)      \* derives: C2.2; format v2 E1
+             /\ \A m \in rcMsgs : ~up[m.to]                       \* derives: C3.4; format v5 E1
+             /\ NoPending                                         \* derives: C3.4; format v5 E1
+             /\ \A x \in Nodes : up[x] => \A a \in owed[x] : ~Link(x, a.op)   \* derives: C3.4; v5 E1
+             /\ opMsgs = {}                                       \* derives: C3.4; format v5 E1
 \* derives: F1.1, F1.2, F1.3; format v2 E1 -- the run has reached its end: every step applied,
 \* and either the end trigger fired (armed when the last step was taken) or, for
 \* `end: quiescent`, the state is quiescent

````
## U02: `model/compile.py`
````diff
diff --git a/model/compile.py b/model/compile.py
index 2de1525..b36e1bf 100644
--- a/model/compile.py
+++ b/model/compile.py
@@ -1,12 +1,14 @@
 #!/usr/bin/env python3
-# derives: F1.1, F1.2, F1.3, F2.1, F2.2, C2.1, C2.2; format v4 (cut, drop, L1, L2); v3 (read); v2.1 T1, A1; v2 T2, T3, A2, E1, E2 (schedule compiler)
-"""Compile a fault schedule (testbed/schedule-format.md v2) into a TLC model.
+# derives: F1.1, F1.2, F1.3, F2.1, F2.2, F3.1, F3.2, F3.3, C2.1, C2.2, C3.4, C3.8; format v5 (config, operators, lifetime, reconfigure, clock, restart amnesia, R1-R3, L3, T1, E1); v4 (cut, drop, L1, L2); v3 (read); v2.1 T1, A1; v2 T2, T3, A2, E1, E2 (schedule compiler)
+"""Compile a fault schedule (testbed/schedule-format.md, v5 addendum included) into a TLC model.
 
 Usage: compile.py <schedule.yaml> <outdir> [--lease <Lease.tla>]
 
 Writes into <outdir>:
   MC.tla        EXTENDS Lease; defines the constants (processes, Steps, EndTrig, bounds)
-  MC.cfg        safety invariants C1_1..C1_3 and liveness C1_4 (the checking run)
+  MC.cfg        every clause invariant and the liveness properties (the checking run)
+  MC_<P>.cfg    one property alone (C1_4, C3_4), to attribute a liveness violation
+  MC_only.cfg   written by compile_schedule(..., only=<clause>) for a mutation run
   Witness.cfg   invariant NotEnded: a violation is a trace that completes the schedule
   Done.cfg      invariant NotDone: weaker witness (end trigger fired, not quiescent)
   schedule.json the parsed schedule, for the exporter
@@ -18,39 +20,62 @@ A schedule naming an action outside the failure model is rejected (exit 2).
 import json
 import shutil
 import sys
+from fractions import Fraction
 from pathlib import Path
 
 import yaml
 
-# derives: F1.1, F1.2, F1.3, F2.1, F2.2 -- the only fault actions the failure model contains, by cell
+# derives: F1.1, F1.2, F1.3, F2.1, F2.2, F3.1, F3.2, F3.3 -- the only fault actions the failure model contains, by cell
 FAULTS = {
     "F1.1": {"crash", "restart"},
     "F1.2": {"partition", "heal"},
     "F1.3": {"pause", "resume"},
     "F2.1": {"cut", "heal"},     # derives: F2.1; format v4 cut, L2 (a heal under any cell restores every link)
     "F2.2": {"drop", "heal"},    # derives: F2.2; format v4 drop, L2
+    "F3.1": {"reconfigure"},     # derives: F3.1; format v5 R1 (a request, not a fault)
+    "F3.2": {"clock"},           # derives: F3.2; format v5 R2
+    "F3.3": {"restart"},         # derives: F3.3; format v5 R3 (with amnesia: true)
 }
-# derives: C1.1, C1.2, C1.3 -- observable events of contract/v1.md, plus `start`
+# derives: F3.1, F3.2, F3.3; format v5 -- the extra keys each v5 action takes
+V5_KEYS = {"reconfigure": {"to", "id", "operator"}, "clock": {"step"}, "restart": {"amnesia"}}
+# derives: C1.1, C1.2, C1.3, C3.x -- observable events of the contract, plus `start`
 EVENTS = {"start", "Request", "Grant", "WriteAttempt", "WriteAccept", "WriteReject", "WriteAck",
           # derives: C2.1, C2.2; format v3 -- contract v2's read events
-          "ReadAttempt", "ReadAccept", "ReadReject", "ReadAck"}
-# derives: C1.1, C1.2, C1.3 -- fields each event carries (filters must name one of these)
+          "ReadAttempt", "ReadAccept", "ReadReject", "ReadAck",
+          # derives: C3.1, C3.4, C3.7, C3.8, F3.x; format v5 -- contract v3's events, and Fault records
+          "ReconfigSend", "ReconfigRequest", "ConfigCommitted", "ReconfigRefused", "ReconfigAck",
+          "Agree", "Agreed", "Fault"}
+# derives: C1.1, C1.2, C1.3, C3.x -- fields each event carries (filters must name one of these)
 EVENT_FIELDS = {
     "Request": {"client", "key"},
-    "Grant": {"client", "key", "token", "lifetime", "grantor_term"},
+    "Grant": {"client", "key", "token", "lifetime", "grantor_term", "config_epoch"},
     "WriteAttempt": {"client", "key", "token", "value", "grantor_term"},
     "WriteAccept": {"key", "token", "highest_before", "grantor_term"},
     "WriteReject": {"key", "token", "highest_before", "grantor_term"},
-    "WriteAck": {"client", "key", "token", "outcome"},
+    "WriteAck": {"client", "key", "token", "outcome", "grantor_term"},
     # derives: C2.1, C2.2; format v3
     "ReadAttempt": {"client", "key", "token", "grantor_term"},
     "ReadAccept": {"key", "token", "highest_before", "grantor_term", "value"},
     "ReadReject": {"key", "token", "highest_before", "grantor_term"},
-    "ReadAck": {"client", "key", "token", "outcome", "value"},
+    "ReadAck": {"client", "key", "token", "outcome", "value", "grantor_term"},
+    # derives: C3.1, C3.4, C3.8, F3.1; format v5 (triggers on the new events)
+    "ReconfigSend": {"operator", "request_id", "to", "members"},
+    "ReconfigRequest": {"node", "operator", "request_id", "members"},
+    "ConfigCommitted": {"node", "epoch", "members", "request_id", "decided"},
+    "ReconfigRefused": {"node", "request_id", "reason", "epoch"},
+    "ReconfigAck": {"operator", "request_id", "outcome", "epoch"},
+    "Agree": set(),     # no filters: in this model an agreement is recorded in the step that counts it
+    "Agreed": set(),
+    # derives: F1.1-F3.3; observe v1 "a fault step is recorded as Fault"; format v5 T1 -- a Fault filter
+    # names the cell, amnesia, or the action with its target (`restart: n2`)
+    "Fault": {"cell", "amnesia", "crash", "restart", "pause", "resume", "clock"},
 }
-# derives: C1.3, C2.2; format v3 -- outcome values per ack event
-OUTCOMES = {"WriteAck": ("accepted", "rejected"), "ReadAck": ("served", "rejected")}
-ALIASES = {"grantor", "holder", "rest", "non-grantor"}   # non-grantor: format v2.1 A1
+# derives: C1.3, C2.2, C3.4; format v3, v5 -- outcome values per ack event
+OUTCOMES = {"WriteAck": ("accepted", "rejected"), "ReadAck": ("served", "rejected"),
+            "ReconfigAck": ("committed", "refused")}
+REASONS = ("invalid", "busy", "superseded")   # derives: C3.4
+ALIASES = {"grantor", "holder", "rest", "non-grantor", "non-member"}   # non-grantor: v2.1 A1; non-member: v5 R1
+MAX_LEASE = 6   # derives: F3.1 -- the brief: "any number the schedules name, up to six"
 
 
 class ScheduleError(Exception):
@@ -75,7 +100,7 @@ def tla(v):
 
 
 def trigger(t, procs):
-    # derives: F1.1, F1.2, F1.3 -- a trigger is `start` or {event: E, field: value, ...}
+    # derives: F1.1, F1.2, F1.3, F3.x -- a trigger is `start` or {event: E, field: value, ...}
     if t == "start":
         return {"event": "start"}
     if not isinstance(t, dict) or "event" not in t:
@@ -88,11 +113,23 @@ def trigger(t, procs):
         if k == "event":
             continue
         if k not in EVENT_FIELDS[ev]:
-            raise ScheduleError(f"event {ev} has no field {k!r}")
+            raise ScheduleError(f"event {ev} has no field {k!r} the model can filter on")
         if k == "client" and v not in procs["clients"]:
             raise ScheduleError(f"unknown client {v!r}")
         if k == "outcome" and v not in OUTCOMES[ev]:
             raise ScheduleError(f"{ev} outcome must be one of {OUTCOMES[ev]}, got {v!r}")
+        if k == "reason" and v not in REASONS:
+            raise ScheduleError(f"reason must be one of {REASONS}, got {v!r}")
+        if k == "members":
+            # derives: C3.8 -- members compared as a set
+            if not isinstance(v, list):
+                raise ScheduleError("members filter must be a list")
+            out[k] = set(map(str, v))
+            continue
+        if ev == "Fault" and k in ("crash", "restart", "pause", "resume", "clock"):
+            # the model's Fault record names the action and its target
+            out["action"], out["target"] = k, v
+            continue
         out[k] = v
     return out
 
@@ -104,28 +141,73 @@ def proc_name(x, procs, allowed, aliases=("grantor", "holder")):
     raise ScheduleError(f"unknown or ill-typed process {x!r}")
 
 
-def action(d, procs):
-    # derives: C1.2, C1.4, F1.1, F1.2, F1.3 -- one step's action; rejects anything not in the model
+def all_procs(procs):
+    # derives: F1.2, F3.1 -- every process, operators included (format v5 "Processes")
+    return set(procs["lease"]) | set(procs["clients"]) | set(procs["storage"]) | set(procs["operators"])
+
+
+def action(d, procs, lifetime):
+    # derives: C1.2, C1.4, F1.1, F1.2, F1.3, F3.x -- one step's action; rejects anything not in the model
     if not isinstance(d, dict):
         raise ScheduleError(f"bad action {d!r}")
-    allp = set(procs["lease"]) | set(procs["clients"]) | set(procs["storage"])
+    allp = all_procs(procs)
+    lease = set(procs["lease"])
     clients = set(procs["clients"])
     if "cell" in d:
         cell = d["cell"]
         if cell not in FAULTS:
-            raise ScheduleError(f"cell {cell!r} is not in failure-model/v2.md")
+            raise ScheduleError(f"cell {cell!r} is not in failure-model/v3.md")
         keys = set(d) - {"cell"}
-        if len(keys) != 1:
-            raise ScheduleError(f"fault step must name exactly one action: {d!r}")
-        (verb,) = keys
-        if verb not in FAULTS[cell]:
-            raise ScheduleError(f"action {verb!r} does not belong to cell {cell}")
+        verbs = keys & FAULTS[cell]
+        if len(verbs) != 1:
+            raise ScheduleError(f"fault step must name exactly one action of cell {cell}: {d!r}")
+        (verb,) = verbs
+        extra = keys - {verb}
+        allowed_extra = V5_KEYS.get(verb, set()) if cell.startswith("F3") else set()
+        if extra - allowed_extra:
+            raise ScheduleError(f"unexpected keys {sorted(extra - allowed_extra)} in {d!r}")
         arg = d[verb]
+        if cell == "F3.1":
+            # derives: F3.1; format v5 R1 -- members are names (possibly not lease nodes: `invalid`);
+            # `to` is a lease node or grantor, non-grantor, non-member
+            if not isinstance(arg, list):
+                raise ScheduleError("reconfigure needs a list of members")
+            if "to" not in d or "id" not in d:
+                raise ScheduleError("reconfigure needs `to` and `id`")
+            to = d["to"]
+            if to not in lease and to not in ("grantor", "non-grantor", "non-member"):
+                raise ScheduleError(f"R1: `to` must be a lease node or grantor/non-grantor/non-member, got {to!r}")
+            op = d.get("operator", "op")
+            if op not in procs["operators"]:
+                raise ScheduleError(f"unknown operator {op!r}")
+            for x in arg:
+                if x in ALIASES:
+                    raise ScheduleError("R1: members are process names, not selectors")
+            return {"kind": "reconfig", "p": to, "mem": set(map(str, arg)), "rid": str(d["id"]), "op": op}
+        if cell == "F3.2":
+            # derives: F3.2; format v5 R2 -- step x L must be a whole number of ticks
+            step = d.get("step")
+            if not isinstance(step, (int, float)) or isinstance(step, bool):
+                raise ScheduleError("clock needs a numeric `step`")
+            ticks = Fraction(str(step)) * lifetime
+            if ticks.denominator != 1:
+                raise ScheduleError(f"R2: step {step} x lifetime {lifetime} is not a whole number of ticks")
+            return {"kind": "clock", "p": proc_name(arg, procs, allp, ("grantor", "holder", "non-grantor")),
+                    "s": int(ticks), "step": step}
+        if cell == "F3.3":
+            # derives: F3.3; format v5 R3 -- only `restart: <lease node>, amnesia: true`
+            if d.get("amnesia") is not True:
+                raise ScheduleError("F3.3 restart needs `amnesia: true`")
+            p = proc_name(arg, procs, lease, ("grantor", "non-grantor"))
+            return {"kind": "amnesia", "p": p}
         if verb in ("crash", "restart"):
             # derives: F1.1; format v2.1 A1 -- non-grantor is a lease-node selector
-            return {"kind": verb, "p": proc_name(arg, procs, allp, ("grantor", "holder", "non-grantor"))}
+            p = proc_name(arg, procs, allp, ("grantor", "holder", "non-grantor"))
+            if p in procs["operators"]:
+                raise ScheduleError("an operator does not crash (contract v3)")
+            return {"kind": verb, "p": p}
         if verb in ("pause", "resume"):
-            if arg == "grantor" or arg in set(procs["lease"]) | set(procs["storage"]):
+            if arg == "grantor" or arg in lease | set(procs["storage"]) | set(procs["operators"]):
                 raise ScheduleError("A2: only clients can be paused or resumed")
             return {"kind": verb, "p": proc_name(arg, procs, clients, ("holder",))}
         if verb == "heal":
@@ -168,7 +250,7 @@ def action(d, procs):
                     raise ScheduleError("partition without `rest` must name every process")
             return {"kind": "partition", "a": sides[0], "b": sides[1]}
     if set(d) - {"request", "write", "read", "value", "token"}:
-        raise ScheduleError(f"action not in schedule format v1: {d!r}")
+        raise ScheduleError(f"action not in the schedule format: {d!r}")
     if "request" in d:
         if set(d) != {"request"}:
             raise ScheduleError(f"bad request {d!r}")
@@ -194,23 +276,33 @@ def action(d, procs):
 
 
 def static_checks(steps, procs):
-    # derives: F1.1, F1.3; format v2 A1, A2 -- reject what can be decided without running:
+    # derives: F1.1, F1.3, F3.1, F3.3; format v2 A1, A2, v5 R1, R3 -- reject what can be decided without running:
     # an alias used before any Grant can have occurred (no earlier request step), and
     # crash/restart/pause/resume of a process in the wrong state. An alias target is
     # tracked as "maybe" for every process it could denote; the model's own guards make
     # a step that is illegal at run time wait rather than act.
     lease, clients = set(procs["lease"]), set(procs["clients"])
-    allp = lease | clients | set(procs["storage"])
     down, maybe_down = set(), set()          # crashed for sure / possibly crashed
     paused, maybe_paused = set(), set()
     requested = False
     ng_down = False
+    ids = set()
     for i, (a, _) in enumerate(steps, 1):
         names = {a.get("p")} | set(a.get("a", ())) | set(a.get("b", ())) \
             | {x for e in a.get("l", ()) for x in e}   # derives: F2.1, F2.2; format v4 L1 (A1 applies)
         if names & {"grantor", "holder", "non-grantor"} and not requested:
             raise ScheduleError(f"A1: step {i} uses grantor/holder/non-grantor before any Grant can have occurred")
         k, p = a["kind"], a.get("p")
+        if k == "reconfig":
+            # derives: F3.1; format v5 R1 -- request ids are unique within the schedule
+            if a["rid"] in ids:
+                raise ScheduleError(f"R1: request id {a['rid']} used twice")
+            ids.add(a["rid"])
+            continue
+        if k == "clock":
+            continue
+        if k == "amnesia":
+            k = "restart"   # derives: F3.3; format v5 R3 -- an amnesic restart is a restart of a crashed lease node
         # derives: F1.1; format v2.2 A1 (restart: non-grantor is the node the most recent
         # crash: non-grantor crashed; rejected without an earlier one), v2.1 A1, v2 A2 -- restart: non-grantor needs an earlier,
         # not yet restarted, crash: non-grantor; crash: non-grantor is always of an up node
@@ -262,54 +354,92 @@ def static_checks(steps, procs):
 
 
 def tla_step(st, trig):
-    # derives: F1.1, F1.2, F1.3, F2.1, F2.2 -- every step record gets the same fields (TLC compares
-    # them); `l` is the link list of a cut/drop (a set of <<x, y>> pairs), `cell` names the heal's cell
+    # derives: F1.1, F1.2, F1.3, F2.1, F2.2, F3.x -- every step record gets the same fields (TLC compares
+    # them); `l` is the link list of a cut/drop (a set of <<x, y>> pairs), `cell` names the heal's cell;
+    # X3: `mem`, `rid`, `op` for a reconfigure, `s` (ticks) for a clock step
     rec = {"kind": st["kind"], "p": st.get("p", "none"), "v": st.get("v", "none"),
            "stale": st.get("stale", False), "a": set(st.get("a", set())),
-           "b": set(st.get("b", set())), "trig": trig, "cell": st.get("cell", "none")}
+           "b": set(st.get("b", set())), "trig": trig, "cell": st.get("cell", "none"),
+           "mem": set(st.get("mem", set())), "rid": st.get("rid", "none"), "op": st.get("op", "none"),
+           "s": st.get("s", 0)}
     links = "{" + ", ".join(sorted(f"<<{tla(x)}, {tla(y)}>>" for x, y in st.get("l", ()))) + "}"
     return tla(rec)[:-1] + f", l |-> {links}]"
 
 
-def compile_schedule(path, outdir, lease):
-    # derives: F1.1, F1.2, F1.3, F2.1, F2.2
+INVARIANTS = ["TypeOK", "C1_1", "C1_2", "C1_3", "C2_1", "C2_2", "C3_1", "C3_7", "C3_8", "C3_5",
+              "TermUnique", "C1_1order", "TermHeadroom"]   # derives: every clause; README X3 "What is checked"
+
+
+def compile_schedule(path, outdir, lease, only=None):
+    # derives: F1.1, F1.2, F1.3, F2.1, F2.2, F3.1, F3.2, F3.3
+    # only: a mutation run checks this clause alone (an invariant or a property), with TypeOK and
+    # TermHeadroom (README X3, "Mutation runs check the pair's clause")
     doc = yaml.safe_load(Path(path).read_text())
     for k in ("schedule", "processes", "steps", "end"):
         if k not in doc:
             raise ScheduleError(f"missing `{k}`")
-    procs = doc["processes"]
-    if len(procs.get("lease", [])) != 3 or len(procs.get("clients", [])) != 2 \
-            or len(procs.get("storage", [])) != 1:
-        raise ScheduleError("model is fixed at 3 lease nodes, 2 clients, 1 storage")
+    procs = dict(doc["processes"])
+    procs.setdefault("operators", ["op"])           # derives: F3.1; format v5 "Processes"
+    procs.setdefault("config", list(procs.get("lease", [])))
+    procs["clients"] = procs.get("clients", [])
+    nl = len(procs.get("lease", []))
+    if not (1 <= nl <= MAX_LEASE) or len(procs["clients"]) < 1 or len(procs.get("storage", [])) != 1:
+        raise ScheduleError(f"model takes 1 to {MAX_LEASE} lease nodes, at least 1 client, exactly 1 storage")
+    if not procs["config"] or not set(procs["config"]) <= set(procs["lease"]):
+        raise ScheduleError("format v5: `config` must be a non-empty subset of `lease`")
+    names = procs["lease"] + procs["clients"] + procs["storage"] + procs["operators"]
+    if len(set(names)) != len(names) or set(names) & ALIASES:
+        raise ScheduleError("process names must be distinct and not selectors")
+    lifetime = doc.get("lifetime", 1)
+    if not isinstance(lifetime, int) or isinstance(lifetime, bool) or lifetime < 1:
+        raise ScheduleError("format v5: `lifetime` is a positive whole number of ticks")
     steps = []
     for i, s in enumerate(doc["steps"], 1):
         if set(s) != {"at", "do"}:
             raise ScheduleError(f"step {i}: needs exactly `at` and `do`")
-        steps.append((action(s["do"], procs), trigger(s["at"], procs)))
+        steps.append((action(s["do"], procs, lifetime), trigger(s["at"], procs)))
     # derives: format v2 E1 -- `quiescent` or an event trigger
     end = {"event": "quiescent"} if doc["end"] == "quiescent" else trigger(doc["end"], procs)
     static_checks(steps, procs)
     bound = int((doc.get("bound") or {}).get("events", 200))
-    # derives: C1.1, C1.4, F2.1, F2.2 -- cut and drop count as fault steps for the term bound
+    # derives: C1.1, C1.4, F2.1, F2.2, F3.1, F3.2, F3.3 -- cut, drop, reconfigure, clock and amnesic
+    # restarts count as fault steps for the term bound (a removal or a forward clock step may force
+    # an election); this bounds the state space only, and TermHeadroom checks it never binds
     nfault = sum(1 for a, _ in steps
-                 if a["kind"] in ("crash", "partition", "restart", "heal", "cut", "drop"))
+                 if a["kind"] in ("crash", "partition", "restart", "heal", "cut", "drop",
+                                  "reconfig", "clock", "amnesia"))
     max_term = 2 + 2 * nfault          # elections happen only when no reachable leader exists
     max_dups = 1
+    reqsets = {a["rid"]: a["mem"] for a, _ in steps if a["kind"] == "reconfig"}
+    receivers = set()
+    for a, _ in steps:
+        if a["kind"] == "reconfig":
+            receivers |= {a["p"]} if a["p"] in procs["lease"] else set(procs["lease"])
 
     outdir = Path(outdir)
     outdir.mkdir(parents=True, exist_ok=True)
     shutil.copy(lease, outdir / "Lease.tla")
+    reqsets_tla = ("[x \\in {} |-> {}]" if not reqsets else
+                   " @@ ".join(f"({tla(k)} :> {tla(v)})" for k, v in reqsets.items()))
     lines = [
         "---- MODULE MC ----",
         f"\\* derives: {', '.join(map(str, doc.get('derives', [])))} -- compiled from {Path(path).name}",
         "EXTENDS Lease",
-        "\\* derives: C1.1, C1.4",
+        "\\* derives: C1.1, C1.4, F3.1",
         f"MCNodes == {tla(set(procs['lease']))}",
+        "\\* derives: C3.1, C3.7, F3.1; format v5 config",
+        f"MCInit0 == {tla(set(procs['config']))}",
         "\\* derives: C1.2, C1.3, C1.4",
         f"MCClients == {tla(set(procs['clients']))}",
         "\\* derives: C1.2, C1.3",
         f"MCStore == {tla(procs['storage'][0])}",
-        "\\* derives: F1.1, F1.2, F1.3, F2.1, F2.2",
+        "\\* derives: C3.4, C3.8, F3.1; format v5 operators",
+        f"MCOps == {tla(set(procs['operators']))}",
+        "\\* derives: C3.8 -- request id -> requested set",
+        f"MCReqSets == {reqsets_tla}",
+        "\\* derives: C3.4",
+        f"MCReceivers == {tla(receivers)}",
+        "\\* derives: F1.1, F1.2, F1.3, F2.1, F2.2, F3.x",
         "MCSteps == <<",
         ",\n".join("    " + tla_step(a, t) for a, t in steps),
         ">>",
@@ -320,20 +450,39 @@ def compile_schedule(path, outdir, lease):
     (outdir / "MC.tla").write_text("\n".join(lines) + "\n")
     consts = (
         "CONSTANTS\n"
-        "  Nodes <- MCNodes\n  Clients <- MCClients\n  Store <- MCStore\n"
-        '  Key = "k"\n  Lifetime = 1\n  Steps <- MCSteps\n  EndTrig <- MCEnd\n'
+        "  Nodes <- MCNodes\n  Init0 <- MCInit0\n  Clients <- MCClients\n  Store <- MCStore\n"
+        "  Ops <- MCOps\n  ReqSets <- MCReqSets\n  Receivers <- MCReceivers\n"
+        f'  Key = "k"\n  Lifetime = {lifetime}\n  Steps <- MCSteps\n  EndTrig <- MCEnd\n'
         f"  MaxTerm = {max_term}\n  MaxDups = {max_dups}\n"
         "SPECIFICATION Spec\n"
+        "VIEW View\n"   # derives: (bounds) -- README X3 "Bounds": lastEv is not fingerprinted
     )
+    # derives: C1.4, C3.4 (README X3 "Liveness, checked at terminal states") -- the checking run checks every
+    # clause invariant and the terminal-state forms of the liveness clauses; Acyclic.cfg checks, without
+    # fairness, that the state graph has no cycle but stuttering, which makes those forms exact; Live.cfg
+    # is TLC's own liveness check under the fairness of Spec, used only if a cycle is found
+    props = ["C1_4"] + (["C3_4"] if reqsets else [])
+    terms = [p + "T" for p in props]
     (outdir / "MC.cfg").write_text(
-        "\\* derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2\n" + consts +
-        "INVARIANT TypeOK C1_1 C1_2 C1_3 C2_1 C2_2 TermHeadroom\nPROPERTY C1_4\n")
+        "\\* derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8\n" + consts +
+        "INVARIANT " + " ".join(INVARIANTS[:-2] + terms + INVARIANTS[-2:]) + "\n")
+    (outdir / "Acyclic.cfg").write_text(
+        "\\* derives: C1.4, C3.4\n" + consts.replace("SPECIFICATION Spec\n", "SPECIFICATION SpecNF\n") +
+        "PROPERTY Acyclic\n")
+    (outdir / "Live.cfg").write_text("\\* derives: C1.4, C3.4\n" + consts + "".join(f"PROPERTY {p}\n" for p in props))
+    for p in props:
+        (outdir / f"MC_{p}.cfg").write_text("\\* derives: C1.4, C3.4\n" + consts + f"PROPERTY {p}\n")
+    if only is not None:
+        inv = only + "T" if only in ("C1_4", "C3_4") else only
+        (outdir / "MC_only.cfg").write_text(f"\\* derives: {only} (mutation run)\n" + consts +
+                                            f"INVARIANT TypeOK {inv} TermHeadroom\n")
     (outdir / "Witness.cfg").write_text(
         "\\* derives: F1.1, F1.2, F1.3\n" + consts + "INVARIANT NotEnded\n")
     (outdir / "Done.cfg").write_text(
         "\\* derives: F1.1, F1.2, F1.3\n" + consts + "INVARIANT NotDone\n")
     meta = {"schedule": doc["schedule"], "derives": doc.get("derives", []),
             "processes": procs, "bound": bound, "max_term": max_term, "max_dups": max_dups,
+            "lifetime": lifetime, "props": props,
             "steps": [{"do": s["do"], "at": s["at"]} for s in doc["steps"]], "end": doc["end"]}
     (outdir / "schedule.json").write_text(json.dumps(meta, indent=1, default=list))
     return meta

````
## U03: `model/export.py`
````diff
diff --git a/model/export.py b/model/export.py
index 4604e28..9f6ae05 100644
--- a/model/export.py
+++ b/model/export.py
@@ -1,13 +1,15 @@
 #!/usr/bin/env python3
-# derives: C1.1, C1.2, C1.3, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2 (trace exporter: TLC trace -> observe/schema.md records, incl. v2, v3 and v4 addenda)
+# derives: C1.1, C1.2, C1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F1.1, F1.2, F1.3, F2.1, F2.2, F3.1, F3.2, F3.3 (trace exporter: TLC trace -> observe/schema.md records, incl. v2, v3, v4 and v5 addenda)
 """Turn a TLC trace (witness or counterexample) into observe/schema.md records.
 
 Usage: export.py <tlc-output.txt> <schedule.json> <out.jsonl> <run-id>
 
-Reads the `lastEv` variable of every state in the first trace printed by TLC.
-Each observable event becomes one JSON line; `Fault` steps are emitted from
-proc "env". Internal protocol steps (elections, deliveries) are not observable
-events and are not emitted. Lines are written in trace order; `seq` is per process.
+Reads the `lastEv` variable of every state in the first trace printed by TLC (X3: a
+sequence of the events the step emitted; a grant or commit step carries the agreements it
+counted, which become Agree and Agreed records). Each observable event becomes one JSON
+line; `Fault` steps are emitted from proc "env". Internal protocol steps (elections,
+deliveries) are not observable events and are not emitted. Lines are written in trace
+order; identity is (proc, inc, seq) per observe v5, seq from 0 in each incarnation.
 
 Exit status: 0 if every WriteAccept/WriteReject can be traced to a Grant and its
 grantor_term (the schema's provenance question), 3 if not, 4 if no trace found.
@@ -164,38 +166,58 @@ CONTRACT_FIELDS = {
     "WriteAttempt": ["client", "key", "token", "value", "grantor_term"],
     "WriteAccept": ["key", "token", "highest_before", "grantor_term"],
     "WriteReject": ["key", "token", "highest_before", "grantor_term"],
-    "WriteAck": ["client", "key", "token", "outcome"],
+    # derives: C3.x; observe v5 -- "the eight write and read events above also carry grantor_term"
+    "WriteAck": ["client", "key", "token", "outcome", "grantor_term"],
     # derives: C2.1, C2.2; observe v2 addendum -- read events, fields as their write counterparts
     "ReadAttempt": ["client", "key", "token", "grantor_term"],
     "ReadAccept": ["key", "token", "highest_before", "value", "grantor_term"],
     "ReadReject": ["key", "token", "highest_before", "grantor_term"],
-    "ReadAck": ["client", "key", "token", "outcome"],   # + value when served
+    "ReadAck": ["client", "key", "token", "outcome", "grantor_term"],   # + value when served
 }
 
 
+def tset(v):
+    # derives: C3.x -- a TLA+ set as printed by TLC ("set", items) -> sorted list
+    if isinstance(v, tuple) and v and v[0] == "set":
+        return sorted(v[1], key=lambda x: json.dumps(x))
+    return v
+
+
 def export(tlc_text, sched, run):
-    # derives: C1.1, C1.2, C1.3, F1.1, F1.2, F1.3
+    # derives: C1.1, C1.2, C1.3, F1.1, F1.2, F1.3, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3; observe v5
     states, loop = trace_states(tlc_text)
     if not states:
         return None, ["no trace in TLC output"], loop
     procs = sched["processes"]
-    allp = set(procs["lease"]) | set(procs["clients"]) | set(procs["storage"])
+    lease = set(procs["lease"])
+    init0 = sorted(procs.get("config", procs["lease"]))
+    allp = lease | set(procs["clients"]) | set(procs["storage"]) | set(procs.get("operators", ["op"]))
     storage = procs["storage"][0]
+    L = sched.get("lifetime", 1)
+    # derives: observe v5 "Identity" -- (proc, inc, seq): a lease node's inc is its incarnation, any
+    # other process's the number of times it has restarted; seq restarts at 0 in each incarnation and
+    # continues across a lease node's ordinary restart
+    incs = {p: 0 for p in allp}
     seqs, out = {}, []
     last = {}  # index for causes
     problems = []
 
-    def emit(proc, event, fields, causes):
-        seqs[proc] = seqs.get(proc, 0) + 1
-        rec = {"proc": proc, "seq": seqs[proc], "event": event}
+    def emit(proc, event, fields, causes, inputs=None, inc=None):
+        i = incs.get(proc, 0) if inc is None else inc
+        s = seqs.get((proc, i), -1) + 1
+        seqs[(proc, i)] = s
+        rec = {"proc": proc, "inc": i, "seq": s, "event": event}
         rec.update(fields)
-        rec["causes"] = causes
+        if inputs is not None:
+            rec["inputs"] = inputs
+        rec["causes"] = [c for c in causes if c]
         rec["run"] = run
         rec["side"] = "model"
         out.append(rec)
-        return {"proc": proc, "seq": seqs[proc]}
+        return {"proc": proc, "inc": i, "seq": s}
 
-    dec_att = {}  # storage decision (proc, seq) -> the attempt it names
+    dec_att = {}  # storage decision (proc, inc, seq) -> the attempt it names
+    keyof = lambda r: (r["proc"], r["inc"], r["seq"])
 
     def answers(e, fields, att, d):
         # derives: C1.3, C2.2; observe v3 addendum -- an ack names the attempt it answers,
@@ -205,84 +227,215 @@ def export(tlc_text, sched, run):
             problems.append(f"{e} for {fields.get('client')} token {fields.get('token')} answers no attempt in the trace")
             return
         fields["answers"] = att[0]
-        if d is not None and dec_att.get((d["proc"], d["seq"])) != att[0]:
-            problems.append(f"{e} answers {att[0]} but its causes chain reaches {dec_att.get((d['proc'], d['seq']))}")
+        if d is not None and dec_att.get(keyof(d)) != att[0]:
+            problems.append(f"{e} answers {att[0]} but its causes chain reaches {dec_att.get(keyof(d))}")
+
+    # derives: C3.1; contract v3 "Observable events" -- every initial member's first record is
+    # ConfigCommitted for epoch 0, decided false, request_id null, readmits empty
+    for n in init0:
+        last[("cc", n, 0)] = emit(n, "ConfigCommitted", {"node": n, "epoch": 0, "members": init0,
+                                                         "request_id": None, "readmits": [], "decided": False}, [])
+    decided = {}   # (epoch, request id) -> the decided record
+
+    def rid(x):
+        return None if x == "none" else x
+
+    def agree_and_agreed(decider, pairs, proposal, toward):
+        # derives: C3.7, C3.8; observe v5 -- each agreement: the node's Agree, then the decider's
+        # Agreed naming it, with the majorities it is counted toward
+        refs = []
+        for (q, i) in sorted(pairs):
+            a = emit(q, "Agree", {"node": q, "incarnation": i, "proposal": proposal}, [], inc=i)
+            g = emit(decider, "Agreed", {"decider": decider, "node": q, "node_incarnation": i,
+                                         "proposal": proposal, "counted_toward": toward(q, i)}, [a])
+            refs.append((q, g))
+        return refs
 
     for st in states:
         if "lastEv" not in st:
             continue
-        ev = parse_tla(st["lastEv"])
-        e = ev.get("event")
-        if e in ("Init", "Internal"):
-            continue
-        if e == "Fault":
-            f = {"cell": ev["cell"]}
-            act = ev["action"]
-            if act == "partition":
-                a = sorted(ev["sideA"][1])
-                f["partition"] = [a, sorted(allp - set(a))]
-            elif act == "heal":
-                # derives: F1.2, F2.1, F2.2; observe v4 addendum -- a heal carries links: [] and heal: true
-                f["heal"] = True
-                f["links"] = []
-            elif act in ("cut", "drop"):
-                # derives: F2.1, F2.2; observe v4 addendum -- the directed links the step took down,
-                # selectors resolved and self-pairs removed (a cut of [a, b] is [a, b] and [b, a])
-                f[act] = sorted([list(x) for x in ev["pairs"][1]])
-                f["links"] = sorted([list(x) for x in ev["links"][1]])
-            else:
-                f[act] = ev["target"]
-            emit("env", "Fault", f, [])
-            continue
-        fields = {k: ev[k] for k in CONTRACT_FIELDS[e]}
-        if e == "ReadAck" and ev["outcome"] == "served":
-            fields["value"] = ev["value"]   # derives: C2.2 -- value only on a served ReadAck
-        if e == "Request":
-            ref = emit(ev["client"], e, fields, [])
-            last[("req", ev["client"])] = ref
-        elif e == "Grant":
-            causes = [last[("req", ev["client"])]] if ("req", ev["client"]) in last else []
-            ref = emit(ev["node"], e, fields, causes)
-            last[("grant", ev["token"], ev["grantor_term"])] = ref
-        elif e == "WriteAttempt":
-            g = last.get(("grant", ev["token"], ev["grantor_term"]))
-            ref = emit(ev["client"], e, fields, [g] if g else [])
-            last[("att", ev["client"], ev["token"], ev["value"])] = (ref, g)
-        elif e in ("WriteAccept", "WriteReject"):
-            a = last.get(("att", ev["client"], ev["token"], ev["value"]))
-            ref = emit(storage, e, fields, [a[0]] if a else [])
-            last[("dec", ev["client"], ev["token"], ev["value"])] = ref
-            dec_att[(ref["proc"], ref["seq"])] = a[0] if a else None
-            if not a or not a[1]:
-                problems.append(f"{e} seq {ref['seq']} (token {ev['token']}) has no traceable Grant")
-        elif e == "ReadAttempt":
-            # derives: C2.1; observe v2 -- a ReadAttempt names the Grant whose token it uses
-            g = last.get(("grant", ev["token"], ev["grantor_term"]))
-            ref = emit(ev["client"], e, fields, [g] if g else [])
-            last[("ratt", ev["client"], ev["rid"])] = (ref, g)
-        elif e in ("ReadAccept", "ReadReject"):
-            # derives: C2.1, C2.2; observe v2 -- a read decision names the ReadAttempt
-            a = last.get(("ratt", ev["client"], ev["rid"]))
-            ref = emit(storage, e, fields, [a[0]] if a else [])
-            last[("rdec", ev["client"], ev["rid"])] = ref
-            dec_att[(ref["proc"], ref["seq"])] = a[0] if a else None
-            if not a or not a[1]:
-                problems.append(f"{e} seq {ref['seq']} (token {ev['token']}) has no traceable Grant")
-        elif e == "ReadAck":
-            # derives: C2.2; observe v2 -- a ReadAck names the storage decision
-            d = last.get(("rdec", ev["client"], ev["rid"]))
-            att = last.get(("ratt", ev["client"], ev["rid"]))
-            answers(e, fields, att, d)
-            ref = emit(ev["client"], e, fields, [d] if d else [])
-            if not d and ev["outcome"] == "served":
-                problems.append(f"ReadAck served at {ref} has no storage decision")
-        elif e == "WriteAck":
-            d = last.get(("dec", ev["client"], ev["token"], ev["value"]))
-            att = last.get(("att", ev["client"], ev["token"], ev["value"]))
-            answers(e, fields, att, d)
-            ref = emit(ev["client"], e, fields, [d] if d else [])
-            if not d and ev["outcome"] == "accepted":
-                problems.append(f"WriteAck accepted at {ref} has no storage decision")
+        evs = parse_tla(st["lastEv"])
+        for ev in evs:
+            e = ev.get("event")
+            if e == "Init":
+                continue
+            if e == "Fault":
+                f = {"cell": ev["cell"]}
+                act = ev["action"]
+                if act == "partition":
+                    a = sorted(tset(ev["sideA"]))
+                    f["partition"] = [a, sorted(allp - set(a))]
+                elif act == "heal":
+                    # derives: F1.2, F2.1, F2.2; observe v4 addendum -- a heal carries links: [] and heal: true
+                    f["heal"] = True
+                    f["links"] = []
+                elif act in ("cut", "drop"):
+                    # derives: F2.1, F2.2; observe v4 addendum -- the directed links the step took down,
+                    # selectors resolved and self-pairs removed (a cut of [a, b] is [a, b] and [b, a])
+                    f[act] = sorted([list(x) for x in tset(ev["pairs"])])
+                    f["links"] = sorted([list(x) for x in tset(ev["links"])])
+                elif act == "clock":
+                    # derives: F3.2; observe v5 -- clock: proc, step (signed, in units of L)
+                    s = ev["step"] / L
+                    f["clock"] = ev["target"]
+                    f["step"] = int(s) if s == int(s) else s
+                else:
+                    f[act] = ev["target"]
+                    if ev.get("amnesia"):
+                        f["amnesia"] = True   # derives: F3.3; observe v5
+                emit("env", "Fault", f, [])
+                # derives: observe v5 "Identity" -- incarnations
+                if act == "restart" and ev.get("amnesia"):
+                    incs[ev["target"]] += 1
+                elif act == "restart" and ev["target"] not in lease:
+                    incs[ev["target"]] += 1
+                continue
+            if e == "Grant":
+                # derives: C1.1, C3.5, C3.7; observe v5 -- the agreements it counted, then the decision with its inputs
+                n, ep = ev["node"], ev["config_epoch"]
+                prop = {"client": ev["client"], "token": ev["token"], "lifetime": ev["lifetime"], "config_epoch": ep}
+                refs = agree_and_agreed(n, [tuple(x) for x in tset(ev["agreed"])], prop, lambda q, i: [ep])
+                fields = {k: ev[k] for k in CONTRACT_FIELDS[e]}
+                fields["config_epoch"] = ep
+                inputs = [{"name": "agreed", "value": q, "ref": g} for q, g in refs]
+                inputs += [{"name": "members", "value": sorted(tset(ev["members"]))},
+                           {"name": "config_epoch", "value": ep},
+                           {"name": "grantor_term", "value": ev["grantor_term"]},
+                           {"name": "last_token", "value": ev["last_token"]}]
+                causes = [last.get(("req", ev["client"]))]
+                ref = emit(n, e, fields, causes, inputs)
+                last[("grant", ev["token"], ev["grantor_term"])] = ref
+                continue
+            if e == "Commit":
+                # derives: C3.1, C3.5, C3.8, F3.3; observe v5 -- agreements (counted toward e, e+1, both, or
+                # none: re-admission evidence), then the decided ConfigCommitted with its inputs
+                n, rec = ev["node"], ev["rec"]
+                ep, oep = rec["ep"], ev["oep"]
+                mem = sorted(tset(rec["mem"]))
+                ago = {tuple(x) for x in tset(ev["ago"])}
+                agn = {tuple(x) for x in tset(ev["agn"])}
+                agr = {tuple(x) for x in tset(ev["agr"])}
+                prop = {"epoch": ep, "members": mem, "request_id": rec["rid"]}
+                tw = lambda q, i: ([oep] if (q, i) in ago else []) + ([ep] if (q, i) in agn else [])
+                refs = agree_and_agreed(n, ago | agn | agr, prop, tw)
+                rdm = sorted([list(x) for x in tset(rec["rdm"])])
+                inputs = [{"name": "agreed", "value": q, "ref": g} for q, g in refs]
+                inputs += [{"name": "old_members", "value": sorted(tset(ev["old"]))},
+                           {"name": "old_epoch", "value": oep},
+                           {"name": "request_id", "value": rec["rid"]},
+                           {"name": "requested_members", "value": sorted(tset(ev["req"]))}]
+                causes = [last.get(("rreq", n, rec["rid"]))]
+                ref = emit(n, "ConfigCommitted", {"node": n, "epoch": ep, "members": mem, "request_id": rec["rid"],
+                                                  "readmits": rdm, "decided": True}, causes, inputs)
+                decided[(ep, rec["rid"])] = ref
+                last[("cc", n, ep)] = ref
+                continue
+            if e == "Learn":
+                # derives: C3.1; observe v5 -- a learned commit names the decided record (its identity travels
+                # with the configuration in this model)
+                n = ev["node"]
+                for rec in ev["recs"]:
+                    ep = rec["ep"]
+                    ref = emit(n, "ConfigCommitted", {"node": n, "epoch": ep, "members": sorted(tset(rec["mem"])),
+                                                      "request_id": rid(rec["rid"]),
+                                                      "readmits": sorted([list(x) for x in tset(rec["rdm"])]),
+                                                      "decided": False},
+                               [decided.get((ep, rec["rid"]))])
+                    last[("cc", n, ep)] = ref
+                continue
+            if e == "ReconfigSend":
+                last[("rsend", ev["request_id"])] = emit(ev["operator"], e, {
+                    "operator": ev["operator"], "request_id": ev["request_id"], "to": ev["to"],
+                    "members": sorted(tset(ev["members"]))}, [])
+                continue
+            if e == "ReconfigRequest":
+                n = ev["node"]
+                last[("rreq", n, ev["request_id"])] = emit(n, e, {
+                    "operator": ev["operator"], "request_id": ev["request_id"],
+                    "members": sorted(tset(ev["members"]))}, [last.get(("rsend", ev["request_id"]))])
+                continue
+            if e == "Refused":
+                # derives: C3.4, C3.5; observe v5 -- refusals' inputs: request_id, requested_members, and the
+                # pending request (busy) or the superseding commit (superseded), by ref
+                n, reason = ev["node"], ev["reason"]
+                inputs = [{"name": "request_id", "value": ev["request_id"]},
+                          {"name": "requested_members", "value": sorted(tset(ev["members"]))}]
+                if reason == "busy":
+                    inputs.append({"name": "pending", "value": ev["pending"],
+                                   "ref": last.get(("rreq", n, ev["pending"]))})
+                if reason == "superseded":
+                    inputs.append({"name": "commit", "value": ev["epoch"], "ref": last.get(("cc", n, ev["epoch"]))})
+                ref = emit(n, "ReconfigRefused", {"node": n, "request_id": ev["request_id"], "reason": reason,
+                                                  "epoch": ev["epoch"] if reason == "superseded" else None},
+                           [last.get(("rreq", n, ev["request_id"]))], inputs)
+                last[("refused", n, ev["request_id"])] = ref
+                continue
+            if e == "ReconfigAck":
+                # derives: C3.4, C3.8; observe v5 -- the ack names the receiver's own record, whose identity the reply carries
+                x = ev["node"]
+                cause = (last.get(("cc", x, ev["epoch"])) if ev["outcome"] == "committed"
+                         else last.get(("refused", x, ev["request_id"])))
+                if cause is None:
+                    problems.append(f"ReconfigAck for {ev['request_id']} names no record of its receiver {x}")
+                emit(ev["operator"], e, {"operator": ev["operator"], "request_id": ev["request_id"],
+                                         "outcome": ev["outcome"],
+                                         "epoch": ev["epoch"] if ev["epoch"] >= 0 else None}, [cause])
+                continue
+            fields = {k: ev[k] for k in CONTRACT_FIELDS[e]}
+            if e == "ReadAck" and ev["outcome"] == "served":
+                fields["value"] = ev["value"]   # derives: C2.2 -- value only on a served ReadAck
+            if e == "Request":
+                ref = emit(ev["client"], e, fields, [])
+                last[("req", ev["client"])] = ref
+            elif e == "WriteAttempt":
+                g = last.get(("grant", ev["token"], ev["grantor_term"]))
+                ref = emit(ev["client"], e, fields, [g] if g else [])
+                last[("att", ev["client"], ev["token"], ev["value"])] = (ref, g)
+            elif e in ("WriteAccept", "WriteReject"):
+                # derives: C3.5; observe v5 -- storage decisions carry token, ledger, stored_value, value
+                a = last.get(("att", ev["client"], ev["token"], ev["value"]))
+                inputs = [{"name": "token", "value": ev["token"]}, {"name": "ledger", "value": ev["highest_before"]},
+                          {"name": "stored_value", "value": rid(ev["stored_value"])},
+                          {"name": "value", "value": ev["value"]}]
+                ref = emit(storage, e, fields, [a[0]] if a else [], inputs)
+                last[("dec", ev["client"], ev["token"], ev["value"])] = ref
+                dec_att[keyof(ref)] = a[0] if a else None
+                if not a or not a[1]:
+                    problems.append(f"{e} seq {ref['seq']} (token {ev['token']}) has no traceable Grant")
+            elif e == "ReadAttempt":
+                # derives: C2.1; observe v2 -- a ReadAttempt names the Grant whose token it uses
+                g = last.get(("grant", ev["token"], ev["grantor_term"]))
+                ref = emit(ev["client"], e, fields, [g] if g else [])
+                last[("ratt", ev["client"], ev["rid"])] = (ref, g)
+            elif e in ("ReadAccept", "ReadReject"):
+                # derives: C2.1, C2.2, C3.5; observe v2, v5 -- a read decision names the ReadAttempt, with its inputs
+                a = last.get(("ratt", ev["client"], ev["rid"]))
+                inputs = [{"name": "token", "value": ev["token"]}, {"name": "ledger", "value": ev["highest_before"]},
+                          {"name": "stored_value", "value": rid(ev["stored_value"])}]
+                if "value" in fields:
+                    fields["value"] = rid(fields["value"])
+                ref = emit(storage, e, fields, [a[0]] if a else [], inputs)
+                last[("rdec", ev["client"], ev["rid"])] = ref
+                dec_att[keyof(ref)] = a[0] if a else None
+                if not a or not a[1]:
+                    problems.append(f"{e} seq {ref['seq']} (token {ev['token']}) has no traceable Grant")
+            elif e == "ReadAck":
+                # derives: C2.2; observe v2 -- a ReadAck names the storage decision
+                if "value" in fields:
+                    fields["value"] = rid(fields["value"])
+                d = last.get(("rdec", ev["client"], ev["rid"]))
+                att = last.get(("ratt", ev["client"], ev["rid"]))
+                answers(e, fields, att, d)
+                ref = emit(ev["client"], e, fields, [d] if d else [])
+                if not d and ev["outcome"] == "served":
+                    problems.append(f"ReadAck served at {ref} has no storage decision")
+            elif e == "WriteAck":
+                d = last.get(("dec", ev["client"], ev["token"], ev["value"]))
+                att = last.get(("att", ev["client"], ev["token"], ev["value"]))
+                answers(e, fields, att, d)
+                ref = emit(ev["client"], e, fields, [d] if d else [])
+                if not d and ev["outcome"] == "accepted":
+                    problems.append(f"WriteAck accepted at {ref} has no storage decision")
     return out, problems, loop
 
 

````
## U04: `model/mutate.py`
````diff
diff --git a/model/mutate.py b/model/mutate.py
index 345af1e..ab16f7f 100644
--- a/model/mutate.py
+++ b/model/mutate.py
@@ -1,6 +1,6 @@
 #!/usr/bin/env python3
-# derives: P1-P30 (mutation half of every pair; P13-P18 derive from C2.1/C2.2, contract v2; P19-P30 from F2.1/F2.2, failure model v2); round 2: P11 re-placed, P8 keeps Join
-"""Generate the thirty mutated models (P1-P30), model/mutations/<P>/Lease.tla.
+# derives: P1-P33, P40-P54, P58-P63 (mutation half of every pair; P13-P18 derive from C2.1/C2.2, contract v2; P19-P30 from F2.1/F2.2, failure model v2; P31-P63 from C3.x/F3.x and C1.x/F3.x, contract v3 and failure model v3); round 2: P11 re-placed, P8 keeps Join; X3: P1-P30 re-applied to the X3 text, breaks unchanged
+"""Generate the fifty-four mutated models (P1-P33, P40-P54, P58-P63), model/mutations/<P>/Lease.tla.
 
 Each mutation is a copy of model/Lease.tla with one deliberate break on the path
 that enforces the pair's clause. The break is named in the copy's header and next
@@ -18,60 +18,65 @@ HERE = Path(__file__).parent
 #      | ("str", old, new)        replaces one unique occurrence of old
 MUTATIONS = [
     ("P1", "C1.1, F1.1", "C1_1",
-     "lease nodes do not durably record the highest token issued; it is lost on crash",
+     'lease nodes do not durably record the highest token issued; it is lost on crash',
      [("def", "Restart", r"""\* derives: F1.1
 \* mutation: P1 maxTok treated as volatile: a restarted lease node forgets every token it confirmed
 Restart(p) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ ~up[p]
     /\ up' = [up EXCEPT ![p] = TRUE]
     /\ maxTok' = IF p \in Nodes THEN [maxTok EXCEPT ![p] = 0] ELSE maxTok \* mutation: P1
-    /\ UNCHANGED <<paused, down, promised, leader, term, ltok, reqs, pending, tok,
-                   myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
-                   toAck, grants, rq, issued, decisions, told>>
-    /\ lastEv' = [event |-> "Fault", cell |-> "F1.1", action |-> "restart", target |-> p]
+    /\ UNCHANGED <<paused, down, promised, leader, term, ltok, reqs, pending, tok, myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval, toAck, grants, rq, issued, decisions, told>>
+    /\ lastEv' = <<[event |-> "Fault", cell |-> "F1.1", action |-> "restart", target |-> p]>>
 """)]),
     ("P2", "C1.1, F1.2", "C1_1",
-     "the grantor issues a grant without confirmation from a majority of lease nodes",
-     [("str", r"""    /\ \E Q \in SUBSET {q \in Nodes : up[q] /\ Conn(n, q) /\ promised[q] = term[n]} :
+     'the grantor issues a grant without confirmation from a majority of lease nodes',
+     [("str", r"""    /\ \E Q \in SUBSET {q \in Nodes : up[q] /\ Conn(n, q) /\ promised[q] = term[n] /\ Elig(q, n)} :
         /\ n \in Q
-        /\ Majority(Q)
-""", r"""    /\ \E Q \in {{n}} : \* mutation: P2 no majority confirmation; the leader alone decides
+        /\ MajOf(Q, Cur(n).mem)                         \* derives: C3.7
+""",
+       r"""    /\ \E Q \in {{n}} : \* mutation: P2 no majority confirmation; the leader alone decides
         /\ n \in Q
 """)]),
     ("P3", "C1.1, F1.3", "C1_1",
-     "the grantor reissues its last token instead of incrementing",
-     [("str", r"""        /\ LET k == ltok[n] + 1 IN""",
-       r"""        /\ LET k == Max({ltok[n], 1}) IN \* mutation: P3 next holder gets the expired holder's token""")]),
+     'the grantor reissues its last token instead of incrementing',
+     [("str", r"""        /\ LET k == ltok[n] + 1
+""",
+       r"""        /\ LET k == Max({ltok[n], 1}) \* mutation: P3 next holder gets the expired holder's token
+""")]),
     ("P4", "C1.2, F1.1", "C1_2",
      "storage's fence ledger is volatile: reset to 0 on restart",
      [("def", "Restart", r"""\* derives: F1.1
 \* mutation: P4 the fence ledger is not durable: storage restarts with highest = 0
 Restart(p) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ ~up[p]
     /\ up' = [up EXCEPT ![p] = TRUE]
     /\ highest' = IF p = Store THEN 0 ELSE highest \* mutation: P4
-    /\ UNCHANGED <<paused, down, promised, maxTok, leader, term, ltok, reqs, pending, tok,
-                   myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, stval,
-                   toAck, grants, rq, issued, decisions, told>>
-    /\ lastEv' = [event |-> "Fault", cell |-> "F1.1", action |-> "restart", target |-> p]
+    /\ UNCHANGED <<paused, down, promised, maxTok, leader, term, ltok, reqs, pending, tok, myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, stval, toAck, grants, rq, issued, decisions, told>>
+    /\ lastEv' = <<[event |-> "Fault", cell |-> "F1.1", action |-> "restart", target |-> p]>>
 """)]),
     ("P5", "C1.2, F1.2", "C1_2",
-     "storage accepts without comparing the token to the ledger",
+     'storage accepts without comparing the token to the ledger',
      [("str", r"""    /\ LET acc == m.t >= highest""",
        r"""    /\ LET acc == TRUE \* mutation: P5 the fencing comparison is skipped""")]),
     ("P6", "C1.2, F1.3", "C1_2",
-     "storage does not record the accepted token as the new highest",
+     'storage does not record the accepted token as the new highest',
      [("str", r"""       /\ highest' = IF acc THEN m.t ELSE highest""",
        r"""       /\ highest' = highest \* mutation: P6 acceptance does not advance the ledger""")]),
     ("P7", "C1.3, F1.1", "C1_3",
-     "storage acks acceptance on receipt, before deciding; the decision is volatile",
+     'storage acks acceptance on receipt, before deciding; the decision is volatile',
      [("def", "StorageDecide", r"""\* derives: C1.2, C1.3, F1.1
 \* mutation: P7 storage acks "accept" on receipt, before the (volatile) decision is taken
 StorageDecide(m, dup) ==
     \/ /\ ~dup
        /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+       /\ UNCHANGED kvars
+       /\ UNCHANGED xvars
        /\ up[Store]
        /\ m \in writeMsgs
        /\ ~\E a \in toAck \cup ackMsgs : a.c = m.c /\ a.t = m.t /\ a.v = m.v
@@ -83,6 +88,8 @@ StorageDecide(m, dup) ==
        /\ Internal("EarlyAck", Store)
     \/ /\ up[Store]
        /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+       /\ UNCHANGED kvars
+       /\ UNCHANGED xvars
        /\ m \in writeMsgs
        /\ dup => dups < MaxDups
        /\ LET acc == m.t >= highest
@@ -92,22 +99,25 @@ StorageDecide(m, dup) ==
           /\ writeMsgs' = IF dup THEN writeMsgs ELSE writeMsgs \ {m}
           /\ dups' = IF dup THEN dups + 1 ELSE dups
           /\ decisions' = Append(decisions, [token |-> m.t, hb |-> highest, outcome |-> out,
-                                             client |-> m.c, value |-> m.v, term |-> m.g])
+                                             client |-> m.c, value |-> m.v, term |-> m.g, sv |-> stval])
           /\ UNCHANGED <<up, paused, down, promised, maxTok, leader, term, ltok, reqs,
                          pending, tok, myToks, awaiting, grantMsgs, ackMsgs, grants, rq, issued, told,
                          toAck>>
-          /\ Emit([event |-> IF acc THEN "WriteAccept" ELSE "WriteReject", key |-> Key,
-                   token |-> m.t, highest_before |-> highest, grantor_term |-> m.g,
-                   client |-> m.c, value |-> m.v])
+          /\ Emit(<<[event |-> IF acc THEN "WriteAccept" ELSE "WriteReject", key |-> Key,
+                     token |-> m.t, highest_before |-> highest, grantor_term |-> m.g,
+                     client |-> m.c, value |-> m.v, stored_value |-> stval]>>)
 """)]),
     ("P8", "C1.3, F1.2", "C1_3",
-     "a client cut off from storage presumes its outstanding write succeeded",
-     [("str", r"""\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2
+     'a client cut off from storage presumes its outstanding write succeeded',
+     [("str", r"""\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, C3.x, F3.x
 Protocol ==
-""", r"""\* derives: C1.3, F1.2
+""",
+       r"""\* derives: C1.3, F1.2
 \* mutation: P8 a client that cannot reach storage treats its outstanding write as acked
 PresumeAck(c) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ up[c] /\ ~paused[c]
     /\ ~Conn(c, Store)
     /\ \E w \in awaiting[c] :
@@ -116,72 +126,76 @@ PresumeAck(c) ==
         /\ UNCHANGED <<up, paused, down, promised, maxTok, leader, term, ltok, reqs,
                        pending, tok, myToks, grantMsgs, writeMsgs, ackMsgs, dups, highest,
                        stval, toAck, grants, rq, issued, decisions>>
-        /\ Emit([event |-> "WriteAck", client |-> c, key |-> Key, token |-> w.t,
-                 outcome |-> "accepted", value |-> w.v, grantor_term |-> w.g])
+        /\ Emit(<<[event |-> "WriteAck", client |-> c, key |-> Key, token |-> w.t,
+                   outcome |-> "accepted", value |-> w.v, grantor_term |-> w.g]>>)
 
-\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2
+\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, C3.x, F3.x
 Protocol ==
     \/ \E c \in Clients : PresumeAck(c) \* mutation: P8
-"""),
-      ]),
+""")]),
     ("P9", "C1.3, F1.3", "C1_3",
-     "a client records any ack carrying its current token as success, ignoring the outcome",
+     'a client records any ack carrying its current token as success, ignoring the outcome',
      [("str", r"""            /\ told' = IF a.outcome = "accept" THEN""",
        r"""            \* mutation: P9 outcome replaced by the client's belief in its current token
             /\ told' = IF a.outcome = "accept" \/ a.t = tok[a.c].t THEN"""),
-      ("str", r"""                     outcome |-> IF a.outcome = "accept" THEN "accepted" ELSE "rejected",""",
-       r"""                     outcome |-> IF a.outcome = "accept" \/ a.t = tok[a.c].t THEN "accepted" ELSE "rejected",""")]),
+      ("str", r"""                       outcome |-> IF a.outcome = "accept" THEN "accepted" ELSE "rejected",""",
+       r"""                       outcome |-> IF a.outcome = "accept" \/ a.t = tok[a.c].t THEN "accepted" ELSE "rejected",""")]),
     ("P10", "C1.4, F1.1", "C1_4",
-     "election requires every lease node rather than a majority",
-     [("str", r"""        /\ Majority(Q)
-        /\ \A q \in Q : ~HearsLeader(q)""",
-       r"""        /\ Q = Nodes \* mutation: P10 unanimity instead of a majority
-        /\ \A q \in Q : ~HearsLeader(q)""")]),
+     'election requires every lease node (of the configuration) rather than a majority',
+     [("str", r"""        /\ MajOf(Q, X.mem)
+        /\ \A q \in Q : ~HearsLeader(q) \/ early[q]""",
+       r"""        /\ Q = X.mem \* mutation: P10 unanimity instead of a majority
+        /\ \A q \in Q : ~HearsLeader(q) \/ early[q]""")]),
     ("P11", "C1.4, F1.2", "C1_4",
-     "(round 2, re-placed) a request made while the requester cannot reach a majority of lease nodes is lost and never retried",
+     '(round 2, re-placed) a request made while the requester cannot reach a majority of lease nodes is lost and never retried',
      [("str", r"""    /\ reqs' = reqs \cup {c}
-""", r"""    \* mutation: P11 the request reaches the grantor only if a majority is reachable when it is
+""",
+       r"""    \* mutation: P11 the request reaches the grantor only if a majority is reachable when it is
     \* made; it is not retried after a heal, although the client keeps waiting
-    /\ reqs' = IF Majority({n \in Nodes : up[n] /\ Conn(c, n)}) THEN reqs \cup {c} ELSE reqs
+    /\ reqs' = IF MajOf({n \in Nodes : up[n] /\ Conn(c, n)}, GLatest.mem) THEN reqs \cup {c} ELSE reqs
 """)]),
     ("P12", "C1.4, F1.3", "C1_4",
-     "the grantor will not grant to another client until the previous holder releases (expiry ignored)",
+     'the grantor will not grant to another client until the previous holder releases (expiry ignored)',
      [("str", r"""    /\ c \in reqs
     /\ ReqRoute(c, n)
-""", r"""    /\ c \in reqs
+""",
+       r"""    /\ c \in reqs
     /\ ReqRoute(c, n)
     /\ ~\E d \in Clients : d # c /\ tok[d].t > 0 \* mutation: P12 waits for a release that never comes; expiry ignored
 """)]),
     # ---- X1 (contract v2): mutations for P13-P18, named in PREDICTIONS-x1.md before running
     ("P13", "C2.1, F1.1", "C2_1",
-     "the fence ledger is volatile: storage restarts with highest = 0 (same locus as P4, exercised on the read path)",
-     [("def", "Restart", r"""\* derives: F1.1, C2.1
+     'the fence ledger is volatile: storage restarts with highest = 0 (same locus as P4, exercised on the read path)',
+     [("def", "Restart", r"""\* derives: F1.1
 \* mutation: P13 the fence ledger is not durable: storage restarts with highest = 0, so a stale read is served
 Restart(p) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ ~up[p]
     /\ up' = [up EXCEPT ![p] = TRUE]
     /\ highest' = IF p = Store THEN 0 ELSE highest \* mutation: P13
-    /\ UNCHANGED <<paused, down, promised, maxTok, leader, term, ltok, reqs, pending, tok,
-                   myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, stval,
-                   toAck, grants, rq, issued, decisions, told>>
-    /\ lastEv' = [event |-> "Fault", cell |-> "F1.1", action |-> "restart", target |-> p]
+    /\ UNCHANGED <<paused, down, promised, maxTok, leader, term, ltok, reqs, pending, tok, myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, stval, toAck, grants, rq, issued, decisions, told>>
+    /\ lastEv' = <<[event |-> "Fault", cell |-> "F1.1", action |-> "restart", target |-> p]>>
 """)]),
     ("P14", "C2.1, F1.2", "C2_1",
-     "storage serves reads without comparing the token to the ledger",
+     'storage serves reads without comparing the token to the ledger',
      [("str", r"""    /\ LET srv == m.t >= highest""",
        r"""    /\ LET srv == TRUE \* mutation: P14 the read fence comparison is skipped""")]),
     ("P15", "C2.1, F1.3", "C2_1",
-     "storage serves a read whose token is one below the ledger (grace for the just-expired holder)",
+     'storage serves a read whose token is one below the ledger (grace for the just-expired holder)',
      [("str", r"""    /\ LET srv == m.t >= highest""",
        r"""    /\ LET srv == m.t >= highest - 1 \* mutation: P15 expiry grace: the previous token may still read""")]),
     ("P16", "C2.2, F1.1", "C2_2",
-     "storage acks a read as served, with the value it holds, on receipt, before its volatile decision",
+     'storage acks a read as served, with the value it holds, on receipt, before its volatile decision',
      [("str", r"""\* derives: C2.2, F1.1, F1.2, F2.1, F2.2 -- storage sends a queued read ack (lost if the link
 \* storage->client is down or the client is down, at the moment it is sent)
-SendReadAck(a) ==""", r"""\* derives: C2.2, F1.1
+SendReadAck(a) ==""",
+       r"""\* derives: C2.2, F1.1
 \* mutation: P16 storage acks "served" with its current value on receipt of a read, before deciding
 EarlyReadAck(m) ==
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ up[Store]
     /\ m \in readMsgs
     /\ ~\E a \in rToAck \cup rAckMsgs : a.c = m.c /\ a.r = m.r
@@ -197,16 +211,20 @@ EarlyReadAck(m) ==
 \* storage->client is down or the client is down, at the moment it is sent)
 SendReadAck(a) =="""),
       ("str", r"""    \/ \E m \in readMsgs, d \in BOOLEAN : StorageRead(m, d)   \* derives: C2.1, C2.2
-""", r"""    \/ \E m \in readMsgs, d \in BOOLEAN : StorageRead(m, d)   \* derives: C2.1, C2.2
+""",
+       r"""    \/ \E m \in readMsgs, d \in BOOLEAN : StorageRead(m, d)   \* derives: C2.1, C2.2
     \/ \E m \in readMsgs : EarlyReadAck(m) \* mutation: P16
 """)]),
     ("P17", "C2.2, F1.2", "C2_2",
-     "a client cut off from storage presumes its outstanding read was served with the value of a write it was told succeeded",
-     [("str", r"""\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2
+     'a client cut off from storage presumes its outstanding read was served with the value of a write it was told succeeded',
+     [("str", r"""\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, C3.x, F3.x
 Protocol ==
-""", r"""\* derives: C2.2, F1.2
+""",
+       r"""\* derives: C2.2, F1.2
 \* mutation: P17 a client that cannot reach storage answers its outstanding read from what it last wrote
 PresumeRead(c) ==
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ up[c] /\ ~paused[c]
     /\ ~Conn(c, Store)
     /\ \E w \in awaitingR[c], x \in {y \in told : y.c = c} :
@@ -216,10 +234,10 @@ PresumeRead(c) ==
         /\ UNCHANGED <<up, paused, down, promised, maxTok, leader, term, ltok, reqs, pending,
                        tok, myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
                        toAck, grants, rq, issued, decisions, told>>
-        /\ Emit([event |-> "ReadAck", client |-> c, key |-> Key, token |-> w.t,
-                 outcome |-> "served", value |-> x.v, grantor_term |-> w.g, rid |-> w.r])
+        /\ Emit(<<[event |-> "ReadAck", client |-> c, key |-> Key, token |-> w.t,
+                   outcome |-> "served", value |-> x.v, grantor_term |-> w.g, rid |-> w.r]>>)
 
-\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2
+\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, C3.x, F3.x
 Protocol ==
     \/ \E c \in Clients : PresumeRead(c) \* mutation: P17
 """)]),
@@ -232,21 +250,21 @@ Protocol ==
                    ELSE rAckMsgs""")]),
     # ---- X2 (failure model v2): mutations for P19-P30, named in PREDICTIONS-x2.md before running
     ("P19", "C1.1, F2.1", "C1_1",
-     "a voter that still hears the leader lends its vote without promising the new term (a pre-vote counted as a vote)",
-     [("str", r"""        /\ \A q \in Q : ~HearsLeader(q)   \* derives: C1.4, F2.1 -- voter stickiness
+     'a voter that still hears the leader lends its vote without promising the new term (a pre-vote counted as a vote)',
+     [("str", r"""        /\ \A q \in Q : ~HearsLeader(q) \/ early[q]   \* derives: C1.4, F2.1, F3.2 -- voter stickiness
         /\ LET t == 1 + Max({promised[q] : q \in Q}) IN
            /\ t <= MaxTerm
            /\ promised' = [q \in Nodes |-> IF q \in Q THEN t ELSE promised[q]]""",
        r"""        \* mutation: P19 a voter that still hears the leader votes anyway but does not promise the new term
         /\ LET t == 1 + Max({promised[q] : q \in Q}) IN
            /\ t <= MaxTerm
-           /\ promised' = [q \in Nodes |-> IF q \in Q /\ ~HearsLeader(q) THEN t ELSE promised[q]]""")]),
+           /\ promised' = [q \in Nodes |-> IF q \in Q /\ (~HearsLeader(q) \/ early[q]) THEN t ELSE promised[q]]""")]),
     ("P20", "C1.1, F2.2", "C1_1",
-     "a newly elected leader starts from its own durable maxTok, not the highest over its quorum",
+     'a newly elected leader starts from its own durable maxTok, not the highest over its quorum',
      [("str", r"""           /\ ltok' = [ltok EXCEPT ![n] = Max({maxTok[q] : q \in Q})]""",
        r"""           /\ ltok' = [ltok EXCEPT ![n] = maxTok[n]] \* mutation: P20 the quorum's records are not consulted""")]),
     ("P21", "C1.2, F2.1", "C1_2",
-     "storage defers to a grantor it can still reach: a token below the ledger is accepted if its grantor is connected to storage and still believes it leads",
+     'storage defers to a grantor it can still reach: a token below the ledger is accepted if its grantor is connected to storage and still believes it leads',
      [("str", r"""    /\ LET acc == m.t >= highest""",
        r"""    \* mutation: P21 storage defers to a grantor it can still reach
     /\ LET acc == \/ m.t >= highest
@@ -254,19 +272,22 @@ Protocol ==
                                                /\ up[grants[i].node] /\ leader[grants[i].node]
                                                /\ Conn(Store, grants[i].node)""")]),
     ("P22", "C1.2, F2.2", "C1_2",
-     "storage keeps the fence per writer (the highest token it accepted from that client), not per key",
+     'storage keeps the fence per writer (the highest token it accepted from that client), not per key',
      [("str", r"""    /\ LET acc == m.t >= highest""",
        r"""    \* mutation: P22 the fence is per writer, not per key
     /\ LET acc == m.t >= Max({decisions[i].token : i \in {j \in 1..Len(decisions) :
                                 decisions[j].outcome = "accept" /\ decisions[j].client = m.c}})""")]),
     ("P23", "C1.3, F2.1", "C1_3",
      "a client that has lost only its storage link, and still reaches a lease node, presumes its outstanding writes succeeded (v1's transitive reasoning)",
-     [("str", r"""\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2
+     [("str", r"""\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, C3.x, F3.x
 Protocol ==
-""", r"""\* derives: C1.3, F2.1
+""",
+       r"""\* derives: C1.3, F2.1
 \* mutation: P23 a client cut off from storage alone, still connected to a lease node, presumes its writes landed
 PresumeAckCut(c) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ up[c] /\ ~paused[c]
     /\ ~Link(c, Store) /\ ~Link(Store, c)
     /\ \E n \in Nodes : up[n] /\ Conn(c, n)
@@ -276,21 +297,24 @@ PresumeAckCut(c) ==
         /\ UNCHANGED <<up, paused, down, promised, maxTok, leader, term, ltok, reqs,
                        pending, tok, myToks, grantMsgs, writeMsgs, ackMsgs, dups, highest,
                        stval, toAck, grants, rq, issued, decisions>>
-        /\ Emit([event |-> "WriteAck", client |-> c, key |-> Key, token |-> w.t,
-                 outcome |-> "accepted", value |-> w.v, grantor_term |-> w.g])
+        /\ Emit(<<[event |-> "WriteAck", client |-> c, key |-> Key, token |-> w.t,
+                   outcome |-> "accepted", value |-> w.v, grantor_term |-> w.g]>>)
 
-\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2
+\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, C3.x, F3.x
 Protocol ==
     \/ \E c \in Clients : PresumeAckCut(c) \* mutation: P23
 """)]),
     ("P24", "C1.3, F2.2", "C1_3",
-     "a client that can send to storage but hears nothing back presumes its outstanding writes succeeded",
-     [("str", r"""\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2
+     'a client that can send to storage but hears nothing back presumes its outstanding writes succeeded',
+     [("str", r"""\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, C3.x, F3.x
 Protocol ==
-""", r"""\* derives: C1.3, F2.2
+""",
+       r"""\* derives: C1.3, F2.2
 \* mutation: P24 a client whose acks never come back presumes its writes landed
 PresumeAckSilent(c) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ up[c] /\ ~paused[c]
     /\ Link(c, Store) /\ ~Link(Store, c)
     /\ \E w \in awaiting[c] :
@@ -299,25 +323,26 @@ PresumeAckSilent(c) ==
         /\ UNCHANGED <<up, paused, down, promised, maxTok, leader, term, ltok, reqs,
                        pending, tok, myToks, grantMsgs, writeMsgs, ackMsgs, dups, highest,
                        stval, toAck, grants, rq, issued, decisions>>
-        /\ Emit([event |-> "WriteAck", client |-> c, key |-> Key, token |-> w.t,
-                 outcome |-> "accepted", value |-> w.v, grantor_term |-> w.g])
+        /\ Emit(<<[event |-> "WriteAck", client |-> c, key |-> Key, token |-> w.t,
+                   outcome |-> "accepted", value |-> w.v, grantor_term |-> w.g]>>)
 
-\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2
+\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, C3.x, F3.x
 Protocol ==
     \/ \E c \in Clients : PresumeAckSilent(c) \* mutation: P24
 """)]),
     ("P25", "C1.4, F2.1", "C1_4",
-     "the grantor will not grant while any lease node is unreachable (it waits for the whole configuration)",
+     'the grantor will not grant while any lease node is unreachable (it waits for the whole configuration)',
      [("str", r"""    /\ c \in reqs
     /\ ReqRoute(c, n)
-""", r"""    /\ c \in reqs
+""",
+       r"""    /\ c \in reqs
     /\ ReqRoute(c, n)
     /\ \A q \in Nodes : Conn(n, q) \* mutation: P25 a majority is not enough while a follower is unreachable
 """)]),
     ("P26", "C1.4, F2.2", "C1_4",
-     "the quorum check counts followers the grantor can send to, not ones it is connected to",
-     [("str", r"""    /\ ~Majority({q \in Nodes : up[q] /\ Conn(n, q)})""",
-       r"""    /\ ~Majority({q \in Nodes : up[q] /\ Link(n, q)}) \* mutation: P26 outgoing links only""")]),
+     'the quorum check counts followers the grantor can send to, not ones it is connected to',
+     [("str", r"""       \/ ~MajOf({q \in Nodes : up[q] /\ Conn(n, q) /\ Elig(q, n)}, Cur(n).mem)""",
+       r"""       \/ ~MajOf({q \in Nodes : up[q] /\ Link(n, q) /\ Elig(q, n)}, Cur(n).mem) \* mutation: P26 outgoing links only""")]),
     ("P27", "C2.1, F2.1", "C2_1",
      "storage serves a read below the ledger if its token's grantor is connected to storage and still believes it leads",
      [("str", r"""    /\ LET srv == m.t >= highest""",
@@ -327,18 +352,21 @@ Protocol ==
                                                /\ up[grants[i].node] /\ leader[grants[i].node]
                                                /\ Conn(Store, grants[i].node)""")]),
     ("P28", "C2.1, F2.2", "C2_1",
-     "storage fences reads per reader (the highest token it accepted a write from that client with), not per key",
+     'storage fences reads per reader (the highest token it accepted a write from that client with), not per key',
      [("str", r"""    /\ LET srv == m.t >= highest""",
        r"""    \* mutation: P28 the read fence is per client, not per key
     /\ LET srv == m.t >= Max({decisions[i].token : i \in {j \in 1..Len(decisions) :
                                 decisions[j].outcome = "accept" /\ decisions[j].client = m.c}})""")]),
     ("P29", "C2.2, F2.1", "C2_2",
-     "a client that has lost only its storage link, still reaching a lease node, answers its outstanding read from its cache (last value read, or none)",
-     [("str", r"""\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2
+     'a client that has lost only its storage link, still reaching a lease node, answers its outstanding read from its cache (last value read, or none)',
+     [("str", r"""\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, C3.x, F3.x
 Protocol ==
-""", r"""\* derives: C2.2, F2.1
+""",
+       r"""\* derives: C2.2, F2.1
 \* mutation: P29 a client cut off from storage alone answers its read from its cache
 PresumeReadCut(c) ==
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ up[c] /\ ~paused[c]
     /\ ~Link(c, Store) /\ ~Link(Store, c)
     /\ \E n \in Nodes : up[n] /\ Conn(c, n)
@@ -350,20 +378,23 @@ PresumeReadCut(c) ==
         /\ UNCHANGED <<up, paused, down, promised, maxTok, leader, term, ltok, reqs, pending,
                        tok, myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
                        toAck, grants, rq, issued, decisions, told>>
-        /\ Emit([event |-> "ReadAck", client |-> c, key |-> Key, token |-> w.t,
-                 outcome |-> "served", value |-> cache, grantor_term |-> w.g, rid |-> w.r])
+        /\ Emit(<<[event |-> "ReadAck", client |-> c, key |-> Key, token |-> w.t,
+                   outcome |-> "served", value |-> cache, grantor_term |-> w.g, rid |-> w.r]>>)
 
-\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2
+\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, C3.x, F3.x
 Protocol ==
     \/ \E c \in Clients : PresumeReadCut(c) \* mutation: P29
 """)]),
     ("P30", "C2.2, F2.2", "C2_2",
-     "a client that can send to storage but hears nothing back presumes its read was served with the value of its last acknowledged write",
-     [("str", r"""\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2
+     'a client that can send to storage but hears nothing back presumes its read was served with the value of its last acknowledged write',
+     [("str", r"""\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, C3.x, F3.x
 Protocol ==
-""", r"""\* derives: C2.2, F2.2
+""",
+       r"""\* derives: C2.2, F2.2
 \* mutation: P30 a client whose read acks never come back presumes its read was served
 PresumeReadSilent(c) ==
+    /\ UNCHANGED kvars
+    /\ UNCHANGED xvars
     /\ up[c] /\ ~paused[c]
     /\ Link(c, Store) /\ ~Link(Store, c)
     /\ \E w \in awaitingR[c], x \in {y \in told : y.c = c} :
@@ -373,13 +404,189 @@ PresumeReadSilent(c) ==
         /\ UNCHANGED <<up, paused, down, promised, maxTok, leader, term, ltok, reqs, pending,
                        tok, myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
                        toAck, grants, rq, issued, decisions, told>>
-        /\ Emit([event |-> "ReadAck", client |-> c, key |-> Key, token |-> w.t,
-                 outcome |-> "served", value |-> x.v, grantor_term |-> w.g, rid |-> w.r])
+        /\ Emit(<<[event |-> "ReadAck", client |-> c, key |-> Key, token |-> w.t,
+                   outcome |-> "served", value |-> x.v, grantor_term |-> w.g, rid |-> w.r]>>)
 
-\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2
+\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, C3.x, F3.x
 Protocol ==
     \/ \E c \in Clients : PresumeReadSilent(c) \* mutation: P30
 """)]),
+    # ---- X3 (contract v3, failure model v3): mutations for P31-P33, P40-P54, P58-P63, named in PREDICTIONS-x3.md before running
+    ("P31", "C3.1, F3.1", "C3_1",
+     'the decider does not apply its own commit to its configuration history, so a second pending request for the same epoch is committed too',
+     [("str", r"""           /\ cfg' = [cfg EXCEPT ![l] = H]
+""",
+       r"""           /\ cfg' = cfg \* mutation: P31 the decider keeps proposing from the old epoch
+""")]),
+    ("P32", "C3.1, F3.2", "C3_1",
+     'the leader numbers the new configuration from its clock: current + 1 + its clock offset in lifetimes',
+     [("str", r"""               X == [ep |-> e + 1, mem |-> r.mem, rid |-> r.rid,""",
+       r"""               X == [ep |-> e + 1 + (off[l] \div Lifetime), mem |-> r.mem, rid |-> r.rid, \* mutation: P32 a clock-derived epoch""")]),
+    ("P33", "C3.1, F3.3", "C3_1",
+     'a leader accepts a forwarded request at whatever epoch the receiver targeted, counting it against its own current configuration',
+     [("str", r"""    /\ r.tgt = e + 1
+""",
+       r"""    /\ r.tgt <= e + 1 \* mutation: P33 the receiver's target epoch is taken as given
+"""),
+      ("str", r"""               X == [ep |-> e + 1, mem |-> r.mem, rid |-> r.rid,""",
+       r"""               X == [ep |-> r.tgt, mem |-> r.mem, rid |-> r.rid, \* mutation: P33""")]),
+    ("P40", "C3.4, F3.1", "C3_4",
+     'the leader waits for agreements from every member of the old configuration before it commits',
+     [("str", r"""        /\ l \in Qo
+""",
+       r"""        /\ l \in Qo
+        /\ Old.mem \subseteq Qo \* mutation: P40 every old member must agree, a majority is not enough
+""")]),
+    ("P41", "C3.4, F3.2", "C3_4",
+     "a leader whose clock reads earlier than the receiver's clock when it recorded the request treats it as a replay and silently drops it",
+     [("str", r"""NoPend == [rid |-> "none", mem |-> {}, op |-> "none", tgt |-> -1]""",
+       r"""NoPend == [rid |-> "none", mem |-> {}, op |-> "none", tgt |-> -1, ro |-> 0] \* mutation: P41 requests carry their recording time"""),
+      ("str", r"""[rid |-> m.rid, mem |-> m.mem, op |-> m.op, tgt |-> CurEp(x) + 1]""",
+       r"""[rid |-> m.rid, mem |-> m.mem, op |-> m.op, tgt |-> CurEp(x) + 1, ro |-> off[x]]"""),
+      ("str", r"""    /\ r.tgt = e + 1
+""",
+       r"""    /\ r.tgt = e + 1
+    /\ off[l] >= r.ro \* mutation: P41 a request "from the future" is dropped as a replay
+""")]),
+    ("P42", "C3.4, F3.3", "C3_4",
+     'the leader will not commit while any member of the old configuration is in an incarnation not yet re-admitted',
+     [("str", r"""    /\ r.tgt = e + 1
+""",
+       r"""    /\ r.tgt = e + 1
+    /\ \A q \in Old.mem : inc[q] = 0 \/ <<q, inc[q]>> \in R \* mutation: P42 waits for a re-admission nobody requests
+""")]),
+    ("P43", "C3.5, F3.1", "C3_5",
+     'the decider drops from the new membership every requested member it cannot reach (it consults its links, unrecorded)',
+     [("str", r"""               X == [ep |-> e + 1, mem |-> r.mem, rid |-> r.rid,""",
+       r"""               X == [ep |-> e + 1, mem |-> {q \in r.mem : Conn(l, q)}, rid |-> r.rid, \* mutation: P43 unrecorded link state""")]),
+    ("P44", "C3.5, F3.2", "C3_5",
+     'storage judges a write or read expired by its own clock, which it does not record (elapsed run time is open, so any may be judged expired)',
+     [("str", r"""    /\ LET acc == m.t >= highest
+           out == IF acc THEN "accept" ELSE "reject" IN""",
+       r"""    /\ \E expired \in BOOLEAN : \* mutation: P44 an unrecorded clock reading decides expiry
+       LET acc == m.t >= highest /\ ~expired
+           out == IF acc THEN "accept" ELSE "reject" IN"""),
+      ("str", '    /\\ LET srv == m.t >= highest\n           out == IF srv THEN "served" ELSE "rejected"',
+       '    /\\ \\E expired \\in BOOLEAN : \\* mutation: P44\n       LET srv == m.t >= highest /\\ ~expired\n           out == IF srv THEN "served" ELSE "rejected"')]),
+    ("P45", "C3.5, F3.3", "C3_5",
+     'the decider puts in readmits every amnesic incarnation in the new membership that it can reach, not only those whose agreement it recorded',
+     [("str", r"""                     rdm |-> {<<q, inc[q]>> : q \in {p \in A : inc[p] > 0 /\ p \in r.mem}}, by |-> l]""",
+       r"""                     rdm |-> {<<q, inc[q]>> : q \in {p \in A \cup {p2 \in r.mem \cap Nodes : up[p2] /\ Conn(l, p2)} :
+                                                     inc[p] > 0 /\ p \in r.mem}}, by |-> l] \* mutation: P45""")]),
+    ("P46", "C1.1, F3.1", "C1_1",
+     "the nodes agreeing to a configuration commit do not receive the leader's token count (no log transfer with the joint entry)",
+     [("str", r"""           /\ maxTok' = [q \in Nodes |-> IF q \in A THEN Max({maxTok[q], ltok[l]}) ELSE maxTok[q]]""",
+       r"""           /\ maxTok' = maxTok \* mutation: P46 the new members start from 0""")]),
+    ("P47", "C1.1, F3.2", "C1_1",
+     'the grantor takes its next token from its clock: max(1, last + 1 + its clock offset in lifetimes)',
+     [("str", r"""        /\ LET k == ltok[n] + 1
+""",
+       r"""        /\ LET k == Max({1, ltok[n] + 1 + (off[n] \div Lifetime)}) \* mutation: P47 a clock-derived token
+""")]),
+    ("P48", "C1.1, F3.3", "C1_1",
+     "an amnesic restart keeps the node's incarnation number, so its empty state votes and agrees as the old node",
+     [("str", r"""    /\ inc' = [inc EXCEPT ![n] = @ + 1]""",
+       r"""    /\ inc' = inc \* mutation: P48 amnesia not told apart from an ordinary restart""")]),
+    ("P49", "C1.2, F3.1", "C1_2",
+     'storage resets its ledger to 0 whenever a configuration commit is decided (a new configuration as a new fencing era)',
+     [("str", r"""                          myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
+                          toAck, grants, rq, issued, decisions, told>>
+           /\ Emit(<<[event |-> "Commit",""",
+       r"""                          myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, stval,
+                          toAck, grants, rq, issued, decisions, told>>
+           /\ highest' = 0 \* mutation: P49 the ledger restarts with the configuration
+           /\ Emit(<<[event |-> "Commit",""")]),
+    ("P50", "C1.2, F3.2", "C1_2",
+     "storage accepts a stale write if the writer's own clock says its grant is unexpired (its clock offset is negative)",
+     [("str", r"""    /\ LET acc == m.t >= highest""",
+       r"""    /\ LET acc == m.t >= highest \/ off[m.c] < 0 \* mutation: P50 the writer's clock vouches for its grant""")]),
+    ("P51", "C1.2, F3.3", "C1_2",
+     'storage fails open: while some lease node is in an incarnation not yet re-admitted, it accepts every write',
+     [("str", r"""    /\ LET acc == m.t >= highest""",
+       r"""    /\ LET acc == m.t >= highest \/ \E q \in Nodes : inc[q] > 0 /\ <<q, inc[q]>> \notin GRdm(GLatest.ep, 0) \* mutation: P51 fail open""")]),
+    ("P52", "C1.4, F3.1", "C1_4",
+     "only members of the deployment's initial configuration may stand for election",
+     [("str", r"""    /\ up[n] /\ ~leader[n]
+    /\ ~HearsLeader(n) \/ early[n]
+""",
+       r"""    /\ up[n] /\ ~leader[n]
+    /\ ~HearsLeader(n) \/ early[n]
+    /\ n \in Init0 \* mutation: P52 candidacy from the deployment's list
+""")]),
+    ("P53", "C1.4, F3.2", "C1_4",
+     'a lease node whose clock has stepped refuses to agree to grants (a clock alarm nobody clears)',
+     [("str", r"""    /\ \E Q \in SUBSET {q \in Nodes : up[q] /\ Conn(n, q) /\ promised[q] = term[n] /\ Elig(q, n)} :""",
+       r"""    /\ \E Q \in SUBSET {q \in Nodes : up[q] /\ Conn(n, q) /\ promised[q] = term[n] /\ Elig(q, n) /\ off[q] = 0} : \* mutation: P53""")]),
+    ("P54", "C1.4, F3.3", "C1_4",
+     'the leader suspends granting while any member of its configuration is in an incarnation not yet re-admitted',
+     [("str", r"""    /\ c \in reqs
+    /\ ReqRoute(c, n)
+""",
+       r"""    /\ c \in reqs
+    /\ ReqRoute(c, n)
+    /\ \A q \in Cur(n).mem : inc[q] = 0 \/ <<q, inc[q]>> \in RdmOf(cfg[n]) \* mutation: P54
+""")]),
+    ("P58", "C3.7, F3.1", "C3_7",
+     "the grantor issues every grant under the deployment's initial configuration and does not give up leadership when a commit removes it",
+     [("str", r"""    /\ Elig(n, n)                                       \* derives: C3.7, F3.1, F3.3""",
+       r"""    /\ n \in Init0 \* mutation: P58 the deployment's configuration, not the current one"""),
+      ("str", r"""    /\ \E Q \in SUBSET {q \in Nodes : up[q] /\ Conn(n, q) /\ promised[q] = term[n] /\ Elig(q, n)} :
+        /\ n \in Q
+        /\ MajOf(Q, Cur(n).mem)                         \* derives: C3.7""",
+       r"""    /\ \E Q \in SUBSET {q \in Nodes : up[q] /\ Conn(n, q) /\ promised[q] = term[n] /\ q \in Init0} :
+        /\ n \in Q
+        /\ MajOf(Q, Init0) \* mutation: P58"""),
+      ("str", r"""                                        ninc |-> inc[n], ep |-> CurEp(n), cep |-> CurEp(n),
+                                        mem |-> Cur(n).mem, ag |-> ag, lt |-> ltok[n]])""",
+       r"""                                        ninc |-> inc[n], ep |-> 0, cep |-> CurEp(n),
+                                        mem |-> Init0, ag |-> ag, lt |-> ltok[n]]) \* mutation: P58"""),
+      ("str", r"""                      config_epoch |-> CurEp(n), members |-> Cur(n).mem, last_token |-> ltok[n],""",
+       r"""                      config_epoch |-> 0, members |-> Init0, last_token |-> ltok[n],"""),
+      ("str", r"""           /\ leader' = [leader EXCEPT ![l] = l \in r.mem]""",
+       r"""           /\ UNCHANGED leader \* mutation: P58 a removed leader keeps leading"""),
+      ("str", r"""    /\ \/ ~Elig(n, n)
+       \/ ~MajOf({q \in Nodes : up[q] /\ Conn(n, q) /\ Elig(q, n)}, Cur(n).mem)""",
+       r"""    /\ \/ ~MajOf({q \in Nodes : up[q] /\ Conn(n, q) /\ q \in Init0}, Init0) \* mutation: P58""")]),
+    ("P59", "C3.7, F3.2", "C3_7",
+     "the leader counts as a member any node whose clock is ahead of its own (heartbeats stamped with the sender's clock look fresh)",
+     [("str", r"""    /\ \E Q \in SUBSET {q \in Nodes : up[q] /\ Conn(n, q) /\ promised[q] = term[n] /\ Elig(q, n)} :
+        /\ n \in Q
+        /\ MajOf(Q, Cur(n).mem)                         \* derives: C3.7""",
+       r"""    /\ \E Q \in SUBSET {q \in Nodes : up[q] /\ Conn(n, q) /\ promised[q] = term[n] /\ (Elig(q, n) \/ off[q] > off[n])} :
+        /\ n \in Q
+        /\ 2 * Cardinality(Q) > Cardinality(Cur(n).mem) \* mutation: P59 a node with a fast clock looks like a member""")]),
+    ("P60", "C3.7, F3.3", "C3_7",
+     "grant counting ignores incarnations: an amnesic incarnation's agreement counts toward a grant",
+     [("str", r"""    /\ \E Q \in SUBSET {q \in Nodes : up[q] /\ Conn(n, q) /\ promised[q] = term[n] /\ Elig(q, n)} :""",
+       r"""    /\ \E Q \in SUBSET {q \in Nodes : up[q] /\ Conn(n, q) /\ promised[q] = term[n] /\ q \in Cur(n).mem} : \* mutation: P60""")]),
+    ("P61", "C3.8, F3.1", "C3_8",
+     'a receiver that is not the leader tells the operator committed as soon as it has recorded the request',
+     [("str", r"""            /\ UNCHANGED <<owed, refusals>>
+""",
+       r"""            /\ owed' = IF leader[x] THEN owed \* mutation: P61 a forwarded request is presumed committed
+                       ELSE [owed EXCEPT ![x] = @ \cup {[op |-> m.op, rid |-> m.rid, outcome |-> "committed",
+                                                        ep |-> CurEp(x) + 1, x |-> x]}]
+            /\ UNCHANGED refusals
+""")]),
+    ("P62", "C3.8, F3.2", "C3_8",
+     'a receiver whose timer fires early (forward clock step) presumes its pending request committed and tells the operator so',
+     [("str", r"""    /\ UNCHANGED kvars
+    /\ UNCHANGED agreeLog
+    /\ off' = [off EXCEPT ![p] = @ + s]""",
+       r"""    /\ UNCHANGED <<inc, cfg, jprop, pend, rcMsgs, opMsgs, commits, refusals, opTold>>
+    \* mutation: P62 the receiver's request timer fires and it presumes success
+    /\ owed' = IF p \in Nodes /\ s > 0 /\ pend[p] # NoPend
+               THEN [owed EXCEPT ![p] = @ \cup {[op |-> pend[p].op, rid |-> pend[p].rid, outcome |-> "committed",
+                                                  ep |-> pend[p].tgt, x |-> p]}]
+               ELSE owed
+    /\ UNCHANGED agreeLog
+    /\ off' = [off EXCEPT ![p] = @ + s]""")]),
+    ("P63", "C3.8, F3.3", "C3_8",
+     'the decider counts a re-admission agreement toward the commit that re-admits it (toward both majorities)',
+     [("str", r"""    /\ \E Qo \in SUBSET {q \in Agreeable(l, Old.mem) : EligIn(q, Old.mem, R)},
+          Qn \in SUBSET {q \in Agreeable(l, r.mem) : EligIn(q, r.mem, R)},""",
+       r"""    /\ \E Qo \in SUBSET Agreeable(l, Old.mem), \* mutation: P63 an unadmitted incarnation counts
+          Qn \in SUBSET Agreeable(l, r.mem),""")]),
 ]
 
 EXPECTED = {p: inv for p, _, inv, _, _ in MUTATIONS}
@@ -398,7 +605,7 @@ def replace_def(src, name, new):
 
 
 def build(pair, derives, desc, edits, src):
-    # derives: P1-P30 (pairs v3; was tagged P1-P12 only, stale since X1, fixed in the routing round)
+    # derives: P1-P33, P40-P54, P58-P63 (pairs v4; was tagged P1-P12 only, stale since X1, fixed in the routing round)
     for kind, a, b in edits:
         if kind == "def":
             src = replace_def(src, a, b)

````
## U05: `model/run.py`
````diff
diff --git a/model/run.py b/model/run.py
index 75824e7..fdb6931 100644
--- a/model/run.py
+++ b/model/run.py
@@ -1,31 +1,36 @@
 #!/usr/bin/env python3
-# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2; format v2 E1, E2, v4 E3 (checking runs for the 35 shared schedules P1-P30, false-suspicion-v1, H7-H10, and mutations P1-P30)
+# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F1.1, F1.2, F1.3, F2.1, F2.2, F3.1, F3.2, F3.3; format v2 E1, E2, v4 E3 (checking runs for the 59 shared schedules P1-P33, P40-P54, P58-P63, false-suspicion-v1, H7-H10, and mutations P1-P33, P40-P54, P58-P63)
 # (routing round: the header said "P1-P12 and M1" and named neither C2.x nor F2.x; that stale tag is fixed here)
 """Driver behind model/run.sh.
 
   run.py <schedule-name>   check the model on one schedule; print PASS | FAIL <inv> | UNEXPLAINED <why>
   run.py --mutations       regenerate and check every mutation on its pair's schedule;
                            every one must print FAIL <the pair's clause>
-  run.py --all             every schedule, then every mutation
+  run.py --all             every schedule, then every mutation, then the decision-replay check
+  run.py --replay          observe/decision_replay.py over every unmutated observe file
 """
 import os
 import re
 import subprocess
 import sys
+import time
 from pathlib import Path
 
 HERE = Path(__file__).resolve().parent
 ROOT = HERE.parent
 WORK = HERE / ".work"
 OBS = HERE / "observe"
-JAR = os.environ.get("TLA2TOOLS", "/home/tony/projects/tlaplus/tla2tools.jar")
+JAR = os.environ.get("TLA2TOOLS", "/opt/tlaplus/tla2tools.jar")
+HEAP = os.environ.get("TLC_HEAP", "8g")   # derives: (bounds) -- the session's memory cap is 24 GB, the machine has 13 GB; README X3 "Limits"
 sys.path.insert(0, str(HERE))
 import compile as compiler  # noqa: E402
 import export as exporter  # noqa: E402
 import mutate  # noqa: E402
 
-# derives: C1.1-C1.4, C2.1, C2.2, F2.1, F2.2 -- every shared schedule (P13-P18 added for contract v2, P19-P30 for failure model v2)
-ORDER = [f"P{i}" for i in range(1, 31)] + ["false-suspicion-v1"] + [f"H{i}" for i in range(7, 11)]  # H7-H10 shared after X2
+# derives: C1.1-C1.4, C2.1, C2.2, F2.1, F2.2, C3.x, F3.x -- every shared schedule (P13-P18 added for contract v2,
+# P19-P30 for failure model v2, P31-P33, P40-P54, P58-P63 for contract v3 / failure model v3)
+ORDER = ([f"P{i}" for i in range(1, 34)] + [f"P{i}" for i in range(40, 55)] + [f"P{i}" for i in range(58, 64)]
+         + ["false-suspicion-v1"] + [f"H{i}" for i in range(7, 11)])  # H7-H10 shared after X2
 
 
 def find_schedule(name):
@@ -39,24 +44,27 @@ def tlc(dirp, cfg):
     # derives: C1.1, C1.2, C1.3, C1.4
     jtmp = WORK / "jtmp"
     jtmp.mkdir(parents=True, exist_ok=True)
-    cmd = ["java", f"-Djava.io.tmpdir={jtmp}", "-XX:+UseParallelGC", "-cp", JAR, "tlc2.TLC",
-           "-deadlock", "-cleanup", "-workers", os.environ.get("TLC_WORKERS", "4"),
+    cmd = ["java", f"-Xmx{HEAP}", f"-Djava.io.tmpdir={jtmp}", "-XX:+UseParallelGC", "-cp", JAR, "tlc2.TLC",
+           "-deadlock", "-cleanup", "-workers", os.environ.get("TLC_WORKERS", "8"),
            "-metadir", str(dirp / "states"), "-config", cfg, "MC.tla"]
-    r = subprocess.run(cmd, cwd=dirp, capture_output=True, text=True)
-    out = r.stdout + r.stderr
-    (dirp / (cfg.replace(".cfg", "") + ".out")).write_text(out)
-    return out
+    log = dirp / (cfg.replace(".cfg", "") + ".out")
+    with open(log, "w") as f:   # streamed, so a long run can be watched
+        subprocess.run(cmd, cwd=dirp, stdout=f, stderr=subprocess.STDOUT, text=True)
+    return log.read_text()
 
 
 def verdict(out):
-    # derives: C1.1, C1.2, C1.3, C1.4 -- classify TLC's output
+    # derives: C1.1, C1.2, C1.3, C1.4, C3.x -- classify TLC's output
     m = re.search(r"Invariant (\w+) is violated", out)
     if m and m.group(1) == "TermHeadroom":
         return "UNEXPLAINED", "MaxTerm bound reached; raise it before reading this run"
+    if m and m.group(1) == "C1_1order":
+        # derives: C1.1 (README X3) -- the v1 reading alone is not v3's C1.1
+        return "UNEXPLAINED", "C1_1order (tokens fall in the model's total order; v3's reading of C1.1 holds there)"
     if m:
         return "FAIL", m.group(1)
     if "Temporal properties were violated" in out:
-        return "FAIL", "C1_4"
+        return "FAIL", "temporal"
     if "Model checking completed. No error has been found." in out:
         return "PASS", None
     err = re.search(r"^Error: (.*)$", out, re.M)
@@ -69,19 +77,51 @@ def stats(out):
     return (m.group(2) if m else "?"), (d.group(1) if d else "?")
 
 
-def check(name, lease=None, run_id=None, quiet=False):
-    # derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
+def check(name, lease=None, run_id=None, quiet=False, only=None):
+    # derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, C3.x
+    # only: the clause a mutation run checks (README X3, "Mutation runs check the pair's clause")
     path = find_schedule(name)
     if path is None:
         return f"UNEXPLAINED no schedule named {name}"
     run_id = run_id or path.stem
     dirp = WORK / run_id
     try:
-        meta = compiler.compile_schedule(path, dirp, lease or (HERE / "Lease.tla"))
+        meta = compiler.compile_schedule(path, dirp, lease or (HERE / "Lease.tla"), only=only)
     except compiler.ScheduleError as e:
         return f"UNEXPLAINED schedule rejected: {e}"
-    out = tlc(dirp, "MC.cfg")
+    t0 = time.time()
+    out = tlc(dirp, "MC_only.cfg" if only else "MC.cfg")
     v, inv = verdict(out)
+    if v == "FAIL" and inv in ("C1_4T", "C3_4T"):
+        inv = inv[:-1]   # derives: C1.4, C3.4 -- a reachable terminal state where the premise holds and the conclusion does not
+    acyc = ""
+    if v == "PASS" and (only is None or only in ("C1_4", "C3_4")):
+        # derives: C1.4, C3.4 (README X3) -- the terminal-state forms are exact only if the state graph has
+        # no cycle but stuttering; if it has one, fall back to TLC's liveness check under Spec's fairness
+        aout = tlc(dirp, "Acyclic.cfg")
+        if "Temporal properties were violated" in aout:
+            acyc = ", cycle found: full liveness check"
+            lcfg = f"MC_{only}.cfg" if only else "Live.cfg"
+            lout = tlc(dirp, lcfg)
+            lv, linv = verdict(lout)
+            if lv == "FAIL":
+                if only:
+                    inv = only
+                else:
+                    for p in meta["props"]:
+                        pout = tlc(dirp, f"MC_{p}.cfg")
+                        if "Temporal properties were violated" in pout:
+                            inv, lout = p, pout
+                            break
+                    else:
+                        return "UNEXPLAINED temporal violation not reproduced by any single property"
+                v, out = "FAIL", lout
+            elif lv != "PASS":
+                return f"UNEXPLAINED liveness check: {linv}"
+        elif "Model checking completed. No error has been found." in aout:
+            acyc = ", acyclic"
+        else:
+            return "UNEXPLAINED acyclicity check: " + verdict(aout)[1]
     distinct, depth = stats(out)
     OBS.mkdir(exist_ok=True)
     obs = OBS / f"{run_id}.jsonl"
@@ -107,39 +147,73 @@ def check(name, lease=None, run_id=None, quiet=False):
             f.write(__import__("json").dumps(r) + "\n")
     if not quiet:
         print(f"# {run_id}: {distinct} distinct states, depth {depth}, max_term {meta['max_term']},"
-              f" observe -> {obs.relative_to(ROOT)}{note}"
+              f" {time.time() - t0:.0f} s{acyc}, observe -> {obs.relative_to(ROOT)}{note}"
               + (f", liveness lasso ({loop})" if loop else ""), file=sys.stderr)
     if v == "PASS" and problems:
         return "UNEXPLAINED provenance: " + "; ".join(problems)
     return "PASS" if v == "PASS" else f"FAIL {inv}"
 
 
-def mutations():
-    # derives: P1-P30 (pairs v3)
-    mutate.main()
+REPLAY = ROOT / "observe" / "decision_replay.py"
+
+
+def replay(paths):
+    # derives: C3.5, C1.1, C3.1, C3.7, C3.8 -- the steward's decision-replay check over observe files
+    r = subprocess.run([sys.executable, str(REPLAY)] + [str(p) for p in paths], capture_output=True, text=True)
+    return r.returncode, r.stdout
+
+
+def mutations(only_pairs=()):
+    # derives: P1-P33, P40-P54, P58-P63 (pairs v4)
+    mutate.main(only_pairs)
     ok = True
     for pair, _, expected, desc, _ in mutate.MUTATIONS:
+        if only_pairs and pair not in only_pairs:
+            continue
         res = check(pair, lease=HERE / "mutations" / pair / "Lease.tla",
-                    run_id=f"{pair}-mutation")
+                    run_id=f"{pair}-mutation", only=expected)
         good = res == f"FAIL {expected}"
+        note = ""
+        if good and expected == "C3_5":
+            # derives: C3.5; pairs v4 "the decision-replay check must report it" -- the counterexample
+            # with the unmutated witness of the same schedule
+            rc, txt = replay([OBS / f"{pair}-mutation.jsonl", OBS / f"{pair}.jsonl"])
+            good = rc != 0
+            note = "; replay: " + (txt.strip().splitlines()[-1] if txt.strip() else "no output")
+            (OBS / f"{pair}-mutation-replay.txt").write_text(txt)
         ok &= good
-        print(f"{pair} mutation: {res}" + ("" if good else f"   <-- expected FAIL {expected}"))
+        print(f"{pair} mutation: {res}{note}" + ("" if good else f"   <-- expected FAIL {expected}"
+                                                 + (" reported by the replay" if expected == "C3_5" else "")))
     return ok
 
 
+def replay_all():
+    # derives: C3.5 -- every unmutated observe file of this side, in one invocation (part 3 is across runs)
+    files = sorted(p for p in OBS.glob("*.jsonl") if "-mutation" not in p.name)
+    rc, txt = replay(files)
+    (OBS / "decision-replay.txt").write_text(txt)
+    print(txt.strip().splitlines()[-1] if txt.strip() else "decision-replay: no output")
+    return rc == 0
+
+
 def main(argv):
     if len(argv) != 2:
         print(__doc__, file=sys.stderr)
         return 2
     if argv[1] == "--mutations":
         return 0 if mutations() else 1
+    if argv[1].startswith("--mutation="):
+        return 0 if mutations(tuple(argv[1].split("=", 1)[1].split(","))) else 1
+    if argv[1] == "--replay":
+        return 0 if replay_all() else 1
     if argv[1] == "--all":
         ok = True
         for n in ORDER:
             res = check(n)
-            print(f"{n}: {res}")
+            print(f"{n}: {res}", flush=True)
             ok &= res == "PASS"
         ok &= mutations()
+        ok &= replay_all()
         return 0 if ok else 1
     res = check(argv[1])
     print(res)

````
## U06: `model/Lease.tla`
````diff
diff --git a/model/Lease.tla b/model/Lease.tla
index 41819cc..baf72fb 100644
--- a/model/Lease.tla
+++ b/model/Lease.tla
@@ -30,7 +30,9 @@ CONSTANTS
     Steps,      \* derives: F1.1, F1.2, F1.3 -- compiled schedule steps
     EndTrig,    \* derives: F1.1, F1.2, F1.3 -- compiled end trigger
     MaxTerm,    \* derives: C1.1, C1.4 -- bound on grantor terms (state-space bound)
-    MaxDups     \* derives: C1.2, C1.3 -- bound on duplicated write deliveries
+    MaxDups,    \* derives: C1.2, C1.3 -- bound on duplicated write deliveries
+    NodeSeq,    \* derives: C1.4, C3.4 -- the lease nodes in a fixed order (for the progress measure)
+    ClientSeq   \* derives: C1.4 -- the clients in a fixed order (for the progress measure)
 
 VARIABLES
     \* --- environment state (derives: F1.1, F1.2, F1.3, F2.1, F2.2)
@@ -1206,6 +1208,24 @@ Protocol ==
 \* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
 Next == Protocol \/ ScheduleStep
 
+\* derives: C1.4, C3.4 -- the steps Fairness makes fair: every protocol action but a duplicated delivery, and
+\* the schedule (README X3, "Fairness (X3)")
+FairNext ==
+    \/ \E n \in Nodes : Elect(n) \/ StepDown(n) \/ CheckQuorum(n) \/ Join(n)
+    \/ \E n \in Nodes, c \in Clients : Grant(n, c) \/ Resend(n, c)
+    \/ \E m \in grantMsgs : RecvGrant(m)
+    \/ \E m \in writeMsgs : StorageDecide(m, FALSE)
+    \/ \E a \in toAck : SendAck(a)
+    \/ \E a \in ackMsgs : RecvAck(a)
+    \/ \E m \in readMsgs : StorageRead(m, FALSE)
+    \/ \E a \in rToAck : SendReadAck(a)
+    \/ \E a \in rAckMsgs : RecvReadAck(a)
+    \/ \E l, x \in Nodes : Commit(l, x)
+    \/ \E n, m \in Nodes : LearnConfig(n, m)
+    \/ \E m \in rcMsgs : RecvReconfig(m)
+    \/ \E x \in Nodes : \E a \in owed[x] : ReplyOp(x, a)
+    \/ ScheduleStep
+
 \* derives: C1.4 -- weak fairness on every protocol action and on the schedule
 \* (the environment does eventually perform each scheduled step whose trigger held).
 \* X2: every condition is named, with its justification, in README "Fairness (X2)". Each
@@ -1409,15 +1429,47 @@ C3_4 == /\ \A x \in Receivers : (<>[]GoodR(x)) => [](pend[x] # NoPend => <>(pend
              (<>[](up[x] /\ Conn(x, o))) => [](Owes(x, o) => <>~Owes(x, o))
 
 \* derives: C1.4, C3.4 (README X3 "Liveness, checked at terminal states") -- the state graph of this model
-\* has no cycle but stuttering (Acyclic, checked on every run). Then every weakly fair behaviour
-\* ends stuttering in a state where no step is enabled, and C1_4 and C3_4 hold iff at every such
+\* has no cycle but stuttering (Progress, checked on every run). Then every behaviour that satisfies
+\* Fairness ends stuttering in a state where no fair step (FairNext) is enabled, and every path to
+\* such a state, stuttering there, satisfies Fairness; so C1_4 and C3_4 hold iff at every such
 \* reachable state each premise implies its conclusion. These invariants say that; ENABLED is
 \* evaluated only where a premise holds and its conclusion does not.
-C1_4T == (\E c \in Clients : Good(c) /\ pending[c]) => ENABLED <<Next>>_vars
+C1_4T == (\E c \in Clients : Good(c) /\ pending[c]) => ENABLED <<FairNext>>_vars
 \* derives: C3.4
 C3_4T == (\/ \E x \in Receivers : GoodR(x) /\ pend[x] # NoPend
-          \/ \E x \in Receivers, o \in Ops : up[x] /\ Conn(x, o) /\ Owes(x, o)) => ENABLED <<Next>>_vars
-\* derives: C1.4, C3.4 -- the spec without fairness, for the acyclicity check
+          \/ \E x \in Receivers, o \in Ops : up[x] /\ Conn(x, o) /\ Owes(x, o)) => ENABLED <<FairNext>>_vars
+\* derives: C1.4, C3.4 (README X3 "Liveness, checked at terminal states") -- a progress measure: every
+\* step but stuttering strictly increases it, lexicographically, so the state graph has no cycle but
+\* stuttering. The components, in order: the schedule position; each node's promise (Elect, Join,
+\* StepDown raise promises and no protocol step lowers one); the number of non-leaders (CheckQuorum);
+\* grants; each client's request phase (waiting with no reply in flight < waiting with one < answered
+\* with one in flight < answered); storage write and read decisions; commits; each node's recorded
+\* configurations; and, decreasing, the acks queued and in flight, the read acks queued and in flight,
+\* the requests in flight, and each node's replies owed. Per-node and per-client values are separate
+\* components (none of them falls in a protocol step), which keeps the measure cheap to compute.
+\* derives: C1.4
+Phase(c) == LET inflight == \E m \in grantMsgs : m.c = c IN
+            IF pending[c] THEN (IF inflight THEN 1 ELSE 0) ELSE (IF inflight THEN 2 ELSE 3)
+\* derives: C1.4, C3.4 -- f applied along the sequence S
+Along(S, f(_)) == [i \in 1..Len(S) |-> f(S[i])]
+\* derives: C1.4, C3.4
+Measure == <<pc>> \o Along(NodeSeq, LAMBDA n : promised[n])
+           \o <<Cardinality({n \in Nodes : ~leader[n]}), Len(grants)>>
+           \o Along(ClientSeq, Phase)
+           \o <<Len(decisions), Len(rdecisions), Len(commits)>>
+           \o Along(NodeSeq, LAMBDA n : Len(cfg[n]))
+           \o <<-(2 * Cardinality(toAck) + Cardinality(ackMsgs)), -(2 * Cardinality(rToAck) + Cardinality(rAckMsgs)),
+               -Cardinality(rcMsgs)>>
+           \o Along(NodeSeq, LAMBDA n : -Cardinality(owed[n]))
+\* derives: C1.4, C3.4 -- lexicographic order on equal-length tuples of integers
+LexGt(a, b) == \E i \in 1..Len(a) : a[i] > b[i] /\ \A j \in 1..(i - 1) : a[j] = b[j]
+\* derives: C1.4, C3.4 -- checked on every transition of every run (an action property, no liveness search)
+\* (every step of Spec is a Next step or stutters, so "Next =>" is not written: evaluating Next as a
+\* predicate on each transition cost ten times the search)
+Progress == [][LET after == Measure'
+                   before == Measure IN LexGt(after, before)]_vars
+
+\* derives: C1.4, C3.4 -- the spec without fairness, for the acyclicity check (a cross-check of Progress)
 SpecNF == Init /\ [][Next]_vars
 \* derives: C1.4, C3.4 -- every behaviour eventually stops changing the fingerprinted state, i.e. the
 \* state graph has no cycle other than stuttering (a violation is a lasso through a real cycle)

````
## U07: `model/compile.py`
````diff
diff --git a/model/compile.py b/model/compile.py
index b36e1bf..56a556f 100644
--- a/model/compile.py
+++ b/model/compile.py
@@ -366,6 +366,47 @@ def tla_step(st, trig):
     return tla(rec)[:-1] + f", l |-> {links}]"
 
 
+def reach_probes(steps, procs):
+    # derives: C3.1, C3.4, C3.7, C3.8, F3.1, F3.2, F3.3 (reach) -- what each schedule needs the model to reach:
+    # every epoch its requests could commit, a grant under a changed configuration, each refusal reason a
+    # request could get, re-admission where an amnesic node may agree to a commit listing it, an amnesic
+    # incarnation, a timer fired early by a forward clock step, and the number of grants it requests
+    kinds = [a["kind"] for a, _ in steps]
+    reqs = [a for a, _ in steps if a["kind"] == "reconfig"]
+    out = []
+    for k in range(1, len(reqs) + 1):
+        out.append((f"epoch{k}", f"\\E i \\in 1..Len(commits) : commits[i].rec.ep = {k}", f"epoch {k} committed"))
+    if reqs and "request" in kinds[kinds.index("reconfig"):]:
+        out.append(("grantNewEpoch", "\\E i \\in 1..Len(grants) : grants[i].ep >= 1", "a grant under epoch 1 or later"))
+    valid = [a for a in reqs if a["mem"] and a["mem"] <= set(procs["lease"])]
+    sel = {"grantor", "non-grantor", "non-member"}
+    same = any(a["p"] == b["p"] or a["p"] in sel or b["p"] in sel
+               for i, a in enumerate(reqs) for b in reqs[i + 1:])
+    need = {"invalid": len(valid) < len(reqs), "busy": len(reqs) >= 2 and same, "superseded": len(valid) >= 2}
+    for reason in ("invalid", "busy", "superseded"):
+        if need[reason]:
+            out.append((f"refused_{reason}", f'\\E i \\in 1..Len(refusals) : refusals[i].reason = "{reason}"',
+                        f"a request refused as {reason}"))
+    if "amnesia" in kinds:
+        out.append(("amnesic", "\\E n \\in Nodes : inc[n] > 0", "an amnesic incarnation"))
+        # re-admission is needed only where a request after an amnesic restart names the restarted node
+        later = [(a, b) for i, (a, _) in enumerate(steps) if a["kind"] == "amnesia"
+                 for b, _ in steps[i + 1:] if b["kind"] == "reconfig"]
+        if any(a["p"] in b["mem"] or a["p"] in ("grantor", "non-grantor") for a, b in later):
+            out.append(("readmit", "\\E i \\in 1..Len(commits) : commits[i].rec.rdm # {}", "a commit that re-admits"))
+        if reqs:
+            out.append(("readmitNot", "\\E i \\in 1..Len(commits) : commits[i].rec.rdm = {} /\\ \\E n \\in Nodes : inc[n] > 0",
+                        "a commit after an amnesic restart that re-admits nobody"))
+    if any(a["kind"] == "clock" and a["s"] > 0 for a, _ in steps):
+        out.append(("early", "\\E n \\in Nodes : early[n]", "a lease node's timer fired early by a forward clock step"))
+    if any(a["kind"] == "clock" for a, _ in steps):
+        out.append(("clockStepped", "\\E p \\in DOMAIN off : off[p] # 0", "a clock offset after a step"))
+    n = kinds.count("request")
+    if n:
+        out.append((f"grants{n}", f"Len(grants) >= {n}", f"{n} grants (one per request step)"))
+    return out
+
+
 INVARIANTS = ["TypeOK", "C1_1", "C1_2", "C1_3", "C2_1", "C2_2", "C3_1", "C3_7", "C3_8", "C3_5",
               "TermUnique", "C1_1order", "TermHeadroom"]   # derives: every clause; README X3 "What is checked"
 
@@ -439,6 +480,9 @@ def compile_schedule(path, outdir, lease, only=None):
         f"MCReqSets == {reqsets_tla}",
         "\\* derives: C3.4",
         f"MCReceivers == {tla(receivers)}",
+        "\\* derives: C1.4, C3.4 -- fixed orders for the progress measure",
+        f"MCNodeSeq == {tla(sorted(procs['lease']))}",
+        f"MCClientSeq == {tla(sorted(procs['clients']))}",
         "\\* derives: F1.1, F1.2, F1.3, F2.1, F2.2, F3.x",
         "MCSteps == <<",
         ",\n".join("    " + tla_step(a, t) for a, t in steps),
@@ -453,7 +497,7 @@ def compile_schedule(path, outdir, lease, only=None):
         "  Nodes <- MCNodes\n  Init0 <- MCInit0\n  Clients <- MCClients\n  Store <- MCStore\n"
         "  Ops <- MCOps\n  ReqSets <- MCReqSets\n  Receivers <- MCReceivers\n"
         f'  Key = "k"\n  Lifetime = {lifetime}\n  Steps <- MCSteps\n  EndTrig <- MCEnd\n'
-        f"  MaxTerm = {max_term}\n  MaxDups = {max_dups}\n"
+        f"  MaxTerm = {max_term}\n  MaxDups = {max_dups}\n  NodeSeq <- MCNodeSeq\n  ClientSeq <- MCClientSeq\n"
         "SPECIFICATION Spec\n"
         "VIEW View\n"   # derives: (bounds) -- README X3 "Bounds": lastEv is not fingerprinted
     )
@@ -465,7 +509,7 @@ def compile_schedule(path, outdir, lease, only=None):
     terms = [p + "T" for p in props]
     (outdir / "MC.cfg").write_text(
         "\\* derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8\n" + consts +
-        "INVARIANT " + " ".join(INVARIANTS[:-2] + terms + INVARIANTS[-2:]) + "\n")
+        "INVARIANT " + " ".join(INVARIANTS[:-2] + terms + INVARIANTS[-2:]) + "\n" + "PROPERTY Progress\n")
     (outdir / "Acyclic.cfg").write_text(
         "\\* derives: C1.4, C3.4\n" + consts.replace("SPECIFICATION Spec\n", "SPECIFICATION SpecNF\n") +
         "PROPERTY Acyclic\n")
@@ -475,14 +519,23 @@ def compile_schedule(path, outdir, lease, only=None):
     if only is not None:
         inv = only + "T" if only in ("C1_4", "C3_4") else only
         (outdir / "MC_only.cfg").write_text(f"\\* derives: {only} (mutation run)\n" + consts +
-                                            f"INVARIANT TypeOK {inv} TermHeadroom\n")
+                                            f"INVARIANT TypeOK {inv} TermHeadroom\n" +
+                                            ("PROPERTY Progress\n" if only in ("C1_4", "C3_4") else ""))
+    # derives: (reach; README X3 "Reach") -- probes: each RP_x is a state the schedule needs the model to be
+    # able to reach; Reach_x.cfg checks ~RP_x, so a violation is a witness that x is reachable
+    probes = reach_probes(steps, procs)
+    mc = (outdir / "MC.tla").read_text().replace("====\n", "".join(
+        f"\\* derives: (reach) -- {why}\nRP_{k} == {p}\nNRP_{k} == ~RP_{k}\n" for k, p, why in probes) + "====\n")
+    (outdir / "MC.tla").write_text(mc)
+    for k, _, _ in probes:
+        (outdir / f"Reach_{k}.cfg").write_text("\\* derives: (reach)\n" + consts + f"INVARIANT NRP_{k}\n")
     (outdir / "Witness.cfg").write_text(
         "\\* derives: F1.1, F1.2, F1.3\n" + consts + "INVARIANT NotEnded\n")
     (outdir / "Done.cfg").write_text(
         "\\* derives: F1.1, F1.2, F1.3\n" + consts + "INVARIANT NotDone\n")
     meta = {"schedule": doc["schedule"], "derives": doc.get("derives", []),
             "processes": procs, "bound": bound, "max_term": max_term, "max_dups": max_dups,
-            "lifetime": lifetime, "props": props,
+            "lifetime": lifetime, "props": props, "probes": [[k, why] for k, _, why in probes],
             "steps": [{"do": s["do"], "at": s["at"]} for s in doc["steps"]], "end": doc["end"]}
     (outdir / "schedule.json").write_text(json.dumps(meta, indent=1, default=list))
     return meta

````
## U08: `model/mutate.py`
````diff
diff --git a/model/mutate.py b/model/mutate.py
index ab16f7f..85d0779 100644
--- a/model/mutate.py
+++ b/model/mutate.py
@@ -488,7 +488,15 @@ Protocol ==
      [("str", r"""    /\ inc' = [inc EXCEPT ![n] = @ + 1]""",
        r"""    /\ inc' = inc \* mutation: P48 amnesia not told apart from an ordinary restart""")]),
     ("P49", "C1.2, F3.1", "C1_2",
-     'storage resets its ledger to 0 whenever a configuration commit is decided (a new configuration as a new fencing era)',
+     'storage keeps one fence per configuration epoch: a write is compared only with the tokens accepted under its own epoch (re-placed, PREDICTIONS-x3.md amendment 1)',
+     [("str", r"""    /\ LET acc == m.t >= highest""",
+       r"""    \* mutation: P49 one fence per configuration epoch (the epoch travels with the token from its grant)
+    /\ LET TokEp(t) == IF \E i \in 1..Len(grants) : grants[i].token = t
+                       THEN grants[CHOOSE i \in 1..Len(grants) : grants[i].token = t].ep ELSE 0
+           acc == m.t >= Max({decisions[j].token : j \in {i \in 1..Len(decisions) :
+                                decisions[i].outcome = "accept" /\ TokEp(decisions[i].token) = TokEp(m.t)}})""")]),
+    ("P49a", "C1.2, F3.1", "PASS",
+     '(pre-registered as P49, FAIL C1_2; printed PASS: not on a path P49 exercises; kept as a record, PREDICTIONS-x3.md amendment 1) storage resets its ledger to 0 whenever a configuration commit is decided',
      [("str", r"""                          myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
                           toAck, grants, rq, issued, decisions, told>>
            /\ Emit(<<[event |-> "Commit",""",
@@ -590,6 +598,8 @@ Protocol ==
 ]
 
 EXPECTED = {p: inv for p, _, inv, _, _ in MUTATIONS}
+# derives: pairs v4 -- the clause a record-only mutation is checked against
+CLAUSE = {"P49a": "C1_2"}
 
 
 def replace_def(src, name, new):

````
## U09: `model/run.py`
````diff
diff --git a/model/run.py b/model/run.py
index fdb6931..bc298a4 100644
--- a/model/run.py
+++ b/model/run.py
@@ -29,8 +29,9 @@ import mutate  # noqa: E402
 
 # derives: C1.1-C1.4, C2.1, C2.2, F2.1, F2.2, C3.x, F3.x -- every shared schedule (P13-P18 added for contract v2,
 # P19-P30 for failure model v2, P31-P33, P40-P54, P58-P63 for contract v3 / failure model v3)
-ORDER = ([f"P{i}" for i in range(1, 34)] + [f"P{i}" for i in range(40, 55)] + [f"P{i}" for i in range(58, 64)]
-         + ["false-suspicion-v1"] + [f"H{i}" for i in range(7, 11)])  # H7-H10 shared after X2
+ORDER = ([f"P{i}" for i in range(1, 34) if i != 31] + [f"P{i}" for i in range(40, 55)] + [f"P{i}" for i in range(58, 64)]
+         + ["false-suspicion-v1"] + [f"H{i}" for i in range(7, 11)]  # H7-H10 shared after X2
+         + ["P31"])  # X3: P31 last, its space is by far the largest (README X3 "Results")
 
 
 def find_schedule(name):
@@ -42,7 +43,7 @@ def find_schedule(name):
 
 def tlc(dirp, cfg):
     # derives: C1.1, C1.2, C1.3, C1.4
-    jtmp = WORK / "jtmp"
+    jtmp = dirp / "jtmp"   # per run: TLC extracts its standard modules here, and runs may be concurrent
     jtmp.mkdir(parents=True, exist_ok=True)
     cmd = ["java", f"-Xmx{HEAP}", f"-Djava.io.tmpdir={jtmp}", "-XX:+UseParallelGC", "-cp", JAR, "tlc2.TLC",
            "-deadlock", "-cleanup", "-workers", os.environ.get("TLC_WORKERS", "8"),
@@ -55,6 +56,9 @@ def tlc(dirp, cfg):
 
 def verdict(out):
     # derives: C1.1, C1.2, C1.3, C1.4, C3.x -- classify TLC's output
+    if "Action property Progress is violated" in out:
+        # derives: C1.4, C3.4 -- the progress measure did not increase on some step (README X3)
+        return "NOPROGRESS", "Progress"
     m = re.search(r"Invariant (\w+) is violated", out)
     if m and m.group(1) == "TermHeadroom":
         return "UNEXPLAINED", "MaxTerm bound reached; raise it before reading this run"
@@ -95,7 +99,19 @@ def check(name, lease=None, run_id=None, quiet=False, only=None):
     if v == "FAIL" and inv in ("C1_4T", "C3_4T"):
         inv = inv[:-1]   # derives: C1.4, C3.4 -- a reachable terminal state where the premise holds and the conclusion does not
     acyc = ""
-    if v == "PASS" and (only is None or only in ("C1_4", "C3_4")):
+    noprog = v == "NOPROGRESS"
+    if noprog:
+        # derives: C1.4, C3.4 -- TLC stopped at the Progress violation: check the invariants without it,
+        # then look for a cycle directly
+        (dirp / "MC_np.cfg").write_text((dirp / ("MC_only.cfg" if only else "MC.cfg")).read_text()
+                                        .replace("PROPERTY Progress\n", ""))
+        out = tlc(dirp, "MC_np.cfg")
+        v, inv = verdict(out)
+        if v == "FAIL" and inv in ("C1_4T", "C3_4T"):
+            inv = inv[:-1]
+    if v == "PASS" and not noprog and (only is None or only in ("C1_4", "C3_4")):
+        acyc = ", progress measure holds"
+    if v == "PASS" and noprog and (only is None or only in ("C1_4", "C3_4")):
         # derives: C1.4, C3.4 (README X3) -- the terminal-state forms are exact only if the state graph has
         # no cycle but stuttering; if it has one, fall back to TLC's liveness check under Spec's fairness
         aout = tlc(dirp, "Acyclic.cfg")
@@ -119,7 +135,7 @@ def check(name, lease=None, run_id=None, quiet=False, only=None):
             elif lv != "PASS":
                 return f"UNEXPLAINED liveness check: {linv}"
         elif "Model checking completed. No error has been found." in aout:
-            acyc = ", acyclic"
+            acyc = ", progress measure fails but acyclic"
         else:
             return "UNEXPLAINED acyclicity check: " + verdict(aout)[1]
     distinct, depth = stats(out)
@@ -170,9 +186,13 @@ def mutations(only_pairs=()):
     for pair, _, expected, desc, _ in mutate.MUTATIONS:
         if only_pairs and pair not in only_pairs:
             continue
-        res = check(pair, lease=HERE / "mutations" / pair / "Lease.tla",
-                    run_id=f"{pair}-mutation", only=expected)
-        good = res == f"FAIL {expected}"
+        # derives: pairs v4 -- a suffixed pair (P49a) is a superseded mutation kept as a record, run on its
+        # pair's schedule; its expected line is the result it printed (PREDICTIONS-x3.md amendment 1)
+        sched = re.sub(r"[a-z]$", "", pair)
+        clause = mutate.CLAUSE.get(pair, expected)
+        res = check(sched, lease=HERE / "mutations" / pair / "Lease.tla",
+                    run_id=f"{pair}-mutation", only=clause)
+        good = res == (expected if expected == "PASS" else f"FAIL {expected}")
         note = ""
         if good and expected == "C3_5":
             # derives: C3.5; pairs v4 "the decision-replay check must report it" -- the counterexample
@@ -182,7 +202,7 @@ def mutations(only_pairs=()):
             note = "; replay: " + (txt.strip().splitlines()[-1] if txt.strip() else "no output")
             (OBS / f"{pair}-mutation-replay.txt").write_text(txt)
         ok &= good
-        print(f"{pair} mutation: {res}{note}" + ("" if good else f"   <-- expected FAIL {expected}"
+        print(f"{pair} mutation: {res}{note}" + ("" if good else f"   <-- expected {'' if expected == 'PASS' else 'FAIL '}{expected}"
                                                  + (" reported by the replay" if expected == "C3_5" else "")))
     return ok
 
@@ -196,6 +216,24 @@ def replay_all():
     return rc == 0
 
 
+def reach(name):
+    # derives: (reach; README X3 "Reach") -- run every reach probe of a schedule; each must be reachable
+    path = find_schedule(name)
+    dirp = WORK / f"{name}-reach"
+    meta = compiler.compile_schedule(path, dirp, HERE / "Lease.tla")
+    rows = []
+    for k, why in meta["probes"]:
+        out = tlc(dirp, f"Reach_{k}.cfg")
+        hit = f"Invariant NRP_{k} is violated" in out
+        dm = re.search(r"^State (\d+):", out[::-1] and "\n".join(reversed(out.splitlines())), re.M) if hit else None
+        depth = dm.group(1) if dm else "-"
+        rows.append((k, why, "reachable" if hit else ("NOT reachable" if "No error has been found" in out
+                                                         else "UNEXPLAINED " + verdict(out)[1]), depth))
+    for k, why, res, d in rows:
+        print(f"{name}\t{k}\t{res}\t(state {d})\t{why}")
+    return all(r[2] == "reachable" for r in rows)
+
+
 def main(argv):
     if len(argv) != 2:
         print(__doc__, file=sys.stderr)
@@ -204,6 +242,11 @@ def main(argv):
         return 0 if mutations() else 1
     if argv[1].startswith("--mutation="):
         return 0 if mutations(tuple(argv[1].split("=", 1)[1].split(","))) else 1
+    if argv[1].startswith("--reach="):
+        ok = True
+        for n in argv[1].split("=", 1)[1].split(","):
+            ok &= reach(n)
+        return 0 if ok else 1
     if argv[1] == "--replay":
         return 0 if replay_all() else 1
     if argv[1] == "--all":

````
## U10: `model/Lease.tla`
````diff
diff --git a/model/Lease.tla b/model/Lease.tla
index baf72fb..5568cd7 100644
--- a/model/Lease.tla
+++ b/model/Lease.tla
@@ -68,9 +68,11 @@ VARIABLES
     grants,     \* derives: C1.1, C3.5, C3.7 -- sequence of every grant issued, with its recorded inputs
     \* --- routing fix (derives: C1.1, C1.4, F2.1, F2.2; format v4 L3; observe v4 "Grants and retransmission")
     rq,         \* derives: C1.4 -- rq[c]: number of requests c has made (identifies the current request)
-    issued,     \* derives: C1.1, C1.4, F2.2 -- grants each leader issued, [n, c, r, t, g]: leader n in
+    issued,     \* derives: C1.1, C1.4, F2.2, F3.3 -- grants each leader issued, [n, c, r, t, g]: leader n in
                 \* term g answered c's request r with token t. Volatile in a real node, but keyed by
-                \* term, and a node never leads the same term twice, so its loss on crash is not modelled
+                \* term, and a node never leads the same term twice, so its loss on crash is not modelled.
+                \* X3: after an amnesic restart the node leads again only once re-admitted, elected at a
+                \* term above every promise of its quorum; TermUnique checks the consequence for grants
     decisions,  \* derives: C1.2, C1.3, C3.5 -- sequence of every storage decision
     told,       \* derives: C1.3 -- set of writes clients were told succeeded
     \* --- schedule driver (derives: F1.1, F1.2, F1.3)
@@ -994,6 +996,8 @@ Crash(p) ==
     /\ lastEv' = <<[event |-> "Fault", cell |-> "F1.1", action |-> "crash", target |-> p]>>
 
 \* derives: F1.1 -- restart with durable state only (a restarted client has no grant)
+\* X3 (derives: F1.1, F3.3): this is the ordinary restart, which keeps a lease node's durable state and its
+\* incarnation (contract v3 "Incarnation"); a restart with no durable state is AmnesicRestart (F3.3)
 Restart(p) ==
     /\ UNCHANGED rvars  \* derives: C2.1, C2.2 -- reads untouched
     /\ UNCHANGED kvars
@@ -1411,13 +1415,15 @@ C1_4 == \A c \in Clients : (<>[]Good(c)) => [](pending[c] => <>(~pending[c]))
 \* more than half of the globally committed configuration's members are eligible; and x, an eligible
 \* majority of that configuration and an eligible majority of the requested set are up and connected
 \* to each other
+\* (C stands for the union of the two majorities: an up set, connected to each other and to x, holding an
+\* eligible majority of each; one enumeration instead of one per pair of majorities)
 GoodR(x) == pend[x] # NoPend =>
               /\ up[x]
               /\ MajOf({q \in Nodes : GElig(q)}, GLatest.mem)
-              /\ \E Q1 \in SUBSET {q \in Nodes : GElig(q) /\ up[q]},
-                    Q2 \in SUBSET {q \in Nodes : EligIn(q, pend[x].mem, GRdm(GLatest.ep, 0)) /\ up[q]} :
-                   /\ MajOf(Q1, GLatest.mem) /\ MajOf(Q2, pend[x].mem)
-                   /\ \A p, q \in Q1 \cup Q2 \cup {x} : Conn(p, q)
+              /\ \E C \in SUBSET {q \in Nodes : up[q] /\ Conn(q, x)} :
+                   /\ MajOf({q \in C : GElig(q)}, GLatest.mem)
+                   /\ MajOf({q \in C : EligIn(q, pend[x].mem, GRdm(GLatest.ep, 0))}, pend[x].mem)
+                   /\ \A p, q \in C : Conn(p, q)
 \* derives: C3.4 -- an outcome x owes operator o, or has sent it and o has not yet received it
 Owes(x, o) == (\E a \in owed[x] : a.op = o) \/ (\E a \in opMsgs : a.op = o /\ a.x = x)
 \* derives: C3.4 -- (b): a request pending at x under the premise is eventually committed or refused
@@ -1465,9 +1471,9 @@ Measure == <<pc>> \o Along(NodeSeq, LAMBDA n : promised[n])
 LexGt(a, b) == \E i \in 1..Len(a) : a[i] > b[i] /\ \A j \in 1..(i - 1) : a[j] = b[j]
 \* derives: C1.4, C3.4 -- checked on every transition of every run (an action property, no liveness search)
 \* (every step of Spec is a Next step or stutters, so "Next =>" is not written: evaluating Next as a
-\* predicate on each transition cost ten times the search)
-Progress == [][LET after == Measure'
-                   before == Measure IN LexGt(after, before)]_vars
+\* predicate on each transition cost ten times the search; the measures are bound by a quantifier,
+\* which TLC evaluates once, where a LET was re-evaluated at each use)
+Progress == [][\E after \in {Measure'}, before \in {Measure} : LexGt(after, before)]_vars
 
 \* derives: C1.4, C3.4 -- the spec without fairness, for the acyclicity check (a cross-check of Progress)
 SpecNF == Init /\ [][Next]_vars

````
## U11: `model/compile.py`
````diff
diff --git a/model/compile.py b/model/compile.py
index 56a556f..91b3a52 100644
--- a/model/compile.py
+++ b/model/compile.py
@@ -374,14 +374,17 @@ def reach_probes(steps, procs):
     kinds = [a["kind"] for a, _ in steps]
     reqs = [a for a, _ in steps if a["kind"] == "reconfig"]
     out = []
-    for k in range(1, len(reqs) + 1):
+    nvalid = sum(1 for a in reqs if a["mem"] and a["mem"] <= set(procs["lease"]))
+    for k in range(1, nvalid + 1):   # an invalid request never commits
         out.append((f"epoch{k}", f"\\E i \\in 1..Len(commits) : commits[i].rec.ep = {k}", f"epoch {k} committed"))
     if reqs and "request" in kinds[kinds.index("reconfig"):]:
         out.append(("grantNewEpoch", "\\E i \\in 1..Len(grants) : grants[i].ep >= 1", "a grant under epoch 1 or later"))
     valid = [a for a in reqs if a["mem"] and a["mem"] <= set(procs["lease"])]
     sel = {"grantor", "non-grantor", "non-member"}
-    same = any(a["p"] == b["p"] or a["p"] in sel or b["p"] in sel
-               for i, a in enumerate(reqs) for b in reqs[i + 1:])
+    # two valid requests can meet at one receiver unless they name different nodes, or one goes to
+    # `grantor` and the other to `non-grantor`
+    same = any(a["p"] == b["p"] or ((a["p"] in sel or b["p"] in sel) and {a["p"], b["p"]} != {"grantor", "non-grantor"})
+               for i, a in enumerate(valid) for b in valid[i + 1:])
     need = {"invalid": len(valid) < len(reqs), "busy": len(reqs) >= 2 and same, "superseded": len(valid) >= 2}
     for reason in ("invalid", "busy", "superseded"):
         if need[reason]:

````
## U12: `model/run.py`
````diff
diff --git a/model/run.py b/model/run.py
index bc298a4..10a4355 100644
--- a/model/run.py
+++ b/model/run.py
@@ -47,6 +47,9 @@ def tlc(dirp, cfg):
     jtmp.mkdir(parents=True, exist_ok=True)
     cmd = ["java", f"-Xmx{HEAP}", f"-Djava.io.tmpdir={jtmp}", "-XX:+UseParallelGC", "-cp", JAR, "tlc2.TLC",
            "-deadlock", "-cleanup", "-workers", os.environ.get("TLC_WORKERS", "8"),
+           # derives: (bounds) -- TLC deletes consumed queue pages only at a checkpoint; P31's queue
+           # outgrew the disk at the default 30 minutes (README X3 "Bounds and limits")
+           "-checkpoint", os.environ.get("TLC_CHECKPOINT", "5"),
            "-metadir", str(dirp / "states"), "-config", cfg, "MC.tla"]
     log = dirp / (cfg.replace(".cfg", "") + ".out")
     with open(log, "w") as f:   # streamed, so a long run can be watched

````