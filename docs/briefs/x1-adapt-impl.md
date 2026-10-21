# Brief: implementation author, X1 adapt arm (contract v2: reads are fenced)

Same author and access list as before, plus: `contract/v2.md`, `tests/pairs-v2.md`, the v3 addendum at the end of `testbed/schedule-format.md`, the v2 addendum at the end of `observe/schema.md`, and the six new shared schedules P13 to P18. `model/` is absent on purpose; do not read `docs/` beyond this brief or `experiments/`.

The contract changed additively: two clauses, C2.1 and C2.2, and four read events. The failure model is unchanged. Adapt `impl/` so that every element that enforces, tests or observes reads derives from C2.x and says so in its tag. Add the read path to storage and clients, checkers for C2.1 and C2.2 over the observe log, the `read` workload action in the compiler, the read events in the emitter, your half of P13 to P18, and a mutation for each. Do not retire anything that still derives from a v1 clause.

Order: predictions for all nineteen schedules (per seed) and eighteen mutations committed first; adapt; `impl/run.sh --all --seeds 3` and `--mutations --seeds 3`; README additively; adapted-version commit. Report commit hash, per-seed results, interpretations, wall-clock time. Your clone has the signing configuration; commit normally.
