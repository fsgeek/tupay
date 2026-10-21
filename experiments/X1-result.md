# X1 result: contract change, additive clause (reads are fenced)

Scored 2026-10-21 against `experiments/X1-prereg.md` (commit 7556e40) with Amendments B and C. Arms: **A** (adapt, the M1 authors resumed), **R2** (regenerate, fresh instances, self-contained inputs; the scored regenerate arm), **R1** (regenerate, fresh instances, delta inputs; reported, not scored, per Amendment B). All steward runs are the first runs after each arm's merge, before any fix. Evidence under `experiments/X1/`.

## Measures
| Measure | A model | A impl | R2 model | R2 impl | R1 model | R1 impl |
|---|---|---|---|---|---|---|
| 1(a) shared schedules (19; impl × 3 seeds) | 19/19 | 57/57 | 19/19 | 57/57 | 19/19 | 57/57 |
| 1(b) mutations killed | 18/18 | 54/54 | 18/18 | 54/54 | 18/18 | 54/54 |
| 1(c) hold-out H4–H6 (never seen by any author) | 3/3 | 9/9 | 3/3 | 9/9 | 3/3 | 9/9 |
| 1(c') hold-out H1–H3 | 3/3 | 9/9 | 3/3 (contaminated, Amendment C) | 9/9 (contaminated) | **2/3, H3 FAIL C1_4** | 9/9 |
| 1(d) untraceable decisions (steward's checker, writes and reads) | 0 | 0 | 0 | 0 of 147 | 0 | 0 |
| 1(e) M1's P10 defect recurs | no | | no | | no on P10; a sibling stall on H3 (judge D4) | |
| 2 divergences, shared / hold-out | 0 / 0 | | 0 / 0 | | 0 / 1 (H3, explained, locus model) | |
| 3 author wall-clock | 13 min | 10 min 15 s | 35 min | 14 min 25 s | 55 min | 20 min 5 s |
| 3 author tokens (harness-reported, approx.) | 42k | 110k | 197k | 127.5k | 180k | 164k |
| 4 residue: read-path elements without a C2 tag | **1** (`run.py` mutation list tag) | 0 | 0 | 0 | 0 | 0 |
| tag coverage (files with `derives:`) | 100% | 100% | 26/26 | 9/9 | 25/25 | 13/13 |

Decisions asked of Tony during X1: 0. Interruptions: 0. Steward wall-clock for X1 (inputs, schedules, briefs, four plus two checkouts, merges, runs, judge, scoring): about 2 hours 10 minutes, of which about 25 minutes were spent on the two steward errors below.

Every author in every arm committed its predictions before building and reported every prediction met, and the steward's runs reproduced every author's claim. The library choice differed within a family: R2's implementation author chose etcd raft where the M1 and R1 authors chose HashiCorp Raft.

## The one divergence: D4, R1 on hold-out H3
Judge: Gemini 4 Argon, packet inlined (`experiments/X1/judge/`). **Explained, locus model.** Mechanism, from the TLC lasso: the grantor is isolated with the holder; the majority elects term 2 and grants; the partition heals but the old term-1 leader never steps down (the author's interpretation I3); the term-2 leader then crashes; the live pair is a deposed lower-term leader and a higher-term follower; `GrantTo` needs a quorum whose terms are at most the leader's, which the follower violates, and `Elect` is blocked for both because a connected node still claims leadership. The implementation's Raft steps the stale leader down and elects term 4. The judge classes it as a **different stale-leadership mechanism** from M1's P10 (there the current leader could not raise a lagging follower; here a deposed leader blocks a higher-term follower), not the same defect.

## Predictions scored
- **X1-1** (adaptation wins; A's author cost below half of R2's on both sides): **adaptation wins under the scoring rule.** A's correctness equals R2's on every item 1(a)–1(e), and A's author cost is lower on both sides. The "below half" clause holds on the model side (13 vs 35 min; 42k vs 197k tokens) and **fails on the implementation side** (10 vs 14.5 min; 110k vs 127.5k tokens). Scored: first clause confirmed, second clause half-confirmed.
- **X1-2** (R's model reintroduces the P10-class defect on shared P10; stated p = 0.6): **not confirmed.** Neither fresh model fails shared P10; R2's grant rule records on any majority, and R1's handles the P10 case by raising terms in `GrantTo`. R1's H3 stall is a sibling, by the judge's reading, caught only by a hold-out.
- **X1-3** (A ≤ 1 divergence on the shared set; R ≥ 1): **first half confirmed, second half falsified.** R2 has zero on the shared set, and so does R1.
- **X1-4** (A leaves ≥ 1 under-tagged read-path element; R leaves none): **confirmed.** A's model runner's mutation list runs eighteen mutations under a tag naming twelve. Both regenerate arms have none. A's author also caught and fixed a second instance before committing (the runner's schedule list), recorded in its own outcome section.
- **X1-5** (hold-out: model sides equal; A's impl ≥ R's): **confirmed** on H4–H6 (3/3 and 9/9 everywhere).
- **X1-6** (at least one hold-out divergence in at least one arm): **confirmed only through R1**, the delta-input arm, on H3. Neither scored arm has one on H4–H6. Reported with that caveat.
- **X1-7** (no author reads C2.2 as "current at ack time"): **confirmed.** Every author took the value at the moment of serving (A model X1.4; A impl 59; R2 impl 9; R2 model I-series; R1 impl 5).

## What regeneration discards, and what it finds (measure 5, reported)
Discarded by R2 relative to A, by the steward's reading of the READMEs: the M1 history (the P10 stall and its fix) and 49 recorded interpretations, of which R2 re-derived most, contradicted none that the steward could identify, and omitted the ones about the M1-era interfaces (trigger arming before v2, alias scope) because v2.1 had closed them. Found by regeneration and not by adaptation: R2's model author reported a **schema gap** (acks carry no operation id, so a retried request's acks are distinguishable only through `causes`), which no adapt author noticed in three rounds; tessera's finding E-02 (`docs/requests/2026-10-21-from-tessera-evidence-offer.md`) is the same mechanism in a real service. R1's model author, building from a delta, reconstructed the four v1 clauses correctly and said so. Fresh eyes found a defect in the interface; carried history avoided a defect in the artifact.

## Steward errors in X1, both on the record
1. **Delta inputs** (Amendment B): `contract/v2.md` and `tests/pairs-v2.md` referred to v1 by id; the regenerate arm had no v1. Cost: arm R1 confounded; arm R2 run; about 50 minutes of author time and ~340k tokens that would not otherwise have been spent. Rule now: a versioned input is self-contained.
2. **Hold-out leak** (Amendment C): H1–H3 entered `testbed/schedules/` through a blanket `git add` and reached R2's checkouts. Cost: H1–H3 unusable for R2; H4–H6 written and registered. Rule now: hold-outs run from a scratch worktree, never from the main checkout.

## Residues for the next interface revision (v2.2)
- Rule A1: `restart: non-grantor` must name the node the most recent `crash: non-grantor` crashed; the format defines `non-grantor` as an up node. Flagged independently by all four fresh-arm authors.
- Schema: `WriteAck` and `ReadAck` should carry the operation they answer (R2 model; tessera E-02).
- Measure 4 should also count an element whose code was adapted and whose tag was not, since that is the residue that actually occurred.

## Conclusion
Under the pre-registered rule, **adaptation wins X1**, on equal correctness and lower cost, with the cost margin on the implementation side small and the "below half" clause failing there. The clearest evidence for what adaptation keeps came from the unscored arm: a fresh model that passed every shared schedule and every mutation stalled on a hold-out through a stale-leadership mechanism the original model's history had already taught the adapting author to avoid. The clearest evidence for what regeneration gives came from the scored arm: a fresh author found a gap in the steward's schema that three rounds of adaptation had not. X2 next, with the interface revision first.
