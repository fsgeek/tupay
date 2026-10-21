<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, E2 -->
# Schedule-format v2.1 results

Predictions committed before adaptation: `dc93d1e57518bf4f062c7982bc1647af3c5bf87d`.
Implementation checkpoint: `9ff6584c912e50f8b2806e85cebd325ea9d01d6a`.
Normal signing remains enabled for every commit in this round.

| Schedule | Baseline seed 1 | Seed 2 | Seed 3 | Mutation seed 1 | Seed 2 | Seed 3 |
|---|---|---|---|---|---|---|
| P1 | PASS | PASS | PASS | FAIL C1.1 | FAIL C1.1 | FAIL C1.1 |
| P2 | PASS | PASS | PASS | FAIL C1.1 | FAIL C1.1 | FAIL C1.1 |
| P3 | PASS | PASS | PASS | FAIL C1.1 | FAIL C1.1 | FAIL C1.1 |
| P4 | PASS | PASS | PASS | FAIL C1.2 | FAIL C1.2 | FAIL C1.2 |
| P5 | PASS | PASS | PASS | FAIL C1.2 | FAIL C1.2 | FAIL C1.2 |
| P6 | PASS | PASS | PASS | FAIL C1.2 | FAIL C1.2 | FAIL C1.2 |
| P7 | PASS | PASS | PASS | FAIL C1.3 | FAIL C1.3 | FAIL C1.3 |
| P8 | PASS | PASS | PASS | FAIL C1.3 | FAIL C1.3 | FAIL C1.3 |
| P9 | PASS | PASS | PASS | FAIL C1.3 | FAIL C1.3 | FAIL C1.3 |
| P10 | PASS | PASS | PASS | FAIL C1.4 | FAIL C1.4 | FAIL C1.4 |
| P11 | PASS | PASS | PASS | FAIL C1.4 | FAIL C1.4 | FAIL C1.4 |
| P12 | PASS | PASS | PASS | FAIL C1.4 | FAIL C1.4 | FAIL C1.4 |
| false-suspicion-v1 | PASS | PASS | PASS | observed only | observed only | observed only |

39/39 shared schedule results PASS; 36/36 mutation results FAIL their predicted
clause; 12/12 mutations killed across three seeds. Both required commands exit 0.
No unexpected fixture, schedule, or mutation result; preregistration remains
byte-for-byte unchanged and no amendment was needed. No mutation was re-placed.

The fixture suite and go vet exit 0. Focused regressions cover numeric ordering,
down/grantor exclusion, frozen selection, remembered restart, unbound selectors,
partition use, role validation, and the complete shared P10 lifecycle. Existing
T1 predecessor-event regressions still pass; the behavior is now explicitly
tagged as v2.1 T1 without changing the action boundary.

The [P10 binding receipt](evidence-v2.1/selector-bindings.tsv) uses causal Grant
parents and env process sequence to show the lowest eligible crash, its matching
restart and the subsequent grantor crash, for each seed.
The [raw receipts](evidence-v2.1/logs/),
[input hashes](evidence-v2.1/shared-inputs.tsv),
[trace/checksum manifest](evidence-v2.1/manifest.tsv), JSONL and horizon sidecars
are retained. The shared inputs were not edited.

```sh
impl/run.sh --all --seeds 3
impl/run.sh --mutations --seeds 3
```

README interpretations 43–48 are additive. Timing starts at
2026-10-21 00:51:37 UTC; the final response reports wall time through the final
commit and its OTS hook. Blocked: none. The existing finite liveness certificate
and bounded sampling limitations remain.
