# Handoff from the thirteenth steward (Claude Opus 5.5): FINAL (2026-11-18)

The log outranks this note. The tenure began 2026-11-13, at acceptance commit `86c2971`. The last context figure Tony gave was 369.3k of 1M (2026-11-18). The handoff line is 450k. **This note is final.** Everything below was pushed to GitHub at `b6134ce` after a clean secrets scan. Later commits are the handoff itself.

## First
- **The channel sweep is a hook** (`docs/steward/channel-sweep.sh`, from `.claude/settings.local.json`). Read what it prints before anything else.
- **Two daily checks guard the backup:** `backup-check.sh` (14:00Z: backups are being made) and, new this tenure, **`restore-path-check.sh`** (14:30Z: the restore host can still reach R by its own key). A failure posts to the plaza as guest:tupay.
- **Never end a turn on a promise of later work.** Do it, or say what it waits on.

## The line: the verified-backup service, and W1
**State, in reading order:**
1. `docs/backup/recovery-account.md`, **including its new section, "Recovery-path dependencies"**. No need in the table is *promised*, and every one is *observed*. The open question that matters most is on which physical machine the box (a Hyper-V VM) runs. If it is S's machine, losing S loses the restore host too. **Answered (Tony, 2026-11-18): it runs on WAM-THREADRIPPER, S's machine.** The restore host shares fate with S. Until binding v2 moves the restore host to separate hardware (*pundit* is the first candidate), a restore after machine loss rests on Tony's key reaching wam-nuc from wam-vector or the Mac. **Verifying that path is the first owed check.**
2. `docs/backup/contract-draft-7.md`, arm F. **Registered as backup contract v1** (commit `d65e9b4`; sha256 `aa782b31…`). From now on, changes of obligation are new versions.
3. `docs/backup/contract-prose-arm-draft-2.md`, arm P. **Kimi's check found it obligation-equivalent to draft 7** (`review/kimi-w1/check-1.md`).
4. **`experiments/W1-prereg.md`, registered** (`d65e9b4`; drafts 1 to 4 kept): **an exploratory pilot with arms F, P and N.** N is a Codex implementation author with the prose arm and no workflow. P against N tests the workflow, and F against P tests the form. It has a tag-based unit, a decision tree, a primary count that needs both judges to agree, and determinate reporting. Its predictions are W1-1 (form), W1-3 (cost) and W1-5 (workflow). **W1-2 and W1-4 are retired.**
5. `docs/backup/review/kimi-w1/`: the review (26 findings, all accepted), `DISPOSITIONS.md`, check 1, the diffs, and (when it arrives) check 2.

**Stop rule (log, 2026-11-18):** after Kimi's second check of draft 4, only blocking items are fixed, each fix is registered without a further check, and the rest become known limits.

**Status:** check 2 returned one blocking item (33: no fixed scoring horizon). It was fixed (a horizon per schedule, committed with the hash; later windows censored), and items 34 to 37 are registered known limits. **Contract v1, the prose arm, binding v1 and W1 are registered.** Nothing has launched.

**Next, for the successor. Steps 1 and 2 are done; start at step 3:**
1. Dispose of check 2 under the stop rule.
2. Register contract v1 (draft 7) and W1 (draft 4 plus blocking fixes) in one commit.
3. **Rebuild the box's author setup.** The 2026-11-17 Hyper-V rollback to the June checkpoint removed the `tupay-author` user, its home, and the egress and nft units. Run `scripts/steward/box/box-setup-author.sh` and the units in `scripts/steward/box/`, then `box-check.sh`.
4. **Generate the author-facing contract copies mechanically** from the normative sections only. Leave out draft 7's history preamble, §7 and §8 (§8 holds a steward hypothesis: the steward's pre-review finding S1), and the prose arm's header paragraph. List the omitted headings in each brief.
5. **Hold-outs:** Gemini (`agy`), given the prose arm, the binding and the failure model only. At least 2 schedules for each of the 13 BF1 cells, **every assertion tagged `derives:`, and every schedule stating its own fixed scoring horizon** (W1 measure 5). Commit the count, the mapping and the hashes before any author starts.
6. **Briefs:** five, symmetric, with the clarification rule (record the question, state the reading, go on), the 6 h wall-clock cap, and the turn cap. **A non-Claude leak review of every brief** goes to a family with no W1 role, not Kimi again if avoidable; GLM has no role in W1 so far. Run `inputcheck.sh` on every checkout.
7. **Name the families to Tony** (W1 § Families) and launch all five concurrently. Every box run gets a tracked watcher.

## Also running or owed
- **First owed check:** that Tony's key reaches wam-nuc from wam-vector (`ssh tony@192.168.111.160 hostname`). The restore host runs on S's machine, so this is the last resort after a machine loss.
- **M365 predictions** (`experiments/M365-2026-11-postmortem-predictions.md`, A1 to A3a): provisionally scored against Microsoft's preliminary PIR (`M365-2026-11-provisional-score.md`, Brier at chance on 1 to 8). **Owed:** a non-Claude judge for prediction 4, a non-steward review before the score is final, and the **final PIR** (due about 11-20) for 4, 11, 12 and the final score. The PDF is in `tupay-private/m365-2026-11/`, and its notice forbids reproduction.
- **Meerkat predictions** (`experiments/Meerkat-2026-11-defect-predictions.md`), scored against Cloudflare's own publications by 2027-11-30. Tony has no objection to them being public.
- **The practice audit** (`docs/steward/practice-audit-2026-11-18.md`): 37 rules, of which 16 are method, 7 mechanism, **4 failed** and 9 single-incident. Its proposals are **not yet applied**: mechanisms for the four failed rules, single-incident rules moved to their point of use, and START.md's entry ritual changed. Rule 18 (no steward hypotheses to authors) failed a third time, in draft 7 §8.
- **v2 failure-model cells, recorded, not written:** a recovery-path dependency that is unavailable, possibly because of the failure itself; a recovery mechanism that amplifies the failure (M365); demand at recovery; a restore host whose state is reverted, or changed by another party. These come with encryption (the key holder).
- **The 2026-12-31 line** is, in Tony's framing, a decision about whether tupay has turned into theater. The 11-26 report against the month's measure is still owed.

## Decisions standing
- Tupay is the instrument. The services are specimens, and they are judged against specimens built without the workflow, which for the backup line is arm N. `backup.sh` is only descriptive.
- One line at a time. A Paxos line waits behind the backup line, and Eidolon's steward is asked first.
- Three seeds are kept as given (`docs/seeds/`). They share one experiment: an incomplete model, a condition outside it, and whether it is noticed.
- The idea of reducing ambiguity with a controlled language is **Karpathy's**. Tony brought it.

## Errors and lapses this tenure (all logged)
- My patches carried the next defects in both rounds this tenure (W1 drafts 3 and 4), continuing the twelfth's four. The stop rule is the response.
- Acceptance decision 1 named `backup.sh` as the baseline, and Kimi showed it is unfair. Corrected by arm N.
- "Owned by another resident" was written about the box's `arangod` before the owner was known. Corrected.
- An assumption of user-mode thread pools in prediction 12's reasoning. Corrected (A3a).
- The box key's removal was logged as unexplained, which was correct, and it was then explained by the rollback.
