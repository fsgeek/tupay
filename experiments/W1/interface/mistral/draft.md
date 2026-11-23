Below is a complete interface specification. It does not change `contract-P.md` or `binding-tupay.md`, and it does not design the backup service.

---

# Shared test interface for the backup contract

## 0. Scope and non-goals

This interface exists so that one schedule file can be run unchanged against:

- every implementation of the contract, and
- every formal model that has its own schedule runner.

The interface prescribes only what is needed for:

- virtual time,
- placing all roles on one unprivileged machine,
- injecting every BF1 cell,
- observing notices, marks, snapshots and recoverability,
- writing assertions tagged with `derives: B1.x`,
- judging recoverability at a fixed scoring horizon.

It does **not** prescribe a backup algorithm, a storage engine, a programming language, a network protocol above the harness relay, or a notice transport beyond the minimal JSON notice envelope defined below.

---

# 1. Schedule format

## 1.1 Grammar

Schedules are JSON documents. The top-level shape is:

```json
{
  "schedule": {
    "id": "string",
    "version": "1",
    "binding": "binding-tupay",
    "start": "2026-11-12T00:00:00Z",
    "scoring_horizon": "8d",
    "events": [ Event ],
    "assertions": [ Assertion ]
  }
}
```

### 1.1.1 Primitive types

- `rfc3339` — an RFC 3339 UTC timestamp, e.g. `"2026-11-12T00:00:00Z"`.
- `duration` — a string matching `^[0-9]+(ms|s|m|h|d|w)$`, where `d` = 24 h and `w` = 7 d.
- `signedDuration` — `^[+-][0-9]+(s|m|h|d|w)$`.
- `HostId` — one of `"S"`, `"R"`, `"RESTORE"`, `"CHANNEL"`.
- `Role` — one of `"source-host"`, `"store"`, `"restore-host"`, `"freshness-checker"`, `"notice-channel"`.

### 1.1.2 Event

```json
Event = {
  "id": "string",
  "at": "rfc3339?",                 // absolute virtual time
  "after": "string?",               // id of a previous event
  "delay": "duration?",             // default "0s"; used with "after"
  "when": When?,                    // wait for an observation predicate
  "timeout": "duration?",           // default "7d"; only meaningful with "when"
  "do": Action
}
```

Exactly one of `at` or `after` should be present, or neither if the event is meant to run immediately after the previous event. If both `at` and `when` are present, the event runs at the later of the absolute time and the time at which `when` becomes true.

```json
When = {
  "kind": "run.started" | "run.inventory_read" | "run.finished"
        | "restore_check.started" | "restore_check.finished"
        | "reverify.started" | "reverify.finished"
        | "prune.started" | "prune.finished"
        | "mark.written" | "notice.sent" | "deadline.started",
  "seq": "last" | integer?,
  "match": { ... }?                 // optional extra field selectors on the observation
}
```

`seq: "last"` means the sequence number of the most recent `run.started` observation.

### 1.1.3 Action

`Action` is one of:

```json
{ "control": { "cmd": "ping" | "run.start" | "check.run" } }

{ "advance": "duration" }

{ "source": {
    "cell": "BF1.5" | "BF1.9",
    "op": "write_append" | "rewrite_in_place" | "delete" | "rename"
        | "git.set_ref" | "move_tree" | "empty_tree" | "truncate_tree",
    "path": "string",                 // relative to SOURCE_DIR
    "from": "string?", "to": "string?",   // for rename
    "ref": "string?", "object": "string?", // for git.set_ref
    "content": "string?",             // for write_append / rewrite_in_place
    "mode": "once" | "continuous",    // for rewrite_in_place
    "size": "integer?",               // for truncate_tree
    "duration": "duration?",          // for continuous mode
    "until": "string?"                // event id; alternative to duration
} }

{ "fault": { "cell": "BF1.x", ... } }   // see fault table in §5

{ "clock.step": { "host": HostId, "delta": signedDuration, "cell": "BF1.6" } }
{ "clock.set":  { "host": HostId, "time": rfc3339, "cell": "BF1.6" } }
```

### 1.1.4 Assertion

```json
Assertion = {
  "id": "string",
  "derives": "B1.x" | "BF1.x" | "EX1.x" | "AI1.x",   // never a retired id
  "at": "horizon" | "string",       // default "horizon"; may be an event id or rfc3339
  "expect": Expectation
}
```

`Expectation` is a closed set of predicates:

```json
Expectation =
  { "all": [ Expectation, ... ] }
| { "any": [ Expectation, ... ] }
| { "not": Expectation }
| { "notice_reached": {
      "clause": "B1.7" | "B1.16" | ...,
      "within": "duration",
      "of": EventRef
  } }
| { "record_entry": {
      "copy": "S" | "R",
      "kind": "run" | "mark",
      "selector": { "seq": integer, ... },
      "exists": bool
  } }
| { "snapshot_present": { "seq": integer } }
| { "snapshot_absent":  { "seq": integer } }
| { "manifest_complete": { "seq": integer } }
| { "recoverable": { "seq": integer } }
| { "not_recoverable": { "seq": integer } }
| { "recoverable_exists": { "max_age": "duration" } }
| { "not_recoverable_exists": { "max_age": "duration" } }

EventRef =
  { "event": "string" }                       // a schedule event id
| { "kind": "run" | "mark" | "deadline.started" | ...,
    "copy": "S" | "R"?, "seq": integer?, ... }
```

The harness rejects any schedule whose `derives` is one of the retired ids: `B1.10`, `B1.14`, `BF1.11`, `AI1.6`, `EX1.4`, `T7a`, `T7b`, `T14`, `T27`.

### 1.1.5 Scoring horizon

`schedule.scoring_horizon` is a fixed duration after the schedule’s **last injected event**.

An event is “injected” if its `do` contains:

- a `fault` object, or
- a `source` object with a `cell`, or
- a `clock.step` / `clock.set` with `cell: "BF1.6"`.

The harness computes:

```text
horizon = actual_virtual_time_of_last_injected_event + scoring_horizon
```

If there is no injected event, the horizon is the actual time of the last event plus `scoring_horizon`. The harness advances virtual time to the horizon, firing timers, and then evaluates all assertions whose `at` is `"horizon"`. Recoverability is judged at that horizon.

---

## 1.2 Complete example schedule

This example injects two failure-model cells:

- **BF1.3** — silent corruption of stored bytes at R,
- **BF1.5** — a source file rewritten in place during a run.

```json
{
  "schedule": {
    "id": "ex-bf1-3-and-bf1-5",
    "version": "1",
    "binding": "binding-tupay",
    "start": "2026-11-12T00:00:00Z",
    "scoring_horizon": "8d",

    "events": [
      {
        "id": "e1",
        "at": "2026-11-12T00:00:00Z",
        "do": { "control": { "cmd": "run.start" } }
      },
      {
        "id": "e2",
        "after": "e1",
        "delay": "0s",
        "when": { "kind": "run.finished", "seq": "last" },
        "do": {
          "fault": {
            "cell": "BF1.3",
            "host": "R",
            "snapshot": 1,
            "path": "tupay-homes/a/t.jsonl",
            "offset": 0,
            "flip": "0xff"
          }
        }
      },
      {
        "id": "e3",
        "at": "2026-11-12T02:00:00Z",
        "do": { "control": { "cmd": "run.start" } }
      },
      {
        "id": "e4",
        "after": "e3",
        "delay": "0s",
        "when": { "kind": "run.inventory_read", "seq": "last" },
        "do": {
          "source": {
            "cell": "BF1.5",
            "op": "rewrite_in_place",
            "path": "tupay-homes/state.db",
            "mode": "continuous",
            "duration": "2h"
          }
        }
      }
    ],

    "assertions": [
      {
        "id": "a1",
        "derives": "B1.12",
        "at": "horizon",
        "expect": {
          "record_entry": {
            "copy": "R",
            "kind": "mark",
            "selector": { "seq": 1, "mark": "damaged" },
            "exists": true
          }
        }
      },
      {
        "id": "a2",
        "derives": "B1.7",
        "at": "horizon",
        "expect": {
          "notice_reached": {
            "clause": "B1.7",
            "within": "1h",
            "of": { "kind": "mark", "copy": "R", "seq": 1, "mark": "damaged" }
          }
        }
      },
      {
        "id": "a3",
        "derives": "B1.17",
        "at": "horizon",
        "expect": {
          "all": [
            {
              "record_entry": {
                "copy": "S",
                "kind": "run",
                "selector": { "seq": 2, "status": "failed", "stage": "capture" },
                "exists": true
              }
            },
            {
              "record_entry": {
                "copy": "S",
                "kind": "run",
                "selector": { "seq": 2, "status": "ok" },
                "exists": false
              }
            }
          ]
        }
      }
    ]
  }
}
```

In this example, the last injected event is `e4`, so the horizon is `e4`’s actual virtual time plus `8d`.

---

# 2. Time

## 2.1 Virtual time model

The harness keeps:

- one global virtual time `T`, used only to order schedule events and to advance host clocks;
- one virtual clock per host, `C[h]`.

Initially:

```text
T = schedule.start
C[h] = schedule.start   for every host h
```

When the harness advances global time by `Δ`, every host clock advances by `Δ`:

```text
T  += Δ
C[h] += Δ   for all h
```

A clock step on one host changes only that host’s offset:

```text
clock.step host=h delta=+24h   =>   C[h] += 24h
clock.set  host=h time=...     =>   C[h]  = ...
```

Global `T` is unchanged by a clock step. Therefore a host’s clock can diverge from `T` and from other hosts, exactly as the contract allows: ages measured on that host can be wrong by up to the step size.

A host suspension (BF1.14) does **not** stop its virtual clock. The host’s processes are stopped, but `C[h]` continues to advance with `T`. This matches the contract’s rule that deadlines are never restarted by unavailability.

## 2.2 How time is given to an implementation

Each role process is launched with a harness clock service socket, named by the environment variable `CLOCK_SOCK`.

The implementation must obtain the current time **only** by asking that service:

```text
request:  { "op": "now" }
response: { "time": "2026-11-12T00:00:00Z" }   // this host's own virtual clock C[HOST_ID]
```

The implementation must not read the system clock, `time(2)`, `clock_gettime`, or any other real-time source for contract time.

**Why this constraint is needed:** the harness must be able to compress weeks into minutes and inject BF1.6 clock steps deterministically. If implementations read the real clock, neither is possible.

## 2.3 Timers

Every timed wait an implementation needs — run interval, daily check, restore-check deadline, re-verify deadline, notice retry, prune timer — must be registered with the harness timer service at `TIMER_SOCK`:

```text
request:  { "op": "after", "id": "run", "delay": "24h" }
response: { "op": "wake", "id": "run", "time": "..." }   // delivered when C[HOST_ID] reaches the deadline
request:  { "op": "cancel", "id": "run" }
```

Timer ids must be stable and meaningful, e.g. `"run"`, `"daily-check"`, `"restore-check:50"`, `"reverify:50"`, `"notice:B1.7:50"`.

The harness fires timers in host-clock deadline order when virtual time advances. BF1.8 is injected by dropping a named timer wakeup; see §5.

**Why this constraint is needed:** BF1.8 says “a timer on any host fails to fire.” Without a harness-visible timer registry, the harness cannot deterministically drop one timer while leaving the host up.

---

# 3. Hosts and roles on one machine, without root

## 3.1 Run directory layout

For each schedule run the harness creates:

```text
<run_dir>/
  schedule.json                 // the unchanged schedule text
  observations.jsonl            // harness-written observation log
  results.json                  // assertion results, recoverability table, horizon
  hosts/
    S/
      sources/                  // the source trees
      record/status.json        // S's copy of the status record
      out/                      // implementation logs; not asserted
    R/
      store/
        snapshots/<seq>/...     // snapshot payload files
        manifests/<seq>.json    // manifest for snapshot <seq>
      record/status.json        // R's copy of the status record
      out/
    RESTORE/
      restore/                  // restore-check workspace
      out/
    CHANNEL/
      record.jsonl              // the notice channel's own record
```

All directories are owned by the unprivileged harness user. No root, no mounts, no network namespaces, no iptables.

## 3.2 What each role is in a test

| Contract role | In a test |
|---|---|
| Source host S | sandbox `hosts/S`; a process with `HOST_ID=S`, `ROLE=source-host`; sources under `hosts/S/sources/` |
| Store R | sandbox `hosts/R`; a process with `HOST_ID=R`, `ROLE=store`; snapshots/manifests under `hosts/R/store/`; R’s record at `hosts/R/record/status.json` |
| Restore host | sandbox `hosts/RESTORE`; a process with `HOST_ID=RESTORE`, `ROLE=restore-host`; workspace under `hosts/RESTORE/restore/`; no shared directory with S and no direct path to S |
| Freshness checker | a process with `HOST_ID=R`, `ROLE=freshness-checker`; it runs on R and writes marks into R’s record |
| Notice channel | a harness-owned process with `HOST_ID=CHANNEL`, `ROLE=notice-channel`; its record is `hosts/CHANNEL/record.jsonl` |

The binding says which hosts the channel depends on and where its record lives. For `binding-tupay`, the channel’s record is on S, so the harness treats the channel as dependent on S: if S is suspended or otherwise unavailable, the channel is unreachable. BF1.7 can still inject “channel down while S is up” independently.

## 3.3 How an implementation is told where things are

The harness launches each role process with these environment variables:

```text
HARNESS_RUN_DIR=<run_dir>
HOST_ID=S|R|RESTORE|CHANNEL
ROLE=source-host|store|restore-host|freshness-checker|notice-channel

CLOCK_SOCK=<path>          # §2.2
TIMER_SOCK=<path>          # §2.3
CONTROL_SOCK=<path>        # §4.2
OBSERVE_SOCK=<path>        # §4.3
NET_SOCK=<path>            # §3.4 harness relay

SOURCE_DIR=<run_dir>/hosts/S/sources          # only on S
STORE_DIR=<run_dir>/hosts/R/store             # only on R
RESTORE_DIR=<run_dir>/hosts/RESTORE/restore   # only on RESTORE
RECORD_PATH=<run_dir>/hosts/<S|R>/record/status.json   # on S and R

S_ADDR=<relay address for S>
R_ADDR=<relay address for R>
RESTORE_ADDR=<relay address for RESTORE>
CHANNEL_ADDR=<relay address for CHANNEL>

BINDING_ID=binding-tupay
PARAMS_JSON=<JSON object with I, M, P, H, D, X, Rb, G, K, Mo, Q, Dmax, T>
```

## 3.4 Network and partition injection

All inter-role communication in a test must go through the harness relay at `NET_SOCK`. The implementation connects to the relay addresses above, not directly to other hosts.

The harness relay can drop all traffic between any two of `S`, `R`, `RESTORE` for a chosen virtual duration. That is BF1.2.

**Why this constraint is needed:** without root, the harness cannot use `iptables` or network namespaces. A user-space relay is the only portable way to inject a partition while keeping both hosts up.

---

# 4. Implementation-side contract

An implementation must expose or obey exactly the following, and nothing more.

| # | Constraint | Why it is needed |
|---|---|---|
| 1 | Run as an unprivileged child process of the harness; use only the sandbox directories and harness sockets given in the environment. | One machine, no root; fault injection and observation. |
| 2 | Read contract time only from `CLOCK_SOCK` (`now`). Never read the system clock. | Virtual-time compression and BF1.6 clock steps. |
| 3 | Register all timers/wakeups with `TIMER_SOCK`; use stable timer ids. | BF1.8 deterministic timer drop. |
| 4 | Send all inter-role messages through the harness relay at `NET_SOCK`; use `S_ADDR`, `R_ADDR`, `RESTORE_ADDR`, `CHANNEL_ADDR`. | BF1.2 partition injection without root. |
| 5 | Keep S’s and R’s status-record copies as JSON files at `RECORD_PATH`, in the format of §6.2, with the hash field of B1.18. | Observation of run entries and marks; BF1.13 injection. |
| 6 | Keep R’s snapshots under `STORE_DIR/snapshots/<seq>/` and manifests under `STORE_DIR/manifests/<seq>.json`, in the format of §6.3. | Observation of snapshot presence and manifests; BF1.3, BF1.10, BF1.12 injection. |
| 7 | Keep sources under `SOURCE_DIR`; keep restore-check workspace under `RESTORE_DIR`. | BF1.5/BF1.9 source mutation; restore-host isolation. |
| 8 | Accept control commands on `CONTROL_SOCK`: `ping`, `run.start`, `check.run`. | Deterministic schedules; injecting source changes during a run. |
| 9 | Emit the required observations of §4.3 on `OBSERVE_SOCK`. | `when` predicates and assertion evaluation. |
| 10 | Send notices to `CHANNEL_ADDR` as JSON with at least a `clause` field, in the format of §6.4. | Observation of the notice channel’s record; BF1.7. |
| 11 | Be restartable after SIGKILL; survive SIGSTOP/SIGCONT; treat write errors (`ENOSPC`, `EFBIG`, `EACCES`) on its sandbox as a full disk; treat relay errors as unreachable hosts. | BF1.1, BF1.14, BF1.4, BF1.2. |

The interface does **not** prescribe:

- language, runtime, or libraries;
- backup algorithm, scheduling policy, pruning policy, or storage engine;
- the protocol spoken above the harness relay;
- the notice transport beyond the JSON envelope in §6.4;
- the internal format of snapshot payloads, except that they are ordinary files under `STORE_DIR/snapshots/<seq>/` so the harness can corrupt or delete them.

## 4.2 Control commands

On `CONTROL_SOCK`, the implementation must accept JSON lines:

```json
{ "op": "ping" }
{ "op": "run.start" }
{ "op": "check.run" }
```

and reply:

```json
{ "ok": true }
```

`run.start` starts one run on S immediately. `check.run` starts one freshness-checker pass on R immediately. These commands exist so a schedule can create deterministic points such as “during this run, after the inventory is read.”

## 4.3 Required observations

The implementation must send JSON observations to `OBSERVE_SOCK`. The harness appends them to `observations.jsonl` with both global time and the emitting host’s own clock:

```json
{
  "time": "2026-11-12T02:00:00Z",
  "host_time": "2026-11-12T02:00:00Z",
  "host": "S",
  "kind": "run.inventory_read",
  "seq": 2
}
```

Required observation kinds:

- `run.started`, `run.inventory_read`, `run.finished`
- `restore_check.started`, `restore_check.finished`
- `reverify.started`, `reverify.finished`
- `prune.started`, `prune.finished`
- `mark.written`
- `notice.sent`
- `deadline.started` — emitted by the freshness checker on R when it starts measuring a B1.7 deadline; fields include `clause`, `cause`, `seq`.

---

# 5. Fault injection: every BF1 cell

The harness injects faults directly; it does not ask the implementation to misbehave.

| Cell | Schedule action | Mechanism | How it ends |
|---|---|---|---|
| **BF1.1** crash/restart | `{"fault":{"cell":"BF1.1","host":"R","role":"store","action":"crash","restart":"immediate"}}` | Harness sends SIGKILL to the named role process and immediately relaunches it with the same environment. A schedule can combine this with `"when":{"kind":"prune.started"}` or `"restore_check.started"` to crash mid-prune or mid-check. | Ends at restart. No duration. |
| **BF1.2** partition | `{"fault":{"cell":"BF1.2","partition":["S","R"],"duration":"48h"}}` or `"until":"event-id"` | Harness relay drops all messages between the two named hosts. Hosts stay up; their clocks keep advancing. | Ends after `duration` virtual time or at the `until` event; relay restored. |
| **BF1.3** silent corruption at R | `{"fault":{"cell":"BF1.3","host":"R","snapshot":50,"path":"tupay-homes/a/t.jsonl","offset":1024,"flip":"0xff"}}` | Harness opens `hosts/R/store/snapshots/50/tupay-homes/a/t.jsonl` and flips bytes at `offset` without notifying the implementation. | Persistent until a later schedule action repairs the file, or BF1.10/BF1.12 removes the snapshot. |
| **BF1.4** disk full on S or R | `{"fault":{"cell":"BF1.4","host":"R","duration":"12h"}}` or `"until":"..."` | Harness sets `RLIMIT_FSIZE=0` on all processes of that host (with `SIGXFSZ` ignored in the child before exec) and makes the host’s writable sandbox directories read-only. Writes and new-file creation fail. | Ends after `duration`/`until`; harness restores rlimits and directory permissions. |
| **BF1.5** source mutation during run | `{"source":{"cell":"BF1.5","op":"rewrite_in_place","path":"tupay-homes/state.db","mode":"continuous","duration":"2h"}}`, usually with `"when":{"kind":"run.inventory_read","seq":"last"}` | Harness mutates the file under `hosts/S/sources/...` at the scheduled stage. `mode:"continuous"` rewrites the file on every virtual-time tick while active. | `mode:"once"` is a one-time mutation. `mode:"continuous"` ends after `duration`/`until` or when a later source action touches the same path. |
| **BF1.6** clock step | `{"clock.step":{"host":"S","delta":"+24h","cell":"BF1.6"}}` or `{"clock.set":{"host":"S","time":"...","cell":"BF1.6"}}` | Harness changes only that host’s virtual clock offset; global `T` is unchanged; timers are recomputed. | Persistent until another `clock.step`/`clock.set` on the same host. |
| **BF1.7** notice channel down while S up | `{"fault":{"cell":"BF1.7","channel":"down","duration":"6h"}}` or `"until":"..."` | Harness marks `CHANNEL_ADDR` unreachable; sends fail and are not recorded in the channel record. | Ends after `duration`/`until`; channel accepts notices again. |
| **BF1.8** timer fails to fire | `{"fault":{"cell":"BF1.8","host":"S","timer":"daily-check","once":true}}` | When the named timer’s deadline is reached, the harness records `timer.dropped` and does not deliver the wakeup. | The dropped wakeup never fires. With `once:false`, all matching wakeups are dropped until `until`. |
| **BF1.9** source tree moved/emptied/truncated | `{"source":{"cell":"BF1.9","op":"move_tree","path":"tupay-homes","to":"tupay-homes-moved"}}` or `empty_tree` / `truncate_tree` | Harness moves, empties, or truncates the source tree under `hosts/S/sources/...`. | Persistent until a later source action restores it. |
| **BF1.10** R reimaged, all snapshots lost | `{"fault":{"cell":"BF1.10","host":"R"}}` | Harness deletes everything under `hosts/R/store/snapshots/` and `hosts/R/store/manifests/`. R’s status record is left intact. | Persistent; later runs may write new snapshots. |
| **BF1.12** some snapshots lost at R | `{"fault":{"cell":"BF1.12","host":"R","snapshots":[50,51]}}` | Harness deletes `hosts/R/store/snapshots/<seq>/` and `hosts/R/store/manifests/<seq>.json` for the listed sequence numbers. | Persistent. |
| **BF1.13** status record lost/corrupted | `{"fault":{"cell":"BF1.13","copy":"S"|"R"|"both","mode":"lost"|"corrupt"}}` | `lost`: harness deletes or truncates `hosts/<copy>/record/status.json`. `corrupt`: harness flips bytes in that file so its hash fails. | Persistent; the implementation must recover per B1.18. The harness never repairs it. |
| **BF1.14** host suspended | `{"fault":{"cell":"BF1.14","host":"RESTORE","duration":"48h"}}` or `"until":"..."` | Harness sends SIGSTOP to all processes on that host. The host’s virtual clock continues to advance. | Ends after `duration`/`until` with SIGCONT. |

---

# 6. Observation formats

## 6.1 Observation log

`observations.jsonl` is JSON Lines. Each line:

```json
{
  "time": "2026-11-12T02:00:00Z",
  "host_time": "2026-11-12T02:00:00Z",
  "host": "S",
  "kind": "run.inventory_read",
  "seq": 2
}
```

`time` is global virtual time; `host_time` is the emitting host’s own clock at that moment. Assertions that compare deadlines use `host_time` of the referenced observation and the channel record host’s clock for notice arrival.

## 6.2 Status record

Each copy is a single JSON file at `RECORD_PATH`:

```json
{
  "entries": [
    {
      "kind": "run",
      "seq": 50,
      "status": "started" | "ok" | "failed",
      "stage": "unknown" | "source" | "capture" | "no-credentials" | "...",
      "time": "2026-11-12T00:00:00Z",
      "writer": "S"
    },
    {
      "kind": "mark",
      "seq": 50,
      "mark": "restore-checked" | "restore-failed" | "not-restore-checked" | "damaged" | "missing",
      "time": "2026-11-12T13:00:00Z",
      "writer": "R" | "checker" | "restore"
    }
  ],
  "hash": "sha256:..."
}
```

`hash` is the SHA-256 of the canonical JSON encoding of `entries` (sorted keys, no whitespace). The implementation must update the file atomically — write a temp file and rename — and recompute `hash` at every update, per B1.18.

The harness reads both `hosts/S/record/status.json` and `hosts/R/record/status.json`. It can also delete or corrupt them for BF1.13.

## 6.3 Snapshot and manifest

Snapshot payload files live under:

```text
hosts/R/store/snapshots/<seq>/...
```

The manifest lives at:

```text
hosts/R/store/manifests/<seq>.json
```

Manifest format:

```json
{
  "seq": 50,
  "created_time": "2026-11-12T00:00:00Z",
  "inventory": [
    { "type": "file", "path": "tupay-homes/a/t.jsonl" },
    { "type": "git-ref", "ref": "refs/heads/main", "object": "abc123" }
  ],
  "files": [
    { "type": "file", "path": "tupay-homes/a/t.jsonl", "sha256": "...", "status": "present" },
    { "type": "file", "path": "tupay-homes/old.txt", "status": "gone" },
    { "type": "git-ref", "ref": "refs/heads/main", "object": "abc123", "status": "present" }
  ]
}
```

`manifest_complete` for a sequence number means: every entry in `inventory` has a matching entry in `files` by `path` or by `ref`, with `status` either `"present"` or `"gone"`.

## 6.4 Notice channel record

The channel’s own record is `hosts/CHANNEL/record.jsonl`, JSON Lines:

```json
{
  "seq": 1,
  "clause": "B1.7",
  "cause": "overdue",
  "snapshot": 50,
  "event_time": "2026-11-12T13:00:00Z",
  "arrival_time": "2026-11-12T13:05:00Z",
  "arrival_host_time": "2026-11-12T13:05:00Z",
  "sender_host": "R"
}
```

- `clause` is the clause the notice names.
- `arrival_time` is global virtual time when the channel’s record first held the notice.
- `arrival_host_time` is the clock of the binding’s channel record host at arrival. For `binding-tupay`, that host is S.

A notice “reaches” the channel exactly when this record holds it.

## 6.5 Recoverability

At the scoring horizon the harness computes, for every sequence number with an `ok` run entry in S’s record:

```text
present(seq)         = hosts/R/store/snapshots/<seq>/ exists
                       and hosts/R/store/manifests/<seq>.json exists

marks(seq)           = all mark entries for seq in R's record, in record append order

latest_check(seq)    = last mark in marks(seq) whose mark is
                       "restore-checked" or "restore-failed"

recoverable(seq)     = present(seq)
                       and latest_check(seq) == "restore-checked"
                       and no mark after latest_check(seq) in marks(seq)
                         has mark "damaged" or "missing"
```

This is the interface’s observation of B1.3 recoverability. The harness does not itself run a restore check; it observes the marks and the store listing. `results.json` contains a `recoverability` table with these fields for every relevant `seq`.

---

# 7. Assertions and scoring

## 7.1 Evaluation

The harness evaluates each assertion at its `at` time:

- `"horizon"` means the scoring horizon defined in §1.1.5;
- an event id means the actual virtual time of that event;
- an RFC 3339 time means that absolute virtual time.

Each assertion result is written to `results.json`:

```json
{
  "assertions": [
    {
      "id": "a1",
      "derives": "B1.12",
      "status": "pass" | "fail",
      "detail": "..."
    }
  ],
  "horizon": "2026-11-20T02:00:00Z",
  "recoverability": [ ... ],
  "unsupported": []
}
```

## 7.2 Time comparisons in assertions

For `notice_reached`, the harness uses:

```text
deadline = of.host_time + within
pass     = exists notice in CHANNEL/record.jsonl with clause == clause
           and notice.arrival_host_time <= deadline
```

where `of.host_time` is the host clock of the referenced observation/entry. For a `mark` reference, the harness uses the `deadline.started` observation emitted by the freshness checker on R for that mark, if present; otherwise it uses the mark entry’s `time` on the writer’s clock.

---

# 8. Harness obligations

The harness must:

1. Create the run directory of §3.1 and launch all roles with the environment of §3.3.
2. Provide the clock, timer, control, observe, and relay services of §§2–4.
3. Parse and validate the schedule against §1.1; reject retired `derives` ids.
4. Execute events in order:
   - compute the event’s earliest virtual time from `at` or `after` + `delay`;
   - advance global virtual time to that point, firing timers in host-clock deadline order;
   - if `when` is present, advance virtual time in 1-minute steps until the predicate is true or `timeout` expires, firing timers;
   - execute `do`.
5. Inject every BF1 cell as specified in §5, without asking the implementation to cooperate.
6. Record all observations, record files, store listings, and channel notices in the formats of §6.
7. After the last event, compute the scoring horizon, advance to it, evaluate assertions, and write `results.json`.
8. Run the same schedule text unchanged against implementations and models.
9. Never require root, mounts, namespaces, or firewall rules.

---

# 9. Model runners

A formal model’s own schedule runner must accept the **same schedule JSON text**.

It must:

- parse and validate the full schedule against §1.1;
- resolve `binding` to the same parameter values as the harness;
- understand the abstract semantics of `events` and `assertions`, including virtual time, per-host clock offsets, `when` predicates, fault cell ids, and the scoring horizon;
- either execute the schedule and write a `results.json` in the same format as §7.1, or report that it cannot express the schedule.

A model must **not** silently skip an event or assertion it cannot express. If it cannot express part of a schedule, it must write:

```json
{
  "status": "unsupported",
  "schedule": "ex-bf1-3-and-bf1-5",
  "unsupported": [
    { "id": "e4", "reason": "byte-level continuous source rewrite not expressible", "field": "source.op" },
    { "id": "a1", "reason": "..." }
  ]
}
```

and exit with a distinct non-zero status, e.g. `3`. The harness records this in `results.json` under `unsupported` and does not count those assertions against the model.

---

# 10. OPEN CHOICES

These are points where the contract or binding left the interface design open. For each, the options I saw and the reason for my choice are given.

1. **Schedule language.** Options: JSON, YAML, TOML, custom DSL. Chose JSON: strict schema, easy to validate, easy for both harnesses and model runners to parse, no comments needed.

2. **Time representation.** Options: global virtual time with per-host offsets; per-host event times; real-time sleeps; Lamport clocks. Chose global virtual time plus per-host offsets: it compresses weeks into minutes, keeps schedule event times readable, and lets BF1.6 be a single offset change on one host.

3. **Time advancement.** Options: explicit `at`/`after`/`advance` events; real-time waiting; hybrid. Chose explicit virtual-time advancement with timers fired instantly: required for “weeks in minutes.”

4. **Timer injection for BF1.8.** Options: OS timers plus signals; harness timer registry; clock manipulation only. Chose harness timer registry: only way to deterministically make one timer fail while the host stays up.

5. **Host isolation on one machine without root.** Options: containers, VMs, user namespaces, plain directories plus relay. Chose plain directories plus harness relay and signals: no root, portable, sufficient for the failure model.

6. **Partition injection for BF1.2.** Options: `iptables`, network namespaces, user-space relay. Chose user-space relay: no root required.

7. **Disk-full injection for BF1.4.** Options: real filesystem quota, FUSE, `RLIMIT_FSIZE` plus read-only dirs, `LD_PRELOAD` shim. Chose `RLIMIT_FSIZE=0` with `SIGXFSZ` ignored plus read-only sandbox dirs: portable, no root, and produces write failures on the host. The observable effect is “writes fail,” which is what a full disk does to the service.

8. **Status-record format.** Options: opaque implementation storage plus API, JSONL, single JSON file with hash. Chose single JSON file with `entries` and `hash` at a known path: needed for observation and for BF1.13 corruption/loss injection.

9. **Snapshot/manifest layout.** Options: opaque store plus API, known directories. Chose known directories under `STORE_DIR`: needed for BF1.3/BF1.10/BF1.12 injection and for presence/manifest observation.

10. **Notice channel in a test.** Options: real plaza, harness-owned fake channel. Chose harness-owned fake channel with its own record: needed for BF1.7 and for observing clause and arrival time.

11. **Triggering runs and checks.** Options: rely only on timers; explicit control commands. Chose explicit `run.start` and `check.run` control commands: needed to inject BF1.5 deterministically during a run and to keep schedules model-readable.

12. **Assertion language.** Options: full first-order logic, SPIN/TLA+ expressions, closed predicate set. Chose a closed set of predicates: models can implement it without agreeing on a full logic, and schedules stay readable.

13. **Scoring horizon.** Options: absolute time, after last event, after last injected event. Chose after last injected event, as required by the prompt.

14. **Fault end semantics.** Options: explicit end events for every cell; `duration`/`until`; persistence for state changes. Chose `duration`/`until` for transient faults and persistence for state-changing faults (BF1.3, BF1.9, BF1.10, BF1.12, BF1.13, BF1.6).

15. **Mark ordering.** Options: host clock `time` fields; record append order; sequence numbers. Chose record append order in R’s copy for marks on the same snapshot: the contract says sequence numbers order runs and snapshots, and record entries are append-only; clock times can be stepped.

16. **Recoverability observation.** Options: harness independently restores snapshots; derive from marks and store presence. Chose derived from marks and store presence per B1.3: the contract says only a passing restore check is evidence, and the harness observes those marks rather than duplicating the service.

17. **Channel dependency.** Options: ignore binding’s channel dependencies; enforce them. Chose enforce: `binding-tupay` says the channel’s record is on S, so EX1.6 applies; the harness marks the channel unreachable when S is unavailable, while BF1.7 can still inject channel-down independently.

18. **Suspended host’s clock.** Options: stop the host clock during suspension; let it advance. Chose let it advance: real hardware clocks continue during suspension, and the contract says deadlines are never restarted.

19. **Model unsupported reporting.** Options: silent skip, warning, explicit machine-readable report. Chose explicit `unsupported` report with exit code: required so a model can say it cannot express a schedule without pretending it ran.

20. **Source mutation operations.** Options: run `git` commands, call implementation APIs, direct file/ref mutation. Chose direct file and ref-file mutation under `SOURCE_DIR`: no tooling prescribed, and it works for both files and git refs.

---

# 11. CONTRACT QUESTIONS

These are places where I could not fully design injection or observation because the contract text itself is unclear. I quote the text and do not resolve them.

1