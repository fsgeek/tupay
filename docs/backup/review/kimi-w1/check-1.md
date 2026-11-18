For findings 1–26, the severity shown is the **original** severity; “resolved” means no residual defect on that finding. For partly resolved findings, the severity describes the residual problem.

## 1. Findings 1–16: ARM P changes

**1 — Resolved | significant.**  
**Where:** ARM P, “Parties and terms.”  
**What/why:** The snapshot and manifest requirements now include the sequence-number name, complete inventory, writer and storage location: “Each snapshot is stored at R and **named by its sequence number**. The run writes the snapshot's **manifest**, which lists every file in the snapshot with its sha256 together with the run's source inventory, and stores it with the snapshot.” The inventory definition also carries the git `(ref name, object id)` pairs.  
**Fix:** None.

**2 — Resolved | minor.**  
**Where:** ARM P, B1.2.  
**What/why:** The over-strong exact-object-set wording is gone. P now follows F: “A git repository in a snapshot is bundled from the inventory's (ref name, object id) pairs, never from names resolved later, so its refs are exactly those pairs.” This constrains the source object ids and resulting refs without forbidding additional reachable historical objects.  
**Fix:** None.

**3 — Resolved | significant.**  
**Where:** ARM P, “Parties and terms,” status-record and notice definitions.  
**What/why:** Run entries now contain “sequence number; started, ok or failed; … and times,” and marks contain “sequence number; …; time; and the host that wrote it.” A notice now “names the clause requiring it,” and “**reaches** the channel when the channel's own record holds it.” Those are the missing T15/T16 fields and delivery test.  
**Fix:** None.

**4 — Resolved | significant.**  
**Where:** ARM P, “Parties and terms.”  
**What/why:** P now says: “A day is 24 hours, and a month is a UTC calendar month”; “A **daily snapshot** is the acknowledged snapshot with the highest sequence number in its UTC day”; and “The **daily check** runs on S once every *I*.” This supplies the cadence, UTC-day selection and calendar-month rule.  
**Fix:** None.

**5 — Resolved | minor.**  
**Where:** ARM P, B1.5, B1.15 and B1.17.  
**What/why:** The actor and prescribed stages are restored: “**The run** never writes a credential file…”; a detector hit “fails the run at stage *no-credentials*”; an unreadable tree “fails the run at stage *source*”; and an uncapturable path “fails the run at stage *capture*, and the snapshot is not acknowledged.”  
**Fix:** None.

**6 — Resolved | significant.**  
**Where:** ARM P, B1.7.  
**What/why:** The checker trigger is now “a *failed* run entry appearing,” rather than the actual failure time. The run’s own notice is also “within *D* of failing.” The two clocks now match F.  
**Fix:** None.

**7 — Resolved | minor.**  
**Where:** ARM P, B1.8.  
**What/why:** P now expressly requires the pending state: “Until a check completes, the record shows *not restore-checked*, which is a state and not a discharge of this clause.”  
**Fix:** None.

**8 — Resolved | significant.**  
**Where:** ARM P, “Parties and terms” and B1.15.  
**What/why:** A logged reason is now “an entry in the record the binding names, written before the run, that names the source tree and the change.” B1.15 requires the notice “within *D* of the comparison.” This prevents retrospective or generic reasons and preserves the deadline’s start event.  
**Fix:** None.

**9 — Resolved | minor.**  
**Where:** ARM P, B1.17.  
**What/why:** The acknowledged-snapshot qualifier is gone: “**The manifest** holds every path in the run's source inventory, or lists it as *gone*….” B1.1’s separate acknowledgement gate remains intact.  
**Fix:** None.

**10 — Resolved | significant.**  
**Where:** ARM P, B1.18.  
**What/why:** All three missing obligations are present: each hash is “rewritten at each update”; “if R's copy is lost, R takes S's at the next run”; and “every disagreement is reported under B1.7.”  
**Fix:** None.

**11 — Resolved | significant.**  
**Where:** ARM P, B1.19.  
**What/why:** The report is now specifically “as *overdue*, naming the cause: failed checks, failed runs, failed captures, or an unavailable host.” The recoverability predicate itself is unchanged.  
**Fix:** None.

**12 — Resolved | significant.**  
**Where:** ARM P, “Deadlines.”  
**What/why:** P now measures each limit from its starting event “whatever happens to the hosts,” and says it is “never suspended, paused or restarted, under any failure.” Unavailability-caused misses are reported “under B1.7 as *overdue*,” with the cause. This covers crashes and the other non-unavailability cells as well as host unavailability.  
**Fix:** None.

**13 — Resolved | minor.**  
**Where:** ARM P, “Parameters.”  
**What/why:** P now gives “*H* … equal to *I* plus slack,” calls *T* “a floor,” and states: “Under BF1.2, BF1.4, BF1.8 or BF1.14 no detection bound holds.” In the context of *Dmax* and *T*, that carries the intended four-cell exclusion.  
**Fix:** None.

**14 — Resolved | minor.**  
**Where:** ARM P, “Parties and terms” and BF1.6.  
**What/why:** P now says: “Every age is measured on the clock of the host that measures it,” and BF1.6 requires: “The tests inject steps of ±1 h and ±24 h, and the error is reported.”  
**Fix:** None.

**15 — Resolved | minor.**  
**Where:** ARM P, “Parties and terms” and EX1.6.  
**What/why:** Both generic binding declarations are now present: “the binding states which hosts the channel depends on,” and “Each binding states whether this exclusion applies to it.”  
**Fix:** None.

**16 — Resolved | minor.**  
**Where:** ARM P, retired identifiers.  
**What/why:** The list now includes “T7a, T7b, T14 and T27,” in addition to the original five identifiers.  
**Fix:** None.

### New ARM P difference/defect check

I found **no new difference in the backup service’s obligations and no new substantive ARM P defect**. I checked every diff hunk: the header, all parties/terms replacements, every changed B1 clause, the deadline paragraph, BF1.6, EX1.6, retired ids, parameters, and all eight added worked cases.

The worked-case adaptations do not change their substance. For example, F has “Sequence numbers (T5a)” and “as T5a says,” while P has “Sequence numbers” and “as the numbering rule above says”; P’s numbering rule is the equivalent rule. Likewise, F’s “Inventory (T28)” becomes P’s “Inventory.”

One editorial difference is not a service-obligation change: F’s §12 heading says “each is also a test case,” whereas P’s heading says only “Worked cases (the same as the four-part form's §12).” If that parenthetical is intended as an instruction to authors rather than a description of F’s existing examples, repeating it in P would remove any doubt about author-facing symmetry.

## 2. Findings 17–26: W1 draft 3

**17 — Resolved | blocking originally.**  
**Where:** W1, “Status: exploratory and descriptive.”  
**What/why:** The general causal claim is expressly withdrawn: “W1 cannot separate an arm's effect from the variation between sessions”; “**W1 claims nothing general about contract form or about the workflow**”; and “It reports what happened with these documents and these runs.” One author per cell remains a limit, but it is no longer disqualifying for the stated descriptive pilot.  
**Fix:** None.

**18 — Resolved | significant.**  
**Where:** W1, “Arms” and “Known limits.”  
**What/why:** The chosen remedy is adequate for the narrowed document comparison: “The worked cases … are in **both** contracts. Interpretation records are F's alone, because they are part of the treatment.” The unequal scrutiny remains disclosed, and “The claim is narrowed to these two documents.”  
**Fix:** None.

**19 — Partly resolved | blocking for the primary measure.**  
**Where:** W1, “Where findings come from” and the decision tree.  
**What/why:** The tree now supplies categories for attribution, implementation/model defects, text defects and supported-reading divergences. However, consequence is merely declared: “A finding is **consequential by construction**, because every finding arises from a failed schedule or a divergence.” A divergence need not have any consequence. The unit and permitted-reading rules also contain the defects detailed in items 27–29 below.  
**Fix:** Define consequence and shared root-cause units operationally, and correct the ordering of the permitted-reading test.

**20 — Resolved | significant.**  
**Where:** W1, decision tree step 3.  
**What/why:** The separate adjudication now supplies both forms: “wrong in both forms: a **contract defect**”; “wrong in this arm's text only: an **arm-specific text defect**.” It also states: “Neither kind enters the primary count.” That remedies the original one-form adjudication and missing arm-specific category.  
**Fix:** None for finding 20; the separate step-2/step-4 ordering problem is item 29.

**21 — Partly resolved | blocking for W1-1.**  
**Where:** W1, decision tree step 1 and “Judging.”  
**What/why:** Blinding and the intended agreement rule are improved: judges do not receive the hypothesis, predictions or other arms’ outcomes, and the primary count is “the findings that **both** judges class as misreadings.” But step 1 says: “Each judge may split or merge it, and that judge's grouping is used for that judge's count.” If the judges use different groupings, there is no defined set of shared findings over which to evaluate “both judges.”  
**Fix:** Use frozen, shared root-cause identifiers for the primary intersection; confine judge-specific regrouping to reported sensitivity analyses.

**22 — Resolved | significant.**  
**Where:** W1, “Hold-outs.”  
**What/why:** The hold-out author now receives “**the prose arm, the binding and the failure model**, and nothing else.” The suite is common to the arms, and “The count, the schedule-to-cell mapping and the schedules' hashes are committed together, before any first version exists.” Although the matrix says “at least two” per cell, the exact count is fixed before outcomes are available. The separate model-expressibility caveat is addressed in item 30.  
**Fix:** None for the original construction finding.

**23 — Resolved | significant.**  
**Where:** W1, “Author protocol.”  
**What/why:** The alternative remedies address the finding: “Every author has a fresh, isolated session”; “All five authors run concurrently,” avoiding order effects; “No clarifying question is answered during a run”; budgets and turn caps are specified; and every exchange is logged. Concurrency is an acceptable substitute for randomized order here.  
**Fix:** None.

**24 — Resolved | significant.**  
**Where:** W1 header, measures and predictions.  
**What/why:** “W1-2 and W1-4 are retired,” and measure 3 is now only “Divergence count, arms F and P (descriptive).” The unsupported “harms the diagnostic” inference is gone.  
**Fix:** None.

**25 — Resolved | blocking for W1-4 originally.**  
**Where:** W1, arms, measure 5 and predictions.  
**What/why:** The original structurally favourable `backup.sh` prediction is withdrawn: “W1-2 and W1-4 are retired,” and “The `backup.sh` row is descriptive: it was not built to this contract.” Arm N instead receives the same prose contract and binding, with no workflow. That resolves the original `backup.sh` finding; the interpretation of the new P–N comparison is discussed in item 32.  
**Fix:** None for the original finding.

**26 — Partly resolved | blocking for W1-5.**  
**Where:** W1, measure 5.  
**What/why:** The revision correctly separates “*recoverable*: B1.19 holds at the schedule's end” from “*reported*,” makes them two booleans, and fixes the denominator as “the committed hold-out set plus one injection per BF1 cell.” However, the reporting boolean still lacks delivery and censoring rules, and the four-cell fallback can replace deadlines that the contract still imposes. See item 31.  
**Fix:** Define reportable events, notice-sent/recorded/delivered states, open reporting windows at schedule end, and genuinely unbounded intervals clause by clause.

## 3. Residual/new defects in W1 draft 3

**27 — Blocking | Decision tree step 1 and Judging: the primary intersection has no stable unit, and grouping is post hoc.**  
**Where:** “Decision tree,” step 1; “Judging,” primary count.  
**What:** There is no determinate mapping between judges’ findings when they split or merge differently, and the steward proposes groupings after failures are known.  
**Why:** The text says both “The steward proposes the grouping. Each judge may split or merge it” and “Primary count per arm: the findings that **both** judges class as misreadings.” If one judge merges two failures into one declared reading and the other splits them by code location, their counts and the both-judges intersection can differ without a defined reconciliation. The steward’s post-outcome grouping is also an uncontrolled researcher degree of freedom.  
**Fix:** Freeze shared, arm-blind root-cause IDs before judging, use only those IDs for the primary intersection, and preregister any reconciliation and model-to-implementation propagation rules.

**28 — Significant | “Where findings come from”: consequence is asserted rather than operationalized.**  
**Where:** “Where findings come from,” final sentence; measure 1.  
**What:** The primary construct can include immaterial divergences or failures, despite calling every finding consequential.  
**Why:** “A finding is **consequential by construction**, because every finding arises from a failed schedule or a divergence.” A model–implementation divergence can concern behavior with no failed contract assertion, and a failed schedule can be defective or concern an immaterial detail. Step 2’s later “other” category does not supply a consequence threshold.  
**Fix:** Either define consequence by a preregistered failed contract assertion/material-impact rule, or delete “consequential” and state plainly that the primary outcome counts all observed qualifying misreadings.

**29 — Significant | Decision tree steps 2 and 4: the supported-reading-divergence class is bypassed in its central case.**  
**Where:** Decision tree steps 2 and 4.  
**What:** A divergence between two behaviors that are both permitted by the text can be classified as *other* before the tree reaches step 4.  
**Why:** Step 2 says: “Is the behaviour a violation of the arm's text? **If not, the finding is *other*.**” Step 4 later says: “If the artifact follows one of two or more readings the text permits, the finding is a **supported-reading divergence**.” But a compliant artifact following a permitted reading is precisely not a violation, so it exits at step 2. Step 3’s undefined word “defective” could additionally swallow mere ambiguity unless ambiguity is expressly excluded.  
**Fix:** Route divergences through the permitted-reading test before the violation/*other* exit, and state that a schedule expecting only one of several permitted readings is a test defect.

**30 — Significant | Hold-outs and divergence discovery: model expressibility is an unfixed exclusion rule.**  
**Where:** “Hold-outs,” final bullet; “Where findings come from,” source (a).  
**What:** Schedules can be excluded from model comparison without a fixed criterion or scoring consequence, changing opportunities to discover misreadings.  
**Why:** Hold-outs run against “both models (**where a model can express them**),” while findings come from “Model–implementation divergences on shared schedules.” The text does not say who decides expressibility, when that decision is frozen, or whether non-expression is itself a model limitation/defect. Deciding after inspecting a model can remove exactly the schedules that would expose its unsupported reading.  
**Fix:** Preregister expressibility criteria, freeze each model’s attempted/expressible schedule set before outcomes are inspected, and give non-expression a fixed scoring rule.

**31 — Blocking for W1-5 | Measure 5: “reported” is not yet a determinate or consistently contract-faithful boolean.**  
**Where:** Measure 5, *reported* bullet; W1-5.  
**What:** The text does not define whether reporting means notice-sent, recorded for later delivery, or delivered to the channel, and it does not say how to score a reporting window that is still open when the schedule ends.  
**Why:** Measure 5 says: “every violation the contract requires to be reported was reported within its bound,” but B1.16 distinguishes a notice that “reaches the channel” from one retained while the channel is unreachable and delivered later. A schedule ending 30 minutes after an event with *D* = 1 h also leaves a compliant implementation’s status undetermined. Further, “Under BF1.2, BF1.4, BF1.8 and BF1.14 no bound holds, and ‘reported by the schedule's end’ is used instead” generalizes the parameter section’s *Dmax*/*T* no-bound statement to all reporting. In some such schedules R and the channel remain available and clause-specific B1.7/B1.16 deadlines still operate; in others a schedule-end report may be impossible and not contractually due. These choices can flip individual schedules and therefore W1-5’s three-schedule threshold.  
**Fix:** Score named reportable events against clause-specific sent/recorded/delivered deadlines, extend or censor windows still open at schedule end, and apply a schedule-end fallback only to expressly defined, genuinely unbounded detection intervals.

**32 — Minor | Arm N: clarify that W1-5 compares workflow packages, not equal-total-compute efficiency.**  
**Where:** Arms table; “Author protocol,” budgets; W1-5.  
**What:** P has an implementation author and a model author, whereas N has one implementation author; N receives the same budget as P’s implementation author, not P’s total arm budget.  
**Why:** The text says: “Arm N's single author gets the same budget as P's implementation author,” and “The workflow's extra cost, the model author, is reported as cost … not hidden.” Because the additional model author is part of the treatment and its cost is reported, this does **not** make W1-5 unfalsifiable or structurally incapable of favouring N. It does, however, mean that the title “the workflow itself” must not be read as an equal-total-budget or efficiency claim.  
**Fix:** Add to Known limits: “W1-5 compares the workflow package at its measured additional cost with one author’s unassisted practice; it is not an equal-total-compute comparison.”

None of W1-1, W1-3 or W1-5 is an outcome that cannot fail: W1-1 and W1-5 have express failure branches, and W1-3 has a numerical threshold. The remaining registration obstacle is deterministic scoring, not the exploratory reclassification itself.

**Bottom line:** ARM P draft 2 is now obligation-equivalent to ARM F for the reviewed service obligations, with no new diff-introduced obligation difference; W1 draft 3 is **not yet fit to register**, even as an exploratory pilot, until the shared-finding/aggregation rule (27) and measure-5 reporting rule (31) are fixed.