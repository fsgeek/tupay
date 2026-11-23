## Findings

The interface is not ready for W1. The blocking problems include the core completeness/recoverability predicates, notice and clock scoring, and deterministic schedule execution. I distinguish a restricted but valid fault variant from a forced contract reading in the contract-question tables below.

**1. Kind 2 — blocking. Where: §6.3 and §6.6, `manifest_complete` and `restores`.**  
**What/why:** Completeness is checked entirely against the implementation’s own manifest: “every `inventory` entry has a matching `files` entry … with status `present` or `gone`.” An implementation can omit a source path from both arrays, or mark every existing path `gone`, and pass; the independent restore then checks only the remaining `present` entries. It also accepts `gone` git refs despite B1.2’s “refs are exactly those pairs,” does not reject extra restored refs, and has no evidence that a file’s contents were a version that existed or were untorn. Thus the suggested predicates do not establish B1.17 or B1.2.  
**Fix:** Compare against a harness-derived inventory and source-version log, validate every `gone` against a post-inventory deletion, and compare restored files and the complete git ref set bidirectionally.

**2. Kind 2 — blocking. Where: §6.5 and §1.5, `marks_restorable` and `recoverable_exists`.**  
**What/why:** `marks_restorable` omits B1.3’s “protected” precondition and does not require an *ok* entry. Consequently the prescribed B1.3 implication can apply to an unacknowledged snapshot that B1.3 does not cover. `recoverable_exists` adds an unspecified “*ok* entry” without saying which copy is authoritative, which clock measures “younger,” or how B1.19’s initial activation is determined. In addition, “If R’s record copy is lost … `marks_restorable` is false” can make `recoverable_exists` false even when S’s surviving copy contains the relevant run entries and merged marks. These are not merely conservative under-approximations: they can produce false B1.19 failures.  
**Fix:** Separate raw protection/check/age observations from the B1.3/B1.19 predicates and score those predicates only where their record-copy, activation, and clock readings are fixed or explicitly quantified over.

**3. Kind 3 — significant. Where: §6.5, mark ordering.**  
**What/why:** “marks(seq) = … in append order” and “no damaged or missing mark follows it” choose record-order semantics for “latest” and “since.” Contract question 23 expressly leaves record order versus timestamp order unresolved; under BF1.6 they diverge. A schedule cannot use `any` to repair this because the interface supplies only the append-order predicate.  
**Fix:** Expose the raw ordered marks and either provide both reading-specific predicates or withhold B1.3/B1.19 assertions in cases where the readings differ.

**4. Kind 4 — significant. Where: §4 obligation 6 versus §6.6.**  
**What/why:** Obligation 6 says “Inside a snapshot directory, the layout is free,” but §6.6 requires each manifest path to exist at that path inside the snapshot and recognizes only a bare repository at the repo path or a bundle at `<repo path>.bundle`. A permitted `payload/...` layout or differently named bundle therefore scores `does-not-restore`. The interface prescribes a storage layout while claiming not to.  
**Fix:** Add manifest fields for stored file and bundle locations, or replace “layout is free” with one exact, acknowledged storage format.

**5. Kind 2 — blocking. Where: §§3.4, 4.3, 6.4 and 7, notice observation and matching.**  
**What/why:** The relay “carries bytes” and “imposes no protocol,” yet the harness channel must parse implementation notices; no wire framing is specified. `notice_reached` also leaves early arrivals, multiple matching references/notices, notice-`seq` matching, and `match` semantics undefined, so an unrelated notice can potentially satisfy an assertion. Finally, a `deadline.started` reference is emitted “when [the checker] starts measuring a deadline,” not when the harness establishes that the contract’s starting event occurred. This lets the implementation determine the scoring clock and makes a missing observation produce `unreached` rather than a missed-deadline failure.  
**Fix:** Specify notice framing and exact reference/match semantics, and derive deadline starts from defined raw contract events wherever possible rather than from an implementation-selected `deadline.started`.

**6. Kind 4 — significant. Where: §4 obligation 10.**  
**What/why:** Every notice must contain “at least `clause`, `cause` and `seq`.” The contract does not require all three for every notice. In particular, a B1.19 violation with no usable snapshot and a whole-record disagreement need have no meaningful sequence number, and not every notice has a contract-required cause. A correct implementation would have to invent dummy values.  
**Fix:** Make `seq` and `cause` optional/nullable except where the applicable clause requires them, while retaining the mandatory clause identity.

**7. Kind 5 — blocking. Where: §7 deadline comparisons, with §6.4.**  
**What/why:** “Deadline comparisons … use the referenced observation’s `host_time` plus `within`, against the notice’s `arrival_host_time`.” The latter is explicitly read on S’s clock, while the reference may be on R or RESTORE. After a clock step these timestamps are not a common time base. For example, a +24 h step on S can make an immediately delivered notice appear 24 h late. No tolerance or alternative reading is scored, despite the contract allowing clock-step error and questions 3/9 leaving the governing reading open.  
**Fix:** Record per-host clock readings at every reference and arrival, and score all permitted clock readings with the applicable step tolerance—or censor cross-clock deadline assertions until the contract is resolved.

**8. Kind 6 — blocking. Where: §1.5 and §7, expectation and scoring semantics.**  
**What/why:** The interface says “An assertion built with `any` over the readings is the way” to accept multiple readings, but never defines `all`/`any`/`not` when a branch is `unreached`, `censored`, or `unsupported`. Nor does it define the empty-object languages for `selector` and `match`, multiple-match selection, or precisely when a deadline is censored rather than failed. Two harnesses can therefore assign different verdicts to the same reading-parametric assertion.  
**Fix:** Define a complete multi-valued scoring algebra and normative selector/match, reference-selection, and censoring rules.

**9. Kind 6 — blocking. Where: §1.4 and §1.6, `unreached` and horizon anchoring.**  
**What/why:** If a required `run.finished` never occurs because the implementation is defective, the dependent injection times out and dependent assertions are “scored `unreached`, never `pass` or `fail`.” Thus non-performance can remove the test instead of failing it. If the last scheduled injected event is unreached, its “virtual time at which [it] actually ran” does not exist, so the horizon is also undefined.  
**Fix:** Distinguish invalid schedule preconditions from missing contract-required behaviour, give unreached injections a defined horizon anchor, and score independent state assertions normally.

**10. Kind 6 — blocking. Where: §1.5, §1.6, §6.6 and §9.7, assertion times and horizon.**  
**What/why:** Assertions may be evaluated at an event or timestamp, but §9.7 says to “evaluate assertions” after advancing to the horizon, without requiring snapshots of the record, manifests, marks, or snapshot presence at earlier assertion times. Later pruning or record updates make earlier states unrecoverable. It is also undefined whether `at: "<event>"` means before or after that event, and how a non-horizon `restores` assertion obtains its result. Separately, post-injection events can run later than `last injection + scoring_horizon`; §9.7 would then require advancing backwards to the horizon.  
**Fix:** Evaluate and snapshot all assertion state at defined assertion points, and reject or otherwise define schedules whose events extend beyond the computed horizon.

**11. Kind 5 — blocking. Where: §2.3 and §9.4, virtual-time execution.**  
**What/why:** The harness advances virtual time in one-minute steps while waiting for observations, but no real-time scheduling or quiescence rule prevents a slow correct process from being overtaken by virtual time. Roles are not required to be frozen while horizon state is read. “Host-clock deadline order” also does not define a global order after host clocks diverge, and “timers are recomputed” does not define backward-step, already-fired, or simultaneous-timer behaviour. These choices can change runs, marks, and verdicts.  
**Fix:** Specify a deterministic scheduler with explicit process-yield/quiescence and horizon-freeze rules, plus total timer and clock-step ordering rules.

**12. Kind 5 — blocking. Where: §1.3 and §1.4, world and source actions.**  
**What/why:** “Deterministically from `seed`” does not specify generated file names, contents, sizes, or encodings; the example later assumes `f0001`. Generated git histories have no canonical object IDs, timestamps, or content, so schedules cannot portably name objects. “Every virtual tick” is undefined, and operations such as `truncate_tree`, `git.commit`, and continuous rewriting lack sufficient semantics for a harness or TLA+ runner to reproduce them.  
**Fix:** Publish a canonical world-generation algorithm and byte-exact, deterministic semantics for every source operation and continuous-action tick.

**13. Kind 1 — blocking. Where: §5 BF1.1 and BF1.5.**  
**What/why:** A crash “often with `when` (e.g. `prune.started`)” and a BF1.5 change “usually with `when: run.inventory_read`” are not guaranteed to occur during the target operation. Observation emission does not block the implementation; a fast run or prune may finish before the harness acts. Likewise, the continuous rewrite specification does not guarantee that a file changes between two capture attempts, so a schedule cannot fairly assume the worked case’s mandatory *capture* failure.  
**Fix:** Add synchronous observation gates for injection points, or define injections only at guaranteed harness-controlled state transitions and avoid assertions whose premise was not established.

**14. Kind 1 — blocking. Where: §5 BF1.4.**  
**What/why:** “`RLIMIT_FSIZE=0` … on that host’s processes, and its writable sandbox directories made read-only” is not a portable way to change limits on existing processes. Read-only directories alone do not stop writes to already-existing writable files, and “relaunch with the same environment” in BF1.1 does not ensure that a process restarted during the fault remains limited. Consequently the harness cannot guarantee the specified full-disk condition.  
**Fix:** Use a specified harness-controlled write-fault layer, or narrowly define and verify a platform-specific live-process mechanism, treating inability to establish write failure as an injection error.

**15. Kind 1 — significant. Where: §5 BF1.7 and BF1.8.**  
**What/why:** BF1.7 says the relay “refuses connections” but also “Nothing reaches the channel’s record”; refusing new connections does not stop notices on an existing persistent connection. BF1.8 drops a `(host, kind)` wakeup, but the interface never requires a run timer to use `kind: "run"` rather than `"other"`, so a hold-out injection can be a no-op on a correct implementation. No-op injection reporting is not defined.  
**Fix:** Drop all channel traffic including existing flows, add an implementation-independent timer selection such as `kind: "any"`, and count coverage only after an actual channel block or timer drop.

**16. Kind 3 — significant. Where: §5 BF1.10.**  
**What/why:** “R’s record copy is untouched” fixes contract question 7 to the record-survives reading for BF1.10 alone. The alternative is available only by adding BF1.13 “in the same instant,” but separate schedule events are not atomic with respect to role activity. The mechanism also models deletion rather than reimage/replacement, with no R restart or other host-state reset.  
**Fix:** Keep BF1.10 record-dependent assertions unscored or expose record-surviving and record-lost environment variants explicitly, with an atomic composite injection.

**17. Kind 1 — significant. Where: §5 BF1.3/BF1.12 and §6.5 `present`.**  
**What/why:** BF1.3 can corrupt only files below snapshot directories: it cannot corrupt a manifest, cannot inject into a fileless snapshot, and has no defined missing-path, bad-offset, or largest-file tie behaviour. BF1.12 always deletes both snapshot directory and manifest, while `present` requires both. These are useful particular variants, but they do not cover the scopes left open by contract questions 16 and 17, and a no-op must not be reported as successful injection.  
**Fix:** Define validated, total payload-only variants and separately named manifest/record variants, without claiming coverage of unresolved cell scopes.

**18. Kind 3 — significant. Where: §6.2 status-record schema.**  
**What/why:** A run entry’s writer is fixed to `"S"`, and mark writers are limited to `"checker" | "restore" | "R"`. Contract questions 1 and 2 leave open whether the checker can write the crash-derived *failed/unknown* run entry and whether a run can write a *missing* mark. A correct implementation following those readings cannot faithfully represent its entries in this format.  
**Fix:** Make writer an open observational value and allow assertions to accept the permitted writer/copy alternatives without selecting one.

**19. Kind 3 — significant. Where: §3.2 and §3.4, channel dependence.**  
**What/why:** The channel is made unreachable only when S is “suspended or crashed,” while an S–R partition drops only traffic between S and R. R–CHANNEL traffic therefore remains available, effectively answering contract question 15 in favour of delivery during that partition. Also, although the binding says the channel record is on S, an S disk-full injection does not affect the harness-owned channel record.  
**Fix:** Model channel reachability as an explicit dependency/variant and withhold partition-delivery assertions until the contract reading is settled.

**20. Kind 2 — blocking for contract-wide W1 schedules. Where: §§4–7, missing observations and assertions.**  
**What/why:** The observation and expectation lists cannot score several clauses, even indirectly at their actual deadlines:

| Clause | Missing capability |
|---|---|
| B1.1 | No initial-verification result or way to assert that verification and completeness preceded *ok*. |
| B1.5 | No assertion that credential files are absent at R/RESTORE; portable new-commit scan input is also undefined. |
| B1.8, B1.12 | No generic observation-by-deadline expectation. A final mark proves only completion by the horizon, and a successful re-verification need leave no mark. |
| B1.9 | No interval-start semantics or *ok*-with-sequence-greater-than predicate. |
| B1.11 | No daily-check outcome or decision-log observation. |
| B1.13 | `check.run` is only accepted, with no checker-pass completion observation or defined protected-set source. |
| B1.15 | No comparison observation containing counts/bytes/baseline and no portable logged-reason injection. |
| B1.16 | No defined channel-recovery reference for the redelivery deadline; held notices are not observable. |
| B1.18/B1.4 | No kept-aside, consistent-disagreement, rebuild-start/finish, or rebuild-complete observation, so *Rb*, evidence retention, and the pruning pause cannot generally be judged. |

For example, the contract requires checks “within *M*” and re-verification “within *P*,” but the only timed expectation is `notice_reached`.  
**Fix:** Add raw clause-specific observations and a generic timed-observation expectation, and explicitly mark contract-dependent remnants unsupported rather than implying coverage.

**21. Kind 5 — significant. Where: §6.2 record hashing.**  
**What/why:** “Canonical JSON … sorted keys, no whitespace” is not a complete canonicalization, especially because arbitrary ignored extra fields are permitted. Number representation, Unicode escaping, and nested ordering can differ between an implementation and harness, causing a valid copy to be treated as hash-lost.  
**Fix:** Specify a standard canonicalization such as RFC 8785/JCS and restrict or canonicalize all permitted extra fields.

**22. Kind 6 — significant. Where: §1.7 example.**  
**What/why:** The example is not a reliable template. First, `a2` requires notice within `1h` of a B1.8 `deadline.started`; if that observation starts *M* at *ok*, B1.7 instead allows *M + D* = 25 h, while if it starts *D* when *M* passes, §4.3 must say so. Second, the world omits the binding’s `tupay-homes/` source without defining omitted sources as empty. Third, `tupay-private/f0001` is not guaranteed by §1.3. Finally, corruption and suspension race with the implementation’s restore check, so `a1`’s outcome is not fixed.  
**Fix:** Rewrite the example using a complete canonical world, defined injection gates, and an unambiguous deadline reference.

**23. Kind 6 — minor. Where: §6.1, §6.3, §6.7 and §8.**  
**What/why:** Several formats conflict or are incomplete: a `gone` file still appears to require a `sha256`; harness-only observations have no defined `host`/`host_time` although event references may need them; `clock.set` must produce a `signedDuration` `delta` even for an arbitrary timestamp difference; and §8’s alternate `unsupported` result contains no per-assertion scores although §7 says dependent assertions are scored `unsupported`.  
**Fix:** Publish one normative schedule, observation, manifest, clock-log, and results schema covering all variants.

**24. Kind 2 — minor. Where: §1.5 `next_seq_at_least`.**  
**What/why:** Worked case 4 requires exactly 43, but “at least `value`” also accepts 44, although the numbering rule computes `max(...) + 1`. It is also undefined how the predicate scores if no next run occurs before the horizon.  
**Fix:** Use an exact expected-next-number predicate computed from surviving records/snapshot names, with defined no-next-run scoring.

---

## Disposition of the first drafter’s questions

“Open/weak” means the interface does not expressly choose a reading, but W1 can write only a conservative partial check or must leave the point unscored.

| Question | Interface disposition |
|---|---|
| **A1. Where held notices are read** | **Open on location.** No spool host or path is prescribed, which is appropriate; only delivery is observable. A full redelivery-deadline assertion is not yet portable (F5, F20). |
| **A2. B1.19 violation trigger** | **Not reading-neutral in practice.** Scoring can use a checker-announced `deadline.started`, but has no reliable state-crossing reference or working `any` semantics for both readings (F5, F8). |
| **A3. Start/clock of B1.8’s *M*** | **Open but unscored.** There is no direct *M* predicate; §7’s mixed-clock arithmetic is not a valid resolution (F7, F20). |
| **A4. Meaning of intact-copy disagreement** | **Open and untestable.** No disagreement definition or consistent-rewrite injection is supplied (F20). |
| **A5. Clock defining UTC day/month** | **Open.** No daily/month predicate chooses a host; no-step schedules can avoid the issue, BF1.6 retention schedules cannot be generally scored (F20). |
| **A6. Quantity to which *Q* applies** | **Open.** A total shrink can avoid the count-versus-bytes ambiguity, but the actual comparison deadline and logged-reason condition remain unobservable (F20). |
| **A7. Whether BF1.10 preserves R’s record** | **Forced for BF1.10 alone:** the record survives. The other environment is representable only as a non-atomic combination with BF1.13 (F16). |
| **A8. B1.9 interval start** | **Open.** The interface supplies no interval construct or higher-numbered-*ok* predicate; a schedule choosing a start does not thereby resolve the contract (F20). |

## Disposition of the second drafter’s questions

| Question | Interface disposition |
|---|---|
| **B1. Who records a run without a final entry** | **Forced/unsupported alternative:** the record format admits only writer S, so a checker-written entry cannot be represented faithfully (F18). |
| **B2. Whether a run may write marks** | **Not both readings supported:** the closed mark-writer set has no run/S writer (F18). |
| **B3. Which copy supplies B1.13’s protected set** | **Open but unscored.** Either copy can be read by `record_entry`, but no protected-set or missing-mark provenance rule exists (F2, F20). |
| **B4. Protection during a both-copies-lost rebuild** | **Not fully reading-neutral.** Rebuild protection is unobservable, and R-record loss forcibly makes `marks_restorable` false (F2, F20). |
| **B5. Where a corrupt copy is kept aside** | **Open and unobservable.** The interface rightly prescribes no path, but also supplies no set-aside observation (F20). |
| **B6. Notice for a record disagreement** | **Open fields, unscored trigger.** Clause/cause can be left broad, but there is no defined disagreement event from which to measure *D* (F5, F20). |
| **B7. Starting event for B1.19’s notice** | Same as **A2**: no reliable assertion accepting both state-crossing and first-observation readings (F5, F8). |
| **B8. When B1.19 becomes active** | **No activation rule.** A conservative schedule can wait until after *G* from the first run and avoid the disputed early window; earlier assertions are not portable (F2). |
| **B9. Clock for cross-host deadlines** | **Not reading-neutral:** the scoring rule mixes host clocks rather than accepting the permitted alternatives (F7). |
| **B10. Clock for “younger than *G*”** | **Undefined:** `recoverable_exists` names no evaluation clock (F2). |
| **B11. Quantity governed by *Q*** | Same as **A6**: no formula is forced, but the full clause is not observable (F20). |
| **B12. Logged-reason format** | **Open.** No format is imposed; the no-reason case can be attempted, but a portable reason-suppression case cannot (F20). |
| **B13. Recording a failed daily check** | **Open and unobservable:** there is no daily-check result or decision-log record (F20). |
| **B14. Location of undelivered notices** | **Open on location**, but the channel-return event and its clock are not reliably referenceable for redelivery scoring (F5, F20). |
| **B15. Channel access during S–R partition** | **Forced reachable:** R–CHANNEL remains up under the relay rules (F19). |
| **B16. Scope of BF1.3** | **Restricted injection, not full scope:** snapshot payload files only. That is a useful minimal variant where files exist, but other scopes and fileless snapshots cannot be injected (F17). |
| **B17. Whether BF1.12 includes manifests** | **Forced in the injection/observation:** both payload and manifest are deleted, and `present` requires both (F17). |
| **B18. Degree of BF1.4** | **One variant only:** total write failure. This need not force an implementation’s contract reading, but partial fullness cannot be scheduled (F14). |
| **B19. Where BF1.6’s error is reported** | **No service location is forced.** The interface instead forbids requiring a service report and keeps only a harness log; that part of BF1.6 is therefore untested. |
| **B20. Pruning host and retention clock** | **Pruning host is properly left free.** The clock/day question remains open and under-step retention is not generally scoreable (F20). |
| **B21. Observability of rebuild** | **Open and unobservable:** no rebuild state is recorded (F20). |
| **B22. B1.9’s quantified interval** | Same as **A8**: open, with no adequate liveness predicate (F20). |
| **B23. Meaning of “since”** | **Forced to record append order** (F3). |
| **B24. Meaning of git “new commits”** | **Open.** `git.commit` and scan-material semantics are insufficient for a portable new-commit credential test (F12, F20). |
| **B25. Who deletes a path that becomes `gone`** | **No deleter is chosen**, but `manifest_complete` accepts `gone` without evidence of deletion, so it is too weak rather than safely comprehensive (F1). |
| **B26. Whether staleness notice lapses** | **Open.** No staleness state machine is defined; avoiding a newer acknowledgement permits a conservative test (F5). |
| **B27. Whether initial verification starts *P*** | **Open and unscored:** the first *P* deadline cannot be computed or asserted under both readings (F20). |
| **B28. Whether B1.19’s cause list is exhaustive** | **Reading-neutral on vocabulary:** `cause` is a free string and the expectation may omit a match. The interface cannot robustly verify that a cause actually names something, and the notice trigger remains blocked (F5, F6). |

The safe course for the unresolved questions is raw observation plus explicit `unsupported`/censored coverage, not new normative predicates or fault effects that silently select an answer.