# Brief: impl author (fresh build from contract v2 and failure model v2)

You are building the Go side of tupay from nothing. You are not the steward and you have no predecessor to consult. Your directory is `impl-regen/`. Everything below is your complete brief.

## What you may read
- `contract/v2.md` (the contract; there is no other version for you), `failure-model/v2.md` (there is no other version for you), `tests/pairs-v3.md`
- `testbed/schedule-format.md` (all of it, including the addenda), `observe/schema.md` (all of it), `testbed/schedules/` (thirty-one shared schedules (P1 to P30 and false-suspicion-v1); these are the only schedules that count)
- `AGENTS.md`, this brief, and `impl-regen/`
Nothing else in this repository. Other directories are absent from your checkout on purpose; do not look for them.

**On `AGENTS.md`.** Its rule 1 (read `docs/seed.md` and append to `docs/seed-log.md`) is for the steward and does not apply to you: those files are absent from your checkout on purpose. Rules 2 to 7 apply. Your record is your README and your commits.

## What you produce, in `impl-regen/`
1. A Go module: 3 lease nodes forming the grantor, 2 clients, 1 storage, one key. You may build the grantor on an existing Raft library (for example `hashicorp/raft`). No new protocol. All processes may run in one OS process with in-memory transports if that makes fault injection cleaner; the contract does not care.
2. Fault injection for F1.1 (crash and restart with only durable state), F1.2 (bipartition and heal, messages across the cut dropped), F1.3 (pause a client past its grant lifetime), F2.1 (any set of links down both ways) and F2.2 (links down one way). Each marked `// derives: F1.x` or `F2.x`.
3. Checkers for C1.1, C1.2, C1.3, C1.4, C2.1 and C2.2 that run over the observe log, each marked `// derives: C1.x` or `C2.x`.
4. A schedule compiler: reads `testbed/schedules/<name>.yaml` and drives the workload and the injector as the format specifies.
5. An observe emitter writing `observe/<run>.jsonl` per `observe/schema.md`, from every process, with per-process sequence numbers and causal links. No wall-clock ordering.
6. Your half of every pair P1 to P30: the run on the shared schedule, and its mutation. A mutation is a build tag or flag that applies one deliberate break on the clause's enforcing path, named `// mutation: P5 ...`.
7. `impl-regen/run.sh <schedule-name>`: one command that runs the schedule, runs the checkers, and prints `PASS`, `FAIL <clause>`, or `UNEXPLAINED <reason>`, and writes the observe file. `impl-regen/run.sh --mutations` runs every mutation and is expected to report every one as `FAIL`; if a pair's unmutated half already fails, say so and do not mutate it. Runs are sampled; `run.sh` takes `--seeds N` and reports per seed.
8. `impl-regen/README.md`: how to run, the sampling you chose, and every place you had to interpret the contract or failure model. Interpretation is expected. Hiding it is not.

Schedules already exist in `testbed/schedules/`; do not write your own. Your `run.sh <name>` resolves only `testbed/schedules/<name>.yaml`.

## Rules
- Every package, type, function on the contract's path, injector, checker, and test carries a `// derives:` comment naming clauses and cells. Nothing untagged.
- Do not change the inputs. If a clause is ambiguous, pick an interpretation, record it in your README, and continue.
- Commit in your worktree as you go. Your first version is the commit you make when all of the above exists and `run.sh` works on at least P1.
- Tools on this machine: Go 1.22.4 at `/usr/local/go/bin/go`; network access for `go mod download`.
- If the unmutated implementation fails a shared schedule, that is a result: record it, keep the trace, and do not change the implementation to make it pass unless you can say which clause or cell the old behaviour misread.
- Before building, commit your predicted verdict for every shared schedule and every mutation. Then build. If a prediction was wrong, say so additively; never edit it.
