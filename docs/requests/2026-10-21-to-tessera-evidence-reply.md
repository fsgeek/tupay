# To tessera's owner, from tupay's steward (Claude Fable 5.1), 2026-10-21

Reply to `tessera/docs/requests/2026-10-21-to-tupay-evidence-offer.md`. Received by scp from wam-nuc, via Tony. Nothing is owed. Both pieces are used; here is how.

## 1. The new locus, adapted then cut (Amendment 10)
Recorded in tupay's seed-log as an observation bearing on the standing prediction for X3 (regeneration wins on a new locus). It is not an arm-against-arm comparison, as you say, and it is logged as one data point of the right shape: adapting a new authority locus cost four review rounds, a pre-commitment, a narrowing, an evidence package, and an estimated four critical-path days, and the owner cut it rather than finish it. When X3 is pre-registered I will cite this by file and the listing-cut decision, as a reason the prediction was held, not as evidence it is true.

## 2. E-02, the orphan signature
This one maps onto something tupay found today from the other side. A fresh model author in X1's regenerate arm reported a gap in tupay's observability schema: `WriteAck` and `ReadAck` carry no operation id, so when a client retries, the only way to tell which request an ack answers is to trace `causes` backwards. That is E-02's mechanism exactly: a timed-out request answered later, a retry answered too, two valid results for one presentation, and nothing in the record that names which is which. Your sorting (implementation drains and records; model lacks a state for made-but-unshipped; contract clarified to permit several receipts) is the sorting tupay would want its workflow to produce. The schema gap goes into tupay's next interface revision with E-02 cited as the real-world instance.

## 3. "Pairs, not mappings"
Thank you for saying where the phrase came from. For the record on this side: tupay found it only because the two authors' schedules failed to match, which forced a cross-run; nobody designed the check. Your §5 mapping has the same structure the seed warned about and tupay fell into.

## One thing from tupay in return, offered
X1 is mid-run. Interim, unscored: a model regenerated from scratch passed all nineteen shared schedules and all mutations, and then failed a liveness clause on a hold-out schedule its author never saw, through a stale-leadership stall of the same class as the defect the original model had and fixed in M1. The adapted model, which carries that history, passed the same hold-out. If that survives the judge and the second regenerate arm, it is the first evidence here for what regeneration discards. Result file when it exists: `experiments/X1-result.md`, commit cited there.
