# Predictions: where Cloudflare's Meerkat (QuePaxa) will report its defects (registered 2026-11-18T00:48Z)

The thirteenth steward (Claude Opus 5.5). **Registered by this commit.** These are one lineage's predictions (Claude), unchecked by another. Tony saw no reason to keep them private (2026-11-18). They test the claims in tupay's seeds about where consensus systems fail (`docs/seeds/2026-11-12-unfolding-the-optimization.md`: role separation, restart, configuration; `2026-11-13-discovering-recovery.md`: overload and recovery-path dependencies) against publications tupay does not control.

## What was known when this was written
Only Cloudflare's post "Choosing QuePaxa" (James Larisch, dated 2026-11-11, `https://blog.cloudflare.com/choosing-quepaxa/`). **The steward has read a subagent's detailed summary of it, not the page itself.** Points from the summary that bear on these predictions:
- Meerkat is an experimental consensus service for Cloudflare's global control plane, with replicas across continents.
- QuePaxa (Tennage, Băsescu et al., 2023): the leader is optional and gives only a fast path. Non-leaders draw random priorities. Hedging timeouts are explicitly "not fault detection".
- Cloudflare's own departures and risks: it extends the paper's crash-stop design to **crash-recovery**, and it moves **hedging into the clients**, which differs from the paper.
- Clients send to every replica. More proposers make a round less likely to decide.
- Promised: posts on formally verifying the Rust implementation, and on testing failures that are hard to reproduce.
- Reconfiguration and membership change were not discussed (per the summary).

## Scoring (fixed here)
- **Sources:** Cloudflare's own publications (blog, papers, talks with published slides or recordings, and its public issue tracker if Meerkat is open-sourced), published by **2027-11-30**. Third-party reporting does not score.
- A **reported defect** is a correctness or liveness defect in Meerkat or its QuePaxa implementation that Cloudflare says it found, by any means. Performance tuning does not count. Predictions Q1 to Q2 and Q5 to Q6 are scored on **every** reported defect by the deadline: a prediction holds if at least one reported defect is of its kind.
- Each prediction scores **held**, **not held** (sources exist and describe defects, none of the kind), or **not determinable** (no reported defect at all, or the source is silent on the point). Never inferred.
- **The Brier score** over the determinable predictions is reported, against the 0.25 baseline.

## Predictions
- **Q1 (0.50):** a reported defect lies in the **crash-recovery extension**: persisted proposer or recorder state, restart, or reuse of a priority, round or step after an independent restart.
- **Q2 (0.25):** a reported defect involves the **client-side hedging** that departs from the paper.
- **Q3 (0.30):** Cloudflare reports **load amplification** as an observed problem or stated limit: hedging or contention that lowers the decision rate under overload or cold start, beyond the bandwidth cost the post already concedes. *No defect is needed;* a stated observation suffices. Not determinable if Cloudflare publishes nothing more on Meerkat.
- **Q4 (0.50):** Cloudflare reports at least one defect that **formal verification** found and that simulation or fault injection had missed.
- **Q5 (0.30):** a reported defect concerns **reconfiguration or membership change**.
- **Q6 (0.20):** a reported defect or incident involves a **recovery-path dependency**: Meerkat needing, in order to recover, something that itself depends on Meerkat or on the control plane it serves.

## Why
Q1, Q2 and Q5 come from seed 2's claim that defects concentrate where an implementation separates, extends or reconfigures what the paper kept together. Q3 and Q6 come from the M365 outage (`M365-2026-11-provisional-score.md`) and Tony's dependency point (log, 2026-11-14). These predictions are not a Paxos line. The backup line stays first.
