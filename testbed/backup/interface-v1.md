# Shared test interface for the backup contract, v1

Merged from two independent drafts by GLM and Mistral. The disposition of every difference is in `experiments/W1/interface/DISPOSITIONS.md` (the steward, 2026-11-23). Items marked [Dn] or [An] name the line there. This interface changes no clause of the contract and designs no part of the service.

## 0. Scope
One schedule file runs unchanged against every implementation of the contract and against every formal model that has a schedule runner. This interface prescribes only what is needed for virtual time, for placing all roles on one unprivileged machine, for injecting every BF1 cell, for observing notices, marks, snapshots and recoverability, for tagged assertions, and for a fixed scoring horizon. It prescribes no backup algorithm, storage engine, language, process model, or protocol above the harness relay.

## 1. Schedule format [D1]
A schedule is one JSON document matching the schema below. Any object may carry a `"note"` string, which every runner ignores.

```json
{
  "schedule": {
    "id": "string",
    "version": "1",
    "binding": "binding-tupay-v1",
    "params": { },
    "start": "2026-11-12T00:00:00Z",
    "scoring_horizon": "8d",
    "world": [ WorldItem ],
    "events": [ Event ],
    "assertions": [ Assertion ]
  }
}
```

### 1.1 Primitive types
- `rfc3339`: an RFC 3339 UTC timestamp.
- `duration`: `^[0-9]+(ms|s|m|h|d|w)$`, where `d` is 24 h and `w` is 7 d.
- `signedDuration`: `^[+-][0-9]+(s|m|h|d|w)$`.
- `HostId`: `"S"`, `"R"`, `"RESTORE"` or `"CHANNEL"`.
- `Role`: `"source-host"`, `"store"`, `"restore-host"`, `"freshness-checker"` or `"notice-channel"`.
- `TimerKind`: `"run"`, `"check"`, `"restore-check"`, `"reverify"`, `"prune"`, `"notice-retry"` or `"other"` [D2].

### 1.2 Parameters
`params` overrides binding values, using the binding's names (*I*, *M*, *P*, *H*, *D*, *X*, *Rb*, *G*, *Q*, *K*, *Mo*), with durations as `duration` strings, *Q* as a number and *Mo* as an integer number of months. *Dmax* and *T* are derived by the harness as the contract states. Every runner uses the same resulting values.

### 1.3 World: S's sources at time zero [D11]
```json
WorldItem =
  { "type": "dir",  "path": "tupay-private/", "files": 40, "bytes": 200000, "seed": 7 }
| { "type": "file", "path": "tupay-homes/a/t.jsonl", "content": "string", "append_only": true }
| { "type": "git",  "path": "tupay.git", "refs": { "refs/heads/main": "commits:3" } }
```
Paths are relative to `SOURCE_DIR`. `dir` generates `files` files totalling `bytes` bytes, deterministically from `seed`. `git` creates a repository with the named refs, each pointing at a generated history of the stated number of commits. The harness builds the world before the first event.

### 1.4 Events
```json
Event = {
  "id": "string",
  "at": "rfc3339?",
  "after": "string?",
  "delay": "duration?",
  "when": When?,
  "timeout": "duration?",
  "do": Action
}
```
An event names `at`, or `after` (an earlier event's id) with an optional `delay` (default `0s`), or neither (it then runs immediately after the previous event). With both `at` and `when`, it runs at the later of the two. `timeout` (default `7d`) applies only to `when`.

```json
When = { "kind": ObservationKind, "seq": "last" | integer?, "match": { }? }
```
`seq: "last"` means the sequence number of the most recent `run.started` observation. **If `when` is not true before `timeout` expires, the event is *unreached*.** It is not executed, and every assertion that names it, or any later event that depends on it, is scored `unreached`, never `pass` or `fail` [D5].

```json
Action =
  { "control": { "cmd": "run.start" | "check.run" | "ping" } }
| { "advance": duration }
| { "source": SourceAction }
| { "fault": Fault }
| { "clock.step": { "host": HostId, "delta": signedDuration, "cell": "BF1.6" } }
| { "clock.set":  { "host": HostId, "time": rfc3339, "cell": "BF1.6" } }
| { "query": { "what": "restore", "seq": integer } }
```
- `control` asks the implementation to start one run on S now, or one freshness-checker pass on R now (§4.2).
- `query` makes the **harness itself** perform an independent restore of snapshot `seq` (§6.6) [D12]. It is an observation, never the implementation's restore check, and it never counts toward B1.8.

```json
SourceAction = {
  "cell": "BF1.5" | "BF1.9" | null,
  "op": "write_append" | "rewrite_in_place" | "create" | "delete" | "rename"
      | "git.set_ref" | "git.commit" | "move_tree" | "empty_tree" | "truncate_tree",
  "path": "string", "to": "string?", "ref": "string?", "object": "string?",
  "content": "string?", "mode": "once" | "continuous", "size": "integer?",
  "duration": "duration?", "until": "string?"
}
```
A `source` action with `cell: null` is an ordinary change, not an injection. `rewrite_in_place` with `mode: "continuous"` rewrites the file at every virtual tick until `duration` passes or the `until` event runs.

### 1.5 Assertions
```json
Assertion = {
  "id": "string",
  "derives": "B1.x" | "BF1.x" | "EX1.x" | "AI1.x",
  "at": "horizon" | "<event id>" | rfc3339,
  "expect": Expectation
}
```
`at` defaults to `"horizon"`. **Every assertion carries exactly one `derives:` tag** [A8]. The harness rejects a schedule whose tag names a retired id: `B1.10`, `B1.14`, `BF1.11`, `AI1.6`, `EX1.4`, `T7a`, `T7b`, `T14` or `T27`.

```json
Expectation =
  { "all": [ Expectation ] } | { "any": [ Expectation ] } | { "not": Expectation }
| { "notice_reached": { "clause": "B1.x", "within": duration, "of": EventRef, "cause": "string?" } }
| { "record_entry": { "copy": "S" | "R", "kind": "run" | "mark", "selector": { }, "exists": bool } }
| { "snapshot_present": { "seq": integer } }
| { "snapshot_absent":  { "seq": integer } }
| { "manifest_complete": { "seq": integer } }
| { "marks_restorable": { "seq": integer } }
| { "restores": { "seq": integer } }
| { "recoverable_exists": { "max_age": duration } }
| { "next_seq_at_least": { "value": integer } }

EventRef = { "event": "string" } | { "kind": ObservationKind | "run" | "mark", "copy": "S" | "R"?, "seq": integer?, "match": { }? }
```
- `marks_restorable(seq)`: §6.5's `marks_restorable` holds for `seq`.
- `restores(seq)`: the harness's independent restore of `seq` (§6.6) succeeded. **A B1.3 assertion takes the form `marks_restorable(seq)` implies `restores(seq)`**, that is, `{"any": [{"not": {"marks_restorable": …}}, {"restores": …}]}` [D4].
- `recoverable_exists(max_age)`: some `seq` has `marks_restorable(seq)`, and its *ok* entry is younger than `max_age` at the assertion's time. A B1.19 assertion uses `max_age` = *G* [D4].
- `next_seq_at_least`: the next run's sequence number is at least `value` (worked case 4).
- **Where the contract permits several readings, an assertion must accept each of them** (W1 decision tree, step 2). An assertion built with `any` over the readings is the way to do it. **No assertion may require the service itself to report a clock step** [D8].

### 1.6 Scoring horizon [D10]
`scoring_horizon` is a fixed duration after the schedule's **last injected event**. An event is injected if its action is a `fault`, a `source` action with a non-null `cell`, or a `clock.step` or `clock.set`. The harness computes horizon = (the virtual time at which the last injected event actually ran) + `scoring_horizon`. With no injected event, the horizon is anchored on the last event. The harness advances to the horizon, firing timers, and evaluates every assertion whose `at` is `"horizon"`. A deadline that falls after the horizon is **censored** and listed as such in `results.json`. The horizon is never extended or shortened.

### 1.7 Example
```json
{ "schedule": {
  "id": "ex-bf1-3-bf1-14", "version": "1", "binding": "binding-tupay-v1", "params": {},
  "start": "2026-11-12T00:00:00Z", "scoring_horizon": "6d",
  "world": [ { "type": "git", "path": "tupay.git", "refs": { "refs/heads/main": "commits:3" } },
             { "type": "dir", "path": "tupay-private/", "files": 40, "bytes": 200000, "seed": 1 } ],
  "events": [
    { "id": "e1", "at": "2026-11-12T00:00:00Z", "do": { "control": { "cmd": "run.start" } } },
    { "id": "e2", "after": "e1", "when": { "kind": "run.finished", "seq": "last" },
      "do": { "fault": { "cell": "BF1.3", "host": "R", "seq": 1, "path": "tupay-private/f0001", "offset": 0, "flip": "0xff" } } },
    { "id": "e3", "after": "e2", "delay": "1h",
      "do": { "fault": { "cell": "BF1.14", "host": "RESTORE", "duration": "48h" } } }
  ],
  "assertions": [
    { "id": "a1", "derives": "B1.3", "expect": { "any": [ { "not": { "marks_restorable": { "seq": 1 } } }, { "restores": { "seq": 1 } } ] } },
    { "id": "a2", "derives": "B1.7", "expect": { "notice_reached": { "clause": "B1.7", "within": "1h",
        "of": { "kind": "deadline.started", "match": { "clause": "B1.8", "seq": 1 } } } } },
    { "id": "a3", "derives": "B1.19", "expect": { "recoverable_exists": { "max_age": "96h" } } }
  ] } }
```
It injects BF1.3 and BF1.14. Its horizon is e3's actual time plus 6 d.

## 2. Time
### 2.1 Model [A1, D3]
The harness keeps one global virtual time `T` and one clock per host, `C[h]`, all equal to `start` at first. Advancing global time by Δ advances every `C[h]` by Δ. `clock.step` and `clock.set` change only the named host's `C[h]`, and `T` is unchanged. **A suspended host's clock keeps advancing** with `T`, because the contract's deadlines are never suspended, paused or restarted [D3].

### 2.2 Time for the implementation [A2]
Each role process gets `CLOCK_SOCK`. The implementation obtains contract time only by asking it: `{"op":"now"}` returns `{"time": "<C[HOST_ID] as rfc3339>"}`. It never reads the system clock for contract time. *Why:* weeks must run in minutes, and BF1.6 must step one host's clock.

### 2.3 Timers [D2]
Every timed wait the implementation needs is registered with `TIMER_SOCK`:
```text
{"op":"after","id":"<free id>","kind":"<TimerKind>","delay":"24h"}  ->  later {"op":"wake","id":"...","time":"..."}
{"op":"cancel","id":"..."}
```
Wakeups are delivered when `C[HOST_ID]` reaches the deadline, in host-clock deadline order. `kind` is required and comes from the closed set in §1.1. `other` is for anything else. *Why:* BF1.8 drops a wakeup chosen by (host, kind), and a hold-out written without seeing any implementation can only name a kind.

## 3. Hosts and roles [A3, A7]
### 3.1 Layout
```text
<run_dir>/
  schedule.json  observations.jsonl  clock-steps.jsonl  results.json
  hosts/S/sources/  hosts/S/record/status.json  hosts/S/out/
  hosts/R/store/snapshots/<seq>/  hosts/R/store/manifests/<seq>.json  hosts/R/record/status.json  hosts/R/out/
  hosts/RESTORE/restore/  hosts/RESTORE/out/
  hosts/CHANNEL/record.jsonl
  harness/restores/<seq>/
```
Everything is owned by the unprivileged harness user. There is no root, no mount, no namespace and no firewall rule.

### 3.2 Roles in a test
| Role | In a test |
|---|---|
| Source host S | processes with `HOST_ID=S`, `ROLE=source-host`; sources under `hosts/S/sources/` |
| Store R | `HOST_ID=R`, `ROLE=store`; snapshots and manifests under `hosts/R/store/`; R's record copy |
| Restore host | `HOST_ID=RESTORE`, `ROLE=restore-host`; workspace `hosts/RESTORE/restore/`; **its environment names no path under `hosts/S/`** |
| Freshness checker | `HOST_ID=R`, `ROLE=freshness-checker`; writes marks into R's record copy |
| Notice channel | a harness-owned process, `HOST_ID=CHANNEL`; its record is `hosts/CHANNEL/record.jsonl` |

**The channel depends on S** under binding v1 (its record is on S). While S is suspended or crashed and not yet restarted, the channel is unreachable. BF1.7 makes it unreachable while S is up.

### 3.3 Environment given to each role process
`HARNESS_RUN_DIR`, `HOST_ID`, `ROLE`, `CLOCK_SOCK`, `TIMER_SOCK`, `CONTROL_SOCK`, `OBSERVE_SOCK`, `NET_SOCK`, `S_ADDR`, `R_ADDR`, `RESTORE_ADDR`, `CHANNEL_ADDR`, `BINDING_ID`, `PARAMS_JSON`; plus `SOURCE_DIR` on S only, `STORE_DIR` on R only, `RESTORE_DIR` on the restore host only, and `RECORD_PATH` on S and R.

### 3.4 The relay [A4, D9]
All communication between roles, notices included, goes through the relay at `NET_SOCK`, to the addresses above. The relay carries bytes. It imposes no protocol on them. It can drop all traffic between any two hosts (BF1.2), or refuse connections to the channel (BF1.7).

## 4. Implementation-side obligations (all of them)
| # | Obligation | Why |
|---|---|---|
| 1 | Run unprivileged as a child of the harness; use only the directories and sockets the environment names. | One machine, no root; injection and observation. |
| 2 | Read contract time only from `CLOCK_SOCK`. | Compression and BF1.6. |
| 3 | Register every timed wait with `TIMER_SOCK`, with a `kind`. | BF1.8. |
| 4 | Send all traffic between roles, notices included, through the relay. | BF1.2 and BF1.7 without root. |
| 5 | Keep each status-record copy at `RECORD_PATH` in the format of §6.2, written atomically (temporary file, then rename). | Observation; BF1.13. |
| 6 | Keep snapshots as ordinary files under `STORE_DIR/snapshots/<seq>/` and manifests at `STORE_DIR/manifests/<seq>.json` (§6.3). Inside a snapshot directory, the layout is free, but the harness must be able to restore from it by §6.6's rule. | BF1.3, BF1.10, BF1.12; observation; B1.3. |
| 7 | Keep sources under `SOURCE_DIR`, and the restore workspace under `RESTORE_DIR`. | BF1.5, BF1.9; the restore host's isolation. |
| 8 | Accept `ping`, `run.start` and `check.run` on `CONTROL_SOCK` (§4.2). | Deterministic points in a schedule. |
| 9 | Emit the observations of §4.3 on `OBSERVE_SOCK`. | `when` predicates and deadline starts. An observation not emitted makes the dependent event *unreached* (§1.4). |
| 10 | Send each notice as JSON with at least `clause`, `cause` and `seq` (§6.4). | B1.7 and B1.16 assertions. |
| 11 | Survive SIGKILL and restart, and SIGSTOP and SIGCONT. Treat a write error on the sandbox (`ENOSPC`, `EFBIG`, `EACCES`, `EROFS`) as a full disk, and a relay error as an unreachable host. | BF1.1, BF1.14, BF1.4, BF1.2. |
| 12 | **No side channels:** do not detect the harness, and do not bypass the clock, the timers, the relay or the channel. [D13] | A test-validity rule, not a design rule. |

Nothing else is prescribed: not the language, runtime or libraries; not the backup algorithm, scheduling or pruning policy, or storage engine; and not the protocol above the relay.

### 4.2 Control
JSON lines on `CONTROL_SOCK`: `{"op":"ping"}`, `{"op":"run.start"}` and `{"op":"check.run"}`, each answered with `{"ok":true}` as soon as it is accepted. `run.start` starts one run on S now, and `check.run` starts one checker pass on R now.

### 4.3 Observations
JSON lines on `OBSERVE_SOCK`. The harness appends each to `observations.jsonl` with `time` (global) and `host_time` (the sender's clock). The required kinds (`ObservationKind`) are:
`run.started`, `run.inventory_read`, `run.finished`, `restore_check.started`, `restore_check.finished`, `reverify.started`, `reverify.finished`, `prune.started`, `prune.finished`, `mark.written`, `notice.sent`, and `deadline.started`. The last is emitted by the checker when it starts measuring a deadline, with `clause`, `cause` and `seq`. Each carries `seq` where it has one.

## 5. Fault injection, every BF1 cell [A9]
The harness injects. It never asks the implementation to misbehave.

| Cell | Action | Mechanism | Ends |
|---|---|---|---|
| BF1.1 crash | `{"fault":{"cell":"BF1.1","host":"R","role":"store","restart":"immediate"|duration}}`, often with `when` (e.g. `prune.started`) | SIGKILL to the role's processes, then relaunch with the same environment | At restart |
| BF1.2 partition | `{"fault":{"cell":"BF1.2","partition":["S","R"],"duration":"48h"}}` or `"until"` | The relay drops all traffic between the two hosts, both ways. Both stay up, and their clocks run. | `duration` or `until` |
| BF1.3 corruption at R | `{"fault":{"cell":"BF1.3","host":"R","seq":50,"path":"...","offset":1024,"flip":"0xff"}}` | The harness flips bytes in a file under `hosts/R/store/snapshots/50/`. `path` may be `"*"`, meaning the harness picks the largest file. | Persists |
| BF1.4 disk full | `{"fault":{"cell":"BF1.4","host":"S"|"R","duration":"12h"}}` | `RLIMIT_FSIZE=0` (with `SIGXFSZ` ignored) on that host's processes, and its writable sandbox directories made read-only [D6] | `duration` or `until`: limits and permissions restored |
| BF1.5 source change during a run | a `source` action with `cell: "BF1.5"`, usually with `when: run.inventory_read` | Direct change under `hosts/S/sources/` | `once`, or `continuous` until `duration` or `until` |
| BF1.6 clock step | `clock.step` or `clock.set` | Changes one host's `C[h]`. Timers are recomputed. **The harness records the step in `clock-steps.jsonl`** [D8]. | Persists |
| BF1.7 channel down, S up | `{"fault":{"cell":"BF1.7","duration":"6h"}}` | The relay refuses connections to `CHANNEL_ADDR`. Nothing reaches the channel's record. | `duration` or `until` |
| BF1.8 timer fails | `{"fault":{"cell":"BF1.8","host":"S","kind":"run","count":1}}` | The next `count` wakeups of that (host, kind) are recorded as `timer.dropped` in `observations.jsonl` and not delivered. With `"count":"all"`, every one is dropped until `until`. | After `count`, or `until` |
| BF1.9 source damaged | a `source` action with `cell: "BF1.9"`: `move_tree`, `empty_tree`, `truncate_tree`, `delete` | Direct change under `hosts/S/sources/` | Persists until a later source action |
| BF1.10 R reimaged | `{"fault":{"cell":"BF1.10","host":"R"}}` | Deletes everything under `hosts/R/store/snapshots/` and `hosts/R/store/manifests/`. **R's record copy is untouched.** To lose it as well, inject BF1.13 on copy R in the same instant [D7]. | Persists |
| BF1.12 snapshots lost | `{"fault":{"cell":"BF1.12","host":"R","seqs":[50,51]}}` | Deletes those snapshot directories and manifests | Persists |
| BF1.13 record lost or corrupted | `{"fault":{"cell":"BF1.13","copy":"S"|"R"|"both","mode":"lost"|"corrupt"}}` | `lost`: the file is deleted. `corrupt`: bytes are flipped so its hash fails. | Persists; never repaired by the harness |
| BF1.14 host suspended | `{"fault":{"cell":"BF1.14","host":"RESTORE","duration":"48h"}}` | SIGSTOP to all the host's processes. Its clock keeps advancing [D3]. Its timer wakeups due during the suspension are delivered at SIGCONT, in deadline order. | `duration` or `until`: SIGCONT |

## 6. Observation formats
### 6.1 `observations.jsonl`
One JSON object per line: `{"time": rfc3339, "host_time": rfc3339, "host": HostId, "kind": "...", "seq": n, ...}`. It also holds the harness's own lines: `timer.dropped`, `event.ran`, `event.unreached` and `fault.injected`.

### 6.2 Status record copy [A5]
```json
{ "entries": [
    { "kind": "run",  "seq": 50, "status": "started"|"ok"|"failed", "stage": "unknown"|"source"|"capture"|"no-credentials"|"...", "time": rfc3339, "writer": "S" },
    { "kind": "mark", "seq": 50, "mark": "restore-checked"|"restore-failed"|"not-restore-checked"|"damaged"|"missing", "time": rfc3339, "writer": "checker"|"restore"|"R" } ],
  "hash": "sha256:<hex>" }
```
`hash` is SHA-256 over the canonical JSON of `entries` (sorted keys, no whitespace), recomputed at every update. Entries are in append order. The implementation may keep further fields in an entry, which the harness ignores.

### 6.3 Manifest
```json
{ "seq": 50, "created_time": rfc3339,
  "inventory": [ { "type": "file", "path": "..." }, { "type": "git-ref", "repo": "tupay.git", "ref": "refs/heads/main", "object": "<oid>" } ],
  "files": [ { "type": "file", "path": "...", "sha256": "<hex>", "status": "present"|"gone" },
             { "type": "git-ref", "repo": "tupay.git", "ref": "...", "object": "<oid>", "status": "present"|"gone" } ] }
```
`manifest_complete(seq)`: every `inventory` entry has a matching `files` entry, by path or by (repo, ref), with status `present` or `gone`.

### 6.4 The channel's record [A6]
`hosts/CHANNEL/record.jsonl`, one notice per line: `{"n": 1, "clause": "B1.7", "cause": "...", "seq": 50, "arrival_time": rfc3339, "arrival_host_time": rfc3339, "sender_host": "R", "body": { }}`. `arrival_host_time` is read on the clock of the binding's channel-record host, which is S under binding v1. **A notice reaches the channel exactly when this record holds it.**

### 6.5 Marks and B1.19 [D4]
At any assertion time:
```text
present(seq)          = hosts/R/store/snapshots/<seq>/ and hosts/R/store/manifests/<seq>.json exist
marks(seq)            = the mark entries for seq in R's record copy, in append order
latest_check(seq)     = the last mark in marks(seq) that is restore-checked or restore-failed
marks_restorable(seq) = present(seq) and latest_check(seq) = restore-checked
                        and no damaged or missing mark follows it in marks(seq)
```
If R's record copy is lost or fails its hash, `marks_restorable` is false for every `seq` until a valid copy exists again.

### 6.6 The harness's independent restore [D4, D12]
At a `query` event and, at the horizon, for every `seq` named by a `restores` assertion, the harness copies `hosts/R/store/snapshots/<seq>/` to `harness/restores/<seq>/` and checks it against the manifest. Every `present` file entry must hash to its `sha256` at the path it names inside the snapshot directory. Every `present` git-ref entry must resolve, in a repository restored from the snapshot, to its `object`. That repository is either a bare repository at the repo's path, or a git bundle at `<repo path>.bundle`, cloned with `git clone`. It records `{"seq": n, "time": rfc3339, "result": "restores"|"does-not-restore", "diff": [ ... ]}` in `results.json`. This check runs with the harness's own tools, never the implementation's.

### 6.7 `clock-steps.jsonl` [D8]
`{"time": rfc3339, "host": HostId, "delta": signedDuration}`, one line per BF1.6 injection.

## 7. Scoring
Each assertion is scored at its `at` as `pass`, `fail`, `unreached` (§1.4), `censored` (§1.6) or, for a model, `unsupported` (§8). `results.json` holds the assertion results, the horizon, a recoverability table (`present`, `marks_restorable` and `restores` per `seq`), the censored windows, and a coverage map: the BF1 cells injected and the `derives:` tags asserted.

Deadline comparisons in `notice_reached` use the referenced observation's `host_time` plus `within`, against the notice's `arrival_host_time`. A reference to a mark uses the checker's `deadline.started` observation for it when one exists, and otherwise the mark entry's `time`.

## 8. Model runners [A10]
A model's runner accepts the same schedule JSON. It validates it against §1, resolves `binding` and `params` to the same values, and gives events and assertions their abstract meaning: virtual time, per-host clocks, `when` predicates, fault cells and the horizon. In a model, `marks_restorable` and `restores` are state predicates the model defines, and `restores` stands for the harness's independent check. The runner writes a `results.json` in §7's format, or, for whatever it cannot express:
```json
{ "status": "unsupported", "schedule": "<id>", "unsupported": [ { "id": "<event or assertion id>", "field": "...", "reason": "..." } ] }
```
It exits with status 3. It never skips an event or an assertion silently. Every assertion that depends on an unsupported item is scored `unsupported`.

## 9. Harness obligations
1. Create the run directory (§3.1), build the world (§1.3), and launch every role with its environment (§3.3).
2. Provide the clock, timer, control, observation and relay services (§§2 to 4) and the channel process.
3. Validate the schedule against §1, rejecting retired ids and untagged assertions.
4. Run events in order: compute each event's earliest time, advance virtual time to it while firing timers in host-clock deadline order, then wait on `when` in 1-minute virtual steps up to `timeout`, then execute or mark *unreached*.
5. Inject every cell as §5 says, without the implementation's cooperation.
6. Record everything in §6's formats, and never change the implementation's files except by an injection.
7. After the last event, compute the horizon (§1.6), advance to it, run the independent restores (§6.6), evaluate assertions, and write `results.json`.
8. Run the same schedule text unchanged against every implementation, and give model runners the identical file.
9. Need no root, mounts, namespaces or firewall rules, and run a schedule of several weeks in minutes.
