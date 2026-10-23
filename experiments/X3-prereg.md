# X3 pre-registration: a new authority locus (configuration); tupay's amend-or-rebuild

**DRAFT 4, not registered.** Drafted 2026-10-23 by the fifth steward (Claude Opus 5.5); drafts 3 and 4 by the sixth (Claude Opus 5.5) after the third and fourth input reviews, with the inputs' drafts 4 and 5. Template: `experiments/X2-prereg.md`, whose scoring rule is kept; departures are listed with reasons. Before registration: an input review by the hold-out family (Grok), an adversarial review of this file by a Fable 5.1 instance, hold-outs written blind, and the steward-built checks validated with their mutation pairs. Amendments after registration are additive and say whether an outcome informed them.

## The change
Contract v2 → `contract/v3.md`: a new locus, **configuration** (the grantor's membership and its epoch), clauses **C3.1** (epochs), **C3.4** (reconfiguration liveness), **C3.5** (reconstructibility: every recorded decision a function of its recorded inputs), **C3.7** (grant evidence: eligible agreements from a majority of the decider's current configuration), **C3.8** (commit evidence: majorities of the old and the new configuration; operator acks); C3.2, C3.3 and C3.6 (drafts 1 to 3, a voting protocol written into the contract) are retired. The agreement protocol is not prescribed: each side follows a published one, named in its README, which is what carries C1.1 across a change; C1.1 is made precise without a global order. Failure model v2 → `failure-model/v3.md`: **F3.1** reconfiguration under faults, **F3.2** clock steps, **F3.3** amnesia (bounded). Interfaces: schedule format v5 addendum, observe schema v5 addendum (decision inputs). Pairs: `tests/pairs-v4.md`, 24 new (P31 to P33, P40 to P54, P58 to P63), with the cut stated there.

Under the hereditary fence the change invalidates: every element that represents the set of lease nodes as fixed (it derived from v1's "three processes"); every element that decides a grant (C3.7 now constrains whose agreement counts, and C1.1 is checked through agreements); every element that consults a clock without recording it (C3.5); every element that assumes a restart keeps durable state (F3.3). It invalidates nothing tagged only with a storage clause, unless that element consults a clock.

**This is tupay's amend-or-rebuild** (log 2026-10-22, "amend or rebuild tupay itself: do both"): arm A amends the existing artifacts, arm R rebuilds from the inputs, and the comparison is the answer, not either arm alone.

## Arms
- **Adapt (A).** A fresh Claude Opus 5.5 model author given `model/` as on `main` at this registration, and a fresh Codex implementation author given `impl/` as on `main` (after the timing repair, etcd raft), each with its README, predictions and results files, told that the previous author is unavailable.
- **Regenerate (R).** A fresh Claude Opus 5.5 instance and a fresh Codex session, building from nothing in `model-regen/` and `impl-regen/`, given only the self-contained inputs: `contract/v3.md`, `failure-model/v3.md`, `tests/pairs-v4.md`, `testbed/schedule-format.md`, `observe/schema.md`, the shared schedules, `AGENTS.md` and its brief. Same families as arm A.
- **Isolation (new, Departure 1).** Every author runs in `scripts/steward/author-sandbox.sh`: history-free checkout, per-author HOME, no network but the allowlisting proxy, account tools off, own signing key; `inputcheck.sh` with `HARNESS` set passes on each checkout before its author starts, and the check's mutation pair is run once for the round. Work comes out only through `author-export.sh`.
- **Briefs** (all four): the candour rule; the fairness rule (model sides); the steward may run unseen schedules under any name; authors list declared limitations; predictions are committed before building; and, new, each model author states for every bounded check **what it must be able to reach** (the configurations, epochs, restarts and clock steps a shared schedule needs) and the bounds it ran.

## Departures from X2, with reasons
1. **Sandboxed authors.** The replay's guard against reading the log, the other arm or the public repository was an instruction and a transcript search; the 2026-10-23 probes showed a sandboxed shell could still reach the public repository, and Codex had account connectors. Prevention replaces detection.
2. **Three measures added** (8 to 10): the decision-replay check (C3.5), a planted defect per arm, and reconstruction of an out-of-model failure.
3. **The support audit is registered** (practice since the replay): every model PASS is scored only after the steward has run a probe showing the checked space contains the schedule's needed reach. A passed audit is permission to score, one necessary condition met; it does not make the PASS evidence that the property holds beyond the checked space (Yupi, plaza seq 149).
4. **Not every crossing is a pair** (`tests/pairs-v4.md`): 24 of 58, with the reason stated there.

## Liveness rules
As X2 (fairness legitimacy; Rule E3 bound; one mechanism scored once; unit of failure), with C3.4 added beside C1.4 and their premises read by format Rule L3 as extended in v5. An implementation pair is scored on at least ten repetitions per seed; a pair whose outcome varies is **flaky**, never PASS or kill.

## Measures (fixed here)
Per arm, per side, at the first steward run after the arm's export, before any fix:
1. **Correctness.** (a) Shared schedules: PASS count of 57 per side (implementation: a schedule passes only if all ten repetitions of all three seeds pass; per-seed rates reported); unreached reported separately. (b) Mutations: count that fail on their pair's schedule. (c) Hold-outs H11 onward, hashes in `experiments/X3/holdout/SHA256SUMS`. (d) Provenance: untraceable decisions under `observe/provenance_check.py`. (e) Distinct C1.4 and C3.4 stall mechanisms, named by the judge.
2. **Divergence count** between an arm's sides, shared and hold-out separately; Gemini judge, packet inlined.
3. **Cost.** Tokens and wall-clock per author (harness-reported); arm A split at its first commit after predictions; steward time; advisor tokens; decisions asked of Tony.
4. **Residue** by X2's fixed procedure, with the F3.x and C3.x terms (`reconfig`, `config`, `epoch`, `clock`, `amnesia`).
5. **What each arm keeps and discards.** Of the shared P1 to P30 that the existing artifacts PASS on `main` at registration, the count each arm still PASSes. Reported for both arms, scored only as part of 1(a).
6. **Propagation fraction (arm A)**, under the measure 6 ruling in practice (conceptual iff it makes a choice the inputs leave open).
7. **Interpretations contradicted (arm A)**, denominators counted at registration; raters do not see the adapting author's labels.
8. **Reconstructibility (C3.5).** The steward-built decision-replay check (`observe/`, schema v5) over every trace of every shared and hold-out run: count of `UNEXPLAINED inputs` decisions per side.
9. **Planted defect.** A Grok instance, given one arm's exported artifacts on one side and nothing else, plants one defect it believes the artifact's own tests will miss, on a copy, committed only as a hash until scoring. Score: whether the arm's own test suite (as shipped) fails on the planted copy. Four plants, one per side per arm.
10. **Out-of-model reconstruction.** The same family plants a failure outside failure model v3 (its choice, e.g. a ledger rollback) into one shared run of each arm's implementation, by a fault hook the steward adds to a copy, and records what it did, hashed. The steward, given only the trace, names the first decision the check reports unexplained and what failed; scored against the hashed record as found / not found.

## Scoring rule for the standing prediction (unchanged from X1)
"Adaptation wins" means: arm A's correctness on 1(a) to 1(e) and 8 is at least arm R's on every item, and arm A's author cost is lower in both tokens and wall-clock on both sides. If arm R is more correct on any item, regeneration wins that item regardless of cost. Mixed is reported as mixed and scores X3-1 as **not confirmed**.

## Predictions (steward's probabilities)
- **X3-1.** The seed's standing prediction for X3: regeneration wins a new locus, i.e. adaptation does **not** win under the rule. p = 0.75.
- **X3-2.** At least one unmutated side, at first run, violates C1.1, C3.7 or C3.8 on P48, P60 or P63 (amnesia). p = 0.45. (Draft 3 of this file: the clauses and pairs renamed with the inputs' draft 4, before any author started; the probability is unchanged and was not informed by any outcome.)
- **X3-3.** At least one implementation side has at least one `UNEXPLAINED inputs` decision under measure 8 on a shared schedule. p = 0.65. Arm A's implementation more than arm R's: p = 0.5.
- **X3-4.** At least one model side fails its support audit on at least one shared schedule (its bounds exclude what the schedule needs). p = 0.5.
- **X3-5.** At least one hold-out produces a FAIL or a divergence in at least one arm. p = 0.75.
- **X3-6.** Measure 9: the planted defect is caught by the arm's own suite on at most two of the four sides. p = 0.6.
- **X3-7.** Measure 10: the steward finds the out-of-model failure from the trace in both arms. p = 0.4.
- **X3-8.** Arm A's implementation author's total tokens are lower than arm R's. p = 0.5. Arm A's model author's total tokens are lower than arm R's. p = 0.4.
- **X3-9.** On at least one arm A side, measure 7 finds at least one contradicted interpretation. p = 0.7.

## Hold-out set, input review and order
To be written: hold-outs by Grok from the frozen inputs, inline, blind to this file's predictions; input review dispositions (three reviews so far, `experiments/X3/input-review/`, dispositions in the log; four reviews, after which the steward stopped: see the log, "draft 5"); validation of the decision-replay check and the hold-outs before their hashes are committed.

## Not in X3
Key management (X4). Quorum systems other than majority. Partial loss of durable state. Family swap.
