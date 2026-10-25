### E1
- contract: Each server fails by stopping, and a restart resumes from the stable storage that belonged to that same server, rather than by continuing to emit well-formed RPCs after its memory or decision logic has been corrupted.
- source: §8.1 "Servers fail by stopping and may later restart from stable storage on disk."
- stated: stated
- violation: A process with a wild pointer, a bit flip in a live term or log entry, or a compromised host keeps running and sends a vote or a log entry it did not decide.
- at-risk: Election Safety and State Machine Safety fail, because a single server can vote twice in one term or present two different commands at one index, and the majority argument no longer has an honest voter. Leader Completeness fails for the same reason.
- detectable: partly — peers can notice a term that goes backwards or two leaders in one term if both remain reachable, but one well-formed false vote is indistinguishable from a real vote.
- silent: 1 — a host that keeps sending plausible RPCs after a fault is rare on ECC machines, and most faults stop the process.
- basis: text

### E2
- contract: The network delivers each cluster or client RPC with the payload and the sender identity that were sent, or it delivers nothing; delay, loss, reordering, duplication, and partition are allowed.
- source: §2.1 "including network delays, partitions, and packet loss, duplication, and reordering."
- stated: implicit
- violation: A peer address is spoofed, a proxy swaps two responses, or a bit error changes a command or a term inside a checksum that still passes.
- at-risk: Log Matching and State Machine Safety fail if two servers accept different commands for one index and term; Election Safety fails if a forged vote completes a second majority. I am sure about altered log entries; I am less sure how often a swapped RPC response would be well-typed enough to commit the wrong follower.
- detectable: partly — an implementation can authenticate peers and checksum RPCs, which this text only suggests for snapshot files; without that, an altered RPC is accepted as genuine.
- silent: 1 — forged Raft RPCs and checksum-escaping corruption are rare on the closed networks these clusters usually use.
- basis: text

### E3
- contract: A write of the current term, the vote, or a log entry that the server has treated as persisted stays readable after process crash and power loss, and it is persisted before the vote is cast or the entry counts toward commitment.
- source: §3.8 "Raft servers must persist enough information to stable storage to survive server restarts safely."
- stated: stated
- violation: A disk or filesystem acknowledges a flush while the bytes are only in a volatile write cache, or the deployment runs with write caching left on, and a power loss drops a vote or a committed entry.
- at-risk: Election Safety fails if a server votes, loses that vote, and votes for someone else in the same term. Leader Completeness and the durability of committed entries fail if a majority counted copies that did not survive.
- detectable: no — after the device acknowledges the flush, the server cannot tell that a later power loss would drop the bytes.
- silent: 3 — volatile write caches and filesystems that acknowledge a flush early are a common configuration, and nothing signals it until power is actually lost.
- basis: text

### E4
- contract: Stable storage returns the bytes that were acknowledged, or a read error, and a partially written tail is distinguishable from a complete term, vote, or log record.
- source: §5.1.3 "also be beneficial to compress the stream and apply a checksum to it."
- stated: implicit
- violation: A torn sector or a silent misread is parsed as a different complete log entry, term, or vote.
- at-risk: Log Matching fails because one index and term now denote two commands; Election Safety fails if the stored vote flips. The text only says a checksum is beneficial, so I am treating integrity as an obligation the checksum is there to police.
- detectable: partly — a record checksum catches many torn and flipped reads; with no checksum, a plausible wrong record looks stored.
- silent: 2 — on one cluster over a year this is uncommon, and without a checksum it raises no error.
- basis: general systems experience

### E5
- contract: Publishing a snapshot is crash-atomic: after the snapshot has been flushed and its name installed, a restart loads that complete snapshot or the previous complete one.
- source: §5.1.3 "flushed to disk; this ensures that no server loads a partially written snapshot on startup."
- stated: stated
- violation: A crash or a filesystem that reorders the directory update ahead of the data exposes a renamed snapshot whose body is short or mixed.
- at-risk: State Machine Safety fails on any follower that installs the partial image and then applies later entries on a different base. I am sure about the divergence; how far the logs can then drift depends on whether the last-included index still matches.
- detectable: partly — a checksum or a trailer can make a short file fail to load; a partial file that still parses does not.
- silent: 2 — the crash has to land in the publish window, which is uncommon, and a parseable partial file does not announce itself.
- basis: text

### E6
- contract: The snapshot body and the Raft restart metadata for it (last included index, last included term, and the latest configuration at that index) are durable before the corresponding log prefix can disappear.
- source: §5.1 "Once the state machine completes writing a snapshot, the log can be truncated."
- stated: implicit
- violation: The log prefix is discarded, then power fails before the snapshot and its index, term, and configuration reach stable storage, or those writes are reordered past the discard.
- at-risk: Leader Completeness and durability fail for the discarded prefix, and a missing configuration can make the restarted server use the wrong majority. State Machine Safety fails if the server later applies a new log on an empty or older base.
- detectable: partly — a restart can notice that the log no longer contains the prefix and the snapshot file is missing or short; if both the prefix and a plausible older snapshot are gone, the server just looks empty.
- silent: 2 — it requires a crash in that window, and the usual symptom is a server that restarts with a hole rather than an explicit ordering alarm.
- basis: text

### E7
- contract: A server whose persisted term, vote, or log has been lost or replaced by an older image does not rejoin under its previous identity.
- source: §3.8 "If a server loses any of its persistent state, it cannot safely rejoin the cluster with its prior identity."
- stated: stated
- violation: An operator or a hypervisor restores one member's disk or VM snapshot from last week, or a volume comes back empty, and the process starts again with the same server id.
- at-risk: Election Safety fails because the restored server can vote again in a term it had already voted in. Leader Completeness fails because a committed entry that lived only on that server's newer image is gone, so a later leader can lack it.
- detectable: partly — a peer can refuse a server whose term or log suddenly shrank if it remembers that peer, but a stale yet well-formed image looks like an ordinary restart.
- silent: 2 — many clusters never restore a single member in a year; when they do, the node often comes up looking healthy.
- basis: text

### E8
- contract: At most one live process runs a given server identity and reads or writes its stable store.
- source: §3.8 "this is necessary to prevent the server from"
- stated: implicit
- violation: A data directory is copied and started on a second host, or two processes are pointed at one member directory, and both cast votes or append entries for that identity.
- at-risk: Election Safety fails because the identity votes twice in one term. Log Matching fails if the two processes diverge and both convince followers they are that member.
- detectable: partly — a lock on the data directory or a bound port catches two processes on one machine; two hosts with two copies do not meet until their terms collide.
- silent: 1 — a second local process usually dies on the port or the lock, so the quiet case is uncommon.
- basis: general systems experience

### E9
- contract: The stable stores of a majority of the current configuration survive, so a committed entry remains on at least one surviving voter.
- source: §3.8 "If a majority of the cluster loses its persistent state, however,"
- stated: stated
- violation: A shared array, a site, or a bad restore wipes the disks of a majority of voters at once.
- at-risk: The durability of committed entries fails, and Leader Completeness fails for any later leader elected from the survivors. The text also says membership changes can no longer make progress.
- detectable: yes — the remaining servers can see that they cannot assemble a majority that still holds the log, though they cannot by themselves name every committed entry.
- silent: 1 — losing a majority of stores in one year is rare for a single deployment, and the outage is obvious.
- basis: text

### E10
- contract: Each configured voter is a distinct process, and each configured address reaches that process alone.
- source: §4 "there would be an extra vote"
- stated: implicit
- violation: The membership lists one machine twice under two names, a load balancer sits in the peer mesh, or DHCP gives a member's address to a different host.
- at-risk: Election Safety fails because majorities need not intersect in a real server, so two leaders can be elected for one term. I take the text's "extra vote" example, written for a returned server, to be the same intersection failure.
- detectable: partly — the configuration can be checked for duplicate ids, but two names that route to one process still look distinct.
- silent: 2 — this is an occasional misconfiguration and it can sit quiet until an election.
- basis: general systems experience

### E11
- contract: Voting members fail independently at the granularity the operator counts, so one fault the deployment claims to survive does not stop or erase a majority of voters.
- source: §2.1 "can tolerate the failure of any two servers."
- stated: implicit
- violation: Three of five voters share one virtual machine, one rack power feed, or one disk array.
- at-risk: The availability claim fails because the cluster cannot tolerate the two server failures §2.1 names. Durability fails too if that fault erases a majority of stable stores. Safety among servers that have merely stopped still holds. I am unsure whether the text means only process independence or also site independence; the counting treats a server as the unit.
- detectable: no — Raft does not know that several configured servers share a power supply or a disk.
- silent: 3 — putting a majority in one failure domain is a common layout and raises no error until that domain fails.
- basis: general systems experience

### E12
- contract: The integers used for terms and log indexes do not wrap for the life of the cluster, and a server's durable term only moves forward.
- source: §3.3 "current term number, which increases monotonically over time."
- stated: implicit
- violation: A 32-bit term wraps, or a restarted process loads a truncated counter and treats a newer peer as stale.
- at-risk: Election Safety and Leader Completeness depend on terms increasing and on a larger term superseding a smaller one. After a wrap, a new leader can look older than a deposed one, so the voting and commit rules apply to the wrong order. I have not found a place where the text discusses width, so this is my reading of "monotonically".
- detectable: partly — the process can refuse an increment that would overflow; a wrap that has already been stored looks like a small legitimate term.
- silent: 1 — a 64-bit term or index will not wrap in a year of elections.
- basis: general systems experience

### E13
- contract: The election timeout is about an order of magnitude larger than the time to send a round of RPCs and to persist the term, vote, and log entries those RPCs require.
- source: §3.9 "broadcast time should be an order of magnitude less than the election timeout"
- stated: stated
- violation: The timeout stays at a few tens of milliseconds while a fsync or a loaded disk takes longer, so followers start elections while a leader is still alive.
- at-risk: Availability fails: the cluster does not keep a steady leader, so it cannot commit. The text says safety does not depend on this timing, and I agree for the core algorithm, with the lease exception in E18.
- detectable: partly — a server can measure RPC and disk latency and see followers campaigning anyway; a short spike looks like ordinary packet loss.
- silent: 3 — timeouts left below real disk latency are a familiar production setting, and the resulting blips are often logged only as ordinary leader changes.
- basis: text

### E14
- contract: The election timeout is a few orders of magnitude smaller than the mean time between failures of a server, so a leader stays up long enough to be elected and to commit.
- source: §3.9 "election timeout should be a few orders of magnitude less than MTBF"
- stated: stated
- violation: A process is crash-looped, killed, or rescheduled so often that every candidate dies before a majority of votes returns.
- at-risk: Availability fails because no steady leader is elected, which is the case §3.9 describes. Safety of entries already committed is not by itself broken.
- detectable: partly — repeated restarts are in the logs, but the implementation does not know the operator's MTBF target.
- silent: 2 — a crash loop is unusual when the process otherwise stays up for weeks, and it usually leaves a restart record.
- basis: text

### E15
- contract: Each server draws its election timeout independently from a range wide enough, relative to network delay, that the servers' timers are not synchronized.
- source: §9 "servers must choose timeouts from a random distribution (they are not"
- stated: stated
- violation: Every server uses the same constant timeout, or cloned images share one RNG seed and one clock, so several candidates always start together.
- at-risk: Availability fails because split votes repeat and no leader is elected for as long as the draws stay locked. §9 says safety is still maintained, and the majority vote rule supports that.
- detectable: partly — a run of split elections is visible, but servers do not see one another's timeout draws.
- silent: 2 — identical draws are uncommon once clocks and RNGs differ, and they show up only when a leader has already failed.
- basis: text

### E16
- contract: Clocks used for election timers advance at about the same rate, without jumps large compared with the election timeout.
- source: §9 "clocks must proceed at about the same rates"
- stated: stated
- violation: NTP steps a clock, a VM is migrated, or a garbage collector stops a process for longer than the election timeout.
- at-risk: Availability fails for that period: followers start elections or fail to start them while a leader is still valid. §9 and §3.10 say safety holds even when clocks run at arbitrary speeds, apart from the lease in E18.
- detectable: partly — a server that samples a monotonic clock against wall time can log its own jump; it cannot see that a peer's clock ran fast.
- silent: 3 — pauses and NTP steps of this size happen on ordinary hosts, and the usual trace is a leader change like any other.
- basis: text

### E17
- contract: A server the operator counts as up answers within about a broadcast time, and a server that cannot do so is stopped rather than paused and later resumed.
- source: §9 "must be timely (or stopped)."
- stated: stated
- violation: A virtual machine is suspended, or a scheduler freezes the process, and later the server resumes and campaigns or holds a client.
- at-risk: Availability fails while the cluster cannot elect or keep a leader, which is the bound §9 states. Safety of the core algorithm remains, because a resumed server still has its old term and log.
- detectable: partly — RPC timeouts expose a slow peer; a pause shorter than the failure detector looks like ordinary delay.
- silent: 2 — suspend-and-resume is less common than a crash, and the extra election is easy to miss among ordinary ones.
- basis: text

### E18
- contract: If read-only queries use the clock lease, no server's clock runs ahead of another's by more than the drift bound used to shorten that lease.
- source: §6.4.1 "The lease approach assumes a bound on clock drift across servers"
- stated: stated
- violation: A follower's clock jumps forward, its election timer fires inside the leader's lease, a new leader commits entries, and the old leader still answers reads.
- at-risk: Linearizability of those reads fails: the client can be given arbitrarily stale state, which is the failure §6.4.1 names. State Machine Safety for entries that were applied is a separate question; the stale read may simply omit newer committed entries.
- detectable: no — the stale reply is a successful response, and the old leader has no signal that a follower's clock already started an election.
- silent: 2 — the text advises against this mechanism unless it is required; where it is enabled, a clock step is silent, but many deployments never take the path.
- basis: text

### E19
- contract: If servers use the monotonic-read extension, each client tells the server the highest log index it has already observed.
- source: §6.4.1 "Clients would track the latest index corresponding to"
- stated: stated
- violation: A client reads at index n, then contacts another server and omits n, so that server answers from an older applied prefix.
- at-risk: The sequential-consistency fallback in §6.4.1 fails for that client. It is the fallback for when the lease clocks misbehave, so losing it brings back a stale read. I am unsure how often operators rely on this extension; the text offers it and LogCabin does not implement the lease.
- detectable: no — a missing index is indistinguishable from a client that has never read.
- silent: 2 — the omission matters only when the client changes servers, and Raft does not flag it.
- basis: text

### E20
- contract: The state machine is a deterministic function of the committed log: local time, randomness, and host identity affect results only when a leader has already written those inputs into the log.
- source: §11.6 "the effects of client requests must not depend on each server’s current time."
- stated: stated
- violation: Apply reads the local clock, iterates a hash map in randomized order, or calls an unreplicated service, so two replicas compute different states or outputs.
- at-risk: State Machine Safety fails in effect: the same log index yields different client-visible results on different servers, so the cluster no longer behaves as one state machine. The log entries themselves can still match.
- detectable: partly — replicas can checksum state and compare, which Raft does not require; otherwise the outputs simply disagree.
- silent: 3 — custom state machines that consult local time or randomness show up regularly, and the divergence raises no consensus error.
- basis: text

### E21
- contract: Expiry of client sessions is a deterministic function of the replicated log, using the same inputs on every server.
- source: §6.3 "session expiry must be deterministic, just as normal state"
- stated: stated
- violation: One server drops a client's session from its own wall clock and then executes a duplicate command, while another server still suppresses that duplicate.
- at-risk: State Machine Safety fails because the replicas no longer hold the same state, which is the divergence §6.3 spells out. Linearizability fails with it, because the command was applied twice on one replica and once on another.
- detectable: partly — comparing session tables across replicas would show it; a single server sees only its own expiry.
- silent: 3 — tying expiry to the local clock is an easy mistake, and the split in duplicate filtering need not raise an error.
- basis: text

### E22
- contract: The only externally visible effect of applying a command is the deterministic output returned to the client through Raft.
- source: §2.1 "the servers appear to form a single, highly reliable state"
- stated: implicit
- violation: Apply sends mail, charges a card, or deletes an object in another system, so every replica performs that action.
- at-risk: The guarantee that the cluster appears as one state machine fails for that action: the client observes one response and the outside world observes one action per replica. I am reading this from the architecture in §2.1; the text does not discuss side effects by name.
- detectable: no — Raft sees the command and the returned output, not an action the state machine took elsewhere.
- silent: 3 — doing real work inside apply is a common integration shortcut, and the duplicates look like application behavior.
- basis: general systems experience

### E23
- contract: After a restart, a volatile state machine is rebuilt by loading the latest snapshot and reapplying the following log entries, and its old address space is not resumed in place of that rebuild.
- source: §3.8 "A volatile state machine must be recovered"
- stated: stated
- violation: A hibernated process or a memory checkpoint is resumed with a half-updated state machine while the log on disk has moved on or was replayed differently.
- at-risk: State Machine Safety fails because that server's applied state is no longer the state of the committed prefix. A normal process restart does not do this; a checkpoint restore does.
- detectable: partly — rebuilding from the log and comparing a checksum to the snapshot catches a mismatch; a resumed image has no marker that replay was skipped.
- silent: 1 — ordinary restarts drop volatile memory, and resuming a conflicting checkpoint is rare.
- basis: text

### E24
- contract: For a persistent state machine, the durable image and the durable last-applied index describe the same prefix across a crash.
- source: §3.8 "its last applied index must also be persistent."
- stated: stated
- violation: A crash falls between applying a command to the on-disk database and recording lastApplied, so restart either skips the command or runs an increment a second time.
- at-risk: State Machine Safety fails because this server's state diverges from peers that applied the prefix once. The text's reason for persisting the index is to avoid reapplying, which is this failure.
- detectable: partly — a checksum that ties lastApplied to the image catches the mismatch; without it, a replayed command looks like a normal apply.
- silent: 3 — that crash window is a regular bug on disk-backed machines, and the following restart is quiet.
- basis: text

### E25
- contract: The state machine can produce and later reload a consistent image of committed state at a single log index, including the session table used for linearizability.
- source: §5.1 "serialize the information they keep for providing linearizability to clients (see Chapter 6)."
- stated: stated
- violation: fork copies the address space while other threads are mid-update, or the snapshot omits client sessions, and a follower or a restarted server loads that image.
- at-risk: State Machine Safety fails if later entries apply on a torn base. Linearizability fails if a session was dropped and a duplicate command runs again after the snapshot. §5 also requires the image to be consistent; this entry includes that.
- detectable: partly — a structural checksum can reject some torn images; a parseable image that simply lacks sessions still loads.
- silent: 2 — careful servers snapshot under a lock and include sessions, but a fork racing other threads, or a forgotten session field, fails without an alarm.
- basis: text

### E26
- contract: Applying a committed command returns in finite time and does not wait on a further Raft commit.
- source: §3.5 "Raft guarantees that committed entries are durable and will eventually be exe-"
- stated: implicit
- violation: The state machine blocks on a lock the consensus thread holds, or calls out to a service that never answers, so the committed prefix stops being applied.
- at-risk: The guarantee that committed entries are eventually executed on available servers fails. Clients can also stop receiving results for commands that are already durable. I am unsure only about commands that are allowed to run for a very long time but do finish.
- detectable: yes — the server can bound apply and surface a stall when the command does not return.
- silent: 2 — a permanent stall is usually visible; the quiet cases are applies that are only extremely slow.
- basis: text

### E27
- contract: The host provides enough durable capacity for the compacted state and the uncompacted log tail, and a write that does not fit returns an error instead of a short record treated as complete.
- source: §5 "servers will either run out of space, or they will take too"
- stated: stated
- violation: The log is left uncompacted until the disk fills, or a short write at ENOSPC is acknowledged as a full log entry.
- at-risk: Availability fails once servers cannot append or cannot restart in time, which is the failure §5 names. A short write acknowledged as complete is also an E4 integrity failure and can break Log Matching.
- detectable: partly — a normal ENOSPC is returned to the server; a short write is detectable only if lengths are checked.
- silent: 2 — filling the disk is usually reported; accepting a short write as a full entry is the rarer quiet case.
- basis: text

### E28
- contract: The host provides the extra memory concurrent snapshotting needs, or it lets the server stop taking new entries until the snapshot finishes.
- source: §5.1.1 "Servers require additional memory for snapshotting concurrently, which should be planned for"
- stated: stated
- violation: Copy-on-write snapshotting exhausts memory and the kernel kills the process, or the server keeps accepting entries and never finishes the snapshot.
- at-risk: Availability of that server fails, and if enough servers snapshot at once the cluster can lose the ability to commit. A kill during a non-atomic publish is also an E5 risk. The text already tells the server to stop accepting entries rather than die.
- detectable: yes — allocation failure is visible to the process, which can shed load as §5.1.1 describes; an external kill looks like a crash.
- silent: 2 — memory pressure often becomes a visible kill or stall, though some hosts only slow down.
- basis: text

### E29
- contract: Whenever the deployment expects the cluster to be available, some majority of the configuration is up and can exchange messages with each other and with clients.
- source: §2.1 "any majority of the servers are operational"
- stated: stated
- violation: A partition or a power cut leaves every majority either down or unable to talk, while clients can still reach only a minority.
- at-risk: Availability fails, including during the outage's reads and writes. The text's safety claim is meant to survive this partition, so Election Safety and State Machine Safety should hold; a leader on the minority must stop committing.
- detectable: yes — a leader that cannot hear a majority steps down, and clients see the outage.
- silent: 2 — a full majority partition is an outage operators usually see; a partial one that still looks up from some clients is easier to miss.
- basis: text

### E30
- contract: A server that the operator counts as available can, in finite time, receive the leader's retried RPCs and therefore apply every committed entry.
- source: §3.5 "Raft guarantees that committed entries are durable and will eventually be exe-"
- stated: implicit
- violation: A firewall or a one-way link drops every AppendEntries to a server that otherwise looks up, forever.
- at-risk: The "eventually executed by all of the available state machines" guarantee fails for that server. Entries committed on the majority stay committed. The formal model in §8.1 allows arbitrary delay, so this obligation is only as strong as the informal "eventually" claim; I am unsure the text means a hard bound.
- detectable: partly — the leader sees failed RPCs to that follower, while a follower that still answers heartbeats can hide a stalled apply.
- silent: 2 — RPC failures are often logged, and a server believed to be caught up can lag if those logs are ignored.
- basis: text

### E31
- contract: The mechanism clients use to find the cluster returns every current member, is updated to add a server before that server joins and to remove a server only after it has left, and uses broadcast or multicast only on a network that delivers them.
- source: §6.1 "clients should always be able to find all of the cluster"
- stated: stated
- violation: DNS still lists only the servers that were just removed, or it lists a different cluster, or clients broadcast on a network that drops broadcasts.
- at-risk: Availability fails because clients cannot reach a leader. Including a few extra servers is harmless, as the text says; listing the wrong cluster can make a client treat another state machine's result as this one's. I am unsure the text counts that last case as more than a directory mistake.
- detectable: partly — a server that is shown both the directory and the configuration can compare them; Raft as specified does not look up DNS.
- silent: 3 — directories drift from live membership in ordinary operation, and clients keep working as long as one path to a leader remains.
- basis: text

### E32
- contract: If the cluster uses a static configuration, every server's file names the same set of members.
- source: §4.4 "each server simply has a static file listing the configuration."
- stated: implicit
- violation: One server is booted with a hand-edited file that names a different trio than its peers.
- at-risk: Election Safety fails if the two files allow two majorities that do not intersect, which is the split §4 illustrates for a configuration change. Availability fails if each server waits for a majority the others do not recognize.
- detectable: partly — servers can exchange a hash of the file once they can talk; until then each side looks healthy to itself.
- silent: 2 — this arises in clusters that still use static files, and the disagreement can wait until the next election.
- basis: text

### E33
- contract: A new cluster starts from a single configuration that one initial server already has committed, and every other process starts with an empty log and joins later.
- source: §4.4 "initialized with a configuration entry as the first entry in its log."
- stated: stated
- violation: Two servers are each initialized as a one-server cluster, both commit client commands, and both are later pointed at the same clients.
- at-risk: State Machine Safety and linearizability fail across the pair the operator thinks is one cluster: the same client command can be decided differently on each side. Each side separately satisfies Raft. The text presents this bootstrap as a recommendation because the static file is error-prone.
- detectable: partly — the two singletons never meet, so neither server notices; an operator who looks at both can.
- silent: 2 — bringing up two accidental primaries is a known mistake and each side looks healthy.
- basis: text

### E34
- contract: If a new server replaces a member by taking over its network address, the replaced server never runs again.
- source: §4 "the replaced server will never come back up"
- stated: stated
- violation: The old host is powered back on, still configured as a voter, while the new host has its address, and both answer RequestVote.
- at-risk: Election Safety fails because there is an extra vote, which is the example §4 gives, so two leaders can be chosen for one term. Leader Completeness can fail with them.
- detectable: partly — hearing two hosts claim one address is suspicious, but an extra RequestVote looks like any other vote.
- silent: 2 — automated membership changes avoid this path; where address takeover is still used, the old host can return without an error of its own.
- basis: text

### E35
- contract: Automation and operators do not remove voting members in a way that leaves fewer durable copies than the deployment's fault-tolerance target, and a replacement is added before the member it replaces is removed.
- source: §4.4 "it can be dangerous for the cluster to automatically remove failed servers"
- stated: stated
- violation: A controller deletes a dead voter as soon as it stops answering, or it removes the old server before the new one's log has caught up, leaving two voters where three were required.
- at-risk: The durability and availability claims fail: one more fault can wipe or isolate the remaining majority. Safety of entries still stored on a majority of whoever is left holds. §4.4 says adding before removing is what keeps a one-failure margin during the swap.
- detectable: partly — the cluster can compare its voter count with a configured target if one was set; Raft does not know the intended replication factor by itself.
- silent: 3 — removing a dead voter before a replacement is caught up is a recurring policy, and the cluster still answers while it is one fault from losing data.
- basis: text

### E36
- contract: During a membership change, a majority of the old configuration stays available at least until the new configuration is committed, and a majority of the new configuration is available.
- source: §4.2.4 "majority of the old configuration is available (at least until Cnew is committed) and that a majority"
- stated: stated
- violation: The operator starts adding a server that is down, or the only servers that hold the old configuration fail before the new entry commits.
- at-risk: Availability during the change fails: §4.2.4's argument that a leader can be elected and can finish the change no longer applies. Safety of the single-server overlap still holds if the servers that remain follow the log rules. The text says it assumes this "among other things," and it does not list the other things.
- detectable: yes — the leader cannot commit the new configuration if the required majority does not answer, and §4.2.1 says to abort a server that never catches up.
- silent: 2 — a change with no new majority usually stalls visibly; a barely alive majority can look fine.
- basis: text

### E37
- contract: Each client uses a distinct identifier returned by a completed registration, and puts that identifier on every later command.
- source: §6.3 "each client is given a unique identifier"
- stated: stated
- violation: Two clients share an identifier, or a client invents one, or a client continues with an identifier whose session the cluster has already dropped.
- at-risk: Linearizability fails. A shared identifier makes one client's command suppress the other's as a duplicate, or lets one client observe the other's result. An unknown session is rejected rather than executed, which preserves exactly-once only if the client stops; §6.3 says LogCabin crashes the client there.
- detectable: partly — an unknown identifier is rejected after the session is gone; two clients that share a live identifier are indistinguishable.
- silent: 2 — registration makes collisions uncommon, but a copied identifier suppresses commands with no extra error.
- basis: text

### E38
- contract: Each logical command carries a client-chosen serial number that is unique among that client's in-flight commands, and every retransmission or network duplicate repeats that same serial number.
- source: §6.3 "serial numbers to every command."
- stated: stated
- violation: A client or a proxy times out, allocates a new serial number, and sends the same operation again, or a duplicate arrives with a rewritten serial number.
- at-risk: Linearizability fails because the command is applied twice, which is the duplicate-lock and double-increment failure §6.3 describes. The core log properties can all still hold.
- detectable: no — a fresh serial number is defined to be a new command, so the server has no signal that the client meant a retry.
- silent: 4 — lost responses and retries are ordinary, and the second execution is returned as a new success.
- basis: text

### E39
- contract: A client that has not received a response does not submit that same operation as a new command, including after the cluster reports that the session is gone.
- source: §6.3 "this would risk duplicate execution of"
- stated: stated
- violation: The client gets a session-expired error or a timeout, opens a new session, and resubmits the unacknowledged operation.
- at-risk: Linearizability fails for that operation: it may already have been committed under the old session and is then committed again. §6.3 prefers an error over allocating a fresh session precisely to avoid this.
- detectable: partly — the session-expired error tells the client to stop; once the client uses a new session, the server treats the command as new.
- silent: 3 — opening a new session after a timeout and resubmitting is ordinary client behavior, and the second apply is reported as success.
- basis: text

### E40
- contract: A client that still has commands in flight or that expects its session to remain sends keep-alives so the agreed expiry rule does not drop the session.
- source: §6.3 "Live clients issue keep-alive requests during periods of inactivity"
- stated: stated
- violation: A quiet client sends nothing until the logged idle time passes the session limit, then sends another command.
- at-risk: The exactly-once session is gone. The next command returns an error if the server follows §6.3, so linearizability of a command already applied is preserved only if the client does not reissue it (E39). Availability of that client's further commands fails.
- detectable: yes — the session expires and the next command returns an error rather than running.
- silent: 2 — the client is told, so the fully quiet case is a stack that drops the session and continues without surfacing that error.
- basis: text

### E41
- contract: The leader clock that is written into the log as the time base for session expiry does not jump forward far enough to expire sessions that still have live clients.
- source: §6.3 "the leader augments each command that it appends to"
- stated: implicit
- violation: NTP or a virtual-machine migration steps the leader's clock past the idle bound, the new timestamp is committed, and every active session expires at once.
- at-risk: Those clients lose the exactly-once session. If they stop, an unacknowledged command may have been applied with no response, which linearizability allows for an incomplete operation. If they reissue under E39's violation, the command runs twice. I am unsure the text treats the clock as more than an agreed input; the hazard is how far that input jumps.
- detectable: partly — a huge gap between logged timestamps is visible in the log; a moderate step looks like time passing.
- silent: 2 — a step large enough to expire live sessions is occasional, and clients see an error if the server follows LogCabin.
- basis: general systems experience

### E42
- contract: Clients tolerate a period of unavailability on the order of an election timeout without treating the cluster as failed.
- source: §4.2.1 "clients must already be able to tolerate"
- stated: stated
- violation: A client library uses a deadline shorter than the election timeout and returns a hard failure while a new leader is still being chosen.
- at-risk: The availability the client observes fails during ordinary leader changes, which §4.2.1 says clients must already absorb. Safety of committed entries is unchanged. A client that then retries under a new serial number also hits E38.
- detectable: no — the server cannot see the client's deadline; it is still finishing the election.
- silent: 2 — the application sees a timeout, so the failure is not invisible, but Raft itself records nothing that names the client's deadline.
- basis: text

### E43
- contract: A client that loses the server it was using retries some other member instead of waiting on that one server.
- source: §6.2 "simply retry with a random server."
- stated: stated
- violation: The client keeps dialing a leader that has crashed, or a server that is partitioned from the majority, until its own budget is spent.
- at-risk: Availability for that client fails even though a majority is up and has elected a leader. §6.2 describes this as unnecessary delay. Safety is unchanged.
- detectable: partly — the server can return the leader's address on a redirect, but it cannot tell whether the client followed it.
- silent: 2 — the client sees connection errors, which are visible, while the cluster looks healthy.
- basis: text

## Recognised

- E3: etcd's operational guidance requires the WAL to reach stable media (fsync, write cache off or a power-loss-protected disk); this dissertation's LogCabin setup records "write caching off" in §10.3. I recall the same class from disks that acknowledge a flush from a volatile cache. I am not pinning one CVE from memory.
- E7: I recall etcd documentation and production incidents where one member was restored from an older data-directory snapshot, or restarted empty under the same member id, and the cluster lost committed data or diverged; copying a data directory to clone a member is the same failure.
- E8: I recall etcd taking an exclusive lock on the data directory so two processes cannot run one member.
- E13: I recall etcd clusters failing to keep a leader when disk fsync latency exceeded the election timeout, especially on cloud volumes.
- E16: I recall etcd leader churn when a process pause or a clock step exceeded the election timeout; the symptom is elections, matching the availability bound rather than a safety break.
- E18: I recall hashicorp/raft's lease-based read-only option, documented to assume bounded clock drift, the same assumption as §6.4.1. I also recall CockroachDB leaseholder incidents in which a clock jump broke linearizability; I am not certain of the post's title.
- E33: I recall operators starting more than one etcd with `--force-new-cluster`, so two servers each believed they were the sole committed configuration.
- E34: the returned-server extra vote is the case §4 already states; I have seen the same failure described for address takeover without fencing.
- E35: I recall Kubernetes etcd controllers and hand-run membership changes that removed a voting member before its replacement had caught up, leaving a cluster one fault from losing quorum.
- E20: I recall custom state machines that read local time or a random source inside apply and diverged; I do not have one canonical incident name.
- E38: I recall applications that retry a non-idempotent command as a new request after a lost response. This is the failure §6.3 is written to prevent; I am not naming a separate paper.
- The stale reads Jepsen reported for etcd and Consul (Kingsbury, "Call me maybe: etcd and Consul", cited as [45] in §6.4 and §8.3) are an implementation skipping the read-only quorum check, under a partition §2.1 says safety must survive. I do not count that as one of these environment contracts.

## Report

43 contracts, E1 through E43.

Algorithm limits I did not enter as environment contracts: §11.3 says that if a leader is elected and crashes repeatedly before it commits an entry from its term, the log can grow without bound, because an entry from an older term is not committed by counting replicas. The text calls that impractical. Early Raft also had a safety bug in committing entries from older terms (Figure 3.7), found by David Mazières, and a membership-change liveness bug found by Ezra Hoch; the dissertation gives the repaired rules. Hugues Evrard found a small omission in the formal specification. §8.4 leaves membership, log compaction, client interaction, and liveness unproved. None of those is an obligation on the disk, the network, the clock, the process manager, the operator, the state machine, or the host.

`ls -R` and `git status` in the checkout, after this file was written:

```
.:
AGENTS.md
BRIEF.md
enumeration.md
source

./source:
OngaroPhD.pdf
OngaroPhD.txt
```

```
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

Things I could not decide:

- The formula line in §3.9 is stored in `OngaroPhD.txt` with the much-less-than sign replaced by the ASCII control character 0x1c, so I quoted the prose sentences around it. I did not try to re-read that glyph from the PDF.
- §4.2.3 tells servers to ignore a RequestVote that arrives within the minimum election timeout of a heartbeat, so a removed server does not need an operator to power it off. I did not add that operator obligation. A deployment that omits that rule would have one.
- E12 (integer wrap) and E22 (side effects outside the client reply) are mine; the text never mentions width or external actions.
- E18 and E19 apply only if those optional read paths are used. The text states them and recommends the lease only when performance requires it.
- E34 applies to the manual address-takeover procedure. The automated membership change is the path the text prefers.
- §4.2.4 says availability during a membership change assumes the two majorities "among other things" and does not list the other things. I did not invent the missing assumptions.
- §2.2's use of two-phase commit across partitioned state machines is a client of Raft, not a service Raft depends on, so I left it out.
- I could not see the PDF's page images as text; every quotation was copied from `OngaroPhD.txt`. Page headers are sometimes inserted mid-sentence in that file. I avoided those broken lines.
