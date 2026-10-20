# Brief: model author (TLA+)

You are writing the formal model for tupay. You are not the steward, and you must not read anything the steward or the implementation author has written except the files listed here.

## What you may read
- `contract/v1.md`, `failure-model/v1.md`, `tests/pairs-v1.md`
- `testbed/schedule-format.md`, `observe/schema.md`
- `AGENTS.md`
- Your own directory, `model/`
Nothing else in this repository. Do not read `impl/`, `docs/`, or the git log.

## What you produce, in `model/`
1. `Lease.tla` and a `.cfg`: state machine for 3 lease nodes, 2 clients, storage, one key. The grantor may be modelled abstractly (a leader per term, elected by a majority) rather than as a Raft protocol; the contract constrains what the grantor does, not how it agrees.
2. Environment actions for F1.1, F1.2, F1.3, each marked `\* derives: F1.x`.
3. Invariants for C1.1, C1.2, C1.3 and a liveness property for C1.4, each marked `\* derives: C1.x`.
4. A schedule compiler: a script that takes a `testbed/schedules/<name>.yaml` and produces a TLC configuration (constants or a refinement) in which the environment actions are enabled exactly as the schedule says. Write it in Python.
5. A trace exporter that turns a TLC trace (including a counterexample) into `observe/<run>.jsonl` records per `observe/schema.md`.
6. Your half of every pair P1 to P12: a schedule file (if not present, write it from `tests/pairs-v1.md`), the checking run, and its mutation. Each test is named by its pair id. A mutation is a copy of the model with one deliberate break on the clause's enforcing path, named in a comment `\* mutation: P5 ...`.
7. `model/run.sh <schedule-name>`: one command that runs TLC on the schedule and prints `PASS`, `FAIL <invariant>`, or `UNEXPLAINED <reason>`, and writes the observe file. `model/run.sh --mutations` runs every mutation and must report every one as `FAIL`.
8. `model/README.md`: how to run, the TLC bounds you chose (state space, number of grants, number of writes), and every place you had to interpret the contract or failure model. Interpretation is expected. Hiding it is not.

## Rules
- Every TLA+ definition, action, invariant, and test carries a `derives:` comment naming contract clauses and failure-model cells. Nothing untagged.
- Do not change the inputs. If a clause is ambiguous, pick an interpretation, record it in your README, and continue.
- Commit in your worktree as you go. Your first version is the commit you make when all of the above exists and `run.sh` works on at least the false-suspicion schedule.
- Tools on this machine: Java 11 and `/home/tony/projects/tlaplus/tla2tools.jar`; Python 3.14 via `uv`.
