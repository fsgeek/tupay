# W1: does the four-part contract form reduce misreadings? (pre-registration DRAFT 2; NOT registered)

The twelfth steward, 2026-11-12; draft 2 by the thirteenth, 2026-11-18, adding the baseline (§ Baseline) and the families (§ Families), per its acceptance decisions 1 and 3. Nothing else changed from draft 1. The id is W1, for wording: F1 collides with the seed's failure cells. **This draft registers nothing.** It is registered only after an outside review of it, together with the prose arm, has been disposed of, and its review is the one the log names as next (2026-11-11 and 11-12). Ids are never reused.

## Question
The idea of reducing specification ambiguity with a controlled language was Andrej Karpathy's; Tony brought it to tupay (2026-11-07; attribution corrected 2026-11-13). The steward turned the question into a test (log, 2026-11-07 and the amendment that day): **does a contract written in the four-part form produce fewer consequential misreadings than the same obligations written as prose?**

## Arms
- **Arm F (four-part):** `docs/backup/contract-draft-7.md` with `binding-tupay.md`.
- **Arm P (prose):** `docs/backup/contract-prose-arm-draft-1.md` with the same binding.
- **The same obligations.** Before registration, an outside review checks, clause by clause, that the two forms carry the same obligations. Every difference it finds is fixed in the prose arm, never in arm F, so the treatment stays what Tony read.
- Each arm has **one implementation author and one model author**, briefed symmetrically. The briefs are the same apart from which contract file they name.
- **Families:** implementations outside Claude, with the same family in both arms; models from a different family than the implementations, also the same in both arms. The families are named to Tony before launch.
- Authors run in the sandbox under the current practice file.

## Measures (fixed here)
1. **Primary: consequential misreadings.** These are found after the first versions, by:
   - (a) model–implementation divergences;
   - (b) failures under the injected failure-model cells and the hold-out schedules, which a third family writes from the contract alone, with only their hashes committed until both arms' first versions are in.

   A **judge** from a family that is neither author family rules on each finding, given the finding, the contract text of its arm and the artifact, with the arm's name hidden where possible. It classifies the finding as **misreading** (the artifact follows a reading the text does not support, or one of two readings the text permits), **implementation defect**, **contract defect** (the text is wrong or contradictory in both forms) or **other**. The count is the misreadings per arm.
2. **Divergence count** per arm: model against implementation, on shared schedules.
3. **Clarifying questions** each author raises, and **declared limitations**.
4. **Cost:** author tokens and wall-clock per arm, and the steward's and Tony's attention.

## Predictions and scoring (fixed here)
- **W1-1 (the treatment helps):** arm P's misreadings exceed arm F's by at least 3. **It does not hold** if arm F has as many or more. Anything in between is **inconclusive**.
  - The threshold of 3 is stated without a basis in any earlier measurement, because none exists. With one author pair per arm, only a large effect can show, and the registration says so.
- **W1-2 (harm to divergence):** the four-part form **harms the diagnostic** if arm F has fewer divergences than arm P (measure 2) while W1-1 does not hold. That would mean the authors agree more without misreading less.
- **W1-3 (cost):** arm F's author tokens exceed arm P's by more than 25 %. This prediction is about cost, not correctness, and it is reported beside the others.

Contract defects (measure 1, class 3) count against **both forms**, and are reported as findings about the contract, not about the arms.

## Known limits
- One pair per arm. The steward wrote both forms, so the prose arm's quality is the steward's; the equivalence review checks only the obligations, not the quality of the writing.
- The four-part form was hardened by four review rounds before the prose arm existed. The prose arm inherits every fix, but not the scrutiny of form that those rounds gave arm F.
- The steward has read every review, and every author brief gets a non-Claude review for leaks of the reviews' findings.
- The judges' classification is the weakest link. Two judges from different families rule independently, and where they disagree, the result is reported under each judge, as in D2.

## Baseline (added in draft 2)
Tupay is the instrument and the services it builds are its specimens (log, 2026-11-13). The rung below, `scripts/steward/backup.sh`, was written without the workflow. **Each arm's implementation and `backup.sh` are run against the same injected failure cells (BF1.x) and the same hold-out schedules**, and against the migration acceptance contract when the move happens.
- **Measure 5, the baseline:** for each of the three (arm F's implementation, arm P's implementation, `backup.sh`), the number of injected cells and hold-outs after which B1.19 holds (a demonstrated-recoverable snapshot younger than *G* exists) and every violation is reported as the contract requires.
- **W1-4 (the workflow beats the rung below):** both arms' implementations meet B1.19 and report violations in strictly more cells than `backup.sh`. **It does not hold** if either arm's implementation meets it in no more cells than `backup.sh`. *Note:* `backup.sh` was not written to this contract, so some of its failures are expected by construction. The prediction is about whether the workflow's specimens are better than the specimen built without it, not about fairness to `backup.sh`.

## Families (added in draft 2; named to Tony before launch)
- Implementation authors, both arms: **Codex** (GPT, by subscription).
- Model authors, both arms: **Grok** (xAI, by subscription).
- Hold-out author: **Gemini** (`agy`, by subscription), from the contract alone.
- Judges: **Qwen** and **DeepSeek** (through OpenRouter), ruling independently.
- Review of this draft and the prose arm's equivalence: **Kimi** (Moonshot, through OpenRouter), which takes no other role in W1.
- The steward (Claude) authors neither side.

## Not in scope
Building the backup service itself is the round's by-product, not its question. Which arm's implementation, if either, becomes the service tupay runs is decided after scoring. Both are measured against the rung below and against migration acceptance.
