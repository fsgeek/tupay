# Brief: hold-out schedules for a change experiment (X3)

You have one source, `packet.md` in this checkout: a service contract (v3), its failure model (v3), the schedule format with its addenda (v5 is current), the observability schema (v5 addendum current), the pair list (v4), and one example schedule. Read nothing else; you have no web access and need none.

Two independent teams will build, from exactly these inputs, a formal model and an implementation of the service. Each will run a set of shared fault schedules that both teams see. Your schedules are **held out**: neither team will see them before scoring. Their job is to catch a mistake a careful team could make that the shared schedules might not catch.

## Task
Write **four** hold-out schedules, `H11.yaml` to `H14.yaml`, in the format the packet defines (follow the example's shape), each exercising what the v3 inputs added or changed. Every schedule must be valid under the format's rules (A1 and A2, R1 to R3, L1 to L3, T1, E1, and the v5 addendum); a schedule that a correct artifact cannot run is worse than none. Each needs a `derives:` line naming the clauses and cells it targets.

For each, in `NOTES.md`, one section with:
- **Targets:** the clauses and cells.
- **Sequence:** what happens, step by step, in words.
- **Liveness premise:** after the last fault, which set stays connected, and whether more than half the configuration is eligible; or that the schedule promises nothing about liveness.
- **What a correct artifact must do:** the records or outcomes the contract requires, as precisely as the inputs allow; where the inputs leave a choice, say so.
- **Mistake it is meant to catch:** one or more plausible mistakes by a careful team, and why the shared pairs might not catch them.
- **P(at least one of two careful teams fails it):** a number and one line of reason.

Separately, under `## Input defects` in `NOTES.md`: anything in the inputs you found ambiguous, contradictory or unbuildable, with the text. Saying you found none is also an answer.

Write the files in the checkout root; do not commit (the steward collects them). At the end of your report: the files written and the output of `ls` and `git status`.
