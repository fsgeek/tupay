# Handoff from the fourteenth steward (Claude Opus 5.5): FINAL (2026-11-23)

The log outranks this note. The tenure ran from 2026-11-22 (acceptance `5fbda91`) to 2026-11-23. It ended at Tony's figure of **420.1k of 1M**, under the 450k line. Everything is pushed.

## First
- **The session-start sweep** now also lists author processes no harness tracks. It prints only pid, elapsed time and a strictly matched name, never author argv.
- **A PreToolUse hook** (`scripts/steward/hooks/no-host-git-in-author-checkout.py`) blocks any Bash command containing "git" that also names an author checkout, or that runs with its working directory in one. Over-blocking is deliberate. Use the file tool to edit text that mentions such names. Its known limit is in its header.
- **Daily checks still guard the backup:** `backup-check` (14:00Z) and `restore-path-check` (14:30Z, now against `tupay-restore@pundit`).
- Never end a turn on a promise or on "any reply from you begins it". The courtier freeze recurred in that new form this tenure.

## State
- **The backup line is closed as a study** (Tony, 11-23: "a single event"). The service stays: binding v2 (`docs/backup/binding-tupay-v2.md`), with the restore host on pundit. The drill (`scripts/steward/restore-drill.sh`) passes when started from S and from wam-vector. See the recovery account's dated sections.
- **W1 is closed unlaunched.** Its predictions are *never scored*. Amendment A2 (a shared test interface) found contract v1 untestable as written. The material, kept for any v2: two interface drafts, `testbed/backup/interface-v1.md`, Kimi's check (24 findings, 13 blocking), and 72 contract questions.
- **W2 is scored and final** (`experiments/W2-result.md`): the four-part form drew fewer contract questions or the same number (GLM 8/8, StepFun 10/8, Mistral 28/10). Both predictions hold, registered and amended. The steward's forecast was wrong in direction. Two counting amendments (A1, A2) were informed by outcomes. Both are logged, and the registered score is reported first.
- **The practice audit is applied:** mechanisms for rules 18, 26 and 53; rule 25 is still unenforced (it failed a third time this tenure); cautions moved to `docs/steward/checklists.md`; START.md's ritual changed.
- **Method change, acceptance decision 3:** the steward does not patch its own inputs. Fixes and new inputs are drafted in parallel by two other families, and the steward disposes. This tenure's evidence for it: every steward-written merge or script carried defects that the parallel drafts or an outside check caught.

## Owed
- **11-26 report** against the month's measure. Its honest content: two worked examples (Episode and backup); one real outside use (yanantin uses T10/T11 and moved its restore host to pundit first; same family, Claude); no non-Claude scorer of a tupay output, though W2's judges and drafters were non-Claude, they were internal instruments; whether the Mallku sign shows: say so plainly.
- **12-31:** the theater decision, Tony's framing: "If we could build something that convinces the steward it is useful, I'd respect that decision."
- **Tony: `grok login`.** The OIDC login died silently (refresh rejected), and Grok falls back to per-token `XAI_API_KEY`. No Grok author may launch on that.
- **M365 final PIR:** not yet seen (Tony, 11-22). Predictions 4, 11 and 12 wait on it.
- **authority's survey, and research-program's seq 291 pointer** (quantumos's `verified_at` design): answer after 11-26, as decided.

## Recommendation for the next line (the successor decides)
**A first slice of Arariwa on the backup service's recovery path:** a record of each recovery-path dependency (the restore host's key and reach, the logins a restore needs, the age of the last drill, the timers themselves), each with its own `verified_at` (quantumos's rule: never merge event time with verification time), reporting drift. Every operational defect found in this line (the box that travelled back in time, the restore host that could never reach R, Grok's dead login) was found by asking and would have been found by this. Build it with the method change: contract, failure model **and test interface drafted in parallel** by different families, before registration. The SMR seed is the alternative if its code arrives (an outside judge, and outside the training data).

## Errors this tenure (all logged, with costs)
- Planned a gazelle VM from the handoff's step without reading `box-launch.sh` (one round of Tony's time).
- Committed before reading why the secrets scan exited 1.
- The courtier freeze, in a new wording.
- The merged interface carried 13 blocking items.
- Two counting-script defects in W2, each needing an amendment informed by an outcome.
- Renamed a script under running cells (rule 25).
- A false "both files exist" in a log entry, and a wrong sum.
