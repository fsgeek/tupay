# Formal score of episode's sealed D2 prediction

Prediction: `sealed/2026-10-26-tupay-D2-prediction.md`, commit `7eeb027`,
sha256 `2a578fa40a729b3b2b95ca76694044053ce1961eed211b5544fae1c4fcde4ad4`,
written before any D2 output existed. Scored by its author (episode's steward,
Claude Opus 5.5), 2026-11-03.

"Found" is scored two ways: by **match** only, and by **match or partial**. The
basis is my rulings (`judging/D2/findings.json`, `4fd2c09`), where match =
{E6} and partial = {E6 (F07), E3 (F08)}. Under all three judges, D2-2 holds on
F03 → E6 (`tupay/experiments/D2-result.md`).

## The four claims

| # | claim | outcome (match only) | outcome (match or partial) | score |
|---|---|---|---|---|
| 1 | finds 4 of 7, range 3–5 | 1 | 2 | **miss** (below range both ways) |
| 2 | finds E2, E3, E5, E4; misses E1, E6, E7 | {E6} | {E3, E6} | see per-bug table |
| 3 | of E1, E4, E7 (no trace in the source), finds 1 (E4) | 0 | 0 | **miss** |
| 4 | the most likely false positive is a claim that P1 or P2 fails | no finding flagged | — | **miss** |

**Claims held: 0 of 4.**

## Per-bug calls (claim 2)

| bug | predicted | found (match) | found (m/p) | right (match) | right (m/p) |
|---|---|---|---|---|---|
| E1 | missed | no | no | yes | yes |
| E2 | found | no | no | no | no |
| E3 | found | no | partial | no | yes |
| E4 | found | no | no | no | no |
| E5 | found | no | no | no | no |
| E6 | missed | **yes** | yes | no | no |
| E7 | missed | no | no | yes | yes |

**Correct: 2 of 7 (match only), 3 of 7 (match or partial).**

**Baseline:** predicting "finds none" would have scored 6 of 7 under match only
and 5 of 7 under match or partial. The prediction did worse than the trivial
baseline both ways.

## Why

The reasoning in the prediction bet that a contract-first workflow would turn
the textbook contract (completion implies durability) into findings, and would
miss defects visible only by modelling the code as written. The cells did name
the textbook contract: 10 of 110 name a sealed bug's contract, including C078.
But no finding reached E2, E4 or E5. The model authors did model the code as
written, and that is where they found E6 and the defects in
`second-looks.md`. The direction of my error: I underestimated how far "model
the defence in place" pushes an author into the source, and overestimated how
far a named contract carries an author to its consequence.
