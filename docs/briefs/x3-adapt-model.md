# Brief: model author, adapt (contract v3, failure model v3: a changing membership)

You are taking over an existing TLA+ artifact, `model/`, from an author who is no longer available. You are not the steward. Everything below is your complete brief.

## What you may read
- `model/` (all of it: the model, its scripts, its README with the previous author's interpretations, its predictions and results)
- `contract/v3.md`, `failure-model/v3.md`, `tests/pairs-v4.md`, `testbed/schedule-format.md` (all of it, including the v5 addendum), `observe/schema.md` (all of it, including the v5 addendum), `testbed/schedules/` (fifty-nine shared schedules: P1 to P33, P40 to P54, P58 to P63, false-suspicion-v1 and H7 to H10; these are the only schedules that count)
- `AGENTS.md` and this brief
Nothing else. Other directories are absent from your checkout on purpose; do not look for them.

**On `AGENTS.md`.** Its rule 1 names a steward's entry point, which is not yours: your brief is your entry point. Rules 2 to 7 apply. Your record is your README and your commits.

## The change
The contract gained a locus, **configuration** (the grantor's membership and its epoch), with clauses C3.1, C3.4, C3.5, C3.7 and C3.8 and new observable events; C1.1 is made precise without a global order (`contract/v3.md`, "How v1 and v2 read under v3"). The failure model gained F3.1 (reconfiguration under faults), F3.2 (clock steps) and F3.3 (amnesia). The format gained `config`, `operators`, `lifetime`, `reconfigure`, `clock` and amnesic `restart` (v5 addendum); the schema gained identities with incarnations, the new events, and decision `inputs` (v5 addendum). `tests/pairs-v4.md` adds twenty-four pairs (P31 to P33, P40 to P54, P58 to P63).

Adapt `model/`: configurations and epochs, the operator, clocks and amnesic restarts as environment actions, the new invariants and the C3.4 liveness property, the v5 actions in the compiler, the new events and decision `inputs` in the exporter, your half of the twenty-four new pairs, and a mutation for each. The model may abstract the published protocol as that protocol's own specifications do; name what you abstract. Every element that the change invalidates (it represents the lease nodes as fixed, decides a grant, consults a clock without recording it, or assumes a restart keeps durable state) must derive from the clauses and cells it now enforces, and say so in its tag. Do not retire anything that still derives from a v1 or v2 clause or cell. Where a previous interpretation no longer holds under v3, say so in the README, additively: name it, say why, and say what replaces it. Do not delete it.

**The agreement protocol.** `contract/v3.md` does not prescribe how lease nodes agree on grants or on configurations. Follow a **published** protocol for agreement and membership change, name it in your README with a citation, say how it handles an amnesic restart (F3.3), and say where you adapted it to the contract. Do not invent an agreement protocol. Whatever protocol you follow, record the evidence the contract requires (`Agree`, `Agreed`, `ConfigCommitted` with `readmits`, decision `inputs`).

## Order
1. Read the README and the inputs. Commit predictions first: the verdict for every one of the fifty-nine shared schedules and every mutation, and which previous interpretations you expect to change.
2. Adapt. Commit as you go; say in each commit message whether the commit is mechanical propagation or a change required by the meaning of the new clauses or cells.
3. `run.sh --all` and `run.sh --mutations`. README additively. Adapted-version commit.
4. Report: commit hash, results, interpretations (new, extended, contradicted), declared limitations, wall-clock time.

## Rules
- If an unmutated artifact fails a shared schedule, that is a result: record it, keep the trace or counterexample, and do not change the artifact to make it pass unless you can name the clause or cell the old behaviour misread.
- The steward may run schedules you have not seen, under any name, from `testbed/schedules/`; `run.sh <name>` must accept any schedule in the format, not only the ones listed here.
- In your report, list your **declared limitations**: shapes of schedule you believe your artifact would fail or could not check, and why you left them.
- **Reach.** For every bounded check you run, state in your README **what it must be able to reach** for each shared schedule (how many configurations and epochs, restarts and amnesic restarts, clock steps and their sizes, grants and tokens, terms) and the bounds you ran it at. A PASS from a space that cannot contain what the schedule needs is not a PASS; if your bounds cannot reach it, say so for that schedule.
- Tools: Java and `/home/tony/projects/tlaplus/tla2tools.jar`; Python via `uv`. Keep explorations within memory you can name in your README; the machine is shared.

**Where you run.** Your session runs in a sandbox that shows you only your checkout and the toolchains. There is no network except your harness's own service. Commit normally: signing is configured with a key of your own. Your work is collected from your commits, so commit everything you want counted.

**Liveness.** C1.4 and C3.4 are checked as temporal properties, and their verdicts depend on the fairness you assume. Name every fairness condition in your README and say which clause or cell justifies it. Fairness may be assumed only on an action whose enablement depends on the acting process's own state and on messages delivered over links that are up; never on an action that requires having heard from a peer across a link that is down. A liveness result that rests on any other fairness is reported as such.
