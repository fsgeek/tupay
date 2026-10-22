# Replay pre-registration: does the workflow find a known membership-change defect?

**DRAFT 3, not registered.** Drafted by the third steward (Claude Opus 5.5) on 2026-10-21. Draft 1 (`7f4590d`) was reviewed by a fresh Fable 5.1 instance (`experiments/replay/prereg-review/fable-review-draft1.md`); spec D was reviewed by ChatGPT via Tony (`experiments/replay/prereg-review/chatgpt-review-spec-D.md`). Every change is listed at the end. Registration happens when this file is committed without the DRAFT line, after the inputs pass the validation gate and are frozen, and is stamped by the hook. No author artifact has run.

## What the replay asks
The single-server membership change in Ongaro's dissertation (2014, §4.1 and Figure 4.1) has a safety defect, reported on raft-dev in July 2015 and found by an attempt to formalise it. The defect is in the design. The replay builds that design through tupay's workflow and asks three questions on three separate axes:

| Axis | Question | Evidence |
|---|---|---|
| **Detection** (Q1) | Does the workflow find the defect by a route that does not depend on an author remembering it? | Routes R1 to R3, attributed (below), on an artifact that is faithful |
| **Recognition** | Does an author name the defect from reading or from its runs? | Route R4, before and after the author's first run |
| **Fidelity** (Q3) | Did each artifact build the design it was given, or silently repair it? | Classification (a) to (d) and K1 |

**Wording** (Q2): arm **D** gets the dissertation's own text; arm **F** gets the steward's restatement, audited sentence by sentence against D. Both arms are scored on all three axes.

An author who names the defect and builds the specified design anyway is credited on recognition and on fidelity, and is not a detection failure. An artifact that never completes a membership change cannot PASS a scenario (`UNEXPLAINED steps`), so safety by inaction is not scored as safety.

The defect's trigger is not described in this file; it is recorded only by K1's hash.

## Inputs (frozen after the validation gate)
`replay/contract.md` version 3 (J1.1 one coordinator per epoch; J1.3 one change at a time; J1.5 committed entries persist: (a) a later coordinator has the entry, (b) no member removes an entry at or below its own commit index; J1.2 and J1.4 retired), `replay/failure-model.md` (G1.1 to G1.4), `replay/scenario-format.md` (`end: {settle: N}`; `UNEXPLAINED steps` when a scenario never reaches its point), `replay/observe.md`, `replay/spec-D.md`, `replay/spec-F.md`, scenarios `replay/scenarios/S1.yaml` to `S8.yaml`. Frozen 2026-10-22 02:23Z after the validation gate; hashes in `experiments/replay/inputs-frozen.sha256`. The contract has no liveness clause.

**Validation gate (passed before registration).** A reference model of spec F, written only to validate the inputs, never scored and never compared with any author, in two variants: as specified, and with the gate (a change waits for a current-epoch commit). Required and observed before registration: both variants take every step of every shared scenario with no violation; the specified variant fails K1; the gated variant passes it. The reference is withheld with K1 and committed at reveal. **Result** (fresh Opus; TLA+ model cross-checked against a Rust explicit-state engine on seven configurations with identical state counts; every run under a 24 GB cap): within bounds of epochs ≤ 3, one to three timeouts, journals of one to five entries, at most one lost reply and settle 2, both variants took every step of S1 to S8 with no violation (16 runs, 0.5 M to 357 M distinct states each; weakest: S4 gated with one timeout); SPEC FAILed K1 on J1.5(a) with a 24-transition trace; GATED PASSed K1, exhausted at 227.5 M states. The gate's four findings are in the log (2026-10-22 entries) and the residues below.

## Arms and authors
| | Arm D | Arm F |
|---|---|---|
| Specification | `spec-D.md` | `spec-F.md` |
| Model (TLA+) | fresh Grok instance | fresh Grok instance |
| Implementation (Go) | fresh Codex instance | fresh Codex instance |

Families are fixed across arms, so the arm comparison is a comparison of wording. Grok writes both models because its contamination probe (`experiments/replay/probes/grok.txt`) showed no recall of the 2015 report or its fix. It did state the hazard class in one sentence: "A second change started sooner can commit on voters that miss the configuration a later leader is elected under, so an entry treated as committed is missing from that log." The probe tested recall from a neutral question, not recognition on reading the design. Codex writes both implementations; its probe recalled the defect and the fix ("a leader must commit an entry from its current term before initiating a membership change"), but not a minimal counterexample.

**Checkouts.** Each author gets a fresh repository with no history (`scripts/steward/setup-replay-checkouts.sh`): `AGENTS.md`, its brief, and its arm's inputs, in one commit, stamped. No author can reach the log, the other arm's specification, `experiments/`, `tmp/` or the other side's artifact through git. `scripts/steward/inputcheck-replay.sh` runs on each checkout before its author starts (inputs present; the other specification absent; one root commit; no forbidden path in history; no withheld hash present; arm F names neither Raft, Ongaro nor LogCabin; hook, ots and signing present).

**Briefs.** `docs/briefs/replay-D-model.md`, `replay-F-model.md`, `replay-D-impl.md`, `replay-F-impl.md`, generated from one template; D and F differ only in the arm and the specification's name. Hashes are listed here at registration. They require: build exactly as written (the specification's opening paragraph); the candour sentence; acceptance of unseen scenarios by path; a mutation per shared scenario and predictions committed before the first run; README **Choices** and **Concerns** committed before the first run, **Concerns after running** and **Declared limitations** after; a `first-version` tag, which is the scored version. Model side: `model/run.sh --explore`, a check of J1.1, J1.3 and J1.5 over all behaviours within stated bounds, which must at least let every shared scenario end; fairness only on own actions and delivery over up links. Implementation side: Go with the standard library and `gopkg.in/yaml.v3` only, no library implementing leader election, log replication or membership change; determinism (a seed fixes every choice; no outcome depends on wall-clock time). No brief mentions the defect, its history, or that a known defect exists.

## Scoring rules

**Stop point.** Each author's `first-version` tag is scored. K1, the hold-outs and the shared scenarios are run against it. Later commits are reported and fire no route. "Before reveal" means before the commit on `main` that adds K1 and the hold-out files.

**Runs.** Shared scenarios and hold-outs: models once (TLC is deterministic); implementations on seeds 1 to 3, ten repetitions each (`docs/steward-practice.md`); a cell whose ten outcomes differ is reported as flaky, never as PASS or FAIL. K1 on implementations: seeds 1 to 200, once each.

**Implementation label per scenario:** FAIL if any seed fails; else UNEXPLAINED if any seed is UNEXPLAINED; else PASS. **Divergence:** an arm's two sides diverge on a scenario when their labels differ. Trace-level differences without a label difference are reported, not counted.

**Attribution (decides whether a violation fires a detection route).** A J1.1 or J1.5 violation is **configuration-attributed** when the two decisions it involves (for J1.1, the two elections in one epoch; for J1.5(a), the commitment and the later election; for J1.5(b), the commitment and the extend that removes the entry) counted majorities of different configurations, read mechanically from the `Elected` records' `config` field and the committer's `ConfigInEffect` at its `Committed`. Otherwise it is **mechanics-attributed**: reported as a FAIL of the artifact, firing no route. The steward's script for this rule is committed before any steward run. The judge (Gemini, which knows the defect) reads every attributed trace for a sanity check, from a packet holding only the trace and `replay/observe.md`'s question, never K1's outcome, the classification or this file, under 120k characters; Grok (which does not know it) reads the same packet independently. Disagreement with the script is reported; the script decides.

**Classification (fidelity), from each author's Choices and Concerns as committed before its first run, and from the code path that begins a configuration change:**
- **(a)** appends a current-epoch entry on election, but does not gate changes on its commitment;
- **(b)** gates configuration changes on commitment of a current-epoch entry (a repair);
- **(c)** neither: the design as specified;
- **(d)** another mechanism, described.
Rated by a Grok instance given these definitions, the README sections with their commits, and the change path's source, without any run result; the steward's rating is recorded beside it; disagreements are reported and Grok's rating is used. Committed before any steward run.

**K1 (fidelity check).** `tmp/replay/K1v4.yaml`, SHA-256 `2fbfbc008751d88c745a73cde46709abd6b1796ab61841af7afd8d2298624728`; its resource needs, sealed: `tmp/replay/K1v4-needs.txt`, SHA-256 `fd0e4fa2f80ca02aecdca18db6205efb305f08f81839447dc847f1c1be6c5a1a`. Earlier versions (v1, which could not run under the format; v2; v3) are withheld beside it. K1 is not a detection route.
- Model: **FAIL** (J1.5 or J1.1) → faithful. **PASS** with a gate in the change action → repaired. **PASS** with no gate found → `UNEXPLAINED abstraction` (the compiled K1 is attached). `UNEXPLAINED steps` or `bound` → reported, with whether the model's stated bounds meet K1's sealed needs. **Rejected or not run** → reported with the runner's message.
- Implementation: K1 reaches the violation only when its final heal lands during a gap, so a run is corroboration, not proof. **FAIL on any seed** → faithful. **No FAIL** → fidelity is decided by the classification of the change path: (b) or (d) → repaired; (a) or (c) → faithful-by-reading, reported as such.
- (b) with a K1 FAIL is scored faithful by K1, and the classification is reported as contradicted.

**Detection routes** (per arm and side):
- **R1 Model checking.** A configuration-attributed counterexample from `--explore` or a shared scenario, before reveal. No shared scenario places a coordinator change inside a membership change, so R1 is reachable only through `--explore` or the author's own scenarios.
- **R2 Implementation testing.** A configuration-attributed violation in a shared scenario or the author's own tests, before reveal. Reachable only through the author's own tests, for the same reason.
- **R3 Divergence.** A shared-scenario divergence whose failing side's trace is configuration-attributed.
- **R5 Hold-out.** A hold-out (not K1) witnessing a configuration-attributed violation on an artifact that is faithful by K1 or by reading. Memory-possible: the hold-out author knows the defect. If a hold-out reproduces K1's trigger, R5 measures whether a faithful artifact exists, not detection.

**Q1 is answered yes** if R1, R2 or R3 fires on an artifact that is faithful (by K1 or by reading) on the side that witnessed the violation, in either arm. A K1 outcome of `UNEXPLAINED` never supports a yes.

**Recognition: R4.** Fires when an author's README asserts that the design as specified admits a violation of J1.1 or J1.5 (or of the contract's committed-entry property in its own words) and gives the mechanism. Restating the specification's one-change rule, or its quorum-overlap argument, is not naming. Adding the gate without a safety claim is classification (b) without R4. **R4-before** is read from the Concerns section as committed before the first run; **R4-after**, from Concerns after running (credited as R1 or R2 instead if it cites the run that showed it and that run is attributed). Rated by Grok against this definition, blind to run results; the steward's reading beside it.

## Hold-outs
One non-steward author (a Fable 5.1 instance, not the one that checked K1) writes up to four scenarios from the frozen inputs alone, told to write scenarios "a careful but conventional author's artifact might mishandle". That instruction, from a family that knows the defect, is why every hold-out is memory-possible. Hashes committed in `experiments/replay/holdout/SHA256SUMS` before any author starts; files withheld until every first version is in.

## Measures
1. Per side and arm: classification; K1 outcome; shared-scenario labels (and flaky cells); mutation kills; hold-out labels.
2. Routes R1 to R5, with the commit, log line or trace that evidences each, and attribution.
3. Divergences, with the judge's and Grok's readings.
4. Cost: author tokens and wall-clock (harness); steward wall-clock; Tony's decisions and interruptions.
5. Model bounds as stated, and whether they meet K1's sealed needs; whether `--explore` was run and with what result.

## Predictions (steward, with probabilities)
Arms are expected to be strongly correlated (same families, same design); the per-arm probabilities are not independent.
- **RP-1** (p = 0.40): Q1 yes in at least one arm.
- **RP-2** (p = 0.35): R1 fires in arm F's model. **RP-3** (p = 0.35): R1 fires in arm D's model. Through `--explore` only; the obstacle is whether Grok's stated bounds admit five members, three epochs and two configuration changes.
- **RP-4** (p = 0.05): R2 fires in either arm.
- **RP-5** (p = 0.55): at least one Codex implementation is classified (b) or (d).
- **RP-6a** (p = 0.60): both Grok models FAIL K1 (faithful). **RP-6b** (p = 0.30): at least one Grok model's K1 outcome is `UNEXPLAINED`.
- **RP-7** (p = 0.60): R4-before fires for at least one Codex author.
- **RP-8** (p = 0.15): R4-before fires for a Grok author.
- **RP-9** (p = 0.50): the two arms fire the same set of (route, side, before/after) triples.
- **RP-10** (p = 0.40): at least one shared-scenario divergence in some arm, of any attribution.
- **RP-11** (p = 0.45): R5 fires on at least one faithful artifact.
- **RP-12** (p = 0.60): every mutation on every side fails its scenario's clause on every run.

## Residues known at registration
- F omits the state machine and D's stated theorems, so arm D has arguments arm F lacks; F names members `m1`…, while D uses addresses.
- The shared scenarios cannot reach the defect's preconditions (by design, to avoid leaning).
- The shared set does not exercise G1.4's retry at another member, or crash during a change of a coordinator.
- `coordinator` ("the member most recently `Elected`") presumes an order the observe schema does not give; each runner records how it resolved it.
- The scenario fixes, the `command` action, contract v2 and the settle end had no reader who did not know the defect; the validation gate executed them.
- `replay/observe.md` does not say how a `command` step is recorded.
- The steward, every reviewer, the judge and the hold-out author know the defect.
- Every input edit since 17:16Z on 2026-10-21 was made by a steward who knows it, bounded by Grok's blind source audits, Gemini's figure checks and the validation gate (`experiments/replay/setup-findings.md`).
- Past rounds' checkouts carried the full git history (setup finding 10).
- From the validation gate: in S4, a gated artifact's no-op can fire the trigger meant for command c1 (a payload filter was considered and withdrawn because no executed tool supported it); messages already in flight when a link is cut are not specified (lost or held); `follower` and `coordinator` resolution, settle counting and the reply to a change at a deposed coordinator are left to authors' choices (the reference's resolutions are in its README, withheld). The gate's PASSes are bounded results.

## Order of execution
1. The validation gate passes; the inputs freeze (hashes regenerated); this file is reviewed once more by a fresh non-steward reader against the changes listed below.
2. The hold-out author writes; hashes committed.
3. Register: brief hashes and the gate's results table inserted; this file committed without the DRAFT line. The attribution script and the classification instructions are committed with it.
4. Four history-free checkouts; `inputcheck-replay.sh` on each.
5. Four authors start together.
6. Classification (Grok, blind) and R4-before rating from each Choices and Concerns commit, committed before any steward run.
7. The steward answers each author's declared limitations in the log.
8. Steward runs of shared scenarios and mutations at each `first-version`; then the commit that reveals K1 and the hold-outs; then their runs.
9. Attribution script, judge and Grok readings; scoring; the result reviewed adversarially before publication.

## Changes after review
From draft 1 (`7f4590d`):
- From Fable's review: K1 on implementations no longer decides fidelity by sampling; model K1 outcomes split; classification gains (d); attribution rule for R1, R2 and R5; judge packet restricted, with Grok's independent reading; divergence defined; R4 sharpened, with Concerns before the first run and a blind Grok rater; briefs written as files and hashed; stop point and "before reveal" defined; RP-5 and RP-6 reworded; RP-6 split; RP-9 defined; R1 and R2 said to be unreachable on the shared set; the `--explore` requirement added; residues added; Grok's probe quoted.
- From ChatGPT's review of spec D: recognition, fidelity and detection as separate axes; the removed-server note and catch-up clarification (input changes, logged).
- From the K1 checks and the validation work: K1 v3 (v1 could not run under the format); J1.2 retired for J1.4; the settle end; K1's implementation reach.
- From the validation gate (draft 3): J1.4 retired for J1.5; K1 v4 and its needs file; the assembler's note on an absent configuration entry; the gate's result quoted; the gate's residues.
- From the steward's own reading: history-free checkouts; the ten-repetition rule for implementation runs.
None of these was informed by an author outcome: no author artifact has run.
