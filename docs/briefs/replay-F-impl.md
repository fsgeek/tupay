# Replay brief: arm F, implementation author

Your repository contains only what you need: `AGENTS.md`, this brief, and under `replay/`: `contract.md`, `failure-model.md`, `spec-F.md`, `scenario-format.md`, `observe.md` and `scenarios/`. `AGENTS.md` rules 2 to 7 apply to you; the files rule 1 names are not in this repository and you do not need them. Do not use the web, and do not look for files outside this repository.

## What you build
An implementation of the design, in `impl/`, in Go (`/usr/local/go/bin/go`), using the standard library and `gopkg.in/yaml.v3` only. Use no library that implements leader election, log replication or membership change: build the design from the specification.
- Members as concurrent processes exchanging messages through a network layer the runner controls, so that every failure-model cell can be injected.
- A runner that compiles a scenario file into fault injection and administrator requests against the running system, and records events as `replay/observe.md` describes.
- Checkers for J1.1, J1.3 and J1.5 over the recorded events.
- `impl/run.sh <scenario-file> --seeds N` prints, per seed, `PASS`, `FAIL <clause>` or `UNEXPLAINED <reason>`, and writes the observe file. `impl/run.sh --mutations --seeds N` runs every mutation against its scenario.

## The rules (the same for every author)
1. **Build the design in `replay/spec-F.md` exactly as written.** Its opening paragraph is part of this brief: where it says how something is done, do it that way, even if you believe another way is better; if you believe the design is wrong somewhere, record that and build what is written; where it is silent, choose, and record the choice.
2. **An unmutated failure is a result.** Do not change the artifact to make it pass without naming, in your README, the clause, cell or specification sentence you believe you misread.
3. **The steward may run scenarios you have not seen, under any name.** Your runner must accept a scenario file by path and must not refuse a scenario because of its name.
4. **Mutations.** For every shared scenario, write a mutation: a deliberately broken copy of your artifact, selected by a flag, that should fail that scenario's clause. Commit, before your first run, your predicted outcome for every shared scenario and every mutation.
5. **README sections.** Before your first run, commit **Choices** (every place the specification left open, and what you chose) and **Concerns** (anything in the design you believe is wrong, from reading alone, with the shape of a scenario that would show it; "none" is an answer). After your runs, add **Concerns after running** and **Declared limitations** (shapes of scenario your artifact would mishandle, and why you left them).
6. **Determinism.** A seed fixes every choice the runner and the scheduler make, and time is the scheduler's: no outcome may depend on wall-clock time or real elapsed time, and the same scenario with the same seed gives the same outcome every time. Run at least three seeds per scenario.

## Order
1. Commit Choices, Concerns and your predictions.
2. Build; run every shared scenario and every mutation with `--seeds 3`.
3. Add the after-running README sections; commit; tag the commit `first-version`. That tag is the version that is scored. You may keep working after it; later commits are reported but not scored.
4. Report: the `first-version` hash, the results of every run, your predictions beside them, and your wall-clock time.

Commit normally; this repository timestamps every commit.
