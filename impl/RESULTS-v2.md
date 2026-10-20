<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, E2 -->
# Schedule-format v2 results

Implementation checkpoint: `14521075ecfcbc5d8964c4eb1799376b8e678e89`.
Predictions committed first: `5d866a6b53aa32118a97fe5be5b46652bb5e72d4`; original bytes preserved as prefix.
The additive fixture outcome note is retained without revising any prediction.

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

39/39 shared schedule results PASS; 36/36 mutation results FAIL the predicted
clause; 12/12 mutations killed across three seeds. Both required commands exit 0.
No schedule/mutation prediction miss and no final UNEXPLAINED result.

P7 was re-placed as preregistered: bypass storage acceptance after restart and
return success for that unaccepted attempt. Its unreachable later trigger does
not hide the C1.3 violation (E2). All other mutations retained their placements.

The first fixture run failed because the alias test omitted its Engine storage
ID; the fixture was corrected, with an additive outcome-informed note. The final
complete Go fixture suite and go vet exit 0. The two later tests additionally
cover a synchronous final-action end event and all holder-target positions.

Only root shared schedules were run. Private schedules remain historical.
The [shared-input hashes](evidence-v2/shared-inputs.tsv),
[trace checksums/derivations](evidence-v2/manifest.tsv),
[raw receipts](evidence-v2/logs/) and
[false-suspicion decision provenance](evidence-v2/false-suspicion-provenance.tsv)
are retained with the raw observe JSONL and horizon sidecars.
False suspicion is observed, not scored as a paired correctness proof.

Commands:

```sh
impl/run.sh --all --seeds 3
impl/run.sh --mutations --seeds 3
```

Interpretations: README entries 29–42. Finite liveness trusts the same duration
certificate as M1; no wall-clock event ordering is introduced.

Wall-clock start: 2026-10-20 23:33:13 UTC. The final response reports elapsed
time through the adapted-version commit and its OTS hook. Blocked: none.
