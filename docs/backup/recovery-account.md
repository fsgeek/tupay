# If S disappears tonight: what tupay can recover, from what, and what is lost

The twelfth steward, 2026-11-11, written at Codex's request (review of draft 3) and checked against the machines that day. This describes **what exists today**, `backup.sh` and its timers, not what any contract draft promises. S is this machine (WAM-THREADRIPPER under WSL).

## What survives, and where
| Material | Survives on | Age at worst |
|---|---|---|
| `main` and its history | GitHub (`origin`, fully pushed 2026-11-11) **and** wam-nuc's nightly git bundle | GitHub: the last push. wam-nuc: up to about 24 h |
| The other 23 local branches (the arms' model and impl branches: `impl-v1`, `model-v2.1`, `x1-*`, `fixr-*` …) | **wam-nuc's bundle only.** 23 of tupay's 24 local branches are not on GitHub | up to about 24 h |
| `tupay-private/` (sealed and licence-restricted material, author transcripts), 55 MB | wam-nuc only | up to about 24 h |
| `tupay-homes/` without credentials and caches (author transcripts, egress logs), 406 MB | wam-nuc only | up to about 24 h |

wam-nuc keeps the last 14 nightly runs (the oldest is about two weeks back). Each run is verified there against its manifest when it is made. **Restore has been tested once, by hand** (2026-11-03): the bundle cloned with every branch, and `tupay-private/` came back byte-identical.

## How a restore goes, today
1. From a machine that can ssh to wam-nuc, copy the newest `backups/tupay/<run>/` directory.
2. Check its manifest: `sha256sum -c MANIFEST.sha256`.
3. `git clone tupay.bundle tupay`, then `git branch` for each `origin/*` ref you want back. Point `origin` at GitHub again.
4. Copy `tupay-private/` and `tupay-homes/` next to it, under `projects/`.
5. Log the harnesses in again (Codex, Grok), reinstall the two systemd timers from `scripts/steward/systemd/`, and fill the Go and uv caches as the practice file says.

None of these steps needs a key, because snapshots are not encrypted today.

## What is lost or delayed, and is accepted today
- **Up to a day of work** that has not been pushed: branches other than `main`, and everything in `tupay-private/` and `tupay-homes/` since the last 11:15Z run.
- **Harness credentials**, by design. They are never copied off S, so you log in again.
- **Caches** (Go modules, uv). They are refilled, which costs time, not data.
- **The 60 sibling author checkouts** (`../tupay-*`, several GB). They are not backed up. What mattered in each was exported into tupay's history as a signed bundle. What is lost is only the working state of finished runs.
- **Not tupay's to back up, and not known to be backed up by anyone:** the steward's own session transcripts (`~/.claude/projects/-home-tony-projects-tupay/`, 109 MB), which khipumaq indexes, and the qhaway memories. Whether khipumaq's and qhaway's stores have their own backup is their owners' answer, not tupay's. The move is the time to ask.
- **The wait:** today nothing would tell you that S has gone silent, because the alarm and the plaza both live on S. You would notice by not seeing tupay, not because anything told you.

## What the restore depends on that is not in the backup
- **An ssh path to wam-nuc from somewhere other than S.** The key S uses lives on S. *Unknown to the steward:* whether your Mac or another machine has its own key for wam-nuc. If none does, recovery needs physical access to wam-nuc.
- **wam-nuc itself.** If S and wam-nuc are lost together (a fire, or one move carrying both), only `main` on GitHub survives. Contract EX1.1 says so, and the off-site copy is the remedy it proposes.

## Why this comes first
Every clause in the contract drafts should make one of the rows above better, or remove a loss from the list. The Fedora move (plaza seq 246) will be **the first real restore**. Done from wam-nuc onto the new disk, with the old disk untouched as the way back, it is also the test of this account.

---

## Recovery-path dependencies (added 2026-11-18, by the thirteenth steward)
What each restore step needs, beyond the bytes at R. Each need is marked **promised** (a party has committed to it), **observed** (it works today, and nobody has promised it) or **incidental** (a side effect nobody intends). The last column says what it could fail together with. This section was prompted by the M365 outage and Tony's Akamai login (log, 2026-11-14), and by the box rollback (log, 2026-11-18). The rows above are unchanged. Where this section updates one of them, it says so.

| Step | Needs | Held where | Kind | Could fail together with |
|---|---|---|---|---|
| 1. Reach R without S | the restore host's own key to R (`tupay-restore-wam-nuc`, read-only by rrsync) | the box | observed; **checked daily** by `restore-path-check.sh` from 11-18 | **the box's physical host, if that is S's machine (unknown; asked of Tony)**; a hypervisor rollback (happened 11-17; a June checkpoint still exists); suspension (BF1.14) |
| | Tony's route to the box | wam-vector (Tony verified, 11-13) | observed | — |
| | Tony's route straight to wam-nuc | wam-nuc authorizes one personal key (SHA256:Nu/tv…), which S holds. Tony keeps his keys backed up privately. | observed; **whether wam-vector or the Mac holds that exact key is unverified** | S, if no other machine holds it |
| 2. Check the manifest | `sha256sum` | any host | — | — |
| 3. Clone the bundle; point `origin` at GitHub | git; to push, a GitHub ssh key and the account | Tony's keys (private backup); account second factor: backup codes (Tony) | observed | email, only if a recovery falls back to it. Tony avoids email codes. |
| 4. Copy `tupay-private/`, `tupay-homes/` | nothing beyond step 1 | R | — | — |
| 5a. Log the harnesses in again | Codex (OpenAI account), Grok (xAI), Claude Code (Anthropic) | Tony's accounts; backup codes | observed | **per account, unverified:** whether any login falls back to email |
| 5b. The stamp hook | the OTS client (`uv sync` from PyPI; `.venv` is not in the bundle) and the public OTS calendars | the internet | observed | internet loss. Stamps stay *pending* and then upgrade, which delays but does not block. |
| 5c. Signing new commits with the project key | GPG key `1D7C4A68…` | `~/.gnupg` on S; Tony believes there is a separate saved copy | observed. **Accepted recovery: regenerate**, publish the new key on GitHub, update `NOTICE`, and keep the old public key published. History stays attested by OTS, independently of the key. | S |
| 5d. Timers, the Go and uv caches | systemd units in the repository; `proxy.golang.org` and PyPI | repository; internet | observed | internet loss (it costs time, not data) |
| 5e. Model authors on the box | `box-setup-author.sh`, the egress units, and the toolchains, rebuilt | repository; the box | observed. **Lost in the 11-17 rollback; to be rebuilt before any model author runs** | the box's host; rollback |
| Notice of S's silence | the plaza and the alert | **S** | — | **S**, as row "The wait" above says. This is unchanged and is still the account's largest gap. |

**Superseded rows above, by fact:**
- "Unknown to the steward: whether your Mac or another machine has its own key for wam-nuc." The box has had its own key since 11-13, re-made on 11-18 and now checked daily. A direct path from Tony's machines is still unverified.
- "None of these steps needs a key." Steps 1, 3 and 5 need keys or logins, as listed above. Step 2 does not, because snapshots are not encrypted.

**The question that matters most:** on which physical machine does the box (a Hyper-V VM) run? If it is S's machine, "S disappears" also takes the restore host, and step 1 rests on Tony's personal key alone.

**Answered 2026-11-18 (Tony): the box runs under Hyper-V on WAM-THREADRIPPER, the same physical machine as S.** So "S disappears" in the sense of the machine also takes the restore host. The data-path rule T4 holds (the box has no path to S's files), but the two **share fate**. The contract requires physical separation only for R (T3), not for the restore host, so this is a binding-level risk, not a contract violation. **Until the binding changes, a restore after machine loss rests on Tony's own key reaching wam-nuc from wam-vector or the Mac. That path is still unverified.**
**Recommended for binding v2 (the post-move binding):** a restore host on separate hardware. *pundit*, which Tony offered for storage, is the first candidate. The box can stay as a second restore host.

**Verified 2026-11-22: the last-resort path works.** wam-vector reaches wam-nuc with its own key (`~/.ssh/wam-nuc-ed25519` through its `Host wam-nuc` entry), non-interactively, with no agent forwarded from S. Tony confirmed the same path by hand. So after the loss of WAM-THREADRIPPER (S and the box together), step 1 of a restore can start from wam-vector. **Noted for binding v2:** wam-vector's `known_hosts` entry for *pundit* predates pundit's reinstall, so it will fail host-key verification until it is replaced. That matters if pundit becomes the restore host.

## 2026-11-22: the restore host moves to pundit (binding v2)
**Step 1, reach R without S:** the restore host is now **pundit** (separate hardware), as user `tupay-restore`, with its own read-only key to R (rrsync, only from 192.168.111.165). It is checked daily by `restore-path-check.sh`, whose mutation pair passes against pundit. The box's key line at R is removed, and the box is retired from the role. **Superseded by this section:** the 11-18 rows that name the box as restore host, and the fate-sharing with S that they record.
**Drilled, steps 1 to 3** (`scripts/steward/restore-drill.sh`, snapshot 20261122T111803Z, 493 MB at R): manifest ok (8,831 entries), bundle cloned, fsck clean, 25 remote branches, HEAD `9dba8de` (S's `main` at snapshot time), about 11 s. Run twice: started from S, and **started from wam-vector**, whose `wam-nuc-ed25519` key `tupay-restore@pundit` now authorizes, with pundit's host key pinned there (SHA256:50iqQXRP…). So after the loss of WAM-THREADRIPPER, a restore can start from wam-vector onto separate hardware. Steps 4 and 5 (placing `tupay-private/` and `tupay-homes/`, re-login, timers) were not drilled.
**Still observed, not promised:** pundit's power, and the network. Pundit is shared with yanantin's weekly restore check (Sundays from 15:00Z), under another user. wam-vector's `Host pundit` entry still names an old address (.138); the drill used the address directly. That is Tony's file, so it is his to fix.
