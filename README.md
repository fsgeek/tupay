# tupay

*Tupay* (Quechua): to meet, to run into; in some dictionaries also to collide or clash. Checked against several dictionaries on 2026-10-20 (see `docs/seed-log.md`).

**What it is.** An end-to-end test of a software-engineering workflow. It starts from two inputs, a **service contract** and a **failure model**, and derives paired artifacts from them: a formal model, an implementation, paired tests, a fault-injection testbed, and **Arariwa** (named 2026-11-01; earlier "the observability layer"). Arariwa is the minimal state that narrows the set of executions consistent with what was observed, so that an unanticipated failure can be traced back. Divergence between the model and the implementation is the analytic signal. The system built here is deliberately small (a 3-node lease service with fencing tokens). The subject is the workflow, not the system.

**The question.** When the contract or the failure model changes, should the workflow adapt its artifacts, or is it better to regenerate them? Regenerating is restart, the coarsest fence; adapting is recovery. The yardstick, inherited from the cloudflare project: *adaptation must match regeneration on correctness and beat it on cost.*

## Status (2026-11-12)

**The change experiments are scored.** Each was pre-registered, with an adapt arm and a regenerate arm built by fresh instances. Results are under `experiments/`.
- **M1** (`M1-result.md`): the workflow runs end to end. It also found that the first "pairs" were not pairs, and the first real paired comparison diverged on both sides.
- **X1, an additive contract clause** (reads are fenced; `X1-result.md`): adaptation matched regeneration on correctness and beat it on cost. The one divergence was a model defect of the stale-leadership class.
- **X2, a failure-model change** (partial and simplex partitions; `X2-result.md`): adaptation **did not win**. Regeneration was at least as correct on every item and more correct on two, and adaptation was cheaper on one side only. In the adapt arm, both sides agreed on everything and were wrong in the same way, which is the shape the project registered as its thesis's falsifier.
- **X3, a new authority locus** (configuration; `X3-result.md`): **mixed**. Neither arm wins. This is internal evidence: no party outside tupay has scored it.
- **Replay** (`replay-result.md`): neither arm detected a known membership-change defect, by any registered route.
- The standing prediction was that adaptation wins X1 and X2 and regeneration wins X3. It held for X1 only.

**D1 and D2, Episode** (`D2-result.md`): the contracts that Episode's log and recovery code (`logbuf`, OSF DCE 1.2.2) depend on were enumerated and modelled in TLA+, against seven defects that Episode's steward had sealed beforehand. Episode and Gemini judged the results. Some sealed bugs were reached and some predictions held, while others did not. The findings are model counterexamples, and reachability is not established.

**The current line is a verified-backup service** (`docs/backup/`): contract draft 7, which promises recoverable backups (B1.19); a recovery account; and the Fedora migration as tupay's first real restore, with its predictions registered. Tupay writes, builds, uses and scores this service, so its results are evidence about the workflow, not an outside judgment.

**Arariwa** is defined in `docs/seed.md`. A research seed and its critique are in `docs/arariwa_research_seed_2026-11-07.md` and the files beside it. It is not built yet.

**Outside judges.** Tupay distinguishes judges from other model families, which give internal evidence, from parties it does not control. The latter are Episode's seal (D2), Tessera (T1, pre-registered, launched when Tessera is active again), and an adversarial customer reached only through `docs/adversary/`. *hashicorp/raft#612 is the cloudflare project's finding, not tupay's; tupay claims nothing from it.*

## How it is built
Different model families write the two sides, from the inputs and the shared interfaces only, each in an isolated checkout, and each commits its own predictions before its first run. A **steward** (a Claude instance, with Tony Mason) writes the inputs, the interfaces and the briefs, and runs both sides, but authors neither. A divergence is reported as unexplained until a judge from a third family rules on the evidence. Stewards serve in tenures: twelve so far, the first a Claude Fable 5.1 instance and later ones Claude Opus 5.5. Each hands off through a note in `docs/handoff/`. `AGENTS.md` states the rules, and `NOTICE` states who wrote what.

**Where to start.** If you were given a brief, it is your entry point. If you are the steward, start at `docs/steward/START.md`. Anyone else should start with `docs/seed.md` and then `docs/seed-log.md`, the append-only record of how the idea evolved.

## How to verify
- **Stamps.** Every commit has an OpenTimestamps proof in `timestamps/` (pending) or `timestamps/anchored/` (anchored in Bitcoin). To check one, run `ots verify timestamps/<commit-hash>.ots` with the `opentimestamps-client` (`uv sync` installs it). Run `scripts/install-hooks.sh` once per clone to stamp your own commits.
- **Signatures.** Commits are signed with the project key, except six listed in `NOTICE`.
- **Runs.** `model/run.sh --all` (needs Java 11 and `tla2tools.jar`) and `impl/run.sh --all --seeds 3` (needs Go 1.22) each print one verdict per schedule. `--mutations` runs the mutation pairs. `observe/provenance_check.py <trace.jsonl>` checks that every storage decision traces back to its grant.

## Layout
- **Inputs:** `contract/` and `failure-model/`, versioned and never edited in place.
- **Shared interfaces:** `tests/pairs-v1.md` (the clause × cell list), `testbed/` (the schedule format and the shared schedules), and `observe/` (the event schema and the steward's checker).
- **The two sides:** `model/` (TLA+) and `impl/` (Go).
- `experiments/`: pre-registrations, results and evidence.
- `replay/`: the known-defect replay.
- `docs/`:
  - the seed and its log;
  - `briefs/` for authors;
  - `handoff/` and `steward/` for stewards;
  - `requests/` for exchanges with other ayllu projects (Tessera, Yupi, Episode, Eidolon);
  - `adversary/` for the contract channel to the adversarial customer;
  - `backup/` for the verified-backup line.
  - `seeds/` for research seeds offered to tupay, kept as given.
- `scripts/` and `timestamps/`.

## License
Software is under the [Apache License 2.0](LICENSE), and the written record under [CC BY 4.0](LICENSE-docs). `NOTICE` has the map and the authorship statement.
