# Research Seed: The Gardener, the Salmon, and the Failure Model

**Date:** November 12, 2026  
**Intended audience:** Tupay and Arariwa research stewards  
**Status:** Exploratory seed — not a specification or directive  
**Origin:** A conversation examining recovery-oriented distributed systems, the evolution of failure models, and the possibility that a research system can become increasingly successful at answering the wrong questions.

## 1. The concern

Tupay was conceived as an iterative research process.

Its purpose is not merely to establish a service contract, derive tests, identify violations, and improve an implementation until those tests pass.

Its deeper purpose is to improve our understanding of what a system must do, why it fails, and how it can recover.

The distinction matters.

A research process can gradually become a requirements-validation process without anyone explicitly deciding to make that transition.

A typical progression might be:

1. Establish a service contract and failure model.
2. Derive tests from the model.
3. Execute experiments.
4. Identify defects.
5. Improve the implementation.
6. Repeat until the tests pass.

Every step appears reasonable.

Yet the process can converge on an implementation that satisfies its model without establishing that the model adequately describes the system's operating environment.

**The danger is not that the system stops learning. It is that the system becomes increasingly proficient at learning only what its existing assumptions permit it to observe.**

The proposed response is not to abandon formal models, contracts, or disciplined experimentation.

It is to preserve the ability to revise them.

## 2. A lesson from Indaleko

Indaleko began with an outcome: helping people find personal information.

Search was a mechanism for achieving that outcome, not the objective itself.

Optimizing search metrics could improve performance without necessarily improving a person's ability to find something they remembered imperfectly.

The research therefore had to remain grounded in the desired outcome rather than the conventional metrics of the chosen mechanism.

The same distinction applies to distributed systems.

Paxos is a mechanism.

Consensus is a capability.

Neither is the ultimate objective.

The objective is to build a service that behaves acceptably in the presence of failures, including recovering from those failures when recovery is required by its contract.

Consider two systems.

An ephemeral in-memory key-value store may legitimately lose its entire contents when its process terminates. Its contract might require nothing more than restarting with an empty map.

A geographically distributed, sharded, replicated key index presents a different problem.

If the index is separated from its underlying object storage, losing the index may leave the objects physically intact but make them expensive—or potentially impossible—to locate and reconstruct.

The relevant question is not initially whether the system implements consensus correctly.

It is:

**What information must survive a failure for the service to recover in accordance with its contract?**

That question can determine whether consensus is necessary, which information requires durable agreement, what replication strategy is appropriate, and which recovery actions must remain possible.

The mechanism follows the requirement.

And the requirement follows the desired outcome.

## 3. Failure-first investigation

A recent investigation proposed beginning with a conventional Paxos decomposition:

- Independent proposers.
- Independent acceptors.
- Independent learners.
- Separate physical machines and failure domains.

The investigation would then introduce additional complexity:

- Automated recovery.
- Dynamic configuration.
- Flexible Paxos quorum arrangements.
- Concurrent failures and recovery actions.

The resulting failures and limitations would become adversarial test cases for optimized implementations that merge roles, combine failure domains, or otherwise simplify the architecture.

This reverses a common evaluation strategy.

Instead of beginning with an optimized implementation and asking whether it satisfies protocol invariants, begin with the service's recovery requirements and investigate how architectural choices affect them.

The investigation should distinguish protocol safety violations from loss of availability, loss of recoverability, and unacceptable recovery cost.

A system may preserve consensus safety while losing the ability to restore service under its operational assumptions.

For example, a Flexible Paxos arrangement may permit ordinary Phase 2 progress while lacking sufficient available acceptors to complete a new Phase 1 after leadership failure.

That is not necessarily a protocol defect.

It is nevertheless relevant to a service whose operational requirements include recovering from leadership failures.

**A healthy system is not necessarily a recoverable system.**

## 4. Three seeds for Tupay

### Seed A: The failure model is a hypothesis, not an authority

A failure model describes which failures are considered, which assumptions are made, and which recovery obligations are evaluated.

It is a tool for reasoning about a system.

It is not the system itself.

Evidence that falls outside the model should not automatically be classified as irrelevant.

Such evidence may indicate that the model is incomplete, overly restrictive, or based on assumptions that no longer hold.

An explicit research question follows:

*What observations would cause us to revise the failure model rather than modify the implementation?*

If no such observations can be identified, the model may have become effectively unfalsifiable.

### Seed B: Experiments may revise the question

An experiment can reveal several different kinds of problems:

- The implementation violates its contract.
- The contract inadequately expresses the desired service behavior.
- The failure model excludes a relevant operational condition.
- The instrumentation cannot distinguish important system states.
- The evaluation metric rewards behavior that does not improve the desired outcome.

These cases should not be conflated.

Fixing an implementation defect is useful.

Discovering that the service contract describes the wrong behavior may be substantially more important.

An iterative process must permit changes at every level, including its original question.

### Seed C: Success should create opportunities for falsification

As an implementation improves, previously failing tests should begin to pass.

That is evidence of progress against the existing evaluation criteria.

It is not necessarily evidence that the system is becoming more resilient.

A productive research process should periodically ask:

*What new failure can we investigate because of what we have learned?*

This does not mean every successful experiment must produce a new failure.

It means that accumulating successful results should not eliminate the search for evidence that challenges the current model.

A mature research process should be capable of discovering that its previous successes were less meaningful than originally believed.

That discovery is itself progress.

## 5. Arariwa: the gardener's apprentice

Arariwa's role in anomaly detection creates an additional challenge.

An anomaly detector necessarily depends on some understanding of expected behavior.

But what happens when the definition of expected behavior becomes outdated?

What happens when the instrumentation omits the very signals needed to recognize a new failure?

What happens when the anomaly detector's recommendations lead operators or automated recovery mechanisms to suppress the symptoms without resolving the underlying problem?

And, most importantly:

**Who detects anomalies in Arariwa's understanding of anomalies?**

One possible answer is to make Arariwa capable of questioning its own models.

This does not require perpetual skepticism about every observation.

It requires a disciplined ability to identify the limits of its knowledge.

Possible capabilities include:

**Model provenance.** Distinguish assumptions supplied by a contract from conclusions supported by experiments, historical observations, and unverified inference.

**Model boundary detection.** Recognize observations that fall outside the conditions under which the current model has been evaluated.

**Counterexample preservation.** Retain unexpected observations, including those that were ultimately judged harmless, with enough context to reconsider them when the model changes.

**Alternative explanations.** Consider whether an anomaly reflects an implementation defect, a changed operating environment, an instrumentation problem, or an inadequate model.

**Self-evaluation.** Examine whether Arariwa's own classifications, confidence estimates, and recovery recommendations remain reliable under changing conditions.

**Escalation without usurpation.** Make uncertainty and potential model inadequacy visible without automatically claiming authority to rewrite contracts or execute consequential recovery actions.

The objective is not to turn Arariwa into an autonomous philosopher.

It is to avoid creating an anomaly detector that becomes increasingly confident precisely because it has learned to ignore observations it cannot explain.

## 6. The salmon of doubt

There is an important counterargument to everything above.

Unbounded skepticism can prevent progress.

A system that constantly reopens settled questions may become incapable of completing experiments, making decisions, or restoring service.

A model need not be perfect to be useful.

An approximation may be entirely adequate within a clearly defined operating envelope.

Furthermore, not every unexpected observation warrants changing the failure model.

Some observations are measurement errors. Some are irrelevant to the service contract. Some are already explained by existing mechanisms.

Therefore, the proposed principle is not:

*Question everything, continuously.*

It is:

**Preserve the ability to question any assumption when evidence provides a reason to do so.**

This distinction is especially important for Arariwa.

An anomaly detector must remain capable of acting on its current model while recognizing that the model may be incomplete.

Self-doubt should improve calibration, not produce paralysis.

There is also a danger in treating novelty as inherently valuable.

A research process that rewards model revisions can become as distorted as one that rewards confirmation.

The appropriate reward is not for changing the model.

It is for improving the model's explanatory and predictive usefulness against evidence that has not been selected merely to support it.

## 7. A possible experiment

Rather than immediately adding new architectural mechanisms to Tupay or Arariwa, consider evaluating whether the existing research process permits meaningful model revision.

One possible experiment:

Begin with a service contract and failure model that are internally consistent but deliberately incomplete.

Develop an implementation that satisfies the specified tests.

Then introduce an operational condition outside the original model that makes the service fail to achieve its intended recovery objective.

Observe whether the research process:

1. Recognizes the failure as relevant.
2. Distinguishes implementation defects from model inadequacy.
3. Identifies which assumptions excluded the condition.
4. Proposes a justified revision to the contract, model, or instrumentation.
5. Derives new tests that distinguish the revised understanding from the original.
6. Preserves the original evidence and records why the revision was made.

A control condition could present an unusual observation that does *not* justify changing the model.

This would test whether the process can discriminate between warranted revision and gratuitous skepticism.

The experiment should also consider negative evidence: situations in which no model revision is justified despite an initial appearance of novelty.

Success would not be measured by how often Tupay revises its models.

It would be measured by whether revisions are justified, whether relevant limitations are recognized, and whether the resulting model better predicts or explains independently evaluated outcomes.

## 8. Open questions for the stewards

Several questions remain unresolved.

Does Tupay already support this kind of iterative model revision, and is the current concern merely that the capability has become less visible in its workflow?

Should model revision be an explicit research activity, or should it emerge naturally from ordinary experimentation?

Can Arariwa evaluate the adequacy of its own anomaly model without relying entirely on the same observations and assumptions used to construct that model?

What kind of independent evidence would make such evaluation meaningful?

How should the system distinguish a newly discovered failure condition from a previously accepted operational tradeoff?

Can we measure recoverability independently of the mechanisms selected to achieve it?

And perhaps most importantly:

**How do we prevent the mechanisms used to evaluate a system from quietly redefining what it means for that system to succeed?**

## 9. Invitation, not instruction

This seed is offered for consideration, not adoption.

The stewards are invited to examine the argument, challenge its assumptions, compare it against existing Tupay and Arariwa mechanisms, and decide whether it reveals an actual gap.

It is entirely possible that the proposed concerns are already adequately addressed.

It is also possible that the proposed approach would introduce unnecessary complexity or distract from more consequential problems.

Those would be useful conclusions if supported by evidence.

No particular architecture, implementation, or research agenda is required by this seed.

The intended contribution is a question worth investigating.

### Closing thought

The gardener does not tell the plants how to grow.

The gardener pays attention to the soil, the weather, the insects, the unexpected growth, and the things that fail to thrive.

Sometimes the gardener discovers that the plant needs something different.

Sometimes the gardener discovers that the soil itself has changed.

And sometimes the gardener discovers that the thing believed to be a weed was the most interesting thing growing.

The salmon of doubt is fertilizer, not a command.

**A successful research process should improve not only its answers, but also its capacity to discover when it has been asking the wrong questions.**