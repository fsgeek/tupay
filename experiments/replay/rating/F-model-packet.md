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
## README sections as committed before the first run (commit 1435384)
## Choices

Where the specification is silent, or where a finite check has to represent an unbounded network, these are the readings the model uses.

1. A ballot is not a stored message. The voter grants in one action, and only while both directions of the link are up. The action reads the candidate's journal and the candidate's current epoch at that moment. Taking the same grant again changes nothing. A lost ballot is a grant that is never taken. A delayed ballot is a grant taken later. Reordering is the order of grant actions. A reply to the candidate that would carry an older epoch is outside this representation, because there is no buffered request.

2. An extend is applied to the follower inside the coordinator's send. The follower leaves one reply. A later send replaces an untaken reply, and the replaced reply is lost. Two extends to the same follower are not in flight together, and a reply is not delivered twice. Delay of an extend, while the link is up, is the send not having been taken yet. A send on a down link is dropped and not queued.

3. A reply carries three fields the message list does not name: success or failure, the match index, and the sender's epoch. A reply whose epoch is higher than the coordinator's makes the coordinator a follower and clears `votedFor`. It is not also applied as a success or a failure. A reply at an equal or lower epoch is applied. Success sets `matchIndex` to the last index the request carried and `nextIndex` to one past that. Failure decreases `nextIndex`. `nextIndex` stays at least 1, so `prevIndex` does not go below 0.

4. The durable vote and the grant are one action. A grant has no observable event of its own. An `Elected` cause names each counting voter by `(proc, seq)` where `seq` is that member's latest observable record at the grant, or 0 when the member has none. The candidate's own vote uses the same rule, with the sequence number of the candidate's latest record when the election begins. Causes are ordered by member name.

5. `Elect` is the election timeout. It is enabled for every up follower and candidate whose epoch is below `MaxEpoch`. An extend or a grant does not disable it. A coordinator does not take it. There is no timer variable. Once `matchIndex` has caught the log and `nextIndex` is past the end, the empty extend is not sent: it would change no stored state. The specification's periodic heartbeat has no clock to hang on here.

6. Catch-up sends at most `MaxRounds` extends. A `timeout` reply is enabled the whole time the change is in catch-up. Waiting for the previous configuration to commit, and waiting for the new entry to commit, have no timeout. If the new member's journal already equals the coordinator's, catch-up is over at once and the change moves to the commit wait. A change request while one is already in progress is answered `busy`. An add of a member already in the configuration, or a remove of a member who is absent, is answered `reject` (the `wide_change` mutation does not reject). The specification names `not coordinator`, `timeout`, and `ok`. `busy` and `reject` are the answers for the cases it leaves unnamed. `not coordinator` is checked first. The pending change is volatile and disappears on a crash.

7. One extend carries the suffix from `nextIndex` through the last entry. An existing entry is the sent entry when kind, epoch, command, and members all agree. The specification defines a conflict as the same index and a different epoch. The same epoch with a different payload is left open; the model treats that pair as a conflict and truncates from that index.

8. The commitment action sets `commitIndex` to the largest eligible index and emits `Committed` for every newly covered index. `crecs` records each of those, with `commitEpoch` equal to the coordinator's current epoch. That value is the epoch `e` in J1.5(a), which is the epoch of the coordinator who marked the entry, including entries the rule commits indirectly. A follower who copies `commitIndex` emits `Committed` and does not write `crecs`.

9. `ConfigInEffect` is emitted when an append or a truncation changes the configuration the member is using. Index 0 means the journal has no configuration entry, so the initial configuration is in effect.

10. A coordinator who is sent an extend of its own epoch stays coordinator and applies the entries. A candidate who is sent an extend of an epoch at least its own becomes a follower and then applies them. A higher epoch on any message is adopted first: `epoch` moves up, `votedFor` is cleared, the role becomes follower.

11. The coordinator's own match is not a stored `matchIndex`. The majority count includes the coordinator when the coordinator belongs to the configuration and the index sits in the coordinator's journal. More than half means `2 * count > Cardinality(C)`. A one-member configuration wins inside `Elect`, with no grant. A candidate who is outside its own configuration does not count itself. Grants are accepted only from members of the candidate's configuration. The voter does not consult the voter's own configuration.

12. A crash leaves the network and any queued reply alone. `cut` and `drop` discard a queued reply whose direction is one of the links just failed. `heal` raises every link and does not put those replies back. Link failures accumulate until `heal`. A self-pair in `cut` or `drop` is ignored.

13. A command at a member who is down, who is not coordinator, or whose journal is already at `MaxLogLen`, is taken and appends nothing. It emits no `ChangeRequested`. Every scenario action and every explore fault emits `Fault` from `proc` `env`. That record counts in the event bound. `cut` and `drop` include the resolved directed links.

14. `follower` is each member who is up and is not the coordinator, fixed when the trigger fires. The model branches on every such member. An empty resolution means the trigger does not fire. `crashed` before any crash step, and `coordinator` on step 1 when the trigger is `start`, are rejected by the compiler with `UNEXPLAINED selector ...`. The runner accepts any path and does not look at the file's name.

15. All five members start up, at epoch 0, `votedFor` none, journal empty, role follower, `commitIndex` 0. The configuration each one uses is the scenario's `initial` list until a configuration entry appears in that member's journal. Members outside the initial list are up, so they can be added and so they can themselves call an election.

16. `bound.events` caps the run until every step has been taken. After the last step, the cap becomes the event count at that moment plus `end.settle`, which may sit above `bound.events`. The check explores every behaviour inside those caps, including every prefix. Completion inside the caps with the marker `SCENARIO_DONE` and no violated invariant is `PASS`. A finished check in which no behaviour takes every step is `UNEXPLAINED steps`. The memory cap, an out-of-memory error, or a fingerprint-collision estimate above zero is `UNEXPLAINED bound`.

17. `Fairness` in the module is weak fairness of each member's `Elect` and `SendExtend`, and of taking a reply while the reply's link is up. The configuration checks `Spec`, which has no fairness conjunct. There is no liveness clause to check.

18. On becoming coordinator, `nextIndex` is set to the last index plus one for every member, and `matchIndex` to 0. The self entry is unused. The specification says "every other member."

19. Explore's command set is `{c1}`. Scenario commands are the strings in the scenario file, whatever they are.

## Concerns

From the specification, before any run. Each one names a shape that would show it.

1. Success and failure replies are applied unconditionally. An older success, delivered after a newer one, can move `matchIndex` backward, and a string of failure replies can walk `nextIndex` down. A commit can then count a follower who no longer holds the entry. Shape: one follower, two extend replies in flight, the later applied first, then the earlier success, then a commit of an index that follower has since lost. The one-reply slot in Choices 2 cannot exhibit this. The concern stands, and this model will not produce the trace.

2. A member outside the initial configuration still has that configuration as its own, and the election rule lets that member become coordinator of it. `m5` does not count itself, and three grants from `{m1, m2, m3, m4}` are a majority of four. Shape: no admin request, journals still empty so `m5` is up to date, `m5` times out and is granted by `m1`, `m2`, and `m3`. I do not claim this breaks J1.1 or J1.5. The design allows a coordinator who is not a member of the configuration it leads.

3. The reason given for one-member changes is that any majority of the old configuration overlaps any majority of the new one. That sentence does not mention the up-to-date check or the single vote in an epoch, and overlap of adjacent majorities is the whole of the written argument. The wait (do not append another configuration entry while the previous one is uncommitted) is what keeps a third configuration from being appended beside an uncommitted second. Shape that would show a real break in leader completeness: a configuration entry committed by a majority that excludes the previous coordinator, then a partition, then a new coordinator whose journal lacks that committed entry. S7 is the nearest shared scenario. I predict S7 passes. The concern is that the written justification is thinner than the property.

4. Adding a member who is already in the configuration, or removing one who is absent, has no specified answer. Appending either request would write a configuration equal to the current one, and J1.3 would fail. The model answers `reject` and does not append (Choice 6). Shape, if the append were done: after `Elected`, `{add: m1, at: coordinator}` with `m1` in the initial configuration.

5. A coordinator who hears another coordinator of the same epoch does not step down. The step-down rules are a higher epoch, and a candidate hearing a coordinator of an epoch at least its own. Two coordinators of one epoch stay coordinators. Shape: the `double_vote` mutation, in which two members become coordinator of one epoch. J1.1 has already failed; the design gives no later action that repairs it.


## README section at first-version (ed92c12)
## Concerns after running

The scenario predictions were not edited after these runs. Each unmutated scenario and each mutation printed the predicted line.

S5 is the largest finished scenario: 2,426,356 distinct states, depth 29, 74 seconds. TLC's fingerprint estimate was `8.9E-7`, under the `1e-3` cutoff from amendment 3. S6 finished in 2 seconds at 2,461 states with no behaviour that takes the second election. That matches the prediction written above.

The pre-registered explore envelope did not finish. With `MaxCrashes = 1`, `MaxAdmin = 3`, `MaxLinkFaults = 4`, and an event cap of 400, TLC at diameter 10 held 4,959,972 distinct states and 4,480,694 queued, and was still adding about 2.4 million distinct states a minute. The JVM was stopped. `model/run.sh --explore` printed `UNEXPLAINED bound`. No smaller fault envelope was substituted, so there is no explore PASS to read as coverage of S6's four cuts or S8's three configuration changes. The scenario results above were not changed because of this.

Trace counters had to leave the state view. A cycle can restore the journals, indexes, and roles while bumping `seq`. With the counter in the view, that cycle is a new state on every turn and the scenario graphs do not close. `led`, `crecs`, and `bad` stay in the view.


## Source of the configuration-change path (at first-version)
### model/Journal.tla lines 358-393
```
ReachableLeader(m) ==
  \E l \in M :
    /\ l /= m
    /\ up[l]
    /\ role[l] = "l"
    /\ epoch[l] >= epoch[m]
    /\ lnk[l, m] /\ lnk[m, l]

Campaigning(m) ==
  \E other \in M :
    /\ other /= m
    /\ up[other]
    /\ role[other] = "c"

Elect(m) ==
  /\ up[m]
  /\ role[m] \in {"f", "c"}
  /\ epoch[m] < MaxEpoch
  /\ m \in ConfigOf(journal[m])
  /\ ~ Campaigning(m)
  /\ \/ Mutation = "double_vote"
     \/ ~ ReachableLeader(m)
  /\ LET e == epoch[m] + 1
         C == ConfigOf(journal[m])
         self == IF m \in C THEN 1 ELSE 0
         instant == \/ /\ Mutation = "double_vote" /\ m \in C
                    \/ IsMaj(self, C)
         r0 == [Now EXCEPT !.epoch[m] = e,
                           !.votedFor[m] = m,
                           !.grants[m] = {},
                           !.gseq[m] = seq[m],
                           !.role[m] = "c",
                           !.obs = << >>]
         r1 == IF instant THEN NoteLeader(r0, m) ELSE r0
     IN MemberAfter(r1)

```
### model/Journal.tla lines 673-793
```
ActChange(who, op, target, counting) ==
  /\ who \in M /\ target \in M
  /\ LET sqE == seqEnv + 1
         fe == FaultEv(sqE, op, {})
         reqSq == seq[who] + 1
         req == Ev("ChangeRequested", who, reqSq, 0, 0, "", "", {}, op, target,
                   "", 0, NilCauses)
         replyEv(st, sq) == Ev("ChangeReplied", who, sq, 0, 0, "", "", {}, op,
                               target, st, 0, <<[proc |-> who, seq |-> reqSq]>>)
     IN IF ~ up[who] \/ role[who] /= "l"
        THEN LET sq2 == reqSq + 1
                 r == [Now EXCEPT !.seq[who] = sq2,
                                  !.seqEnv = sqE,
                                  !.obs = <<req, replyEv("not coordinator", sq2), fe>>]
             IN IF counting THEN FinishEnv(r, nCrash, nAdmin + 1, nLink)
                ELSE FinishEnv(r, nCrash, nAdmin, nLink)
        ELSE IF ch[who].phase /= "idle"
        THEN LET sq2 == reqSq + 1
                 r == [Now EXCEPT !.seq[who] = sq2, !.seqEnv = sqE,
                                  !.obs = <<req, replyEv("busy", sq2), fe>>]
             IN IF counting THEN FinishEnv(r, nCrash, nAdmin + 1, nLink)
                ELSE FinishEnv(r, nCrash, nAdmin, nLink)
        ELSE IF \/ /\ op = "add" /\ target \in ConfigOf(journal[who]) /\ Mutation /= "wide_change"
                \/ /\ op = "remove" /\ target \notin ConfigOf(journal[who]) /\ Mutation /= "wide_change"
        THEN LET sq2 == reqSq + 1
                 r == [Now EXCEPT !.seq[who] = sq2, !.seqEnv = sqE,
                                  !.obs = <<req, replyEv("reject", sq2), fe>>]
             IN IF counting THEN FinishEnv(r, nCrash, nAdmin + 1, nLink)
                ELSE FinishEnv(r, nCrash, nAdmin, nLink)
        ELSE
          LET phase1 == IF op = "remove" THEN "waitprev"
                        ELSE IF journal[target] = journal[who] THEN "waitprev"
                        ELSE "catchup"
              r == [Now EXCEPT !.ch[who] = [phase |-> phase1, op |-> op,
                                            target |-> target, rounds |-> 0, idx |-> 0],
                               !.seq[who] = reqSq,
                               !.seqEnv = sqE,
                               !.obs = <<req, fe>>]
          IN IF counting THEN FinishEnv(r, nCrash, nAdmin + 1, nLink)
             ELSE FinishEnv(r, nCrash, nAdmin, nLink)

ScenarioFire ==
  /\ ~Explore
  /\ phase = "ready"
  /\ si >= 1 /\ si <= Len(Steps)
  /\ LET k == pend.kind
     IN \/ /\ k = "crash" /\ pend.target \in M /\ up[pend.target]
           /\ LET fe == FaultEv(seqEnv + 1, "crash", {})
                  r == ActCrashBody([Now EXCEPT !.obs = <<fe>>,
                                               !.seqEnv = seqEnv + 1], pend.target)
              IN FinishEnv(r, nCrash, nAdmin, nLink)
        \/ /\ k = "restart" /\ pend.target \in M /\ ~ up[pend.target]
           /\ LET fe == FaultEv(seqEnv + 1, "restart", {})
                  r == ActRestartBody([Now EXCEPT !.obs = <<fe>>,
                                                  !.seqEnv = seqEnv + 1], pend.target)
              IN FinishEnv(r, nCrash, nAdmin, nLink)
        \/ /\ k = "heal"
           /\ LET fe == FaultEv(seqEnv + 1, "heal", {})
                  r == [Now EXCEPT !.lnk = [d \in M \X M |-> TRUE],
                                  !.obs = <<fe>>,
                                  !.seqEnv = seqEnv + 1]
              IN FinishEnv(r, nCrash, nAdmin, nLink)
        \/ /\ k \in {"cut", "drop"}
           /\ LET downs == pend.links
                  fe == FaultEv(seqEnv + 1, k, downs)
                  r0 == [Now EXCEPT !.lnk = [d \in M \X M |->
                                  IF d \in downs THEN FALSE ELSE lnk[d]],
                                  !.obs = <<fe>>,
                                  !.seqEnv = seqEnv + 1]
                  r == [r0 EXCEPT !.reply = DropReplies(r0, downs)]
              IN FinishEnv(r, nCrash, nAdmin, nLink)
        \/ /\ k = "command"
           /\ ActCommand(pend.at, pend.cmd, FALSE)
        \/ /\ k \in {"add", "remove"}
           /\ ActChange(pend.at, k, pend.target, FALSE)

TimeoutChange(m, status) ==
  LET reqSq == ch[m].op
      sq == seq[m] + 1
      ev == Ev("ChangeReplied", m, sq, 0, 0, "", "", {}, ch[m].op, ch[m].target,
               status, 0, NilCauses)
      r == [Now EXCEPT !.ch[m] = IdleCh, !.seq[m] = sq, !.obs = <<ev>>]
  IN MemberAfter(r)

AppendCfg(m, op, target) ==
  LET C == ConfigOf(journal[m])
      members == NewMembers(op, C, target)
      ent == [kind |-> "config", epoch |-> epoch[m], cmd |-> "", members |-> members]
      idx == Len(journal[m]) + 1
      sq == seq[m] + 1
      evA == Ev("Appended", m, sq, epoch[m], idx, "config", "", members, "", "",
                "", 0, NilCauses)
      sq2 == sq + 1
      evC == Ev("ConfigInEffect", m, sq2, 0, idx, "", "", members, "", "", "", 0,
                <<[proc |-> m, seq |-> sq]>>)
      r == [Now EXCEPT !.journal[m] = Append(journal[m], ent),
                       !.appSeq[m][idx] = sq,
                       !.seq[m] = sq2,
                       !.ch[m] = [phase |-> "waitcommit", op |-> op,
                                  target |-> target, rounds |-> ch[m].rounds,
                                  idx |-> idx],
                       !.obs = <<evA, evC>>]
  IN MemberAfter(r)

FinishChange(m) ==
  LET sq == seq[m] + 1
      ev == Ev("ChangeReplied", m, sq, 0, 0, "", "", {}, ch[m].op, ch[m].target,
               "ok", 0, NilCauses)
      stepdown == ch[m].op = "remove" /\ ch[m].target = m
      r == [Now EXCEPT !.ch[m] = IdleCh,
                       !.seq[m] = sq,
                       !.role[m] = IF stepdown THEN "f" ELSE role[m],
                       !.obs = <<ev>>]
  IN MemberAfter(r)

ChangeTimeout(m) ==
  /\ up[m] /\ role[m] = "l"
  /\ ch[m].phase = "catchup"
  /\ TimeoutChange(m, "timeout")

\* A catch-up round that does not go through the broken CatchupSend conjunction.
```
