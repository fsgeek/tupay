# D1: dependency contracts of Raft, searched blind (design, draft 1)

Steward's design, 2026-10-25, before any source is fetched or any search made. Not a pre-registration; the prereg follows phase 0 and is committed before phase 2 starts. derives: log 2026-10-25 "the seventh steward accepts", items 1, 4, 8, 9.

## Question
Pointed at the service contracts a consensus protocol relies on from its environment, does tupay's workflow find a violation that breaks a real implementation and that nobody has reported? A blind rediscovery of a reported one is reported too, as a weaker result: it shows the workflow can find a bug when no one tells it where, not that it found something new.

## Why blind, and how the order makes it so
Tony (2026-10-25): evidence found by other means and then credited to the workflow is theater. So no step that chooses where to look may use knowledge of reported bugs. Every step's output is committed (OTS-stamped by the hook) before the next begins, and **no search for prior reports happens until a finding exists**. The steward knows the 2015 membership-change defect, the general argument about lease reads and clocks, and the twelve entries of `docs/steward/candidates-2026-10-23.md` (etcd-io/raft#166 among them); this is a residue the order cannot remove, and the steward makes no choice in phase 1 that this knowledge could steer.

## Phases
0. **Enumeration.** Two fresh instances of two non-Claude families (Codex and Grok, in `author-sandbox.sh`, no web), each given only the text of Ongaro's dissertation (*Consensus: Bridging Theory and Practice*, 2014) and a brief. Each lists every service contract Raft relies on from its environment (storage, network, clocks and timers, processes and restarts, identity, configuration and operators, the state machine, the host), with: the text that states or implies it (section), stated or implicit, what violating it in a deployment looks like, whether an implementation could detect the violation at run time, and its own rating of how often real deployments violate it silently. Two families, not one (counsel: run both): the union is the cell list, each cell tagged by who found it; the difference between them is reported.
1. **Selection by a rule, not a reader.** Every enumerated contract becomes a failure-model cell (F-ids, never reused). Which cells phase 2 pursues first is decided by a rule registered before enumeration output is read: the enumerators' own silent-violation ratings, ties broken by detectability (undetectable first). The steward does not add, drop or reorder cells.
2. **The workflow.** Contract (Raft's safety and liveness promises) and failure model (the cells) as inputs, as in M1 to X3: a model author (TLA+, environment actions for each violated cell) and an implementation-side author of a different family who builds the injection harness against a **real, widely deployed implementation**, chosen by a rule registered in the prereg; paired tests with mutation pairs; the observability layer on the real system. A divergence or a contract violation is a candidate finding.
3. **Finding, then search.** Only now: a literature and issue-tracker search for prior reports of each finding. Novel findings go to the implementation's maintainers, third-party judges tupay does not control. The commit order from phase 0 to the finding is published with it.

## What this does not claim
A violation found under a broken assumption can be dismissed as "you broke the precondition". The result that matters is a contract real deployments violate silently and the implementation never checks (cf. Tony's OSR FSDK processor-groups bug). Whether a cell is of that kind is reported from the enumerators' ratings and the maintainers' response, not asserted by the steward.

## Open, decided in the prereg
The implementation under test and the rule that picks it; the phase 1 rule's exact form; budget; whether the replay's exploration gap (log 2026-10-25 item 4) needs a directed explorer in phase 2, and how that explorer is kept blind.
