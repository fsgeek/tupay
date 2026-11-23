# Shared Test Interface for the Verified Backup Contract  
**Interface name:** VBTI (Verified Backup Test Interface), version 1  
**Applies to:** contract-F.md (draft 7) and binding-tupay.md (v1)

---

## 1. What this interface is

VBTI is the only artifact shared by implementation teams and model authors besides the contract and binding. It defines:

1. A **schedule format** (YAML) that scripts sources, fault injections, and assertions.
2. An **implementation-side contract**: the minimum set of things an implementation must expose or obey so that one harness can drive it.
3. The **harness’s obligations**: what the harness must build, inject, observe, and score.
4. **OPEN CHOICES**: every place the contract or binding left the design open, the options considered, and the option chosen.
5. **CONTRACT QUESTIONS**: places where the contract text is too unclear to design injection or observation; these are quoted, not resolved.

The interface prescribes **no service protocol and no tooling**. Where it constrains an implementation, the constraint is the minimum required for injection or observation, and the reason is stated.

---

## 2. Schedule format

A schedule is a single YAML document. All times are **virtual**. All durations use the contract’s units: `m` (minutes), `h` (hours), `d` (= 24 h). A schedule covering weeks runs in minutes because the harness advances virtual time, not real time.

### 2.1 Grammar

```ebnf
schedule    := header setup steps
header      := "id:" string
               "binding:" string
               "parameters:" param_map
               "horizon:" duration
param_map   := "I:" duration "M:" duration "P:" duration "H:" duration
               "D:" duration "X:" duration "Rb:" duration "G:" duration
               "K:" duration "Mo:" integer "Q:" float
setup       := "setup:" "sources:" source_list ["seed:" seed_spec]
source_list := { source_spec }
source_spec := ("path:" string "content:" string)
             | ("git:" string "refs:" oid_map)
oid_map     := { ref_name ":" oid }
seed_spec   := "snapshots:" int_list "status_record:" string
steps       := { step }
step        := "at:" time (inject | mutate | assert)
time        := duration            (* relative to virtual epoch, e.g. "0h", "24h" *)
inject      := "inject:" "cell:" cell_id "target:" host
               ["duration:" duration]
               ["after:" event_trigger]
               ["params:" inject_params]
cell_id     := "BF1.1" | "BF1.2" | "BF1.3" | "BF1.4" | "BF1.5"
             | "BF1.6" | "BF1.7" | "BF1.8" | "BF1.9" | "BF1.10"
             | "BF1.12" | "BF1.13" | "BF1.14"
host        := "S" | "R" | "restore-host" | "freshness-checker" | "notice-channel"
event_trigger := "kind:" ("mark" | "notice" | "run")
                 "seq:" integer
                 ["mark:" mark_type]
                 ["clause:" string]
mark_type   := "restore-checked" | "restore-failed" | "not restore-checked"
             | "damaged" | "missing"
inject_params := (* cell-specific; see §2.3 *)
mutate      := "mutate:" "target:" "S" "op:" mutate_op
mutate_op   := ("write" "path:" string "content:" string)
             | ("delete" "path:" string)
             | ("truncate" "path:" string "bytes:" integer)
             | ("git-set" "repo:" string "ref:" string "oid:" string)
assert      := "assert:" "derives:" clause_id "type:" assert_type
               "subject:" subject_map "condition:" condition
               ["by:" time]
clause_id   := "B1." integer | "T" integer | "BF1." integer | "I-B1." integer
assert_type := "notice" | "mark" | "state" | "ordering" | "absence" | "count"
subject_map := { string ":" value }
condition   := string | condition_map
condition_map := { string ":" value }
```

**Scoring horizon.** `horizon` is a duration added to the timestamp of the **last step** in the schedule. The harness advances virtual time to that sum, freezes observations, and evaluates every assertion whose `by` is `horizon` (or earlier). Assertions with an explicit `by` earlier than the horizon are evaluated at that time.

### 2.2 Complete example schedule

The example below injects **BF1.6** (clock step at S) and **BF1.3** (silent corruption at R), then asserts the consequences under B1.12, B1.7, and T5.

```yaml
id: ex-corruption-and-clock-step
binding: tupay-v1
parameters:
  I: 24h
  M: 1d
  P: 7d
  H: 36h
  D: 1h
  X: 2h
  Rb: 2d
  G: 96h
  K: 14d
  Mo: 6
  Q: 0.05
horizon: 8d

setup:
  sources:
    - path: tupay-homes/a/t.jsonl
      content: "line1\n"
    - path: tupay-private/notes.txt
      content: "hello\n"
  seed:
    snapshots: [1]
    status_record: seed-record.json

steps:
  # --- BF1.6: clock step at S ---
  - at: "0h"
    inject:
      cell: BF1.6
      target: S
      params:
        step: +24h

  # --- BF1.3: silent corruption of one byte in snapshot 2 at R ---
  # Fires as soon as the harness observes the ok mark for seq 2.
  - at: "24h"
    inject:
      cell: BF1.3
      target: R
      after:
        kind: mark
        seq: 2
        mark: restore-checked
      params:
        seq: 2
        path: "snapshots/2/tupay-homes/a/t.jsonl"
        offset: 0
        bytes: "ff"

  # --- Assertions ---
  # B1.12: the corrupted snapshot must be marked damaged.
  - at: "24h"
    assert:
      derives: B1.12
      type: mark
      subject: {seq: 2}
      condition: damaged
      by: horizon

  # B1.7: a notice naming B1.12 must reach the channel within D of the damaged mark.
  - at: "24h"
    assert:
      derives: B1.7
      type: notice
      subject: {clause: "B1.12"}
      condition:
        within: 1h
        of: {kind: mark, seq: 2, mark: damaged}
      by: horizon

  # T5: sequence numbers order runs; the clock step must not reorder them.
  - at: "24h"
    assert:
      derives: T5
      type: ordering
      subject: {kind: sequence}
      condition: "strictly increasing across the injected clock step"
      by: horizon
```

**Reading the example.** The harness starts all hosts at virtual `0h`. It immediately steps S’s clock forward by 24 h. It waits until snapshot 2 is restore-checked, flips one byte in snapshot 2’s payload at R, then advances to the scoring horizon (`24h + 8d = 9d`). At the horizon it checks that snapshot 2 carries a `damaged` mark, that a notice naming `B1.12` arrived within 1 h of that mark, and that run sequence numbers never decreased.

### 2.3 Cell-specific `inject.params`

| Cell | Required params | Meaning |
|------|----------------|---------|
| BF1.1 | `stage` (optional string) | Kill the target process with `SIGKILL`. If `after` is given, fire when the observed event occurs; otherwise at `at`. The harness restarts the process immediately with the same environment. |
| BF1.2 | `peer` (host name) | Break the symlink from `target` to `peer` for `duration` (or until healed by a later `BF1.2` with `duration: 0`). |
| BF1.3 | `seq`, `path`, `offset`, `bytes` (hex) | Overwrite `bytes` at `offset` in the file `path` under `R/snapshots/<seq>/`. |
| BF1.4 | `path` (optional) | Apply `RLIMIT_FSIZE` to the target process. If `path` is given, the harness also creates a sparse file of the limit size in the target’s state dir. |
| BF1.5 | — | No params; the harness performs the `mutate` steps interleaved in the schedule. |
| BF1.6 | `step` (signed duration) | Add `step` to the target’s clock file. |
| BF1.7 | — | Mark the notice channel unavailable. The harness stops moving files from the outbox to the channel record. |
| BF1.8 | `duration` | `SIGSTOP` the target for `duration` of virtual time, then `SIGCONT`. |
| BF1.9 | — | No params; expressed as `mutate` steps (`truncate`, `delete`). |
| BF1.10 | — | Recursively delete everything under `R/` except the harness’s own bookkeeping. |
| BF1.12 | `seqs` (list of int) | Delete `R/snapshots/<seq>/` for each seq. |
| BF1.13 | `copies` (list of `S`, `R`, `both`) | Delete or corrupt the local status record file(s). Corruption flips one byte. |
| BF1.14 | `duration` | `SIGSTOP` the target for `duration`, then `SIGCONT`. |

---

## 3. Implementation-side contract

An implementation is a set of processes. The harness starts each process in the foreground with one environment variable: `VBTI_ENV`, pointing to a JSON file. The implementation **must** read that file and obey the following. Nothing else is prescribed.

### 3.1 Environment file

```json
{
  "role": "S",
  "clock_file": "/vt/s/clock",
  "state_dir": "/vt/s",
  "sources": ["/vt/s/src/tupay-homes", "/vt/s/src/tupay-private"],
  "caches": ["/vt/s/src/tupay-homes/.cache"],
  "peer_r": "/vt/s/peer-r",
  "notice_outbox": "/vt/notice/outbox",
  "status_view_dir": "/vt/r/status-view",
  "local_status_record": "/vt/s/status-record.bin"
}
```

Fields by role:

| Field | S | R | restore-host | freshness-checker |
|-------|---|----|----|----|
| `role` | ✔ | ✔ | ✔ | ✔ |
| `clock_file` | ✔ | ✔ | ✔ | ✔ |
| `state_dir` | ✔ | ✔ | ✔ | ✔ |
| `sources`, `caches` | ✔ | — | — | — |
| `peer_r` | ✔ | — | ✔ | — |
| `notice_outbox` | ✔ | ✔ | ✔ | ✔ |
| `status_view_dir` | ✔ | ✔ | ✔ | ✔ |
| `local_status_record` | ✔ | ✔ | — | — |

### 3.2 Obligations

1. **Virtual clock.** The implementation must read the current time for its host from `clock_file`. The file contains one line: integer nanoseconds since the virtual epoch. The implementation must **not** call `time()`, `clock_gettime()`, or read `/proc/uptime` for any contract purpose.  
   *Why:* weeks must run in minutes, and BF1.6 must step each host’s clock independently (T12).

2. **Peer access via symlinks.** All inter-host file access must go through the paths in the environment (`peer_r`). The harness injects BF1.2 by unlinking these symlinks. The implementation must treat `ENOENT` on a peer path as “peer unavailable” and must not cache directory handles across such errors.  
   *Why:* on a single unprivileged machine, symlink removal is the only way to partition same-user processes without a control protocol.

3. **Restore-host isolation.** The restore host must not read any path under S’s source tree. In the test, S’s sources are not present in the restore host’s environment; the implementation must not search parent directories or use absolute paths outside `state_dir` and `peer_r`.  
   *Why:* T4 requires no path to S. Without root, the harness cannot enforce this with permissions; the implementation must confine itself.

4. **Notice outbox.** Every notice the implementation sends must be written as a single JSON file into `notice_outbox/`. Filename: `<uuid>.json`. Content:
   ```json
   {"clause":"B1.7","text":"...","event_time":123456789,"host":"S"}
   ```
   The freshness checker must also scan `notice_outbox/` for notices that have not yet reached the channel (B1.16 second part).  
   *Why:* the harness must observe notices and inject BF1.7 by withholding delivery.

5. **Status-record view.** The implementation must mirror every status-record entry into `status_view_dir/` as a separate JSON file named `<seq>-<type>-<nanotime>.json`. Two entry shapes:
   ```json
   {"type":"run","seq":42,"state":"ok","stage":"unknown","times":{"started":100,"end":200},"host":"S"}
   {"type":"mark","seq":42,"mark":"restore-checked","time":300,"writing_host":"restore-host"}
   ```
   S writes run entries here after each run (as part of copying the record to R). The freshness checker, R’s re-verification, and the restore host write marks here. S never writes a mark (T15).  
   *Why:* teams will choose different on-disk formats; the harness needs one observable format.

6. **Local status record.** S and R must each keep their own copy of the status record at `local_status_record`. The format is the implementation’s choice, but B1.18’s hash must be computed over it. The harness may delete or corrupt this file for BF1.13.  
   *Why:* B1.18 is about the service’s own copies; the view is only for observation.

7. **Foreground process.** Each process must run in the foreground and exit when killed. The harness restarts it with the same `VBTI_ENV` after BF1.1 or BF1.14.  
   *Why:* the harness must be able to inject crashes and suspensions deterministically.

8. **Snapshot layout.** Snapshots must live under `state_dir/snapshots/<seq>/`. The manifest must be stored with the snapshot (T7c); its format is free.  
   *Why:* the harness needs a stable path to corrupt bytes (BF1.3) or delete snapshots (BF1.12).

9. **No real time.** As per obligation 1.

---

## 4. Harness obligations

The harness is a single unprivileged process tree on one machine.

### 4.1 Construction

1. Create a test root with one directory per host: `s/`, `r/`, `restore/`, `checker/`, `notice/`.
2. Populate `s/src/` from `setup.sources`. Populate `r/snapshots/` and seed status records from `setup.seed`.
3. Create symlinks: `s/peer-r → r`, `restore/peer-r → r`.
4. Write one `VBTI_ENV` JSON per process.
5. Initialize each `clock_file` to `0`.
6. Start processes in this order: R, freshness-checker, S, restore-host. Implementations must tolerate peers that are not yet up (BF1.2 at startup).

### 4.2 Virtual-time loop

The harness advances virtual time in increments of **1 minute** (or the remaining distance to the next step, whichever is smaller). After each increment it writes the new nanotime to every `clock_file`. A real-time sleep of 5 ms between increments lets processes observe the change while keeping a 9-day schedule near 1–2 minutes of real time.

### 4.3 Injection engine

- **Time-based:** at the step’s `at`, apply the injection.
- **Event-based:** poll `status_view_dir/` and `notice/outbox/` every loop iteration. When the `after` trigger is seen, apply the injection and mark it consumed.
- **Active injections:** maintain a table of ongoing effects (broken symlinks, stopped processes, unavailable notice channel, rlimits). Re-apply them each loop iteration until their `duration` expires or an explicit heal step appears.

### 4.4 Notice channel

The harness owns the authoritative channel record at `notice/channel-record.jsonl`. Each loop iteration:

1. If BF1.7 is **not** active, move every file from `notice/outbox/` to the channel record, appending a line:
   ```json
   {"arrival_time":<virtual ns>,"clause":"B1.7","text":"...","event_time":<ns>,"host":"S"}
   ```
2. If BF1.7 **is** active, leave files in the outbox. The freshness checker is expected to read them there (B1.16).

### 4.5 Observation store

The harness keeps an in-memory (and on-disk) log of:

- Every status-view entry, with the virtual time it was first seen.
- Every notice arrival, with the virtual time.
- Every source mutation applied.
- Every injection applied, with start/end virtual times.

### 4.6 Scoring

At the scoring horizon (`last step time + horizon`):

1. Stop advancing time.
2. Snapshot the observation store.
3. Evaluate each assertion:
   - `notice`: find a channel-record entry whose `clause` matches `subject.clause` and whose `arrival_time` is within `condition.within` of the referenced event. If `of` is omitted, any arrival by `by` passes.
   - `mark`: find the latest mark for `subject.seq`; compare to `condition`.
   - `ordering`: check the sequence of run entries.
   - `state` / `absence` / `count`: evaluate against the observation snapshot.
4. Emit a report mapping each assertion’s `derives` tag to **PASS**, **FAIL**, or **UNOBSERVED**.

### 4.7 Model feeding

The harness serializes the parsed schedule to a normalized JSON document and writes it to `model-schedule.json`. A model’s schedule runner reads that file. The model may reply with:

```json
{"status":"ok"}
{"status":"cannot-express","step":3,"reason":"byte-level corruption not modeled"}
```

The harness records `cannot-express` and does not treat it as a failure.

---

## 5. OPEN CHOICES

Every point where the contract or binding left the interface open, the options seen, and the option chosen.

1. **Virtual-time transport**  
   *Options:* (a) a Unix socket serving time on request; (b) an environment variable refreshed by signal; (c) a plain file rewritten by atomic rename.  
   *Chose:* (c). It needs no library, no protocol, and works with any language. Atomic rename prevents torn reads.

2. **Clock-step granularity**  
   *Options:* (a) one global clock with per-host offsets; (b) one independent clock file per host.  
   *Chose:* (b). T12 says ages are measured on the clock of the host that measures them, and BF1.6 steps “any host.” Independent files make that literal.

3. **Host isolation without root**  
   *Options:* (a) separate OS users; (b) user namespaces / rootless containers; (c) chroot; (d) disjoint directory trees plus symlinks.  
   *Chose:* (d). (a) needs root. (b) and (c) prescribe tooling and are not universally available. Disjoint trees approximate T4 closely enough for a test, and the implementation-side obligation to stay in its tree closes the gap.

4. **Partition injection (BF1.2)**  
   *Options:* (a) iptables / network namespaces (root); (b) a userspace proxy (tooling); (c) a control socket the implementation must honor (cooperation); (d) breaking the peer symlink.  
   *Chose:* (d). It requires only that the implementation use the provided path, which is already needed for observation. No extra protocol is introduced.

5. **Notice-channel unavailability (BF1.7)**  
   *Options:* (a) make the channel file read-only (bypassable by same user); (b) delete the channel path; (c) a harness-managed outbox that is withheld.  
   *Chose:* (c). B1.16 already requires the sender to record notices “where the freshness checker reads” while the channel is down. The outbox is that place, and the harness controls delivery.

6. **Status-record observation format**  
   *Options:* (a) let each team choose and write a parser per team; (b) require a `dump` subcommand; (c) a canonical append-only view directory.  
   *Chose:* (c). One harness cannot parse N formats. A `dump` command is cooperation beyond injection/observation. The view directory is write-only for the implementation and read-only for the harness.

7. **Assertion evaluation model**  
   *Options:* (a) continuous monitoring during the run; (b) snapshot at the scoring horizon only.  
   *Chose:* (b). Continuous monitoring makes schedules non-deterministic across implementations. A horizon snapshot is reproducible and matches the prompt’s “fixed time after its last injected event.”

8. **Event-triggered injection**  
   *Options:* (a) implementation callbacks to the harness; (b) harness polling of observation logs.  
   *Chose:* (b). Polling needs no cooperation. The 1-minute loop granularity is fine because all contract deadlines are ≥ 1 h.

9. **Full-disk injection (BF1.4)**  
   *Options:* (a) fill the real disk (dangerous); (b) mount a small tmpfs (root); (c) `RLIMIT_FSIZE`.  
   *Chose:* (c). It is safe, unprivileged, and produces genuine `ENOSPC` / `EFBIG` errors without prescribing a filesystem tool to the implementation.

10. **Timer failure (BF1.8)**  
    *Options:* (a) skip virtual-time advances for one host; (b) `SIGSTOP` the process.  
    *Chose:* (b). Skipping advances would desynchronize the host’s clock from the schedule. `SIGSTOP` leaves the clock correct but prevents the process from acting, which is what “a timer does not fire” means observably.

11. **Crash targeting (BF1.1)**  
    *Options:* (a) kill by PID; (b) kill by role plus optional stage trigger.  
    *Chose:* (b). PIDs are unstable across restarts. Role + event trigger expresses “crash during a restore check” without knowing internals.

12. **Parameter values in the schedule**  
    *Options:* (a) let a schedule override binding values; (b) restate them read-only.  
    *Chose:* (b). The binding fixes values; a schedule that changed them would test a different contract. Restating them lets a model runner see the numbers without a separate binding file.

13. **Model cannot-express reporting**  
    *Options:* (a) require models to implement every injection; (b) allow a structured refusal.  
    *Chose:* (b). A TLA+ model cannot flip a byte at an offset. The interface must accept that a model covers a subset.

14. **Scoring horizon base**  
    *Options:* (a) absolute virtual time; (b) offset from the last step.  
    *Chose:* (b). Schedules are written relative to their own events; an absolute base would break when a step is inserted.

15. **Source mutation vocabulary**  
    *Options:* (a) raw shell commands; (b) structured operations (`write`, `delete`, `truncate`, `git-set`).  
    *Chose:* (b). Shell prescribes tooling. Structured ops are abstract enough for a model and concrete enough for the harness.

---

## 6. CONTRACT QUESTIONS

These are places where the contract text does not determine an interface design. They are quoted, not resolved.

1. **Status-record entry schema (T15).**  
   *Quote:* “a **run entry**: sequence number; *started*, *ok* or *failed*; stage, where *unknown* is a valid stage; times;”  
   *Question:* What are the exact field names and types for `times`? Is it one timestamp or a start/end pair? Is the list ordered, and if so by what? Without this, two teams may emit different JSON for the same logical entry, and the harness cannot compare them.

2. **Notice clause naming (T16).**  
   *Quote:* “a message on the notice channel (T29) that names its clause.”  
   *Question:* Must the notice contain the literal string `B1.7`, or is a structured enum acceptable? Are other fields (timestamp, host) mandatory? The interface assumes a `clause` string, but the contract does not say whether free text is allowed.

3. **Status-record hash algorithm (B1.18).**  
   *Quote:* “Each copy of the status record carries a hash over its entries, rewritten at each update.”  
   *Question:* Which hash algorithm, and what is the canonical serialization of the entries being hashed? BF1.13 injection must corrupt bytes in a way the hash detects; if teams choose different algorithms or serializations, the harness cannot predict detectability.

4. **Location of the record while the channel is down (B1.16).**  
   *Quote:* “While the notice channel cannot be reached, the sender records the notice where the freshness checker reads, and delivers it within *D* of the notice channel becoming reachable.”  
   *Question:* Is “where the freshness checker reads” a path named by the binding, a well-known location, or an implementation choice? The interface assumes an outbox, but the contract does not name it.

5. **Both status-record copies lost (T5a).**  
   *Quote:* “If every record and snapshot that carries a number is lost, the contract makes no claim about that number.”  
   *Question:* In a BF1.13 test that destroys both copies, what sequence number should the next run use? The contract explicitly makes no claim, so no assertion can be written; the interface can only record the observed number.

6. **Partition scope for the freshness checker (BF1.2).**  
   *Quote:* “A partition between any two of S, R and the restore host, of any length, healed or not.”  
   *Question:* The freshness checker is “a process on R” (T23). Can the checker be partitioned from R’s own storage, or is it always co-located? The interface treats the checker as part of R, but the cell names hosts, not processes.

7. **Observable rebuild state (B1.4 / B1.18).**  
   *Quote:* “While the status record is being rebuilt (B1.18), pruning removes nothing.”  
   *Question:* How does the harness observe “being rebuilt”? Is there a required mark, a lock file, or a state in the record? Without this, a schedule cannot assert that pruning was frozen.

8. **Restorability evidence for the test (T11).**  
   *Quote:* “Its evidence is a passing T10. A later T8 shows only that the bytes checked by that T10 are unchanged. T8 is never evidence on its own.”  
   *Question:* May a schedule assert restorability by having the harness perform its own restore probe, or must it rely solely on the `restore-checked` mark? The interface chooses marks-only, but the contract does not forbid a probe.