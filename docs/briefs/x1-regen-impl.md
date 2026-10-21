# Brief: impl author, X1 regenerate arm (fresh build from contract v2)

You are building the Go side of tupay from nothing. You are not the steward and you have no predecessor to consult. Your directory is `impl-regen/`. Everything below is your complete brief.

## What you may read
- `contract/v2.md` (the contract; there is no other version for you), `failure-model/v1.md`, `tests/pairs-v2.md`
- `testbed/schedule-format.md` (all of it, including the addendum), `observe/schema.md` (all of it), `testbed/schedules/` (nineteen shared schedules; these are the only schedules that count)
- `AGENTS.md`, this brief, and `impl-regen/`
Nothing else in this repository. Other directories are absent from your checkout on purpose; do not look for them.

## What you produce, in `impl-regen/`
1. A Go module: 3 lease nodes forming the grantor, 2 clients, 1 storage, one key. You may build the grantor on an existing Raft library (for example `hashicorp/raft`). No new protocol. All processes may run in one OS process with in-memory transports if that makes fault injection cleaner; the contract does not care.
2. Fault injection for F1.1 (crash and restart with only durable state), F1.2 (bipartition and heal, messages across the cut dropped), F1.3 (pause a client past its grant lifetime). Each marked `// derives: F1.x`.
3. Checkers for C1.1, C1.2, C1.3, C1.4, C2.1 and C2.2 that run over the observe log, each marked `// derives: C1.x` or `C2.x`.
4. A schedule compiler: reads `testbed/schedules/<name>.yaml` and drives the workload and the injector as the format specifies.
5. An observe emitter writing `observe/<run>.jsonl` per `observe/schema.md`, from every process, with per-process sequence numbers and causal links. No wall-clock ordering.
6. Your half of every pair P1 to P18: the run on the shared schedule, and its mutation. A mutation is a build tag or flag that applies one deliberate break on the clause's enforcing path, named `// mutation: P5 ...`.
7. `impl-regen/run.sh <schedule-name>`: one command that runs the schedule, runs the checkers, and prints `PASS`, `FAIL <clause>`, or `UNEXPLAINED <reason>`, and writes the observe file. `impl-regen/run.sh --mutations` runs every mutation and must report every one as `FAIL`. Runs are sampled; `run.sh` takes `--seeds N` and reports per seed.
8. `impl-regen/README.md`: how to run, the sampling you chose, and every place you had to interpret the contract or failure model. Interpretation is expected. Hiding it is not.

Schedules already exist in `testbed/schedules/`; do not write your own. Your `run.sh <name>` resolves only `testbed/schedules/<name>.yaml`.

## Rules
- Every package, type, function on the contract's path, injector, checker, and test carries a `// derives:` comment naming clauses and cells. Nothing untagged.
- Do not change the inputs. If a clause is ambiguous, pick an interpretation, record it in your README, and continue.
- Commit in your worktree as you go. Your first version is the commit you make when all of the above exists and `run.sh` works on at least the false-suspicion schedule.
- Tools on this machine: Go 1.22.4 at `/usr/local/go/bin/go`; network access for `go mod download`.
- Before building, commit your predicted verdict for every shared schedule and every mutation. Then build. If a prediction was wrong, say so additively; never edit it.
