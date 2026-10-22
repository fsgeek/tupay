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
## README sections as committed before the first run (commit 938cb5b)
## Choices

<!-- derives: J1.1, J1.3, J1.5, G1.1, G1.2, G1.3, G1.4 -->

- Five independent Go goroutines own their member state. A discrete-event scheduler delivers one input at a time and waits for its response; this chooses an interleaving of concurrent actors without using wall time. Network requests and responses travel independently through a controlled queue. No goroutine reads another member's state.
- Logical timer units have no physical duration. Election timeouts are seeded random values in [40,80], heartbeats every 10, ordinary delivery delays in [1,3]. Seeded occasional extra delays, loss, and duplicates sample G1.2 as well as explicitly injected link failures. Stable member iteration order and scheduler tie-breaking make an entire run reproducible.
- A scheduler event is one timer firing, message delivery, administrator action, or fault. Bounds and settling count these events, including events that emit no contract record. Auxiliary `Scheduled` records expose this count in the observe file. Contract records emitted by one transition are atomic and are all checked; a bound never splits a transition. Actions fire after a seeded delay of 0 to 2 logical units. The next step is armed immediately before the action, so its synchronous records can match.
- The durable store is a member-owned in-memory storage object separate from volatile protocol state. Crash/restart preserves exactly term, vote, and journal. This simulates the stated crash model, not an OS process kill or disk corruption. Observer sequence numbers survive restart as observer metadata. Commit index and administrator requests do not survive. Configuration is recovered by scanning the durable log.
- All members begin with the scenario's initial configuration and an empty journal. A member whose latest configuration excludes itself does not initiate elections, but it still processes and votes on incoming RPCs without membership filtering. A removed leader finishes its pending configuration reply and steps down after commitment. No removed-server disruption suppression from omitted section 4.2 is added.
- Leaders replicate to their latest configuration, plus any server currently being caught up. On election all nextIndex values start at last index + 1 and matchIndex at zero; the leader counts its own durable journal in quorums. Responses carry the corresponding request's matched index; stale responses never decrease matchIndex or increase nextIndex beyond evidence. Failed probes decrement nextIndex with a floor at matchIndex + 1.
- AppendEntries sends the entire suffix at nextIndex. Empty requests confirm prevLogIndex. The follower advances commitIndex only through the last index covered by the request, never its unmatched trailing suffix. Entries are compared by term as Figure 3.1 specifies. Every committed index is recorded individually, including indirect commitments.
- Configuration applies immediately on append and reverts on truncation. Every requested change waits for the last configuration entry in the local journal to be committed, including inherited entries. No extra election no-op, joint consensus, commitment barrier from another specification, or special repair of the published membership algorithm is added.
- AddServer catch-up uses two successful replication rounds; an empty, already matched log completes immediately after evidence of a match. A round targets a snapshot of the leader's last index. Progress restarts a timeout of one election interval; the final round also has an absolute election-interval deadline. Step 2 precedes waiting on a previous configuration. Pending requests are serialized in arrival order. Already-present adds, absent removes, unknown identities, and removing the last member return `invalid`; followers return `not_leader`; catch-up failure returns `timeout`; successful completion returns `ok`.
- Command payloads are opaque YAML values; commands at nonleaders are ignored. Administrator changes are not automatically retried or redirected. Pending requests at a deposed leader receive `not_leader`; crashing loses them without a reply.
- Observe files contain the specified contract records plus ballots, acknowledgements, restart/reset records, and scheduler records. Ballot and acknowledgement records give precise evidence links. Election and commitment records carry the local configuration and the voters/acknowledgers counted; snapshots are auxiliary audit data. The checkers reconstruct journals from append/truncate records and reset only volatile commit knowledge on restart. J1.5(a) uses the epoch of the coordinator marking commitment, and keeps all historical obligations, including ones established later in record order than a higher-epoch election.
- Scenario names are labels only. Arbitrary paths and names use the same compiler. Invalid scenarios are reported as `UNEXPLAINED input`; unrealized triggers at the bound are `UNEXPLAINED steps`; FAIL takes precedence. If all actions run, the scheduler stops after the settle count or at the bound, as the shared format specifies.

## Concerns

<!-- derives: J1.1, J1.5, G1.1, G1.3, G1.4 -->

Reading alone: the membership argument assumes that intersecting adjacent configurations suffice across leadership changes. Different uncommitted configuration suffixes and rollback can leave several configurations in use, and a newly elected leader's volatile commit index is zero. A scenario with a partly replicated removal, a leadership change, an inherited or competing change, and a partition should probe both election and leader completeness across those configurations. This is a concern, not an established diagnosis; the implementation will retain immediate configuration adoption, rollback, and the local previous-configuration wait exactly as written. No claim of correctness follows from agreement with another artifact.

Reading alone: S6 appears unable to reach its final trigger. A four-member configuration split 2/2 has no majority of three, and the next action requires a new election before healing. The old leader retains one side; terms on the other side can grow without electing. Expect `UNEXPLAINED steps`, not PASS. No liveness property is being asserted.


## README section at first-version (983916c)
## Concerns after running

<!-- derives: J1.1, J1.3, J1.5, G1.1, G1.2, G1.3, G1.4 -->

No unmutated safety violation was witnessed in the 24 shared executions, either before or after the documented corrections. Twenty completed and passed; four did not complete their steps. Every one of the 24 mutation executions failed its predicted clause. These are mutation-sensitivity results and bounded samples, not a correctness argument for the design.

S6's three incomplete runs match the preregistered concern about waiting for an election in a 2/2 partition. S8 seed 2 contradicts the initial PASS prediction: self-removal followed by a request to the just-removed coordinator leaves the final success trigger unmet. Its result remains UNEXPLAINED steps. No shared outcome was changed to conceal an initial result; the original trace archive and run transcript remain available.

The reading-only concern about several configurations and leadership changes remains unresolved. None of the shared executions discriminated that concern. No formal-model output was read or used as an oracle. All code corrections are identified above with the relevant specification sentence and whether a probe informed them.

Verification passed after the corrections: independent contract-boundary fixtures, durable-vote and log-freshness probes, rollback and nonmember RPC probes, old-term commitment gating, duplicate catch-up responses, selectors in trigger filters, synchronous trigger arming, start-time crash semantics, and invalid selectors. Every saved execution replays byte for byte with the same seed. All 48 files passed causal/evidence auditing and standalone checking with the proper outcome. An unrelated filename and scenario label passed seeds 1–3 with the same normalized behavior. `go test -race -count=1 ./...`, `go vet ./...`, and `git diff --check` passed.


## Source of the configuration-change path (at first-version)
### impl/member.go lines 169-195
```
func (m *Member) maybeElected() {
	if m.Role == "candidate" && len(refList(m.Votes, m.Config)) >= majority(m.Config) {
		m.becomeLeader(false)
	}
}

// derives: J1.1, J1.5, G1.2 -- election initializes replication state; Elected records actual counted grants.
func (m *Member) becomeLeader(usurped bool) {
	m.Role = "leader"
	m.Leader = m.ID
	m.ElectionToken++
	m.HeartbeatToken++
	m.Next = map[string]int{}
	m.Match = map[string]int{}
	m.Acks = map[string]Ref{}
	for _, id := range []string{"m1", "m2", "m3", "m4", "m5"} {
		m.Next[id] = len(m.Store.Log) + 1
		m.Match[id] = 0
	}
	refs := refList(m.Votes, m.Config)
	m.emit("Elected", Record{"member": m.ID, "epoch": m.Store.Term, "config": canonical(m.Config), "voters": refs, "journal": copyEntries(m.Store.Log), "mutation_usurp": usurped}, refs...)
	m.broadcast()
	m.schedule(10, Input{Kind: "heartbeat", Token: m.HeartbeatToken})
}

// derives: J1.1, J1.5, G1.2, G1.4 -- higher terms always force follower state and clear the persisted vote.
func (m *Member) follower(term int, leader string) {
```
### impl/member.go lines 427-528
```
// derives: J1.3, J1.5, G1.4 -- Figure 4.1 RPC order: catch-up, prior config wait, append, commit, reply.
func (m *Member) change(op, target string) {
	r := m.emit("ChangeRequested", Record{"member": m.ID, "op": op, "target": target})
	p := &Request{Op: op, Target: target, Stage: "new", Ref: r}
	if m.Role != "leader" {
		m.reply(p, "not_leader")
		return
	}
	m.Pending = append(m.Pending, p)
	m.processRequests()
	m.broadcast()
}

// derives: J1.1, J1.3, J1.5, G1.1, G1.2, G1.4
func (m *Member) reply(p *Request, status string) {
	m.emit("ChangeReplied", Record{"member": m.ID, "op": p.Op, "target": p.Target, "status": status}, p.Ref)
}

// derives: J1.1, J1.3, J1.5, G1.1, G1.2, G1.4
func (m *Member) processRequests() {
	for m.Role == "leader" && len(m.Pending) > 0 {
		p := m.Pending[0]
		if p.Stage == "new" {
			if !validID(p.Target) || (p.Op == "add" && contains(m.Config, p.Target)) || (p.Op == "remove" && (!contains(m.Config, p.Target) || len(m.Config) == 1)) {
				m.reply(p, "invalid")
				m.Pending = m.Pending[1:]
				continue
			}
			if p.Op == "add" {
				p.Stage = "catchup"
				p.ProbeFloor = m.Probe + 1
				p.Goal = len(m.Store.Log)
				p.Progress = m.Match[p.Target]
				m.armCatchup(p)
				// A prior acknowledgement is evidence of an already matching log.
				if _, ok := m.Acks[p.Target]; ok && m.Match[p.Target] == len(m.Store.Log) {
					p.Stage = "wait"
				} else {
					m.replicate(p.Target)
					return
				}
			} else {
				p.Stage = "wait"
			}
		}
		if p.Stage == "catchup" {
			return
		}
		if p.Stage == "wait" {
			if m.ConfigIndex > m.Commit {
				return
			}
			next := []string{}
			for _, id := range m.Config {
				if p.Op != "remove" || id != p.Target {
					next = append(next, id)
				}
			}
			if p.Op == "add" {
				next = append(next, p.Target)
			}
			// derives: J1.3, G1.4 -- deliberately broken bulk edit changes a second identity in one journal entry.
			if m.Mutation == "S8" {
				for _, id := range []string{"m1", "m2", "m3", "m4", "m5"} {
					if id == p.Target {
						continue
					}
					if contains(next, id) {
						out := []string{}
						for _, v := range next {
							if v != id {
								out = append(out, v)
							}
						}
						next = out
					} else {
						next = append(next, id)
					}
					break
				}
			}
			next = canonical(next)
			m.appendLocal(Entry{Term: m.Store.Term, Kind: "config", Payload: configPayload(next), Config: next})
			p.Index = len(m.Store.Log)
			p.Stage = "commit"
			m.advanceCommit()
			m.broadcast()
			return
		}
		if p.Stage == "commit" {
			if p.Index > m.Commit {
				return
			}
			m.reply(p, "ok")
			m.Pending = m.Pending[1:]
			if !contains(m.Config, m.ID) {
				m.follower(m.Store.Term, "")
				return
			}
		}
	}
}
```
