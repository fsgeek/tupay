# Tupay's binding to the generic backup contract (draft 5; not registered)

The twelfth steward, 2026-11-12. This binding maps the roles of `contract-draft-7.md` onto tupay's machines, directories and values. A change of host is a new version of this binding; it is not a change to the contract. **Binding v1 describes the host before the move. The post-move binding, v2, is written when the house's new system exists (`host-requirements.md`).**

## Roles
| Role | Bound to (v1) |
|---|---|
| S (T1) | WAM-THREADRIPPER, under WSL |
| Sources (T2, T20) | tupay's git repository (every ref); `../tupay-private/`; `../tupay-homes/` |
| R (T3) | wam-nuc, at `backups/tupay/` |
| Restore host (T4) | the box (`ubuntu26-test` VM), which has no tupay sources and no path to S |
| Freshness checker (T23) | a process on wam-nuc |
| Notice channel (T29) | the plaza, as `guest:tupay`. **Its record is on S**, so EX1.6 applies to this binding. |
| Caches (T21) | `.cache`, `go` and package caches under `tupay-homes/` |
| Credential (T13) | file names matching `auth.json`, `.credentials.json` and `*credential*`; content reported by `scripts/steward/secrets-scan.sh`, pattern set v1 (mutation pair: `secrets-scan-check.sh`) |
| Logged reason (T26) | an entry in `docs/seed-log.md` |
| Hosts that can be suspended (BF1.14) | the box (lent to other residents); S (WSL); wam-nuc (power) |
| Daily check (T24) | runs on S |

## Values (derivations in contract §6)
- *I* = 24 h.
- *M* = 1 d.
- *P* = 7 d.
- *H* = 36 h, which is *I* + 12 h.
- *D* = 1 h.
- *X* = 2 h.
- *Rb* = 2 d.
- ***G* = 72 h** (recoverable age, B1.19). It must exceed *I* + *X* + *M* = 50 h. 72 h tolerates one missed run or check, and not two.
- *K* = 14 d and *Mo* = 6 months.
- ***Q* = 0.05.** Measured 2026-11-11 from 9 quiet runs. `tupay-private/` and `tupay-homes/` did not change; the bundle's size moved between −0.87 % and +1.32 %. Its noise under author load is unmeasured, so it is measured again after the first round with authors.
- Derived: ***Dmax* = 27 h** and ***T* = 51 h**, both under contract §6's conditions.

## What this binding changes in what you can recover
The baseline is `recovery-account.md`, checked 2026-11-11.

| Row of the account | Clauses that change it |
|---|---|
| Restore tested once, by hand | Every snapshot restore-checked within *M*, from R alone (B1.8); **a demonstrated-recoverable snapshot never older than *G*, or a reported violation (B1.19)** |
| Corruption at R found only by chance | Every protected snapshot re-read every *P* (B1.12) |
| Snapshots lost at R go unnoticed | An inventory at every run and check (B1.13) |
| A copy can silently miss files | Completeness against an inventory (B1.17) |
| Retention by count | A way back by age, from a restore-checked snapshot (B1.4) |
| A source emptied by mistake is copied "successfully" | Reported within *Dmax* (B1.15) |
| S's silence unseen | Seen by the checker on wam-nuc (B1.7). Delivery while S is down: **open (EX1.6)** |
| A credential could enter in a commit | Scanned at every run (B1.5, AI1.5) |

**Accepted by v1 (draft 6, B1.17):** no file is silently omitted. Append-only files, such as author transcripts, are captured as a prefix and do not fail a run. While a file rewritten in place cannot be captured untorn, each run fails and is reported, until a run can capture it.

**Not changed by v1:**
- S and wam-nuc lost together (EX1.1; an off-site copy is a second contract);
- plaintext at wam-nuc (EX1.7; encryption is contract v2);
- harness credentials, which are never backed up, by design.

## The rung below (a comparison of behaviour)
The rung below is `backup.sh`, its two timers, `backup-check.sh` and `backup-alert.sh`.
- **It gives:** B1.1 without completeness; B1.5 by file name only; part of B1.6; B1.9, through the timer; and part of B1.7, from S.
- **It lacks:** B1.3 and B1.8 from R alone, B1.4, B1.12, B1.13, B1.15, B1.16, B1.17, B1.18, and a checker off S.
- Its acknowledgement defect was fixed on 2026-11-08 (Qwen's finding 10).

If the service cannot beat both this rung and restic on what they lack, the finding is that a rung was enough.

## Open, for Tony (one batch, none blocking)
1. **A notice channel that does not depend on S.** Recommendation: wam-nuc sends a single kind of push message when S has been silent longer than *H*, or the daily check has not run for 2 *I*. Which channel would you notice?
2. **An ssh key for wam-nuc that is not held only on S.** Recommendation: create one and keep it in the house's new key management.
3. **The move as the first real restore.** This is settled (log, 2026-11-11). The migration acceptance contract (`migration-acceptance-draft-1.md`) defines what passing means.
