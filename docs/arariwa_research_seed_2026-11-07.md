# Arariwa: When Independent Models Stop Composing

**Research seed for Tupay — November 7, 2026**

**Status:** A deliberately provisional framing, not an endorsed architecture, formalism, or implementation specification.

## 1. The proposition

**Arariwa may be most valuable not as a detector of deviations from a known failure model, but as an instrument for finding and investigating the limits of independence among incomplete, evolving models—including the limits of its own observations and questions.**

The proposed test is not whether this vocabulary sounds coherent. It is whether it enables an investigator to notice a consequential relationship, formulate a discriminating experiment, or revisit an assumption that existing approaches missed.

Until then, regard the ontology as **wrong**.

If it yields an independently supported discovery, promote it only to **useful but still probably wrong**.

## 2. How the thread emerged

The immediate stimulus was high-speed, parallel source development by AI agents.

OpenAI and Anthropic have approached source-control scaling differently; earlier Microsoft work on Git virtual filesystems offers another relevant precedent.

The point here is **not** that any organization ignored prior work, nor that a new Git replacement is needed.

Rather, parallel development exposes a deeper issue:

* Developers and agents work from **local, incomplete world models**. Nobody possesses a canonical account of what the entire system means or how it behaves.
* Most changes are locally independent; some interact syntactically, semantically, temporally, or through hidden dependencies.
* Clean merges do not imply correct composition, and textual conflicts do not imply semantic incompatibility.
* A repository can preserve code history without preserving the assumptions, evidence, abandoned alternatives, or reasons that made a decision seem appropriate.

Two earlier threads sharpened this observation.

### Separated identity and content

In a previous distributed key-value service exploration, an object's persistent identity was separated from the location and availability of its content.

Its identity need not determine where its content lives, how it is currently resolved, or which interpretation has authority.

This service was also intended as a practical workload for testing Tupay.

### Polyvalues

Montgomery's 1979 polyvalues work provides another perspective.

Unresolved alternatives need not force all computation to stop. Operations that are safe across the relevant possibilities may proceed while reconciliation is deferred.

This is an **inspiration**, not proof that program versions form a useful semilattice or that arbitrary alternatives can be merged.

Correlated histories matter.

A third earlier thread, **prompt interference**, supplied a surprising parallel: individually useful instructions, assumptions, or contexts may cease to work as intended when composed.

The mechanisms differ from software merging, but the general failure of compositionality resembles it.

## 3. The central difficulty: local validity is not compositional validity

Informally:

$$
\operatorname{Valid}(A,C_A)
\land
\operatorname{Valid}(B,C_B)
$$

does not imply

$$
\operatorname{Valid}(A\oplus B,C)
$$

Here, \(\oplus\) means some context-dependent composition, not necessarily an algebraic join.

Neither validity nor context is assumed to have a single universal definition.

### Example: storage and indexing

A storage agent assumes an acknowledged write is durable on a leader but may not immediately appear on a replica.

An indexing agent assumes that, after acknowledgment, every subsequent read sees the write.

Their code may touch different files and pass separate tests.

The discrepancy appears in a **reliance relationship** between services, not necessarily in the diff.

It might be a real fault, a missing guarantee, or simply two uses of *acknowledged* under different contexts.

Arariwa must be able to record **unresolved**, not just compatible or incompatible.

This connects directly to Tupay's existing **dependent-services contract** concept.

That is not a new invention from this wander. Rather, it may be the already available foothold.

The question is whether the same reasoning can extend to unwritten assumptions, interacting observers, and changing objectives without merely renaming the existing mechanism.

### Local compatibility is not necessarily global compatibility

Nor is pairwise compatibility enough.

Three locally coherent constraints can be pairwise satisfiable yet jointly inconsistent:

$$
x=y,\qquad y=z,\qquad x\ne z
$$

Sheaf-like language about gluing local descriptions is one possible mathematical lens, but no theorem or practical advantage has been established merely by invoking it.

The important observation is that an apparently successful local reconciliation need not establish global coherence.

## 4. A possible expansion of Arariwa's role

Tupay already contains service contracts, failure models, dependent-service reasoning, test-case twinning, heterogeneous judges, and an ambition to recognize changes outside the declared failure model.

**Do not erase this existing design.**

The new question is whether Arariwa should also ask what the evaluative apparatus cannot currently see.

There are several different failures worth separating.

**Behavioral discrepancy:** Observed behavior departs from a declared contract.

**Compositional discrepancy:** Components satisfy local expectations but violate a reliance, invariant, or resource/timing assumption when combined.

**Coverage discrepancy:** The system changes in ways the observations or tests no longer expose. Two changes may increase the chance of failure *while decreasing the chance of detecting it*.

**Model discrepancy:** Available observations no longer fit an existing explanation—or competing explanations are valid only in different contexts.

**Question or objective drift:** The monitored system may satisfy all currently measured goals while the reason for caring about those goals has changed. A system can become excellent at answering questions that no longer matter.

These may not deserve five modules or even five primitives.

They are **candidate distinctions to test**, not a mandated taxonomy.

### The attention contract—or attention manifest

One provisional instrument is an **attention manifest**, previously called an *attention contract*.

It would record:

* What Arariwa currently observes.
* Why those measurements are considered relevant.
* Which dependencies make them informative.
* Which blind spots are already known.
* What changes would trigger reconsideration.

Calling it a contract may overpromise, so the name is negotiable.

In particular, a manifest cannot enumerate unknown blind spots by definition.

Arariwa would not be a privileged possessor of global truth.

Its inferences, detectors, choice of evidence, and attention policy are themselves local models subject to challenge.

## 5. A minimal working vocabulary—deliberately suspect

For an initial experiment, try expressing only the following concepts.

**Claim:** An assertion made by a particular actor or model; not necessarily true.

**Scope or context:** Conditions, time, version, and authority within which a claim is intended to apply.

**Reliance:** A condition one component or decision needs from another.

**Observation or evidence:** A recorded event or test result, preserved separately from interpretations of it.

**Interaction or interference hypothesis:** A proposition that composition changes some relevant property under specified conditions.

**Unresolved alternatives:** Correlated possibilities that should not be collapsed into a confident single answer.

**Discriminating experiment:** A proposed observation or intervention expected to distinguish alternatives.

Record provenance and competing interpretations.

Distinguish an assertion, evidence that reaches a model, an explanation that cites the evidence, and an independent check that the evidence supports the explanation.

Do not treat an absence of proof of compatibility as proof of incompatibility.

Evidence records may accumulate monotonically while interpretations, confidence, and authority change.

That does **not** mean executable states or beliefs necessarily have valid algebraic joins.

If a semilattice is claimed, specify its elements, order, and join, and prove the necessary properties.

### The language must admit its own inadequacy

The vocabulary must permit a response equivalent to:

> This appears consequential, but the current representation cannot express why.

Preserve the original observations so later vocabularies can reinterpret them.

The language itself must have a versioned and contestable history.

An ontology that cannot express its own limitations risks becoming a mechanism for hiding them.

## 6. The relationship to the Prime Radiant

This exploration repeatedly reconstructed aspects of the **Prime Radiant**:

* Persistent identity.
* Alternative investigative paths.
* Navigable provenance.
* Reconstruction of prior decisions.
* Revisiting earlier conclusions when new evidence appears.

**Tampu** offers a wayfinding perspective.

**Tessera** offers attestable evidence and provenance.

The separated key-value service offers a possible operational substrate.

Source control could become one client rather than the central purpose.

But none of this justifies building a universal platform first.

A narrower, useful Arariwa experiment may reveal which persistence, navigation, and attestation facilities are actually needed.

Resist an elegant architecture that cannot be falsified.

## 7. The proposed first experiment

Take a small distributed service and have independent agents modify it concurrently.

Preserve their local assumptions, tests, code changes, observations, and provenance.

Include controlled situations such as the following.

### Hidden reliance

A change to acknowledgment or visibility semantics silently invalidates a dependent index's assumption, despite a clean textual merge.

### Apparent conflict

Two apparently incompatible claims are both valid, but under different conditions.

The instrument must avoid confidently reporting a contradiction.

### Higher-order interference

Individually and pairwise acceptable changes fail when three are composed.

### Observer impairment

One change alters behavior while another reduces the effectiveness of the instrumentation intended to detect that change.

### Question drift

The implementation keeps improving a measured KPI even as the task or surrounding needs change.

Can the instrument discover why the KPI has become less informative?

### Experimental discipline

Start with explicit, reproducible cases, then progress to partially blinded and naturally arising episodes.

**Preregister expected outcomes and failure hypotheses** before giving the test cases to Arariwa.

Keep an independent adjudicator and preserve negative cases.

Do not allow post-hoc explanations to count as successful predictions.

Compare with meaningful baselines:

* Git plus CI and tests.
* Ordinary code review or static analysis.
* Independent LLM review.
* **Tupay's existing dependent-service and failure-model machinery.**

The most important comparison is the last.

**Does this framing add anything that Tupay cannot already do?**

Measure not the number of anomalies or novel questions generated, but independently supported, previously missed, consequential distinctions or experiments.

Also measure false leads, investigator effort, latency, and cost.

Evaluation metrics are themselves provisional and may distort what the system attends to.

## 8. Failure conditions and cautions

Treat the idea as weakened or refuted if:

* It merely renames existing contract checks.
* Its extra alerts are mostly invented dependencies.
* Formalizing assumptions costs more than the discoveries justify.
* It hides real failures behind a beautiful but overly narrow vocabulary.
* Existing tools match its results at lower cost.

Several fundamental questions remain unresolved.

**Independence:** What operational meaning should independence have, and relative to which properties and contexts?

**Inference:** How can Arariwa propose previously unarticulated reliance relationships without hallucinating them into authority?

**Disagreement:** How do we distinguish disagreement, missing information, genuine contradiction, and legitimate differences of jurisdiction or scope?

**Reconciliation:** When is it safe to proceed amid alternatives, and when must a coherent state or authority decision be selected?

**Self-observation:** Can the monitoring apparatus recognize degradation in its own sensitivity without presupposing the very classes of failure it is missing?

**Changing objectives:** Who may revise the objective, and how can changing purposes be investigated without simply imposing another fixed objective at a higher level?

These are not minor implementation details. Some may prove to be fundamental limitations.

## 9. Request to Tupay

Please respond as an **independent critic**, not as an implementation agent seeking to agree with this seed.

**First**, map the claims above onto Tupay's existing service contracts, dependent-services contracts, failure models, twinned tests, multi-judge review, and Arariwa design.

Identify what is already covered and where this seed is rediscovering existing work.

**Second**, identify the strongest conceptual or engineering objections, including any category errors in moving from polyvalues, semilattices, prompt interference, or local-model *gluing* to software evolution.

**Third**, propose the smallest discriminating experiment that would tell us whether the additional framing permits an important discovery beyond the existing Tupay baseline.

State in advance what success, failure, and an inconclusive result would look like.

**Finally**, tell us which distinctions in this seed should be discarded, revised, or left unresolved.

Do not produce a broad implementation roadmap unless the critical experiment establishes a reason to do so.

---

## Closing proposition

The proposed service is not an oracle for correctness, nor necessarily a replacement for source control.

It is a potentially useful instrument for noticing and testing when local models, their dependencies, and even their chosen questions stop being adequate to an evolving shared world.

**Its ontology starts wrong. The only promotion available is to usefully wrong, earned by discovery.**
