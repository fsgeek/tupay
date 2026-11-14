
# Discovering Recovery
### A research seed for Tupay
*November 13, 2026*

**Status:** Exploratory research seed, not a specification  
**Audience:** The current steward of Tupay and interested members of the ayllu  
**Origin:** A conversation exploring intelligence, continual learning, distributed-system failure, recovery, and the construction of new models

---

## 1. An invitation

This seed is offered as a collection of observations, hypotheses, and questions. It does not prescribe an architecture, research direction, or implementation.

Tupay already has a methodology, a history, and a steward responsible for its continuity. Nothing in this document takes precedence over those.

The gardener and a GPT-6 instance spent an extended conversation considering whether distributed-system recovery might benefit from a different conceptual foundation.

The conversation began with an apparently unrelated subject: a Google Research proposal for using sleep-like consolidation to improve continual learning in language models.

It eventually arrived at a question that might be worth investigating:

**Can we construct systems that discover and improve their own models of recovery, rather than merely execute recovery procedures derived from predefined failure models?**

There are several possible answers, including that the proposed approach is unnecessary, already exists, or performs worse than simpler alternatives.

All are worth discovering.

## 2. Intelligence as discovery

The conversation began by considering intelligence as the capacity to acquire, organize, and apply information in unfamiliar circumstances.

That definition raises an important distinction between improving performance on known problems and discovering previously unrecognized problems.

Recent AI mathematics research offers an example. Models have made progress on established open problems, but there is a more ambitious possibility: systems that invent mathematical structures allowing them to formulate and investigate questions that were not previously expressible.

This recalls the proposed *Einstein Test*: provide a model with scientific knowledge predating general relativity and investigate whether it can discover a new explanatory framework.

Success would not necessarily require independently reproducing Einstein's equations. A different theory that explained the observations and generated successful novel predictions could be equally interesting.

The distinction matters for Tupay.

A system might become increasingly effective at recovering from its existing catalogue of failures while remaining incapable of recognizing an unmodeled failure mechanism.

Indeed, optimizing against a fixed evaluation framework could make that problem worse.

**The objective is not merely to become better at solving familiar problems. It is to improve the ability to recognize, formulate, and investigate unfamiliar ones.**

This suggests a possible research direction: evaluate whether Tupay can discover shortcomings in its own construction methodology and develop more effective alternatives.

That is a hypothesis about an aspect of intelligence, not an assertion that Tupay must pursue recursive self-improvement.

## 3. Recovery at scale is not operation at scale

A major theme in the conversation was the distinction between steady-state operation and recovery.

A distributed system capable of serving millions of requests may be incapable of restoring service to those same clients simultaneously.

Its recovery capacity can be substantially smaller than its normal operating capacity.

Electric-grid restoration provides a useful analogy.

Following a widespread blackout, operators perform a *blackstart*. They establish limited generation, restore carefully selected loads, construct viable electrical islands, and progressively reconnect them.

The system cannot immediately accept its normal electrical load. Cold load pickup, unstable frequency, voltage constraints, insufficient reserves, and the requirements of starting additional generation all complicate recovery.

Restoration is not simply ordinary operation with fewer functioning components.

**It is a distinct operating regime with different capabilities, constraints, objectives, and authority relationships.**

Distributed computing already has important examples of this approach.

Meta's BellJar framework investigates service recoverability under restricted infrastructure availability. Its more recent work on datacenter-wide power-loss recovery addresses the bootstrapping of orchestration services and their circular dependencies.

Google's SRE literature discusses cascading failures, overload, and the need to constrain demand during recovery.

AWS has emphasized the importance of recovery mechanisms that do not depend on the availability of impaired control-plane infrastructure.

These examples establish substantial prior art.

The opportunity, if one exists, is unlikely to be inventing staged recovery. It may be constructing a more general model that explains when and how viable recovery configurations can be discovered.

## 4. Our failure models may be incomplete

Distributed-systems research contains a substantial body of work on failure behaviours that do not fit simple crash or fail-stop models.

Examples include:

- Fail-slow behaviour, in which components continue operating but cannot satisfy their normal performance expectations.
- Gray failures, in which different observers disagree about whether a component or service is functioning correctly.
- Metastable failures, in which feedback mechanisms sustain a failure after the initiating disturbance disappears.
- Authority-transfer failures, in which the system cannot safely determine, assign, or exercise the authority required for continued operation or recovery.

These are not necessarily distinct fundamental categories.

A slowdown can produce a gray failure. A response to that failure can create a feedback loop. The resulting metastability can interfere with the authority required to resolve it.

Perhaps we are observing different manifestations of a more general problem.

Classical distributed-systems theory distinguishes safety from liveness.

Recovery is related to both, but is not simply another equivalent classification.

Safety concerns prohibited behaviour. Liveness concerns eventual progress under specified assumptions. Recovery concerns the ability to reach an acceptable operating condition following a disturbance.

An important subtlety is that recovering future service does not erase a historical safety violation.

A system may also satisfy its normal operating obligations while having lost the ability to recover from a subsequent disturbance.

Thus:

**Correct operation does not establish recoverability.**

Nor does the existence of a viable configuration establish that the system can reach it from its current state.

## 5. Recovery as a relational problem

The conversation found an unexpected connection to Ayni, the Andean concept of reciprocity.

In an earlier model of human–AI relationships, each participant could determine the degree of imbalance they were willing to tolerate.

Exceeding that tolerance triggered a repair process.

Repair might establish revised expectations, obligations, or boundaries. If repair proved unsuccessful, the relationship could be terminated.

Neither repair nor termination was necessarily permanent. Relationships and their governing conditions could change over time.

The key insight was that **repair need not restore the previous relationship; it may construct a different viable relationship.**

This suggested a way to reconsider distributed-system recovery.

A service provides capabilities under conditions. Another service depends upon those capabilities and makes commitments of its own.

When conditions change, those commitments may become incompatible.

Recovery then involves discovering what participants can currently provide, identifying which obligations can still be satisfied, and constructing compatible relationships.

For software components, *willingness* is metaphorical. Unlike human participants, services express their limits through protocols, resource budgets, policies, and authority constraints.

Nevertheless, the abstraction may be useful.

A recovery process could:

- Repair a dependency.
- Reduce or suspend an obligation.
- Transfer responsibility or authority.
- Reconfigure membership or routing.
- Sever an unsustainable dependency.
- Establish a degraded but viable service.
- Progressively expand commitments as capabilities return.

These operations need not restore the original configuration.

Successful recovery may produce a different system.

### Metastability as an example

Consider a service whose effective capacity falls below the work demanded of it.

Retries, background activity, dependency contention, or recovery operations may sustain the resulting overload.

Restarting components may fail because the system continues making commitments that cannot be fulfilled in its recovering state.

One possible remedy is to change those commitments: constrain admissions, suppress work amplification, isolate dependencies, reserve resources for restoration, and progressively restore service.

This is an example rather than an exhaustive explanation of metastability.

The broader hypothesis is that **recovery requires establishing a sustainable relationship between capabilities, commitments, and the mechanisms available to change them.**

Admission control may therefore be part of the recovery protocol, not merely an optimization of normal operation.

## 6. A possible mathematical abstraction

Consider modeling a distributed system as a dynamic network of conditional commitments.

Each participant has capabilities, dependencies, resource constraints, and obligations.

Relationships determine which services are requested and provided, under which conditions, and with whose authority.

Let a system state contain four conceptual elements:

**Operational state:** Resources, queues, replicated data, processing capacity, and other physical or computational conditions.

**Commitments:** The currently established obligations and conditions among participants.

**Authority:** The assignments and transition rules determining which participants may change configuration, commitments, and operational behaviour.

**Knowledge:** Observations, hypotheses, uncertainties, and evidence concerning the other elements.

A recovery operation can change any of these.

We can then distinguish two questions.

**Is a particular configuration viable?**

Can it satisfy the required service obligations under its anticipated operating conditions?

**Is that configuration reachable?**

Can the system safely transition from its current condition to that configuration using the available resources, mechanisms, and authority?

These questions are not equivalent.

The transition itself consumes resources and may require capabilities unavailable during the outage.

A theoretically viable configuration may therefore be unreachable.

This suggests investigating a *recovery frontier*: the set of acceptable service configurations that can be reached from the current state under admissible interventions.

The frontier need not correspond to a single optimum. Different configurations may trade availability, latency, functionality, resource consumption, recovery time, and risk.

Some safety guarantees may be nonnegotiable, even when service-level obligations are revised.

The interesting question is whether recovery can expand the frontier by changing commitments, relationships, or available interventions.

### Existing mathematics

This is not yet a new mathematical theory.

Viability theory, control theory, supervisory control, dynamic reconfiguration, assume-guarantee contracts, distributed planning, and safety-engineering approaches such as STAMP already contain relevant machinery.

Before claiming novelty, Tupay should determine how much of the proposed abstraction can be expressed using existing methods.

The unexplored opportunity, if any, might concern systems that can revise the *model of permissible interventions itself*.

This leads to a distinction between three activities:

**Recovery planning:** Find an acceptable path through a known model.

**Recovery-model revision:** Change the assumptions, parameters, commitments, or structure of that model to explain observed behaviour.

**Recovery-model invention:** Discover that the existing representation cannot adequately express the relevant behaviour or intervention, and construct a different representation.

The third is the most ambitious, but we should not assume it will be necessary or superior.

## 7. Manual recovery as model-space exploration

The gardener suggested that much manual recovery may be ad hoc exploration of possible system models.

This is an empirical hypothesis worth investigating.

Consider an operator who disables retries, isolates a dependency, changes routing, reduces admission rates, or temporarily disables a feature.

Such interventions can have two simultaneous effects.

They change the system's condition.

They also reveal information about how the system behaves.

An operator who disables a dependency and observes recovery has learned something about the dependency's possible role in sustaining the failure.

But the observation may not uniquely determine the cause.

Several explanations could remain consistent with the result.

Furthermore, not all manual recovery is exploratory. Some operators execute known procedures. Some interventions are selected primarily to restore service rather than distinguish competing hypotheses.

Nevertheless, manual recovery may frequently involve implicit hypothesis generation and testing.

This suggests an opportunity to capture more than the final sequence of successful actions.

An explicit recovery investigation could preserve:

- The hypotheses considered.
- The observations supporting them.
- The expected consequences of each intervention.
- The actual consequences.
- Alternative explanations that remain viable.
- Changes to the recovery model.
- Uncertainties and unresolved questions.

Tupay's existing emphasis on contracts, test construction, and independent evaluation may offer a foundation for this.

### Existing empirical material

The gardener's recent study examined 335 hyperscaler incident postmortems.

Preliminary observations suggested that retreat-oriented actions—such as routing changes, disabling functionality, or rolling back—accounted for a substantial proportion of resolutions, approximately 45% under the working taxonomy.

A smaller practitioner-focused collection also suggested that humans directly executed most recorded resolutions.

These results have coding and sampling limitations, and their interpretation should be checked against the underlying evidence.

They do not establish that operators were exploring model space.

But they motivate investigating what humans recognized and changed when automatic recovery mechanisms proved insufficient.

## 8. Failed recovery as information

Suppose Tupay constructs a recovery model and generates an intervention.

The model predicts that suspending admissions will allow a queue to drain.

The intervention is executed.

The queue continues growing.

A recovery script has failed.

But an explicit recovery model has also produced a contradiction.

Possible explanations include unmodeled work generation, incorrect capacity assumptions, inaccurate observations, or failure to execute the intended intervention.

The discrepancy provides information about the model, although it may not identify a unique cause.

Tupay could respond by constructing diagnostic experiments capable of distinguishing competing explanations.

For example, an experiment might isolate retry traffic from internally generated work.

The important distinction is between collecting more evidence and collecting evidence specifically chosen to discriminate among models.

A failed intervention could therefore improve the next recovery attempt even when it provides no immediate restoration.

However, it is equally important to avoid retrospective rationalization.

**A model that explains every outcome after the fact, but predicts nothing reliably beforehand, has not demonstrated meaningful improvement.**

Candidate revisions should make new predictions that can be independently tested.

## 9. An experimental opportunity

There are two complementary ways to investigate this hypothesis.

### Observe human discovery

Study incident records and, where possible, recovery exercises.

Attempt to reconstruct how operators identified candidate explanations, selected interventions, and revised their understanding.

Existing postmortems may be insufficient because they often record actions and outcomes without preserving the reasoning that produced them.

Contemporaneous records or structured exercises may be more informative.

The objective would not be to assume that human operators are performing sophisticated model discovery.

It would be to determine when they are, what that process looks like, and whether recognizable patterns transfer across incidents.

### Experiment with AI discovery

Construct simulated distributed services with known underlying behaviour but incomplete recovery models.

Give an AI instance observations, limited interventions, and the opportunity to investigate failures.

Then evaluate its ability to construct models that explain observations and predict the effects of interventions.

Possible experimental conditions include fixed recovery scripts, planning with fixed models, model revision, model regeneration, and systems capable of generating new investigative methods or candidate interventions.

The purpose would not be to create a hierarchy in which the most complicated method is presumed best.

It would be to discover which capabilities contribute measurable value under which circumstances.

One particularly interesting experiment would introduce a failure mechanism absent from the instance's initial modeling vocabulary.

Could it recognize that its existing representation was inadequate?

Could it construct a new explanation?

Could that explanation predict previously unobserved behaviour?

Could it generate and validate an effective intervention?

And could the resulting discovery process transfer to a structurally different system?

These questions are related to the earlier discussion of intelligence.

**The experiment should evaluate the discovery process, not merely the eventual recovery outcome.**

### Important controls

The research should distinguish improvements attributable to the generated methodology from those attributable to the underlying model, task selection, or evaluation environment.

Independent challenge environments, held-out mechanisms, competing models, and adversarial evaluations could help.

Recovery actions should initially be restricted to simulation or otherwise appropriately authorized, bounded environments.

A generated intervention is a hypothesis, not permission to change production infrastructure.

Useful measurements might include service resumption time, data loss, preserved safety guarantees, authority correctness, predictive accuracy, diagnostic information gained, and transfer to unfamiliar mechanisms.

No single measure should automatically dominate all others.

## 10. Tupay as a generator of methods

This returns to an earlier insight about Tupay itself.

Tupay is not necessarily a single AI instance.

It may be better understood as a methodology or framework for constructing and evaluating systems.

An intriguing possibility is that Tupay could generate a set of skills appropriate to a particular instance, task, and environment.

Those skills would not be immutable.

Their effectiveness could be evaluated, and the results could inform subsequent skill construction.

This creates several opportunities for learning.

A generated skill may improve task performance.

Experience with several skills may improve the selection and construction of future skills.

Evidence accumulated across experiments may reveal deficiencies in the methodology used to generate and evaluate those skills.

This need not require modification of model weights. Effective algorithms can also change through procedures, tools, representations, and control policies.

Whether the resulting system constitutes recursive self-improvement depends on how independently it can revise its own methods and establish that those revisions represent genuine improvements.

The original discussion of AI sleep and continual learning becomes relevant here.

A consolidation process might examine accumulated experiments and discover that certain methods of model construction have become unreliable.

But consolidation could also preserve mistaken explanations or discard evidence that appears unimportant under the current framework.

Thus, the interesting question is not simply what should be remembered.

It is whether experience improves the system's ability to investigate unfamiliar circumstances.

The possibility that revision, regeneration, preservation, or other transformations may be preferable in different situations should remain open.

## 11. Some productive doubts

Several questions could undermine the proposed direction.

**Is the relational model adding anything?**

Perhaps existing control theory, assume-guarantee reasoning, and dynamic reconfiguration already capture everything useful here.

If so, the contribution may be methodological or practical rather than mathematical.

**Are commitments the correct abstraction?**

Some failures may be better explained through state dynamics, resource contention, or interactions that do not map naturally onto explicit service obligations.

A relational model should earn its usefulness through improved predictions or interventions.

**Can a system safely change its recovery contracts?**

Relaxing service obligations is not the same as relaxing safety guarantees.

The authority to renegotiate a commitment must itself be defined and protected.

A proposed repair cannot simply redefine success to conceal failure.

**Can we distinguish model discovery from increasingly elaborate curve fitting?**

A model that acquires more parameters or special cases may explain its training observations without gaining predictive capability.

Transfer to unfamiliar situations is essential evidence.

**How much model construction is actually necessary?**

A simpler recovery planner using a sufficiently expressive existing model might perform as well as a system that generates new representations.

That comparison matters.

**Can we recognize genuinely new interventions?**

A generated action may merely recombine known operations. That can still be valuable, but novelty should not be asserted without examining the prior art and the relevant action space.

**Is recovery model discovery the right goal at all?**

Perhaps a modest collection of carefully engineered recovery protocols, supported by improved anomaly detection and better simulation, will outperform a more ambitious adaptive framework.

That outcome would also be useful.

## 12. A possible first experiment

One modest experiment might provide a useful starting point.

Construct a distributed service whose normal operating configuration has sufficient resources to satisfy its contracts.

Introduce a disturbance that makes its ordinary recovery procedure ineffective.

The critical constraint should not necessarily be insufficient total capacity.

Instead, the system might be unable to reach its viable configuration because of a dependency cycle, an authority limitation, a sustaining feedback mechanism, or a recovery operation that consumes needed resources.

Give Tupay an incomplete model.

Allow it to predict recovery outcomes, propose bounded experiments, observe discrepancies, and revise its understanding.

Compare its results against a planner operating with the original fixed model.

The critical result would not be whether Tupay eventually found a successful sequence of actions.

It would be whether the experiments led it to identify a missing relationship, constraint, or intervention—and whether the resulting model made successful independent predictions.

An especially useful negative result would show that model revision added no value over fixed-model planning.

That would help establish where greater modeling complexity is warranted.

## 13. The larger possibility

Perhaps the most useful product of this research would not be a universal model of distributed-system failure.

It might instead be **a methodology for constructing useful recovery models from incomplete evidence, discovering when those models cease to be adequate, and generating better alternatives.**

That would make recovery an ongoing process of scientific inquiry.

Anomalies provide evidence of divergence from expectations.

Experiments distinguish competing explanations.

Model revisions establish new predictions.

Recovery interventions test whether those predictions lead to viable operating configurations.

And accumulated experience may improve the methods used to conduct future investigations.

Arariwa's anomaly-detection work could be relevant.

Tessera's attention to provenance and attestation could help preserve the evidentiary history of model changes.

Levadura's emphasis on independent checking could help distinguish a convincing explanation from one actually supported by the evidence.

These are possible connections, not required architectural dependencies.

The essential ambition is simpler:

**Can we improve a system's ability to discover how to recover from circumstances its designers did not anticipate?**

And can the experience of unsuccessful recovery improve that ability?

## 14. An invitation to the steward

There is no requirement to adopt any of these ideas.

Some may already be represented in Tupay. Others may conflict with its current methodology. Some may be readily explained by existing mathematics.

The research opportunity is not established merely because the proposed abstraction is appealing.

What would be useful is an investigation of whether there is a genuine gap between existing recovery models and the process humans use to discover viable recovery configurations.

In particular, it would be interesting to determine whether our current modeling approaches can express the discovery and controlled introduction of previously unmodeled recovery interventions.

If they can, perhaps the problem is one of applying established theory.

If they cannot, perhaps something remains to be invented.

Either outcome advances our understanding.

The gardener's recurring question might be expressed this way:

**What does the system need to discover that it does not yet know how to ask?**

And an equally important companion question:

**What evidence would convince us that this entire approach is mistaken?**

Those questions are offered as seeds.

What grows from them belongs to those who investigate.

---

*End of seed.*