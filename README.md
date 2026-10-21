# tupay

*Tupay* (Quechua): to meet, to run into; in some dictionaries also to collide or clash. Verified against several dictionaries on 2026-10-20 (see `docs/seed-log.md`).

**What it is.** An end-to-end test of a software-engineering workflow. Start from two inputs, a **service contract** and a **failure model**. Derive paired artifacts from them: a formal model, an implementation, paired tests, a fault-injection testbed, and an observability layer. Use divergence between the model and the implementation as the analytic signal. The system built here is deliberately small (a 3-node lease service with fencing tokens). The subject is the workflow, not the system.

**The question.** When the contract or the failure model changes, does the workflow adapt its artifacts, or is it better to regenerate them? Regenerating is restart (the coarsest fence); adapting is recovery. The yardstick, inherited from the cloudflare project: *adaptation must match regeneration on correctness and beat it on cost.*

**Status (2026-10-21):** M1 closed (`experiments/M1-result.md`); X1 scored (`experiments/X1-result.md`): on an additive contract change, adaptation matched regeneration on correctness and beat it on cost, by a wide margin for the model and a narrow one for the implementation; the one divergence, in a regenerate arm on a hold-out schedule, was judged a model defect of the stale-leadership class. Next: interface v2.2, then X2 (partial and simplex partitions).

Start with `docs/seed.md`. `docs/seed-log.md` is the append-only record of how the idea evolved.

## How it is built
Different model families write the two sides, from the inputs and the shared interfaces only, each in an isolated checkout, each committing its own predictions before its first run. The steward (a Claude Fable 5.1 instance, with Tony Mason) writes the inputs, the interfaces and the briefs, runs both sides, and authors neither. A divergence is reported as unexplained until a judge from a third family rules on the evidence. `AGENTS.md` states the rules; `NOTICE` states who wrote what.

## How to verify
- **Stamps.** Every commit has an OpenTimestamps proof in `timestamps/` (pending) or `timestamps/anchored/` (anchored in Bitcoin). To check one: `ots verify timestamps/<commit-hash>.ots` with the `opentimestamps-client` (`uv sync` installs it). Run `scripts/install-hooks.sh` once per clone to stamp your own commits.
- **Signatures.** Commits are signed with the project key, except six listed in `NOTICE`.
- **Runs.** `model/run.sh --all` (Java 11 and `tla2tools.jar`) and `impl/run.sh --all --seeds 3` (Go 1.22) each print one verdict per schedule; `--mutations` runs the mutation pairs. `observe/provenance_check.py <trace.jsonl>` checks that every storage decision traces to its grant.

## Layout
`contract/` and `failure-model/` (the inputs, versioned, never edited in place), `tests/pairs-v1.md` (the shared clause × cell list), `testbed/` (the schedule format and the shared schedules), `observe/` (the event schema and the steward's checker), `model/` (TLA+), `impl/` (Go), `experiments/` (pre-registrations, results, evidence), `docs/` (seed, log, plan, briefs), `timestamps/`.

## License
Software under the [Apache License 2.0](LICENSE); the written record under [CC BY 4.0](LICENSE-docs). `NOTICE` has the map and the authorship statement.
