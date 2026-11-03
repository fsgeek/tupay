# D2 result (final, 2026-11-03, after review)

Scored by the eleventh steward (Claude Opus 5.5), 2026-11-03, by `scripts/steward/d2-score.py`. v1 was committed at `a41cc82` before its first run. v2 corrects it after Qwen's review (`experiments/D2/review/qwen/`, findings and dispositions). Outputs: `experiments/D2/score/score.json` (v1) and `score-v2.json` (v2, the score). The design and the log outrank this file. Draft 1 is in git history.

## What was tested
D2 asked whether enumerating the service contracts that Episode's log and recovery (`logbuf`, OSF DCE 1.2.2) rely on, and modelling them in TLA+, finds the seven defects a recent independent analysis found. That analysis was Episode's steward's, sealed before any list existed.
- **Phase 0:** two Codex and two Grok enumerators.
- **Phase 1:** 110 merged cells.
- **Phase 2:** four model authors, Claude and Grok, each in condition C (given the cells) and condition N (not given them), each scored on its own findings: Claude C 2, Claude N 3, Grok C 5, Grok N 0. Grok N's TLC ran (16 output files, commit "record TLC checks"). It pre-registered "0 schema findings, 1 honest-environment failure", and the design counts no finding unless its honest-environment check holds.
- **Phase 3:** three judges ruled blind on opaque ids. Episode and Gemini are registered; GLM is reported beside.

## Registered predictions
A prediction holds only if it holds under both Episode and Gemini. Denominator: all seven sealed bugs, since Episode's answer came after phase 0. The four environment-contract bugs (E2 to E5) are reported beside. **Gemini has no registered ruling on `cells-2`** (37 of 110 cells). A missing ruling is not a negative one, so under Gemini a cell prediction is decided only if every possible ruling on `cells-2` gives the same outcome. Otherwise it is undetermined.

| | p | Episode | Gemini | Result | GLM (beside) |
|---|---|---|---|---|---|
| **D2-1** cells name the contract of more commented bugs than uncommented (strictly, by fraction) | 0.6 | 3/4 vs 1/3: holds | 3/4 vs 1/3 on ruled packets: **undetermined** | **not established** | 2/4 vs 1/3: holds |
| **D2-2** some sealed bug is a match among some author's scored findings | 0.55 | E6 (F03) | E6 (F03), E2 (F06), E3 (F08) | **holds** | E6 (F03) |
| D2-2g, Grok's authors only (beside) | 0.4 | void | void | **void** | void |
| **D2-3** in each family, condition C reaches more sealed bugs than N | 0.5 | Claude 0 vs 1; Grok 1 vs 0 | Claude 1 vs 1; Grok 2 vs 0 | **does not hold** | Claude 0 vs 1; Grok 0 vs 0 |
| **D2-4** at least 4 of 7 bugs have their contract named by some cell | 0.55 | 4 (E2, E3, E4, E5) | 4 on ruled packets (the same); holds whatever `cells-2` says | **holds** | 3 (no E5) |
| **D2-5** Claude C reaches more sealed bugs than Grok C | 0.6 | 0 vs 1 | 1 vs 2 | **does not hold** | 0 vs 0 |
| P0-4 (phase 0) a Recognised line names a sealed bug | 0.5 | R04, R13 → E2 | the same | **holds** | the same |

Gemini's `cells-2` repair, reported beside, gives D2-1 a hold under Gemini. It is never the registered ruling.
**D2-5's confounds, as the design states them:** the sealed analysis was a Claude instance's, so Claude's findings may correlate with it by family; and Grok enumerated half of the cells its condition C author read, while Claude enumerated none.

**Leakage, as registered.** R04 (grok-2) and R13 (grok-1) are Recognised lines that all three judges match to E2. That makes them leakage flags, which void D2-2 for Grok's enumerations. The registration does not say which findings that removes. The score applies the widest reading, chosen after the outcome was seen: it removes every condition C author (their inputs include Grok's enumerations) and Grok's own authors. **D2-2 holds under that reading and under both narrower ones**, because F03 is from Claude's condition N author, who saw no enumeration. D2-2g is void. **Episode's view, beside:** both lines are "general write-cache knowledge, not leakage". E2 is the volatile write cache.

## Findings, per judge
| id | author | Episode | Gemini | GLM |
|---|---|---|---|---|
| F03 | Claude N | **match E6** | **match E6** | **match E6** |
| F07 | Claude N | partial E6 | partial E6 | no match |
| F08 | Grok C | partial E3 | match E3 | no match |
| F06 | Grok C | no match | match E2 | no match |
| F10 | Claude C | no match | partial E2 | no match |
| F01, F02, F04, F05, F09 | | no match | no match | no match |

Precision, given as matches and then matches-or-partials, over scored findings:

| Author | Episode | Gemini | GLM (beside) |
|---|---|---|---|
| Claude C | 0/2, 0/2 | 0/2, 1/2 | 0/2, 0/2 |
| Claude N | 1/3, 2/3 | 1/3, 2/3 | 1/3, 1/3 |
| Grok C | 0/5, 1/5 | 2/5, 2/5 | 0/5, 0/5 |

Grok N had no findings. No finding was flagged as contradicting a confirmed property.
Sealed bugs reached by any finding: **E6** (a match, under all three judges) and **E3** (partial or match, under both registered judges). E2 is reached under Gemini only. **No finding reached E1, E4, E5 or E7.**

**Where the registered judges disagree** (from `score-v2.json`, `disagreements`; the 37 `cells-2` cells where Gemini has no ruling are not repeated here):
- **Findings:** F06 (Episode no match; Gemini match E2), F08 (partial E3; match E3), F10 (no match; partial E2).
- **Cells:** C013 (none; E5), C018 (E4; E2 to E5), C032 (none; E2 to E5), C036 (none; E2, E3, E5), C078 (E2, E3, E5; E2 to E5), C107 (E2, E3; none), C108 (E4; E2 to E5).

The steward resolves none of them.

**Episode's sealed prediction.** It is scored by Episode, as registered. In its rulings reply Episode calls it "mostly wrong": it expected four of seven found by turning the textbook contract into findings, and instead the model authors reached E6 and E3 by modelling the defence in place. Its README lists the formal score as still to do.

## Reading beside the score (not a rule change)
1. **D2-1 is mostly a measure of the env/own split.** Three bugs (E1, E6, E7) are `logbuf`'s own defects, with "none violated" as their contract, and two of the three uncommented bugs are among them. On the four environment-contract bugs, Episode's and Gemini's rulings name 3 of 3 commented and 1 of 1 uncommented, which is not strictly higher. GLM's name 2 of 3 and 1 of 1. The outcome also depends on which cells each judge credited.
2. **Enumeration named the environment contracts; findings came mostly from modelling.** Under both registered judges, the cells name the contracts of all four environment-contract bugs. The condition C authors, who had those cells, reached E3 (Grok, under both judges) and E2 (Gemini only). The only finding all three judges call a match, F03 → E6, came from the Claude author with no cells, and it is a `logbuf` own-rule defect: in Episode's words, found by "modelling the defence in place".
3. **Possible defects beyond the sealed analysis.** Episode's reasons call several findings plausible and absent from its analysis:
   - F01 (Claude N): EarlierPassno aliasing in TranCommitted when a write stays outstanding for a full lap; "a plausible own-rule defect the sealed analysis missed; it deserves verification".
   - F02 (Grok C): an unknown checksum version forces success, `recover.c:2577`.
   - F09 (Grok C): a restart page that is not checksummed is accepted as a clean log.

   Its README lists second looks for F07 (which disputes the sealed note that the recovery path's +2 bump is safe), F06 (which may lie outside its model's "sealed once" page abstraction), and F01, F02, F04, F09, R20 and R47 ("claims of defects the analysis did not list"). None of these is verified. Tony notes that DCE's code cannot be checked against what runs today, because that code is IBM proprietary (log, "2026-11-02: the eleventh steward accepts"). The design's only scored route to "something the analysis missed" is a finding that contradicts a confirmed property, and none does. So these are reported, not scored. Episode's second looks are awaited at `episode/judging/D2/second-looks.md`.
4. **The judges differ in generosity.** Gemini credits the most and GLM the least; Gemini is the only judge to credit Grok C with two matches.

## Disclosures
- Claude C's two findings carry the heading word "draft" (passed through as `author_status`), and F10 names "F-draft-1", which links it to F05's author (Episode's packet defect 2). Condition is visible to a judge, because C findings cite cells.
- 32 of the 60 rows are captured shell output or headings, not claims (Episode's packet defect 1). Every judge ruled them "no", and they affect no prediction.
- `{SEALED_WHERE}` was unexpanded in all five packets.
- Gemini's `cells-2` failed to parse on both runs (log, 2026-10-29 06:26Z). A void run against sealed v1 exists, unread (`phase3/void-v1-run.sha256`).
- The scoring steward is Claude, as are Episode's judge, the sealed analysis and one author family. The registered judges are Episode and Gemini. GLM is beside, and the reviewer of this scoring is Qwen.
- Phases 0 and 1, scored earlier (log, 2026-10-26 22:43Z and 2026-10-27 04:09Z): P0-1 not confirmed; P0-2 not confirmed (a line-count ambiguity in the steward's brief); P0-3 confirmed for Codex, not for Grok.
- v1 of the scorer counted the missing `cells-2` ruling as negative and did not apply the leakage void. Qwen found both, and v2 corrects them; this changed D2-1's registered result from "holds" to "not established".

## What this does not claim
Seven bugs in one component of one 1992 file system is a small sample. A match shows the workflow can reach what a careful analysis reached; it is not a discovery. The candidate defects in reading 3 stay candidates until they are verified.
