<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
# Implementation author v1

This directory is the implementation author's independent artifact. No model,
steward notes, other documentation, existing schedules, or git history were read.
The permitted brief, contract, failure model, pairs, schedule format, schema and
AGENTS.md were read. The brief's explicit access list supersedes AGENTS.md's
request to read and append steward seed documents.

## Design and plan

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
Schedules are under `impl/testbed/schedules/`; JSONL output is under
`impl/observe/`. These relative paths implement the shared interface while
honouring the instruction to produce everything under `impl/`. Build artifacts,
module caches and run output are ignored. The runner accepts a schedule basename
or a YAML path within its own directory tree. Exit 0 means expected results;
exit 1 means an unexpected result; input/operational errors say UNEXPLAINED.

## Sampling

<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
Default: three seeds, numbered 1 through N. Each seed varies workload delivery
jitter, Raft RPC timeout, and duplicate write delivery. Raft's own election
randomness is additional nondeterminism, so a seed does not promise bit-for-bit
replay. Observe traces are the replay evidence. This is bounded sampling, not
exhaustive verification. Per-seed results and mutation kills are printed.

## Interpretations

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

Current blocker after the steward's parent-root change: the exact directory
`/home/tony/projects/tupay/.git/worktrees/tupay-impl` is still a separate read-only
mount. `findmnt` reports the parent `.git` as rw and this child as ro. Retrying
`git add` and `git commit` still fails creating `index.lock`. The child needs an
explicit writable-root entry. No outcome-bearing run has occurred; preregistration
is unchanged and uncommitted. The historical initial report follows below.

### Git metadata is outside writable sandbox

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

## Current delivery and remaining execution

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
