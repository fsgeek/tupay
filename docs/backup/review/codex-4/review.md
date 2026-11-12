# Codex/ChatGPT's review of backup contract draft 6 (verbatim, as relayed by Tony, 2026-11-12)

I would still hold your clean read. Draft 6 improves the capture policy and execution examples, but one correction substantially weakens the service, and two explicit contradictions remain.

1. The service can now pass while never producing a recoverable backup. B1.1 permits acknowledgement after verification and completeness. B1.8 is satisfied when the restore attempt completes—even if it fails. B1.3 protects only snapshots whose restore check succeeded.

   Consequently, a service that creates complete, hash-matching snapshots that always fail restoration could satisfy these clauses by reporting every failure. There is no obligation to obtain a successfully restore-checked snapshot, repair the failure, or keep its age bounded.

   This resolves the earlier textual conflict by removing a substantive guarantee. My earlier recommendation should have distinguished these more clearly: permitting a failed check to complete the checking obligation must not eliminate the recovery obligation.
   B1.3 (docs/backup/contract-draft-6.md:83) · B1.8 (docs/backup/contract-draft-6.md:107)
2. The accepted capture policy contradicts liveness. B1.17 explicitly accepts that every run fails while a file cannot be captured. B1.9 nevertheless promises a new acknowledged snapshot whenever S and R remain up, connected, and not full. A continuously rewritten source file satisfies that premise while preventing its promised outcome.

   Decide whether capturable sources are a liveness assumption, or whether the service must provide a capture method that meets the guarantee. Reporting the failure does not satisfy the current liveness clause.
   B1.9 (docs/backup/contract-draft-6.md:112) · Capture policy (docs/backup/contract-draft-6.md:132)
3. The status-record reconciliation rule disagrees with its example. B1.18 says snapshot marks follow the copy on the host that wrote them. Restore-check marks are written by the restore host, but the two status copies are on S and R. The execution example instead declares that R's copy wins for a restore-host mark. That authority is not established by the rule. This needs one unambiguous reconciliation policy.
   B1.18 (docs/backup/contract-draft-6.md:136) · Example 5 (docs/backup/contract-draft-6.md:242)

These warrant a small correction, not another broad review cycle. In particular, the first requires a visible policy decision: does this service promise recoverable backups, or verified copies plus reports when recovery fails?

The document's freeze does not settle that decision. Sending it to model authors now could faithfully formalize the weaker service while leaving you to discover the difference during your review.
