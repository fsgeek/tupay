# M1 result (steward, 2026-10-20)

M1's criteria, from `docs/plan-m1.md`: every artifact present and tagged; the twelve pairs run on both sides; every mutation pair fails; the false-suspicion run observed with provenance. **All four are met.** What M1 also found is that the pairs were not pairs, and that the first real paired comparison produced divergences on both sides. Those are the result.

## What was built, by whom, in how long
| Side | Author | Wall-clock | Tokens (author's count) | Tool calls | Sessions |
|---|---|---|---|---|---|
| `model/` TLA+ | Claude Opus 5.5, fresh instance | 24 min (21:31Z to 21:55Z) | 164k | 36 | 1 |
| `impl/` Go on HashiCorp Raft | Codex CLI 0.163.0 (gpt-6.1 family) | 31 min (21:31Z to 22:02Z), of which ~21 min blocked by the steward's sandbox | 234k | not reported | 3 (two resumes) |
| inputs, interfaces, briefs, prereg | steward (Claude Fable 5.1) | 20:06Z to 21:31Z, interleaved with plaza work | not measured at the task level | | |

Both authors committed their own predictions before building anything, unprompted by the brief: the model author at `22628ab` (schedules and `PREDICTIONS.md`), the implementation author at `37283d5` (`impl/PREREGISTRATION.md`, a predicted outcome per pair and mutation). Both read AGENTS.md rule 3 as binding their own test runs. Both READMEs state 21 and 28 interpretations respectively. Derivation tags: 33 of 33 files on the model side, 27 of 27 on the implementation side.

Neither author saw the other's directory. Both could physically read `docs/`; both state they did not.

## Steward's runs (the first runs after the merge at `86ad268`; no fix on either side before or since)
**Each side on its own schedules.** Model: 13 of 13 PASS, 12 of 12 mutations FAIL on the predicted invariant, 83 s. Implementation: 36 of 36 pair runs PASS (three seeds), 36 of 36 mutation runs FAIL on the predicted clause, 2 min. Both reproduce the authors' claims. Logs in `experiments/M1/own-run/`.

**The pairs were not pairs.** The seed says one fault schedule compiles to both sides. The steward left `testbed/schedules/` empty, so each author wrote its own thirteen schedules from `tests/pairs-v1.md`. Compared semantically, none of the thirteen is the same on both sides. "P5 passes" meant two different P5s. This is a steward defect in the workflow's setup, found by the workflow.

**Cross-run: each side on the other's schedules** (`experiments/M1/cross-run/`).
| Schedule | Model on impl's schedule | Impl on model's schedule |
|---|---|---|
| P1 | PASS | UNEXPLAINED (compiler rejects `crash: grantor`) |
| P2 | UNEXPLAINED end of schedule unreachable | PASS |
| P3 | UNEXPLAINED end of schedule unreachable | UNEXPLAINED (rejects `pause: holder`) |
| P4, P5, P7, P8, P9, P11 | PASS | PASS |
| P6 | PASS | UNEXPLAINED (rejects `pause: holder`) |
| P10 | **FAIL C1_4** | UNEXPLAINED (rejects `crash: grantor`) |
| P12 | PASS | UNEXPLAINED (rejects `pause: holder`) |
| false-suspicion-v1 | PASS | PASS |
| model mutations on impl's schedules | 11 of 12 FAIL as predicted; **P11's mutation survives** | |

Three divergences were sent to the judge (Gemini 4 Argon via `agy`, as Amendment A fixed): D1, P10; D2, P2 and P3; D3, the alias rejections. The steward's reading of the evidence was not given to the judge. Verdicts are in the section below.

**Provenance.** `observe/provenance_check.py` (steward's, independent of both sides) traces every `WriteAccept` and `WriteReject` in every observe file on both sides, 25 model files and 126 implementation files, to a `Grant` with the same token and grantor term. No decision is untraceable.

**False-suspicion run, observed, not judged.** Both sides show the same shape: the superseded holder's write is accepted while the new token has not yet reached storage, and rejected once it has. Both trace each decision to its grant and term. Fencing as specified allows a superseded holder to keep writing until a newer token reaches storage; neither side treats that as a violation, and the contract does not make it one.

## Predictions scored (against these first runs only)
- **P-a** (different interpretations of at least one input): **confirmed.** C1.4's "long enough" is "eventually forever under weak fairness" on the model side and a three-second horizon with a trusted duration certificate on the implementation side. Restart differs in what a lease node keeps. Grant spacing differs: the model never waits for expiry, the implementation waits a full lifetime. Both read `token: stale` the same way, which the prediction named as a likely difference.
- **P-b** (1 to 3 pairs disagree at first paired run, in P10 to P12 or P5/P6): **confirmed in count and partly in location.** On own schedules, zero disagreements. On the cross-run, three substantive disagreements (P2, P3, P10) and five interface rejections. P10 was predicted; P2 and P3 were not.
- **P-c** (every mutation fails on its own side first time): **confirmed**, 24 of 24. Addendum: on the other side's P11 schedule, the model's P11 mutation survives, so mutation adequacy is relative to the schedule, not to the pair.
- **P-d** (false-suspicion shape): **confirmed** on both sides, including the second clause (acceptance before the new token reaches storage).
- **P-e** (the observability layer fails its own test on at least one side): **falsified.** Every decision on both sides is traceable.

## Cost baseline for the change experiments
- Author wall-clock and tokens: the table above.
- Decisions asked of Tony during M1: 1 (how to reach Hamut'ay; Tony arranged plaza access). Interruptions that blocked work: 0. Tony volunteered two things unasked: Gemini's availability through `agy`, and the plaza access itself.
- Steward cost not in the table: two Codex resumes caused by the steward's sandbox choice (about 21 minutes and roughly 100k of the implementation's 234k tokens), and the cross-run, which took about 5 minutes of machine time.
- Divergence count at first paired run: 3 substantive, 5 interface. Stale-tag residue: 0 (nothing retired).

## Judge's verdicts
Judge: Gemini 4 Argon (high) through `agy`, 2026-10-20 22:11Z to 22:14Z. Packet, prompt, schema and raw output in `experiments/M1/judge/`. The first attempt returned nothing: headless mode denied the judge's file reads. The second attempt inlined the whole packet (66 KB) in the prompt, so the judge used no tools. It emitted two JSON objects; they agree on every verdict and locus, and the complete one is used.

- **D1 (P10): explained, locus model.** The judge's mechanism, from the TLC lasso: n3 is elected leader of term 1 by the non-maximal majority {n1, n3}; n1 then crashes; n2 still has promise 0. `Grant` needs a majority already promised to term 1, which no longer exists; `Elect(n2)` is disabled because n2 can see a leader of a term at least its own promise; `StepDown(n3)` is disabled because nobody has promised higher. The model has no action by which a leader brings a lagging follower into its term, so it stutters forever with a majority, storage and the requester all up and connected. That violates C1.4 under a schedule the failure model admits.
  Steward's note on the packet: the implementation trace supplied to the judge was, by the steward's error, one of the author's pre-fix reference runs (two events, no Grant). The judge noticed and made its verdict conditional on post-fix traces emitting a Grant. The steward's own post-merge runs do: all three P10 seeds contain a Grant to c1. The condition is met. The steward had formed the same hypothesis before the judge ran, but did not record it first, so no priority is claimed.
- **D2 (P2, P3): explained, locus interface.** The schedule format does not say whether a step's trigger, and `end:`, match only events emitted after the previous step was applied (the model's reading) or stay satisfied once observed (the implementation's reading). The implementation's P2 and P3 use the same Grant as both the last step's trigger and the end trigger, which is unreachable under the model's reading.
- **D3 (P1, P3, P6, P10, P12): explained, locus interface.** The format defines `grantor` and `holder` in its general rules but shows them only in the partition example. The model author allowed them for crash, restart, pause and resume; the implementation author restricted them to partitions and rejects the rest.

Tally: one model defect, two interface defects, zero implementation defects from the cross-run. The implementation's own defect (P10 bootstrap) was found and fixed by its author before its first version, with an outcome-informed amendment on the record.

## What follows (steward decisions, 2026-10-20)
1. **Schedule format v2**, additive: a trigger-arming rule and an alias-scope rule, each settling one of D2 and D3 the way the judge said would settle it. Then a **shared schedule set** in `testbed/schedules/`, written by the steward, which replaces both authors' private sets. Both compilers must then be adapted to v2. That is the first adaptation in the project; it is small, uncontrolled, and logged with its cost, not run as an experiment.
2. **The model's D1 defect** goes back to the model author with the judge's verdict and the lasso, as a known-category failure (F1.1) that demands a new pair: crash of a non-leader quorum member before the first grant. The fix and the new pair are the author's; the steward does not touch `model/`.
3. M1 closes when both sides pass the shared schedules or every remaining divergence has a verdict. Until then M1 is complete on its stated criteria and open on its findings.

## What the steward concludes, and what it does not
- The workflow's weakest point in M1 was the steward's own interface work: the schedule set was not shared, and the schedule format left trigger arming and alias scope open. Both authors filled the gaps differently, and the cross-run is where it showed.
- No fix has been made to either side. Any fix follows the judge's verdict and is logged as such. The model side's P10 result is an observation that the model, under a schedule it did not write, reports a liveness violation; whether that is the model's fault, the inputs', or the interface's is the judge's call, not the steward's.
- The next change to the project is to the schedule format, not to the contract or the failure model. That is an interface change, and under the hereditary fence it invalidates both compilers' derivations from `testbed/schedule-format.md`. It happens before X1 and is logged, not pre-registered as an experiment.
