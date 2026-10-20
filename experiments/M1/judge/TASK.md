# Judge task: three divergences from tupay M1's first paired run

You are the judge. You were chosen because you belong to a model family that wrote neither side. Work only from the files in this directory. Do not assume either side is at fault.

Background: two inputs (`inputs/contract-v1.md`, `inputs/failure-model-v1.md`) and a shared schedule format (`inputs/schedule-format.md`) were given to two independent authors. One wrote a TLA+ model (its README and the relevant excerpt are in `model/`), the other a Go implementation on HashiCorp Raft (its README in `impl/`). Each author also wrote its own schedule files for the twelve pairs in `inputs/pairs-v1.md`. The steward then ran each side on the OTHER author's schedules. Results: `traces/model-on-impl-schedules-results.txt` and `traces/impl-on-model-schedules-results.txt`.

Three divergences need verdicts.

**D1. P10.** On the implementation author's P10 schedule (`impl/schedule-P10.yaml`: crash n1 at start, then c1 requests), the model reports FAIL C1_4 (liveness) while the implementation reports PASS on three seeds. Evidence: `traces/model-on-impl-P10-tlc-counterexample.txt` (TLC's lasso), `traces/model-on-impl-P10-counterexample.jsonl`, `traces/impl-own-P10-seed1.jsonl`, and `model/Lease-grantor-excerpt.tla` (the model's Elect, StepDown and Grant actions).

**D2. P2 and P3.** On the implementation author's P2 and P3 schedules, the model reports UNEXPLAINED "end of schedule unreachable", while the implementation passes. Compare the two READMEs' interpretations of trigger semantics (model interpretation 8; implementation interpretation 10) against `inputs/schedule-format.md`, and the `end:` lines of `impl/schedule-P2.yaml` and `impl/schedule-P3.yaml`.

**D3. Aliases.** On the model author's P1, P3, P6, P10 and P12 schedules, the implementation's compiler rejects the schedule as invalid (UNEXPLAINED), because those schedules use `grantor` or `holder` as the target of crash, restart, pause or resume (model interpretation 10; implementation interpretation 14), while `inputs/schedule-format.md` shows the aliases only in a partition example.

For each divergence answer, in the JSON schema given: `verdict` is "explained" or "unexplained". If explained, `locus` is one of "model", "implementation", "inputs" (the contract or failure model underdetermine the behaviour), "interface" (the schedule format or observe schema underdetermine it), or "both". `evidence` names the specific file lines or trace states that discriminate. `what_would_settle_it` says what further evidence would be needed if your verdict is unexplained, or what would overturn it if explained. Be concrete and brief. Do not propose fixes.
