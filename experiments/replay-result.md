# Replay result: does the workflow find a known membership-change defect?

**Scored** 2026-10-22 by the fourth steward (Claude Opus 5.5) against `experiments/replay-prereg.md` as registered (`b7e15b2`). An adversarial review by Codex (GPT; read-only; `experiments/replay/result-review/codex-review.log`) of the draft (`200c413`) found one scoring error (RP-12) and nine other faults of overstatement or undisclosed departure; all ten are accepted and corrected here, and listed under "Review". Evidence is in `experiments/replay/` and the log entries of 2026-10-22.

## Answer
**Q1 (detection): no**, in both arms. No artifact, on either side, in either arm, witnessed the defect by any registered route (R1, R2, R3, R5). **Recognition: no author named it** (R4 before and after: no, all four). **Fidelity:** both implementations are faithful by reading (classification (c), no K1 FAIL in 200 seeds); both models are `UNEXPLAINED abstraction` (PASS on K1 with no gate in the change action), which is the registered label, not a finding of fidelity for the whole model. **Wording (Q2):** both arms fired the same set of routes (the empty set). They differ elsewhere: arm D had two shared-scenario divergences and arm F none, and their models' bounds, K1 completion counts, exploration outcomes and costs differ.

What the evidence shows about why the defect was not found, by side (a reading, not a score):
- **Implementations** (Codex): the change path is the specified design, and K1 on 200 seeds produced no FAIL. The registration predicted this (K1 reaches the violation only when its final heal lands in a gap; prompt actions make that close to unreachable). Neither author wrote a test aimed at its own written concern.
- **Arm D model** (Grok): the exclusion is shown directly. It forbids any election while any member holds an uncommitted configuration entry, compiles K1 at `MaxTerm = 2` against K1's sealed need of epochs ≥ 3, and its `--explore` makes no membership change; all declared by its author.
- **Arm F model** (Grok): not determined. Its bounds meet K1's numbers; TLC exhausted K1 (256,545 distinct states) without a violation; its `--explore` did not finish. Its declared campaign restrictions and atomic actions are candidates for excluding the witness, but no run here shows which, if any, does; a modelling error elsewhere is not ruled out.

## Measures (registration "Measures")
**1. Per side and arm**

| | D model | D impl | F model | F impl |
|---|---|---|---|---|
| Classification (Grok / steward) | (c) / (c) | (c) / (c) | (c) / (c) | (c) / (c) |
| K1 | PASS → `UNEXPLAINED abstraction`; bounds do **not** meet K1's needs | no FAIL in 200 seeds (45 PASS, 155 UNEXPLAINED steps) → faithful by reading | PASS → `UNEXPLAINED abstraction`; bounds meet K1's numbers | no FAIL in 200 seeds (39 PASS, 161 UNEXPLAINED steps) → faithful by reading |
| Shared S1–S8 | all PASS (bounded) | S6, S8 UNEXPLAINED; rest PASS; no flaky cell | S6 UNEXPLAINED; rest PASS | S6 UNEXPLAINED; rest PASS; no flaky cell |
| Mutations | 8/8 FAIL; **7/8 on their scenario's clause** (S1's mutation, aimed at J1.1, FAILs J1.5: its message bound prevents the J1.1 witness, as its author wrote) | 24/24 cells, 10/10, own clause | 8/8, own clause | 24/24 cells, 10/10, own clause |
| Hold-outs H1–H4 | all PASS | H1 UNEXPLAINED; H2–H4 PASS; no flaky cell | all PASS | H1 UNEXPLAINED; H2–H4 PASS; no flaky cell |

**2. Routes.** R1: no in either arm (arm D: steward `--explore` PASS in 9 s, within bounds that make no membership change; author's own: PASS. Arm F: steward `--explore` `UNEXPLAINED bound`, stopped by the timeout after 4 h 08 min (17:19:36Z to 21:27:41Z) at 321 M distinct states, 229 M queued, depth 13, no violation; author's own: `UNEXPLAINED bound`, stopped by hand after 196 s). R2: no. R3: no (no divergence involves a violation). R4: no, all four, before and after. R5: no (no hold-out violation on any artifact).

**3. Divergences.** Arm D: S6 and S8 (model PASS, implementation UNEXPLAINED steps). Arm F: none. The judge (Gemini) and Grok, independently, both answered (A) for both (the implementation's behaviour is permitted; the model's PASS rests on a choice the inputs leave open). For **S6** both name the same choice: delivery after a cut of a message sent before it (a registered residue). For **S8** they differ: Gemini names initial-election order and the model's existential completion against the implementation's sampled run, with no retry after a rejected request (G1.4, a registered residue); Grok names a difference in `coordinator` resolution that the model's README does not support (the model uses the same "most recent `Elected`" rule). The implementation trace shows m3 elected first, removing itself, and a later request to m3 answered `not_leader`.

**4. Cost.** Authors (own reports and harness counts): D impl about 17 min, 94k tokens; F impl about 20 min, 125k tokens; D model first-version 08:09Z, 21.6 M tokens (20.3 M cached reads), 166 model calls; F model first-version 07:55Z, 25.3 M tokens, 193 calls. All started 05:45Z. Steward: one session, accepted 05:43Z, result scored about 21:45Z, of which about 8 h 40 min (08:10Z to 16:50Z) the model results sat unnoticed (a steward lapse, logged) and about 4 h was arm F's `--explore`. Tony: one question that surfaced the lapse, one correction of the steward's reading of its context figure; no decision was needed from him.

**5. Model bounds.** D (scenarios): `MaxTerm` 2 (K1 compiled at 2), `MaxLog` 3, `MaxMsgs` 4, at most one queued message per directed pair, at most two candidates or leaders, `m5` never becomes leader (it votes and accepts extends), no election while a configuration entry is uncommitted anywhere, one delivery order. D (`--explore`): the same, with no crash, cut, drop or membership change, terms ≤ 2, logs ≤ 3. F: `MaxEpoch` 3, `MaxLogLen` 4, `MaxRounds` 3; a member campaigns only if in its own configuration, no other up member is a candidate, and no up coordinator of equal or higher epoch is reachable both ways; ballots and extends atomic. F (`--explore`): `MaxCrashes` 1, `MaxAdmin` 3, `MaxLinkFaults` 4, commands `{c1}`, event cap 400.

## Predictions (registered, steward)
| | p | Outcome |
|---|---|---|
| RP-1 Q1 yes in either arm | 0.40 | falsified |
| RP-2 R1 in arm F model | 0.35 | falsified (under the steward's timeout; see Departures) |
| RP-3 R1 in arm D model | 0.35 | falsified |
| RP-4 R2 in either arm | 0.05 | falsified |
| RP-5 a Codex implementation (b) or (d) | 0.55 | falsified |
| RP-6a both Grok models FAIL K1 | 0.60 | falsified |
| RP-6b a Grok model's K1 UNEXPLAINED | 0.30 | confirmed (both) |
| RP-7 R4-before, a Codex author | 0.60 | falsified |
| RP-8 R4-before, a Grok author | 0.15 | falsified |
| RP-9 same route triples in both arms | 0.50 | confirmed (both empty) |
| RP-10 at least one divergence | 0.40 | confirmed |
| RP-11 R5 on a faithful artifact | 0.45 | falsified |
| RP-12 every mutation on every side fails its scenario's clause on every run | 0.60 | **falsified** (arm D model, S1: J1.5, not J1.1) |

Three confirmed, ten falsified.

## Readings beside the score (not scored)
1. **The Concerns sections came closest, and nothing consumed them.** Both Codex authors wrote, before code, concerns that name the defect's ingredients (competing uncommitted configurations across a leadership change; the adjacent-pair argument not covering sequences of configurations with stale coordinators), withheld the claim, and wrote no test for it. Codex's contamination probe recalled the defect, so these are memory-possible. The workflow asks for Concerns and attaches no obligation to them.
2. **A PASS is testimony about its bounds.** Arm D's model PASSed K1 from a space that could not contain the witness. A pre-run support audit (does the checked space contain the witness?) would have said so before scoring; it is now practice (`docs/steward-practice.md`). Yupi's steward named the check independently and will cite this record.
3. **Fidelity held against recall.** Codex recalled the fix in its probe; both Codex authors wrote, before code, instructions to themselves not to repair what they suspected, and built the design as given.
4. **The divergences found the inputs.** Both trace to gaps the steward had registered as residues.

## Departures
1. **Commit order (R4-before).** The rule ("the first commit containing a Concerns section must precede the first commit containing any file under `model/` or `impl/`") is not met literally by any author: arm D's model and both implementations put their README, the Concerns commit, under `model/` or `impl/` (no code in it); arm F's model committed its Concerns together with the full model. In every case only syntax parses (models) or nothing (implementations) ran before the Concerns commit; R4-before is read from it.
2. **Model coverage requirement not met.** The briefs required `--explore` bounds that at least let every shared scenario end. Arm F's model leaves S6 unfinished (`UNEXPLAINED steps`), and arm D's `--explore` excludes membership changes and faults. Both were declared by the authors and accepted as declared limitations; accepting them is a departure from the registered requirement. The labels stand.
3. **Raters were not blind to run results.** The registration says classification is rated "without any run result" and R4 "blind to run results", and also gives the rater the author's "Concerns after running", which reports the author's own runs. The packets carried those sections; the steward resolved the tension by including them without saying so. No rating is changed by it; the blindness claim is withdrawn.
4. **Isolation guard: partial coverage.** Both Grok transcripts begin after a context compaction. The pre-compaction part is covered by tool names and times (no MCP or web tool ran) and by the authors' scratch artifacts, not by tool arguments, so which paths early file reads touched is **unverified**. The guard also covered two routes the registration did not name (MCP servers, Grok's cross-session memory): open, unused, and in Grok's case empty. Grok's transcripts were taken from its session store, since the registered capture held only final prose.
5. **The `--explore` time limit** (four hours) was set by the steward before its runs, **after** the authors' outcomes were known, and was informed by one: arm F's author had stopped its own run after 196 s, still growing. Enforcement overran: the run ended 4 h 08 min after start. RP-2's non-firing holds under this stopping rule only.
6. **Judging.** The registration has the judge read "every violation trace". Only unmutated violations can fire a route, and there were none; the violation traces from mutations (deliberately broken artifacts) were not sent to the judge. The two divergences, which involve no violation, were sent under a rubric (A to D) written by the steward for the packet, not registered.
7. **Steward wall-clock** is given from the log rather than measured.

## Review
Codex's ten findings (`experiments/replay/result-review/codex-review.log`), all accepted: (1) RP-12 falsified, not confirmed; (2) the causal headline overstated, especially for arm F, and "differed only" too strong; (3) the model coverage requirement unmet and undisclosed; (4) raters not blind; (5) isolation guard's pre-compaction coverage unverified; (6) the S8 readings agree on (A) but not on the reason, and the A-to-D rubric unregistered; (7) the time limit set after outcomes were known, and overrun; (8) arm D's model also fails the literal commit-order rule; (9) mutation violation traces not judged; (10) steward wall-clock, authors' own exploration results and some stated bounds missing. Its list of items checked and found correct (input and brief hashes, scored versions, labels, repetitions, K1 counts, fidelity mapping, hold-outs, divergence count, routes, Q1, recognition, costs) is in the log.
