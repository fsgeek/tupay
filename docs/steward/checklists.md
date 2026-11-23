# Checklists: single-incident cautions, at the point of use

Moved from `docs/steward-practice.md` by the practice audit (2026-11-18, proposal 2; applied 2026-11-23). Each came from one incident, with no mechanism and no recurrence on record. Run the section before the step it names. Rule text is verbatim.

## Briefs and schedules
- **Briefs say the steward may run unseen schedules**, under any name, so no artifact refuses them. (X2 error 7.)
- **Shared schedules exercise every form the format allows**, including an event `end:`. (X2 error 6.)
- **Every event trigger in a shared schedule is owed by a clause**: an event an artifact may legitimately never emit can stall the run into "end unreachable" and test nothing. Say in the comment which clause owes it. Read selectors against A1 by hand; the lint's rule is weaker. (2026-10-23: P33 waited on one node's `Agree`; P58's first version used a fixed node where its pair needed the grantor, which the lint passed.)
- Check the registered fairness rule against every model-side liveness PASS, and say so in the result. (X2 result review.)

## Launching
- **Every box run gets a tracked watcher on this host** (the harness's background mechanism) that polls the unit and exits when it ends or the box stops answering. Box units are not the harness's processes, so without one nothing reports their end. (2026-10-28: the Claude C author's end went unnoticed for most of a day, and then the box was unreachable.)
- Hooks in linked worktrees are shared with the main checkout: install nothing in `.git/hooks` while model authors are working.

## Judging
- **Before a steward check's report goes to a judge, search every author's README for the check's name.** An author may already have declared why it misfires. (X3, 2026-10-27: arm A's model README explained `provenance_check.py`'s restart defect; no steward read it, and the defect went to both judges as arm R's 80 untraceable decisions.)

## Records
- **Before `git add` of a directory a script wrote, list what it holds.** A file that embeds another resident's material (a sealed file appended to a packet) is not committed without that resident's word. (2026-10-29: Episode's v2 seal entered tupay's local history inside judge packets; nothing was pushed.)
