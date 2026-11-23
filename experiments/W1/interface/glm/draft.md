# Shared Test Interface Specification
**sti-v1.md** — for contract-P.md (draft 7) and binding-tupay.md (v1). This document specifies the interface only. It prescribes no protocol, no storage format, no tooling inside an implementation, except where explicitly marked **CONSTRAINT** with a reason.

---

## 0. Overview

A **test** runs one **implementation** (a program, or a formal model) against one **schedule**. The schedule is a text file. The **harness** is the program that reads the schedule, sets up the world, feeds time and events to the implementation, injects failures, records observations, and scores assertions.

Everything the implementation sees of the world — time, files, network, the notice channel — it sees **through the harness**. This is the one structural constraint of the interface, and it exists for one reason: the harness must be able to inject every BF1 cell and observe every outcome without the implementation's cooperation. An implementation that talks to real clocks, real disks and real networks directly cannot be tested by a shared suite, because the harness could neither step a clock nor corrupt a byte.

---

## 1. Time

### 1.1 Virtual time

All time in a test is **virtual**. The harness owns a single logical timeline, measured in **virtual hours** from an epoch `t=0` (which the schedule may label with a UTC date, e.g. `2026-11-01T00:00:00Z`, for daily/monthly reasoning). One virtual hour can elapse in milliseconds of wall time.

### 1.2 Per-host clocks

Each host (S, R, restore host, checker — see §2) has its own **clock offset** from the timeline. A clock step (BF1.6) changes a host's offset. When the harness asks "what time is it on host H", the answer is `timeline + offset[H]`. Ages measured by the implementation on H's clock are therefore wrong by up to the step size, exactly as the contract allows.

### 1.3 How time is given — CONSTRAINT

> **CONSTRAINT C1.** The implementation must obtain the current time **only** by calling the harness's clock service for the host it runs on, and must not cache a time value across an operation that can be preempted by the harness.
> *Why:* BF1.6 requires the harness to step any host's clock at any moment, including mid-run. If the implementation reads a real clock or caches one, a step has no effect and BF1.6 is untestable.

Mechanically, the harness exposes, on each host's environment:

- a file `CLOCK` in the harness control directory (see §2.3), containing the current virtual time for that host in ISO-8601 UTC, rewritten by the harness whenever it advances; **or**
- a `gettime` request on the same channel the implementation uses for other harness services (§2.3).

Either transport is acceptable; the schedule and scoring do not care. What is mandatory is *single-sourced time*.

### 1.4 How time advances

The harness advances time in **ticks** driven by the schedule (§3, `at` fields). Between ticks the harness may also advance time while waiting for the implementation to finish an action (see §4.4, *run-to-completion*). The harness never advances time while an injected fault is "in flight" unless the schedule says so.

---

## 2. Hosts and roles

All roles run on one physical machine, as one unprivileged user. Each role is:

| Contract role | In a test |
|---|---|
| **S (source host)** | a directory `S/` containing `S/sources/` (the source trees, including the git repo), `S/record/` (S's copy of the status record), `S/log/` (logged reasons), and the implementation's S-side component. |
| **R (store)** | a directory `R/` containing `R/snapshots/`, `R/record/` (R's copy of the status record), and the implementation's R-side component. "Network" between S and R is a harness-controlled gate (§5, BF1.2). |
| **Restore host** | a directory `RH/`, empty of sources, with the implementation's restore-side component. Its only access to R is through the same gate. It has **no path to `S/sources/`** — the harness enforces this by never exporting that path to it (AI1.4 is the implementation's problem; the harness's job is not to *give* it a path). |
| **Freshness checker** | the implementation's checker component, running "on R" (per the binding): its process/files live under `R/`. |
| **Notice channel** | a harness-owned directory `CHANNEL/`. A notice "reaches the channel" when a file appears in `CHANNEL/inbox/` (§6.1). Per the binding, the channel's record is on S, so `CHANNEL/` is placed under `S/` in the directory layout — the harness models the dependency by making channel delivery subject to S's availability gate. |

### 2.1 Telling the implementation where things are

The harness writes a single **environment file** `ENV.json` (path given to the implementation at start, by argv or env var `STI_ENV`):

```json
{
  "role_dirs": {"S": "…/S", "R": "…/R", "RH": "…/RH", "channel": "…/S/CHANNEL"},
  "sources": ["sources/tupay.git", "sources/tupay-private", "sources/tupay-homes"],
  "params": {"I": 24, "M": 24, "P": 168, "H": 36, "D": 1, "X": 2,
             "Rb": 48, "G": 96, "Q": 0.05, "K": 336, "Mo": 6,
             "Dmax": 27, "T": 51},
  "clock": {"transport": "file", "path_per_host": {"S": "…/S/CLOCK", "R": "…/R/CLOCK", "RH": "…/RH/CLOCK"}},
  "api_version": "sti-v1"
}
```

Units: hours for *I, M, P, H, D, X, Rb, G, Dmax, T, K*; *Mo* in months; *Q* a fraction. The harness fills these from the binding; a schedule may override them (§3) so models and implementations see identical numbers.

### 2.2 What the implementation exposes — CONSTRAINT

> **CONSTRAINT C2.** The implementation must be startable as one or more processes with a documented entry point per role, taking only: the ENV path, the role to run, and a subcommand vocabulary limited to `run` (a backup run on S), `check` (one freshness-checker pass on R), `restore-check` (one restore check of a named snapshot on RH), `reverify` (one re-verification pass on R), and `daemon` (whatever periodic behaviour the implementation has). Timers (BF1.8) are the harness's to fire or not fire: the harness invokes `run`/`check`/`restore-check`/`reverify` at the moments the implementation's configuration says they are due, and BF1.8 is injected by *not* invoking them.
> *Why:* the contract prescribes no protocol, so the interface cannot observe internals; but the harness must be able to (a) start each role, (b) decide when periodic actions are due, and (c) withhold them, or no deadline clause and no BF1.8 cell is testable. This constrains *invocation*, not internals.

The implementation declares its due-times in `ENV-impl.json` (written by the implementation at setup): `{"run_interval": I, "checker_interval": ≤D, "reverify_interval": P, "restore_check_policy": "on-ok-entry"}`. The harness uses these only to schedule invocations.

### 2.3 Harness control directory

Each host directory contains `CTL/` with `CLOCK` and a FIFO or socket `EVT` on which the harness can deliver out-of-band events (currently only "wake", used after un-suspending a host). Nothing else is ever required of the implementation's internals.

---

## 3. Schedule format

A schedule is a single YAML document (schema below; normative grammar in Appendix A). Top-level keys:

```yaml
schedule: <id-string>
binding: tupay-v1            # informational; params below are what count
params: {…}                  # overrides of ENV params, same units
epoch: "2026-11-01T00:00:00Z"
world:                       # initial source content, declared as a tree spec
  - {path: sources/tupay-private/, type: dir, files: 40, bytes: 200000}
  - {path: sources/tupay.git, type: git, refs: {main: "abc123"}}
  - {path: sources/tupay-homes/a/t.jsonl, type: append-file}
events: [ … ]                # the scenario, in timeline order
horizon: 240                 # virtual hours after the last event; scoring time
asserts: [ … ]               # scored at the horizon (and at `at` times if given)
```

### 3.1 Events

Each event is one of (all times are virtual hours from epoch, `at` is required and events are sorted by it):

- **`source`** — mutate sources: `{at, action: create|delete|rename|append|rewrite-in-place|truncate|move-tree|update-ref, path, [to], [ref], [oid], [rate]}`. `rewrite-in-place` with `rate: continuous` reproduces worked case 8; with `rate: once` it rewrites once mid-run.
- **`inject`** — a BF1 cell: `{at, cell: BF1.x, target: S|R|RH|channel|record-S|record-R|snapshot|disk, [args], [until]}`. Semantics per cell in §5. `until` (a time, or `next-event`, or `forever`) ends it.
- **`timer`** — fire or skip a due invocation: `{at, kind: run|check|reverify|restore-check, fire: true|false, [snapshot: n]}`. If a schedule contains no `timer` events, the harness fires everything on time (BF1.8 not exercised).
- **`crash`** — BF1.1: `{at, target: S|R|RH|checker, [during: run|prune|restore-check|reverify]}`. See §5.
- **`query`** — force an observation point: `{at, what: restore-check|record|channel, [snapshot: n]}`. A `query` of `restore-check` makes the **harness itself** perform an independent restore check (§6.3) — this never counts as the implementation's B1.8 check.

### 3.2 Assertions

```yaml
- {derives: B1.19, at: 96, claim: "violated", cause: "restore checks failing"}
- {derives: B1.7,  claim: "notice-exists", clause: B1.8, within: 1, of: "ok-entry n=70"}
- {derives: B1.4,  claim: "snapshot-present", n: 59}
- {derives: B1.17, claim: "manifest-complete", n: 50}
- {derives: B1.6,  claim: "record-never", entry: {n: 44, status: failed-after-ok}}
```

The assertion vocabulary (closed set, Appendix B) is over **harness-observable facts only** (§6): notice records, record entries and marks, snapshot presence, manifest contents, harness restore-check results, clock-step error reports. Each assertion carries exactly one `derives:` tag naming the clause (or failure-model cell, e.g. `derives: BF1.6`) it checks. Assertions without `at` are scored at the horizon; the horizon is fixed per schedule and is the time at which **recoverability** (B1.3/B1.19) is judged.

### 3.3 Complete example schedule

```yaml
schedule: worked-cases-2-and-3
binding: tupay-v1
params: {}                      # binding values stand
epoch: "2026-11-01T00:00:00Z"
world:
  - {path: sources/tupay.git, type: git, refs: {main: "abc123"}}
  - {path: sources/tupay-private/, type: dir, files: 40, bytes: 200000}
events:
  # bootstrap: three good daily runs
  - {at: 0,   timer: {kind: run, fire: true}}
  - {at: 24,  timer: {kind: run, fire: true}}
  - {at: 48,  timer: {kind: run, fire: true}}
  # worked case 2: run 60 acknowledged 11:20 day 3; corrupt one file at R before its check
  - {at: 59.33, timer: {kind: run, fire: true}}                 # run 60, ok at 59.33
  - {at: 60,  inject: {cell: BF1.3, target: snapshot, snapshot: 60,
                       args: {file: "tupay-private/notes.md", mode: flip-byte}}}
  - {at: 61,  timer: {kind: restore-check, fire: true, snapshot: 60}}   # fails at 13:00
  # worked case 3: suspend the restore host from 12:00 day 3 to 09:00 day 5
  - {at: 60,  inject: {cell: BF1.14, target: RH, until: 129}}
  - {at: 72,  timer: {kind: run, fire: true}}                   # run 61
  - {at: 96,  timer: {kind: run, fire: true}}                   # run 62
  # a clock step on R mid-story (BF1.6, +24h)
  - {at: 100, inject: {cell: BF1.6, target: R, args: {step: +24}}}
  - {at: 120, timer: {kind: run, fire: true}}
  - {at: 129, inject: {cell: BF1.14, target: RH, until: 0}}     # end suspension
  - {at: 130, timer: {kind: restore-check, fire: true, snapshot: 61}}
horizon: 240
asserts:
  - {derives: B1.8,  claim: "mark-exists", n: 60, mark: restore-failed}
  - {derives: B1.7,  claim: "notice-exists", clause: B1.7, trigger: "snapshot 60 restore-failed", within: 1}
  - {derives: B1.3,  claim: "not-restorable", n: 60}
  - {derives: B1.4,  claim: "snapshot-present", n: 59}
  - {derives: B1.7,  claim: "notice-exists", clause: B1.19, trigger: "overdue", within: 1,
                     of: "ok-entry n=59 age 96"}                # scored at its `at`/horizon
  - {derives: B1.19, claim: "violated", at: 96, cause: "restore host suspended"}
  - {derives: BF1.6, claim: "clock-error-reported", host: R, step: 24}
  - {derives: B1.12, claim: "mark-exists", n: 60, mark: damaged}  # reverify finds the flip
```

This injects BF1.3, BF1.14 and BF1.6, and exercises B1.3/B1.4/B1.7/B1.8/B1.12/B1.19.

---

## 4. Implementation-side contract (the whole of it)

An implementation must obey **only** these; nothing else about its internals is constrained:

1. **C1 — time** (§1.3): read time from the harness clock for the host you run on; don't cache across preemptible operations.
2. **C2 — entry points** (§2.2): expose `run`, `check`, `restore-check`, `reverify`, `daemon`, `setup`; declare due-intervals in `ENV-impl.json`.
3. **C3 — network through the gate**: all S↔R and RH↔R traffic goes through the harness's gate endpoint (a local socket/port the harness proxies). The implementation is told the endpoint in `ENV.json`. *Why:* BF1.2 (partition) and BF1.7 (channel down) are injected at the gate; there is no other place a harness can partition two processes on one machine without root.
4. **C4 — record readability**: both copies of the status record, and each snapshot's manifest, must be readable as **plain files** by an unprivileged reader, in the record/manifest **exchange format** of §6.2. *Why:* every B1.6/B1.13/B1.17/B1.18 assertion and the sequence-number cases are scored from the record and manifests; the harness cannot parse fourteen different private formats. This constrains the *copy's* file format, not the service's internal state.
5. **C5 — notices**: a notice is delivered by writing one file to `CHANNEL/inbox/` in the notice format of §6.1. *Why:* B1.7/B1.16 assertions need the clause id and arrival time; the channel is a contract role, so fixing its test-side shape is observation, not protocol prescription.
6. **C6 — no side channels**: the implementation must not detect the harness (e.g. by probing for it) or bypass the gate, the clock, or the channel. This is a test-validity rule, not a design rule.

That is all. Storage layout inside `R/snapshots/`, dedup, encryption-at-rest (EX1.7 says none), transport protocol, language, process model: all free.

---

## 5. Fault injection, cell by cell

| Cell | Injection | End |
|---|---|---|
| **BF1.1** crash | Harness SIGKILLs the named role's process(es) at the scheduled instant; optionally only when the role is in the named stage (the harness detects stage via the record's stage field, C4). Restart is the harness's next `timer` invocation of that role, or a `query`. | At restart. |
| **BF1.2** partition | Gate drops all packets between the named pair, both directions. | `until` time or next event. |
| **BF1.3** corrupt bytes | Harness rewrites bytes inside `R/snapshots/<n>/` (flip a byte in a named file, or truncate). The implementation is not told. | Permanent; discovered by reverify/restore-check or never. |
| **BF1.4** disk full | Harness sets a quota (via a small FUSE-free trick: a loopback file mounted without root is impossible, so the harness pre-allocates the target directory's free space with a sparse-then-filled filler file, and/or the gate returns ENOSPC on writes above a threshold — the gate is the enforcement point). | `until`; harness frees the filler. |
| **BF1.5** source churn | `source` events (§3.1) at times that land mid-run. | The event itself. |
| **BF1.6** clock step | Harness changes `offset[target]` by ±1 or ±24 h; the host's `CLOCK` jumps. The harness itself records the step in `OBS/clock-steps.jsonl` (the "error is reported" requirement is on the *test report*, not the implementation). | Instantaneous. |
| **BF1.7** channel down | Harness makes `CHANNEL/inbox/` unwritable (chmod 000 is not needed: the gate refuses writes to it) while S stays up. B1.16's hold-and-redeliver is the implementation's job. | `until`; then the harness checks delivery within *D*. |
| **BF1.8** timer fails | Harness simply does not fire the due `timer` invocation. | Next fired invocation of that kind. |
| **BF1.9** source damaged | `source` events: `truncate`, `move-tree`, `empty`. | The event. |
| **BF1.10** R reimaged | Harness deletes all of `R/snapshots/` and `R/record/` contents (keeping the implementation's R-side *program* — the machine is replaced, not the software). | Instantaneous. |
| **BF1.12** snapshots lost | Harness deletes `R/snapshots/<n>/` for chosen n. | Instantaneous. |
| **BF1.13** record lost/corrupted | Harness deletes or byte-corrupts `S/record/`, `R/record/`, or both. Corruption is "wrong but consistent" only if the schedule says `mode: consistent-rewrite`; default is hash-breaking corruption. | Instantaneous; recovery is the implementation's. |
| **BF1.14** suspend | Harness SIGSTOPs all processes of the target host and freezes its `CLOCK` (time on that host does not advance — a suspended box's clock is stopped). Other hosts' clocks continue. | `until`; SIGCONT + clock unfreeze + `wake` on `EVT`. |

Note on BF1.14 + deadlines: the checker runs on R; if R is suspended, "nothing promises any detection time while R is down" — the harness simply scores notices by R's own clock, and the contract's wording governs.

---

## 6. Observation

All observations are written by the harness into `OBS/`:

### 6.1 Notice channel record — `OBS/channel.jsonl`

One line per notice that **reached** the channel (a file appeared in `CHANNEL/inbox/`), recorded at the moment of arrival, with the harness's timeline time **and** the channel host's own clock reading (they differ after a step):

```json
{"t": 61.4, "host_clock": "2026-11-03T13:24Z", "clause": "B1.7",
 "trigger": {"kind": "restore-failed", "snapshot": 60},
 "cause": "one file differs", "sender": "RH", "raw": "<original file name>"}
```

`clause` is parsed from the notice file's required header line `clause: B1.x` (C5). `trigger`/`cause` are parsed from required fields `trigger:` and `cause:` in the notice file. The raw file is kept.

### 6.2 Record and manifests — the exchange format (part of C4)

The status record copy is a file `record.jsonl` (one JSON object per line, append-ordered) with exactly these entry shapes:

- run entry: `{"n": 43, "kind": "run", "status": "started|ok|failed", "stage": "…|unknown", "t": <host time>, "writer": "S"}`
- mark: `{"n": 60, "kind": "mark", "mark": "restore-checked|restore-failed|not-restore-checked|damaged|missing", "t": <host time>, "writer": "checker|reverify|RH"}`
- hash line: `{"kind": "hash", "h": "<sha256 over all preceding lines>"}` — rewritten at each update per B1.18.

A manifest is `manifest.jsonl` at the snapshot root: one line per path `{"path": "...", "sha256": "…", "state": "present|gone"}`, plus a header line carrying the run's source inventory (same paths, and for git the `(ref, oid)` pairs). This is the *minimum* the harness must be able to read; an implementation may keep more alongside.

The harness snapshots (copies) both record files and all manifests into `OBS/` at every event time and at the horizon, so assertions can be evaluated offline.

### 6.3 Independent recoverability — `OBS/restore.jsonl`

At each `query: restore-check` and at the **horizon**, the harness performs its own restore check of each snapshot named by an assertion: copy `R/snapshots/<n>/` to a scratch dir, clone any bundle, rehash every file against the manifest (on the harness's own tooling — AI1.2 is about R's tool, and the harness is "elsewhere"). Result line: `{"n": 60, "t": 240, "result": "restorable|not-restorable", "diff": [...]}`. This is the **only** evidence a B1.3/B1.19 assertion may cite; the implementation's own marks are cited only for B1.8/B1.6/B1.12/B1.13 assertions.

### 6.4 Clock steps — `OBS/clock-steps.jsonl`

`{"t": 100, "host": "R", "step": 24}` — the BF1.6 "error is reported" record.

---

## 7. Scoring

Each assertion is scored PASS/FAIL/NA at its `at` (or the horizon). A schedule's result is the list of `(tag, verdict)`. The harness also emits a **coverage map**: which BF1 cells were injected and which `derives:` tags appeared. NA is used only when the assertion's precondition event did not occur (e.g. the run it names never started because a prior crash was scheduled) — the harness records why.

---

## 8. Models

A formal model (TLA+ or other) runs the **same schedule text** through the model's own runner, which must accept:

- `params`, `epoch`, `events` (all kinds; a model may treat `source` events abstractly as inventory deltas),
- `horizon`,
- `asserts` with their `derives:` tags, evaluated against the model's abstract versions of the observables: the channel record, the record entries/marks, snapshot presence, and an *oracle* restore-check (in a model, "restorable" is a state predicate the model defines; the harness's independent check corresponds to it).

**Refusal protocol:** if the model cannot express part of a schedule, its runner must emit, for each offending item, a line `UNSUPPORTED <schedule-id> <line-or-key> <reason>` and score every assertion whose `derives:` clause depends on the unsupported construct as `NA-UNSUPPORTED`, never as PASS. Models must not silently drop events. A model that supports only a subset of the assertion vocabulary declares that subset in a manifest `model-capabilities.json`; the shared suite's coverage map then shows which schedules are fully model-checked.

---

## 9. Harness's obligations

1. Build the world (§2) from `world`, start the implementation via its declared entry points, hand it `ENV.json`.
2. Advance virtual time only per §1.4; maintain per-host offsets; freeze clocks of suspended hosts.
3. Fire `timer` invocations exactly when due per `ENV-impl.json`, unless the schedule says otherwise; never fire them during a suspension of that host.
4. Inject every event exactly once, at its `at`, in order; end injections at their `until`.
5. Record all observables (§6) at every event time and at the horizon; never modify the implementation's files except as an explicit injection.
6. Perform independent restore checks only at `query` events and the horizon.
7. Score assertions, emit the result list, coverage map, and the clock-step report.
8. Run without root, on one machine, in minutes for multi-week schedules.

---

## OPEN CHOICES

1. **Schedule syntax: YAML.** Options: YAML, JSON, custom DSL, TLA+ module. Chose YAML: human-writable, machine-parseable everywhere, comments; JSON lacks comments; a DSL needs its own tooling (prescription risk); TLA+ would prescribe a model tool.
2. **Virtual time driven by the harness, not by the implementation sleeping.** Options: real-time-compressed (sleep-based), virtual clock service, LD_PRELOAD clock shim. Sleep-based cannot do weeks in minutes reliably; LD_PRELOAD prescribes a platform and language family. The clock service (C1) is the least-prescriptive single-source option.
3. **Per-host clock offsets with frozen clocks under suspension.** Options: shared timeline only; per-host offsets. The contract explicitly measures ages on each host's own clock and injects per-host steps, so offsets are forced; freezing a suspended host's clock was my choice (a suspended machine's clock arguably stops) — the alternative (clock keeps running) changes BF1.14 semantics materially.
4. **Timer invocation by the harness (C2).** Options: implementation runs its own timers; harness fires invocations. Own timers make BF1.8 (timer fails to fire) injectable only by killing timers, which is fragile and platform-specific; harness-fired timers make BF1.8 trivial and deterministic. Cost: the interface constrains invocation, which I flagged as C2 with its reason.
5. **Network gate (C3).** Options: gate proxy; iptables (needs root); separate network namespaces (needs root); "trust the implementation to honour a partition flag". Only the gate works unprivileged and without cooperation.
6. **Disk full via filler file + gate ENOSPC.** Options: FUSE (root-ish, kernel deps), loopback mount (root), quota (root), filler+gate. Imperfect (an implementation could write elsewhere) but the only root-free option; noted as a soft injection.
7. **Exchange formats for record/manifest/notices (C4, C5).** Options: require plain JSONL; require only "documented format" per team; scrape logs. Documented-per-team breaks the one-shared-suite requirement (the harness would need N parsers, and models N more); log-scraping is brittle. JSONL is the minimum that both a harness and a TLA+ runner can read. This is the interface's largest constraint on implementations, and it is justified purely by observation needs.
8. **Channel record placed under S (binding says the plaza's record is on S).** Options: channel independent of S; channel on S. The binding fixes this ("Its record is on S, so EX1.6 applies"), so the test world mirrors it; EX1.6 then applies to tests too.
9. **Independent harness restore check as the only B1.3/B1.19 evidence.** Options: trust the implementation's restore-check marks; harness re-checks. The contract itself says "Only a passing restore check is evidence of that" and AI1.2 distinguishes R's tool from elsewhere — the harness is the elsewhere.
10. **Assertion vocabulary as a closed set.** Options: closed vocabulary; free-form predicates (e.g. embedded Python). Free-form breaks model runners and portability; closed set is translatable into TLA+ predicates.
11. **Models report refusal per-item with NA-UNSUPPORTED, never silent drops.** Options: refuse whole schedule; skip silently; per-item NA. Per-item NA maximizes shared coverage while keeping the coverage map honest.
12. **`query` events separate from `timer` events.** Options: one event kind. Separating "make the implementation act" from "make the harness observe" keeps observation clearly outside the implementation.
13. **BF1.1 crash by SIGKILL at a scheduled time, stage detected via the record.** Options: crash hooks inside the implementation (needs cooperation, violating requirement 3); random crashes (nondeterministic). SIGKILL needs no cooperation; stage-conditional crashes are best-effort and noted as such.

## CONTRACT QUESTIONS

1. **B1.16 / BF1.7 — where does the checker "read" held notices?** "the sender keeps the notice where the checker reads" — but the binding puts the channel's record on S, and the checker on R. When S is up and the channel is down, who holds the notice, and on which host? I could not design the BF1.7 injection's observation (whether a held notice is observable before delivery) without knowing this.
2. **B1.7 — "B1.19 being violated" as a trigger.** B1.19 is a state ("there is always a protected snapshot…"), not an event. When exactly does the *event* that starts the *D* clock occur — the moment the newest recoverable snapshot's ok-entry passes *G*, or the moment the checker first observes that it has? The two differ under BF1.14 (R suspended) and the Deadlines paragraph says detection is not promised while R is down, but B1.19's trigger time still needs a definition for scoring.
3. **B1.8 — the start of *M*.** "within *M* of its *ok* entry" — the ok entry's time is written by S on S's clock; the deadline is measured by the checker on R's clock. After a BF1.6 step on either host, which reading of "within *M*" governs? The contract allows error "up to the size of the step", but a test needs to know which side's clock the assertion uses.
4. **B1.18 — "both copies are intact but disagree."** Disagree *about what*? The hash covers "its entries", but S's copy holds run entries and merged marks while R's holds marks and copied run entries. May two intact copies legitimately differ (S ahead after a run, before the copy lands)? If so, "disagreement" must mean something narrower (same entry, different content), and the boundary is not stated. This blocks designing the BF1.13 `consistent-rewrite` injection precisely.
5. **B1.4 — "the first daily snapshot of each month for *Mo* months."** With clock steps (BF1.6) a UTC day boundary can be crossed twice or never on a host. Which host's clock defines the UTC day of a snapshot's ok entry, given the entry time is written on S but daily snapshots are presumably identified by the checker on R?
6. **B1.15 — *Q* "measured on the binding's own history."** The comparison baseline is "the previous acknowledged snapshot", but *Q*'s noise band was measured on bundle size, while the clause compares "file count and bytes". Is the *Q* test on count and bytes separately, either, or the larger? The worked cases do not cover it, and the assertion needs the formula.
7. **BF1.10 — "R is reimaged or replaced."** Does the *status record's* R copy survive (it is "R's copy", stored at R)? Worked case 4 implies R's record can exist independently, but BF1.10 says "all its snapshots are lost" and is silent on the record. The injection differs materially (delete `R/record/` or not).
8. **B1.9 — the interval's starting event.** "over an interval of *I* + *X*" starting when? At the previous ok entry, at the start of the run that produces it, or at an arbitrary point the test chooses? The premise's start determines when the assertion's clock starts, and the text does not fix it.

---

### Appendix A — normative grammar (abridged)

```
schedule    := "schedule:" id  binding?  params?  epoch?  world  events  horizon  asserts
event       := source | inject | timer | crash | query
inject      := {at: num, cell: "BF1." ("1"|"2"|"3"|"4"|"5"|"6"|"7"|"8"|"9"|"10"|"12"|"13"|"14"),
                target: id, args?: map, until?: num | "next-event" | "forever"}
assert      := {derives: id, claim: claim-id, at?: num, …claim-args}
claim-id    := notice-exists | notice-absent | mark-exists | record-never | record-entry |
               snapshot-present | snapshot-absent | manifest-complete | manifest-lists-gone |
               restorable | not-restorable | violated | held | clock-error-reported |
               sequence-next | prune-kept | rebuild-within
```

### Appendix B — assertion vocabulary (summary)

Each claim is defined over `OBS/` facts only; full definitions in the harness reference. `notice-exists` requires clause, trigger, and (optionally) `within` hours `of` a named event; `restorable`/`not-restorable` cite only `OBS/restore.jsonl`; `mark-exists`/`record-*` cite the record exchange format; `manifest-*` cite manifests; `sequence-next` checks the next run's number against max over both records and snapshot names (worked case 4); `rebuild-within` checks both-lost recovery inside *Rb* with pruning frozen.

---

*End of sti-v1.*