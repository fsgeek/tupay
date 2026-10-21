# X2 pre-registration: adversarial review and the steward's response

The review below is by a Claude Fable 5.1 instance acting as advisor to the steward (134k tokens, about 9 minutes, charged to the steward). It read the draft pre-registration, the inputs, the briefs and the hold-out author's notes; not the artifacts and not the hold-out files. Its full text describes two of the hold-outs, so it is withheld with the hold-out files and committed, unedited, when they are (pre-registration, "Hold-out secrecy"). Its findings are summarised by number in the table below.

## Steward's response
| Finding | Disposition |
|---|---|
| 1. Liveness dependency; brief asymmetry; fairness; bound | **Accepted in full.** Dependency groups and "one mechanism, scored once"; unreached and unassessable categories; the fairness legitimacy rule in the pre-registration and both model briefs; format Rule E3 (bound); identical candour sentence in all four briefs, and "must report FAIL" softened in the regen briefs. P19/P20 not decoupled: the grouping makes their dependence harmless to the score, and decoupling would turn them into P2's shape. This was the most consequential steward error in X2's preparation. |
| 2. Two hold-outs telegraphed by the input fixes | **Accepted.** Attenuation stated; pre- and post-fix probabilities both registered, post-fix scored; one more hold-out (H10) from the fixed inputs, aimed at something they do not state. |
| 3. Measures 6 and 7 not two-rater operational | **Accepted.** Units, exclusions, the operational tests the reviewer proposed, commit messages stripped, two raters on both, kappa reported, disagreements resolved by the diff, denominators counted (model 37, impl 66), X2-7 scored on the lower rater against X1's baseline, which is rated before any X2 commit. |
| 4. Departure 1 and cost | **Accepted.** Before/after split at the first adapting commit; X2-1 scored on total tokens and wall-clock, both, per side; mixed scores X2-1 not confirmed; X2-6 control added (null if a zero-contradiction side also rises). |
| 5. "A finding either way" | **Accepted.** X2-11 registered, with what follows for the seed if it holds or fails. |
| 6. Hold-out secrecy | **Accepted.** Hashes committed now; files and notes after the arms' first versions. The draft also described the hold-outs in words; those descriptions were removed. |
| 7.1 P(X2-8) < P(X2-10) | **Accepted.** X2-8 raised to 0.7; X2-10's two opposing effects both stated. |
| 7.2 Unit of "fails" | **Accepted.** An impl side fails a schedule if any seed fails; comparisons count schedules. |
| 7.3, 7.4 Input check | **Accepted.** Check (iii) added (exact schedule set; no hold-out hash present). "Reference" defined as a path the brief tells the author to read; prose mentions of earlier versions in committed inputs accepted and stated. My own new text no longer names `docs/seed.md` or the hold-out author, and brief titles no longer name the arm. |
| 7.5 P23/P29 comments; P24 serial client; P22/P28 weak bite | P23/P29 and P22/P28 recorded as residues. P24: format v4 restates T3 (a write or read does not wait on an earlier unanswered one; a serialising client must not wait for ever on a lost reply). |
| 7.6 Measure 4 by reading | **Accepted.** A fixed grep-and-compare procedure, with reading reported separately. |
| 7.7 Library rationale | **Accepted.** Marked in X2-3 as rationale, not explanation. |
| 7.8 Date | UTC, as the OTS stamp will show. |
| 8. One family in three roles | Stated once in the pre-registration, Departure 3. |

