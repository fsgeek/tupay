# Reference model and scenario driver for the replay inputs (validation tool)

This is a steward's validation tool, not an experimental artifact. It checks that the replay inputs
(`replay/spec-F.md`, `replay/contract.md` v2, `replay/failure-model.md`, `replay/scenario-format.md`,
`replay/observe.md`, `replay/scenarios/S1..S8.yaml`, withheld `tmp/replay/K1v3.yaml`) are executable and
mean what they say. Nothing here is scored or compared with an author's work.
derives: J1.1, J1.3, J1.4, G1.1, G1.2, G1.3, G1.4

## Files
- `tla/F.tla`: the model, in TLA+. It covers spec F, the SPEC and GATED variants, the scenario driver and the
  checkers. This file is the readable statement of the model. `tla/F_v1_unreduced.tla` is the first version
  (replies as separate messages); it was too slow to use and is kept only for the record.
- `fexp/` (Rust, std only): the same transition system as `F.tla`, run as a parallel explicit-state DFS with
  a shared lock-free 64-bit fingerprint table. It does about 1.5 to 2.5M states/s, where TLC on `F.tla`
  managed about 15k states/s. Build it with `cargo build --release`.
- `run.py`: the front end. It compiles a scenario YAML into either engine's input (`--engine fexp|tlc`),
  runs it under the mandatory cap (`systemd-run --user --scope -q -p MemoryMax=24G -p MemorySwapMax=0`),
  and reports `PASS`, `FAIL <clause>` with a trace, `UNEXPLAINED steps` or `UNEXPLAINED bound`.
- `run_all.py`: runs every scenario against both variants with a ladder of bounds (see below) and prints the
  table. Results are in `results/*.json`, logs in `logs/`, per-run inputs and outputs in `runs/`.
- `explorer.py`, `pexplore.py`, `logs/probe_K1_SPEC.log`: the earlier uncapped attempt, left as found.
  They were read, not used.

## Cross-check of the two engines
On every configuration TLC could exhaust, `fexp --noprune` (unbounded reply loss, timeouts not split)
reports exactly TLC's distinct-state count for `F.tla`:

| scenario | variant | E,T,J,settle | TLC distinct | fexp distinct |
|---|---|---|---|---|
| K1v3 | SPEC | 1,1,3,2 | 7,641 | 7,641 |
| S3 | SPEC / GATED | 1,1,3/4,2 | 67,051 / 631,826 | 67,051 / 631,826 |
| S5 | SPEC / GATED | 1,1,3/4,2 | 71,929 / 884,464 | 71,929 / 884,464 (rechecked after the final build) |
| S8 | SPEC / GATED | 1,1,3/4,2 | 33,678 / 424,513 | 33,678 / 424,513 |

The pruning, the reply-loss budget and the timeout split described below exist only in `fexp`. Each of them
only removes behaviours, and each is stated as a bound.


## The model
It is spec F as written, with five members m1..m5. All five start with the scenario's initial configuration and
an empty journal; non-members time out, vote and can be elected exactly like members, because the spec says
requests are processed without consulting configuration. Durable state is epoch, votedFor and journal.
A crash resets role, commitIndex, nextIndex/matchIndex, ballots and any pending change. Crash, restart, cut,
drop, heal, add, remove and command happen only as scenario steps. Everything else is free nondeterminism:
- a follower or candidate times out at any time; a coordinator never does;
- any in-flight request is delivered at any later point, any number of times, or never;
- the coordinator's local progress on a change happens at any later point.

**Variants.**
- SPEC is `Gated = FALSE`.
- GATED is identical except for two things. On election a coordinator appends one `noop` command entry.
  `Proceed` will not append a configuration entry until some entry at an index ≤ its commitIndex
  carries its own epoch. Nothing else differs (`grep Gated tla/F.tla`).

**Checkers** (contract v2; ghost state, monotone):
- J1.1: two `Elected` in the same epoch by different members.
- J1.4(a): every election is recorded with the journal held at election. Every commitment by a coordinator
  in epoch e is recorded as (index, entry, e), counting the indirect commitment of every earlier index.
  It is a violation if some election in an epoch above e lacks that entry at that index, whichever happened first.
- J1.4(b): a member removes (truncates or overwrites) an entry at an index where that entry has been
  committed, at the moment of removal.
- J1.3: every configuration entry is compared with the preceding configuration in the same journal
  (or the initial one); the flag is sticky.
- A FAIL is a violation in a behaviour that has taken every step (the violating state is a prefix of it).
  Violations in behaviours that had not yet taken every step are reported as notes with their trace.
- Diagnostic only, never a FAIL by default: J1.4(b'), a member removes an entry at an index at or below its
  own commitIndex.

**Scenario driver** (format rules):
- Step 1 is armed at the start. Step i is armed when step i−1's action is taken, and the action's own
  synchronous events are matched against step i.
- A trigger matches the first event of a transition that has every filter field with an equal value.
- Selectors are resolved when the trigger fires: `coordinator` is the member most recently `Elected`;
  `follower` branches over every up member that is not the coordinator; `crashed` is the target of the
  most recent crash step. A scenario that uses `coordinator` before any Elected, or `crashed` before any crash
  step, is rejected.
- The fired action is taken at any later transition.
- Cuts and drops accumulate until `heal`; self-pairs are ignored.
- `settle`: after the last action, a transition may be taken only if the events since that action (not
  counting its own) stay ≤ N.
- PASS needs at least one behaviour that takes every step, and an exhaustive search with no FAIL.
- `UNEXPLAINED steps` means the space was exhausted and no behaviour took every step.
- `UNEXPLAINED bound` means the wall-clock limit or the fingerprint table stopped the search first.

## Abstractions (each cannot add behaviours; each is chosen so that it cannot remove a J1.1/J1.3/J1.4 violation, or is stated as a bound)
1. **Replies are processed atomically with the request's delivery, or lost** (two transitions). Requests
   keep full loss, delay, reordering and duplication. Delay of a reply alone is not modelled: a reply
   that arrives late is a request delivered later, or a reply lost and the request re-delivered.
2. **Eager sending with retries.** Whenever a coordinator's record changes, it sends its current extend
   request to every target. A candidate sends ballot requests at timeout. Either one re-sends (`retry`)
   whenever its current request is not in flight, which covers sends lost on a down link. An extend request
   carries every entry from nextIndex to the end. Heartbeats are these requests with no entries.
3. **Dead requests are removed.** A request is removed once delivering it could change nothing, and the
   sender's retry re-creates anything it could change later:
   - a stale request whose sender's epoch is not below the receiver's;
   - a ballot request of the receiver's epoch from a sender that is no longer candidate of that epoch.
     A vote for it only makes the receiver refuse others, and not delivering the other candidate's request
     reproduces that;
   - a ballot request whose receiver voted for someone else, or whose grant was already counted;
   - an extend request whose entries and commit index the receiver already holds, and whose success reply
     could not raise the sender's matchIndex or nextIndex.
4. **matchIndex and nextIndex take the max on success.** The spec sets them to the reply's last index; with
   reordered or duplicated replies that can move them backwards. Lowering matchIndex only delays commitment.
5. **Catch-up** for add is not counted in rounds:
   - if the new member's journal equals the coordinator's when the request arrives, catch-up is complete at once;
   - otherwise it completes when the coordinator's matchIndex for it reaches the coordinator's last index;
   - at any time during catch-up the coordinator may reply `timeout` (the timer).
6. **Fingerprints** are 64-bit: collision probability about n²/2⁶⁵, about 0.4% at 360M states. Collisions can
   only hide states, never invent a FAIL; every reported trace is re-derived step by step.

## Bounds
- E: highest epoch.
- T: election timeouts in all.
- T_pre: timeouts before every step is taken; after that, T − T_pre more.
- J: journal length. It is set to the entries the steps append, plus one no-op per needed election plus one
  spare for GATED (K1v3 GATED: J = 5).
- lost: deliverable replies that may be lost. Replies lost because the reverse link is down or the sender
  is down are not counted.
- settle: 2 contract events after the last action, against the scenario's 100.
- The scenario's `bound: {events: 400}` is not used as a cut-off, because the bounds above make the space
  finite. Every reported trace is far below 400 events; the K1v3 FAIL trace has 16.
- Prefixes from which the remaining `Elected` triggers cannot all fire are pruned. Each needs an election,
  and an election needs a timeout left under T_pre or a current candidate. The format does not explore
  such prefixes.

`run_all.py` tries a ladder for each scenario and variant (k = the scenario's Elected triggers):
1. (T=k+2, T_pre=k+1, lost=1), only when k+2 ≤ 3, with a 180 s limit
2. (T=k+1, T_pre=k, lost=1)
3. the same with lost=0
4. (T=k, T_pre=k, lost=0)

The first attempt that exhausts or FAILs is the reported result. The other rungs have a 300 s limit. Every
attempt runs on 64 threads with a 2³¹-slot table.

## Results

| scenario | variant | outcome | E | T | T_pre | J | lost | settle | distinct states | exhausted | s | earlier attempts (UNEXPLAINED bound) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | SPEC | PASS | 3 | 3 | 2 | 1 | 1 | 2 | 32,656,628 | yes | 23 | none |
| S1 | GATED | PASS | 3 | 2 | 2 | 4 | 0 | 2 | 124,032,049 | yes | 56 | T=3,T_pre=2,lost=1: 683,317,319 states in 309s; T=3,T_pre=2,lost=0: 694,175,721 states in 309s |
| S2 | SPEC | PASS | 3 | 3 | 2 | 0 | 1 | 2 | 463,940 | yes | 10 | none |
| S2 | GATED | PASS | 3 | 3 | 2 | 3 | 1 | 2 | 108,429,616 | yes | 54 | none |
| S3 | SPEC | PASS | 3 | 2 | 1 | 2 | 1 | 2 | 5,707,089 | yes | 12 | T=3,T_pre=2,lost=1: 379,363,758 states in 189s |
| S3 | GATED | PASS | 3 | 2 | 1 | 4 | 1 | 2 | 21,921,380 | yes | 19 | T=3,T_pre=2,lost=1: 383,483,853 states in 189s |
| S4 | SPEC | PASS | 3 | 2 | 1 | 2 | 0 | 2 | 218,225,995 | yes | 100 | T=3,T_pre=2,lost=1: 436,765,824 states in 189s; T=2,T_pre=1,lost=1: 597,551,786 states in 309s |
| S4 | GATED | PASS | 3 | 1 | 1 | 4 | 0 | 2 | 162,898,529 | yes | 72 | T=3,T_pre=2,lost=1: 401,544,908 states in 189s; T=2,T_pre=1,lost=1: 607,071,576 states in 308s; T=2,T_pre=1,lost=0: 593,073,184 states in 309s |
| S5 | SPEC | PASS | 3 | 2 | 1 | 1 | 1 | 2 | 5,642,318 | yes | 12 | T=3,T_pre=2,lost=1: 380,688,625 states in 188s |
| S5 | GATED | PASS | 3 | 2 | 1 | 3 | 1 | 2 | 26,011,573 | yes | 19 | T=3,T_pre=2,lost=1: 443,109,642 states in 189s |
| S6 | SPEC | PASS | 3 | 3 | 2 | 1 | 1 | 2 | 29,164,888 | yes | 22 | none |
| S6 | GATED | PASS | 3 | 3 | 2 | 4 | 0 | 2 | 356,499,086 | yes | 180 | T=3,T_pre=2,lost=1: 606,317,739 states in 309s |
| S7 | SPEC | PASS | 3 | 3 | 2 | 2 | 1 | 2 | 11,085,880 | yes | 14 | none |
| S7 | GATED | PASS | 3 | 3 | 2 | 4 | 1 | 2 | 139,561,397 | yes | 78 | none |
| S8 | SPEC | PASS | 3 | 3 | 2 | 3 | 1 | 2 | 76,066,560 | yes | 41 | none |
| S8 | GATED | PASS | 3 | 2 | 1 | 5 | 1 | 2 | 8,605,697 | yes | 13 | T=3,T_pre=2,lost=1: 429,403,468 states in 189s |
| K1v3 | SPEC | FAIL J1.4(a) | 3 | 3 | 2 | 2 | 1 | 2 | 4,989 | no (stopped at FAIL) | 9 | none |
| K1v3 | GATED | PASS | 3 | 3 | 2 | 5 | 0 | 2 | 227,532,361 | yes | 145 | T=3,T_pre=2,lost=1: 476,755,973 states in 308s |

Supplementary runs (same model):
- K1v3 GATED with J=3, T=3, T_pre=2, lost=1: PASS, exhausted, 242,794,882 states in 202 s.
- The same with lost=0: PASS, 51,762,752 states.
- With T=3 unsplit: not exhausted (about 1.07B states with lost=0 in 413 s; about 0.97B with unbounded loss
  in 553 s), so the timeout split is needed for K1v3 GATED.
- S1 and S2 SPEC also PASS with T=3 unsplit and unbounded reply loss (151,794,429 and 3,498,269 states).
- S2 GATED with only J1.4(b) as the FAIL clause, T=3 unsplit, lost=1: no J1.4(b) witness in 680,511,064
  states (not exhausted).

**Required outcome: holds, within the bounds above.**
- Both variants take every step of S1..S8 with no clause witnessed. No note was raised in any run of the table.
- SPEC FAILs K1v3 on J1.4(a).
- GATED PASSes K1v3 exhaustively. 223,483,549 of its 227,532,361 states (98%) are past the last step,
  which is where m1's re-election attempt is explored.

Bounds are weakest for S4 GATED (T=1: only the one election the step needs) and S1 GATED (T=2: no timeout
after the last step).

**K1v3 SPEC witness** (`results/K1v3_SPEC_0.json`, 24 transitions, 16 events), condensed:
1. m1 is elected in e1 under C0 ({m1..m4}); step 1 fires.
2. `add m5 at m1`: journals match (both empty), and there is no previous configuration entry. m1 appends
   C1 = {m1..m5} and sends it to all four.
3. m1 steps down to e2 on m2's ballot reply. Cut m1 from m2..m4. m5 receives C1 (step 3), then the m3–m4 cut.
4. m2 is elected in e2 with m3 and m4 under C0, having no configuration entry (step 4).
5. `remove m4 at m2`: no previous configuration entry, so m2 appends C2 = {m1,m2,m3} at index 1. m3 acks;
   m2 commits index 1 in e2 (majority of C2) and replies ok. Step 5: heal.
6. m1 times out to e3 and asks C1. m4 (empty journal) and m5 (C1 only) grant. m1 is elected in e3 by
   {m1,m4,m5}, 3 of 5 under C1, holding e1:C1 at index 1 and not the committed e2:C2. J1.4(a) is violated.
   Extend requests from m1 would then overwrite C2 on m2 and m3, which is J1.4(b).

GATED blocks this: m2 must first commit its e2 no-op with three C0 members (m2, m3, m4). m4's last entry is
then (e2), and it refuses m1, whose last is (e1).

## Findings about the inputs
**F1. J1.4(b) as written is violated by a correct protocol (GATED), not only by the defect.** Witness:
`results/K1v3_GATED_J14b_literal_witness_unsplit_bounds.txt` (GATED, T=3 unsplit, unbounded reply loss,
no pruning). It is a behaviour that had not yet taken every step, so it is not a FAIL under the format:
- m5, a non-member, is elected in e1 and appends e1:noop at index 1.
- m1 is elected in e2, holding no entry.
- m3, which got e1:noop from m5, is elected in e3, replicates it to m2 and m4, and commits index 1 in e3.
- m5, still in e2 and never told index 1 is committed, accepts the stale e2 coordinator m1's extend
  request and overwrites the committed e1:noop at index 1.

The same pattern needs no non-member. The author of an entry lags in epoch; a later coordinator commits the
entry; an intermediate-epoch coordinator overwrites the author's copy. This is the same over-reach that
retired J1.2. A reading that holds for GATED is J1.4(b'): no member removes an entry at or below its own
commitIndex. No run in the table witnessed J1.4(b) or J1.4(b'). It is still a hazard: a longer run, or an
implementation sampled over seeds, could report `FAIL J1.4` on GATED or on a correct implementation for this
reason alone. The steward should decide on the wording before authors start.

**F2. K1v3 depends on one silent point of spec F.** Add step 3 and remove step 2 ("wait until the previous
configuration entry is committed") say nothing about a coordinator whose journal has no configuration
entry. The model treats the initial configuration as committed. Under the other reading m2 could not remove m4
until it committed something of its own, which K1v3 never provides in SPEC.

**F3. GATED's no-op is a `command` entry.** `{event: Appended, kind: command}` (S4 step 2) can therefore fire
on a follower appending the no-op, before c1 replicates. That is correct under the format, but S4 then
exercises something different in GATED than in SPEC.

**F4. K1v3's comment** says C2 is "never sent to m4". That holds in SPEC. In GATED m4 must hold m2's no-op,
and that no-op is what prevents the counterexample.

## Ambiguities and how they were resolved (none changes an input file)
1. No previous configuration entry: treated as committed (F2).
2. A change requested while another is pending: reply `busy`. An add of a present member or a remove of an
   absent one: reply `invalid`, nothing appended. A request at a crashed member is lost, with no event. A
   coordinator that crashes or steps down with a pending change sends no reply.
3. Catch-up rounds and the "fixed number of rounds" are abstracted (abstraction 5).
4. A coordinator that receives an extend request of its own epoch ignores it; this is reachable only after a
   J1.1 violation. A candidate steps down only on an extend request of an epoch ≥ its own, as written.
5. GATED's gate is applied where the configuration entry is appended (after catch-up), not when the request
   is accepted.
6. Format, settle: the last action's own events are not counted. Transitions with no contract event
   (deliveries without effect, retries, timeouts) do not count, so settle bounds events, not time. A
   transition that would carry the count past N is not taken.
7. Format, cut: requests already in flight on a link when it is cut are held, and become deliverable after
   heal. The format only says messages *sent* while a link is down are lost.
8. Format, selectors: `follower` includes non-members and candidates. `coordinator` is the most recently
   `Elected` member even if it has since crashed or been deposed.
9. Contract, events: one `Committed` per newly covered index, on every member that learns it, so a
   `{event: Committed}` trigger can fire on a follower. `Elected.config` is the configuration in effect at
   election.
10. Contract, J1.4: "commits the entry at index i in epoch e" is taken as the committing coordinator's epoch,
    and includes indirect commitment.
11. Contract, J1.4(b): checked only for removals at or after commitment (removal before commitment is not a
    violation). See F1.
12. matchIndex moving backwards under reordering, as literally specified, is replaced by max (abstraction 4).

## Resource use
Every run went through the mandatory cap. The explorer preallocates its fingerprint table (2³¹ slots, 16 GiB).
Peak RSS of the largest run was 16.9 GB (16,870,408 kB, K1v3 GATED with unbounded reply loss), and 16.0 GB for
every run in the table. TLC runs peaked at 4.6 GB. No run was killed by the cap.

## Reproduce
```
cd tmp/replay/reference/fexp && cargo build --release && cd ..
/usr/bin/python3 run_all.py            # whole table, about 75 min
/usr/bin/python3 run.py ../K1v3.yaml SPEC --maxe 3 --maxt 3 --maxtpre 2 --maxlost 1 --settle 2 --bits 31
/usr/bin/python3 run.py ../../../replay/scenarios/S5.yaml SPEC --engine tlc --maxe 1 --maxt 1 --maxj 3 --settle 2 --modes safety   # TLC cross-check
```
