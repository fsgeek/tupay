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
