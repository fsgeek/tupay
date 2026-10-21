# Handoff from the third steward (Claude Opus 5.5), kept from 2026-10-21

A living note, updated at every boundary, so that a crash of this steward's context leaves a recovery record (log entry "third steward accepts", decision 1). The log outranks it. If this steward's session ended without warning, the state below as of its last update is the state; anything after it is in the log or not done.

## State at last update (2026-10-21 19:30Z)
- Replay inputs **frozen** 18:15Z (`experiments/replay/inputs-frozen.sha256`). K1 unchanged, `a44ab378…ce24`.
- Replay pre-registration: **draft 1** `experiments/replay-prereg.md` (`7f4590d`). Fable's review archived (`experiments/replay/prereg-review/fable-review-draft1.md`); every item accepted; decisions in the log entry "Fable's review of the replay pre-registration draft; decisions" (`1810a34`), including the new model-brief requirement (an invariant check over all behaviours within stated bounds). **ChatGPT's review is pending, via Tony.** Next: merge both into draft 2, write the four briefs as files (hash them in the registration), K1's sealed resource needs, the attribution rule; then a short second review; then the hold-out author; then register.
- Seed-dependence: diagnosed as **timing-dependent** (`experiments/sdiag/`, log "seed-dependence diagnostic, scored"); revert insufficient. Steward practice gained the ten-repetition rule. **Flake census of all pairs on `main`** was running at 19:24Z (scratchpad `sdiag/census.sh` → `census.txt`); score it against the FC-1 to FC-3 predictions in the log. Owed before X3: the implementation author repairs the wall-clock dependence (scheduler-driven time), acceptance = ten repetitions per seed, no flaky cell.
- Scratch worktrees `sdiag/main` and `sdiag/revert` are registered git worktrees; remove with `git worktree remove` when done.
- Open questions to Tony: the context figure (asked; Tony offered to say at half).

## Standing practice for this tenure
- Ask Tony for the framework's context-remaining figure at each round boundary and before any outcome-bearing round; treat about half as the handoff zone (Tony: quality degrades with context, not only at the edge).
- Theater check, from Tony's account of Mallku: if producing the evidence of progress is costing more than building the thing itself would, stop and say so. In tupay the thing is the fence service; the apparatus is the measures.
