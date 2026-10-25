### E1
- contract: A server fails only by stopping, and until it stops it runs the protocol as written, including the messages it sends and the state it keeps.
- source: §8.1 "Servers fail by stopping and may later restart from stable storage on disk."
- stated: stated
- violation: A live process keeps sending votes or log entries after a bit flip, wild pointer, or partial memory corruption changes a term, a vote, or a command.
- at-risk: Election Safety and State Machine Safety fail because both rest on servers obeying the protocol whenever they are not stopped; a single forged-by-bug vote can complete a second majority in one term.
- detectable: partly — replica invariant checks can notice two leaders in one term or a log mismatch after the fact, and a well-formed but wrong vote is indistinguishable from a legal one.
- silent: 1 — silent memory corruption that still speaks Raft is rare on server hardware over a year; ordinary crashes stop the process and are visible.
- basis: text

### E2
- contract: The network may delay, drop, duplicate, reorder, and partition messages, and it must not alter an RPC payload or deliver a message invented by a host that is not the member it names.
- source: §2.1 "They ensure safety (never returning an incorrect result) under all non-Byzantine conditions,"
- stated: implicit
- violation: A bit error changes a log term in flight, or a host outside the configuration injects a RequestVote or AppendEntries that servers accept as coming from a member.
- at-risk: Election Safety and Log Matching fail: an extra or altered vote elects two leaders in one term, and an altered command at the same index and term makes two logs disagree.
- detectable: partly — a checksum or peer authentication above the transport would reject the bad message; with neither, the cluster accepts it as normal traffic.
- silent: 1 — on a private network, undetected payload changes and forged cluster RPCs are rare over a year.
- basis: text

### E3
- contract: The host runs at most one live process for each voting identity, and a server that has been replaced must never accept RPCs as that member again.
- source: §4 "the administrator must guarantee that the replaced server will never come back up,"
- stated: stated
- violation: An operator starts a VM clone, a forked child, or the old host while the replacement is already voting under the same server identity or the same address.
- at-risk: Election Safety fails: the two processes can grant two votes in one term, so two candidates can each collect a majority (the dissertation's "extra vote").
- detectable: partly — binding one address twice fails loudly, but two addresses for one identity are accepted as normal votes until logs diverge.
- silent: 2 — cloning a VM or moving an address without fencing the old host happens in a minority of deployments over a year and raises no duplicate-identity error.
- basis: text

### E4
- contract: A server that has lost any of its persistent state must not rejoin under its previous identity; it may return only as a new member through a membership change.
- source: §3.8 "If a server loses any of its persistent state, it cannot safely rejoin the cluster with its prior identity."
- stated: stated
- violation: An operator deletes the data directory or replaces the disk, then starts the same server id with an empty log and a fresh term.
- at-risk: Leader Completeness fails when that empty member's vote completes a majority for a candidate that never stored a committed entry, so a later leader applies a different command at that index.
- detectable: partly — an empty log on a known member can be noticed by an operator, and the protocol still accepts the member's vote.
- silent: 2 — repaving one node and restarting it in place is a familiar recovery step and often produces no error unless a second fault hits the dangerous window.
- basis: text

### E5
- contract: A majority of the cluster must not lose the persistent state it has already acknowledged, or the operator must not proceed as if the old log were still intact.
- source: §3.8 "If a majority of the cluster loses its persistent state, however,"
- stated: stated
- violation: A shared disk, a restore of an old snapshot onto a majority of members, or a script wipes three of five data directories and the processes start again as the same cluster.
- at-risk: The durability guarantee fails: committed entries can be gone, and membership changes cannot make progress; State Machine Safety fails if the emptied majority elects a leader and commits a new command at an old index.
- detectable: partly — a majority that cannot form a quorum is obvious, and a majority that restarts empty and then commits a new history looks like a fresh cluster unless something outside the protocol remembers the old log.
- silent: 1 — losing a majority of durable copies is uncommon in a year, and the outage or the missing data is visible.
- basis: text

### E6
- contract: Stable storage must retain the latest current term and the vote granted in that term across a restart, including after power loss.
- source: §3.8 "each server persists its current term and vote; this is necessary to prevent the server from"
- stated: stated
- violation: Power fails after a server has sent a vote, and the disk comes back without that term or that vote, so the restarted process votes for a second candidate in the same term.
- at-risk: Election Safety fails because one server supplies two votes in one term; Leader Completeness also fails if a forgotten higher term lets the server replace a newer leader's entries with entries from a deposed leader.
- detectable: no — after restart the server has no record of the lost vote, and the second vote is a legal RequestVote response.
- silent: 2 — the window is a crash between the vote and a durable record, which is uncommon but leaves no error on the following restart.
- basis: text

### E7
- contract: Stable storage must retain every log prefix the server has acknowledged as stored, and a restart must not revive an older prefix, a hole, or a different command at a stored index.
- source: §3.8 "Each server also persists new log entries before they are counted towards"
- stated: stated
- violation: A follower answers AppendEntries successfully, then a crash or a disk rollback returns a shorter log, and the leader has already counted that follower toward commitment.
- at-risk: The durability guarantee for committed entries fails, and State Machine Safety fails if a later leader is elected without the committed command and writes a different one at that index.
- detectable: partly — a later consistency check can fail if the truncated server still holds a conflicting suffix; a clean rollback to a prefix looks like an ordinary lagging follower.
- silent: 2 — acknowledged entries disappearing is uncommon on sound disks over a year and is not reported as a distinct error when the server simply restarts behind.
- basis: text

### E8
- contract: A write that the disk has confirmed as flushed must still be readable after power loss, which means a volatile write cache must not acknowledge the flush early.
- source: §10.2 "flushes the log entry to disk, and sends out AppendEntries requests."
- stated: implicit
- violation: The drive or the hypervisor reports the flush complete while the data is only in a volatile cache, and power loss drops the term, the vote, or the log entries that peers already counted.
- at-risk: The same committed entries the leader may treat as durable once a majority of followers have flushed can vanish, so Leader Completeness and the durability guarantee both fail.
- detectable: no — the successful flush is the only signal Raft has, and nothing in the protocol probes that the bits survived power loss.
- silent: 3 — hosts that acknowledge flushes from a volatile cache are a regular part of ordinary fleets, and the lie produces no error unless power is actually lost.
- basis: text

### E9
- contract: Stable storage must return the bytes that were written for the term, the vote, the log, and snapshots, not a silently different or torn record that still parses.
- source: §5.1.3 "apply a checksum to it"
- stated: implicit
- violation: A torn sector changes a stored term or command into a different value that the server loads as a valid log entry.
- at-risk: Log Matching fails because one index and term now stand for two commands, so two state machines apply different entries at that index.
- detectable: partly — a checksum, which the dissertation says is worth adding, rejects the torn record; without one, a still-parseable record is loaded as normal.
- silent: 2 — undetected torn or bit-flipped records that remain syntactically valid are uncommon over a year, and deployments that skip checksums do not see them.
- basis: text

### E10
- contract: A crash during a snapshot write must not leave a partial snapshot that the server will load as the full state on the next start.
- source: §5.1.3 "flushed to disk; this ensures that no server loads a partially written snapshot on startup."
- stated: stated
- violation: The filesystem exposes the destination filename with a short or torn snapshot after power loss, and the process loads it, discards the older complete snapshot, and truncates the log to match.
- at-risk: State Machine Safety fails because this server's state no longer matches the committed prefix, and later applies continue from the wrong state.
- detectable: partly — a checksum or an expected length catches many partial files; a short file that still parses does not.
- silent: 2 — crashes in the middle of a snapshot are occasional, and a partial file that parses is loaded without an error.
- basis: text

### E11
- contract: After a log prefix is discarded, stable storage must keep the index and term of the last included entry so the remaining log stays anchored.
- source: §5 "Raft retains the index and term of the last entry it discarded; this anchors the rest of"
- stated: stated
- violation: The snapshot is kept and the log suffix is kept, but the saved last-included term is lost or replaced, so the next AppendEntries consistency check uses the wrong predecessor.
- at-risk: Log Matching fails across the snapshot boundary: a follower can accept entries that do not continue the committed prefix, and State Machine Safety fails at the first overwritten index.
- detectable: partly — a follower whose own log still has the old prefix will reject the mismatch; a server that lost the anchor and has no other copy will not.
- silent: 2 — losing only the anchor metadata is uncommon, and the server still boots.
- basis: text

### E12
- contract: The latest cluster configuration in a discarded log prefix must remain durable with that prefix.
- source: §5 "Raft also retains the latest configuration from the discarded log prefix"
- stated: stated
- violation: After compaction the process restarts with the snapshot and the log suffix but with an older or empty configuration, so it computes majorities from the wrong member set.
- at-risk: Election Safety fails if the restored configuration and a newer one on other servers can each form a majority in the same term.
- detectable: partly — peers that still have the newer configuration refuse votes that do not match their log, and a server that only has the stale configuration does not see an error by itself.
- silent: 2 — a configuration record dropped independently of the snapshot is uncommon and looks like a normal boot.
- basis: text

### E13
- contract: On a persistent state machine, the durable user state and the persisted last-applied index must describe the same prefix after a restart.
- source: §3.8 "its last applied index must also be persistent."
- stated: stated
- violation: The process crashes after applying an entry to its on-disk state machine and before recording the index, or the other way around, then restarts and either skips that entry or applies it again.
- at-risk: State Machine Safety fails on a second apply of a non-idempotent command, and a skipped index makes this server's state diverge from the others even though the log matches.
- detectable: partly — a double apply of a counter is visible in the data; a skipped entry with no external cross-check is not.
- silent: 2 — the crash window is uncommon on a single node over a year, and a matching restart produces no error.
- basis: text

### E14
- contract: The host must provide enough durable space for the log and the snapshot the server is required to keep, and running out of space must not destroy older durable state.
- source: §5 "will eventually cause availability problems: servers will either run out of space, or they will take too"
- stated: stated
- violation: The data volume fills during log append or snapshot write, or a cleanup job deletes the previous snapshot to free space before the new one is durable.
- at-risk: Availability fails when a majority cannot persist new entries; State Machine Safety fails if the only complete snapshot is removed and a restart loads nothing for a discarded prefix.
- detectable: yes — a full volume returns a write error the process can observe, unless some other agent deletes old files without an error from the disk.
- silent: 1 — filling the disk is usually reported; silent deletion of the last good snapshot is rare.
- basis: text

### E15
- contract: For the cluster to stay available, some majority of the configured servers must be operational.
- source: §2.1 "as long as any majority of the servers are operational"
- stated: stated
- violation: Two of three servers lose power, or a shared rack takes out three of five, and fewer than a majority remain up.
- at-risk: The availability guarantee fails because elections and commitment both need a majority; safety is not what this contract is for.
- detectable: yes — heartbeats fail, the leader steps down, and clients stop receiving results.
- silent: 1 — a majority outage is an outage the operator sees.
- basis: text

### E16
- contract: That same majority must be able to exchange RPCs with one another and with clients.
- source: §2.1 "and can communicate with each other and with clients."
- stated: stated
- violation: A partition leaves no majority in any connected component, or the surviving majority cannot reach any client network.
- at-risk: Availability fails for the duration of the partition; the dissertation's safety claims are meant to survive this case, so this contract is the availability side of the same sentence.
- detectable: yes — servers on the minority side time out and clients that cannot reach the leader see errors.
- silent: 1 — a partition that stops the service is visible.
- basis: text

### E17
- contract: Until the new configuration entry is committed, a majority of the old configuration must stay available, and a majority of the new configuration must be available.
- source: §4.2.4 "majority of the old configuration is available (at least until Cnew is committed) and that a majority"
- stated: stated
- violation: The operator removes the leader and another old voter, or the new server is partitioned, before the new configuration is committed.
- at-risk: Availability during the membership change fails, and in the extreme the cluster cannot finish the change or elect a leader; the overlap argument for Election Safety assumes the configured sets, not that these majorities stayed up.
- detectable: yes — the configuration change stalls and client calls time out.
- silent: 1 — a stuck reconfiguration is visible as an outage or a failed admin call.
- basis: text

### E18
- contract: Clients must be able to discover every live member, and any new member's address must be published before that member is added to the cluster.
- source: §6.1 "it should be inclusive: clients should always be able to find all of the cluster"
- stated: stated
- violation: DNS still lists only the servers that were just removed, or a new server is added before any client directory knows its address and the old addresses then go away.
- at-risk: The availability guarantee fails at the client even while a majority is healthy, because the client cannot reach a server that can route it to the leader.
- detectable: partly — the cluster does not see the directory; clients see connection failures, which an operator may not tie to the missing record.
- silent: 2 — hand-maintained directories drift a few times a year in ordinary clusters, and a list that is merely stale often still contains one live server so nobody sees an error.
- basis: text

### E19
- contract: The time to send RPCs to the cluster and collect responses, including each recipient's durable write, must stay about an order of magnitude below the election timeout.
- source: §3.9 "broadcast time should be an order of magnitude less than the election timeout so that leaders can"
- stated: stated
- violation: Followers' disks take longer to flush than the election timeout, or the timeout is set near the wide-area round trip, so followers start elections while a leader is healthy.
- at-risk: Availability fails: the cluster does not keep a steady leader, so clients cannot get commits; the dissertation states that safety does not depend on this timing.
- detectable: partly — repeated elections appear in logs and are not labeled as a broken timing assumption.
- silent: 2 — disk stalls and tight timeouts produce occasional leader changes over a year that are logged as ordinary elections rather than as errors.
- basis: text

### E20
- contract: The election timeout must be orders of magnitude shorter than the mean time between failures of a single server.
- source: §3.9 "election timeout should be a few orders of magnitude less than MTBF so that the system makes"
- stated: stated
- violation: Processes are killed or crash every few seconds, faster than an election can finish and a leader can commit an entry.
- at-risk: Availability fails because no leader stays up long enough to make progress; safety is not claimed to depend on this inequality.
- detectable: yes — the implementation sees continuous elections and almost no successful commits.
- silent: 1 — servers that crash every few seconds are rare, and the resulting election storm is obvious.
- basis: text

### E21
- contract: Servers must draw election timeouts from a random distribution that is not synchronized across the cluster, and their clocks must advance at about the same rate.
- source: §9 "somehow synchronized), clocks must proceed at about the same rates, and servers and networks"
- stated: stated
- violation: Every server is configured with the same fixed timeout and the same clock, or one server's clock runs several times faster than the others and fires elections continuously.
- at-risk: Availability fails when split votes repeat or a fast clock keeps deposing the leader; the text says safety still holds when these assumptions fail.
- detectable: partly — endless split votes show up as election churn without identifying synchronized timers as the cause.
- silent: 1 — identical timeouts and clocks that run at very different rates are rare in a year of ordinary NTP-disciplined hosts.
- basis: text

### E22
- contract: A server that has not failed must be scheduled and must finish its durable RPCs promptly, or it must be treated as stopped.
- source: §9 "must be timely (or stopped). If these assumptions are not met for some period of time, the cluster"
- stated: stated
- violation: A stop-the-world garbage collection, a virtual-machine freeze, or a multi-second fsync stall pauses a follower or the leader for longer than an election timeout while the process is still considered up.
- at-risk: Availability fails for that interval because followers start elections or a leader cannot complete heartbeats; safety is maintained, as the same paragraph says.
- detectable: partly — the cluster observes an election and does not report the pause itself.
- silent: 3 — long GC, migration, and disk stalls occur on ordinary fleets over a year and are not surfaced as a violated timing assumption.
- basis: text

### E23
- contract: If read-only queries use a leader lease instead of a confirming round of heartbeats, no server's clock, including pauses and time-sync steps, may advance faster than the drift bound used to shorten that lease.
- source: §6.4.1 "The lease approach assumes a bound on clock drift across servers (over a given time period, no"
- stated: stated
- violation: The leader's monotonic clock jumps forward, or a follower is paused longer than the drift bound, and the leader answers reads after followers have already elected someone else.
- at-risk: Linearizability of reads fails: the deposed leader returns a stale value with no later committed write. I am unsure only about deployments that never enable this extension; the basic heartbeat read path does not take this dependency.
- detectable: no — the stale reply is a normal successful query, which is why the text says the result can be arbitrarily stale.
- silent: 3 — on clusters that enable clock leases, pauses and step adjustments past a tight bound are occasional over a year and raise no error; clusters that do not enable leases do not take the dependency.
- basis: text

### E24
- contract: The state machine must be a deterministic function of the log: the same prefix must produce the same state and outputs on every server, so any local time, randomness, or host identity used in a command must already have been written into that log entry.
- source: §11.6 "the effects of client requests must not depend on each server’s current time."
- stated: stated
- violation: A command reads the local clock or iterates a hash map in randomized order at apply time, so two servers that apply the same entry compute different states or different replies.
- at-risk: The single-state-machine guarantee fails: clients observe different outputs for one committed index, which is State Machine Safety in the form the operator can see.
- detectable: partly — comparing state checksums across replicas would catch it, and Raft does not require that comparison, so the first sign is often two clients reading different values.
- silent: 3 — commands that sample local time or unordered collections still appear in ordinary services over a year, and nothing in the protocol flags the divergence at apply time.
- basis: text

### E25
- contract: Session expiry and any other housekeeping that decides which commands run must be a deterministic function of the log, not of a local timer.
- source: §6.3 "session expiry must be deterministic, just as normal state"
- stated: stated
- violation: One server drops a client's session from a local LRU or a local clock while another server keeps it, and only one of them re-executes a retried command.
- at-risk: State Machine Safety fails because the replicas no longer hold the same state after the same log prefix, which is the divergence the dissertation walks through for sessions.
- detectable: partly — divergent reads can expose it later; the expiry decision itself looks local and legal.
- silent: 2 — production session tables usually follow the log timestamp, and a local-timer expiry bug shows up only occasionally over a year.
- basis: text

### E26
- contract: The state machine must treat a repeated client serial number as already done: it returns the stored response and does not execute the command again.
- source: §6.3 "immediately without re-executing the request."
- stated: stated
- violation: The apply path runs the command again on a duplicate serial number, or it recomputes a new response instead of returning the saved one.
- at-risk: Linearizability fails because the operation is no longer exactly once; a lock or an increment applied twice is the case drawn in the dissertation.
- detectable: no — the second execution returns a normal success result.
- silent: 3 — custom state machines omit the duplicate table often enough that a year of retries produces extra applies with no Raft error.
- basis: text

### E27
- contract: Every snapshot and every reload of the state machine must include the client-session table used to filter duplicates.
- source: §5.1 "serialize the information they keep for providing linearizability to clients (see Chapter 6)."
- stated: stated
- violation: A server snapshots the key-value data, discards the log, and restarts without the session map, then executes a retried command whose serial number was already applied.
- at-risk: Linearizability fails on that retry, and if replicas disagree about whether the session was reloaded, their states diverge.
- detectable: no — the replayed command looks like a new successful command.
- silent: 3 — leaving the session map out of the snapshot is a common custom-snapshot mistake and stays quiet until a client retries after a restart.
- basis: text

### E28
- contract: The image a server snapshots or ships to a follower must be a consistent state of exactly the committed prefix identified by that snapshot's last included index and term.
- source: §5 "the state machine must provide a consistent image of the"
- stated: stated
- violation: The snapshot mixes writes from later commands, omits an earlier committed command, or is labeled with an index it does not represent, and a slow follower installs it.
- at-risk: State Machine Safety fails on every server that installs that image, because later log entries are applied on top of the wrong state.
- detectable: partly — a follower that still has the overlapping log can fail the consistency check; a wrong value inside a prefix with the right endpoint index is not checked.
- silent: 2 — inconsistent images are not routine once snapshot code is mature, and a wrong-but-well-formed image installs without an error.
- basis: text

### E29
- contract: After a restart, the state machine must load the snapshot for the discarded prefix before it applies any later log entry.
- source: §5 "discarded log entries from disk before it can apply any entries from the Raft log."
- stated: stated
- violation: The process applies the surviving log suffix onto an empty or older in-memory state because the snapshot load was skipped or ordered after the first log entry.
- at-risk: State Machine Safety fails on this server: the same log produces a different state than on servers that loaded the snapshot.
- detectable: partly — an external checksum of state would catch it; the server otherwise comes up and serves the wrong state.
- silent: 2 — skipping the load is an occasional restart bug and does not raise an error by itself.
- basis: text

### E30
- contract: A disk-based state machine must make a prefix durable, and must be able to hand out a point-in-time consistent copy of it, before Raft is allowed to discard that prefix.
- source: §5.2 "Disk-based state machines must be able to provide a consistent snapshot of the disk for the pur-"
- stated: stated
- violation: Raft truncates the log once the state machine has the writes only in a volatile buffer, or the image sent to a follower is a mix of blocks from different prefixes because copy-on-write was not used.
- at-risk: A crash then loses committed user state even though the log prefix is gone, and a follower that installs the mixed image diverges, breaking State Machine Safety.
- detectable: partly — a crash that cannot rebuild the prefix is visible as missing data; a mixed image with a plausible index is not.
- silent: 2 — write-back buffers and in-place disk images are ordinary, and the bad window is quiet until a crash or a catch-up transfer.
- basis: text

### E31
- contract: The state machine must reflect a discarded prefix to durable storage in a form that can recover the current state, and it must tell Raft to drop that prefix only after that reflection is durable.
- source: §5 "the state machine reflects those entries to disk in a way that can recover the current system state."
- stated: stated
- violation: The state machine reports the prefix saved, Raft deletes the log entries, and the state machine's own durable copy is only a partial write.
- at-risk: The durability guarantee fails for every committed command in the discarded prefix, and a restart cannot rebuild them.
- detectable: partly — a checksum of the state machine's file catches some partial saves; a clean early acknowledgment does not.
- silent: 2 — the early acknowledgment is uncommon in a year and looks like a normal compaction.
- basis: text

### E32
- contract: Each client must use a unique client identifier and must resubmit an unacknowledged command with the same serial number rather than a new one.
- source: §6.3 "each client is given a unique identifier, and clients assign unique"
- stated: stated
- violation: A client times out, generates a new serial number or a new client id, and submits the same logical command again.
- at-risk: Linearizability fails: the command runs twice, which is the duplicate lock and the double increment in the dissertation.
- detectable: no — both executions commit and return success.
- silent: 4 — HTTP clients and job runners routinely retry with a fresh request id, and the extra apply looks like a normal success.
- basis: text

### E33
- contract: A client that is told its session is unknown must not register a new session and replay a command whose earlier outcome is uncertain.
- source: §6.3 "this would risk duplicate execution of"
- stated: stated
- violation: The session has expired, the client treats the error as "register again and retry the same write," and the write had already committed before the expiry.
- at-risk: Linearizability fails by a second execution of a command the client intended once; the dissertation adopts a crash of the client here because a retry is unsafe.
- detectable: no — the new session's command is a normal committed entry.
- silent: 3 — reconnect-and-retry is a common client reaction to an unknown-session error and returns success.
- basis: text

### E34
- contract: A live client must send keep-alives often enough that the deterministic expiry rule does not drop its session during ordinary idle periods.
- source: §6.3 "Live clients issue keep-alive requests during periods of inactivity, which are also augmented with"
- stated: stated
- violation: A client stays idle longer than the session lifetime and then submits a new command on the expired session.
- at-risk: That client's availability fails if the server returns an error, and linearizability fails if the client then takes the new-session path in E33.
- detectable: yes — a server that follows the dissertation returns an error for the unknown session, which the client can see.
- silent: 2 — idle clients miss the window occasionally; the next call usually surfaces an error, so fully silent cases are the ones that never call again.
- basis: text

### E35
- contract: The leader clock recorded into log entries for session expiry must move forward closely enough that live keep-alives still fall inside the expiry window and idle sessions do eventually expire.
- source: §6.3 "the leader augments each command that it appends to"
- stated: implicit
- violation: The leader's clock jumps forward by more than the session lifetime between two commands, and every live session is expired by the deterministic rule.
- at-risk: I am unsure this breaks State Machine Safety, because every server expires the same sessions from the log; it does break client availability, and it breaks exactly-once if those clients register again and replay, as in E33.
- detectable: partly — a bound check on the logged timestamp would see the jump, and nothing in the algorithm requires that check.
- silent: 2 — a step large enough to mass-expire sessions is uncommon over a year and is not reported as a session fault.
- basis: text

### E36
- contract: A client that loses the leader must try another server instead of waiting indefinitely on the last leader it knew.
- source: §6.2 "simply retry with a random server. Insisting on being able to contact the last known leader"
- stated: stated
- violation: The client keeps reconnecting only to a leader that has crashed or been partitioned, while another server is leader and could serve the call.
- at-risk: The availability guarantee fails for that client even though a majority is healthy and has elected a leader.
- detectable: no — the cluster does not observe that this client refused to fail over; the client sees its own timeouts.
- silent: 2 — pinned-leader clients show up occasionally, and the operator sees no cluster error, only a client-side timeout.
- basis: text

### E37
- contract: If servers stamp replies with the applied log index so that one client never reads backward, the client must present the greatest index it has already seen.
- source: §6.4.1 "Clients would track the latest index corresponding to"
- stated: stated
- violation: The client drops the index it was given and accepts a later reply from a server that has applied only an older prefix.
- at-risk: The per-client monotonic-read guarantee fails. This is sequential consistency for one client, not the basic linearizable read path, and I am unsure it matters for deployments that do not enable the extension.
- detectable: no — the server still returns a successful older read when the client omits the index.
- silent: 2 — among deployments that enable the extension, clients that forget the index are occasional and the older read looks successful.
- basis: text

### E38
- contract: Automatic removal of failed servers must not shrink the cluster below the fault tolerance the operator required.
- source: §4.4 "it can be dangerous for the cluster to automatically remove failed servers, as it could then be left"
- stated: stated
- violation: A controller removes every unresponsive server until one or two members remain, and the desired replica count is five.
- at-risk: The guarantee that a five-server cluster tolerates two failures no longer holds; the next failure of the smaller cluster loses availability or, if a majority of the remainder then loses disks, durability.
- detectable: partly — the implementation can compare the committed configuration to a configured target size, and a successful removal is not itself an error.
- silent: 3 — aggressive replacement controllers do this kind of shrink on real clusters over a year and report the smaller cluster as healthy.
- basis: text

### E39
- contract: A replacement that must keep tolerating a failure throughout has to add the new server before it removes the old one.
- source: §4.4 "adding one server and then removing the other allows the system to handle one server failure at all"
- stated: stated
- violation: In a three-server cluster the operator removes one server first, leaving a two-server cluster that needs both survivors for every commit.
- at-risk: Availability under one fault fails for the whole window; one more crash leaves no majority, so the cluster cannot commit.
- detectable: partly — the configuration size is visible in the log, and the remove call itself succeeds with no error.
- silent: 3 — remove-then-add is a common manual sequence and is silent whenever nothing else fails during the window.
- basis: text

### E40
- contract: Cluster creation must start from one server whose log contains a singleton configuration, and every other process must start with an empty log and join by a membership change; a static configuration file, if used instead, must name the same member set on every server.
- source: §4.4 "This configuration lists only that one"
- stated: stated
- violation: Two processes are each bootstrapped as the sole member, or two servers' static files list overlapping sets that can each form a majority.
- at-risk: Election Safety fails: each singleton commits as its own leader, or the two static majorities elect two leaders for one term.
- detectable: partly — each side looks healthy alone; only a client that can see both histories, or a human comparing files, notices.
- silent: 2 — double bootstrap is a bring-up mistake rather than a weekly event, and each side serves reads and writes without an error.
- basis: text

### E41
- contract: The host must provide the extra memory concurrent snapshotting needs, and an out-of-memory condition must stop the server cleanly instead of continuing with a corrupted address space.
- source: §5.1.1 "Servers require additional memory for snapshotting concurrently, which should be planned for"
- stated: stated
- violation: Copy-on-write during a snapshot exhausts RAM and the process keeps running after the allocator or the kernel has corrupted its state.
- at-risk: If the process is simply killed, that is an ordinary stop and safety holds; if it keeps sending messages from corrupted memory, Election Safety and State Machine Safety fail as in E1.
- detectable: yes — allocation failure and the out-of-memory killer are visible to the operator.
- silent: 1 — memory exhaustion almost always ends in a logged failure or a dead process.
- basis: text

### E42
- contract: When the operating system supplies the snapshot by fork or by a copy-on-write disk device, that image must be a stable point-in-time copy, and the forked child must not itself vote or answer clients.
- source: §5.1.1 "to make a copy of the server’s entire address space. Then, the child process can write out the"
- stated: implicit
- violation: The child continues the parent's Raft threads and accepts RPCs, or the copy-on-write device returns a mix of blocks from before and after later writes.
- at-risk: A second voting child breaks Election Safety the same way as a cloned process; a mixed disk image breaks State Machine Safety on any follower that installs it.
- detectable: partly — a parent that expects the child to exit can notice that it did not; a mixed block device does not announce itself.
- silent: 1 — a child that remains a second cluster member is rare over a year of ordinary operation.
- basis: text

### E43
- contract: Each state-machine command on an operational server must finish, so a committed entry can be applied and its result returned.
- source: §3.5 "entry to its state machine and returns the result of that execution to the client."
- stated: implicit
- violation: A command deadlocks or loops forever inside the state machine, and the apply thread never reaches the next committed index.
- at-risk: The guarantee that committed entries are eventually executed on the available state machines fails, and availability fails for every later command.
- detectable: yes — the leader's commit index moves and the applied index does not, which clients observe as timeouts.
- silent: 2 — a wedged apply is occasional over a year and is often visible only as client timeouts rather than as a named error.
- basis: text

## Recognised

- E4 and E5 are the contracts behind restoring a data directory or a VM disk onto a member that still has its old identity, including restoring a snapshot beside a live peer; I recall this class from etcd operator incidents and from Hashicorp Raft deployments, and the dissertation already states both contracts.
- E6, E7, and E8 are the contracts behind lost votes and lost log tails when a flush is not power-fail durable; I recall the Linux fsync-error discussions and etcd's warnings about disks that do not actually persist a flush, and Table 10.1 turns write caching off.
- E23 is the contract behind stale reads when a leader lease outruns follower clocks; I recall the same failure mode from CockroachDB clock-offset incidents, and the dissertation states it directly.
- E24, E26, and E27 are the contracts behind divergent replicas and double applies in application state machines, including session state dropped at snapshot time; I have seen that class in services built on Raft, and the dissertation states each piece.
- E32 and E33 are the contracts behind Figure 6.2; retries that mint a new request id are the usual client bug I recall in services on etcd and on custom Raft libraries.
- E19 and E22 are the contracts behind leader flapping when fsync or a garbage-collection pause exceeds the election timeout; I recall that pattern on JVM and cloud deployments.
- The stale read-only queries Jepsen found in two Raft implementations, which §6.4 cites, were implementations skipping the confirming-heartbeat read rule, so I did not enter them as an environment contract.

## Algorithm limits

These are limits of the algorithm's own rules, not environment contracts. A leader that crashes over and over before it commits an entry from its current term can append an entry each time and grow the log without a matching client workload; §11.3 and the acknowledgments both say storage can be exhausted that way. The safety proof and the TLA+ specification cover the basic algorithm only; §8.4 leaves membership, log compaction, client interaction, liveness, and availability unproved, and Appendix B says the written proof may contain errors. David Mazières's Figure 3.7 scenario was a bug in an earlier commitment rule; the rule in this text is the repair. Ezra Hoch's membership liveness report is described as a bug in an earlier design; I cannot tell from this text whether a liveness hole remains in Chapter 4.

## Could not decide

- Clock leases (§6.4.1) and the per-client monotonic index are optional, and the dissertation advises against leases unless performance requires them. I included E23 and E37 because the text states the obligations, and I marked them as applying when the extension is enabled.
- "Persist before you answer" is a rule of the server. I treated the disk's behavior after it confirms a flush as the environment contract (E6, E7, E8) and did not list the call site as an environment contract.
- The timing inequality in the source file is stored with byte 0x1c where the printed page has a much-less-than sign. The prose in §3.9 is what I quoted.
- E8's silent score is a judgment about a standing condition (a cache that acknowledges early) rather than about how often power is lost. I scored it 3.
- I did not find a defect in the rules as published in this text beyond the space bound under unbounded leader churn, which the dissertation already states.

## Checkout

Contracts: 43.

`ls -R` in the checkout:

```
/home/tony/projects/tupay-d1-enum-grok-1:
AGENTS.md
BRIEF.md
enumeration.md
source

/home/tony/projects/tupay-d1-enum-grok-1/source:
OngaroPhD.pdf
OngaroPhD.txt
```

`git status` in the checkout:

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
