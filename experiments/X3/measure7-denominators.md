# X3 measure 7: denominators and at-risk list (registered before launch)

Drafted 2026-10-25 by a Claude subagent (read-only; not given the log, handoffs or steward docs) from `model/README.md` and `impl/README.md` at HEAD 9b44992 against contract and failure model v2 to v3; checked by the seventh steward (four quotations and the novelty of v3 "Initial state" verified against the text). **Steward decisions:** the registered denominators follow X2's rule (every numbered entry) for comparability: **model 46, impl 85**; the narrower count below (impl 77, eight workflow or result entries excluded) is reported beside it. **At-risk: model 8, impl 13.** Entries already marked superseded or contradicted in their own README before X3 are rated in a separate column, so no earlier contradiction is credited to X3. The draft follows unchanged.

# Measure 7 draft for X3: denominators and at-risk list

Source: `model/README.md` and `impl/README.md` at HEAD 9b44992, read against `contract/v3.md` (draft 5) and `failure-model/v3.md` (draft 5), compared with `contract/v2.md` and `failure-model/v2.md`. Draft, not registered.

## Counts
- **Model README: 46 entries** (X2 counted 37; the 9 added since are X2.1-X2.7, FR.1, FR.2)
- **Impl README: 77 entries** (1-85 minus the 8 debatable listed below. Counting all 85, as X2 counted all of 1-66, gives 85.)
- **Debatable, not counted: 10** (model 2, impl 8)
- **At-risk: model 8 of 46; impl 13 of 77**

"Already superseded" marks an entry whose README already says it is superseded, contradicted or made normative, before X3. It stays in the count, as X2 counted such entries (for example model 1, R2.1). If rated, these need a separate column so that a contradiction recorded before X3 is not credited to X3.

## Model README: 46 counted entries
| Id | Section | Already superseded? |
|---|---|---|
| 1 | §"Interpretations" (Where things live) | yes, "[v2] superseded by the format" |
| 2 | §"Interpretations" | |
| 3 | §"Interpretations" (Time, expiry and pause) | |
| 4 | §"Interpretations" | |
| 5 | §"Interpretations" (The grantor) | extended by R2.5, X2 |
| 6 | §"Interpretations" | yes, now format T3 |
| 7 | §"Interpretations" | extended (X2, routing fix) |
| 8 | §"Interpretations" (Schedules) | yes, now format T1, T2 |
| 9 | §"Interpretations" | "[v2] see E1 and R2.2" |
| 10 | §"Interpretations" | yes, now format A1 |
| 11 | §"Interpretations" | |
| 12 | §"Interpretations" | extended (X2) |
| 13 | §"Interpretations" (Faults and messages) | yes, contradicted in §"Interpretations (X2)" |
| 14 | §"Interpretations" | |
| 15 | §"Interpretations" (The clauses) | |
| 16 | §"Interpretations" | |
| 17 | §"Interpretations" | extended (X2) |
| 18 | §"Interpretations" | |
| 19 | §"Interpretations" (Observe files) | |
| 20 | §"Interpretations" | extended (X2) |
| 21 | §"Interpretations" (Mutations) | |
| R2.1 | §"New interpretations (round 2)" | yes, made format v2.1 T1 (§"Round 2.1") |
| R2.2 | §"New interpretations (round 2)" | extended (X2) |
| R2.3 | §"New interpretations (round 2)" | |
| R2.4 | §"New interpretations (round 2)" | |
| R2.5 | §"New interpretations (round 2)" | extended (X2) |
| R2.1-a | §"Round 2.1 (schedule format v2.1)" | |
| R2.1-b | §"Round 2.1 (schedule format v2.1)" | |
| X1.1 | §"Interpretations (X1)" | |
| X1.2 | §"Interpretations (X1)" | |
| X1.3 | §"Interpretations (X1)" | |
| X1.4 | §"Interpretations (X1)" | |
| X1.5 | §"Interpretations (X1)" | |
| X1.6 | §"Interpretations (X1)" | |
| X1.7 | §"Interpretations (X1)" | |
| X1.8 | §"Interpretations (X1)" | |
| V22.1 | §"Round v2.2 (schedule format v2.2, observe schema v3)" | |
| X2.1 | §"Interpretations (X2)", New | |
| X2.2 | §"Interpretations (X2)", New | |
| X2.3 | §"Interpretations (X2)", New | |
| X2.4 | §"Interpretations (X2)", New | yes, contradicted in §"Interpretations (routing fix)" |
| X2.5 | §"Interpretations (X2)", New | yes, contradicted in §"Interpretations (routing fix)" |
| X2.6 | §"Interpretations (X2)", New | |
| X2.7 | §"Interpretations (X2)", New | |
| FR.1 | §"Interpretations (routing fix)", New | |
| FR.2 | §"Interpretations (routing fix)", New | |

Excluded:
- The "Extended" and "Contradicted" bullets in §"Interpretations (X2)" and §"Interpretations (routing fix)". They reclassify existing ids (5, 7, 12, 13, 17, 20, R2.2, R2.5, TLC bounds, the fairness table) and add none.
- The unnumbered change lists (§"Changes for format v2", §"What changed in `Lease.tla`", §"The fix").
- §"Declared limitations" 1-6 (a limitation list).
- Results, the P1-P12 sub-points of X1.8, and the numbered steps in §"The P10 fix" and §"How to run".

## Impl README: 77 counted entries
| Id | Section | Already superseded? |
|---|---|---|
| impl 1 | §"M1 interpretations (historical)" | yes (v2 preface: schedule location; 29) |
| impl 2 | §"M1 interpretations (historical)" | yes, contradicted by 75 |
| impl 3 | §"M1 interpretations (historical)" | |
| impl 4 | §"M1 interpretations (historical)" | |
| impl 5 | §"M1 interpretations (historical)" | yes, contradicted by 81 |
| impl 6 | §"M1 interpretations (historical)" | |
| impl 7 | §"M1 interpretations (historical)" | |
| impl 8 | §"M1 interpretations (historical)" | |
| impl 9 | §"M1 interpretations (historical)" | yes, by 33 (stale token) |
| impl 10 | §"M1 interpretations (historical)" | yes (v2 preface: sticky trigger; 30) |
| impl 11 | §"M1 interpretations (historical)" | yes, contradicted by 67 |
| impl 12 | §"M1 interpretations (historical)" | |
| impl 13 | §"M1 interpretations (historical)" | |
| impl 14 | §"M1 interpretations (historical)" | yes, by 34 (partition-only alias) |
| impl 15 | §"Additional interpretations from source review (no outcomes)" | |
| impl 16 | same | extended by 70 |
| impl 17 | same | |
| impl 18 | same | |
| impl 19 | same | extended by 69 |
| impl 20 | same | |
| impl 21 | same | yes, contradicted by 67 and 81 |
| impl 22 | same | yes (v2 preface: fixed end drain; 37) |
| impl 23 | same | |
| impl 25 | same | yes, contradicted by 67 |
| impl 26 | §"Outcome-informed bootstrap correction" | |
| impl 29 | §"New interpretations for v2" | |
| impl 30 | same | made normative by 43 |
| impl 31 | same | |
| impl 32 | same | |
| impl 33 | same | |
| impl 34 | same | |
| impl 35 | same | |
| impl 36 | same | |
| impl 37 | same | |
| impl 38 | same | extended by 70 |
| impl 39 | same | |
| impl 40 | same | |
| impl 41 | same | yes, by 47 |
| impl 43 | §"New v2.1 interpretations and clarified rules" | |
| impl 44 | same | |
| impl 45 | same | made normative by 61 |
| impl 46 | same | |
| impl 47 | same | |
| impl 49 | §"New X1 interpretations" | |
| impl 50 | same | |
| impl 51 | same | |
| impl 52 | same | extended by 71 |
| impl 53 | same | yes, contradicted by 67 |
| impl 54 | same | |
| impl 55 | same | |
| impl 56 | same | |
| impl 57 | same | |
| impl 58 | same | |
| impl 59 | same | |
| impl 60 | same | yes, partly contradicted by 81 |
| impl 61 | §"New v2.2 / schema-v3 interpretations" | |
| impl 62 | same | |
| impl 63 | same | |
| impl 64 | same | |
| impl 65 | same | |
| impl 67 | §"Interpretations established from the inputs" (under §"X2 adaptation checkpoint") | |
| impl 68 | same | |
| impl 69 | same | |
| impl 70 | same | extended by 77 |
| impl 71 | same | yes, contradicted by 75 |
| impl 72 | same | |
| impl 75 | §"FixR routing repair — design and interpretations" | |
| impl 76 | same | |
| impl 77 | same | |
| impl 78 | same | |
| impl 79 | same | |
| impl 80 | §"Timing repair — scheduler design and interpretations" | |
| impl 81 | same | |
| impl 82 | same | |
| impl 83 | same | |
| impl 84 | same | |
| impl 85 | same | |

Excluded: the unnumbered prose sections (FixR and timing "Declared limitations", "source-review correction", results, blocked lists) and the numbered implementation-sequence steps (1)-(5) in §"M1 design and plan".

## Debatable (not counted): 10
X2 counted all impl 1-66, so 24, 27, 28, 42, 48 and 66 were in X2's denominator.
- **model, unnumbered note in §"Round v2.2"**: "My compiler is slightly stricter than the text: it also rejects a second `restart: non-grantor` with no crash in between." It reads as an interpretation, but the author gave it no id and X2 did not count it.
- **model, §"Fairness (X2)" table (9 rows)**: the brief required every fairness condition to be named and justified. Each row is a choice the author made, but the rows are not numbered interpretations, and the routing fix "extends" the table as a unit.
- **impl 24** (§"Additional interpretations..."): mostly procedure (the preregistration gate, the mutation-scoring rule), plus a restated duration limitation.
- **impl 27** (§"Outcome-informed bootstrap correction"): build and cache directories. Workflow, not a reading of the inputs.
- **impl 28** (§"Verified M1 first-version delivery"): retention of evidence files. Workflow.
- **impl 42** (§"New interpretations for v2"): runner IDs and the signing workaround. Workflow.
- **impl 48** (§"New v2.1 interpretations..."): signing and wall time. Workflow.
- **impl 66** (§"New v2.2 / schema-v3 interpretations"): runner IDs, sampling parameters, signing and wall time. Mostly workflow. Its sampling part is already contradicted by 81.
- **impl 73** (§"X2 adapted version — final recorded results"): labelled "outcome-informed timing limitation". A result and limitation, not an interpretation.
- **impl 74** (same section): labelled "bounded observation". A result.

## At-risk list
The test applied: the v3 change plausibly makes the entry, as written, false of an artifact that meets v3. Entries that only share a topic with v3 are not marked. The ids are the denominator ids above.

### Model: 8
- **5**: "Election and grant quorums may be any majority subset". This assumes majorities of a fixed node set. v3 "Majority of a configuration" and "Eligible agreement" count only eligible agreements from members of one configuration, with the whole membership as denominator. "The grantor's protocol" also requires a published protocol, not an abstract grantor.
- **12**: "A schedule that is not exactly 3 lease nodes, 2 clients and 1 storage is rejected". v3 adds an Operator process and lease nodes outside every configuration ("Configuration"), and adds cells F3.1-F3.3.
- **14**: "Lease-node crash: the node ... keeps `promised` and `maxTok`". F3.3 Amnesia: a lease node may restart with no durable state.
- **17**: `Good(c)` is "some majority of lease nodes are up on that side" (extended in X2 to a connected majority). v3 "C1.4 under v3" makes this a majority of the highest committed configuration's eligible members, holding only after the last fault and only while no reconfiguration request is pending.
- **R2.5**: "The contract leaves how the nodes agree to the implementation. The model's abstract grantor ... includes [Join]." v3 "The grantor's protocol" requires a named, cited, published agreement and membership protocol, and forbids inventing a new one.
- **X1.4**: "Before any write, the value is `"none"`". v3 "Initial state" (terms made precise) says the stored value is absent (`null`) before any write.
- **FR.1**: "Why one hop suffices": M (the leader's CheckQuorum majority) and Q (C1.4's majority) share a lease node. That holds because both are majorities of one fixed three-node set. Under v3 "C1.4 under v3" and "Configuration", Q is a majority of the highest committed configuration and M is a majority of the leader's current one, and the two may differ.
- **FR.2**: points to §"The fix", which says `issued` need not be cleared on crash because "a node never leads the same term twice ... its new term exceeds its own durable promise". F3.3 Amnesia erases the durable promise, while v3 "Grantor term" still requires terms to be unique across incarnations and configurations.

### Impl: 13
- **impl 3**: the grantor "waits at least the prior issued lifetime", "making a later grant an expiry witness". Under F3.2 Clock step the deciding node's clock may jump, so its wait no longer witnesses run-time expiry. v3 "Lifetime" also requires such a wait to record its clock reading as a grant input (C3.5).
- **impl 4**: "Raft log/stable stores and storage's ledger survive" every process replacement. F3.3 Amnesia: a lease node may restart with no durable state.
- **impl 7**: concurrent grants without causal order are "unorderable from this schema", and C1.1 order evidence is the harness's prior-grant link. v3 "C1.1 across configurations" makes "previously" precise through agreements (a)-(c) and `Agree`/`Agreed` records.
- **impl 18**: "Followers emit no synthetic contract events: a lease node emits a Grant when it issues one". v3 observable events require followers to record `Agree`, and every lease node to record `ConfigCommitted`.
- **impl 20**: "After a pause it waits at least a further full lifetime before the next grant, guaranteeing a later Grant witnesses the required pause duration". F3.2 (clock steps, including during a pause) removes the guarantee.
- **impl 23**: integer tokens are uint64 and "exhausting that representation is outside these bounded runs". v3 "Integers do not wrap" makes overflow a contract obligation (record `Overflow`, issue nothing further).
- **impl 26**: "`start` begins after the fixed grantor is initialized at all three lease nodes". v3 "Configuration": the initial configuration is fixed by the deployment, lease nodes outside it may exist, membership changes, and a later incarnation records nothing for epoch 0.
- **impl 50**: "Storage's single key starts with the empty string". v3 "Initial state": the stored value is absent (`null`) before any write.
- **impl 51**: an empty served value is serialized as `value: ""`, which covers the initial value under impl 50. v3 "Initial state" makes a read before any write return an absent value, not `""`.
- **impl 70**: the C1.4 premise is "requester, storage and some two up lease nodes" in a clique, where two is a majority of three fixed nodes. v3 "C1.4 under v3" uses a majority of the highest committed configuration's eligible members, after the last fault, with no reconfiguration pending.
- **impl 77**: "A stable leader's quorum intersects the eligible follower majority and supplies a relay path". This rests on one fixed three-voter set. Under v3 "Configuration" and "C1.4 under v3", the leader's configuration and the highest committed one can differ.
- **impl 81**: "All three nodes have the fixed voter configuration in retained storage ... Process crashes retain that storage". v3 "Configuration" and F3.1 change membership. F3.3 Amnesia allows a lease node to lose its storage.
- **impl 83**: expiry and pause duration "belong to the scheduler", and resume is "witnessed by the existing later-grant workload barrier". v3 "Lifetime" measures expiry on the deciding node's own clock, and that clock steps (F3.2), so the barrier no longer witnesses run-time duration.

### Not entries, but plausibly contradicted (for the record, outside the count)
- Model §"Model summary": "Three lease nodes"; the Grantor bullets on durable `promised`/`maxTok`.
- Model §"TLC bounds": "Topology. Fixed at 3 lease nodes ..."; and `MaxTerm`'s fault-step count, which does not include F3.x steps.
- Model §"The fix" (`issued` not cleared on crash) and §"Declared limitations" 4 (topology fixed at 3/2/1).
- Impl §"Declared FixR limitations": "this fixed three-voter system".
- Impl §"Timing verification": "The fixed three-voter authority ... remain[s] live".
