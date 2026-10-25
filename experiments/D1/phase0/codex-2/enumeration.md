# Environment contracts required by Raft

<!-- derives: BRIEF.md Task, Format, Rules; source sections cited per entry. No C/F clause or failure-cell identifiers are supplied in this checkout; none are invented here. -->

Scope: obligations on external services, hosts, operators, application state machines, and clients. Optional mechanisms are identified in their contracts. “Stated” includes explicit interface obligations whose failure consequences are inferred. Silent scores estimate unnoticed violations per deployment-year, not total failures or severity; these are qualitative judgments from general systems experience, not measurements in the dissertation.

### E1
- contract: The host must restrict server failures to stopping and recovery rather than arbitrary execution.
- source: §2 "Servers are assumed to fail by stopping;"
- stated: stated
- violation: A faulty CPU or memory bit flip changes a vote, term, or command while the process continues.
- at-risk: Election Safety, Log Matching, Leader Completeness, and State Machine Safety can fail because the server no longer follows the transition rules.
- detectable: partly — checksums and assertions catch some corruption, but plausible incorrect execution can evade them.
- silent: 1 — Silent arbitrary execution faults are rare on ordinary hosts.
- basis: general systems experience

### E2
- contract: The transport must deliver authentic, unaltered messages attributable to their actual sending server.
- source: §8.1 "The network may reorder, drop, and duplicate messages."
- stated: implicit
- violation: A proxy corrupts an entry payload or an attacker fabricates successful replication acknowledgments.
- at-risk: Log Matching or Leader Completeness can fail when messages assert entries or votes that never existed; this exceeds loss, duplication, and reordering.
- detectable: partly — authentication and integrity checks can reject many altered messages, but cannot establish an honest endpoint.
- silent: 1 — Undetected message forgery or corruption is rare in ordinary deployments.
- basis: general systems experience

### E3
- contract: Stable storage must retain an acknowledged current term across crashes and restarts.
- source: §3.8 "each server persists its current term and vote;"
- stated: stated
- violation: A storage rollback restores a term older than the last completed persistence operation.
- at-risk: Election Safety and Leader Completeness are at risk because the recovered server can accept obsolete leadership and repeat prior decisions.
- detectable: partly — peers may expose a regression, but an isolated recovered server cannot prove its prior term.
- silent: 1 — Silent acknowledged-write loss is rare with functioning durable storage.
- basis: general systems experience

### E4
- contract: Stable storage must retain an acknowledged vote across crashes and restarts.
- source: §3.8 "this is necessary to prevent the server from
voting twice in the same term"
- stated: stated
- violation: A power failure loses a vote that fsync reported durable.
- at-risk: Election Safety fails if the server votes for two candidates in one term; conflicting same-term logs can follow.
- detectable: partly — external vote histories can expose double voting, but ordinary recovery has no independent copy.
- silent: 1 — Silent loss of durable vote records is rare.
- basis: general systems experience

### E5
- contract: Stable storage must preserve the contents and order of acknowledged durable log entries.
- source: §3.8 "this prevents committed entries from being lost or “uncommitted” when servers restart."
- stated: stated
- violation: A controller drops or corrupts an acknowledged log tail after power loss.
- at-risk: Leader Completeness and State Machine Safety can fail when a quorum no longer remembers a committed entry.
- detectable: partly — checksums detect many corruptions, but a valid old log prefix can look legitimate.
- silent: 1 — Silent durable-log rollback is uncommon.
- basis: general systems experience

### E6
- contract: The storage stack must honor completion and ordering barriers used to persist Raft state before external acknowledgments.
- source: §3.8 "Each server also persists new log entries before they are counted towards the entries’ com-
mitment;"
- stated: implicit
- violation: A drive reports a successful flush while data remains only in an unprotected volatile cache.
- at-risk: Leader Completeness and acknowledged-write durability fail if counted replicas disappear after a crash.
- detectable: partly — I/O errors are visible, but dishonest flush completion normally requires independent crash testing to expose.
- silent: 1 — Most ordinary storage honors flushes; silent violations remain possible.
- basis: general systems experience

### E7
- contract: The process manager must prevent two live processes from using one voting server identity.
- source: §4 "there would be an extra vote"
- stated: implicit
- violation: A VM clone and its original both run with the same server identity and separate state.
- at-risk: Election Safety can fail because one logical voter can supply inconsistent votes to different candidates.
- detectable: partly — competing connections or identity leases can expose clones, but partitioned clones may evade detection.
- silent: 1 — Unnoticed concurrent identity clones are unusual.
- basis: general systems experience

### E8
- contract: An operator must fence the old server permanently when replacing a member by reusing its network address.
- source: §4 "the administrator must guarantee that the replaced server will never come back up,"
- stated: stated
- violation: An old machine reboots after its address has been assigned to a replacement.
- at-risk: Election Safety and subsequent log safety are at risk from the extra vote explicitly identified by the source.
- detectable: partly — duplicate endpoints or conflicting histories may reveal it, but a partition can hide the old server.
- silent: 1 — Accidental unfenced replacement is rare but plausible.
- basis: general systems experience

### E9
- contract: Recovery tooling must not restart a server with its old identity after any of its persistent state has been lost.
- source: §3.8 "If a server loses any of its persistent state, it cannot safely rejoin the cluster with its prior identity."
- stated: stated
- violation: An administrator restores an old VM snapshot or deletes the data directory and reuses the member ID.
- at-risk: Election Safety or Leader Completeness can fail because the server forgets votes or committed entries.
- detectable: partly — a missing-state marker can help, but a self-consistent old backup need not disclose rollback.
- silent: 2 — Backup restoration can silently reuse obsolete state.
- basis: general systems experience

### E10
- contract: Operators must preserve a majority of persistent histories to retain both committed data and normal recovery progress.
- source: §3.8 "If a majority of the cluster loses its persistent state, however,
log entries may be lost"
- stated: stated
- violation: A shared storage failure or coordinated restore wipes most members.
- at-risk: Acknowledged-write durability and availability can be lost; ordinary membership changes cannot repair the missing quorum.
- detectable: partly — lost volumes may be obvious, but valid older backups can conceal lost commits.
- silent: 1 — Unnoticed majority state loss is rare.
- basis: general systems experience

### E11
- contract: Deployment configuration must provide an operational majority for availability.
- source: §2 "They are fully functional (available) as long as any majority of the servers are operational"
- stated: stated
- violation: Maintenance stops three members of a five-member cluster.
- at-risk: Availability fails because no election or new commitment can collect a majority; safety need not fail.
- detectable: yes — lack of quorum responses and inability to commit are observable.
- silent: 1 — Quorum outages normally produce visible errors, so silent violations are rare.
- basis: general systems experience

### E12
- contract: The network must allow the operational majority to exchange messages for progress.
- source: §2 "and can communicate with each other and with clients."
- stated: stated
- violation: Firewalls split all live members into groups smaller than a quorum.
- at-risk: Availability fails despite healthy processes because votes and replication cannot reach a majority.
- detectable: yes — timeouts and failed quorum communication reveal the symptom.
- silent: 1 — Partitions normally manifest as visible timeouts.
- basis: general systems experience

### E13
- contract: The network must connect clients to the available cluster for client-visible availability.
- source: §2 "and can communicate with each other and with clients."
- stated: stated
- violation: A working quorum is unreachable from the application network.
- at-risk: Client availability fails even though the cluster itself can elect and commit.
- detectable: partly — clients see timeouts, but servers cannot observe every client-side route.
- silent: 1 — Client connectivity failures usually yield errors.
- basis: general systems experience

### E14
- contract: Host scheduling, storage, and network latency must permit RPC broadcasts substantially faster than the configured election timeout for stable leadership.
- source: §3.9 "broadcast time should be an order of magnitude less than the election timeout"
- stated: stated
- violation: Disk stalls, CPU starvation, or long WAN latency delay heartbeats past election timeouts.
- at-risk: Availability and timely leader election degrade through repeated elections; basic safety remains timing independent.
- detectable: yes — heartbeat latency, election frequency, and scheduler stalls can be measured.
- silent: 2 — Transient stalls occasionally occur without a separately reported infrastructure error.
- basis: general systems experience

### E15
- contract: Servers must remain operational for intervals substantially longer than election timeouts to sustain progress.
- source: §3.9 "The
election timeout should be a few orders of magnitude less than MTBF"
- stated: stated
- violation: Crash loops or repeated orchestrator restarts terminate candidates before they can lead.
- at-risk: Availability fails when no stable leader lasts long enough to commit.
- detectable: yes — restart rates and leadership durations expose the condition.
- silent: 1 — Persistent crash loops normally produce visible failures.
- basis: general systems experience

### E16
- contract: The timer and scheduling service must eventually deliver election timeouts on surviving candidates.
- source: §3.4 "Each candidate restarts its randomized
election timeout at the start of an election"
- stated: implicit
- violation: A timer service freezes indefinitely while no leader exists.
- at-risk: Availability fails because surviving followers or candidates never retry an election.
- detectable: partly — another watchdog can detect timer starvation, but a fully suspended process cannot self-diagnose.
- silent: 1 — Indefinitely frozen timers rarely remain unnoticed.
- basis: general systems experience

### E17
- contract: The randomness service must supply sufficiently decorrelated election timeout draws across servers and retries.
- source: §3.4 "This spreads out the servers so that in most cases only
a single server will time out;"
- stated: implicit
- violation: Cloned PRNG states cause every candidate to choose the same timeout repeatedly.
- at-risk: The promised rapid resolution of split votes and availability degrade; safety does not depend on good randomness.
- detectable: partly — repeated equal timeout draws can be monitored but finite observations cannot establish independence.
- silent: 2 — Cloned seeds and correlated startup can be silently deployed.
- basis: general systems experience

### E18
- contract: During membership changes the environment must keep a majority of the old configuration available until the new configuration commits.
- source: §4.2.4 "a
majority of the old configuration is available (at least until Cnew is committed)"
- stated: stated
- violation: Automation powers off old members before the replacement configuration commits.
- at-risk: Availability during membership change fails because the old quorum is still needed.
- detectable: yes — old-configuration quorum responses and transition status are observable.
- silent: 1 — Loss of the necessary quorum usually causes visible stalled changes.
- basis: general systems experience

### E19
- contract: During membership changes the environment must provide an available majority of the new configuration.
- source: §4.2.4 "a majority
of the new configuration is available."
- stated: stated
- violation: New members share an unreachable subnet or are stopped during the transition.
- at-risk: Membership-change progress and client availability can stall without the new quorum.
- detectable: yes — replication responses and configuration commitment reveal the shortage.
- silent: 1 — A stalled change normally exposes this violation.
- basis: general systems experience

### E20
- contract: Membership management policy must retain enough replicas to meet the intended durability and failure-tolerance target.
- source: §4.4 "it could then be left
with too few replicas to satisfy the intended durability and fault-tolerance requirements."
- stated: stated
- violation: An automatic failure handler repeatedly removes failed members until only one remains.
- at-risk: The operator-facing fault-tolerance target fails even if current Raft operations succeed safely.
- detectable: partly — replica count is visible, but the intended target must be supplied externally.
- silent: 2 — An undersized cluster can quietly continue serving requests.
- basis: general systems experience

### E21
- contract: Replacement orchestration must add the replacement before removing the old member when continuous single-failure tolerance is required.
- source: §4.4 "it is prefer-
able to add servers before removing servers."
- stated: stated
- violation: A three-member cluster is reduced to two before the new member is added.
- at-risk: Continuous one-failure availability is lost during replacement because both remaining voters are required.
- detectable: yes — configuration size and operation order can be audited at runtime.
- silent: 2 — Remove-first procedures can silently reduce resilience without immediate request errors.
- basis: general systems experience

### E22
- contract: Bootstrap tooling must supply one coherent initial cluster configuration rather than independently bootstrap competing clusters as one service.
- source: §4.4 "one server is
initialized with a configuration entry as the first entry in its log."
- stated: implicit
- violation: Several hosts independently bootstrap singleton clusters behind one service endpoint.
- at-risk: The advertised single consistent service fails because unrelated quorums can acknowledge conflicting histories.
- detectable: partly — cluster identifiers can distinguish histories, but isolated clusters cannot discover each other.
- silent: 1 — Silent conflicting bootstraps are rare.
- basis: general systems experience

### E23
- contract: State machines must compute identical states and outputs from identical initial states and command sequences.
- source: §2 "Since the state machines are deterministic, each computes the
same state and the same sequence of outputs."
- stated: stated
- violation: Replicas use local time, unordered iteration, random numbers, or incompatible application versions.
- at-risk: Consistent replicated-service results fail despite identical logs; Figure 3.2 State Machine Safety alone only constrains applied entries.
- detectable: partly — state hashes can expose divergence, but agreement on a hash is not proof of every output.
- silent: 2 — Hidden nondeterminism can remain unnoticed until a triggering command.
- basis: general systems experience

### E24
- contract: Nondeterministic state-machine inputs must be supplied identically to all replicas through the replicated command.
- source: §11.6 "the effects of client requests must not depend on each server’s current time."
- stated: stated
- violation: Each replica independently obtains a timestamp or external-service response while applying a command.
- at-risk: Single-state-machine behavior and client result consistency fail when identical entries have different effects.
- detectable: partly — deterministic replay or state comparison may catch differences but cannot observe every external dependency.
- silent: 2 — Local time and external reads are easy to introduce silently.
- basis: general systems experience

### E25
- contract: A persistent state-machine service must recover its applied index consistently with its durable application state.
- source: §3.8 "its last applied index must also be persistent."
- stated: stated
- violation: The application database persists an increment but loses its applied-index update, or persists the index before the increment.
- at-risk: Exactly-once effects and state consistency fail through replaying an applied command or skipping an unapplied command.
- detectable: partly — transactional recovery metadata can detect some mismatches; plausible state/index pairs may conceal them.
- silent: 1 — Silent crash inconsistency is rare with correct transactional storage.
- basis: general systems experience

### E26
- contract: The state-machine compaction service must retain recoverable durable effects before releasing the corresponding Raft log prefix.
- source: §5 "the state machine reflects those entries to disk in a way that can recover the current system state."
- stated: stated
- violation: A database signals that compaction is safe while its writes are still only in RAM.
- at-risk: Committed-state durability fails after a crash because neither snapshot nor retained log contains the discarded effects.
- detectable: partly — durable checkpoints can be checked, but false durability acknowledgments are hard to detect online.
- silent: 1 — Premature durable-checkpoint reporting is an uncommon silent fault.
- basis: general systems experience

### E27
- contract: The state-machine recovery service must restore the discarded prefix before processing retained log entries.
- source: §5 "load the state corresponding to the
discarded log entries from disk before it can apply any entries from the Raft log."
- stated: stated
- violation: A plugin starts from empty state and applies only the retained suffix.
- at-risk: Replicated-service correctness fails because commands execute against a missing committed history.
- detectable: partly — checkpoint indices and state hashes may catch it, but application content need not be independently known.
- silent: 1 — Incorrect successful recovery is rare.
- basis: general systems experience

### E28
- contract: Snapshot serialization and loading must faithfully preserve the application state represented by the checkpoint.
- source: §5.1.3 "Saving a snapshot involves serializing the state machine’s
       state and writing that data out to a file, while loading is the reverse process."
- stated: implicit
- violation: The serializer omits a map, changes integer precision, or reconstructs dependencies incorrectly.
- at-risk: Durable state and consistent client results fail after recovery or snapshot installation even if log entries remain consistent.
- detectable: partly — round-trip checks and state hashes catch some omissions; shared serialization defects may evade them.
- silent: 2 — Rarely used fields can be silently omitted until recovery exercises them.
- basis: general systems experience

### E29
- contract: Snapshot services must preserve client deduplication and response information along with application state.
- source: §5.1 "State machines must also
serialize the information they keep for providing linearizability to clients"
- stated: stated
- violation: A snapshot keeps account balances but drops session sequence numbers and cached responses.
- at-risk: Exactly-once linearizability fails when a retried command is applied again after snapshot recovery.
- detectable: partly — snapshot schemas and session checks help, but missing old response records may look like expiration.
- silent: 2 — Incomplete application snapshots can silently pass ordinary traffic.
- basis: general systems experience

### E30
- contract: Snapshot and copy-on-write services must expose a consistent point-in-time state while writes continue.
- source: §5.2 "Disk-based state machines must be able to provide a consistent snapshot of the disk"
- stated: stated
- violation: A volume snapshot combines blocks from before and after a multi-block update.
- at-risk: A follower or recovered node can serve a state that no committed prefix ever produced, violating consistent-service semantics.
- detectable: partly — application invariants or state hashes detect some mixed images, but plausible mixed state can escape.
- silent: 1 — Silent inconsistency in a supported snapshot service is rare.
- basis: general systems experience

### E31
- contract: The filesystem must provide the crash-safe publication semantics used to replace a completed snapshot file.
- source: §5.1.3 "then renames the file when writing is complete and has been
       flushed to disk;"
- stated: implicit
- violation: After power failure the published snapshot name points to a partial file despite successful flush and rename operations.
- at-risk: Recovery and committed-state durability are at risk if the old log has already been discarded.
- detectable: partly — checksums and completeness markers detect some partial files but cannot restore discarded data.
- silent: 1 — Silent violation of correctly requested filesystem durability is uncommon.
- basis: general systems experience

### E32
- contract: The host must provide enough memory for the live state and additional concurrent snapshot copy-on-write data.
- source: §5.1.1 "Servers require additional memory for snapshotting concurrently, which should be planned for
and managed."
- stated: stated
- violation: Snapshot dirty pages exhaust container memory and trigger an OOM kill.
- at-risk: Availability and promised snapshot concurrency degrade; a quorum of simultaneous OOMs stops service.
- detectable: yes — allocation failures, memory pressure, and OOM records expose the violation.
- silent: 1 — Memory exhaustion normally causes observable pressure or termination.
- basis: general systems experience

### E33
- contract: The host must provide enough storage capacity for retained logs, old state, and compaction output simultaneously.
- source: §5.1.2 "requires about 6 times the disk capacity as that needed to store a single copy of the state"
- stated: implicit
- violation: A volume has space for the live database but not the old snapshot, log, and new snapshot together.
- at-risk: Availability fails when durable appends or compaction cannot complete.
- detectable: yes — free-space accounting and failed writes reveal exhaustion.
- silent: 1 — Capacity exhaustion normally emits visible storage errors.
- basis: general systems experience

### E34
- contract: The host must provide sufficient CPU and disk bandwidth for compaction without starving quorum communication and application work.
- source: §5.1.2 "Snapshotting still creates a burst of CPU and disk bandwidth usage that might impact client
performance."
- stated: stated
- violation: All replicas snapshot on saturated disks and miss heartbeats or request deadlines.
- at-risk: Timely client service and stable leadership degrade; the basic safety properties remain intact.
- detectable: yes — resource utilization, heartbeat delays, and request latency expose starvation.
- silent: 2 — Short resource bursts occasionally degrade performance without infrastructure errors.
- basis: general systems experience

### E35
- contract: A state-machine log-cleaning service must preserve every live value and still-needed deletion marker.
- source: §5.3.1 "RAMCloud preserves deletion
commands (called tombstones) as necessary"
- stated: implicit
- violation: A storage library removes a tombstone while an older segment still contains the deleted key.
- at-risk: Durable application correctness fails when deleted data reappears after compaction or recovery.
- detectable: partly — state comparisons can detect resurrection, but a plausible old value need not trigger an invariant.
- silent: 1 — Silent corruption from incorrect cleaner liveness is rare.
- basis: general systems experience

### E36
- contract: A client discovery directory must remain reachable at its well-known location when clients depend on it.
- source: §6.1 "an external directory service, such as DNS, that is
        accessible at a well-known location."
- stated: stated
- violation: DNS becomes unreachable and new clients cannot locate any member.
- at-risk: Client availability fails even with a healthy Raft quorum.
- detectable: partly — clients observe lookup failure, while servers may have no visibility into their resolvers.
- silent: 1 — Directory outages normally produce visible lookup errors.
- basis: general systems experience

### E37
- contract: The discovery directory and its administrative update process must keep the server list inclusive through membership changes.
- source: §6.1 "clients should always be able to find all of the cluster
        servers,"
- stated: stated
- violation: DNS still lists only removed servers because administrative scripts never added replacements.
- at-risk: Clients may fail to find the available leader, defeating client availability despite successful reconfiguration.
- detectable: partly — comparing directory answers with membership detects some omissions, but caches and split DNS complicate observation.
- silent: 2 — Stale discovery records can persist silently while existing connections work.
- basis: general systems experience

### E38
- contract: Networks used for broadcast or multicast discovery must actually support the selected discovery mechanism.
- source: §6.1 "this will
        only work in particular environments that support these features."
- stated: stated
- violation: A deployment moves into a routed cloud network that drops discovery multicast.
- at-risk: New-client availability fails because clients cannot discover the cluster.
- detectable: yes — discovery timeouts and diagnostic probes expose failure.
- silent: 1 — Unsupported discovery generally causes visible connection failure.
- basis: general systems experience

### E39
- contract: Client software must retry reachable alternative members after losing its connection to a server.
- source: §6.2 "If a client loses its connection to the leader (or any particular server), it should
      simply retry with a random server."
- stated: stated
- violation: A client pins all retries to a failed former leader.
- at-risk: Client availability fails even though a new leader can service requests.
- detectable: partly — a client can log its retry targets, but the cluster cannot observe attempts that never reach it.
- silent: 2 — Sticky reconnect policies can silently delay otherwise healthy applications.
- basis: general systems experience

### E40
- contract: Client identity management must prevent distinct active clients from sharing a deduplication identity.
- source: §6.3 "each client is given a unique identifier"
- stated: stated
- violation: Two application instances restore the same session token and issue different commands with the same serial number.
- at-risk: Linearizable exactly-once request semantics fail because one client can receive another command’s cached result.
- detectable: partly — comparing payload hashes may expose collisions, but identical payloads or missing histories conceal them.
- silent: 1 — Accidental active session cloning is uncommon.
- basis: general systems experience

### E41
- contract: Clients must assign distinct serial numbers to distinct commands within a session.
- source: §6.3 "clients assign unique"
- stated: stated
- violation: A client counter resets after restart while the old session remains valid.
- at-risk: Linearizability fails when a new operation is mistaken for an already executed request and returns its old result.
- detectable: partly — payload comparisons detect some reuse but cannot distinguish all new invocations from retries.
- silent: 2 — Counter resets across client recovery can be silently deployed.
- basis: general systems experience

### E42
- contract: Clients must preserve the identity, serial number, and command contents of an operation across retries.
- source: §6.3 "servers must filter out duplicate requests."
- stated: implicit
- violation: A retry allocates a new serial number or changes the command while retaining the old number.
- at-risk: Exactly-once semantics fail through duplicate effects or returning a response for a different operation.
- detectable: partly — conflicting payloads can be rejected, but a fresh ID hides the fact that an operation is a retry.
- silent: 2 — Generic retry layers can silently generate fresh operation identifiers.
- basis: general systems experience

### E43
- contract: Concurrent clients must report a truthful lower bound for sequence numbers whose replies are still outstanding.
- source: §6.3 "the client includes the lowest sequence
number for which it has not yet received a response"
- stated: stated
- violation: A pipelined client advances its response watermark past an unacknowledged request.
- at-risk: The server may discard a response still needed for safe retry, jeopardizing the stated concurrent-request semantics; exact behavior depends on expired-response handling.
- detectable: partly — impossible future bounds can be rejected, but the server cannot know which replies the client actually received.
- silent: 1 — Silent incorrect acknowledgment watermarks are uncommon.
- basis: general systems experience

### E44
- contract: State-machine session expiration must use deterministic replicated inputs rather than independently observed local time.
- source: §6.3 "session expiry must be deterministic, just as normal state
machine operations must be."
- stated: stated
- violation: Each replica expires sessions using its own wall clock.
- at-risk: Replicas can disagree about duplicate suppression and diverge in application state and results.
- detectable: partly — session and state comparisons expose some divergence, but different clocks need not immediately affect a request.
- silent: 2 — Local-clock expiration is an easy silent integration error.
- basis: general systems experience

### E45
- contract: Clients that require continuous session validity must issue keep-alives often enough for the configured expiry policy.
- source: §6.3 "Live clients issue keep-alive requests during periods of inactivity,"
- stated: stated
- violation: A suspended client misses its inactivity deadline.
- at-risk: Continued client availability fails when its session expires; the specified rejection preserves safety.
- detectable: yes — the cluster can detect expiration and reject the old session.
- silent: 1 — Under the specified protocol expiration yields an explicit error rather than silent incorrect execution.
- basis: general systems experience

### E46
- contract: Client recovery must treat an expired session as an uncertain prior outcome rather than blindly resubmitting outstanding effects in a new session.
- source: §6.3 "commands that were executed before the client’s previous session was expired."
- stated: implicit
- violation: An SDK automatically opens a new session and repeats an unacknowledged money transfer.
- at-risk: End-to-end exactly-once semantics fail across session expiration even though each session is handled correctly.
- detectable: partly — the SDK sees expiration but cannot determine the old command outcome without application-specific evidence.
- silent: 2 — Transparent session recreation can quietly duplicate application effects.
- basis: general systems experience

### E47
- contract: Queries submitted through the read-only path must have no state-changing effects.
- source: §6.4 "Read-only client commands only query the replicated state machine; they do not change it."
- stated: stated
- violation: A query callback increments a persisted counter or updates application data without a log entry.
- at-risk: Replicated-service consistency fails because effects bypass replicated ordering and may occur on only one replica.
- detectable: partly — read-only transactions can block writes, but arbitrary external side effects can evade enforcement.
- silent: 2 — Hidden writes such as access counters can silently enter query handlers.
- basis: general systems experience

### E48
- contract: Clocks used for lease-based reads must obey the configured relative drift bound throughout each lease.
- source: §6.4.1 "The lease approach assumes a bound on clock drift across servers"
- stated: stated
- violation: A leader clock pauses while follower clocks advance enough to elect a replacement.
- at-risk: Read linearizability fails because an old leader can return arbitrarily stale information while believing its lease valid.
- detectable: partly — independent clocks can detect some drift, but a paused process cannot reliably certify the bound itself.
- silent: 2 — VM pauses and clock adjustments can violate assumed bounds without explicit clock errors.
- basis: general systems experience

### E49
- contract: Host scheduling and migration must preserve the effective clock-drift bound relied on by lease reads.
- source: §6.4.1 "due to scheduling and garbage collection pauses,
virtual machine migrations, or clock rate adjustments for time synchronization"
- stated: stated
- violation: A VM resumes a lease-holding process after a long suspension with an effectively unexpired lease.
- at-risk: Read linearizability is at risk from stale lease authority; this condition is specific to the optional clock-based read scheme.
- detectable: partly — resume notifications and independent elapsed-time checks help, but arbitrary suspension can evade local checks.
- silent: 2 — Long pauses and migrations occasionally lack an application-visible error.
- basis: general systems experience

### E50
- contract: Clients using the optional monotonic-read extension must retain and send the greatest observed state index across server changes.
- source: §6.4.1 "Clients would track the latest index corresponding to
results they had seen, and they would provide this information to servers on each request."
- stated: stated
- violation: A reconnecting client loses its watermark and accepts an older follower state.
- at-risk: The optional monotonic-progress guarantee fails when the client observes an earlier state after a later one.
- detectable: partly — the client can compare retained indices, but a lost watermark cannot be reconstructed from the next reply alone.
- silent: 2 — Reconnect and restart paths can silently discard client metadata.
- basis: general systems experience

## Recognised

I recognise no specific reported implementation bug from independent recall with enough confidence to name it. The source itself reports stale-read bugs in two third-party implementations (§6.4, reference [45]); those concern missing algorithm precautions, not a requirement that the network never partition.

## Count and unresolved decisions

50 contracts. No outcome-bearing model or implementation run was performed, and no commit was made, as instructed by the brief.

The boundary between a state-machine service and the Raft implementation is deployment-dependent; application persistence, serialization, compaction, and session interfaces are treated as depended-on services here. Internal rules about voting, commitment, log truncation, snapshot metadata, read-index checks, lease expiration before leadership transfer, and configuration sequencing are excluded. I found no independently established algorithm defect to report.

The source does not specify storage atomicity at a filesystem-operation level: E6, E25, and E31 state the required effect rather than prescribing a transaction or rename recipe. Lease clock and host-pause obligations overlap intentionally: E48 is the mathematical clock condition and E49 its host-service realization. Basic Raft requires neither bounded clock drift nor reliable, FIFO, duplicate-free networking for safety. Availability needs eventual useful communication and scheduling, but the source gives a practical timing condition rather than a general liveness proof.

No C/F identifiers or failure-model file exist in this checkout, so the derivation comment uses the actual brief and each entry uses a source section; fabricated clause identifiers would not provide traceability. The requested schema lists eight fields despite describing seven lines; all eight are included. Source quotations preserve extracted line breaks and hyphenation. Silent scores and several implicit obligations remain judgment calls, especially identity cloning, client recovery, and filesystem crash semantics.

## Checkout output: ls -R

```text
.:
AGENTS.md
BRIEF.md
enumeration.md
source

./source:
OngaroPhD.pdf
OngaroPhD.txt
```

## Checkout output: git status

```text
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	AGENTS.md
	BRIEF.md
	enumeration.md
	source/

nothing added to commit but untracked files present (use "git add" to track)
```
