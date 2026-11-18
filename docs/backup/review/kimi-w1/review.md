**Disposition: do not register yet.** ARM P does **not** pass the obligation-equivalence gate. Its central B1.19 recoverability predicate is intact, but there are differences in record contents, deadline triggers, failure stages, recovery timing, reporting and parameter scope. Separately, W1 as designed **cannot answer its question as a general causal claim**; it can at most produce an exploratory comparison of these particular documents and author runs.

## Part A — obligation equivalence

**1 — A | significant | T6, T7c, T28: snapshot and manifest records.**  
**What is wrong:** P omits the requirements that a snapshot be named by its sequence number and that its manifest include the complete source inventory, be written by the run, and be stored with the snapshot.  
**Why:** F says: “**T6 Snapshot** … It is stored at R and **named by its sequence number**,” and “**T7c Manifest**: every file in the snapshot with its sha256, **together with the run's source inventory (T28). The run writes it and stores it with the snapshot**.” P says only: “Each snapshot has a manifest that lists every file and its sha256.” B1.17 reconstructs much of the path inventory, but P still need not preserve the git `(ref name, object id)` inventory in the manifest, nor associate the manifest with the snapshot in the required way.  
**Fix:** Add the substance of F’s T6 and T7c sentences to P, including the git inventory, manifest writer and storage location.

**2 — A | minor | B1.2, T28: git object scope.**  
**What is wrong:** P can impose a stronger exact-object-set requirement than F.  
**Why:** F requires that a repository “is bundled from T28's `(name, object id)` pairs, **so its refs are exactly those pairs**.” P instead says: “A git repository in a snapshot holds **exactly the refs and objects** read at the run's start,” and earlier “bundles exactly those objects.” F constrains the source object ids and the resulting refs; it does not say that reachable historical objects absent from the inventory are forbidden. P’s wording can exclude objects needed to reconstruct the listed commits.  
**Fix:** Replace P’s git wording with F’s requirement: build from the inventory’s `(ref name, object id)` pairs, never later-resolved names, with refs exactly equal to those pairs.

**3 — A | significant | T15, T16: status-record and notice contents.**  
**What is wrong:** P weakens the record schema and notice reporting/delivery requirements.  
**Why:** F requires run entries to contain “sequence number; *started*, *ok* or *failed*; stage …; **times**,” and snapshot marks to contain “sequence number; …; **time; writing host**.” P describes only “run entries (started, ok or failed, with the stage that failed …) and snapshot marks …,” omitting times and writing hosts. F also defines a notice as “a message … that **names its clause**,” which “**reaches** the channel when the channel's record holds it.” P has no corresponding definition; its B1.16 merely says “A notice reaches the channel.” Thus P permits less informative records and notices and lacks F’s delivery test.  
**Fix:** Add the missing run-entry and mark fields, require every notice to name its clause, and define receipt as presence in the channel’s record.

**4 — A | significant | T24, T25, T19: check cadence and retention selection.**  
**What is wrong:** P does not determine the same daily-check schedule, daily snapshot or month boundary.  
**Why:** F says: “**T24 Daily check** … runs on S **once every *I***”; “**T25 Daily snapshot**: the acknowledged snapshot with the **highest sequence number in its UTC day**”; and “*d* = 24 h; *month* = a **UTC calendar month**.” P says only “the daily check on S” and uses “any daily snapshot” and “the first daily snapshot of each month.” Calling a check “daily” does not guarantee one check in every rolling interval *I*, and P does not say which acknowledged snapshot is retained when a UTC day has several.  
**Fix:** Add the once-per-*I* cadence, the highest-sequence-number UTC-day definition, and F’s unit definitions.

**5 — A | minor | B1.5, B1.15, B1.17: failure stages and B1.5’s actor.**  
**What is wrong:** P drops three prescribed failure stages and broadens B1.5’s no-write actor.  
**Why:**  
- F: “**The run** never writes a credential file … A hit fails the run at stage ***no-credentials***.” P: “**No credential file is ever written** … A hit fails the run.”  
- F: “An unreadable source tree fails the run at stage ***source***.” P: “A source tree that cannot be read fails the run.”  
- F: “the run fails at stage ***capture***, and the snapshot is not acknowledged.” P: “A path … fails the run.”  

P’s B1.6 requires some stage, but not the stage that identifies the cause. P’s passive B1.5 also covers writers other than the run, whereas F’s obligation is specifically on the run. B1.1 already prevents acknowledgment after a completeness failure, so the principal B1.17 loss here is the prescribed stage, not a new permission to acknowledge.  
**Fix:** Restore “The run” in B1.5 and add the exact stages *no-credentials*, *source* and *capture*, plus F’s explicit non-acknowledgment sentence.

**6 — A | significant | B1.7: the failed-run notice trigger.**  
**What is wrong:** P changes the checker’s trigger and potentially its deadline start.  
**Why:** F requires a checker notice within *D* of “**a *failed* run entry appearing**.” P requires it within *D* of “**a failed run**.” These differ when S fails while partitioned from R: F’s checker clock starts when the entry appears; P can be read as starting it at the actual failure, before the checker can observe it. Both forms separately require the failing run on S to send its own notice.  
**Fix:** Change P’s bullet to “a *failed* run entry appearing.”

**7 — A | minor | B1.8: the pending restore-check mark.**  
**What is wrong:** P omits an express status obligation and its non-discharge effect.  
**Why:** F says: “**Until a check completes, the record shows *not restore-checked*, which is a state and not a discharge.**” P lists *not restore-checked* among possible marks but says only that the restore host “completes a restore check … and records the result.” P therefore does not expressly require the pending state to be shown.  
**Fix:** Add F’s pending-mark sentence verbatim in substance.

**8 — A | significant | T26, B1.15: logged reasons and the notice deadline.**  
**What is wrong:** P permits a different suppression condition for shrinkage notices and does not preserve the deadline’s start event.  
**Why:** F defines a logged reason as “an entry in the record the binding names, **written before the run, that names the source tree and the change**,” and requires the notice “within *D* **of the comparison**.” P says only “A fall of more than *Q* that **no logged reason covers** sends a notice … within *D*.” Without T26, a retrospective or generic reason might “cover” the fall; without “of the comparison,” the clock can be attached to the earlier source change rather than the run’s comparison.  
**Fix:** Add T26’s record, timing and specificity requirements and change P’s deadline to “within *D* of the comparison.”

**9 — A | minor | B1.17: completeness obligation narrowed to acknowledged snapshots.**  
**What is wrong:** P’s first completeness sentence applies only to acknowledged snapshots; F’s applies to run manifests generally.  
**Why:** F says: “**The manifest** holds every path in the source inventory … or lists it as *gone* ….” P says: “**An acknowledged snapshot's manifest** holds every path ….” The acknowledged-snapshot guarantee is largely preserved through B1.1, but P does not impose the same manifest obligation on failed or otherwise unacknowledged runs.  
**Fix:** Remove P’s “acknowledged snapshot’s” qualifier and state the manifest rule for every run, while retaining B1.1’s acknowledgment gate.

**10 — A | significant | B1.18: hash maintenance, recovery timing and disagreement reporting.**  
**What is wrong:** P weakens three distinct recovery obligations.  
**Why:**  
- F: each copy’s hash is “**rewritten at each update**”; P says only that each copy “carries a hash over its entries.”  
- F: “If R's copy is lost, R takes S's copy **at the next run**”; P: “if R's copy is lost, R takes S's,” with no equivalent deadline.  
- F: when intact copies disagree, “**Each disagreement is reported under B1.7**”; P says only “every disagreement is reported,” omitting B1.7’s notice route and timing.  

These are not merely stylistic omissions: they concern whether the integrity mechanism is maintained, when R must recover, and how quickly a disagreement must be reported.  
**Fix:** Add “rewritten at each update,” “at the next run” for R’s recovery, and “under B1.7” for every disagreement.

**11 — A | significant | B1.19: violation-report contents.**  
**What is wrong:** P preserves the recoverability predicate but weakens the required violation report.  
**Why:** F requires: “B1.7 reports it as ***overdue*, with the cause: failed checks, failed runs, failed captures, or an unavailable host**.” P says only: “this clause is violated, whatever the cause, and B1.7 reports it.” A bare notice can satisfy P without identifying the violation as overdue or reporting its cause.  
**Fix:** Require the B1.7 notice to be *overdue* and to name the applicable cause category.

**12 — A | significant | Deadline class rule.**  
**What is wrong:** P makes non-suspension/non-restart conditional on host unavailability, while F makes it unconditional.  
**Why:** F says deadline clauses “are **never suspended and never restarted**,” and the checker measures age from the original event “**whatever happens to the hosts**.” P says only: “Every time limit above … is **never paused or restarted when a host is unavailable**.” P therefore leaves open resetting or pausing a deadline after a crash or another non-unavailability failure. F also requires unavailability-caused misses to be reported “**under B1.7**”; P requires an overdue report but does not consistently preserve that notice path.  
**Fix:** State that deadlines are never suspended, paused or restarted under any failure cell, and that unavailability-caused misses are reported under B1.7 as overdue with the cause.

**13 — A | minor | Parameters: derivations and excluded detection bounds.**  
**What is wrong:** P omits part of F’s parameter derivation and no-bound scope.  
**Why:** F defines “*H* staleness, **= *I* + slack**,” calls *T* “**a floor**,” and expressly says that “Under **BF1.2, BF1.4, BF1.8 or BF1.14 no bound holds**.” P calls *H* only “the staleness limit,” omits “floor,” and says of *Dmax* and *T*: “Both hold only if the next run succeeds, the damage crosses *Q*, and R and the channel are reachable.” The shared binding currently gives the same numerical *H*, but P does not carry the generic derivation or the express exclusion for all four cells, notably timer failure and restore-host suspension.  
**Fix:** Copy F’s *H* derivation, *T* floor statement and explicit four-cell no-bound sentence into P.

**14 — A | minor | T12, BF1.6: clock measurement, tests and reporting.**  
**What is wrong:** P changes reporting of clock error and omits the prescribed test steps.  
**Why:** F says an age is measured “on the clock of the host that measures it,” and BF1.6 states: “The tests inject steps of **±1 h and ±24 h**, and the error is **reported**.” P says only: “Every deadline can then be wrong by up to the size of the step, and the error is **measured**.” Measurement alone does not require reporting, and P does not carry the two injection parameters.  
**Fix:** Add T12’s clock rule and require ±1 h and ±24 h test steps with the error reported, not merely measured.

**15 — A | minor | T29, EX1.6: binding declarations.**  
**What is wrong:** P omits two requirements placed on a binding.  
**Why:** F says: “The binding states **which hosts the channel depends on**,” and EX1.6 adds: “**Each binding states whether this exclusion applies to it**.” P’s EX1.6 describes the dependency condition but imposes neither declaration requirement. The present shared binding does state that its record is on S and that EX1.6 applies, so the immediate Tupay configuration is covered; the generic obligation on other or future bindings is nevertheless absent from P.  
**Fix:** Add both binding-declaration requirements to P.

**16 — A | minor | Retired identifiers.**  
**What is wrong:** P’s retirement list is incomplete.  
**Why:** F retires “B1.10, B1.14, BF1.11, AI1.6, EX1.4, **T7a, T7b, T14 and T27**.” P lists only “B1.10, B1.14, BF1.11, AI1.6 and EX1.4.” Its general statement that ids are never reused does not tell a P author that these four T ids already have retired meanings.  
**Fix:** Add T7a, T7b, T14 and T27 to P’s retired-id list.

### A: identifier reconciliation and sound areas

Within the two contract files, P contains **no T-series or I-series labels**. Consequently, these F labels are absent from P as labels: **T1, T2, T3, T4, T5, T5a, T6, T7c, T8, T9, T10, T11, T12, T13, T15, T16, T17, T18, T19, T20, T21, T23, T24, T25, T26, T28, T29**, and **I-B1.1, I-B1.2, I-B1.3, I-B1.4, I-B1.5, I-B1.6, I-B1.7, I-B1.8, I-B1.9, I-B1.11, I-B1.12, I-B1.13, I-B1.15, I-B1.16, I-B1.17, I-B1.18, I-B1.19**. Their absence as labels is intentional and is not itself a finding; the substantive omissions are identified above. P introduces no new live identifier and contains all live B1, BF1, EX and AI identifiers used by F.

**Sound in A:** B1.1, B1.3, B1.6, B1.9, B1.12 and B1.13 match in substance; B1.4’s four retention groups, B1.11’s expiry rule, B1.16’s two delivery limbs and B1.19’s recoverability predicate also match, subject to the related definition/reporting findings above.

## Part B — adversarial review of W1

**17 — B | blocking | Arms, W1-1 and Known limits: one author pair cannot identify the claimed effect.**  
**What is wrong:** The design has no replication from which to separate an arm effect from session-to-session author variation.  
**Why:** “Each arm has **one implementation author and one model author**,” and the draft admits: “With one author pair per arm, **only a large effect can show**.” Holding the model family constant does not remove variation between fresh sessions, prompts, decoding, tool trajectories or stopping points. A three-finding difference can arise from that variation; a real but smaller effect cannot be detected. This is disqualifying for the general claim that the form “produce[s] fewer” misreadings, not merely a limitation on statistical precision.  
**Fix:** Either replicate independent author pairs with randomized arm assignment and a preregistered uncertainty/analysis plan, or explicitly reclassify W1 as a descriptive pilot limited to these runs.

**18 — B | significant | Known limits: preparation and information are confounded with form.**  
**What is wrong:** The result cannot be attributed cleanly to the four-part form rather than unequal scrutiny and test-relevant explanatory content.  
**Why:** The draft admits: “The steward wrote both forms, so **the prose arm's quality is the steward's**,” and “The four-part form was **hardened by four review rounds** … The prose arm inherits every fix, **but not the scrutiny of form**.” In addition, F supplies interpretation witnesses and §12 execution examples that P deliberately withholds. Fewer P misreadings could therefore reflect prose quality; fewer F misreadings could reflect extra scrutiny or concrete examples rather than controlled syntax. The draft discloses these confounds but does not control them.  
**Fix:** Equalize non-form semantic content and independent review effort, or narrow the claim explicitly to these two exact documents rather than to the form itself.

**19 — B | blocking | Measures 1: the primary outcome is not an operational count.**  
**What is wrong:** “Consequential,” the unit of counting and the boundary between misreading and implementation defect are not fixed.  
**Why:** A judge must distinguish “the artifact follows a reading the text does not support” from “implementation defect,” without any specified evidence of what the author read or any decision rule. The definition also calls following “**one of two readings the text permits**” a misreading, although that is a supported-reading ambiguity or divergence, not textual nonconformance. There is no rule for merging findings with one root cause, splitting one failure into several clauses, charging a model–implementation divergence to the model, implementation or both, or deciding which divergences are “consequential.” Since W1-1 depends on a difference of three counts, these choices can determine the result after outcomes are visible.  
**Fix:** Preregister a decision tree and unit of analysis covering consequence, root-cause deduplication, artifact attribution, supported-reading divergences and the evidence required to call behavior a misreading rather than a defect.

**20 — B | significant | Measures 1: the contract-defect class is neither judgeable nor arm-symmetric.**  
**What is wrong:** A judge is asked to decide a both-forms question while receiving only one form, and a defect unique to one form has no coherent category.  
**Why:** The judge receives “the finding, **the contract text of its arm** and the artifact,” but must identify a “contract defect (**the text is wrong or contradictory in both forms**).” That judge cannot establish the state of the other form from the supplied evidence. If only one arm’s text is contradictory, the stated definition excludes contract defect, potentially forcing the finding into misreading or “other.”  
**Fix:** Use a separate both-forms contract-defect adjudication and add an explicitly arm-specific text-defect category, with a fixed rule for whether it enters either arm’s primary count.

**21 — B | blocking | Measures 1 and Known limits: judge disagreement and blinding leave scoring unresolved.**  
**What is wrong:** There is no single preregistered rule mapping two judges’ counts to W1-1, and the purported arm concealment cannot conceal the treatment.  
**Why:** “Two judges … rule independently, and where they disagree, **the result is reported under each judge**.” One judge can therefore produce a P−F difference of at least three while the other produces an inconclusive difference; the draft does not say whether W1-1 holds. Also, hiding “the arm's name **where possible**” does not blind a judge who receives the unmistakable four-part or prose contract. That matters because the primary classification is discretionary. The phrase “while W1-1 does not hold” in W1-2 is additionally unclear about whether the inconclusive region qualifies.  
**Fix:** Predeclare the aggregation rule—for example, a judge-specific primary result with a specified requirement for agreement—and blind judges to the hypothesis, predictions and other-arm outcomes while acknowledging that document form itself cannot be hidden.

**22 — B | significant | Measures 1(b): hold-out construction can differentially determine finding opportunities.**  
**What is wrong:** The draft does not say which contract the hold-out author receives or fix the suite’s coverage and granularity.  
**Why:** The hold-outs are written “**from the contract alone**,” but there are two contract texts. A suite derived from F also receives its witnesses and execution examples; one derived from P does not. Hashes committed before the first versions prevent later schedule editing, but they do not prevent differential coverage, many schedules around one anticipated weakness, or schedules that cannot be instantiated without the shared binding. Because test failures are a source of the primary count, these choices can change the result independently of author misreading.  
**Fix:** Name exactly which documents and binding the hold-out author receives, and freeze a common coverage matrix, schedule count/mapping and deduplication rules before either arm runs.

**23 — B | significant | Arms and Known limits: author isolation and clarification protocols are unspecified.**  
**What is wrong:** Symmetric brief filenames do not prevent cross-arm information, order effects or asymmetric assistance.  
**Why:** The briefs are “the same apart from which contract file they name,” and authors run “in the sandbox under the current practice file.” The only stated leak control is “a non-Claude review” of each brief for review findings. There is no requirement for fresh independent sessions, randomized order, denial of access to the other arm/review history, or symmetric handling of clarifying answers. Nor is there a common stopping rule or budget, even though completeness and cost can affect the number of detected defects.  
**Fix:** Use fresh isolated sessions with controlled file visibility and randomized order, and preregister budgets, stopping and clarification-answer rules with all author communications logged.

**24 — B | significant | W1-2: fewer divergences do not establish harm to a diagnostic.**  
**What is wrong:** The proposed interpretation does not follow from the measurements, and the two measures are mechanically coupled.  
**Why:** W1-2 says F “harms the diagnostic” if it has fewer divergences while W1-1 does not hold: “That would mean the authors agree more without misreading less.” Fewer divergences can instead reflect agreement on correct behavior, fewer implemented features, less test sensitivity, or a shared error that produces no divergence. Moreover, divergences are themselves a discovery source for measure 1, so fewer divergences can mechanically reduce the number of findings available for misreading classification.  
**Fix:** Report divergence count descriptively and remove the causal “harms the diagnostic” conclusion unless diagnostic value is tested against independently known ambiguity cases.

**25 — B | blocking for W1-4 | Baseline: the comparison is structurally favorable to both treatment arms.**  
**What is wrong:** The baseline is scored against a contract-specific recoverability/reporting target it was not built to implement, so the comparison cannot identify an effect of the workflow.  
**Why:** The draft admits: “`backup.sh` was **not written to this contract**, so some of its failures are **expected by construction**.” The shared binding is more specific: it lacks, among other things, “B1.3 and B1.8 from R alone … B1.16 … B1.17 [and] B1.18.” It can therefore lose measure 5 for lacking restore-check marks or contract notices regardless of whether its copies are useful. Calling this “not about fairness to `backup.sh`” does not make it evidence that the workflow, rather than contract targeting and unequal design information, caused the difference. W1-4 can logically fail, but the design makes success likely without the workflow claim being true.  
**Fix:** Give an independent non-workflow baseline author the same recovery/reporting SLO, binding and resources, or demote `backup.sh` to a descriptive engineering comparison and withdraw the workflow-effect claim.

**26 — B | significant | Measure 5 and W1-4: the baseline score and aggregation are ambiguous.**  
**What is wrong:** Recoverability and contract-compliant violation reporting are combined without a determinate per-schedule rule.  
**Why:** Measure 5 counts cells and hold-outs “after which **B1.19 holds** … **and every violation is reported**,” whereas the binding describes the service guarantee as a recoverable snapshot “**or a reported violation**.” It is unclear whether a correctly reported B1.19 violation earns any credit, which past violations must be reported by the schedule’s end, or how cells with no promised detection bound are scored. Measure 5 covers “cells **and hold-outs**,” while W1-4 asks about “strictly more **cells**,” leaving hold-outs’ contribution unclear. Multiplicity and weighting of schedules are also unspecified.  
**Fix:** Score recoverability and timely required reporting as separate preregistered booleans per named schedule, define reportable violations and excluded detection intervals, and state the exact cells/hold-outs denominator used by W1-4.

### B: sound elements and overall judgment

**Sound in B:** W1-1 and W1-3 are not unfalsifiable—W1-1 expressly fails when F has at least as many misreadings, and W1-3 has a numerical failure condition; the arbitrary threshold is also openly acknowledged.

**Sound in B:** Holding author families and the binding constant, using separate hold-out and judge families, committing hold-out hashes before artifacts, and giving the equivalence reviewer no other W1 role are useful safeguards, though insufficient for the problems above.

**Overall:** Even after all Part A differences are repaired, W1 can support only a narrowly descriptive result unless findings 17, 19 and 21 are resolved. W1-4 cannot presently support its workflow claim. A clearly labelled **exploratory case study** would be defensible with the scoring ambiguities fixed; a general answer to “does the four-part form reduce consequential misreadings?” is not supported by the present design.