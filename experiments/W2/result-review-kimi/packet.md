You are checking an experiment's result file against its frozen artifacts. Your scope is limited by the registration: check that every number in the result follows from the artifacts below by the stated rules, that the registered result and the amended result are each computed as their rules say, and that no claim in the result goes beyond the numbers. Do not propose new scoring rules. Report numbered findings (severity: blocking / significant / minor; where; what; why), or say that you found none.

===== RESULT FILE =====
# W2 result: a census of ambiguity in contract v1's two forms (DRAFT, before the result review)

The fourteenth steward, 2026-11-23. Registration: `experiments/W2-prereg.md` (commit `19105b1`). Amendments A1 and A2, each informed by an outcome, are logged with their hashes (log, 2026-11-23). **The registered result comes first. The amended result is beside it, labelled.** Exploratory: one sample per cell.

## Counts: contract questions per cell
| Family | Q(P) | Q(F), registered (v1) | Q(F), amended (v3) | Note |
|---|---|---|---|---|
| GLM | 8 | **0** | 8 | v1 missed the heading `## F. CONTRACT QUESTIONS` and counted a continuation that was not needed (A1) |
| StepFun | 10 | **0** | 8 | v1 took an overview list item at line 15 as the heading (A2) |
| Mistral | 28 | 10 | 10 | — |

Q(P) is the same under v1 and v3 in every family. Every cell is complete, and all three families are evaluable for both predictions.

## Matching (judge: Cohere `command-a-plus`; one call each; all parsed on the first attempt)
| Family | Pipeline | n(F) | n(P) | grounded F / P | matched pairs | I(F) | I(P) |
|---|---|---|---|---|---|---|---|
| GLM | registered | 0 | 8 | 0 / 8 | 0 | 0 | 8 |
| GLM | amended | 8 | 8 | 8 / 8 | 2 | 6 | 6 |
| StepFun | registered | 0 | 10 | 0 / 10 | 0 | 0 | 10 |
| StepFun | amended | 8 | 10 | 8 / 10 | 3 | 5 | 8 |
| Mistral | registered | 10 | 28 | 10 / 28 | 3 | 7 | 25 |
| Mistral | amended | 10 | 28 | 10 / 28 | 5 | 6 | 23 |

**Judge variance, measured:** Mistral's two judge packets are byte-identical (sha256 prefix `421b77847123b063`), and the two rulings differ: 3 against 5 matched pairs, I(P) 25 against 23, and I(F) 7 against 6. The judge is not deterministic at temperature 0. A single ruling per family therefore carries noise of a few items. This was not anticipated in the registration, and it is reported here as observed.

## Predictions
| Prediction | Steward's probability | Registered result | Amended result |
|---|---|---|---|
| **W2-1** Q(F) < Q(P) in a majority of evaluable families | 0.40 | **Holds** (3 of 3; two of the three on artifacts) | **Holds** (2 of 3: StepFun 8 < 10, Mistral 10 < 28; GLM ties at 8) |
| **W2-2** Σ I(P) > Σ I(F) | 0.50 | **Holds** (43 against 7) | **Holds** (37 against 17) |

Per family, amended I(P) − I(F): GLM 0, StepFun +3, Mistral +17. The pooled result rests mostly on Mistral, which is review finding 6, registered as a known limit.

## What it says, and what it does not
- **In this census, readers trying to build tests from the four-part form listed fewer open contract questions than readers working from prose, or the same number.** No family listed more on F. The issues they raised overlapped little across forms (2 to 5 matched pairs per family). The two forms provoke largely different questions, not one set at different rates.
- This is the direction of the idea behind W1-1, Karpathy's: a controlled form leaves less open. The steward predicted against it for W2-1 (0.40). **The steward's forecast was wrong in direction.**
- It is weak evidence. There is one sample per cell, and family-to-family variation is large (Q(P) from 8 to 28). One family ties, and one family (Mistral) carries most of the pooled difference. The judge varies on identical input. Questions listed are not misreadings: W2 says nothing about how authors would build from either form.
- **Two of the registered counts are artifacts of the steward's script.** The registered result holds for the right sign partly for the wrong reason. The amended result removes the artifacts and still holds, by a smaller margin.

## Cost
Cells: GLM-F US$0.08 (with an unneeded continuation), Mistral-F US$0.09, StepFun-P US$0.07, StepFun-F US$0.07. Judge: six calls, US$0.09 in all. The review of draft 1: US$0.18. **W2 total: US$0.57**, summed from every response file under `experiments/W2/`. The earlier P cells' cost was counted under W1 A2.

## Evidence
`experiments/W2/` (cells, both judges' packets, responses and summaries; `review-kimi/`), `experiments/W1/interface/{glm,mistral}/` (the P cells), and `scripts/steward/w2-*.py` (registered and amended versions).


===== REGISTRATION =====
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


===== experiments/W2/glm-F/cell.json =====
{
 "model": "z-ai/glm-5.3-prime",
 "form": "F",
 "packet_sha256": "e586a68ca66efcd9e60badcd711e661d080a4df29f50b5c39f4febbb729af388",
 "calls": [
  [
   "first",
   "stop",
   27142,
   0.05287608
  ],
  [
   "continuation",
   "stop",
   8216,
   0.026126592
  ]
 ],
 "status": "complete",
 "q": 0
}

===== experiments/W2/mistral-F/cell.json =====
{
 "model": "mistralai/mistral-large-4-0",
 "form": "F",
 "packet_sha256": "e586a68ca66efcd9e60badcd711e661d080a4df29f50b5c39f4febbb729af388",
 "calls": [
  [
   "first",
   "stop",
   37525,
   0.0868721
  ]
 ],
 "status": "complete",
 "q": 10
}

===== experiments/W2/stepfun-F/cell.json =====
{
 "model": "stepfun/step-5-preview",
 "form": "F",
 "packet_sha256": "e586a68ca66efcd9e60badcd711e661d080a4df29f50b5c39f4febbb729af388",
 "calls": [
  [
   "first",
   "stop",
   23952,
   0.069617
  ]
 ],
 "status": "complete",
 "q": 0
}

===== experiments/W2/stepfun-P/cell.json =====
{
 "model": "stepfun/step-5-preview",
 "form": "P",
 "packet_sha256": "30ac673b5207011073706abe00568e69b715e3630eb84cab59d095a2649a658a",
 "calls": [
  [
   "first",
   "stop",
   27335,
   0.0698745
  ]
 ],
 "status": "complete",
 "q": 10
}

===== experiments/W2/judge-v3/glm/summary.json =====
{
 "family": "glm",
 "status": "ok",
 "list1": "F",
 "n": {
  "F": 8,
  "P": 8
 },
 "grounded": {
  "F": 8,
  "P": 8
 },
 "matched_pairs": 2,
 "I": {
  "F": 6,
  "P": 6
 }
}

===== experiments/W2/judge-v3/mistral/summary.json =====
{
 "family": "mistral",
 "status": "ok",
 "list1": "P",
 "n": {
  "P": 28,
  "F": 10
 },
 "grounded": {
  "P": 28,
  "F": 10
 },
 "matched_pairs": 5,
 "I": {
  "P": 23,
  "F": 6
 }
}

===== experiments/W2/judge-v3/stepfun/summary.json =====
{
 "family": "stepfun",
 "status": "ok",
 "list1": "F",
 "n": {
  "F": 8,
  "P": 10
 },
 "grounded": {
  "F": 8,
  "P": 10
 },
 "matched_pairs": 3,
 "I": {
  "F": 5,
  "P": 8
 }
}

===== experiments/W2/judge/glm/summary.json =====
{
 "family": "glm",
 "status": "ok",
 "list1": "F",
 "n": {
  "F": 0,
  "P": 8
 },
 "grounded": {
  "F": 0,
  "P": 8
 },
 "matched_pairs": 0,
 "I": {
  "F": 0,
  "P": 8
 }
}

===== experiments/W2/judge/mistral/summary.json =====
{
 "family": "mistral",
 "status": "ok",
 "list1": "P",
 "n": {
  "P": 28,
  "F": 10
 },
 "grounded": {
  "P": 28,
  "F": 10
 },
 "matched_pairs": 3,
 "I": {
  "P": 25,
  "F": 7
 }
}

===== experiments/W2/judge/stepfun/summary.json =====
{
 "family": "stepfun",
 "status": "ok",
 "list1": "F",
 "n": {
  "F": 0,
  "P": 10
 },
 "grounded": {
  "F": 0,
  "P": 10
 },
 "matched_pairs": 0,
 "I": {
  "F": 0,
  "P": 10
 }
}

===== w2-count.py on GLM-P (experiments/W1/interface/glm) =====
{"status": "complete", "q": 8, "items": ["1. **B1.16 / BF1.7 \u2014 where does the checker \"read\" held notices?** \"the sender k", "2. **B1.7 \u2014 \"B1.19 being violated\" as a trigger.** B1.19 is a state (\"there is a", "3. **B1.8 \u2014 the start of *M*.** \"within *M* of its *ok* entry\" \u2014 the ok entry's ", "4. **B1.18 \u2014 \"both copies are intact but disagree.\"** Disagree *about what*? The", "5. **B1.4 \u2014 \"the first daily snapshot of each month for *Mo* months.\"** With clo", "6. **B1.15 \u2014 *Q* \"measured on the binding's own history.\"** The comparison basel", "7. **BF1.10 \u2014 \"R is reimaged or replaced.\"** Does the *status record's* R copy s", "8. **B1.9 \u2014 the interval's starting event.** \"over an interval of *I* + *X*\" sta"], "source": "draft.md"}


===== w2-count-v3.py on GLM-P (experiments/W1/interface/glm) =====
{"status": "complete", "q": 8, "items": ["1. **B1.16 / BF1.7 \u2014 where does the checker \"read\" held notices?** \"the sender k", "2. **B1.7 \u2014 \"B1.19 being violated\" as a trigger.** B1.19 is a state (\"there is a", "3. **B1.8 \u2014 the start of *M*.** \"within *M* of its *ok* entry\" \u2014 the ok entry's ", "4. **B1.18 \u2014 \"both copies are intact but disagree.\"** Disagree *about what*? The", "5. **B1.4 \u2014 \"the first daily snapshot of each month for *Mo* months.\"** With clo", "6. **B1.15 \u2014 *Q* \"measured on the binding's own history.\"** The comparison basel", "7. **BF1.10 \u2014 \"R is reimaged or replaced.\"** Does the *status record's* R copy s", "8. **B1.9 \u2014 the interval's starting event.** \"over an interval of *I* + *X*\" sta"], "source": "draft.md", "note": null}


===== w2-count.py on Mistral-P (experiments/W1/interface/mistral) =====
{"status": "complete", "q": 28, "items": ["1. **Who records a run that ends without a final entry.** B1.6 says: \"When a run", "2. **Whether a run may write marks.** B1.13 says: \"Every run, and every pass of ", "3. **Which copy \"the record\" is in B1.13.** B1.13 says the comparison is against", "4. **What \"protected\" means during a both-copies-lost rebuild.** B1.18 says: \"if", "5. **Where a corrupt copy is \"kept aside\".** B1.18 says: \"A copy whose hash fail", "6. **What notice a record disagreement sends.** B1.18 says: \"if both copies are ", "7. **The \"starting event\" for a B1.19 violation.** The Deadlines paragraph says:", "8. **When B1.19 becomes active.** B1.19 says: \"After the first G of operation, t", "9. **Which clock measures cross-host deadlines.** The contract says: \"Every age ", "10. **Whose clock judges \"younger than G\" at the scoring horizon.** B1.19 requir", "11. **What quantity Q applies to in B1.15.** B1.15 says: \"A run compares each re", "12. **The format of a logged reason.** The contract says: \"A logged reason is an", "13. **How a failed daily check is recorded.** B1.11 says: \"After that date the d", "14. **Where undelivered notices are kept.** B1.16 says: \"While the channel canno", "15. **Whether a partitioned host can still reach the notice channel.** BF1.2 say", "16. **The scope of BF1.3.** BF1.3 says: \"Stored bytes at R are silently corrupte", "17. **The scope of BF1.12.** BF1.12 says: \"Some snapshots at R are lost by somet", "18. **The degree of BF1.4.** BF1.4 says: \"A disk on R or S fills.\" It does not s", "19. **Where a BF1.6 clock-step error is \"reported\".** BF1.6 says: \"The tests inj", "20. **Which host prunes, and on which clock \"younger than T\" is measured.** B1.4", "21. **How \"being rebuilt\" is observable.** B1.4 says: \"It removes nothing while ", "22. **What interval B1.9 quantifies over.** B1.9 says: \"Suppose that, over an in", "23. **What \"since\" means in B1.3/B1.4/B1.19.** B1.3 says: \"A protected snapshot ", "24. **What \"new commits\" means for the B1.5 scan.** B1.5 says: \"Each run scans t", "25. **Who deletes a path that becomes \"gone\".** B1.17 says: \"The manifest holds ", "26. **Whether the staleness notice lapses when a newer snapshot is acknowledged.", "27. **Whether the initial verification counts as the \"previous verification\".** ", "28. **Whether the B1.19 cause list is exhaustive.** B1.19 says: \"When no such sn"], "source": "continuation.md"}


===== w2-count-v3.py on Mistral-P (experiments/W1/interface/mistral) =====
{"status": "complete", "q": 28, "items": ["1. **Who records a run that ends without a final entry.** B1.6 says: \"When a run", "2. **Whether a run may write marks.** B1.13 says: \"Every run, and every pass of ", "3. **Which copy \"the record\" is in B1.13.** B1.13 says the comparison is against", "4. **What \"protected\" means during a both-copies-lost rebuild.** B1.18 says: \"if", "5. **Where a corrupt copy is \"kept aside\".** B1.18 says: \"A copy whose hash fail", "6. **What notice a record disagreement sends.** B1.18 says: \"if both copies are ", "7. **The \"starting event\" for a B1.19 violation.** The Deadlines paragraph says:", "8. **When B1.19 becomes active.** B1.19 says: \"After the first G of operation, t", "9. **Which clock measures cross-host deadlines.** The contract says: \"Every age ", "10. **Whose clock judges \"younger than G\" at the scoring horizon.** B1.19 requir", "11. **What quantity Q applies to in B1.15.** B1.15 says: \"A run compares each re", "12. **The format of a logged reason.** The contract says: \"A logged reason is an", "13. **How a failed daily check is recorded.** B1.11 says: \"After that date the d", "14. **Where undelivered notices are kept.** B1.16 says: \"While the channel canno", "15. **Whether a partitioned host can still reach the notice channel.** BF1.2 say", "16. **The scope of BF1.3.** BF1.3 says: \"Stored bytes at R are silently corrupte", "17. **The scope of BF1.12.** BF1.12 says: \"Some snapshots at R are lost by somet", "18. **The degree of BF1.4.** BF1.4 says: \"A disk on R or S fills.\" It does not s", "19. **Where a BF1.6 clock-step error is \"reported\".** BF1.6 says: \"The tests inj", "20. **Which host prunes, and on which clock \"younger than T\" is measured.** B1.4", "21. **How \"being rebuilt\" is observable.** B1.4 says: \"It removes nothing while ", "22. **What interval B1.9 quantifies over.** B1.9 says: \"Suppose that, over an in", "23. **What \"since\" means in B1.3/B1.4/B1.19.** B1.3 says: \"A protected snapshot ", "24. **What \"new commits\" means for the B1.5 scan.** B1.5 says: \"Each run scans t", "25. **Who deletes a path that becomes \"gone\".** B1.17 says: \"The manifest holds ", "26. **Whether the staleness notice lapses when a newer snapshot is acknowledged.", "27. **Whether the initial verification counts as the \"previous verification\".** ", "28. **Whether the B1.19 cause list is exhaustive.** B1.19 says: \"When no such sn"], "source": "continuation.md", "note": null}


===== w2-count.py on glm-F =====
{"status": "complete", "q": 0, "items": [], "source": "continuation.md"}


===== w2-count-v3.py on glm-F =====
{"status": "complete", "q": 8, "items": ["1. **\"Verified\" (T8) is unobservable from outside.** T8: *\"Verified: an event. A", "2. **B1.7's notice content for \"overdue\" reports.** B1.7/B1.19: the checker repo", "3. **What \"the notice channel is unavailable\" means when the record is on S (BF1", "4. **BF1.8 (\"a timer does not fire\") vs. B1.3's clock freeze.** The interface im", "5. **T5a's \"highest snapshot name at R\" under BF1.10.** After R is reimaged (BF1", "6. **B1.15's *Q* \"measured on the binding's own history.\"** The binding gives Q=", "7. **B1.18's \"hash over its entries.\"** The interface corrupts the record file b", "8. **\"At least every *D*\" (T23) vs. B1.7's \"within *D*.\"** The checker runs at l"], "source": "draft.md", "note": "continuation-unneeded"}


===== w2-count.py on stepfun-F =====
{"status": "complete", "q": 0, "items": [], "source": "draft.md"}


===== w2-count-v3.py on stepfun-F =====
{"status": "complete", "q": 8, "items": ["1. **Status-record entry schema (T15).**  ", "2. **Notice clause naming (T16).**  ", "3. **Status-record hash algorithm (B1.18).**  ", "4. **Location of the record while the channel is down (B1.16).**  ", "5. **Both status-record copies lost (T5a).**  ", "6. **Partition scope for the freshness checker (BF1.2).**  ", "7. **Observable rebuild state (B1.4 / B1.18).**  ", "8. **Restorability evidence for the test (T11).**  "], "source": "draft.md", "note": null}


===== w2-count.py on stepfun-P =====
{"status": "complete", "q": 10, "items": ["1. **B1.8 cleanup scope.**  ", "2. **B1.16 queue location.**  ", "3. **B1.18 merge semantics.**  ", "4. **B1.19 evidence standard.**  ", "5. **BF1.6 error reporting channel.**  ", "6. **B1.4 monthly retention edge case.**  ", "7. **B1.5 detector interface.**  ", "8. **B1.15 logged-reason location.**  ", "9. **EX1.6 / binding channel dependency.**  ", "10. **B1.12 re-verification observability.**  "], "source": "draft.md"}


===== w2-count-v3.py on stepfun-P =====
{"status": "complete", "q": 10, "items": ["1. **B1.8 cleanup scope.**  ", "2. **B1.16 queue location.**  ", "3. **B1.18 merge semantics.**  ", "4. **B1.19 evidence standard.**  ", "5. **BF1.6 error reporting channel.**  ", "6. **B1.4 monthly retention edge case.**  ", "7. **B1.5 detector interface.**  ", "8. **B1.15 logged-reason location.**  ", "9. **EX1.6 / binding channel dependency.**  ", "10. **B1.12 re-verification observability.**  "], "source": "draft.md", "note": null}


===== w2-count.py on mistral-F =====
{"status": "complete", "q": 10, "items": ["1. **Which timers BF1.8 covers.**  ", "2. **What \"any stage\" means in BF1.1.**  ", "3. **Whether a suspended host's clock advances.**  ", "4. **Where undelivered notices are recorded under B1.16.**  ", "5. **BF1.7 versus a notice-channel record on S.**  ", "6. **What exactly the B1.18 status-record hash covers.**  ", "7. **What B1.15's `Q` is a fraction of.**  ", "8. **When \"operation\" starts for B1.19.**  ", "9. **What BF1.10 destroys besides snapshots.**  ", "10. **What \"full disk\" means for BF1.4.**  "], "source": "draft.md"}


===== w2-count-v3.py on mistral-F =====
{"status": "complete", "q": 10, "items": ["1. **Which timers BF1.8 covers.**  ", "2. **What \"any stage\" means in BF1.1.**  ", "3. **Whether a suspended host's clock advances.**  ", "4. **Where undelivered notices are recorded under B1.16.**  ", "5. **BF1.7 versus a notice-channel record on S.**  ", "6. **What exactly the B1.18 status-record hash covers.**  ", "7. **What B1.15's `Q` is a fraction of.**  ", "8. **When \"operation\" starts for B1.19.**  ", "9. **What BF1.10 destroys besides snapshots.**  ", "10. **What \"full disk\" means for BF1.4.**  "], "source": "draft.md", "note": null}
