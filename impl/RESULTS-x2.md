<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2, L1, L2, L3, E1, E2, E3, T3 -->
# X2 adaptation results: failure-model v2, schedule v4, schema v4

Predictions: signed `6c58815`, OTS stamp `e39c88c`, before adaptation or any
outcome-bearing run. Initial implementation: `94549e3`, stamp `27e8c36`.
Additive source-review registration: `3b73f2c`, stamp `2e62373`.
Final implementation checkpoint: `8321ab5`, stamp `acae806`.
The final response names the adapted-version evidence commit and its OTS stamp.

Both required commands exit 0:

```sh
# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2
impl/run.sh --all --seeds 3
impl/run.sh --mutations --seeds 3
```

For each seed: all 31 shared schedules PASS, including observed false suspicion;
all 30 mutations FAIL their preregistered clause. Thus 93/93 final baseline passes,
90/90 expected mutation failures, and 30/30 kills on all three seeds. No unmutated
shared schedule failed, no verdict prediction missed, and no scoring rule,
mutation placement, horizon or shared schedule changed. All 42 top-level Go
fixture tests and go vet pass. Bounded samples, unseeded Raft randomness and the
trusted finite C1.4 certificate remain limitations. No model agreement or proof
of correctness is claimed.

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

## Interpretations

<!-- derives: C1.1, C1.3, C1.4, C2.2, F1.1, F1.2, F2.1, F2.2, L1, L2, L3, E1, E3, T3 -->
- **Contradicted:** README interpretations 11, 21, 25 and 53's cut-history and
  delivery-time link checks conflict with v2 send-time fate. Interpretation 67
  replaces them, preserving historical statements and v1 derivations.
- **Extended:** interpretations 16/38 now require a literal bidirectional clique,
  including lease-node-to-lease-node connectivity; the current grantor need not
  be a member (70). Complete partitions become accumulated directed faults (69).
  Reads count in quiescence; reaching a bound cannot silently PASS (71).
- **New:** local reply preparation precedes network send (68). Storage crash
  discards that volatile work under F1.1 while preserving sent packets. Lost
  grant sends leave the requester outstanding. New enforcing-path mutations
  cover P19–P30 (72), with both P25/P26 baseline halves working.
- **Observed timing residue:** P17's first served reply arrives after healing on
  every final seed; the short cut ends before its send. Its second read sent
  during the cut is lost. The comment does not force loss of the first reply
  under v2 semantics. C2.2 passes and its mutation is killed. Interpretation 73
  records this coverage limitation without tuning the schedule or timing.

## Progress evidence

<!-- derives: C1.1, C1.4, F2.1, F2.2, L3 -->
Final P19/P25 retain n1, term 2, on all seeds. In P25, c2 receives token 4 after
c1's token 3 while the partial cut remains. P20 transfers from n1, term 2, token 3
to n2 (seed 1) or n3 (seeds 2/3), term 3, token 6; later grants increase to 7 and 8.
P26 transfers from n1, term 2, token 3 to n3, term 3, token 6 on every seed while
the simplex drop remains. Suppressing grant service in P25/P26 fails C1.4 with a
qualified pending-c2 horizon on every seed. See [progress.tsv](evidence-x2/progress.tsv).
Interpretation 74 limits these observations to the sampled short executions;
they do not establish resilience to every prolonged election pattern.

## Retained evidence and amendments

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2 -->
The [initial baseline](evidence-x2/logs/all-initial.txt) at 94549e3 also passed
93/93. Source review found the new local-send stage retained unsent reply work
across storage restart, contrary to F1.1. Additive preregistration preceded its
[red regression](evidence-x2/logs/red-storage.txt) and correction. This was not
a repair prompted by a failing shared schedule. Both complete baseline matrices
and the final mutation matrix are retained: 276 runs, 552 JSONL/sidecar files.

Raw [final baseline](evidence-x2/logs/all.txt),
[mutations](evidence-x2/logs/mutations.txt), [fixtures](evidence-x2/logs/go-test.txt),
[vet exit receipt](evidence-x2/logs/go-vet.exit.txt) and
[missing-link-support red run](evidence-x2/logs/red.txt) are retained.
The first audit failed handling JSON null for an empty horizon list; its
[receipt](evidence-x2/logs/audit-initial.txt) is retained. Correcting that input
handling changed no implementation, evidence, prediction or score. The
[final audit](evidence-x2/logs/audit.txt) passes. An initial report-rendering
attempt used CSV's default separator for the TSV and failed before creating this
report; the renderer now explicitly uses tabs. No result was recomputed or changed.

[Manifest](evidence-x2/manifest.tsv) hashes all 552 evidence files;
[shared-input hashes](evidence-x2/shared-inputs.tsv) verify all 38 permitted inputs
against their committed contents; [per-seed TSV](evidence-x2/per-seed.tsv) records
the final matrix. [Ack audit](evidence-x2/ack-answers.tsv) validates 646 explicit
answers, including mutation replies. [Fault audit](evidence-x2/fault-links.tsv)
checks 108 new directed link-fault records and every heal's empty list.
[P17 witnesses](evidence-x2/p17-replies.tsv) record its delayed original reply
and lost second read. The audit also verifies no c1 write acks in baseline
P23/P24, no old-holder read values in P29/P30, and served c2 reads after those
heals. Reproduce the audit with `python3 impl/evidence-x2/audit.py` from the root;
`python3 impl/evidence-x2/report.py` renders this report from its audited TSV.

The README access record discloses the initial external generic workflow-file
read and six git-log titles; no formal-model artifact was read. All task outputs
are in impl/, no tmp/ or cache is committed, .venv is untouched, and nothing is
pushed. No unexplained schedule result or implementation blocker remains. No
model comparison, model mutation, or divergence attribution was performed here.

## Wall clock

<!-- derives: C1.4, F2.1, F2.2 -->
First recorded clock: 2026-10-21 05:51:48 UTC, before source/input review.
The final response reports elapsed time through the final signed commit and OTS
hook. The pre-final-commit timestamp is in [timing.json](evidence-x2/timing.json).
These clocks are workflow metadata and supply no observable event ordering.
