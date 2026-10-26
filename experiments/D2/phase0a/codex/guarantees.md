### G1
- guarantee: After a crash and successful recovery, file-system metadata, including directories, allocation bitmaps, indirect blocks, and anode tables, is consistent.
- source: §"Background" "guarantee that after a crash, the le system meta-data (directories, allocation bitmaps, indirect blocks and
anode tables) are consistent, generally eliminating the need for running \fsck.""
- stated: stated

### G2
- guarantee: A committed metadata transaction applies all its updates atomically.
- source: §"Component Architecture" "that either all the updates within a transaction (if a transaction commits), or none of them (if a transaction
aborts), will be applied."
- stated: stated

### G3
- guarantee: An aborted metadata transaction leaves none of its updates applied.
- source: §"Component Architecture" "that either all the updates within a transaction (if a transaction commits), or none of them (if a transaction
aborts), will be applied."
- stated: stated

### G4
- guarantee: For every metadata update, logging records both the original and new values.
- source: §"Component Architecture" "value logging techniques [MOH 89]. In a nutshell, this form of logging works by logging, for every update
made to any le system meta-data, both the original and new values of the updated data."
- stated: stated

### G5
- guarantee: Before writing a dirty metadata buffer to its home disk location, the buffer package writes the corresponding log entries to disk.
- source: §"Component Architecture" "before the bu er package allows any dirty meta-data bu er to be written back out to the disk, it writes
out these log entries to the disk."
- stated: stated

### G6
- guarantee: Recovery restores aborted metadata updates to their values before the transaction began.
- source: §"Component Architecture" "the log to undo all of the updates made to the meta-data, and restore the meta-data to its state before the
transaction started."
- stated: stated

### G7
- guarantee: Recovery redoes committed metadata updates even when their buffers had not reached disk before the crash.
- source: §"Component Architecture" "transaction started. If the transaction committed, there is enough information in the log to redo all of the
meta-data updates, even those that hadn't yet made it from the disk bu ers to the disk."
- stated: stated

### G8
- guarantee: Recovery undoes transactions that were uncommitted at the crash.
- source: §"Component Architecture" "The recovery procedure runs after a crash, replaying the committed transactions and undoing the
uncommitted transactions, and thus restoring the le system to a consistent state."
- stated: stated

### G9
- guarantee: The paper initially promises recovery time proportional to activity at the crash rather than disk size, subject to its later qualification about uncheckpointed committed transactions.
- source: §"Component Architecture" "contains information describing transactions still in progress, recovery time is proportional to the activity
at the time of the crash, not to the size of the disk."
- stated: stated

### G10
- guarantee: The paper claims log replay runs orders of magnitude faster than BSD fsck.
- source: §"Component Architecture" "of magnitude faster than the BSD fsck program."
- stated: stated

### G11
- guarantee: Transactions may release transactional locks before the end of the transaction.
- source: §"Logging Architecture" "tional locking instead of two-phase locking. Episode transactions can acquire locks when they need them,
and drop them as soon as they are nished using them, rather than waiting for the transaction's end."
- stated: stated

### G12
- guarantee: Active transactions that lock the same object during their lifetimes are merged into an equivalence class.
- source: §"Logging Architecture" "have otherwise been able to commit, if a crash intervenes. Speci cally, all active transactions that lock the
same object during their lifetime are merged into an equivalence class (EC). An EC has the property that"
- stated: stated

### G13
- guarantee: All transactions in an equivalence class commit together or none commit.
- source: §"Logging Architecture" "either all of its transactions commit or none do.3 In the example above, transaction 1 and 2 would form"
- stated: stated

### G14
- guarantee: A crash before all transactions in an equivalence class have committed aborts every transaction in that class.
- source: §"Logging Architecture" "If the system crashes before all of the transactions in an EC have committed, all the transactions in
the EC are aborted."
- stated: stated

### G15
- guarantee: An explicit synchronization request such as fsync prevents the requested metadata persistence from being indefinitely deferred.
- source: §"Logging Architecture" "Meta-data changes to the disk itself can often be deferred, unless speci cally requested by an oper-
ation like fsync. Consistency of the le system doesn't require that the system be current."
- stated: implied

### G16
- guarantee: When a newly allocated data block has an incomplete first-write transaction at a crash, recovery zeroes the block.
- source: §"Logging Architecture" "to it completes. If the system crashes and the transaction aborts, the recovery procedure for this special
transaction zeroes the contents of the block."
- stated: stated

### G17
- guarantee: Log-space admission control keeps running transactions within the available log space.
- source: §"Logging Architecture" "when they begin. This allows the use of a very simple algorithm to ensure that running transactions never
exceed the space available in the log."
- stated: stated

### G18
- guarantee: Dirty metadata buffers may be written before their transactions end.
- source: §"Logging Architecture" "when to write these bu ers. Old value / new value logging, on the other hand de-couples the writing of
bu ers from the end of transactions, at the expense of having to write more data to the log."
- stated: implied

### G19
- guarantee: Each transaction in a multi-transaction filesystem operation leaves the filesystem consistent, even if the overall operation is unfinished.
- source: §"Logging Architecture" "operations, followed by a deletion of the empty le. After each transaction, the le system is consistent, if
not in the nal desired state."
- stated: stated

### G20
- guarantee: The active log retains uncommitted transactions needed for crash undo.
- source: §"Recovery Time" "active portion of the log is that part of the log that needs to be replayed after a crash, and must include all
of the uncommitted transactions, since these must be undone in the event of a crash."
- stated: stated

### G21
- guarantee: The active log also retains committed updates whose metadata buffers remain dirty, qualifying the earlier claim that recovery depends only on in-progress transactions.
- source: §"Recovery Time" "of the log may go back even further, should the bu er cache still contain dirty meta-data blocks that were
modi ed by committed transactions."
- stated: stated

### G22
- guarantee: Checkpointing discards committed log history only after writing the buffers required to preserve those transactions.
- source: §"Recovery Time" "the replay of that part of the log in the event of a crash. The operation of writing bu ers modi ed by
committed transactions and discarding those portions no longer required to ensure the permanence of those"
- stated: implied

### G23
- guarantee: The system prevents the log from becoming full.
- source: §"Recovery Time" "permit the log to become full"
- stated: stated

### G24
- guarantee: The work needed to replay one active log block has a finite bound on the number of metadata blocks it can affect.
- source: §"Recovery Time" "Of course, the time to replay a block of the active log is not constant, but is bounded: There is a
maximum number of meta-data blocks whose updates can be described by a block of the log, but many"
- stated: stated

### G25
- guarantee: elbb_LogForce with waitOK zero commits a complete transaction but returns BUF_WOULDBLOCK if it would have to wait for the transaction to end.
- source: logbuf/tran.c:948 " *     0 -- caller can't wait for other transactions to end.  Commit only if
 *         transaction is complete, otherwise return BUF_WOULDBLOCK."
- stated: stated

### G26
- guarantee: elbb_LogForce with waitOK one returns only after the transaction has committed, making its updates persistent.
- source: logbuf/tran.c:950 " *     1 -- don't return until transaction has committed.  This guarantees
 *         persistence for updated done under this transaction.  "fsync" is the"
- stated: stated

### G27
- guarantee: elbb_LogForce with waitOK two waits for completion and serializes the transaction with transactions begun after the call returns.
- source: logbuf/tran.c:953 " *     2 -- don't return until transaction has completed.  This ensures
 *         serialization of this transaction with respect to any transactions"
- stated: stated

### G28
- guarantee: Forcing an already forgotten transaction returns success.
- source: logbuf/tran.c:968 "    if (!tP)
	return BUFFER_OK;"
- stated: implied

### G29
- guarantee: Ending a transaction in an unfinished equivalence class may leave it pending rather than committed.
- source: logbuf/tran.c:426 " * elbt_EndTran -- handle changing the state of a transaction from active to
 *     complete or pending (EC)."
- stated: stated

### G30
- guarantee: An equivalence class writes all member batch-end records before writing its final head end record.
- source: logbuf/tran.c:795 "     * We won't write the end record out for the final transaction until
     * after all the batch end records have been written out."
- stated: stated

### G31
- guarantee: elbt_ECMerge joins the supplied transactions into one equivalence class.
- source: logbuf/tran.c:641 " * elbt_ECMerge -- joins two transactions into an equivalence class.  The
 *     second tran must be active."
- stated: stated

### G32
- guarantee: Starting a transaction with an old transaction ID does not block waiting for other transactions to complete.
- source: logbuf/buffer.c:1739 " *     By providing an old transaction ID, this call will not block.  If there
 *     is no transaction ID, this call might wait pending completion of other"
- stated: stated

### G33
- guarantee: When transaction allocation fails because of log pressure, elbb_StartTran handles the full log and retries.
- source: logbuf/buffer.c:1743 " *     If this routine fails to allocate a transaction we presume it is because
 *     the log is full and so we invoke the log full handling and try again."
- stated: stated

### G34
- guarantee: A transaction is not treated as durably committed merely because its end record has been constructed in memory.
- source: logbuf/log.c:140 " * The transactions on the cTranList are being held until their end records are
 * actually committed to disk.  Then they are returned to the tran module when"
- stated: implied

### G35
- guarantee: elbl_ForceTran forces the log to disk through the transaction's last update.
- source: logbuf/log.c:2035 " * elbl_ForceTran -- force the log to disk up to the specified transaction's
 *     last update."
- stated: stated

### G36
- guarantee: elbl_ForceBuffer forces the log to disk through the specified buffer's last update.
- source: logbuf/log.c:2108 " * elbl_ForceBuffer -- force the log to disk up to the specified buffer's
 *     last update."
- stated: stated

### G37
- guarantee: elbb_Release with elbb_syncLog forces the log through the most recent transaction on that buffer.
- source: logbuf/buffer.c:1250 " * syncLog - force log up to most recent transaction on this buffer"
- stated: stated

### G38
- guarantee: elbb_Release with elbb_sync returns after both the necessary log and the data buffer have been written.
- source: logbuf/logbuf.p.h:66 "    elbb_sync,    /* force write log, force write data buffer, upon return
                   * both log and data buffer have been written */"
- stated: stated

### G39
- guarantee: elbb_Release with elbb_async schedules a write immediately and returns without waiting for write completion.
- source: logbuf/logbuf.p.h:63 "    elbb_async,   /* schedule write now, but don't wait for completion */"
- stated: stated

### G40
- guarantee: The elbb_Release interface comment promises that elbb_lazy returns without scheduling I/O, although its implementation writes unlogged buffers.
- source: logbuf/buffer.c:1259 " * lazy always returns without I/O being scheduled."
- stated: stated

### G41
- guarantee: The elbb_adel interface description promises asynchronous deletion and buffer reuse upon write completion, although the implementation waits.
- source: logbuf/logbuf.p.h:69 "    elbb_adel,    /* schedule write now, reuse upon completion of write. */"
- stated: stated

### G42
- guarantee: elbb_Release with elbb_sdel waits for the scheduled write before buffer reuse.
- source: logbuf/logbuf.p.h:70 "    elbb_sdel     /* schedule write now, wait, reuse upon completion. */"
- stated: stated

### G43
- guarantee: elbb_QuiesceSystem with SERIALIZE waits for transactions active at entry to end.
- source: logbuf/logbuf.p.h:332 " *             SERIALIZE -- ensure all currently active trans have ended."
- stated: stated

### G44
- guarantee: elbb_QuiesceSystem with COMMIT waits for transactions active at entry to commit.
- source: logbuf/logbuf.p.h:333 " *             COMMIT -- as above but wait until all trans have committed."
- stated: stated

### G45
- guarantee: elbb_QuiesceSystem with WRITE schedules dirty user-data buffers for writing.
- source: logbuf/logbuf.p.h:335 " *             WRITE -- schedules all dirty buffers containing user data."
- stated: stated

### G46
- guarantee: elbb_QuiesceSystem with FSYNC also waits for the user-data writes to finish.
- source: logbuf/logbuf.p.h:336 " *             FSYNC -- also waits for writes to complete."
- stated: stated

### G47
- guarantee: elbb_QuiesceSystem with FLUSH also invalidates user-data buffers.
- source: logbuf/logbuf.p.h:337 " *             FLUSH -- also invalidates user buffers (vol_close)."
- stated: stated

### G48
- guarantee: elbb_QuiesceSystem with FLUSHALL also invalidates all buffers.
- source: logbuf/logbuf.p.h:338 " *             FLUSHALL -- also invalidates all buffers (elbb_Shutdown)."
- stated: stated

### G49
- guarantee: Quiescing allows concurrent activity after the captured log position rather than requiring the whole system to stop.
- source: logbuf/tran.c:1220 " *     when the caller (elbb_QuiesceSystem) started.  Other activity is allowed
 *     to continue concurrently."
- stated: stated

### G50
- guarantee: elbt_Quiesce consistency zero waits for earlier unnested transactions to end.
- source: logbuf/tran.c:1224 " *     "consistency"; if zero, we wait for all unnested transactions started
 *     before (pass,off) to end.  Unnested transaction includes all those"
- stated: stated

### G51
- guarantee: elbt_Quiesce consistency one waits for earlier unnested transactions to commit.
- source: logbuf/tran.c:1226 " *     except undo zero transactions.  If it is one we wait for all unnested
 *     transactions to commit.  The other interesting value is three,"
- stated: stated

### G52
- guarantee: elbt_Quiesce consistency three also commits earlier undo-zero transactions.
- source: logbuf/tran.c:1228 " *     requesting that we also commit undo zeros (see cautions below).  The"
- stated: stated

### G53
- guarantee: elbt_Quiesce consistency two serializes earlier undo-zero transactions.
- source: logbuf/tran.c:1229 " *     value two serializes undo zero trans, this is used by elbb_StartTran."
- stated: stated

### G54
- guarantee: elbb_Shutdown writes pending buffers, removes the device's buffers from use, and shuts down its log.
- source: logbuf/buffer.c:2563 " *     or unlogged.) this routine writes out all pending buffers and removes
 *     all buffers for this device from use.  It uses QuiesceSystem to do this"
- stated: stated

### G55
- guarantee: elbl_Close waits for active transactions to complete and writes a restart block.
- source: logbuf/log.c:1482 " * This routine is inclusive of elbl_Shutdown;  it however always blocks
 * pending the completion of any active transactions.  It then writes a"
- stated: stated

### G56
- guarantee: On return from elbl_Close, the log is clean, metadata is on disk, and the returned transactions count as committed.
- source: logbuf/log.c:1487 " * this log.  They should all be considered committed upon return from
 * this function (the log is clean, all meta-data is written to disk, etc.)"
- stated: stated

### G57
- guarantee: elbb_FsyncForce writes and waits for dirty cached buffers selected by file-handle tag or block array.
- source: logbuf/buffer.c:2138 "	code = asevent_WaitAll(aset);"
- stated: implied

### G58
- guarantee: Ordinary elbb_SyncForce schedules dirty buffers that are neither being updated nor already being written, without waiting for pending writes.
- source: logbuf/buffer.c:2166 "       * For sync, we do not want to wait.  We walk through the entire hash
       * pool, skipping buffers being updated (they're busy), and scheduling"
- stated: stated

### G59
- guarantee: elbb_ModifySource logs the buffer modification when the transaction ID is valid and logging is requested.
- source: logbuf/buffer.c:1410 " * this routine changes the contents of a buffer and logs that change
 * if the tranId is not the invalid transaction id and the logRequest"
- stated: stated

### G60
- guarantee: elbb_ModifySource returns the resulting buffer handle through its output parameter.
- source: logbuf/buffer.c:1414 " * this routine returns the buffer handle in the nbP pointer - caller
 * cannot assume the buffer handle will not change across this call."
- stated: stated

### G61
- guarantee: elbb_Initialize logs initialization without logging the previous contents.
- source: logbuf/buffer.c:1588 " * By initialization, we mean modification in the case where the old data
 * do not have to be logged, i.e. the buffer was created by CreateBlock."
- stated: stated

### G62
- guarantee: elbb_ReadGeneral checks for an existing cached buffer before scheduling a disk read.
- source: logbuf/buffer.c:974 " * It checks to see if a buffer already exists for this block prior to
 * scheduling a read."
- stated: stated

### G63
- guarantee: The synchronous read mode of elbb_ReadGeneral waits for read completion.
- source: logbuf/buffer.c:971 " * (2) Allocate & read a buffer (waits for completion)"
- stated: stated

### G64
- guarantee: The asynchronous read mode of elbb_ReadGeneral schedules a read without waiting for completion.
- source: logbuf/buffer.c:972 " * (3) Allocate & schedule read for a buffer (doesn't wait for completion)."
- stated: stated

### G65
- guarantee: elbb_Kill refuses to delete a dirty logged buffer when metadataOK is false.
- source: logbuf/buffer.c:1364 " * RETURN CODES -- returns zero if all went well, and CANTDELETE if metadataOK
 *     was false and the buffer was LOGGED and DIRTY. */"
- stated: stated

### G66
- guarantee: elbb_Reserve provides buffer reservations for paths that need multiple buffers simultaneously to avoid buffer-allocation deadlock.
- source: logbuf/buffer.c:2193 " * elbb_Reserve - reservation call for code paths which require multiple
 *		buffers simultaneously; this avoids deadlock."
- stated: stated

### G67
- guarantee: elbb_UndoZero records undo-zero coverage for the requested byte range in an existing transaction, including I/O outside the buffer system.
- source: logbuf/buffer.c:2414 " * elbb_UndoZero - Adds an undo-zero record to an existing transaction for
 * the specified range of bytes.  This is to be used by the VM system for I/Os"
- stated: stated

### G68
- guarantee: elbb_UndoZeroBuffer creates and attaches a transaction if the buffer has no undo-zero transaction already.
- source: logbuf/buffer.c:2457 " * elbb_UndoZeroBuffer -- Adds an undo-zero record for the specified buffer.  A
 *     transaction is started and attached to the buffer if one is not already"
- stated: stated

### G69
- guarantee: Recovery redoes a transaction with an end record even when its begin record is outside the active log.
- source: logbuf/recover.c:1787 "     * (no start, has end) - REDO"
- stated: stated

### G70
- guarantee: Recovery rejects transaction records with neither a start nor an end record.
- source: logbuf/recover.c:1781 "     * The last state (no start, no end) is invalid - we should NEVER
     * see such a log.  The other three are valid.  Their corresponding"
- stated: stated

### G71
- guarantee: Recovery recognizes member end records from batch-end records only when the containing transaction committed.
- source: logbuf/recover.c:1690 " *     with BEND records we search to see if the transaction committed.  If it
 *     did, we take the data section of each BEND record (which is really an"
- stated: stated

### G72
- guarantee: For each recovered data block, recovery performs undo operations before redo operations.
- source: logbuf/recover.c:1970 "	   * To actually perform the recovery we must make two passes.
	   * Pass # 1 is where all undo operations are done; pass # 2"
- stated: stated

### G73
- guarantee: Recovery skips obsolete updates preceding an undo-zero kill record for a reused block.
- source: logbuf/recover.c:1875 " *     NBS.  These must be interpreted as kill records for earlier updates to
 *     the same block.  Set the status of all such updates to SKIP. */"
- stated: stated

### G74
- guarantee: Recovery fails with RCVR_USERDATA if an uncommitted kill precedes newer metadata records on the same block.
- source: logbuf/recover.c:1906 "		if ((rec->status == RECVR_STATUS_UNDO) && someRecs)
		    RECVR_RAISE (RCVR_USERDATA);"
- stated: implied

### G75
- guarantee: Recovery fails with RCVR_METADATA if an uncommitted metadata update precedes a kill record on the same block.
- source: logbuf/recover.c:1914 "	    if (rec->status == RECVR_STATUS_UNDO)
		RECVR_RAISE (RCVR_METADATA);"
- stated: implied

### G76
- guarantee: Recovery can move the log head backward past incompletely written in-transit pages even when log writes completed out of order.
- source: logbuf/recover.c:888 "     * out to disk. Because we don't assume writes are in order, we
     * must check to assure ourselves that all the pages in the I/O"
- stated: stated

### G77
- guarantee: Recovery checks page pass numbers as well as checksums to reject older log pages left on disk.
- source: logbuf/recover.c:929 "	 * to be checked as the log page could be a much older logpage
	 * with a correct checksum but an old passnumber."
- stated: stated

### G78
- guarantee: For supported checksum formats, a checksum failure in the retained active log outside the in-transit window causes recovery to fail.
- source: logbuf/recover.c:756 "     * expected to be on disk correctly. If checksum errors are
     * detected for these pages, there is really nothing we can do"
- stated: stated

### G79
- guarantee: Successful recovery writes a clean restart record after applying disk changes.
- source: logbuf/recover.c:507 "      /* Step 5: recovery is complete.  Write out a clean restart record. */"
- stated: implied

### G80
- guarantee: A crash while writing the checkpoint block leaves the previous active log usable.
- source: logbuf/recover.c:2606 " * block of the active log, so if the machine crashes while we are writing
 * the checkpoint block, there's no problem.  If we successfully write a"
- stated: stated

### G81
- guarantee: A crash while writing the restart block after a successful checkpoint leaves a usable recovery log.
- source: logbuf/recover.c:2614 " * the checkpoint block.  In either case, the log is usable (recovery can
 * proceed)."
- stated: stated

### G82
- guarantee: elbr_GetCleanLogInfo returns zero for a log needing recovery and one for a clean log.
- source: logbuf/recover.c:2760 " * returns 0 if not clean (needs recovery), 1 if clean."
- stated: stated

### G83
- guarantee: After reading a page with the correct salvage magic, elbr_GetCleanLogInfo fills a supplied header output even when later checks find the log unclean.
- source: logbuf/recover.c:2761 " * The log page hdr structure ptr (if non-zero) is
 * filled in by this routine."
- stated: stated

### G84
- guarantee: In kernel mode, elbr_Recover returns RCVR_MUSTRCVR instead of performing recovery.
- source: logbuf/recover.c:2374 "      return RCVR_MUSTRCVR; /* no kernel recovery anymore */"
- stated: implied

### G85
- guarantee: Log initialization detects a missing clean restart record and attempts recovery instead of starting ordinary logging.
- source: logbuf/log.c:730 "       * disk.  If so, we continue.  If not, we attempt recovery and
       * return the resulting error value (never OK) to the caller."
- stated: stated

### G86
- guarantee: Successful recovery during log initialization is reported as RCVR_RECOVERED rather than ordinary success.
- source: logbuf/log.c:737 "	      return RCVR_RECOVERED;	/* so upper levels can clear buffers */"
- stated: implied

### G87
- guarantee: elbb_LogInit invalidates cached buffers after successful recovery.
- source: logbuf/buffer.c:1837 "	      /* log recovered, we invalidate the buffer pool by
	       * calling shutdown.  Note that we assume none of the"
- stated: stated

### G88
- guarantee: Log initialization rejects a device that already has an active log.
- source: logbuf/log.c:712 "	  return LOG_LOGEXISTS;"
- stated: implied

### G89
- guarantee: Log initialization rejects a log smaller than the computed minimum size.
- source: logbuf/log.c:750 "      if (elbl_MinLogSize(lmP->dev, 0) > logLocnArraySize) {"
- stated: implied

### G90
- guarantee: Unknown on-disk checksum types are accepted with a diagnostic that checksum checking is being ignored.
- source: logbuf/recover.c:2578 "	    /* Unknown checksum type recorded on disk. Force success of
	     * checksum validity check */"
- stated: stated

### G91
- guarantee: Recognized legacy log pages with checksums but no recorded checksum lengths remain supported.
- source: logbuf/recover.c:2438 "	 * Account for (pre solaris release) aggregates that record checksums
	 * but no checksum lengths in the log pages, when determining"
- stated: stated

### G92
- guarantee: Writing a restart block with an unknown checksum version switches the log to the default checksum version.
- source: logbuf/recover.c:2705 "      /* Validate checksum version and switch to default version type"
- stated: implied

### G93
- guarantee: Successful user-space recovery reports elapsed time and counts of recovered pages, records, changed blocks, and undo/redo operations.
- source: logbuf/recover.c:562 "      printf("recovery statistics:\n");"
- stated: implied

### G94
- guarantee: The active-log dump interface exposes the contents of the active portion of the log to external programs.
- source: logbuf/recover.c:592 " * of the active log.  It can be called by an external program to retrieve the
 * actual contents of the active portion of the log."
- stated: stated

### G95
- guarantee: The entire-log dump interface exposes the contents of the whole log to external programs.
- source: logbuf/recover.c:633 " * of the ENTIRE log.  It can be called by an external program to retrieve the
 * actual contents of the entire log."
- stated: stated

### G96
- guarantee: The implementation of elbb_Release with elbb_lazy schedules a write for unlogged buffers, contrary to its no-I/O interface comment.
- source: logbuf/buffer.c:1288 "	  if (!bufferIsLogged(bP)) {
	      retval = Write(bP);"
- stated: implied

### G97
- guarantee: The implementation of elbb_Release with elbb_adel waits for the write just like elbb_sdel, despite the asynchronous-deletion interface description.
- source: logbuf/buffer.c:1295 "	  /* Can't presently handle asyncronous deletion of buffers.  To do it
	   * right ReadGeneral would have to check and wait.  So we just wait"
- stated: stated

### G98
- guarantee: The header promises that elbb_syncLog both forces the log and schedules the data-buffer write.
- source: logbuf/logbuf.p.h:64 "    elbb_syncLog, /* force write log, schedule buffer write, don't wait
                   * for data buffer write completion. */"
- stated: stated

### G99
- guarantee: The implementation of elbb_Release with elbb_syncLog only forces the log and does not itself schedule the data-buffer write promised by the header.
- source: logbuf/buffer.c:1314 "	case elbb_syncLog:
	  elbl_ForceBuffer(bP);"
- stated: implied

### G100
- guarantee: elbb_Fill fills the specified region with the requested one-byte pattern.
- source: logbuf/buffer.c:1499 " * This routine is used to implement a "flood" of a data area with a
 * specific bit pattern (1 char).  It optionally saves the old data"
- stated: stated

### G101
- guarantee: When logging and saveOld are requested, elbb_Fill records the old data for undo before the new fill.
- source: logbuf/buffer.c:1549 "	  LogWrite(tranId, LOGREC_ODATA, fillSize, offset, bP, 0, retval,"
- stated: implied

### G102
- guarantee: elbb_FastModify promises a logged modification equivalent to reading, modifying, and releasing the buffer, although its source identifies a log-full bug.
- source: logbuf/buffer.c:1644 " * This routine is equivalent to a ReadGeneral/ModifySource/Release operation"
- stated: stated

### G103
- guarantee: For each recovered block, undo applies records from newest to oldest.
- source: logbuf/recover.c:1992 "	      for (rec2P = FIFO_LookAtNewest(&(recP)->diskFifo, DISKTHREAD);"
- stated: implied

### G104
- guarantee: For each recovered block, redo applies records from oldest to newest.
- source: logbuf/recover.c:2020 "		   rec2P = FIFO_NextOldest(&(recP)->diskFifo, rec2P,"
- stated: implied

### G105
- guarantee: Recovery writes changed data blocks synchronously before proceeding to its clean-log completion.
- source: logbuf/recover.c:2037 "	       * write changes back (synch. I/O) - do nothing if
	       * I/O was deferred (ie for NBS)."
- stated: implied

### G106
- guarantee: User-space elbr_Recover rejects null devices, a null log block array, or an empty log block array with RCVR_INVALID.
- source: logbuf/recover.c:410 "      if ( !ldP || !dP || !logLocnArray || (logLocnArraySize == 0))
	  return RCVR_INVALID;"
- stated: implied

### G107
- guarantee: The committed-status convenience function returns true for either a committed transaction or a transaction ID no longer in the transaction table.
- source: logbuf/buffer.c:1886 "      if ((code == BUF_BADTRAN) || (code == BUF_TRANCOMMIT))
	  return 1;"
- stated: implied

### G108
- guarantee: Log creation zero-initializes every log block except the first, which receives a restart record.
- source: logbuf/log.c:904 "       * We skip the first block because we will be writing a restart
       * record into it.  All other blocks are initialized to zero."
- stated: stated

## Report notes

108 guarantees. No commits were made. This is source extraction, not an outcome-bearing model/implementation run.

The consistency and replay guarantees concern successful recovery of recoverable crashes. The paper explicitly excludes cases such as hard I/O errors updating critical metadata (end of “Component Architecture”), which require the salvager. The promises concern metadata consistency; general user-data transactionality and persistence of every recently completed operation are not promised. Explicit force operations provide stronger persistence. Equivalence-class completion and durable commitment are distinct.

Disagreements and qualifications:

- G9 records the early paper claim that recovery depends on activity at the crash; G21 records the later qualification that uncheckpointed committed updates also remain active. The source retains both transaction and buffer age queues (`logbuf/log.c:136`). Thus the early “only” description is too narrow; there is no unconditional activity-only recovery-time bound.
- G40 and G96 conflict: the lazy-release comment promises no I/O, while the implementation schedules writes for unlogged buffers. G41 and G97 record the asynchronous-deletion description and synchronous fallback. G98 and G99 record the syncLog header promise and implementation's log-only force.
- G102 records FastModify's advertised equivalence; its source explicitly identifies the incorrect transaction-start path under log pressure. This is a stated promise with an implementation caveat, not a verified implementation guarantee.
- G85 limits automatic recovery in the released source to user space. The paper describes crash recovery without that interface limitation; this is a version/interface qualification, not evidence of weaker atomicity after successful user-space recovery.

Things not decided or promoted to guarantees:

- The paper's expectation of recovery under 30 seconds in “most configurations” and its measured recovery times are predictions/observations, not universal behavioral promises. Its faster-than-fsck assertion is included as an explicit comparative claim (G10), without treating measurements as proof.
- Two-phase locking's serializability and exclusion of uncommitted reads are described as properties of another locking scheme. Episode instead describes read/write sharing and equivalence classes; I did not infer serializable isolation or a prohibition on reading uncommitted data.
- The recovery package's early comment says it should support simultaneous recoveries, while its later overview requires user-space recovery to run single-threaded, and the released kernel entry point refuses recovery. A generally usable concurrent-recovery guarantee is unresolved.
- The comment at `logbuf/recover.c:2526` promises checksum-version/length agreement across pages, but the corresponding check is compiled out. No enforcement guarantee is inferred. Unknown checksum types explicitly bypass checking (G90); restart-only pages are deliberately not checksummed. Checksums do not imply detection of every possible corruption.
- Exact completion-time bounds, progress under permanent I/O failure, arbitrary corruption repair, and recovery after every possible repeated interruption are not established. Checkpoint/restart interruption protection is expressly stated and included (G81–G82).
- No contract clauses or failure-model cells were supplied in this checkout, so derivation IDs cannot be assigned without inventing them; entries instead provide the brief's source derivations. No formal model or implementation was authored.

Checkout listing (`ls -R --ignore=episode .`; excludes `source/episode/`):

```
.:
AGENTS.md
BRIEF.md
guarantees.md
source

./source:
episode-1992.pdf
episode-1992.txt
```

Git status (`git status`):

```
On branch main
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	guarantees.md

nothing added to commit but untracked files present (use "git add" to track)
```
