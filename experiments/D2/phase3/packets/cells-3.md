# D2 judge packet 4 of 5 (cells, 3 of 3): Episode's log and recovery, against the sealed analysis

You are a judge. Work only from the text in this packet; do not read files, run commands or search.

Context: a component's log and recovery (`logbuf` in the Episode file system, OSF DCE 1.2.2) relies on contracts from the layers around it. Independent readers enumerated those contracts ("cells"); independent model authors then wrote TLA+ models and reported **findings**: violations of an obligation outside `logbuf` that break a stated guarantee of the log and recovery with the model's defences in place. A separate analysis, done before any of this and sealed, lists bugs, confirmed properties and an open item; it is given to you {SEALED_WHERE}. Items carry opaque ids; you are not told who wrote them. Packets are split by size by a stated rule; this one is part 4 of 5 (cells, 3 of 3).

Episode's criteria (fixed by Episode's steward 2026-10-26, before any list existed): a finding is a **match** for a sealed bug if it has the same violated contract, the same mechanism and the same class of effect; **partial** if it has the contract and one of the other two, or the right mechanism under a different contract; **no match** otherwise. A finding that claims a violation contradicting one of the sealed file's confirmed properties is **flagged** (name the property). A finding about the sealed file's open item is **unresolved**. A finding may match several bugs.

For **each cell**: does it name the violated contract that the sealed file records for some bug? Binary per cell; list the bugs if yes. A cell is a contract, not a finding; mechanism and effect do not matter here.

Answer schema: {"cells": [{"id": "C...", "names_contract_of": ["<sealed bug id>", ...], "reason": "<one sentence>"}]}  (empty list for no)

Answer with one JSON object only, as specified. Be concrete and brief; cite the sealed file's bug ids and the item's own words. Do not propose fixes. Disagreement with the sealed analysis is allowed: say so in `reason`.

## Cells

### C075
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

### C076
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

### C077
- contract: The storage stack must return the requested bytes and report failed or short I/O as an error.
- source: async/asevent.c:1126 "if (bp->b_flags & B_ERROR) {"
- violation: A driver returns success with a short transfer, wrong-sector read, or failed write while leaving B_ERROR clear.
- at-risk: G1, G31, G35, G40: success is interpreted as a complete transfer, so stale bytes or missing updates can survive recovery.
- detectable: partly — log checksums can catch bad reads; ordinary data blocks have no equivalent protection here.
- silent: 1 — Silent driver transfer errors are unusual on supported systems.

### C078
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

### C079
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

### C080
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

### C081
- contract: The user-space recovery process must provide setjmp and longjmp with ordinary C semantics, so the code passed to longjmp is the code setjmp returns.
- source: logbuf/recover.c:125 " * This assumes traditional semantics for an in-kernel setjmp/longjmp."
- violation: The C library or a kernel-style jump buffer returns 1, or returns 0, for every longjmp, and recovery reports failure for success or success for a checksum error.
- at-risk: G55 fails because a failed replay can still write a restart record, or a successful replay can be reported as failure and then be followed by another writer.
- detectable: partly — a crash of the process is visible, but a wrong return code looks like an ordinary recovery status.
- silent: 1 — user-space libc on the described hosts implements setjmp in the usual way.

### C082
- contract: Log-creation callers must exclude all other activity on that device while creating its log.
- source: logbuf/log.c:878 "Locking: This code presumes no other thread is calling for this"
- violation: A formatting utility creates the log while the filesystem still has active users.
- at-risk: G1, G63: zeroing the log can destroy active undo and redo history.
- detectable: partly — aggregate mount exclusion can detect use, but log creation cannot see every external writer.
- silent: 1 — Normal tools format offline.

### C083
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

### C084
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

### C085
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

### C086
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

### C087
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

### C089
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

### C090
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

### C091
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

### C092
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

### C093
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

### C094
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

### C095
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

### C096
- contract: The VM and vnode layers must ensure the strategy layer’s documented bound on simultaneous waiters for each in-transit block.
- source: anode/strategy.c:271 "multiple I/O requests for a given block, and other writers are"
- violation: Two VM or volume-operation threads wait for the same block where the code expects at most one waiter.
- at-risk: G16 and buffer/I/O availability: premature in-transit record reuse can invalidate synchronization.
- detectable: partly — waiter-count assertions catch documented cases, but all release races require careful tracking.
- silent: 1 — The source’s waiter checks usually make a violation visible.

### C097
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

### C098
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

### C099
- contract: The operator leaves removable media in place until the last aggregate close has returned, and no other agent reads or writes it during that close.
- source: anode/aggregate.c:1716 " * this means that if the disk is on removable media it could be safely"
- violation: The operator ejects the disk, or a raw copy starts, after the unmount call begins and before the restart block write finishes.
- at-risk: G39 and G56 fail because the clean restart never becomes durable, so the next attach either replays a torn close or treats a partial restart as clean.
- detectable: partly — a failed restart write returns RCVR_FAILED from the restart writer; an eject after a false completion is the E2 case.
- silent: 1 — unloading during the close window is rare in ordinary server operation.

### C100
- contract: Callers requiring persistence must choose a mode that waits for the necessary data or transaction commit and check its result.
- source: logbuf/logbuf.p.h:63 " elbb_async, /* schedule write now, but don't wait for completion */"
- violation: A vnode fsync returns success after SyncForce, async release or a completion-only transaction wait.
- at-risk: G15, G40: scheduled or ended changes can still be lost on a crash.
- detectable: partly — the selected mode is visible, but the caller's promised durability is outside logbuf.
- silent: 1 — Using a scheduling-only API for persistence is an uncommon caller defect and is invisible in ordinary operation.

### C101
- contract: Log-creation callers must enter without holding buffer-package locks that creation needs.
- source: logbuf/log.c:880 "I/O, it presumes locks are not held in the buffer package."
- violation: A caller creates a log while retaining the buffer lock needed by CreateBlock.
- at-risk: G63 and initialization availability: recursive lock acquisition can deadlock creation.
- detectable: partly — lock ownership tracking can expose the cycle.
- silent: 1 — Normal initialization follows the documented lock convention.

### C102
- contract: Aggregate configuration must keep log length and page indices within the range supported by the on-disk fields and signed-distance arithmetic.
- source: logbuf/log.c:187 "As with pass numbers, log offsets are unsigned int16s. So we have to do"
- violation: A tool allocates a log whose page index truncates in oldestDataPage or whose distance changes sign in int16 arithmetic.
- at-risk: G17, G20, G21, G54: tail retention and recovery head/tail interpretation may select incorrect history.
- detectable: partly — initialization can validate representability; the precise safe bound requires further analysis of all comparisons.
- silent: 1 — The paper’s example log sizes are small relative to these field ranges.

### C103
- contract: The OS time service must provide usable elapsed-time progression for the buffer-cache aging heuristics.
- source: logbuf/buffer.c:2857 " * reused. Thus the average age of reuse must be much smaller than the"
- violation: A broken clock freezes age calculations or jumps enough to distort cache-cost comparisons.
- at-risk: G9, G11: maintenance and cache behavior may lose the stated recovery/performance characteristics; correctness dependence is uncertain.
- detectable: partly — clock anomalies can be detected against an independent clock.
- silent: 1 — Clock failures are unusual, and cache heuristics tolerate ordinary timing variation.

### C104
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

### C105
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

### C106
- contract: A port must ensure that pointer alignment calculations do not truncate addresses and that cast log records meet CPU alignment requirements.
- source: logbuf/logrec.h:232 "a power-of-two. The use of (unsigned) may not be strictly correct"
- violation: The code is built with 64-bit pointers and 32-bit unsigned, and ALIGN discards the upper address bits.
- at-risk: G1 and log service availability: memory accesses can fault or target unrelated storage.
- detectable: partly — faults or address checks detect many cases, but aliasing can corrupt memory silently.
- silent: 1 — The paper’s 32-bit machines meet this condition; an unadapted later port may not.

### C107
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

### C108
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

### C109
- contract: Initialization callers must supply writable buffer-pool memory of the declared size and keep it owned by logbuf for the package lifetime.
- source: logbuf/buffer.c:731 "caddr_t startAddr = elbbParams->bufferPool;"
- violation: The caller frees or repurposes the pool after Init, or exaggerates byteCount beyond its allocation.
- at-risk: G4, G5, G42: log and cached bytes can be corrupted in memory before being written.
- detectable: partly — allocation and lifetime instrumentation can detect invalid ownership; ordinary I/O cannot establish it.
- silent: 1 — Normal kernel initialization retains the supplied pool.

### C110
- contract: Callers must classify external buffers as data or logged buffers and leave internal buffer types to logbuf.
- source: logbuf/logbuf.p.h:47 " * users of this package are restricted to the first two cases"
- violation: A filesystem caller requests elbb_bufLog for a normal metadata block.
- at-risk: G5, G42: internal-type handling can bypass ordinary logging or cache rules.
- detectable: partly — type assertions exist on some paths.
- silent: 1 — Internal buffer types are not normally requested by filesystem callers.
