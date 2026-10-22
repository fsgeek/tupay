# Replay result: does the workflow find a known membership-change defect?

**DRAFT** (fourth steward, Claude Opus 5.5, 2026-10-22). Scored against `experiments/replay-prereg.md` as registered (`b7e15b2`); every departure is listed under "Departures". Pending before this line is removed: arm F's `--explore` outcome (R1, RP-1, RP-2, RP-9) and an adversarial review of this scoring by a non-steward family. Evidence is in `experiments/replay/` and the log entries of 2026-10-22.

## Answer
**Q1 (detection): no** in arm D; arm F pending only on its `--explore`. No artifact, on either side, in either arm, witnessed the defect, by any route. **Recognition: no author named it** (R4 before and after: no, for all four). **Fidelity: every artifact built the specified design on its change path** (classification (c), all four, Grok and steward agreeing). **Wording (Q2): no difference was observable**: the arms fired the same (empty) set of routes, and differed only in arm D's two divergences, which the judges trace to input gaps rather than to wording.

The defect was not missed through repair or through misreading. It was missed because every artifact stopped looking before the defect's precondition:
- **Implementations** (Codex): faithful by reading; K1 on 200 seeds each produced no FAIL. The registration predicted this (K1 reaches the violation only when its final heal lands in a gap; prompt actions make that close to unreachable), and no author wrote a test aimed at its own concern.
- **Models** (Grok): both PASS K1 and every hold-out (`UNEXPLAINED abstraction`). Both authors tightened their bounds to fit the 24 GB cap, and the tightened bounds exclude the defect's precondition. Arm D's model forbids any election while any member holds an uncommitted configuration entry, compiles K1 at `MaxTerm = 2` against K1's need for epochs ≥ 3, and its `--explore` makes no membership change at all (all declared). Arm F's bounds meet K1's numbers; its declared campaign restrictions or atomic actions exclude the witness.

## Measures (registration "Measures")
**1. Per side and arm**

| | D model | D impl | F model | F impl |
|---|---|---|---|---|
| Classification (Grok / steward) | (c) / (c) | (c) / (c) | (c) / (c) | (c) / (c) |
| K1 | PASS → `UNEXPLAINED abstraction`; bounds do **not** meet K1's needs | no FAIL in 200 seeds (45 PASS, 155 UNEXPLAINED steps) → faithful by reading | PASS → `UNEXPLAINED abstraction`; bounds meet K1's numbers | no FAIL in 200 seeds (39 PASS, 161 UNEXPLAINED steps) → faithful by reading |
| Shared S1–S8 | all PASS | S6, S8 UNEXPLAINED; rest PASS; no flaky cell | S6 UNEXPLAINED; rest PASS | S6 UNEXPLAINED; rest PASS; no flaky cell |
| Mutations | 8/8 FAIL their clause | 24/24 cells, 10/10 | 8/8 | 24/24 cells, 10/10 |
| Hold-outs H1–H4 | all PASS | H1 UNEXPLAINED; H2–H4 PASS; no flaky cell | all PASS | H1 UNEXPLAINED; H2–H4 PASS; no flaky cell |

**2. Routes.** R1: arm D no (steward `--explore` PASS in 9 s within bounds that make no membership change); arm F pending. R2: no (no author test witnessed a violation; the shared scenarios cannot reach the precondition). R3: no (no divergence involves a violation). R4: no, all four, before and after. R5: no (no hold-out violation on any artifact).

**3. Divergences.** Arm D: S6 and S8 (model PASS, implementation UNEXPLAINED steps). Arm F: none. Judge (Gemini) and Grok, independently: (A) for both — the implementation's behaviour is permitted and the model's PASS rests on a choice the inputs leave open: S6, delivery after a cut of a message sent before it (registered residue); S8, `coordinator` resolution after a self-removal plus the absence of a retry (registered residues).

**4. Cost.** Authors (own reports and harness counts): D impl about 17 min, 94k tokens; F impl about 20 min, 125k tokens; D model first-version 08:09Z, 21.6 M tokens (20.3 M cached reads), 166 model calls; F model first-version 07:55Z, 25.3 M tokens, 193 calls. All started 05:45Z. Steward: one session; the model results sat unnoticed from about 08:10Z to 16:50Z (steward lapse, logged). Tony: one question that surfaced the lapse, one correction of the steward's context reading; no decision was needed from him.

**5. Model bounds.** D: scenario `MaxTerm` 2 (K1 compiled at 2), `MaxLog` 3, `MaxMsgs` 4, at most two candidates or leaders, no election while a configuration entry is uncommitted anywhere, one delivery order; `--explore` without crash, cut, drop or membership change. F: `MaxEpoch` 3, `MaxLogLen` 4, `MaxRounds` 3; a member campaigns only if in its own configuration, no other up member is a candidate, and no up coordinator of equal or higher epoch is reachable both ways; ballots and extends atomic. `--explore`: D PASS; F pending (four-hour limit fixed before launch).

## Predictions (registered, steward)
| | p | Outcome |
|---|---|---|
| RP-1 Q1 yes in either arm | 0.40 | pending (arm F `--explore`) |
| RP-2 R1 in arm F model | 0.35 | pending |
| RP-3 R1 in arm D model | 0.35 | falsified |
| RP-4 R2 in either arm | 0.05 | falsified |
| RP-5 a Codex implementation (b) or (d) | 0.55 | falsified |
| RP-6a both Grok models FAIL K1 | 0.60 | falsified |
| RP-6b a Grok model's K1 UNEXPLAINED | 0.30 | confirmed (both) |
| RP-7 R4-before, a Codex author | 0.60 | falsified |
| RP-8 R4-before, a Grok author | 0.15 | falsified |
| RP-9 same route triples in both arms | 0.50 | pending (so far both empty) |
| RP-10 at least one divergence | 0.40 | confirmed |
| RP-11 R5 on a faithful artifact | 0.45 | falsified |
| RP-12 every mutation fails every run | 0.60 | confirmed |

## Readings beside the score (not scored)
1. **The Concerns sections came closest, and nothing consumed them.** Both Codex authors wrote, before code, concerns that name the defect's ingredients (competing uncommitted configurations across a leadership change; the adjacent-pair argument not covering sequences of configurations with stale coordinators), withheld the claim, and wrote no test for it. Codex's contamination probe recalled the defect, so these are memory-possible. The workflow asks for Concerns and attaches no obligation to them.
2. **The defect lived where every author stopped looking.** Both models' bounds were chosen to fit the memory cap, and both exclude the precondition. A pre-run support audit, asking whether each artifact's checked space contains K1's witness at all, would have shown before scoring that R1 was impossible for arm D. Yupi's steward named this check independently (`docs/requests/2026-10-22-from-yupi-consistent-executions.md`).
3. **Fidelity held against recall.** Codex recalled the fix in its probe; both Codex authors wrote, before code, instructions to themselves not to repair what they suspected, and built the design as given.
4. **The divergences found the inputs, not the artifacts.** Both trace to gaps the steward had already registered as residues.

## Departures
- Arm F's model committed its Concerns together with the model (`1435384`), against the ordering rule as worded; only SANY parses preceded it. R4-before read from that commit.
- The implementations' Concerns commits contain `impl/README.md`, so "precede the first commit containing any file under `impl/`" cannot hold literally; read as "precedes any code".
- The isolation guard was extended to two routes the registration did not name (MCP servers; Grok's cross-session memory): open, unused, and in Grok's case empty.
- `--explore` time limit (four hours) set by the steward before launch; the registration gave none.
- Grok's harness transcripts were taken from its session store, since the registered capture (`--output-format plain`) held only final prose.
