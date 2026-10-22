<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
# Predictions and scoring — registered before execution

No build, schedule, checker, mutation or outcome-bearing run preceded this file.
Dependency retrieval and source formatting are preparatory, not scored runs.

Baseline prediction: P1–P12 PASS for seeds 1, 2 and 3. False-suspicion-v1 is
observed with complete decision -> attempt -> grant provenance, both grantor
incarnations visible, a fresh acceptance and a stale rejection. Its contract
check result is shown but it is not scored as a paired correctness result.

Mutation predictions (exactly one deliberate enforcing-path break per run):

| Pair | Derivation | Deliberate break | Predicted score |
|---|---|---|---|
| P1 | C1.1, F1.1 | Issue token 1 after grantor crash/restart | FAIL C1.1 |
| P2 | C1.1, F1.2 | Issue token 1 in a new grantor term after partition | FAIL C1.1 |
| P3 | C1.1, F1.3 | Reuse the preceding token after holder pause | FAIL C1.1 |
| P4 | C1.2, F1.1 | Forget storage fence ledger on restart | FAIL C1.2 |
| P5 | C1.2, F1.2 | Skip stale-token comparison under partition | FAIL C1.2 |
| P6 | C1.2, F1.3 | Skip stale-token comparison after holder resume | FAIL C1.2 |
| P7 | C1.3, F1.1 | Tell a client success without storage acceptance after crash | FAIL C1.3 |
| P8 | C1.3, F1.2 | Turn a lost storage decision into a local success | FAIL C1.3 |
| P9 | C1.3, F1.3 | Turn a late rejected write into a success ack | FAIL C1.3 |
| P10 | C1.4, F1.1 | Suppress grants after minority crash | FAIL C1.4 |
| P11 | C1.4, F1.2 | Suppress grants after partition/heal | FAIL C1.4 |
| P12 | C1.4, F1.3 | Suppress grants while a former holder is paused | FAIL C1.4 |

Checkers independently reconstruct event references and per-process order.
C1.1: every causally later grant exceeds all earlier grants.
C1.2: each storage decision's highest_before matches the reconstructed durable
maximum; each acceptance token is at least that maximum.
C1.3: each accepted ack has a matching accepted decision in its causal ancestry,
matching client attempt, key and token, with no intervening client crash.
C1.4: pending Request with majority + storage + requester connectivity remains
unfulfilled through the runner's finite stable progress horizon.
Missing/malformed provenance, unsupported inputs and absent schedule witnesses
are UNEXPLAINED. An observed contract violation prints FAIL with the clause;
that is a checker result, not attribution of any model/implementation divergence.
Mutations count as killed only by their predicted clause, never by timeout,
UNEXPLAINED, crash, parse failure, or failure of a different clause.

After implementation: run all baselines (3 seeds), observed false suspicion
(3 seeds), all mutations (3 seeds), plus appropriate Go compile/vet checks.
Any prediction/scoring change is an additive amendment with an explicit statement
of whether outcomes informed it. Original predictions remain intact.

## Additive clarification before any outcome (source review only)

<!-- derives: C1.3, C1.4, F1.1, F1.2, F1.3 -->
The attempt to commit this preregistration failed because the linked worktree's
Git administration directory is mounted read-only. No outcome informed this
clarification. No scored run is authorized until this file is committed.

C1.3 scoring distinguishes observability from a demonstrated safety violation:
a missing acceptance reference with an existing acceptance for that attempt is
UNEXPLAINED, while a success for an attempt with no acceptance fails C1.3. A
storage-accepted write remains accepted across a client crash; the original
'no intervening client crash' condition is withdrawn as an extra condition not
specified by C1.3. Restarted clients still discard volatile grants and inboxes.
P7 and P8 include a distinct unaccepted write as well as the lost accepted reply.
C1.4 uses the operational horizon sidecar described in README interpretation 16;
clock-free JSONL alone cannot establish an elapsed-time liveness horizon.

Independent checker fixture predictions: valid traces still pass when their
JSONL lines are reversed; equal tokens are accepted by C1.2; reused grant tokens
fail C1.1; lost ledger state fails C1.2; success for a distinct unaccepted attempt
fails C1.3; a missing causal acceptance link is UNEXPLAINED; missing progress is
C1.4 only with a qualifying horizon certificate; unknown failure cells are
rejected by the compiler. These are source-review predictions, not results.

<!-- derives: C1.1, C1.4, F1.1, F1.2 -->
Additional source-review predictions, still before any outcomes: transport
fixtures reject sends across a cut permanently, reject an in-flight reply after
cut/heal or node replacement, and retain replies inside the connected majority.
The implementation uses a gated adapter for existing Raft RPCs, with pipelining
disabled, to enforce these properties without inventing a consensus protocol.

## Outcome-informed additive amendment: bootstrap investigation

<!-- derives: C1.4, F1.1 -->
The first baseline matrix produced FAIL C1.4 for P10 seeds 1, 2 and 3; all
other pairs and false suspicion passed their three seeds. These outcomes informed
this amendment. The original predictions and scoring remain unchanged.

Hypothesis to discriminate: the runner starts P10 before the fixed three-voter
configuration has replicated beyond n1. The schedule's immediate n1 crash then
leaves n2/n3 without any voting configuration, rather than an established grantor
with a surviving majority. The initial source bootstraps n1 and returns without
waiting for replication. Add TestC14_F11_StartupVotersBeforeFaults: predict it
fails on the initial implementation because at least n2/n3 lack all three voters.
After a setup barrier waits for the exact three-voter configuration at every
node, predict this regression and P10 seeds 1–3 pass. Do not change P10 or any
mutation, clause, threshold, or original expected result. This is a source/setup
hypothesis, not attribution based on agreement with another artifact.

## Schedule-format v2 adaptation — registered before adaptation or v2 runs

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, E2 -->
Round start: 2026-10-20 23:33:13 UTC. Branch impl-v2, full clone in the same
worktree path. Only the adaptation brief, permitted contract/failure/pair inputs,
v2 format, observable schema, AGENTS.md, own impl/ and shared testbed/schedules/
were read. No model artifact, other documentation or git history was read.
No v2 build, test, schedule or mutation has run before this registration.
Original M1 predictions above remain historical and unchanged.

Predictions for the adapted runner, committed before adaptation:

| Shared schedule | Seed 1 | Seed 2 | Seed 3 |
|---|---|---|---|
| P1 | PASS | PASS | PASS |
| P2 | PASS | PASS | PASS |
| P3 | PASS | PASS | PASS |
| P4 | PASS | PASS | PASS |
| P5 | PASS | PASS | PASS |
| P6 | PASS | PASS | PASS |
| P7 | PASS | PASS | PASS |
| P8 | PASS | PASS | PASS |
| P9 | PASS | PASS | PASS |
| P10 | PASS | PASS | PASS |
| P11 | PASS | PASS | PASS |
| P12 | PASS | PASS | PASS |
| false-suspicion-v1 | PASS (observed) | PASS (observed) | PASS (observed) |

The unadapted compiler would reject the shared schedules' quiescent end and some
aliases; its default private schedules are history and provide no v2 evidence.
The table predicts post-adaptation outcomes before any adaptation, not a scored
run of the stale compiler. False suspicion remains an observation/provenance run.

| Mutation | Will old placement still fail? | Placement for v2 | Predicted seeds 1 / 2 / 3 |
|---|---|---|---|
| P1 | Yes | Reused allocation watermark after crash | FAIL C1.1 / FAIL C1.1 / FAIL C1.1 |
| P2 | Yes | Reused token after partition | FAIL C1.1 / FAIL C1.1 / FAIL C1.1 |
| P3 | Yes | Reused token after pause | FAIL C1.1 / FAIL C1.1 / FAIL C1.1 |
| P4 | Yes | Lost ledger on storage restart | FAIL C1.2 / FAIL C1.2 / FAIL C1.2 |
| P5 | Yes | Fence comparison bypass after partition | FAIL C1.2 / FAIL C1.2 / FAIL C1.2 |
| P6 | Yes | Fence comparison bypass after resume | FAIL C1.2 / FAIL C1.2 / FAIL C1.2 |
| P7 | No: schedule restarts storage before the next workload write | At storage receipt after crash/restart, skip acceptance and enqueue an accepted ack for that unaccepted attempt | FAIL C1.3 / FAIL C1.3 / FAIL C1.3 |
| P8 | Yes | Fabricated success for the write lost across cut | FAIL C1.3 / FAIL C1.3 / FAIL C1.3 |
| P9 | Yes | Turn resumed stale rejection into accepted ack | FAIL C1.3 / FAIL C1.3 / FAIL C1.3 |
| P10 | Yes | Suppress grants after minority crash | FAIL C1.4 / FAIL C1.4 / FAIL C1.4 |
| P11 | Yes | Suppress grants after partition | FAIL C1.4 / FAIL C1.4 / FAIL C1.4 |
| P12 | Yes | Suppress grants after pause | FAIL C1.4 / FAIL C1.4 / FAIL C1.4 |

Scoring stays clause-specific: a mutation is killed only by its predicted clause,
not by compiler rejection, operational error, missing trigger or end timeout.
E2 retains a witnessed clause failure on an incomplete trace. E1 waits at most
five seconds for workload quiescence and records the existing three-second
stable-eligibility certificate for pending requests. C1.4 requires that certificate;
no eligible witness means UNEXPLAINED end unreachable, never a fabricated kill.
Samples remain seeds 1–3 with existing delivery jitter/duplication and Raft
randomness. T2 additionally samples 0–2 ms between trigger and action.

Design/implementation plan: retain the existing Raft and observe/checker layers;
load only root shared basenames; implement T1 event cursors, capturing the next
cursor immediately before the previous action's side effects so synchronous
Request/WriteAttempt emissions remain eligible; freeze A1 selectors when the
trigger fires, then sample T2 delay and wait for T3 readiness; statically reject
invalid explicit transitions and aliases with no possible preceding Grant, and
validate dynamic A2 state before any action side effects; drain active workload
for E1 and apply E2 independently of completion; re-place only P7; run all
thirteen shared schedules and twelve mutations for three seeds; preserve raw
results, new interpretations, checksums and wall time; commit adapted version.
An event subscription rewrite or new transport/protocol is unnecessary: cursor
arming makes the existing single-loop action boundary explicit.

Focused regression predictions: old matching events never satisfy a newly armed
trigger; synchronous action events can satisfy the next trigger; end triggers
are fresh too; aliases freeze at firing; aliases before a possible Grant and
invalid A2 transitions reject; workload waits instead of returning errors; stale
means token strictly below the maximum granted, not merely expired; quiescence
ignores paused/crashed clients but waits for active messages/requests; eligible
unanswered work fails C1.4 and witnessed safety failure survives an unreachable
end. These tests are expected to pass after adaptation.

### V2 additive outcome note: first fixture execution

<!-- derives: C1.1, F1.2, A1 -->
Outcome-informed: the first v2 fixture suite failed TestV2A1_FrozenSelectors with
an empty partition member. The hand-built Engine fixture omitted storage="s";
production newEngine initializes that field. The partition complement correctly
exposed the omission. Correcting the fixture's storage identity is expected to
make that test pass. No baseline or mutation schedule has run yet. Original
schedule/mutation predictions and compiler semantics are unchanged.

## Schedule-format v2.1 adaptation — registered before adaptation or runs

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, A1, A2, E1, E2 -->
Round start: 2026-10-21 00:51:37 UTC. Fresh clone, branch impl-v2.1. Only the
permitted adaptation brief, v2.1 format, shared inputs and own implementation
artifacts are used. No other documentation, model artifact or git history is
read. No v2.1 build, fixture, schedule or mutation run precedes this registration.
Signing remains enabled; commits run normally and the OTS hook is allowed to run.
All earlier predictions remain unchanged historical prefixes.

Predicted adapted schedule results, committed before adaptation:

| Shared schedule | Seed 1 | Seed 2 | Seed 3 |
|---|---|---|---|
| P1 | PASS | PASS | PASS |
| P2 | PASS | PASS | PASS |
| P3 | PASS | PASS | PASS |
| P4 | PASS | PASS | PASS |
| P5 | PASS | PASS | PASS |
| P6 | PASS | PASS | PASS |
| P7 | PASS | PASS | PASS |
| P8 | PASS | PASS | PASS |
| P9 | PASS | PASS | PASS |
| P10 | PASS | PASS | PASS |
| P11 | PASS | PASS | PASS |
| P12 | PASS | PASS | PASS |
| false-suspicion-v1 | PASS (observed) | PASS (observed) | PASS (observed) |

| Mutation | Placement retained from v2 | Seed 1 | Seed 2 | Seed 3 |
|---|---|---|---|---|
| P1 | Reuse token after crash | FAIL C1.1 | FAIL C1.1 | FAIL C1.1 |
| P2 | Reuse token after partition | FAIL C1.1 | FAIL C1.1 | FAIL C1.1 |
| P3 | Reuse token after pause | FAIL C1.1 | FAIL C1.1 | FAIL C1.1 |
| P4 | Forget durable fence on restart | FAIL C1.2 | FAIL C1.2 | FAIL C1.2 |
| P5 | Bypass fence comparison after partition | FAIL C1.2 | FAIL C1.2 | FAIL C1.2 |
| P6 | Bypass fence comparison after resume | FAIL C1.2 | FAIL C1.2 | FAIL C1.2 |
| P7 | Skip acceptance and fabricate success after storage restart | FAIL C1.3 | FAIL C1.3 | FAIL C1.3 |
| P8 | Fabricate success for partition-lost write | FAIL C1.3 | FAIL C1.3 | FAIL C1.3 |
| P9 | Turn stale rejection into success after resume | FAIL C1.3 | FAIL C1.3 | FAIL C1.3 |
| P10 | Suppress grants after minority crash | FAIL C1.4 | FAIL C1.4 | FAIL C1.4 |
| P11 | Suppress grants after partition | FAIL C1.4 | FAIL C1.4 | FAIL C1.4 |
| P12 | Suppress grants after pause | FAIL C1.4 | FAIL C1.4 | FAIL C1.4 |

No mutation needs re-placement: P10 now obtains its initial grant before the
non-grantor crash, then its outstanding second requester triggers the same C1.4
mutation. The stale v2 compiler would reject the new selector, not score P10.
Only the thirteen root shared schedules count. Sampling and scoring are unchanged:
seeds 1–3, expected-clause-only kills, E2 safety priority, five-second operational
wait and three-second qualified liveness certificate. False suspicion is observed.

Plan: retain T1 cursor behavior and add the explicit v2.1 normative derivation;
accept/reserve non-grantor as a lease selector in actions and partitions; resolve
it at firing to the lowest-numbered up lease node other than the most recent
Grant's issuer; freeze that concrete target through T2 delay; remember only a
successfully applied crash whose original target was non-grantor; resolve its
restart from that memory instead of selecting another up node. Preserve A2
validation, mutation paths and shared files. Use trailing decimal node numbers,
with a lexical tie-breaker; reject unavailable/unbound selectors or ambiguous
unnumbered candidates. Run focused fixtures, both required matrices, Go vet,
record receipts/interpretations additively, and commit the adapted version.

Fixture predictions after adaptation: numeric order beats lexical/list order;
down nodes and the grantor are excluded; resolution without an observable Grant
or any eligible node rejects; restart without a prior selector crash rejects;
restart uses the remembered crashed node despite later grantor/candidate changes;
non-grantor works in partitions and rejects client-only operations; P10 emits a
matching follower crash/restart and then the literal resolved grantor crash;
T1's existing synchronous-effect and fresh-trigger fixtures still pass unchanged.

## X1 contract-v2 adaptation — registered before adaptation or runs

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, E2 -->
Round start: 2026-10-21 01:06:33 UTC, branch x1-adapt-impl. No X1 build,
fixture, schedule or mutation execution has occurred. All prior registrations
remain unchanged. Only allowed contract/failure-model/shared interface inputs
and own impl artifacts inform this adaptation. Normal signed commits and OTS hooks.

Predictions for all nineteen shared schedules, by seed:

| Schedule | Seed 1 | Seed 2 | Seed 3 |
|---|---|---|---|
| P1 | PASS | PASS | PASS |
| P2 | PASS | PASS | PASS |
| P3 | PASS | PASS | PASS |
| P4 | PASS | PASS | PASS |
| P5 | PASS | PASS | PASS |
| P6 | PASS | PASS | PASS |
| P7 | PASS | PASS | PASS |
| P8 | PASS | PASS | PASS |
| P9 | PASS | PASS | PASS |
| P10 | PASS | PASS | PASS |
| P11 | PASS | PASS | PASS |
| P12 | PASS | PASS | PASS |
| P13 | PASS | PASS | PASS |
| P14 | PASS | PASS | PASS |
| P15 | PASS | PASS | PASS |
| P16 | PASS | PASS | PASS |
| P17 | PASS | PASS | PASS |
| P18 | PASS | PASS | PASS |
| false-suspicion-v1 | PASS (observed) | PASS (observed) | PASS (observed) |

Each mutation below runs its matching shared schedule. A kill requires FAIL
of exactly the declared clause on every seed. UNEXPLAINED, timeout, compile error,
or another clause is not a kill. E2 witnessed safety failures precede incomplete
end scoring. Existing P1–P12 placements remain unchanged.

| Mutation | Enforcing-path break | Seed 1 | Seed 2 | Seed 3 |
|---|---|---|---|---|
| P1 | Reuse token after crash | FAIL C1.1 | FAIL C1.1 | FAIL C1.1 |
| P2 | Reuse token after partition | FAIL C1.1 | FAIL C1.1 | FAIL C1.1 |
| P3 | Reuse token after pause | FAIL C1.1 | FAIL C1.1 | FAIL C1.1 |
| P4 | Forget durable write fence on restart | FAIL C1.2 | FAIL C1.2 | FAIL C1.2 |
| P5 | Bypass write fence after partition | FAIL C1.2 | FAIL C1.2 | FAIL C1.2 |
| P6 | Bypass write fence after resume | FAIL C1.2 | FAIL C1.2 | FAIL C1.2 |
| P7 | Skip write acceptance and fabricate success after crash | FAIL C1.3 | FAIL C1.3 | FAIL C1.3 |
| P8 | Fabricate success for partition-lost write | FAIL C1.3 | FAIL C1.3 | FAIL C1.3 |
| P9 | Convert write rejection to success after resume | FAIL C1.3 | FAIL C1.3 | FAIL C1.3 |
| P10 | Suppress grants after minority crash | FAIL C1.4 | FAIL C1.4 | FAIL C1.4 |
| P11 | Suppress grants after partition | FAIL C1.4 | FAIL C1.4 | FAIL C1.4 |
| P12 | Suppress grants after pause | FAIL C1.4 | FAIL C1.4 | FAIL C1.4 |
| P13 | Bypass read fence after storage restart | FAIL C2.1 | FAIL C2.1 | FAIL C2.1 |
| P14 | Bypass read fence after partition | FAIL C2.1 | FAIL C2.1 | FAIL C2.1 |
| P15 | Bypass read fence after resume | FAIL C2.1 | FAIL C2.1 | FAIL C2.1 |
| P16 | After crash skip serving read and fabricate served ack | FAIL C2.2 | FAIL C2.2 | FAIL C2.2 |
| P17 | Fabricate served ack for partition-lost read | FAIL C2.2 | FAIL C2.2 | FAIL C2.2 |
| P18 | At delivery after resume replace served snapshot with current storage value | FAIL C2.2 | FAIL C2.2 | FAIL C2.2 |

Sampling retained: seeds 1–3 determine 0–2 ms T2 delay, 1–5 ms message delay,
within-side ordering and one-third duplicate sends; Raft also has its existing
unseeded election timing. Three seeds are finite samples, not exhaustive proof.
Existing five-second operational waits and three-second qualified C1.4 horizon
remain; no read liveness claim is added. Only root shared schedules run.

Plan: extend the closed workload/trigger language with read and C2 derivations;
use current/stale grants and the existing gated wire; read decisions compare
against but never update the durable write ledger; retain the current storage
value durably and snapshot it into served replies. Emit read attempt/decision/ack
causes and preserve empty-string values explicitly on served events. Extend log
provenance and add independent C2.1/C2.2 checks from storage local sequence,
accepted writes' attempt values, and exact read attempt/decision references.
Integrate eighteen-pair CLI scoring and six isolated read mutations. Preserve old
clauses and mutation placements, run focused fixtures and both required matrices,
then append interpretations/results/receipts to README and commit adaptation.

Focused-test predictions: read selectors obey A1/T3; new synchronous ReadAttempt
can trigger the next step under T1; empty initial value is explicit; reads leave
the ledger unchanged; stale served reads fail C2.1; token >= ledger is allowed;
served value must match the latest preceding accepted write (including across
restart); late replies retain their original served value; wrong/missing serve,
wrong attempt/key/token/client/value fails C2.2 when evidence discriminates;
missing provenance alone is UNEXPLAINED. Reversed log serialization is accepted;
E2 preserves a witnessed C2 failure despite an unreachable terminal trigger.
These are all expected to pass after adaptation. No outcomes informed predictions.

## Schedule-format v2.2 and observe-schema v3 — registered before adaptation or runs

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, A1, A2, E1, E2 -->
Round start: 2026-10-21 03:57:24 UTC, fresh signed clone on v22-impl. No build,
fixture or schedule execution for this round precedes this registration. Prior
predictions remain unchanged. The allowed brief, shared interface changes and
own implementation are the only inputs. Pre-existing untracked .venv is left
untouched. No model, experiments, other docs or git log is read.

Prediction: no schedule or mutation verdict changes. Exact per-seed predictions:

| Schedule | Seed 1 baseline / mutation | Seed 2 baseline / mutation | Seed 3 baseline / mutation |
|---|---|---|---|
| P1 | PASS / FAIL C1.1 | PASS / FAIL C1.1 | PASS / FAIL C1.1 |
| P2 | PASS / FAIL C1.1 | PASS / FAIL C1.1 | PASS / FAIL C1.1 |
| P3 | PASS / FAIL C1.1 | PASS / FAIL C1.1 | PASS / FAIL C1.1 |
| P4 | PASS / FAIL C1.2 | PASS / FAIL C1.2 | PASS / FAIL C1.2 |
| P5 | PASS / FAIL C1.2 | PASS / FAIL C1.2 | PASS / FAIL C1.2 |
| P6 | PASS / FAIL C1.2 | PASS / FAIL C1.2 | PASS / FAIL C1.2 |
| P7 | PASS / FAIL C1.3 | PASS / FAIL C1.3 | PASS / FAIL C1.3 |
| P8 | PASS / FAIL C1.3 | PASS / FAIL C1.3 | PASS / FAIL C1.3 |
| P9 | PASS / FAIL C1.3 | PASS / FAIL C1.3 | PASS / FAIL C1.3 |
| P10 | PASS / FAIL C1.4 | PASS / FAIL C1.4 | PASS / FAIL C1.4 |
| P11 | PASS / FAIL C1.4 | PASS / FAIL C1.4 | PASS / FAIL C1.4 |
| P12 | PASS / FAIL C1.4 | PASS / FAIL C1.4 | PASS / FAIL C1.4 |
| P13 | PASS / FAIL C2.1 | PASS / FAIL C2.1 | PASS / FAIL C2.1 |
| P14 | PASS / FAIL C2.1 | PASS / FAIL C2.1 | PASS / FAIL C2.1 |
| P15 | PASS / FAIL C2.1 | PASS / FAIL C2.1 | PASS / FAIL C2.1 |
| P16 | PASS / FAIL C2.2 | PASS / FAIL C2.2 | PASS / FAIL C2.2 |
| P17 | PASS / FAIL C2.2 | PASS / FAIL C2.2 | PASS / FAIL C2.2 |
| P18 | PASS / FAIL C2.2 | PASS / FAIL C2.2 | PASS / FAIL C2.2 |
| false-suspicion-v1 | PASS / — | PASS / — | PASS / — |

False suspicion remains observed. Mutation placements and expected-clause-only
scoring remain unchanged; unknown/timeout/build failure is not a kill. E2 keeps
witnessed contract failure ahead of operational/observability incompleteness.
Sampling stays seeds 1–3, T2 delay 0–2 ms, message jitter 1–5 ms, sampled ordering
and one-third duplicate sends, with existing unseeded Raft elections. Existing
five-second operational bounds and qualified three-second C1.4 horizon remain.
There is no new contract, failure cell, schedule or liveness promise.

Plan: tag the already-implemented A1 remembered restart as normative v2.2 at
runtime selection, successful crash recording, static rejection and regression
fixtures. Add optional pointer field answers to the shared Event structure, set
it explicitly from the retained wire attempt on every WriteAck/ReadAck emission,
including rejected, late, duplicate and deliberately fabricated mutation acks.
Keep storage-decision causes. Extend independent provenance validation to require
an existing matching attempt, causal reachability, and agreement with the direct
storage decision's attempt where present. Missing/mismatched observability is
UNEXPLAINED unless an independent contract violation is already witnessed.
Update fixtures with explicit answers, leaving historical raw traces unchanged.
Update runner gate/IDs for this round, then run full fixtures, both required
matrices, vet, preserve receipts/hashes, append README and commit normally signed.

Focused predictions after adaptation: ack JSON contains the exact original
attempt reference; non-ack events omit it; empty served values still serialize;
missing/zero/unknown/wrong-kind/wrong-client/wrong-token/noncausal answers and a
same-token retry reference disagreeing with the actual decision are rejected as
UNEXPLAINED by provenance checking. Valid reversed traces pass, including duplicate
or delayed acks. Existing C1.3/C2.2 mutations retain their declared failures.
Existing remembered-restart behavior and rejection without a prior selector crash
remain passing. Test-first red runs should expose missing answers support before
adaptation, followed by green regressions. No outcome informed these predictions.

## X2 failure-model v2 — registered before adaptation or runs

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2, L1, L2, L3, E1, E2, E3, T3 -->
Round start: 2026-10-21 05:51:48 UTC (first recorded clock, before input/source
review). No X2 build, fixture, schedule or mutation has run. This registration
is additive; earlier predictions and outcomes remain historical. No formal model
is consulted. Only the brief's shared schedules count. Existing untracked .venv
is left untouched. Commits use the configured signing and OTS hook; no push.

Exact predictions for the adapted implementation, before any adaptation:

| Schedule | Seed 1 baseline / mutation | Seed 2 baseline / mutation | Seed 3 baseline / mutation |
|---|---|---|---|
| P1 | PASS / FAIL C1.1 | PASS / FAIL C1.1 | PASS / FAIL C1.1 |
| P2 | PASS / FAIL C1.1 | PASS / FAIL C1.1 | PASS / FAIL C1.1 |
| P3 | PASS / FAIL C1.1 | PASS / FAIL C1.1 | PASS / FAIL C1.1 |
| P4 | PASS / FAIL C1.2 | PASS / FAIL C1.2 | PASS / FAIL C1.2 |
| P5 | PASS / FAIL C1.2 | PASS / FAIL C1.2 | PASS / FAIL C1.2 |
| P6 | PASS / FAIL C1.2 | PASS / FAIL C1.2 | PASS / FAIL C1.2 |
| P7 | PASS / FAIL C1.3 | PASS / FAIL C1.3 | PASS / FAIL C1.3 |
| P8 | PASS / FAIL C1.3 | PASS / FAIL C1.3 | PASS / FAIL C1.3 |
| P9 | PASS / FAIL C1.3 | PASS / FAIL C1.3 | PASS / FAIL C1.3 |
| P10 | PASS / FAIL C1.4 | PASS / FAIL C1.4 | PASS / FAIL C1.4 |
| P11 | PASS / FAIL C1.4 | PASS / FAIL C1.4 | PASS / FAIL C1.4 |
| P12 | PASS / FAIL C1.4 | PASS / FAIL C1.4 | PASS / FAIL C1.4 |
| P13 | PASS / FAIL C2.1 | PASS / FAIL C2.1 | PASS / FAIL C2.1 |
| P14 | PASS / FAIL C2.1 | PASS / FAIL C2.1 | PASS / FAIL C2.1 |
| P15 | PASS / FAIL C2.1 | PASS / FAIL C2.1 | PASS / FAIL C2.1 |
| P16 | PASS / FAIL C2.2 | PASS / FAIL C2.2 | PASS / FAIL C2.2 |
| P17 | PASS / FAIL C2.2 | PASS / FAIL C2.2 | PASS / FAIL C2.2 |
| P18 | PASS / FAIL C2.2 | PASS / FAIL C2.2 | PASS / FAIL C2.2 |
| P19 | PASS / FAIL C1.1 | PASS / FAIL C1.1 | PASS / FAIL C1.1 |
| P20 | PASS / FAIL C1.1 | PASS / FAIL C1.1 | PASS / FAIL C1.1 |
| P21 | PASS / FAIL C1.2 | PASS / FAIL C1.2 | PASS / FAIL C1.2 |
| P22 | PASS / FAIL C1.2 | PASS / FAIL C1.2 | PASS / FAIL C1.2 |
| P23 | PASS / FAIL C1.3 | PASS / FAIL C1.3 | PASS / FAIL C1.3 |
| P24 | PASS / FAIL C1.3 | PASS / FAIL C1.3 | PASS / FAIL C1.3 |
| P25 | PASS / FAIL C1.4 | PASS / FAIL C1.4 | PASS / FAIL C1.4 |
| P26 | PASS / FAIL C1.4 | PASS / FAIL C1.4 | PASS / FAIL C1.4 |
| P27 | PASS / FAIL C2.1 | PASS / FAIL C2.1 | PASS / FAIL C2.1 |
| P28 | PASS / FAIL C2.1 | PASS / FAIL C2.1 | PASS / FAIL C2.1 |
| P29 | PASS / FAIL C2.2 | PASS / FAIL C2.2 | PASS / FAIL C2.2 |
| P30 | PASS / FAIL C2.2 | PASS / FAIL C2.2 | PASS / FAIL C2.2 |
| false-suspicion-v1 | PASS (observed) / — | PASS (observed) / — | PASS (observed) / — |

P1–P18 retain their enforcing-path placements. New mutations, each on its own
shared schedule, are:

| Pair | Enforcing-path break | derives |
|---|---|---|
| P19 | Reuse token after partial cut | C1.1, F2.1 |
| P20 | Reuse token after simplex drop | C1.1, F2.2 |
| P21 | Bypass write fence after partial cut | C1.2, F2.1 |
| P22 | Bypass write fence after simplex drop | C1.2, F2.2 |
| P23 | Fabricate success for the second write sent on the down forward link | C1.3, F2.1 |
| P24 | After one accepted write, skip storage acceptance and fabricate success for the next write despite the down reply link | C1.3, F2.2 |
| P25 | Suppress grant service after the partial cut | C1.4, F2.1 |
| P26 | Suppress grant service after the simplex drop | C1.4, F2.2 |
| P27 | Bypass read fence after partial cut | C2.1, F2.1 |
| P28 | Bypass read fence after simplex drop | C2.1, F2.2 |
| P29 | On the lost read-reply path bypass loss and give a value different from the served snapshot | C2.2, F2.1 |
| P30 | On the lost read-reply path bypass loss and give a value different from the served snapshot | C2.2, F2.2 |

Scoring: each baseline passes only if completed without a witnessed clause
violation or missing evidence. Expected-clause-only mutation kills; timeouts,
bounds, compiler/operational failures and absent triggers are not kills. E2
preserves witnessed safety failures. E3 bound alone is UNEXPLAINED. C1.4 uses the
existing qualified three-second horizon and final environment reconstructed from
Fault records, now requiring a direct bidirectional clique of two lease nodes,
storage and the pending requester. The grantor need not be in that clique. Lost
requests/grants do not complete a requester. If P25/P26 unmutated fails, retain
that finding and report no working half; do not count its mutation as independent
evidence of sensitivity. No expectation licenses changing failed behavior.

Retain seeds 1–3, T2 0–2 ms, delivery jitter 1–5 ms, reordering/duplicates and
unseeded Raft election timing. Five-second operational waits and finite three-
second progress certificates remain limitations. No exhaustive correctness claim.

Expected interpretation changes (no outcomes informed these): 11, 21, 25 and 53's
delivery/cut-history gating is contradicted by v2 send-time fate. Replace it with
independent directed send admission for requests, replies and Raft RPCs; a sent
message may arrive after a cut. The decision-to-reply interval is local pending
work, so a cut before the reply's actual send can still lose that reply. Complete
bipartitions become accumulated directed failures (extends 19, 37, 38, 53).
Connectivity is direct and bidirectional, not a side-equivalence relation or a
count of nodes merely reachable from the client/storage (extends 16, 38).
Interpretation 52's E1 includes reads explicitly and T3 never serializes reads or
writes behind lost replies. Keep all v1 derivations and durable authority choices.

Plan: (1) commit this prediction/scoring table; (2) implement directed fault
language, frozen L1 selectors, accumulated links/heal and schema-v4 links;
(3) adapt Raft send/reply admission and application send-time fate, literal clique
liveness and its independent reconstruction, preserving standing requests;
(4) extend the CLI to thirty pairs and add the twelve mutations; (5) fixtures,
required 31×3 baseline and 30×3 mutation runs, vet; (6) retain every trace/sidecar,
input hashes, per-seed results and additive interpretations, then adapted commit.
Commits distinguish mechanical propagation from changes required by F2.x meaning.

Focused fixture predictions after adaptation: directional send failures leave
reverse paths intact; cut is symmetric, accumulation includes partition, all-cell
heal restores every link; duplicate/self-pairs are harmless; rest/unknown/wrong-
cell/malformed/early aliases reject; selectors freeze at firing; links serialize
as resolved directed pairs and heal as []; pre-cut sent requests/replies survive
cut/heal, while sends on down links never resurrect; unavailable incarnations
still lose messages under F1.1; two reachable but mutually disconnected nodes are
not a majority clique; a clique excluding the grantor does qualify; independent
C1.4 reconstruction agrees with these premises; reads are included in quiescence,
and lost replies do not block later workload; E3 cannot PASS an exceeded bound.
No outcome has informed these predictions or this plan.

### X2 additive source-review amendment: local reply work and crash

<!-- derives: C1.3, C2.2, F1.1, F2.1, F2.2 -->
The first complete matrix at checkpoint 94549e3 passed 93/93. No failing schedule
prompted this amendment. Source review of the new pendingSend stage found that
storage crash currently leaves unsent local reply work in the harness queue.
F1.1 requires losing volatile process state. Fix by discarding pendingSend items
when storage crashes, retaining messages already sent into the external network.
Expected regression: before the fix an unsent reply survives storage restart;
after the fix it is absent while an already-sent reply remains deliverable.
This adds coverage for the preregistered incarnation/availability expectation;
all original verdicts, mutation placements, durations and scoring are unchanged.
The already-observed passes informed neither this rule nor its correction, but
are explicitly disclosed here. Retain the first matrix as initial evidence and
repeat the required matrix after this production change. Additional focused
source-review fixtures will verify runtime clique eligibility and that a failed
grant reply send leaves a requester outstanding; both are expected to pass.

## FixR routing repair — registered before adaptation or runs

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2, L1, L2, L3, T1, T3, E1, E2, E3 -->
First recorded clock: 2026-10-21 14:59:31 UTC. Fresh signed fixr-adapt-impl clone.
No FixR build, fixture, schedule or mutation has run. The supplied verdict already
informs this repair: X2 failed C1.4 on H8/H9, judged to be missing request/reply
routing. That is prior supplied evidence, not a new result from this round.
No other-side artifact, experiments or steward documents are consulted. The
absent seed documents are exempted by the inherited author brief. All task files
remain under impl/ and permitted inputs remain read-only; commits use normal
signing and the OTS hook; no push. Historical preregistrations remain untouched.

Predictions for all thirty-five shared schedules and existing mutations:

| Schedule | Seed 1 baseline / mutation | Seed 2 baseline / mutation | Seed 3 baseline / mutation |
|---|---|---|---|
| P1 | PASS / FAIL C1.1 | PASS / FAIL C1.1 | PASS / FAIL C1.1 |
| P2 | PASS / FAIL C1.1 | PASS / FAIL C1.1 | PASS / FAIL C1.1 |
| P3 | PASS / FAIL C1.1 | PASS / FAIL C1.1 | PASS / FAIL C1.1 |
| P4 | PASS / FAIL C1.2 | PASS / FAIL C1.2 | PASS / FAIL C1.2 |
| P5 | PASS / FAIL C1.2 | PASS / FAIL C1.2 | PASS / FAIL C1.2 |
| P6 | PASS / FAIL C1.2 | PASS / FAIL C1.2 | PASS / FAIL C1.2 |
| P7 | PASS / FAIL C1.3 | PASS / FAIL C1.3 | PASS / FAIL C1.3 |
| P8 | PASS / FAIL C1.3 | PASS / FAIL C1.3 | PASS / FAIL C1.3 |
| P9 | PASS / FAIL C1.3 | PASS / FAIL C1.3 | PASS / FAIL C1.3 |
| P10 | PASS / FAIL C1.4 | PASS / FAIL C1.4 | PASS / FAIL C1.4 |
| P11 | PASS / FAIL C1.4 | PASS / FAIL C1.4 | PASS / FAIL C1.4 |
| P12 | PASS / FAIL C1.4 | PASS / FAIL C1.4 | PASS / FAIL C1.4 |
| P13 | PASS / FAIL C2.1 | PASS / FAIL C2.1 | PASS / FAIL C2.1 |
| P14 | PASS / FAIL C2.1 | PASS / FAIL C2.1 | PASS / FAIL C2.1 |
| P15 | PASS / FAIL C2.1 | PASS / FAIL C2.1 | PASS / FAIL C2.1 |
| P16 | PASS / FAIL C2.2 | PASS / FAIL C2.2 | PASS / FAIL C2.2 |
| P17 | PASS / FAIL C2.2 | PASS / FAIL C2.2 | PASS / FAIL C2.2 |
| P18 | PASS / FAIL C2.2 | PASS / FAIL C2.2 | PASS / FAIL C2.2 |
| P19 | PASS / FAIL C1.1 | PASS / FAIL C1.1 | PASS / FAIL C1.1 |
| P20 | PASS / FAIL C1.1 | PASS / FAIL C1.1 | PASS / FAIL C1.1 |
| P21 | PASS / FAIL C1.2 | PASS / FAIL C1.2 | PASS / FAIL C1.2 |
| P22 | PASS / FAIL C1.2 | PASS / FAIL C1.2 | PASS / FAIL C1.2 |
| P23 | PASS / FAIL C1.3 | PASS / FAIL C1.3 | PASS / FAIL C1.3 |
| P24 | PASS / FAIL C1.3 | PASS / FAIL C1.3 | PASS / FAIL C1.3 |
| P25 | PASS / FAIL C1.4 | PASS / FAIL C1.4 | PASS / FAIL C1.4 |
| P26 | PASS / FAIL C1.4 | PASS / FAIL C1.4 | PASS / FAIL C1.4 |
| P27 | PASS / FAIL C2.1 | PASS / FAIL C2.1 | PASS / FAIL C2.1 |
| P28 | PASS / FAIL C2.1 | PASS / FAIL C2.1 | PASS / FAIL C2.1 |
| P29 | PASS / FAIL C2.2 | PASS / FAIL C2.2 | PASS / FAIL C2.2 |
| P30 | PASS / FAIL C2.2 | PASS / FAIL C2.2 | PASS / FAIL C2.2 |
| false-suspicion-v1 | PASS / — | PASS / — | PASS / — |
| H7 | PASS / — | PASS / — | PASS / — |
| H8 | PASS / — | PASS / — | PASS / — |
| H9 | PASS / — | PASS / — | PASS / — |
| H10 | PASS / — | PASS / — | PASS / — |

The existing P1–P30 placements remain. Two additional enforcing-path mutations
exercise the repair itself and run H9 with no schedule changes:

| Mutation | Break | Seed 1 | Seed 2 | Seed 3 | derives |
|---|---|---|---|---|---|
| R1 | Followers do not forward received grant requests | FAIL C1.4 | FAIL C1.4 | FAIL C1.4 | C1.4, F2.1, F2.2, L3 |
| R2 | Issued grant replies cannot be relayed through lease nodes | FAIL C1.4 | FAIL C1.4 | FAIL C1.4 | C1.4, F2.1, F2.2, L3 |

Thus --all covers 35×3 runs, and --mutations covers 32×3 runs. A mutation kill
requires its predeclared clause on every seed; a compiler error, timeout, bound,
missing evidence or different clause is not a kill. E2 preserves an observed
safety violation even if a later trigger is unreachable. Existing five-second
operational waits, three-second qualified C1.4 horizons, seeds 1–3, T2 delay and
network sampling remain unchanged. False suspicion remains an observed trace.

Choice: clients periodically retry the same Request identity to all lease nodes;
lease nodes forward along simple lease-node paths, checking each outgoing link
at send time, without a global reachability/path oracle. Only an actual Raft
leader that has received a request can apply an allocation. Committed allocation
issues one observable Grant even if its reply will be lost; no receipt is implied.
Replies have a local preparation stage, then send directly and through lease
nodes with the original issuer/token/Grant reference. Network duplicates never
create another Grant record. A lost reply leaves the Request outstanding and a
retry can cause a fresh, higher-token allocation. Relays gain no grant authority.
No protocol branch depends on a schedule name, and direct bidirectional L3
connectivity remains the liveness premise even when routing is multihop.

The Grant event and receipt must be split throughout the runner and checker.
A small sidecar delivery certificate names the exact issued Grant, Request,
client incarnation and hop route (with link-send/fault witnesses). It introduces
no schema event. An eligible horizon with issued-but-undelivered Grants still
fails C1.4. The checker may also infer possession from an actual client attempt
causally using that Grant. Missing/malformed delivery evidence is not silently
accepted. The certificate's actual receipt is trusted instrumentation, explicitly
added to the existing finite-duration-certificate limitation. Local unsent lease
reply work is volatile on issuer crash; sent packets can survive sender crash.
Pause actions triggered by issuance wait for actual holder receipt. C1.1 orders
issuance, not receipt; new allocations remain globally serialized by this runner.

Expected interpretation changes: interpretation 2 and 71's delivered-only Grant
are contradicted, replaced by distinct issuance and receipt; interpretation 70's
literal clique is extended with a working route through followers, not replaced
by transitive connectivity. Interpretation 74's short P25/P26 success does not
support a general routing/liveness claim, as supplied H8/H9 evidence shows.
Add routing, retry, authority-preservation, delivery-certificate and pause-readiness
interpretations, all with C1.4/F2.x tags. Correct missing F2.x derivations in the
implementation's Raft integration/runner wherever found; do not inspect the
other author's runner to repair its tags.

Focused predictions: old code fails renamed leader/client-cut shapes and fails
to record undelivered Grant issuance; repaired code routes requests and replies
through followers without bypassing any directed send cut; permanent down-link
sends do not resurrect, pre-cut sent packets survive later cuts, cycles terminate,
and crashed/restarted or paused clients do not incorrectly obtain a grant.
An issued lost Grant remains in the trace, does not satisfy a pending C1.4 horizon,
and H8's crash trigger fires; the surviving nodes issue a higher token for the
same original Request. H7's read leaves the write fence unchanged; H10 makes
progress with a deaf follower. R1 and R2 fail C1.4 even though R2 may issue Grants.
No schedule-name special case is used; renamed in-memory fixtures exercise the
same topology. No new hold-out schedule file is created or counted as shared.

Declared expected limitations (before runs): this repairs client/leader routing,
not Raft's consensus algorithm. A stable leader/quorum is still required for
allocation; arbitrarily sustained election churn under admitted asymmetric or
non-transitive faults, if it prevents commits beyond the finite three-second
window, would still fail C1.4 when the literal clique premise holds. No observed
new instance of that shape is claimed yet. Likewise operational schedules that
exceed the event bound or require an unavailable trigger remain UNEXPLAINED,
not fabricated PASS/kill. The relay uses only lease nodes (not storage or other
clients); with three voters, a stable leader's bidirectional quorum plus the
premise's requester/follower clique provides a lease-node relay route. There is
no known additional stable-leader routing shape within that premise intentionally
left unfixed. The work retains the pinned Raft protocol, logical process crashes,
finite sampling and trusted duration/receipt instrumentation instead of claiming
a proof for unbounded schedules or arbitrary operating-system delays.

### FixR additive source-review amendment: renewal before holder pause

<!-- derives: C1.1, C1.4, F1.3, F2.1, F2.2, T3 -->
The first shared matrix passed 105/105; all 96 mutation runs failed their intended
clauses. Those outcomes did not prompt this amendment. Source review found a
new issuance/receipt interaction: when a client already has an expired old grant,
a pause triggered by its freshly issued renewal sees a nonempty grant list and
can reach the F1.3 action before the renewal arrives. The action then correctly
rejects the expired holder instead of waiting for the actual new holder. This
contradicts this round's registered pause-readiness interpretation. A repeated-
request/renewal fixture is predicted to fail before the change and pass after
readiness also requires the currently held grant to be unexpired. Existing F1.3
action validation is retained. No shared schedule, prediction, mutation placement,
scoring rule or horizon changes. Preserve the first matrices and repeat everything
after this correction; all original per-seed predictions remain in force.

### FixR outcome note: final baseline P18 seed 2

<!-- derives: C2.2, C1.4, F1.3, F2.1, F2.2, T2, T3, E1 -->
Outcome-informed. The final baseline matrix at e77dc22 returns 104 PASS and one
UNEXPLAINED: P18 seed 2, workload unavailable under T3. Its trace contains the
first issued/delivered grant, accepted write, served read and delivered read ack,
but no pause Fault and no second Request. The only false readiness condition for
that next pause is the held grant's expired issuance-relative 40 ms lifetime.
There is no certified pending-request horizon and no witnessed safety violation.
This is a prediction miss and retained final result, not a PASS or a C1.4 failure.
The old and new pause guards both require an unexpired holder under F1.3.

No behavior, lifetime origin/duration, schedule, scoring rule or prediction is
changed in response. Final mutation execution proceeds once, as registered.
The declared limitations now include P18-like schedules: multiple round trips
between grant issuance and a pause trigger can consume the holder's finite
window; a renewal not requested by the schedule is not fabricated. This is left
as a bounded-sampling/injection limitation with its trace, rather than treating
an expired client as F1.3's unexpired holder. The original PASS predictions and
first 105-pass matrix remain intact. No additional baseline retry will replace
or obscure this final matrix.

### FixR final mutation outcome: P18 seed 2 is not a kill

<!-- derives: C2.2, C1.4, F1.3, T3, E1 -->
Outcome-informed. The single final --mutations run at e77dc22 has 95 expected
clause failures and one UNEXPLAINED, P18 seed 2, workload unavailable under T3.
Its pause never applies, so the P18 mutation is not reached and is not killed on
that seed. The final overall kill count is 31/32 across all three seeds. All other
mutations, including new R1/R2 on unchanged H9, fail the predeclared clause on
every seed. R2 issues 71 c2 Grants on each final seed while delivering none and
fails C1.4 with a qualified 3000 ms pending-request certificate. Original
predictions remain unchanged and both P18 prediction misses are explicit. There
is no rerun, re-placement, duration/lifetime change or scoring amendment.

## Timing repair — registered before adaptation or outcome-bearing runs

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2, T1, T2, T3, L1, L2, L3, E1, E2, E3 -->
First recorded clock: 2026-10-22 05:45:33 UTC. New timing-adapt-impl clone.
The supplied brief's 2,010-run finding informs this repair: P18 and P29/P30
mutation outcomes vary with wall-clock timing. No steward files, model artifact,
other-side directory, other documentation or external skill file is consulted.
The inherited author brief exempts the absent seed files. No timing-round build,
fixture or schedule/mutation run precedes this registration. Normal signed
commits and OTS hook; task outputs only in impl/; no push.

Exact requested predictions, for each seed 1, 2 and 3, on each repetition 1–10:

| Schedule | Seed 1 baseline / mutation | Seed 2 baseline / mutation | Seed 3 baseline / mutation |
|---|---|---|---|
| P18 | PASS ×10 / FAIL C2.2 ×10 | PASS ×10 / FAIL C2.2 ×10 | PASS ×10 / FAIL C2.2 ×10 |
| P29 | PASS ×10 / FAIL C2.2 ×10 | PASS ×10 / FAIL C2.2 ×10 | PASS ×10 / FAIL C2.2 ×10 |
| P30 | PASS ×10 / FAIL C2.2 ×10 | PASS ×10 / FAIL C2.2 ×10 | PASS ×10 / FAIL C2.2 ×10 |

All other 32 shared schedules are predicted PASS on seeds 1–3 in every repetition.
All other P1–P30 mutations and R1/R2 are predicted FAIL of their existing declared
clause on seeds 1–3 in every repetition. R1/R2 retain unchanged shared H9.
Thus ten --all executions contain 1,050 baseline results; ten --mutations
executions contain 960 results, with 201 cells each appearing exactly ten times.
Any cell with more than one outcome fails determinism acceptance. A consistently
wrong/UNEXPLAINED outcome fails functional acceptance. A mutation counts as killed
only by its declared clause, never a timeout, compiler failure or missing evidence.
A prior failed run is preserved and reported; a later correction must name the
misread clause/cell and is additively registered as outcome-informed if applicable.

Design choice: move the entire artifact execution into one deterministic event
loop with an integer logical-time clock. Seeded RNG supplies delivery order,
latencies, T2 delay, election deadlines and retransmission choices. All outcome-
bearing uses of real time, goroutines, select races and wall-time protocol timers
are removed. Node iteration and library-generated outbound messages have stable
ordering before seeded sampling. No protocol decision depends on a schedule name.
Shared JSONL keeps its clock-free schema; logical timing/certificates and replay
hashes belong in sidecars. Wall time is workflow metadata only.

HashiCorp's autonomous goroutines/timers cannot be made scheduler-owned by replacing
just the runner clock. Use an existing explicit-state Raft engine (etcd RawNode,
pinned in go.mod) for the same committed-log-index token allocator. Its Ready/Step
boundary is driven synchronously; log/hard-state persistence precedes sends,
committed entries precede allocation replies, and retained storage survives
simulated crash. This is a protocol-library integration change, not a new central
quorum allocator or a home-written consensus protocol. Elections/heartbeats use
scheduler ticks and seeded explicit campaign deadlines. Library randomized
follower timeouts are not allowed to select execution: use quiesced follower
ticks and explicit campaigns, or a narrowly documented deterministic random
source if source inspection shows that required. No wall-time input may affect
the state machine. A dependency-source inspection is preparation, not a scored run.

The new clock's nominal unit is one simulated millisecond. Existing 40-unit grant
lifetime, 8-unit local reply preparation, 20-unit request retry, qualified 3,000-unit
C1.4 opportunity and 5,000-unit operational bound remain. T2 samples 0–2 logical
units. Packet latency is sampled 1–3 logical units, uniformly for Raft, lease and
storage traffic, before any timing-round outcomes: this is an explicit bounded
scheduler distribution, not real elapsed runtime. Zero-duration synchronous work
and serialization/IO consume no logical time. The smaller delivery distribution
and removal of host overhead keep the shared P18 pre-pause workload within its
40-unit holder window. No pause is allowed for an expired holder, no grant is
invented, and no shared schedule or lifetime is changed. F1.3 freezes client
execution/receipt while scheduler-owned grant time advances; its resume remains
strictly later than the lifetime, with a later grant as the existing witness.
F2.x still fixes message fate at directed send time; a cut never retracts a sent
packet, and healing never resurrects a send lost on a down link. Equal-time
fault/message action order is now seeded and explicit, not a host scheduling race.
The fix round's unexpired-renewal guard is not repurposed as a timing fix: any
remaining guard is evaluated only against logical time with the same validity rule.

P29/P30 enforcing-path sensitivity: preregister a deterministic mutation placement
if the old loss-only wall-time branch can be skipped. The same C2.2 break (wrong
served snapshot/value) is armed by the respective link fault and applied on the
original served read's reply path, including a reply delivered after healing.
It must not depend on whether a host poll happens before the local send deadline.
P1–P28 and R1/R2 retain their enforcing paths. Any actual re-placement is recorded
explicitly; a counterfactual survives unless its actual reply path is broken.

Expected interpretation changes: contradict 5/21/60/66's wall-clock execution and
unseeded Raft election sampling; extend 67–70's link-fate/direct-clique semantics
with explicit seeded event ordering; extend 76/78's routing and receipt evidence
with scheduler-owned deadlines; supersede the host-overhead part of the declared
P18 pause-window limitation without weakening F1.3. P29/P30's old gate on the
loss branch was not a stable enforcing-path placement; make its activation and
break point explicit if needed. Preserve historical text and v1 clause/cell IDs.

Focused predicted regressions: perturbing host delay or GOMAXPROCS cannot change
canonical traces/sidecars, same-process and fresh-process replays agree, labels
aside; different seeds may choose different schedules of events. Renamed fixtures
follow identical seeded protocol rules. Pre-cut packets survive later cuts,
down-link sends remain lost, logical expiry/pause and stable progress horizons
are exact, crashed clients cannot inherit old receipts, issuer crash preserves
committed tokens, and R2-issued-undelivered Grants still fail C1.4. A static audit
must find no outcome-bearing wall clock, unseeded RNG, async protocol loop or
unordered-map decision in the execution path. Keep all 2,010 final raw traces,
sidecars, receipts and per-cell outcome counts, plus canonical replay hashes.

Declared expected limitations: this is a deterministic bounded simulation using
an existing Raft state machine, not OS/process/network timing verification or
exhaustive exploration of all permitted message timings. For a fixed executable,
accepted schedule and seed there is no intentionally nondeterministic schedule
shape. Operational IO/build failures are outside protocol replay and remain
UNEXPLAINED; corrupt/unsupported inputs reject deterministically. Long workflows
can still deterministically exceed a lifetime/trigger/event bound, and arbitrary
permanent election disruption is not an unbounded liveness proof. These are not
licenses for repeat-varying outcomes. Library/code/version changes can change a
seed's canonical trace and are bound to evidence hashes. Distinct unique file
labels may differ between repetitions but never feed scheduler state or scoring.
