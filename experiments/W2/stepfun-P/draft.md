# Backup Service Shared Test Interface (BSTI) v1

This document specifies the only artefact that independent implementation teams and formal-modelling teams share besides the contract: a **schedule format**, an **implementation-side contract**, and the **harness obligations** needed to run schedules unchanged against every implementation and every model.

The interface prescribes no backup protocol, no language, and no tooling.  It prescribes only what is strictly required to **inject** the fixed failure model and to **observe** the fixed contract from outside a black-box implementation.

---

## 1. Schedule format

A schedule is a single YAML document.  All times are **logical seconds** (integers) measured from the start of the test.  Durations are integers.  The harness resolves the binding’s hour/day parameters to seconds before running.

### 1.1 Grammar / schema

```yaml
api_version: "test-if/1"
id: string                       # unique schedule id
binding: string                  # e.g. "tupay-v1"; harness resolves parameters
horizon: integer                 # seconds after the last injected event at which
                                 # recoverability is judged and final assertions run
parameters:                      # optional overrides; symbol -> seconds
  I: 86400
  M: 86400
  P: 604800
  H: 129600
  D: 3600
  X: 7200
  Rb: 172800
  G: 345600
  K: 1209600
  Mo: 15552000
  Q: 0.05
  Dmax: 97200
  T: 183600

setup:
  hosts:                         # every role the contract names must appear
    - id: string                 # sandbox name, e.g. "s1"
      role: "S" | "R" | "restore" | "checker" | "channel"
  sources:
    - host: "S"                  # sources live on S
      path: string               # relative path inside S's sandbox
      type: "dir" | "git"
      files:                     # initial content for type "dir"
        - path: string
          content: string        # literal text
      git_refs:                  # initial refs for type "git"
        - name: string           # e.g. "refs/heads/main"
          oid: string
  initial_status_record:         # optional seed for S and R
    runs: [{seq: int, status: string, stage: string, started_at: int, ok_at: int, failed_at: int}]
    marks: [{seq: int, mark: string, at: int, writer: string}]

steps:
  - at: integer                  # master logical time; mutually exclusive with `after`
    after: integer               # seconds after the previous step
    action: "inject" | "modify_source" | "log_reason" | "clear_fault" | "wait" | "noop"
    note: string

    # ---- action: inject -------------------------------------------------
    cell: "BF1.1" | "BF1.2" | "BF1.3" | "BF1.4" | "BF1.5" | "BF1.6" |
          "BF1.7" | "BF1.8" | "BF1.9" | "BF1.10" | "BF1.12" | "BF1.13" |
          "BF1.14"
    target: string               # host id (single-target cells)
    targets: [string]            # host ids (BF1.2 only)
    duration: integer            # virtual seconds; fault auto-clears after this
    restart_after: integer       # BF1.1 only
    seq: integer                 # BF1.3, BF1.12
    seqs: [integer]              # BF1.12
    step: integer                # BF1.6; signed, e.g. +3600 or -86400
    mode: "delete" | "corrupt"   # BF1.13
    capacity_bytes: integer      # BF1.4

    # ---- action: modify_source -----------------------------------------
    path: string                 # source-relative path
    op: "create" | "append" | "rewrite" | "delete" | "rename" | "truncate" |
        "move" | "update_ref"
    to: string                   # destination for rename/move
    content: string
    ref: string                  # for update_ref
    oid: string

    # ---- action: log_reason --------------------------------------------
    text: string                 # written to the binding's logged-reason location

    # ---- action: clear_fault -------------------------------------------
    # uses the same cell/target fields as inject; ends a persistent fault early

assertions:
  - at: integer | "horizon"      # "horizon" means last_event + horizon
    derives: string              # contract clause id, e.g. "B1.17"
    check:
      type: "notice" | "notice_absent" | "run_entry" | "mark" |
            "snapshot_present" | "recoverable" | "manifest" | "pruning" |
            "record_valid"
      # type-specific fields follow; unknown fields are ignored by models
      clause: string             # notice / notice_absent
      event: string              # e.g. "overdue", "failed-run", "damaged"
      snapshot: integer
      cause: string
      arrived_by: integer        # notice
      until: integer             # notice_absent
      seq: integer               # run_entry, mark, snapshot_present, manifest
      status: "started" | "ok" | "failed"
      stage: string
      by: integer                # deadline for the observed state
      mark: "restore-checked" | "restore-failed" | "not restore-checked" |
            "damaged" | "missing"
      writer: string
      present: boolean           # snapshot_present
      contains: [string]         # manifest paths that must be listed
      git_refs: [{name: string, oid: string}]
      kept: [integer]            # pruning
      removed: [integer]
      host: "S" | "R"            # record_valid
```

### 1.2 Complete example schedule (injects BF1.1, BF1.3 and BF1.6)

```yaml
api_version: "test-if/1"
id: "ex-001-crash-corrupt-step"
binding: "tupay-v1"
horizon: 7200                    # judge recoverability 2 h after last event

setup:
  hosts:
    - {id: s1,  role: S}
    - {id: r1,  role: R}
    - {id: rh1, role: restore}
    - {id: chk1, role: checker}
    - {id: chan1, role: channel}
  sources:
    - host: s1
      path: "data"
      type: dir
      files:
        - {path: "a.txt", content: "alpha"}
        - {path: "b.txt", content: "beta"}

steps:
  - at: 0
    action: noop
    note: "implementation may start its first run immediately"

  - at: 900
    action: inject
    cell: BF1.1
    target: s1
    restart_after: 300
    note: "crash S in the middle of a run; relaunch after 5 virtual minutes"

  - at: 1800
    action: inject
    cell: BF1.3
    target: r1
    seq: 1
    note: "silently corrupt bytes inside snapshot 1's payload at R"

  - at: 2700
    action: inject
    cell: BF1.6
    target: r1
    step: 86400
    note: "step R's clock forward 24 h; ages on R are now wrong by that much"

  - at: 3600
    action: modify_source
    path: "data/a.txt"
    op: append
    content: "-gamma"
    note: "append to a.txt; the next run must capture a real version, never a torn write"

assertions:
  - at: 4500
    derives: B1.1
    check:
      type: run_entry
      seq: 1
      status: ok
      by: 4500

  - at: 5400
    derives: B1.12
    check:
      type: mark
      seq: 1
      mark: damaged
      by: 5400

  - at: 5400
    derives: B1.7
    check:
      type: notice
      clause: B1.7
      event: damaged
      snapshot: 1
      arrived_by: 5400

  - at: horizon
    derives: B1.19
    check:
      type: recoverable
      seq: 2
```

---

## 2. Implementation-side contract

An implementation is a black box.  The harness launches it and injects faults.  The implementation must obey the following constraints and **nothing more**.  Each constraint exists only because injection or observation is impossible without it.

### 2.1 Launch and location

* The harness starts **one process per host id** listed in `setup.hosts`.
* Each process receives:
  * `HARNESS_HOST_ID` – the host id (e.g. `s1`).
  * `HARNESS_HOST_ROOT` – absolute path to that host’s sandbox directory.
  * `HARNESS_TOPOLOGY` – absolute path to a JSON file mapping every host id to its role and sandbox root.
* The implementation must discover peers only through `HARNESS_TOPOLOGY`.  It must not use DNS, `/etc/hosts`, or hard-coded machine names.

**Topology JSON (written by the harness):**
```json
{
  "hosts": {
    "s1":  {"role": "S",        "root": "/tmp/bsti/run-42/s1"},
    "r1":  {"role": "R",        "root": "/tmp/bsti/run-42/r1"},
    "rh1": {"role": "restore",  "root": "/tmp/bsti/run-42/rh1"},
    "chk1":{"role": "checker",  "root": "/tmp/bsti/run-42/chk1"},
    "chan1":{"role":"channel",  "root": "/tmp/bsti/run-42/chan1"}
  },
  "parameters": {"I": 86400, "M": 86400, "...": "..."}
}
```

### 2.2 Time (C1)

* The implementation must read the current time from the file `$HARNESS_HOST_ROOT/clock`.
* The file contains a single line: a decimal integer of logical seconds.
* The implementation must **not** read the system clock, `gettimeofday`, or any wall-clock source.
* The implementation must poll `clock` at least once per real second while it is running.

**Why:** the contract measures ages on each host’s own clock, and BF1.6 steps clocks independently.  Only a harness-owned clock file makes virtual time and per-host steps possible while letting a weeks-long schedule finish in minutes.

### 2.3 Sandbox confinement (C2)

* All persistent state (status record, snapshots, caches, working files) must live under `$HARNESS_HOST_ROOT`.
* All cross-host I/O must target paths under the peer’s `root` as given in the topology.
* The implementation must not write outside its own sandbox, except to read source trees under S’s sandbox.

**Why:** the harness must be able to find, corrupt, delete, or observe every byte the implementation touches, without root and without knowing the implementation’s internal layout.

### 2.4 Observable artefacts (C3)

The implementation must expose the following in the exact locations and formats below.  All files must be updated by **atomic rename** (write to a temp name, then `rename`) so the harness never sees a torn read.

#### 2.4.1 Status record
* Path: `$HARNESS_HOST_ROOT/status-record.json` on **S** and on **R**.
* Format:
```json
{
  "runs": [
    {"seq": 1, "status": "started", "stage": "unknown", "started_at": 0},
    {"seq": 1, "status": "ok",      "stage": "done",    "ok_at": 300},
    {"seq": 2, "status": "failed",  "stage": "capture", "failed_at": 900}
  ],
  "marks": [
    {"seq": 1, "mark": "restore-checked", "at": 1200, "writer": "rh1"},
    {"seq": 1, "mark": "damaged",         "at": 2400, "writer": "r1"}
  ],
  "hash": "sha256:..."
}
```
* `hash` is the hex SHA-256 of the canonical JSON serialisation of `runs` followed by `marks` (arrays sorted by `seq`, then by time).  The implementation must rewrite `hash` at every update.
* A missing file or a failing hash means the copy is lost (B1.18).

#### 2.4.2 Snapshots
* Path: `$HARNESS_HOST_ROOT/snapshots/<seq>/` on **R**.
* Each directory must contain `manifest.json`:
```json
{
  "seq": 1,
  "source_inventory": ["data/a.txt", "data/b.txt"],
  "files": [
    {"path": "data/a.txt", "sha256": "..."},
    {"path": "data/b.txt", "sha256": "..."}
  ],
  "git_refs": [
    {"name": "refs/heads/main", "oid": "abc123"}
  ]
}
```
* Snapshot payload bytes may be stored in any format or sub-path inside the snapshot directory.

#### 2.4.3 Notice channel record
* Path: `$HARNESS_HOST_ROOT/notices/<uuid>.json` on the **channel** host.
* One file per notice, written when the notice **reaches** the channel:
```json
{
  "clause": "B1.7",
  "event": "overdue",
  "snapshot": 70,
  "cause": "restore host suspended",
  "arrived_at": 123456
}
```
* While the channel is down (BF1.7), undelivered notices must be queued in `$HARNESS_HOST_ROOT/pending-notices/<uuid>.json` with the same fields plus `queued_at`.

#### 2.4.4 Process id
* Path: `$HARNESS_HOST_ROOT/pid` containing the decimal PID of the main process.
* If the implementation forks children that must be killed for BF1.1, it must also maintain `$HARNESS_HOST_ROOT/pids/<name>` for each.

**Why:** assertions need to see run entries, marks, manifests, and notices without instrumenting the implementation.  Atomic rename prevents the harness from observing half-written state.

### 2.5 Harness control files (C4)

Before performing the corresponding action, the implementation must check these files and behave as described.  The files are created and removed by the harness.

| File (under `$HARNESS_HOST_ROOT`) | Created for | Required behaviour |
|---|---|---|
| `partitions/<peer_id>` (content `blocked`) | BF1.2 | All I/O to that peer must fail as if the peer were unreachable. |
| `capacity_bytes` (integer) | BF1.4 | Total bytes written under this sandbox must not exceed the value; further writes must fail with a disk-full error. |
| `channel_down` (empty) | BF1.7 | Notice delivery to the channel must fail; notices go to `pending-notices/`. |
| `timers_disabled` (empty) | BF1.8 | Timer-driven actions must not fire. |

**Why:** the test runs on one machine without root.  These files are the only portable, implementation-agnostic way to inject partition, disk-full, channel outage, and timer failure deterministically.

### 2.6 Prohibitions (C5–C7)

* **C5** – No system clock, no randomness seeded from wall time, no real network names.  All non-determinism must come from the harness-controlled inputs above.
* **C6** – No privileged operations: no binding to ports < 1024, no `setuid`, no raw sockets, no mounting.
* **C7** – No reliance on process count: the harness may run all hosts as separate processes or as one process; the implementation must work either way as long as the sandbox and control-file contracts are honoured.

---

## 3. Harness obligations

The harness is the reference runner for implementations.  It must:

1. **Resolve parameters** from the named binding (or schedule overrides) into seconds.
2. **Create sandboxes** for every host, write `topology.json`, initialise every `clock` to `0`, and materialise `setup.sources`.
3. **Launch** one process per host with the environment in §2.1.
4. **Advance master time** in ticks (default 60 virtual seconds).  At each tick it writes the current per-host clock to every `clock` file, then sleeps a short real interval (default 50 ms) to let implementations react.
5. **Maintain per-host clock offsets.**  Host clock = master time + `offset[host]`.  BF1.6 adds `step` to that host’s offset immediately.
6. **Execute steps** in master-time order:
   * `inject` – perform the fault action in §4.
   * `modify_source` – apply the file operation inside S’s source tree.
   * `log_reason` – append the text to the binding’s logged-reason location.
   * `clear_fault` – undo a persistent fault early.
   * `wait` / `noop` – advance time only.
7. **Observe continuously.**  After every tick (and immediately after any fault that changes state) the harness reads the observable artefacts and appends events to `observations.jsonl`:
   ```json
   {"t": 1800, "host_clock": {"r1": 1800}, "kind": "mark", "data": {"seq":1,"mark":"damaged","at":1800,"writer":"r1"}}
   {"t": 1800, "host_clock": {"r1": 1800}, "kind": "notice", "data": {"clause":"B1.7","event":"damaged","snapshot":1,"arrived_at":1800}}
   {"t": 2700, "host_clock": {"r1": 111600}, "kind": "clock_step", "data": {"host":"r1","old":2700,"new":111600}}
   ```
   Observation kinds: `run_entry`, `mark`, `snapshot_present`, `snapshot_absent`, `notice`, `pending_notice`, `record_lost`, `record_rebuilt`, `fault_injected`, `fault_cleared`, `clock_step`.
8. **Judge the horizon.**  Let `T_last` be the master time of the last step whose action is `inject` or `modify_source`.  At master time `T_last + horizon` the harness:
   * reads the final status record and snapshot list;
   * determines, for every sequence number, whether it is **recoverable** (protected, latest restore check passed, not marked damaged or missing since that check);
   * evaluates every assertion whose `at` is `horizon` or earlier.
9. **Emit a report** mapping each assertion id to `PASS`, `FAIL`, or `NOT-EXPRESSED` (models only), with the observation lines used as evidence.
10. **Tear down** all processes and sandboxes.

---

## 4. Fault injection reference

Every BF1 cell is injectable by the harness alone.  “Ends” describes how the fault stops affecting the system under test.

| Cell | Injection mechanism | Ends when |
|---|---|---|
| **BF1.1** crash | `SIGKILL` to the process group of `target`. | Harness relaunches the process after `restart_after` virtual seconds. |
| **BF1.2** partition | Harness writes `partitions/<peer>` = `blocked` in both hosts’ sandboxes. | After `duration`, or on `clear_fault`, the harness removes the files. |
| **BF1.3** corrupt bytes | Harness opens `snapshots/<seq>/` under R and flips bits at a random offset in the payload. | Persistent; only a re-verify or restore check can detect it. |
| **BF1.4** disk full | Harness writes `capacity_bytes` under the target sandbox. | On `clear_fault` or a later `inject` with a larger value. |
| **BF1.5** concurrent source change | `modify_source` steps scheduled during a run window. | The file operation itself is the fault; it persists as source state. |
| **BF1.6** clock step | Harness adds `step` to the target’s clock offset and rewrites `clock`. | Persistent; the offset remains for the rest of the schedule. |
| **BF1.7** channel down | Harness creates `channel_down` in the channel sandbox. | After `duration`, or on `clear_fault`, the harness removes the file. |
| **BF1.8** timer fails | Harness creates `timers_disabled` in the target sandbox. | After `duration`, or on `clear_fault`, the harness removes the file. |
| **BF1.9** source moved/emptied | `modify_source` with `op: truncate` or `op: move`. | Persistent source state. |
| **BF1.10** R reimaged | Harness deletes `snapshots/*` and `status-record.json` under R. | Persistent; the implementation must rebuild per B1.18. |
| **BF1.12** snapshots lost | Harness deletes `snapshots/<seqs>` under R. | Persistent. |
| **BF1.13** record lost/corrupt | Harness deletes or bit-flips `status-record.json` on S, R, or both (`mode`). | Persistent; recovery is the implementation’s job. |
| **BF1.14** host suspended | `SIGSTOP` to the process group of `target`. | `SIGCONT` after `duration`. |

---

## 5. Assertions and the scoring horizon

* Every assertion carries `derives: <clause-id>`.  The harness never invents clause ids; it only checks the predicate.
* The **scoring horizon** is `T_last + horizon`.  At that master time the harness freezes observation and evaluates all assertions with `at: horizon` plus any earlier assertions that have not yet been evaluated.
* `recoverable` assertions are evaluated against the B1.19 definition: a protected snapshot whose latest restore check passed and which has not been marked damaged or missing since.

---

## 6. Models

A formal model ships its own **schedule runner**.  The runner must:

1. **Accept the full YAML syntax** of §1, including `setup`, every `action`, and every `check.type`.  A model may not reject a schedule because it uses a feature the model does not simulate.
2. **Simulate master time and per-host clock offsets** exactly as the harness does.
3. **Apply `modify_source` and `log_reason`** to its abstract source state.
4. **Report inexpressibility** rather than failing.  When a step, injection, or observation cannot be expressed in the model’s state space, the runner emits:
   ```json
   {"assertion_id": "ex-001/B1.12", "status": "unsupported",
    "reason": "model abstracts snapshot payloads as tokens; BF1.3 byte corruption is not representable"}
   ```
   The harness treats `unsupported` as *model cannot express*, never as a contract violation.
5. **Emit the same report shape** as the harness (`PASS` / `FAIL` / `unsupported` with evidence) so results are comparable.

A model must accept at minimum: host/role setup, source initialisation, logical time, all BF1 cells as *events* (even if their effect is abstract), and all assertion types as *queries* over the model state.

---

## 7. OPEN CHOICES

Every point where the contract or binding left the interface open, the option chosen, and the alternatives rejected.

| # | Decision point | Options seen | Choice and rationale |
|---|---|---|
| 1 | **Time delivery** | (a) environment variable set once; (b) Unix socket; (c) file polled by implementation. | **(c) `clock` file.** A socket would prescribe a protocol; an env var cannot express steps. A file is protocol-free, survives process restarts, and is trivially observable. |
| 2 | **Virtual-time pacing** | (a) event-driven (advance only when implementation is idle); (b) fixed-tick polling. | **(b) Fixed 60 s ticks with a 50 ms real sleep.** Detecting quiescence is impossible without instrumenting the implementation. Polling is the only black-box-compatible way to run weeks in minutes. |
| 3 | **Clock-step representation** | (a) rewrite a single global clock; (b) per-host offset added to master time. | **(b) Per-host offset.** The contract measures ages on each host’s own clock; a single global clock cannot express BF1.6. |
| 4 | **Host identity in a test** | (a) separate containers/VMs; (b) sandbox directories with a topology file. | **(b) Sandboxes.** Containers require root or user-namespace support that is not portable. Directories work without root and let the harness inspect state directly. |
| 5 | **Partition injection (BF1.2)** | (a) `iptables` / network namespaces; (b) `chmod` on peer sandboxes; (c) `partitions/<peer>` control file. | **(c) Control file.** `iptables` needs root; `chmod` is defeated by open file descriptors and cached paths. A control file is deterministic and requires only a documented pre-I/O check. |
| 6 | **Disk-full injection (BF1.4)** | (a) `ulimit -f`; (b) fill a loopback device; (c) `capacity_bytes` control file. | **(c) Control file.** `ulimit -f` kills the process with `SIGXFSZ` rather than returning `ENOSPC`; loopback devices need root. A capacity limit is observable and testable. |
| 7 | **Notice channel model** | (a) single append-only log; (b) directory of per-notice JSON files. | **(b) Directory of files.** Atomic per-notice writes avoid torn reads and make “when it arrived” unambiguous. |
| 8 | **Status-record format** | (a) implementation-defined binary; (b) line-oriented text; (c) JSON with explicit hash field. | **(c) JSON.** The contract already specifies a hash over entries; JSON makes the hash input canonical and the record externally readable. |
| 9 | **Snapshot manifest format** | (a) implementation-defined; (b) JSON with `source_inventory`, `files`, `git_refs`. | **(b) JSON.** B1.2 and B1.17 assertions need to compare inventory, file hashes, and git refs from outside. |
| 10 | **Assertion language** | (a) arbitrary predicate calculus; (b) fixed structured templates. | **(b) Structured templates.** A formal model can accept a closed set of query types far more easily than an open expression language, satisfying requirement 6. |
| 11 | **Scoring horizon semantics** | (a) wall-clock timeout; (b) fixed offset after last injected event. | **(b) Fixed offset.** The prompt requires a *fixed* time after the last injected event; wall-clock would make results non-deterministic. |
| 12 | **Crash target granularity** | (a) kill by host role; (b) kill by process group of the host’s main PID. | **(b) Process group.** An implementation may fork workers; killing the group guarantees BF1.1 without knowing the process tree. |
| 13 | **Model inexpressibility reporting** | (a) abort the schedule; (b) skip silently; (c) explicit `unsupported` status. | **(c) Explicit status.** Silent skipping would hide coverage gaps; aborting would prevent partial validation. |

---

## 8. CONTRACT QUESTIONS

Places where the contract text was too ambiguous to design injection or observation without guessing.  The quoted text is reproduced verbatim; these are **not** resolved here.

1. **B1.8 cleanup scope.**  
   > “At the start of each check, the restore host removes anything left by a check that crashed.”  
   The contract does not define the restore host’s working directory or distinguish crash debris from legitimate snapshot data.  The harness cannot tell whether a file left in the restore sandbox is debris that *should* have been removed or a new artefact.

2. **B1.16 queue location.**  
   > “While the channel cannot be reached, the sender keeps the notice where the checker reads, and delivers it within D of the channel coming back.”  
   “Where the checker reads” is not named.  The interface had to invent `pending-notices/`; the contract should state whether that location is observable or implementation-private.

3. **B1.18 merge semantics.**  
   > “if both copies are intact but disagree, run entries follow S’s copy and marks follow R’s copy, every disagreement is reported under B1.7, and both copies are kept.”  
   It is unclear whether R’s copy is *rewritten* to match S for run entries, or merely kept aside unchanged.  This affects whether the harness should expect `status-record.json` on R to change after a merge.

4. **B1.19 evidence standard.**  
   > “Only a passing restore check is evidence of that.”  
   The harness can observe a `restore-checked` mark, but the contract does not say whether the harness may treat that mark as sufficient for a `recoverable` assertion, or whether it must independently re-run the restore procedure at the horizon.

5. **BF1.6 error reporting channel.**  
   > “The tests inject steps of ±1 h and ±24 h, and the error is reported.”  
   The contract does not say *where* the error is reported (notice under B1.7? a mark? a log entry?) or which clause the report names, so the interface cannot specify an assertion template for it.

6. **B1.4 monthly retention edge case.**  
   > “the first daily snapshot of each month for Mo months.”  
   If the first UTC day of a month has no acknowledged snapshot, it is undefined whether the first daily snapshot of that month is the first day that *does* have one, or whether the month is simply skipped.

7. **B1.5 detector interface.**  
   > “Each run scans the material that is new since the previous acknowledged snapshot … with the binding’s credential detector.”  
   The detector is binding-specific.  A generic harness cannot construct a guaranteed positive test case for B1.5 without knowing the detector’s patterns; the interface can only modify sources blindly.

8. **B1.15 logged-reason location.**  
   > “A logged reason is an entry in the record the binding names, written before the run, that names the source tree and the change.”  
   The binding names `docs/seed-log.md`, but the contract does not specify a machine-readable format.  The harness cannot reliably determine whether a reason was logged before a given run.

9. **EX1.6 / binding channel dependency.**  
   > “Its record is on S, so EX1.6 applies to this binding.”  
   If the notice channel’s record lives on S and S is down, the contract excludes the scenario, but the interface still needs to know whether the channel host sandbox is readable/writable by the checker when S is partitioned.  The exclusion does not say whether the channel is *observable* while S is down.

10. **B1.12 re-verification observability.**  
    > “R verifies every protected snapshot again within P of its previous verification, without needing S.”  
    The contract requires the act of re-verification but names no observable artefact for “a verification happened at time T”.  The interface can only infer it from a later `damaged` mark or from an implementation-specific log, neither of which the contract mandates.