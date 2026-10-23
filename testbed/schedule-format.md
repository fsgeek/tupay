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
