<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2, T2, T3, L3, E1, E2, E3 -->
# Timing repair: ten-repetition acceptance results

Signed registration `b7867c5`, OTS stamp `674db60`, preceded adaptation and every
outcome-bearing run. Implementation checkpoint `afb4fc2`, stamp `36ec2be`.
The final answer gives the adapted-version evidence commit and its OTS stamp.
No prediction, scoring rule, shared input, lifetime or mutation placement was
amended after outcomes. The initial source-audit red run is retained separately.

Each required command was executed exactly ten times:

```sh
# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2
impl/run.sh --all --seeds 3
impl/run.sh --mutations --seeds 3
```

All twenty executions exit 0. All **1,050 baseline runs PASS** and all **960
mutation runs FAIL their declared clause**. Every one of the 201 (schedule, seed,
mode/mutation) cells has exactly ten identical expected outcomes. **Zero flaky
cells, zero prediction misses, zero UNEXPLAINED results.** All 32 mutations are
killed on every seed in every repetition. False suspicion remains an observed
schedule, not a paired correctness proof.

Each cell also has exactly one canonical execution hash across its ten fresh-
process repetitions. Canonicalization removes only the unique JSONL run label
and includes every other observable field plus the complete sidecar. Verdicts
are counted independently. Thus equal verdicts are not hiding different sampled
executions. Raw trace/sidecar hashes preserve the original unique labels too.

| Seed | Baseline PASS | Expected mutation failures |
|---|---|---|
| 1 | 350/350 | 320/320 |
| 2 | 350/350 | 320/320 |
| 3 | 350/350 | 320/320 |

## Counts for every cell

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2 -->
Each table entry gives the actual count and verdict, separately for the baseline
and the corresponding P mutation. R1/R2 on shared H9 are listed afterwards.
The [201-row cell-count TSV](evidence-timing/cell-counts.tsv) also gives distinct
verdict/execution counts and the canonical hash for each cell.

| Schedule | Seed 1 baseline / mutation | Seed 2 baseline / mutation | Seed 3 baseline / mutation |
|---|---|---|---|
| P1 | 10 PASS / 10 FAIL C1.1 | 10 PASS / 10 FAIL C1.1 | 10 PASS / 10 FAIL C1.1 |
| P2 | 10 PASS / 10 FAIL C1.1 | 10 PASS / 10 FAIL C1.1 | 10 PASS / 10 FAIL C1.1 |
| P3 | 10 PASS / 10 FAIL C1.1 | 10 PASS / 10 FAIL C1.1 | 10 PASS / 10 FAIL C1.1 |
| P4 | 10 PASS / 10 FAIL C1.2 | 10 PASS / 10 FAIL C1.2 | 10 PASS / 10 FAIL C1.2 |
| P5 | 10 PASS / 10 FAIL C1.2 | 10 PASS / 10 FAIL C1.2 | 10 PASS / 10 FAIL C1.2 |
| P6 | 10 PASS / 10 FAIL C1.2 | 10 PASS / 10 FAIL C1.2 | 10 PASS / 10 FAIL C1.2 |
| P7 | 10 PASS / 10 FAIL C1.3 | 10 PASS / 10 FAIL C1.3 | 10 PASS / 10 FAIL C1.3 |
| P8 | 10 PASS / 10 FAIL C1.3 | 10 PASS / 10 FAIL C1.3 | 10 PASS / 10 FAIL C1.3 |
| P9 | 10 PASS / 10 FAIL C1.3 | 10 PASS / 10 FAIL C1.3 | 10 PASS / 10 FAIL C1.3 |
| P10 | 10 PASS / 10 FAIL C1.4 | 10 PASS / 10 FAIL C1.4 | 10 PASS / 10 FAIL C1.4 |
| P11 | 10 PASS / 10 FAIL C1.4 | 10 PASS / 10 FAIL C1.4 | 10 PASS / 10 FAIL C1.4 |
| P12 | 10 PASS / 10 FAIL C1.4 | 10 PASS / 10 FAIL C1.4 | 10 PASS / 10 FAIL C1.4 |
| P13 | 10 PASS / 10 FAIL C2.1 | 10 PASS / 10 FAIL C2.1 | 10 PASS / 10 FAIL C2.1 |
| P14 | 10 PASS / 10 FAIL C2.1 | 10 PASS / 10 FAIL C2.1 | 10 PASS / 10 FAIL C2.1 |
| P15 | 10 PASS / 10 FAIL C2.1 | 10 PASS / 10 FAIL C2.1 | 10 PASS / 10 FAIL C2.1 |
| P16 | 10 PASS / 10 FAIL C2.2 | 10 PASS / 10 FAIL C2.2 | 10 PASS / 10 FAIL C2.2 |
| P17 | 10 PASS / 10 FAIL C2.2 | 10 PASS / 10 FAIL C2.2 | 10 PASS / 10 FAIL C2.2 |
| P18 | 10 PASS / 10 FAIL C2.2 | 10 PASS / 10 FAIL C2.2 | 10 PASS / 10 FAIL C2.2 |
| P19 | 10 PASS / 10 FAIL C1.1 | 10 PASS / 10 FAIL C1.1 | 10 PASS / 10 FAIL C1.1 |
| P20 | 10 PASS / 10 FAIL C1.1 | 10 PASS / 10 FAIL C1.1 | 10 PASS / 10 FAIL C1.1 |
| P21 | 10 PASS / 10 FAIL C1.2 | 10 PASS / 10 FAIL C1.2 | 10 PASS / 10 FAIL C1.2 |
| P22 | 10 PASS / 10 FAIL C1.2 | 10 PASS / 10 FAIL C1.2 | 10 PASS / 10 FAIL C1.2 |
| P23 | 10 PASS / 10 FAIL C1.3 | 10 PASS / 10 FAIL C1.3 | 10 PASS / 10 FAIL C1.3 |
| P24 | 10 PASS / 10 FAIL C1.3 | 10 PASS / 10 FAIL C1.3 | 10 PASS / 10 FAIL C1.3 |
| P25 | 10 PASS / 10 FAIL C1.4 | 10 PASS / 10 FAIL C1.4 | 10 PASS / 10 FAIL C1.4 |
| P26 | 10 PASS / 10 FAIL C1.4 | 10 PASS / 10 FAIL C1.4 | 10 PASS / 10 FAIL C1.4 |
| P27 | 10 PASS / 10 FAIL C2.1 | 10 PASS / 10 FAIL C2.1 | 10 PASS / 10 FAIL C2.1 |
| P28 | 10 PASS / 10 FAIL C2.1 | 10 PASS / 10 FAIL C2.1 | 10 PASS / 10 FAIL C2.1 |
| P29 | 10 PASS / 10 FAIL C2.2 | 10 PASS / 10 FAIL C2.2 | 10 PASS / 10 FAIL C2.2 |
| P30 | 10 PASS / 10 FAIL C2.2 | 10 PASS / 10 FAIL C2.2 | 10 PASS / 10 FAIL C2.2 |
| H7 | 10 PASS / — | 10 PASS / — | 10 PASS / — |
| H8 | 10 PASS / — | 10 PASS / — | 10 PASS / — |
| H9 | 10 PASS / — | 10 PASS / — | 10 PASS / — |
| H10 | 10 PASS / — | 10 PASS / — | 10 PASS / — |
| false-suspicion-v1 | 10 PASS / — | 10 PASS / — | 10 PASS / — |

| Routing mutation (shared H9) | Seed 1 | Seed 2 | Seed 3 |
|---|---|---|---|
| R1 | 10 FAIL C1.4 | 10 FAIL C1.4 | 10 FAIL C1.4 |
| R2 | 10 FAIL C1.4 | 10 FAIL C1.4 | 10 FAIL C1.4 |

## Interpretation changes

<!-- derives: C1.1, C1.4, C2.2, F1.1, F1.3, F2.1, F2.2, T2, T3, L3, E1 -->
- **New (80):** one synchronous event loop owns logical time and seeded choices.
  One nominal millisecond is one simulated unit. Synchronous work and host IO
  consume no simulated time. T2 remains 0–2 units; packet delay is the explicitly
  preregistered 1–3-unit distribution. Output file suffixes never enter state.
- **Contradicted (81/82):** prior real-time execution and unseeded election
  sampling are superseded. Pinned etcd Raft v3.6.0 RawNode replaces HashiCorp's
  autonomous goroutines/timers. The existing committed-entry index/term token
  authority remains: persistence precedes sends, and actual commit precedes grant
  issuance. Go is pinned to 1.23.12. Stable Ready-message ordering precedes seeded
  network sampling. This is a library integration, not a new quorum allocator.
- **Extended F1.3 (83):** client pause freezes execution/receipt while logical
  grant time advances. The 40-unit issuance-relative lifetime, unexpired-holder
  validity/renewal guard and strictly-later resume rule remain. Their clock is
  now scheduler-owned. The host-overhead P18 limitation is superseded; sufficiently
  long logical workflows may still miss a holder window deterministically.
- **Extended F2.x (84):** directed send-time fate is unchanged. A later cut cannot
  retract a sent packet and a heal cannot resurrect a down-link send. Receiver
  replacement discards its inbox. Equal-time event order is now explicit and
  seeded; direct bidirectional L3 eligibility and follower routing remain.
- **Preserved enforcing paths (85):** no mutation was re-placed. P29/P30 still
  break the actual lost read-reply path. The registered contingency to move a
  race-gated break was not needed. Every P18/P29/P30 mutation trace contains an
  ack value different from its actual served snapshot, with the same original
  attempt/decision references; no kill relies on an unreachable trigger.

The pinned RawNode library computes an internal random follower timeout, but the
driver never permits it to choose an event: leader roles receive Tick; followers
and candidates receive TickQuiesced, advancing only lease age. Explicit seeded
Campaign deadlines start their elections and current-leader messages reset those
deadlines. The internal random timeout is consulted only by tickElection, which
is not called for a follower/candidate in this driver. The
[upstream reference audit](evidence-timing/logs/upstream-timeout-references.txt)
records the source locations. An upgrade of that library/API requires re-audit.

## Verification and retained evidence

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2 -->
All 51 top-level Go tests and vet pass. Added tests reject outcome-bearing host
clocks, goroutines, select races and OS entropy in production sources; canonical
replays compare P18/P29/P30 baseline/mutation cases under host delay, different
GOMAXPROCS values and renamed schedules. Host elapsed time cannot advance the
logical clock. Existing protocol fixtures retain voter/storage/send-admission
checks through the explicit-state library interface. See
[red audit](evidence-timing/logs/red.txt), [full tests](evidence-timing/logs/go-test.txt),
[focused replays](evidence-timing/logs/focused.txt), and
[vet exit](evidence-timing/logs/go-vet.exit.txt).

[Exit receipts](evidence-timing/logs/exits.tsv) identify all twenty command runs.
[Per-run replay hashes](evidence-timing/replay-hashes.tsv) bind all 2,010 runs to
cells and raw paths. [Manifest](evidence-timing/manifest.tsv) hashes all 4,020
JSONL/sidecar files, which are retained. [Source hashes](evidence-timing/source-sha256.tsv),
[pinned dependency receipt](evidence-timing/logs/dependency.json), and
[toolchain receipt](evidence-timing/logs/toolchain.txt) identify the executable's
source/dependency environment. [Shared input hashes](evidence-timing/shared-inputs.tsv)
verify all 42 allowed shared inputs are byte-identical to committed contents.

The [independent audit](evidence-timing/logs/audit.txt) verifies canonical equality,
exact expected outcomes, 4,170 grant receipts, 4,880 ack references and the actual
P18/P29/P30 value-breaking paths. [Mechanism witnesses](evidence-timing/mechanism-witnesses.tsv)
also retain H8's lost issuance/higher-token recovery, H9's follower routes and
R1/R2's qualified C1.4 failures. All authority/attempt/decision references remain
intact even in deliberate mutations. Reproduce from the root with
`python3 impl/evidence-timing/audit.py`; render this report with
`python3 impl/evidence-timing/report.py`.

Historical FixR/steward findings remain historical; no failing result was replaced
by a repeat or rescored into success. The timing-round matrix required no repairs
or outcome-informed amendment. No model artifact, steward file, external skill or
out-of-brief documentation was read. Shared inputs were unchanged; task output,
caches and dependency inspection stay inside the checkout. No tmp/ or cache is
committed, .venv is untouched, and nothing is pushed.

## Declared limitations

<!-- derives: C1.1, C1.4, C2.2, F1.1, F1.3, F2.1, F2.2, E1, E3 -->
For a fixed executable, valid schedule and seed, **no schedule shape is knowingly
left nondeterministic**. This claim concerns the artifact's deterministic protocol
simulation. It does not control external IO/build failures or unique output-label
suffixes; those do not feed scheduler state, and operational failure is still
reported UNEXPLAINED. It does not promise identical traces after code/library
changes; evidence hashes pin this version.

The simulation samples a bounded 1–3-unit latency distribution, not all permitted
message delays or OS timing. Logical process replacement and retained in-memory
storage do not test operating-system crashes. Receipt/duration certificates
remain trusted instrumentation. Long workflows and unstable topology/elections
can deterministically exceed a lifetime, trigger, event or finite progress bound;
repeat-varying outcomes would still be a defect, not an excused limitation.
This is not an unbounded liveness proof or exhaustive verification. These limits
were declared before runs and do not weaken F1.3 or F2.x fault semantics.

## Wall clock

<!-- derives: C1.4, F1.3, F2.1, F2.2 -->
First recorded clock: 2026-10-22 05:45:33 UTC. The final response reports elapsed
workflow time through the adapted-version commit and OTS hook. Pre-final-commit
measurement is in [timing.json](evidence-timing/timing.json). Wall time supplies no
execution decision or observe ordering.
