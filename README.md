# tupay

*Tupay* (Quechua): to meet, to fit together. The gloss is the steward's, unverified; check before using it publicly.

**What it is.** An end-to-end test of a software-engineering workflow. Start from two inputs, a **service contract** and a **failure model**. Derive paired artifacts from them: a formal model, an implementation, paired tests, a fault-injection testbed, and an observability layer. Use divergence between the model and the implementation as the analytic signal. The system built here is deliberately small (a 3-node lease service with fencing tokens). The subject is the workflow, not the system.

**The question.** When the contract or the failure model changes, does the workflow adapt its artifacts, or is it better to regenerate them? Regenerating is restart (the coarsest fence); adapting is recovery. The yardstick, inherited from the cloudflare project: *adaptation must match regeneration on correctness and beat it on cost.*

Start with `docs/seed.md`. `docs/seed-log.md` is the append-only record of how the idea evolved.

Layout (planned): `contract/` and `failure-model/` (the inputs, versioned), `model/` (TLA+), `impl/` (Go), `tests/` (paired), `testbed/`, `observe/`, `experiments/` (pre-registrations and results), `docs/`, `timestamps/` (OpenTimestamps proofs, one per commit; run `scripts/install-hooks.sh` once per clone).
