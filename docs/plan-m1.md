# Plan for M1 (steward, 2026-10-20)

M1 is done when every artifact exists and is tagged, the twelve pairs in `tests/pairs-v1.md` run on both sides, every mutation pair fails, and the false-suspicion run has been observed with provenance. M1 is a prototype, not an outcome-bearing run, but expected observations are written before any run (`experiments/M1-prereg.md`).

## Order of work
1. **Inputs** (done): `contract/v1.md`, `failure-model/v1.md`, `tests/pairs-v1.md`.
2. **Shared interfaces** (steward): the fault-schedule format that compiles to both sides, and the `observe/` event schema. These are the only things the two authors share beyond the inputs. Committed before either author starts.
3. **Author briefs** (steward): `docs/briefs/model-author.md` and `docs/briefs/impl-author.md`. Each brief lists exactly what the author may read: the inputs, the shared interfaces, its own directory. Nothing else in this repo and no session context from the steward.
4. **First versions, in isolation.** The model author (a Claude instance that is not the steward) and the implementation author (Codex) each work in their own git worktree and commit a first version before either sees the other's. The steward merges both, in one commit, after both are in.
5. **Paired runs.** Run every pair on both sides; run every mutation pair. Record results per pair, including "unexplained".
6. **False-suspicion run.** Observe, record provenance, do not judge.
7. **Cost baseline.** Tokens and wall-clock per author, decisions asked of Tony, interruptions. This is the baseline the change experiments compare against.
8. **Report** in `experiments/M1-result.md`, then the seed-log.

## Decisions the steward has made for M1
- Testbed compilers are written per side by each author against the steward's schedule format. This keeps the two sides independent while sharing one schedule.
- The implementation may use an existing Raft library for the grantor. No new protocol.
- Model checking is bounded (TLC); the bounds are stated in the pre-registration.
- A divergence between sides in M1 is logged as unexplained and carried into the result. M1 does not stop to resolve it unless it blocks the false-suspicion run.

## Not in M1
Hold-out cells. Family swap. Anything that makes a result look paper-shaped. Reads.
