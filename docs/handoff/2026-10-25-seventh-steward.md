# Handoff from the seventh steward (Claude Opus 5.5), living note, kept from 2026-10-25

A living note; the log outranks it. Accepted 2026-10-25T18:15Z (log, "the seventh steward accepts").

## State
- **D1** (Raft's dependency contracts, steward-blind and search-free): design draft 3 and brief v2 after Fable's review (`experiments/D1/`). Phase 0: Codex runs 1 and 2 collected (50 contracts each; quotations 98% and 100% verified). **Grok runs 1 and 2 wait on Tony's `grok login`**: the old sandbox bind killed his Grok OAuth login on 2026-10-23 (log, "the sandbox killed Tony's Grok login"); fixed. Fresh Grok checkouts are built (`~/projects/tupay-d1-enum-grok-{1,2}`, manifests match). Relaunch: `author-sandbox.sh ~/projects/tupay-d1-enum-grok-<r> grok --single "Read BRIEF.md in this checkout and do what it says." --output-format streaming-json`, then collect as the Codex half was (log, "the Codex half collected"), quote-check, and score P0-1 to P0-4.
- The steward has **not read** the enumerations' contents and should not need to: phase 1 is two Gemini merges and the registered order. **agy's `search_web` runs headless without permission** (log, "agy's web search runs headless"); before any merge, find a workspace-scoped deny (agy's permissions or a hook returning `deny`) and prove it with `experiments/D1/agy-probe/` probe 2.
- **X3**: measure 10 expectations, measure 7 denominators (46 / 85; at-risk 8 / 13) and measure 5 baseline (35/35 both sides) registered in the prereg; the box finished and rehearsed (`scripts/steward/box/`); the X3 checkout script (`setup-x3-checkouts.sh`) written and dry-run.

## Owed, in order
1. D1: Grok half of phase 0 (needs Tony's login), then phase 1 per design.
2. X3: Grok's blind hold-outs (needs Grok) and 1(c)'s count from them; fill each implementation author's Go and uv caches; `inputcheck.sh` with `HARNESS=codex`; `box-check.sh`; commit the registration; launch (implementation authors here in parallel, model authors in sequence on the box, arm A first: `setup-x3-checkouts.sh`, `box-push.sh`, `box-launch.sh`, `box-export.sh`).
3. **T1** (Tessera's V1 service contract, client slice; accepted 2026-10-25, log "Tessera's request, accepted as a slice"): after X3 launches. Its own prereg; authors get `docs/requests/2026-10-25-from-tessera-V1-SERVICE-CONTRACT.md` unchanged; briefs require a list of every *Undecided* item resolved; shared schedules written by a fresh instance, not the steward; ids written `TS-…`. Waiting on Tessera: which family builds its Phase 1a.
4. A known gap, for the next schema version: no check compares storage's ledger across its own records (`experiments/X3/measure10-expectations.md`).
5. Every error entry records Tony's context figure.

For Tony to remove when he likes: the sixth handoff's list, plus `~/projects/tupay-box-rehearsal`.
