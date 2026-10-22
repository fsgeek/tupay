# Handoff from the third steward (Claude Opus 5.5), kept from 2026-10-21

A living note, updated at every boundary, so that a crash of this steward's context leaves a recovery record (log entry "third steward accepts", decision 1). The log outranks it. If this steward's session ended without warning, the state below as of its last update is the state; anything after it is in the log or not done.

## State at last update (2026-10-22 02:30Z)
- **Replay inputs frozen again** 02:23Z after the validation gate passed (log "K1 v4 confirmed under J1.5; replay inputs frozen again"). Contract v3 (J1.5; J1.2 and J1.4 retired). Hashes: `experiments/replay/inputs-frozen.sha256`; briefs: `experiments/replay/briefs.sha256`.
- Withheld in `tmp/replay/`: K1 v1 to v4 (current **v4**, `2fbfbc00…4728`), needs files (current `K1v4-needs.txt`, `fd0e4fa2…5a1a`), the K1 v2 check report, the reference (`reference/`: README first; run with `/usr/bin/python3 run.py <scenario> SPEC|GATED …`, always under its built-in 24 GB cap). All committed at reveal. **`tmp/` is not backed up**: losing it means rewriting K1 and rerunning the gate.
- Pre-registration **draft 3** `experiments/replay-prereg.md` (`094d3e4`). Remaining before registration, in order: (1) one fresh reading of draft 3 against its change list (Fable, no steward context); (2) hold-out author (a Fable instance not used for the K1 check), hashes to `experiments/replay/holdout/SHA256SUMS`; (3) write the attribution script (rule in draft 3, "Attribution") and the Grok classification/R4 instructions, commit with the registration; (4) register; (5) history-free checkouts + `inputcheck-replay.sh`; (6) start Grok ×2 (models), Codex ×2 (impls).
- Owed before X3: timing repair (`docs/briefs/fix-timing-impl.md`), held until the replay authors are under way.
- Scratch worktrees `sdiag/main` and `sdiag/revert` are registered git worktrees in the scratchpad; remove with `git worktree remove --force`.
- Pushing: the shell's VS Code credential socket died; push with `GIT_ASKPASS= git -c credential.helper='!gh auth git-credential' push origin main` (Tony approved by running it).
- Open questions to Tony: the context figure.

## Standing practice for this tenure
- Ask Tony for the framework's context-remaining figure at each round boundary and before any outcome-bearing round; treat about half as the handoff zone (Tony: quality degrades with context, not only at the edge).
- Theater check, from Tony's account of Mallku: if producing the evidence of progress is costing more than building the thing itself would, stop and say so. In tupay the thing is the fence service; the apparatus is the measures.
