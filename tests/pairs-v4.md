# Paired tests v4: the shared (clause × cell) list for contract v3 under failure model v3

**DRAFT 3, not registered.** Drafted 2026-10-23 for X3; P44, P50 and P51 reworded after the second input review. Self-contained: P1 to P30 from `pairs-v3.md` are restated with id and wording unchanged; P31 to P57 are added. Every pair name is the derivation tag for both halves and both mutations.

**Which crossings are pairs, and why (registered with X3).** Every new clause crossed with every new cell (F3.1 to F3.3), and C1.1, C1.2 and C1.4 crossed with every new cell: 27 pairs (P31 to P57). Not paired: C1.3, C2.1 and C2.2 crossed with F3.x, because a storage decision depends only on the token presented and the ledger, which membership does not touch, and a storage decision that consults a clock is caught by P44 (C3.5 under F3.2); and C3.x crossed with F1.x or F2.x on their own, because F3.1 schedules apply reconfiguration while those cells are in effect. The full cross would add 66 pairs (twelve clauses by eight cells, less the thirty existing); the steward judged that cost larger than what the further 39 would discriminate. Hold-out authors are told nothing of this cut and may aim at what it leaves out, which tests it.

| Pair | Derives | What the pair checks |
|---|---|---|
| P1 | C1.1, F1.1 | Grantor nodes crash and restart; tokens still strictly increase across grantor incarnations. |
| P2 | C1.1, F1.2 | Grantor partitioned from its peers; two grantor incarnations may exist; tokens still strictly increase. |
| P3 | C1.1, F1.3 | Holder paused past lifetime; the next grant's token exceeds the paused holder's. |
| P4 | C1.2, F1.1 | Storage crashes and restarts; a write with a stale token is still rejected afterwards. |
| P5 | C1.2, F1.2 | Holder cut off from grantor but connected to storage; after a new grant is accepted, the old holder's writes are rejected. |
| P6 | C1.2, F1.3 | Paused holder resumes and writes; rejected if a newer token has been accepted. |
| P7 | C1.3, F1.1 | Client or storage crashes between accept and ack; no client is told success for a write storage did not accept. |
| P8 | C1.3, F1.2 | Ack lost in a partition; the client is not told success. |
| P9 | C1.3, F1.3 | Paused client receives a late ack; it refers to a write storage actually accepted. |
| P10 | C1.4, F1.1 | A minority of lease nodes crash; a requester still eventually gets a grant. |
| P11 | C1.4, F1.2 | Partition heals; a requester on the majority side eventually gets a grant. |
| P12 | C1.4, F1.3 | Holder paused past lifetime; another requester eventually gets a grant. |
| P13 | C2.1, F1.1 | Storage crashes and restarts after accepting a newer token; a read with a stale token is still rejected afterwards. |
| P14 | C2.1, F1.2 | Holder cut off from the grantor but connected to storage; after a newer token's write is accepted, the old holder's read is rejected. |
| P15 | C2.1, F1.3 | Paused holder resumes and reads; rejected if a newer token has been accepted. |
| P16 | C2.2, F1.1 | Storage crashes between serving a read and the ack, or the client crashes after the serve; no client is given a value storage did not serve, and the value given is the one served. |
| P17 | C2.2, F1.2 | Read ack lost in a partition; the client is not given a value; a later served read's value matches storage. |
| P18 | C2.2, F1.3 | Paused client receives a late read ack; it refers to a read storage served and carries the value served. |
| P19 | C1.1, F2.1 | After the first grant, the link between the grantor and one follower is cut both ways; the cut-off follower may start elections through the node both still reach; every later grant's token exceeds every earlier one. |
| P20 | C1.1, F2.2 | The grantor can send to the other lease nodes but not hear them; whether it keeps acting or a new grantor emerges, tokens still strictly increase. |
| P21 | C1.2, F2.1 | The grantor is cut from the other lease nodes only, still reaching both clients and storage (not a bipartition); after the new holder's write is accepted, the old holder's write is rejected. |
| P22 | C1.2, F2.2 | The old holder can send to everyone but hears nothing from the lease nodes; after the new holder's write is accepted, the old holder's write is rejected. |
| P23 | C1.3, F2.1 | Only the holder–storage link is cut, after storage accepts; the client is not told success for that write or a later one that never arrives. |
| P24 | C1.3, F2.2 | Storage hears the holder but its replies to the holder are lost; writes may be accepted, and the client is not told success for any of them. |
| P25 | C1.4, F2.1 | After the first grant, the link between the grantor and one follower is cut both ways and stays cut; the grantor, the other follower, storage and a requester stay connected; the requester eventually gets a grant. |
| P26 | C1.4, F2.2 | After the first grant, the grantor stops hearing the other lease nodes but they still hear it; the two followers, storage and a requester stay connected; the requester eventually gets a grant. |
| P27 | C2.1, F2.1 | As P21, with a read: the old holder's read after the new holder's accepted write is rejected. |
| P28 | C2.1, F2.2 | As P22, with a read: the old holder, hearing nothing from the lease nodes, reads after the new holder's accepted write and is rejected. |
| P29 | C2.2, F2.1 | Only the holder–storage link is cut, after storage serves a read; the client is not given a value; after the heal a served read's value matches storage. |
| P30 | C2.2, F2.2 | Storage hears the holder's read but its reply is lost; the client is not given a value; after the heal a served read's value matches storage. |
| P31 | C3.1, F3.1 | Two reconfiguration requests naming different member sets arrive at different members before either is answered; committed epochs strictly increase and no epoch has two configurations. |
| P32 | C3.1, F3.2 | The grantor's clock jumps back by several lifetimes while a reconfiguration is in progress; committed epochs strictly increase and no epoch has two configurations. |
| P33 | C3.1, F3.3 | After a configuration is committed, a member that agreed to it crashes and restarts amnesic, and a reconfiguration request is sent to it; no epoch is committed twice. |
| P34 | C3.2, F3.1 | A reconfiguration removes the grantor, sent to the grantor itself; every later grant is agreed by a majority of the configuration it names, none of whose counted members had learned of a newer one. |
| P35 | C3.2, F3.2 | A node removed by a committed reconfiguration stays up and its clock jumps forward past every lifetime; it takes part in no grant under the old configuration. |
| P36 | C3.2, F3.3 | A configuration change is committed; one member that agreed to it restarts amnesic while a member that never learned of it is still up; no grant is agreed by a majority of the old configuration that counts either. |
| P37 | C3.3, F3.1 | A reconfiguration request is sent to a non-member, which forwards or refuses it; the operator is told success only for a configuration that was committed. |
| P38 | C3.3, F3.2 | The clock of the node that received a reconfiguration request jumps forward before the commit; the operator is not told success early. |
| P39 | C3.3, F3.3 | The node that received a reconfiguration request crashes before answering and restarts amnesic; the operator is told success only for a committed configuration. |
| P40 | C3.4, F3.1 | A reconfiguration adds two nodes and removes one while a follower of the old configuration is partitioned away; majorities of both configurations stay connected; the request is eventually committed or refused. |
| P41 | C3.4, F3.2 | Every lease node's clock jumps back once during a reconfiguration; majorities of both configurations stay connected; the request is eventually committed or refused. |
| P42 | C3.4, F3.3 | A minority member restarts amnesic during a reconfiguration that does not re-add it; majorities of both configurations stay connected; the request is eventually committed or refused. |
| P43 | C3.5, F3.1 | Reconfiguration under a partial partition; every recorded decision (grant, storage decision, configuration commit) is re-derivable from its recorded inputs. |
| P44 | C3.5, F3.2 | The grantor's clock jumps around a grant's expiry, back then forward, while another client requests; every recorded decision is a function of its recorded inputs, clock readings included. |
| P45 | C3.5, F3.3 | An amnesic restart followed by its re-addition by reconfiguration; every recorded decision is re-derivable from its recorded inputs. |
| P46 | C1.1, F3.1 | The grantor is removed and replaced by nodes that were never members; the first grant under the new configuration carries a token greater than every token granted under the old one. |
| P47 | C1.1, F3.2 | The grantor's clock jumps back by several lifetimes between two grants; tokens still strictly increase. |
| P48 | C1.1, F3.3 | A minority member restarts amnesic and the grantor then crashes; tokens granted afterwards still exceed every earlier token. |
| P49 | C1.2, F3.1 | A holder of a grant under the old configuration is cut off from the lease nodes but not from storage while a reconfiguration commits and a new holder is granted and writes; the old holder's later write is rejected. |
| P50 | C1.2, F3.2 | A holder's clock jumps back by several lifetimes; after a newer holder's write is accepted, the old holder's write is rejected (what the old holder believes about expiry decides nothing). |
| P51 | C1.2, F3.3 | After an amnesic restart of a minority member, a new holder is granted and its write is accepted; then the previous holder's write is rejected. |
| P52 | C1.4, F3.1 | After a reconfiguration that removes the grantor is committed and answered, a majority of the new configuration, storage and a requester stay connected; the requester eventually gets a grant. |
| P53 | C1.4, F3.2 | After clock jumps on every lease node, a majority, storage and a requester stay connected; the requester eventually gets a grant. |
| P54 | C1.4, F3.3 | After a minority member restarts amnesic, a majority, storage and a requester stay connected; the requester eventually gets a grant. |
| P55 | C3.6, F3.1 | A member that has voted for a reconfiguration is still connected to the old grantor, which is cut off from the rest and asks it to vote for a grant under the old epoch; it does not, and no such grant is issued counting it. |
| P56 | C3.6, F3.2 | A member's clock jumps back by several lifetimes between its vote for a reconfiguration and a grant request under the old epoch; it still does not vote for that grant. |
| P57 | C3.6, F3.3 | A member that voted for a reconfiguration restarts amnesic before the commit; votes of its new incarnation are not counted toward any grant or commit until it is re-added. |

## Mutation pairs
Each pair has a deliberately broken model and a deliberately broken implementation on the clause's enforcing path, named before running. P1 to P18's mutations are unchanged unless an author finds that one no longer sits on the enforcing path, in which case it is re-placed and the change is recorded. For P25 and P26 (liveness), the mutation must break the mechanism by which the artifact makes progress under that cell, so that the mutated artifact fails C1.4 on the pair's shared schedule; if the unmutated artifact already fails, say so: the pair then has no working half to mutate, and that is a finding, not a gap to paper over.
For P31 to P57 the same rule applies. For C3.5 pairs, the mutation makes one decision consult an input it does not record (on the model side, a decision guarded by a variable absent from the emitted record; on the implementation side, an unrecorded clock read or map iteration), and the decision-replay check must report it.

## Changelog
- v4 (2026-10-23, draft 3): P31 to P57; P1 to P30 restated. Reason: X3, contract v3 and failure model v3.
- v3 (2026-10-21): P19 to P30; P1 to P18 restated. Reason: X2, failure model v2.
