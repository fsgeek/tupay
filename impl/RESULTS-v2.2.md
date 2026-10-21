<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, E2 -->
# Schedule v2.2 / observe schema v3 results

Round start: 2026-10-21 03:57:24 UTC. Signed predictions `b3cbaf6`, OTS stamp
`5adaff8`; signed implementation checkpoint `a912afc`, stamp `160a069`.
Final response reports wall time through final commit and OTS hook.

Both required commands exit 0: `impl/run.sh --all --seeds 3` and
`impl/run.sh --mutations --seeds 3`. No verdict changed. All 57 baseline runs
PASS, and all 54 mutation runs FAIL their declared clause (18/18 kills across
three seeds). False suspicion remains observed. Full Go fixtures and vet pass.
The test-first red run exposed absent answers and undetected retry mismatch;
green fixtures verify the adaptation. Original predictions remain unchanged.

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

Independent raw-record audit validated every emitted ack's answers, including
normal, rejected, late, duplicate and deliberately fabricated mutation replies:
**297 acks**. [Ack provenance](evidence-v2.2/ack-answers.tsv) records
attempt identity, causal reachability and exact decision/direct-attempt agreement.
[Manifest](evidence-v2.2/manifest.tsv) checksums all 222 retained JSONL/sidecar files.
[Shared-input hashes](evidence-v2.2/shared-inputs.tsv) bind the unchanged schedules
and contracts to the updated interfaces. Raw [baseline](evidence-v2.2/logs/all.txt),
[mutation](evidence-v2.2/logs/mutations.txt), [fixture](evidence-v2.2/logs/go-test.txt)
and [vet](evidence-v2.2/logs/go-vet.txt) receipts are retained.

No model comparison or attribution is made. Sampling and C1.4's trusted finite
opportunity certificate remain unchanged; there is no new contract obligation.
Historical traces retain their original schema. Pre-existing untracked .venv
is untouched and uncommitted. Blocked: none.
