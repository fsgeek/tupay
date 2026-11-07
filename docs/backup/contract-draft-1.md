# Verified backup: contract and failure model (DRAFT 1, for Tony's review; not registered)

Draft 1 (2026-11-07) answers Tony's four questions on draft 0: retention is now derived, not picked; restore is checked on every snapshot; R is encrypted; exclusions expire; and alternatives are compared. Draft 0 is in git history.

The eleventh steward, 2026-11-07. This is a draft for Tony to read before any outside review or author sees it. Once registered, ids are monotone and never reused. It derives from tupay's need (log, 2026-11-03: nothing backed up tupay's unpushed record) and the ayllu's existing pattern (`scripts/steward/backup.sh`, which stays running as **the rung below**: every claim about this service is measured against it). Like X3's contract, it prescribes **no protocol**: what the service guarantees, not how.

## Parties and terms
- **S**, the source host (this machine): tupay's repository, `tupay-private/`, and `tupay-homes/` without credentials or caches.
- **R**, the store (wam-nuc), a physically separate machine reached over the network.
- **Snapshot:** one run's copy of the sources.
- **Acknowledged:** recorded as ok in the status record.
- **Verified:** every file at R checked against the snapshot's manifest, at R.
- **Restore-checked:** restored **from R alone**, into a place that does not read S, and compared with the manifest.
- **Pruning:** the deliberate removal of snapshots.

## Contract v1 (draft)
- **B1.1 (acknowledgement is earned)** A snapshot is acknowledged only if it is verified at R.
- **B1.2 (snapshots are faithful)** The repository part of a snapshot is one consistent state of every ref. Every other file in it is a version that existed at S during the snapshot's window: no file is torn.
- **B1.3 (restorable)** Every acknowledged snapshot that has not been pruned can be restored from R alone, with S unavailable, to bytes matching its manifest.
- **B1.4 (pruning keeps a way back)** Pruning never removes the newest restore-checked snapshot. It keeps restore-checked snapshots reaching back at least *T* = *M* + *Dmax*, where *M* is the restore-check interval and *Dmax* is the longest stated detection delay of any failure that damages a source (BF1.9). Within that span it keeps every daily snapshot for *K* days and one per month for *Mo* months.
- **B1.10 (confidential at rest)** Snapshot contents at R, and at any further copy, are encrypted under a key that R does not hold.
- **B1.11 (exclusions expire)** Every explicit exclusion (EX) and every unwitnessed assumption (AI) carries a review date. The daily check fails after that date until the item is re-decided and the decision logged.
- **B1.5 (no credential leaves S)** No file matching the credential patterns is ever written to R.
- **B1.6 (the status record does not lie)** The status record never reports ok for a snapshot that B1.1 does not acknowledge. Every failure record names the stage that failed.
- **B1.7 (silence is detected)** If a run fails, or no acknowledged snapshot is newer than *H* hours, a notice reaches the plaza within *D*. If the plaza cannot be reached, that failure is recorded where an independent daily check reads it.
- **B1.8 (restore is exercised)** Every acknowledged snapshot is restore-checked within *M* of being acknowledged, and the result is recorded. Until then its status says it has not been restore-checked.
- **B1.9 (liveness)** If S and R stay up and connected long enough, a new acknowledged snapshot exists within 24 hours plus *X*.

## Failure model v1 (draft)
**Anticipated:**
- **BF1.1** Crash of the backup process at any stage (mid-copy, mid-verify, mid-prune), then restart.
- **BF1.2** Partition between S and R, of any length, healed or not.
- **BF1.3** Silent corruption of stored bytes at R, found only by reading them.
- **BF1.4** A full disk at R or at S.
- **BF1.5** Writes to the sources during a snapshot (commits, author runs, OTS stamping).
- **BF1.6** Clock steps at S (WSL suspend and resume). No ordering across S and R is relied on.
- **BF1.7** The alert path down: the plaza or Hamut'ay unavailable.
- **BF1.8** The timer not firing (the user session not running, WSL not started).
- **BF1.9** A source moved, emptied or truncated by mistake (GitLab 2017's shape: "the backup succeeded" while what it copied was wrong).
- **BF1.10** R reimaged or replaced, so every snapshot there is lost.

**Explicitly excluded** (the service does not tolerate these, and says so):
- **EX1.1** S and R lost together, *if no third copy exists*. **Draft 1 recommends removing this exclusion before Tony's move** with an encrypted off-site copy: the transcripts in `tupay-private/` exist nowhere else, and in a move S and R travel together. Review date: 2026-12-01.
- **EX1.2** Deliberate tampering by someone holding access to both S and R.
- **EX1.3** Loss of anything before the first snapshot.

**Assumed impossible, each with its witness or marked unwitnessed:**
- **AI1.1** A sha256 collision. *Unwitnessed.*
- **AI1.2** R's `sha256sum` reporting a match for bytes that differ. *Witness:* the restore check recomputes hashes in a different place.
- **AI1.3** The host answering as `wam-nuc` being wam-nuc. *Witness:* a pinned SSH host key.
- **AI1.4** The restore check not secretly reading S. *Witness:* it runs on R or the box with S's paths absent.

## What Arariwa observes (draft obligations, not scoring)
Per run, for each source tree: file count, bytes and the change from the last run; time per stage; the age of the newest restore-checked snapshot; the age of the last delivered alert-path test.
**Anomalies it should raise without being told:**
- a source that shrinks or empties without a logged reason (BF1.9);
- verification passing while no restore check has run within *M* (B1.8 decaying quietly);
- an alert path not exercised for longer than its period (B1.7's own witness ageing).

Each failure-model cell gets an injected test, and Arariwa's **detection delay** for each is measured against injection time, the measure registered for Arariwa on 2026-11-02.

## What the service must beat
`backup.sh` already gives B1.1, B1.5, B1.6, B1.9 and part of B1.7. The new service has to justify itself on what the script lacks: **B1.3/B1.8** (scheduled restore from R alone), **B1.4** (pruning relative to a restore-checked snapshot, not a count), **BF1.9's detection**, and **B1.7's witness of its own alert path**. If it can't beat the script on those, the finding is that the script was enough.

## Alternatives, and why (draft 1)
- **Retention:** count only (draft 0's *K* = 7, which had no basis and contradicted `backup.sh`'s 14) versus a time window versus daily-plus-monthly. Chosen: daily plus monthly, sized from *T* = *M* + *Dmax*. A count alone ties history to run frequency and can fall inside the restore-test window.
- **Restore checks:** sampled monthly (draft 0, copied from Hamut'ay) versus every snapshot. Chosen: every snapshot, because at about 500 MB it costs minutes, and it removes the window in which snapshots are verified but never restored.
- **Tooling:** rsync with manifests (the ayllu's pattern) versus restic or borg (deduplication, encryption and a restore command built in). **Not decided:** restic is to be measured as a second rung below, beside `backup.sh`. If it meets the contract, the finding is that no new service is needed.
- **At rest:** plaintext (draft 0) versus encrypted. Chosen: encrypted (B1.10). levadura's backup already encrypts, and `tupay-private/` holds another resident's sealed material.
- **Restore location:** R versus the box. Chosen: the box (AI1.4).

## For Tony (batched, each with a recommendation)
**Draft 1's recommendations:** *M* = 1 day; *K* = 14 days; *Mo* = 6 months; *Dmax* stated per BF1.9 detector, and at most 7 days until measured; *H* = 36 h; *D* = 1 h; *X* = 2 h; the restore check on the box; and a third, encrypted, off-site copy before the move. Draft 0's list follows for the record.
1. ***K, H, D, M, X***: recommend *K* = 7, *H* = 36 h, *D* = 1 h, *M* = 30 days (Hamut'ay's cadence), *X* = 2 h.
2. **Author homes in scope?** Recommend yes, for the transcripts only (about 400 MB). They are evidence, and their hashes are committed.
3. **Where the restore check runs:** recommend the box, which has no tupay sources, so AI1.4's witness is structural.
4. **A third copy of `tupay-private/`?** Recommend not yet. EX1.1 is stated, and revisited if the private material grows.
