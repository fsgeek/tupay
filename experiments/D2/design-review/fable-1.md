I have read everything the brief allows: the D2 design and brief with its diff, D1's design, brief and earlier review, AGENTS.md, Episode's reply, and the steward scripts the design names (`author-sandbox.sh`, `sandbox-check.sh`, `d1-merge.sh`, `d1-agy-workspace.sh`, `d1-quote-check.py`, `d1-phase1.py`, the egress allowlists, and the box launcher and check, since the design puts the Claude author "on the box"). I did not open the DCE tree, the paper, anything under `episode/` other than the reply, or any log, memory or handoff. Nothing was written or run with side effects.

One note on my own residue: Episode's reply, which I was told to read, quotes the seventh steward's five headings and describes the open item's nature in two words. I will not repeat either, and nothing below is shaped by them beyond the structural point in finding 6.

# Adversarial review of D2 (design draft 1 + brief-enumerate v1)

## Blocking

**1. The guarantees are not fixed before phase 0; every author invents their own, so "at-risk", the conditions and the judges' "effect" have no common referent.**
Text: brief §Task, "The text and the source state what the log and recovery guarantee ... Find those guarantees." Diff: D1 quoted Figure 3.2 verbatim; D2 replaces it with an instruction to find them. D1 draft 3 also committed `contract.md` before phase 0 (D1 §Phase 2 "Inputs"); D2 has no equivalent.
Failure: four enumerators produce four guarantee sets; `at-risk` fields point at different things; merges in phase 1 are harder to accept (Gemini will see "the same obligation" tied to different guarantees); the C and N authors each model whichever guarantees they chose, so "class of effect" in the match rubric is matched against four private vocabularies. A judge can then call almost anything partial. The design avoided naming guarantees because the steward has not read the paper, which is the right instinct, but the cost is that the one input the whole scoring hangs on is unregistered.
Fix: a phase 0a before phase 0: two fresh non-Claude instances, in the enumerator sandbox, each extract the guarantees from the paper and the source alone, in a fixed format (one sentence, source citation); only guarantees both produce are kept, committed as `contract.md`, and the brief quotes it verbatim with D1's catch-all ("and any other guarantee the text or source makes"). The steward does not edit the list.
Leak from the fix: none; the extractors see only the sources. The steward will read `contract.md`, which is paper content; record that in the residue.

**2. In condition C a "finding" is produced by construction, so D2-2 and D2-3 collapse into D2-4.**
Text: design §Phase 2 C, "adds an environment action per cell it can express (the contract violated), checks the guarantees, and reports each violation as a finding".
Failure: violate an assumed obligation and the guarantee that rests on it fails; that is what "assumption" means. Every modelled cell yields a counterexample and therefore a finding, and the finding's "contract" is the cell's contract by definition. "Match" then reduces to "was a sealed bug's contract among the cells modelled before the clock ran out", which is D2-4 restated with a time limit, and "mechanism" is whatever the author wrote when describing a tautology. Nothing in the design distinguishes a trivial counterexample from a defect the sources claim to tolerate and do not. There is also no mutation pair of any kind (AGENTS.md 5): a model whose stated guarantee is simply wrong, failing even in an honest environment, is scored as findings.
Fix: define a finding for C now: the sources describe (or the code implements) a defence against the violated contract, the model includes that defence, and the guarantee still fails; a cell with no described defence is reported as "unguarded" (listed, not a finding). Per cell, two checks are required and committed: the environment honours the contract and the guarantee holds; the defence is removed and the guarantee fails. Each author ranks its findings; the prereg fixes the scored cut (say the first ten per author) and reports the full list as secondary. Report precision (matches per finding) beside recall.
Leak from the fix: none; the brief would not state the cut size, so authors learn nothing about the answer's size.

**3. The phase 2 briefs are written after the cells exist, by the steward, who holds the residue and will have read four enumerations.**
Text: design §Phase 2, "Briefs, budget and the model-side support audit are in the phase 2 prereg, committed before any model author starts." The prereg follows phases 0 and 1.
Failure: this is D1's finding 1 in a new place. The N brief is one sentence today; its final wording is written by someone who has just read 60 to 240 contract statements. Any phrase that drifts in ("consider what the surrounding layers may do") makes N a weaker copy of C, and any phrase that echoes the steward's five headings is residue entering the treatment. An outsider cannot tell drift from design.
Fix: commit both phase 2 briefs now, complete, with only run paths, dates and the cell file name to be filled; the prereg may restate, not change. Any later wording change is an additive amendment that says it was made after reading the lists.
Leak from the fix: none.

**4. Judging is under-registered where it matters: two judges with no rule for which ruling scores the predictions, judges who see family and condition, and a cell-to-bug mapping with no rubric.**
Text: design §Phase 3, "Episode's steward rules first ... then a fresh Gemini instance rules independently ... disagreements are reported, not resolved by the steward"; "The judges also map each phase 1 cell to the sealed bug, if any, whose violated contract it names."
Failure: (a) D2-1 to D2-5 are scored on rulings, and with two sets of rulings the steward picks after seeing both, or reports whichever reads better. (b) The first judge wrote the sealed file and Episode's sealed prediction, and is a Claude instance ruling on Claude's findings against Grok's; the second judge's "independent" ruling is only independent if it does not see the first judge's reasons, which the design does not say. (c) "Names the violated contract" has no definition for cells, and the match rubric's three fields have no stated home in the sealed file (the reply does not say the file holds a per-bug contract, mechanism and effect in fixed form); if the judge composes those from the sealed prose after seeing the findings, the rubric is chosen after outcomes. (d) A finding that matches several bugs, and the D2-1 tie case (0/4 vs 0/3), are undefined.
Fix: pre-register now: each prediction is scored under each judge's rulings and reported both ways, and "holds" only if it holds under both; the packet sent to both judges carries findings and cells under opaque ids, shuffled by the beacon, with the id-to-author mapping sealed in tupay until both rulings are committed; Gemini rules in the deny-all workspace without the first ruling; cell-to-bug mapping is binary against the sealed file's per-bug "enabling assumption" field; ask the holder (count only) to confirm that every sealed bug carries contract, mechanism and effect as three fields already written; a finding matching several bugs counts for each; D2-1 requires strictly higher.
Leak from the fix: the holder's confirmation is a count; none otherwise.

**5. Whether the seven sealed bugs are dependency-contract violations at all is unestablished, and the brief routes `logbuf`'s own defects out of the cells.**
Text: reply §1, "7 bugs in Episode's log and recovery"; brief §Task, "if you find a defect in `logbuf`'s own rules, note it in your report, not in the list"; design D2-1 and D2-4 use 7 (4 + 3) as the denominator.
Failure: the holder counted bugs, not contract violations. If some of the seven are internal logic defects, no cell can name them, C cannot be pointed at them, N can find them by reading, and D2-1, D2-3 and D2-4 are scored against the wrong denominator. The enumerators' report notes (internal defects they saw) are collected but never scored, although an enumerator noticing a sealed bug while reading would mean the enumeration, not the model, found it.
Fix: before phase 0, ask the holder for one more count: how many of the seven are violations of an obligation on something outside `logbuf` (by the brief's definition, which the holder can read). Fix D2-1 and D2-4's denominators to that count. Freeze the enumerators' report notes with the lists and have the judges score them against the sealed list as a separate row, "found by reading", not as workflow evidence.
Leak from the fix: a count reaches the steward; record it as residue. A count cannot steer the brief, which is already written.

## Should-fix

**6. The recorded residue is smaller than the residue.**
Text: design §Why blind, "The steward's residue for D2: the seventh steward's proposed contract list (five headings ...)."
Failure: the reply the steward read also carries the 4/3 split and its wording ("assumption or the hazard"), a two-word description of the open item's subject, the fact that the analysis compared against a Linux journal, that the analysis touched files outside `logbuf`, and a pointer to session `38a33a70` ("how he fire-tested Episode's recovery"), on which the design is silent. D2-1 is built on the 4/3 split, so the residue is already in the predictions. An outsider who later reads the reply will find the design's residue statement incomplete.
Fix: list every item of the reply that is more than a hash in the residue paragraph; state whether `38a33a70`'s answer was read and, if so, its one-line content. Also note that this review's author read the same reply.
Leak from the fix: none.

**7. Steward-blindness is by discipline only, and the design claims more than that.**
Text: design §Why blind, "checked by the steward without reading the files"; reply §3, where the findings also live (a public GitHub branch; sessions reachable by the steward's own search tool with `scope: "all"`).
Failure: the sealed plaintext sits on the same filesystem under the same uid as the steward's process, which runs with bypass permissions; the analysis sessions are one tool call away. OTS proves the hash existed, not that nobody read the file. D1's draft 3 learned to say "steward-blind and search-free, not blind"; D2 says "blind, and how far" and then describes the holder's seal, not the steward's.
Fix: move the plaintext off the shared path (ciphertext committed in Episode, key held by Tony offline until phase 3; or plaintext under a uid the steward's session cannot read); say in the design that the steward's not-reading is attested by the log and by nothing else; record the public branch's push date against each model's published cutoff instead of asserting "after every current model's training cutoff".
Leak from the fix: none.

**8. The `silent` anchor is D1's and does not fit a system with no production deployments.**
Text: brief, "how often ordinary production deployments, over a year of operation, violate it"; `d1-phase1.py` tier 1 orders cells by it; design §Phase 2 C, "Cells are taken in order".
Failure: there are no ordinary production deployments of Episode. Enumerators will rate a counterfactual (1992 hardware? a modern system with this structure?) each in its own way, and that rating decides which cells the C authors reach inside six hours. D1's abort criterion ("no merged cell with silent ≥ 3") inherits the same meaninglessness.
Fix: fix the anchor now, in the brief: "deployments of the kind the paper describes, on the hardware and operating practice it assumes", or drop tier 1 and order by `detectable`, source, beacon. Either is defensible; choose before any list exists.
Leak from the fix: none.

**9. The "paper before code" tier was fixed with the 4/3 count in hand and is unjustified; its mechanics are underdefined.**
Text: design §Phase 1 departure, "a source citation to (99, path order, line), so the paper's statements sort before the code's".
Failure: the steward knows four of seven sealed assumptions are stated in source comments and chose a tier that sorts code-cited cells after every paper-cited cell. Whether that helps or hurts is unknowable, which is the point: it is a choice made with residue, undeclared as such. Also "path order" is undefined (filesystem `find` order differs by machine), and the brief's rule for unnumbered headings ("its heading in quotation marks") maps in `d1-phase1.py` to `(0,)`, before every numbered section, which is not what "earliest" means.
Fix: either drop tier 3 for the beacon, or keep it and say it was chosen knowing the 4/3 split; define path order as byte order of the path below `source/episode/`; map a quoted heading to its byte offset in the text file. Update `d1-phase1.py` before phase 1 and commit its test cases.
Leak from the fix: none.

**10. Findings are not in one schema, so the C condition is pre-formatted for the rubric and N is not.**
Text: design §Phase 2 C, "the cell, the mechanism, the effect, the counterexample"; §Phase 2 N, "find what breaks it".
Failure: C's output lines up with "contract, mechanism, effect" by instruction; N's author is not told to name a violated assumption at all, so the judge reconstructs it. Style also differs by family. A match for C and a partial for N can be the same content.
Fix: one finding schema for both conditions (violated assumption or obligation; mechanism; effect; counterexample; the model's defence, if any), given to N without the cells.
Leak from the fix: none; the schema names no category.

**11. Grok enumerates and models; Claude only models. D2-5 confounds family capability, family correlation with the analysis, and self-authored inputs.**
Text: design §Phase 0 (Codex, Grok) and §Phase 2 (Claude, Grok).
Failure: Grok's C author reads cells half-written by Grok; Claude's C author reads none by Claude. D2-5 ("Grok's C finds fewer than Claude's C") is then uninterpretable along three axes at once, and the design presents Grok as "the cleaner test".
Fix: with four families available, the clean assignment is enumerate (Codex, Grok), merge (Gemini), model (Claude, Codex or Gemini), judge (the family not used in modelling). If Gemini must stay the judge, state the confound in the design and in D2-5 rather than calling Grok cleaner.
Leak from the fix: none.

**12. Transcripts and API traffic redistribute the source the design says it will not redistribute.**
Text: design §Sources, "Neither is committed to tupay (... DCE's licence limits redistribution ...)"; §Phase 0, output "collected unchanged with transcript".
Failure: an agent's transcript over a 415-file tree contains large verbatim reads of it; committed to a public repository, that is the redistribution the manifest rule was meant to avoid. The source is also sent to three providers' APIs and to Google for the merge. The design states the licence limits redistribution without citing the licence text.
Fix: read the mirror's licence file and record what it permits; commit transcript hashes and a tool-output-redacted transcript, keeping the full transcripts private; if the licence does forbid transmission, the design has a problem it must state, not an inconvenience.
Leak from the fix: none.

**13. Budgets are not enforced where they decide the result.**
Text: design §Phase 2, "each author capped at 24 GB and six hours' wall clock; findings committed before the cap counts".
Failure: `box-launch.sh` sets `MemoryMax=24G` and no `RuntimeMaxSec`; `author-sandbox.sh` (bubblewrap) sets neither. The six-hour stop is therefore the steward's hand, timed with a transcript in view. Authors are also not told to commit incrementally, so "before the cap" may mean nothing was committed.
Fix: `RuntimeMaxSec=6h` on the box unit and a cgroup (or `systemd-run --scope`) around bwrap with both limits; the brief tells authors to commit each finding when found; the kill time is logged.
Leak from the fix: none.

**14. Recognised sections and report notes are kept for phase 3 with no stated use; they are the design's only leak detector.**
Text: design §Phase 1, "Recognised sections removed first and kept for phase 3"; P0-4.
Failure: in D1 Recognised lines scored contamination against public reports. In D2 the sealed bugs have no public record, so a Recognised line matching a sealed bug can only mean leakage (the public branch, or something else). The design does not say the judges score them.
Fix: pre-register that judges score every Recognised line and every report note against the sealed list; a match is a leakage flag reported with the result and voids D2-2 for that family's enumerations.
Leak from the fix: none.

**15. The merge script and the phase 1 brief are D1's.**
Text: `d1-merge.sh` line 9 reads `experiments/D1/brief-merge.md`; design §Phase 1, "D1's rule, unchanged".
Failure: the merge packet would be prefixed with a brief written for Raft lists; whatever it says about Raft reaches the merger. The packet format also sends `source` fields that now contain code lines.
Fix: a D2 merge brief, committed before phase 1, differing from D1's by substitution only, with its diff beside it as the enumeration brief has; parametrise the script.
Leak from the fix: none, if the substitution rule is kept.

**16. The Question names the whole workflow; the design runs half of it.**
Text: design §Question, "does the workflow (dependency contracts ...; a formal model ...; observation ...) find the defects"; §Phase 2, no implementation, no paired tests, no mutation pairs, no observability; the implementation pilot is optional and ungated.
Failure: a positive is read as evidence for the workflow; it is evidence for enumeration plus modelling. The pilot, if it runs, has a Codex author reading committed counterexamples before building, which is the reverse of AGENTS.md 4 and must not be called the workflow's implementation side.
Fix: state in §Question and §What this does not claim that D2 tests enumeration and modelling only, and that the pilot is tooling for a later design.
Leak from the fix: none.

**17. Scoring details left open.**
D2-2 counts Claude's findings, which the design itself discounts; pre-register a Grok-only variant. D2-1 reuses "assumption a source comment states" where the holder wrote "assumption or the hazard"; use the holder's wording. Episode's sealed prediction: say who scores it and against what. A "no match" against a confirmed property that the second look finds the analysis got wrong is the only route to an actual discovery in D2; pre-register how it is reported (as a finding against the analysis, with Episode's response). A model that never checks (TLC not run inside the cap) scores as zero findings and is reported as such.

**18. The box author's credential and context.**
`box-launch.sh` and `box-check.sh` close MCP, plugins, history and web, which is good. The design should say whether the box's Anthropic credential is the account under which the analysis sessions ran, and prefer a separate key. Also, Claude Code loads `CLAUDE.md`, not `AGENTS.md`; the brief reaches the box author through `prompt.txt`, so say that the checkout for the box holds the brief and that `AGENTS.md`'s rules are in the prompt, or the author never sees them.

## Minor

**19.** Brief: "a level-3 heading and seven lines" lists eight bullets (D1 inherited the same miscount after `basis` was added). A script reads it; say eight.

**20.** Quote check on C: normalise line endings before matching (a 1990s tree may mix CRLF); the hyphenation join `(\w)-\s*\n\s*(\w)` alters C expressions across line breaks on both sides, fine, but say so; trivial lines (`}`, `#endif`, `return 0;`) verify anywhere within 20 lines, so the check proves existence, not relevance, as in D1; the `- source:` regex takes the last `"` on the line as the close, which works for C string literals only if nothing follows; write test cases for a quote from the right file but a line 21 away, from the wrong file, and with an embedded `"`.

**21.** Paper (1992) and code (DCE 1.2.2) can disagree on what the log guarantees. Say which is authoritative for the model ("as the sources describe them" lets each author pick), and ask authors to report conflicts.

**22.** The enumerators have no wall-clock budget; a Codex run over a 415-file tree can run long and the stop is then the steward's. Set one.

**23.** The design cites "log, 'two notes from Tony'" and "log, 'the eighth steward accepts'", which an outside reader cannot follow (D1's finding 21). Inline the one-line content.

**24.** The merge packet keeps `at-risk`, which after finding 1 names guarantees; fine once `contract.md` exists, otherwise the merger sees four vocabularies.

## The three that matter most

1. **Finding 2.** As written, condition C cannot fail to produce findings, so D2-2 and D2-3 measure cell coverage under a clock, not whether modelling finds anything. The defence-included definition, the honest-environment check and ranked findings are needed before any prereg.
2. **Finding 1.** With no registered guarantee list, the match rubric's "effect" and every `at-risk` field float; the fix (a phase 0a extraction by non-Claude instances, before phase 0) is cheap and leaks nothing.
3. **Finding 4** (with 10). Two judges, one of whom wrote both the answer and a prediction about it, ruling with author identity visible and no rule for which ruling scores, is where a result would be steered after outcomes. Opaque ids, both rulings reported with "holds under both", and a binary cell-to-bug rule fix it.

Findings 3, 5 and 7 should also be settled before phase 0 because each changes something that must exist before any list does (the phase 2 briefs, the denominators, and where the sealed plaintext lives). Findings 8, 9 and 15 must be settled before phase 1; 11, 13, 16 and 17 belong in the design before the prereg; the rest are wording.

Files reviewed: `/home/tony/projects/tupay/experiments/D2/design.md`, `/home/tony/projects/tupay/experiments/D2/brief-enumerate.md`, `/home/tony/projects/tupay/experiments/D2/brief-enumerate.diff-from-D1.txt`, `/home/tony/projects/tupay/experiments/D1/design.md`, `/home/tony/projects/tupay/experiments/D1/brief-enumerate.md`, `/home/tony/projects/tupay/experiments/D1/design-review/fable-1.md`, `/home/tony/projects/tupay/AGENTS.md`, `/home/tony/projects/episode/docs/requests/2026-10-26-to-tupay-D2-answers.md`, and under `/home/tony/projects/tupay/scripts/steward/`: `author-sandbox.sh`, `sandbox-check.sh`, `d1-merge.sh`, `d1-agy-workspace.sh`, `d1-quote-check.py`, `d1-phase1.py`, the three `egress-*.allow` files, and `box/box-launch.sh`, `box/box-check.sh`, `box/box-setup-author.sh`, `box/author-settings.json`.