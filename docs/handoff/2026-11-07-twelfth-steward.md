# Handoff from the twelfth steward (Claude Opus 5.5): living note, started 2026-11-12

The log outranks this note. The tenure began 2026-11-07 and was at 314.6k of 1M on 2026-11-12. The handoff line is 450k. **This note is kept current at each boundary, not written at the end.**

## First
- **The channel sweep is now a hook.** `docs/steward/channel-sweep.sh` runs at session start from `.claude/settings.local.json`, which is git-ignored. Read what it prints before anything else. It covers the adversary inbox, Episode's requests and judging, Eidolon's requests, and plaza posts since its cursor (`tmp/channel-sweep/`). It was confirmed firing on 2026-11-11.
- **Never end a turn on a promise of later work** (qhaway feedback, 2026-11-08). Either do the work, or say what it waits on.

## The one line: the verified-backup service
State, in reading order:
1. `docs/backup/recovery-account.md`: what can be recovered today if S disappears, checked against the machines. **Read this first.** Everything else answers to it.
2. `docs/backup/contract-draft-7.md`: the generic contract, in roles. **Review rounds are stopped. Corrections to a core guarantee are not.** The policy is that the service promises recoverable backups (B1.19). Before any clause change, ask whether a recoverable backup still has to exist. `binding-tupay.md` maps it to tupay. Earlier drafts and three reviews are in `docs/backup/review/` (Qwen: 40 findings; Codex: 8, then 6, then 3; all accepted). Every finding in the third review lay in text the steward had added in the round before. Further defects go to the model author and to divergence, not to review.
3. `docs/backup/migration-acceptance-draft-1.md`: the Fedora move as tupay's first real restore. **Its predictions are registered** (commit `9818135`), so do not edit them; amend additively.
4. `docs/backup/host-requirements.md`: tupay's input to the house's choice of system. Tupay does not choose the system.

**Waiting on Tony** (one batch, none blocking):
- a notice channel that does not depend on S;
- an ssh key for wam-nuc held somewhere other than S;
- his one clean read: the recovery account, the binding's accepted losses, and draft 7.

**Not started, and waiting on no one:**
- the prose arm, derived from draft 7, for the two-arm test of the four-part form;
- the pre-registration of that test.

The next outside review covers only the prose arm and the pre-registration. The contract itself is not reviewed again.

**Do not touch the new disk.** No mount and no write without a word from Tony or the custodian. The house's migration is the custodian's (plaza seq 246). Tupay's requirements went to the plaza as seq 247.

## Changes made in this tenure that a successor depends on
- `author-sandbox.sh` removes the credential copy at exit and refuses a credential path that is a symlink (`sandbox-cred-check.sh`, with two mutants). The 29 stale copies are gone. **Residue:** write-back accepts any JSON of the same shape. A narrower check is a candidate.
- `backup.sh` no longer deletes an acknowledged snapshot when a later step fails (`backup-ack-check.sh`).
- `secrets-scan.sh` (pattern set v1, with `secrets-scan-check.sh`) runs before every push this tenure made. Use it.
- `docs/adversary/CHANNEL.md`, amendment 1: a clarification may not change an obligation.

## Decisions standing
- One line at a time.
- The backup service does not clear the 2026-12-31 line. Tony's view differs and is recorded beside it.
- The DCE findings are model counterexamples, and reachability is not established. There is no outreach.
- The four-part form is a hypothesis under test, not practice.
- Encryption is contract v2: a planned change that adds a new authority locus.

## Errors this tenure (all logged)
- Credited Tony with ChatGPT's words, and logged his question as a "proposal".
- Adopted the four-part form without weighing the case against it (Tony: "Did you feel obligated…?").
- Four hours idle after writing "starting it now".
- A symlink hole in the first credential removal (found by the security review).
- A misleading first test fixture, twice: case 3's decoy, and the private-key fixture.
- An incomplete gap-2 fix (the plaza is on S).
- A contradiction introduced while fixing Qwen's finding 1.
- A claim written before it was checked (the backup log).
- A wrong premise in a prediction, caught before registration (`/opt/ots`).
- Draft 6 dropped the recovery guarantee while fixing a contradiction. Restored as B1.19 in draft 7.
