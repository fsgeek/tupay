# Brief: implementation author, the timing repair (before X3)

Same access list as your X2 brief; `model/`, `experiments/` and the steward's docs are absent on purpose. Nothing in the inputs changed.

**The finding.** The steward ran your artifact on `main` ten times per seed (three seeds) for every shared schedule and every mutation: 2,010 runs. Seven of 201 (schedule, seed) cells gave different outcomes across repetitions of the same seed:
- P18 unmutated, seed 2: 7 PASS, 3 `UNEXPLAINED workload unavailable under T3`.
- P18's mutation, seed 2: 7 `FAIL C2.2`, 3 `UNEXPLAINED workload unavailable under T3`.
- P29's mutation, seeds 1 and 2: survives (PASS) once in ten each.
- P30's mutation, seeds 1, 2 and 3: survives 3, 4 and 2 times in ten.
Every other cell gave the same outcome ten times out of ten. With your F1.3 change of the fix round (`e77dc22`, the unexpired-renewal condition on a pause) reverted, P30's mutation survives once in thirty and P18 shows `UNEXPLAINED pause requires an unexpired holder` instead; so that change made one pair worse but did not create the instability. The common factor is an outcome that depends on wall-clock time: `time.Now()` in the pause readiness check, and wherever else real elapsed time decides what a run does. The raw results are summarised above; you will not be given the steward's files.

**What to achieve.** A seed fixes every choice your runner and scheduler make, and time is the scheduler's: no outcome depends on wall-clock time or real elapsed time, so the same schedule with the same seed gives the same outcome every time. Every unmutated shared schedule passes, and every mutation fails its clause, on every repetition. How is yours to choose; record the choice as an interpretation, with the clause and cell it derives from. If making time the scheduler's changes what an F1.3 pause or an F2.x link change means in your artifact, say so.

**Acceptance (the steward's rule, applied after you report):** `impl/run.sh --all --seeds 3` and `impl/run.sh --mutations --seeds 3`, each ten times; a cell whose ten outcomes differ is flaky and fails acceptance. Run that yourself before reporting.

**Order.** Predictions first, committed: for P18, P29 and P30 and their mutations, what you expect after the repair, and which interpretations you expect to change. Then the repair, then the ten-repetition run of everything, README additively, adapted-version commit. Report: commit hash, the ten-repetition results (counts per cell), interpretations (new, extended, contradicted), wall-clock time, and **declared limitations**: any shape of schedule you believe would still be nondeterministic, and why you left it.

If an unmutated schedule fails, that is a result: record it and keep the evidence; do not change the artifact to make it pass without naming the clause or cell the old behaviour misread. The steward may run your artifact on schedules you have not seen, under any name. Stay inside this brief: the fix round's out-of-brief F1.3 change is what made P30 worse.
