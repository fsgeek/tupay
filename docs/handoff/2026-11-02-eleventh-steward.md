# Handoff from the eleventh steward (Claude Opus 5.5), kept from 2026-11-02, final 2026-11-07

The log outranks this note (`docs/seed-log.md`). The tenure ran from acceptance at 2026-11-02T19:31Z to this handoff at 391.3k of 1M (39%, Tony's figure), under the 450k line set at acceptance, at a boundary.

## First, before anything else
1. **Look at every channel before acting** (the five recorded cases, below):
   - `docs/adversary/inbox/`;
   - `episode/docs/requests/` and `episode/judging/`;
   - the plaza from seq 238;
   - `eidolon/docs/requests/`.

   A promise to look "at each boundary" failed in this tenure (case 5), so treat this list as the first command, not a rule to remember.
2. **Tony's answers on the backup contract** (`docs/backup/contract-draft-1.md`, "For Tony"). Nothing is registered until he has read it. Then an outside-family review, then registration.

## Standing state
- **D2 is final** (`experiments/D2-result.md`): D2-2 and D2-4 hold, D2-1 is not established, D2-3 and D2-5 do not hold, and D2-2g is void.
  - Appended after the result: Episode's second looks and executed models. **F01, F01b and F07 are defects in DCE 1.2.2's `logbuf` that the prior analysis missed.** They are TLC counterexamples, re-run here with identical results.
  - **Owed:** a non-Claude family models F01b and F07 from the DCE source and the finding text alone, without Episode's specs. This closes the dependence on one family's encoding. Do it before anyone outside the ayllu is told about the defects.
- **Backups:**
  - `tupay-backup.timer` (11:15Z daily) and `tupay-backup-check.timer` (14:00Z) send to `wam-nuc:backups/tupay`, with alerts going to the plaza as guest:tupay. The restore was tested once by hand.
  - **Owed:** a scheduled restore test; removing the roughly 20 stale `auth.json` copies in `tupay-homes/*/` while no author is running; and making `author-sandbox.sh` delete its copy when it exits.
- **Pushes:** tupay is pushed and current. Tony pushes too, and the PR rule is bypassed by design.

## Direction, in order (log, 2026-11-05 to 11-07)
1. **The verified-backup service:** tupay's own contract, code and Arariwa. `backup.sh` and restic are the rungs below it.
2. **PolyStore**, as tupay's author orchestrator. Its contract comes from an **adversarial customer**, a separate project whose family is not disclosed to tupay. The channel is fixed in `docs/adversary/CHANNEL.md`. Write nothing about the adversary's role. Before each launch, name the planned families to Tony and he answers only "conflict" or "fine".
   - Tony's hidden tests for the challenge layer have sha256 `6443bca7…a18e`, logged 2026-11-03.
   - The four guards against circularity are in the log (2026-11-06).
3. **The Episode rebuild**, contract-first: a library, SPDK, bitbucket, stage 1 first.
   - The answer key is sealed (`episode` `bf5ec91`, sha256 `64d77c4b…`), **unopened by this steward**. Episode's blindness list is adopted.
   - This steward has read the whole D2 answer key, so every brief gets a non-Claude review for leaks.
4. **Arariwa's first natural test:** tupay's own steward process, measuring the delay from evidence becoming available to being consumed, in three arms (`docs/arariwa-seed-critique-2026-11-07-reply.md`).
   - The five recorded cases of evidence that never reached its decision serve as calibration only.
   - The research seed and its critique are in `docs/`. This steward cannot choose held-out classes from the seed's five cases.
5. **Candidates, not started:** an RFC as the contract (RFC 1045, VMTP, first; see the log, 2026-11-07, and Tony's correction in qhaway); hashicorp/raft with #612 as witness; T1, once Tessera is active.

## Practice, proposed and not done
- **Prune `docs/steward-practice.md`.** This tenure's evidence: three of four "available, not retrieved" cases were fixed by rules that failed the next time, and the one fixed by a mechanism has held. The tenth steward's test still stands: a rule stays only if someone can show it would have caught something since it was written. Rules that keep failing should become mechanisms, or go.
- **Every exclusion expires** (backup B1.11). The same idea could apply to the practice file's own rules.

## Errors this tenure (all logged)
- D2 scoring: v1 treated a missing ruling as a negative and did not apply the leakage void (Qwen caught both).
- An unenforced push hold.
- A test bundle written into the working tree.
- A wrong "can't" about public data.
- The backup draft's unexplained *K* = 7, and a "not yet" with no trigger.
- Case 5: Episode's posts unseen for two days.
