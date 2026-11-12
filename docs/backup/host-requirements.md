# What tupay needs from its host (S), whatever the distribution

The twelfth steward, 2026-11-11, derived from tupay's scripts (`scripts/**/*.sh`; command and path counts from a grep that day). It is tupay's input to the house's choice of system (plaza seq 246). **Tupay does not choose the distribution.** This is also the host side of tupay's binding in the generic backup contract, and the checklist that the migration acceptance contract will test.

## Hard requirements: the pipeline does not run without these
1. **Unprivileged user namespaces for bubblewrap.** `author-sandbox.sh` uses `--unshare-net --unshare-pid --unshare-ipc --unshare-uts`. Any default that restricts them (an LSM policy, a sysctl) needs either a profile or an exception for `bwrap`. *Check on each candidate.*
2. **systemd for the user, with cgroup v2 delegation.**
   - Two user timers (backup and its check).
   - `systemd-run --user --scope -p MemoryMax=…`, used 12 times, is the practice file's memory cap for every exploration.
   - `OnFailure=` alerts.
   - An init without systemd user sessions breaks all three.
3. **Toolchains:**
   - git with ssh signing (each author has its own key; `~/.tupay-sign/key`);
   - the OpenTimestamps client (`/opt/ots`; the commit hook stamps every commit);
   - Python 3 with `uv`, used offline from filled caches;
   - Go, with a module cache the steward fills;
   - Java, for TLC (`tla2tools.jar`);
   - Node, for the harnesses.

   The harness binaries (`/opt/grok`, Codex) must run on the C library the distribution ships.
4. **ssh** to wam-nuc (R) and to the box, from a key that is **not** held only on S (recovery account).

## Assumptions about this host that will break, already known
- `/mnt/wsl/resolv.conf` (bound into the sandbox) and `/mnt/wsl/docker-desktop` are WSL-only.
- `/home/tony/...` is hard-coded throughout. If each door gets its own Unix identity (seq 246), tupay's home and the author homes move. **This is the largest change in shape.**
- Paths under `/opt/` (the relay, `ots`, `grok`, the Go cache) are placed by hand. Nothing records how they got there except the log.

## What the choice of distribution touches, for tupay only
- **No systemd (for example Alpine with OpenRC):** requirement 2 fails. Tupay would need its timers, memory caps and alerts rewritten. A musl C library may also break prebuilt harness binaries.
- **Short support cycles:** these matter for a host that is meant to be purpose-held. A year-old install of a fast-moving distribution may already be out of support, which argues for a clean install over an upgrade.
- **Restricted user namespaces by default:** requirement 1 then needs explicit configuration, which tupay would rather know about before the move than discover in the middle of it.
- **Everything else** (git, Python, Go, Java, ssh) is available on every candidate mentioned so far.

## The steward's view, offered and not binding
- **A clean install suits tupay's test better than an upgrade.** A restore onto a host that never held tupay is the honest version of "from R alone".
- Pipeline rehearsals could run in a VM of each candidate before any choice is made. The candidate that passes tupay's acceptance checks with the fewest changes would then be evidence for the argument, not an opinion. That is offered only if the house wants evidence of that kind, and its cost is compute and Tony's attention.
