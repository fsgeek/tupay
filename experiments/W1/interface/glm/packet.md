You are designing a shared test interface for a backup service. The contract and failure model below are fixed; do not change them, and do not design the service itself.

Several independent teams will each build an implementation of this contract, and some will also write a formal model (for example in TLA+). One test suite of "schedules" must run, unchanged, against every implementation and every model. A schedule is a scripted scenario: what happens to the sources, which failure-model cells (BF1.x) are injected and when, and what must be observed. Your interface is the only thing the teams share besides the contract, so whatever it leaves unspecified, each team will decide differently.

The interface must make the following possible:
1. Time. The contract's parameters are hours and days (see the binding's values). A schedule covering several weeks must run in minutes. Say how time is given to an implementation, and how clock steps on one host are expressed (the contract measures ages on each host's own clock).
2. Hosts and roles. Every role the contract names (source host, store, restore host, freshness checker, notice channel) must exist in a test, on one machine, without root. Say what each is in a test and how an implementation is told where it is.
3. Fault injection. Every BF1 cell in the failure model must be injectable by the test harness, without the implementation's cooperation beyond what the interface requires. For each cell, say how it is injected and how it ends.
4. Observation. Everything a schedule's assertions need must be observable from outside the implementation: in particular, the notice channel's record (which clause a notice names, and when it arrived), snapshot marks, and whether a snapshot is recoverable. Say what is recorded, where, and in what format.
5. Assertions. Every assertion in a schedule carries a tag naming the contract clause it checks, written `derives: B1.x` (or the id it checks). Each schedule states a fixed scoring horizon: a fixed time after its last injected event, at which recoverability is judged.
6. Models. The same schedule text must be readable by a formal model's own schedule runner. Say which parts of a schedule a model must accept, and how a model reports that it cannot express a schedule.
7. Prescription. The contract prescribes no protocol and no tooling. Your interface must not prescribe any either, beyond what injection and observation strictly need. Where you must constrain an implementation (for example, to read time from the harness), say so, and say why the constraint is needed.

Write the interface as a specification another engineer could implement a harness from, with:
- a schedule format (grammar or schema, with one complete example schedule that injects at least two cells);
- the implementation-side contract (what an implementation must expose or obey, and nothing more);
- the harness's obligations;
- a list headed OPEN CHOICES: every point where the contract or binding leaves the interface's design open and you chose one option. For each, give the options you saw and why you chose yours.
- a list headed CONTRACT QUESTIONS: any place where you could not design injection or observation because the contract itself is unclear. Quote the text. Do not resolve these yourself.
Be concrete and complete rather than brief.

===== THE CONTRACT AND FAILURE MODEL (contract-P.md) =====
# Verified backup: contract and failure model

## Parties and terms
The service backs up some **sources** (directories, and possibly git repositories) from a **source host S** to a **store R**, which is a separate machine reached over a network. **Snapshots** are restore-checked on a **restore host**, which has no copy of the sources and no path to S's files. A **freshness checker** runs on R. Notices go to a **notice channel**; the binding states which hosts the channel depends on. A **notice** is a message on the channel that names the clause requiring it, and it **reaches** the channel when the channel's own record holds it. A separate binding document says which machines, directories, channel and parameter values these are, and which hosts can be suspended. Credentials and caches, as the binding defines them, are never part of the sources.

Each run gets a sequence number, which orders runs and snapshots; clocks never do. Every age is measured on the clock of the host that measures it, so across a clock step an age can be wrong by up to the size of the step. A day is 24 hours, and a month is a UTC calendar month. Runs happen one at a time. Before doing anything else, a run records that it has started, in R's copy of the status record. A run that cannot do so does not start. Its number is one more than the highest number found in S's record, R's record or R's snapshot names. So no number is reused while any surviving record or snapshot carries it. If every record and snapshot carrying a number is lost, nothing is promised about that number.

At its start, a run reads, once, the list of every file path in each source tree: its **source inventory**. For a git repository the inventory is instead the list of (ref name, object id) pairs, read once at the start, and the bundle is built from those object ids, never from names resolved later. Paths created after the inventory is read, including any created and deleted during the run, are not part of that run, and nothing here claims them. Each snapshot is stored at R and **named by its sequence number**. The run writes the snapshot's **manifest**, which lists every file in the snapshot with its sha256 together with the run's source inventory, and stores it with the snapshot.

A snapshot is **verified** when R has read every file and every hash has matched the manifest. It is **acknowledged** when the status record holds an *ok* entry for it. A **restore check** copies the snapshot from R to the restore host, clones any repository from its bundle, and compares every file with the manifest. It ends either as *restore-checked*, meaning the snapshot restored and matched, or as *restore-failed*. A snapshot is **restorable** when that procedure, run without S, would reproduce its manifest. Only a passing restore check is evidence of that. A later verification shows only that the checked bytes have not changed since.

The **status record** is kept on S and copied to R after each run. It holds run entries (sequence number; started, ok or failed; the stage, where "unknown" is a valid stage; and times) and snapshot marks (sequence number; restore-checked, restore-failed, not restore-checked, damaged or missing; time; and the host that wrote it). Only S writes run entries. Marks are written only into R's copy, by the freshness checker, by R's re-verification and by the restore host, and S merges them at its next run. A snapshot is **protected** from the moment it is acknowledged until pruning removes it. A **daily snapshot** is the acknowledged snapshot with the highest sequence number in its UTC day. The **daily check** runs on S once every *I*. A **logged reason** is an entry in the record the binding names, written before the run, that names the source tree and the change.

## Contract v1
- **B1.1** A run writes *ok* only after its snapshot is verified at R and is complete under B1.17.
- **B1.2** A git repository in a snapshot is bundled from the inventory's (ref name, object id) pairs, never from names resolved later, so its refs are exactly those pairs. Every other file in a snapshot is a version that existed on S during the run, and no file is torn.
- **B1.3** A protected snapshot whose latest restore check passed, and which has not been marked damaged or missing since, is restorable. A snapshot not yet checked is covered only by B1.8. A snapshot whose check failed is covered by nothing, and B1.7 reports it.
- **B1.4** Pruning never removes the newest snapshot that passed its restore check and has not since been marked damaged. It also never removes:
  - any snapshot younger than *T*;
  - any daily snapshot younger than *K*;
  - the first daily snapshot of each month for *Mo* months.

  While there is less history than that, pruning removes nothing those rules would keep. Pruning never frees space by breaking this clause. It removes nothing while the status record is being rebuilt.
- **B1.5** The run never writes a credential file to R or to the restore host. Each run scans the material that is new since the previous acknowledged snapshot (for a git repository, the new commits) with the binding's credential detector. A hit fails the run at stage *no-credentials*.
- **B1.6** The record never holds *ok* for a snapshot that B1.1 does not allow. Every *failed* entry names its stage. Once a snapshot is *ok*, the service never records it as failed and never removes it except by pruning. When a run ends without a final entry, the next run or the freshness checker, whichever comes first, records it as failed, stage unknown.
- **B1.7** The freshness checker sends a notice under B1.16 within *D* of each of these:
  - the newest acknowledged snapshot becoming older than *H*;
  - a *failed* run entry appearing;
  - B1.8's deadline passing;
  - B1.12's deadline passing;
  - B1.19 being violated;
  - a snapshot being marked restore-failed, damaged or missing.

  A run that fails on S also sends its own notice under B1.16 within *D* of failing.
- **B1.8** The restore host completes a restore check of every acknowledged snapshot within *M* of its *ok* entry, and records the result. A check that completes with *restore-failed* meets this clause and triggers B1.7, but never meets B1.3. Until a check completes, the record shows *not restore-checked*, which is a state and not a discharge of this clause. At the start of each check, the restore host removes anything left by a check that crashed.
- **B1.9** Suppose that, over an interval of *I* + *X*, S and R stay up, connected and not full, and every source file can be captured untorn. Then by the end of that interval an *ok* entry exists with a higher number than every number acknowledged at its start.
- **B1.11** Every exclusion (EX) and assumption (AI) below carries a review date. After that date the daily check on S fails until the item is decided again and the decision is logged.
- **B1.12** R verifies every protected snapshot again within *P* of its previous verification, without needing S. A mismatch marks the snapshot damaged, and pruning does not count a damaged snapshot towards B1.4.
- **B1.13** Every run, and every pass of the checker, compares the snapshots present at R with the protected snapshots in the record, and marks each absent one missing.
- **B1.15** A run compares each readable source tree's file count and bytes with the previous acknowledged snapshot. A fall of more than *Q* in a run that no logged reason names sends a notice under B1.16 within *D* of the comparison. The snapshot is still made and acknowledged. A source tree that cannot be read fails the run at stage *source*.
- **B1.16** A notice reaches the channel within *D* of the event that requires it. While the channel cannot be reached, the sender keeps the notice where the checker reads, and delivers it within *D* of the channel coming back.
- **B1.17** The manifest holds every path in the run's source inventory, or lists it as *gone* when it was deleted after the inventory was read. A path that cannot be captured untorn after one retry fails the run at stage *capture*, and the snapshot is not acknowledged, so no path is ever silently left out of an acknowledged snapshot. While such a file keeps changing, every run fails and is reported. A renamed file shows as its old path deleted, and the next run picks up its new path.
- **B1.18** Each copy of the status record carries a hash over its entries, rewritten at each update. A copy whose hash fails is treated as lost, and is kept aside unchanged as evidence; it is never copied over the other copy. Recovery works as follows:
  - if S's copy is lost, S takes R's at its next run;
  - if R's copy is lost, R takes S's at the next run;
  - if both are lost, the service rebuilds the record within *Rb*, by listing, re-verifying and restore-checking every snapshot at R; every snapshot present stays protected meanwhile;
  - if both copies are intact but disagree, run entries follow S's copy and marks follow R's copy, every disagreement is reported under B1.7, and both copies are kept.

  The hash catches accidental corruption, not a copy that is wrong but consistent.
- **B1.19** After the first *G* of operation, there is always a protected snapshot whose latest restore check passed, which has not been marked damaged or missing since, and whose *ok* entry is younger than *G*. **The service promises recoverable backups, not verified copies plus failure reports.** When no such snapshot exists, this clause is violated, whatever the cause, and B1.7 reports it as *overdue*, naming the cause: failed checks, failed runs, failed captures, or an unavailable host. Checks that complete, and failures that are reported, do not satisfy it.

**Deadlines.** Every time limit above is measured by the freshness checker from its own starting event, whatever happens to the hosts, and is never suspended, paused or restarted, under any failure. When an unavailable host (BF1.2, BF1.4, BF1.8, BF1.14) causes a deadline to be missed, the checker reports it under B1.7 as *overdue* and names the cause. Unavailability explains a missed deadline; it never excuses or resets one. Nothing promises any detection time while R, where the checker runs, is down. The things the service must always do or never do (B1.1, B1.2, B1.4, B1.5, B1.6, B1.17) hold under every failure. A failure can stop the service from acting, but never licenses it to act wrongly. When stored data is lost to the environment (BF1.3, BF1.10, BF1.12, BF1.13), the service is not expected to prevent the loss. It must mark it and report it.

## Failure model v1
- **BF1.1** The backup process crashes at any point, including during a restore check or a re-verification, and restarts. A crash in the middle of a prune still never leaves anything B1.4 keeps removed. Files a crashed check leaves behind are removed at the next check's start.
- **BF1.2** Any two of S, R and the restore host are partitioned, for any length of time.
- **BF1.3** Stored bytes at R are silently corrupted.
- **BF1.4** A disk on R or S fills.
- **BF1.5** Files in the sources are written, deleted or renamed, or refs are updated, during a run. B1.2 and B1.17 are what this cell tests.
- **BF1.6** A clock on any host steps. Every deadline can then be wrong by up to the size of the step. The tests inject steps of ±1 h and ±24 h, and the error is reported. Order is unaffected, because it follows sequence numbers.
- **BF1.7** The notice channel is down while S is up. B1.16's second sentence applies.
- **BF1.8** A timer on any host fails to fire.
- **BF1.9** A source tree is moved, emptied or truncated by mistake. Copying it faithfully is correct, and B1.15 reports it.
- **BF1.10** R is reimaged or replaced, and all its snapshots are lost. Without a further copy they are gone (EX1.1). The next comparison marks them missing.
- **BF1.12** Some snapshots at R are lost by something other than the service.
- **BF1.13** The status record is lost or corrupted, on S, on R or on both. While both copies are being rebuilt, pruning stops.
- **BF1.14** A host is suspended. A restore check that misses *M* because the restore host is suspended is reported as overdue, with that cause.

**Excluded:**
- **EX1.1** S and R lost together with no further copy (review 2026-12-01).
- **EX1.2** Deliberate tampering by someone with access to S and R (2027-05-01).
- **EX1.3** Loss of anything from before the first snapshot (2027-05-01).
- **EX1.5** The checker and S's runs both stopped for longer than *H* (2026-12-01).
- **EX1.6** S down for longer than *H* when the binding's notice channel depends on S, so that the checker sees the silence but cannot tell anyone. Each binding states whether this exclusion applies to it (2026-12-01).
- **EX1.7** Snapshots are not encrypted at R or on the restore host. Encryption comes in contract v2 (2026-12-01).

**Assumed impossible:**
- **AI1.1** sha256 collisions (2027-11-01).
- **AI1.2** R's hash tool reporting a false match; the restore check rehashes elsewhere (2027-05-01).
- **AI1.3** The host answering as R not being R; a pinned host key (2027-05-01).
- **AI1.4** The restore check secretly reading S; it has no path to S (2027-05-01).
- **AI1.5** A credential entering a source undetected; the per-run scan, whose detector has its own mutation test (2027-05-01).

**Retired ids, never reused:** B1.10, B1.14, BF1.11, AI1.6, EX1.4, T7a, T7b, T14 and T27.

## Parameters
The binding gives the values. *I* is the run interval. *M* is the restore-check deadline. *P* is the re-verify interval. *H* is the staleness limit, equal to *I* plus slack. *D* is the notice delay; the checker runs at least every *D*. *X* is the liveness slack. *Q* is the shrink fraction, measured on the binding's own history. *Rb* is the rebuild deadline. *G* is the maximum age of a recoverable snapshot, which must exceed *I* + *X* + *M*. *Dmax* = *I* + *X* + *D*, and *T* = *M* + *Dmax*, which is a floor. Both hold only if the next run succeeds, the damage crosses *Q*, and R and the channel are reachable. Under BF1.2, BF1.4, BF1.8 or BF1.14 no detection bound holds. *K* and *Mo* are retention choices above *T*.
## Worked cases (the same as the four-part form's §12; each is also a test case)
1. **Completeness (B1.17).** Run 50 reads its inventory. `tupay-homes/a/t.jsonl` is being appended to by an author. Because the file is only appended to, the run copies it up to the length it read, and checks that prefix. A prefix is a version the file really had, so it is captured untorn, and run 50 is acknowledged. A different file, `state.db`, is **rewritten in place** faster than the run can capture it twice the same. Run 50 fails at *capture*, B1.7 sends a notice within *D*, and nothing is acknowledged until a run captures `state.db` untorn. **No acknowledged snapshot lacks either file.**
2. **Restore (B1.3, B1.8).** Run 60 is acknowledged at 11:20. At 13:00 its restore check completes and fails: one file differs. The restore host writes *restore-failed*. B1.8 is discharged, because the check completed. B1.7 sends a notice. B1.3 does not cover snapshot 60. Pruning keeps run 59, the newest *restore-checked* snapshot, under B1.4.
3. **Deadlines.** Run 70 is acknowledged at 11:20 on day 1, and the box is suspended from 12:00 on day 1 to 09:00 on day 3. At 11:20 on day 2, *M* has passed. The checker on R reports snapshot 70 as *overdue*, with the cause "restore host suspended". The deadline is not restarted when the box returns. The overdue report stands until a check of snapshot 70 completes.
4. **Sequence numbers.** Run 42 writes *started 42* to R's record, then fails before making a snapshot. S's record is then lost. The next run computes max(S: none, R's record: 42, R's snapshots: 41) + 1 = **43**. If R's record had also been lost, it would compute 42 again, and the contract makes no claim in that case, as the numbering rule above says.
5. **Corrupted record (B1.18).** S's copy fails its hash. R's copy passes. S sets its copy aside unchanged, takes R's copy, and B1.7 sends a notice. If both copies pass but disagree about run 44's run entry, S's copy wins. If they disagree about a mark on snapshot 44, R's copy wins, because marks are written only there. Either disagreement is reported.
6. **Inventory.** At the start of run 80 the inventory reads `refs/heads/main` → `abc123`. A commit then moves `main` to `def456` during the run. The bundle contains `main` = `abc123`, and run 81 captures `def456`. A file created at 11:21 and deleted at 11:22, during run 80, is in no inventory and no manifest, and no clause claims it.
7. **Recoverable (B1.19).** *G* = 96 h. Runs 90 to 93 are acknowledged daily, and each restore check completes with *restore-failed*: a restore-procedure bug. B1.8 is discharged each day. B1.3 covers none of these snapshots. Snapshot 89, the newest *restore-checked*, is kept by B1.4. At 96 h after run 89's *ok* entry, **B1.19 is violated**, and B1.7 reports it as *overdue*, with the cause "restore checks failing". The service is failing its contract, and the record says so, rather than passing because it reported each failure.
8. **Capture and liveness (B1.9, B1.17).** `state.db` is rewritten in place continuously from day 1. Every run fails at *capture*. B1.9's premise is false, so B1.9 is vacuous. **B1.19 is not vacuous:** once the newest recoverable snapshot passes *G*, it is violated and reported. Capturability is an assumption of liveness, and never an excuse for the recovery guarantee.


===== THE BINDING (maps the contract roles to machines and values) (binding-tupay.md) =====
# Tupay's binding to the generic backup contract: binding v1, for contract draft 7 (not registered)

The twelfth steward, 2026-11-12. This binding maps the roles of `contract-draft-7.md` onto tupay's machines, directories and values. A change of host is a new version of this binding; it is not a change to the contract. **Binding v1 describes the host before the move. The post-move binding, v2, is written when the house's new system exists (`host-requirements.md`).**

## Roles
| Role | Bound to (v1) |
|---|---|
| S (T1) | WAM-THREADRIPPER, under WSL |
| Sources (T2, T20) | tupay's git repository (every ref); `../tupay-private/`; `../tupay-homes/` |
| R (T3) | wam-nuc, at `backups/tupay/` |
| Restore host (T4) | the box (`ubuntu26-test` VM), which has no tupay sources and no path to S |
| Freshness checker (T23) | a process on wam-nuc |
| Notice channel (T29) | the plaza, as `guest:tupay`. **Its record is on S**, so EX1.6 applies to this binding. |
| Caches (T21) | `.cache`, `go` and package caches under `tupay-homes/` |
| Credential (T13) | file names matching `auth.json`, `.credentials.json` and `*credential*`; content reported by `scripts/steward/secrets-scan.sh`, pattern set v1 (mutation pair: `secrets-scan-check.sh`) |
| Logged reason (T26) | an entry in `docs/seed-log.md` |
| Hosts that can be suspended (BF1.14) | the box (lent to other residents); S (WSL); wam-nuc (power) |
| Daily check (T24) | runs on S |

## Values (derivations in contract §6)
- *I* = 24 h.
- *M* = 1 d.
- *P* = 7 d.
- *H* = 36 h, which is *I* + 12 h.
- *D* = 1 h.
- *X* = 2 h.
- *Rb* = 2 d.
- ***G* = 96 h** (recoverable age, B1.19; Tony, 2026-11-12, changed from 72 h). It must exceed *I* + *X* + *M* = 50 h, the normal worst-case age of the newest restore-checked snapshot. Each missed run or check adds *I* = 24 h: one miss gives 74 h, which passes; two in a row give 98 h, which is violated. **Correction:** the steward's 72 h claimed to tolerate one miss, but one miss (74 h) already exceeded it.
- *K* = 14 d and *Mo* = 6 months.
- ***Q* = 0.05.** Measured 2026-11-11 from 9 quiet runs. `tupay-private/` and `tupay-homes/` did not change; the bundle's size moved between −0.87 % and +1.32 %. Its noise under author load is unmeasured, so it is measured again after the first round with authors.
- Derived: ***Dmax* = 27 h** and ***T* = 51 h**, both under contract §6's conditions.

## What this binding changes in what you can recover
The baseline is `recovery-account.md`, checked 2026-11-11.

| Row of the account | Clauses that change it |
|---|---|
| Restore tested once, by hand | Every snapshot restore-checked within *M*, from R alone (B1.8); **a demonstrated-recoverable snapshot never older than *G*, or a reported violation (B1.19)** |
| Corruption at R found only by chance | Every protected snapshot re-read every *P* (B1.12) |
| Snapshots lost at R go unnoticed | An inventory at every run and check (B1.13) |
| A copy can silently miss files | Completeness against an inventory (B1.17) |
| Retention by count | A way back by age, from a restore-checked snapshot (B1.4) |
| A source emptied by mistake is copied "successfully" | Reported within *Dmax* (B1.15) |
| S's silence unseen | Seen by the checker on wam-nuc (B1.7). Delivery while S is down: **open (EX1.6)** |
| A credential could enter in a commit | Scanned at every run (B1.5, AI1.5) |

**Accepted by v1 (draft 6, B1.17):** no file is silently omitted. Append-only files, such as author transcripts, are captured as a prefix and do not fail a run. While a file rewritten in place cannot be captured untorn, each run fails and is reported, until a run can capture it.

**Not changed by v1:**
- S and wam-nuc lost together (EX1.1; an off-site copy is a second contract);
- plaintext at wam-nuc (EX1.7; encryption is contract v2);
- harness credentials, which are never backed up, by design.

## The rung below (a comparison of behaviour)
The rung below is `backup.sh`, its two timers, `backup-check.sh` and `backup-alert.sh`.
- **It gives:** B1.1 without completeness; B1.5 by file name only; part of B1.6; B1.9, through the timer; and part of B1.7, from S.
- **It lacks:** B1.3 and B1.8 from R alone, B1.4, B1.12, B1.13, B1.15, B1.16, B1.17, B1.18, and a checker off S.
- Its acknowledgement defect was fixed on 2026-11-08 (Qwen's finding 10).

If the service cannot beat both this rung and restic on what they lack, the finding is that a rung was enough.

## Answered by Tony, 2026-11-12 (his notes kept verbatim; the steward's disposition follows each)
1. **A notice channel that does not depend on S.** Recommendation: wam-nuc sends a single kind of push message when S has been silent longer than *H*, or the daily check has not run for 2 *I*. Which channel would you notice? [TM: whichever one I am told to watch.  wam-nuc is fine. pundit doesn't have much CPU/memory, but it has plenty of storage.]
   *Disposition:* the sender runs on wam-nuc. **The channel is the steward's to name, and Tony watches it.** It is named when the alert is built, with its message types fixed and carrying no content from the sources. *pundit* (little CPU, plenty of storage) is recorded as a candidate home for EX1.1's further copy, under the second contract. It is not assumed.
2. **An ssh key for wam-nuc that is not held only on S.** Recommendation: create one and keep it in the house's new key management. [TM: agreed.  Assignment TBD.]
   *Disposition:* agreed. The key is created when the house's key management assigns it. Until then the recovery account's dependency stands.
3. **The move as the first real restore.** This is settled (log, 2026-11-11). The migration acceptance contract (`migration-acceptance-draft-1.md`) defines what passing means.  [TM:Amendment permissible in an emergency situation only, with a clear record of any deviation.]
   *Disposition:* recorded as amendment A1 of `migration-acceptance-draft-1.md`.
