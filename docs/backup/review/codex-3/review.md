# Codex's review of backup contract draft 5 and binding-tupay (verbatim, as relayed by Tony, 2026-11-12)

Draft 5 addresses several earlier findings, but still contains obvious conflicts and a new loophole in completeness.

I read draft 5 and its Tupay binding, without consulting the intervening reviews. These are textual findings, not implementation results.

1. A "complete" acknowledged backup may omit changing files indefinitely. B1.17 permits a file to be marked changing after one retry, and B1.1 then permits acknowledgement. A frequently updated file could be absent from every successful backup. There is no bound, escalation, or requirement to retain a recoverable version. That may be an acceptable policy, but it needs explicit approval as permissible data loss—not presentation as completeness.
   B1.17 (docs/backup/contract-draft-5.md:121)
2. Restore success and completion of a failed attempt are still conflated. B1.8 requires every snapshot to be successfully restore-checked; its interpretation permits either success or failure to discharge the obligation. Meanwhile I-B1.3 requires a previous successful restore check, immediately contradicting the permitted window before the first check. Separate "restorable," "successfully demonstrated restorable," and "check completed with failure," and state their obligations consistently.
   B1.8 (docs/backup/contract-draft-5.md:99) · I-B1.3 (docs/backup/contract-draft-5.md:135)
3. Deadline suspension makes overdue detection ambiguous. The class rule restarts deadlines when a required host becomes available again. But the restore-host suspension row says B1.7 fires after M even during suspension. Has the deadline passed or been suspended? Repeated short availability periods could also keep resetting it indefinitely. Define a separate maximum age for an uncompleted check, measured by the available checker, if that is the intended guarantee.
   Class rule (docs/backup/contract-draft-5.md:168) · Suspension exception (docs/backup/contract-draft-5.md:181)
4. Sequence assignment does not deliver its claimed guarantee. Suppose run 42 fails before creating a snapshot. Then S loses its status record; R's latest snapshot is 41. T5a assigns 42 again—even if R's status record still records the failed run. Concurrent runs can also select the same number unless assignment is serialized. "A lost record never reuses a number" is therefore unsupported by the prescribed rule.
   T5a (docs/backup/contract-draft-5.md:36)
5. The failure model includes corrupted status records; recovery handles only lost ones. B1.18 says how to copy a surviving record or rebuild when both are lost. It does not establish how corruption is detected, which copy is trustworthy, or what happens when both exist but disagree. Copying corruption between hosts could destroy the surviving evidence.
   B1.18 (docs/backup/contract-draft-5.md:126)
6. The source inventory promises observations the procedure cannot establish as written. T28 reads paths once at the start. B1.17 then requires the manifest to list paths created during the run, including those left out. A file created and deleted between observations cannot be discovered through that initial inventory. For Git, "ref list" also needs to mean captured names and object IDs, rather than names subsequently resolved at different times. State the intended capture boundary and evidence.
   T28 (docs/backup/contract-draft-5.md:63)

There is also a small but telling residue from the generic split: T20 still defines a source tree as "one of the three parts of T2," although the generic binding can name a different number.

My recommendation: send these back for a bounded correction, with a concrete execution example resolving each finding. Another expansion of the document is unnecessary. Your clean read should be spent deciding whether its recovery guarantees and accepted losses meet your needs—not reconciling conflicting meanings of success, completeness, and deadlines.
