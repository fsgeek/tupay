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
