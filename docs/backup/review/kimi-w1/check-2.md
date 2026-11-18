## 1. Disposition of the requested items

**19 — Resolved for the original defect; the rewritten tree has a new defect (35).**  
Consequence is no longer merely asserted: “**A qualifying finding** is a failed tagged assertion, or a divergence on a tagged observable,” and “The word ‘consequential’ is dropped.” Units are frozen and the permitted-reading question has moved to step 2. The remaining classification gap is new item 35, not draft 3’s declared-consequence problem.

**21 — Resolved.**  
The primary intersection now has a shared unit set: “Every judge classifies the same frozen units (step 1), so the intersection is always defined.” Judge-specific root-cause comments cannot alter that set.

**26 — Partly resolved; residual blocking item 33 and significant item 34.**  
Delivery is now defined through the channel record, and the blanket four-cell fallback is expressly removed: “Each clause keeps its own deadline under BF1.2, BF1.4, BF1.8 and BF1.14.” However, the reporting rules still omit B1.16’s required recording state, apply the R-down exception too broadly, and replace censoring with an unworkable schedule-termination rule.

**27 — Resolved.**  
The unit is now an “**(artifact, clause id)** pair”; “nobody groups after the outcomes are seen,” and judges’ root-cause comments “never change the units.” That supplies the stable primary intersection and removes the steward’s post-outcome grouping freedom.

**28 — Resolved.**  
The text now mechanically delimits qualifying findings and expressly says: “The word ‘consequential’ is dropped.” The primary outcome therefore counts qualifying misreadings without claiming that every underlying finding has material impact.

**29 — Resolved for the original bypass; new tree-completeness defect 35.**  
Step 2 now asks the permission question “first, so ambiguity is caught before any violation exit,” and expressly states: “A schedule that accepts only one of several permitted readings is a **test defect**.” The original supported-reading case therefore reaches the intended classification.

**30 — Resolved for the original post-hoc-exclusion defect; residual comparison limit 36 and editorial defect 37.**  
Rejection is mechanical and occurs “before any hold-out outcome of any implementation is read”; rejected schedules are recorded per model, and “The set is frozen when it is recorded.” Non-expression also has a fixed consequence: it is reported as a model limitation and yields no divergence unit. The remaining unequal-exposure problem is not post-hoc freedom, but it still affects the raw-count comparison.

**31 — Partly resolved; a blocking residual remains (33).**  
The clause-specific reporting rules are substantially improved, but “**No window is left open**” is implemented by waiting for every window to close. Some windows need never close, and the unspecified “quiet tail of **at least** *D* + one checker period” leaves the recovery-scoring endpoint outcome-dependent.

**32 — Resolved.**  
Known limits now states exactly the required restriction: “**W1-5 compares the workflow package, at its measured additional cost, with one author's unassisted practice. It is not an equal-total-compute comparison**.”

## 2. Residual and diff-introduced defects

**33 — Blocking | Measure 5, schedule termination and the quiet tail: W1-5 can become unscorable, and its recovery endpoint can be chosen after outcomes.**  
**Where:** Measure 5, *recoverable*, *reported*, and “No window is left open.”  
**What/why:** *Recoverable* is evaluated “at the schedule's end,” but the harness “ends a schedule only once every reporting window the schedule opened has closed.” A channel-outage window closes only after the channel returns and its subsequent deadline expires; if the channel never returns, there is no schedule end and therefore neither boolean nor a W1-5 score. This is not merely hypothetical: BF1.2 permits partitions “of any length, healed or not,” and BF1.7 does not require the notice channel to recover. Continually recurring failures can likewise keep opening new windows.  
Even when every window closes, the tail is only “**at least** *D* + one checker period.” Its length is not fixed, while B1.19 can change during that tail. Extending or shortening observation can therefore flip *recoverable* after outcomes are visible. Outcome-dependent events can also give N and P different scoring durations for the same named schedule.  
**Fix:** Precommit every schedule’s scoring endpoint and exact observation tail; score *recoverable* there, and score *reported* false only for deadlines already due and unmet at that fixed horizon, listing later-due windows as open/censored rather than waiting for recovery or choosing a longer tail.

**34 — Significant | Measure 5: the new reporting rules are determinate but not contract-faithful.**  
**Where:** Measure 5, the three deadline bullets and the channel-record definition.  
**What/why:**  
- The rule “while R … is down, *D* after R returns” applies to every reportable event. It therefore excuses late S-originated notices even though B1.7 requires “A run on S that fails … within *D* of failing,” and B1.15 has its own *D*-from-comparison deadline. R being down need not prevent either S notice. For checker deadlines, the class rule also says deadlines are “never suspended and never restarted” and that unavailability “never excuses or resets one.”  
- During channel unavailability, draft 4 checks only eventual delivery: “the notice channel's record holds a notice.” B1.16 additionally requires that, “While the notice channel cannot be reached, the sender **records the notice where the freshness checker reads**.” An implementation that records nothing and invents the notice only after recovery can consequently be scored *reported*.  
These conventions can flip individual schedule booleans and hence W1-5, although they do not themselves make the prediction unscorable.  
**Fix:** Use event-origin-specific sent/recorded/delivered rules: preserve S’s own deadlines, never restart missed deadlines, confine any R-return detection rule to checker-originated events, require B1.16’s outage recording as well as later delivery, and state the EX1.6 treatment explicitly.

**35 — Significant | Decision tree steps 2–4: the rewrite removes the old *other* exit without providing complete replacement branches.**  
**Where:** “Where findings come from” and decision tree steps 2–4.  
**What/why:** A qualifying finding can simply be “a failed tagged assertion.” Step 2 handles permitted behaviour only when “the text permits two or more readings.” Step 4’s non-misreading branch then requires “No such evidence, **where the artifact simply does not do what the text says**.” Consequently, an artifact that follows the sole permitted reading but fails an incorrect assertion has no classification: it is neither a supported-reading divergence nor an artifact that disobeys the text. A similar fall-through occurs when an author declares a supported reading but implements it incorrectly. Judges are given no consistent test-defect/*other*/implementation-defect route for these units.  
**Fix:** Restore an explicit compliant-behaviour exit—wrong assertion → test defect, otherwise *other*—and add a branch assigning implementation/model defects when the declared reading is supported but the artifact violates it.

**36 — Significant | Hold-outs: mechanical expressibility still leaves unequal primary-count exposure and conflates rejection with non-expression.**  
**Where:** Hold-outs, final bullet; measures 1–2.  
**What/why:** “Schedules the runner rejects” yield “no divergence unit.” F’s and P’s runners can reject different schedules, leaving different opportunities to discover model misreadings, while W1-1 compares raw “misreadings per arm,” not exposure-adjusted results. A runner defect or execution failure can also be labelled non-expression rather than a model failure. The freeze removes after-the-fact steward choice, but not this confound.  
**Fix:** Use a frozen common F/P expressible set for primary model-divergence scoring, or a fixed exposure-adjusted rule, and distinguish syntactic non-expression from runner execution defects; otherwise disclose the resulting raw-count limitation explicitly.

**37 — Minor | Hold-outs versus measure 2: the named reporting category is missing.**  
**Where:** Hold-outs, final bullet; measure 2.  
**What/why:** Hold-outs says rejected schedules “are reported under measure 2 as a model limitation,” but measure 2 lists only “Supported-reading divergences, arm-specific text defects and contract defects.”  
**Fix:** Add “model limitations, including non-expressible schedules” to measure 2.

I checked every diff hunk: header, hold-outs, tags/findings, decision tree, judging, measures, and Known limits. Apart from items 33–37, those changes introduce no new unfalsifiable prediction, leak, or post-outcome adjudication freedom.

**W1 draft 4 is not fit to register as an exploratory pilot until blocking item 33 is fixed; items 34–37 must otherwise become expressly stated limits.**