# Brief: implementation author (Go)

You are writing the implementation for tupay. You are not the steward, and you must not read anything the steward or the model author has written except the files listed here.

## What you may read
- `contract/v1.md`, `failure-model/v1.md`, `tests/pairs-v1.md`
- `testbed/schedule-format.md`, `observe/schema.md`
- `AGENTS.md`
- Your own directory, `impl/`
Nothing else in this repository. Do not read `model/`, `docs/`, or the git log.

## What you produce, in `impl/`
1. A Go module: 3 lease nodes forming the grantor, 2 clients, 1 storage, one key. You may build the grantor on an existing Raft library (for example `hashicorp/raft`). No new protocol. All processes may run in one OS process with in-memory transports if that makes fault injection cleaner; the contract does not care.
2. Fault injection for F1.1 (crash and restart with only durable state), F1.2 (bipartition and heal, messages across the cut dropped), F1.3 (pause a client past its grant lifetime). Each marked `// derives: F1.x`.
3. Checkers for C1.1, C1.2, C1.3 and C1.4 that run over the observe log, each marked `// derives: C1.x`.
4. A schedule compiler: reads `testbed/schedules/<name>.yaml` and drives the workload and the injector as the format specifies.
5. An observe emitter writing `observe/<run>.jsonl` per `observe/schema.md`, from every process, with per-process sequence numbers and causal links. No wall-clock ordering.
6. Your half of every pair P1 to P12: the schedule file (write it from `tests/pairs-v1.md` if absent), the run, and its mutation. A mutation is a build tag or flag that applies one deliberate break on the clause's enforcing path, named `// mutation: P5 ...`.
7. `impl/run.sh <schedule-name>`: one command that runs the schedule, runs the checkers, and prints `PASS`, `FAIL <clause>`, or `UNEXPLAINED <reason>`, and writes the observe file. `impl/run.sh --mutations` runs every mutation and must report every one as `FAIL`. Runs are sampled; `run.sh` takes `--seeds N` and reports per seed.
8. `impl/README.md`: how to run, the sampling you chose, and every place you had to interpret the contract or failure model. Interpretation is expected. Hiding it is not.

## Rules
- Every package, type, function on the contract's path, injector, checker, and test carries a `// derives:` comment naming clauses and cells. Nothing untagged.
- Do not change the inputs. If a clause is ambiguous, pick an interpretation, record it in your README, and continue.
- Commit in your worktree as you go. Your first version is the commit you make when all of the above exists and `run.sh` works on at least the false-suspicion schedule.
- Tools on this machine: Go 1.22.4 at `/usr/local/go/bin/go`; network access for `go mod download`.
