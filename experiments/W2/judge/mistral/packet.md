You are a judge. Below are two contract texts, Contract 1 and Contract 2. They are meant to impose the same obligations in two different written forms. Below them are two lists of questions that independent readers raised about them: List 1 was raised about Contract 1, and List 2 about Contract 2.

For every item in each list, decide:
- "grounded": true if the item concerns text that is actually present in its own list's contract (a quotation from it, or a clear reference to a clause, term or cell that it contains); false otherwise.
- "matches": the numbers of the items in the OTHER list that raise the same underlying contract issue (the same open point about the same obligation, term or cell), even if worded differently or quoting the other form's wording. An empty list if none.

Answer with JSON only, exactly in this schema, covering every item number of both lists:
{"list1": [{"n": 1, "grounded": true, "matches": [3]}, ...], "list2": [{"n": 1, "grounded": true, "matches": []}, ...]}

===== CONTRACT 1 =====
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


===== CONTRACT 2 =====
# Verified backup: contract and failure model

**Scope of prescription.** This contract prescribes no protocol and no tooling. It fixes **placement** where independence needs it: the restore host has no path to S (T4), and the freshness checker runs on R (T23).

## 0. Authority
Unless an item says otherwise, the **steward** establishes, interprets, amends and retires every item, and Tony reviews before registration. After registration:
- an interpretation chooses only among readings the text already permits;
- any change of obligation is a new version (`docs/adversary/CHANNEL.md`, amendment 1);
- an author's reading that differs from an interpretation record is a finding, not an error.

**Ids retired in draft 4, never to be reused:** B1.10, B1.14, BF1.11, AI1.6, EX1.4, T7a, T7b, T14 and T27, with encryption (§11).

## 1. Vocabulary rules
These are ASD-STE100's writing rules, not its word list:
- Each defined word has one meaning.
- Each clause sentence states one obligation.
- Sentences are in the active voice and name the actor.
- No "should", "normally", "as needed" or "etc." appears in a normative clause. §8 is not normative.
- Every quantity is a named parameter (§6) or a unit (T19).
- Every "within" names its start event. T12 gives its clock.

## 2. Defined terms (ids never reused)
- **T1 S** (role): the source host the binding names.
- **T2 Sources** (role): the source trees (T20) the binding names, without credentials (T13) or caches (T21).
- **T3 R** (role): the store the binding names. It is physically separate from S and reached over a network.
- **T4 Restore host** (role): the host the binding names. It holds no copy of the sources and has no path to S's files.
- **T5 Run**: one attempt to make a snapshot. Each run has a sequence number that only increases, and T5a says how it is assigned. Sequence numbers order runs and snapshots. Clocks never do.
- **T5a Sequence assignment**:
  - S runs one run at a time.
  - Before a run does anything else, it writes a *started* run entry for its number to R's copy of the status record. A run that cannot write that entry does not start.
  - The number is max(the highest in S's record, the highest in R's record, the highest snapshot name at R) + 1.
  - So a number is never reused while it names a snapshot or appears in any surviving record. If every record and snapshot that carries a number is lost, the contract makes no claim about that number.
- **T6 Snapshot**: the copy of the sources that one run makes. It is stored at R and named by its sequence number.
- **T7c Manifest**: every file in the snapshot with its sha256, together with the run's source inventory (T28). The run writes it and stores it with the snapshot.
- **T8 Verified**: an event. At R, every file of the snapshot was read and matched T7c.
- **T9 Acknowledged**: the status record holds an *ok* run entry for the snapshot.
- **T10 Restore-checked**: an event. On the restore host, the snapshot was copied from R, any git repository was cloned from its bundle, and every file was compared with T7c, and every file matched.
- **T11 Restorable** at time *t*: the restore procedure, run on the restore host with S unavailable, would produce bytes that match T7c.
  - It is a claim about a procedure.
  - **Its evidence is a passing T10.** A later T8 shows only that the bytes checked by that T10 are unchanged. T8 is never evidence on its own.
- **T12 Clock and age**: an age is measured on the clock of the host that measures it. Across a clock step, an age can be wrong by up to the size of the step.
- **T13 Credential**: a file that matches the binding's name patterns, or content that the binding's named detector reports.
- **T15 Status record**: a list of entries, kept at S and copied to R after each run. There are two kinds of entry:
  - a **run entry**: sequence number; *started*, *ok* or *failed*; stage, where *unknown* is a valid stage; times;
  - a **snapshot mark**: sequence number; one of *restore-checked*, *restore-failed*, *not restore-checked*, *damaged* or *missing*; time; writing host.

  Snapshot marks are written only to R's copy, by the freshness checker, by R's re-verification and by the restore host. S merges them at its next run, and never writes a mark.
- **T16 Notice**: a message on the notice channel (T29) that names its clause. A notice **reaches** the channel when the channel's record holds it.
- **T17 Pruning**: the service's deliberate removal of a snapshot from R.
- **T18 Protected set**: every acknowledged snapshot that pruning has not removed.
- **T19 Units**: *h*; *d* = 24 h; *month* = a UTC calendar month.
- **T20 Source tree**: one of the source trees the binding names.
- **T21 Caches** (role): the directories the binding names as caches.
- **T23 Freshness checker**: a process on R. It evaluates B1.7's events, B1.8's and B1.12's deadlines, and B1.13's inventory, at least every *D*.
- **T24 Daily check**: the check B1.11 names. It runs on S once every *I*.
- **T25 Daily snapshot**: the acknowledged snapshot with the highest sequence number in its UTC day.
- **T26 Logged reason**: an entry in the record the binding names, written before the run, that names the source tree and the change.
- **T29 Notice channel** (role): the channel the binding names. The binding states which hosts the channel depends on.
- **T28 Source inventory**: for each source tree, the list of every file path, read once at the start of the run.
  - For a git repository, it is the list of (ref name, object id) pairs, read once at the start. The bundle is built from those object ids, never from names resolved later.
  - Paths created after the inventory is read, including any created and deleted during the run, are not observed, and no clause claims them. The next run's inventory sees whatever then exists.

## 3. Normative clauses (contract v1, draft 5)
Each clause has one of three **classes**, which §5 uses:
- **[service]**: something the service does or never does. It holds under every cell.
- **[deadline]**: an obligation with a time bound that needs named hosts to be available.
- **[preservation]**: something about stored data that environmental loss can defeat.

- **B1.1 [service] (acknowledgement is earned)** The run writes an *ok* run entry only after the snapshot is verified at R and B1.17 holds for it.
- **B1.2 [service] (snapshots are faithful)**
  - A source tree that is a git repository is bundled from T28's (name, object id) pairs, so its refs are exactly those pairs.
  - Every other file is a version that existed at S during the run, and no file is torn.
- **B1.3 [preservation] (restorable)** Every snapshot in the protected set whose latest restore-check mark is *restore-checked*, and that is not marked *damaged* or *missing* since then, is restorable (T11). A snapshot not yet checked is covered by B1.8 only. A snapshot marked *restore-failed* is covered by no clause, and B1.7 reports it.
- **B1.4 [service] (pruning keeps a way back)** Pruning never removes:
  - the newest snapshot that is *restore-checked* and not since marked *damaged*;
  - any snapshot younger than *T*;
  - any daily snapshot younger than *K*;
  - the first daily snapshot of each month, for *Mo* months.

  While less history exists than these need, pruning removes nothing they would keep. Pruning never frees space by breaking this clause. While the status record is being rebuilt (B1.18), pruning removes nothing.
- **B1.5 [service] (no credential leaves S)**
  - The run never writes a credential file to R or to the restore host.
  - The run scans the material new since the previous acknowledged snapshot (for a git repository, the new commits) with the binding's credential detector. A hit fails the run at stage *no-credentials*.
- **B1.6 [service] (the status record does not lie)**
  - The status record never holds *ok* for a snapshot that B1.1 does not permit.
  - Every *failed* entry names a stage.
  - After an *ok* entry, the service never writes *failed* for that sequence number, and the service never removes the snapshot except by pruning.
  - When a run ends without a final entry, the next run or the freshness checker, whichever runs first, writes *failed, stage unknown* for it.
- **B1.7 [deadline] (silence is detected)** The freshness checker sends a notice under B1.16 within *D* of each of these events:
  - the newest acknowledged snapshot becoming older than *H*;
  - a *failed* run entry appearing;
  - B1.8's deadline passing;
  - B1.12's deadline passing;
  - B1.19 being violated (listed here in draft 7, 2026-11-12. B1.19 already required this report, so no obligation changes);
  - a *restore-failed*, *damaged* or *missing* mark being written.

  A run on S that fails also sends its own notice under B1.16 within *D* of failing.
- **B1.8 [deadline] (restore is exercised)**
  - The restore host **completes** a restore check of every acknowledged snapshot within *M* of its *ok* entry. It writes *restore-checked* when the snapshot restored and matched, and *restore-failed* when the check completed and the snapshot did not.
  - Completing with *restore-failed* discharges B1.8 and fires B1.7. It never discharges B1.3, which then does not cover the snapshot.
  - Until a check completes, the record shows *not restore-checked*, which is a state and not a discharge.
  - At the start of each check, the restore host removes any files left by an earlier check that crashed.
- **B1.9 [deadline] (liveness)** If S and R stay up, connected and not full, **and every source path can be captured untorn (B1.17)**, for an interval of *I* + *X*, then at its end an *ok* entry exists with a sequence number higher than every number acknowledged at the interval's start.
- **B1.11 [deadline] (exclusions expire)** Every EX and AI item carries a review date. After that date the daily check fails until the item is decided again and logged.
- **B1.12 [deadline] (the protected set is re-verified)**
  - R verifies every snapshot in the protected set again within *P* of its previous verification. This needs no contact with S.
  - On a mismatch, R writes *damaged*.
  - Pruning does not count a *damaged* snapshot towards B1.4.
- **B1.13 [deadline] (lost snapshots are noticed)**
  - Each run, and each pass of the freshness checker, compares the snapshots present at R with the protected set in the status record.
  - Each absent snapshot gets a *missing* mark.
- **B1.15 [deadline] (a vanished source is reported)**
  - For each readable source tree, the run compares its file count and bytes with the previous acknowledged snapshot.
  - A fall of more than *Q* in a run that no logged reason names sends a notice under B1.16 within *D* of the comparison.
  - The snapshot is still made and acknowledged.
  - An unreadable source tree fails the run at stage *source*.
- **B1.16 [deadline] (notices are delivered)**
  - A notice reaches the notice channel within *D* of the event that requires it.
  - While the notice channel cannot be reached, the sender records the notice where the freshness checker reads, and delivers it within *D* of the notice channel becoming reachable.
- **B1.17 [service] (snapshots are complete)**
  - The manifest holds every path in the source inventory (T28), or lists it as *gone* when it was deleted after the inventory was read.
  - When the run cannot capture a path untorn after one retry, the run fails at stage *capture*, and the snapshot is not acknowledged. **No path is ever silently omitted from an acknowledged snapshot.**
  - The accepted cost: while a file cannot be captured, every run fails, and B1.7 reports each failure.
  - A renamed file appears as its old path *gone*. Its new path is captured by the next run.
- **B1.18 [deadline] (the status record recovers)** *New, Codex finding 5. Integrity added in draft 6, after Codex's third review.*
  - Each copy of the status record carries a hash over its entries, rewritten at each update. A copy whose hash does not match is **treated as lost**. It is kept aside unchanged, as evidence, and is never copied over the other copy.
  - When both copies are intact and disagree, **run entries follow S's copy, and snapshot marks follow R's copy.** S writes run entries. Marks are written only to R's copy, by R and by the restore host, which reads from R (T15). Each disagreement is reported under B1.7. Both copies are kept as they were.
  - Limit: the hash detects accidental corruption, not a copy that is consistent but wrong.
  - If S's copy is lost, S restores it from R's copy at its next run.
  - If R's copy is lost, R takes S's copy at the next run.
  - If both are lost, the service rebuilds the record within *Rb*: R lists the snapshots present, re-verifies each, and the restore host restore-checks each one. During the rebuild, every present snapshot keeps B1.4's protection.
- **B1.19 [deadline] (a recoverable backup always exists)** *New, draft 7.*
  - After the first *G* of operation, the protected set always holds a snapshot whose latest check is *restore-checked*, not marked *damaged* or *missing* since then, and whose *ok* entry is younger than *G*.
  - When it does not, B1.19 is **violated**, not discharged. B1.7 reports it as *overdue*, with the cause: failed checks, failed runs, failed captures, or an unavailable host.
  - B1.8 (checks complete) and B1.3 (demonstrated snapshots are restorable) do not satisfy this clause on their own. Only a snapshot that is actually recoverable, and young enough, does.
  - B1.4 already keeps the newest *restore-checked* snapshot, so pruning can never cause a violation of B1.19.

## 4. Interpretation records
**U** marks an assumption that is not yet resolved. These are the steward's readings, one reading among several (§0).
- **I-B1.1** *State, at every ok write.* `ok(n) ⇒ verified_at_R(n) ∧ complete(n) happened before it`. Witness: mutants that write *ok* before verification, or after leaving out a directory, are caught.
- **I-B1.2** *Observation.* The restored bundle's refs equal T28's ref list exactly, ref by ref. Every other file's hash equals a version of it observed at S during the run. Witness: refs updated and files written during the run (BF1.5). **U:** a file rewritten twice during the run can only be checked against observed versions, so the witness samples.
- **I-B1.3** *State.* `∀n ∈ protected: latest_check(n) = restore_checked ∧ ¬(damaged ∨ missing since it)(n) ⇒ restorable(n)`. No other snapshot is in this clause's scope.
- **I-B1.4** *Transition, at every prune.* After a prune, each of the four kept groups is present, as far as the history allows. Witness: these prune mutants are caught: prune by count; remove the newest checked snapshot; free space; prune during ramp-up; prune during a rebuild.
- **I-B1.5** *State, plus a per-run scan.* No credential file at R or on the restore host, and no detector hit in the run's new material. Witnesses: a mutant that drops a name pattern must FAIL, and the detector's own mutation pair (the binding names both).
- **I-B1.6** *State plus transition.* Witnesses: SIGKILL a run mid-copy and check the next entry; `backup-ack-check.sh` (a failure after *ok* neither removes the snapshot nor contradicts its entry).
- **I-B1.7** *Temporal.* For each event *e* in the list, `□(e ⇒ ◇≤D notice-sent)`, on R's clock.
- **I-B1.8** *Temporal.* `□(ok(n) ⇒ ◇≤M check_completed(n))`, where a completed check writes *restore-checked* or *restore-failed*. This is a completion obligation. Success is B1.3's concern, not B1.8's.
- **I-B1.9** *Temporal, conditional.* If the premise holds over [*t*, *t* + *I* + *X*], an *ok* entry for a higher sequence number exists by *t* + *I* + *X*.
- **I-B1.11** *Transition, daily.* Witness: an item dated in the past makes the check FAIL.
- **I-B1.12** *Temporal.* `□(n ∈ protected ⇒ ◇≤P (verified_at_R(n) ∨ damaged(n)))`. Witness: flip a byte at R, then see the mark and the notice within *P* + *D*.
- **I-B1.13** *Observation.* After each comparison, every member of the protected set is present at R or marked *missing*. B1.7 then sends a notice within *D*. Witnesses: delete one snapshot (BF1.12); reimage a scratch R (BF1.10).
- **I-B1.15** *Observation.* Empty a scratch source tree, then see the notice within *D* of the comparison. **U:** slow shrinkage spread over many runs is missed. That is a known limit, left to Arariwa.
- **I-B1.16** *Temporal, conditional.* Either the notice reaches the notice channel within *D*, or it is recorded and then delivered within *D* of the notice channel becoming reachable. **U:** gap 6 (EX1.6).
- **I-B1.17** *Observation.* `ok(n) ⇒ inventory(n) ⊆ manifest_paths(n) ∪ gone(n)`. Witnesses: an implementation mutant that skips a directory is caught. A file rewritten continuously during the run makes the run fail at *capture*, and B1.7 fires. Deletions and renames during the run appear as stated.
- **I-B1.19** *State, at every instant after the first G.* `∃n ∈ protected: latest_check(n) = restore_checked ∧ ¬(damaged ∨ missing since it)(n) ∧ age(ok(n)) < G`. Witnesses: a mutant whose restore checks always fail but are reported is caught, because B1.19 is violated, not satisfied. So is a mutant that keeps capture failing.
- **I-B1.18** *Temporal.* After a loss of both copies, `◇≤Rb rebuilt`, with pruning frozen until the rebuild ends. Witness: delete both copies in a scratch deployment, then time the rebuild.

## 5. Failure model v1 (draft 5) and its effect on each clause
### Cells
- **BF1.1** The backup process crashes at any stage, including during a restore check or a re-verify, and then restarts.
- **BF1.2** A partition between any two of S, R and the restore host, of any length, healed or not.
- **BF1.3** Silent corruption of stored bytes at R.
- **BF1.4** A full disk at R or at S.
- **BF1.5** Writes, deletions, renames and ref updates in the sources during a run.
- **BF1.6** Clock steps at any host.
- **BF1.7** The notice channel is unavailable while S is up.
- **BF1.8** A timer does not fire, at any host.
- **BF1.9** A source tree is moved, emptied or truncated by mistake.
- **BF1.10** R is reimaged or replaced, so all its snapshots are lost.
- **BF1.12** Some snapshots at R are lost or deleted, not by the service.
- **BF1.13** The status record is lost or corrupted at S, at R, or at both.
- **BF1.14** *New, Codex finding 4.* A host is suspended (the binding names which of its hosts can be).

### The class rule (Codex finding 4; it replaces draft 3's blanket H)
- **[service] clauses hold under every cell.** Each cell's injected test checks them. A cell can stop the service from acting; it never licenses the service to act wrongly.
- **[deadline] clauses are never suspended and never restarted** (draft 6; Codex's third review, finding 3).
  - The freshness checker measures each deadline's age from the clause's own start event, whatever happens to the hosts.
  - When an unavailable host (BF1.2, BF1.4, BF1.8, BF1.14) causes a missed deadline, the checker reports it under B1.7 as *overdue* and names the cause.
  - Unavailability explains a missed deadline. It never excuses or resets one.
  - **No detection bound holds while R, the checker's host, is down, and the contract does not claim one.**
- **[preservation] clauses under an environmental loss** (BF1.3, BF1.10, BF1.12, BF1.13) are **replaced by detection**: the loss is marked, under B1.12, B1.13 or B1.18, and reported under B1.7, instead of being prevented. Without a further copy, data lost to BF1.10 or BF1.12 is lost for good (EX1.1).

### Exceptions to the class rule, and pairs that need saying
| Cell | Clause | Effect |
|---|---|---|
| BF1.1 | B1.4 | [service] holds. A crash during a prune never leaves any of B1.4's kept groups removed. This is the hardest case. |
| BF1.1 | B1.8 | Files left by a crashed check are removed at the next check's start (B1.8's last part). Until then they sit on the restore host only. |
| BF1.5 | B1.2, B1.17 | [service] holds. These clauses are what this cell tests. |
| BF1.6 | every [deadline] | Each deadline is wrong by up to the size of the step (T12). The tests inject steps of ±1 h and ±24 h, and the error is reported. Order is unaffected (T5). |
| BF1.7 | B1.16 | B1.16's second part covers it. |
| BF1.9 | B1.1, B1.2, B1.3 | They hold: a faithful copy of a damaged source is correct. B1.15 reports it. |
| BF1.13 (both copies) | B1.4 | Pruning is frozen until B1.18 ends. No known obligation is lost. |
| BF1.14 (the restore host) | B1.8 | Not suspended. Past *M*, the checker on R reports the check *overdue*, with the cause "restore host suspended". |

### Explicitly excluded (each with its review date)
- **EX1.1** S and R lost together, with no further copy. The remedy is the off-site copy, a second contract. Review: 2026-12-01.
- **EX1.2** Deliberate tampering by someone with access to S and R. Review: 2027-05-01.
- **EX1.3** Loss of anything before the first snapshot. Review: 2027-05-01.
- **EX1.5** R's checker and S's runs both stopped for longer than *H*. Review: 2026-12-01.
- **EX1.6** S down for longer than *H*, under a binding whose notice channel depends on S. R sees it, but no notice can reach the channel (gap 6). Each binding states whether this exclusion applies to it. Review: 2026-12-01.
- **EX1.7** *New.* Snapshot contents are plaintext at R and on the restore host. The remedy is v2 (§11). Review: 2026-12-01.

### Assumed impossible (each with its review date)
- **AI1.1** A sha256 collision. *Unwitnessed.* Review: 2027-11-01.
- **AI1.2** R's hash tool reporting a match for bytes that differ. *Witness:* T10 recomputes hashes on another host. Review: 2027-05-01.
- **AI1.3** The host that answers as R being R. *Witness:* a pinned SSH host key. Review: 2027-05-01.
- **AI1.4** The restore check not reading S. *Witness:* the restore host has no path to S. Review: 2027-05-01.
- **AI1.5** No credential enters a source undetected. *Witness:* B1.5's per-run scan with the binding's credential detector. The detector must have its own mutation pair. Its limit: a detector finds only the patterns it knows. Review: 2027-05-01.

## 6. Parameters (names and derivations; **values are the binding's**)
- *I* run interval; *M* restore-check deadline; *P* re-verify interval; *H* staleness, = *I* + slack; *D* notice delay (the checker runs at least every *D*); *X* liveness slack; *Q* shrink fraction, **measured** on the binding's own history; *Rb* rebuild deadline; *G* recoverable age (B1.19), greater than *I* + *X* + *M*, so that one missed run or check does not violate it.
- *Dmax* = *I* + *X* + *D*, **conditional on** the next run succeeding, the damage crossing *Q*, and R and the notice channel being reachable. Under BF1.2, BF1.4, BF1.8 or BF1.14 no bound holds (the class rule).
- *T* = *M* + *Dmax*, with the same conditions. It is a floor.
- *K* (daily keeps) and *Mo* (monthly keeps) are the binding's choices, above *T*.

## 11. v2, planned: encryption at rest and the key holder
v2 adds encryption at R under a key held outside S and R. It brings a new authority locus, the **key holder**, after the house's new key management exists. Under the seed's question, this is a contract change that adds a locus to a service with live artifacts, the side of the hyperplane not yet seen. It is planned by tupay, so it is weaker evidence than a change the adversary times, and its registration will say so. The ids retired in §0 are not reused. v2 states encryption afresh.

## 12. Execution examples for draft 6's corrections (each is also a test case)
1. **Completeness (B1.17).** Run 50 reads its inventory. `tupay-homes/a/t.jsonl` is being appended to by an author. Because the file is only appended to, the run copies it up to the length it read, and checks that prefix. A prefix is a version the file really had, so it is captured untorn, and run 50 is acknowledged. A different file, `state.db`, is **rewritten in place** faster than the run can capture it twice the same. Run 50 fails at *capture*, B1.7 sends a notice within *D*, and nothing is acknowledged until a run captures `state.db` untorn. **No acknowledged snapshot lacks either file.**
2. **Restore (B1.3, B1.8).** Run 60 is acknowledged at 11:20. At 13:00 its restore check completes and fails: one file differs. The restore host writes *restore-failed*. B1.8 is discharged, because the check completed. B1.7 sends a notice. B1.3 does not cover snapshot 60. Pruning keeps run 59, the newest *restore-checked* snapshot, under B1.4.
3. **Deadlines.** Run 70 is acknowledged at 11:20 on day 1, and the box is suspended from 12:00 on day 1 to 09:00 on day 3. At 11:20 on day 2, *M* has passed. The checker on R reports snapshot 70 as *overdue*, with the cause "restore host suspended". The deadline is not restarted when the box returns. The overdue report stands until a check of snapshot 70 completes.
4. **Sequence numbers (T5a).** Run 42 writes *started 42* to R's record, then fails before making a snapshot. S's record is then lost. The next run computes max(S: none, R's record: 42, R's snapshots: 41) + 1 = **43**. If R's record had also been lost, it would compute 42 again, and the contract makes no claim in that case, as T5a says.
5. **Corrupted record (B1.18).** S's copy fails its hash. R's copy passes. S sets its copy aside unchanged, takes R's copy, and B1.7 sends a notice. If both copies pass but disagree about run 44's run entry, S's copy wins. If they disagree about a mark on snapshot 44, R's copy wins, because marks are written only there. Either disagreement is reported.
6. **Inventory (T28).** At the start of run 80 the inventory reads `refs/heads/main` → `abc123`. A commit then moves `main` to `def456` during the run. The bundle contains `main` = `abc123`, and run 81 captures `def456`. A file created at 11:21 and deleted at 11:22, during run 80, is in no inventory and no manifest, and no clause claims it.
7. **Recoverable (B1.19), draft 7.** *G* = 96 h. Runs 90 to 93 are acknowledged daily, and each restore check completes with *restore-failed*: a restore-procedure bug. B1.8 is discharged each day. B1.3 covers none of these snapshots. Snapshot 89, the newest *restore-checked*, is kept by B1.4. At 96 h after run 89's *ok* entry, **B1.19 is violated**, and B1.7 reports it as *overdue*, with the cause "restore checks failing". The service is failing its contract, and the record says so, rather than passing because it reported each failure.
8. **Capture and liveness (B1.9, B1.17).** `state.db` is rewritten in place continuously from day 1. Every run fails at *capture*. B1.9's premise is false, so B1.9 is vacuous. **B1.19 is not vacuous:** once the newest recoverable snapshot passes *G*, it is violated and reported. Capturability is an assumption of liveness, and never an excuse for the recovery guarantee.


===== LIST 1 =====
[1] 1. **Who records a run that ends without a final entry.** B1.6 says: "When a run ends without a final entry, the next run or the freshness checker, whichever comes first, records it as failed, stage unknown." But the status-record paragraph says: "Only S writes run entries." The freshness checker runs on R, so if only S writes run entries, the checker cannot write the `failed`/`unknown` entry. I cannot decide which copy of the record receives that entry first, so `record_entry` assertions and BF1.1 crash-during-run schedules cannot be judged.

[2] 2. **Whether a run may write marks.** B1.13 says: "Every run, and every pass of the checker, compares the snapshots present at R with the protected snapshots in the record, and marks each absent one missing." But the status-record paragraph says: "Marks are written only into R's copy, by the freshness checker, by R's re-verification and by the restore host, and S merges them at its next run." A run is on S and is not in the list of mark writers. I cannot decide whether a run writes `missing` marks into R's copy directly or only the checker does, which changes when BF1.10/BF1.12 losses become observable.

[3] 3. **Which copy "the record" is in B1.13.** B1.13 says the comparison is against "the protected snapshots in the record", and protection is defined as: "A snapshot is protected from the moment it is acknowledged until pruning removes it", where acknowledged means "the status record holds an ok entry for it". The contract does not say whether the run's comparison reads S's copy or R's copy, and the two can disagree under B1.18. I cannot fix which copy the harness treats as the source of `missing` marks.

[4] 4. **What "protected" means during a both-copies-lost rebuild.** B1.18 says: "if both are lost, the service rebuilds the record within Rb, by listing, re-verifying and restore-checking every snapshot at R; every snapshot present stays protected meanwhile". But "A snapshot is protected from the moment it is acknowledged until pruning removes it", and if both copies are lost there are no ok entries, so nothing is acknowledged. I cannot design the BF1.13 `both`/`lost` injection or observe B1.4 pruning behavior during the rebuild.

[5] 5. **Where a corrupt copy is "kept aside".** B1.18 says: "A copy whose hash fails is treated as lost, and is kept aside unchanged as evidence; it is never copied over the other copy." No path, name, or format for the kept-aside copy is given. I cannot observe the evidence copy, so assertions about BF1.13 `corrupt` cannot check it.

[6] 6. **What notice a record disagreement sends.** B1.18 says: "if both copies are intact but disagree, run entries follow S's copy and marks follow R's copy, every disagreement is reported under B1.7, and both copies are kept." But B1.7's list is closed: "The freshness checker sends a notice under B1.16 within D of each of these: ..." and record disagreement is not one of the listed events. I cannot decide what `clause` and `cause` fields the notice record must carry for a disagreement.

[7] 7. **The "starting event" for a B1.19 violation.** The Deadlines paragraph says: "Every time limit above is measured by the freshness checker from its own starting event, whatever happens to the hosts, and is never suspended, paused or restarted, under any failure." But B1.19 says: "When no such snapshot exists, this clause is violated, whatever the cause, and B1.7 reports it as overdue". A continuously-violated clause has no starting event, so I cannot compute the `within D` deadline for the `overdue` notice.

[8] 8. **When B1.19 becomes active.** B1.19 says: "After the first G of operation, there is always a protected snapshot whose latest restore check passed, which has not been marked damaged or missing since, and whose ok entry is younger than G." "Operation" start is never defined (first run? service installation?). I cannot decide at what virtual time a schedule may first assert B1.19.

[9] 9. **Which clock measures cross-host deadlines.** The contract says: "Every age is measured on the clock of the host that measures it, so across a clock step an age can be wrong by up to the size of the step." But B1.8 says: "The restore host completes a restore check of every acknowledged snapshot within M of its ok entry", and the ok entry's time is written by S on S's clock while the deadline is "measured by the freshness checker" on R. Likewise B1.7: "the newest acknowledged snapshot becoming older than H". I cannot fix the arithmetic the harness uses to judge "within M"/"within H" under BF1.6 clock steps.

[10] 10. **Whose clock judges "younger than G" at the scoring horizon.** B1.19 requires a snapshot "whose ok entry is younger than G". The ok entry's time is S's clock reading; the checker that detects the violation runs on R. I cannot decide which host's clock the harness uses to evaluate recoverability age at the horizon.

[11] 11. **What quantity Q applies to in B1.15.** B1.15 says: "A run compares each readable source tree's file count and bytes with the previous acknowledged snapshot. A fall of more than Q in a run that no logged reason names sends a notice under B1.16 within D of the comparison." Q is a fraction (0.05), but the contract does not say whether the fall is in file count, in bytes, or either/both. The manifest "lists every file in the snapshot with its sha256 together with the run's source inventory" — it carries no byte counts, so I cannot even define where the "bytes" figure comes from. I cannot define the observation a B1.15 schedule asserts.

[12] 12. **The format of a logged reason.** The contract says: "A logged reason is an entry in the record the binding names, written before the run, that names the source tree and the change." The binding says: "Logged reason (T26) | an entry in `docs/seed-log.md`". No entry schema is given. A schedule cannot inject a logged reason in a form every implementation will recognize, so B1.15's "no logged reason names" condition cannot be tested either way.

[13] 13. **How a failed daily check is recorded.** B1.11 says: "After that date the daily check on S fails until the item is decided again and the decision is logged." The daily check is not a run and has no run entry; the contract does not say where its failure is recorded or what "the decision is logged" writes. Schedules whose horizon crosses a review date (e.g. EX1.1's 2026-12-01) cannot be observed for B1.11.

[14] 14. **Where undelivered notices are kept.** B1.16 says: "While the channel cannot be reached, the sender keeps the notice where the checker reads, and delivers it within D of the channel coming back." "Where the checker reads" names no record, path, or format, and "the channel coming back" is an event on no named host's clock. I cannot observe the pending-notice spool for BF1.7, nor verify the redelivery deadline.

[15] 15. **Whether a partitioned host can still reach the notice channel.** BF1.2 says: "Any two of S, R and the restore host are partitioned, for any length of time." The contract separately says: "Notices go to a notice channel; the binding states which hosts the channel depends on", and binding-tupay says the channel's "record is on S". The contract does not say whether R can still send to the channel while S and R are partitioned. I cannot design combined BF1.2 + BF1.7 schedules or judge B1.16 delivery during a partition.

[16] 16. **The scope of BF1.3.** BF1.3 says: "Stored bytes at R are silently corrupted." It does not say whether "stored bytes at R" includes R's status-record copy and manifests or only snapshot payloads; BF1.13 separately covers the record. I cannot decide what the harness may corrupt for BF1.3 without overlapping BF1.13.

[17] 17. **The scope of BF1.12.** BF1.12 says: "Some snapshots at R are lost by something other than the service." It does not say whether "snapshots" includes their manifests. B1.13 "marks each absent one missing" — absent payload or absent manifest? I cannot define `snapshot_present` versus a `missing` mark precisely.

[18] 18. **The degree of BF1.4.** BF1.4 says: "A disk on R or S fills." It does not say whether the disk fills completely or partially. That changes B1.9's "not full" premise and whether B1.17 capture retries can succeed, so I cannot fix the injection's observable effect.

[19] 19. **Where a BF1.6 clock-step error is "reported".** BF1.6 says: "The tests inject steps of ±1 h and ±24 h, and the error is reported." No clause, notice, or record is named for this report. I cannot observe it.

[20] 20. **Which host prunes, and on which clock "younger than T" is measured.** B1.4 says: "Pruning never removes the newest snapshot that passed its restore check and has not since been marked damaged. It also never removes: any snapshot younger than T; any daily snapshot younger than K; the first daily snapshot of each month for Mo months." The contract never names the host that runs pruning, and "A daily snapshot is the acknowledged snapshot with the highest sequence number in its UTC day" plus "a month is a UTC calendar month" do not say whose clock defines the UTC day. I cannot judge B1.4 retention assertions under BF1.6.

[21] 21. **How "being rebuilt" is observable.** B1.4 says: "It removes nothing while the status record is being rebuilt." The status record's entries and hash carry no rebuild state. I cannot observe when pruning is paused during a BF1.13 both-lost rebuild.

[22] 22. **What interval B1.9 quantifies over.** B1.9 says: "Suppose that, over an interval of I + X, S and R stay up, connected and not full, and every source file can be captured untorn. Then by the end of that interval an ok entry exists with a higher number than every number acknowledged at its start." "An interval" is not bounded or located, and no clock is named for "the end of that interval". A schedule cannot assert B1.9 without the harness choosing intervals the contract does not define.

[23] 23. **What "since" means in B1.3/B1.4/B1.19.** B1.3 says: "A protected snapshot whose latest restore check passed, and which has not been marked damaged or missing since, is restorable." B1.4 says "has not since been marked damaged". "Since" could mean since the check by record order or by timestamp; under BF1.6 clock steps these diverge. I cannot define the ordering the harness uses to compute `recoverable(seq)`.

[24] 24. **What "new commits" means for the B1.5 scan.** B1.5 says: "Each run scans the material that is new since the previous acknowledged snapshot (for a git repository, the new commits) with the binding's credential detector." The contract does not define "new" (by object reachability between the previous bundle's refs and the new inventory?). I cannot decide what source mutation a schedule must inject to make a `no-credentials` failure observable.

[25] 25. **Who deletes a path that becomes "gone".** B1.17 says: "The manifest holds every path in the run's source inventory, or lists it as gone when it was deleted after the inventory was read." It does not say whether the deleter is the run itself or an external writer (BF1.5). This changes whether `gone` manifest entries are expected in BF1.5 schedules.

[26] 26. **Whether the staleness notice lapses when a newer snapshot is acknowledged.** B1.7 requires a notice within D of "the newest acknowledged snapshot becoming older than H". If a newer snapshot is acknowledged before H elapses, the contract does not say whether the obligation for the older snapshot disappears. I cannot decide whether the notice is still required.

[27] 27. **Whether the initial verification counts as the "previous verification".** B1.12 says: "R verifies every protected snapshot again within P of its previous verification, without needing S." It does not say whether the verification at snapshot creation is the first "previous verification". I cannot compute the first P deadline a schedule may assert.

[28] 28. **Whether the B1.19 cause list is exhaustive.** B1.19 says: "When no such snapshot exists, this clause is violated, whatever the cause, and B1.7 reports it as overdue, naming the cause: failed checks, failed runs, failed captures, or an unavailable host." "Whatever the cause" sits next to a four-item list. I cannot enumerate the `cause` values the notice record must be able to carry.

===== LIST 2 =====
[1] 1. **Which timers BF1.8 covers.**  
   > "BF1.8 A timer does not fire, at any host."  
   The interface can suppress only timers the implementation labels in `wait_until`. Internal implementation timers that are not contract-visible cannot be selected by the harness without implementation cooperation. Which timers are in scope for BF1.8?

[2] 2. **What "any stage" means in BF1.1.**  
   > "BF1.1 The backup process crashes at any stage, including during a restore check or a re-verify, and then restarts."  
   The contract names stages such as `no-credentials`, `capture`, `source`, and `unknown`, but "any stage" includes internal stages the harness cannot observe. The interface can crash at any virtual time or on observable events (`run_started`, `restore_check_started`, `reverify_started`), but cannot know an unobservable internal stage. What counts as a "stage" for BF1.1?

[3] 3. **Whether a suspended host's clock advances.**  
   > "BF1.14 ... A host is suspended (the binding names which of its hosts can be)."  
   > "T12 Clock and age: an age is measured on the clock of the host that measures it. Across a clock step, an age can be wrong by up to the size of the step."  
   If a host is suspended, does its own clock advance during the suspension? This affects deadlines measured on that host (for example the daily check on S) and the meaning of suspension versus BF1.6.

[4] 4. **Where undelivered notices are recorded under B1.16.**  
   > "B1.16 ... While the notice channel cannot be reached, the sender records the notice where the freshness checker reads, and delivers it within D of the notice channel becoming reachable."  
   The contract does not name the record, host, or path "where the freshness checker reads". The binding says the notice channel's record is on S and the freshness checker runs on R. Which record holds queued notices?

[5] 5. **BF1.7 versus a notice-channel record on S.**  
   > "BF1.7 The notice channel is unavailable while S is up."  
   > Binding: "Notice channel (T29) | the plaza, as guest:tupay. Its record is on S, so EX1.6 applies to this binding."  
   If the channel's record is on S and S is up, what exactly is unavailable during BF1.7 — the channel endpoint, the plaza service, or the record file? Does the harness still append to the record on S while the channel is "unavailable"?

[6] 6. **What exactly the B1.18 status-record hash covers.**  
   > "B1.18 ... Each copy of the status record carries a hash over its entries, rewritten at each update. A copy whose hash does not match is treated as lost."  
   The contract does not say which bytes are hashed (entry lines only? canonical serialization? including the digest line?), nor the hash algorithm. The interface needs this to verify and to inject BF1.13 corruption consistently.

[7] 7. **What B1.15's `Q` is a fraction of.**  
   > "B1.15 ... For each readable source tree, the run compares its file count and bytes with the previous acknowledged snapshot. A fall of more than Q in a run that no logged reason names sends a notice..."  
   > Binding: "Q = 0.05. Measured 2026-11-11 from 9 quiet runs. ... the bundle's size moved between −0.87 % and +1.32 %."  
   Is the "fall of more than Q" measured on file count, on bytes, or on both? Relative to the previous acknowledged snapshot's count/bytes, or to the current inventory?

[8] 8. **When "operation" starts for B1.19.**  
   > "B1.19 ... After the first G of operation, the protected set always holds a snapshot whose latest check is restore-checked, not marked damaged or missing since then, and whose ok entry is younger than G."  
   Does "operation" start at the first run attempt, the first `ok` entry, service installation, or schedule `t0`? The interface needs this to judge B1.19 at the scoring horizon.

[9] 9. **What BF1.10 destroys besides snapshots.**  
   > "BF1.10 R is reimaged or replaced, so all its snapshots are lost."  
   Does BF1.10 also destroy R's copy of the status record, the freshness checker's local state, and the notice spool, or only the snapshots? "Reimaged or replaced" suggests the whole host, but the clause only explicitly says snapshots are lost.

[10] 10. **What "full disk" means for BF1.4.**  
    > "BF1.4 A full disk at R or at S."  
    The binding gives no disk capacity or utilization threshold. What capacity and fill level define "full" in a test, and is it ENOSPC on any write or a specific utilization?