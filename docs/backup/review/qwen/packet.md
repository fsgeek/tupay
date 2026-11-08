You are reviewing, adversarially, a draft service contract and failure model for a backup service, before any implementation author sees it. Authors will build from it; a formal model and an implementation will be tested against it; failure cells will be injected.

Find defects in it. Kinds of defect to look for, not suspicions: a term used in more than one meaning or undefined; a clause that cannot be satisfied, or is satisfied vacuously; two clauses that contradict; a clause whose obligation depends on an unstated assumption; an interpretation record that does not match its clause; a (clause x failure cell) effect in section 5 that is wrong, or a pair marked H (holds, by omission) that does not in fact hold; a failure a backup service of this shape plausibly meets that no cell names; a parameter whose derivation does not follow; a claim in section 9 about the script that the script contradicts; anything that prescribes a protocol when it says it does not.

Report a numbered list of findings, each with: severity (blocking / significant / minor), where (id or section), what is wrong, and why (quote the text). If an area is sound, say so in one line. Do not rewrite the contract; a one-line suggested fix per finding is enough.

===== the contract draft under review (contract-draft-2.md) =====
# Verified backup: contract and failure model (DRAFT 2, four-part form; not registered)

The twelfth steward, 2026-11-08. Draft 1 is `contract-draft-1.md`, and its history is in git. Draft 2 does three things:

1. It writes the contract in the four-part form: vocabulary, defined terms, normative clauses and interpretation records (log, 2026-11-07, "controlled language"). That form is **the treatment arm of a registered test, not tupay's practice** (log amendment, same day). The prose arm is derived from this text at registration and carries the same obligations.
2. It adds the **effect of every failure cell on every clause** (§5). Both arms get that table. Filling it in found six gaps in draft 1, listed in §7. Their fixes are new ids, and no id is reused.
3. It fixes draft 1's parameter values, with their derivations (§6).

It prescribes no protocol: it says what the service guarantees, not how.

## 0. Authority
Unless an item says otherwise, the **steward** establishes, interprets, amends and retires every term, clause, cell and record here. Tony reviews before registration. Once registered, an interpretation can only choose among readings the text already permits. Anything that changes an obligation is a new version (`docs/adversary/CHANNEL.md`, amendment 1, applied here too). Implementation and model authors are not authorities: where an author's reading differs from an interpretation record, that is a **finding** to judge, not an error to correct.

## 1. Vocabulary rules
Adopted from ASD-STE100's writing rules, **not** its word list, which is built for maintenance procedures:
- one meaning per word: a word defined in §2 is used only in that meaning, and a word that is not defined is used in its ordinary sense only where no defined term applies;
- one obligation per clause sentence;
- the active voice, with the party that acts named;
- no "should", "normally", "as needed" or "etc." in a normative clause;
- every quantity is a named parameter (§6), never a bare number;
- "within *X*" always names its clock and its start event (T12).

## 2. Defined terms (ids never reused)
- **T1 S**: the source host, this machine (WAM-THREADRIPPER under WSL).
- **T2 Sources**: tupay's git repository (every ref); `tupay-private/`; and `tupay-homes/`, excluding credentials (T13) and caches.
- **T3 R**: the store, wam-nuc. It is physically separate from S and reached over the network.
- **T4 Restore host**: the host on which restore checks run, the box. It holds no copy of the sources and has no path to S's files.
- **T5 Run**: one attempt to make a snapshot. Runs are numbered by a **sequence number** that only increases, which S assigns. The sequence number, not any clock, orders runs and snapshots.
- **T6 Snapshot**: the copy of the sources that one run produces, stored at R, named by its run's sequence number.
- **T7 Manifest**: a list of every file in a snapshot with its sha256, written by the run and stored with the snapshot.
- **T8 Verified**: every file of the snapshot was read at R, and its hash matched the manifest. Verification is an event with a time; it is not a lasting property.
- **T9 Acknowledged**: the status record holds an *ok* entry for the snapshot. This is a property of the record (see B1.1 for when it is permitted).
- **T10 Restore-checked**: on the restore host, the snapshot was copied from R, decrypted with the escrowed key (T14), and every file compared with the manifest, and all matched. Like T8, it is an event with a time.
- **T11 Restorable** (draft 1 used this word without a definition): at time *t*, the restore procedure, run on the restore host with S unavailable and using the escrowed key, would produce bytes that match the manifest. **It is a claim about a procedure, not about bytes existing.** Its only evidence is a restore check (T10) or a verification (T8) newer than the last event that could damage it.
- **T12 Clock and age**: an age or a "within" is measured on the clock of the host that does the measuring, from the event named. **Across a clock step, an age can be wrong by up to the step's size** (BF1.6). Where that matters, the clause says so.
- **T13 Credential**: a file matching the credential patterns in `scripts/steward/backup.sh` (`auth.json`, `.credentials.json`, `*credential*`).
- **T14 Escrowed key**: the key that encrypts snapshots, held where neither S nor R holds it. Tony holds a copy "in a safe place" (2026-11-07). The restore host holds a copy for checks.
- **T15 Status record**: the list of run outcomes. Each entry has a sequence number, a result (*ok* or *failed*), the failed stage if any, and times.
- **T16 Notice**: a post to the plaza that names the clause it reports on. A notice **reaches** the plaza when the plaza's record holds the row.
- **T17 Pruning**: the deliberate removal of a snapshot from R.
- **T18 Retained span**: the set of snapshots that pruning must keep (B1.4).

## 3. Normative clauses (contract v1, draft 2)
B1.1 to B1.11 keep their draft-1 ids and meaning, restated in the vocabulary above. **B1.12 to B1.15 are new in draft 2** (gaps 1 to 4, §7).

- **B1.1 (acknowledgement is earned)** The service writes an *ok* entry for a snapshot only after that snapshot is verified at R.
- **B1.2 (snapshots are faithful)** In a snapshot, the repository part is one consistent state of every ref, and every other file is a version that existed at S during the run. No file is torn.
- **B1.3 (restorable)** Every acknowledged snapshot that is not pruned is restorable (T11), **except as §5 states for BF1.3, BF1.10 and BF1.11.**
- **B1.4 (pruning keeps a way back)** Pruning never removes the newest snapshot whose last restore check passed. It keeps a retained span reaching back at least *T* = *M* + *Dmax*, by run sequence and age. Within that span it keeps every daily snapshot for *K* days and one per month for *Mo* months. Pruning never removes a snapshot to make space if doing so breaks this clause.
- **B1.5 (no credential leaves S)** The service never writes a credential to R or to the restore host.
- **B1.6 (the status record does not lie)** The status record never holds *ok* for a snapshot that B1.1 does not permit. Every *failed* entry names its stage. A run that ends without a final entry is recorded as *failed, stage unknown* by the next run or the next freshness check (B1.7), whichever comes first.
- **B1.7 (silence is detected)** If a run fails, or no acknowledged snapshot is younger than *H*, a notice reaches the plaza within *D*. **The freshness check runs on a host other than S** (gap 2). If the plaza cannot be reached, the failure is recorded where the freshness check reads it, and the notice is sent when the plaza returns.
- **B1.8 (restore is exercised)** Every acknowledged snapshot is restore-checked within *M* of being acknowledged, and the result is recorded. Until then, the status record marks it *not restore-checked*.
- **B1.9 (liveness)** If S and R stay up, connected and not full long enough, a new acknowledged snapshot exists within 24 h + *X* of the last one.
- **B1.10 (confidential at rest)** Snapshot contents at R and at any further copy are encrypted under the escrowed key. R never holds that key.
- **B1.11 (exclusions expire)** Every EX and AI item carries a review date. After that date the daily check fails until the item is decided again and the decision logged.
- **B1.12 (retained snapshots are re-verified)** *New, gap 1.* Every snapshot in the retained span is verified again at R at least every *P*. A snapshot whose re-verification fails is marked *damaged* in the status record, and a notice reaches the plaza within *D*. Pruning does not count a damaged snapshot towards B1.4.
- **B1.13 (lost snapshots are noticed)** *New, gap 3.* If an acknowledged, unpruned snapshot is absent from R, a notice reaches the plaza within *D* of the first run or check that could observe it.
- **B1.14 (the key is not a single point)** *New, gap 4.* The restore check uses the restore host's escrowed copy of the key, never S's. At least one copy of the key is held outside S, R and the restore host (Tony's). The key's loss at S does not prevent a restore.
- **B1.15 (a vanished source is reported)** *New, gap 5.* If a source tree's file count or bytes fall by more than a fraction *Q* from the previous acknowledged snapshot, and no logged reason names that run, a notice reaches the plaza within *D*. The snapshot is still taken and acknowledged under B1.1, because a faithful copy of a damaged source is still faithful. The notice is what B1.4's *Dmax* is measured from.

## 4. Interpretation records
Each record gives the clause's form, its interpretation, the witness that tests it, and its assumptions. **U** marks an assumption that is not yet resolved. These are the steward's readings, one among several (§0).

- **I-B1.1** *State, at every write of an* ok *entry.* `ok(n) ⇒ verified_at_R(n) happened before ok(n)`. Witness: a mutant that writes *ok* before verification is caught by the check. Assumes the status record is written only by the run (U, if anything else ever writes it).
- **I-B1.2** *Observation.* Restoring the snapshot gives a git bundle for which `git bundle verify` passes, and every ref resolves. Every other file's hash equals some version that file had at S during the run window. Witness: a test that writes to a source during the run, under BF1.5. **U:** "a version that existed": a file rewritten twice during the run can only be checked against versions that were observed. The witness can only sample.
- **I-B1.3** *State, under §5's exceptions.* `∀n: ok(n) ∧ ¬pruned(n) ∧ ¬damaged(n) ⇒ restorable(n)`, where *restorable* is T11, a claim about a procedure. Evidence that the claim holds is a restore check or verification newer than the last damaging event. **The predicate alone does not settle BF1.10.** §5 does, by replacing the obligation.
- **I-B1.4** *Transition, at every prune.* After a prune: the newest snapshot whose last restore check passed is present, and the retained span (T18) is present. Witness: prune mutants (prune by count; prune the newest checked snapshot; prune to make space) are caught. Assumes *Dmax* is known: it is the stated delay of B1.15's notice.
- **I-B1.5** *State, at all times.* No file at R or the restore host matches T13. Witness: the existing mutation pair (the `auth.json` exclude removed must FAIL).
- **I-B1.6** *State, plus transition.* As B1.1 for *ok*. A *failed* entry has a stage. A run with no final entry gets one later. Witness: kill a run with SIGKILL mid-copy, then check the next entry.
- **I-B1.7** *Temporal.* `□(stale ∨ failed ⇒ ◇≤D notice)`, where *stale* means the newest *ok* entry is older than *H* on the checker's clock. The checker is not S. **U:** when the plaza is down, the record goes where the checker reads it, but nothing yet says **who reads the checker's record** if the plaza stays down (gap 6, §7).
- **I-B1.8** *Temporal.* `□(ok(n) ⇒ ◇≤M restore_checked(n) ∨ marked_not_checked(n))`. Marking a snapshot as not checked does not discharge the obligation: past *M*, the clause is violated and B1.7 reports it.
- **I-B1.9** *Temporal, conditional.* Under its premise, `◇≤(24h+X) ok(n+1)`. When the premise is false (§5), the clause is vacuous, not violated.
- **I-B1.10** *State.* Every byte stored at R is ciphertext under the escrowed key, and R's filesystem holds no copy of the key. Witness: grep R for known plaintext from a canary file planted in a source.
- **I-B1.11** *Transition, daily.* For every item past its review date with no later decision in the log, the daily check returns failure. Witness: an item with a review date in the past makes the check FAIL.
- **I-B1.12** *Temporal.* `□(n ∈ retained ⇒ ◇≤P verified_at_R(n) ∨ damaged(n))`. Witness: flip one byte at R and see the notice within *P* + *D*.
- **I-B1.13** *Observation.* After any run or check, every acknowledged, unpruned *n* is present at R, or a notice has been sent. Witness: delete a snapshot directory at R, and separately reimage a scratch R (BF1.10).
- **I-B1.14** *Observation.* A restore check succeeds on the restore host with S's key file renamed away. Witness: that test, and a mutant that reads S's key, which must be caught by AI1.4's structure (the restore host has no path to S).
- **I-B1.15** *Observation.* Witness: empty a source tree in a scratch copy, and see the notice within *D*. **U:** a fraction *Q* misses slow shrinkage spread over many runs. That is left to Arariwa as an anomaly it should find unaided (§8), and it is stated here as a known limit.

## 5. Failure model v1 (draft 2) and its effect on each clause
### Cells
BF1.1 to BF1.10 are as in draft 1. **BF1.11 is new** (gap 4).
- **BF1.1** The backup process crashes at any stage (mid-copy, mid-verify, mid-prune, mid-restore-check), then restarts.
- **BF1.2** A partition between any two of S, R and the restore host, of any length, healed or not.
- **BF1.3** Silent corruption of stored bytes at R, found only by reading them.
- **BF1.4** A full disk at R or at S.
- **BF1.5** Writes to the sources during a run (commits, author runs, OTS stamping).
- **BF1.6** Clock steps at S, R or the restore host (WSL suspend and resume). No cross-host ordering is relied on.
- **BF1.7** The alert path is down: the plaza or Hamut'ay is unavailable.
- **BF1.8** A timer does not fire (the user session is not running, or WSL has not started), on S or on the checker's host.
- **BF1.9** A source is moved, emptied or truncated by mistake (GitLab 2017's shape).
- **BF1.10** R is reimaged or replaced, so every snapshot there is lost.
- **BF1.11** *New.* The escrowed key's copy on the restore host is lost, or S's copy is lost.

### Effects
Every pair not listed below is **H**: the clause holds unchanged under that cell, and the cell's test checks it. Every listed pair is **S**, suspended until a named event, or **W**, replaced by a stated weaker obligation. **V** means the clause's premise is false, so it is vacuous, not violated.

| Cell | Clause | Effect | Obligation that holds instead |
|---|---|---|---|
| BF1.1 | B1.6 | W | A crash leaves no final entry; the next run or check records *failed, stage unknown* (already in B1.6). |
| BF1.1 | B1.4 | H | A crash mid-prune never leaves the newest passed-check snapshot removed. Stated here because it is the hardest H to meet. |
| BF1.2 | B1.8 | S | While the restore host cannot reach R, restore checks are suspended. Past *M*, B1.8 is violated and B1.7 reports it; the partition does not excuse it. |
| BF1.2 | B1.9 | V | The premise ("connected") is false. |
| BF1.2 (S, R) | B1.7 | H | The checker is off S (gap 2), so a partition of S is seen as staleness. |
| BF1.3 | B1.3 | W | A corrupted snapshot is restorable **or** marked *damaged* within *P* + *D* of the corruption (B1.12). |
| BF1.3 | B1.4 | W | A damaged snapshot does not count towards the retained span. If that empties the span, a notice is sent. |
| BF1.4 (R) | B1.9 | V | The premise ("not full") is false. B1.7 still reports the staleness. |
| BF1.4 | B1.4 | H | Pruning never breaks B1.4 to make space (stated in B1.4). |
| BF1.6 | B1.7, B1.8, B1.12 | W | Each "within" holds up to the size of the step (T12). A backward step can hide staleness by that amount. The test injects steps of ±1 h and ±24 h, and the size of the error is reported. |
| BF1.6 | B1.4 | H | Order is by sequence number (T5), not time, so a step cannot reorder snapshots. Ages used for *K* and *Mo* are W, as above. |
| BF1.7 | B1.7 | W | The notice is delayed until the plaza returns. The failure is recorded where the checker reads it. **Gap 6 is open:** nothing yet escalates a plaza that stays down. |
| BF1.8 (S) | B1.9 | V | The premise ("S up long enough") is read as "the service is running on S". With timers stopped it is false. |
| BF1.8 (S) | B1.7 | H | The checker is off S (gap 2), so the silence is seen. |
| BF1.8 (checker) | B1.7 | W | With the checker's timer stopped, B1.7 holds only through S's own failure notices. The silence of both at once is an EX (EX1.5). |
| BF1.9 | B1.1, B1.2, B1.3 | H | The damaged source is copied faithfully, and that is correct behaviour. |
| BF1.9 | B1.15 | H | This cell is what B1.15 exists for. |
| BF1.10 | B1.3 | S | Suspended for the lost snapshots, permanently, **unless a further copy exists (EX1.1)**. A new snapshot at the new R restarts B1.3 for itself. |
| BF1.10 | B1.4 | S | The retained span is lost. It rebuilds from the next run. |
| BF1.10 | B1.13 | H | The loss is noticed within *D* of the first run or check after it. |
| BF1.11 (restore host's copy) | B1.8 | S | Suspended until the copy is restored from Tony's. Past *M*, B1.7 reports it. |
| BF1.11 (S's copy) | B1.3 | H | Restore never uses S's copy (B1.14). |
| BF1.11 (S's copy) | B1.9 | V | S cannot encrypt, so runs fail and B1.7 reports them. |

### Explicitly excluded (the service does not tolerate these, and says so)
- **EX1.1** S and R lost together, *if no further copy exists*. Draft 1 recommended an encrypted off-site copy before Tony's move. **Draft 2 leaves the off-site copy out of this contract's scope, as a second contract to follow.** It adds a third party, its own failure cells and its own key path, and this contract should be tested first. Review date: 2026-12-01.
- **EX1.2** Deliberate tampering by someone with access to both S and R.
- **EX1.3** Loss of anything before the first snapshot.
- **EX1.4** *New.* Disclosure of the escrowed key. B1.10 holds only while the key is secret.
- **EX1.5** *New.* The checker's host and S both failing to run timers at once, for longer than *H*. Review date: 2026-12-01.

### Assumed impossible, each with its witness or marked unwitnessed
- **AI1.1** A sha256 collision. *Unwitnessed.* Review date: 2027-11-01.
- **AI1.2** R's hash tool reporting a match for bytes that differ. *Witness:* the restore check recomputes hashes on another host.
- **AI1.3** The host that answers as wam-nuc being wam-nuc. *Witness:* a pinned SSH host key.
- **AI1.4** The restore check not secretly reading S. *Witness:* the restore host has no path to S's files.

## 6. Parameters
Each value gives its derivation, or says it is a choice.
- ***M* = 1 day** (restore-check interval). A check costs minutes at about 500 MB, so every snapshot is checked (draft 1).
- ***P* = 7 days** (re-verify interval, new). This is a choice. Reading about 7 GB of retained snapshots a week is cheap. A shorter *P* narrows BF1.3's undetected window. Revisit once corruption has been measured.
- ***H* = 36 h** (staleness): the daily run interval plus 12 h of slack for a late timer.
- ***D* = 1 h** (notice delay). A choice, bounded by the checker's cadence.
- ***X* = 2 h** (liveness slack). A choice.
- ***Q* = 0.2** (shrink fraction, new). A choice. Tupay's sources have shrunk by more than 20 % only by deliberate cleanup, which can be logged as a reason. **U:** not measured. To be measured from `backup.sh`'s manifests before registration.
- ***Dmax*** = *D* + one run interval = 25 h. B1.15 fires at the first run after the damage, so this is derived, no longer "at most 7 days until measured".
- ***T*** = *M* + *Dmax* ≈ 2 days. **This is a floor, not a target.**
- ***K* = 14 days** and ***Mo* = 6 months**. Both are choices that keep far more than *T*, because BF1.9 is not the only damage that goes unseen: a damaged file can go unnoticed by people for weeks, and nothing in the service sees that. *K* matches `backup.sh`.

## 7. Gaps in draft 1 found by filling in §5 (each is a candidate finding for the test, and is shown to both arms' authors only as the fixed text)
1. **No re-verification** (B1.12). Draft 1's B1.3 could not hold under BF1.3, because nothing ever read a snapshot again after its first check.
2. **The checker was on S.** Under BF1.8, the timer that misses the backup is on the same host as the timer that checks it, so the "independent daily check" was not independent (B1.7 revised).
3. **Lost snapshots were invisible** (B1.13). After BF1.10, the next run would write a fresh snapshot to the new R and report ok, and the loss of every earlier snapshot would go unreported.
4. **The key was a single point** (B1.14, BF1.11). Draft 1's B1.10 encrypted everything without saying where the key lives or which copy a restore uses. If the restore check used S's key, AI1.4's witness would be broken in effect.
5. **BF1.9's detection was not an obligation** (B1.15). It lived only in "What Arariwa observes", yet B1.4's *Dmax* depended on it.
6. **Open:** who escalates when the plaza stays down? B1.7's fallback record has no named reader. **Recommendation for Tony:** a check failing for longer than 24 h is shown at the start of the steward's session, by the channel-sweep hook, the same mechanism as the steward's inbox. Tony, or whoever next opens a tupay session, then sees it, without a new alert path that could fail silently in its own turn.

## 8. What Arariwa observes (unchanged from draft 1, except B1.15 now owns the source-shrink case)
For each run and each source tree: file count, bytes and the change from the last run; time per stage; the age of the newest restore-checked snapshot; the age of the last delivered alert-path test. **It should raise these without being told:** slow shrinkage below *Q* spread over many runs (I-B1.15's U); verification passing while restore checks age (B1.8 decaying quietly); and an alert path not exercised for longer than its period. Its detection delay is measured from injection time, for every cell.

## 9. What the service must beat
`backup.sh` and restic are the rungs below it. `backup.sh` gives B1.1, B1.5, B1.6 (in part), B1.9 and part of B1.7. It lacks B1.3/B1.8 from R alone, B1.4, B1.7's off-S checker, B1.12, B1.13, B1.14 and B1.15. If the new service cannot beat both rungs on those, the finding is that a rung was enough.

## 10. For Tony (one batch, each with a recommendation; none blocks this week)
1. **Gap 6, escalation:** recommend the hook route in §7.6.
2. **The checker's host:** recommend wam-nuc (R) checking its own newest snapshot's age, posting through the plaza CLI over ssh, or recording locally if that fails. The alternative is the box, which is suspended at times for other residents (qhaway, 2026-10-28), so it is a worse checker.
3. **The off-site copy as a second contract** (EX1.1): recommend yes, after this one is registered, with a review date of 2026-12-01 because of the move.


===== the existing script, the "rung below" (section 9 makes claims about it) (backup.sh) =====
#!/usr/bin/env bash
# Nightly backup of tupay's unreplicated record to wam-nuc (a physically separate machine).
# Modelled on hamutay/deploy/backup-records.sh. Before 2026-11-03 nothing backed these up
# (Tony, eleventh steward's acceptance): 200+ unpushed commits, tupay-private/, author homes.
#
# What: (1) tupay's repository as a git bundle of every ref (a consistent snapshot of a live
# repository; rsync of .git is not), checked with `git bundle verify`; (2) tupay-private/
# (sealed and licence-restricted material, author transcripts); (3) tupay-homes/ (author
# transcripts, egress logs) WITHOUT credentials or caches: auth.json, .credentials.json and
# anything named *credential* are excluded, so no harness token leaves this host.
# How: snapshot (hard-linked against the previous run) -> MANIFEST.sha256 -> rsync to wam-nuc
# (hard-linked there) -> verify the remote manifest -> prune to KEEP runs each side -> one JSON
# status line in backup-log.jsonl here and on wam-nuc. Nothing is written under any source.
set -euo pipefail
PROJECTS="${PROJECTS:-/home/tony/projects}"
REPO="$PROJECTS/tupay"
LOCAL_ROOT="${LOCAL_ROOT:-/home/tony/backups/tupay}"
REMOTE="${REMOTE:-wam-nuc}"
REMOTE_ROOT="${REMOTE_ROOT:-backups/tupay}"
KEEP="${KEEP:-14}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$LOCAL_ROOT/$TS"
LOG="$LOCAL_ROOT/backup-log.jsonl"
STAGE="start"
RQ="$(printf %q "$REMOTE_ROOT")"
runs() { find "$1" -mindepth 1 -maxdepth 1 -type d -name '20*Z' 2>/dev/null | sort; }

umask 077
mkdir -p "$LOCAL_ROOT"
status() {  # status <ok|failed> <stage> [extra-json-fields]
  local line
  line="{\"run\":\"$TS\",\"status\":\"$1\",\"stage\":\"$2\",\"finished\":\"$(date -u +%FT%TZ)\"${3:+,$3}}"
  echo "$line" >> "$LOG"
  echo "$line"
}
# A failed run leaves nothing behind, so it never counts among the KEEP good runs.
trap 'status failed "$STAGE"; rm -rf "$OUT"; ssh -o BatchMode=yes "$REMOTE" "rm -rf $RQ/$TS" 2>/dev/null || true; exit 1' ERR

STAGE="source"
[ -d "$REPO/.git" ] && [ -d "$PROJECTS/tupay-private" ] && [ -d "$PROJECTS/tupay-homes" ]
PREV="$(runs "$LOCAL_ROOT" | tail -n 1)"
mkdir -p "$OUT"

STAGE="bundle"
# Read-only on the repository: bundle create and verify write only to $OUT.
git -C "$REPO" bundle create "$OUT/tupay.bundle" --all 2>/dev/null
git -C "$REPO" bundle verify "$OUT/tupay.bundle" >/dev/null 2>&1
HEAD="$(git -C "$REPO" rev-parse HEAD)"

STAGE="private"
rsync -a ${PREV:+--link-dest="$PREV/tupay-private"} "$PROJECTS/tupay-private/" "$OUT/tupay-private/"

STAGE="homes"
rsync -a ${PREV:+--link-dest="$PREV/tupay-homes"} \
  --exclude='auth.json' --exclude='.credentials.json' --exclude='*credential*' \
  --exclude='.cache/' --exclude='go/pkg/' --exclude='.npm/' --exclude='node_modules/' \
  "$PROJECTS/tupay-homes/" "$OUT/tupay-homes/"

STAGE="no-credentials"
# Belt and braces: the copy must hold no credential file, whatever the excludes missed.
# (Not `! find | grep`: a negated pipeline is exempt from set -e and could never fail the run.)
if find "$OUT" \( -name 'auth.json' -o -name '.credentials.json' -o -name '*credential*' \) -print -quit | grep -q .; then
  echo "credential file in the copy" >&2; false
fi

STAGE="manifest"
( cd "$OUT" && find . -type f ! -name MANIFEST.sha256 -print0 | sort -z | xargs -0 -r sha256sum > MANIFEST.sha256 )
SIZE="$(du -sb "$OUT" | cut -f1)"
FILES="$(wc -l < "$OUT/MANIFEST.sha256")"

STAGE="copy"
ssh -o BatchMode=yes "$REMOTE" "mkdir -p $RQ && chmod 700 $RQ"
RPREV="$(ssh -o BatchMode=yes "$REMOTE" "find $RQ -mindepth 1 -maxdepth 1 -type d -name '20*Z' | sort | tail -n 1")"
rsync -a --protect-args ${RPREV:+--link-dest="../$(basename "$RPREV")"} "$OUT/" "$REMOTE:$REMOTE_ROOT/$TS/"

STAGE="verify-remote"
# git bundle verify needs a repository; use a throwaway bare one (the bundle is complete, so
# it has no prerequisites to resolve).
ssh -o BatchMode=yes "$REMOTE" "cd $RQ/$TS && test -s MANIFEST.sha256 && sha256sum --quiet -c MANIFEST.sha256 && V=\$(mktemp -d) && git init -q --bare \$V && git -C \$V bundle verify \$PWD/tupay.bundle >/dev/null 2>&1; r=\$?; rm -rf \$V; exit \$r"

STAGE="prune"
runs "$LOCAL_ROOT" | head -n -"$KEEP" | xargs -r -d '\n' rm -rf
ssh -o BatchMode=yes "$REMOTE" "find $RQ -mindepth 1 -maxdepth 1 -type d -name '20*Z' | sort | head -n -$KEEP | xargs -r -d '\n' rm -rf"

STAGE="done"
status ok done "\"head\":\"$HEAD\",\"bytes\":$SIZE,\"files\":$FILES,\"remote\":\"$REMOTE:$REMOTE_ROOT/$TS\""
rsync -a --protect-args "$LOG" "$REMOTE:$REMOTE_ROOT/backup-log.jsonl"
