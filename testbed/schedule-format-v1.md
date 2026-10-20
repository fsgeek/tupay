# Fault schedule format v1 (shared interface)

Fixed 2026-10-20 by the steward. A schedule is one YAML file. The same file compiles to TLC environment actions (model side) and to fault injection against the implementation (impl side). Each side writes its own compiler. This file is the only definition of the format.

## Shape
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
end: <trigger>                   # the run stops when this trigger fires, or at `bound`
bound: {events: 200}             # safety bound for both sides
```

## Triggers
A trigger names an observable event from `contract/v1.md`, with optional field filters. `start` fires immediately. Examples:
```yaml
at: start
at: {event: Grant, client: c1}
at: {event: WriteAck, client: c2, outcome: accepted}
at: {event: WriteReject}
```
On the model side a trigger is a predicate on the trace; the step's action becomes enabled once the predicate has held. On the impl side the injector watches the observe log and acts when the event appears. Both sides may take the action at any later point before the next step's trigger fires; neither side may act before.

## Actions
Workload (drives clients; derives from the contract, not a cell):
```yaml
do: {request: c1}                       # c1 requests a grant for the key
do: {write: c1, value: v1}              # c1 writes with whatever token it holds
do: {write: c1, value: v2, token: stale}  # c1 writes with its most recent *expired or superseded* token
```
Faults (one per cell):
```yaml
do: {cell: F1.1, crash: n2}
do: {cell: F1.1, restart: n2}
do: {cell: F1.2, partition: [[grantor, c1, s], [rest]]}   # two sides; `grantor` and `holder` resolve at trigger time; `rest` is everyone else
do: {cell: F1.2, heal: true}
do: {cell: F1.3, pause: c1}
do: {cell: F1.3, resume: c1}
```
`pause` must last longer than the grant's lifetime: a `resume` step must be triggered by an event that can only happen after expiry (for example a later `Grant` to another client).

## Rules
- A schedule may not name an action the failure model does not contain. The compiler on each side rejects it.
- `grantor` means the node that issued the most recent `Grant`; `holder` means the client that received it.
- Nondeterminism left open by the schedule (message order within a side, timing between trigger and action) is explored by TLC and sampled by the impl. A pair passing on the model side and failing on the impl side, or the reverse, is a divergence, not a bug on either side.
- Schedules live in `testbed/schedules/<name>.yaml`. The twelve pairs and the false-suspicion run each have one.
