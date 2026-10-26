# Environment contracts for Episode log and recovery

Obligations on things outside `logbuf` (the disk and its driver, the async I/O veneer, the host, the operator, and the anode, vnode, directory, and VM callers). Rules `logbuf` itself implements are not listed here.

### E1
- contract: A crash stops the machine, discards volatile memory, and leaves on disk only the sector writes that had already completed, rather than continuing to store arbitrary bytes.
- source: §"Component Architecture" "       The recovery procedure runs after a crash, replaying the committed transactions and undoing the"
- stated: implicit
- violation: The processor continues after a fault and writes partial or wild data into the log or into metadata blocks, or a crash scrambles memory-mapped I/O that was not an in-flight sector write.
- at-risk: G1, G6, G7, and G8 fail because recovery replays a log and a disk that are no longer the prefix of a fail-stop execution, so undo and redo restore a state the transactions never produced.
- detectable: no — recovery cannot tell a wild store from a legitimate sector write once the page checksum happens to match.
- silent: 1 — the SunOS and AIX machines in the paper fail by panic or power loss, and a crash that keeps storing is rare over a year.
- basis: text

### E2
- contract: When the async layer or the device driver reports that a write has completed, every sector of that write is on stable storage and will still be there after a crash or power loss.
- source: logbuf/recover.c:894 "     * underlying system to really guarantee that a page is on disk"
- stated: stated
- violation: A SCSI disk or the driver acknowledges the write when the bytes reach a volatile write-back cache, and a power loss then drops a log page the log package has already treated as committed, or drops it while a later metadata write remains.
- at-risk: G5, G7, G29, and G30 fail because write-ahead logging waits only for completion, so a dirty metadata buffer can be written, or a transaction can be called committed, while its log records are not actually durable.
- detectable: no — completion is success, and the loss appears only after the next crash.
- silent: 3 — write-back caches were a normal silent setting on the SCSI disks of this period, and Episode never issues a cache flush after a log force.
- basis: general systems experience

### E3
- contract: Each hardware sector write is atomic, and the log page header together with its checksum occupies that first sector.
- source: logbuf/recover.c:746 "     * correctness/atomicity of each sector.  So if the log page did"
- stated: stated
- violation: A disk tears one sector so that the first sector of a log page mixes old and new bytes, and the mixture still carries a plausible pass number or checksum.
- at-risk: G54 and G8 fail because recovery's binary search trusts the first sector to be entirely old or entirely new, and a spliced header can select the wrong head or accept a torn page.
- detectable: partly — a torn sector usually fails the page checksum, but a splice that preserves the checksum is accepted.
- silent: 1 — the 512-byte sectors on the disks the paper uses almost always write atomically, so a checksum-preserving tear is rare.
- basis: source

### E4
- contract: A log page that was written successfully and is outside the in-transit window remains byte-for-byte intact until the log package overwrites it.
- source: logbuf/recover.c:756 "     * expected to be on disk correctly. If checksum errors are"
- stated: stated
- violation: Media corruption, a dropped write that was acknowledged, or a stale read changes a committed log page after the in-transit window has moved past it.
- at-risk: G6, G7, and G20 fail because recovery gives up on a checksum error, or, if the checksum accidentally matches, replays the wrong records and applies them to metadata.
- detectable: partly — a checksum mismatch raises an I/O failure and asks for the salvager, but a corruption that preserves the checksum is invisible.
- silent: 1 — silent, checksum-preserving corruption of a recently written log page is rare on these disks over a year.
- basis: source

### E5
- contract: The restart page, which recovery does not checksum, must keep the exact header and restart record written by log creation, clean shutdown, or a finished recovery.
- source: logbuf/recover.c:2738 "       * We choose not to checksum the log page containing a restart record"
- stated: stated
- violation: Bit rot or a torn write leaves the salvage magic and a restart record type in the first log block of a log that still has an active tail, or destroys a genuine restart record.
- at-risk: G56 and G58 fail because a dirty log is treated as clean and ordinary operation starts without replay, or a clean log is treated as dirty and recovery rewrites metadata from an old tail.
- detectable: no — the clean test looks only for the magic and a restart record, not a checksum.
- silent: 1 — one block is rewritten at shutdown and recovery, and an undetected flip of that pattern is rare.
- basis: source

### E6
- contract: The device and the async veneer must report a failed or unreadable log or metadata transfer as an error, and must not return success for a page that was not stored or not read.
- source: logbuf/recover.c:788 "	     * log page is damaged; run salvager."
- stated: stated
- violation: The driver returns a zero completion for a write it dropped, or returns old or zeroed data for a read that the media could not perform.
- at-risk: G5 and G7 fail because the log package panics only when it sees an error, and a false success lets it treat a missing log page as durable or replay garbage as metadata.
- detectable: partly — a reported error panics the log or raises recovery failure, but a false success is invisible.
- silent: 2 — drivers usually surface hard errors, but a dropped write reported as success shows up often enough on bad cables and failing disks to be more than rare.
- basis: source

### E7
- contract: On AIX, an I/O completion reported as ESOFT must mean the transfer finished and is durable, because the async layer clears that error and treats the buffer as successful.
- source: async/asevent.c:1070 "    if (bp->b_error == ESOFT) {"
- stated: implicit
- violation: The AIX driver returns ESOFT for a write that was not stored, and Episode clears the error and continues as if the log page or metadata block were on disk.
- at-risk: G5 and G29 fail for the same reason as a false success: the log force returns, and a later crash finds the page missing.
- detectable: no — the error is deliberately discarded before the log package sees it.
- silent: 2 — recovered soft errors are normal on AIX and are harmless, but an ESOFT that does not mean the data was stored happens on real adapters often enough to be occasional.
- basis: source

### E8
- contract: A later read of a block must return, sector by sector, the data of the last write to that sector that the driver has reported complete.
- source: logbuf/recover.c:892 "     * We trust the log to make sure it doesn't assume a page with"
- stated: implicit
- violation: A drive cache, a multipath disk, or a host buffer returns a stale copy after a completed write, so recovery or the next mount sees an older log page.
- at-risk: G54 and G7 fail because the head, the pass number, or the redo records recovery reads are not the ones the running system forced.
- detectable: partly — a stale page often fails the pass-number or checksum test, and an older but well-formed page can be mistaken for the head.
- silent: 2 — coherent SCSI disks usually read what they just wrote, but stale cache and multipath windows are an occasional field failure.
- basis: general systems experience

### E9
- contract: The device block size is a power of two, at least 1024 bytes, small enough for the recovery allocator, and it is the unit of every log and metadata address the caller passes in.
- source: logbuf/log.c:863 "      afsl_MBZ(blkSize & 1023); /* must be power-of-two >= 1K */"
- stated: stated
- violation: The aggregate is opened with a block size other than the one stamped in the superblock, or with a size below 1024 or not a power of two, so log pages and metadata blocks are read at the wrong offsets.
- at-risk: G1 and G54 fail because recovery and logging interpret the wrong bytes as log page headers and apply updates to the wrong disk addresses.
- detectable: yes — initialization asserts on the size, and the aggregate header check rejects a mismatch with the device.
- silent: 1 — newaggr and attach enforce the size, so a running system described by the paper does not silently use a bad block size.
- basis: source

### E10
- contract: The user-space process that recovers or creates an aggregate must open the device so that a completed write is durable before completion returns, and the kernel must not mount until that process has finished.
- source: salvage/salvage_main.c:255 "				 ? US_OFLAGS_SYNC : US_OFLAGS_RDONLY));"
- stated: stated
- violation: Recovery runs through us_open without US_OFLAGS_SYNC, the process exits or the machine crashes with the restart record in the host page cache and the recovered metadata blocks not yet on media, and the kernel then mounts.
- at-risk: G55 and G1 fail because the log can look clean, or the restart can be durable, while the metadata writes recovery performed are not.
- detectable: no — write completion returns success from the host cache, and the loss is visible only after a later crash.
- silent: 1 — the salvager opens with the synchronous flag whenever it recovers, so a deployment run as the source describes rarely omits it.
- basis: source

### E11
- contract: The caller must pass a log-location array that lists every log-container block in order, with page number i stored at that array entry and with no other file or metadata block in the list.
- source: logbuf/recover.c:983 "    /* guarantee the caller described the log properly */"
- stated: stated
- violation: The aggregate map is short, permuted, or overlaps a directory or bitmap, so recovery reads file data as the log or fails to read the real tail.
- at-risk: G8 and G47 fail because the head and tail are computed from the wrong blocks, and replay then undoes or redoes the wrong metadata, or asserts when the on-page page number disagrees with the array index.
- detectable: yes — recovery asserts when the head page's page number is not the array index it just selected, and a bad magic raises an I/O error.
- silent: 1 — the aggregate opener builds the array by mapping the log container, and a map that is wrong but still internally consistent is rare.
- basis: source

### E12
- contract: Every block of the log container must already be allocated and mapped before logging starts.
- source: anode/aggregate.c:326 "	    /* All log pages must be pre-allocated.  There is a faster way to"
- stated: stated
- violation: A log page address is a hole or an unallocated block, so a log write fails or lands on a block that a file is also using.
- at-risk: G17 and G5 fail because the circular log is no longer a fixed stable buffer, and a write of the log can destroy metadata or never become durable.
- detectable: yes — mapping the container returns an error, which initialization turns into a bad-log-blocks failure.
- silent: 1 — creation allocates the container up front, and a hole in a log that is already in service is rare.
- basis: source

### E13
- contract: The log container must not grow or shrink while the aggregate is in use.
- source: §"Data Architecture" "do not, in the current implementation, change dynamically. The log container does not grow or shrink"
- stated: stated
- violation: An operator or a later tool extends or truncates the log container while transactions are running, so the in-memory location array and the pass numbers no longer describe the disk.
- at-risk: G17 and G9 fail because admission control and recovery both assume a fixed circular buffer, and a resized log can wrap onto live records or drop the tail.
- detectable: partly — a size mismatch at the next attach is rejected, but a resize under a live kernel is not checked on each write.
- silent: 1 — the implementation provides no working resize of the log, so a deployment run as described does not change it.
- basis: text

### E14
- contract: The log must be at least large enough for one maximum transaction plus the reserve of buffers that are allowed to be in transit, for the block size and the concurrency the file system will start.
- source: logbuf/log.c:1694 "	   * is large enough for at least one transaction, we also proceed if"
- stated: stated
- violation: newaggr or the operator creates a log smaller than elbl_MinLogSize, or small enough that the transactions the vnode layer actually starts cannot all reserve space.
- at-risk: G17 fails because the admission check assumes that a single transaction always fits, and a smaller log either refuses to attach or cannot start the transactions the file system needs without overrunning the circular buffer.
- detectable: yes — log initialization returns a log-full error when the array is shorter than the minimum.
- silent: 1 — an undersized log fails attach with an error, so it is not a silent violation on a system that comes up.
- basis: source

### E15
- contract: The initialization utilities must record the log container that recovery will open, and if that container is placed on another device both devices must be recovered together and both must be stable.
- source: §"Data Architecture" "be on the same aggregate as the data that it is logging, but this restriction is currently imposed by our"
- stated: stated
- violation: The utilities point the aggregate at a log device that is missing at recovery, or at a log on volatile media while the data disk kept its completed writes.
- at-risk: G7 and G1 fail because redo information is on a device recovery does not read, or that device lost the committed tail while metadata writes remained.
- detectable: yes — a missing or short log container fails the map or the minimum-size check at attach.
- silent: 1 — the utilities in this tree put the log on the same aggregate, so a split log that is not recovered with the data is rare in the described setup.
- basis: text

### E16
- contract: Operators and tools must not write a restart record, or otherwise mark the log clean, except by log creation, a clean shutdown, or a recovery that has finished applying updates.
- source: logbuf/recover.c:2738 "       * We choose not to checksum the log page containing a restart record"
- stated: implicit
- violation: patchlog or an operator copies a restart record onto the first log block of a dirty aggregate to make it mount, without replaying the tail.
- at-risk: G56 and G1 fail because attach treats the log as clean and serves metadata that still contains uncommitted updates and is missing committed ones.
- detectable: no — a well-formed restart record is the definition of a clean log.
- silent: 1 — normal operation does not rewrite the restart block by hand, and doing so is a rare administrative act.
- basis: source

### E17
- contract: After a crash the operator or the mount path must run user-space recovery to completion before the kernel attaches the aggregate, and must not expect the kernel to recover.
- source: logbuf/recover.c:2374 "      return RCVR_MUSTRCVR; /* no kernel recovery anymore */"
- stated: stated
- violation: A mount tool attaches a dirty aggregate in the kernel, ignores RCVR_MUSTRCVR or the recovered status, and serves the file system on the unreplayed disk.
- at-risk: G57, G58, and G1 fail because the kernel refuses to replay and, if the caller mounts anyway, metadata from the crash is left inconsistent.
- detectable: yes — log initialization calls recovery and returns a distinct code instead of success when the restart block is not clean.
- silent: 1 — the salvager and epimount in this tree run user-space recovery, and the kernel path returns an error rather than succeeding quietly.
- basis: source

### E18
- contract: User-space recovery of one aggregate must run on a single thread, and the caller must be prepared for the recovery routines to return by longjmp.
- source: logbuf/recover.c:358 " * This code must run single-threaded in user space;  it runs multi-threaded"
- stated: stated
- violation: Two threads in the salvager call elbr_Recover at once, or a caller invokes the dump routine without a setjmp frame, so a checksum failure longjmps off the stack.
- at-risk: G8 and G55 fail because the two recoveries interleave writes of the same metadata and restart block, or the process dies and leaves a half-applied recovery.
- detectable: partly — a longjmp with no frame aborts the process, which the operator sees, but two interleaved recoveries can finish with success and a wrong disk.
- silent: 1 — the salvager runs recovery on one thread, so a concurrent second recovery in the described operation is rare.
- basis: source

### E19
- contract: The user-space recovery process must provide setjmp and longjmp with ordinary C semantics, so the code passed to longjmp is the code setjmp returns.
- source: logbuf/recover.c:125 " * This assumes traditional semantics for an in-kernel setjmp/longjmp."
- stated: stated
- violation: The C library or a kernel-style jump buffer returns 1, or returns 0, for every longjmp, and recovery reports failure for success or success for a checksum error.
- at-risk: G55 fails because a failed replay can still write a restart record, or a successful replay can be reported as failure and then be followed by another writer.
- detectable: partly — a crash of the process is visible, but a wrong return code looks like an ordinary recovery status.
- silent: 1 — user-space libc on the described hosts implements setjmp in the usual way.
- basis: source

### E20
- contract: The recovery process must be able to allocate memory for every page of the active log and for the record index built from it.
- source: logbuf/recover.c:1031 "	/* TODO: is this a safe assumption ---"
- stated: stated
- violation: The active log is larger than the address space or the ulimit of the salvager, malloc fails, and recovery panics or raises out of the replay.
- at-risk: G8 and G10 fail because replay never finishes, so the aggregate stays dirty, and the recovery-time claim assumes the active log can be read in and applied.
- detectable: yes — allocation failure panics or raises, and the operator sees the salvager stop.
- silent: 2 — the paper's logs are a few megabytes and fit, but a large aggregate under a tight data limit fails this way occasionally.
- basis: source

### E21
- contract: After a crash the primary superblock must still be a valid aggregate header naming this log, because attach and the salvager do not fall back to an alternate superblock.
- source: anode/aggregate.c:1138 " *     primary superblock, and since the salvager doesn't presently"
- stated: stated
- violation: The only primary superblock is torn or unreadable, or its block size or log length no longer matches the device, and the alternate copies are ignored.
- at-risk: G58 fails because the log is never opened, so replay cannot run, and a superblock that points at the wrong log length or the wrong container makes replay use the wrong blocks.
- detectable: yes — a bad primary header fails aggregate open with a not-an-aggregate error.
- silent: 1 — the superblock is a single checked block written at format and grow, and losing it with no error at the disk is rare.
- basis: source

### E22
- contract: The host must call the file system's sync often enough that committed dirty metadata buffers are written and the active log is checkpointed on the order of the paper's interval of T seconds.
- source: §"Recovery Time" "every T seconds, as is the case with Episode, then the active portion of the log can rise to include all the"
- stated: implicit
- violation: The update daemon is disabled or wedged, so dirty metadata stays in memory until log-full handling is forced to write it, and the active tail grows to the whole log.
- at-risk: G9, G10, and G21 fail because recovery must replay every committed update whose buffer is still dirty, so recovery time tracks the uncheckpointed tail rather than the activity at the crash.
- detectable: partly — the log-full path eventually writes buffers and can stall new transactions, which operators notice, but a merely long tail produces no error.
- silent: 2 — the described systems run a periodic sync, and a host left without it is an occasional administrative state rather than the common one.
- basis: text

### E23
- contract: When recovery or logging hits a hard I/O error, a bad log magic, or a checksum or pass-number failure outside the in-transit window, the operator must run the salvager and must not serve the aggregate.
- source: §"Component Architecture" "can not regenerate a consistent le system, however, such as when hard I/O errors occur while updating"
- stated: stated
- violation: The operator ignores a recovery I/O error, forces the aggregate online, or keeps serving after the kernel panics on a log write error and is rebooted onto the same disk.
- at-risk: G1 fails because the paper's own limit is that hard errors while updating critical metadata leave a state replay cannot repair, and serving it preserves the inconsistency.
- detectable: yes — recovery raises an error and the log write path panics with an I/O message.
- silent: 2 — the error is visible, but continuing to serve after it is an occasional operator action over a year.
- basis: text

### E24
- contract: Higher layers must allow only one writer, the kernel service or the salvager, to use an aggregate at a time, and must have stopped new transactions before shutdown of the log.
- source: logbuf/tran.c:553 "       * levels have properly synchronized access to this aggregate."
- stated: stated
- violation: Two hosts mount the same aggregate, or the salvager runs against a mounted aggregate, or shutdown runs while vnode threads are still in StartTran.
- at-risk: G1 and G55 fail because the two writers append different tails and then one of them writes a restart record over the other's committed updates.
- detectable: partly — shutdown asserts if active transactions remain, but two hosts do not see each other's in-memory state and both can finish without an error.
- silent: 2 — dual-mount and salvage-while-mounted mistakes are a known occasional administrative failure, and nothing on the disk serializes them.
- basis: source

### E25
- contract: The anode, directory, and vnode layers must make every metadata update, and only metadata updates, through a logged buffer operation inside a transaction.
- source: §"Logging Architecture" "requires only that the meta-data be consistent. Episode logs only meta-data changes. Although restricting"
- stated: stated
- violation: A directory, bitmap, indirect block, or anode is written as user data or by a raw device write, or a user-data block is passed to the log as a logged buffer.
- at-risk: G1 and G4 fail because replay never sees the metadata change, or it tries to undo and redo user data and then leaves the metadata image inconsistent.
- detectable: no — the log records what it is given and has no second copy of the container type.
- silent: 1 — the callers in this tree mark directories, bitmaps, and anodes logged and send them through elbb_Modify, so a bypass in ordinary operation is rare.
- basis: text

### E26
- contract: Callers must modify a logged buffer only through Modify, Fill, or Initialize, and must not mix logged and unlogged updates to the same buffer.
- source: logbuf/buffer.c:1442 "      /* Require that updates to logged buffers are either always logged or"
- stated: stated
- violation: A caller stores into the buffer's data pointer, or logs one update to a buffer and writes the next update with logging off, so the log does not contain the bytes that later reach disk.
- at-risk: G4, G6, and G7 fail because the old and new values in the log are not the update that the dirty buffer holds, and replay restores the wrong bytes.
- detectable: no — the checks that would reject a mixed update are compiled out, and a direct store is not looked for.
- silent: 1 — the anode paths use the modify routines consistently, so a direct store in the described system is a rare bug rather than a routine event.
- basis: source

### E27
- contract: Callers must use buffer initialization only for a block just created with CreateBlock, whose previous contents must not be restored.
- source: logbuf/buffer.c:1588 " * By initialization, we mean modification in the case where the old data"
- stated: stated
- violation: A caller initializes an existing metadata block, so the log gets the new bytes and not the old ones, and an abort cannot put the old bytes back.
- at-risk: G4 and G6 fail because undo has no old value, and recovery either leaves the new bytes in place or writes a redo of data the aborted transaction should not keep.
- detectable: no — initialization is accepted whenever the caller asks for it.
- silent: 1 — initialization is tied to block creation in the anode code, and using it on a live block is rare.
- basis: source

### E28
- contract: Each transaction the caller commits must take a consistent metadata state to another consistent one, including directory, bitmap, indirect-block, anode-table, and clone copy-on-write updates.
- source: §"Logging Architecture" "operations, followed by a deletion of the empty le. After each transaction, the le system is consistent, if"
- stated: stated
- violation: A vnode operation commits a directory entry without the anode, or updates a copy-on-write pointer in a different transaction from the block allocation that the pointer names.
- at-risk: G19 and G1 fail because replay is faithful: it will durably keep the inconsistent transaction and, after a crash, that is the metadata the file system serves.
- detectable: no — the log cannot tell a consistent group of updates from an inconsistent one.
- silent: 2 — the split of large operations is a standing source of missed pairings, and a crash in between is the only symptom, so a missed pairing can sit unnoticed until then.
- basis: text

### E29
- contract: Callers must keep each transaction within the reservation the log assumed for them and must end it, splitting any larger operation into such transactions.
- source: §"Logging Architecture" "exceed the space available in the log. Transactions that run too long or modify too much data represent"
- stated: stated
- violation: A fileset or directory operation logs more than the presumptive maximum, or never calls EndTran, so the reservation no longer covers the tail the transaction pins.
- at-risk: G17 fails because admission control reserves a fixed size per transaction, and a larger one, or one that never ends, pins the log until new transactions cannot start or the circular buffer is overrun.
- detectable: partly — an oversized completed transaction prints that the reservation was raised and can assert if the log cannot hold it, but a transaction that never ends only stalls the log.
- silent: 2 — ordinary vnode operations stay inside the bound, but large administrative updates have overrun it often enough to be occasional.
- basis: text

### E30
- contract: A caller that force-starts a nested undo-zero transaction must keep that transaction's reservation plus its parent's within the size of one maximum transaction.
- source: logbuf/log.c:1673 "       * space in the log.  The caller is guaranteeing that the new"
- stated: stated
- violation: The VM or the anode layer nests an undo-zero transaction whose combined size exceeds one maximum transaction, and the log admits it without checking free space.
- at-risk: G17 fails because the force path skips the free-space test, so the nested records can extend the active log past the circular buffer.
- detectable: no — the force path is defined to proceed regardless of free space.
- silent: 2 — nested undo-zero is used on the allocation path, and an overrun is occasional under heavy allocation rather than routine.
- basis: source

### E31
- contract: A thread that waits for other transactions to complete or commit, including quiesce, must not itself hold an active transaction.
- source: logbuf/tran.c:1313 " * CAUTIONS -- The calling thread must not be holding any active transactions."
- stated: stated
- violation: A vnode thread calls quiesce or otherwise waits for a transaction while it still owns an active transaction that the wait needs to end.
- at-risk: G32 and G33 fail because the wait never finishes, so the caller does not get the serialization or the commit it asked for, and the transactions it holds stay uncommitted.
- detectable: yes — the file system hangs, which operators and clients see.
- silent: 1 — the hang is visible, and the calling code in this tree does not wait while holding the transaction it needs to finish.
- basis: source

### E32
- contract: Whenever two uncommitted transactions use the same metadata object, the caller must merge them into one equivalence class with a tlock while the later transaction is still active.
- source: anode/tlock.h:20 " * the same lock, they must be put in the same equivalence class.  To minimize"
- stated: stated
- violation: A code path locks a shared anode, bitmap, or volume object with an ordinary lock, or releases it without elbt_ECMerge, and the later transaction then commits on its own.
- at-risk: G12, G13, and G14 fail because early lock release is safe only when the equivalence class aborts or commits together, and a crash otherwise keeps one update and rolls back the other.
- detectable: no — merge of a missing partner is not attempted, and both transactions commit or abort without an error.
- silent: 2 — missed tlocks have shown up on real fileset paths, and the resulting crash inconsistency produces no error while the system is up.
- basis: source

### E33
- contract: The allocation bitmap's logged-or-unlogged bit must match the block's use, and the allocator must perform the buffer-pool transition when a block changes from logged to unlogged or the reverse, before the block is reused.
- source: §"Data Architecture" "the fragment is allocated, and whether the fragment represents logged or unlogged data. This last distinc-"
- stated: stated
- violation: A freed metadata block is handed out as user data, or the reverse, without killing the old buffer and without the bitmap bit changing in the same transaction.
- at-risk: G1 and G51 fail because a logged image is written as an unlogged block, or an old logged buffer is written back over the new occupant, and recovery then skips or replays the wrong records.
- detectable: partly — recovery raises a user-data or metadata error for some bad reuse orders, but a wrong bitmap bit alone is not checked against the buffer type.
- silent: 2 — reuse is continuous, and a missed transition is silent until a later crash, which makes it occasional rather than routine in a year of operation.
- basis: text

### E34
- contract: Callers must pass metadataOK to elbb_Kill only after the transaction that freed that metadata block has committed, which is also after every transaction that modified the block has committed.
- source: logbuf/buffer.c:1359 " * PARAMETERS -- metadataOK is true if it is safe to kill dirty metadata"
- stated: stated
- violation: The allocator kills a dirty logged buffer before the freeing transaction's end record is on disk, so the buffer leaves the age queue while its updates exist only in the log or are still uncommitted.
- at-risk: G21 and G22 fail because checkpointing drops the log tail when no dirty buffer still pins it, and killing the buffer early discards committed updates that were not yet on their home blocks.
- detectable: no — with metadataOK set, the kill succeeds and returns zero.
- silent: 1 — the freed-block list kills metadata only after TranIsCommitted returns true, so a premature kill in ordinary operation is rare.
- basis: source

### E35
- contract: The allocator must not leave an uncommitted kill record newer than ordinary records on the same block, and every record a committed kill skips must already be committed.
- source: logbuf/recover.h:84 " * record on the same block.  The transaction contain such records must have"
- stated: stated
- violation: A new metadata update is logged for a block while an undo-zero kill of that block is still uncommitted, or the kill would skip a record whose transaction has no end record.
- at-risk: G51, G52, and G53 fail closed: recovery raises user-data or metadata failure and does not finish replay, so the aggregate is left unrestored.
- detectable: yes — recovery raises RCVR_USERDATA or RCVR_METADATA when it sees that order.
- silent: 1 — the bad order is rare in the allocator as written, and when it is present recovery reports it rather than succeeding quietly.
- basis: source

### E36
- contract: For a newly allocated user-data block, the caller must record an undo-zero covering every byte that could expose old contents, and must end that transaction only when the first write of the block has completed.
- source: §"Logging Architecture" "problem by starting another transaction when the block is allocated, and ending it when the rst write"
- stated: stated
- violation: The allocating transaction commits, the machine crashes before the first write is durable, and no undo-zero record covers the block, so the old occupant remains readable in the new file.
- at-risk: G16 fails because recovery zeroes a block only when that special transaction aborts, and without the record it has nothing to apply.
- detectable: no — the allocation looks like a normal committed metadata transaction.
- silent: 4 — the buffer path records undo-zero, but the VM strategy path used for ordinary file data does not, and those allocations proceed with no error.
- basis: text

### E37
- contract: The caller must attach an undo-zero record only after the new bytes are in the buffer, and must do so before ending the transaction that allocated the block.
- source: anode/anode.c:696 "         * attach the undo-zero record.  If we do this any earlier, the logbuf"
- stated: stated
- violation: The caller attaches undo-zero before the new data is copied, the buffer package cleans the buffer and ends the undo-zero transaction, and the new bytes are stored only afterward.
- at-risk: G16 fails because the undo-zero transaction can commit or abort against a buffer that does not yet hold the first write, so recovery either zeroes a block the user already replaced or fails to zero a block that still holds old data.
- detectable: no — cleaning the buffer and ending the nested transaction is a normal logbuf action.
- silent: 1 — the anode write path attaches the record at release, after the copy, so the early attach is rare on the described path.
- basis: source

### E38
- contract: For I/O that does not use the buffer cache, the VM must call the undo-zero entry with the byte range being written and must not end that transaction before the write completes.
- source: logbuf/buffer.c:2415 " * the specified range of bytes.  This is to be used by the VM system for I/Os"
- stated: stated
- violation: Strategy writes a newly allocated block from the page cache and never records an undo-zero, which is the state of the strategy module in this tree.
- at-risk: G16 fails on the VM path: a crash after the allocation commits and before the page is durable leaves the previous contents in the new block, and recovery does not zero it.
- detectable: no — the write completes through the normal iodone path, and the missing record is not checked.
- silent: 5 — the strategy code states that undo-zero processing is not implemented, and VM file writes are the normal AIX path, so the omission is routine and raises no error.
- basis: source

### E39
- contract: While quiesce waits for undo-zero transactions, the VM's own asynchronous daemon must keep running and must end those transactions when its I/O completes.
- source: logbuf/tran.c:1239 " *     from the VM system which has its own Async daemon to complete I/O.  We"
- stated: stated
- violation: The thread blocked in quiesce is the thread that would complete the VM I/O, or the daemon stops, so the undo-zero transactions stay active and quiesce never returns.
- at-risk: G32, G33, and G38 fail because quiesce is defined to wait for those transactions, and a stuck daemon means commit and serialization do not finish.
- detectable: yes — the quiesce call hangs and clients stop making progress.
- silent: 1 — the hang is visible, and on the described AIX integration the daemon is a separate thread.
- basis: source

### E40
- contract: A caller that needs metadata to be persistent, such as fsync, must invoke log force or fsync-force on the buffers of that file, identified by the file's magic or by an explicit block list, and the VM must write back that file's dirty pages.
- source: §"Logging Architecture" "       Meta-data changes to the disk itself can often be deferred, unless speci cally requested by an oper-"
- stated: stated
- violation: The vnode fsync path returns without elbb_LogForce, the file-handle magic on the buffers does not match the magic passed to fsync-force, or the platform's VM flush is a stub that returns success.
- at-risk: G15, G23, and G40 fail because deferred metadata stays deferred, and fsync-force writes only the buffers the caller actually names.
- detectable: no — fsync returns success as soon as the calls it does make return, including a VM stub that does nothing.
- silent: 3 — metadata force is wired on the vnode path, but the SunOS VM integration the paper describes is incomplete, so a silent no-op page flush is a normal configuration there.
- basis: text

### E41
- contract: The caller of log initialization must not have dirty buffers cached for that device, and after recovery reports that it repaired the log the caller must drop cached buffers before using the device.
- source: logbuf/buffer.c:1839 "	       * buffers were dirty when elbb_LogInit was called."
- stated: stated
- violation: Log initialization is called while dirty metadata buffers are cached, or a caller of recovery keeps those buffers and writes them back over the blocks recovery just repaired.
- at-risk: G60 and G1 fail because the shutdown used to invalidate the pool writes or discards the dirty buffers against the recovered disk, and a later write of a stale buffer restores the pre-recovery image.
- detectable: no — initialization assumes the cache is clean and does not compare buffer contents with the disk.
- silent: 1 — attach kills the log pages and initializes the log before serving, so a dirty cache at that moment is rare.
- basis: source

### E42
- contract: One device object and one block number must name one physical block, and the C layout must place the device pointer immediately before the block number with no padding between them.
- source: logbuf/buffer.c:839 "       * note that for this key to work, we assume that the device and"
- stated: stated
- violation: Two async device objects alias one disk, or a compiler inserts padding between the device pointer and the block number, so the address hash misses or collides.
- at-risk: G5 and G7 fail because two buffer headers for one block let one be written without the log force recorded on the other, and a hash miss serves a stale cached copy.
- detectable: partly — wildly wrong data can trip later asserts, but a duplicate device alias is served without an error.
- silent: 1 — the compilers used for SPARC and POWER lay this pair out with no padding, and one device object per aggregate is the normal open path.
- basis: source

### E43
- contract: An aligned store of a 32-bit value must be atomic with respect to every concurrent reader on the machine.
- source: logbuf/log.c:2602 " * a 32 bit quantity is atomic w.r.t. all readers."
- stated: stated
- violation: A reader observes a half-updated 32-bit tuning or status word, for example a log-full threshold mixed from the old and new values.
- at-risk: G17 is the closest guarantee: a torn log-limit word can admit transactions the free log cannot hold, or refuse transactions that would have fit. I am unsure it affects any other guarantee.
- detectable: no — the torn value is used as if it were stored whole.
- silent: 1 — aligned 32-bit stores are atomic on the SPARC and POWER machines Episode runs on.
- basis: source

### E44
- contract: The host must not require a stricter alignment than 32-bit for the log record layouts, and recovery must run with the same integer endianness and width as the writer.
- source: logbuf/logrec.h:44 " * more strict alignment than is assumed here (i.e. all data"
- stated: stated
- violation: The aggregate is recovered on a big-endian host after being written on a little-endian host, or the CPU faults on an access the log record macros perform.
- at-risk: G4, G47, and G54 fail because pass numbers, record types, and old and new images are decoded as different values, so replay applies the wrong bytes or rejects the log.
- detectable: partly — a strict-alignment fault panics, but a wrong endianness can still look like a well-formed log of different contents.
- silent: 1 — the described deployments recover on the same machine that wrote the log.
- basis: source

### E45
- contract: Memory that holds log pages and metadata buffers must remain resident, with its contents unchanged, until logbuf releases it.
- source: logbuf/logrec.h:371 "#define logbuf_pin(x, s) /* nothing */"
- stated: implicit
- violation: On a platform where the pin macro is empty, the kernel reclaims a dirty metadata or log page and later returns different bytes for the same address.
- at-risk: G4 and G5 fail because the bytes forced to the log or written to the home block are not the update the transaction made.
- detectable: no — the buffer header still says the page is valid.
- silent: 2 — AIX pins the pages, but the other kernels the paper ships on do not, and a reclaim of that memory is an occasional risk rather than an hourly one.
- basis: source

### E46
- contract: The pointer passed to the log and buffer tuning call must address memory in the caller's own address space that holds the whole value being read or written.
- source: logbuf/buffer.c:873 " * Note that elbb_Tune assumes the address of value is in its address"
- stated: stated
- violation: A caller passes a user pointer or a short buffer, so the tune reads or writes the wrong word and changes the maximum log or the full-log fraction.
- at-risk: G17 fails if the log-full fraction or the maximum number of logs is silently changed to a value the running transactions cannot satisfy. I am unsure it affects guarantees other than admission and attach.
- detectable: no — there is no copyin check, and a bad pointer that happens to be readable is accepted.
- silent: 1 — in-kernel callers pass a kernel address, and a bad tune from user space is rare in ordinary operation.
- basis: source

### E47
- contract: Callers of the quick logged modify and of buffer fill must pass metadata that already resides in the kernel address space, never a user pointer and never file-body data.
- source: logbuf/buffer.c:1703 "       * assume along this code path that we never have user data (e.g. we"
- stated: stated
- violation: A caller points the fast modify path at a user address or at file contents, so the log record copies the wrong bytes or faults, and user data is written into the log.
- at-risk: G4 fails because the old and new images in the log are not the metadata update, and replay writes those wrong bytes back to a metadata block.
- detectable: partly — a bad user address can fault, but a readable wrong address is logged as success.
- silent: 1 — the fast-modify path is unused and the fill path is given kernel patterns, so this mis-call is rare.
- basis: source

### E48
- contract: Code that runs during a kernel panic must not depend on starting further transactions once log-full handling has stopped retrying.
- source: logbuf/buffer.c:1762 "	if (osi_IsKernelPanic() && ++nLoops == ELBB_MAX_PANIC_LOOP)"
- stated: stated
- violation: Panic or crash-dump code keeps modifying metadata after elbb_StartTran returns failure, and a dirty buffer is then written without a new log record.
- at-risk: G5 and G7 fail because that buffer can reach disk with updates that are not in the log, so the next recovery cannot redo or undo them.
- detectable: partly — the start call returns an out-of-memory code, but a caller that ignores it and writes anyway gets no further check.
- silent: 1 — kernel panics are rare over a year, and the panic path usually stops issuing new metadata transactions after a few attempts.
- basis: source

### E49
- contract: The checksum version recorded on the log must be a version recovery knows, so torn pages are rejected rather than ignored.
- source: logbuf/recover.c:2578 "	    /* Unknown checksum type recorded on disk. Force success of"
- stated: implicit
- violation: An operator or patchlog sets an unknown checksum version, and recovery then treats every page checksum as valid.
- at-risk: G54 fails because a torn or out-of-order log page in the in-transit window is accepted as the head, and replay proceeds from a page the disk did not finish writing.
- detectable: partly — recovery prints that it is ignoring the checksum, but it still returns success if the rest of the log parses.
- silent: 1 — logs are created with the CRC-32 version, and changing that version is a rare manual act.
- basis: source

### E50
- contract: Transaction initialization must run single-threaded, before any thread starts a transaction.
- source: logbuf/tran.c:177 " * Locks: assumes no locking (single-threaded at init time).  Call is"
- stated: stated
- violation: Two threads call the transaction initializer concurrently during the first mount, and the free list or the locks are published half-initialized.
- at-risk: G13 and G29 fail because the transaction structures those guarantees use can be duplicated or lost, so commits and equivalence classes are recorded in the wrong objects.
- detectable: partly — a crash during initialization is visible, but a duplicated free-list link can survive into later transactions.
- silent: 1 — the first mount initializes once, before the file system accepts calls, so a concurrent second initializer is rare.
- basis: source

## Recognised

- OT 3435, recorded in logbuf/crc.c: out-of-order sector writes inside a log page made a torn page look valid, which is why page checksums were added; E3 is the contract that remains.
- OT 3338, recorded in the epimount history: the mount path did not recover a dirty log before the kernel attached it; that is E17.
- OT 3804 and OT 1020, new-block security, recorded in the anode and logbuf history: a crash after allocation and before the first write exposed the previous contents; E36 and E38, and strategy.c still says the VM undo-zero path is not implemented.
- OT 3802, recorded in anode/volume_table.h: a fileset path had no tlock, so equivalence classes were not merged; that is E32.
- OT 4548, recorded in logbuf/logbuf-locking: the fixed transaction reservation was too small for real callers; that is E29 and E30.
- Write-back disk caches that acknowledge a write before it is on media, the failure E2 names. I do not have an Episode defect number for it; it is the same class of bug as other write-ahead logs of the period.
- DB 3189, in tran.c: an optional compile forces every metadata transaction to commit before return. I did not list it, because with the option off the code matches the paper's rule that metadata may stay deferred until fsync.

## Report

50 contracts, E1 through E50.

`ls -R --ignore=episode` from the checkout root (this leaves out `source/episode/`):

```
.:
AGENTS.md
BRIEF.md
GUARANTEES.md
enumeration.md
source

./source:
episode-1992.pdf
episode-1992.txt
```

`git status`:

```
On branch main
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	enumeration.md

nothing added to commit but untracked files present (use "git add" to track)
```

Defects in `logbuf`'s own rules, not listed as contracts: an unknown checksum version is accepted and the check is skipped (recover.c around the message that the checksum is ignored), so E49 is only partly enforced. The restart page is deliberately not checksummed. The asserts that a logged buffer's updates are either all logged or all unlogged are compiled out. elbb_FastModify does not go through elbb_StartTran when the log is full; its comment says no caller uses it. The comment above user-space recovery says both that the code must run single-threaded and that locking was removed so several recoveries may run at once. The comment on MAX_TRAN_SIZE says 35K; the constant is 70 times 1024.

I could not decide three points. Dirty zero pages from efs_MakeWritableBlocks do not by themselves meet the paper's zero-on-abort rule, because they vanish on a crash unless they were written, so I kept E36 and E38; I am not sure the authors still considered the VM undo-zero record required once those pages existed. logbuf-locking names OT 5527 as a pass-number bug exposed by a test; I did not decide whether that bug is an environment contract, and the pass-number arithmetic itself is logbuf's rule. The silent score on E2 depends on how often the paper's SCSI disks had write-back caches enabled, which these sources do not say.
