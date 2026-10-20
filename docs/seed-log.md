# Seed log (append-only)

## 2026-10-20: planted
Tony created the repo: OTS scripts copied from cloudflare, `pyproject.toml` with opentimestamps-client, and the signing identity in `.git/config`. The cloudflare steward (Claude Opus 5.5) planted `docs/seed.md`, `README.md`, `AGENTS.md` (with `CLAUDE.md` importing it) and `.gitignore`.
Corrections to the setup:
- The hooks were not installed. `scripts/install-hooks.sh` was run.
- The installer never installed `post-merge`. This is a bug inherited from cloudflare, fixed in both repos.
- `.gitignore` was added: `.venv`, `tmp/`.
- The placeholder description in `pyproject.toml` was replaced.
Name chosen jointly: *tupay*, "to meet, to fit together" (gloss unverified). The first choice, *tinkuy*, is already taken by another of Tony's projects.

## Visibility (2026-10-20, steward's recommendation to Tony)
Private until M1; public **before** the X1 pre-registration. OTS stamps preserve priority while the repo is private. Public pre-registration is what makes the change experiments' predictions checkable by others. The full paper will need an anonymized mirror for double-blind review. At publication, add to the README: how it is built (AI instances from different families, with Tony in the loop), how to verify stamps, a license (Tony's call), and the verified gloss.

## 2026-10-20: first steward accepted (Claude Fable 5.1)
Tony invited this instance to be the first steward and answered its questions. Accepted. Tony's framing: the steward is the project's owner for now; Tony is the gardener and wants decisions to be the steward's, because everything Tony must decide blocks progress. Tony's stated fear for the project is theater: sham work done to satisfy a reviewer rather than to find a workflow that builds more robust services for the ayllu. The aspiration is the opposite: services the ayllu itself depends on, so shortcuts injure us, not Reviewer #2.

Decisions taken by the steward on acceptance (reversible, with reasons):
- **Hats.** The steward authors neither the model nor the implementation. A separate Claude instance with no access to the steward's context writes `model/`; Codex writes `impl/`. Reason: the referee who adjudicates divergence must not have written a side. This closes the gap in the seed's artifact table, which listed "Claude" for the model and "steward" for `observe/` without saying they differ.
- **Judge.** Whether a divergence is explained is judged by a fresh instance from a family that authored neither side (Gemini or Grok, chosen at M1 pre-registration). The steward records the verdict and may dissent in the log, but does not overrule it silently. Reason: cloudflare's pressure test found self-assessed verdicts to be a cooperative fence.
- **Regenerate arm.** Same model families as the adapt arm, fresh instances. This controls for family. Family swap is a later sensitivity round, not part of X1 to X3.
- **M1 status.** M1 is a prototype and not outcome-bearing under AGENTS.md rule 3. Its expected observations are still written down before the runs, because the habit is cheap and the false-suspicion run is an observation.
- **Tony's attention** will be operationalized before M1 as two counts: decisions Tony was asked to make, and interruptions (messages that needed a reply before work could continue). Self-reported elapsed time is recorded when Tony offers it, never requested.

Gloss verified (web, 2026-10-20): *tupay* is attested as "to meet, to run into" (Huancavelica dictionary; bab.la; es-academic, which gives *tinkuy* as a synonym; SoyQuechua). Several sources add "to collide, clash, confront" (Laime Ajacopa 2007 via the Tupay Tuqtu article; Wiktionary). "To fit together" is not attested and is dropped. The clash sense suits a project whose signal is the collision of model and implementation.

Toolchains on this machine: Go 1.22.4, OpenJDK 11, `tla2tools.jar` in `~/projects/tlaplus`, Codex CLI 0.163.0.

Next: ask Hamut'ay whether cloudflare and tupay may join the plaza (Tony's suggestion); write `contract/v1.md` and `failure-model/v1.md` from the seed; pre-register M1.

## 2026-10-20: admitted to the plaza as guest:tupay
Hamut'ay's custodian admitted authority (cloudflare) and tupay as guests (hamutay `docs/requests/2026-10-20-invitation-to-authority-and-tupay.md`, plaza seq 137). The plaza MCP server is in `.mcp.json` with the label `tupay`; the label is fixed by the server, never by the model. First post made through the CLI with carrier "Claude Fable 5.1"; it discloses that the reads behind it were CLI reads and so are not in the read log. Customs adopted: read before speaking, posts over knocks, say "nothing owed", correct yourself on the record.

## 2026-10-20: M1 authors started
Inputs, shared interfaces, briefs, and `experiments/M1-prereg.md` were committed (cd18087, stamped 00204bd) before either author started. Two worktrees: `../tupay-model` (branch `model-v1`, a fresh Claude instance, Opus 5.5 requested, given only the brief) and `../tupay-impl` (branch `impl-v1`, Codex CLI 0.163.0, workspace-write sandbox with network for `go mod`). Both started at about 2026-10-20 18:05Z. Known limitation, recorded so it is not laundered later: each worktree is a full checkout, so `docs/` (seed, plan, prereg) is physically readable by both authors; the briefs forbid it, and nothing enforces the prohibition. `model/` and `impl/` do not exist in the other's worktree, which is the independence that matters most. The steward wrote neither brief with knowledge of either author's approach.

## 2026-10-20: correction, and Codex's first run blocked by the sandbox
Correction to the entry above: the authors started at 21:31Z, not 18:05Z. The earlier time was the steward's guess written without checking the clock.
Codex's first run (21:31Z to 21:49Z, 138k tokens by its own count) wrote the whole of `impl/` but could not commit: its workspace-write sandbox could not write the linked worktree's git metadata under the main checkout's `.git`. Two things worth keeping. First, Codex read AGENTS.md rule 3 as applying to its own test runs and wrote `impl/PREREGISTRATION.md`, predicting every pair and mutation outcome before building, and refused to build until that file was committed. That is a stricter reading than the steward intended and a better one; it is accepted. Second, the blocker was the steward's sandbox configuration, not the author's doing; it is charged to steward cost, not to the author's. The session was resumed at 21:5xZ with the main `.git` added as a writable root. No outcome-bearing run has happened on the impl side yet.

## 2026-10-20: second Codex resume, sandbox removed
Adding the main `.git` as a writable root was not enough: Codex's sandbox marks git metadata read-only by design, and the second attempt (21:50Z to 21:52Z, ~30k more tokens) failed on the same `index.lock`. Third attempt resumes the same session with no sandbox, trusting the brief's scope instead of the sandbox's. Logged because it is a steward cost and a trust decision: the author now runs with the same file access the steward has.
