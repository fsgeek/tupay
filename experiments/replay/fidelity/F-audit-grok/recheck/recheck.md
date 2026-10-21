# Recheck of changes.diff against spec-D

Compared each changed line in `changes.diff` with the design text in `spec-D.md`: Figure 3.1, sections 3.3–3.8, the Chapter 4 introduction, section 4.1, and Figure 4.1. The opening paragraph, Source note, and closing section of D are the assembler's and were not used. Vocabulary used here is F's mapping: member = server, epoch = term, coordinator = leader, journal = log. A ballot request is RequestVote. An extend request is AppendEntries.

Fifteen lines changed. Every verdict below is supported.

One change gives a statement a more prominent place than D gives it: the network assumption now opens the Messages section. Four lines only remove bold, and the commitment line also drops bold on "current." Those sentences are then at the level of D's plain prose. Details are under the lines and collected at the end.

Quotes below drop line-break hyphens from the PDF extract. Section and figure numbers are D's.

## 1. Journal

`spec-F.md` line 7. "An append-only sequence of entries" becomes "A sequence of entries". The rest of the sentence is unchanged.

**Verdict: supported.**

D describes a log as a sequence of indexed entries, with the first index at 1:

> Logs are composed of entries, which are numbered sequentially. Each entry contains the term in which it was created (the number in each box) and a command for the state machine. (Figure 3.5 caption)

> Each log entry also has an integer index identifying its position in the log. (§3.5)

> log[]: log entries; each entry contains command for state machine, and term when entry was received by leader (first index is 1) (Figure 3.1)

Figure 3.1 has the receiver delete conflicting entries: "If an existing entry conflicts with a new one (same index but different terms), delete the existing entry and all that follow it (§3.5)." The new sentence uses that description: a sequence of indexed entries.

D states a separate leader rule: "A leader never overwrites or deletes entries in its own log (the Leader Append-Only Property in Figure 3.2)." (§3.5). The new sentence leaves that rule as it stands in D. In F the deletion step is still the receiver of an extend request, which is Figure 3.1's receiver step.

**Prominence.** Vocabulary definition, the same role as D's description of log entries. No increase.

## 2. Epoch

`spec-F.md` line 8. Adds "0 when the member first starts."

**Verdict: supported.**

> currentTerm: latest term server has seen (initialized to 0 on first boot, increases monotonically) (Figure 3.1)

"First starts" matches "first boot." The unchanged "Epochs only increase" matches "increases monotonically." Section 3.8 persists the current term across restarts, so the zero is the first boot, which "first" records.

**Prominence.** D puts the zero in the persistent-state list of Figure 3.1. F puts it in the vocabulary definition of epoch. Same role. No increase.

## 3. Committed

`spec-F.md` line 12. The sentence "Committed entries are never removed from any member's journal." is removed. The remaining definition is unchanged.

**Verdict: supported.**

The remaining sentence matches D's account of when an entry is committed, including commitment by a later leader through a later entry:

> A log entry is committed once the leader that created the entry has replicated it on a majority of the servers (e.g., entry 7 in Figure 3.5). This also commits all preceding entries in the leader's log, including entries created by previous leaders. (§3.5)

> Only log entries from the leader's current term are committed by counting replicas; once an entry from the current term has been committed in this way, then all prior entries are committed indirectly because of the Log Matching Property. (§3.6.2)

Figure 3.1 and §§3.5–3.6 state commitment as that majority rule and the indirect commitment of earlier entries. The removed sentence, that a committed entry is never removed from any journal, has no matching rule there. The nearby guarantee in §3.5 is different: "Raft guarantees that committed entries are durable and will eventually be executed by all of the available state machines." The new line keeps the "committed once" definition and leaves deletion as the Figure 3.1 receiver step already in F: a conflicting entry and everything after it.

**Prominence.** A prohibition D does not state as a rule is dropped. No increase.

## 4. Durable state

`spec-F.md` line 15. Adds "Durable state is written to stable storage before the member responds to any request."

**Verdict: supported.**

The durable fields in that sentence are `epoch`, `votedFor`, and `journal`. Those are Figure 3.1's persistent state, and the figure's header applies to all of it:

> Persistent state on all servers: (Updated on stable storage before responding to RPCs)
>
> - currentTerm
> - votedFor
> - log[]

In F, the requests a member responds to are the RPCs (ballot, extend, add, remove). Section 3.8 requires the same three pieces of state to be persisted: the current term, the vote, and new log entries before they count toward commitment.

**Prominence.** D prints this as the header of the persistent-state box in Figure 3.1. F states it as the sentence after the durable list. No increase over the figure.

## 5. Lost, delayed, reordered; retry; parallel

`spec-F.md` line 19. The epoch rules on this line are unchanged. The new prefix is: "Requests and replies may be lost, delayed or reordered. A member that gets no timely reply to a request retries it; requests to different members are sent in parallel."

**Verdict: supported.**

> Raft assumes RPC requests and responses may be lost in the network; it is the requester's responsibility to retry the RPC if it does not receive a response in a timely manner. Servers issue RPCs in parallel for best performance, and Raft does not assume the network preserves ordering between RPCs. (§3.3)

Loss, the requester's retry when a response is not timely, parallel RPCs, and no preserved order are those two sentences. "Reordered" is "does not assume the network preserves ordering." "Delayed" is not a word D uses; the case it names is the one D states next, a response that does not arrive in a timely manner. The behavior F attaches is that same retry. F does not add a further delay rule.

**Prominence.** This is the one increase. D states the assumption in the body of §3.3, after terms and the two RPC types, and Figure 3.1 does not list it. F places it as the opening of Messages, ahead of the epoch rule.

## 6. Requests are processed without the receiver's configuration

`spec-F.md` line 21. Bold is removed. The words are unchanged.

**Verdict: supported.**

> A server accepts AppendEntries requests from a leader that is not part of the server's latest configuration. (§4.1)

> A server also grants its vote to a candidate that is not part of the server's latest configuration (if the candidate has a sufficiently up-to-date log and a current term). (§4.1)

> Thus, servers process incoming RPC requests without consulting their current configurations. (§4.1)

The second sentence of the F line ("grants votes to, and accepts journal extensions from, members that are not in its configuration") is those two bullets.

**Prominence.** The change lowers prominence. D's sentence is the closing sentence of §4.1, in plain prose. The previous F bolded it.

## 7. Election timeout, timer reset, and who is asked

`spec-F.md` line 24. Three edits: "anew each time it is reset" is removed; "resets its election timer" is added on becoming a candidate; "every member of its own configuration" becomes "every other member of its own configuration." The sentence about resetting a follower's timer is unchanged.

**Verdict: supported.**

Random choice from a fixed range:

> election timeouts are chosen randomly from a fixed interval (e.g., 150–300 ms). (§3.4)

Restart when an election starts:

> Each candidate restarts its randomized election timeout at the start of an election, and it waits for that timeout to elapse before starting the next election. (§3.4)

Figure 3.1's candidate step is "Reset election timer," in the same list as incrementing the term, voting for self, and sending RequestVote. F's new clause is in that same place in the same list.

D ties the randomized restart to the start of an election. It does not say that every reset, including a follower's reset on an extend request or a granted ballot, draws a new value. Dropping "anew each time it is reset" leaves the random choice and the election-start reset, which is the scope §3.4 states.

Who is asked:

> Send RequestVote RPCs to all other servers (Figure 3.1)

> It then votes for itself and issues RequestVote RPCs in parallel to each of the other servers in the cluster. (§3.4)

The self-vote is a separate step, so the RPCs go to the others. "Of its own configuration" was already in this sentence. Section 4.1 says "it is the caller's configuration that is used in reaching consensus, both for voting and for log replication."

**Prominence.** The reset is one step in the candidate list, as in Figure 3.1. No increase.

## 8. Majority of the candidate's configuration

`spec-F.md` line 26. Bold is removed from "of its own configuration." The words are unchanged.

**Verdict: supported.**

> A candidate wins an election if it receives votes from a majority of the servers in the full cluster for the same term. (§3.4)

> If votes received from majority of servers: become leader (Figure 3.1)

With membership change, that set is the caller's configuration (§4.1, quoted under item 7). The candidate "votes for itself" (§3.4), so its own grant counts. The parenthetical "counting itself if it is a member of it" was already in the line.

**Prominence.** The change lowers prominence. D states the majority rule in plain prose and in the figure. The previous F bolded "of its own configuration."

## 9. Where an extend request starts, and retry until stored

`spec-F.md` line 29. Adds that entries sent to a member start at that member's `nextIndex`, so `prevIndex` is `nextIndex` − 1, and that the coordinator retries extend requests to a member indefinitely until the member stores every entry. "With no entries it serves as a heartbeat" is reworded as "with no entries the request serves as a heartbeat."

**Verdict: supported.**

Where the entries start, and what `prevIndex` is:

> nextIndex[]: for each server, index of the next log entry to send to that server (initialized to leader last log index + 1) (Figure 3.1)

> If last log index ≥ nextIndex for a follower: send AppendEntries RPC with log entries starting at nextIndex (Figure 3.1)

> prevLogIndex: index of log entry immediately preceding new ones (Figure 3.1)

> The leader maintains a nextIndex for each follower, which is the index of the next log entry the leader will send to that follower. (§3.5)

Entries that start at `nextIndex` are immediately preceded by index `nextIndex` − 1. That is `prevIndex`.

Heartbeat:

> entries[]: log entries to store (empty for heartbeat; may send more than one for efficiency) (Figure 3.1)

> Leaders send periodic heartbeats (AppendEntries RPCs that carry no log entries) (§3.4)

Indefinite retry:

> If followers crash or run slowly, or if network packets are lost, the leader retries AppendEntries RPCs indefinitely (even after it has responded to the client) until all followers eventually store all log entries. (§3.5)

F's "until the member stores every entry" is that requirement per member. The sentence it follows still sends to "each other member of its configuration," which is the set §4.1 replicates to once a configuration entry is in the log ("the Cnew entry is replicated to the Cnew servers").

**Prominence.** `nextIndex` and the empty heartbeat are already leader rules in Figure 3.1. The indefinite retry is its own sentence in §3.5. Placing it on the extend-request rule gives it that same weight.

## 10. Values written on a successful extend

`spec-F.md` line 31. "on success it updates `nextIndex` and `matchIndex`" becomes "on success it sets that member's `matchIndex` to the index of the last entry the request carried, and `nextIndex` to one more than that."

**Verdict: supported.**

Figure 3.1 says, under the branch that sends entries starting at `nextIndex`: "If successful: update nextIndex and matchIndex for follower (§3.5)." The fields are defined there as:

> nextIndex[]: for each server, index of the next log entry to send to that server

> matchIndex[]: for each server, index of highest log entry known to be replicated on server (initialized to 0, increases monotonically)

Section 3.5 fixes what a success establishes:

> whenever AppendEntries returns successfully, the leader knows that the follower's log is identical to its own log up through the new entries.

The highest index known to be replicated is then the last of those entries, and the next index to send is the one after it. The new clause states those two values. D also says `matchIndex` increases monotonically; on this success path the confirmed index is that new highest index.

Figure 3.1 attaches "update nextIndex and matchIndex" to the branch that sends entries. The new clause is in the bullet that also sends heartbeats. The receiver bullet, unchanged by this diff, already defines "the index of the last entry the request carried" as `prevIndex` plus the number of entries sent. For an empty request that is `prevIndex`. A successful check has confirmed the follower has that prefix (§3.5, the consistency check, and the success sentence above). Setting `matchIndex` to that index matches "highest log entry known to be replicated."

**Prominence.** The success case is more specific than the figure's verb "update." It stays in the leader rule the figure uses for that success.

## 11. Commitment rule

`spec-F.md` line 34. "A coordinator may mark the entry at index N committed … only if (a) … and (b) …" becomes "Whenever there is an index N greater than its `commitIndex` such that (a) … and (b) …, the coordinator sets `commitIndex` to N, marking the entry at N committed." Bold is also removed from "current."

**Verdict: supported.**

> If there exists an N such that N > commitIndex, a majority of matchIndex[i] ≥ N, and log[N].term == currentTerm: set commitIndex = N (§3.5, §3.6). (Figure 3.1)

> The server behavior in the lower-right box is described as a set of rules that trigger independently and repeatedly. (Figure 3.1 caption)

The new wording is that triggering rule: when such an N exists, set `commitIndex` to N. Conditions (a) and (b) are `log[N].term == currentTerm` and a majority with `matchIndex` at least N. The rest of the F paragraph is unchanged and matches §3.5 (committing N commits every preceding entry) and §3.6.2 (earlier-term entries are committed only indirectly).

The majority is "of the coordinator's configuration (counting the coordinator if it is a member)." That qualifier was already in the line. For a fixed cluster, Figure 3.1 says "a majority of matchIndex[i]" and §3.5 says "a majority of the servers." After a configuration change, §4.1 uses "a majority of the new configuration" to decide commitment of the new configuration entry, and "each server always uses the latest configuration found in its log."

**Prominence.** The new "whenever … sets" has the force of Figure 3.1's rule that triggers, including the caption that the rules trigger repeatedly. The previous F's "may … only if" was weaker than the figure. The change meets the figure's force. Removing bold from "current" lowers a typographic stress D does not use; the figure writes `log[N].term == currentTerm` in plain text, and §3.6.2 states the current-term restriction in prose.

## 12. When a configuration takes effect

`spec-F.md` line 38. Bold is removed from "A configuration takes effect on a member as soon as the entry is in its journal." The words are unchanged.

**Verdict: supported.**

> The new configuration takes effect on each server as soon as it is added to that server's log: the Cnew entry is replicated to the Cnew servers, and a majority of the new configuration is used to determine the Cnew entry's commitment. This means that servers do not wait for configuration entries to be committed, and each server always uses the latest configuration found in its log. (§4.1)

**Prominence.** The change lowers prominence. D gives this a paragraph in §4.1, in plain prose. The previous F bolded the first clause.

## 13. Majority for committing a configuration entry

`spec-F.md` line 39. Bold is removed from "new." The words are unchanged.

**Verdict: supported.**

> a majority of the new configuration is used to determine the Cnew entry's commitment. (§4.1)

Figure 4.1 says the same for both RPCs: "commit it using majority of new configuration (§4.1)."

**Prominence.** The change lowers prominence. D names "the new configuration" in plain prose. The previous F bolded "new."

## 14. One member at a time

`spec-F.md` line 40. Adds "larger changes are made as a series of such changes." Replaces "Any majority of a configuration and any majority of a configuration that differs from it by one member intersect." with "The design restricts changes to one member at a time because any majority of the old configuration then overlaps any majority of the new one, so the cluster cannot split into two independent majorities."

**Verdict: supported.**

> Thus, Raft restricts the types of changes that are allowed: only one server can be added or removed from the cluster at a time. More complex changes in membership are implemented as a series of single-server changes. (§4.1)

> When adding a single server to a cluster or removing a single server from a cluster, any majority of the old cluster overlaps with any majority of the new cluster; see Figure 4.3. This overlap prevents the cluster from splitting into two independent majorities (§4.1)

"Larger changes are made as a series of such changes" is the second sentence of the first passage. "Cannot split into two independent majorities" is the second passage's "prevents the cluster from splitting into two independent majorities." The same part of §4.1 gives the reason: "disallow membership changes that could result in disjoint majorities," with a one-server change keeping the overlap. Figure 4.3's caption says the overlap "is preserved, as needed for safety."

**Prominence.** No increase. D opens §4.1 with this argument and uses Figures 4.2 and 4.3. F adds two clauses to one bullet.

## 15. A coordinator that removed itself

`spec-F.md` line 53. "it stops being coordinator" becomes "it steps down." The condition "If the coordinator removed itself" and "after the entry is committed" are unchanged.

**Verdict: supported.**

Figure 4.1, RemoveServer, step 4:

> Reply OK and, if this server was removed, step down (§4.2.2)

The receiver of RemoveServer is the leader (step 1 replies if it is not the leader). "If this server was removed" is the leader removing itself. Step 3 commits the new configuration; step 4 then replies and steps down. "After the entry is committed" is that order.

Section 4.1 also says that once Cnew is committed, "If the configuration change removed a server, that server can be shut down." That sentence is about shutting down a removed server. The verb this edit uses is the figure's "step down."

**Prominence.** Step 4 of the remove procedure, the same place as Figure 4.1. No increase.

## Emphasis and prominence

| Change | Relative to D |
| --- | --- |
| 5. Network loss, retry, and parallel send | More prominent. Body paragraph of §3.3; Figure 3.1 omits it. F opens Messages with it. |
| 10. Exact `matchIndex` and `nextIndex` on success | More explicit than the figure's "update." Same leader rule. |
| 11. "Whenever … the coordinator sets `commitIndex`" | Same force as Figure 3.1's triggering rule. The previous wording was weaker than D. |
| 6, 8, 12, 13, and the unbolding of "current" in 11 | Less prominent than the previous F. D states those sentences in plain prose. |
| 14. Overlap and the series of one-member changes | Less space than §4.1 and Figures 4.2 and 4.3. |
| 1–4, 7, 9, 15 | Same role D gives the statement: a definition, a figure step, or a sentence of the section that states it. |
