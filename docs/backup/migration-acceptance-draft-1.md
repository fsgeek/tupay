# Migration acceptance: tupay restored onto a new host (DRAFT 1; predictions registered by this commit)

The twelfth steward, 2026-11-12. This defines what it means for tupay to have **arrived** on the house's new host (plaza seq 246). The test is a restore from R alone: the move is tupay's first real restore (log, 2026-11-11). It is written against `host-requirements.md`, not against any distribution, so it does not wait on the house's choice. Ids are never reused. The steward's predictions (§4) are **registered by the commit that adds this file**. Later amendments are additive, and each says whether an outcome informed it.

## 1. Terms
- **Old S**: WAM-THREADRIPPER under WSL. It stays untouched, as the way back.
- **New S**: the house's new host, whatever system it runs.
- **Rehearsal**: a restore onto new S that is checked and then discarded. Rehearsals may be repeated.
- **Cutover**: the single rehearsal after which new S becomes tupay's S, and old S stops running tupay's timers.
- **From R alone**: during the restore, new S reads nothing from old S. Its only inputs are wam-nuc's snapshot, GitHub (the `main` branch only), and the steps in `recovery-account.md` as written at the rehearsal's commit.

## 2. Acceptance clauses (MA1.x)
**Level 1: the data.**
- **MA1.1** The newest acknowledged snapshot restores onto new S from R alone, and every file matches its manifest.
- **MA1.2** The restored repository holds every ref of the snapshot's ref list, and `git fsck` reports no error.

**Level 2: the pipeline.** On new S, after the restore, each of these passes:
- **MA1.3** A commit in the restored repository is OTS-stamped by the hook.
- **MA1.4** A commit is signed with an author key, and the signature verifies.
- **MA1.5** `inputcheck.sh` and `sandbox-check.sh` pass on a fresh checkout, and their mutation runs FAIL.
- **MA1.6** `sandbox-cred-check.sh` passes, and its two mutants FAIL, each on its own case.
- **MA1.7** `secrets-scan-check.sh` passes, and its mutants FAIL.
- **MA1.8** `backup-ack-check.sh` passes, and its mutant FAILs.
- **MA1.9** A past round's shared paired tests reproduce on new S, with the same outcomes as recorded: M1 round 2's shared schedules, implementation and model sides, at ten repetitions per seed, as the practice file requires.
- **MA1.10** A TLC run with a memory cap completes. The cap is enforced by the new host's mechanism; with `systemd-run`, that is `MemoryMax`.
- **MA1.11** A sandboxed author can start, reach only its allowlisted egress, and exit. Its credential copy is removed at exit.
- **MA1.12** The backup timers run on new S, and a run from new S to R is acknowledged.
- **MA1.13** That snapshot restore-checks on the restore host.
- **MA1.14** The channel-sweep hook prints at the start of a steward session on new S.

**Level 3: the account.**
- **MA1.15** Every step of `recovery-account.md` that did not work as written is logged as a finding, and the account is amended (additively) before cutover.
- **MA1.16** The losses the account lists as accepted are the only losses. Anything else missing after the restore is a finding.

**Cutover** happens only after a rehearsal in which MA1.1 to MA1.16 all pass, or after Tony accepts a named failure in writing.

## 3. What is measured at every rehearsal
- The wall-clock time per level.
- The steps taken by hand that the account does not list.
- Tony's attention: each question he is asked, and each action only he can take.
- Each MA clause: PASS, FAIL, or blocked (by an earlier FAIL).

## 4. The steward's predictions (registered by this commit)
These predictions concern the **first** rehearsal, with the steps as written today:
1. **Level 1 passes** (MA1.1 and MA1.2): the same steps passed by hand on 2026-11-03.
2. **MA1.11 fails at first.** `author-sandbox.sh` binds `/mnt/wsl/resolv.conf`, which exists only on WSL.
3. **At least one script fails on a hard-coded `/home/tony` path**, if new S gives tupay a different home. If the home stays `/home/tony`, no script fails for that reason.
4. **MA1.3 fails at first.** On old S the commit hook calls the OTS client from tupay's own `.venv`. (`/opt/ots` exists only on the box. A first draft of this prediction said otherwise, and was corrected before this commit after checking.) Two things are not in the snapshot, and the account names neither:
   - `.venv` is untracked, so it is not in the bundle;
   - `.git/hooks/post-commit`, the wrapper that calls `scripts/hooks/post-commit`, is never carried by a clone.

   So a fresh clone stamps nothing until the hook and the venv are restored.
5. **MA1.12 fails at first.** The account says "reinstall the two systemd timers", but wam-nuc's host key and tupay's ssh key are not in the snapshot. The first run cannot reach R until a key is provisioned. (This is the recovery account's own dependency.)
6. **MA1.9 reproduces.** The paired tests' outcomes depend on the code and the schedules, not on the host. **Lower confidence:** the third steward found that timing can decide outcomes, so a pair that was flaky before may be flaky again. That would be reported as flaky, not as a failure of migration.
7. **More than 5 steps are taken by hand that the account does not list.**
8. **MA1.15 produces at least 3 amendments to the account.**

**The scoring is plain:** each prediction holds or does not, at the first rehearsal. The predictions say what the steward expects to break. A prediction that turns out wrong is information about the steward's model of tupay, and is reported as such.

## 5. Not in scope
- The house's own migration (the custodian's).
- Other residents' data.
- The choice of system.
- Per-door Unix identities. These are the house's decision. This contract measures their effect on tupay, through prediction 3.

## Amendment A1 (2026-11-12, additive; informed by no outcome, since no rehearsal has run)
**Tony:** amending this acceptance contract is "permissible in an emergency situation only, with a clear record of any deviation." So:
- the clauses, the cutover rule and the registered predictions (§4) stay as they are, unless an emergency forces a change;
- such an amendment names the emergency, the clause it changes, what was done instead, and who decided;
- it is logged before cutover, or, if the emergency prevents that, immediately after.

A deviation without a record counts as a failure of MA1.15.
