You are reviewing, adversarially, the scoring of a pre-registered experiment (D2) before it is published. The registration (design.md) fixed the predictions, denominators and judging rules before any outcome existed; later log entries changed the judges and the denominator, and are included. Three judges ruled blind on opaque ids; the mapping from id to author is given. A script computes the score; its output and a draft result are given, with every ruling.

Find defects. In particular: does the script implement each prediction (D2-1 to D2-5, D2-2g, P0-4) exactly as the registration words it, including the denominator, the comment split, the "holds only under both registered judges" rule, the treatment of the missing Gemini cells-2 ruling, and the leakage rule? Recompute every number in the draft's tables from the rulings and check it. Does the draft state anything the evidence does not support, omit anything the registration says must be reported, or present a reading beside the score as if it were the score? Is any rule applied that the registration does not contain? Are the 'reading beside' claims (especially readings 1 and 2) correct as stated?

Report a numbered list of findings, each: severity (blocking / significant / minor), where (file, prediction or table cell), what is wrong, and the evidence (ids, rulings). If an area is correct, say so in one line. Do not propose new predictions or rescore by rules the registration lacks.

===== the registration (experiments/D2/design.md) (design.md) =====
# D2: dependency contracts of Episode's log and recovery, against a sealed answer (design, draft 2)

Steward's design (the eighth steward, Claude Opus 5.5), 2026-10-26, before any list exists. Draft 1 (`7c62375`) adapted D1's design draft 3 (`experiments/D1/design.md`); draft 2 applies Fable 5.1's adversarial review (`design-review/fable-1.md`, 24 findings; dispositions in the log, 2026-10-26, "D2 design review"). D1's rules are kept unless a departure is stated with its reason. Proposed by Tony Mason, 2026-10-26: in Episode, the bugs found by modelling the log and recovery tended to lie where the layers below violated their service contracts; test whether naming those contracts finds them.

## Question
Pointed at the service contracts a component relies on from the layers around it, do **enumeration and modelling** (dependency contracts enumerated by two non-Claude families; a TLA+ model with an environment action per contract) find the defects a recent independent analysis found in Episode's log and recovery? D2 tests these two steps of the workflow only: no implementation side, paired tests or observability layer (review 16).

## How blind, and how far
- **The answer is sealed and outside tupay.** `episode` commit `7eeb027` (local): `sealed/2026-10-26-tupay-D2-findings.md` (sha256 `227d2508…6b7b9698`) and Episode's own prediction (`2a578fa4…fcde4ad4`), hashes recorded in tupay's log (`b23c483`, OTS-stamped), checked without reading. Per Episode's reply: 7 bugs, none visible in DCE 1.2.2's history; in 4, "the enabling assumption or the hazard is stated in a source comment", in 3 nothing in the source points at it; 6 confirmed properties; 1 open item. The analysis was done within the past month; the model families' published training cutoffs are recorded beside the date `spec/` was first pushed to the public `fsgeek/AssFS` branch (asked of Episode), rather than asserted.
- **The steward's not-reading is attested by its log and by nothing else** (review 7): the plaintext is on the same filesystem, under the same uid. Episode has been asked whether it can hold the sealed files out of the steward's reach until phase 3 (`docs/requests/2026-10-26-to-episode-D2-followup.md`); its answer is recorded either way.
- **The steward's residue** (review 6), everything in Episode's reply beyond hashes: the seventh steward's five proposed contract headings; the 4/3 comment split and its wording (D2-1 is built on it, so the residue is in the predictions by design); the open item's subject, in two words; that the analysis also concerned a Linux journal and touched files outside `logbuf`; that session `38a33a70` asked Tony how he fire-tested Episode's recovery (**not read**). The steward has not read the paper beyond its title block, the DCE tree, the sealed files, `episode/spec/`, khipumaq's Episode sessions, or Tony on Episode, and does not before phase 3. The reviewer read the same reply.
- **Guards on what the steward writes:** the enumeration brief is D1's brief v2 by substitution, diff committed (`brief-enumerate.diff-from-D1.txt`); it names no category of dependency. Every other brief (guarantees, both model briefs, merge) is committed in this draft, before any list exists (review 3); a later wording change is an additive amendment that says whether a list had been read. Two examples in the steward's first wording of the model briefs echoed the residue and were cut before commit (log).

## Sources (the authors' only inputs)
- **Paper:** *The Episode File System*, USENIX Winter 1992, public copy https://fsgeek.ca/media/2017/11/1992-The-Episode-File-System.pdf, sha256 `5bd8e654…fb84bed` (byte-identical to Tony's); text by `pdftotext -layout`.
- **Source:** `file/episode/` of OSF DCE 1.2.2 from an independent public mirror (github.com/nealelliott/dce_1.2.2, `745a220`, 2020-04-24, "the inital osf dce code from the osf website"); 415 files byte-identical to Tony's tree. Whole tree given; `logbuf` named, as Episode recommends.
- **Where they disagree, the model follows the source** and records the disagreement (review 21).
- **Licence (review 12).** The tree carries the OSF notice (1995-96) and Tony's copy the 1997 Open Group licence ("academic, research, and internal business purposes ... without fee"; copies only to DCE source licensees); contemporary reports say The Open Group released DCE 1.2.2 under the LGPL in January 2005, which the mirror's files do not state. Read conservatively: the source and the paper are **not committed** to tupay's public repository, and **full author transcripts are kept outside it** (`~/projects/tupay-private/D2/`, sha256 committed), since they contain long verbatim reads. Enumerations, guarantee lists and findings (quotations of at most two lines) are committed. Sending the sources to the model providers is research use.

## Phase 0a: guarantees (new; review 1)
Two fresh instances, Codex and Grok, one each, in `author-sandbox.sh`, each in a history-free checkout of exactly `AGENTS.md`, `BRIEF.md` (= `brief-guarantees.md`) and `source/`, extract `guarantees.md`. Merge as phase 1 does (two Gemini instances in deny-all workspaces, a merge brief by substitution from D1's; a group is kept only where both merges produce it), keeping only guarantees **both extractors** produced; the result, ids `G<n>` in the order of the first extractor's list, is `GUARANTEES.md`, given unchanged to every later author. The steward does not edit it, and reads it (paper content; recorded as residue).

## Phase 0: enumeration (as D1, sources changed)
Two families (Codex, Grok), two independent runs each, fresh instances in `author-sandbox.sh` (no web), each in a separate history-free repository of exactly `AGENTS.md`, `BRIEF.md` (= `brief-enumerate.md`), `GUARANTEES.md` and `source/` (`scripts/steward/d2-checkouts.sh`; manifest committed; `sandbox-check.sh` and its mutation pair before launch). Grok with `--always-approve`. **Wall clock:** two hours per enumerator, enforced by `systemd-run --user --scope -p RuntimeMaxSec=2h -p MemoryMax=24G` around the sandbox (review 13, 22); the kill time, if any, logged. Output `enumeration.md` collected unchanged; report notes kept for phase 3 (review 5, 14). **Quotation check:** `scripts/steward/d2-quote-check.py` (ten test cases written before it ran; line endings normalised, an embedded quotation mark, a line 21 away and a wrong file added as cases before phase 0, review 20).
**Predictions:** P0-1 each list 15 to 60 contracts (p 0.75); P0-2 at least 90% of each list's quotations verify (p 0.6); P0-3 as D1's (p 0.6); P0-4 at least one Recognised section names a reported bug (p 0.5). Abort criteria as D1's.

## Phase 1: merge and order
Recognised sections removed first and kept for phase 3. Two Gemini merges in deny-all workspaces, with `brief-merge.md` by substitution from D1's, diff committed, and `d1-merge.sh` parametrised to take it (review 15); only agreed groups accepted. **Order:** D1's tiers 1, 2 and 4: `silent` as within-list percentile rank (the anchor fixed in the brief to "systems of the kind the paper describes, run as it describes", review 8), then detectability, then the NIST beacon pulse first published after the merge commit. **D1's tier 3 (earliest source) is dropped** (review 9): draft 1's "paper before code" rule was chosen with the 4/3 split in hand; the beacon decides instead. The abort criterion "no merged cell with silent at least 3" is kept under the new anchor. The resulting `CELLS.md` gives each cell's contract, source, violation, at-risk, detectable and silent fields only.

## Phase 2: the model, two conditions, two families
- **Condition C** (`brief-model-C.md`): the sources, `GUARANTEES.md` and `CELLS.md`. **Condition N** (`brief-model-N.md`): the sources and `GUARANTEES.md`, no cells. Both briefs are complete in this draft. Both use **one finding schema** (violated obligation, mechanism, effect, defence, counterexample, confidence; review 10).
- **What counts as a finding (review 2).** A violation of an obligation outside `logbuf` that breaks a guarantee **with the model's defences in place**, while the honest-environment check holds; per cell (C) or per run (N), the defence-removed check must change the outcome (the mutation pair, AGENTS.md rule 5). A violation the model has no defence against is **unguarded**: listed, not a finding. Each author ranks its findings; **the scored set is each author's first ten**; the full list is reported as secondary.
- **Families:** Claude Opus 5.5 (on the box) and Grok (sandbox; calibrated for TLA+ 2026-10-21), each in both conditions: four fresh model authors, no web. **Confounds, stated (review 11):** the sealed analysis was a Claude instance's, so Claude's findings may correlate with it by family; Grok enumerated half of the cells its condition C author reads, Claude none. Neither is "the cleaner test"; D2-5 is read with both.
- **Limits enforced:** 24 GB and **six hours** per author: `RuntimeMaxSec=6h` on the box unit (added to `box-launch.sh` before phase 2) and the scope above for Grok; authors commit each finding when found (review 13). A box checkout carries `CLAUDE.md` holding `@AGENTS.md`, so the Claude author loads AGENTS.md's rules (review 18). The box's Claude credential is Tony's account, the one under which Episode's analysis ran; nothing in a box session reaches another session's content (no MCP, no web, no memory, history cleared by `box-check.sh`), and that is stated as a residue, not tested.
- **Support:** every guarantee-holds result is read with its stated bounds; a check that cannot reach what its violation needs is "no support".
- **Implementation pilot:** not part of D2 (review 16); possible tooling for a later design.

## Phase 3: freeze, unseal, judge
1. **Freeze.** Every phase 2 finding, unguarded list, report note and Recognised line is committed and stamped before anything goes to a judge.
2. **Packet.** Findings and cells under opaque ids, shuffled by the first beacon pulse after the freeze commit; the mapping from id to author, family and condition is committed only as a hash until both rulings are in (review 4).
3. **Judges.** Episode's steward rules first, by its criteria fixed 2026-10-26 (match: same violated contract, mechanism and class of effect; partial: the contract and one of the other two, or the right mechanism under a different contract; no match otherwise; a claim against a confirmed property is flagged; the open item is "unresolved"), and commits its rulings with reasons. Then a fresh Gemini instance, in a deny-all workspace, rules on the same packet **without** the first ruling. **Every prediction is scored under each judge's rulings and reported both ways; it holds only if it holds under both.** Disagreements are listed; the steward resolves none.
4. **Also judged, from the same packet:** each phase 1 cell, binary: does it name the violated contract the sealed file records for some bug (for D2-1, D2-4); each report note and Recognised line against the sealed list, as a separate row, "found by reading", not workflow evidence; a Recognised line matching a sealed bug is a **leakage flag** reported with the result, and voids D2-2 for that family's lists (review 14).
5. **A finding judged "no match" because it contradicts a confirmed property** is the one route in D2 to something the analysis missed: it goes to Episode for a second look, and is reported as a finding against the analysis with Episode's response (review 17).
6. **Episode's sealed prediction** is scored by Episode's steward against the sealed file, reported as Episode's.
A finding that matches several bugs counts for each. An author whose TLC never ran inside its six hours scores zero findings, reported as such.

## Predictions for phase 3 (steward's probabilities; before any list exists)
Denominators: the number of sealed bugs that are violations of an obligation outside `logbuf` by the enumeration brief's definition (asked of Episode, count only; if not answered before phase 0, the seven, and the count is reported when known), and its split by comment (review 5). Wording "assumption or hazard stated in a source comment" is Episode's (review 17).
- **D2-1.** The fraction of sealed bugs whose violated contract some phase 1 cell names is **strictly** higher for those with the assumption or hazard stated in a source comment than for those without. p = 0.6.
- **D2-2.** At least one sealed bug is a "match" among the scored findings of at least one model author. p = 0.55. **Variant D2-2g**, reported beside it: the same, Grok's authors only. p = 0.4.
- **D2-3.** In each family separately, condition C's scored findings match (match or partial) more sealed bugs than condition N's. p = 0.5.
- **D2-4.** At least four of the denominator's sealed bugs have their violated contract named by some phase 1 cell (if the denominator is under five, at least all but one). p = 0.55.
- **D2-5.** Claude's condition C matches (match or partial) more sealed bugs than Grok's condition C. p = 0.6. Read with both confounds above.
Reported beside every count: precision (matched findings over scored findings) per author.

## What this does not claim
Seven bugs in one component of one 1992 file system is a small sample. A match shows enumeration and modelling can find what a careful analysis found; it is not a discovery (the analysis came first), and it calibrates D1, whose question is open-ended.


===== log entries that change judges, denominator or rulings (excerpt by heading) =====
## 2026-10-27: more families offered (Tony); how they are used (18:40Z)
Tony: Kimi, DeepSeek and GLM models are available beside Grok (through OpenRouter, per khipumaq). None has touched tupay's material, which makes them the cleanest third parties tupay has. **Decided, before any judge packet or audit review exists:**
1. **The X3 support audit's mapping** (built by a Claude subagent for a Claude steward) gets an adversarial review by **DeepSeek**, packet inline, before any probe verdict counts. One family checking itself is what the practice's outsider review exists to prevent.
2. **X3's judge stays as registered (Gemini).** **Kimi** rules on the same packets, without Gemini's rulings, as a second reading **reported beside** the registered score, never instead of it.
3. **D2 phase 3**: Episode's steward and Gemini as designed; **GLM** rules on the same packet without either ruling, reported beside, and "a prediction holds only under both" is unchanged. Recorded here as an additive amendment to the design, before any phase 2 output is read.
One role per family, so no family sees two experiments' material. Through the API these run as plain calls with no tools or files, so the packet is the only thing they see.

## 2026-10-29: Episode had answered the follow-up; the seal is v2; a judge run against v1 stopped and voided (05:31Z)
**Found late:** Episode's steward answered the 2026-10-26 follow-up on 2026-10-27 at 18:16Z (`episode` `2066184`, `docs/requests/2026-10-27-to-tupay-D2-followup-answers.md`; counts, yes/no and paths only, read in full), and re-sealed (`b30107c`, signed, 18:15:54Z, 18 minutes before any phase 2 author started). Tony was not aware, and neither steward looked at Episode's repository after asking; the eighth handoff said "awaiting Episode". **Answers:** (1) **denominator: 4 of 7** sealed bugs are environment-contract violations under the enumeration brief's definition, 3 are own-rule defects of `logbuf`; of the 4 with the hazard stated in a source comment, 3 are environment-contract violations and 1 own-rule. The registered rule ("if not answered before phase 0, the seven, and the count is reported when known") makes **seven** the scored denominator, **four reported beside it**. (2) **Fields:** v1 lacked explicit fields and described two bugs' contracts in terms the brief would not accept; **v2 "supersedes v1 for judging"**, changes no bug and adds none, carries all three fields for 7 of 7, and fixes in advance how matching treats one bug whose effect class is uncertain; sha256 `17368796…efb47f17231`, checked here, contents unread; signature verified. (3) **Custody: declined**, with reasons (the same content is readable by this uid in `episode/spec/`, git history, khipumaq and the public `fsgeek/AssFS` branch); the residue stands as attested by the log alone. **Date:** `spec/tla-models` public on GitHub since **2026-10-09**, after every author family's training cutoff.
**The stopped run:** the step 2 judges had been launched at 05:2xZ with **v1** appended. Stopped at 05:31Z during Gemini's findings ruling, which had already returned one result. That run is **void**: moved unread to `~/projects/tupay-private/D2/phase3/void-v1/`, its file hashes in `experiments/D2/phase3/void-v1-run.sha256`, reported with the result as existing and unread. GLM had not started. `d2-judge.sh` now appends v2 (hash-checked); the packets are unchanged (`packets.sha256`); both judges run again on all five, fresh.
**Lapse:** a request sent is not a channel watched. From here, the handoff note names each awaited answer with where it will appear, and the steward looks there at each boundary.

## 2026-10-29: D2 judges: harness failures, and one fresh rerun each, fixed before any ruling is read (06:23Z)
Gemini (v2 appended) answered all five packets: findings 10 items, cells-1 37, cells-3 36 (its answer was in the transcript; the runner's summary step had not printed it, reparsed from the transcript), rows 60; **cells-2's answer is not valid JSON** (a missing delimiter at character 98). **GLM (`z-ai/glm-5.3-prime`) answered nothing**: on all five packets it spent its whole 65,536-token output on reasoning (`finish_reason: length`, content two or three characters; US$3.08 in all). Diagnosed from lengths and parse errors only; no ruling has been read. **Rule:** an answer that does not parse is a harness failure, not an outcome; each such packet gets **one** fresh run (`scripts/steward/d2-judge-rerun.sh`, the same `packet-sent.md`, hash-checked), into `<packet>/<judge>-2/`, the failed run kept beside it. GLM's rerun caps reasoning at 24k tokens. If a rerun fails too, that packet has no ruling from that judge, reported as such; no third run.

## 2026-10-29: D2 judges Gemini and GLM: rulings in, unread (06:26Z)
**GLM rerun** (reasoning capped at 24k tokens): all five packets answered and parsed, finish `stop`: findings 10, cells 37 + 37 + 36, rows 60; US$0.30. **Gemini:** findings 10, cells-1 37, cells-3 36, rows 60 parsed. **Gemini cells-2: its rerun also fails to parse**, at the same place (an item line's 99th character); under the rule logged before the reruns, **cells-2 has no Gemini ruling**, the primary record, reported as such. **Beside it, labelled:** a mechanical repair (escape the nearest unescaped quotation mark before each parse error; 34 escapes, about one per item, consistent with quoted text inside reasons), accepted only because the result parses to exactly the packet's 37 cell ids, saved as `cells-2/gemini-2/ruling-repaired-beside.json`. It changes no value; it is reported beside, never as the registered ruling. **No ruling has been read by the steward.** Every judge directory is committed (`experiments/D2/phase3/judges/`), which fixes the rulings before Episode's. Episode's steward has been asked not to read that directory before committing its own.

## 2026-11-02: Episode's D2 rulings recorded; the mapping published; the first outside score (18:23Z)
**Context: 360.2k of 1M (36%), Tony's figure**, past this steward's 350k line; this tenure hands off after this entry and the handoff note.
**Episode's steward ruled** on all five D2 packets: `episode` `4fd2c09` (good signature, Tony's episode key), `judging/D2/`, reply `episode/docs/requests/2026-11-01-to-tupay-D2-rulings.md` (`6d8981f`). The six file hashes in the reply match the commit's files, checked here. Episode says it verified the packets against `packets.sha256` and did not read `phase3/judges/` or the mapping. Copied into `experiments/D2/phase3/judges/episode/` (`SHA256SUMS`). **The mapping is now published** (`experiments/D2/phase3/mapping.json`, sha256 `7e5d2586…`, equal to `mapping.sha256` committed before any ruling). Every judge has ruled: Gemini (registered; cells-2 has no registered ruling), GLM (beside) and Episode.
**Episode's summary (its words, not tupay's score):** findings: 1 match (F03 → E6), 2 partial (F07 → E6, F08 → E3); 10 of 110 cells name a sealed bug's contract; rows: 2 match (general write-cache knowledge, not leakage). Its own sealed prediction it scores as "mostly wrong": it expected 4 of 7 found by turning the textbook contract into findings; instead the model authors, "modelling the defence in place", reached E6 and E3 and several defects the sealed analysis did not list. **This is the first time a party outside tupay has scored a tupay output** (the month's measure; the Mallku sign is answered). Episode reports packet defects (32 of 60 rows are captured shell output, not claims; F10's text names "F-draft-1", linking it to F05's author; `{SEALED_WHERE}` unexpanded) and **a correction to its sealed file** (Transarc delta comments do survive in the DCE tree; count unchanged; two entries in the area of E7 and E1). Second looks to come in `episode/judging/D2/second-looks.md`: F07 first. Episode asks that requests to it go in `episode/docs/requests/`.
**Publication:** Episode permits publishing its sealed text from tupay **once every judge has ruled and the mapping is published** (both now true), **with its README's correction alongside** (copied above). **Not pushed in this tenure**, as a decision: the D2 packets and judge directories carry authors' text that may quote DCE source, whose licence limits redistribution (D2 design "Licence"; the freeze was committed by hash for that reason). The successor checks the committed D2 files for DCE quotation before the first push, and logs the check.
**Next for the successor:** score D2-1 to D2-5 under each judge separately (a prediction holds only under both Episode and Gemini; GLM beside), precision per author, rows as "found by reading" with leakage flags, then a non-Claude adversarial review. Then T1's pre-registration, then Arariwa's.

===== the findings packet as sent to the judges, with GUARANTEES.md and the sealed analysis v2 (packet-sent.md) =====
# D2 judge packet 1 of 5 (findings): Episode's log and recovery, against the sealed analysis

You are a judge. Work only from the text in this packet; do not read files, run commands or search.

Context: a component's log and recovery (`logbuf` in the Episode file system, OSF DCE 1.2.2) relies on contracts from the layers around it. Independent readers enumerated those contracts ("cells"); independent model authors then wrote TLA+ models and reported **findings**: violations of an obligation outside `logbuf` that break a stated guarantee of the log and recovery with the model's defences in place. A separate analysis, done before any of this and sealed, lists bugs, confirmed properties and an open item; it is given to you at the end of this packet, under "The sealed analysis". Items carry opaque ids; you are not told who wrote them. Packets are split by size by a stated rule; this one is part 1 of 5 (findings).

Episode's criteria (fixed by Episode's steward 2026-10-26, before any list existed): a finding is a **match** for a sealed bug if it has the same violated contract, the same mechanism and the same class of effect; **partial** if it has the contract and one of the other two, or the right mechanism under a different contract; **no match** otherwise. A finding that claims a violation contradicting one of the sealed file's confirmed properties is **flagged** (name the property). A finding about the sealed file's open item is **unresolved**. A finding may match several bugs.

For **each finding**, rule against the sealed bugs.

Answer schema: {"findings": [{"id": "F..", "ruling": "match|partial|no match|unresolved", "bugs": ["<sealed bug id>", ...], "flag_confirmed_property": "<property id or null>", "reason": "<two to four sentences>"}]}

Answer with one JSON object only, as specified. Be concrete and brief; cite the sealed file's bug ids and the item's own words. Do not propose fixes. Disagreement with the sealed analysis is allowed: say so in `reason`.

## Findings

### F01
- violated: The log device left one log-page write (page 0) outstanding while it completed enough later log writes for currentLogBlock to wrap round to the same page index, a full lap of the log.
- mechanism: TranCommitted and BufCommitted compare a position against (EarlierPassno(activeLogBlock), activeLogBlock), where activeLogBlock is the oldest page still in transit. When that page has the same index as currentLogBlock, EarlierPassno returns the current pass, so the stalled page looks a lap newer and every record behind it, including pages still in transit, counts as committed. elbl_ForceTran then returns without waiting, so elbt_TranForce(waitOK=1) returns for a transaction whose END page is not on disk. A crash loses that page, and recovery undoes the transaction.
- effect: A transaction whose commit was acknowledged by a forced commit (fsync path) is rolled back by recovery (silent): breaks G7 and G23 (also G29). The same test gates buffer.c Write's log force (G5), but no WAL break was found within the bounds checked (see REPORT.md).
- defence: The model has the activeLogBlock-based commit test, which is the source's defence against out-of-order completion. Without it (D_ALB=FALSE, `mut_noalb`) a forced commit returns before its page lands even in the honest environment. With it in place, the page-offset wrap defeats it.
- confidence: medium — the arithmetic is exactly log.c's TranCommitted/EarlierPassno. It needs one log write to stay outstanding for a full lap: 4 pages in the model, at least 13 pages in a real log (elbl_MinLogSize with 8K blocks).

### F02
- violated: C021
- mechanism: The committed log records b1 changing from 0 to 1, and the home block is already 1. The page recovery reads has a bad checksum, an unknown checksum version, and a body that records the new value 2 together with an end record. ValidLogPageChecksum forces success on UNKNOWN_CKSUM_TYPE (recover.c:2577). The torn page is parsed instead of pulling the head back to the good prefix. Redo installs 2.
- effect: Recovery finishes and writes a metadata value the disk did not commit. Users see block b1 as 2 rather than the committed 1. Breaks G54 and G1.
- defence: The checksum routine is the defence, and it is enabled in this run. The unknown-version branch makes the check succeed and print that the checksum is being ignored. Removing the checksum defence also accepts the torn body (traces/C021-nodefence.txt). A known bad checksum is pulled back; this cell is the fail-open version.
- confidence: high — the trace ends recovered b1=2, oracle b1=1, cksum bad, version unknown, and the honest replay of the real log keeps 1.

### F03
- violated: The log device completed a later write of a freshly opened log (page 1) before its first write (page 0, which overwrites the restart block), and the machine crashed in between; log.c ForceMap explicitly allows this ("We don't assume in-order writes").
- mechanism: Page 0 still holds the restart record, so elbl_InitLog (elbr_GetCleanLogInfo) treats the log as clean, skips recovery, and reopens it with passno = IncPassno(restart pass), the same pass the crashed incarnation used, so the stale page 1 cannot be told apart from the new incarnation's pages. After a second crash SafeDumpLog's binary search takes the stale page as head, its io_window and pass-number checks pass because page 0 now holds a new page with the same pass, and the stale records join the active log. MarkCommitted matches records by tran id alone and tran ids restart at 0xfffffff6 on every boot, so the stale END of boot-1 tran 1 marks boot-2 tran 1's uncommitted update REDO.
- effect: Recovery reports success but metadata now holds an update of a transaction that never ended (silent): breaks G3 and G8 (also G1, G2). The same mechanism can instead make recovery abort with RCVR_ASSERT on records left UNDEF (G55/G58; `model/results/v3/f1_fail.out`).
- defence: The model has the pass-number fence between log incarnations (IncPassno at open, +2 after recovery), the in-transit io_window check and the per-page pass check. The fence fails because two incarnations get the same pass when no recovery ran between them. The io_window check, which would catch the missing page 0, never runs because the log looks clean. Removing the fence (D_INC=FALSE) lets stale pages join a log with no environment deviation at all (`mut_noinc` fails). Removing D_IOW, D_PASS or D_BUMP leaves this run unchanged (`f1_noIOW`, `f1_noPASS`, `f1_noBUMP` fail the same way).
- confidence: medium — each step follows a source line (log.c elbl_InitLog, recover.c SafeDumpLog/MarkCommitted, tran.c elbt_GlobalTranId), but it needs out-of-order completion among the first pages after a mount, then a second crash before those pages are overwritten.

### F04
- violated: C024
- mechanism: Transaction t1 commits an update of b1 from 0 to 1. The home block is still 0 because the dirty buffer is holding the redo in the active log. Transaction t2 then logs an update and does not commit. elbb_Kill with metadataOK true drops t1's buffer, and the active log that recovery sees no longer contains t1's redo (the model replaces that log with t2's record, which is the checkpoint moving past a buffer that left the age queue). Crash undoes t2 and has nothing to redo for t1, so b1 stays 0.
- effect: A committed metadata update is gone after the crash, while the uncommitted follower is undone. A later free can look committed in memory and then abort, resurrecting or dropping the block the committed transaction described. Breaks G7, G21, and G22.
- defence: elbb_Kill returns BUF_CANTDELETE only when metadataOK is false and the buffer is logged and dirty (buffer.c:1395). That boolean is the defence. It does not look at whether the freeing transaction's end record is durable. block_alloc.c:450 passes metadataOK true. The defence-removed run breaks the same way (traces/C024-nodefence.txt) because the true flag never consulted the commit record.
- confidence: high — the trace ends recovered b1=0 and oracle b1=1 after the kill replaces the log, and the honest run keeps t1's redo.

### F05
- author_status: draft
- violated: C088
- mechanism: A completed, acknowledged log page at the head of the active log is overwritten (no magic, bad checksum). Recovery's binary search does not check magic on the endpoints, finds that page as head, and the in-transit window scan (recover.c:940-975) treats the checksum failure as an incomplete write, moving the head to the previous page. The committed transaction's END is discarded and its records are undone (or simply not redone), with no error.
- effect: a transaction fsync/LogForce reported as committed is silently lost after recovery; G7, G23 (Inv_Durable).
- defence: checksums (ValidLogPageChecksum) and pass numbers detect the damage, but the head-window rule converts detected damage into "not yet written" instead of failing; only damage outside the window raises RCVR_IOERR.
- confidence: medium — mechanism follows the source line by line; the overwrite must hit the newest pages before the crash.

### F06
- violated: C018
- mechanism: The committed log is an update of b1 from 0 to 1 plus an end record, and the home block is already 1. The read of the head returns the previous well-formed page, which contains the update and not the end. Pass number and checksum both accept that page. Recovery classifies the transaction as undo, because it sees no end, and writes the old value 0 back over the committed home block.
- effect: A committed metadata update is undone after a stale read of the log head. Users see the pre-transaction value of b1. Breaks G7.
- defence: SafeDumpLog checks the checksum and the pass number of the page it read (recover.c:933 and the active-page pass check). Both succeed for an older well-formed page. They do not detect that the end record was on the page the device should have returned. The defence-removed run undoes the same committed value (traces/C018-nodefence.txt).
- confidence: high — the trace ends recovered b1=0 and oracle b1=1, with the seen log containing only the update, and the honest run replays the end record and keeps 1.

### F07
- violated: The log device kept one write (page 1) outstanding while it completed a later one (page 2, holding a transaction's END), and the machine crashed. Then a second crash (or a failed restart write followed by a rerun of recovery) interrupted elbr_Recover after elbr_WriteCheckpointBlock and before elbr_WriteRestartBlock.
- mechanism: The first recovery's head search stops at the hole and correctly undoes the transaction. It then writes its checkpoint block at head+1, which is the hole, with the same pass number and a valid checksum. On the next recovery the binary search therefore reaches the stale page 2 as head, and its io_window check sees only the valid checkpoint page. The transaction whose END is on page 2 is marked REDO even though its middle record (on the lost page 1) is gone, so only part of it is redone, reversing the first recovery's decision.
- effect: After a successful recovery a transaction is partly applied, and an abort decided by one recovery is undone by the next (silent): breaks G2 and G6/G8 (also G1).
- defence: The model has recover.c's checkpoint-before-restart block ("the checkpoint block itself becomes the entire active region of the log") plus the head search (binary search, io_window, pass checks). Removing the checkpoint write (D_CKPT=FALSE, `f2_noCKPT`) removes every violation at the same bounds, so the checkpoint write is what turns a tolerated hole into corruption. Removing D_IOW does not change this run (`f2_noIOW`), because at N=4 the binary search, not the io_window check, stops at the hole.
- confidence: medium — direct consequence of recover.c step 5 and SafeDumpLog; needs two independent events (a hole at the first crash, then an interruption inside recovery's two-write window).

### F08
- violated: C041
- mechanism: The update of b1 is logged in memory and the log force is the next step. On AIX, asevent_Iodone clears ESOFT, b_resid, and B_ERROR before the log looks at the event (asevent.c:1070). The force is therefore reported successful while the log page was not stored. Write-ahead then allows the home write, so disk b1 becomes 1. No end record is durable, so the committed image is still the old value. Crash sees an empty log and leaves b1 at 1.
- effect: A metadata write that the file system treated as logged is on disk, and the log that should undo it is not. After the crash users see the uncommitted value. Breaks G5 and G29.
- defence: The log's check of the I/O status is the defence. It never observes ESOFT, because the async layer cleared the error first. With that check removed the same home block is still published (traces/C041-nodefence.txt).
- confidence: high — the trace ends with an empty log, recovered b1=1, and oracle b1=0, and the honest force keeps the log record ahead of the home write.

### F09
- violated: C058
- mechanism: An uncommitted update of block b1 from 0 to 1 is logged and its home block is written. The environment then plants a restart image on the first log block. elbr_GetCleanLogInfo (recover.c:2813 and recover.c:2840) treats salvage magic plus a first record of type restart as a clean log, and it does not checksum that page (recover.c:2826 and recover.c:2737). Replay never runs. The home block stays 1.
- effect: After the crash the aggregate mounts as a clean log. Users see metadata the transaction did not commit. Breaks G56, G58, G8, and G1.
- defence: The clean test is the defence, and a well-formed restart is what it accepts. elbr_InitLogPageHdr already puts the salvage magic on every page, and the restart page is deliberately not checksummed, so a restored or forged restart is indistinguishable from a finished recovery. Removing the magic check does not help: the clean path is taken because the image looks like a restart, which traces/C058-nodefence.txt also shows.
- confidence: high — the trace ends recovered b1=1, oracle b1=0, with fake restart set, and the honest run of the same uncommitted image undoes it.

### F10
- author_status: draft
- violated: C071
- mechanism: Bits of a completed head log page decay (checksum fails, header intact). Recovery finds it as head by pass number; the in-transit scan (index 0 is the head itself) sees the bad checksum and pulls the head back one page, so the END of an acknowledged transaction is dropped and its updates are undone or not redone.
- effect: acknowledged commits silently disappear; G7, G23.
- defence: checksums detect the decay, but within the io_window range a bad page is taken to be an in-flight write and silently truncated.
- confidence: medium — same mechanism as F-draft-1.

## Cells named by a finding

### C018
- contract: A later read of a block must return, sector by sector, the data of the last write to that sector that the driver has reported complete.
- source: logbuf/recover.c:892 " * We trust the log to make sure it doesn't assume a page with"
- violation: A drive cache, a multipath disk, or a host buffer returns a stale copy after a completed write, so recovery or the next mount sees an older log page.
- at-risk: G54 and G7 fail because the head, the pass number, or the redo records recovery reads are not the ones the running system forced.
- detectable: partly — a stale page often fails the pass-number or checksum test, and an older but well-formed page can be mistaken for the head.
- silent: 2 — coherent SCSI disks usually read what they just wrote, but stale cache and multipath windows are an occasional field failure.

### C021
- contract: Administrators must select a supported effective checksum scheme when relying on torn-page or corruption detection.
- source: logbuf/recover.c:2582 "printf("Log has unknown checksum type on disk. Ignoring checksum check\n");"
- violation: A log uses checksum version NONE or an unknown type and the deployment assumes every torn page will be rejected.
- at-risk: G54 and G1: unchecked damaged pages can enter head selection or replay; checksumming is conditional on configuration.
- detectable: partly — the version is inspectable and an unknown version emits a warning; version NONE can operate without an error.
- silent: 2 — Legacy configurations can silently lack the protection expected of newer logs.

- contract: Provisioning must select a working supported checksum format when relying on detection of partial log-page writes.
- source: logbuf/recover.c:2445 " case LOGREC_CKSUMVER_NONE:"
- violation: An aggregate uses the no-checksum format yet expects a partly written multi-sector page to be detected.
- at-risk: G54, G1: sector atomicity alone does not establish completeness of the remaining sectors.
- detectable: partly — checksum mode is inspectable, but damage cannot be checked without redundancy.
- silent: 1 — No-checksum operation can conceal torn pages, but the incidence depends on configuration and crash timing.

- contract: The checksum version recorded on the log must be a version recovery knows, so torn pages are rejected rather than ignored.
- source: logbuf/recover.c:2578 " /* Unknown checksum type recorded on disk. Force success of"
- violation: An operator or patchlog sets an unknown checksum version, and recovery then treats every page checksum as valid.
- at-risk: G54 fails because a torn or out-of-order log page in the in-transit window is accepted as the head, and replay proceeds from a page the disk did not finish writing.
- detectable: partly — recovery prints that it is ignoring the checksum, but it still returns success if the rest of the log parses.
- silent: 1 — logs are created with the CRC-32 version, and changing that version is a rare manual act.

- contract: The checksum version stored in the log is one this recovery code implements.
- source: logbuf/recover.c:2578 " /* Unknown checksum type recorded on disk. Force success of"
- violation: A newer or older creator writes a checksum version the running salvager does not know.
- at-risk: G54 fails open: an unknown version forces the checksum check to succeed, so a torn or corrupt page is replayed.
- detectable: partly — recovery prints that it is ignoring the checksum, and then continues.
- silent: 1 — matching kernel and salvager binaries are the normal deployment, and a mismatch is rare over a year.

### C024
- contract: Callers may set metadataOK on Kill only after the transaction freeing that metadata has committed.
- source: logbuf/buffer.c:1359 "PARAMETERS -- metadataOK is true if it is safe to kill dirty metadata"
- violation: An allocator passes metadataOK=1 merely because a free was issued, before that free commits.
- at-risk: G21, G22, G44: discarding the dirty buffer can retire the only committed state still needed if the free is undone.
- detectable: partly — a transaction-aware allocator can verify the freeing commit, but Kill receives only the caller’s boolean.
- silent: 2 — A false safety assertion can silently bypass the discard protection.

- contract: A caller may authorize killing dirty metadata only after the freeing transaction and all prior modifiers have committed.
- source: logbuf/buffer.c:1370 " * buffers. This will only be true if the transaction that freed the"
- violation: An allocator passes metadataOK=true before its freeing transaction commits.
- at-risk: G44, G6: the only dirty copy can be discarded while rollback still needs it.
- detectable: partly — false metadataOK is checked, but a dishonest true is trusted.
- silent: 1 — A false kill authorization requires a caller defect and may remain hidden until rollback is needed.

- contract: Callers must pass metadataOK to elbb_Kill only after the transaction that freed that metadata block has committed, which is also after every transaction that modified the block has committed.
- source: logbuf/buffer.c:1359 " * PARAMETERS -- metadataOK is true if it is safe to kill dirty metadata"
- violation: The allocator kills a dirty logged buffer before the freeing transaction's end record is on disk, so the buffer leaves the age queue while its updates exist only in the log or are still uncommitted.
- at-risk: G21 and G22 fail because checkpointing drops the log tail when no dirty buffer still pins it, and killing the buffer early discards committed updates that were not yet on their home blocks.
- detectable: no — with metadataOK set, the kill succeeds and returns zero.
- silent: 1 — the freed-block list kills metadata only after TranIsCommitted returns true, so a premature kill in ordinary operation is rare.

- contract: A caller passes metadataOK to elbb_Kill only after the transaction that freed that metadata block has committed.
- source: logbuf/buffer.c:1360 " * buffers. This will only be true if the transaction that freed the"
- violation: The allocator kills a dirty logged buffer while the freeing transaction is still uncommitted, and the buffer's updates disappear from memory.
- at-risk: G44 and G6 fail because recovery may still undo other records on that block while the killed dirty image has already been discarded, and a reuse can then proceed without the committed free.
- detectable: partly — elbb_Kill returns BUF_CANTDELETE when metadataOK is false and the buffer is dirty; a true flag on an uncommitted free is accepted.
- silent: 1 — fb_CheckTrans kills only after elbb_TranIsCommitted, so a premature kill is a rare caller bug.

### C041
- contract: On AIX, an I/O completion reported as ESOFT must mean the transfer finished and is durable, because the async layer clears that error and treats the buffer as successful.
- source: async/asevent.c:1070 " if (bp->b_error == ESOFT) {"
- violation: The AIX driver returns ESOFT for a write that was not stored, and Episode clears the error and continues as if the log page or metadata block were on disk.
- at-risk: G5 and G29 fail for the same reason as a false success: the log force returns, and a later crash finds the page missing.
- detectable: no — the error is deliberately discarded before the log package sees it.
- silent: 2 — recovered soft errors are normal on AIX and are harmless, but an ESOFT that does not mean the data was stored happens on real adapters often enough to be occasional.

- contract: The driver reports a transfer that did not finish as a hard error, and the async layer is entitled to treat any other completion as success.
- source: async/asevent.c:1070 " if (bp->b_error == ESOFT) {"
- violation: AIX returns ESOFT for a write that did not reach stable media, and asevent_Iodone clears b_error and B_ERROR before the log inspects the event.
- at-risk: G5 and G29 fail because a log force or a metadata write is treated as committed when the transfer was only partial.
- detectable: no — the error is cleared inside the async layer before CheckIOError runs.
- silent: 2 — this path exists only on AIX, and drivers return ESOFT for an incomplete durable write only on some media faults.

### C058
- contract: The storage and operating environment must preserve a clean restart marker’s authenticity and its ordering after all recovery or shutdown data writes.
- source: logbuf/recover.c:2738 "We choose not to checksum the log page containing a restart record"
- violation: A forged, corrupted, restored, or prematurely durable restart marker survives while recovered metadata writes do not.
- at-risk: G39, G55, G56: a plausible restart record can suppress necessary recovery because it is not checksummed.
- detectable: partly — header and record checks catch malformed markers, but not a plausible stale or wrongly ordered clean marker.
- silent: 1 — Normal synchronous durable I/O preserves this order; silent violation is rare.

- contract: The restart page, which recovery does not checksum, must keep the exact header and restart record written by log creation, clean shutdown, or a finished recovery.
- source: logbuf/recover.c:2738 " * We choose not to checksum the log page containing a restart record"
- violation: Bit rot or a torn write leaves the salvage magic and a restart record type in the first log block of a log that still has an active tail, or destroys a genuine restart record.
- at-risk: G56 and G58 fail because a dirty log is treated as clean and ordinary operation starts without replay, or a clean log is treated as dirty and recovery rewrites metadata from an old tail.
- detectable: no — the clean test looks only for the magic and a restart record, not a checksum.
- silent: 1 — one block is rewritten at shutdown and recovery, and an undetected flip of that pattern is rare.

- contract: Operators and tools must not write a restart record, or otherwise mark the log clean, except by log creation, a clean shutdown, or a recovery that has finished applying updates.
- source: logbuf/recover.c:2738 " * We choose not to checksum the log page containing a restart record"
- violation: patchlog or an operator copies a restart record onto the first log block of a dirty aggregate to make it mount, without replaying the tail.
- at-risk: G56 and G1 fail because attach treats the log as clean and serves metadata that still contains uncommitted updates and is missing committed ones.
- detectable: no — a well-formed restart record is the definition of a clean log.
- silent: 1 — normal operation does not rewrite the restart block by hand, and doing so is a rare administrative act.

### C071
- contract: The storage stack must preserve completed writes until an explicitly authorized overwrite.
- source: logbuf/recover.c:755 "active log pages outside the in-transit window are really"
- violation: A completed active log page later develops an unreadable sector or silently loses bits.
- at-risk: G1, G6, G7, G20: the only surviving undo or redo image may be lost.
- detectable: partly — supported checksums detect many corruptions, but cannot reconstruct lost records.
- silent: 1 — Latent media damage without a reported error is rare but possible.

- contract: The device must preserve completed home-block writes until a later authorized overwrite.
- source: logbuf/recover.c:1354 " writeBlock(&buf, returnVal);"
- violation: A controller loses an acknowledged recovered block after a clean restart record is written.
- at-risk: G55, G1: recovery is declared complete although its repairs are missing.
- detectable: no — successful completion does not expose later loss.
- silent: 1 — Loss of previously completed home writes is an exceptional hardware failure and often produces later visible damage.

- contract: Until Episode overwrites a block, the device returns the bytes of the last completed write to that block, or it returns an I/O error.
- source: logbuf/recover.c:756 " * expected to be on disk correctly. If checksum errors are"
- violation: A later media error, a misdirected write, or a dropped sector changes a log page or a metadata block that recovery still needs, and the read succeeds with different bytes.
- at-risk: G6, G7, and G1 fail; a corrupted log page outside the in-transit window aborts recovery, and a corrupted metadata home block is applied as if it were the image the log expected.
- detectable: partly — log pages are checksummed and a bad page raises RCVR_IOERR; metadata home blocks have no checksum, so a wrong image is accepted.
- silent: 1 — silent bit rot or a misdirected write over a year on these SCSI disks is rare, and a checksum failure is visible when it hits a log page.

### C088
- contract: The allocator and administrator must reserve log blocks exclusively and keep their addresses and log length fixed during normal logging.
- source: §"Data Architecture" "The log container does not grow or shrink"
- violation: A live resize, relocation, or overlapping allocation lets file data overwrite active log pages.
- at-risk: G20, G21, G54: retained history and circular page numbering cease to describe persistent storage.
- detectable: partly — checksum and page-number failures may reveal damage, after recovery information is already lost.
- silent: 1 — The source’s normal initialization and allocation rules avoid live log resizing.

- contract: The aggregate layer must keep the log allocation and address map fixed while logging is attached.
- source: logbuf/log.c:697 " IN daddr_t *logLocnArray,"
- violation: An online resize or relocation changes log blocks without a coordinated log replacement.
- at-risk: G7, G54: recovery and logging disagree about where retained records reside.
- detectable: partly — malformed page sequences may be found; no relocation protocol is supplied here.
- silent: 1 — Normal operation deliberately does not resize the log; unsupported live changes are rare.

- contract: The log container must not grow or shrink while the aggregate is in use.
- source: §"Data Architecture" "do not, in the current implementation, change dynamically. The log container does not grow or shrink"
- violation: An operator or a later tool extends or truncates the log container while transactions are running, so the in-memory location array and the pass numbers no longer describe the disk.
- at-risk: G17 and G9 fail because admission control and recovery both assume a fixed circular buffer, and a resized log can wrap onto live records or drop the tail.
- detectable: partly — a size mismatch at the next attach is rejected, but a resize under a live kernel is not checked on each write.
- silent: 1 — the implementation provides no working resize of the log, so a deployment run as described does not change it.

- contract: The operator gives the aggregate a log at least as large as the minimum for its workload, and leaves that container's size and block list fixed while the aggregate exists.
- source: §"Data Architecture" "The log container does not grow or shrink"
- violation: newaggr creates a log smaller than elbl_MinLogSize, or an administrator grows, shrinks, or relocates the log container under a live aggregate.
- at-risk: G17 and G28 fail because elbl_InitLog returns LOG_LOGFULL, or a resized log moves the blocks whose pass numbers recovery uses to find the head.
- detectable: yes — an undersized log is rejected at init; a resized live log is not checked again and shows up later as a bad pass or a failed recovery.
- silent: 2 — the creation check is visible, while an offline rewrite of the log container is an occasional administrative mistake and is silent until the next crash.

## GUARANTEES.md (the guarantees findings cite as G<n>)
# GUARANTEES.md: what the log and recovery guarantee

Extracted from the paper and the source by two readers independently; kept where both found the same guarantee. Each guarantee is given as each reader stated it, unedited.

### G1
- guarantee: After a crash and successful recovery, file-system metadata, including directories, allocation bitmaps, indirect blocks, and anode tables, is consistent.
  source: §"Background" "guarantee that after a crash, the le system meta-data (directories, allocation bitmaps, indirect blocks and anode tables) are consistent, generally eliminating the need for running \fsck.""
- guarantee: After a crash, file-system meta-data (directories, allocation bitmaps, indirect blocks, and anode tables) are consistent.
  source: §"Background" "guarantee that after a crash, the le system meta-data (directories, allocation bitmaps, indirect blocks and"

### G2
- guarantee: A committed metadata transaction applies all its updates atomically.
  source: §"Component Architecture" "that either all the updates within a transaction (if a transaction commits), or none of them (if a transaction aborts), will be applied."
- guarantee: All meta-data updates are grouped into atomic transactions: if a transaction commits, every update in it is applied; if it aborts, none is applied.
  source: §"Component Architecture" "that either all the updates within a transaction (if a transaction commits), or none of them (if a transaction"

### G3
- guarantee: An aborted metadata transaction leaves none of its updates applied.
  source: §"Component Architecture" "that either all the updates within a transaction (if a transaction commits), or none of them (if a transaction aborts), will be applied."
- guarantee: All meta-data updates are grouped into atomic transactions: if a transaction commits, every update in it is applied; if it aborts, none is applied.
  source: §"Component Architecture" "that either all the updates within a transaction (if a transaction commits), or none of them (if a transaction"

### G4
- guarantee: For every metadata update, logging records both the original and new values.
  source: §"Component Architecture" "value logging techniques [MOH 89]. In a nutshell, this form of logging works by logging, for every update made to any le system meta-data, both the original and new values of the updated data."
- guarantee: For every update to file-system meta-data, the log stores both the original value and the new value of the updated data.
  source: §"Component Architecture" "made to any le system meta-data, both the original and new values of the updated data. Furthermore,"

### G5
- guarantee: Before writing a dirty metadata buffer to its home disk location, the buffer package writes the corresponding log entries to disk.
  source: §"Component Architecture" "before the bu er package allows any dirty meta-data bu er to be written back out to the disk, it writes out these log entries to the disk."
- guarantee: Before the buffer package writes any dirty meta-data buffer back to disk, it writes that buffer's log entries to disk.
  source: §"Component Architecture" "before the bu er package allows any dirty meta-data bu er to be written back out to the disk, it writes"
- guarantee: Before a dirty buffer on the log age queue is written, the log is forced at least through that buffer's last log record.
  source: logbuf/buffer.c:3769 " /* maybe force write log */"

### G6
- guarantee: Recovery restores aborted metadata updates to their values before the transaction began.
  source: §"Component Architecture" "the log to undo all of the updates made to the meta-data, and restore the meta-data to its state before the transaction started."
- guarantee: If a transaction aborted, the log contains enough information to undo all of its meta-data updates and restore the meta-data to its state before the transaction started.
  source: §"Component Architecture" "the log to undo all of the updates made to the meta-data, and restore the meta-data to its state before the"

### G7
- guarantee: Recovery redoes committed metadata updates even when their buffers had not reached disk before the crash.
  source: §"Component Architecture" "transaction started. If the transaction committed, there is enough information in the log to redo all of the meta-data updates, even those that hadn't yet made it from the disk bu ers to the disk."
- guarantee: If a transaction committed, the log contains enough information to redo all of its meta-data updates, including those that had not yet reached disk from the buffers.
  source: §"Component Architecture" "meta-data updates, even those that hadn't yet made it from the disk bu ers to the disk."

### G8
- guarantee: Recovery undoes transactions that were uncommitted at the crash.
  source: §"Component Architecture" "The recovery procedure runs after a crash, replaying the committed transactions and undoing the uncommitted transactions, and thus restoring the le system to a consistent state."
- guarantee: After a crash, recovery replays committed transactions and undoes uncommitted transactions, restoring the file system to a consistent state.
  source: §"Component Architecture" "uncommitted transactions, and thus restoring the le system to a consistent state. Since the log only"

### G9
- guarantee: The paper initially promises recovery time proportional to activity at the crash rather than disk size, subject to its later qualification about uncheckpointed committed transactions.
  source: §"Component Architecture" "contains information describing transactions still in progress, recovery time is proportional to the activity at the time of the crash, not to the size of the disk."
- guarantee: The log contains only information describing transactions still in progress, so recovery time is proportional to activity at the time of the crash and not to disk size.
  source: §"Component Architecture" "contains information describing transactions still in progress, recovery time is proportional to the activity"

### G10
- guarantee: The paper initially promises recovery time proportional to activity at the crash rather than disk size, subject to its later qualification about uncheckpointed committed transactions.
  source: §"Component Architecture" "contains information describing transactions still in progress, recovery time is proportional to the activity at the time of the crash, not to the size of the disk."
- guarantee: Recovery takes essentially the same amount of time on small and large aggregates.
  source: §"Recovery Time" "From this data, we can see that recovery takes essentially the same amount of time on"
- guarantee: Recovery time does not depend on aggregate size.
  source: §"Recovery Time" "none of which, however, are the aggregate size. Despite this complexity, it also appears that in typical"

### G11
- guarantee: The paper claims log replay runs orders of magnitude faster than BSD fsck.
  source: §"Component Architecture" "of magnitude faster than the BSD fsck program."
- guarantee: Replaying the log runs orders of magnitude faster than BSD fsck.
  source: §"Component Architecture" "at the time of the crash, not to the size of the disk. The result is that the log-replaying operation runs orders"

### G12
- guarantee: Transactions may release transactional locks before the end of the transaction.
  source: §"Logging Architecture" "tional locking instead of two-phase locking. Episode transactions can acquire locks when they need them, and drop them as soon as they are nished using them, rather than waiting for the transaction's end."
- guarantee: A transaction may acquire a lock when it needs it and drop the lock as soon as it has finished using the object, without waiting for the transaction to end.
  source: §"Logging Architecture" "and drop them as soon as they are nished using them, rather than waiting for the transaction's end. This"

### G13
- guarantee: All transactions in an equivalence class commit together or none commit.
  source: §"Logging Architecture" "either all of its transactions commit or none do.3 In the example above, transaction 1 and 2 would form"
- guarantee: Either every transaction in an equivalence class commits, or none of them does.
  source: §"Logging Architecture" "either all of its transactions commit or none do.3 In the example above, transaction 1 and 2 would form"

### G14
- guarantee: A crash before all transactions in an equivalence class have committed aborts every transaction in that class.
  source: §"Logging Architecture" "If the system crashes before all of the transactions in an EC have committed, all the transactions in the EC are aborted."
- guarantee: If a crash intervenes, Episode aborts transactions that might otherwise have been able to commit, rather than letting another transaction make uncommitted data permanent.
  source: §"Logging Architecture" "have otherwise been able to commit, if a crash intervenes. Speci cally, all active transactions that lock the"
- guarantee: If the system crashes before every transaction in an equivalence class has committed, every transaction in that class is aborted.
  source: §"Logging Architecture" "the EC are aborted. It is therefore desirable to minimize the duration and the number of ECs formed in the"

### G15
- guarantee: An explicit synchronization request such as fsync prevents the requested metadata persistence from being indefinitely deferred.
  source: §"Logging Architecture" "Meta-data changes to the disk itself can often be deferred, unless speci cally requested by an oper- ation like fsync. Consistency of the le system doesn't require that the system be current."
- guarantee: Meta-data changes to disk may be deferred unless an operation such as fsync requests otherwise.
  source: §"Logging Architecture" "Meta-data changes to the disk itself can often be deferred, unless speci cally requested by an oper-"

### G16
- guarantee: When a newly allocated data block has an incomplete first-write transaction at a crash, recovery zeroes the block.
  source: §"Logging Architecture" "to it completes. If the system crashes and the transaction aborts, the recovery procedure for this special transaction zeroes the contents of the block."
- guarantee: If a crash occurs after a block is allocated to a file and before the first write to that block, and the special allocation transaction aborts, recovery zeroes the contents of the block.
  source: §"Logging Architecture" "transaction zeroes the contents of the block."

### G17
- guarantee: Log-space admission control keeps running transactions within the available log space.
  source: §"Logging Architecture" "when they begin. This allows the use of a very simple algorithm to ensure that running transactions never exceed the space available in the log."
- guarantee: Transaction sizes are bounded when they begin, and running transactions never exceed the space available in the log.
  source: §"Logging Architecture" "exceed the space available in the log. Transactions that run too long or modify too much data represent"

### G18
- guarantee: Dirty metadata buffers may be written before their transactions end.
  source: §"Logging Architecture" "when to write these bu ers. Old value / new value logging, on the other hand de-couples the writing of bu ers from the end of transactions, at the expense of having to write more data to the log."
- guarantee: Because the log holds old and new values, a dirty meta-data buffer may be written to its home on disk before its transaction commits.
  source: §"Logging Architecture" "bu ers from the end of transactions, at the expense of having to write more data to the log."

### G19
- guarantee: Each transaction in a multi-transaction filesystem operation leaves the filesystem consistent, even if the overall operation is unfinished.
  source: §"Logging Architecture" "operations, followed by a deletion of the empty le. After each transaction, the le system is consistent, if not in the nal desired state."
- guarantee: After each bounded transaction that makes up a larger operation, the file system is consistent, even if it is not yet in the final desired state.
  source: §"Logging Architecture" "not in the nal desired state."

### G20
- guarantee: The active log retains uncommitted transactions needed for crash undo.
  source: §"Recovery Time" "active portion of the log is that part of the log that needs to be replayed after a crash, and must include all of the uncommitted transactions, since these must be undone in the event of a crash."
- guarantee: The active portion of the log includes all uncommitted transactions, which must be undone after a crash.
  source: §"Recovery Time" "of the uncommitted transactions, since these must be undone in the event of a crash. The active portion"

### G21
- guarantee: The active log also retains committed updates whose metadata buffers remain dirty, qualifying the earlier claim that recovery depends only on in-progress transactions.
  source: §"Recovery Time" "of the log may go back even further, should the bu er cache still contain dirty meta-data blocks that were modi ed by committed transactions."
- guarantee: The active portion of the log also includes committed updates whose dirty meta-data blocks still reside only in the buffer cache.
  source: §"Recovery Time" "modi ed by committed transactions. In this case, the updates are in the log and only in the log, requiring"

### G22
- guarantee: Checkpointing discards committed log history only after writing the buffers required to preserve those transactions.
  source: §"Recovery Time" "the replay of that part of the log in the event of a crash. The operation of writing bu ers modi ed by committed transactions and discarding those portions no longer required to ensure the permanence of those"
- guarantee: Checkpointing writes buffers modified by committed transactions and discards those log portions no longer required to make those transactions permanent.
  source: §"Recovery Time" "transactions is generally called checkpointing the log."

### G23
- guarantee: elbb_LogForce with waitOK one returns only after the transaction has committed, making its updates persistent.
  source: logbuf/tran.c:950 " * 1 -- don't return until transaction has committed. This guarantees * persistence for updated done under this transaction. "fsync" is the"
- guarantee: elbb_LogForce with waitOK 1 does not return until the transaction has committed, which makes updates done under that transaction persistent.
  source: logbuf/tran.c:950 " * 1 -- don't return until transaction has committed. This guarantees"

### G24
- guarantee: elbb_LogForce with waitOK two waits for completion and serializes the transaction with transactions begun after the call returns.
  source: logbuf/tran.c:953 " * 2 -- don't return until transaction has completed. This ensures * serialization of this transaction with respect to any transactions"
- guarantee: elbb_LogForce with waitOK 2 does not return until the transaction has completed, which serializes it with any transaction started after the call returns.
  source: logbuf/tran.c:953 " * 2 -- don't return until transaction has completed. This ensures"

### G25
- guarantee: Ending a transaction in an unfinished equivalence class may leave it pending rather than committed.
  source: logbuf/tran.c:426 " * elbt_EndTran -- handle changing the state of a transaction from active to * complete or pending (EC)."
- guarantee: Until the last member of an equivalence class ends, every earlier member is only pending and has no END record on disk.
  source: logbuf/tran.c:447 " /* This tran is part of an EC but we are not the last. Just mark"

### G26
- guarantee: An equivalence class writes all member batch-end records before writing its final head end record.
  source: logbuf/tran.c:795 " * We won't write the end record out for the final transaction until * after all the batch end records have been written out."
- guarantee: Equivalence-class ends are written atomically: the head transaction writes a BEND record for each member and then its own END, and recovery reconstitutes those member END records only if the head transaction is REDO.
  source: logbuf/recover.c:1687 " * Bulk ends are the recovery end of ECs. Because the end records must"

### G27
- guarantee: Starting a transaction with an old transaction ID does not block waiting for other transactions to complete.
  source: logbuf/buffer.c:1739 " * By providing an old transaction ID, this call will not block. If there * is no transaction ID, this call might wait pending completion of other"
- guarantee: Starting a transaction with a non-null oldTranId starts a nested transaction and does not block waiting for log space.
  source: logbuf/buffer.c:1739 " * By providing an old transaction ID, this call will not block. If there"

### G28
- guarantee: When transaction allocation fails because of log pressure, elbb_StartTran handles the full log and retries.
  source: logbuf/buffer.c:1743 " * If this routine fails to allocate a transaction we presume it is because * the log is full and so we invoke the log full handling and try again."
- guarantee: elbb_StartTran without an old transaction retries, including log-full handling, until it obtains a transaction (except during a bounded kernel-panic loop).
  source: logbuf/buffer.c:1743 " * If this routine fails to allocate a transaction we presume it is because"

### G29
- guarantee: A transaction is not treated as durably committed merely because its end record has been constructed in memory.
  source: logbuf/log.c:140 " * The transactions on the cTranList are being held until their end records are * actually committed to disk. Then they are returned to the tran module when"
- guarantee: A transaction is committed only once its last log record has been written to disk, not merely when the transaction has ended in memory.
  source: logbuf/log.c:2259 " * elbl_IsTranCommitted -- check to see if the last record of this transaction"
- guarantee: Completed transactions are held until their end records are committed to disk, and only then are they garbage-collected.
  source: logbuf/log.c:140 " * The transactions on the cTranList are being held until their end records are"

### G30
- guarantee: elbl_ForceBuffer forces the log to disk through the specified buffer's last update.
  source: logbuf/log.c:2108 " * elbl_ForceBuffer -- force the log to disk up to the specified buffer's * last update."
- guarantee: After that log force, elbl_ForceBuffer has made the buffer's log records committed on disk.
  source: logbuf/log.c:2125 " afsl_Assert (BufCommitted (lmP, bP));"

### G31
- guarantee: elbb_Release with elbb_sync returns after both the necessary log and the data buffer have been written.
  source: logbuf/logbuf.p.h:66 " elbb_sync, /* force write log, force write data buffer, upon return * both log and data buffer have been written */"
- guarantee: elbb_Release with elbb_sync does not return until the log (if needed) and the data buffer have both been written.
  source: logbuf/logbuf.p.h:66 " elbb_sync, /* force write log, force write data buffer, upon return"

### G32
- guarantee: elbb_QuiesceSystem with SERIALIZE waits for transactions active at entry to end.
  source: logbuf/logbuf.p.h:332 " * SERIALIZE -- ensure all currently active trans have ended."
- guarantee: elbb_QuiesceSystem with SERIALIZE returns only after every transaction that was active at the start of the call has ended.
  source: logbuf/logbuf.p.h:332 " * SERIALIZE -- ensure all currently active trans have ended."

### G33
- guarantee: elbb_QuiesceSystem with COMMIT waits for transactions active at entry to commit.
  source: logbuf/logbuf.p.h:333 " * COMMIT -- as above but wait until all trans have committed."
- guarantee: elbb_QuiesceSystem with COMMIT returns only after every such transaction has committed.
  source: logbuf/logbuf.p.h:333 " * COMMIT -- as above but wait until all trans have committed."

### G34
- guarantee: elbb_QuiesceSystem with WRITE schedules dirty user-data buffers for writing.
  source: logbuf/logbuf.p.h:335 " * WRITE -- schedules all dirty buffers containing user data."
- guarantee: elbb_QuiesceSystem with WRITE schedules all dirty user-data buffers; with FSYNC it also waits for those writes; with FLUSH it also invalidates user buffers; with FLUSHALL it invalidates all buffers.
  source: logbuf/logbuf.p.h:335 " * WRITE -- schedules all dirty buffers containing user data."

### G35
- guarantee: elbb_QuiesceSystem with FSYNC also waits for the user-data writes to finish.
  source: logbuf/logbuf.p.h:336 " * FSYNC -- also waits for writes to complete."
- guarantee: elbb_QuiesceSystem with WRITE schedules all dirty user-data buffers; with FSYNC it also waits for those writes; with FLUSH it also invalidates user buffers; with FLUSHALL it invalidates all buffers.
  source: logbuf/logbuf.p.h:335 " * WRITE -- schedules all dirty buffers containing user data."

### G36
- guarantee: elbb_QuiesceSystem with FLUSH also invalidates user-data buffers.
  source: logbuf/logbuf.p.h:337 " * FLUSH -- also invalidates user buffers (vol_close)."
- guarantee: elbb_QuiesceSystem with WRITE schedules all dirty user-data buffers; with FSYNC it also waits for those writes; with FLUSH it also invalidates user buffers; with FLUSHALL it invalidates all buffers.
  source: logbuf/logbuf.p.h:335 " * WRITE -- schedules all dirty buffers containing user data."

### G37
- guarantee: elbb_QuiesceSystem with FLUSHALL also invalidates all buffers.
  source: logbuf/logbuf.p.h:338 " * FLUSHALL -- also invalidates all buffers (elbb_Shutdown)."
- guarantee: elbb_QuiesceSystem with WRITE schedules all dirty user-data buffers; with FSYNC it also waits for those writes; with FLUSH it also invalidates user buffers; with FLUSHALL it invalidates all buffers.
  source: logbuf/logbuf.p.h:335 " * WRITE -- schedules all dirty buffers containing user data."

### G38
- guarantee: Quiescing allows concurrent activity after the captured log position rather than requiring the whole system to stop.
  source: logbuf/tran.c:1220 " * when the caller (elbb_QuiesceSystem) started. Other activity is allowed * to continue concurrently."
- guarantee: Quiesce without stopping the system waits only for transactions older than the log position sampled at the start of the call, so later activity may continue concurrently.
  source: logbuf/tran.c:1217 " * Quiescing without stopping the system works by waiting for all currently"

### G39
- guarantee: elbl_Close waits for active transactions to complete and writes a restart block.
  source: logbuf/log.c:1482 " * This routine is inclusive of elbl_Shutdown; it however always blocks * pending the completion of any active transactions. It then writes a"
- guarantee: A clean shutdown writes a checkpoint block and then a restart block, and does not return until pending transactions on that device are complete.
  source: logbuf/buffer.c:2581 " * Close the log; this waits until all pending transactions are complete."

### G40
- guarantee: elbb_FsyncForce writes and waits for dirty cached buffers selected by file-handle tag or block array.
  source: logbuf/buffer.c:2138 " code = asevent_WaitAll(aset);"
- guarantee: elbb_FsyncForce writes the tagged or listed buffers, forcing the log as needed for any logged buffer among them.
  source: logbuf/buffer.c:2018 " * elbb_FsyncForce -- implements fsync using two basic methods of specifying"

### G41
- guarantee: Ordinary elbb_SyncForce schedules dirty buffers that are neither being updated nor already being written, without waiting for pending writes.
  source: logbuf/buffer.c:2166 " * For sync, we do not want to wait. We walk through the entire hash * pool, skipping buffers being updated (they're busy), and scheduling"
- guarantee: elbb_SyncForce schedules writes of dirty buffers and does not wait for those writes to complete.
  source: logbuf/buffer.c:2166 " * For sync, we do not want to wait. We walk through the entire hash"

### G42
- guarantee: elbb_ModifySource logs the buffer modification when the transaction ID is valid and logging is requested.
  source: logbuf/buffer.c:1410 " * this routine changes the contents of a buffer and logs that change * if the tranId is not the invalid transaction id and the logRequest"
- guarantee: A logged modification writes the log record and then copies the new data into the buffer, leaving the buffer dirty.
  source: logbuf/buffer.c:1455 " if (logRequest) {"

### G43
- guarantee: elbb_Initialize logs initialization without logging the previous contents.
  source: logbuf/buffer.c:1588 " * By initialization, we mean modification in the case where the old data * do not have to be logged, i.e. the buffer was created by CreateBlock."
- guarantee: elbb_Initialize logs only the new contents of a CreateBlock buffer (no old data).
  source: logbuf/buffer.c:1588 " * By initialization, we mean modification in the case where the old data"

### G44
- guarantee: elbb_Kill refuses to delete a dirty logged buffer when metadataOK is false.
  source: logbuf/buffer.c:1364 " * RETURN CODES -- returns zero if all went well, and CANTDELETE if metadataOK * was false and the buffer was LOGGED and DIRTY. */"
- guarantee: elbb_Kill will not discard a dirty logged buffer unless metadataOK is true, which is allowed only after the transaction that freed that meta-data block has committed.
  source: logbuf/buffer.c:1359 " * metadataOK is true if it is safe to kill dirty metadata"

### G45
- guarantee: elbb_UndoZero records undo-zero coverage for the requested byte range in an existing transaction, including I/O outside the buffer system.
  source: logbuf/buffer.c:2414 " * elbb_UndoZero - Adds an undo-zero record to an existing transaction for * the specified range of bytes. This is to be used by the VM system for I/Os"
- guarantee: elbb_UndoZero appends old-fill-of-zero records to an existing transaction for a byte range, covering I/O that does not use the buffer system.
  source: logbuf/buffer.c:2414 " * elbb_UndoZero - Adds an undo-zero record to an existing transaction for"

### G46
- guarantee: elbb_UndoZeroBuffer creates and attaches a transaction if the buffer has no undo-zero transaction already.
  source: logbuf/buffer.c:2457 " * elbb_UndoZeroBuffer -- Adds an undo-zero record for the specified buffer. A * transaction is started and attached to the buffer if one is not already"
- guarantee: elbb_UndoZeroBuffer starts a nested transaction, attaches it to the dirty buffer, logs an old-fill-of-zero, and that transaction is ended when the buffer is no longer dirty.
  source: logbuf/buffer.c:2457 " * elbb_UndoZeroBuffer -- Adds an undo-zero record for the specified buffer. A"

### G47
- guarantee: Recovery redoes a transaction with an end record even when its begin record is outside the active log.
  source: logbuf/recover.c:1787 " * (no start, has end) - REDO"
- guarantee: User-space recovery marks a transaction REDO if an end record is seen (whether or not a begin is seen) and UNDO if a begin is seen and no end is seen.
  source: logbuf/recover.h:80 " * Begin seen REDO UNDO"

### G48
- guarantee: Recovery rejects transaction records with neither a start nor an end record.
  source: logbuf/recover.c:1781 " * The last state (no start, no end) is invalid - we should NEVER * see such a log. The other three are valid. Their corresponding"
- guarantee: User-space recovery fails if it finds a transaction that has neither a begin nor an end in the active log.
  source: logbuf/recover.h:81 " * Begin not seen REDO <fail>"

### G49
- guarantee: Recovery recognizes member end records from batch-end records only when the containing transaction committed.
  source: logbuf/recover.c:1690 " * with BEND records we search to see if the transaction committed. If it * did, we take the data section of each BEND record (which is really an"
- guarantee: Equivalence-class ends are written atomically: the head transaction writes a BEND record for each member and then its own END, and recovery reconstitutes those member END records only if the head transaction is REDO.
  source: logbuf/recover.c:1687 " * Bulk ends are the recovery end of ECs. Because the end records must"

### G50
- guarantee: For each recovered data block, recovery performs undo operations before redo operations.
  source: logbuf/recover.c:1970 " * To actually perform the recovery we must make two passes. * Pass # 1 is where all undo operations are done; pass # 2"
- guarantee: For each data block, recovery applies undo records newest-first, then redo records oldest-first, then writes the block back only if it actually read it.
  source: logbuf/recover.c:1970 " * To actually perform the recovery we must make two passes."

### G51
- guarantee: Recovery skips obsolete updates preceding an undo-zero kill record for a reused block.
  source: logbuf/recover.c:1875 " * NBS. These must be interpreted as kill records for earlier updates to * the same block. Set the status of all such updates to SKIP. */"
- guarantee: A committed undo-zero fill of zeroes is a kill record: recovery marks every earlier recoverable record on that same disk block SKIP, and those earlier records must have been REDO.
  source: logbuf/recover.h:83 " * Records (not whole transactions) are marked SKIP if they predate a kill"

### G52
- guarantee: Recovery fails with RCVR_USERDATA if an uncommitted kill precedes newer metadata records on the same block.
  source: logbuf/recover.c:1906 " if ((rec->status == RECVR_STATUS_UNDO) && someRecs) RECVR_RAISE (RCVR_USERDATA);"
- guarantee: Recovery raises RCVR_USERDATA if it sees an uncommitted kill after ordinary records on the same block.
  source: logbuf/recover.c:1907 " RECVR_RAISE (RCVR_USERDATA);"

### G53
- guarantee: Recovery fails with RCVR_METADATA if an uncommitted metadata update precedes a kill record on the same block.
  source: logbuf/recover.c:1914 " if (rec->status == RECVR_STATUS_UNDO) RECVR_RAISE (RCVR_METADATA);"
- guarantee: Recovery raises RCVR_METADATA if it sees an uncommitted recoverable record that a later kill would have skipped.
  source: logbuf/recover.c:1915 " RECVR_RAISE (RCVR_METADATA);"

### G54
- guarantee: Recovery checks page pass numbers as well as checksums to reject older log pages left on disk.
  source: logbuf/recover.c:929 " * to be checked as the log page could be a much older logpage * with a correct checksum but an old passnumber."
- guarantee: The log page header, including checksum, occupies the first sector, and recovery relies on sector atomicity: a page that was not written keeps an earlier pass number and is ignored as head.
  source: logbuf/recover.c:745 " * sector for the log page and we can rely on"

### G55
- guarantee: Successful recovery writes a clean restart record after applying disk changes.
  source: logbuf/recover.c:507 " /* Step 5: recovery is complete. Write out a clean restart record. */"
- guarantee: After successful user-space recovery, a checkpoint record is written on the next log page and a restart record is written on the first log block with the pass number increased by two.
  source: logbuf/recover.c:543 " * we increase the pass # to allow for an Episode crash immediately"
- guarantee: After successful recovery the log is clean.
  source: anode/aggregate.c:2405 " /* By definition the log is now clean. */"

### G56
- guarantee: elbr_GetCleanLogInfo returns zero for a log needing recovery and one for a clean log.
  source: logbuf/recover.c:2760 " * returns 0 if not clean (needs recovery), 1 if clean."
- guarantee: A log is clean, and recovery is not required, if and only if the first log block's page header has the salvage magic number and its first record is a restart record.
  source: logbuf/recover.c:2760 " * returns 0 if not clean (needs recovery), 1 if clean."

### G57
- guarantee: In kernel mode, elbr_Recover returns RCVR_MUSTRCVR instead of performing recovery.
  source: logbuf/recover.c:2374 " return RCVR_MUSTRCVR; /* no kernel recovery anymore */"
- guarantee: In the kernel, elbr_Recover does not recover a dirty log; it returns RCVR_MUSTRCVR.
  source: logbuf/recover.c:2374 "return RCVR_MUSTRCVR; /* no kernel recovery anymore */"

### G58
- guarantee: Log initialization detects a missing clean restart record and attempts recovery instead of starting ordinary logging.
  source: logbuf/log.c:730 " * disk. If so, we continue. If not, we attempt recovery and * return the resulting error value (never OK) to the caller."
- guarantee: Log initialization refuses to attach a dirty log until recovery has run: if the restart block is not clean it calls recovery and, on success, returns RCVR_RECOVERED.
  source: logbuf/log.c:733 " if (elbr_GetCleanLogInfo(ldP, *logLocnArray, &myLogHdr) == 0) {"

### G59
- guarantee: Successful recovery during log initialization is reported as RCVR_RECOVERED rather than ordinary success.
  source: logbuf/log.c:737 " return RCVR_RECOVERED; /* so upper levels can clear buffers */"
- guarantee: Log initialization refuses to attach a dirty log until recovery has run: if the restart block is not clean it calls recovery and, on success, returns RCVR_RECOVERED.
  source: logbuf/log.c:733 " if (elbr_GetCleanLogInfo(ldP, *logLocnArray, &myLogHdr) == 0) {"

### G60
- guarantee: elbb_LogInit invalidates cached buffers after successful recovery.
  source: logbuf/buffer.c:1837 " /* log recovered, we invalidate the buffer pool by * calling shutdown. Note that we assume none of the"
- guarantee: After recovery returns RCVR_RECOVERED, the buffer pool for that device is invalidated.
  source: logbuf/buffer.c:1837 " /* log recovered, we invalidate the buffer pool by"

### G61
- guarantee: For each recovered block, undo applies records from newest to oldest.
  source: logbuf/recover.c:1992 " for (rec2P = FIFO_LookAtNewest(&(recP)->diskFifo, DISKTHREAD);"
- guarantee: For each data block, recovery applies undo records newest-first, then redo records oldest-first, then writes the block back only if it actually read it.
  source: logbuf/recover.c:1970 " * To actually perform the recovery we must make two passes."

### G62
- guarantee: For each recovered block, redo applies records from oldest to newest.
  source: logbuf/recover.c:2020 " rec2P = FIFO_NextOldest(&(recP)->diskFifo, rec2P,"
- guarantee: For each data block, recovery applies undo records newest-first, then redo records oldest-first, then writes the block back only if it actually read it.
  source: logbuf/recover.c:1970 " * To actually perform the recovery we must make two passes."

### G63
- guarantee: Log creation zero-initializes every log block except the first, which receives a restart record.
  source: logbuf/log.c:904 " * We skip the first block because we will be writing a restart * record into it. All other blocks are initialized to zero."
- guarantee: Create of a new log zeroes every page but the first and writes a restart record on the first log block.
  source: logbuf/log.c:904 " * We skip the first block because we will be writing a restart"


## The sealed analysis (v2, sealed 2026-10-27T18:15:54Z, before any finding existed)

# SEALED for tupay D2, version 2. Do not read unless you are judging the comparison.

Written by episode's steward (Claude Opus 5.5) on 2026-10-27, answering tupay's follow-up
(`docs/requests/2026-10-26-from-tupay-D2-followup.md`), before D2 phase 0.
**This file supersedes `sealed/2026-10-26-tupay-D2-findings.md` for judging.**
v1 stays in the history unchanged. v2 changes no bug. It adds, for each one, an
explicit effect class and a classification against D2's definition of an
environment contract (`tupay/experiments/D2/brief-enumerate.md`, Task: "an
obligation on something `logbuf` depends on ... **not** a rule of `logbuf`
itself"). It also makes the mechanism a field of its own. Where v1's wording
was loose, v2 says so.

Code: `/home/tony/projects/dce/dce/src/file/episode/logbuf` (DCE 1.2.2).
Models: `spec/` (see `spec/README.md`).

Effect classes: **silent-loss** (committed or acknowledged data gone, no error);
**silent-atomicity** (a partial or uncommitted change survives recovery, no
error); **silent-splice** (recovery accepts log pages from two runs as one log);
**exposure** (another owner's data becomes visible in a file); **fail-stop**
(recovery refuses or salvages; no wrong state is accepted).

Environment column: **env** = the bug is a violation of an obligation on something
outside `logbuf`; **own** = a defect in `logbuf`'s own rules, where the environment
behaves within what it promises.

| id | contract or assumption | mechanism | effect class | env / own | in a source comment |
|---|---|---|---|---|---|
| E1 | none violated. The I/O layer may complete log page writes out of order, and the code says it doesn't assume order | `log.c:2990` stores `io_window` as the *count* of pages in transit; recovery (SafeDumpLog) uses it as the *distance* back from the head to check. An older page still in transit after newer ones complete lies outside the count, so a missing page falls inside the scanned range | fail-stop (spurious `RCVR_IOERR`, salvager) | own | no |
| E2 | disk: a completed write is durable | the log treats a completed page write as stable; on a volatile write cache the page can be lost at power failure after commit is acknowledged | silent-loss (acknowledged commit) | env | yes (`recover.c:894`, wam 920624) |
| E3 | disk: a completed write is durable (includes: a write that completes *during* a flush is not covered by that flush) | a stolen uncommitted metadata page reaches media while its undo record, though "complete", is still only in cache; crash; recovery has no undo for it | silent-atomicity | env | yes (`recover.c:894`) |
| E4 | disk: a completed write was actually stored (no lost writes) | a lost metadata page write is masked by old/new redo until checkpoint truncation discards the redo record; metadata pages carry no parent-held version, so the stale page is never detected | silent-loss (committed update) | env | no |
| E5 | disk: a completed write is durable (here: the user data write covered by undo-zero) | OFILL correctly precedes the allocation's END; Z's END becomes durable while the user data sits in a volatile cache; crash; recovery keeps the allocation, does not undo-zero, and the block shows its old contents | exposure | env | yes (ordering at `log.c:1680`, wam 920805; device assumption at `recover.c:894`; the exposure is not stated) |
| E6 | none violated. Out-of-order completion is permitted (as E1), and a crash is an expected event | the clean-mount path starts pass R+1 at slot 0 without persisting it; after crash, out-of-order landing and a second clean mount, two runs' pages share a pass number and a valid checksum | silent-splice | own | partly (`recover.c:545` "+2 ... paranoia" anticipates it on the recovery path only) |
| E7 | none below `logbuf`; an internal invariant: every page on media is within half the pass range of the head | restarting at slot 0 on every mount leaves far slots unrewritten while the pass counter advances; the masked comparison in the head search can then read an old page as newer | fail-stop in the model (3-bit field: salvage). At 16 bits, argued only: the head is misidentified, and whether the result is fail-stop or silent is **not established** | own | no |

Counts: 7 bugs. env 4 (E2, E3, E4, E5); own 3 (E1, E6, E7).
Comment: 4 (E2, E3, E5, E6), of which env 3 (E2, E3, E5) and own 1 (E6).
All 7 carry contract-or-assumption, mechanism and effect class. E7's effect class is
given with its uncertainty, which matching must respect: for E7, either a fail-stop
or a silent wrong-head effect counts as the same effect class.

Corrections to v1's wording, not to substance:
- v1 gave E1 and E6 a "contract violated" of in-order completion. Under D2's
  definition that is wrong: the environment doesn't promise in-order completion,
  and `logbuf` doesn't rely on it by contract. The bugs are `logbuf`'s own.
- v1's E3 effect was descriptive; v2 classes it silent-atomicity.

Unchanged from v1 and not repeated here: the confirmed design properties P1–P6, the
open item O1, the out-of-scope list, and the visible-in-history column (0 of 7).


===== mapping from opaque id to author (excerpt: author, label, scored, author_status; rows: kind, enumerator) =====
{
 "findings": {
  "F01": {
   "author": "model-n-claude",
   "label": "model-n-claude#3",
   "scored": true,
   "author_status": null
  },
  "F02": {
   "author": "model-c-grok",
   "label": "model-c-grok#4",
   "scored": true,
   "author_status": null
  },
  "F03": {
   "author": "model-n-claude",
   "label": "model-n-claude#1",
   "scored": true,
   "author_status": null
  },
  "F04": {
   "author": "model-c-grok",
   "label": "model-c-grok#2",
   "scored": true,
   "author_status": null
  },
  "F05": {
   "author": "model-c-claude",
   "label": "model-c-claude#1",
   "scored": true,
   "author_status": "draft"
  },
  "F06": {
   "author": "model-c-grok",
   "label": "model-c-grok#5",
   "scored": true,
   "author_status": null
  },
  "F07": {
   "author": "model-n-claude",
   "label": "model-n-claude#2",
   "scored": true,
   "author_status": null
  },
  "F08": {
   "author": "model-c-grok",
   "label": "model-c-grok#3",
   "scored": true,
   "author_status": null
  },
  "F09": {
   "author": "model-c-grok",
   "label": "model-c-grok#1",
   "scored": true,
   "author_status": null
  },
  "F10": {
   "author": "model-c-claude",
   "label": "model-c-claude#2",
   "scored": true,
   "author_status": "draft"
  }
 },
 "rows": {
  "R01": {
   "kind": "recognised",
   "enumerator": "grok-1",
   "section": "Recognised"
  },
  "R02": {
   "kind": "report",
   "enumerator": "codex-2",
   "section": "Checkout inventory and status"
  },
  "R03": {
   "kind": "report",
   "enumerator": "grok-1",
   "section": "Report"
  },
  "R04": {
   "kind": "recognised",
   "enumerator": "grok-2",
   "section": "Recognised"
  },
  "R05": {
   "kind": "recognised",
   "enumerator": "grok-1",
   "section": "Recognised"
  },
  "R06": {
   "kind": "recognised",
   "enumerator": "grok-2",
   "section": "Recognised"
  },
  "R07": {
   "kind": "report",
   "enumerator": "codex-1",
   "section": "Inventory"
  },
  "R08": {
   "kind": "recognised",
   "enumerator": "grok-1",
   "section": "Recognised"
  },
  "R09": {
   "kind": "report",
   "enumerator": "grok-1",
   "section": "Report"
  },
  "R10": {
   "kind": "report",
   "enumerator": "grok-2",
   "section": "Report"
  },
  "R11": {
   "kind": "report",
   "enumerator": "grok-2",
   "section": "Report"
  },
  "R12": {
   "kind": "report",
   "enumerator": "grok-2",
   "section": "Report"
  },
  "R13": {
   "kind": "recognised",
   "enumerator": "grok-1",
   "section": "Recognised"
  },
  "R14": {
   "kind": "report",
   "enumerator": "codex-2",
   "section": "Checkout inventory and status"
  },
  "R15": {
   "kind": "report",
   "enumerator": "grok-1",
   "section": "Report"
  },
  "R16": {
   "kind": "report",
   "enumerator": "grok-2",
   "section": "Report"
  },
  "R17": {
   "kind": "report",
   "enumerator": "codex-1",
   "section": "Limitations and undecided points"
  },
  "R18": {
   "kind": "report",
   "enumerator": "grok-1",
   "section": "Report"
  },
  "R19": {
   "kind": "report",
   "enumerator": "grok-2",
   "section": "Report"
  },
  "R20": {
   "kind": "report",
   "enumerator": "codex-2",
   "section": "Limits and undecided points"
  },
  "R21": {
   "kind": "report",
   "enumerator": "grok-2",
   "section": "Report"
  },
  "R22": {
   "kind": "report",
   "enumerator": "grok-2",
   "section": "Report"
  },
  "R23": {
   "kind": "report",
   "enumerator": "grok-2",
   "section": "Report"
  },
  "R24": {
   "kind": "report",
   "enumerator": "grok-1",
   "section": "Report"
  },
  "R25": {
   "kind": "report",
   "enumerator": "grok-2",
   "section": "Report"
  },
  "R26": {
   "kind": "report",
   "enumerator": "codex-2",
   "section": "Checkout inventory and status"
  },
  "R27": {
   "kind": "report",
   "enumerator": "grok-2",
   "section": "Report"
  },
  "R28": {
   "kind": "report",
   "enumerator": "codex-2",
   "section": "Limits and undecided points"
  },
  "R29": {
   "kind": "report",
   "enumerator": "grok-2",
   "section": "Report"
  },
  "R30": {
   "kind": "report",
   "enumerator": "grok-1",
   "section": "Report"
  },
  "R31": {
   "kind": "report",
   "enumerator": "codex-2",
   "section": "Checkout inventory and status"
  },
  "R32": {
   "kind": "report",
   "enumerator": "codex-2",
   "section": "Limits and undecided points"
  },
  "R33": {
   "kind": "recognised",
   "enumerator": "codex-1",
   "section": "Recognised"
  },
  "R34": {
   "kind": "report",
   "enumerator": "grok-2",
   "section": "Report"
  },
  "R35": {
   "kind": "report",
   "enumerator": "codex-2",
   "section": "Checkout inventory and status"
  },
  "R36": {
   "kind": "report",
   "enumerator": "codex-1",
   "section": "Inventory"
  },
  "R37": {
   "kind": "report",
   "enumerator": "grok-2",
   "section": "Report"
  },
  "R38": {
   "kind": "report",
   "enumerator": "grok-2",
   "section": "Report"
  },
  "R39": {
   "kind": "recognised",
   "enumerator": "grok-1",
   "section": "Recognised"
  },
  "R40": {
   "kind": "report",
   "enumerator": "codex-1",
   "section": "Inventory"
  },
  "R41": {
   "kind": "report",
   "enumerator": "codex-2",
   "section": "Limits and undecided points"
  },
  "R42": {
   "kind": "report",
   "enumerator": "grok-1",
   "section": "Report"
  },
  "R43": {
   "kind": "recognised",
   "enumerator": "grok-1",
   "section": "Recognised"
  },
  "R44": {
   "kind": "report",
   "enumerator": "codex-1",
   "section": "Inventory"
  },
  "R45": {
   "kind": "report",
   "enumerator": "grok-1",
   "section": "Report"
  },
  "R46": {
   "kind": "report",
   "enumerator": "codex-1",
   "section": "Limitations and undecided points"
  },
  "R47": {
   "kind": "report",
   "enumerator": "grok-2",
   "section": "Report"
  },
  "R48": {
   "kind": "report",
   "enumerator": "codex-1",
   "section": "Inventory"
  },
  "R49": {
   "kind": "report",
   "enumerator": "grok-2",
   "section": "Report"
  },
  "R50": {
   "kind": "report",
   "enumerator": "grok-2",
   "section": "Report"
  },
  "R51": {
   "kind": "report",
   "enumerator": "grok-1",
   "section": "Report"
  },
  "R52": {
   "kind": "report",
   "enumerator": "grok-2",
   "section": "Report"
  },
  "R53": {
   "kind": "report",
   "enumerator": "codex-1",
   "section": "Inventory"
  },
  "R54": {
   "kind": "recognised",
   "enumerator": "codex-2",
   "section": "Recognised"
  },
  "R55": {
   "kind": "report",
   "enumerator": "codex-2",
   "section": "Checkout inventory and status"
  },
  "R56": {
   "kind": "recognised",
   "enumerator": "grok-2",
   "section": "Recognised"
  },
  "R57": {
   "kind": "report",
   "enumerator": "codex-1",
   "section": "Inventory"
  },
  "R58": {
   "kind": "report",
   "enumerator": "codex-1",
   "section": "Limitations and undecided points"
  },
  "R59": {
   "kind": "report",
   "enumerator": "grok-2",
   "section": "Report"
  },
  "R60": {
   "kind": "recognised",
   "enumerator": "grok-1",
   "section": "Recognised"
  }
 }
}

===== Episode ruling: findings (findings.json) =====
{
 "findings": [
  {
   "id": "F01",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "Shares only the effect class with E2 (silent loss of an acknowledged commit). Its contract (a log write outstanding for a full lap) and its mechanism (EarlierPassno aliasing in TranCommitted/BufCommitted when activeLogBlock equals currentLogBlock) are not in the sealed file, and E1's count-versus-distance defect is a different line of recovery code. This looks like a plausible own-rule defect the sealed analysis missed; it deserves verification."
  },
  {
   "id": "F02",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "Unknown checksum version forcing success (recover.c:2577) is not among E1-E7. It does not contradict P5, which concerns torn home-page writes under physical redo, not torn log pages accepted by a disabled check. Plausibly real from the cited source line; not in the sealed analysis."
  },
  {
   "id": "F03",
   "ruling": "match",
   "bugs": [
    "E6"
   ],
   "flag_confirmed_property": null,
   "reason": "Same trigger as E6 (out-of-order completion among the first pages after a clean mount, then crashes), same mechanism (elbr_GetCleanLogInfo sees page 0's restart record, the log reopens with IncPassno(restart pass), and two incarnations share a pass number), and same class of effect: silent-splice, with stale records joining the active log. The finding calls the trigger an environment violation, while v2 classes E6 as logbuf's own defect because the source permits out-of-order writes; the finding quotes that permission itself, so this is a labelling difference, not a different contract. Its tran-id restart detail (MarkCommitted by tran id alone) extends the sealed mechanism and is consistent with it."
  },
  {
   "id": "F04",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "A caller passing metadataOK=true to elbb_Kill before the freeing transaction commits is a caller-contract defect not among E1-E7. The scenario depends on the model replacing the active log at the kill, which the finding itself presents as an abstraction of checkpointing; how faithful that is was not established in the sealed analysis either way."
  },
  {
   "id": "F05",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "An overwrite of an acknowledged head log page being taken as an incomplete write is not in E1-E7. E4 shares the effect class (silent loss) but has a different contract (a lost write at write time) and mechanism (masking until checkpoint truncation). The ambiguity it exploits, that a damaged newest page is indistinguishable from an interrupted write, is the same trade-off the sealed analysis named for jbd2 (out of scope) but did not list for Episode; a fair omission to charge to the analysis."
  },
  {
   "id": "F06",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "A stale read of the log head (C018) is a different contract from E4's lost write and a different mechanism (END not seen, so the committed transaction is undone), though the effect class, silent loss, is shared. The sealed EpisodeLog model treats pages as sealed once (no tail rewrite); if Episode rewrites a partly filled head page, this scenario lies outside that model's reach. That is an abstraction gap in the analysis worth a second look, not a match."
  },
  {
   "id": "F07",
   "ruling": "partial",
   "bugs": [
    "E6"
   ],
   "flag_confirmed_property": null,
   "reason": "Same contract as E6 (permitted out-of-order completion plus crashes, nothing below logbuf violated) and same class of effect (stale pages of a crashed incarnation accepted into the log, splicing histories), but a different mechanism: the recovery path's checkpoint block written into the hole with the old pass before the +2 restart block. This disagrees with the sealed E6 note that the +2 bump covers the recovery path; WrapLog modelled that path and did not report it, so either the sealed model's bounds missed it or the finding is wrong. Second look required."
  },
  {
   "id": "F08",
   "ruling": "partial",
   "bugs": [
    "E3"
   ],
   "flag_confirmed_property": null,
   "reason": "The right mechanism of E3 (a home metadata write reaches media while the log record that would undo it does not, so an uncommitted value survives: silent-atomicity) under a different contract: AIX ESOFT success for an unstored log write, which is E4's contract (a completed write is stored), not E3's (a completed write is durable). E4 itself does not match: only its contract is shared."
  },
  {
   "id": "F09",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "A forged or corrupted restart page, which recovery deliberately does not checksum (recover.c:2738), is not among E1-E7. Plausible from the source; not in the sealed analysis."
  },
  {
   "id": "F10",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "Same shape as F05, under media decay (C071) instead of an overwrite. E4's contract is a lost write at write time, not later decay, and its mechanism differs; only the effect class (silent loss) is shared."
  }
 ]
}


===== Gemini ruling: findings (ruling.json) =====
{
 "findings": [
  {
   "id": "F01",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "F01 relies on out-of-order log write completion (like E1 and E6) where page 0 remains in transit for a full lap of the log so `EarlierPassno(activeLogBlock)` wraps in `TranCommitted`/`BufCommitted`, causing `elbl_ForceTran` to return early and losing an acknowledged commit (`silent-loss`, like E2). None of the sealed bugs has this full-lap `activeLogBlock` wrap mechanism in runtime commit checks: E1 is the `io_window` count-versus-distance bug in `SafeDumpLog` (`fail-stop`), E6 is clean-mount pass reuse (`silent-splice`), and E2 is loss of a completed write from a volatile cache."
  },
  {
   "id": "F02",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "F02 violates C021 when a torn log page carries `UNKNOWN_CKSUM_TYPE`, causing `ValidLogPageChecksum` (recover.c:2577) to force checksum success and replay uncommitted data. None of E1\u2013E7 involves checksum version configuration, `UNKNOWN_CKSUM_TYPE`, or fail-open checksum validation on torn pages."
  },
  {
   "id": "F03",
   "ruling": "match",
   "bugs": [
    "E6"
   ],
   "flag_confirmed_property": null,
   "reason": "F03 matches E6 in assumption, mechanism, and effect class. Both start from permitted out-of-order log page completion and a crash before page 0 overwrites the restart block, so `elbr_GetCleanLogInfo` sees a clean log and reopens with `IncPassno(restart pass)` (pass R+1) without recovery; after a second crash, stale and new pages share the same pass number and valid checksums, splicing records across incarnations (`silent-splice`)."
  },
  {
   "id": "F04",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "F04 violates C024 by calling `elbb_Kill` with `metadataOK` set to true on a dirty logged buffer, dropping the buffer from the age queue so checkpointing advances past a committed update that never reached its home block. Although the effect is `silent-loss` of a committed update (like E4), E4 is caused by a lost disk write to a metadata home block rather than caller misuse of `elbb_Kill`."
  },
  {
   "id": "F05",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "F05 violates C088 when an external overwrite corrupts a completed head log page and `SafeDumpLog`'s in-transit window scan (recover.c:940-975) treats the bad checksum as an incomplete write, pulling the head back and losing a committed transaction (`silent-loss`). While it shares the `silent-loss` effect class of E2, neither the violated contract (C088 log container exclusivity/fixed mapping) nor the mechanism (checksum failure masked by the `io_window` pullback) matches E1\u2013E7."
  },
  {
   "id": "F06",
   "ruling": "match",
   "bugs": [
    "E2"
   ],
   "flag_confirmed_property": null,
   "reason": "F06 violates C018 when the storage stack fails to return the last completed write at the log head and instead returns the previous well-formed page lacking the transaction's END record, so recovery undoes a committed transaction (`silent-loss`). This matches E2's contract (completed log writes are durable/visible after completion), mechanism (the log treats a completed page write as stable on disk, and when the newly completed head page is missing at recovery, the committed transaction is lost), and effect class (`silent-loss`)."
  },
  {
   "id": "F07",
   "ruling": "partial",
   "bugs": [
    "E6"
   ],
   "flag_confirmed_property": null,
   "reason": "Like E1 and E6, F07 assumes only permitted out-of-order log page completion (leaving a hole at page 1 before a completed page 2) plus crashes, and like E6 it produces a `silent-splice` / `silent-atomicity` effect where stale page 2 from before the first crash is joined into the active log after a second crash. However, its mechanism bridges the hole via `elbr_WriteCheckpointBlock` writing head+1 with the same pass number before `elbr_WriteRestartBlock` completes, rather than E6's clean-mount `IncPassno` reuse."
  },
  {
   "id": "F08",
   "ruling": "match",
   "bugs": [
    "E3"
   ],
   "flag_confirmed_property": null,
   "reason": "F08 violates C041 when AIX `asevent_Iodone` clears `ESOFT` on a log write that was not stored, reporting the log force complete so write-ahead allows the dirty uncommitted metadata home block to be written to disk before a crash. This matches E3 (and shares E4's false-completion contract): a 'completed' undo log write is not actually durable on media while the uncommitted metadata home page reaches disk, leaving recovery with no undo record (`silent-atomicity`)."
  },
  {
   "id": "F09",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "F09 violates C058 by planting or restoring an unchecksummed restart image on the first log block after an uncommitted metadata home block write, causing `elbr_GetCleanLogInfo` to treat the dirty log as clean and skip recovery. None of E1\u2013E7 involves forged or unchecksummed restart markers suppressing recovery."
  },
  {
   "id": "F10",
   "ruling": "partial",
   "bugs": [
    "E2"
   ],
   "flag_confirmed_property": null,
   "reason": "F10 violates C071 (the storage stack must preserve completed writes) when bits of a completed head log page decay, and shares E2's `silent-loss` effect on an acknowledged commit. It is a partial match for E2 because it shares the violated durability contract and effect class, but its mechanism relies on bit rot triggering a bad checksum inside `SafeDumpLog`'s in-transit window pullback rather than a volatile write cache losing a whole page at power failure."
  }
 ]
}

===== GLM ruling (beside): findings (ruling.json) =====
{
 "findings": [
  {
   "id": "F01",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "The contract situation matches E1/E6 (no environment contract violated; out-of-order completion is permitted), but the mechanism is different: E1 is the io_window count-vs-distance confusion in SafeDumpLog, while F01 is the EarlierPassno/page-index wrap in TranCommitted letting a forced commit return early. The effect also differs: E1 is fail-stop (spurious RCVR_IOERR), F01 is silent-loss of an acknowledged commit. Neither partial condition (shared contract plus mechanism or effect) is met."
  },
  {
   "id": "F02",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "F02 is a configuration/contract violation (unknown checksum version forces the check open, C021) with a torn-page replay. No sealed bug concerns checksum configuration or fail-open validation; E4 is a lost metadata write masked by redo, a different contract and mechanism. Effect (silent wrong value) alone is insufficient for even a partial ruling."
  },
  {
   "id": "F03",
   "ruling": "match",
   "bugs": [
    "E6"
   ],
   "flag_confirmed_property": null,
   "reason": "This is E6: the clean-mount path reopens with a pass number (IncPassno of the restart pass) that collides with the crashed incarnation's pass because no recovery ran between them, so out-of-order landing of the first pages lets stale pages from two runs share a pass number and valid checksums and join the active log. Same contract (none violated, logbuf's own), same mechanism (pass collision after a clean mount without persisted pass), same effect class (silent-splice: stale records spliced in, uncommitted update redone)."
  },
  {
   "id": "F04",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "F04 is a caller-contract violation (metadataOK passed true before the freeing transaction commits, C024) causing loss of a committed update via checkpoint truncation. The sealed file has no bug about elbb_Kill or the metadataOK contract; E4 is a disk lost-write bug with a different contract and mechanism. No overlap sufficient for partial."
  },
  {
   "id": "F05",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "The cited contract C088 (log container fixed) does not match the actual mechanism described (a completed head page decayed or overwritten, with the in-transit window rule converting detected damage into 'not yet written'). No sealed bug has this mechanism: E1's io_window confusion yields fail-stop, not silent truncation of the head, and E2/E4 concern durability of completed writes, not later decay. Effect class (silent-loss) alone does not reach partial."
  },
  {
   "id": "F06",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "F06 is an environment contract violation (stale read of a completed write, C018) where an older well-formed page passes checksum and pass checks and is taken as head. E7 also involves head misidentification, but its contract is 'none violated / own' and its mechanism is the masked pass-range comparison after far slots go unrewritten, not a device returning stale data. Contract differs and mechanism differs; the shared effect (wrong head) is not enough for partial under the stated criteria."
  },
  {
   "id": "F07",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "F07's mechanism is the checkpoint block written into the hole at head+1 with a valid pass and checksum, letting a later binary search bridge the hole and partially redo a transaction the first recovery aborted. E1 concerns the io_window count/distance mismatch and is fail-stop; E6 concerns pass collision on clean mounts. Neither shares the contract or the mechanism, and the effect (silent reversal of a prior recovery decision) matches neither sealed effect class."
  },
  {
   "id": "F08",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "F08's contract is the AIX async layer clearing ESOFT before the log inspects it (C041), an environment obligation not present in the sealed list. E3 is the closest in effect class (silent-atomicity: uncommitted value on media with no undo), but its contract is disk durability and its mechanism is buffer steal before the undo record is durable, not a masked I/O error. Contract and mechanism both differ, so no partial."
  },
  {
   "id": "F09",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "F09 concerns authenticity of the unchecksummed restart record (C058): a forged or restored clean marker suppresses recovery. No sealed bug addresses the clean-log test or restart-record authenticity; E6 involves a genuinely clean mount and pass collision, a different contract and mechanism. The silent-atomicity effect alone is insufficient."
  },
  {
   "id": "F10",
   "ruling": "no match",
   "bugs": [],
   "flag_confirmed_property": null,
   "reason": "F10 is bit decay of a completed head page where the in-transit window scan treats a bad checksum as an incomplete write and silently pulls the head back, dropping acknowledged commits. No sealed bug has this mechanism: E1's io_window defect produces a spurious error (fail-stop), not silent truncation, and E2/E4 concern lost or volatile writes rather than post-completion decay. Effect class alone does not yield a partial."
  }
 ]
}

===== Episode ruling: cells-1 (cells-1.json) =====
{
 "cells": [
  {
   "id": "C001",
   "names_contract_of": [
    "E4"
   ],
   "reason": "Its obligation that the device 'must not return success for a page that was not stored' is E4's contract (a completed write was actually stored), with 'a write it dropped' as the violation."
  },
  {
   "id": "C002",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C003",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C004",
   "names_contract_of": [],
   "reason": "Equivalence-class merging obligations relate to confirmed property P3, not to a sealed bug; no."
  },
  {
   "id": "C005",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C006",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C007",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C008",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C009",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C010",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C011",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C012",
   "names_contract_of": [],
   "reason": "The forced nested undo-zero reservation is the unmodelled `force` bypass noted under P4, not a sealed bug; no."
  },
  {
   "id": "C013",
   "names_contract_of": [],
   "reason": "Names the caller's obligation to end undo-zero only after the first write completes; E5's violated contract is the device's (completion implies durability), which this cell does not state, so no."
  },
  {
   "id": "C014",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C015",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C016",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C017",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C018",
   "names_contract_of": [
    "E4"
   ],
   "reason": "A later read must return the last write reported complete; a write reported complete but not stored violates this, so it names E4's contract, though its examples are stale caches and multipath rather than lost writes."
  },
  {
   "id": "C019",
   "names_contract_of": [
    "E2",
    "E3",
    "E5"
   ],
   "reason": "Its second statement requires that 'a completed write is durable before completion returns', the contract of E2, E3 and E5, applied to the recovery process's writes through the host page cache; the first statement (restart marker authenticity) names no sealed contract."
  },
  {
   "id": "C020",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C021",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C022",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C023",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C024",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C025",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C026",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C027",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C028",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C029",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C030",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C031",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C032",
   "names_contract_of": [],
   "reason": "Requires reads to return the last *durably* written bytes, which a lost write that was never durable does not violate, so it does not name E4's contract (nor E2's)."
  },
  {
   "id": "C033",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C034",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C035",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C036",
   "names_contract_of": [],
   "reason": "Bounds what a crash may leave on disk (only completed writes, no wild writes); that is an upper bound, not E2's durability-on-completion or E4's lost-write contract; no."
  },
  {
   "id": "C037",
   "names_contract_of": [],
   "reason": "Equivalence-class merge arguments relate to P3, not to a sealed bug; no."
  }
 ]
}


===== Gemini ruling: cells-1 (ruling.json) =====
{
 "cells": [
  {
   "id": "C001",
   "names_contract_of": [
    "E4"
   ],
   "reason": "C001 states the device 'must not return success for a page that was not stored' ('zero completion for a write it dropped'), matching E4's violated contract 'disk: a completed write was actually stored (no lost writes)'."
  },
  {
   "id": "C002",
   "names_contract_of": [],
   "reason": "C002 concerns client selection of write-back modes ('elbb_syncLog or elbb_async'), which is not the violated contract of any sealed bug."
  },
  {
   "id": "C003",
   "names_contract_of": [],
   "reason": "C003 concerns passing kernel addresses and accurate 'osi_copyin' on the metadata modify path, which matches no sealed bug."
  },
  {
   "id": "C004",
   "names_contract_of": [],
   "reason": "C004 concerns higher layers merging dependent transactions into equivalence classes via 'tlock' and 'elbt_ECMerge', which matches no sealed bug."
  },
  {
   "id": "C005",
   "names_contract_of": [],
   "reason": "C005 concerns callers ending transactions in bounded time and staying within 'MAX_TRAN_SIZE', which matches no sealed bug."
  },
  {
   "id": "C006",
   "names_contract_of": [],
   "reason": "C006 concerns retiring historical transaction IDs before 'elbt_GlobalTranId' 32-bit wrap, which matches no sealed bug."
  },
  {
   "id": "C007",
   "names_contract_of": [],
   "reason": "C007 concerns block allocator and buffer-pool transitions between logged and unlogged block incarnations, which matches no sealed bug."
  },
  {
   "id": "C008",
   "names_contract_of": [],
   "reason": "C008 concerns the aggregate layer supplying the complete ordered array of preallocated log-container blocks, which matches no sealed bug."
  },
  {
   "id": "C009",
   "names_contract_of": [],
   "reason": "C009 concerns maintaining a single canonical 'async_device_t' identity per aggregate, which matches no sealed bug."
  },
  {
   "id": "C010",
   "names_contract_of": [],
   "reason": "C010 concerns calling 'epig_InitAggregate' with 'logged' set to true, which matches no sealed bug."
  },
  {
   "id": "C011",
   "names_contract_of": [],
   "reason": "C011 concerns keeping 'logLocnArray' allocated and unchanged until log detachment, which matches no sealed bug."
  },
  {
   "id": "C012",
   "names_contract_of": [],
   "reason": "C012 concerns keeping nested undo-zero transactions and their parents within a single-transaction space reservation, which matches no sealed bug."
  },
  {
   "id": "C013",
   "names_contract_of": [
    "E5"
   ],
   "reason": "C013 requires that the caller record an undo-zero and 'ends that transaction only after the first write of the new data has completed' ('before that write is durable'), naming the contract underlying E5 ('disk: a completed write is durable (here: the user data write covered by undo-zero)')."
  },
  {
   "id": "C014",
   "names_contract_of": [],
   "reason": "C014 concerns CPU and compiler 4-byte alignment rules for log records, which matches no sealed bug."
  },
  {
   "id": "C015",
   "names_contract_of": [],
   "reason": "C015 concerns callers not treating 'elbb_QuiesceSystem' as covering subsequent concurrent updates, which matches no sealed bug."
  },
  {
   "id": "C016",
   "names_contract_of": [],
   "reason": "C016 concerns single-writer exclusivity and stopping new transactions before log shutdown, which matches no sealed bug."
  },
  {
   "id": "C017",
   "names_contract_of": [],
   "reason": "C017 concerns administrative tuning of global transaction and log-capacity limits across active log maps, which matches no sealed bug."
  },
  {
   "id": "C018",
   "names_contract_of": [
    "E2",
    "E3",
    "E4",
    "E5"
   ],
   "reason": "C018 requires that a later read return 'the data of the last write to that sector that the driver has reported complete' (violated when a drive cache or disk 'returns a stale copy after a completed write'), which covers the disk durability and non-dropped write contracts of E2, E3, E4, and E5."
  },
  {
   "id": "C019",
   "names_contract_of": [
    "E2",
    "E3",
    "E5"
   ],
   "reason": "C019 requires that the storage/OS environment ensure 'a completed write is durable before completion returns' and preserve ordering relative to the restart marker, naming the 'disk: a completed write is durable' contract of E2, E3, and E5 (though scoped to user-space recovery/shutdown)."
  },
  {
   "id": "C020",
   "names_contract_of": [],
   "reason": "C020 concerns higher layers serializing conflicting accesses to shared metadata objects via container/transactional locks, which matches no sealed bug."
  },
  {
   "id": "C021",
   "names_contract_of": [],
   "reason": "C021 concerns provisioning and using a known, supported log checksum version rather than 'LOGREC_CKSUMVER_NONE' or an unknown version, which matches no sealed bug."
  },
  {
   "id": "C022",
   "names_contract_of": [],
   "reason": "C022 concerns preserving stable 'async_device_t' identities and physical mappings across cached buffer lifetimes, which matches no sealed bug."
  },
  {
   "id": "C023",
   "names_contract_of": [],
   "reason": "C023 concerns callers passing only kernel-space metadata (not user pointers or file data) to quick logged modify and buffer fill, which matches no sealed bug."
  },
  {
   "id": "C024",
   "names_contract_of": [],
   "reason": "C024 concerns callers setting 'metadataOK' in 'elbb_Kill' only after the freeing transaction has committed, which matches no sealed bug."
  },
  {
   "id": "C025",
   "names_contract_of": [],
   "reason": "C025 concerns OS memory pinning ('logbuf_pin') and preventing the VM from reclaiming or writing buffer-pool pages during I/O, which matches no sealed bug."
  },
  {
   "id": "C026",
   "names_contract_of": [],
   "reason": "C026 concerns logical devices retaining a constant 'blkSize' and address mapping while attached, which matches no sealed bug."
  },
  {
   "id": "C027",
   "names_contract_of": [],
   "reason": "C027 concerns forcing or completing remembered transactions before destroying or recycling 'tlock' storage, which matches no sealed bug."
  },
  {
   "id": "C028",
   "names_contract_of": [],
   "reason": "C028 concerns callers having no dirty buffers at 'elbb_LogInit' and discarding cached state upon 'RCVR_RECOVERED', which matches no sealed bug."
  },
  {
   "id": "C029",
   "names_contract_of": [],
   "reason": "C029 concerns atomic lock release and reliable wakeup delivery in OS sleep and condition-variable primitives, which matches no sealed bug."
  },
  {
   "id": "C030",
   "names_contract_of": [],
   "reason": "C030 concerns keeping active log history and I/O performance comparable when interpreting recovery-time benchmarks, which matches no sealed bug."
  },
  {
   "id": "C031",
   "names_contract_of": [],
   "reason": "C031 concerns the primary superblock remaining valid and matching the log because attach and salvager do not use alternate superblocks, which matches no sealed bug."
  },
  {
   "id": "C032",
   "names_contract_of": [
    "E2",
    "E3",
    "E4",
    "E5"
   ],
   "reason": "C032 states 'Storage must return the bytes last durably written to the requested address or report an error' (violated when 'A read silently returns stale data'), which directly corresponds to the storage durability and no-lost-write contracts of E4 (and post-completion durability in E2, E3, E5)."
  },
  {
   "id": "C033",
   "names_contract_of": [],
   "reason": "C033 concerns matching CPU endianness, integer widths, and structure alignment between log writing and recovery, which matches no sealed bug."
  },
  {
   "id": "C034",
   "names_contract_of": [],
   "reason": "C034 concerns callers initializing all bytes of a no-read 'CreateBlock' buffer before writeback, which matches no sealed bug."
  },
  {
   "id": "C035",
   "names_contract_of": [],
   "reason": "C035 concerns passing valid, in-range block addresses that the device can read and write, which matches no sealed bug."
  },
  {
   "id": "C036",
   "names_contract_of": [
    "E2",
    "E3",
    "E5"
   ],
   "reason": "C036 states a crash 'leaves on disk only the sector writes that had already completed' ('whose writes had reached the device'), which touches the crash-durability boundary of E2, E3, and E5, though C036 focuses on absence of wild post-crash stores rather than volatile write caches."
  },
  {
   "id": "C037",
   "names_contract_of": [],
   "reason": "C037 concerns passing an active second transaction to 'elbt_ECMerge' and merging transactions that share metadata objects, which matches no sealed bug."
  }
 ]
}

===== GLM ruling (beside): cells-1 (ruling.json) =====
{
 "cells": [
  {
   "id": "C001",
   "names_contract_of": [
    "E4"
   ],
   "reason": "The cell's clause 'must not return success for a page that was not stored' is E4's contract that a completed write was actually stored (no lost writes)."
  },
  {
   "id": "C002",
   "names_contract_of": [],
   "reason": "Write-back mode selection is a caller obligation not recorded for any sealed bug."
  },
  {
   "id": "C003",
   "names_contract_of": [],
   "reason": "Kernel-address/copyin contract is not among the sealed contracts (E2\u2013E5 are disk durability only)."
  },
  {
   "id": "C004",
   "names_contract_of": [],
   "reason": "Equivalence-class merging obligations are not recorded for any sealed bug."
  },
  {
   "id": "C005",
   "names_contract_of": [],
   "reason": "Transaction lifetime/reservation bounds are not sealed contracts."
  },
  {
   "id": "C006",
   "names_contract_of": [],
   "reason": "Transaction-ID retirement is not a sealed contract."
  },
  {
   "id": "C007",
   "names_contract_of": [],
   "reason": "Block-reuse/buffer-transition contract is not among the sealed bugs."
  },
  {
   "id": "C008",
   "names_contract_of": [],
   "reason": "Log-block array description is not a sealed contract."
  },
  {
   "id": "C009",
   "names_contract_of": [],
   "reason": "Canonical device identity is not a sealed contract."
  },
  {
   "id": "C010",
   "names_contract_of": [],
   "reason": "Logging-enabled initialization is not a sealed contract."
  },
  {
   "id": "C011",
   "names_contract_of": [],
   "reason": "Log-location array lifetime is not a sealed contract."
  },
  {
   "id": "C012",
   "names_contract_of": [],
   "reason": "Nested-transaction size bounds are not sealed contracts."
  },
  {
   "id": "C013",
   "names_contract_of": [],
   "reason": "The caller-timing obligation on ending undo-zero differs from E5's sealed contract, which is disk durability of the completed user-data write, not a VM ending rule."
  },
  {
   "id": "C014",
   "names_contract_of": [],
   "reason": "CPU/compiler alignment is not a sealed contract."
  },
  {
   "id": "C015",
   "names_contract_of": [],
   "reason": "Quiesce boundary interpretation is not a sealed contract."
  },
  {
   "id": "C016",
   "names_contract_of": [],
   "reason": "Shutdown synchronization/single-writer is not a sealed contract."
  },
  {
   "id": "C017",
   "names_contract_of": [],
   "reason": "Live tuning limits are not a sealed contract."
  },
  {
   "id": "C018",
   "names_contract_of": [],
   "reason": "Read returning last completed write's data is a read contract; the sealed file records only write-durability contracts (E2\u2013E5)."
  },
  {
   "id": "C019",
   "names_contract_of": [],
   "reason": "Restart-marker authenticity/ordering is not a sealed contract."
  },
  {
   "id": "C020",
   "names_contract_of": [],
   "reason": "Object serialization is not a sealed contract."
  },
  {
   "id": "C021",
   "names_contract_of": [],
   "reason": "Checksum scheme selection is not a sealed contract."
  },
  {
   "id": "C022",
   "names_contract_of": [],
   "reason": "Device identity/mapping stability is not a sealed contract."
  },
  {
   "id": "C023",
   "names_contract_of": [],
   "reason": "Fast-modify kernel-address contract is not sealed."
  },
  {
   "id": "C024",
   "names_contract_of": [],
   "reason": "metadataOK-after-commit is not a sealed contract."
  },
  {
   "id": "C025",
   "names_contract_of": [],
   "reason": "OS pinning/DMA residency is not a sealed contract."
  },
  {
   "id": "C026",
   "names_contract_of": [],
   "reason": "Stable device block-size/addressing is not a sealed contract."
  },
  {
   "id": "C027",
   "names_contract_of": [],
   "reason": "Tlock recycling serialization is not a sealed contract."
  },
  {
   "id": "C028",
   "names_contract_of": [],
   "reason": "RCVR_RECOVERED handling is not a sealed contract."
  },
  {
   "id": "C029",
   "names_contract_of": [],
   "reason": "Sleep/wakeup atomicity is not a sealed contract."
  },
  {
   "id": "C030",
   "names_contract_of": [],
   "reason": "Recovery-time comparability is not a sealed contract."
  },
  {
   "id": "C031",
   "names_contract_of": [],
   "reason": "Primary superblock validity is not a sealed contract."
  },
  {
   "id": "C032",
   "names_contract_of": [],
   "reason": "Storage returning last durably written bytes is a read-side contract; sealed bugs record only write-durability contracts."
  },
  {
   "id": "C033",
   "names_contract_of": [],
   "reason": "On-disk format/endianness compatibility is not a sealed contract."
  },
  {
   "id": "C034",
   "names_contract_of": [],
   "reason": "No-read buffer initialization is not a sealed contract."
  },
  {
   "id": "C035",
   "names_contract_of": [],
   "reason": "In-range block addresses are not a sealed contract."
  },
  {
   "id": "C036",
   "names_contract_of": [],
   "reason": "Fail-stop crash semantics are the ambient model, not the violated contract recorded for any sealed bug (E1/E6/E7 record 'none violated')."
  },
  {
   "id": "C037",
   "names_contract_of": [],
   "reason": "Active-second-transaction merge precondition is not a sealed contract."
  }
 ]
}

===== Episode ruling: cells-2 (cells-2.json) =====
{
 "cells": [
  {
   "id": "C038",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C039",
   "names_contract_of": [],
   "reason": "End-record reservation for large ECs is the area of confirmed property P4, not a sealed bug; no."
  },
  {
   "id": "C040",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C041",
   "names_contract_of": [
    "E4"
   ],
   "reason": "ESOFT success 'for a write that was not stored' is a completion reported for an unstored write, E4's contract; its 'did not reach stable media' wording is close to E2's durability contract, but the cell is about a write never stored, so E4 only."
  },
  {
   "id": "C042",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C043",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C044",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C045",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C046",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C047",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C048",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C049",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C050",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C051",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C052",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C053",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C054",
   "names_contract_of": [],
   "reason": "Sector atomicity; no sealed bug rests on it (cf. confirmed property P5)."
  },
  {
   "id": "C055",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C056",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C057",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C058",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C059",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C060",
   "names_contract_of": [
    "E4"
   ],
   "reason": "Its second statement (a driver that 'signals completion for another request or drops an I/O error') is a write reported complete without being stored, E4's contract; borderline, since the contract is stated as correct association."
  },
  {
   "id": "C061",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C062",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C063",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C064",
   "names_contract_of": [],
   "reason": "Names no sealed bug's contract; it is the open item O1 (vnode-level serialisation so a block cannot re-enter transit after a waiter's in-transit check), which the sealed file leaves unresolved."
  },
  {
   "id": "C065",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C066",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C067",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C068",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C069",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C070",
   "names_contract_of": [],
   "reason": "Concerns completion reported while DMA still reads host memory (buffer reuse), not whether a completed write is stored or durable; no."
  },
  {
   "id": "C071",
   "names_contract_of": [
    "E4"
   ],
   "reason": "Mostly later decay, which is not a sealed contract, but its statements cover 'a controller loses an acknowledged recovered block' and 'a dropped sector', which are E4's lost-write contract."
  },
  {
   "id": "C072",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C073",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C074",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  }
 ]
}


===== Gemini cells-2: NO registered ruling (both runs unparseable); mechanical repair, beside only (ruling-repaired-beside.json) =====
{
 "cells": [
  {
   "id": "C038",
   "names_contract_of": [],
   "reason": "C038 concerns C compiler/ABI struct layout (\"contiguous device-pointer and block-number layout\") and device pointer aliasing, whereas the sealed bugs only record violated contracts on disk write durability and storage (E2\u2013E5)."
  },
  {
   "id": "C039",
   "names_contract_of": [],
   "reason": "C039 concerns callers keeping transaction equivalence classes small enough that \"every pending member's end-record reservation fits in the log,\" which is not the violated contract of any sealed bug."
  },
  {
   "id": "C040",
   "names_contract_of": [],
   "reason": "C040 concerns administrative callers requesting COMMIT quiescence and flushing buffers before reading the raw device, which does not match any contract in E1\u2013E7."
  },
  {
   "id": "C041",
   "names_contract_of": [
    "E2",
    "E3",
    "E4",
    "E5"
   ],
   "reason": "C041 states that an I/O completion reported as `ESOFT` \"must mean the transfer finished and is durable\" / reached \"stable media\" rather than being a write that \"was not stored,\" which is the AIX-specific instance of the sealed contract for E2, E3, E4, and E5 that a completed disk write is durable and actually stored."
  },
  {
   "id": "C042",
   "names_contract_of": [],
   "reason": "C042 concerns API callers choosing the right `waitOK` persistence level rather than treating `EndTran` as durable commitment, not disk durability of completed writes (E2\u2013E5)."
  },
  {
   "id": "C043",
   "names_contract_of": [],
   "reason": "C043 concerns clients passing \"live transaction IDs belonging to the intended device\" and not logging after `EndTran`, which is not a contract of E1\u2013E7."
  },
  {
   "id": "C044",
   "names_contract_of": [],
   "reason": "C044 concerns the liveness obligation that the async I/O service \"must eventually complete each accepted request\" rather than hanging, whereas E2\u2013E5 concern whether an already completed write was durably stored."
  },
  {
   "id": "C045",
   "names_contract_of": [],
   "reason": "C045 concerns clients classifying buffers as \"logged metadata or unlogged data correctly,\" which is unrelated to the contracts in E1\u2013E7."
  },
  {
   "id": "C046",
   "names_contract_of": [],
   "reason": "C046 concerns VM integration flushing dirty mapped pages and vnode `fsync` calling `elbb_LogForce`, which does not match any sealed bug's contract."
  },
  {
   "id": "C047",
   "names_contract_of": [],
   "reason": "C047 concerns OS thread scheduling and VM I/O daemon liveness (\"eventually schedule threads and I/O workers\"), which is not the contract of any sealed bug."
  },
  {
   "id": "C048",
   "names_contract_of": [],
   "reason": "C048 concerns callers scheduling dirty-buffer and VM undo-zero writes before waiting in commit quiescence, which does not match any sealed bug's contract."
  },
  {
   "id": "C049",
   "names_contract_of": [],
   "reason": "C049 concerns OS mutex mutual exclusion and interprocessor memory visibility, which is unrelated to E1\u2013E7."
  },
  {
   "id": "C050",
   "names_contract_of": [],
   "reason": "C050 concerns callers not holding an active transaction while waiting for transaction completion or quiescence, which is not a contract of E1\u2013E7."
  },
  {
   "id": "C051",
   "names_contract_of": [],
   "reason": "C051 concerns the block allocator not reusing freed metadata blocks until \"the freeing transaction and its prior dependencies have committed,\" which is not the contract of any sealed bug."
  },
  {
   "id": "C052",
   "names_contract_of": [],
   "reason": "C052 concerns callers passing in-bounds byte ranges and valid pointers to buffer modification APIs and finishing buffer updates before `elbb_UndoZeroBuffer`, whereas E5's contract is disk durability of the completed write."
  },
  {
   "id": "C053",
   "names_contract_of": [],
   "reason": "C053 concerns excluding concurrent filesystem mounts, raw writers, or multiple salvagers on the same aggregate, which is not a contract of E1\u2013E7."
  },
  {
   "id": "C054",
   "names_contract_of": [],
   "reason": "C054 concerns single-sector crash atomicity (\"write each sector atomically and correctly across a crash\" without tearing), whereas E2\u2013E5 concern whole completed writes being durable and actually stored."
  },
  {
   "id": "C055",
   "names_contract_of": [],
   "reason": "C055 concerns callers finishing in-memory buffer updates before calling `UndoZeroBuffer`, whereas E5's violated contract is the disk contract that \"a completed write is durable\" once written."
  },
  {
   "id": "C056",
   "names_contract_of": [],
   "reason": "C056 concerns callers passing valid kernel-space pointers to `elbb_Tune`/`elbl_Tune`, which is unrelated to E1\u2013E7."
  },
  {
   "id": "C057",
   "names_contract_of": [],
   "reason": "C057 concerns CPU/compiler atomicity of 32-bit memory stores for tuning parameters, which is unrelated to E1\u2013E7."
  },
  {
   "id": "C058",
   "names_contract_of": [],
   "reason": "C058 concerns not forging or corrupting the unchecksummed clean restart record and ordering it after recovery or shutdown writes, which is not the general completed-write durability/storage contract recorded for E2\u2013E5."
  },
  {
   "id": "C059",
   "names_contract_of": [],
   "reason": "C059 concerns running user-space recovery single-threaded with a valid `setjmp` frame and excluding concurrent writers, which is not a contract of E1\u2013E7."
  },
  {
   "id": "C060",
   "names_contract_of": [
    "E2",
    "E3",
    "E4",
    "E5"
   ],
   "reason": "C060 requires that the async I/O service \"associate each completion and error with the correct submitted request\" so waiting cannot \"certify a write that never completed\" or drop an I/O error, matching the obligation in E2\u2013E5 that a write reported complete was actually and durably stored."
  },
  {
   "id": "C061",
   "names_contract_of": [],
   "reason": "C061 concerns provisioning the log container to at least `elbl_MinLogSize` and keeping its size fixed, which is not a contract of E1\u2013E7."
  },
  {
   "id": "C062",
   "names_contract_of": [],
   "reason": "C062 concerns kernel panic code not continuing to modify metadata after `elbb_StartTran` fails, which is unrelated to E1\u2013E7."
  },
  {
   "id": "C063",
   "names_contract_of": [],
   "reason": "C063 concerns device block sizes being a supported power of two between 1 KiB and 64 KiB, which is unrelated to E1\u2013E7."
  },
  {
   "id": "C064",
   "names_contract_of": [],
   "reason": "C064 concerns higher-level vnode locking serializing overlapping block I/O across in-transit waits, which is not a contract of E1\u2013E7."
  },
  {
   "id": "C065",
   "names_contract_of": [],
   "reason": "C065 concerns callers holding valid writable buffer references and releasing them without leaks, which is unrelated to E1\u2013E7."
  },
  {
   "id": "C066",
   "names_contract_of": [],
   "reason": "C066 concerns `DEV_BSIZE`/`btodb` sector-address conversion matching physical disk sectors, rather than completed writes being durable or retained (E2\u2013E5)."
  },
  {
   "id": "C067",
   "names_contract_of": [],
   "reason": "C067 concerns the VM async daemon and scheduler continuing to run to complete undo-zero I/O without deadlocking on log space, which is not a contract of E1\u2013E7."
  },
  {
   "id": "C068",
   "names_contract_of": [],
   "reason": "C068 concerns callers checking `BUF_WOULDBLOCK` and error return codes from `logbuf`, which is unrelated to E1\u2013E7."
  },
  {
   "id": "C069",
   "names_contract_of": [],
   "reason": "C069 concerns the block allocator committing user-data kill (`undo-zero`) transactions before reusing blocks for metadata, which is not a contract of E1\u2013E7."
  },
  {
   "id": "C070",
   "names_contract_of": [
    "E2",
    "E3",
    "E4",
    "E5"
   ],
   "reason": "C070 states that the async service \"must finish all transfers before reporting their event complete,\" which is part of the E2\u2013E5 contract that a write reported as completed has actually been stored to durable media."
  },
  {
   "id": "C071",
   "names_contract_of": [
    "E2",
    "E3",
    "E4",
    "E5"
   ],
   "reason": "C071 states that the storage stack/device \"must preserve completed writes until an explicitly authorized overwrite\" and return \"the bytes of the last completed write,\" directly naming the E2\u2013E5 contract that a completed write is durably stored and not lost."
  },
  {
   "id": "C072",
   "names_contract_of": [],
   "reason": "C072 concerns the host memory allocator supplying enough heap space to hold the active log during recovery, which is unrelated to E1\u2013E7."
  },
  {
   "id": "C073",
   "names_contract_of": [],
   "reason": "C073 concerns callers calling `elbb_Reserve` before acquiring multiple buffers simultaneously, which is unrelated to E1\u2013E7."
  },
  {
   "id": "C074",
   "names_contract_of": [],
   "reason": "C074 concerns `setjmp`/`longjmp` properly unwinding the stack on `RCVR_RAISE` during recovery, which is unrelated to E1\u2013E7."
  }
 ]
}

===== GLM ruling (beside): cells-2 (ruling.json) =====
{
 "cells": [
  {
   "id": "C038",
   "names_contract_of": [],
   "reason": "ABI field-layout/device-aliasing contract is not any sealed bug's contract (E1/E6/E7 violate no contract; E2\u2013E5 are disk durability)."
  },
  {
   "id": "C039",
   "names_contract_of": [],
   "reason": "Equivalence-class size contract on callers is not among the sealed contracts (disk durability only)."
  },
  {
   "id": "C040",
   "names_contract_of": [],
   "reason": "Quiesce/commit-level contract for external readers is not a sealed bug's contract."
  },
  {
   "id": "C041",
   "names_contract_of": [
    "E2",
    "E4"
   ],
   "reason": "The contract that a completion reported as success means the transfer finished and is stored/durable is the sealed 'disk: a completed write was actually stored' (E4) and 'a completed write is durable' (E2) contract, here attributed to the AIX driver."
  },
  {
   "id": "C042",
   "names_contract_of": [],
   "reason": "Caller persistence-level/waitOK contract is not a sealed contract."
  },
  {
   "id": "C043",
   "names_contract_of": [],
   "reason": "Live transaction-ID discipline is not a sealed contract."
  },
  {
   "id": "C044",
   "names_contract_of": [],
   "reason": "Async liveness contract (eventual completion) is not among the sealed durability contracts."
  },
  {
   "id": "C045",
   "names_contract_of": [],
   "reason": "Buffer classification contract is not a sealed contract."
  },
  {
   "id": "C046",
   "names_contract_of": [],
   "reason": "VM flush/fsync-force contract is not a sealed contract."
  },
  {
   "id": "C047",
   "names_contract_of": [],
   "reason": "Scheduler/daemon forward-progress contract is not a sealed contract."
  },
  {
   "id": "C048",
   "names_contract_of": [],
   "reason": "Quiesce ordering prerequisite is not a sealed contract."
  },
  {
   "id": "C049",
   "names_contract_of": [],
   "reason": "Mutex/memory-ordering contract is not a sealed contract."
  },
  {
   "id": "C050",
   "names_contract_of": [],
   "reason": "No-active-transaction-while-waiting contract is not a sealed contract."
  },
  {
   "id": "C051",
   "names_contract_of": [],
   "reason": "Kill-record/allocator ordering contract is not a sealed contract."
  },
  {
   "id": "C052",
   "names_contract_of": [],
   "reason": "Byte-range/undo-zero caller ordering contracts are not sealed contracts."
  },
  {
   "id": "C053",
   "names_contract_of": [],
   "reason": "Single-writer/single-recovery exclusion contract is not a sealed contract."
  },
  {
   "id": "C054",
   "names_contract_of": [],
   "reason": "Sector-write atomicity contract is not among the sealed contracts (E2\u2013E5 concern durability of completed writes, not atomicity of a single sector)."
  },
  {
   "id": "C055",
   "names_contract_of": [],
   "reason": "Undo-zero attach-after-write contract is not a sealed contract."
  },
  {
   "id": "C056",
   "names_contract_of": [],
   "reason": "Tune pointer/address-space contract is not a sealed contract."
  },
  {
   "id": "C057",
   "names_contract_of": [],
   "reason": "Atomic 32-bit store contract is not a sealed contract."
  },
  {
   "id": "C058",
   "names_contract_of": [],
   "reason": "Restart-record authenticity/ordering contract is not a sealed contract."
  },
  {
   "id": "C059",
   "names_contract_of": [],
   "reason": "Recovery exclusion/single-thread contract is not a sealed contract."
  },
  {
   "id": "C060",
   "names_contract_of": [],
   "reason": "Async completion liveness/correct-association contract is not a sealed durability contract."
  },
  {
   "id": "C061",
   "names_contract_of": [],
   "reason": "Log sizing/provisioning contract is not a sealed contract."
  },
  {
   "id": "C062",
   "names_contract_of": [],
   "reason": "Panic-path no-new-transactions contract is not a sealed contract."
  },
  {
   "id": "C063",
   "names_contract_of": [],
   "reason": "Block-size limits contract is not a sealed contract."
  },
  {
   "id": "C064",
   "names_contract_of": [],
   "reason": "Overlapping-I/O serialization contract is not a sealed contract."
  },
  {
   "id": "C065",
   "names_contract_of": [],
   "reason": "Buffer reference discipline is not a sealed contract."
  },
  {
   "id": "C066",
   "names_contract_of": [],
   "reason": "DEV_BSIZE/sector conversion contract is not a sealed contract."
  },
  {
   "id": "C067",
   "names_contract_of": [],
   "reason": "VM daemon/scheduler forward-progress contracts are not sealed contracts."
  },
  {
   "id": "C068",
   "names_contract_of": [],
   "reason": "Caller error-checking contract is not a sealed contract."
  },
  {
   "id": "C069",
   "names_contract_of": [],
   "reason": "Kill-before-reuse allocator ordering contract is not a sealed contract."
  },
  {
   "id": "C070",
   "names_contract_of": [],
   "reason": "Premature-completion (transfer not yet finished) is a completion-reporting contract, not the sealed 'completed write is durable/stored' contract."
  },
  {
   "id": "C071",
   "names_contract_of": [
    "E2",
    "E3",
    "E4"
   ],
   "reason": "The contract that completed writes are preserved (stored and durable) until an authorized overwrite is exactly the sealed disk contracts of E2, E3 and E4."
  },
  {
   "id": "C072",
   "names_contract_of": [],
   "reason": "Memory-capacity contract for recovery is not a sealed contract."
  },
  {
   "id": "C073",
   "names_contract_of": [],
   "reason": "Buffer reservation contract is not a sealed contract."
  },
  {
   "id": "C074",
   "names_contract_of": [],
   "reason": "setjmp/longjmp semantics contract is not a sealed contract."
  }
 ]
}

===== Episode ruling: cells-3 (cells-3.json) =====
{
 "cells": [
  {
   "id": "C075",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C076",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C077",
   "names_contract_of": [
    "E4"
   ],
   "reason": "'A failed write while leaving B_ERROR clear' is a write reported complete that was not stored, E4's contract."
  },
  {
   "id": "C078",
   "names_contract_of": [
    "E2",
    "E3",
    "E5"
   ],
   "reason": "'When the driver reports an I/O complete, that entire transfer is on stable storage', violated by a volatile write-back cache: exactly the contract of E2, E3 and E5 (E5 through its general 'every sector of that write' statements, which cover user data writes)."
  },
  {
   "id": "C079",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C080",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C081",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C082",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C083",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C084",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C085",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C086",
   "names_contract_of": [],
   "reason": "Names the caller's undo-zero coverage obligation, not E5's device durability contract; no."
  },
  {
   "id": "C087",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C088",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C089",
   "names_contract_of": [],
   "reason": "Names the VM's undo-zero obligation, not E5's device durability contract; no."
  },
  {
   "id": "C090",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C091",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C092",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C093",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C094",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C095",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C096",
   "names_contract_of": [],
   "reason": "Names no sealed bug's contract; it is the asserted half of the strategy-layer assumption around O1 (at most one waiter per in-transit block), which the sealed file records as asserted (fail-stop), not a bug."
  },
  {
   "id": "C097",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C098",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C099",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C100",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C101",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C102",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C103",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C104",
   "names_contract_of": [],
   "reason": "Sector atomicity and header placement; no sealed bug rests on it (cf. P5)."
  },
  {
   "id": "C105",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C106",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C107",
   "names_contract_of": [
    "E2",
    "E3"
   ],
   "reason": "Its statements that a completed write on the log device must still be present at recovery, violated by 'a log on volatile media while the data disk kept its completed writes', name the durability-on-completion contract in E3's shape (data durable, log record lost) and E2's."
  },
  {
   "id": "C108",
   "names_contract_of": [
    "E4"
   ],
   "reason": "Its third statement names 'a dropped write that was acknowledged' on a committed log page, E4's contract; the rest is later decay or stale reads, which no sealed bug records."
  },
  {
   "id": "C109",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  },
  {
   "id": "C110",
   "names_contract_of": [],
   "reason": "States an obligation that no sealed bug records as its violated contract (E2/E3/E5: completion implies durability; E4: a completed write was stored; E1, E6, E7: none below logbuf)."
  }
 ]
}


===== Gemini ruling: cells-3 (ruling.json) =====
{
 "cells": [
  {
   "id": "C075",
   "names_contract_of": [],
   "reason": "Requires upper filesystem layers to route all metadata updates through logged transactions, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C076",
   "names_contract_of": [],
   "reason": "Requires mount and operator paths to run user-space recovery on a dirty log (`RCVR_MUSTRCVR`), which is not the violated contract of any sealed bug."
  },
  {
   "id": "C077",
   "names_contract_of": [
    "E4"
   ],
   "reason": "States that the storage stack must report a \u201dfailed write\u201d as an error rather than returning \u201dsuccess with a short transfer, wrong-sector read, or failed write while leaving B_ERROR clear,\u201d matching E4's contract that \u201ddisk: a completed write was actually stored (no lost writes).\u201d"
  },
  {
   "id": "C078",
   "names_contract_of": [
    "E2",
    "E3",
    "E4",
    "E5"
   ],
   "reason": "States (citing `recover.c:894`) that \u201dwhen the driver reports an I/O complete, that entire transfer is on stable storage and later reads, including reads after power loss, return those bytes\u201d rather than sitting in a \u201dvolatile write-back cache,\u201d directly naming the completed-write durability and storage contracts of E2, E3, E4, and E5."
  },
  {
   "id": "C079",
   "names_contract_of": [],
   "reason": "Requires callers to use the replacement buffer handle (`nbP`) returned by modifying operations, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C080",
   "names_contract_of": [],
   "reason": "Requires the configured device and aggregate block size to be a supported power of two matching the superblock, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C081",
   "names_contract_of": [],
   "reason": "Requires user-space `setjmp`/`longjmp` to preserve the return code passed to `longjmp`, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C082",
   "names_contract_of": [],
   "reason": "Requires log-creation callers to exclude concurrent activity on the device, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C083",
   "names_contract_of": [],
   "reason": "Requires the failure environment not to produce CRC-preserving corruption on log pages, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C084",
   "names_contract_of": [],
   "reason": "Requires callers to keep `newData` source memory stable while it is logged and copied into the buffer, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C085",
   "names_contract_of": [],
   "reason": "Requires operators to run the salvager rather than force an aggregate online after hard I/O or unrecoverable log errors, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C086",
   "names_contract_of": [],
   "reason": "Requires filesystem and VM allocation callers to record an undo-zero transaction and end it only after the first write completes, whereas E5 violates the disk's completed-write durability contract after the caller properly orders `OFILL` before `END`."
  },
  {
   "id": "C087",
   "names_contract_of": [],
   "reason": "Requires periodic OS sync/checkpoint activity to bound the active log tail, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C088",
   "names_contract_of": [],
   "reason": "Requires the log container's size and block allocation to remain fixed while the aggregate is in use, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C089",
   "names_contract_of": [],
   "reason": "Requires VM strategy callers to invoke `elbb_UndoZero` with the right byte range and wait for write completion before ending the transaction, whereas E5 is a violation of the disk durability contract rather than caller omission."
  },
  {
   "id": "C090",
   "names_contract_of": [],
   "reason": "Requires callers to keep each transaction within `MAX_TRAN_SIZE` and split oversized operations, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C091",
   "names_contract_of": [],
   "reason": "Requires `fsync` callers to tag or list all relevant buffers and flush VM pages, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C092",
   "names_contract_of": [],
   "reason": "Requires callers to use redo-only initialization (`elbb_Initialize`/`CreateBlock`) only on newly allocated blocks whose old contents need not be restored, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C093",
   "names_contract_of": [],
   "reason": "Requires the log-location array to list distinct preallocated log blocks that do not overlap file or metadata blocks, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C094",
   "names_contract_of": [],
   "reason": "Requires transaction package initialization to run single-threaded before concurrent use, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C095",
   "names_contract_of": [],
   "reason": "Requires storage writes to affect only the addressed sectors without misdirected overwrites of unrelated blocks, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C096",
   "names_contract_of": [],
   "reason": "Requires the VM and vnode layers to respect the strategy layer's bound on simultaneous waiters per in-transit block, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C097",
   "names_contract_of": [],
   "reason": "Requires callers not to mix logged and unlogged modifications on the same buffer, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C098",
   "names_contract_of": [],
   "reason": "Requires callers of `elbb_LogInit` to have no dirty cached buffers for the device when recovery may run, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C099",
   "names_contract_of": [],
   "reason": "Requires operators to leave removable media in place until aggregate close finishes writing the restart block, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C100",
   "names_contract_of": [],
   "reason": "Requires callers needing persistence to select a synchronous wait mode rather than `elbb_async`, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C101",
   "names_contract_of": [],
   "reason": "Requires log-creation callers not to hold buffer-package locks upon entry, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C102",
   "names_contract_of": [],
   "reason": "Requires log length and page indices to fit within 16-bit offset and signed-distance arithmetic, whereas E7 is an internal pass-number invariant (`own`) rather than a log-size configuration contract."
  },
  {
   "id": "C103",
   "names_contract_of": [],
   "reason": "Requires the OS clock to progress normally for buffer-cache aging heuristics, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C104",
   "names_contract_of": [],
   "reason": "Requires hardware sector writes to be atomic and large enough to hold the log page header and checksum, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C105",
   "names_contract_of": [],
   "reason": "Requires upper layers to place transaction boundaries so that each committed transaction preserves filesystem invariants, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C106",
   "names_contract_of": [],
   "reason": "Requires pointer alignment macros not to truncate addresses on the target architecture, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C107",
   "names_contract_of": [],
   "reason": "Requires backup/restore and split log/data device deployments to keep the log and data devices paired and recovered together, which is not the single-disk durability or lost-write contract of E2\u2013E5."
  },
  {
   "id": "C108",
   "names_contract_of": [
    "E2",
    "E3",
    "E4",
    "E5"
   ],
   "reason": "States that \u201duntil Episode overwrites a block, the device returns the bytes of the last completed write to that block\u201d and forbids \u201da dropped write that was acknowledged\u201d or \u201ddropped sector,\u201d naming E4's contract that \u201ddisk: a completed write was actually stored (no lost writes)\u201d and overlapping with E2, E3, and E5's completed-write durability contract."
  },
  {
   "id": "C109",
   "names_contract_of": [],
   "reason": "Requires initialization callers to provide a valid writable buffer pool for the package's lifetime, which is not the violated contract of any sealed bug."
  },
  {
   "id": "C110",
   "names_contract_of": [],
   "reason": "Requires external callers to request only data or logged buffer types and leave internal types to `logbuf`, which is not the violated contract of any sealed bug."
  }
 ]
}

===== GLM ruling (beside): cells-3 (ruling.json) =====
{
 "cells": [
  {
   "id": "C075",
   "names_contract_of": [],
   "reason": "Caller-side obligation to log metadata updates; no sealed bug records a violated contract (E1/E6/E7 have none, E2\u2013E5 are disk durability)."
  },
  {
   "id": "C076",
   "names_contract_of": [],
   "reason": "Mount/recovery orchestration contract; not any sealed bug's contract."
  },
  {
   "id": "C077",
   "names_contract_of": [],
   "reason": "Storage must report failed/short I/O as errors; sealed bugs concern durability of completed writes, not error reporting."
  },
  {
   "id": "C078",
   "names_contract_of": [
    "E2",
    "E3",
    "E4"
   ],
   "reason": "Contract that a successfully completed write is durable/stable storage is exactly the disk contract recorded for E2, E3 and E4."
  },
  {
   "id": "C079",
   "names_contract_of": [],
   "reason": "Caller must use returned buffer handle; no sealed bug records this contract."
  },
  {
   "id": "C080",
   "names_contract_of": [],
   "reason": "Block-size/geometry contract; not a sealed bug contract."
  },
  {
   "id": "C081",
   "names_contract_of": [],
   "reason": "setjmp/longjmp semantics; not a sealed bug contract."
  },
  {
   "id": "C082",
   "names_contract_of": [],
   "reason": "Log-creation exclusion contract; not a sealed bug contract."
  },
  {
   "id": "C083",
   "names_contract_of": [],
   "reason": "Checksum-collision environment contract; not a sealed bug contract."
  },
  {
   "id": "C084",
   "names_contract_of": [],
   "reason": "Caller keeps new-data stable during logging; not a sealed bug contract."
  },
  {
   "id": "C085",
   "names_contract_of": [],
   "reason": "Operator must run salvager after hard errors; not a sealed bug contract."
  },
  {
   "id": "C086",
   "names_contract_of": [],
   "reason": "Caller-side undo-zero coverage obligation; E5's violated contract is the disk's durability of the completed user-data write, not caller coverage, so no."
  },
  {
   "id": "C087",
   "names_contract_of": [],
   "reason": "Periodic sync/checkpoint contract; not a sealed bug contract."
  },
  {
   "id": "C088",
   "names_contract_of": [],
   "reason": "Fixed log container size/location; not a sealed bug contract."
  },
  {
   "id": "C089",
   "names_contract_of": [],
   "reason": "VM caller obligation to record undo-zero; E5's contract is disk durability, not this caller rule."
  },
  {
   "id": "C090",
   "names_contract_of": [],
   "reason": "Transaction size/reservation bound; not a sealed bug contract."
  },
  {
   "id": "C091",
   "names_contract_of": [],
   "reason": "Fsync buffer tagging; not a sealed bug contract."
  },
  {
   "id": "C092",
   "names_contract_of": [],
   "reason": "Initialization only for new blocks; not a sealed bug contract."
  },
  {
   "id": "C093",
   "names_contract_of": [],
   "reason": "Log block reservation/exclusivity; not a sealed bug contract."
  },
  {
   "id": "C094",
   "names_contract_of": [],
   "reason": "Single-threaded initialization; not a sealed bug contract."
  },
  {
   "id": "C095",
   "names_contract_of": [],
   "reason": "Writes confined to addressed sectors; not a sealed bug contract."
  },
  {
   "id": "C096",
   "names_contract_of": [],
   "reason": "Strategy waiter bound; not a sealed bug contract."
  },
  {
   "id": "C097",
   "names_contract_of": [],
   "reason": "No mixing logged/unlogged updates; not a sealed bug contract."
  },
  {
   "id": "C098",
   "names_contract_of": [],
   "reason": "Clean buffer cache at LogInit; not a sealed bug contract."
  },
  {
   "id": "C099",
   "names_contract_of": [],
   "reason": "Removable media during close; not a sealed bug contract."
  },
  {
   "id": "C100",
   "names_contract_of": [],
   "reason": "Persistence mode selection; not a sealed bug contract."
  },
  {
   "id": "C101",
   "names_contract_of": [],
   "reason": "Lock convention at log creation; not a sealed bug contract."
  },
  {
   "id": "C102",
   "names_contract_of": [],
   "reason": "Log length field ranges; not a sealed bug contract."
  },
  {
   "id": "C103",
   "names_contract_of": [],
   "reason": "OS time service; not a sealed bug contract."
  },
  {
   "id": "C104",
   "names_contract_of": [],
   "reason": "Sector atomicity for log page headers; not a sealed bug contract."
  },
  {
   "id": "C105",
   "names_contract_of": [],
   "reason": "Transaction boundary consistency; not a sealed bug contract."
  },
  {
   "id": "C106",
   "names_contract_of": [],
   "reason": "Pointer alignment on ports; not a sealed bug contract."
  },
  {
   "id": "C107",
   "names_contract_of": [],
   "reason": "Backup/log-data crash-consistent pairing; not a sealed bug contract."
  },
  {
   "id": "C108",
   "names_contract_of": [
    "E2",
    "E4"
   ],
   "reason": "Contract that completed writes are preserved intact until authorized overwrite, including acknowledged-but-dropped writes, matches E4's 'completed write was actually stored' and E2's durability contract."
  },
  {
   "id": "C109",
   "names_contract_of": [],
   "reason": "Buffer-pool memory ownership; not a sealed bug contract."
  },
  {
   "id": "C110",
   "names_contract_of": [],
   "reason": "Buffer type classification; not a sealed bug contract."
  }
 ]
}

===== Episode ruling: rows (rows.json) =====
{
 "rows": [
  {
   "id": "R01",
   "matches": [],
   "reason": "OT 3435 (CRCs added for out-of-order sector writes within a log page) is real DCE history (crc.c), but concerns torn log pages, not a sealed bug."
  },
  {
   "id": "R02",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R03",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R04",
   "matches": [
    "E2"
   ],
   "reason": "Names E2's contract (volatile caches reporting completion before media is stable) with the write-ahead-log loss of acknowledged log writes as the failure; recognised from general practice of the era, not from the sealed analysis, so a match by contract and general mechanism but not evidence of leakage."
  },
  {
   "id": "R05",
   "matches": [],
   "reason": "Exposure of previous contents after allocation shares E5's effect class, but the mechanism (missing VM undo-zero coverage, OT 3804/1020) and contract (caller coverage) differ from E5's (device durability with coverage correct)."
  },
  {
   "id": "R06",
   "matches": [],
   "reason": "As R05: new-block security via missing undo-zero coverage, not E5's device-durability mechanism."
  },
  {
   "id": "R07",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R08",
   "matches": [],
   "reason": "Does not describe any sealed bug's contract and mechanism."
  },
  {
   "id": "R09",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R10",
   "matches": [],
   "reason": "As R05; the observation that elbb_UndoZero has no caller in this tree, if true, is an exposure path the sealed analysis did not list (its P6 is only about the B_ASYNC precondition)."
  },
  {
   "id": "R11",
   "matches": [],
   "reason": "Points at E6's location (GetCleanLogInfo inspecting block 0 under out-of-order completion) but concludes it 'looks safe' and gives no failing mechanism, so no match; it is the question F03 answered."
  },
  {
   "id": "R12",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R13",
   "matches": [
    "E2"
   ],
   "reason": "Same as R04: write-back caches acknowledging before media, 'the same class of bug as other write-ahead logs'; general knowledge, not leakage."
  },
  {
   "id": "R14",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R15",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R16",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R17",
   "matches": [],
   "reason": "Unknown checksum types and unchecksummed restart pages (cf. F02, F09) are not sealed bugs."
  },
  {
   "id": "R18",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R19",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R20",
   "matches": [],
   "reason": "The elbb_UndoZero multi-block loop that never increments blkno (buffer.c:2440-2449) is a new own-rule defect claim not in the sealed file; worth verifying."
  },
  {
   "id": "R21",
   "matches": [],
   "reason": "No match, and a disagreement with E7: it argues that pass-number collision needs a lost write because 'each pass overwrites every log page', which is the premise E7 shows false (restarting at slot 0 leaves far slots unrewritten)."
  },
  {
   "id": "R22",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R23",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R24",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R25",
   "matches": [],
   "reason": "Does not describe any sealed bug's contract and mechanism."
  },
  {
   "id": "R26",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R27",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R28",
   "matches": [],
   "reason": "States that the code assumes no in-order completion, consistent with v2's classification of E1 and E6 as logbuf's own defects; no match."
  },
  {
   "id": "R29",
   "matches": [],
   "reason": "Does not describe any sealed bug's contract and mechanism."
  },
  {
   "id": "R30",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R31",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R32",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R33",
   "matches": [],
   "reason": "Does not describe any sealed bug's contract and mechanism."
  },
  {
   "id": "R34",
   "matches": [],
   "reason": "Does not describe any sealed bug's contract and mechanism."
  },
  {
   "id": "R35",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R36",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R37",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R38",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R39",
   "matches": [],
   "reason": "Does not describe any sealed bug's contract and mechanism."
  },
  {
   "id": "R40",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R41",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R42",
   "matches": [],
   "reason": "Own-rule observations (unknown checksum accepted, restart page unchecksummed, compiled-out asserts) are not sealed bugs."
  },
  {
   "id": "R43",
   "matches": [],
   "reason": "Does not describe any sealed bug's contract and mechanism."
  },
  {
   "id": "R44",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R45",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R46",
   "matches": [],
   "reason": "Does not describe any sealed bug's contract and mechanism."
  },
  {
   "id": "R47",
   "matches": [],
   "reason": "NewLogPage ignoring asevent_QueueIO's return is a new own-rule defect claim not in the sealed file."
  },
  {
   "id": "R48",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R49",
   "matches": [],
   "reason": "Unknown checksum accepted (cf. F02); not a sealed bug."
  },
  {
   "id": "R50",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R51",
   "matches": [],
   "reason": "OT 5527 is real DCE history: a pass number reaching zero after repeated init/shutdown (anode/passno.test). It is in E7's area (pass numbers across mounts) but is a different defect, and the row draws no mechanism; no match."
  },
  {
   "id": "R52",
   "matches": [],
   "reason": "Does not describe any sealed bug's contract and mechanism."
  },
  {
   "id": "R53",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R54",
   "matches": [],
   "reason": "Names E2's contract only as 'a familiar filesystem failure pattern', with no mechanism; no match."
  },
  {
   "id": "R55",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R56",
   "matches": [],
   "reason": "Recognises OT 5527 as an internal pass-number bug, in E7's area, but gives no mechanism, and OT 5527 (a zero pass number after repeated mounts) is not E7's masked-comparison aliasing; no match."
  },
  {
   "id": "R57",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R58",
   "matches": [],
   "reason": "Consistent with v2's E1/E6 classification; no match."
  },
  {
   "id": "R59",
   "matches": [],
   "reason": "Not a claim: a heading, count, file listing or git output captured from the report (see packet notes)."
  },
  {
   "id": "R60",
   "matches": [],
   "reason": "Does not describe any sealed bug's contract and mechanism."
  }
 ]
}


===== Gemini ruling: rows (ruling.json) =====
{
 "rows": [
  {
   "id": "R01",
   "matches": [],
   "reason": "Describes torn-page corruption from out-of-order sector writes within a single page (OT 3435), whereas sealed E1 and E6 concern out-of-order completion across whole log pages."
  },
  {
   "id": "R02",
   "matches": [],
   "reason": "Contains only a filename (`enumeration.md`) with no contract or mechanism."
  },
  {
   "id": "R03",
   "matches": [],
   "reason": "Contains only `git status` output with no contract or mechanism."
  },
  {
   "id": "R04",
   "matches": [
    "E2"
   ],
   "reason": "Matches sealed E2's durable-write contract and mechanism via \"volatile disk write caches that report completion before the media is stable\"."
  },
  {
   "id": "R05",
   "matches": [],
   "reason": "Describes historical new-block security (OT 3804/1020) and an unimplemented VM `strategy.c` undo-zero path rather than sealed E5's volatile disk write-cache mechanism after `OFILL` and `END`."
  },
  {
   "id": "R06",
   "matches": [],
   "reason": "Describes historical new-block security (OT 3804/1020) and `anode/strategy.c`'s unimplemented `iodone` undo-zero database rather than sealed E5's volatile disk write-cache mechanism."
  },
  {
   "id": "R07",
   "matches": [],
   "reason": "Contains only `git status` output with no contract or mechanism."
  },
  {
   "id": "R08",
   "matches": [],
   "reason": "Describes an `epimount` defect (OT 3338) where a dirty log was not recovered before kernel attach, which does not match any of sealed E1\u2013E7."
  },
  {
   "id": "R09",
   "matches": [],
   "reason": "Contains only `git status` output with no contract or mechanism."
  },
  {
   "id": "R10",
   "matches": [],
   "reason": "Discusses whether `epia_Iodone`'s \"undo-zero not yet implemented\" comment and uncalled `elbb_UndoZero` represent a VM gap, not sealed E5's volatile write-cache exposure mechanism."
  },
  {
   "id": "R11",
   "matches": [],
   "reason": "Questions whether `GetCleanLogInfo` checking only block 0 is safe under out-of-order completion, without stating sealed E1's `io_window` count-versus-distance mechanism or E6's clean-mount pass reuse."
  },
  {
   "id": "R12",
   "matches": [],
   "reason": "Contains only a section header (\"Could not decide:\") with no contract or mechanism."
  },
  {
   "id": "R13",
   "matches": [
    "E2"
   ],
   "reason": "Matches sealed E2's durable-write contract and mechanism via \"Write-back disk caches that acknowledge a write before it is on media\"."
  },
  {
   "id": "R14",
   "matches": [],
   "reason": "Contains only directory listing output with no contract or mechanism."
  },
  {
   "id": "R15",
   "matches": [],
   "reason": "Contains only directory listing output with no contract or mechanism."
  },
  {
   "id": "R16",
   "matches": [],
   "reason": "States only a contract count (\"48 contracts.\") with no contract or mechanism."
  },
  {
   "id": "R17",
   "matches": [],
   "reason": "Lists internal source concerns (`#if 0` assertions, `ModifySource` copy faults, unknown checksum types, unchecksummed restart pages, and `strategy.c` undo-zero completion) that do not match sealed E1\u2013E7."
  },
  {
   "id": "R18",
   "matches": [],
   "reason": "Contains only an `ls -R` command note with no contract or mechanism."
  },
  {
   "id": "R19",
   "matches": [],
   "reason": "Contains only a section header with no contract or mechanism."
  },
  {
   "id": "R20",
   "matches": [],
   "reason": "Describes static code observations (`elbb_UndoZero` not incrementing `blkno`, `elbl_MinTranReservation` mask assertion, and disabled assertions) that do not match sealed E1\u2013E7."
  },
  {
   "id": "R21",
   "matches": [],
   "reason": "Discusses 16-bit pass-number wrap under the assumption that \"Each pass overwrites every log page\" plus a lost write, missing sealed E7's mechanism where restarting at slot 0 on mount leaves far slots unrewritten."
  },
  {
   "id": "R22",
   "matches": [],
   "reason": "Contains only directory listing output with no contract or mechanism."
  },
  {
   "id": "R23",
   "matches": [],
   "reason": "Contains only directory listing output with no contract or mechanism."
  },
  {
   "id": "R24",
   "matches": [],
   "reason": "Contains only a `git status` header with no contract or mechanism."
  },
  {
   "id": "R25",
   "matches": [],
   "reason": "Notes that restart pages are written without a checksum and rely on the checkpoint-then-restart sequence, which does not match sealed E1\u2013E7."
  },
  {
   "id": "R26",
   "matches": [],
   "reason": "Contains only report inventory metadata with no contract or mechanism."
  },
  {
   "id": "R27",
   "matches": [],
   "reason": "Contains only `git status` output with no contract or mechanism."
  },
  {
   "id": "R28",
   "matches": [],
   "reason": "Summarizes general performance qualifications, excluded user-data atomicity, finite checksums, and in-transit window tolerance without stating any sealed E1\u2013E7 bug mechanism."
  },
  {
   "id": "R29",
   "matches": [],
   "reason": "Notes that `elbr_Recover` panics when `SafeDumpLog` returns an error, without stating sealed E1's `io_window` count-versus-distance mechanism that triggers a spurious `RCVR_IOERR`."
  },
  {
   "id": "R30",
   "matches": [],
   "reason": "Contains only directory listing output with no contract or mechanism."
  },
  {
   "id": "R31",
   "matches": [],
   "reason": "Contains only `ls -R` output with no contract or mechanism."
  },
  {
   "id": "R32",
   "matches": [],
   "reason": "Contains only methodological notes about the source enumeration with no contract or mechanism."
  },
  {
   "id": "R33",
   "matches": [],
   "reason": "Lists OT defect numbers from revision history by topic only without stating the contract and mechanism of any sealed bug E1\u2013E7."
  },
  {
   "id": "R34",
   "matches": [],
   "reason": "Comments only on the unknown default write-cache setting of Seagate ST1239NS and IBM 0661 drives for scoring, without stating sealed E2's contract or mechanism."
  },
  {
   "id": "R35",
   "matches": [],
   "reason": "Contains only `git status` output with no contract or mechanism."
  },
  {
   "id": "R36",
   "matches": [],
   "reason": "Contains only directory listing output with no contract or mechanism."
  },
  {
   "id": "R37",
   "matches": [],
   "reason": "Contains only an `ls -R` header with no contract or mechanism."
  },
  {
   "id": "R38",
   "matches": [],
   "reason": "Contains only a markdown code fence with no contract or mechanism."
  },
  {
   "id": "R39",
   "matches": [],
   "reason": "Describes compile option DB 3189 in `tran.c` for synchronous metadata commits, which does not match any of sealed E1\u2013E7."
  },
  {
   "id": "R40",
   "matches": [],
   "reason": "Contains only an `ls -R` command string with no contract or mechanism."
  },
  {
   "id": "R41",
   "matches": [],
   "reason": "States only a contract count (\"Contract count: 68.\") with no contract or mechanism."
  },
  {
   "id": "R42",
   "matches": [],
   "reason": "Lists internal `logbuf` issues (unknown checksum versions, unchecksummed restart page, compiled-out asserts, `elbb_FastModify`, recovery threading comment, and `MAX_TRAN_SIZE` comment) that do not match sealed E1\u2013E7."
  },
  {
   "id": "R43",
   "matches": [],
   "reason": "Describes OT 4548 regarding fixed transaction reservation size being too small for callers, which does not match any of sealed E1\u2013E7."
  },
  {
   "id": "R44",
   "matches": [],
   "reason": "Contains only `git status` output with no contract or mechanism."
  },
  {
   "id": "R45",
   "matches": [],
   "reason": "States only a contract count (\"50 contracts, E1 through E50.\") with no contract or mechanism."
  },
  {
   "id": "R46",
   "matches": [],
   "reason": "Discusses unverified log length bounds, 16-bit offsets, and `MAX_TRAN_SIZE` comments without stating any sealed E1\u2013E7 bug mechanism."
  },
  {
   "id": "R47",
   "matches": [],
   "reason": "Notes that `NewLogPage` ignores `asevent_QueueIO`'s return value while marking the log page in transit, which does not match sealed E1\u2013E7."
  },
  {
   "id": "R48",
   "matches": [],
   "reason": "Contains only a `git status` label with no contract or mechanism."
  },
  {
   "id": "R49",
   "matches": [],
   "reason": "Notes that recovery accepts an unknown checksum version as valid, which does not match any of sealed E1\u2013E7."
  },
  {
   "id": "R50",
   "matches": [],
   "reason": "Contains only `git status` output with no contract or mechanism."
  },
  {
   "id": "R51",
   "matches": [],
   "reason": "Discusses `efs_MakeWritableBlocks` dirty zero pages, mentions OT 5527 as a pass-number bug without stating sealed E6 or E7's mechanism, and notes unknown SCSI write-back cache frequency."
  },
  {
   "id": "R52",
   "matches": [],
   "reason": "Describes `elbb_SyncForce` and `elbb_StartTran` giving up early during a kernel panic, which does not match any of sealed E1\u2013E7."
  },
  {
   "id": "R53",
   "matches": [],
   "reason": "Contains only directory listing output with no contract or mechanism."
  },
  {
   "id": "R54",
   "matches": [],
   "reason": "Mentions OT numbers by topic and calls \"Volatile write-cache acknowledgements\" a familiar pattern, without stating the durable-write contract and post-acknowledgement loss/ordering mechanism of sealed E2, E3, or E5."
  },
  {
   "id": "R55",
   "matches": [],
   "reason": "Contains only `git status` output with no contract or mechanism."
  },
  {
   "id": "R56",
   "matches": [],
   "reason": "Mentions \"pass-number comparison work named as OT 5527\" as an internal log bug without stating sealed E7's slot-0 restart and unrewritten far-slot mechanism."
  },
  {
   "id": "R57",
   "matches": [],
   "reason": "States only a contract count (\"Contracts: 74.\") with no contract or mechanism."
  },
  {
   "id": "R58",
   "matches": [],
   "reason": "Summarizes general design boundaries around the in-transit window, sector atomicity, and truthful completion without stating any sealed E1\u2013E7 failure mechanism."
  },
  {
   "id": "R59",
   "matches": [],
   "reason": "Contains only a `git status` header with no contract or mechanism."
  },
  {
   "id": "R60",
   "matches": [],
   "reason": "Describes OT 3802 regarding a missing `tlock` on a fileset path failing to merge equivalence classes, which does not match any of sealed E1\u2013E7."
  }
 ]
}

===== GLM ruling (beside): rows (ruling.json) =====
{
 "rows": [
  {
   "id": "R01",
   "matches": [],
   "reason": "Torn-page/out-of-order sector writes with checksums is a different mechanism from sealed E3's undo-record-still-in-cache mechanism, though it names the same durability contract."
  },
  {
   "id": "R02",
   "matches": [],
   "reason": "Noise (a filename), no contract or mechanism."
  },
  {
   "id": "R03",
   "matches": [],
   "reason": "git status noise."
  },
  {
   "id": "R04",
   "matches": [
    "E2"
   ],
   "reason": "Same contract (completed write durable) and same mechanism (volatile write-back cache losing an acknowledged page at power failure)."
  },
  {
   "id": "R05",
   "matches": [],
   "reason": "New-block exposure after allocation-before-first-write is a different mechanism from sealed E5's undo-zero record lost in a volatile cache, and it cites a different contract (E36/E38)."
  },
  {
   "id": "R06",
   "matches": [],
   "reason": "Undo-zero not implemented is an implementation gap, not sealed E5's mechanism of a completed undo write lost to a volatile cache."
  },
  {
   "id": "R07",
   "matches": [],
   "reason": "git status noise."
  },
  {
   "id": "R08",
   "matches": [],
   "reason": "Mount-path failure to recover a dirty log (E17/OT 3338) is not any sealed bug."
  },
  {
   "id": "R09",
   "matches": [],
   "reason": "git status noise."
  },
  {
   "id": "R10",
   "matches": [],
   "reason": "A question about whether an undo-zero comment is stale is not a sealed bug's contract-and-mechanism pair."
  },
  {
   "id": "R11",
   "matches": [],
   "reason": "An undecided safety question about block-0 inspection under out-of-order completion states no violation; it does not assert sealed E1's count-vs-distance mechanism."
  },
  {
   "id": "R12",
   "matches": [],
   "reason": "Truncated note, no content."
  },
  {
   "id": "R13",
   "matches": [
    "E2"
   ],
   "reason": "Same contract and mechanism as sealed E2: write-back cache acknowledges before media, page lost at power failure."
  },
  {
   "id": "R14",
   "matches": [],
   "reason": "Directory listing noise."
  },
  {
   "id": "R15",
   "matches": [],
   "reason": "Directory listing noise."
  },
  {
   "id": "R16",
   "matches": [],
   "reason": "Contract count only."
  },
  {
   "id": "R17",
   "matches": [],
   "reason": "Internal logbuf implementation concerns (disabled asserts, unchecked checksum types, undo-zero path) are 'own' observations, none matching a sealed bug's contract and mechanism."
  },
  {
   "id": "R18",
   "matches": [],
   "reason": "Command listing noise."
  },
  {
   "id": "R19",
   "matches": [],
   "reason": "Truncated heading, no contract or mechanism."
  },
  {
   "id": "R20",
   "matches": [],
   "reason": "elbb_UndoZero loop and reservation observations are logbuf-own defects, not any sealed bug."
  },
  {
   "id": "R21",
   "matches": [],
   "reason": "Pass-number wrap requiring a lost write is a different mechanism from sealed E7's slot-0 restart leaving far slots unrewritten, and the row leaves it out as no violation."
  },
  {
   "id": "R22",
   "matches": [],
   "reason": "Directory listing noise."
  },
  {
   "id": "R23",
   "matches": [],
   "reason": "Directory listing noise."
  },
  {
   "id": "R24",
   "matches": [],
   "reason": "git status noise."
  },
  {
   "id": "R25",
   "matches": [],
   "reason": "Un-checksummed restart pages handled by checkpoint-then-restart is not a sealed bug; it only references E3."
  },
  {
   "id": "R26",
   "matches": [],
   "reason": "Inventory note, no contract or mechanism."
  },
  {
   "id": "R27",
   "matches": [],
   "reason": "git status noise."
  },
  {
   "id": "R28",
   "matches": [],
   "reason": "Qualification of performance and detection claims, no bug."
  },
  {
   "id": "R29",
   "matches": [],
   "reason": "elbr_Recover panicking on SafeDumpLog error is a logbuf-own defect not in the sealed list."
  },
  {
   "id": "R30",
   "matches": [],
   "reason": "Directory listing noise."
  },
  {
   "id": "R31",
   "matches": [],
   "reason": "Directory listing noise."
  },
  {
   "id": "R32",
   "matches": [],
   "reason": "Process disclaimer, no contract or mechanism."
  },
  {
   "id": "R33",
   "matches": [],
   "reason": "Explicitly recalls no specific incident; lists source-history OT numbers without a mechanism matching a sealed bug."
  },
  {
   "id": "R34",
   "matches": [],
   "reason": "A scoring judgment about E2's frequency, not a finding with a mechanism."
  },
  {
   "id": "R35",
   "matches": [],
   "reason": "git status noise."
  },
  {
   "id": "R36",
   "matches": [],
   "reason": "Directory listing noise."
  },
  {
   "id": "R37",
   "matches": [],
   "reason": "Command listing noise."
  },
  {
   "id": "R38",
   "matches": [],
   "reason": "Empty code fence."
  },
  {
   "id": "R39",
   "matches": [],
   "reason": "DB 3189 optional commit-before-return in tran.c is not a sealed bug."
  },
  {
   "id": "R40",
   "matches": [],
   "reason": "Command listing noise."
  },
  {
   "id": "R41",
   "matches": [],
   "reason": "Contract count only."
  },
  {
   "id": "R42",
   "matches": [],
   "reason": "Internal logbuf defects (checksum version, restart page, asserts, FastModify) are 'own' issues not in the sealed list."
  },
  {
   "id": "R43",
   "matches": [],
   "reason": "OT 4548 reservation-size fix (E29/E30) is not any sealed bug."
  },
  {
   "id": "R44",
   "matches": [],
   "reason": "git status noise."
  },
  {
   "id": "R45",
   "matches": [],
   "reason": "Contract count only."
  },
  {
   "id": "R46",
   "matches": [],
   "reason": "Limits and constants discussion, no sealed bug."
  },
  {
   "id": "R47",
   "matches": [],
   "reason": "NewLogPage ignoring asevent_QueueIO's return is a logbuf-own defect, not a sealed bug."
  },
  {
   "id": "R48",
   "matches": [],
   "reason": "git status noise."
  },
  {
   "id": "R49",
   "matches": [],
   "reason": "Unknown checksum version accepted is an internal recover.c defect, not in the sealed list."
  },
  {
   "id": "R50",
   "matches": [],
   "reason": "git status noise."
  },
  {
   "id": "R51",
   "matches": [],
   "reason": "Undecided points about E36/E38, OT 5527 and E2 frequency; no asserted mechanism matching a sealed bug."
  },
  {
   "id": "R52",
   "matches": [],
   "reason": "Panic-path SyncForce/StartTran behaviour is a logbuf-own defect, not a sealed bug."
  },
  {
   "id": "R53",
   "matches": [],
   "reason": "Directory listing noise."
  },
  {
   "id": "R54",
   "matches": [],
   "reason": "Explicitly no independent recall; source-history OT numbers without a matching mechanism."
  },
  {
   "id": "R55",
   "matches": [],
   "reason": "git status noise."
  },
  {
   "id": "R56",
   "matches": [],
   "reason": "OT 5527 pass-number comparison bug is a different mechanism from sealed E7's slot-0 restart/masked head comparison, and the row classifies it as internal, not environment."
  },
  {
   "id": "R57",
   "matches": [],
   "reason": "Contract count only."
  },
  {
   "id": "R58",
   "matches": [],
   "reason": "Statement of design assumptions (no whole-page atomicity assumed), not a bug."
  },
  {
   "id": "R59",
   "matches": [],
   "reason": "git status noise."
  },
  {
   "id": "R60",
   "matches": [],
   "reason": "OT 3802 missing tlock (E32) is not any sealed bug."
  }
 ]
}

===== Episode README for its rulings (its summary, packet defects, correction) (README.md) =====
# episode's rulings on tupay D2 phase 3

Judge: episode's steward (Claude Opus 5.5), 2026-11-01. Ruled against
`sealed/2026-10-27-tupay-D2-findings-v2.md` (`b30107c`) using the criteria fixed
on 2026-10-26 (`docs/requests/2026-10-26-to-tupay-D2-answers.md` §4), including
v2's advance rule for E7. One file per packet, in each packet's schema.

Packets: `tupay/experiments/D2/phase3/packets/` at `a86ea00`. All five were
verified against `packets.sha256` before reading. I did **not** read
`tupay/experiments/D2/phase3/judges/` or the mapping.

## Summary

| packet | result |
|---|---|
| findings (10) | **1 match** (F03 → E6); **2 partial** (F07 → E6; F08 → E3); 7 no match; 0 flagged; 0 unresolved |
| cells (110) | **10** name a sealed bug's violated contract: E4 in 7 (C001, C018, C041, C060, C071, C077, C108); E2/E3/E5 in C019 and C078; E2/E3 in C107. No cell names a contract for E1, E6 or E7, which v2 classes as logbuf's own defects |
| rows (60) | **2** match (R04, R13 → E2, both general write-cache knowledge, not leakage). R11 points at E6's location without a mechanism. R21 disputes E7's premise. 32 rows are captured shell output or headings, not claims |

Sealed bugs reached by a finding, at match or partial: E6 (by two) and E3. Not reached:
E1, E2, E4, E5, E7.

## Packet defects (reported, not fixed)

1. **rows.md: 32 of 60 rows are not claims.** They are git status output, `ls`
   listings, counts and section headings captured from the reports (R02, R03,
   R07, R09, R12, R14–R16, R18, R19, R22–R24, R26, R27, R30–R32, R35–R38, R40,
   R41, R44, R45, R48, R50, R53, R55, R57, R59). Ruled "no" with that reason. The
   extraction rule seems to take every paragraph of a report.
2. **findings.md, F10** says "same mechanism as F-draft-1", which links F10 to
   F05's author (both are marked `author_status: draft`). That is a small hole in
   the opaque ids.
3. `{SEALED_WHERE}` is unexpanded in all five packets, as the request warned.

## Correction to the sealed file's history claim (an error of mine)

v1 and v2 say that DCE 1.2.2's RCS logs hold only OSF merge housekeeping and that
"Transarc's internal history is not in the release". **That is false.** Transarc
delta comments survive in `logbuf/logbuf-locking`, in the test scripts
(`logbuf/*.test`, `anode/passno*.test`) and in `crc.c`. OT/DB numbers also appear
in `log.c`, `tran.c`, `buffer.c` and `elb.h`. I checked only the `$Log` blocks of
the C files. The enumerators' rows (R01, R33, R51, R56) cited this history, and
that's how I found the error.

After reading those entries, **the count is unchanged: none describes E1–E7.**
Two are in the same area:
- **OT 5527** (`anode/passno.test`): "Initialize and shutdown a log enough times
  so that a log with a zero pass # results." This is a pass number reaching zero
  across repeated mounts. It's E7's area (pass numbers across mounts) but a
  different defect from E7's masked-comparison aliasing.
- The **RecycleLogBufs fix** (`logbuf-locking`, 1992-11): "reporting a more
  recent value for activeLogBlock than was correct if the members of the
  inTransit list were within 5 blocks of the end of the log". This is a
  wrap-around error in `activeLogBlock`. It's in the area of E1 (which
  `activeLogBlock` would repair) and of F01, but it's neither.

I have not read every Transarc delta comment in the tree, only those under
`logbuf/` and the pass-number tests. The sealed files stay as committed. This
section and the steward log carry the correction.

## Still to do, after these rulings are committed (tupay's request, item 3)

- Score the sealed prediction (`2a578fa4…`).
- Take second looks, reported as findings against the analysis: F07 (disputes the
  sealed note that the recovery path's +2 bump is safe), F06 (may lie outside
  EpisodeLog's "sealed once" page abstraction), and F01, F02, F04, F09, R20 and
  R47 (claims of defects the analysis did not list).


===== the scoring script (d2-score.py) =====
#!/usr/bin/env python3
"""Score D2 phase 3 by the registration (experiments/D2/design.md, "Predictions for phase 3").

Written by the eleventh steward 2026-11-03 and committed before its first run. Rules, each from
the design or the log, and nowhere else:

Judges (log 2026-10-27 18:40Z, 2026-10-29 06:23Z and 06:26Z): Episode (judges/episode/<packet>.json)
and Gemini (judges/<packet>/gemini/ruling.json) are registered; a prediction holds only if it
holds under both. GLM (judges/<packet>/glm-2/ruling.json, its one rerun) is reported beside.
Gemini has no registered ruling on cells-2 (both runs failed to parse); its mechanical repair
(gemini-2/ruling-repaired-beside.json) is reported beside, never as the registered ruling. Under
Gemini, the registered cell outcomes therefore come from cells-1 and cells-3 only, stated as such.

Denominators (design; log 2026-10-29 05:31Z): Episode's answer came after phase 0, so the scored
denominator is all seven sealed bugs (E1-E7); the four environment-contract bugs (E2-E5) are
reported beside. Comment split from the sealed file v2's own counts: comment E2, E3, E5, E6;
no comment E1, E4, E7 (beside: comment E2, E3, E5; none E4).

D2-1  fraction of denominator bugs whose contract some cell names: comment group > no-comment
      group, strictly.
D2-2  at least one sealed bug is a "match" among the scored findings of at least one model
      author. D2-2g beside: Grok's authors only. A Recognised row (kind "recognised") matching
      a sealed bug is a leakage flag and voids D2-2 for that enumerator family's lists; reported.
D2-3  in each family separately, condition C's scored findings reach (match or partial) more
      distinct sealed bugs than condition N's. One prediction "in each family": holds only if
      it holds for both families.
D2-4  at least four denominator bugs have their contract named by some cell (if the
      denominator is under five, all but one).
D2-5  Claude C reaches (match or partial) more distinct sealed bugs than Grok C.
P0-4  (phase 0, judged here) at least one Recognised row names a sealed bug.
Precision per author: findings judged match, and match or partial, over scored findings; both
are reported, neither is chosen as primary (the design says "matched").
A finding matching several bugs counts for each (design).
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "experiments/D2/phase3"
J = ROOT / "judges"
ALL7 = ["E1", "E2", "E3", "E4", "E5", "E6", "E7"]
ENV4 = ["E2", "E3", "E4", "E5"]
COMMENT = {"E2", "E3", "E5", "E6"}
AUTHORS = ["model-c-claude", "model-n-claude", "model-c-grok", "model-n-grok"]
CELL_PACKETS = ["cells-1", "cells-2", "cells-3"]


def load(p):
    return json.load(open(p))


def ruling(judge, packet, beside_repair=False):
    """Return the parsed ruling list for (judge, packet), or None if there is no ruling."""
    if judge == "episode":
        p = J / "episode" / f"{packet}.json"
    elif judge == "gemini":
        if packet == "cells-2":
            if not beside_repair:
                return None
            p = J / "cells-2" / "gemini-2" / "ruling-repaired-beside.json"
        else:
            p = J / packet / "gemini" / "ruling.json"
    elif judge == "glm":
        p = J / packet / "glm-2" / "ruling.json"
    key = "cells" if packet.startswith("cells") else packet
    return load(p)[key]


def cells_named(judge, beside_repair=False):
    named, missing = set(), []
    for pk in CELL_PACKETS:
        r = ruling(judge, pk, beside_repair)
        if r is None:
            missing.append(pk)
            continue
        for c in r:
            named.update(c.get("names_contract_of") or [])
    return named, missing


def frac(bugs, named):
    return sum(b in named for b in bugs), len(bugs)


def score(judge, mapping, beside_repair=False):
    out = {"judge": judge, "beside_repair": beside_repair}
    # cells
    named, missing = cells_named(judge, beside_repair)
    out["cells_missing_packets"] = missing
    out["bugs_named_by_cells"] = sorted(named)
    for label, den in (("seven", ALL7), ("env4", ENV4)):
        c = [b for b in den if b in COMMENT]
        n = [b for b in den if b not in COMMENT]
        fc, fn = frac(c, named), frac(n, named)
        d21 = (fc[0] / fc[1]) > (fn[0] / fn[1]) if fc[1] and fn[1] else None
        k = sum(b in named for b in den)
        need = 4 if len(den) >= 5 else len(den) - 1
        out[f"D2-1[{label}]"] = {"comment": fc, "no_comment": fn, "holds": d21}
        out[f"D2-4[{label}]"] = {"named": k, "of": len(den), "need": need, "holds": k >= need}
    # findings
    fr = {f["id"]: f for f in ruling(judge, "findings")}
    per = {a: {"scored": 0, "match": 0, "match_or_partial": 0, "bugs_match": set(), "bugs_reach": set(),
               "flagged_confirmed_property": 0} for a in AUTHORS}
    for fid, meta in mapping["findings"].items():
        if not meta.get("scored"):
            continue
        a, r = meta["author"], fr[fid]
        p = per[a]
        p["scored"] += 1
        bugs = r.get("bugs") or []
        if r["ruling"] == "match":
            p["match"] += 1
            p["bugs_match"].update(bugs)
        if r["ruling"] in ("match", "partial"):
            p["match_or_partial"] += 1
            p["bugs_reach"].update(bugs)
        if r.get("flag_confirmed_property"):
            p["flagged_confirmed_property"] += 1
    out["per_author"] = {a: {**{k: v for k, v in p.items() if not isinstance(v, set)},
                             "bugs_match": sorted(p["bugs_match"]), "bugs_reach": sorted(p["bugs_reach"]),
                             "precision_match": f"{p['match']}/{p['scored']}",
                             "precision_match_or_partial": f"{p['match_or_partial']}/{p['scored']}"}
                         for a, p in per.items()}
    # rows: found by reading, leakage
    rr = {r["id"]: r for r in ruling(judge, "rows")}
    found, leak = [], []
    for rid, meta in mapping["rows"].items():
        m = rr[rid].get("matches") or []
        if m:
            found.append({"row": rid, "kind": meta["kind"], "enumerator": meta["enumerator"], "bugs": m})
            if meta["kind"] == "recognised":
                leak.append({"row": rid, "enumerator": meta["enumerator"], "bugs": m})
    out["rows_found_by_reading"] = found
    out["leakage_flags"] = leak
    leak_fams = {l["enumerator"].split("-")[0] for l in leak}
    out["P0-4"] = {"holds": bool(leak), "recognised_rows_matching": leak}
    # D2-2: voided for a family whose enumeration lists leaked
    fam = lambda a: a.split("-")[-1]
    def any_match(authors):
        return any(per[a]["match"] > 0 for a in authors)
    out["D2-2"] = {"holds": any_match(AUTHORS), "voided_for_families_with_leakage": sorted(leak_fams)}
    out["D2-2g"] = {"holds": any_match(["model-c-grok", "model-n-grok"])}
    d23 = {}
    for f in ("claude", "grok"):
        c, n = len(per[f"model-c-{f}"]["bugs_reach"]), len(per[f"model-n-{f}"]["bugs_reach"])
        d23[f] = {"C": c, "N": n, "holds": c > n}
    out["D2-3"] = {**d23, "holds": all(v["holds"] for v in d23.values())}
    cc, gc = len(per["model-c-claude"]["bugs_reach"]), len(per["model-c-grok"]["bugs_reach"])
    out["D2-5"] = {"claude_C": cc, "grok_C": gc, "holds": cc > gc}
    return out


def main():
    mapping = load(ROOT / "mapping.json")
    res = {"registered": [score("episode", mapping), score("gemini", mapping)],
           "beside": [score("gemini", mapping, beside_repair=True), score("glm", mapping)]}
    preds = ["D2-1[seven]", "D2-2", "D2-3", "D2-4[seven]", "D2-5", "P0-4"]
    verdict = {}
    for p in preds:
        e, g = (r[p]["holds"] for r in res["registered"])
        verdict[p] = {"episode": e, "gemini": g, "holds_under_both": bool(e and g)}
    res["verdict"] = verdict
    json.dump(res, sys.stdout, indent=1, default=sorted)
    print()


if __name__ == "__main__":
    main()


===== the script output (score.json) =====
{
 "registered": [
  {
   "judge": "episode",
   "beside_repair": false,
   "cells_missing_packets": [],
   "bugs_named_by_cells": [
    "E2",
    "E3",
    "E4",
    "E5"
   ],
   "D2-1[seven]": {
    "comment": [
     3,
     4
    ],
    "no_comment": [
     1,
     3
    ],
    "holds": true
   },
   "D2-4[seven]": {
    "named": 4,
    "of": 7,
    "need": 4,
    "holds": true
   },
   "D2-1[env4]": {
    "comment": [
     3,
     3
    ],
    "no_comment": [
     1,
     1
    ],
    "holds": false
   },
   "D2-4[env4]": {
    "named": 4,
    "of": 4,
    "need": 3,
    "holds": true
   },
   "per_author": {
    "model-c-claude": {
     "scored": 2,
     "match": 0,
     "match_or_partial": 0,
     "flagged_confirmed_property": 0,
     "bugs_match": [],
     "bugs_reach": [],
     "precision_match": "0/2",
     "precision_match_or_partial": "0/2"
    },
    "model-n-claude": {
     "scored": 3,
     "match": 1,
     "match_or_partial": 2,
     "flagged_confirmed_property": 0,
     "bugs_match": [
      "E6"
     ],
     "bugs_reach": [
      "E6"
     ],
     "precision_match": "1/3",
     "precision_match_or_partial": "2/3"
    },
    "model-c-grok": {
     "scored": 5,
     "match": 0,
     "match_or_partial": 1,
     "flagged_confirmed_property": 0,
     "bugs_match": [],
     "bugs_reach": [
      "E3"
     ],
     "precision_match": "0/5",
     "precision_match_or_partial": "1/5"
    },
    "model-n-grok": {
     "scored": 0,
     "match": 0,
     "match_or_partial": 0,
     "flagged_confirmed_property": 0,
     "bugs_match": [],
     "bugs_reach": [],
     "precision_match": "0/0",
     "precision_match_or_partial": "0/0"
    }
   },
   "rows_found_by_reading": [
    {
     "row": "R04",
     "kind": "recognised",
     "enumerator": "grok-2",
     "bugs": [
      "E2"
     ]
    },
    {
     "row": "R13",
     "kind": "recognised",
     "enumerator": "grok-1",
     "bugs": [
      "E2"
     ]
    }
   ],
   "leakage_flags": [
    {
     "row": "R04",
     "enumerator": "grok-2",
     "bugs": [
      "E2"
     ]
    },
    {
     "row": "R13",
     "enumerator": "grok-1",
     "bugs": [
      "E2"
     ]
    }
   ],
   "P0-4": {
    "holds": true,
    "recognised_rows_matching": [
     {
      "row": "R04",
      "enumerator": "grok-2",
      "bugs": [
       "E2"
      ]
     },
     {
      "row": "R13",
      "enumerator": "grok-1",
      "bugs": [
       "E2"
      ]
     }
    ]
   },
   "D2-2": {
    "holds": true,
    "voided_for_families_with_leakage": [
     "grok"
    ]
   },
   "D2-2g": {
    "holds": false
   },
   "D2-3": {
    "claude": {
     "C": 0,
     "N": 1,
     "holds": false
    },
    "grok": {
     "C": 1,
     "N": 0,
     "holds": true
    },
    "holds": false
   },
   "D2-5": {
    "claude_C": 0,
    "grok_C": 1,
    "holds": false
   }
  },
  {
   "judge": "gemini",
   "beside_repair": false,
   "cells_missing_packets": [
    "cells-2"
   ],
   "bugs_named_by_cells": [
    "E2",
    "E3",
    "E4",
    "E5"
   ],
   "D2-1[seven]": {
    "comment": [
     3,
     4
    ],
    "no_comment": [
     1,
     3
    ],
    "holds": true
   },
   "D2-4[seven]": {
    "named": 4,
    "of": 7,
    "need": 4,
    "holds": true
   },
   "D2-1[env4]": {
    "comment": [
     3,
     3
    ],
    "no_comment": [
     1,
     1
    ],
    "holds": false
   },
   "D2-4[env4]": {
    "named": 4,
    "of": 4,
    "need": 3,
    "holds": true
   },
   "per_author": {
    "model-c-claude": {
     "scored": 2,
     "match": 0,
     "match_or_partial": 1,
     "flagged_confirmed_property": 0,
     "bugs_match": [],
     "bugs_reach": [
      "E2"
     ],
     "precision_match": "0/2",
     "precision_match_or_partial": "1/2"
    },
    "model-n-claude": {
     "scored": 3,
     "match": 1,
     "match_or_partial": 2,
     "flagged_confirmed_property": 0,
     "bugs_match": [
      "E6"
     ],
     "bugs_reach": [
      "E6"
     ],
     "precision_match": "1/3",
     "precision_match_or_partial": "2/3"
    },
    "model-c-grok": {
     "scored": 5,
     "match": 2,
     "match_or_partial": 2,
     "flagged_confirmed_property": 0,
     "bugs_match": [
      "E2",
      "E3"
     ],
     "bugs_reach": [
      "E2",
      "E3"
     ],
     "precision_match": "2/5",
     "precision_match_or_partial": "2/5"
    },
    "model-n-grok": {
     "scored": 0,
     "match": 0,
     "match_or_partial": 0,
     "flagged_confirmed_property": 0,
     "bugs_match": [],
     "bugs_reach": [],
     "precision_match": "0/0",
     "precision_match_or_partial": "0/0"
    }
   },
   "rows_found_by_reading": [
    {
     "row": "R04",
     "kind": "recognised",
     "enumerator": "grok-2",
     "bugs": [
      "E2"
     ]
    },
    {
     "row": "R13",
     "kind": "recognised",
     "enumerator": "grok-1",
     "bugs": [
      "E2"
     ]
    }
   ],
   "leakage_flags": [
    {
     "row": "R04",
     "enumerator": "grok-2",
     "bugs": [
      "E2"
     ]
    },
    {
     "row": "R13",
     "enumerator": "grok-1",
     "bugs": [
      "E2"
     ]
    }
   ],
   "P0-4": {
    "holds": true,
    "recognised_rows_matching": [
     {
      "row": "R04",
      "enumerator": "grok-2",
      "bugs": [
       "E2"
      ]
     },
     {
      "row": "R13",
      "enumerator": "grok-1",
      "bugs": [
       "E2"
      ]
     }
    ]
   },
   "D2-2": {
    "holds": true,
    "voided_for_families_with_leakage": [
     "grok"
    ]
   },
   "D2-2g": {
    "holds": true
   },
   "D2-3": {
    "claude": {
     "C": 1,
     "N": 1,
     "holds": false
    },
    "grok": {
     "C": 2,
     "N": 0,
     "holds": true
    },
    "holds": false
   },
   "D2-5": {
    "claude_C": 1,
    "grok_C": 2,
    "holds": false
   }
  }
 ],
 "beside": [
  {
   "judge": "gemini",
   "beside_repair": true,
   "cells_missing_packets": [],
   "bugs_named_by_cells": [
    "E2",
    "E3",
    "E4",
    "E5"
   ],
   "D2-1[seven]": {
    "comment": [
     3,
     4
    ],
    "no_comment": [
     1,
     3
    ],
    "holds": true
   },
   "D2-4[seven]": {
    "named": 4,
    "of": 7,
    "need": 4,
    "holds": true
   },
   "D2-1[env4]": {
    "comment": [
     3,
     3
    ],
    "no_comment": [
     1,
     1
    ],
    "holds": false
   },
   "D2-4[env4]": {
    "named": 4,
    "of": 4,
    "need": 3,
    "holds": true
   },
   "per_author": {
    "model-c-claude": {
     "scored": 2,
     "match": 0,
     "match_or_partial": 1,
     "flagged_confirmed_property": 0,
     "bugs_match": [],
     "bugs_reach": [
      "E2"
     ],
     "precision_match": "0/2",
     "precision_match_or_partial": "1/2"
    },
    "model-n-claude": {
     "scored": 3,
     "match": 1,
     "match_or_partial": 2,
     "flagged_confirmed_property": 0,
     "bugs_match": [
      "E6"
     ],
     "bugs_reach": [
      "E6"
     ],
     "precision_match": "1/3",
     "precision_match_or_partial": "2/3"
    },
    "model-c-grok": {
     "scored": 5,
     "match": 2,
     "match_or_partial": 2,
     "flagged_confirmed_property": 0,
     "bugs_match": [
      "E2",
      "E3"
     ],
     "bugs_reach": [
      "E2",
      "E3"
     ],
     "precision_match": "2/5",
     "precision_match_or_partial": "2/5"
    },
    "model-n-grok": {
     "scored": 0,
     "match": 0,
     "match_or_partial": 0,
     "flagged_confirmed_property": 0,
     "bugs_match": [],
     "bugs_reach": [],
     "precision_match": "0/0",
     "precision_match_or_partial": "0/0"
    }
   },
   "rows_found_by_reading": [
    {
     "row": "R04",
     "kind": "recognised",
     "enumerator": "grok-2",
     "bugs": [
      "E2"
     ]
    },
    {
     "row": "R13",
     "kind": "recognised",
     "enumerator": "grok-1",
     "bugs": [
      "E2"
     ]
    }
   ],
   "leakage_flags": [
    {
     "row": "R04",
     "enumerator": "grok-2",
     "bugs": [
      "E2"
     ]
    },
    {
     "row": "R13",
     "enumerator": "grok-1",
     "bugs": [
      "E2"
     ]
    }
   ],
   "P0-4": {
    "holds": true,
    "recognised_rows_matching": [
     {
      "row": "R04",
      "enumerator": "grok-2",
      "bugs": [
       "E2"
      ]
     },
     {
      "row": "R13",
      "enumerator": "grok-1",
      "bugs": [
       "E2"
      ]
     }
    ]
   },
   "D2-2": {
    "holds": true,
    "voided_for_families_with_leakage": [
     "grok"
    ]
   },
   "D2-2g": {
    "holds": true
   },
   "D2-3": {
    "claude": {
     "C": 1,
     "N": 1,
     "holds": false
    },
    "grok": {
     "C": 2,
     "N": 0,
     "holds": true
    },
    "holds": false
   },
   "D2-5": {
    "claude_C": 1,
    "grok_C": 2,
    "holds": false
   }
  },
  {
   "judge": "glm",
   "beside_repair": false,
   "cells_missing_packets": [],
   "bugs_named_by_cells": [
    "E2",
    "E3",
    "E4"
   ],
   "D2-1[seven]": {
    "comment": [
     2,
     4
    ],
    "no_comment": [
     1,
     3
    ],
    "holds": true
   },
   "D2-4[seven]": {
    "named": 3,
    "of": 7,
    "need": 4,
    "holds": false
   },
   "D2-1[env4]": {
    "comment": [
     2,
     3
    ],
    "no_comment": [
     1,
     1
    ],
    "holds": false
   },
   "D2-4[env4]": {
    "named": 3,
    "of": 4,
    "need": 3,
    "holds": true
   },
   "per_author": {
    "model-c-claude": {
     "scored": 2,
     "match": 0,
     "match_or_partial": 0,
     "flagged_confirmed_property": 0,
     "bugs_match": [],
     "bugs_reach": [],
     "precision_match": "0/2",
     "precision_match_or_partial": "0/2"
    },
    "model-n-claude": {
     "scored": 3,
     "match": 1,
     "match_or_partial": 1,
     "flagged_confirmed_property": 0,
     "bugs_match": [
      "E6"
     ],
     "bugs_reach": [
      "E6"
     ],
     "precision_match": "1/3",
     "precision_match_or_partial": "1/3"
    },
    "model-c-grok": {
     "scored": 5,
     "match": 0,
     "match_or_partial": 0,
     "flagged_confirmed_property": 0,
     "bugs_match": [],
     "bugs_reach": [],
     "precision_match": "0/5",
     "precision_match_or_partial": "0/5"
    },
    "model-n-grok": {
     "scored": 0,
     "match": 0,
     "match_or_partial": 0,
     "flagged_confirmed_property": 0,
     "bugs_match": [],
     "bugs_reach": [],
     "precision_match": "0/0",
     "precision_match_or_partial": "0/0"
    }
   },
   "rows_found_by_reading": [
    {
     "row": "R04",
     "kind": "recognised",
     "enumerator": "grok-2",
     "bugs": [
      "E2"
     ]
    },
    {
     "row": "R13",
     "kind": "recognised",
     "enumerator": "grok-1",
     "bugs": [
      "E2"
     ]
    }
   ],
   "leakage_flags": [
    {
     "row": "R04",
     "enumerator": "grok-2",
     "bugs": [
      "E2"
     ]
    },
    {
     "row": "R13",
     "enumerator": "grok-1",
     "bugs": [
      "E2"
     ]
    }
   ],
   "P0-4": {
    "holds": true,
    "recognised_rows_matching": [
     {
      "row": "R04",
      "enumerator": "grok-2",
      "bugs": [
       "E2"
      ]
     },
     {
      "row": "R13",
      "enumerator": "grok-1",
      "bugs": [
       "E2"
      ]
     }
    ]
   },
   "D2-2": {
    "holds": true,
    "voided_for_families_with_leakage": [
     "grok"
    ]
   },
   "D2-2g": {
    "holds": false
   },
   "D2-3": {
    "claude": {
     "C": 0,
     "N": 1,
     "holds": false
    },
    "grok": {
     "C": 0,
     "N": 0,
     "holds": false
    },
    "holds": false
   },
   "D2-5": {
    "claude_C": 0,
    "grok_C": 0,
    "holds": false
   }
  }
 ],
 "verdict": {
  "D2-1[seven]": {
   "episode": true,
   "gemini": true,
   "holds_under_both": true
  },
  "D2-2": {
   "episode": true,
   "gemini": true,
   "holds_under_both": true
  },
  "D2-3": {
   "episode": false,
   "gemini": false,
   "holds_under_both": false
  },
  "D2-4[seven]": {
   "episode": true,
   "gemini": true,
   "holds_under_both": true
  },
  "D2-5": {
   "episode": false,
   "gemini": false,
   "holds_under_both": false
  },
  "P0-4": {
   "episode": true,
   "gemini": true,
   "holds_under_both": true
  }
 }
}


===== the draft result under review (D2-result.md) =====
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
