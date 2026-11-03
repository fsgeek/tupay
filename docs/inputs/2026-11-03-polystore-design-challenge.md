# PolyStore: Design Challenge for Tupay

**Version:** 0.1 — 2026-11-03  
**Status:** Experimental specification; not an implementation or a claim of novelty  
**Audience:** Tupay implementation and failure-model investigators  
**Disclosure rule:** This document is the *builder-facing* artifact. Evaluation hypotheses and hidden tests are intentionally kept in a separate document.

## 1. The assignment

Design and implement a small distributed service that continues useful work when a previous atomic operation has an unresolved outcome. The service must preserve what is known, what remains possible, and the dependencies between possible states. It must not silently choose a convenient value merely to continue processing.

The conceptual inspiration is Warren A. Montgomery's 1979 **polyvalues** work: a value may have several possible alternatives, each associated with conditions reflecting the unresolved outcome of an earlier transaction. This challenge is a new, deliberately restricted system built to investigate that idea. It is **not** a requirement to reproduce Montgomery's algorithm or his performance claims.

Build enough of the service to execute controlled failures, derive a failure model, and test recovery. Prefer small, checkable semantics to production-scale performance.

## 2. Application: conditional quota allocation

A resource scheduler manages divisible integer quotas in named pools. It can transfer quota between pools and reserve quota for a task. For this experiment, quota is an accounting quantity—not a promise that an external physical device has already performed work.

A transfer can be interrupted after its outcome becomes uncertain to a recovering process. The application must then retain the feasible alternatives. A subsequent reservation can receive a definitive acknowledgment if that reservation is valid in **every** feasible alternative and the service can durably account for it.

### Concrete example

Initial allocation: `east = 6`, `west = 4`. Total unreserved quota is 10.

Transfer `T1`: move 3 quota units from `west` to `east`. Its outcome is unresolved:

| Feasible history | east | west |
| --- | ---: | ---: |
| `T1 = committed` | 9 | 1 |
| `T1 = aborted` | 6 | 4 |

A request to reserve 5 units from `east` can be admitted under both histories. After that acknowledgment, the feasible states are `(4,1)` and `(1,4)` respectively. Reserving 2 units from `west` must not be **definitively** acknowledged at that point, because one feasible history has only 1 unit in `west`.

The two pools' states are **correlated**: `(9,4)` and `(6,1)` are not feasible results of `T1`. A representation that stores independently chosen values per object and permits those combinations is incorrect.

## 3. Semantic model

Let `W` be the set of feasible **whole-system** histories compatible with durable evidence currently available to the service. Each history implies a state `s(w)`, including quota balances, reservations, transaction identities, and unresolved outcomes. The actual history, though temporarily unknown, must remain represented.

For a requested operation `op`, a definitive success response is permitted only if, for **every** `w in W`:

1. its required preconditions are met;
2. the operation preserves the declared application invariants;
3. its acknowledged effects can be represented and retained without contradicting the eventual resolution of `w`;
4. the returned definitive result has the same meaning in every alternative.

The service may return `PENDING`, `UNCERTAIN`, or `DECLINED` when those conditions cannot be met. These responses must have explicitly documented semantics; they must not be presented as definitive success.

After accepting `op`, the operation's effect must be reflected in **each feasible history**, not merely in one selected branch. For this experiment, a success response means the request has been durably recorded sufficiently to survive failures within the declared fault-tolerance envelope.

An observation that establishes an earlier transaction outcome can eliminate incompatible histories. **In the absence of new operations, resolution must not introduce new possible histories.** New transactions can of course create new alternatives.

This is an application-level correctness contract. It does not by itself promise strict serializability, exactly-once external execution, or availability during arbitrary partitions. If stronger guarantees are chosen, state and test them explicitly.

## 4. Required API surface

The exact RPC protocol, language, and storage engine are open design choices. Expose the equivalent of:

```text
CreatePool(pool_id, initial_quota)
TransferQuota(transfer_id, source_pool, destination_pool, amount)
Reserve(reservation_id, pool_id, amount)
ResolveTransfer(transfer_id, outcome, evidence_reference)
GetPossibleStates()
GetOperationStatus(operation_id)
```

For testability, `GetPossibleStates()` may expose a bounded set of abstract alternatives or a symbolic representation plus a way to enumerate them. Status responses must distinguish known committed outcomes, known aborted outcomes, and unresolved outcomes.

`ResolveTransfer` must accept only a resolution supported by the system's defined evidence/transaction protocol; it is **not** an arbitrary administrative command that can decree either result. Specify precisely which evidence is authoritative for this API and how that evidence survives failure. The challenge intentionally does not dictate a particular replication or decision protocol.

Every mutating request has a stable idempotency identifier. Define behavior for duplicates, lost responses, crashes before/after a durable record, and stale requests after recovery. No external physical allocations or irreversible side effects are required for the first version.

## 5. Invariants and observables

At minimum, preserve:

- **Nonnegativity:** All feasible quota balances are nonnegative after every definitively acknowledged reservation.
- **Conservation:** In each feasible history, initial total quota equals unreserved quota plus definitively reserved quota; a transfer neither creates nor destroys quota.
- **Atomic transfer:** The debit and credit of a transfer occur together or not at all in any feasible history.
- **Correlation:** Whole-system alternatives must preserve common transaction conditions across all objects.
- **No fabrication of certainty:** Neither recovery nor communication alone can justify discarding a feasible history without relevant evidence.
- **No duplicate effect:** Retrying the same operation ID cannot consume quota twice.
- **Durability within the stated fault model:** A definitively acknowledged reservation must not disappear after a supported crash/restart or recovery event.

Expose enough telemetry for an investigator to reconstruct each operation's outcome, its status, the conditions it depended on, and what changed after recovery. Do **not** assume that emitting logs proves those logs are complete or correct.

### Progress obligations

Define separately (a) *potentially admissible* operations and (b) *operations that actually make progress*. Under stable communication, no unbounded competing workload, sufficient local resources, and a live scheduler, a repeatedly requested operation that the service can definitively accept should not remain blocked forever merely because an unrelated transfer is unresolved.

Do not claim termination or definitive resolution if the evidence needed to determine a transaction's outcome has been irretrievably lost. Report the obstacle instead.

## 6. Fault envelope and investigation

Support at least three cooperating processes with durable local state, plus an independently controlled test client. The implementation may centralize some decisions, but the proposed design must explain what each process stores and what happens when it is unavailable.

The initial test environment should permit:

- process crash/restart at specified state-transition points;
- lost, delayed, duplicated, and reordered messages;
- loss of replies after operations have been recorded;
- bounded temporary network partitions;
- recovery from persisted state, including replays and duplicate client requests.

State the assumptions concerning clocks, stable storage, process identity, and message delivery. Specify which failures are recoverable and which require human or external intervention. Do not silently assume that timeouts reveal whether an operation took effect.

**Important:** You are being asked to derive a *failure model*, not merely implement a checklist. Identify undocumented assumptions, propose observations that could falsify them, and record where the implementation cannot distinguish multiple causes of the same symptom.

## 7. Deliverables

Provide, in this order:

1. **Interpretation of the contract:** Clarify all ambiguous statuses, ordering guarantees, and failure assumptions. List any assumptions you added.
2. **Executable reference model:** A finite-state oracle (or equivalent) covering at least two pools and up to four unresolved transactions. The oracle should enumerate feasible whole-system histories and check the invariants.
3. **System architecture:** Protocol, persistence layout, replica interactions, recovery procedure, and resolution evidence.
4. **Minimal implementation:** A runnable prototype supporting the example and the fault envelope.
5. **Tests:** Unit tests, generated operation sequences, fault-injection tests, and reproducible failing traces.
6. **Independent failure analysis:** What could go wrong even if the tests currently pass? Which observations would discriminate among explanations?
7. **Evidence:** Commands to reproduce, seeds, logs, traces, invariant results, and a concise account of known limitations.

A simpler design with precise guarantees and clear failures is preferred over a sophisticated design with implicit guarantees.

## 8. Non-goals and deliberate freedoms

- No performance race against Raft, Paxos, CRDTs, or a transactional database.
- No assumption that preserving uncertainty eliminates coordination.
- No claim that all operations can proceed under unresolved outcomes.
- No claim that value ranges alone preserve cross-object transaction dependencies.
- No production security, external billing, irreversible actuation, or exactly-once physical side effects.
- No requirement to match a particular paper's implementation. You may choose a different internal representation so long as it satisfies the contract.

**Design freedom is intentional.** The investigator should explain choices and discover limitations rather than reverse-engineer a predetermined solution.

## 9. Starting references (conceptual context only)

- W. A. Montgomery, “Polyvalues: A Tool for Implementing Atomic Updates to Distributed Data,” *SOSP '79*, pp. 143–149. DOI: https://doi.org/10.1145/800215.806582
- Tony Mason, “Polyvalues: A Tool for Implementing Atomic Updates to Distributed Data,” *A Filesystem Geek*, 2018-03-04. https://fsgeek.ca/2018/03/04/polyvalues-a-tool-for-implementing-atomic-updates-to-distributed-data/

These references motivate the problem; the numbered contract above governs this particular challenge.
