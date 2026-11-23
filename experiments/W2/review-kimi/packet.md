You are an outside reviewer of a pre-registration that has not yet been registered. Read it adversarially. Kinds of defect to look for, not suspicions: a prediction that cannot fail, or that the design makes likely whatever the truth; a measure whose count can be steered after outcomes are seen; a confound that makes the two forms' cells not comparable; a scoring rule that is ambiguous or incomplete; a missing rule for a case that will plausibly occur. Report numbered findings, each with severity (blocking / significant / minor), where, what is wrong, why (quote the text), and a one-line fix. Blocking means: the experiment cannot be scored fairly unless it is fixed. If you find nothing blocking, say so.

===== THE PRE-REGISTRATION DRAFT =====
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


===== THE DRAFTERS' TASK TEXT (sent unchanged to every cell, followed by one contract form and the binding) =====
You are designing a shared test interface for a backup service. The contract and failure model below are fixed; do not change them, and do not design the service itself.

Several independent teams will each build an implementation of this contract, and some will also write a formal model (for example in TLA+). One test suite of "schedules" must run, unchanged, against every implementation and every model. A schedule is a scripted scenario: what happens to the sources, which failure-model cells (BF1.x) are injected and when, and what must be observed. Your interface is the only thing the teams share besides the contract, so whatever it leaves unspecified, each team will decide differently.

The interface must make the following possible:
1. Time. The contract's parameters are hours and days (see the binding's values). A schedule covering several weeks must run in minutes. Say how time is given to an implementation, and how clock steps on one host are expressed (the contract measures ages on each host's own clock).
2. Hosts and roles. Every role the contract names (source host, store, restore host, freshness checker, notice channel) must exist in a test, on one machine, without root. Say what each is in a test and how an implementation is told where it is.
3. Fault injection. Every BF1 cell in the failure model must be injectable by the test harness, without the implementation's cooperation beyond what the interface requires. For each cell, say how it is injected and how it ends.
4. Observation. Everything a schedule's assertions need must be observable from outside the implementation: in particular, the notice channel's record (which clause a notice names, and when it arrived), snapshot marks, and whether a snapshot is recoverable. Say what is recorded, where, and in what format.
5. Assertions. Every assertion in a schedule carries a tag naming the contract clause it checks, written `derives: B1.x` (or the id it checks). Each schedule states a fixed scoring horizon: a fixed time after its last injected event, at which recoverability is judged.
6. Models. The same schedule text must be readable by a formal model's own schedule runner. Say which parts of a schedule a model must accept, and how a model reports that it cannot express a schedule.
7. Prescription. The contract prescribes no protocol and no tooling. Your interface must not prescribe any either, beyond what injection and observation strictly need. Where you must constrain an implementation (for example, to read time from the harness), say so, and say why the constraint is needed.

Write the interface as a specification another engineer could implement a harness from, with:
- a schedule format (grammar or schema, with one complete example schedule that injects at least two cells);
- the implementation-side contract (what an implementation must expose or obey, and nothing more);
- the harness's obligations;
- a list headed OPEN CHOICES: every point where the contract or binding leaves the interface's design open and you chose one option. For each, give the options you saw and why you chose yours.
- a list headed CONTRACT QUESTIONS: any place where you could not design injection or observation because the contract itself is unclear. Quote the text. Do not resolve these yourself.
Be concrete and complete rather than brief.