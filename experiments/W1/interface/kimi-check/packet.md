You are an outside checker. Below are a contract and failure model for a backup service (fixed), its binding (fixed), and a shared test interface that several independent teams will use: some write implementations, some write formal models, and one writes test schedules without seeing any implementation. The same schedule text must run unchanged against all of them. Two drafters raised the contract questions at the end; they are unresolved on purpose, because the interface must not choose a reading of the contract for the teams.

Check the interface for defects of these kinds (kinds, not suspicions):
1. Injection: a failure-model cell (BF1.x) that cannot be injected as specified, or whose injection does not match the cell's text, or that needs the implementation's cooperation beyond what the interface requires.
2. Observation and scoring: an assertion a schedule would need, for some clause, that the vocabulary cannot express or the harness cannot score from what it records; a predicate whose definition does not match the clause it would test.
3. Readings: a place where the interface itself picks one reading of the contract where the contract permits several, so that a correct implementation following another permitted reading would fail. Use the contract questions here: for each, say whether the interface as written lets an assertion accept every permitted reading, or forces one.
4. Prescription: a constraint on implementations that injection or observation does not strictly need, or that favours one design over another the contract permits.
5. Determinism and portability: anything that would make the same schedule produce different verdicts on two correct harness implementations, or that a TLA+ model's runner could not reasonably read.
6. Internal consistency: contradictions between sections; undefined terms; examples that do not match the grammar.

Report numbered findings, each with: kind (1 to 6), severity (blocking / significant / minor), where (section), what is wrong, and why (quote the text). One-line suggested fix per finding. Blocking means: W1's schedules cannot be written or scored fairly unless it is fixed. If you find nothing of a kind, say so for that kind.

===== THE CONTRACT AND FAILURE MODEL =====
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


===== THE BINDING =====
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


===== THE INTERFACE UNDER CHECK =====
# Shared test interface for the backup contract, v1

Merged from two independent drafts by GLM and Mistral. The disposition of every difference is in `experiments/W1/interface/DISPOSITIONS.md` (the steward, 2026-11-23). Items marked [Dn] or [An] name the line there. This interface changes no clause of the contract and designs no part of the service.

## 0. Scope
One schedule file runs unchanged against every implementation of the contract and against every formal model that has a schedule runner. This interface prescribes only what is needed for virtual time, for placing all roles on one unprivileged machine, for injecting every BF1 cell, for observing notices, marks, snapshots and recoverability, for tagged assertions, and for a fixed scoring horizon. It prescribes no backup algorithm, storage engine, language, process model, or protocol above the harness relay.

## 1. Schedule format [D1]
A schedule is one JSON document matching the schema below. Any object may carry a `"note"` string, which every runner ignores.

```json
{
  "schedule": {
    "id": "string",
    "version": "1",
    "binding": "binding-tupay-v1",
    "params": { },
    "start": "2026-11-12T00:00:00Z",
    "scoring_horizon": "8d",
    "world": [ WorldItem ],
    "events": [ Event ],
    "assertions": [ Assertion ]
  }
}
```

### 1.1 Primitive types
- `rfc3339`: an RFC 3339 UTC timestamp.
- `duration`: `^[0-9]+(ms|s|m|h|d|w)$`, where `d` is 24 h and `w` is 7 d.
- `signedDuration`: `^[+-][0-9]+(s|m|h|d|w)$`.
- `HostId`: `"S"`, `"R"`, `"RESTORE"` or `"CHANNEL"`.
- `Role`: `"source-host"`, `"store"`, `"restore-host"`, `"freshness-checker"` or `"notice-channel"`.
- `TimerKind`: `"run"`, `"check"`, `"restore-check"`, `"reverify"`, `"prune"`, `"notice-retry"` or `"other"` [D2].

### 1.2 Parameters
`params` overrides binding values, using the binding's names (*I*, *M*, *P*, *H*, *D*, *X*, *Rb*, *G*, *Q*, *K*, *Mo*), with durations as `duration` strings, *Q* as a number and *Mo* as an integer number of months. *Dmax* and *T* are derived by the harness as the contract states. Every runner uses the same resulting values.

### 1.3 World: S's sources at time zero [D11]
```json
WorldItem =
  { "type": "dir",  "path": "tupay-private/", "files": 40, "bytes": 200000, "seed": 7 }
| { "type": "file", "path": "tupay-homes/a/t.jsonl", "content": "string", "append_only": true }
| { "type": "git",  "path": "tupay.git", "refs": { "refs/heads/main": "commits:3" } }
```
Paths are relative to `SOURCE_DIR`. `dir` generates `files` files totalling `bytes` bytes, deterministically from `seed`. `git` creates a repository with the named refs, each pointing at a generated history of the stated number of commits. The harness builds the world before the first event.

### 1.4 Events
```json
Event = {
  "id": "string",
  "at": "rfc3339?",
  "after": "string?",
  "delay": "duration?",
  "when": When?,
  "timeout": "duration?",
  "do": Action
}
```
An event names `at`, or `after` (an earlier event's id) with an optional `delay` (default `0s`), or neither (it then runs immediately after the previous event). With both `at` and `when`, it runs at the later of the two. `timeout` (default `7d`) applies only to `when`.

```json
When = { "kind": ObservationKind, "seq": "last" | integer?, "match": { }? }
```
`seq: "last"` means the sequence number of the most recent `run.started` observation. **If `when` is not true before `timeout` expires, the event is *unreached*.** It is not executed, and every assertion that names it, or any later event that depends on it, is scored `unreached`, never `pass` or `fail` [D5].

```json
Action =
  { "control": { "cmd": "run.start" | "check.run" | "ping" } }
| { "advance": duration }
| { "source": SourceAction }
| { "fault": Fault }
| { "clock.step": { "host": HostId, "delta": signedDuration, "cell": "BF1.6" } }
| { "clock.set":  { "host": HostId, "time": rfc3339, "cell": "BF1.6" } }
| { "query": { "what": "restore", "seq": integer } }
```
- `control` asks the implementation to start one run on S now, or one freshness-checker pass on R now (§4.2).
- `query` makes the **harness itself** perform an independent restore of snapshot `seq` (§6.6) [D12]. It is an observation, never the implementation's restore check, and it never counts toward B1.8.

```json
SourceAction = {
  "cell": "BF1.5" | "BF1.9" | null,
  "op": "write_append" | "rewrite_in_place" | "create" | "delete" | "rename"
      | "git.set_ref" | "git.commit" | "move_tree" | "empty_tree" | "truncate_tree",
  "path": "string", "to": "string?", "ref": "string?", "object": "string?",
  "content": "string?", "mode": "once" | "continuous", "size": "integer?",
  "duration": "duration?", "until": "string?"
}
```
A `source` action with `cell: null` is an ordinary change, not an injection. `rewrite_in_place` with `mode: "continuous"` rewrites the file at every virtual tick until `duration` passes or the `until` event runs.

### 1.5 Assertions
```json
Assertion = {
  "id": "string",
  "derives": "B1.x" | "BF1.x" | "EX1.x" | "AI1.x",
  "at": "horizon" | "<event id>" | rfc3339,
  "expect": Expectation
}
```
`at` defaults to `"horizon"`. **Every assertion carries exactly one `derives:` tag** [A8]. The harness rejects a schedule whose tag names a retired id: `B1.10`, `B1.14`, `BF1.11`, `AI1.6`, `EX1.4`, `T7a`, `T7b`, `T14` or `T27`.

```json
Expectation =
  { "all": [ Expectation ] } | { "any": [ Expectation ] } | { "not": Expectation }
| { "notice_reached": { "clause": "B1.x", "within": duration, "of": EventRef, "cause": "string?" } }
| { "record_entry": { "copy": "S" | "R", "kind": "run" | "mark", "selector": { }, "exists": bool } }
| { "snapshot_present": { "seq": integer } }
| { "snapshot_absent":  { "seq": integer } }
| { "manifest_complete": { "seq": integer } }
| { "marks_restorable": { "seq": integer } }
| { "restores": { "seq": integer } }
| { "recoverable_exists": { "max_age": duration } }
| { "next_seq_at_least": { "value": integer } }

EventRef = { "event": "string" } | { "kind": ObservationKind | "run" | "mark", "copy": "S" | "R"?, "seq": integer?, "match": { }? }
```
- `marks_restorable(seq)`: §6.5's `marks_restorable` holds for `seq`.
- `restores(seq)`: the harness's independent restore of `seq` (§6.6) succeeded. **A B1.3 assertion takes the form `marks_restorable(seq)` implies `restores(seq)`**, that is, `{"any": [{"not": {"marks_restorable": …}}, {"restores": …}]}` [D4].
- `recoverable_exists(max_age)`: some `seq` has `marks_restorable(seq)`, and its *ok* entry is younger than `max_age` at the assertion's time. A B1.19 assertion uses `max_age` = *G* [D4].
- `next_seq_at_least`: the next run's sequence number is at least `value` (worked case 4).
- **Where the contract permits several readings, an assertion must accept each of them** (W1 decision tree, step 2). An assertion built with `any` over the readings is the way to do it. **No assertion may require the service itself to report a clock step** [D8].

### 1.6 Scoring horizon [D10]
`scoring_horizon` is a fixed duration after the schedule's **last injected event**. An event is injected if its action is a `fault`, a `source` action with a non-null `cell`, or a `clock.step` or `clock.set`. The harness computes horizon = (the virtual time at which the last injected event actually ran) + `scoring_horizon`. With no injected event, the horizon is anchored on the last event. The harness advances to the horizon, firing timers, and evaluates every assertion whose `at` is `"horizon"`. A deadline that falls after the horizon is **censored** and listed as such in `results.json`. The horizon is never extended or shortened.

### 1.7 Example
```json
{ "schedule": {
  "id": "ex-bf1-3-bf1-14", "version": "1", "binding": "binding-tupay-v1", "params": {},
  "start": "2026-11-12T00:00:00Z", "scoring_horizon": "6d",
  "world": [ { "type": "git", "path": "tupay.git", "refs": { "refs/heads/main": "commits:3" } },
             { "type": "dir", "path": "tupay-private/", "files": 40, "bytes": 200000, "seed": 1 } ],
  "events": [
    { "id": "e1", "at": "2026-11-12T00:00:00Z", "do": { "control": { "cmd": "run.start" } } },
    { "id": "e2", "after": "e1", "when": { "kind": "run.finished", "seq": "last" },
      "do": { "fault": { "cell": "BF1.3", "host": "R", "seq": 1, "path": "tupay-private/f0001", "offset": 0, "flip": "0xff" } } },
    { "id": "e3", "after": "e2", "delay": "1h",
      "do": { "fault": { "cell": "BF1.14", "host": "RESTORE", "duration": "48h" } } }
  ],
  "assertions": [
    { "id": "a1", "derives": "B1.3", "expect": { "any": [ { "not": { "marks_restorable": { "seq": 1 } } }, { "restores": { "seq": 1 } } ] } },
    { "id": "a2", "derives": "B1.7", "expect": { "notice_reached": { "clause": "B1.7", "within": "1h",
        "of": { "kind": "deadline.started", "match": { "clause": "B1.8", "seq": 1 } } } } },
    { "id": "a3", "derives": "B1.19", "expect": { "recoverable_exists": { "max_age": "96h" } } }
  ] } }
```
It injects BF1.3 and BF1.14. Its horizon is e3's actual time plus 6 d.

## 2. Time
### 2.1 Model [A1, D3]
The harness keeps one global virtual time `T` and one clock per host, `C[h]`, all equal to `start` at first. Advancing global time by Δ advances every `C[h]` by Δ. `clock.step` and `clock.set` change only the named host's `C[h]`, and `T` is unchanged. **A suspended host's clock keeps advancing** with `T`, because the contract's deadlines are never suspended, paused or restarted [D3].

### 2.2 Time for the implementation [A2]
Each role process gets `CLOCK_SOCK`. The implementation obtains contract time only by asking it: `{"op":"now"}` returns `{"time": "<C[HOST_ID] as rfc3339>"}`. It never reads the system clock for contract time. *Why:* weeks must run in minutes, and BF1.6 must step one host's clock.

### 2.3 Timers [D2]
Every timed wait the implementation needs is registered with `TIMER_SOCK`:
```text
{"op":"after","id":"<free id>","kind":"<TimerKind>","delay":"24h"}  ->  later {"op":"wake","id":"...","time":"..."}
{"op":"cancel","id":"..."}
```
Wakeups are delivered when `C[HOST_ID]` reaches the deadline, in host-clock deadline order. `kind` is required and comes from the closed set in §1.1. `other` is for anything else. *Why:* BF1.8 drops a wakeup chosen by (host, kind), and a hold-out written without seeing any implementation can only name a kind.

## 3. Hosts and roles [A3, A7]
### 3.1 Layout
```text
<run_dir>/
  schedule.json  observations.jsonl  clock-steps.jsonl  results.json
  hosts/S/sources/  hosts/S/record/status.json  hosts/S/out/
  hosts/R/store/snapshots/<seq>/  hosts/R/store/manifests/<seq>.json  hosts/R/record/status.json  hosts/R/out/
  hosts/RESTORE/restore/  hosts/RESTORE/out/
  hosts/CHANNEL/record.jsonl
  harness/restores/<seq>/
```
Everything is owned by the unprivileged harness user. There is no root, no mount, no namespace and no firewall rule.

### 3.2 Roles in a test
| Role | In a test |
|---|---|
| Source host S | processes with `HOST_ID=S`, `ROLE=source-host`; sources under `hosts/S/sources/` |
| Store R | `HOST_ID=R`, `ROLE=store`; snapshots and manifests under `hosts/R/store/`; R's record copy |
| Restore host | `HOST_ID=RESTORE`, `ROLE=restore-host`; workspace `hosts/RESTORE/restore/`; **its environment names no path under `hosts/S/`** |
| Freshness checker | `HOST_ID=R`, `ROLE=freshness-checker`; writes marks into R's record copy |
| Notice channel | a harness-owned process, `HOST_ID=CHANNEL`; its record is `hosts/CHANNEL/record.jsonl` |

**The channel depends on S** under binding v1 (its record is on S). While S is suspended or crashed and not yet restarted, the channel is unreachable. BF1.7 makes it unreachable while S is up.

### 3.3 Environment given to each role process
`HARNESS_RUN_DIR`, `HOST_ID`, `ROLE`, `CLOCK_SOCK`, `TIMER_SOCK`, `CONTROL_SOCK`, `OBSERVE_SOCK`, `NET_SOCK`, `S_ADDR`, `R_ADDR`, `RESTORE_ADDR`, `CHANNEL_ADDR`, `BINDING_ID`, `PARAMS_JSON`; plus `SOURCE_DIR` on S only, `STORE_DIR` on R only, `RESTORE_DIR` on the restore host only, and `RECORD_PATH` on S and R.

### 3.4 The relay [A4, D9]
All communication between roles, notices included, goes through the relay at `NET_SOCK`, to the addresses above. The relay carries bytes. It imposes no protocol on them. It can drop all traffic between any two hosts (BF1.2), or refuse connections to the channel (BF1.7).

## 4. Implementation-side obligations (all of them)
| # | Obligation | Why |
|---|---|---|
| 1 | Run unprivileged as a child of the harness; use only the directories and sockets the environment names. | One machine, no root; injection and observation. |
| 2 | Read contract time only from `CLOCK_SOCK`. | Compression and BF1.6. |
| 3 | Register every timed wait with `TIMER_SOCK`, with a `kind`. | BF1.8. |
| 4 | Send all traffic between roles, notices included, through the relay. | BF1.2 and BF1.7 without root. |
| 5 | Keep each status-record copy at `RECORD_PATH` in the format of §6.2, written atomically (temporary file, then rename). | Observation; BF1.13. |
| 6 | Keep snapshots as ordinary files under `STORE_DIR/snapshots/<seq>/` and manifests at `STORE_DIR/manifests/<seq>.json` (§6.3). Inside a snapshot directory, the layout is free, but the harness must be able to restore from it by §6.6's rule. | BF1.3, BF1.10, BF1.12; observation; B1.3. |
| 7 | Keep sources under `SOURCE_DIR`, and the restore workspace under `RESTORE_DIR`. | BF1.5, BF1.9; the restore host's isolation. |
| 8 | Accept `ping`, `run.start` and `check.run` on `CONTROL_SOCK` (§4.2). | Deterministic points in a schedule. |
| 9 | Emit the observations of §4.3 on `OBSERVE_SOCK`. | `when` predicates and deadline starts. An observation not emitted makes the dependent event *unreached* (§1.4). |
| 10 | Send each notice as JSON with at least `clause`, `cause` and `seq` (§6.4). | B1.7 and B1.16 assertions. |
| 11 | Survive SIGKILL and restart, and SIGSTOP and SIGCONT. Treat a write error on the sandbox (`ENOSPC`, `EFBIG`, `EACCES`, `EROFS`) as a full disk, and a relay error as an unreachable host. | BF1.1, BF1.14, BF1.4, BF1.2. |
| 12 | **No side channels:** do not detect the harness, and do not bypass the clock, the timers, the relay or the channel. [D13] | A test-validity rule, not a design rule. |

Nothing else is prescribed: not the language, runtime or libraries; not the backup algorithm, scheduling or pruning policy, or storage engine; and not the protocol above the relay.

### 4.2 Control
JSON lines on `CONTROL_SOCK`: `{"op":"ping"}`, `{"op":"run.start"}` and `{"op":"check.run"}`, each answered with `{"ok":true}` as soon as it is accepted. `run.start` starts one run on S now, and `check.run` starts one checker pass on R now.

### 4.3 Observations
JSON lines on `OBSERVE_SOCK`. The harness appends each to `observations.jsonl` with `time` (global) and `host_time` (the sender's clock). The required kinds (`ObservationKind`) are:
`run.started`, `run.inventory_read`, `run.finished`, `restore_check.started`, `restore_check.finished`, `reverify.started`, `reverify.finished`, `prune.started`, `prune.finished`, `mark.written`, `notice.sent`, and `deadline.started`. The last is emitted by the checker when it starts measuring a deadline, with `clause`, `cause` and `seq`. Each carries `seq` where it has one.

## 5. Fault injection, every BF1 cell [A9]
The harness injects. It never asks the implementation to misbehave.

| Cell | Action | Mechanism | Ends |
|---|---|---|---|
| BF1.1 crash | `{"fault":{"cell":"BF1.1","host":"R","role":"store","restart":"immediate"|duration}}`, often with `when` (e.g. `prune.started`) | SIGKILL to the role's processes, then relaunch with the same environment | At restart |
| BF1.2 partition | `{"fault":{"cell":"BF1.2","partition":["S","R"],"duration":"48h"}}` or `"until"` | The relay drops all traffic between the two hosts, both ways. Both stay up, and their clocks run. | `duration` or `until` |
| BF1.3 corruption at R | `{"fault":{"cell":"BF1.3","host":"R","seq":50,"path":"...","offset":1024,"flip":"0xff"}}` | The harness flips bytes in a file under `hosts/R/store/snapshots/50/`. `path` may be `"*"`, meaning the harness picks the largest file. | Persists |
| BF1.4 disk full | `{"fault":{"cell":"BF1.4","host":"S"|"R","duration":"12h"}}` | `RLIMIT_FSIZE=0` (with `SIGXFSZ` ignored) on that host's processes, and its writable sandbox directories made read-only [D6] | `duration` or `until`: limits and permissions restored |
| BF1.5 source change during a run | a `source` action with `cell: "BF1.5"`, usually with `when: run.inventory_read` | Direct change under `hosts/S/sources/` | `once`, or `continuous` until `duration` or `until` |
| BF1.6 clock step | `clock.step` or `clock.set` | Changes one host's `C[h]`. Timers are recomputed. **The harness records the step in `clock-steps.jsonl`** [D8]. | Persists |
| BF1.7 channel down, S up | `{"fault":{"cell":"BF1.7","duration":"6h"}}` | The relay refuses connections to `CHANNEL_ADDR`. Nothing reaches the channel's record. | `duration` or `until` |
| BF1.8 timer fails | `{"fault":{"cell":"BF1.8","host":"S","kind":"run","count":1}}` | The next `count` wakeups of that (host, kind) are recorded as `timer.dropped` in `observations.jsonl` and not delivered. With `"count":"all"`, every one is dropped until `until`. | After `count`, or `until` |
| BF1.9 source damaged | a `source` action with `cell: "BF1.9"`: `move_tree`, `empty_tree`, `truncate_tree`, `delete` | Direct change under `hosts/S/sources/` | Persists until a later source action |
| BF1.10 R reimaged | `{"fault":{"cell":"BF1.10","host":"R"}}` | Deletes everything under `hosts/R/store/snapshots/` and `hosts/R/store/manifests/`. **R's record copy is untouched.** To lose it as well, inject BF1.13 on copy R in the same instant [D7]. | Persists |
| BF1.12 snapshots lost | `{"fault":{"cell":"BF1.12","host":"R","seqs":[50,51]}}` | Deletes those snapshot directories and manifests | Persists |
| BF1.13 record lost or corrupted | `{"fault":{"cell":"BF1.13","copy":"S"|"R"|"both","mode":"lost"|"corrupt"}}` | `lost`: the file is deleted. `corrupt`: bytes are flipped so its hash fails. | Persists; never repaired by the harness |
| BF1.14 host suspended | `{"fault":{"cell":"BF1.14","host":"RESTORE","duration":"48h"}}` | SIGSTOP to all the host's processes. Its clock keeps advancing [D3]. Its timer wakeups due during the suspension are delivered at SIGCONT, in deadline order. | `duration` or `until`: SIGCONT |

## 6. Observation formats
### 6.1 `observations.jsonl`
One JSON object per line: `{"time": rfc3339, "host_time": rfc3339, "host": HostId, "kind": "...", "seq": n, ...}`. It also holds the harness's own lines: `timer.dropped`, `event.ran`, `event.unreached` and `fault.injected`.

### 6.2 Status record copy [A5]
```json
{ "entries": [
    { "kind": "run",  "seq": 50, "status": "started"|"ok"|"failed", "stage": "unknown"|"source"|"capture"|"no-credentials"|"...", "time": rfc3339, "writer": "S" },
    { "kind": "mark", "seq": 50, "mark": "restore-checked"|"restore-failed"|"not-restore-checked"|"damaged"|"missing", "time": rfc3339, "writer": "checker"|"restore"|"R" } ],
  "hash": "sha256:<hex>" }
```
`hash` is SHA-256 over the canonical JSON of `entries` (sorted keys, no whitespace), recomputed at every update. Entries are in append order. The implementation may keep further fields in an entry, which the harness ignores.

### 6.3 Manifest
```json
{ "seq": 50, "created_time": rfc3339,
  "inventory": [ { "type": "file", "path": "..." }, { "type": "git-ref", "repo": "tupay.git", "ref": "refs/heads/main", "object": "<oid>" } ],
  "files": [ { "type": "file", "path": "...", "sha256": "<hex>", "status": "present"|"gone" },
             { "type": "git-ref", "repo": "tupay.git", "ref": "...", "object": "<oid>", "status": "present"|"gone" } ] }
```
`manifest_complete(seq)`: every `inventory` entry has a matching `files` entry, by path or by (repo, ref), with status `present` or `gone`.

### 6.4 The channel's record [A6]
`hosts/CHANNEL/record.jsonl`, one notice per line: `{"n": 1, "clause": "B1.7", "cause": "...", "seq": 50, "arrival_time": rfc3339, "arrival_host_time": rfc3339, "sender_host": "R", "body": { }}`. `arrival_host_time` is read on the clock of the binding's channel-record host, which is S under binding v1. **A notice reaches the channel exactly when this record holds it.**

### 6.5 Marks and B1.19 [D4]
At any assertion time:
```text
present(seq)          = hosts/R/store/snapshots/<seq>/ and hosts/R/store/manifests/<seq>.json exist
marks(seq)            = the mark entries for seq in R's record copy, in append order
latest_check(seq)     = the last mark in marks(seq) that is restore-checked or restore-failed
marks_restorable(seq) = present(seq) and latest_check(seq) = restore-checked
                        and no damaged or missing mark follows it in marks(seq)
```
If R's record copy is lost or fails its hash, `marks_restorable` is false for every `seq` until a valid copy exists again.

### 6.6 The harness's independent restore [D4, D12]
At a `query` event and, at the horizon, for every `seq` named by a `restores` assertion, the harness copies `hosts/R/store/snapshots/<seq>/` to `harness/restores/<seq>/` and checks it against the manifest. Every `present` file entry must hash to its `sha256` at the path it names inside the snapshot directory. Every `present` git-ref entry must resolve, in a repository restored from the snapshot, to its `object`. That repository is either a bare repository at the repo's path, or a git bundle at `<repo path>.bundle`, cloned with `git clone`. It records `{"seq": n, "time": rfc3339, "result": "restores"|"does-not-restore", "diff": [ ... ]}` in `results.json`. This check runs with the harness's own tools, never the implementation's.

### 6.7 `clock-steps.jsonl` [D8]
`{"time": rfc3339, "host": HostId, "delta": signedDuration}`, one line per BF1.6 injection.

## 7. Scoring
Each assertion is scored at its `at` as `pass`, `fail`, `unreached` (§1.4), `censored` (§1.6) or, for a model, `unsupported` (§8). `results.json` holds the assertion results, the horizon, a recoverability table (`present`, `marks_restorable` and `restores` per `seq`), the censored windows, and a coverage map: the BF1 cells injected and the `derives:` tags asserted.

Deadline comparisons in `notice_reached` use the referenced observation's `host_time` plus `within`, against the notice's `arrival_host_time`. A reference to a mark uses the checker's `deadline.started` observation for it when one exists, and otherwise the mark entry's `time`.

## 8. Model runners [A10]
A model's runner accepts the same schedule JSON. It validates it against §1, resolves `binding` and `params` to the same values, and gives events and assertions their abstract meaning: virtual time, per-host clocks, `when` predicates, fault cells and the horizon. In a model, `marks_restorable` and `restores` are state predicates the model defines, and `restores` stands for the harness's independent check. The runner writes a `results.json` in §7's format, or, for whatever it cannot express:
```json
{ "status": "unsupported", "schedule": "<id>", "unsupported": [ { "id": "<event or assertion id>", "field": "...", "reason": "..." } ] }
```
It exits with status 3. It never skips an event or an assertion silently. Every assertion that depends on an unsupported item is scored `unsupported`.

## 9. Harness obligations
1. Create the run directory (§3.1), build the world (§1.3), and launch every role with its environment (§3.3).
2. Provide the clock, timer, control, observation and relay services (§§2 to 4) and the channel process.
3. Validate the schedule against §1, rejecting retired ids and untagged assertions.
4. Run events in order: compute each event's earliest time, advance virtual time to it while firing timers in host-clock deadline order, then wait on `when` in 1-minute virtual steps up to `timeout`, then execute or mark *unreached*.
5. Inject every cell as §5 says, without the implementation's cooperation.
6. Record everything in §6's formats, and never change the implementation's files except by an injection.
7. After the last event, compute the horizon (§1.6), advance to it, run the independent restores (§6.6), evaluate assertions, and write `results.json`.
8. Run the same schedule text unchanged against every implementation, and give model runners the identical file.
9. Need no root, mounts, namespaces or firewall rules, and run a schedule of several weeks in minutes.


===== CONTRACT QUESTIONS RAISED BY ONE DRAFTER (unresolved) =====
## CONTRACT QUESTIONS

1. **B1.16 / BF1.7 — where does the checker "read" held notices?** "the sender keeps the notice where the checker reads" — but the binding puts the channel's record on S, and the checker on R. When S is up and the channel is down, who holds the notice, and on which host? I could not design the BF1.7 injection's observation (whether a held notice is observable before delivery) without knowing this.
2. **B1.7 — "B1.19 being violated" as a trigger.** B1.19 is a state ("there is always a protected snapshot…"), not an event. When exactly does the *event* that starts the *D* clock occur — the moment the newest recoverable snapshot's ok-entry passes *G*, or the moment the checker first observes that it has? The two differ under BF1.14 (R suspended) and the Deadlines paragraph says detection is not promised while R is down, but B1.19's trigger time still needs a definition for scoring.
3. **B1.8 — the start of *M*.** "within *M* of its *ok* entry" — the ok entry's time is written by S on S's clock; the deadline is measured by the checker on R's clock. After a BF1.6 step on either host, which reading of "within *M*" governs? The contract allows error "up to the size of the step", but a test needs to know which side's clock the assertion uses.
4. **B1.18 — "both copies are intact but disagree."** Disagree *about what*? The hash covers "its entries", but S's copy holds run entries and merged marks while R's holds marks and copied run entries. May two intact copies legitimately differ (S ahead after a run, before the copy lands)? If so, "disagreement" must mean something narrower (same entry, different content), and the boundary is not stated. This blocks designing the BF1.13 `consistent-rewrite` injection precisely.
5. **B1.4 — "the first daily snapshot of each month for *Mo* months."** With clock steps (BF1.6) a UTC day boundary can be crossed twice or never on a host. Which host's clock defines the UTC day of a snapshot's ok entry, given the entry time is written on S but daily snapshots are presumably identified by the checker on R?
6. **B1.15 — *Q* "measured on the binding's own history."** The comparison baseline is "the previous acknowledged snapshot", but *Q*'s noise band was measured on bundle size, while the clause compares "file count and bytes". Is the *Q* test on count and bytes separately, either, or the larger? The worked cases do not cover it, and the assertion needs the formula.
7. **BF1.10 — "R is reimaged or replaced."** Does the *status record's* R copy survive (it is "R's copy", stored at R)? Worked case 4 implies R's record can exist independently, but BF1.10 says "all its snapshots are lost" and is silent on the record. The injection differs materially (delete `R/record/` or not).
8. **B1.9 — the interval's starting event.** "over an interval of *I* + *X*" starting when? At the previous ok entry, at the start of the run that produces it, or at an arbitrary point the test chooses? The premise's start determines when the assertion's clock starts, and the text does not fix it.

---



===== CONTRACT QUESTIONS RAISED BY THE OTHER DRAFTER (unresolved) =====
# 11. CONTRACT QUESTIONS

Each item below quotes the contract or binding text verbatim and states the injection or observation decision I could not make because of it. None of these are resolved here.

1. **Who records a run that ends without a final entry.** B1.6 says: "When a run ends without a final entry, the next run or the freshness checker, whichever comes first, records it as failed, stage unknown." But the status-record paragraph says: "Only S writes run entries." The freshness checker runs on R, so if only S writes run entries, the checker cannot write the `failed`/`unknown` entry. I cannot decide which copy of the record receives that entry first, so `record_entry` assertions and BF1.1 crash-during-run schedules cannot be judged.

2. **Whether a run may write marks.** B1.13 says: "Every run, and every pass of the checker, compares the snapshots present at R with the protected snapshots in the record, and marks each absent one missing." But the status-record paragraph says: "Marks are written only into R's copy, by the freshness checker, by R's re-verification and by the restore host, and S merges them at its next run." A run is on S and is not in the list of mark writers. I cannot decide whether a run writes `missing` marks into R's copy directly or only the checker does, which changes when BF1.10/BF1.12 losses become observable.

3. **Which copy "the record" is in B1.13.** B1.13 says the comparison is against "the protected snapshots in the record", and protection is defined as: "A snapshot is protected from the moment it is acknowledged until pruning removes it", where acknowledged means "the status record holds an ok entry for it". The contract does not say whether the run's comparison reads S's copy or R's copy, and the two can disagree under B1.18. I cannot fix which copy the harness treats as the source of `missing` marks.

4. **What "protected" means during a both-copies-lost rebuild.** B1.18 says: "if both are lost, the service rebuilds the record within Rb, by listing, re-verifying and restore-checking every snapshot at R; every snapshot present stays protected meanwhile". But "A snapshot is protected from the moment it is acknowledged until pruning removes it", and if both copies are lost there are no ok entries, so nothing is acknowledged. I cannot design the BF1.13 `both`/`lost` injection or observe B1.4 pruning behavior during the rebuild.

5. **Where a corrupt copy is "kept aside".** B1.18 says: "A copy whose hash fails is treated as lost, and is kept aside unchanged as evidence; it is never copied over the other copy." No path, name, or format for the kept-aside copy is given. I cannot observe the evidence copy, so assertions about BF1.13 `corrupt` cannot check it.

6. **What notice a record disagreement sends.** B1.18 says: "if both copies are intact but disagree, run entries follow S's copy and marks follow R's copy, every disagreement is reported under B1.7, and both copies are kept." But B1.7's list is closed: "The freshness checker sends a notice under B1.16 within D of each of these: ..." and record disagreement is not one of the listed events. I cannot decide what `clause` and `cause` fields the notice record must carry for a disagreement.

7. **The "starting event" for a B1.19 violation.** The Deadlines paragraph says: "Every time limit above is measured by the freshness checker from its own starting event, whatever happens to the hosts, and is never suspended, paused or restarted, under any failure." But B1.19 says: "When no such snapshot exists, this clause is violated, whatever the cause, and B1.7 reports it as overdue". A continuously-violated clause has no starting event, so I cannot compute the `within D` deadline for the `overdue` notice.

8. **When B1.19 becomes active.** B1.19 says: "After the first G of operation, there is always a protected snapshot whose latest restore check passed, which has not been marked damaged or missing since, and whose ok entry is younger than G." "Operation" start is never defined (first run? service installation?). I cannot decide at what virtual time a schedule may first assert B1.19.

9. **Which clock measures cross-host deadlines.** The contract says: "Every age is measured on the clock of the host that measures it, so across a clock step an age can be wrong by up to the size of the step." But B1.8 says: "The restore host completes a restore check of every acknowledged snapshot within M of its ok entry", and the ok entry's time is written by S on S's clock while the deadline is "measured by the freshness checker" on R. Likewise B1.7: "the newest acknowledged snapshot becoming older than H". I cannot fix the arithmetic the harness uses to judge "within M"/"within H" under BF1.6 clock steps.

10. **Whose clock judges "younger than G" at the scoring horizon.** B1.19 requires a snapshot "whose ok entry is younger than G". The ok entry's time is S's clock reading; the checker that detects the violation runs on R. I cannot decide which host's clock the harness uses to evaluate recoverability age at the horizon.

11. **What quantity Q applies to in B1.15.** B1.15 says: "A run compares each readable source tree's file count and bytes with the previous acknowledged snapshot. A fall of more than Q in a run that no logged reason names sends a notice under B1.16 within D of the comparison." Q is a fraction (0.05), but the contract does not say whether the fall is in file count, in bytes, or either/both. The manifest "lists every file in the snapshot with its sha256 together with the run's source inventory" — it carries no byte counts, so I cannot even define where the "bytes" figure comes from. I cannot define the observation a B1.15 schedule asserts.

12. **The format of a logged reason.** The contract says: "A logged reason is an entry in the record the binding names, written before the run, that names the source tree and the change." The binding says: "Logged reason (T26) | an entry in `docs/seed-log.md`". No entry schema is given. A schedule cannot inject a logged reason in a form every implementation will recognize, so B1.15's "no logged reason names" condition cannot be tested either way.

13. **How a failed daily check is recorded.** B1.11 says: "After that date the daily check on S fails until the item is decided again and the decision is logged." The daily check is not a run and has no run entry; the contract does not say where its failure is recorded or what "the decision is logged" writes. Schedules whose horizon crosses a review date (e.g. EX1.1's 2026-12-01) cannot be observed for B1.11.

14. **Where undelivered notices are kept.** B1.16 says: "While the channel cannot be reached, the sender keeps the notice where the checker reads, and delivers it within D of the channel coming back." "Where the checker reads" names no record, path, or format, and "the channel coming back" is an event on no named host's clock. I cannot observe the pending-notice spool for BF1.7, nor verify the redelivery deadline.

15. **Whether a partitioned host can still reach the notice channel.** BF1.2 says: "Any two of S, R and the restore host are partitioned, for any length of time." The contract separately says: "Notices go to a notice channel; the binding states which hosts the channel depends on", and binding-tupay says the channel's "record is on S". The contract does not say whether R can still send to the channel while S and R are partitioned. I cannot design combined BF1.2 + BF1.7 schedules or judge B1.16 delivery during a partition.

16. **The scope of BF1.3.** BF1.3 says: "Stored bytes at R are silently corrupted." It does not say whether "stored bytes at R" includes R's status-record copy and manifests or only snapshot payloads; BF1.13 separately covers the record. I cannot decide what the harness may corrupt for BF1.3 without overlapping BF1.13.

17. **The scope of BF1.12.** BF1.12 says: "Some snapshots at R are lost by something other than the service." It does not say whether "snapshots" includes their manifests. B1.13 "marks each absent one missing" — absent payload or absent manifest? I cannot define `snapshot_present` versus a `missing` mark precisely.

18. **The degree of BF1.4.** BF1.4 says: "A disk on R or S fills." It does not say whether the disk fills completely or partially. That changes B1.9's "not full" premise and whether B1.17 capture retries can succeed, so I cannot fix the injection's observable effect.

19. **Where a BF1.6 clock-step error is "reported".** BF1.6 says: "The tests inject steps of ±1 h and ±24 h, and the error is reported." No clause, notice, or record is named for this report. I cannot observe it.

20. **Which host prunes, and on which clock "younger than T" is measured.** B1.4 says: "Pruning never removes the newest snapshot that passed its restore check and has not since been marked damaged. It also never removes: any snapshot younger than T; any daily snapshot younger than K; the first daily snapshot of each month for Mo months." The contract never names the host that runs pruning, and "A daily snapshot is the acknowledged snapshot with the highest sequence number in its UTC day" plus "a month is a UTC calendar month" do not say whose clock defines the UTC day. I cannot judge B1.4 retention assertions under BF1.6.

21. **How "being rebuilt" is observable.** B1.4 says: "It removes nothing while the status record is being rebuilt." The status record's entries and hash carry no rebuild state. I cannot observe when pruning is paused during a BF1.13 both-lost rebuild.

22. **What interval B1.9 quantifies over.** B1.9 says: "Suppose that, over an interval of I + X, S and R stay up, connected and not full, and every source file can be captured untorn. Then by the end of that interval an ok entry exists with a higher number than every number acknowledged at its start." "An interval" is not bounded or located, and no clock is named for "the end of that interval". A schedule cannot assert B1.9 without the harness choosing intervals the contract does not define.

23. **What "since" means in B1.3/B1.4/B1.19.** B1.3 says: "A protected snapshot whose latest restore check passed, and which has not been marked damaged or missing since, is restorable." B1.4 says "has not since been marked damaged". "Since" could mean since the check by record order or by timestamp; under BF1.6 clock steps these diverge. I cannot define the ordering the harness uses to compute `recoverable(seq)`.

24. **What "new commits" means for the B1.5 scan.** B1.5 says: "Each run scans the material that is new since the previous acknowledged snapshot (for a git repository, the new commits) with the binding's credential detector." The contract does not define "new" (by object reachability between the previous bundle's refs and the new inventory?). I cannot decide what source mutation a schedule must inject to make a `no-credentials` failure observable.

25. **Who deletes a path that becomes "gone".** B1.17 says: "The manifest holds every path in the run's source inventory, or lists it as gone when it was deleted after the inventory was read." It does not say whether the deleter is the run itself or an external writer (BF1.5). This changes whether `gone` manifest entries are expected in BF1.5 schedules.

26. **Whether the staleness notice lapses when a newer snapshot is acknowledged.** B1.7 requires a notice within D of "the newest acknowledged snapshot becoming older than H". If a newer snapshot is acknowledged before H elapses, the contract does not say whether the obligation for the older snapshot disappears. I cannot decide whether the notice is still required.

27. **Whether the initial verification counts as the "previous verification".** B1.12 says: "R verifies every protected snapshot again within P of its previous verification, without needing S." It does not say whether the verification at snapshot creation is the first "previous verification". I cannot compute the first P deadline a schedule may assert.

28. **Whether the B1.19 cause list is exhaustive.** B1.19 says: "When no such snapshot exists, this clause is violated, whatever the cause, and B1.7 reports it as overdue, naming the cause: failed checks, failed runs, failed captures, or an unavailable host." "Whatever the cause" sits next to a four-item list. I cannot enumerate the `cause` values the notice record must be able to carry.