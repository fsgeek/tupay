# W2: a census of ambiguity in contract v1's two forms (PRE-REGISTRATION, draft 1)

The fourteenth steward, 2026-11-23. **Not registered until the log says so.** Ids are never reused.

## Why
W1 asks whether the four-part form (arm F) leads to fewer misreadings than prose (arm P). That idea, of reducing specification ambiguity with a controlled language, was Andrej Karpathy's, and Tony brought it to tupay. W1's launch is suspended (log, 2026-11-23): the first attempt to derive a shared test interface from the prose arm raised 36 contract questions, and an outside check found the contract untestable as written. Those questions were raised as a by-product of a fixed task, by readers who did not know the hypothesis. **W2 runs the same task on the other form.** It is a cheap, partial test of W1-1's idea. It measures the open questions an independent reader finds when it tries to build tests, not the misreadings of an author building a service.

## Design
- **Task:** the text of `scripts/steward/w1-interface-draft.py` (task string unchanged since commit 9de78d2, the first drafting run): design a shared test interface, and list OPEN CHOICES and CONTRACT QUESTIONS. The packet differs between forms **only** in the contract file: `experiments/W1/inputs/contract-P.md` (form P) or `experiments/W1/inputs/contract-F.md` (form F). Both are the registered author copies (hashes in `omitted.json`). The binding is binding v1 in both.
- **Families (cells):** GLM (`z-ai/glm-5.3-prime`, reasoning capped at 24k tokens, as in its P run), Mistral (`mistralai/mistral-large-4-0`) and StepFun (`stepfun/step-5-preview`), each run once per form, at temperature 0. No family here has a role in W1.
- **Existing cells, used as they are:** GLM-P (`experiments/W1/interface/glm/`) and Mistral-P (`experiments/W1/interface/mistral/`, with its CONTRACT QUESTIONS from `continuation.md`). **New cells:** GLM-F, Mistral-F, StepFun-P and StepFun-F, in `experiments/W2/<family>-<form>/`.
- **Truncation rule (fixed now, the same for every cell):** if a reply ends before its CONTRACT QUESTIONS section is complete (a transport error, or a length stop), one continuation is asked for that section alone, in the exact words used for Mistral-P. If the section is still missing, the cell is reported as *missing* and is excluded from W2-1, which then needs both of the remaining families.
- **Count Q(family, form):** the number of top-level numbered items under the heading CONTRACT QUESTIONS. It is counted by script, and no item is merged or split by the steward.
- **Matching, by a judge:** **Cohere** (`cohere/command-a-plus`; no role in W1 or W2). For each family, the judge gets the two question lists, labelled *List 1* and *List 2* with the assignment to forms fixed by a coin committed here (**List 1 = F for GLM and StepFun, P for Mistral**), and both contract texts, also labelled by number. For every question it states: (a) whether the quoted text is in its list's contract (*grounded*), and (b) which question in the other list raises the same contract issue, or none. Then **I(form)** = grounded questions on that form with no match on the other, pooled over families.

## Predictions (fixed here; exploratory; informed by the P outcomes already seen: GLM-P 8, Mistral-P 28)
- **W2-1 (count, Karpathy's direction):** Q(F) < Q(P) for at least 2 of the 3 families. **Steward's probability: 0.40.** Reason, stated first: F is longer and more explicit, so it offers more text to question, and its interpretation records mark unresolved assumptions (*U*) that a reader may raise as questions. Its defined terms and the class rule may close others.
- **W2-2 (issues):** I(P) > I(F). **Steward's probability: 0.50.**
- Each is scored *holds* or *does not hold*. There is no inconclusive band, because both are counts compared once.

## Known limits
- One sample per cell, at temperature 0. Family-to-family variation is large (8 against 28 on P), so W2 can show only a consistent direction, not a size.
- Questions a reader raises are not misreadings. A form can raise more questions because it says more.
- Form F carries interpretation records, which are part of the treatment and are kept.
- The P cells ran before this registration, and the steward has read them. Only the new cells are blind to the steward's expectations, and the drafters never see the hypothesis.
- GLM-P was GLM's second attempt (its first returned nothing). GLM-F gets one attempt plus the truncation rule.
- Matching is one judge's reading. Its rulings are kept verbatim.

## Scoring
After all four new cells and the judge's six rulings are in, and nowhere else. The result file reports the six counts, the matching tables, W2-1 and W2-2 as registered, and the cost. A non-steward family reviews the result before it is final.
