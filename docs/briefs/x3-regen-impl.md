# Brief: implementation author, fresh build (contract v3, failure model v3)

You are building the Go implementation side of tupay from nothing. You are not the steward and you have no predecessor to consult. Your directory is `impl-regen/`. Everything below is your complete brief.

## What you may read
- `contract/v3.md` (the contract; there is no other version for you), `failure-model/v3.md` (there is no other version for you), `tests/pairs-v4.md`, `testbed/schedule-format.md` (all of it, including the v5 addendum), `observe/schema.md` (all of it, including the v5 addendum), `testbed/schedules/` (fifty-nine shared schedules: P1 to P33, P40 to P54, P58 to P63, false-suspicion-v1 and H7 to H10; these are the only schedules that count)
- `AGENTS.md`, this brief, and `impl-regen/`
Nothing else in this repository. Other directories are absent from your checkout on purpose; do not look for them.

**On `AGENTS.md`.** Its rule 1 names a steward's entry point, which is not yours: your brief is your entry point. Rules 2 to 7 apply. Your record is your README and your commits.

## What you produce, in `impl-regen/`
1. A Go implementation of the lease service: lease nodes (any number the schedules name, up to six), clients, storage and operators, one key. You may build the grantor on an existing Raft library, following the protocol rule below.
2. A testbed that injects every fault the format names (F1.1 to F3.3) against the implementation, each injection point marked `// derives: F…`.
3. A schedule compiler that takes a `testbed/schedules/<name>.yaml` and drives the testbed exactly as the schedule says.
4. An emitter that writes `observe/<run>.jsonl` records per `observe/schema.md`, including identities with incarnations, the v5 events and decision `inputs`.
5. Your half of every pair (P1 to P33, P40 to P54, P58 to P63): the run on the shared schedule and its mutation. A mutation is a copy with one deliberate break on the clause's enforcing path, named `// mutation: P…`.
6. `impl-regen/run.sh <schedule-name> [--seeds N --reps M]`, printing `PASS`, `FAIL <clause>` or `UNEXPLAINED <reason>` per run and writing the observe file; `--all` runs every shared schedule; `--mutations` runs every mutation, each expected to `FAIL`.
7. `impl-regen/README.md`: how to run, the protocol you followed, and every place you had to interpret the inputs. Interpretation is expected. Hiding it is not.

Schedules already exist in `testbed/schedules/`; do not write your own. `run.sh <name>` resolves `testbed/schedules/<name>.yaml`.

**The agreement protocol.** `contract/v3.md` does not prescribe how lease nodes agree on grants or on configurations. Follow a **published** protocol for agreement and membership change, name it in your README with a citation, say how it handles an amnesic restart (F3.3), and say where you adapted it to the contract. Do not invent an agreement protocol. Whatever protocol you follow, record the evidence the contract requires (`Agree`, `Agreed`, `ConfigCommitted` with `readmits`, decision `inputs`).

## Rules
- Every function, injection point, check and test carries a `derives:` comment naming contract clauses and failure-model cells. Nothing untagged.
- Do not change the inputs. If a clause is ambiguous, pick an interpretation, record it in your README, and continue.
- Before building, commit your predicted verdict per seed for every shared schedule and every mutation. Then build. If a prediction was wrong, say so additively; never edit it.
- Commit as you go. Your first version is the commit you make when all of the above exists and `run.sh` works on at least P1.
- If an unmutated artifact fails a shared schedule, that is a result: record it, keep the trace or counterexample, and do not change the artifact to make it pass unless you can name the clause or cell the old behaviour misread.
- The steward may run schedules you have not seen, under any name, from `testbed/schedules/`; `run.sh <name>` must accept any schedule in the format, not only the ones listed here.
- In your report, list your **declared limitations**: shapes of schedule you believe your artifact would fail or could not check, and why you left them.
- The steward will run every shared schedule at three seeds and ten repetitions per seed; a schedule whose outcome varies across repetitions of one seed is reported as **flaky**. `run.sh` should accept `--seeds N --reps M`.
- Tools: Go at `/usr/local/go/bin/go`; modules come from a local cache filled beforehand, so if one you need is missing, say so in your report and do without it.

**Where you run.** Your session runs in a sandbox that shows you only your checkout and the toolchains. There is no network except your harness's own service. Commit normally: signing is configured with a key of your own. Your work is collected from your commits, so commit everything you want counted.
