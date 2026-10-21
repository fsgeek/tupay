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
