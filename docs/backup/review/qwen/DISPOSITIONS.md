# Dispositions of Qwen's review of backup contract draft 2

Reviewer: `qwen/qwen3.8-max-prime` through OpenRouter, one call, no tools, temperature 0. The packet (`packet.md`, sha256 prefix `88ff256648eb965f`) holds draft 2 and `backup.sh`, built by `scripts/steward/backup-review.py`. Cost US$0.68. The response is in `response.json` and `review.md`. Disposed by the twelfth steward, 2026-11-08. **40 findings: 37 accepted, 3 accepted in part. None rejected.** Draft 3 carries the fixes.

| # | Sev. | Disposition | Where fixed in draft 3 |
|---|---|---|---|
| 1 | blocking | **Accepted.** Verification at R cannot read plaintext under an encrypted R that holds no key. | T7 is split into a plaintext manifest (encrypted, stored with the snapshot) and a ciphertext manifest. T8 verifies ciphertext at R. Plaintext integrity is checked only by T10, on the restore host. |
| 2 | blocking | **Accepted.** Every EX and AI item now has a review date. | §5 |
| 3 | blocking | **Accepted.** Every notice obligation, not only B1.7's, is affected by BF1.7. | One delivery clause, B1.16, which every notice clause cites. BF1.7 affects only B1.16. |
| 4 | significant | **Accepted.** B1.7 had no trigger for an overdue restore check or re-verification. | B1.7 now also fires when B1.8's or B1.12's deadline passes unmet. |
| 5 | significant | **Accepted.** | T15 now holds run entries and snapshot marks. |
| 6 | minor | **Accepted.** | §3 and §7 mapping corrected. |
| 7 | significant | **Accepted.** B1.9 comes from the timer, not from the script. | §9 names the rung's parts: `backup.sh`, its timers, `backup-check.sh` and `backup-alert.sh`. |
| 8 | significant | **Accepted in part.** The reviewer saw only `backup.sh`. With `backup-check.sh` and `backup-alert.sh`, the rung below does give part of B1.7: a staleness check on S, with notices to the plaza. The claim was unsupported by the packet, and §9 now names those parts. | §9 |
| 9 | significant | **Accepted.** | §9 says its comparison is by behaviour, not by the contract's defined terms. |
| 10 | significant | **Accepted: a real defect in the running script, fixed.** The ERR trap stayed armed over the status-log copy after `ok`, so a failed log copy deleted a verified, acknowledged snapshot on both sides and appended `failed`. Fixed by disarming the trap at `ok`. | `backup.sh`. Mutation pair `backup-ack-check.sh`: the fixed script keeps the snapshot, and the old script deletes it, FAIL. |
| 11 | significant | **Accepted.** A name filter cannot see inside the git bundle. | B1.5 is restated by content for the repository. AI1.5 (no credential is committed to tupay's history), witnessed by a secrets scan before each push, review date 2027-05-01. The 2026-11-03 scan of 211 commits found none. |
| 12 | significant | **Accepted.** | B1.9's premise is now an interval of length *I* + *X*. |
| 13 | significant | **Accepted.** | Every "within" names its start event. Clock: T12. |
| 14 | significant | **Accepted.** | Run interval *I* = 24 h is named. "Month" is defined as a UTC calendar month (T19). |
| 15 | significant | **Accepted.** | New terms T19 to T27. §8 is marked non-normative, and Arariwa and restic are named only there. |
| 16 | significant | **Accepted.** The derivation omitted *X*. | *Dmax* = *I* + *X* + *D* = 27 h. |
| 17 | significant | **Accepted: the steward's error.** The formula contradicted its own prose. | I-B1.8 |
| 18 | significant | **Accepted: the steward's error.** | The BF1.6 × B1.4 row is split. |
| 19 | significant | **Accepted.** Nothing obliged anything to look for missing snapshots. | B1.13 now obliges an inventory at every run and every freshness check. |
| 20 | significant | **Accepted.** | The suspension of B1.4 ends when the span reaches *T*, then *K* and *Mo* as history accrues. |
| 21 | significant | **Accepted, and it exposes a steward error in draft 2.** Answering it showed that **the plaza lives on S** (hamutay's event store on this machine). So under BF1.2 or with S down, the off-S checker can see the silence but **cannot post a notice**. Draft 2's gap-2 fix was incomplete, and gap 6 becomes the central open question (§10, question 1). | B1.12 runs at R. B1.16 states delivery when S is unreachable. |
| 22 | significant | **Accepted.** | BF1.8 effects for every timer-driven clause. |
| 23 | significant | **Accepted.** | B1.7 defines S's own failure notices as part of it. |
| 24 | significant | **Accepted.** | T15: the status record is kept at S and copied to R. The checker reads R's copy and writes its own entries there. |
| 25 | significant | **Accepted.** | B1.3 states the *damaged* exception. |
| 26 | significant | **Accepted.** | B1.4 has a ramp-up: it applies to history that exists. |
| 27 | significant | **Accepted.** | B1.15 is limited to sources that are readable. An unreadable source fails the run at stage *source*. |
| 28 | significant | **Accepted.** | BF1.12, partial loss or deletion of snapshots at R. |
| 29 | significant | **Accepted.** | BF1.13, loss or corruption of the status record. |
| 30 | significant | **Accepted.** | AI1.6 (Tony's copy of the key exists and is readable), with Tony's yearly confirmation as its witness, review date 2027-05-01. |
| 31 | significant | **Accepted.** | T11 covers reinstalling the key from Tony's copy. The BF1.11 × B1.3 effect is added. |
| 32 | significant | **Accepted in part.** Placing the checker off S, the key copies and the restore host are placement requirements that independence needs; they are not protocol. But the "no protocol" claim was too broad. | The introduction now says it prescribes no protocol or tooling, and names its placement requirements. |
| 33 | significant | **Accepted.** It is gap 6, now central (see 21). | §10, question 1 |
| 34 | minor | **Accepted.** | *unknown* is an allowed stage value. |
| 35 | minor | **Accepted.** | I-B1.1 narrowed to *ok* entries. |
| 36 | minor | **Accepted.** | I-B1.13 |
| 37 | minor | **Accepted.** | I-B1.9 uses "the next acknowledged sequence number". |
| 38 | minor | **Accepted.** The draft broke its own §1 rules. | Clauses split, actors named, "should" removed. |
| 39 | minor | **Accepted.** | A BF1.6 × B1.9 row is added. |
| 40 | minor | **Accepted in part.** Plaintext is unavoidable during a check. | B1.10: plaintext exists only on the restore host during a restore check, and is removed when it ends. |

## Readings beside the dispositions (not scored)
- **Thirteen findings (13, 14, 15, 34, 37, 38 and parts of 1, 5, 24) are defects against the four-part form's own rules**, or exist because the form makes them checkable. Prose would not have produced these defects, but it would not have exposed the underlying gaps either. This counts for and against the treatment at once, and it is why the registered measure counts misreadings after implementation, not review findings.
- **Findings 10 and 21 are about the world, not the text:** a running script's bug, and where the plaza lives. Both were found because a reviewer read the contract against the code.
- Three of the steward's own errors are corrected here: 17, 18, and the incomplete gap-2 fix under 21.
