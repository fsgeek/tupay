# Codex's review of backup contract draft 3 (verbatim, as relayed by Tony, 2026-11-11)

I would return this draft for a focused revision before registration. It contains useful guarantees, but several conflict or permit a backup to pass without demonstrating what you would reasonably expect.

I reviewed draft 3 independently, without reading Qwen's earlier findings. These are findings about the contract's text; I have not tested the implementation.

1. "Faithful" does not require a complete backup. B1.2 requires each included file to be an untorn version that existed during the run. It never explicitly requires every eligible source file to be included. T7a describes the files of the snapshot, so a manifest can faithfully describe an incomplete snapshot. An implementation could omit a directory and still satisfy these sentences. Require completeness against a defined source inventory, with explicit treatment of concurrent creation, deletion, and renaming. The repository's consistent-ref requirement also needs evidence stronger than "every ref resolves": individually valid refs need not represent one simultaneous source state.
   B1.2 and its interpretation (docs/backup/contract-draft-3.md:60)
2. The encryption requirements contradict the verification design. T7b explicitly stores the ciphertext manifest unencrypted; B1.10 requires every stored object at R to be ciphertext. Read literally, both cannot hold. Specify which metadata may remain plaintext and what it may reveal. Separately, matching ciphertext hashes establishes byte preservation; it does not establish that encryption, the key, or the restore procedure works. T11 should not present T8 verification alone as evidence sufficient for restorability.
   Manifest definitions (docs/backup/contract-draft-3.md:29) · B1.10 (docs/backup/contract-draft-3.md:88)
3. There is no defined handling of a restore check that actually fails. T10 defines "restore-checked" as success. B1.8 requires writing "the result," but T15 has no explicit failed-restore result. B1.12 assigns a damaged mark for failed ciphertext verification, which is a different check. Consider ciphertext that remains intact but cannot be decrypted: what mark is written, what notice follows, and may pruning remove the last usable alternative? State that transition directly.
   Status marks (docs/backup/contract-draft-3.md:38) · B1.8 (docs/backup/contract-draft-3.md:83)
4. Several failure effects claim obligations survive when they cannot. Section 5 makes every unlisted pair hold unchanged. Consequently:
   - A crash mid-restore-check must still leave no plaintext when the check ends, although crash cleanup is unspecified.
   - Deleting an acknowledged snapshot violates B1.6's "nothing removes … except pruning," despite BF1.12 explicitly admitting deletion.
   - Suspending the box is documented, but host suspension is not clearly a failure cell with corresponding deadline effects.
   - Loss of S's key is labelled as making B1.9's premise false, although that premise only says the hosts are up, connected, and not full.

   These are repairable by distinguishing service-controlled actions, environmental losses, and availability conditions. The current blanket H makes promises stronger than the exceptions support.
   Failure effects (docs/backup/contract-draft-3.md:146)
5. Status-record recovery is incomplete and can erase obligations. BF1.13 includes loss or corruption at either host, but its effects omit the R-only case. Both-copy loss makes previously acknowledged snapshots "unacknowledged," removing their B1.3 protection until verification happens again—with no recovery deadline. Meanwhile, sequence numbers must only increase, but their recovery after state loss is unspecified. Require durable identity recovery, bounded reconstruction, and preservation of known obligations during reconstruction.
   BF1.13 recovery (docs/backup/contract-draft-3.md:182)
6. Retention and corruption detection do not yet fit together. "Sequence number lies within T … measured by age" mixes two different quantities. More significantly, B1.12 re-verifies only the retained span, while B1.3 covers every acknowledged, unpruned snapshot. An extra snapshot kept outside the required retention set can therefore escape re-verification, yet BF1.3 still promises its corruption is marked within P. Define the retention windows precisely and make the verification population match the protected population.
   B1.4 (docs/backup/contract-draft-3.md:62) · B1.12 (docs/backup/contract-draft-3.md:92)

Two further points matter for your decision:

- The stated 27-hour damage-detection bound is conditional. It assumes another successful run, the shrink threshold being crossed, and an available delivery path. B1.9 supplies no such bound during partitions or full disks. The derived 51-hour retention floor should carry those conditions explicitly.
  Parameters (docs/backup/contract-draft-3.md:209)
- The credential assumption is checked at the wrong boundary. A scan before each push does not cover local commits backed up before any push. Also, "a secrets scan of the kind run" does not identify a reproducible detector. State the detector and ensure the assumption is checked against the material actually entering each backup.
  AI1.5 (docs/backup/contract-draft-3.md:198)

My larger concern is familiar from your Tessera account: the draft asks you to approve machinery before giving you a readily inspectable account of recovery. Its questions for Tony emphasize the notification channel, but a more fundamental question is missing:

> If S disappears tonight, what exactly can I recover, using which surviving materials, and which losses or delays am I accepting?

I would ask Claude to put that answer first, in a short standalone passage. Then resolve the conflicts above against it. That would make your review a decision about the backup service's usefulness, with the identifiers available to substantiate it.
