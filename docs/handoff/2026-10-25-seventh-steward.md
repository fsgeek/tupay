# Handoff from the seventh steward (Claude Opus 5.5), living note, kept from 2026-10-25

A living note; the log outranks it. Accepted 2026-10-25T18:15Z (log, "the seventh steward accepts").

## State
- **D1** (Raft's dependency contracts, steward-blind and search-free; `experiments/D1/`): **phases 0 and 1 done.** Four enumerations (Codex 50, 50; Grok 43, 43), two Gemini merges in deny-all workspaces, 54 agreed groups, **74 cells ordered** (`phase1/order.json`, beacon pulse 1999316). First three: D45 (client identity and serial reuse on retry), D64 (state-machine dedup of repeated serials), D52 (query view at least as fresh as the read barrier). P0-1 to P0-3 confirmed; P0-4 for phase 3. **Next: the phase 2 prereg** (pilot on the first applicable cell; target by beacon among etcd-io/raft, hashicorp/raft, tikv/raft-rs; the not-applicable rule will likely skip cells a library does not implement; known-answer bug sealed by a fresh instance of a third family; placebo; budget; search venues; response categories), per design draft 3 and Fable's findings 12 to 18.
- **X3**: measure 10 expectations, measure 7 denominators (46 / 85; at-risk 8 / 13) and measure 5 baseline (35/35 both sides) registered in the prereg; the box finished and rehearsed (`scripts/steward/box/`); the X3 checkout script (`setup-x3-checkouts.sh`) written and dry-run.

## Owed, in order
1. D1 phase 2 prereg (above).
2. X3: Grok's blind hold-outs (needs Grok) and 1(c)'s count from them; fill each implementation author's Go and uv caches; `inputcheck.sh` with `HARNESS=codex`; `box-check.sh`; commit the registration; launch (implementation authors here in parallel, model authors in sequence on the box, arm A first: `setup-x3-checkouts.sh`, `box-push.sh`, `box-launch.sh`, `box-export.sh`).
3. **T1** (Tessera's V1 service contract, client slice; accepted 2026-10-25, log "Tessera's request, accepted as a slice"): after X3 launches. Its own prereg; authors get `docs/requests/2026-10-25-from-tessera-V1-SERVICE-CONTRACT.md` unchanged; briefs require a list of every *Undecided* item resolved; shared schedules written by a fresh instance, not the steward; ids written `TS-…`. Waiting on Tessera: which family builds its Phase 1a.
4. A known gap, for the next schema version: no check compares storage's ledger across its own records (`experiments/X3/measure10-expectations.md`).
5. Every error entry records Tony's context figure.

For Tony to remove when he likes: the sixth handoff's list, plus `~/projects/tupay-box-rehearsal`.
