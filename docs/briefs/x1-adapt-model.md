# Brief: model author, X1 adapt arm (contract v2: reads are fenced)

Same author and access list as before, plus: `contract/v2.md`, `tests/pairs-v2.md`, the v3 addendum at the end of `testbed/schedule-format.md`, the v2 addendum at the end of `observe/schema.md`, and the six new shared schedules P13 to P18. `impl/` is absent on purpose; do not read `docs/` beyond this brief or `experiments/`.

The contract changed additively: two clauses, C2.1 and C2.2, and four read events. The failure model is unchanged. Adapt `model/` so that every element that enforces, tests or observes reads derives from C2.x and says so in its tag. Add invariants for C2.1 and C2.2, the `read` workload action, the read events in the exporter, your half of P13 to P18, and a mutation for each. Do not retire anything that still derives from a v1 clause.

Order: predictions for all nineteen schedules and eighteen mutations committed first; adapt; `run.sh --all`; README additively; adapted-version commit. Report commit hash, results, interpretations, wall-clock time.
