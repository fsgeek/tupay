# Paired tests v1: the shared (clause × cell) list

Fixed 2026-10-20 before either author starts. Each author writes its own half of every pair from this list and the two input files, and nothing else. Every pair name below is the derivation tag for both halves and for both mutations.

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

## Mutation pairs
Each pair has a deliberately broken model and a deliberately broken implementation, and the pair must fail against each. Each author names its mutation in the test before running it. A mutation must sit on the path that enforces the clause (for example, storage comparing with `>` instead of `>=` does not break C1.2; skipping the comparison does). The steward checks placement, not the mutation's content.

## The false-suspicion run (M1 requirement)
Schedule: F1.2 isolating the grantor from the other two lease nodes while the holder stays reachable from both the old grantor and storage. The remaining nodes may elect a new grantor and issue a new grant. The run is observed, not judged: its provenance must let a reader say, for every `WriteAccept` and `WriteReject`, which grant and which grantor term it traces to.
