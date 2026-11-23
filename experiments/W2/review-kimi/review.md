Blocking defects are present. The strict-inequality predictions are falsifiable on complete, well-formed data, but the draft does not yet guarantee comparable cells or a unique score.

1. **Blocking — `Q` is not a frozen or stable count of questions.**  
   **Where:** “Count Q(family, form)” and the drafters’ CONTRACT QUESTIONS instruction.  
   **What is wrong:** The draft says Q is “**the number of top-level numbered items**” and is “**counted by script**,” but neither the script nor its parsing rules are fixed. The task requires only “**a list headed CONTRACT QUESTIONS**”: it does not require numbering or one atomic issue per item. A bulleted list containing ten questions therefore scores zero; ten questions grouped under one number score one; one issue split into ten numbered items scores ten. Because the steward has already seen the P outputs and no script hash is registered, parsing decisions can also be chosen after seeing the new outputs.  
   **Fix:** Before inspecting any new output, publish and hash the counting script with deterministic rules for bullets, nesting, empty/malformed/partial sections, and duplicates; if Q is intended to measure issues, rerun all cells under a common atomic one-issue-per-item format.

2. **Blocking — W2-2’s grounding and matching rules do not determine `I`.**  
   **Where:** “Matching, by a judge.”  
   **What is wrong:** The judge decides whether text is “**in its list's contract (grounded)**” and which question raises “**the same contract issue**,” but there is no fixed judge prompt, output schema, quote-normalization rule, or operational matching criterion. Nor is matching required to be symmetric or one-to-one. For example, if P1 and P2 both concern the issue raised by F1, many-to-one matching can leave all three matched, while one-to-one matching leaves one P question unmatched; asymmetric judge answers have no reconciliation rule. No-quote, multiple-quote, binding-only quote, and judge-failure cases are also uncovered. These choices can change the sign of `I(P)-I(F)`.  
   **Fix:** Pre-register the complete judge prompt and schema, exact grounding rules, and a symmetric pair-level matching algorithm covering duplicates and many-to-one matches, then compute `I` mechanically from those rulings.

3. **Blocking — Anticipated truncation and missingness can leave either prediction without a registered score.**  
   **Where:** “Truncation rule,” “Predictions,” and “Scoring.”  
   **What is wrong:** A missing cell is “**excluded from W2-1, which then needs both of the remaining families**.” With two incomplete families, fewer than two families remain and that rule is undefined. W2-2 has no missing-cell rule at all, although matching requires both lists and scoring awaits “**the judge's six rulings**.” The draft also does not say whether a normally completed reply without the heading is zero or missing, what happens when a continuation leaves the section present but incomplete, or whether continuation text replaces or is appended to the original section. Declaring “**There is no inconclusive band**” does not resolve these cases.  
   **Fix:** Define family evaluability and every zero-to-three-missing-family case for both predictions, including incomplete continuations and judge failure, using either a fully fixed retry policy or an explicit inconclusive outcome.

4. **Blocking — GLM’s two forms did not receive the same generation opportunities.**  
   **Where:** “Known limits.”  
   **What is wrong:** “**GLM-P was GLM's second attempt (its first returned nothing). GLM-F gets one attempt plus the truncation rule.**” A fresh full generation after an empty response is not equivalent to a section-only continuation: it changes both the chance of obtaining a usable cell and the possible question list. GLM can therefore supply one of the two families needed for W2-1, and contribute to pooled W2-2, through a retry-policy difference rather than a form difference.  
   **Fix:** Give GLM-F the same empty-response full-retry opportunity under a policy applied to every cell, or exclude GLM from both outcomes and register a revised two-family W2-1 rule.

5. **Significant — The continuation protocol and relevant run settings are not fully frozen.**  
   **Where:** “Existing cells,” “Families,” and “Truncation rule.”  
   **What is wrong:** The continuation must use “**the exact words used for Mistral-P**,” but those words are neither reproduced nor hashed, and the assembly of Mistral-P’s original output with `continuation.md` is not specified. Apart from temperature and GLM’s reasoning cap, output budgets and other generation settings are not registered, even though a length stop triggers continuation or exclusion. Thus the draft does not establish equal output opportunities within each P/F pair.  
   **Fix:** Include and hash the continuation prompt and transcript-assembly rule, and pin all per-family generation settings and output budgets for both forms, rerunning or excluding existing cells that do not conform.

6. **Significant — Pooled `I` weights families by question-list granularity, not equally or by distinct issue.**  
   **Where:** “Then **I(form)** … pooled over families” and W2-2.  
   **What is wrong:** Even after matching is made deterministic, a family producing many finely split questions contributes more to `I` than the other families combined; W2-2 can therefore hold while two of three families show the opposite direction. This compounds the atomicity problem in Q and makes “issues” potentially a count of unmatched list entries rather than distinct contract issues.  
   **Fix:** Count distinct issue clusters and aggregate families equally, or register a per-family normalized unmatched measure while retaining raw pooled counts as secondary reporting.

7. **Minor — Final review has no change-control boundary.**  
   **Where:** “A non-steward family reviews the result before it is final.”  
   **What is wrong:** The draft does not say whether this review is limited to arithmetic and artifact verification or may reopen parsing, grounding, or matching after the result is known. The latter would reintroduce post-outcome scoring discretion.  
   **Fix:** Restrict review to checking frozen artifacts and computations, and label any substantive scoring change as a post-registration amendment rather than part of the registered result.