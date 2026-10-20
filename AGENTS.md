# For every instance working here (Claude, Codex, or other)

1. Read `docs/seed.md` first, then the tail of `docs/seed-log.md`. Append to the log; never rewrite it.
2. **Derivation tags are the discipline.** Every artifact element names the contract clauses and failure-model cells it derives from, in a comment `derives: C1.2, F1.3` (or in the test name). Clause and cell ids are never reused: a retired id stays retired. A tag that points at a retired id is a stale derivation, which counts as laundering here.
3. **Pre-register before any outcome-bearing run.** Commit the predictions and scoring first. Every commit is OTS-stamped by the hook. Amendments are additive and say whether an outcome informed them.
4. **Cross-family roles.** The formal model and the implementation are written by different model families, from the contract and failure model only. Neither author reads the other's artifact before its own first version is committed.
5. **Anti-theater.** Every paired test has a mutation pair (a deliberately broken model and a deliberately broken implementation) that must fail. Agreement between the model and the implementation is not evidence of correctness.
6. Divergence is reported as **unexplained** until the evidence discriminates. Do not assume the implementation is at fault.
7. `tmp/` is never committed.
