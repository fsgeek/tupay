# Audit of `docs/steward-practice.md`: method, mechanism, or caution (2026-11-18)

The thirteenth steward, acting on acceptance decision 4. Tony's counsel (2026-11-13): he "would be rather surprised if much of it wasn't an appended list of cautions dressed up as findings."

**Kinds.**
- **method:** the rule defines how tupay does its work. It is not a guard against a past error.
- **mechanism:** a caution that is now enforced by a script or check.
- **failed:** a caution kept in memory whose error recurred after the rule existed. The log entry is the evidence.
- **single:** a caution from one incident, with no mechanism and no recurrence on record.
- **superseded:** covered by another rule.

The "Line" column is the rule's line in `steward-practice.md` at commit `d7a51fe`.

| Line | Rule (short) | Kind | Evidence |
|---|---|---|---|
| 6 | Inputs are self-contained | method | |
| 7 | Read the inputs as an outsider would | method | every review since X2 found defects; the backup contract had 4 rounds, all with findings |
| 8 | Briefs are symmetric | method | |
| 9 | Briefs say unseen schedules may run | single | X2 error 7 |
| 10 | Briefs ask for declared limitations | method | |
| 11 | Checkouts from `setup-checkouts.sh` | mechanism | the script |
| 12 | Authors run sandboxed | mechanism | `author-sandbox.sh`, `sandbox-check.sh` |
| 13 | `inputcheck.sh` on every checkout | mechanism | the script and its mutation pair |
| 14 | Hold-outs by a third family, hashes only | method | |
| 15 | Shared schedules exercise every form | single | X2 error 6 |
| 16 | Every event trigger owed by a clause | single | P33 and P58, one preparation, 10-23; the lint is weaker than the rule |
| 17 | Needed reach generated from schedule text | mechanism | `reach-table.py` |
| 18 | The steward does not hand authors its hypotheses | **failed** | log L770 (10-25, a leak in the brief), L924 (10-26, a residue leak in the brief); 11-18, a steward hypothesis in draft 7 §8, author-facing, caught before any author |
| 20 | Credentials copied in, never bind-mounted | mechanism | `author-sandbox.sh` |
| 21 | Model authors run on the box | mechanism | `scripts/steward/box/` |
| 22 | Every box run gets a tracked watcher | single | 10-28 |
| 25 | Never edit a script a run is executing | **failed** | written after 10-25's D1 exits; recurred 10-26 (L940) |
| 26 | Do not touch a running author's checkout | **failed** | "host git never runs in an author checkout" since 10-23; recurred 10-27 (L999) |
| 27 | Hooks in linked worktrees are shared | single | |
| 33 | Search authors' READMEs for a check's name before judging | single | X3, 10-27 |
| 34 | Steward runs from scratch worktrees | method | |
| 35 | Divergences to a third-family judge; `agy` invocation | method | the `agy` detail is reference, not rule |
| 36 | Check the fairness rule against liveness PASSes | single | X2 result review |
| 37 | Ten repetitions per seed; flaky reported as such | method | the 10-21 diagnostic |
| 38 | Memory cap on any exploration | single | 10-21: the machine hung. Kept for its cost, not its frequency |
| 39 | Write times from the clock | superseded | by line 40 |
| 40 | A time only from `date -u` in the same command | mechanism | the command form. As a memory rule it failed four stewards in a row |
| 42 | Support audit before scoring a bounded check | method | the replay, 10-22 |
| 45 | Score at the registered moment only | method | |
| 46 | Measure 6 ruling | method | |
| 47 | Measure 7 raters blind to labels | method | |
| 48 | Non-steward review of scoring before publication | method | |
| 49 | Commit the evidence behind every number | method | |
| 52 | List a script-written directory before `git add` | single | 10-29 |
| 53 | Long processes through the tracked mechanism | **failed** | 10-21; recurred 11-01 (L1107, plant 4) |
| 54 | Log every error with its cost | method | its clock clause duplicates line 40 |
| 55 | Never rewrite committed history | method | |

**Counts (37 rules):**
- 16 method;
- 7 mechanism;
- **4 failed**;
- **9 single**;
- 1 superseded.

**Reading.** Tony's suspicion holds in part:
- **20 of the 37 began as cautions** (mechanism, failed, single and superseded).
- 7 earned a mechanism.
- 13 are still rules kept in memory, and **4 of those 13 demonstrably failed**.
- The method rules, which are the larger part, are not cautions. They are what makes tupay's evidence blind.

**Proposals** (to be applied after the W1 review is disposed of, and logged when applied):
1. **Each failed rule gets a mechanism or is admitted to be unenforced.**
   - 18: a scan of author-facing inputs for the steward's voice ("the steward expects", "we suspect", predictions), run by `inputcheck.sh`, beside W1's planned non-Claude leak review.
   - 25: launch scripts run from a copy taken at launch.
   - 26: a guard that refuses host `git` inside a directory marked as an author checkout.
   - 53: the session-start sweep lists author-run processes that no harness tracks.
2. **Single-incident cautions move to the point of use**, the procedure or script where they apply, out of the file a steward reads on arrival:
   - 9, 15, 16 and 36 into the brief and schedule checklists;
   - 22 into `box-launch.sh`, which can start its watcher itself;
   - 27 and 52 into the scripts they concern;
   - 33 into the judging procedure.

   38 stays where it is, because its cost is the machine. Nothing is deleted. Each moved rule leaves a one-line handle here.
3. **Line 39 is merged into 40**, and line 54's clock clause points to 40.
4. **START.md's entry ritual changes:** read the method rules and the mechanisms. Consult error entries when a task touches them (thirteenth's answer to Tony's question 6, 2026-11-13).
