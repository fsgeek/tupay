# Shared test interface for the verified-backup contract

This document specifies only the **test interface**: the schedule format, the implementation-side obligations, the harness obligations, observation, fault injection, and model-runner rules. It does **not** design the backup service, prescribe a backup protocol, or prescribe service tooling. Where the interface constrains an implementation, the constraint is stated with the reason it is needed for time compression, fault injection, or observation.

All times inside schedules and observation records are **virtual seconds** unless a schedule string says otherwise. Schedule time strings use `s`, `m`, `h`, `d`; `1d = 24h`, `1h = 3600s`, `1m = 60s`. Internally the harness uses integer virtual seconds since schedule `t0`.

---

## 1. Schedule format

### 1.1 Grammar / schema

A schedule is one JSON document.

```ebnf
schedule        = object {
                    "format" : "backup-test-schedule/1",
                    "id" : string,
                    "title" : string,
                    "contract" : { "id" : string, "version" : string },
                    "binding" : { "id" : string, "version" : string,
                                  "values" : object },
                    "utc_start" : string,             ; RFC3339, default "2026-01-01T00:00:00Z"
                    "harness" : harness-block,        ; optional, harness-only
                    "setup" : setup-block,
                    "scoring_horizon_after_last_event" : time-expr,
                    "timeline" : [ event, ... ],
                    "assertions" : [ assertion, ... ]
                  }

time-expr       = string matching
                  /^(?:\+)?\d+(?:\.\d+)?(?:s|m|h|d)
                    (?:\s*\+\s*\d+(?:\.\d+)?(?:s|m|h|d))*$/
                ; absolute times are non-negative from t0;
                ; relative times start with '+'

event           = {
                    "id" : string,
                    ( "at" : time-expr | "when" : trigger ),
                    "do" : action
                  }

trigger         = { "observe" : string, ...match-fields... }
                ; harness waits until the observation log contains a matching
                ; record, then executes "do" at that virtual time

action          = source-action | inject-action | note-action

source-action   = { "source" : {
                      "op" : "write"|"append"|"delete"|"rename"|"truncate"
                           | "empty_tree"|"move_tree"|"create_file"
                           | "git_commit"|"git_ref_update"|"log_reason",
                      "tree" : string,
                      "path" : string,
                      "content" : string?,
                      "to" : string?,
                      "ref" : string?,
                      "object" : string?,
                      "size" : int?
                  } }

inject-action   = { "inject" : {
                      "cell" : "BF1.1"|"BF1.2"|"BF1.3"|"BF1.4"|"BF1.5"
                             | "BF1.6"|"BF1.7"|"BF1.8"|"BF1.9"|"BF1.10"
                             | "BF1.12"|"BF1.13"|"BF1.14",
                      "target" : "S"|"R"|"RESTORE"|"notice_channel",
                      "between" : [ "S"|"R"|"RESTORE", "S"|"R"|"RESTORE" ]?,
                      "until" : time-expr?,
                      "restart_at" : time-expr?,
                      "offset" : time-expr?,
                      "seq" : "latest"|int?,
                      "count" : int?,
                      "bytes" : int?,
                      "mode" : "lost"|"corrupted"?,
                      "timer" : "run"|"daily_check"|"freshness_check"
                              | "restore_check"|"reverify"|"notice_delivery"
                              | "prune"|"other"?,
                      "ops" : [ source-action, ... ]?
                  } }

note-action     = { "note" : string }

assertion       = {
                    "id" : string,
                    "tag" : "derives: " id,       ; e.g. "derives: B1.19"
                    "at" : time-expr | "horizon",
                    "expect" : "holds" | "violated" | "reported" | "passes",
                    "expr" : expr
                  }

expr            = JSON assertion DSL defined in §7.3
```

Retired ids (`B1.10`, `B1.14`, `BF1.11`, `AI1.6`, `EX1.4`, `T7a`, `T7b`, `T14`, `T27`) are invalid in `tag`.

### 1.2 Complete example schedule

This example injects four cells: **BF1.1** (crash S during run 1), **BF1.3** (silent corruption at R), **BF1.2** (partition S–R), and **BF1.6** (clock step at R).

```json
{
  "format": "backup-test-schedule/1",
  "id": "tupay-example-crash-corrupt-partition-clock",
  "title": "Crash S during run 1, corrupt snapshot 2 at R, partition S-R, step R clock",
  "contract": { "id": "contract-F.md", "version": "draft 7" },
  "binding": {
    "id": "binding-tupay.md",
    "version": "v1",
    "values": {
      "I": "24h", "M": "1d", "P": "7d", "H": "36h", "D": "1h",
      "X": "2h", "Rb": "2d", "G": "96h", "K": "14d", "Mo": "6month",
      "Q": 0.05, "Dmax": "27h", "T": "51h"
    }
  },
  "utc_start": "2026-01-01T00:00:00Z",
  "harness": { "real_time_budget": "10m", "output": "out/" },
  "setup": {
    "sources": [
      { "tree": "tupay", "kind": "git", "refs": { "refs/heads/main": "abc123" } },
      { "tree": "tupay-private", "kind": "dir", "files": { "a.txt": "private" } },
      { "tree": "tupay-homes", "kind": "dir", "files": { "h.txt": "home" } }
    ],
    "status_record": "empty",
    "notice_channel_record": "empty"
  },
  "scoring_horizon_after_last_event": "72h",
  "timeline": [
    {
      "id": "e1",
      "when": { "observe": "run_entry", "host": "S", "seq": 1, "state": "started" },
      "do": { "inject": { "cell": "BF1.1", "target": "S", "restart_at": "+2h" } }
    },
    {
      "id": "e2",
      "when": { "observe": "run_entry", "host": "S", "seq": 2, "state": "ok" },
      "do": { "inject": { "cell": "BF1.3", "target": "R", "seq": 2, "bytes": 16 } }
    },
    {
      "id": "e3",
      "at": "48h",
      "do": { "inject": { "cell": "BF1.2", "between": ["S", "R"], "until": "72h" } }
    },
    {
      "id": "e4",
      "at": "50h",
      "do": { "inject": { "cell": "BF1.6", "target": "R", "offset": "+24h" } }
    },
    {
      "id": "e5",
      "at": "96h",
      "do": { "source": { "op": "write", "tree": "tupay-homes", "path": "h.txt", "content": "changed" } }
    }
  ],
  "assertions": [
    {
      "id": "a1",
      "tag": "derives: B1.6",
      "at": "horizon",
      "expect": "holds",
      "expr": {
        "exists": [
          { "var": "e", "in": { "status_entries_at": ["horizon"] } },
          { "and": [
            { "eq": [ { "get": ["e", "kind"] }, "run_entry" ] },
            { "eq": [ { "get": ["e", "seq"] }, 1 ] },
            { "eq": [ { "get": ["e", "state"] }, "failed" ] },
            { "eq": [ { "get": ["e", "stage"] }, "unknown" ] }
          ] }
        ]
      }
    },
    {
      "id": "a2",
      "tag": "derives: B1.7",
      "at": "horizon",
      "expect": "holds",
      "expr": {
        "exists": [
          { "var": "f", "in": { "run_entries_failed_at": ["horizon"] } },
          { "notice_within": [ "B1.7", { "get": ["f", "time"] }, { "param": "D" }, "R" ] }
        ]
      }
    },
    {
      "id": "a3",
      "tag": "derives: B1.12",
      "at": "horizon",
      "expect": "holds",
      "expr": { "eq": [ { "latest_mark": [2, "horizon"] }, "damaged" ] }
    },
    {
      "id": "a4",
      "tag": "derives: B1.19",
      "at": "horizon",
      "expect": "holds",
      "expr": {
        "exists": [
          { "var": "n", "in": { "protected_at": ["horizon"] } },
          { "and": [
            { "eq": [ { "latest_mark": ["n", "horizon"] }, "restore-checked" ] },
            { "not": { "damaged_or_missing_since": ["n", { "latest_mark_time": ["n", "horizon"] }, "horizon"] } },
            { "lt": [ { "age_ok": ["n", "horizon", "R"] }, { "param": "G" } ] }
          ] }
        ]
      }
    }
  ]
}
```

The last injected event in this example is `e5` at `96h`, so the scoring horizon is `96h + 72h = 168h`.

---

## 2. Time

### 2.1 How time is given to an implementation

Each host sandbox has a **clock endpoint**. The implementation must obtain contract-visible time only from that endpoint.

The clock endpoint supports two methods:

```json
{"method": "now"} -> {"host": "R", "virtual_seconds": 180000, "utc": "2026-01-08T02:00:00Z"}

{"method": "wait_until", "time": 180000, "timer": "freshness_check"}
```

- `now` returns the host's current virtual time.
- `wait_until` blocks until the host's virtual clock reaches `time`. The `timer` label is mandatory and must be one of the labels in §5.4.

**Constraint and reason:** every timestamp the contract observes — status-record times, notice arrival times, manifest times, deadline ages, ages used by B1.7/B1.8/B1.12/B1.19 — must come from the harness clock, not from the OS clock. Otherwise a multi-week schedule could not run in minutes, and BF1.6 clock steps could not be injected deterministically. OS real time may be used only for non-contract internal scheduling.

### 2.2 How the harness advances time

The harness advances virtual time in **event jumps**: it runs processes in real time between jumps, then jumps each host clock to the next scheduled event, timer wake, or clock step. It does not sleep in real time for contract durations such as `I = 24h`. A schedule covering several weeks therefore runs in minutes, bounded only by `harness.real_time_budget`.

### 2.3 How clock steps on one host are expressed

A schedule injects BF1.6 with:

```json
{ "inject": { "cell": "BF1.6", "target": "R", "offset": "+24h" } }
```

The harness adds `offset` to that host's virtual clock instantly. Other hosts are unaffected. The observation log records:

```json
{"type":"clock_step","host":"R","offset":86400,"time":180000}
```

Per T12, an age measured on that host can be wrong by up to `|offset|` across the step. Sequence numbers are unaffected (T5).

---

## 3. Hosts and roles on one machine, without root

The harness creates one **host sandbox** per contract host. A sandbox is an unprivileged execution context with:

- its own root directory,
- its own virtual clock,
- its own network address behind a harness router,
- a settable byte quota on its root filesystem,
- its own process table.

No root is required. The harness may implement a sandbox with any unprivileged mechanism (separate directories plus a userspace router, unprivileged namespaces, FUSE, etc.). The implementation sees an ordinary filesystem and ordinary network endpoints.

### 3.1 Roles in a test

| Contract role | What it is in a test | How the implementation is told |
|---|---|---|
| S (T1) | Host sandbox `S`, with source trees, caches, status-record copy, notice-channel record, logged-reason file, credential detector, daily-check process | Host context JSON, `host_id: "S"`, `roles: ["source-host","daily-check"]` |
| Sources (T2/T20) | Directories under S's root, named in the test binding | `paths.sources` in S's host context |
| R (T3) | Host sandbox `R`, reached only through the harness router, with `store/` and R's status-record copy | Host context JSON, `host_id: "R"`, `roles: ["store","freshness-checker"]` |
| Restore host (T4) | Host sandbox `RESTORE`, with no source trees and a permanent network policy denying RESTORE→S | Host context JSON, `host_id: "RESTORE"`, `roles: ["restore-host"]` |
| Freshness checker (T23) | A process on R, started by the harness with `roles: ["freshness-checker"]` | Same R host context, separate process |
| Notice channel (T29) | A harness-provided endpoint with its record file on S, per the binding | `notice_channel.endpoint` and `notice_channel.record` in every host context |

### 3.2 Host context

The harness starts each implementation process with one environment variable:

```text
BACKUP_TEST_CONTEXT=/path/to/context.json
```

Example for R:

```json
{
  "host_id": "R",
  "roles": ["store", "freshness-checker"],
  "root": "/tmp/tb/r",
  "clock": { "socket": "/tmp/tb/r/.tb/clock.sock" },
  "event_log": { "socket": "/tmp/tb/r/.tb/event.sock" },
  "net": { "address": "tb://r", "router": "/tmp/tb/router.sock" },
  "paths": {
    "store_root": "/tmp/tb/r/store",
    "status_record": "/tmp/tb/r/status-record.jsonl",
    "notice_spool": "/tmp/tb/r/notice-spool.jsonl"
  },
  "notice_channel": {
    "endpoint": "/tmp/tb/notice-channel.sock",
    "record": "/tmp/tb/s/notice-channel/record.jsonl"
  },
  "parameters": { "I": 86400, "M": 86400, "P": 604800, "H": 129600,
                  "D": 3600, "X": 7200, "Rb": 172800, "G": 345600,
                  "K": 1209600, "Mo": 6, "Q": 0.05, "Dmax": 97200, "T": 183600 }
}
```

Example for S adds:

```json
"paths": {
  "sources": {
    "tupay": "/tmp/tb/s/sources/tupay",
    "tupay-private": "/tmp/tb/s/sources/tupay-private",
    "tupay-homes": "/tmp/tb/s/sources/tupay-homes"
  },
  "caches": ["/tmp/tb/s/sources/tupay-homes/.cache"],
  "status_record": "/tmp/tb/s/status-record.jsonl",
  "notice_channel_record": "/tmp/tb/s/notice-channel/record.jsonl",
  "logged_reason": "/tmp/tb/s/docs/seed-log.md",
  "credential_detector": "/tmp/tb/s/scripts/steward/secrets-scan.sh"
}
```

The restore host context has `restore_work` and no `sources`.

---

## 4. Implementation-side contract

An implementation must expose or obey **only** the following. Each constraint is needed for time compression, fault injection, or observation.

1. **Run inside the harness sandbox.** Each role process must run as an ordinary user inside its assigned host sandbox and keep all persistent state under its host root.  
   *Why:* BF1.1, BF1.4, BF1.10, BF1.12, BF1.13, BF1.14 must be injectable without root and without touching the real machine.

2. **Read contract time only from the harness clock.** All contract-visible timestamps, ages, deadlines, and timers must use `now` / `wait_until`. Every `wait_until` must carry a `timer` label from the fixed set in §5.4.  
   *Why:* multi-week schedules must run in minutes; BF1.6 and BF1.8 must be deterministic.

3. **Use the harness router for all inter-host traffic.** S, R, and RESTORE communicate only through the harness-provided network addresses.  
   *Why:* BF1.2 partitions must be injectable without implementation cooperation. The interface does not prescribe the backup protocol above this transport.

4. **Use the paths in the host context.** Sources, caches, status-record copies, R's store root, restore scratch, notice-channel record, notice spool, logged-reason file, and credential detector are at the paths given in the context.  
   *Why:* the harness must create, mutate, corrupt, delete, and observe them.

5. **Store the status record in the fixed JSONL format** described in §6.2 at the given path on S and R.  
   *Why:* the harness must observe run entries and snapshot marks, copy the record, and inject BF1.13 corruption/loss; B1.18 requires a hash the harness must be able to recompute.

6. **Store each snapshot at R as `store/<seq>/manifest.json` plus `store/<seq>/data/...`**, with the manifest in the fixed JSON format in §6.3.  
   *Why:* the harness must inject BF1.3, BF1.10, BF1.12 and must judge presence, damage, and recoverability without parsing implementation-specific formats.

7. **Emit contract events to the harness event log** via the `event_log` socket, using the event names in §6.4.  
   *Why:* T8, T10, notice sending, pruning, and restore-check starts are not otherwise visible from outside without parsing internals.

8. **Send notices to the notice-channel endpoint** given in the context. If the endpoint is unavailable, write the notice to the host's `notice_spool` path.  
   *Why:* B1.16's second part and BF1.7 require observable queued notices.

9. **Invoke the binding's credential detector** at the path given in the context when the contract requires a credential scan.  
   *Why:* B1.5/AI1.5 name the binding's detector; the interface only supplies its path.

10. **Tolerate the fault cells** in §5 without special cooperation: SIGKILL, network drops, ENOSPC, clock steps, suspended processes, corrupted bytes, deleted snapshots, lost/corrupted status records.

The implementation is free to choose its own internal protocols, storage engines, process structure, and tooling, provided the above test-visible surfaces are respected.

---

## 5. Fault injection: every BF1 cell

The harness injects cells by acting on the sandboxes, router, clocks, and files. The implementation does not need to do anything except obey §4.

| Cell | How injected | How it ends |
|---|---|---|
| **BF1.1** crash at any stage | Harness sends SIGKILL to all implementation processes on `target` at the event time. `restart_at` is required; harness restarts the same processes with the same context. To crash during a restore check or re-verify, schedule `when: {"observe":"restore_check_started", ...}` or `when: {"observe":"reverify_started", ...}` with `target: "RESTORE"` or `"R"`. | Ends at `restart_at` when processes are restarted. If `restart_at` is omitted, the host stays dead until schedule end. |
| **BF1.2** partition | Harness router drops all packets between the two hosts in `between` from the event time. | Ends at `until` (healed) or at schedule end if `until` is absent. |
| **BF1.3** silent corruption at R | Harness flips `bytes` bytes in a file under `store/<seq>/data/` on R (or in `manifest.json` if `path` says so). `seq` may be `"latest"` or an integer. | Ends immediately; corrupted bytes persist until overwritten or another fault. |
| **BF1.4** full disk at R or S | Harness sets the target host root's byte quota to `quota_bytes`; default is current usage, so the next write fails with ENOSPC. | Ends at `until` when the quota is restored. |
| **BF1.5** writes/deletes/renames/ref updates during a run | Schedule uses `inject.cell = "BF1.5"` with `ops: [source-action,...]`, normally with `when: {"observe":"run_entry","host":"S","state":"started"}` so the mutations happen during the run. | Ends when the ops complete; source changes persist. |
| **BF1.6** clock step | Harness adds `offset` (e.g. `"+24h"`, `"-1h"`) to `target` host's virtual clock instantly. | Ends immediately; the clock remains stepped. |
| **BF1.7** notice channel unavailable while S is up | Harness makes the notice-channel endpoint return unavailable; S's host remains up. | Ends at `until` when the channel becomes reachable again. |
| **BF1.8** a timer does not fire | Harness suppresses the next `wait_until` wake for the named `timer` label on `target`. | Ends after one suppressed firing. |
| **BF1.9** source tree moved/emptied/truncated by mistake | Harness performs the corresponding `source` op on S (`move_tree`, `empty_tree`, `truncate`). | Ends immediately; source state persists. |
| **BF1.10** R reimaged/replaced | Harness deletes all snapshot directories under R's `store_root` and restarts R's processes. Default: R's status-record copy is **not** deleted unless BF1.13 is also injected; see CONTRACT QUESTIONS. | Ends immediately; R has no snapshots. |
| **BF1.12** some snapshots at R lost/deleted, not by the service | Harness deletes `count` snapshot directories under `store_root`, chosen by `seq`/`seqs`. | Ends immediately; snapshots are gone. |
| **BF1.13** status record lost/corrupted at S, R, or both | `mode: "lost"` deletes the status-record file; `mode: "corrupted"` flips bytes in the file so the digest no longer matches. `target` may be `"S"`, `"R"`, or `"both"`. | Ends immediately; the record state persists until the service recovers it. |
| **BF1.14** host suspended | Harness sends SIGSTOP to all processes on `target`. Default: the host's virtual clock continues to advance while processes are frozen; a separate BF1.6 is needed to change the clock. See CONTRACT QUESTIONS. | Ends at `until` with SIGCONT. |

### 5.4 Timer labels for BF1.8

`wait_until` calls must use one of:

```text
"run" | "daily_check" | "freshness_check" | "restore_check"
| "reverify" | "notice_delivery" | "prune" | "other"
```

These correspond to the contract-visible timers: S's run interval, the daily check (T24), the freshness checker (T23), restore checks (B1.8), re-verification (B1.12), notice delivery (B1.16), and pruning. `other` is for any other contract-visible timer.

---

## 6. Observation

### 6.1 Observation log

The harness writes one append-only JSONL file at `<output>/observation.jsonl`. The implementation never writes this file directly; it emits events to the `event_log` socket and the harness records them.

Record types include:

```json
{"type":"schedule_start","schedule_id":"...","t0":0,"utc_start":"2026-01-01T00:00:00Z"}
{"type":"virtual_time","host":"R","time":180000,"utc":"2026-01-08T02:00:00Z"}
{"type":"clock_step","host":"R","offset":86400,"time":180000}
{"type":"fault","cell":"BF1.3","target":"R","params":{"seq":2,"bytes":16},"time":90000}
{"type":"source_op","op":"write","tree":"tupay-homes","path":"h.txt","time":345600}
{"type":"status_entry","host":"S","copy":"S","line":{...},"time":3600}
{"type":"snapshot_present","seq":2,"present":true,"time":90000}
{"type":"notice","clause":"B1.7","notice_id":"n-1","from_host":"R","channel_record_seq":1,"time":7200}
{"type":"event","host":"R","event":"verified_at_R","seq":2,"time":86400}
{"type":"event","host":"RESTORE","event":"restore_check_completed","seq":2,"result":"restore-checked","time":90000}
{"type":"assertion","id":"a1","tag":"derives: B1.6","status":"pass","time":604800}
```

### 6.2 Status record format

Both copies are JSONL at the paths in the host context. Each line is one entry; the last line is a digest.

Run entry:

```json
{"kind":"run_entry","seq":1,"state":"started","stage":null,"time":3600,"host":"S"}
{"kind":"run_entry","seq":1,"state":"failed","stage":"unknown","time":7200,"host":"S"}
{"kind":"run_entry","seq":2,"state":"ok","stage":null,"time":86400,"host":"S"}
```

Snapshot mark:

```json
{"kind":"snapshot_mark","seq":2,"mark":"restore-checked","time":90000,"writing_host":"RESTORE"}
```

Digest line:

```json
{"kind":"digest","algo":"sha256","digest":"<sha256 hex over the bytes of all previous lines>"}
```

`time` is the writing host's virtual clock in seconds. The harness recomputes the digest to detect BF1.13 corruption and B1.18 hash mismatch.

### 6.3 Snapshot manifest format

Each snapshot at R is:

```text
store/<seq>/manifest.json
store/<seq>/data/...
```

`manifest.json`:

```json
{
  "kind": "manifest",
  "seq": 2,
  "run_time": 86400,
  "inventory": {
    "tupay": { "type": "git", "refs": [ {"name": "refs/heads/main", "object": "abc123"} ] },
    "tupay-private": { "type": "dir", "files": ["a.txt"] }
  },
  "files": [
    { "path": "tupay-private/a.txt", "sha256": "...", "gone": false },
    { "path": "tupay-homes/old.txt", "sha256": null, "gone": true }
  ]
}
```

### 6.4 Event tap

The implementation must emit these events to the harness event log:

```text
run_started(seq, time)
run_finished(seq, state, stage, time)
verified_at_R(seq, time)                 ; T8
restore_check_started(seq, time)
restore_check_completed(seq, result, time) ; T10 result: restore-checked | restore-failed
reverify_started(seq, time)
reverify_completed(seq, result, time)    ; result: verified | damaged
pruned(seq, time)
notice_sent(clause, notice_id, time)
status_recovered(host, time)
```

### 6.5 Notice channel record

The notice channel's record is a JSONL file at the path given by `notice_channel.record` (on S in this binding). When a notice reaches the channel, the harness appends:

```json
{"seq":1,"time":7200,"from_host":"R","clause":"B1.7","notice_id":"n-1","kind":"failed-run","cause":"..."}
```

This records **which clause the notice names** and **when it arrived** on the channel's own record.

While the channel is unavailable (BF1.7), the harness does not append to the record. The sender writes the notice to its host's `notice_spool` JSONL; the harness observes the spool and later verifies delivery within `D` of the channel becoming reachable (B1.16).

### 6.6 Snapshot marks and recoverability

Snapshot marks are observed from R's status-record copy (§6.2). The harness also observes snapshot presence by listing `store/<seq>/`.

At any time `t`, the harness derives:

```text
protected(seq, t) =
  exists ok run_entry for seq at or before t
  and no pruned(seq) event at or before t

recoverable(seq, t) =
  let m = latest snapshot_mark for seq at R with time <= t
  in m.mark == "restore-checked"
     and no snapshot_mark for seq with mark in {"damaged","missing"}
         and time > m.time and time <= t
     and protected(seq, t)
```

This is the observable evidence for B1.3/B1.19: a passing T10 (`restore-checked`) plus no later `damaged`/`missing`. T8 alone is never treated as evidence of restorability.

---

## 7. Assertions and scoring horizon

### 7.1 Tags

Every assertion carries:

```json
"tag": "derives: B1.19"
```

The id after `derives:` must be an active contract id. Retired ids are invalid.

### 7.2 Scoring horizon

Each schedule states:

```json
"scoring_horizon_after_last_event": "72h"
```

The harness computes:

```text
last_injected_event_time = max actual execution time of all timeline events with a "do" action
horizon = last_injected_event_time + scoring_horizon_after_last_event
```

Assertions with `"at": "horizon"` are evaluated at `horizon`. Recoverability is judged at `horizon`.

### 7.3 Assertion DSL

Assertions use a small JSON query language over the observation log. Primitives:

| Primitive | Meaning |
|---|---|
| `{"param": "G"}` | binding parameter in seconds |
| `{"status_entries_at": [t]}` | all status-record entries observed at or before `t` |
| `{"run_entries_failed_at": [t]}` | failed run entries at or before `t` |
| `{"protected_at": [t]}` | set of seq in the protected set at `t` |
| `{"latest_mark": [seq, t]}` | latest snapshot mark for `seq` at `t` |
| `{"latest_mark_time": [seq, t]}` | time of that mark |
| `{"damaged_or_missing_since": [seq, from, to]}` | bool |
| `{"present_at_R": [seq, t]}` | bool |
| `{"age_ok": [seq, t, host]}` | `t_host - ok_time(seq)` |
| `{"notice_within": [clause, event_time, D, host]}` | a notice naming `clause` reached the channel record by `event_time + D` on `host`'s clock |
| `{"get": [obj, field]}` | field access |
| `{"eq": [a,b]}`, `{"lt": [a,b]}`, `{"le": [a,b]}`, `{"gt": [a,b]}`, `{"ge": [a,b]}` | comparisons |
| `{"and": [...]}`, `{"or": [...]}`, `{"not": x}`, `{"implies": [a,b]}` | logic |
| `{"exists": [{"var": v, "in": set}, expr]}`, `{"forall": [{"var": v, "in": set}, expr]}` | quantification |

The harness evaluates each assertion and writes a verdict:

```json
{
  "schedule_id": "...",
  "horizon": 604800,
  "assertions": [
    {"id":"a1","tag":"derives: B1.6","status":"pass","evidence":[...]}
  ]
}
```

`status` is `pass` or `fail`. The harness does not interpret the contract's class rule; the schedule's assertions encode the expected outcome.

---

## 8. Harness obligations

The harness must:

1. Parse and validate the schedule against §1.1.
2. Create the host sandboxes, source trees, caches, status-record files, notice-channel record, notice spool, logged-reason file, and credential detector from the binding and `setup`.
3. Start each role process with its host context in `BACKUP_TEST_CONTEXT`.
4. Enforce the permanent network policy: RESTORE has no path to S; all inter-host traffic goes through the harness router.
5. Run the virtual-time event loop: execute `timeline` events in order, honoring `at` and `when` triggers, applying source ops and fault injections per §5.
6. Maintain `<output>/observation.jsonl` per §6.1.
7. Evaluate assertions at their `at` times and at the scoring horizon; write `<output>/verdict.json`.
8. Run the whole schedule within `harness.real_time_budget` of real time; if exceeded, fail the run with a harness error, not an implementation failure.
9. Clean up sandboxes without requiring root.
10. Give the **same schedule file unchanged** to a model runner; the `harness` block is harness-only and may be ignored by models.

---

## 9. Model runners

A formal model's schedule runner must accept the same schedule JSON file. It must parse and accept at least:

- `format`, `id`, `title`
- `contract`, `binding` (including `values`)
- `utc_start`
- `setup`
- `scoring_horizon_after_last_event`
- `timeline` — every event's `at`/`when` and `do`
- `assertions` — every `tag`, `at`, `expect`, `expr`

It may ignore the `harness` block.

If the model cannot express a schedule element, it must **not** silently skip it. It must emit a machine-readable report and exit non-zero:

```json
{
  "status": "unsupported",
  "schedule_id": "tupay-example-...",
  "element": "timeline[2].do.inject.cell",
  "reason": "BF1.3 byte-level corruption of stored bytes is not expressible in this model"
}
```

Exit code `3` means `unsupported`; exit code `0` means the model ran the schedule and produced a verdict in the same format as §7.3.

---

## 10. OPEN CHOICES

Points where the contract or binding left the interface open, and the option chosen here:

1. **Schedule serialization: JSON vs YAML vs custom DSL.**  
   Chose JSON. Models and harnesses parse it without extra tooling; the grammar in §1.1 is enough; the example is machine-checkable.

2. **Internal time representation: integer virtual seconds vs decimal hours vs UTC timestamps.**  
   Chose integer virtual seconds since `t0`, with `utc_start` deriving UTC. Avoids float drift; contract units (`h`, `d`, `month`) are expressed in schedule strings and converted once.

3. **Time advancement: fixed-step vs event-jump.**  
   Chose event-jump: the harness jumps virtual clocks to the next event/timer/clock step. This makes multi-week schedules run in minutes without real-time sleeps.

4. **Host realization: separate OS processes vs containers vs threads.**  
   Chose harness-provided unprivileged sandboxes with separate root, clock, network, and quota. Needed for BF1.1/BF1.2/BF1.4/BF1.10/BF1.12/BF1.13/BF1.14 without root.

5. **Inter-host network: real loopback ports vs harness router.**  
   Chose a harness router with virtual addresses. Needed so BF1.2 partitions can drop traffic between any two of S, R, RESTORE without implementation cooperation.

6. **Status-record serialization: implementation-specific vs fixed JSONL+digest.**  
   Chose fixed JSONL with a trailing sha256 digest line. Needed so the harness can observe marks, copy records, verify B1.18 hashes, and inject BF1.13.

7. **Snapshot store layout: opaque vs fixed `store/<seq>/manifest.json` + `data/`.**  
   Chose fixed layout. Needed so the harness can inject BF1.3/BF1.10/BF1.12 and observe presence/recoverability without parsing implementation formats.

8. **Observation log format: binary vs JSONL.**  
   Chose JSONL at `<output>/observation.jsonl`. Human-inspectable, model-readable, append-only.

9. **Assertion language: natural language vs JSON DSL vs executable code.**  
   Chose the small JSON DSL in §7.3. It is concrete enough for harnesses and simple enough for model checkers to interpret.

10. **Scoring horizon: absolute vs relative.**  
    Chose relative to the last injected event, as required: `scoring_horizon_after_last_event`. "Last injected event" is defined as the latest actual execution time of any `timeline` event with a `do` action.

11. **BF1.4 full-disk mechanism: real small partition vs quota vs read-only.**  
    Chose a harness-enforced byte quota on the host root, defaulting to current usage so the next write fails ENOSPC. Needed because the test runs without root and must not fill the real disk.

12. **BF1.8 timer suppression: random vs labeled timers.**  
    Chose mandatory `timer` labels on `wait_until`. Needed so the harness can suppress exactly one contract-visible timer without knowing implementation internals.

13. **BF1.14 suspension and the host clock.**  
    Chose: processes are SIGSTOPped; the host's virtual clock continues to advance; a separate BF1.6 is needed to change the clock. This matches "deadlines are never suspended", but the contract text is unclear — see CONTRACT QUESTIONS.

14. **Notice spool location for B1.16's second part.**  
    Chose a per-host `notice_spool.jsonl`, with R's spool readable by the freshness checker. Needed to observe queued notices under BF1.7. The contract does not name the location — see CONTRACT QUESTIONS.

15. **Model unsupported reporting: skip vs fail.**  
    Chose machine-readable `unsupported` report with exit code 3. A model must never silently skip a schedule element it cannot express.

16. **BF1.10 scope.**  
    Chose: BF1.10 deletes all snapshot directories under R's `store_root` and restarts R; it does not delete R's status-record copy unless BF1.13 is also injected. The contract says "reimaged or replaced" but only explicitly says snapshots are lost — see CONTRACT QUESTIONS.

---

## 11. CONTRACT QUESTIONS

Places where the interface could not be designed completely because the contract text itself is unclear. Quoted verbatim; not resolved here.

1. **Which timers BF1.8 covers.**  
   > "BF1.8 A timer does not fire, at any host."  
   The interface can suppress only timers the implementation labels in `wait_until`. Internal implementation timers that are not contract-visible cannot be selected by the harness without implementation cooperation. Which timers are in scope for BF1.8?

2. **What "any stage" means in BF1.1.**  
   > "BF1.1 The backup process crashes at any stage, including during a restore check or a re-verify, and then restarts."  
   The contract names stages such as `no-credentials`, `capture`, `source`, and `unknown`, but "any stage" includes internal stages the harness cannot observe. The interface can crash at any virtual time or on observable events (`run_started`, `restore_check_started`, `reverify_started`), but cannot know an unobservable internal stage. What counts as a "stage" for BF1.1?

3. **Whether a suspended host's clock advances.**  
   > "BF1.14 ... A host is suspended (the binding names which of its hosts can be)."  
   > "T12 Clock and age: an age is measured on the clock of the host that measures it. Across a clock step, an age can be wrong by up to the size of the step."  
   If a host is suspended, does its own clock advance during the suspension? This affects deadlines measured on that host (for example the daily check on S) and the meaning of suspension versus BF1.6.

4. **Where undelivered notices are recorded under B1.16.**  
   > "B1.16 ... While the notice channel cannot be reached, the sender records the notice where the freshness checker reads, and delivers it within D of the notice channel becoming reachable."  
   The contract does not name the record, host, or path "where the freshness checker reads". The binding says the notice channel's record is on S and the freshness checker runs on R. Which record holds queued notices?

5. **BF1.7 versus a notice-channel record on S.**  
   > "BF1.7 The notice channel is unavailable while S is up."  
   > Binding: "Notice channel (T29) | the plaza, as guest:tupay. Its record is on S, so EX1.6 applies to this binding."  
   If the channel's record is on S and S is up, what exactly is unavailable during BF1.7 — the channel endpoint, the plaza service, or the record file? Does the harness still append to the record on S while the channel is "unavailable"?

6. **What exactly the B1.18 status-record hash covers.**  
   > "B1.18 ... Each copy of the status record carries a hash over its entries, rewritten at each update. A copy whose hash does not match is treated as lost."  
   The contract does not say which bytes are hashed (entry lines only? canonical serialization? including the digest line?), nor the hash algorithm. The interface needs this to verify and to inject BF1.13 corruption consistently.

7. **What B1.15's `Q` is a fraction of.**  
   > "B1.15 ... For each readable source tree, the run compares its file count and bytes with the previous acknowledged snapshot. A fall of more than Q in a run that no logged reason names sends a notice..."  
   > Binding: "Q = 0.05. Measured 2026-11-11 from 9 quiet runs. ... the bundle's size moved between −0.87 % and +1.32 %."  
   Is the "fall of more than Q" measured on file count, on bytes, or on both? Relative to the previous acknowledged snapshot's count/bytes, or to the current inventory?

8. **When "operation" starts for B1.19.**  
   > "B1.19 ... After the first G of operation, the protected set always holds a snapshot whose latest check is restore-checked, not marked damaged or missing since then, and whose ok entry is younger than G."  
   Does "operation" start at the first run attempt, the first `ok` entry, service installation, or schedule `t0`? The interface needs this to judge B1.19 at the scoring horizon.

9. **What BF1.10 destroys besides snapshots.**  
   > "BF1.10 R is reimaged or replaced, so all its snapshots are lost."  
   Does BF1.10 also destroy R's copy of the status record, the freshness checker's local state, and the notice spool, or only the snapshots? "Reimaged or replaced" suggests the whole host, but the clause only explicitly says snapshots are lost.

10. **What "full disk" means for BF1.4.**  
    > "BF1.4 A full disk at R or at S."  
    The binding gives no disk capacity or utilization threshold. What capacity and fill level define "full" in a test, and is it ENOSPC on any write or a specific utilization?