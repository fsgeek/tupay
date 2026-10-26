# D2: dependency contracts of Episode's log and recovery, against a sealed answer (design, draft 1)

Steward's design (the eighth steward, Claude Opus 5.5), 2026-10-26, before any enumeration exists. Adapted from D1's design draft 3 (`experiments/D1/design.md`), whose rules are kept unless a departure is stated here with its reason. Proposed by Tony Mason, 2026-10-26 (log, "two notes from Tony"); the sealed answer is Episode's (log, "the eighth steward accepts").

## Question
Pointed at the service contracts a component relies on from the layers around it, does the workflow (dependency contracts enumerated by two non-Claude families; a formal model with an environment action per contract; observation of contracts not honoured) find the defects a recent independent analysis found in Episode's log and recovery, which no public record holds?

## Why this is blind, and how far
- **The answer is sealed and outside tupay.** `episode` commit `7eeb027`: `sealed/2026-10-26-tupay-D2-findings.md` (sha256 `227d2508…6b7b9698`; 7 bugs, all found only by the analysis, none visible in DCE 1.2.2's history; in 4 the enabling assumption is stated in a source comment, in 3 nothing in the source points at it; 6 confirmed properties; 1 open item) and Episode's own prediction (`2a578fa4…fcde4ad4`). Hashes recorded in tupay's log (commit `b23c483`, OTS-stamped) and checked by the steward without reading the files. The analysis was done in the past month, after every current model's training cutoff.
- **The code is public and may be in training**; an enumerator may recognise its structure, which is allowed. What none can have seen is the analysis.
- **The steward's residue for D2:** the seventh steward's proposed contract list (five headings, quoted in Episode's answer; log, "the eighth steward accepts"). The steward has not read the paper beyond its title block, `logbuf`, the sealed files, `episode/spec/`, khipumaq's Episode sessions, or Tony on Episode, and does not until phase 3. **Guard:** the enumeration brief is D1's brief v2 with substitutions only; the diff is committed beside it (`brief-enumerate.diff-from-D1.txt`), so every word the steward added can be read. It names no category of dependency; D1's parenthetical list (a disk, a network, a clock, ...) is replaced by "anything outside `logbuf` that it calls, that calls it, or that it runs on, including an operator".

## Sources (the enumerators' and modellers' only inputs)
- **Paper:** *The Episode File System*, USENIX Winter 1992, from its public copy (https://fsgeek.ca/media/2017/11/1992-The-Episode-File-System.pdf), sha256 `5bd8e654…fb84bed`, byte-identical to Tony's local copy; text by `pdftotext -layout`.
- **Source:** `file/episode/` of OSF DCE 1.2.2, taken from an independent public mirror (github.com/nealelliott/dce_1.2.2, commit `745a220`, 2020-04-24, "the inital osf dce code from the osf website"); its 415 files are byte-identical to Tony's tree (`~/projects/dce/dce/src/file/episode`, `diff -r` empty). Whole tree given; `logbuf` named as the component, as Episode recommends (a hand-picked list would point at what the analysis touched).
- **Neither is committed to tupay** (the repository is public; DCE's licence limits redistribution; the paper's copyright is USENIX's and the authors'). Each checkout's manifest (path and sha256 of every file) is committed instead.
- Nothing from `episode/`, by default and by Episode's advice.

## Phase 0: enumeration (as D1, with the source change)
Two families (Codex, Grok), two independent runs each, each a fresh instance in `scripts/steward/author-sandbox.sh` (no web), in a separate history-free repository holding exactly `AGENTS.md`, `BRIEF.md` (= `brief-enumerate.md`) and `source/`; manifest committed and `sandbox-check.sh` (and its mutation pair) run before launch; Grok with `--always-approve`. Output `enumeration.md` collected unchanged with transcript and egress log. **Quotation check:** D1's checker extended to `<path>:<line>` quotations, matched in that file within 20 lines of the cited line after the same normalisation; its test cases written before it runs.
**Predictions:** P0-1 each list 15 to 60 contracts (p 0.75); P0-2 at least 90% of each list's quotations verify (p 0.6; lower than D1's, since source quotations carry more layout); P0-3 as D1's (top three of one family's two runs agree in at most one, p 0.6); P0-4 at least one Recognised section names a reported bug (p 0.5; Episode is far less discussed than Raft). Abort criteria as D1.

## Phase 1: merge and order (D1's rule, unchanged)
Recognised sections removed first and kept for phase 3; two Gemini merges in deny-all workspaces (`scripts/steward/d1-merge.sh`), only agreed groups accepted; D1's total order (silent percentile rank, then detectability, then earliest source, then the NIST beacon pulse after the merge commit). **Departure:** "earliest source" maps a paper section to its numeric tuple and a source citation to (99, path order, line), so the paper's statements sort before the code's; fixed now, before any list.

## Phase 2: the model, two conditions, two families (departure from D1's k = 3 against a library)
Episode's log and recovery is not a library tupay can drive; the workflow's formal side is applied to it directly.
- **Condition C (contracts).** A model author gets the paper, the source and every phase 1 cell's contract, source, violation, at-risk, detectable and silent fields, in the registered order. It writes a TLA+ model of the log and recovery as the sources describe them, adds an environment action per cell it can express (the contract violated), checks the guarantees, and reports each violation as a finding: the cell, the mechanism, the effect, the counterexample. Cells are taken in order; cells not modelled are listed with the reason.
- **Condition N (no contracts).** The same sources, no cells: model the log and recovery and find what breaks it. This tests whether naming the dependency contracts is what finds the defects, against modelling alone (Tony's counsel: when a choice is either/or, run both).
- **Families:** Claude Opus 5.5 (on the box) and Grok (sandbox; calibrated for TLA+ 2026-10-21), each in both conditions: four model authors, fresh instances, no web. The sealed analysis was a Claude instance's, so Claude's findings may correlate with it by family; Grok's are the cleaner test, and both are reported.
- **Budget and abandon rule:** each author capped at 24 GB and six hours' wall clock; findings committed before the cap counts.
- **Implementation side (pilot, optional):** whether `logbuf` builds in user space with a fault-injecting device beneath it, so a model counterexample can be replayed against the 1992 code, is tried by a Codex author with a three-hour budget after phase 2's models are committed; it does not gate phase 3.
- Briefs, budget and the model-side support audit are in the phase 2 prereg, committed before any model author starts.

## Phase 3: unseal and judge
Every phase 2 finding is frozen (committed and stamped) before anything is sent to Episode. Episode's steward rules first, by its criteria fixed 2026-10-26 (match: same violated contract, mechanism and class of effect; partial: the contract and one of the other two; no match otherwise; a claim against a confirmed property is flagged; the open item is "unresolved"; several findings on one sealed bug count once), and commits its rulings with reasons; then a fresh Gemini instance rules independently from the same packet; disagreements are reported, not resolved by the steward. The judges also map each phase 1 cell to the sealed bug, if any, whose violated contract it names (for D2-1 and D2-4).

## Predictions for phase 3 (steward's probabilities, before any list exists)
- **D2-1 (Tony's comments).** Of the sealed bugs, the fraction whose violated contract is named by at least one phase 1 cell is higher for the four whose assumption a source comment states than for the three with nothing in the source. p = 0.6.
- **D2-2.** At least one sealed bug is a "match" in at least one of the four model authors' findings. p = 0.55.
- **D2-3.** Condition C matches (match or partial) more sealed bugs than condition N, in each family separately. p = 0.5.
- **D2-4.** At least four of the seven sealed bugs' violated contracts are named by some phase 1 cell. p = 0.55.
- **D2-5.** Grok's condition C finds fewer matches than Claude's condition C. p = 0.6.

## What this does not claim
Seven bugs in one component of one 1992 file system is a small sample. A match shows the method can find what a careful analysis found; it is not a discovery (the analysis came first), and it is calibration for D1, whose question is open-ended. Families: the enumerators and one model family are not Claude; the analysis and the other model family are.
