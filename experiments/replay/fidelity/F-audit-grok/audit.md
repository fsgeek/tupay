# Fidelity audit of spec-F against spec-D

Scope: design content only. Vocabulary is the mapping in D's source note (member = server, epoch = term, coordinator = leader, journal = log, configuration = configuration). Motivation and history in D are not scored; the excluded passages are listed at the end. This audit does not judge whether either design is correct or safe.

Search: each quoted anchor was searched in `spec-D.md`. A match split only by a line break, or by a `pdftotext` hyphen at a line end, is counted as present. D uses a curly apostrophe; the table's straight apostrophe is the same word. "Wrong anchor" is reserved for a citation that does not locate the supporting passage.

Rows 0–47 were checked (48 rows).

## 1. Row verdicts

| # | Verdict | What the check showed |
|---|---|---|
| 0 | status wrong | The opening paragraph is in D, word for word (D lines 3). Under the table's own definitions that is **sourced**. **Steward** is defined there as "not in D". |
| 1 | unsupported | "member = server" is in D's source note and supports only the rename. It does not say that a member is a process that stores a journal and takes part in agreement, and it does not name members `m1`, `m2`, …. D's examples use S1, S5. The rename is sourced; the names are a **steward** choice; the process/journal/agreement gloss is a **reading** of "server". |
| 2 | confirmed | "first index is 1" and "delete the existing entry and all that follow it" are both in Figure 3.1. F's universal "append-only" does depart from the deletion rule. Qualification: D does state an append-only property, scoped to the leader's own log ("A leader never overwrites or deletes entries in its own log", the Leader Append-Only Property, §3.5). The flag's "append-only is false" fits F's wording for every journal. It does not fit that leader property. |
| 3 | confirmed | Figure 3.1 and §3.5 store "the term when the entry was received by the leader". §3.6.2 says entries keep that original term when a later leader replicates them, which supports "first appended". |
| 4 | confirmed | §4.1 stores configurations as special log entries; ordinary entries carry a state-machine command. "A set of member names" is thinner than this anchor; see part 2. |
| 5 | confirmed | "initialized to 0 on first boot, increases monotonically" supports a non-negative value that only increases. F itself never says the stored epoch starts at 0; see part 3. |
| 6 | confirmed | §3.3: three states, and a candidate that wins serves as leader for the rest of the term. |
| 7 | confirmed | The sentence is split across a line break and is present: each server uses the latest configuration in its log. The next lines add "regardless of whether that configuration entry has been committed". |
| 8 | confirmed | No passage says what the configuration is when the log has no configuration entry. Disclosed choice. |
| 9 | confirmed | D never defines "majority". Figure 4.3's caption uses 2 of 3 and 3 of 4, so "more than half" matches the illustration. It is still not a sentence of D. |
| 10 | confirmed | Figure 3.1's `set commitIndex = N` and §3.6.2 (current-term entries committed by counting replicas; earlier entries committed with them) support F's definition. |
| 11 | status wrong | "Leader Completeness" occurs in §3.6.3. That section does not say committed entries are never removed from any server's log. It argues that the leader of a later term stores entries committed in an earlier term. Its lemmas are that leaders never delete or overwrite entries, and that followers remove entries only when they conflict with the leader. The nearest guarantee in the prose is §3.5: committed entries are durable and will eventually be executed. Should be **flag**: F adds a universal non-removal sentence and places it in the definition of Committed. The row's identification of that sentence with Leader Completeness is not the text. References in the row to a bug and to J1.2 are outside these two documents. |
| 12 | confirmed | Figure 3.1's persistent state is currentTerm, votedFor, and log[]. |
| 13 | confirmed | Figure 3.1 initializes commitIndex to 0. §3.4: servers start as followers. §3.8: commit index may be reinitialized to 0 on restart; other non-persistent variables may be lost. |
| 14 | confirmed | "Volatile state on leaders" names nextIndex and matchIndex. F drops the definitions that sit in that same passage; see part 3. |
| 15 | confirmed | Figure 3.1: if a request or response carries T > currentTerm, set currentTerm = T and convert to follower. votedFor is "the candidateId that received vote in current term", so clearing it on a term change is a reading. "Before processing the message further" is a second reading (order), which the row's note does not mention. The status **reading** still fits. |
| 16 | confirmed | Both receiver procedures: "Reply false if term < currentTerm". §3.3: a stale-term request is rejected. Results carry currentTerm. F's sentence does not say the reply is negative; see part 3. |
| 17 | confirmed | The sentence is in §4.1, almost verbatim. The bold is F's. |
| 18 | confirmed | The two bullets immediately above that sentence: accept AppendEntries from a leader outside the latest configuration, and grant a vote to a candidate outside it. |
| 19 | status wrong | "Raft uses randomized election timeouts" is present, and §3.4 chooses them from a fixed interval. The same paragraph restarts a candidate's randomized timeout at the start of an election. It does not draw again on every reset. F's resets include a follower receiving an extend or granting a ballot. Should be **flag**. |
| 20 | confirmed | Figure 3.1, followers: election timeout elapses without AppendEntries from the current leader or without granting a vote. F follows this sentence. §3.4's prose is broader; see part 3. |
| 21 | confirmed | "Increment currentTerm", "Vote for self", and "the caller's configuration" are all in D (the last with a curly apostrophe). RequestVote carries lastLogIndex and lastLogTerm. The flag is right: Figure 3.1 also says "Reset election timer", and F's candidate steps omit it. "Every member" versus the figure's "all other servers" is a further difference; see part 3. |
| 22 | confirmed | RequestVote receiver steps, plus §3.6.1: higher last term is more up to date; same last term, the longer log is more up to date. "Index at least as large" matches "at least as up to date" for logs whose last index is their length. |
| 23 | confirmed | The persistent-state header says it is updated on stable storage before responding to RPCs. votedFor is in that set. F states the timing only on the grant path. |
| 24 | confirmed | Figure 3.1: votes from a majority of servers, become leader. §4.1: the caller's configuration is what is used for voting. "Counting itself if it is a member" is not in the reproduced text. §4.2.2 is not included. **Reading** is the right status. |
| 25 | confirmed | §3.4: if the leader's term in an AppendEntries RPC is at least the candidate's current term, the candidate returns to follower. F's "hears from a coordinator" does not name the extend request. |
| 26 | confirmed | AppendEntries arguments are prevLogIndex, prevLogTerm, entries[] (empty for heartbeat), leaderCommit. §4.1 uses the caller's configuration for log replication, and replicates Cnew to the Cnew servers. |
| 27 | confirmed | The anchor is a prefix of the same line: "Reply false if log doesn't contain an entry at prevLogIndex whose term matches prevLogTerm". |
| 28 | confirmed | "Receiver steps 3 and 4" is a pointer, not a quote. Steps 3 and 4 are the conflict deletion and the append of entries not already in the log. |
| 29 | confirmed | The figure says `min(leaderCommit, index of last new entry)`. F's "`prevIndex` plus the number of entries sent" is one reading of that phrase, including when the entry list is empty. **Reading** is right. |
| 30 | confirmed | commitIndex "increases monotonically" in Figure 3.1. |
| 31 | status wrong | No sentence says "`prevLogIndex` 0 matches". The figure's check is "no entry at prevLogIndex", and the first index is 1, so a literal reading rejects 0. §3.5 says the initial empty logs satisfy the Log Matching Property and that the consistency check is the induction step. F resolves that in favor of the induction. The row calls this both **steward** and "implicit in D". Under the table's definitions it is **reading**. |
| 32 | confirmed | The sentence is split after "fall back" and is present. For a suffix deletion, "the previous configuration" and "the latest configuration entry that remains" are the same. |
| 33 | confirmed | nextIndex initializes to last log index + 1 and matchIndex to 0, reinitialized after election. Heartbeats repeat "during idle periods to prevent election timeouts"; §3.4 says periodic heartbeats. "Shorter than the election timeout" is the bound that sentence is for. |
| 34 | confirmed | "If AppendEntries fails because of log inconsistency: decrement nextIndex and retry", and on success update nextIndex and matchIndex. In F, the failure reply is the prevIndex mismatch, so "on failure" matches that case. |
| 35 | status wrong | `log[N].term == currentTerm` supports (a). "A majority of the new configuration is used to determine the Cnew entry's commitment" is split across a line break and speaks only about Cnew. The general quorum is the caller's configuration, used for log replication. F's sentence also counts the coordinator if it is a member; the table's summary drops that clause, and D does not state it (the same gap row 24 calls a reading). Separate departure: Figure 3.1 states the assignment as a rule that fires ("set commitIndex = N"). F says the coordinator "may" mark N. Should be **reading** for the quorum and the self-count, and **flag** for "may". |
| 36 | confirmed | The anchor is hyphenated in D as "previ-ous" and is the §3.6.2 sentence. That paragraph says a current-term entry committed by counting replicas commits all prior entries indirectly. |
| 37 | confirmed | §4.1: configurations are special entries in the replicated log, using the existing replicate-and-persist mechanism. |
| 38 | confirmed | "takes effect on each server as soon as it is added to that server's log", and servers do not wait for the entry to be committed. The bold is F's. |
| 39 | status wrong | The anchor is split across a line break: the caller's configuration is used "both for voting and for log replication". F says the latest configuration is used "for elections and for commitment". Commitment is one part of log replication; the anchor also covers who is replicated to. Should be **reading**. |
| 40 | confirmed | The phrase is split after "a majority of the new" and continues "configuration is used to determine the Cnew entry's commitment". |
| 41 | confirmed | "only one server can be added or removed from the cluster at a time". F's "the configuration in which it is made" matches Cold in that section. |
| 42 | confirmed | The prose hyphenates "ma-jority"; the sentence is "any majority of the old cluster overlaps with any majority of the new cluster" when one server is added or removed. Figure 4.3's caption is the same overlap claim. F's "intersect" / "differs by one member" matches that claim. D places it in the §4.1 safety argument, with the figure. F places it as an unargued sentence among the rules. The salience flag matches the texts. The row's remark that this premise is "insufficient" for a bug is outside the two documents and is not a fidelity finding. |
| 43 | status wrong | AddServer steps 1–5 match Figure 4.1, including the timeout conditions and commit-by-new-majority. F's step 2 adds "of extend requests". The figure says "a fixed number of rounds" and points at §4.2.1, which is not in D. Should be **sourced** for the five steps, and **reading** for what a round consists of. |
| 44 | confirmed | RemoveServer steps match the figure, including "step down" after the commit. F's verb is "stops being coordinator"; see part 3. |
| 45 | confirmed | The sentence is split after "previous change's" (curly apostrophe) and continues "entry has committed". |
| 46 | status wrong | The exclusion sentence is in D, in "What the design does not include", word for word (D lines 655–656). Should be **sourced**. It is not absent from D. |
| 47 | wrong anchor | "If command received from client: append entry to local log" is in Figure 3.1, and the same bullet continues ", respond after entry applied to state machine". That bullet does not say the command is opaque. The full F sentence, including "opaque", is the closing sentence of D (D line 656), which row 46 treats as outside D. |

## 2. Statements in F that the table does not cover

The table's short statements drop these clauses. Coverage elsewhere is noted.

1. **A member "takes part in agreement"** (F vocabulary; row 1 stops at storing a journal and the names). D supports this as a gloss of a server in the cluster. It is not a sentence of the source note.

2. **A configuration is a set of member names** (F vocabulary; row 4 says only "command or a configuration"). D defines the configuration as the set of servers participating in consensus (§4 introduction) and, in Figure 4.1, identifies the added or removed server by address. The set-of-participants part is supported. The names `m1`, `m2`, … are not in D (row 1).

3. **`votedFor` is for the current epoch** (F state; row 12 lists the variable and does not include the qualifier). D supports it: "candidateId that received vote in current term (or null if none)". Row 15 uses that fact as the reason a reading clears `votedFor`. The statement in F is not itself a row.

4. **`nextIndex` and `matchIndex` are kept for each other member** (F state and the on-election sentence). Rows 14 and 33 name the variables and the initial values. D says both arrays are "for each server".

5. **A matching extend replies success** (F journal-extension bullet; row 28 stops at delete-and-append). D supports it. AppendEntries' result is `success: true if follower contained entry matching prevLogIndex and prevLogTerm`, and the receiver replies false only for a stale term or a failed consistency check.

6. **The coordinator advances `commitIndex` only to an N greater than its current value** (F commitment rule; row 35's summary omits it). D supports it: Figure 3.1 requires `N > commitIndex`.

7. **That majority counts the coordinator if it is a member** (same F sentence; row 24's self-count is only the election). D does not state this for commitment. It is the same kind of reading as row 24. Figure 3.1 says "a majority of matchIndex[i] ≥ N" with matchIndex "for each server".

8. **Commitment is permission** ("may mark"). Row 35's verb is "Commit N only if". Figure 3.1's verb is the rule firing. See row 35.

Row 43 does cover the add steps as a bundle; the extra words "of extend requests" are handled in that row, not here.

## 3. Design differences

F keeps the election restriction, the current-epoch commitment restriction, indirect commitment of earlier entries, immediate adoption of a configuration entry, one-server changes, the new-configuration commit quorum, the ban on overlapping changes, fallback after a configuration entry is deleted, and the rule that incoming requests are processed without consulting the receiver's configuration. The differences below are the rest.

### Changes

- **Append-only.** F defines every journal as append-only. D's deletion rule, which F also restates, removes a conflicting entry and everything after it. D's append-only sentence is only that a leader never overwrites or deletes entries in its own log.
- **Election-timeout draws.** D chooses timeouts from a fixed interval and restarts a candidate's randomized timeout at the start of an election. F draws anew on every reset, and F resets a follower's timer on an extend from the current coordinator or on granting a ballot.
- **Who receives a ballot.** Figure 3.1 sends RequestVote "to all other servers". §3.4 says "each of the other servers in the cluster". F sends a ballot request to every member of the sender's configuration and also votes for itself. "Every member" includes the sender when it is a member. §4.1 supports using the caller's configuration as the voting set. It does not say to send the RPC to oneself.
- **Leader arrays.** D: nextIndex and matchIndex for each server. F: for each other member, with a separate self-count "if it is a member" on election (row 24) and on commitment (uncovered, part 2).
- **What the latest configuration is for.** D: the caller's configuration is used for voting and for log replication. F's rule sentence says elections and commitment. F's send rules still address the current configuration, so the recipient rule is not absent; the named purposes of this sentence are narrower.
- **Commitment modality.** Figure 3.1: if such an N exists, set commitIndex to N. The figure caption says those rules trigger independently and repeatedly. F: the coordinator may mark N, and only if the two conditions hold.
- **Removed coordinator.** Figure 4.1: if this server was removed, step down. F: if the coordinator removed itself, it stops being coordinator after the entry is committed. F does not give the resulting role. D's source note says a removed server stops acting as Figure 4.1 describes; §4.2.2, which the figure cites for step down, is not in the extract.
- **Follower timeout events.** F matches Figure 3.1 (AppendEntries from the current leader, or granting a vote). §3.4 also says a server remains a follower as long as it receives valid RPCs from a leader or candidate. F takes the figure's events and leaves the broader sentence out.
- **Identity of members.** F names members `m1`, `m2`, … and stores configurations as sets of those names. D's membership RPCs take an address.

### Omissions of mechanism

- **Sending the journal.** Figure 3.1: if last log index ≥ nextIndex for a follower, send AppendEntries with entries starting at nextIndex. The state block defines nextIndex as the next entry to send to that server, and matchIndex as the highest index known to be replicated there, increasing monotonically. F initializes the two arrays, decrements nextIndex on failure, and "updates" both on success. F never says which entries an extend carries, never ties `prevIndex` to `nextIndex`, and never defines either array. On success it does not say what values are written.
- **State machine.** Figure 3.1 and §§3.5–3.6, all inside the included text: `lastApplied`; if commitIndex > lastApplied, increment it and apply that entry; the leader appends a client command and responds after the entry is applied; the leader returns the execution result; a follower applies a committed entry in log order; servers apply entries in index order. The state machine may be volatile or persistent, and a persistent machine's last applied index must be persistent (§3.8). F has none of this. D's closing, which F copies, calls a command an opaque payload that the coordinator appends. That closing and the apply rules are both in D.
- **Candidate timer reset.** On conversion to candidate, Figure 3.1 resets the election timer. §3.4 restarts the candidate's randomized timeout at the start of an election and waits for that timeout before another election. F's expiry rule applies to a follower or a candidate, and F never restarts the timer when the candidate steps begin. (Row 21 flags the figure line.)
- **Initial epoch.** Figure 3.1 initializes currentTerm to 0 on first boot. F says a non-negative integer that only increases, and does not state the initial value.
- **Durable write barrier.** Figure 3.1 updates all persistent state on stable storage before responding to RPCs. §3.8: persist current term and vote, and persist new log entries before they count toward commitment. F makes epoch, votedFor, and the journal durable, and says votedFor is recorded before a grant reply. F does not state the barrier for epoch or for journal entries, or the "before they are counted" order.
- **Loss and retry.** §3.3: requests and responses may be lost; the requester retries if no timely response arrives; servers issue RPCs in parallel; Raft does not assume the network preserves order. §3.5: the leader retries AppendEntries indefinitely until every follower stores every entry, including after it has answered the client. §3.7: follower and candidate crashes are handled by retrying indefinitely; an RPC repeated after a crash has the same effect. F's only retry sentence is decrement-and-retry on an extend's failure reply. F does not state ballot retry, retry on a lost message, indefinite retry, parallelism, or the no-ordering assumption. F's receiver does skip entries it already has, which is D's idempotent-append example.
- **Empty journal in an election.** RequestVote always carries lastLogIndex and lastLogTerm. F describes those as the index and epoch of the candidate's last entry, and the up-to-date check is phrased only in terms of that entry. F special-cases `prevIndex` 0 for extend requests and has no corresponding case for a ballot.
- **Client-redirect fields.** AppendEntries carries leaderId "so follower can redirect clients". §3.3: a follower redirects a client to the leader. Figure 4.1's results include leaderHint. D's source note puts unreproduced client-interaction sections, with §6.2 as the example, outside the build. The redirect sentence in §3.3 and the leaderId argument are in the included text. F has neither.
- **After Cnew commits.** §4.1 allows the removed server to be shut down. F does not say this. The same list's other two consequences (acknowledge the change; further changes may start) are in F as "reply ok" and the no-overlap rule.
- **One complex change is a series.** §4.1: changes that add or remove more than one server are done as a series of single-server changes. F's "exactly one" rule leaves a series possible and does not state it.
- **Optional locate-the-match speedups.** §3.5: while the match point is unknown the leader can send empty AppendEntries; a rejection can carry the conflicting term and its first index; alternatively a binary search. D presents these as optional. F does not include them.
- **Execution model.** The Figure 3.1 caption says the server rules trigger independently and repeatedly. F presents ordered bullets and does not say that.
- **Messages F does not give a body.** F never defines `voteGranted`. A ballot reply is specified on the grant path (durable `votedFor`, then reply) and for a lower epoch (reply with its own epoch). D's RequestVote result is term plus voteGranted.

### Properties and consequences D states in the design sections and F does not

These are claims in the included design text, not extra mechanism. F's rules sometimes imply them. F does not state them.

- At most one leader in a given term (§3.3). In normal operation exactly one leader, and the others followers (§3.3). A term can end with no leader (§3.4 and the Figure 3.4 caption).
- Followers are passive: they issue no requests and only respond (§3.3 and the Figure 3.3 caption).
- Terms are consecutive integers (§3.3). Different servers may observe term changes at different times, and a server may miss a term (Figure 3.4 caption and §3.3).
- Election votes are for the same term (§3.4: a majority "for the same term"). Each server votes for at most one candidate in a term, first come first served (§3.4). F's grant rule encodes the single vote. F does not say the majority that wins is same-epoch grants, beyond "coordinator of that epoch".
- Log Matching (§3.5): same index and term implies same command, and identical prefixes. A leader creates at most one entry with a given index in a given term, and entries do not change position. On a successful AppendEntries the leader knows the follower's log matches its own through the new entries.
- Leader Completeness, as §3.6 states it: a new leader already stores every entry committed in previous terms. State Machine Safety (§3.6.3): if a server has applied an entry at an index, no server applies a different entry at that index. F's "never removed from any member's journal" is not either sentence (row 11).
- §3.5's availability claims: the algorithm can accept, replicate, and apply entries while a majority is up; a normal replication is one round to a majority; one slow follower does not set the pace.
- Once Cnew is committed, a majority of Cnew have adopted it; servers that do not have Cnew cannot form a majority and cannot be elected leader (§4.1).
- Configuration entries and client commands are ordered by the log, and both may be replicated concurrently in a pipeline or in batches (§4.1). F allows an extend to carry more than one entry. F does not state the pipeline or the ordering claim.
- A server that loses its persistent state cannot rejoin under its prior identity; it can be added back with a new identity by a membership change. If a majority loses persistent state, log entries may be lost and membership changes cannot make progress (§3.8).
- The cluster continues to operate during a membership change (§4 introduction). That sentence is the design requirement next to the history of manual changes; the manual procedures themselves are not scored.

D's §3.6.3 proof, and the sentence in §4.1 that the overlap "guarantees the existence of the voter", are argument. F does not carry the argument. It does carry two sentences from it, at higher salience: non-removal (changed, row 11) and majority intersection (row 42).

### Emphasis, order, and bold

- F bolds the whole sentence "Members process incoming requests without consulting their own configuration" and the whole clause "A configuration takes effect on a member as soon as the entry is in its journal". D states both in §4.1 body text with no bold (rows 17 and 38).
- F also bolds, inside rules, "of its own configuration" (election majority), the commitment rule's "current" epoch, and the configuration entry's "new" configuration. The table does not flag these. D does not bold them. Vocabulary bold on first definition (Member, Journal, Epoch, and so on) is glossary styling; D's figure bolds its state headings and does not bold these rule words.
- F places non-consultation with one's own configuration in the message rules, before election and replication, and in bold. D places it at the end of §4.1, after the reason.
- F places "any majority … intersect" in the configuration rule list, with no figure and no surrounding argument. D places the overlap sentence inside the §4.1 safety argument and points at Figure 4.3 (row 42).
- F places "committed entries are never removed from any member's journal" in the definition of Committed. D's deletion rule has no committed-entry exception; the claim that committed entries survive is argued in §3.6.3 and summarized as durability in §3.5.
- F gives the commitment rule its own section between journal extension and configuration changes. D puts the triggering rule in the leader box of Figure 3.1 and the previous-term restriction in §3.6.2.
- F omits the worked pictures that the extract does include as captions: Figure 4.2 (a direct multi-server switch), Figure 4.3 (overlap on adding or removing one server from an even- and an odd-sized cluster, with the 2-of-3 and 3-of-4 counts), and Figure 3.7 (why a majority copy of an older-term entry is not by itself a commit). The one-server rule and the current-epoch commit rule are in F without those illustrations.

### Explicit resolutions F adds where D is silent or split

Disclosed in the table, and matching the texts: initial configuration when the journal has none (steward); "majority" means more than half (steward; Figure 4.3 illustrates that ratio); `prevIndex` 0 matches (should be a reading, row 31); clear `votedFor` and apply a higher epoch before the rest of the message (reading); `commitIndex` update uses `prevIndex` plus the number of entries sent (reading); an election counts the candidate if it is a member of its configuration (reading).

Not disclosed as readings: a new timeout draw on every follower reset (row 19); catch-up rounds are rounds of extend requests (row 43); the commitment majority counts the coordinator when it is a member (part 2).

### Passages treated as motivation or history and not scored

The abandoned ranking election (§3.4); the manual off-line and address-takeover procedures and their operational downsides (chapter 4 introduction); the history of the original multi-server method and LogCabin (§4.1); comparisons with Viewstamped Replication and with algorithms that renumber entries; remarks on understandability and on why the optional consistency-check speedups are unnecessary. Design claims that sit in those passages and are stated as part of the algorithm are scored above (single-server changes, series of single-server changes, leader does not overwrite its own log, entries keep their original term).
