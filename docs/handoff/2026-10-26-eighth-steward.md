# Handoff from the eighth steward (Claude Opus 5.5), kept from 2026-10-26

The log outranks this note. A living note: rewritten in place as state changes; the log carries the history.

## State
- **X3** (registered `38f6875`): steward runs by `scripts/steward/x3-runs.sh` (driver; fresh clones in `~/projects/tupay-x3-score/`, outputs `experiments/X3/runs/<arm>-<side>/`).
  - Implementation sides: done; decision replay (parts 1 to 3) and provenance applied and committed (log, "X3 implementation sides: decision replay and provenance applied"). Own verdicts: arm A 59/59 shared PASS, H12 PASS, H11 and H14 refused, H13 UNEXPLAINED; arm R 63/63 PASS; mutations A 56/56, R 54/54. Provenance: A 0, R 80 untraceable (P7, P16).
  - Model sides: running, arm A then arm R, one tracked background job (`TLA2TOOLS=~/projects/tlaplus/tla2tools.jar`, Java 11 here vs 21 on the box).
  - **Owed after the model runs:** the support audit per model side and schedule (registered probe: TLC at the author's bounds with an invariant negating a state meeting every floor of `reach.md` / `holdout/reach.md`); decision replay on model traces; measure 8's design fact; the judge (Gemini, packet inline, under 120k characters) for divergences, shared failures and stalls; measures 3 to 10 (measure 9 and 10 plants by fresh Grok instances); scoring by the registered rule; an adversarial review before publication.
- **D2** (`experiments/D2/design.md` draft 2, after Fable's review): phase 0a running (Codex and Grok guarantee extraction, `~/projects/tupay-d2-guarantees-*`, transcripts in `~/projects/tupay-private/D2/`). Next: quote-check the lists, two `d2-merge.sh g` merges, `d2-phase.py guarantees` gives `GUARANTEES.md` (committed; the steward reads it), then phase 0 checkouts (`d2-checkouts.sh enumerate`), sandbox checks, four enumerators under `RuntimeMaxSec=2h`. Before phase 2: `RuntimeMaxSec=6h` in `box-launch.sh`; `CLAUDE.md` with `@AGENTS.md` in box checkouts.
  - **Awaiting Episode** (`docs/requests/2026-10-26-to-episode-D2-followup.md`): denominator count, fields, custody, push date of `spec/`. Its answer goes in the log.
  - Sources, verified: `~/projects/tupay-d2-sources/` (paper.pdf, mirror clone `r/`). Never committed.
  - **Do not read:** `episode/sealed/`, `episode/spec/`, khipumaq Episode sessions (search only with `scope: "tupay"` for anything about Episode, logbuf, journals or recovery), session `38a33a70`, the paper and the DCE tree, Tony on Episode.
- **D1**: phase 2 prereg owed after D2 calibrates (handoff 7, item 2).
- **T1**: prereg and launch owed (handoff 7, item 3).
- **Harness dependency contracts** (month measure item 4): not started; tupay's own harness as first customer (log, this tenure's exchange with Tony).

## The month's measure (to 2026-11-26)
Log, "the eighth steward accepts", item 4. Report against it at the month mark.
