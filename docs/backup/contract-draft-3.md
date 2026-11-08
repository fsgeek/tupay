# Verified backup: contract and failure model (DRAFT 3, four-part form; not registered)

The twelfth steward, 2026-11-08. Draft 3 applies the dispositions of Qwen's review of draft 2 (`review/qwen/DISPOSITIONS.md`: 40 findings, all accepted, 3 of them in part). Draft 2 is `contract-draft-2.md`. The four-part form is **the treatment arm of a registered test, not tupay's practice** (log, 2026-11-07). The prose arm is derived from this text at registration and carries the same obligations.

**Scope of prescription.** The contract prescribes no protocol and no tooling. It does fix **placement** where independence needs it: the restore host has no path to S (T4), the freshness checker is not on S (B1.7), and the key has a copy outside S, R and the restore host (B1.14).

## 0. Authority
Unless an item says otherwise, the **steward** establishes, interprets, amends and retires every term, clause, cell and record here, and Tony reviews before registration. After registration:
- an interpretation may only choose among readings the text already permits;
- anything that changes an obligation is a new version (`docs/adversary/CHANNEL.md`, amendment 1);
- where an author's reading differs from an interpretation record, that is a **finding** to be judged, not an error to correct.

## 1. Vocabulary rules
These are ASD-STE100's writing rules, not its word list:
- A word defined in §2 has only that meaning. An undefined word has its ordinary meaning, and is used only where no defined term applies.
- A clause sentence states one obligation.
- Normative sentences use the active voice and name the party that acts.
- A normative clause never uses "should", "normally", "as needed" or "etc." §8 is not normative.
- Every quantity is a named parameter (§6) or a defined unit (T19).
- Every "within" names its start event. Its clock is the one T12 gives.

## 2. Defined terms (ids never reused)
- **T1 S**: the source host, this machine (WAM-THREADRIPPER under WSL). **The plaza's record is on S** (T16).
- **T2 Sources**: three source trees (T20): tupay's git repository, every ref; `tupay-private/`; and `tupay-homes/` without credentials (T13) or caches (T21).
- **T3 R**: the store, wam-nuc. It is physically separate from S and reached over the network.
- **T4 Restore host**: the host where restore checks run, the box (T22). It holds no copy of the sources and has no path to S's files.
- **T5 Run**: one attempt to make a snapshot. S gives each run a sequence number that only increases. Runs and snapshots are ordered by that number, never by a clock.
- **T6 Snapshot**: the copy of the sources one run produces, stored at R and named by its run's sequence number.
- **T7a Plaintext manifest**: every file of the snapshot with its plaintext sha256. The run writes it, encrypts it, and stores it with the snapshot.
- **T7b Ciphertext manifest**: every stored object of the snapshot with its ciphertext sha256. The run writes it and stores it with the snapshot unencrypted.
- **T8 Verified**: an event. At R, every stored object of the snapshot was read and matched T7b. It needs no key.
- **T9 Acknowledged**: the status record holds an *ok* run entry for the snapshot (B1.1 says when that is permitted).
- **T10 Restore-checked**: an event. On the restore host, the snapshot was copied from R, decrypted with the escrowed key, and every file was compared with T7a, and all matched.
- **T11 Restorable** at time *t*: the restore procedure would produce bytes that match T7a, when it is run on the restore host with S unavailable, using the escrowed key or a copy reinstalled from Tony's (T14). **This is a claim about a procedure.** Its evidence is a T10 or T8 event newer than the last event that could damage the snapshot.
- **T12 Clock and age**: an age or a "within" is measured on the clock of the host that measures it. Across a clock step, an age can be wrong by up to the size of the step (BF1.6).
- **T13 Credential**: a file that matches the patterns in `scripts/steward/backup.sh` (`auth.json`, `.credentials.json`, `*credential*`), or content that a secrets scan of the kind run on 2026-11-03 would report.
- **T14 Escrowed key**: the key that encrypts snapshots. The restore host holds one copy, and Tony holds one copy "in a safe place" (2026-11-07). S holds a copy only so that it can encrypt. R holds none.
- **T15 Status record**: a list of entries, kept at S and copied to R after each run. Each entry is one of two kinds:
  - a **run entry**: sequence number; result *ok* or *failed*; stage, which may be *unknown*; times;
  - a **snapshot mark**: sequence number and one of *restore-checked*, *not restore-checked*, *damaged* or *missing*, with its time and the host that wrote it.

  The freshness checker writes its entries to R's copy, and S merges them into its own at the next run.
- **T16 Notice**: a post to the plaza naming the clause it reports. A notice **reaches** the plaza when the plaza's record holds it. Because the plaza is on S, a notice cannot reach it while S is down or unreachable (B1.16).
- **T17 Pruning**: the deliberate removal of a snapshot from R.
- **T18 Retained span**: the snapshots that B1.4 requires pruning to keep.
- **T19 Units**: *h* (hour), *d* (day = 24 h), and *month* (a UTC calendar month).
- **T20 Source tree**: one of the three parts of T2.
- **T21 Caches**: directories named `.cache` or `go`, and module or package caches, under `tupay-homes/`.
- **T22 The box**: the `ubuntu26-test` VM. Tony can suspend it for other residents (2026-10-28).
- **T23 Freshness checker**: the process that evaluates B1.7's conditions, B1.8's and B1.12's deadlines, and B1.13's inventory. It runs on R.
- **T24 Daily check**: the check that B1.11 names. It runs on S once every *I*.
- **T25 Daily snapshot**: the acknowledged snapshot with the highest sequence number in each UTC day.
- **T26 Logged reason**: an entry in tupay's log, written before the run, that names the source tree and the change.
- **T27 Restore-check host's plaintext**: the decrypted files during a restore check.

## 3. Normative clauses (contract v1, draft 3)
Each clause names its start events. Ids B1.1 to B1.11 are from draft 1; B1.12 to B1.15 were added in draft 2 (gaps 1, 3, 4 and 5, §7); B1.16 is new in draft 3 (Qwen's finding 3).

- **B1.1 (acknowledgement is earned)** The run writes an *ok* run entry for a snapshot only after the snapshot is verified at R.
- **B1.2 (snapshots are faithful)** In a snapshot, the repository is one consistent state of every ref. Every other file is a version that existed at S during the run. No file is torn.
- **B1.3 (restorable)** Every acknowledged snapshot that is not pruned, not marked *damaged* and not marked *missing* is restorable (T11), except as §5 states.
- **B1.4 (pruning keeps a way back)**
  - Pruning never removes the newest snapshot whose last restore check passed.
  - Pruning keeps every snapshot whose sequence number lies within *T* of the newest acknowledged snapshot, measured by age.
  - Within that span and beyond it, pruning keeps every daily snapshot (T25) for *K* d and the first daily snapshot of each month for *Mo* months.
  - These hold for the history that exists. While less history exists than they require, pruning removes nothing that any of them would keep.
  - Pruning never removes a snapshot to free space when the removal would break this clause.
- **B1.5 (no credential leaves S)**
  - The run never writes a credential file to R or to the restore host.
  - For the repository, whose contents travel inside a bundle, this clause rests on AI1.5.
- **B1.6 (the status record does not lie)**
  - The status record never holds *ok* for a snapshot that B1.1 does not permit.
  - Every *failed* run entry names a stage, and *unknown* is a stage.
  - After an *ok* run entry, nothing writes a *failed* run entry for the same sequence number, and nothing removes the snapshot except pruning.
  - When a run ends without a final run entry, the next run or the freshness checker, whichever runs first, writes *failed, stage unknown* for that sequence number.
- **B1.7 (silence is detected)** The freshness checker sends a notice under B1.16 within *D* of each of these events:
  - the newest acknowledged snapshot becoming older than *H*;
  - a *failed* run entry appearing in R's copy of the status record;
  - B1.8's deadline passing for a snapshot that is not restore-checked;
  - B1.12's deadline passing for a retained snapshot that has not been re-verified.

  A run on S that fails also sends a notice under B1.16 within *D* of its failure. That is S's own failure notice; it supplements the checker and does not replace it.
- **B1.8 (restore is exercised)**
  - The restore host restore-checks every acknowledged snapshot within *M* of its *ok* run entry.
  - The restore host writes the result as a snapshot mark.
  - Until a *restore-checked* mark exists, the status record shows the snapshot as *not restore-checked*.
- **B1.9 (liveness)** If S and R stay up, connected and not full for an interval of *I* + *X*, a new acknowledged snapshot exists at its end.
- **B1.10 (confidential at rest)**
  - Every stored object at R is ciphertext under the escrowed key, and R holds no copy of the key.
  - Plaintext of a snapshot exists outside S only on the restore host during a restore check, and the restore host removes it when the check ends.
- **B1.11 (exclusions expire)** Every EX and AI item carries a review date. After that date the daily check fails until the item is decided again and the decision is logged.
- **B1.12 (retained snapshots are re-verified)**
  - R verifies every snapshot in the retained span again at least every *P* after its previous verification. This needs no key and no contact with S.
  - When a re-verification fails, R writes a *damaged* mark, and the freshness checker sends a notice under B1.16 within *D* of the mark.
  - Pruning does not count a *damaged* snapshot towards B1.4.
- **B1.13 (lost snapshots are noticed)**
  - Each run, and each pass of the freshness checker, compares the set of snapshots present at R with every acknowledged, unpruned sequence number in the status record.
  - For each one that is absent, it writes a *missing* mark and sends a notice under B1.16 within *D* of the comparison.
- **B1.14 (the key is not a single point)**
  - The restore host uses its own copy of the escrowed key and never S's.
  - At least one copy of the key is held outside S, R and the restore host (AI1.6).
- **B1.15 (a vanished source is reported)**
  - For each source tree that is readable, the run compares its file count and bytes with the previous acknowledged snapshot.
  - A fall of more than a fraction *Q*, in a run that no logged reason (T26) names, makes the run send a notice under B1.16 within *D* of the comparison.
  - The run still takes and acknowledges the snapshot, because a faithful copy of a damaged source is faithful.
  - A source tree that is not readable fails the run at stage *source*.
- **B1.16 (notices are delivered)** *New, draft 3.* A notice reaches the plaza within *D* of the event that requires it. While the plaza cannot be reached, the sender records the notice where the freshness checker reads, and sends it to the plaza within *D* of the plaza becoming reachable. **Open (gap 6, §10 question 1):** while S is down, no notice can reach anyone this contract names.

## 4. Interpretation records
Each record gives its form, its interpretation, its witness and its assumptions. **U** marks an assumption that is unresolved. These records are the steward's reading, which is one reading among several (§0).

- **I-B1.1** *State, at every ok write.* `ok(n) ⇒ verified_at_R(n) happened before it`. Witness: a mutant that writes *ok* before verification is caught. Assumes only the run writes *ok* run entries.
- **I-B1.2** *Observation.* After restore, `git bundle verify` passes and every ref resolves. Every other file's hash equals a version of that file observed at S during the run window. Witness: writes injected into the sources during a run (BF1.5). **U:** a file rewritten twice during the run can only be checked against versions that were observed, so the witness samples.
- **I-B1.3** *State.* `∀n: ok(n) ∧ ¬pruned(n) ∧ ¬damaged(n) ∧ ¬missing(n) ⇒ restorable(n)`. *restorable* is T11, a claim about a procedure. §5 replaces the obligation under BF1.3, BF1.10, BF1.11 and BF1.12. The predicate alone does not settle those cases.
- **I-B1.4** *Transition, at every prune.* After a prune, the newest passed-check snapshot, the retained span and the daily and monthly keeps are all present, as far as the existing history allows. Witness: prune mutants (prune by count; remove the newest checked snapshot; prune to free space; prune during ramp-up) are caught.
- **I-B1.5** *State.* No credential file exists at R or on the restore host. Witness: the existing mutation pair (the `auth.json` exclusion removed must FAIL). Repository content rests on AI1.5.
- **I-B1.6** *State plus transition.* As B1.1 for *ok*. Every *failed* entry has a stage. No *failed* entry follows an *ok* entry for the same number. A run with no final entry receives one later. Witnesses: SIGKILL a run mid-copy and read the next entry; `backup-ack-check.sh` (a failure after *ok* neither deletes the snapshot nor contradicts its entry).
- **I-B1.7** *Temporal.* For each of B1.7's four events *e*, `□(e ⇒ ◇≤D notice-sent-under-B1.16)`, measured on R's clock.
- **I-B1.8** *Temporal.* `□(ok(n) ⇒ ◇≤M restore_checked(n))`. A *not restore-checked* mark is a state, not a discharge. When *M* passes without a restore check, B1.8 is violated, and B1.7's third event reports it.
- **I-B1.9** *Temporal, conditional.* If the premise holds over [*t*, *t* + *I* + *X*], then an *ok* run entry with a sequence number greater than every acknowledged one at *t* exists by *t* + *I* + *X*. When the premise is false, the clause is vacuous, not violated.
- **I-B1.10** *State.* Every stored object at R is ciphertext under the key, and R's filesystem holds no key. Witness: a canary file planted in a source, then a search of R for its plaintext. Plaintext on the restore host is absent once each check ends.
- **I-B1.11** *Transition, daily.* For every item past its review date with no later logged decision, the daily check fails. Witness: an item dated in the past makes the check FAIL.
- **I-B1.12** *Temporal.* `□(n ∈ retained ⇒ ◇≤P (verified_at_R(n) ∨ damaged(n)))`, and after a *damaged* mark, a notice within *D*. Witness: flip one stored byte at R, then see the mark and the notice within *P* + *D*.
- **I-B1.13** *Observation.* After each comparison, every acknowledged, unpruned *n* is present at R, or it has a *missing* mark and a notice is sent within *D*. Witnesses: delete one snapshot at R (BF1.12); reimage a scratch R (BF1.10).
- **I-B1.14** *Observation.* A restore check succeeds on the restore host with S's key file renamed away.
- **I-B1.15** *Observation.* Empty a source tree in a scratch copy, and see the notice within *D* of the comparison. **U:** shrinkage below *Q* per run, spread over many runs, is missed. That is a known limit, left to Arariwa (§8).
- **I-B1.16** *Temporal, conditional on reachability.* `□(required(notice) ⇒ ◇≤D reached ∨ (unreachable ∧ recorded ∧ ◇≤D-after-reachable reached))`. **U:** gap 6.

## 5. Failure model v1 (draft 3) and its effect on each clause
### Cells
BF1.12 and BF1.13 are new in draft 3.
- **BF1.1** The backup process crashes at any stage (mid-copy, mid-verify, mid-prune, mid-restore-check, mid-re-verify), then restarts.
- **BF1.2** A partition between any two of S, R and the restore host, of any length, healed or not.
- **BF1.3** Silent corruption of stored bytes at R, found only by reading them.
- **BF1.4** A full disk at R or at S.
- **BF1.5** Writes to the sources during a run.
- **BF1.6** Clock steps at S, R or the restore host.
- **BF1.7** The alert path is down: the plaza or Hamut'ay is unavailable while S is up.
- **BF1.8** A timer does not fire, at any host: S's run timer, S's daily check, R's freshness checker or re-verify, the restore host's check.
- **BF1.9** A source tree is moved, emptied or truncated by mistake.
- **BF1.10** R is reimaged or replaced, so every snapshot there is lost.
- **BF1.11** A copy of the escrowed key is lost: the restore host's copy, or S's copy.
- **BF1.12** *New.* Some snapshots at R are lost or deleted, but not all of them.
- **BF1.13** *New.* The status record is lost or corrupted, at S or at R.

### Effects
Every pair not listed is **H**: the clause holds unchanged, and the cell's injected test checks it. **S** means suspended until a named event. **W** means replaced by the stated weaker obligation. **V** means the clause's premise is false, so it is vacuous, not violated.

| Cell | Clause | Effect | Obligation that holds instead |
|---|---|---|---|
| BF1.1 | B1.6 | H | The fourth part of B1.6 covers it. |
| BF1.1 | B1.4 | H | A crash mid-prune never leaves the newest passed-check snapshot removed. This is the hardest H. |
| BF1.2 (restore host, R) | B1.8 | S | Restore checks are suspended while the restore host cannot reach R. The partition does not excuse B1.8: past *M*, B1.7's third event fires. |
| BF1.2 (S, R) | B1.9 | V | The premise is false. |
| BF1.2 (S, R) | B1.7 | W | The checker on R detects the staleness. Its notice is held under B1.16 until S is reachable. |
| BF1.2 (S, R) | B1.16 | W | Notices from R are recorded at R and delivered within *D* of reconnection. |
| BF1.2 (S, R) | B1.12 | H | R re-verifies without S. A *damaged* notice waits under B1.16. |
| BF1.3 | B1.3 | W | A corrupted snapshot is restorable, or it has a *damaged* mark within *P* of the corruption and a notice within *D* of the mark. |
| BF1.3 | B1.4 | W | A damaged snapshot does not count towards the span. If none remains, a notice is sent. |
| BF1.4 (R) | B1.9 | V | The premise is false. B1.7 still reports the staleness. |
| BF1.4 | B1.4 | H | B1.4's last part covers it. |
| BF1.6 | B1.7, B1.8, B1.9, B1.12, B1.16 | W | Each deadline holds up to the size of the step (T12). The injected steps are ±1 h and ±24 h, and the measured error is reported. |
| BF1.6 | B1.4 (order) | H | Order is by sequence number. |
| BF1.6 | B1.4 (ages) | W | The *T*, *K* and *Mo* ages are wrong by up to the step. |
| BF1.7 | B1.16 | W | The second sentence of B1.16 covers it. Every notice clause inherits it. |
| BF1.8 (S run timer) | B1.9 | V | The premise ("up") is read as "the service is running on S". |
| BF1.8 (S run timer) | B1.7 | W | The checker on R detects the staleness. Its notice reaches the plaza only if S is up apart from its timer, which it is in this cell. |
| BF1.8 (S daily check) | B1.11 | S | Suspended until the check runs. Past 2 *I*, B1.7's first event cannot see it. **Gap 7:** nothing checks the daily check. It is added to §10 question 1. |
| BF1.8 (R checker) | B1.7, B1.13 | W | Only S's own failure notices remain. If both stop for longer than *H*, that is EX1.5. |
| BF1.8 (R re-verify) | B1.12 | S | Suspended until the timer fires. Past *P*, B1.7's fourth event fires, if the checker is running. |
| BF1.8 (restore host) | B1.8 | S | As BF1.2 × B1.8. |
| BF1.9 | B1.1, B1.2, B1.3 | H | The damaged source is copied faithfully. |
| BF1.9 | B1.15 | H | B1.15 exists for this cell. |
| BF1.10 | B1.3 | S | Suspended for the lost snapshots permanently, unless a further copy exists (EX1.1). |
| BF1.10 | B1.4 | S | Suspended until the new span reaches *T*. Then *K* and *Mo* apply as history accrues. |
| BF1.10 | B1.13 | H | The next comparison writes *missing* marks and sends a notice. |
| BF1.11 (restore host's copy) | B1.8 | S | Suspended until the copy is reinstalled from Tony's. Past *M*, B1.7 fires. |
| BF1.11 (restore host's copy) | B1.3 | H | T11 includes reinstalling from Tony's copy. |
| BF1.11 (S's copy) | B1.9 | V | S cannot encrypt, so runs fail and B1.7 reports them. |
| BF1.12 | B1.3 | S | Suspended for the lost snapshots. The others hold. |
| BF1.12 | B1.13 | H | B1.13 exists for this cell. |
| BF1.13 (S's copy) | B1.6, B1.13 | W | S rebuilds its record from R's copy at the next run. If both copies are lost, every snapshot is treated as unacknowledged until it is verified again. |
| BF1.13 (both copies) | B1.3 | W | The obligation applies only to snapshots acknowledged again after re-verification. |

### Explicitly excluded (the service does not tolerate these, and says so; every item has a review date)
- **EX1.1** S and R lost together, if no further copy exists. The off-site copy is a second contract, to follow. Review: 2026-12-01.
- **EX1.2** Deliberate tampering by someone with access to both S and R. Review: 2027-05-01.
- **EX1.3** Loss of anything before the first snapshot. Review: 2027-05-01.
- **EX1.4** Disclosure of the escrowed key. Review: 2027-05-01.
- **EX1.5** R's checker and S's run both stopped for longer than *H*. Review: 2026-12-01.
- **EX1.6** *New.* S down for longer than *H* (power, the move, WSL not started). The checker on R sees it, but no notice can reach the plaza. **This is gap 6.** Review: 2026-12-01, or sooner if §10 question 1 is answered.

### Assumed impossible (every item has a review date)
- **AI1.1** A sha256 collision. *Unwitnessed.* Review: 2027-11-01.
- **AI1.2** R's hash tool reporting a match for bytes that differ. *Witness:* T10 recomputes the plaintext hashes on another host. Review: 2027-05-01.
- **AI1.3** The host that answers as wam-nuc being wam-nuc. *Witness:* a pinned SSH host key. Review: 2027-05-01.
- **AI1.4** The restore check not secretly reading S. *Witness:* the restore host has no path to S. Review: 2027-05-01.
- **AI1.5** *New.* No credential is committed to tupay's repository history. *Witness:* a secrets scan before each push. The 2026-11-03 scan of 211 commits found none. Review: 2027-05-01.
- **AI1.6** *New.* Tony's copy of the key exists and is readable. *Witness:* Tony's confirmation, logged once a year. Review: 2027-05-01.

## 6. Parameters
- ***I* = 24 h** (run interval): the timer's period.
- ***M* = 1 d** (restore-check deadline). A check costs minutes at about 500 MB.
- ***P* = 7 d** (re-verify interval). A choice: reading about 7 GB at R a week is cheap. Revisit after corruption is measured.
- ***H* = 36 h** (staleness): *I* plus 12 h for a late timer.
- ***D* = 1 h** (notice delay). A choice, bounded by the checker's cadence: it runs at least every *D*.
- ***X* = 2 h** (liveness slack). A choice.
- ***Q* = 0.2** (shrink fraction). A choice. **U:** not yet measured. To be measured from `backup.sh`'s manifests before registration.
- ***Dmax*** = *I* + *X* + *D* = **27 h**. This is the longest delay from damage to B1.15's notice: the damage lands just after a run, the next run is up to *I* + *X* later, and its notice comes within *D*.
- ***T*** = *M* + *Dmax* = **51 h**. This is a floor.
- ***K* = 14 d** and ***Mo* = 6 months**. Both are choices, well above *T*, because damage that no clause can see (a file wrongly edited, which people notice only weeks later) is not covered by *Dmax*. *K* matches `backup.sh`.

## 7. Gaps found since draft 1, mapped to ids
1. No re-verification: B1.12 (draft 2).
2. The checker was on S: B1.7 and T23 (draft 2). **Incomplete in draft 2:** the plaza is on S, so the checker could detect without delivering. Now B1.16 and EX1.6 (draft 3).
3. Lost snapshots went unreported: B1.13 (draft 2). Draft 3 adds the inventory obligation.
4. The key was a single point: B1.14 and BF1.11 (draft 2); AI1.6 (draft 3).
5. BF1.9's detection was not an obligation: B1.15 (draft 2).
6. **Open:** no delivery path while S is down. EX1.6 states it, and §10 question 1 asks for a decision.
7. **Open, new in draft 3:** nothing checks the daily check (BF1.8 × B1.11). It is folded into §10 question 1.

## 8. What Arariwa observes (not normative)
For each run and each source tree: file count, bytes and the change from the last run; time per stage; the age of the newest restore-checked snapshot; the age of the last delivered alert-path test. The steward expects Arariwa to raise three things unprompted: slow shrinkage below *Q*, restore checks ageing while verification passes, and an alert path that goes unexercised. Its detection delay is measured from injection time, for every cell. Restic is measured as a second rung below (§9).

## 9. What the service must beat (a comparison of behaviour, not of the defined terms)
The rung below consists of `backup.sh`, its two systemd timers, `backup-check.sh` (a staleness check on S) and `backup-alert.sh` (plaza notices on failure). Together they behave roughly as B1.1, B1.5 (by file name only), part of B1.6, B1.9 (through the timer) and part of B1.7 (the check, but on S). They lack B1.3 and B1.8 from R alone, B1.4, the off-S checker, B1.10, B1.12, B1.13, B1.14, B1.15 and B1.16's held delivery. The rung's acknowledgement defect was fixed on 2026-11-08 (Qwen's finding 10). If the new service cannot beat both rungs (this one and restic) on what they lack, the finding is that a rung was enough.

## 10. For Tony (one batch, each with a recommendation; none blocks your week)
1. **Gaps 6 and 7: a path that does not go through S.** The plaza is on S, so while S is down (the move, power, WSL not started) nothing this contract names can reach you. **Recommendation:** wam-nuc sends one push notification, through ntfy or an email you choose, when S has been silent for more than *H*, and when the daily check has not run for 2 *I*. That is a single message type sent from R, and it never replaces the plaza. Otherwise, EX1.6 stands until 2026-12-01. Which channel would you notice?
2. **The checker's host:** R, as T23 now says. The box is a worse choice, because it is sometimes suspended for other residents.
3. **The off-site copy** as a second contract after this one is registered (EX1.1, reviewed 2026-12-01 because of the move).
