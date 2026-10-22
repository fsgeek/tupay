# Hold-out scenarios H1 to H4: notes

Written from replay/contract.md (v3), replay/failure-model.md (v1), replay/scenario-format.md (v1), replay/observe.md (v1), replay/spec-F.md, replay/spec-D.md and replay/scenarios/S1 to S8 only. Nothing under docs/, experiments/ or tmp/ was read.

Each scenario was walked through spec-F by hand. For each, "the path" below is one execution of a design that follows spec-F exactly in which every trigger fires; the model side explores it among the others, the implementation side may or may not sample it.

## H1: coordinator dies mid-add, survivors change under the old configuration

**Targets.** The interaction of spec-F's "wait until the previous configuration entry in the coordinator's journal is committed" with a configuration entry that exists only on the dead coordinator (and m5). The survivors' journals have no configuration entry, so the initial configuration "counts as committed" and the removal proceeds at once. C1 = {m1..m5} (majority 3) and C2 = {m1,m2,m3} (majority 2) differ by two members, so {m1,m4,m5} and {m2,m3} are disjoint majorities.

**The path.** L1 appends C1 at index 1, sends it to m5, crashes. m2 is elected in e2 by m3, m4 under the initial configuration, appends C2 = initial − m4 at index 1, commits it with m3, replies ok, and stops sending to m4. L1 restarts with [C1@e1]. m5, orphaned with C1, times out and sends ballots to m1..m4 in e3; m4 (journal empty, never told of C2) grants; m1 grants if m5's ballot reaches it before m2's extend request does (G1.2 lets it). m5 counts itself: three of five. Elected(m5, e3, C1) without C2 at index 1, which m2 committed in e2. That is a J1.5(a) violation produced by a design that follows spec-F exactly. This is the gap Ongaro reported in 2015 against the single-server change as published; the fix (a new coordinator appends and commits an entry of its own epoch before any change) is not in spec-F.

**Expected mishandling.** A faithful artifact should FAIL J1.5 here. An artifact that PASSes has either added a no-op-on-election or a "current-epoch commit before change" rule the specification does not contain, or does not let m5 campaign under C1 (for example, m5 derives its configuration from somewhere other than its journal, or a removed/orphaned member is silenced), or its election counts a majority of the initial configuration rather than of the candidate's own. Also possible: an artifact's model never reaches the path because its bound on epochs is too small for e3 and the disruptions m4 and m5 cause. If m5 is the survivor elected in step 3, it has an uncommitted C1 from e1, cannot commit it without a command of its own epoch, and never answers the removal: that run is UNEXPLAINED steps, which is itself a fact about the design.

**P(at least one of four artifacts mishandles it)**: 0.55 that at least one artifact PASSes when it should FAIL, or reports a FAIL for the wrong reason (for example J1.1), or returns UNEXPLAINED on every seed because the crash is never sampled before C1 replicates.

## H2: configuration entry truncated under a member, which must fall back

**Targets.** Spec-F's one sentence "If entries it deleted included a configuration entry, its configuration falls back to the latest configuration entry that remains", combined with a second change so that the stale configuration and the real one differ by two members. S-scenarios never truncate a configuration entry.

**The path.** L1 appends C1 = initial + m5 at index 1 and is cut from m1..m4 (it keeps m5, which it heartbeats, so m5 stays quiet). m2 is elected in e2 by all three survivors, appends c1 at index 1, commits it with all three (it needs all three: three of four, and L1 is cut). m2 removes m4: C2 = {m1,m2,m3} at index 2, committed with m3; m4 is not sent C2. Heal. m2's extend to L1 has prevIndex 0 and overwrites C1 with c1: Truncated(L1, 1), and L1's configuration must become the initial one. m5 is orphaned with C1 and campaigns with ever higher epochs, deposing m2 repeatedly; each deposition opens an election in which L1 may be the first to time out. Correct: L1 campaigns under the initial configuration, gets m4 (equal journals) but not m2 or m3 (longer), two of four, not elected. Buggy fallback (L1 keeps C1): L1 sends ballots to m2..m5, gets m4 and m5, three of five, Elected(L1, e, C1) without C2 at index 2, which m2 committed. J1.5(a).

**Expected mishandling.** Implementations that keep a cached `config` field updated only on append (common: `if entry.kind == config { r.config = entry.payload }` in the append path and nothing in the truncate path). Models that define the configuration as a variable rather than a function of the journal. Also, an implementation that sends c1 and C2 in one extend request after healing never shows the stale window; that is a legitimate PASS, not a mishandling. If the coordinator elected in step 3 is m5 (possible in the model), c1 goes to index 2 and the removal is on C1; the path is different but every trigger still fires.

**P**: 0.45.

## H3: heartbeat carries a commit index past a stale entry

**Targets.** The receiver rule "sets its commitIndex to the smaller of the coordinator's commitIndex and the index of the last entry the request carried (prevIndex plus the number of entries sent)" when the request carries no entries. The conventional slip is `min(leaderCommit, lastIndex of own journal)` or, as in the published raft.tla "already done with request" branch, `commitIndex := leaderCommit` with no bound at all. Either marks a stale uncommitted entry committed on the receiver; the next extend request then deletes it, violating J1.5(b) on that member.

**The path.** Five members after the add (C1 at 1, c1 at 2 committed). L1 appends c2 at index 3 and crashes with c2 on at most one follower F. Among the four survivors, any three without c2 elect one of them (F refuses, it is longer; it does not matter). L2 appends c3 at index 3 and commits it with the other two. L1 restarts with [C1, c1, c2@e1] and commitIndex 0. L2's nextIndex for L1 (and F) is 3, so its requests carry prevIndex 2, prevEpoch 1, which matches. An empty heartbeat with commitIndex 3 arrives (G1.2 reordering or just the timer) before the request carrying c3. Correct: commitIndex := min(3, 2 + 0) = 2. Wrong: 3, with c2 at index 3; Committed(L1, 3) is recorded; the next request deletes index 3: Truncated(L1, 3) at or below commitIndex. The same happens to F without any restart, so the scenario has two chances.

**Expected mishandling.** Any model copied from memory of raft.tla; any implementation whose heartbeat path is separate from the entries path and clamps to its own last index. Implementations that always send entries from nextIndex and never send a bare heartbeat while entries are pending cannot show it; that is a legitimate PASS. Observability risk: an artifact that records Committed only on the coordinator will still violate the state property if its checker looks at every member's commitIndex, and will silently PASS if the checker only looks at the coordinator's.

**P**: 0.50.

## H4: requests at the wrong member, then changes that change nothing

**Targets.** G1.4's retry-at-another-member, the "not coordinator" reply path, and the contract's claim that J1.3 "holds by construction if the specification is followed". Spec-F says a change appends "the current configuration plus the new member" and "without the removed member"; it says nothing about a member already present or already absent. Following it literally appends an entry equal to its predecessor, which differs by zero members: J1.3 FAIL.

**The path.** Trivial: add at a follower (reply "not coordinator"), retry at the coordinator (ok), add m5 again (catch-up immediate, previous configuration committed, append C1 again), remove m5 (ok), remove m5 again.

**Expected mishandling.** Artifacts that follow spec-F literally FAIL J1.3 at step 3 (which is the interesting result: the contract's by-construction claim does not survive G1.4). Artifacts that reject the duplicate with a status, or answer ok without appending, PASS. Artifacts that neither reply nor append hang the scenario: UNEXPLAINED steps. Artifacts whose runner does not implement the `follower` selector or the non-ok ChangeReplied statuses also show up here. A model that fixes the configuration-change request set to "one add of m5, one remove" cannot express the duplicate and will reject the scenario.

**P**: 0.70 that at least one artifact does not PASS (mostly a J1.3 FAIL on a literal reading, which the steward should treat as a finding about spec-F and the contract, not about the author).

## Selector caveats common to all four

- `coordinator` and `crashed` are resolved when the trigger fires; in H1 and H3 the old coordinator is reached through `crashed` after its restart, which is the only handle the format offers for it.
- Removal targets are fixed names (m4, m5), so the model will also explore executions where the coordinator removes itself; those executions are valid under spec-F ("steps down after the entry is committed") but are not the targeted path.
- `{event: Committed, index: N}` triggers assume a Committed record is emitted per entry index, as the contract's per-entry definition implies; an artifact that records only the commit-index jump may leave H3 step 6 unfired on the path where the stale-entry holder is elected.
