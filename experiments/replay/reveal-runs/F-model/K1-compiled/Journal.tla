---- MODULE Journal ----
\* derives: J1.1, J1.3, J1.5, G1.1, G1.2, G1.3, G1.4
\*
\* Specification F, built as written in replay/spec-F.md.
\* Ballot grants are member actions (a request is not buffered): loss is a
\* grant that is never taken, delay is taking it later, reorder is the order
\* of Grant actions, and a repeated grant is idempotent. An extend's reply
\* occupies one slot per follower; a newer send replaces an untaken reply
\* (the replaced reply is lost). See README Choices and Declared limitations.

EXTENDS Integers, Sequences, FiniteSets, TLC

CONSTANTS
  InitialConfig, MaxEpoch, MaxLogLen, MaxRounds, SettleN, MaxEvents,
  Mutation, Explore, MaxCrashes, MaxAdmin, MaxLinkFaults, Commands, Steps

M == {"m1", "m2", "m3", "m4", "m5"}
None == "none"

VARIABLES
  epoch, votedFor, journal, role, commitIndex, nextIndex, matchIndex, up,
  grants, gseq, appSeq, ch, lnk, reply, led, crecs, bad, seq, seqEnv, obs,
  si, phase, pend, events, cap, lastEl, lastCr, nCrash, nAdmin, nLink

vars == <<epoch, votedFor, journal, role, commitIndex, nextIndex, matchIndex,
          up, grants, gseq, appSeq, ch, lnk, reply, led, crecs, bad, seq,
          seqEnv, obs, si, phase, pend, events, cap, lastEl, lastCr, nCrash,
          nAdmin, nLink>>

Min(a, b) == IF a < b THEN a ELSE b
Max(a, b) == IF a > b THEN a ELSE b

IsMaj(cnt, C) == C /= {} /\ 2 * cnt > Cardinality(C)

NoPend == [kind |-> "none", at |-> "", target |-> "", cmd |-> "", links |-> {}]
IdleCh == [phase |-> "idle", op |-> "", target |-> "", rounds |-> 0, idx |-> 0]
NoReply == [valid |-> FALSE, from |-> "", to |-> "", epoch |-> 0,
            success |-> FALSE, match |-> 0]

BlankEntry == [kind |-> "", epoch |-> 0, cmd |-> "", members |-> {}]

\* ---------- journals and configurations ----------

RECURSIVE ScanCfg(_)
ScanCfg(j) ==
  IF Len(j) = 0 THEN [ok |-> FALSE, members |-> InitialConfig, index |-> 0]
  ELSE IF j[Len(j)].kind = "config"
       THEN [ok |-> TRUE, members |-> j[Len(j)].members, index |-> Len(j)]
       ELSE ScanCfg(SubSeq(j, 1, Len(j) - 1))

ConfigOf(j) == ScanCfg(j).members
CfgIndex(j) == ScanCfg(j).index

LastEp(j) == IF Len(j) = 0 THEN 0 ELSE j[Len(j)].epoch

SameEntry(a, b) ==
  /\ a.kind = b.kind
  /\ a.epoch = b.epoch
  /\ a.cmd = b.cmd
  /\ a.members = b.members

UpToDate(cj, vj) ==
  \/ LastEp(cj) > LastEp(vj)
  \/ /\ LastEp(cj) = LastEp(vj)
     /\ Len(cj) >= Len(vj)

RECURSIVE Configs(_)
Configs(j) ==
  IF j = << >> THEN << >>
  ELSE IF Head(j).kind = "config"
       THEN <<Head(j).members>> \o Configs(Tail(j))
       ELSE Configs(Tail(j))

DiffOne(A, B) ==
  \/ /\ A \subseteq B /\ Cardinality(B \ A) = 1
  \/ /\ B \subseteq A /\ Cardinality(A \ B) = 1

PrevCommitted(m) ==
  LET idx == CfgIndex(journal[m])
  IN idx = 0 \/ commitIndex[m] >= idx

\* ---------- observable events ----------

NilCauses == << >>

Ev(event, proc, sq, ep, index, kind, cmd, conf, op, target, status, fr, causes) ==
  [event |-> event, proc |-> proc, seq |-> sq, epoch |-> ep, index |-> index,
   kind |-> kind, cmd |-> cmd, conf |-> conf, op |-> op, target |-> target,
   status |-> status, from |-> fr, causes |-> causes, links |-> {}]

FaultEv(sq, action, links) ==
  [event |-> "Fault", proc |-> "env", seq |-> sq, epoch |-> 0, index |-> 0,
   kind |-> "", cmd |-> "", conf |-> {}, op |-> action, target |-> "",
   status |-> "", from |-> 0, causes |-> NilCauses, links |-> links]

\* ---------- log merge (follower applying an extend) ----------

RECURSIVE AppendFrom(_)
AppendFrom(s) ==
  IF s.i > Len(s.entries) THEN s
  ELSE
    LET idx == s.prev + s.i
        ent == s.entries[s.i]
        sq == s.seq + 1
        cause == IF s.leaderApp[idx] > 0
                 THEN <<[proc |-> s.leader, seq |-> s.leaderApp[idx]]>>
                 ELSE NilCauses
        ev == Ev("Appended", s.proc, sq, ent.epoch, idx, ent.kind, ent.cmd,
                 ent.members, "", "", "", 0, cause)
    IN AppendFrom([s EXCEPT !.log = Append(s.log, ent),
                            !.app = [s.app EXCEPT ![idx] = sq],
                            !.seq = sq,
                            !.evs = Append(s.evs, ev),
                            !.i = s.i + 1])

RECURSIVE Merge(_)
Merge(s) ==
  IF s.i > Len(s.entries) THEN s
  ELSE
    LET idx == s.prev + s.i
        ent == s.entries[s.i]
    IN IF idx > Len(s.log) THEN AppendFrom(s)
       ELSE IF SameEntry(s.log[idx], ent)
            THEN Merge([s EXCEPT !.i = s.i + 1])
            ELSE
              LET truncBad == idx <= s.ci
                  kept == IF idx = 1 THEN << >> ELSE SubSeq(s.log, 1, idx - 1)
                  sq == s.seq + 1
                  tev == Ev("Truncated", s.proc, sq, 0, 0, "", "", {}, "", "",
                            "", idx, NilCauses)
                  cleared == [i \in 1..MaxLogLen |-> IF i >= idx THEN 0 ELSE s.app[i]]
                  s2 == [s EXCEPT !.log = kept,
                                 !.app = cleared,
                                 !.seq = sq,
                                 !.evs = Append(s.evs, tev),
                                 !.bad = s.bad \/ truncBad,
                                 !.trunc = idx]
              IN AppendFrom(s2)

RECURSIVE CommitEvs(_)
CommitEvs(s) ==
  IF s.i > s.n THEN s
  ELSE
    LET ent == s.log[s.i]
        sq == s.seq + 1
        cause == IF s.app[s.i] > 0
                 THEN <<[proc |-> s.proc, seq |-> s.app[s.i]]>>
                 ELSE NilCauses
        ev == Ev("Committed", s.proc, sq, ent.epoch, s.i, ent.kind, ent.cmd,
                 ent.members, "", "", "", 0, cause)
    IN CommitEvs([s EXCEPT !.i = s.i + 1, !.seq = sq,
                           !.evs = Append(s.evs, ev),
                           !.recs = s.recs \cup
                             {[index |-> s.i, kind |-> ent.kind, cmd |-> ent.cmd,
                               members |-> ent.members, entryEpoch |-> ent.epoch,
                               commitEpoch |-> s.cep]}])

\* ---------- scenario resolution ----------

UsesFollower(act) ==
  \/ act.at = "follower"
  \/ act.target = "follower"
  \/ \E i \in 1..Len(act.links) :
       \/ act.links[i][1] = "follower"
       \/ act.links[i][2] = "follower"

SubName(name, fol, el, cr) ==
  IF name = "follower" THEN fol
  ELSE IF name = "coordinator" THEN el
  ELSE IF name = "crashed" THEN cr
  ELSE name

NeedsName(act, name) ==
  \/ act.at = name
  \/ act.target = name
  \/ \E i \in 1..Len(act.links) : act.links[i][1] = name \/ act.links[i][2] = name

BuildPend(act, fol, el, cr) ==
  LET at == SubName(act.at, fol, el, cr)
      tg == SubName(act.target, fol, el, cr)
      n == Len(act.links)
      one(i) == <<SubName(act.links[i][1], fol, el, cr),
                  SubName(act.links[i][2], fol, el, cr)>>
      raw == IF n = 0 THEN {}
             ELSE IF act.kind = "cut"
             THEN {one(i) : i \in 1..n} \cup {<<one(i)[2], one(i)[1]>> : i \in 1..n}
             ELSE {one(i) : i \in 1..n}
      dirs == {d \in raw : d[1] /= d[2] /\ d[1] \in M /\ d[2] \in M}
  IN [kind |-> act.kind, at |-> at, target |-> tg, cmd |-> act.cmd, links |-> dirs]

Resolutions(step, el, cr, upf) ==
  IF step < 1 \/ step > Len(Steps) THEN {}
  ELSE
    LET act == Steps[step].action
        fols == {m \in M : upf[m] /\ m /= el}
        needsF == UsesFollower(act)
        choices == IF needsF THEN fols ELSE {"*"}
    IN IF needsF /\ fols = {} THEN {}
       ELSE IF NeedsName(act, "coordinator") /\ el \notin M THEN {}
       ELSE IF NeedsName(act, "crashed") /\ cr \notin M THEN {}
       ELSE {BuildPend(act, f, el, cr) : f \in choices}

MatchEv(ev, t) ==
  /\ t.kind = "event"
  /\ ev.event = t.event
  /\ (t.member = "" \/ ev.proc = t.member)
  /\ (t.index = -1 \/ ev.index = t.index)
  /\ (t.ekind = "" \/ ev.kind = t.ekind)
  /\ (t.status = "" \/ ev.status = t.status)
  /\ (t.epoch = -1 \/ ev.epoch = t.epoch)
  /\ (t.op = "" \/ ev.op = t.op)
  /\ (t.target = "" \/ ev.target = t.target)

AnyMatch(emitted, t) ==
  \E i \in 1..Len(emitted) : MatchEv(emitted[i], t)

LastOf(emitted, name, prev) ==
  LET hit == {i \in 1..Len(emitted) : emitted[i].event = name}
  IN IF hit = {} THEN prev ELSE emitted[CHOOSE i \in hit : \A j \in hit : j <= i].proc

\* ---------- base record ----------

Now ==
  [epoch |-> epoch, votedFor |-> votedFor, journal |-> journal, role |-> role,
   commitIndex |-> commitIndex, nextIndex |-> nextIndex, matchIndex |-> matchIndex,
   up |-> up, grants |-> grants, gseq |-> gseq, appSeq |-> appSeq, ch |-> ch,
   lnk |-> lnk, reply |-> reply, led |-> led, crecs |-> crecs, bad |-> bad,
   seq |-> seq, seqEnv |-> seqEnv, obs |-> obs, si |-> si, phase |-> phase,
   pend |-> pend, events |-> events, cap |-> cap, lastEl |-> lastEl,
   lastCr |-> lastCr, nCrash |-> nCrash, nAdmin |-> nAdmin, nLink |-> nLink]

Apply(r) ==
  /\ epoch' = r.epoch
  /\ votedFor' = r.votedFor
  /\ journal' = r.journal
  /\ role' = r.role
  /\ commitIndex' = r.commitIndex
  /\ nextIndex' = r.nextIndex
  /\ matchIndex' = r.matchIndex
  /\ up' = r.up
  /\ grants' = r.grants
  /\ gseq' = r.gseq
  /\ appSeq' = r.appSeq
  /\ ch' = r.ch
  /\ lnk' = r.lnk
  /\ reply' = r.reply
  /\ led' = r.led
  /\ crecs' = r.crecs
  /\ bad' = r.bad
  /\ seq' = r.seq
  /\ seqEnv' = r.seqEnv
  /\ obs' = r.obs
  /\ si' = r.si
  /\ phase' = r.phase
  /\ pend' = r.pend
  /\ events' = r.events
  /\ cap' = r.cap
  /\ lastEl' = r.lastEl
  /\ lastCr' = r.lastCr
  /\ nCrash' = r.nCrash
  /\ nAdmin' = r.nAdmin
  /\ nLink' = r.nLink

WithObs(r, emitted, el, cr) ==
  [r EXCEPT !.obs = emitted,
            !.events = r.events + Len(emitted),
            !.lastEl = IF el = "" THEN r.lastEl ELSE el,
            !.lastCr = IF cr = "" THEN r.lastCr ELSE cr]

Arm(r, step, el, cr, upf) ==
  LET res == Resolutions(step, el, cr, upf)
  IN IF step > Len(Steps) THEN
       [r EXCEPT !.phase = "settle", !.si = step, !.pend = NoPend,
                 !.cap = r.events + SettleN]
     ELSE IF Steps[step].trigger.kind = "start" /\ res /= {} THEN
       \* nondet picked by caller; this arm is the deterministic start case
       [r EXCEPT !.phase = "ready", !.si = step]
     ELSE IF Steps[step].trigger.kind = "event" /\ AnyMatch(r.obs, Steps[step].trigger)
             /\ res /= {} THEN
       [r EXCEPT !.phase = "ready", !.si = step]
     ELSE [r EXCEPT !.phase = "wait", !.si = step, !.pend = NoPend]

\* ---------- J1.5(a) at election ----------

Missing(log, ep) ==
  \E rec \in crecs :
    /\ rec.commitEpoch < ep
    /\ \/ rec.index > Len(log)
       \/ ~ SameEntry(log[rec.index],
                      [kind |-> rec.kind, epoch |-> rec.entryEpoch,
                       cmd |-> rec.cmd, members |-> rec.members])

\* Elected causes are built by CauseFrom / WinCauses, in member-name order.

RECURSIVE CauseFrom(_)
CauseFrom(s) ==
  IF s.i > 5 THEN s.out
  ELSE
    LET v == s.vs[s.i]
        take == \/ v \in s.grants
                \/ v = s.self
    IN IF take
       THEN CauseFrom([s EXCEPT !.i = s.i + 1,
                               !.out = Append(s.out, [proc |-> v, seq |-> s.gseq[v]])])
       ELSE CauseFrom([s EXCEPT !.i = s.i + 1])

WinCauses(r, m) ==
  LET C == ConfigOf(r.journal[m])
      grantsC == r.grants[m] \cap C
      self == IF m \in C THEN {m} ELSE {}
  IN CauseFrom([i |-> 1, vs |-> << "m1", "m2", "m3", "m4", "m5" >>,
                out |-> << >>, grants |-> grantsC \cup self,
                self |-> "", gseq |-> r.gseq])

NoteLeader(r, m) ==
  LET ep == r.epoch[m]
      sq == r.seq[m] + 1
      ev == Ev("Elected", m, sq, ep, 0, "", "", ConfigOf(r.journal[m]),
               "", "", "", 0, WinCauses(r, m))
      bad1 == IF Missing(r.journal[m], ep) THEN "J1.5" ELSE r.bad
  IN [r EXCEPT !.role[m] = "l",
              !.led = r.led \cup {<<ep, m>>},
              !.seq[m] = sq,
              !.obs = Append(r.obs, ev),
              !.nextIndex[m] = [p \in M |-> Len(r.journal[m]) + 1],
              !.matchIndex[m] = [p \in M |-> 0],
              !.bad = bad1,
              !.grants[m] = r.grants[m]]

\* ---------- actions ----------

\* MemberAfter wires scenario trigger detection for non-env actions.
MemberAfter(r) ==
  IF Explore
  THEN Apply([r EXCEPT !.events = events + Len(r.obs),
                       !.lastEl = LastOf(r.obs, "Elected", lastEl)])
  ELSE IF phase = "ready" \/ phase = "settle"
  THEN Apply([r EXCEPT !.events = events + Len(r.obs),
                       !.lastEl = LastOf(r.obs, "Elected", lastEl),
                       !.cap = cap, !.si = si, !.phase = phase, !.pend = pend])
  ELSE
    LET el == LastOf(r.obs, "Elected", lastEl)
        rE == [r EXCEPT !.events = events + Len(r.obs), !.lastEl = el]
        trig == IF si <= Len(Steps) THEN Steps[si].trigger ELSE [kind |-> "none"]
        res == IF si <= Len(Steps) THEN Resolutions(si, el, lastCr, up) ELSE {}
        fire == trig.kind = "event" /\ AnyMatch(r.obs, trig) /\ res /= {}
    IN IF fire
       THEN \E p \in res : Apply([rE EXCEPT !.phase = "ready", !.pend = p])
       ELSE Apply(rE)

\* Bounds, recorded in the README amendments. A member outside its own
\* configuration does not campaign. A member who can exchange messages with
\* an up coordinator of an epoch at least its own does not campaign, whether
\* or not that coordinator's configuration includes the member. A member does
\* not start a campaign while another up member is already a candidate.
\* double_vote ignores the reachable-coordinator half, and its Elect ends as
\* coordinator, so a second coordinator of the same epoch can still be elected.
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

Grant(v, c) ==
  /\ up[v] /\ up[c]
  /\ v /= c
  /\ role[c] = "c"
  /\ lnk[c, v] /\ lnk[v, c]
  /\ v \in ConfigOf(journal[c])
  /\ LET higher == epoch[c] > epoch[v]
         e1 == IF higher THEN epoch[c] ELSE epoch[v]
         vf == IF higher THEN None ELSE votedFor[v]
         voteOk == \/ Mutation = "double_vote"
                   \/ vf = None
                   \/ vf = c
         logOk == \/ Mutation = "skip_uptodate"
                  \/ UpToDate(journal[c], journal[v])
     IN /\ epoch[c] >= e1
        /\ voteOk
        /\ logOk
        /\ LET r0 == [Now EXCEPT !.epoch[v] = e1,
                                 !.votedFor[v] = c,
                                 !.role[v] = "f",
                                 !.gseq[v] = seq[v],
                                 !.grants[c] = grants[c] \cup {v},
                                 !.obs = << >>]
               C == ConfigOf(journal[c])
               cnt == Cardinality((grants[c] \cup {v}) \cap C)
                      + IF c \in C THEN 1 ELSE 0
               win == role[c] /= "l" /\ IsMaj(cnt, C)
               r1 == IF win THEN NoteLeader([r0 EXCEPT !.gseq[v] = seq[v]], c) ELSE r0
           IN MemberAfter(r1)

Learn(v, c) ==
  /\ up[v] /\ up[c]
  /\ role[c] = "c"
  /\ v /= c
  /\ lnk[c, v] /\ lnk[v, c]
  /\ v \in ConfigOf(journal[c])
  /\ epoch[v] > epoch[c]
  /\ LET r == [Now EXCEPT !.epoch[c] = epoch[v],
                          !.role[c] = "f",
                          !.votedFor[c] = None,
                          !.grants[c] = {},
                          !.obs = << >>]
     IN MemberAfter(r)

\* Apply leader m's extend to follower dst. Returns an updated Now-record
\* for the follower's state and a reply slot. Leader matchIndex is untouched.
SendExtend(m, dst) ==
  /\ up[m] /\ up[dst] /\ m /= dst
  /\ role[m] = "l"
  /\ lnk[m, dst]
  /\ \/ dst \in ConfigOf(journal[m])
     \/ /\ ch[m].phase = "catchup"
        /\ ch[m].target = dst
  /\ matchIndex[m][dst] < Len(journal[m]) \/ nextIndex[m][dst] <= Len(journal[m])
  /\ LET ni == nextIndex[m][dst]
         prev == ni - 1
         prevEp == IF prev <= 0 THEN 0 ELSE journal[m][prev].epoch
         entries == IF \/ ni > Len(journal[m])
                       \/ ni < 1
                    THEN << >>
                    ELSE SubSeq(journal[m], ni, Len(journal[m]))
         higher == epoch[dst] > epoch[m]
     IN IF higher
        THEN \* The follower's epoch is higher. The coordinator steps down in
             \* this action. The reply is not a separate state. See README.
             LET r == [Now EXCEPT !.epoch[m] = epoch[dst],
                                  !.role[m] = "f",
                                  !.votedFor[m] = None,
                                  !.grants[m] = {},
                                  !.reply[dst] = NoReply,
                                  !.obs = << >>]
             IN MemberAfter(r)
        ELSE
          LET newEp == Max(epoch[dst], epoch[m])
              newVF == IF epoch[m] > epoch[dst] THEN None ELSE votedFor[dst]
              newRole == IF epoch[m] > epoch[dst] THEN "f"
                         ELSE IF role[dst] = "c" /\ epoch[m] >= epoch[dst] THEN "f"
                         ELSE role[dst]
              prevOk == \/ prev = 0
                        \/ /\ prev <= Len(journal[dst])
                           /\ journal[dst][prev].epoch = prevEp
          IN IF ~ prevOk
             THEN LET r == [Now EXCEPT !.epoch[dst] = newEp,
                                       !.votedFor[dst] = newVF,
                                       !.role[dst] = newRole,
                                       !.nextIndex[m][dst] = Max(1, nextIndex[m][dst] - 1),
                                       !.reply[dst] = NoReply,
                                       !.obs = << >>]
                  IN MemberAfter(r)
             ELSE
               LET s0 == [log |-> journal[dst], app |-> appSeq[dst],
                          seq |-> seq[dst], evs |-> << >>, bad |-> FALSE,
                          i |-> 1, prev |-> prev, entries |-> entries,
                          proc |-> dst, leader |-> m, leaderApp |-> appSeq[m],
                          ci |-> commitIndex[dst], trunc |-> 0]
                   s1 == IF entries = << >> THEN s0 ELSE Merge(s0)
                   last == prev + Len(entries)
                   newCI == IF epoch[m] = newEp /\ commitIndex[m] > commitIndex[dst]
                            THEN Min(commitIndex[m], last)
                            ELSE commitIndex[dst]
                   s2 == IF newCI > commitIndex[dst]
                         THEN CommitEvs([log |-> s1.log, app |-> s1.app,
                                         seq |-> s1.seq, evs |-> s1.evs,
                                         i |-> commitIndex[dst] + 1, n |-> newCI,
                                         proc |-> dst, recs |-> {},
                                         cep |-> epoch[m]])
                         ELSE [evs |-> s1.evs, seq |-> s1.seq, recs |-> {},
                               app |-> s1.app]
                   oldC == ConfigOf(journal[dst])
                   newC == ConfigOf(s1.log)
                   oldI == CfgIndex(journal[dst])
                   newI == CfgIndex(s1.log)
                   sqC == s2.seq + 1
                   cfgEv == IF oldC /= newC
                            THEN Ev("ConfigInEffect", dst, sqC, 0, newI, "", "",
                                    newC, "", "", "", 0,
                                    IF s1.trunc > 0 /\ s1.seq > seq[dst]
                                    THEN <<[proc |-> dst, seq |->
                                            (CHOOSE q \in 1..s1.seq :
                                               \E k \in 1..Len(s1.evs) :
                                                 s1.evs[k].event = "Truncated"
                                                 /\ s1.evs[k].seq = q)]>>
                                    ELSE IF \E k \in 1..Len(s1.evs) :
                                              s1.evs[k].event = "Appended"
                                         THEN <<[proc |-> dst,
                                                 seq |-> s1.evs[CHOOSE k \in 1..Len(s1.evs) :
                                                   s1.evs[k].event = "Appended"
                                                   /\ \A j \in 1..Len(s1.evs) :
                                                     s1.evs[j].event = "Appended" => j <= k].seq]>>
                                         ELSE NilCauses)
                            ELSE [event |-> ""]
                   evs == IF oldC /= newC THEN Append(s2.evs, cfgEv) ELSE s2.evs
                   seqF == IF oldC /= newC THEN sqC ELSE s2.seq
                   r == [Now EXCEPT !.epoch[dst] = newEp,
                                    !.votedFor[dst] = newVF,
                                    !.role[dst] = newRole,
                                    !.journal[dst] = s1.log,
                                    !.appSeq[dst] = s2.app,
                                    !.seq[dst] = seqF,
                                    !.commitIndex[dst] = newCI,
                                    !.matchIndex[m][dst] = last,
                                    !.nextIndex[m][dst] = last + 1,
                                    !.reply[dst] = NoReply,
                                    !.bad = IF s1.bad THEN "J1.5" ELSE bad,
                                    !.obs = evs,
                                    !.grants[dst] = IF newRole = "f" /\ role[dst] = "c"
                                                    THEN {} ELSE grants[dst]]
               IN MemberAfter(r)

TakeReply(dst) ==
  /\ reply[dst].valid
  /\ up[reply[dst].to]
  /\ lnk[reply[dst].from, reply[dst].to]
  /\ LET rpy == reply[dst]
         ldr == rpy.to
     IN IF rpy.epoch > epoch[ldr]
        THEN LET r == [Now EXCEPT !.epoch[ldr] = rpy.epoch,
                                  !.role[ldr] = "f",
                                  !.votedFor[ldr] = None,
                                  !.grants[ldr] = {},
                                  !.reply[dst] = NoReply,
                                  !.obs = << >>]
             IN MemberAfter(r)
        ELSE IF role[ldr] = "l"
             THEN LET r == IF rpy.success
                           THEN [Now EXCEPT !.matchIndex[ldr][dst] = rpy.match,
                                             !.nextIndex[ldr][dst] = rpy.match + 1,
                                             !.reply[dst] = NoReply,
                                             !.obs = << >>]
                           ELSE [Now EXCEPT !.nextIndex[ldr][dst] =
                                            Max(1, nextIndex[ldr][dst] - 1),
                                             !.reply[dst] = NoReply,
                                             !.obs = << >>]
                  IN MemberAfter(r)
             ELSE LET r == [Now EXCEPT !.reply[dst] = NoReply, !.obs = << >>]
                  IN MemberAfter(r)

MajorityHas(m, n) ==
  LET C == ConfigOf(journal[m])
      have == {p \in C \ {m} : matchIndex[m][p] >= n}
      cnt == Cardinality(have) + IF m \in C /\ n <= Len(journal[m]) THEN 1 ELSE 0
  IN IsMaj(cnt, C)

AdvanceCommit(m) ==
  /\ up[m] /\ role[m] = "l"
  /\ LET goods == {n \in (commitIndex[m] + 1)..Len(journal[m]) :
                     /\ journal[m][n].epoch = epoch[m]
                     /\ MajorityHas(m, n)}
     IN /\ goods /= {}
        /\ LET N == CHOOSE n \in goods : \A k \in goods : k <= n
               s == CommitEvs([log |-> journal[m], app |-> appSeq[m],
                               seq |-> seq[m], evs |-> << >>,
                               i |-> commitIndex[m] + 1, n |-> N,
                               proc |-> m, recs |-> {}, cep |-> epoch[m]])
               r0 == [Now EXCEPT !.commitIndex[m] = N,
                                 !.seq[m] = s.seq,
                                 !.crecs = crecs \cup s.recs,
                                 !.obs = s.evs]
               r1 == IF Mutation = "skip_uptodate"
                     THEN [r0 EXCEPT !.journal[m] = << >>,
                                     !.bad = "J1.5",
                                     !.appSeq[m] = [i \in 1..MaxLogLen |-> 0]]
                     ELSE r0
           IN MemberAfter(r1)

OneExtra(S) == IF S = {} THEN {} ELSE {CHOOSE x \in S : TRUE}

NewMembers(op, C, target) ==
  IF Mutation = "wide_change"
  THEN IF op = "add"
       THEN C \cup {target} \cup OneExtra(M \ (C \cup {target}))
       ELSE C \ ({target} \cup OneExtra(C \ {target}))
  ELSE IF op = "add" THEN C \cup {target} ELSE C \ {target}

\* ---------- environment ----------

DropReplies(r, down) ==
  [d \in M |-> IF r.reply[d].valid /\ <<r.reply[d].from, r.reply[d].to>> \in down
               THEN NoReply ELSE r.reply[d]]

ActCrashBody(r, m) ==
  [r EXCEPT !.up[m] = FALSE, !.lastCr = m]

ActRestartBody(r, m) ==
  [r EXCEPT !.up[m] = TRUE,
            !.role[m] = "f",
            !.commitIndex[m] = 0,
            !.grants[m] = {},
            !.nextIndex[m] = [p \in M |-> 1],
            !.matchIndex[m] = [p \in M |-> 0],
            !.ch[m] = IdleCh]

FinishEnv(r, crashN, adminN, linkN) ==
  LET el == r.lastEl
      cr == r.lastCr
      r1 == [r EXCEPT !.nCrash = crashN, !.nAdmin = adminN, !.nLink = linkN,
                      !.events = events + Len(r.obs)]
  IN IF Explore
     THEN Apply(r1)
     ELSE IF si >= Len(Steps)
       THEN /\ PrintT("SCENARIO_DONE")
            /\ Apply([r1 EXCEPT !.phase = "settle",
                               !.si = si + 1,
                               !.pend = NoPend,
                               !.cap = r1.events + SettleN])
       ELSE
         LET nsi == si + 1
             trig == Steps[nsi].trigger
             res == Resolutions(nsi, el, cr, r.up)
             sync == trig.kind = "event" /\ AnyMatch(r.obs, trig) /\ res /= {}
             start == trig.kind = "start" /\ res /= {}
         IN IF sync \/ start
            THEN \E p \in res :
                   Apply([r1 EXCEPT !.phase = "ready", !.si = nsi, !.pend = p])
            ELSE Apply([r1 EXCEPT !.phase = "wait", !.si = nsi, !.pend = NoPend])

ActCommand(who, cmd, counting) ==
  /\ who \in M
  /\ LET fe == FaultEv(seqEnv + 1, "command", {})
     IN IF ~ up[who] \/ role[who] /= "l" \/ Len(journal[who]) >= MaxLogLen
        THEN LET r == [Now EXCEPT !.obs = <<fe>>, !.seqEnv = seqEnv + 1]
             IN IF counting
                THEN FinishEnv([r EXCEPT !.nAdmin = nAdmin + 1], nCrash, nAdmin + 1, nLink)
                ELSE FinishEnv(r, nCrash, nAdmin, nLink)
        ELSE
          LET ent == [kind |-> "command", epoch |-> epoch[who], cmd |-> cmd, members |-> {}]
              idx == Len(journal[who]) + 1
              sq == seq[who] + 1
              ev == Ev("Appended", who, sq, epoch[who], idx, "command", cmd, {},
                       "", "", "", 0, NilCauses)
              r == [Now EXCEPT !.journal[who] = Append(journal[who], ent),
                               !.appSeq[who][idx] = sq,
                               !.seq[who] = sq,
                               !.seqEnv = seqEnv + 1,
                               !.obs = <<ev, fe>>]
          IN IF counting
             THEN FinishEnv(r, nCrash, nAdmin + 1, nLink)
             ELSE FinishEnv(r, nCrash, nAdmin, nLink)

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
CatchupRound(m) ==
  /\ up[m] /\ role[m] = "l"
  /\ ch[m].phase = "catchup"
  /\ ch[m].rounds < MaxRounds
  /\ journal[ch[m].target] /= journal[m]
  /\ up[ch[m].target]
  /\ lnk[m, ch[m].target]
  /\ LET target == ch[m].target
         ni0 == nextIndex[m][target]
         ni == IF ni0 > Len(journal[m]) + 1 THEN Len(journal[m]) + 1
               ELSE IF ni0 < 1 THEN 1 ELSE ni0
         prev == ni - 1
         prevEp == IF prev <= 0 THEN 0 ELSE journal[m][prev].epoch
         entries == IF ni > Len(journal[m]) THEN << >>
                    ELSE SubSeq(journal[m], ni, Len(journal[m]))
         dst == target
         higher == epoch[dst] > epoch[m]
     IN IF higher
        THEN LET r == [Now EXCEPT !.epoch[m] = epoch[dst],
                                  !.role[m] = "f",
                                  !.votedFor[m] = None,
                                  !.grants[m] = {},
                                  !.reply[dst] = NoReply,
                                  !.ch[m].rounds = ch[m].rounds + 1,
                                  !.obs = << >>]
             IN MemberAfter(r)
        ELSE
          LET newEp == Max(epoch[dst], epoch[m])
              newVF == IF epoch[m] > epoch[dst] THEN None ELSE votedFor[dst]
              newRole == IF epoch[m] > epoch[dst] THEN "f"
                         ELSE IF role[dst] = "c" /\ epoch[m] >= epoch[dst] THEN "f"
                         ELSE role[dst]
              prevOk == \/ prev = 0
                        \/ /\ prev <= Len(journal[dst])
                           /\ journal[dst][prev].epoch = prevEp
          IN IF ~ prevOk
             THEN LET r == [Now EXCEPT !.epoch[dst] = newEp,
                                       !.votedFor[dst] = newVF,
                                       !.role[dst] = newRole,
                                       !.nextIndex[m][dst] = Max(1, nextIndex[m][dst] - 1),
                                       !.reply[dst] = NoReply,
                                       !.ch[m].rounds = ch[m].rounds + 1,
                                       !.obs = << >>]
                  IN MemberAfter(r)
             ELSE
               LET s0 == [log |-> journal[dst], app |-> appSeq[dst],
                          seq |-> seq[dst], evs |-> << >>, bad |-> FALSE,
                          i |-> 1, prev |-> prev, entries |-> entries,
                          proc |-> dst, leader |-> m, leaderApp |-> appSeq[m],
                          ci |-> commitIndex[dst], trunc |-> 0]
                   s1 == IF entries = << >> THEN s0 ELSE Merge(s0)
                   last == prev + Len(entries)
                   newCI == IF epoch[m] = newEp /\ commitIndex[m] > commitIndex[dst]
                            THEN Min(commitIndex[m], last) ELSE commitIndex[dst]
                   s2 == IF newCI > commitIndex[dst]
                         THEN CommitEvs([log |-> s1.log, app |-> s1.app,
                                         seq |-> s1.seq, evs |-> s1.evs,
                                         i |-> commitIndex[dst] + 1, n |-> newCI,
                                         proc |-> dst, recs |-> {}, cep |-> epoch[m]])
                         ELSE [evs |-> s1.evs, seq |-> s1.seq, recs |-> {}, app |-> s1.app]
                   oldC == ConfigOf(journal[dst])
                   newC == ConfigOf(s1.log)
                   sqC == s2.seq + 1
                   \* cause: last Appended or the Truncated in s1.evs
                   cause == IF \E k \in 1..Len(s1.evs) : s1.evs[k].event = "Appended"
                            THEN <<[proc |-> dst, seq |->
                                    s1.evs[CHOOSE k \in 1..Len(s1.evs) :
                                      /\ s1.evs[k].event = "Appended"
                                      /\ \A j \in 1..Len(s1.evs) :
                                           s1.evs[j].event = "Appended" => j <= k].seq]>>
                            ELSE IF \E k \in 1..Len(s1.evs) : s1.evs[k].event = "Truncated"
                                 THEN <<[proc |-> dst, seq |->
                                         s1.evs[CHOOSE k \in 1..Len(s1.evs) :
                                           s1.evs[k].event = "Truncated"].seq]>>
                                 ELSE NilCauses
                   evs == IF oldC /= newC
                          THEN Append(s2.evs,
                                 Ev("ConfigInEffect", dst, sqC, 0, CfgIndex(s1.log),
                                    "", "", newC, "", "", "", 0, cause))
                          ELSE s2.evs
                   seqF == IF oldC /= newC THEN sqC ELSE s2.seq
                   r == [Now EXCEPT !.epoch[dst] = newEp,
                                    !.votedFor[dst] = newVF,
                                    !.role[dst] = newRole,
                                    !.journal[dst] = s1.log,
                                    !.appSeq[dst] = s2.app,
                                    !.seq[dst] = seqF,
                                    !.commitIndex[dst] = newCI,
                                    !.matchIndex[m][dst] = last,
                                    !.nextIndex[m][dst] = last + 1,
                                    !.reply[dst] = NoReply,
                                    !.bad = IF s1.bad THEN "J1.5" ELSE bad,
                                    !.ch[m].rounds = ch[m].rounds + 1,
                                    !.obs = evs,
                                    !.grants[dst] = IF newRole = "f" /\ role[dst] = "c"
                                                    THEN {} ELSE grants[dst]]
               IN MemberAfter(r)

ExploreCrash(m) ==
  /\ Explore /\ up[m] /\ nCrash < MaxCrashes
  /\ LET fe == FaultEv(seqEnv + 1, "crash", {})
         r == ActCrashBody([Now EXCEPT !.obs = <<fe>>, !.seqEnv = seqEnv + 1], m)
     IN FinishEnv(r, nCrash + 1, nAdmin, nLink)

ExploreRestart(m) ==
  /\ Explore /\ ~ up[m]
  /\ LET fe == FaultEv(seqEnv + 1, "restart", {})
         r == ActRestartBody([Now EXCEPT !.obs = <<fe>>, !.seqEnv = seqEnv + 1], m)
     IN FinishEnv(r, nCrash, nAdmin, nLink)

ExploreCommand(m, c) ==
  /\ Explore /\ nAdmin < MaxAdmin /\ c \in Commands
  /\ ActCommand(m, c, TRUE)

ExploreChange(m, op, t) ==
  /\ Explore /\ nAdmin < MaxAdmin /\ m \in M /\ t \in M /\ op \in {"add", "remove"}
  /\ ActChange(m, op, t, TRUE)

ExploreCut(a, b) ==
  /\ Explore /\ nLink < MaxLinkFaults /\ a \in M /\ b \in M /\ a /= b
  /\ LET downs == {<<a, b>>, <<b, a>>}
         links == {<<a, b>>, <<b, a>>}
         fe == FaultEv(seqEnv + 1, "cut", links)
         r0 == [Now EXCEPT !.lnk = [d \in M \X M |-> IF d \in downs THEN FALSE ELSE lnk[d]],
                         !.obs = <<fe>>, !.seqEnv = seqEnv + 1]
         r == [r0 EXCEPT !.reply = DropReplies(r0, downs)]
     IN FinishEnv(r, nCrash, nAdmin, nLink + 1)

ExploreDrop(a, b) ==
  /\ Explore /\ nLink < MaxLinkFaults /\ a \in M /\ b \in M /\ a /= b
  /\ LET downs == {<<a, b>>}
         links == {<<a, b>>}
         fe == FaultEv(seqEnv + 1, "drop", links)
         r0 == [Now EXCEPT !.lnk = [d \in M \X M |-> IF d \in downs THEN FALSE ELSE lnk[d]],
                         !.obs = <<fe>>, !.seqEnv = seqEnv + 1]
         r == [r0 EXCEPT !.reply = DropReplies(r0, downs)]
     IN FinishEnv(r, nCrash, nAdmin, nLink + 1)

ExploreHeal ==
  /\ Explore
  /\ \E a, b \in M : a /= b /\ ~ lnk[a, b]
  /\ LET fe == FaultEv(seqEnv + 1, "heal", {})
         r == [Now EXCEPT !.lnk = [d \in M \X M |-> TRUE],
                         !.obs = <<fe>>, !.seqEnv = seqEnv + 1]
     IN FinishEnv(r, nCrash, nAdmin, nLink)

Next ==
  \/ \E m \in M : Elect(m)
  \/ \E v \in M, c \in M : Grant(v, c)
  \/ \E v \in M, c \in M : Learn(v, c)
  \/ \E m \in M, d \in M : SendExtend(m, d)
  \/ \E d \in M : TakeReply(d)
  \/ \E m \in M : AdvanceCommit(m)
  \/ \E m \in M : \/ /\ ch[m].phase = "catchup"
                    /\ journal[ch[m].target] = journal[m]
                    /\ up[m] /\ role[m] = "l"
                    /\ MemberAfter([Now EXCEPT !.ch[m].phase = "waitprev", !.obs = << >>])
                 \/ /\ ch[m].phase = "catchup"
                    /\ journal[ch[m].target] /= journal[m]
                    /\ ch[m].rounds >= MaxRounds
                    /\ up[m] /\ role[m] = "l"
                    /\ TimeoutChange(m, "timeout")
                 \/ CatchupRound(m)
                 \/ /\ ch[m].phase = "waitprev"
                    /\ up[m] /\ role[m] = "l"
                    /\ PrevCommitted(m)
                    /\ Len(journal[m]) < MaxLogLen
                    /\ AppendCfg(m, ch[m].op, ch[m].target)
                 \/ /\ ch[m].phase = "waitcommit"
                    /\ up[m] /\ role[m] = "l"
                    /\ commitIndex[m] >= ch[m].idx
                    /\ FinishChange(m)
  \/ \E m \in M : ChangeTimeout(m)
  \/ ScenarioFire
  \/ \E m \in M : ExploreCrash(m)
  \/ \E m \in M : ExploreRestart(m)
  \/ \E m \in M, c \in Commands : ExploreCommand(m, c)
  \/ \E m \in M, t \in M, op \in {"add", "remove"} : ExploreChange(m, op, t)
  \/ \E a \in M, b \in M : ExploreCut(a, b)
  \/ \E a \in M, b \in M : ExploreDrop(a, b)
  \/ ExploreHeal

\* ---------- invariants (derives: J1.1, J1.3, J1.5) ----------

J11 == \A e \in 1..MaxEpoch : Cardinality({m \in M : <<e, m>> \in led}) <= 1

J13 ==
  \A m \in M :
    LET cs == <<InitialConfig>> \o Configs(journal[m])
    IN \A i \in 1..(Len(cs) - 1) : DiffOne(cs[i], cs[i + 1])

J15 == bad = "none"

StateConstraint ==
  /\ events <= cap
  /\ \A m \in M : Len(journal[m]) <= MaxLogLen
  /\ \A m \in M : epoch[m] <= MaxEpoch

\* Trace counters are not part of state identity. A cycle that restores the
\* protocol state and only bumps these counters is one state. led, crecs, and
\* bad stay in the view, so J1.1 and J1.5 still see them. The stored state
\* still carries obs and seq, and the observe file is rebuilt from the trace.
\* Recorded in the README.
View == <<epoch, votedFor, journal, role, commitIndex, nextIndex, matchIndex,
          up, grants, ch, lnk, reply, led, crecs, bad, si, phase, pend, cap,
          lastEl, lastCr, nCrash, nAdmin, nLink>>

\* Fairness is stated and not used. The checker assumes none: the contract has
\* no liveness clause, and a fairness assumption would only hide safety
\* violations. What is allowed, were liveness checked, is weak fairness of each
\* member's own actions and of reply delivery while the reply's link is up.
\* derives: G1.2, failure-model clocks.
MemberStep(m) ==
  \/ Elect(m)
  \/ \E v \in M : Grant(v, m)
  \/ \E c \in M : Grant(m, c)
  \/ \E d \in M : SendExtend(m, d)
  \/ AdvanceCommit(m)
  \/ ChangeTimeout(m)

Fairness ==
  /\ \A m \in M : WF_vars(Elect(m))
  /\ \A m \in M : WF_vars(\E d \in M : SendExtend(m, d))
  /\ \A d \in M : WF_vars(TakeReply(d) /\ lnk[reply[d].from, reply[d].to])

Init ==
  /\ epoch = [m \in M |-> 0]
  /\ votedFor = [m \in M |-> None]
  /\ journal = [m \in M |-> << >>]
  /\ role = [m \in M |-> "f"]
  /\ commitIndex = [m \in M |-> 0]
  /\ nextIndex = [m \in M |-> [p \in M |-> 1]]
  /\ matchIndex = [m \in M |-> [p \in M |-> 0]]
  /\ up = [m \in M |-> TRUE]
  /\ grants = [m \in M |-> {}]
  /\ gseq = [m \in M |-> 0]
  /\ appSeq = [m \in M |-> [i \in 1..MaxLogLen |-> 0]]
  /\ ch = [m \in M |-> IdleCh]
  /\ lnk = [d \in M \X M |-> TRUE]
  /\ reply = [m \in M |-> NoReply]
  /\ led = {}
  /\ crecs = {}
  /\ bad = "none"
  /\ seq = [m \in M |-> 0]
  /\ seqEnv = 0
  /\ obs = << >>
  /\ events = 0
  /\ cap = MaxEvents
  /\ lastEl = None
  /\ lastCr = None
  /\ nCrash = 0
  /\ nAdmin = 0
  /\ nLink = 0
  /\ IF Explore \/ Len(Steps) = 0
     THEN /\ si = 1 /\ phase = "wait" /\ pend = NoPend
          /\ IF ~Explore /\ Len(Steps) = 0 THEN PrintT("SCENARIO_DONE") ELSE TRUE
     ELSE /\ si = 1
          /\ IF Steps[1].trigger.kind = "start"
             THEN /\ phase = "ready"
                  /\ pend \in Resolutions(1, None, None, [m \in M |-> TRUE])
             ELSE /\ phase = "wait" /\ pend = NoPend

Spec == Init /\ [][Next]_vars
\* FairSpec is not checked. See Fairness above.
FairSpec == Spec /\ Fairness

====
