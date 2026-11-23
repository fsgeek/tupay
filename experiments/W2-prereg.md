# W2: a census of ambiguity in contract v1's two forms (PRE-REGISTRATION)

The fourteenth steward, 2026-11-23. Draft 1 (`W2-prereg-draft-1.md`) had one outside review (Kimi, `experiments/W2/review-kimi/review.md`, US$0.18): 4 blocking, 2 significant, 1 minor. **Under the stop rule, only the blocking items are fixed here (marked [K1] to [K4]), and the rest are registered as known limits, with no further check.** This file is registered by the commit that the log names. Ids are never reused.

## Why
W1 asks whether the four-part form (arm F) leads to fewer misreadings than prose (arm P). That idea, of reducing specification ambiguity with a controlled language, was Andrej Karpathy's, and Tony brought it to tupay. W1's launch is suspended (log, 2026-11-23): the first attempt to derive a shared test interface from the prose arm raised 36 contract questions, and an outside check found the contract untestable as written. Those questions were raised as a by-product of a fixed task, by readers who did not know the hypothesis. **W2 runs the same task on the other form.** It is a cheap, partial test of W1-1's idea. It measures the open questions an independent reader lists when it tries to build tests, not the misreadings of an author building a service.

## Design
- **Task and packet:** built by `scripts/steward/w2-cell.py`, which takes the task string verbatim from `scripts/steward/w1-interface-draft.py` (unchanged since 9de78d2) and the packet layout from it. The forms differ **only** in the contract file, `experiments/W1/inputs/contract-P.md` or `contract-F.md` (the registered author copies; hashes in `omitted.json`), and therefore in that file's name in one heading line. The binding is binding v1 in both.
- **Families:** GLM (`z-ai/glm-5.3-prime`, reasoning capped at 24k tokens), Mistral (`mistralai/mistral-large-4-0`) and StepFun (`stepfun/step-5-preview`). Every call uses temperature 0 and no output limit. No family here has a role in W1.
- **Existing cells, used as they are:** GLM-P (`experiments/W1/interface/glm/`, run with the 24k cap) and Mistral-P (`experiments/W1/interface/mistral/`, with its section from `continuation.md`). **New cells:** GLM-F, Mistral-F, StepFun-P and StepFun-F, in `experiments/W2/<family>-<form>/`.
- **One retry policy for every cell [K4, K3]**, as `w2-cell.py` implements it and as the existing cells received it:
  1. one call;
  2. if the reply's content is empty, one full rerun of the identical request (GLM-P's first attempt was empty and its rerun is the cell; GLM's first attempt ran without the cap, and every new GLM call has it);
  3. if no CONTRACT QUESTIONS section is then found, one continuation, in the fixed words in `w2-cell.py` (`CONT`, the words sent for Mistral-P), with the section read from the continuation;
  4. nothing further. A cell still without a section is **missing**.
- **Count Q(family, form) [K1]:** by `scripts/steward/w2-count.py`, whose rules are in its header and whose hash is committed with this registration. Q counts the top-level list items under the CONTRACT QUESTIONS heading, numbered or bulleted, at column 0. It counts list items as the drafter wrote them, not issues. On the existing cells it gives GLM-P 8 and Mistral-P 28.
- **Matching [K2]:** by `scripts/steward/w2-judge.py`, with its prompt, schema, retry and algorithm in the script and its hash committed. The judge is **Cohere** (`cohere/command-a-plus`), with no role in W1 or W2, one family per call. The lists are labelled List 1 and List 2, by an assignment fixed here (**List 1 = F for GLM and StepFun; List 1 = P for Mistral**), and the contracts likewise. For every item, the judge states *grounded* (true or false) and its *matches* in the other list. A pair counts as matched if either side names it (symmetric union). **I(family, form)** = grounded items on that form that are in no matched pair. If two attempts both fail the schema, the family is **judge-failed**.

## Evaluability [K3]
- A family is **evaluable for W2-1** if both of its cells are complete (neither is missing).
- A family is **evaluable for W2-2** if it is evaluable for W2-1 and its judge ruling is ok.
- **W2-1 holds** if Q(F) < Q(P) in more than half of the families evaluable for it, and at least 2 families are evaluable. It **does not hold** if at least 2 are evaluable and the condition fails. **With fewer than 2 evaluable, it is inconclusive.**
- **W2-2 holds** if the sum over families evaluable for it of I(family, P) exceeds the sum of I(family, F), with at least 2 evaluable. It **does not hold** if at least 2 are evaluable and the condition fails. **With fewer than 2, it is inconclusive.**

## Predictions (fixed here; exploratory; informed by the P outcomes already seen: GLM-P 8, Mistral-P 28)
- **W2-1 (count, Karpathy's direction):** as above. **Steward's probability: 0.40.** Reason, stated first: F is longer and more explicit, so it offers more text to question, and its interpretation records mark unresolved assumptions (*U*) that a reader may raise as questions. Its defined terms and the class rule may close others.
- **W2-2 (unmatched issues):** as above. **Steward's probability: 0.50.**

## Known limits
- One sample per cell, at temperature 0. Family-to-family variation is large (8 against 28 on P), so W2 can show only a consistent direction, not a size.
- Questions a reader raises are not misreadings. A form can raise more questions because it says more. Q counts list items as written, so granularity is the drafter's (review finding 1's atomicity point, accepted as a limit).
- Form F carries interpretation records, which are part of the treatment and are kept.
- The P cells ran before this registration, and the steward has read them. Only the new cells are blind to the steward's expectations, and the drafters never see the hypothesis.
- **Review finding 5 (significant):** the continuation's words name Mistral-P's section numbers. They are used unchanged for every cell. Output limits are each provider's defaults, the same for both forms of a family.
- **Review finding 6 (significant):** pooled I weights a family by how finely it splits its list. Per-family I is reported beside the pooled sum, as secondary.
- **Review finding 7 (minor):** the review of the result checks the frozen artifacts and the arithmetic only. A substantive change to scoring after outcomes would be a post-registration amendment, labelled as such, never part of the registered result.
- Matching is one judge's reading. Its rulings are kept verbatim.

## Scoring
After all four new cells and the three judge rulings are in, and nowhere else. The result file reports the six counts, the matching tables, per-family and pooled I, W2-1 and W2-2 as registered above, and the cost.
