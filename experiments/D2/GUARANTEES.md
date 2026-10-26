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

