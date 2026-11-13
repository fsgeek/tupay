# Verified backup: contract and failure model (prose form, for the comparison arm; DRAFT 1, not registered)

This is the same contract as `contract-draft-7.md`, written as ordinary prose. It is the **comparison arm** of the test of the four-part form. It carries the same obligations, ids and effects, but not the four-part form's vocabulary rules, numbered terms, interpretation records, clause classes or worked examples. An outside review checks that the two forms carry the same obligations before either is used. Ids are never reused.

## Parties and terms
The service backs up some **sources** (directories, and possibly git repositories) from a **source host S** to a **store R**, which is a separate machine reached over a network. **Snapshots** are restore-checked on a **restore host**, which has no copy of the sources and no path to S's files. A **freshness checker** runs on R. Notices go to a **notice channel**. A separate binding document says which machines, directories, channel and parameter values these are, and which hosts can be suspended. Credentials and caches, as the binding defines them, are never part of the sources.

Each run gets a sequence number, which orders runs and snapshots; clocks never do. Runs happen one at a time. Before doing anything else, a run records that it has started, in R's copy of the status record. A run that cannot do so does not start. Its number is one more than the highest number found in S's record, R's record or R's snapshot names. So no number is reused while any surviving record or snapshot carries it. If every record and snapshot carrying a number is lost, nothing is promised about that number.

At its start, a run reads the list of every file path in each source tree. For a git repository it instead reads the ref names with their object ids, and it bundles exactly those objects. Files created after this list is read are not part of that run. Each snapshot has a manifest that lists every file and its sha256.

A snapshot is **verified** when R has read every file and every hash has matched the manifest. It is **acknowledged** when the status record holds an *ok* entry for it. A **restore check** copies the snapshot from R to the restore host, clones any repository from its bundle, and compares every file with the manifest. It ends either as *restore-checked*, meaning the snapshot restored and matched, or as *restore-failed*. A snapshot is **restorable** when that procedure, run without S, would reproduce its manifest. Only a passing restore check is evidence of that. A later verification shows only that the checked bytes have not changed since.

The **status record** is kept on S and copied to R after each run. It holds run entries (started, ok or failed, with the stage that failed, which may be "unknown") and snapshot marks (restore-checked, restore-failed, not restore-checked, damaged or missing). Only S writes run entries. Marks are written only into R's copy, by the freshness checker, by R's re-verification and by the restore host, and S merges them at its next run. A snapshot is **protected** from the moment it is acknowledged until pruning removes it.

## Contract v1
- **B1.1** A run writes *ok* only after its snapshot is verified at R and is complete under B1.17.
- **B1.2** A git repository in a snapshot holds exactly the refs and objects read at the run's start. Every other file in a snapshot is a version that existed on S during the run, and no file is torn.
- **B1.3** A protected snapshot whose latest restore check passed, and which has not been marked damaged or missing since, is restorable. A snapshot not yet checked is covered only by B1.8. A snapshot whose check failed is covered by nothing, and B1.7 reports it.
- **B1.4** Pruning never removes the newest snapshot that passed its restore check and has not since been marked damaged. It also never removes:
  - any snapshot younger than *T*;
  - any daily snapshot younger than *K*;
  - the first daily snapshot of each month for *Mo* months.

  While there is less history than that, pruning removes nothing those rules would keep. Pruning never frees space by breaking this clause. It removes nothing while the status record is being rebuilt.
- **B1.5** No credential file is ever written to R or to the restore host. Each run scans the material that is new since the previous acknowledged snapshot (for a git repository, the new commits) with the binding's credential detector. A hit fails the run.
- **B1.6** The record never holds *ok* for a snapshot that B1.1 does not allow. Every *failed* entry names its stage. Once a snapshot is *ok*, the service never records it as failed and never removes it except by pruning. When a run ends without a final entry, the next run or the freshness checker, whichever comes first, records it as failed, stage unknown.
- **B1.7** The freshness checker sends a notice under B1.16 within *D* of each of these:
  - the newest acknowledged snapshot becoming older than *H*;
  - a failed run;
  - B1.8's deadline passing;
  - B1.12's deadline passing;
  - B1.19 being violated;
  - a snapshot being marked restore-failed, damaged or missing.

  A run that fails on S also sends its own notice under B1.16 within *D*.
- **B1.8** The restore host completes a restore check of every acknowledged snapshot within *M* of its *ok* entry, and records the result. A check that completes with *restore-failed* meets this clause and triggers B1.7, but never meets B1.3. At the start of each check, the restore host removes anything left by a check that crashed.
- **B1.9** Suppose that, over an interval of *I* + *X*, S and R stay up, connected and not full, and every source file can be captured untorn. Then by the end of that interval an *ok* entry exists with a higher number than every number acknowledged at its start.
- **B1.11** Every exclusion (EX) and assumption (AI) below carries a review date. After that date the daily check on S fails until the item is decided again and the decision is logged.
- **B1.12** R verifies every protected snapshot again within *P* of its previous verification, without needing S. A mismatch marks the snapshot damaged, and pruning does not count a damaged snapshot towards B1.4.
- **B1.13** Every run, and every pass of the checker, compares the snapshots present at R with the protected snapshots in the record, and marks each absent one missing.
- **B1.15** A run compares each readable source tree's file count and bytes with the previous acknowledged snapshot. A fall of more than *Q* that no logged reason covers sends a notice under B1.16 within *D*. The snapshot is still made and acknowledged. A source tree that cannot be read fails the run.
- **B1.16** A notice reaches the channel within *D* of the event that requires it. While the channel cannot be reached, the sender keeps the notice where the checker reads, and delivers it within *D* of the channel coming back.
- **B1.17** An acknowledged snapshot's manifest holds every path the run listed at its start, or marks it as deleted since the list was read. A path that cannot be captured untorn after one retry fails the run, so no path is ever silently left out. While such a file keeps changing, every run fails and is reported. A renamed file shows as its old path deleted, and the next run picks up its new path.
- **B1.18** Each copy of the status record carries a hash over its entries. A copy whose hash fails is treated as lost, and is kept aside unchanged as evidence; it is never copied over the other copy. Recovery works as follows:
  - if S's copy is lost, S takes R's at its next run;
  - if R's copy is lost, R takes S's;
  - if both are lost, the service rebuilds the record within *Rb*, by listing, re-verifying and restore-checking every snapshot at R; every snapshot present stays protected meanwhile;
  - if both copies are intact but disagree, run entries follow S's copy and marks follow R's copy, every disagreement is reported, and both copies are kept.

  The hash catches accidental corruption, not a copy that is wrong but consistent.
- **B1.19** After the first *G* of operation, there is always a protected snapshot whose latest restore check passed, which has not been marked damaged or missing since, and whose *ok* entry is younger than *G*. **The service promises recoverable backups, not verified copies plus failure reports.** When no such snapshot exists, this clause is violated, whatever the cause, and B1.7 reports it. Checks that complete, and failures that are reported, do not satisfy it.

**Deadlines.** Every time limit above is measured by the freshness checker from its own starting event, and is never paused or restarted when a host is unavailable. When an unavailable host causes a deadline to be missed, the checker reports it as overdue and names the cause. Nothing promises any detection time while R, where the checker runs, is down. The things the service must always do or never do (B1.1, B1.2, B1.4, B1.5, B1.6, B1.17) hold under every failure. A failure can stop the service from acting, but never licenses it to act wrongly. When stored data is lost to the environment (BF1.3, BF1.10, BF1.12, BF1.13), the service is not expected to prevent the loss. It must mark it and report it.

## Failure model v1
- **BF1.1** The backup process crashes at any point, including during a restore check or a re-verification, and restarts. A crash in the middle of a prune still never leaves anything B1.4 keeps removed. Files a crashed check leaves behind are removed at the next check's start.
- **BF1.2** Any two of S, R and the restore host are partitioned, for any length of time.
- **BF1.3** Stored bytes at R are silently corrupted.
- **BF1.4** A disk on R or S fills.
- **BF1.5** Files in the sources are written, deleted or renamed, or refs are updated, during a run. B1.2 and B1.17 are what this cell tests.
- **BF1.6** A clock on any host steps. Every deadline can then be wrong by up to the size of the step, and the error is measured. Order is unaffected, because it follows sequence numbers.
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
- **EX1.6** S down for longer than *H* when the binding's notice channel depends on S, so that the checker sees the silence but cannot tell anyone (2026-12-01).
- **EX1.7** Snapshots are not encrypted at R or on the restore host. Encryption comes in contract v2 (2026-12-01).

**Assumed impossible:**
- **AI1.1** sha256 collisions (2027-11-01).
- **AI1.2** R's hash tool reporting a false match; the restore check rehashes elsewhere (2027-05-01).
- **AI1.3** The host answering as R not being R; a pinned host key (2027-05-01).
- **AI1.4** The restore check secretly reading S; it has no path to S (2027-05-01).
- **AI1.5** A credential entering a source undetected; the per-run scan, whose detector has its own mutation test (2027-05-01).

**Retired ids, never reused:** B1.10, B1.14, BF1.11, AI1.6 and EX1.4.

## Parameters
The binding gives the values. *I* is the run interval. *M* is the restore-check deadline. *P* is the re-verify interval. *H* is the staleness limit. *D* is the notice delay; the checker runs at least every *D*. *X* is the liveness slack. *Q* is the shrink fraction, measured on the binding's own history. *Rb* is the rebuild deadline. *G* is the maximum age of a recoverable snapshot, which must exceed *I* + *X* + *M*. *Dmax* = *I* + *X* + *D*, and *T* = *M* + *Dmax*. Both hold only if the next run succeeds, the damage crosses *Q*, and R and the channel are reachable. *K* and *Mo* are retention choices above *T*.
