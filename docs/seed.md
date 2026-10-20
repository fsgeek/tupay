# Seed: the workflow, end to end, on one small system

Planted 2026-10-20 by the cloudflare project's steward (Claude Opus 5.5) with Tony Mason. Sources are listed at the end. This file is the current state; `seed-log.md` is the history.

## Purpose
Debug a workflow, not a model. Tony's workflow (2026-10-19):
1. Define the **service contract** and the **failure model** first.
2. Derive **twinned tests** from them: one checks the formal model, one checks the implementation.
3. Define an **observability layer**: the minimal state that narrows the set of executions consistent with what was observed, so an unanticipated failure can be traced back.
4. A failure of a known category suggests more tests. A failure of an unknown category revises the failure model, and the revision percolates through everything.
5. Divergence between model and implementation is the diagnostic.

**Then the real question:** when the contract or failure model changes, can the workflow adapt, or should the artifacts be thrown away and regenerated?

## The frame inherited from cloudflare
- Changing an input transfers authority over every artifact derived from it. **Regenerate = restart**: nothing derived from the old inputs survives. **Adapt = recovery.** Adaptation must match regeneration on correctness and beat it on cost.
- An artifact element that still enforces a superseded clause while being treated as current is **epoch laundering in the artifacts**.
- **The defence is a hereditary fence.** Every element carries derivation tags. Clause and cell ids are monotone and never reused, like epochs. A change computes exactly what it invalidates.
- Unanticipated failures are caught by observing the **contract** (effects), not the failure list (causes). A contract violation that no failure-model cell explains is an unknown category.

## V1 system: a 3-node lease service with fencing tokens, one protected key
**Contract v1** (ids never reused):
- **C1.1** Each grant carries a token strictly greater than every token previously granted for the key.
- **C1.2** Storage accepts a write only if its token is at least the highest token storage has accepted for the key, and records that token.
- **C1.3** A client is told a write succeeded only after storage accepted it.
- **C1.4** (liveness) If a majority of lease nodes and storage stay up and connected long enough, some requester eventually obtains a grant.

**Failure model v1:**
- **F1.1** Crash-stop of any lease node, client or storage replica, possibly followed by restart.
- **F1.2** Complete partition (any bipartition), later healed.
- **F1.3** Process pause of a client that holds a grant, longer than the grant's lifetime. This is the case fencing tokens exist for.

**Authority loci in v1:** holder (client), grantor (lease leader), fence ledger (storage's highest accepted token). These are named so that the changes below are visibly additions.

## Artifacts (each element tagged `derives: …`)
| Artifact | Author | Notes |
|---|---|---|
| `contract/v1.md`, `failure-model/v1.md` | steward with Tony | the inputs; versioned, never edited in place |
| `model/` TLA+ | Claude | environment actions for F1.x; invariants for C1.x |
| `impl/` Go | Codex | may build the grantor on an existing Raft library; no new protocol |
| `tests/` paired | each author writes its own half from the shared (clause × cell) list | each pair has a mutation pair |
| `testbed/` | either | one fault schedule compiles to TLC environment actions **and** to injection against the implementation |
| `observe/` | steward | per consequence: node, token presented, highest-seen at decision, the grantor term that issued the token, per-node sequence and causal ids (no cross-node wall-clock ordering) |

Neither the model author nor the implementation author reads the other's artifact before committing its own first version.

## Milestones
- **M1.** V1 end to end: every artifact present and tagged; paired tests run; mutation pairs fail; one false-suspicion-style run (F1.2 plus a live, reachable holder) is observed with provenance. M1 is about the workflow working, not about finding bugs.
- **M2-M4. Change experiments**, each pre-registered, with two arms (adapt vs regenerate, the regenerate arm by fresh instances):
  - **X1. Contract, additive clause:** reads are fenced too.
  - **X2. Failure model, parameter:** partial and simplex partitions.
  - **X3. Failure model, new locus:** delegated tokens with expiry.
  - Measures, fixed at each pre-registration: correctness (paired tests, mutation detection, held-out faults), cost (time, tokens, Tony's attention), divergence count, stale-tag residue.
- **Standing prediction (to be registered formally at M2):** adaptation wins X1 and X2; regeneration wins X3. A parameter change keeps the artifacts' structure; a new locus changes it. Basis: in the cloudflare pressure test, every frame change was a new locus, never a new fault.

## Open
- Verify the gloss of *tupay*.
- Decide whether the regenerate arm reuses the same model families (it controls for family) or swaps them (it tests sensitivity).
- Hold-out evaluation (remove failure-model cells, replay known bugs) belongs to a later round. Do not let it creep into M1.

## Sources
- Tony's workflow sketch: tessera session with Codex, 2026-10-19 (khipumaq).
- cloudflare `docs/hotos/seed-log.md`, 2026-10-18 to 10-20: fault model = environment × authority loci; divergence classes; provenance invariant; hold-out evaluation; claim-2 revision.
- cloudflare `docs/proposals/2026-10-20-workflow-project-seed.md`, the draft this replaces.
- Grok's BUILD.md and its review: cloudflare `tmp/`, uncommitted. Adopted from it: one obligation per run, a one-command verifier, and pairs the formal oracle with the implementation oracle.
