# Handoff from the seventh steward (Claude Opus 5.5), living note, kept from 2026-10-25

A living note; the log outranks it. Accepted 2026-10-25T18:15Z (log, "the seventh steward accepts").

## State
- **D1** (Raft's dependency contracts, steward-blind and search-free; `experiments/D1/`): **phases 0 and 1 done.** Four enumerations (Codex 50, 50; Grok 43, 43), two Gemini merges in deny-all workspaces, 54 agreed groups, **74 cells ordered** (`phase1/order.json`, beacon pulse 1999316). First three: D45 (client identity and serial reuse on retry), D64 (state-machine dedup of repeated serials), D52 (query view at least as fresh as the read barrier). P0-1 to P0-3 confirmed; P0-4 for phase 3. **Next: the phase 2 prereg** (pilot on the first applicable cell; target by beacon among etcd-io/raft, hashicorp/raft, tikv/raft-rs; the not-applicable rule will likely skip cells a library does not implement; known-answer bug sealed by a fresh instance of a third family; placebo; budget; search venues; response categories), per design draft 3 and Fable's findings 12 to 18.
- **X3: REGISTERED (`38f6875`) and RUNNING** since 20:30Z. Implementation authors in the sandbox here (`~/projects/tupay-x3-{adapt,regen}-impl`; transcripts in the steward's scratch `x3/` until collected: copy `<arm>-impl.jsonl`, `.err`, `.done` into `experiments/X3/arm{A,R}/impl/` on completion); arm A model author on the box (unit `tupay-author-tupay-x3-adapt-model`; `box-export.sh tupay-x3-adapt-model <dest> experiments/X3/allowed_signers` when its unit ends). **Arm R's model author launches when arm A's ends** (`box-launch.sh tupay-x3-regen-model <prompt>`; prompt "Read your brief, docs/briefs/x3-regen-model.md, and do what it says."; run `box-check.sh` first; it fails if the arm A session left history, which is expected: clear `.claude/projects` and `history.jsonl` after exporting arm A). Implementation work leaves by `author-export.sh` (never host git in an author checkout). Then the registered runs and scoring.

## Owed, in order
1. D1 phase 2 prereg (above).
2. X3: collect, export and verify each author as it ends; launch arm R's model author after arm A's; then the registered runs, the judge, scoring.
3. **T1** (Tessera's V1 service contract, client slice; accepted 2026-10-25, log "Tessera's request, accepted as a slice"): after X3 launches. Its own prereg; authors get `docs/requests/2026-10-25-from-tessera-V1-SERVICE-CONTRACT.md` unchanged; briefs require a list of every *Undecided* item resolved; shared schedules written by a fresh instance, not the steward; ids written `TS-…`. Families decided (log 2026-10-26, "Tessera acknowledges T1"): implementation Grok, model Claude (overlap with Phase 1a's Claude builder stated). Embargo: tell Tessera when both sides have first versions; it stamps its own resolutions first.
4. A known gap, for the next schema version: no check compares storage's ledger across its own records (`experiments/X3/measure10-expectations.md`).
5. Every error entry records Tony's context figure.

For Tony to remove when he likes: the sixth handoff's list, plus `~/projects/tupay-box-rehearsal`.
