# X3 result: a new authority locus (configuration); amend versus rebuild

**DRAFT for adversarial review**, scored 2026-11-02 by the tenth steward (Claude Opus 5.5) against `experiments/X3-prereg.md` as registered. Arms: **A** (adapt: fresh instances inheriting `model/` and `impl/`) and **R** (regenerate: fresh instances from the inputs alone). Implementations by Codex in the sandbox; models by Claude Opus 5.5 on the box. Evidence under `experiments/X3/`; the log entries of 2026-10-25 to 2026-11-02 give the history. **X3's score is internal evidence:** every judge and rater is another model family, and no party outside tupay has scored it.

## Headline
**Mixed.** Adaptation does not win: arm A cost more tokens on both sides and more wall-clock on the implementation side. Regeneration does not win either: arm R is more correct on three items and arm A on three (one of them an artefact of the steward's check). One registered sentence makes X3-1a's own score self-contradictory under "mixed"; see X3-1a below.

## Measures
| Measure | A impl | R impl | A model | R model | more correct |
|---|---|---|---|---|---|
| 1(a) shared PASS of 59, registered conditions applied | 59 | 59 | **46** (13 "no support": P8, P17, P19, P22 to P25, P28 to P30, H7, H9, H10) | **50** (P63 FAIL C3.4; 8 clock rows vacuous by design: P32, P41, P44, P47, P50, P53, P59, P62) | impl tie; **model R** |
| 1(b) mutations killed of 54 | 54 (56/56 with two extras) | 54 (every run) | **41** (13 unassessable: no support; extra P49a PASSes) | **53** (P12 `UNEXPLAINED end unreachable`) | impl tie; **model R** |
| 1(c) hold-outs H11 to H14 PASS | **1** (H12; H11 and H14 refused by an exactly-two-clients rule, H13 UNEXPLAINED 30/30) | **4** | **4** | **1** (H14; H11, H12 vacuous by design; H13 TLC disk-write abort) | **impl R**; **model A** |
| 1(d) untraceable decisions, registered `provenance_check.py` | **0** | **80** (P7, P16) | 4 | 4 | **impl A** (artefact; see below); model tie |
| 1(d) beside: `provenance_check_v5.py` | 0 | 0 | 0 | 0 | tie |
| 1(e) distinct C1.4/C3.4 stall mechanisms (judge) | 0 | 0 | **0** | **1** (R-P63, genuine C3.4) | impl tie; **model A** |
| 1(f) replay part 1 and 2 reports, shared and hold-out traces | 0 | 0 | 0 | 0 | tie |
| 8 `UNEXPLAINED inputs` (groups, decisions) | 0, 0 | 0, 0 | 0, 0 | 0, 0 | tie (models by construction) |
| 2 divergences, shared / hold-out | | | | | A: 0 / 3 (H11, H13, H14); R: 1 (P63) / 1 (H13) |
| 3 author tokens (total) | 7.34M | 3.33M | 120.6M | 89.4M | |
| 3 author wall-clock | 25 min | 14 min | 5 h 08 | 5 h 26 | |
| 4 residue | 2 | 0 | 0 | 0 (1 if an exclusion is refused) | |
| 5 of the 35 baseline schedules, still PASS (part of 1(a)) | 35 | 35 | 22 (13 no support) | 35 | |
| 6 propagation fraction (DeepSeek / Kimi) | 0.56 / 0.78 | | 0.08 / 0.67 (kappa 0.09) | | |
| 7 interpretations contradicted (DeepSeek / Kimi) | 15 / 9 of 85 | | 6 / 5 of 46 | | |
| 9 planted defect caught | yes (C1.2) | yes (C1.3) | yes (C1.1) | yes (C1.2) | |
| 10 (i) a check flags / (ii) steward names | no / yes | yes / yes | | | |

Files: 1(a) to 1(c) `runs/*/schedules.txt`, `runs/*/mutations.txt`, `audit/{A,R}-verdicts.txt`; 1(d) `runs/*/provenance{,-v5}.txt`; 1(e) and 2 `judge/RULINGS.md`; 1(f) and 8 `runs/*/replay-*.txt`; 3 `measure3-cost.md`; 4 `residue/RESULT.md`; 6 and 7 `raters/RESULT.md`; 8's design fact `measure8-design-fact.md`; 9 `plants/RESULT.md`; 10 `recon/RESULT.md`.

## Readings the registration forced, stated
1. **Vacuous by design, two registered sentences in conflict.** Departure 3: a model side that does not model a quantity a row needs is "vacuous by design for that schedule: reported, not PASS". Measure 8: a side whose grant path consults no clock "passes the F3.2 schedules and P44 vacuously as to clocks: counted as PASS (the contract permits it), reported as vacuous by design". Arm R's model has no clock. **Primary reading here: Departure 3 for the support audit**, because 1(a)'s model PASS is conditioned on the audit by name ("a model PASS also needs its support audit (Departure 3)"). Measure 8 governs the clock design fact. **Beside, under measure 8's reading:** R model 1(a) 58, 1(c) 3. **Neither reading changes any "more correct" cell**: R model 50 or 58 against A model 46; A model 4 against R model 1 or 3.
2. **1(b) and vacuity.** The registration makes a *failed* audit's mutation unassessable and says nothing about vacuous rows; R model's eight vacuous pairs are counted as assessed (all eight killed). Beside, if they were unassessable: 45 of 54, still above A model's 41.
3. **1(d) is an artefact.** Both judges found the registered `provenance_check.py` keys records by `(proc, seq)`, not schema v5's `(proc, inc, seq)`, so R impl's 80 are valid chains after a client restart, and the model sides' 4 each are the same defect (arm A's model README declared it; log 2026-10-27). Under the corrected check every side is 0. The registered score stands, and "A more correct on 1(d) impl" **is a fact about the steward's instrument, not about either arm**.
4. **1(e).** Counted as stall mechanisms the judge names as genuine C1.4 or C3.4 violations: R-P63 only. A-H13's run blocks under T3, but both judges call it explained with no genuine violation (Gemini locus implementation, Kimi interface). If it were counted, the impl cell becomes A 1 / R 0, R more correct.

## Scoring rule
"Adaptation wins" needs arm A at least as correct on every item of 1(a) to 1(f) and 8, and cheaper in tokens and wall-clock on both sides. **Cost fails** (tokens on both sides, wall-clock on impl). Item by item: **R strictly more correct** on 1(a) model, 1(b) model, 1(c) impl; **A strictly more correct** on 1(c) model, 1(d) impl (instrument artefact, reading 3), 1(e) model. Ties elsewhere. **Mixed.** In the rule's required words: **arm A is strictly more correct on 1(c) model, 1(d) impl and 1(e) model, and more expensive.**

## Predictions
| | prediction | p | outcome |
|---|---|---|---|
| X3-1a | adaptation does not win under the rule | 0.75 | **contradictory registration**: by its own words, confirmed (adaptation does not win). The scoring-rule section also says "Mixed is reported as mixed and scores X3-1a as **not confirmed**", a sentence carried from X1, where the first prediction was "adaptation wins". Under that sentence: not confirmed. Both are reported; the steward does not choose. |
| X3-1b | regeneration wins (R at least as correct everywhere, strictly more somewhere) | 0.4 | **not confirmed** (A strictly more correct on three items; on two of them without the artefact) |
| X3-2 | an unmutated side violates C1.1, C3.7 or C3.8 on P48, P60 or P63 | 0.45 | **not confirmed** (R model's P63 violates C3.4, not a named clause; replay parts 1 and 2 report nothing) |
| X3-3 | an impl side has an `UNEXPLAINED inputs` decision on a shared schedule | 0.65 | **not confirmed** (0 both); second part unscorable (R impl's grant path consults no clock) |
| X3-4 | a model side fails its support audit on a shared schedule | 0.5 | **confirmed** (A model, 13; failing floor terms = 2 on all; with terms at 1 all 13 have support, beside) |
| X3-5 | a hold-out produces a FAIL or divergence in some arm | 0.75 | **confirmed** (A: H11, H13, H14 divergences; R: H13) |
| X3-6 | planted defect caught on at most two of four sides | 0.6 | **not confirmed** (four of four) |
| X3-7 | steward finds the out-of-model failure from the trace in both arms | 0.4 | **confirmed**, with the departure (a helper added the hooks) |
| X3-8 | A impl total tokens below R's; A model below R's | 0.5; 0.4 | **not confirmed; not confirmed** (on output tokens alone the model half reverses, beside) |
| X3-9 | measure 7 finds a contradiction on some arm A side | 0.7 | **confirmed** (both raters, both sides) |

## What X3 shows, read beside the score
- **The structure the seed predicted is not what separated the arms.** The seed's standing prediction was that a new locus favours regeneration. Correctness split by side, not by arm: regeneration did better on the model's support and mutations and on the implementation's hold-outs; adaptation did better on the model's hold-outs and had no genuine stall. Every arm A loss on the implementation's hold-outs traces to one inherited rule (an exactly-two-clients admission check from an earlier format), which is the epoch-laundering-in-artifacts the seed names: a superseded requirement still enforced by an inherited element. Measure 4's residue (2, arm A impl) is the same kind of thing.
- **Arm A's model lost 13 schedules to a registered reach floor** (terms = 2 on any schedule with a partition) that its untimed failure detector need not reach; a choice its README states. Whether the floor or the model is wrong is not settled here.
- **The measures that need raters are weak.** Measure 6 has kappa 0.09 on model units; the ruling did not make the boundary between propagation and choice reliable.
- **No arm's own suite missed a planted defect**, but every planter chose a core safety clause unprompted, so measure 9 tested easy plants.
- **The steward's instruments were wrong twice in X3** (the provenance check's identity key, inherited; the reach generator's terms floor, a reading). Both were found by others (judges, an author's README), not by the steward.

## Departures and disclosures
- Measure 10's hooks were added by a helper, not the steward (logged before any chooser ran).
- Measures 6 and 7 rated by DeepSeek and Kimi, the steward rating nothing (logged before any rating).
- Plant 4 launched untracked, watched a minute later; three scoring-script corrections before the affected plants scored; the residue tool's wrapped-tag defect fixed before disposition.
- The adversarial review of this draft by a non-Claude family follows, and its findings are disposed of before the word DRAFT is removed.
