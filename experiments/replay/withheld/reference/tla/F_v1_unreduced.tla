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
(*     own epoch.                                                          *)
(*                                                                         *)
(* Messages: a set of every message sent and not yet garbage (G1.2).       *)
(* Delivery leaves the message in the set, so any message can be           *)
(* delivered any number of times (duplication), at any later point         *)
(* (delay, reordering), or never (loss). Replies that can never again      *)
(* have an effect are removed (see Dead).                                  *)
(***************************************************************************)
EXTENDS Naturals, Sequences, FiniteSets, TLC

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
          msgs,    \* set of messages in the network
          down,    \* set of directed links <<a, b>> that are down
          elec,    \* ghost: set of [e, m, j] coordinator elections (journal at election)
          comm,    \* ghost: set of [idx, ent, e] commitments by a coordinator in epoch e
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
\* length of the common prefix of two journals
CP(J, K) == Max({k \in 0..Min({Len(J), Len(K)}) : \A x \in 1..k : J[x] = K[x]})

\* J1.3: each configuration entry differs from its predecessor in the same journal
\* (or the initial configuration) by exactly one member.
J13ok(K) == \A k \in 1..Len(K) :
              K[k].isc => LET P == CfgOf(SubSeq(K, 1, k - 1))
                          IN Cardinality((P \ K[k].mem) \cup (K[k].mem \ P)) = 1

------------------------------------------------------------------------------
(* Messages: one record shape for all kinds.
   RV : a = last index, b = last epoch.        RVR: ok = granted.
   AE : a = prevIndex, b = prevEpoch, ents, ci. AER: ok = success, a = match. *)
Msg(ty, s, d, e, a, b, ents, c, ok) ==
  [ty |-> ty, src |-> s, dst |-> d, ep |-> e, a |-> a, b |-> b, ents |-> ents, ci |-> c, ok |-> ok]
LinkUp(s, d) == <<s, d>> \notin down
Sendable(S) == {m \in S : LinkUp(m.src, m.dst)}   \* sent over a down link: lost (G1.3)

\* A reply that can never again change anything. A ballot reply for epoch e matters only
\* to a candidate of epoch e (or as a higher epoch); an extend reply only to the coordinator
\* of epoch e (or as a higher epoch). A member is candidate/coordinator of an epoch at most
\* once, so once it has left that role in that epoch, or passed the epoch, the reply is dead.
Dead(m, S) ==
  \/ m.ty = "RVR" /\ (S[m.dst].ep > m.ep \/ (S[m.dst].ep = m.ep /\ S[m.dst].role # "L"))
  \/ m.ty = "AER" /\ (S[m.dst].ep > m.ep \/ (S[m.dst].ep = m.ep /\ S[m.dst].role # "C"))
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
  LET usesF == "follower" \in {do.t, do.at} \cup UNION {{l[1], l[2]} : l \in do.links}
      usesE == "coordinator" \in {do.t, do.at} \cup UNION {{l[1], l[2]} : l \in do.links}
      usesC == "crashed" \in {do.t, do.at} \cup UNION {{l[1], l[2]} : l \in do.links}
      Fs == IF usesF THEN {f \in M : st'[f].up /\ f # le} ELSE {None}
      R(x, f) == IF x = "coordinator" THEN le ELSE IF x = "crashed" THEN lc ELSE IF x = "follower" THEN f ELSE x
  IN IF usesE /\ le = None THEN Assert(FALSE, "scenario rejected: coordinator before any Elected")
     ELSE IF usesC /\ lc = None THEN Assert(FALSE, "scenario rejected: crashed before any crash")
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

\* Ghost bookkeeping for the checkers, then the scenario driver.
Post(i, isEnv, xev) ==
  LET a == st[i]  b == st'[i]  J == a.jr  K == b.jr  cp == CP(J, K)
      coordCommit == b.ci > a.ci /\ (b.role = "C" \/ (a.role = "C" /\ a.ep = b.ep))
      newC == IF coordCommit THEN {[idx |-> k, ent |-> K[k], e |-> b.ep] : k \in 1..b.ci} ELSE {}
      comm2 == comm \cup {c \in newC : ~\E d \in comm : d.idx = c.idx /\ d.ent = c.ent /\ d.e <= c.e}
  IN /\ elec' = IF a.role # "C" /\ b.role = "C" THEN elec \cup {[e |-> b.ep, m |-> i, j |-> J]} ELSE elec
     /\ comm' = comm2
     /\ bad13' = (bad13 \/ ~J13ok(K))
     /\ bad14b' = (bad14b \/ \E k \in (cp + 1)..Len(J) : \E c \in comm2 : c.idx = k /\ c.ent = J[k])
     /\ ScenUpd(xev \o DiffEv(i), isEnv)

------------------------------------------------------------------------------
(* System transitions *)
Upd(i, r2, out) ==
  /\ st' = [st EXCEPT ![i] = r2]
  /\ SetMsgs(msgs \cup Sendable(out))
  /\ UNCHANGED <<down, tmo>>
  /\ Post(i, FALSE, <<>>)

\* A follower or candidate times out (any time).
Timeout(i) ==
  LET r == st[i]  e == r.ep + 1  C == CfgOf(r.jr)
      r1 == [r EXCEPT !.ep = e, !.vf = i, !.role = "L", !.votes = {i}, !.ni = Zero, !.mi = Zero, !.ch = NoCh]
      win == Maj({i}, C)
      rv == {Msg("RV", i, j, e, Len(r.jr), LastEp(r.jr), <<>>, 0, FALSE) : j \in C \ {i}}
  IN /\ r.up /\ r.role # "C" /\ e <= MaxE /\ tmo < MaxT
     /\ (win /\ Gated) => Len(r.jr) < MaxJ
     /\ st' = [st EXCEPT ![i] = IF win THEN BecomeCoordR(i, r1) ELSE r1]
     /\ SetMsgs(msgs \cup Sendable(rv))
     /\ tmo' = tmo + 1
     /\ UNCHANGED down
     /\ Post(i, FALSE, <<>>)

\* A candidate retries a ballot request (needed after a loss on a down link).
ResendRV(i, j) ==
  LET r == st[i]  m == Msg("RV", i, j, r.ep, Len(r.jr), LastEp(r.jr), <<>>, 0, FALSE)
  IN /\ r.up /\ r.role = "L" /\ j \in CfgOf(r.jr) \ {i} /\ LinkUp(i, j) /\ m \notin msgs
     /\ msgs' = msgs \cup {m}
     /\ UNCHANGED <<st, down, elec, comm, bad13, bad14b, tmo, stp, pend, lastE, lastC, settle>>

\* A coordinator sends (or retries) an extend request: entries from nextIndex to its last.
SendAE(i, j) ==
  LET r == st[i]
      T == CfgOf(r.jr) \cup (IF r.ch.op = "add" /\ r.ch.ph = "catch" THEN {r.ch.t} ELSE {})
      p == r.ni[j] - 1
      m == Msg("AE", i, j, r.ep, p, IF p = 0 THEN 0 ELSE r.jr[p].ep, SubSeq(r.jr, p + 1, Len(r.jr)), r.ci, FALSE)
  IN /\ r.up /\ r.role = "C" /\ j \in T \ {i} /\ LinkUp(i, j) /\ m \notin msgs
     /\ msgs' = msgs \cup {m}
     /\ UNCHANGED <<st, down, elec, comm, bad13, bad14b, tmo, stp, pend, lastE, lastC, settle>>

Deliver(m) ==
  LET i == m.dst  r == BumpR(st[i], m.ep)
      fail == Msg("AER", i, m.src, r.ep, 0, 0, <<>>, 0, FALSE)
  IN /\ st[i].up /\ LinkUp(m.src, m.dst)
     /\ CASE m.ty = "RV" ->
               LET grant == m.ep = r.ep /\ r.vf \in {None, m.src} /\ UpToDate(m.a, m.b, r.jr)
                   r2 == IF grant THEN [r EXCEPT !.vf = m.src] ELSE r
               IN Upd(i, r2, {Msg("RVR", i, m.src, r2.ep, 0, 0, <<>>, 0, grant)})
          [] m.ty = "RVR" ->
               IF r.role = "L" /\ m.ep = r.ep /\ m.ok
               THEN LET r2 == [r EXCEPT !.votes = r.votes \cup {m.src}]
                    IN IF Maj(r2.votes, CfgOf(r.jr))
                       THEN /\ Gated => Len(r.jr) < MaxJ
                            /\ Upd(i, BecomeCoordR(i, r2), {})
                       ELSE Upd(i, r2, {})
               ELSE Upd(i, r, {})
          [] m.ty = "AE" ->
               IF m.ep < r.ep THEN Upd(i, r, {fail})
               ELSE IF r.role = "C" THEN Upd(i, r, {})   \* same-epoch coordinator (only after a J1.1 violation)
               ELSE LET r1 == [r EXCEPT !.role = "F", !.votes = {}]
                        ok == m.a = 0 \/ (m.a <= Len(r1.jr) /\ r1.jr[m.a].ep = m.b)
                        last == m.a + Len(m.ents)
                    IN IF ~ok THEN Upd(i, r1, {fail})
                       ELSE Upd(i, [r1 EXCEPT !.jr = Merge(r1.jr, m.a, m.ents),
                                              !.ci = IF m.ci > r1.ci THEN Max({r1.ci, Min({m.ci, last})}) ELSE r1.ci],
                                {Msg("AER", i, m.src, r1.ep, last, 0, <<>>, 0, TRUE)})
          [] m.ty = "AER" ->
               IF r.role = "C" /\ m.ep = r.ep
               THEN IF m.ok
                    THEN Upd(i, CommitR(i, [r EXCEPT !.mi[m.src] = m.a, !.ni[m.src] = m.a + 1]), {})
                    ELSE Upd(i, [r EXCEPT !.ni[m.src] = Max({1, r.ni[m.src] - 1})], {})
               ELSE Upd(i, r, {})

\* Configuration change progress at the coordinator (catch-up done; previous entry committed).
Proceed(i) ==
  LET r == st[i]  t == r.ch.t  C == CfgOf(r.jr)
      newC == IF r.ch.op = "add" THEN C \cup {t} ELSE C \ {t}
  IN /\ r.up /\ r.role = "C"
     /\ \/ /\ r.ch.ph = "catch" /\ r.mi[t] >= Len(r.jr)       \* new member holds every entry
           /\ Upd(i, [r EXCEPT !.ch.ph = "wait"], {})
        \/ /\ r.ch.ph = "wait" /\ CfgIdx(r.jr) <= r.ci        \* previous configuration entry committed
           /\ Gated => \E k \in 1..r.ci : r.jr[k].ep = r.ep   \* GATED only
           /\ Len(r.jr) < MaxJ
           /\ Upd(i, CommitR(i, [r EXCEPT !.jr = Append(r.jr, CfgE(r.ep, newC)),
                                          !.ch.ph = "commit", !.ch.idx = Len(r.jr) + 1]), {})

\* Catch-up gives up (timer): reply "timeout".
CatchTimeout(i) ==
  LET r == st[i]
  IN /\ r.up /\ r.role = "C" /\ r.ch.ph = "catch"
     /\ st' = [st EXCEPT ![i].ch = NoCh]
     /\ UNCHANGED <<msgs, down, tmo>>
     /\ Post(i, FALSE, <<[event |-> "ChangeReplied", member |-> i, op |-> r.ch.op, target |-> r.ch.t,
                          status |-> "timeout"]>>)

------------------------------------------------------------------------------
(* Environment: the scenario's pending action *)
AdminReq(p) ==
  LET a == p.at  r == st[a]  C == CfgOf(r.jr)
      rq == [event |-> "ChangeRequested", member |-> a, op |-> p.op, target |-> p.t]
      Rep(s) == [event |-> "ChangeReplied", member |-> a, op |-> p.op, target |-> p.t, status |-> s]
  IN IF ~r.up THEN /\ UNCHANGED <<st, msgs, down, tmo>> /\ Post(a, TRUE, <<>>)
     ELSE IF r.role # "C" THEN /\ UNCHANGED <<st, msgs, down, tmo>> /\ Post(a, TRUE, <<rq, Rep("not coordinator")>>)
     ELSE IF r.ch.op # "none" THEN /\ UNCHANGED <<st, msgs, down, tmo>> /\ Post(a, TRUE, <<rq, Rep("busy")>>)
     ELSE IF (p.op = "add") = (p.t \in C) THEN /\ UNCHANGED <<st, msgs, down, tmo>> /\ Post(a, TRUE, <<rq, Rep("invalid")>>)
     ELSE /\ st' = [st EXCEPT ![a].ch = [op |-> p.op, t |-> p.t, idx |-> 0,
                                         ph |-> IF p.op = "add" /\ st[p.t].jr # r.jr THEN "catch" ELSE "wait"]]
          /\ UNCHANGED <<msgs, down, tmo>>
          /\ Post(a, TRUE, <<rq>>)

EnvStep ==
  LET p == pend IN
  /\ p # NoAct
  /\ CASE p.op \in {"add", "remove"} -> AdminReq(p)
       [] p.op = "command" ->
            LET r == st[p.at] IN
            IF r.up /\ r.role = "C"
            THEN /\ Len(r.jr) < MaxJ
                 /\ st' = [st EXCEPT ![p.at] = CommitR(p.at, [r EXCEPT !.jr = Append(r.jr, CmdE(r.ep, p.cmd))])]
                 /\ UNCHANGED <<msgs, down, tmo>>
                 /\ Post(p.at, TRUE, <<>>)
            ELSE /\ UNCHANGED <<st, msgs, down, tmo>> /\ Post(p.at, TRUE, <<>>)   \* ignored
       [] p.op = "crash" ->
            /\ st' = [st EXCEPT ![p.t] = [@ EXCEPT !.up = FALSE, !.role = "F", !.ci = 0, !.votes = {},
                                                   !.ni = Zero, !.mi = Zero, !.ch = NoCh]]
            /\ SetMsgs(msgs)
            /\ UNCHANGED <<down, tmo>>
            /\ Post(p.t, TRUE, <<>>)
       [] p.op = "restart" ->
            /\ st' = [st EXCEPT ![p.t].up = TRUE]
            /\ UNCHANGED <<msgs, down, tmo>>
            /\ Post(p.t, TRUE, <<>>)
       [] p.op = "cut" ->
            /\ down' = down \cup p.links \cup {<<l[2], l[1]>> : l \in p.links}
            /\ UNCHANGED <<st, msgs, tmo>>
            /\ Post("m1", TRUE, <<>>)
       [] p.op = "drop" ->
            /\ down' = down \cup p.links
            /\ UNCHANGED <<st, msgs, tmo>>
            /\ Post("m1", TRUE, <<>>)
       [] p.op = "heal" ->
            /\ down' = {}
            /\ UNCHANGED <<st, msgs, tmo>>
            /\ Post("m1", TRUE, <<>>)

------------------------------------------------------------------------------
Init ==
  /\ st = [i \in M |-> [up |-> TRUE, ep |-> 0, vf |-> None, jr |-> <<>>, role |-> "F", ci |-> 0,
                        votes |-> {}, ni |-> Zero, mi |-> Zero, ch |-> NoCh]]
  /\ msgs = {} /\ down = {} /\ elec = {} /\ comm = {} /\ bad13 = FALSE /\ bad14b = FALSE /\ tmo = 0
  /\ stp = 1 /\ lastE = None /\ lastC = None /\ settle = 0
  /\ pend = IF NS >= 1 /\ Steps[1].at.event = "start"
            THEN CHOOSE x \in {[op |-> Steps[1].act.op, t |-> Steps[1].act.t, at |-> Steps[1].act.at,
                                cmd |-> Steps[1].act.cmd, links |-> Steps[1].act.links]} : TRUE
            ELSE NoAct

Next ==
  \/ \E i \in M : Timeout(i) \/ Proceed(i) \/ CatchTimeout(i)
  \/ \E i, j \in M : SendAE(i, j) \/ ResendRV(i, j)
  \/ \E m \in msgs : Deliver(m)
  \/ EnvStep

Spec == Init /\ [][Next]_vars

------------------------------------------------------------------------------
(* Checkers (contract v2) *)
Done == stp > NS
OkJ11 == ~\E r1, r2 \in elec : r1.e = r2.e /\ r1.m # r2.m
OkJ14a == ~\E r \in elec, c \in comm : c.e < r.e /\ ~(Len(r.j) >= c.idx /\ r.j[c.idx] = c.ent)
OkJ14b == ~bad14b
OkJ13 == ~bad13

\* A violation in a behaviour that takes every step (the format's FAIL).
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
