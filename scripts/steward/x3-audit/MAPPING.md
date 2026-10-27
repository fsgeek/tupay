# X3 support audit: reach columns to model state

derives: experiments/X3-prereg.md Departure 3 (support audit, probe method, "no support", "vacuous by design") and
measure 1(a); experiments/X3/reach.md and experiments/X3/holdout/reach.md (columns from scripts/steward/reach-table.py)

`probe.py` builds `Floor` as the conjunction of one conjunct per nonzero column of the schedule's reach row, using
the expressions below (the `{k}` is the row's floor), and `NoFloor == ~Floor`. TLC checks `NoFloor` as the only
invariant, at the side's own compiled bounds. The audit passes (SUPPORT) iff `NoFloor` is violated.

Sources are the clones at the commits scored: arm A `~/projects/tupay-x3-score/armA-model` (7e28e18), files under
`model/`; arm R `~/projects/tupay-x3-score/armR-model` (85e9b19), files under `model-regen/`.

## How each column is counted

Kinds: **structural** means a compiled constant. `probe.py` checks it against the side's compiler output (A:
`meta["processes"]`, R: `meta["lease"/"config"/"clients"]`) before TLC runs, and a miss is NO-SUPPORT without a
run. It is also conjoined in `Floor`, where it is constant-level and costs nothing. **state** means a model variable.
**step** means the count comes from the schedule position. In both models `pc` is the index of the next schedule
step, and a step at index `i < pc` has been taken: its action fired in the model, through A's `ScheduleStep`
(`pc' = pc + 1`, Lease.tla:1186) or R's `Take` (Lease.tla:913). **vacuous** means the model has no state for the
quantity.

| Column (reach.md) | Arm A (`model/Lease.tla`) | Arm R (`model-regen/Lease.tla`) |
|---|---|---|
| lease | structural: `Cardinality(Nodes) >= k` (CONSTANT Nodes :21; compile.py:473 `MCNodes`) | structural: `Len(LeaseSeq) >= k` (:33; compile.py:279) |
| config | structural: `Cardinality(Init0) >= k` (:22; compile.py:475) | structural: `Cardinality(InitCfg) >= k` (:37; compile.py:280) |
| clients | structural: `Cardinality(Clients) >= k` (:23; compile.py:477) | structural: `Cardinality(Clients) >= k` (:34) |
| grants | state: `Len(grants) >= k`. `grants` (:68) is the history of every Grant, appended in `Grant` (:531) | state: `Cardinality(gr) >= k`. `gr` (:64) is the set of decided grants, added in `AE` and `Propose` from `Eval` (:257, :432, :462). This is the author's own `ProbeGrants` |
| reconfig sent | step: `AuditStepsDone("reconfig") >= k` (`Steps[i].kind`, compile.py:186; applied by `DoReconfig` :847). A keeps no send history: `rcMsgs` is consumed | state: `Cardinality(rqs) >= k`. `rqs` (:64) gains a record on every reconfigure step (:900) |
| epochs | state: `\E i \in 1..Len(commits) : commits[i].rec.ep >= k`. `commits` (:106) holds every decided commit, and `rec.ep = e + 1` (:621) | state: `GCur >= k`. `GCur` (:173) is the highest epoch in `dc`, the decided commits (:713), with epoch 0 the deployment. This is the author's own `ProbeEpoch` |
| crashes | step: `AuditStepsDone("crash") >= k` (`kind` "crash", compile.py:208; `Crash` :955). Like reach-table.py, this counts every crash step, of a client or storage too | step: `AuditStepsDone("crash") >= k` (`do.a` "crash", compile.py:170; `DoAct` :829) |
| amnesic | state: `AuditSum(inc, Nodes) >= k`. `inc` (:95) is +1 per amnesic restart (`AmnesicRestart` :1016) | state: `AuditSum(inc, Lease) >= k`. `inc` (:66) is +1 in `AmnesiaEff` (:787) |
| clock steps | step: `AuditStepsDone("clock") >= k`. Each step sets `off' = off + s` (`ClockStep` :1036, `off` :110) | **vacuous** (not modelled). Lease.tla:27 says no protocol decision reads a clock, and the `clock` branch of `DoAct` (:903) changes only `ev`. Conjoined by step position only so the rest can be reported |
| max ticks | step: `\E i \in 1..(pc-1) : Steps[i].kind = "clock" /\ abs(Steps[i].s) >= k` (`s` is ticks, compile.py:195) | **vacuous**. Same expression on `Steps[i].do.ticks` (compile.py:263) |
| terms | state: `(\E i : grants[i].term >= k) \/ (\E n \in Nodes : leader[n] /\ term[n] >= k)` (`leader` :47, `term` :48; elected in `Elect`, bounded by `t <= MaxTerm` :398) | state: `(\E g \in gr : g.term >= k) \/ (\E n \in Lease : role[n] = "L" /\ term[n] >= k)` (`WinEff` :330 makes the leader; `TermCap` :310) |

In the TLA+ source, `abs(x) >= k` is written as `x >= k \/ -x >= k`, and `AuditStepsDone(kind) ==
Cardinality({i \in 1..(pc - 1) : <kind of step i> = kind})`. Bound identifiers are prefixed (`ai`, `ag`, `an`,
`audit*`) because arm R declares a constant `S`.

**Vacuous verdict.** Arm A models every column. Arm R does not model a clock, so on R any row with a nonzero
clock-steps or max-ticks floor (P32, P41, P44, P47, P50, P53, P59, P62, H11, H12, H13) gets the verdict VACUOUS.
`audit.sh` still runs the probe with every floor, the clock ones counted by step position, and reports that result
beside VACUOUS, so a reader can see whether the rest of the row is reachable.

## Bounds and configuration used (the side's own, as `scripts/steward/x3-runs.sh` ran them: `run.sh <name>`, no flags)

- **A**: `compile.compile_schedule(path, dir, Lease.tla)` (model/run.py `check`). It gives MaxTerm = 2 + 2 × fault
  steps (compile.py:455) and MaxDups = 1. The cfg is the author's `MC.cfg` with its `INVARIANT` and `PROPERTY`
  lines removed, which leaves CONSTANTS, `SPECIFICATION Spec` and `VIEW View`. TLC flags are the author's
  (run.py:49): `-deadlock -cleanup -checkpoint 5`. A has no CONSTRAINT or ACTION_CONSTRAINT.
- **R**: `compile.compile_schedule(sched, None, None)` and `write_outputs(..., 'Lease')` (model-regen/run.py
  `run_one`). It gives MaxTerm = 1 + leader losses + Spur0 (compile.py:277), Spur0 = 1, and TermCap = MaxTerm +
  |lease| after the last fault (Lease.tla:310). The cfg is the author's `safety.cfg` up to its `INVARIANTS`:
  CONSTANTS, `VIEW View`, `SPECIFICATION SpecL`. TLC flag is `-nowarning`. R has no CONSTRAINT or
  ACTION_CONSTRAINT.
- Both: heap 8g, `-workers 8`, `systemd-run --user --scope -q -p MemoryMax=12G -p MemorySwapMax=0`, metadir and
  java tmpdir inside the outdir.

## Judgement calls

1. **Conjunction at one state.** The registered method needs one state that meets every floor. Every expression
   above is monotone along a run (history variables, step counts), except three. The `leader`/`role` disjunct of
   terms is volatile. `inc` is monotone, but A and R reset `promised`/`term` on amnesia, which is why terms is read
   from grant history or a current leader and not from `promised`/`term` alone. A's `off` is not monotone and is
   not used (item 3).
2. **Terms means a leader (grantor) term k existed.** It is read as a grant issued in term ≥ k, or a node that is
   currently leader at term ≥ k. A bare `term[n] >= k` was rejected for R because `SpurFail` (:360, `BecomeCand`
   :319) raises a term with no leader. A's `promised` would be equivalent in A, since it is raised only to an
   elected term, but it is reset on amnesia. A schedule with a terms floor of 2 and no request that both ends with
   no leader would be judged by the leader disjunct only. Of the 63 rows, H11 is the only one with a terms floor
   of 2 and zero grants.
3. **Max ticks is counted by step position in A, not by `off`.** `off[p]` accumulates: P44 steps the grantor by
   −1 and then +3 ticks, so `off` never reaches 3 although a 3-tick step is taken. The floor asks for the largest
   single step, which is the `s` of a taken clock step. Taking that step is what changes `off`
   (`ClockStep`, `off' = off + s`), so in A the step is the modelled clock.
4. **Crashes, reconfig sent (A) and clock steps are counted by step position.** No state variable counts them,
   because a crash is undone by a restart and requests are consumed. A taken step is a reached model transition,
   since every step is guarded by its trigger and its own enabling condition. A floor that needs the schedule to
   get that far can therefore fail.
5. **R's clock is vacuous, not step-counted.** R takes the clock step but has no clock state. Departure 3 names
   "no clock" as the example of vacuous by design. `audit.sh` labels these rows VACUOUS and reports the step-position
   result beside the label. That result is not presented as SUPPORT.
6. **R's deadlock check is off in the probe.** The author's `safety.cfg` has `CHECK_DEADLOCK TRUE`, which is the
   liveness terminal form. Left on, it would stop the search at the first stuck state, which is not a reach
   question. A's runs already pass `-deadlock`, which turns the check off. For arm R, the full-space count from a
   NO-SUPPORT run (for example, P63 MUTANT: 638,457 distinct) is therefore larger than the count from the author's
   safety run when that run stopped at a FAIL (P63: 24,725, FAIL C3.4).
7. **R uses `SpecL`, not `Spec`.** `SpecL` is the specification of the author's checking run. It adds only `Idle`
   stuttering, so the set of reachable states is the same.
8. **Floors are ≥.** A state that exceeds a floor (more grants, a higher epoch) meets it.

## Anti-theater (`MUTANT=1`)

The epochs floor is set to (number of reconfigure steps in the schedule) + 1. Each request commits at most one
epoch, in A (`commits` gets one record per decided request) and in R (one `dc` entry per decided request), so no
run reaches it. The verdict must be NO-SUPPORT, after a complete search. In arm A, the complete search of the mutant
visits exactly the distinct-state count of the author's own checking run (P1: 20,852; H13: 101,502, from
`model/.work/<id>/MC.out`). The probe therefore explores the space the author checked: not a smaller one, and not
a different one.

## Run all 63 schedules for one side

```
SIDE=A   # or R
O=<out-root>; for n in $(seq 1 33 | sed 's/^/P/') $(seq 40 54 | sed 's/^/P/') $(seq 58 63 | sed 's/^/P/') \
  false-suspicion-v1 H7 H8 H9 H10 H11 H12 H13 H14; do
  scripts/steward/x3-audit/audit.sh $SIDE $n $O/$SIDE-$n; done | tee $O/$SIDE-verdicts.txt
```
Add `SPLIT=1` to have each NO-SUPPORT followed by one probe per floor, which shows the floor or floors that are
not reachable.
