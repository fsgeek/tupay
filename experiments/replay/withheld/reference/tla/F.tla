---------------------------- MODULE F ----------------------------
(***************************************************************************)
(* Reference model of replay/spec-F.md, with the scenario driver of        *)
(* replay/scenario-format.md and checkers for contract v2.                 *)
(* Validation tool for the replay inputs; not an experimental artifact.    *)
(* derives: J1.1, J1.3, J1.4, G1.1, G1.2, G1.3, G1.4                       *)
(*                                                                         *)
(* Variants (constant Gated):                                              *)
(*   SPEC  (Gated = FALSE): spec F as written.                             *)
(*   GATED (Gated = TRUE) : SPEC plus (i) a new coordinator appends one    *)
(*     no-op command entry on election; (ii) a coordinator does not append *)
(*     a configuration entry until its commitIndex covers an entry of its  *)
(*     own epoch. Nothing else differs.                                    *)
(*                                                                         *)
(* Network (G1.2, G1.3). msgs holds requests (ballot RV, extend AE). A     *)
(* request stays in msgs after delivery, so it can be delivered again      *)
(* (duplication), at any later point (delay, reordering) or never (loss). *)
(* The reply is processed atomically with the request's delivery, or lost  *)
(* (two transitions). Requests that can never again change anything are    *)
(* removed (Dead); the sender's retry (ResendRV, SendAE) re-creates the    *)
(* current request whenever it is not in flight. A coordinator sends its   *)
(* current extend request to each target whenever its state changes.       *)
(* A link that is down loses what is sent over it and holds what was in   *)
(* flight on it until it is healed.                                        *)
(***************************************************************************)
EXTENDS Integers, Sequences, FiniteSets, TLC

CONSTANTS Steps,   \* sequence of [at |-> trigger record, act |-> action record]
          Init0,   \* initial configuration (set of member names)
          Gated,   \* BOOLEAN: GATED variant
          MaxE,    \* bound: highest epoch
          MaxT,    \* bound: total election timeouts
          MaxJ,    \* bound: journal length
          Settle   \* bound: events after the last step's action

M == {"m1", "m2", "m3", "m4", "m5"}
None == "none"
NS == Len(Steps)
Zero == [j \in M |-> 0]
NoCh == [op |-> "none", t |-> None, ph |-> "none", idx |-> 0]
NoAct == [op |-> "none", t |-> None, at |-> None, links |-> {}, cmd |-> ""]

Max(S) == CHOOSE x \in S : \A y \in S : y <= x
Min(S) == CHOOSE x \in S : \A y \in S : x <= y

VARIABLES st,      \* [M -> member record]
          msgs,    \* set of requests in the network
          down,    \* set of directed links <<a, b>> that are down
          elec,    \* ghost: set of [e, m, j]: m elected coordinator of epoch e with journal j
          comm,    \* ghost: set of [idx, ent, e]: a coordinator of epoch e committed ent at idx
          bad13,   \* ghost: a J1.3 violation has been witnessed
          bad14b,  \* ghost: a J1.4(b) violation has been witnessed
          tmo,     \* bound counter: election timeouts so far
          stp,     \* scenario: index of the armed step (NS+1 once every step is taken)
          pend,    \* scenario: resolved action of a fired step, not yet taken (or NoAct)
          lastE,   \* scenario: member most recently Elected
          lastC,   \* scenario: member most recently crashed by a crash step
          settle   \* scenario: events since the last step's action

vars == <<st, msgs, down, elec, comm, bad13, bad14b, tmo, stp, pend, lastE, lastC, settle>>

------------------------------------------------------------------------------
(* Journals and configurations *)
CmdE(e, c) == [ep |-> e, isc |-> FALSE, mem |-> {}, cmd |-> c]
CfgE(e, C) == [ep |-> e, isc |-> TRUE, mem |-> C, cmd |-> ""]
LastEp(J) == IF Len(J) = 0 THEN 0 ELSE J[Len(J)].ep
CfgIdx(J) == LET S == {k \in 1..Len(J) : J[k].isc} IN IF S = {} THEN 0 ELSE Max(S)
CfgOf(J) == IF CfgIdx(J) = 0 THEN Init0 ELSE J[CfgIdx(J)].mem
Maj(S, C) == 2 * Cardinality(S \cap C) > Cardinality(C)
UpToDate(lidx, lep, J) == lep > LastEp(J) \/ (lep = LastEp(J) /\ lidx >= Len(J))
CP(J, K) == Max({k \in 0..Min({Len(J), Len(K)}) : \A x \in 1..k : J[x] = K[x]})

\* J1.3: each configuration entry differs from its predecessor in the same journal
\* (or the initial configuration, for the first) by exactly one member.
J13ok(K) == \A k \in 1..Len(K) :
              K[k].isc => LET P == CfgOf(SubSeq(K, 1, k - 1))
                          IN Cardinality((P \ K[k].mem) \cup (K[k].mem \ P)) = 1

------------------------------------------------------------------------------
(* Requests. RV: a = last index, b = last epoch. AE: a = prevIndex, b = prevEpoch. *)
Msg(ty, s, d, e, a, b, ents, c) ==
  [ty |-> ty, src |-> s, dst |-> d, ep |-> e, a |-> a, b |-> b, ents |-> ents, ci |-> c]
LinkUp(s, d) == <<s, d>> \notin down
Sendable(S) == {m \in S : LinkUp(m.src, m.dst)}   \* sent over a down link: lost (G1.3)

RVof(i, r, j) == Msg("RV", i, j, r.ep, Len(r.jr), LastEp(r.jr), <<>>, 0)
Targets(r) == CfgOf(r.jr) \cup (IF r.ch.op = "add" /\ r.ch.ph = "catch" THEN {r.ch.t} ELSE {})
AEof(i, r, j) == LET p == r.ni[j] - 1
                 IN Msg("AE", i, j, r.ep, p, IF p = 0 THEN 0 ELSE r.jr[p].ep, SubSeq(r.jr, p + 1, Len(r.jr)), r.ci)
\* A coordinator's current extend request to every target (sent whenever its state changes).
Bcast(i, r) == IF r.up /\ r.role = "C" THEN {AEof(i, r, j) : j \in Targets(r) \ {i}} ELSE {}

\* A request is dead when delivering it (with or without its reply) can change nothing now,
\* and anything it could change later is also produced by the sender's retry.
\*  - stale (epoch below the receiver's) and the receiver's epoch is not above the sender's;
\*  - RV of the receiver's epoch whose sender is no longer candidate of that epoch (a vote for
\*    it can only make the receiver refuse others later, which not delivering another
\*    candidate's request reproduces), or whose receiver has voted for another member, or
\*    whose vote the sender has already counted;
\*  - AE of the receiver's epoch whose entries and commit index the receiver already holds,
\*    and whose success reply could not raise the coordinator's matchIndex or nextIndex.
Dead(m, S) ==
  LET j == S[m.dst]  c == S[m.src]
      stale == m.ep < j.ep /\ c.ep >= j.ep
      last == m.a + Len(m.ents)
  IN \/ stale
     \/ /\ m.ty = "RV" /\ m.ep = j.ep
        /\ \/ ~(c.ep = m.ep /\ c.role = "L")          \* sender no longer candidate of m.ep (see README)
           \/ (j.vf # None /\ (j.vf # m.src \/ m.dst \in c.votes))
     \/ /\ m.ty = "AE" /\ m.ep = j.ep /\ j.up
        /\ (m.a = 0 \/ (m.a <= Len(j.jr) /\ j.jr[m.a].ep = m.b))
        /\ last <= Len(j.jr)
        /\ \A k \in 1..Len(m.ents) : j.jr[m.a + k] = m.ents[k]
        /\ j.ci >= Min({m.ci, last})
        /\ (~(c.ep = m.ep /\ c.role = "C") \/ (c.mi[m.dst] >= last /\ c.ni[m.dst] >= last + 1))
SetMsgs(S) == msgs' = {m \in S : ~Dead(m, st')}

------------------------------------------------------------------------------
(* Member-record transformers *)
BumpR(r, e) ==
  IF e > r.ep
  THEN [r EXCEPT !.ep = e, !.vf = None, !.role = "F", !.votes = {}, !.ni = Zero, !.mi = Zero, !.ch = NoCh]
  ELSE r

\* Commitment rule, then completion of a pending configuration change.
CommitR(i, r) ==
  LET C == CfgOf(r.jr)
      ok(n) == r.jr[n].ep = r.ep /\ Maj({i} \cup {j \in M \ {i} : r.mi[j] >= n}, C)
      Ns == {n \in (r.ci + 1)..Len(r.jr) : ok(n)}
      n == IF Ns = {} THEN r.ci ELSE Max(Ns)
      r2 == [r EXCEPT !.ci = n]
  IN IF r.ch.ph = "commit" /\ n >= r.ch.idx
     THEN IF r.ch.op = "remove" /\ r.ch.t = i
          THEN [r2 EXCEPT !.ch = NoCh, !.role = "F", !.ni = Zero, !.mi = Zero]  \* removed itself: steps down
          ELSE [r2 EXCEPT !.ch = NoCh]
     ELSE r2

BecomeCoordR(i, r) ==
  CommitR(i, [r EXCEPT !.role = "C", !.votes = {}, !.ni = [j \in M |-> Len(r.jr) + 1], !.mi = Zero,
                       !.ch = NoCh,
                       !.jr = IF Gated THEN Append(r.jr, CmdE(r.ep, "noop")) ELSE r.jr])

\* Receiver's journal after accepting an extend request that matched at p.
Merge(J, p, E) ==
  LET conf == {k \in 1..Len(E) : p + k <= Len(J) /\ J[p + k].ep # E[k].ep}
  IN IF conf # {}
     THEN LET k == Min(conf) IN SubSeq(J, 1, p + k - 1) \o SubSeq(E, k, Len(E))
     ELSE IF p + Len(E) > Len(J) THEN J \o SubSeq(E, Len(J) - p + 1, Len(E)) ELSE J

\* Receiver side: new record and reply ([ep, ok, a]; ep = -1 means no reply).
RecvRV(m) ==
  LET r == BumpR(st[m.dst], m.ep)
      grant == m.ep = r.ep /\ r.vf \in {None, m.src} /\ UpToDate(m.a, m.b, r.jr)
  IN [r |-> IF grant THEN [r EXCEPT !.vf = m.src] ELSE r, rep |-> [ep |-> r.ep, ok |-> grant, a |-> 0]]

RecvAE(m) ==
  LET r == BumpR(st[m.dst], m.ep)
      r1 == [r EXCEPT !.role = "F", !.votes = {}]
      ok == m.a = 0 \/ (m.a <= Len(r1.jr) /\ r1.jr[m.a].ep = m.b)
      last == m.a + Len(m.ents)
  IN IF m.ep < r.ep THEN [r |-> r, rep |-> [ep |-> r.ep, ok |-> FALSE, a |-> 0]]
     ELSE IF r.role = "C" THEN [r |-> r, rep |-> [ep |-> -1, ok |-> FALSE, a |-> 0]]  \* only after a J1.1 violation
     ELSE IF ~ok THEN [r |-> r1, rep |-> [ep |-> r1.ep, ok |-> FALSE, a |-> 0]]
     ELSE [r |-> [r1 EXCEPT !.jr = Merge(r1.jr, m.a, m.ents),
                            !.ci = IF m.ci > r1.ci THEN Max({r1.ci, Min({m.ci, last})}) ELSE r1.ci],
           rep |-> [ep |-> r1.ep, ok |-> TRUE, a |-> last]]

\* Sender side: processing the reply to its request m (only if m is of its current epoch).
OnReply(m, rep) ==
  LET s == m.src  j == m.dst  r == BumpR(st[s], rep.ep)
  IN IF m.ep # r.ep \/ rep.ep # r.ep THEN r
     ELSE IF m.ty = "RV"
     THEN IF r.role = "L" /\ rep.ok
          THEN LET r2 == [r EXCEPT !.votes = r.votes \cup {j}]
               IN IF Maj(r2.votes, CfgOf(r.jr)) THEN BecomeCoordR(s, r2) ELSE r2
          ELSE r
     ELSE IF r.role = "C"
          THEN IF rep.ok
               THEN CommitR(s, [r EXCEPT !.mi[j] = Max({@, rep.a}), !.ni[j] = Max({@, rep.a + 1})])
               ELSE [r EXCEPT !.ni[j] = Max({1, @ - 1})]
          ELSE r

------------------------------------------------------------------------------
(* Observable events of one member's change, derived from its record before and after. *)
AppEv(i, k, x) == [event |-> "Appended", member |-> i, index |-> k, epoch |-> x.ep,
                   kind |-> IF x.isc THEN "config" ELSE "command",
                   payload |-> IF x.isc THEN x.mem ELSE {x.cmd}]
DiffEv(i) ==
  LET a == st[i]  b == st'[i]  J == a.jr  K == b.jr  cp == CP(J, K)
      el == IF a.role # "C" /\ b.role = "C"
            THEN <<[event |-> "Elected", member |-> i, epoch |-> b.ep, config |-> CfgOf(J)]>> ELSE <<>>
      tr == IF cp < Len(J) THEN <<[event |-> "Truncated", member |-> i, from_index |-> cp + 1]>> ELSE <<>>
      ap == [x \in 1..(Len(K) - cp) |-> AppEv(i, cp + x, K[cp + x])]
      cf == IF CfgIdx(J) # CfgIdx(K) \/ (CfgIdx(K) > 0 /\ CfgIdx(K) > cp)
            THEN <<[event |-> "ConfigInEffect", member |-> i, config |-> CfgOf(K), index |-> CfgIdx(K)]>>
            ELSE <<>>
      cm == IF b.ci > a.ci
            THEN [x \in 1..(b.ci - a.ci) |-> [event |-> "Committed", member |-> i, index |-> a.ci + x,
                                              epoch |-> K[a.ci + x].ep]]
            ELSE <<>>
      rp == IF a.ch.ph = "commit" /\ b.ch.op = "none" /\ b.up /\ b.ci >= a.ch.idx
            THEN <<[event |-> "ChangeReplied", member |-> i, op |-> a.ch.op, target |-> a.ch.t, status |-> "ok"]>>
            ELSE <<>>
  IN el \o tr \o ap \o cf \o cm \o rp

------------------------------------------------------------------------------
(* Scenario driver *)
Match(trig, ev) == trig.event = ev.event /\
                   \A f \in DOMAIN trig \ {"event"} : f \in DOMAIN ev /\ ev[f] = trig[f]

Resolve(do, le, lc) ==
  LET names == {do.t, do.at} \cup UNION {{l[1], l[2]} : l \in do.links}
      Fs == IF "follower" \in names THEN {f \in M : st'[f].up /\ f # le} ELSE {None}
      R(x, f) == IF x = "coordinator" THEN le ELSE IF x = "crashed" THEN lc ELSE IF x = "follower" THEN f ELSE x
  IN IF "coordinator" \in names /\ le = None THEN Assert(FALSE, "scenario rejected: coordinator before any Elected")
     ELSE IF "crashed" \in names /\ lc = None THEN Assert(FALSE, "scenario rejected: crashed before any crash")
     ELSE {[op |-> do.op, t |-> R(do.t, f), at |-> R(do.at, f), cmd |-> do.cmd,
            links |-> {<<R(l[1], f), R(l[2], f)>> : l \in do.links} \ {<<x, x>> : x \in M}] : f \in Fs}

ScenUpd(evs, isEnv) ==
  LET armed == IF isEnv THEN stp + 1 ELSE stp
      can == armed <= NS /\ (isEnv \/ pend = NoAct)
      ks == IF can THEN {k \in 1..Len(evs) : Match(Steps[armed].at, evs[k])} ELSE {}
      LE(k) == LET es == {x \in 1..k : evs[x].event = "Elected"}
               IN IF es = {} THEN lastE ELSE evs[Max(es)].member
      lc == IF isEnv /\ pend.op = "crash" THEN pend.t ELSE lastC
  IN /\ stp' = armed
     /\ lastE' = LE(Len(evs))
     /\ lastC' = lc
     /\ IF ks # {}
        THEN LET R == Resolve(Steps[armed].act, LE(Min(ks)), lc)
             IN IF R = {} THEN pend' = NoAct ELSE \E x \in R : pend' = x
        ELSE pend' = IF isEnv THEN NoAct ELSE pend
     /\ settle' = IF armed > NS THEN (IF isEnv THEN 0 ELSE settle + Len(evs)) ELSE 0
     /\ settle' <= Settle

\* Ghost bookkeeping for the checkers, then the scenario driver. L: members changed (1 or 2).
Post(L, isEnv, xev) ==
  LET X == {L[k] : k \in 1..Len(L)}
      CommNew(i) == IF st'[i].ci > st[i].ci /\ (st'[i].role = "C" \/ (st[i].role = "C" /\ st[i].ep = st'[i].ep))
                    THEN {[idx |-> k, ent |-> st'[i].jr[k], e |-> st'[i].ep] : k \in 1..st'[i].ci} ELSE {}
      comm2 == comm \cup {c \in UNION {CommNew(i) : i \in X} :
                            ~\E d \in comm : d.idx = c.idx /\ d.ent = c.ent /\ d.e <= c.e}
      Removed(i) == LET J == st[i].jr IN {[idx |-> k, ent |-> J[k]] : k \in (CP(J, st'[i].jr) + 1)..Len(J)}
  IN /\ \A i \in X : Len(st'[i].jr) <= MaxJ
     /\ elec' = elec \cup {[e |-> st'[i].ep, m |-> i, j |-> st[i].jr] : i \in {x \in X : st[x].role # "C" /\ st'[x].role = "C"}}
     /\ comm' = comm2
     /\ bad13' = (bad13 \/ \E i \in X : ~J13ok(st'[i].jr))
     /\ bad14b' = (bad14b \/ \E i \in X : \E rm \in Removed(i) : \E c \in comm2 : c.idx = rm.idx /\ c.ent = rm.ent)
     /\ ScenUpd(xev \o DiffEv(L[1]) \o (IF Len(L) > 1 THEN DiffEv(L[2]) ELSE <<>>), isEnv)

------------------------------------------------------------------------------
(* System transitions *)

\* A follower or candidate times out (any time) and asks every other member of its configuration.
Timeout(i) ==
  LET r == st[i]  e == r.ep + 1  C == CfgOf(r.jr)
      r1 == [r EXCEPT !.ep = e, !.vf = i, !.role = "L", !.votes = {i}, !.ni = Zero, !.mi = Zero, !.ch = NoCh]
      r2 == IF Maj({i}, C) THEN BecomeCoordR(i, r1) ELSE r1
  IN /\ r.up /\ r.role # "C" /\ e <= MaxE /\ tmo < MaxT
     /\ st' = [st EXCEPT ![i] = r2]
     /\ SetMsgs(msgs \cup Sendable({RVof(i, r1, j) : j \in C \ {i}} \cup Bcast(i, r2)))
     /\ tmo' = tmo + 1
     /\ UNCHANGED down
     /\ Post(<<i>>, FALSE, <<>>)

\* Retries: a candidate re-sends its ballot request, a coordinator its extend request,
\* when the current one is not in flight.
ResendRV(i, j) ==
  LET r == st[i]  m == RVof(i, r, j)
  IN /\ r.up /\ r.role = "L" /\ j \in CfgOf(r.jr) \ {i} /\ LinkUp(i, j) /\ m \notin msgs /\ ~Dead(m, st)
     /\ msgs' = msgs \cup {m}
     /\ UNCHANGED <<st, down, elec, comm, bad13, bad14b, tmo, stp, pend, lastE, lastC, settle>>

SendAE(i, j) ==
  LET r == st[i]  m == AEof(i, r, j)
  IN /\ r.up /\ r.role = "C" /\ j \in Targets(r) \ {i} /\ LinkUp(i, j) /\ m \notin msgs /\ ~Dead(m, st)
     /\ msgs' = msgs \cup {m}
     /\ UNCHANGED <<st, down, elec, comm, bad13, bad14b, tmo, stp, pend, lastE, lastC, settle>>

\* Delivery of request m; wr: its reply is delivered too (atomically), else the reply is lost.
Deliver(m, wr) ==
  LET R == IF m.ty = "RV" THEN RecvRV(m) ELSE RecvAE(m)
      s == m.src
      rs == IF wr THEN OnReply(m, R.rep) ELSE st[s]
  IN /\ st[m.dst].up /\ LinkUp(m.src, m.dst)
     /\ wr => (R.rep.ep >= 0 /\ st[s].up /\ LinkUp(m.dst, s))
     /\ st' = [st EXCEPT ![m.dst] = R.r, ![s] = rs]
     /\ SetMsgs(msgs \cup Sendable(Bcast(s, rs)))
     /\ UNCHANGED <<down, tmo>>
     /\ Post(<<m.dst, s>>, FALSE, <<>>)

\* Configuration change progress at the coordinator.
Proceed(i) ==
  LET r == st[i]  t == r.ch.t  C == CfgOf(r.jr)
      newC == IF r.ch.op = "add" THEN C \cup {t} ELSE C \ {t}
      r2 == CommitR(i, [r EXCEPT !.jr = Append(r.jr, CfgE(r.ep, newC)), !.ch.ph = "commit", !.ch.idx = Len(r.jr) + 1])
  IN /\ r.up /\ r.role = "C"
     /\ \/ /\ r.ch.ph = "catch" /\ r.mi[t] >= Len(r.jr)       \* add step 2: new member holds every entry
           /\ st' = [st EXCEPT ![i].ch.ph = "wait"]
           /\ UNCHANGED msgs
        \/ /\ r.ch.ph = "wait" /\ CfgIdx(r.jr) <= r.ci        \* previous configuration entry committed
           /\ Gated => \E k \in 1..r.ci : r.jr[k].ep = r.ep   \* GATED only
           /\ st' = [st EXCEPT ![i] = r2]
           /\ SetMsgs(msgs \cup Sendable(Bcast(i, r2)))
     /\ UNCHANGED <<down, tmo>>
     /\ Post(<<i>>, FALSE, <<>>)

\* Catch-up gives up (timer): reply "timeout".
CatchTimeout(i) ==
  LET r == st[i]
  IN /\ r.up /\ r.role = "C" /\ r.ch.ph = "catch"
     /\ st' = [st EXCEPT ![i].ch = NoCh]
     /\ SetMsgs(msgs)
     /\ UNCHANGED <<down, tmo>>
     /\ Post(<<i>>, FALSE, <<[event |-> "ChangeReplied", member |-> i, op |-> r.ch.op, target |-> r.ch.t,
                             status |-> "timeout"]>>)

------------------------------------------------------------------------------
(* Environment: the scenario's pending action *)
AdminReq(p) ==
  LET a == p.at  r == st[a]  C == CfgOf(r.jr)
      rq == [event |-> "ChangeRequested", member |-> a, op |-> p.op, target |-> p.t]
      Rep(s) == [event |-> "ChangeReplied", member |-> a, op |-> p.op, target |-> p.t, status |-> s]
  IN IF ~r.up THEN /\ UNCHANGED <<st, msgs, down, tmo>> /\ Post(<<a>>, TRUE, <<>>)   \* request lost
     ELSE IF r.role # "C" THEN /\ UNCHANGED <<st, msgs, down, tmo>> /\ Post(<<a>>, TRUE, <<rq, Rep("not coordinator")>>)
     ELSE IF r.ch.op # "none" THEN /\ UNCHANGED <<st, msgs, down, tmo>> /\ Post(<<a>>, TRUE, <<rq, Rep("busy")>>)
     ELSE IF (p.op = "add") = (p.t \in C) THEN /\ UNCHANGED <<st, msgs, down, tmo>> /\ Post(<<a>>, TRUE, <<rq, Rep("invalid")>>)
     ELSE LET r2 == [r EXCEPT !.ch = [op |-> p.op, t |-> p.t, idx |-> 0,
                                      ph |-> IF p.op = "add" /\ st[p.t].jr # r.jr THEN "catch" ELSE "wait"]]
          IN /\ st' = [st EXCEPT ![a] = r2]
             /\ SetMsgs(msgs \cup Sendable(Bcast(a, r2)))
             /\ UNCHANGED <<down, tmo>>
             /\ Post(<<a>>, TRUE, <<rq>>)

EnvStep ==
  LET p == pend IN
  /\ p # NoAct
  /\ CASE p.op \in {"add", "remove"} -> AdminReq(p)
       [] p.op = "command" ->
            LET r == st[p.at]
                r2 == CommitR(p.at, [r EXCEPT !.jr = Append(r.jr, CmdE(r.ep, p.cmd))])
            IN IF r.up /\ r.role = "C"
               THEN /\ st' = [st EXCEPT ![p.at] = r2]
                    /\ SetMsgs(msgs \cup Sendable(Bcast(p.at, r2)))
                    /\ UNCHANGED <<down, tmo>>
                    /\ Post(<<p.at>>, TRUE, <<>>)
               ELSE /\ UNCHANGED <<st, msgs, down, tmo>> /\ Post(<<p.at>>, TRUE, <<>>)   \* ignored
       [] p.op = "crash" ->
            /\ st' = [st EXCEPT ![p.t] = [@ EXCEPT !.up = FALSE, !.role = "F", !.ci = 0, !.votes = {},
                                                   !.ni = Zero, !.mi = Zero, !.ch = NoCh]]
            /\ SetMsgs(msgs)
            /\ UNCHANGED <<down, tmo>>
            /\ Post(<<p.t>>, TRUE, <<>>)
       [] p.op = "restart" ->
            /\ st' = [st EXCEPT ![p.t].up = TRUE]
            /\ SetMsgs(msgs)
            /\ UNCHANGED <<down, tmo>>
            /\ Post(<<p.t>>, TRUE, <<>>)
       [] p.op = "cut" ->
            /\ down' = down \cup p.links \cup {<<l[2], l[1]>> : l \in p.links}
            /\ UNCHANGED <<st, msgs, tmo>>
            /\ Post(<<"m1">>, TRUE, <<>>)
       [] p.op = "drop" ->
            /\ down' = down \cup p.links
            /\ UNCHANGED <<st, msgs, tmo>>
            /\ Post(<<"m1">>, TRUE, <<>>)
       [] p.op = "heal" ->
            /\ down' = {}
            /\ UNCHANGED <<st, msgs, tmo>>
            /\ Post(<<"m1">>, TRUE, <<>>)

------------------------------------------------------------------------------
Init ==
  /\ st = [i \in M |-> [up |-> TRUE, ep |-> 0, vf |-> None, jr |-> <<>>, role |-> "F", ci |-> 0,
                        votes |-> {}, ni |-> Zero, mi |-> Zero, ch |-> NoCh]]
  /\ msgs = {} /\ down = {} /\ elec = {} /\ comm = {} /\ bad13 = FALSE /\ bad14b = FALSE /\ tmo = 0
  /\ stp = 1 /\ lastE = None /\ lastC = None /\ settle = 0
  /\ pend = IF NS >= 1 /\ Steps[1].at.event = "start"
            THEN [op |-> Steps[1].act.op, t |-> Steps[1].act.t, at |-> Steps[1].act.at,
                  cmd |-> Steps[1].act.cmd, links |-> Steps[1].act.links]
            ELSE NoAct

Next ==
  \/ \E i \in M : Timeout(i) \/ Proceed(i) \/ CatchTimeout(i)
  \/ \E i, j \in M : SendAE(i, j) \/ ResendRV(i, j)
  \/ \E m \in msgs, wr \in BOOLEAN : Deliver(m, wr)
  \/ EnvStep

Spec == Init /\ [][Next]_vars

------------------------------------------------------------------------------
(* Checkers (contract v2) *)
Done == stp > NS
OkJ11 == ~\E r1, r2 \in elec : r1.e = r2.e /\ r1.m # r2.m
OkJ14a == ~\E r \in elec, c \in comm : c.e < r.e /\ ~(Len(r.j) >= c.idx /\ r.j[c.idx] = c.ent)
OkJ14b == ~bad14b
OkJ13 == ~bad13

\* A violation in a behaviour that takes every step (the format's FAIL; the behaviour's
\* violating prefix is a prefix of a behaviour that takes every step).
InvJ11 == Done => OkJ11
InvJ13 == Done => OkJ13
InvJ14a == Done => OkJ14a
InvJ14b == Done => OkJ14b
\* Any violation, whether or not the behaviour goes on to take every step (diagnostic).
AnyJ11 == OkJ11
AnyJ13 == OkJ13
AnyJ14a == OkJ14a
AnyJ14b == OkJ14b
\* Reachability probe: violated exactly when some behaviour takes every step.
NotDone == ~Done
=============================================================================
