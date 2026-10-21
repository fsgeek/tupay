<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, E2 -->
# X1 fenced-read adaptation results

Predictions: signed commit `fc87c3b`, OTS stamp `9d153c5`.
Implementation checkpoint: signed `7bc3488`, OTS stamp `922d690`.
Round start: 2026-10-21 01:06:33 UTC. Final response reports elapsed time through
adapted-version commit and OTS hook. Historical evidence and predictions unchanged.

Commands `impl/run.sh --all --seeds 3` and `impl/run.sh --mutations --seeds 3`
both exit 0. 57/57 schedule runs PASS. 54/54 mutation runs FAIL exactly their
predeclared clause: 18/18 mutations killed on all three seeds. No schedule or
mutation prediction missed. The test-first red run records the pre-adaptation
missing feature, then the complete Go fixture suite and vet pass.

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
| false-suspicion-v1 | PASS / — (observed) | PASS / — (observed) | PASS / — (observed) |

Read decisions are independently summarized in [read-provenance.tsv](evidence-x1/read-provenance.tsv).
Every P18 seed has a causal witness that the resumed client receives v1 after a
newer v2 write, retaining the served snapshot: [late-read-snapshots.tsv](evidence-x1/late-read-snapshots.tsv).
Raw receipts: [all](evidence-x1/logs/all.txt), [mutations](evidence-x1/logs/mutations.txt),
[fixtures](evidence-x1/logs/go-test-1.txt), [vet](evidence-x1/logs/go-vet.txt).
All 111 runs' JSONL and sidecars are retained and checksummed in
[manifest.tsv](evidence-x1/manifest.tsv); shared inputs in [shared-inputs.tsv](evidence-x1/shared-inputs.tsv).
No model comparison or attribution is made. False suspicion is an observation.
Sampling is finite; Raft election timing is not seed-deterministic. C1.4 retains
its separately trusted finite opportunity certificate. There is no read liveness claim.

Blocked: none.
