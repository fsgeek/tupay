# X3 measures 6 and 7: ratings

Raters: DeepSeek (`deepseek/deepseek-v4-pro-0813`) and Kimi (`moonshotai/kimi-k3.1-pro`), independent, packets in `packets/` (hashes `packets/SHA256SUMS`), answers in `runs/<measure>-<side>/<rater>/`, tally `tally.txt` by `scripts/steward/x3-raters/tally.py`. The steward rated nothing (log 2026-11-01). Seven of eight calls parsed at first. **Kimi's m7-impl call stopped at its output limit with no answer** (`finish length`) and was rerun once, as the rule logged before sending allows, with reasoning capped at 24k tokens (`runs/m7-impl/kimi-2/`, parsed, 85 ratings); the failed run is kept. Cost of all nine calls: about US$2.36. derives: X3 prereg measures 6, 7, X3-9.

## Measure 6: propagation fraction (arm A), per rater
| side | DeepSeek | Kimi | agreement | Cohen's kappa |
|---|---|---|---|---|
| impl (27 units) | 15/27 = **0.56** | 21/27 = **0.78** | 21/27 | 0.53 |
| model (12 units) | 1/12 = **0.08** | 8/12 = **0.67** | 5/12 | **0.09** |

The raters disagree on the model side almost entirely: kappa near zero, 7 of 12 units split. Under the measure 6 ruling, DeepSeek read nearly every model unit as making a choice the inputs leave open; Kimi read two thirds as implementing a prescription. X2's raters split on the same boundary before the ruling existed. **The ruling did not make measure 6 reliable on model units**, and that is reported as a result about the measure. The steward does not adjudicate.

## Measure 7: interpretations contradicted (arm A), per rater
| side | DeepSeek | Kimi | agreement (3 verdicts) | kappa |
|---|---|---|---|---|
| model (of 46) | **6**: 3, 5, 12, 17, 20, X2.2 | **5**: 3, 5, 12, 20, X2.2 | 42/46 | 0.85 |
| impl (of 85) | **15**: 3, 4, 7, 13, 18, 23, 26, 42, 50, 51, 70, 77, 80, 83, 85 | **9**: 3, 7, 13, 20, 23, 26, 50, 80, 83 | 63/85 | 0.55 |
| impl (of 77, beside) | 14 | 9 | | |

Own column, as the registration requires: entries contradicted that the old README had already marked superseded: DeepSeek 0 on both sides; Kimi 1 on impl (81), 0 on model. Both raters name **3, 5, 12, 20, X2.2** on the model and **3, 7, 13, 23, 26, 50, 80, 83** on impl.

## X3-9
"On at least one arm A side, measure 7 finds at least one contradicted interpretation" (p 0.7): **confirmed under both raters, on both sides.**

**Correction (appended):** the cost figure above was written before it was computed. Summed from the nine `response.json` usage records it is **US$2.34**.
