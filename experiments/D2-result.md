# D2 result (draft 1, before review)

Scored by the eleventh steward (Claude Opus 5.5), 2026-11-03, by `scripts/steward/d2-score.py` (committed at `a41cc82` before its first run; rules in its header, each taken from `experiments/D2/design.md` or the log). Output: `experiments/D2/score/score.json`. The design and the log outrank this file.

## What was tested
D2 asked whether enumerating the service contracts that Episode's log and recovery (`logbuf`, OSF DCE 1.2.2) rely on, and modelling them in TLA+, finds the seven defects a recent independent analysis found. That analysis was Episode's steward's, sealed before any list existed. Phase 0: two Codex and two Grok enumerators. Phase 1: 110 merged cells. Phase 2: four model authors, Claude and Grok, each in condition C (given the cells) and condition N (not given them), each scored on its own findings: Claude C 2, Claude N 3, Grok C 5, Grok N 0. Phase 3: three judges ruled blind on opaque ids. Episode and Gemini are registered; GLM is reported beside.

## Registered predictions
A prediction holds only if it holds under both Episode and Gemini. Denominator: all seven sealed bugs, since Episode's answer came after phase 0. The four environment-contract bugs (E2 to E5) are reported beside. Gemini has no registered ruling on `cells-2`, so its cell outcomes rest on `cells-1` and `cells-3`. The mechanical repair of `cells-2`, reported beside, changes no outcome.

| | p | Episode | Gemini | Result | GLM (beside) |
|---|---|---|---|---|---|
| **D2-1** cells name the contract of more commented bugs than uncommented (strictly, by fraction) | 0.6 | 3/4 vs 1/3 | 3/4 vs 1/3 | **holds** | 2/4 vs 1/3 |
| **D2-2** some sealed bug is a match among some author's scored findings | 0.55 | E6 (F03) | E6 (F03) | **holds** | E6 (F03) |
| D2-2g, Grok's authors only (beside) | 0.4 | none | E2, E3 | not | none |
| **D2-3** in each family, condition C reaches more sealed bugs than N | 0.5 | Claude 0 vs 1; Grok 1 vs 0 | Claude 1 vs 1; Grok 2 vs 0 | **does not hold** | Claude 0 vs 1; Grok 0 vs 0 |
| **D2-4** at least 4 of 7 bugs have their contract named by some cell | 0.55 | 4 (E2, E3, E4, E5) | 4 (the same) | **holds** | 3 (no E5) |
| **D2-5** Claude C reaches more sealed bugs than Grok C | 0.6 | 0 vs 1 | 1 vs 2 | **does not hold** | 0 vs 0 |
| P0-4 (phase 0) a Recognised line names a sealed bug | 0.5 | R04, R13 → E2 | the same | **holds** | the same |

**Leakage flag, as registered:** R04 (grok-2) and R13 (grok-1) are Recognised lines that all three judges match to E2. Under the registered rule that makes them leakage flags, and they void D2-2 for Grok's enumerations. D2-2 itself rests on F03, from Claude's condition N author, who was given no enumeration, so the void does not reach it. D2-2g is void under the rule and does not hold in any case. **Episode's view, beside:** both lines are "general write-cache knowledge, not leakage". E2 is the volatile write cache, which is textbook.

## Findings, per judge
| id | author | Episode | Gemini | GLM |
|---|---|---|---|---|
| F03 | Claude N | **match E6** | **match E6** | **match E6** |
| F07 | Claude N | partial E6 | partial E6 | no match |
| F08 | Grok C | partial E3 | match E3 | no match |
| F06 | Grok C | no match | match E2 | no match |
| F10 | Claude C | no match | partial E2 | no match |
| F01, F02, F04, F05, F09 | | no match | no match | no match |

Precision (matches, then matches or partials, over scored findings), Episode / Gemini: Claude C 0/2, 0/2 / 0/2, 1/2. Claude N 1/3, 2/3 / 1/3, 2/3. Grok C 0/5, 1/5 / 2/5, 2/5. Grok N had no findings. No finding was flagged as contradicting a confirmed property.
Sealed bugs reached by any finding, under both registered judges: **E6** (match) and **E3** (partial or match). E2 is reached under Gemini only. **No finding reached E1, E4, E5 or E7.**

## Reading beside the score (not a rule change)
1. **D2-1 holds by the denominator's construction, not by the comments.** Three bugs (E1, E6, E7) are `logbuf`'s own defects with "none violated" as their contract, so no cell can name them. Two of the three uncommented bugs are among them. On the four environment-contract bugs reported beside, the cells name 3 of 3 commented and 1 of 1 uncommented: not strictly higher, so it does not hold. The registered result stands. What it measures is mostly the env/own split.
2. **Enumeration named every environment contract, and modelling with those contracts found little.** Under both registered judges the cells name the contracts of all four environment-contract bugs (E2 to E5). The condition C authors, who had those cells, reached E3 (Grok, under both judges) and E2 (Gemini only). The only finding all three judges call a match is F03 → E6, from the Claude author who had no cells, and it is a `logbuf` own-rule defect. So naming the contract was enough to *name* where the env bugs lie, but not to *find* them through the model. The finding came from modelling the defence in place (Episode's words in its rulings reply).
3. **Possible defects beyond the sealed analysis.** Episode's reasons say four findings are not in its analysis and are plausible from the cited source: F01 (Claude N: EarlierPassno aliasing in TranCommitted when a write stays outstanding for a full lap; "a plausible own-rule defect the sealed analysis missed; it deserves verification"), F02 (Grok C: an unknown checksum version forces success, `recover.c:2577`), F09 (Grok C: a restart page that is not checksummed, accepted as a clean log), and F07, which "disagrees with the sealed E6 note that the +2 bump covers" the recovery path. None is verified, and DCE's code cannot be checked against what runs today (Tony). Episode's second looks, F07 first, are awaited at `episode/judging/D2/second-looks.md`. They are reported, not scored: the design's only scored route to "something the analysis missed" is a finding that contradicts a confirmed property, and none did.
4. **Judges disagree most on Grok C.** Gemini credits it with two matches (F06 → E2, F08 → E3); Episode gives one partial and GLM none. Gemini is the most generous judge throughout, and GLM the strictest.

## Disclosures
- Claude C's two findings carry the heading word "draft" (passed through as `author_status`), and F10 names "F-draft-1", which links it to F05's author (Episode's packet defect 2). Condition is visible to a judge, because C findings cite cells.
- 32 of the 60 rows are captured shell output or headings, not claims (Episode's packet defect 1). They were ruled "no" with that reason by every judge, and they affect no prediction.
- `{SEALED_WHERE}` was unexpanded in all five packets.
- Gemini's `cells-2` failed to parse on both runs and has no registered ruling. The repaired file is beside (log, 2026-10-29). A void run against sealed v1 exists, unread (`phase3/void-v1-run.sha256`).
- The scoring steward is Claude, as are Episode's judge, the sealed analysis and one author family. The registered "holds under both" rule pairs Episode with Gemini for that reason.
- Phase 0 to 1, scored earlier: P0-1 not confirmed; P0-2 not confirmed (a line-count ambiguity in the steward's brief); P0-3 confirmed for Codex, not for Grok.

## What this does not claim
Seven bugs in one component of one 1992 file system is a small sample. A match shows the workflow can reach what a careful analysis reached; it is not a discovery. The candidate defects in reading 3 are candidates until verified.
