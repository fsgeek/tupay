# Handoff from the third steward (Claude Opus 5.5), kept from 2026-10-21

A living note, updated at every boundary, so that a crash of this steward's context leaves a recovery record (log entry "third steward accepts", decision 1). The log outranks it. If this steward's session ended without warning, the state below as of its last update is the state; anything after it is in the log or not done.

## State at handoff (2026-10-22 04:05Z, context ~47%)
**The replay is registered** (`b7e15b2`, stamped `9de4053`). Nothing is running. The boundary is deliberate: the third steward set "no outcome-bearing round starts late in a session" and "boundaries at the end of rounds", so the successor starts the authors and owns the whole round.

**Successor, first steps (all scripted):**
1. `R=b7e15b2; for a in D F; do for s in model impl; do scripts/steward/setup-replay-checkouts.sh $R $a $s; done; done`
2. For each checkout: `scripts/steward/inputcheck-replay.sh <dir> <D|F> <model|impl> 2fbfbc008751d88c745a73cde46709abd6b1796ab61841af7afd8d2298624728 fd0e4fa2f80ca02aecdca18db6205efb305f08f81839447dc847f1c1be6c5a1a 5ee222390d858bd5b4920959e57126a3e984628e45fed48898eb3adee6ad737e ed3987bb9a0fa51439283f2698690d975f4aa1c8e3e2bd9cc8f5c8458ebdcca2 b0f23600d7be585010897248b6cff69f5066cec88b54cfa3a2deee47cf6bc936 937dceb97d6c2876a26117f61ea43132aca03c775380b8d3ae353ac121cc254a` → must print OK.
3. Start together, each with the prompt "Read docs/briefs/replay-<A>-<side>.md and do exactly what it says.", as tracked background tasks: Grok models `grok -p "<prompt>" --cwd <dir> --always-approve --disable-web-search --output-format plain`; Codex implementations `codex exec --sandbox danger-full-access -C <dir> "<prompt>"` (keep the printed session id for resumes). Log the start time from the clock.
4. Then follow the registration's "Order of execution" from step 6. Keep every author's harness transcript: the isolation guard is a search of them for paths outside the checkout and for web access.

**Then:** the timing repair (`docs/briefs/fix-timing-impl.md`; acceptance by the ten-repetition rule), then X3 = tupay's amend-or-rebuild in two arms (log 2026-10-22).

**Withheld in `tmp/replay/` (not backed up; committed at reveal):** K1 v1–v4 (current v4), needs files, the K1 v2 check, `reference/` (README first; `/usr/bin/python3 run.py <scenario> SPEC|GATED …`, capped), `holdout/` H1–H4 and notes. The reference's runs under `reference/runs/` are large; do not commit those.

**Recipes:** push with `GIT_ASKPASS= git -c credential.helper='!gh auth git-credential' push origin main` while the shell's VS Code socket is dead; every exploration under `systemd-run --user --scope -q -p MemoryMax=24G -p MemorySwapMax=0`; scratch worktrees `sdiag/main` and `sdiag/revert` in the third steward's scratchpad are registered worktrees (`git worktree prune` after the scratchpad is gone).

**What I would most want a successor to remember:** every defect this tenure found in the inputs, and most of my own errors, were claims nobody had executed. Run the thing.

## Standing practice for this tenure
- Ask Tony for the framework's context-remaining figure at each round boundary and before any outcome-bearing round; treat about half as the handoff zone (Tony: quality degrades with context, not only at the edge).
- Theater check, from Tony's account of Mallku: if producing the evidence of progress is costing more than building the thing itself would, stop and say so. In tupay the thing is the fence service; the apparatus is the measures.
