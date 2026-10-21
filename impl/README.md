<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
# Implementation author — current v2, M1 history retained

The M1 implementation below was authored independently. In that round no model,
steward notes, other documentation, existing schedules, or git history were read.
The v2 round additionally reads the expressly permitted adaptation brief and
shared root schedules. No model artifact or other documentation is consulted. The brief's explicit access list supersedes AGENTS.md's
request to read and append steward seed documents.

Current v2 results: [RESULTS-v2.md](RESULTS-v2.md). All thirteen shared schedules
pass all three seeds; all twelve mutations fail their intended clauses on all
three seeds. Nothing remains blocked. The v2 section and interpretations 29–42
supersede conflicting M1 statements. Historical results below are retained.

## M1 design and plan (historical)

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
Use the existing HashiCorp Raft protocol with three nodes and durable in-memory
log/stable stores retained across node replacement. A committed FSM command
allocates each token. Two clients and one storage execute in the same OS process.
Storage retains its ledger across replacement; restarted clients lose grants.
Disconnect Raft transports and gate all client/storage traffic across a complete
bipartition. Pauses freeze client activity, while grant lifetimes continue.

Alternatives considered: an external multi-process deployment makes fault runs
slower and harder to reproduce; implementing a new quorum protocol violates the
brief. The selected in-process Raft arrangement uses a real existing protocol
with an independently implemented event-log checker.

Implementation sequence: (1) preregister and commit predictions and scoring;
(2) implement Raft, clients, storage, injectors and causal emitter; (3) implement
strict YAML compiler, all thirteen schedules, independent checkers and mutation
runner; (4) run the preregistered baseline/mutation matrix, document any
outcome-informed amendments additively; (5) commit the first complete version.

## How to run

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
`impl/run.sh false-suspicion-v1 --seeds 3`

`impl/run.sh --all --seeds 3`

`impl/run.sh --mutations --seeds 3`

Go is `/usr/local/go/bin/go`. The script changes directory to `impl/`.
V2 schedules are read from root `testbed/schedules/`; JSONL output is under
`impl/observe/`. Outputs stay under `impl/`; shared schedules are read-only. Build artifacts,
module caches and run output are ignored. The runner accepts only a shared schedule basename
with an optional `.yaml` suffix. Exit 0 means expected results;
exit 1 means an unexpected result; input/operational errors say UNEXPLAINED.

## Sampling

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
Default: three seeds, numbered 1 through N. Each seed varies workload delivery
jitter, Raft RPC timeout, and duplicate write delivery. Raft's own election
randomness is additional nondeterminism, so a seed does not promise bit-for-bit
replay. Observe traces are the replay evidence. This is bounded sampling, not
exhaustive verification. Per-seed results and mutation kills are printed.

## M1 interpretations (historical)

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
1. All generated artifacts, including the shared relative `testbed/schedules/`
   and `observe/` paths, live beneath `impl/` to respect the brief's output scope.
2. A grant is an observable committed reply. Failed or timed-out Raft operations
   may consume tokens without issuing grants. Integer gaps are permitted.
3. The contract does not require exclusive holders or specify renewal. This
   implementation waits at least the prior issued lifetime before issuing the
   next grant, making a later grant an expiry witness for pause/resume schedules.
4. Durable state is an in-memory object that survives simulated process
   replacement, not OS termination. Raft log/stable stores and storage's ledger
   survive; clients' volatile grants and pending reply inboxes do not.
5. Timeouts and real elapsed time drive the execution only. Checkers never order
   records by wall clock or by cross-process line order. Causal references and
   process sequence numbers determine observable order.
6. The schema's prose says a WriteAccept 'causes' a WriteAttempt, but its example
   and causal intent imply references point backwards: decision -> attempt ->
   grant -> request, and ack -> decision. We implement backwards references.
7. C1.1 concurrent grants without causal order are unorderable from this schema.
   The runner serializes successful grants through the grantor and links the
   previous grant into the next grant, including across incarnations. The
   checker rejects missing order evidence as UNEXPLAINED, not as a violation.
8. Liveness is tested with a finite three-second progress opportunity after
   eligible pending requests and stable connectivity. A qualifying unfulfilled
   request at that horizon fails C1.4; an unreachable schedule trigger without
   such a witness is UNEXPLAINED. This is a bounded operational interpretation
   of 'long enough', not proof of unbounded eventuality.
9. A paused holder may intentionally submit its old token after resumption;
   fencing, rather than the client's expiry check, is the protection being tested.
   `token: stale` chooses its newest superseded or expired grant and is rejected
   as an invalid workload if no such grant exists.
10. Trigger predicates remain true once observed, as the format states. Repeated
    `start` triggers are immediately enabled. Actions are serialized and fault
    events include causal trigger references. End is checked after all actions.
11. Messages crossing a cut are lost, including accept replies. Within-side
    duplicate write deliveries retain the original attempt reference. Successful
    late replies are correlated to their actual storage decision; client restart
    discards its old inbox. Paused clients retain their inbox until resumed.
12. The false-suspicion topology is exactly old grantor + c1 + storage against
    the remaining nodes + c2. It heals before c2 writes because storage is on
    c1's side during the cut. Its trace receives provenance validation and is
    reported as observed; ordinary contract results remain separately visible.
13. The same half-open lifetime applies to all grants (40 ms). Requests are
    retried against reachable leaders; a minority cannot issue a committed grant.
    Raft timers are operational and excluded from the observable record.
14. Crash/restart actions name explicit process IDs. Dynamic `grantor`, `holder`
    and `rest` aliases are supported in partition membership only, per format.

## Blocked

None currently. V2 runs in the full clone on impl-v2. The earlier permission
reports below are historical; the OTS stamp hook succeeds.

### Historical: Git metadata outside writable sandbox

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
The initial preregistration `git add` and `git commit` both failed before any
outcome-bearing run: Git could not create
`/home/tony/projects/tupay/.git/worktrees/tupay-impl/index.lock` (read-only file
system). This linked worktree's administrative directory is outside the writable
roots. No approval escalation is available. No first-version commit or hook
stamp can be produced in this environment. The preregistration gate therefore
also blocks scored baseline/mutation runs. Implementation and preparatory
source/dependency work continue. No outcome has informed this entry.

## Additional interpretations from source review (no outcomes)

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
15. Tokens are committed Raft log indices, rather than a separate persistent
    counter. Configuration and election entries cause legal gaps. The term is
    the committed entry's Raft term. FSM snapshots retain the last allocation.
16. The three-second C1.4 opportunity cannot be inferred from a clock-free finite
    event log alone. The runner writes a separate `<run>.meta.json` certificate
    naming each pending request, the last fault reference and the stable budget.
    The checker independently verifies final connectivity and lack of a grant
    from the JSONL, but trusts the runner's duration certificate. This limitation
    is explicit; a timeout without a certificate is UNEXPLAINED. Offline checking
    uses `impl/run.sh P10 --check observe/<run>.jsonl` from the repository root,
    with paths relative to `impl/`; `--evidence` overrides the sidecar path.
17. An ack missing its acceptance reference is UNEXPLAINED when an acceptance for
    that exact attempt exists elsewhere in the trace. A ghost ack for a distinct
    attempt with no acceptance is a C1.3 failure even if another write with the
    same token was accepted. Duplicate deliveries of one attempt may each have
    a decision. The P7/P8 schedules therefore contain both an accepted write with
    a lost reply and a second write that never reaches storage.
18. Observe sequence numbers survive simulated process restart in the observer.
    They are instrumentation state, not recovered grant authority. Followers
    emit no synthetic contract events: a lease node emits a Grant when it issues
    one; all fault actions are emitted by env. 'From every process' means every
    process producing a contract event uses its own sequence, not that idle
    followers invent events outside the schema.
19. Fault records include resolved partition memberships, so alias meanings are
    recoverable directly from the trace. The original YAML retains the aliases.
    The schedule compiler rejects omitted, repeated or unresolved members and
    rejects unknown cells, fields and operations before starting the workload.
20. The runner serializes request completion and spaces grants as a workload
    policy. After a pause it waits at least a further full lifetime before the
    next grant, guaranteeing a later Grant witnesses the required pause duration.
    This timing policy is not a replacement consensus protocol or a safety
    assumption of the Raft token allocator. The observer's prior-grant reference
    records the harness's serial causal chain; it does not carry allocation
    authority between partitioned nodes.
21. Sampling covers 1–5 ms delivery jitter, 25–39 ms Raft RPC timeouts, shuffled
    due-message batches, and a one-in-three chance of a duplicate write delivery.
    Ack delivery adds 8 ms plus jitter, so a fault triggered by a decision can
    intervene. Initial grants also depend on Raft's internal election randomness.
    Network messages are gated at delivery and cut creation, so healing does not
    resurrect messages discarded across the cut. This samples a subset of the
    permitted nondeterminism and does not explore arbitrary Raft message
    duplication or every possible action delay.
22. End predicates are checked after all actions to prevent historical matches
    from skipping required actions. A final 50 ms drain observes in-flight
    replies; a step waiting for an absent trigger has a five-second operational
    guard. The event bound also stops the runner. Clause violations already
    witnessed in a partial trace remain failures even if a later trigger is
    unreachable; an absent trigger alone never kills a mutation.
23. Baseline storage starts with a zero fence for positive allocated tokens, and
    retains the last accepted value as well as the fence through storage crashes.
    Negative or arbitrary externally forged tokens are not workload actions in
    the shared format. The contract's integer tokens are represented by uint64
    Raft indices; exhausting that representation is outside these bounded runs.
24. The preregistration gate in `run.sh` requires the preregistration file in HEAD
    before it builds or runs the program. No model/implementation comparison or
    correctness attribution is performed by this author. Mutation kills are
    scored only against the predeclared clause. The schema does not itself encode
    elapsed duration, so the sidecar is a limitation of bounded liveness scoring.

<!-- derives: C1.1, C1.3, C1.4, F1.1, F1.2 -->
25. The final transport is a small adapter for HashiCorp Raft's existing RPC
    interface, using locked in-memory inboxes. It has no consensus or allocation
    logic. It atomically checks connectivity when sending, tracks endpoint
    incarnations and cut history, and gates replies separately. Pipelining is
    disabled through Raft's supported fallback. Requests delivered into an inbox
    before a cut may still be processed, but their replies are independently
    subject to the cut. Client writes sent during a cut are dropped immediately,
    even if healing precedes their sampled delivery deadline. Adapter fixtures
    separately cover lost sends, cut/heal replies, unaffected majority traffic
    and process replacement. The 1024-entry inbox is an operational resource
    limit; exhaustion is not a new admitted failure cell and must be treated as
    an operational limitation if encountered.

## Initial delivery and remaining execution (historical)

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
The Go module, pinned dependencies/checksums, compiler, causal emitter, three
Raft nodes, clients, durable ledger/value, all injectors, four checkers, thirteen
schedules, twelve named mutations, command-line runner and independent checker
fixtures have been written. Dependency retrieval, `gofmt`, and `bash -n impl/run.sh` parsing completed. The first
`go mod tidy` attempt needed a writable `GOCACHE`; retrying with all Go caches
under `impl/.cache/` completed. No compilation, vet, unit test, schedule,
false-suspicion trace or mutation run has been performed. No PASS/FAIL result or
first-version hash is claimed. The Git metadata blocker above prevents the
required preregistration commit, first-version commit and hook stamps.

After the worktree administration path becomes writable, the remaining commands
are, in order (from the repository root):

```sh
# derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
git add impl/README.md impl/PREREGISTRATION.md impl/.gitignore
git commit -m 'impl: preregister independent predictions and scoring'
impl/run.sh --all --seeds 3
impl/run.sh --mutations --seeds 3
cd impl
export GOMODCACHE="$PWD/.cache/mod"
export GOPATH="$PWD/.cache/gopath"
export GOCACHE="$PWD/.cache/build"
/usr/local/go/bin/go test -mod=readonly ./...
/usr/local/go/bin/go vet -mod=readonly ./...
cd ..
# Resolve any failures, with additive outcome-informed notes, then:
git add impl
git commit -m 'impl: first version with paired schedules and mutations'
git rev-parse HEAD
```

No `tmp/` directory, run output, binary or module cache should be committed.


## Git blocker retested before first outcome

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
The steward added the parent `/home/tony/projects/tupay/.git` writable root.
A fresh preregistration `git add`/`git commit` retry still failed creating the
same `index.lock`. Mount inspection discriminated the cause: the parent `.git`
is mounted rw, while `/home/tony/projects/tupay/.git/worktrees/tupay-impl` is a
separate ro mount. That exact worktree-administration directory also needs to be
an explicit writable root. This is the current blocker under Blocked above,
refined by direct mount evidence. No source build, test, schedule or mutation has
run; the original preregistration file and predictions remain unchanged. No
outcome has informed this entry. The branch remains impl-v1.

## Execution resumed; initial observations

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
The steward removed the filesystem sandbox; ordinary Git operations now work.
Preregistration commit: `37283d5`; its hook stamp commit: `61050e7`.
The previous Blocked entries are historical. The first build succeeded, and the
false-suspicion observation passed seeds 1–3. In the initial pair matrix P1–P9,
P11 and P12 passed all three seeds; P10 failed C1.4 on all three. Predictions
were not rewritten. A clearly outcome-informed amendment records the setup
hypothesis and a new startup-voter regression before that test is executed.
The P10 trace contains only the n1 crash and c1 request, with a qualifying finite
progress certificate. Diagnosis remains unexplained pending direct configuration
evidence; no model artifact or model comparison is involved.

## Outcome-informed bootstrap correction

<!-- derives: C1.4, F1.1 -->
The registered startup-voter regression failed before the fix: n2 and n3 each
reported an empty configuration immediately after newEngine returned. This
observation discriminates the initial P10 failure as an implementation setup
defect. The fixed grantor was not fully established before the start-triggered
crash. The correction waits until all three Raft nodes expose the exact fixed
three-voter configuration, using the existing library's replication. The fault
schedule and the original baseline/mutation predictions are unchanged.

<!-- derives: C1.1, C1.4, F1.1, F1.2 -->
26. `start` begins after the fixed grantor is initialized at all three lease
    nodes. Bootstrap/configuration replication is setup, not a workload grant.
    The setup barrier is limited to the same three-second operational horizon;
    setup failure is UNEXPLAINED, not a paired clause violation. The barrier
    applies to all schedules and mutations, without changing injected faults.

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
27. Go build caches, module caches, test temporary directories and runner output
    are directed into impl/.cache or impl/observe. The runner sets TMPDIR too.
    Normal Git metadata writes and the authorized stamp hook are part of commits;
    no alternative checkout or other project artifact is used.

<!-- derives: C1.4, F1.1 -->
Bootstrap-fix validation: the startup-voter regression now passes; P10 baseline
seeds 1, 2 and 3 each PASS. The complete Go fixture suite passes and go vet reports
no findings. The initial mutation matrix reported the predicted clause on every
pair/seed, but its P10 result alone was not discriminating because the initial
baseline also failed. A fresh complete baseline and mutation matrix follows the
fix, with the original predictions unchanged.

## Verified M1 first-version delivery (historical)

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
The complete corrected matrix is recorded in [RESULTS.md](RESULTS.md): all twelve
baseline pairs PASS on each of seeds 1, 2 and 3; all twelve mutations FAIL their
predeclared clauses on each seed (36 baseline passes, 36 expected mutation
failures, 12/12 mutations killed across three seeds). The standalone
false-suspicion observation and its repeats in --all pass all three seeds, with
complete authority provenance and both grantor incarnations. All three final
runner commands exit 0. Go build, the complete fixture suite and go vet pass.
No final UNEXPLAINED result or outstanding blocker remains. These are bounded
sample results; the finite liveness certificate limitation remains as recorded.

The bootstrap setup barrier is the only outcome-informed behavior correction.
The initial failure and all command receipts are preserved. The original
preregistration remains byte-for-byte intact, followed by its additive
outcome-informed amendment. No prediction, pair schedule, mutation, clause,
scoring rule or horizon was revised in response to a result.

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
28. Generated run outputs are ignored by default. The 159 reference runs used
    for initial/final matrices and the focused P10 verification are explicitly
    retained in this first-version commit, including their JSONL and liveness
    sidecars. JSONL keeps the shared schema without added comment records.
    `evidence/manifest.tsv` supplies per-file `# derives:` comments and SHA-256
    bindings to the originating schedule; `evidence/logs/` retains raw command
    receipts, and the provenance TSV lists each false-suspicion storage decision.
    Go caches, binaries and temporary files remain excluded. Rerunning produces
    new unique run IDs rather than overwriting reference evidence.

## Adaptation to schedule format v2

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, E2 -->
The current runner implements v2 and reads only the thirteen shared root
`testbed/schedules/` inputs. M1's private `impl/testbed/schedules/` remains history
and is never resolved by the runner. The v2 predictions were committed before
adaptation (`5d866a6`, hook stamp `202f2f4`). The adapted implementation checkpoint
is `1452107` (stamp `c398b86`). No shared input was edited.

Both required commands completed with exit 0:

```sh
# derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, E2
impl/run.sh --all --seeds 3
impl/run.sh --mutations --seeds 3
```

All 39 schedule/seed results PASS, including the observed false-suspicion run;
all 36 mutation/seed results FAIL the predicted clause. There were no schedule
or mutation prediction misses. Raw receipts, traces, horizon sidecars and shared
input hashes are retained with [RESULTS-v2.md](RESULTS-v2.md). The first fixture
suite failed because a hand-built test Engine omitted its storage identity; the
fixture was corrected and the observation recorded additively in preregistration.
The full fixture suite and go vet now pass. P7 was the only re-placed mutation.

## New interpretations for v2

The entries below supersede the conflicting schedule-location, stale-token,
sticky-trigger, partition-only-alias and fixed-end-drain statements in the M1
history above. Contract clauses and failure cells retain their original IDs.

29. Schedule arguments are basenames (optionally `.yaml`), resolved only in the
    repository-root shared directory. Private/other paths and escaping file
    symlinks are rejected; the YAML name must match its basename.
    <!-- derives: C1.1, C1.4, T1, A1, E1 -->
30. A successor trigger, including an event end, is armed immediately before the
    preceding action's synchronous effects. Thus its Request or WriteAttempt
    is eligible; older events are not. `start` fires when armed. Cursors are
    injector state; checkers still use causal and per-process order only.
    <!-- derives: C1.1, C1.3, T1, T2, E1 -->
31. T2 samples a uniform 0, 1 or 2 ms action delay while workload progresses.
    Selectors freeze when the trigger fires, before that delay and before any
    T3 readiness wait. Only one step/action is pending at a time.
    <!-- derives: C1.1, C1.4, F1.2, T1, T2, T3, A1 -->
32. T3 waits for a running target, an answered prior request in its current
    incarnation, or an available write token. A multi-target workload waits for
    all selected clients. A blocked/ineligible workload reaches the operational
    bound as UNEXPLAINED unless an independently eligible request supplies C1.4
    evidence. A restarted client's old pending request is not its new request.
    <!-- derives: C1.1, C1.2, C1.4, F1.1, F1.3, T3, E1 -->
33. `stale` means the newest client token numerically lower than the highest
    token ever granted. Expiry alone no longer qualifies, nor does merely having
    a different Grant reference. The current-token write can still exercise a
    resumed holder's old token, as the shared schedules require.
    <!-- derives: C1.1, C1.2, F1.3, T3 -->
34. Aliases work in every action target, subject to process roles: grantor is a
    lease node and holder a client. Literal/alias role mismatches reject. Aliases
    before any possible Grant reject statically; an unresolved actual binding
    rejects during incremental compilation when the trigger fires.
    <!-- derives: C1.1, C1.4, F1.1, F1.3, A1, A2 -->
35. The format defines `rest` relative to a partition but also permits it outside
    partitions. Outside a partition, this implementation reuses the rest set
    resolved for the most recent partition containing `rest`, including after
    heal. Without that context it rejects ambiguity. Group selectors expand to
    concrete actions; each concrete process must have the operation's valid
    role. A group fault emits a Fault record per concrete target.
    <!-- derives: C1.1, C1.4, F1.1, F1.2, F1.3, A1, A2 -->
36. A2 uses two-phase validation: definite explicit-state errors reject at load;
    alias-dependent state is validated against frozen concrete IDs before action
    effects. Uncertain static states are not guessed. Pause/resume retain the
    F1.3 holder/lifetime checks when applied. Invalid lease/storage pauses reject.
    <!-- derives: C1.4, F1.1, F1.3, A1, A2 -->
37. Quiescence counts requests and queued writes/acks for running, unpaused,
    current client incarnations. Paused/crashed/old-incarnation work is excluded.
    Raft maintenance RPCs are not client workload. The former unconditional
    50 ms end drain is replaced by this actual-work predicate. `end: start` is
    rejected: v2 ends are an observable event or quiescent.
    <!-- derives: C1.3, C1.4, F1.1, F1.3, T1, E1 -->
38. E1 uses a five-second operational wait and the existing three-second stable
    eligibility horizon. An unanswered eligible request is checked through C1.4,
    including when a pending step prevents reaching the end. No eligible horizon
    means UNEXPLAINED, not a liveness failure. Duration remains a trusted sidecar
    certificate, never cross-process event ordering or unbounded liveness proof.
    <!-- derives: C1.4, F1.1, F1.2, F1.3, T3, E1, E2 -->
39. A witnessed clause failure takes priority over end/trigger incompleteness
    and a later operational error. A malformed trace that cannot establish the
    failure remains UNEXPLAINED. No result attributes a model divergence.
    <!-- derives: C1.1, C1.2, C1.3, C1.4, E2 -->
40. P7 now bypasses storage acceptance after restart and enqueues a success reply
    for that unaccepted attempt. The actual C1.3 path is broken without adding a
    schedule fault or forging an acceptance event. E2 preserves the resulting
    failure if the subsequent WriteAccept trigger cannot fire. Other mutations
    retain their existing enforcing-path placement.
    <!-- derives: C1.3, F1.1, T1, E2 -->
41. P10 executes its explicit first target n1. Its descriptive comment calls
    that node a non-leader, but Raft may elect it during setup; the runner does
    not rewrite the shared action to choose another node. C1.4 covers either
    case with the connected surviving majority.
    <!-- derives: C1.4, F1.1, A1 -->
42. V2 runs have a v2 marker in their unique IDs and require committed v2
    preregistration. M1 receipts stay historical. Git's unavailable GPG signer
    is disabled only for each commit command; the required OTS post-commit hook
    still runs and adds its stamp commit. The entire round stays in this clone.
    <!-- derives: C1.1, C1.2, C1.3, C1.4, T1, A1, E1, E2 -->

## V2 timing and blockers

<!-- derives: C1.1, C1.2, C1.3, C1.4, T1, T2, T3, A1, A2, E1, E2 -->
Wall-clock measurement began at 2026-10-20 23:33:13 UTC, before reading the brief.
The final reported elapsed time includes the adapted-version commit and its
stamp hook. It is human workflow metadata, never observe ordering. Blocked: none.

## Schedule format v2.1 — current round

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, A1, A2, E1, E2 -->
This section is additive; the prior rounds above remain historical. The current
checkout is the fresh full clone on impl-v2.1. Predictions were committed first
as `dc93d1e` (OTS stamp `1dc4570`), and the implementation checkpoint is `9ff6584`
(stamp `4b9688d`). All commits in this round use normal signing, without signing
configuration overrides. No shared input was edited and no out-of-brief artifact
was read.

The two required commands each exit 0:

```sh
# derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3, T1, A1, A2, E1, E2
impl/run.sh --all --seeds 3
impl/run.sh --mutations --seeds 3
```

All thirteen shared schedules PASS on each seed (39/39); all twelve mutations
FAIL their predeclared clause on each seed (36/36, 12/12 kills across three seeds).
The complete fixture suite and go vet pass. No prediction missed and no amendment
was needed. Detailed per-seed receipts, input/trace hashes and the P10 selector
binding evidence are in [RESULTS-v2.1.md](RESULTS-v2.1.md). The false-suspicion
run remains observed, not a paired correctness proof. No mutation was re-placed;
P10's existing C1.4 mutation now leaves c2's request unanswered after the first
non-grantor crash. The same qualified three-second horizon checks it.

## New v2.1 interpretations and clarified rules

43. Interpretation 30 is now normative v2.1 T1: the predecessor's synchronous
    Request, WriteAttempt and Fault count after successor arming. The existing
    cursor behavior is unchanged and the exact action boundary carries an
    explicit v2.1 T1 derivation comment; the synchronous/fresh-event regressions
    remain passing. Checkers introduce no wall-clock ordering.
    <!-- derives: C1.1, C1.3, F1.1, T1, E1 -->
44. `non-grantor` excludes the issuer of the most recent observable Grant; it
    does not probe the current Raft leader. Among up lease nodes it selects the
    lowest trailing decimal identifier number, with lexical tie-breaking for
    equal numbers. Missing/overflowing numeric suffixes reject rather than
    silently inventing an order. All shared nodes are n1, n2 and n3. Selection
    is frozen at trigger firing, before the existing T2 delay.
    <!-- derives: C1.1, C1.4, F1.1, A1, A2, T2 -->
45. Only a successfully applied `crash: non-grantor` updates the remembered
    target. Resolving a selector, partition membership, or crashing a literal
    node does not. `restart: non-grantor` uses that remembered ID regardless of
    subsequent candidate or grantor changes; it never chooses another up node.
    No remembered crash rejects; restarting an already running remembered node
    rejects under A2. Restart does not clear the record; the next selector crash
    replaces it. This is injector state, not protocol authority or durable data.
    <!-- derives: C1.4, F1.1, A1, A2 -->
46. The new selector is reserved and role-checked as a lease node in every
    supported action target and partition position. Client-only operations
    reject it. Before any possible/actual Grant, or with no up eligible node,
    resolution rejects. Partition use selects normally and does not change
    remembered crash state. Static and incremental A2 validation are retained.
    <!-- derives: C1.4, F1.1, F1.2, F1.3, A1, A2 -->
47. The rewritten shared P10 supersedes interpretation 41: it first observes a
    Grant, crashes a selected up non-grantor, obtains another grant, restores the
    selected node, then crashes the observable grantor and requests again. The
    runner executes those shared actions without substituting a literal n1 or
    hidden leadership test. Baseline evidence contains three grants and matching
    selector crash/restart on each seed; the mutation still fails C1.4.
    <!-- derives: C1.4, F1.1, T1, A1, A2, E1 -->
48. The previous round's signing workaround is historical: this round commits
    normally with signing enabled, and lets each OTS hook add its stamp commit.
    Runner IDs and the committed-prediction gate now identify v2.1; old evidence
    remains unchanged. Wall time begins 2026-10-21 00:51:37 UTC and is reported
    through the final commit and hook; it is workflow metadata only.
    <!-- derives: C1.1, C1.4, T1, A1, E1, E2 -->

<!-- derives: C1.1, C1.2, C1.3, C1.4, T1, A1, E1, E2 -->
Current v2.1 blocked items: none. Bounded sampling and the trusted finite liveness
certificate remain the limitations recorded in previous rounds.

## X1 contract v2 — fenced reads

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, E2 -->
This additive section records the X1 adapt round on x1-adapt-impl. Predictions
for all nineteen schedules and eighteen mutations, separately for seeds 1–3,
were signed and committed as `fc87c3b`, then OTS-stamped by `9d153c5`, before
any X1 build or outcome-bearing execution. Implementation checkpoint `7bc3488`
was signed and stamped by `922d690`. No v1 clause, prior prediction, or historical
evidence was retired or rewritten. Repository reading stayed within the brief's
allowed inputs and own artifacts; no model, experiment or other docs were read.

The read workload/compiler, storage/client paths, observable records, provenance
and independent C2.1/C2.2 log checkers now derive explicitly from C2.x. The six
new enforcing-path mutations preserve P1–P12's placements. To run from the root:

```sh
# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, T1, T2, T3, A1, A2, E1, E2
impl/run.sh --all --seeds 3
impl/run.sh --mutations --seeds 3
# One shared schedule, optionally its paired mutation:
impl/run.sh P18 --seeds 3
impl/run.sh P18 --mutation P18 --seeds 3
```

Both required matrix commands exited 0. All 57 schedule runs PASS; all 54 mutation
runs FAIL their declared clause, giving 18/18 kills on all three seeds. The full
Go fixture suite and vet pass. Test-first red receipts record the initial missing
read language/path/value handling, followed by green fixtures; those red runs
were before adaptation and are not post-adaptation schedule prediction misses.
No schedule/mutation prediction missed or needed amendment. All 111 runs' raw
JSONL and sidecars, 48 baseline read-decision provenance rows, three P18 late
snapshot witnesses, input hashes and per-seed table are linked from
[RESULTS-x1.md](RESULTS-x1.md). No model/implementation divergence is attributed.

## New X1 interpretations

49. A read presents an actually held current or numerically superseded token;
    serving compares it to the highest token of an accepted write, not the
    highest granted token or wall-clock expiry. Equality is allowed. Serving
    never advances that ledger, even when the read token is larger.
    <!-- derives: C2.1, C1.2, F1.1, F1.2, F1.3, T3 -->
50. Storage's single key starts with the empty string. Both its accepted-write
    ledger and stored value survive storage restart. Serving atomically captures
    the current value into a reply; subsequent writes cannot change that reply.
    Reads and rejections never modify the stored value.
    <!-- derives: C2.1, C2.2, C1.2, F1.1 -->
51. An empty served value is explicitly serialized as `value: ""` on ReadAccept
    and served ReadAck. ReadReject and rejected ReadAck omit value. Decoding
    retains field presence separately from its string contents. Read attempts
    and decisions carry the originating grantor term and exact causal authority
    references; read acks name the decision.
    <!-- derives: C2.1, C2.2, F1.1, F1.2, F1.3 -->
52. The v3 read action is part of the closed workload language: current/stale
    selection, client-only roles, A1 freezing, T3 availability/token waits and
    E1 draining match writes. A read action cannot supply a write value or fault
    cell. Its synchronous ReadAttempt can trigger its successor under T1. All
    v2.1 alias and remembered non-grantor semantics remain in force.
    <!-- derives: C2.1, C2.2, F1.1, F1.3, T1, T2, T3, A1, A2, E1 -->
53. Read traffic uses the existing sampled network: within-side reordering,
    one-third duplicate sends, permanent loss for sends across a cut, delivery
    connectivity checks, and paused-client reply queues. Client crash clears
    grants and changes incarnation, so old replies cannot reach its restart.
    Wire messages already handed to the external simulated network may arrive
    after storage restart if they were not dropped while storage was down; this
    does not retain a storage process inbox or introduce a new fault cell.
    <!-- derives: C2.1, C2.2, F1.1, F1.2, F1.3 -->
54. C2.1 is checked using storage's local sequence and only accepted writes to
    reconstruct its durable maximum. Both read decision types must report that
    ledger, while a served read must have token >= maximum. Reads never update
    the reconstructed maximum. C2.1 states a necessary condition for service;
    rejecting a non-stale read alone is not scored as a C2.1 violation.
    <!-- derives: C2.1, C1.2, F1.1, F1.2, F1.3 -->
55. C2.2's independent checker reconstructs the stored value from the exact
    WriteAttempt that each storage WriteAccept names, in storage sequence order.
    It compares every ReadAccept to that reconstructed value. It reads no live
    ledger, client state or engine value; JSONL line order and wall clocks do not
    determine causal ordering. Storage sequence continuity spans restart.
    <!-- derives: C2.2, C1.2, F1.1, F1.2, F1.3 -->
56. Every served ack must identify a served read of that same client, key and
    token, with the exact served value. A precisely correlated attempt never
    served is C2.2 FAIL; an existing serve whose reference was omitted is
    UNEXPLAINED missing evidence. Missing value fields or missing provenance alone
    are also UNEXPLAINED. A witnessed wrong snapshot/value remains C2.2 FAIL even
    if another part of the trace lacks provenance or the end is unreachable.
    <!-- derives: C2.2, F1.1, F1.2, F1.3, E2 -->
57. P13/P14/P15 mutations bypass only the read comparison after crash, partition
    or resume, respectively. They preserve the write ledger and its reported
    highest_before, exposing stale service directly to C2.1. P1–P12 remain at
    their previous enforcing paths; no re-placement was necessary this round.
    <!-- derives: C2.1, C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
58. P16 skips serving a read after a crash and fabricates its served ack. P17
    fabricates a served ack for a read sent across the partition and never served.
    Both preserve attempt correlation so the checker can discriminate unserved
    reads from missing references. P16 can leave its ReadAccept trigger
    unreachable; E2 still scores the earlier witnessed C2.2 violation.
    <!-- derives: C2.2, F1.1, F1.2, E2 -->
59. P18 deliberately reloads current storage value at delivery after resume,
    instead of delivering the captured snapshot. The baseline's served v1 and
    later v2 write are causally before the late ack on every seed; baseline
    carries v1 and mutation carries v2, demonstrating the value part of C2.2.
    <!-- derives: C2.2, F1.3 -->
60. Read clauses add safety checks only; C1.4 and its qualified three-second
    progress certificate are unchanged. The five-second operational bound is
    not a read liveness promise. Seeds 1–3 sample T2 delay (0–2 ms), message delay
    (1–5 ms), ordering and duplicates; Raft's election timing remains unseeded.
    Runner IDs use x1-v3 and the committed-prediction gate requires this round's
    preregistration. Only declared-clause failures kill mutations. Commits remain
    signed, with OTS hooks allowed to finish. Round wall time starts at
    2026-10-21 01:06:33 UTC and is reported through the final commit and stamp;
    it is workflow metadata only. Finite sampling is not exhaustive proof.
    <!-- derives: C2.1, C2.2, C1.4, F1.1, F1.2, F1.3, T2, E1, E2 -->

## Blocked

<!-- derives: C2.1, C2.2, C1.4, F1.1, F1.2, F1.3, E1, E2 -->
Current X1 blocked items: none. Prior rounds and their historical limitations
remain above; finite sampling and the trusted C1.4 certificate still apply.

## Schedule format v2.2 and observe schema v3

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, A1, A2, E1, E2 -->
This additive section records the v22-impl round. Predictions were signed and
committed first as `b3cbaf6`, then OTS-stamped by `5adaff8`. Implementation
checkpoint `a912afc` is signed and stamped by `160a069`. No prediction was revised.
There is no contract, failure-model or schedule change, and no mutation was
re-placed. The normative remembered-restart rule now carries v2.2 A1 comments;
every write/read ack carries explicit schema-v3 answers from its original attempt.
Independent provenance checking validates those references as well as causes.

Both required commands exit 0:

```sh
# derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, A1, A2, E1, E2
impl/run.sh --all --seeds 3
impl/run.sh --mutations --seeds 3
```

Every shared schedule passes seeds 1–3 (57/57); every mutation fails its declared
clause on seeds 1–3 (54/54, 18/18 kills). No verdict changed from the predeclared
X1 results and no prediction amendment was needed. All 34 top-level Go tests and
vet pass. Test-first red receipts show the missing fields and same-token retry
ambiguity before adaptation, followed by passing regressions. Raw traces,
sidecars, ack-reference audits, hashes and the complete per-seed results are in
[RESULTS-v2.2.md](RESULTS-v2.2.md). Only own artifacts and brief-permitted inputs
were read; other docs, model, experiments and git log were not read.

## New v2.2 / schema-v3 interpretations

61. Interpretation 45 is now normative v2.2 A1: restart non-grantor binds to the
    most recent successfully applied crash non-grantor, even if that node is now
    the grantor. Missing prior selector crash rejects. Runtime binding, successful
    crash recording, static rejection and regression carry explicit v2.2 tags;
    their behavior is unchanged. A2 still rejects restart of a running process.
    <!-- derives: C1.4, F1.1, A1, A2 -->
62. Every WriteAck and ReadAck, including rejection, late/duplicate receipt and
    deliberate mutation reply, names the original wire attempt in answers.
    It does not name a storage decision, Grant, most recent attempt or retry.
    Storage-decision causes remain intact. Non-ack emissions omit answers.
    <!-- derives: C1.3, C2.2, F1.1, F1.2, F1.3 -->
63. Schema-v3 answers is redundant evidence, not a new causal edge or contract
    clause. The checker requires an existing operation-appropriate attempt with
    matching client/process, key and token, and causal reachability through the
    recorded history. It never inserts an answers edge to make a bad reference
    appear causal. Missing or mismatched evidence is UNEXPLAINED unless a separate
    contract violation has already been witnessed under E2.
    <!-- derives: C1.3, C2.2, F1.1, F1.2, F1.3, E2 -->
64. Where an ack directly names a storage decision, answers must equal that
    decision's exact attempt reference. Merely reaching an earlier same-token
    attempt through local sequence or prior decisions is insufficient. Fabricated
    mutation replies instead name their direct original attempt, allowing C1.3
    and C2.2 to retain the discriminated unaccepted/unserved failure evidence.
    <!-- derives: C1.3, C2.2, F1.1, F1.2, F1.3, E2 -->
65. Current fixtures explicitly name their attempts; malformed raw-record tests
    bypass no validation and are not repaired automatically. Historical traces
    retain their original schema and are not rewritten. The current strict v3
    provenance checker reports missing answers if asked to check older traces.
    New runs of every old schedule retain their prior contract verdicts.
    <!-- derives: C1.3, C2.2, F1.1, F1.2, F1.3 -->
66. Runner IDs identify v22-observe-v3, and the execution gate requires this
    round's committed registration. Sampling and all prior operational/liveness
    bounds stay unchanged: seeds 1–3, T2 0–2 ms, jitter 1–5 ms, reordering and
    one-third duplicate sends, with unseeded Raft election timing. Normal signed
    commits run the OTS hook. Wall time starts 2026-10-21 03:57:24 UTC and includes
    the final commit/hook; it supplies no event ordering. The pre-existing
    untracked .venv remains untouched and uncommitted.
    <!-- derives: C1.4, C1.3, C2.2, F1.1, F1.2, F1.3, T2, E1, E2 -->

## Blocked

<!-- derives: C1.4, C1.3, C2.2, F1.1, F1.2, F1.3, E1, E2 -->
Current v2.2/schema-v3 blocked items: none. Finite sampling and the trusted C1.4
horizon certificate retain their previously documented limits.

## X2 adaptation checkpoint (before shared schedule execution)

<!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F1.1, F1.2, F1.3, F2.1, F2.2, L1, L2, L3, E1, E2, E3, T3 -->
Predictions and scoring for all 31 shared schedules and 30 mutations were signed
and committed as `6c58815`, OTS stamp `e39c88c`, before adaptation or tests.
The initial red fixture receipt records absent link-language/API support. The
six focused X2 tests and full Go fixture suite pass at this checkpoint; no shared
schedule or mutation has yet run. The existing transport fixture expecting a
cut/heal history to invalidate a later reply send was replaced to assert v2's
opposite rule. The read storage fixture now pumps the distinct send and delivery
stages. These are semantic fixture adaptations, not changes to predictions.

### Interpretations established from the inputs

67. **Contradicted:** interpretations 11, 21, 25 and 53 discard queued messages
    on a new cut or recheck connectivity at delivery. Failure-model v2 fixes link
    fate at send. Requests admitted before a cut can reach storage afterwards;
    sent replies survive later cuts. Messages sent on down links are permanently
    lost. F1.1 process availability and client incarnation still govern receipt.
    The prior text and receipts above are retained as history.
    <!-- derives: C1.3, C2.2, F1.1, F1.2, F2.1, F2.2 -->
68. **New:** storage prepares each reply locally for 8 ms before its actual send;
    send then samples 1–5 ms network delivery. This makes the decision-to-send
    interval explicit. A decision-triggered fault can precede send, explaining
    the lost-ack schedules without retroactively losing an already sent packet.
    Raft's reply relay independently admits the reverse direction at its send,
    with no cut-history or receive-time link recheck. Raft retains its existing
    protocol and process-incarnation checks.
    <!-- derives: C1.1, C1.3, C1.4, C2.2, F1.1, F2.1, F2.2 -->
69. **Extended:** interpretations 19 and 53's partition environment is an
    accumulated directed matrix. F1.2 adds all cross-side links to the same
    matrix; F2.1 adds both directions per pair; F2.2 adds just the named direction.
    Every heal clears the whole matrix. L1 selectors freeze when the trigger
    fires, self-pairs are removed and duplicates are harmless. Fault links record
    resolved directed pairs, including already-down links named by that action;
    a heal explicitly serializes links: []. The old cell IDs remain live.
    <!-- derives: F1.2, F2.1, F2.2, L1, L2, A1, T2 -->
70. **Extended:** interpretations 16 and 38 require literal direct connectivity:
    requester, storage and some two up lease nodes form a bidirectional clique.
    Counting two lease nodes reachable from the requester/storage is insufficient
    unless those lease nodes also connect to each other. The observable grantor
    need not belong to that clique. The engine and offline checker reconstruct
    this premise independently. The trusted three-second duration certificate
    remains a limitation; bounded samples do not prove eventuality.
    <!-- derives: C1.4, F1.1, F2.1, F2.2, L3 -->
71. **Extended:** interpretation 52 includes read requests and replies in
    quiescence. T3 allows another read/write despite a lost previous reply; only
    a prior request waits for its answer. Link-lost grant completions leave the
    existing RequestState outstanding: a failed send emits no delivered Grant,
    and the next attempt uses a fresh committed allocation. Allocation gaps are
    allowed; no duplicate Grant record is used for retransmission. A reached
    event bound has priority over readiness and cannot silently become PASS.
    <!-- derives: C1.1, C1.4, C2.2, F2.1, F2.2, T3, E1, E3 -->
72. **New:** P19–P30 have the preregistered enforcing-path mutations. P24 skips
    a later write's acceptance (leaving the first WriteAccept trigger intact)
    and invents success despite the down reverse link. P29/P30 bypass reply loss
    with a value different from the actual served snapshot, exposing C2.2's value
    condition. P25/P26 suppress the same grant-service mechanism used normally;
    a baseline failure means there is no working half to mutate and will be
    reported as such. No formal model or model mutation has been read or authored.
    <!-- derives: C1.1, C1.2, C1.3, C1.4, C2.1, C2.2, F2.1, F2.2, E2 -->

### Access and timing record

<!-- derives: C1.1, C1.4, F2.1, F2.2 -->
The first recorded clock is 2026-10-21 05:51:48 UTC; final wall time will be
reported through the adapted commit and hook. Before reading the complete brief,
the agent attempted the absent steward seed files, read an external generic
using-superpowers workflow SKILL.md, and later displayed six git-log titles.
These are access-list deviations, recorded explicitly rather than asserting
perfect scope compliance. No formal-model artifact or other author's code was
read. After the brief, source/input reads and all task outputs stay in its listed
paths (plus git commit/status metadata). The untracked .venv is untouched.

### X2 source-review correction before final matrices

<!-- derives: C1.3, C1.4, C2.2, F1.1, F2.1, F2.2, L3 -->
The initial 31×3 baseline matrix at 94549e3 passed all 93 runs; its receipt and
traces are retained. Additive registration `3b73f2c` (stamp `2e62373`) records a
source-review issue in the new local-send stage: storage restart retained local
unsent reply work. The preregistered regression failed as expected, then passed
after crash discards only pendingSend entries. External packets already sent
remain eligible for delivery after the sender restarts. This correction enforces
F1.1's volatile-state rule, and was not prompted by a failed shared schedule.
The full fixture suite passes again. Additional fixtures independently exercise
runtime clique eligibility and verify that a failed reverse grant send leaves
the requester outstanding until a later allocation's reply succeeds. No baseline
or mutation prediction, placement, horizon, schedule or scoring rule changed.
