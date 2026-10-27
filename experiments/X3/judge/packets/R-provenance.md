# Judge task: tupay X3, arm R implementation, provenance on P7 and P16

You are the judge. You belong to a model family that wrote neither side. Work only from the text below; do not read files, run commands or search, and do not look for anything else.

Background: in each of two arms, a TLA+ model and an implementation were written independently, by different model families, from the same inputs (contract v3, failure model v3, the schedule format and the observe schema, all given below). Arm A adapted earlier artifacts; arm R wrote new ones. The steward ran each side on shared schedules and on hold-out schedules (H11 to H14) that no author saw. A side reports PASS, FAIL <clause>, or UNEXPLAINED <reason> for a schedule.

**Item.** Arm R's implementation PASSes P7 and P16, but the steward's provenance check reports untraceable decisions in every one of their thirty runs (and on no other schedule), with the messages shown. The question is whether these are decisions whose recorded provenance is genuinely missing or wrong under the observe schema, or an artefact of the check, and where the locus is. Report `genuine_violation` as to the observe schema's provenance requirements.

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

===== FILE: arm R model-regen/README.md, whole =====
# model-regen: the TLA+ model side of tupay, built fresh from contract v3 and failure model v3

derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F1.1, F1.2, F1.3, F2.1, F2.2, F3.1, F3.2, F3.3

This directory is the model half of every pair in `tests/pairs-v4.md` (P1 to P33, P40 to P54, P58 to P63), written
from `contract/v3.md`, `failure-model/v3.md`, the schedule format (v2.2 to v5), the observability schema (v1 to v5)
and the steward's decision-replay check, and nothing else. Predictions were committed before any of it existed
(`PREDICTIONS.md`, commit `be79db9`). Results are in `RESULTS.md`; this file says what was built, how to run it, what
the model abstracts, how I read the inputs, the bounds and what they reach, and what I believe it cannot show.

## How to run

```
model-regen/run.sh P1                 # one schedule: prints PASS, FAIL <clause> or UNEXPLAINED <reason>
model-regen/run.sh --all              # every testbed/schedules/*.yaml (any name the format accepts)
model-regen/run.sh --mutations        # every pair's mutant on its pair's shared schedule
model-regen/run.sh P31 --spur 0 --max-term 3 --sims 4    # bounds and the number of random witness traces
```

Requirements: Java 21, `/opt/tlaplus/tla2tools.jar` (TLC 2.19), `uv` with `pyyaml==6.0.3` in its offline cache.
Environment: `TLC_HEAP` (default `10g`), `TLC_WORKERS` (48), `TLC_TIMEOUT` seconds per TLC run (5400),
`MODEL_SIMS` random witness traces per schedule (8). Generated TLC inputs go to `tmp/model-regen/<name>/` (never
committed); each run writes `observe/<run>.jsonl` (the counterexample if there is one, otherwise the shortest
behaviour that reaches the schedule's end) and `model-regen/results/schedules/<name>/` (verdict, TLC tails, traces,
the decision-replay report). `run.sh` resolves `testbed/schedules/<name>.yaml` and accepts any schedule in the format;
a schedule the format does not allow is reported `UNEXPLAINED rejected <reason>`.

One run of `run.sh <name>`:
1. `compile.py` turns the YAML into `MC.tla` (the schedule as TLA+ constants) and three TLC configurations.
2. TLC explores, breadth first and exhaustively within the bounds below, `SpecL` against every safety invariant
   and per-step property, and the liveness clauses in terminal form (see Liveness). A violation is `FAIL <clause>`
   with its counterexample exported; a terminal state with an unmet C1.4 or C3.4 obligation is `FAIL C1.4` or
   `FAIL C3.4`, or `UNEXPLAINED bound` if it sits at the term bound.
3. TLC finds the shortest behaviour that reaches the schedule's end (`NotEnded` as an invariant); none means
   `UNEXPLAINED end unreachable` (Rule E2: only when no violation was witnessed).
4. TLC samples `MODEL_SIMS` more behaviours to the end at random (simulation mode), for C3.5 across runs.
5. `observe/decision_replay.py` runs on every exported trace of the run; a report is `FAIL` with the clause it names
   (`C3.5` for equal inputs with unequal outcomes).

Files: `Lease.tla` (the model), `compile.py` (schedule compiler), `export.py` (TLC trace to `observe/<run>.jsonl`),
`run.py`/`run.sh` (runner; `run.sh --reach` runs the reach probes), `reach.py` and `report.py` (the reach table and
`RESULTS.md`), `mutations/make.py` (generates `mutations/Lease_P<n>.tla`,
one deliberate break per pair, listed in `mutations/MUTATIONS.md`), `tlc.sh` (a bare TLC launcher used while
building), `PREDICTIONS.md`, `RESULTS.md`, `results/`.

## The protocol followed

**Raft with joint consensus**: D. Ongaro and J. Ousterhout, "In Search of an Understandable Consensus Algorithm",
USENIX ATC 2014, sections 5 (leader election, log replication, safety) and 6 (cluster membership changes by joint
consensus); with **PreVote** and **CheckQuorum** from D. Ongaro, *Consensus: Bridging Theory and Practice*, PhD
thesis, Stanford University, 2014, sections 9.6 and 6.2. The model is a Raft abstraction in the style of published
atomic-quorum specifications: an election is one step, an AppendEntries and its acknowledgement are one step
(see Abstractions).

A grant is a Raft log entry `(client, token, lifetime, config_epoch, term)`; a membership change from epoch e to
e+1 is a joint entry (C_old,new) carrying the new members and the request; leaders also append Raft's no-op on
election when they inherit an undecided change (paper, section 8).

**Amnesic restart (F3.3).** The thesis (section 3.8) says a server that loses its persistent state cannot safely
rejoin under its old identity and can be added back as a new server through a membership change; until then it
behaves as a non-voting member (section 4.2.1). That is what the model does: an amnesic restart starts incarnation
i+1 with an empty log, term 0, no vote, and only the deployment's knowledge (its name, the lease nodes, the initial
configuration). Its acknowledgements are recorded but count toward no majority, its votes and pre-votes count for
nothing, and it may not start an election, until a commit that lists it and whose decider recorded this
incarnation's agreement re-admits it (contract v3, "Re-admission"). It stays in every denominator.

**Where the protocol is adapted to the contract** (each is a reading of the contract, listed again under
Interpretations):
- *Who decides.* Contract v3 makes a commit a decision recorded once, by one node (`decided: true` exactly once per
  epoch). In Raft every leader that advances its commit index "learns" commitment, so two leaders can each believe
  they decided the same entry. The model therefore names one decider per proposal:
  - a **grant** is decided only by the leader that created its entry, from acknowledgements in its own term (Raft's
    direct commitment rule); an entry of an earlier term that a later leader commits indirectly is never decided
    and its token is dead (the client asks again);
  - a **configuration** is decided by the request's **receiver**, acting as a distinguished learner (L. Lamport,
    "Paxos Made Simple", SIGACT News 2001, section 2.3): a leader that knows the joint entry is committed (it
    counted joint majorities over an entry of its own term at or after it) hands the receiver the agreements it
    counted, possibly relayed by one node; the receiver records them as `Agreed` and decides when they form
    eligible majorities of the old and the new membership (C3.8).
- *C_new is implied.* Raft appends C_new after C_old,new commits; here a node uses the new membership alone once it
  knows epoch e+1 decided, and the joint one while the entry is in its log undecided. A leader not in the new
  membership steps down when it learns the decision.
- *Grants pause during a change.* A leader proposes no grant while a configuration entry in its log is undecided,
  and a grant is decided only under the decider's current configuration (C3.7).
- *A grant proposal carries its Raft entry term* (the contract's proposal fields plus `term`), so two entries with
  one token from different leaders are different proposals.
- *Requests reach a leader through a member.* A non-leader that receives a client's request or an operator's
  request passes it to a leader it reaches (directly, or through one member that reaches one), as Raft followers
  redirect; the receiver stays the node that records the outcome and answers the operator. A grant reply goes
  straight to the client, or back through the node that forwarded the request if the decider cannot reach the
  client (H9).

## Abstractions (what the model does not represent, and why)

- **Messages between lease nodes are atomic.** An AppendEntries and the follower's acknowledgement are one step,
  taken only while leader→follower is up; the acknowledgement is lost if follower→leader is down at that moment.
  Elections (timeout, pre-vote, votes, win) are one step with every member that would vote. A higher term carried
  on a message (an AppendEntries reply or a RequestVote) is its own step (`TermProp`). So a message between lease
  nodes is never delivered after a link change, never duplicated, never reordered with others between the same
  pair. This is the main abstraction; see Limitations.
- **Repeated timeouts are collapsed.** A needed election takes the smallest term at which a quorum would vote; a
  pre-vote rejected for a stale term teaches the higher term (as etcd's PreVote does), so terms do not gate it.
- **Client and operator messages.** A client's request and an operator's reconfiguration request arrive in the step
  they are sent, if the link is up (lost otherwise; a client whose request survives nowhere sends it again, which
  abstracts its retry timer). A receiver's reply reaches its operator in the step it is sent, or is lost and resent.
  A grant reply to a running client arrives in the step it is sent; to a paused client it stays in flight until the
  client resumes. Writes, reads and their replies are explicit in-flight messages (they may be reordered and may
  arrive after a link goes down); storage holds its replies in an outbox that a crash empties.
- **Messages to a crashed process are lost**; a restarted process does not receive what was sent while it was down.
- **No clocks.** No protocol decision reads a clock: the grantor does not wait for expiry (the contract allows
  non-exclusive grants) and Raft's timers are abstracted by nondeterminism. A clock step (F3.2) is recorded as a
  `Fault` with its size and changes no state, so every clock value is equivalent to every other for this model;
  "between steps clocks advance by any number of ticks" is covered because nothing depends on the number. The
  mutants that need a clock (P32, P41, P44, P47, P50, P53, P59, P62) add one.
- **Storage** is one process with a durable ledger and value (contract v3).
- **Integers** are TLA+ integers; TLC's term bound keeps them small; `Overflow` never occurs and is not modelled.

## Interpretations of the inputs

Each of these is a place where the inputs left a choice. None changes an input.

1. *Decider per proposal* (above). Consequence: a configuration whose receiver restarts amnesic before deciding is
   never decided (see Findings, P63).
2. *Agreed records.* A grant's decider records `Agreed` for each agreement to an undecided entry of its own term when
   it receives it (counted toward the grant's epoch if eligible, else `[]`); agreements arriving after the decision
   are not recorded. A configuration's receiver records `Agreed` for each agreement handed to it while its request
   is pending, with `counted_toward` the epochs among e, e+1 in which it is eligible (an amnesic incarnation's is
   `[]`, the re-admission evidence). Every `Agreed` names the node's `Agree` in `causes` (matched by node,
   incarnation and proposal).
3. *Grant inputs.* `agreed` (every recorded `Agreed`, by ref), `members` and `config_epoch` (the decider's current
   configuration), `grantor_term` (the decider's term), `last_token` (the highest token in the decider's log before
   the entry: what it knew when it chose the token). No grant reads a clock, so `clock` and `last_grant_at` are
   never recorded. No extra input names are used (`--extra-inputs` is not needed).
4. *Which epoch a request would occupy* is the receiver's current epoch plus one when it records the request. A
   leader starts it only as that epoch; if the receiver learns that epoch committed to another request it refuses
   `superseded` (the operator may send it again). `invalid` then `busy` are decided when the request is recorded.
5. *C1.1 across configurations* is checked as (a) no two grants share a token, (b) a higher epoch carries a higher
   token, and (c) in every node's log, decided grants appear in increasing token order (a node agrees in log order
   and decided entries are never removed); the trace-level form of (c) is checked by decision replay, part 2.
   Two grants with one term must come from one node incarnation, and at most one leader holds a term at a time.
6. *C1.2 and C2.1, "the highest token storage has accepted"*, are read against the history of accepted writes, not
   only the current ledger, so a ledger that loses its value is caught. They are "only if" clauses: storage's
   rejecting *only* below the ledger is v3's fixed rule, which the contract says C1.2 and C2.1 permit and C3.5 needs,
   so that half is checked under C3.5 (`C3_5`), not under C1.2/C2.1. (My first invariants checked it under C1.2 and
   C2.1; the P43 and P44 mutants, which make storage reject on an unrecorded input, showed the misattribution.)
7. *C1.4 and C3.4 premises* are read as the schedule format's Rule L3 extended: after the last fault step of the
   schedule has been taken; the globally committed configuration (the highest decided epoch in the run); an
   eligible majority of it (and, for C3.4(b), of the requested set) up and pairwise connected with the receiver or
   with storage and the requester; no reconfiguration request pending at an up node for C1.4.
8. *Where the last fault depends on the obligation.* In P12 the last fault (the resume) is triggered by the grant
   to c2, and in P10 the last fault (the grantor's crash) follows a step triggered by the grant to c2. If c2 is never
   granted, the last fault never happens and C1.4 owes nothing for c2 (it is owed only after the last fault). The
   model reports such a run as `UNEXPLAINED end unreachable`, not `FAIL`.
9. *Spurious elections* (asynchrony) are allowed only before the last fault: after it, messages arrive within a
   bound and a node that hears a leader does not time out.
10. *Selectors.* `grantor`, `holder` and `non-member` are resolved when the trigger fires, from the most recent
    `Grant` and the highest decided commit in the run; every `non-grantor` (and `non-member`) choice is explored;
    several `non-grantor` occurrences in one step denote one node. A schedule that names `grantor`/`holder` before
    any `request` step is rejected.
11. *`quiescent`* holds when every step has been taken, no message is in flight to a running process, storage's
    outbox is empty, no running client is waiting for a grant and no request is pending at an up receiver.
12. *The schedule's `bound: {events: N}`* is not used; TLC's bounds below replace it, and are reported.
13. *Incarnations in records*: a lease node's `inc` counts its amnesic restarts; a client's or storage's counts its
    restarts (schema v5); `env` and operators are 0.
14. *Values*: storage's initial value `null` is `"null"` in the model and `null` in the trace.
15. *Clock steps* are compiled to ticks (`step × L`) and must be whole (the format's rule).
16. *Removed nodes* keep running and keep their state (failure model, Configuration locus); they stop campaigning
    once they know they are not members.

## Bounds, and what each schedule must reach

Every exhaustive run is bounded by:
- **MaxTerm**: the highest term reachable before the last fault: `1 + L + Spur0`, where L counts the schedule's
  leader-loss steps (each run of consecutive lease-node crashes once, each partition, cut or drop, and one for any
  reconfiguration). After the last fault the cap rises by one term per lease node, so that elections the faults
  force can still happen; a terminal state stuck at the cap is reported `UNEXPLAINED bound`, never `PASS` or `FAIL`.
- **Spur0 = 1**: one spurious election (a timeout while a leader is still reachable) before the last fault.
- The schedule itself: its steps, processes and requests (tokens and grants grow only with requests and terms).
No other constraint is applied; there is no depth bound. `RESULTS.md` lists, per schedule, what it must reach
(epochs, restarts, amnesic restarts, clock steps and their sizes in ticks, grants, the elections its faults force),
the bounds it ran at, the number of states explored, what its shortest witness reached, and **reach probes**: TLC
reachability checks, at the same bounds, of every epoch the schedule's valid requests allow (`ProbeEpoch(k)`), of one
grant per request (`ProbeGrants`), and of a re-admitting commit where an amnesic restart is followed by a request
(`ProbeReadmit`). Every probe that the schedule allows is reachable; the three "re-admission: unreachable" (P33, P42,
P60) are schedules whose later request omits the amnesic node, so re-admission is impossible there, as it should be.
A schedule whose witness reaches its end, and whose probes are reachable, shows that the bounded space contains the
behaviours the schedule asks for.

## Liveness (C1.4, C3.4), and the fairness it rests on

C1.4 and C3.4 are checked in **terminal form**. Every action of the model moves the state forward in a well-founded
order (terms, logs, decided-configuration knowledge, the schedule position, consumed messages, histories; a leader
that steps down can lead again only in a higher term). So the reachable state graph has no cycle, every behaviour ends in a terminal state where nothing is
enabled, and at a terminal state weak fairness of every action holds vacuously. Under weak fairness of every action,
"eventually P" then holds in every behaviour if and only if P holds in every reachable terminal state. The checked
specification is `SpecL == Init /\ [][Next \/ Idle]_vars` with `Idle` (stuttering) enabled exactly when no
obligation is unmet; TLC's deadlock check then finds exactly the terminal states that leave a C1.4 or C3.4
obligation unmet, and a one-state TLC run classifies which (`Stuck14`, `Stuck34`, `StuckBound`).

I validated the terminal form against TLC's temporal check of `C1_4` under explicit fairness (`LiveSpec`,
`live.cfg`, `-lncheck final`) on small schedules (`results/liveness-crosscheck.txt`). The two agree on every case
tried: unmutated P10, P11, P25, P26, P54, H9 and H10 hold; the P11, P25, P26 and P54 mutants and the redesigned P10
mutant are violated; the original P10 mutant holds under both (interpretation 8). The temporal check is ~1,000 times slower
here (`ENABLED` for ~80 fairness conditions), which is why it is not the default.

The fairness the terminal form amounts to is weak fairness of every action. Every action of the model is enabled by
the acting process's own state and by links that are up at that moment: an AppendEntries needs leader→follower up,
an election needs the candidate and its voters connected, a forward needs the link to the leader, a delivery needs
the message in flight to a running process. No action requires hearing from a peer across a link that is down, and
the actions whose enablement is "nothing was heard" (an election timeout when no leader is heard; CheckQuorum's
step-down when a majority is not heard) depend only on the acting node's own state. Spurious timeouts are not fair
and stop at the last fault. Liveness therefore rests on: weak fairness of every action (justified by "after the last
fault, a message between two connected processes is delivered within a bound", failure model v3) and the absence
of spurious elections after the last fault (the same clause: timers longer than the bound). No liveness result
rests on fairness across a down link.

## Mutations

`mutations/make.py` generates one copy of `Lease.tla` per pair with one deliberate break on the enforcing path of
the pair's clause, marked `\* mutation: P<n>` at the break and named in the module header; `mutations/MUTATIONS.md`
lists them. Mutants that need state the model does not keep add it as `aux` (clock offsets for the F3.2 pairs;
pending client operations for the C1.3 and C2.2 pairs that fabricate an outcome). For C3.5 the break makes a
decision consult an input it does not record (storage reading a link state or its own clock; a commit reading
incarnations it did not record), which both the model's `C3_5` rule and the steward's decision-replay check catch.
A mutant may break more than its pair's clause, and TLC stops at the first violation it meets; in mutation mode the
runner then checks the pair's own clause alone as well and reports both (`FAIL C1.1; FAIL C3.7 (pair clause,
checked alone)`). Mutants redesigned after a run are recorded in `mutations/MUTATIONS.md` and below. Results are in
`RESULTS.md`.

## Development history before the first version (recorded, not hidden)

The model failed shared schedules twice while it was being built; both times the old behaviour misread the
published protocol (and so C1.4/C3.4), and the counterexamples are kept under `results/dev-history/`:
- **P10, FAIL C1.4**: a node left with a vote for itself in term 2 by a spurious timeout could not vote for anyone in
  term 2, and my atomic election only tried term+1. Raft times out again. Fix: an election takes the smallest
  winnable term (`Elect`).
- **P42, FAIL C3.4**: a pre-vote was refused when the voter's term exceeded the pre-candidate's term + 1, leaving
  no node able to elect after the leader that held the change restarted amnesic. In Raft's PreVote the rejection
  carries the higher term and the pre-candidate retries. Fix: terms do not gate the pre-vote.
Other changes while building reduced state space without changing behaviours the clauses distinguish (atomic
forwarding, immediate client/operator messages, a VIEW without the last step's events, the terminal form of
liveness), or made spurious elections atomic. Mutations redesigned after a run: P10 (the first design, unanimous
grants, could not fail: interpretation 8; moved to unanimous elections); P63 (first "the old majority is not
required": ineffective on P63, where every majority of the new set contains one of the old; then "the receiver
counts an amnesic agreement": ineffective, because the leader hands over agreements only after counting eligible
majorities itself; finally both the leader's commit count and the receiver's decision judge eligibility by node).
All of this is in the commit history.

## Findings

- **P63: FAIL C3.4, predicted.** In the counterexample n1 (leader) appends r1's joint entry, whose receiver is
  n2 (incarnation 0); n2 restarts amnesic; the entry is then replicated and committed, counted through n1, n3 and n4
  (n2#1 acknowledges too, uncounted); its only decider no longer exists, the change stays undecided in every log, the leader cannot start r2, and r2
  (pending at n1, every premise of C3.4(b) holding) is never committed or refused. In the world I predicted
  (the entry committed before the receiver's amnesic restart, its decision possibly recorded and not yet heard of)
  I believe no protocol keeps both C3.1's single decision per epoch and C3.4: no live process can tell "decided
  and not yet announced" from "never decided", so deciding again risks a second decided record for epoch 1, taking
  epoch 1 for r2 risks two configurations for it, and waiting blocks r2. In the world TLC shows the entry was not
  yet committed when the receiver restarted, so a protocol that could abandon an appended joint entry would pass;
  Raft cannot. The verdict stays FAIL (unexplained until a judge discriminates); it is a property of the contract's
  single-decider rule under F3.3 at the decider as much as of this design.
- **P10 and P12: C1.4 is vacuous where the last fault waits on the grant** (interpretation 8); their mutants cannot
  fail C1.4 by design of the schedule. (The P10 mutation was moved to elections, which bite after the last fault.)

## Declared limitations

Shapes of schedule this model would fail or could not check, and why I left them:
- **Stale messages between lease nodes.** Because lease-to-lease messages are atomic, the model cannot show a
  failure that needs an AppendEntries, vote or acknowledgement sent before a link change and delivered after it, a
  duplicated one, or one reordered behind a later one. Raft is designed for those, and modelling them made the
  state space unmanageable (P1 alone exceeded 25 million states at depth 18).
- **Duplicated client, storage and operator messages** are not modelled (sets, not bags).
- **Bounded asynchrony.** One spurious election before the last fault, and MaxTerm as above. A failure needing two
  spurious elections, or more elections than the faults force plus one, is outside the space.
- **No clocks in the protocol.** A schedule whose failure depends on a decision reading a clock cannot fail here
  (none does in this design); conversely a clock-based lease protocol is not what is modelled.
- **Liveness under the terminal form** relies on the reachable graph being acyclic (argued above; validated against
  the temporal check on seven small schedules and six mutants; not proved). A livelock that keeps raising terms after the last
  fault is reported `UNEXPLAINED bound`, not `FAIL`.
- **C3.5 across runs** is checked over the traces the runner exports (one shortest witness or counterexample plus
  `MODEL_SIMS` random behaviours per schedule), not over every behaviour; within the model, every decision of every
  explored behaviour is checked against the rule of its recorded inputs (`C3_5`).
- **Large schedules take minutes**: P31 (5 nodes, two operators) ~9 million states, P52 (6 nodes) ~12 million;
  `run.sh --all` takes about an hour on 48 cores. A larger schedule (more lease nodes, more requests, more faults)
  may exceed `TLC_TIMEOUT` and is then reported `UNEXPLAINED bound (TLC time limit ...)`.
- **The inputs I could not use.** This checkout also contains `contract/v2.md`, `failure-model/v1.md` and `v2.md`,
  `tests/pairs-v1.md` to `v3.md`, `pyproject.toml`, `uv.lock` and `scripts/hooks/`, which the brief says are absent;
  I did not read them (I saw the first lines of `pyproject.toml` while checking the toolchain, and nothing else).

===== FILE: arm R impl-regen/README.md, whole =====
# Fresh Go lease implementation

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F1.1, F1.2, F1.3, F2.1, F2.2, F3.1, F3.2, F3.3 -->

Run `impl-regen/run.sh P1 --seeds 3 --reps 10`, `impl-regen/run.sh --all`, or `impl-regen/run.sh --mutations`. Go is built without third-party modules. Python 3 and PyYAML compile YAML to JSON; Go executes the service and faults. Traces and replay reports live under `impl-regen/observe/`. Temporary binaries and compiled schedules live under `impl-regen/tmp/` and are never committed. Predictions are in PREDICTIONS.md. Runs are sampled executions, not a proof.

## Protocol and adaptations

<!-- derives: C1.1, C3.1, C3.7, C3.8, F3.3 -->

The intended agreement basis is Leslie Lamport, *Paxos Made Simple* (2001), sections 2 and 3, https://lamport.azurewebsites.net/pubs/paxos-simple.pdf, with joint old/new majorities for membership as in Diego Ongaro and John Ousterhout, *In Search of an Understandable Consensus Algorithm* (2014), section 6, https://raft.github.io/raft.pdf. The current engine serializes proposals and records durable promises and accepted proposals on acceptors. It records each counted agreement individually. Amnesic incarnations lose promises and accepted state and cannot count until a configuration re-admits them. A configuration may collect their uncounted agreements to establish re-admission.

**Declared protocol limitation:** this initial implementation does not yet implement full Paxos recovery (prepare responses must adopt the highest accepted proposal), distributed leadership, or a replicated ordered log. The simulation driver holds committed membership, last token and ballot allocation centrally; these values survive simulated faults. This is stronger than a real lease node's available knowledge under F1.1/F3.3. It is not a complete implementation of either cited protocol and therefore does not satisfy the brief's published-protocol requirement. Evidence passing alone must not be taken as satisfying that requirement. No external Raft library is used; no module cache was present at the reported GOPATH.

## Interpretations and declared limitations

<!-- derives: C3.5, C1.4, C3.4, F1.1, F1.2, F1.3, F2.1, F2.2, F3.1, F3.2, F3.3 -->

* The scheduler advances integer ticks, samples queued message delivery using the seed, and prioritizes an enabled schedule action. Agreement collection is currently atomic; faults triggered by Agree or Agreed run after the decision, not between agreements and decision. This restricts explored interleavings and can prevent later triggers from firing.
* Directed link fate is fixed at send. Paused recipients retain queued messages; crashed recipients currently retain queued messages too. Ordinary restart preserves durable state. Clients discard grants on restart. Storage retains ledger and value.
* Grant does not wait for lease expiry or read any clock. Clock faults change the named local clock; resume advances run time by more than L. Local clocks are not consulted by baseline decisions.
* Reconfiguration requests are queued at the receiver, with invalid-before-busy refusal. A lost operator send is not retried. Propagation and acknowledgments are queued messages. Supersession of a pending request by another receiver's committed configuration is not yet implemented.
* Selectors resolve on trigger firing; non-grantor uses sorted deployment order and restart refers to its last selected crash target. The compiler validates process state dynamically; it is not a complete static validator of arbitrary YAML.
* Quiescence is limited to outstanding work tracked by this driver. At a stall, the liveness check enumerates directly connected eligible majorities only after every schedule action has executed. It cannot establish a violation while an earlier trigger is unreachable. Such runs are UNEXPLAINED.
* Machine integers have no overflow guard yet; schedules exceeding their capacity cannot be checked. No production networking, disk fsync, or operating-system process isolation is claimed: faults affect Go process-state objects in a deterministic discrete-event testbed.
* Mutation switches are copies at the enforcing path selected by the pair's clause; related pairs share a switch. C3.5 changes the grant using an unrecorded tick and requires cross-run replay. Mutation effectiveness is measured, not assumed.

## Records

<!-- derives: C3.5, F3.2 -->

This README is append-only after its first commit. Limitations above are part of the first version, not excuses for a passing verdict. Later findings and corrections are appended. The artifact's full suitability requires protocol review as well as trace checks.

## First baseline results and corrective interpretation

<!-- derives: C1.1, C1.4, F1.1, F1.3 -->

Outcome-informed, after first version: 177 runs (59 schedules, seeds 1–3, one repetition) produced 168 PASS and nine UNEXPLAINED: P3 and P12 reported an unresolved holder, P52 reported end unreachable despite issuing c2's grant. Original traces and batch-1.json remain unchanged. Predictions of PASS were wrong for those runs. A1 is interpreted to make `holder` resolve from the most recent Grant's client, including while delivery of that grant is queued; otherwise the shared P3/P12 triggers cannot identify their holder. E1 explicitly excludes crashed and paused processes from quiescence; the original queue-length check misread that rule by counting delivery to crashed n4 in P52. Corrections will retain queued messages but ignore inactive recipients when deciding quiescence. Neither correction is evidence of a complete agreement protocol.

## Mutation scoring correction and next protocol revision

<!-- derives: C1.4, C3.4, C3.5, C3.7, C3.8, F1.1, F3.1, F3.3 -->

Outcome-informed: the first mutation batch is batch-2.json. Its reporter incorrectly matched the replay summary text `0 UNEXPLAINED inputs` as a conflict. It also compared different mutated artifacts together. Both are scoring bugs; evidence reports are retained. A deadlocked state with an unanswered requester and a connected eligible majority can witness liveness even when later schedule actions wait on the missing grant. Restricting this check to schedules whose actions had all run misread C1.4/C3.4. These corrections affect reporting, not service decisions. The C3.7/C3.8 mutations now withhold majority evidence on the decision path, and the ack mutations deliberately acknowledge at the attempt before storage decides; first-batch mutation results record these revised paths.

Planned protocol correction (informed by source review, not a counterexample): replace the central committed-state oracle with replicas and per-slot Paxos state. The published basis is van Renesse and Altinbuken, *Paxos Made Moderately Complex*, ACM Computing Surveys 47(3), 2015, https://paxos.systems/paper/ , replicated state machine and reconfiguration with window size one. A configuration command in slot s selects the acceptors for slot s+1. C3.8 additionally requires the new membership's majority to accept that configuration command. This is a stricter acceptance requirement, not a new way to choose a value. Retain phase-one highest-accepted-value adoption, per-slot promises, and replica state transfer. Atomic agreement phases remain a declared testbed sampling restriction.

## Replica protocol revision and remaining limits

<!-- derives: C1.1, C1.4, C3.1, C3.4, C3.5, C3.7, C3.8, F1.1, F2.1, F2.2, F3.1, F3.2, F3.3 -->

The revision in protocol.go supersedes the initial central-allocation implementation. Service decisions now use replica-local committed logs, per-slot acceptor promises/accepted ballots, and unique node-ranked ballots; global Token/Epoch/Members are observation and workload-selector state only. Replica state transfer copies a chosen prefix through a direct round trip. A proposer prepares the next slot and adopts the highest accepted value; already decided values are learned without reissuing their Grant. Membership commands take effect in the following slot (window one), require old and new eligible majorities, and transfer prior grant state to new replicas. The receiver retains its identity when forwarding and acknowledges its own learned commit. Pending requests superseded at their receiver are refused with that commit as an input. Learned re-admissions are local replica state, and amnesia erases all replica and acceptor state, including that information. Ordinary restart preserves it.

This implements the cited Paxos replicated-state-machine protocol within a deliberately restricted discrete-event scheduler. Prepare/accept/decision/learning at reachable acceptors are one atomic scheduling operation. Thus an accepted-but-undecided value cannot arise in this testbed; the recovery guard refuses to overwrite such a value if introduced. A schedule requiring a fault between an individual agreement and the decision is sampled with the action after that decision (T2); no coverage claim is made for every interleaving. This restriction, lack of production disk/network/process isolation, and incomplete static validation remain declared limitations. They were left to keep a small executable testbed with reviewable protocol state; they limit evidence beyond these executions.

The original README's statements about central allocation, missing replicated log, missing supersession, and requiring every step to execute before liveness checks describe the first version and no longer describe this revision. Machine token/term/epoch increments now guard against wrap and emit Overflow; incarnation increment is guarded on restart. Clocks advance for every process including paused ones and signed fractional lifetime steps are accepted only if they yield whole ticks. The service does not consult clocks when deciding grants or storage operations. No extra decision input names are used. For the C3.5 mutations only, an unrecorded scheduling seed changes the chosen token, so replay of equal recorded inputs discriminates the deliberately introduced violation.

Runner corrections preserve original trace names and add an attempt suffix on subsequent runs. Per-run storage/provenance/ack checks are independent of the Go service; steward decision replay also runs per trace and across runs of the same artifact. Mutations are separate artifacts and are compared within each pair, never mixed across different mutation switches. A demonstrated input conflict caused by the explicitly declared C3.5 mutation is reported FAIL C3.5; other unexplained input conflicts remain UNEXPLAINED.

## Final validation batch interruption

<!-- derives: C3.5, F1.1 -->

Outcome-informed: the first 3×10 baseline invocation was interrupted by a runner infrastructure race when a concurrent mutation invocation rebuilt the shared temporary engine path. Python reported FileNotFoundError while launching that engine. Completed and partial traces are retained, and this invocation has no aggregate PASS verdict. The runner now creates a separate temporary build directory per invocation. This is a runner correction, not a change to service decisions. A fresh full batch will supply the reported final validation.

<!-- derives: C3.7, C3.8, F3.1, F3.2, F3.3 -->

Mutation path correction after source review: withholding decision inputs alone would demonstrate missing evidence, not necessarily a missing majority in the actual service. Final C3.7/C3.8 mutants therefore accept at one node and bypass the majority gate before issuing the decision. They break the clause's enforcing path itself. Earlier mutation traces remain as recorded.

## Final mutation form and additional schedule shape

<!-- derives: C3.5, C3.8, F3.1, F3.2 -->

The final C3.5 mutant reads the deciding node's local clock without recording it. Initial local clock offsets are chosen by seed parity (allowed by F3.2's unrelated clocks); baseline decisions ignore them. This supersedes the direct seed-read mutant and conforms to pairs-v4's clock-read mutation requirement. Its dedicated final runs are reported separately. A receiver outside both old and requested membership now learns the chosen configuration by a separate queued transfer before acknowledging; it stays pending until that learning. This extends the forwarding path beyond P61's receiver, which is included in the requested membership.

Remaining liveness limitation: a reconfiguration reply lost before a heal is not retransmitted. The declared shape is an operator-to-receiver round trip cut after decision and healed later; C3.4's eventual acknowledgment can fail there. The existing shared runs do not establish that shape. Declaring it does not waive the clause. Process-state validation is dynamic and compile-time validation is partial. These limitations should be tested by the steward; no extra private schedules were authored.

## Term recovery correction

<!-- derives: C1.1, F3.3 -->

Source-review correction: amnesia must erase the replica's remembered ballot term too, not just its per-slot promises. Snapshot learning now recovers the maximum chosen ballot from the log before a replica allocates a leadership term, and amnesia resets its term. This prevents reuse of a leadership period after disk replacement or transfer to a previously unused node. This was identified by inspecting the F3.3 reset path, not by a shared-schedule failure. Targeted final checks cover transfer and amnesic restart paths.

## Completed validation

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, C3.1, C3.4, C3.5, C3.7, C3.8, F1.1, F1.2, F1.3, F2.1, F2.2, F3.1, F3.2, F3.3 -->

See RESULTS.md for the completed full 3-seed × 10-repetition results and every final batch. Full baseline: 1,770 PASS. Full mutations: 1,620 FAIL on the predicted clauses. No flaky seed groups. Final clock mutants add 90 expected failures; final recovery and forwarding refinements add 180 baseline passes. All earlier contrary results and the interrupted invocation remain preserved. Runner trace and batch creation now reserve unique paths exclusively to protect append-only records during concurrent invocations. No tmp files are committed.

===== FILE: observe/provenance_check.py (the steward's check) =====
#!/usr/bin/env python3
"""Steward's independent check of the observability layer.
derives: C1.1, C1.2, C1.3, C2.1, C2.2, F1.1, F1.2, F1.3 (observe/schema.md v2 and v3: the provenance question, writes and reads, and acks' answers)

For every WriteAccept and WriteReject in an observe file: follow `causes`
backwards and require that the chain reaches a Grant whose token equals the
decision's token, and that grantor_term on the decision equals that Grant's.
Also require highest_before to be present. Prints one line per file.
"""
import json, sys, glob

def check(path):
    recs = {}
    order = []
    for line in open(path):
        line = line.strip()
        if not line: continue
        r = json.loads(line)
        recs[(r['proc'], r['seq'])] = r
        order.append(r)
    decisions = [r for r in order if r['event'] in ('WriteAccept', 'WriteReject', 'ReadAccept', 'ReadReject')]
    bad = []
    for d in decisions:
        if 'highest_before' not in d: bad.append((d, 'no highest_before')); continue
        seen, stack, found = set(), list(d.get('causes', [])), None
        while stack:
            c = stack.pop(); k = (c['proc'], c['seq'])
            if k in seen: continue
            seen.add(k)
            r = recs.get(k)
            if r is None: bad.append((d, f'dangling cause {k}')); break
            if r['event'] == 'Grant' and r.get('token') == d.get('token'):
                found = r; break
            stack.extend(r.get('causes', []))
        if found is None:
            if not any(b[0] is d for b in bad): bad.append((d, 'no Grant with this token reachable'))
        elif found.get('grantor_term') != d.get('grantor_term'):
            bad.append((d, f"term mismatch: decision {d.get('grantor_term')} grant {found.get('grantor_term')}"))
    # v3 addendum: every ack's `answers` names an attempt in the trace, and the ack's causes chain reaches it.
    acks = [r for r in order if r['event'] in ('WriteAck', 'ReadAck')]
    for a in acks:
        ans = a.get('answers')
        if not ans:
            bad.append((a, 'no answers field')); continue
        k = (ans['proc'], ans['seq'])
        t = recs.get(k)
        if t is None or t['event'] not in ('WriteAttempt', 'ReadAttempt'):
            bad.append((a, f'answers {k} is not an attempt in the trace')); continue
        seen, stack, hit = set(), list(a.get('causes', [])), False
        while stack:
            c = stack.pop(); ck = (c['proc'], c['seq'])
            if ck in seen: continue
            seen.add(ck)
            if ck == k: hit = True; break
            r = recs.get(ck)
            if r: stack.extend(r.get('causes', []))
        if not hit: bad.append((a, f'causes chain does not reach answered attempt {k}'))
    return len(decisions) + len(acks), bad

tot = 0
for path in sys.argv[1:]:
    n, bad = check(path)
    tot += len(bad)
    status = 'OK' if not bad else 'FAIL'
    print(f'{status} {path}: {n} decisions, {len(bad)} untraceable')
    for d, why in bad[:5]:
        print(f'   {d["event"]} proc={d["proc"]} seq={d["seq"]} token={d.get("token")}: {why}')
sys.exit(1 if tot else 0)

===== FILE: provenance_check.py output on arm R's implementation traces: each distinct message (trace names and repetition-specific numbers removed) with the number of traces it occurs in, by rule =====
20 x WriteAccept proc=s seq=N token=1: no Grant with this token reachable
60 x WriteAck proc=c1 seq=N token=1: answers ('c1', 2) is not an attempt in the trace
1 x exit 1
30 x P16: 8 decisions, 1 untraceable
10 x P7: 6 decisions, 1 untraceable
20 x P7: 6 decisions, 2 untraceable

===== FILE: schedule P7.yaml =====
schedule: P7
derives: [C1.3, F1.1]
processes:
  lease: [n1, n2, n3]
  clients: [c1, c2]
  storage: [s]
steps:
  # derives: P7 (C1.3, F1.1). Storage crashes between receipt and ack, then the client crashes after an accept; no client is told success for a write storage did not accept.
  - {at: start, do: {request: c1}}
  - {at: {event: Grant, client: c1}, do: {write: c1, value: v1}}
  - {at: {event: WriteAttempt, client: c1}, do: {cell: F1.1, crash: s}}
  - {at: start, do: {cell: F1.1, restart: s}}
  - {at: start, do: {write: c1, value: v2}}
  - {at: {event: WriteAccept}, do: {cell: F1.1, crash: c1}}
  - {at: start, do: {cell: F1.1, restart: c1}}
  - {at: start, do: {request: c2}}
  - {at: {event: Grant, client: c2}, do: {write: c2, value: v3}}
end: quiescent
bound: {events: 200}

===== FILE: arm R implementation trace impl-regen/observe/P7-seed1-rep1-attempt4.jsonl =====
{"causes":[],"decided":false,"epoch":0,"event":"ConfigCommitted","inc":0,"members":["n1","n2","n3"],"node":"n1","proc":"n1","readmits":[],"request_id":null,"run":"P7","seq":1,"side":"impl"}
{"causes":[],"decided":false,"epoch":0,"event":"ConfigCommitted","inc":0,"members":["n1","n2","n3"],"node":"n2","proc":"n2","readmits":[],"request_id":null,"run":"P7","seq":1,"side":"impl"}
{"causes":[],"decided":false,"epoch":0,"event":"ConfigCommitted","inc":0,"members":["n1","n2","n3"],"node":"n3","proc":"n3","readmits":[],"request_id":null,"run":"P7","seq":1,"side":"impl"}
{"causes":[],"client":"c1","event":"Request","inc":0,"key":"k","proc":"c1","run":"P7","seq":1,"side":"impl"}
{"causes":[],"event":"Agree","inc":0,"incarnation":0,"node":"n1","proc":"n1","proposal":{"client":"c1","config_epoch":0,"lifetime":1,"token":1},"run":"P7","seq":2,"side":"impl"}
{"causes":[{"inc":0,"proc":"n1","seq":2}],"counted_toward":[0],"decider":"n1","event":"Agreed","inc":0,"node":"n1","node_incarnation":0,"proc":"n1","proposal":{"client":"c1","config_epoch":0,"lifetime":1,"token":1},"run":"P7","seq":3,"side":"impl"}
{"causes":[],"event":"Agree","inc":0,"incarnation":0,"node":"n2","proc":"n2","proposal":{"client":"c1","config_epoch":0,"lifetime":1,"token":1},"run":"P7","seq":2,"side":"impl"}
{"causes":[{"inc":0,"proc":"n2","seq":2}],"counted_toward":[0],"decider":"n1","event":"Agreed","inc":0,"node":"n2","node_incarnation":0,"proc":"n1","proposal":{"client":"c1","config_epoch":0,"lifetime":1,"token":1},"run":"P7","seq":4,"side":"impl"}
{"causes":[],"event":"Agree","inc":0,"incarnation":0,"node":"n3","proc":"n3","proposal":{"client":"c1","config_epoch":0,"lifetime":1,"token":1},"run":"P7","seq":2,"side":"impl"}
{"causes":[{"inc":0,"proc":"n3","seq":2}],"counted_toward":[0],"decider":"n1","event":"Agreed","inc":0,"node":"n3","node_incarnation":0,"proc":"n1","proposal":{"client":"c1","config_epoch":0,"lifetime":1,"token":1},"run":"P7","seq":5,"side":"impl"}
{"causes":[],"client":"c1","config_epoch":0,"event":"Grant","grantor_term":5,"inc":0,"inputs":[{"name":"agreed","ref":{"inc":0,"proc":"n1","seq":3},"value":null},{"name":"agreed","ref":{"inc":0,"proc":"n1","seq":4},"value":null},{"name":"agreed","ref":{"inc":0,"proc":"n1","seq":5},"value":null},{"name":"members","value":["n1","n2","n3"]},{"name":"config_epoch","value":0},{"name":"grantor_term","value":5},{"name":"last_token","value":0}],"key":"k","lifetime":1,"proc":"n1","run":"P7","seq":6,"side":"impl","token":1}
{"causes":[{"inc":0,"proc":"n1","seq":6}],"client":"c1","event":"WriteAttempt","grantor_term":5,"inc":0,"key":"k","proc":"c1","run":"P7","seq":2,"side":"impl","token":1,"value":"v1"}
{"causes":[],"cell":"F1.1","crash":"s","event":"Fault","inc":0,"proc":"env","run":"P7","seq":1,"side":"impl"}
{"causes":[],"cell":"F1.1","event":"Fault","inc":0,"proc":"env","restart":"s","run":"P7","seq":2,"side":"impl"}
{"causes":[{"inc":0,"proc":"n1","seq":6}],"client":"c1","event":"WriteAttempt","grantor_term":5,"inc":0,"key":"k","proc":"c1","run":"P7","seq":3,"side":"impl","token":1,"value":"v2"}
{"causes":[{"inc":0,"proc":"c1","seq":3}],"event":"WriteAccept","grantor_term":5,"highest_before":0,"inc":0,"inputs":[{"name":"token","value":1},{"name":"ledger","value":0},{"name":"stored_value","value":null},{"name":"value","value":"v2"}],"key":"k","proc":"s","run":"P7","seq":1,"side":"impl","token":1}
{"causes":[],"cell":"F1.1","crash":"c1","event":"Fault","inc":0,"proc":"env","run":"P7","seq":3,"side":"impl"}
{"causes":[],"cell":"F1.1","event":"Fault","inc":0,"proc":"env","restart":"c1","run":"P7","seq":4,"side":"impl"}
{"causes":[],"client":"c2","event":"Request","inc":0,"key":"k","proc":"c2","run":"P7","seq":1,"side":"impl"}
{"answers":{"inc":0,"proc":"c1","seq":3},"causes":[{"inc":0,"proc":"s","seq":1}],"client":"c1","event":"WriteAck","grantor_term":5,"inc":1,"key":"k","outcome":"accepted","proc":"c1","run":"P7","seq":1,"side":"impl","token":1}
{"causes":[{"inc":0,"proc":"c1","seq":2}],"event":"WriteAccept","grantor_term":5,"highest_before":1,"inc":0,"inputs":[{"name":"token","value":1},{"name":"ledger","value":1},{"name":"stored_value","value":"v2"},{"name":"value","value":"v1"}],"key":"k","proc":"s","run":"P7","seq":2,"side":"impl","token":1}
{"answers":{"inc":0,"proc":"c1","seq":2},"causes":[{"inc":0,"proc":"s","seq":2}],"client":"c1","event":"WriteAck","grantor_term":5,"inc":1,"key":"k","outcome":"accepted","proc":"c1","run":"P7","seq":2,"side":"impl","token":1}
{"causes":[],"event":"Agree","inc":0,"incarnation":0,"node":"n1","proc":"n1","proposal":{"client":"c2","config_epoch":0,"lifetime":1,"token":2},"run":"P7","seq":7,"side":"impl"}
{"causes":[{"inc":0,"proc":"n1","seq":7}],"counted_toward":[0],"decider":"n1","event":"Agreed","inc":0,"node":"n1","node_incarnation":0,"proc":"n1","proposal":{"client":"c2","config_epoch":0,"lifetime":1,"token":2},"run":"P7","seq":8,"side":"impl"}
{"causes":[],"event":"Agree","inc":0,"incarnation":0,"node":"n2","proc":"n2","proposal":{"client":"c2","config_epoch":0,"lifetime":1,"token":2},"run":"P7","seq":3,"side":"impl"}
{"causes":[{"inc":0,"proc":"n2","seq":3}],"counted_toward":[0],"decider":"n1","event":"Agreed","inc":0,"node":"n2","node_incarnation":0,"proc":"n1","proposal":{"client":"c2","config_epoch":0,"lifetime":1,"token":2},"run":"P7","seq":9,"side":"impl"}
{"causes":[],"event":"Agree","inc":0,"incarnation":0,"node":"n3","proc":"n3","proposal":{"client":"c2","config_epoch":0,"lifetime":1,"token":2},"run":"P7","seq":3,"side":"impl"}
{"causes":[{"inc":0,"proc":"n3","seq":3}],"counted_toward":[0],"decider":"n1","event":"Agreed","inc":0,"node":"n3","node_incarnation":0,"proc":"n1","proposal":{"client":"c2","config_epoch":0,"lifetime":1,"token":2},"run":"P7","seq":10,"side":"impl"}
{"causes":[],"client":"c2","config_epoch":0,"event":"Grant","grantor_term":9,"inc":0,"inputs":[{"name":"agreed","ref":{"inc":0,"proc":"n1","seq":8},"value":null},{"name":"agreed","ref":{"inc":0,"proc":"n1","seq":9},"value":null},{"name":"agreed","ref":{"inc":0,"proc":"n1","seq":10},"value":null},{"name":"members","value":["n1","n2","n3"]},{"name":"config_epoch","value":0},{"name":"grantor_term","value":9},{"name":"last_token","ref":{"inc":0,"proc":"n1","seq":6},"value":1}],"key":"k","lifetime":1,"proc":"n1","run":"P7","seq":11,"side":"impl","token":2}
{"causes":[{"inc":0,"proc":"n1","seq":11}],"client":"c2","event":"WriteAttempt","grantor_term":9,"inc":0,"key":"k","proc":"c2","run":"P7","seq":2,"side":"impl","token":2,"value":"v3"}
{"causes":[{"inc":0,"proc":"c2","seq":2}],"event":"WriteAccept","grantor_term":9,"highest_before":1,"inc":0,"inputs":[{"name":"token","value":2},{"name":"ledger","value":1},{"name":"stored_value","value":"v1"},{"name":"value","value":"v3"}],"key":"k","proc":"s","run":"P7","seq":3,"side":"impl","token":2}
{"answers":{"inc":0,"proc":"c2","seq":2},"causes":[{"inc":0,"proc":"s","seq":3}],"client":"c2","event":"WriteAck","grantor_term":9,"inc":0,"key":"k","outcome":"accepted","proc":"c2","run":"P7","seq":3,"side":"impl","token":2}

===== FILE: schedule P16.yaml =====
schedule: P16
derives: [C2.2, F1.1]
processes:
  lease: [n1, n2, n3]
  clients: [c1, c2]
  storage: [s]
steps:
  # derives: P16 (C2.2, F1.1). Storage crashes between receiving a read and acking it, then the client crashes after a served read; no client is given a value storage did not serve.
  - {at: start, do: {request: c1}}
  - {at: {event: Grant, client: c1}, do: {write: c1, value: v1}}
  - {at: {event: WriteAck, client: c1, outcome: accepted}, do: {read: c1}}
  - {at: {event: ReadAttempt, client: c1}, do: {cell: F1.1, crash: s}}
  - {at: start, do: {cell: F1.1, restart: s}}
  - {at: start, do: {read: c1}}
  - {at: {event: ReadAccept}, do: {cell: F1.1, crash: c1}}
  - {at: start, do: {cell: F1.1, restart: c1}}
  - {at: start, do: {request: c2}}
  - {at: {event: Grant, client: c2}, do: {read: c2}}
end: quiescent
bound: {events: 200}

===== FILE: arm R implementation trace impl-regen/observe/P16-seed1-rep1-attempt5.jsonl =====
{"causes":[],"decided":false,"epoch":0,"event":"ConfigCommitted","inc":0,"members":["n1","n2","n3"],"node":"n1","proc":"n1","readmits":[],"request_id":null,"run":"P16","seq":1,"side":"impl"}
{"causes":[],"decided":false,"epoch":0,"event":"ConfigCommitted","inc":0,"members":["n1","n2","n3"],"node":"n2","proc":"n2","readmits":[],"request_id":null,"run":"P16","seq":1,"side":"impl"}
{"causes":[],"decided":false,"epoch":0,"event":"ConfigCommitted","inc":0,"members":["n1","n2","n3"],"node":"n3","proc":"n3","readmits":[],"request_id":null,"run":"P16","seq":1,"side":"impl"}
{"causes":[],"client":"c1","event":"Request","inc":0,"key":"k","proc":"c1","run":"P16","seq":1,"side":"impl"}
{"causes":[],"event":"Agree","inc":0,"incarnation":0,"node":"n1","proc":"n1","proposal":{"client":"c1","config_epoch":0,"lifetime":1,"token":1},"run":"P16","seq":2,"side":"impl"}
{"causes":[{"inc":0,"proc":"n1","seq":2}],"counted_toward":[0],"decider":"n1","event":"Agreed","inc":0,"node":"n1","node_incarnation":0,"proc":"n1","proposal":{"client":"c1","config_epoch":0,"lifetime":1,"token":1},"run":"P16","seq":3,"side":"impl"}
{"causes":[],"event":"Agree","inc":0,"incarnation":0,"node":"n2","proc":"n2","proposal":{"client":"c1","config_epoch":0,"lifetime":1,"token":1},"run":"P16","seq":2,"side":"impl"}
{"causes":[{"inc":0,"proc":"n2","seq":2}],"counted_toward":[0],"decider":"n1","event":"Agreed","inc":0,"node":"n2","node_incarnation":0,"proc":"n1","proposal":{"client":"c1","config_epoch":0,"lifetime":1,"token":1},"run":"P16","seq":4,"side":"impl"}
{"causes":[],"event":"Agree","inc":0,"incarnation":0,"node":"n3","proc":"n3","proposal":{"client":"c1","config_epoch":0,"lifetime":1,"token":1},"run":"P16","seq":2,"side":"impl"}
{"causes":[{"inc":0,"proc":"n3","seq":2}],"counted_toward":[0],"decider":"n1","event":"Agreed","inc":0,"node":"n3","node_incarnation":0,"proc":"n1","proposal":{"client":"c1","config_epoch":0,"lifetime":1,"token":1},"run":"P16","seq":5,"side":"impl"}
{"causes":[],"client":"c1","config_epoch":0,"event":"Grant","grantor_term":5,"inc":0,"inputs":[{"name":"agreed","ref":{"inc":0,"proc":"n1","seq":3},"value":null},{"name":"agreed","ref":{"inc":0,"proc":"n1","seq":4},"value":null},{"name":"agreed","ref":{"inc":0,"proc":"n1","seq":5},"value":null},{"name":"members","value":["n1","n2","n3"]},{"name":"config_epoch","value":0},{"name":"grantor_term","value":5},{"name":"last_token","value":0}],"key":"k","lifetime":1,"proc":"n1","run":"P16","seq":6,"side":"impl","token":1}
{"causes":[{"inc":0,"proc":"n1","seq":6}],"client":"c1","event":"WriteAttempt","grantor_term":5,"inc":0,"key":"k","proc":"c1","run":"P16","seq":2,"side":"impl","token":1,"value":"v1"}
{"causes":[{"inc":0,"proc":"c1","seq":2}],"event":"WriteAccept","grantor_term":5,"highest_before":0,"inc":0,"inputs":[{"name":"token","value":1},{"name":"ledger","value":0},{"name":"stored_value","value":null},{"name":"value","value":"v1"}],"key":"k","proc":"s","run":"P16","seq":1,"side":"impl","token":1}
{"answers":{"inc":0,"proc":"c1","seq":2},"causes":[{"inc":0,"proc":"s","seq":1}],"client":"c1","event":"WriteAck","grantor_term":5,"inc":0,"key":"k","outcome":"accepted","proc":"c1","run":"P16","seq":3,"side":"impl","token":1}
{"causes":[{"inc":0,"proc":"n1","seq":6}],"client":"c1","event":"ReadAttempt","grantor_term":5,"inc":0,"key":"k","proc":"c1","run":"P16","seq":4,"side":"impl","token":1}
{"causes":[],"cell":"F1.1","crash":"s","event":"Fault","inc":0,"proc":"env","run":"P16","seq":1,"side":"impl"}
{"causes":[],"cell":"F1.1","event":"Fault","inc":0,"proc":"env","restart":"s","run":"P16","seq":2,"side":"impl"}
{"causes":[{"inc":0,"proc":"n1","seq":6}],"client":"c1","event":"ReadAttempt","grantor_term":5,"inc":0,"key":"k","proc":"c1","run":"P16","seq":5,"side":"impl","token":1}
{"causes":[{"inc":0,"proc":"c1","seq":5}],"event":"ReadAccept","grantor_term":5,"highest_before":1,"inc":0,"inputs":[{"name":"token","value":1},{"name":"ledger","value":1},{"name":"stored_value","value":"v1"}],"key":"k","proc":"s","run":"P16","seq":2,"side":"impl","token":1,"value":"v1"}
{"causes":[],"cell":"F1.1","crash":"c1","event":"Fault","inc":0,"proc":"env","run":"P16","seq":3,"side":"impl"}
{"causes":[],"cell":"F1.1","event":"Fault","inc":0,"proc":"env","restart":"c1","run":"P16","seq":4,"side":"impl"}
{"causes":[],"client":"c2","event":"Request","inc":0,"key":"k","proc":"c2","run":"P16","seq":1,"side":"impl"}
{"answers":{"inc":0,"proc":"c1","seq":5},"causes":[{"inc":0,"proc":"s","seq":2}],"client":"c1","event":"ReadAck","grantor_term":5,"inc":1,"key":"k","outcome":"served","proc":"c1","run":"P16","seq":1,"side":"impl","token":1,"value":"v1"}
{"causes":[{"inc":0,"proc":"c1","seq":4}],"event":"ReadAccept","grantor_term":5,"highest_before":1,"inc":0,"inputs":[{"name":"token","value":1},{"name":"ledger","value":1},{"name":"stored_value","value":"v1"}],"key":"k","proc":"s","run":"P16","seq":3,"side":"impl","token":1,"value":"v1"}
{"answers":{"inc":0,"proc":"c1","seq":4},"causes":[{"inc":0,"proc":"s","seq":3}],"client":"c1","event":"ReadAck","grantor_term":5,"inc":1,"key":"k","outcome":"served","proc":"c1","run":"P16","seq":2,"side":"impl","token":1,"value":"v1"}
{"causes":[],"event":"Agree","inc":0,"incarnation":0,"node":"n1","proc":"n1","proposal":{"client":"c2","config_epoch":0,"lifetime":1,"token":2},"run":"P16","seq":7,"side":"impl"}
{"causes":[{"inc":0,"proc":"n1","seq":7}],"counted_toward":[0],"decider":"n1","event":"Agreed","inc":0,"node":"n1","node_incarnation":0,"proc":"n1","proposal":{"client":"c2","config_epoch":0,"lifetime":1,"token":2},"run":"P16","seq":8,"side":"impl"}
{"causes":[],"event":"Agree","inc":0,"incarnation":0,"node":"n2","proc":"n2","proposal":{"client":"c2","config_epoch":0,"lifetime":1,"token":2},"run":"P16","seq":3,"side":"impl"}
{"causes":[{"inc":0,"proc":"n2","seq":3}],"counted_toward":[0],"decider":"n1","event":"Agreed","inc":0,"node":"n2","node_incarnation":0,"proc":"n1","proposal":{"client":"c2","config_epoch":0,"lifetime":1,"token":2},"run":"P16","seq":9,"side":"impl"}
{"causes":[],"event":"Agree","inc":0,"incarnation":0,"node":"n3","proc":"n3","proposal":{"client":"c2","config_epoch":0,"lifetime":1,"token":2},"run":"P16","seq":3,"side":"impl"}
{"causes":[{"inc":0,"proc":"n3","seq":3}],"counted_toward":[0],"decider":"n1","event":"Agreed","inc":0,"node":"n3","node_incarnation":0,"proc":"n1","proposal":{"client":"c2","config_epoch":0,"lifetime":1,"token":2},"run":"P16","seq":10,"side":"impl"}
{"causes":[],"client":"c2","config_epoch":0,"event":"Grant","grantor_term":9,"inc":0,"inputs":[{"name":"agreed","ref":{"inc":0,"proc":"n1","seq":8},"value":null},{"name":"agreed","ref":{"inc":0,"proc":"n1","seq":9},"value":null},{"name":"agreed","ref":{"inc":0,"proc":"n1","seq":10},"value":null},{"name":"members","value":["n1","n2","n3"]},{"name":"config_epoch","value":0},{"name":"grantor_term","value":9},{"name":"last_token","ref":{"inc":0,"proc":"n1","seq":6},"value":1}],"key":"k","lifetime":1,"proc":"n1","run":"P16","seq":11,"side":"impl","token":2}
{"causes":[{"inc":0,"proc":"n1","seq":11}],"client":"c2","event":"ReadAttempt","grantor_term":9,"inc":0,"key":"k","proc":"c2","run":"P16","seq":2,"side":"impl","token":2}
{"causes":[{"inc":0,"proc":"c2","seq":2}],"event":"ReadAccept","grantor_term":9,"highest_before":1,"inc":0,"inputs":[{"name":"token","value":2},{"name":"ledger","value":1},{"name":"stored_value","value":"v1"}],"key":"k","proc":"s","run":"P16","seq":4,"side":"impl","token":2,"value":"v1"}
{"answers":{"inc":0,"proc":"c2","seq":2},"causes":[{"inc":0,"proc":"s","seq":4}],"client":"c2","event":"ReadAck","grantor_term":9,"inc":0,"key":"k","outcome":"served","proc":"c2","run":"P16","seq":3,"side":"impl","token":2,"value":"v1"}
