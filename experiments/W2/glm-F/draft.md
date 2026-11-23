# The Shared Test Interface (STI) for the Verified-Backup Contract

**Version 1, for contract draft 7 and binding-tupay v1.**

This document specifies: (A) the schedule format, (B) the implementation-side contract, (C) the harness's obligations, (D) one complete example schedule, (E) OPEN CHOICES, (F) CONTRACT QUESTIONS.

The interface's design rule, applied throughout: **prescribe nothing the contract does not prescribe, except where injection or observation is impossible without it.** Every such constraint is flagged with a *why*.

---

## A. The schedule format

### A.1 Physical form

A schedule is a single UTF-8 text file, name ending `.sched`. It is line-oriented: one directive per line, `#` starts a comment. It is valid YAML (a subset), so both harnesses and model runners can parse it with stock tools, but the grammar below is the normative definition. Schedules are compared byte-for-byte when checking that "the same suite ran everywhere."

### A.2 Grammar

```
schedule     := header events assertions
header       := "schedule:" WS name
               "binding:" WS binding-id
               "params:" WS param-overrides?        # optional; defaults from binding
               "horizon:" WS duration "after" WS "last-event"
param-override := param-name "=" value (";" param-name "=" value)*
event        := clock-event | source-event | inject-event | heal-event | query-event
clock-event  := "at" WS time "on" WS host-id ":" WS clock-op
clock-op     := "advance" WS duration            # virtual clock moves forward
               | "step" WS ("+"|"-") duration     # discontinuous jump (BF1.6)
source-event := "at" WS time "on" WS "S" ":" WS source-op
source-op    := "write" WS path WS bytes
               | "delete" WS path
               | "rename" WS path WS path
               | "truncate" WS path WS integer
               | "empty" WS path
               | "git-commit" WS path
               | "churn" WS path WS duration      # rewrite in place for duration (BF1.5)
               | "place-credential" WS path       # a file matching T13's patterns
inject-event := "at" WS time ":" WS "inject" WS cell-id WS cell-args
heal-event   := "at" WS time ":" WS "heal" WS cell-id (WS cell-args)
query-event  := "at" WS time ":" WS "check" WS check-id
assertion    := "assert" WS temporal-expr WS "derives:" WS clause-id
               | "assert-not" WS temporal-expr WS "derives:" WS clause-id
```

**Time.** All times in a schedule are given in **harness time** (`h`), a monotonic counter starting at 0, in units of hours (T19). `at 168.0` means "168 harness-hours after the schedule starts." Durations use `h` and `d` only. The harness maps harness time to each host's clock (see C.2); a schedule never mentions a host's clock directly except in `step`.

**Hosts.** The five host ids are fixed: `S`, `R`, `RH` (restore host), `FC` (freshness checker — a process on R, but addressable separately for injection), `NC` (notice channel). The harness instantiates all of them (C.3).

**Params.** A schedule may override the binding's parameter values (e.g. `params: I=1h; M=2h`) so that weeks of contract time compress. The implementation must accept parameter values from the harness at start-up (B.4). Default: the binding's values.

**Horizon.** `horizon: 24h after last-event` fixes the scoring instant: the harness time of the last event plus this duration. All recoverability (T11/B1.3/B1.19) assertions are judged at that instant and only there. Deadline assertions (`within D`, `within M`, …) are interval assertions and are judged continuously.

**Assertions.** An assertion's expression is built from the observation vocabulary (A.4). Every assertion carries exactly one `derives:` tag naming the clause (or interpretation id, e.g. `derives: I-B1.12`) it checks. A schedule with an untagged assertion is invalid; the harness rejects it before running.

### A.3 Fault-injection vocabulary (one entry per BF1 cell)

| Cell | Directive | How injected (harness-side) | How it ends |
|---|---|---|---|
| BF1.1 | `inject BF1.1 process=S stage=copy` | `SIGKILL` the implementation's process (harness knows PIDs via B.1); `stage` is advisory | `heal BF1.1` — harness restarts the process per B.2 (implementation must be restartable) |
| BF1.2 | `inject BF1.2 pair=S,R` (any pair of S, R, RH) | harness drops all packets between the two hosts' network namespaces / loopback ports | `heal BF1.2 pair=S,R` |
| BF1.3 | `inject BF1.3 snapshot=<n> byte=<off> xor=<hex>` | harness flips bytes in the snapshot's stored bytes at R's data directory (harness knows the layout only as "the directory R was given"; it corrupts a random byte in a file chosen by size, or the named snapshot if the implementation exposes snapshot names per B.6) | permanent for the run; "ends" by detection (B1.12) or by `heal BF1.3` restoring the byte |
| BF1.4 | `inject BF1.4 host=R` | harness fills the host's scratch filesystem (a small loopback fs, C.3) to 100% | `heal BF1.4 host=R` — harness deletes its filler files |
| BF1.5 | source-ops during a run (the `churn`, `write`, `rename` events above) | harness mutates the source trees while a run is in progress | ends when the run ends |
| BF1.6 | `at t on R: step +24h` | harness moves that host's virtual clock discontinuously (C.2) | instantaneous; the step *is* the event |
| BF1.7 | `inject BF1.7` | harness makes the notice channel unreachable (stops the NC listener) while S stays up | `heal BF1.7` |
| BF1.8 | `inject BF1.8 timer=FC` (or `S`, `RH`) | harness suppresses delivery of clock ticks to that host for the injected period: the host's clock simply does not advance | `heal BF1.8 timer=FC` |
| BF1.9 | `empty`/`truncate`/source-ops on a source tree | harness mutates sources | ends when the harness restores the tree (`heal BF1.9 tree=<path>`) or never |
| BF1.10 | `inject BF1.10` | harness deletes the entire contents of R's data directory | permanent; ends by rebuild (B1.18) |
| BF1.12 | `inject BF1.12 snapshot=<n>` or `snapshot=random` | harness deletes snapshot files at R, not via the service | permanent |
| BF1.13 | `inject BF1.13 copy=S` / `copy=R` / `copy=both`, `mode=lost` or `mode=corrupt` | harness deletes or byte-corrupts the status-record file(s) the implementation registered (B.5) | permanent; ends by B1.18 recovery |
| BF1.14 | `inject BF1.14 host=RH` (binding: RH, S, R) | harness `SIGSTOP`s all the host's implementation processes; its clock freezes | `heal BF1.14 host=RH` — `SIGCONT` |

Injection never requires the implementation's cooperation, except that the implementation must have told the harness where its processes, status record, and R-side data live (B.1, B.5, B.6). That is the whole of the cooperation the interface requires.

### A.4 Observation vocabulary (what assertions may name)

The harness records, in a single **event log** (JSON Lines, one file per run, written by the harness — never by the implementation):

- `notice {clause, arrived_at, sent_from, content_hash}` — every message that reaches the notice channel, with the clause id it names (T16) and arrival time in harness time. The harness reads these from the NC endpoint (C.3).
- `mark {snapshot, mark, at, writer}` — every snapshot mark written to R's copy of the status record. The harness learns marks by watching the status-record file(s) registered under B.5 (see C.6 for how).
- `run_entry {seq, state, stage, at}` — same mechanism.
- `snapshot_present {seq, at}` — harness polls R's data directory for snapshot names (B.6).
- `recoverable {seq, at, result}` — the harness's own restore check: at the horizon (or at a `check` event), the harness copies the snapshot from R to a scratch restore area, compares every file's sha256 against the manifest stored with the snapshot, and clones any git bundle and compares refs. This is the harness's independent T10, run on harness-controlled code, not the implementation's.
- `clock {host, harness_time, host_time}` — logged at every step and every advance.

Assertion expressions are conjunctions of predicates over this log, e.g.:

```
assert notice(clause="B1.7", after=event("inject BF1.12 snapshot=5"), within="1h") derives: B1.7
assert at(horizon): recoverable(snapshot=5) derives: B1.3
assert never: run_entry(state="ok", seq=5) and not verified(seq=5) derives: B1.1
```

The full predicate set: `notice`, `mark`, `run_entry`, `snapshot_present`, `recoverable`, `verified` (R-side re-verification observed via the record), `at(t)`, `within(d)`, `after(ev)`, `never`, `always`, `exists`. `verified` is observable only through the record and notices; the interface does not require the implementation to expose an internal verification event (see CONTRACT QUESTIONS, Q3).

---

## B. The implementation-side contract

An implementation must expose or obey **exactly** the following, and nothing more:

**B.1 Registration file.** At start-up the implementation writes, to a path given by the harness in the environment variable `STI_REG`, a JSON file:
```
{ "pids": [...],                       // all long-running processes (for BF1.1, BF1.14)
  "status_record_S": "<path>",         // file(s) holding S's copy of T15
  "status_record_R": "<path>",         // file(s) holding R's copy
  "r_data_dir": "<path>",              // directory where snapshots live at R
  "nc_endpoint": "<uri>",              // where the implementation sends notices
  "snapshot_naming": "seq-in-filename" }
```
*Why this constraint:* BF1.1, BF1.13, BF1.14, BF1.3, BF1.12 and notice observation are impossible without knowing where these things are. The interface does not constrain their format, only their location.

**B.2 Restartability.** Every process must be restartable by re-running the same start command the harness used. *Why:* BF1.1 requires crash-and-restart injection.

**B.3 No wall-clock, no real sleeps.** Implementations must read time exclusively from the harness clock service (C.2) at the address given in `STI_CLOCK`, per host. Timers are set against that clock. *Why:* requirement 1 — weeks in minutes — is impossible if the implementation sleeps on the real clock; and T12 (ages on each host's own clock) requires per-host clocks the harness can step (BF1.6) and freeze (BF1.8). This is the interface's largest constraint and it is unavoidable.

**B.4 Parameters from the harness.** The implementation accepts *I, M, P, H, D, X, Q, Rb, G, K, Mo* as configuration from the harness (environment or argv), overriding the binding's values. *Why:* schedules compress contract time by shrinking parameters; without this, a multi-week schedule cannot run in minutes.

**B.5 Status record as a file.** Both copies of T15 must be files (or directories of files) under paths the harness can read and write. *Why:* BF1.13 injection and mark/run-entry observation.

**B.6 Snapshots addressable by sequence number.** Snapshot names at R must embed the sequence number such that the harness can, given a number, find the snapshot's bytes and manifest. The `snapshot_naming` field in B.1 lets the implementation declare its scheme (v1 of this interface accepts only `seq-in-filename`: a filename containing the decimal sequence number). *Why:* BF1.3, BF1.12, `snapshot_present`, and the harness's independent restore check all need this. The contract itself already names snapshots by sequence number (T6), so this adds only a filename convention.

**B.7 Notices to the NC endpoint.** All notices (T16) are delivered to `nc_endpoint`, as JSON: `{"clause": "B1.7", "sent_at": <host time>, "body": "..."}`. The clause field is mandatory (the contract already requires a notice to name its clause). *Why:* assertion 4 requires observing which clause a notice names and when it arrived.

**B.8 Nothing else.** No required API, protocol, daemon shape, language, storage format, or tooling. The implementation may run as one process or many, on one machine or several, as long as the registration file is truthful and the role placement the contract fixes (checker on R, restore host with no path to S) is honored within the test topology (C.3).

---

## C. The harness's obligations

**C.1 Topology.** The harness creates, on one machine, without root:
- **S**: a scratch directory tree holding the source trees (a git repo, a private dir, a homes dir, with caches), plus the implementation's S-side processes.
- **R**: a scratch directory (on a small loopback/sparse filesystem so BF1.4 is injectable) holding `r_data_dir` and R's status-record copy, plus the checker process.
- **RH**: a scratch directory and the implementation's restore-host processes. The harness enforces T4 by network isolation: RH's namespace can reach R, not S.
- **FC**: the checker, as a process registered under R's pids.
- **NC**: a harness-owned local listener (a unix socket or localhost port) that records every received notice into the event log with arrival time. The binding says the channel's record is on S; in a test the record *is* the harness's log — see OPEN CHOICES 6.

Hosts are separated by network namespaces or by distinct loopback ports per host, whichever the harness can do without root; partitions (BF1.2) are enforced at that boundary.

**C.2 Time.** The harness runs a clock service per host. Each host's clock starts at a fixed epoch (harness time 0 = host time 0, in hours). The harness advances clocks by delivering tick messages; the mapping harness-time → host-time is logged. `advance` moves a host's clock smoothly (the harness delivers the new time; the implementation's timers fire against it); `step` moves it discontinuously (BF1.6, error up to the step per T12); BF1.8 injection simply stops delivering ticks to that host. The harness advances all clocks together at a configurable real-time compression factor, and may advance them as fast as the implementations permit (implementations must not assume real time passes — B.3).

**C.3 Execution.** The harness: starts the implementation with `STI_REG`, `STI_CLOCK`, parameters, and scratch paths; waits for the registration file; replays the schedule's events at their harness times; runs `check` events and the horizon check; writes the event log; evaluates assertions; reports pass/fail per assertion with its `derives:` tag.

**C.4 Independent restore check.** At each `check` and at the horizon, the harness performs its own T10-equivalent (copy from R, hash every file against the manifest, clone bundles, compare refs) using harness code, and logs `recoverable`. The implementation's own restore check is *not* used for scoring recoverability; it is observed only through marks. *Why:* AI1.2's witness ("T10 recomputes hashes on another host") demands an independent checker.

**C.5 Injection.** As tabled in A.3. The harness must be able to inject every cell without the implementation's help beyond B.1–B.6.

**C.6 Mark/run-entry observation.** The harness polls (or inotify-watches) the registered status-record files. Because the record's *format* is implementation-defined, the harness cannot parse it directly; instead **the implementation must additionally append, to a harness-watched sidecar file next to each status record, one JSON line per entry write**: `{"kind":"run_entry"|"mark", ...}` (fields as in A.4). *Why:* T15's format is not fixed by the contract, but assertions need marks and entries; a sidecar is the least-prescriptive observation point. This is constraint B.9 (folded here): the sidecar is write-only observation, never read by the implementation, and its loss must not affect the service.

**C.7 Model runner.** The same `.sched` file must be readable by a formal model's runner. A model must accept: the header (name, binding, params, horizon); all `inject`/`heal` events and their cell ids and arguments; clock `step` events; source events (as abstract mutations); and all assertions. A model **reports inexpressibility** by emitting, before running, a line per problem:
```
UNSUPPORTED <line-number> <reason>
```
and then runs the schedule with those lines removed, reporting assertions only for what it ran. The harness treats a model run with UNSUPPORTED lines as a partial result, never as a pass. *Why:* requirement 6 — the same text must be usable, and refusal must be explicit and per-feature, not silent.

**C.8 Determinism.** Where a schedule says `snapshot=random` or BF1.3 picks a byte, the harness seeds its RNG from the schedule name, so runs are reproducible.

---

## D. Example schedule

`b1_12_b1_13_corrupt_and_loss.sched` — injects BF1.3 (corruption) and BF1.12 (snapshot loss), checks B1.12, B1.13, B1.7, B1.3, B1.19. Compressed parameters.

```yaml
# Two environmental losses: a corrupted byte (BF1.3) and a deleted
# snapshot (BF1.12). Detection must follow; the protected set must
# survive. Weeks compressed by shrinking I.
schedule: corrupt-and-lose
binding: tupay-v1
params: I=1h; M=1h; P=2h; H=1.5h; D=0.5h; X=0.5h; Rb=1h; G=4h; K=6h; Mo=1h
horizon: 2h after last-event

# Day 0: let the service establish itself.
at 0.0 on S: write tupay-homes/a/seed.txt "hello"
at 0.0 on S: git-commit tupay
at 1.0: check establish          # expect >=1 ok entry by now (B1.9)

# BF1.5: churn during a run, to make snapshot 2's life interesting.
at 1.2 on S: churn tupay-homes/a/state.db 0.3h

# BF1.3: corrupt one byte of snapshot 1 at R.
at 2.0: inject BF1.3 snapshot=1 byte=auto xor=01

# BF1.12: delete snapshot 2 at R, not by the service.
at 3.0: inject BF1.12 snapshot=2

# BF1.6: clock step at R, so deadline error is exercised (T12).
at 3.5 on R: step +1h

# Let the checker run and the record react.
at 5.0: check marks

# Horizon: 2h after the last event (7.0).
assert mark(snapshot=1, mark="damaged", after=event("inject BF1.3 snapshot=1"), within="2.5h") derives: B1.12
assert notice(clause="B1.7", after=event("inject BF1.3 snapshot=1"), within="3h") derives: B1.7
assert mark(snapshot=2, mark="missing", after=event("inject BF1.12 snapshot=2"), within="2.5h") derives: B1.13
assert notice(clause="B1.7", after=event("inject BF1.12 snapshot=2"), within="3h") derives: B1.7
assert at(horizon): snapshot_present(3) derives: B1.4
assert at(horizon): recoverable(snapshot=3) derives: B1.3
assert at(horizon): exists(n: run_entry(state="ok", seq=n) and mark(snapshot=n, mark="restore-checked") and age(n) < "4h") derives: B1.19
assert never: run_entry(state="ok", seq=2) and not snapshot_present(2) and not mark(snapshot=2, mark="missing") derives: B1.6
```

---

## E. OPEN CHOICES

1. **Schedule file syntax (YAML subset vs. custom DSL vs. JSON).** Chose line-oriented YAML-valid text: stock parsers exist for both harness languages and model runners (TLA+ tooling can be given a simple reader), and it stays diffable and byte-comparable. Rejected: full YAML (too permissive, ambiguous across parsers), JSON (unreadable for weeks of events).
2. **Virtual time mechanism (clock service vs. LD_PRELOAD vs. container time namespaces).** Chose an explicit clock service the implementation must query (B.3). Rejected LD_PRELOAD faketime: it prescribes a C-unix toolchain and breaks for Go/Rust/VM implementations; rejected time namespaces: needs root. Cost: implementations must be written against `STI_CLOCK`. This is the one place the interface constrains internal design, justified by requirement 1 and BF1.6/BF1.8.
3. **Host isolation without root (network namespaces vs. loopback ports vs. none).** Chose "either, harness's choice," with loopback ports as the portable fallback. T4 (RH has no path to S) is contract-fixed, so *some* isolation is mandatory; namespaces give real partitions for BF1.2, ports only approximate them (a partition becomes "refuse connections"). Left as a harness quality tier.
4. **Observation of the status record (parse it vs. sidecar).** Chose the sidecar (C.6). Parsing would prescribe T15's format, which the contract deliberately does not fix. Cost: one extra write path in the implementation, declared write-only.
5. **Recoverability scoring (implementation's restore check vs. harness's own).** Chose the harness's independent check at the horizon. The contract's T11 says restorability is "a claim about a procedure" whose evidence is a passing T10 — but for scoring we need an observer that is not the examinee (AI1.2's witness says exactly this). The implementation's checks are still observed via marks, so B1.8's completion obligation is testable on the implementation's own behavior.
6. **The notice channel's record "on S" (binding) vs. harness log.** The binding says the plaza's record is on S, and EX1.6 follows from that. In a test, the harness's NC listener *is* the channel and its log *is* the record, held by the harness, not S. This changes EX1.6's applicability in tests. Chose this because the harness cannot host a real plaza; flagged because it means BF1.7 tests the "channel unreachable" case only via the harness stopping its listener, and S-down-with-record-on-S cannot be reproduced faithfully. See CONTRACT QUESTIONS Q5.
7. **Horizon semantics (fixed instant vs. per-assertion deadlines).** Chose a single fixed horizon for state assertions (B1.3, B1.19, B1.4) plus continuous evaluation for temporal assertions. The contract mixes state and temporal obligations; a single scoring instant matches "recoverability is judged" in requirement 5 and avoids arguing about when a state assertion should be sampled.
8. **Parameter compression vs. real-time compression.** Chose both available, with parameter override as the default (the example uses it). Pure time-compression (advance clocks fast, keep I=24h) is more faithful to the binding's values but makes *D*=1h etc. also fast, which is fine; parameter shrinkage risks crossing thresholds where behavior is qualitatively different (e.g. G vs I+X+M). Schedules must state which they use; the example uses parameter override and says so.
9. **BF1.3 target selection.** The contract does not fix R's storage layout, so "corrupt a byte of snapshot n" can only mean "corrupt a byte in a file under `r_data_dir` belonging to n." Chose `seq-in-filename` naming (B.6) to make this well-defined; a layout-agnostic random-byte option is kept for implementations whose dedup stores snapshots interleaved — in which case BF1.3 may hit shared data and the harness logs which files changed.
10. **Model inexpressibility (refuse whole schedule vs. partial run).** Chose partial run with explicit `UNSUPPORTED` lines. A model that cannot express, say, BF1.4 (disk full) should still check B1.7's notice behavior. Rejected whole-file refusal: it would let models silently shrink coverage.
11. **Assertion language (full temporal logic vs. fixed predicate set).** Chose a small fixed predicate set with `always/never/within/after`. Full LTL would be more expressive but each model runner would interpret it differently; the fixed set maps directly onto the event log and onto TLA⁺ temporal formulas without ambiguity.

---

## F. CONTRACT QUESTIONS

Places where injection or observation could not be designed because the contract is unclear. Not resolved here.

1. **"Verified" (T8) is unobservable from outside.** T8: *"Verified: an event. At R, every file of the snapshot was read and matched T7c."* Nothing in T15 or T16 records that a verification happened, except indirectly (an *ok* entry implies it for the initial verification; B1.12's re-verification is observable only when it *fails*, via a *damaged* mark). So I-B1.12's `◇≤P (verified_at_R(n) ∨ damaged(n))` cannot be asserted positively: a service that never re-verifies and nothing corrupts passes every observable test. The interface records `verified` only via sidecar run entries if the implementation volunteers them; the harness cannot require it without prescribing a record format. *Question for the steward: does some clause require a positive record of re-verification?*
2. **B1.7's notice content for "overdue" reports.** B1.7/B1.19: the checker reports violations "as *overdue*, with the cause." The interface requires the notice's `clause` field (T16 forces that much) but the *cause* string is unspecified vocabulary ("failed checks, failed runs, failed captures, or an unavailable host" — is that an exhaustive enum? free text?). Assertions can check `clause` but not cause. *Is the cause vocabulary normative?*
3. **What "the notice channel is unavailable" means when the record is on S (BF1.7 + EX1.6).** B1.16: *"While the notice channel cannot be reached, the sender records the notice where the freshness checker reads."* For this binding the channel's record is on S, and BF1.7 is "the notice channel is unavailable **while S is up**." It is unclear whether unavailability is a property of the channel endpoint, of the record's host, or both, and where the checker "reads" if the record is on S and the checker is on R (T23). The harness injects BF1.7 by stopping its NC listener, but whether that faithfully models this binding's channel is unclear.
4. **BF1.8 ("a timer does not fire") vs. B1.3's clock freeze.** The interface implements BF1.8 as freezing a host's clock, and BF1.14 as SIGSTOP (which also freezes the clock). The contract does not say whether a timer that "does not fire" leaves the host's clock running (time passes, timers are lost) or stops time. These are observably different for T12 ages and for B1.7's "measures each deadline's age from the clause's own start event." *Which is it?*
5. **T5a's "highest snapshot name at R" under BF1.10.** After R is reimaged (BF1.10) and both record copies are lost, T5a says the number is max(…, highest snapshot name at R)+1, but there are no snapshots and no records; the contract "makes no claim about that number." The interface can inject this, but a schedule cannot assert anything about sequence numbers afterward — confirmed untestable, listed because teams will expect a cell here. No question, just a boundary.
6. **B1.15's *Q* "measured on the binding's own history."** The binding gives Q=0.05 measured from 9 quiet runs, with noise "unmeasured." A schedule that empties a source tree trivially crosses Q, but a schedule testing the *boundary* (a fall of exactly Q) cannot know what the implementation computes as the baseline (previous acknowledged snapshot's file count and bytes — of the snapshot, or of the inventory?). *Which bytes: the snapshot's stored bytes or T28's inventory sums?*
7. **B1.18's "hash over its entries."** The interface corrupts the record file blindly (BF1.13 `mode=corrupt` flips a byte). Whether that produces a hash mismatch depends on the hash's coverage (entries only? whole file? metadata?). A corruption that lands outside the hashed region is not "a copy whose hash does not match," so the injection may be a no-op. *What exactly is covered by the hash?*
8. **"At least every *D*" (T23) vs. B1.7's "within *D*."** The checker runs at least every D, and notices go out within D of the event; under BF1.8 at the checker itself, no bound holds while "R, the checker's host, is down" — but BF1.8 is "a timer does not fire," not "R is down." *Does a frozen checker timer (with R otherwise up) suspend B1.7's bounds or not?* The class rule lists BF1.8 among unavailable-host cells, but T23's checker is a process, not a host.