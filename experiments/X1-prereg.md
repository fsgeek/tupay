# X1 pre-registration: contract change, additive clause (reads are fenced)

Registered 2026-10-21 by the steward, before any arm starts. Amendments are additive and say whether an outcome informed them. The repository is public at registration.

## The change
`contract/v1.md` → `contract/v2.md`: two clauses (C2.1 fence on reads, C2.2 the read's horizon), four observable events, no clause retired. `tests/pairs-v2.md` adds P13 to P18. Because the contract gains events, the interfaces gain an action and four events (`testbed/schedule-format.md` v3 addendum; `observe/schema.md` v2 addendum). The failure model is unchanged (v1). Under the hereditary fence, the change invalidates: nothing tagged only with C1.x or F1.x; everything that must now also derive from C2.x; and every compiler element that derives from the format's action list and the schema's event list. The stale-tag residue measure counts elements that enforce reads without a C2 tag.

In the vocabulary of the 2026-10-20 seed-log entry on indeterminacy: an unfenced read externalizes (H) before the fence resolves the token's validity (C). C2.1 moves C in front of H. C2.2 is the read's own horizon clause, the counterpart of C1.3.

## Arms
- **Adapt (A).** The current model author (Claude Opus 5.5, the same instance, resumed) and the current implementation author (Codex, the same session, resumed) each adapt their artifact from the merged v2.1 state, in isolation from each other, given `contract/v2.md`, `tests/pairs-v2.md`, the addenda, the six new shared schedules, and a one-paragraph brief. They keep their READMEs, predictions and history.
- **Regenerate (R).** A fresh Claude Opus 5.5 instance and a fresh Codex session, with no access to any prior artifact, README, log or result, each build from nothing given `contract/v2.md`, `failure-model/v1.md`, `tests/pairs-v2.md`, the interfaces, all nineteen shared schedules, and the M1 brief adjusted for v2. They never see v1 of the contract. Same families as arm A, so the arm controls for family (steward's decision of 2026-10-20).
- Both arms get the same shared schedules, written by the steward before either starts. Neither arm sees the hold-out set. Each author commits its predictions before building, as every author has so far.
- Isolation as in rounds 2 and 2.1: sparse checkouts excluding the other side's directory; for arm R also excluding `model/`, `impl/`, `experiments/` and `docs/` except the brief. Codex authors work in full clones with the signing configuration copied in.

## Measures (fixed here)
Per arm, per side, at the first steward run after the arm's merge, before any fix:
1. **Correctness.** (a) Shared schedules: PASS count of 19 (model) and of 19 × 3 seeds (impl). (b) Mutations: count of 18 that fail on their pair's shared schedule. (c) Hold-out: PASS count on the three hold-out schedules `experiments/X1/holdout/H1-H3.yaml`, committed at registration with SHA-256 `35ad1626…5191`, `e5560e3b…41c4`, `c08a86a6…4aa0`, and never shown to any author. (d) Provenance: untraceable decisions under `observe/provenance_check.py`, writes and reads. (e) **Known-defect recurrence:** whether the arm's model fails shared P10 the way the v1 model did (the `Join` defect, verdict D1).
2. **Divergence count** between the arm's two sides at first run, on the shared set, and separately on the hold-out set; verdicts by the judge of Amendment A as before.
3. **Cost.** Wall-clock and tokens per author (harness-reported); steward wall-clock for the arm's briefs, isolation, merge and runs; decisions asked of Tony; interruptions of Tony.
4. **Residue.** Count of elements on each side that enforce or test reads and carry no C2.x tag (under-tagging), and tags naming a retired id (none exist; expected 0).
5. **What regeneration discards** (reported, not scored): the count of recorded interpretations in arm A's READMEs that arm R re-derives, contradicts, or omits, by the steward's reading; listed, not summarized.

## Scoring rule for the standing prediction
"Adaptation wins" means: arm A's correctness on 1(a) to 1(e) is at least arm R's on every item, and arm A's author cost (3) is lower on both sides. If correctness is equal and cost is lower, adaptation wins. If arm R is more correct on any item, regeneration wins that item regardless of cost. Mixed results are reported as mixed.

## Predictions
- **X1-1.** Adaptation wins X1 (the seed's standing prediction). Author cost in arm A is below half of arm R on both sides.
- **X1-2.** Arm R's model reintroduces the P10-class liveness defect (fails shared P10). Basis: the v1 model fell into it naturally and the fix came only from a judged cross-run. Probability stated: 0.6.
- **X1-3.** Arm A has at most one divergence on the shared set at first run; arm R has at least one.
- **X1-4.** Arm A leaves at least one under-tagged element (a read-path element without a C2 tag) on at least one side; arm R leaves none. This is the predicted cost of adaptation.
- **X1-5.** On the hold-out set, the two arms are equal in PASS count on the model side; on the implementation side arm A passes at least as many as arm R.
- **X1-6.** At least one hold-out schedule produces a divergence in at least one arm.
- **X1-7.** No author in either arm reads the contract's C2.2 as requiring the value to be *current* at ack time (the contract says the value storage held when it served); if one does, it is a divergence with locus inputs.

## Order of execution
1. Commit this file, the inputs, the addenda, the six shared schedules, the hold-out set and the four briefs (this commit).
2. Merge and steward-run the v2.1 round first; arm A starts from that merge.
3. Run arm A and arm R concurrently, four authors, each isolated.
4. Merge each arm in one commit each (arm R into `model-regen/` and `impl-regen/` directories on a branch, not into `model/` and `impl/`); steward runs; hold-out runs; judge; score; `experiments/X1-result.md`.

## Not in X1
Family swap. Changing the failure model. Fixing anything before it is scored. Hold-out *cells* (removing failure-model cells); the hold-out here is schedules only.

## Amendment B (2026-10-21, 01:30Z; outcome-informed: yes)
Discovered from the regenerate-arm implementation author's report (its interpretation 1, "missing C1 clauses provisionally mean…", and its Blocked note): `contract/v2.md` and `tests/pairs-v2.md` referred to v1 by id without restating it, and arm R is deliberately given no v1. Arm R therefore built from a delta and reconstructed C1.1 to C1.4, the v1 events and P1 to P12 from the schedules, the schema and the pairs table's ids. This is a steward defect in the inputs, not in either author. Handling: (1) arm R as launched is reported as **R1, delta input**, scored on every measure, with this confound stated; it is also kept as an observation about regenerating from versioned-delta inputs. (2) Both v2 input files receive an additive restatement of v1 (no clause changes, ids unchanged). (3) A second regenerate arm, **R2, self-contained input**, is run with fresh instances of the same families from the amended inputs, and the standing prediction is scored against R2. Predictions X1-1 to X1-7 are unchanged and apply to R2; for R1 they are reported, not scored.
