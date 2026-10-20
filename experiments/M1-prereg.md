# M1 pre-registration (steward, 2026-10-20, before any author starts)

M1 is a prototype, not an outcome-bearing run under AGENTS.md rule 3. This is written anyway: the predictions below are cheap, and recording them now is the habit the project exists to test. Amendments are additive and say whether an outcome informed them.

## Setup, fixed here
- Model author: a fresh Claude instance (Opus 5.5 requested; the carrier is recorded in the result), given only `docs/briefs/model-author.md` and the files it names, in its own git worktree.
- Implementation author: Codex (the CLI on this machine, version recorded in the result), given only `docs/briefs/impl-author.md` and the files it names, in its own worktree.
- Neither sees the other's work before its first-version commit. The steward merges both in one commit after both are in, and does not edit either side before the first paired runs.
- Judge of any divergence: a fresh instance of a family that authored neither side. Choice recorded when the first divergence appears, not before.

## Predictions
- **P-a.** Both first versions will interpret at least one input differently from each other. Most likely places: what "restart" restores (F1.1), whether a paused holder's expired token is "stale" or merely "late" (F1.3 with C1.2), and C1.4's "long enough".
- **P-b.** At the first paired run, at least one of the twelve pairs will disagree between sides. Predicted count: 1 to 3. Predicted location: P10 to P12 (liveness), or P5/P6 (fence after partition or pause).
- **P-c.** Every mutation pair will fail on its own side on the first run. If one does not, the mutation is misplaced, and that is reported as a defect in the pair, not in the artifact.
- **P-d.** The false-suspicion run will show the isolated grantor's holder's write **rejected** by storage after the new grant's write is accepted, with provenance tracing the rejected token to the old `grantor_term`. If the old holder's write arrives before any new-token write, it will be **accepted**, and that is contract-conformant.
- **P-e.** The observability layer on at least one side will fail its own test (some storage decision without a complete causal chain) on the first run.

## Scoring
A prediction is scored only against the first paired run after the merge, before any fix on either side. Later runs are a separate record.

## Cost baseline (the measures the change experiments compare against)
Recorded per author in `experiments/M1-result.md`:
- Tokens consumed (from the harness, where reported) and wall-clock from spawn to first-version commit.
- Steward tokens and wall-clock for the merge and the first paired run.
- Decisions asked of Tony: count, listed. Interruptions of Tony (a message that needed Tony's reply before work could continue): count, listed.
- Divergence count at first run; stale-tag residue (tags naming a retired id): expected 0 in M1 since nothing is retired yet.

## Not in M1
Hold-out cells. Family swap. Fixing divergences before they are recorded. Anything shaped for a paper.
