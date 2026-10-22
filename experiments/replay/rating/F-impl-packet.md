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
## README sections as committed before the first run (commit e22ce41)
## Choices

<!-- derives: J1.1, J1.3, J1.5, G1.1, G1.2, G1.3, G1.4 -->

* Use five member goroutines, each owning its state. A logical scheduler releases
  one mailbox operation at a time and waits for completion. Members communicate
  only through queued messages. This supplies actual concurrent processes with a
  reproducible interleaving, independent of OS scheduling and wall time.
* Seed an isolated PRNG per run. Election timeouts are uniform integer ticks in
  [24, 44], heartbeat interval 6, network delay [1, 4], independent random loss
  probability 1/100 and duplication probability 1/50. Cut/drop links lose sends;
  messages already in flight remain deliverable. Administrative actions run
  1--3 ticks after their triggers. All choices, including tie ordering, use this
  PRNG or a fixed sorted member order. Crash/restart does not reseed it.
* Count every recorded event, including scheduler deliveries/timer firings and
  evidence records, against the event bound and settling count. These auxiliary
  records make quiescent/partitioned runs bounded even without contract events.
  Finish an atomic mailbox operation even if its emitted records cross a bound;
  check every record for safety. Event bounds apply between mailbox operations.
* Persist epoch, vote and journal as JSON via atomic rename under repository
  `tmp/`, before a mailbox operation releases any reply for delivery. Restart
  reads only those fields; volatile role, commit index, replication state,
  pending administrative requests and timers are reset. Observation counters
  are external instrumentation and survive process restart.
* Replicate the entire suffix starting at nextIndex. Initialize nextIndex to
  lastIndex+1 and matchIndex to zero, including newly contacted peers. On a
  failure decrement nextIndex, bounded below by 1; on success set it to the
  request's last index+1 exactly, even for reordered replies. Retry on heartbeat
  ticks, and immediately after failures and new appends. No election no-op.
* All five members run election timers, including those outside their current
  configuration. Count the candidate's own ballot only if it belongs to that
  configuration. Process incoming requests without membership checks. A same
  epoch extend makes a candidate a follower. Reject lower epoch requests with
  an epoch-bearing negative reply. A higher epoch in any message resets role
  and vote before processing. Timers reset on granted ballots and accepted-epoch
  extend requests, including requests failing the previous-entry check.
* Handle administrator requests in a FIFO per coordinator. An add catches up
  via three rounds (a round completes on a successful extension acknowledgement);
  an acknowledgement matching the current full journal completes catch-up at
  once. Contact an add target before membership using the same extension logic.
  Abort catch-up on a full election-timeout interval without progress or on an
  overlong final round. Wait for the latest configuration to commit before
  appending each change. Reply ok only after that entry commits. Abandon pending
  work on loss of leadership or crash; an administrator can retry. Invalid
  duplicate adds/removes receive `invalid`; a pending request is revalidated
  against the current configuration before it appends. Commands at followers
  are ignored. A self-removing leader steps down after commitment.
* Record each contract event with per-process sequence, causal links and run id.
  BallotGranted and Acknowledged auxiliary records provide real evidence refs.
  Election records include the journal and counted ballot evidence; commitment
  records include the configuration, journal and counted acknowledgement
  evidence. This supplements the contract fields to answer the observability
  question. Configuration effects are recorded on append and truncation.
* Implement an independent streaming checker consuming JSONL, reconstructing
  each journal, configuration and local commit index (including restart resets).
  J1.1 checks coordinator identity across each epoch over the whole run. J1.3
  compares each appended configuration with its journal predecessor or initial
  configuration. J1.5 checks all entries newly covered by commitment against
  every later higher-epoch election and checks truncation against the removing
  member's current commit index. Report the first witnessed violated clause.
* Accept any scenario path and any name. Select mutations only by an explicit
  flag, never implicitly from a scenario's name. The mutations batch associates
  each shared input with its preregistered flag. Validate input shape and reject
  unresolved selectors. Keep traces under impl/observe; generated binaries and
  durable state under ignored tmp/. Use only Go's standard library and yaml.v3.

## Concerns

<!-- derives: J1.1, J1.3, J1.5, G1.1, G1.2, G1.3, G1.4 -->

1. The specification's justification for single-member changes concerns one
   adjacent pair of configurations. It does not prove safety for a sequence of
   configurations combined with early activation and stale coordinators. A
   scenario could partition a coordinator, change membership elsewhere, then
   let a stale member campaign against members with newer configurations.
   Implement early activation and outsider request processing exactly as written.
2. Lost volatile commitIndex on restart allows a member to overwrite something
   previously known committed; J1.5(b) is about its current commit index, while
   J1.5(a) still constrains future elections. Do not persist commitIndex as a fix.
3. Reordered success replies can regress matchIndex, and failure replies can
   regress nextIndex. Implement the assignments as written, not monotonic fixes.
4. A two-by-two partition of a four-member configuration need not elect anybody.
   S6's heal waits for Elected, so it is likely to exhaust its bound: no liveness
   requirement licenses calling an unreached step PASS.
5. A removed member keeps campaigning and can vote or accept extensions from
   outsiders. Do not add a membership admission guard. Zero-member configurations
   have no possible majority. The brief prescribes no nonempty check.


## README section at first-version (2fb8f5d)
## Concerns after running

<!-- derives: J1.1, J1.3, J1.5, G1.1, G1.2, G1.3, G1.4 -->

No unmutated shared run witnessed a contract failure. All predictions matched
for seeds 1, 2 and 3, including all 24 deliberately broken runs. See
[the complete report](report.md) for predictions beside every result and trace
links. All 48 shared results and trace bytes matched on repetition, and matched
again after the documented empty-initial parser clarification. No protocol
change was made in response to a shared result.

S6 exhausted exactly 400 records having taken two of three actions in each seed.
The final action, heal, was waiting for a new Elected event. In seed 2 m1 led the
initial four-voter configuration and the partition split those voters into two
pairs. In seeds 1 and 3 m5 was elected while outside the initial configuration;
it remained connected to all four voters across S6's cut. None of the three
runs emitted a later Elected event. The outcome remains UNEXPLAINED steps,
without a liveness or correctness conclusion.

The outsider election is a direct consequence of the specification's "a
follower or candidate whose timer expires" and its rule that receivers process
requests without consulting membership. It also occurs in S1--S5, S7 and S8
for seeds 1 and 3. Do not infer that every named scenario exercised the topology
its author may have had in mind. The unresolved concern about successive
configuration transitions remains; these bounded samples do not discriminate
it. No formal-model artifact was read or compared, and this repository's
mutation results supply only the implementation half of cross-family evidence.

Checker fixtures distinguish forbidden committed truncation and missing
higher-epoch entries from permitted stale-follower truncation and post-restart
commit-index reset. Vet and race-enabled tests passed. An unfamiliar scenario
name passed all three seeds with the same process-event content as S3 after
normalizing only the run id. Explicit empty-initial runs passed all three seeds;
a missing initial field was rejected as preregistered.


## Source of the configuration-change path (at first-version)
### impl/member.go lines 212-234
```
func (n *Member) becomeCoordinator() {
	n.Role = "coordinator"
	n.Next = map[string]int{}
	n.Match = map[string]int{}
	n.Ack = map[string]Ref{}
	for _, m := range names {
		n.Next[m] = len(n.D.Journal) + 1
		n.Match[m] = 0
	}
	counted := []Counted{}
	causes := []Ref{}
	for _, m := range n.config() {
		if ref, ok := n.Votes[m]; ok {
			counted = append(counted, Counted{m, ref})
			causes = append(causes, ref)
		}
	}
	n.E.emit(n.Name, "Elected", Record{"epoch": n.D.Epoch, "config": n.config(), "evidence": n.evidence(counted)}, causes...)
	n.HeartbeatGeneration++
	n.broadcast()
	n.E.timer(n.Name, "heartbeat", n.HeartbeatGeneration, 6)
}

```
### impl/member.go lines 460-554
```
// derives: J1.1, J1.3, J1.5, G1.1, G1.2, G1.3, G1.4
func (n *Member) driveChange() {
	if n.Role != "coordinator" || len(n.Changes) == 0 {
		return
	}
	c := n.Changes[0]
	if c.Stage == "committing" {
		if n.Commit < c.Index {
			return
		}
		selfRemoved := c.Op == "remove" && c.Target == n.Name
		n.reply(c.Op, c.Target, "ok")
		n.Changes = n.Changes[1:]
		if selfRemoved {
			n.follower(n.D.Epoch)
			return
		}
		n.driveChange()
		return
	}
	if c.Stage == "" {
		present := contains(n.config(), c.Target)
		if (c.Op == "add" && present) || (c.Op == "remove" && !present) {
			n.reply(c.Op, c.Target, "invalid")
			n.Changes = n.Changes[1:]
			n.driveChange()
			return
		}
		if c.Op == "add" && c.Target != n.Name {
			c.Stage = "catchup"
			c.LastProgress = n.E.Now
			c.RoundStart = n.E.Now
			c.Interval = n.Interval
			n.Next[c.Target] = len(n.D.Journal) + 1
			n.Match[c.Target] = 0
			n.sendExtend(c.Target)
			return
		}
		c.Stage = "waiting"
	}
	if c.Stage == "catchup" {
		if n.E.Now-c.LastProgress >= c.Interval || (c.Rounds >= 2 && n.E.Now-c.RoundStart > c.Interval) {
			n.reply(c.Op, c.Target, "timeout")
			n.Changes = n.Changes[1:]
			n.driveChange()
		}
		return
	}
	if n.configIndex() > n.Commit {
		return
	}
	config := n.config()
	present := contains(config, c.Target)
	if (c.Op == "add" && present) || (c.Op == "remove" && !present) {
		n.reply(c.Op, c.Target, "invalid")
		n.Changes = n.Changes[1:]
		n.driveChange()
		return
	}
	if c.Op == "add" {
		config = append(config, c.Target)
	} else {
		next := []string{}
		for _, m := range config {
			if m != c.Target {
				next = append(next, m)
			}
		}
		config = next
	}
	if n.E.Mutation == "S8" {
		for _, m := range names {
			if m != c.Target {
				if contains(config, m) {
					next := []string{}
					for _, v := range config {
						if v != m {
							next = append(next, v)
						}
					}
					config = next
				} else {
					config = append(config, m)
				}
				break
			}
		}
	}
	sort.Strings(config)
	c.Stage = "committing"
	c.Index = len(n.D.Journal) + 1
	n.append(Entry{Epoch: n.D.Epoch, Kind: "config", Config: config})
	n.advanceCommit()
	n.broadcast()
}
```
