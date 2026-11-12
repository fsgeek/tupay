# Verified backup: a generic contract and failure model (DRAFT 7, four-part form; not registered)

**Draft 7** (2026-11-12) corrects a defect that draft 6 introduced. Draft 6 had turned B1.8 into a completion obligation and narrowed B1.3 to snapshots that had passed a check. A service that always failed its restore checks, and reported each failure, could therefore pass, and **nothing obliged the service to produce a recoverable backup** (Codex's fourth review, finding 1). The policy is now stated: **this service promises recoverable backups, not verified copies plus failure reports.** B1.19 is that promise. Two further fixes: B1.9's premise includes capturability, and B1.18's precedence rule now matches its example. Draft 6's "frozen" stopped review rounds; it did not stop corrections to a core guarantee (log, 2026-11-12).

**Draft 6** (2026-11-12) is a bounded correction of draft 5 after Codex's third review (`review/codex-3/`). All six findings, and the T20 residue, lay in text that draft 4 had added, so each fix narrows or removes text. §12 gives a concrete execution example for each fix. **The draft is now frozen:** later defects go to the model author and to divergence, not to more review rounds (log, 2026-11-12).

Draft 5 (2026-11-12) splits draft 4 in two:
- **this generic contract**, whose parties are **roles**;
- **a binding** that maps those roles to machines, directories and values. Tupay's binding is `binding-tupay.md`, and it holds what draft 4's §A, §6 values, §9 and §10 held.

Tony asked whether the proposal was generic or specific (log, 2026-11-11). It was specific in its parties and generic in its clauses. The split means a change of host, such as the Fedora move, changes a binding, not the contract. Other residents' bindings are offered, never assumed.

Apart from the split, the obligations are draft 4's, unchanged: no clause was added, removed or weakened. The changes are listed in the log entry of the day, and every one is mechanical. The four-part form is still the treatment arm of a registered test, not tupay's practice.

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

## 7. Gaps found since draft 1
- Gaps 1 to 5 of drafts 2 and 3 are closed: B1.12, B1.7 with T23, B1.13, B1.15, and the key clauses, which are now v2.
- **Gap 6 is open**: no delivery path while S is down (EX1.6).
- **Gap 7 is open**: nothing checks the daily check. The proposal is to fold it into gap 6's answer.
- Codex's eight findings are closed by B1.17, B1.18, the *restore-failed* mark, the class rule, BF1.14, the conditional *Dmax*, and AI1.5's detector.

## 8. What Arariwa observes (not normative)
For each run and each source tree:
- file count, bytes and the change from the last run;
- the time each stage took;
- the age of the newest restore-checked snapshot;
- the age of the last delivered alert-path test.

The steward expects it to raise three things unprompted: slow shrinkage below *Q*, restore checks ageing while verification passes, and an unexercised alert path. Its detection delay is measured from the injection time, for every cell. Restic is measured as a second rung below.

## 11. v2, planned: encryption at rest and the key holder
v2 adds encryption at R under a key held outside S and R. It brings a new authority locus, the **key holder**, after the house's new key management exists. Under the seed's question, this is a contract change that adds a locus to a service with live artifacts, the side of the hyperplane not yet seen. It is planned by tupay, so it is weaker evidence than a change the adversary times, and its registration will say so. The ids retired in §0 are not reused. v2 states encryption afresh.

## 12. Execution examples for draft 6's corrections (each is also a test case)
1. **Completeness (B1.17).** Run 50 reads its inventory. `tupay-homes/a/t.jsonl` is being appended to by an author. Because the file is only appended to, the run copies it up to the length it read, and checks that prefix. A prefix is a version the file really had, so it is captured untorn, and run 50 is acknowledged. A different file, `state.db`, is **rewritten in place** faster than the run can capture it twice the same. Run 50 fails at *capture*, B1.7 sends a notice within *D*, and nothing is acknowledged until a run captures `state.db` untorn. **No acknowledged snapshot lacks either file.**
2. **Restore (B1.3, B1.8).** Run 60 is acknowledged at 11:20. At 13:00 its restore check completes and fails: one file differs. The restore host writes *restore-failed*. B1.8 is discharged, because the check completed. B1.7 sends a notice. B1.3 does not cover snapshot 60. Pruning keeps run 59, the newest *restore-checked* snapshot, under B1.4.
3. **Deadlines.** Run 70 is acknowledged at 11:20 on day 1, and the box is suspended from 12:00 on day 1 to 09:00 on day 3. At 11:20 on day 2, *M* has passed. The checker on R reports snapshot 70 as *overdue*, with the cause "restore host suspended". The deadline is not restarted when the box returns. The overdue report stands until a check of snapshot 70 completes.
4. **Sequence numbers (T5a).** Run 42 writes *started 42* to R's record, then fails before making a snapshot. S's record is then lost. The next run computes max(S: none, R's record: 42, R's snapshots: 41) + 1 = **43**. If R's record had also been lost, it would compute 42 again, and the contract makes no claim in that case, as T5a says.
5. **Corrupted record (B1.18).** S's copy fails its hash. R's copy passes. S sets its copy aside unchanged, takes R's copy, and B1.7 sends a notice. If both copies pass but disagree about run 44's run entry, S's copy wins. If they disagree about a mark on snapshot 44, R's copy wins, because marks are written only there. Either disagreement is reported.
6. **Inventory (T28).** At the start of run 80 the inventory reads `refs/heads/main` → `abc123`. A commit then moves `main` to `def456` during the run. The bundle contains `main` = `abc123`, and run 81 captures `def456`. A file created at 11:21 and deleted at 11:22, during run 80, is in no inventory and no manifest, and no clause claims it.
7. **Recoverable (B1.19), draft 7.** *G* = 72 h. Runs 90 to 93 are acknowledged daily, and each restore check completes with *restore-failed*: a restore-procedure bug. B1.8 is discharged each day. B1.3 covers none of these snapshots. Snapshot 89, the newest *restore-checked*, is kept by B1.4. At 72 h after run 89's *ok* entry, **B1.19 is violated**, and B1.7 reports it as *overdue*, with the cause "restore checks failing". The service is failing its contract, and the record says so, rather than passing because it reported each failure.
8. **Capture and liveness (B1.9, B1.17).** `state.db` is rewritten in place continuously from day 1. Every run fails at *capture*. B1.9's premise is false, so B1.9 is vacuous. **B1.19 is not vacuous:** once the newest recoverable snapshot passes *G*, it is violated and reported. Capturability is an assumption of liveness, and never an excuse for the recovery guarantee.
