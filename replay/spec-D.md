# Specification D: the design as published

This is the design you are to build, exactly as written. It is not a contract you may satisfy by any design you like: where this specification says how something is done, do it that way, even if you believe another way is better. If you find a place where you think the design is wrong, do not fix it; record it in your README as an interpretation or a concern, and build what is written. Where the specification is silent, choose, and record the choice.

## Source
The design below is quoted from Diego Ongaro, *Consensus: Bridging Theory and Practice*, PhD dissertation, Stanford University, 2014 (https://web.stanford.edu/~ouster/cgi-bin/papers/OngaroPhD.pdf): chapter 3's Figure 3.1 and sections 3.3 to 3.8 (the basic algorithm), and chapter 4's introduction, Figure 4.1 and section 4.1 (single-server membership changes). The text is extracted with `pdftotext` and reproduced as extracted, including page headers; figures other than Figures 3.1 and 4.1 are images and are not reproduced, so references to them can be ignored; Figures 3.1 and 4.1 are transcribed. Build what this text describes, with the vocabulary it uses. Where it refers to sections not reproduced here (for example §6.2, client interaction, or §4.2, availability), those mechanisms are not part of what you build, except that a coordinator that removes itself steps down after the change is committed, as Figure 4.1 (RemoveServer, step 4) says. The contract you build to is `replay/contract.md`; its terms map onto this text as: member = server, epoch = term, coordinator = leader, journal = log, configuration = configuration.

## Figure 3.1 (transcribed)

Transcribed by the third steward from the rendered page (dissertation page 13, PDF page 31), because the figure is not extractable as text. Wording, order and section references are the figure's.

### State
**Persistent state on all servers:** (Updated on stable storage before responding to RPCs)
- currentTerm: latest term server has seen (initialized to 0 on first boot, increases monotonically)
- votedFor: candidateId that received vote in current term (or null if none)
- log[]: log entries; each entry contains command for state machine, and term when entry was received by leader (first index is 1)

**Volatile state on all servers:**
- commitIndex: index of highest log entry known to be committed (initialized to 0, increases monotonically)
- lastApplied: index of highest log entry applied to state machine (initialized to 0, increases monotonically)

**Volatile state on leaders:** (Reinitialized after election)
- nextIndex[]: for each server, index of the next log entry to send to that server (initialized to leader last log index + 1)
- matchIndex[]: for each server, index of highest log entry known to be replicated on server (initialized to 0, increases monotonically)

### AppendEntries RPC
Invoked by leader to replicate log entries (§3.5); also used as heartbeat (§3.4).
Arguments:
- term: leader's term
- leaderId: so follower can redirect clients
- prevLogIndex: index of log entry immediately preceding new ones
- prevLogTerm: term of prevLogIndex entry
- entries[]: log entries to store (empty for heartbeat; may send more than one for efficiency)
- leaderCommit: leader's commitIndex
Results:
- term: currentTerm, for leader to update itself
- success: true if follower contained entry matching prevLogIndex and prevLogTerm
Receiver implementation:
1. Reply false if term < currentTerm (§3.3)
2. Reply false if log doesn't contain an entry at prevLogIndex whose term matches prevLogTerm (§3.5)
3. If an existing entry conflicts with a new one (same index but different terms), delete the existing entry and all that follow it (§3.5)
4. Append any new entries not already in the log
5. If leaderCommit > commitIndex, set commitIndex = min(leaderCommit, index of last new entry)

### RequestVote RPC
Invoked by candidates to gather votes (§3.4).
Arguments:
- term: candidate's term
- candidateId: candidate requesting vote
- lastLogIndex: index of candidate's last log entry (§3.6)
- lastLogTerm: term of candidate's last log entry (§3.6)
Results:
- term: currentTerm, for candidate to update itself
- voteGranted: true means candidate received vote
Receiver implementation:
1. Reply false if term < currentTerm (§3.3)
2. If votedFor is null or candidateId, and candidate's log is at least as up-to-date as receiver's log, grant vote (§3.4, §3.6)

### Rules for Servers
All Servers:
- If commitIndex > lastApplied: increment lastApplied, apply log[lastApplied] to state machine (§3.5)
- If RPC request or response contains term T > currentTerm: set currentTerm = T, convert to follower (§3.3)

Followers (§3.4):
- Respond to RPCs from candidates and leaders
- If election timeout elapses without receiving AppendEntries RPC from current leader or granting vote to candidate: convert to candidate

Candidates (§3.4):
- On conversion to candidate, start election:
  - Increment currentTerm
  - Vote for self
  - Reset election timer
  - Send RequestVote RPCs to all other servers
- If votes received from majority of servers: become leader
- If AppendEntries RPC received from new leader: convert to follower
- If election timeout elapses: start new election

Leaders:
- Upon election: send initial empty AppendEntries RPC (heartbeat) to each server; repeat during idle periods to prevent election timeouts (§3.4)
- If command received from client: append entry to local log, respond after entry applied to state machine (§3.5)
- If last log index ≥ nextIndex for a follower: send AppendEntries RPC with log entries starting at nextIndex
  - If successful: update nextIndex and matchIndex for follower (§3.5)
  - If AppendEntries fails because of log inconsistency: decrement nextIndex and retry (§3.5)
- If there exists an N such that N > commitIndex, a majority of matchIndex[i] ≥ N, and log[N].term == currentTerm: set commitIndex = N (§3.5, §3.6).

Figure 3.1: A condensed summary of the Raft consensus algorithm (excluding membership changes, log compaction, and client interaction). The server behavior in the lower-right box is described as a set of rules that trigger independently and repeatedly. Section numbers such as §3.4 indicate where particular features are discussed. The formal specification in Appendix B describes the algorithm more precisely.

## Chapter 3, sections 3.3 to 3.8 (verbatim extraction)

```text
3.3     Raft basics

A Raft cluster contains several servers; five is a typical number, which allows the system to tolerate
two failures. At any given time each server is in one of three states: leader, follower, or candidate.
In normal operation there is exactly one leader and all of the other servers are followers. Followers
are passive: they issue no requests on their own but simply respond to requests from leaders and can-
didates. The leader handles all client requests (if a client contacts a follower, the follower redirects
it to the leader). The third state, candidate, is used to elect a new leader as described in Section 3.4.
Figure 3.3 shows the states and their transitions; the transitions are discussed below.
     Raft divides time into terms of arbitrary length, as shown in Figure 3.4. Terms are numbered
with consecutive integers. Each term begins with an election, in which one or more candidates
attempt to become leader as described in Section 3.4. If a candidate wins the election, then it serves
as leader for the rest of the term. In some situations an election will result in a split vote. In this case
CHAPTER 3. BASIC RAFT ALGORITHM                                                                     15

  Figure 3.3: Server states. Followers only respond to requests from other servers. If a follower
  receives no communication, it becomes a candidate and initiates an election. A candidate that
  receives votes from a majority of the full cluster becomes the new leader. Leaders typically
  operate until they fail.

  Figure 3.4: Time is divided into terms, and each term begins with an election. After a successful
  election, a single leader manages the cluster until the end of the term. Some elections fail, in
  which case the term ends without choosing a leader. The transitions between terms may be
  observed at different times on different servers.

the term will end with no leader; a new term (with a new election) will begin shortly. Raft ensures
that there is at most one leader in a given term.

    Different servers may observe the transitions between terms at different times, and in some situ-
ations a server may not observe an election or even entire terms. Terms act as a logical clock [47] in
Raft, and they allow servers to detect obsolete information such as stale leaders. Each server stores a
current term number, which increases monotonically over time. Current terms are exchanged when-
ever servers communicate; if one server’s current term is smaller than the other’s, then it updates
its current term to the larger value. If a candidate or leader discovers that its term is out of date,
it immediately reverts to follower state. If a server receives a request with a stale term number, it
rejects the request.
16                                                       CHAPTER 3. BASIC RAFT ALGORITHM

     Raft servers communicate using remote procedure calls (RPCs), and the basic consensus algo-
rithm requires only two types of RPCs between servers. RequestVote RPCs are initiated by candi-
dates during elections (Section 3.4), and AppendEntries RPCs are initiated by leaders to replicate
log entries and to provide a form of heartbeat (Section 3.5). Leadership transfer (Section 3.10) and
the mechanisms described in subsequent chapters introduce additional RPCs beyond the two in the
core consensus algorithm.
     We chose to structure communication in Raft as RPCs to simplify its communication patterns.
Each request type has a corresponding response type, which also serves as the request’s acknowl-
edgment. Raft assumes RPC requests and responses may be lost in the network; it is the requester’s
responsibility to retry the RPC if it does not receive a response in a timely manner. Servers issue
RPCs in parallel for best performance, and Raft does not assume the network preserves ordering
between RPCs.

3.4     Leader election

Raft uses a heartbeat mechanism to trigger leader election. When servers start up, they begin as
followers. A server remains in follower state as long as it receives valid RPCs from a leader or
candidate. Leaders send periodic heartbeats (AppendEntries RPCs that carry no log entries) to all
followers in order to maintain their authority. If a follower receives no communication over a period
of time called the election timeout, then it assumes there is no viable leader and begins an election
to choose a new leader.
     To begin an election, a follower increments its current term and transitions to candidate state.
It then votes for itself and issues RequestVote RPCs in parallel to each of the other servers in the
cluster. A candidate continues in this state until one of three things happens: (a) it wins the election,
(b) another server establishes itself as leader, or (c) another election timeout goes by with no winner.
These outcomes are discussed separately in the paragraphs below.
     A candidate wins an election if it receives votes from a majority of the servers in the full cluster
for the same term. Each server will vote for at most one candidate in a given term, on a first-
come-first-served basis (note: Section 3.6 adds an additional restriction on votes). The majority rule
ensures that at most one candidate can win the election for a particular term (the Election Safety
Property in Figure 3.2). Once a candidate wins an election, it becomes leader. It then sends heartbeat
messages to all of the other servers to establish its authority and prevent new elections.
     While waiting for votes, a candidate may receive an AppendEntries RPC from another server
CHAPTER 3. BASIC RAFT ALGORITHM                                                                       17

claiming to be leader. If the leader’s term (included in its RPC) is at least as large as the candidate’s
current term, then the candidate recognizes the leader as legitimate and returns to follower state. If
the term in the RPC is smaller than the candidate’s current term, then the candidate rejects the RPC
and continues in candidate state.
    The third possible outcome is that a candidate neither wins nor loses the election: if many
followers become candidates at the same time, votes could be split so that no candidate obtains a
majority. When this happens, each candidate will time out and start a new election by incrementing
its term and initiating another round of RequestVote RPCs. However, without extra measures split
votes could repeat indefinitely.
    Raft uses randomized election timeouts to ensure that split votes are rare and that they are
resolved quickly. To prevent split votes in the first place, election timeouts are chosen randomly
from a fixed interval (e.g., 150–300 ms). This spreads out the servers so that in most cases only
a single server will time out; it wins the election and sends heartbeats before any other servers
time out. The same mechanism is used to handle split votes. Each candidate restarts its randomized
election timeout at the start of an election, and it waits for that timeout to elapse before starting the
next election; this reduces the likelihood of another split vote in the new election. Chapter 9 shows
that this approach elects a leader rapidly.
    Elections are an example of how understandability guided our choice between design alter-
natives. Initially we planned to use a ranking system: each candidate was assigned a unique rank,
which was used to select between competing candidates. If a candidate discovered another candidate
with higher rank, it would return to follower state so that the higher ranking candidate could more
easily win the next election. We found that this approach created subtle issues around availability (a
lower-ranked server might need to time out and become a candidate again if a higher-ranked server
fails, but if it does so too soon, it can reset progress towards electing a leader). We made adjustments
to the algorithm several times, but after each adjustment new corner cases appeared. Eventually we
concluded that the randomized retry approach is more obvious and understandable.

3.5    Log replication

Once a leader has been elected, it begins servicing client requests. Each client request contains a
command to be executed by the replicated state machine. The leader appends the command to its log
as a new entry, then issues AppendEntries RPCs in parallel to each of the other servers to replicate
the entry. When the entry has been safely replicated (as described below), the leader applies the
18                                                        CHAPTER 3. BASIC RAFT ALGORITHM

  Figure 3.5: Logs are composed of entries, which are numbered sequentially. Each entry con-
  tains the term in which it was created (the number in each box) and a command for the state
  machine. An entry is considered committed if it is safe for that entry to be applied to state
  machines.

entry to its state machine and returns the result of that execution to the client. If followers crash or
run slowly, or if network packets are lost, the leader retries AppendEntries RPCs indefinitely (even
after it has responded to the client) until all followers eventually store all log entries.
     Logs are organized as shown in Figure 3.5. Each log entry stores a state machine command along
with the term number when the entry was received by the leader. The term numbers in log entries
are used to detect inconsistencies between logs and to ensure some of the properties in Figure 3.2.
Each log entry also has an integer index identifying its position in the log.
     The leader decides when it is safe to apply a log entry to the state machines; such an entry is
called committed. Raft guarantees that committed entries are durable and will eventually be exe-
cuted by all of the available state machines. A log entry is committed once the leader that created
the entry has replicated it on a majority of the servers (e.g., entry 7 in Figure 3.5). This also commits
all preceding entries in the leader’s log, including entries created by previous leaders. Section 3.6
discusses some subtleties when applying this rule after leader changes, and it also shows that this
definition of commitment is safe. The leader keeps track of the highest index it knows to be com-
mitted, and it includes that index in future AppendEntries RPCs (including heartbeats) so that the
other servers eventually find out. Once a follower learns that a log entry is committed, it applies the
entry to its local state machine (in log order).
CHAPTER 3. BASIC RAFT ALGORITHM                                                                      19

    We designed the Raft log mechanism to maintain a high level of coherency between the logs on
different servers. Not only does this simplify the system’s behavior and make it more predictable,
but it is an important component of ensuring safety. Raft maintains the following properties, which
together constitute the Log Matching Property in Figure 3.2:
   • If two entries in different logs have the same index and term, then they store the same com-
      mand.
   • If two entries in different logs have the same index and term, then the logs are identical in all
      preceding entries.
    The first property follows from the fact that a leader creates at most one entry with a given log
index in a given term, and log entries never change their position in the log. The second property is
guaranteed by a consistency check performed by AppendEntries. When sending an AppendEntries
RPC, the leader includes the index and term of the entry in its log that immediately precedes the
new entries. If the follower does not find an entry in its log with the same index and term, then it
refuses the new entries. The consistency check acts as an induction step: the initial empty state of
the logs satisfies the Log Matching Property, and the consistency check preserves the Log Matching
Property whenever logs are extended. As a result, whenever AppendEntries returns successfully, the
leader knows that the follower’s log is identical to its own log up through the new entries.
    During normal operation, the logs of the leader and followers stay consistent, so the Append-
Entries consistency check never fails. However, leader crashes can leave the logs inconsistent (the
old leader may not have fully replicated all of the entries in its log). These inconsistencies can
compound over a series of leader and follower crashes. Figure 3.6 illustrates the ways in which
followers’ logs may differ from that of a new leader. A follower may be missing entries that are
present on the leader, it may have extra entries that are not present on the leader, or both. Missing
and extraneous entries in a log may span multiple terms.
    In Raft, the leader handles inconsistencies by forcing the followers’ logs to duplicate its own.
This means that conflicting entries in follower logs will be overwritten with entries from the leader’s
log. Section 3.6 will show that this is safe when coupled with a restriction on elections.
    To bring a follower’s log into consistency with its own, the leader must find the latest log entry
where the two logs agree, delete any entries in the follower’s log after that point, and send the
follower all of the leader’s entries after that point. All of these actions happen in response to the
consistency check performed by AppendEntries RPCs. The leader maintains a nextIndex for each
follower, which is the index of the next log entry the leader will send to that follower. When a
leader first comes to power, it initializes all nextIndex values to the index just after the last one in
20                                                   CHAPTER 3. BASIC RAFT ALGORITHM

 Figure 3.6: When the leader at the top comes to power, it is possible that any of scenarios (a–f)
 could occur in follower logs. Each box represents one log entry; the number in the box is its
 term. A follower may be missing entries (a–b), may have extra uncommitted entries (c–d), or
 both (e–f). For example, scenario (f) could occur if that server was the leader for term 2, added
 several entries to its log, then crashed before committing any of them; it restarted quickly,
 became leader for term 3, and added a few more entries to its log; before any of the entries
 in either term 2 or term 3 were committed, the server crashed again and remained down for
 several terms.
CHAPTER 3. BASIC RAFT ALGORITHM                                                                      21

its log (11 in Figure 3.6). If a follower’s log is inconsistent with the leader’s, the AppendEntries
consistency check will fail in the next AppendEntries RPC. After a rejection, the leader decrements
the follower’s nextIndex and retries the AppendEntries RPC. Eventually the nextIndex will reach a
point where the leader and follower logs match. When this happens, AppendEntries will succeed,
which removes any conflicting entries in the follower’s log and appends entries from the leader’s
log (if any). Once AppendEntries succeeds, the follower’s log is consistent with the leader’s, and it
will remain that way for the rest of the term.

    Until the leader has discovered where it and the follower’s logs match, the leader can send
AppendEntries with no entries (like heartbeats) to save bandwidth. Then, once the matchIndex im-
mediately precedes the nextIndex, the leader should begin to send the actual entries.

    If desired, the protocol can be optimized to reduce the number of rejected AppendEntries RPCs.
For example, when rejecting an AppendEntries request, the follower can include the term of the
conflicting entry and the first index it stores for that term. With this information, the leader can
decrement nextIndex to bypass all of the conflicting entries in that term; one AppendEntries RPC
will be required for each term with conflicting entries, rather than one RPC per entry. Alternatively,
the leader can use a binary search approach to find the first entry where the follower’s log differs
from its own; this has better worst-case behavior. In practice, we doubt these optimizations are
necessary, since failures happen infrequently and it is unlikely that there will be many inconsistent
entries.

    With this mechanism, a leader does not need to take any special actions to restore log consistency
when it comes to power. It just begins normal operation, and the logs automatically converge in
response to failures of the AppendEntries consistency check. A leader never overwrites or deletes
entries in its own log (the Leader Append-Only Property in Figure 3.2).

    This log replication mechanism exhibits the desirable consensus properties described in Sec-
tion 2.1: Raft can accept, replicate, and apply new log entries as long as a majority of the servers are
up; in the normal case a new entry can be replicated with a single round of RPCs to a majority of
the cluster; and a single slow follower will not impact performance. The log replication algorithm
is also practical to implement, since AppendEntries requests are manageable in size (leaders never
need to send more than one entry in a single AppendEntries request to make progress). Some other
consensus algorithms are described as sending entire logs over the network; this places a burden on
the implementer to develop optimizations required for a practical implementation.
22                                                       CHAPTER 3. BASIC RAFT ALGORITHM

3.6     Safety

The previous sections described how Raft elects leaders and replicates log entries. However, the
mechanisms described so far are not quite sufficient to ensure that each state machine executes
exactly the same commands in the same order. For example, a follower might be unavailable while
the leader commits several log entries, then it could be elected leader and overwrite these entries
with new ones; as a result, different state machines might execute different command sequences.
     This section completes the Raft algorithm by adding a restriction on which servers may be
elected leader. The restriction ensures that the leader for any given term contains all of the entries
committed in previous terms (the Leader Completeness Property from Figure 3.2). Given the elec-
tion restriction, we then make the rules for commitment more precise. Finally, we present a proof
sketch for the Leader Completeness Property and show how it leads to correct behavior of the repli-
cated state machine.

3.6.1    Election restriction

In any leader-based consensus algorithm, the leader must eventually store all of the committed
log entries. In some consensus algorithms, such as Viewstamped Replication [66], a leader can be
elected even if it doesn’t initially contain all of the committed entries. These algorithms contain
additional mechanisms to identify the missing entries and transmit them to the new leader, either
during the election process or shortly afterwards. Unfortunately, this results in considerable addi-
tional mechanism and complexity. Raft uses a simpler approach where it guarantees that all the
committed entries from previous terms are present on each new leader from the moment of its elec-
tion, without the need to transfer those entries to the leader. This means that log entries only flow in
one direction, from leaders to followers, and leaders never overwrite existing entries in their logs.
     Raft uses the voting process to prevent a candidate from winning an election unless its log con-
tains all committed entries. A candidate must contact a majority of the cluster in order to be elected,
which means that every committed entry must be present in at least one of those servers. If the can-
didate’s log is at least as up-to-date as any other log in that majority (where “up-to-date” is defined
precisely below), then it will hold all the committed entries. The RequestVote RPC implements this
restriction: the RPC includes information about the candidate’s log, and the voter denies its vote if
its own log is more up-to-date than that of the candidate.
     Raft determines which of two logs is more up-to-date by comparing the index and term of the
last entries in the logs. If the logs have last entries with different terms, then the log with the later
CHAPTER 3. BASIC RAFT ALGORITHM                                                                    23

 Figure 3.7: A time sequence showing why a leader cannot determine commitment using log
 entries from older terms. In (a) S1 is leader and partially replicates the log entry at index 2. In
 (b) S1 crashes; S5 is elected leader for term 3 with votes from S3, S4, and itself, and accepts
 a different entry at log index 2. In (c) S5 crashes; S1 restarts, is elected leader, and continues
 replication. At this point, the log entry from term 2 has been replicated on a majority of the
 servers, but it is not committed. If S1 crashes as in (d1), S5 could be elected leader (with votes
 from S2, S3, and S4) and overwrite the entry with its own entry from term 3. However, if S1
 replicates an entry from its current term on a majority of the servers before crashing, as in (d2),
 then this entry is committed (S5 cannot win an election). At this point all preceding entries in
 the log are committed as well.
24                                                     CHAPTER 3. BASIC RAFT ALGORITHM

term is more up-to-date. If the logs end with the same term, then whichever log is longer is more
up-to-date.

3.6.2    Committing entries from previous terms

As described in Section 3.5, a leader knows that an entry from its current term is committed once
that entry is stored on a majority of the servers. If a leader crashes before committing an entry,
future leaders will attempt to finish replicating the entry. However, a leader cannot immediately
conclude that an entry from a previous term is committed once it is stored on a majority of servers.
Figure 3.7 illustrates a situation where an old log entry is stored on a majority of servers, yet can
still be overwritten by a future leader.
     To eliminate problems like the one in Figure 3.7, Raft never commits log entries from previ-
ous terms by counting replicas. Only log entries from the leader’s current term are committed by
counting replicas; once an entry from the current term has been committed in this way, then all prior
entries are committed indirectly because of the Log Matching Property. There are some situations
where a leader could safely conclude that an older log entry is committed (for example, if that entry
is stored on every server), but Raft takes a more conservative approach for simplicity.
     Raft incurs this extra complexity in the commitment rules because log entries retain their orig-
inal term numbers when a leader replicates entries from previous terms. In other consensus algo-
rithms, if a new leader re-replicates entries from prior “terms”, it must do so with its new “term
number”. Raft’s approach makes it easier to reason about log entries, since they maintain the same
term number over time and across logs. In addition, new leaders in Raft send fewer log entries from
previous terms than in other algorithms, since other algorithms must send redundant log entries to
renumber them before they can be committed; however, this may not be very important in practice,
since leader changes should be rare.

3.6.3    Safety argument

Given the complete Raft algorithm, we can now argue more precisely that the Leader Completeness
Property holds (this argument is based on the safety proof; see Chapter 8). We assume that the
Leader Completeness Property does not hold, then we prove a contradiction. Suppose the leader for
term T (leaderT ) commits a log entry from its term, but that log entry is not stored by the leader of
some future term. Consider the smallest term U > T whose leader (leaderU ) does not store the entry.

     1. The committed entry must have been absent from leaderU ’s log at the time of its election
CHAPTER 3. BASIC RAFT ALGORITHM                                                                       25

 Figure 3.8: If S1 (leader for term T) commits a new log entry from its term, and S5 is elected
 leader for a later term U, then there must be at least one server (S3) that accepted the log entry
 and also voted for S5.

     (leaders never delete or overwrite entries).

  2. leaderT replicated the entry on a majority of the cluster, and leaderU received votes from a
     majority of the cluster. Thus, at least one server (“the voter”) both accepted the entry from
     leaderT and voted for leaderU , as shown in Figure 3.8. The voter is key to reaching a contra-
     diction.

  3. The voter must have accepted the committed entry from leaderT before voting for leaderU ;
     otherwise it would have rejected the AppendEntries request from leaderT (its current term
     would have been higher than T).

  4. The voter still stored the entry when it voted for leaderU , since every intervening leader con-
     tained the entry (by assumption), leaders never remove entries, and followers only remove
     entries if they conflict with the leader.

  5. The voter granted its vote to leaderU , so leaderU ’s log must have been as up-to-date as the
     voter’s. This leads to one of two contradictions.

  6. First, if the voter and leaderU shared the same last log term, then leaderU ’s log must have
     been at least as long as the voter’s, so its log contained every entry in the voter’s log. This is a
     contradiction, since the voter contained the committed entry and leaderU was assumed not to.

  7. Otherwise, leaderU ’s last log term must have been larger than the voter’s. Moreover, it was
     larger than T, since the voter’s last log term was at least T (it contains the committed entry
     from term T). The earlier leader that created leaderU ’s last log entry must have contained the
26                                                      CHAPTER 3. BASIC RAFT ALGORITHM

        committed entry in its log (by assumption). Then, by the Log Matching Property, leaderU ’s
        log must also contain the committed entry, which is a contradiction.

     8. This completes the contradiction. Thus, the leaders of all terms greater than T must contain
        all entries from term T that are committed in term T.

     9. The Log Matching Property guarantees that future leaders will also contain entries that are
        committed indirectly, such as index 2 in Figure 3.7(d2).

     Given the Leader Completeness Property, we can prove the State Machine Safety Property from
Figure 3.2, which states that if a server has applied a log entry at a given index to its state machine,
no other server will ever apply a different log entry for the same index. At the time a server applies a
log entry to its state machine, its log must be identical to the leader’s log up through that entry, and
the entry must be committed. Now consider the lowest term in which any server applies a given log
index; the Leader Completeness Property guarantees that the leaders for all higher terms will store
that same log entry, so servers that apply the index in later terms will apply the same value. Thus,
the State Machine Safety Property holds.
     Finally, Raft requires servers to apply entries in log index order. Combined with the State Ma-
chine Safety Property, this means that all servers will apply exactly the same set of log entries to
their state machines, in the same order.

3.7      Follower and candidate crashes

Until this point we have focused on leader failures. Follower and candidate crashes are much sim-
pler to handle than leader crashes, and they are both handled in the same way. If a follower or
candidate crashes (or the network link between it and the leader fails), then future RequestVote and
AppendEntries RPCs sent to it will fail. Raft handles these failures by retrying indefinitely; if the
crashed server restarts, then the RPC will complete successfully. If a server crashes after completing
an RPC but before responding, then it will receive the same RPC again after it restarts. Raft RPCs
have the same effect if repeated, so this causes no harm. For example, if a follower receives an
AppendEntries request that includes log entries already present in its log, it ignores those entries in
the new request.
CHAPTER 3. BASIC RAFT ALGORITHM                                                                             27

3.8    Persisted state and server restarts

Raft servers must persist enough information to stable storage to survive server restarts safely. In
particular, each server persists its current term and vote; this is necessary to prevent the server from
voting twice in the same term or replacing log entries from a newer leader with those from a deposed
leader. Each server also persists new log entries before they are counted towards the entries’ com-
mitment; this prevents committed entries from being lost or “uncommitted” when servers restart.
    Other state variables are safe to lose on a restart, as they can all be recreated. The most interesting
example is the commit index, which can safely be reinitialized to zero on a restart. Even if every
server restarts at the same time, the commit index will only temporarily lag behind its true value.
Once a leader is elected and is able to commit a new entry, its commit index will advance, and it
will quickly propagate this commit index to its followers.
    The state machine can either be volatile or persistent. A volatile state machine must be recovered
after restarts by reapplying log entries (after applying the latest snapshot; see Chapter 5). A persis-
tent state machine, however, has already applied most entries after a restart; to avoid reapplying
them, its last applied index must also be persistent.
    If a server loses any of its persistent state, it cannot safely rejoin the cluster with its prior identity.
Such a server can usually be added back into the cluster with a new identity by invoking a cluster
membership change (see Chapter 4). If a majority of the cluster loses its persistent state, however,
log entries may be lost and progress on cluster membership changes will not be possible; to proceed,
a system administrator would need to admit the possibility of data loss.

```

## Chapter 4, introduction and section 4.1 (verbatim extraction)

```text
on understandability, we hope to have provided a solid foundation for implementers to adjust Raft
according to their experiences. Since Raft works in our testing environment, we expect these to be
straightforward extensions rather than fundamental changes.
Chapter 4

Cluster membership changes

Up until now we have assumed that the cluster configuration (the set of servers participating in the
consensus algorithm) is fixed. In practice, it will occasionally be necessary to change the configura-
tion, for example to replace servers when they fail or to change the degree of replication. This could
be done manually, using one of two approaches:

   • Configuration changes could be done by taking the entire cluster off-line, updating configu-
      ration files, and then restarting the cluster. However, this would leave the cluster unavailable
      during the changeover.

   • Alternatively, a new server could replace a cluster member by acquiring its network address.
      However, the administrator must guarantee that the replaced server will never come back up,
      or else the system would lose its safety properties (for example, there would be an extra vote).

Both of these approaches to membership changes have significant downsides, and if there are any
manual steps, they risk operator error.
    In order to avoid these issues, we decided to automate configuration changes and incorporate
them into the Raft consensus algorithm. Raft allows the cluster to continue operating normally
during changes, and membership changes can be implemented with only a few extensions to the
basic consensus algorithm. Figure 4.1 summarizes the RPCs used to change cluster membership,
whose elements are described in the remainder of this chapter.

                                                 32
CHAPTER 4. CLUSTER MEMBERSHIP CHANGES                                                               33

[Assembler's note: Figure 4.1 is an image here; its transcription is in the section "Figure 4.1 (transcribed)" below.]

  Figure 4.1: RPCs used to change cluster membership. The AddServer RPC is used to add a
  new server to the current configuration, and the RemoveServer RPC is used to remove a server
  from the current configuration. Section numbers such as §4.1 indicate where particular features
  are discussed. Section 4.4 discusses ways to use these RPCs in a complete system.

4.1        Safety

Preserving safety is the first challenge for configuration changes. For the mechanism to be safe, there
must be no point during the transition where it is possible for two leaders to be elected for the same
term. If a single configuration change adds or removes many servers, switching the cluster directly
from the old configuration to the new configuration can be unsafe; it isn’t possible to atomically
switch all of the servers at once, so the cluster can potentially split into two independent majorities
during the transition (see Figure 4.2).
     Most membership change algorithms introduce additional mechanism to deal with such prob-
lems. This is what we did for Raft initially, but we later discovered a simpler approach, which is to
disallow membership changes that could result in disjoint majorities. Thus, Raft restricts the types
of changes that are allowed: only one server can be added or removed from the cluster at a time.
More complex changes in membership are implemented as a series of single-server changes. Most
of this chapter describes the single-server approach, which is easier to understand than our original
approach. For completeness, Section 4.3 describes the original approach, which incurs additional
complexity to handle arbitrary configuration changes. We implemented the more complex approach
in LogCabin prior to discovering the simpler single-server change approach; it still uses the more
34                                              CHAPTER 4. CLUSTER MEMBERSHIP CHANGES

 Figure 4.2: Switching directly from one configuration to another can be unsafe because differ-
 ent servers will switch at different times. In this example, the cluster grows from three servers
 to five. Unfortunately, there is a point in time where two different leaders can be elected for the
 same term, one with a majority of the old configuration (Cold ) and another with a majority of
 the new configuration (Cnew ).

       (a) Adding one server to a 4-server cluster.      (b) Adding one server to a 3-server cluster.

     (c) Removing one server from a 5-server cluster. (d) Removing one server from a 4-server cluster.

 Figure 4.3: The addition and removal of a single server from an even- and an odd-sized cluster.
 In each figure, the blue rectangle shows a majority of the old cluster, and the red rectangle
 shows a majority of the new cluster. In every single-server membership change, an overlap
 between any majority of the old cluster and any majority of the new cluster is preserved, as
 needed for safety. For example in (b), a majority of the old cluster must include two of the left
 three servers, and a majority of the new cluster must include three of the servers in the new
 cluster, of which at least two must come from the old cluster.
CHAPTER 4. CLUSTER MEMBERSHIP CHANGES                                                                35

complex approach at the time of this writing.
    When adding a single server to a cluster or removing a single server from a cluster, any ma-
jority of the old cluster overlaps with any majority of the new cluster; see Figure 4.3. This overlap
prevents the cluster from splitting into two independent majorities; in terms of the safety argument
of Section 3.6.3, it guarantees the existence of “the voter”. Thus, when adding or removing just a
single server, it is safe to switch directly to the new configuration. Raft exploits this property to
change cluster membership safely using little additional mechanism.
    Cluster configurations are stored and communicated using special entries in the replicated log.
This leverages the existing mechanisms in Raft to replicate and persist configuration information.
It also allows the cluster to continue to service client requests while configuration changes are in
progress, by imposing ordering between configuration changes and client requests (while allowing
both to be replicated concurrently in a pipeline and/or in batches).
    When the leader receives a request to add or remove a server from its current configuration
(Cold ), it appends the new configuration (Cnew ) as an entry in its log and replicates that entry using
the normal Raft mechanism. The new configuration takes effect on each server as soon as it is added
to that server’s log: the Cnew entry is replicated to the Cnew servers, and a majority of the new
configuration is used to determine the Cnew entry’s commitment. This means that servers do not
wait for configuration entries to be committed, and each server always uses the latest configuration
found in its log.
    The configuration change is complete once the Cnew entry is committed. At this point, the leader
knows that a majority of the Cnew servers have adopted Cnew . It also knows that any servers that have
not moved to Cnew can no longer form a majority of the cluster, and servers without Cnew cannot be
elected leader. Commitment of Cnew allows three things to continue:

   1. The leader can acknowledge the successful completion of the configuration change.

   2. If the configuration change removed a server, that server can be shut down.

   3. Further configuration changes can be started. Before this point, overlapped configuration
      changes could degrade to unsafe situations like the one in Figure 4.2.

    As stated above, servers always use the latest configuration in their logs, regardless of whether
that configuration entry has been committed. This allows leaders to easily avoid overlapping config-
uration changes (the third item above), by not beginning a new change until the previous change’s
entry has committed. It is only safe to start another membership change once a majority of the old
36                                              CHAPTER 4. CLUSTER MEMBERSHIP CHANGES

cluster has moved to operating under the rules of Cnew . If servers adopted Cnew only when they
learned that Cnew was committed, Raft leaders would have a difficult time knowing when a major-
ity of the old cluster had adopted it. They would need to track which servers know of the entry’s
commitment, and the servers would need to persist their commit index to disk; neither of these
mechanisms is required in Raft. Instead, each server adopts Cnew as soon as that entry exists in its
log, and the leader knows it’s safe to allow further configuration changes as soon as the Cnew entry
has been committed. Unfortunately, this decision does imply that a log entry for a configuration
change can be removed (if leadership changes); in this case, a server must be prepared to fall back
to the previous configuration in its log.
     In Raft, it is the caller’s configuration that is used in reaching consensus, both for voting and for
log replication:

     • A server accepts AppendEntries requests from a leader that is not part of the server’s latest
       configuration. Otherwise, a new server could never be added to the cluster (it would never
       accept any log entries preceding the configuration entry that adds the server).

     • A server also grants its vote to a candidate that is not part of the server’s latest configuration (if
       the candidate has a sufficiently up-to-date log and a current term). This vote may occasionally
       be needed to keep the cluster available. For example, consider adding a fourth server to a
       three-server cluster. If one server were to fail, the new server’s vote would be needed to form
       a majority and elect a leader.

Thus, servers process incoming RPC requests without consulting their current configurations.

```

## Figure 4.1 (transcribed)

### AddServer RPC
Invoked by admin to add a server to the cluster configuration.
Arguments: newServer — address of server to add to configuration
Results: status — OK if server was added successfully; leaderHint — address of recent leader, if known
Receiver implementation:
1. Reply NOT_LEADER if not leader (§6.2)
2. Catch up new server for fixed number of rounds. Reply TIMEOUT if new server does not make progress for an election timeout or if the last round takes longer than the election timeout. (§4.2.1)
3. Wait until previous configuration in log is committed (§4.1)
4. Append new configuration entry to log (old configuration plus newServer), commit it using majority of new configuration (§4.1)
5. Reply OK

Assembler's note on step 2: if the new server's log already matches the leader's, catch-up is complete at once.

### RemoveServer RPC
Invoked by admin to remove a server from the cluster configuration.
Arguments: oldServer — address of server to remove from configuration
Results: status — OK if server was removed successfully; leaderHint — address of recent leader, if known
Receiver implementation:
1. Reply NOT_LEADER if not leader (§6.2)
2. Wait until previous configuration in log is committed (§4.1)
3. Append new configuration entry to log (old configuration without oldServer), commit it using majority of new configuration (§4.1)
4. Reply OK and, if this server was removed, step down (§4.2.2)

Figure 4.1: RPCs used to change cluster membership. The AddServer RPC is used to add a new server to the current configuration, and the RemoveServer RPC is used to remove a server from the current configuration. Section numbers such as §4.1 indicate where particular features are discussed. Section 4.4 discusses ways to use these RPCs in a complete system.

## What the design does not include
(This section, the opening paragraph and the Source note are the steward's, not the dissertation's.)
Client requests other than commands and configuration changes; reads; snapshots or journal compaction; non-voting members. A command is an opaque payload appended by the coordinator on request.
