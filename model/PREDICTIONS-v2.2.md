# Model-side predictions, round v2.2 (format v2.2, observe schema v3)

derives: C1.3, C2.2, F1.1; format v2.2 A1; observe v3 addendum

Additive. The earlier prediction files are not edited. Committed after reading the v2.2 brief, the format v2.2 text and the observe v3 addendum, and before any change or TLC run in this round.

## Plan
- **`restart: non-grantor`.** No behaviour change: the model already resolves it to `ngDown`, the node the most recent `crash: non-grantor` crashed, whatever that node is now. The compiler already rejects a schedule whose restart has no earlier crash. Only the tags change, to `format v2.2 A1`.
- **`answers`.** The exporter adds `answers: {proc, seq}` to every `WriteAck` and `ReadAck`, naming the `WriteAttempt` or `ReadAttempt` it answers. The attempt is found by the same key as the decision's cause: (client, token, value) for writes, and (client, read id) for reads. The model is unchanged, so TLC verdicts cannot change.

## Predictions
- **Schedules.** All 19 schedules (P1-P18, false-suspicion-v1): PASS, unchanged.
- **Mutations.** All 18 mutations: FAIL on the same clause as in X1, unchanged.
- **Witnesses.** In every PASS witness, each `WriteAck` and `ReadAck` carries `answers`, and the attempt it names is the one its `causes` chain reaches.
- **Mutation counterexamples.** Where an ack has no storage decision behind it (P8, P16, P17), `answers` still names the attempt the client believes it answers. In those records `causes` is empty, which is exactly what the mutations break.

## Outcome (appended after `run.sh --all`; the predictions above are unedited)
- **Schedules.** All 19 print `PASS`, unchanged, as predicted.
- **Mutations.** All 18 print `FAIL` on the same clause as in X1, as predicted.
- **`answers` consistency.** I checked all 56 `WriteAck`/`ReadAck` records across the 37 observe files with a one-off script. Every one carries `answers` naming a `WriteAttempt` or `ReadAttempt` in the same file. Wherever `causes` is non-empty, the decision it names cites the same attempt: 0 inconsistent.
- **Miss (descriptive, not a verdict).** I listed P8, P16 and P17 as the mutation counterexamples with an ack that has no storage decision behind it. P7 has one too: its early ack, sent before the decision. So the list was incomplete. In all four, `answers` names the attempt, as predicted.
- **Not done.** I did not run the steward's `observe/provenance_check.py`, because it is not in my access list.
