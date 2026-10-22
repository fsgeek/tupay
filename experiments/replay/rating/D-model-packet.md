# Rater instructions (Grok), replay classification and R4

Given to a fresh Grok instance for each author, with: these instructions, the author's README sections **Choices** and **Concerns** (as committed before its first run, with the commit hash) and **Concerns after running**, and the source of the code path that begins a configuration change. Never with any run result, K1, the hold-outs, or the pre-registration.

## 1. Classification of the configuration-change path
Choose one, and quote the code or README line that decides it:
- **(a)** On becoming coordinator, the member appends an entry of its own epoch, but a configuration change does not wait for that entry (or any entry of its own epoch) to be committed.
- **(b)** A configuration change does not begin until an entry of the coordinator's current epoch is committed.
- **(c)** Neither: the coordinator appends nothing on election and a change waits only for the previous configuration entry to be committed.
- **(d)** Some other mechanism that restricts when a change may begin or how it is counted. Describe it, and state whether it stops a configuration change from beginning until something beyond "the previous configuration entry is committed" has happened (yes / no).

## 2. Recognition (R4)
Answer separately for the Concerns committed before the first run and for Concerns after running: does the README assert that the design as specified admits a violation of J1.1 or J1.5 (or of "committed entries persist", in the author's own words), and give a mechanism? Restating the specification's one-change-at-a-time rule, or its argument that majorities of configurations differing by one member overlap, is **not** naming. Answer yes / no, and quote the passage.

Report both answers as JSON: `{"classification": "a|b|c|d", "d_restricts_beyond_wait": true|false|null, "r4_before": true|false, "r4_after": true|false, "quotes": {...}}`.

---
# Material
## README sections as committed before the first run (commit b9beb3e)
## Choices

Where Specification D is silent or where two passages disagree, what this model does:

1. **Empty AppendEntries and commitIndex.** Figure 3.1 step 5 sets `commitIndex` to `min(leaderCommit, index of last new entry)`. A heartbeat carries no entry. The prose in §3.5 says heartbeats carry `leaderCommit` so followers learn what is committed. For an empty request that passed the consistency check, the index used is `prevLogIndex`, not the follower's log length. Extra entries the follower has past `prevLogIndex` are not committed by a heartbeat.

2. **The leader counts toward a majority.** Figure 3.1 initialises `matchIndex` to 0 for every server. The prose in §3.5 says an entry is committed once the leader that created it has replicated it on a majority of the servers, and the leader holds the entry. `matchIndex[self]` is the leader's log length. A majority is more than half of the caller's latest configuration, and the leader is included only when that configuration contains the leader.

3. **Latest configuration.** A server's configuration is the payload of the last `config` entry in its log, or the initial configuration when the log has none. The initial configuration is not itself a log entry. Voting and commitment use the caller's configuration (§4.1). Incoming RPCs are processed without consulting the receiver's configuration.

4. **`votedFor` resets when the term changes.** The field is the vote for the current term. On any term increase it becomes null, then the RPC is processed.

5. **Term check before the RPC body.** The all-servers rule "RPC carries term T > currentTerm" runs in the same step as the handler, before the handler. A candidate that receives AppendEntries with term ≥ its current term becomes a follower even if the log check then fails (§3.4).

6. **Who is sent RPCs.** RequestVote and AppendEntries go to every other server in the sender's latest configuration. During AddServer catch-up the leader also sends AppendEntries to the server being added.

7. **Non-members run the election timer.** Every server starts as a follower. Nothing in the reproduced text exempts a server that is absent from its latest configuration, so such a server can become a candidate. Its self-vote does not count toward a majority of a configuration it is not in. See Concerns.

8. **Catch-up.** §4.2 is not part of the build. Figure 4.1 step 2 plus the assembler's note are implemented as: catch-up is complete when the new server's log is identical to the leader's, and it is complete in the same step when the logs already match. Until then the leader replicates with ordinary AppendEntries. A nondeterministic timeout (the election timeout) may answer `timeout` instead. There is no fixed round count.

9. **One change at a time.** A second request that arrives at a member with a change still in progress is answered `busy`. A request to add a member already present, to remove a member who is absent, or to remove the last member is answered `rejected` and appends nothing. Otherwise the leader waits until the previous configuration is committed (the initial configuration counts as committed), appends one new configuration entry, and answers `ok` once that entry's index is at most `commitIndex`. The pending request is volatile and is discarded on crash or on stepping down, in which case the answer is `not_leader` if the member is still up.

10. **Stepping down after self-removal.** Once the removal entry is committed, that server sets its role to follower and stays in the term (§4.1 / Figure 4.1 RemoveServer step 4). It is not shut down. "Can be shut down" is left to a later crash step.

11. **Crash and restart (G1.1).** Crash keeps `term`, `votedFor` and `log`. It clears `commitIndex`, `lastApplied`, role (follower), vote tally, `nextIndex`, `matchIndex` and any pending change. Messages addressed to the crashed server are discarded. Restart restores the durable fields, sets role to follower and `commitIndex` to 0.

12. **Links (G1.3).** `down` is a set of directed pairs. `cut` adds both directions, `drop` adds one, a self-pair is ignored, and the set accumulates until `heal`. A send on a down link is not queued. A message already queued, sent while the link was up, may still be delivered (delay, G1.2). Only sends that happen while the link is down are lost.

13. **Scenario network versus explore network.** In a scenario the environment's crash, restart, cut, drop, heal, add, remove and command actions occur only as the steps say, at a time the model chooses after the trigger. Delivery order is unconstrained (delay and reordering). Spontaneous loss and an extra duplicate delivery are environment actions of G1.2 and are enabled in `--explore` only; a scenario that does not name them does not take them. Retries resend an RPC that is no longer queued. Handlers are idempotent (§3.7): votes are a set, `matchIndex` uses `Max`, and a duplicate failure reply decrements `nextIndex` only while it still equals `prevIndex + 1`.

14. **One entry per AppendEntries.** The figure allows a batch. §3.5 says one entry is enough to make progress. Each request carries at most one entry.

15. **Apply.** When `commitIndex` advances, `lastApplied` catches up in the same step. The contract has no separate applied event. Interleaving one-index applies would not change J1.1, J1.3 or J1.5.

16. **Committed epoch.** `Committed.epoch` is the member's `currentTerm` when its `commitIndex` first covers that index. For the leader, that is the term in which the entry is marked committed, including entries from older terms that commit indirectly. J1.5(a) uses that same epoch: a later coordinator, elected in a strictly higher epoch, must hold the entry at election. Using the entry's own term would reject a correct indirect commit, because a leader elected between the entry's term and the commit need not have held an entry that was not yet committed.

17. **ConfigInEffect.** Emitted when the latest configuration in the log changes, including when truncation reveals an older one. `index` 0 means the log no longer contains a configuration entry and the initial configuration is back in effect. The cause is the `Appended` or `Truncated` in the same step.

18. **Which events count toward `bound` and `settle`.** The seven contract events. `Fault` records do not.

19. **Selectors.** Resolved when the trigger fires. `coordinator` is the member of the most recent `Elected`. `crashed` is the member of the most recent crash step. `follower` is any member that is up and is not `coordinator`; the model branches on every such member. If the set is empty, or `coordinator` / `crashed` has no referent yet, the trigger does not fire on that event.

20. **A command at a non-leader is ignored.** The step is still taken (§ scenario format).

21. **Initial state.** Term 0, `votedFor` null, empty log, `commitIndex` 0, role follower, up. All five servers start, including those outside the initial configuration.

22. **Fairness.** `FairSpec` is weak fairness on each up member's own actions and on delivery of a queued message whose receiver is up and whose link is up. Crash, restart, partition, heal, administrative requests, spontaneous loss and duplication are not fair. The checked properties are safety invariants, so TLC is run on `Spec` without the fairness conjunct and therefore includes unfair finite behaviours.

23. **Observability ghosts.** `seq`, `grantSeq`, `appAt` and `lastObs` are for the trace. They are not protocol state. An `Elected` cause names each granting member and that member's `seq` at the grant. `seq` 0 means the member had emitted no contract event yet. A follower `Appended` names the sender's `Appended` of the same index.

24. **Bounds used for every scenario run.**
    - `MaxTerm = 3`. A shared scenario needs two elections (S1, S2, S6). The third term lets a completing path survive one split vote.
    - `MaxLog = 3`. S8 appends three configuration entries and no shared scenario appends more.
    - `MaxMsgs = 12`. A wave of RequestVote to three peers, their replies, and a wave of AppendEntries fit under this cap along a path that delivers as it goes.
    - `MaxEvents` and `Settle` come from the scenario (400 and 100 on the shared files). A state at the cap is kept; the next event is not.
    - `MaxDown = 20` in scenario mode so a cut of every directed pair is representable.

25. **Bounds used only by `--explore`.** Initial configuration `{m1, m2, m3, m4}`, same `MaxTerm`, `MaxLog` and `MaxMsgs`. Also at most 1 command, 3 membership changes, 2 crashes, 4 directed links down, 3 spontaneous drops and 3 extra redeliveries. Those caps are large enough for every shared scenario's environment shape except S6's eight directed cuts; S6 is checked in scenario mode, where `MaxDown` is 20. Explore does not use a scenario event bound.

## Concerns

A server that is not in its latest configuration can still win an election. Every follower runs the election timeout (§3.4), a voter grants a vote without consulting its configuration (§4.1), and the candidate counts a majority of its own latest configuration. Before any membership change, `m5`'s configuration is the initial one and does not contain `m5`, but `m1`–`m4` will vote for `m5` while the logs are level, and three of their votes are a majority. The omitted §4.2 is the natural place the dissertation would have kept a new server from campaigning; it is not part of this build, so the model allows the election.

A scenario that shows it: initial configuration `[m1, m2, m3, m4]`, one step `{at: start, do: {command: c1, at: m5}}` is the wrong shape (a command is ignored). The shape that shows it is: no administrative step, `end: {settle: 0}`, and a bound large enough for one election. The trace contains `Elected` for `m5`. That is legal under the text above and is not what a membership change is for.


## README section at first-version (4ae17eb)
## Concerns after running

The S1 mutation was aimed at J1.1: a candidate becomes leader on its own vote, so two servers can both do that in one term. With `MaxMsgs = 4` the second `StartElection` cannot queue three RequestVote messages beside the first candidate's three, and `BecomeLeader` cannot queue its heartbeats until a slot is free. Delivering the first candidate's requests makes the others vote in that term, so a later election uses the next term. The violation TLC reaches is J1.5. In the trace, `m1` commits command `c1` in term 1, then `m4` becomes leader in term 2 on its own vote with an empty log. That breaks leader completeness. The two-leader state in one term was not reached under this message cap.

The concern that `m5` can win an election is not witnessed. The role constraint drops that successor, including after `m5` has been added.


## Source of the configuration-change path (at first-version)
### model/Raft.tla lines 480-562
```
\* ---- elections (derives: J1.1) --------------------------------------------

\* No new campaign while any server holds a configuration entry it has
\* not committed. One leader replicates that entry. S6 has no
\* configuration entry, so its post-commit election stays enabled.
OpenConfig(st) ==
  LET log == st.log
      idxs == {i \in 1..Len(log) : log[i].kind = "config"}
  IN IF idxs = {} THEN FALSE
     ELSE st.commitIndex < CHOOSE i \in idxs : \A j \in idxs : j <= i

ConfigElectionOK == \A s \in Servers : ~OpenConfig(servers[s])

StartElection(s) ==
  /\ servers[s].up
  /\ servers[s].role \in {"follower", "candidate"}
  /\ ConfigElectionOK
  /\ LET newTerm == IF Bug = "S2" THEN servers[s].term ELSE servers[s].term + 1
         log == servers[s].log
     IN /\ newTerm <= MaxTerm
        /\ \/ servers[s].role = "follower"
           \/ newTerm /= servers[s].term
           \/ servers[s].votedFor /= s
        /\ LET st2 == [servers[s] EXCEPT !.term = newTerm, !.votedFor = s,
                                      !.role = "candidate", !.votes = {s}]
               rvs == {RVMsg(s, j, newTerm, Len(log), LastTerm(log)) :
                         j \in LatestCfg(log) \ {s}}
               msgs2 == Queued(msgs, rvs)
           IN /\ Cardinality(msgs2) <= MaxMsgs
              /\ servers' = [servers EXCEPT ![s] = st2]
              /\ msgs' = msgs2
              /\ grantSeq' = [grantSeq EXCEPT ![s] = seq[s]]
              /\ leaders' = leaders
              /\ lastObs' = <<>>
              /\ breach' = breach \cup BreachAdd(servers, servers')
              /\ Fire(NoME, UpSet(servers'), coord, crashed)
              /\ UNCHANGED <<down, pending, committed, seq, appAt, envSeq,
                             step, events, doneAt, coord, crashed,
                             crashCount, changeCount, cmdCount, dropCount, redeliverCount>>

BecomeLeader(s) ==
  /\ servers[s].up
  /\ servers[s].role = "candidate"
  /\ VoteQuorum(servers[s].votes, servers[s].log)
  /\ LET st == servers[s]
         log == st.log
         newSeq == seq[s] + 1
         obs == <<"Elected|" \o ToString(s) \o "|" \o ToString(newSeq) \o "|"
                  \o ToString(st.term) \o "|" \o CfgStr(LatestCfg(log)) \o "|"
                  \o VoterStr(st.votes)>>
         match == <<ME("Elected", ToString(s), -1, st.term, "", "", "", "")>>
         st2 == [st EXCEPT !.role = "leader",
                           !.nextIndex = [j \in Servers |-> Len(log) + 1],
                           !.matchIndex = [j \in Servers |-> IF j = s THEN Len(log) ELSE 0]]
         sv2 == [servers EXCEPT ![s] = st2]
         ls2 == leaders \cup {<<st.term, s>>}
         miss == MissingAtElection(st.term, log)
         msgs2 == Queued(msgs, HB(s, st.term, log, st.commitIndex))
     IN /\ Cardinality(msgs2) <= MaxMsgs
        /\ servers' = sv2
        /\ msgs' = msgs2
        /\ leaders' = ls2
        /\ seq' = [seq EXCEPT ![s] = newSeq]
        /\ lastObs' = obs
        /\ coord' = s
        /\ events' = Ev(1)
        /\ breach' = (breach \cup BreachAdd(servers, sv2))
                     \cup (IF miss THEN {"J1.5"} ELSE {})
        /\ Fire(match, UpSet(sv2), s, crashed)
        /\ UNCHANGED <<down, pending, committed, grantSeq, appAt, envSeq,
                       step, doneAt, crashed,
                       crashCount, changeCount, cmdCount, dropCount, redeliverCount>>

\* ---- replication (derives: J1.5, G1.2) ------------------------------------

\* Lower member id first. Model values are unordered, so rank them.
Rank(s) ==
  IF s = m1 THEN 1
  ELSE IF s = m2 THEN 2
  ELSE IF s = m3 THEN 3
  ELSE IF s = m4 THEN 4
  ELSE 5

```
### model/Raft.tla lines 1162-1202
```
DoChange(s, op, target) ==
  LET st == servers[s]
      cfg == LatestCfg(st.log)
      isLeader == st.up /\ st.role = "leader"
      illegal == \/ op = "add" /\ target \in cfg
                 \/ op = "remove" /\ target \notin cfg
                 \/ op = "remove" /\ Cardinality(cfg) <= 1
      busy == isLeader /\ pending[s].active
      reject == ~isLeader \/ busy \/ illegal
      status == IF ~isLeader THEN "not_leader"
                ELSE IF busy THEN "busy"
                ELSE "rejected"
      nReq == seq[s] + 1
      nRep == nReq + 1
      reqS == "ChangeRequested|" \o ToString(s) \o "|" \o ToString(nReq)
              \o "|" \o op \o "|" \o ToString(target)
      repS == "ChangeReplied|" \o ToString(s) \o "|" \o ToString(nRep)
              \o "|" \o op \o "|" \o ToString(target) \o "|" \o status
      obs == IF reject THEN <<reqS, repS>> ELSE <<reqS>>
      match == IF reject
               THEN <<ME("ChangeRequested", ToString(s), -1, -1, "", "", op, ToString(target)),
                       ME("ChangeReplied", ToString(s), -1, -1, "", status, op, ToString(target))>>
               ELSE <<ME("ChangeRequested", ToString(s), -1, -1, "", "", op, ToString(target))>>
      phase == IF op = "add" THEN "catchup" ELSE "wait"
      pend2 == IF reject THEN pending
               ELSE [pending EXCEPT ![s] = [active |-> TRUE, op |-> op,
                                             target |-> target, phase |-> phase, idx |-> 0]]
  IN /\ target \in Servers
     /\ changeCount' = changeCount + 1
     /\ changeCount + 1 <= MaxChanges \/ Mode = "scenario"
     /\ servers' = servers
     /\ pending' = pend2
     /\ seq' = [seq EXCEPT ![s] = IF reject THEN nRep ELSE nReq]
     /\ lastObs' = obs
     /\ leaders' = leaders
     /\ breach' = breach
     /\ UNCHANGED <<msgs, down, committed, grantSeq, appAt, envSeq,
                    coord, crashed, crashCount, cmdCount,
                    dropCount, redeliverCount>>

\* A scenario step, then arm the following step.
```
