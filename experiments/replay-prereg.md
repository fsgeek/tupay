# Replay pre-registration: does the workflow find a known membership-change bug?

**DRAFT, not registered.** Drafted by the third steward (Claude Opus 5.5) on 2026-10-21 against frozen inputs (`experiments/replay/inputs-frozen.sha256`, log entry "replay inputs frozen"). Registration happens when this file is committed without the DRAFT line, after the adversarial review in the last section, and is stamped by the hook.

## What the replay asks
The single-server membership change in Ongaro's dissertation (2014, §4.1 and Figure 4.1) has a safety defect, reported on raft-dev in July 2015 and found by an attempt to formalise it. The defect is in the design, not in any implementation of it. The replay builds that design through tupay's workflow (contract and failure model, a TLA+ model and an implementation written independently by different families, shared scenarios, mutation pairs, divergence) and asks:

- **Q1.** Does the workflow find the defect by a route that does not depend on an author remembering it?
- **Q2.** Does the wording of the specification matter? Arm **D** gets the dissertation's own text; arm **F** gets the steward's restatement, audited sentence by sentence against D.
- **Q3.** Are the artifacts faithful to the design they were given? An artifact that silently repairs the design cannot find its defect, and a model that does so creates an illusion of correctness (log, "the counterbalance").

The defect is not described in this file. Its trigger is recorded only by K1's hash (below). Every reader of this registration who knows the bug knows it from elsewhere.

## Inputs (frozen)
`replay/contract.md` (J1.1 one coordinator per epoch, J1.2 committed entries persist, J1.3 one change at a time), `replay/failure-model.md` (G1.1 crash and restart, G1.2 message loss and reordering, G1.3 partition, G1.4 administrative change), `replay/scenario-format.md`, `replay/observe.md`, `replay/spec-D.md`, `replay/spec-F.md`, shared scenarios `replay/scenarios/S1.yaml` to `S8.yaml`. Hashes in `experiments/replay/inputs-frozen.sha256`. The contract has no liveness clause.

## Arms and authors
| | Arm D | Arm F |
|---|---|---|
| Specification | `spec-D.md` | `spec-F.md` |
| Model (TLA+) | fresh Grok instance | fresh Grok instance |
| Implementation | fresh Codex instance | fresh Codex instance |

Families are fixed across arms, so the arm comparison is a comparison of wording. Grok writes both models because it is the only family whose contamination probe showed no recall of the defect (`experiments/replay/probes/`); Grok was calibrated on TLA+ (log, "Grok calibrated"). Codex writes both implementations; its probe recalled the defect and the fix ("a leader must commit an entry from its current term before initiating a membership change") but not a minimal counterexample.

Each author sees: its arm's specification, the contract, the failure model, the scenario format, the observe schema, the shared scenarios, its brief, and `scripts/hooks/`. No author sees the other arm's specification, `experiments/`, `tmp/`, the other side's artifact, or this file. Arm F authors never see D or the fidelity material.

Implementations are written from scratch in Go with the standard library and the YAML parser only: **no consensus or Raft library.** A library would bring its own membership-change rules, which is not the design given.

## Briefs (fixed here; the same in both arms except for the specification's name)
Every brief contains, verbatim in all four:
1. The specification's own opening paragraph (build exactly as written; record, do not fix, what you believe is wrong; where silent, choose and record).
2. The candour sentence: "An unmutated failure is a result. Do not change the artifact to make it pass without naming, in your README, the clause, cell or specification sentence you believe you misread."
3. "The steward may run scenarios you have not seen, under any name; your runner must accept a scenario file by path."
4. "Before your first run, commit a README section **Choices**: every place the specification left open and what you chose. After your runs, add **Concerns**: anything in the design you believe is wrong, with the shape of a scenario that would show it, and **Declared limitations**: shapes of scenario your artifact would mishandle, and why you left them."
5. Model side only: fairness only on a member's own enabled actions and on delivery over links that are up; bounds stated in the README with the reason for each. Implementation side only: the seeds rule (at least three seeds per scenario; a seed fixes the scheduler's choices, and wall-clock time does not decide any outcome).
6. Each side writes its own mutation for every shared scenario (a deliberately broken artifact that should fail the scenario's clause) and commits its predicted outcomes before its first run.

Nothing in any brief mentions membership-change defects, the dissertation's history, or the existence of a known bug.

## The defect's trigger, withheld
`tmp/replay/K1.yaml`, SHA-256 `a44ab3788b3b5780e8793d15dc5d64e3c70bb2e2957e1b4dccbe652a2259ce24`, written by the second steward, never committed until every author's first version is in. K1 is in the shared scenario format and drives the system into the defect's trigger. **K1 is a faithfulness check, not a detection route** (Q3): run against all four artifacts after their first versions; an artifact that does not violate J1.1 or J1.2 on K1 has built a repaired design. On the model side "does not violate" means TLC explores K1 exhaustively within the author's bounds and finds no violation; a bound hit is `UNEXPLAINED bound` and is reported as such, not as faithful or unfaithful.

## Hold-outs
One non-steward author (Fable 5.1, a family that knows the defect, so every hold-out is scored as a **memory-possible** route) writes up to four scenarios from the frozen inputs alone, with the instruction to write scenarios that "a careful but conventional author's artifact might mishandle". Hashes are committed in `experiments/replay/holdout/SHA256SUMS` before any author starts; files are withheld until every first version is in. No hold-out is written by the steward.

## Detection routes (scored separately, per arm and per side)
- **R1 Model checking.** A TLC counterexample to J1.1 or J1.2 on a shared scenario, or in an exploration the model author ran on its own initiative, before any hold-out or K1 is revealed.
- **R2 Implementation testing.** An implementation run that witnesses a J1.1 or J1.2 violation on a shared scenario or in the author's own tests, before reveal.
- **R3 Divergence.** Model and implementation of the same arm disagree on a shared scenario, and the third-family judge (Gemini) traces the divergence to the defect.
- **R4 Author naming.** An author's README names the defect (the trigger, or the gate that fixes it) as a concern. Scored **before** the author's first run (memory or reasoning, indistinguishable) and **after** (possibly prompted by its own runs; R1 or R2 is credited if a run is cited).
- **R5 Hold-out.** A hold-out scenario that is not K1 witnesses a violation on an artifact that is faithful by K1. Memory-possible (see Hold-outs).

**Q1 is answered yes** if R1, R2 or R3 fires on an artifact that K1 shows to be faithful, in either arm. R4 and R5 answer a weaker question (the workflow carried an author's or a hold-out author's knowledge to a result).

## The current-epoch entry: three outcomes, classified before any steward run
The specifications are silent on whether a new coordinator appends an entry of its own epoch on election, and on whether a change waits for one to commit. From each author's **Choices** section, as committed before its first run, the steward classifies the artifact:
- **(a)** appends a current-epoch entry on election, but does not gate changes on its commitment (the design as specified plus a common convention; the defect remains);
- **(b)** gates configuration changes on commitment of a current-epoch entry (a repair; the artifact is unfaithful by construction, and R4-before is credited if the author named it as a concern rather than a choice);
- **(c)** neither, or another mechanism (the design as specified; K1 decides).
The classification is committed before any steward run and is not revised after.

## Measures
1. Per side and arm: K1 outcome (faithful / repaired / UNEXPLAINED bound); shared-scenario outcomes; mutation kills; hold-out outcomes.
2. Routes R1 to R5 fired, with the commit or log line that evidences each.
3. Classification (a)/(b)/(c) per side.
4. Divergences on shared scenarios, with the judge's verdicts.
5. Cost: author tokens and wall-clock from the harness; steward wall-clock; Tony's decisions and interruptions.
6. Model bounds as stated, and whether any model ran an exploration beyond the shared scenarios.

## Predictions (steward, with probabilities)
- **RP-1** (p = 0.30): Q1 yes in at least one arm.
- **RP-2** (p = 0.20): R1 fires in arm F's model. **RP-3** (p = 0.20): R1 fires in arm D's model. Reason for the low value: the shared scenarios were written not to lean toward the trigger, and an unprompted Grok model is likely to check only the shared scenarios within small bounds.
- **RP-4** (p = 0.10): R2 fires in either arm. Sampling three seeds per scenario rarely reaches a narrow interleaving.
- **RP-5** (p = 0.55): at least one Codex implementation is classified (b) or fails K1's faithfulness check (repaired), in at least one arm. Codex recalls the fix.
- **RP-6** (p = 0.85): both Grok models are faithful by K1 (or UNEXPLAINED bound), none classified (b).
- **RP-7** (p = 0.50): R4-before fires for at least one Codex author.
- **RP-8** (p = 0.15): R4-before fires for a Grok author.
- **RP-9** (p = 0.60): arms D and F agree on every route (same routes fire, or none). If they disagree, the direction is reported without a prediction.
- **RP-10** (p = 0.40): at least one shared-scenario divergence in some arm, of any cause.
- **RP-11** (p = 0.50): at least one hold-out witnesses a violation on a K1-faithful artifact (R5).

## Residues known at registration
F omits the state machine and D's stated theorems, so arm D has arguments arm F lacks. F names members `m1`…; D uses addresses. Grok's probe tested recall, not recognition on reading the design. The steward, the registration's reviewers, the judge and the hold-out author all know the defect. `replay/observe.md` does not say how a `command` step is recorded (it covers `Fault` steps only). Every input edit since 2026-10-21 17:16Z was made by a steward who knows the defect, bounded by Grok's blind source audits and Gemini's figure checks (`experiments/replay/fidelity/`, `experiments/replay/setup-findings.md`).

## Order of execution
1. Adversarial review of this draft by a knowing reviewer outside the steward's family (ChatGPT, via Tony) and a second Claude instance; changes listed at the end of this file with whether any outcome informed them (none can: nothing has run).
2. Hold-out author writes; hashes committed.
3. Register (commit this file without the DRAFT line).
4. Four checkouts from `scripts/steward/setup-checkouts.sh`; `scripts/steward/inputcheck.sh` on each (inputs present, D and F not crossed, no hold-out or K1 hash present, hook and signing).
5. Four authors start together.
6. Classification (a)/(b)/(c) from each committed Choices section, committed before any steward run.
7. Steward runs: shared scenarios and mutations, then K1 and the hold-outs revealed and run, then K1 and the hold-out files committed.
8. Judge on divergences; scoring; result reviewed adversarially before publication.

## Changes after review
(none yet)
