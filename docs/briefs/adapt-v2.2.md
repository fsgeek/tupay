# Brief: both authors, adaptation to schedule format v2.2 and observe schema v3

Same access list as your X1 adapt brief; the other side's directory and `experiments/` are absent on purpose. Read the changelog at the end of `testbed/schedule-format.md` (v2.2) and the v3 addendum at the end of `observe/schema.md`.

Two changes. (1) `restart: non-grantor` is now defined as restarting the node the most recent `crash: non-grantor` crashed; you already implemented this; tag it. (2) `WriteAck` and `ReadAck` records carry `answers: {proc, seq}` naming the attempt they answer; emit it, and the steward's `observe/provenance_check.py` now checks it. No contract or failure-model change; no new schedules.

Order: predictions (which schedules and mutations change verdict: expected none) committed first; adapt; run everything; README additively; adapted-version commit. Report commit hash, results, wall-clock time.
