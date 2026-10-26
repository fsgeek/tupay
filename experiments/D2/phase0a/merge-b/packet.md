# Brief: merge two lists of guarantees (D2 phase 0a)

Below are two lists, written independently from two sources (the paper *The Episode File System*, USENIX Winter 1992, and Episode's source in OSF DCE 1.2.2), of the **guarantees** Episode's log and recovery (`logbuf`) make to the rest of the file system, its users or operators. Each entry has an id `<list>:G<n>`. Different lists often state the same guarantee in different words, or split one guarantee into several finer ones.

Your task: group entries that state **the same guarantee**. Two entries belong in one group only if a run that violates one necessarily violates the other. An entry that is broader than another may appear in more than one group (once with each finer entry it covers). An entry that matches nothing need not be listed.

Use only the text below. Do not use any tool. Reply with JSON only, in exactly this shape, and nothing else:

{"groups": [["codex:G3", "grok:G7"], ["codex:G1", "grok:G4", "grok:G2"]]}

Every id you write must appear in the lists below. Groups have at least two ids.

---
### codex:G1
- guarantee: After a crash and successful recovery, file-system metadata, including directories, allocation bitmaps, indirect blocks, and anode tables, is consistent.
- source: §"Background" "guarantee that after a crash, the le system meta-data (directories, allocation bitmaps, indirect blocks and anode tables) are consistent, generally eliminating the need for running \fsck.""
- stated: stated

### codex:G2
- guarantee: A committed metadata transaction applies all its updates atomically.
- source: §"Component Architecture" "that either all the updates within a transaction (if a transaction commits), or none of them (if a transaction aborts), will be applied."
- stated: stated

### codex:G3
- guarantee: An aborted metadata transaction leaves none of its updates applied.
- source: §"Component Architecture" "that either all the updates within a transaction (if a transaction commits), or none of them (if a transaction aborts), will be applied."
- stated: stated

### codex:G4
- guarantee: For every metadata update, logging records both the original and new values.
- source: §"Component Architecture" "value logging techniques [MOH 89]. In a nutshell, this form of logging works by logging, for every update made to any le system meta-data, both the original and new values of the updated data."
- stated: stated

### codex:G5
- guarantee: Before writing a dirty metadata buffer to its home disk location, the buffer package writes the corresponding log entries to disk.
- source: §"Component Architecture" "before the bu er package allows any dirty meta-data bu er to be written back out to the disk, it writes out these log entries to the disk."
- stated: stated

### codex:G6
- guarantee: Recovery restores aborted metadata updates to their values before the transaction began.
- source: §"Component Architecture" "the log to undo all of the updates made to the meta-data, and restore the meta-data to its state before the transaction started."
- stated: stated

### codex:G7
- guarantee: Recovery redoes committed metadata updates even when their buffers had not reached disk before the crash.
- source: §"Component Architecture" "transaction started. If the transaction committed, there is enough information in the log to redo all of the meta-data updates, even those that hadn't yet made it from the disk bu ers to the disk."
- stated: stated

### codex:G8
- guarantee: Recovery undoes transactions that were uncommitted at the crash.
- source: §"Component Architecture" "The recovery procedure runs after a crash, replaying the committed transactions and undoing the uncommitted transactions, and thus restoring the le system to a consistent state."
- stated: stated

### codex:G9
- guarantee: The paper initially promises recovery time proportional to activity at the crash rather than disk size, subject to its later qualification about uncheckpointed committed transactions.
- source: §"Component Architecture" "contains information describing transactions still in progress, recovery time is proportional to the activity at the time of the crash, not to the size of the disk."
- stated: stated

### codex:G10
- guarantee: The paper claims log replay runs orders of magnitude faster than BSD fsck.
- source: §"Component Architecture" "of magnitude faster than the BSD fsck program."
- stated: stated

### codex:G11
- guarantee: Transactions may release transactional locks before the end of the transaction.
- source: §"Logging Architecture" "tional locking instead of two-phase locking. Episode transactions can acquire locks when they need them, and drop them as soon as they are nished using them, rather than waiting for the transaction's end."
- stated: stated

### codex:G12
- guarantee: Active transactions that lock the same object during their lifetimes are merged into an equivalence class.
- source: §"Logging Architecture" "have otherwise been able to commit, if a crash intervenes. Speci cally, all active transactions that lock the same object during their lifetime are merged into an equivalence class (EC). An EC has the property that"
- stated: stated

### codex:G13
- guarantee: All transactions in an equivalence class commit together or none commit.
- source: §"Logging Architecture" "either all of its transactions commit or none do.3 In the example above, transaction 1 and 2 would form"
- stated: stated

### codex:G14
- guarantee: A crash before all transactions in an equivalence class have committed aborts every transaction in that class.
- source: §"Logging Architecture" "If the system crashes before all of the transactions in an EC have committed, all the transactions in the EC are aborted."
- stated: stated

### codex:G15
- guarantee: An explicit synchronization request such as fsync prevents the requested metadata persistence from being indefinitely deferred.
- source: §"Logging Architecture" "Meta-data changes to the disk itself can often be deferred, unless speci cally requested by an oper- ation like fsync. Consistency of the le system doesn't require that the system be current."
- stated: implied

### codex:G16
- guarantee: When a newly allocated data block has an incomplete first-write transaction at a crash, recovery zeroes the block.
- source: §"Logging Architecture" "to it completes. If the system crashes and the transaction aborts, the recovery procedure for this special transaction zeroes the contents of the block."
- stated: stated

### codex:G17
- guarantee: Log-space admission control keeps running transactions within the available log space.
- source: §"Logging Architecture" "when they begin. This allows the use of a very simple algorithm to ensure that running transactions never exceed the space available in the log."
- stated: stated

### codex:G18
- guarantee: Dirty metadata buffers may be written before their transactions end.
- source: §"Logging Architecture" "when to write these bu ers. Old value / new value logging, on the other hand de-couples the writing of bu ers from the end of transactions, at the expense of having to write more data to the log."
- stated: implied

### codex:G19
- guarantee: Each transaction in a multi-transaction filesystem operation leaves the filesystem consistent, even if the overall operation is unfinished.
- source: §"Logging Architecture" "operations, followed by a deletion of the empty le. After each transaction, the le system is consistent, if not in the nal desired state."
- stated: stated

### codex:G20
- guarantee: The active log retains uncommitted transactions needed for crash undo.
- source: §"Recovery Time" "active portion of the log is that part of the log that needs to be replayed after a crash, and must include all of the uncommitted transactions, since these must be undone in the event of a crash."
- stated: stated

### codex:G21
- guarantee: The active log also retains committed updates whose metadata buffers remain dirty, qualifying the earlier claim that recovery depends only on in-progress transactions.
- source: §"Recovery Time" "of the log may go back even further, should the bu er cache still contain dirty meta-data blocks that were modi ed by committed transactions."
- stated: stated

### codex:G22
- guarantee: Checkpointing discards committed log history only after writing the buffers required to preserve those transactions.
- source: §"Recovery Time" "the replay of that part of the log in the event of a crash. The operation of writing bu ers modi ed by committed transactions and discarding those portions no longer required to ensure the permanence of those"
- stated: implied

### codex:G23
- guarantee: The system prevents the log from becoming full.
- source: §"Recovery Time" "permit the log to become full"
- stated: stated

### codex:G24
- guarantee: The work needed to replay one active log block has a finite bound on the number of metadata blocks it can affect.
- source: §"Recovery Time" "Of course, the time to replay a block of the active log is not constant, but is bounded: There is a maximum number of meta-data blocks whose updates can be described by a block of the log, but many"
- stated: stated

### codex:G25
- guarantee: elbb_LogForce with waitOK zero commits a complete transaction but returns BUF_WOULDBLOCK if it would have to wait for the transaction to end.
- source: logbuf/tran.c:948 " * 0 -- caller can't wait for other transactions to end. Commit only if * transaction is complete, otherwise return BUF_WOULDBLOCK."
- stated: stated

### codex:G26
- guarantee: elbb_LogForce with waitOK one returns only after the transaction has committed, making its updates persistent.
- source: logbuf/tran.c:950 " * 1 -- don't return until transaction has committed. This guarantees * persistence for updated done under this transaction. "fsync" is the"
- stated: stated

### codex:G27
- guarantee: elbb_LogForce with waitOK two waits for completion and serializes the transaction with transactions begun after the call returns.
- source: logbuf/tran.c:953 " * 2 -- don't return until transaction has completed. This ensures * serialization of this transaction with respect to any transactions"
- stated: stated

### codex:G28
- guarantee: Forcing an already forgotten transaction returns success.
- source: logbuf/tran.c:968 " if (!tP) return BUFFER_OK;"
- stated: implied

### codex:G29
- guarantee: Ending a transaction in an unfinished equivalence class may leave it pending rather than committed.
- source: logbuf/tran.c:426 " * elbt_EndTran -- handle changing the state of a transaction from active to * complete or pending (EC)."
- stated: stated

### codex:G30
- guarantee: An equivalence class writes all member batch-end records before writing its final head end record.
- source: logbuf/tran.c:795 " * We won't write the end record out for the final transaction until * after all the batch end records have been written out."
- stated: stated

### codex:G31
- guarantee: elbt_ECMerge joins the supplied transactions into one equivalence class.
- source: logbuf/tran.c:641 " * elbt_ECMerge -- joins two transactions into an equivalence class. The * second tran must be active."
- stated: stated

### codex:G32
- guarantee: Starting a transaction with an old transaction ID does not block waiting for other transactions to complete.
- source: logbuf/buffer.c:1739 " * By providing an old transaction ID, this call will not block. If there * is no transaction ID, this call might wait pending completion of other"
- stated: stated

### codex:G33
- guarantee: When transaction allocation fails because of log pressure, elbb_StartTran handles the full log and retries.
- source: logbuf/buffer.c:1743 " * If this routine fails to allocate a transaction we presume it is because * the log is full and so we invoke the log full handling and try again."
- stated: stated

### codex:G34
- guarantee: A transaction is not treated as durably committed merely because its end record has been constructed in memory.
- source: logbuf/log.c:140 " * The transactions on the cTranList are being held until their end records are * actually committed to disk. Then they are returned to the tran module when"
- stated: implied

### codex:G35
- guarantee: elbl_ForceTran forces the log to disk through the transaction's last update.
- source: logbuf/log.c:2035 " * elbl_ForceTran -- force the log to disk up to the specified transaction's * last update."
- stated: stated

### codex:G36
- guarantee: elbl_ForceBuffer forces the log to disk through the specified buffer's last update.
- source: logbuf/log.c:2108 " * elbl_ForceBuffer -- force the log to disk up to the specified buffer's * last update."
- stated: stated

### codex:G37
- guarantee: elbb_Release with elbb_syncLog forces the log through the most recent transaction on that buffer.
- source: logbuf/buffer.c:1250 " * syncLog - force log up to most recent transaction on this buffer"
- stated: stated

### codex:G38
- guarantee: elbb_Release with elbb_sync returns after both the necessary log and the data buffer have been written.
- source: logbuf/logbuf.p.h:66 " elbb_sync, /* force write log, force write data buffer, upon return * both log and data buffer have been written */"
- stated: stated

### codex:G39
- guarantee: elbb_Release with elbb_async schedules a write immediately and returns without waiting for write completion.
- source: logbuf/logbuf.p.h:63 " elbb_async, /* schedule write now, but don't wait for completion */"
- stated: stated

### codex:G40
- guarantee: The elbb_Release interface comment promises that elbb_lazy returns without scheduling I/O, although its implementation writes unlogged buffers.
- source: logbuf/buffer.c:1259 " * lazy always returns without I/O being scheduled."
- stated: stated

### codex:G41
- guarantee: The elbb_adel interface description promises asynchronous deletion and buffer reuse upon write completion, although the implementation waits.
- source: logbuf/logbuf.p.h:69 " elbb_adel, /* schedule write now, reuse upon completion of write. */"
- stated: stated

### codex:G42
- guarantee: elbb_Release with elbb_sdel waits for the scheduled write before buffer reuse.
- source: logbuf/logbuf.p.h:70 " elbb_sdel /* schedule write now, wait, reuse upon completion. */"
- stated: stated

### codex:G43
- guarantee: elbb_QuiesceSystem with SERIALIZE waits for transactions active at entry to end.
- source: logbuf/logbuf.p.h:332 " * SERIALIZE -- ensure all currently active trans have ended."
- stated: stated

### codex:G44
- guarantee: elbb_QuiesceSystem with COMMIT waits for transactions active at entry to commit.
- source: logbuf/logbuf.p.h:333 " * COMMIT -- as above but wait until all trans have committed."
- stated: stated

### codex:G45
- guarantee: elbb_QuiesceSystem with WRITE schedules dirty user-data buffers for writing.
- source: logbuf/logbuf.p.h:335 " * WRITE -- schedules all dirty buffers containing user data."
- stated: stated

### codex:G46
- guarantee: elbb_QuiesceSystem with FSYNC also waits for the user-data writes to finish.
- source: logbuf/logbuf.p.h:336 " * FSYNC -- also waits for writes to complete."
- stated: stated

### codex:G47
- guarantee: elbb_QuiesceSystem with FLUSH also invalidates user-data buffers.
- source: logbuf/logbuf.p.h:337 " * FLUSH -- also invalidates user buffers (vol_close)."
- stated: stated

### codex:G48
- guarantee: elbb_QuiesceSystem with FLUSHALL also invalidates all buffers.
- source: logbuf/logbuf.p.h:338 " * FLUSHALL -- also invalidates all buffers (elbb_Shutdown)."
- stated: stated

### codex:G49
- guarantee: Quiescing allows concurrent activity after the captured log position rather than requiring the whole system to stop.
- source: logbuf/tran.c:1220 " * when the caller (elbb_QuiesceSystem) started. Other activity is allowed * to continue concurrently."
- stated: stated

### codex:G50
- guarantee: elbt_Quiesce consistency zero waits for earlier unnested transactions to end.
- source: logbuf/tran.c:1224 " * "consistency"; if zero, we wait for all unnested transactions started * before (pass,off) to end. Unnested transaction includes all those"
- stated: stated

### codex:G51
- guarantee: elbt_Quiesce consistency one waits for earlier unnested transactions to commit.
- source: logbuf/tran.c:1226 " * except undo zero transactions. If it is one we wait for all unnested * transactions to commit. The other interesting value is three,"
- stated: stated

### codex:G52
- guarantee: elbt_Quiesce consistency three also commits earlier undo-zero transactions.
- source: logbuf/tran.c:1228 " * requesting that we also commit undo zeros (see cautions below). The"
- stated: stated

### codex:G53
- guarantee: elbt_Quiesce consistency two serializes earlier undo-zero transactions.
- source: logbuf/tran.c:1229 " * value two serializes undo zero trans, this is used by elbb_StartTran."
- stated: stated

### codex:G54
- guarantee: elbb_Shutdown writes pending buffers, removes the device's buffers from use, and shuts down its log.
- source: logbuf/buffer.c:2563 " * or unlogged.) this routine writes out all pending buffers and removes * all buffers for this device from use. It uses QuiesceSystem to do this"
- stated: stated

### codex:G55
- guarantee: elbl_Close waits for active transactions to complete and writes a restart block.
- source: logbuf/log.c:1482 " * This routine is inclusive of elbl_Shutdown; it however always blocks * pending the completion of any active transactions. It then writes a"
- stated: stated

### codex:G56
- guarantee: On return from elbl_Close, the log is clean, metadata is on disk, and the returned transactions count as committed.
- source: logbuf/log.c:1487 " * this log. They should all be considered committed upon return from * this function (the log is clean, all meta-data is written to disk, etc.)"
- stated: stated

### codex:G57
- guarantee: elbb_FsyncForce writes and waits for dirty cached buffers selected by file-handle tag or block array.
- source: logbuf/buffer.c:2138 " code = asevent_WaitAll(aset);"
- stated: implied

### codex:G58
- guarantee: Ordinary elbb_SyncForce schedules dirty buffers that are neither being updated nor already being written, without waiting for pending writes.
- source: logbuf/buffer.c:2166 " * For sync, we do not want to wait. We walk through the entire hash * pool, skipping buffers being updated (they're busy), and scheduling"
- stated: stated

### codex:G59
- guarantee: elbb_ModifySource logs the buffer modification when the transaction ID is valid and logging is requested.
- source: logbuf/buffer.c:1410 " * this routine changes the contents of a buffer and logs that change * if the tranId is not the invalid transaction id and the logRequest"
- stated: stated

### codex:G60
- guarantee: elbb_ModifySource returns the resulting buffer handle through its output parameter.
- source: logbuf/buffer.c:1414 " * this routine returns the buffer handle in the nbP pointer - caller * cannot assume the buffer handle will not change across this call."
- stated: stated

### codex:G61
- guarantee: elbb_Initialize logs initialization without logging the previous contents.
- source: logbuf/buffer.c:1588 " * By initialization, we mean modification in the case where the old data * do not have to be logged, i.e. the buffer was created by CreateBlock."
- stated: stated

### codex:G62
- guarantee: elbb_ReadGeneral checks for an existing cached buffer before scheduling a disk read.
- source: logbuf/buffer.c:974 " * It checks to see if a buffer already exists for this block prior to * scheduling a read."
- stated: stated

### codex:G63
- guarantee: The synchronous read mode of elbb_ReadGeneral waits for read completion.
- source: logbuf/buffer.c:971 " * (2) Allocate & read a buffer (waits for completion)"
- stated: stated

### codex:G64
- guarantee: The asynchronous read mode of elbb_ReadGeneral schedules a read without waiting for completion.
- source: logbuf/buffer.c:972 " * (3) Allocate & schedule read for a buffer (doesn't wait for completion)."
- stated: stated

### codex:G65
- guarantee: elbb_Kill refuses to delete a dirty logged buffer when metadataOK is false.
- source: logbuf/buffer.c:1364 " * RETURN CODES -- returns zero if all went well, and CANTDELETE if metadataOK * was false and the buffer was LOGGED and DIRTY. */"
- stated: stated

### codex:G66
- guarantee: elbb_Reserve provides buffer reservations for paths that need multiple buffers simultaneously to avoid buffer-allocation deadlock.
- source: logbuf/buffer.c:2193 " * elbb_Reserve - reservation call for code paths which require multiple * buffers simultaneously; this avoids deadlock."
- stated: stated

### codex:G67
- guarantee: elbb_UndoZero records undo-zero coverage for the requested byte range in an existing transaction, including I/O outside the buffer system.
- source: logbuf/buffer.c:2414 " * elbb_UndoZero - Adds an undo-zero record to an existing transaction for * the specified range of bytes. This is to be used by the VM system for I/Os"
- stated: stated

### codex:G68
- guarantee: elbb_UndoZeroBuffer creates and attaches a transaction if the buffer has no undo-zero transaction already.
- source: logbuf/buffer.c:2457 " * elbb_UndoZeroBuffer -- Adds an undo-zero record for the specified buffer. A * transaction is started and attached to the buffer if one is not already"
- stated: stated

### codex:G69
- guarantee: Recovery redoes a transaction with an end record even when its begin record is outside the active log.
- source: logbuf/recover.c:1787 " * (no start, has end) - REDO"
- stated: stated

### codex:G70
- guarantee: Recovery rejects transaction records with neither a start nor an end record.
- source: logbuf/recover.c:1781 " * The last state (no start, no end) is invalid - we should NEVER * see such a log. The other three are valid. Their corresponding"
- stated: stated

### codex:G71
- guarantee: Recovery recognizes member end records from batch-end records only when the containing transaction committed.
- source: logbuf/recover.c:1690 " * with BEND records we search to see if the transaction committed. If it * did, we take the data section of each BEND record (which is really an"
- stated: stated

### codex:G72
- guarantee: For each recovered data block, recovery performs undo operations before redo operations.
- source: logbuf/recover.c:1970 " * To actually perform the recovery we must make two passes. * Pass # 1 is where all undo operations are done; pass # 2"
- stated: stated

### codex:G73
- guarantee: Recovery skips obsolete updates preceding an undo-zero kill record for a reused block.
- source: logbuf/recover.c:1875 " * NBS. These must be interpreted as kill records for earlier updates to * the same block. Set the status of all such updates to SKIP. */"
- stated: stated

### codex:G74
- guarantee: Recovery fails with RCVR_USERDATA if an uncommitted kill precedes newer metadata records on the same block.
- source: logbuf/recover.c:1906 " if ((rec->status == RECVR_STATUS_UNDO) && someRecs) RECVR_RAISE (RCVR_USERDATA);"
- stated: implied

### codex:G75
- guarantee: Recovery fails with RCVR_METADATA if an uncommitted metadata update precedes a kill record on the same block.
- source: logbuf/recover.c:1914 " if (rec->status == RECVR_STATUS_UNDO) RECVR_RAISE (RCVR_METADATA);"
- stated: implied

### codex:G76
- guarantee: Recovery can move the log head backward past incompletely written in-transit pages even when log writes completed out of order.
- source: logbuf/recover.c:888 " * out to disk. Because we don't assume writes are in order, we * must check to assure ourselves that all the pages in the I/O"
- stated: stated

### codex:G77
- guarantee: Recovery checks page pass numbers as well as checksums to reject older log pages left on disk.
- source: logbuf/recover.c:929 " * to be checked as the log page could be a much older logpage * with a correct checksum but an old passnumber."
- stated: stated

### codex:G78
- guarantee: For supported checksum formats, a checksum failure in the retained active log outside the in-transit window causes recovery to fail.
- source: logbuf/recover.c:756 " * expected to be on disk correctly. If checksum errors are * detected for these pages, there is really nothing we can do"
- stated: stated

### codex:G79
- guarantee: Successful recovery writes a clean restart record after applying disk changes.
- source: logbuf/recover.c:507 " /* Step 5: recovery is complete. Write out a clean restart record. */"
- stated: implied

### codex:G80
- guarantee: A crash while writing the checkpoint block leaves the previous active log usable.
- source: logbuf/recover.c:2606 " * block of the active log, so if the machine crashes while we are writing * the checkpoint block, there's no problem. If we successfully write a"
- stated: stated

### codex:G81
- guarantee: A crash while writing the restart block after a successful checkpoint leaves a usable recovery log.
- source: logbuf/recover.c:2614 " * the checkpoint block. In either case, the log is usable (recovery can * proceed)."
- stated: stated

### codex:G82
- guarantee: elbr_GetCleanLogInfo returns zero for a log needing recovery and one for a clean log.
- source: logbuf/recover.c:2760 " * returns 0 if not clean (needs recovery), 1 if clean."
- stated: stated

### codex:G83
- guarantee: After reading a page with the correct salvage magic, elbr_GetCleanLogInfo fills a supplied header output even when later checks find the log unclean.
- source: logbuf/recover.c:2761 " * The log page hdr structure ptr (if non-zero) is * filled in by this routine."
- stated: stated

### codex:G84
- guarantee: In kernel mode, elbr_Recover returns RCVR_MUSTRCVR instead of performing recovery.
- source: logbuf/recover.c:2374 " return RCVR_MUSTRCVR; /* no kernel recovery anymore */"
- stated: implied

### codex:G85
- guarantee: Log initialization detects a missing clean restart record and attempts recovery instead of starting ordinary logging.
- source: logbuf/log.c:730 " * disk. If so, we continue. If not, we attempt recovery and * return the resulting error value (never OK) to the caller."
- stated: stated

### codex:G86
- guarantee: Successful recovery during log initialization is reported as RCVR_RECOVERED rather than ordinary success.
- source: logbuf/log.c:737 " return RCVR_RECOVERED; /* so upper levels can clear buffers */"
- stated: implied

### codex:G87
- guarantee: elbb_LogInit invalidates cached buffers after successful recovery.
- source: logbuf/buffer.c:1837 " /* log recovered, we invalidate the buffer pool by * calling shutdown. Note that we assume none of the"
- stated: stated

### codex:G88
- guarantee: Log initialization rejects a device that already has an active log.
- source: logbuf/log.c:712 " return LOG_LOGEXISTS;"
- stated: implied

### codex:G89
- guarantee: Log initialization rejects a log smaller than the computed minimum size.
- source: logbuf/log.c:750 " if (elbl_MinLogSize(lmP->dev, 0) > logLocnArraySize) {"
- stated: implied

### codex:G90
- guarantee: Unknown on-disk checksum types are accepted with a diagnostic that checksum checking is being ignored.
- source: logbuf/recover.c:2578 " /* Unknown checksum type recorded on disk. Force success of * checksum validity check */"
- stated: stated

### codex:G91
- guarantee: Recognized legacy log pages with checksums but no recorded checksum lengths remain supported.
- source: logbuf/recover.c:2438 " * Account for (pre solaris release) aggregates that record checksums * but no checksum lengths in the log pages, when determining"
- stated: stated

### codex:G92
- guarantee: Writing a restart block with an unknown checksum version switches the log to the default checksum version.
- source: logbuf/recover.c:2705 " /* Validate checksum version and switch to default version type"
- stated: implied

### codex:G93
- guarantee: Successful user-space recovery reports elapsed time and counts of recovered pages, records, changed blocks, and undo/redo operations.
- source: logbuf/recover.c:562 " printf("recovery statistics:\n");"
- stated: implied

### codex:G94
- guarantee: The active-log dump interface exposes the contents of the active portion of the log to external programs.
- source: logbuf/recover.c:592 " * of the active log. It can be called by an external program to retrieve the * actual contents of the active portion of the log."
- stated: stated

### codex:G95
- guarantee: The entire-log dump interface exposes the contents of the whole log to external programs.
- source: logbuf/recover.c:633 " * of the ENTIRE log. It can be called by an external program to retrieve the * actual contents of the entire log."
- stated: stated

### codex:G96
- guarantee: The implementation of elbb_Release with elbb_lazy schedules a write for unlogged buffers, contrary to its no-I/O interface comment.
- source: logbuf/buffer.c:1288 " if (!bufferIsLogged(bP)) { retval = Write(bP);"
- stated: implied

### codex:G97
- guarantee: The implementation of elbb_Release with elbb_adel waits for the write just like elbb_sdel, despite the asynchronous-deletion interface description.
- source: logbuf/buffer.c:1295 " /* Can't presently handle asyncronous deletion of buffers. To do it * right ReadGeneral would have to check and wait. So we just wait"
- stated: stated

### codex:G98
- guarantee: The header promises that elbb_syncLog both forces the log and schedules the data-buffer write.
- source: logbuf/logbuf.p.h:64 " elbb_syncLog, /* force write log, schedule buffer write, don't wait * for data buffer write completion. */"
- stated: stated

### codex:G99
- guarantee: The implementation of elbb_Release with elbb_syncLog only forces the log and does not itself schedule the data-buffer write promised by the header.
- source: logbuf/buffer.c:1314 " case elbb_syncLog: elbl_ForceBuffer(bP);"
- stated: implied

### codex:G100
- guarantee: elbb_Fill fills the specified region with the requested one-byte pattern.
- source: logbuf/buffer.c:1499 " * This routine is used to implement a "flood" of a data area with a * specific bit pattern (1 char). It optionally saves the old data"
- stated: stated

### codex:G101
- guarantee: When logging and saveOld are requested, elbb_Fill records the old data for undo before the new fill.
- source: logbuf/buffer.c:1549 " LogWrite(tranId, LOGREC_ODATA, fillSize, offset, bP, 0, retval,"
- stated: implied

### codex:G102
- guarantee: elbb_FastModify promises a logged modification equivalent to reading, modifying, and releasing the buffer, although its source identifies a log-full bug.
- source: logbuf/buffer.c:1644 " * This routine is equivalent to a ReadGeneral/ModifySource/Release operation"
- stated: stated

### codex:G103
- guarantee: For each recovered block, undo applies records from newest to oldest.
- source: logbuf/recover.c:1992 " for (rec2P = FIFO_LookAtNewest(&(recP)->diskFifo, DISKTHREAD);"
- stated: implied

### codex:G104
- guarantee: For each recovered block, redo applies records from oldest to newest.
- source: logbuf/recover.c:2020 " rec2P = FIFO_NextOldest(&(recP)->diskFifo, rec2P,"
- stated: implied

### codex:G105
- guarantee: Recovery writes changed data blocks synchronously before proceeding to its clean-log completion.
- source: logbuf/recover.c:2037 " * write changes back (synch. I/O) - do nothing if * I/O was deferred (ie for NBS)."
- stated: implied

### codex:G106
- guarantee: User-space elbr_Recover rejects null devices, a null log block array, or an empty log block array with RCVR_INVALID.
- source: logbuf/recover.c:410 " if ( !ldP || !dP || !logLocnArray || (logLocnArraySize == 0)) return RCVR_INVALID;"
- stated: implied

### codex:G107
- guarantee: The committed-status convenience function returns true for either a committed transaction or a transaction ID no longer in the transaction table.
- source: logbuf/buffer.c:1886 " if ((code == BUF_BADTRAN) || (code == BUF_TRANCOMMIT)) return 1;"
- stated: implied

### codex:G108
- guarantee: Log creation zero-initializes every log block except the first, which receives a restart record.
- source: logbuf/log.c:904 " * We skip the first block because we will be writing a restart * record into it. All other blocks are initialized to zero."
- stated: stated

### grok:G1
- guarantee: After a crash, file-system meta-data (directories, allocation bitmaps, indirect blocks, and anode tables) are consistent.
- source: §"Background" "guarantee that after a crash, the le system meta-data (directories, allocation bitmaps, indirect blocks and"
- stated: stated

### grok:G2
- guarantee: After a crash, recovery generally eliminates the need to run fsck.
- source: §"Background" "anode tables) are consistent, generally eliminating the need for running \fsck."
- stated: stated

### grok:G3
- guarantee: Logging of meta-data makes the file system restart quickly after a crash.
- source: §Abstract "It utilizes logging of meta-data to obtain good performance, and to restart quickly after a crash."
- stated: stated

### grok:G4
- guarantee: All meta-data updates are recorded in the aggregate's transaction log.
- source: §"Data Architecture" "updates are recorded in this log. The log is processed as a circular bu er of disk blocks, with the tail of"
- stated: stated

### grok:G5
- guarantee: The log is processed as a circular buffer of disk blocks whose in-memory tail is forced to disk only when necessary.
- source: §"Data Architecture" "the log stored in memory and forced to disk only when necessary. The log is not actually constrained to"
- stated: stated

### grok:G6
- guarantee: The log need not reside on the same aggregate as the data it logs.
- source: §"Data Architecture" "be on the same aggregate as the data that it is logging, but this restriction is currently imposed by our"
- stated: stated

### grok:G7
- guarantee: Under normal operation the log container does not grow or shrink.
- source: §"Data Architecture" "The log container does not grow or shrink"
- stated: stated

### grok:G8
- guarantee: The log/buffer package mediates all buffer modifications so they can be logged.
- source: §"Component Architecture" "mediates all bu er modi cations so that they can be logged as required by the logging strategy employed"
- stated: stated

### grok:G9
- guarantee: All meta-data updates are grouped into atomic transactions: if a transaction commits, every update in it is applied; if it aborts, none is applied.
- source: §"Component Architecture" "that either all the updates within a transaction (if a transaction commits), or none of them (if a transaction"
- stated: stated

### grok:G10
- guarantee: Making all file-system meta-data modifications inside atomic transactions lets recovery restore the file system to a consistent state after a crash.
- source: §"Component Architecture" " le system can be restored to a consistent state after a crash."
- stated: stated

### grok:G11
- guarantee: For every update to file-system meta-data, the log stores both the original value and the new value of the updated data.
- source: §"Component Architecture" "made to any le system meta-data, both the original and new values of the updated data. Furthermore,"
- stated: stated

### grok:G12
- guarantee: Before the buffer package writes any dirty meta-data buffer back to disk, it writes that buffer's log entries to disk.
- source: §"Component Architecture" "before the bu er package allows any dirty meta-data bu er to be written back out to the disk, it writes"
- stated: stated

### grok:G13
- guarantee: If a transaction aborted, the log contains enough information to undo all of its meta-data updates and restore the meta-data to its state before the transaction started.
- source: §"Component Architecture" "the log to undo all of the updates made to the meta-data, and restore the meta-data to its state before the"
- stated: stated

### grok:G14
- guarantee: If a transaction committed, the log contains enough information to redo all of its meta-data updates, including those that had not yet reached disk from the buffers.
- source: §"Component Architecture" "meta-data updates, even those that hadn't yet made it from the disk bu ers to the disk."
- stated: stated

### grok:G15
- guarantee: After a crash, recovery replays committed transactions and undoes uncommitted transactions, restoring the file system to a consistent state.
- source: §"Component Architecture" "uncommitted transactions, and thus restoring the le system to a consistent state. Since the log only"
- stated: stated

### grok:G16
- guarantee: The log contains only information describing transactions still in progress, so recovery time is proportional to activity at the time of the crash and not to disk size.
- source: §"Component Architecture" "contains information describing transactions still in progress, recovery time is proportional to the activity"
- stated: stated

### grok:G17
- guarantee: Replaying the log runs orders of magnitude faster than BSD fsck.
- source: §"Component Architecture" "at the time of the crash, not to the size of the disk. The result is that the log-replaying operation runs orders"
- stated: stated

### grok:G18
- guarantee: When hard I/O errors occur while updating critical meta-data, recovery cannot regenerate a consistent file system and the salvager must be run.
- source: §"Component Architecture" "can not regenerate a consistent le system, however, such as when hard I/O errors occur while updating"
- stated: stated

### grok:G19
- guarantee: A transaction may acquire a lock when it needs it and drop the lock as soon as it has finished using the object, without waiting for the transaction to end.
- source: §"Logging Architecture" "and drop them as soon as they are nished using them, rather than waiting for the transaction's end. This"
- stated: stated

### grok:G20
- guarantee: If a crash intervenes, Episode aborts transactions that might otherwise have been able to commit, rather than letting another transaction make uncommitted data permanent.
- source: §"Logging Architecture" "have otherwise been able to commit, if a crash intervenes. Speci cally, all active transactions that lock the"
- stated: stated

### grok:G21
- guarantee: All active transactions that lock the same object during their lifetime are merged into one equivalence class.
- source: §"Logging Architecture" "same object during their lifetime are merged into an equivalence class (EC). An EC has the property that"
- stated: stated

### grok:G22
- guarantee: Either every transaction in an equivalence class commits, or none of them does.
- source: §"Logging Architecture" "either all of its transactions commit or none do.3 In the example above, transaction 1 and 2 would form"
- stated: stated

### grok:G23
- guarantee: If the system crashes before every transaction in an equivalence class has committed, every transaction in that class is aborted.
- source: §"Logging Architecture" "the EC are aborted. It is therefore desirable to minimize the duration and the number of ECs formed in the"
- stated: stated

### grok:G24
- guarantee: The logging system guarantees consistency of the file system.
- source: §"Logging Architecture" "The primary goal of the logging system in Episode is to guarantee the consistency of the le system."
- stated: stated

### grok:G25
- guarantee: Meta-data changes to disk may be deferred unless an operation such as fsync requests otherwise.
- source: §"Logging Architecture" "Meta-data changes to the disk itself can often be deferred, unless speci cally requested by an oper-"
- stated: stated

### grok:G26
- guarantee: File-system consistency does not require that on-disk meta-data be current with in-memory updates.
- source: §"Logging Architecture" "ation like fsync. Consistency of the le system doesn't require that the system be current."
- stated: stated

### grok:G27
- guarantee: The log and recovery give no transactional guarantees about user data.
- source: §"Logging Architecture" "No transactional guarantees are required about the user-data, since consistency of the le system"
- stated: stated

### grok:G28
- guarantee: Episode logs only meta-data changes.
- source: §"Logging Architecture" "requires only that the meta-data be consistent. Episode logs only meta-data changes. Although restricting"
- stated: stated

### grok:G29
- guarantee: If a crash occurs after a block is allocated to a file and before the first write to that block, and the special allocation transaction aborts, recovery zeroes the contents of the block.
- source: §"Logging Architecture" "transaction zeroes the contents of the block."
- stated: stated

### grok:G30
- guarantee: Transaction sizes are bounded when they begin, and running transactions never exceed the space available in the log.
- source: §"Logging Architecture" "exceed the space available in the log. Transactions that run too long or modify too much data represent"
- stated: stated

### grok:G31
- guarantee: Because the log holds old and new values, a dirty meta-data buffer may be written to its home on disk before its transaction commits.
- source: §"Logging Architecture" "bu ers from the end of transactions, at the expense of having to write more data to the log."
- stated: stated

### grok:G32
- guarantee: After each bounded transaction that makes up a larger operation, the file system is consistent, even if it is not yet in the final desired state.
- source: §"Logging Architecture" "not in the nal desired state."
- stated: stated

### grok:G33
- guarantee: Meta-data updates are batched into writes to the file-system log.
- source: §"Performance" "considerably faster than BSD's because Episode batches meta-data updates into writes to the le system"
- stated: stated

### grok:G34
- guarantee: Recovery time depends primarily on the size of the active portion of the transaction log.
- source: §"Recovery Time" "Episode's time to recover depends primarily on the size of the active portion of transaction log. The"
- stated: stated

### grok:G35
- guarantee: The active portion of the log includes all uncommitted transactions, which must be undone after a crash.
- source: §"Recovery Time" "of the uncommitted transactions, since these must be undone in the event of a crash. The active portion"
- stated: stated

### grok:G36
- guarantee: The active portion of the log also includes committed updates whose dirty meta-data blocks still reside only in the buffer cache.
- source: §"Recovery Time" "modi ed by committed transactions. In this case, the updates are in the log and only in the log, requiring"
- stated: stated

### grok:G37
- guarantee: Checkpointing writes buffers modified by committed transactions and discards those log portions no longer required to make those transactions permanent.
- source: §"Recovery Time" "transactions is generally called checkpointing the log."
- stated: stated

### grok:G38
- guarantee: Episode will not permit the log to become full.
- source: §"Recovery Time" "permit the log to become full, but it is dicult to guarantee any other bound on the size of the active"
- stated: stated

### grok:G39
- guarantee: Recovery takes essentially the same amount of time on small and large aggregates.
- source: §"Recovery Time" "From this data, we can see that recovery takes essentially the same amount of time on"
- stated: stated

### grok:G40
- guarantee: Recovery time does not depend on aggregate size.
- source: §"Recovery Time" "none of which, however, are the aggregate size. Despite this complexity, it also appears that in typical"
- stated: stated

### grok:G41
- guarantee: In typical configurations, recovery times are under 30 seconds.
- source: §"Recovery Time" "con gurations, recovery times will be under 30 seconds."
- stated: stated

### grok:G42
- guarantee: Logging permits Episode to batch repetitive meta-data updates, reducing cumulative disk traffic.
- source: §"Conclusions" "updating operations and reduced the cumulative disk trac by permitting Episode to batch repetitive"
- stated: stated

### grok:G43
- guarantee: Each fragment is marked logged or unlogged, and reusing a logged block as an unlogged block (or the reverse) requires buffer-pool operations that keep the two classes distinct.
- source: §"Data Architecture" "tion is necessary because certain bu er pool operations have to be performed when reusing a logged block"
- stated: stated

### grok:G44
- guarantee: In the kernel, elbr_Recover does not recover a dirty log; it returns RCVR_MUSTRCVR.
- source: logbuf/recover.c:2374 "return RCVR_MUSTRCVR; /* no kernel recovery anymore */"
- stated: stated

### grok:G45
- guarantee: User-space recovery marks a transaction REDO if an end record is seen (whether or not a begin is seen) and UNDO if a begin is seen and no end is seen.
- source: logbuf/recover.h:80 " * Begin seen REDO UNDO"
- stated: stated

### grok:G46
- guarantee: User-space recovery fails if it finds a transaction that has neither a begin nor an end in the active log.
- source: logbuf/recover.h:81 " * Begin not seen REDO <fail>"
- stated: stated

### grok:G47
- guarantee: After successful user-space recovery, a checkpoint record is written on the next log page and a restart record is written on the first log block with the pass number increased by two.
- source: logbuf/recover.c:543 " * we increase the pass # to allow for an Episode crash immediately"
- stated: stated

### grok:G48
- guarantee: A log is clean, and recovery is not required, if and only if the first log block's page header has the salvage magic number and its first record is a restart record.
- source: logbuf/recover.c:2760 " * returns 0 if not clean (needs recovery), 1 if clean."
- stated: stated

### grok:G49
- guarantee: Log initialization refuses to attach a dirty log until recovery has run: if the restart block is not clean it calls recovery and, on success, returns RCVR_RECOVERED.
- source: logbuf/log.c:733 " if (elbr_GetCleanLogInfo(ldP, *logLocnArray, &myLogHdr) == 0) {"
- stated: stated

### grok:G50
- guarantee: After recovery returns RCVR_RECOVERED, the buffer pool for that device is invalidated.
- source: logbuf/buffer.c:1837 " /* log recovered, we invalidate the buffer pool by"
- stated: stated

### grok:G51
- guarantee: After successful recovery the log is clean.
- source: anode/aggregate.c:2405 " /* By definition the log is now clean. */"
- stated: stated

### grok:G52
- guarantee: A clean shutdown writes a checkpoint block and then a restart block, and does not return until pending transactions on that device are complete.
- source: logbuf/buffer.c:2581 " * Close the log; this waits until all pending transactions are complete."
- stated: stated

### grok:G53
- guarantee: A transaction is committed only once its last log record has been written to disk, not merely when the transaction has ended in memory.
- source: logbuf/log.c:2259 " * elbl_IsTranCommitted -- check to see if the last record of this transaction"
- stated: stated

### grok:G54
- guarantee: Completed transactions are held until their end records are committed to disk, and only then are they garbage-collected.
- source: logbuf/log.c:140 " * The transactions on the cTranList are being held until their end records are"
- stated: stated

### grok:G55
- guarantee: elbb_LogForce with waitOK 1 does not return until the transaction has committed, which makes updates done under that transaction persistent.
- source: logbuf/tran.c:950 " * 1 -- don't return until transaction has committed. This guarantees"
- stated: stated

### grok:G56
- guarantee: elbb_LogForce with waitOK 2 does not return until the transaction has completed, which serializes it with any transaction started after the call returns.
- source: logbuf/tran.c:953 " * 2 -- don't return until transaction has completed. This ensures"
- stated: stated

### grok:G57
- guarantee: elbb_QuiesceSystem with SERIALIZE returns only after every transaction that was active at the start of the call has ended.
- source: logbuf/logbuf.p.h:332 " * SERIALIZE -- ensure all currently active trans have ended."
- stated: stated

### grok:G58
- guarantee: elbb_QuiesceSystem with COMMIT returns only after every such transaction has committed.
- source: logbuf/logbuf.p.h:333 " * COMMIT -- as above but wait until all trans have committed."
- stated: stated

### grok:G59
- guarantee: elbb_QuiesceSystem with WRITE schedules all dirty user-data buffers; with FSYNC it also waits for those writes; with FLUSH it also invalidates user buffers; with FLUSHALL it invalidates all buffers.
- source: logbuf/logbuf.p.h:335 " * WRITE -- schedules all dirty buffers containing user data."
- stated: stated

### grok:G60
- guarantee: Before a dirty buffer on the log age queue is written, the log is forced at least through that buffer's last log record.
- source: logbuf/buffer.c:3769 " /* maybe force write log */"
- stated: implied

### grok:G61
- guarantee: After that log force, elbl_ForceBuffer has made the buffer's log records committed on disk.
- source: logbuf/log.c:2125 " afsl_Assert (BufCommitted (lmP, bP));"
- stated: implied

### grok:G62
- guarantee: Equivalence-class ends are written atomically: the head transaction writes a BEND record for each member and then its own END, and recovery reconstitutes those member END records only if the head transaction is REDO.
- source: logbuf/recover.c:1687 " * Bulk ends are the recovery end of ECs. Because the end records must"
- stated: stated

### grok:G63
- guarantee: Until the last member of an equivalence class ends, every earlier member is only pending and has no END record on disk.
- source: logbuf/tran.c:447 " /* This tran is part of an EC but we are not the last. Just mark"
- stated: stated

### grok:G64
- guarantee: A committed undo-zero fill of zeroes is a kill record: recovery marks every earlier recoverable record on that same disk block SKIP, and those earlier records must have been REDO.
- source: logbuf/recover.h:83 " * Records (not whole transactions) are marked SKIP if they predate a kill"
- stated: stated

### grok:G65
- guarantee: Recovery raises RCVR_USERDATA if it sees an uncommitted kill after ordinary records on the same block.
- source: logbuf/recover.c:1907 " RECVR_RAISE (RCVR_USERDATA);"
- stated: stated

### grok:G66
- guarantee: Recovery raises RCVR_METADATA if it sees an uncommitted recoverable record that a later kill would have skipped.
- source: logbuf/recover.c:1915 " RECVR_RAISE (RCVR_METADATA);"
- stated: stated

### grok:G67
- guarantee: For each data block, recovery applies undo records newest-first, then redo records oldest-first, then writes the block back only if it actually read it.
- source: logbuf/recover.c:1970 " * To actually perform the recovery we must make two passes."
- stated: stated

### grok:G68
- guarantee: Redo of a recoverable record copies or fills from the record's new data; if the record has no new data, redo is a no-op.
- source: logbuf/recover.c:2068 " /* if there is no new data, redo is a no-op */"
- stated: stated

### grok:G69
- guarantee: Undo of a recoverable record copies or fills from the record's old data; if the record has no old data, undo is a no-op.
- source: logbuf/recover.c:2115 " /* if there is no old data, undo is a no-op */"
- stated: stated

### grok:G70
- guarantee: A data log record may be split across log pages; fill, end, and other non-data types are not split.
- source: logbuf/logrec.h:188 " * is a data record."
- stated: stated

### grok:G71
- guarantee: Each log page other than a restart-only page carries a checksum; the default algorithm is CRC-32 over the whole page.
- source: logbuf/logrec.h:114 "#define LOGREC_CKSUMVER_DEFAULT LOGREC_CKSUMVER_CRC32_STD_ALL"
- stated: stated

### grok:G72
- guarantee: A log page that contains only a restart record is written without a checksum.
- source: logbuf/recover.c:2738 " * We choose not to checksum the log page containing a restart record"
- stated: stated

### grok:G73
- guarantee: The log page header, including checksum, occupies the first sector, and recovery relies on sector atomicity: a page that was not written keeps an earlier pass number and is ignored as head.
- source: logbuf/recover.c:745 " * sector for the log page and we can rely on"
- stated: stated

### grok:G74
- guarantee: Recovery does not assume in-order writes; it uses the head page's io_window to check in-transit pages and pulls the head back to the page before the oldest invalid in-transit page.
- source: logbuf/recover.c:888 " * out to disk. Because we don't assume writes are in order, we"
- stated: stated

### grok:G75
- guarantee: If an in-transit log page did not reach disk, recovery may safely move the head further back: no on-disk change that must be undone can be missing from the log that is on disk.
- source: logbuf/recover.c:897 " * cannot be any changes on disk we must undo that aren't in the"
- stated: stated

### grok:G76
- guarantee: A checksum error on an active log page outside the in-transit window makes recovery fail with RCVR_IOERR, leaving the salvager as the remaining recourse.
- source: logbuf/recover.c:1043 " * Only resort is to run salvager"
- stated: stated

### grok:G77
- guarantee: Pass number 0 is unused on an active log page; a newly initialized log uses pass 0, and incrementing a pass number skips 0.
- source: logbuf/recover.c:770 " * A newly initialized log has pass # 0 written into"
- stated: stated

### grok:G78
- guarantee: Every log page header carries salvage magic 0x73697045; a page without that magic is treated as a damaged log.
- source: logbuf/recover.h:44 "#define LOG_SALVAGE_MAGIC_NUMBER (0x73697045)"
- stated: stated

### grok:G79
- guarantee: The package panics rather than overwrite the log if it cannot keep the active region strictly smaller than the log.
- source: logbuf/log.c:2907 " * Better a good panic than to have the log overwritten,"
- stated: stated

### grok:G80
- guarantee: Starting a non-forced transaction or writing a log record fails with LOG_LOGFULL when the active log plus a reserved buffer of pages would exceed the log.
- source: logbuf/log.c:287 " ((lmP->activeSize + LOG_FULL_BUFFER) > lmP->logLocnArraySize)"
- stated: implied

### grok:G81
- guarantee: A nested (undo-zero) transaction may be started even when the log is full; the caller guarantees that nested size plus the parent still fits in one transaction reservation.
- source: logbuf/log.c:1672 " * If the force option is set we proceed regardless of the available"
- stated: stated

### grok:G82
- guarantee: Log space is reserved as (active transactions times full or undo-zero size) plus (pending transactions times end-record size).
- source: logbuf/log.c:138 " * length(aTranList) * (nested ? undoSize : fullSize) +"
- stated: stated

### grok:G83
- guarantee: The tail of the log is pinned by the oldest active or pending transaction on the transaction age queue and by the oldest dirty logged buffer on the buffer age queue.
- source: logbuf/log.c:136 " * The result of this is that the tranAgeQ is used to pin the tail of the log."
- stated: stated

### grok:G84
- guarantee: If a transaction identifier is unknown or the transaction record has been freed, callers treating it as committed are correct.
- source: logbuf/tran.c:919 " return BUF_TRANCOMMIT;"
- stated: implied

### grok:G85
- guarantee: elbb_Kill will not discard a dirty logged buffer unless metadataOK is true, which is allowed only after the transaction that freed that meta-data block has committed.
- source: logbuf/buffer.c:1359 " * metadataOK is true if it is safe to kill dirty metadata"
- stated: stated

### grok:G86
- guarantee: An unrecoverable EIO on a logged (meta-data) buffer panics.
- source: logbuf/buffer.c:4413 " if (bufferIsLogged(bP) && ((code) == EIO))"
- stated: stated

### grok:G87
- guarantee: User data is never logged.
- source: logbuf/buffer.c:1702 " * from the same address space. Since user data is never logged, we"
- stated: stated

### grok:G88
- guarantee: elbb_Release with elbb_sync does not return until the log (if needed) and the data buffer have both been written.
- source: logbuf/logbuf.p.h:66 " elbb_sync, /* force write log, force write data buffer, upon return"
- stated: stated

### grok:G89
- guarantee: elbb_Release with elbb_syncLog forces the log through the buffer's last record, schedules the buffer write, and does not wait for that data write.
- source: logbuf/logbuf.p.h:64 " elbb_syncLog, /* force write log, schedule buffer write, don't wait"
- stated: stated

### grok:G90
- guarantee: elbb_UndoZero appends old-fill-of-zero records to an existing transaction for a byte range, covering I/O that does not use the buffer system.
- source: logbuf/buffer.c:2414 " * elbb_UndoZero - Adds an undo-zero record to an existing transaction for"
- stated: stated

### grok:G91
- guarantee: elbb_UndoZeroBuffer starts a nested transaction, attaches it to the dirty buffer, logs an old-fill-of-zero, and that transaction is ended when the buffer is no longer dirty.
- source: logbuf/buffer.c:2457 " * elbb_UndoZeroBuffer -- Adds an undo-zero record for the specified buffer. A"
- stated: stated

### grok:G92
- guarantee: When a buffer is cleaned, an attached undo-zero transaction may be ended and the buffer removed from the age queue even if those undo-zero log records have not yet committed.
- source: logbuf/buffer.c:339 " * If this is an undo zero buffer then the log records may not have"
- stated: stated

### grok:G93
- guarantee: A bona fide meta-data buffer is removed from the age queue only after its updates have committed: either the log was forced before the write, or the freeing transaction was committed before a kill.
- source: logbuf/buffer.c:345 " * In the case of bona fide metadata buffers updates to those buffer must"
- stated: stated

### grok:G94
- guarantee: Recovery code takes no locks and may recover more than one log at a time.
- source: logbuf/recover.c:101 " * Locking is no longer done in this package; all code should be thread-safe"
- stated: stated

### grok:G95
- guarantee: The smallest usable log is load times the per-transaction reservation, plus LOG_FULL_BUFFER, plus one page.
- source: logbuf/log.c:848 " minSize = (load * elbl_MinTranReservation(dP->blkSize)) +"
- stated: stated

### grok:G96
- guarantee: The log is given at least LOGREC_MAX_BUFFERS (5) pages, which is the number of in-transit pages recovery will verify.
- source: logbuf/logrec.h:53 " * this defines the number of pages the recovery package will verify have"
- stated: stated

### grok:G97
- guarantee: A logged modification writes the log record and then copies the new data into the buffer, leaving the buffer dirty.
- source: logbuf/buffer.c:1455 " if (logRequest) {"
- stated: implied

### grok:G98
- guarantee: elbb_Initialize logs only the new contents of a CreateBlock buffer (no old data).
- source: logbuf/buffer.c:1588 " * By initialization, we mean modification in the case where the old data"
- stated: stated

### grok:G99
- guarantee: elbb_Fill with saveOld logs the old data and then a new-fill record, all in the same transaction, so the fill may be split into chunks.
- source: logbuf/buffer.c:1542 " * A single call here can always be divided into chunks because of"
- stated: stated

### grok:G100
- guarantee: Starting a transaction with a non-null oldTranId starts a nested transaction and does not block waiting for log space.
- source: logbuf/buffer.c:1739 " * By providing an old transaction ID, this call will not block. If there"
- stated: stated

### grok:G101
- guarantee: elbb_StartTran without an old transaction retries, including log-full handling, until it obtains a transaction (except during a bounded kernel-panic loop).
- source: logbuf/buffer.c:1743 " * If this routine fails to allocate a transaction we presume it is because"
- stated: implied

### grok:G102
- guarantee: Recovery walks log records in increasing LSN order.
- source: logbuf/recover.c:1633 " * we must guarantee our transactions remain time-ordered."
- stated: stated

### grok:G103
- guarantee: The null transaction identifier is never issued to a live transaction; restart and checkpoint records may use it.
- source: logbuf/recover.c:1656 " /* we don't use the zero transaction id - but we allow it for a restart"
- stated: stated

### grok:G104
- guarantee: elbb_FsyncForce writes the tagged or listed buffers, forcing the log as needed for any logged buffer among them.
- source: logbuf/buffer.c:2018 " * elbb_FsyncForce -- implements fsync using two basic methods of specifying"
- stated: implied

### grok:G105
- guarantee: elbb_SyncForce schedules writes of dirty buffers and does not wait for those writes to complete.
- source: logbuf/buffer.c:2166 " * For sync, we do not want to wait. We walk through the entire hash"
- stated: stated

### grok:G106
- guarantee: On a logged modify, fill, or initialize, if the write leaves the log in a log-full state, HandleLogFull is invoked before the call returns.
- source: logbuf/buffer.c:1489 " if (logRequest && logFullState)"
- stated: implied

### grok:G107
- guarantee: Create of a new log zeroes every page but the first and writes a restart record on the first log block.
- source: logbuf/log.c:904 " * We skip the first block because we will be writing a restart"
- stated: stated

### grok:G108
- guarantee: Each log record carries a monotonically increasing LSN that skips zero.
- source: logbuf/log.c:355 " (lmP)->lsn = (++((lmP)->lsn) ? (lmP)->lsn : ++((lmP)->lsn)); \"
- stated: implied

### grok:G109
- guarantee: Recoverable record types are data and fill records with old data, new data, or both; end, checkpoint, restart, debug, flush, and bend records are not applied as data updates.
- source: logbuf/logrec.h:167 " ((type) == LOGREC_NFILL))"
- stated: implied

### grok:G110
- guarantee: If recovery must raise an error, it unwinds and returns a recovery error code rather than panicking, except for a few allocation and dump firewalls.
- source: logbuf/recover.c:385 " * This routine must be *very* paranoid about failure. It is better"
- stated: stated

### grok:G111
- guarantee: Nested undo-zero transactions are logically ordered after the allocation transaction that created them, even though they are not merged into that transaction's equivalence class.
- source: logbuf/log.c:1678 " * This is dangerous, but necessary to cascade UndoZero transactions with"
- stated: stated

### grok:G112
- guarantee: Quiesce without stopping the system waits only for transactions older than the log position sampled at the start of the call, so later activity may continue concurrently.
- source: logbuf/tran.c:1217 " * Quiescing without stopping the system works by waiting for all currently"
- stated: stated

