# Log and recovery guarantees (Episode)

### G1
- guarantee: After a crash, file-system meta-data (directories, allocation bitmaps, indirect blocks, and anode tables) are consistent.
- source: §"Background" "guarantee that after a crash, the le system meta-data (directories, allocation bitmaps, indirect blocks and"
- stated: stated

### G2
- guarantee: After a crash, recovery generally eliminates the need to run fsck.
- source: §"Background" "anode tables) are consistent, generally eliminating the need for running \fsck."
- stated: stated

### G3
- guarantee: Logging of meta-data makes the file system restart quickly after a crash.
- source: §Abstract "It utilizes logging of meta-data to obtain good performance, and to restart quickly after a crash."
- stated: stated

### G4
- guarantee: All meta-data updates are recorded in the aggregate's transaction log.
- source: §"Data Architecture" "updates are recorded in this log. The log is processed as a circular bu er of disk blocks, with the tail of"
- stated: stated

### G5
- guarantee: The log is processed as a circular buffer of disk blocks whose in-memory tail is forced to disk only when necessary.
- source: §"Data Architecture" "the log stored in memory and forced to disk only when necessary. The log is not actually constrained to"
- stated: stated

### G6
- guarantee: The log need not reside on the same aggregate as the data it logs.
- source: §"Data Architecture" "be on the same aggregate as the data that it is logging, but this restriction is currently imposed by our"
- stated: stated

### G7
- guarantee: Under normal operation the log container does not grow or shrink.
- source: §"Data Architecture" "The log container does not grow or shrink"
- stated: stated

### G8
- guarantee: The log/buffer package mediates all buffer modifications so they can be logged.
- source: §"Component Architecture" "mediates all bu er modi cations so that they can be logged as required by the logging strategy employed"
- stated: stated

### G9
- guarantee: All meta-data updates are grouped into atomic transactions: if a transaction commits, every update in it is applied; if it aborts, none is applied.
- source: §"Component Architecture" "that either all the updates within a transaction (if a transaction commits), or none of them (if a transaction"
- stated: stated

### G10
- guarantee: Making all file-system meta-data modifications inside atomic transactions lets recovery restore the file system to a consistent state after a crash.
- source: §"Component Architecture" " le system can be restored to a consistent state after a crash."
- stated: stated

### G11
- guarantee: For every update to file-system meta-data, the log stores both the original value and the new value of the updated data.
- source: §"Component Architecture" "made to any le system meta-data, both the original and new values of the updated data. Furthermore,"
- stated: stated

### G12
- guarantee: Before the buffer package writes any dirty meta-data buffer back to disk, it writes that buffer's log entries to disk.
- source: §"Component Architecture" "before the bu er package allows any dirty meta-data bu er to be written back out to the disk, it writes"
- stated: stated

### G13
- guarantee: If a transaction aborted, the log contains enough information to undo all of its meta-data updates and restore the meta-data to its state before the transaction started.
- source: §"Component Architecture" "the log to undo all of the updates made to the meta-data, and restore the meta-data to its state before the"
- stated: stated

### G14
- guarantee: If a transaction committed, the log contains enough information to redo all of its meta-data updates, including those that had not yet reached disk from the buffers.
- source: §"Component Architecture" "meta-data updates, even those that hadn't yet made it from the disk bu ers to the disk."
- stated: stated

### G15
- guarantee: After a crash, recovery replays committed transactions and undoes uncommitted transactions, restoring the file system to a consistent state.
- source: §"Component Architecture" "uncommitted transactions, and thus restoring the le system to a consistent state. Since the log only"
- stated: stated

### G16
- guarantee: The log contains only information describing transactions still in progress, so recovery time is proportional to activity at the time of the crash and not to disk size.
- source: §"Component Architecture" "contains information describing transactions still in progress, recovery time is proportional to the activity"
- stated: stated

### G17
- guarantee: Replaying the log runs orders of magnitude faster than BSD fsck.
- source: §"Component Architecture" "at the time of the crash, not to the size of the disk. The result is that the log-replaying operation runs orders"
- stated: stated

### G18
- guarantee: When hard I/O errors occur while updating critical meta-data, recovery cannot regenerate a consistent file system and the salvager must be run.
- source: §"Component Architecture" "can not regenerate a consistent le system, however, such as when hard I/O errors occur while updating"
- stated: stated

### G19
- guarantee: A transaction may acquire a lock when it needs it and drop the lock as soon as it has finished using the object, without waiting for the transaction to end.
- source: §"Logging Architecture" "and drop them as soon as they are nished using them, rather than waiting for the transaction's end. This"
- stated: stated

### G20
- guarantee: If a crash intervenes, Episode aborts transactions that might otherwise have been able to commit, rather than letting another transaction make uncommitted data permanent.
- source: §"Logging Architecture" "have otherwise been able to commit, if a crash intervenes. Speci cally, all active transactions that lock the"
- stated: stated

### G21
- guarantee: All active transactions that lock the same object during their lifetime are merged into one equivalence class.
- source: §"Logging Architecture" "same object during their lifetime are merged into an equivalence class (EC). An EC has the property that"
- stated: stated

### G22
- guarantee: Either every transaction in an equivalence class commits, or none of them does.
- source: §"Logging Architecture" "either all of its transactions commit or none do.3 In the example above, transaction 1 and 2 would form"
- stated: stated

### G23
- guarantee: If the system crashes before every transaction in an equivalence class has committed, every transaction in that class is aborted.
- source: §"Logging Architecture" "the EC are aborted. It is therefore desirable to minimize the duration and the number of ECs formed in the"
- stated: stated

### G24
- guarantee: The logging system guarantees consistency of the file system.
- source: §"Logging Architecture" "The primary goal of the logging system in Episode is to guarantee the consistency of the le system."
- stated: stated

### G25
- guarantee: Meta-data changes to disk may be deferred unless an operation such as fsync requests otherwise.
- source: §"Logging Architecture" "Meta-data changes to the disk itself can often be deferred, unless speci cally requested by an oper-"
- stated: stated

### G26
- guarantee: File-system consistency does not require that on-disk meta-data be current with in-memory updates.
- source: §"Logging Architecture" "ation like fsync. Consistency of the le system doesn't require that the system be current."
- stated: stated

### G27
- guarantee: The log and recovery give no transactional guarantees about user data.
- source: §"Logging Architecture" "No transactional guarantees are required about the user-data, since consistency of the le system"
- stated: stated

### G28
- guarantee: Episode logs only meta-data changes.
- source: §"Logging Architecture" "requires only that the meta-data be consistent. Episode logs only meta-data changes. Although restricting"
- stated: stated

### G29
- guarantee: If a crash occurs after a block is allocated to a file and before the first write to that block, and the special allocation transaction aborts, recovery zeroes the contents of the block.
- source: §"Logging Architecture" "transaction zeroes the contents of the block."
- stated: stated

### G30
- guarantee: Transaction sizes are bounded when they begin, and running transactions never exceed the space available in the log.
- source: §"Logging Architecture" "exceed the space available in the log. Transactions that run too long or modify too much data represent"
- stated: stated

### G31
- guarantee: Because the log holds old and new values, a dirty meta-data buffer may be written to its home on disk before its transaction commits.
- source: §"Logging Architecture" "bu ers from the end of transactions, at the expense of having to write more data to the log."
- stated: stated

### G32
- guarantee: After each bounded transaction that makes up a larger operation, the file system is consistent, even if it is not yet in the final desired state.
- source: §"Logging Architecture" "not in the nal desired state."
- stated: stated

### G33
- guarantee: Meta-data updates are batched into writes to the file-system log.
- source: §"Performance" "considerably faster than BSD's because Episode batches meta-data updates into writes to the le system"
- stated: stated

### G34
- guarantee: Recovery time depends primarily on the size of the active portion of the transaction log.
- source: §"Recovery Time" "Episode's time to recover depends primarily on the size of the active portion of transaction log. The"
- stated: stated

### G35
- guarantee: The active portion of the log includes all uncommitted transactions, which must be undone after a crash.
- source: §"Recovery Time" "of the uncommitted transactions, since these must be undone in the event of a crash. The active portion"
- stated: stated

### G36
- guarantee: The active portion of the log also includes committed updates whose dirty meta-data blocks still reside only in the buffer cache.
- source: §"Recovery Time" "modi ed by committed transactions. In this case, the updates are in the log and only in the log, requiring"
- stated: stated

### G37
- guarantee: Checkpointing writes buffers modified by committed transactions and discards those log portions no longer required to make those transactions permanent.
- source: §"Recovery Time" "transactions is generally called checkpointing the log."
- stated: stated

### G38
- guarantee: Episode will not permit the log to become full.
- source: §"Recovery Time" "permit the log to become full, but it is dicult to guarantee any other bound on the size of the active"
- stated: stated

### G39
- guarantee: Recovery takes essentially the same amount of time on small and large aggregates.
- source: §"Recovery Time" "From this data, we can see that recovery takes essentially the same amount of time on"
- stated: stated

### G40
- guarantee: Recovery time does not depend on aggregate size.
- source: §"Recovery Time" "none of which, however, are the aggregate size. Despite this complexity, it also appears that in typical"
- stated: stated

### G41
- guarantee: In typical configurations, recovery times are under 30 seconds.
- source: §"Recovery Time" "con gurations, recovery times will be under 30 seconds."
- stated: stated

### G42
- guarantee: Logging permits Episode to batch repetitive meta-data updates, reducing cumulative disk traffic.
- source: §"Conclusions" "updating operations and reduced the cumulative disk trac by permitting Episode to batch repetitive"
- stated: stated

### G43
- guarantee: Each fragment is marked logged or unlogged, and reusing a logged block as an unlogged block (or the reverse) requires buffer-pool operations that keep the two classes distinct.
- source: §"Data Architecture" "tion is necessary because certain bu er pool operations have to be performed when reusing a logged block"
- stated: stated

### G44
- guarantee: In the kernel, elbr_Recover does not recover a dirty log; it returns RCVR_MUSTRCVR.
- source: logbuf/recover.c:2374 "return RCVR_MUSTRCVR; /* no kernel recovery anymore */"
- stated: stated

### G45
- guarantee: User-space recovery marks a transaction REDO if an end record is seen (whether or not a begin is seen) and UNDO if a begin is seen and no end is seen.
- source: logbuf/recover.h:80 " * Begin seen        REDO       UNDO"
- stated: stated

### G46
- guarantee: User-space recovery fails if it finds a transaction that has neither a begin nor an end in the active log.
- source: logbuf/recover.h:81 " * Begin not seen    REDO       <fail>"
- stated: stated

### G47
- guarantee: After successful user-space recovery, a checkpoint record is written on the next log page and a restart record is written on the first log block with the pass number increased by two.
- source: logbuf/recover.c:543 " * we increase the pass # to allow for an Episode crash immediately"
- stated: stated

### G48
- guarantee: A log is clean, and recovery is not required, if and only if the first log block's page header has the salvage magic number and its first record is a restart record.
- source: logbuf/recover.c:2760 " * returns 0 if not clean (needs recovery), 1 if clean."
- stated: stated

### G49
- guarantee: Log initialization refuses to attach a dirty log until recovery has run: if the restart block is not clean it calls recovery and, on success, returns RCVR_RECOVERED.
- source: logbuf/log.c:733 "      if (elbr_GetCleanLogInfo(ldP, *logLocnArray, &myLogHdr) == 0) {"
- stated: stated

### G50
- guarantee: After recovery returns RCVR_RECOVERED, the buffer pool for that device is invalidated.
- source: logbuf/buffer.c:1837 "	      /* log recovered, we invalidate the buffer pool by"
- stated: stated

### G51
- guarantee: After successful recovery the log is clean.
- source: anode/aggregate.c:2405 "		    /* By definition the log is now clean. */"
- stated: stated

### G52
- guarantee: A clean shutdown writes a checkpoint block and then a restart block, and does not return until pending transactions on that device are complete.
- source: logbuf/buffer.c:2581 "       * Close the log; this waits until all pending transactions are complete."
- stated: stated

### G53
- guarantee: A transaction is committed only once its last log record has been written to disk, not merely when the transaction has ended in memory.
- source: logbuf/log.c:2259 " * elbl_IsTranCommitted -- check to see if the last record of this transaction"
- stated: stated

### G54
- guarantee: Completed transactions are held until their end records are committed to disk, and only then are they garbage-collected.
- source: logbuf/log.c:140 " * The transactions on the cTranList are being held until their end records are"
- stated: stated

### G55
- guarantee: elbb_LogForce with waitOK 1 does not return until the transaction has committed, which makes updates done under that transaction persistent.
- source: logbuf/tran.c:950 " *     1 -- don't return until transaction has committed.  This guarantees"
- stated: stated

### G56
- guarantee: elbb_LogForce with waitOK 2 does not return until the transaction has completed, which serializes it with any transaction started after the call returns.
- source: logbuf/tran.c:953 " *     2 -- don't return until transaction has completed.  This ensures"
- stated: stated

### G57
- guarantee: elbb_QuiesceSystem with SERIALIZE returns only after every transaction that was active at the start of the call has ended.
- source: logbuf/logbuf.p.h:332 " *             SERIALIZE -- ensure all currently active trans have ended."
- stated: stated

### G58
- guarantee: elbb_QuiesceSystem with COMMIT returns only after every such transaction has committed.
- source: logbuf/logbuf.p.h:333 " *             COMMIT -- as above but wait until all trans have committed."
- stated: stated

### G59
- guarantee: elbb_QuiesceSystem with WRITE schedules all dirty user-data buffers; with FSYNC it also waits for those writes; with FLUSH it also invalidates user buffers; with FLUSHALL it invalidates all buffers.
- source: logbuf/logbuf.p.h:335 " *             WRITE -- schedules all dirty buffers containing user data."
- stated: stated

### G60
- guarantee: Before a dirty buffer on the log age queue is written, the log is forced at least through that buffer's last log record.
- source: logbuf/buffer.c:3769 "	  /* maybe force write log */"
- stated: implied

### G61
- guarantee: After that log force, elbl_ForceBuffer has made the buffer's log records committed on disk.
- source: logbuf/log.c:2125 "    afsl_Assert (BufCommitted (lmP, bP));"
- stated: implied

### G62
- guarantee: Equivalence-class ends are written atomically: the head transaction writes a BEND record for each member and then its own END, and recovery reconstitutes those member END records only if the head transaction is REDO.
- source: logbuf/recover.c:1687 " *     Bulk ends are the recovery end of ECs.  Because the end records must"
- stated: stated

### G63
- guarantee: Until the last member of an equivalence class ends, every earlier member is only pending and has no END record on disk.
- source: logbuf/tran.c:447 "	  /* This tran is part of an EC but we are not the last.  Just mark"
- stated: stated

### G64
- guarantee: A committed undo-zero fill of zeroes is a kill record: recovery marks every earlier recoverable record on that same disk block SKIP, and those earlier records must have been REDO.
- source: logbuf/recover.h:83 " * Records (not whole transactions) are marked SKIP if they predate a kill"
- stated: stated

### G65
- guarantee: Recovery raises RCVR_USERDATA if it sees an uncommitted kill after ordinary records on the same block.
- source: logbuf/recover.c:1907 "		    RECVR_RAISE (RCVR_USERDATA);"
- stated: stated

### G66
- guarantee: Recovery raises RCVR_METADATA if it sees an uncommitted recoverable record that a later kill would have skipped.
- source: logbuf/recover.c:1915 "		RECVR_RAISE (RCVR_METADATA);"
- stated: stated

### G67
- guarantee: For each data block, recovery applies undo records newest-first, then redo records oldest-first, then writes the block back only if it actually read it.
- source: logbuf/recover.c:1970 "	   * To actually perform the recovery we must make two passes."
- stated: stated

### G68
- guarantee: Redo of a recoverable record copies or fills from the record's new data; if the record has no new data, redo is a no-op.
- source: logbuf/recover.c:2068 "      /* if there is no new data, redo is a no-op */"
- stated: stated

### G69
- guarantee: Undo of a recoverable record copies or fills from the record's old data; if the record has no old data, undo is a no-op.
- source: logbuf/recover.c:2115 "      /* if there is no old data, undo is a no-op */"
- stated: stated

### G70
- guarantee: A data log record may be split across log pages; fill, end, and other non-data types are not split.
- source: logbuf/logrec.h:188 " * is a data record."
- stated: stated

### G71
- guarantee: Each log page other than a restart-only page carries a checksum; the default algorithm is CRC-32 over the whole page.
- source: logbuf/logrec.h:114 "#define LOGREC_CKSUMVER_DEFAULT LOGREC_CKSUMVER_CRC32_STD_ALL"
- stated: stated

### G72
- guarantee: A log page that contains only a restart record is written without a checksum.
- source: logbuf/recover.c:2738 "       * We choose not to checksum the log page containing a restart record"
- stated: stated

### G73
- guarantee: The log page header, including checksum, occupies the first sector, and recovery relies on sector atomicity: a page that was not written keeps an earlier pass number and is ignored as head.
- source: logbuf/recover.c:745 "     * sector for the log page and we can rely on"
- stated: stated

### G74
- guarantee: Recovery does not assume in-order writes; it uses the head page's io_window to check in-transit pages and pulls the head back to the page before the oldest invalid in-transit page.
- source: logbuf/recover.c:888 "     * out to disk. Because we don't assume writes are in order, we"
- stated: stated

### G75
- guarantee: If an in-transit log page did not reach disk, recovery may safely move the head further back: no on-disk change that must be undone can be missing from the log that is on disk.
- source: logbuf/recover.c:897 "     * cannot be any changes on disk we must undo that aren't in the"
- stated: stated

### G76
- guarantee: A checksum error on an active log page outside the in-transit window makes recovery fail with RCVR_IOERR, leaving the salvager as the remaining recourse.
- source: logbuf/recover.c:1043 "	     * Only resort is to run salvager"
- stated: stated

### G77
- guarantee: Pass number 0 is unused on an active log page; a newly initialized log uses pass 0, and incrementing a pass number skips 0.
- source: logbuf/recover.c:770 "     * A newly initialized log has pass # 0 written into"
- stated: stated

### G78
- guarantee: Every log page header carries salvage magic 0x73697045; a page without that magic is treated as a damaged log.
- source: logbuf/recover.h:44 "#define LOG_SALVAGE_MAGIC_NUMBER (0x73697045)"
- stated: stated

### G79
- guarantee: The package panics rather than overwrite the log if it cannot keep the active region strictly smaller than the log.
- source: logbuf/log.c:2907 "	   * Better a good panic than to have the log overwritten,"
- stated: stated

### G80
- guarantee: Starting a non-forced transaction or writing a log record fails with LOG_LOGFULL when the active log plus a reserved buffer of pages would exceed the log.
- source: logbuf/log.c:287 "    ((lmP->activeSize + LOG_FULL_BUFFER) > lmP->logLocnArraySize)"
- stated: implied

### G81
- guarantee: A nested (undo-zero) transaction may be started even when the log is full; the caller guarantees that nested size plus the parent still fits in one transaction reservation.
- source: logbuf/log.c:1672 "       * If the force option is set we proceed regardless of the available"
- stated: stated

### G82
- guarantee: Log space is reserved as (active transactions times full or undo-zero size) plus (pending transactions times end-record size).
- source: logbuf/log.c:138 " *     length(aTranList) * (nested ? undoSize : fullSize) +"
- stated: stated

### G83
- guarantee: The tail of the log is pinned by the oldest active or pending transaction on the transaction age queue and by the oldest dirty logged buffer on the buffer age queue.
- source: logbuf/log.c:136 " * The result of this is that the tranAgeQ is used to pin the tail of the log."
- stated: stated

### G84
- guarantee: If a transaction identifier is unknown or the transaction record has been freed, callers treating it as committed are correct.
- source: logbuf/tran.c:919 "	  return BUF_TRANCOMMIT;"
- stated: implied

### G85
- guarantee: elbb_Kill will not discard a dirty logged buffer unless metadataOK is true, which is allowed only after the transaction that freed that meta-data block has committed.
- source: logbuf/buffer.c:1359 " *     metadataOK is true if it is safe to kill dirty metadata"
- stated: stated

### G86
- guarantee: An unrecoverable EIO on a logged (meta-data) buffer panics.
- source: logbuf/buffer.c:4413 "      if (bufferIsLogged(bP) && ((code) == EIO))"
- stated: stated

### G87
- guarantee: User data is never logged.
- source: logbuf/buffer.c:1702 "       * from the same address space.  Since user data is never logged, we"
- stated: stated

### G88
- guarantee: elbb_Release with elbb_sync does not return until the log (if needed) and the data buffer have both been written.
- source: logbuf/logbuf.p.h:66 "    elbb_sync,    /* force write log, force write data buffer, upon return"
- stated: stated

### G89
- guarantee: elbb_Release with elbb_syncLog forces the log through the buffer's last record, schedules the buffer write, and does not wait for that data write.
- source: logbuf/logbuf.p.h:64 "    elbb_syncLog, /* force write log, schedule buffer write, don't wait"
- stated: stated

### G90
- guarantee: elbb_UndoZero appends old-fill-of-zero records to an existing transaction for a byte range, covering I/O that does not use the buffer system.
- source: logbuf/buffer.c:2414 " * elbb_UndoZero - Adds an undo-zero record to an existing transaction for"
- stated: stated

### G91
- guarantee: elbb_UndoZeroBuffer starts a nested transaction, attaches it to the dirty buffer, logs an old-fill-of-zero, and that transaction is ended when the buffer is no longer dirty.
- source: logbuf/buffer.c:2457 " * elbb_UndoZeroBuffer -- Adds an undo-zero record for the specified buffer.  A"
- stated: stated

### G92
- guarantee: When a buffer is cleaned, an attached undo-zero transaction may be ended and the buffer removed from the age queue even if those undo-zero log records have not yet committed.
- source: logbuf/buffer.c:339 " *     If this is an undo zero buffer then the log records may not have"
- stated: stated

### G93
- guarantee: A bona fide meta-data buffer is removed from the age queue only after its updates have committed: either the log was forced before the write, or the freeing transaction was committed before a kill.
- source: logbuf/buffer.c:345 " *     In the case of bona fide metadata buffers updates to those buffer must"
- stated: stated

### G94
- guarantee: Recovery code takes no locks and may recover more than one log at a time.
- source: logbuf/recover.c:101 " * Locking is no longer done in this package; all code should be thread-safe"
- stated: stated

### G95
- guarantee: The smallest usable log is load times the per-transaction reservation, plus LOG_FULL_BUFFER, plus one page.
- source: logbuf/log.c:848 "      minSize = (load * elbl_MinTranReservation(dP->blkSize)) +"
- stated: stated

### G96
- guarantee: The log is given at least LOGREC_MAX_BUFFERS (5) pages, which is the number of in-transit pages recovery will verify.
- source: logbuf/logrec.h:53 " * this defines the number of pages the recovery package will verify have"
- stated: stated

### G97
- guarantee: A logged modification writes the log record and then copies the new data into the buffer, leaving the buffer dirty.
- source: logbuf/buffer.c:1455 "      if (logRequest) {"
- stated: implied

### G98
- guarantee: elbb_Initialize logs only the new contents of a CreateBlock buffer (no old data).
- source: logbuf/buffer.c:1588 " * By initialization, we mean modification in the case where the old data"
- stated: stated

### G99
- guarantee: elbb_Fill with saveOld logs the old data and then a new-fill record, all in the same transaction, so the fill may be split into chunks.
- source: logbuf/buffer.c:1542 "       * A single call here can always be divided into chunks because of"
- stated: stated

### G100
- guarantee: Starting a transaction with a non-null oldTranId starts a nested transaction and does not block waiting for log space.
- source: logbuf/buffer.c:1739 " *     By providing an old transaction ID, this call will not block.  If there"
- stated: stated

### G101
- guarantee: elbb_StartTran without an old transaction retries, including log-full handling, until it obtains a transaction (except during a bounded kernel-panic loop).
- source: logbuf/buffer.c:1743 " *     If this routine fails to allocate a transaction we presume it is because"
- stated: implied

### G102
- guarantee: Recovery walks log records in increasing LSN order.
- source: logbuf/recover.c:1633 "	   * we must guarantee our transactions remain time-ordered."
- stated: stated

### G103
- guarantee: The null transaction identifier is never issued to a live transaction; restart and checkpoint records may use it.
- source: logbuf/recover.c:1656 "      /* we don't use the zero transaction id - but we allow it for a restart"
- stated: stated

### G104
- guarantee: elbb_FsyncForce writes the tagged or listed buffers, forcing the log as needed for any logged buffer among them.
- source: logbuf/buffer.c:2018 " * elbb_FsyncForce -- implements fsync using two basic methods of specifying"
- stated: implied

### G105
- guarantee: elbb_SyncForce schedules writes of dirty buffers and does not wait for those writes to complete.
- source: logbuf/buffer.c:2166 "       * For sync, we do not want to wait.  We walk through the entire hash"
- stated: stated

### G106
- guarantee: On a logged modify, fill, or initialize, if the write leaves the log in a log-full state, HandleLogFull is invoked before the call returns.
- source: logbuf/buffer.c:1489 "      if (logRequest && logFullState)"
- stated: implied

### G107
- guarantee: Create of a new log zeroes every page but the first and writes a restart record on the first log block.
- source: logbuf/log.c:904 "       * We skip the first block because we will be writing a restart"
- stated: stated

### G108
- guarantee: Each log record carries a monotonically increasing LSN that skips zero.
- source: logbuf/log.c:355 "	(lmP)->lsn = (++((lmP)->lsn) ? (lmP)->lsn : ++((lmP)->lsn)); \"
- stated: implied

### G109
- guarantee: Recoverable record types are data and fill records with old data, new data, or both; end, checkpoint, restart, debug, flush, and bend records are not applied as data updates.
- source: logbuf/logrec.h:167 "				    ((type) == LOGREC_NFILL))"
- stated: implied

### G110
- guarantee: If recovery must raise an error, it unwinds and returns a recovery error code rather than panicking, except for a few allocation and dump firewalls.
- source: logbuf/recover.c:385 " * This routine must be *very* paranoid about failure.  It is better"
- stated: stated

### G111
- guarantee: Nested undo-zero transactions are logically ordered after the allocation transaction that created them, even though they are not merged into that transaction's equivalence class.
- source: logbuf/log.c:1678 "       * This is dangerous, but necessary to cascade UndoZero transactions with"
- stated: stated

### G112
- guarantee: Quiesce without stopping the system waits only for transactions older than the log position sampled at the start of the call, so later activity may continue concurrently.
- source: logbuf/tran.c:1217 " *     Quiescing without stopping the system works by waiting for all currently"
- stated: stated
