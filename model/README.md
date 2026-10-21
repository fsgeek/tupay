# tupay model (TLA+), v2 round (schedule format v2, shared schedules, P10 fix)

derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3; format v2 T1, T2, T3, A1, A2, E1, E2

Round 2 adds three things: the format v2 adaptation, the P10 fix, and a re-placed P11 mutation.
They are described in the "Round 2" section below. Everything after that section is the round-1 text, with each change marked **[v2]**.
The round-2 predictions and their outcome are in `PREDICTIONS-v2.md`.

## Round 2
### Changes for format v2
- **Schedule resolution.** `run.sh <name>` resolves only `testbed/schedules/<name>.yaml`. `model/schedules/` is M1 history and is never run.
  The v1 alias `false-suspicion` is gone: use `false-suspicion-v1`.
  `derives: F1.1-F1.3; format v2 "Schedules live in testbed/schedules/"`
- **E1.** `end: quiescent` compiles to `EndTrig = [event |-> "quiescent"]`, and `Done` becomes "every step applied, and `Quiescent`".
  `Quiescent` is a state predicate: no request, write or ack in flight to a running receiver, and no running, unpaused client waiting for a grant.
  An event `end` is still matched after the last step. `derives: F1.1-F1.3; format v2 E1`
- **E2.** The checking run is judged first, and the end is looked for only after it passes. So a clause violation is `FAIL` whether or not the end is reachable, and `UNEXPLAINED end unreachable` is printed only when no violation was witnessed. This was already the round-1 order; only the message changed. `derives: format v2 E2`
- **T1, T2, T3.** No change in behaviour. The round-1 trigger semantics already armed step *i* when step *i*−1's action was taken, and offered a trigger only the events emitted while it was armed. The round-1 workload guards already made a step wait as T3 says (client crashed or paused, a request outstanding, no token, no superseded token).
  The `derives` tags now name the rules. `derives: format v2 T1, T2, T3`
- **A1.**
  - `holder` is accepted as the target of `request`, `write`, `pause`, `resume`, `crash` and `restart`.
  - `grantor` is accepted for `crash`, `restart` and partition sides.
  - The compiler rejects a schedule that uses either alias before any request step, since no Grant can have occurred by then.
  - At run time, a step whose alias resolves to no process waits (the `Resolved` guard in `DoStep`).
  `derives: F1.1-F1.3; format v2 A1`
- **A2.**
  - The compiler rejects restarting a process that is not crashed, crashing one that already is, pausing a paused client, resuming a running client, and pausing a lease node or storage.
  - An alias target makes the check conservative: `crash grantor` marks every lease node "possibly crashed".
  - The model's own guards make a step that is illegal at run time wait rather than act.
  `derives: F1.1, F1.3; format v2 A2`

### The P10 fix (judge's verdict, locus: model)
The defect was the one the judge described.
1. n3 is elected for term 1 by the non-maximal majority {n1, n3}.
2. n1 crashes.
3. c1 requests.
4. Grant needs a majority promised to term 1, and only n3 is. Elect(n2) is disabled because n2 can reach a leader whose term is at least its own promise. StepDown(n3) is disabled because nobody has promised higher.
5. The model stutters with a majority, storage and the requester all up and connected.

The adapted model without the fix (commit `362f1ae`) reproduces this lasso on shared P10 state for state.

**Change.** A new action, `Join(n, q)`, under weak fairness. A leader `n` that can reach an up node `q` whose promise is below `n`'s term raises `promised[q]` to that term. If `q` was a stale leader, it stops leading. This is the abstract counterpart of a leader's heartbeat or append bringing a follower into its term.

**Why it is safe.**
- Promises only grow.
- A grant still needs a majority promised to exactly the leader's term.
- An election still takes `max(maxTok)` over a majority. Any grant's confirming majority intersects that majority, and each member of the intersection recorded the token before it raised its promise.

C1_1, C1_2 and C1_3 still hold on every shared schedule, and the mutations still break them.

**Not changed:** `C1_4`, `Good`, every fairness condition except the added `WF(Join)`, and every failure-model action. `derives: C1.4, F1.1, F1.2`

### Mutations, round 2
- **P11 re-placed.** The round-1 break (the request is consumed when the grant is issued) needs a grant reply to be lost across the cut. Shared P11 never loses one: the partition keeps the grantor and the holder together. Run once on shared P11, it printed `PASS`, as predicted.
  The new break is in `DoRequest`. A request made while the requester cannot reach a majority of lease nodes never reaches the grantor and is not retried after the heal, while the client keeps waiting. It sits on C1.4's path from request to grant, and it is specific to partitions. On shared P11 it prints `FAIL C1_4`.
- **P8 re-applied.** P8's edit now inserts its extra action into `Protocol` instead of replacing the whole definition, so the copy keeps `Join`. The break itself is unchanged.
- **Unchanged.** Every other mutation is unchanged and still fails on its shared schedule.

### New interpretations (round 2)
- **R2.1, T1 and an action's own event.** The event that step *i*−1's action emits is emitted after step *i* is armed, so it can satisfy step *i*'s trigger.
  Shared P11 needs this: step 5 `{event: Request, client: c1}` is satisfied by the Request emitted by step 4's own `request: c1`. Under the strict reading P11 could never end. `format v2 T1`
- **R2.2, E1 "in flight".** A message counts as in flight when its receiver is running. Acks and grant replies to a crashed or paused client are not counted, and neither are writes to a crashed storage.
  A write the client still awaits, but whose message was lost, is not in flight. The client simply never hears back.
  "No client is waiting for a grant" applies only to running, unpaused clients. `format v2 E1`
- **R2.3, A1 at run time.** "Resolved at the moment the step's trigger fires" is kept from round 1. If no Grant has happened by then, the alias names nothing, and the step waits for ever. The run is then UNEXPLAINED end unreachable, unless a violation is witnessed first. `format v2 A1`
- **R2.4, A2 with aliases.** The static check is conservative wherever an alias makes the target unknowable before running. `format v2 A2`
- **R2.5, the P10 fix as an interpretation of "the grantor".** The contract leaves how the nodes agree to the implementation. The model's abstract grantor must not lose liveness through its own bookkeeping, so it includes a leader bringing a lagging node into its term. Round 1 omitted this, and that was a modelling error, not a reading of the contract.

### Results, round 2 (`run.sh --all`, about 115 s)
| Run | Verdict | Distinct states | Depth | MaxTerm |
|---|---|---|---|---|
| P1 | PASS | 20,700 | 23 | 18 |
| P2 | PASS | 725 | 15 | 6 |
| P3 | PASS | 728 | 14 | 2 |
| P4 | PASS | 4,232 | 26 | 6 |
| P5 | PASS | 2,654 | 27 | 6 |
| P6 | PASS | 5,375 | 26 | 2 |
| P7 | PASS | 31,646 | 28 | 10 |
| P8 | PASS | 3,122 | 19 | 6 |
| P9 | PASS | 17,123 | 26 | 2 |
| P10 | PASS | 250 | 13 | 8 |
| P11 | PASS | 611 | 15 | 6 |
| P12 | PASS | 467 | 11 | 2 |
| false-suspicion-v1 | PASS | 8,672 | 31 | 6 |

- **Mutations.** All 12 fail on their pair's clause: P1-P3 `FAIL C1_1`, P4-P6 `FAIL C1_2`, P7-P9 `FAIL C1_3`, P10-P12 `FAIL C1_4`.
- **Bound.** `TermHeadroom` held in every run, so the MaxTerm bound never binds.
- **Other bounds.** Unchanged in kind: 1-3 requests and 0-4 writes per shared schedule, `MaxDups = 1`, and every run finite by construction. The deepest state graph is 31, against the schedules' bound of 200 events.

Written only from `contract/v1.md`, `failure-model/v1.md`, `tests/pairs-v1.md`,
`testbed/schedule-format.md`, `observe/schema.md`, `AGENTS.md` and this directory.

## Round 2.1 (schedule format v2.1)
derives: C1.4, F1.1; format v2.1 T1, A1

Additive to the Round 2 section. The predictions and their outcome are in `PREDICTIONS-v2.1.md`.

- **T1 clarified.** v2.1 makes my round-2 interpretation R2.1 the rule, so R2.1 is now format v2.1 T1 and is no longer an interpretation. There is no behaviour change.
  `Matches`, `Emit` and `ScheduleStep` are tagged `format v2.1 T1`. `ScheduleStep` offers the next trigger `lastEv'`, the event its own action emitted.
- **New selector `non-grantor` (A1).**
  - **Model.** At the moment a trigger fires, the model records `trigNG`: the lease nodes that are up, minus the grantor of the most recent Grant. `ScheduleStep` explores every member of `trigNG` as the step's resolution (`NGChoices`, an existential).
  - **Restart.** `crash: non-grantor` records the chosen node in `ngDown`, and `restart: non-grantor` resolves to `ngDown`.
  - **Where it is accepted.** The selector is accepted as a target of `crash` and `restart` and as a member of a partition side. It is rejected as a target of `request`, `write`, `pause` and `resume`, since it names a lease node.
  - **Compiler checks.** The compiler rejects it before any request step (A1, as for `grantor`), and rejects `restart: non-grantor` with no outstanding `crash: non-grantor` (A2).
  - Two new variables, `trigNG` and `ngDown`, are tagged `derives: F1.1; format v2.1 A1`.
- **New interpretation, R2.1-a.** "Up at the moment the trigger fires" is evaluated in the state just after the event, or after the step action, that fired the trigger.
  For a partition side, `non-grantor` is resolved over the same candidates. No shared schedule uses it there.
- **New interpretation, R2.1-b.** If `trigNG` is empty (every other lease node down), the step waits for ever. The run is then UNEXPLAINED end unreachable, unless a violation is witnessed first. This mirrors R2.3.
- **Rewritten P10.** Without `Join`, it still exposes the round-2 defect (`FAIL C1_4`, by the predicted route). With `Join`, it prints `PASS` at 1,145 distinct states, depth 15, MaxTerm 8.
- **Results.**
  - All 13 shared schedules print `PASS`.
  - All 12 mutations fail on their clause: P1-P3 `C1_1`, P4-P6 `C1_2`, P7-P9 `C1_3`, P10-P12 `C1_4`.
  - No mutation needed re-placing.
  - The state counts for the unchanged schedules are as in Round 2.
- **Note.** The observe witnesses are produced with 4 TLC workers, so which shortest witness is printed can differ between runs: for example, which node wins the first election. The verdicts are unaffected.

## How to run
```
model/run.sh <schedule-name>   # e.g. P5, false-suspicion-v1; resolves only testbed/schedules/<name>.yaml [v2]
model/run.sh --mutations       # every mutation on its pair's schedule; each must print FAIL <its clause>
model/run.sh --all             # all 13 schedules, then all 12 mutations
```
It needs Java 11, `/home/tony/projects/tlaplus/tla2tools.jar` (override with `TLA2TOOLS=`) and `uv`.
`run.sh` pulls in `pyyaml==6.0.3` through `uv run --with`. `TLC_WORKERS` sets the TLC worker count (default 4).
A run prints exactly one line on stdout: `PASS`, `FAIL <invariant>` or `UNEXPLAINED <reason>`.
TLC statistics go to stderr. The observe file goes to `model/observe/<run>.jsonl`.
Scratch output (generated modules, raw TLC output) goes to `model/.work/`, which is git-ignored.

Pipeline for one run:
1. `compile.py` reads the schedule and writes `MC.tla` (the constants plus `Steps`), `MC.cfg`, `Witness.cfg` and `Done.cfg`.
2. TLC checks `MC.cfg`: invariants `TypeOK C1_1 C1_2 C1_3 TermHeadroom` and property `C1_4`.
3. On a PASS, TLC searches for a witness, i.e. a breadth-first, hence shortest, trace that completes the schedule and quiesces.
   `export.py` turns that trace into the observe file.
   On a FAIL, the counterexample becomes the observe file (`<pair>-mutation.jsonl` for mutation runs).
4. The run is UNEXPLAINED if any of these happens:
   - no trace reaches the schedule's end,
   - a witness's storage decision cannot be traced back to a Grant and grantor_term,
   - the `MaxTerm` bound is reached,
   - TLC reports anything other than a verdict.

## Files
| File | What | derives |
|---|---|---|
| `Lease.tla` | state machine, environment actions, invariants, liveness | all clauses and cells, per definition |
| `compile.py` | schedule compiler (YAML -> TLC model) | F1.1, F1.2, F1.3 |
| `export.py` | TLC trace -> `observe/schema.md` records | C1.1-C1.3, F1.1-F1.3 |
| `mutate.py` | generates `mutations/<P>/Lease.tla` | P1-P12 |
| `run.py`, `run.sh` | runner | all |
| `schedules/*.yaml` | **[v2] history only**: my M1 schedules, no longer run; the shared ones are `testbed/schedules/` | per file header |
| `mutations/<P>/Lease.tla` | the 12 mutated models (regenerated by `--mutations`) | per file header |
| `observe/*.jsonl` | observe files from the last `--all` | per run |
| `PREDICTIONS.md` | pre-registered verdicts, committed before any TLC run | |

## Model summary
- **Processes.** Three lease nodes, two clients and one storage process, with names taken from the schedule. The key is `"k"`.
- **Grantor.** Abstract: a leader per term.
  - Election: a node that cannot reach a leader whose term is at least its own promise may run an election.
    Any majority `Q` of up, reachable nodes promises the term `1 + max(promised over Q)`.
    The new leader starts from `max(maxTok over Q)`.
  - Grant: the leader issues token `ltok + 1` only when a majority that is still promised to its term confirms it.
    Each member of that majority durably records the token in `maxTok`.
  - Durable state: `promised` and `maxTok`. Volatile state: `leader`, `term` and `ltok`.
  - A leader that can reach a node promised to a higher term steps down.
  - **[v2]** A leader brings any reachable node whose promise is lower than its term into that term (`Join`).
- **Storage.** It accepts a write iff `token >= highest`, and on acceptance sets `highest := token`.
  The ledger and the value are durable.
  The ack is queued in volatile `toAck` and sent by a separate step, so a crash between accept and ack is possible.
- **Environment.** The actions are `Crash`, `Restart` (F1.1), `Partition`, `Heal` (F1.2) and `Pause`, `Resume` (F1.3).
  Each is tagged and reachable only through a schedule step.
- **Invariants.** They are stated over history variables (`grants`, `decisions`, `told`), not over the state they protect, so a component that forgets is caught:
  - `C1_1`: tokens strictly increase along the grant sequence.
  - `C1_2`: every accepted token is `>=` every previously accepted token.
  - `C1_3`: every write a client was told succeeded has an earlier accept decision for the same client, token and value.
- **Liveness.** `C1_4 == \A c : <>[]Good(c) => [](pending[c] => <>~pending[c])`, under weak fairness of every protocol action and of schedule steps.

## TLC bounds
- **Topology.** Fixed at 3 lease nodes, 2 clients, 1 storage and 1 key.
- **Terms.** `MaxTerm = 2 + 2 × (number of F1.1/F1.2 steps)`.
  `TermHeadroom` checks in every run that no reachable state uses the last allowed term, so the bound never constrains a behaviour.
  It held in all 13 runs. If it is ever reached, the run is UNEXPLAINED, not PASS.
- **Grants.** Bounded by requests: at most one grant per request step, plus a re-issue after a grant reply is lost to a fault.
  Requests per schedule: 1-3. The witnesses contain 1-3 grants.
- **Writes.** Exactly the schedule's write steps (0-4 per schedule), plus at most `MaxDups = 1` duplicated delivery of a write to storage.
  Duplicated grants and acks are not modelled; the client ignores them anyway (see interpretations).
- **Events.** The schedule's `bound: {events: 200}` is not needed as a TLC bound, because every run is finite by construction.
  The deepest state graph is 31 steps.
  The exporter warns if a trace exceeds `bound`; none does.
- **State space, unmutated model (distinct states / depth):**

| Run | States | Depth | MaxTerm |
|---|---|---|---|
| P1 | 11,678 | 17 | 10 |
| P2 | 476 | 15 | 6 |
| P3 | 371 | 10 | 2 |
| P4 | 3,470 | 25 | 6 |
| P5 | 2,420 | 27 | 6 |
| P6 | 2,387 | 21 | 2 |
| P7 | 4,679 | 20 | 10 |
| P8 | 794 | 14 | 6 |
| P9 | 9,680 | 21 | 2 |
| P10 | 329 | 10 | 4 |
| P11 | 389 | 10 | 6 |
| P12 | 371 | 10 | 2 |
| false-suspicion-v1 | 7,232 | 31 | 6 |

The full `--all` run takes about 80 s on this machine.
These state spaces are small because the schedule drives all workload and faults.
The model checks every interleaving of protocol steps around one scripted run, not arbitrary fault placement.

## Mutations
`run.sh --mutations` regenerates each copy from `Lease.tla` and runs it on its pair's schedule. Result at first version: all 12 FAIL on the predicted clause.

| Pair | Break (on the enforcing path) | Result |
|---|---|---|
| P1 | lease nodes lose `maxTok` on crash/restart | FAIL C1_1 |
| P2 | grant without majority confirmation | FAIL C1_1 |
| P3 | grantor reissues its last token (no increment) | FAIL C1_1 |
| P4 | storage ledger reset to 0 on restart | FAIL C1_2 |
| P5 | storage skips the `token >= highest` comparison | FAIL C1_2 |
| P6 | acceptance does not advance the ledger | FAIL C1_2 |
| P7 | storage acks "accept" on receipt, before its volatile decision | FAIL C1_3 |
| P8 | a client cut off from storage presumes its write succeeded | FAIL C1_3 |
| P9 | a client counts any ack carrying its current token as success | FAIL C1_3 |
| P10 | election needs every lease node, not a majority | FAIL C1_4 |
| P11 | a grant consumes the request at issue; a reply lost in a partition is never reissued (**[v2] re-placed**, see Round 2) | FAIL C1_4 |
| P12 | grantor waits for the previous holder to release; expiry ignored | FAIL C1_4 |

## Interpretations
Each item is a place where the inputs did not fix the answer, together with the choice made.

**Where things live**
1. **[v2] superseded by the format: shared schedules only.** **Schedule location.** `testbed/schedules/` did not exist, so I wrote all 13 schedules from `tests/pairs-v1.md` into `model/schedules/`.
   `run.sh` looks in `testbed/schedules/<name>.yaml` first, so a shared schedule replaces mine once it exists.
   The impl side will probably write its own versions of these schedules. Any difference between the two is itself a divergence to examine.
2. **Observe file location.** `observe/schema.md` names `observe/<run>.jsonl`. To avoid colliding with the impl side's file of the same name, the model writes `model/observe/<run>.jsonl` with `"side": "model"`.

**Time, expiry and pause**
3. **Time is abstract.** Grant lifetime is not a number in the model; `Lifetime = 1` is only the value reported on `Grant` events.
   - The grantor is not required to wait for a previous grant to expire before granting again. The contract states fencing properties (C1.1-C1.3), not mutual exclusion of holders.
   - An unpaused client's belief in its grant is never expired by the model. A schedule `write` uses the client's current token whatever its age.
4. **F1.3 pause.** "Paused past lifetime" is modelled as follows:
   - the paused client takes no steps (it receives no grants or acks) while every other process proceeds;
   - `resume` continues with the client's pre-pause state, including the token it believes is valid.
   - "Longer than the lifetime" is guaranteed by the schedule's trigger (for example, the resume fires on a later Grant to another client). The model has no clock to enforce it.
   - A paused client counts as not "up" in C1.4's condition.

**The grantor**
5. **[v2] with the P10 fix (`Join`), see R2.5.** **Grantor abstraction.**
   - Election and grant quorums may be any majority subset. They are not forced to be maximal.
   - A node runs an election only when it cannot reach a leader of a term at least its own promise. This is an abstract failure detector. It allows false suspicion under partition and prevents elections that would never end.
   - The token is a plain integer that the majority confirms. It is not term-encoded.
6. **[v2] now format rule T3.** **A request while waiting.** A client that is already waiting for a grant does not send a second request. The step waits until the earlier grant has arrived.
   This interpretation was adopted after a run: the first P1 witness merged two requests into one. The change tightened what the witness shows. Every verdict was the same before and after.
7. **Grant event and retries.**
   - `Grant` is recorded by the issuing lease node when it issues the grant, so a `{event: Grant}` trigger fires at issuance, not on receipt. A `write` step then waits until the client actually holds a token.
   - A lost grant reply is retried: the request stays pending until the client receives a grant, and the grantor may issue a new grant with a new token.
   - A grant reply that arrives when the client is no longer waiting is dropped.

**Schedules**
8. **[v2] now format rules T1, T2; see R2.1.** **Trigger semantics.** Steps are strictly sequential. Step *i*'s trigger is matched only against events emitted after step *i−1* was applied, including the event step *i−1* itself emitted. `start` fires immediately.
   This reads "both sides may act at any later point before the next step's trigger fires" as "the next trigger is not armed until this step is taken".
9. **[v2] see E1 and R2.2.** **End of a run.** The `end` trigger is matched after the last step. Ending stops the schedule's stimuli, but protocol steps continue, so in-flight work quiesces. Without this, C1.4 would be judged on runs cut off in the middle.
10. **[v2] now format rule A1.** **`grantor` and `holder`.**
    - They resolve to the node and the client of the most recent Grant at the moment the step's trigger fired.
    - The format mentions them only for partitions. I also accept them as the target of crash, restart, pause, resume and request.
    - `rest` is every process not named on the other side.
11. **`token: stale`.** The client's most recent token that is lower than the highest token granted so far, i.e. superseded. If the client has no such token, the step waits.
12. **Process names.** Process names come from the schedule. A schedule that is not exactly 3 lease nodes, 2 clients and 1 storage is rejected.
    The compiler also rejects:
    - a cell outside F1.1-F1.3;
    - an action that does not belong to its cell;
    - pausing a lease node;
    - a partition that does not have exactly two sides;
    - any other action not in the format.

**Faults and messages**
13. **Messages.**
    - Every channel is a set, so messages within a side may be reordered.
    - Only writes to storage are duplicated (at most once per run, `MaxDups = 1`). A duplicated grant or ack is ignored by the client: an ack counts only for a write it is still awaiting, and a grant only while the client is waiting.
    - At the moment of a partition, messages whose endpoints end up on different sides are dropped.
    - A message sent across an existing cut is lost.
    - A heal restores no lost message.
    - A message to a crashed process is lost.
14. **Crash.**
    - Storage crash: storage loses its inbox (in-flight writes) and its unsent acks. It keeps the ledger and the value.
    - Lease-node crash: the node loses its leadership state and keeps `promised` and `maxTok`.
    - Client crash: the client loses its token, every token it had received, its pending request and its awaited writes ("a restarted client has no grant").
    - "Storage replica" is read as the storage service, which is modelled as one process.

**The clauses**
15. **C1.2.** C1.2 is checked over the history of decisions, not over storage's own ledger variable, so a ledger that rolls back (mutation P4) is caught.
    "Records that token as the new highest" is not a separate invariant. A ledger that fails to record is caught when it accepts a lower token later (mutation P6).
16. **C1.3.** "Told a write succeeded" means the client recorded `WriteAck` with outcome `accepted`.
    The write is identified by (client, token, value). Values are unique within each schedule.
17. **C1.4, the condition.**
    - "A majority of lease nodes and storage stay up and connected to each other and to some requester" becomes `Good(c)`: storage is up, `c` is up and not paused, `c` and storage are on the same side, and some majority of lease nodes are up on that side.
    - "For long enough" is read as "eventually forever" (`<>[]Good(c)`).
    - Fairness is weak fairness on every protocol action and on schedule steps. The environment eventually performs each step whose trigger has held, so partitions heal when the schedule says so.
18. **C1.4, "obtains a grant".** This is read as "stops waiting". A crash also ends the wait; I read a crashed requester as no longer a requester. None of P10-P12 crashes the requester.

**Observe files**
19. **Witnesses.** An observe file for a PASS run is one sample: the shortest trace that completes the schedule and quiesces. It is not a summary of all behaviours.
    The exhaustive check is the verdict; the observe file is provenance for one run.
20. **What an observe record contains.**
    - Records are written in the model's trace order. The model has a total order; the file order is the only cross-process ordering the file carries, and no field records it.
    - `seq` is per process.
    - `causes` follow the schema. In addition, a `Grant` cites the `Request` it answers.
    - Internal steps (elections, step-downs, deliveries, sending an ack) are not observable events and are not emitted.
    - A `Fault` record is emitted from `proc: "env"`, with the action's resolved targets; a partition lists both sides.
    - For a liveness counterexample, the trace is the lasso's prefix; that the run stutters forever is reported on stderr, not in the file.

**Mutations**
21. **Mutation placement.**
    - P3's break (no increment) is not specific to F1.3: any second grant would expose it. It sits on C1.1's enforcing path, the increment, and P3's schedule exercises it through the paused holder's successor.
    - P7's break would also fail without the crash, because an ack sent before the decision is wrong on its own. The crash makes the lost decision permanent.

## Observations (not judgements)
- **False-suspicion witness** (`observe/false-suspicion-v1.jsonl`):
  1. The old holder c1 writes during the partition with token 1, after n2 had already granted token 2 (term 2) to c2.
  2. That write is accepted (`highest_before: 1`), because token 2 had not yet reached storage.
  3. After the heal, c2's token-2 write is accepted.
  4. c1's next token-1 write is then rejected (`highest_before: 2`).

  Every WriteAccept/WriteReject in the file names its token, its grantor_term and, through `causes`, the Grant it traces to.
  Fencing, as specified, allows a superseded holder to keep writing until a newer token reaches storage.

## Round-1 results
The round-1 bounds table and mutation table above describe M1 on my own schedules. The round-2 results are in the Round 2 section.

## Blocked
Nothing in the brief is blocked.

One conflict, resolved in favour of the brief: `AGENTS.md` says to read `docs/seed.md` and append to `docs/seed-log.md`, but my brief forbids reading `docs/` beyond the brief itself.
I did neither. Whoever is allowed should log this work.
