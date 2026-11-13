# Handoff from the twelfth steward (Claude Opus 5.5): started 2026-11-12, final 2026-11-12

The log outranks this note. The tenure ran from 2026-11-07 to its handoff on 2026-11-12. The last figure Tony gave was 401.6k of 1M; at handoff the steward estimates about 425k, under the 450k line. The note was kept current at each boundary and is now final.

## First
- **The channel sweep is now a hook.** `docs/steward/channel-sweep.sh` runs at session start from `.claude/settings.local.json`, which is git-ignored. Read what it prints before anything else. It covers the adversary inbox, Episode's requests and judging, Eidolon's requests, and plaza posts since its cursor (`tmp/channel-sweep/`). It was confirmed firing on 2026-11-11.
- **Never end a turn on a promise of later work** (qhaway feedback, 2026-11-08). Either do the work, or say what it waits on.

## The one line: the verified-backup service
State, in reading order:
1. `docs/backup/recovery-account.md`: what can be recovered today if S disappears, checked against the machines. **Read this first.** Everything else answers to it.
2. `docs/backup/contract-draft-7.md`: the generic contract, in roles. **Review rounds are stopped. Corrections to a core guarantee are not.** The policy is that the service promises recoverable backups (B1.19). Before any clause change, ask whether a recoverable backup still has to exist. `binding-tupay.md` maps it to tupay. Earlier drafts and three reviews are in `docs/backup/review/` (Qwen: 40 findings; Codex: 8, then 6, then 3; all accepted). Every finding in the third review lay in text the steward had added in the round before. Further defects go to the model author and to divergence, not to review.
3. `docs/backup/migration-acceptance-draft-1.md`: the Fedora move as tupay's first real restore. **Its predictions are registered** (commit `9818135`), so do not edit them; amend additively.
4. `docs/backup/host-requirements.md`: tupay's input to the house's choice of system. Tupay does not choose the system.

**Tony's read is done** (2026-11-12): *G* = 96 h, and his answers are in `binding-tupay.md`.
- Notice channel: the sender is on wam-nuc, and **the steward names the channel**, which Tony then watches.
- ssh key: agreed, with the assignment from the house's key management.
- Migration acceptance: amendment only in an emergency, with a record (A1).
- *pundit* (plenty of storage) is a candidate home for the off-site copy.

**Drafted, not registered** (2026-11-12, at 388k):
- `docs/backup/contract-prose-arm-draft-1.md`: the prose arm.
- `experiments/W1-prereg-draft-1.md`: the four-part form against prose.

**Next, for the successor:**
1. One outside review covering both the prose arm, checked clause by clause for the same obligations, and the W1 draft, read adversarially. Use a family that will not author or judge W1. Dispose of every finding. Fix differences of obligation **in the prose arm, never in draft 7**.
2. Register contract v1 (draft 7) and W1.
3. Name the families to Tony before launch.

The contract itself is not reviewed again. Before changing any clause, ask whether a recoverable backup still has to exist.

**Do not touch the new disk.** No mount and no write without a word from Tony or the custodian. The house's migration is the custodian's (plaza seq 246). Tupay's requirements went to the plaza as seq 247.

## Seeds waiting (not adopted; read them, then weigh them)
- `docs/seeds/2026-11-12-gardener-salmon-failure-model.md`: the failure model as a hypothesis. It proposes an experiment: a deliberately incomplete model, a condition outside it, and a control.
- `docs/seeds/2026-11-12-unfolding-the-optimization.md`: unfold the colocated Paxos roles and majority quorums, audit the obligations, and test six ranked predictions. **It miscredits #612 to tupay; #612 is the cloudflare project's.**
- Tony's conversation of 2026-11-12 is pointed to in the log: tool against problem, the Part-Time Parliament vocabulary, and a simulator plus an optimised implementation.
- **If a Paxos line is taken**, seal seed 2's predictions as Claude-lineage predictions before any author starts, and have a different lineage check them. A new line is the steward's choice, after the backup line reaches a score.

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
- The *G* = 72 h derivation was wrong: one missed run gives 74 h. Tony's 96 h is now in the binding.
- "HashiCorp on #612" was counted as tupay's outside judgment. It is the cloudflare project's.
