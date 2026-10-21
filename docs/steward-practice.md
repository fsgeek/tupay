# Steward practice

How the steward runs a round, as of 2026-10-21 after X2. Each rule names the error that produced it. The log (`docs/seed-log.md`) is the history and outranks this file; this file is the current procedure, revised in place, with every revision logged.

## Before an author starts
- **Inputs are self-contained.** A versioned input restates what it depends on; it never says "as in v1" to an author who has no v1. (X1 Amendment B.)
- **Read the inputs as an outsider would.** Before registration, a non-steward family reviews the inputs for defects, and a second instance reviews the draft pre-registration adversarially. Fix what is found before registration; each round of fixes after hold-outs exist telegraphs them, so stop when that cost exceeds the benefit and record the rest as residues. (X2: thirteen input defects, six the steward's.)
- **Briefs are symmetric.** Every arm's brief carries the same candour sentence (an unmutated failure is a result; do not change the artifact to make it pass without naming the misread clause or cell) and, for model sides, the same fairness rule. (X2 error 1.)
- **Briefs say the steward may run unseen schedules**, under any name, so no artifact refuses them. (X2 error 7.)
- **Briefs ask authors to list declared limitations** in their report: shapes of schedule they believe their artifact would fail, and why they left them. (X2: the arm A model author declared H9's mechanism in advance, and nothing consumed it.)
- **Checkouts** come from `scripts/steward/setup-checkouts.sh`; include-list checkouts carry `scripts/hooks/`. (X2 error 4.)
- **Run `scripts/steward/inputcheck.sh` on every checkout** before its author starts: brief and named inputs present, nothing excluded present, no hold-out hash among the shared schedules, timestamp hook present, signing configured. (X1 Amendment C; X2 errors 3 and 4.)
- **Hold-outs** are written by a family that is neither the steward's nor an author's, from the inputs alone, inlined, unsteered by the steward's hypotheses. Only their hashes are committed until every arm's first version is in. (X1 Amendment C; X2 Departure 2.)
- **Shared schedules exercise every form the format allows**, including an event `end:`. (X2 error 6.)
- **The steward does not hand its own hypotheses to authors, hold-out authors or judges.**

## While authors work
- Do not touch a running author's checkout. If the steward's setup broke something (a missing hook), repair the consequence from the main checkout, before any steward run, and log it.
- Hooks in linked worktrees are shared with the main checkout: install nothing in `.git/hooks` while model authors are working.

## Declared limitations
Before hold-outs run, the steward answers each declared limitation in the log: a schedule is written for it (as a shared schedule in the next round, never retroactively in this one), or the steward says why not. A declared limitation that a hold-out then exposes is reported as declared, not as a blind spot. (X2.)

## Running and judging
- Steward runs are the first runs after each arm's merge, from scratch worktrees, never from the main checkout; hold-out files enter scratch copies only. (X1 Amendment C.)
- Divergences, shared failures and bound hits go to the judge, a third family, packet inlined, never the steward's hypothesis. `agy` reads a long prompt from stdin only as `agy -p= --input-format stream-json --output-format stream-json` with one line `{"event":"user","message":{"content":...}}`; keep a packet under about 120k characters (a 207k packet was spilled to a file and produced no verdict). Split per item if needed, with any excerpting done by a rule stated in the packet. (X2 error 5.)
- Check the registered fairness rule against every model-side liveness PASS, and say so in the result. (X2 result review.)
- An implementation pair is scored on at least ten repetitions per seed, and its rate is reported. A pair whose outcome varies across repetitions of one seed is **flaky**, reported as such, never as PASS or kill. A seed is not a reproduction: wall-clock time can decide outcomes. (Third steward's diagnostic, 2026-10-21: the fix round's "seed-dependent" regression was timing-dependent, with rates up to 30%; every result before it was a single sample per seed.)
- Write times from the clock, never from memory, including in the steward's own log entries. (Logged by all three stewards; the third broke it a minute after relying on it.)

## Scoring
- **Score at the moment the registration names, and nowhere else.** No scoring rule is introduced after an outcome is seen. A reading that an outcome suggests is reported beside the registered score, never instead of it. (X2 error 8: a "first version" rule written after seeing 28 of 30 was the only item on which one arm beat the other.)
- **Measure 6 ruling (from X2's residue).** A unit is **conceptual** iff it makes a choice the inputs leave open: choosing between behaviours the inputs permit, or reading an ambiguous input. Implementing an unambiguous prescription of the inputs, however much code it takes, is **propagation**. Both X2 rater pairs split on exactly this; this ruling applies from X3 and is not applied retroactively.
- **Measure 7 raters do not see the adapting author's labels.** They get the old README and the code diff, not the new README; the author's statements are compared afterwards. (X2 error 9.)
- Before publication, a non-steward family reviews the scoring adversarially against the registration and the evidence. (X2: the review changed the headline.)
- Commit the evidence behind every number: run logs, provenance outputs, ratings, judge streams. `tmp/` is never committed; copy into `experiments/`.

## Records
- Start every long-running process through the harness's tracked background mechanism, never a bare `&`; an untracked process is invisible to Tony and sends no completion notice. Report a process's state only from an observation made at the time of reporting. (2026-10-21: the Grok calibration was reported as still running half an hour after it had finished.)
- Log every steward error with its cost, as soon as it is known. Check the clock before writing a time. (2026-10-20 and 2026-10-21: two guessed times.)
- Never rewrite committed history; OpenTimestamps proofs bind the hashes. Corrections are appended.
