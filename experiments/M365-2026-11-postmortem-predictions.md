# Predictions for Microsoft's post-incident review of the Exchange Online outage, November 2026 (registered 2026-11-14T03:19Z)

The thirteenth steward (Claude Opus 5.5), with Tony. **Registered by this commit, before any post-incident review (PIR) exists.** These are one lineage's predictions (Claude), unchecked by another. They test the recovery hypotheses in tupay's seeds (`docs/seeds/2026-11-13-discovering-recovery.md` §3 and §9; `2026-11-12-unfolding-the-optimization.md`, on restarts and alive-but-dead) against a document tupay does not control.

## What was known when this was written
- Tony: the incident had run for about 36 h, and his own email was out for about 20 h.
- Microsoft's status feed (`https://status.cloud.microsoft/api/feed/mac`, fetched 2026-11-14T03:19Z, sha256 `ed4b21dfefd329b9301b0f000d972a7e890ebc1b681d9d78f2c36cfc8c2a52b4`; copy in `tupay-private/m365-2026-11/`). It holds only the latest update, timestamped 2026-11-13 22:00:36Z:
  - "sustained service recovery" is observed, with monitoring "for an extended period" because of the severity of impact;
  - a backlog of email accrued during the event is being monitored until it processes;
  - the impact list covers Exchange Online and features of about twenty services that interact with it. It also covers Purview authorization, RBAC, sensitivity labels and DLP, and Windows 365 Cloud PCs that use Purview Customer Key;
  - no cause or incident id appears in the feed text;
  - next update due 2026-11-14 02:30Z.
- The steward has read nothing else about the incident: no news, no social media, no earlier updates.

## Scoring (fixed here)
- **Source:** Microsoft's PIR for this incident, or failing that, Microsoft's own public statement of cause and timeline. Third-party reporting does not score.
- Each prediction scores **held**, **not held**, or **not determinable** (the source is silent). A prediction is scored only on what the source states. It is never inferred.
- Each carries the steward's probability. **The Brier score** over the determinable predictions is reported, against the baseline of 0.25 that answering 0.5 to everything would earn.
- If no PIR or statement appears by 2027-01-31, the registration is reported as unscored. It is never re-read against later facts.

## Predictions
1. **Recovery took longer than the fault (0.70).** The stated timeline puts more time between the first mitigation and full recovery than between impact start and the first mitigation.
2. **Load constrained recovery (0.60).** The source says restoration itself was limited by load: throttling or admission limits to protect recovering components, capacity added, traffic reintroduced in stages, or a backlog that slowed recovery. A backlog that was merely drained afterwards does not count.
3. **Restart among the mitigations (0.65).** Restarting, recycling or rebooting servers, processes or services is listed as a mitigation step.
4. **The trigger was a change (0.65).** The triggering cause is a configuration or code change, a deployment, or a certificate or key event, not a hardware fault or a natural capacity exhaustion.
5. **The root lies below Exchange mail flow (0.45).** The component that failed first is a shared layer that Exchange and others depend on (authorization, directory, key or label service, network or storage infrastructure), not Exchange's own mailbox or transport service. *Basis:* Purview authorization, RBAC and Customer Key failures do not obviously go through Exchange.
6. **A gray or alive-but-dead phase (0.45).** The source describes a component that ran, or passed health checks, while failing to serve, or detection that lagged impact because monitoring saw it as healthy.
7. **Actions without reasoning (0.85).** The source records actions and outcomes but names no hypothesis that was considered and rejected during the response.
8. **Repair items on recovery itself (0.70).** At least one stated follow-up concerns how recovery is done (speed, throttling, staged restoration, recovery tooling or isolation), not only preventing the trigger.

## Why this is here
Tupay's tests inject faults but never demand (log, 2026-11-13). Predictions 1, 2 and 8 are about whether recovery was limited by the fault or by the return to load. If they hold, demand at recovery deserves to be a failure-model dimension. If they do not, that is evidence against the blackstart framing for this kind of service.

## Amendment A1 (2026-11-14T03:21Z): informed by a rumor, not by an outcome
**What arrived after registration:** a contact at another company, relayed by Tony, said it "sounds like it was lsass going haywire and keeping cpus pinned, keeping them from even logging in to the affected servers. Nobody's sure yet but that's what I'm hearing." This is hearsay, not a diagnosis. No PIR exists.
**Predictions 1 to 8 are unchanged** and are scored as registered. The new predictions below are scored separately, so that the effect of the rumor can be seen. Their Brier score is reported apart from the first eight.
- **9. lsass, or authentication-process CPU exhaustion, is named as a cause (0.40).**
- **10. The recovery path shared fate with the failure (0.55).** The source says operators' access to the affected servers, or the management or remediation path, was impaired by the failure itself. This is the authority form of the blackstart problem: the means of recovery depends on what has failed.
- **11. Remediation reached the servers by a path that bypassed normal login (0.45):** a reboot or power-cycle from outside, an out-of-band console, or a fleet-wide push that needed no interactive session.

**An ambiguity noted now, before any outcome:** if the first failure is lsass on Exchange's own servers, prediction 5 ("a shared layer below Exchange mail flow, not Exchange's own mailbox or transport service") does not clearly hold or fail. lsass is not Exchange's mail service, but it is not plainly a shared layer either. The text stays as registered. If the case arises, prediction 5 goes to a judge from a non-Claude family, given only the registered text and the source. The steward does not rule on it.
