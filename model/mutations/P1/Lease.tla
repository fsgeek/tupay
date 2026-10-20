-------------------------------- MODULE Lease --------------------------------
\* mutation: P1 lease nodes do not durably record the highest token issued; it is lost on crash
\* derives: P1, C1.1, F1.1
\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
\* Lease service with fencing tokens: 3 lease nodes (the grantor), 2 clients,
\* one storage service, one key. The grantor is abstract: a leader per term,
\* elected by a majority; a grant is issued only with a majority's confirmation.
\* The environment (F1.1-F1.3) and the workload are driven by a compiled
\* schedule: Steps is a sequence of step records, applied in order.
EXTENDS Integers, Sequences, FiniteSets, TLC

CONSTANTS
    Nodes,      \* derives: C1.1, C1.4 -- the three lease nodes
    Clients,    \* derives: C1.2, C1.3, C1.4 -- the two clients
    Store,      \* derives: C1.2, C1.3 -- the storage service (one process)
    Key,        \* derives: C1.1, C1.2 -- the single protected key
    Lifetime,   \* derives: C1.1, F1.3 -- abstract grant lifetime, reported on Grant only
    Steps,      \* derives: F1.1, F1.2, F1.3 -- compiled schedule steps
    EndTrig,    \* derives: F1.1, F1.2, F1.3 -- compiled end trigger
    MaxTerm,    \* derives: C1.1, C1.4 -- bound on grantor terms (state-space bound)
    MaxDups     \* derives: C1.2, C1.3 -- bound on duplicated write deliveries

VARIABLES
    \* --- environment state (derives: F1.1, F1.2, F1.3)
    up,         \* derives: F1.1 -- up[p]: process p is running
    paused,     \* derives: F1.3 -- paused[c]: client c is paused
    sideA,      \* derives: F1.2 -- one side of the current bipartition (Procs when healed)
    \* --- grantor (derives: C1.1, C1.4)
    promised,   \* derives: C1.1, F1.1 -- durable: highest term node n has voted for
    maxTok,     \* derives: C1.1, F1.1 -- durable: highest token node n has confirmed
    leader,     \* derives: C1.1, C1.4 -- volatile: n believes it is the grantor
    term,       \* derives: C1.1 -- volatile: the term n leads (meaningful when leader[n])
    ltok,       \* derives: C1.1 -- volatile: leader's last issued token
    reqs,       \* derives: C1.4 -- grantor-visible outstanding requests
    \* --- clients (derives: C1.2, C1.3, C1.4, F1.3)
    pending,    \* derives: C1.4 -- pending[c]: c is waiting for (and retrying) a grant
    tok,        \* derives: C1.2, F1.3 -- c's current token [t, g] (g = grantor_term), volatile
    myToks,     \* derives: C1.2, F1.3 -- every token c has received since its last start
    awaiting,   \* derives: C1.3 -- writes c has sent and not yet had acked
    \* --- network (derives: F1.2; reorder by set semantics, duplication bounded by MaxDups)
    grantMsgs,  \* derives: C1.1, F1.2 -- grant replies in flight, node -> client
    writeMsgs,  \* derives: C1.2, F1.2 -- writes in flight, client -> storage
    ackMsgs,    \* derives: C1.3, F1.2 -- acks in flight, storage -> client
    dups,       \* derives: C1.2, C1.3 -- duplicated deliveries used so far
    \* --- storage (derives: C1.2, C1.3)
    highest,    \* derives: C1.2, F1.1 -- durable fence ledger
    stval,      \* derives: C1.2 -- durable key value
    toAck,      \* derives: C1.3, F1.1 -- volatile: decided writes whose ack is not yet sent
    \* --- history (ghost) variables used only by invariants and the exporter
    grants,     \* derives: C1.1 -- sequence of every grant issued
    decisions,  \* derives: C1.2, C1.3 -- sequence of every storage decision
    told,       \* derives: C1.3 -- set of writes clients were told succeeded
    \* --- schedule driver (derives: F1.1, F1.2, F1.3)
    pc,         \* derives: F1.1, F1.2, F1.3 -- index of the next schedule step
    fired,      \* derives: F1.1, F1.2, F1.3 -- trigger of step pc has held since step pc-1
    trigG,      \* derives: F1.2, F1.3 -- most recent grant at trigger time (resolves grantor/holder)
    lastEv      \* derives: C1.1, C1.2, C1.3 -- the event emitted by the last step (for the exporter)

\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -- all state variables
vars == <<up, paused, sideA, promised, maxTok, leader, term, ltok, reqs,
          pending, tok, myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups,
          highest, stval, toAck, grants, decisions, told, pc, fired, trigG, lastEv>>

\* derives: F1.1, F1.2 -- every process
Procs == Nodes \cup Clients \cup {Store}

\* derives: C1.2, F1.3 -- "no token"
NoTok == [t |-> 0, g |-> 0]

\* derives: C1.1, C1.2
Max(S) == IF S = {} THEN 0 ELSE CHOOSE x \in S : \A y \in S : y <= x

\* derives: F1.2 -- two processes are on the same side of the cut
Conn(p, q) == (p \in sideA) <=> (q \in sideA)

\* derives: C1.1, C1.4 -- majority of lease nodes
Majority(Q) == 2 * Cardinality(Q) > Cardinality(Nodes)

\* derives: C1.1, F1.2, F1.3 -- most recent Grant ("grantor" = its node, "holder" = its client)
LastGrant == IF grants = <<>> THEN [node |-> "none", client |-> "none"]
             ELSE [node |-> grants[Len(grants)].node, client |-> grants[Len(grants)].client]

\* derives: C1.1 -- highest token ever granted
MaxGranted == Max({grants[i].token : i \in 1..Len(grants)})

\* ---------------------------------------------------------------------------
\* Schedule triggers
\* derives: F1.1, F1.2, F1.3
Trig(i) == IF i <= Len(Steps) THEN Steps[i].trig ELSE EndTrig
\* derives: F1.1, F1.2, F1.3
IsStart(T) == T.event = "start"
\* derives: F1.1, F1.2, F1.3 -- an event matches a trigger: same event and every filter field equal
Matches(T, e) == /\ T.event # "start"
                 /\ e.event = T.event
                 /\ \A f \in (DOMAIN T) \ {"event"} : f \in DOMAIN e /\ e[f] = T[f]
\* derives: F1.1, F1.2, F1.3 -- the run has reached its end trigger (no more stimuli)
Done == pc = Len(Steps) + 1 /\ fired

\* derives: C1.1, C1.2, C1.3, F1.1, F1.2, F1.3
\* Protocol step emitting event e: record it, and advance the current trigger.
\* Must be the last conjunct of an action (uses grants').
Emit(e) == /\ lastEv' = e
           /\ fired' = (fired \/ Matches(Trig(pc), e))
           /\ trigG' = IF ~fired /\ Matches(Trig(pc), e) THEN LastGrant' ELSE trigG
           /\ UNCHANGED pc

\* derives: C1.1, C1.4 -- internal (non-observable) protocol step
Internal(what, p) == Emit([event |-> "Internal", what |-> what, proc |-> p])

\* ---------------------------------------------------------------------------
\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
Init ==
    /\ up = [p \in Procs |-> TRUE]
    /\ paused = [c \in Clients |-> FALSE]
    /\ sideA = Procs
    /\ promised = [n \in Nodes |-> 0]
    /\ maxTok = [n \in Nodes |-> 0]
    /\ leader = [n \in Nodes |-> FALSE]
    /\ term = [n \in Nodes |-> 0]
    /\ ltok = [n \in Nodes |-> 0]
    /\ reqs = {}
    /\ pending = [c \in Clients |-> FALSE]
    /\ tok = [c \in Clients |-> NoTok]
    /\ myToks = [c \in Clients |-> {}]
    /\ awaiting = [c \in Clients |-> {}]
    /\ grantMsgs = {}
    /\ writeMsgs = {}
    /\ ackMsgs = {}
    /\ dups = 0
    /\ highest = 0
    /\ stval = "none"
    /\ toAck = {}
    /\ grants = <<>>
    /\ decisions = <<>>
    /\ told = {}
    /\ pc = 1
    /\ fired = IsStart(Trig(1))
    /\ trigG = [node |-> "none", client |-> "none"]
    /\ lastEv = [event |-> "Init"]

\* ===========================================================================
\* Grantor (abstract): leader per term, majority election, majority-confirmed grants
\* ===========================================================================

\* derives: C1.1, C1.4, F1.1, F1.2
\* A node that cannot reach a leader of a term at least its own promise starts an
\* election; a majority Q (reachable, up) promises a fresh term; the new leader
\* learns the highest token any member of Q confirmed.
Elect(n) ==
    /\ up[n] /\ ~leader[n]
    /\ ~\E m \in Nodes : up[m] /\ Conn(n, m) /\ leader[m] /\ term[m] >= promised[n]
    /\ \E Q \in SUBSET {q \in Nodes : up[q] /\ Conn(n, q)} :
        /\ n \in Q
        /\ Majority(Q)
        /\ LET t == 1 + Max({promised[q] : q \in Q}) IN
           /\ t <= MaxTerm
           /\ promised' = [q \in Nodes |-> IF q \in Q THEN t ELSE promised[q]]
           /\ leader' = [q \in Nodes |-> IF q = n THEN TRUE
                                         ELSE IF q \in Q THEN FALSE ELSE leader[q]]
           /\ term' = [term EXCEPT ![n] = t]
           /\ ltok' = [ltok EXCEPT ![n] = Max({maxTok[q] : q \in Q})]
    /\ UNCHANGED <<up, paused, sideA, maxTok, reqs, pending, tok, myToks, awaiting,
                   grantMsgs, writeMsgs, ackMsgs, dups, highest, stval, toAck,
                   grants, decisions, told>>
    /\ Internal("Elect", n)

\* derives: C1.1, C1.4, F1.2 -- a leader that reaches a node promised to a higher term steps down
StepDown(n) ==
    /\ up[n] /\ leader[n]
    /\ \E q \in Nodes : up[q] /\ Conn(n, q) /\ promised[q] > term[n]
    /\ leader' = [leader EXCEPT ![n] = FALSE]
    /\ promised' = [promised EXCEPT ![n] =
                      Max({promised[q] : q \in {x \in Nodes : up[x] /\ Conn(n, x)}})]
    /\ UNCHANGED <<up, paused, sideA, maxTok, term, ltok, reqs, pending, tok, myToks,
                   awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
                   toAck, grants, decisions, told>>
    /\ Internal("StepDown", n)

\* derives: C1.1, C1.4, F1.1, F1.2
\* The leader issues a grant to a requester it can reach, once a majority still
\* promised to its term durably confirms the new token.
Grant(n, c) ==
    /\ up[n] /\ leader[n]
    /\ c \in reqs
    /\ Conn(n, c)
    /\ ~\E m \in grantMsgs : m.c = c
    /\ \E Q \in SUBSET {q \in Nodes : up[q] /\ Conn(n, q) /\ promised[q] = term[n]} :
        /\ n \in Q
        /\ Majority(Q)
        /\ LET k == ltok[n] + 1 IN
           /\ maxTok' = [q \in Nodes |-> IF q \in Q THEN Max({maxTok[q], k}) ELSE maxTok[q]]
           /\ ltok' = [ltok EXCEPT ![n] = k]
           /\ grantMsgs' = grantMsgs \cup {[n |-> n, c |-> c, t |-> k, g |-> term[n]]}
           /\ grants' = Append(grants, [token |-> k, term |-> term[n], node |-> n, client |-> c])
           /\ UNCHANGED <<up, paused, sideA, promised, leader, term, reqs, pending, tok,
                          myToks, awaiting, writeMsgs, ackMsgs, dups, highest, stval,
                          toAck, decisions, told>>
           /\ Emit([event |-> "Grant", client |-> c, key |-> Key, token |-> k,
                    lifetime |-> Lifetime, grantor_term |-> term[n], node |-> n])

\* derives: C1.4, F1.3 -- a (running, unpaused) client receives a grant reply
RecvGrant(m) ==
    /\ m \in grantMsgs
    /\ up[m.c] /\ ~paused[m.c]
    /\ grantMsgs' = grantMsgs \ {m}
    /\ IF pending[m.c]
       THEN /\ tok' = [tok EXCEPT ![m.c] = [t |-> m.t, g |-> m.g]]
            /\ myToks' = [myToks EXCEPT ![m.c] = @ \cup {[t |-> m.t, g |-> m.g]}]
            /\ pending' = [pending EXCEPT ![m.c] = FALSE]
            /\ reqs' = reqs \ {m.c}
       ELSE UNCHANGED <<tok, myToks, pending, reqs>>
    /\ UNCHANGED <<up, paused, sideA, promised, maxTok, leader, term, ltok, awaiting,
                   writeMsgs, ackMsgs, dups, highest, stval, toAck, grants, decisions, told>>
    /\ Internal("RecvGrant", m.c)

\* ===========================================================================
\* Storage
\* ===========================================================================

\* derives: C1.2, C1.3, F1.1
\* Storage decides a write: accept iff token >= ledger; on accept the token becomes
\* the ledger. The ack is queued (volatile) and sent by SendAck. dup = TRUE models a
\* duplicated delivery (the message stays in flight), bounded by MaxDups.
StorageDecide(m, dup) ==
    /\ up[Store]
    /\ m \in writeMsgs
    /\ dup => dups < MaxDups
    /\ LET acc == m.t >= highest
           out == IF acc THEN "accept" ELSE "reject" IN
       /\ highest' = IF acc THEN m.t ELSE highest
       /\ stval' = IF acc THEN m.v ELSE stval
       /\ writeMsgs' = IF dup THEN writeMsgs ELSE writeMsgs \ {m}
       /\ dups' = IF dup THEN dups + 1 ELSE dups
       /\ decisions' = Append(decisions, [token |-> m.t, hb |-> highest, outcome |-> out,
                                          client |-> m.c, value |-> m.v, term |-> m.g])
       /\ toAck' = toAck \cup {[c |-> m.c, t |-> m.t, g |-> m.g, v |-> m.v, outcome |-> out]}
       /\ UNCHANGED <<up, paused, sideA, promised, maxTok, leader, term, ltok, reqs,
                      pending, tok, myToks, awaiting, grantMsgs, ackMsgs, grants, told>>
       /\ Emit([event |-> IF acc THEN "WriteAccept" ELSE "WriteReject", key |-> Key,
                token |-> m.t, highest_before |-> highest, grantor_term |-> m.g,
                client |-> m.c, value |-> m.v])

\* derives: C1.3, F1.1, F1.2 -- storage sends a queued ack (lost if the client is cut off or down)
SendAck(a) ==
    /\ up[Store]
    /\ a \in toAck
    /\ toAck' = toAck \ {a}
    /\ ackMsgs' = IF Conn(Store, a.c) /\ up[a.c] THEN ackMsgs \cup {a} ELSE ackMsgs
    /\ UNCHANGED <<up, paused, sideA, promised, maxTok, leader, term, ltok, reqs, pending,
                   tok, myToks, awaiting, grantMsgs, writeMsgs, dups, highest, stval,
                   grants, decisions, told>>
    /\ Internal("SendAck", Store)

\* derives: C1.3, F1.3 -- a client receives an ack for a write it is awaiting
\* and is told the write's outcome exactly as the ack states it.
RecvAck(a) ==
    /\ a \in ackMsgs
    /\ up[a.c] /\ ~paused[a.c]
    /\ ackMsgs' = ackMsgs \ {a}
    /\ LET w == [t |-> a.t, g |-> a.g, v |-> a.v] IN
       IF w \in awaiting[a.c]
       THEN /\ awaiting' = [awaiting EXCEPT ![a.c] = @ \ {w}]
            /\ told' = IF a.outcome = "accept" THEN told \cup {[c |-> a.c, t |-> a.t, v |-> a.v]}
                       ELSE told
            /\ UNCHANGED <<up, paused, sideA, promised, maxTok, leader, term, ltok, reqs,
                           pending, tok, myToks, grantMsgs, writeMsgs, dups, highest,
                           stval, toAck, grants, decisions>>
            /\ Emit([event |-> "WriteAck", client |-> a.c, key |-> Key, token |-> a.t,
                     outcome |-> IF a.outcome = "accept" THEN "accepted" ELSE "rejected",
                     value |-> a.v, grantor_term |-> a.g])
       ELSE /\ UNCHANGED <<up, paused, sideA, promised, maxTok, leader, term, ltok, reqs,
                           pending, tok, myToks, awaiting, grantMsgs, writeMsgs, dups,
                           highest, stval, toAck, grants, decisions, told>>
            /\ Internal("DropAck", a.c)

\* ===========================================================================
\* Schedule steps: workload (derives from the contract) and faults (one per cell)
\* ===========================================================================

\* derives: F1.2, F1.3 -- resolve "grantor"/"holder" at trigger time
Resolve(x) == IF x = "grantor" THEN trigG.node
              ELSE IF x = "holder" THEN trigG.client ELSE x

\* derives: C1.2, F1.3 -- the client's most recent superseded token (lower than the highest granted)
StaleTok(c) ==
    LET S == {x \in myToks[c] : x.t < MaxGranted} IN
    IF S = {} THEN NoTok ELSE CHOOSE x \in S : \A y \in S : y.t <= x.t

\* derives: C1.4 -- workload: client requests a grant (a client already waiting for
\* a grant does not issue a second request; the step waits until it is not waiting)
DoRequest(c) ==
    /\ up[c] /\ ~paused[c]
    /\ ~pending[c]
    /\ pending' = [pending EXCEPT ![c] = TRUE]
    /\ reqs' = reqs \cup {c}
    /\ UNCHANGED <<up, paused, sideA, promised, maxTok, leader, term, ltok, tok, myToks,
                   awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval, toAck,
                   grants, decisions, told>>
    /\ lastEv' = [event |-> "Request", client |-> c, key |-> Key]

\* derives: C1.2, C1.3, F1.3 -- workload: client writes with its current (or stale) token
DoWrite(c, v, stale) ==
    LET k == IF stale THEN StaleTok(c) ELSE tok[c] IN
    /\ up[c] /\ ~paused[c]
    /\ k.t > 0
    /\ writeMsgs' = IF Conn(c, Store) /\ up[Store]
                    THEN writeMsgs \cup {[c |-> c, t |-> k.t, g |-> k.g, v |-> v]}
                    ELSE writeMsgs
    /\ awaiting' = [awaiting EXCEPT ![c] = @ \cup {[t |-> k.t, g |-> k.g, v |-> v]}]
    /\ UNCHANGED <<up, paused, sideA, promised, maxTok, leader, term, ltok, reqs, pending,
                   tok, myToks, grantMsgs, ackMsgs, dups, highest, stval, toAck,
                   grants, decisions, told>>
    /\ lastEv' = [event |-> "WriteAttempt", client |-> c, key |-> Key, token |-> k.t,
                  value |-> v, grantor_term |-> k.g]

\* derives: F1.1 -- crash-stop: volatile state lost, durable state kept, messages to p lost
Crash(p) ==
    /\ up[p]
    /\ up' = [up EXCEPT ![p] = FALSE]
    /\ IF p \in Nodes
       THEN /\ leader' = [leader EXCEPT ![p] = FALSE]
            /\ term' = [term EXCEPT ![p] = 0]
            /\ ltok' = [ltok EXCEPT ![p] = 0]
            /\ UNCHANGED <<paused, reqs, pending, tok, myToks, awaiting, grantMsgs,
                           writeMsgs, ackMsgs, toAck>>
       ELSE IF p \in Clients
       THEN /\ paused' = [paused EXCEPT ![p] = FALSE]
            /\ reqs' = reqs \ {p}
            /\ pending' = [pending EXCEPT ![p] = FALSE]
            /\ tok' = [tok EXCEPT ![p] = NoTok]
            /\ myToks' = [myToks EXCEPT ![p] = {}]
            /\ awaiting' = [awaiting EXCEPT ![p] = {}]
            /\ grantMsgs' = {m \in grantMsgs : m.c # p}
            /\ ackMsgs' = {a \in ackMsgs : a.c # p}
            /\ UNCHANGED <<leader, term, ltok, writeMsgs, toAck>>
       ELSE \* storage
            /\ writeMsgs' = {}
            /\ toAck' = {}
            /\ UNCHANGED <<leader, term, ltok, paused, reqs, pending, tok, myToks,
                           awaiting, grantMsgs, ackMsgs>>
    /\ UNCHANGED <<sideA, promised, maxTok, dups, highest, stval, grants, decisions, told>>
    /\ lastEv' = [event |-> "Fault", cell |-> "F1.1", action |-> "crash", target |-> p]

\* derives: F1.1
\* mutation: P1 maxTok treated as volatile: a restarted lease node forgets every token it confirmed
Restart(p) ==
    /\ ~up[p]
    /\ up' = [up EXCEPT ![p] = TRUE]
    /\ maxTok' = IF p \in Nodes THEN [maxTok EXCEPT ![p] = 0] ELSE maxTok \* mutation: P1
    /\ UNCHANGED <<paused, sideA, promised, leader, term, ltok, reqs, pending, tok,
                   myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
                   toAck, grants, decisions, told>>
    /\ lastEv' = [event |-> "Fault", cell |-> "F1.1", action |-> "restart", target |-> p]

\* derives: F1.2 -- complete bipartition; messages in flight across the cut are lost
Partition(A) ==
    /\ A # {} /\ A # Procs
    /\ sideA' = A
    /\ LET C(p, q) == (p \in A) <=> (q \in A) IN
       /\ grantMsgs' = {m \in grantMsgs : C(m.n, m.c)}
       /\ writeMsgs' = {m \in writeMsgs : C(m.c, Store)}
       /\ ackMsgs' = {a \in ackMsgs : C(Store, a.c)}
    /\ UNCHANGED <<up, paused, promised, maxTok, leader, term, ltok, reqs, pending, tok,
                   myToks, awaiting, dups, highest, stval, toAck, grants, decisions, told>>
    /\ lastEv' = [event |-> "Fault", cell |-> "F1.2", action |-> "partition", sideA |-> A]

\* derives: F1.2 -- the partition heals; lost messages stay lost
Heal ==
    /\ sideA' = Procs
    /\ UNCHANGED <<up, paused, promised, maxTok, leader, term, ltok, reqs, pending, tok,
                   myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
                   toAck, grants, decisions, told>>
    /\ lastEv' = [event |-> "Fault", cell |-> "F1.2", action |-> "heal", target |-> "all"]

\* derives: F1.3 -- holder pause: the client takes no steps; the rest of the world proceeds
Pause(c) ==
    /\ up[c] /\ ~paused[c]
    /\ paused' = [paused EXCEPT ![c] = TRUE]
    /\ UNCHANGED <<up, sideA, promised, maxTok, leader, term, ltok, reqs, pending, tok,
                   myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
                   toAck, grants, decisions, told>>
    /\ lastEv' = [event |-> "Fault", cell |-> "F1.3", action |-> "pause", target |-> c]

\* derives: F1.3 -- resume as if no time had passed (the client keeps its old token)
Resume(c) ==
    /\ paused[c]
    /\ paused' = [paused EXCEPT ![c] = FALSE]
    /\ UNCHANGED <<up, sideA, promised, maxTok, leader, term, ltok, reqs, pending, tok,
                   myToks, awaiting, grantMsgs, writeMsgs, ackMsgs, dups, highest, stval,
                   toAck, grants, decisions, told>>
    /\ lastEv' = [event |-> "Fault", cell |-> "F1.3", action |-> "resume", target |-> c]

\* derives: F1.2 -- the side of a partition step, after resolving grantor/holder/rest
SideOf(st) ==
    LET a == {Resolve(x) : x \in st.a \ {"rest"}}
        b == {Resolve(x) : x \in st.b \ {"rest"}} IN
    IF "rest" \in st.a THEN Procs \ b ELSE a

\* derives: C1.2, C1.4, F1.1, F1.2, F1.3 -- the effect of one schedule step
DoStep(st) ==
    CASE st.kind = "request"   -> DoRequest(Resolve(st.p))
      [] st.kind = "write"     -> DoWrite(Resolve(st.p), st.v, st.stale)
      [] st.kind = "crash"     -> Crash(Resolve(st.p))
      [] st.kind = "restart"   -> Restart(Resolve(st.p))
      [] st.kind = "partition" -> Partition(SideOf(st))
      [] st.kind = "heal"      -> Heal
      [] st.kind = "pause"     -> Pause(Resolve(st.p))
      [] st.kind = "resume"    -> Resume(Resolve(st.p))

\* derives: F1.1, F1.2, F1.3 -- apply step pc once its trigger has held; arm the next trigger
ScheduleStep ==
    /\ pc <= Len(Steps)
    /\ fired
    /\ DoStep(Steps[pc])
    /\ pc' = pc + 1
    /\ fired' = (IsStart(Trig(pc + 1)) \/ Matches(Trig(pc + 1), lastEv'))
    /\ trigG' = IF fired' THEN LastGrant ELSE trigG

\* ===========================================================================
\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
Protocol ==
    \/ \E n \in Nodes : Elect(n) \/ StepDown(n)
    \/ \E n \in Nodes, c \in Clients : Grant(n, c)
    \/ \E m \in grantMsgs : RecvGrant(m)
    \/ \E m \in writeMsgs, d \in BOOLEAN : StorageDecide(m, d)
    \/ \E a \in toAck : SendAck(a)
    \/ \E a \in ackMsgs : RecvAck(a)

\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
Next == Protocol \/ ScheduleStep

\* derives: C1.4 -- weak fairness on every protocol action and on the schedule
\* (the environment does eventually perform each scheduled step whose trigger held)
Fairness ==
    /\ \A n \in Nodes : WF_vars(Elect(n)) /\ WF_vars(StepDown(n))
    /\ \A n \in Nodes, c \in Clients : WF_vars(Grant(n, c))
    /\ WF_vars(\E m \in grantMsgs : RecvGrant(m))
    /\ WF_vars(\E m \in writeMsgs : StorageDecide(m, FALSE))
    /\ WF_vars(\E a \in toAck : SendAck(a))
    /\ WF_vars(\E a \in ackMsgs : RecvAck(a))
    /\ WF_vars(ScheduleStep)

\* derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
Spec == Init /\ [][Next]_vars /\ Fairness

\* ===========================================================================
\* Properties
\* ===========================================================================

\* derives: C1.1, C1.2, C1.3 -- shape of the state (catches modelling errors, not a clause)
TypeOK ==
    /\ up \in [Procs -> BOOLEAN]
    /\ paused \in [Clients -> BOOLEAN]
    /\ sideA \subseteq Procs
    /\ highest \in Nat
    /\ pc \in 1..(Len(Steps) + 1)

\* derives: C1.1 -- each grant's token is strictly greater than every earlier grant's
C1_1 == \A i, j \in 1..Len(grants) : i < j => grants[i].token < grants[j].token

\* derives: C1.2 -- storage accepts only tokens >= every token it accepted before
\* (stated over the decision history, not over storage's own ledger variable, so a
\* ledger that forgets is caught; the ledger update is implied by this)
C1_2 == \A i \in 1..Len(decisions) :
          decisions[i].outcome = "accept" =>
            \A j \in 1..(i - 1) : decisions[j].outcome = "accept" =>
                                    decisions[j].token <= decisions[i].token

\* derives: C1.3 -- every write a client was told succeeded was accepted by storage
C1_3 == \A x \in told : \E i \in 1..Len(decisions) :
          /\ decisions[i].outcome = "accept"
          /\ decisions[i].client = x.c
          /\ decisions[i].token = x.t
          /\ decisions[i].value = x.v

\* derives: C1.4 -- a majority of lease nodes and storage are up and mutually
\* connected, and connected to client c, which is up and not paused
Good(c) == /\ up[Store] /\ up[c] /\ ~paused[c]
           /\ Conn(c, Store)
           /\ \E Q \in SUBSET Nodes : Majority(Q) /\ \A q \in Q : up[q] /\ Conn(q, Store)

\* derives: C1.4 -- if the good condition eventually holds forever, every pending
\* requester eventually stops waiting (obtains a grant)
C1_4 == \A c \in Clients : (<>[]Good(c)) => [](pending[c] => <>(~pending[c]))

\* derives: C1.1, C1.4 -- bound check: no election ever reaches the last allowed term,
\* so MaxTerm never constrains a behaviour (run.sh reports a violation as UNEXPLAINED)
TermHeadroom == \A n \in Nodes : promised[n] < MaxTerm

\* derives: F1.1, F1.2, F1.3 -- witness target: the run ended and the system is quiescent
Quiescent == /\ grantMsgs = {} /\ writeMsgs = {} /\ ackMsgs = {} /\ toAck = {}
             /\ \A c \in Clients : ~pending[c] \/ ~up[c]
\* derives: F1.1, F1.2, F1.3 -- violated by any trace that reaches the end of the schedule
NotEnded == ~(Done /\ Quiescent)
\* derives: F1.1, F1.2, F1.3 -- weaker witness: the schedule's end trigger fired
NotDone == ~Done
=============================================================================
