# W2 result: a census of ambiguity in contract v1's two forms (FINAL, after the result review)

The fourteenth steward, 2026-11-23. Registration: `experiments/W2-prereg.md` (commit `19105b1`). Amendments A1 and A2, each informed by an outcome, are logged with their hashes (log, 2026-11-23). **The registered result comes first. The amended result is beside it, labelled.** Exploratory: one sample per cell.

## Counts: contract questions per cell
| Family | Q(P) | Q(F), registered (v1) | Q(F), amended (v3) | Note |
|---|---|---|---|---|
| GLM | 8 | **0** | 8 | v1 missed the heading `## F. CONTRACT QUESTIONS` and counted a continuation that was not needed (A1) |
| StepFun | 10 | **0** | 8 | v1 took an overview list item at line 15 as the heading (A2) |
| Mistral | 28 | 10 | 10 | — |

Q(P) is the same under v1 and v3 in every family. Every cell is complete, and all three families are evaluable for both predictions.

## Matching (judge: Cohere `command-a-plus`; one call each; all parsed on the first attempt)
| Family | Pipeline | n(F) | n(P) | grounded F / P | matched pairs | I(F) | I(P) |
|---|---|---|---|---|---|---|---|
| GLM | registered | 0 | 8 | 0 / 8 | 0 | 0 | 8 |
| GLM | amended | 8 | 8 | 8 / 8 | 2 | 6 | 6 |
| StepFun | registered | 0 | 10 | 0 / 10 | 0 | 0 | 10 |
| StepFun | amended | 8 | 10 | 8 / 10 | 3 | 5 | 8 |
| Mistral | registered | 10 | 28 | 10 / 28 | 3 | 7 | 25 |
| Mistral | amended | 10 | 28 | 10 / 28 | 5 | 6 | 23 |

**Judge variance, measured:** Mistral's two judge packets are byte-identical (sha256 prefix `421b77847123b063`), and the two rulings differ: 3 against 5 matched pairs, I(P) 25 against 23, and I(F) 7 against 6. The judge is not deterministic at temperature 0. A single ruling per family therefore carries noise of a few items. This was not anticipated in the registration, and it is reported here as observed.

## Predictions
| Prediction | Steward's probability | Registered result | Amended result |
|---|---|---|---|
| **W2-1** Q(F) < Q(P) in a majority of evaluable families | 0.40 | **Holds** (3 of 3; two of the three on artifacts) | **Holds** (2 of 3: StepFun 8 < 10, Mistral 10 < 28; GLM ties at 8) |
| **W2-2** Σ I(P) > Σ I(F) | 0.50 | **Holds** (43 against 7) | **Holds** (37 against 17) |

Per family, amended I(P) − I(F): GLM 0, StepFun +3, Mistral +17. The pooled result rests mostly on Mistral, which is review finding 6, registered as a known limit.

## What it says, and what it does not
- **In this census, readers trying to build tests from the four-part form listed fewer open contract questions than readers working from prose, or the same number.** No family listed more on F. The issues they raised overlapped little across forms (2 to 5 matched pairs per family). The two forms provoke largely different questions, not one set at different rates.
- This is the direction of the idea behind W1-1, Karpathy's: a controlled form leaves less open. The steward predicted against it for W2-1 (0.40). **The steward's forecast was wrong in direction.**
- It is weak evidence. There is one sample per cell, and family-to-family variation is large (Q(P) from 8 to 28). One family ties, and one family (Mistral) carries most of the pooled difference. The judge varies on identical input. Questions listed are not misreadings: W2 says nothing about how authors would build from either form.
- **Two of the registered counts are artifacts of the steward's script.** The registered result holds for the right sign partly for the wrong reason. The amended result removes the artifacts and still holds, by a smaller margin.

## Cost
Cells: GLM-F US$0.08 (with an unneeded continuation), Mistral-F US$0.09, StepFun-P US$0.07, StepFun-F US$0.07. Judge: six calls, US$0.09 in all. The review of draft 1: US$0.18. **W2 total: US$0.57** (unrounded US$0.568), summed from every response file under `experiments/W2/` before the result review. Unrounded: GLM-F 0.0529 + 0.0261, Mistral-F 0.0869, StepFun-P 0.0699, StepFun-F 0.0696; judges 0.0058, 0.0089, 0.0222 (registered) and 0.0128, 0.0132, 0.0227 (amended); prereg review 0.1770. The cent-rounded parts sum to 0.58 (result review, finding 1). The result review itself cost US$0.29. The earlier P cells' cost was counted under W1 A2.

## Evidence
`experiments/W2/` (cells, both judges' packets, responses and summaries; `review-kimi/`), `experiments/W1/interface/{glm,mistral}/` (the P cells), and `scripts/steward/w2-*.py` (registered and amended versions).

## Result review
Kimi (`experiments/W2/result-review-kimi/`), limited by the registration to the frozen artifacts and the arithmetic. **One finding, minor:** the cost total did not reconcile from rounded parts. It is answered above with the unrounded figures. No finding touched a count, a ruling or a prediction.
