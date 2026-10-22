# Steward: start here

If you are an author (you were given a brief), stop: your brief is your entry point, and nothing in `docs/steward/` is for you.

You are tupay's steward if Tony has invited you to the role, or a handoff note names you. Read, in this order:
1. `docs/seed.md`: what tupay is for (the current state of the seed; `docs/seed-log.md` is its history).
2. The newest handoff note in `docs/handoff/`: the state at the last boundary and what is owed.
3. `docs/steward-practice.md`: how a round runs. Every rule names the error that produced it.
4. `docs/steward/log-index.md`: a bounded index of the log that **declares what it omits**. Regenerate it with `python3 scripts/steward/log-index.py` before reading, and read every log entry it lists under errors before you start a round.
5. `qhaway recall()` and, before deciding anything that may already have been decided, a khipumaq search.

Then the log is yours to append to, never to rewrite (`AGENTS.md` rule 1). Times go into it only from `date -u` read in the same command.

## Why this file exists
`AGENTS.md` is read by every model family's harness (Claude Code, Codex and Grok all load it; Grok also loads `CLAUDE.md`), so it carries only rules every author needs. Until 2026-10-22 its first line told every reader to read the seed and the log's tail; both replay Codex authors executed that line as their first command, and only the history-free checkout kept the log out of their reach. Author checkouts now exclude `CLAUDE.md` and `docs/steward/`, and the input checks fail if either is present. And "read the tail" was a silent truncation: a steward could not tell what lay outside it. The index replaces it with a bounded list and a stated omission.
