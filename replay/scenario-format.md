# Replay scenario format (shared interface)

Version 1, fixed 2026-10-21. Both sides compile a scenario: the model side into a TLC configuration that constrains the environment to the scenario's steps while exploring every interleaving it leaves open; the implementation side into fault injection and requests against a running system, sampled over seeds.

## Shape
```yaml
scenario: <name>
derives: [J1.4, G1.3]           # clauses and cells exercised
initial: [m1, m2, m3, m4]       # initial configuration; m5 exists too and is started with it
steps:
  - at: <trigger>
    do: <action>
end: {settle: 100}               # events after the last step's action
bound: {events: 400}
```

## Triggers
`start`, or an observable event from `replay/contract.md` with optional field filters, for example `{event: Elected, member: m2}`, `{event: Committed, member: m2, index: 3}`, `{event: Appended, member: m5, kind: config}`. Step 1 is armed at the start; step *i* is armed when step *i*−1's action is taken, and matches only events emitted after it was armed (the action's own synchronous events count). Once a trigger fires, the action is taken at some later point: the model explores every such point, the implementation samples one.

## Actions
```yaml
do: {add: m5, at: m1}                 # an administrator asks m1 to add m5 (G1.4)
do: {remove: m4, at: m2}              # asks m2 to remove m4 (G1.4)
do: {crash: m3}                       # G1.1
do: {restart: m3}                     # G1.1
do: {cut: [[m1, m2], [m1, m3]]}       # each listed link down in both directions (G1.3)
do: {drop: [[m2, m1]]}                # messages from m2 to m1 lost; the reverse untouched (G1.3)
do: {heal: true}                      # every link restored
do: {command: c1, at: m1}             # an administrator asks m1 to append command c1; a member that is not coordinator ignores it
```
Three selectors may stand for a member name anywhere one is allowed, resolved when the step's trigger fires: `coordinator`, the member most recently `Elected`; `follower`, a member that is up and is not `coordinator` (the model explores every such member, the implementation picks the lowest-numbered); `crashed`, the member most recently crashed by a `crash` step (a scenario that uses it before any crash is rejected; likewise `coordinator` before any `Elected`). A self-pair in `cut` or `drop` is ignored; link failures accumulate until `heal`.

## End and bound
`end: {settle: N}`: the run continues for N events after the last step's action is taken, then stops. A violation of J1.1, J1.3 or J1.4 witnessed at any point is `FAIL <clause>`. If `bound` is reached before every step's action is taken, the outcome is `UNEXPLAINED steps` (the scenario never reached its point), never PASS. Otherwise the outcome is `PASS`. The model side explores every behaviour within its bounds that takes every step and at most N further events, with every prefix of such behaviours; it reports `UNEXPLAINED steps` if no behaviour within its bounds takes every step.

## Where scenarios live
Shared scenarios are in `replay/scenarios/<name>.yaml`. Each side's runner also accepts a path to a scenario file anywhere, because the steward may run scenarios the authors have not seen.
