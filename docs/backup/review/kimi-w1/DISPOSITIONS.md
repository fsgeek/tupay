# Dispositions: Kimi's review of the prose arm and W1 draft 2 (2026-11-18)

Reviewer `moonshotai/kimi-k3.1-pro` (OpenRouter; US$0.48; one call, no tools). Packet sha256 prefix `b0f120f2007287cf`; review kept verbatim in `review.md` (sha256 prefix `c10c03004fc331bc`). Kimi takes no other role in W1. Dispositions by the thirteenth steward.

**All 26 findings are accepted.** No finding is rejected.

## Part A: equivalence (findings 1 to 16)
**All accepted. Each is fixed in the prose arm only (`contract-prose-arm-draft-2.md`), by carrying draft 7's substance and quoting its wording where possible.** Draft 7 is not touched.
- 1: T6 and T7c records, including the git inventory, who writes the manifest, and where it is stored.
- 2: here P was *stronger* than F. It is replaced with F's (ref name, object id) wording.
- 3: run-entry times, the writing host on marks, notices naming their clause, and *reaches* defined.
- 4: once every *I*, the daily snapshot as the highest sequence number in its UTC day, and the units.
- 5: "the run" restored as the actor of B1.5, and the stages *no-credentials*, *source* and *capture*.
- 6: "a *failed* run entry appearing".
- 7: the pending *not restore-checked* sentence.
- 8: T26's logged-reason definition, and "within *D* of the comparison".
- 9: the manifest rule applies to every run.
- 10: "rewritten at each update", "at the next run", "under B1.7".
- 11: *overdue*, with the cause categories.
- 12: deadlines are never suspended or restarted, under any cell.
- 13: *H* = *I* + slack, *T* as a floor, and the four cells under which no bound holds.
- 14: T12's clock rule; ±1 h and ±24 h steps, reported.
- 15: the two binding declarations.
- 16: T7a, T7b, T14 and T27 added to the retired list.

**Risk, named:** the backup contract's last four rounds each put their next defect into the steward's own patches. So the prose arm's draft 2 diff is checked once more by an outside family, for these 16 changes only, before registration. This is a check of a patch, not a new review round.

## Part B: W1 (findings 17 to 26)
- **17 (blocking): accepted.** With one author pair per arm, W1 cannot support a causal claim about the form. **W1 is reclassified as an exploratory, descriptive pilot about these documents and these runs.** Its predictions stay registered and are scored as stated, and the result claims nothing general about the form. Whether a replicated study is worth its cost is decided from the pilot.
- **18: accepted.** The claim is narrowed to the two documents. §12's execution examples are content, not form, so they go to **both** arms, in prose for P. The interpretation records stay with F, because they are part of the treatment. The unequal scrutiny the forms received remains a stated limit.
- **19 (blocking): accepted.** Draft 3 pre-registers a decision tree: the unit is one root cause per artifact, with rules for de-duplication, for attribution (model, implementation or both), and for the evidence a misreading needs (the artifact's declared reading, or its code or spec text). Following one of two readings the text permits becomes its own class, **supported-reading divergence**, counted separately and never as a misreading.
- **20: accepted.** Contract-defect claims are adjudicated separately, with both forms given to the judge. A class for a **text defect in one arm only** is added, reported per arm and kept out of the primary count.
- **21 (blocking): accepted.** **Aggregation:** the primary count is the findings that **both** judges class as misreadings, and each judge's own count is reported beside it. Judges are blinded to the hypothesis, the predictions and the other arm's outcomes. The form itself cannot be hidden, and draft 3 says so. W1-2's phrase about the inconclusive region is removed with W1-2 (see 24).
- **22: accepted.** The hold-out author receives the **prose arm, the binding and the failure model**. The coverage matrix is fixed before either arm runs: at least two schedules per BF1 cell, with the count and the mapping committed with the hashes.
- **23: accepted.** Every author has a fresh, isolated session (existing practice: sandbox, fresh home, separate checkout). The arms run concurrently. No clarifying question is answered during a run: authors record the question, state the reading they chose, and go on. That rule is identical for every author. Budgets are the same per role, in wall-clock and turn caps, and every exchange is logged.
- **24: accepted.** W1-2 is withdrawn. The divergence count is reported descriptively.
- **25 (blocking for W1-4): accepted.** `backup.sh` was not built to this contract, so beating it is no evidence for the workflow. **W1-4 is withdrawn, and the `backup.sh` comparison becomes descriptive.** Kimi's fix is adopted instead: **arm N**, an implementation author of the same family (Codex), with the prose arm, the binding and the same budget, and **no workflow**: no formal model, no paired tests, no divergence loop. It writes its own tests, as an engineer would. Arm P against arm N then tests the workflow. Arm F against arm P tests the form. Both comparisons are exploratory, with one author per cell. **This corrects acceptance decision 1**, which named `backup.sh` as the baseline (log, 2026-11-13).
- **26: accepted.** Per named schedule, recoverability (B1.19) and timely required reporting are scored as separate booleans. Excluded detection intervals are stated, and the denominator is fixed.

## The steward's pre-review finding S1 (logged before the review returned; not given to the reviewer)
Draft 7 §8 holds a steward hypothesis ("The steward expects it to raise three things…"), and P has no counterpart. **Disposition:** the author-facing copies of both arms are generated mechanically from their normative sections. The non-normative history preamble, §7 (gaps) and §8 (Arariwa) are left out of both, and the omitted headings are listed in each brief. Draft 7 itself is unchanged. Rule 18's failure is recorded in the practice audit.
