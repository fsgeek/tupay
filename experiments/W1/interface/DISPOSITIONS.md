# W1 amendment A2: dispositions of the two interface drafts

The fourteenth steward, 2026-11-23. Drafts: `glm/draft.md` (GLM, `z-ai/glm-5.3-prime`, second attempt; the first, `glm-attempt1-empty/`, spent its whole output on reasoning) and `mistral/draft.md` (Mistral, `mistralai/mistral-large-4-0`; the transport failed at its §11, and `mistral/continuation.md` holds that section, asked for alone). Both had the same packet (sha256 prefix `30ac673b52070110`): the prose author copy and binding v1.

**Rule (acceptance decision 3):** where the drafts agree, the interface takes it. Where they differ, the choice is named here, decided by the contract text where the text decides it, and otherwise by the stated reason. **The interface never resolves a contract question:** where the text permits several readings, the interface makes each observable, and W1's decision tree (step 2) already makes a schedule that accepts only one permitted reading a test defect.

## Agreed by both drafts (taken as is)
- A1. One global virtual time and a clock offset per host. A clock step (BF1.6) moves one host's offset only.
- A2. The implementation reads contract time only from the harness. This constraint is needed for compression and for BF1.6.
- A3. Every role is a directory on one machine, run unprivileged. The restore host is given no path to S's sources.
- A4. All traffic between roles goes through a harness relay, so BF1.2 needs no root.
- A5. Both copies of the status record and every manifest are plain JSON at known paths in a fixed exchange format, because observation and BF1.13 injection need them. This is the interface's largest constraint on implementations, and both drafts say so.
- A6. A notice reaches the channel when the channel's record holds it, with the clause it names and its arrival time, on global time and on the channel host's clock.
- A7. The channel depends on S, because the binding puts its record on S (EX1.6).
- A8. Assertions use a closed vocabulary, each carrying exactly one `derives:` tag.
- A9. Injections need no cooperation: SIGKILL for BF1.1, a byte flip at R for BF1.3, deletion for BF1.12, deletion or corruption of a record copy for BF1.13, and SIGSTOP/SIGCONT for BF1.14.
- A10. Models read the same schedule text, report what they cannot express item by item and machine-readably, and never skip anything silently.

## Differences, decided
| # | Point | GLM | Mistral | Decided | Why |
|---|---|---|---|---|---|
| D1 | Syntax | YAML | JSON with a strict schema | **JSON** | Validation against one schema is what makes "unchanged against every runner" checkable. Comments go in an `note` field. |
| D2 | Periodic actions and BF1.8 | Harness fires fixed subcommands (`run`, `check`, `restore-check`, `reverify`) at due times the implementation declares | Implementation registers its timers with a harness timer service; free ids | **Timer service, with a required `kind` from a closed set** (`run`, `check`, `restore-check`, `reverify`, `prune`, `notice-retry`, `other`); ids free | Mistral's leaves the process model and retry timers free. GLM's closed kinds are what lets a hold-out written without seeing any implementation name the timer BF1.8 drops. BF1.8 targets (host, kind). |
| D3 | A suspended host's clock (BF1.14) | Frozen | Keeps advancing | **Keeps advancing** | The contract's Deadlines paragraph: limits are "never suspended, paused or restarted, under any failure"; worked case 3 measures *M* across the suspension. |
| D4 | Evidence of recoverability | Harness's own restore check is the only evidence for B1.3 and B1.19 | Derived from the service's marks and the store listing | **Both, for different clauses.** B1.19 (and measure 5's *recoverable*) is evaluated from the marks and the listing (Mistral §6.5). B1.3 is tested by the harness's independent restore of every snapshot whose marks make it restorable (GLM §6.3): if the marks say restorable and the bytes do not restore, B1.3 fails. | B1.3 is a claim that marks imply restorability, and B1.19 is stated over the marks ("whose latest restore check passed"). Taking only one would test only one of the two clauses. |
| D5 | Injecting during a run | Stage read from the record's stage field, best effort | Implementation emits stage observations (`run.inventory_read`, …), and schedules wait on them with `when` | **Mistral's, with a timeout:** a `when` that never becomes true marks the event *unreached*, and every assertion depending on it is scored `unreached`, never pass or fail | A deterministic point inside a run needs a signal from inside the run. An implementation that never emits it cannot gain from that: the injection is reported unreached, per implementation. |
| D6 | BF1.4 disk full | Filler file and gate ENOSPC | `RLIMIT_FSIZE=0` plus read-only sandbox directories | **Mistral's** | Deterministic and root-free. The implementation-side rule "treat write errors on the sandbox as a full disk" goes with it. |
| D7 | BF1.10 and R's record | Deletes snapshots and R's record | Deletes snapshots and manifests, keeps R's record | **Snapshots and manifests only.** Losing R's record as well is BF1.10 plus BF1.13 (copy R), injected together. | The text ("all its snapshots are lost") names snapshots, and it is silent on the record (GLM's contract question 7). Composing the two cells makes both readings expressible without the interface choosing one. |
| D8 | BF1.6 "the error is reported" | The harness records each step | Silent | **The harness records each step** in `clock-steps.jsonl`, and **no assertion may require the service itself to report a step** | The text does not say who reports. Recording it in the harness costs nothing. Asserting that the service reports would pick one reading. |
| D9 | Channel transport | Files in an inbox directory | An address on the relay | **An address on the relay** | Notices then pass through the same relay as everything else, so BF1.2 and BF1.7 act on one mechanism. |
| D10 | Horizon anchor | After the last event | After the last injected event | **After the last injected event** | That is W1's registered rule (Measures, item 5). |
| D11 | Initial sources | `world` section | Absent | **GLM's `world`** | A schedule must state what S holds at time zero, or its source events mean different things to different runners. |
| D12 | Harness-initiated observation | `query` events | Absent | **GLM's `query`**, for an independent restore check at a chosen time (D4) | B1.3 sometimes needs testing before the horizon. |
| D13 | No side channels | Explicit (C6) | Implicit | **Explicit** | A test-validity rule both drafts rely on. |

## Contract questions (from both drafts): not resolved by the interface
GLM listed eight (`glm/draft.md`, CONTRACT QUESTIONS), and Mistral's are in `mistral/continuation.md`. None is answered here, and none is given to any author or to the hold-out author. That keeps the hold-out author's inputs as W1 registered them, plus this interface. They are kept for three uses:
1. **The outside check of the merged interface**, which is asked whether any of them makes a cell uninjectable or an assertion unscorable. If so, the interface makes every permitted reading observable.
2. **Judging:** W1's decision tree step 2 (supported reading) and step 3 (contract defect) receive the relevant question when a finding touches it.
3. **Contract v2**, as recorded ambiguities.
