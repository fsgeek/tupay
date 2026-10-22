# Handoff from the third steward (Claude Opus 5.5), kept from 2026-10-21

A living note, updated at every boundary, so that a crash of this steward's context leaves a recovery record (log entry "third steward accepts", decision 1). The log outranks it. If this steward's session ended without warning, the state below as of its last update is the state; anything after it is in the log or not done.

## State at last update (2026-10-22 03:00Z, context ~45%)
- Replay inputs frozen (02:23Z). Contract v3 (J1.5). Briefs edited after the freeze (memory cap; F vocabulary) and rehashed: `experiments/replay/briefs.sha256`.
- Pre-registration **draft 4** (`406a70d`), after Fable's review of draft 1, ChatGPT's of spec D, the validation gate, and a fresh reading of draft 3. Attribution script + tests committed (`927a5a0`).
- **Hold-out author running** (Fable) → `tmp/replay/holdout/H1-H4.yaml` + `notes.md`. Next: validate the hold-outs on the reference (`tmp/replay/reference/run.py`, system python3, both variants; a hold-out GATED fails is invalid), commit `experiments/replay/holdout/SHA256SUMS`, insert brief hashes into the draft, remove the DRAFT line = **register**. Then `setup-replay-checkouts.sh <reg> D|F model|impl`, `inputcheck-replay.sh <dir> <arm> <side> <K1v4 hash> <needs hash> <holdout hashes>`, start Grok ×2 (`grok -p … --cwd <dir> --always-approve --disable-web-search --output-format plain`) and Codex ×2.
- **X3 decided** (log "amend or rebuild tupay itself"): two arms on the same revised inputs for the fence service; arm A adapts existing artifacts (after the timing repair), arm R regenerates.
- Owed before X3: timing repair (`docs/briefs/fix-timing-impl.md`).
- Withheld in `tmp/replay/` (not backed up): K1 v1–v4, needs, K1 v2 check, reference, hold-outs.
- Pushing: `GIT_ASKPASS= git -c credential.helper='!gh auth git-credential' push origin main`.
- Open questions to Tony: none.

## Standing practice for this tenure
- Ask Tony for the framework's context-remaining figure at each round boundary and before any outcome-bearing round; treat about half as the handoff zone (Tony: quality degrades with context, not only at the edge).
- Theater check, from Tony's account of Mallku: if producing the evidence of progress is costing more than building the thing itself would, stop and say so. In tupay the thing is the fence service; the apparatus is the measures.
