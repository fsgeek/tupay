# CELLS.md: environment contracts of the log and recovery, in a fixed order

Enumerated from the paper and the source by other readers; a cell with several statements is one contract stated by several readers. Take them in this order.

### D68
- contract: A deployment interpreting the recovery-time comparisons must keep active history, I/O performance, and available recovery resources comparable rather than scaling them with aggregate size.
- source: §"Recovery Time" "Episode's time to recover depends primarily on the size of the active portion of transaction log."
- violation: A larger aggregate is configured with much more active log history or a much slower recovery device.
- at-risk: G9–G11: replay cost depends on active pages and affected blocks, so aggregate-size-independent timing is conditional.
- detectable: yes — active-log size, affected-block count, and recovery timings can be measured.
- silent: 3 — Workload and device-speed variation commonly changes recovery time without a filesystem error.

### D62
- contract: VM clients doing I/O outside the buffer system must provide the correct device, block range, and live transaction to UndoZero.
- source: logbuf/buffer.c:2416 "that do not use the buffer system. It is expected that this would not be"
- violation: The VM reports the wrong offset, omits the last block, or supplies a null transaction for a newly allocated extent.
- at-risk: G16, G45: replay zeroes an incorrect range or leaves stale bytes uncovered.
- detectable: partly — null and range checks catch some errors, but the intended VM extent is external information.
- silent: 2 — Range translation mistakes can stay hidden until a crash.

- contract: For I/O that does not use the buffer cache, the VM must call the undo-zero entry with the byte range being written and must not end that transaction before the write completes.
- source: logbuf/buffer.c:2415 " * the specified range of bytes. This is to be used by the VM system for I/Os"
- violation: Strategy writes a newly allocated block from the page cache and never records an undo-zero, which is the state of the strategy module in this tree.
- at-risk: G16 fails on the VM path: a crash after the allocation commits and before the page is durable leaves the previous contents in the new block, and recovery does not zero it.
- detectable: no — the write completes through the normal iodone path, and the missing record is not checked.
- silent: 5 — the strategy code states that undo-zero processing is not implemented, and VM file writes are the normal AIX path, so the omission is routine and raises no error.

- contract: The layer that allocates a user-data block records an undo-zero for that byte range and ends that transaction only after the first write of the new data has completed, including when the virtual memory system writes the block outside the buffer pool.
- source: logbuf/buffer.c:2415 " * the specified range of bytes. This is to be used by the VM system for I/Os"
- violation: A pageout or a strategy write stores a newly allocated block without an undo-zero record, or it ends the undo-zero transaction before that write is durable.
- at-risk: G16 fails because a crash that aborts the allocation leaves the previous contents readable in the new file.
- detectable: no — elbb_UndoZero has no caller in this tree, and epia_Iodone does not update an undo-zero database.
- silent: 4 — buffered writes attach an undo-zero, but the AIX VM path the paper relies on writes file data from the virtual memory system, and that iodone path states that undo-zero handling is not implemented, with no error returned.

### D1
- contract: The storage stack must make a successfully completed log write durable across the crashes against which recovery is promised.
- source: logbuf/recover.c:894 "underlying system to really guarantee that a page is on disk"
- violation: A controller acknowledges a log write while its only copy is in volatile cache, then power fails.
- at-risk: G5, G7, G23, G29, G30: metadata can reach disk without its undo information, or acknowledged commits can disappear.
- detectable: partly — rereads may expose loss, but a successful completion cannot prove power-loss durability.
- silent: 2 — Honest completion was the intended disk interface; volatile controller caches are a plausible silent exception.

- contract: The device must preserve successfully completed log writes through subsequent power loss.
- source: logbuf/recover.c:1302 " returnVal = asevent_WaitEvent(ae);"
- violation: A drive acknowledges writes in an unprotected volatile write cache, then loses them on power failure.
- at-risk: G5, G7: metadata can become durable while its undo or redo log disappears.
- detectable: no — an acknowledged but volatile write is indistinguishable from a durable one.
- silent: 2 — Unprotected drive caches can conceal nondurability until a power failure; the historical controller configuration is unspecified.

- contract: When the async layer or the device driver reports that a write has completed, every sector of that write is on stable storage and will still be there after a crash or power loss.
- source: logbuf/recover.c:894 " * underlying system to really guarantee that a page is on disk"
- violation: A SCSI disk or the driver acknowledges the write when the bytes reach a volatile write-back cache, and a power loss then drops a log page the log package has already treated as committed, or drops it while a later metadata write remains.
- at-risk: G5, G7, G29, and G30 fail because write-ahead logging waits only for completion, so a dirty metadata buffer can be written, or a transaction can be called committed, while its log records are not actually durable.
- detectable: no — completion is success, and the loss appears only after the next crash.
- silent: 3 — write-back caches were a normal silent setting on the SCSI disks of this period, and Episode never issues a cache flush after a log force.

- contract: When the driver reports an I/O complete, that entire transfer is on stable storage and later reads, including reads after power loss, return those bytes.
- source: logbuf/recover.c:894 " * underlying system to really guarantee that a page is on disk"
- violation: A disk or controller write-back cache acknowledges the write while the bytes still sit only in volatile memory, and a power loss drops them after Episode has forced the log and then written a metadata block.
- at-risk: G5, G7, G20, G29, and G30 fail because recovery trusts a completed log page and will not undo a metadata write whose log record was lost after a false completion.
- detectable: no — asevent treats the driver's completion as truth, and the log records the I/O window from that report.
- silent: 3 — SCSI disks of this era often could enable a volatile write cache, and the file system sees a normal completion until a power loss.

### D67
- contract: The deployment must provide periodic checkpoint-driving work and sufficient metadata write bandwidth to keep the active log small when relying on fast recovery.
- source: §"Recovery Time" "every T seconds, as is the case with Episode, then the active portion of the log can rise to include all the"
- violation: Background checkpoint activity is disabled or the metadata disk stays saturated while committed dirty buffers accumulate.
- at-risk: G9–G11, G21, G22: recovery must replay more retained history, though bounded log admission can still preserve safety.
- detectable: yes — dirty-buffer age, active-log size, and checkpoint progress can be measured.
- silent: 3 — Temporary checkpoint lag during busy periods is occasional even in ordinary deployments.

- contract: The host must call the file system's sync often enough that committed dirty metadata buffers are written and the active log is checkpointed on the order of the paper's interval of T seconds.
- source: §"Recovery Time" "every T seconds, as is the case with Episode, then the active portion of the log can rise to include all the"
- violation: The update daemon is disabled or wedged, so dirty metadata stays in memory until log-full handling is forced to write it, and the active tail grows to the whole log.
- at-risk: G9, G10, and G21 fail because recovery must replay every committed update whose buffer is still dirty, so recovery time tracks the uncheckpointed tail rather than the activity at the crash.
- detectable: partly — the log-full path eventually writes buffers and can stall new transactions, which operators notice, but a merely long tail produces no error.
- silent: 2 — the described systems run a periodic sync, and a host left without it is an occasional administrative state rather than the common one.

- contract: The operating system calls the file system's sync often enough that committed dirty metadata is written and the active log is checkpointed about every T seconds.
- source: §"Recovery Time" "every T seconds, as is the case with Episode, then the active portion of the log can rise to include all the"
- violation: The update daemon is disabled, or efs_sync always finds its lock busy and never reaches elbb_SyncForce.
- at-risk: G9, G10, G21, and G22 weaken because the active log keeps every committed update whose buffer is still dirty, until log-full handling finally writes buffers.
- detectable: no — skipping sync returns without an error, and the log simply stays long.
- silent: 2 — the paper's kernels run a periodic sync, and turning it off is an occasional administrative change that produces no immediate error.

### D63
- contract: VM and allocation clients must end undo-zero transactions only after the covered first write has successfully reached disk.
- source: §"Logging Architecture" "to it completes. If the system crashes and the transaction aborts, the recovery procedure for this special"
- violation: A VM client ends its transaction on write submission or after a failed first write.
- at-risk: G16, G45: a committed kill record prevents zeroing although disk still contains stale bytes.
- detectable: partly — I/O events and transaction lifetime can be correlated, but logbuf cannot establish completion of unreported external I/O.
- silent: 2 — Submission-versus-completion mistakes can produce silent stale-data exposure.

- contract: The VM must end an undo-zero transaction only after the protected first data write has completed successfully.
- source: logbuf/tran.c:1255 " * from the VM system which has its own Async daemon to complete I/O. We"
- violation: VM ends the protection on submission or after a failed first write.
- at-risk: G16: recovery treats the kill as committed and leaves unwritten old data visible.
- detectable: partly — I/O status is available, but a falsely ended transaction is trusted.
- silent: 1 — Premature protection completion is an unusual VM integration defect that can remain hidden until failure.

- contract: For a newly allocated user-data block, the caller must record an undo-zero covering every byte that could expose old contents, and must end that transaction only when the first write of the block has completed.
- source: §"Logging Architecture" "problem by starting another transaction when the block is allocated, and ending it when the rst write"
- violation: The allocating transaction commits, the machine crashes before the first write is durable, and no undo-zero record covers the block, so the old occupant remains readable in the new file.
- at-risk: G16 fails because recovery zeroes a block only when that special transaction aborts, and without the record it has nothing to apply.
- detectable: no — the allocation looks like a normal committed metadata transaction.
- silent: 4 — the buffer path records undo-zero, but the VM strategy path used for ordinary file data does not, and those allocations proceed with no error.

- contract: For I/O that does not use the buffer cache, the VM must call the undo-zero entry with the byte range being written and must not end that transaction before the write completes.
- source: logbuf/buffer.c:2415 " * the specified range of bytes. This is to be used by the VM system for I/Os"
- violation: Strategy writes a newly allocated block from the page cache and never records an undo-zero, which is the state of the strategy module in this tree.
- at-risk: G16 fails on the VM path: a crash after the allocation commits and before the page is durable leaves the previous contents in the new block, and recovery does not zero it.
- detectable: no — the write completes through the normal iodone path, and the missing record is not checked.
- silent: 5 — the strategy code states that undo-zero processing is not implemented, and VM file writes are the normal AIX path, so the omission is routine and raises no error.

- contract: The layer that allocates a user-data block records an undo-zero for that byte range and ends that transaction only after the first write of the new data has completed, including when the virtual memory system writes the block outside the buffer pool.
- source: logbuf/buffer.c:2415 " * the specified range of bytes. This is to be used by the VM system for I/Os"
- violation: A pageout or a strategy write stores a newly allocated block without an undo-zero record, or it ends the undo-zero transaction before that write is durable.
- at-risk: G16 fails because a crash that aborts the allocation leaves the previous contents readable in the new file.
- detectable: no — elbb_UndoZero has no caller in this tree, and epia_Iodone does not update an undo-zero database.
- silent: 4 — buffered writes attach an undo-zero, but the AIX VM path the paper relies on writes file data from the virtual memory system, and that iodone path states that undo-zero handling is not implemented, with no error returned.

### D108
- contract: A caller that needs a durable point for the outside world asks quiesce to commit, and any tool that reads the raw device does so only after that commit and the matching buffer flush.
- source: logbuf/tran.c:1210 " * the outside world, like vol_fsync. A third variant allows commit of"
- violation: A fileset export, move, or raw backup reads disk blocks while dirty logged buffers or uncommitted log records still exist, or it asks only for SERIALIZE when it needed COMMIT.
- at-risk: G18 and G1 fail for that reader because old-and-new logging is allowed to write uncommitted metadata, so the raw image is not a consistent file system until recovery or a committing quiesce.
- detectable: no — quiesce returns once the requested level is reached, and a raw read has no log check.
- silent: 2 — administrative copies of a live aggregate are occasional, and nothing reports that the raw image still needs the log.

### D107
- contract: Callers keep each equivalence class small enough that every pending member's end-record reservation fits in the log.
- source: logbuf/log.c:138 " * length(aTranList) * (nested ? undoSize : fullSize) +"
- violation: A hot lock merges tens or hundreds of transactions into one class, and each ended member stays pending, holding an end reservation, until the last member ends.
- at-risk: G17 and G14 fail because the pending class fills the log, and a crash then aborts the whole class, including transactions that had already ended in memory.
- detectable: partly — the log-full path panics when the active region reaches the container; it does not report the class size as the cause.
- silent: 2 — the paper tells callers to keep classes short, and a large class under a hot directory is an occasional load spike rather than every-day operation.

### D61
- contract: Allocation and VM clients must establish undo-zero coverage for every newly exposed data byte before allocation can leave stale contents visible after a crash.
- source: §"Logging Architecture" "problem by starting another transaction when the block is allocated, and ending it when the rst write"
- violation: A new block or fragment is linked into a file without the special first-write transaction for part of its contents.
- at-risk: G16, G45, G46: an incomplete first write can reveal the block’s former owner’s bytes.
- detectable: partly — allocation-to-coverage instrumentation could detect holes; logbuf cannot infer allocations outside its API.
- silent: 2 — Missing first-write coverage can remain silent through normal operation.

- contract: Filesystem allocation code must establish undo-zero protection for all newly exposed user-data bytes before allocation becomes durable.
- source: logbuf/buffer.c:2437 " * elbb_UndoZero - Adds an undo-zero record to an existing transaction for"
- violation: A newly allocated block is linked into a file without an undo-zero record.
- at-risk: G16, G45: a crash before its first write exposes data from the previous owner.
- detectable: no — missing coverage is not distinguishable from intentional unlogged data.
- silent: 1 — Omitted first-write protection is an unusual allocation-path defect that is latent until crash timing exposes old data.

- contract: For a newly allocated user-data block, the caller must record an undo-zero covering every byte that could expose old contents, and must end that transaction only when the first write of the block has completed.
- source: §"Logging Architecture" "problem by starting another transaction when the block is allocated, and ending it when the rst write"
- violation: The allocating transaction commits, the machine crashes before the first write is durable, and no undo-zero record covers the block, so the old occupant remains readable in the new file.
- at-risk: G16 fails because recovery zeroes a block only when that special transaction aborts, and without the record it has nothing to apply.
- detectable: no — the allocation looks like a normal committed metadata transaction.
- silent: 4 — the buffer path records undo-zero, but the VM strategy path used for ordinary file data does not, and those allocations proceed with no error.

- contract: The layer that allocates a user-data block records an undo-zero for that byte range and ends that transaction only after the first write of the new data has completed, including when the virtual memory system writes the block outside the buffer pool.
- source: logbuf/buffer.c:2415 " * the specified range of bytes. This is to be used by the VM system for I/Os"
- violation: A pageout or a strategy write stores a newly allocated block without an undo-zero record, or it ends the undo-zero transaction before that write is durable.
- at-risk: G16 fails because a crash that aborts the allocation leaves the previous contents readable in the new file.
- detectable: no — elbb_UndoZero has no caller in this tree, and epia_Iodone does not update an undo-zero database.
- silent: 4 — buffered writes attach an undo-zero, but the AIX VM path the paper relies on writes file data from the virtual memory system, and that iodone path states that undo-zero handling is not implemented, with no error returned.

### D96
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

### D66
- contract: Clients must not use quiesce’s captured position as proof that later concurrently issued updates have completed.
- source: logbuf/tran.c:1220 "when the caller (elbb_QuiesceSystem) started. Other activity is allowed"
- violation: An administrative operation quiesces and assumes all subsequent writers are also included without excluding them.
- at-risk: G32, G33, G38: quiesce guarantees only the captured transaction prefix, so later writes remain outstanding.
- detectable: partly — position and transaction tracking can identify excluded activity, but not the caller’s intended administrative boundary.
- silent: 2 — Misinterpreting a concurrent snapshot boundary need not raise an error.

### D64
- contract: The VM and higher vnode layers must serialize overlapping block I/O so that waiting for an in-transit block is not invalidated by another writer.
- source: anode/strategy.c:267 "transit again. The higher-level vnode locking should guarantee this."
- violation: A second writer starts I/O to a block after a waiter has passed its in-transit check.
- at-risk: G16, G31, G35 and correct user-data ordering: later writes may be overwritten by earlier completions.
- detectable: partly — in-transit instrumentation detects some races; the critical reentry window requires higher-layer knowledge.
- silent: 2 — Cross-path VM and volume-operation races can be timing-dependent and silent.

### D48
- contract: Clients must choose a write-back mode that waits for data completion when they promise synchronous persistence.
- source: logbuf/logbuf.p.h:64 "elbb_syncLog, /* force write log, schedule buffer write, don't wait"
- violation: An upper layer returns synchronous success after elbb_syncLog or elbb_async while data is still in transit.
- at-risk: G15, G31, G35: these weaker modes do not imply the data buffer was written on return.
- detectable: partly — pending I/O is observable, but the caller’s intended external promise is not.
- silent: 2 — Confusing log synchronization with data synchronization is a plausible silent integration error.

### D57
- contract: Clients must classify buffers as logged metadata or unlogged data correctly and restrict external requests to public buffer types.
- source: logbuf/logbuf.p.h:47 "users of this package are restricted to the first two cases"
- violation: A metadata block is read as elbb_bufData or an external caller requests internal log/recovery buffer treatment.
- at-risk: G4, G5, G42, G44: buffer write and discard rules can use the wrong logging policy.
- detectable: partly — enum validation can reject internal types, but logbuf cannot independently infer metadata ownership.
- silent: 2 — Classification errors on transition paths can be silent.

### D76
- contract: Callers must check error and would-block returns before reporting successful persistence or using returned buffer contents.
- source: logbuf/tran.c:957 "RETURN CODES -- returns BUF_WOULDBLOCK only if waitOK is zero and the"
- violation: A caller ignores BUF_WOULDBLOCK from a nonwaiting force or returns success after a read/copy/I/O error.
- at-risk: G15, G23, G31, G40, G42: an unsuccessful operation does not establish the success guarantee the upper layer reports.
- detectable: partly — return codes and pending state are visible, but logbuf cannot know that a caller discarded an error.
- silent: 2 — Error-handling omissions can silently affect uncommon paths.

### D47
- contract: Clients must request the persistence level they require and distinguish transaction completion from durable commitment.
- source: logbuf/tran.c:953 "2 -- don't return until transaction has completed. This ensures"
- violation: An fsync caller uses waitOK=2 or treats EndTran as proof that its end record reached disk.
- at-risk: G15, G23, G24, G25, G29: completion or pending membership does not establish crash persistence.
- detectable: partly — call arguments are observable, but logbuf cannot know which user-visible durability promise was made.
- silent: 2 — Similar-looking completion interfaces can be misused on uncommon paths.

### D97
- contract: A later read of a block must return, sector by sector, the data of the last write to that sector that the driver has reported complete.
- source: logbuf/recover.c:892 " * We trust the log to make sure it doesn't assume a page with"
- violation: A drive cache, a multipath disk, or a host buffer returns a stale copy after a completed write, so recovery or the next mount sees an older log page.
- at-risk: G54 and G7 fail because the head, the pass number, or the redo records recovery reads are not the ones the running system forced.
- detectable: partly — a stale page often fails the pass-number or checksum test, and an older but well-formed page can be mistaken for the head.
- silent: 2 — coherent SCSI disks usually read what they just wrote, but stale cache and multipath windows are an occasional field failure.

### D95
- contract: The device and the async veneer must report a failed or unreadable log or metadata transfer as an error, and must not return success for a page that was not stored or not read.
- source: logbuf/recover.c:788 " * log page is damaged; run salvager."
- violation: The driver returns a zero completion for a write it dropped, or returns old or zeroed data for a read that the media could not perform.
- at-risk: G5 and G7 fail because the log package panics only when it sees an error, and a false success lets it treat a missing log page as durable or replay garbage as metadata.
- detectable: partly — a reported error panics the log or raises recovery failure, but a false success is invisible.
- silent: 2 — drivers usually surface hard errors, but a dropped write reported as success shows up often enough on bad cables and failing disks to be more than rare.

### D50
- contract: VM integration must flush its own dirty pages as part of a filesystem-level synchronization promise.
- source: logbuf/logbuf.p.h:335 "WRITE -- schedules all dirty buffers containing user data."
- violation: An fsync implementation flushes only logbuf buffers while dirty mapped file pages remain solely in VM.
- at-risk: G15, G35: logbuf cache completion alone does not persist user data outside that cache.
- detectable: partly — VM dirty-page enumeration can detect pending writes, but logbuf cannot inspect an independent cache.
- silent: 2 — Separate cache coordination is a plausible source of silent durability gaps.

- contract: VM integration must flush file data outside the buffer pool before claiming whole-file durability.
- source: logbuf/buffer.c:2439 " * that do not use the buffer system. It is expected that this would not be"
- violation: A file fsync flushes logbuf buffers but leaves dirty mapped pages in the VM.
- at-risk: G15: metadata synchronization alone does not persist the requested file contents; the paper explicitly disclaims user-data transactions.
- detectable: no — logbuf does not enumerate VM-resident dirty file pages.
- silent: 1 — Incomplete VM fsync integration is an uncommon port defect; ordinary writes can conceal it until a crash.

- contract: A caller that needs metadata to be persistent, such as fsync, must invoke log force or fsync-force on the buffers of that file, identified by the file's magic or by an explicit block list, and the VM must write back that file's dirty pages.
- source: §"Logging Architecture" " Meta-data changes to the disk itself can often be deferred, unless speci cally requested by an oper-"
- violation: The vnode fsync path returns without elbb_LogForce, the file-handle magic on the buffers does not match the magic passed to fsync-force, or the platform's VM flush is a stub that returns success.
- at-risk: G15, G23, and G40 fail because deferred metadata stays deferred, and fsync-force writes only the buffers the caller actually names.
- detectable: no — fsync returns success as soon as the calls it does make return, including a VM stub that does nothing.
- silent: 3 — metadata force is wired on the vnode path, but the SunOS VM integration the paper describes is incomplete, so a silent no-op page flush is a normal configuration there.

- contract: An fsync or any other call that promises durable metadata writes the file's dirty VM pages, then forces the log through that file's transaction before it returns.
- source: vnops/efs_vnodeops.c:1755 " /* Flush all buffers associated with the vnode and make sure metadata"
- violation: The vnode returns from fsync without vnvm_fsync, without epia_Fsync, or without elbb_LogForce of the vnode transaction, or the caller holds the vnode lock across the VM flush and the flush waits for that lock.
- at-risk: G15, G23, and G40 fail because the operation returns while the log end record or the user pages are still only in memory.
- detectable: no — a skipped force still returns success to the caller.
- silent: 2 — efs_fsync does call both steps, while the Sun VM hook is a stub on platforms where vnvm_fsync is compiled to return zero, so durability of user pages is silently skipped there.

### D49
- contract: Fsync clients must tag every relevant cached buffer with the correct file handle or provide the complete correct block list.
- source: logbuf/buffer.c:2019 "buffers to write out. Either a magic value is used to tag each"
- violation: A metadata or data buffer is omitted from the file’s tag chain or explicit block list.
- at-risk: G15, G40: FsyncForce writes only the selected buffers and can return with omitted updates dirty.
- detectable: partly — comparing selection against higher-level ownership can expose omissions; logbuf cannot derive that ownership.
- silent: 2 — Tracking omissions can remain silent until a crash exposes missing data.

- contract: The filesystem fsync path must identify every required cached buffer with correct file-handle tags or a complete block list.
- source: logbuf/buffer.c:2039 " * the buffers to write out. Either a magic value is used to tag each"
- violation: A file has an untagged dirty indirect block or a required block is omitted from the array.
- at-risk: G15, G40: FsyncForce does not flush omitted buffers.
- detectable: no — logbuf cannot infer the higher-level set of blocks belonging to the request.
- silent: 1 — Missing fsync selection is an uncommon tagging defect that may stay silent until crash testing.

- contract: A caller that needs metadata to be persistent, such as fsync, must invoke log force or fsync-force on the buffers of that file, identified by the file's magic or by an explicit block list, and the VM must write back that file's dirty pages.
- source: §"Logging Architecture" " Meta-data changes to the disk itself can often be deferred, unless speci cally requested by an oper-"
- violation: The vnode fsync path returns without elbb_LogForce, the file-handle magic on the buffers does not match the magic passed to fsync-force, or the platform's VM flush is a stub that returns success.
- at-risk: G15, G23, and G40 fail because deferred metadata stays deferred, and fsync-force writes only the buffers the caller actually names.
- detectable: no — fsync returns success as soon as the calls it does make return, including a VM stub that does nothing.
- silent: 3 — metadata force is wired on the vnode path, but the SunOS VM integration the paper describes is incomplete, so a silent no-op page flush is a normal configuration there.

### D40
- contract: Upper layers must use transactional object locking and report every intertransaction read/write dependency that requires equivalence-class merging.
- source: anode/tlock.h:20 "the same lock, they must be put in the same equivalence class. To minimize"
- violation: A transaction reads another’s uncommitted bitmap or anode through a nontransactional lock and commits independently.
- at-risk: G1, G12–G14: a dependent update may survive while the state it relied on is undone.
- detectable: partly — dependency instrumentation could detect missing merges; logbuf cannot infer semantic reads.
- silent: 2 — Rare nontransactional access paths can miss a merge without an immediate failure.

- contract: Transactional-lock callers must report read/write dependencies on uncommitted state by merging the corresponding transactions.
- source: anode/tlock.c:112 " elbb_EquivTran (*tlockTransP, trans, (unsigned long) &tlock->lock);"
- violation: A caller uses an ordinary lock or a null transaction when consuming another active transaction's update.
- at-risk: G13, G14: recovery may commit the dependent transaction while undoing its prerequisite.
- detectable: no — logbuf cannot discover unreported object-level dependencies.
- silent: 1 — Unreported dependencies require a higher-layer integration defect and may remain latent until a crash.

- contract: Whenever two uncommitted transactions use the same metadata object, the caller must merge them into one equivalence class with a tlock while the later transaction is still active.
- source: anode/tlock.h:20 " * the same lock, they must be put in the same equivalence class. To minimize"
- violation: A code path locks a shared anode, bitmap, or volume object with an ordinary lock, or releases it without elbt_ECMerge, and the later transaction then commits on its own.
- at-risk: G12, G13, and G14 fail because early lock release is safe only when the equivalence class aborts or commits together, and a crash otherwise keeps one update and rolls back the other.
- detectable: no — merge of a missing partner is not attempted, and both transactions commit or abort without an error.
- silent: 2 — missed tlocks have shown up on real fileset paths, and the resulting crash inconsistency produces no error while the system is up.

- contract: Higher layers put in one equivalence class every set of still-active transactions on the same log that lock the same object, and they pass an active transaction as the second argument of the merge.
- source: §"Logging Architecture" "same object during their lifetime are merged into an equivalence class (EC). An EC has the property that"
- violation: Two transactions update or read-and-update the same metadata under different tlocks, or a caller merges a transaction from another aggregate or one that has already ended.
- at-risk: G13, G14, and G1 fail in the way the paper's figure shows: one transaction commits a shared object and a crash undoes the other transaction's update to a related object.
- detectable: partly — a cross-log or inactive second transaction trips an assert in elbt_ECMerge; a missed merge of two live transactions returns success.
- silent: 2 — the tlock macros merge on the locks they cover, and a missed lock on a cold path is an occasional bug that shows up only after a crash.

### D59
- contract: Block reuse must invalidate or safely write the prior cached incarnation before exposing a new logged or unlogged incarnation.
- source: §"Data Architecture" "tion is necessary because certain bu er pool operations have to be performed when reusing a logged block"
- violation: A freed dirty metadata buffer remains cached while the same physical block is allocated as user data.
- at-risk: G1, G16, G51: a later cache write or read can revive stale contents over the new owner’s data.
- detectable: partly — cache identity and allocation-generation checks can detect reuse, but physical block keys alone do not distinguish incarnations.
- silent: 2 — Logged/unlogged transitions are uncommon paths where omissions can stay silent.

- contract: The block allocator must retain the logged-versus-unlogged classification and execute the required buffer transitions when reusing blocks.
- source: logbuf/recover.c:1897 " * NBS. These must be interpreted as kill records for earlier updates to"
- violation: A metadata block is reassigned to user data while dirty metadata remains cached.
- at-risk: G16, G51: old metadata may overwrite user data or stale records may replay into a new owner.
- detectable: partly — RCVR_USERDATA and RCVR_METADATA expose some invalid histories.
- silent: 1 — Incorrect block-type transitions require an allocator defect and often cause visible recovery refusal.

- contract: The allocation bitmap's logged-or-unlogged bit must match the block's use, and the allocator must perform the buffer-pool transition when a block changes from logged to unlogged or the reverse, before the block is reused.
- source: §"Data Architecture" "the fragment is allocated, and whether the fragment represents logged or unlogged data. This last distinc-"
- violation: A freed metadata block is handed out as user data, or the reverse, without killing the old buffer and without the bitmap bit changing in the same transaction.
- at-risk: G1 and G51 fail because a logged image is written as an unlogged block, or an old logged buffer is written back over the new occupant, and recovery then skips or replays the wrong records.
- detectable: partly — recovery raises a user-data or metadata error for some bad reuse orders, but a wrong bitmap bit alone is not checked against the buffer type.
- silent: 2 — reuse is continuous, and a missed transition is silent until a later crash, which makes it occasional rather than routine in a year of operation.

- contract: The bitmap's logged-or-unlogged mark, the anode's logged flag, and the buffer type agree, and a block that changes from one class to the other is killed or undo-zeroed first.
- source: §"Data Architecture" "tion is necessary because certain bu er pool operations have to be performed when reusing a logged block"
- violation: A metadata fragment is allocated as elbb_bufData, or a freed logged block is reused as user data while a dirty logged buffer is still cached.
- at-risk: G1 and G16 fail because the update is omitted from the log, or a kill record never covers the old metadata and recovery mixes the two lives of the block.
- detectable: partly — salvage reports DIRNOTLOGGED and FILELOGGED when it walks the aggregate; the running log does not check the bitmap bit against the buffer type.
- silent: 2 — the allocator maintains the bit, and a mismatch is an occasional bug that salvage sees only when someone runs it.

### D37
- contract: Transaction clients must end their transactions in bounded time and release resources needed by other admitted transactions.
- source: §"Logging Architecture" "Transactions that run too long or modify too much data represent"
- violation: An error path leaks an active transaction or leaves it blocked forever holding an object lock.
- at-risk: G9, G20, G23, G28, G39: old history cannot be reclaimed and forcing or shutdown may never finish.
- detectable: partly — age and active-transaction monitoring can expose a suspect transaction, without a universal deadline.
- silent: 2 — Leaked transactions on uncommon failure paths can remain unnoticed until pressure develops.

- contract: Filesystem callers must finish active transactions rather than leave them open indefinitely.
- source: logbuf/log.c:1703 " * Each running transaction is assumed to need MAX_TRAN_SIZE of log"
- violation: An error path forgets EndTran and pins the log tail throughout continued operation.
- at-risk: G9, G17, G39: the log fills and checkpoint, admission or shutdown stalls.
- detectable: yes — transaction age and pending state can be monitored.
- silent: 1 — Leaked active transactions generally cause visible log pressure or shutdown hangs.

- contract: Callers must keep each transaction within the reservation the log assumed for them and must end it, splitting any larger operation into such transactions.
- source: §"Logging Architecture" "exceed the space available in the log. Transactions that run too long or modify too much data represent"
- violation: A fileset or directory operation logs more than the presumptive maximum, or never calls EndTran, so the reservation no longer covers the tail the transaction pins.
- at-risk: G17 fails because admission control reserves a fixed size per transaction, and a larger one, or one that never ends, pins the log until new transactions cannot start or the circular buffer is overrun.
- detectable: partly — an oversized completed transaction prints that the reservation was raised and can assert if the log cannot hold it, but a transaction that never ends only stalls the log.
- silent: 2 — ordinary vnode operations stay inside the bound, but large administrative updates have overrun it often enough to be occasional.

- contract: The caller that starts a transaction ends it, and a thread holds at most one unnested transaction at a time.
- source: anode/block_alloc.c:1141 " * CAUTIONS -- This violates the basic rule that a single thread will not"
- violation: A vnode path returns without elbt_EndTran, or one thread starts a second unnested transaction while the first is still active.
- at-risk: G17 and G20 fail because the abandoned transaction pins the log tail until the log-full path panics, and a second unnested transaction can deadlock the thread that would have ended the first.
- detectable: partly — log-full handling eventually panics with a printed reason; a deadlock waits with no error return.
- silent: 2 — the anode layer pairs start and end, and a leaked transaction is an occasional bug that the operator sees as a hung or panicked server.

### D12
- contract: The execution environment must eventually schedule threads and I/O workers needed to end transactions and write buffers.
- source: logbuf/tran.c:1239 "from the VM system which has its own Async daemon to complete I/O. We"
- violation: The VM write daemon is disabled or starved while commit waits for its undo-zero transaction.
- at-risk: G23, G28, G33, G39: log space and completion depend on this forward progress.
- detectable: partly — outstanding work and starvation can be monitored, without a definitive finite deadline.
- silent: 2 — Temporary worker starvation is plausible, persistent silent starvation less common.

- contract: The scheduler must allow transaction owners and I/O completion workers to run while other threads wait for them.
- source: logbuf/tran.c:1215 " elbt_TranUnlockAndSleep(tP,tP);"
- violation: A high-priority waiter starves the only thread that can finish its transaction or I/O.
- at-risk: G15, G39: forced commit and shutdown lose eventual completion.
- detectable: yes — scheduler and wait-state tracing can show starvation.
- silent: 1 — Scheduler starvation generally manifests as visible unresponsiveness.

- contract: The scheduler and the VM I/O daemon keep running the threads that end transactions, finish undo-zero I/O, and write dirty buffers while other threads wait for log space.
- source: logbuf/tran.c:1239 " * from the VM system which has its own Async daemon to complete I/O. We"
- violation: A high-priority thread spins waiting for a transaction while it holds the buffer or vnode lock the transaction needs, or the VM daemon that would end an undo-zero never runs.
- at-risk: G17, G28, and G32 fail because log-full handling and quiesce wait forever and no commit or checkpoint completes.
- detectable: no — the wait is a sleep, and the log returns no error.
- silent: 2 — priority inversions on these kernels show up under occasional heavy metadata load, as a hung server with no logged I/O error.

### D55
- contract: Callers must treat no-read buffer allocation as requiring initialization of every byte they will expose or preserve.
- source: logbuf/buffer.c:970 "(1) Just allocate a buffer (for overwriting an entire disk block."
- violation: CreateBlock is followed by a partial overwrite and the remaining recycled memory is written as file contents.
- at-risk: G1 and additional source-implied confidentiality/correct-block-content guarantee: unwritten bytes need not contain valid disk data or zeros.
- detectable: partly — byte-initialization tracking could detect uninitialized regions; ordinary dirty flags cannot.
- silent: 2 — Partial initialization can expose stale bytes without any I/O error.

- contract: Callers using CreateBlock without a disk read must initialize all bytes that can become visible or significant before writeback.
- source: logbuf/buffer.c:974 " * (1) Just allocate a buffer (for overwriting an entire disk block."
- violation: Only part of a fresh cache buffer is initialized and the whole block is written to disk.
- at-risk: G1, G16: uninitialized memory becomes metadata or file contents.
- detectable: partly — debug randomization helps expose misuse, but no initialized-byte map is maintained.
- silent: 1 — Partial initialization is an uncommon caller defect and may expose garbage without an explicit I/O error.

### D54
- contract: Callers must keep new-data bytes stable across logging and copying them into the destination buffer.
- source: logbuf/buffer.c:1456 "LogWrite(tranId, LOGREC_DATA, newDataLen, offset, bP, newData,"
- violation: A concurrent thread changes newData after LogWrite records it but before LOGCOPY installs it.
- at-risk: G4, G7, G42: recovered new data differs from the live modification that was acknowledged.
- detectable: partly — snapshot comparison could detect a race, but ordinary logging performs no independent source-version check.
- silent: 2 — Shared or user-controlled source memory can change silently unless callers stabilize it.

- contract: Callers must keep source data and its declared address-space classification valid until a modification call finishes copying and logging it.
- source: logbuf/buffer.c:1436 " IN osi_uio_seg_t newDataSource, /* address space of newData ptr */"
- violation: A user buffer changes concurrently between log copying and home-buffer copying, or a user pointer is marked OSI_UIOSYS.
- at-risk: G4, G42: logged new bytes may differ from the actual update, or copying faults.
- detectable: partly — address faults are observable, but concurrent valid data changes need not be.
- silent: 1 — Unstable copy sources are uncommon in the described local kernel callers and often cause a visible fault.

### D35
- contract: Upper layers must construct transactions whose committed boundaries preserve filesystem invariants.
- source: §"Logging Architecture" "After each transaction, the le system is consistent, if"
- violation: A large truncate commits a bitmap free before removing the last reachable pointer in another independent transaction.
- at-risk: G1, G19: perfect atomic replay still restores a logically inconsistent committed state.
- detectable: partly — a full invariant checker could detect the result, but logbuf lacks filesystem semantics.
- silent: 2 — Unusual multi-step operations can contain latent boundary mistakes.

- contract: Filesystem transaction boundaries must enclose a logically consistent complete metadata operation.
- source: logbuf/tran.c:435 "void elbt_EndTran(IN elbt_TranRec_t tranId)"
- violation: A caller ends a transaction after allocating a block but before installing its required reference.
- at-risk: G1, G2: atomic replay preserves an inconsistent application-level state.
- detectable: no — logbuf cannot infer directory or allocation invariants from byte updates.
- silent: 1 — Incorrect transaction boundaries are uncommon integration defects that can remain latent until a crash.

- contract: Filesystem callers must split oversized operations into bounded transactions that each preserve filesystem consistency.
- source: logbuf/log.c:1703 " * Each running transaction is assumed to need MAX_TRAN_SIZE of log"
- violation: Deleting a huge file is issued as one transaction or leaves an inconsistent intermediate truncation.
- at-risk: G17, G19: reservation can be exceeded or a crash can expose an inconsistent intermediate state.
- detectable: partly — transaction-size checks detect excess, but semantic inconsistency needs higher-layer validation.
- silent: 1 — Oversized operations normally encounter size or log-full failures; inconsistent intermediate states are less directly visible.

- contract: Each transaction the caller commits must take a consistent metadata state to another consistent one, including directory, bitmap, indirect-block, anode-table, and clone copy-on-write updates.
- source: §"Logging Architecture" "operations, followed by a deletion of the empty le. After each transaction, the le system is consistent, if"
- violation: A vnode operation commits a directory entry without the anode, or updates a copy-on-write pointer in a different transaction from the block allocation that the pointer names.
- at-risk: G19 and G1 fail because replay is faithful: it will durably keep the inconsistent transaction and, after a crash, that is the metadata the file system serves.
- detectable: no — the log cannot tell a consistent group of updates from an inconsistent one.
- silent: 2 — the split of large operations is a standing source of missed pairings, and a crash in between is the only symptom, so a missed pairing can sit unnoticed until then.

### D34
- contract: Upper filesystem layers must bracket every consistency-relevant metadata change in the appropriate logged transaction.
- source: §"Component Architecture" "By making all le system meta-data modi cations within atomic transactions, the"
- violation: A directory or bitmap update bypasses logging, uses a null transaction, or requests an unlogged modification.
- at-risk: G1–G8, especially G4 and G42: recovery has no old/new record for that change.
- detectable: partly — API instrumentation could detect bypasses, but raw stores are not necessarily visible to logbuf.
- silent: 2 — Rare error paths and integration mistakes can omit logging without an immediate error.

- contract: Filesystem callers must route every metadata modification through logged buffer operations in a valid transaction.
- source: logbuf/buffer.c:1422 " * if the tranId is not the invalid transaction id and the logRequest"
- violation: An anode or directory writer changes metadata directly or disables logRequest.
- at-risk: G1, G4, G6: recovery has no old/new record for that update.
- detectable: partly — API checks catch some bad arguments, but bypass writes are not generally visible.
- silent: 2 — A bypass logging path can run successfully for long periods; its silent incidence depends on unmeasured caller defects.

- contract: The anode, directory, and vnode layers must make every metadata update, and only metadata updates, through a logged buffer operation inside a transaction.
- source: §"Logging Architecture" "requires only that the meta-data be consistent. Episode logs only meta-data changes. Although restricting"
- violation: A directory, bitmap, indirect block, or anode is written as user data or by a raw device write, or a user-data block is passed to the log as a logged buffer.
- at-risk: G1 and G4 fail because replay never sees the metadata change, or it tries to undo and redo user data and then leaves the metadata image inconsistent.
- detectable: no — the log records what it is given and has no second copy of the container type.
- silent: 1 — the callers in this tree mark directories, bitmaps, and anodes logged and send them through elbb_Modify, so a bypass in ordinary operation is rare.

- contract: Every update to directories, allocation bitmaps, indirect blocks, and anode tables is made through a logged buffer transaction that records the old and new bytes.
- source: §"Component Architecture" "made to any le system meta-data, both the original and new values of the updated data. Furthermore,"
- violation: A higher layer writes a metadata block through the raw device or through an unlogged buffer, or it modifies the bytes in place without elbb_Modify.
- at-risk: G1, G4, and G6 fail because recovery never sees the update and cannot undo or redo it.
- detectable: no — the log records only what callers submit, and an unlogged metadata write looks like ordinary user data.
- silent: 1 — the anode and vnode paths in this tree use logged buffers for those structures, and a bypass would be a rare code fault.

### D38
- contract: Nested-transaction callers must keep the new transaction plus its parent within the reservation for a single ordinary transaction.
- source: logbuf/log.c:1674 "transaction size plus old transaction size will be less than the"
- violation: A caller supplies oldTranId to bypass admission and then logs a second full-sized operation.
- at-risk: G17, G27: nonblocking nested admission is safe only under the combined size bound.
- detectable: yes — parent and nested log-consumption accounting could detect excess.
- silent: 1 — Supplied nesting is intended for small undo-zero work.

- contract: Forced nested undo-zero transactions and their parent must fit within the single-transaction space bound.
- source: logbuf/log.c:1693 " * transaction size plus old transaction size will be less than the"
- violation: A caller creates enough forced child coverage to exceed its parent's reserved space.
- at-risk: G17, G16: forced admission bypasses normal space checks and can exhaust the log.
- detectable: partly — later log-full and size assertions expose excess, possibly too late.
- silent: 1 — Excess forced reservation is uncommon and tends to surface as a full log or assertion.

- contract: A caller that force-starts a nested undo-zero transaction must keep that transaction's reservation plus its parent's within the size of one maximum transaction.
- source: logbuf/log.c:1673 " * space in the log. The caller is guaranteeing that the new"
- violation: The VM or the anode layer nests an undo-zero transaction whose combined size exceeds one maximum transaction, and the log admits it without checking free space.
- at-risk: G17 fails because the force path skips the free-space test, so the nested records can extend the active log past the circular buffer.
- detectable: no — the force path is defined to proceed regardless of free space.
- silent: 2 — nested undo-zero is used on the allocation path, and an overrun is occasional under heavy allocation rather than routine.

- contract: A caller that starts a nested undo-zero transaction while the log is full keeps that transaction, plus the transaction it nests under, inside the maximum size of one transaction.
- source: logbuf/log.c:1673 " * space in the log. The caller is guaranteeing that the new"
- violation: The VM or the buffer package nests an undo-zero whose combined size exceeds one transaction reservation, and the force path skips the free-space check.
- at-risk: G17 and G27 fail because the nested start is allowed to proceed and can wrap the log that G20 still needs for undo.
- detectable: partly — a later log-full panic names data or tran overflow; the nested start itself returns success.
- silent: 2 — ordinary undo-zero records are a few bytes, and a nested overflow would be an occasional bug rather than steady operation.

### D42
- contract: Callers merging equivalence classes must provide an active second transaction.
- source: logbuf/tran.c:642 "second tran must be active."
- violation: A caller invokes ECMerge after the current transaction has ended or committed.
- at-risk: G13, G14, G26: a previously committed class cannot retroactively share atomic fate with new work.
- detectable: yes — ECMerge checks the second transaction’s activity.
- silent: 1 — The explicit assertion normally makes misuse visible.

- contract: Callers must supply an active second transaction when requesting an equivalence-class merge.
- source: logbuf/tran.c:648 " * second tran must be active."
- violation: A stale completed transaction ID is passed as the new merge target.
- at-risk: G13: the intended dependency cannot be safely attached to a running transaction.
- detectable: yes — the transaction manager asserts the active-state precondition.
- silent: 1 — An inactive merge target normally trips the transaction assertion.

- contract: Whenever two uncommitted transactions use the same metadata object, the caller must merge them into one equivalence class with a tlock while the later transaction is still active.
- source: anode/tlock.h:20 " * the same lock, they must be put in the same equivalence class. To minimize"
- violation: A code path locks a shared anode, bitmap, or volume object with an ordinary lock, or releases it without elbt_ECMerge, and the later transaction then commits on its own.
- at-risk: G12, G13, and G14 fail because early lock release is safe only when the equivalence class aborts or commits together, and a crash otherwise keeps one update and rolls back the other.
- detectable: no — merge of a missing partner is not attempted, and both transactions commit or abort without an error.
- silent: 2 — missed tlocks have shown up on real fileset paths, and the resulting crash inconsistency produces no error while the system is up.

- contract: Higher layers put in one equivalence class every set of still-active transactions on the same log that lock the same object, and they pass an active transaction as the second argument of the merge.
- source: §"Logging Architecture" "same object during their lifetime are merged into an equivalence class (EC). An EC has the property that"
- violation: Two transactions update or read-and-update the same metadata under different tlocks, or a caller merges a transaction from another aggregate or one that has already ended.
- at-risk: G13, G14, and G1 fail in the way the paper's figure shows: one transaction commits a shared object and a crash undoes the other transaction's update to a related object.
- detectable: partly — a cross-log or inactive second transaction trips an assert in elbt_ECMerge; a missed merge of two live transactions returns success.
- silent: 2 — the tlock macros merge on the locks they cover, and a missed lock on a cold path is an occasional bug that shows up only after a crash.

### D11
- contract: The execution environment must eventually schedule threads and I/O workers needed to end transactions and write buffers.
- source: logbuf/tran.c:1239 "from the VM system which has its own Async daemon to complete I/O. We"
- violation: The VM write daemon is disabled or starved while commit waits for its undo-zero transaction.
- at-risk: G23, G28, G33, G39: log space and completion depend on this forward progress.
- detectable: partly — outstanding work and starvation can be monitored, without a definitive finite deadline.
- silent: 2 — Temporary worker starvation is plausible, persistent silent starvation less common.

- contract: VM integration must drive outstanding first-write I/O and finish its undo-zero transactions independently of log-space waiters.
- source: logbuf/tran.c:1240 "can safely wait for it to end its undo zeros."
- violation: The only VM worker able to finish a first write is blocked trying to start another ordinary transaction on the same full log.
- at-risk: G28, G33, G39, G46: nested transactions never end, so quiescing or admission can deadlock.
- detectable: partly — worker dependency and wait graphs can expose this cycle.
- silent: 1 — A persistent cycle generally becomes an observable hang.

- contract: The VM must independently drive outstanding undo-zero I/O to completion while logbuf waits.
- source: logbuf/tran.c:1256 " * can safely wait for it to end its undo zeros."
- violation: The only VM flush worker is blocked trying to start a transaction behind its own pending undo zero.
- at-risk: G17, G39: log-space recovery or quiescing deadlocks.
- detectable: yes — pending I/O and wait dependencies can reveal lack of progress.
- silent: 1 — A stalled VM completion worker usually produces an observable synchronization hang.

- contract: While quiesce waits for undo-zero transactions, the VM's own asynchronous daemon must keep running and must end those transactions when its I/O completes.
- source: logbuf/tran.c:1239 " * from the VM system which has its own Async daemon to complete I/O. We"
- violation: The thread blocked in quiesce is the thread that would complete the VM I/O, or the daemon stops, so the undo-zero transactions stay active and quiesce never returns.
- at-risk: G32, G33, and G38 fail because quiesce is defined to wait for those transactions, and a stuck daemon means commit and serialization do not finish.
- detectable: yes — the quiesce call hangs and clients stop making progress.
- silent: 1 — the hang is visible, and on the described AIX integration the daemon is a separate thread.

- contract: The scheduler and the VM I/O daemon keep running the threads that end transactions, finish undo-zero I/O, and write dirty buffers while other threads wait for log space.
- source: logbuf/tran.c:1239 " * from the VM system which has its own Async daemon to complete I/O. We"
- violation: A high-priority thread spins waiting for a transaction while it holds the buffer or vnode lock the transaction needs, or the VM daemon that would end an undo-zero never runs.
- at-risk: G17, G28, and G32 fail because log-full handling and quiesce wait forever and no commit or checkpoint completes.
- detectable: no — the wait is a sleep, and the log returns no error.
- silent: 2 — priority inversions on these kernels show up under occasional heavy metadata load, as a hung server with no logged I/O error.

### D84
- contract: Callers must not mix logged and unlogged dirty modifications to the same logged buffer between writebacks.
- source: logbuf/buffer.c:1453 " /* Require that updates to logged buffers are either always logged or"
- violation: A caller first dirties a metadata buffer without logging and then performs a logged edit.
- at-risk: G4, G5: the age queue no longer describes every dirty byte's recovery requirements.
- detectable: partly — the relevant assertions are present but disabled with #if 0.
- silent: 1 — Mixed logging requires an unusual caller path, although disabled assertions make latent misuse possible.

- contract: Callers must modify a logged buffer only through Modify, Fill, or Initialize, and must not mix logged and unlogged updates to the same buffer.
- source: logbuf/buffer.c:1442 " /* Require that updates to logged buffers are either always logged or"
- violation: A caller stores into the buffer's data pointer, or logs one update to a buffer and writes the next update with logging off, so the log does not contain the bytes that later reach disk.
- at-risk: G4, G6, and G7 fail because the old and new values in the log are not the update that the dirty buffer holds, and replay restores the wrong bytes.
- detectable: no — the checks that would reject a mixed update are compiled out, and a direct store is not looked for.
- silent: 1 — the anode paths use the modify routines consistently, so a direct store in the described system is a rare bug rather than a routine event.

- contract: Every modification of a buffer that is being logged is itself logged, and a buffer that is not logged is never given a log record.
- source: logbuf/buffer.c:1442 " /* Require that updates to logged buffers are either always logged or"
- violation: A caller passes logRequest false for a dirty logged buffer, or logRequest true for an unlogged user-data buffer.
- at-risk: G4 and G42 fail on the first case, so a later crash restores or keeps bytes the transaction changed without a record; the second case logs user data into the metadata recovery stream and can trip G52.
- detectable: no — the assert that would catch this is compiled out under #if 0.
- silent: 2 — the shipped callers pass the flag consistently, but a mistaken call is silent and the check cannot fire.

### D41
- contract: Callers must serialize access to shared metadata objects while their values are read or changed.
- source: anode/tlock.c:99 "lock_ObtainWrite_r (&tlock->lock);"
- violation: Two callers update overlapping anode bytes without holding the object’s write lock.
- at-risk: G2, G4, G42: old values or new values can describe interleaved changes rather than either operation.
- detectable: partly — lock checking can expose missing ownership, but logbuf’s internal lock does not establish object semantics.
- silent: 2 — Uncommon access paths can bypass object locking silently.

- contract: Higher layers must serialize conflicting accesses to the contents of each metadata object.
- source: anode/tlock.c:99 " lock_ObtainWrite_r (&tlock->lock);"
- violation: Two writers update a directory or anode without its transactional lock.
- at-risk: G1, G2: byte-level logs cannot repair lost semantic updates or inconsistent before-images.
- detectable: partly — races may assert, but valid-looking conflicting changes can pass.
- silent: 1 — Missing object locks are unusual in the supported code and often manifest under concurrency.

- contract: A higher layer holds the container lock across an anode metadata operation so two transactions do not update that container together.
- source: anode/anode.c:2175 " * LOCKS USED -- The container is assumed to be locked by a higher level to"
- violation: Two threads call epia_Write on the same anode without the vnode or container lock.
- at-risk: G2 and G19 fail because the two transactions interleave byte updates inside one block and the log's per-transaction images no longer describe a serial order.
- detectable: no — the anode layer does not take that lock itself.
- silent: 1 — the vnode operations take the tlock before they call the anode layer, so an unlocked call is a rare bug.

### D56
- contract: Callers may omit old-value logging only for genuinely new storage whose old contents need not be restored after abort.
- source: logbuf/buffer.c:1589 "do not have to be logged, i.e. the buffer was created by CreateBlock."
- violation: Initialize or Fill with saveOld=false is used on reachable preexisting metadata.
- at-risk: G3, G6, G43: recovery cannot undo the lost previous contents.
- detectable: partly — allocation-generation tracking could verify newness, but logbuf does not know reachability.
- silent: 2 — Misclassifying a reused block can stay invisible until abort or recovery.

- contract: Callers may omit old-value logging only for genuinely new block initialization whose old contents need not be restored.
- source: logbuf/buffer.c:1602 " * do not have to be logged, i.e. the buffer was created by CreateBlock."
- violation: Initialize is used to overwrite live metadata that must survive transaction abort.
- at-risk: G6, G43: redo-only initialization has no before-image for undo.
- detectable: no — logbuf cannot infer whether the old bytes were semantically disposable.
- silent: 1 — Misuse of initialization is uncommon in stable metadata callers but may stay hidden until crash undo.

- contract: Callers must use buffer initialization only for a block just created with CreateBlock, whose previous contents must not be restored.
- source: logbuf/buffer.c:1588 " * By initialization, we mean modification in the case where the old data"
- violation: A caller initializes an existing metadata block, so the log gets the new bytes and not the old ones, and an abort cannot put the old bytes back.
- at-risk: G4 and G6 fail because undo has no old value, and recovery either leaves the new bytes in place or writes a redo of data the aborted transaction should not keep.
- detectable: no — initialization is accepted whenever the caller asks for it.
- silent: 1 — initialization is tied to block creation in the anode code, and using it on a live block is rare.

- contract: Callers log a new block with elbb_Initialize or CreateBlock, and they log an existing metadata block with the old bytes included.
- source: logbuf/buffer.c:1588 " * By initialization, we mean modification in the case where the old data"
- violation: A caller uses a full old-and-new record on a CreateBlock buffer, or uses Initialize on a block that already holds live metadata.
- at-risk: G6 and G43 fail because undo writes back uninitialized old bytes, or redo has no old image for a block that recovery must restore.
- detectable: no — both calls are legal, and recovery applies whichever image was logged.
- silent: 1 — the anode paths choose CreateBlock for new pages and Modify for existing ones, so a swapped call is a rare coding fault.

### D60
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

### D69
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

### D58
- contract: Block allocation must not reuse freed metadata for unlogged data until the freeing transaction and its prior dependencies have committed.
- source: logbuf/buffer.c:1361 "metadata block has committed, which implies that all transactions that"
- violation: A block becomes file data while an earlier metadata transaction on that block can still be undone.
- at-risk: G1, G51–G53: old metadata replay can overwrite user data or recovery must reject the conflicting history.
- detectable: partly — kill-record analysis can raise RCVR_METADATA or RCVR_USERDATA; not every conflict is necessarily represented.
- silent: 2 — Reuse ordering errors can remain latent until a crash.

- contract: The allocator must commit earlier metadata modifications before a later user-data kill makes their history obsolete.
- source: logbuf/recover.c:1937 " RECVR_RAISE (RCVR_METADATA);"
- violation: A block is reused for user data while a preceding metadata update is still uncommitted.
- at-risk: G53, G1: recovery rejects this history instead of safely discarding its old records.
- detectable: yes — HandleKillRecords raises RCVR_METADATA for the forbidden ordering.
- silent: 1 — Forbidden metadata-to-data ordering is explicitly detected during recovery.

- contract: The allocator must not leave an uncommitted kill record newer than ordinary records on the same block, and every record a committed kill skips must already be committed.
- source: logbuf/recover.h:84 " * record on the same block. The transaction contain such records must have"
- violation: A new metadata update is logged for a block while an undo-zero kill of that block is still uncommitted, or the kill would skip a record whose transaction has no end record.
- at-risk: G51, G52, and G53 fail closed: recovery raises user-data or metadata failure and does not finish replay, so the aggregate is left unrestored.
- detectable: yes — recovery raises RCVR_USERDATA or RCVR_METADATA when it sees that order.
- silent: 1 — the bad order is rare in the allocator as written, and when it is present recovery reports it rather than succeeding quietly.

- contract: The allocator does not hand a freed block out again until the freeing transaction has committed, and a committed zero-fill kill record is the newest record that may precede the block's next use.
- source: anode/block_alloc.c:565 " * return. Recently freed blocks are not okay if the transaction in which"
- violation: A newly allocated metadata or user block receives records while an older uncommitted update or an uncommitted zero-fill is still in the active log for that address.
- at-risk: G51, G52, and G53 fail: recovery raises RCVR_USERDATA or RCVR_METADATA and stops, leaving the aggregate dirty.
- detectable: yes — the next recovery raises one of those two codes when the kill order is wrong.
- silent: 1 — the freed-block list withholds the block until commit, and the violation is reported at recovery rather than ignored.

### D24
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

### D25
- contract: Aggregate creation must allocate at least the minimum log space required for its block size and intended admitted workload.
- source: logbuf/log.c:848 "minSize = (load * elbl_MinTranReservation(dP->blkSize)) +"
- violation: An administrator constructs an undersized log or chooses a minimum supporting too little concurrent work.
- at-risk: G17, G28: initialization may reject the log, or operations cannot obtain useful admission capacity.
- detectable: yes — minimum-size checks and observed admission pressure expose inadequate sizing.
- silent: 1 — An undersized log usually generates a visible rejection or stall.

- contract: Provisioning must allocate a log large enough for the minimum transaction reservation and safety margin.
- source: logbuf/log.c:1713 " * is large enough for at least one transaction, we also proceed if"
- violation: An aggregate is initialized with fewer pages than its transaction and block-size configuration needs.
- at-risk: G17: admission cannot guarantee room for one transaction and progress.
- detectable: yes — initialization and log-full checks can reject inadequate space.
- silent: 1 — Undersized logs are rejected during attachment rather than silently violating the bound.

- contract: The log must be at least large enough for one maximum transaction plus the reserve of buffers that are allowed to be in transit, for the block size and the concurrency the file system will start.
- source: logbuf/log.c:1694 " * is large enough for at least one transaction, we also proceed if"
- violation: newaggr or the operator creates a log smaller than elbl_MinLogSize, or small enough that the transactions the vnode layer actually starts cannot all reserve space.
- at-risk: G17 fails because the admission check assumes that a single transaction always fits, and a smaller log either refuses to attach or cannot start the transactions the file system needs without overrunning the circular buffer.
- detectable: yes — log initialization returns a log-full error when the array is shorter than the minimum.
- silent: 1 — an undersized log fails attach with an error, so it is not a silent violation on a system that comes up.

- contract: The operator gives the aggregate a log at least as large as the minimum for its workload, and leaves that container's size and block list fixed while the aggregate exists.
- source: §"Data Architecture" "The log container does not grow or shrink"
- violation: newaggr creates a log smaller than elbl_MinLogSize, or an administrator grows, shrinks, or relocates the log container under a live aggregate.
- at-risk: G17 and G28 fail because elbl_InitLog returns LOG_LOGFULL, or a resized log moves the blocks whose pass numbers recovery uses to find the head.
- detectable: yes — an undersized log is rejected at init; a resized live log is not checked again and shows up later as a bad pass or a failed recovery.
- silent: 2 — the creation check is visible, while an offline rewrite of the log container is an occasional administrative mistake and is silent until the next crash.

### D46
- contract: Shutdown callers must stop new aggregate activity and synchronize access before closing the log.
- source: logbuf/tran.c:553 "levels have properly synchronized access to this aggregate."
- violation: A close races with a new StartTran or VM dirtying after shutdown has sampled active work.
- at-risk: G37, G39, G55: the restart record can declare clean while new changes are not covered.
- detectable: partly — aggregate activity counts can detect some races, but logbuf cannot fence every external producer.
- silent: 1 — Normal unmount protocols exclude new activity.

- contract: Higher layers must synchronize aggregate access against log shutdown and teardown.
- source: logbuf/tran.c:557 " * levels have properly synchronized access to this aggregate."
- violation: An aggregate is closed while another thread starts a modification or uses its device descriptor.
- at-risk: G39, G55: clean restart can race new updates or teardown can invalidate live state.
- detectable: partly — closed-map and transaction assertions catch some races.
- silent: 1 — Unsynchronized close is an uncommon lifecycle defect and often trips assertions.

- contract: Higher layers must allow only one writer, the kernel service or the salvager, to use an aggregate at a time, and must have stopped new transactions before shutdown of the log.
- source: logbuf/tran.c:553 " * levels have properly synchronized access to this aggregate."
- violation: Two hosts mount the same aggregate, or the salvager runs against a mounted aggregate, or shutdown runs while vnode threads are still in StartTran.
- at-risk: G1 and G55 fail because the two writers append different tails and then one of them writes a restart record over the other's committed updates.
- detectable: partly — shutdown asserts if active transactions remain, but two hosts do not see each other's in-memory state and both can finish without an error.
- silent: 2 — dual-mount and salvage-while-mounted mistakes are a known occasional administrative failure, and nothing on the disk serializes them.

- contract: Only one Episode instance writes an aggregate at a time, user-space recovery runs single-threaded, and higher layers have stopped other threads before shutdown.
- source: logbuf/tran.c:553 " * levels have properly synchronized access to this aggregate."
- violation: Two hosts mount the same disk, salvage runs against a mounted aggregate, or shutdown races with a thread still in elbb_StartTran.
- at-risk: G1, G2, and G39 fail because two logs, or a log and a salvager, write the same home blocks and the clean restart no longer describes a single history.
- detectable: partly — a second log map in one process returns LOG_LOGEXISTS; a second host is invisible.
- silent: 1 — the paper's system is a single server per aggregate, and a dual mount over a year is an unusual operational mistake.

### D30
- contract: Recovery orchestration must exclude concurrent filesystem, VM, raw-device, and administrative writes to the recovered aggregate and log.
- source: logbuf/recover.c:505 "AdjustDisk(diskHash, dP, &allocList, rcvr_env);"
- violation: A mounted filesystem changes a metadata block while user-space recovery reads and rewrites it.
- at-risk: G1, G50, G55: recovery can overwrite newer changes or declare clean a state it never analyzed.
- detectable: partly — mount and device exclusion can be checked; recovery has no version check for every competing writer.
- silent: 1 — Recovery normally runs offline.

- contract: The recovery caller must exclude concurrent filesystem writes and other recovery instances on the same aggregate.
- source: logbuf/recover.c:359 " * This code must run single-threaded in user space; it runs multi-threaded"
- violation: A mounted writer or second salvager changes blocks while recovery calculates and writes repairs.
- at-risk: G1, G50, G55: recovery has no lock protocol for coordinating these disk updates.
- detectable: partly — deployment locks could detect overlap, but this recovery code has no such protection.
- silent: 1 — Concurrent recovery or mounted recovery is an exceptional operational error and often gives visible failures.

- contract: Higher layers must allow only one writer, the kernel service or the salvager, to use an aggregate at a time, and must have stopped new transactions before shutdown of the log.
- source: logbuf/tran.c:553 " * levels have properly synchronized access to this aggregate."
- violation: Two hosts mount the same aggregate, or the salvager runs against a mounted aggregate, or shutdown runs while vnode threads are still in StartTran.
- at-risk: G1 and G55 fail because the two writers append different tails and then one of them writes a restart record over the other's committed updates.
- detectable: partly — shutdown asserts if active transactions remain, but two hosts do not see each other's in-memory state and both can finish without an error.
- silent: 2 — dual-mount and salvage-while-mounted mistakes are a known occasional administrative failure, and nothing on the disk serializes them.

- contract: Only one Episode instance writes an aggregate at a time, user-space recovery runs single-threaded, and higher layers have stopped other threads before shutdown.
- source: logbuf/tran.c:553 " * levels have properly synchronized access to this aggregate."
- violation: Two hosts mount the same disk, salvage runs against a mounted aggregate, or shutdown races with a thread still in elbb_StartTran.
- at-risk: G1, G2, and G39 fail because two logs, or a log and a salvager, write the same home blocks and the clean restart no longer describes a single history.
- detectable: partly — a second log map in one process returns LOG_LOGEXISTS; a second host is invisible.
- silent: 1 — the paper's system is a single server per aggregate, and a dual mount over a year is an unusual operational mistake.

### D14
- contract: The OS pinning and DMA services must keep I/O memory resident and mapped to the supplied bytes until completion.
- source: logbuf/recover.c:1364 "logbuf_pin(data, dev->blkSize);"
- violation: A port treats pinning as a no-op where DMA requires pinned memory and a page is reclaimed during I/O.
- at-risk: G5, G7, G31: disk transfers can contain different memory or fail after their buffers move.
- detectable: partly — faults or I/O errors expose some cases; valid but wrong transferred bytes may escape.
- silent: 1 — Correctly supported ports provide this service; silent failure is exceptional.

- contract: The OS must honor memory pinning for buffers used by asynchronous I/O.
- source: logbuf/recover.c:1376 " logbuf_pin(data, dev->blkSize);"
- violation: The VM reclaims or relocates a pinned page during device access.
- at-risk: G1, G5: DMA consumes or overwrites unrelated memory.
- detectable: partly — faults or checksums can expose damage.
- silent: 1 — Broken pinning is an unusual OS-port defect and normally leads to a fault or obvious corruption.

- contract: Memory that holds log pages and metadata buffers must remain resident, with its contents unchanged, until logbuf releases it.
- source: logbuf/logrec.h:371 "#define logbuf_pin(x, s) /* nothing */"
- violation: On a platform where the pin macro is empty, the kernel reclaims a dirty metadata or log page and later returns different bytes for the same address.
- at-risk: G4 and G5 fail because the bytes forced to the log or written to the home block are not the update the transaction made.
- detectable: no — the buffer header still says the page is valid.
- silent: 2 — AIX pins the pages, but the other kernels the paper ships on do not, and a reclaim of that memory is an occasional risk rather than an hourly one.

- contract: Memory the log pins, or hands to the driver, stays resident and unmodified until the matching I/O completes, and the virtual memory system does not write a buffer-pool page by any other path.
- source: async/async.p.h:83 "#define ASEVENT_NOPIN 16 /* do not pin/unpin data (AIXism) */"
- violation: pin fails or is a no-op and the kernel reclaims a log page or a dirty metadata buffer, or it writes that page from a paging path that never forces the log.
- at-risk: G5 and G42 fail because the bytes that reach disk are not the bytes that were logged, or the logged page is gone before the write completes.
- detectable: partly — on AIX a failed pin trips afsl_MBZ; on platforms where pin is empty, a stolen page is silent.
- silent: 1 — Episode allocates the buffer pool as kernel memory and pins log pages on AIX, and a pager writing those pages on the paper's kernels is rare.

### D36
- contract: Transaction clients must bound each ordinary transaction’s log consumption by the reservation assumed at admission.
- source: logbuf/log.c:1684 "Each running transaction is assumed to need MAX_TRAN_SIZE of log"
- violation: A vnode operation logs an unbounded large truncate in one transaction.
- at-risk: G17, G28: outstanding work can exceed the capacity reserved for it and exhaust the circular log.
- detectable: yes — reservation accounting can compare actual consumption with the admitted bound.
- silent: 1 — The paper calls this a programming error, and overrun usually produces a visible stall or assertion.

- contract: Filesystem callers must split oversized operations into bounded transactions that each preserve filesystem consistency.
- source: logbuf/log.c:1703 " * Each running transaction is assumed to need MAX_TRAN_SIZE of log"
- violation: Deleting a huge file is issued as one transaction or leaves an inconsistent intermediate truncation.
- at-risk: G17, G19: reservation can be exceeded or a crash can expose an inconsistent intermediate state.
- detectable: partly — transaction-size checks detect excess, but semantic inconsistency needs higher-layer validation.
- silent: 1 — Oversized operations normally encounter size or log-full failures; inconsistent intermediate states are less directly visible.

- contract: Callers must keep each transaction within the reservation the log assumed for them and must end it, splitting any larger operation into such transactions.
- source: §"Logging Architecture" "exceed the space available in the log. Transactions that run too long or modify too much data represent"
- violation: A fileset or directory operation logs more than the presumptive maximum, or never calls EndTran, so the reservation no longer covers the tail the transaction pins.
- at-risk: G17 fails because admission control reserves a fixed size per transaction, and a larger one, or one that never ends, pins the log until new transactions cannot start or the circular buffer is overrun.
- detectable: partly — an oversized completed transaction prints that the reservation was raised and can assert if the log cannot hold it, but a transaction that never ends only stalls the log.
- silent: 2 — ordinary vnode operations stay inside the bound, but large administrative updates have overrun it often enough to be occasional.

- contract: Each higher-level transaction stays within the reservation the log assumed for it, initially 70K and five log blocks, or within the log after that reservation has grown.
- source: logbuf/log.c:481 " * this is presumtive, not declarative; it reflects our understanding of"
- violation: A vnode or anode operation logs more than the reserved size in one transaction, and the log cannot grow the reservation without overrunning the container.
- at-risk: G17 fails, and a transaction larger than the log panics in elbl_CompleteTran or in the log-full path, so G2's commit never finishes.
- detectable: yes — the log prints that it is raising the reservation, and it asserts if the new size cannot fit.
- silent: 1 — an oversized transaction prints or panics, and the paper treats that case as a programming error rather than a normal year of operation.

### D33
- contract: Operators must invoke salvage rather than assume successful log recovery when hard errors have destroyed critical metadata or needed history.
- source: §"Component Architecture" "In such cases, the Episode salvager utility needs to be run; the salvager's performance"
- violation: After a failed recovery with unreadable active log pages, an operator forces the aggregate online without salvage.
- at-risk: G1, G11: log replay alone cannot restore lost information, and salvage loses the fast-recovery timing benefit.
- detectable: yes — recovery errors and I/O failures identify this case, although undetected corruption can escape.
- silent: 1 — Hard errors and recovery failure normally produce visible errors.

- contract: Operators must use the salvager rather than rely on log replay alone after unrecoverable active-log or critical metadata I/O damage.
- source: logbuf/recover.c:1049 " * Only resort is to run salvager"
- violation: A deployment resumes normal service after recovery fails on corrupted required log pages.
- at-risk: G1, G11: replay cannot reconstruct missing information and fsck-like salvage is required.
- detectable: yes — recovery errors and I/O failures identify the need; silent corruption remains a limit.
- silent: 1 — Failed recovery explicitly reports the need for repair; disregarding it is usually an observable operational incident.

- contract: When recovery or logging hits a hard I/O error, a bad log magic, or a checksum or pass-number failure outside the in-transit window, the operator must run the salvager and must not serve the aggregate.
- source: §"Component Architecture" "can not regenerate a consistent le system, however, such as when hard I/O errors occur while updating"
- violation: The operator ignores a recovery I/O error, forces the aggregate online, or keeps serving after the kernel panics on a log write error and is rebooted onto the same disk.
- at-risk: G1 fails because the paper's own limit is that hard errors while updating critical metadata leave a state replay cannot repair, and serving it preserves the inconsistency.
- detectable: yes — recovery raises an error and the log write path panics with an I/O message.
- silent: 2 — the error is visible, but continuing to serve after it is an occasional operator action over a year.

- contract: When recovery or a metadata I/O hits a hard error, a bad log page, RCVR_USERDATA, or RCVR_METADATA, the operator runs the salvager and leaves the aggregate unmounted.
- source: §"Component Architecture" "critical meta-data. In such cases, the Episode salvager utility needs to be run; the salvager's performance"
- violation: The operator forces the aggregate online, or ignores a panic, after a checksum failure outside the in-transit window or a kill-record conflict.
- at-risk: G1 and G8 fail because the log has already refused to finish replay, and further writes make the on-disk metadata diverge from any later salvage.
- detectable: yes — recovery raises RCVR_IOERR, RCVR_USERDATA, or RCVR_METADATA, and a metadata EIO panics with a printed block number.
- silent: 1 — these failures print or panic, so they are not silent when they happen.

### D13
- contract: The memory service must supply enough allocation capacity for the active log and recovery bookkeeping.
- source: logbuf/recover.c:1031 "TODO: is this a safe assumption ---"
- violation: Recovery on a memory-constrained host cannot allocate all active log pages and record structures.
- at-risk: G1, G9, G11: recovery cannot finish or meet its timing claim; allocation failure can panic.
- detectable: yes — allocation failures and resource accounting expose exhaustion.
- silent: 1 — Exhaustion generally produces an explicit failure rather than remaining silent.

- contract: The allocator must supply sufficient memory for the active log and recovery record structures.
- source: logbuf/recover.c:1038 " that we can read this much stuff into memory? */"
- violation: A valid large active log exhausts the recovery process address space.
- at-risk: G9, G55: recovery panics or cannot finish rather than meeting its time and completion claims.
- detectable: yes — allocation failure or process termination is visible.
- silent: 1 — Memory exhaustion normally panics or stops recovery visibly.

- contract: The recovery process must be able to allocate memory for every page of the active log and for the record index built from it.
- source: logbuf/recover.c:1031 " /* TODO: is this a safe assumption ---"
- violation: The active log is larger than the address space or the ulimit of the salvager, malloc fails, and recovery panics or raises out of the replay.
- at-risk: G8 and G10 fail because replay never finishes, so the aggregate stays dirty, and the recovery-time claim assumes the active log can be read in and applied.
- detectable: yes — allocation failure panics or raises, and the operator sees the salvager stop.
- silent: 2 — the paper's logs are a few megabytes and fit, but a large aggregate under a tight data limit fails this way occasionally.

- contract: The process that runs recovery can allocate memory for every page and record of the active log at once.
- source: logbuf/recover.c:1031 " /* TODO: is this a safe assumption ---"
- violation: The salvage process is short of address space or the active log is larger than the heap, and osi_Alloc or the recovery allocator fails.
- at-risk: G8 and G55 fail because recovery panics or unwinds before it writes the clean restart record.
- detectable: yes — SafeDumpLog panics on malloc failure, or the longjmp path returns an error the operator sees.
- silent: 1 — a failed allocation stops recovery with a panic or an error, so a year of ordinary crashes does not hide it.

### D91
- contract: Device management must use one stable canonical async-device identity for each attached aggregate.
- source: logbuf/log.c:109 " LookupLogMap(dP, lmP); \"
- violation: Two descriptors name the same disk and permit independent log attachments or conflicting cache entries.
- at-risk: G1, G58: pointer-keyed attachment checks do not exclude a second writer through an alias.
- detectable: partly — external device identity checks can detect aliases; pointer lookup alone cannot.
- silent: 1 — Device aliases require unusual attachment management and often produce visible conflicting service.

### D86
- contract: Callers requiring persistence must choose a mode that waits for the necessary data or transaction commit and check its result.
- source: logbuf/logbuf.p.h:63 " elbb_async, /* schedule write now, but don't wait for completion */"
- violation: A vnode fsync returns success after SyncForce, async release or a completion-only transaction wait.
- at-risk: G15, G40: scheduled or ended changes can still be lost on a crash.
- detectable: partly — the selected mode is visible, but the caller's promised durability is outside logbuf.
- silent: 1 — Using a scheduling-only API for persistence is an uncommon caller defect and is invisible in ordinary operation.

### D83
- contract: Callers must classify external buffers as data or logged buffers and leave internal buffer types to logbuf.
- source: logbuf/logbuf.p.h:47 " * users of this package are restricted to the first two cases"
- violation: A filesystem caller requests elbb_bufLog for a normal metadata block.
- at-risk: G5, G42: internal-type handling can bypass ordinary logging or cache rules.
- detectable: partly — type assertions exist on some paths.
- silent: 1 — Internal buffer types are not normally requested by filesystem callers.

### D79
- contract: Storage must return the bytes last durably written to the requested address or report an error.
- source: logbuf/recover.c:1328 " readBlock(&buf, returnVal);"
- violation: A read silently returns stale data or data from another block.
- at-risk: G1, G50: recovery calculates repairs from the wrong home contents; metadata lacks a general checksum here.
- detectable: partly — log checksum and page-number checks catch some log misreads, not arbitrary home-block misreads.
- silent: 1 — Silent stale or misdirected reads are unusual relative to reads that report media errors.

### D90
- contract: The aggregate layer must keep the log-location array allocated and unchanged until the log is detached.
- source: logbuf/log.c:816 " lmP->logLocnArray = logLocnArray;"
- violation: A caller frees its temporary address array after LogInit returns.
- at-risk: G5, G7: the stored pointer then supplies arbitrary destinations for log I/O.
- detectable: partly — bad addresses may cause I/O errors, but valid misdirected destinations can pass.
- silent: 1 — Prematurely freed location arrays are uncommon caller defects and commonly fault or misdirect I/O visibly.

### D80
- contract: The async service must finish all transfers before reporting their event complete.
- source: logbuf/recover.c:1302 " returnVal = asevent_WaitEvent(ae);"
- violation: The callback runs while DMA still reads the buffer that logbuf then recycles.
- at-risk: G5, G55: the durable bytes can differ from the recorded or recovered bytes.
- detectable: partly — checksums may expose damaged log pages later.
- silent: 1 — Premature DMA completion is an unusual driver defect and often corrupts checksummed log pages.

### D81
- contract: The supplied logical device must retain its block size and address interpretation for its entire log attachment.
- source: logbuf/buffer.c:1004 " bpeP = GetBufferPool(dP->blkSize);"
- violation: A device descriptor is retargeted or its block size changes while buffers remain cached.
- at-risk: G1, G5: cached blocks and log addresses refer to different physical bytes.
- detectable: partly — some size checks exist, but descriptor identity does not certify stable mapping.
- silent: 1 — Live descriptor retargeting is exceptional and commonly causes visible addressing errors.

### D87
- contract: Callers requesting commit quiescence must arrange completion of dirty-buffer and VM undo-zero writes before waiting for their transactions.
- source: logbuf/tran.c:1254 " * all dirty buffers to be written. Any other undo zero transactions are"
- violation: A higher layer waits for undo-zero commit without scheduling the data writes that end those transactions.
- at-risk: G39, G46: quiescing can wait forever.
- detectable: yes — dirty buffers and unfinished undo-zero transactions expose the unmet prerequisite.
- silent: 1 — Incorrect quiesce ordering normally hangs visibly.

### D70
- contract: The failure environment must not alter a protected log page in a way that preserves its checksum and passes its structural checks.
- source: logbuf/recover.c:1039 "if (!ValidLogPageChecksum(logBlocks[index], ldP->blkSize,"
- violation: Corruption changes both payload and checksum consistently, or two payloads collide under the configured CRC.
- at-risk: G1, G6, G7, G54: a valid checksum is an error detector, not proof that bytes are the originally written history.
- detectable: no — the available checksum and structure alone cannot distinguish such a valid-looking corruption.
- silent: 1 — Undetected CRC collisions or coordinated corruption are rare in the described nonadversarial systems.

- contract: The environment must not silently alter log pages into different records with the same accepted checksum and plausible headers.
- source: logbuf/recover.c:2603 " SameChecksum(storedCksum, calcCksum, storedCksumLen)) {"
- violation: Corruption happens to collide under CRC32 or a tool recomputes the checksum after an incorrect edit.
- at-risk: G47, G50: recovery accepts incorrect transaction or byte-update information.
- detectable: no — the available checksum cannot distinguish such pages.
- silent: 1 — Accidental CRC collisions are very rare for ordinary random corruption; unchecked formats weaken this assessment.

### D43
- contract: Callers that destroy or recycle transactional lock objects must serialize their remembered transaction before reusing the lock identity.
- source: anode/tlock.c:53 "code = elbb_LogForce(*transP, 2/*complete*/);"
- violation: A remembered transaction ID survives lock destruction and is associated with an unrelated object at the same address.
- at-risk: G13, G24: dependencies can be lost or attached to the wrong object.
- detectable: partly — lifecycle instrumentation can detect reuse, but logbuf sees only transaction IDs.
- silent: 1 — The supplied destroy/recycle helpers perform this synchronization.

- contract: Transactional-lock storage must not be recycled for a different object until its associated transaction has completed.
- source: anode/tlock.c:53 " code = elbb_LogForce(*transP, 2/*complete*/);"
- violation: An anode lock is freed and reused without tlock_Recycle or Destroy while its transaction is active.
- at-risk: G13, G24: dependency tracking can be lost or attached to an unrelated new object.
- detectable: partly — stored transaction state can identify premature reuse if the higher layer reports it.
- silent: 1 — Premature lock recycling is an uncommon lifecycle error that often exposes dependency or memory misuse.

### D51
- contract: Clients must retain valid buffer references, obey write access requirements, and release every acquired reference.
- source: logbuf/buffer.c:1432 "afsl_Assert(bufferIsWrite(bP) && (bP->refCount > 0));"
- violation: A caller modifies an unreferenced buffer after recycling, or leaks held references until the pool cannot reclaim space.
- at-risk: G28, G40, G42: wrong-buffer access or unreclaimable buffers can corrupt updates or stop progress.
- detectable: partly — reference and flag assertions catch some cases, but balanced counters alone do not establish ownership.
- silent: 1 — Many such API mistakes produce assertions or hangs.

- contract: Callers must retain a valid held writable buffer reference throughout modification and release it exactly once when finished.
- source: logbuf/buffer.c:1443 " afsl_Assert(bufferIsWrite(bP) && (bP->refCount > 0));"
- violation: A stale buffer pointer is used after Release or a leaked hold prevents reclamation.
- at-risk: G42, G39: another block can be modified or shutdown cannot reclaim its buffers.
- detectable: partly — reference and write-state assertions catch some misuse.
- silent: 1 — Stale or leaked references usually assert, corrupt visible data or impede shutdown.

### D9
- contract: The OS synchronization service must provide mutual exclusion and memory visibility for the logbuf locks.
- source: logbuf/buffer.c:750 "epi_mutex_init(&bufferLock, "buffer");"
- violation: An unsupported port implements a mutex without the required interprocessor memory ordering.
- at-risk: G2, G5, G13, G29: races can corrupt buffer contents, transaction lists, or log ordering.
- detectable: partly — assertions may catch damaged state, but subtle races can silently alter values.
- silent: 1 — Supported kernels ordinarily meet their locking interface.

- contract: The OS synchronization primitives must provide mutual exclusion and visibility of protected memory.
- source: logbuf/log.c:449 "#define map_assertlocked(map) afsl_Assert(epi_mutex_held(&(map)->mapLock))"
- violation: Two CPUs enter the same protected log-map critical section or observe stale fields after acquiring its lock.
- at-risk: G2, G5, G13: log state and transaction membership can race.
- detectable: partly — assertions catch some impossible states, not every lost update.
- silent: 1 — Broken mutex semantics are unusual on supported ports and tend to cause broad visible failures.

### D10
- contract: The OS sleep and wakeup primitives must atomically release the appropriate lock and avoid lost wakeups.
- source: logbuf/tran.c:1200 "elbt_TranUnlockAndSleep(tP,tP);"
- violation: A wakeup races with a non-atomic unlock-and-sleep operation and a forcing thread sleeps indefinitely.
- at-risk: G23, G24, G32, G33, G39: waiting callers can fail to finish despite the awaited transition.
- detectable: partly — blocked threads are observable, though recovery cannot distinguish slow work from a lost wakeup.
- silent: 1 — Lost wakeups indicate an unusual portability-layer defect.

- contract: The OS condition-variable wait must release and reacquire its mutex atomically with sleeping and must deliver notifications reliably.
- source: logbuf/buffer.c:2347 " epi_cond_broadcast (&bpeP->cond);"
- violation: A waiter misses a wakeup and never notices newly available buffer space.
- at-risk: G17, G40: transaction admission or synchronization loses forward progress.
- detectable: yes — blocked threads with a satisfied predicate can in principle be observed.
- silent: 1 — Lost wakeups generally surface as visible hangs under load.

### D7
- contract: The asynchronous I/O service must eventually complete each accepted request and signal its event with the correct result.
- source: logbuf/log.c:786 "retval = asevent_WaitEvent(ae);"
- violation: An accepted disk write never invokes iodone, or signals the wrong event.
- at-risk: G23, G31, G35, G39, G40: forced writes or shutdown may wait forever or return before the intended I/O.
- detectable: partly — a timeout or outstanding-event monitor could notice a hang, but no universal bound proves failure.
- silent: 1 — Lost completions are rare and usually manifest as visible hangs.

- contract: The async service must associate each completion and error with the correct submitted request.
- source: logbuf/recover.c:1300 " returnVal = asevent_QueueIO(buffer->adev, bp, ae);"
- violation: A driver signals completion for another request or drops an I/O error.
- at-risk: G5, G40: waiting can certify a write that never completed.
- detectable: partly — inconsistent event state can assert, but a plausible false success is invisible.
- silent: 1 — Misassociated event completion requires a driver or event-layer fault and commonly produces a hang or assertion.

### D6
- contract: The device must confine each write to its addressed sectors and preserve unrelated bytes.
- source: logbuf/recover.c:1343 "writeBlock(&buf, returnVal);"
- violation: A firmware or DMA error writes a log page over a different metadata block.
- at-risk: G1, G2: value logging cannot restore unrelated damage for which it has no record.
- detectable: partly — later log or metadata validation may reveal damage, but address correctness is not independently verified.
- silent: 1 — Misdirected writes are rare latent hardware or driver failures.

- contract: Storage writes must affect only their requested blocks and byte ranges.
- source: logbuf/recover.c:1299 " buffer->adev, buffer->blockNum, 0);"
- violation: A misdirected write damages a neighboring metadata block or an unrelated log page.
- at-risk: G1, G7: unrecorded collateral damage cannot be reconstructed from the transaction log.
- detectable: partly — damaged log pages may fail checksums; collateral metadata damage may remain silent.
- silent: 1 — Misdirected writes require unusual controller, driver or address faults; many cause visible damage.

### D8
- contract: The asynchronous I/O service must eventually complete each accepted request and signal its event with the correct result.
- source: logbuf/log.c:786 "retval = asevent_WaitEvent(ae);"
- violation: An accepted disk write never invokes iodone, or signals the wrong event.
- at-risk: G23, G31, G35, G39, G40: forced writes or shutdown may wait forever or return before the intended I/O.
- detectable: partly — a timeout or outstanding-event monitor could notice a hang, but no universal bound proves failure.
- silent: 1 — Lost completions are rare and usually manifest as visible hangs.

- contract: The async service must eventually complete every accepted request or return a failure.
- source: logbuf/recover.c:1302 " returnVal = asevent_WaitEvent(ae);"
- violation: A lost interrupt leaves an event pending forever.
- at-risk: G39, G40, G55: shutdown, fsync or recovery waits indefinitely.
- detectable: yes — elapsed-time monitoring can identify a stalled request, though this code has no general timeout.
- silent: 1 — A lost completion normally causes an observable hung operation rather than a silent successful year.

### D82
- contract: Callers must finish all updates to a dirty buffer before attaching its undo-zero transaction with UndoZeroBuffer.
- source: logbuf/buffer.c:2483 " * present. All updates to the dirty buffer have been done when this call"
- violation: The caller continues initializing the buffer after the first-write protection is attached and a write starts.
- at-risk: G16, G46: completion can certify an incomplete initialization.
- detectable: partly — update flags may expose overlap, but raw concurrent stores may not.
- silent: 1 — Updating after protection attachment requires caller misuse and may cause visible partial initialization.

- contract: The caller must attach an undo-zero record only after the new bytes are in the buffer, and must do so before ending the transaction that allocated the block.
- source: anode/anode.c:696 " * attach the undo-zero record. If we do this any earlier, the logbuf"
- violation: The caller attaches undo-zero before the new data is copied, the buffer package cleans the buffer and ends the undo-zero transaction, and the new bytes are stored only afterward.
- at-risk: G16 fails because the undo-zero transaction can commit or abort against a buffer that does not yet hold the first write, so recovery either zeroes a block the user already replaced or fails to zero a block that still holds old data.
- detectable: no — cleaning the buffer and ending the nested transaction is a normal logbuf action.
- silent: 1 — the anode write path attaches the record at release, after the copy, so the early attach is rare on the described path.

- contract: The caller of elbb_UndoZeroBuffer has finished writing the new bytes into the dirty buffer before the call, and the range lies inside that buffer.
- source: logbuf/buffer.c:2459 " * present. All updates to the dirty buffer have been done when this call"
- violation: The caller attaches the undo-zero and then keeps modifying the buffer, or the log cleans the buffer and ends the nested transaction before the new bytes are stored.
- at-risk: G16 and G46 fail because recovery zeroes a block whose new data never became durable, or it keeps a block whose allocation aborted after a partial store.
- detectable: no — the call returns after logging the fill, and it does not check that the caller has stopped writing.
- silent: 1 — the anode write path attaches the record in ReleaseBuf after the copy, which matches the comment, so a reversed order is a rare bug.

### D85
- contract: The recovery caller must exclude concurrent filesystem writes and other recovery instances on the same aggregate.
- source: logbuf/recover.c:359 " * This code must run single-threaded in user space; it runs multi-threaded"
- violation: A mounted writer or second salvager changes blocks while recovery calculates and writes repairs.
- at-risk: G1, G50, G55: recovery has no lock protocol for coordinating these disk updates.
- detectable: partly — deployment locks could detect overlap, but this recovery code has no such protection.
- silent: 1 — Concurrent recovery or mounted recovery is an exceptional operational error and often gives visible failures.

- contract: User-space recovery of one aggregate must run on a single thread, and the caller must be prepared for the recovery routines to return by longjmp.
- source: logbuf/recover.c:358 " * This code must run single-threaded in user space; it runs multi-threaded"
- violation: Two threads in the salvager call elbr_Recover at once, or a caller invokes the dump routine without a setjmp frame, so a checksum failure longjmps off the stack.
- at-risk: G8 and G55 fail because the two recoveries interleave writes of the same metadata and restart block, or the process dies and leaves a half-applied recovery.
- detectable: partly — a longjmp with no frame aborts the process, which the operator sees, but two interleaved recoveries can finish with success and a wrong disk.
- silent: 1 — the salvager runs recovery on one thread, so a concurrent second recovery in the described operation is rare.

- contract: Only one Episode instance writes an aggregate at a time, user-space recovery runs single-threaded, and higher layers have stopped other threads before shutdown.
- source: logbuf/tran.c:553 " * levels have properly synchronized access to this aggregate."
- violation: Two hosts mount the same disk, salvage runs against a mounted aggregate, or shutdown races with a thread still in elbb_StartTran.
- at-risk: G1, G2, and G39 fail because two logs, or a log and a salvager, write the same home blocks and the clean restart no longer describes a single history.
- detectable: partly — a second log map in one process returns LOG_LOGEXISTS; a second host is invisible.
- silent: 1 — the paper's system is a single server per aggregate, and a dual mount over a year is an unusual operational mistake.

### D92
- contract: The allocator must complete a user-data kill transaction before reusing that block for newer logged metadata.
- source: logbuf/recover.c:1929 " RECVR_RAISE (RCVR_USERDATA);"
- violation: New metadata is installed on a block whose user-data undo-zero transaction remains uncommitted.
- at-risk: G52, G1: undo-zero could erase newer metadata and recovery refuses the history.
- detectable: yes — HandleKillRecords raises RCVR_USERDATA when newer ordinary records precede an uncommitted kill in reverse scan.
- silent: 1 — Forbidden data-to-metadata ordering is explicitly detected during recovery.

- contract: The allocator must not leave an uncommitted kill record newer than ordinary records on the same block, and every record a committed kill skips must already be committed.
- source: logbuf/recover.h:84 " * record on the same block. The transaction contain such records must have"
- violation: A new metadata update is logged for a block while an undo-zero kill of that block is still uncommitted, or the kill would skip a record whose transaction has no end record.
- at-risk: G51, G52, and G53 fail closed: recovery raises user-data or metadata failure and does not finish replay, so the aggregate is left unrestored.
- detectable: yes — recovery raises RCVR_USERDATA or RCVR_METADATA when it sees that order.
- silent: 1 — the bad order is rare in the allocator as written, and when it is present recovery reports it rather than succeeding quietly.

- contract: The allocator does not hand a freed block out again until the freeing transaction has committed, and a committed zero-fill kill record is the newest record that may precede the block's next use.
- source: anode/block_alloc.c:565 " * return. Recently freed blocks are not okay if the transaction in which"
- violation: A newly allocated metadata or user block receives records while an older uncommitted update or an uncommitted zero-fill is still in the active log for that address.
- at-risk: G51, G52, and G53 fail: recovery raises RCVR_USERDATA or RCVR_METADATA and stops, leaving the aggregate dirty.
- detectable: yes — the next recovery raises one of those two codes when the kill order is wrong.
- silent: 1 — the freed-block list withholds the block until commit, and the violation is reported at recovery rather than ignored.

### D52
- contract: Modification callers must use the returned replacement buffer handle after operations that can replace the original.
- source: logbuf/buffer.c:1415 "cannot assume the buffer handle will not change across this call."
- violation: A client ignores nbP and continues modifying or releasing the previous buffer after log-full handling replaces it.
- at-risk: G42: subsequent updates can target stale storage or the wrong buffer identity.
- detectable: partly — generation or reference tracking could detect stale handles; a plausible reused pointer may pass checks.
- silent: 1 — Supplied call patterns normally propagate the returned handle.

- contract: Callers must use the returned buffer handle after operations that may replace the handle.
- source: logbuf/buffer.c:1426 " * cannot assume the buffer handle will not change across this call."
- violation: A caller ignores nbP and continues using the original pointer after a modifying operation.
- at-risk: G42: subsequent accesses may refer to a recycled or inappropriate buffer.
- detectable: partly — stale-reference checks are limited.
- silent: 1 — Ignoring a replacement handle requires a caller defect; repeated use tends to expose it.

- contract: After a modify, fill, or initialize, the caller uses the buffer pointer the call returns.
- source: logbuf/buffer.c:1415 " * cannot assume the buffer handle will not change across this call."
- violation: The caller keeps logging or releasing the pointer it passed in after the package has moved the block to a different buffer header.
- at-risk: G42 and G5 fail because the log record is attached to one buffer and the caller writes or forces another, so the home block and the log disagree.
- detectable: no — the old pointer can still address a live header for a different block.
- silent: 1 — the anode macros thread the returned pointer, and holding the old one is a rare bug.

### D4
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

### D53
- contract: Callers must keep modification byte ranges within the addressed block and supply accessible data in the declared address space.
- source: logbuf/buffer.c:1474 "retval = osi_copyin_r(newData, bP->data + offset, newDataLen);"
- violation: A client supplies offset plus length beyond the block, an invalid source pointer, or USER bytes labeled SYS.
- at-risk: G4, G42: copies can fault, overwrite adjacent memory, or log bytes different from those installed.
- detectable: partly — bounds and copyin validation can catch some misuse, but not valid wrong pointers.
- silent: 1 — Ordinary internal callers use bounded kernel buffers.

- contract: Callers must restrict undo-zero buffer ranges to the current buffer and provide valid byte ranges to modification APIs.
- source: logbuf/buffer.c:2500 " afsl_Assert(fillSize + offset <= bP->adev->blkSize);"
- violation: An offset or length runs beyond the block or wraps arithmetic.
- at-risk: G42, G45: the log covers the wrong bytes or memory outside the buffer is modified.
- detectable: partly — range assertions catch ordinary overflow of the block, not necessarily integer wrap.
- silent: 1 — Out-of-range calls usually assert or fault rather than remain silent.

- contract: The caller of elbb_UndoZeroBuffer has finished writing the new bytes into the dirty buffer before the call, and the range lies inside that buffer.
- source: logbuf/buffer.c:2459 " * present. All updates to the dirty buffer have been done when this call"
- violation: The caller attaches the undo-zero and then keeps modifying the buffer, or the log cleans the buffer and ends the nested transaction before the new bytes are stored.
- at-risk: G16 and G46 fail because recovery zeroes a block whose new data never became durable, or it keeps a block whose allocation aborted after a partial store.
- detectable: no — the call returns after logging the fill, and it does not check that the caller has stopped writing.
- silent: 1 — the anode write path attaches the record in ReleaseBuf after the copy, which matches the comment, so a reversed order is a rare bug.

### D45
- contract: Callers must arrange multi-buffer reservations before taking a path that holds several buffers simultaneously.
- source: logbuf/buffer.c:2194 " buffers simultaneously; this avoids deadlock."
- violation: Many threads each retain one buffer and wait for a second without reserving enough pool space.
- at-risk: G28 and log service availability: no thread can finish and release the buffers required for progress.
- detectable: partly — reservation ownership and wait graphs can expose the resource cycle.
- silent: 1 — Buffer exhaustion typically turns the error into an observable hang.

- contract: Code paths needing multiple simultaneously held buffers must reserve sufficient buffer capacity before acquisition and return their reservation.
- source: logbuf/buffer.c:2215 " * elbb_Reserve - reservation call for code paths which require multiple"
- violation: Several operations each hold one buffer and wait for another in an exhausted pool.
- at-risk: G17, G40: transactions cannot finish or flush and admission stalls.
- detectable: yes — reservations, held buffers and waits can reveal the resource cycle.
- silent: 1 — Missing capacity reservations generally lead to visible allocation deadlocks.

- contract: A caller that will hold several buffers at once reserves that many first, and the operator configures a buffer pool large enough for those reservations.
- source: logbuf/buffer.c:2306 " afsl_PAssert(code, ("Insufficient space for buffer reservation"));"
- violation: An anode path locks two blocks without elbb_Reserve, or the pool is smaller than the reservation the caller then requests.
- at-risk: G22 and G15 fail because the threads deadlock or panic while holding the dirty buffers checkpoint needs to write, so the active log cannot shrink and fsync cannot finish.
- detectable: yes — an impossible reservation panics with the insufficient-space assert; a lock-order deadlock hangs.
- silent: 1 — the panic is visible, and the shipped metadata paths reserve before the double-block operations.

### D20
- contract: Device registration must keep block sizes within the buffer and record-offset limits supported by this build.
- source: logbuf/logbuf.p.h:416 "#define BUF_MAXBUFSIZE (64 * BUF_MINBLKSIZE) /* largest buffer size */"
- violation: An operator or port registers blocks larger than the buffer maximum or representable record offsets.
- at-risk: G42, G54: allocations and 16-bit record offsets cannot faithfully represent the block.
- detectable: partly — buffer-pool and size checks can reject configurations; unchecked truncation remains possible.
- silent: 1 — The paper uses ordinary 8K blocks, well within these limits.

- contract: The configured device block size must be a supported power of two between 1 KiB and 64 KiB.
- source: logbuf/logbuf.p.h:416 "#define BUF_MAXBUFSIZE (64 * BUF_MINBLKSIZE) /* largest buffer size */"
- violation: An operator attaches a device using unsupported 3 KiB or 128 KiB logical blocks.
- at-risk: G17, G1: pool indexing and log reservation arithmetic cease to match real blocks.
- detectable: partly — VALID_SIZE and assertions check sizes, but the cited log reservation mask alone does not prove a power of two.
- silent: 1 — Unsupported block sizes are deployment mistakes usually caught by setup checks or assertions.

- contract: The device block size is a power of two, at least 1024 bytes, small enough for the recovery allocator, and it is the unit of every log and metadata address the caller passes in.
- source: logbuf/log.c:863 " afsl_MBZ(blkSize & 1023); /* must be power-of-two >= 1K */"
- violation: The aggregate is opened with a block size other than the one stamped in the superblock, or with a size below 1024 or not a power of two, so log pages and metadata blocks are read at the wrong offsets.
- at-risk: G1 and G54 fail because recovery and logging interpret the wrong bytes as log page headers and apply updates to the wrong disk addresses.
- detectable: yes — initialization asserts on the size, and the aggregate header check rejects a mismatch with the device.
- silent: 1 — newaggr and attach enforce the size, so a running system described by the paper does not silently use a bad block size.

### D32
- contract: Callers must handle RCVR_RECOVERED by discarding stale higher-layer state and retrying initialization against recovered disk contents.
- source: logbuf/log.c:737 "return RCVR_RECOVERED; /* so upper levels can clear buffers */"
- violation: The aggregate layer treats RCVR_RECOVERED as ordinary success and retains anodes loaded before recovery.
- at-risk: G1, G59, G60: later operations can reintroduce stale state despite a recovered buffer pool.
- detectable: partly — return-code handling is visible, but stale derived caches are not all visible to logbuf.
- silent: 1 — The supplied aggregate code has explicit retry handling.

- contract: Higher layers must honor recovery and initialization return codes and retry initialization after RCVR_RECOVERED.
- source: logbuf/log.c:743 " return RCVR_RECOVERED; /* so upper levels can clear buffers */"
- violation: The caller proceeds as if a normal log attachment succeeded after recovery or ignores a recovery failure.
- at-risk: G58, G59: cache invalidation and valid log attachment can be skipped.
- detectable: partly — return codes expose the condition, but logbuf cannot enforce every caller's control flow.
- silent: 1 — Ignoring initialization status is an uncommon integration error and commonly prevents usable logging.

- contract: The caller of log initialization must not have dirty buffers cached for that device, and after recovery reports that it repaired the log the caller must drop cached buffers before using the device.
- source: logbuf/buffer.c:1839 " * buffers were dirty when elbb_LogInit was called."
- violation: Log initialization is called while dirty metadata buffers are cached, or a caller of recovery keeps those buffers and writes them back over the blocks recovery just repaired.
- at-risk: G60 and G1 fail because the shutdown used to invalidate the pool writes or discards the dirty buffers against the recovered disk, and a later write of a stale buffer restores the pre-recovery image.
- detectable: no — initialization assumes the cache is clean and does not compare buffer contents with the disk.
- silent: 1 — attach kills the log pages and initializes the log before serving, so a dirty cache at that moment is rare.

### D26
- contract: Initialization callers must serialize first-time package initialization before concurrent use.
- source: logbuf/tran.c:177 "Locks: assumes no locking (single-threaded at init time). Call is"
- violation: Two mount threads enter first-time transaction initialization concurrently.
- at-risk: G2, G13, G28: lock and free-list initialization can race and lose or duplicate state.
- detectable: partly — initialization guards detect some repeats but do not by themselves serialize racing callers.
- silent: 1 — Kernel startup ordinarily initializes these services once.

- contract: Startup must initialize transaction globals without concurrent transaction users.
- source: logbuf/tran.c:178 " * Locks: assumes no locking (single-threaded at init time). Call is"
- violation: Two startup threads initialize or use transaction lists concurrently.
- at-risk: G2, G13: transaction tracking can be corrupted before ordinary locking applies.
- detectable: partly — initialization guards and list assertions may expose races.
- silent: 1 — Initialization is normally single-threaded; violating it is an unusual startup integration defect.

- contract: Transaction initialization must run single-threaded, before any thread starts a transaction.
- source: logbuf/tran.c:177 " * Locks: assumes no locking (single-threaded at init time). Call is"
- violation: Two threads call the transaction initializer concurrently during the first mount, and the free list or the locks are published half-initialized.
- at-risk: G13 and G29 fail because the transaction structures those guarantees use can be duplicated or lost, so commits and equivalence classes are recorded in the wrong objects.
- detectable: partly — a crash during initialization is visible, but a duplicated free-list link can survive into later transactions.
- silent: 1 — the first mount initializes once, before the file system accepts calls, so a concurrent second initializer is rare.

### D44
- contract: Callers waiting for transaction completion must hold no active transaction whose progress can depend on that wait.
- source: logbuf/tran.c:1313 "CAUTIONS -- The calling thread must not be holding any active transactions."
- violation: A thread forces a transaction in its own unfinished equivalence class while retaining an active member.
- at-risk: G23, G24, G32, G33, G39: the caller can wait for completion that only it can enable.
- detectable: partly — per-thread transaction and wait-graph tracking could identify the cycle.
- silent: 1 — These mistakes usually become visible deadlocks.

- contract: Callers must avoid waiting for transaction completion while holding an active transaction needed by that wait.
- source: logbuf/tran.c:1330 " * CAUTIONS -- The calling thread must not be holding any active transactions."
- violation: A thread forces a transaction in its own EC while retaining an unfinished member.
- at-risk: G13, G15, G39: the class cannot complete and the waiter deadlocks.
- detectable: yes — active transaction ownership and a wait-for graph could expose the cycle.
- silent: 1 — Self-dependent transaction waits normally produce a visible hang.

- contract: A thread that waits for other transactions to complete or commit, including quiesce, must not itself hold an active transaction.
- source: logbuf/tran.c:1313 " * CAUTIONS -- The calling thread must not be holding any active transactions."
- violation: A vnode thread calls quiesce or otherwise waits for a transaction while it still owns an active transaction that the wait needs to end.
- at-risk: G32 and G33 fail because the wait never finishes, so the caller does not get the serialization or the commit it asked for, and the transactions it holds stay uncommitted.
- detectable: yes — the file system hangs, which operators and clients see.
- silent: 1 — the hang is visible, and the calling code in this tree does not wait while holding the transaction it needs to finish.

### D31
- contract: Callers must present a clean buffer cache when initializing a log that may require recovery.
- source: logbuf/buffer.c:1839 "buffers were dirty when elbb_LogInit was called."
- violation: A caller dirties cached metadata before LogInit, then successful recovery invalidates or writes that cache.
- at-risk: G1, G55, G60: stale dirty cache contents can overwrite recovered blocks.
- detectable: yes — dirty-buffer state is inspectable at entry.
- silent: 1 — Normal mount initialization precedes metadata updates.

- contract: The caller must invoke LogInit without dirty cached buffers on the recovered device.
- source: logbuf/buffer.c:1854 " * buffers were dirty when elbb_LogInit was called."
- violation: An aggregate has dirty pre-recovery cache entries when initialization triggers recovery.
- at-risk: G55, G60: shutdown can write stale buffers over freshly recovered disk contents.
- detectable: yes — dirty flags can be inspected before recovery begins.
- silent: 1 — Normal startup precedes dirty metadata activity; misuse is an exceptional lifecycle error.

- contract: The caller of log initialization must not have dirty buffers cached for that device, and after recovery reports that it repaired the log the caller must drop cached buffers before using the device.
- source: logbuf/buffer.c:1839 " * buffers were dirty when elbb_LogInit was called."
- violation: Log initialization is called while dirty metadata buffers are cached, or a caller of recovery keeps those buffers and writes them back over the blocks recovery just repaired.
- at-risk: G60 and G1 fail because the shutdown used to invalidate the pool writes or discards the dirty buffers against the recovered disk, and a later write of a stale buffer restores the pre-recovery image.
- detectable: no — initialization assumes the cache is clean and does not compare buffer contents with the disk.
- silent: 1 — attach kills the log pages and initializes the log before serving, so a dirty cache at that moment is rare.

- contract: The caller of elbb_LogInit has no dirty buffers for that device.
- source: logbuf/buffer.c:1839 " * buffers were dirty when elbb_LogInit was called."
- violation: Log initialization recovers the log and then elbb_Shutdown writes dirty cached metadata back over the repaired blocks.
- at-risk: G60 and G1 fail because the post-recovery invalidation assumes those buffers were clean, and a dirty write restores the pre-recovery image.
- detectable: no — the comment records the assumption, and the shutdown path will write a dirty buffer.
- silent: 1 — mount initializes the log before file operations dirty the pool, so a dirty pool at LogInit is a rare call-order bug.

### D15
- contract: The CPU and compiler must make the shared 32-bit tuning assignments atomic to readers.
- source: logbuf/log.c:2602 "a 32 bit quantity is atomic w.r.t. all readers."
- violation: A port implements a shared tuning store as two separately observable halfword stores.
- at-risk: G17, G28: torn reservation or capacity limits can invalidate admission calculations or block progress.
- detectable: partly — limits can be sanity checked, but a transient torn read may leave no evidence.
- silent: 1 — Aligned 32-bit stores on the described machines normally meet the assumption.

- contract: The machine must provide atomic assignment and observation of the 32-bit tuning quantities used without reader locks.
- source: logbuf/log.c:2639 " * a 32 bit quantity is atomic w.r.t. all readers."
- violation: A port reads a torn value while a parameter is changed.
- at-risk: G17: reservation or limit calculations can use an impossible value.
- detectable: partly — range checks may catch some torn values.
- silent: 1 — The target 32-bit machines normally provide this atomicity; incompatible ports are uncommon.

- contract: An aligned store of a 32-bit value must be atomic with respect to every concurrent reader on the machine.
- source: logbuf/log.c:2602 " * a 32 bit quantity is atomic w.r.t. all readers."
- violation: A reader observes a half-updated 32-bit tuning or status word, for example a log-full threshold mixed from the old and new values.
- at-risk: G17 is the closest guarantee: a torn log-limit word can admit transactions the free log cannot hold, or refuse transactions that would have fit. I am unsure it affects any other guarantee.
- detectable: no — the torn value is used as if it were stored whole.
- silent: 1 — aligned 32-bit stores are atomic on the SPARC and POWER machines Episode runs on.

- contract: A naturally aligned 32-bit store is atomic with respect to every reader on the machine.
- source: logbuf/log.c:2602 " * a 32 bit quantity is atomic w.r.t. all readers."
- violation: A reader observes a half-updated word of a tuneable log parameter while another CPU stores it.
- at-risk: Unsure. The stated use is elbl_Tune's shared counters; a torn limit could disturb G17's admission check if a caller ever set one of those words in parallel.
- detectable: no — a torn read returns a plausible integer and the log does not checksum memory.
- silent: 1 — the hosts in the paper provide atomic aligned 32-bit stores, and the tune path is not on the crash-recovery hot path.

### D75
- contract: Tuning callers must pass appropriately typed accessible values in the package address space and copy user arguments before calling.
- source: logbuf/buffer.c:908 "caller must copyin/copyout the version string"
- violation: An ioctl wrapper passes a user pointer directly to a routine expecting a kernel-space value or an undersized destination.
- at-risk: Log service availability and G17 where reservation configuration is affected: invalid dereferences or overwritten tuning values can crash or misconfigure logging.
- detectable: partly — address-space and buffer-size validation can reject malformed arguments, but the package trusts its wrapper.
- silent: 1 — Correct wrappers normally validate arguments and faults are usually visible.

- contract: Tuning callers must supply accessible kernel-address-space values and perform user-space copyin or copyout themselves.
- source: logbuf/buffer.c:876 " * Note that elbb_Tune assumes the address of value is in its address"
- violation: An administrative interface forwards an unchecked user pointer to Tune.
- at-risk: G17: faults or unintended parameter writes can disrupt reservation and logging service.
- detectable: partly — address faults are visible, but valid wrong addresses can corrupt memory.
- silent: 1 — Incorrect address-space forwarding commonly faults visibly.

- contract: The pointer passed to the log and buffer tuning call must address memory in the caller's own address space that holds the whole value being read or written.
- source: logbuf/buffer.c:873 " * Note that elbb_Tune assumes the address of value is in its address"
- violation: A caller passes a user pointer or a short buffer, so the tune reads or writes the wrong word and changes the maximum log or the full-log fraction.
- at-risk: G17 fails if the log-full fraction or the maximum number of logs is silently changed to a value the running transactions cannot satisfy. I am unsure it affects guarantees other than admission and attach.
- detectable: no — there is no copyin check, and a bad pointer that happens to be readable is accepted.
- silent: 1 — in-kernel callers pass a kernel address, and a bad tune from user space is rare in ordinary operation.

- contract: Callers of elbb_Tune and elbl_Tune pass a pointer in the log package's address space.
- source: logbuf/buffer.c:873 " * Note that elbb_Tune assumes the address of value is in its address"
- violation: A system call passes a raw user pointer and the log stores a limit through it.
- at-risk: Unsure which of G17's limits would change. A wild store can corrupt the caller, and a truncated write can leave max-tran or log-full thresholds wrong so admission no longer matches the log.
- detectable: partly — a bad kernel pointer faults; a user pointer that happens to be mapped is written with no error.
- silent: 1 — tune is an in-kernel control, and the paper's file-system calls do not pass user pointers here.

### D18
- contract: A port must preserve the contiguous device-pointer and block-number layout used as the buffer address hash key.
- source: logbuf/buffer.c:840 "block # fields are contiguous, with the device *first*. We"
- violation: A compiler inserts padding between adev and blockNum so the fixed-length key omits part of the block number.
- at-risk: G5, G40, G42: the cache can confuse or fail to locate block identities.
- detectable: partly — layout assertions could detect this at initialization; runtime collisions need not identify the cause.
- silent: 1 — The supported ABI normally supplies the expected layout.

- contract: The compiler and ABI must lay out the device pointer immediately before the block-number field as the address hash expects.
- source: logbuf/buffer.c:842 " * block # fields are contiguous, with the device *first*. We"
- violation: An ABI inserts padding that becomes part of a hash key.
- at-risk: G1, G40: one disk address can acquire conflicting cache identities or fail lookup.
- detectable: partly — inconsistent hash behavior may be diagnosed, but no portable layout check is shown.
- silent: 1 — The supported ABI normally meets the layout assumption; a new incompatible ABI commonly fails early.

- contract: One device object and one block number must name one physical block, and the C layout must place the device pointer immediately before the block number with no padding between them.
- source: logbuf/buffer.c:839 " * note that for this key to work, we assume that the device and"
- violation: Two async device objects alias one disk, or a compiler inserts padding between the device pointer and the block number, so the address hash misses or collides.
- at-risk: G5 and G7 fail because two buffer headers for one block let one be written without the log force recorded on the other, and a hash miss serves a stale cached copy.
- detectable: partly — wildly wrong data can trip later asserts, but a duplicate device alias is served without an error.
- silent: 1 — the compilers used for SPARC and POWER lay this pair out with no padding, and one device object per aggregate is the normal open path.

- contract: One async_device object names an aggregate for the life of its buffer cache, and the compiler lays the device pointer and the block number out as one contiguous hash key with the device pointer first.
- source: logbuf/buffer.c:839 " * note that for this key to work, we assume that the device and"
- violation: A second device object is opened for the same disk, or a compiler inserts padding between adev and blockNum, so two cache entries alias or one block is looked up under the wrong key.
- at-risk: G5 and G1 fail because the log is forced for a different buffer than the one written, or a stale cached block is treated as the current metadata.
- detectable: no — the hash init succeeds either way, and there is no check that the key bytes are exactly those two fields.
- silent: 1 — one device object per mount is how the aggregate layer works, and the ABIs of the paper's compilers keep those two fields adjacent.

### D16
- contract: A port must preserve the alignment, integer widths, byte order, and structure layout expected by the native on-disk log format.
- source: logbuf/logrec.h:227 "pointers rather than bcopy (remember we want things to be fast.)"
- violation: An aggregate is recovered using a build with a different endian order or daddr_t layout and no format conversion.
- at-risk: G6, G7, G47, G54: headers, offsets, and values are decoded differently or fault.
- detectable: partly — magic, checksums, and assertions catch many incompatible layouts, but do not establish semantic compatibility.
- silent: 1 — Same-platform recovery is normal; unsupported cross-platform use is rare.

- contract: Recovery must use the same compatible on-disk integer representation, structure layout and alignment as the log writer.
- source: logbuf/logrec.h:298 "#define GetPageHdr(buf) (struct logPageHdr *)(buf)"
- violation: An aggregate is recovered on a machine with incompatible byte order or structure packing.
- at-risk: G47, G50, G54: direct structure casts interpret headers and records incorrectly.
- detectable: partly — magic, checksum and record checks reject many incompatible layouts.
- silent: 1 — Unsupported on-disk representation normally fails magic or record checks instead of silently succeeding.

- contract: The host must not require a stricter alignment than 32-bit for the log record layouts, and recovery must run with the same integer endianness and width as the writer.
- source: logbuf/logrec.h:44 " * more strict alignment than is assumed here (i.e. all data"
- violation: The aggregate is recovered on a big-endian host after being written on a little-endian host, or the CPU faults on an access the log record macros perform.
- at-risk: G4, G47, and G54 fail because pass numbers, record types, and old and new images are decoded as different values, so replay applies the wrong bytes or rejects the log.
- detectable: partly — a strict-alignment fault panics, but a wrong endianness can still look like a well-formed log of different contents.
- silent: 1 — the described deployments recover on the same machine that wrote the log.

- contract: The machine that recovers a log uses the same endianness, integer sizes, and structure padding as the machine that wrote it.
- source: logbuf/logrec.h:44 " * more strict alignment than is assumed here (i.e. all data"
- violation: An aggregate written on a big-endian SPARC or RS/6000 is recovered on a little-endian host, so the salvage id, pass number, and record fields are byte-swapped.
- at-risk: G54 and G56 fail closed when the magic number does not match, and G8 fails open if a swapped header happens to look like a plausible page.
- detectable: partly — a swapped salvage id makes GetCleanLogInfo and the page scan reject the log; a few swapped fields can still checksum if the checksum was stored in the same byte order.
- silent: 1 — the paper's running systems are SPARC and RS/6000, both big-endian, and moving an aggregate to the other endianness is rare.

### D22
- contract: Aggregate setup must supply the complete log-block array in its original circular order and associate it with the correct data device.
- source: logbuf/recover.c:983 "/* guarantee the caller described the log properly */"
- violation: Recovery receives a reordered block list, a truncated list, or another aggregate’s data device.
- at-risk: G1, G6, G7, G54: head search or replay addresses the wrong history or metadata.
- detectable: partly — page-number and bounds checks catch many array errors; a plausible wrong aggregate may evade them.
- silent: 1 — The aggregate layer normally reconstructs this mapping consistently.

- contract: The aggregate layer must provide the correct ordered array of physical log block addresses and its exact length.
- source: logbuf/recover.c:989 " /* guarantee the caller described the log properly */"
- violation: A damaged log anode supplies a permuted, truncated or wrong address array.
- at-risk: G54, G55: recovery searches and replays the wrong circular log.
- detectable: partly — page-number and tail bounds checks catch some incorrect descriptions.
- silent: 1 — Wrong log maps normally cause page-number, checksum or bounds failures.

- contract: The caller must pass a log-location array that lists every log-container block in order, with page number i stored at that array entry and with no other file or metadata block in the list.
- source: logbuf/recover.c:983 " /* guarantee the caller described the log properly */"
- violation: The aggregate map is short, permuted, or overlaps a directory or bitmap, so recovery reads file data as the log or fails to read the real tail.
- at-risk: G8 and G47 fail because the head and tail are computed from the wrong blocks, and replay then undoes or redoes the wrong metadata, or asserts when the on-page page number disagrees with the array index.
- detectable: yes — recovery asserts when the head page's page number is not the array index it just selected, and a bad magic raises an I/O error.
- silent: 1 — the aggregate opener builds the array by mapping the log container, and a map that is wrong but still internally consistent is rare.

- contract: The caller of log initialization passes the full ordered list of preallocated log-container blocks, and those blocks are not also used as file or metadata blocks.
- source: anode/aggregate.c:326 " /* All log pages must be pre-allocated. There is a faster way to"
- violation: The array omits a page, repeats one, points at file data, or disagrees with the page numbers stored in the log headers.
- at-risk: G54, G56, and G8 fail because SafeDumpLog asserts that the head's page number matches the caller's index and then replays the wrong blocks.
- detectable: yes — a mismatched page number raises RCVR_ASSERT, and a missing map at init returns EPI_E_BADLOGBLOCKS.
- silent: 1 — newaggr builds this array once, and a corrupt superblock that still names a plausible list is rare and usually fails the assert.

### D19
- contract: Device registration must supply a supported power-of-two block size and an accurate matching logBlkSize.
- source: logbuf/log.c:863 "afsl_MBZ(blkSize & 1023); /* must be power-of-two >= 1K */"
- violation: A registered device advertises 3072-byte blocks or a logBlkSize inconsistent with blkSize.
- at-risk: G17, G30, G54: shifts, reservations, offsets, and transfer sizes no longer describe the same blocks.
- detectable: partly — size assertions reject some invalid sizes, but the quoted bitmask alone does not establish a power of two.
- silent: 1 — Normal device setup uses supported geometry.

- contract: The configured device block size must be a supported power of two between 1 KiB and 64 KiB.
- source: logbuf/logbuf.p.h:416 "#define BUF_MAXBUFSIZE (64 * BUF_MINBLKSIZE) /* largest buffer size */"
- violation: An operator attaches a device using unsupported 3 KiB or 128 KiB logical blocks.
- at-risk: G17, G1: pool indexing and log reservation arithmetic cease to match real blocks.
- detectable: partly — VALID_SIZE and assertions check sizes, but the cited log reservation mask alone does not prove a power of two.
- silent: 1 — Unsupported block sizes are deployment mistakes usually caught by setup checks or assertions.

- contract: The device block size is a power of two, at least 1024 bytes, small enough for the recovery allocator, and it is the unit of every log and metadata address the caller passes in.
- source: logbuf/log.c:863 " afsl_MBZ(blkSize & 1023); /* must be power-of-two >= 1K */"
- violation: The aggregate is opened with a block size other than the one stamped in the superblock, or with a size below 1024 or not a power of two, so log pages and metadata blocks are read at the wrong offsets.
- at-risk: G1 and G54 fail because recovery and logging interpret the wrong bytes as log page headers and apply updates to the wrong disk addresses.
- detectable: yes — initialization asserts on the size, and the aggregate header check rejects a mismatch with the device.
- silent: 1 — newaggr and attach enforce the size, so a running system described by the paper does not silently use a bad block size.

- contract: The aggregate's block size is a power of two of at least 1K, equals the async device block size, and the fragment size is a power of two from 1K up to that block size.
- source: logbuf/log.c:863 " afsl_MBZ(blkSize & 1023); /* must be power-of-two >= 1K */"
- violation: The superblock names a block size the device was not opened with, or a fragment size below 1K or not a power of two.
- at-risk: G4 and G54 fail because log records, page checksums, and byte offsets are computed in the wrong block units and recovery patches the wrong range.
- detectable: yes — AGGREGATE_HDR_OK rejects a mismatched superblock, and the log asserts on a bad block size at reservation time.
- silent: 1 — a mount of a mismatched superblock fails the header check, so the operator sees the refusal.

### D2
- contract: The disk must write each sector atomically and correctly across a crash.
- source: logbuf/recover.c:746 "correctness/atomicity of each sector. So if the log page did"
- violation: A power interruption leaves a sector containing a mixture of its old and new contents.
- at-risk: G54 and G1: recovery may trust a torn header during head search or misidentify the clean restart state.
- detectable: partly — page checksums and structural checks detect some torn sectors; header search and restart records do not provide full protection.
- silent: 1 — Sector failure without an I/O error is rare on the paper’s intended disks.

- contract: The storage device must make each log sector write atomic across a crash.
- source: logbuf/recover.c:752 " * correctness/atomicity of each sector. So if the log page did"
- violation: Power loss leaves a sector containing a mixture of old and new header bytes.
- at-risk: G54, G1: head discovery can select the wrong log extent before checksum validation.
- detectable: partly — checksums may detect damage, but binary search deliberately trusts sector headers.
- silent: 1 — Sector tearing is exceptional on the historical disks, and often yields a visible checksum or device error.

- contract: Each hardware sector write is atomic, and the log page header together with its checksum occupies that first sector.
- source: logbuf/recover.c:746 " * correctness/atomicity of each sector. So if the log page did"
- violation: A disk tears one sector so that the first sector of a log page mixes old and new bytes, and the mixture still carries a plausible pass number or checksum.
- at-risk: G54 and G8 fail because recovery's binary search trusts the first sector to be entirely old or entirely new, and a spliced header can select the wrong head or accept a torn page.
- detectable: partly — a torn sector usually fails the page checksum, but a splice that preserves the checksum is accepted.
- silent: 1 — the 512-byte sectors on the disks the paper uses almost always write atomically, so a checksum-preserving tear is rare.

- contract: A device sector is written entirely or left entirely unchanged, including the first sector of a log page and every sector of a metadata block.
- source: logbuf/recover.c:746 " * correctness/atomicity of each sector. So if the log page did"
- violation: A crash tears a 512-byte sector so the log-page header mixes a new checksum with an old pass number, or a metadata sector mixes bytes from two versions of the same block.
- at-risk: G54 fails for a torn log header, and G6 and G7 fail for a torn metadata sector whose unlogged bytes recovery will not rewrite.
- detectable: partly — a torn log page usually fails the checksum once the header sector is whole; a torn metadata sector is not checksummed.
- silent: 1 — the single SCSI disks in the paper's setups write 512-byte sectors atomically, and a torn sector is a rare firmware fault.

### D3
- contract: The storage stack must preserve completed writes until an explicitly authorized overwrite.
- source: logbuf/recover.c:755 "active log pages outside the in-transit window are really"
- violation: A completed active log page later develops an unreadable sector or silently loses bits.
- at-risk: G1, G6, G7, G20: the only surviving undo or redo image may be lost.
- detectable: partly — supported checksums detect many corruptions, but cannot reconstruct lost records.
- silent: 1 — Latent media damage without a reported error is rare but possible.

- contract: The disk subsystem must keep completed active log pages readable and intact until reuse.
- source: logbuf/recover.c:761 " * active log pages outside the in-transit window are really"
- violation: A latent media error corrupts an older active log page.
- at-risk: G7, G8: required undo or redo records are lost and recovery must give up.
- detectable: partly — checksum or read error detects many failures, but checksum collisions can pass.
- silent: 1 — Latent media damage is possible, but required log pages are checked and usually produce a visible recovery error.

- contract: A log page that was written successfully and is outside the in-transit window remains byte-for-byte intact until the log package overwrites it.
- source: logbuf/recover.c:756 " * expected to be on disk correctly. If checksum errors are"
- violation: Media corruption, a dropped write that was acknowledged, or a stale read changes a committed log page after the in-transit window has moved past it.
- at-risk: G6, G7, and G20 fail because recovery gives up on a checksum error, or, if the checksum accidentally matches, replays the wrong records and applies them to metadata.
- detectable: partly — a checksum mismatch raises an I/O failure and asks for the salvager, but a corruption that preserves the checksum is invisible.
- silent: 1 — silent, checksum-preserving corruption of a recently written log page is rare on these disks over a year.

- contract: Until Episode overwrites a block, the device returns the bytes of the last completed write to that block, or it returns an I/O error.
- source: logbuf/recover.c:756 " * expected to be on disk correctly. If checksum errors are"
- violation: A later media error, a misdirected write, or a dropped sector changes a log page or a metadata block that recovery still needs, and the read succeeds with different bytes.
- at-risk: G6, G7, and G1 fail; a corrupted log page outside the in-transit window aborts recovery, and a corrupted metadata home block is applied as if it were the image the log expected.
- detectable: partly — log pages are checksummed and a bad page raises RCVR_IOERR; metadata home blocks have no checksum, so a wrong image is accepted.
- silent: 1 — silent bit rot or a misdirected write over a year on these SCSI disks is rare, and a checksum failure is visible when it hits a log page.

### D29
- contract: Mount and recovery orchestration must run user-space recovery for a dirty log before allowing ordinary filesystem access.
- source: logbuf/recover.c:2374 "return RCVR_MUSTRCVR; /* no kernel recovery anymore */"
- violation: A mount path ignores RCVR_MUSTRCVR and serves a dirty aggregate.
- at-risk: G1, G8, G57, G58: uncommitted updates remain and committed updates may be absent.
- detectable: yes — dirty-log inspection and the explicit return code identify the need for recovery.
- silent: 1 — Bypassing a visible mount error is unusual.

- contract: The operator or aggregate layer must arrange user-space recovery when a dirty log is rejected by the kernel.
- source: logbuf/recover.c:2402 " return RCVR_MUSTRCVR; /* no kernel recovery anymore */"
- violation: An operator treats RCVR_MUSTRCVR as a clean mount or never runs the recovery utility.
- at-risk: G1, G57, G58: the kernel deliberately does not repair the dirty aggregate.
- detectable: yes — the explicit return code identifies the need for recovery.
- silent: 1 — Ignoring a required-recovery return normally prevents service or produces a visible mount error.

- contract: After a crash the operator or the mount path must run user-space recovery to completion before the kernel attaches the aggregate, and must not expect the kernel to recover.
- source: logbuf/recover.c:2374 " return RCVR_MUSTRCVR; /* no kernel recovery anymore */"
- violation: A mount tool attaches a dirty aggregate in the kernel, ignores RCVR_MUSTRCVR or the recovered status, and serves the file system on the unreplayed disk.
- at-risk: G57, G58, and G1 fail because the kernel refuses to replay and, if the caller mounts anyway, metadata from the crash is left inconsistent.
- detectable: yes — log initialization calls recovery and returns a distinct code instead of success when the restart block is not clean.
- silent: 1 — the salvager and epimount in this tree run user-space recovery, and the kernel path returns an error rather than succeeding quietly.

- contract: Before the kernel uses a dirty aggregate, the operator runs user-space recovery to a clean restart and does not mount the aggregate in between.
- source: logbuf/recover.c:2374 " return RCVR_MUSTRCVR; /* no kernel recovery anymore */"
- violation: The operator mounts a crashed aggregate without epilog or salvage, or mounts it while a user-space recovery is still writing the restart block.
- at-risk: G57, G58, and G8 fail because the kernel refuses to replay and, if the caller ignored the error and wrote anyway, new log records would be appended to an unrepaired log.
- detectable: yes — log initialization calls recovery, the kernel returns RCVR_MUSTRCVR, and epig_InitAggregate returns that failure.
- silent: 1 — a mount of a dirty log fails visibly on the kernel path the source actually ships.

### D23
- contract: The allocator and administrator must reserve log blocks exclusively and keep their addresses and log length fixed during normal logging.
- source: §"Data Architecture" "The log container does not grow or shrink"
- violation: A live resize, relocation, or overlapping allocation lets file data overwrite active log pages.
- at-risk: G20, G21, G54: retained history and circular page numbering cease to describe persistent storage.
- detectable: partly — checksum and page-number failures may reveal damage, after recovery information is already lost.
- silent: 1 — The source’s normal initialization and allocation rules avoid live log resizing.

- contract: The allocator must reserve distinct log blocks that do not overlap home metadata or user data.
- source: logbuf/recover.c:1044 " readData(ldP, logLocnArray[current], logBlocks[index]);"
- violation: The log address array repeats a block or includes a block also allocated to a file.
- at-risk: G5, G7: ordinary writes can overwrite recovery records or logging can destroy home data.
- detectable: partly — page-number checks may reveal overlap after damage.
- silent: 1 — Allocation overlap is a rare allocator or provisioning fault and often produces visible corruption.

- contract: The caller must pass a log-location array that lists every log-container block in order, with page number i stored at that array entry and with no other file or metadata block in the list.
- source: logbuf/recover.c:983 " /* guarantee the caller described the log properly */"
- violation: The aggregate map is short, permuted, or overlaps a directory or bitmap, so recovery reads file data as the log or fails to read the real tail.
- at-risk: G8 and G47 fail because the head and tail are computed from the wrong blocks, and replay then undoes or redoes the wrong metadata, or asserts when the on-page page number disagrees with the array index.
- detectable: yes — recovery asserts when the head page's page number is not the array index it just selected, and a bad magic raises an I/O error.
- silent: 1 — the aggregate opener builds the array by mapping the log container, and a map that is wrong but still internally consistent is rare.

- contract: Every block of the log container must already be allocated and mapped before logging starts.
- source: anode/aggregate.c:326 " /* All log pages must be pre-allocated. There is a faster way to"
- violation: A log page address is a hole or an unallocated block, so a log write fails or lands on a block that a file is also using.
- at-risk: G17 and G5 fail because the circular log is no longer a fixed stable buffer, and a write of the log can destroy metadata or never become durable.
- detectable: yes — mapping the container returns an error, which initialization turns into a bad-log-blocks failure.
- silent: 1 — creation allocates the container up front, and a hole in a log that is already in service is rare.

- contract: The caller of log initialization passes the full ordered list of preallocated log-container blocks, and those blocks are not also used as file or metadata blocks.
- source: anode/aggregate.c:326 " /* All log pages must be pre-allocated. There is a faster way to"
- violation: The array omits a page, repeats one, points at file data, or disagrees with the page numbers stored in the log headers.
- at-risk: G54, G56, and G8 fail because SafeDumpLog asserts that the head's page number matches the caller's index and then replays the wrong blocks.
- detectable: yes — a mismatched page number raises RCVR_ASSERT, and a missing map at init returns EPI_E_BADLOGBLOCKS.
- silent: 1 — newaggr builds this array once, and a corrupt superblock that still names a plausible list is rare and usually fails the assert.

### D103
- contract: setjmp and longjmp, and the kernel exception longjmp where it is still compiled in, restore the recovery catch point and abandon the failed pass.
- source: logbuf/recover.c:125 " * This assumes traditional semantics for an in-kernel setjmp/longjmp."
- violation: The C library or the kernel exception handler returns into a half-updated recovery structure, or it fails to jump, and recovery continues after RCVR_RAISE.
- at-risk: G8 and G50 fail because a detected bad page is then applied, or cleanup is skipped and a later pass uses freed record memory.
- detectable: no — a broken jump looks like a crash or a wrong repair, and the log package has no separate check that the jump happened.
- silent: 1 — the user-space C library on the paper's hosts provides ordinary setjmp, and a broken jump would be a porting fault rather than a yearly event.

### D106
- contract: A deployment that relies on crash consistency initializes the aggregate with logging turned on.
- source: anode/aggregate.c:1418 " * logged -- whether to turn on logging. Usually true, only false for some"
- violation: A mount or test harness calls epig_InitAggregate with logged false on an aggregate that users expect to survive a crash.
- at-risk: G1 and G4 fail because metadata updates are not logged, and recovery has nothing to replay.
- detectable: no — the flag is a legal argument, and the file system still serves reads and writes.
- silent: 1 — the kernel mount path passes logged true, and the false setting is described as a debug and test option.

### D104
- contract: The CPU and compiler honor the log's 4-byte alignment rules for on-disk records and in-memory casts.
- source: logbuf/logrec.h:44 " * more strict alignment than is assumed here (i.e. all data"
- violation: A port to a machine that faults on the unaligned references the macros still perform, or a compiler inserts padding the on-disk layout does not have.
- at-risk: G4 and G42 fail because a record is stored or recovered at the wrong offset, so undo and redo patch the wrong bytes.
- detectable: partly — recovery raises RCVR_ALIGN when a pointer fails PTR_ALIGNED; a padded struct that is still 4-byte aligned is accepted.
- silent: 1 — the paper's SPARC and RS/6000 ABIs match the layout the 1992 code was written for.

### D109
- contract: The fast metadata modify path receives kernel addresses, and any user-address modify copies exactly the requested bytes or returns an error.
- source: logbuf/buffer.c:1703 " * assume along this code path that we never have user data (e.g. we"
- violation: A caller passes a user pointer to the fast path, or osi_copyin reports success after copying a different range.
- at-risk: G4 and G42 fail because the logged new value is not the value the caller meant to store, and recovery will redo that wrong value.
- detectable: partly — a user pointer on the fast path can fault; a short copyin that still returns zero is silent.
- silent: 1 — directory and anode updates use kernel buffers, and a bad copyin on these hosts is rare.

### D102
- contract: The kernel's device-block conversion addresses the same physical sectors the driver writes, and an Episode block is an integer number of those sectors.
- source: async/asevent.c:139 "#define ToBufferBlocks(adevice, ablock, aoffset) \"
- violation: DEV_BSIZE, abtodb, or btodb disagrees with the disk's sector size, so log and metadata I/O lands on the wrong addresses.
- at-risk: G1, G5, and G54 fail because the log and the home blocks recovery reads are not the blocks Episode wrote.
- detectable: partly — a wildly wrong address often returns an I/O error and panics a log read; an off-by-a-factor address on a large disk can succeed with unrelated bytes.
- silent: 1 — the SunOS and AIX ports the paper describes use one consistent DEV_BSIZE for the disk they mount.

### D105
- contract: The operator leaves removable media in place until the last aggregate close has returned, and no other agent reads or writes it during that close.
- source: anode/aggregate.c:1716 " * this means that if the disk is on removable media it could be safely"
- violation: The operator ejects the disk, or a raw copy starts, after the unmount call begins and before the restart block write finishes.
- at-risk: G39 and G56 fail because the clean restart never becomes durable, so the next attach either replays a torn close or treats a partial restart as clean.
- detectable: partly — a failed restart write returns RCVR_FAILED from the restart writer; an eject after a false completion is the E2 case.
- silent: 1 — unloading during the close window is rare in ordinary server operation.

### D110
- contract: Block addresses passed into the log and into recovery name blocks the device can read and write.
- source: logbuf/recover.c:1319 " if (returnVal != 0) panic("ReadData: bad read");"
- violation: A caller or a damaged log record names a block past the end of the device or on a hole the driver rejects.
- at-risk: G8 fails because recovery panics on the read and never writes the clean restart, and a metadata write during normal operation hits the same address.
- detectable: yes — readData and writeData panic, and the async path surfaces an I/O error.
- silent: 1 — legal allocators hand out in-range blocks, and an out-of-range address panics rather than succeeding quietly.

### D93
- contract: A crash stops the machine, discards volatile memory, and leaves on disk only the sector writes that had already completed, rather than continuing to store arbitrary bytes.
- source: §"Component Architecture" " The recovery procedure runs after a crash, replaying the committed transactions and undoing the"
- violation: The processor continues after a fault and writes partial or wild data into the log or into metadata blocks, or a crash scrambles memory-mapped I/O that was not an in-flight sector write.
- at-risk: G1, G6, G7, and G8 fail because recovery replays a log and a disk that are no longer the prefix of a fail-stop execution, so undo and redo restore a state the transactions never produced.
- detectable: no — recovery cannot tell a wild store from a legitimate sector write once the page checksum happens to match.
- silent: 1 — the SunOS and AIX machines in the paper fail by panic or power loss, and a crash that keeps storing is rare over a year.

- contract: A crash stops the machine, discards memory, and leaves on disk only updates whose writes had reached the device.
- source: §"Component Architecture" "In the event of a crash, only some of the updates to the le system"
- violation: The machine keeps issuing writes after the failure, or a DMA engine scribbles arbitrary blocks as power fails.
- at-risk: G1 and G8 fail because recovery replays a log that no longer matches the blocks actually left on disk. Unsure how much of a wild post-crash write the checksum on log pages would still catch.
- detectable: partly — a damaged log page fails its checksum or salvage id and recovery stops; a wild write onto a metadata home block has no log checksum.
- silent: 1 — the paper's crash model is a power loss or kernel halt, and a scribbling failure is rare on the Sun and RS/6000 hosts it names.

### D94
- contract: Each hardware sector write is atomic, and the log page header together with its checksum occupies that first sector.
- source: logbuf/recover.c:746 " * correctness/atomicity of each sector. So if the log page did"
- violation: A disk tears one sector so that the first sector of a log page mixes old and new bytes, and the mixture still carries a plausible pass number or checksum.
- at-risk: G54 and G8 fail because recovery's binary search trusts the first sector to be entirely old or entirely new, and a spliced header can select the wrong head or accept a torn page.
- detectable: partly — a torn sector usually fails the page checksum, but a splice that preserves the checksum is accepted.
- silent: 1 — the 512-byte sectors on the disks the paper uses almost always write atomically, so a checksum-preserving tear is rare.

- contract: The device's atomic sector is large enough to hold the whole log-page header and its checksum, which the log places at the start of the page.
- source: logbuf/recover.c:744 " /* The log page header ( including checksum ) is in the first"
- violation: The device sector is smaller than the header plus checksum, so a crash can persist a new checksum while leaving part of the header from an older page.
- at-risk: G54 fails because the binary search trusts the header sector to describe the whole page, and a split header can select the wrong log head.
- detectable: partly — a mismatched checksum on the in-transit window pulls the head back; a header that is internally consistent and checksums against a torn body can be accepted.
- silent: 1 — Episode blocks are at least 1K and the header plus a CRC-32 fit in a 512-byte sector on the machines the paper runs.

### D73
- contract: Backup, restore, and raw-device administration must preserve a crash-consistent pairing of the aggregate’s metadata and its retained log history.
- source: logbuf/log.c:734 "code = elbr_Recover(ldP, dP, logLocnArray, logLocnArraySize);"
- violation: An operator restores only the log from an older backup, or independently snapshots log and data devices at incompatible times.
- at-risk: G1, G6, G7, G20, G21: replay history can be absent or belong to a different version of the metadata.
- detectable: partly — structural checks detect some mismatches, but no cross-device snapshot identity is established here.
- silent: 1 — Normal same-aggregate operation avoids independently restored log/data versions.

- contract: The initialization utilities must record the log container that recovery will open, and if that container is placed on another device both devices must be recovered together and both must be stable.
- source: §"Data Architecture" "be on the same aggregate as the data that it is logging, but this restriction is currently imposed by our"
- violation: The utilities point the aggregate at a log device that is missing at recovery, or at a log on volatile media while the data disk kept its completed writes.
- at-risk: G7 and G1 fail because redo information is on a device recovery does not read, or that device lost the committed tail while metadata writes remained.
- detectable: yes — a missing or short log container fails the map or the minimum-size check at attach.
- silent: 1 — the utilities in this tree put the log on the same aggregate, so a split log that is not recovered with the data is rare in the described setup.

- contract: The log device and the data device experience the same crashes and the same durability, so a completed write on one is still present when recovery runs on the other.
- source: §"Data Architecture" "be on the same aggregate as the data that it is logging, but this restriction is currently imposed by our"
- violation: The log sits on a disk that loses power or fails independently of the data disk, or the operator recovers only one of the two devices.
- at-risk: G7 and G21 fail when the log disk loses committed records whose metadata never reached the data disk, and G6 fails when the data disk is restored from a copy that is newer than the log.
- detectable: no — InitLog accepts two device pointers, and nothing checks that they failed together.
- silent: 1 — the initialization utilities put the log on the same aggregate, so a split deployment is rare in a system run as the paper describes.

### D101
- contract: Code that runs during a kernel panic must not depend on starting further transactions once log-full handling has stopped retrying.
- source: logbuf/buffer.c:1762 " if (osi_IsKernelPanic() && ++nLoops == ELBB_MAX_PANIC_LOOP)"
- violation: Panic or crash-dump code keeps modifying metadata after elbb_StartTran returns failure, and a dirty buffer is then written without a new log record.
- at-risk: G5 and G7 fail because that buffer can reach disk with updates that are not in the log, so the next recovery cannot redo or undo them.
- detectable: partly — the start call returns an out-of-memory code, but a caller that ignores it and writes anyway gets no further check.
- silent: 1 — kernel panics are rare over a year, and the panic path usually stops issuing new metadata transactions after a few attempts.

### D100
- contract: Callers of the quick logged modify and of buffer fill must pass metadata that already resides in the kernel address space, never a user pointer and never file-body data.
- source: logbuf/buffer.c:1703 " * assume along this code path that we never have user data (e.g. we"
- violation: A caller points the fast modify path at a user address or at file contents, so the log record copies the wrong bytes or faults, and user data is written into the log.
- at-risk: G4 fails because the old and new images in the log are not the metadata update, and replay writes those wrong bytes back to a metadata block.
- detectable: partly — a bad user address can fault, but a readable wrong address is logged as success.
- silent: 1 — the fast-modify path is unused and the fill path is given kernel patterns, so this mis-call is rare.

### D98
- contract: The user-space recovery process must provide setjmp and longjmp with ordinary C semantics, so the code passed to longjmp is the code setjmp returns.
- source: logbuf/recover.c:125 " * This assumes traditional semantics for an in-kernel setjmp/longjmp."
- violation: The C library or a kernel-style jump buffer returns 1, or returns 0, for every longjmp, and recovery reports failure for success or success for a checksum error.
- at-risk: G55 fails because a failed replay can still write a restart record, or a successful replay can be reported as failure and then be followed by another writer.
- detectable: partly — a crash of the process is visible, but a wrong return code looks like an ordinary recovery status.
- silent: 1 — user-space libc on the described hosts implements setjmp in the usual way.

### D99
- contract: After a crash the primary superblock must still be a valid aggregate header naming this log, because attach and the salvager do not fall back to an alternate superblock.
- source: anode/aggregate.c:1138 " * primary superblock, and since the salvager doesn't presently"
- violation: The only primary superblock is torn or unreadable, or its block size or log length no longer matches the device, and the alternate copies are ignored.
- at-risk: G58 fails because the log is never opened, so replay cannot run, and a superblock that points at the wrong log length or the wrong container makes replay use the wrong blocks.
- detectable: yes — a bad primary header fails aggregate open with a not-an-aggregate error.
- silent: 1 — the superblock is a single checked block written at format and grow, and losing it with no error at the disk is rare.

### D71
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

### D72
- contract: The storage and operating environment must preserve a clean restart marker’s authenticity and its ordering after all recovery or shutdown data writes.
- source: logbuf/recover.c:2738 "We choose not to checksum the log page containing a restart record"
- violation: A forged, corrupted, restored, or prematurely durable restart marker survives while recovered metadata writes do not.
- at-risk: G39, G55, G56: a plausible restart record can suppress necessary recovery because it is not checksummed.
- detectable: partly — header and record checks catch malformed markers, but not a plausible stale or wrongly ordered clean marker.
- silent: 1 — Normal synchronous durable I/O preserves this order; silent violation is rare.

- contract: The user-space process that recovers or creates an aggregate must open the device so that a completed write is durable before completion returns, and the kernel must not mount until that process has finished.
- source: salvage/salvage_main.c:255 " ? US_OFLAGS_SYNC : US_OFLAGS_RDONLY));"
- violation: Recovery runs through us_open without US_OFLAGS_SYNC, the process exits or the machine crashes with the restart record in the host page cache and the recovered metadata blocks not yet on media, and the kernel then mounts.
- at-risk: G55 and G1 fail because the log can look clean, or the restart can be durable, while the metadata writes recovery performed are not.
- detectable: no — write completion returns success from the host cache, and the loss is visible only after a later crash.
- silent: 1 — the salvager opens with the synchronous flag whenever it recovers, so a deployment run as the source describes rarely omits it.

### D74
- contract: Initialization callers must supply writable buffer-pool memory of the declared size and keep it owned by logbuf for the package lifetime.
- source: logbuf/buffer.c:731 "caddr_t startAddr = elbbParams->bufferPool;"
- violation: The caller frees or repurposes the pool after Init, or exaggerates byteCount beyond its allocation.
- at-risk: G4, G5, G42: log and cached bytes can be corrupted in memory before being written.
- detectable: partly — allocation and lifetime instrumentation can detect invalid ownership; ordinary I/O cannot establish it.
- silent: 1 — Normal kernel initialization retains the supplied pool.

### D27
- contract: Log-creation callers must exclude all other activity on that device while creating its log.
- source: logbuf/log.c:878 "Locking: This code presumes no other thread is calling for this"
- violation: A formatting utility creates the log while the filesystem still has active users.
- at-risk: G1, G63: zeroing the log can destroy active undo and redo history.
- detectable: partly — aggregate mount exclusion can detect use, but log creation cannot see every external writer.
- silent: 1 — Normal tools format offline.

### D21
- contract: The device layer must preserve a stable unique device identity and physical block mapping for the lifetime of cached buffers and transactions.
- source: logbuf/buffer.c:845 "sizeof(async_device_t *) +"
- violation: A device object is recycled for a different partition while old cache entries still use its pointer.
- at-risk: G1, G40, G42: cached data and log records can be applied to the wrong storage.
- detectable: partly — identity and lifetime instrumentation could detect reuse, but ordinary block I/O cannot establish it.
- silent: 1 — Normal aggregate open and close protocols avoid silent identity reuse.

### D78
- contract: Aggregate configuration must keep log length and page indices within the range supported by the on-disk fields and signed-distance arithmetic.
- source: logbuf/log.c:187 "As with pass numbers, log offsets are unsigned int16s. So we have to do"
- violation: A tool allocates a log whose page index truncates in oldestDataPage or whose distance changes sign in int16 arithmetic.
- at-risk: G17, G20, G21, G54: tail retention and recovery head/tail interpretation may select incorrect history.
- detectable: partly — initialization can validate representability; the precise safe bound requires further analysis of all comparisons.
- silent: 1 — The paper’s example log sizes are small relative to these field ranges.

### D17
- contract: A port must ensure that pointer alignment calculations do not truncate addresses and that cast log records meet CPU alignment requirements.
- source: logbuf/logrec.h:232 "a power-of-two. The use of (unsigned) may not be strictly correct"
- violation: The code is built with 64-bit pointers and 32-bit unsigned, and ALIGN discards the upper address bits.
- at-risk: G1 and log service availability: memory accesses can fault or target unrelated storage.
- detectable: partly — faults or address checks detect many cases, but aliasing can corrupt memory silently.
- silent: 1 — The paper’s 32-bit machines meet this condition; an unadapted later port may not.

### D5
- contract: The storage stack must return the requested bytes and report failed or short I/O as an error.
- source: async/asevent.c:1126 "if (bp->b_flags & B_ERROR) {"
- violation: A driver returns success with a short transfer, wrong-sector read, or failed write while leaving B_ERROR clear.
- at-risk: G1, G31, G35, G40: success is interpreted as a complete transfer, so stale bytes or missing updates can survive recovery.
- detectable: partly — log checksums can catch bad reads; ordinary data blocks have no equivalent protection here.
- silent: 1 — Silent driver transfer errors are unusual on supported systems.

### D77
- contract: Clients retaining historical transaction IDs must retire them before ID wrap can make the same numeric ID identify unrelated work.
- source: logbuf/tran.c:1062 "elbt_GlobalTranId++;"
- violation: An old vnode or transactional lock retains a numeric ID across a complete 32-bit allocation cycle and later forces or merges an unrelated transaction.
- at-risk: G13, G23, G24: ID reuse can make a stale dependency or persistence check refer to the wrong work; the actual supported lifetime bound is uncertain.
- detectable: partly — generation-aware tracking could detect reuse, but a bare numeric ID is ambiguous.
- silent: 1 — Retaining an actionable ID across billions of transaction allocations is rare for the described workloads.

### D39
- contract: Clients must pass live transaction IDs belonging to the intended device and stop adding updates after ending them.
- source: logbuf/log.c:1020 "afsl_Assert (dataLength <= tP->dev->blkSize);"
- violation: A client reuses a stale transaction handle, logs after EndTran, or modifies one device under another device’s transaction.
- at-risk: G2, G7, G42: updates can lack a valid lifetime or replay on the wrong aggregate.
- detectable: partly — lookup and status assertions catch some cases, but a recycled ID or plausible wrong device can evade them.
- silent: 1 — Correct API clients normally retain IDs only for the operation lifetime.

### D28
- contract: Log-creation callers must enter without holding buffer-package locks that creation needs.
- source: logbuf/log.c:880 "I/O, it presumes locks are not held in the buffer package."
- violation: A caller creates a log while retaining the buffer lock needed by CreateBlock.
- at-risk: G63 and initialization availability: recursive lock acquisition can deadlock creation.
- detectable: partly — lock ownership tracking can expose the cycle.
- silent: 1 — Normal initialization follows the documented lock convention.

### D65
- contract: The VM and vnode layers must ensure the strategy layer’s documented bound on simultaneous waiters for each in-transit block.
- source: anode/strategy.c:271 "multiple I/O requests for a given block, and other writers are"
- violation: Two VM or volume-operation threads wait for the same block where the code expects at most one waiter.
- at-risk: G16 and buffer/I/O availability: premature in-transit record reuse can invalidate synchronization.
- detectable: partly — waiter-count assertions catch documented cases, but all release races require careful tracking.
- silent: 1 — The source’s waiter checks usually make a violation visible.

### D88
- contract: Administrative tuning must preserve valid transaction, equivalence-class and log-capacity limits for attached devices.
- source: logbuf/log.c:2668 " /* XXX: go back and recompute for all active log maps. */"
- violation: An operator changes a global maximum and assumes existing log maps have been resized or re-reserved.
- at-risk: G17: configured limits and per-map reservations can diverge; the exact impact depends on the parameter.
- detectable: partly — value checks catch some invalid settings, but existing-map consistency is not fully recomputed.
- silent: 1 — Unsafe live tuning is unusual in ordinary operation and may visibly exhaust resources.

### D89
- contract: The OS time service must provide usable elapsed-time progression for the buffer-cache aging heuristics.
- source: logbuf/buffer.c:2857 " * reused. Thus the average age of reuse must be much smaller than the"
- violation: A broken clock freezes age calculations or jumps enough to distort cache-cost comparisons.
- at-risk: G9, G11: maintenance and cache behavior may lose the stated recovery/performance characteristics; correctness dependence is uncertain.
- detectable: partly — clock anomalies can be detected against an independent clock.
- silent: 1 — Clock failures are unusual, and cache heuristics tolerate ordinary timing variation.

