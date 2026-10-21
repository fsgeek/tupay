# Paired tests v2: the shared (clause × cell) list for contract v2

Fixed 2026-10-21 for X1. P1 to P12 are unchanged from `pairs-v1.md` and keep their ids. Six pairs are added for the two new clauses. Every pair name is the derivation tag for both halves and both mutations.

| Pair | Derives | What the pair checks |
|---|---|---|
| P13 | C2.1, F1.1 | Storage crashes and restarts after accepting a newer token; a read with a stale token is still rejected afterwards. |
| P14 | C2.1, F1.2 | Holder cut off from the grantor but connected to storage; after a newer token's write is accepted, the old holder's read is rejected. |
| P15 | C2.1, F1.3 | Paused holder resumes and reads; rejected if a newer token has been accepted. |
| P16 | C2.2, F1.1 | Storage crashes between serving a read and the ack, or the client crashes after the serve; no client is given a value storage did not serve, and the value given is the one served. |
| P17 | C2.2, F1.2 | Read ack lost in a partition; the client is not given a value; a later served read's value matches storage. |
| P18 | C2.2, F1.3 | Paused client receives a late read ack; it refers to a read storage served and carries the value served. |

## Mutation pairs
As in v1: each pair has a deliberately broken model and a deliberately broken implementation on the clause's enforcing path, named before running. P1 to P12's mutations are unchanged unless an author finds that one no longer sits on the enforcing path, in which case it is re-placed and the change is recorded.

## Amendment 2026-10-21: P1 to P12 restated (additive; the regenerate arm has no v1)
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
