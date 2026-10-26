# Environment contracts for the Episode log and recovery

### E1
- contract: A crash stops the machine, discards memory, and leaves on disk only updates whose writes had reached the device.
- source: §"Component Architecture" "In the event of a crash, only some of the updates to the le system"
- stated: implicit
- violation: The machine keeps issuing writes after the failure, or a DMA engine scribbles arbitrary blocks as power fails.
- at-risk: G1 and G8 fail because recovery replays a log that no longer matches the blocks actually left on disk. Unsure how much of a wild post-crash write the checksum on log pages would still catch.
- detectable: partly — a damaged log page fails its checksum or salvage id and recovery stops; a wild write onto a metadata home block has no log checksum.
- silent: 1 — the paper's crash model is a power loss or kernel halt, and a scribbling failure is rare on the Sun and RS/6000 hosts it names.
- basis: text

### E2
- contract: When the driver reports an I/O complete, that entire transfer is on stable storage and later reads, including reads after power loss, return those bytes.
- source: logbuf/recover.c:894 "     * underlying system to really guarantee that a page is on disk"
- stated: stated
- violation: A disk or controller write-back cache acknowledges the write while the bytes still sit only in volatile memory, and a power loss drops them after Episode has forced the log and then written a metadata block.
- at-risk: G5, G7, G20, G29, and G30 fail because recovery trusts a completed log page and will not undo a metadata write whose log record was lost after a false completion.
- detectable: no — asevent treats the driver's completion as truth, and the log records the I/O window from that report.
- silent: 3 — SCSI disks of this era often could enable a volatile write cache, and the file system sees a normal completion until a power loss.
- basis: source

### E3
- contract: A device sector is written entirely or left entirely unchanged, including the first sector of a log page and every sector of a metadata block.
- source: logbuf/recover.c:746 "     * correctness/atomicity of each sector.  So if the log page did"
- stated: stated
- violation: A crash tears a 512-byte sector so the log-page header mixes a new checksum with an old pass number, or a metadata sector mixes bytes from two versions of the same block.
- at-risk: G54 fails for a torn log header, and G6 and G7 fail for a torn metadata sector whose unlogged bytes recovery will not rewrite.
- detectable: partly — a torn log page usually fails the checksum once the header sector is whole; a torn metadata sector is not checksummed.
- silent: 1 — the single SCSI disks in the paper's setups write 512-byte sectors atomically, and a torn sector is a rare firmware fault.
- basis: source

### E4
- contract: The device's atomic sector is large enough to hold the whole log-page header and its checksum, which the log places at the start of the page.
- source: logbuf/recover.c:744 "    /* The log page header ( including checksum ) is in the first"
- stated: stated
- violation: The device sector is smaller than the header plus checksum, so a crash can persist a new checksum while leaving part of the header from an older page.
- at-risk: G54 fails because the binary search trusts the header sector to describe the whole page, and a split header can select the wrong log head.
- detectable: partly — a mismatched checksum on the in-transit window pulls the head back; a header that is internally consistent and checksums against a torn body can be accepted.
- silent: 1 — Episode blocks are at least 1K and the header plus a CRC-32 fit in a 512-byte sector on the machines the paper runs.
- basis: source

### E5
- contract: The driver reports a transfer that did not finish as a hard error, and the async layer is entitled to treat any other completion as success.
- source: async/asevent.c:1070 "    if (bp->b_error == ESOFT) {"
- stated: implicit
- violation: AIX returns ESOFT for a write that did not reach stable media, and asevent_Iodone clears b_error and B_ERROR before the log inspects the event.
- at-risk: G5 and G29 fail because a log force or a metadata write is treated as committed when the transfer was only partial.
- detectable: no — the error is cleared inside the async layer before CheckIOError runs.
- silent: 2 — this path exists only on AIX, and drivers return ESOFT for an incomplete durable write only on some media faults.
- basis: source

### E6
- contract: Until Episode overwrites a block, the device returns the bytes of the last completed write to that block, or it returns an I/O error.
- source: logbuf/recover.c:756 "     * expected to be on disk correctly. If checksum errors are"
- stated: stated
- violation: A later media error, a misdirected write, or a dropped sector changes a log page or a metadata block that recovery still needs, and the read succeeds with different bytes.
- at-risk: G6, G7, and G1 fail; a corrupted log page outside the in-transit window aborts recovery, and a corrupted metadata home block is applied as if it were the image the log expected.
- detectable: partly — log pages are checksummed and a bad page raises RCVR_IOERR; metadata home blocks have no checksum, so a wrong image is accepted.
- silent: 1 — silent bit rot or a misdirected write over a year on these SCSI disks is rare, and a checksum failure is visible when it hits a log page.
- basis: source

### E7
- contract: The kernel's device-block conversion addresses the same physical sectors the driver writes, and an Episode block is an integer number of those sectors.
- source: async/asevent.c:139 "#define ToBufferBlocks(adevice, ablock, aoffset) \"
- stated: implicit
- violation: DEV_BSIZE, abtodb, or btodb disagrees with the disk's sector size, so log and metadata I/O lands on the wrong addresses.
- at-risk: G1, G5, and G54 fail because the log and the home blocks recovery reads are not the blocks Episode wrote.
- detectable: partly — a wildly wrong address often returns an I/O error and panics a log read; an off-by-a-factor address on a large disk can succeed with unrelated bytes.
- silent: 1 — the SunOS and AIX ports the paper describes use one consistent DEV_BSIZE for the disk they mount.
- basis: source

### E8
- contract: Memory the log pins, or hands to the driver, stays resident and unmodified until the matching I/O completes, and the virtual memory system does not write a buffer-pool page by any other path.
- source: async/async.p.h:83 "#define ASEVENT_NOPIN		16	/* do not pin/unpin data  (AIXism) */"
- stated: stated
- violation: pin fails or is a no-op and the kernel reclaims a log page or a dirty metadata buffer, or it writes that page from a paging path that never forces the log.
- at-risk: G5 and G42 fail because the bytes that reach disk are not the bytes that were logged, or the logged page is gone before the write completes.
- detectable: partly — on AIX a failed pin trips afsl_MBZ; on platforms where pin is empty, a stolen page is silent.
- silent: 1 — Episode allocates the buffer pool as kernel memory and pins log pages on AIX, and a pager writing those pages on the paper's kernels is rare.
- basis: source

### E9
- contract: The process that runs recovery can allocate memory for every page and record of the active log at once.
- source: logbuf/recover.c:1031 "	/* TODO: is this a safe assumption ---"
- stated: stated
- violation: The salvage process is short of address space or the active log is larger than the heap, and osi_Alloc or the recovery allocator fails.
- at-risk: G8 and G55 fail because recovery panics or unwinds before it writes the clean restart record.
- detectable: yes — SafeDumpLog panics on malloc failure, or the longjmp path returns an error the operator sees.
- silent: 1 — a failed allocation stops recovery with a panic or an error, so a year of ordinary crashes does not hide it.
- basis: source

### E10
- contract: setjmp and longjmp, and the kernel exception longjmp where it is still compiled in, restore the recovery catch point and abandon the failed pass.
- source: logbuf/recover.c:125 " * This assumes traditional semantics for an in-kernel setjmp/longjmp."
- stated: stated
- violation: The C library or the kernel exception handler returns into a half-updated recovery structure, or it fails to jump, and recovery continues after RCVR_RAISE.
- at-risk: G8 and G50 fail because a detected bad page is then applied, or cleanup is skipped and a later pass uses freed record memory.
- detectable: no — a broken jump looks like a crash or a wrong repair, and the log package has no separate check that the jump happened.
- silent: 1 — the user-space C library on the paper's hosts provides ordinary setjmp, and a broken jump would be a porting fault rather than a yearly event.
- basis: source

### E11
- contract: The machine that recovers a log uses the same endianness, integer sizes, and structure padding as the machine that wrote it.
- source: logbuf/logrec.h:44 " * more strict alignment than is assumed here (i.e. all data"
- stated: implicit
- violation: An aggregate written on a big-endian SPARC or RS/6000 is recovered on a little-endian host, so the salvage id, pass number, and record fields are byte-swapped.
- at-risk: G54 and G56 fail closed when the magic number does not match, and G8 fails open if a swapped header happens to look like a plausible page.
- detectable: partly — a swapped salvage id makes GetCleanLogInfo and the page scan reject the log; a few swapped fields can still checksum if the checksum was stored in the same byte order.
- silent: 1 — the paper's running systems are SPARC and RS/6000, both big-endian, and moving an aggregate to the other endianness is rare.
- basis: source

### E12
- contract: The CPU and compiler honor the log's 4-byte alignment rules for on-disk records and in-memory casts.
- source: logbuf/logrec.h:44 " * more strict alignment than is assumed here (i.e. all data"
- stated: stated
- violation: A port to a machine that faults on the unaligned references the macros still perform, or a compiler inserts padding the on-disk layout does not have.
- at-risk: G4 and G42 fail because a record is stored or recovered at the wrong offset, so undo and redo patch the wrong bytes.
- detectable: partly — recovery raises RCVR_ALIGN when a pointer fails PTR_ALIGNED; a padded struct that is still 4-byte aligned is accepted.
- silent: 1 — the paper's SPARC and RS/6000 ABIs match the layout the 1992 code was written for.
- basis: source

### E13
- contract: A naturally aligned 32-bit store is atomic with respect to every reader on the machine.
- source: logbuf/log.c:2602 " * a 32 bit quantity is atomic w.r.t. all readers."
- stated: stated
- violation: A reader observes a half-updated word of a tuneable log parameter while another CPU stores it.
- at-risk: Unsure. The stated use is elbl_Tune's shared counters; a torn limit could disturb G17's admission check if a caller ever set one of those words in parallel.
- detectable: no — a torn read returns a plausible integer and the log does not checksum memory.
- silent: 1 — the hosts in the paper provide atomic aligned 32-bit stores, and the tune path is not on the crash-recovery hot path.
- basis: source

### E14
- contract: The caller of log initialization passes the full ordered list of preallocated log-container blocks, and those blocks are not also used as file or metadata blocks.
- source: anode/aggregate.c:326 "	    /* All log pages must be pre-allocated.  There is a faster way to"
- stated: stated
- violation: The array omits a page, repeats one, points at file data, or disagrees with the page numbers stored in the log headers.
- at-risk: G54, G56, and G8 fail because SafeDumpLog asserts that the head's page number matches the caller's index and then replays the wrong blocks.
- detectable: yes — a mismatched page number raises RCVR_ASSERT, and a missing map at init returns EPI_E_BADLOGBLOCKS.
- silent: 1 — newaggr builds this array once, and a corrupt superblock that still names a plausible list is rare and usually fails the assert.
- basis: source

### E15
- contract: The operator gives the aggregate a log at least as large as the minimum for its workload, and leaves that container's size and block list fixed while the aggregate exists.
- source: §"Data Architecture" "The log container does not grow or shrink"
- stated: implicit
- violation: newaggr creates a log smaller than elbl_MinLogSize, or an administrator grows, shrinks, or relocates the log container under a live aggregate.
- at-risk: G17 and G28 fail because elbl_InitLog returns LOG_LOGFULL, or a resized log moves the blocks whose pass numbers recovery uses to find the head.
- detectable: yes — an undersized log is rejected at init; a resized live log is not checked again and shows up later as a bad pass or a failed recovery.
- silent: 2 — the creation check is visible, while an offline rewrite of the log container is an occasional administrative mistake and is silent until the next crash.
- basis: text

### E16
- contract: Each higher-level transaction stays within the reservation the log assumed for it, initially 70K and five log blocks, or within the log after that reservation has grown.
- source: logbuf/log.c:481 " * this is presumtive, not declarative; it reflects our understanding of"
- stated: stated
- violation: A vnode or anode operation logs more than the reserved size in one transaction, and the log cannot grow the reservation without overrunning the container.
- at-risk: G17 fails, and a transaction larger than the log panics in elbl_CompleteTran or in the log-full path, so G2's commit never finishes.
- detectable: yes — the log prints that it is raising the reservation, and it asserts if the new size cannot fit.
- silent: 1 — an oversized transaction prints or panics, and the paper treats that case as a programming error rather than a normal year of operation.
- basis: source

### E17
- contract: A caller that starts a nested undo-zero transaction while the log is full keeps that transaction, plus the transaction it nests under, inside the maximum size of one transaction.
- source: logbuf/log.c:1673 "       * space in the log.  The caller is guaranteeing that the new"
- stated: stated
- violation: The VM or the buffer package nests an undo-zero whose combined size exceeds one transaction reservation, and the force path skips the free-space check.
- at-risk: G17 and G27 fail because the nested start is allowed to proceed and can wrap the log that G20 still needs for undo.
- detectable: partly — a later log-full panic names data or tran overflow; the nested start itself returns success.
- silent: 2 — ordinary undo-zero records are a few bytes, and a nested overflow would be an occasional bug rather than steady operation.
- basis: source

### E18
- contract: The aggregate's block size is a power of two of at least 1K, equals the async device block size, and the fragment size is a power of two from 1K up to that block size.
- source: logbuf/log.c:863 "      afsl_MBZ(blkSize & 1023); /* must be power-of-two >= 1K */"
- stated: stated
- violation: The superblock names a block size the device was not opened with, or a fragment size below 1K or not a power of two.
- at-risk: G4 and G54 fail because log records, page checksums, and byte offsets are computed in the wrong block units and recovery patches the wrong range.
- detectable: yes — AGGREGATE_HDR_OK rejects a mismatched superblock, and the log asserts on a bad block size at reservation time.
- silent: 1 — a mount of a mismatched superblock fails the header check, so the operator sees the refusal.
- basis: source

### E19
- contract: The log device and the data device experience the same crashes and the same durability, so a completed write on one is still present when recovery runs on the other.
- source: §"Data Architecture" "be on the same aggregate as the data that it is logging, but this restriction is currently imposed by our"
- stated: implicit
- violation: The log sits on a disk that loses power or fails independently of the data disk, or the operator recovers only one of the two devices.
- at-risk: G7 and G21 fail when the log disk loses committed records whose metadata never reached the data disk, and G6 fails when the data disk is restored from a copy that is newer than the log.
- detectable: no — InitLog accepts two device pointers, and nothing checks that they failed together.
- silent: 1 — the initialization utilities put the log on the same aggregate, so a split deployment is rare in a system run as the paper describes.
- basis: text

### E20
- contract: The checksum version stored in the log is one this recovery code implements.
- source: logbuf/recover.c:2578 "	    /* Unknown checksum type recorded on disk. Force success of"
- stated: stated
- violation: A newer or older creator writes a checksum version the running salvager does not know.
- at-risk: G54 fails open: an unknown version forces the checksum check to succeed, so a torn or corrupt page is replayed.
- detectable: partly — recovery prints that it is ignoring the checksum, and then continues.
- silent: 1 — matching kernel and salvager binaries are the normal deployment, and a mismatch is rare over a year.
- basis: source

### E21
- contract: Before the kernel uses a dirty aggregate, the operator runs user-space recovery to a clean restart and does not mount the aggregate in between.
- source: logbuf/recover.c:2374 "      return RCVR_MUSTRCVR; /* no kernel recovery anymore */"
- stated: stated
- violation: The operator mounts a crashed aggregate without epilog or salvage, or mounts it while a user-space recovery is still writing the restart block.
- at-risk: G57, G58, and G8 fail because the kernel refuses to replay and, if the caller ignored the error and wrote anyway, new log records would be appended to an unrepaired log.
- detectable: yes — log initialization calls recovery, the kernel returns RCVR_MUSTRCVR, and epig_InitAggregate returns that failure.
- silent: 1 — a mount of a dirty log fails visibly on the kernel path the source actually ships.
- basis: source

### E22
- contract: When recovery or a metadata I/O hits a hard error, a bad log page, RCVR_USERDATA, or RCVR_METADATA, the operator runs the salvager and leaves the aggregate unmounted.
- source: §"Component Architecture" "critical meta-data. In such cases, the Episode salvager utility needs to be run; the salvager's performance"
- stated: stated
- violation: The operator forces the aggregate online, or ignores a panic, after a checksum failure outside the in-transit window or a kill-record conflict.
- at-risk: G1 and G8 fail because the log has already refused to finish replay, and further writes make the on-disk metadata diverge from any later salvage.
- detectable: yes — recovery raises RCVR_IOERR, RCVR_USERDATA, or RCVR_METADATA, and a metadata EIO panics with a printed block number.
- silent: 1 — these failures print or panic, so they are not silent when they happen.
- basis: text

### E23
- contract: Only one Episode instance writes an aggregate at a time, user-space recovery runs single-threaded, and higher layers have stopped other threads before shutdown.
- source: logbuf/tran.c:553 "       * levels have properly synchronized access to this aggregate."
- stated: stated
- violation: Two hosts mount the same disk, salvage runs against a mounted aggregate, or shutdown races with a thread still in elbb_StartTran.
- at-risk: G1, G2, and G39 fail because two logs, or a log and a salvager, write the same home blocks and the clean restart no longer describes a single history.
- detectable: partly — a second log map in one process returns LOG_LOGEXISTS; a second host is invisible.
- silent: 1 — the paper's system is a single server per aggregate, and a dual mount over a year is an unusual operational mistake.
- basis: source

### E24
- contract: The operator leaves removable media in place until the last aggregate close has returned, and no other agent reads or writes it during that close.
- source: anode/aggregate.c:1716 " *     this means that if the disk is on removable media it could be safely"
- stated: stated
- violation: The operator ejects the disk, or a raw copy starts, after the unmount call begins and before the restart block write finishes.
- at-risk: G39 and G56 fail because the clean restart never becomes durable, so the next attach either replays a torn close or treats a partial restart as clean.
- detectable: partly — a failed restart write returns RCVR_FAILED from the restart writer; an eject after a false completion is the E2 case.
- silent: 1 — unloading during the close window is rare in ordinary server operation.
- basis: source

### E25
- contract: The caller of elbb_LogInit has no dirty buffers for that device.
- source: logbuf/buffer.c:1839 "	       * buffers were dirty when elbb_LogInit was called."
- stated: stated
- violation: Log initialization recovers the log and then elbb_Shutdown writes dirty cached metadata back over the repaired blocks.
- at-risk: G60 and G1 fail because the post-recovery invalidation assumes those buffers were clean, and a dirty write restores the pre-recovery image.
- detectable: no — the comment records the assumption, and the shutdown path will write a dirty buffer.
- silent: 1 — mount initializes the log before file operations dirty the pool, so a dirty pool at LogInit is a rare call-order bug.
- basis: source

### E26
- contract: A deployment that relies on crash consistency initializes the aggregate with logging turned on.
- source: anode/aggregate.c:1418 " *     logged -- whether to turn on logging.  Usually true, only false for some"
- stated: stated
- violation: A mount or test harness calls epig_InitAggregate with logged false on an aggregate that users expect to survive a crash.
- at-risk: G1 and G4 fail because metadata updates are not logged, and recovery has nothing to replay.
- detectable: no — the flag is a legal argument, and the file system still serves reads and writes.
- silent: 1 — the kernel mount path passes logged true, and the false setting is described as a debug and test option.
- basis: source

### E27
- contract: Every update to directories, allocation bitmaps, indirect blocks, and anode tables is made through a logged buffer transaction that records the old and new bytes.
- source: §"Component Architecture" "made to any le system meta-data, both the original and new values of the updated data. Furthermore,"
- stated: stated
- violation: A higher layer writes a metadata block through the raw device or through an unlogged buffer, or it modifies the bytes in place without elbb_Modify.
- at-risk: G1, G4, and G6 fail because recovery never sees the update and cannot undo or redo it.
- detectable: no — the log records only what callers submit, and an unlogged metadata write looks like ordinary user data.
- silent: 1 — the anode and vnode paths in this tree use logged buffers for those structures, and a bypass would be a rare code fault.
- basis: text

### E28
- contract: Every modification of a buffer that is being logged is itself logged, and a buffer that is not logged is never given a log record.
- source: logbuf/buffer.c:1442 "      /* Require that updates to logged buffers are either always logged or"
- stated: stated
- violation: A caller passes logRequest false for a dirty logged buffer, or logRequest true for an unlogged user-data buffer.
- at-risk: G4 and G42 fail on the first case, so a later crash restores or keeps bytes the transaction changed without a record; the second case logs user data into the metadata recovery stream and can trip G52.
- detectable: no — the assert that would catch this is compiled out under #if 0.
- silent: 2 — the shipped callers pass the flag consistently, but a mistaken call is silent and the check cannot fire.
- basis: source

### E29
- contract: The bitmap's logged-or-unlogged mark, the anode's logged flag, and the buffer type agree, and a block that changes from one class to the other is killed or undo-zeroed first.
- source: §"Data Architecture" "tion is necessary because certain bu er pool operations have to be performed when reusing a logged block"
- stated: stated
- violation: A metadata fragment is allocated as elbb_bufData, or a freed logged block is reused as user data while a dirty logged buffer is still cached.
- at-risk: G1 and G16 fail because the update is omitted from the log, or a kill record never covers the old metadata and recovery mixes the two lives of the block.
- detectable: partly — salvage reports DIRNOTLOGGED and FILELOGGED when it walks the aggregate; the running log does not check the bitmap bit against the buffer type.
- silent: 2 — the allocator maintains the bit, and a mismatch is an occasional bug that salvage sees only when someone runs it.
- basis: text

### E30
- contract: Higher layers put in one equivalence class every set of still-active transactions on the same log that lock the same object, and they pass an active transaction as the second argument of the merge.
- source: §"Logging Architecture" "same object during their lifetime are merged into an equivalence class (EC). An EC has the property that"
- stated: stated
- violation: Two transactions update or read-and-update the same metadata under different tlocks, or a caller merges a transaction from another aggregate or one that has already ended.
- at-risk: G13, G14, and G1 fail in the way the paper's figure shows: one transaction commits a shared object and a crash undoes the other transaction's update to a related object.
- detectable: partly — a cross-log or inactive second transaction trips an assert in elbt_ECMerge; a missed merge of two live transactions returns success.
- silent: 2 — the tlock macros merge on the locks they cover, and a missed lock on a cold path is an occasional bug that shows up only after a crash.
- basis: text

### E31
- contract: The caller that starts a transaction ends it, and a thread holds at most one unnested transaction at a time.
- source: anode/block_alloc.c:1141 "     * CAUTIONS -- This violates the basic rule that a single thread will not"
- stated: stated
- violation: A vnode path returns without elbt_EndTran, or one thread starts a second unnested transaction while the first is still active.
- at-risk: G17 and G20 fail because the abandoned transaction pins the log tail until the log-full path panics, and a second unnested transaction can deadlock the thread that would have ended the first.
- detectable: partly — log-full handling eventually panics with a printed reason; a deadlock waits with no error return.
- silent: 2 — the anode layer pairs start and end, and a leaked transaction is an occasional bug that the operator sees as a hung or panicked server.
- basis: source

### E32
- contract: Callers keep each equivalence class small enough that every pending member's end-record reservation fits in the log.
- source: logbuf/log.c:138 " *     length(aTranList) * (nested ? undoSize : fullSize) +"
- stated: implicit
- violation: A hot lock merges tens or hundreds of transactions into one class, and each ended member stays pending, holding an end reservation, until the last member ends.
- at-risk: G17 and G14 fail because the pending class fills the log, and a crash then aborts the whole class, including transactions that had already ended in memory.
- detectable: partly — the log-full path panics when the active region reaches the container; it does not report the class size as the cause.
- silent: 2 — the paper tells callers to keep classes short, and a large class under a hot directory is an occasional load spike rather than every-day operation.
- basis: source

### E33
- contract: A caller that will hold several buffers at once reserves that many first, and the operator configures a buffer pool large enough for those reservations.
- source: logbuf/buffer.c:2306 "	      afsl_PAssert(code, ("Insufficient space for buffer reservation"));"
- stated: stated
- violation: An anode path locks two blocks without elbb_Reserve, or the pool is smaller than the reservation the caller then requests.
- at-risk: G22 and G15 fail because the threads deadlock or panic while holding the dirty buffers checkpoint needs to write, so the active log cannot shrink and fsync cannot finish.
- detectable: yes — an impossible reservation panics with the insufficient-space assert; a lock-order deadlock hangs.
- silent: 1 — the panic is visible, and the shipped metadata paths reserve before the double-block operations.
- basis: source

### E34
- contract: Callers log a new block with elbb_Initialize or CreateBlock, and they log an existing metadata block with the old bytes included.
- source: logbuf/buffer.c:1588 " * By initialization, we mean modification in the case where the old data"
- stated: stated
- violation: A caller uses a full old-and-new record on a CreateBlock buffer, or uses Initialize on a block that already holds live metadata.
- at-risk: G6 and G43 fail because undo writes back uninitialized old bytes, or redo has no old image for a block that recovery must restore.
- detectable: no — both calls are legal, and recovery applies whichever image was logged.
- silent: 1 — the anode paths choose CreateBlock for new pages and Modify for existing ones, so a swapped call is a rare coding fault.
- basis: source

### E35
- contract: A caller passes metadataOK to elbb_Kill only after the transaction that freed that metadata block has committed.
- source: logbuf/buffer.c:1360 " *     buffers.  This will only be true if the transaction that freed the"
- stated: stated
- violation: The allocator kills a dirty logged buffer while the freeing transaction is still uncommitted, and the buffer's updates disappear from memory.
- at-risk: G44 and G6 fail because recovery may still undo other records on that block while the killed dirty image has already been discarded, and a reuse can then proceed without the committed free.
- detectable: partly — elbb_Kill returns BUF_CANTDELETE when metadataOK is false and the buffer is dirty; a true flag on an uncommitted free is accepted.
- silent: 1 — fb_CheckTrans kills only after elbb_TranIsCommitted, so a premature kill is a rare caller bug.
- basis: source

### E36
- contract: The allocator does not hand a freed block out again until the freeing transaction has committed, and a committed zero-fill kill record is the newest record that may precede the block's next use.
- source: anode/block_alloc.c:565 " *     return.  Recently freed blocks are not okay if the transaction in which"
- stated: stated
- violation: A newly allocated metadata or user block receives records while an older uncommitted update or an uncommitted zero-fill is still in the active log for that address.
- at-risk: G51, G52, and G53 fail: recovery raises RCVR_USERDATA or RCVR_METADATA and stops, leaving the aggregate dirty.
- detectable: yes — the next recovery raises one of those two codes when the kill order is wrong.
- silent: 1 — the freed-block list withholds the block until commit, and the violation is reported at recovery rather than ignored.
- basis: source

### E37
- contract: The layer that allocates a user-data block records an undo-zero for that byte range and ends that transaction only after the first write of the new data has completed, including when the virtual memory system writes the block outside the buffer pool.
- source: logbuf/buffer.c:2415 " * the specified range of bytes.  This is to be used by the VM system for I/Os"
- stated: stated
- violation: A pageout or a strategy write stores a newly allocated block without an undo-zero record, or it ends the undo-zero transaction before that write is durable.
- at-risk: G16 fails because a crash that aborts the allocation leaves the previous contents readable in the new file.
- detectable: no — elbb_UndoZero has no caller in this tree, and epia_Iodone does not update an undo-zero database.
- silent: 4 — buffered writes attach an undo-zero, but the AIX VM path the paper relies on writes file data from the virtual memory system, and that iodone path states that undo-zero handling is not implemented, with no error returned.
- basis: source

### E38
- contract: The caller of elbb_UndoZeroBuffer has finished writing the new bytes into the dirty buffer before the call, and the range lies inside that buffer.
- source: logbuf/buffer.c:2459 " *     present.  All updates to the dirty buffer have been done when this call"
- stated: stated
- violation: The caller attaches the undo-zero and then keeps modifying the buffer, or the log cleans the buffer and ends the nested transaction before the new bytes are stored.
- at-risk: G16 and G46 fail because recovery zeroes a block whose new data never became durable, or it keeps a block whose allocation aborted after a partial store.
- detectable: no — the call returns after logging the fill, and it does not check that the caller has stopped writing.
- silent: 1 — the anode write path attaches the record in ReleaseBuf after the copy, which matches the comment, so a reversed order is a rare bug.
- basis: source

### E39
- contract: After a modify, fill, or initialize, the caller uses the buffer pointer the call returns.
- source: logbuf/buffer.c:1415 " * cannot assume the buffer handle will not change across this call."
- stated: stated
- violation: The caller keeps logging or releasing the pointer it passed in after the package has moved the block to a different buffer header.
- at-risk: G42 and G5 fail because the log record is attached to one buffer and the caller writes or forces another, so the home block and the log disagree.
- detectable: no — the old pointer can still address a live header for a different block.
- silent: 1 — the anode macros thread the returned pointer, and holding the old one is a rare bug.
- basis: source

### E40
- contract: An fsync or any other call that promises durable metadata writes the file's dirty VM pages, then forces the log through that file's transaction before it returns.
- source: vnops/efs_vnodeops.c:1755 "	/* Flush all buffers associated with the vnode and make sure metadata"
- stated: stated
- violation: The vnode returns from fsync without vnvm_fsync, without epia_Fsync, or without elbb_LogForce of the vnode transaction, or the caller holds the vnode lock across the VM flush and the flush waits for that lock.
- at-risk: G15, G23, and G40 fail because the operation returns while the log end record or the user pages are still only in memory.
- detectable: no — a skipped force still returns success to the caller.
- silent: 2 — efs_fsync does call both steps, while the Sun VM hook is a stub on platforms where vnvm_fsync is compiled to return zero, so durability of user pages is silently skipped there.
- basis: source

### E41
- contract: The operating system calls the file system's sync often enough that committed dirty metadata is written and the active log is checkpointed about every T seconds.
- source: §"Recovery Time" "every T seconds, as is the case with Episode, then the active portion of the log can rise to include all the"
- stated: implicit
- violation: The update daemon is disabled, or efs_sync always finds its lock busy and never reaches elbb_SyncForce.
- at-risk: G9, G10, G21, and G22 weaken because the active log keeps every committed update whose buffer is still dirty, until log-full handling finally writes buffers.
- detectable: no — skipping sync returns without an error, and the log simply stays long.
- silent: 2 — the paper's kernels run a periodic sync, and turning it off is an occasional administrative change that produces no immediate error.
- basis: text

### E42
- contract: A caller that needs a durable point for the outside world asks quiesce to commit, and any tool that reads the raw device does so only after that commit and the matching buffer flush.
- source: logbuf/tran.c:1210 " *     the outside world, like vol_fsync.  A third variant allows commit of"
- stated: stated
- violation: A fileset export, move, or raw backup reads disk blocks while dirty logged buffers or uncommitted log records still exist, or it asks only for SERIALIZE when it needed COMMIT.
- at-risk: G18 and G1 fail for that reader because old-and-new logging is allowed to write uncommitted metadata, so the raw image is not a consistent file system until recovery or a committing quiesce.
- detectable: no — quiesce returns once the requested level is reached, and a raw read has no log check.
- silent: 2 — administrative copies of a live aggregate are occasional, and nothing reports that the raw image still needs the log.
- basis: source

### E43
- contract: Callers of elbb_Tune and elbl_Tune pass a pointer in the log package's address space.
- source: logbuf/buffer.c:873 " * Note that elbb_Tune assumes the address of value is in its address"
- stated: stated
- violation: A system call passes a raw user pointer and the log stores a limit through it.
- at-risk: Unsure which of G17's limits would change. A wild store can corrupt the caller, and a truncated write can leave max-tran or log-full thresholds wrong so admission no longer matches the log.
- detectable: partly — a bad kernel pointer faults; a user pointer that happens to be mapped is written with no error.
- silent: 1 — tune is an in-kernel control, and the paper's file-system calls do not pass user pointers here.
- basis: source

### E44
- contract: The fast metadata modify path receives kernel addresses, and any user-address modify copies exactly the requested bytes or returns an error.
- source: logbuf/buffer.c:1703 "       * assume along this code path that we never have user data (e.g. we"
- stated: stated
- violation: A caller passes a user pointer to the fast path, or osi_copyin reports success after copying a different range.
- at-risk: G4 and G42 fail because the logged new value is not the value the caller meant to store, and recovery will redo that wrong value.
- detectable: partly — a user pointer on the fast path can fault; a short copyin that still returns zero is silent.
- silent: 1 — directory and anode updates use kernel buffers, and a bad copyin on these hosts is rare.
- basis: source

### E45
- contract: A higher layer holds the container lock across an anode metadata operation so two transactions do not update that container together.
- source: anode/anode.c:2175 " * LOCKS USED -- The container is assumed to be locked by a higher level to"
- stated: stated
- violation: Two threads call epia_Write on the same anode without the vnode or container lock.
- at-risk: G2 and G19 fail because the two transactions interleave byte updates inside one block and the log's per-transaction images no longer describe a serial order.
- detectable: no — the anode layer does not take that lock itself.
- silent: 1 — the vnode operations take the tlock before they call the anode layer, so an unlocked call is a rare bug.
- basis: source

### E46
- contract: One async_device object names an aggregate for the life of its buffer cache, and the compiler lays the device pointer and the block number out as one contiguous hash key with the device pointer first.
- source: logbuf/buffer.c:839 "       * note that for this key to work, we assume that the device and"
- stated: stated
- violation: A second device object is opened for the same disk, or a compiler inserts padding between adev and blockNum, so two cache entries alias or one block is looked up under the wrong key.
- at-risk: G5 and G1 fail because the log is forced for a different buffer than the one written, or a stale cached block is treated as the current metadata.
- detectable: no — the hash init succeeds either way, and there is no check that the key bytes are exactly those two fields.
- silent: 1 — one device object per mount is how the aggregate layer works, and the ABIs of the paper's compilers keep those two fields adjacent.
- basis: source

### E47
- contract: The scheduler and the VM I/O daemon keep running the threads that end transactions, finish undo-zero I/O, and write dirty buffers while other threads wait for log space.
- source: logbuf/tran.c:1239 " *     from the VM system which has its own Async daemon to complete I/O.  We"
- stated: stated
- violation: A high-priority thread spins waiting for a transaction while it holds the buffer or vnode lock the transaction needs, or the VM daemon that would end an undo-zero never runs.
- at-risk: G17, G28, and G32 fail because log-full handling and quiesce wait forever and no commit or checkpoint completes.
- detectable: no — the wait is a sleep, and the log returns no error.
- silent: 2 — priority inversions on these kernels show up under occasional heavy metadata load, as a hung server with no logged I/O error.
- basis: source

### E48
- contract: Block addresses passed into the log and into recovery name blocks the device can read and write.
- source: logbuf/recover.c:1319 "      if (returnVal != 0) panic("ReadData: bad read");"
- stated: implicit
- violation: A caller or a damaged log record names a block past the end of the device or on a hole the driver rejects.
- at-risk: G8 fails because recovery panics on the read and never writes the clean restart, and a metadata write during normal operation hits the same address.
- detectable: yes — readData and writeData panic, and the async path surfaces an I/O error.
- silent: 1 — legal allocators hand out in-range blocks, and an out-of-range address panics rather than succeeding quietly.
- basis: source

## Recognised

- E2 is the contract behind volatile disk write caches that report completion before the media is stable. I recall that failure mode from write-ahead logging practice of this era, including DFS and Episode deployments that enabled SCSI write caching without a battery.
- E37 is the contract behind Episode new-block security. The logbuf locking history in this tree names it as OT 3804 and OT 1020, and anode/strategy.c still says the iodone undo-zero database is not implemented.
- I recognise the pass-number comparison work named as OT 5527 in that same history as an internal log bug, so I did not make a separate environment contract for it.

## Report

48 contracts.

Defects in logbuf's own rules, kept out of the list:

- An unknown checksum version is treated as valid and the page is accepted. That weakens G54 instead of failing recovery.
- elbr_Recover panics when SafeDumpLog returns an error, despite the comment that recovery should return an error rather than panic.
- NewLogPage ignores the return value of asevent_QueueIO and still marks the log page in transit.
- During a kernel panic, elbb_SyncForce returns immediately when the buffer lock or the log lock is held, and elbb_StartTran gives up after three loops. That narrows G41 and G28 on the panic path.
- Restart pages are written without a checksum. The crash window is handled by the checkpoint-then-restart sequence, which still depends on E3.

Could not decide:

- Whether a 16-bit pass-number wrap is its own obligation on log traffic. Each pass overwrites every log page, so a collision with an older pass also requires a lost write, which is E2. I left it out.
- Whether GetCleanLogInfo's inspection of block 0 alone is safe when log writes complete out of order. It looks safe if E2 holds and a force waits for every earlier in-transit page, but I did not follow every commit path far enough to be certain.
- Whether the "undo-zero not yet implemented" comment in epia_Iodone is stale after the OT 3804 work. elbb_UndoZero has no caller in this tree, so I treated the VM gap as real and scored E37 accordingly.
- The silent score for E2. I do not know the write-cache default on the paper's Seagate ST1239NS and IBM 0661, so 3 is a judgment from the period rather than a measurement.

`ls -R` of the checkout, with `source/episode/` pruned:

```
.:
AGENTS.md
BRIEF.md
GUARANTEES.md
enumeration.md
source

./source:
episode
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
