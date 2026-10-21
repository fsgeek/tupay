# Replay observability schema (shared interface)

Version 1, fixed 2026-10-21. Both sides write one JSON object per line to `<side>/observe/<run>.jsonl`; the model side from a TLC trace, the implementation side live.

```json
{"proc": "m2", "seq": 14, "event": "Committed", "index": 3, "epoch": 2,
 "causes": [{"proc": "m2", "seq": 12}], "run": "<run id>", "side": "impl"}
```
- `proc`, `seq`: the member the event concerns and its own counter. There is no cross-member clock; wall time, if kept, goes in a separate file for humans.
- Event fields are exactly those in `replay/contract.md`.
- `causes`: the records this one follows from, by `(proc, seq)`. An `Appended` on a follower names the coordinator's `Appended` of the same entry; a `Committed` names the `Appended` of the entry committed; an `Elected` names the ballot grants that elected it, recorded as the voters' `(proc, seq)` of their latest record when they granted; a `ConfigInEffect` names the `Appended` or `Truncated` that caused it.
- Fault steps are recorded as `Fault` records from `proc: "env"` with the step's action as fields and, for `cut` and `drop`, the resolved directed links.

## The question a trace must answer
For any violation of J1.1 or J1.4: which configuration entries each involved member had in effect at each election and each commitment, and which members' grants or acknowledgements those decisions counted. A trace that cannot answer this has failed the observability layer's own test.
