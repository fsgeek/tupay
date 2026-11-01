# Rating task: measure 7 (interpretations contradicted), one rater, independent

An author kept a README listing its **interpretations** of earlier inputs. The inputs then changed (service
contract and failure model to version 3, given in full below) and the author adapted its code. You get the
README **as it was before the change** and the **code diff** of the adaptation. You do not get the author's
updated README, on purpose: judge from the diff, not from the author's account of it.

For each listed entry of the old README (ids as numbered or labelled there), give one verdict:
- **CONTRADICTED**: the adapted code now handles some situation the entry makes a claim about differently from
  what the entry says.
- **EXTENDED**: every claim the entry makes still holds, and the diff changed the element the entry describes so
  that it also covers situations new in version 3.
- **UNCHANGED**: neither.
Also give **already_contradicted_before**: true iff the old README itself already marks the entry superseded,
contradicted or replaced (then judge the verdict only on whether this diff changes its status again).
Read entries as written; take a named set literally.

Answer with one JSON object and nothing after it:
{"ratings": [{"entry": "<id>", "verdict": "CONTRADICTED" | "EXTENDED" | "UNCHANGED", "already_contradicted_before": true | false, "reason": "one or two sentences citing the diff"}, ...]}
Every listed id gets exactly one entry.

# Entries to rate
1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85

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
# The README before the change (`impl/README.md` at the inputs commit)
````
<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
# Implementation author — current v2, M1 history retained

The M1 implementation below was authored independently. In that round no model,
steward notes, other documentation, existing schedules, or git history were read.
The v2 round additionally reads the expressly permitted adaptation brief and
shared root schedules. No model artifact or other documentation is consulted. The brief's explicit access list supersedes AGENTS.md's
request to read and append steward seed documents.

Current v2 results: [RESULTS-v2.md](RESULTS-v2.md). All thirteen shared schedules
pass all three seeds; all twelve mutations fail their intended clauses on all
three seeds. Nothing remains blocked. The v2 section and interpretations 29–42
supersede conflicting M1 statements. Historical results below are retained.

## M1 design and plan (historical)

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
Use the existing HashiCorp Raft protocol with three nodes and durable in-memory
log/stable stores retained across node replacement. A committed FSM command
allocates each token. Two clients and one storage execute in the same OS process.
Storage retains its ledger across replacement; restarted clients lose grants.
Disconnect Raft transports and gate all client/storage traffic across a complete
bipartition. Pauses freeze client activity, while grant lifetimes continue.

Alternatives considered: an external multi-process deployment makes fault runs
slower and harder to reproduce; implementing a new quorum protocol violates the
brief. The selected in-process Raft arrangement uses a real existing protocol
with an independently implemented event-log checker.

Implementation sequence: (1) preregister and commit predictions and scoring;
(2) implement Raft, clients, storage, injectors and causal emitter; (3) implement
strict YAML compiler, all thirteen schedules, independent checkers and mutation
runner; (4) run the preregistered baseline/mutation matrix, document any
outcome-informed amendments additively; (5) commit the first complete version.

## How to run

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
`impl/run.sh false-suspicion-v1 --seeds 3`

`impl/run.sh --all --seeds 3`

`impl/run.sh --mutations --seeds 3`

Go is `/usr/local/go/bin/go`. The script changes directory to `impl/`.
V2 schedules are read from root `testbed/schedules/`; JSONL output is under
`impl/observe/`. Outputs stay under `impl/`; shared schedules are read-only. Build artifacts,
module caches and run output are ignored. The runner accepts only a shared schedule basename
with an optional `.yaml` suffix. Exit 0 means expected results;
exit 1 means an unexpected result; input/operational errors say UNEXPLAINED.

## Sampling

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
Default: three seeds, numbered 1 through N. Each seed varies workload delivery
jitter, Raft RPC timeout, and duplicate write delivery. Raft's own election
randomness is additional nondeterminism, so a seed does not promise bit-for-bit
replay. Observe traces are the replay evidence. This is bounded sampling, not
exhaustive verification. Per-seed results and mutation kills are printed.

## M1 interpretations (historical)

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
1. All generated artifacts, including the shared relative `testbed/schedules/`
   and `observe/` paths, live beneath `impl/` to respect the brief's output scope.
2. A grant is an observable committed reply. Failed or timed-out Raft operations
   may consume tokens without issuing grants. Integer gaps are permitted.
3. The contract does not require exclusive holders or specify renewal. This
   implementation waits at least the prior issued lifetime before issuing the
   next grant, making a later grant an expiry witness for pause/resume schedules.
4. Durable state is an in-memory object that survives simulated process
   replacement, not OS termination. Raft log/stable stores and storage's ledger
   survive; clients' volatile grants and pending reply inboxes do not.
5. Timeouts and real elapsed time drive the execution only. Checkers never order
   records by wall clock or by cross-process line order. Causal references and
   process sequence numbers determine observable order.
6. The schema's prose says a WriteAccept 'causes' a WriteAttempt, but its example
   and causal intent imply references point backwards: decision -> attempt ->
   grant -> request, and ack -> decision. We implement backwards references.
7. C1.1 concurrent grants without causal order are unorderable from this schema.
   The runner serializes successful grants through the grantor and links the
   previous grant into the next grant, including across incarnations. The
   checker rejects missing order evidence as UNEXPLAINED, not as a violation.
8. Liveness is tested with a finite three-second progress opportunity after
   eligible pending requests and stable connectivity. A qualifying unfulfilled
   request at that horizon fails C1.4; an unreachable schedule trigger without
   such a witness is UNEXPLAINED. This is a bounded operational interpretation
   of 'long enough', not proof of unbounded eventuality.
9. A paused holder may intentionally submit its old token after resumption;
   fencing, rather than the client's expiry check, is the protection being tested.
   `token: stale` chooses its newest superseded or expired grant and is rejected
   as an invalid workload if no such grant exists.
10. Trigger predicates remain true once observed, as the format states. Repeated
    `start` triggers are immediately enabled. Actions are serialized and fault
    events include causal trigger references. End is checked after all actions.
11. Messages crossing a cut are lost, including accept replies. Within-side
    duplicate write deliveries retain the original attempt reference. Successful
    late replies are correlated to their actual storage decision; client restart
    discards its old inbox. Paused clients retain their inbox until resumed.
12. The false-suspicion topology is exactly old grantor + c1 + storage against
    the remaining nodes + c2. It heals before c2 writes because storage is on
    c1's side during the cut. Its trace receives provenance validation and is
    reported as observed; ordinary contract results remain separately visible.
13. The same half-open lifetime applies to all grants (40 ms). Requests are
    retried against reachable leaders; a minority cannot issue a committed grant.
    Raft timers are operational and excluded from the observable record.
14. Crash/restart actions name explicit process IDs. Dynamic `grantor`, `holder`
    and `rest` aliases are supported in partition membership only, per format.

## Blocked

None currently. V2 runs in the full clone on impl-v2. The earlier permission
reports below are historical; the OTS stamp hook succeeds.

### Historical: Git metadata outside writable sandbox

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
The initial preregistration `git add` and `git commit` both failed before any
outcome-bearing run: Git could not create
`/home/tony/projects/tupay/.git/worktrees/tupay-impl/index.lock` (read-only file
system). This linked worktree's administrative directory is outside the writable
roots. No approval escalation is available. No first-version commit or hook
stamp can be produced in this environment. The preregistration gate therefore
also blocks scored baseline/mutation runs. Implementation and preparatory
source/dependency work continue. No outcome has informed this entry.

## Additional interpretations from source review (no outcomes)

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
15. Tokens are committed Raft log indices, rather than a separate persistent
    counter. Configuration and election entries cause legal gaps. The term is
    the committed entry's Raft term. FSM snapshots retain the last allocation.
16. The three-second C1.4 opportunity cannot be inferred from a clock-free finite
    event log alone. The runner writes a separate `<run>.meta.json` certificate
    naming each pending request, the last fault reference and the stable budget.
    The checker independently verifies final connectivity and lack of a grant
    from the JSONL, but trusts the runner's duration certificate. This limitation
    is explicit; a timeout without a certificate is UNEXPLAINED. Offline checking
    uses `impl/run.sh P10 --check observe/<run>.jsonl` from the repository root,
    with paths relative to `impl/`; `--evidence` overrides the sidecar path.
17. An ack missing its acceptance reference is UNEXPLAINED when an acceptance for
    that exact attempt exists elsewhere in the trace. A ghost ack for a distinct
    attempt with no acceptance is a C1.3 failure even if another write with the
    same token was accepted. Duplicate deliveries of one attempt may each have
    a decision. The P7/P8 schedules therefore contain both an accepted write with
    a lost reply and a second write that never reaches storage.
18. Observe sequence numbers survive simulated process restart in the observer.
    They are instrumentation state, not recovered grant authority. Followers
    emit no synthetic contract events: a lease node emits a Grant when it issues
    one; all fault actions are emitted by env. 'From every process' means every
    process producing a contract event uses its own sequence, not that idle
    followers invent events outside the schema.
19. Fault records include resolved partition memberships, so alias meanings are
    recoverable directly from the trace. The original YAML retains the aliases.
    The schedule compiler rejects omitted, repeated or unresolved members and
    rejects unknown cells, fields and operations before starting the workload.
20. The runner serializes request completion and spaces grants as a workload
    policy. After a pause it waits at least a further full lifetime before the
    next grant, guaranteeing a later Grant witnesses the required pause duration.
    This timing policy is not a replacement consensus protocol or a safety
    assumption of the Raft token allocator. The observer's prior-grant reference
    records the harness's serial causal chain; it does not carry allocation
    authority between partitioned nodes.
21. Sampling covers 1–5 ms delivery jitter, 25–39 ms Raft RPC timeouts, shuffled
    due-message batches, and a one-in-three chance of a duplicate write delivery.
    Ack delivery adds 8 ms plus jitter, so a fault triggered by a decision can
    intervene. Initial grants also depend on Raft's internal election randomness.
    Network messages are gated at delivery and cut creation, so healing does not
    resurrect messages discarded across the cut. This samples a subset of the
    permitted nondeterminism and does not explore arbitrary Raft message
    duplication or every possible action delay.
22. End predicates are checked after all actions to prevent historical matches
    from skipping required actions. A final 50 ms drain observes in-flight
    replies; a step waiting for an absent trigger has a five-second operational
    guard. The event bound also stops the runner. Clause violations already
    witnessed in a partial trace remain failures even if a later trigger is
    unreachable; an absent trigger alone never kills a mutation.
23. Baseline storage starts with a zero fence for positive allocated tokens, and
    retains the last accepted value as well as the fence through storage crashes.
    Negative or arbitrary externally forged tokens are not workload actions in
    the shared format. The contract's integer tokens are represented by uint64
    Raft indices; exhausting that representation is outside these bounded runs.
24. The preregistration gate in `run.sh` requires the preregistration file in HEAD
    before it builds or runs the program. No model/implementation comparison or
    correctness attribution is performed by this author. Mutation kills are
    scored only against the predeclared clause. The schema does not itself encode
    elapsed duration, so the sidecar is a limitation of bounded liveness scoring.

<!-- derives: C1.1, C1.3, C1.4, F1.1, F1.2 -->
25. The final transport is a small adapter for HashiCorp Raft's existing RPC
    interface, using locked in-memory inboxes. It has no consensus or allocation
    logic. It atomically checks connectivity when sending, tracks endpoint
    incarnations and cut history, and gates replies separately. Pipelining is
    disabled through Raft's supported fallback. Requests delivered into an inbox
    before a cut may still be processed, but their replies are independently
    subject to the cut. Client writes sent during a cut are dropped immediately,
    even if healing precedes their sampled delivery deadline. Adapter fixtures
    separately cover lost sends, cut/heal replies, unaffected majority traffic
    and process replacement. The 1024-entry inbox is an operational resource
    limit; exhaustion is not a new admitted failure cell and must be treated as
    an operational limitation if encountered.

## Initial delivery and remaining execution (historical)

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
The Go module, pinned dependencies/checksums, compiler, causal emitter, three
Raft nodes, clients, durable ledger/value, all injectors, four checkers, thirteen
schedules, twelve named mutations, command-line runner and independent checker
fixtures have been written. Dependency retrieval, `gofmt`, and `bash -n impl/run.sh` parsing completed. The first
`go mod tidy` attempt needed a writable `GOCACHE`; retrying with all Go caches
under `impl/.cache/` completed. No compilation, vet, unit test, schedule,
false-suspicion trace or mutation run has been performed. No PASS/FAIL result or
first-version hash is claimed. The Git metadata blocker above prevents the
required preregistration commit, first-version commit and hook stamps.

After the worktree administration path becomes writable, the remaining commands
are, in order (from the repository root):

```sh
# derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
git add impl/README.md impl/PREREGISTRATION.md impl/.gitignore
git commit -m 'impl: preregister independent predictions and scoring'
impl/run.sh --all --seeds 3
impl/run.sh --mutations --seeds 3
cd impl
export GOMODCACHE="$PWD/.cache/mod"
export GOPATH="$PWD/.cache/gopath"
export GOCACHE="$PWD/.cache/build"
/usr/local/go/bin/go test -mod=readonly ./...
/usr/local/go/bin/go vet -mod=readonly ./...
cd ..
# Resolve any failures, with additive outcome-informed notes, then:
git add impl
git commit -m 'impl: first version with paired schedules and mutations'
git rev-parse HEAD
```

No `tmp/` directory, run output, binary or module cache should be committed.


## Git blocker retested before first outcome

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
The steward added the parent `/home/tony/projects/tupay/.git` writable root.
A fresh preregistration `git add`/`git commit` retry still failed creating the
same `index.lock`. Mount inspection discriminated the cause: the parent `.git`
is mounted rw, while `/home/tony/projects/tupay/.git/worktrees/tupay-impl` is a
separate ro mount. That exact worktree-administration directory also needs to be
an explicit writable root. This is the current blocker under Blocked above,
refined by direct mount evidence. No source build, test, schedule or mutation has
run; the original preregistration file and predictions remain unchanged. No
outcome has informed this entry. The branch remains impl-v1.

## Execution resumed; initial observations

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
The steward removed the filesystem sandbox; ordinary Git operations now work.
Preregistration commit: `37283d5`; its hook stamp commit: `61050e7`.
The previous Blocked entries are historical. The first build succeeded, and the
false-suspicion observation passed seeds 1–3. In the initial pair matrix P1–P9,
P11 and P12 passed all three seeds; P10 failed C1.4 on all three. Predictions
were not rewritten. A clearly outcome-informed amendment records the setup
hypothesis and a new startup-voter regression before that test is executed.
The P10 trace contains only the n1 crash and c1 request, with a qualifying finite
progress certificate. Diagnosis remains unexplained pending direct configuration
evidence; no model artifact or model comparison is involved.

## Outcome-informed bootstrap correction

<!-- derives: C1.4, F1.1 -->
The registered startup-voter regression failed before the fix: n2 and n3 each
reported an empty configuration immediately after newEngine returned. This
observation discriminates the initial P10 failure as an implementation setup
defect. The fixed grantor was not fully established before the start-triggered
crash. The correction waits until all three Raft nodes expose the exact fixed
three-voter configuration, using the existing library's replication. The fault
schedule and the original baseline/mutation predictions are unchanged.

<!-- derives: C1.1, C1.4, F1.1, F1.2 -->
26. `start` begins after the fixed grantor is initialized at all three lease
    nodes. Bootstrap/configuration replication is setup, not a workload grant.
    The setup barrier is limited to the same three-second operational horizon;
    setup failure is UNEXPLAINED, not a paired clause violation. The barrier
    applies to all schedules and mutations, without changing injected faults.

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
27. Go build caches, module caches, test temporary directories and runner output
    are directed into impl/.cache or impl/observe. The runner sets TMPDIR too.
    Normal Git metadata writes and the authorized stamp hook are part of commits;
    no alternative checkout or other project artifact is used.

<!-- derives: C1.4, F1.1 -->
Bootstrap-fix validation: the startup-voter regression now passes; P10 baseline
seeds 1, 2 and 3 each PASS. The complete Go fixture suite passes and go vet reports
no findings. The initial mutation matrix reported the predicted clause on every
pair/seed, but its P10 result alone was not discriminating because the initial
baseline also failed. A fresh complete baseline and mutation matrix follows the
fix, with the original predictions unchanged.

## Verified M1 first-version delivery (historical)

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
The complete corrected matrix is recorded in [RESULTS.md](RESULTS.md): all twelve
baseline pairs PASS on each of seeds 1, 2 and 3; all twelve mutations FAIL their
predeclared clauses on each seed (36 baseline passes, 36 expected mutation
failures, 12/12 mutations killed across three seeds). The standalone
false-suspicion observation and its repeats in --all pass all three seeds, with
complete authority provenance and both grantor incarnations. All three final
runner commands exit 0. Go build, the complete fixture suite and go vet pass.
No final UNEXPLAINED result or outstanding blocker remains. These are bounded
sample results; the finite liveness certificate limitation remains as recorded.

The bootstrap setup barrier is the only outcome-informed behavior correction.
The initial failure and all command receipts are preserved. The original
preregistration remains byte-for-byte intact, followed by its additive
outcome-informed amendment. No prediction, pair schedule, mutation, clause,
scoring rule or horizon was revised in response to a result.

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
28. Generated run outputs are ignored by default. The 159 reference runs used
    for initial/final matrices and the focused P10 verification are explicitly
    retained in this first-version commit, including their JSONL and liveness
    sidecars. JSONL keeps the shared schema without added comment records.
    `evidence/manifest.tsv` supplies per-file `# derives:` comments and SHA-256
    bindings to the originating schedule; `evidence/logs/` retains raw command
    receipts, and the provenance TSV lists each false-suspicion storage decision.
    Go caches, binaries and temporary files remain excluded. Rerunning produces
    new unique run IDs rather than overwriting reference evidence.

## Adaptation to schedule format v2

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, E2 -->
The current runner implements v2 and reads only the thirteen shared root
`testbed/schedules/` inputs. M1's private `impl/testbed/schedules/` remains history
and is never resolved by the runner. The v2 predictions were committed before
adaptation (`5d866a6`, hook stamp `202f2f4`). The adapted implementation checkpoint
is `1452107` (stamp `c398b86`). No shared input was edited.

Both required commands completed with exit 0:

```sh
# derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, E2
impl/run.sh --all --seeds 3
impl/run.sh --mutations --seeds 3
```

All 39 schedule/seed results PASS, including the observed false-suspicion run;
all 36 mutation/seed results FAIL the predicted clause. There were no schedule
or mutation prediction misses. Raw receipts, traces, horizon sidecars and shared
input hashes are retained with [RESULTS-v2.md](RESULTS-v2.md). The first fixture
suite failed because a hand-built test Engine omitted its storage identity; the
fixture was corrected and the observation recorded additively in preregistration.
The full fixture suite and go vet now pass. P7 was the only re-placed mutation.

## New interpretations for v2

The entries below supersede the conflicting schedule-location, stale-token,
sticky-trigger, partition-only-alias and fixed-end-drain statements in the M1
history above. Contract clauses and failure cells retain their original IDs.

29. Schedule arguments are basenames (optionally `.yaml`), resolved only in the
    repository-root shared directory. Private/other paths and escaping file
    symlinks are rejected; the YAML name must match its basename.
    <!-- derives: C1.1, C1.4, T1, A1, E1 -->
30. A successor trigger, including an event end, is armed immediately before the
    preceding action's synchronous effects. Thus its Request or WriteAttempt
    is eligible; older events are not. `start` fires when armed. Cursors are
    injector state; checkers still use causal and per-process order only.
    <!-- derives: C1.1, C1.3, T1, T2, E1 -->
31. T2 samples a uniform 0, 1 or 2 ms action delay while workload progresses.
    Selectors freeze when the trigger fires, before that delay and before any
    T3 readiness wait. Only one step/action is pending at a time.
    <!-- derives: C1.1, C1.4, F1.2, T1, T2, T3, A1 -->
32. T3 waits for a running target, an answered prior request in its current
    incarnation, or an available write token. A multi-target workload waits for
    all selected clients. A blocked/ineligible workload reaches the operational
    bound as UNEXPLAINED unless an independently eligible request supplies C1.4
    evidence. A restarted client's old pending request is not its new request.
    <!-- derives: C1.1, C1.2, C1.4, F1.1, F1.3, T3, E1 -->
33. `stale` means the newest client token numerically lower than the highest
    token ever granted. Expiry alone no longer qualifies, nor does merely having
    a different Grant reference. The current-token write can still exercise a
    resumed holder's old token, as the shared schedules require.
    <!-- derives: C1.1, C1.2, F1.3, T3 -->
34. Aliases work in every action target, subject to process roles: grantor is a
    lease node and holder a client. Literal/alias role mismatches reject. Aliases
    before any possible Grant reject statically; an unresolved actual binding
    rejects during incremental compilation when the trigger fires.
    <!-- derives: C1.1, C1.4, F1.1, F1.3, A1, A2 -->
35. The format defines `rest` relative to a partition but also permits it outside
    partitions. Outside a partition, this implementation reuses the rest set
    resolved for the most recent partition containing `rest`, including after
    heal. Without that context it rejects ambiguity. Group selectors expand to
    concrete actions; each concrete process must have the operation's valid
    role. A group fault emits a Fault record per concrete target.
    <!-- derives: C1.1, C1.4, F1.1, F1.2, F1.3, A1, A2 -->
36. A2 uses two-phase validation: definite explicit-state errors reject at load;
    alias-dependent state is validated against frozen concrete IDs before action
    effects. Uncertain static states are not guessed. Pause/resume retain the
    F1.3 holder/lifetime checks when applied. Invalid lease/storage pauses reject.
    <!-- derives: C1.4, F1.1, F1.3, A1, A2 -->
37. Quiescence counts requests and queued writes/acks for running, unpaused,
    current client incarnations. Paused/crashed/old-incarnation work is excluded.
    Raft maintenance RPCs are not client workload. The former unconditional
    50 ms end drain is replaced by this actual-work predicate. `end: start` is
    rejected: v2 ends are an observable event or quiescent.
    <!-- derives: C1.3, C1.4, F1.1, F1.3, T1, E1 -->
38. E1 uses a five-second operational wait and the existing three-second stable
    eligibility horizon. An unanswered eligible request is checked through C1.4,
    including when a pending step prevents reaching the end. No eligible horizon
    means UNEXPLAINED, not a liveness failure. Duration remains a trusted sidecar
    certificate, never cross-process event ordering or unbounded liveness proof.
    <!-- derives: C1.4, F1.1, F1.2, F1.3, T3, E1, E2 -->
39. A witnessed clause failure takes priority over end/trigger incompleteness
    and a later operational error. A malformed trace that cannot establish the
    failure remains UNEXPLAINED. No result attributes a model divergence.
    <!-- derives: C1.1, C1.2, C1.3, C1.4, E2 -->
40. P7 now bypasses storage acceptance after restart and enqueues a success reply
    for that unaccepted attempt. The actual C1.3 path is broken without adding a
    schedule fault or forging an acceptance event. E2 preserves the resulting
    failure if the subsequent WriteAccept trigger cannot fire. Other mutations
    retain their existing enforcing-path placement.
    <!-- derives: C1.3, F1.1, T1, E2 -->
41. P10 executes its explicit first target n1. Its descriptive comment calls
    that node a non-leader, but Raft may elect it during setup; the runner does
    not rewrite the shared action to choose another node. C1.4 covers either
    case with the connected surviving majority.
    <!-- derives: C1.4, F1.1, A1 -->
42. V2 runs have a v2 marker in their unique IDs and require committed v2
    preregistration. M1 receipts stay historical. Git's unavailable GPG signer
    is disabled only for each commit command; the required OTS post-commit hook
    still runs and adds its stamp commit. The entire round stays in this clone.
    <!-- derives: C1.1, C1.2, C1.3, C1.4, T1, A1, E1, E2 -->

## V2 timing and blockers

<!-- derives: C1.1, C1.2, C1.3, C1.4, T1, T2, T3, A1, A2, E1, E2 -->
Wall-clock measurement began at 2026-10-20 23:33:13 UTC, before reading the brief.
The final reported elapsed time includes the adapted-version commit and its
stamp hook. It is human workflow metadata, never observe ordering. Blocked: none.

## Schedule format v2.1 — current round

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, A1, A2, E1, E2 -->
This section is additive; the prior rounds above remain historical. The current
checkout is the fresh full clone on impl-v2.1. Predictions were committed first
as `dc93d1e` (OTS stamp `1dc4570`), and the implementation checkpoint is `9ff6584`
(stamp `4b9688d`). All commits in this round use normal signing, without signing
configuration overrides. No shared input was edited and no out-of-brief artifact
was read.

The two required commands each exit 0:

```sh
# derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, A1, A2, E1, E2
impl/run.sh --all --seeds 3
impl/run.sh --mutations --seeds 3
```

All thirteen shared schedules PASS on each seed (39/39); all twelve mutations
FAIL their predeclared clause on each seed (36/36, 12/12 kills across three seeds).
The complete fixture suite and go vet pass. No prediction missed and no amendment
was needed. Detailed per-seed receipts, input/trace hashes and the P10 selector
binding evidence are in [RESULTS-v2.1.md](RESULTS-v2.1.md). The false-suspicion
run remains observed, not a paired correctness proof. No mutation was re-placed;
P10's existing C1.4 mutation now leaves c2's request unanswered after the first
non-grantor crash. The same qualified three-second horizon checks it.

## New v2.1 interpretations and clarified rules

43. Interpretation 30 is now normative v2.1 T1: the predecessor's synchronous
    Request, WriteAttempt and Fault count after successor arming. The existing
    cursor behavior is unchanged and the exact action boundary carries an
    explicit v2.1 T1 derivation comment; the synchronous/fresh-event regressions
    remain passing. Checkers introduce no wall-clock ordering.
    <!-- derives: C1.1, C1.3, F1.1, T1, E1 -->
44. `non-grantor` excludes the issuer of the most recent observable Grant; it
    does not probe the current Raft leader. Among up lease nodes it selects the
    lowest trailing decimal identifier number, with lexical tie-breaking for
    equal numbers. Missing/overflowing numeric suffixes reject rather than
    silently inventing an order. All shared nodes are n1, n2 and n3. Selection
    is frozen at trigger firing, before the existing T2 delay.
    <!-- derives: C1.1, C1.4, F1.1, A1, A2, T2 -->
45. Only a successfully applied `crash: non-grantor` updates the remembered
    target. Resolving a selector, partition membership, or crashing a literal
    node does not. `restart: non-grantor` uses that remembered ID regardless of
    subsequent candidate or grantor changes; it never chooses another up node.
    No remembered crash rejects; restarting an already running remembered node
    rejects under A2. Restart does not clear the record; the next selector crash
    replaces it. This is injector state, not protocol authority or durable data.
    <!-- derives: C1.4, F1.1, A1, A2 -->
46. The new selector is reserved and role-checked as a lease node in every
    supported action target and partition position. Client-only operations
    reject it. Before any possible/actual Grant, or with no up eligible node,
    resolution rejects. Partition use selects normally and does not change
    remembered crash state. Static and incremental A2 validation are retained.
    <!-- derives: C1.4, F1.1, F1.2, F1.3, A1, A2 -->
47. The rewritten shared P10 supersedes interpretation 41: it first observes a
    Grant, crashes a selected up non-grantor, obtains another grant, restores the
    selected node, then crashes the observable grantor and requests again. The
    runner executes those shared actions without substituting a literal n1 or
    hidden leadership test. Baseline evidence contains three grants and matching
    selector crash/restart on each seed; the mutation still fails C1.4.
    <!-- derives: C1.4, F1.1, T1, A1, A2, E1 -->
48. The previous round's signing workaround is historical: this round commits
    normally with signing enabled, and lets each OTS hook add its stamp commit.
    Runner IDs and the committed-prediction gate now identify v2.1; old evidence
    remains unchanged. Wall time begins 2026-10-21 00:51:37 UTC and is reported
    through the final commit and hook; it is workflow metadata only.
    <!-- derives: C1.1, C1.4, T1, A1, E1, E2 -->

<!-- derives: C1.1, C1.2, C1.3, C1.4, T1, A1, E1, E2 -->
Current v2.1 blocked items: none. Bounded sampling and the trusted finite liveness
certificate remain the limitations recorded in previous rounds.

## X1 contract v2 — fenced reads

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, E2 -->
This additive section records the X1 adapt round on x1-adapt-impl. Predictions
for all nineteen schedules and eighteen mutations, separately for seeds 1–3,
were signed and committed as `fc87c3b`, then OTS-stamped by `9d153c5`, before
any X1 build or outcome-bearing execution. Implementation checkpoint `7bc3488`
was signed and stamped by `922d690`. No v1 clause, prior prediction, or historical
evidence was retired or rewritten. Repository reading stayed within the brief's
allowed inputs and own artifacts; no model, experiment or other docs were read.

The read workload/compiler, storage/client paths, observable records, provenance
and independent C2.1/C2.2 log checkers now derive explicitly from C2.x. The six
new enforcing-path mutations preserve P1–P12's placements. To run from the root:

```sh
# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, E2
impl/run.sh --all --seeds 3
impl/run.sh --mutations --seeds 3
# One shared schedule, optionally its paired mutation:
impl/run.sh P18 --seeds 3
impl/run.sh P18 --mutation P18 --seeds 3
```

Both required matrix commands exited 0. All 57 schedule runs PASS; all 54 mutation
runs FAIL their declared clause, giving 18/18 kills on all three seeds. The full
Go fixture suite and vet pass. Test-first red receipts record the initial missing
read language/path/value handling, followed by green fixtures; those red runs
were before adaptation and are not post-adaptation schedule prediction misses.
No schedule/mutation prediction missed or needed amendment. All 111 runs' raw
JSONL and sidecars, 48 baseline read-decision provenance rows, three P18 late
snapshot witnesses, input hashes and per-seed table are linked from
[RESULTS-x1.md](RESULTS-x1.md). No model/implementation divergence is attributed.

## New X1 interpretations

49. A read presents an actually held current or numerically superseded token;
    serving compares it to the highest token of an accepted write, not the
    highest granted token or wall-clock expiry. Equality is allowed. Serving
    never advances that ledger, even when the read token is larger.
    <!-- derives: C2.1, C1.2, F1.1, F1.2, F1.3, T3 -->
50. Storage's single key starts with the empty string. Both its accepted-write
    ledger and stored value survive storage restart. Serving atomically captures
    the current value into a reply; subsequent writes cannot change that reply.
    Reads and rejections never modify the stored value.
    <!-- derives: C2.1, C2.2, C1.2, F1.1 -->
51. An empty served value is explicitly serialized as `value: ""` on ReadAccept
    and served ReadAck. ReadReject and rejected ReadAck omit value. Decoding
    retains field presence separately from its string contents. Read attempts
    and decisions carry the originating grantor term and exact causal authority
    references; read acks name the decision.
    <!-- derives: C2.1, C2.2, F1.1, F1.2, F1.3 -->
52. The v3 read action is part of the closed workload language: current/stale
    selection, client-only roles, A1 freezing, T3 availability/token waits and
    E1 draining match writes. A read action cannot supply a write value or fault
    cell. Its synchronous ReadAttempt can trigger its successor under T1. All
    v2.1 alias and remembered non-grantor semantics remain in force.
    <!-- derives: C2.1, C2.2, F1.1, F1.3, T1, T2, T3, A1, A2, E1 -->
53. Read traffic uses the existing sampled network: within-side reordering,
    one-third duplicate sends, permanent loss for sends across a cut, delivery
    connectivity checks, and paused-client reply queues. Client crash clears
    grants and changes incarnation, so old replies cannot reach its restart.
    Wire messages already handed to the external simulated network may arrive
    after storage restart if they were not dropped while storage was down; this
    does not retain a storage process inbox or introduce a new fault cell.
    <!-- derives: C2.1, C2.2, F1.1, F1.2, F1.3 -->
54. C2.1 is checked using storage's local sequence and only accepted writes to
    reconstruct its durable maximum. Both read decision types must report that
    ledger, while a served read must have token >= maximum. Reads never update
    the reconstructed maximum. C2.1 states a necessary condition for service;
    rejecting a non-stale read alone is not scored as a C2.1 violation.
    <!-- derives: C2.1, C1.2, F1.1, F1.2, F1.3 -->
55. C2.2's independent checker reconstructs the stored value from the exact
    WriteAttempt that each storage WriteAccept names, in storage sequence order.
    It compares every ReadAccept to that reconstructed value. It reads no live
    ledger, client state or engine value; JSONL line order and wall clocks do not
    determine causal ordering. Storage sequence continuity spans restart.
    <!-- derives: C2.2, C1.2, F1.1, F1.2, F1.3 -->
56. Every served ack must identify a served read of that same client, key and
    token, with the exact served value. A precisely correlated attempt never
    served is C2.2 FAIL; an existing serve whose reference was omitted is
    UNEXPLAINED missing evidence. Missing value fields or missing provenance alone
    are also UNEXPLAINED. A witnessed wrong snapshot/value remains C2.2 FAIL even
    if another part of the trace lacks provenance or the end is unreachable.
    <!-- derives: C2.2, F1.1, F1.2, F1.3, E2 -->
57. P13/P14/P15 mutations bypass only the read comparison after crash, partition
    or resume, respectively. They preserve the write ledger and its reported
    highest_before, exposing stale service directly to C2.1. P1–P12 remain at
    their previous enforcing paths; no re-placement was necessary this round.
    <!-- derives: C2.1, C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
58. P16 skips serving a read after a crash and fabricates its served ack. P17
    fabricates a served ack for a read sent across the partition and never served.
    Both preserve attempt correlation so the checker can discriminate unserved
    reads from missing references. P16 can leave its ReadAccept trigger
    unreachable; E2 still scores the earlier witnessed C2.2 violation.
    <!-- derives: C2.2, F1.1, F1.2, E2 -->
59. P18 deliberately reloads current storage value at delivery after resume,
    instead of delivering the captured snapshot. The baseline's served v1 and
    later v2 write are causally before the late ack on every seed; baseline
    carries v1 and mutation carries v2, demonstrating the value part of C2.2.
    <!-- derives: C2.2, F1.3 -->
60. Read clauses add safety checks only; C1.4 and its qualified three-second
    progress certificate are unchanged. The five-second operational bound is
    not a read liveness promise. Seeds 1–3 sample T2 delay (0–2 ms), message delay
    (1–5 ms), ordering and duplicates; Raft's election timing remains unseeded.
    Runner IDs use x1-v3 and the committed-prediction gate requires this round's
    preregistration. Only declared-clause failures kill mutations. Commits remain
    signed, with OTS hooks allowed to finish. Round wall time starts at
    2026-10-21 01:06:33 UTC and is reported through the final commit and stamp;
    it is workflow metadata only. Finite sampling is not exhaustive proof.
    <!-- derives: C2.1, C2.2, C1.4, F1.1, F1.2, F1.3, T2, E1, E2 -->

## Blocked

<!-- derives: C2.1, C2.2, C1.4, F1.1, F1.2, F1.3, E1, E2 -->
Current X1 blocked items: none. Prior rounds and their historical limitations
remain above; finite sampling and the trusted C1.4 certificate still apply.

## Schedule format v2.2 and observe schema v3

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, A1, A2, E1, E2 -->
This additive section records the v22-impl round. Predictions were signed and
committed first as `b3cbaf6`, then OTS-stamped by `5adaff8`. Implementation
checkpoint `a912afc` is signed and stamped by `160a069`. No prediction was revised.
There is no contract, failure-model or schedule change, and no mutation was
re-placed. The normative remembered-restart rule now carries v2.2 A1 comments;
every write/read ack carries explicit schema-v3 answers from its original attempt.
Independent provenance checking validates those references as well as causes.

Both required commands exit 0:

```sh
# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, A1, A2, E1, E2
impl/run.sh --all --seeds 3
impl/run.sh --mutations --seeds 3
```

Every shared schedule passes seeds 1–3 (57/57); every mutation fails its declared
clause on seeds 1–3 (54/54, 18/18 kills). No verdict changed from the predeclared
X1 results and no prediction amendment was needed. All 34 top-level Go tests and
vet pass. Test-first red receipts show the missing fields and same-token retry
ambiguity before adaptation, followed by passing regressions. Raw traces,
sidecars, ack-reference audits, hashes and the complete per-seed results are in
[RESULTS-v2.2.md](RESULTS-v2.2.md). Only own artifacts and brief-permitted inputs
were read; other docs, model, experiments and git log were not read.

## New v2.2 / schema-v3 interpretations

61. Interpretation 45 is now normative v2.2 A1: restart non-grantor binds to the
    most recent successfully applied crash non-grantor, even if that node is now
    the grantor. Missing prior selector crash rejects. Runtime binding, successful
    crash recording, static rejection and regression carry explicit v2.2 tags;
    their behavior is unchanged. A2 still rejects restart of a running process.
    <!-- derives: C1.4, F1.1, A1, A2 -->
62. Every WriteAck and ReadAck, including rejection, late/duplicate receipt and
    deliberate mutation reply, names the original wire attempt in answers.
    It does not name a storage decision, Grant, most recent attempt or retry.
    Storage-decision causes remain intact. Non-ack emissions omit answers.
    <!-- derives: C1.3, C2.2, F1.1, F1.2, F1.3 -->
63. Schema-v3 answers is redundant evidence, not a new causal edge or contract
    clause. The checker requires an existing operation-appropriate attempt with
    matching client/process, key and token, and causal reachability through the
    recorded history. It never inserts an answers edge to make a bad reference
    appear causal. Missing or mismatched evidence is UNEXPLAINED unless a separate
    contract violation has already been witnessed under E2.
    <!-- derives: C1.3, C2.2, F1.1, F1.2, F1.3, E2 -->
64. Where an ack directly names a storage decision, answers must equal that
    decision's exact attempt reference. Merely reaching an earlier same-token
    attempt through local sequence or prior decisions is insufficient. Fabricated
    mutation replies instead name their direct original attempt, allowing C1.3
    and C2.2 to retain the discriminated unaccepted/unserved failure evidence.
    <!-- derives: C1.3, C2.2, F1.1, F1.2, F1.3, E2 -->
65. Current fixtures explicitly name their attempts; malformed raw-record tests
    bypass no validation and are not repaired automatically. Historical traces
    retain their original schema and are not rewritten. The current strict v3
    provenance checker reports missing answers if asked to check older traces.
    New runs of every old schedule retain their prior contract verdicts.
    <!-- derives: C1.3, C2.2, F1.1, F1.2, F1.3 -->
66. Runner IDs identify v22-observe-v3, and the execution gate requires this
    round's committed registration. Sampling and all prior operational/liveness
    bounds stay unchanged: seeds 1–3, T2 0–2 ms, jitter 1–5 ms, reordering and
    one-third duplicate sends, with unseeded Raft election timing. Normal signed
    commits run the OTS hook. Wall time starts 2026-10-21 03:57:24 UTC and includes
    the final commit/hook; it supplies no event ordering. The pre-existing
    untracked .venv remains untouched and uncommitted.
    <!-- derives: C1.4, C1.3, C2.2, F1.1, F1.2, F1.3, T2, E1, E2 -->

## Blocked

<!-- derives: C1.4, C1.3, C2.2, F1.1, F1.2, F1.3, E1, E2 -->
Current v2.2/schema-v3 blocked items: none. Finite sampling and the trusted C1.4
horizon certificate retain their previously documented limits.

## X2 adaptation checkpoint (before shared schedule execution)

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2, L1, L2, L3, E1, E2, E3, T3 -->
Predictions and scoring for all 31 shared schedules and 30 mutations were signed
and committed as `6c58815`, OTS stamp `e39c88c`, before adaptation or tests.
The initial red fixture receipt records absent link-language/API support. The
six focused X2 tests and full Go fixture suite pass at this checkpoint; no shared
schedule or mutation has yet run. The existing transport fixture expecting a
cut/heal history to invalidate a later reply send was replaced to assert v2's
opposite rule. The read storage fixture now pumps the distinct send and delivery
stages. These are semantic fixture adaptations, not changes to predictions.

### Interpretations established from the inputs

67. **Contradicted:** interpretations 11, 21, 25 and 53 discard queued messages
    on a new cut or recheck connectivity at delivery. Failure-model v2 fixes link
    fate at send. Requests admitted before a cut can reach storage afterwards;
    sent replies survive later cuts. Messages sent on down links are permanently
    lost. F1.1 process availability and client incarnation still govern receipt.
    The prior text and receipts above are retained as history.
    <!-- derives: C1.3, C2.2, F1.1, F1.2, F2.1, F2.2 -->
68. **New:** storage prepares each reply locally for 8 ms before its actual send;
    send then samples 1–5 ms network delivery. This makes the decision-to-send
    interval explicit. A decision-triggered fault can precede send, explaining
    the lost-ack schedules without retroactively losing an already sent packet.
    Raft's reply relay independently admits the reverse direction at its send,
    with no cut-history or receive-time link recheck. Raft retains its existing
    protocol and process-incarnation checks.
    <!-- derives: C1.1, C1.3, C1.4, C2.2, F1.1, F2.1, F2.2 -->
69. **Extended:** interpretations 19 and 53's partition environment is an
    accumulated directed matrix. F1.2 adds all cross-side links to the same
    matrix; F2.1 adds both directions per pair; F2.2 adds just the named direction.
    Every heal clears the whole matrix. L1 selectors freeze when the trigger
    fires, self-pairs are removed and duplicates are harmless. Fault links record
    resolved directed pairs, including already-down links named by that action;
    a heal explicitly serializes links: []. The old cell IDs remain live.
    <!-- derives: F1.2, F2.1, F2.2, L1, L2, A1, T2 -->
70. **Extended:** interpretations 16 and 38 require literal direct connectivity:
    requester, storage and some two up lease nodes form a bidirectional clique.
    Counting two lease nodes reachable from the requester/storage is insufficient
    unless those lease nodes also connect to each other. The observable grantor
    need not belong to that clique. The engine and offline checker reconstruct
    this premise independently. The trusted three-second duration certificate
    remains a limitation; bounded samples do not prove eventuality.
    <!-- derives: C1.4, F1.1, F2.1, F2.2, L3 -->
71. **Extended:** interpretation 52 includes read requests and replies in
    quiescence. T3 allows another read/write despite a lost previous reply; only
    a prior request waits for its answer. Link-lost grant completions leave the
    existing RequestState outstanding: a failed send emits no delivered Grant,
    and the next attempt uses a fresh committed allocation. Allocation gaps are
    allowed; no duplicate Grant record is used for retransmission. A reached
    event bound has priority over readiness and cannot silently become PASS.
    <!-- derives: C1.1, C1.4, C2.2, F2.1, F2.2, T3, E1, E3 -->
72. **New:** P19–P30 have the preregistered enforcing-path mutations. P24 skips
    a later write's acceptance (leaving the first WriteAccept trigger intact)
    and invents success despite the down reverse link. P29/P30 bypass reply loss
    with a value different from the actual served snapshot, exposing C2.2's value
    condition. P25/P26 suppress the same grant-service mechanism used normally;
    a baseline failure means there is no working half to mutate and will be
    reported as such. No formal model or model mutation has been read or authored.
    <!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F2.1, F2.2, E2 -->

### Access and timing record

<!-- derives: C1.1, C1.4, F2.1, F2.2 -->
The first recorded clock is 2026-10-21 05:51:48 UTC; final wall time will be
reported through the adapted commit and hook. Before reading the complete brief,
the agent attempted the absent steward seed files, read an external generic
using-superpowers workflow SKILL.md, and later displayed six git-log titles.
These are access-list deviations, recorded explicitly rather than asserting
perfect scope compliance. No formal-model artifact or other author's code was
read. After the brief, source/input reads and all task outputs stay in its listed
paths (plus git commit/status metadata). The untracked .venv is untouched.

### X2 source-review correction before final matrices

<!-- derives: C1.3, C1.4, C2.2, F1.1, F2.1, F2.2, L3 -->
The initial 31×3 baseline matrix at 94549e3 passed all 93 runs; its receipt and
traces are retained. Additive registration `3b73f2c` (stamp `2e62373`) records a
source-review issue in the new local-send stage: storage restart retained local
unsent reply work. The preregistered regression failed as expected, then passed
after crash discards only pendingSend entries. External packets already sent
remain eligible for delivery after the sender restarts. This correction enforces
F1.1's volatile-state rule, and was not prompted by a failed shared schedule.
The full fixture suite passes again. Additional fixtures independently exercise
runtime clique eligibility and verify that a failed reverse grant send leaves
the requester outstanding until a later allocation's reply succeeds. No baseline
or mutation prediction, placement, horizon, schedule or scoring rule changed.

## X2 adapted version — final recorded results

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2, L1, L2, L3, E1, E2, E3, T3 -->
This section supersedes earlier current-round headlines additively. The final
implementation checkpoint is `8321ab5` (OTS stamp `acae806`). Both required
commands exit 0: all 31 shared schedules PASS seeds 1, 2 and 3 (93/93); all 30
mutations FAIL their predeclared clause on each seed (90/90, 30/30 kills across
three seeds). All 42 top-level Go fixture tests and vet pass. No shared baseline
failed, no verdict prediction missed, and no mutation was re-placed. The initial
93-pass matrix, preregistered source-review correction, all raw traces/sidecars,
per-seed verdicts and interpretations are in [RESULTS-x2.md](RESULTS-x2.md).

The independent raw-record audit validates 646 ack references, 108 F2.x fault
records and 38 unchanged input hashes across 276 retained runs (552 evidence
files). An initial audit null-list handling error was corrected; its receipt is
retained and no outcome or score changed. P23/P24 have no old-holder write acks;
P29/P30 have no old-holder read values and do have correct post-heal c2 values.
P25 and P26 both have working halves to mutate, and both mutations fail C1.4.

73. **New, outcome-informed timing limitation:** P17's first served read reply
    is received after healing on all three final seeds. The short cut ends before
    the reply's send; the second read sent on the down link is lost. This is
    consistent with v2 send-time fate and C2.2. The schedule's comment about its
    first ack being lost is not forced by its actions. Its mutation still fails
    C2.2 through the distinct unserved second attempt. No schedule, timing,
    prediction or scorer was changed to conceal this coverage limitation.
    <!-- derives: C2.2, F1.2, F2.1, F2.2, L2, T2, T3 -->
74. **New, bounded observation:** P25 retains n1, term 2, granting token 4 to c2
    after c1's token 3, on every final seed. P26 transfers from n1, term 2, token 3
    to n3, term 3, token 6, while the one-way drop remains. These short traces
    witness progress under the new cells; they do not establish resilience to
    every long-running election pattern. Mutation suppression independently
    demonstrates sensitivity of the finite C1.4 checker, not unbounded liveness.
    <!-- derives: C1.1, C1.4, F2.1, F2.2, L3 -->

<!-- derives: C1.4, C1.3, C2.2, F2.1, F2.2 -->
Current X2 blockers: none. No formal-model comparison or divergence attribution
has been made. The access deviations, finite sampling, unseeded Raft randomness
and trusted duration-certificate limitations remain explicitly recorded above.
First clock: 2026-10-21 05:51:48 UTC; final response reports elapsed time through
the adapted-version commit and OTS hook. Nothing is pushed; .venv is untouched.

## FixR routing repair — design and interpretations

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2, L3, E1, E2, E3, T3 -->
This new round follows the supplied third-family judgement: X2's H8/H9 C1.4
failures were genuine missing-routing violations. That attribution is supplied
by the brief; no model artifact or steward judgement document was consulted.
The routing predictions were signed first as `063c9a0`, OTS stamp `64b8b02`.
They cover all 35 shared schedules, all existing P1–P30 mutations, and R1/R2
routing mutations. The first clock is 2026-10-21 14:59:31 UTC. No test ran before
registration. No external skill file or previous clone was accessed this round;
the absent steward seed files are exempt under the inherited author brief.
Historical X2 results and interpretations remain above and are superseded only
where named below. All shared inputs remain unchanged; nothing is pushed.

75. **Contradicted:** interpretations 2 and 71 equate observable Grant with a
    delivered reply. A committed successful allocation now records its Grant
    before delivery, even when the reply is lost. The same Request remains
    outstanding until actual receipt. A later fresh allocation records a new,
    higher-token Grant; forwarding/duplicating an existing reply records none.
    This corrects the C1.4/L3 reading named by the brief, and makes H8's issuer
    crash trigger observable without pretending that its recipient held a token.
    <!-- derives: C1.1, C1.4, F1.1, F2.1, F2.2, L3 -->
76. **New:** clients retry their standing Request every 20 ms to all lease nodes.
    Received requests forward along simple lease-node paths. Each outgoing hop
    consults its directed link only at send; no global reachability oracle or
    schedule-name branch selects a route. Only a Raft leader with an actually
    received request can apply allocation. Replies preserve the original issuer,
    token, term and Grant reference while forwarding through lease nodes. Local
    lease reply preparation lasts 8 ms, is volatile on issuer crash, and precedes
    network sends. Sent packets survive later cuts; endpoint incarnation checks
    still prevent inheriting a crashed process's inbox.
    <!-- derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, L3 -->
77. **Extended:** interpretation 70's liveness premise remains a direct
    bidirectional clique. Forwarding is a service mechanism, not a transitive
    reinterpretation of connected. A stable leader's quorum intersects the
    eligible follower majority and supplies a relay path. Round-robin allocation
    between standing requests prevents an unreachable client monopolizing the
    serialized allocator. A holder pause triggered by issuance waits until the
    named client has actually received its grant.
    <!-- derives: C1.4, F1.1, F1.3, F2.1, F2.2, L3, T3 -->
78. **Extended observability limitation:** grant_deliveries in the existing
    sidecar names each Request, the Grant actually received, client incarnation,
    request/reply hop paths and receipt's latest Fault reference. JSONL schema is
    unchanged. The offline checker independently validates identity, directed
    send-link admission, hop continuity, endpoint generations and receipt state
    from Fault records. Actual receipt, like the three-second duration horizon,
    remains trusted instrumentation. An observed client attempt can also prove
    possession. Issued-but-undelivered Grants cannot discharge a certified C1.4
    horizon. This is stronger evidence, not a claim of independently provable
    receipt from the clock-free shared schema alone.
    <!-- derives: C1.1, C1.4, F1.1, F1.3, F2.1, F2.2, L3 -->
79. **New anti-theater checks:** R1 disables follower request forwarding, and R2
    disables lease-node reply forwarding. Both run unchanged shared H9 and are
    predicted to fail C1.4. R2 can issue Grants while its client still obtains
    none, exposing the issuance/receipt distinction to the independent checker.
    P1–P30 retain their enforcing-path mutations. The Raft integration and
    selector/runner tags now explicitly include F2.x where previously missing.
    No retired clause or cell is used; no other-side tag was inspected or edited.
    <!-- derives: C1.1, C1.4, F1.1, F2.1, F2.2, L3 -->

### FixR fixture receipts before shared runs

<!-- derives: C1.1, C1.4, F1.1, F2.1, F2.2, L3 -->
The initial red run reproduced omitted undelivered issuance, the checker treating
issuance as receipt, and C1.4 failure on renamed copies of H8/H9. After repair,
these tests pass. Additional tests cover independently directed request/reply
paths, invalid delivery-route certificates and fairness for two standing clients.
The first full fixture run exposed two historical assumptions: X2's lost-grant
fixture expected no issuance event and synchronous completion; P10 expected
exactly three Grant records. Those assertions are replaced by distinct issuance
and receipt checks and exactly three completed Request identities, allowing a
fresh issuance after a lost reply. The original failing receipt is retained.
The full suite now passes. No shared schedule or mutation has run at this
checkpoint, and no prediction, scoring rule, duration or shared input was changed.

### Declared FixR limitations (before shared results)

<!-- derives: C1.1, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, L3, E1, E3 -->
No additional stable-leader routing shape satisfying C1.4's three-voter premise
is known to be intentionally left broken. The repair retains the existing pinned
Raft algorithm. It does not prove that every asymmetric/non-transitive topology
and every permitted message/election interleaving eventually stabilizes a leader.
A schedule causing sustained election churn and no commits for the finite
three-second qualified window can therefore still fail C1.4 despite a connected
majority; this round adds no consensus-election repair or unbounded proof. No
new concrete counterexample to that limitation is claimed before runs.

Relays use lease nodes, not storage or other clients. A stable leader/quorum plus
the premise's eligible majority gives a lease-node route in this fixed three-
voter system; this is not a general arbitrary-membership routing proof. Logical
process replacement, seeded bounded workload sampling, unseeded Raft timing,
trusted duration/receipt certificates, five-second operational waits and event
bounds remain. Unreachable-trigger or over-bound schedules without a witnessed
clause violation remain UNEXPLAINED. These limits are retained to keep this fix
within routing and the established independently checked Raft allocation path.

### FixR source-review renewal correction

<!-- derives: C1.1, C1.4, F1.3, F2.1, F2.2, T3 -->
The first complete shared matrix at 786a384 passed all 105 runs; all 96 mutations
failed their predicted clauses. Source review then found the expired-old-grant
pause-readiness interaction. Additive registration `abd85e2` (stamp `4de31ef`)
preceded a regression that failed with "pause requires an unexpired holder".
Readiness now waits for an unexpired held grant, while the F1.3 action's validation
remains unchanged. The renewal fixture and full suite pass. This corrects the
new interpretation 77's receipt-before-pause behavior; it was not prompted by a
shared schedule failure. Both first matrices, their traces and the passing first
audit are retained; everything is rerun after this correction. No prediction,
mutation placement, liveness horizon, scoring rule or shared schedule changed.

### FixR declared observed limitation: P18's finite pause window

<!-- derives: C2.2, C1.4, F1.3, F2.1, F2.2, T2, T3, E1 -->
The final rerun at e77dc22 has one prediction miss: P18 seed 2 is UNEXPLAINED
workload unavailable under T3. After the grant's relayed delivery, the write and
read round trips consumed the issuance-relative 40 ms lifetime before the pause
action. The trace has ReadAccept and ReadAck, no pause Fault, and no c2 Request.
The pause-readiness guard waits for an unexpired held grant that this schedule
never renews. No clause violation or eligible unanswered-request horizon was
witnessed. This is retained as an incomplete run; it is not upgraded to PASS.
No lifetime, pause validity rule, schedule, scoring or prediction is changed.

This declares a concrete remaining shape: a pause scheduled after enough message
round trips can miss the finite unexpired-holder window and yield UNEXPLAINED.
The routing relay's extra hops can expose this window. The implementation keeps
its existing lifetime origin/duration and F1.3 validity rule; the brief allows
recording an adverse result, and the evidence does not justify weakening F1.3
or claiming a read safety failure. The complete raw trace and sidecar are retained.
The first all-PASS matrix and final prediction miss will both appear in results.

## FixR final results and limitations

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2, L3, T3, E1, E2, E3 -->
The routing repair is verified on H8 and H9 on all three seeds. H7 and H10 also
pass all seeds. The final source checkpoint is e77dc22, stamped by 5b3a98f.
[RESULTS-fixr.md](RESULTS-fixr.md) records every shared schedule and mutation by
seed, all interpretations, declared limits, amendments and evidence links.

Final --all exits 1: 104 PASS and one UNEXPLAINED (P18 seed 2). Final --mutations
exits 1: 95 expected clause failures and one UNEXPLAINED (P18 seed 2); the latter
is not a kill, giving 31/32 killed across all three seeds. Per seed, baseline
passes are 35/35, 34/35, 35/35; expected mutation failures are 32/32, 31/32, 32/32.
The pause-window result and its reason remain recorded above. All 48 top-level
Go fixture tests and vet pass. The first matrices at 786a384 had 105 passes and
96 expected failures; their evidence is retained without replacing final results.

Both R1 and R2 fail C1.4 on every final seed. R2 issues 71 grants to c2 per seed
but delivers none, demonstrating the checker's sensitivity to lost receipt even
when issuance is observable. In final H8, c2's issued token 4 is lost, its issuer
crashes, and the same Request receives token 6 from a surviving grantor. Final
H9 uses three request hops and two reply hops for c2 while keeping the original
leader. H7 preserves the old write fence across a higher-token read; H10 grants
and accepts c2's higher-token write despite its deaf follower.

The raw-record audit passes validation across 402 retained runs (804 hashed
JSONL/sidecar files), checking 832 grant receipts, 965 ack references, all four
newly shared schedule witnesses and 42 unchanged input hashes. It explicitly
records two prediction misses; audit success does not turn them into PASS.
Task files remain under impl/, no tmp/ or cache is committed, .venv is untouched,
and nothing is pushed. No model artifact or external file was read this round.

Declared limitations are part of this result: a P18-like post-grant workload can
consume the finite unexpired-holder window before a pause, leaving an incomplete
run and an unexercised mutation. Pinned Raft election behavior, bounded sampling,
logical crashes and trusted duration/receipt certificates remain. A sustained
no-commit election pattern could still exhaust C1.4's finite horizon; no such new
counterexample was seen here and no further stable-leader routing shape is known
to be intentionally unfixed. No lifetime, validity rule, input or score was tuned
after the adverse result. Wall time begins 2026-10-21 14:59:31 UTC and is reported
through the adapted commit and hook in the final answer.

## Timing repair — scheduler design and interpretations

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2, T1, T2, T3, L1, L2, L3, E1, E2, E3 -->
The supplied brief reports 2,010 steward runs and seven unstable cells. Those
reported outcomes inform the repair; none of the steward's files or other-side
artifacts was read. Registration `b7867c5`, OTS stamp `674db60`, preceded all
adaptation and timing-round tests. First clock: 2026-10-22 05:45:33 UTC. The
absent seed documents are exempt under the inherited author brief. All source,
cache, dependency inspection and output remain under the permitted directory;
no external skill, model, experiment or steward file was accessed this round.
Prior results, adverse traces and interpretations remain unchanged history.

80. **New scheduler:** one event loop owns integer logical time. A nominal
    millisecond is one simulated unit; synchronous work and IO consume no units.
    Seeded sampling chooses packet latency (1–3 units), T2 delay (0–2), delivery
    order and campaign deadlines. Stable node/message ordering precedes sampling.
    Grant lifetime 40, local reply preparation 8, request retry 20, qualified
    progress window 3,000 and operational wait 5,000 remain the existing nominal
    values. The delivery range is the preregistered bounded simulation choice,
    replacing 1–5 real milliseconds and host overhead. No schedule name chooses
    protocol behavior. Logical time is recorded only in a sidecar, never used
    to order independent-process JSONL events in the checker.
    <!-- derives: C1.1, C1.4, C2.2, F1.3, F2.1, F2.2, T2, T3, E1 -->
81. **Contradicted execution assumptions:** interpretations 5/21/60/66's real
    elapsed execution and unseeded Raft election sampling no longer apply.
    HashiCorp's autonomous timer/goroutine engine is replaced by pinned etcd
    Raft v3.6.0 RawNode, driven synchronously through Ready/Step/Advance. The
    scheduler persists entries/hard state before sends, and only actually
    committed entries supply index/term tokens. All three nodes have the fixed
    voter configuration in retained storage before workload start. Process
    crashes retain that storage/applied state and discard volatile nodes/inboxes.
    No central quorum allocator or new consensus algorithm was introduced.
    The Go toolchain is pinned to 1.23.12.
    <!-- derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2 -->
82. **Explicit election clock:** leaders receive a protocol tick every 10
    logical units. Other roles receive TickQuiesced to advance only lease age;
    only scheduler-seeded Campaign deadlines can start their elections. A
    delivered current-leader heartbeat/append resets that deadline. Source
    inspection of the pinned library confirms its internally computed random
    follower timeout is consulted by tickElection, which this driver never calls
    for a follower/candidate. That unused internal random value cannot select
    an event. Outbound Ready messages are sorted by serialized bytes before
    seeded delivery, removing map iteration from protocol input order. The
    canonical replay tests exercise independent library instances and host
    thread counts. Quiesced ticking is a pinned-library integration choice;
    a future library upgrade needs a new source audit and replay registration.
    <!-- derives: C1.1, C1.4, F1.1, F2.1, F2.2 -->
83. **Extended F1.3 semantics:** expiry and pause duration now belong to the
    scheduler. Pausing freezes client execution/receipt while logical grant
    time advances; resume is still strictly later than the lifetime, witnessed
    by the existing later-grant workload barrier. The existing unexpired-holder
    action check and renewal-readiness condition use that clock. No validity
    check is weakened, no duration/origin is changed, no hidden renewal is added.
    The host-overhead part of the P18 pause-window limitation is superseded;
    longer logical workflows may still deterministically miss a holder window.
    <!-- derives: C1.4, C2.2, F1.3, T3, E1 -->
84. **Extended F2.x scheduling:** each directed send fixes fate at its logical
    event. A later cut cannot retract a sent packet; healing cannot resurrect
    a down-link send. An already-sent packet may survive its sender crashing,
    while a receiver's replaced inbox cannot inherit old deliveries. Equal-time
    processing is now explicit and reproducible. The direct bidirectional L3
    premise remains unchanged, as does lease-node routing around a stable leader.
    <!-- derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, L1, L2, L3 -->
85. **Mutation placement and replay evidence:** P1–P30 and R1/R2 retain their
    actual enforcing-path placements, including P29/P30's wrong-value break on
    a lost read-reply path. Registration allowed a deterministic re-placement if
    needed; the focused logical-time executions kill both existing mutations,
    so that contingency was not used. Canonical replay includes all event
    fields except the unique run label, plus the entire sidecar/verdict. Labels
    use collision-free sequential output suffixes rather than OS randomness and
    never enter scheduler state. Changing a schedule's display name or host
    thread count cannot alter canonical execution for the same schedule/seed.
    <!-- derives: C1.1, C1.4, C2.2, F1.3, F2.1, F2.2 -->

### Timing verification before the full repetition matrix

<!-- derives: C1.1, C1.4, C2.2, F1.1, F1.3, F2.1, F2.2, T2, T3, E1 -->
The red source audit identified the old real clocks, timers, goroutines, select
races and OS-random labels. The adapted source passes that audit, all existing
fixtures and the added timing fixtures. P18/P29/P30 baseline/mutation executions
on seeds 1–3 match canonical traces/sidecars after schedule renaming, host thread
count changes and host delays. The whole fixture suite and vet pass. No shared
matrix was executed before this checkpoint; no prediction/scoring amendment
has been needed. Protocol-specific fixtures now inspect retained voter storage
and explicit message admission instead of HashiCorp's asynchronous interfaces.
The fixed three-voter authority and all old clause/cell derivations remain live.

### Declared timing limitations

<!-- derives: C1.1, C1.4, C2.2, F1.1, F1.3, F2.1, F2.2, E1, E3 -->
For a fixed executable, valid schedule and seed, no schedule shape is knowingly
left nondeterministic. This is a deterministic bounded simulation, not OS/process
or network-timing verification, and 1–3-unit delivery samples do not explore all
permitted delay patterns. Unsupported/corrupt input rejects deterministically.
Long workloads or disrupted elections may deterministically exceed a lifetime,
trigger, event or finite progress bound; repeat-varying outcomes are not excused
by those limits. Arbitrary permanent topology changes are not an unbounded Raft
liveness proof. Logical receipt and duration remain trusted sidecar instrumentation.
Output-label suffixes and external IO/build failures are outside protocol state;
operational failures remain UNEXPLAINED. Package/executable changes can change
canonical traces and require fresh replay evidence. None of these limits permits
changing a failing shared result into a PASS or counting a missing mutation kill.

## Timing repair — final ten-repetition result

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2, T2, T3, L3, E1, E2, E3 -->
At source checkpoint afb4fc2 (OTS stamp 36ec2be), both required commands were
executed ten times: every command exits 0. All 1,050 baseline runs PASS; all 960
mutation runs FAIL their declared clauses. Each of the 201 cells has ten identical
expected outcomes and ten identical canonical event/sidecar hashes (excluding only
unique run labels). No flaky cell, prediction miss, UNEXPLAINED result or missing
mutation kill remains in this timing-round matrix. All 32 mutations are killed
on all three seeds in all ten repetitions. No mutation placement changed.

Specifically P18, P29 and P30 each have 10 PASS and 10 FAIL C2.2 on every seed.
The original P18 holder pause executes, its late read preserves the served value,
and each mutation exhibits an actual mismatched served snapshot in the raw log.
P29/P30's old-holder replies are lost while the later c2 read succeeds after
healing. H8/H9 routing repair witnesses and R1/R2 sensitivity remain present.
All 51 top-level Go tests and vet pass. Host delay/thread-count/name perturbations
cannot change canonical replay in the added fixtures.

[RESULTS-timing.md](RESULTS-timing.md) gives counts for every cell and declared
limitations. The independent audit covers all 2,010 runs, 4,020 hashed raw files,
4,170 grant receipts, 4,880 ack references and 42 unchanged shared inputs. No
shared input or score changed, no failed run was replaced by another sample,
and no outcome-informed repair amendment was needed after the registered timing
adaptation. All raw traces, sidecars, command receipts and replay hashes are kept.
Historical adverse results above remain unchanged. No formal-model artifact or
steward file was consulted, .venv is untouched, and nothing is pushed.

No valid-schedule shape is knowingly left nondeterministic for this executable
and seed. The result is bounded deterministic simulation, not real OS timing or
exhaustive delay exploration; external IO failures remain operational errors.
Logical crashes, trusted receipt/duration instrumentation and deterministic
lifetime/trigger/event/progress bounds remain limitations. Code/library changes
require fresh replay evidence. First workflow clock: 2026-10-22 05:45:33 UTC;
the final answer reports elapsed time through the adapted commit and OTS hook.

````
# The code diff of the adaptation
````diff
diff --git a/impl/check.go b/impl/check.go
index 80929d3..787d7a2 100644
--- a/impl/check.go
+++ b/impl/check.go
@@ -1,4 +1,4 @@
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 package main
 
 import (
@@ -6,18 +6,20 @@ import (
 	"encoding/json"
 	"fmt"
 	"os"
+	"os/exec"
 	"sort"
+	"strings"
 )
 
 // Verdict distinguishes observed clause failure from missing evidence.
-// derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type Verdict struct {
 	Clause string
 	Reason string
 }
 
 // traceGraph is rebuilt from the JSONL, never from implementation state.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type traceGraph struct {
 	events  map[Ref]Event
 	local   map[string][]Event
@@ -25,7 +27,7 @@ type traceGraph struct {
 }
 
 // readTrace validates local sequence continuity and reconstructs causal order.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func readTrace(path string) (*traceGraph, error) {
 	f, err := os.Open(path)
 	if err != nil {
@@ -51,7 +53,7 @@ func readTrace(path string) (*traceGraph, error) {
 		if v.Run != run {
 			return nil, fmt.Errorf("mixed runs")
 		}
-		r := Ref{v.Proc, v.Seq}
+		r := Ref{v.Proc, v.Seq, v.Inc}
 		if _, ok := g.events[r]; ok {
 			return nil, fmt.Errorf("duplicate event reference %v", r)
 		}
@@ -65,11 +67,22 @@ func readTrace(path string) (*traceGraph, error) {
 		return nil, fmt.Errorf("empty trace")
 	}
 	for proc, events := range g.local {
-		sort.Slice(events, func(i, j int) bool { return events[i].Seq < events[j].Seq })
-		for i, e := range events {
-			if e.Seq != uint64(i+1) {
+		sort.Slice(events, func(i, j int) bool {
+			if events[i].Inc != events[j].Inc {
+				return events[i].Inc < events[j].Inc
+			}
+			return events[i].Seq < events[j].Seq
+		})
+		var lastInc, lastSeq uint64
+		for _, e := range events {
+			if e.Inc != lastInc {
+				lastInc = e.Inc
+				lastSeq = 0
+			}
+			if e.Seq != lastSeq+1 {
 				return nil, fmt.Errorf("missing local sequence on %s", proc)
 			}
+			lastSeq = e.Seq
 		}
 		g.local[proc] = events
 	}
@@ -79,7 +92,7 @@ func readTrace(path string) (*traceGraph, error) {
 	for r, v := range g.events {
 		edges := map[Ref]bool{}
 		if r.Seq > 1 {
-			edges[Ref{r.Proc, r.Seq - 1}] = true
+			edges[Ref{r.Proc, r.Seq - 1, r.Inc}] = true
 		}
 		for _, cause := range v.Causes {
 			edges[cause] = true
@@ -123,7 +136,7 @@ func readTrace(path string) (*traceGraph, error) {
 }
 
 // precedes traverses explicit causes plus implicit per-process program order.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (g *traceGraph) precedes(a, b Ref) bool {
 	if a == b {
 		return false
@@ -143,7 +156,7 @@ func (g *traceGraph) precedes(a, b Ref) bool {
 		}
 		edges := append([]Ref{}, v.Causes...)
 		if r.Seq > 1 {
-			edges = append(edges, Ref{r.Proc, r.Seq - 1})
+			edges = append(edges, Ref{r.Proc, r.Seq - 1, r.Inc})
 		}
 		for _, p := range edges {
 			if p == a {
@@ -156,7 +169,7 @@ func (g *traceGraph) precedes(a, b Ref) bool {
 }
 
 // directEvent finds an explicit causal parent of a particular event type.
-// derives: C1.1, C1.2, C1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (g *traceGraph) directEvent(e Event, names ...string) (Event, bool) {
 	for _, r := range e.Causes {
 		v := g.events[r]
@@ -170,7 +183,7 @@ func (g *traceGraph) directEvent(e Event, names ...string) (Event, bool) {
 }
 
 // checkC11 compares all ordered grants and demands a total observable grant order.
-// derives: C1.1, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (g *traceGraph) checkC11() Verdict {
 	var grants []Event
 	for _, v := range g.ordered {
@@ -185,9 +198,19 @@ func (g *traceGraph) checkC11() Verdict {
 			grants = append(grants, v)
 		}
 	}
+	v5 := false
+	for _, event := range g.ordered {
+		if event.Event == "ConfigCommitted" {
+			v5 = true
+			break
+		}
+	}
+	if v5 {
+		return Verdict{}
+	}
 	for i, a := range grants {
 		for _, b := range grants[i+1:] {
-			ar, br := Ref{a.Proc, a.Seq}, Ref{b.Proc, b.Seq}
+			ar, br := Ref{a.Proc, a.Seq, a.Inc}, Ref{b.Proc, b.Seq, b.Inc}
 			if !g.precedes(ar, br) {
 				return Verdict{Reason: "grants lack total causal order"}
 			}
@@ -200,7 +223,7 @@ func (g *traceGraph) checkC11() Verdict {
 }
 
 // checkProvenance checks the authority path for EVERY acceptance and rejection.
-// derives: C1.1, C1.2, C1.3, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (g *traceGraph) checkProvenance() Verdict {
 	for _, e := range g.ordered {
 		if e.Event != "WriteAccept" && e.Event != "WriteReject" && e.Event != "ReadAccept" && e.Event != "ReadReject" {
@@ -223,7 +246,7 @@ func (g *traceGraph) checkProvenance() Verdict {
 }
 
 // checkC12 reconstructs the durable maximum using storage's own sequence only.
-// derives: C1.2, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.2, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (g *traceGraph) checkC12(storage string) Verdict {
 	var highest uint64
 	for _, e := range g.local[storage] {
@@ -247,7 +270,7 @@ func (g *traceGraph) checkC12(storage string) Verdict {
 }
 
 // checkC13 correlates each success to THIS attempt's acceptance, including late acks.
-// derives: C1.3, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.3, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (g *traceGraph) checkC13() Verdict {
 	unknown := Verdict{}
 acks:
@@ -280,7 +303,7 @@ acks:
 					continue
 				}
 				parent, exists := g.directEvent(candidate, "WriteAttempt")
-				if exists && (Ref{parent.Proc, parent.Seq}) == (Ref{attempt.Proc, attempt.Seq}) {
+				if exists && (Ref{parent.Proc, parent.Seq, parent.Inc}) == (Ref{attempt.Proc, attempt.Seq, attempt.Inc}) {
 					unknown = Verdict{Reason: "success ack omits an existing acceptance reference"}
 					continue acks
 				}
@@ -299,7 +322,7 @@ acks:
 }
 
 // checkC14 independently reconstructs the final environment from Fault records.
-// derives: C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, E1, C2.1, C2.2
+// derives: C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, E1, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (g *traceGraph) checkC14(s Schedule, evidence RunEvidence) Verdict {
 	if len(evidence.Witnesses) == 0 {
 		return Verdict{}
@@ -315,7 +338,7 @@ func (g *traceGraph) checkC14(s Schedule, evidence RunEvidence) Verdict {
 		if e.Event != "Fault" {
 			continue
 		}
-		lastFault = Ref{e.Proc, e.Seq}
+		lastFault = Ref{e.Proc, e.Seq, e.Inc}
 		if e.Crash != "" {
 			up[e.Crash] = false
 			paused[e.Crash] = false
@@ -324,7 +347,7 @@ func (g *traceGraph) checkC14(s Schedule, evidence RunEvidence) Verdict {
 			up[e.Restart] = true
 		}
 		// Independently reconstruct the directed environment from observable faults.
-		// derives: C1.4, F1.2, F2.1, F2.2, L2, L3
+		// derives: C1.4, F1.2, F2.1, F2.2, L2, L3, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 		if e.Partition != nil {
 			for _, a := range e.Partition[0] {
 				for _, b := range e.Partition[1] {
@@ -359,12 +382,11 @@ func (g *traceGraph) checkC14(s Schedule, evidence RunEvidence) Verdict {
 		if !up[client] || paused[client] || !up[storage] || !connected(client, storage) {
 			return Verdict{Reason: "progress certificate has unavailable requester/storage"}
 		}
-		clique := false
-		for i, a := range s.Processes.Lease {
-			for _, b := range s.Processes.Lease[i+1:] {
-				if connected(a, b) && connected(a, client) && connected(b, client) && connected(a, storage) && connected(b, storage) {
-					clique = true
-				}
+		mem, eligibility, _ := g.finalMembership(s)
+		clique := cliquePremise(mem, mem, []string{client, storage}, func(n string) bool { return eligibility[n] }, connected)
+		for _, req := range g.ordered {
+			if req.Event == "ReconfigRequest" && up[req.Proc] && g.requestPending(req) {
+				return Verdict{Reason: "progress horizon while reconfiguration pending"}
 			}
 		}
 		if !clique {
@@ -382,13 +404,13 @@ func (g *traceGraph) checkC14(s Schedule, evidence RunEvidence) Verdict {
 }
 
 // checkTrace reports clause failures before operational incompleteness.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, E1, E2, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, E1, E2, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func checkTrace(path string, s Schedule, evidence RunEvidence) Verdict {
 	g, err := readTrace(path)
 	if err != nil {
 		return Verdict{Reason: err.Error()}
 	}
-	checks := []Verdict{g.checkC11(), g.checkC12(s.Processes.Storage[0]), g.checkC13(), g.checkC14(s, evidence), g.checkC21(s.Processes.Storage[0]), g.checkC22(s.Processes.Storage[0]), g.checkProvenance(), g.checkAckAnswers(), g.checkGrantDeliveries(s, evidence)}
+	checks := []Verdict{g.checkC11(), g.checkC12(s.Processes.Storage[0]), g.checkC13(), g.checkC14(s, evidence), g.checkC21(s.Processes.Storage[0]), g.checkC22(s.Processes.Storage[0]), g.checkProvenance(), g.checkAckAnswers(), g.checkGrantDeliveries(s, evidence), g.checkV3(path, s, evidence)}
 	for _, v := range checks {
 		if v.Clause != "" {
 			return v
@@ -409,5 +431,35 @@ func checkTrace(path string, s Schedule, evidence RunEvidence) Verdict {
 }
 
 // upName validates a reconstructed fault endpoint against the shared identities.
-// derives: C1.4, F2.1, F2.2, L1, L3
+// derives: C1.4, F2.1, F2.2, L1, L3, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func upName(s Schedule, id string) bool { return processRoles(s)[id] != "" }
+
+// checkV3 delegates the shared evidence semantics to the supplied independent replay checker.
+// derives: C1.1, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
+func (g *traceGraph) checkV3(path string, s Schedule, evidence RunEvidence) Verdict {
+	v5 := false
+	for _, v := range g.ordered {
+		if v.Event == "ConfigCommitted" {
+			v5 = true
+			break
+		}
+	}
+	if !v5 {
+		return Verdict{}
+	}
+	out, err := exec.Command("python3", "../observe/decision_replay.py", path).CombinedOutput()
+	if err != nil {
+		msg := string(out)
+		for _, clause := range []string{"C3.1", "C3.7", "C3.8", "C1.1"} {
+			if strings.Contains(msg, "("+clause+")") {
+				return Verdict{Clause: clause, Reason: strings.TrimSpace(msg)}
+			}
+		}
+		if strings.Contains(msg, "outcome contradicts") || strings.Contains(msg, "UNEXPLAINED inputs") {
+			return Verdict{Clause: "C3.5", Reason: strings.TrimSpace(msg)}
+		}
+		return Verdict{Reason: strings.TrimSpace(msg)}
+	}
+	// C3.4 uses a recorded finite stable horizon, with premise rechecked below.
+	return g.checkReconfigProgress(s, evidence)
+}
diff --git a/impl/check_answers.go b/impl/check_answers.go
index ba969a0..156b822 100644
--- a/impl/check_answers.go
+++ b/impl/check_answers.go
@@ -1,11 +1,11 @@
-// derives: C1.3, C2.2, F1.1, F1.2, F1.3
+// derives: C1.3, C2.2, F1.1, F1.2, F1.3, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 package main
 
 import "fmt"
 
 // checkAckAnswers enforces observe schema v3 without inventing a contract clause.
 // Redundant identity must match causal provenance even for same-token retries.
-// derives: C1.3, C2.2, F1.1, F1.2, F1.3
+// derives: C1.3, C2.2, F1.1, F1.2, F1.3, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (g *traceGraph) checkAckAnswers() Verdict {
 	for _, ack := range g.ordered {
 		attemptName, acceptName, rejectName := "", "", ""
@@ -24,15 +24,15 @@ func (g *traceGraph) checkAckAnswers() Verdict {
 		if !ok || attempt.Event != attemptName || attempt.Proc != ack.Proc || attempt.Client != ack.Client || attempt.Proc != ack.Client || attempt.Key != ack.Key || attempt.Token != ack.Token {
 			return Verdict{Reason: fmt.Sprintf("ack %s:%d answers does not name its matching attempt", ack.Proc, ack.Seq)}
 		}
-		if !g.precedes(*ack.Answers, Ref{ack.Proc, ack.Seq}) {
+		if !g.precedes(*ack.Answers, Ref{ack.Proc, ack.Seq, ack.Inc}) {
 			return Verdict{Reason: "ack answers is not reachable through causal provenance"}
 		}
 		if decision, found := g.directEvent(ack, acceptName, rejectName); found {
 			actual, exists := g.directEvent(decision, attemptName)
-			if !exists || (Ref{actual.Proc, actual.Seq}) != *ack.Answers {
+			if !exists || (Ref{actual.Proc, actual.Seq, actual.Inc}) != *ack.Answers {
 				return Verdict{Reason: "ack answers disagrees with storage decision attempt"}
 			}
-		} else if actual, found := g.directEvent(ack, attemptName); found && (Ref{actual.Proc, actual.Seq}) != *ack.Answers {
+		} else if actual, found := g.directEvent(ack, attemptName); found && (Ref{actual.Proc, actual.Seq, actual.Inc}) != *ack.Answers {
 			return Verdict{Reason: "ack answers disagrees with direct attempt cause"}
 		}
 	}
diff --git a/impl/check_reads.go b/impl/check_reads.go
index d503bb8..d1989d7 100644
--- a/impl/check_reads.go
+++ b/impl/check_reads.go
@@ -1,11 +1,11 @@
-// derives: C2.1, C2.2, F1.1, F1.2, F1.3
+// derives: C2.1, C2.2, F1.1, F1.2, F1.3, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 package main
 
 import "fmt"
 
 // checkC21 reconstructs the write-only fence in storage order, including restarts.
 // Reads must report that ledger but never advance it, even with a larger token.
-// derives: C2.1, C1.2, F1.1, F1.2, F1.3
+// derives: C2.1, C1.2, F1.1, F1.2, F1.3, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (g *traceGraph) checkC21(storage string) Verdict {
 	var highest uint64
 	for _, e := range g.local[storage] {
@@ -30,7 +30,7 @@ func (g *traceGraph) checkC21(storage string) Verdict {
 
 // checkC22 reconstructs value snapshots and requires exact attempt/serve/ack linkage.
 // Missing evidence is distinguished from a witnessed wrong value or unserved read.
-// derives: C2.2, C1.2, C1.3, F1.1, F1.2, F1.3, E2
+// derives: C2.2, C1.2, C1.3, F1.1, F1.2, F1.3, E2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (g *traceGraph) checkC22(storage string) Verdict {
 	unknown := Verdict{}
 	value := ""
@@ -96,7 +96,7 @@ acks:
 					continue
 				}
 				parent, exists := g.directEvent(candidate, "ReadAttempt")
-				if exists && (Ref{parent.Proc, parent.Seq}) == (Ref{attempt.Proc, attempt.Seq}) {
+				if exists && (Ref{parent.Proc, parent.Seq, parent.Inc}) == (Ref{attempt.Proc, attempt.Seq, attempt.Inc}) {
 					unknown = Verdict{Reason: "served ack omits an existing serve reference"}
 					continue acks
 				}
diff --git a/impl/check_routing.go b/impl/check_routing.go
index ea071f7..6507e0e 100644
--- a/impl/check_routing.go
+++ b/impl/check_routing.go
@@ -1,10 +1,10 @@
-// derives: C1.1, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, L3
+// derives: C1.1, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, L3, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 package main
 
 import "fmt"
 
 // routeEnvironment reconstructs the state at a hop's send-fault reference.
-// derives: C1.4, F1.1, F1.2, F1.3, F2.1, F2.2
+// derives: C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type routeEnvironment struct {
 	up         map[string]bool
 	generation map[string]uint64
@@ -13,7 +13,7 @@ type routeEnvironment struct {
 }
 
 // routingEnvironments reads only observable Fault records, not the live injector.
-// derives: C1.4, F1.1, F1.2, F1.3, F2.1, F2.2
+// derives: C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (g *traceGraph) routingEnvironments(s Schedule) map[Ref]routeEnvironment {
 	states := map[Ref]routeEnvironment{}
 	current := routeEnvironment{map[string]bool{}, map[string]uint64{}, map[link]bool{}, map[string]bool{}}
@@ -78,14 +78,14 @@ func (g *traceGraph) routingEnvironments(s Schedule) map[Ref]routeEnvironment {
 		if e.Resume != "" {
 			current.paused[e.Resume] = false
 		}
-		save(Ref{e.Proc, e.Seq})
+		save(Ref{e.Proc, e.Seq, e.Inc})
 	}
 	return states
 }
 
 // checkGrantDeliveries checks route plausibility and exact identities independently.
 // Actual receipt and the duration horizon remain trusted sidecar instrumentation.
-// derives: C1.1, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, L3
+// derives: C1.1, C1.4, F1.1, F1.2, F1.3, F2.1, F2.2, L3, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (g *traceGraph) checkGrantDeliveries(s Schedule, evidence RunEvidence) Verdict {
 	states := g.routingEnvironments(s)
 	roles := processRoles(s)
@@ -94,7 +94,7 @@ func (g *traceGraph) checkGrantDeliveries(s Schedule, evidence RunEvidence) Verd
 		req, ok := g.events[d.Request]
 		grant, issued := g.events[d.Grant]
 		actual, answers := g.directEvent(grant, "Request")
-		if !ok || !issued || req.Event != "Request" || grant.Event != "Grant" || req.Client != grant.Client || !answers || (Ref{actual.Proc, actual.Seq}) != d.Request || seen[d.Request] {
+		if !ok || !issued || req.Event != "Request" || grant.Event != "Grant" || req.Client != grant.Client || !answers || (Ref{actual.Proc, actual.Seq, actual.Inc}) != d.Request || seen[d.Request] {
 			return Verdict{Reason: "invalid/duplicate grant delivery identity"}
 		}
 		seen[d.Request] = true
@@ -139,7 +139,7 @@ func (g *traceGraph) checkGrantDeliveries(s Schedule, evidence RunEvidence) Verd
 
 // requestObtained requires receipt evidence or an observable operation using a grant.
 // An issuer's Grant alone says nothing about delivery to its client.
-// derives: C1.4, F1.1, F2.1, F2.2, L3
+// derives: C1.4, F1.1, F2.1, F2.2, L3, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (g *traceGraph) requestObtained(request Ref, evidence RunEvidence) bool {
 	for _, d := range evidence.Deliveries {
 		if d.Request == request {
@@ -155,7 +155,7 @@ func (g *traceGraph) requestObtained(request Ref, evidence RunEvidence) bool {
 			continue
 		}
 		req, ok := g.directEvent(grant, "Request")
-		if ok && (Ref{req.Proc, req.Seq}) == request && e.Client == req.Client {
+		if ok && (Ref{req.Proc, req.Seq, req.Inc}) == request && e.Client == req.Client {
 			return true
 		}
 	}
diff --git a/impl/check_test.go b/impl/check_test.go
index 2492883..ffb7d24 100644
--- a/impl/check_test.go
+++ b/impl/check_test.go
@@ -14,10 +14,10 @@ func checkerFixture() []Event {
 	zero := uint64(0)
 	return []Event{
 		{Proc: "c1", Seq: 1, Event: "Request", Client: "c1", Key: "k"},
-		{Proc: "n1", Seq: 1, Event: "Grant", Client: "c1", Key: "k", Token: 7, Term: 2, Lifetime: 40, Causes: []Ref{{"c1", 1}}},
-		{Proc: "c1", Seq: 2, Event: "WriteAttempt", Client: "c1", Key: "k", Token: 7, Term: 2, Value: "v", Causes: []Ref{{"n1", 1}}},
-		{Proc: "s", Seq: 1, Event: "WriteAccept", Key: "k", Token: 7, Term: 2, HighestBefore: &zero, Causes: []Ref{{"c1", 2}}},
-		{Proc: "c1", Seq: 3, Event: "WriteAck", Answers: &Ref{"c1", 2}, Client: "c1", Key: "k", Token: 7, Outcome: "accepted", Causes: []Ref{{"s", 1}}},
+		{Proc: "n1", Seq: 1, Event: "Grant", Client: "c1", Key: "k", Token: 7, Term: 2, Lifetime: 40, Causes: []Ref{{"c1", 1, 0}}},
+		{Proc: "c1", Seq: 2, Event: "WriteAttempt", Client: "c1", Key: "k", Token: 7, Term: 2, Value: "v", Causes: []Ref{{"n1", 1, 0}}},
+		{Proc: "s", Seq: 1, Event: "WriteAccept", Key: "k", Token: 7, Term: 2, HighestBefore: &zero, Causes: []Ref{{"c1", 2, 0}}},
+		{Proc: "c1", Seq: 3, Event: "WriteAck", Answers: &Ref{"c1", 2, 0}, Client: "c1", Key: "k", Token: 7, Outcome: "accepted", Causes: []Ref{{"s", 1, 0}}},
 	}
 }
 
@@ -71,7 +71,7 @@ func TestC11C12C13_CausalOrder(t *testing.T) {
 // derives: C1.1, F1.1
 func TestC11_F11_ReusedToken(t *testing.T) {
 	events := checkerFixture()
-	events = append(events, Event{Proc: "c2", Seq: 1, Event: "Request", Client: "c2", Key: "k"}, Event{Proc: "n2", Seq: 1, Event: "Grant", Client: "c2", Key: "k", Token: 7, Term: 3, Lifetime: 40, Causes: []Ref{{"c2", 1}, {"n1", 1}}})
+	events = append(events, Event{Proc: "c2", Seq: 1, Event: "Request", Client: "c2", Key: "k"}, Event{Proc: "n2", Seq: 1, Event: "Grant", Client: "c2", Key: "k", Token: 7, Term: 3, Lifetime: 40, Causes: []Ref{{"c2", 1, 0}, {"n1", 1, 0}}})
 	v := checkTrace(writeFixture(t, events), fixtureSchedule(), RunEvidence{Completed: true})
 	if v.Clause != "C1.1" {
 		t.Fatalf("wanted C1.1, got %+v", v)
@@ -83,7 +83,7 @@ func TestC11_F11_ReusedToken(t *testing.T) {
 func TestC12_F11_LedgerLoss(t *testing.T) {
 	events := checkerFixture()
 	zero := uint64(0)
-	events = append(events, Event{Proc: "s", Seq: 2, Event: "WriteAccept", Key: "k", Token: 7, Term: 2, HighestBefore: &zero, Causes: []Ref{{"c1", 2}}})
+	events = append(events, Event{Proc: "s", Seq: 2, Event: "WriteAccept", Key: "k", Token: 7, Term: 2, HighestBefore: &zero, Causes: []Ref{{"c1", 2, 0}}})
 	v := checkTrace(writeFixture(t, events), fixtureSchedule(), RunEvidence{Completed: true})
 	if v.Clause != "C1.2" {
 		t.Fatalf("wanted C1.2, got %+v", v)
@@ -95,7 +95,7 @@ func TestC12_F11_LedgerLoss(t *testing.T) {
 func TestC12_F12_EqualTokenAllowed(t *testing.T) {
 	events := checkerFixture()
 	seven := uint64(7)
-	events = append(events, Event{Proc: "s", Seq: 2, Event: "WriteAccept", Key: "k", Token: 7, Term: 2, HighestBefore: &seven, Causes: []Ref{{"c1", 2}}})
+	events = append(events, Event{Proc: "s", Seq: 2, Event: "WriteAccept", Key: "k", Token: 7, Term: 2, HighestBefore: &seven, Causes: []Ref{{"c1", 2, 0}}})
 	v := checkTrace(writeFixture(t, events), fixtureSchedule(), RunEvidence{Completed: true})
 	if v != (Verdict{}) {
 		t.Fatalf("equal token must be accepted: %+v", v)
@@ -106,7 +106,7 @@ func TestC12_F12_EqualTokenAllowed(t *testing.T) {
 // derives: C1.3, F1.2
 func TestC13_F12_UnacceptedAttempt(t *testing.T) {
 	events := checkerFixture()
-	events = append(events, Event{Proc: "c1", Seq: 4, Event: "WriteAttempt", Client: "c1", Key: "k", Token: 7, Term: 2, Value: "different-attempt", Causes: []Ref{{"n1", 1}}}, Event{Proc: "c1", Seq: 5, Event: "WriteAck", Answers: &Ref{"c1", 4}, Client: "c1", Key: "k", Token: 7, Outcome: "accepted", Causes: []Ref{{"c1", 4}}})
+	events = append(events, Event{Proc: "c1", Seq: 4, Event: "WriteAttempt", Client: "c1", Key: "k", Token: 7, Term: 2, Value: "different-attempt", Causes: []Ref{{"n1", 1, 0}}}, Event{Proc: "c1", Seq: 5, Event: "WriteAck", Answers: &Ref{"c1", 4, 0}, Client: "c1", Key: "k", Token: 7, Outcome: "accepted", Causes: []Ref{{"c1", 4, 0}}})
 	v := checkTrace(writeFixture(t, events), fixtureSchedule(), RunEvidence{Completed: true})
 	if v.Clause != "C1.3" {
 		t.Fatalf("wanted C1.3, got %+v", v)
@@ -117,7 +117,7 @@ func TestC13_F12_UnacceptedAttempt(t *testing.T) {
 // derives: C1.3, F1.3
 func TestC13_F13_MissingLinkUnexplained(t *testing.T) {
 	events := checkerFixture()
-	events[4].Causes = []Ref{{"c1", 2}}
+	events[4].Causes = []Ref{{"c1", 2, 0}}
 	v := checkTrace(writeFixture(t, events), fixtureSchedule(), RunEvidence{Completed: true})
 	if v.Clause != "" || v.Reason == "" {
 		t.Fatalf("wanted UNEXPLAINED, got %+v", v)
@@ -127,13 +127,13 @@ func TestC13_F13_MissingLinkUnexplained(t *testing.T) {
 // TestC14_F11_ProgressHorizon distinguishes a finite liveness witness from a timeout.
 // derives: C1.4, F1.1
 func TestC14_F11_ProgressHorizon(t *testing.T) {
-	events := []Event{{Proc: "env", Seq: 1, Event: "Fault", Cell: "F1.1", Crash: "n1"}, {Proc: "c1", Seq: 1, Event: "Request", Client: "c1", Key: "k", Causes: []Ref{{"env", 1}}}}
+	events := []Event{{Proc: "env", Seq: 1, Event: "Fault", Cell: "F1.1", Crash: "n1"}, {Proc: "c1", Seq: 1, Event: "Request", Client: "c1", Key: "k", Causes: []Ref{{"env", 1, 0}}}}
 	path := writeFixture(t, events)
 	v := checkTrace(path, fixtureSchedule(), RunEvidence{Reason: "timeout"})
 	if v.Clause != "" || v.Reason == "" {
 		t.Fatalf("timeout alone is not C1.4: %+v", v)
 	}
-	evidence := RunEvidence{Witnesses: []ProgressWitness{{Request: Ref{"c1", 1}, StableFault: Ref{"env", 1}, BudgetMillis: 3000}}}
+	evidence := RunEvidence{Witnesses: []ProgressWitness{{Request: Ref{"c1", 1, 0}, StableFault: Ref{"env", 1, 0}, BudgetMillis: 3000}}}
 	v = checkTrace(path, fixtureSchedule(), evidence)
 	if v.Clause != "C1.4" {
 		t.Fatalf("wanted C1.4 with eligible horizon: %+v", v)
diff --git a/impl/consensus.go b/impl/consensus.go
index 403fe76..f0a7d20 100644
--- a/impl/consensus.go
+++ b/impl/consensus.go
@@ -1,9 +1,9 @@
-// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
+// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 package main
 
 import (
 	"bytes"
-	"encoding/binary"
+	"encoding/json"
 	"fmt"
 	raft "go.etcd.io/raft/v3"
 	pb "go.etcd.io/raft/v3/raftpb"
@@ -12,7 +12,7 @@ import (
 )
 
 // proposalFlight correlates one committed-library command with a live request.
-// derives: C1.1, C1.4, F1.1, F2.1, F2.2
+// derives: C1.1, C1.4, F1.1, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type proposalFlight struct {
 	id         uint64
 	completion completedAllocation
@@ -21,7 +21,7 @@ type proposalFlight struct {
 
 // collectReady persists before sends and applies only committed Raft entries.
 // Sorting message bytes removes upstream map iteration from scheduler inputs.
-// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
+// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) collectReady(n *LeaseNode) {
 	for n.peer != nil && n.peer.HasReady() {
 		rd := n.peer.Ready()
@@ -30,6 +30,15 @@ func (e *Engine) collectReady(n *LeaseNode) {
 				e.network.problem = err
 				return
 			}
+			n.applied = rd.Snapshot.Metadata.Index
+			n.conf = rd.Snapshot.Metadata.ConfState
+			var state snapshotState
+			if json.Unmarshal(rd.Snapshot.Data, &state) == nil {
+				if state.Commit.Epoch > 0 {
+					e.learnCommit(n, state.Commit, Ref{})
+				}
+				n.lastToken = state.LastToken
+			}
 		}
 		if err := n.durable.Append(rd.Entries); err != nil {
 			e.network.problem = err
@@ -41,6 +50,9 @@ func (e *Engine) collectReady(n *LeaseNode) {
 				return
 			}
 		}
+		for _, entry := range rd.Entries {
+			e.persistedAgreement(n, entry)
+		}
 		sort.SliceStable(rd.Messages, func(i, j int) bool {
 			a, _ := rd.Messages[i].Marshal()
 			b, _ := rd.Messages[j].Marshal()
@@ -52,33 +64,60 @@ func (e *Engine) collectReady(n *LeaseNode) {
 			if err != nil {
 				continue
 			}
-			e.network.wire = append(e.network.wire, RaftPacket{m, ticket, e.now().Add(e.jitter())})
+			agreements := []Agreement{}
+			if m.Type == pb.MsgAppResp && !m.Reject {
+				indexes := []uint64{}
+				for index := range n.agreements {
+					if index <= m.Index {
+						indexes = append(indexes, index)
+					}
+				}
+				sort.Slice(indexes, func(i, j int) bool { return indexes[i] < indexes[j] })
+				for _, index := range indexes {
+					agreements = append(agreements, n.agreements[index])
+				}
+			}
+			// Ineligible recovering nodes persist and report evidence, but never supply a Raft vote or quorum ack.
+			if !e.nodeEligible(n.id, n.epoch) && (m.Type == pb.MsgVoteResp || m.Type == pb.MsgPreVoteResp) {
+				continue
+			}
+			e.network.wire = append(e.network.wire, RaftPacket{agreements: agreements, message: m, ticket: ticket, due: e.now().Add(e.jitter())})
 		}
 		for _, entry := range rd.CommittedEntries {
 			if entry.Index <= n.applied {
 				continue
 			}
 			n.applied = entry.Index
+			if entry.Type == pb.EntryConfChangeV2 {
+				e.applyConfiguration(n, entry)
+				continue
+			}
 			if entry.Type != pb.EntryNormal {
-				e.network.problem = fmt.Errorf("unexpected membership change")
+				e.network.problem = fmt.Errorf("unsupported membership encoding")
 				return
 			}
 			if len(entry.Data) == 0 {
 				continue
 			}
-			if len(entry.Data) != 8 {
-				e.network.problem = fmt.Errorf("bad allocation command")
+			var command grantLogCommand
+			if err := json.Unmarshal(entry.Data, &command); err != nil {
+				e.network.problem = err
 				return
 			}
-			id := binary.BigEndian.Uint64(entry.Data)
+			id := command.ID
+
 			if e.inflight && e.flight != nil && e.flight.id == id && e.flight.completion.node == n.id && e.flight.completion.generation == n.generation {
 				result := e.flight.completion
-				result.allocation = Allocation{entry.Index, entry.Term}
+				result.allocation = Allocation{Token: entry.Index, Term: entry.Term, Proposal: command.Proposal}
 				e.inflight = false
 				e.flight = nil
 				e.finishAllocation(result)
 			}
 		}
+		if n.applied > 1 {
+			data, _ := json.Marshal(snapshotState{n.commit, n.lastToken})
+			_, _ = n.durable.CreateSnapshot(n.applied, &n.conf, data)
+		}
 		n.peer.Advance(rd)
 	}
 }
@@ -86,9 +125,31 @@ func (e *Engine) collectReady(n *LeaseNode) {
 // stepConsensus runs every library transition on the seeded logical event loop.
 // Follower/candidate ticks cannot consult the library's random election timeout:
 // quiesced ticks advance lease age; only our seeded Campaign deadlines can elect.
-// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
+// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) stepConsensus() {
 	now := e.now()
+	// Recovery requests obtain a protocol snapshot from a connected live leader.
+	// derives: C1.1, C3.7, C3.8, F3.3, C3.1, C3.4, C3.5, F3.1, F3.2
+	for _, id := range e.schedule.Processes.Lease {
+		leader := e.nodes[id]
+		if leader.peer == nil || leader.peer.BasicStatus().RaftState != raft.StateLeader {
+			continue
+		}
+		for _, to := range e.schedule.Processes.Lease {
+			target := e.nodes[to]
+			if target.peer == nil || target.applied != 0 || !e.canSend(id, to) {
+				continue
+			}
+			snap, _ := leader.durable.Snapshot()
+			if snap.Metadata.Index == 0 {
+				continue
+			}
+			ticket, err := e.network.admit(id, to)
+			if err == nil {
+				e.network.wire = append(e.network.wire, RaftPacket{message: pb.Message{Type: pb.MsgSnap, From: leader.number, To: target.number, Term: leader.peer.BasicStatus().Term, Snapshot: &snap}, ticket: ticket, due: now.Add(e.jitter())})
+			}
+		}
+	}
 	if now.Sub(time.Unix(0, 0).UTC())%(10*time.Millisecond) == 0 {
 		for _, id := range e.schedule.Processes.Lease {
 			n := e.nodes[id]
@@ -107,7 +168,10 @@ func (e *Engine) stepConsensus() {
 		if n.peer == nil {
 			continue
 		}
-		if n.peer.BasicStatus().RaftState != raft.StateLeader && !now.Before(n.electionAt) {
+		if e.nodeEligible(id, n.epoch) && contains(n.members, id) && n.peer.BasicStatus().RaftState != raft.StateLeader && !now.Before(n.electionAt) {
+			if !e.canCampaign(n) {
+				continue
+			}
 			if err := n.peer.Campaign(); err != nil {
 				e.network.problem = err
 			}
@@ -128,7 +192,18 @@ func (e *Engine) stepConsensus() {
 		if n == nil || n.peer == nil || e.network.generation[id] != packet.ticket.toGeneration {
 			continue
 		}
-		if err := n.peer.Step(packet.message); err != nil {
+		if packet.message.Type == pb.MsgAppResp && !packet.message.Reject {
+			for _, a := range packet.agreements {
+				e.receiveAgreement(n, a)
+			}
+		}
+		if packet.message.Type == pb.MsgAppResp && !e.nodeEligible(packet.ticket.path.from, n.epoch) {
+			continue
+		}
+		if n.applied == 0 && packet.message.Type != pb.MsgSnap {
+			continue
+		}
+		if err := n.peer.Step(packet.message); err != nil && err != raft.ErrStepPeerNotFound {
 			e.network.problem = err
 			continue
 		}
@@ -138,6 +213,25 @@ func (e *Engine) stepConsensus() {
 		}
 		e.collectReady(n)
 	}
+	if e.pendingCommit != nil {
+		p := e.pendingCommit
+		n := e.nodes[p.Node]
+		if e.majorityEvidence(n, p.Proposal, n.members, n.epoch) && e.majorityEvidence(n, p.Proposal, p.Proposal.Members, p.Proposal.Epoch) {
+			e.decideConfiguration(n, p.Proposal)
+		}
+	}
+	for _, id := range e.schedule.Processes.Lease {
+		n := e.nodes[id]
+		if n.peer == nil {
+			continue
+		}
+		for _, to := range e.schedule.Processes.Lease {
+			other := e.nodes[to]
+			if other.peer != nil && other.epoch < n.epoch && e.canSend(id, to) {
+				e.configWire = append(e.configWire, ConfigPacket{to, other.generation, n.commit, n.commitRef, e.now().Add(e.jitter())})
+			}
+		}
+	}
 	if e.inflight && e.flight != nil && !now.Before(e.flight.deadline) {
 		e.inflight = false
 		e.flight = nil
diff --git a/impl/engine.go b/impl/engine.go
index d6e23db..7997034 100644
--- a/impl/engine.go
+++ b/impl/engine.go
@@ -1,8 +1,9 @@
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 package main
 
 import (
 	"fmt"
+	"math"
 	"math/rand"
 	"sort"
 	"time"
@@ -11,15 +12,15 @@ import (
 )
 
 // grantLifetime is scheduler time; observe lifetimes use logical milliseconds.
-// derives: C1.1, C1.4, F1.3, C2.1, C2.2
+// derives: C1.1, C1.4, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 const grantLifetime = 40 * time.Millisecond
 
 // progressHorizon is the preregistered finite liveness opportunity.
-// derives: C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 const progressHorizon = 3 * time.Second
 
 // HeldGrant retains provenance even when an old holder resumes after expiry.
-// derives: C1.1, C1.2, F1.1, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, F1.1, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type HeldGrant struct {
 	token, term uint64
 	ref         Ref
@@ -27,7 +28,7 @@ type HeldGrant struct {
 }
 
 // Client retains no grant or inbox across simulated crash/restart.
-// derives: C1.2, C1.3, C1.4, F1.1, F1.3, C2.1, C2.2
+// derives: C1.2, C1.3, C1.4, F1.1, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type Client struct {
 	id         string
 	up, paused bool
@@ -37,7 +38,7 @@ type Client struct {
 }
 
 // RequestState tracks a particular observable request, not merely a client ID.
-// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type RequestState struct {
 	client        string
 	ref           Ref
@@ -50,19 +51,20 @@ type RequestState struct {
 }
 
 // WireMessage is a sampled transport delivery or a paused client's inbox item.
-// derives: C1.2, C1.3, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.2, C1.3, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type WireMessage struct {
 	kind, client      string
 	generation        uint64
 	attempt, decision Ref
 	grant             HeldGrant
 	value, outcome    string
+	nullValue         bool
 	due               time.Time
 	pendingSend       bool // derives: F2.1, F2.2 — local reply work before network send
 }
 
 // completedAllocation preserves exact committed-proposal/request correspondence.
-// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, C2.1, C2.2
+// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type completedAllocation struct {
 	request    *RequestState
 	node       string
@@ -73,7 +75,7 @@ type completedAllocation struct {
 }
 
 // ProgressWitness records a finite progress horizon separately from the schema.
-// derives: C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type ProgressWitness struct {
 	Request      Ref   `json:"request"`
 	StableFault  Ref   `json:"stable_fault"`
@@ -81,29 +83,45 @@ type ProgressWitness struct {
 }
 
 // RunEvidence contains operational horizon certificates, never event ordering.
-// derives: C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, E1, E2, C2.1, C2.2
+// derives: C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, E1, E2, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 // LogicalClockEvidence identifies scheduler time without adding a clock to JSONL.
-// derives: C1.4, F1.3, F2.1, F2.2, E1
+// derives: C1.4, F1.3, F2.1, F2.2, E1, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type LogicalClockEvidence struct {
 	Version string `json:"version"`
 	Seed    int64  `json:"seed"`
 	Millis  int64  `json:"logical_ms"`
 }
 
-// derives: C1.1, C1.4, F1.1, F1.3, F2.1, F2.2, E1
+// derives: C1.1, C1.4, F1.1, F1.3, F2.1, F2.2, E1, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type RunEvidence struct {
-	Clock       LogicalClockEvidence `json:"clock"` // derives: C1.4, F1.3, F2.1, F2.2
-	Derives     []string             `json:"derives"`
-	Operational string               `json:"operational_error,omitempty"`
-	Witnesses   []ProgressWitness    `json:"progress_horizons"`
-	Completed   bool                 `json:"schedule_completed"`
-	Reason      string               `json:"reason,omitempty"`
-	Deliveries  []GrantDelivery      `json:"grant_deliveries,omitempty"` // derives: C1.4, F1.1, F2.1, F2.2
+	ReconfigHorizons []ReconfigHorizon    `json:"reconfiguration_horizons,omitempty"`
+	ProtocolState    []string             `json:"protocol_state,omitempty"`
+	Clock            LogicalClockEvidence `json:"clock"` // derives: C1.4, F1.3, F2.1, F2.2
+	Derives          []string             `json:"derives"`
+	Operational      string               `json:"operational_error,omitempty"`
+	Witnesses        []ProgressWitness    `json:"progress_horizons"`
+	Completed        bool                 `json:"schedule_completed"`
+	Reason           string               `json:"reason,omitempty"`
+	Deliveries       []GrantDelivery      `json:"grant_deliveries,omitempty"` // derives: C1.4, F1.1, F2.1, F2.2
 }
 
 // Engine owns every workload, network and Raft transition on one logical clock.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, A1, T1, T2, T3, E1, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, A1, T1, T2, T3, E1, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
+// derives: C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type Engine struct {
+	clockSeen, amnesiaSeen                          bool
+	crashCount                                      int
+	futureFaults                                    int
+	epoch                                           uint64
+	members                                         []string
+	readmitted                                      map[string]uint64
+	readmitEpoch                                    map[string]uint64
+	clocks                                          map[string]int64
+	reconfigs                                       []*Reconfiguration
+	activeConfig                                    *Reconfiguration
+	pendingCommit                                   *pendingConfiguration
+	configWire                                      []ConfigPacket
+	storagePresent                                  bool
 	schedule                                        Schedule
 	seed                                            int64 // derives: C1.1, C1.4, F1.3, F2.1, F2.2
 	out                                             *Emitter
@@ -135,10 +153,20 @@ type Engine struct {
 	partialSeen, simplexSeen                        bool // derives: F2.1, F2.2 — independent mutation activation
 }
 
-// newEngine bootstraps exactly one fixed three-voter configuration.
-// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, C2.1, C2.2
+// newEngine initializes the deployment configuration and all named non-members.
+// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func newEngine(s Schedule, out *Emitter, seed int64, mutation string) (*Engine, error) {
 	e := &Engine{seed: seed, schedule: s, out: out, rng: rand.New(rand.NewSource(seed)), nodes: map[string]*LeaseNode{}, network: newRaftNetwork(), clients: map[string]*Client{}, down: map[link]bool{}, storage: s.Processes.Storage[0], storageUp: true, mutation: mutation}
+	for _, step := range s.Steps {
+		a := step.Do
+		if a.Cell != "" && a.Reconfigure == nil && !a.Heal {
+			e.futureFaults++
+		}
+	}
+	e.members = append([]string{}, initialMembers(s)...)
+	e.readmitted = map[string]uint64{}
+	e.readmitEpoch = map[string]uint64{}
+	e.clocks = map[string]int64{}
 	e.network.owner = e
 	e.now()
 	for index, id := range s.Processes.Lease {
@@ -156,8 +184,13 @@ func newEngine(s Schedule, out *Emitter, seed int64, mutation string) (*Engine,
 			return nil, err
 		}
 	}
+	for _, id := range initialMembers(s) {
+		n := e.nodes[id]
+		n.commit = Event{Proc: id, Event: "ConfigCommitted", Epoch: 0, Members: append([]string{}, initialMembers(s)...)}
+		n.commitRef = e.out.emit(n.commit)
+	}
 	e.connect()
-	if err := e.nodes[s.Processes.Lease[0]].peer.Campaign(); err != nil {
+	if err := e.nodes[initialMembers(s)[0]].peer.Campaign(); err != nil {
 		e.close()
 		return nil, err
 	}
@@ -168,8 +201,8 @@ func newEngine(s Schedule, out *Emitter, seed int64, mutation string) (*Engine,
 	return e, nil
 }
 
-// awaitBootstrap establishes the fixed grantor before start-triggered faults.
-// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, C2.1, C2.2
+// awaitBootstrap establishes the initial grantor before start-triggered faults.
+// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) awaitBootstrap() error {
 	deadline := e.now().Add(progressHorizon)
 	for e.now().Before(deadline) {
@@ -193,11 +226,11 @@ func (e *Engine) awaitBootstrap() error {
 }
 
 // jitter samples a directed packet delay from 1–3 logical milliseconds.
-// derives: C1.2, C1.3, F1.2, F2.1, F2.2, C2.1, C2.2
+// derives: C1.2, C1.3, F1.2, F2.1, F2.2, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) jitter() time.Duration { return time.Duration(1+e.rng.Intn(3)) * time.Millisecond }
 
 // close shuts down nodes even if execution failed partway through setup.
-// derives: F1.1, C1.1, C2.1, C2.2
+// derives: F1.1, C1.1, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) close() {
 	for _, id := range e.schedule.Processes.Lease {
 		if n := e.nodes[id]; n != nil {
@@ -207,7 +240,7 @@ func (e *Engine) close() {
 }
 
 // alive distinguishes durable state from a running process.
-// derives: F1.1, C1.4, C2.1, C2.2
+// derives: F1.1, C1.4, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) alive(id string) bool {
 	if n := e.nodes[id]; n != nil {
 		return n.peer != nil
@@ -215,41 +248,65 @@ func (e *Engine) alive(id string) bool {
 	if c := e.clients[id]; c != nil {
 		return c.up
 	}
+	if contains(e.schedule.Processes.Operators, id) || id == "op" {
+		return true
+	}
 	return id == e.storage && e.storageUp
 }
 
 // connected is a direct bidirectional relation; send admission uses canSend.
-// derives: F1.1, F1.2, F2.1, F2.2, C1.3, C1.4, C2.1, C2.2
+// derives: F1.1, F1.2, F2.1, F2.2, C1.3, C1.4, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) connected(a, b string) bool {
 	return e.canSend(a, b) && e.canSend(b, a)
 }
 
 // connect copies the accumulated directed failures to the Raft transport router.
-// derives: F1.1, F1.2, F2.1, F2.2, C1.1, C1.4, C2.1, C2.2
+// derives: F1.1, F1.2, F2.1, F2.2, C1.1, C1.4, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) connect() { e.network.setDown(e.down) }
 
 // eligible is the contract's majority/storage/requester connectivity predicate.
-// derives: C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) eligible(r *RequestState) bool {
+	if e.futureFaults > 0 {
+		return false
+	}
 	c := e.clients[r.client]
 	if !c.up || c.paused || c.generation != r.generation || !e.connected(r.client, e.storage) {
 		return false
 	}
-	for i, a := range e.schedule.Processes.Lease {
-		if !e.connected(r.client, a) || !e.connected(e.storage, a) {
+	for _, r := range e.reconfigs {
+		if r.Request.Seq != 0 && !r.Done && e.alive(r.Receiver) && r.Generation == e.nodes[r.Receiver].generation {
+			return false
+		}
+	}
+	members := e.members
+	for mask := 1; mask < (1 << len(members)); mask++ {
+		if bitCount(mask)*2 <= len(members) {
 			continue
 		}
-		for _, b := range e.schedule.Processes.Lease[i+1:] {
-			if e.connected(a, b) && e.connected(r.client, b) && e.connected(e.storage, b) {
-				return true
+		ok := true
+		for i, a := range members {
+			if mask&(1<<i) == 0 {
+				continue
+			}
+			if !e.nodeEligible(a, e.epoch) || !e.connected(r.client, a) || !e.connected(e.storage, a) {
+				ok = false
 			}
+			for j, b := range members {
+				if mask&(1<<j) != 0 && !e.connected(a, b) {
+					ok = false
+				}
+			}
+		}
+		if ok {
+			return true
 		}
 	}
 	return false
 }
 
 // request emits once; retries reuse that request's identity.
-// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) request(id string) error {
 	c := e.clients[id]
 	if !c.up || c.paused {
@@ -261,10 +318,10 @@ func (e *Engine) request(id string) error {
 }
 
 // suppressGrant is the deliberate liveness enforcement break, one pair per run.
-// derives: C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) suppressGrant() bool {
 	// mutation: P10 suppress grant service after a minority crash.
-	if e.mutation == "P10" && e.crashSeen {
+	if e.mutation == "P10" && e.crashCount >= 2 {
 		return true
 	}
 	// mutation: P11 suppress grant service after a partition, including after heal.
@@ -272,15 +329,25 @@ func (e *Engine) suppressGrant() bool {
 		return true
 	}
 	// mutation: P12 retain a paused holder forever and suppress later grants.
-	return e.mutation == "P12" && e.pauseSeen || e.mutation == "P25" && e.partialSeen || e.mutation == "P26" && e.simplexSeen
+	return e.mutation == "P52" && e.epoch > 0 || e.mutation == "P53" && e.clockSeen || e.mutation == "P54" && e.amnesiaSeen || e.mutation == "P25" && e.partialSeen || e.mutation == "P26" && e.simplexSeen
 }
 
 // pump advances sampled messages and retries requests without blocking faults.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) pump() {
 	e.logicalNow = e.now().Add(time.Millisecond)
 	now := e.now()
 	e.stepConsensus()
+	e.pumpReconfiguration()
+	for _, r := range e.reconfigs {
+		if e.reconfigPremise(r) {
+			if r.EligibleSince.IsZero() {
+				r.EligibleSince = now
+			}
+		} else {
+			r.EligibleSince = time.Time{}
+		}
+	}
 	e.deliver(now)
 	e.deliverLease(now)
 	for _, r := range e.requests {
@@ -296,7 +363,7 @@ func (e *Engine) pump() {
 			r.eligibleSince = time.Time{}
 		}
 	}
-	if e.inflight || now.Before(e.nextGrant) || e.suppressGrant() {
+	if e.inflight || e.activeConfig != nil || now.Before(e.nextGrant) || e.suppressGrant() {
 		return
 	}
 	for offset := 0; offset < len(e.requests); offset++ {
@@ -308,17 +375,30 @@ func (e *Engine) pump() {
 		}
 		for _, id := range e.schedule.Processes.Lease {
 			n := e.nodes[id]
-			if n.peer == nil || n.peer.BasicStatus().RaftState != raft.StateLeader || r.ingress[id] != n.generation {
+			if n.peer == nil || n.peer.BasicStatus().RaftState != raft.StateLeader || !e.nodeEligible(id, n.epoch) || !contains(n.members, id) || r.ingress[id] != n.generation {
+				continue
+			}
+			if g, ok := n.issued[r.ref]; ok {
+				e.leaseWire = append(e.leaseWire, LeasePacket{kind: "grant-send", from: id, to: id, targetGeneration: n.generation, request: r, grant: g, requestHops: append([]RouteHop{}, r.paths[id]...), due: now.Add(8 * time.Millisecond)})
+				e.nextRequest = (index + 1) % len(e.requests)
+				return
+			}
+			if n.hasGranted && e.localClock(id) < n.lastGrantAt+e.lifetimeTicks() {
 				continue
 			}
 			// Only the library's committed entry supplies the index/term token.
-			// derives: C1.1, C1.4, F1.1, F2.1, F2.2
+			// derives: C1.1, C1.4, F1.1, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
+			lastIndex, _ := n.durable.LastIndex()
+			if lastIndex == math.MaxUint64 {
+				e.overflow(n, "token")
+				return
+			}
 			e.proposalID++
 			result := completedAllocation{request: r, node: id, generation: n.generation, route: append([]RouteHop{}, r.paths[id]...)}
 			e.flight = &proposalFlight{e.proposalID, result, now.Add(100 * time.Millisecond)}
 			e.inflight = true
 			e.nextRequest = (index + 1) % len(e.requests)
-			if err := n.peer.Propose(raftCommand(e.proposalID)); err != nil {
+			if err := n.peer.Propose(e.grantCommand(n, r)); err != nil {
 				e.inflight = false
 				e.flight = nil
 			}
@@ -329,7 +409,7 @@ func (e *Engine) pump() {
 }
 
 // finishAllocation records committed issuance independently of reply delivery.
-// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) finishAllocation(v completedAllocation) {
 	r := v.request
 	c := e.clients[r.client]
@@ -349,24 +429,48 @@ func (e *Engine) finishAllocation(v completedAllocation) {
 	// mutation: P3 reuse a token while the preceding holder is paused.
 	if e.mutation == "P3" && e.pauseSeen && e.lastGrant.Seq != 0 {
 		for _, event := range e.out.events {
-			if (Ref{event.Proc, event.Seq}) == e.lastGrant {
+			if (Ref{event.Proc, event.Seq, event.Inc}) == e.lastGrant {
 				token = event.Token
 				break
 			}
 		}
 	}
-	ref := e.out.emit(Event{Proc: v.node, Event: "Grant", Client: r.client, Key: "k", Token: token, Lifetime: grantLifetime.Milliseconds(), Term: v.allocation.Term}, r.ref, e.lastGrant)
+	p := v.allocation.Proposal
+	if p.Kind == "" {
+		p = Proposal{Kind: "grant", Client: r.client, Token: token, Lifetime: e.lifetimeTicks(), ConfigEpoch: n.epoch}
+	}
+	ins := e.evidenceInputs(n, p)
+	if !e.majorityEvidence(n, p, n.members, n.epoch) {
+		e.network.problem = fmt.Errorf("committed grant lacks received eligible agreement evidence")
+		return
+	}
+	ins = append(ins, input("members", n.members), input("config_epoch", n.epoch), input("grantor_term", v.allocation.Term), reference("last_token", n.lastToken, n.lastTokenRef), input("clock", e.localClock(n.id)), input("last_grant_at", n.lastGrantAt))
+	if e.mutation == "P46" || e.mutation == "P47" || e.mutation == "P48" {
+		if n.lastToken > 0 {
+			token = 1
+		}
+	}
+	if e.mutation == "P58" || e.mutation == "P59" || e.mutation == "P60" {
+		ins = ins[len(ins)-6:]
+	}
+	ref := e.out.emit(Event{Proc: v.node, Event: "Grant", Client: r.client, Key: "k", Token: token, Lifetime: e.lifetimeTicks(), Term: v.allocation.Term, ConfigEpoch: n.epoch, Inputs: ins}, r.ref, e.lastGrant)
+	n.lastToken = token
 	now := e.now()
-	grant := HeldGrant{token: token, term: v.allocation.Term, ref: ref, expires: now.Add(grantLifetime)}
+	grant := HeldGrant{token: token, term: v.allocation.Term, ref: ref, expires: now.Add(e.lifetime())}
+	if n.issued == nil {
+		n.issued = map[Ref]HeldGrant{}
+	}
+	n.issued[r.ref] = grant
 	e.leaseWire = append(e.leaseWire, LeasePacket{kind: "grant-send", from: v.node, to: v.node, targetGeneration: v.generation, request: r, grant: grant, requestHops: v.route, due: now.Add(8 * time.Millisecond)})
 	e.lastGrant = ref
 	e.grantor = v.node
 	e.holder = r.client
-	e.nextGrant = now.Add(grantLifetime)
+	n.lastGrantAt = e.localClock(n.id)
+	n.hasGranted = true
 }
 
 // write selects the client's actual grant and queues delivery to storage.
-// derives: C1.2, C1.3, F1.1, F1.2, F2.1, F2.2, F1.3, T3, C2.1, C2.2
+// derives: C1.2, C1.3, F1.1, F1.2, F2.1, F2.2, F1.3, T3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) write(id, value, selection string) error {
 	c := e.clients[id]
 	if !c.up || c.paused || len(c.grants) == 0 {
@@ -396,6 +500,13 @@ func (e *Engine) write(id, value, selection string) error {
 
 	m := WireMessage{kind: "write", client: id, generation: c.generation, attempt: ref, grant: g, value: value, due: e.now().Add(e.jitter())}
 	e.wire = append(e.wire, m)
+	if e.mutation == "P43" || e.mutation == "P44" || e.mutation == "P45" {
+		for i := 1; i <= 2; i++ {
+			copy := m
+			copy.due = copy.due.Add(time.Duration(i) * time.Millisecond)
+			e.wire = append(e.wire, copy)
+		}
+	}
 	if e.rng.Intn(3) == 0 {
 		duplicate := m
 		duplicate.due = duplicate.due.Add(e.jitter())
@@ -405,7 +516,7 @@ func (e *Engine) write(id, value, selection string) error {
 }
 
 // read selects the client's actual grant and queues delivery to storage.
-// derives: C1.2, C1.3, F1.1, F1.2, F2.1, F2.2, F1.3, T3, C2.1, C2.2
+// derives: C1.2, C1.3, F1.1, F1.2, F2.1, F2.2, F1.3, T3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) read(id, selection string) error {
 	c := e.clients[id]
 	if !c.up || c.paused || len(c.grants) == 0 {
@@ -444,7 +555,7 @@ func (e *Engine) read(id, selection string) error {
 }
 
 // ghostAck breaks the client success path only for writes that never reached storage.
-// derives: C1.3, F1.1, F1.2, F2.1, F2.2, C2.1, C2.2
+// derives: C1.3, F1.1, F1.2, F2.1, F2.2, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) ghostAck(m WireMessage) {
 	c := e.clients[m.client]
 	if !c.up || c.paused || c.generation != m.generation {
@@ -452,16 +563,16 @@ func (e *Engine) ghostAck(m WireMessage) {
 	}
 	// mutation: P8 manufacture success for an undelivered write across a partition.
 	if e.mutation == "P8" && e.partitionSeen || e.mutation == "P23" && e.partialSeen {
-		e.out.emit(Event{Proc: m.client, Event: "WriteAck", Answers: &m.attempt, Client: m.client, Key: "k", Token: m.grant.token, Outcome: "accepted"}, m.attempt)
+		e.out.emit(Event{Proc: m.client, Event: "WriteAck", Answers: &m.attempt, Client: m.client, Key: "k", Token: m.grant.token, Term: m.grant.term, Outcome: "accepted"}, m.attempt)
 	}
 }
 
 // storageDecision compares against the retained ledger atomically.
-// derives: C1.2, C1.3, F1.1, F1.2, F2.1, F2.2, F1.3, T1, E2, C2.1, C2.2
+// derives: C1.2, C1.3, F1.1, F1.2, F2.1, F2.2, F1.3, T1, E2, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) storageDecision(m WireMessage) {
 	// P24 bypasses acceptance on a later write, preserving the first accept trigger.
 	// Skip duplicate deliveries of an already accepted attempt as well.
-	// derives: C1.3, F2.2, P24
+	// derives: C1.3, F2.2, P24, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 	if e.mutation == "P24" && e.simplexSeen && e.ledger > 0 {
 		accepted := false
 		for _, v := range e.out.events {
@@ -474,12 +585,12 @@ func (e *Engine) storageDecision(m WireMessage) {
 			}
 		}
 		if !accepted {
-			e.out.emit(Event{Proc: m.client, Event: "WriteAck", Answers: &m.attempt, Client: m.client, Key: "k", Token: m.grant.token, Outcome: "accepted"}, m.attempt)
+			e.out.emit(Event{Proc: m.client, Event: "WriteAck", Answers: &m.attempt, Client: m.client, Key: "k", Token: m.grant.token, Term: m.grant.term, Outcome: "accepted"}, m.attempt)
 			return
 		}
 	}
 	// mutation: P7 after storage restart, bypass acceptance and fabricate its success reply.
-	// derives: C1.3, F1.1, T1, E2, C2.1, C2.2
+	// derives: C1.3, F1.1, T1, E2, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 	if e.mutation == "P7" && e.crashSeen {
 		m.kind = "ack"
 		m.decision = m.attempt
@@ -488,8 +599,17 @@ func (e *Engine) storageDecision(m WireMessage) {
 		return
 	}
 	before := e.ledger
+	stored := e.storedInput()
 	accept := m.grant.token >= before
+	// Mutation: consult the local clock without emitting it as a decision input.
+	// derives: C3.5, F3.1, F3.2, F3.3, C3.1, C3.4, C3.7, C3.8
+	if e.mutation == "P43" || e.mutation == "P44" || e.mutation == "P45" {
+		accept = e.now().UnixMilli()%2 == 0
+	}
 	// mutation: P5 bypass the fencing comparison in the partition path.
+	if e.mutation == "P49" || e.mutation == "P50" || e.mutation == "P51" {
+		accept = true
+	}
 	if e.mutation == "P5" && e.partitionSeen || e.mutation == "P21" && e.partialSeen || e.mutation == "P22" && e.simplexSeen {
 		accept = true
 	}
@@ -503,8 +623,9 @@ func (e *Engine) storageDecision(m WireMessage) {
 		outcome = "accepted"
 		e.ledger = m.grant.token
 		e.storageValue = m.value
+		e.storagePresent = true
 	}
-	ref := e.out.emit(Event{Proc: e.storage, Event: name, Key: "k", Token: m.grant.token, Term: m.grant.term, HighestBefore: &before}, m.attempt)
+	ref := e.out.emit(Event{Proc: e.storage, Event: name, Key: "k", Token: m.grant.token, Term: m.grant.term, HighestBefore: &before, Inputs: []Input{input("token", m.grant.token), input("ledger", before), input("stored_value", stored), input("value", m.value)}}, m.attempt)
 	m.kind = "ack"
 	m.decision = ref
 	m.outcome = outcome
@@ -512,7 +633,7 @@ func (e *Engine) storageDecision(m WireMessage) {
 }
 
 // deliver samples due-message order; a cut drops messages rather than delaying them.
-// derives: C1.2, C1.3, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.2, C1.3, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) deliver(now time.Time) {
 	messages := e.wire
 	e.wire = nil
@@ -542,9 +663,9 @@ func (e *Engine) deliver(now time.Time) {
 		if m.pendingSend {
 			if !e.canSend(e.storage, m.client) {
 				// Wrong-value mutations bypass loss at the reply enforcing path.
-				// derives: C2.2, F2.1, F2.2, P29, P30
+				// derives: C2.2, F2.1, F2.2, P29, P30, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 				if m.kind == "read-ack" && m.outcome == "served" && (e.mutation == "P29" && e.partialSeen || e.mutation == "P30" && e.simplexSeen) && c.up && c.generation == m.generation {
-					e.out.emit(Event{Proc: m.client, Event: "ReadAck", Answers: &m.attempt, Client: m.client, Key: "k", Token: m.grant.token, Outcome: "served", Value: m.value + "-wrong"}, m.decision)
+					e.out.emit(Event{Proc: m.client, Event: "ReadAck", Answers: &m.attempt, Client: m.client, Key: "k", Token: m.grant.token, Term: m.grant.term, Outcome: "served", Value: m.value + "-wrong"}, m.decision)
 				}
 				continue
 			}
@@ -561,12 +682,16 @@ func (e *Engine) deliver(now time.Time) {
 			continue
 		}
 		if m.kind == "read-ack" {
+			if m.outcome == "served" && (e.mutation == "P29" && e.partialSeen || e.mutation == "P30" && e.simplexSeen) {
+				m.value += "-wrong"
+				m.nullValue = false
+			}
 			// mutation: P18 replace a paused reply snapshot with current storage value.
-			// derives: C2.2, F1.3
+			// derives: C2.2, F1.3, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 			if e.mutation == "P18" && e.resumeSeen && m.outcome == "served" {
 				m.value = e.storageValue
 			}
-			e.out.emit(Event{Proc: m.client, Event: "ReadAck", Answers: &m.attempt, Client: m.client, Key: "k", Token: m.grant.token, Outcome: m.outcome, Value: m.value}, m.decision)
+			e.out.emit(Event{Proc: m.client, Event: "ReadAck", Answers: &m.attempt, Client: m.client, Key: "k", Token: m.grant.token, Term: m.grant.term, Outcome: m.outcome, Value: m.value, NullValue: m.nullValue}, m.decision)
 			continue
 		}
 		outcome := m.outcome
@@ -574,12 +699,12 @@ func (e *Engine) deliver(now time.Time) {
 		if e.mutation == "P9" && e.resumeSeen && outcome == "rejected" {
 			outcome = "accepted"
 		}
-		e.out.emit(Event{Proc: m.client, Event: "WriteAck", Answers: &m.attempt, Client: m.client, Key: "k", Token: m.grant.token, Outcome: outcome}, m.decision)
+		e.out.emit(Event{Proc: m.client, Event: "WriteAck", Answers: &m.attempt, Client: m.client, Key: "k", Token: m.grant.token, Term: m.grant.term, Outcome: outcome}, m.decision)
 	}
 }
 
 // expandPartition resolves aliases at the trigger, not when the YAML is parsed.
-// derives: F1.2, F2.1, F2.2, C1.1, C1.2, C1.4, A1, C2.1, C2.2
+// derives: F1.2, F2.1, F2.2, C1.1, C1.2, C1.4, A1, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) expandPartition(input [][]string) ([][]string, error) {
 	output := [][]string{{}, {}}
 	used := map[string]bool{}
@@ -612,6 +737,7 @@ func (e *Engine) expandPartition(input [][]string) ([][]string, error) {
 		}
 	}
 	all := append(append(append([]string{}, e.schedule.Processes.Lease...), e.schedule.Processes.Clients...), e.storage)
+	all = append(all, e.schedule.Processes.Operators...)
 	for _, id := range all {
 		if !used[id] {
 			if rest < 0 {
@@ -630,8 +756,19 @@ func (e *Engine) expandPartition(input [][]string) ([][]string, error) {
 }
 
 // act applies only a validated workload action or one admitted failure cell.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) act(a Action, trigger Ref) error {
+
+	if a.Reconfigure != nil {
+		return e.reconfigure(a, trigger)
+	}
+	if a.Clock != "" {
+		e.clockSeen = true
+		e.resetProgress()
+		e.clocks[a.Clock] += int64(a.ClockStep * float64(e.schedule.Lifetime))
+		e.out.emit(Event{Proc: "env", Event: "Fault", Cell: a.Cell, Clock: a.Clock, ClockStep: a.ClockStep}, trigger)
+		return nil
+	}
 	if a.Request != "" {
 		return e.request(a.Request)
 	}
@@ -641,7 +778,7 @@ func (e *Engine) act(a Action, trigger Ref) error {
 	if a.Read != "" {
 		return e.read(a.Read, a.Token)
 	}
-	v := Event{Proc: "env", Event: "Fault", Cell: a.Cell, Crash: a.Crash, Restart: a.Restart, Heal: a.Heal, Pause: a.Pause, Resume: a.Resume}
+	v := Event{Proc: "env", Event: "Fault", Cell: a.Cell, Crash: a.Crash, Restart: a.Restart, Heal: a.Heal, Pause: a.Pause, Resume: a.Resume, Amnesia: a.Amnesia}
 	if a.Partition != nil {
 		resolved, err := e.expandPartition(a.Partition)
 		if err != nil {
@@ -650,7 +787,7 @@ func (e *Engine) act(a Action, trigger Ref) error {
 		v.Partition = resolved
 	}
 	// L1 selectors were frozen at trigger firing; act also validates direct callers.
-	// derives: F2.1, F2.2, L1, L2
+	// derives: F2.1, F2.2, L1, L2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 	cut, err := e.expandLinks(a.Cut)
 	if err != nil {
 		return err
@@ -674,17 +811,19 @@ func (e *Engine) act(a Action, trigger Ref) error {
 	}
 	if a.Resume != "" {
 		c := e.clients[a.Resume]
-		if !c.up || !c.paused || e.now().Sub(c.pauseTime) <= grantLifetime {
+		if !c.up || !c.paused || e.now().Sub(c.pauseTime) < e.lifetime() {
 			return fmt.Errorf("resume must follow pause longer than lifetime")
 		}
 	}
 	e.out.emit(v, trigger)
+	e.resetProgress()
 	for _, r := range e.requests {
 		r.eligibleSince = time.Time{}
 	}
-	// derives: F1.1 — crash discards volatile state, retaining only the named stores., C2.1, C2.2
+	// derives: F1.1 — crash discards volatile state, retaining only the named stores., C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 	if id := a.Crash; id != "" {
 		e.crashSeen = true
+		e.crashCount++
 		if n := e.nodes[id]; n != nil {
 			if err := n.stop(); err != nil {
 				return err
@@ -697,7 +836,7 @@ func (e *Engine) act(a Action, trigger Ref) error {
 		} else {
 			e.storageUp = false
 			// The F2.x send stage is local volatile work, not an external packet.
-			// derives: C1.3, C2.2, F1.1, F2.1, F2.2
+			// derives: C1.3, C2.2, F1.1, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 			sent := e.wire[:0]
 			for _, m := range e.wire {
 				if !m.pendingSend {
@@ -708,13 +847,44 @@ func (e *Engine) act(a Action, trigger Ref) error {
 		}
 		e.connect()
 	}
-	// derives: F1.1 — restarted clients have no grant; Raft nodes replay durable logs., C2.1, C2.2
+	// derives: F1.1 — restarted clients have no grant; Raft nodes replay durable logs., C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 	if id := a.Restart; id != "" {
 		if n := e.nodes[id]; n != nil {
+			if a.Amnesia {
+				e.amnesiaSeen = true
+				if e.out.inc[id] == math.MaxUint64 {
+					e.overflow(n, "incarnation")
+					return nil
+				}
+				e.out.inc[id]++
+				e.out.seq[id] = 0
+				n.durable = raft.NewMemoryStorage()
+				n.applied = 0
+				n.members = nil
+				n.epoch = 0
+				n.commit = Event{}
+				n.commitRef = Ref{}
+				n.agreements = nil
+				n.received = nil
+				n.lastToken = 0
+				n.issued = nil
+				n.hasGranted = false
+				n.lastGrantAt = 0
+				n.lastTokenRef = Ref{}
+			}
 			if err := n.start(); err != nil {
 				return err
 			}
+			if !a.Amnesia {
+				for _, r := range e.reconfigs {
+					if r.Receiver == id && r.Request.Seq != 0 && r.Generation+1 == n.generation {
+						r.Generation = n.generation
+					}
+				}
+			}
 		} else if c := e.clients[id]; c != nil {
+			e.out.inc[id]++
+			e.out.seq[id] = 0
 			c.up = true
 			c.paused = false
 			c.grants = nil
@@ -728,7 +898,7 @@ func (e *Engine) act(a Action, trigger Ref) error {
 		e.connect()
 	}
 	// Failures accumulate. Never remove messages already sent on an up link.
-	// derives: F1.2, F2.1, F2.2, L1, L2, C1.1, C1.3, C1.4, C2.2
+	// derives: F1.2, F2.1, F2.2, L1, L2, C1.1, C1.3, C1.4, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 	if v.Partition != nil || a.Cut != nil || a.Drop != nil {
 		if e.down == nil {
 			e.down = map[link]bool{}
@@ -745,14 +915,14 @@ func (e *Engine) act(a Action, trigger Ref) error {
 		e.down = map[link]bool{}
 		e.connect()
 	}
-	// derives: F1.3 — client execution and reply receipt stop while grant time continues., C2.1, C2.2
+	// derives: F1.3 — client execution and reply receipt stop while grant time continues., C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 	if a.Pause != "" {
 		e.pauseSeen = true
 		c := e.clients[a.Pause]
 		c.paused = true
 		c.pauseTime = e.now()
 		// A later Grant is the schedule's witness of a complete holder pause.
-		if horizon := c.pauseTime.Add(grantLifetime + time.Millisecond); horizon.After(e.nextGrant) {
+		if horizon := c.pauseTime.Add(e.lifetime() + time.Millisecond); horizon.After(e.nextGrant) {
 			e.nextGrant = horizon
 		}
 	}
@@ -764,7 +934,7 @@ func (e *Engine) act(a Action, trigger Ref) error {
 }
 
 // witnesses certifies only uninterrupted, eligible progress opportunities.
-// derives: C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) witnesses() []ProgressWitness {
 	var result []ProgressWitness
 	now := e.now()
@@ -777,20 +947,20 @@ func (e *Engine) witnesses() []ProgressWitness {
 }
 
 // ghostReadAck breaks only the partition-lost read's client delivery path.
-// derives: C2.2, F1.2, F2.1, F2.2, P17
+// derives: C2.2, F1.2, F2.1, F2.2, P17, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) ghostReadAck(m WireMessage) {
 	c := e.clients[m.client]
 	if e.mutation == "P17" && e.partitionSeen && c.up && !c.paused && c.generation == m.generation {
-		e.out.emit(Event{Proc: m.client, Event: "ReadAck", Answers: &m.attempt, Client: m.client, Key: "k", Token: m.grant.token, Outcome: "served", Value: "fabricated"}, m.attempt)
+		e.out.emit(Event{Proc: m.client, Event: "ReadAck", Answers: &m.attempt, Client: m.client, Key: "k", Token: m.grant.token, Term: m.grant.term, Outcome: "served", Value: "fabricated"}, m.attempt)
 	}
 }
 
 // readDecision snapshots the durable value without changing the accepted-write ledger.
-// derives: C2.1, C2.2, F1.1, F1.2, F2.1, F2.2, F1.3, P13, P14, P15, P16
+// derives: C2.1, C2.2, F1.1, F1.2, F2.1, F2.2, F1.3, P13, P14, P15, P16, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) readDecision(m WireMessage) {
 	if e.mutation == "P16" && e.crashSeen {
 		// Skip serving, then give the client a fabricated served response.
-		// derives: C2.2, F1.1, P16, E2
+		// derives: C2.2, F1.1, P16, E2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 		m.kind = "read-ack"
 		m.decision = m.attempt
 		m.outcome = "served"
@@ -801,7 +971,7 @@ func (e *Engine) readDecision(m WireMessage) {
 	before := e.ledger
 	serve := m.grant.token >= before
 	// Each mutation bypasses only the read fence; the write ledger remains intact.
-	// derives: C2.1, F1.1, F1.2, F2.1, F2.2, F1.3, P13, P14, P15
+	// derives: C2.1, F1.1, F1.2, F2.1, F2.2, F1.3, P13, P14, P15, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 	if e.mutation == "P13" && e.crashSeen || e.mutation == "P14" && e.partitionSeen || e.mutation == "P15" && e.resumeSeen || e.mutation == "P27" && e.partialSeen || e.mutation == "P28" && e.simplexSeen {
 		serve = true
 	}
@@ -811,10 +981,11 @@ func (e *Engine) readDecision(m WireMessage) {
 		outcome = "served"
 		value = e.storageValue
 	}
-	ref := e.out.emit(Event{Proc: e.storage, Event: name, Key: "k", Token: m.grant.token, Term: m.grant.term, HighestBefore: &before, Value: value}, m.attempt)
+	ref := e.out.emit(Event{Proc: e.storage, Event: name, Key: "k", Token: m.grant.token, Term: m.grant.term, HighestBefore: &before, Value: value, NullValue: serve && !e.storagePresent, Inputs: []Input{input("token", m.grant.token), input("ledger", before), input("stored_value", e.storedInput())}}, m.attempt)
 	m.kind = "read-ack"
 	m.decision = ref
 	m.outcome = outcome
 	m.value = value
+	m.nullValue = serve && !e.storagePresent
 	e.queueReply(m)
 }
diff --git a/impl/evidence-x3/report.py b/impl/evidence-x3/report.py
new file mode 100644
index 0000000..d832e34
--- /dev/null
+++ b/impl/evidence-x3/report.py
@@ -0,0 +1,78 @@
+#!/usr/bin/env python3
+"""Retain and score X3 evidence without changing any historical record.
+derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
+"""
+import collections, hashlib, json, pathlib, re, shutil, subprocess
+ROOT=pathlib.Path(__file__).resolve().parents[2]
+IMPL=ROOT/'impl'; OUT=IMPL/'evidence-x3'
+
+def records(log):
+    rows=[]
+    for line in (OUT/'logs'/log).read_text().splitlines():
+        match=re.search(r'^(.*?) schedule=(\S+) seed=(\d+)(?: mutation=(\S+) expected=FAIL_(\S+))?(?: observed=true)? trace=(\S+)',line)
+        if match:rows.append(dict(zip(['verdict','schedule','seed','mutation','expected','trace'],match.groups())))
+    return rows
+
+def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
+def newtext(path,text):
+    with path.open('x') as f:f.write(text)
+
+baseline=records('all-final.txt');mutations=records('mutations-final.txt')
+assert len(baseline)==59*3*10,(len(baseline),'baseline count')
+assert len(mutations)==56*3,(len(mutations),'mutation count')
+cells=collections.defaultdict(list)
+for row in baseline:cells[(row['schedule'],int(row['seed']))].append(row)
+assert len(cells)==177
+cell_lines=['schedule\tseed\tPASS\tFAIL\tUNEXPLAINED\tflaky\tcanonical_variants']
+flaky=0;canonical_misses=0
+for (name,seed),rows in sorted(cells.items()):
+    assert len(rows)==10
+    variants=set()
+    for r in rows:
+        path=IMPL/r['trace']
+        events=[json.loads(l) for l in path.read_text().splitlines()]
+        for event in events:event.pop('run',None)
+        meta=json.loads(path.with_suffix('.meta.json').read_text())
+        variants.add(hashlib.sha256(json.dumps([events,meta],sort_keys=True,separators=(',',':')).encode()).hexdigest())
+    verdicts={r['verdict'] for r in rows};isflaky=len(verdicts)>1
+    flaky+=isflaky;canonical_misses+=len(variants)>1
+    count=collections.Counter(r['verdict'].split()[0] for r in rows)
+    cell_lines.append(f"{name}\t{seed}\t{count['PASS']}\t{count['FAIL']}\t{count['UNEXPLAINED']}\t{str(isflaky).lower()}\t{len(variants)}")
+newtext(OUT/'per-seed.tsv','\n'.join(cell_lines)+'\n')
+mutation_lines=['mutation\tschedule\tseed\texpected\tobserved\tkilled']
+for r in mutations:mutation_lines.append('\t'.join([r['mutation'],r['schedule'],r['seed'],r['expected'],r['verdict'],str(r['verdict']=='FAIL '+r['expected']).lower()]))
+newtext(OUT/'mutation-seeds.tsv','\n'.join(mutation_lines)+'\n')
+# Keep every X3 execution, including adverse intermediate traces and focused runs.
+traces=set((IMPL/'observe').glob('*x3-v1-*.jsonl'))
+traces.update((IMPL/'observe').glob('fixture-membership-*.jsonl'))
+for name in ('P45','P46','P61'):traces.update((IMPL/'observe').glob(name+'-timing-v1-*.jsonl'))
+p=IMPL/'observe/P1-timing-v1-baseline-seed-1-rep-0011.jsonl'
+if p.exists():traces.add(p)
+(OUT/'traces').mkdir(exist_ok=True)
+manifest=['path\tsha256\tbytes']
+for p in sorted(traces):
+    for source in (p,p.with_suffix('.meta.json')):
+        if not source.exists():continue
+        dest=OUT/'traces'/source.name
+        if dest.exists():assert dest.read_bytes()==source.read_bytes()
+        else:shutil.copyfile(source,dest)
+        manifest.append(f"{dest.relative_to(IMPL)}\t{digest(dest)}\t{dest.stat().st_size}")
+newtext(OUT/'manifest.tsv','\n'.join(manifest)+'\n')
+inputs=[ROOT/p for p in ['contract/v3.md','failure-model/v3.md','tests/pairs-v4.md','testbed/schedule-format.md','observe/schema.md','observe/decision_replay.py']]
+inputs+=sorted((ROOT/'testbed/schedules').glob('*.yaml'))
+newtext(OUT/'shared-inputs.tsv','path\tsha256\n'+''.join(f'{p.relative_to(ROOT)}\t{digest(p)}\n' for p in inputs))
+sources=sorted(IMPL.glob('*.go'))+[IMPL/'run.sh',IMPL/'go.mod',IMPL/'go.sum']
+newtext(OUT/'source-sha256.tsv','path\tsha256\n'+''.join(f'{p.relative_to(IMPL)}\t{digest(p)}\n' for p in sources))
+# Evaluate equal-input outcomes across the entire unmutated final matrix.
+command=['python3',str(ROOT/'observe/decision_replay.py')]+[str(IMPL/r['trace']) for r in baseline]
+with (OUT/'logs/decision-replay-final.txt').open('x') as f:result=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT)
+replay_mutations={}
+for pair in ('P43','P44','P45'):
+    with (OUT/f'logs/decision-replay-{pair}.txt').open('x') as f:
+        result_mut=subprocess.run(['python3',str(ROOT/'observe/decision_replay.py')]+[str(IMPL/r['trace']) for r in mutations if r['mutation']==pair],stdout=f,stderr=subprocess.STDOUT)
+    replay_mutations[pair]=result_mut.returncode
+summary={'baseline_runs':len(baseline),'baseline_pass':sum(r['verdict']=='PASS' for r in baseline),'mutation_runs':len(mutations),'mutation_kills':sum(r['verdict']=='FAIL '+r['expected'] for r in mutations),'flaky_cells':flaky,'canonical_misses':canonical_misses,'decision_replay_exit':result.returncode,'clock_mutation_replay_exits':replay_mutations,'retained_traces':len(traces)}
+newtext(OUT/'summary.json',json.dumps(summary,indent=2)+'\n')
+print(json.dumps(summary,indent=2))
+assert result.returncode==0 and all(replay_mutations.values())
+assert summary['baseline_pass']==1770 and summary['mutation_kills']==168 and flaky==0 and canonical_misses==0
diff --git a/impl/links_v2_test.go b/impl/links_v2_test.go
index 9aad0e4..f113ee6 100644
--- a/impl/links_v2_test.go
+++ b/impl/links_v2_test.go
@@ -135,7 +135,7 @@ func TestX2ApplicationSendFate(t *testing.T) {
 	}
 	defer e.close()
 	c := e.clients["c1"]
-	c.grants = []HeldGrant{{token: 7, ref: Ref{"n1", 1}}}
+	c.grants = []HeldGrant{{token: 7, ref: Ref{"n1", 1, 0}}}
 	if err = e.write("c1", "before-cut", ""); err != nil {
 		t.Fatal(err)
 	}
@@ -197,8 +197,8 @@ func TestX2C14LiteralClique(t *testing.T) {
 				}
 			}
 		}
-		events := []Event{{Proc: "env", Seq: 1, Event: "Fault", Cell: "F2.2", Links: links}, {Proc: "c2", Seq: 1, Event: "Request", Client: "c2", Key: "k", Causes: []Ref{{"env", 1}}}}
-		evidence := RunEvidence{Witnesses: []ProgressWitness{{Ref{"c2", 1}, Ref{"env", 1}, 3000}}}
+		events := []Event{{Proc: "env", Seq: 1, Event: "Fault", Cell: "F2.2", Links: links}, {Proc: "c2", Seq: 1, Event: "Request", Client: "c2", Key: "k", Causes: []Ref{{"env", 1, 0}}}}
+		evidence := RunEvidence{Witnesses: []ProgressWitness{{Ref{"c2", 1, 0}, Ref{"env", 1, 0}, 3000}}}
 		g, err := readTrace(writeFixture(t, events))
 		if err != nil {
 			t.Fatal(err)
@@ -208,12 +208,12 @@ func TestX2C14LiteralClique(t *testing.T) {
 		}
 	}
 	// The isolated current grantor is irrelevant: followers form a full clique.
-	events := []Event{{Proc: "env", Seq: 1, Event: "Fault", Cell: "F2.1", Links: [][]string{{"n1", "n2"}, {"n2", "n1"}, {"n1", "n3"}, {"n3", "n1"}}}, {Proc: "c2", Seq: 1, Event: "Request", Client: "c2", Key: "k", Causes: []Ref{{"env", 1}}}}
+	events := []Event{{Proc: "env", Seq: 1, Event: "Fault", Cell: "F2.1", Links: [][]string{{"n1", "n2"}, {"n2", "n1"}, {"n1", "n3"}, {"n3", "n1"}}}, {Proc: "c2", Seq: 1, Event: "Request", Client: "c2", Key: "k", Causes: []Ref{{"env", 1, 0}}}}
 	g, err := readTrace(writeFixture(t, events))
 	if err != nil {
 		t.Fatal(err)
 	}
-	if v := g.checkC14(fixtureSchedule(), RunEvidence{Witnesses: []ProgressWitness{{Ref{"c2", 1}, Ref{"env", 1}, 3000}}}); v.Clause != "C1.4" {
+	if v := g.checkC14(fixtureSchedule(), RunEvidence{Witnesses: []ProgressWitness{{Ref{"c2", 1, 0}, Ref{"env", 1, 0}, 3000}}}); v.Clause != "C1.4" {
 		t.Fatalf("clique excluding grantor ignored: %+v", v)
 	}
 }
@@ -257,7 +257,7 @@ func TestX2StorageCrashLosesOnlyUnsentReplies(t *testing.T) {
 	e.wire = []WireMessage{
 		{kind: "ack", client: "c1", generation: 1, pendingSend: true},
 		{kind: "read-ack", client: "c1", generation: 1, pendingSend: true},
-		{kind: "ack", client: "c1", generation: 1, decision: Ref{"s", 1}},
+		{kind: "ack", client: "c1", generation: 1, decision: Ref{"s", 1, 0}},
 	}
 	if err = e.act(Action{Cell: "F1.1", Crash: "s"}, Ref{}); err != nil {
 		t.Fatal(err)
@@ -282,11 +282,11 @@ func TestX2RuntimeCliqueAndLostGrantStanding(t *testing.T) {
 		t.Fatal(err)
 	}
 	defer out.close()
-	e := &Engine{rng: rand.New(rand.NewSource(1)), schedule: fixtureSchedule(), storage: "s", storageUp: true, clients: map[string]*Client{"c2": {id: "c2", up: true, generation: 1}}, nodes: map[string]*LeaseNode{}, down: map[link]bool{}, out: out}
+	e := &Engine{rng: rand.New(rand.NewSource(1)), schedule: fixtureSchedule(), storage: "s", storageUp: true, members: initialMembers(fixtureSchedule()), clients: map[string]*Client{"c2": {id: "c2", up: true, generation: 1}}, nodes: map[string]*LeaseNode{}, down: map[link]bool{}, out: out}
 	for _, id := range e.schedule.Processes.Lease {
-		e.nodes[id] = &LeaseNode{peer: &raft.RawNode{}, generation: 1}
+		e.nodes[id] = &LeaseNode{peer: &raft.RawNode{}, generation: 1, members: initialMembers(e.schedule)}
 	}
-	r := &RequestState{client: "c2", generation: 1, ref: Ref{"c2", 1}}
+	r := &RequestState{client: "c2", generation: 1, ref: Ref{"c2", 1, 0}}
 	if !e.eligible(r) {
 		t.Fatal("full clique not eligible")
 	}
@@ -299,8 +299,8 @@ func TestX2RuntimeCliqueAndLostGrantStanding(t *testing.T) {
 		t.Fatal("runtime ignored followers' clique")
 	}
 	e.down = map[link]bool{{"n1", "c2"}: true}
-	e.finishAllocation(completedAllocation{request: r, node: "n1", generation: 1, allocation: Allocation{7, 2}})
-	if r.done || len(e.clients["c2"].grants) > 0 || len(out.events) != 1 || out.events[0].Event != "Grant" {
+	e.finishAllocation(completedAllocation{request: r, node: "n1", generation: 1, allocation: fixtureAllocation(e, "n1", 7, 2)})
+	if r.done || len(e.clients["c2"].grants) > 0 || out.events[len(out.events)-1].Event != "Grant" {
 		t.Fatal("issuance/receipt were conflated")
 	}
 	// Break relaying just for the lost direct send; then restore the normal path.
@@ -312,7 +312,7 @@ func TestX2RuntimeCliqueAndLostGrantStanding(t *testing.T) {
 	}
 	e.mutation = ""
 	e.down = nil
-	e.finishAllocation(completedAllocation{request: r, node: "n2", generation: 1, allocation: Allocation{8, 2}})
+	e.finishAllocation(completedAllocation{request: r, node: "n2", generation: 1, allocation: fixtureAllocation(e, "n2", 8, 2)})
 	if r.done {
 		t.Fatal("new issuance completed before receipt")
 	}
diff --git a/impl/main.go b/impl/main.go
index 71ac558..f945c88 100644
--- a/impl/main.go
+++ b/impl/main.go
@@ -1,4 +1,4 @@
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 package main
 
 import (
@@ -11,17 +11,18 @@ import (
 )
 
 // Options deliberately permits flags before or after the schedule basename.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type Options struct {
 	schedule, mutation, check, evidence string
 	all, mutations                      bool
 	seeds                               int
+	reps                                int
 }
 
 // parseOptions rejects contradictory modes rather than silently ignoring them.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func parseOptions(args []string) (Options, error) {
-	o := Options{seeds: 3}
+	o := Options{seeds: 3, reps: 1}
 	for i := 0; i < len(args); i++ {
 		a := args[i]
 		switch a {
@@ -29,13 +30,19 @@ func parseOptions(args []string) (Options, error) {
 			o.all = true
 		case "--mutations":
 			o.mutations = true
-		case "--seeds", "--mutation", "--check", "--evidence":
+		case "--reps", "--seeds", "--mutation", "--check", "--evidence":
 			if i+1 >= len(args) {
 				return o, fmt.Errorf("missing value for %s", a)
 			}
 			i++
 			v := args[i]
 			switch a {
+			case "--reps":
+				n, err := strconv.Atoi(v)
+				if err != nil || n < 1 || n > 1000 {
+					return o, fmt.Errorf("reps must be 1..1000")
+				}
+				o.reps = n
 			case "--seeds":
 				n, err := strconv.Atoi(v)
 				if err != nil || n < 1 || n > 1000 {
@@ -70,7 +77,7 @@ func parseOptions(args []string) (Options, error) {
 		return o, fmt.Errorf("use <schedule>, --all, or --mutations")
 	}
 	if o.mutation != "" && (o.schedule == "" || expectedClause(o.mutation) == "") {
-		return o, fmt.Errorf("--mutation requires one schedule and P1..P30 or R1/R2")
+		return o, fmt.Errorf("--mutation requires one schedule and registered pair or R1/R2")
 	}
 	if o.check != "" && (o.schedule == "" || o.mutation != "") {
 		return o, fmt.Errorf("--check requires one schedule and no mutation")
@@ -82,9 +89,25 @@ func parseOptions(args []string) (Options, error) {
 }
 
 // expectedClause implements the precommitted mutation scoring table.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func expectedClause(pair string) string {
 	switch pair {
+	case "P31", "P32", "P33":
+		return "C3.1"
+	case "P40", "P41", "P42":
+		return "C3.4"
+	case "P43", "P44", "P45":
+		return "C3.5"
+	case "P46", "P47", "P48":
+		return "C1.1"
+	case "P49", "P50", "P51":
+		return "C1.2"
+	case "P52", "P53", "P54":
+		return "C1.4"
+	case "P58", "P59", "P60":
+		return "C3.7"
+	case "P61", "P62", "P63":
+		return "C3.8"
 	case "P1", "P2", "P3", "P19", "P20":
 		return "C1.1"
 	case "P4", "P5", "P6", "P21", "P22":
@@ -102,7 +125,7 @@ func expectedClause(pair string) string {
 }
 
 // runOne writes a fresh trace and scores only its decoded observable evidence.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, E2, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, E2, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func runOne(s Schedule, seed int64, mutation string) (Verdict, string) {
 	mode := "baseline"
 	if mutation != "" {
@@ -115,7 +138,7 @@ func runOne(s Schedule, seed int64, mutation string) (Verdict, string) {
 	var emitter *Emitter
 	var err error
 	for label := 1; ; label++ {
-		run = fmt.Sprintf("%s-timing-v1-%s-seed-%d-rep-%04d", s.Name, mode, seed, label)
+		run = fmt.Sprintf("%s-x3-v1-%s-seed-%d-rep-%04d", s.Name, mode, seed, label)
 		path = filepath.Join("observe", run+".jsonl")
 		emitter, err = newEmitter(path, run)
 		if os.IsExist(err) {
@@ -147,7 +170,7 @@ func runOne(s Schedule, seed int64, mutation string) (Verdict, string) {
 }
 
 // printResult always begins with the shared result vocabulary.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func printResult(v Verdict, schedule string, seed int, mutation, path string) {
 	status := "PASS"
 	if v.Clause != "" {
@@ -172,7 +195,7 @@ func printResult(v Verdict, schedule string, seed int, mutation, path string) {
 }
 
 // execute runs every requested seed, even if an earlier seed fails.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func execute(args []string) int {
 	o, err := parseOptions(args)
 	if err != nil {
@@ -221,11 +244,18 @@ func execute(args []string) int {
 	}
 	var schedules []string
 	if o.all || o.mutations {
-		for i := 1; i <= 30; i++ {
-			schedules = append(schedules, fmt.Sprintf("P%d", i))
+		entries, err := os.ReadDir("../testbed/schedules")
+		if err != nil {
+			fmt.Println("UNEXPLAINED", err)
+			return 2
 		}
-		if o.all {
-			schedules = append(schedules, "H7", "H8", "H9", "H10", "false-suspicion-v1")
+		for _, entry := range entries {
+			if strings.HasSuffix(entry.Name(), ".yaml") {
+				name := strings.TrimSuffix(entry.Name(), ".yaml")
+				if o.all || expectedClause(name) != "" {
+					schedules = append(schedules, name)
+				}
+			}
 		}
 	} else {
 		schedules = []string{o.schedule}
@@ -252,15 +282,17 @@ func execute(args []string) int {
 		}
 		allKilled := true
 		for seed := 1; seed <= o.seeds; seed++ {
-			v, path := runOne(s, int64(seed), mutation)
-			printResult(v, s.Name, seed, mutation, path)
-			if mutation != "" {
-				if v.Clause != expectedClause(mutation) {
+			for rep := 1; rep <= o.reps; rep++ {
+				v, path := runOne(s, int64(seed), mutation)
+				printResult(v, s.Name, seed, mutation, path)
+				if mutation != "" {
+					if v.Clause != expectedClause(mutation) {
+						exit = 1
+						allKilled = false
+					}
+				} else if v.Clause != "" || v.Reason != "" {
 					exit = 1
-					allKilled = false
 				}
-			} else if v.Clause != "" || v.Reason != "" {
-				exit = 1
 			}
 		}
 		if mutation != "" && allKilled {
@@ -268,17 +300,17 @@ func execute(args []string) int {
 		}
 	}
 	if o.mutations {
-		fmt.Printf("Mutation kills: %d/32 across %d seed(s)\n", killed, o.seeds)
+		fmt.Printf("Mutation kills: %d/%d across %d seed(s), %d repetition(s)\n", killed, len(schedules), o.seeds, o.reps)
 	}
 	return exit
 }
 
 // main returns a nonzero status for any unexpected or unexplained result.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func main() { os.Exit(execute(os.Args[1:])) }
 
 // ownEvidencePath confines offline reads, including symlinks, to this artifact.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func ownEvidencePath(path string) error {
 	root, err := filepath.Abs(".")
 	if err != nil {
diff --git a/impl/membership_v3.go b/impl/membership_v3.go
new file mode 100644
index 0000000..f037cdf
--- /dev/null
+++ b/impl/membership_v3.go
@@ -0,0 +1,591 @@
+// derives: C1.1, C1.4, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
+package main
+
+import (
+	"encoding/json"
+	"fmt"
+	raft "go.etcd.io/raft/v3"
+	pb "go.etcd.io/raft/v3/raftpb"
+	"math"
+	"sort"
+	"time"
+)
+
+// Proposal is the complete contract proposal, carried in the replicated log.
+// derives: C1.1, C3.1, C3.5, C3.7, C3.8, F3.1, F3.3
+type Proposal struct {
+	Kind        string   `json:"kind"`
+	Client      string   `json:"client,omitempty"`
+	Token       uint64   `json:"token,omitempty"`
+	Lifetime    int64    `json:"lifetime,omitempty"`
+	ConfigEpoch uint64   `json:"config_epoch,omitempty"`
+	Epoch       uint64   `json:"epoch,omitempty"`
+	Members     []string `json:"members,omitempty"`
+	RequestID   string   `json:"request_id,omitempty"`
+}
+
+// Agreement metadata accompanies the actual Raft append acknowledgement.
+// derives: C3.5, C3.7, C3.8, F3.1, F3.3
+type Agreement struct {
+	Proposal Proposal
+	Ref      Ref
+	Index    uint64
+}
+
+// Reconfiguration has receiver-local pending state and independent message sends.
+// derives: C3.1, C3.4, C3.8, F3.1, F3.3
+type Reconfiguration struct {
+	ID, Operator, Receiver                string
+	Members                               []string
+	Send, Request, Outcome                Ref
+	Reason                                string
+	Base                                  uint64
+	Proposed, Joint, Leaving, Done, Acked bool
+	Decider                               string
+	Due                                   time.Time
+	Generation                            uint64
+	EligibleSince                         time.Time
+}
+
+// ConfigPacket carries learned commit evidence and is gated at send time.
+// derives: C3.1, C3.4, C3.8, F3.1, F3.3
+type ConfigPacket struct {
+	To         string
+	Generation uint64
+	Event      Event
+	Ref        Ref
+	Due        time.Time
+}
+
+// derives: C3.5, C3.7, C3.8, F3.2
+func input(name string, value any) Input { return Input{Name: name, Value: value} }
+
+// derives: C3.5, C3.7, C3.8, F3.3
+func reference(name string, value any, r Ref) Input {
+	if r.Seq == 0 {
+		return input(name, value)
+	}
+	return Input{Name: name, Value: value, Ref: &r}
+}
+
+// derives: C1.1, C3.5, C3.7, C3.8, F3.1
+func proposalKey(p Proposal) string { b, _ := json.Marshal(p); return string(b) }
+
+// derives: C1.1, C3.5, C3.7, F3.2
+func (e *Engine) lifetime() time.Duration {
+	if e.schedule.Lifetime == 0 {
+		return grantLifetime
+	}
+	return time.Duration(e.schedule.Lifetime) * grantLifetime
+}
+
+// derives: C3.1, C3.7, C3.8, F3.1
+func initialMembers(s Schedule) []string {
+	if s.Processes.Config != nil {
+		return s.Processes.Config
+	}
+	return s.Processes.Lease
+}
+
+// derives: C3.1, C3.7, C3.8, F3.1
+func contains(xs []string, x string) bool {
+	for _, v := range xs {
+		if v == x {
+			return true
+		}
+	}
+	return false
+}
+
+// derives: C3.7, C3.8, F3.3
+func (e *Engine) nodeEligible(n string, epoch uint64) bool {
+	inc := e.out.inc[n]
+	if inc == 0 {
+		return true
+	}
+	admitted, ok := e.readmitted[n]
+	return ok && admitted == inc && e.readmitEpoch[n] <= epoch
+}
+
+// derives: C3.1, C3.4, F3.1
+func (e *Engine) nonMember() (string, error) {
+	ids := append([]string{}, e.schedule.Processes.Lease...)
+	sort.Slice(ids, func(i, j int) bool { a, _ := leaseNumber(ids[i]); b, _ := leaseNumber(ids[j]); return a < b })
+	for _, id := range ids {
+		if !contains(e.members, id) {
+			return id, nil
+		}
+	}
+	return "", fmt.Errorf("no non-member")
+}
+
+// decodeEntry distinguishes entering joint state from the proposal to leave it.
+// derives: C3.1, C3.7, C3.8, F3.1
+func decodeEntry(entry pb.Entry) (Proposal, bool) {
+	var p Proposal
+	if entry.Type == pb.EntryNormal {
+		if len(entry.Data) == 0 {
+			return p, false
+		}
+		if json.Unmarshal(entry.Data, &p) != nil {
+			return p, false
+		}
+		return p, p.Kind == "grant"
+	}
+	if entry.Type == pb.EntryConfChangeV2 {
+		var cc pb.ConfChangeV2
+		if cc.Unmarshal(entry.Data) != nil || len(cc.Changes) != 0 {
+			return p, false
+		}
+		if json.Unmarshal(cc.Context, &p) != nil {
+			return p, false
+		}
+		return p, p.Kind == "config"
+	}
+	return p, false
+}
+
+// persistedAgreement runs only after durable Append, before any response send.
+// derives: C1.1, C3.5, C3.7, C3.8, F3.1, F3.3
+func (e *Engine) persistedAgreement(n *LeaseNode, entry pb.Entry) {
+	p, ok := decodeEntry(entry)
+	if !ok {
+		return
+	}
+	if n.agreements == nil {
+		n.agreements = map[uint64]Agreement{}
+	}
+	if a, ok := n.agreements[entry.Index]; ok && proposalKey(a.Proposal) == proposalKey(p) {
+		return
+	}
+	ref := e.out.emit(Event{Proc: n.id, Event: "Agree", Node: n.id, Incarnation: e.out.inc[n.id], Proposal: p})
+	if p.Kind == "grant" && p.Token > n.lastToken {
+		n.lastToken = p.Token
+		n.lastTokenRef = ref
+	}
+	a := Agreement{p, ref, entry.Index}
+	n.agreements[entry.Index] = a
+	if n.peer.BasicStatus().RaftState == raft.StateLeader {
+		e.receiveAgreement(n, a)
+	}
+}
+
+// receiveAgreement records only identity-carrying acknowledgements actually received.
+// derives: C3.5, C3.7, C3.8, F3.1, F3.3
+func (e *Engine) receiveAgreement(n *LeaseNode, a Agreement) {
+	if n.received == nil {
+		n.received = map[string][]Ref{}
+	}
+	key := proposalKey(a.Proposal)
+	for _, r := range n.received[key] {
+		v := e.out.lookup(r)
+		if v.Node == a.Ref.Proc && v.NodeInc == a.Ref.Inc {
+			return
+		}
+	}
+	counted := []uint64{}
+	if a.Ref.Inc == 0 || e.readmitted[a.Ref.Proc] == a.Ref.Inc && e.readmitEpoch[a.Ref.Proc] <= n.epoch {
+		if a.Proposal.Kind == "grant" {
+			if contains(n.members, a.Ref.Proc) {
+				counted = append(counted, n.epoch)
+			}
+		} else {
+			if contains(n.members, a.Ref.Proc) {
+				counted = append(counted, n.epoch)
+			}
+			if contains(a.Proposal.Members, a.Ref.Proc) {
+				counted = append(counted, a.Proposal.Epoch)
+			}
+		}
+	}
+	r := e.out.emit(Event{Proc: n.id, Event: "Agreed", Node: a.Ref.Proc, NodeInc: a.Ref.Inc, Proposal: a.Proposal, Counted: counted}, a.Ref)
+	n.received[key] = append(n.received[key], r)
+}
+
+// derives: C3.5, C3.7, C3.8, F3.3
+func (e *Emitter) lookup(r Ref) Event {
+	for i := len(e.events) - 1; i >= 0; i-- {
+		v := e.events[i]
+		if v.Proc == r.Proc && v.Seq == r.Seq && v.Inc == r.Inc {
+			return v
+		}
+	}
+	return Event{}
+}
+
+// evidenceInputs selects received protocol evidence deterministically.
+// derives: C3.5, C3.7, C3.8, F3.1, F3.3
+func (e *Engine) evidenceInputs(n *LeaseNode, p Proposal) []Input {
+	refs := append([]Ref{}, n.received[proposalKey(p)]...)
+	sort.Slice(refs, func(i, j int) bool {
+		a, b := e.out.lookup(refs[i]), e.out.lookup(refs[j])
+		if a.Node != b.Node {
+			return a.Node < b.Node
+		}
+		return a.NodeInc < b.NodeInc
+	})
+	ins := []Input{}
+	for _, r := range refs {
+		ins = append(ins, reference("agreed", nil, r))
+	}
+	return ins
+}
+
+// majorityEvidence counts distinct eligible nodes, including the whole denominator.
+// derives: C3.7, C3.8, F3.3
+func (e *Engine) majorityEvidence(n *LeaseNode, p Proposal, members []string, epoch uint64) bool {
+	got := map[string]bool{}
+	for _, r := range n.received[proposalKey(p)] {
+		v := e.out.lookup(r)
+		if contains(members, v.Node) && (v.NodeInc == 0 || e.readmitted[v.Node] == v.NodeInc && e.readmitEpoch[v.Node] <= epoch) {
+			got[v.Node] = true
+		}
+	}
+	return len(got)*2 > len(members)
+}
+
+// reconfigure emits an operator send; receipt occurs later through a real link.
+// derives: C3.4, C3.8, F3.1
+func (e *Engine) reconfigure(a Action, trigger Ref) error {
+	op := a.Operator
+	if op == "" {
+		op = "op"
+	}
+	members := append([]string{}, a.Reconfigure...)
+	sort.Strings(members)
+	r := e.out.emit(Event{Proc: op, Event: "ReconfigSend", Operator: op, To: a.To, RequestID: a.ID, Members: members}, trigger)
+	if e.canSend(op, a.To) {
+		e.reconfigs = append(e.reconfigs, &Reconfiguration{ID: a.ID, Operator: op, Receiver: a.To, Members: members, Send: r, Due: e.now().Add(e.jitter()), Generation: e.nodes[a.To].generation})
+	}
+	return nil
+}
+
+// refuses are receiver decisions, with the precise pending/commit input.
+// derives: C3.4, C3.5, F3.1, F3.3
+func (e *Engine) refuse(r *Reconfiguration, reason string, cause Ref) {
+	ins := []Input{input("request_id", r.ID), input("requested_members", r.Members)}
+	if reason == "busy" {
+		ins = append(ins, reference("pending", nil, cause))
+	}
+	if reason == "superseded" {
+		ins = append(ins, reference("commit", nil, cause))
+	}
+	r.Outcome = e.out.emit(Event{Proc: r.Receiver, Event: "ReconfigRefused", RequestID: r.ID, Reason: reason, Epoch: e.epoch, Inputs: ins}, r.Request, cause)
+	r.Reason = reason
+	r.Done = true
+}
+
+// reconfigActive includes requests and outcome acknowledgements in flight.
+// derives: C3.4, C3.8, F3.1, F3.3
+func (e *Engine) reconfigActive() bool {
+	for _, r := range e.reconfigs {
+		if !r.Acked && e.alive(r.Receiver) && r.Generation == e.nodes[r.Receiver].generation {
+			return true
+		}
+	}
+	return len(e.configWire) > 0
+}
+
+// pumpReconfiguration forwards receiver requests to Raft leaders and explicitly
+// leaves joint consensus. Neither a clock step nor an amnesic copy can decide it.
+// derives: C3.1, C3.4, C3.5, C3.8, F3.1, F3.2, F3.3
+func (e *Engine) pumpReconfiguration() {
+	now := e.now()
+	packets := e.configWire
+	e.configWire = nil
+	for _, m := range packets {
+		if now.Before(m.Due) {
+			e.configWire = append(e.configWire, m)
+			continue
+		}
+		n := e.nodes[m.To]
+		if n.peer == nil || n.generation != m.Generation {
+			continue
+		}
+		e.learnCommit(n, m.Event, m.Ref)
+	}
+	for _, r := range e.reconfigs {
+		n := e.nodes[r.Receiver]
+		if n.peer == nil || r.Generation != n.generation {
+			continue
+		}
+		if r.Request.Seq == 0 {
+			if now.Before(r.Due) {
+				continue
+			}
+			r.Request = e.out.emit(Event{Proc: r.Receiver, Event: "ReconfigRequest", Operator: r.Operator, RequestID: r.ID, Members: r.Members}, r.Send)
+			r.Base = n.epoch
+			valid := len(r.Members) > 0
+			seen := map[string]bool{}
+			for _, id := range r.Members {
+				if e.nodes[id] == nil || seen[id] {
+					valid = false
+				}
+				seen[id] = true
+			}
+			if !valid {
+				e.refuse(r, "invalid", Ref{})
+				continue
+			}
+			busy := Ref{}
+			for _, earlier := range e.reconfigs {
+				if earlier == r {
+					break
+				}
+				if earlier.Receiver == r.Receiver && earlier.Request.Seq != 0 && !earlier.Done && earlier.Generation == n.generation {
+					busy = earlier.Request
+					break
+				}
+			}
+			if busy.Seq != 0 {
+				e.refuse(r, "busy", busy)
+				continue
+			}
+			r.Due = now.Add(4 * time.Millisecond)
+			continue
+		}
+		if r.Done {
+			if !r.Acked && e.canSend(r.Receiver, r.Operator) {
+				if now.Before(r.Due) {
+					continue
+				}
+				outcome := "committed"
+				if r.Reason != "" {
+					outcome = "refused"
+				}
+				e.out.emit(Event{Proc: r.Operator, Event: "ReconfigAck", Operator: r.Operator, RequestID: r.ID, Outcome: outcome, Epoch: e.out.lookup(r.Outcome).Epoch}, r.Outcome)
+				r.Acked = true
+			}
+			continue
+		}
+		if n.epoch > r.Base {
+			if n.commit.RequestID == r.ID {
+				r.Outcome = n.commitRef
+				r.Done = true
+				r.Due = now.Add(e.jitter())
+			} else {
+				e.refuse(r, "superseded", n.commitRef)
+			}
+			continue
+		}
+		if now.Before(r.Due) || e.inflight {
+			continue
+		}
+		if e.mutation == "P40" || e.mutation == "P41" || e.mutation == "P42" {
+			continue
+		}
+		if e.activeConfig != nil && e.activeConfig != r {
+			continue
+		}
+		for _, id := range e.schedule.Processes.Lease {
+			leader := e.nodes[id]
+			if leader.peer == nil || leader.peer.BasicStatus().RaftState != raft.StateLeader || !e.reconfigRoute(r.Receiver, id) {
+				continue
+			}
+			if !r.Proposed {
+				if leader.epoch == math.MaxUint64 {
+					e.overflow(leader, "epoch")
+					continue
+				}
+				p := Proposal{Kind: "config", Epoch: leader.epoch + 1, Members: r.Members, RequestID: r.ID}
+				data, _ := json.Marshal(p)
+				changes := []pb.ConfChangeSingle{}
+				for _, member := range e.schedule.Processes.Lease {
+					old, new := contains(leader.members, member), contains(r.Members, member)
+					if new && !old {
+						changes = append(changes, pb.ConfChangeSingle{Type: pb.ConfChangeAddNode, NodeID: e.network.ids[member]})
+					}
+					if old && !new {
+						changes = append(changes, pb.ConfChangeSingle{Type: pb.ConfChangeRemoveNode, NodeID: e.network.ids[member]})
+					}
+				}
+				// A same-set re-admission still enters joint consensus explicitly.
+				if len(changes) == 0 {
+					changes = append(changes, pb.ConfChangeSingle{Type: pb.ConfChangeAddNode, NodeID: e.network.ids[r.Members[0]]})
+				}
+				if err := leader.peer.ProposeConfChange(pb.ConfChangeV2{Transition: pb.ConfChangeTransitionJointExplicit, Changes: changes, Context: data}); err == nil {
+					r.Proposed = true
+					r.Decider = id
+					e.activeConfig = r
+				}
+			} else if r.Joint && !r.Leaving {
+				p := Proposal{Kind: "config", Epoch: leader.epoch + 1, Members: r.Members, RequestID: r.ID}
+				data, _ := json.Marshal(p)
+				if err := leader.peer.ProposeConfChange(pb.ConfChangeV2{Context: data}); err == nil {
+					r.Leaving = true
+					r.Decider = id
+				}
+			}
+			break
+		}
+	}
+}
+
+// applyConfiguration is invoked only for committed ConfChangeV2 library entries.
+// derives: C3.1, C3.5, C3.8, F3.1, F3.3
+func (e *Engine) applyConfiguration(n *LeaseNode, entry pb.Entry) {
+	var cc pb.ConfChangeV2
+	if err := cc.Unmarshal(entry.Data); err != nil {
+		e.network.problem = err
+		return
+	}
+	n.conf = *n.peer.ApplyConfChange(cc)
+	var p Proposal
+	if json.Unmarshal(cc.Context, &p) != nil {
+		return
+	}
+	if len(cc.Changes) > 0 {
+		for _, r := range e.reconfigs {
+			if r.ID == p.RequestID {
+				r.Joint = true
+			}
+		}
+		return
+	}
+	if e.epoch >= p.Epoch {
+		return
+	}
+	if e.activeConfig == nil || e.activeConfig.Decider != n.id {
+		return
+	}
+	if !e.majorityEvidence(n, p, n.members, n.epoch) || !e.majorityEvidence(n, p, p.Members, p.Epoch) {
+		e.pendingCommit = &pendingConfiguration{n.id, p}
+		return
+	}
+	e.decideConfiguration(n, p)
+}
+
+// derives: C3.1, C3.8, F3.1
+type pendingConfiguration struct {
+	Node     string
+	Proposal Proposal
+}
+
+// decideConfiguration publishes the contract epoch after joint-majority commit.
+// derives: C3.1, C3.5, C3.8, F3.1, F3.3
+func (e *Engine) decideConfiguration(n *LeaseNode, p Proposal) {
+	ins := e.evidenceInputs(n, p)
+	ins = append(ins, input("old_members", n.members), input("old_epoch", n.epoch), input("request_id", p.RequestID), input("requested_members", p.Members))
+	readmits := [][]any{}
+	for _, r := range n.received[proposalKey(p)] {
+		a := e.out.lookup(r)
+		if a.NodeInc > 0 && contains(p.Members, a.Node) {
+			readmits = append(readmits, []any{a.Node, a.NodeInc})
+		}
+	}
+	if e.mutation == "P61" || e.mutation == "P62" || e.mutation == "P63" {
+		ins = ins[len(ins)-4:]
+	}
+	v := Event{Proc: n.id, Event: "ConfigCommitted", Epoch: p.Epoch, Members: p.Members, RequestID: p.RequestID, Readmits: readmits, Decided: true, Inputs: ins}
+	ref := e.out.emit(v, n.commitRef)
+	e.epoch = p.Epoch
+	e.members = append([]string{}, p.Members...)
+	for _, a := range readmits {
+		e.readmitted[a[0].(string)] = a[1].(uint64)
+		e.readmitEpoch[a[0].(string)] = p.Epoch
+	}
+	n.epoch = p.Epoch
+	n.members = append([]string{}, p.Members...)
+	n.commit = v
+	n.commitRef = ref
+	e.activeConfig = nil
+	e.pendingCommit = nil
+	if e.mutation == "P31" || e.mutation == "P32" || e.mutation == "P33" {
+		e.out.emit(v, ref)
+	}
+	for _, id := range e.schedule.Processes.Lease {
+		if id != n.id && e.canSend(n.id, id) {
+			e.configWire = append(e.configWire, ConfigPacket{id, e.nodes[id].generation, v, ref, e.now().Add(e.jitter())})
+		}
+	}
+}
+
+// learnCommit keeps receiver-local configurations distinct from global observation.
+// derives: C3.1, C3.4, C3.7, C3.8, F3.1, F3.3
+func (e *Engine) learnCommit(n *LeaseNode, v Event, ref Ref) {
+	if v.Epoch <= n.epoch {
+		return
+	}
+	v.Proc = n.id
+	v.Decided = false
+	v.Inputs = nil
+	n.commitRef = e.out.emit(v, ref)
+	n.commit = v
+	n.members = append([]string{}, v.Members...)
+	n.epoch = v.Epoch
+}
+
+// grantLogCommand carries the full proposal and request correlation separately.
+// derives: C1.1, C3.5, C3.7, F3.1, F3.3
+type grantLogCommand struct {
+	Proposal
+	ID uint64 `json:"request_correlation"`
+}
+
+// snapshotState is Raft FSM state transferred through the protocol snapshot.
+// derives: C1.1, C3.1, C3.7, C3.8, F3.3
+type snapshotState struct {
+	Commit    Event
+	LastToken uint64
+}
+
+// derives: C1.1, C3.5, C3.7, F3.2
+func (e *Engine) grantCommand(n *LeaseNode, r *RequestState) []byte {
+	last, _ := n.durable.LastIndex()
+	p := Proposal{Kind: "grant", Client: r.client, Token: last + 1, Lifetime: e.lifetimeTicks(), ConfigEpoch: n.epoch}
+	b, _ := json.Marshal(grantLogCommand{p, e.proposalID})
+	return b
+}
+
+// derives: C1.2, C2.1, C3.5, F3.1
+func (e *Engine) storedInput() any {
+	if !e.storagePresent {
+		return nil
+	}
+	return e.storageValue
+}
+
+// derives: C1.4, C3.4, C3.7, C3.8, F3.1, F3.3
+func bitCount(x int) int {
+	n := 0
+	for x > 0 {
+		n += x & 1
+		x >>= 1
+	}
+	return n
+}
+
+// reconfigRoute forwards over available lease-node links in stable process order.
+// derives: C3.4, C3.8, F3.1, F2.1, F2.2
+func (e *Engine) reconfigRoute(from, to string) bool {
+	queue := []string{from}
+	seen := map[string]bool{from: true}
+	for len(queue) > 0 {
+		current := queue[0]
+		queue = queue[1:]
+		if current == to {
+			return true
+		}
+		for _, id := range e.schedule.Processes.Lease {
+			if !seen[id] && e.connected(current, id) {
+				seen[id] = true
+				queue = append(queue, id)
+			}
+		}
+	}
+	return false
+}
+
+// The deployment tick contains 40 deterministic transport/CPU substeps.
+// derives: C1.1, C3.5, F1.3, F3.2
+func (e *Engine) localClock(id string) int64 {
+	return e.now().UnixMilli()/grantLifetime.Milliseconds() + e.clocks[id]
+}
+
+// derives: C1.1, C3.5, F1.3, F3.2
+func (e *Engine) lifetimeTicks() int64 {
+	if e.schedule.Lifetime == 0 {
+		return 1
+	}
+	return e.schedule.Lifetime
+}
diff --git a/impl/membership_v3_test.go b/impl/membership_v3_test.go
new file mode 100644
index 0000000..993e3a6
--- /dev/null
+++ b/impl/membership_v3_test.go
@@ -0,0 +1,141 @@
+// derives: C1.1, C1.4, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
+package main
+
+import (
+	"encoding/json"
+	"path/filepath"
+	"testing"
+)
+
+// fixtureAllocation supplies explicit synthetic quorum evidence to isolated
+// reply-routing tests. Paired executions obtain evidence from persisted entries.
+// derives: C1.4, C3.7, F1.1, F2.1, F2.2
+func fixtureAllocation(e *Engine, node string, token, term uint64) Allocation {
+	n := e.nodes[node]
+	p := Proposal{Kind: "grant", Client: "c2", Token: token, Lifetime: e.lifetimeTicks(), ConfigEpoch: n.epoch}
+	for _, id := range n.members {
+		ref := e.out.emit(Event{Proc: id, Event: "Agree", Node: id, Proposal: p})
+		e.receiveAgreement(n, Agreement{p, ref, token})
+	}
+	return Allocation{Token: token, Term: term, Proposal: p}
+}
+
+// TestX3RecoveryEvidence checks actual protocol traces, including a renamed
+// disjoint replacement and both sides of amnesic eligibility.
+// derives: C1.1, C3.1, C3.5, C3.7, C3.8, F3.1, F3.3
+func TestX3RecoveryEvidence(t *testing.T) {
+	for _, name := range []string{"P45", "P46", "P60", "P63"} {
+		t.Run(name, func(t *testing.T) {
+			s, err := loadSchedule(name)
+			if err != nil {
+				t.Fatal(err)
+			}
+			s.Name = "fixture-membership-" + name
+			verdict, path := runOne(s, 1, "")
+			if verdict != (Verdict{}) {
+				t.Fatalf("%+v trace=%s", verdict, path)
+			}
+			g, err := readTrace(path)
+			if err != nil {
+				t.Fatal(err)
+			}
+			sawInc, sawReadmit := false, false
+			for _, v := range g.ordered {
+				if v.Proc == "n2" && v.Inc == 1 {
+					sawInc = true
+					if v.Event == "ConfigCommitted" && v.Epoch == 0 {
+						t.Fatal("amnesic node fabricated epoch 0")
+					}
+				}
+				if name == "P60" && v.Event == "Agreed" && v.Node == "n2" && v.NodeInc == 1 && len(v.Counted) > 0 {
+					t.Fatal("unreadmitted incarnation counted")
+				}
+				if v.Event == "ConfigCommitted" && v.Decided {
+					for _, r := range v.Readmits {
+						if r[0] == "n2" && r[1] == float64(1) {
+							sawReadmit = true
+						}
+					}
+				}
+			}
+			if name == "P45" && (!sawInc || !sawReadmit) {
+				t.Fatal("re-admission evidence absent")
+			}
+		})
+	}
+}
+
+// TestX3OverflowAndIdentity prevents wrap and distinguishes ordinary recovery.
+// derives: C1.1, C3.1, C3.7, F1.1, F3.3
+func TestX3OverflowAndIdentity(t *testing.T) {
+	out, err := newEmitter(filepath.Join(t.TempDir(), "identity.jsonl"), "identity")
+	if err != nil {
+		t.Fatal(err)
+	}
+	defer out.close()
+	e, err := newEngine(fixtureSchedule(), out, 1, "")
+	if err != nil {
+		t.Fatal(err)
+	}
+	defer e.close()
+	n := e.nodes["n2"]
+	before := out.seq[n.id]
+	inc := out.inc[n.id]
+	if err = n.stop(); err != nil {
+		t.Fatal(err)
+	}
+	if err = n.start(); err != nil {
+		t.Fatal(err)
+	}
+	r := out.emit(Event{Proc: n.id, Event: "Agree", Node: n.id, Proposal: Proposal{Kind: "grant", Token: 99}})
+	if r.Inc != inc || r.Seq != before+1 {
+		t.Fatal("ordinary restart reused or changed identity")
+	}
+	e.overflow(n, "token")
+	if n.peer != nil {
+		t.Fatal("overflow left issuer running")
+	}
+	if err = n.start(); err != nil {
+		t.Fatal(err)
+	}
+	if n.peer != nil {
+		t.Fatal("overflow issuer restarted")
+	}
+	if out.events[len(out.events)-1].Event != "Overflow" {
+		t.Fatal("overflow was not recorded")
+	}
+}
+
+// TestX3InitialNullAndDecisionInputs checks absent storage separately from "".
+// derives: C1.2, C2.1, C2.2, C3.5, F3.2
+func TestX3InitialNullAndDecisionInputs(t *testing.T) {
+	out, err := newEmitter(filepath.Join(t.TempDir(), "null.jsonl"), "initial-null")
+	if err != nil {
+		t.Fatal(err)
+	}
+	defer out.close()
+	e, err := newEngine(fixtureSchedule(), out, 1, "")
+	if err != nil {
+		t.Fatal(err)
+	}
+	defer e.close()
+	e.readDecision(WireMessage{client: "c1", generation: 1, grant: HeldGrant{token: 3, term: 2}})
+	v := out.events[len(out.events)-1]
+	if v.Event != "ReadAccept" || !v.NullValue {
+		t.Fatal("initial read did not serve null")
+	}
+	b, err := json.Marshal(v)
+	if err != nil {
+		t.Fatal(err)
+	}
+	var fields map[string]any
+	if err = json.Unmarshal(b, &fields); err != nil {
+		t.Fatal(err)
+	}
+	if value, present := fields["value"]; !present || value != nil {
+		t.Fatal("null value missing")
+	}
+	if len(v.Inputs) != 3 || v.Inputs[2].Name != "stored_value" || v.Inputs[2].Value != nil {
+		t.Fatal("initial stored_value input missing")
+	}
+}
diff --git a/impl/observe.go b/impl/observe.go
index 27610fd..c7ac79c 100644
--- a/impl/observe.go
+++ b/impl/observe.go
@@ -1,35 +1,66 @@
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 package main
 
 import (
+	"bytes"
 	"encoding/json"
 	"fmt"
 	"os"
 )
 
 // Ref identifies an event without a cross-process clock.
-// derives: C1.1, C1.2, C1.3, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type Ref struct {
 	Proc string `json:"proc"`
 	Seq  uint64 `json:"seq"`
+	Inc  uint64 `json:"inc"`
 }
 
 // Event is the shared observable record. Fault fields are copied from the action.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
+// derives: C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
+type Input struct {
+	Name  string `json:"name"`
+	Value any    `json:"value"`
+	Ref   *Ref   `json:"ref,omitempty"`
+}
+
+// derives: C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type Event struct {
-	Proc          string  `json:"proc"`
-	Seq           uint64  `json:"seq"`
-	Event         string  `json:"event"`
-	Client        string  `json:"client,omitempty"`
-	Key           string  `json:"key,omitempty"`
-	Token         uint64  `json:"token,omitempty"`
-	Lifetime      int64   `json:"lifetime,omitempty"`
-	Term          uint64  `json:"grantor_term,omitempty"`
-	Value         string  `json:"value,omitempty"`
-	ValuePresent  bool    `json:"-"`
-	HighestBefore *uint64 `json:"highest_before,omitempty"`
-	Outcome       string  `json:"outcome,omitempty"`
-	Causes        []Ref   `json:"causes"`
+	Inc           uint64   `json:"inc"`
+	Epoch         uint64   `json:"epoch,omitempty"`
+	ConfigEpoch   uint64   `json:"config_epoch,omitempty"`
+	Members       []string `json:"members,omitempty"`
+	RequestID     string   `json:"request_id,omitempty"`
+	Decided       bool     `json:"decided,omitempty"`
+	Readmits      [][]any  `json:"readmits,omitempty"`
+	Node          string   `json:"node,omitempty"`
+	NodeInc       uint64   `json:"node_incarnation,omitempty"`
+	Incarnation   uint64   `json:"incarnation,omitempty"`
+	Proposal      any      `json:"proposal,omitempty"`
+	Counted       []uint64 `json:"counted_toward,omitempty"`
+	Inputs        []Input  `json:"inputs,omitempty"`
+	Reason        string   `json:"reason,omitempty"`
+	Operator      string   `json:"operator,omitempty"`
+	To            string   `json:"to,omitempty"`
+	Clock         string   `json:"clock,omitempty"`
+	ClockStep     float64  `json:"step,omitempty"`
+	Amnesia       bool     `json:"amnesia,omitempty"`
+	What          string   `json:"what,omitempty"`
+	Proc          string   `json:"proc"`
+	Seq           uint64   `json:"seq"`
+	Event         string   `json:"event"`
+	Client        string   `json:"client,omitempty"`
+	Key           string   `json:"key,omitempty"`
+	Token         uint64   `json:"token,omitempty"`
+	Lifetime      int64    `json:"lifetime,omitempty"`
+	Term          uint64   `json:"grantor_term,omitempty"`
+	Value         string   `json:"value,omitempty"`
+	NullValue     bool     `json:"-"`
+	ValuePresent  bool     `json:"-"`
+	HighestBefore *uint64  `json:"highest_before,omitempty"`
+	Outcome       string   `json:"outcome,omitempty"`
+	Causes        []Ref    `json:"causes"`
 
 	Run       string     `json:"run"`
 	Side      string     `json:"side"`
@@ -37,21 +68,22 @@ type Event struct {
 	Crash     string     `json:"crash,omitempty"`
 	Restart   string     `json:"restart,omitempty"`
 	Partition [][]string `json:"partition,omitempty"`
-	// derives: F2.1, F2.2, L1, L2
+	// derives: F2.1, F2.2, L1, L2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 	Links  [][]string `json:"links,omitempty"`
 	Heal   bool       `json:"heal,omitempty"`
 	Pause  string     `json:"pause,omitempty"`
 	Resume string     `json:"resume,omitempty"`
 	// Observe schema v3: explicit attempt identity, independent of ack order.
-	// derives: C1.3, C2.2, F1.1, F1.2, F2.1, F2.2, F1.3
+	// derives: C1.3, C2.2, F1.1, F1.2, F2.1, F2.2, F1.3, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 	Answers *Ref `json:"answers,omitempty"`
 }
 
 // Emitter persists events synchronously; only the runner's event loop calls it.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type Emitter struct {
 	file   *os.File
 	run    string
+	inc    map[string]uint64
 	seq    map[string]uint64
 	events []Event
 	fault  Ref
@@ -59,18 +91,19 @@ type Emitter struct {
 }
 
 // newEmitter creates one trace per run, without truncating another run's trace.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func newEmitter(path, run string) (*Emitter, error) {
 	f, err := os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0644)
 	if err != nil {
 		return nil, err
 	}
-	return &Emitter{file: f, run: run, seq: map[string]uint64{}}, nil
+	return &Emitter{file: f, run: run, seq: map[string]uint64{}, inc: map[string]uint64{}}, nil
 }
 
 // emit adds local program order and the latest environmental cause.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Emitter) emit(v Event, causes ...Ref) Ref {
+	v.Inc = e.inc[v.Proc]
 	e.seq[v.Proc]++
 	v.Seq = e.seq[v.Proc]
 	v.Run = e.run
@@ -88,7 +121,7 @@ func (e *Emitter) emit(v Event, causes ...Ref) Ref {
 		v.Causes = append(v.Causes, r)
 	}
 	if v.Seq > 1 {
-		add(Ref{v.Proc, v.Seq - 1})
+		add(Ref{v.Proc, v.Seq - 1, v.Inc})
 	}
 	add(e.fault)
 	for _, r := range causes {
@@ -98,7 +131,7 @@ func (e *Emitter) emit(v Event, causes ...Ref) Ref {
 		e.err = err
 	}
 	e.events = append(e.events, v)
-	r := Ref{v.Proc, v.Seq}
+	r := Ref{v.Proc, v.Seq, v.Inc}
 	if v.Event == "Fault" {
 		e.fault = r
 	}
@@ -106,7 +139,7 @@ func (e *Emitter) emit(v Event, causes ...Ref) Ref {
 }
 
 // close makes emitter failures operational errors rather than checker results.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Emitter) close() error {
 	err := e.file.Close()
 	if e.err != nil {
@@ -116,7 +149,7 @@ func (e *Emitter) close() error {
 }
 
 // MarshalJSON emits even an empty value exactly when a read serves a value.
-// derives: C2.2
+// derives: C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e Event) MarshalJSON() ([]byte, error) {
 	type plain Event
 	var value *string
@@ -131,15 +164,59 @@ func (e Event) MarshalJSON() ([]byte, error) {
 		}
 		links = &resolved
 	}
-	return json.Marshal(struct {
+	b, err := json.Marshal(struct {
 		plain
 		Value *string     `json:"value,omitempty"`
 		Links *[][]string `json:"links,omitempty"`
 	}{plain(e), value, links})
+	if err != nil {
+		return nil, err
+	}
+	var m map[string]any
+	decoder := json.NewDecoder(bytes.NewReader(b))
+	decoder.UseNumber()
+	if err = decoder.Decode(&m); err != nil {
+		return nil, err
+	}
+	if e.NullValue {
+		m["value"] = nil
+	}
+	switch e.Event {
+	case "ReconfigSend", "ReconfigRequest":
+		m["members"] = e.Members
+		if e.Members == nil {
+			m["members"] = []string{}
+		}
+	case "Grant":
+		m["config_epoch"] = e.ConfigEpoch
+	case "Agree":
+		m["incarnation"] = e.Incarnation
+	case "Agreed":
+		m["node_incarnation"] = e.NodeInc
+		m["counted_toward"] = e.Counted
+		if e.Counted == nil {
+			m["counted_toward"] = []uint64{}
+		}
+	case "ConfigCommitted":
+		m["epoch"] = e.Epoch
+		m["decided"] = e.Decided
+		m["readmits"] = e.Readmits
+		if e.Readmits == nil {
+			m["readmits"] = [][]any{}
+		}
+		if e.Epoch == 0 {
+			m["request_id"] = nil
+		}
+	case "ReconfigRefused":
+		if e.Reason != "superseded" {
+			m["epoch"] = nil
+		}
+	}
+	return json.Marshal(m)
 }
 
 // UnmarshalJSON retains value presence so empty and absent are distinguishable.
-// derives: C2.2
+// derives: C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Event) UnmarshalJSON(data []byte) error {
 	type plain Event
 	var v plain
@@ -152,6 +229,7 @@ func (e *Event) UnmarshalJSON(data []byte) error {
 	}
 	*e = Event(v)
 	raw, ok := fields["value"]
-	e.ValuePresent = ok && string(raw) != "null"
+	e.ValuePresent = ok
+	e.NullValue = ok && string(raw) == "null"
 	return nil
 }
diff --git a/impl/observe_v3_test.go b/impl/observe_v3_test.go
index eb40944..4fabf63 100644
--- a/impl/observe_v3_test.go
+++ b/impl/observe_v3_test.go
@@ -29,10 +29,10 @@ func schemaRecords(t *testing.T, events []Event, change func([]map[string]any))
 			t.Fatal(err)
 		}
 		if e.Event == "WriteAck" {
-			records[i]["answers"] = Ref{"c1", 2}
+			records[i]["answers"] = Ref{"c1", 2, 0}
 		}
 		if e.Event == "ReadAck" {
-			records[i]["answers"] = Ref{"c1", 4}
+			records[i]["answers"] = Ref{"c1", 4, 0}
 		}
 	}
 	change(records)
@@ -70,13 +70,13 @@ func TestObserveV3Answers(t *testing.T) {
 				{"valid", false, func(m map[string]any) {}},
 				{"missing", true, func(m map[string]any) { delete(m, "answers") }},
 				{"zero", true, func(m map[string]any) { m["answers"] = Ref{} }},
-				{"absent", true, func(m map[string]any) { m["answers"] = Ref{"c1", 99} }},
-				{"wrong-kind", true, func(m map[string]any) { m["answers"] = Ref{"n1", 1} }},
+				{"absent", true, func(m map[string]any) { m["answers"] = Ref{"c1", 99, 0} }},
+				{"wrong-kind", true, func(m map[string]any) { m["answers"] = Ref{"n1", 1, 0} }},
 				{"wrong-operation", true, func(m map[string]any) {
 					if kind == "read" {
-						m["answers"] = Ref{"c1", 2}
+						m["answers"] = Ref{"c1", 2, 0}
 					} else {
-						m["answers"] = Ref{"c1", 1}
+						m["answers"] = Ref{"c1", 1, 0}
 					}
 				}},
 			} {
@@ -101,7 +101,7 @@ func TestObserveV3Answers(t *testing.T) {
 func TestObserveV3SameTokenRetry(t *testing.T) {
 	es := checkerFixture()
 	seven := uint64(7)
-	es = append(es, Event{Proc: "c1", Seq: 4, Event: "WriteAttempt", Client: "c1", Key: "k", Token: 7, Term: 2, Value: "retry", Causes: []Ref{{"n1", 1}, {"c1", 3}}}, Event{Proc: "s", Seq: 2, Event: "WriteAccept", Key: "k", Token: 7, Term: 2, HighestBefore: &seven, Causes: []Ref{{"c1", 4}, {"s", 1}}}, Event{Proc: "c1", Seq: 5, Event: "WriteAck", Client: "c1", Key: "k", Token: 7, Outcome: "accepted", Causes: []Ref{{"s", 2}, {"c1", 4}}})
+	es = append(es, Event{Proc: "c1", Seq: 4, Event: "WriteAttempt", Client: "c1", Key: "k", Token: 7, Term: 2, Value: "retry", Causes: []Ref{{"n1", 1, 0}, {"c1", 3, 0}}}, Event{Proc: "s", Seq: 2, Event: "WriteAccept", Key: "k", Token: 7, Term: 2, HighestBefore: &seven, Causes: []Ref{{"c1", 4, 0}, {"s", 1, 0}}}, Event{Proc: "c1", Seq: 5, Event: "WriteAck", Client: "c1", Key: "k", Token: 7, Outcome: "accepted", Causes: []Ref{{"s", 2, 0}, {"c1", 4, 0}}})
 	path := schemaRecords(t, es, func(ms []map[string]any) {})
 	v := checkTrace(path, fixtureSchedule(), RunEvidence{Completed: true})
 	if v.Clause != "" || v.Reason == "" {
diff --git a/impl/overflow_v3.go b/impl/overflow_v3.go
new file mode 100644
index 0000000..55de027
--- /dev/null
+++ b/impl/overflow_v3.go
@@ -0,0 +1,22 @@
+// derives: C1.1, C3.1, C3.7, C3.8, F3.2, F3.3
+package main
+
+import "math"
+
+// overflow stops this process's issuance before a bounded integer could wrap.
+// derives: C1.1, C3.1, C3.7, C3.8, F3.2, F3.3
+func (e *Engine) overflow(n *LeaseNode, what string) {
+	e.out.emit(Event{Proc: n.id, Event: "Overflow", What: what})
+	n.exhausted = true
+	_ = n.stop()
+}
+
+// canCampaign checks the next term before asking the library to increment it.
+// derives: C1.1, C3.7, F3.2, F3.3
+func (e *Engine) canCampaign(n *LeaseNode) bool {
+	if n.peer.BasicStatus().Term == math.MaxUint64 {
+		e.overflow(n, "term")
+		return false
+	}
+	return true
+}
diff --git a/impl/progress_v3.go b/impl/progress_v3.go
new file mode 100644
index 0000000..ab4783d
--- /dev/null
+++ b/impl/progress_v3.go
@@ -0,0 +1,166 @@
+// derives: C1.4, C3.4, C3.8, F1.1, F2.1, F2.2, F3.1, F3.2, F3.3
+package main
+
+import (
+	"fmt"
+	"time"
+)
+
+// ReconfigHorizon certifies a bounded stable opportunity, never an event order.
+// derives: C3.4, F3.1, F3.2, F3.3
+type ReconfigHorizon struct {
+	Request      Ref   `json:"request"`
+	StableFault  Ref   `json:"stable_fault"`
+	BudgetMillis int64 `json:"budget_ms"`
+}
+
+// cliquePremise enumerates connected eligible majorities of both configurations.
+// derives: C1.4, C3.4, C3.7, C3.8, F3.1, F3.3
+func cliquePremise(old, new []string, required []string, eligible func(string) bool, connected func(string, string) bool) bool {
+	union := append([]string{}, old...)
+	for _, n := range new {
+		if !contains(union, n) {
+			union = append(union, n)
+		}
+	}
+	for mask := 1; mask < (1 << len(union)); mask++ {
+		nodes := append([]string{}, required...)
+		a, b := 0, 0
+		for i, n := range union {
+			if mask&(1<<i) != 0 && eligible(n) {
+				nodes = append(nodes, n)
+				if contains(old, n) {
+					a++
+				}
+				if contains(new, n) {
+					b++
+				}
+			}
+		}
+		if a*2 <= len(old) || b*2 <= len(new) {
+			continue
+		}
+		ok := true
+		for _, x := range nodes {
+			for _, y := range nodes {
+				if !connected(x, y) {
+					ok = false
+				}
+			}
+		}
+		if ok {
+			return true
+		}
+	}
+	return false
+}
+
+// derives: C3.4, F3.1, F3.2, F3.3
+func (e *Engine) reconfigPremise(r *Reconfiguration) bool {
+	if e.futureFaults > 0 {
+		return false
+	}
+	if r.Request.Seq == 0 || r.Done || !e.alive(r.Receiver) || r.Generation != e.nodes[r.Receiver].generation {
+		return false
+	}
+	return cliquePremise(e.members, r.Members, []string{r.Receiver}, func(n string) bool { return e.nodeEligible(n, e.epoch) }, e.connected)
+}
+
+// derives: C3.4, F3.1, F3.2, F3.3
+func (e *Engine) reconfigHorizons() []ReconfigHorizon {
+	out := []ReconfigHorizon{}
+	for _, r := range e.reconfigs {
+		if e.reconfigPremise(r) && !r.EligibleSince.IsZero() && e.now().Sub(r.EligibleSince) >= progressHorizon {
+			out = append(out, ReconfigHorizon{r.Request, e.out.fault, progressHorizon.Milliseconds()})
+		}
+	}
+	return out
+}
+
+// finalMembership reconstructs global committed membership and latest eligibility.
+// derives: C1.4, C3.4, C3.7, C3.8, F3.1, F3.3
+func (g *traceGraph) finalMembership(s Schedule) ([]string, map[string]bool, Ref) {
+	mem := initialMembers(s)
+	epoch := uint64(0)
+	incs := map[string]uint64{}
+	admitted := map[string]uint64{}
+	var fault Ref
+	for _, v := range g.local["env"] {
+		if v.Event == "Fault" {
+			fault = Ref{v.Proc, v.Seq, v.Inc}
+			if v.Amnesia {
+				incs[v.Restart]++
+			}
+		}
+	}
+	for _, v := range g.ordered {
+		if v.Event == "ConfigCommitted" && v.Decided {
+			if v.Epoch > epoch {
+				mem = v.Members
+				epoch = v.Epoch
+			}
+			for _, a := range v.Readmits {
+				if len(a) == 2 {
+					node, _ := a[0].(string)
+					if inc, ok := a[1].(float64); ok {
+						admitted[node] = uint64(inc)
+					}
+				}
+			}
+		}
+	}
+	eligible := map[string]bool{}
+	for _, n := range s.Processes.Lease {
+		eligible[n] = incs[n] == 0 || admitted[n] == incs[n]
+	}
+	return mem, eligible, fault
+}
+
+// requestPending examines only receiver-local records and amnesia destruction.
+// derives: C1.4, C3.4, F3.1, F3.3
+func (g *traceGraph) requestPending(req Event) bool {
+	for _, v := range g.local[req.Proc] {
+		if v.Inc > req.Inc {
+			return false
+		}
+		if v.Inc == req.Inc && v.Seq > req.Seq && (v.Event == "ReconfigRefused" && v.RequestID == req.RequestID || v.Event == "ConfigCommitted" && v.Epoch > 0) {
+			return false
+		}
+	}
+	return true
+}
+
+// checkReconfigProgress validates the finite certificate against raw final topology.
+// derives: C3.4, F3.1, F3.2, F3.3
+func (g *traceGraph) checkReconfigProgress(s Schedule, evidence RunEvidence) Verdict {
+	mem, eligible, fault := g.finalMembership(s)
+	state := g.routingEnvironments(s)[fault]
+	connected := func(a, b string) bool {
+		return state.up[a] && state.up[b] && !state.down[link{a, b}] && !state.down[link{b, a}]
+	}
+	for _, w := range evidence.ReconfigHorizons {
+		req, ok := g.events[w.Request]
+		if !ok || req.Event != "ReconfigRequest" || w.StableFault != fault || w.BudgetMillis < 3000 {
+			return Verdict{Reason: "invalid reconfiguration horizon"}
+		}
+		if !g.requestPending(req) {
+			continue
+		}
+		if !cliquePremise(mem, req.Members, []string{req.Proc}, func(n string) bool { return eligible[n] }, connected) {
+			return Verdict{Reason: "reconfiguration horizon lacks eligible connected majorities"}
+		}
+		return Verdict{Clause: "C3.4", Reason: fmt.Sprintf("pending request %s exhausted stable horizon", req.RequestID)}
+	}
+	return Verdict{}
+}
+
+// resetProgress preserves the after-last-fault interpretation of both duties.
+// derives: C1.4, C3.4, F3.1, F3.2, F3.3
+func (e *Engine) resetProgress() {
+	for _, r := range e.requests {
+		r.eligibleSince = time.Time{}
+	}
+	for _, r := range e.reconfigs {
+		r.EligibleSince = time.Time{}
+	}
+}
diff --git a/impl/raft.go b/impl/raft.go
index e18a903..674cbb5 100644
--- a/impl/raft.go
+++ b/impl/raft.go
@@ -1,4 +1,4 @@
-// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
+// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 package main
 
 import (
@@ -13,38 +13,59 @@ import (
 )
 
 // Allocation is the index/term of an actually committed Raft log entry.
-// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
-type Allocation struct{ Token, Term uint64 }
+// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
+type Allocation struct {
+	Token, Term uint64
+	Proposal    Proposal
+}
 
 // LeaseNode retains storage/applied FSM state across logical process replacement.
 // RawNode has no timer goroutine and receives only scheduler-controlled inputs.
-// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
+// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
+// derives: C3.1, C3.5, C3.7, C3.8, F3.1, F3.3, C3.4, F3.2
 type LeaseNode struct {
-	id         string
-	number     uint64
-	durable    *raft.MemoryStorage
-	network    *RaftNetwork
-	peer       *raft.RawNode
-	generation uint64
-	applied    uint64
-	electionAt time.Time
+	exhausted    bool
+	issued       map[Ref]HeldGrant
+	lastGrantAt  int64
+	hasGranted   bool
+	lastTokenRef Ref
+	epoch        uint64
+	members      []string
+	conf         pb.ConfState
+	commit       Event
+	commitRef    Ref
+	agreements   map[uint64]Agreement
+	received     map[string][]Ref
+	lastToken    uint64
+	id           string
+	number       uint64
+	durable      *raft.MemoryStorage
+	network      *RaftNetwork
+	peer         *raft.RawNode
+	generation   uint64
+	applied      uint64
+	electionAt   time.Time
 }
 
-// newLeaseNode creates one retained store and a fixed voter identity.
-// derives: C1.1, C1.4, F1.1
+// newLeaseNode creates a retained store and a stable process identity.
+// derives: C1.1, C1.4, F1.1, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func newLeaseNode(id string, network *RaftNetwork) *LeaseNode {
 	number := network.ids[id]
 	return &LeaseNode{id: id, number: number, network: network, durable: raft.NewMemoryStorage()}
 }
 
-// start initializes a fixed configuration or recovers the prior hard state/log.
+// start initializes deployment membership or recovers prior hard state/log.
 // The bootstrap snapshot fixes membership only; it allocates no fencing token.
-// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
+// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (n *LeaseNode) start() error {
 	e := n.network.owner
-	if n.applied == 0 {
-		voters := make([]uint64, 0, len(e.schedule.Processes.Lease))
-		for _, id := range e.schedule.Processes.Lease {
+	if n.exhausted {
+		return nil
+	}
+	if n.applied == 0 && e.out.inc[n.id] == 0 {
+		n.members = append([]string{}, initialMembers(e.schedule)...)
+		voters := make([]uint64, 0, len(initialMembers(e.schedule)))
+		for _, id := range initialMembers(e.schedule) {
 			voters = append(voters, n.network.ids[id])
 		}
 		snap := pb.Snapshot{Metadata: pb.SnapshotMetadata{Index: 1, Term: 1, ConfState: pb.ConfState{Voters: voters}}}
@@ -55,8 +76,9 @@ func (n *LeaseNode) start() error {
 			return err
 		}
 		n.applied = 1
+		n.conf = snap.Metadata.ConfState
 	}
-	config := &raft.Config{ID: n.number, ElectionTick: 10, HeartbeatTick: 1, Storage: n.durable, Applied: n.applied, MaxSizePerMsg: 1 << 20, MaxInflightMsgs: 256, CheckQuorum: true, PreVote: true, Logger: &raft.DefaultLogger{Logger: log.New(io.Discard, "", 0)}}
+	config := &raft.Config{ID: n.number, ElectionTick: 10, HeartbeatTick: 1, Storage: n.durable, Applied: n.applied, MaxSizePerMsg: 1 << 20, MaxInflightMsgs: 256, CheckQuorum: true, StepDownOnRemoval: true, PreVote: true, Logger: &raft.DefaultLogger{Logger: log.New(io.Discard, "", 0)}}
 	peer, err := raft.NewRawNode(config)
 	if err != nil {
 		return fmt.Errorf("start %s: %w", n.id, err)
@@ -70,14 +92,14 @@ func (n *LeaseNode) start() error {
 
 // resetElection supplies the only election deadline that can trigger a campaign.
 // RawNode's randomized follower timeout is never used (followers tick quiesced).
-// derives: C1.4, F1.1, F1.2, F2.1, F2.2
+// derives: C1.4, F1.1, F1.2, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (n *LeaseNode) resetElection() {
 	e := n.network.owner
 	n.electionAt = e.now().Add(time.Duration(100+e.rng.Intn(80)) * time.Millisecond)
 }
 
 // stop loses volatile state and inbox membership while retaining storage/FSM state.
-// derives: C1.1, C1.4, F1.1
+// derives: C1.1, C1.4, F1.1, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (n *LeaseNode) stop() error {
 	if n.peer != nil {
 		n.network.remove(n.id)
@@ -87,7 +109,7 @@ func (n *LeaseNode) stop() error {
 }
 
 // raftCommand identifies a proposal, never the allocation's authoritative token.
-// derives: C1.1, C1.4, F1.1
+// derives: C1.1, C1.4, F1.1, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func raftCommand(id uint64) []byte {
 	data := make([]byte, 8)
 	binary.BigEndian.PutUint64(data, id)
diff --git a/impl/read_v2_test.go b/impl/read_v2_test.go
index 65783c5..d69ed77 100644
--- a/impl/read_v2_test.go
+++ b/impl/read_v2_test.go
@@ -17,9 +17,9 @@ func readFixture() []Event {
 	es := checkerFixture()
 	seven := uint64(7)
 	return append(es,
-		Event{Proc: "c1", Seq: 4, Event: "ReadAttempt", Client: "c1", Key: "k", Token: 7, Term: 2, Causes: []Ref{{"n1", 1}}},
-		Event{Proc: "s", Seq: 2, Event: "ReadAccept", Key: "k", Token: 7, Term: 2, HighestBefore: &seven, Value: "v", Causes: []Ref{{"c1", 4}}},
-		Event{Proc: "c1", Seq: 5, Event: "ReadAck", Answers: &Ref{"c1", 4}, Client: "c1", Key: "k", Token: 7, Outcome: "served", Value: "v", Causes: []Ref{{"s", 2}}})
+		Event{Proc: "c1", Seq: 4, Event: "ReadAttempt", Client: "c1", Key: "k", Token: 7, Term: 2, Causes: []Ref{{"n1", 1, 0}}},
+		Event{Proc: "s", Seq: 2, Event: "ReadAccept", Key: "k", Token: 7, Term: 2, HighestBefore: &seven, Value: "v", Causes: []Ref{{"c1", 4, 0}}},
+		Event{Proc: "c1", Seq: 5, Event: "ReadAck", Answers: &Ref{"c1", 4, 0}, Client: "c1", Key: "k", Token: 7, Outcome: "served", Value: "v", Causes: []Ref{{"s", 2, 0}}})
 }
 
 // TestX1ReadCheckers uses counterexamples independent of running storage state.
@@ -35,7 +35,7 @@ func TestX1ReadCheckers(t *testing.T) {
 		{"wrong-storage-snapshot", "C2.2", func(es []Event) []Event { es[6].Value = "invented"; es[7].Value = "invented"; return es }},
 		{"wrong-reply-value", "C2.2", func(es []Event) []Event { es[7].Value = "later-value"; return es }},
 		{"wrong-reply-client", "C2.2", func(es []Event) []Event { es[7].Client = "c2"; return es }},
-		{"unserved-attempt", "C2.2", func(es []Event) []Event { es = append(es[:6], es[7]); es[6].Causes = []Ref{{"c1", 4}}; return es }},
+		{"unserved-attempt", "C2.2", func(es []Event) []Event { es = append(es[:6], es[7]); es[6].Causes = []Ref{{"c1", 4, 0}}; return es }},
 	}
 	for _, tc := range cases {
 		t.Run(tc.name, func(t *testing.T) {
@@ -103,7 +103,7 @@ func TestX1ReadStoragePath(t *testing.T) {
 			defer e.close()
 			e.ledger = 7
 			e.storageValue = "stored"
-			e.clients["c1"].grants = []HeldGrant{{token: token, term: 2, ref: Ref{"n1", 1}}}
+			e.clients["c1"].grants = []HeldGrant{{token: token, term: 2, ref: Ref{"n1", 1, 0}}}
 			var a Action
 			if err = yaml.Unmarshal([]byte("read: c1"), &a); err != nil {
 				t.Fatal(err)
diff --git a/impl/routing.go b/impl/routing.go
index 4fa876b..b99045f 100644
--- a/impl/routing.go
+++ b/impl/routing.go
@@ -90,6 +90,9 @@ func visitedLease(hops []RouteHop, id string) bool {
 // R2 deliberately breaks only the reply relaying mechanism.
 // derives: C1.1, C1.4, F1.1, F2.1, F2.2, L3
 func (e *Engine) spreadGrant(m LeasePacket, id string) {
+	if e.mutation == "P12" && e.pauseSeen {
+		return
+	}
 	m.kind = "grant"
 	e.sendLease(m, id, m.request.client)
 	if e.mutation == "R2" {
diff --git a/impl/routing_test.go b/impl/routing_test.go
index f957241..54ee7bd 100644
--- a/impl/routing_test.go
+++ b/impl/routing_test.go
@@ -25,8 +25,8 @@ func TestFixRIssuanceBeforeReceipt(t *testing.T) {
 	r := e.requests[0]
 	n := e.nodes["n1"]
 	e.down[link{"n1", "c2"}] = true
-	e.finishAllocation(completedAllocation{request: r, node: "n1", generation: n.generation, allocation: Allocation{7, 2}})
-	if len(out.events) != 2 || out.events[1].Event != "Grant" {
+	e.finishAllocation(completedAllocation{request: r, node: "n1", generation: n.generation, allocation: fixtureAllocation(e, "n1", 7, 2)})
+	if out.events[len(out.events)-1].Event != "Grant" {
 		t.Fatal("issued-but-undelivered Grant omitted")
 	}
 	if r.done || len(e.clients["c2"].grants) != 0 {
@@ -39,10 +39,10 @@ func TestFixRIssuanceBeforeReceipt(t *testing.T) {
 func TestFixRC14IssuedNotDelivered(t *testing.T) {
 	es := []Event{
 		{Proc: "env", Seq: 1, Event: "Fault", Cell: "F2.2", Links: [][]string{{"n1", "c2"}}},
-		{Proc: "c2", Seq: 1, Event: "Request", Client: "c2", Key: "k", Causes: []Ref{{"env", 1}}},
-		{Proc: "n1", Seq: 1, Event: "Grant", Client: "c2", Key: "k", Token: 7, Term: 2, Lifetime: 40, Causes: []Ref{{"c2", 1}}},
+		{Proc: "c2", Seq: 1, Event: "Request", Client: "c2", Key: "k", Causes: []Ref{{"env", 1, 0}}},
+		{Proc: "n1", Seq: 1, Event: "Grant", Client: "c2", Key: "k", Token: 7, Term: 2, Lifetime: 40, Causes: []Ref{{"c2", 1, 0}}},
 	}
-	evidence := RunEvidence{Witnesses: []ProgressWitness{{Ref{"c2", 1}, Ref{"env", 1}, 3000}}, Reason: "horizon exhausted"}
+	evidence := RunEvidence{Witnesses: []ProgressWitness{{Ref{"c2", 1, 0}, Ref{"env", 1, 0}, 3000}}, Reason: "horizon exhausted"}
 	v := checkTrace(writeFixture(t, es), fixtureSchedule(), evidence)
 	if v.Clause != "C1.4" {
 		t.Fatalf("undelivered issuance masked liveness: %+v", v)
diff --git a/impl/run.sh b/impl/run.sh
index 6b0d5ad..b1936d0 100755
--- a/impl/run.sh
+++ b/impl/run.sh
@@ -13,6 +13,11 @@ if ! git show HEAD:impl/PREREGISTRATION.md | rg '^## Timing repair' >/dev/null;
   echo 'UNEXPLAINED Timing-repair predictions are not committed'
   exit 2
 fi
+# derives: C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
+if ! git show HEAD:impl/PREREGISTRATION.md | rg '^## X3 adapt preregistration' >/dev/null; then
+  echo 'UNEXPLAINED X3 predictions are not committed'
+  exit 2
+fi
 export GOMODCACHE="$PWD/.cache/mod"
 export GOPATH="$PWD/.cache/gopath"
 export GOCACHE="$PWD/.cache/build"
diff --git a/impl/runner_v2.go b/impl/runner_v2.go
index fe5c899..e0d0f67 100644
--- a/impl/runner_v2.go
+++ b/impl/runner_v2.go
@@ -1,4 +1,4 @@
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, E2, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, E2, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 package main
 
 import (
@@ -7,7 +7,7 @@ import (
 )
 
 // FrozenAction captures selectors when a trigger fires, before delay or waiting.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T2, T3, A1, A2, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T2, T3, A1, A2, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type FrozenAction struct {
 	Actions         []Action
 	Rest            []string
@@ -16,10 +16,10 @@ type FrozenAction struct {
 }
 
 // freezeAction resolves aliases everywhere and checks concrete operation roles.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, A1, A2, T2, T3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, A1, A2, T2, T3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) freezeAction(a Action) (FrozenAction, error) {
 	frozen := FrozenAction{}
-	// derives: F2.1, F2.2, L1, A1, T2
+	// derives: F2.1, F2.2, L1, A1, T2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 	if a.Cut != nil || a.Drop != nil {
 		pairs := a.Cut
 		if a.Drop != nil {
@@ -67,7 +67,7 @@ func (e *Engine) freezeAction(a Action) (FrozenAction, error) {
 			selected := e.lastNonGrantor
 			// v2.2 A1: restart is bound to the most recent selector crash,
 			// regardless of the current grantor or available fresh candidates.
-			// derives: C1.4, F1.1, A1, A2
+			// derives: C1.4, F1.1, A1, A2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 			if a.Restart != "" {
 				if selected == "" {
 					return frozen, fmt.Errorf("A1: restart non-grantor without a preceding crash non-grantor")
@@ -83,6 +83,12 @@ func (e *Engine) freezeAction(a Action) (FrozenAction, error) {
 			if a.Crash != "" {
 				frozen.NonGrantorCrash = selected
 			}
+		case "non-member":
+			selected, err := e.nonMember()
+			if err != nil {
+				return frozen, err
+			}
+			targets = []string{selected}
 		case "rest":
 			targets = append([]string{}, e.rest...)
 		}
@@ -109,7 +115,7 @@ func (e *Engine) freezeAction(a Action) (FrozenAction, error) {
 }
 
 // highestGranted implements the v2 numeric stale-token definition even in mutations.
-// derives: C1.1, C1.2, F1.3, T3, C2.1, C2.2
+// derives: C1.1, C1.2, F1.3, T3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) highestGranted() uint64 {
 	var max uint64
 	for _, event := range e.out.events {
@@ -121,11 +127,14 @@ func (e *Engine) highestGranted() uint64 {
 }
 
 // workloadReady waits for client availability, tokens and previous request replies.
-// derives: C1.1, C1.2, C1.4, F1.1, F1.3, F2.1, F2.2, T3, A1, C2.1, C2.2
+// derives: C1.1, C1.2, C1.4, F1.1, F1.3, F2.1, F2.2, T3, A1, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) workloadReady(f FrozenAction) bool {
 	for _, a := range f.Actions {
+		if a.Resume != "" && e.now().Sub(e.clients[a.Resume].pauseTime) < e.lifetime() {
+			return false
+		}
 		// Issuance can precede actual holder receipt; a holder pause waits for it.
-		// derives: C1.4, F1.3, F2.1, F2.2, T3
+		// derives: C1.4, F1.3, F2.1, F2.2, T3, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 		if a.Pause != "" {
 			c := e.clients[a.Pause]
 			if c == nil || !c.up || c.paused || len(c.grants) == 0 || !e.now().Before(c.grants[len(c.grants)-1].expires) {
@@ -174,8 +183,11 @@ func (e *Engine) workloadReady(f FrozenAction) bool {
 }
 
 // quiescent counts active workload only, excluding stopped/paused incarnations.
-// derives: C1.3, C1.4, F1.1, F1.3, F2.1, F2.2, E1, C2.1, C2.2
+// derives: C1.3, C1.4, F1.1, F1.3, F2.1, F2.2, E1, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) quiescent() bool {
+	if e.reconfigActive() {
+		return false
+	}
 	for _, r := range e.requests {
 		c := e.clients[r.client]
 		if !r.done && c.up && !c.paused && c.generation == r.generation {
@@ -198,7 +210,7 @@ func (e *Engine) quiescent() bool {
 }
 
 // validateTransition compiles state-dependent A2 checks before any side effect.
-// derives: C1.1, C1.4, F1.1, F1.3, A1, A2, C2.1, C2.2
+// derives: C1.1, C1.4, F1.1, F1.3, A1, A2, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) validateTransition(a Action) error {
 	if a.Crash != "" && !e.alive(a.Crash) {
 		return fmt.Errorf("A2: crash of stopped process %s", a.Crash)
@@ -222,7 +234,7 @@ func (e *Engine) validateTransition(a Action) error {
 }
 
 // drive applies fresh arming, frozen selectors, sampled delay and bounded quiescence.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, E2, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, E2, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (e *Engine) drive() RunEvidence {
 	result := RunEvidence{Derives: []string{"C1.1", "C1.2", "C1.3", "C1.4", "C2.1", "C2.2", "F1.1", "F1.2", "F1.3", "F2.1", "F2.2", "L1", "L2", "L3", "E3", "T1", "T2", "T3", "A1", "A2", "E1", "E2"}}
 	wait := func(ready func() bool, reason string) bool {
@@ -245,7 +257,7 @@ func (e *Engine) drive() RunEvidence {
 				result.Reason = e.out.err.Error()
 				return false
 			}
-			if len(e.witnesses()) > 0 {
+			if len(e.witnesses()) > 0 || len(e.reconfigHorizons()) > 0 {
 				result.Reason = "progress horizon exhausted"
 				return false
 			}
@@ -256,8 +268,15 @@ func (e *Engine) drive() RunEvidence {
 		}
 	}
 	finish := func() RunEvidence {
+		for _, id := range e.schedule.Processes.Lease {
+			n := e.nodes[id]
+			if n.peer != nil {
+				result.ProtocolState = append(result.ProtocolState, fmt.Sprintf("%s applied=%d epoch=%d conf=%v status=%+v", id, n.applied, n.epoch, n.conf, n.peer.BasicStatus()))
+			}
+		}
 		result.Clock = LogicalClockEvidence{"timing-v1", e.seed, e.now().Sub(time.Unix(0, 0).UTC()).Milliseconds()}
 		result.Witnesses = e.witnesses()
+		result.ReconfigHorizons = e.reconfigHorizons()
 		result.Deliveries = e.deliveries
 		return result
 	}
@@ -287,8 +306,11 @@ func (e *Engine) drive() RunEvidence {
 		}
 		// v2.1 T1: the predecessor's own Request, WriteAttempt, ReadAttempt and Fault
 		// count as after successor arming; this preserves the existing v2 behavior.
-		// derives: C1.1, C1.3, F1.1, T1, E1, C2.1, C2.2
+		// derives: C1.1, C1.3, F1.1, T1, E1, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 		armed = len(e.out.events)
+		if step.Do.Cell != "" && step.Do.Reconfigure == nil && !step.Do.Heal && e.futureFaults > 0 {
+			e.futureFaults--
+		}
 		for _, a := range frozen.Actions {
 			if err := e.act(a, trigger); err != nil {
 				result.Reason = err.Error()
@@ -296,7 +318,7 @@ func (e *Engine) drive() RunEvidence {
 			}
 		}
 		// v2.2 A1: only a successfully applied selector crash updates this binding.
-		// derives: C1.4, F1.1, A1, A2
+		// derives: C1.4, F1.1, A1, A2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 		if frozen.NonGrantorCrash != "" {
 			e.lastNonGrantor = frozen.NonGrantorCrash
 		}
diff --git a/impl/schedule.go b/impl/schedule.go
index 5a29990..961baf2 100644
--- a/impl/schedule.go
+++ b/impl/schedule.go
@@ -1,18 +1,22 @@
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 package main
 
 import (
+	"encoding/json"
 	"fmt"
 	"io"
+	"math"
 	"os"
 	"path/filepath"
+	"reflect"
+	"sort"
 	"strings"
 
 	"gopkg.in/yaml.v3"
 )
 
 // Trigger describes a freshly armed event predicate or terminal quiescence.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type Trigger struct {
 	Start     bool
 	Quiescent bool
@@ -20,7 +24,7 @@ type Trigger struct {
 }
 
 // UnmarshalYAML rejects unknown or non-observable trigger fields.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (t *Trigger) UnmarshalYAML(n *yaml.Node) error {
 	if n.Kind == yaml.ScalarNode {
 		if n.Value == "quiescent" {
@@ -37,16 +41,26 @@ func (t *Trigger) UnmarshalYAML(n *yaml.Node) error {
 		return fmt.Errorf("trigger must be start or a mapping")
 	}
 	t.Filters = map[string]string{}
-	allowed := map[string]bool{"event": true, "client": true, "key": true, "token": true, "lifetime": true, "grantor_term": true, "value": true, "highest_before": true, "outcome": true, "proc": true}
+	allowed := map[string]bool{"config_epoch": true, "inc": true, "operator": true, "to": true, "what": true, "node_incarnation": true, "incarnation": true, "amnesia": true, "clock": true, "restart": true, "crash": true, "step": true, "epoch": true, "request_id": true, "reason": true, "decided": true, "members": true, "node": true, "event": true, "client": true, "key": true, "token": true, "lifetime": true, "grantor_term": true, "value": true, "highest_before": true, "outcome": true, "proc": true}
 	for i := 0; i < len(n.Content); i += 2 {
 		k, v := n.Content[i].Value, n.Content[i+1]
-		if !allowed[k] || v.Kind != yaml.ScalarNode {
+		if !allowed[k] || v.Kind != yaml.ScalarNode && k != "members" {
 			return fmt.Errorf("unsupported trigger field %q", k)
 		}
 		if _, ok := t.Filters[k]; ok {
 			return fmt.Errorf("duplicate trigger field %s", k)
 		}
-		t.Filters[k] = v.Value
+		if k == "members" {
+			var members []string
+			if err := v.Decode(&members); err != nil {
+				return err
+			}
+			sort.Strings(members)
+			b, _ := json.Marshal(members)
+			t.Filters[k] = string(b)
+		} else {
+			t.Filters[k] = v.Value
+		}
 	}
 	if !observable(t.Filters["event"]) {
 		return fmt.Errorf("trigger must name an observable event")
@@ -55,28 +69,36 @@ func (t *Trigger) UnmarshalYAML(n *yaml.Node) error {
 }
 
 // observable includes Fault for the v4 schedule trigger language.
-// derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func observable(s string) bool {
 	switch s {
-	case "Fault", "Request", "Grant", "WriteAttempt", "WriteAccept", "WriteReject", "WriteAck", "ReadAttempt", "ReadAccept", "ReadReject", "ReadAck":
+	case "Agree", "Agreed", "ConfigCommitted", "ReconfigSend", "ReconfigRequest", "ReconfigRefused", "ReconfigAck", "Overflow", "Fault", "Request", "Grant", "WriteAttempt", "WriteAccept", "WriteReject", "WriteAck", "ReadAttempt", "ReadAccept", "ReadReject", "ReadAck":
 		return true
 	}
 	return false
 }
 
 // Action is the complete, closed action language; there is no arbitrary sleep.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
+// derives: C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type Action struct {
-	Request   string     `yaml:"request,omitempty"`
-	Write     string     `yaml:"write,omitempty"`
-	Read      string     `yaml:"read,omitempty"`
-	Value     string     `yaml:"value,omitempty"`
-	Token     string     `yaml:"token,omitempty"`
-	Cell      string     `yaml:"cell,omitempty"`
-	Crash     string     `yaml:"crash,omitempty"`
-	Restart   string     `yaml:"restart,omitempty"`
-	Partition [][]string `yaml:"partition,omitempty"`
-	// derives: F2.1, F2.2, L1, L2
+	Reconfigure []string   `yaml:"reconfigure,omitempty"`
+	To          string     `yaml:"to,omitempty"`
+	ID          string     `yaml:"id,omitempty"`
+	Operator    string     `yaml:"operator,omitempty"`
+	Clock       string     `yaml:"clock,omitempty"`
+	ClockStep   float64    `yaml:"step,omitempty"`
+	Amnesia     bool       `yaml:"amnesia,omitempty"`
+	Request     string     `yaml:"request,omitempty"`
+	Write       string     `yaml:"write,omitempty"`
+	Read        string     `yaml:"read,omitempty"`
+	Value       string     `yaml:"value,omitempty"`
+	Token       string     `yaml:"token,omitempty"`
+	Cell        string     `yaml:"cell,omitempty"`
+	Crash       string     `yaml:"crash,omitempty"`
+	Restart     string     `yaml:"restart,omitempty"`
+	Partition   [][]string `yaml:"partition,omitempty"`
+	// derives: F2.1, F2.2, L1, L2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 	Cut    [][]string `yaml:"cut,omitempty"`
 	Drop   [][]string `yaml:"drop,omitempty"`
 	Heal   bool       `yaml:"heal,omitempty"`
@@ -85,21 +107,24 @@ type Action struct {
 }
 
 // Step waits for its trigger and then applies exactly one action.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type Step struct {
 	At Trigger `yaml:"at"`
 	Do Action  `yaml:"do"`
 }
 
 // Schedule is the shared YAML interface interpreted independently here.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type Schedule struct {
+	Lifetime  int64    `yaml:"lifetime"`
 	Name      string   `yaml:"schedule"`
 	Derives   []string `yaml:"derives"`
 	Processes struct {
-		Lease   []string `yaml:"lease"`
-		Clients []string `yaml:"clients"`
-		Storage []string `yaml:"storage"`
+		Config    []string `yaml:"config"`
+		Operators []string `yaml:"operators"`
+		Lease     []string `yaml:"lease"`
+		Clients   []string `yaml:"clients"`
+		Storage   []string `yaml:"storage"`
 	} `yaml:"processes"`
 	Steps []Step  `yaml:"steps"`
 	End   Trigger `yaml:"end"`
@@ -109,7 +134,7 @@ type Schedule struct {
 }
 
 // loadSchedule resolves only the repository-root shared schedule directory.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func loadSchedule(name string) (Schedule, error) {
 	var s Schedule
 	base := strings.TrimSuffix(name, ".yaml")
@@ -148,14 +173,29 @@ func loadSchedule(name string) (Schedule, error) {
 	if s.Name == "" || strings.ContainsAny(s.Name, "/\\") || s.Bound.Events < 1 || s.Bound.Events > 10000 || len(s.Steps) == 0 {
 		return s, fmt.Errorf("invalid schedule name, bound or empty steps")
 	}
-	if len(s.Processes.Lease) != 3 || len(s.Processes.Clients) != 2 || len(s.Processes.Storage) != 1 {
-		return s, fmt.Errorf("need 3 lease nodes, 2 clients, 1 storage")
+	if len(s.Processes.Lease) < 1 || len(s.Processes.Lease) > 6 || len(s.Processes.Clients) != 2 || len(s.Processes.Storage) != 1 {
+		return s, fmt.Errorf("need 1..6 lease nodes, 2 clients, 1 storage")
+	}
+	if s.Lifetime == 0 {
+		s.Lifetime = 1
+	}
+	if s.Lifetime < 1 {
+		return s, fmt.Errorf("invalid lifetime")
+	}
+	if s.Processes.Config == nil {
+		s.Processes.Config = append([]string{}, s.Processes.Lease...)
+	}
+	if len(s.Processes.Config) == 0 {
+		return s, fmt.Errorf("empty initial configuration")
+	}
+	if s.Processes.Operators == nil {
+		s.Processes.Operators = []string{"op"}
 	}
 	ids := map[string]string{}
 	for _, group := range []struct {
 		ids  []string
 		role string
-	}{{s.Processes.Lease, "lease"}, {s.Processes.Clients, "client"}, {s.Processes.Storage, "storage"}} {
+	}{{s.Processes.Lease, "lease"}, {s.Processes.Clients, "client"}, {s.Processes.Storage, "storage"}, {s.Processes.Operators, "operator"}} {
 		for _, id := range group.ids {
 			if id == "" || id == "env" || id == "rest" || id == "grantor" || id == "holder" || id == "non-grantor" || ids[id] != "" {
 				return s, fmt.Errorf("invalid process %q", id)
@@ -163,7 +203,14 @@ func loadSchedule(name string) (Schedule, error) {
 			ids[id] = group.role
 		}
 	}
-	known := map[string]bool{"C1.1": true, "C1.2": true, "C1.3": true, "C1.4": true, "C2.1": true, "C2.2": true, "F1.1": true, "F1.2": true, "F1.3": true, "F2.1": true, "F2.2": true, "L1": true, "L2": true, "L3": true, "E3": true, "T1": true, "T2": true, "T3": true, "A1": true, "A2": true, "E1": true, "E2": true}
+	seenConfig := map[string]bool{}
+	for _, id := range s.Processes.Config {
+		if ids[id] != "lease" || seenConfig[id] {
+			return s, fmt.Errorf("invalid initial configuration")
+		}
+		seenConfig[id] = true
+	}
+	known := map[string]bool{"C3.1": true, "C3.4": true, "C3.5": true, "C3.7": true, "C3.8": true, "F3.1": true, "F3.2": true, "F3.3": true, "C1.1": true, "C1.2": true, "C1.3": true, "C1.4": true, "C2.1": true, "C2.2": true, "F1.1": true, "F1.2": true, "F1.3": true, "F2.1": true, "F2.2": true, "L1": true, "L2": true, "L3": true, "E3": true, "T1": true, "T2": true, "T3": true, "A1": true, "A2": true, "E1": true, "E2": true}
 	if len(s.Derives) == 0 {
 		return s, fmt.Errorf("missing derivations")
 	}
@@ -172,7 +219,17 @@ func loadSchedule(name string) (Schedule, error) {
 			return s, fmt.Errorf("unknown derivation %s", id)
 		}
 	}
+	requestIDs := map[string]bool{}
 	for _, step := range s.Steps {
+		if step.Do.Reconfigure != nil {
+			if requestIDs[step.Do.ID] {
+				return s, fmt.Errorf("duplicate request id")
+			}
+			requestIDs[step.Do.ID] = true
+		}
+		if step.Do.Clock != "" && math.Trunc(step.Do.ClockStep*float64(s.Lifetime)) != step.Do.ClockStep*float64(s.Lifetime) {
+			return s, fmt.Errorf("fractional clock tick")
+		}
 		if step.At.Quiescent || !step.At.Start && len(step.At.Filters) == 0 {
 			return s, fmt.Errorf("missing trigger")
 		}
@@ -193,8 +250,39 @@ func loadSchedule(name string) (Schedule, error) {
 }
 
 // validateAction rejects out-of-model faults and malformed workload actions.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func validateAction(a Action, ids map[string]string) error {
+	if a.Reconfigure != nil {
+		residual := a
+		residual.Reconfigure = nil
+		residual.To = ""
+		residual.ID = ""
+		residual.Operator = ""
+		residual.Cell = ""
+		if !reflect.DeepEqual(residual, Action{}) {
+			return fmt.Errorf("extra fields on reconfigure")
+		}
+		if a.Cell != "F3.1" || selectorRole(a.To, ids) != "lease" || a.ID == "" || a.Operator != "" && ids[a.Operator] != "operator" {
+			return fmt.Errorf("invalid reconfiguration action")
+		}
+		return nil
+	}
+	if a.Clock != "" {
+		residual := a
+		residual.Clock = ""
+		residual.ClockStep = 0
+		residual.Cell = ""
+		if !reflect.DeepEqual(residual, Action{}) {
+			return fmt.Errorf("extra fields on clock")
+		}
+		if a.Cell != "F3.2" || selectorRole(a.Clock, ids) == "" || math.IsNaN(a.ClockStep) || math.IsInf(a.ClockStep, 0) {
+			return fmt.Errorf("invalid clock step")
+		}
+		return nil
+	}
+	if a.To != "" || a.ID != "" || a.Operator != "" || a.ClockStep != 0 || a.Amnesia && a.Restart == "" {
+		return fmt.Errorf("extra v5 fields")
+	}
 	count := 0
 	for _, v := range []bool{a.Request != "", a.Write != "", a.Read != "", a.Crash != "", a.Restart != "", a.Partition != nil, a.Cut != nil, a.Drop != nil, a.Heal, a.Pause != "", a.Resume != ""} {
 		if v {
@@ -220,12 +308,15 @@ func validateAction(a Action, ids map[string]string) error {
 	if a.Token != "" || a.Value != "" {
 		return fmt.Errorf("workload fields on fault")
 	}
+	if a.Amnesia && (a.Cell != "F3.3" || selectorRole(a.Restart, ids) != "lease") {
+		return fmt.Errorf("amnesia requires F3.3 lease restart")
+	}
 	if a.Crash != "" || a.Restart != "" {
 		id := a.Crash
 		if id == "" {
 			id = a.Restart
 		}
-		if selectorRole(id, ids) == "" || a.Cell != "F1.1" {
+		if selectorRole(id, ids) == "operator" || selectorRole(id, ids) == "" || (a.Cell != "F1.1" && !(a.Restart != "" && a.Amnesia && a.Cell == "F3.3" && selectorRole(id, ids) == "lease")) {
 			return fmt.Errorf("invalid crash/restart")
 		}
 		return nil
@@ -279,13 +370,16 @@ func validateAction(a Action, ids map[string]string) error {
 }
 
 // triggerRef matches only events emitted after the trigger was armed.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, T1, T2, T3, A1, A2, E1, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func triggerRef(t Trigger, events []Event, armed int) (Ref, bool) {
 	if t.Start {
 		return Ref{}, true
 	}
 	for _, e := range events[armed:] {
-		fields := map[string]string{"event": e.Event, "client": e.Client, "key": e.Key, "token": fmt.Sprint(e.Token), "lifetime": fmt.Sprint(e.Lifetime), "grantor_term": fmt.Sprint(e.Term), "value": e.Value, "outcome": e.Outcome, "proc": e.Proc}
+		sortedMembers := append([]string{}, e.Members...)
+		sort.Strings(sortedMembers)
+		members, _ := json.Marshal(sortedMembers)
+		fields := map[string]string{"config_epoch": fmt.Sprint(e.ConfigEpoch), "inc": fmt.Sprint(e.Inc), "operator": e.Operator, "to": e.To, "what": e.What, "node_incarnation": fmt.Sprint(e.NodeInc), "incarnation": fmt.Sprint(e.Incarnation), "amnesia": fmt.Sprint(e.Amnesia), "clock": e.Clock, "restart": e.Restart, "crash": e.Crash, "step": fmt.Sprint(e.ClockStep), "epoch": fmt.Sprint(e.Epoch), "decided": fmt.Sprint(e.Decided), "members": string(members), "request_id": e.RequestID, "reason": e.Reason, "node": e.Node, "event": e.Event, "client": e.Client, "key": e.Key, "token": fmt.Sprint(e.Token), "lifetime": fmt.Sprint(e.Lifetime), "grantor_term": fmt.Sprint(e.Term), "value": e.Value, "outcome": e.Outcome, "proc": e.Proc}
 		if e.HighestBefore != nil {
 			fields["highest_before"] = fmt.Sprint(*e.HighestBefore)
 		}
@@ -297,7 +391,7 @@ func triggerRef(t Trigger, events []Event, armed int) (Ref, bool) {
 			}
 		}
 		if ok {
-			return Ref{e.Proc, e.Seq}, true
+			return Ref{e.Proc, e.Seq, e.Inc}, true
 		}
 	}
 	return Ref{}, false
diff --git a/impl/schedule_v2_test.go b/impl/schedule_v2_test.go
index 8e18351..805bcb0 100644
--- a/impl/schedule_v2_test.go
+++ b/impl/schedule_v2_test.go
@@ -16,7 +16,7 @@ func TestV2T1_FreshTrigger(t *testing.T) {
 		t.Fatal("historical event matched after arming")
 	}
 	events = append(events, Event{Proc: "n2", Seq: 1, Event: "Grant", Client: "c1"})
-	if ref, ok := triggerRef(trigger, events, 1); !ok || ref != (Ref{"n2", 1}) {
+	if ref, ok := triggerRef(trigger, events, 1); !ok || ref != (Ref{"n2", 1, 0}) {
 		t.Fatalf("fresh event not matched: %v %v", ref, ok)
 	}
 }
@@ -175,7 +175,7 @@ func TestV2T1T3_SynchronousEffects(t *testing.T) {
 // derives: C1.3, F1.2, E1, E2
 func TestV2E2_SafetyBeforeUnreachableEnd(t *testing.T) {
 	events := checkerFixture()
-	events = append(events, Event{Proc: "c1", Seq: 4, Event: "WriteAttempt", Client: "c1", Key: "k", Token: 7, Term: 2, Causes: []Ref{{"n1", 1}}}, Event{Proc: "c1", Seq: 5, Event: "WriteAck", Answers: &Ref{"c1", 4}, Client: "c1", Key: "k", Token: 7, Outcome: "accepted", Causes: []Ref{{"c1", 4}}})
+	events = append(events, Event{Proc: "c1", Seq: 4, Event: "WriteAttempt", Client: "c1", Key: "k", Token: 7, Term: 2, Causes: []Ref{{"n1", 1, 0}}}, Event{Proc: "c1", Seq: 5, Event: "WriteAck", Answers: &Ref{"c1", 4, 0}, Client: "c1", Key: "k", Token: 7, Outcome: "accepted", Causes: []Ref{{"c1", 4, 0}}})
 	evidence := RunEvidence{Reason: "end unreachable", Operational: "later resource problem"}
 	v := checkTrace(writeFixture(t, events), fixtureSchedule(), evidence)
 	if v.Clause != "C1.3" {
diff --git a/impl/transport.go b/impl/transport.go
index 5bab71b..33d46dd 100644
--- a/impl/transport.go
+++ b/impl/transport.go
@@ -1,4 +1,4 @@
-// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
+// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 package main
 
 import (
@@ -8,27 +8,28 @@ import (
 )
 
 // link names one directed connection; its reverse has independent fate.
-// derives: C1.1, C1.4, F1.2, F2.1, F2.2
+// derives: C1.1, C1.4, F1.2, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type link struct{ from, to string }
 
 // rpcTicket records endpoint incarnations at an admitted send.
-// derives: C1.1, C1.4, F1.1, F2.1, F2.2
+// derives: C1.1, C1.4, F1.1, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type rpcTicket struct {
 	path                         link
 	fromGeneration, toGeneration uint64
 }
 
 // RaftPacket is an already-sent library message with a logical delivery deadline.
-// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
+// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type RaftPacket struct {
-	message pb.Message
-	ticket  rpcTicket
-	due     time.Time
+	agreements []Agreement
+	message    pb.Message
+	ticket     rpcTicket
+	due        time.Time
 }
 
 // RaftNetwork is synchronous; only the event loop mutates routing and wire state.
 // The fixture inboxes test admission independently of protocol processing.
-// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
+// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 type RaftNetwork struct {
 	owner      *Engine
 	ids        map[string]uint64
@@ -40,22 +41,22 @@ type RaftNetwork struct {
 	problem    error
 }
 
-// derives: C1.4, F1.1, F1.2, F2.1, F2.2
+// derives: C1.4, F1.1, F1.2, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func newRaftNetwork() *RaftNetwork {
 	return &RaftNetwork{ids: map[string]uint64{}, names: map[uint64]string{}, boxes: map[string][]pb.Message{}, generation: map[string]uint64{}, down: map[link]bool{}}
 }
 
-// derives: C1.1, F1.1
+// derives: C1.1, F1.1, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (n *RaftNetwork) register(id string) []pb.Message {
 	n.generation[id]++
 	n.boxes[id] = []pb.Message{}
 	return n.boxes[id]
 }
 
-// derives: C1.1, F1.1
+// derives: C1.1, F1.1, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (n *RaftNetwork) remove(id string) { delete(n.boxes, id); n.generation[id]++ }
 
-// derives: C1.1, C1.4, F1.2, F2.1, F2.2, L2
+// derives: C1.1, C1.4, F1.2, F2.1, F2.2, L2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (n *RaftNetwork) setDown(down map[link]bool) {
 	n.down = map[link]bool{}
 	for p, v := range down {
@@ -66,7 +67,7 @@ func (n *RaftNetwork) setDown(down map[link]bool) {
 }
 
 // partition is the legacy fixture adapter; all failures accumulate until heal.
-// derives: C1.1, C1.4, F1.2, F2.1, F2.2, L2
+// derives: C1.1, C1.4, F1.2, F2.1, F2.2, L2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (n *RaftNetwork) partition(sides map[string]int) {
 	if sides == nil {
 		n.down = map[link]bool{}
@@ -82,7 +83,7 @@ func (n *RaftNetwork) partition(sides map[string]int) {
 }
 
 // admit fixes fate at send and never rechecks a down link at delivery.
-// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
+// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (n *RaftNetwork) admit(from, to string) (rpcTicket, error) {
 	p := link{from, to}
 	ticket := rpcTicket{p, n.generation[from], n.generation[to]}
@@ -95,7 +96,7 @@ func (n *RaftNetwork) admit(from, to string) (rpcTicket, error) {
 }
 
 // route exposes admission/inbox delivery for protocol-independent injector fixtures.
-// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2
+// derives: C1.1, C1.4, F1.1, F1.2, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (n *RaftNetwork) route(from, to string, m pb.Message) (rpcTicket, error) {
 	ticket, err := n.admit(from, to)
 	if err == nil {
@@ -105,7 +106,7 @@ func (n *RaftNetwork) route(from, to string, m pb.Message) (rpcTicket, error) {
 }
 
 // response is a distinct reverse send, used by the directional injector fixtures.
-// derives: C1.1, C1.4, F1.1, F2.1, F2.2
+// derives: C1.1, C1.4, F1.1, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (n *RaftNetwork) response(t rpcTicket) error {
 	if n.generation[t.path.from] != t.fromGeneration || n.generation[t.path.to] != t.toGeneration {
 		return fmt.Errorf("process replaced")
@@ -114,5 +115,5 @@ func (n *RaftNetwork) response(t rpcTicket) error {
 	return err
 }
 
-// derives: C1.1, C1.4, F1.1, F2.1, F2.2
+// derives: C1.1, C1.4, F1.1, F2.1, F2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func (n *RaftNetwork) issue() error { return n.problem }
diff --git a/impl/validate_v2.go b/impl/validate_v2.go
index e73d2ae..37b4801 100644
--- a/impl/validate_v2.go
+++ b/impl/validate_v2.go
@@ -1,13 +1,13 @@
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, A1, A2, T3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F2.1, F2.2, F1.3, A1, A2, T3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 package main
 
 import "fmt"
 
 // selectorRole checks alias roles without guessing their eventual incarnation.
-// derives: C1.1, C1.4, F1.1, F1.3, A1, A2, C2.1, C2.2
+// derives: C1.1, C1.4, F1.1, F1.3, A1, A2, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func selectorRole(id string, ids map[string]string) string {
 	switch id {
-	case "grantor", "non-grantor":
+	case "grantor", "non-grantor", "non-member":
 		return "lease"
 	case "holder":
 		return "client"
@@ -18,7 +18,7 @@ func selectorRole(id string, ids map[string]string) string {
 }
 
 // processRoles is shared by static and incremental compilation of concrete actions.
-// derives: C1.1, C1.4, F1.1, F1.3, A1, A2, C2.1, C2.2
+// derives: C1.1, C1.4, F1.1, F1.3, A1, A2, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func processRoles(s Schedule) map[string]string {
 	ids := map[string]string{}
 	for _, id := range s.Processes.Lease {
@@ -30,13 +30,16 @@ func processRoles(s Schedule) map[string]string {
 	for _, id := range s.Processes.Storage {
 		ids[id] = "storage"
 	}
+	for _, id := range s.Processes.Operators {
+		ids[id] = "operator"
+	}
 	return ids
 }
 
 // actionTarget identifies the one process-selector position outside partitions.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.3, A1, A2, T3, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.3, A1, A2, T3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func actionTarget(a Action) string {
-	for _, id := range []string{a.Request, a.Write, a.Read, a.Crash, a.Restart, a.Pause, a.Resume} {
+	for _, id := range []string{a.To, a.Clock, a.Request, a.Write, a.Read, a.Crash, a.Restart, a.Pause, a.Resume} {
 		if id != "" {
 			return id
 		}
@@ -45,9 +48,13 @@ func actionTarget(a Action) string {
 }
 
 // replaceTarget substitutes a frozen concrete process without changing operation.
-// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.3, A1, C2.1, C2.2
+// derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.3, A1, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func replaceTarget(a Action, id string) Action {
 	switch {
+	case a.To != "":
+		a.To = id
+	case a.Clock != "":
+		a.Clock = id
 	case a.Request != "":
 		a.Request = id
 	case a.Write != "":
@@ -68,7 +75,7 @@ func replaceTarget(a Action, id string) Action {
 
 // validateSequence rejects statically impossible aliases and definite A2 errors.
 // Alias-dependent transitions are compiled again against their frozen runtime IDs.
-// derives: C1.1, C1.4, F1.1, F1.3, A1, A2, T1, T3, C2.1, C2.2
+// derives: C1.1, C1.4, F1.1, F1.3, A1, A2, T1, T3, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 func validateSequence(s Schedule, ids map[string]string) error {
 	// 0 running, 1 crashed, 2 paused, 3 depends on a dynamic selector.
 	state := map[string]int{}
@@ -96,7 +103,7 @@ func validateSequence(s Schedule, ids map[string]string) error {
 				return fmt.Errorf("step %d: alias %s before any possible Grant", index+1, id)
 			}
 			// v2.2 A1 makes rejection without a prior selector crash normative.
-			// derives: C1.4, F1.1, A1, A2
+			// derives: C1.4, F1.1, A1, A2, C3.1, C3.4, C3.5, C3.7, C3.8, F3.1, F3.2, F3.3
 			if id == "non-grantor" && step.Do.Restart != "" && !nonCrashPossible {
 				return fmt.Errorf("step %d: restart non-grantor without a preceding selector crash", index+1)
 			}

````