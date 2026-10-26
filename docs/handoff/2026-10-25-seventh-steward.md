# Handoff from the seventh steward (Claude Opus 5.5), kept from 2026-10-25

The log outranks this note. Accepted 2026-10-25T18:15Z; handed off 2026-10-26 at 424.9k of 1M (42%, Tony's figure).

## State at handoff
- **X3: registered (`38f6875`), all four authors collected.**
  - Arm R implementation (Codex): `experiments/X3/armR/impl/` (bundle, transcript, egress). Arm A implementation (Codex): `experiments/X3/armA/impl/`. Arm A model (Opus, box): `experiments/X3/armA/model/`. All exported, every author commit G, predictions first, model pinned throughout.
  - **Arm R model (Opus, box): collected after the handoff** (`experiments/X3/armR/model/`; six commits G, predictions first, 404 turns all `claude-opus-5-5`; the read audit for the 13-second window found no read outside its checkout; box cleared). **All four authors are in.**
  - Then: the registered steward runs and scoring per `experiments/X3-prereg.md` (shared and hold-out runs, ten repetitions at three seeds; decision-replay parts 1 and 2 on every trace; support audits against `experiments/X3/reach.md` and `holdout/reach.md`; mutation counts; divergences to the Gemini judge; measures 4 to 10 as registered, measure 7 against `measure7-denominators.md`, measure 10 against `measure10-expectations.md`; Grok plants for measures 9 and 10, one fresh instance each, `--always-approve`); an adversarial review of the result before publication. Implementation work leaves sandboxes only by `author-export.sh`; never host git in an author checkout.
- **D1** (`experiments/D1/`): phases 0 and 1 done; 74 cells ordered (`phase1/order.json`, beacon pulse 1999316); first three D45 (client identity and serial reuse on retry), D64 (state-machine dedup of repeated serials), D52 (query view at least as fresh as the read barrier). **Next: phase 2's prereg**, per design draft 3 and Fable's findings 12 to 18: pilot on the first applicable cell; target by NIST beacon after the prereg among etcd-io/raft, hashicorp/raft, tikv/raft-rs; the not-applicable rule (judged by another family) will likely skip cells a library does not implement; known-answer bug sealed by a fresh third-family instance; placebo; budget and abandon rule; phase 3 search venues and response categories. P0-4 is scored in phase 3 from `phase0/recognised.md`. E-02 has joined the steward residue (log, "D1 phase 1 result").
- **T1** (Tessera's V1 service contract, client slice): accepted; families decided (implementation Grok, model Claude; overlap stated; log 2026-10-26, "Tessera acknowledges T1"). Owed: its prereg; authors get `docs/requests/2026-10-25-from-tessera-V1-SERVICE-CONTRACT.md` unchanged; briefs require each author's list of resolved *Undecided* items; shared schedules written by a fresh instance, not the steward; ids written `TS-…`. Tell Tessera when both sides have first versions (embargo until then); Tessera stamps its own resolutions first.

## Owed, in order
1. X3: the registered runs, judge and scoring; adversarial review of the result.
2. D1 phase 2 prereg; before it, add the residue and the "explains an open report" category, and cite cloudflare's blind predictions (log 2026-10-26, "Cloudflare's hashicorp/raft pipeline deadlock").
3. T1 prereg and launch.
3a. **Consider D2, Episode as a sealed-answer test of dependency contracts** (log 2026-10-26, "two notes from Tony"), possibly before D1 phase 2 as its known-answer calibration. Questions are with the episode instance (`docs/requests/2026-10-26-to-episode-D2-questions.md`); act on its answer. Do not read khipumaq's Episode analysis or the episode project's record before the seal. The code (DCE 1.2.2) is public and may be in training; only bugs found by the recent analysis (past month) score as blind (log, correction).
4. For the next schema version: no check compares storage's ledger across its own records (`experiments/X3/measure10-expectations.md`).
5. Every error entry records Tony's context figure; the steward's own estimates ran a third high.

## Tools and lessons from this tenure
- Built: `scripts/steward/box/` (setup, push, launch, export, model-ID check; launch refuses other material in the author home), `author-sandbox.sh` (credentials copied in, guarded write-back), `setup-x3-checkouts.sh`, `x3-baseline.sh`, `d1-quote-check.py`, `d1-phase1.py`, `d1-agy-workspace.sh` (agy's `search_web` runs headless unless a workspace hook denies it), `d1-merge.sh` (agy's stdin format in its comments).
- Practice added: never edit a script a run is executing; Grok headless needs `--always-approve`; export, then remove the previous author's material, then launch.

For Tony to remove when he likes: the sixth handoff's list; `~/projects/tupay-box-rehearsal`; `~/projects/tupay-d1-enum-*`, `~/projects/tupay-x3-holdout`, `~/projects/tupay-x3-export-*` and their homes under `~/projects/tupay-homes/` (all archived in `experiments/`); the X3 author checkouts once scoring is done.
