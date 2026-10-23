# Brief: model author, fresh build (contract v3, failure model v3)

You are building the TLA+ model side of tupay from nothing. You are not the steward and you have no predecessor to consult. Your directory is `model-regen/`. Everything below is your complete brief.

## What you may read
- `contract/v3.md` (the contract; there is no other version for you), `failure-model/v3.md` (there is no other version for you), `tests/pairs-v4.md`, `testbed/schedule-format.md` (all of it, including the v5 addendum), `observe/schema.md` (all of it, including the v5 addendum), `testbed/schedules/` (fifty-nine shared schedules: P1 to P33, P40 to P54, P58 to P63, false-suspicion-v1 and H7 to H10; these are the only schedules that count)
- `AGENTS.md`, this brief, and `model-regen/`
Nothing else in this repository. Other directories are absent from your checkout on purpose; do not look for them.

**On `AGENTS.md`.** Its rule 1 names a steward's entry point, which is not yours: your brief is your entry point. Rules 2 to 7 apply. Your record is your README and your commits.

## What you produce, in `model-regen/`
1. `Lease.tla` and a `.cfg`: lease nodes (any number the schedules name, up to six), clients, storage and operators, one key, configurations and epochs, clocks, and amnesic restarts. The model may abstract the published protocol as that protocol's own specifications do; name what you abstract.
2. Environment actions for F1.1 to F3.3, each marked `\* derives: F…`.
3. Invariants for every safety clause and temporal properties for C1.4 and C3.4, each marked `\* derives: C…`.
4. A schedule compiler, in Python: a `testbed/schedules/<name>.yaml` to a TLC configuration in which the environment actions are enabled exactly as the schedule says.
5. A trace exporter from a TLC trace (a counterexample included) to `observe/<run>.jsonl` per `observe/schema.md`, including identities with incarnations, the v5 events and decision `inputs`.
6. Your half of every pair (P1 to P33, P40 to P54, P58 to P63): the check on the shared schedule and its mutation, a copy of the model with one deliberate break on the clause's enforcing path, named `\* mutation: P…`.
7. `model-regen/run.sh <schedule-name>`, printing `PASS`, `FAIL <invariant>` or `UNEXPLAINED <reason>` and writing the observe file; `--all` and `--mutations` as for the shared set.
8. `model-regen/README.md`: how to run, the protocol you followed, the TLC bounds, and every place you had to interpret the inputs. Interpretation is expected. Hiding it is not.

Schedules already exist in `testbed/schedules/`; do not write your own. `run.sh <name>` resolves `testbed/schedules/<name>.yaml`.

**The agreement protocol.** `contract/v3.md` does not prescribe how lease nodes agree on grants or on configurations. Follow a **published** protocol for agreement and membership change, name it in your README with a citation, say how it handles an amnesic restart (F3.3), and say where you adapted it to the contract. Do not invent an agreement protocol. Whatever protocol you follow, record the evidence the contract requires (`Agree`, `Agreed`, `ConfigCommitted` with `readmits`, decision `inputs`).

## Rules
- Every TLA+ definition, action, invariant and test carries a `derives:` comment naming contract clauses and failure-model cells. Nothing untagged.
- Do not change the inputs. If a clause is ambiguous, pick an interpretation, record it in your README, and continue.
- Before building, commit your predicted verdict for every shared schedule and every mutation. Then build. If a prediction was wrong, say so additively; never edit it.
- Commit as you go. Your first version is the commit you make when all of the above exists and `run.sh` works on at least P1.
- If an unmutated artifact fails a shared schedule, that is a result: record it, keep the trace or counterexample, and do not change the artifact to make it pass unless you can name the clause or cell the old behaviour misread.
- The steward may run schedules you have not seen, under any name, from `testbed/schedules/`; `run.sh <name>` must accept any schedule in the format, not only the ones listed here.
- In your report, list your **declared limitations**: shapes of schedule you believe your artifact would fail or could not check, and why you left them.
- **Reach.** For every bounded check you run, state in your README **what it must be able to reach** for each shared schedule (how many configurations and epochs, restarts and amnesic restarts, clock steps and their sizes, grants and tokens, terms) and the bounds you ran it at. A PASS from a space that cannot contain what the schedule needs is not a PASS; if your bounds cannot reach it, say so for that schedule.
- Tools: Java and `/home/tony/projects/tlaplus/tla2tools.jar`; Python via `uv`, offline: packages come from a local cache filled beforehand, holding `pyyaml==6.0.3` (use `uv run --no-project --with pyyaml==6.0.3`); if you need another, say so in your report and do without it. Keep explorations within memory you can name in your README; the machine is shared.

**Where you run.** Your session runs in a sandbox that shows you only your checkout and the toolchains. There is no network except your harness's own service. Commit normally: signing is configured with a key of your own. Your work is collected from your commits, so commit everything you want counted.

**Liveness.** C1.4 and C3.4 are checked as temporal properties, and their verdicts depend on the fairness you assume. Name every fairness condition in your README and say which clause or cell justifies it. Fairness may be assumed only on an action whose enablement depends on the acting process's own state and on messages delivered over links that are up; never on an action that requires having heard from a peer across a link that is down. A liveness result that rests on any other fairness is reported as such.
