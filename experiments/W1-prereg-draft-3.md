# W1: an exploratory pilot on contract form and on the workflow itself (pre-registration DRAFT 3; NOT registered)

Draft 1 was written by the twelfth steward (2026-11-12), and drafts 2 and 3 by the thirteenth (2026-11-18). Draft 3 answers Kimi's review of draft 2 (`docs/backup/review/kimi-w1/`, all 26 findings accepted). **This draft registers nothing.** Ids are never reused. **W1-2 and W1-4 are retired.**

## Status: exploratory and descriptive
Each arm has **one author per role**, so W1 cannot separate an arm's effect from the variation between sessions (Kimi, finding 17). **W1 claims nothing general about contract form or about the workflow.** It reports what happened with these documents and these runs. Its predictions are registered and scored as stated, and the result is labelled exploratory. Whether a replicated study is worth its cost is decided from this pilot, after scoring.

## Questions
- **Form (arm F against arm P):** with the same obligations, does the four-part form lead to fewer misreadings than prose? The idea of reducing specification ambiguity with a controlled language was Andrej Karpathy's, and Tony brought it to tupay.
- **Workflow (arm P against arm N):** with the same contract, does tupay's workflow (a formal model, paired tests from the clause × cell list, divergence as the diagnostic) produce an implementation that fails fewer schedules than one built without it? The instrument is judged by whether its specimens beat ones built without it (log, 2026-11-13; corrected 2026-11-18).

## Arms
| Arm | Contract given | Authors | Workflow |
|---|---|---|---|
| **F** | four-part, draft 7, plus the binding | one implementation, one model | yes |
| **P** | prose, `contract-prose-arm-draft-2.md` (or its successor, once the equivalence check passes), plus the binding | one implementation, one model | yes |
| **N** | the same prose arm as P, plus the binding | one implementation | **no**: no formal model, no paired tests, no divergence loop. The author writes its own tests as an engineer would. |

- **Author-facing copies** of both contracts are generated mechanically from their normative sections. Left out of both are draft 7's history preamble, its §7 (gaps) and §8 (Arariwa, which holds a steward hypothesis), and the prose arm's header paragraph. Each brief lists the headings left out. Draft 7 itself is not changed (the steward's finding S1).
- The worked cases (draft 7 §12) are in **both** contracts. Interpretation records are F's alone, because they are part of the treatment.

## Families (named to Tony before launch)
- Implementations, arms F, P and N: **Codex**.
- Models, arms F and P: **Grok**.
- Hold-outs: **Gemini** (`agy`).
- Judges: **Qwen** and **DeepSeek**, through OpenRouter, ruling independently.
- Reviews of this pre-registration: **Kimi**, which takes no other role.
- The steward (Claude) authors nothing that is scored.

## Author protocol (Kimi, finding 23)
- Every author has a fresh, isolated session, under the current practice file: the sandbox, a fresh home, a separate checkout, and no visibility of any other arm or of any review.
- **All five authors run concurrently,** so there is no order effect.
- **No clarifying question is answered during a run.** An author writes the question down, states the reading it chose, and goes on. The rule is the same in every brief.
- **Budgets:** each author has the same wall-clock cap (6 h) and the same harness turn cap. Arm N's single author gets the same budget as P's implementation author. The workflow's extra cost, the model author, is reported as cost (measure 4), not hidden.
- Every exchange with an author is logged.

## Hold-outs (Kimi, finding 22)
- The hold-out author (Gemini) receives **the prose arm, the binding and the failure model**, and nothing else.
- **Coverage matrix, fixed before any author starts:** at least two schedules for each of the thirteen BF1 cells. The count, the schedule-to-cell mapping and the schedules' hashes are committed together, before any first version exists.
- The hold-outs run against all three implementations and both models (where a model can express them), and descriptively against `backup.sh`.

## Where findings come from
- (a) Model–implementation divergences on shared schedules: arms F and P only.
- (b) Failures under the injected BF1 cells and the hold-outs: all three implementations.

A finding is **consequential** by construction, because every finding arises from a failed schedule or a divergence.

## Decision tree for each finding (Kimi, findings 19 and 20; fixed here)
1. **Unit.** One root cause per artifact. Failures that trace to one code location, one spec action or one declared reading are one finding. The steward proposes the grouping. Each judge may split or merge it, and that judge's grouping is used for that judge's count.
2. **Is the behaviour a violation of the arm's text?** If not, the finding is *other*.
3. **Is the text itself defective**, contradictory or unsatisfiable? If so, the finding goes to a **separate contract-defect adjudication**, in which the judge receives **both** forms:
   - wrong in both forms: a **contract defect**, reported against the contract;
   - wrong in this arm's text only: an **arm-specific text defect**, reported per arm.

   Neither kind enters the primary count.
4. **Does the arm's text permit the artifact's reading?** If the artifact follows one of two or more readings the text permits, the finding is a **supported-reading divergence**. It is counted separately and is never a misreading.
5. **Is there evidence of what the author read?** That means the artifact's declared reading, a recorded clarifying question, its README, or its spec or code text that states the reading.
   - Evidence of a reading the text does not support: a **misreading**.
   - No such evidence, where the artifact simply does not do what the text says: an **implementation defect**, or a **model defect**.
6. **Attribution:** to the model, the implementation, or both. A divergence can produce one finding on each side.

## Judging (Kimi, finding 21)
- Judges receive the finding, the arm's own text (both forms only in step 3) and the artifact. They are not given the hypothesis, the predictions, other arms' outcomes, or arm labels. **The form of the text cannot be hidden, and this pre-registration says so.**
- **Primary count per arm:** the findings that **both** judges class as misreadings. Each judge's own count is reported beside it.

## Measures (fixed here)
1. **Primary:** the misreadings per arm, as above.
2. Supported-reading divergences, arm-specific text defects and contract defects, per arm (descriptive).
3. Divergence count, arms F and P (descriptive, Kimi, finding 24).
4. **Cost:** author tokens and wall-clock per arm, including P's model author, and the steward's and Tony's attention.
5. **Per named schedule, for each of the three implementations and for `backup.sh`:**
   - *recoverable*: B1.19 holds at the schedule's end;
   - *reported*: every violation the contract requires to be reported was reported within its bound. Under BF1.2, BF1.4, BF1.8 and BF1.14 no bound holds, and "reported by the schedule's end" is used instead.

   These are two booleans per schedule. The denominator is the committed hold-out set plus one injection per BF1 cell (Kimi, finding 26). The `backup.sh` row is descriptive: it was not built to this contract (Kimi, finding 25).
6. Clarifying questions recorded, and declared limitations, per author.

## Predictions and scoring (fixed here; exploratory)
- **W1-1 (form):** arm P's primary count exceeds arm F's by at least 3. **It does not hold** if F's count is at least P's. Otherwise it is **inconclusive**. The threshold has no basis in an earlier measurement, because none exists.
- **W1-3 (cost):** arm F's author tokens exceed arm P's by more than 25 %.
- **W1-5 (workflow):** arm N's implementation is not *recoverable* or not *reported* (measure 5) on at least 3 more schedules than arm P's implementation. **It does not hold** if N fails on no more schedules than P. Otherwise it is **inconclusive**.

## Known limits
- One author per role and arm, so this is exploratory, as stated above.
- The steward wrote both forms. The four-part form had four review rounds of scrutiny, and the prose arm one equivalence review and one check. The claim is narrowed to these two documents.
- The judges' classification is the weakest link. Agreement is required for the primary count.
- Arm N's author is the same family as F's and P's implementation authors. That holds the family constant, and it also means that N measures one family's unassisted practice.

## Not in scope
Which implementation, if any, becomes the service tupay runs is decided after scoring. It is checked against the migration acceptance contract when the move happens.
