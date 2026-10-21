<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2, L3, T3, E1, E2, E3 -->
# FixR implementation routing repair: actual results and declared limitations

Signed registration `063c9a0`, OTS stamp `64b8b02`, precedes adaptation and tests.
Routing implementation `786a384`, stamp `572841d`. Source-review renewal
registration `abd85e2`, stamp `4de31ef`; final source checkpoint `e77dc22`, stamp
`5b3a98f`. Outcome note `8657767`, stamp `08d4655`, records P18 seed 2 without
changing behavior or scoring. The final answer gives the adapted evidence commit.

Run commands: `impl/run.sh --all --seeds 3` and
`impl/run.sh --mutations --seeds 3`. The final matrix is retained even when its
verdict misses a prediction; no baseline retry replaces it. Full fixtures and
vet pass. All 48 top-level Go tests pass, including renamed H8/H9, directed routes,
fairness, certificate corruption, and renewed-holder pause readiness.

| Seed | Final baseline PASS / 35 | Expected mutation failures / 32 |
|---|---|---|
| 1 | 35/35 | 32/32 |
| 2 | 34/35 | 31/32 |
| 3 | 35/35 | 32/32 |

## Every shared schedule and paired mutation, by seed

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2 -->
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
| P18 | PASS / FAIL C2.2 | UNEXPLAINED workload unavailable under T3 / UNEXPLAINED workload unavailable under T3 | PASS / FAIL C2.2 |
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
| H7 | PASS / — | PASS / — | PASS / — |
| H8 | PASS / — | PASS / — | PASS / — |
| H9 | PASS / — | PASS / — | PASS / — |
| H10 | PASS / — | PASS / — | PASS / — |
| false-suspicion-v1 | PASS / — | PASS / — | PASS / — |

R1 and R2 are additional mechanism mutations on unchanged H9; they are not new
shared schedules or changes to P1–P30's mutation placements.

| Mutation | Seed 1 | Seed 2 | Seed 3 |
|---|---|---|---|
| R1 | FAIL C1.4 | FAIL C1.4 | FAIL C1.4 |
| R2 | FAIL C1.4 | FAIL C1.4 | FAIL C1.4 |

Prediction misses across retained matrices: 2.
- all: P18 seed 2 mutation baseline: predicted PASS; actual **UNEXPLAINED workload unavailable under T3**.
- mutations: P18 seed 2 mutation P18: predicted FAIL C2.2; actual **UNEXPLAINED workload unavailable under T3**.

## Interpretations and discriminating evidence

<!-- derives: C1.1, C1.4, F1.1, F1.3, F2.1, F2.2, L3 -->
- **Contradicted (75):** interpretations 2/71 equated Grant issuance and receipt.
  Issuance is now recorded even when the reply is lost; only receipt completes
  the original Request. H8 records lost token 4 and recovers with token 6 for the
  same Request after the issuer crashes, on every seed.
- **New (76/79):** retry and follower forwarding carry requests and immutable
  grant replies along simple lease-node paths. Only Raft allocates. No protocol
  branch uses a schedule name or a global path oracle. R1 disables request
  forwarding; R2 disables reply forwarding. Both fail C1.4 on all three seeds;
  R2 issues Grants while delivering none to c2, so issuance cannot hide failure.
- **Extended (77):** literal direct bidirectional connectivity under L3 is
  unchanged. Routing through followers supplies service when the eligible
  majority excludes a stable grantor. H9 preserves its grantor and uses follower
  paths in both directions. Fair allocation also prevents an unreachable
  requester from starving another one.
- **Extended evidence/limitations (78):** sidecars distinguish actual receipt
  from issuance. Independent checks validate exact identities, directed hop
  admission at the recorded fault state, generations and route continuity.
  Actual receipt and duration remain trusted instrumentation.

H7 witnesses that reads do not advance the write fence; H10 witnesses progress
with a deaf follower. [Hold-out witnesses](evidence-fixr/holdout-witnesses.tsv),
[delivered routes](evidence-fixr/grant-deliveries.tsv), and
[routing-mutation witnesses](evidence-fixr/routing-mutations.tsv) retain the facts.
There is no fresh model comparison or divergence attribution. The genuine X2
H8/H9 violation attribution is supplied by this round's brief.

## Declared limitations and the retained adverse result

<!-- derives: C2.2, C1.4, F1.1, F1.3, F2.1, F2.2, L3, T2, T3, E1, E3 -->
**Observed remaining shape:** P18-like schedules that pause a holder after several
round trips can miss its issuance-relative 40 ms unexpired-holder window. Final
P18 seed 2 records the first grant's receipt, accepted write, served read and read
ack, then times out waiting for pause readiness. No pause Fault or c2 Request was
emitted. The old held token had expired and the schedule does not renew it.
The result is UNEXPLAINED T3, not PASS, C2.2 failure, or certified C1.4 failure.
The P18 mutation on seed 2 also stops before its enforcing-path break, so P18
is not counted as killed across all seeds in the final matrix (31/32 overall
kills, 95/96 expected mutation failures). The raw trace and sidecar remain in
the manifest. Extra relay hops can expose
this window. The existing lifetime and F1.3 validity rule are retained; an expired
client is not treated as an unexpired holder to force an outcome. This is an
explicit prediction miss and a remaining bounded-injection limitation.

**Consensus limitation:** routing does not change pinned HashiCorp Raft's
consensus/election algorithm. Sustained election churn under asymmetric or
non-transitive faults could prevent commits beyond the qualified three-second
window and still fail C1.4 with an eligible majority. No new concrete example
was observed among these shared schedules, and no additional stable-leader
routing shape satisfying the three-voter premise is known to be intentionally
left broken. An unbounded stabilization proof is outside this routing repair.

Relays use only lease nodes. A stable leader's quorum and the premise's majority
provide a route in this fixed three-voter system; arbitrary-membership systems
are not proved. Logical crashes, bounded seeds, unseeded Raft timing, trusted
receipt/duration certificates, five-second operational waits and event bounds
remain. An unavailable trigger or bound without a witnessed clause violation
is UNEXPLAINED, never a manufactured success or mutation kill.

## Evidence and amendment history

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2 -->
The first matrix at 786a384 passed 105/105 and killed all 32 mutations on all
seeds. Both first receipts and final receipts are preserved. Source review
identified the expired-old-grant/renewal interaction before its regression: the
[registered red renewal test](evidence-fixr/logs/red-renewal.txt) failed, then
passed after readiness required an unexpired received grant. This did not change
any shared prediction, mutation placement, duration, schedule or scoring.
The [initial red routing fixtures](evidence-fixr/logs/red.txt) reproduced the
known H8/H9 problems; two historical synchronous-receipt/count assumptions were
updated in the fixtures, with the [initial full-suite failure](evidence-fixr/logs/go-test-initial.txt)
retained. Final tests are [here](evidence-fixr/logs/go-test.txt), and
[vet's exit receipt](evidence-fixr/logs/go-vet.exit.txt) records exit 0.

Final [baseline receipt](evidence-fixr/logs/all.txt) and
[mutation receipt](evidence-fixr/logs/mutations.txt) retain the actual results;
[per-seed TSV](evidence-fixr/per-seed.tsv) and
[prediction-miss TSV](evidence-fixr/prediction-misses.tsv) make every result explicit.
The [manifest](evidence-fixr/manifest.tsv) hashes all JSONL/sidecar files from both
matrices. The [audit](evidence-fixr/logs/audit.txt) independently checks hop and ack
references, all four newly shared schedule witnesses, receipt completion for
successful runs, and unchanged hashes for all 42 allowed shared inputs.
Shared inputs remain unchanged. No other-side artifact, experiments or steward
documents were read or edited. Task output stays under impl/, .venv is untouched, no tmp/ or cache
is committed, and nothing is pushed. Reproduce the evidence audit from the root
with `python3 impl/evidence-fixr/audit.py` and this report with
`python3 impl/evidence-fixr/report.py`.

## Wall clock

<!-- derives: C1.4, F2.1, F2.2 -->
First recorded clock: 2026-10-21 14:59:31 UTC. The final answer reports elapsed
wall time through the adapted-version commit and OTS hook. The pre-final-commit
measurement is in [timing.json](evidence-fixr/timing.json). These clocks supply no
observable event ordering.
