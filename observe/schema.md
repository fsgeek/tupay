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

## v5 addendum (DRAFT, 2026-10-23, for contract v3 and failure model v3; additive; not an input until X3 registers)
**New events.** `ReconfigRequest`, `ConfigCommitted`, `ReconfigAck` and `Agreed` from `contract/v3.md`, with the fields named there; `Grant` gains `config_epoch`. A `Fault` record for F3.1 carries `members` and `to` (the receiving node); for F3.2, `proc` and `step` (the clock's jump, signed); for F3.3, `proc` and `amnesia: true`.
**Decision inputs** (`derives: C3.5, F3.2`). Every record of a decision (`Grant`, `WriteAccept`, `WriteReject`, `ReadAccept`, `ReadReject`, `ConfigCommitted` at the node that decided the commit, `ReconfigAck` with outcome `refused`) carries `inputs`: a list whose items are either `{"proc", "seq"}` (an earlier record the decision consulted) or `{"value": ..., "source": ...}` (a value consulted at the decision and recorded with it; `source` is one of `clock`, `random`, `config`, and a clock reading is always recorded this way). `causes` stays as before; `inputs` is what the decision depended on, which may be more than what caused it.
**The rule.** Every input a decision consults is recorded in `inputs` or is forbidden. An artifact may not let a decision depend on anything else (wall time not recorded, iteration order of an unordered map, goroutine scheduling, a random draw not recorded).
**The decision-replay check** (steward-built, `observe/`, with its mutation pair, before any author run): for each decision record, re-derive the outcome from its `inputs` alone, by a rule stated per event type (for `WriteAccept`/`WriteReject`, the token against `highest_before`; for `Grant`, the counted `Agreed` records against the configuration in effect and the tokens previously granted; for `ConfigCommitted`, the counted `Agreed` records against the old and new configurations). A decision whose recorded inputs do not determine its outcome is reported `UNEXPLAINED inputs` and counts against C3.5. Mutation pair: a trace in which a decision consulted an unrecorded input (a grant whose agreement set is not a majority of any configuration named in its inputs) must fail the check.
**Measure, not requirement (Yupi's offer, `docs/requests/2026-10-22-from-yupi-consistent-executions.md`).** For small fixed schedules, the number of model behaviours consistent with an observed trace's projection onto this schema, per schema version: how much each field narrows the set of executions consistent with what was observed, which is the seed's definition of this layer.
