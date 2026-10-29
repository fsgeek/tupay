# D2 judge packet 1 of 5 (findings): Episode's log and recovery, against the sealed analysis

You are a judge. Work only from the text in this packet; do not read files, run commands or search.

Context: a component's log and recovery (`logbuf` in the Episode file system, OSF DCE 1.2.2) relies on contracts from the layers around it. Independent readers enumerated those contracts ("cells"); independent model authors then wrote TLA+ models and reported **findings**: violations of an obligation outside `logbuf` that break a stated guarantee of the log and recovery with the model's defences in place. A separate analysis, done before any of this and sealed, lists bugs, confirmed properties and an open item; it is given to you at the end of this packet, under "The sealed analysis". Items carry opaque ids; you are not told who wrote them. Packets are split by size by a stated rule; this one is part 1 of 5 (findings).

Episode's criteria (fixed by Episode's steward 2026-10-26, before any list existed): a finding is a **match** for a sealed bug if it has the same violated contract, the same mechanism and the same class of effect; **partial** if it has the contract and one of the other two, or the right mechanism under a different contract; **no match** otherwise. A finding that claims a violation contradicting one of the sealed file's confirmed properties is **flagged** (name the property). A finding about the sealed file's open item is **unresolved**. A finding may match several bugs.

For **each finding**, rule against the sealed bugs.

Answer schema: {"findings": [{"id": "F..", "ruling": "match|partial|no match|unresolved", "bugs": ["<sealed bug id>", ...], "flag_confirmed_property": "<property id or null>", "reason": "<two to four sentences>"}]}

Answer with one JSON object only, as specified. Be concrete and brief; cite the sealed file's bug ids and the item's own words. Do not propose fixes. Disagreement with the sealed analysis is allowed: say so in `reason`.

## Findings

### F01
- violated: The log device left one log-page write (page 0) outstanding while it completed enough later log writes for currentLogBlock to wrap round to the same page index, a full lap of the log.
- mechanism: TranCommitted and BufCommitted compare a position against (EarlierPassno(activeLogBlock), activeLogBlock), where activeLogBlock is the oldest page still in transit. When that page has the same index as currentLogBlock, EarlierPassno returns the current pass, so the stalled page looks a lap newer and every record behind it, including pages still in transit, counts as committed. elbl_ForceTran then returns without waiting, so elbt_TranForce(waitOK=1) returns for a transaction whose END page is not on disk. A crash loses that page, and recovery undoes the transaction.
- effect: A transaction whose commit was acknowledged by a forced commit (fsync path) is rolled back by recovery (silent): breaks G7 and G23 (also G29). The same test gates buffer.c Write's log force (G5), but no WAL break was found within the bounds checked (see REPORT.md).
- defence: The model has the activeLogBlock-based commit test, which is the source's defence against out-of-order completion. Without it (D_ALB=FALSE, `mut_noalb`) a forced commit returns before its page lands even in the honest environment. With it in place, the page-offset wrap defeats it.
- confidence: medium — the arithmetic is exactly log.c's TranCommitted/EarlierPassno. It needs one log write to stay outstanding for a full lap: 4 pages in the model, at least 13 pages in a real log (elbl_MinLogSize with 8K blocks).

### F02
- violated: C021
- mechanism: The committed log records b1 changing from 0 to 1, and the home block is already 1. The page recovery reads has a bad checksum, an unknown checksum version, and a body that records the new value 2 together with an end record. ValidLogPageChecksum forces success on UNKNOWN_CKSUM_TYPE (recover.c:2577). The torn page is parsed instead of pulling the head back to the good prefix. Redo installs 2.
- effect: Recovery finishes and writes a metadata value the disk did not commit. Users see block b1 as 2 rather than the committed 1. Breaks G54 and G1.
- defence: The checksum routine is the defence, and it is enabled in this run. The unknown-version branch makes the check succeed and print that the checksum is being ignored. Removing the checksum defence also accepts the torn body (traces/C021-nodefence.txt). A known bad checksum is pulled back; this cell is the fail-open version.
- confidence: high — the trace ends recovered b1=2, oracle b1=1, cksum bad, version unknown, and the honest replay of the real log keeps 1.

### F03
- violated: The log device completed a later write of a freshly opened log (page 1) before its first write (page 0, which overwrites the restart block), and the machine crashed in between; log.c ForceMap explicitly allows this ("We don't assume in-order writes").
- mechanism: Page 0 still holds the restart record, so elbl_InitLog (elbr_GetCleanLogInfo) treats the log as clean, skips recovery, and reopens it with passno = IncPassno(restart pass), the same pass the crashed incarnation used, so the stale page 1 cannot be told apart from the new incarnation's pages. After a second crash SafeDumpLog's binary search takes the stale page as head, its io_window and pass-number checks pass because page 0 now holds a new page with the same pass, and the stale records join the active log. MarkCommitted matches records by tran id alone and tran ids restart at 0xfffffff6 on every boot, so the stale END of boot-1 tran 1 marks boot-2 tran 1's uncommitted update REDO.
- effect: Recovery reports success but metadata now holds an update of a transaction that never ended (silent): breaks G3 and G8 (also G1, G2). The same mechanism can instead make recovery abort with RCVR_ASSERT on records left UNDEF (G55/G58; `model/results/v3/f1_fail.out`).
- defence: The model has the pass-number fence between log incarnations (IncPassno at open, +2 after recovery), the in-transit io_window check and the per-page pass check. The fence fails because two incarnations get the same pass when no recovery ran between them. The io_window check, which would catch the missing page 0, never runs because the log looks clean. Removing the fence (D_INC=FALSE) lets stale pages join a log with no environment deviation at all (`mut_noinc` fails). Removing D_IOW, D_PASS or D_BUMP leaves this run unchanged (`f1_noIOW`, `f1_noPASS`, `f1_noBUMP` fail the same way).
- confidence: medium — each step follows a source line (log.c elbl_InitLog, recover.c SafeDumpLog/MarkCommitted, tran.c elbt_GlobalTranId), but it needs out-of-order completion among the first pages after a mount, then a second crash before those pages are overwritten.

### F04
- violated: C024
- mechanism: Transaction t1 commits an update of b1 from 0 to 1. The home block is still 0 because the dirty buffer is holding the redo in the active log. Transaction t2 then logs an update and does not commit. elbb_Kill with metadataOK true drops t1's buffer, and the active log that recovery sees no longer contains t1's redo (the model replaces that log with t2's record, which is the checkpoint moving past a buffer that left the age queue). Crash undoes t2 and has nothing to redo for t1, so b1 stays 0.
- effect: A committed metadata update is gone after the crash, while the uncommitted follower is undone. A later free can look committed in memory and then abort, resurrecting or dropping the block the committed transaction described. Breaks G7, G21, and G22.
- defence: elbb_Kill returns BUF_CANTDELETE only when metadataOK is false and the buffer is logged and dirty (buffer.c:1395). That boolean is the defence. It does not look at whether the freeing transaction's end record is durable. block_alloc.c:450 passes metadataOK true. The defence-removed run breaks the same way (traces/C024-nodefence.txt) because the true flag never consulted the commit record.
- confidence: high — the trace ends recovered b1=0 and oracle b1=1 after the kill replaces the log, and the honest run keeps t1's redo.

### F05
- author_status: draft
- violated: C088
- mechanism: A completed, acknowledged log page at the head of the active log is overwritten (no magic, bad checksum). Recovery's binary search does not check magic on the endpoints, finds that page as head, and the in-transit window scan (recover.c:940-975) treats the checksum failure as an incomplete write, moving the head to the previous page. The committed transaction's END is discarded and its records are undone (or simply not redone), with no error.
- effect: a transaction fsync/LogForce reported as committed is silently lost after recovery; G7, G23 (Inv_Durable).
- defence: checksums (ValidLogPageChecksum) and pass numbers detect the damage, but the head-window rule converts detected damage into "not yet written" instead of failing; only damage outside the window raises RCVR_IOERR.
- confidence: medium — mechanism follows the source line by line; the overwrite must hit the newest pages before the crash.

### F06
- violated: C018
- mechanism: The committed log is an update of b1 from 0 to 1 plus an end record, and the home block is already 1. The read of the head returns the previous well-formed page, which contains the update and not the end. Pass number and checksum both accept that page. Recovery classifies the transaction as undo, because it sees no end, and writes the old value 0 back over the committed home block.
- effect: A committed metadata update is undone after a stale read of the log head. Users see the pre-transaction value of b1. Breaks G7.
- defence: SafeDumpLog checks the checksum and the pass number of the page it read (recover.c:933 and the active-page pass check). Both succeed for an older well-formed page. They do not detect that the end record was on the page the device should have returned. The defence-removed run undoes the same committed value (traces/C018-nodefence.txt).
- confidence: high — the trace ends recovered b1=0 and oracle b1=1, with the seen log containing only the update, and the honest run replays the end record and keeps 1.

### F07
- violated: The log device kept one write (page 1) outstanding while it completed a later one (page 2, holding a transaction's END), and the machine crashed. Then a second crash (or a failed restart write followed by a rerun of recovery) interrupted elbr_Recover after elbr_WriteCheckpointBlock and before elbr_WriteRestartBlock.
- mechanism: The first recovery's head search stops at the hole and correctly undoes the transaction. It then writes its checkpoint block at head+1, which is the hole, with the same pass number and a valid checksum. On the next recovery the binary search therefore reaches the stale page 2 as head, and its io_window check sees only the valid checkpoint page. The transaction whose END is on page 2 is marked REDO even though its middle record (on the lost page 1) is gone, so only part of it is redone, reversing the first recovery's decision.
- effect: After a successful recovery a transaction is partly applied, and an abort decided by one recovery is undone by the next (silent): breaks G2 and G6/G8 (also G1).
- defence: The model has recover.c's checkpoint-before-restart block ("the checkpoint block itself becomes the entire active region of the log") plus the head search (binary search, io_window, pass checks). Removing the checkpoint write (D_CKPT=FALSE, `f2_noCKPT`) removes every violation at the same bounds, so the checkpoint write is what turns a tolerated hole into corruption. Removing D_IOW does not change this run (`f2_noIOW`), because at N=4 the binary search, not the io_window check, stops at the hole.
- confidence: medium — direct consequence of recover.c step 5 and SafeDumpLog; needs two independent events (a hole at the first crash, then an interruption inside recovery's two-write window).

### F08
- violated: C041
- mechanism: The update of b1 is logged in memory and the log force is the next step. On AIX, asevent_Iodone clears ESOFT, b_resid, and B_ERROR before the log looks at the event (asevent.c:1070). The force is therefore reported successful while the log page was not stored. Write-ahead then allows the home write, so disk b1 becomes 1. No end record is durable, so the committed image is still the old value. Crash sees an empty log and leaves b1 at 1.
- effect: A metadata write that the file system treated as logged is on disk, and the log that should undo it is not. After the crash users see the uncommitted value. Breaks G5 and G29.
- defence: The log's check of the I/O status is the defence. It never observes ESOFT, because the async layer cleared the error first. With that check removed the same home block is still published (traces/C041-nodefence.txt).
- confidence: high — the trace ends with an empty log, recovered b1=1, and oracle b1=0, and the honest force keeps the log record ahead of the home write.

### F09
- violated: C058
- mechanism: An uncommitted update of block b1 from 0 to 1 is logged and its home block is written. The environment then plants a restart image on the first log block. elbr_GetCleanLogInfo (recover.c:2813 and recover.c:2840) treats salvage magic plus a first record of type restart as a clean log, and it does not checksum that page (recover.c:2826 and recover.c:2737). Replay never runs. The home block stays 1.
- effect: After the crash the aggregate mounts as a clean log. Users see metadata the transaction did not commit. Breaks G56, G58, G8, and G1.
- defence: The clean test is the defence, and a well-formed restart is what it accepts. elbr_InitLogPageHdr already puts the salvage magic on every page, and the restart page is deliberately not checksummed, so a restored or forged restart is indistinguishable from a finished recovery. Removing the magic check does not help: the clean path is taken because the image looks like a restart, which traces/C058-nodefence.txt also shows.
- confidence: high — the trace ends recovered b1=1, oracle b1=0, with fake restart set, and the honest run of the same uncommitted image undoes it.

### F10
- author_status: draft
- violated: C071
- mechanism: Bits of a completed head log page decay (checksum fails, header intact). Recovery finds it as head by pass number; the in-transit scan (index 0 is the head itself) sees the bad checksum and pulls the head back one page, so the END of an acknowledged transaction is dropped and its updates are undone or not redone.
- effect: acknowledged commits silently disappear; G7, G23.
- defence: checksums detect the decay, but within the io_window range a bad page is taken to be an in-flight write and silently truncated.
- confidence: medium — same mechanism as F-draft-1.

## Cells named by a finding

### C018
- contract: A later read of a block must return, sector by sector, the data of the last write to that sector that the driver has reported complete.
- source: logbuf/recover.c:892 " * We trust the log to make sure it doesn't assume a page with"
- violation: A drive cache, a multipath disk, or a host buffer returns a stale copy after a completed write, so recovery or the next mount sees an older log page.
- at-risk: G54 and G7 fail because the head, the pass number, or the redo records recovery reads are not the ones the running system forced.
- detectable: partly — a stale page often fails the pass-number or checksum test, and an older but well-formed page can be mistaken for the head.
- silent: 2 — coherent SCSI disks usually read what they just wrote, but stale cache and multipath windows are an occasional field failure.

### C021
- contract: Administrators must select a supported effective checksum scheme when relying on torn-page or corruption detection.
- source: logbuf/recover.c:2582 "printf("Log has unknown checksum type on disk. Ignoring checksum check\n");"
- violation: A log uses checksum version NONE or an unknown type and the deployment assumes every torn page will be rejected.
- at-risk: G54 and G1: unchecked damaged pages can enter head selection or replay; checksumming is conditional on configuration.
- detectable: partly — the version is inspectable and an unknown version emits a warning; version NONE can operate without an error.
- silent: 2 — Legacy configurations can silently lack the protection expected of newer logs.

- contract: Provisioning must select a working supported checksum format when relying on detection of partial log-page writes.
- source: logbuf/recover.c:2445 " case LOGREC_CKSUMVER_NONE:"
- violation: An aggregate uses the no-checksum format yet expects a partly written multi-sector page to be detected.
- at-risk: G54, G1: sector atomicity alone does not establish completeness of the remaining sectors.
- detectable: partly — checksum mode is inspectable, but damage cannot be checked without redundancy.
- silent: 1 — No-checksum operation can conceal torn pages, but the incidence depends on configuration and crash timing.

- contract: The checksum version recorded on the log must be a version recovery knows, so torn pages are rejected rather than ignored.
- source: logbuf/recover.c:2578 " /* Unknown checksum type recorded on disk. Force success of"
- violation: An operator or patchlog sets an unknown checksum version, and recovery then treats every page checksum as valid.
- at-risk: G54 fails because a torn or out-of-order log page in the in-transit window is accepted as the head, and replay proceeds from a page the disk did not finish writing.
- detectable: partly — recovery prints that it is ignoring the checksum, but it still returns success if the rest of the log parses.
- silent: 1 — logs are created with the CRC-32 version, and changing that version is a rare manual act.

- contract: The checksum version stored in the log is one this recovery code implements.
- source: logbuf/recover.c:2578 " /* Unknown checksum type recorded on disk. Force success of"
- violation: A newer or older creator writes a checksum version the running salvager does not know.
- at-risk: G54 fails open: an unknown version forces the checksum check to succeed, so a torn or corrupt page is replayed.
- detectable: partly — recovery prints that it is ignoring the checksum, and then continues.
- silent: 1 — matching kernel and salvager binaries are the normal deployment, and a mismatch is rare over a year.

### C024
- contract: Callers may set metadataOK on Kill only after the transaction freeing that metadata has committed.
- source: logbuf/buffer.c:1359 "PARAMETERS -- metadataOK is true if it is safe to kill dirty metadata"
- violation: An allocator passes metadataOK=1 merely because a free was issued, before that free commits.
- at-risk: G21, G22, G44: discarding the dirty buffer can retire the only committed state still needed if the free is undone.
- detectable: partly — a transaction-aware allocator can verify the freeing commit, but Kill receives only the caller’s boolean.
- silent: 2 — A false safety assertion can silently bypass the discard protection.

- contract: A caller may authorize killing dirty metadata only after the freeing transaction and all prior modifiers have committed.
- source: logbuf/buffer.c:1370 " * buffers. This will only be true if the transaction that freed the"
- violation: An allocator passes metadataOK=true before its freeing transaction commits.
- at-risk: G44, G6: the only dirty copy can be discarded while rollback still needs it.
- detectable: partly — false metadataOK is checked, but a dishonest true is trusted.
- silent: 1 — A false kill authorization requires a caller defect and may remain hidden until rollback is needed.

- contract: Callers must pass metadataOK to elbb_Kill only after the transaction that freed that metadata block has committed, which is also after every transaction that modified the block has committed.
- source: logbuf/buffer.c:1359 " * PARAMETERS -- metadataOK is true if it is safe to kill dirty metadata"
- violation: The allocator kills a dirty logged buffer before the freeing transaction's end record is on disk, so the buffer leaves the age queue while its updates exist only in the log or are still uncommitted.
- at-risk: G21 and G22 fail because checkpointing drops the log tail when no dirty buffer still pins it, and killing the buffer early discards committed updates that were not yet on their home blocks.
- detectable: no — with metadataOK set, the kill succeeds and returns zero.
- silent: 1 — the freed-block list kills metadata only after TranIsCommitted returns true, so a premature kill in ordinary operation is rare.

- contract: A caller passes metadataOK to elbb_Kill only after the transaction that freed that metadata block has committed.
- source: logbuf/buffer.c:1360 " * buffers. This will only be true if the transaction that freed the"
- violation: The allocator kills a dirty logged buffer while the freeing transaction is still uncommitted, and the buffer's updates disappear from memory.
- at-risk: G44 and G6 fail because recovery may still undo other records on that block while the killed dirty image has already been discarded, and a reuse can then proceed without the committed free.
- detectable: partly — elbb_Kill returns BUF_CANTDELETE when metadataOK is false and the buffer is dirty; a true flag on an uncommitted free is accepted.
- silent: 1 — fb_CheckTrans kills only after elbb_TranIsCommitted, so a premature kill is a rare caller bug.

### C041
- contract: On AIX, an I/O completion reported as ESOFT must mean the transfer finished and is durable, because the async layer clears that error and treats the buffer as successful.
- source: async/asevent.c:1070 " if (bp->b_error == ESOFT) {"
- violation: The AIX driver returns ESOFT for a write that was not stored, and Episode clears the error and continues as if the log page or metadata block were on disk.
- at-risk: G5 and G29 fail for the same reason as a false success: the log force returns, and a later crash finds the page missing.
- detectable: no — the error is deliberately discarded before the log package sees it.
- silent: 2 — recovered soft errors are normal on AIX and are harmless, but an ESOFT that does not mean the data was stored happens on real adapters often enough to be occasional.

- contract: The driver reports a transfer that did not finish as a hard error, and the async layer is entitled to treat any other completion as success.
- source: async/asevent.c:1070 " if (bp->b_error == ESOFT) {"
- violation: AIX returns ESOFT for a write that did not reach stable media, and asevent_Iodone clears b_error and B_ERROR before the log inspects the event.
- at-risk: G5 and G29 fail because a log force or a metadata write is treated as committed when the transfer was only partial.
- detectable: no — the error is cleared inside the async layer before CheckIOError runs.
- silent: 2 — this path exists only on AIX, and drivers return ESOFT for an incomplete durable write only on some media faults.

### C058
- contract: The storage and operating environment must preserve a clean restart marker’s authenticity and its ordering after all recovery or shutdown data writes.
- source: logbuf/recover.c:2738 "We choose not to checksum the log page containing a restart record"
- violation: A forged, corrupted, restored, or prematurely durable restart marker survives while recovered metadata writes do not.
- at-risk: G39, G55, G56: a plausible restart record can suppress necessary recovery because it is not checksummed.
- detectable: partly — header and record checks catch malformed markers, but not a plausible stale or wrongly ordered clean marker.
- silent: 1 — Normal synchronous durable I/O preserves this order; silent violation is rare.

- contract: The restart page, which recovery does not checksum, must keep the exact header and restart record written by log creation, clean shutdown, or a finished recovery.
- source: logbuf/recover.c:2738 " * We choose not to checksum the log page containing a restart record"
- violation: Bit rot or a torn write leaves the salvage magic and a restart record type in the first log block of a log that still has an active tail, or destroys a genuine restart record.
- at-risk: G56 and G58 fail because a dirty log is treated as clean and ordinary operation starts without replay, or a clean log is treated as dirty and recovery rewrites metadata from an old tail.
- detectable: no — the clean test looks only for the magic and a restart record, not a checksum.
- silent: 1 — one block is rewritten at shutdown and recovery, and an undetected flip of that pattern is rare.

- contract: Operators and tools must not write a restart record, or otherwise mark the log clean, except by log creation, a clean shutdown, or a recovery that has finished applying updates.
- source: logbuf/recover.c:2738 " * We choose not to checksum the log page containing a restart record"
- violation: patchlog or an operator copies a restart record onto the first log block of a dirty aggregate to make it mount, without replaying the tail.
- at-risk: G56 and G1 fail because attach treats the log as clean and serves metadata that still contains uncommitted updates and is missing committed ones.
- detectable: no — a well-formed restart record is the definition of a clean log.
- silent: 1 — normal operation does not rewrite the restart block by hand, and doing so is a rare administrative act.

### C071
- contract: The storage stack must preserve completed writes until an explicitly authorized overwrite.
- source: logbuf/recover.c:755 "active log pages outside the in-transit window are really"
- violation: A completed active log page later develops an unreadable sector or silently loses bits.
- at-risk: G1, G6, G7, G20: the only surviving undo or redo image may be lost.
- detectable: partly — supported checksums detect many corruptions, but cannot reconstruct lost records.
- silent: 1 — Latent media damage without a reported error is rare but possible.

- contract: The device must preserve completed home-block writes until a later authorized overwrite.
- source: logbuf/recover.c:1354 " writeBlock(&buf, returnVal);"
- violation: A controller loses an acknowledged recovered block after a clean restart record is written.
- at-risk: G55, G1: recovery is declared complete although its repairs are missing.
- detectable: no — successful completion does not expose later loss.
- silent: 1 — Loss of previously completed home writes is an exceptional hardware failure and often produces later visible damage.

- contract: Until Episode overwrites a block, the device returns the bytes of the last completed write to that block, or it returns an I/O error.
- source: logbuf/recover.c:756 " * expected to be on disk correctly. If checksum errors are"
- violation: A later media error, a misdirected write, or a dropped sector changes a log page or a metadata block that recovery still needs, and the read succeeds with different bytes.
- at-risk: G6, G7, and G1 fail; a corrupted log page outside the in-transit window aborts recovery, and a corrupted metadata home block is applied as if it were the image the log expected.
- detectable: partly — log pages are checksummed and a bad page raises RCVR_IOERR; metadata home blocks have no checksum, so a wrong image is accepted.
- silent: 1 — silent bit rot or a misdirected write over a year on these SCSI disks is rare, and a checksum failure is visible when it hits a log page.

### C088
- contract: The allocator and administrator must reserve log blocks exclusively and keep their addresses and log length fixed during normal logging.
- source: §"Data Architecture" "The log container does not grow or shrink"
- violation: A live resize, relocation, or overlapping allocation lets file data overwrite active log pages.
- at-risk: G20, G21, G54: retained history and circular page numbering cease to describe persistent storage.
- detectable: partly — checksum and page-number failures may reveal damage, after recovery information is already lost.
- silent: 1 — The source’s normal initialization and allocation rules avoid live log resizing.

- contract: The aggregate layer must keep the log allocation and address map fixed while logging is attached.
- source: logbuf/log.c:697 " IN daddr_t *logLocnArray,"
- violation: An online resize or relocation changes log blocks without a coordinated log replacement.
- at-risk: G7, G54: recovery and logging disagree about where retained records reside.
- detectable: partly — malformed page sequences may be found; no relocation protocol is supplied here.
- silent: 1 — Normal operation deliberately does not resize the log; unsupported live changes are rare.

- contract: The log container must not grow or shrink while the aggregate is in use.
- source: §"Data Architecture" "do not, in the current implementation, change dynamically. The log container does not grow or shrink"
- violation: An operator or a later tool extends or truncates the log container while transactions are running, so the in-memory location array and the pass numbers no longer describe the disk.
- at-risk: G17 and G9 fail because admission control and recovery both assume a fixed circular buffer, and a resized log can wrap onto live records or drop the tail.
- detectable: partly — a size mismatch at the next attach is rejected, but a resize under a live kernel is not checked on each write.
- silent: 1 — the implementation provides no working resize of the log, so a deployment run as described does not change it.

- contract: The operator gives the aggregate a log at least as large as the minimum for its workload, and leaves that container's size and block list fixed while the aggregate exists.
- source: §"Data Architecture" "The log container does not grow or shrink"
- violation: newaggr creates a log smaller than elbl_MinLogSize, or an administrator grows, shrinks, or relocates the log container under a live aggregate.
- at-risk: G17 and G28 fail because elbl_InitLog returns LOG_LOGFULL, or a resized log moves the blocks whose pass numbers recovery uses to find the head.
- detectable: yes — an undersized log is rejected at init; a resized live log is not checked again and shows up later as a bad pass or a failed recovery.
- silent: 2 — the creation check is visible, while an offline rewrite of the log container is an occasional administrative mistake and is silent until the next crash.

## GUARANTEES.md (the guarantees findings cite as G<n>)
# GUARANTEES.md: what the log and recovery guarantee

Extracted from the paper and the source by two readers independently; kept where both found the same guarantee. Each guarantee is given as each reader stated it, unedited.

### G1
- guarantee: After a crash and successful recovery, file-system metadata, including directories, allocation bitmaps, indirect blocks, and anode tables, is consistent.
  source: §"Background" "guarantee that after a crash, the le system meta-data (directories, allocation bitmaps, indirect blocks and anode tables) are consistent, generally eliminating the need for running \fsck.""
- guarantee: After a crash, file-system meta-data (directories, allocation bitmaps, indirect blocks, and anode tables) are consistent.
  source: §"Background" "guarantee that after a crash, the le system meta-data (directories, allocation bitmaps, indirect blocks and"

### G2
- guarantee: A committed metadata transaction applies all its updates atomically.
  source: §"Component Architecture" "that either all the updates within a transaction (if a transaction commits), or none of them (if a transaction aborts), will be applied."
- guarantee: All meta-data updates are grouped into atomic transactions: if a transaction commits, every update in it is applied; if it aborts, none is applied.
  source: §"Component Architecture" "that either all the updates within a transaction (if a transaction commits), or none of them (if a transaction"

### G3
- guarantee: An aborted metadata transaction leaves none of its updates applied.
  source: §"Component Architecture" "that either all the updates within a transaction (if a transaction commits), or none of them (if a transaction aborts), will be applied."
- guarantee: All meta-data updates are grouped into atomic transactions: if a transaction commits, every update in it is applied; if it aborts, none is applied.
  source: §"Component Architecture" "that either all the updates within a transaction (if a transaction commits), or none of them (if a transaction"

### G4
- guarantee: For every metadata update, logging records both the original and new values.
  source: §"Component Architecture" "value logging techniques [MOH 89]. In a nutshell, this form of logging works by logging, for every update made to any le system meta-data, both the original and new values of the updated data."
- guarantee: For every update to file-system meta-data, the log stores both the original value and the new value of the updated data.
  source: §"Component Architecture" "made to any le system meta-data, both the original and new values of the updated data. Furthermore,"

### G5
- guarantee: Before writing a dirty metadata buffer to its home disk location, the buffer package writes the corresponding log entries to disk.
  source: §"Component Architecture" "before the bu er package allows any dirty meta-data bu er to be written back out to the disk, it writes out these log entries to the disk."
- guarantee: Before the buffer package writes any dirty meta-data buffer back to disk, it writes that buffer's log entries to disk.
  source: §"Component Architecture" "before the bu er package allows any dirty meta-data bu er to be written back out to the disk, it writes"
- guarantee: Before a dirty buffer on the log age queue is written, the log is forced at least through that buffer's last log record.
  source: logbuf/buffer.c:3769 " /* maybe force write log */"

### G6
- guarantee: Recovery restores aborted metadata updates to their values before the transaction began.
  source: §"Component Architecture" "the log to undo all of the updates made to the meta-data, and restore the meta-data to its state before the transaction started."
- guarantee: If a transaction aborted, the log contains enough information to undo all of its meta-data updates and restore the meta-data to its state before the transaction started.
  source: §"Component Architecture" "the log to undo all of the updates made to the meta-data, and restore the meta-data to its state before the"

### G7
- guarantee: Recovery redoes committed metadata updates even when their buffers had not reached disk before the crash.
  source: §"Component Architecture" "transaction started. If the transaction committed, there is enough information in the log to redo all of the meta-data updates, even those that hadn't yet made it from the disk bu ers to the disk."
- guarantee: If a transaction committed, the log contains enough information to redo all of its meta-data updates, including those that had not yet reached disk from the buffers.
  source: §"Component Architecture" "meta-data updates, even those that hadn't yet made it from the disk bu ers to the disk."

### G8
- guarantee: Recovery undoes transactions that were uncommitted at the crash.
  source: §"Component Architecture" "The recovery procedure runs after a crash, replaying the committed transactions and undoing the uncommitted transactions, and thus restoring the le system to a consistent state."
- guarantee: After a crash, recovery replays committed transactions and undoes uncommitted transactions, restoring the file system to a consistent state.
  source: §"Component Architecture" "uncommitted transactions, and thus restoring the le system to a consistent state. Since the log only"

### G9
- guarantee: The paper initially promises recovery time proportional to activity at the crash rather than disk size, subject to its later qualification about uncheckpointed committed transactions.
  source: §"Component Architecture" "contains information describing transactions still in progress, recovery time is proportional to the activity at the time of the crash, not to the size of the disk."
- guarantee: The log contains only information describing transactions still in progress, so recovery time is proportional to activity at the time of the crash and not to disk size.
  source: §"Component Architecture" "contains information describing transactions still in progress, recovery time is proportional to the activity"

### G10
- guarantee: The paper initially promises recovery time proportional to activity at the crash rather than disk size, subject to its later qualification about uncheckpointed committed transactions.
  source: §"Component Architecture" "contains information describing transactions still in progress, recovery time is proportional to the activity at the time of the crash, not to the size of the disk."
- guarantee: Recovery takes essentially the same amount of time on small and large aggregates.
  source: §"Recovery Time" "From this data, we can see that recovery takes essentially the same amount of time on"
- guarantee: Recovery time does not depend on aggregate size.
  source: §"Recovery Time" "none of which, however, are the aggregate size. Despite this complexity, it also appears that in typical"

### G11
- guarantee: The paper claims log replay runs orders of magnitude faster than BSD fsck.
  source: §"Component Architecture" "of magnitude faster than the BSD fsck program."
- guarantee: Replaying the log runs orders of magnitude faster than BSD fsck.
  source: §"Component Architecture" "at the time of the crash, not to the size of the disk. The result is that the log-replaying operation runs orders"

### G12
- guarantee: Transactions may release transactional locks before the end of the transaction.
  source: §"Logging Architecture" "tional locking instead of two-phase locking. Episode transactions can acquire locks when they need them, and drop them as soon as they are nished using them, rather than waiting for the transaction's end."
- guarantee: A transaction may acquire a lock when it needs it and drop the lock as soon as it has finished using the object, without waiting for the transaction to end.
  source: §"Logging Architecture" "and drop them as soon as they are nished using them, rather than waiting for the transaction's end. This"

### G13
- guarantee: All transactions in an equivalence class commit together or none commit.
  source: §"Logging Architecture" "either all of its transactions commit or none do.3 In the example above, transaction 1 and 2 would form"
- guarantee: Either every transaction in an equivalence class commits, or none of them does.
  source: §"Logging Architecture" "either all of its transactions commit or none do.3 In the example above, transaction 1 and 2 would form"

### G14
- guarantee: A crash before all transactions in an equivalence class have committed aborts every transaction in that class.
  source: §"Logging Architecture" "If the system crashes before all of the transactions in an EC have committed, all the transactions in the EC are aborted."
- guarantee: If a crash intervenes, Episode aborts transactions that might otherwise have been able to commit, rather than letting another transaction make uncommitted data permanent.
  source: §"Logging Architecture" "have otherwise been able to commit, if a crash intervenes. Speci cally, all active transactions that lock the"
- guarantee: If the system crashes before every transaction in an equivalence class has committed, every transaction in that class is aborted.
  source: §"Logging Architecture" "the EC are aborted. It is therefore desirable to minimize the duration and the number of ECs formed in the"

### G15
- guarantee: An explicit synchronization request such as fsync prevents the requested metadata persistence from being indefinitely deferred.
  source: §"Logging Architecture" "Meta-data changes to the disk itself can often be deferred, unless speci cally requested by an oper- ation like fsync. Consistency of the le system doesn't require that the system be current."
- guarantee: Meta-data changes to disk may be deferred unless an operation such as fsync requests otherwise.
  source: §"Logging Architecture" "Meta-data changes to the disk itself can often be deferred, unless speci cally requested by an oper-"

### G16
- guarantee: When a newly allocated data block has an incomplete first-write transaction at a crash, recovery zeroes the block.
  source: §"Logging Architecture" "to it completes. If the system crashes and the transaction aborts, the recovery procedure for this special transaction zeroes the contents of the block."
- guarantee: If a crash occurs after a block is allocated to a file and before the first write to that block, and the special allocation transaction aborts, recovery zeroes the contents of the block.
  source: §"Logging Architecture" "transaction zeroes the contents of the block."

### G17
- guarantee: Log-space admission control keeps running transactions within the available log space.
  source: §"Logging Architecture" "when they begin. This allows the use of a very simple algorithm to ensure that running transactions never exceed the space available in the log."
- guarantee: Transaction sizes are bounded when they begin, and running transactions never exceed the space available in the log.
  source: §"Logging Architecture" "exceed the space available in the log. Transactions that run too long or modify too much data represent"

### G18
- guarantee: Dirty metadata buffers may be written before their transactions end.
  source: §"Logging Architecture" "when to write these bu ers. Old value / new value logging, on the other hand de-couples the writing of bu ers from the end of transactions, at the expense of having to write more data to the log."
- guarantee: Because the log holds old and new values, a dirty meta-data buffer may be written to its home on disk before its transaction commits.
  source: §"Logging Architecture" "bu ers from the end of transactions, at the expense of having to write more data to the log."

### G19
- guarantee: Each transaction in a multi-transaction filesystem operation leaves the filesystem consistent, even if the overall operation is unfinished.
  source: §"Logging Architecture" "operations, followed by a deletion of the empty le. After each transaction, the le system is consistent, if not in the nal desired state."
- guarantee: After each bounded transaction that makes up a larger operation, the file system is consistent, even if it is not yet in the final desired state.
  source: §"Logging Architecture" "not in the nal desired state."

### G20
- guarantee: The active log retains uncommitted transactions needed for crash undo.
  source: §"Recovery Time" "active portion of the log is that part of the log that needs to be replayed after a crash, and must include all of the uncommitted transactions, since these must be undone in the event of a crash."
- guarantee: The active portion of the log includes all uncommitted transactions, which must be undone after a crash.
  source: §"Recovery Time" "of the uncommitted transactions, since these must be undone in the event of a crash. The active portion"

### G21
- guarantee: The active log also retains committed updates whose metadata buffers remain dirty, qualifying the earlier claim that recovery depends only on in-progress transactions.
  source: §"Recovery Time" "of the log may go back even further, should the bu er cache still contain dirty meta-data blocks that were modi ed by committed transactions."
- guarantee: The active portion of the log also includes committed updates whose dirty meta-data blocks still reside only in the buffer cache.
  source: §"Recovery Time" "modi ed by committed transactions. In this case, the updates are in the log and only in the log, requiring"

### G22
- guarantee: Checkpointing discards committed log history only after writing the buffers required to preserve those transactions.
  source: §"Recovery Time" "the replay of that part of the log in the event of a crash. The operation of writing bu ers modi ed by committed transactions and discarding those portions no longer required to ensure the permanence of those"
- guarantee: Checkpointing writes buffers modified by committed transactions and discards those log portions no longer required to make those transactions permanent.
  source: §"Recovery Time" "transactions is generally called checkpointing the log."

### G23
- guarantee: elbb_LogForce with waitOK one returns only after the transaction has committed, making its updates persistent.
  source: logbuf/tran.c:950 " * 1 -- don't return until transaction has committed. This guarantees * persistence for updated done under this transaction. "fsync" is the"
- guarantee: elbb_LogForce with waitOK 1 does not return until the transaction has committed, which makes updates done under that transaction persistent.
  source: logbuf/tran.c:950 " * 1 -- don't return until transaction has committed. This guarantees"

### G24
- guarantee: elbb_LogForce with waitOK two waits for completion and serializes the transaction with transactions begun after the call returns.
  source: logbuf/tran.c:953 " * 2 -- don't return until transaction has completed. This ensures * serialization of this transaction with respect to any transactions"
- guarantee: elbb_LogForce with waitOK 2 does not return until the transaction has completed, which serializes it with any transaction started after the call returns.
  source: logbuf/tran.c:953 " * 2 -- don't return until transaction has completed. This ensures"

### G25
- guarantee: Ending a transaction in an unfinished equivalence class may leave it pending rather than committed.
  source: logbuf/tran.c:426 " * elbt_EndTran -- handle changing the state of a transaction from active to * complete or pending (EC)."
- guarantee: Until the last member of an equivalence class ends, every earlier member is only pending and has no END record on disk.
  source: logbuf/tran.c:447 " /* This tran is part of an EC but we are not the last. Just mark"

### G26
- guarantee: An equivalence class writes all member batch-end records before writing its final head end record.
  source: logbuf/tran.c:795 " * We won't write the end record out for the final transaction until * after all the batch end records have been written out."
- guarantee: Equivalence-class ends are written atomically: the head transaction writes a BEND record for each member and then its own END, and recovery reconstitutes those member END records only if the head transaction is REDO.
  source: logbuf/recover.c:1687 " * Bulk ends are the recovery end of ECs. Because the end records must"

### G27
- guarantee: Starting a transaction with an old transaction ID does not block waiting for other transactions to complete.
  source: logbuf/buffer.c:1739 " * By providing an old transaction ID, this call will not block. If there * is no transaction ID, this call might wait pending completion of other"
- guarantee: Starting a transaction with a non-null oldTranId starts a nested transaction and does not block waiting for log space.
  source: logbuf/buffer.c:1739 " * By providing an old transaction ID, this call will not block. If there"

### G28
- guarantee: When transaction allocation fails because of log pressure, elbb_StartTran handles the full log and retries.
  source: logbuf/buffer.c:1743 " * If this routine fails to allocate a transaction we presume it is because * the log is full and so we invoke the log full handling and try again."
- guarantee: elbb_StartTran without an old transaction retries, including log-full handling, until it obtains a transaction (except during a bounded kernel-panic loop).
  source: logbuf/buffer.c:1743 " * If this routine fails to allocate a transaction we presume it is because"

### G29
- guarantee: A transaction is not treated as durably committed merely because its end record has been constructed in memory.
  source: logbuf/log.c:140 " * The transactions on the cTranList are being held until their end records are * actually committed to disk. Then they are returned to the tran module when"
- guarantee: A transaction is committed only once its last log record has been written to disk, not merely when the transaction has ended in memory.
  source: logbuf/log.c:2259 " * elbl_IsTranCommitted -- check to see if the last record of this transaction"
- guarantee: Completed transactions are held until their end records are committed to disk, and only then are they garbage-collected.
  source: logbuf/log.c:140 " * The transactions on the cTranList are being held until their end records are"

### G30
- guarantee: elbl_ForceBuffer forces the log to disk through the specified buffer's last update.
  source: logbuf/log.c:2108 " * elbl_ForceBuffer -- force the log to disk up to the specified buffer's * last update."
- guarantee: After that log force, elbl_ForceBuffer has made the buffer's log records committed on disk.
  source: logbuf/log.c:2125 " afsl_Assert (BufCommitted (lmP, bP));"

### G31
- guarantee: elbb_Release with elbb_sync returns after both the necessary log and the data buffer have been written.
  source: logbuf/logbuf.p.h:66 " elbb_sync, /* force write log, force write data buffer, upon return * both log and data buffer have been written */"
- guarantee: elbb_Release with elbb_sync does not return until the log (if needed) and the data buffer have both been written.
  source: logbuf/logbuf.p.h:66 " elbb_sync, /* force write log, force write data buffer, upon return"

### G32
- guarantee: elbb_QuiesceSystem with SERIALIZE waits for transactions active at entry to end.
  source: logbuf/logbuf.p.h:332 " * SERIALIZE -- ensure all currently active trans have ended."
- guarantee: elbb_QuiesceSystem with SERIALIZE returns only after every transaction that was active at the start of the call has ended.
  source: logbuf/logbuf.p.h:332 " * SERIALIZE -- ensure all currently active trans have ended."

### G33
- guarantee: elbb_QuiesceSystem with COMMIT waits for transactions active at entry to commit.
  source: logbuf/logbuf.p.h:333 " * COMMIT -- as above but wait until all trans have committed."
- guarantee: elbb_QuiesceSystem with COMMIT returns only after every such transaction has committed.
  source: logbuf/logbuf.p.h:333 " * COMMIT -- as above but wait until all trans have committed."

### G34
- guarantee: elbb_QuiesceSystem with WRITE schedules dirty user-data buffers for writing.
  source: logbuf/logbuf.p.h:335 " * WRITE -- schedules all dirty buffers containing user data."
- guarantee: elbb_QuiesceSystem with WRITE schedules all dirty user-data buffers; with FSYNC it also waits for those writes; with FLUSH it also invalidates user buffers; with FLUSHALL it invalidates all buffers.
  source: logbuf/logbuf.p.h:335 " * WRITE -- schedules all dirty buffers containing user data."

### G35
- guarantee: elbb_QuiesceSystem with FSYNC also waits for the user-data writes to finish.
  source: logbuf/logbuf.p.h:336 " * FSYNC -- also waits for writes to complete."
- guarantee: elbb_QuiesceSystem with WRITE schedules all dirty user-data buffers; with FSYNC it also waits for those writes; with FLUSH it also invalidates user buffers; with FLUSHALL it invalidates all buffers.
  source: logbuf/logbuf.p.h:335 " * WRITE -- schedules all dirty buffers containing user data."

### G36
- guarantee: elbb_QuiesceSystem with FLUSH also invalidates user-data buffers.
  source: logbuf/logbuf.p.h:337 " * FLUSH -- also invalidates user buffers (vol_close)."
- guarantee: elbb_QuiesceSystem with WRITE schedules all dirty user-data buffers; with FSYNC it also waits for those writes; with FLUSH it also invalidates user buffers; with FLUSHALL it invalidates all buffers.
  source: logbuf/logbuf.p.h:335 " * WRITE -- schedules all dirty buffers containing user data."

### G37
- guarantee: elbb_QuiesceSystem with FLUSHALL also invalidates all buffers.
  source: logbuf/logbuf.p.h:338 " * FLUSHALL -- also invalidates all buffers (elbb_Shutdown)."
- guarantee: elbb_QuiesceSystem with WRITE schedules all dirty user-data buffers; with FSYNC it also waits for those writes; with FLUSH it also invalidates user buffers; with FLUSHALL it invalidates all buffers.
  source: logbuf/logbuf.p.h:335 " * WRITE -- schedules all dirty buffers containing user data."

### G38
- guarantee: Quiescing allows concurrent activity after the captured log position rather than requiring the whole system to stop.
  source: logbuf/tran.c:1220 " * when the caller (elbb_QuiesceSystem) started. Other activity is allowed * to continue concurrently."
- guarantee: Quiesce without stopping the system waits only for transactions older than the log position sampled at the start of the call, so later activity may continue concurrently.
  source: logbuf/tran.c:1217 " * Quiescing without stopping the system works by waiting for all currently"

### G39
- guarantee: elbl_Close waits for active transactions to complete and writes a restart block.
  source: logbuf/log.c:1482 " * This routine is inclusive of elbl_Shutdown; it however always blocks * pending the completion of any active transactions. It then writes a"
- guarantee: A clean shutdown writes a checkpoint block and then a restart block, and does not return until pending transactions on that device are complete.
  source: logbuf/buffer.c:2581 " * Close the log; this waits until all pending transactions are complete."

### G40
- guarantee: elbb_FsyncForce writes and waits for dirty cached buffers selected by file-handle tag or block array.
  source: logbuf/buffer.c:2138 " code = asevent_WaitAll(aset);"
- guarantee: elbb_FsyncForce writes the tagged or listed buffers, forcing the log as needed for any logged buffer among them.
  source: logbuf/buffer.c:2018 " * elbb_FsyncForce -- implements fsync using two basic methods of specifying"

### G41
- guarantee: Ordinary elbb_SyncForce schedules dirty buffers that are neither being updated nor already being written, without waiting for pending writes.
  source: logbuf/buffer.c:2166 " * For sync, we do not want to wait. We walk through the entire hash * pool, skipping buffers being updated (they're busy), and scheduling"
- guarantee: elbb_SyncForce schedules writes of dirty buffers and does not wait for those writes to complete.
  source: logbuf/buffer.c:2166 " * For sync, we do not want to wait. We walk through the entire hash"

### G42
- guarantee: elbb_ModifySource logs the buffer modification when the transaction ID is valid and logging is requested.
  source: logbuf/buffer.c:1410 " * this routine changes the contents of a buffer and logs that change * if the tranId is not the invalid transaction id and the logRequest"
- guarantee: A logged modification writes the log record and then copies the new data into the buffer, leaving the buffer dirty.
  source: logbuf/buffer.c:1455 " if (logRequest) {"

### G43
- guarantee: elbb_Initialize logs initialization without logging the previous contents.
  source: logbuf/buffer.c:1588 " * By initialization, we mean modification in the case where the old data * do not have to be logged, i.e. the buffer was created by CreateBlock."
- guarantee: elbb_Initialize logs only the new contents of a CreateBlock buffer (no old data).
  source: logbuf/buffer.c:1588 " * By initialization, we mean modification in the case where the old data"

### G44
- guarantee: elbb_Kill refuses to delete a dirty logged buffer when metadataOK is false.
  source: logbuf/buffer.c:1364 " * RETURN CODES -- returns zero if all went well, and CANTDELETE if metadataOK * was false and the buffer was LOGGED and DIRTY. */"
- guarantee: elbb_Kill will not discard a dirty logged buffer unless metadataOK is true, which is allowed only after the transaction that freed that meta-data block has committed.
  source: logbuf/buffer.c:1359 " * metadataOK is true if it is safe to kill dirty metadata"

### G45
- guarantee: elbb_UndoZero records undo-zero coverage for the requested byte range in an existing transaction, including I/O outside the buffer system.
  source: logbuf/buffer.c:2414 " * elbb_UndoZero - Adds an undo-zero record to an existing transaction for * the specified range of bytes. This is to be used by the VM system for I/Os"
- guarantee: elbb_UndoZero appends old-fill-of-zero records to an existing transaction for a byte range, covering I/O that does not use the buffer system.
  source: logbuf/buffer.c:2414 " * elbb_UndoZero - Adds an undo-zero record to an existing transaction for"

### G46
- guarantee: elbb_UndoZeroBuffer creates and attaches a transaction if the buffer has no undo-zero transaction already.
  source: logbuf/buffer.c:2457 " * elbb_UndoZeroBuffer -- Adds an undo-zero record for the specified buffer. A * transaction is started and attached to the buffer if one is not already"
- guarantee: elbb_UndoZeroBuffer starts a nested transaction, attaches it to the dirty buffer, logs an old-fill-of-zero, and that transaction is ended when the buffer is no longer dirty.
  source: logbuf/buffer.c:2457 " * elbb_UndoZeroBuffer -- Adds an undo-zero record for the specified buffer. A"

### G47
- guarantee: Recovery redoes a transaction with an end record even when its begin record is outside the active log.
  source: logbuf/recover.c:1787 " * (no start, has end) - REDO"
- guarantee: User-space recovery marks a transaction REDO if an end record is seen (whether or not a begin is seen) and UNDO if a begin is seen and no end is seen.
  source: logbuf/recover.h:80 " * Begin seen REDO UNDO"

### G48
- guarantee: Recovery rejects transaction records with neither a start nor an end record.
  source: logbuf/recover.c:1781 " * The last state (no start, no end) is invalid - we should NEVER * see such a log. The other three are valid. Their corresponding"
- guarantee: User-space recovery fails if it finds a transaction that has neither a begin nor an end in the active log.
  source: logbuf/recover.h:81 " * Begin not seen REDO <fail>"

### G49
- guarantee: Recovery recognizes member end records from batch-end records only when the containing transaction committed.
  source: logbuf/recover.c:1690 " * with BEND records we search to see if the transaction committed. If it * did, we take the data section of each BEND record (which is really an"
- guarantee: Equivalence-class ends are written atomically: the head transaction writes a BEND record for each member and then its own END, and recovery reconstitutes those member END records only if the head transaction is REDO.
  source: logbuf/recover.c:1687 " * Bulk ends are the recovery end of ECs. Because the end records must"

### G50
- guarantee: For each recovered data block, recovery performs undo operations before redo operations.
  source: logbuf/recover.c:1970 " * To actually perform the recovery we must make two passes. * Pass # 1 is where all undo operations are done; pass # 2"
- guarantee: For each data block, recovery applies undo records newest-first, then redo records oldest-first, then writes the block back only if it actually read it.
  source: logbuf/recover.c:1970 " * To actually perform the recovery we must make two passes."

### G51
- guarantee: Recovery skips obsolete updates preceding an undo-zero kill record for a reused block.
  source: logbuf/recover.c:1875 " * NBS. These must be interpreted as kill records for earlier updates to * the same block. Set the status of all such updates to SKIP. */"
- guarantee: A committed undo-zero fill of zeroes is a kill record: recovery marks every earlier recoverable record on that same disk block SKIP, and those earlier records must have been REDO.
  source: logbuf/recover.h:83 " * Records (not whole transactions) are marked SKIP if they predate a kill"

### G52
- guarantee: Recovery fails with RCVR_USERDATA if an uncommitted kill precedes newer metadata records on the same block.
  source: logbuf/recover.c:1906 " if ((rec->status == RECVR_STATUS_UNDO) && someRecs) RECVR_RAISE (RCVR_USERDATA);"
- guarantee: Recovery raises RCVR_USERDATA if it sees an uncommitted kill after ordinary records on the same block.
  source: logbuf/recover.c:1907 " RECVR_RAISE (RCVR_USERDATA);"

### G53
- guarantee: Recovery fails with RCVR_METADATA if an uncommitted metadata update precedes a kill record on the same block.
  source: logbuf/recover.c:1914 " if (rec->status == RECVR_STATUS_UNDO) RECVR_RAISE (RCVR_METADATA);"
- guarantee: Recovery raises RCVR_METADATA if it sees an uncommitted recoverable record that a later kill would have skipped.
  source: logbuf/recover.c:1915 " RECVR_RAISE (RCVR_METADATA);"

### G54
- guarantee: Recovery checks page pass numbers as well as checksums to reject older log pages left on disk.
  source: logbuf/recover.c:929 " * to be checked as the log page could be a much older logpage * with a correct checksum but an old passnumber."
- guarantee: The log page header, including checksum, occupies the first sector, and recovery relies on sector atomicity: a page that was not written keeps an earlier pass number and is ignored as head.
  source: logbuf/recover.c:745 " * sector for the log page and we can rely on"

### G55
- guarantee: Successful recovery writes a clean restart record after applying disk changes.
  source: logbuf/recover.c:507 " /* Step 5: recovery is complete. Write out a clean restart record. */"
- guarantee: After successful user-space recovery, a checkpoint record is written on the next log page and a restart record is written on the first log block with the pass number increased by two.
  source: logbuf/recover.c:543 " * we increase the pass # to allow for an Episode crash immediately"
- guarantee: After successful recovery the log is clean.
  source: anode/aggregate.c:2405 " /* By definition the log is now clean. */"

### G56
- guarantee: elbr_GetCleanLogInfo returns zero for a log needing recovery and one for a clean log.
  source: logbuf/recover.c:2760 " * returns 0 if not clean (needs recovery), 1 if clean."
- guarantee: A log is clean, and recovery is not required, if and only if the first log block's page header has the salvage magic number and its first record is a restart record.
  source: logbuf/recover.c:2760 " * returns 0 if not clean (needs recovery), 1 if clean."

### G57
- guarantee: In kernel mode, elbr_Recover returns RCVR_MUSTRCVR instead of performing recovery.
  source: logbuf/recover.c:2374 " return RCVR_MUSTRCVR; /* no kernel recovery anymore */"
- guarantee: In the kernel, elbr_Recover does not recover a dirty log; it returns RCVR_MUSTRCVR.
  source: logbuf/recover.c:2374 "return RCVR_MUSTRCVR; /* no kernel recovery anymore */"

### G58
- guarantee: Log initialization detects a missing clean restart record and attempts recovery instead of starting ordinary logging.
  source: logbuf/log.c:730 " * disk. If so, we continue. If not, we attempt recovery and * return the resulting error value (never OK) to the caller."
- guarantee: Log initialization refuses to attach a dirty log until recovery has run: if the restart block is not clean it calls recovery and, on success, returns RCVR_RECOVERED.
  source: logbuf/log.c:733 " if (elbr_GetCleanLogInfo(ldP, *logLocnArray, &myLogHdr) == 0) {"

### G59
- guarantee: Successful recovery during log initialization is reported as RCVR_RECOVERED rather than ordinary success.
  source: logbuf/log.c:737 " return RCVR_RECOVERED; /* so upper levels can clear buffers */"
- guarantee: Log initialization refuses to attach a dirty log until recovery has run: if the restart block is not clean it calls recovery and, on success, returns RCVR_RECOVERED.
  source: logbuf/log.c:733 " if (elbr_GetCleanLogInfo(ldP, *logLocnArray, &myLogHdr) == 0) {"

### G60
- guarantee: elbb_LogInit invalidates cached buffers after successful recovery.
  source: logbuf/buffer.c:1837 " /* log recovered, we invalidate the buffer pool by * calling shutdown. Note that we assume none of the"
- guarantee: After recovery returns RCVR_RECOVERED, the buffer pool for that device is invalidated.
  source: logbuf/buffer.c:1837 " /* log recovered, we invalidate the buffer pool by"

### G61
- guarantee: For each recovered block, undo applies records from newest to oldest.
  source: logbuf/recover.c:1992 " for (rec2P = FIFO_LookAtNewest(&(recP)->diskFifo, DISKTHREAD);"
- guarantee: For each data block, recovery applies undo records newest-first, then redo records oldest-first, then writes the block back only if it actually read it.
  source: logbuf/recover.c:1970 " * To actually perform the recovery we must make two passes."

### G62
- guarantee: For each recovered block, redo applies records from oldest to newest.
  source: logbuf/recover.c:2020 " rec2P = FIFO_NextOldest(&(recP)->diskFifo, rec2P,"
- guarantee: For each data block, recovery applies undo records newest-first, then redo records oldest-first, then writes the block back only if it actually read it.
  source: logbuf/recover.c:1970 " * To actually perform the recovery we must make two passes."

### G63
- guarantee: Log creation zero-initializes every log block except the first, which receives a restart record.
  source: logbuf/log.c:904 " * We skip the first block because we will be writing a restart * record into it. All other blocks are initialized to zero."
- guarantee: Create of a new log zeroes every page but the first and writes a restart record on the first log block.
  source: logbuf/log.c:904 " * We skip the first block because we will be writing a restart"


## The sealed analysis (v2, sealed 2026-10-27T18:15:54Z, before any finding existed)

# SEALED for tupay D2, version 2. Do not read unless you are judging the comparison.

Written by episode's steward (Claude Opus 5.5) on 2026-10-27, answering tupay's follow-up
(`docs/requests/2026-10-26-from-tupay-D2-followup.md`), before D2 phase 0.
**This file supersedes `sealed/2026-10-26-tupay-D2-findings.md` for judging.**
v1 stays in the history unchanged. v2 changes no bug. It adds, for each one, an
explicit effect class and a classification against D2's definition of an
environment contract (`tupay/experiments/D2/brief-enumerate.md`, Task: "an
obligation on something `logbuf` depends on ... **not** a rule of `logbuf`
itself"). It also makes the mechanism a field of its own. Where v1's wording
was loose, v2 says so.

Code: `/home/tony/projects/dce/dce/src/file/episode/logbuf` (DCE 1.2.2).
Models: `spec/` (see `spec/README.md`).

Effect classes: **silent-loss** (committed or acknowledged data gone, no error);
**silent-atomicity** (a partial or uncommitted change survives recovery, no
error); **silent-splice** (recovery accepts log pages from two runs as one log);
**exposure** (another owner's data becomes visible in a file); **fail-stop**
(recovery refuses or salvages; no wrong state is accepted).

Environment column: **env** = the bug is a violation of an obligation on something
outside `logbuf`; **own** = a defect in `logbuf`'s own rules, where the environment
behaves within what it promises.

| id | contract or assumption | mechanism | effect class | env / own | in a source comment |
|---|---|---|---|---|---|
| E1 | none violated. The I/O layer may complete log page writes out of order, and the code says it doesn't assume order | `log.c:2990` stores `io_window` as the *count* of pages in transit; recovery (SafeDumpLog) uses it as the *distance* back from the head to check. An older page still in transit after newer ones complete lies outside the count, so a missing page falls inside the scanned range | fail-stop (spurious `RCVR_IOERR`, salvager) | own | no |
| E2 | disk: a completed write is durable | the log treats a completed page write as stable; on a volatile write cache the page can be lost at power failure after commit is acknowledged | silent-loss (acknowledged commit) | env | yes (`recover.c:894`, wam 920624) |
| E3 | disk: a completed write is durable (includes: a write that completes *during* a flush is not covered by that flush) | a stolen uncommitted metadata page reaches media while its undo record, though "complete", is still only in cache; crash; recovery has no undo for it | silent-atomicity | env | yes (`recover.c:894`) |
| E4 | disk: a completed write was actually stored (no lost writes) | a lost metadata page write is masked by old/new redo until checkpoint truncation discards the redo record; metadata pages carry no parent-held version, so the stale page is never detected | silent-loss (committed update) | env | no |
| E5 | disk: a completed write is durable (here: the user data write covered by undo-zero) | OFILL correctly precedes the allocation's END; Z's END becomes durable while the user data sits in a volatile cache; crash; recovery keeps the allocation, does not undo-zero, and the block shows its old contents | exposure | env | yes (ordering at `log.c:1680`, wam 920805; device assumption at `recover.c:894`; the exposure is not stated) |
| E6 | none violated. Out-of-order completion is permitted (as E1), and a crash is an expected event | the clean-mount path starts pass R+1 at slot 0 without persisting it; after crash, out-of-order landing and a second clean mount, two runs' pages share a pass number and a valid checksum | silent-splice | own | partly (`recover.c:545` "+2 ... paranoia" anticipates it on the recovery path only) |
| E7 | none below `logbuf`; an internal invariant: every page on media is within half the pass range of the head | restarting at slot 0 on every mount leaves far slots unrewritten while the pass counter advances; the masked comparison in the head search can then read an old page as newer | fail-stop in the model (3-bit field: salvage). At 16 bits, argued only: the head is misidentified, and whether the result is fail-stop or silent is **not established** | own | no |

Counts: 7 bugs. env 4 (E2, E3, E4, E5); own 3 (E1, E6, E7).
Comment: 4 (E2, E3, E5, E6), of which env 3 (E2, E3, E5) and own 1 (E6).
All 7 carry contract-or-assumption, mechanism and effect class. E7's effect class is
given with its uncertainty, which matching must respect: for E7, either a fail-stop
or a silent wrong-head effect counts as the same effect class.

Corrections to v1's wording, not to substance:
- v1 gave E1 and E6 a "contract violated" of in-order completion. Under D2's
  definition that is wrong: the environment doesn't promise in-order completion,
  and `logbuf` doesn't rely on it by contract. The bugs are `logbuf`'s own.
- v1's E3 effect was descriptive; v2 classes it silent-atomicity.

Unchanged from v1 and not repeated here: the confirmed design properties P1–P6, the
open item O1, the out-of-scope list, and the visible-in-history column (0 of 7).
