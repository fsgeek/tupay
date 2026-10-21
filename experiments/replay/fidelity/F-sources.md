# Spec F: source of every statement in spec D

Steward-side; arm F authors never see this file or D. Written by the third steward on 2026-10-21 against `replay/spec-F.md` at `2b1a943`. The steward knows the bug; the auditor (Grok) does not. Each row quotes an **anchor**, a phrase that appears in `replay/spec-D.md` (search for it), or says **steward** when no passage of D says it. Status: **sourced** (D says it), **reading** (D implies it, and F resolves an ambiguity one way), **steward** (not in D; a disclosed choice), **flag** (F departs from D or adds salience D lacks).

| # | F statement (short) | Anchor in D | Status |
|---|---|---|---|
| 0 | Opening paragraph: build exactly as written; record concerns; where silent, choose | identical paragraph at the top of D | steward (the brief, same in both arms) |
| 1 | Member: a process storing a journal, named m1… | "member = server" (D's source note) | sourced |
| 2 | Journal: an **append-only** sequence of entries, indexed from 1 | "first index is 1"; but D also says "delete the existing entry and all that follow it" | **flag**: "append-only" is false; entries are deleted on conflict |
| 3 | Each entry carries the epoch in which it was first appended, and a payload | "term when entry was received by leader" | sourced |
| 4 | Payload is a command or a configuration | "Cluster configurations are stored and communicated using special entries in the replicated log" | sourced |
| 5 | Epoch: non-negative integer; only increases | "initialized to 0 on first boot, increases monotonically" | sourced |
| 6 | Coordinator: won an election for its epoch; others followers or candidates | "If a candidate wins the election, then it serves" | sourced |
| 7 | Configuration of a member = latest configuration entry, committed or not | "each server always uses the latest configuration found in its log" | sourced |
| 8 | …else the initial configuration it was started with | steward | steward (D does not say how a server starts) |
| 9 | Majority of C: more than half of C's members | steward | steward (D uses "majority" undefined) |
| 10 | Committed: once a coordinator applied the commitment rule to it or a later entry | "set commitIndex = N" (Fig 3.1); "Only log entries from the leader's current term are committed by" | sourced |
| 11 | Committed entries are never removed from any member's journal | Leader Completeness, D §3.6.3 | **flag**: F states as a fact of the design the property J1.2 tests and the bug violates; D argues it as a theorem in a proof section, with less salience |
| 12 | Durable: epoch, votedFor, journal | "Persistent state on all servers" | sourced |
| 13 | Volatile: role (follower on restart), commitIndex 0 on restart | "commitIndex … initialized to 0"; "When servers start up, they begin as" | sourced |
| 14 | Coordinator volatile: nextIndex, matchIndex | "Volatile state on leaders" | sourced |
| 15 | Every message carries sender's epoch; higher epoch → adopt it, clear votedFor, follower, before processing | "set currentTerm = T, convert to follower" | reading ("clear votedFor" follows from votedFor being "in current term") |
| 16 | Ignore a lower-epoch request, replying with own epoch | "Reply false if term < currentTerm"; "rejects the request" | sourced |
| 17 | **Members process incoming requests without consulting their own configuration** (bold) | "servers process incoming RPC requests without consulting their current configurations" | sourced; **flag**: bold not in D |
| 18 | …grant votes to, and accept extensions from, non-members | the two bullets before line 17's anchor | sourced |
| 19 | Election timeout random from a fixed range, anew each reset | "Raft uses randomized election timeouts" | sourced |
| 20 | Follower timer reset on extend from current coordinator or on granting a ballot | "without receiving AppendEntries RPC from current leader or granting vote" | sourced |
| 21 | Expired timer → candidate: increment epoch, vote self, ballot to every member of own configuration with last index and epoch | "Increment currentTerm"; "Vote for self"; "it is the caller's configuration that is used" | sourced; **flag**: omits "Reset election timer" on becoming candidate (Fig 3.1) |
| 22 | Grant if (a) epoch ≥ own, (b) not voted for another, (c) candidate at least as up to date (higher last epoch, or same and index ≥) | RequestVote "Receiver implementation"; "Raft determines which of two logs is more up-to-date" | sourced |
| 23 | Record votedFor durably before replying | "Updated on stable storage before responding to RPCs" | sourced |
| 24 | Majority of own configuration (counting itself if a member) → coordinator | "If votes received from majority of servers"; "the caller's configuration" | reading ("counting itself if a member": D does not reproduce §4.2.2) |
| 25 | Candidate hearing a coordinator of epoch ≥ own → follower | "the candidate recognizes the leader as legitimate" | sourced |
| 26 | Extend request to each other member of its configuration: prevIndex, prevEpoch, entries, commitIndex; empty = heartbeat | AppendEntries "Arguments"; "the caller's configuration" | sourced |
| 27 | No entry at prevIndex with prevEpoch → failure | "Reply false if log doesn't contain an entry at prevLogIndex" | sourced |
| 28 | Delete conflicting entry and all after; append new | receiver steps 3 and 4 | sourced |
| 29 | commitIndex = min(coordinator's, prevIndex + number sent) if greater | "min(leaderCommit, index of last new entry)" | reading ("index of last new entry" read as last entry carried) |
| 30 | commitIndex never decreases | "increases monotonically" (commitIndex) | sourced |
| 31 | prevIndex 0 always matches | steward | steward (implicit in D) |
| 32 | Deleted configuration entry → fall back to latest remaining | "a server must be prepared to fall back to the previous configuration in its log" | sourced |
| 33 | On election: nextIndex = last + 1, matchIndex = 0; heartbeats at interval shorter than the timeout | Fig 3.1 nextIndex/matchIndex; "repeat during idle periods to prevent election timeouts" | sourced |
| 34 | On failure decrement nextIndex and retry; on success update | "decrement nextIndex and retry" | sourced |
| 35 | Commit N only if (a) entry at N has current epoch and (b) majority of own configuration has matchIndex ≥ N | "log[N].term == currentTerm"; "a majority of the new configuration is used to determine" | sourced |
| 36 | Committing N commits every earlier entry; earlier epochs only indirectly | "Raft never commits log entries from previous terms by counting replicas" | sourced |
| 37 | Configurations are journal entries, replicated like any other | "Cluster configurations are stored and communicated using special entries" | sourced |
| 38 | **A configuration takes effect on a member as soon as the entry is in its journal**, before commit (bold) | "takes effect on each server as soon as it is added" | sourced; **flag**: bold not in D |
| 39 | Latest configuration used for elections and for commitment | "both for voting and for log replication" | sourced |
| 40 | Commitment of a configuration entry decided by a majority of the new configuration | "a majority of the new configuration is used to determine the Cnew entry's commitment" | sourced |
| 41 | A change adds or removes exactly one member | "only one server can be added or removed from the cluster at a time" | sourced |
| 42 | Any majority of a configuration and of one differing by one member intersect | "any majority of the old cluster overlaps with any majority of the new cluster" | sourced; **flag (salience)**: in D it is a step in a safety argument with its figure; in F it is a bare assertion among rules, the premise the bug makes insufficient |
| 43 | Add: steps 1 to 5 | Figure 4.1 AddServer | sourced |
| 44 | Remove: steps 1 to 4; a self-removed coordinator stops after commit | Figure 4.1 RemoveServer; "step down" | sourced |
| 45 | No new change while the previous configuration entry is uncommitted | "by not beginning a new change until the previous change's entry has committed" | sourced |
| 46 | Not included: client requests other than commands and changes; reads; snapshots; non-voting members | steward (scoping) | steward |
| 47 | A command is an opaque payload appended by the coordinator on request | "If command received from client: append entry to local log" | sourced |

Steward's own count before the audit: 47 rows; 37 sourced (4 of them flagged for bold or salience or an omission), 3 readings, 5 steward choices, 2 flags on content (2, 11). Proposed fixes after the audit, not before, so the audit sees F as it stands: drop both bolds; "append-only" → "a sequence"; add the candidate's timer reset; for 11 and 42, either cut or move to a non-normative note, decided with the audit's view.
