# Verified backup: contract and failure model (DRAFT 4, four-part form; not registered)

The twelfth steward, 2026-11-11. Draft 4 applies Codex's review of draft 3 (`review/codex/DISPOSITIONS.md`, eight findings, all accepted). It also applies one scope decision: **encryption at rest moves to v2 as a planned contract change**, and its ids are retired here. The four-part form is the treatment arm of a registered test, not tupay's practice. The prose arm is derived from this text at registration.

**Scope of prescription.** This contract prescribes no protocol and no tooling. It fixes **placement** where independence needs it: the restore host has no path to S (T4), and the freshness checker runs on R (T23).

## A. What you can recover, and what this contract changes
**Today** (`recovery-account.md`, checked 2026-11-11):
- If S disappears, `main` survives on GitHub, and everything else in scope survives on wam-nuc, up to about 24 h old.
- That includes the 23 arm branches that exist nowhere else, `tupay-private/` and `tupay-homes/`.
- Restore has been tested once, by hand.
- Nothing would tell you that S had gone silent.

**Under this contract:**

| Row of the account | Clauses that change it |
|---|---|
| Restore tested once, by hand | Every snapshot restore-checked within a day, from R alone (B1.8) |
| Corruption at R found only by chance | Every unpruned snapshot re-read every week (B1.12) |
| Snapshots lost at R go unnoticed | An inventory at every run and check (B1.13) |
| A copy can silently miss files | Completeness against an inventory (B1.17) |
| Retention by count | A way back measured by age, from a restore-checked snapshot (B1.4) |
| A source emptied by mistake is copied "successfully" | Reported within a stated bound (B1.15) |
| S's silence goes unseen | Seen by R (B1.7). Delivery while S is down: **open (EX1.6, §10)** |
| A credential could enter in a commit | Scanned at every run (AI1.5) |

**Not changed by v1:**
- loss of S and R together (EX1.1; the off-site copy is a second contract);
- plaintext at R (EX1.7; encryption is v2);
- harness credentials, which are never backed up, by design.

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
- **T1 S**: the source host, WAM-THREADRIPPER under WSL. The plaza's record is on S. *Changes with the Fedora move (§10.3).*
- **T2 Sources**: three source trees (T20):
  - tupay's git repository, every ref;
  - `tupay-private/`;
  - `tupay-homes/`, without credentials (T13) or caches (T21).
- **T3 R**: the store, wam-nuc. It is physically separate from S and reached over the network.
- **T4 Restore host**: the box (T22). It holds no copy of the sources and has no path to S's files.
- **T5 Run**: one attempt to make a snapshot. Each run has a sequence number that only increases, and T5a says how it is assigned. Sequence numbers order runs and snapshots. Clocks never do.
- **T5a Sequence assignment**: S assigns max(the highest number in S's status record, the highest snapshot name at R) + 1. So a lost record never reuses a number.
- **T6 Snapshot**: the copy of the sources that one run makes. It is stored at R and named by its sequence number.
- **T7c Manifest**: every file in the snapshot with its sha256, together with the run's source inventory (T28). The run writes it and stores it with the snapshot.
- **T8 Verified**: an event. At R, every file of the snapshot was read and matched T7c.
- **T9 Acknowledged**: the status record holds an *ok* run entry for the snapshot.
- **T10 Restore-checked**: an event. On the restore host, the snapshot was copied from R, the repository was cloned from its bundle, and every file was compared with T7c, and every file matched.
- **T11 Restorable** at time *t*: the restore procedure, run on the restore host with S unavailable, would produce bytes that match T7c.
  - It is a claim about a procedure.
  - **Its evidence is a passing T10.** A later T8 shows only that the bytes checked by that T10 are unchanged. T8 is never evidence on its own.
- **T12 Clock and age**: an age is measured on the clock of the host that measures it. Across a clock step, an age can be wrong by up to the size of the step.
- **T13 Credential**: either of two things:
  - a file that matches the name patterns in `scripts/steward/backup.sh`;
  - content that `scripts/steward/secrets-scan.sh` pattern set v1 reports.
- **T15 Status record**: a list of entries, kept at S and copied to R after each run. There are two kinds of entry:
  - a **run entry**: sequence number; *ok* or *failed*; stage, where *unknown* is a valid stage; times;
  - a **snapshot mark**: sequence number; one of *restore-checked*, *restore-failed*, *not restore-checked*, *damaged* or *missing*; time; writing host.

  The freshness checker writes its marks to R's copy, and S merges them at its next run.
- **T16 Notice**: a post to the plaza naming its clause. A notice **reaches** the plaza when the plaza's record holds it.
- **T17 Pruning**: the service's deliberate removal of a snapshot from R.
- **T18 Protected set**: every acknowledged snapshot that pruning has not removed.
- **T19 Units**: *h*; *d* = 24 h; *month* = a UTC calendar month.
- **T20 Source tree**: one of the three parts of T2.
- **T21 Caches**: `.cache`, `go` and package caches under `tupay-homes/`.
- **T22 The box**: the `ubuntu26-test` VM. It can be suspended for other residents.
- **T23 Freshness checker**: a process on R. It evaluates B1.7's events, B1.8's and B1.12's deadlines, and B1.13's inventory, at least every *D*.
- **T24 Daily check**: the check B1.11 names. It runs on S once every *I*.
- **T25 Daily snapshot**: the acknowledged snapshot with the highest sequence number in its UTC day.
- **T26 Logged reason**: an entry in tupay's log, written before the run, that names the source tree and the change.
- **T28 Source inventory**: the list of every file path in each source tree, read once at the start of the run. For the repository it is instead the ref list, also read once at the start of the run.

## 3. Normative clauses (contract v1, draft 4)
Each clause has one of three **classes**, which §5 uses:
- **[service]**: something the service does or never does. It holds under every cell.
- **[deadline]**: an obligation with a time bound that needs named hosts to be available.
- **[preservation]**: something about stored data that environmental loss can defeat.

- **B1.1 [service] (acknowledgement is earned)** The run writes an *ok* run entry only after the snapshot is verified at R and B1.17 holds for it.
- **B1.2 [service] (snapshots are faithful)**
  - The repository part is bundled from the ref list in T28, so its refs are exactly that list.
  - Every other file is a version that existed at S during the run, and no file is torn.
- **B1.3 [preservation] (restorable)** Every snapshot in the protected set that is not marked *damaged*, *missing* or *restore-failed* is restorable (T11).
- **B1.4 [service] (pruning keeps a way back)** Pruning never removes:
  - the newest snapshot that is *restore-checked* and not since marked *damaged*;
  - any snapshot younger than *T*;
  - any daily snapshot younger than *K*;
  - the first daily snapshot of each month, for *Mo* months.

  While less history exists than these need, pruning removes nothing they would keep. Pruning never frees space by breaking this clause. While the status record is being rebuilt (B1.18), pruning removes nothing.
- **B1.5 [service] (no credential leaves S)**
  - The run never writes a credential file to R or to the restore host.
  - The run scans the commits new since the previous acknowledged snapshot with `secrets-scan.sh`. A hit fails the run at stage *no-credentials*.
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
  - The restore host restore-checks every acknowledged snapshot within *M* of its *ok* entry.
  - It writes *restore-checked* or *restore-failed*.
  - Until it does, the record shows *not restore-checked*, which is a state and not a discharge.
  - At the start of each check, the restore host removes any files left by an earlier check that crashed.
- **B1.9 [deadline] (liveness)** If S and R stay up, connected and not full for an interval of *I* + *X*, then at its end an *ok* entry exists with a sequence number higher than every number acknowledged at the interval's start.
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
  - A notice reaches the plaza within *D* of the event that requires it.
  - While the plaza cannot be reached, the sender records the notice where the freshness checker reads, and delivers it within *D* of the plaza becoming reachable.
- **B1.17 [service] (snapshots are complete)** *New, Codex finding 1.* The manifest holds every path in the source inventory (T28), except for these two cases, each of which the manifest lists:
  - a path deleted during the run, marked *gone*;
  - a path whose content changed during the run in a way that B1.2 cannot capture, marked *changing* (the run retries it once).

  A path created during the run is copied or left out, and the manifest lists it either way. A renamed file appears as a deletion plus a creation.
- **B1.18 [deadline] (the status record recovers)** *New, Codex finding 5.*
  - If S's copy is lost, S restores it from R's copy at its next run.
  - If R's copy is lost, R takes S's copy at the next run.
  - If both are lost, the service rebuilds the record within *Rb*: R lists the snapshots present, re-verifies each, and the restore host restore-checks each one. During the rebuild, every present snapshot keeps B1.4's protection.

## 4. Interpretation records
**U** marks an assumption that is not yet resolved. These are the steward's readings, one reading among several (§0).
- **I-B1.1** *State, at every ok write.* `ok(n) ⇒ verified_at_R(n) ∧ complete(n) happened before it`. Witness: mutants that write *ok* before verification, or after leaving out a directory, are caught.
- **I-B1.2** *Observation.* The restored bundle's refs equal T28's ref list exactly, ref by ref. Every other file's hash equals a version of it observed at S during the run. Witness: refs updated and files written during the run (BF1.5). **U:** a file rewritten twice during the run can only be checked against observed versions, so the witness samples.
- **I-B1.3** *State.* `∀n ∈ protected: ¬(damaged ∨ missing ∨ restore_failed)(n) ⇒ ∃ passing T10(n), with no damaging event since`. In the window before the first T10, B1.8 holds the obligation.
- **I-B1.4** *Transition, at every prune.* After a prune, each of the four kept groups is present, as far as the history allows. Witness: these prune mutants are caught: prune by count; remove the newest checked snapshot; free space; prune during ramp-up; prune during a rebuild.
- **I-B1.5** *State, plus a per-run scan.* No credential file at R or on the restore host, and no scanner hit in the run's new commits. Witnesses: the `auth.json` mutation pair, and `secrets-scan-check.sh` (every pattern caught, the control clean, and both mutants FAIL).
- **I-B1.6** *State plus transition.* Witnesses: SIGKILL a run mid-copy and check the next entry; `backup-ack-check.sh` (a failure after *ok* neither removes the snapshot nor contradicts its entry).
- **I-B1.7** *Temporal.* For each event *e* in the list, `□(e ⇒ ◇≤D notice-sent)`, on R's clock.
- **I-B1.8** *Temporal.* `□(ok(n) ⇒ ◇≤M (restore_checked(n) ∨ restore_failed(n)))`. *not restore-checked* never discharges the obligation.
- **I-B1.9** *Temporal, conditional.* If the premise holds over [*t*, *t* + *I* + *X*], an *ok* entry for a higher sequence number exists by *t* + *I* + *X*.
- **I-B1.11** *Transition, daily.* Witness: an item dated in the past makes the check FAIL.
- **I-B1.12** *Temporal.* `□(n ∈ protected ⇒ ◇≤P (verified_at_R(n) ∨ damaged(n)))`. Witness: flip a byte at R, then see the mark and the notice within *P* + *D*.
- **I-B1.13** *Observation.* After each comparison, every member of the protected set is present at R or marked *missing*. B1.7 then sends a notice within *D*. Witnesses: delete one snapshot (BF1.12); reimage a scratch R (BF1.10).
- **I-B1.15** *Observation.* Empty a scratch source tree, then see the notice within *D* of the comparison. **U:** slow shrinkage spread over many runs is missed. That is a known limit, left to Arariwa.
- **I-B1.16** *Temporal, conditional.* Either the notice reaches the plaza within *D*, or it is recorded and then delivered within *D* of the plaza becoming reachable. **U:** gap 6 (EX1.6).
- **I-B1.17** *Observation.* `inventory(n) ⊆ manifest_paths(n) ∪ gone(n) ∪ changing(n)`. Witnesses: an implementation mutant that skips a directory is caught; deletions, creations and renames during a run are injected, and each appears as stated.
- **I-B1.18** *Temporal.* After a loss of both copies, `◇≤Rb rebuilt`, with pruning frozen until the rebuild ends. Witness: delete both copies in a scratch deployment, then time the rebuild.

## 5. Failure model v1 (draft 4) and its effect on each clause
### Cells
- **BF1.1** The backup process crashes at any stage, including during a restore check or a re-verify, and then restarts.
- **BF1.2** A partition between any two of S, R and the restore host, of any length, healed or not.
- **BF1.3** Silent corruption of stored bytes at R.
- **BF1.4** A full disk at R or at S.
- **BF1.5** Writes, deletions, renames and ref updates in the sources during a run.
- **BF1.6** Clock steps at any host.
- **BF1.7** The plaza is unavailable while S is up.
- **BF1.8** A timer does not fire, at any host.
- **BF1.9** A source tree is moved, emptied or truncated by mistake.
- **BF1.10** R is reimaged or replaced, so all its snapshots are lost.
- **BF1.12** Some snapshots at R are lost or deleted, not by the service.
- **BF1.13** The status record is lost or corrupted at S, at R, or at both.
- **BF1.14** *New, Codex finding 4.* A host is suspended (the box for other residents; S under WSL; R by power).

### The class rule (Codex finding 4; it replaces draft 3's blanket H)
- **[service] clauses hold under every cell.** Each cell's injected test checks them. A cell can stop the service from acting; it never licenses the service to act wrongly.
- **[deadline] clauses are suspended while a host they name is unavailable** (BF1.2, BF1.4, BF1.8, BF1.14). Each deadline restarts from the moment the host is available again. The unavailability itself is reported under B1.7 whenever the checker can observe it. **No detection bound holds while R or the checker is unavailable, and the contract does not claim one.**
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
| BF1.14 (the box) | B1.8 | Suspended under the class rule. Past *M*, B1.7 still fires, if R is up. |

### Explicitly excluded (each with its review date)
- **EX1.1** S and R lost together, with no further copy. The remedy is the off-site copy, a second contract. Review: 2026-12-01.
- **EX1.2** Deliberate tampering by someone with access to S and R. Review: 2027-05-01.
- **EX1.3** Loss of anything before the first snapshot. Review: 2027-05-01.
- **EX1.5** R's checker and S's runs both stopped for longer than *H*. Review: 2026-12-01.
- **EX1.6** S down for longer than *H*. R sees it, but no notice can reach the plaza (gap 6). Review: 2026-12-01, or sooner, on Tony's answer to §10.1.
- **EX1.7** *New.* Snapshot contents are plaintext at R and on the restore host. The remedy is v2 (§11). Review: 2026-12-01.

### Assumed impossible (each with its review date)
- **AI1.1** A sha256 collision. *Unwitnessed.* Review: 2027-11-01.
- **AI1.2** R's hash tool reporting a match for bytes that differ. *Witness:* T10 recomputes hashes on another host. Review: 2027-05-01.
- **AI1.3** The host that answers as wam-nuc being wam-nuc. *Witness:* a pinned SSH host key. Review: 2027-05-01.
- **AI1.4** The restore check not reading S. *Witness:* the restore host has no path to S. Review: 2027-05-01.
- **AI1.5** No credential enters the repository undetected. *Witness:* B1.5's per-run scan with `secrets-scan.sh` v1. It has its own mutation pair, and its first run over `8370157..main` on 2026-11-11 found no hit. Its limit: the scanner can only find the patterns it knows. Review: 2027-05-01.

## 6. Parameters
Each value gives its derivation, or says it is a choice.
- ***I* = 24 h**: the run interval.
- ***M* = 1 d**: the restore-check deadline.
- ***P* = 7 d**: the re-verify interval. A choice: reading about 7 GB at R each week is cheap.
- ***H* = 36 h**: *I* plus 12 h of slack.
- ***D* = 1 h**: the notice delay. The checker runs at least every *D*.
- ***X* = 2 h**: the liveness slack.
- ***Q* = 0.05**, measured on 2026-11-11 from the 9 local snapshots (11-03 to 11-11):
  - `tupay-private/` and `tupay-homes/` did not change in file count or bytes between any two runs;
  - the bundle's size moved between −0.87 % and +1.32 %;
  - *Q* is about six times the largest shrink observed. Deliberate clean-ups are covered by logged reasons (T26).
  - **Limit:** no author ran in that window, so the noise under load is unmeasured. *Q* is measured again after the first round with authors.
- ***Rb* = 2 d**: the rebuild deadline. Re-verifying and restore-checking 14 snapshots of about 500 MB each takes hours, not days.
- ***Dmax* = *I* + *X* + *D* = 27 h**, **conditional on** three things: (a) the next run succeeds, (b) the damage crosses *Q*, and (c) R and the plaza are reachable. Under BF1.2, BF1.4, BF1.8 or BF1.14, no bound holds (the class rule).
- ***T* = *M* + *Dmax* = 51 h**, under the same conditions. It is a floor.
- ***K* = 14 d** and ***Mo* = 6 months**: choices well above *T*. They cover damage no clause detects, such as a wrongly edited file that people notice weeks later.

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

## 9. What the service must beat (behaviour, not defined terms)
The rung below is `backup.sh`, its two timers, `backup-check.sh` and `backup-alert.sh`.
- **It gives:** B1.1 without completeness; B1.5 by file name; part of B1.6; B1.9 through the timer; and part of B1.7, from S.
- **It lacks:** B1.3 and B1.8 from R alone, B1.4, B1.12, B1.13, B1.15, B1.16, B1.17, B1.18, and an off-S checker.

If the new service cannot beat this rung and restic on what they lack, the finding is that a rung was enough.

## 10. For Tony (one batch, each with a recommendation; none blocks your week)
1. **Gap 6: a path that does not go through S.** Recommendation: wam-nuc sends a single kind of push message when S has been silent for more than *H*, or the daily check has not run for 2 *I*. Which channel would you notice: ntfy, email, or another?
2. **An ssh path to wam-nuc that is not on S.** The recovery account found that the restore depends on the key S uses, which lives on S. Does another machine have its own key? Recommendation: give one, and store it with the house's new key management.
3. **The Fedora move is the first real restore.** Recommendation: move tupay by restoring it from wam-nuc onto the new disk, following `recovery-account.md`, rather than by copying the old disk. Keep the old disk as the way back. The restore then tests the account, and every step that fails is logged as a finding. T1 changes at that moment, and that is the contract change the move forces.
4. ***Q***: no question for you. It was measured on 2026-11-11 (§6).

## 11. v2, planned: encryption at rest and the key holder
v2 adds encryption at R under a key held outside S and R. It brings a new authority locus, the **key holder**, after the house's new key management exists. Under the seed's question, this is a contract change that adds a locus to a service with live artifacts, the side of the hyperplane not yet seen. It is planned by tupay, so it is weaker evidence than a change the adversary times, and its registration will say so. The ids retired in §0 are not reused. v2 states encryption afresh.
