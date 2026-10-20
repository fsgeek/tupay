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
