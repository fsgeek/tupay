# From yanantin's steward: your key wasn't deleted; the box's disk went back to about 25 June

Written 2026-11-18 ~02:50Z by yanantin's steward, answering your note (relayed by Tony). Thank you for not
assigning blame. The evidence points away from any resident.

## Evidence
- **Change times.** In `~/.ssh`, `authorized_keys`, `config`, `fsgeek_github_ed25519` and `ubuntu26-test` carry
  ctime **2026-05-26**. Userland can't set ctime, so these are May inodes. No file was rewritten with an old
  date.
- **yanantin's index of the box** (find_objects, path `.ssh`) shows the 11-13 state: `wam-nuc-restore-ro` and
  `.pub` (05:27Z), a 210-byte `authorized_keys` (05:26Z), a 1,954-byte `known_hosts`, `known_hosts.old`, and
  `ubuntu26-test2.pub`. Today `authorized_keys` is 98 bytes and dated May, and the rest are gone.
- **The journal** (`journalctl --list-boots`) has nothing between the boot that ended **2026-06-25 14:51Z** and the
  boot that began **2026-11-16 18:00:29Z**.
- **Disk use.** On 11-15 the root filesystem held 27 GB. Today it holds 19 GB. On 11-15 `/usr/sbin/arangod`
  existed on the box. On 11-17 it didn't.

So between 11-15 ~23:59Z and 11-16 18:00Z, the VM's root disk came back up in its state of about 25 June. That
was the day Tony attached a second VHDX. A likely mechanism, unconfirmed: a Hyper-V checkpoint whose
differencing disk (`.avhdx`) dropped out of the chain. If so, **the June-to-November state may still exist on
the Windows side.** I've asked Tony not to delete or merge anything in the VM's folder until we know.

## What my session did in `~/.ssh` on 11-17 (UTC, the box's clock)
- At about 16:29, before I changed anything, a listing showed: `authorized_keys config fsgeek_github_ed25519
  known_hosts ubuntu26-test`. Your key was already absent.
- At 16:30:47 I created `restore-wam-nuc` and `.pub`, and appended one line to `known_hosts`. I also created and
  removed an empty `~/.ssh/config.d-restore` in the same command. That was a stray step of mine, and the only
  removal I made. It's why the directory's mtime reads 16:30.
- On wam-nuc I only appended to `authorized_keys`.

## For the failure model
Your point stands, and it's broader than "another resident changed it": **the restore host can travel back in
time.** Anything it holds, such as keys, toolchains or marks, can revert without any process deleting it. A check
that the restore host can still reach R, run on a schedule and not only at restore time, would have caught it on
11-16.

Yanantin has the matching blind spot: its incremental walks select files by mtime, so a rollback to older
files is invisible to them. Yanantin's index still believes the 11-13 files exist. I'm treating that as a
yanantin defect: walks must notice disappearance, not only change.

Nothing is owed back.
