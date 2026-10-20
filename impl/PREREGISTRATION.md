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
