# Brief: model author (fresh build from contract v2 and failure model v2)

You are building the TLA+ side of tupay from nothing. You are not the steward and you have no predecessor to consult. Your directory is `model-regen/`. Everything below is your complete brief.

## What you may read
- `contract/v2.md` (the contract; there is no other version for you), `failure-model/v2.md` (there is no other version for you), `tests/pairs-v3.md`
- `testbed/schedule-format.md` (all of it, including the addenda), `observe/schema.md` (all of it), `testbed/schedules/` (thirty-one shared schedules (P1 to P30 and false-suspicion-v1); these are the only schedules that count)
- `AGENTS.md`, this brief, and `model-regen/`
Nothing else in this repository. Other directories are absent from your checkout on purpose; do not look for them.

**On `AGENTS.md`.** Its rule 1 (read `docs/seed.md` and append to `docs/seed-log.md`) is for the steward and does not apply to you: those files are absent from your checkout on purpose. Rules 2 to 7 apply. Your record is your README and your commits.

## What you produce, in `model-regen/`
1. `Lease.tla` and a `.cfg`: state machine for 3 lease nodes, 2 clients, storage, one key. The grantor may be modelled abstractly (a leader per term, elected by a majority) rather than as a Raft protocol; the contract constrains what the grantor does, not how it agrees.
2. Environment actions for F1.1, F1.2, F1.3, F2.1, F2.2, each marked `\* derives: F1.x` or `F2.x`.
3. Invariants for C1.1, C1.2, C1.3, C2.1, C2.2 and a liveness property for C1.4, each marked `\* derives: C1.x`.
4. A schedule compiler: a script that takes a `testbed/schedules/<name>.yaml` and produces a TLC configuration (constants or a refinement) in which the environment actions are enabled exactly as the schedule says. Write it in Python.
5. A trace exporter that turns a TLC trace (including a counterexample) into `observe/<run>.jsonl` records per `observe/schema.md`.
6. Your half of every pair P1 to P30: the checking run on the shared schedule, and its mutation. Each test is named by its pair id. A mutation is a copy of the model with one deliberate break on the clause's enforcing path, named in a comment `\* mutation: P5 ...`.
7. `model-regen/run.sh <schedule-name>`: one command that runs TLC on the schedule and prints `PASS`, `FAIL <invariant>`, or `UNEXPLAINED <reason>`, and writes the observe file. `model-regen/run.sh --mutations` runs every mutation and is expected to report every one as `FAIL`; if a pair's unmutated half already fails, say so and do not mutate it.
8. `model-regen/README.md`: how to run, the TLC bounds you chose (state space, number of grants, number of writes), and every place you had to interpret the contract or failure model. Interpretation is expected. Hiding it is not.

Schedules already exist in `testbed/schedules/`; do not write your own. Your `run.sh <name>` resolves only `testbed/schedules/<name>.yaml`.

## Rules
- Every TLA+ definition, action, invariant, and test carries a `derives:` comment naming contract clauses and failure-model cells. Nothing untagged.
- Do not change the inputs. If a clause is ambiguous, pick an interpretation, record it in your README, and continue.
- Commit in your worktree as you go. Your first version is the commit you make when all of the above exists and `run.sh` works on at least P1.
- Tools on this machine: Java 11 and `/home/tony/projects/tlaplus/tla2tools.jar`; Python 3.14 via `uv`.
- If the unmutated model fails a shared schedule, that is a result: record it, keep the counterexample, and do not change the model to make it pass unless you can say which clause or cell the old behaviour misread.
- Before building, commit your predicted verdict for every shared schedule and every mutation. Then build. If a prediction was wrong, say so additively; never edit it.

**Liveness.** C1.4 is checked as a temporal property, and its verdict depends on the fairness you assume. Name every fairness condition in your README and say which clause or cell justifies it. Fairness may be assumed only on an action whose enablement depends on the acting process's own state and on messages delivered over links that are up; never on an action that requires having heard from a peer across a link that is down. A liveness result that rests on any other fairness is reported as such.
