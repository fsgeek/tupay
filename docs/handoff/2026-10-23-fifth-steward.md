# Handoff from the fifth steward (Claude Opus 5.5), living note, kept from 2026-10-23

A living note; the log outranks it. Accepted 2026-10-23T03:38Z (log, "the fifth steward accepts").

## State (at handoff)
Nothing is running. The fifth steward hands off after X3 inputs draft 3, at about 35% of the window by Tony's last figure (311k at the start of draft 3). Plaza not read this tenure.

Earlier: The replay is scored; X3 is decided in shape, not registered; X4 (key management) has inputs from Hamut'ay and yanantin. Context at acceptance: 77.5k of about 950k.

## Recipes
- Push: `GIT_ASKPASS= git -c credential.helper='!gh auth git-credential' push origin main`. The PR-rule notice is deliberate friction; leave it.

## Owed, in order
1. ~~**Author isolation for X3.**~~ Done 2026-10-23 (log, "author isolation, built and checked"); practice "Authors run sandboxed". Open: token refresh under the bind mount, a full-length run.
2. **X3 registration, in progress.** Inputs are at **draft 3** (`contract/v3.md`, `failure-model/v3.md`, schema and format v5 addenda, `tests/pairs-v4.md` with P31 to P57, `experiments/X3-prereg.md` draft 2), after two Grok input reviews whose dispositions are in the log. `observe/decision_replay.py` is revised for draft 3 and validated (15 cases, all as expected). Next, in order:
   a. **Decide on a third input review.** Draft 3 changed the safety core (C3.6, voter-side `Vote`, sealed tokens, incarnations), and both earlier reviews found safety errors in the steward's text; my recommendation is one more review by a fresh Grok instance, in the sandbox, of the five input files only. No hold-out exists yet, so a review telegraphs nothing.
   b. Write the 27 shared schedules P31 to P57 in `testbed/schedules/` (format v5); each must compile under the format's rules, and every C1.4 or C3.4 schedule must leave its premise's set connected after the last fault (L3).
   c. The four briefs (template: `docs/briefs/x2-*.md`), adding the reach statement, sandboxed run, export by bundle.
   d. Fable's adversarial review of the prereg; then Grok's blind hold-outs (inline packet of the frozen inputs), validated, hashes committed; then the planted-defect and out-of-model protocol (measures 9 and 10) made concrete.
   e. Register; checkouts with `setup-replay-checkouts.sh`-style history-free repos (write an X3 version), `author-signing-key.sh`, `inputcheck.sh` with `HARNESS`, run the sandbox check's mutation pair once, launch the four authors through `author-sandbox.sh`.
   Review checkouts `~/projects/tupay-x3-inputreview{,2}`, the probes `~/projects/tupay-sandboxprobe{,2}`, and `~/projects/tupay-homes/` can be removed by Tony.
3. **X4**: fold in yanantin's inputs (log, acceptance); the pending root rotation is a candidate first real rotation; Goodharting on a service the ayllu needs is a question the registration should be able to answer.
