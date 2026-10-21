# Brief: model author (failure model v2: partial and simplex partitions)

You are taking over an existing TLA+ artifact, `model/`, from an author who is no longer available. You are not the steward. Everything below is your complete brief.

## What you may read
- `model/` (all of it: the model, its scripts, its README with the previous author's interpretations, its predictions and results)
- `contract/v2.md`, `failure-model/v2.md`, `tests/pairs-v3.md`, `testbed/schedule-format.md` (all of it), `observe/schema.md` (all of it), `testbed/schedules/` (thirty-one shared schedules (P1 to P30 and false-suspicion-v1); these are the only schedules that count)
- `AGENTS.md` and this brief
Nothing else. Other directories are absent from your checkout on purpose; do not look for them.

**On `AGENTS.md`.** Its rule 1 (read `docs/seed.md` and append to `docs/seed-log.md`) is for the steward and does not apply to you: those files are absent from your checkout on purpose. Rules 2 to 7 apply. Your record is your README and your commits.

## The change
The failure model gained links (one per ordered pair of processes, up or down), a definition of "connected" (both directions of the direct link up), F2.1 partial partition and F2.2 simplex link failure. The contract did not change. The format gained `cut` and `drop` (v4 addendum, rules L1 to L3); the schema gained `links` on `Fault` records (v4 addendum). `tests/pairs-v3.md` adds P19 to P30.

Adapt `model/` so that every element that represents connectivity derives from F2.x where it now must, and says so in its tag. Add F2.1 and F2.2 environment actions, the `cut` and `drop` actions in the compiler, `links` in the exporter, your half of P19 to P30, and a mutation for each. Do not retire anything that still derives from a v1 cell or clause. Where a previous interpretation no longer holds under v2, say so in the README, additively: name it, say why, and say what replaces it. Do not delete it.

## Order
1. Read the README and the inputs. Commit predictions first: the verdict for every one of the thirty-one shared schedules (P1 to P30 and false-suspicion-v1) and every mutation, and which previous interpretations you expect to change.
2. Adapt. Commit as you go; say in each commit message whether the commit is mechanical propagation or a change required by the meaning of F2.x.
3. `run.sh --all` and `run.sh --mutations`. README additively. Adapted-version commit.
4. Report: commit hash, results, interpretations (new, extended, contradicted), wall-clock time.

If the unmutated model fails a shared schedule, that is a result: record it, keep the counterexample, and do not change the model to make it pass unless you can say which clause or cell the old behaviour misread. Tools: Java 11 and `/home/tony/projects/tlaplus/tla2tools.jar`; Python via `uv`.

**Liveness.** C1.4 is checked as a temporal property, and its verdict depends on the fairness you assume. Name every fairness condition in your README and say which clause or cell justifies it. Fairness may be assumed only on an action whose enablement depends on the acting process's own state and on messages delivered over links that are up; never on an action that requires having heard from a peer across a link that is down. A liveness result that rests on any other fairness is reported as such.
