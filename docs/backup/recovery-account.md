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
