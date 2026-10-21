# Replay brief: arm D, model author

Your repository contains only what you need: `AGENTS.md`, this brief, and under `replay/`: `contract.md`, `failure-model.md`, `spec-D.md`, `scenario-format.md`, `observe.md` and `scenarios/`. `AGENTS.md` rules 2 to 7 apply to you; the files rule 1 names are not in this repository and you do not need them. Do not use the web, and do not look for files outside this repository.

## What you build
A TLA+ model of the design, in `model/`, with `tla2tools.jar` from `~/projects/tlaplus`.
- The design's members, messages and state as actions; J1.1, J1.2 and J1.3 from `replay/contract.md` as invariants; the failure model's cells as environment actions.
- A compiler from a scenario file (`replay/scenario-format.md`) to a TLC configuration that constrains the environment to the scenario's steps while exploring every interleaving the scenario leaves open.
- `model/run.sh <scenario-file>` prints `PASS`, `FAIL <clause>` or `UNEXPLAINED <reason>` and writes the observe file (`replay/observe.md`) from TLC's trace when there is one. `model/run.sh --mutations` runs every mutation against its scenario.
- **`model/run.sh --explore`**: check J1.1, J1.2 and J1.3 over all behaviours of the model within bounds you choose, with no scenario constraining the environment, and print the outcome as above. State every bound in your README with the reason for its value. Your bounds must at least let every shared scenario reach its end.

## The rules (the same for every author)
1. **Build the design in `replay/spec-D.md` exactly as written.** Its opening paragraph is part of this brief: where it says how something is done, do it that way, even if you believe another way is better; if you believe the design is wrong somewhere, record that and build what is written; where it is silent, choose, and record the choice.
2. **An unmutated failure is a result.** Do not change the artifact to make it pass without naming, in your README, the clause, cell or specification sentence you believe you misread.
3. **The steward may run scenarios you have not seen, under any name.** Your runner must accept a scenario file by path and must not refuse a scenario because of its name.
4. **Mutations.** For every shared scenario, write a mutation: a deliberately broken copy of your artifact, selected by a flag, that should fail that scenario's clause. Commit, before your first run, your predicted outcome for every shared scenario and every mutation.
5. **README sections.** Before your first run, commit **Choices** (every place the specification left open, and what you chose) and **Concerns** (anything in the design you believe is wrong, from reading alone, with the shape of a scenario that would show it; "none" is an answer). After your runs, add **Concerns after running** and **Declared limitations** (shapes of scenario your artifact would mishandle, and why you left them).
6. **Fairness and bounds.** Fairness only on a member's own enabled actions and on delivery over links that are up. A bound that stops a run before its end is `UNEXPLAINED bound`, never PASS.

## Order
1. Commit Choices, Concerns and your predictions.
2. Build; run every shared scenario and every mutation.
3. Add the after-running README sections; commit; tag the commit `first-version`. That tag is the version that is scored. You may keep working after it; later commits are reported but not scored.
4. Report: the `first-version` hash, the results of every run, your predictions beside them, and your wall-clock time.

Commit normally; this repository timestamps every commit.
