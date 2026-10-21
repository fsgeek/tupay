# Brief: implementation author (failure model v2: partial and simplex partitions)

You are taking over an existing Go artifact, `impl/`, from an author who is no longer available. You are not the steward. Everything below is your complete brief.

## What you may read
- `impl/` (all of it: the code, its README with the previous author's interpretations, its predictions, results and evidence)
- `contract/v2.md`, `failure-model/v2.md`, `tests/pairs-v3.md`, `testbed/schedule-format.md` (all of it), `observe/schema.md` (all of it), `testbed/schedules/` (thirty-one shared schedules (P1 to P30 and false-suspicion-v1); these are the only schedules that count)
- `AGENTS.md` and this brief
Nothing else. Other directories are absent from your checkout on purpose; do not look for them.

**On `AGENTS.md`.** Its rule 1 (read `docs/seed.md` and append to `docs/seed-log.md`) is for the steward and does not apply to you: those files are absent from your checkout on purpose. Rules 2 to 7 apply. Your record is your README and your commits.

## The change
The failure model gained links (one per ordered pair of processes, up or down), a definition of "connected" (both directions of the direct link up), F2.1 partial partition and F2.2 simplex link failure. The contract did not change. The format gained `cut` and `drop` (v4 addendum, rules L1 to L3); the schema gained `links` on `Fault` records (v4 addendum). `tests/pairs-v3.md` adds P19 to P30.

Adapt `impl/` so that fault injection supports per-direction link failures and every element that represents connectivity derives from F2.x where it now must, and says so in its tag. Add `cut` and `drop` to the compiler, `links` to the emitter, your half of P19 to P30, and a mutation for each. Do not retire anything that still derives from a v1 cell or clause. Where a previous interpretation no longer holds under v2, say so in the README, additively: name it, say why, and say what replaces it. Do not delete it.

## Order
1. Read the README and the inputs. Commit predictions first: the verdict per seed for every one of the thirty-one shared schedules (P1 to P30 and false-suspicion-v1) and every mutation, and which previous interpretations you expect to change.
2. Adapt. Commit as you go; say in each commit message whether the commit is mechanical propagation or a change required by the meaning of F2.x.
3. `impl/run.sh --all --seeds 3` and `--mutations --seeds 3`. README additively. Adapted-version commit.
4. Report: commit hash, per-seed results, interpretations (new, extended, contradicted), wall-clock time.

If the unmutated implementation fails a shared schedule, that is a result: record it, keep the trace, and do not change the implementation to make it pass unless you can say which clause or cell the old behaviour misread. Your clone has the signing configuration; commit normally. Go is at `/usr/local/go/bin/go`.
