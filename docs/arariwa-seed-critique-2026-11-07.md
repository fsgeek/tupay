# A critique of "Arariwa: When Independent Models Stop Composing" (seed of 2026-11-07)

By tupay's eleventh steward (Claude Opus 5.5), 2026-11-07, answering §9 of the seed (`docs/arariwa_research_seed_2026-11-07.md`).
**Limits of this critique:** the critic is inside tupay and is Claude, so it is not fully independent. A non-Claude critic should also be asked. Everything here about tupay cites tupay's own record, which the critic has read; it does not cite anything outside it.

## 1. What tupay already has (where the seed rediscovers)

| Seed's concept | Tupay's existing form | Where |
|---|---|---|
| Local validity ≠ compositional validity | The seed's premise: contracts plus dependency contracts; cloudflare's transfer-of-authority frame | `docs/seed.md`; D1, D2 |
| Storage/indexing example ("acknowledged" read two ways) | D1's top-ranked cells: client retry identity, state-machine dedup, **read-barrier visibility** (D52) | D1 phase 1, 2026-10-25 |
| Claim with scope | A contract clause with a monotone id; the **contract version is the scope**. A claim enforced past its version is "epoch laundering", fenced by derivation tags | seed; AGENTS.md rules 1 and 2 |
| Reliance | Dependency-contract cells (component 6 of Tony's model) | D1, D2 |
| Observation kept apart from interpretation | Append-only, stamped log; registered score vs "reading beside"; judges see packets, not hypotheses | practice, "Scoring" |
| Unresolved, not compatible/incompatible | AGENTS.md rule 6: divergence is reported **unexplained** until the evidence discriminates | AGENTS.md |
| Discriminating experiment | Mutation pairs; the support audit; per-item judge packets | practice |
| Coverage discrepancy | **Support audit**: "a PASS from a space that cannot contain the witness is no support" | replay result, 2026-10-22 |
| Observer impairment | Lived: X3's provenance check keyed records wrongly after restarts and misreported 80 decisions. An author had declared it; no steward consumed the declaration | log 2026-10-27 20:07Z |
| Model discrepancy | Lived in D2: Episode's model made recovery's two writes atomic, so F07 was invisible to it; independent models, read against the source, exposed it | D2 result, appendices |
| Attention manifest | The **assumed-impossible list** proposed 2026-10-27 (each item has an independent witness or is marked unwitnessed), with authors' declared limitations and the support audit's stated reach | log 2026-10-27 04:48Z; practice |
| Question drift | Lived: the adapt-or-regenerate question drifted to "where is the boundary" (Tony, 2026-11-01); the Mallku sign; the outside-use line | log, acceptances |

**So most of the seed restates tupay's apparatus in a new vocabulary.** That is not an objection to the seed: it means the foothold is real. But it sets a high bar, because the comparison the seed itself calls "most important" (does the framing add anything tupay cannot already do) starts with tupay already holding most of the parts.

**What tupay does *not* have:**
- (a) a record of each actor's local assumptions at the time it acted (authors' READMEs are the nearest thing, and they are free text);
- (b) any treatment of **three-way** interference: dependency cells are pairwise, component and dependency;
- (c) **continuously measured detection sensitivity**: mutation pairs and X3's plants measure it once per round, not as a running quantity;
- (d) anything for question drift beyond Tony's counsel and a dated line.

## 2. The strongest objections

1. **Polyvalues does not transfer to beliefs.** Montgomery's alternatives are the outcomes of a **specific unresolved transaction**: finite, enumerable, correlated by a shared condition, and *resolved by defined evidence*. Agents' "local world models" have none of these properties: no transaction, no enumerable alternatives, no resolution protocol. Polyvalues fits Arariwa exactly where its alternatives are **executions under a failure model**, which are finite and model-checkable, with observations that eliminate some. That is the seed's step 3 definition of Arariwa. It does not fit assumptions or intentions. Using it there is a category error.
2. **"Gluing" is constraint satisfaction, not yet sheaf theory.** `x=y, y=z, x≠z` is an unsatisfiable constraint set that is pairwise satisfiable: local consistency versus global consistency, standard in constraint solving. Sheaf language earns its place only when some computation (a cohomology class, an obstruction) finds something a solver would not. The seed already says so. I'd go further: drop the word until such a computation exists.
3. **Prompt interference is an analogy without a mechanism.** Prompts have no contract and no defined composition, so their "failure to compose" can't be checked against anything. It may inspire, but it should not shape design.
4. **Inferring unarticulated reliance is where the cost lies.** D1 and D2 enumerated reliance relationships at scale: D2 found 110 cells, of which 10 named any sealed bug's contract. D2's findings came from modelling the defences as written, not from the named reliances (D2 result, readings 1 to 2). A framing that produces *more* candidate reliances, now including unwritten ones, makes the precision problem worse unless it is paired with something that discriminates.
5. **Self-observation is answerable, but not by introspection.** "Can the apparatus recognise degradation in its own sensitivity without presupposing the classes it misses?" Not in general. But sensitivity can be **sampled**: plant faults continuously, from classes chosen by someone independent of the monitor, and track the detection rate (X3's measure 9, made continuous), with independent witnesses whose evidence does not pass through the component being checked. That measures sensitivity to the planted classes only, which is the honest limit.
6. **Question drift is not an instrument property.** Recognising that a goal stopped mattering needs a principal whose purposes changed. An instrument can flag that a KPI's correlation with its stated purpose has weakened, if the purpose is itself measured; otherwise it can only impose a higher fixed objective, which the seed rightly rejects. Leave it to the gardener's cadence and the outside-use line.
7. **The proposed experiment is circular as written.** If the people who plant the controlled cases (hidden reliance, apparent conflict, three-way interference, observer impairment, drift) also judge the instrument, the instrument is scored on recalling its designers' categories. The planted cases must come from someone who neither builds nor judges Arariwa, and natural episodes must carry most of the weight.

## 3. The smallest discriminating experiment

**Substrate:** tupay's lease service (V1 to v3 artifacts, its paired tests and its mutation pairs), which tupay knows well and Arariwa did not write.
**Changes:** about six independent agents, each with one brief and a separate checkout, each making one change that is locally valid against its own tests. A planter outside the steward's family, and outside whichever family builds the instrument, writes **sealed** briefs. These contain an unknown mix of benign changes and changes that interact (pairwise, three-way, or by impairing an observer), with the planter's answer key sealed by hash. The planter's categories are its own: the seed's five cases are *not* given to it.
**Arms, on the same merged history:**
- **A, tupay as it stands:** contracts and dependency contracts, re-derived for the merged result, paired tests, mutation pairs, the support audit, and a third-family judge on divergences.
- **B, A plus the seed's framing:** each agent records its claims, scopes and reliances when it acts, and an instrument built from the seed's minimal vocabulary consumes them, with an attention manifest and an output alphabet that includes *unresolved* and *cannot express*.

**Scored** by an independent adjudicator against the sealed key, plus any natural issue either arm raises, adjudicated blind:
- per interaction: detected, correctly characterised, or reported unresolved where the key says both claims hold under different conditions;
- false leads;
- investigator effort and cost.

**Registered in advance:**
- **Success:** B detects or correctly characterises at least one consequential interaction that A misses, with B's false leads no more than twice A's and B's cost within a stated bound.
- **Failure:** B's detections equal A's (the renaming case), or B's extra alerts are mostly adjudicated as invented reliances.
- **Inconclusive:** both arms miss most interactions (the difficulty is not the instrument's), or the arms differ on only one case. Then the experiment is rerun with more agents, rather than read.

**Not evidence, but a cheap calibration first:** give B's instrument X3's real record (authors' READMEs, the provenance check, the runs) and see whether its attention manifest would have flagged the declared provenance defect. It is retrospective and known, so it cannot count, but it costs little and would show early whether the framing can even express the case tupay actually lived.

## 4. Discard, revise, leave unresolved

- **Discard:** semilattice and sheaf language, until a computation needs them; prompt interference as a design input; the five-way taxonomy as a set of modules.
- **Revise:**
  - Collapse the five discrepancies into **three** that tupay can measure: **behavioural** (against a contract), **compositional** (against a reliance, now including three-way), and **sensitivity** (coverage and observer impairment are both "the detection probability changed", measured by sampled plants).
  - "Model discrepancy" is tupay's divergence diagnostic and stays there.
  - The **attention manifest** merges with the assumed-impossible list: every entry names an independent witness or is marked unwitnessed, and carries its measured sensitivity. "Manifest", not "contract".
- **Keep and strengthen:**
  - **unresolved** and **cannot express** as first-class outputs;
  - evidence kept apart from interpretation;
  - preserved raw observations, so later vocabularies can reinterpret them;
  - scope as a versioned id, never reused.
- **Leave unresolved, and out of Arariwa:** question or objective drift (the principal's job); a general theory of independence (operationalise it per property, as "no shared reliance on a clause or cell", and stop there); reconciliation policy beyond PolyStore's rule ("proceed only on what holds in every feasible alternative").

**One addition the seed lacks:** Arariwa's alternatives should be **executions**, not beliefs. Where an actor's assumptions matter, they enter as reliances on contract clauses with ids, so a violated assumption is a fact about an execution, not about a mind. That keeps polyvalues honest and gives the instrument something it can check.
