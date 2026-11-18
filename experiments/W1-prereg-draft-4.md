# W1: an exploratory pilot on contract form and on the workflow itself (pre-registration DRAFT 4; NOT registered)

Draft 1 was written by the twelfth steward (2026-11-12), and drafts 2 and 3 by the thirteenth (2026-11-18). Draft 3 answered Kimi's review of draft 2 (`docs/backup/review/kimi-w1/`, all 26 findings accepted). Draft 4 answers Kimi's check of draft 3 (`check-1.md`, items 19, 21, 26 to 32, all accepted). By the stop rule (log, 2026-11-18), draft 4 gets one check, and after it only blocking items are fixed. **This draft registers nothing.** Ids are never reused. **W1-2 and W1-4 are retired.**

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
- The hold-outs run against all three implementations and both models, and descriptively against `backup.sh`.
- **Model expressibility is decided mechanically, before any outcome is read** (check item 30). After both first versions are in, the steward feeds every hold-out to each model author's own schedule runner once. That happens before any hold-out outcome of any implementation is read. Schedules the runner rejects are recorded per model as **not expressible**. They are reported under measure 2 as a model limitation, and they yield no divergence unit. The set is frozen when it is recorded.

## Where findings come from
- (a) Model–implementation divergences on shared schedules: arms F and P only.
- (b) Failures under the injected BF1 cells and the hold-outs: all three implementations.

**Tags make findings mechanical.** Every assertion in every shared, injected and hold-out schedule carries a `derives:` tag naming the clause it checks (AGENTS.md rule 2). The hold-out author is told to tag every assertion. A schedule assertion without a tag is fixed before the hashes are committed. Divergences are compared on tagged observables. **A qualifying finding** is a failed tagged assertion, or a divergence on a tagged observable. Nothing else enters the decision tree. (The word "consequential" is dropped: Kimi, check item 28.)

## Decision tree for each finding (Kimi, findings 19 and 20, check items 27 and 29; fixed here)
1. **Unit, fixed before any run.** A unit is an **(artifact, clause id)** pair, where the clause id is the tag on the failed assertion or the diverging observable. Every qualifying finding of one artifact under one clause is one unit, however many schedules show it. A divergence yields one unit on each side. The unit is mechanical, so nobody groups after the outcomes are seen. *Accepted cost:* two root causes under one clause merge, and one root cause that fails two clauses counts twice, the same rule for every arm. Judges may comment on root causes, and those comments are reported as a sensitivity note. They never change the units.
2. **Does the arm's text permit the artifact's behaviour under that clause?** This is asked first, so ambiguity is caught before any violation exit (check item 29).
   - If the text permits two or more readings and the artifact follows one of them, the unit is a **supported-reading divergence**. It is counted separately and is never a misreading. A schedule that accepts only one of several permitted readings is a **test defect**: reported, and excluded from every count.
3. **Is the text itself defective?** Defective means contradictory or unsatisfiable. Mere ambiguity is not a defect, because step 2 handles it. A defective text goes to a **separate contract-defect adjudication**, in which the judge receives **both** forms:
   - wrong in both forms: a **contract defect**, reported against the contract;
   - wrong in this arm's text only: an **arm-specific text defect**, reported per arm.

   Neither kind enters the primary count.
4. **Is there evidence of what the author read?** That means the artifact's declared reading, a recorded clarifying question, its README, or its spec or code text that states the reading.
   - Evidence of a reading the text does not support: a **misreading**.
   - No such evidence, where the artifact simply does not do what the text says: an **implementation defect**, or a **model defect**.
5. **Attribution:** to the model or the implementation, by the unit's artifact.

## Judging (Kimi, finding 21)
- Judges receive the finding, the arm's own text (both forms only in step 3) and the artifact. They are not given the hypothesis, the predictions, other arms' outcomes, or arm labels. **The form of the text cannot be hidden, and this pre-registration says so.**
- **Primary count per arm:** the units that **both** judges class as misreadings. Every judge classifies the same frozen units (step 1), so the intersection is always defined. Each judge's own count is reported beside it.

## Measures (fixed here)
1. **Primary:** the misreadings per arm, as above.
2. Supported-reading divergences, arm-specific text defects and contract defects, per arm (descriptive).
3. Divergence count, arms F and P (descriptive, Kimi, finding 24).
4. **Cost:** author tokens and wall-clock per arm, including P's model author, and the steward's and Tony's attention.
5. **Per named schedule, for each of the three implementations and for `backup.sh`** (check item 31):
   - *recoverable*: B1.19 holds at the schedule's end;
   - *reported*: every **reportable event** the schedule causes was reported in time. The reportable events are those of B1.7, B1.15's notice, and a failing run's own notice. An event counts as reported when **the notice channel's record holds a notice that names the clause** (that is, "reaches", in both forms) within the event's own bound:
     - *D* from the event, while R and the channel are reachable;
     - while the channel is unreachable, *D* after it becomes reachable again (B1.16's second part);
     - while R, the freshness checker's host, is down, *D* after R returns. This is the only case the contract leaves without a bound.

     Each clause keeps its own deadline under BF1.2, BF1.4, BF1.8 and BF1.14, except for the two reachability cases above. No blanket "by the schedule's end" rule applies.
   - **No window is left open.** The harness ends a schedule only once every reporting window the schedule opened has closed, with a quiet tail of at least *D* + one checker period.

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
- **W1-5 compares the workflow package, at its measured additional cost, with one author's unassisted practice. It is not an equal-total-compute comparison** (check item 32).
- Arm N's author is the same family as F's and P's implementation authors. That holds the family constant, and it also means that N measures one family's unassisted practice.

## Not in scope
Which implementation, if any, becomes the service tupay runs is decided after scoring. It is checked against the migration acceptance contract when the move happens.
