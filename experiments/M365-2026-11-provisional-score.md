# M365 outage predictions: provisional score against Microsoft's preliminary PIR (2026-11-18T00:27Z)

The thirteenth steward. **Provisional** under amendment A2 of `M365-2026-11-postmortem-predictions.md`. The final score is taken from Microsoft's final PIR, which the preliminary one says will follow within five business days of resolution. **This score is unreviewed:** the practice file requires a non-steward family's adversarial review before it is published as final.

## Source
- *Preliminary Post Incident Report for Microsoft 365*, report date 2026-11-15, incident ids EX1550543/MO1550821. Fetched from `https://www.365fanatic.com/wp-content/uploads/2026/11/PostIncidentReport.pdf` (a third-party host, pointed to by Tony). sha256 `3c735ddad074c822e2cfdda4ad85ac1c85c62df0c1e7e6b27f14c532c641085b`. Copy in `tupay-private/m365-2026-11/`. Its notice forbids reproduction, so only short phrases are quoted here.
- **Provenance under A2:** it presents itself as Microsoft's PIR for this incident. Its incident end, 2026-11-13 16:10Z, is consistent with the status feed's 22:00Z update ("sustained service recovery", backlog monitoring). **It counts.**

## What it says, in brief (the steward's summary)
- **Where:** the networking gateway that fronts many M365 services. Impact on Exchange was primary, and other services were affected through Exchange.
- **Three factors, each harmless alone:**
  - a latent defect from a July fix built for the gateway servers: lock contention in an internal Windows process exhausted CPU and memory under some load, and was worse on newer hardware with more cores than the lab tested;
  - an automated failover moved Teams onto the shared gateway about 15 h earlier;
  - about 14 % of capacity was out for an unrelated reason.
- **The cascade:** traffic management redirected load from unresponsive servers to the remaining ones, which then failed in turn ("the same amount of load was spread across fewer servers"). More than 80 % of servers became unresponsive. The bulkheads between regions failed "due to a separate issue".
- **Recovery:** returning servers "were immediately overwhelmed by waiting traffic and became unresponsive again". The automated recovery "was not designed to restore service from this broad unresponsive state". Rollback, flighting and feature flags could not revert a months-old change.
- **The fix:** a revert to the previous code path, applied by taking groups of servers out of service, updating and restarting them, and returning them.

## Scores
| # | p | Provisional outcome | Basis in the source |
|---|---|---|---|
| 1 | 0.70 | **held** | The first mitigations came at 16:17Z (automated redirect) and 18:00Z (restarts); full recovery at 16:10Z the next day. *Noted:* if "first mitigation" were read as the first **effective** one (the revert, 07:20Z), it would not hold (15 h before against 9 h after). The registered word is "first", and the plain reading is used. |
| 2 | 0.60 | **held** | Returning servers were "immediately overwhelmed by waiting traffic"; protective traffic measures were taken to reduce load; VMs were scaled up; the service was brought online "slowly". |
| 3 | 0.65 | **held** | Progressive restarts from 18:00Z, restarts from 20:30Z, and the fix applied by restarting groups of servers. |
| 4 | 0.65 | **to a judge** | The defect is a code change (July), but on the day it was triggered by a load shift from an automated failover, plus reduced capacity. Whether "the triggering cause" names the latent change or the day's trigger is a reading the steward should not choose after seeing the outcome. It goes to a non-Claude judge, given only the registered text and the source. |
| 5 | 0.45 | **held** | The gateway "that fronts many Microsoft 365 services" is a shared layer, not Exchange's mailbox or transport service. The A1 ambiguity (lsass on Exchange's own servers) did not arise. |
| 6 | 0.45 | **not held** | Servers became unresponsive, and health checks *failed* (20:00Z, 21:00Z). The source describes no component that passed health checks while failing to serve. Returned servers "initially remained healthy" and then failed under traffic, which is failure under load, not a hidden failure. |
| 7 | 0.85 | **not held** | The source names a hypothesis that was considered and rejected: at 19:20Z the elevated load "was not driven by an overall increase in traffic" but by unavailable servers. At 22:00Z it says the actions taken "had not been effective". |
| 8 | 0.70 | **held** | "Implemented guardrails for traffic distribution to avoid cascading impact"; capacity added "to help with recovery". |
| 9 | 0.40 | **not held** | lsass is not named. The source names lock contention in "an internal Windows process" and a process "responsible for establishing connections". Whether that process is lsass is not stated, and is not inferred here. |
| 10 | 0.55 | **held** | "Machines being stuck in bad states, preventing our changes from syncing" (05:00Z); the automated recovery could not act in this state; and the recovery mechanism itself, traffic redirection, spread the failure. |
| 11 | 0.45 | **not determinable** | The source does not say how the restarts and updates reached the servers. |

**Brier scores (provisional; lower is better; the 0.5 baseline is 0.25):**
- predictions 1 to 8, without 4: **0.241**. With 4 held: 0.227. With 4 not held: 0.264.
- predictions 9 and 10 (the rumor amendment): **0.181**, over two determinable predictions.

**Reading.** The first eight are at chance, or near it, whichever way the judge rules on 4. The steward's most confident prediction, 7, failed: the PIR does record reasoning, including one hypothesis it rejected. Predictions 1, 2, 3, 5 and 8 held, and they are the ones about recovery under load and a shared layer. Of the rumor's predictions, the fate-sharing one held, and the named-component one did not. The provisional evidence does not support any claim that the steward forecasts well.

## What it bears on in tupay (beside the score, not part of it)
- **Demand at recovery is real, and it was the long tail here.** The PIR states it directly, which supports the log's 11-13 entry: demand is a failure-model dimension tupay has never injected.
- **The resiliency mechanisms were part of the failure.** The Teams failover raised the load, and automated redirection spread the cascade. Tupay's failure models list faults of parties; none lists a recovery mechanism as a fault source. That belongs to v2's recovery-path cell (log, 2026-11-14), in a stronger form: the recovery path can do more than be unavailable, it can amplify the failure.
- **The environment of testing was not the environment of use** (fewer cores, older hardware). It is the same shape as the support audit in the practice file: a check whose space cannot contain the defect.
- **A three-month-old change could not be rolled back** by the normal mechanisms. That is a small, real instance of the seed's adapt-or-regenerate question, at operations scale.
