# Environment contracts supporting Raft

Scope: the supplied dissertation only. Optional mechanisms are identified explicitly. Ratings estimate silent violations per deployment-year qualitatively, not measured frequencies; a reduced safety margin counts even before an outage. “State Machine Safety” below refers to Figure 3.2’s log-entry property; application-result consistency is distinguished where necessary.

<!-- derives: BRIEF.md task and format; source sections cited per entry. No C/F identifier registry is supplied in this checkout. -->

### E1
- contract: The host must make server failures fail-stop rather than permit arbitrary execution or memory corruption.
- source: §2.1 "Servers are assumed to fail by stopping; they may"
- stated: stated
- violation: A RAM fault changes a term or a process acknowledges entries it never stored.
- at-risk: Election Safety, Log Matching, Leader Completeness, and State Machine Safety can all fail because faulty participants can fabricate votes or log contents.
- detectable: partly — checksums and internal assertions catch some corruptions, but plausible incorrect execution can escape detection.
- silent: 2 — undetected hardware or runtime corruption is uncommon but possible.
- basis: general systems experience

### E2
- contract: The transport must preserve the contents of delivered Raft requests and responses.
- source: §2.1 "They ensure safety (never returning an incorrect result) under all non-Byzantine conditions,"
- stated: implicit
- violation: A delivered AppendEntries command differs from the bytes sent, without a transport error.
- at-risk: Log Matching and State Machine Safety can fail when replicas associate different commands with the same index and term.
- detectable: partly — end-to-end integrity checks detect many changes, but cannot prove absence of all corruption.
- silent: 1 — common transport checks usually turn corruption into visible loss.
- basis: general systems experience

### E3
- contract: The communication environment must preserve participant identity and must not fabricate messages from other servers.
- source: §3.3 "Each request type has a corresponding response type, which also serves as the request’s acknowl-"
- stated: implicit
- violation: Misrouting or impersonation makes one machine appear to supply votes from multiple members.
- at-risk: Election Safety and Leader Completeness can fail because an apparent majority need not be a real majority.
- detectable: partly — authenticated channels and identity checks can reject many false peers.
- silent: 1 — accidental silent impersonation is rare in an ordinary correctly isolated deployment.
- basis: general systems experience

### E4
- contract: The process manager must run at most one independently executing incarnation of each server identity at a time.
- source: §3.8 "If a server loses any of its persistent state, it cannot safely rejoin the cluster with its prior identity."
- stated: implicit
- violation: A VM clone and its original both run as the same voting member.
- at-risk: Election Safety can fail because the two incarnations can vote differently while being counted as the same quorum member.
- detectable: partly — incarnation fencing or duplicate-connection checks help, but isolated clones need not observe each other.
- silent: 2 — cloning and recovery automation occasionally create unnoticed identity overlap.
- basis: general systems experience

### E5
- contract: Provisioning must assign distinct identities to distinct voting servers.
- source: §B.2 "The set of server IDs"
- stated: implicit
- violation: Two newly provisioned machines receive the same member ID.
- at-risk: Election Safety and quorum-based safety are at risk if distinct physical processes act as one inconsistent voter; implementations that reject duplicates instead lose availability.
- detectable: partly — duplicate IDs can be detected during admission, but partitioned processes can conceal overlap.
- silent: 2 — copied configuration occasionally duplicates identities.
- basis: general systems experience

### E6
- contract: Stable storage must retain the recorded current term across crashes and restarts.
- source: §3.8 "particular, each server persists its current term and vote; this is necessary to prevent the server from"
- stated: stated
- violation: A completed term write vanishes after power loss.
- at-risk: Election Safety and Log Matching are at risk because a restarted member can accept obsolete leadership or repeat a prior-term vote.
- detectable: partly — independent durable records may reveal rollback; a self-consistent old image may not.
- silent: 2 — cache and recovery mistakes sometimes produce silent rollback.
- basis: general systems experience

### E7
- contract: Stable storage must retain the recorded vote across crashes and restarts.
- source: §3.8 "particular, each server persists its current term and vote; this is necessary to prevent the server from"
- stated: stated
- violation: A server forgets its acknowledged vote after reboot.
- at-risk: Election Safety fails if it votes for another candidate in the same term; conflicting leaders then threaten all replicated-log guarantees.
- detectable: partly — redundant records can expose loss, but the lost vote alone leaves no local evidence.
- silent: 2 — silent lost persistence is occasional under faulty storage configurations.
- basis: general systems experience

### E8
- contract: Stable storage must retain acknowledged log entries across crashes and restarts.
- source: §3.8 "mitment; this prevents committed entries from being lost or “uncommitted” when servers restart."
- stated: stated
- violation: An fsync reports success but a power cycle removes the log tail.
- at-risk: Leader Completeness and State Machine Safety can fail when a committed entry loses its quorum and another command replaces it.
- detectable: partly — checksums can expose damage, but a cleanly shortened log may appear valid.
- silent: 2 — misconfigured caches and storage failures sometimes lose acknowledged data.
- basis: general systems experience

### E9
- contract: The storage stack must preserve the integrity of persisted log entries and metadata while they are retained.
- source: §3.8 "Raft servers must persist enough information to stable storage to survive server restarts safely."
- stated: implicit
- violation: Bit rot changes a command, index, term, or vote in a readable file.
- at-risk: Log Matching and State Machine Safety can fail because Raft does not repair arbitrary corrupted durable state by consensus alone.
- detectable: partly — checksums and replica comparison detect many errors, but matching corruption or unchecked fields can escape.
- silent: 2 — silent corruption is uncommon on an individual machine but credible over fleet operation.
- basis: general systems experience

### E10
- contract: The filesystem and device must honor completed flushes and required write ordering before exposing durable snapshot or log state.
- source: §5.1.3 "flushed to disk; this ensures that no server loads a partially written snapshot on startup."
- stated: implicit
- violation: A rename survives a crash while snapshot data or prerequisite log metadata does not.
- at-risk: Leader Completeness and correct state-machine recovery are at risk because discarded log entries may have no complete durable replacement.
- detectable: partly — recovery checks can reject incomplete records, but valid-looking stale data can pass.
- silent: 2 — filesystem and controller durability misunderstandings occasionally remain silent until a crash.
- basis: general systems experience

### E11
- contract: The filesystem must provide the atomic snapshot publication semantics relied upon by the temporary-file rename scheme.
- source: §5.1.3 "snapshot to a temporary file first, then renames the file when writing is complete and has been"
- stated: implicit
- violation: After interrupted publication, the final snapshot name references a partial mixture rather than an old or complete new snapshot.
- at-risk: Correct recovery and client consistency fail if startup accepts a partially published state image.
- detectable: partly — completeness markers and checksums detect many partial images.
- silent: 1 — conventional local filesystems usually provide atomic rename, though unusual backends may not.
- basis: general systems experience

### E12
- contract: Recovery operators must prevent a server with lost persistent state from rejoining under its old identity.
- source: §3.8 "If a server loses any of its persistent state, it cannot safely rejoin the cluster with its prior identity."
- stated: stated
- violation: An operator restores an old backup or replaces a failed disk and starts the old member ID.
- at-risk: Election Safety and Leader Completeness can fail through forgotten votes or committed entries.
- detectable: partly — external incarnation records can detect replacement, but an internally consistent rollback may be invisible.
- silent: 3 — restoration and replacement procedures are common sources of unnoticed state rollback.
- basis: general systems experience

### E13
- contract: Operators must preserve a durable majority if they require recovery without admitting data loss.
- source: §3.8 "If a majority of the cluster loses its persistent state, however,"
- stated: stated
- violation: A common storage failure or operator wipe destroys the only surviving majority copies.
- at-risk: Committed-data durability and recovery availability fail; the source explicitly requires admitting possible data loss to proceed.
- detectable: partly — missing disks are visible, but coherent restoration of stale majority images can hide the loss.
- silent: 2 — correlated destructive recovery is occasional rather than routine.
- basis: general systems experience

### E14
- contract: The deployment must maintain an operational majority able to communicate mutually and with clients for service availability.
- source: §2.1 "They are fully functional (available) as long as any majority of the servers are operational"
- stated: stated
- violation: A partition leaves clients able to contact only a minority, or too many hosts are down.
- at-risk: Availability fails because no reachable voting majority can elect a useful leader and commit operations; safety does not require this contract.
- detectable: yes — failed RPCs, stalled commits, and quorum monitoring expose the symptom.
- silent: 1 — sustained quorum loss normally produces visible timeouts.
- basis: general systems experience

### E15
- contract: The host and network must eventually provide timely execution and message delivery for a sufficiently long interval to make progress.
- source: §9 "must be timely (or stopped)."
- stated: stated
- violation: Repeated scheduler starvation or message delays prevent every election from completing.
- at-risk: Leader-election and request-completion availability fail; asynchronous safety remains intact.
- detectable: partly — observed delays are measurable, but a process cannot infer a permanent progress guarantee.
- silent: 2 — transient stalls can be hidden by retries while degrading service.
- basis: general systems experience

### E16
- contract: The network, storage, and scheduler must keep broadcast latency well below the configured election timeout for stable leadership.
- source: §3.9 "broadcast time should be an order of magnitude less than the election timeout so that leaders can"
- stated: stated
- violation: Disk flush or scheduling delays routinely exceed the heartbeat budget.
- at-risk: Stable-leader availability and expected recovery latency fail because healthy members repeatedly trigger elections.
- detectable: yes — RPC timing, election counts, and flush latency reveal violations.
- silent: 2 — short tail-latency excursions are sometimes masked by retries.
- basis: general systems experience

### E17
- contract: The host fleet must sustain failure intervals much longer than election timeouts for steady progress.
- source: §3.9 "election timeout should be a few orders of magnitude less than MTBF so that the system makes"
- stated: stated
- violation: A restart loop kills leaders before elections and commits finish.
- at-risk: Availability and the claim of a small unavailable fraction fail; log safety remains conditional on durable recovery.
- detectable: yes — restart telemetry and failed election histories expose this condition.
- silent: 1 — frequent crash loops ordinarily produce visible errors.
- basis: general systems experience

### E18
- contract: The random-number service must supply sufficiently independent timeout samples across servers and successive elections.
- source: §9 "somehow synchronized), clocks must proceed at about the same rates, and servers and networks"
- stated: implicit
- violation: Cloned PRNG seeds cause every candidate to select identical timeout sequences.
- at-risk: Rapid probabilistic leader election fails through repeated split votes; safety is unaffected.
- detectable: partly — correlated timeout histories reveal some bad generators but cannot establish independence.
- silent: 2 — image cloning or weak seeding occasionally synchronizes processes.
- basis: general systems experience

### E19
- contract: For the stated election-performance expectations, timer clocks must advance at approximately comparable rates across servers.
- source: §9 "somehow synchronized), clocks must proceed at about the same rates, and servers and networks"
- stated: stated
- violation: One VM timer advances much faster and repeatedly starts disruptive elections.
- at-risk: Election performance and availability may fail; the basic algorithm retains safety despite arbitrary clock rates.
- detectable: partly — external clock comparisons and election traces reveal gross skew.
- silent: 2 — VM pauses and clock adjustments sometimes distort local timing without an explicit clock error.
- basis: general systems experience

### E20
- contract: Membership automation must retain enough replicas to meet the operator’s intended durability and failure tolerance.
- source: §4.4 "with too few replicas to satisfy the intended durability and fault-tolerance requirements."
- stated: stated
- violation: A script removes every failed member until only one replica remains.
- at-risk: The advertised failure-tolerance margin fails even though Raft correctly agrees on the smaller configuration.
- detectable: partly — configuration size is visible, but intended fault tolerance must be supplied externally.
- silent: 3 — a valid but undersized configuration may run quietly until another failure.
- basis: general systems experience

### E21
- contract: Replacement procedures must retain the required quorum margin at every intermediate configuration.
- source: §4.4 "able to add servers before removing servers."
- stated: stated
- violation: A three-member deployment removes one member before adding its replacement and temporarily needs both survivors.
- at-risk: Continuous one-failure availability is lost during the two-member interval; this is an operational margin, not a safety precondition.
- detectable: yes — membership history and configured quorum sizes expose the interval.
- silent: 3 — remove-first maintenance often succeeds quietly while reducing resilience.
- basis: general systems experience

### E22
- contract: During a membership transition, the deployment must keep the required old and new majorities available.
- source: §4.2.4 "majority of the old configuration is available (at least until Cnew is committed) and that a majority"
- stated: stated
- violation: Operators shut down an old majority before the new configuration commits.
- at-risk: Availability through membership changes fails because the transition cannot obtain its required votes or replication acknowledgments.
- detectable: yes — configuration-aware quorum tracking and transition timeouts expose the deficit.
- silent: 1 — stalled reconfiguration normally causes observable delays.
- basis: general systems experience

### E23
- contract: New-server resources and links must support catching up with the leader’s evolving log for addition to finish promptly.
- source: §4.2.4 "Since new servers are caught up before being added to the cluster, a leader can advance"
- stated: implicit
- violation: An incoming server receives log data more slowly than the leader generates it.
- at-risk: Prompt membership-change completion fails; keeping the server non-voting protects the existing cluster’s availability.
- detectable: yes — replication lag and catch-up progress expose the condition.
- silent: 2 — gradual lag can be overlooked before an admission timeout.
- basis: general systems experience

### E24
- contract: Provisioning must bootstrap one intended cluster consistently and admit subsequent servers without independently initialized conflicting history.
- source: §4.4 "Other servers from then on should be initialized with empty logs; they are added to the cluster and"
- stated: stated
- violation: Two bootstrap scripts create separate singleton clusters and expose both as one service.
- at-risk: Single-service consistency and durability expectations fail because independent committed histories have no shared quorum lineage.
- detectable: partly — cluster identifiers and admission checks can expose independent bootstrap, but clients may see only one side.
- silent: 2 — duplicate initialization is an occasional deployment automation error.
- basis: general systems experience

### E25
- contract: The state-machine service must compute identical state and outputs from identical initial state and ordered command inputs.
- source: §11.6 "every server must arrive at the same result after applying the same series of client requests."
- stated: stated
- violation: Commands consult local time, randomness, or platform-dependent iteration order independently on each replica.
- at-risk: Correct replicated-service results and linearizability fail despite matching Raft logs; this need not violate the log-entry formulation of State Machine Safety.
- detectable: partly — state hashes and response comparison detect divergence after execution.
- silent: 3 — nondeterministic application behavior is an occasional integration error.
- basis: general systems experience

### E26
- contract: The state-machine recovery service must reconstruct the state represented by the discarded prefix before processing retained log entries.
- source: §5 "discarded log entries from disk before it can apply any entries from the Raft log."
- stated: stated
- violation: A restarting application starts with empty state and applies only the uncompacted log suffix.
- at-risk: Correct client results and linearizability fail because the recovered application omits committed effects.
- detectable: partly — snapshot identity and state invariants detect many omissions, but a plausible wrong state can pass.
- silent: 2 — recovery paths are exercised less often than ordinary operation.
- basis: general systems experience

### E27
- contract: A persistent state-machine backend must recover its last-applied index consistently with the durable application effects.
- source: §3.8 "them, its last applied index must also be persistent."
- stated: implicit
- violation: A balance update persists but its applied index rolls back, or the index persists without the update.
- at-risk: Exactly-once effects and linearizability fail through replayed or skipped commands; matching logs alone cannot prevent this.
- detectable: partly — transactional recovery metadata can reveal mismatches, but separate valid records may conceal them.
- silent: 3 — independent persistence of application data and progress creates subtle crash windows.
- basis: general systems experience

### E28
- contract: A compaction backend must durably preserve all effects it reports as safely replacing a Raft log prefix.
- source: §5 "the state machine reflects those entries to disk in a way that can recover the current system state."
- stated: stated
- violation: A state-machine library reports completion while its replacement state remains only in a write cache.
- at-risk: Committed-data durability and correct recovery fail once Raft discards the only reliable command copies.
- detectable: partly — backend durability checks detect errors but cannot validate a lying device after every acknowledgment.
- silent: 2 — false durability assumptions sometimes survive until a restart.
- basis: general systems experience

### E29
- contract: The state-machine snapshot service must serialize and restore an exact, complete representation of the represented application state.
- source: §5.1.3 "state and writing that data out to a file, while loading is the reverse process."
- stated: implicit
- violation: Serialization omits a field or restoration changes numeric values or object relationships.
- at-risk: Correct client results and linearizability fail after restart or snapshot installation despite intact logs.
- detectable: partly — round-trip checks and state hashes reveal many omissions, but shared serialization mistakes can escape.
- silent: 3 — schema evolution and rarely used fields occasionally produce quiet recovery errors.
- basis: general systems experience

### E30
- contract: Snapshots must include the state-machine session and duplicate-response information needed to preserve client semantics.
- source: §5.1 "serialize the information they keep for providing linearizability to clients (see Chapter 6)."
- stated: stated
- violation: A snapshot preserves database values but omits cached results and session serial numbers.
- at-risk: Exactly-once semantics fail when a retry after recovery executes an already completed operation again.
- detectable: partly — schema validation can check inclusion, but a forgotten field can look like an empty valid table.
- silent: 3 — application-only snapshots can silently omit protocol state.
- basis: general systems experience

### E31
- contract: The snapshot provider must supply a consistent state image corresponding to one application prefix.
- source: §5 "state, which the leader then sends to the follower."
- stated: stated
- violation: A snapshot combines an old account debit with a new account credit from another instant.
- at-risk: Correct state-machine recovery and linearizability fail because the installed image never represented a valid committed prefix.
- detectable: partly — version markers and invariants catch some mixed images but cannot prove arbitrary state consistency.
- silent: 2 — concurrent copying without proper isolation occasionally creates plausible mixed state.
- basis: general systems experience

### E32
- contract: When concurrent snapshots rely on operating-system copy-on-write, that service must preserve the captured point-in-time view.
- source: §5.1.1 "to make a copy of the server’s entire address space."
- stated: implicit
- violation: The snapshot child sees later parent writes through a broken or unsuitable shared mapping.
- at-risk: Correct snapshot recovery fails because the resulting state can mix command prefixes.
- detectable: partly — version validation may expose mixed state, but valid-looking images can conceal it.
- silent: 1 — standard private-memory fork semantics are usually reliable.
- basis: general systems experience

### E33
- contract: The host must supply enough memory for the chosen concurrent snapshot method or permit controlled backpressure before exhaustion.
- source: §5.1.1 "Servers require additional memory for snapshotting concurrently, which should be planned for"
- stated: stated
- violation: Copy-on-write amplification triggers OOM kills on several snapshotting replicas.
- at-risk: Availability and compaction progress fail; crash-safe storage should preserve core safety.
- detectable: yes — allocation failures, memory pressure, and OOM events expose exhaustion.
- silent: 1 — exhaustion usually leaves visible failures or pressure telemetry.
- basis: general systems experience

### E34
- contract: The deployment must provide enough disk capacity and I/O service for its log, retained snapshots, and ongoing compaction workload.
- source: §5.1.2 "and requires about 6 times the disk capacity as that needed to store a single copy of the state (the"
- stated: implicit
- violation: The log and temporary snapshot fill the volume before compaction can finish.
- at-risk: Sustained request availability fails when entries or snapshots cannot be persisted; this does not inherently break safety.
- detectable: yes — free-space and write-error monitoring expose exhaustion.
- silent: 1 — full disks and failed writes usually produce explicit errors.
- basis: general systems experience

### E35
- contract: A disk-state-machine snapshot backend must retain an immutable consistent disk image throughout transfer.
- source: §5.2 "snapshot for a long enough period to transmit it."
- stated: stated
- violation: A volume snapshot expires or its backing blocks are overwritten while a slow follower copies it.
- at-risk: Follower recovery and correct client results are at risk if a changing image is installed as one committed state.
- detectable: partly — snapshot handles and checksums expose invalidation, but an unversioned image can silently change.
- silent: 2 — retention and copy-on-write capacity problems occasionally invalidate long transfers.
- basis: general systems experience

### E36
- contract: An LSM-based compaction backend must preserve the immutability and completeness of the runs used for state transfer.
- source: §5.3.3 "being modified during the transfer."
- stated: implicit
- violation: Background cleanup deletes a required run or modifies its contents during transfer.
- at-risk: Snapshot-based recovery and availability fail, and accepted incomplete state can violate client consistency.
- detectable: partly — pinned run manifests and checksums expose many missing or changed files.
- silent: 2 — background retention mistakes can occur without immediate application errors.
- basis: general systems experience

### E37
- contract: Client discovery infrastructure must be reachable at its configured well-known location.
- source: §6.1 "accessible at a well-known location."
- stated: stated
- violation: DNS is unavailable to fresh clients even though the Raft majority is healthy.
- at-risk: Client availability fails because clients cannot find a usable service endpoint.
- detectable: yes — discovery failures and lookup timeouts reveal the symptom.
- silent: 1 — discovery outages normally produce visible connection errors.
- basis: general systems experience

### E38
- contract: The external directory and its maintenance scripts must keep discovery inclusive as membership changes.
- source: §6.1 "consistent, but it should be inclusive: clients should always be able to find all of the cluster"
- stated: stated
- violation: DNS retains only removed members or never advertises new members before old ones disappear.
- at-risk: Client availability fails if discovery omits reachable active servers; directory linearizability is unnecessary.
- detectable: partly — comparison with membership detects omissions, but individual clients cannot know missing endpoints.
- silent: 3 — stale DNS and delayed administrative updates commonly remain quiet while some endpoints still work.
- basis: general systems experience

### E39
- contract: When clients use broadcast or multicast discovery, the network must support that discovery mechanism across the intended scope.
- source: §6.1 "only work in particular environments that support these features."
- stated: stated
- violation: A network segment filters discovery multicast while permitting direct Raft traffic.
- at-risk: New-client availability fails because otherwise reachable servers cannot be discovered.
- detectable: yes — failed discovery can be observed and compared with successful direct connections.
- silent: 1 — total discovery failure is usually visible.
- basis: general systems experience

### E40
- contract: The client library must abandon failed server connections and retry reachable alternative members.
- source: §6.2 "simply retry with a random server. Insisting on being able to contact the last known leader"
- stated: stated
- violation: A client pins itself to a failed former leader forever.
- at-risk: Client request availability fails despite a healthy majority and a usable new leader.
- detectable: partly — connection and retry telemetry exposes pinning, but the servers may never see the stranded client.
- silent: 2 — poorly configured client retry policies sometimes cause avoidable delays.
- basis: general systems experience

### E41
- contract: Clients must assign distinct command serial numbers within each client identity and preserve the same identity and serial on retries.
- source: §6.3 "serial numbers to every command. Each server’s state machine maintains a session for each client."
- stated: stated
- violation: A restarted client resets its serial counter under the old identity, or retries a debit with a new serial.
- at-risk: Linearizability and exactly-once intent fail through suppressed new commands or repeated effects.
- detectable: partly — conflicting payload checks reveal some reuse, but a new serial cannot reveal that it represents a retry.
- silent: 3 — counter persistence and retry bookkeeping mistakes can remain silent.
- basis: general systems experience

### E42
- contract: Client identity allocation and client use must keep simultaneously distinct sessions uniquely identified.
- source: §6.3 "To implement this, each client is given a unique identifier, and clients assign unique"
- stated: stated
- violation: Two applications reuse a copied registration ID and overlapping serial numbers.
- at-risk: Correct responses and exactly-once semantics fail when one client’s operations are mistaken for another’s duplicates.
- detectable: partly — identity ownership checks detect some sharing, but identical-looking sessions can escape.
- silent: 2 — cloning client state occasionally creates unnoticed collisions.
- basis: general systems experience

### E43
- contract: A state-machine session backend must retain deduplication results until the protocol permits their removal and expire sessions deterministically.
- source: §6.3 "session expiry must be deterministic, just as normal state"
- stated: stated
- violation: Local wall-clock expiry deletes a session on one replica while another keeps it, or cached replies disappear early.
- at-risk: Linearizability and deterministic replicated results fail when one replica reexecutes a duplicate that another filters.
- detectable: partly — state hashes and expiry traces reveal disagreement, but coordinated premature deletion can be silent.
- silent: 3 — local expiry caches are a common integration choice with subtle consequences.
- basis: general systems experience

### E44
- contract: Concurrent clients must report an accurate lowest unanswered sequence number before servers discard older response records.
- source: §6.3 "With each request, the client includes the lowest sequence"
- stated: stated
- violation: A client advances its acknowledgment watermark past a request whose reply was lost.
- at-risk: Exactly-once retry behavior and correct response recovery are at risk because the server may discard a still-needed reply.
- detectable: partly — servers can reject impossible counters, but cannot know whether a client actually received a response.
- silent: 2 — out-of-order completion bookkeeping occasionally makes erroneous progress claims.
- basis: general systems experience

### E45
- contract: Clients that require uninterrupted sessions must send keep-alives within the service’s session-retention policy during inactivity.
- source: §6.3 "Live clients issue keep-alive requests during periods of inactivity, which are also augmented with"
- stated: stated
- violation: A suspended client misses keep-alives and resumes after its session expires.
- at-risk: Session continuity and client availability fail; correctly rejected expired requests preserve safety rather than silently execute duplicates.
- detectable: yes — missing sessions and explicit expiration errors reveal the violation on resumption.
- silent: 1 — compliant services report expiration as an error.
- basis: general systems experience

### E46
- contract: Clients must treat session-expiration errors as loss of retry certainty rather than automatically resubmit ambiguous commands in a new session.
- source: §6.3 "new session for a client any time there is no record of it, but this would risk duplicate execution of"
- stated: implicit
- violation: After expiration, middleware registers anew and repeats a payment whose first execution may have committed.
- at-risk: Exactly-once application intent fails across sessions because old deduplication records are unavailable.
- detectable: partly — expiration is visible, but a new request does not identify its unknown old effect.
- silent: 3 — automated retry layers can quietly turn explicit expiration into duplicate effects.
- basis: general systems experience

### E47
- contract: Operations classified as read-only must leave all replicated application and session state unchanged.
- source: §6.4 "Read-only client commands only query the replicated state machine; they do not change it."
- stated: stated
- violation: A query increments a replicated counter or lazily mutates state while bypassing the log.
- at-risk: Replicated-state consistency and linearizability fail because mutations escape ordered replication.
- detectable: partly — write guards or state hashes reveal some mutations, but hidden side effects may escape.
- silent: 2 — nominal reads occasionally include caching or bookkeeping mutations.
- basis: general systems experience

### E48
- contract: The state-machine query interface must observe a coherent state at least as recent as the supplied read barrier.
- source: §6.4 "The leader waits for its state machine to advance at least as far as the readIndex; this is current"
- stated: implicit
- violation: An asynchronous database reports applied progress before its query view exposes those updates, or a query sees half an update.
- at-risk: Linearizable reads fail despite a correct leadership check and read index.
- detectable: partly — versioned query results can expose lag, but incorrect backend visibility metadata can conceal it.
- silent: 3 — asynchronous application and database visibility boundaries can quietly diverge.
- basis: general systems experience

### E49
- contract: For clock-based read leases, effective server clocks must remain within the assumed relative drift bound, including host pauses and migration effects.
- source: §6.4.1 "The lease approach assumes a bound on clock drift across servers (over a given time period, no"
- stated: stated
- violation: A paused leader resumes with an apparently live lease after followers have elected a new leader.
- at-risk: Linearizable reads fail and results may be arbitrarily stale; basic Raft log safety does not depend on this bound.
- detectable: partly — independent clock and pause monitoring can invalidate leases, but purely local observations cannot guarantee the bound.
- silent: 3 — scheduling pauses, migration, and clock adjustments occur without explicit lease errors.
- basis: general systems experience

### E50
- contract: For the optional monotonic-read extension, clients must carry their highest observed state index across requests and server changes.
- source: §6.4.1 "results they had seen, and they would provide this information to servers on each request."
- stated: stated
- violation: A client reconnects or switches connection pools and drops its observed-index watermark.
- at-risk: The stated monotonic-progress guarantee can fail because a new server may answer from an older state; the source calls the extension sequential consistency.
- detectable: partly — clients can audit index regressions if they retain history, but a server cannot reconstruct an omitted watermark.
- silent: 3 — reconnect and client-state handoff paths often discard incidental metadata.
- basis: general systems experience

## Recognised
I recall the general class of stale-read bugs in Raft implementations, also explicitly mentioned in §6.4; I do not recall a sufficiently specific independent report to name an implementation honestly. The clock-lease dependency is E49; missing heartbeat/read-barrier checks themselves are algorithm or implementation defects, not environment contracts.

## Count and unresolved boundaries
50 contracts.
No algorithm defect was established by this enumeration. Requirements to persist before acknowledgment, check read leadership, wait for application, serialize configuration changes, and expire a lease before leadership transfer belong to Raft or its extensions; the list instead identifies the service semantics on which those rules rely.
The source does not specify authentication, filesystem crash semantics, or incarnation fencing in implementation detail; those entries are implicit consequences, not claims that the dissertation prescribes a particular mechanism. Server identity uniqueness is grounded in the formal server-ID set. Storage durability, flush ordering, atomic publication, and recovery fencing overlap but describe independently violable obligations.
Session deduplication, snapshotting, and query interfaces are treated as environmental services where Raft delegates to the state machine; implementing these inside one binary does not remove their obligations. No independent contract/failure-model ID registry exists here, so no C/F derivation IDs were invented.
The byte-exact quotations sometimes retain source line wrapping or hyphenation. Ratings are judgment calls based on general systems experience, not empirical estimates supplied by the dissertation. No web sources, experiment, model, implementation, or outcome-bearing test was used.

## Checkout inventory and status
Captured after writing this report and removing temporary working files. Nothing was committed.


`ls -R`:

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

`git status`:

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
