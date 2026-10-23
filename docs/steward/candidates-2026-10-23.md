# Candidates: complex failures hypothesized but not proven (steward-only)

Requested by the sixth steward on 2026-10-23 after Tony's counsel (log, "the sixth steward accepts"): instead of a litmus test of "discover an unknown failure class", look for complex failures that are hypothesized but not proven, then demonstrate one concretely, enough to convince a skeptical steward. Produced by a Claude subagent (general-purpose, web access) from a brief that asked it to separate what sources say from its inference and to exclude the 2015 Raft membership bug. **The steward has not yet verified these sources.** Kept under `docs/steward/` so it reaches no author, hold-out writer or judge of X3.

Summary of the report (sources as the agent gave them; [S] = the source says, [I] = the agent's inference):

1. **etcd-io/raft `ReadOnlyLeaseBased` + CheckQuorum stale read without clock faults.** etcd-io/raft#166 (open since 2024-02), #99; LeaseGuard (arXiv 2512.15659). [S] reporter's own test, self-doubted; a contributor: leases "did not appear correct/usable". [I] from current `raft.go`: lease reads answer immediately; the leader steps down only near 2×ET after a partition, while followers may elect after ET to 2ET. 3 nodes, one partition, deterministic ticks. Small.
2. **ZooKeeper `sync()` + read not linearizable across a leader change.** ZOOKEEPER-1675 (open since 2013), ZOOKEEPER-2136, apache/zookeeper PR #2069 (stalled), Jepsen ZooKeeper 2019 note. No published end-to-end reproduction. 3 to 5 servers, partial partition. Small to medium.
3. **hashicorp/raft leader-lease reads (Consul `default` mode) stale.** hashicorp/raft#108 (stale-closed 2019, disputed); Consul docs concede "a small window". 3 nodes, partial partition, lease vs heartbeat timeouts. Medium.
4. **Vault HA backends other than Consul lack write fencing (key management).** hashicorp/vault PR #23013 fenced Consul only. [I] code search finds `RegisterActiveNodeLock` only in `physical/consul`; etcd, ZooKeeper, DynamoDB and other HA backends appear unfenced, so a deposed active node could overwrite (e.g. lose a revocation). Medium; risk: "community backend" dismissal.
5. **Kubernetes #59848: stale watch cache, two kubelets run one StatefulSet pod.** Open since 2018, "still fundamentally broken" (2021), never cleanly reproduced. Large to implement.
6. **Kafka last-replica-standing (KIP-966):** unclean shutdown of the sole ISR member destroys acked data. Scenario, no incident. Medium (page-cache-loss fault).
7. **Kafka transactions after KIP-890:** Jepsen Bufstream report §6.4's open hypotheses (sequence reuse on timeout, delayed Produce into a later transaction). Large.
8. **Redlock under clock step, or under bounded drift alone** (Kleppmann 2016; antirez reply). The bounded-drift question is the disputed one. Small.
9. **GitHub, Oct 2020: ZooKeeper elected a second leader while hosts were added.** Mechanism unstated. Small; risk: pure misconfiguration.
10. **Raft PreVote + CheckQuorum liveness under partial partitions** (Howard & Abraham 2020; OmniPaxos). Argued informally. Small to medium; Jensen/Howard/Mortier 2021 not opened.
11. **SPIRE nested CA rotation: SVID rejected before bundle propagates** (spiffe/spire#5317, stale-closed). Medium; availability, not safety.
12. **client-go leader election: two leaders under clock-rate skew** (vendor docs concede it). Small.

Excluded as already reproduced or fixed: NATS 2.12.1, etcd #15247, etcd #13883, KAFKA-15489, Vault Consul split-brain, Cassandra LWT (unconfirmed).

The agent's top three for a first demonstration: #1 (smallest, deterministic, no clock rebuttal, upstream harness, natural mutation pair), #2 (13-year-old open question with a stalled fix that a result would inform), #4 (key management, ready test template). The full report is in this session's transcript (khipumaq).
