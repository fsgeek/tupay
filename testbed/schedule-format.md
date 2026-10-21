# Fault schedule format v2.1 (shared interface)

v2.1 fixed 2026-10-21 (two clarifications, listed in the changelog). v2 fixed 2026-10-20 by the steward, after M1's cross-run. v1 is kept as `schedule-format-v1.md`; nothing in it is removed. v2 adds the rules that v1 left open and that the judge named (M1 result, D2 and D3). Every schedule compiler derives from this file; a compiler that implements v1 is stale under v2.

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

**Rule A1, aliases (new in v2; settles D3).** `grantor`, `holder` and `rest` are process selectors and may appear **wherever a process name may appear**: as the target of `crash`, `restart`, `pause`, `resume`, `request` and `write`, and as members of a partition side. `grantor` is the node that issued the most recent `Grant` event; `holder` is the client that received it; `rest` is every process not named on the other side of the same partition. Aliases are resolved at the moment the step's trigger fires. A schedule that uses `grantor` or `holder` before any `Grant` can have occurred is rejected by the compiler. **(v2.1)** A fourth selector, `non-grantor`, means a lease node other than `grantor` that is up at the moment the trigger fires. The model side explores every such node; the impl side picks the lowest-numbered one. It exists because leadership before the first `Grant` is not observable, so "crash a follower" can only be said after a grant.

**Rule A2, crash and restart.** `restart` of a process that is not crashed, `crash` of a process already crashed, `pause` of a paused client, `resume` of a running client, and `pause` of a lease node or storage are all rejected by the compiler.

## End of a run
**Rule E1 (new in v2).** `end:` is either an event trigger, armed when the last step's action is taken and matched by Rule T1, or the word `quiescent`. `quiescent` means: every step has been applied and no request, write or ack is in flight and no client is waiting for a grant, with crashed and paused processes not counted. On the model side `quiescent` is a state predicate; on the impl side it is a bounded wait for in-flight work, after which an unanswered request is reported through the liveness checker, not as `end` unreachable. The shared schedules use `quiescent` unless the end must be a specific event.

**Rule E2.** A clause violation witnessed before the end is a `FAIL` whether or not the end is reached. `UNEXPLAINED end unreachable` is reported only when no violation was witnessed.

## Rules carried from v1
- A schedule may not name an action the failure model does not contain; the compiler rejects it.
- Nondeterminism the schedule leaves open (message order within a side, delay between trigger and action) is explored by TLC and sampled by the impl. A pass on one side and a failure on the other is a divergence, not a bug on either side.
- **Schedules live in `testbed/schedules/<name>.yaml` and nowhere else.** Both runners resolve a name there. The authors' private schedule sets from M1 are kept under their own directories as history and are no longer run.

## Changelog
- v2.1 (2026-10-21): T1 clarified for a predecessor's own events; `non-grantor` selector. Reasons: M1 result, round 2 residues. Shared P10 rewritten to use it.
- v2 (2026-10-20): T1 arming, T2, T3, A1 aliases, A2, E1 `quiescent`, E2; schedules shared. Reasons: M1 result D2 and D3.

## v3 addendum (2026-10-21, for contract v2; additive)
One workload action is added. Everything else in v2.1 is unchanged.
```yaml
do: {read: c1}                 # c1 reads the key with its current token
do: {read: c1, token: stale}   # with its most recent token lower than the highest granted so far
```
Rule T3 applies to `read` as it does to `write`. Triggers may name the new events `ReadAttempt`, `ReadAccept`, `ReadReject` and `ReadAck` (with `outcome: served` or `rejected`). Changelog: v3 (2026-10-21): `read` action and the four read events. Reason: X1, contract v2.
