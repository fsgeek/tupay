# Brief: merge four lists of environment contracts (D1 phase 1)

Below are four lists, written independently from one source (Ongaro, *Consensus: Bridging Theory and Practice*, 2014), of the **environment contracts** Raft relies on: obligations on things outside the algorithm (storage, network, clocks, processes, identity, operators, the state machine, the host). Each entry has an id `<list>:E<n>`. Different lists often state the same obligation in different words, or split one obligation into several finer ones.

Your task: group entries that state **the same obligation on the same depended-on service**. Two entries belong in one group only if a deployment that violates one necessarily violates the other. An entry that is broader than another may appear in more than one group (once with each finer entry it covers). An entry that matches nothing need not be listed.

Use only the text below. Do not use any tool. Reply with JSON only, in exactly this shape, and nothing else:

{"groups": [["codex-1:E3", "grok-2:E7"], ["codex-2:E1", "grok-1:E4", "grok-2:E2"]]}

Every id you write must appear in the lists below. Groups have at least two ids.

---
### codex-1:E1
- contract: The host must make server failures fail-stop rather than permit arbitrary execution or memory corruption.
- source: §2.1 "Servers are assumed to fail by stopping; they may"
- stated: stated
- violation: A RAM fault changes a term or a process acknowledges entries it never stored.
- at-risk: Election Safety, Log Matching, Leader Completeness, and State Machine Safety can all fail because faulty participants can fabricate votes or log contents.
- detectable: partly — checksums and internal assertions catch some corruptions, but plausible incorrect execution can escape detection.

### codex-1:E2
- contract: The transport must preserve the contents of delivered Raft requests and responses.
- source: §2.1 "They ensure safety (never returning an incorrect result) under all non-Byzantine conditions,"
- stated: implicit
- violation: A delivered AppendEntries command differs from the bytes sent, without a transport error.
- at-risk: Log Matching and State Machine Safety can fail when replicas associate different commands with the same index and term.
- detectable: partly — end-to-end integrity checks detect many changes, but cannot prove absence of all corruption.

### codex-1:E3
- contract: The communication environment must preserve participant identity and must not fabricate messages from other servers.
- source: §3.3 "Each request type has a corresponding response type, which also serves as the request’s acknowl-"
- stated: implicit
- violation: Misrouting or impersonation makes one machine appear to supply votes from multiple members.
- at-risk: Election Safety and Leader Completeness can fail because an apparent majority need not be a real majority.
- detectable: partly — authenticated channels and identity checks can reject many false peers.

### codex-1:E4
- contract: The process manager must run at most one independently executing incarnation of each server identity at a time.
- source: §3.8 "If a server loses any of its persistent state, it cannot safely rejoin the cluster with its prior identity."
- stated: implicit
- violation: A VM clone and its original both run as the same voting member.
- at-risk: Election Safety can fail because the two incarnations can vote differently while being counted as the same quorum member.
- detectable: partly — incarnation fencing or duplicate-connection checks help, but isolated clones need not observe each other.

### codex-1:E5
- contract: Provisioning must assign distinct identities to distinct voting servers.
- source: §B.2 "The set of server IDs"
- stated: implicit
- violation: Two newly provisioned machines receive the same member ID.
- at-risk: Election Safety and quorum-based safety are at risk if distinct physical processes act as one inconsistent voter; implementations that reject duplicates instead lose availability.
- detectable: partly — duplicate IDs can be detected during admission, but partitioned processes can conceal overlap.

### codex-1:E6
- contract: Stable storage must retain the recorded current term across crashes and restarts.
- source: §3.8 "particular, each server persists its current term and vote; this is necessary to prevent the server from"
- stated: stated
- violation: A completed term write vanishes after power loss.
- at-risk: Election Safety and Log Matching are at risk because a restarted member can accept obsolete leadership or repeat a prior-term vote.
- detectable: partly — independent durable records may reveal rollback; a self-consistent old image may not.

### codex-1:E7
- contract: Stable storage must retain the recorded vote across crashes and restarts.
- source: §3.8 "particular, each server persists its current term and vote; this is necessary to prevent the server from"
- stated: stated
- violation: A server forgets its acknowledged vote after reboot.
- at-risk: Election Safety fails if it votes for another candidate in the same term; conflicting leaders then threaten all replicated-log guarantees.
- detectable: partly — redundant records can expose loss, but the lost vote alone leaves no local evidence.

### codex-1:E8
- contract: Stable storage must retain acknowledged log entries across crashes and restarts.
- source: §3.8 "mitment; this prevents committed entries from being lost or “uncommitted” when servers restart."
- stated: stated
- violation: An fsync reports success but a power cycle removes the log tail.
- at-risk: Leader Completeness and State Machine Safety can fail when a committed entry loses its quorum and another command replaces it.
- detectable: partly — checksums can expose damage, but a cleanly shortened log may appear valid.

### codex-1:E9
- contract: The storage stack must preserve the integrity of persisted log entries and metadata while they are retained.
- source: §3.8 "Raft servers must persist enough information to stable storage to survive server restarts safely."
- stated: implicit
- violation: Bit rot changes a command, index, term, or vote in a readable file.
- at-risk: Log Matching and State Machine Safety can fail because Raft does not repair arbitrary corrupted durable state by consensus alone.
- detectable: partly — checksums and replica comparison detect many errors, but matching corruption or unchecked fields can escape.

### codex-1:E10
- contract: The filesystem and device must honor completed flushes and required write ordering before exposing durable snapshot or log state.
- source: §5.1.3 "flushed to disk; this ensures that no server loads a partially written snapshot on startup."
- stated: implicit
- violation: A rename survives a crash while snapshot data or prerequisite log metadata does not.
- at-risk: Leader Completeness and correct state-machine recovery are at risk because discarded log entries may have no complete durable replacement.
- detectable: partly — recovery checks can reject incomplete records, but valid-looking stale data can pass.

### codex-1:E11
- contract: The filesystem must provide the atomic snapshot publication semantics relied upon by the temporary-file rename scheme.
- source: §5.1.3 "snapshot to a temporary file first, then renames the file when writing is complete and has been"
- stated: implicit
- violation: After interrupted publication, the final snapshot name references a partial mixture rather than an old or complete new snapshot.
- at-risk: Correct recovery and client consistency fail if startup accepts a partially published state image.
- detectable: partly — completeness markers and checksums detect many partial images.

### codex-1:E12
- contract: Recovery operators must prevent a server with lost persistent state from rejoining under its old identity.
- source: §3.8 "If a server loses any of its persistent state, it cannot safely rejoin the cluster with its prior identity."
- stated: stated
- violation: An operator restores an old backup or replaces a failed disk and starts the old member ID.
- at-risk: Election Safety and Leader Completeness can fail through forgotten votes or committed entries.
- detectable: partly — external incarnation records can detect replacement, but an internally consistent rollback may be invisible.

### codex-1:E13
- contract: Operators must preserve a durable majority if they require recovery without admitting data loss.
- source: §3.8 "If a majority of the cluster loses its persistent state, however,"
- stated: stated
- violation: A common storage failure or operator wipe destroys the only surviving majority copies.
- at-risk: Committed-data durability and recovery availability fail; the source explicitly requires admitting possible data loss to proceed.
- detectable: partly — missing disks are visible, but coherent restoration of stale majority images can hide the loss.

### codex-1:E14
- contract: The deployment must maintain an operational majority able to communicate mutually and with clients for service availability.
- source: §2.1 "They are fully functional (available) as long as any majority of the servers are operational"
- stated: stated
- violation: A partition leaves clients able to contact only a minority, or too many hosts are down.
- at-risk: Availability fails because no reachable voting majority can elect a useful leader and commit operations; safety does not require this contract.
- detectable: yes — failed RPCs, stalled commits, and quorum monitoring expose the symptom.

### codex-1:E15
- contract: The host and network must eventually provide timely execution and message delivery for a sufficiently long interval to make progress.
- source: §9 "must be timely (or stopped)."
- stated: stated
- violation: Repeated scheduler starvation or message delays prevent every election from completing.
- at-risk: Leader-election and request-completion availability fail; asynchronous safety remains intact.
- detectable: partly — observed delays are measurable, but a process cannot infer a permanent progress guarantee.

### codex-1:E16
- contract: The network, storage, and scheduler must keep broadcast latency well below the configured election timeout for stable leadership.
- source: §3.9 "broadcast time should be an order of magnitude less than the election timeout so that leaders can"
- stated: stated
- violation: Disk flush or scheduling delays routinely exceed the heartbeat budget.
- at-risk: Stable-leader availability and expected recovery latency fail because healthy members repeatedly trigger elections.
- detectable: yes — RPC timing, election counts, and flush latency reveal violations.

### codex-1:E17
- contract: The host fleet must sustain failure intervals much longer than election timeouts for steady progress.
- source: §3.9 "election timeout should be a few orders of magnitude less than MTBF so that the system makes"
- stated: stated
- violation: A restart loop kills leaders before elections and commits finish.
- at-risk: Availability and the claim of a small unavailable fraction fail; log safety remains conditional on durable recovery.
- detectable: yes — restart telemetry and failed election histories expose this condition.

### codex-1:E18
- contract: The random-number service must supply sufficiently independent timeout samples across servers and successive elections.
- source: §9 "somehow synchronized), clocks must proceed at about the same rates, and servers and networks"
- stated: implicit
- violation: Cloned PRNG seeds cause every candidate to select identical timeout sequences.
- at-risk: Rapid probabilistic leader election fails through repeated split votes; safety is unaffected.
- detectable: partly — correlated timeout histories reveal some bad generators but cannot establish independence.

### codex-1:E19
- contract: For the stated election-performance expectations, timer clocks must advance at approximately comparable rates across servers.
- source: §9 "somehow synchronized), clocks must proceed at about the same rates, and servers and networks"
- stated: stated
- violation: One VM timer advances much faster and repeatedly starts disruptive elections.
- at-risk: Election performance and availability may fail; the basic algorithm retains safety despite arbitrary clock rates.
- detectable: partly — external clock comparisons and election traces reveal gross skew.

### codex-1:E20
- contract: Membership automation must retain enough replicas to meet the operator’s intended durability and failure tolerance.
- source: §4.4 "with too few replicas to satisfy the intended durability and fault-tolerance requirements."
- stated: stated
- violation: A script removes every failed member until only one replica remains.
- at-risk: The advertised failure-tolerance margin fails even though Raft correctly agrees on the smaller configuration.
- detectable: partly — configuration size is visible, but intended fault tolerance must be supplied externally.

### codex-1:E21
- contract: Replacement procedures must retain the required quorum margin at every intermediate configuration.
- source: §4.4 "able to add servers before removing servers."
- stated: stated
- violation: A three-member deployment removes one member before adding its replacement and temporarily needs both survivors.
- at-risk: Continuous one-failure availability is lost during the two-member interval; this is an operational margin, not a safety precondition.
- detectable: yes — membership history and configured quorum sizes expose the interval.

### codex-1:E22
- contract: During a membership transition, the deployment must keep the required old and new majorities available.
- source: §4.2.4 "majority of the old configuration is available (at least until Cnew is committed) and that a majority"
- stated: stated
- violation: Operators shut down an old majority before the new configuration commits.
- at-risk: Availability through membership changes fails because the transition cannot obtain its required votes or replication acknowledgments.
- detectable: yes — configuration-aware quorum tracking and transition timeouts expose the deficit.

### codex-1:E23
- contract: New-server resources and links must support catching up with the leader’s evolving log for addition to finish promptly.
- source: §4.2.4 "Since new servers are caught up before being added to the cluster, a leader can advance"
- stated: implicit
- violation: An incoming server receives log data more slowly than the leader generates it.
- at-risk: Prompt membership-change completion fails; keeping the server non-voting protects the existing cluster’s availability.
- detectable: yes — replication lag and catch-up progress expose the condition.

### codex-1:E24
- contract: Provisioning must bootstrap one intended cluster consistently and admit subsequent servers without independently initialized conflicting history.
- source: §4.4 "Other servers from then on should be initialized with empty logs; they are added to the cluster and"
- stated: stated
- violation: Two bootstrap scripts create separate singleton clusters and expose both as one service.
- at-risk: Single-service consistency and durability expectations fail because independent committed histories have no shared quorum lineage.
- detectable: partly — cluster identifiers and admission checks can expose independent bootstrap, but clients may see only one side.

### codex-1:E25
- contract: The state-machine service must compute identical state and outputs from identical initial state and ordered command inputs.
- source: §11.6 "every server must arrive at the same result after applying the same series of client requests."
- stated: stated
- violation: Commands consult local time, randomness, or platform-dependent iteration order independently on each replica.
- at-risk: Correct replicated-service results and linearizability fail despite matching Raft logs; this need not violate the log-entry formulation of State Machine Safety.
- detectable: partly — state hashes and response comparison detect divergence after execution.

### codex-1:E26
- contract: The state-machine recovery service must reconstruct the state represented by the discarded prefix before processing retained log entries.
- source: §5 "discarded log entries from disk before it can apply any entries from the Raft log."
- stated: stated
- violation: A restarting application starts with empty state and applies only the uncompacted log suffix.
- at-risk: Correct client results and linearizability fail because the recovered application omits committed effects.
- detectable: partly — snapshot identity and state invariants detect many omissions, but a plausible wrong state can pass.

### codex-1:E27
- contract: A persistent state-machine backend must recover its last-applied index consistently with the durable application effects.
- source: §3.8 "them, its last applied index must also be persistent."
- stated: implicit
- violation: A balance update persists but its applied index rolls back, or the index persists without the update.
- at-risk: Exactly-once effects and linearizability fail through replayed or skipped commands; matching logs alone cannot prevent this.
- detectable: partly — transactional recovery metadata can reveal mismatches, but separate valid records may conceal them.

### codex-1:E28
- contract: A compaction backend must durably preserve all effects it reports as safely replacing a Raft log prefix.
- source: §5 "the state machine reflects those entries to disk in a way that can recover the current system state."
- stated: stated
- violation: A state-machine library reports completion while its replacement state remains only in a write cache.
- at-risk: Committed-data durability and correct recovery fail once Raft discards the only reliable command copies.
- detectable: partly — backend durability checks detect errors but cannot validate a lying device after every acknowledgment.

### codex-1:E29
- contract: The state-machine snapshot service must serialize and restore an exact, complete representation of the represented application state.
- source: §5.1.3 "state and writing that data out to a file, while loading is the reverse process."
- stated: implicit
- violation: Serialization omits a field or restoration changes numeric values or object relationships.
- at-risk: Correct client results and linearizability fail after restart or snapshot installation despite intact logs.
- detectable: partly — round-trip checks and state hashes reveal many omissions, but shared serialization mistakes can escape.

### codex-1:E30
- contract: Snapshots must include the state-machine session and duplicate-response information needed to preserve client semantics.
- source: §5.1 "serialize the information they keep for providing linearizability to clients (see Chapter 6)."
- stated: stated
- violation: A snapshot preserves database values but omits cached results and session serial numbers.
- at-risk: Exactly-once semantics fail when a retry after recovery executes an already completed operation again.
- detectable: partly — schema validation can check inclusion, but a forgotten field can look like an empty valid table.

### codex-1:E31
- contract: The snapshot provider must supply a consistent state image corresponding to one application prefix.
- source: §5 "state, which the leader then sends to the follower."
- stated: stated
- violation: A snapshot combines an old account debit with a new account credit from another instant.
- at-risk: Correct state-machine recovery and linearizability fail because the installed image never represented a valid committed prefix.
- detectable: partly — version markers and invariants catch some mixed images but cannot prove arbitrary state consistency.

### codex-1:E32
- contract: When concurrent snapshots rely on operating-system copy-on-write, that service must preserve the captured point-in-time view.
- source: §5.1.1 "to make a copy of the server’s entire address space."
- stated: implicit
- violation: The snapshot child sees later parent writes through a broken or unsuitable shared mapping.
- at-risk: Correct snapshot recovery fails because the resulting state can mix command prefixes.
- detectable: partly — version validation may expose mixed state, but valid-looking images can conceal it.

### codex-1:E33
- contract: The host must supply enough memory for the chosen concurrent snapshot method or permit controlled backpressure before exhaustion.
- source: §5.1.1 "Servers require additional memory for snapshotting concurrently, which should be planned for"
- stated: stated
- violation: Copy-on-write amplification triggers OOM kills on several snapshotting replicas.
- at-risk: Availability and compaction progress fail; crash-safe storage should preserve core safety.
- detectable: yes — allocation failures, memory pressure, and OOM events expose exhaustion.

### codex-1:E34
- contract: The deployment must provide enough disk capacity and I/O service for its log, retained snapshots, and ongoing compaction workload.
- source: §5.1.2 "and requires about 6 times the disk capacity as that needed to store a single copy of the state (the"
- stated: implicit
- violation: The log and temporary snapshot fill the volume before compaction can finish.
- at-risk: Sustained request availability fails when entries or snapshots cannot be persisted; this does not inherently break safety.
- detectable: yes — free-space and write-error monitoring expose exhaustion.

### codex-1:E35
- contract: A disk-state-machine snapshot backend must retain an immutable consistent disk image throughout transfer.
- source: §5.2 "snapshot for a long enough period to transmit it."
- stated: stated
- violation: A volume snapshot expires or its backing blocks are overwritten while a slow follower copies it.
- at-risk: Follower recovery and correct client results are at risk if a changing image is installed as one committed state.
- detectable: partly — snapshot handles and checksums expose invalidation, but an unversioned image can silently change.

### codex-1:E36
- contract: An LSM-based compaction backend must preserve the immutability and completeness of the runs used for state transfer.
- source: §5.3.3 "being modified during the transfer."
- stated: implicit
- violation: Background cleanup deletes a required run or modifies its contents during transfer.
- at-risk: Snapshot-based recovery and availability fail, and accepted incomplete state can violate client consistency.
- detectable: partly — pinned run manifests and checksums expose many missing or changed files.

### codex-1:E37
- contract: Client discovery infrastructure must be reachable at its configured well-known location.
- source: §6.1 "accessible at a well-known location."
- stated: stated
- violation: DNS is unavailable to fresh clients even though the Raft majority is healthy.
- at-risk: Client availability fails because clients cannot find a usable service endpoint.
- detectable: yes — discovery failures and lookup timeouts reveal the symptom.

### codex-1:E38
- contract: The external directory and its maintenance scripts must keep discovery inclusive as membership changes.
- source: §6.1 "consistent, but it should be inclusive: clients should always be able to find all of the cluster"
- stated: stated
- violation: DNS retains only removed members or never advertises new members before old ones disappear.
- at-risk: Client availability fails if discovery omits reachable active servers; directory linearizability is unnecessary.
- detectable: partly — comparison with membership detects omissions, but individual clients cannot know missing endpoints.

### codex-1:E39
- contract: When clients use broadcast or multicast discovery, the network must support that discovery mechanism across the intended scope.
- source: §6.1 "only work in particular environments that support these features."
- stated: stated
- violation: A network segment filters discovery multicast while permitting direct Raft traffic.
- at-risk: New-client availability fails because otherwise reachable servers cannot be discovered.
- detectable: yes — failed discovery can be observed and compared with successful direct connections.

### codex-1:E40
- contract: The client library must abandon failed server connections and retry reachable alternative members.
- source: §6.2 "simply retry with a random server. Insisting on being able to contact the last known leader"
- stated: stated
- violation: A client pins itself to a failed former leader forever.
- at-risk: Client request availability fails despite a healthy majority and a usable new leader.
- detectable: partly — connection and retry telemetry exposes pinning, but the servers may never see the stranded client.

### codex-1:E41
- contract: Clients must assign distinct command serial numbers within each client identity and preserve the same identity and serial on retries.
- source: §6.3 "serial numbers to every command. Each server’s state machine maintains a session for each client."
- stated: stated
- violation: A restarted client resets its serial counter under the old identity, or retries a debit with a new serial.
- at-risk: Linearizability and exactly-once intent fail through suppressed new commands or repeated effects.
- detectable: partly — conflicting payload checks reveal some reuse, but a new serial cannot reveal that it represents a retry.

### codex-1:E42
- contract: Client identity allocation and client use must keep simultaneously distinct sessions uniquely identified.
- source: §6.3 "To implement this, each client is given a unique identifier, and clients assign unique"
- stated: stated
- violation: Two applications reuse a copied registration ID and overlapping serial numbers.
- at-risk: Correct responses and exactly-once semantics fail when one client’s operations are mistaken for another’s duplicates.
- detectable: partly — identity ownership checks detect some sharing, but identical-looking sessions can escape.

### codex-1:E43
- contract: A state-machine session backend must retain deduplication results until the protocol permits their removal and expire sessions deterministically.
- source: §6.3 "session expiry must be deterministic, just as normal state"
- stated: stated
- violation: Local wall-clock expiry deletes a session on one replica while another keeps it, or cached replies disappear early.
- at-risk: Linearizability and deterministic replicated results fail when one replica reexecutes a duplicate that another filters.
- detectable: partly — state hashes and expiry traces reveal disagreement, but coordinated premature deletion can be silent.

### codex-1:E44
- contract: Concurrent clients must report an accurate lowest unanswered sequence number before servers discard older response records.
- source: §6.3 "With each request, the client includes the lowest sequence"
- stated: stated
- violation: A client advances its acknowledgment watermark past a request whose reply was lost.
- at-risk: Exactly-once retry behavior and correct response recovery are at risk because the server may discard a still-needed reply.
- detectable: partly — servers can reject impossible counters, but cannot know whether a client actually received a response.

### codex-1:E45
- contract: Clients that require uninterrupted sessions must send keep-alives within the service’s session-retention policy during inactivity.
- source: §6.3 "Live clients issue keep-alive requests during periods of inactivity, which are also augmented with"
- stated: stated
- violation: A suspended client misses keep-alives and resumes after its session expires.
- at-risk: Session continuity and client availability fail; correctly rejected expired requests preserve safety rather than silently execute duplicates.
- detectable: yes — missing sessions and explicit expiration errors reveal the violation on resumption.

### codex-1:E46
- contract: Clients must treat session-expiration errors as loss of retry certainty rather than automatically resubmit ambiguous commands in a new session.
- source: §6.3 "new session for a client any time there is no record of it, but this would risk duplicate execution of"
- stated: implicit
- violation: After expiration, middleware registers anew and repeats a payment whose first execution may have committed.
- at-risk: Exactly-once application intent fails across sessions because old deduplication records are unavailable.
- detectable: partly — expiration is visible, but a new request does not identify its unknown old effect.

### codex-1:E47
- contract: Operations classified as read-only must leave all replicated application and session state unchanged.
- source: §6.4 "Read-only client commands only query the replicated state machine; they do not change it."
- stated: stated
- violation: A query increments a replicated counter or lazily mutates state while bypassing the log.
- at-risk: Replicated-state consistency and linearizability fail because mutations escape ordered replication.
- detectable: partly — write guards or state hashes reveal some mutations, but hidden side effects may escape.

### codex-1:E48
- contract: The state-machine query interface must observe a coherent state at least as recent as the supplied read barrier.
- source: §6.4 "The leader waits for its state machine to advance at least as far as the readIndex; this is current"
- stated: implicit
- violation: An asynchronous database reports applied progress before its query view exposes those updates, or a query sees half an update.
- at-risk: Linearizable reads fail despite a correct leadership check and read index.
- detectable: partly — versioned query results can expose lag, but incorrect backend visibility metadata can conceal it.

### codex-1:E49
- contract: For clock-based read leases, effective server clocks must remain within the assumed relative drift bound, including host pauses and migration effects.
- source: §6.4.1 "The lease approach assumes a bound on clock drift across servers (over a given time period, no"
- stated: stated
- violation: A paused leader resumes with an apparently live lease after followers have elected a new leader.
- at-risk: Linearizable reads fail and results may be arbitrarily stale; basic Raft log safety does not depend on this bound.
- detectable: partly — independent clock and pause monitoring can invalidate leases, but purely local observations cannot guarantee the bound.

### codex-1:E50
- contract: For the optional monotonic-read extension, clients must carry their highest observed state index across requests and server changes.
- source: §6.4.1 "results they had seen, and they would provide this information to servers on each request."
- stated: stated
- violation: A client reconnects or switches connection pools and drops its observed-index watermark.
- at-risk: The stated monotonic-progress guarantee can fail because a new server may answer from an older state; the source calls the extension sequential consistency.
- detectable: partly — clients can audit index regressions if they retain history, but a server cannot reconstruct an omitted watermark.

### codex-2:E1
- contract: The host must restrict server failures to stopping and recovery rather than arbitrary execution.
- source: §2 "Servers are assumed to fail by stopping;"
- stated: stated
- violation: A faulty CPU or memory bit flip changes a vote, term, or command while the process continues.
- at-risk: Election Safety, Log Matching, Leader Completeness, and State Machine Safety can fail because the server no longer follows the transition rules.
- detectable: partly — checksums and assertions catch some corruption, but plausible incorrect execution can evade them.

### codex-2:E2
- contract: The transport must deliver authentic, unaltered messages attributable to their actual sending server.
- source: §8.1 "The network may reorder, drop, and duplicate messages."
- stated: implicit
- violation: A proxy corrupts an entry payload or an attacker fabricates successful replication acknowledgments.
- at-risk: Log Matching or Leader Completeness can fail when messages assert entries or votes that never existed; this exceeds loss, duplication, and reordering.
- detectable: partly — authentication and integrity checks can reject many altered messages, but cannot establish an honest endpoint.

### codex-2:E3
- contract: Stable storage must retain an acknowledged current term across crashes and restarts.
- source: §3.8 "each server persists its current term and vote;"
- stated: stated
- violation: A storage rollback restores a term older than the last completed persistence operation.
- at-risk: Election Safety and Leader Completeness are at risk because the recovered server can accept obsolete leadership and repeat prior decisions.
- detectable: partly — peers may expose a regression, but an isolated recovered server cannot prove its prior term.

### codex-2:E4
- contract: Stable storage must retain an acknowledged vote across crashes and restarts.
- source: §3.8 "this is necessary to prevent the server from voting twice in the same term"
- stated: stated
- violation: A power failure loses a vote that fsync reported durable.
- at-risk: Election Safety fails if the server votes for two candidates in one term; conflicting same-term logs can follow.
- detectable: partly — external vote histories can expose double voting, but ordinary recovery has no independent copy.

### codex-2:E5
- contract: Stable storage must preserve the contents and order of acknowledged durable log entries.
- source: §3.8 "this prevents committed entries from being lost or “uncommitted” when servers restart."
- stated: stated
- violation: A controller drops or corrupts an acknowledged log tail after power loss.
- at-risk: Leader Completeness and State Machine Safety can fail when a quorum no longer remembers a committed entry.
- detectable: partly — checksums detect many corruptions, but a valid old log prefix can look legitimate.

### codex-2:E6
- contract: The storage stack must honor completion and ordering barriers used to persist Raft state before external acknowledgments.
- source: §3.8 "Each server also persists new log entries before they are counted towards the entries’ com- mitment;"
- stated: implicit
- violation: A drive reports a successful flush while data remains only in an unprotected volatile cache.
- at-risk: Leader Completeness and acknowledged-write durability fail if counted replicas disappear after a crash.
- detectable: partly — I/O errors are visible, but dishonest flush completion normally requires independent crash testing to expose.

### codex-2:E7
- contract: The process manager must prevent two live processes from using one voting server identity.
- source: §4 "there would be an extra vote"
- stated: implicit
- violation: A VM clone and its original both run with the same server identity and separate state.
- at-risk: Election Safety can fail because one logical voter can supply inconsistent votes to different candidates.
- detectable: partly — competing connections or identity leases can expose clones, but partitioned clones may evade detection.

### codex-2:E8
- contract: An operator must fence the old server permanently when replacing a member by reusing its network address.
- source: §4 "the administrator must guarantee that the replaced server will never come back up,"
- stated: stated
- violation: An old machine reboots after its address has been assigned to a replacement.
- at-risk: Election Safety and subsequent log safety are at risk from the extra vote explicitly identified by the source.
- detectable: partly — duplicate endpoints or conflicting histories may reveal it, but a partition can hide the old server.

### codex-2:E9
- contract: Recovery tooling must not restart a server with its old identity after any of its persistent state has been lost.
- source: §3.8 "If a server loses any of its persistent state, it cannot safely rejoin the cluster with its prior identity."
- stated: stated
- violation: An administrator restores an old VM snapshot or deletes the data directory and reuses the member ID.
- at-risk: Election Safety or Leader Completeness can fail because the server forgets votes or committed entries.
- detectable: partly — a missing-state marker can help, but a self-consistent old backup need not disclose rollback.

### codex-2:E10
- contract: Operators must preserve a majority of persistent histories to retain both committed data and normal recovery progress.
- source: §3.8 "If a majority of the cluster loses its persistent state, however, log entries may be lost"
- stated: stated
- violation: A shared storage failure or coordinated restore wipes most members.
- at-risk: Acknowledged-write durability and availability can be lost; ordinary membership changes cannot repair the missing quorum.
- detectable: partly — lost volumes may be obvious, but valid older backups can conceal lost commits.

### codex-2:E11
- contract: Deployment configuration must provide an operational majority for availability.
- source: §2 "They are fully functional (available) as long as any majority of the servers are operational"
- stated: stated
- violation: Maintenance stops three members of a five-member cluster.
- at-risk: Availability fails because no election or new commitment can collect a majority; safety need not fail.
- detectable: yes — lack of quorum responses and inability to commit are observable.

### codex-2:E12
- contract: The network must allow the operational majority to exchange messages for progress.
- source: §2 "and can communicate with each other and with clients."
- stated: stated
- violation: Firewalls split all live members into groups smaller than a quorum.
- at-risk: Availability fails despite healthy processes because votes and replication cannot reach a majority.
- detectable: yes — timeouts and failed quorum communication reveal the symptom.

### codex-2:E13
- contract: The network must connect clients to the available cluster for client-visible availability.
- source: §2 "and can communicate with each other and with clients."
- stated: stated
- violation: A working quorum is unreachable from the application network.
- at-risk: Client availability fails even though the cluster itself can elect and commit.
- detectable: partly — clients see timeouts, but servers cannot observe every client-side route.

### codex-2:E14
- contract: Host scheduling, storage, and network latency must permit RPC broadcasts substantially faster than the configured election timeout for stable leadership.
- source: §3.9 "broadcast time should be an order of magnitude less than the election timeout"
- stated: stated
- violation: Disk stalls, CPU starvation, or long WAN latency delay heartbeats past election timeouts.
- at-risk: Availability and timely leader election degrade through repeated elections; basic safety remains timing independent.
- detectable: yes — heartbeat latency, election frequency, and scheduler stalls can be measured.

### codex-2:E15
- contract: Servers must remain operational for intervals substantially longer than election timeouts to sustain progress.
- source: §3.9 "The election timeout should be a few orders of magnitude less than MTBF"
- stated: stated
- violation: Crash loops or repeated orchestrator restarts terminate candidates before they can lead.
- at-risk: Availability fails when no stable leader lasts long enough to commit.
- detectable: yes — restart rates and leadership durations expose the condition.

### codex-2:E16
- contract: The timer and scheduling service must eventually deliver election timeouts on surviving candidates.
- source: §3.4 "Each candidate restarts its randomized election timeout at the start of an election"
- stated: implicit
- violation: A timer service freezes indefinitely while no leader exists.
- at-risk: Availability fails because surviving followers or candidates never retry an election.
- detectable: partly — another watchdog can detect timer starvation, but a fully suspended process cannot self-diagnose.

### codex-2:E17
- contract: The randomness service must supply sufficiently decorrelated election timeout draws across servers and retries.
- source: §3.4 "This spreads out the servers so that in most cases only a single server will time out;"
- stated: implicit
- violation: Cloned PRNG states cause every candidate to choose the same timeout repeatedly.
- at-risk: The promised rapid resolution of split votes and availability degrade; safety does not depend on good randomness.
- detectable: partly — repeated equal timeout draws can be monitored but finite observations cannot establish independence.

### codex-2:E18
- contract: During membership changes the environment must keep a majority of the old configuration available until the new configuration commits.
- source: §4.2.4 "a majority of the old configuration is available (at least until Cnew is committed)"
- stated: stated
- violation: Automation powers off old members before the replacement configuration commits.
- at-risk: Availability during membership change fails because the old quorum is still needed.
- detectable: yes — old-configuration quorum responses and transition status are observable.

### codex-2:E19
- contract: During membership changes the environment must provide an available majority of the new configuration.
- source: §4.2.4 "a majority of the new configuration is available."
- stated: stated
- violation: New members share an unreachable subnet or are stopped during the transition.
- at-risk: Membership-change progress and client availability can stall without the new quorum.
- detectable: yes — replication responses and configuration commitment reveal the shortage.

### codex-2:E20
- contract: Membership management policy must retain enough replicas to meet the intended durability and failure-tolerance target.
- source: §4.4 "it could then be left with too few replicas to satisfy the intended durability and fault-tolerance requirements."
- stated: stated
- violation: An automatic failure handler repeatedly removes failed members until only one remains.
- at-risk: The operator-facing fault-tolerance target fails even if current Raft operations succeed safely.
- detectable: partly — replica count is visible, but the intended target must be supplied externally.

### codex-2:E21
- contract: Replacement orchestration must add the replacement before removing the old member when continuous single-failure tolerance is required.
- source: §4.4 "it is prefer- able to add servers before removing servers."
- stated: stated
- violation: A three-member cluster is reduced to two before the new member is added.
- at-risk: Continuous one-failure availability is lost during replacement because both remaining voters are required.
- detectable: yes — configuration size and operation order can be audited at runtime.

### codex-2:E22
- contract: Bootstrap tooling must supply one coherent initial cluster configuration rather than independently bootstrap competing clusters as one service.
- source: §4.4 "one server is initialized with a configuration entry as the first entry in its log."
- stated: implicit
- violation: Several hosts independently bootstrap singleton clusters behind one service endpoint.
- at-risk: The advertised single consistent service fails because unrelated quorums can acknowledge conflicting histories.
- detectable: partly — cluster identifiers can distinguish histories, but isolated clusters cannot discover each other.

### codex-2:E23
- contract: State machines must compute identical states and outputs from identical initial states and command sequences.
- source: §2 "Since the state machines are deterministic, each computes the same state and the same sequence of outputs."
- stated: stated
- violation: Replicas use local time, unordered iteration, random numbers, or incompatible application versions.
- at-risk: Consistent replicated-service results fail despite identical logs; Figure 3.2 State Machine Safety alone only constrains applied entries.
- detectable: partly — state hashes can expose divergence, but agreement on a hash is not proof of every output.

### codex-2:E24
- contract: Nondeterministic state-machine inputs must be supplied identically to all replicas through the replicated command.
- source: §11.6 "the effects of client requests must not depend on each server’s current time."
- stated: stated
- violation: Each replica independently obtains a timestamp or external-service response while applying a command.
- at-risk: Single-state-machine behavior and client result consistency fail when identical entries have different effects.
- detectable: partly — deterministic replay or state comparison may catch differences but cannot observe every external dependency.

### codex-2:E25
- contract: A persistent state-machine service must recover its applied index consistently with its durable application state.
- source: §3.8 "its last applied index must also be persistent."
- stated: stated
- violation: The application database persists an increment but loses its applied-index update, or persists the index before the increment.
- at-risk: Exactly-once effects and state consistency fail through replaying an applied command or skipping an unapplied command.
- detectable: partly — transactional recovery metadata can detect some mismatches; plausible state/index pairs may conceal them.

### codex-2:E26
- contract: The state-machine compaction service must retain recoverable durable effects before releasing the corresponding Raft log prefix.
- source: §5 "the state machine reflects those entries to disk in a way that can recover the current system state."
- stated: stated
- violation: A database signals that compaction is safe while its writes are still only in RAM.
- at-risk: Committed-state durability fails after a crash because neither snapshot nor retained log contains the discarded effects.
- detectable: partly — durable checkpoints can be checked, but false durability acknowledgments are hard to detect online.

### codex-2:E27
- contract: The state-machine recovery service must restore the discarded prefix before processing retained log entries.
- source: §5 "load the state corresponding to the discarded log entries from disk before it can apply any entries from the Raft log."
- stated: stated
- violation: A plugin starts from empty state and applies only the retained suffix.
- at-risk: Replicated-service correctness fails because commands execute against a missing committed history.
- detectable: partly — checkpoint indices and state hashes may catch it, but application content need not be independently known.

### codex-2:E28
- contract: Snapshot serialization and loading must faithfully preserve the application state represented by the checkpoint.
- source: §5.1.3 "Saving a snapshot involves serializing the state machine’s state and writing that data out to a file, while loading is the reverse process."
- stated: implicit
- violation: The serializer omits a map, changes integer precision, or reconstructs dependencies incorrectly.
- at-risk: Durable state and consistent client results fail after recovery or snapshot installation even if log entries remain consistent.
- detectable: partly — round-trip checks and state hashes catch some omissions; shared serialization defects may evade them.

### codex-2:E29
- contract: Snapshot services must preserve client deduplication and response information along with application state.
- source: §5.1 "State machines must also serialize the information they keep for providing linearizability to clients"
- stated: stated
- violation: A snapshot keeps account balances but drops session sequence numbers and cached responses.
- at-risk: Exactly-once linearizability fails when a retried command is applied again after snapshot recovery.
- detectable: partly — snapshot schemas and session checks help, but missing old response records may look like expiration.

### codex-2:E30
- contract: Snapshot and copy-on-write services must expose a consistent point-in-time state while writes continue.
- source: §5.2 "Disk-based state machines must be able to provide a consistent snapshot of the disk"
- stated: stated
- violation: A volume snapshot combines blocks from before and after a multi-block update.
- at-risk: A follower or recovered node can serve a state that no committed prefix ever produced, violating consistent-service semantics.
- detectable: partly — application invariants or state hashes detect some mixed images, but plausible mixed state can escape.

### codex-2:E31
- contract: The filesystem must provide the crash-safe publication semantics used to replace a completed snapshot file.
- source: §5.1.3 "then renames the file when writing is complete and has been flushed to disk;"
- stated: implicit
- violation: After power failure the published snapshot name points to a partial file despite successful flush and rename operations.
- at-risk: Recovery and committed-state durability are at risk if the old log has already been discarded.
- detectable: partly — checksums and completeness markers detect some partial files but cannot restore discarded data.

### codex-2:E32
- contract: The host must provide enough memory for the live state and additional concurrent snapshot copy-on-write data.
- source: §5.1.1 "Servers require additional memory for snapshotting concurrently, which should be planned for and managed."
- stated: stated
- violation: Snapshot dirty pages exhaust container memory and trigger an OOM kill.
- at-risk: Availability and promised snapshot concurrency degrade; a quorum of simultaneous OOMs stops service.
- detectable: yes — allocation failures, memory pressure, and OOM records expose the violation.

### codex-2:E33
- contract: The host must provide enough storage capacity for retained logs, old state, and compaction output simultaneously.
- source: §5.1.2 "requires about 6 times the disk capacity as that needed to store a single copy of the state"
- stated: implicit
- violation: A volume has space for the live database but not the old snapshot, log, and new snapshot together.
- at-risk: Availability fails when durable appends or compaction cannot complete.
- detectable: yes — free-space accounting and failed writes reveal exhaustion.

### codex-2:E34
- contract: The host must provide sufficient CPU and disk bandwidth for compaction without starving quorum communication and application work.
- source: §5.1.2 "Snapshotting still creates a burst of CPU and disk bandwidth usage that might impact client performance."
- stated: stated
- violation: All replicas snapshot on saturated disks and miss heartbeats or request deadlines.
- at-risk: Timely client service and stable leadership degrade; the basic safety properties remain intact.
- detectable: yes — resource utilization, heartbeat delays, and request latency expose starvation.

### codex-2:E35
- contract: A state-machine log-cleaning service must preserve every live value and still-needed deletion marker.
- source: §5.3.1 "RAMCloud preserves deletion commands (called tombstones) as necessary"
- stated: implicit
- violation: A storage library removes a tombstone while an older segment still contains the deleted key.
- at-risk: Durable application correctness fails when deleted data reappears after compaction or recovery.
- detectable: partly — state comparisons can detect resurrection, but a plausible old value need not trigger an invariant.

### codex-2:E36
- contract: A client discovery directory must remain reachable at its well-known location when clients depend on it.
- source: §6.1 "an external directory service, such as DNS, that is accessible at a well-known location."
- stated: stated
- violation: DNS becomes unreachable and new clients cannot locate any member.
- at-risk: Client availability fails even with a healthy Raft quorum.
- detectable: partly — clients observe lookup failure, while servers may have no visibility into their resolvers.

### codex-2:E37
- contract: The discovery directory and its administrative update process must keep the server list inclusive through membership changes.
- source: §6.1 "clients should always be able to find all of the cluster servers,"
- stated: stated
- violation: DNS still lists only removed servers because administrative scripts never added replacements.
- at-risk: Clients may fail to find the available leader, defeating client availability despite successful reconfiguration.
- detectable: partly — comparing directory answers with membership detects some omissions, but caches and split DNS complicate observation.

### codex-2:E38
- contract: Networks used for broadcast or multicast discovery must actually support the selected discovery mechanism.
- source: §6.1 "this will only work in particular environments that support these features."
- stated: stated
- violation: A deployment moves into a routed cloud network that drops discovery multicast.
- at-risk: New-client availability fails because clients cannot discover the cluster.
- detectable: yes — discovery timeouts and diagnostic probes expose failure.

### codex-2:E39
- contract: Client software must retry reachable alternative members after losing its connection to a server.
- source: §6.2 "If a client loses its connection to the leader (or any particular server), it should simply retry with a random server."
- stated: stated
- violation: A client pins all retries to a failed former leader.
- at-risk: Client availability fails even though a new leader can service requests.
- detectable: partly — a client can log its retry targets, but the cluster cannot observe attempts that never reach it.

### codex-2:E40
- contract: Client identity management must prevent distinct active clients from sharing a deduplication identity.
- source: §6.3 "each client is given a unique identifier"
- stated: stated
- violation: Two application instances restore the same session token and issue different commands with the same serial number.
- at-risk: Linearizable exactly-once request semantics fail because one client can receive another command’s cached result.
- detectable: partly — comparing payload hashes may expose collisions, but identical payloads or missing histories conceal them.

### codex-2:E41
- contract: Clients must assign distinct serial numbers to distinct commands within a session.
- source: §6.3 "clients assign unique"
- stated: stated
- violation: A client counter resets after restart while the old session remains valid.
- at-risk: Linearizability fails when a new operation is mistaken for an already executed request and returns its old result.
- detectable: partly — payload comparisons detect some reuse but cannot distinguish all new invocations from retries.

### codex-2:E42
- contract: Clients must preserve the identity, serial number, and command contents of an operation across retries.
- source: §6.3 "servers must filter out duplicate requests."
- stated: implicit
- violation: A retry allocates a new serial number or changes the command while retaining the old number.
- at-risk: Exactly-once semantics fail through duplicate effects or returning a response for a different operation.
- detectable: partly — conflicting payloads can be rejected, but a fresh ID hides the fact that an operation is a retry.

### codex-2:E43
- contract: Concurrent clients must report a truthful lower bound for sequence numbers whose replies are still outstanding.
- source: §6.3 "the client includes the lowest sequence number for which it has not yet received a response"
- stated: stated
- violation: A pipelined client advances its response watermark past an unacknowledged request.
- at-risk: The server may discard a response still needed for safe retry, jeopardizing the stated concurrent-request semantics; exact behavior depends on expired-response handling.
- detectable: partly — impossible future bounds can be rejected, but the server cannot know which replies the client actually received.

### codex-2:E44
- contract: State-machine session expiration must use deterministic replicated inputs rather than independently observed local time.
- source: §6.3 "session expiry must be deterministic, just as normal state machine operations must be."
- stated: stated
- violation: Each replica expires sessions using its own wall clock.
- at-risk: Replicas can disagree about duplicate suppression and diverge in application state and results.
- detectable: partly — session and state comparisons expose some divergence, but different clocks need not immediately affect a request.

### codex-2:E45
- contract: Clients that require continuous session validity must issue keep-alives often enough for the configured expiry policy.
- source: §6.3 "Live clients issue keep-alive requests during periods of inactivity,"
- stated: stated
- violation: A suspended client misses its inactivity deadline.
- at-risk: Continued client availability fails when its session expires; the specified rejection preserves safety.
- detectable: yes — the cluster can detect expiration and reject the old session.

### codex-2:E46
- contract: Client recovery must treat an expired session as an uncertain prior outcome rather than blindly resubmitting outstanding effects in a new session.
- source: §6.3 "commands that were executed before the client’s previous session was expired."
- stated: implicit
- violation: An SDK automatically opens a new session and repeats an unacknowledged money transfer.
- at-risk: End-to-end exactly-once semantics fail across session expiration even though each session is handled correctly.
- detectable: partly — the SDK sees expiration but cannot determine the old command outcome without application-specific evidence.

### codex-2:E47
- contract: Queries submitted through the read-only path must have no state-changing effects.
- source: §6.4 "Read-only client commands only query the replicated state machine; they do not change it."
- stated: stated
- violation: A query callback increments a persisted counter or updates application data without a log entry.
- at-risk: Replicated-service consistency fails because effects bypass replicated ordering and may occur on only one replica.
- detectable: partly — read-only transactions can block writes, but arbitrary external side effects can evade enforcement.

### codex-2:E48
- contract: Clocks used for lease-based reads must obey the configured relative drift bound throughout each lease.
- source: §6.4.1 "The lease approach assumes a bound on clock drift across servers"
- stated: stated
- violation: A leader clock pauses while follower clocks advance enough to elect a replacement.
- at-risk: Read linearizability fails because an old leader can return arbitrarily stale information while believing its lease valid.
- detectable: partly — independent clocks can detect some drift, but a paused process cannot reliably certify the bound itself.

### codex-2:E49
- contract: Host scheduling and migration must preserve the effective clock-drift bound relied on by lease reads.
- source: §6.4.1 "due to scheduling and garbage collection pauses, virtual machine migrations, or clock rate adjustments for time synchronization"
- stated: stated
- violation: A VM resumes a lease-holding process after a long suspension with an effectively unexpired lease.
- at-risk: Read linearizability is at risk from stale lease authority; this condition is specific to the optional clock-based read scheme.
- detectable: partly — resume notifications and independent elapsed-time checks help, but arbitrary suspension can evade local checks.

### codex-2:E50
- contract: Clients using the optional monotonic-read extension must retain and send the greatest observed state index across server changes.
- source: §6.4.1 "Clients would track the latest index corresponding to results they had seen, and they would provide this information to servers on each request."
- stated: stated
- violation: A reconnecting client loses its watermark and accepts an older follower state.
- at-risk: The optional monotonic-progress guarantee fails when the client observes an earlier state after a later one.
- detectable: partly — the client can compare retained indices, but a lost watermark cannot be reconstructed from the next reply alone.

### grok-1:E1
- contract: A server fails only by stopping, and until it stops it runs the protocol as written, including the messages it sends and the state it keeps.
- source: §8.1 "Servers fail by stopping and may later restart from stable storage on disk."
- stated: stated
- violation: A live process keeps sending votes or log entries after a bit flip, wild pointer, or partial memory corruption changes a term, a vote, or a command.
- at-risk: Election Safety and State Machine Safety fail because both rest on servers obeying the protocol whenever they are not stopped; a single forged-by-bug vote can complete a second majority in one term.
- detectable: partly — replica invariant checks can notice two leaders in one term or a log mismatch after the fact, and a well-formed but wrong vote is indistinguishable from a legal one.

### grok-1:E2
- contract: The network may delay, drop, duplicate, reorder, and partition messages, and it must not alter an RPC payload or deliver a message invented by a host that is not the member it names.
- source: §2.1 "They ensure safety (never returning an incorrect result) under all non-Byzantine conditions,"
- stated: implicit
- violation: A bit error changes a log term in flight, or a host outside the configuration injects a RequestVote or AppendEntries that servers accept as coming from a member.
- at-risk: Election Safety and Log Matching fail: an extra or altered vote elects two leaders in one term, and an altered command at the same index and term makes two logs disagree.
- detectable: partly — a checksum or peer authentication above the transport would reject the bad message; with neither, the cluster accepts it as normal traffic.

### grok-1:E3
- contract: The host runs at most one live process for each voting identity, and a server that has been replaced must never accept RPCs as that member again.
- source: §4 "the administrator must guarantee that the replaced server will never come back up,"
- stated: stated
- violation: An operator starts a VM clone, a forked child, or the old host while the replacement is already voting under the same server identity or the same address.
- at-risk: Election Safety fails: the two processes can grant two votes in one term, so two candidates can each collect a majority (the dissertation's "extra vote").
- detectable: partly — binding one address twice fails loudly, but two addresses for one identity are accepted as normal votes until logs diverge.

### grok-1:E4
- contract: A server that has lost any of its persistent state must not rejoin under its previous identity; it may return only as a new member through a membership change.
- source: §3.8 "If a server loses any of its persistent state, it cannot safely rejoin the cluster with its prior identity."
- stated: stated
- violation: An operator deletes the data directory or replaces the disk, then starts the same server id with an empty log and a fresh term.
- at-risk: Leader Completeness fails when that empty member's vote completes a majority for a candidate that never stored a committed entry, so a later leader applies a different command at that index.
- detectable: partly — an empty log on a known member can be noticed by an operator, and the protocol still accepts the member's vote.

### grok-1:E5
- contract: A majority of the cluster must not lose the persistent state it has already acknowledged, or the operator must not proceed as if the old log were still intact.
- source: §3.8 "If a majority of the cluster loses its persistent state, however,"
- stated: stated
- violation: A shared disk, a restore of an old snapshot onto a majority of members, or a script wipes three of five data directories and the processes start again as the same cluster.
- at-risk: The durability guarantee fails: committed entries can be gone, and membership changes cannot make progress; State Machine Safety fails if the emptied majority elects a leader and commits a new command at an old index.
- detectable: partly — a majority that cannot form a quorum is obvious, and a majority that restarts empty and then commits a new history looks like a fresh cluster unless something outside the protocol remembers the old log.

### grok-1:E6
- contract: Stable storage must retain the latest current term and the vote granted in that term across a restart, including after power loss.
- source: §3.8 "each server persists its current term and vote; this is necessary to prevent the server from"
- stated: stated
- violation: Power fails after a server has sent a vote, and the disk comes back without that term or that vote, so the restarted process votes for a second candidate in the same term.
- at-risk: Election Safety fails because one server supplies two votes in one term; Leader Completeness also fails if a forgotten higher term lets the server replace a newer leader's entries with entries from a deposed leader.
- detectable: no — after restart the server has no record of the lost vote, and the second vote is a legal RequestVote response.

### grok-1:E7
- contract: Stable storage must retain every log prefix the server has acknowledged as stored, and a restart must not revive an older prefix, a hole, or a different command at a stored index.
- source: §3.8 "Each server also persists new log entries before they are counted towards"
- stated: stated
- violation: A follower answers AppendEntries successfully, then a crash or a disk rollback returns a shorter log, and the leader has already counted that follower toward commitment.
- at-risk: The durability guarantee for committed entries fails, and State Machine Safety fails if a later leader is elected without the committed command and writes a different one at that index.
- detectable: partly — a later consistency check can fail if the truncated server still holds a conflicting suffix; a clean rollback to a prefix looks like an ordinary lagging follower.

### grok-1:E8
- contract: A write that the disk has confirmed as flushed must still be readable after power loss, which means a volatile write cache must not acknowledge the flush early.
- source: §10.2 "flushes the log entry to disk, and sends out AppendEntries requests."
- stated: implicit
- violation: The drive or the hypervisor reports the flush complete while the data is only in a volatile cache, and power loss drops the term, the vote, or the log entries that peers already counted.
- at-risk: The same committed entries the leader may treat as durable once a majority of followers have flushed can vanish, so Leader Completeness and the durability guarantee both fail.
- detectable: no — the successful flush is the only signal Raft has, and nothing in the protocol probes that the bits survived power loss.

### grok-1:E9
- contract: Stable storage must return the bytes that were written for the term, the vote, the log, and snapshots, not a silently different or torn record that still parses.
- source: §5.1.3 "apply a checksum to it"
- stated: implicit
- violation: A torn sector changes a stored term or command into a different value that the server loads as a valid log entry.
- at-risk: Log Matching fails because one index and term now stand for two commands, so two state machines apply different entries at that index.
- detectable: partly — a checksum, which the dissertation says is worth adding, rejects the torn record; without one, a still-parseable record is loaded as normal.

### grok-1:E10
- contract: A crash during a snapshot write must not leave a partial snapshot that the server will load as the full state on the next start.
- source: §5.1.3 "flushed to disk; this ensures that no server loads a partially written snapshot on startup."
- stated: stated
- violation: The filesystem exposes the destination filename with a short or torn snapshot after power loss, and the process loads it, discards the older complete snapshot, and truncates the log to match.
- at-risk: State Machine Safety fails because this server's state no longer matches the committed prefix, and later applies continue from the wrong state.
- detectable: partly — a checksum or an expected length catches many partial files; a short file that still parses does not.

### grok-1:E11
- contract: After a log prefix is discarded, stable storage must keep the index and term of the last included entry so the remaining log stays anchored.
- source: §5 "Raft retains the index and term of the last entry it discarded; this anchors the rest of"
- stated: stated
- violation: The snapshot is kept and the log suffix is kept, but the saved last-included term is lost or replaced, so the next AppendEntries consistency check uses the wrong predecessor.
- at-risk: Log Matching fails across the snapshot boundary: a follower can accept entries that do not continue the committed prefix, and State Machine Safety fails at the first overwritten index.
- detectable: partly — a follower whose own log still has the old prefix will reject the mismatch; a server that lost the anchor and has no other copy will not.

### grok-1:E12
- contract: The latest cluster configuration in a discarded log prefix must remain durable with that prefix.
- source: §5 "Raft also retains the latest configuration from the discarded log prefix"
- stated: stated
- violation: After compaction the process restarts with the snapshot and the log suffix but with an older or empty configuration, so it computes majorities from the wrong member set.
- at-risk: Election Safety fails if the restored configuration and a newer one on other servers can each form a majority in the same term.
- detectable: partly — peers that still have the newer configuration refuse votes that do not match their log, and a server that only has the stale configuration does not see an error by itself.

### grok-1:E13
- contract: On a persistent state machine, the durable user state and the persisted last-applied index must describe the same prefix after a restart.
- source: §3.8 "its last applied index must also be persistent."
- stated: stated
- violation: The process crashes after applying an entry to its on-disk state machine and before recording the index, or the other way around, then restarts and either skips that entry or applies it again.
- at-risk: State Machine Safety fails on a second apply of a non-idempotent command, and a skipped index makes this server's state diverge from the others even though the log matches.
- detectable: partly — a double apply of a counter is visible in the data; a skipped entry with no external cross-check is not.

### grok-1:E14
- contract: The host must provide enough durable space for the log and the snapshot the server is required to keep, and running out of space must not destroy older durable state.
- source: §5 "will eventually cause availability problems: servers will either run out of space, or they will take too"
- stated: stated
- violation: The data volume fills during log append or snapshot write, or a cleanup job deletes the previous snapshot to free space before the new one is durable.
- at-risk: Availability fails when a majority cannot persist new entries; State Machine Safety fails if the only complete snapshot is removed and a restart loads nothing for a discarded prefix.
- detectable: yes — a full volume returns a write error the process can observe, unless some other agent deletes old files without an error from the disk.

### grok-1:E15
- contract: For the cluster to stay available, some majority of the configured servers must be operational.
- source: §2.1 "as long as any majority of the servers are operational"
- stated: stated
- violation: Two of three servers lose power, or a shared rack takes out three of five, and fewer than a majority remain up.
- at-risk: The availability guarantee fails because elections and commitment both need a majority; safety is not what this contract is for.
- detectable: yes — heartbeats fail, the leader steps down, and clients stop receiving results.

### grok-1:E16
- contract: That same majority must be able to exchange RPCs with one another and with clients.
- source: §2.1 "and can communicate with each other and with clients."
- stated: stated
- violation: A partition leaves no majority in any connected component, or the surviving majority cannot reach any client network.
- at-risk: Availability fails for the duration of the partition; the dissertation's safety claims are meant to survive this case, so this contract is the availability side of the same sentence.
- detectable: yes — servers on the minority side time out and clients that cannot reach the leader see errors.

### grok-1:E17
- contract: Until the new configuration entry is committed, a majority of the old configuration must stay available, and a majority of the new configuration must be available.
- source: §4.2.4 "majority of the old configuration is available (at least until Cnew is committed) and that a majority"
- stated: stated
- violation: The operator removes the leader and another old voter, or the new server is partitioned, before the new configuration is committed.
- at-risk: Availability during the membership change fails, and in the extreme the cluster cannot finish the change or elect a leader; the overlap argument for Election Safety assumes the configured sets, not that these majorities stayed up.
- detectable: yes — the configuration change stalls and client calls time out.

### grok-1:E18
- contract: Clients must be able to discover every live member, and any new member's address must be published before that member is added to the cluster.
- source: §6.1 "it should be inclusive: clients should always be able to find all of the cluster"
- stated: stated
- violation: DNS still lists only the servers that were just removed, or a new server is added before any client directory knows its address and the old addresses then go away.
- at-risk: The availability guarantee fails at the client even while a majority is healthy, because the client cannot reach a server that can route it to the leader.
- detectable: partly — the cluster does not see the directory; clients see connection failures, which an operator may not tie to the missing record.

### grok-1:E19
- contract: The time to send RPCs to the cluster and collect responses, including each recipient's durable write, must stay about an order of magnitude below the election timeout.
- source: §3.9 "broadcast time should be an order of magnitude less than the election timeout so that leaders can"
- stated: stated
- violation: Followers' disks take longer to flush than the election timeout, or the timeout is set near the wide-area round trip, so followers start elections while a leader is healthy.
- at-risk: Availability fails: the cluster does not keep a steady leader, so clients cannot get commits; the dissertation states that safety does not depend on this timing.
- detectable: partly — repeated elections appear in logs and are not labeled as a broken timing assumption.

### grok-1:E20
- contract: The election timeout must be orders of magnitude shorter than the mean time between failures of a single server.
- source: §3.9 "election timeout should be a few orders of magnitude less than MTBF so that the system makes"
- stated: stated
- violation: Processes are killed or crash every few seconds, faster than an election can finish and a leader can commit an entry.
- at-risk: Availability fails because no leader stays up long enough to make progress; safety is not claimed to depend on this inequality.
- detectable: yes — the implementation sees continuous elections and almost no successful commits.

### grok-1:E21
- contract: Servers must draw election timeouts from a random distribution that is not synchronized across the cluster, and their clocks must advance at about the same rate.
- source: §9 "somehow synchronized), clocks must proceed at about the same rates, and servers and networks"
- stated: stated
- violation: Every server is configured with the same fixed timeout and the same clock, or one server's clock runs several times faster than the others and fires elections continuously.
- at-risk: Availability fails when split votes repeat or a fast clock keeps deposing the leader; the text says safety still holds when these assumptions fail.
- detectable: partly — endless split votes show up as election churn without identifying synchronized timers as the cause.

### grok-1:E22
- contract: A server that has not failed must be scheduled and must finish its durable RPCs promptly, or it must be treated as stopped.
- source: §9 "must be timely (or stopped). If these assumptions are not met for some period of time, the cluster"
- stated: stated
- violation: A stop-the-world garbage collection, a virtual-machine freeze, or a multi-second fsync stall pauses a follower or the leader for longer than an election timeout while the process is still considered up.
- at-risk: Availability fails for that interval because followers start elections or a leader cannot complete heartbeats; safety is maintained, as the same paragraph says.
- detectable: partly — the cluster observes an election and does not report the pause itself.

### grok-1:E23
- contract: If read-only queries use a leader lease instead of a confirming round of heartbeats, no server's clock, including pauses and time-sync steps, may advance faster than the drift bound used to shorten that lease.
- source: §6.4.1 "The lease approach assumes a bound on clock drift across servers (over a given time period, no"
- stated: stated
- violation: The leader's monotonic clock jumps forward, or a follower is paused longer than the drift bound, and the leader answers reads after followers have already elected someone else.
- at-risk: Linearizability of reads fails: the deposed leader returns a stale value with no later committed write. I am unsure only about deployments that never enable this extension; the basic heartbeat read path does not take this dependency.
- detectable: no — the stale reply is a normal successful query, which is why the text says the result can be arbitrarily stale.

### grok-1:E24
- contract: The state machine must be a deterministic function of the log: the same prefix must produce the same state and outputs on every server, so any local time, randomness, or host identity used in a command must already have been written into that log entry.
- source: §11.6 "the effects of client requests must not depend on each server’s current time."
- stated: stated
- violation: A command reads the local clock or iterates a hash map in randomized order at apply time, so two servers that apply the same entry compute different states or different replies.
- at-risk: The single-state-machine guarantee fails: clients observe different outputs for one committed index, which is State Machine Safety in the form the operator can see.
- detectable: partly — comparing state checksums across replicas would catch it, and Raft does not require that comparison, so the first sign is often two clients reading different values.

### grok-1:E25
- contract: Session expiry and any other housekeeping that decides which commands run must be a deterministic function of the log, not of a local timer.
- source: §6.3 "session expiry must be deterministic, just as normal state"
- stated: stated
- violation: One server drops a client's session from a local LRU or a local clock while another server keeps it, and only one of them re-executes a retried command.
- at-risk: State Machine Safety fails because the replicas no longer hold the same state after the same log prefix, which is the divergence the dissertation walks through for sessions.
- detectable: partly — divergent reads can expose it later; the expiry decision itself looks local and legal.

### grok-1:E26
- contract: The state machine must treat a repeated client serial number as already done: it returns the stored response and does not execute the command again.
- source: §6.3 "immediately without re-executing the request."
- stated: stated
- violation: The apply path runs the command again on a duplicate serial number, or it recomputes a new response instead of returning the saved one.
- at-risk: Linearizability fails because the operation is no longer exactly once; a lock or an increment applied twice is the case drawn in the dissertation.
- detectable: no — the second execution returns a normal success result.

### grok-1:E27
- contract: Every snapshot and every reload of the state machine must include the client-session table used to filter duplicates.
- source: §5.1 "serialize the information they keep for providing linearizability to clients (see Chapter 6)."
- stated: stated
- violation: A server snapshots the key-value data, discards the log, and restarts without the session map, then executes a retried command whose serial number was already applied.
- at-risk: Linearizability fails on that retry, and if replicas disagree about whether the session was reloaded, their states diverge.
- detectable: no — the replayed command looks like a new successful command.

### grok-1:E28
- contract: The image a server snapshots or ships to a follower must be a consistent state of exactly the committed prefix identified by that snapshot's last included index and term.
- source: §5 "the state machine must provide a consistent image of the"
- stated: stated
- violation: The snapshot mixes writes from later commands, omits an earlier committed command, or is labeled with an index it does not represent, and a slow follower installs it.
- at-risk: State Machine Safety fails on every server that installs that image, because later log entries are applied on top of the wrong state.
- detectable: partly — a follower that still has the overlapping log can fail the consistency check; a wrong value inside a prefix with the right endpoint index is not checked.

### grok-1:E29
- contract: After a restart, the state machine must load the snapshot for the discarded prefix before it applies any later log entry.
- source: §5 "discarded log entries from disk before it can apply any entries from the Raft log."
- stated: stated
- violation: The process applies the surviving log suffix onto an empty or older in-memory state because the snapshot load was skipped or ordered after the first log entry.
- at-risk: State Machine Safety fails on this server: the same log produces a different state than on servers that loaded the snapshot.
- detectable: partly — an external checksum of state would catch it; the server otherwise comes up and serves the wrong state.

### grok-1:E30
- contract: A disk-based state machine must make a prefix durable, and must be able to hand out a point-in-time consistent copy of it, before Raft is allowed to discard that prefix.
- source: §5.2 "Disk-based state machines must be able to provide a consistent snapshot of the disk for the pur-"
- stated: stated
- violation: Raft truncates the log once the state machine has the writes only in a volatile buffer, or the image sent to a follower is a mix of blocks from different prefixes because copy-on-write was not used.
- at-risk: A crash then loses committed user state even though the log prefix is gone, and a follower that installs the mixed image diverges, breaking State Machine Safety.
- detectable: partly — a crash that cannot rebuild the prefix is visible as missing data; a mixed image with a plausible index is not.

### grok-1:E31
- contract: The state machine must reflect a discarded prefix to durable storage in a form that can recover the current state, and it must tell Raft to drop that prefix only after that reflection is durable.
- source: §5 "the state machine reflects those entries to disk in a way that can recover the current system state."
- stated: stated
- violation: The state machine reports the prefix saved, Raft deletes the log entries, and the state machine's own durable copy is only a partial write.
- at-risk: The durability guarantee fails for every committed command in the discarded prefix, and a restart cannot rebuild them.
- detectable: partly — a checksum of the state machine's file catches some partial saves; a clean early acknowledgment does not.

### grok-1:E32
- contract: Each client must use a unique client identifier and must resubmit an unacknowledged command with the same serial number rather than a new one.
- source: §6.3 "each client is given a unique identifier, and clients assign unique"
- stated: stated
- violation: A client times out, generates a new serial number or a new client id, and submits the same logical command again.
- at-risk: Linearizability fails: the command runs twice, which is the duplicate lock and the double increment in the dissertation.
- detectable: no — both executions commit and return success.

### grok-1:E33
- contract: A client that is told its session is unknown must not register a new session and replay a command whose earlier outcome is uncertain.
- source: §6.3 "this would risk duplicate execution of"
- stated: stated
- violation: The session has expired, the client treats the error as "register again and retry the same write," and the write had already committed before the expiry.
- at-risk: Linearizability fails by a second execution of a command the client intended once; the dissertation adopts a crash of the client here because a retry is unsafe.
- detectable: no — the new session's command is a normal committed entry.

### grok-1:E34
- contract: A live client must send keep-alives often enough that the deterministic expiry rule does not drop its session during ordinary idle periods.
- source: §6.3 "Live clients issue keep-alive requests during periods of inactivity, which are also augmented with"
- stated: stated
- violation: A client stays idle longer than the session lifetime and then submits a new command on the expired session.
- at-risk: That client's availability fails if the server returns an error, and linearizability fails if the client then takes the new-session path in E33.
- detectable: yes — a server that follows the dissertation returns an error for the unknown session, which the client can see.

### grok-1:E35
- contract: The leader clock recorded into log entries for session expiry must move forward closely enough that live keep-alives still fall inside the expiry window and idle sessions do eventually expire.
- source: §6.3 "the leader augments each command that it appends to"
- stated: implicit
- violation: The leader's clock jumps forward by more than the session lifetime between two commands, and every live session is expired by the deterministic rule.
- at-risk: I am unsure this breaks State Machine Safety, because every server expires the same sessions from the log; it does break client availability, and it breaks exactly-once if those clients register again and replay, as in E33.
- detectable: partly — a bound check on the logged timestamp would see the jump, and nothing in the algorithm requires that check.

### grok-1:E36
- contract: A client that loses the leader must try another server instead of waiting indefinitely on the last leader it knew.
- source: §6.2 "simply retry with a random server. Insisting on being able to contact the last known leader"
- stated: stated
- violation: The client keeps reconnecting only to a leader that has crashed or been partitioned, while another server is leader and could serve the call.
- at-risk: The availability guarantee fails for that client even though a majority is healthy and has elected a leader.
- detectable: no — the cluster does not observe that this client refused to fail over; the client sees its own timeouts.

### grok-1:E37
- contract: If servers stamp replies with the applied log index so that one client never reads backward, the client must present the greatest index it has already seen.
- source: §6.4.1 "Clients would track the latest index corresponding to"
- stated: stated
- violation: The client drops the index it was given and accepts a later reply from a server that has applied only an older prefix.
- at-risk: The per-client monotonic-read guarantee fails. This is sequential consistency for one client, not the basic linearizable read path, and I am unsure it matters for deployments that do not enable the extension.
- detectable: no — the server still returns a successful older read when the client omits the index.

### grok-1:E38
- contract: Automatic removal of failed servers must not shrink the cluster below the fault tolerance the operator required.
- source: §4.4 "it can be dangerous for the cluster to automatically remove failed servers, as it could then be left"
- stated: stated
- violation: A controller removes every unresponsive server until one or two members remain, and the desired replica count is five.
- at-risk: The guarantee that a five-server cluster tolerates two failures no longer holds; the next failure of the smaller cluster loses availability or, if a majority of the remainder then loses disks, durability.
- detectable: partly — the implementation can compare the committed configuration to a configured target size, and a successful removal is not itself an error.

### grok-1:E39
- contract: A replacement that must keep tolerating a failure throughout has to add the new server before it removes the old one.
- source: §4.4 "adding one server and then removing the other allows the system to handle one server failure at all"
- stated: stated
- violation: In a three-server cluster the operator removes one server first, leaving a two-server cluster that needs both survivors for every commit.
- at-risk: Availability under one fault fails for the whole window; one more crash leaves no majority, so the cluster cannot commit.
- detectable: partly — the configuration size is visible in the log, and the remove call itself succeeds with no error.

### grok-1:E40
- contract: Cluster creation must start from one server whose log contains a singleton configuration, and every other process must start with an empty log and join by a membership change; a static configuration file, if used instead, must name the same member set on every server.
- source: §4.4 "This configuration lists only that one"
- stated: stated
- violation: Two processes are each bootstrapped as the sole member, or two servers' static files list overlapping sets that can each form a majority.
- at-risk: Election Safety fails: each singleton commits as its own leader, or the two static majorities elect two leaders for one term.
- detectable: partly — each side looks healthy alone; only a client that can see both histories, or a human comparing files, notices.

### grok-1:E41
- contract: The host must provide the extra memory concurrent snapshotting needs, and an out-of-memory condition must stop the server cleanly instead of continuing with a corrupted address space.
- source: §5.1.1 "Servers require additional memory for snapshotting concurrently, which should be planned for"
- stated: stated
- violation: Copy-on-write during a snapshot exhausts RAM and the process keeps running after the allocator or the kernel has corrupted its state.
- at-risk: If the process is simply killed, that is an ordinary stop and safety holds; if it keeps sending messages from corrupted memory, Election Safety and State Machine Safety fail as in E1.
- detectable: yes — allocation failure and the out-of-memory killer are visible to the operator.

### grok-1:E42
- contract: When the operating system supplies the snapshot by fork or by a copy-on-write disk device, that image must be a stable point-in-time copy, and the forked child must not itself vote or answer clients.
- source: §5.1.1 "to make a copy of the server’s entire address space. Then, the child process can write out the"
- stated: implicit
- violation: The child continues the parent's Raft threads and accepts RPCs, or the copy-on-write device returns a mix of blocks from before and after later writes.
- at-risk: A second voting child breaks Election Safety the same way as a cloned process; a mixed disk image breaks State Machine Safety on any follower that installs it.
- detectable: partly — a parent that expects the child to exit can notice that it did not; a mixed block device does not announce itself.

### grok-1:E43
- contract: Each state-machine command on an operational server must finish, so a committed entry can be applied and its result returned.
- source: §3.5 "entry to its state machine and returns the result of that execution to the client."
- stated: implicit
- violation: A command deadlocks or loops forever inside the state machine, and the apply thread never reaches the next committed index.
- at-risk: The guarantee that committed entries are eventually executed on the available state machines fails, and availability fails for every later command.
- detectable: yes — the leader's commit index moves and the applied index does not, which clients observe as timeouts.

### grok-2:E1
- contract: Each server fails by stopping, and a restart resumes from the stable storage that belonged to that same server, rather than by continuing to emit well-formed RPCs after its memory or decision logic has been corrupted.
- source: §8.1 "Servers fail by stopping and may later restart from stable storage on disk."
- stated: stated
- violation: A process with a wild pointer, a bit flip in a live term or log entry, or a compromised host keeps running and sends a vote or a log entry it did not decide.
- at-risk: Election Safety and State Machine Safety fail, because a single server can vote twice in one term or present two different commands at one index, and the majority argument no longer has an honest voter. Leader Completeness fails for the same reason.
- detectable: partly — peers can notice a term that goes backwards or two leaders in one term if both remain reachable, but one well-formed false vote is indistinguishable from a real vote.

### grok-2:E2
- contract: The network delivers each cluster or client RPC with the payload and the sender identity that were sent, or it delivers nothing; delay, loss, reordering, duplication, and partition are allowed.
- source: §2.1 "including network delays, partitions, and packet loss, duplication, and reordering."
- stated: implicit
- violation: A peer address is spoofed, a proxy swaps two responses, or a bit error changes a command or a term inside a checksum that still passes.
- at-risk: Log Matching and State Machine Safety fail if two servers accept different commands for one index and term; Election Safety fails if a forged vote completes a second majority. I am sure about altered log entries; I am less sure how often a swapped RPC response would be well-typed enough to commit the wrong follower.
- detectable: partly — an implementation can authenticate peers and checksum RPCs, which this text only suggests for snapshot files; without that, an altered RPC is accepted as genuine.

### grok-2:E3
- contract: A write of the current term, the vote, or a log entry that the server has treated as persisted stays readable after process crash and power loss, and it is persisted before the vote is cast or the entry counts toward commitment.
- source: §3.8 "Raft servers must persist enough information to stable storage to survive server restarts safely."
- stated: stated
- violation: A disk or filesystem acknowledges a flush while the bytes are only in a volatile write cache, or the deployment runs with write caching left on, and a power loss drops a vote or a committed entry.
- at-risk: Election Safety fails if a server votes, loses that vote, and votes for someone else in the same term. Leader Completeness and the durability of committed entries fail if a majority counted copies that did not survive.
- detectable: no — after the device acknowledges the flush, the server cannot tell that a later power loss would drop the bytes.

### grok-2:E4
- contract: Stable storage returns the bytes that were acknowledged, or a read error, and a partially written tail is distinguishable from a complete term, vote, or log record.
- source: §5.1.3 "also be beneficial to compress the stream and apply a checksum to it."
- stated: implicit
- violation: A torn sector or a silent misread is parsed as a different complete log entry, term, or vote.
- at-risk: Log Matching fails because one index and term now denote two commands; Election Safety fails if the stored vote flips. The text only says a checksum is beneficial, so I am treating integrity as an obligation the checksum is there to police.
- detectable: partly — a record checksum catches many torn and flipped reads; with no checksum, a plausible wrong record looks stored.

### grok-2:E5
- contract: Publishing a snapshot is crash-atomic: after the snapshot has been flushed and its name installed, a restart loads that complete snapshot or the previous complete one.
- source: §5.1.3 "flushed to disk; this ensures that no server loads a partially written snapshot on startup."
- stated: stated
- violation: A crash or a filesystem that reorders the directory update ahead of the data exposes a renamed snapshot whose body is short or mixed.
- at-risk: State Machine Safety fails on any follower that installs the partial image and then applies later entries on a different base. I am sure about the divergence; how far the logs can then drift depends on whether the last-included index still matches.
- detectable: partly — a checksum or a trailer can make a short file fail to load; a partial file that still parses does not.

### grok-2:E6
- contract: The snapshot body and the Raft restart metadata for it (last included index, last included term, and the latest configuration at that index) are durable before the corresponding log prefix can disappear.
- source: §5.1 "Once the state machine completes writing a snapshot, the log can be truncated."
- stated: implicit
- violation: The log prefix is discarded, then power fails before the snapshot and its index, term, and configuration reach stable storage, or those writes are reordered past the discard.
- at-risk: Leader Completeness and durability fail for the discarded prefix, and a missing configuration can make the restarted server use the wrong majority. State Machine Safety fails if the server later applies a new log on an empty or older base.
- detectable: partly — a restart can notice that the log no longer contains the prefix and the snapshot file is missing or short; if both the prefix and a plausible older snapshot are gone, the server just looks empty.

### grok-2:E7
- contract: A server whose persisted term, vote, or log has been lost or replaced by an older image does not rejoin under its previous identity.
- source: §3.8 "If a server loses any of its persistent state, it cannot safely rejoin the cluster with its prior identity."
- stated: stated
- violation: An operator or a hypervisor restores one member's disk or VM snapshot from last week, or a volume comes back empty, and the process starts again with the same server id.
- at-risk: Election Safety fails because the restored server can vote again in a term it had already voted in. Leader Completeness fails because a committed entry that lived only on that server's newer image is gone, so a later leader can lack it.
- detectable: partly — a peer can refuse a server whose term or log suddenly shrank if it remembers that peer, but a stale yet well-formed image looks like an ordinary restart.

### grok-2:E8
- contract: At most one live process runs a given server identity and reads or writes its stable store.
- source: §3.8 "this is necessary to prevent the server from"
- stated: implicit
- violation: A data directory is copied and started on a second host, or two processes are pointed at one member directory, and both cast votes or append entries for that identity.
- at-risk: Election Safety fails because the identity votes twice in one term. Log Matching fails if the two processes diverge and both convince followers they are that member.
- detectable: partly — a lock on the data directory or a bound port catches two processes on one machine; two hosts with two copies do not meet until their terms collide.

### grok-2:E9
- contract: The stable stores of a majority of the current configuration survive, so a committed entry remains on at least one surviving voter.
- source: §3.8 "If a majority of the cluster loses its persistent state, however,"
- stated: stated
- violation: A shared array, a site, or a bad restore wipes the disks of a majority of voters at once.
- at-risk: The durability of committed entries fails, and Leader Completeness fails for any later leader elected from the survivors. The text also says membership changes can no longer make progress.
- detectable: yes — the remaining servers can see that they cannot assemble a majority that still holds the log, though they cannot by themselves name every committed entry.

### grok-2:E10
- contract: Each configured voter is a distinct process, and each configured address reaches that process alone.
- source: §4 "there would be an extra vote"
- stated: implicit
- violation: The membership lists one machine twice under two names, a load balancer sits in the peer mesh, or DHCP gives a member's address to a different host.
- at-risk: Election Safety fails because majorities need not intersect in a real server, so two leaders can be elected for one term. I take the text's "extra vote" example, written for a returned server, to be the same intersection failure.
- detectable: partly — the configuration can be checked for duplicate ids, but two names that route to one process still look distinct.

### grok-2:E11
- contract: Voting members fail independently at the granularity the operator counts, so one fault the deployment claims to survive does not stop or erase a majority of voters.
- source: §2.1 "can tolerate the failure of any two servers."
- stated: implicit
- violation: Three of five voters share one virtual machine, one rack power feed, or one disk array.
- at-risk: The availability claim fails because the cluster cannot tolerate the two server failures §2.1 names. Durability fails too if that fault erases a majority of stable stores. Safety among servers that have merely stopped still holds. I am unsure whether the text means only process independence or also site independence; the counting treats a server as the unit.
- detectable: no — Raft does not know that several configured servers share a power supply or a disk.

### grok-2:E12
- contract: The integers used for terms and log indexes do not wrap for the life of the cluster, and a server's durable term only moves forward.
- source: §3.3 "current term number, which increases monotonically over time."
- stated: implicit
- violation: A 32-bit term wraps, or a restarted process loads a truncated counter and treats a newer peer as stale.
- at-risk: Election Safety and Leader Completeness depend on terms increasing and on a larger term superseding a smaller one. After a wrap, a new leader can look older than a deposed one, so the voting and commit rules apply to the wrong order. I have not found a place where the text discusses width, so this is my reading of "monotonically".
- detectable: partly — the process can refuse an increment that would overflow; a wrap that has already been stored looks like a small legitimate term.

### grok-2:E13
- contract: The election timeout is about an order of magnitude larger than the time to send a round of RPCs and to persist the term, vote, and log entries those RPCs require.
- source: §3.9 "broadcast time should be an order of magnitude less than the election timeout"
- stated: stated
- violation: The timeout stays at a few tens of milliseconds while a fsync or a loaded disk takes longer, so followers start elections while a leader is still alive.
- at-risk: Availability fails: the cluster does not keep a steady leader, so it cannot commit. The text says safety does not depend on this timing, and I agree for the core algorithm, with the lease exception in E18.
- detectable: partly — a server can measure RPC and disk latency and see followers campaigning anyway; a short spike looks like ordinary packet loss.

### grok-2:E14
- contract: The election timeout is a few orders of magnitude smaller than the mean time between failures of a server, so a leader stays up long enough to be elected and to commit.
- source: §3.9 "election timeout should be a few orders of magnitude less than MTBF"
- stated: stated
- violation: A process is crash-looped, killed, or rescheduled so often that every candidate dies before a majority of votes returns.
- at-risk: Availability fails because no steady leader is elected, which is the case §3.9 describes. Safety of entries already committed is not by itself broken.
- detectable: partly — repeated restarts are in the logs, but the implementation does not know the operator's MTBF target.

### grok-2:E15
- contract: Each server draws its election timeout independently from a range wide enough, relative to network delay, that the servers' timers are not synchronized.
- source: §9 "servers must choose timeouts from a random distribution (they are not"
- stated: stated
- violation: Every server uses the same constant timeout, or cloned images share one RNG seed and one clock, so several candidates always start together.
- at-risk: Availability fails because split votes repeat and no leader is elected for as long as the draws stay locked. §9 says safety is still maintained, and the majority vote rule supports that.
- detectable: partly — a run of split elections is visible, but servers do not see one another's timeout draws.

### grok-2:E16
- contract: Clocks used for election timers advance at about the same rate, without jumps large compared with the election timeout.
- source: §9 "clocks must proceed at about the same rates"
- stated: stated
- violation: NTP steps a clock, a VM is migrated, or a garbage collector stops a process for longer than the election timeout.
- at-risk: Availability fails for that period: followers start elections or fail to start them while a leader is still valid. §9 and §3.10 say safety holds even when clocks run at arbitrary speeds, apart from the lease in E18.
- detectable: partly — a server that samples a monotonic clock against wall time can log its own jump; it cannot see that a peer's clock ran fast.

### grok-2:E17
- contract: A server the operator counts as up answers within about a broadcast time, and a server that cannot do so is stopped rather than paused and later resumed.
- source: §9 "must be timely (or stopped)."
- stated: stated
- violation: A virtual machine is suspended, or a scheduler freezes the process, and later the server resumes and campaigns or holds a client.
- at-risk: Availability fails while the cluster cannot elect or keep a leader, which is the bound §9 states. Safety of the core algorithm remains, because a resumed server still has its old term and log.
- detectable: partly — RPC timeouts expose a slow peer; a pause shorter than the failure detector looks like ordinary delay.

### grok-2:E18
- contract: If read-only queries use the clock lease, no server's clock runs ahead of another's by more than the drift bound used to shorten that lease.
- source: §6.4.1 "The lease approach assumes a bound on clock drift across servers"
- stated: stated
- violation: A follower's clock jumps forward, its election timer fires inside the leader's lease, a new leader commits entries, and the old leader still answers reads.
- at-risk: Linearizability of those reads fails: the client can be given arbitrarily stale state, which is the failure §6.4.1 names. State Machine Safety for entries that were applied is a separate question; the stale read may simply omit newer committed entries.
- detectable: no — the stale reply is a successful response, and the old leader has no signal that a follower's clock already started an election.

### grok-2:E19
- contract: If servers use the monotonic-read extension, each client tells the server the highest log index it has already observed.
- source: §6.4.1 "Clients would track the latest index corresponding to"
- stated: stated
- violation: A client reads at index n, then contacts another server and omits n, so that server answers from an older applied prefix.
- at-risk: The sequential-consistency fallback in §6.4.1 fails for that client. It is the fallback for when the lease clocks misbehave, so losing it brings back a stale read. I am unsure how often operators rely on this extension; the text offers it and LogCabin does not implement the lease.
- detectable: no — a missing index is indistinguishable from a client that has never read.

### grok-2:E20
- contract: The state machine is a deterministic function of the committed log: local time, randomness, and host identity affect results only when a leader has already written those inputs into the log.
- source: §11.6 "the effects of client requests must not depend on each server’s current time."
- stated: stated
- violation: Apply reads the local clock, iterates a hash map in randomized order, or calls an unreplicated service, so two replicas compute different states or outputs.
- at-risk: State Machine Safety fails in effect: the same log index yields different client-visible results on different servers, so the cluster no longer behaves as one state machine. The log entries themselves can still match.
- detectable: partly — replicas can checksum state and compare, which Raft does not require; otherwise the outputs simply disagree.

### grok-2:E21
- contract: Expiry of client sessions is a deterministic function of the replicated log, using the same inputs on every server.
- source: §6.3 "session expiry must be deterministic, just as normal state"
- stated: stated
- violation: One server drops a client's session from its own wall clock and then executes a duplicate command, while another server still suppresses that duplicate.
- at-risk: State Machine Safety fails because the replicas no longer hold the same state, which is the divergence §6.3 spells out. Linearizability fails with it, because the command was applied twice on one replica and once on another.
- detectable: partly — comparing session tables across replicas would show it; a single server sees only its own expiry.

### grok-2:E22
- contract: The only externally visible effect of applying a command is the deterministic output returned to the client through Raft.
- source: §2.1 "the servers appear to form a single, highly reliable state"
- stated: implicit
- violation: Apply sends mail, charges a card, or deletes an object in another system, so every replica performs that action.
- at-risk: The guarantee that the cluster appears as one state machine fails for that action: the client observes one response and the outside world observes one action per replica. I am reading this from the architecture in §2.1; the text does not discuss side effects by name.
- detectable: no — Raft sees the command and the returned output, not an action the state machine took elsewhere.

### grok-2:E23
- contract: After a restart, a volatile state machine is rebuilt by loading the latest snapshot and reapplying the following log entries, and its old address space is not resumed in place of that rebuild.
- source: §3.8 "A volatile state machine must be recovered"
- stated: stated
- violation: A hibernated process or a memory checkpoint is resumed with a half-updated state machine while the log on disk has moved on or was replayed differently.
- at-risk: State Machine Safety fails because that server's applied state is no longer the state of the committed prefix. A normal process restart does not do this; a checkpoint restore does.
- detectable: partly — rebuilding from the log and comparing a checksum to the snapshot catches a mismatch; a resumed image has no marker that replay was skipped.

### grok-2:E24
- contract: For a persistent state machine, the durable image and the durable last-applied index describe the same prefix across a crash.
- source: §3.8 "its last applied index must also be persistent."
- stated: stated
- violation: A crash falls between applying a command to the on-disk database and recording lastApplied, so restart either skips the command or runs an increment a second time.
- at-risk: State Machine Safety fails because this server's state diverges from peers that applied the prefix once. The text's reason for persisting the index is to avoid reapplying, which is this failure.
- detectable: partly — a checksum that ties lastApplied to the image catches the mismatch; without it, a replayed command looks like a normal apply.

### grok-2:E25
- contract: The state machine can produce and later reload a consistent image of committed state at a single log index, including the session table used for linearizability.
- source: §5.1 "serialize the information they keep for providing linearizability to clients (see Chapter 6)."
- stated: stated
- violation: fork copies the address space while other threads are mid-update, or the snapshot omits client sessions, and a follower or a restarted server loads that image.
- at-risk: State Machine Safety fails if later entries apply on a torn base. Linearizability fails if a session was dropped and a duplicate command runs again after the snapshot. §5 also requires the image to be consistent; this entry includes that.
- detectable: partly — a structural checksum can reject some torn images; a parseable image that simply lacks sessions still loads.

### grok-2:E26
- contract: Applying a committed command returns in finite time and does not wait on a further Raft commit.
- source: §3.5 "Raft guarantees that committed entries are durable and will eventually be exe-"
- stated: implicit
- violation: The state machine blocks on a lock the consensus thread holds, or calls out to a service that never answers, so the committed prefix stops being applied.
- at-risk: The guarantee that committed entries are eventually executed on available servers fails. Clients can also stop receiving results for commands that are already durable. I am unsure only about commands that are allowed to run for a very long time but do finish.
- detectable: yes — the server can bound apply and surface a stall when the command does not return.

### grok-2:E27
- contract: The host provides enough durable capacity for the compacted state and the uncompacted log tail, and a write that does not fit returns an error instead of a short record treated as complete.
- source: §5 "servers will either run out of space, or they will take too"
- stated: stated
- violation: The log is left uncompacted until the disk fills, or a short write at ENOSPC is acknowledged as a full log entry.
- at-risk: Availability fails once servers cannot append or cannot restart in time, which is the failure §5 names. A short write acknowledged as complete is also an E4 integrity failure and can break Log Matching.
- detectable: partly — a normal ENOSPC is returned to the server; a short write is detectable only if lengths are checked.

### grok-2:E28
- contract: The host provides the extra memory concurrent snapshotting needs, or it lets the server stop taking new entries until the snapshot finishes.
- source: §5.1.1 "Servers require additional memory for snapshotting concurrently, which should be planned for"
- stated: stated
- violation: Copy-on-write snapshotting exhausts memory and the kernel kills the process, or the server keeps accepting entries and never finishes the snapshot.
- at-risk: Availability of that server fails, and if enough servers snapshot at once the cluster can lose the ability to commit. A kill during a non-atomic publish is also an E5 risk. The text already tells the server to stop accepting entries rather than die.
- detectable: yes — allocation failure is visible to the process, which can shed load as §5.1.1 describes; an external kill looks like a crash.

### grok-2:E29
- contract: Whenever the deployment expects the cluster to be available, some majority of the configuration is up and can exchange messages with each other and with clients.
- source: §2.1 "any majority of the servers are operational"
- stated: stated
- violation: A partition or a power cut leaves every majority either down or unable to talk, while clients can still reach only a minority.
- at-risk: Availability fails, including during the outage's reads and writes. The text's safety claim is meant to survive this partition, so Election Safety and State Machine Safety should hold; a leader on the minority must stop committing.
- detectable: yes — a leader that cannot hear a majority steps down, and clients see the outage.

### grok-2:E30
- contract: A server that the operator counts as available can, in finite time, receive the leader's retried RPCs and therefore apply every committed entry.
- source: §3.5 "Raft guarantees that committed entries are durable and will eventually be exe-"
- stated: implicit
- violation: A firewall or a one-way link drops every AppendEntries to a server that otherwise looks up, forever.
- at-risk: The "eventually executed by all of the available state machines" guarantee fails for that server. Entries committed on the majority stay committed. The formal model in §8.1 allows arbitrary delay, so this obligation is only as strong as the informal "eventually" claim; I am unsure the text means a hard bound.
- detectable: partly — the leader sees failed RPCs to that follower, while a follower that still answers heartbeats can hide a stalled apply.

### grok-2:E31
- contract: The mechanism clients use to find the cluster returns every current member, is updated to add a server before that server joins and to remove a server only after it has left, and uses broadcast or multicast only on a network that delivers them.
- source: §6.1 "clients should always be able to find all of the cluster"
- stated: stated
- violation: DNS still lists only the servers that were just removed, or it lists a different cluster, or clients broadcast on a network that drops broadcasts.
- at-risk: Availability fails because clients cannot reach a leader. Including a few extra servers is harmless, as the text says; listing the wrong cluster can make a client treat another state machine's result as this one's. I am unsure the text counts that last case as more than a directory mistake.
- detectable: partly — a server that is shown both the directory and the configuration can compare them; Raft as specified does not look up DNS.

### grok-2:E32
- contract: If the cluster uses a static configuration, every server's file names the same set of members.
- source: §4.4 "each server simply has a static file listing the configuration."
- stated: implicit
- violation: One server is booted with a hand-edited file that names a different trio than its peers.
- at-risk: Election Safety fails if the two files allow two majorities that do not intersect, which is the split §4 illustrates for a configuration change. Availability fails if each server waits for a majority the others do not recognize.
- detectable: partly — servers can exchange a hash of the file once they can talk; until then each side looks healthy to itself.

### grok-2:E33
- contract: A new cluster starts from a single configuration that one initial server already has committed, and every other process starts with an empty log and joins later.
- source: §4.4 "initialized with a configuration entry as the first entry in its log."
- stated: stated
- violation: Two servers are each initialized as a one-server cluster, both commit client commands, and both are later pointed at the same clients.
- at-risk: State Machine Safety and linearizability fail across the pair the operator thinks is one cluster: the same client command can be decided differently on each side. Each side separately satisfies Raft. The text presents this bootstrap as a recommendation because the static file is error-prone.
- detectable: partly — the two singletons never meet, so neither server notices; an operator who looks at both can.

### grok-2:E34
- contract: If a new server replaces a member by taking over its network address, the replaced server never runs again.
- source: §4 "the replaced server will never come back up"
- stated: stated
- violation: The old host is powered back on, still configured as a voter, while the new host has its address, and both answer RequestVote.
- at-risk: Election Safety fails because there is an extra vote, which is the example §4 gives, so two leaders can be chosen for one term. Leader Completeness can fail with them.
- detectable: partly — hearing two hosts claim one address is suspicious, but an extra RequestVote looks like any other vote.

### grok-2:E35
- contract: Automation and operators do not remove voting members in a way that leaves fewer durable copies than the deployment's fault-tolerance target, and a replacement is added before the member it replaces is removed.
- source: §4.4 "it can be dangerous for the cluster to automatically remove failed servers"
- stated: stated
- violation: A controller deletes a dead voter as soon as it stops answering, or it removes the old server before the new one's log has caught up, leaving two voters where three were required.
- at-risk: The durability and availability claims fail: one more fault can wipe or isolate the remaining majority. Safety of entries still stored on a majority of whoever is left holds. §4.4 says adding before removing is what keeps a one-failure margin during the swap.
- detectable: partly — the cluster can compare its voter count with a configured target if one was set; Raft does not know the intended replication factor by itself.

### grok-2:E36
- contract: During a membership change, a majority of the old configuration stays available at least until the new configuration is committed, and a majority of the new configuration is available.
- source: §4.2.4 "majority of the old configuration is available (at least until Cnew is committed) and that a majority"
- stated: stated
- violation: The operator starts adding a server that is down, or the only servers that hold the old configuration fail before the new entry commits.
- at-risk: Availability during the change fails: §4.2.4's argument that a leader can be elected and can finish the change no longer applies. Safety of the single-server overlap still holds if the servers that remain follow the log rules. The text says it assumes this "among other things," and it does not list the other things.
- detectable: yes — the leader cannot commit the new configuration if the required majority does not answer, and §4.2.1 says to abort a server that never catches up.

### grok-2:E37
- contract: Each client uses a distinct identifier returned by a completed registration, and puts that identifier on every later command.
- source: §6.3 "each client is given a unique identifier"
- stated: stated
- violation: Two clients share an identifier, or a client invents one, or a client continues with an identifier whose session the cluster has already dropped.
- at-risk: Linearizability fails. A shared identifier makes one client's command suppress the other's as a duplicate, or lets one client observe the other's result. An unknown session is rejected rather than executed, which preserves exactly-once only if the client stops; §6.3 says LogCabin crashes the client there.
- detectable: partly — an unknown identifier is rejected after the session is gone; two clients that share a live identifier are indistinguishable.

### grok-2:E38
- contract: Each logical command carries a client-chosen serial number that is unique among that client's in-flight commands, and every retransmission or network duplicate repeats that same serial number.
- source: §6.3 "serial numbers to every command."
- stated: stated
- violation: A client or a proxy times out, allocates a new serial number, and sends the same operation again, or a duplicate arrives with a rewritten serial number.
- at-risk: Linearizability fails because the command is applied twice, which is the duplicate-lock and double-increment failure §6.3 describes. The core log properties can all still hold.
- detectable: no — a fresh serial number is defined to be a new command, so the server has no signal that the client meant a retry.

### grok-2:E39
- contract: A client that has not received a response does not submit that same operation as a new command, including after the cluster reports that the session is gone.
- source: §6.3 "this would risk duplicate execution of"
- stated: stated
- violation: The client gets a session-expired error or a timeout, opens a new session, and resubmits the unacknowledged operation.
- at-risk: Linearizability fails for that operation: it may already have been committed under the old session and is then committed again. §6.3 prefers an error over allocating a fresh session precisely to avoid this.
- detectable: partly — the session-expired error tells the client to stop; once the client uses a new session, the server treats the command as new.

### grok-2:E40
- contract: A client that still has commands in flight or that expects its session to remain sends keep-alives so the agreed expiry rule does not drop the session.
- source: §6.3 "Live clients issue keep-alive requests during periods of inactivity"
- stated: stated
- violation: A quiet client sends nothing until the logged idle time passes the session limit, then sends another command.
- at-risk: The exactly-once session is gone. The next command returns an error if the server follows §6.3, so linearizability of a command already applied is preserved only if the client does not reissue it (E39). Availability of that client's further commands fails.
- detectable: yes — the session expires and the next command returns an error rather than running.

### grok-2:E41
- contract: The leader clock that is written into the log as the time base for session expiry does not jump forward far enough to expire sessions that still have live clients.
- source: §6.3 "the leader augments each command that it appends to"
- stated: implicit
- violation: NTP or a virtual-machine migration steps the leader's clock past the idle bound, the new timestamp is committed, and every active session expires at once.
- at-risk: Those clients lose the exactly-once session. If they stop, an unacknowledged command may have been applied with no response, which linearizability allows for an incomplete operation. If they reissue under E39's violation, the command runs twice. I am unsure the text treats the clock as more than an agreed input; the hazard is how far that input jumps.
- detectable: partly — a huge gap between logged timestamps is visible in the log; a moderate step looks like time passing.

### grok-2:E42
- contract: Clients tolerate a period of unavailability on the order of an election timeout without treating the cluster as failed.
- source: §4.2.1 "clients must already be able to tolerate"
- stated: stated
- violation: A client library uses a deadline shorter than the election timeout and returns a hard failure while a new leader is still being chosen.
- at-risk: The availability the client observes fails during ordinary leader changes, which §4.2.1 says clients must already absorb. Safety of committed entries is unchanged. A client that then retries under a new serial number also hits E38.
- detectable: no — the server cannot see the client's deadline; it is still finishing the election.

### grok-2:E43
- contract: A client that loses the server it was using retries some other member instead of waiting on that one server.
- source: §6.2 "simply retry with a random server."
- stated: stated
- violation: The client keeps dialing a leader that has crashed, or a server that is partitioned from the majority, until its own budget is spent.
- at-risk: Availability for that client fails even though a majority is up and has elected a leader. §6.2 describes this as unnecessary delay. Safety is unchanged.
- detectable: partly — the server can return the leader's address on a redirect, but it cannot tell whether the client followed it.

