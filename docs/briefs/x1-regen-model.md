# Brief: model author, X1 regenerate arm (fresh build from contract v2)

You are building the TLA+ side of tupay from nothing. You are not the steward and you have no predecessor to consult. Your directory is `model-regen/`. Everything below is your complete brief.

## What you may read
- `contract/v2.md` (the contract; there is no other version for you), `failure-model/v1.md`, `tests/pairs-v2.md`
- `testbed/schedule-format.md` (all of it, including the addendum), `observe/schema.md` (all of it), `testbed/schedules/` (nineteen shared schedules; these are the only schedules that count)
- `AGENTS.md`, this brief, and `model-regen/`
Nothing else in this repository. Other directories are absent from your checkout on purpose; do not look for them.

## What you produce, in `model-regen/`
1. `Lease.tla` and a `.cfg`: state machine for 3 lease nodes, 2 clients, storage, one key. The grantor may be modelled abstractly (a leader per term, elected by a majority) rather than as a Raft protocol; the contract constrains what the grantor does, not how it agrees.
2. Environment actions for F1.1, F1.2, F1.3, each marked `\* derives: F1.x`.
3. Invariants for C1.1, C1.2, C1.3, C2.1, C2.2 and a liveness property for C1.4, each marked `\* derives: C1.x`.
4. A schedule compiler: a script that takes a `testbed/schedules/<name>.yaml` and produces a TLC configuration (constants or a refinement) in which the environment actions are enabled exactly as the schedule says. Write it in Python.
5. A trace exporter that turns a TLC trace (including a counterexample) into `observe/<run>.jsonl` records per `observe/schema.md`.
6. Your half of every pair P1 to P18: the checking run on the shared schedule, and its mutation. Each test is named by its pair id. A mutation is a copy of the model with one deliberate break on the clause's enforcing path, named in a comment `\* mutation: P5 ...`.
7. `model-regen/run.sh <schedule-name>`: one command that runs TLC on the schedule and prints `PASS`, `FAIL <invariant>`, or `UNEXPLAINED <reason>`, and writes the observe file. `model-regen/run.sh --mutations` runs every mutation and must report every one as `FAIL`.
8. `model-regen/README.md`: how to run, the TLC bounds you chose (state space, number of grants, number of writes), and every place you had to interpret the contract or failure model. Interpretation is expected. Hiding it is not.

Schedules already exist in `testbed/schedules/`; do not write your own. Your `run.sh <name>` resolves only `testbed/schedules/<name>.yaml`.

## Rules
- Every TLA+ definition, action, invariant, and test carries a `derives:` comment naming contract clauses and failure-model cells. Nothing untagged.
- Do not change the inputs. If a clause is ambiguous, pick an interpretation, record it in your README, and continue.
- Commit in your worktree as you go. Your first version is the commit you make when all of the above exists and `run.sh` works on at least the false-suspicion schedule.
- Tools on this machine: Java 11 and `/home/tony/projects/tlaplus/tla2tools.jar`; Python 3.14 via `uv`.
- Before building, commit your predicted verdict for every shared schedule and every mutation. Then build. If a prediction was wrong, say so additively; never edit it.
