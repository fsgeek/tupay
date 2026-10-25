# Recognised sections, extracted unchanged (D1 phase 0)

Not read by the steward; passed to no step but phase 3 contamination scoring.

## codex-1
I recall the general class of stale-read bugs in Raft implementations, also explicitly mentioned in §6.4; I do not recall a sufficiently specific independent report to name an implementation honestly. The clock-lease dependency is E49; missing heartbeat/read-barrier checks themselves are algorithm or implementation defects, not environment contracts.

## codex-2
I recognise no specific reported implementation bug from independent recall with enough confidence to name it. The source itself reports stale-read bugs in two third-party implementations (§6.4, reference [45]); those concern missing algorithm precautions, not a requirement that the network never partition.

## grok-1
- E4 and E5 are the contracts behind restoring a data directory or a VM disk onto a member that still has its old identity, including restoring a snapshot beside a live peer; I recall this class from etcd operator incidents and from Hashicorp Raft deployments, and the dissertation already states both contracts.
- E6, E7, and E8 are the contracts behind lost votes and lost log tails when a flush is not power-fail durable; I recall the Linux fsync-error discussions and etcd's warnings about disks that do not actually persist a flush, and Table 10.1 turns write caching off.
- E23 is the contract behind stale reads when a leader lease outruns follower clocks; I recall the same failure mode from CockroachDB clock-offset incidents, and the dissertation states it directly.
- E24, E26, and E27 are the contracts behind divergent replicas and double applies in application state machines, including session state dropped at snapshot time; I have seen that class in services built on Raft, and the dissertation states each piece.
- E32 and E33 are the contracts behind Figure 6.2; retries that mint a new request id are the usual client bug I recall in services on etcd and on custom Raft libraries.
- E19 and E22 are the contracts behind leader flapping when fsync or a garbage-collection pause exceeds the election timeout; I recall that pattern on JVM and cloud deployments.
- The stale read-only queries Jepsen found in two Raft implementations, which §6.4 cites, were implementations skipping the confirming-heartbeat read rule, so I did not enter them as an environment contract.

## grok-2
- E3: etcd's operational guidance requires the WAL to reach stable media (fsync, write cache off or a power-loss-protected disk); this dissertation's LogCabin setup records "write caching off" in §10.3. I recall the same class from disks that acknowledge a flush from a volatile cache. I am not pinning one CVE from memory.
- E7: I recall etcd documentation and production incidents where one member was restored from an older data-directory snapshot, or restarted empty under the same member id, and the cluster lost committed data or diverged; copying a data directory to clone a member is the same failure.
- E8: I recall etcd taking an exclusive lock on the data directory so two processes cannot run one member.
- E13: I recall etcd clusters failing to keep a leader when disk fsync latency exceeded the election timeout, especially on cloud volumes.
- E16: I recall etcd leader churn when a process pause or a clock step exceeded the election timeout; the symptom is elections, matching the availability bound rather than a safety break.
- E18: I recall hashicorp/raft's lease-based read-only option, documented to assume bounded clock drift, the same assumption as §6.4.1. I also recall CockroachDB leaseholder incidents in which a clock jump broke linearizability; I am not certain of the post's title.
- E33: I recall operators starting more than one etcd with `--force-new-cluster`, so two servers each believed they were the sole committed configuration.
- E34: the returned-server extra vote is the case §4 already states; I have seen the same failure described for address takeover without fencing.
- E35: I recall Kubernetes etcd controllers and hand-run membership changes that removed a voting member before its replacement had caught up, leaving a cluster one fault from losing quorum.
- E20: I recall custom state machines that read local time or a random source inside apply and diverged; I do not have one canonical incident name.
- E38: I recall applications that retry a non-idempotent command as a new request after a lost response. This is the failure §6.3 is written to prevent; I am not naming a separate paper.
- The stale reads Jepsen reported for etcd and Consul (Kingsbury, "Call me maybe: etcd and Consul", cited as [45] in §6.4 and §8.3) are an implementation skipping the read-only quorum check, under a partition §2.1 says safety must survive. I do not count that as one of these environment contracts.
