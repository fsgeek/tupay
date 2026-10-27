# Brief: merge four lists of environment contracts (D2 phase 1)

Below are four lists, written independently from two sources (the paper *The Episode File System*, USENIX Winter 1992, and Episode's source in OSF DCE 1.2.2), of the **environment contracts** Episode's log and recovery (`logbuf`) rely on: obligations on things outside `logbuf` (anything it calls, that calls it, or that it runs on, including an operator). Each entry has an id `<list>:E<n>`. Different lists often state the same obligation in different words, or split one obligation into several finer ones.

Your task: group entries that state **the same obligation on the same depended-on service**. Two entries belong in one group only if a deployment that violates one necessarily violates the other. An entry that is broader than another may appear in more than one group (once with each finer entry it covers). An entry that matches nothing need not be listed.

Use only the text below. Do not use any tool. Reply with JSON only, in exactly this shape, and nothing else:

{"groups": [["codex-1:E3", "grok-2:E7"], ["codex-2:E1", "grok-1:E4", "grok-2:E2"]]}

Every id you write must appear in the lists below. Groups have at least two ids.

---
### codex-1:E1
- contract: The storage stack must make a successfully completed log write durable across the crashes against which recovery is promised.
- source: logbuf/recover.c:894 "underlying system to really guarantee that a page is on disk"
- violation: A controller acknowledges a log write while its only copy is in volatile cache, then power fails.

### codex-1:E2
- contract: The disk must write each sector atomically and correctly across a crash.
- source: logbuf/recover.c:746 "correctness/atomicity of each sector. So if the log page did"
- violation: A power interruption leaves a sector containing a mixture of its old and new contents.

### codex-1:E3
- contract: The storage stack must preserve completed writes until an explicitly authorized overwrite.
- source: logbuf/recover.c:755 "active log pages outside the in-transit window are really"
- violation: A completed active log page later develops an unreadable sector or silently loses bits.

### codex-1:E4
- contract: The storage stack must return the requested bytes and report failed or short I/O as an error.
- source: async/asevent.c:1126 "if (bp->b_flags & B_ERROR) {"
- violation: A driver returns success with a short transfer, wrong-sector read, or failed write while leaving B_ERROR clear.

### codex-1:E5
- contract: The device must confine each write to its addressed sectors and preserve unrelated bytes.
- source: logbuf/recover.c:1343 "writeBlock(&buf, returnVal);"
- violation: A firmware or DMA error writes a log page over a different metadata block.

### codex-1:E6
- contract: The asynchronous I/O service must eventually complete each accepted request and signal its event with the correct result.
- source: logbuf/log.c:786 "retval = asevent_WaitEvent(ae);"
- violation: An accepted disk write never invokes iodone, or signals the wrong event.

### codex-1:E7
- contract: The OS synchronization service must provide mutual exclusion and memory visibility for the logbuf locks.
- source: logbuf/buffer.c:750 "epi_mutex_init(&bufferLock, "buffer");"
- violation: An unsupported port implements a mutex without the required interprocessor memory ordering.

### codex-1:E8
- contract: The OS sleep and wakeup primitives must atomically release the appropriate lock and avoid lost wakeups.
- source: logbuf/tran.c:1200 "elbt_TranUnlockAndSleep(tP,tP);"
- violation: A wakeup races with a non-atomic unlock-and-sleep operation and a forcing thread sleeps indefinitely.

### codex-1:E9
- contract: The execution environment must eventually schedule threads and I/O workers needed to end transactions and write buffers.
- source: logbuf/tran.c:1239 "from the VM system which has its own Async daemon to complete I/O. We"
- violation: The VM write daemon is disabled or starved while commit waits for its undo-zero transaction.

### codex-1:E10
- contract: The memory service must supply enough allocation capacity for the active log and recovery bookkeeping.
- source: logbuf/recover.c:1031 "TODO: is this a safe assumption ---"
- violation: Recovery on a memory-constrained host cannot allocate all active log pages and record structures.

### codex-1:E11
- contract: The OS pinning and DMA services must keep I/O memory resident and mapped to the supplied bytes until completion.
- source: logbuf/recover.c:1364 "logbuf_pin(data, dev->blkSize);"
- violation: A port treats pinning as a no-op where DMA requires pinned memory and a page is reclaimed during I/O.

### codex-1:E12
- contract: The CPU and compiler must make the shared 32-bit tuning assignments atomic to readers.
- source: logbuf/log.c:2602 "a 32 bit quantity is atomic w.r.t. all readers."
- violation: A port implements a shared tuning store as two separately observable halfword stores.

### codex-1:E13
- contract: A port must preserve the alignment, integer widths, byte order, and structure layout expected by the native on-disk log format.
- source: logbuf/logrec.h:227 "pointers rather than bcopy (remember we want things to be fast.)"
- violation: An aggregate is recovered using a build with a different endian order or daddr_t layout and no format conversion.

### codex-1:E14
- contract: A port must ensure that pointer alignment calculations do not truncate addresses and that cast log records meet CPU alignment requirements.
- source: logbuf/logrec.h:232 "a power-of-two. The use of (unsigned) may not be strictly correct"
- violation: The code is built with 64-bit pointers and 32-bit unsigned, and ALIGN discards the upper address bits.

### codex-1:E15
- contract: A port must preserve the contiguous device-pointer and block-number layout used as the buffer address hash key.
- source: logbuf/buffer.c:840 "block # fields are contiguous, with the device *first*. We"
- violation: A compiler inserts padding between adev and blockNum so the fixed-length key omits part of the block number.

### codex-1:E16
- contract: Device registration must supply a supported power-of-two block size and an accurate matching logBlkSize.
- source: logbuf/log.c:863 "afsl_MBZ(blkSize & 1023); /* must be power-of-two >= 1K */"
- violation: A registered device advertises 3072-byte blocks or a logBlkSize inconsistent with blkSize.

### codex-1:E17
- contract: Device registration must keep block sizes within the buffer and record-offset limits supported by this build.
- source: logbuf/logbuf.p.h:416 "#define BUF_MAXBUFSIZE (64 * BUF_MINBLKSIZE) /* largest buffer size */"
- violation: An operator or port registers blocks larger than the buffer maximum or representable record offsets.

### codex-1:E18
- contract: The device layer must preserve a stable unique device identity and physical block mapping for the lifetime of cached buffers and transactions.
- source: logbuf/buffer.c:845 "sizeof(async_device_t *) +"
- violation: A device object is recycled for a different partition while old cache entries still use its pointer.

### codex-1:E19
- contract: Aggregate setup must supply the complete log-block array in its original circular order and associate it with the correct data device.
- source: logbuf/recover.c:983 "/* guarantee the caller described the log properly */"
- violation: Recovery receives a reordered block list, a truncated list, or another aggregate’s data device.

### codex-1:E20
- contract: The allocator and administrator must reserve log blocks exclusively and keep their addresses and log length fixed during normal logging.
- source: §"Data Architecture" "The log container does not grow or shrink"
- violation: A live resize, relocation, or overlapping allocation lets file data overwrite active log pages.

### codex-1:E21
- contract: Aggregate creation must allocate at least the minimum log space required for its block size and intended admitted workload.
- source: logbuf/log.c:848 "minSize = (load * elbl_MinTranReservation(dP->blkSize)) +"
- violation: An administrator constructs an undersized log or chooses a minimum supporting too little concurrent work.

### codex-1:E22
- contract: Initialization callers must serialize first-time package initialization before concurrent use.
- source: logbuf/tran.c:177 "Locks: assumes no locking (single-threaded at init time). Call is"
- violation: Two mount threads enter first-time transaction initialization concurrently.

### codex-1:E23
- contract: Log-creation callers must exclude all other activity on that device while creating its log.
- source: logbuf/log.c:878 "Locking: This code presumes no other thread is calling for this"
- violation: A formatting utility creates the log while the filesystem still has active users.

### codex-1:E24
- contract: Log-creation callers must enter without holding buffer-package locks that creation needs.
- source: logbuf/log.c:880 "I/O, it presumes locks are not held in the buffer package."
- violation: A caller creates a log while retaining the buffer lock needed by CreateBlock.

### codex-1:E25
- contract: Mount and recovery orchestration must run user-space recovery for a dirty log before allowing ordinary filesystem access.
- source: logbuf/recover.c:2374 "return RCVR_MUSTRCVR; /* no kernel recovery anymore */"
- violation: A mount path ignores RCVR_MUSTRCVR and serves a dirty aggregate.

### codex-1:E26
- contract: Recovery orchestration must exclude concurrent filesystem, VM, raw-device, and administrative writes to the recovered aggregate and log.
- source: logbuf/recover.c:505 "AdjustDisk(diskHash, dP, &allocList, rcvr_env);"
- violation: A mounted filesystem changes a metadata block while user-space recovery reads and rewrites it.

### codex-1:E27
- contract: Callers must present a clean buffer cache when initializing a log that may require recovery.
- source: logbuf/buffer.c:1839 "buffers were dirty when elbb_LogInit was called."
- violation: A caller dirties cached metadata before LogInit, then successful recovery invalidates or writes that cache.

### codex-1:E28
- contract: Callers must handle RCVR_RECOVERED by discarding stale higher-layer state and retrying initialization against recovered disk contents.
- source: logbuf/log.c:737 "return RCVR_RECOVERED; /* so upper levels can clear buffers */"
- violation: The aggregate layer treats RCVR_RECOVERED as ordinary success and retains anodes loaded before recovery.

### codex-1:E29
- contract: Operators must invoke salvage rather than assume successful log recovery when hard errors have destroyed critical metadata or needed history.
- source: §"Component Architecture" "In such cases, the Episode salvager utility needs to be run; the salvager's performance"
- violation: After a failed recovery with unreadable active log pages, an operator forces the aggregate online without salvage.

### codex-1:E30
- contract: Upper filesystem layers must bracket every consistency-relevant metadata change in the appropriate logged transaction.
- source: §"Component Architecture" "By making all le system meta-data modi cations within atomic transactions, the"
- violation: A directory or bitmap update bypasses logging, uses a null transaction, or requests an unlogged modification.

### codex-1:E31
- contract: Upper layers must construct transactions whose committed boundaries preserve filesystem invariants.
- source: §"Logging Architecture" "After each transaction, the le system is consistent, if"
- violation: A large truncate commits a bitmap free before removing the last reachable pointer in another independent transaction.

### codex-1:E32
- contract: Transaction clients must bound each ordinary transaction’s log consumption by the reservation assumed at admission.
- source: logbuf/log.c:1684 "Each running transaction is assumed to need MAX_TRAN_SIZE of log"
- violation: A vnode operation logs an unbounded large truncate in one transaction.

### codex-1:E33
- contract: Transaction clients must end their transactions in bounded time and release resources needed by other admitted transactions.
- source: §"Logging Architecture" "Transactions that run too long or modify too much data represent"
- violation: An error path leaks an active transaction or leaves it blocked forever holding an object lock.

### codex-1:E34
- contract: Nested-transaction callers must keep the new transaction plus its parent within the reservation for a single ordinary transaction.
- source: logbuf/log.c:1674 "transaction size plus old transaction size will be less than the"
- violation: A caller supplies oldTranId to bypass admission and then logs a second full-sized operation.

### codex-1:E35
- contract: Clients must pass live transaction IDs belonging to the intended device and stop adding updates after ending them.
- source: logbuf/log.c:1020 "afsl_Assert (dataLength <= tP->dev->blkSize);"
- violation: A client reuses a stale transaction handle, logs after EndTran, or modifies one device under another device’s transaction.

### codex-1:E36
- contract: Upper layers must use transactional object locking and report every intertransaction read/write dependency that requires equivalence-class merging.
- source: anode/tlock.h:20 "the same lock, they must be put in the same equivalence class. To minimize"
- violation: A transaction reads another’s uncommitted bitmap or anode through a nontransactional lock and commits independently.

### codex-1:E37
- contract: Callers must serialize access to shared metadata objects while their values are read or changed.
- source: anode/tlock.c:99 "lock_ObtainWrite_r (&tlock->lock);"
- violation: Two callers update overlapping anode bytes without holding the object’s write lock.

### codex-1:E38
- contract: Callers merging equivalence classes must provide an active second transaction.
- source: logbuf/tran.c:642 "second tran must be active."
- violation: A caller invokes ECMerge after the current transaction has ended or committed.

### codex-1:E39
- contract: Callers that destroy or recycle transactional lock objects must serialize their remembered transaction before reusing the lock identity.
- source: anode/tlock.c:53 "code = elbb_LogForce(*transP, 2/*complete*/);"
- violation: A remembered transaction ID survives lock destruction and is associated with an unrelated object at the same address.

### codex-1:E40
- contract: Callers waiting for transaction completion must hold no active transaction whose progress can depend on that wait.
- source: logbuf/tran.c:1313 "CAUTIONS -- The calling thread must not be holding any active transactions."
- violation: A thread forces a transaction in its own unfinished equivalence class while retaining an active member.

### codex-1:E41
- contract: Callers must arrange multi-buffer reservations before taking a path that holds several buffers simultaneously.
- source: logbuf/buffer.c:2194 " buffers simultaneously; this avoids deadlock."
- violation: Many threads each retain one buffer and wait for a second without reserving enough pool space.

### codex-1:E42
- contract: Shutdown callers must stop new aggregate activity and synchronize access before closing the log.
- source: logbuf/tran.c:553 "levels have properly synchronized access to this aggregate."
- violation: A close races with a new StartTran or VM dirtying after shutdown has sampled active work.

### codex-1:E43
- contract: Clients must request the persistence level they require and distinguish transaction completion from durable commitment.
- source: logbuf/tran.c:953 "2 -- don't return until transaction has completed. This ensures"
- violation: An fsync caller uses waitOK=2 or treats EndTran as proof that its end record reached disk.

### codex-1:E44
- contract: Clients must choose a write-back mode that waits for data completion when they promise synchronous persistence.
- source: logbuf/logbuf.p.h:64 "elbb_syncLog, /* force write log, schedule buffer write, don't wait"
- violation: An upper layer returns synchronous success after elbb_syncLog or elbb_async while data is still in transit.

### codex-1:E45
- contract: Fsync clients must tag every relevant cached buffer with the correct file handle or provide the complete correct block list.
- source: logbuf/buffer.c:2019 "buffers to write out. Either a magic value is used to tag each"
- violation: A metadata or data buffer is omitted from the file’s tag chain or explicit block list.

### codex-1:E46
- contract: VM integration must flush its own dirty pages as part of a filesystem-level synchronization promise.
- source: logbuf/logbuf.p.h:335 "WRITE -- schedules all dirty buffers containing user data."
- violation: An fsync implementation flushes only logbuf buffers while dirty mapped file pages remain solely in VM.

### codex-1:E47
- contract: Clients must retain valid buffer references, obey write access requirements, and release every acquired reference.
- source: logbuf/buffer.c:1432 "afsl_Assert(bufferIsWrite(bP) && (bP->refCount > 0));"
- violation: A caller modifies an unreferenced buffer after recycling, or leaks held references until the pool cannot reclaim space.

### codex-1:E48
- contract: Modification callers must use the returned replacement buffer handle after operations that can replace the original.
- source: logbuf/buffer.c:1415 "cannot assume the buffer handle will not change across this call."
- violation: A client ignores nbP and continues modifying or releasing the previous buffer after log-full handling replaces it.

### codex-1:E49
- contract: Callers must keep modification byte ranges within the addressed block and supply accessible data in the declared address space.
- source: logbuf/buffer.c:1474 "retval = osi_copyin_r(newData, bP->data + offset, newDataLen);"
- violation: A client supplies offset plus length beyond the block, an invalid source pointer, or USER bytes labeled SYS.

### codex-1:E50
- contract: Callers must keep new-data bytes stable across logging and copying them into the destination buffer.
- source: logbuf/buffer.c:1456 "LogWrite(tranId, LOGREC_DATA, newDataLen, offset, bP, newData,"
- violation: A concurrent thread changes newData after LogWrite records it but before LOGCOPY installs it.

### codex-1:E51
- contract: Callers must treat no-read buffer allocation as requiring initialization of every byte they will expose or preserve.
- source: logbuf/buffer.c:970 "(1) Just allocate a buffer (for overwriting an entire disk block."
- violation: CreateBlock is followed by a partial overwrite and the remaining recycled memory is written as file contents.

### codex-1:E52
- contract: Callers may omit old-value logging only for genuinely new storage whose old contents need not be restored after abort.
- source: logbuf/buffer.c:1589 "do not have to be logged, i.e. the buffer was created by CreateBlock."
- violation: Initialize or Fill with saveOld=false is used on reachable preexisting metadata.

### codex-1:E53
- contract: Clients must classify buffers as logged metadata or unlogged data correctly and restrict external requests to public buffer types.
- source: logbuf/logbuf.p.h:47 "users of this package are restricted to the first two cases"
- violation: A metadata block is read as elbb_bufData or an external caller requests internal log/recovery buffer treatment.

### codex-1:E54
- contract: Block allocation must not reuse freed metadata for unlogged data until the freeing transaction and its prior dependencies have committed.
- source: logbuf/buffer.c:1361 "metadata block has committed, which implies that all transactions that"
- violation: A block becomes file data while an earlier metadata transaction on that block can still be undone.

### codex-1:E55
- contract: Block reuse must invalidate or safely write the prior cached incarnation before exposing a new logged or unlogged incarnation.
- source: §"Data Architecture" "tion is necessary because certain bu er pool operations have to be performed when reusing a logged block"
- violation: A freed dirty metadata buffer remains cached while the same physical block is allocated as user data.

### codex-1:E56
- contract: Callers may set metadataOK on Kill only after the transaction freeing that metadata has committed.
- source: logbuf/buffer.c:1359 "PARAMETERS -- metadataOK is true if it is safe to kill dirty metadata"
- violation: An allocator passes metadataOK=1 merely because a free was issued, before that free commits.

### codex-1:E57
- contract: Allocation and VM clients must establish undo-zero coverage for every newly exposed data byte before allocation can leave stale contents visible after a crash.
- source: §"Logging Architecture" "problem by starting another transaction when the block is allocated, and ending it when the rst write"
- violation: A new block or fragment is linked into a file without the special first-write transaction for part of its contents.

### codex-1:E58
- contract: VM clients doing I/O outside the buffer system must provide the correct device, block range, and live transaction to UndoZero.
- source: logbuf/buffer.c:2416 "that do not use the buffer system. It is expected that this would not be"
- violation: The VM reports the wrong offset, omits the last block, or supplies a null transaction for a newly allocated extent.

### codex-1:E59
- contract: VM and allocation clients must end undo-zero transactions only after the covered first write has successfully reached disk.
- source: §"Logging Architecture" "to it completes. If the system crashes and the transaction aborts, the recovery procedure for this special"
- violation: A VM client ends its transaction on write submission or after a failed first write.

### codex-1:E60
- contract: VM integration must drive outstanding first-write I/O and finish its undo-zero transactions independently of log-space waiters.
- source: logbuf/tran.c:1240 "can safely wait for it to end its undo zeros."
- violation: The only VM worker able to finish a first write is blocked trying to start another ordinary transaction on the same full log.

### codex-1:E61
- contract: The VM and higher vnode layers must serialize overlapping block I/O so that waiting for an in-transit block is not invalidated by another writer.
- source: anode/strategy.c:267 "transit again. The higher-level vnode locking should guarantee this."
- violation: A second writer starts I/O to a block after a waiter has passed its in-transit check.

### codex-1:E62
- contract: The VM and vnode layers must ensure the strategy layer’s documented bound on simultaneous waiters for each in-transit block.
- source: anode/strategy.c:271 "multiple I/O requests for a given block, and other writers are"
- violation: Two VM or volume-operation threads wait for the same block where the code expects at most one waiter.

### codex-1:E63
- contract: Clients must not use quiesce’s captured position as proof that later concurrently issued updates have completed.
- source: logbuf/tran.c:1220 "when the caller (elbb_QuiesceSystem) started. Other activity is allowed"
- violation: An administrative operation quiesces and assumes all subsequent writers are also included without excluding them.

### codex-1:E64
- contract: The deployment must provide periodic checkpoint-driving work and sufficient metadata write bandwidth to keep the active log small when relying on fast recovery.
- source: §"Recovery Time" "every T seconds, as is the case with Episode, then the active portion of the log can rise to include all the"
- violation: Background checkpoint activity is disabled or the metadata disk stays saturated while committed dirty buffers accumulate.

### codex-1:E65
- contract: A deployment interpreting the recovery-time comparisons must keep active history, I/O performance, and available recovery resources comparable rather than scaling them with aggregate size.
- source: §"Recovery Time" "Episode's time to recover depends primarily on the size of the active portion of transaction log."
- violation: A larger aggregate is configured with much more active log history or a much slower recovery device.

### codex-1:E66
- contract: Administrators must select a supported effective checksum scheme when relying on torn-page or corruption detection.
- source: logbuf/recover.c:2582 "printf("Log has unknown checksum type on disk. Ignoring checksum check\n");"
- violation: A log uses checksum version NONE or an unknown type and the deployment assumes every torn page will be rejected.

### codex-1:E67
- contract: The failure environment must not alter a protected log page in a way that preserves its checksum and passes its structural checks.
- source: logbuf/recover.c:1039 "if (!ValidLogPageChecksum(logBlocks[index], ldP->blkSize,"
- violation: Corruption changes both payload and checksum consistently, or two payloads collide under the configured CRC.

### codex-1:E68
- contract: The storage and operating environment must preserve a clean restart marker’s authenticity and its ordering after all recovery or shutdown data writes.
- source: logbuf/recover.c:2738 "We choose not to checksum the log page containing a restart record"
- violation: A forged, corrupted, restored, or prematurely durable restart marker survives while recovered metadata writes do not.

### codex-1:E69
- contract: Backup, restore, and raw-device administration must preserve a crash-consistent pairing of the aggregate’s metadata and its retained log history.
- source: logbuf/log.c:734 "code = elbr_Recover(ldP, dP, logLocnArray, logLocnArraySize);"
- violation: An operator restores only the log from an older backup, or independently snapshots log and data devices at incompatible times.

### codex-1:E70
- contract: Initialization callers must supply writable buffer-pool memory of the declared size and keep it owned by logbuf for the package lifetime.
- source: logbuf/buffer.c:731 "caddr_t startAddr = elbbParams->bufferPool;"
- violation: The caller frees or repurposes the pool after Init, or exaggerates byteCount beyond its allocation.

### codex-1:E71
- contract: Tuning callers must pass appropriately typed accessible values in the package address space and copy user arguments before calling.
- source: logbuf/buffer.c:908 "caller must copyin/copyout the version string"
- violation: An ioctl wrapper passes a user pointer directly to a routine expecting a kernel-space value or an undersized destination.

### codex-1:E72
- contract: Callers must check error and would-block returns before reporting successful persistence or using returned buffer contents.
- source: logbuf/tran.c:957 "RETURN CODES -- returns BUF_WOULDBLOCK only if waitOK is zero and the"
- violation: A caller ignores BUF_WOULDBLOCK from a nonwaiting force or returns success after a read/copy/I/O error.

### codex-1:E73
- contract: Clients retaining historical transaction IDs must retire them before ID wrap can make the same numeric ID identify unrelated work.
- source: logbuf/tran.c:1062 "elbt_GlobalTranId++;"
- violation: An old vnode or transactional lock retains a numeric ID across a complete 32-bit allocation cycle and later forces or merges an unrelated transaction.

### codex-1:E74
- contract: Aggregate configuration must keep log length and page indices within the range supported by the on-disk fields and signed-distance arithmetic.
- source: logbuf/log.c:187 "As with pass numbers, log offsets are unsigned int16s. So we have to do"
- violation: A tool allocates a log whose page index truncates in oldestDataPage or whose distance changes sign in int16 arithmetic.

### codex-2:E1
- contract: The storage device must make each log sector write atomic across a crash.
- source: logbuf/recover.c:752 " * correctness/atomicity of each sector. So if the log page did"
- violation: Power loss leaves a sector containing a mixture of old and new header bytes.

### codex-2:E2
- contract: The device must preserve successfully completed log writes through subsequent power loss.
- source: logbuf/recover.c:1302 " returnVal = asevent_WaitEvent(ae);"
- violation: A drive acknowledges writes in an unprotected volatile write cache, then loses them on power failure.

### codex-2:E3
- contract: The device must preserve completed home-block writes until a later authorized overwrite.
- source: logbuf/recover.c:1354 " writeBlock(&buf, returnVal);"
- violation: A controller loses an acknowledged recovered block after a clean restart record is written.

### codex-2:E4
- contract: Storage must return the bytes last durably written to the requested address or report an error.
- source: logbuf/recover.c:1328 " readBlock(&buf, returnVal);"
- violation: A read silently returns stale data or data from another block.

### codex-2:E5
- contract: Storage writes must affect only their requested blocks and byte ranges.
- source: logbuf/recover.c:1299 " buffer->adev, buffer->blockNum, 0);"
- violation: A misdirected write damages a neighboring metadata block or an unrelated log page.

### codex-2:E6
- contract: The disk subsystem must keep completed active log pages readable and intact until reuse.
- source: logbuf/recover.c:761 " * active log pages outside the in-transit window are really"
- violation: A latent media error corrupts an older active log page.

### codex-2:E7
- contract: The async service must associate each completion and error with the correct submitted request.
- source: logbuf/recover.c:1300 " returnVal = asevent_QueueIO(buffer->adev, bp, ae);"
- violation: A driver signals completion for another request or drops an I/O error.

### codex-2:E8
- contract: The async service must finish all transfers before reporting their event complete.
- source: logbuf/recover.c:1302 " returnVal = asevent_WaitEvent(ae);"
- violation: The callback runs while DMA still reads the buffer that logbuf then recycles.

### codex-2:E9
- contract: The async service must eventually complete every accepted request or return a failure.
- source: logbuf/recover.c:1302 " returnVal = asevent_WaitEvent(ae);"
- violation: A lost interrupt leaves an event pending forever.

### codex-2:E10
- contract: The OS must honor memory pinning for buffers used by asynchronous I/O.
- source: logbuf/recover.c:1376 " logbuf_pin(data, dev->blkSize);"
- violation: The VM reclaims or relocates a pinned page during device access.

### codex-2:E11
- contract: The OS synchronization primitives must provide mutual exclusion and visibility of protected memory.
- source: logbuf/log.c:449 "#define map_assertlocked(map) afsl_Assert(epi_mutex_held(&(map)->mapLock))"
- violation: Two CPUs enter the same protected log-map critical section or observe stale fields after acquiring its lock.

### codex-2:E12
- contract: The OS condition-variable wait must release and reacquire its mutex atomically with sleeping and must deliver notifications reliably.
- source: logbuf/buffer.c:2347 " epi_cond_broadcast (&bpeP->cond);"
- violation: A waiter misses a wakeup and never notices newly available buffer space.

### codex-2:E13
- contract: The machine must provide atomic assignment and observation of the 32-bit tuning quantities used without reader locks.
- source: logbuf/log.c:2639 " * a 32 bit quantity is atomic w.r.t. all readers."
- violation: A port reads a torn value while a parameter is changed.

### codex-2:E14
- contract: The allocator must supply sufficient memory for the active log and recovery record structures.
- source: logbuf/recover.c:1038 " that we can read this much stuff into memory? */"
- violation: A valid large active log exhausts the recovery process address space.

### codex-2:E15
- contract: The compiler and ABI must lay out the device pointer immediately before the block-number field as the address hash expects.
- source: logbuf/buffer.c:842 " * block # fields are contiguous, with the device *first*. We"
- violation: An ABI inserts padding that becomes part of a hash key.

### codex-2:E16
- contract: Recovery must use the same compatible on-disk integer representation, structure layout and alignment as the log writer.
- source: logbuf/logrec.h:298 "#define GetPageHdr(buf) (struct logPageHdr *)(buf)"
- violation: An aggregate is recovered on a machine with incompatible byte order or structure packing.

### codex-2:E17
- contract: The supplied logical device must retain its block size and address interpretation for its entire log attachment.
- source: logbuf/buffer.c:1004 " bpeP = GetBufferPool(dP->blkSize);"
- violation: A device descriptor is retargeted or its block size changes while buffers remain cached.

### codex-2:E18
- contract: The configured device block size must be a supported power of two between 1 KiB and 64 KiB.
- source: logbuf/logbuf.p.h:416 "#define BUF_MAXBUFSIZE (64 * BUF_MINBLKSIZE) /* largest buffer size */"
- violation: An operator attaches a device using unsupported 3 KiB or 128 KiB logical blocks.

### codex-2:E19
- contract: The aggregate layer must provide the correct ordered array of physical log block addresses and its exact length.
- source: logbuf/recover.c:989 " /* guarantee the caller described the log properly */"
- violation: A damaged log anode supplies a permuted, truncated or wrong address array.

### codex-2:E20
- contract: The allocator must reserve distinct log blocks that do not overlap home metadata or user data.
- source: logbuf/recover.c:1044 " readData(ldP, logLocnArray[current], logBlocks[index]);"
- violation: The log address array repeats a block or includes a block also allocated to a file.

### codex-2:E21
- contract: The aggregate layer must keep the log allocation and address map fixed while logging is attached.
- source: logbuf/log.c:697 " IN daddr_t *logLocnArray,"
- violation: An online resize or relocation changes log blocks without a coordinated log replacement.

### codex-2:E22
- contract: Provisioning must allocate a log large enough for the minimum transaction reservation and safety margin.
- source: logbuf/log.c:1713 " * is large enough for at least one transaction, we also proceed if"
- violation: An aggregate is initialized with fewer pages than its transaction and block-size configuration needs.

### codex-2:E23
- contract: Filesystem callers must route every metadata modification through logged buffer operations in a valid transaction.
- source: logbuf/buffer.c:1422 " * if the tranId is not the invalid transaction id and the logRequest"
- violation: An anode or directory writer changes metadata directly or disables logRequest.

### codex-2:E24
- contract: Filesystem transaction boundaries must enclose a logically consistent complete metadata operation.
- source: logbuf/tran.c:435 "void elbt_EndTran(IN elbt_TranRec_t tranId)"
- violation: A caller ends a transaction after allocating a block but before installing its required reference.

### codex-2:E25
- contract: Filesystem callers must split oversized operations into bounded transactions that each preserve filesystem consistency.
- source: logbuf/log.c:1703 " * Each running transaction is assumed to need MAX_TRAN_SIZE of log"
- violation: Deleting a huge file is issued as one transaction or leaves an inconsistent intermediate truncation.

### codex-2:E26
- contract: Filesystem callers must finish active transactions rather than leave them open indefinitely.
- source: logbuf/log.c:1703 " * Each running transaction is assumed to need MAX_TRAN_SIZE of log"
- violation: An error path forgets EndTran and pins the log tail throughout continued operation.

### codex-2:E27
- contract: Higher layers must serialize conflicting accesses to the contents of each metadata object.
- source: anode/tlock.c:99 " lock_ObtainWrite_r (&tlock->lock);"
- violation: Two writers update a directory or anode without its transactional lock.

### codex-2:E28
- contract: Transactional-lock callers must report read/write dependencies on uncommitted state by merging the corresponding transactions.
- source: anode/tlock.c:112 " elbb_EquivTran (*tlockTransP, trans, (unsigned long) &tlock->lock);"
- violation: A caller uses an ordinary lock or a null transaction when consuming another active transaction's update.

### codex-2:E29
- contract: Callers must supply an active second transaction when requesting an equivalence-class merge.
- source: logbuf/tran.c:648 " * second tran must be active."
- violation: A stale completed transaction ID is passed as the new merge target.

### codex-2:E30
- contract: Callers must avoid waiting for transaction completion while holding an active transaction needed by that wait.
- source: logbuf/tran.c:1330 " * CAUTIONS -- The calling thread must not be holding any active transactions."
- violation: A thread forces a transaction in its own EC while retaining an unfinished member.

### codex-2:E31
- contract: Forced nested undo-zero transactions and their parent must fit within the single-transaction space bound.
- source: logbuf/log.c:1693 " * transaction size plus old transaction size will be less than the"
- violation: A caller creates enough forced child coverage to exceed its parent's reserved space.

### codex-2:E32
- contract: The block allocator must retain the logged-versus-unlogged classification and execute the required buffer transitions when reusing blocks.
- source: logbuf/recover.c:1897 " * NBS. These must be interpreted as kill records for earlier updates to"
- violation: A metadata block is reassigned to user data while dirty metadata remains cached.

### codex-2:E33
- contract: A caller may authorize killing dirty metadata only after the freeing transaction and all prior modifiers have committed.
- source: logbuf/buffer.c:1370 " * buffers. This will only be true if the transaction that freed the"
- violation: An allocator passes metadataOK=true before its freeing transaction commits.

### codex-2:E34
- contract: Filesystem allocation code must establish undo-zero protection for all newly exposed user-data bytes before allocation becomes durable.
- source: logbuf/buffer.c:2437 " * elbb_UndoZero - Adds an undo-zero record to an existing transaction for"
- violation: A newly allocated block is linked into a file without an undo-zero record.

### codex-2:E35
- contract: The VM must end an undo-zero transaction only after the protected first data write has completed successfully.
- source: logbuf/tran.c:1255 " * from the VM system which has its own Async daemon to complete I/O. We"
- violation: VM ends the protection on submission or after a failed first write.

### codex-2:E36
- contract: The VM must independently drive outstanding undo-zero I/O to completion while logbuf waits.
- source: logbuf/tran.c:1256 " * can safely wait for it to end its undo zeros."
- violation: The only VM flush worker is blocked trying to start a transaction behind its own pending undo zero.

### codex-2:E37
- contract: Callers must finish all updates to a dirty buffer before attaching its undo-zero transaction with UndoZeroBuffer.
- source: logbuf/buffer.c:2483 " * present. All updates to the dirty buffer have been done when this call"
- violation: The caller continues initializing the buffer after the first-write protection is attached and a write starts.

### codex-2:E38
- contract: Callers must restrict undo-zero buffer ranges to the current buffer and provide valid byte ranges to modification APIs.
- source: logbuf/buffer.c:2500 " afsl_Assert(fillSize + offset <= bP->adev->blkSize);"
- violation: An offset or length runs beyond the block or wraps arithmetic.

### codex-2:E39
- contract: Callers may omit old-value logging only for genuinely new block initialization whose old contents need not be restored.
- source: logbuf/buffer.c:1602 " * do not have to be logged, i.e. the buffer was created by CreateBlock."
- violation: Initialize is used to overwrite live metadata that must survive transaction abort.

### codex-2:E40
- contract: Callers using CreateBlock without a disk read must initialize all bytes that can become visible or significant before writeback.
- source: logbuf/buffer.c:974 " * (1) Just allocate a buffer (for overwriting an entire disk block."
- violation: Only part of a fresh cache buffer is initialized and the whole block is written to disk.

### codex-2:E41
- contract: Callers must retain a valid held writable buffer reference throughout modification and release it exactly once when finished.
- source: logbuf/buffer.c:1443 " afsl_Assert(bufferIsWrite(bP) && (bP->refCount > 0));"
- violation: A stale buffer pointer is used after Release or a leaked hold prevents reclamation.

### codex-2:E42
- contract: Callers must use the returned buffer handle after operations that may replace the handle.
- source: logbuf/buffer.c:1426 " * cannot assume the buffer handle will not change across this call."
- violation: A caller ignores nbP and continues using the original pointer after a modifying operation.

### codex-2:E43
- contract: Callers must classify external buffers as data or logged buffers and leave internal buffer types to logbuf.
- source: logbuf/logbuf.p.h:47 " * users of this package are restricted to the first two cases"
- violation: A filesystem caller requests elbb_bufLog for a normal metadata block.

### codex-2:E44
- contract: Callers must not mix logged and unlogged dirty modifications to the same logged buffer between writebacks.
- source: logbuf/buffer.c:1453 " /* Require that updates to logged buffers are either always logged or"
- violation: A caller first dirties a metadata buffer without logging and then performs a logged edit.

### codex-2:E45
- contract: Code paths needing multiple simultaneously held buffers must reserve sufficient buffer capacity before acquisition and return their reservation.
- source: logbuf/buffer.c:2215 " * elbb_Reserve - reservation call for code paths which require multiple"
- violation: Several operations each hold one buffer and wait for another in an exhausted pool.

### codex-2:E46
- contract: Higher layers must synchronize aggregate access against log shutdown and teardown.
- source: logbuf/tran.c:557 " * levels have properly synchronized access to this aggregate."
- violation: An aggregate is closed while another thread starts a modification or uses its device descriptor.

### codex-2:E47
- contract: The caller must invoke LogInit without dirty cached buffers on the recovered device.
- source: logbuf/buffer.c:1854 " * buffers were dirty when elbb_LogInit was called."
- violation: An aggregate has dirty pre-recovery cache entries when initialization triggers recovery.

### codex-2:E48
- contract: The recovery caller must exclude concurrent filesystem writes and other recovery instances on the same aggregate.
- source: logbuf/recover.c:359 " * This code must run single-threaded in user space; it runs multi-threaded"
- violation: A mounted writer or second salvager changes blocks while recovery calculates and writes repairs.

### codex-2:E49
- contract: The operator or aggregate layer must arrange user-space recovery when a dirty log is rejected by the kernel.
- source: logbuf/recover.c:2402 " return RCVR_MUSTRCVR; /* no kernel recovery anymore */"
- violation: An operator treats RCVR_MUSTRCVR as a clean mount or never runs the recovery utility.

### codex-2:E50
- contract: Higher layers must honor recovery and initialization return codes and retry initialization after RCVR_RECOVERED.
- source: logbuf/log.c:743 " return RCVR_RECOVERED; /* so upper levels can clear buffers */"
- violation: The caller proceeds as if a normal log attachment succeeded after recovery or ignores a recovery failure.

### codex-2:E51
- contract: Operators must use the salvager rather than rely on log replay alone after unrecoverable active-log or critical metadata I/O damage.
- source: logbuf/recover.c:1049 " * Only resort is to run salvager"
- violation: A deployment resumes normal service after recovery fails on corrupted required log pages.

### codex-2:E52
- contract: The filesystem fsync path must identify every required cached buffer with correct file-handle tags or a complete block list.
- source: logbuf/buffer.c:2039 " * the buffers to write out. Either a magic value is used to tag each"
- violation: A file has an untagged dirty indirect block or a required block is omitted from the array.

### codex-2:E53
- contract: Callers requiring persistence must choose a mode that waits for the necessary data or transaction commit and check its result.
- source: logbuf/logbuf.p.h:63 " elbb_async, /* schedule write now, but don't wait for completion */"
- violation: A vnode fsync returns success after SyncForce, async release or a completion-only transaction wait.

### codex-2:E54
- contract: VM integration must flush file data outside the buffer pool before claiming whole-file durability.
- source: logbuf/buffer.c:2439 " * that do not use the buffer system. It is expected that this would not be"
- violation: A file fsync flushes logbuf buffers but leaves dirty mapped pages in the VM.

### codex-2:E55
- contract: Callers requesting commit quiescence must arrange completion of dirty-buffer and VM undo-zero writes before waiting for their transactions.
- source: logbuf/tran.c:1254 " * all dirty buffers to be written. Any other undo zero transactions are"
- violation: A higher layer waits for undo-zero commit without scheduling the data writes that end those transactions.

### codex-2:E56
- contract: Startup must initialize transaction globals without concurrent transaction users.
- source: logbuf/tran.c:178 " * Locks: assumes no locking (single-threaded at init time). Call is"
- violation: Two startup threads initialize or use transaction lists concurrently.

### codex-2:E57
- contract: Tuning callers must supply accessible kernel-address-space values and perform user-space copyin or copyout themselves.
- source: logbuf/buffer.c:876 " * Note that elbb_Tune assumes the address of value is in its address"
- violation: An administrative interface forwards an unchecked user pointer to Tune.

### codex-2:E58
- contract: Administrative tuning must preserve valid transaction, equivalence-class and log-capacity limits for attached devices.
- source: logbuf/log.c:2668 " /* XXX: go back and recompute for all active log maps. */"
- violation: An operator changes a global maximum and assumes existing log maps have been resized or re-reserved.

### codex-2:E59
- contract: The scheduler must allow transaction owners and I/O completion workers to run while other threads wait for them.
- source: logbuf/tran.c:1215 " elbt_TranUnlockAndSleep(tP,tP);"
- violation: A high-priority waiter starves the only thread that can finish its transaction or I/O.

### codex-2:E60
- contract: The OS time service must provide usable elapsed-time progression for the buffer-cache aging heuristics.
- source: logbuf/buffer.c:2857 " * reused. Thus the average age of reuse must be much smaller than the"
- violation: A broken clock freezes age calculations or jumps enough to distort cache-cost comparisons.

### codex-2:E61
- contract: The aggregate layer must keep the log-location array allocated and unchanged until the log is detached.
- source: logbuf/log.c:816 " lmP->logLocnArray = logLocnArray;"
- violation: A caller frees its temporary address array after LogInit returns.

### codex-2:E62
- contract: Device management must use one stable canonical async-device identity for each attached aggregate.
- source: logbuf/log.c:109 " LookupLogMap(dP, lmP); \"
- violation: Two descriptors name the same disk and permit independent log attachments or conflicting cache entries.

### codex-2:E63
- contract: The allocator must commit earlier metadata modifications before a later user-data kill makes their history obsolete.
- source: logbuf/recover.c:1937 " RECVR_RAISE (RCVR_METADATA);"
- violation: A block is reused for user data while a preceding metadata update is still uncommitted.

### codex-2:E64
- contract: The allocator must complete a user-data kill transaction before reusing that block for newer logged metadata.
- source: logbuf/recover.c:1929 " RECVR_RAISE (RCVR_USERDATA);"
- violation: New metadata is installed on a block whose user-data undo-zero transaction remains uncommitted.

### codex-2:E65
- contract: Provisioning must select a working supported checksum format when relying on detection of partial log-page writes.
- source: logbuf/recover.c:2445 " case LOGREC_CKSUMVER_NONE:"
- violation: An aggregate uses the no-checksum format yet expects a partly written multi-sector page to be detected.

### codex-2:E66
- contract: The environment must not silently alter log pages into different records with the same accepted checksum and plausible headers.
- source: logbuf/recover.c:2603 " SameChecksum(storedCksum, calcCksum, storedCksumLen)) {"
- violation: Corruption happens to collide under CRC32 or a tool recomputes the checksum after an incorrect edit.

### codex-2:E67
- contract: Transactional-lock storage must not be recycled for a different object until its associated transaction has completed.
- source: anode/tlock.c:53 " code = elbb_LogForce(*transP, 2/*complete*/);"
- violation: An anode lock is freed and reused without tlock_Recycle or Destroy while its transaction is active.

### codex-2:E68
- contract: Callers must keep source data and its declared address-space classification valid until a modification call finishes copying and logging it.
- source: logbuf/buffer.c:1436 " IN osi_uio_seg_t newDataSource, /* address space of newData ptr */"
- violation: A user buffer changes concurrently between log copying and home-buffer copying, or a user pointer is marked OSI_UIOSYS.

### grok-1:E1
- contract: A crash stops the machine, discards volatile memory, and leaves on disk only the sector writes that had already completed, rather than continuing to store arbitrary bytes.
- source: §"Component Architecture" " The recovery procedure runs after a crash, replaying the committed transactions and undoing the"
- violation: The processor continues after a fault and writes partial or wild data into the log or into metadata blocks, or a crash scrambles memory-mapped I/O that was not an in-flight sector write.

### grok-1:E2
- contract: When the async layer or the device driver reports that a write has completed, every sector of that write is on stable storage and will still be there after a crash or power loss.
- source: logbuf/recover.c:894 " * underlying system to really guarantee that a page is on disk"
- violation: A SCSI disk or the driver acknowledges the write when the bytes reach a volatile write-back cache, and a power loss then drops a log page the log package has already treated as committed, or drops it while a later metadata write remains.

### grok-1:E3
- contract: Each hardware sector write is atomic, and the log page header together with its checksum occupies that first sector.
- source: logbuf/recover.c:746 " * correctness/atomicity of each sector. So if the log page did"
- violation: A disk tears one sector so that the first sector of a log page mixes old and new bytes, and the mixture still carries a plausible pass number or checksum.

### grok-1:E4
- contract: A log page that was written successfully and is outside the in-transit window remains byte-for-byte intact until the log package overwrites it.
- source: logbuf/recover.c:756 " * expected to be on disk correctly. If checksum errors are"
- violation: Media corruption, a dropped write that was acknowledged, or a stale read changes a committed log page after the in-transit window has moved past it.

### grok-1:E5
- contract: The restart page, which recovery does not checksum, must keep the exact header and restart record written by log creation, clean shutdown, or a finished recovery.
- source: logbuf/recover.c:2738 " * We choose not to checksum the log page containing a restart record"
- violation: Bit rot or a torn write leaves the salvage magic and a restart record type in the first log block of a log that still has an active tail, or destroys a genuine restart record.

### grok-1:E6
- contract: The device and the async veneer must report a failed or unreadable log or metadata transfer as an error, and must not return success for a page that was not stored or not read.
- source: logbuf/recover.c:788 " * log page is damaged; run salvager."
- violation: The driver returns a zero completion for a write it dropped, or returns old or zeroed data for a read that the media could not perform.

### grok-1:E7
- contract: On AIX, an I/O completion reported as ESOFT must mean the transfer finished and is durable, because the async layer clears that error and treats the buffer as successful.
- source: async/asevent.c:1070 " if (bp->b_error == ESOFT) {"
- violation: The AIX driver returns ESOFT for a write that was not stored, and Episode clears the error and continues as if the log page or metadata block were on disk.

### grok-1:E8
- contract: A later read of a block must return, sector by sector, the data of the last write to that sector that the driver has reported complete.
- source: logbuf/recover.c:892 " * We trust the log to make sure it doesn't assume a page with"
- violation: A drive cache, a multipath disk, or a host buffer returns a stale copy after a completed write, so recovery or the next mount sees an older log page.

### grok-1:E9
- contract: The device block size is a power of two, at least 1024 bytes, small enough for the recovery allocator, and it is the unit of every log and metadata address the caller passes in.
- source: logbuf/log.c:863 " afsl_MBZ(blkSize & 1023); /* must be power-of-two >= 1K */"
- violation: The aggregate is opened with a block size other than the one stamped in the superblock, or with a size below 1024 or not a power of two, so log pages and metadata blocks are read at the wrong offsets.

### grok-1:E10
- contract: The user-space process that recovers or creates an aggregate must open the device so that a completed write is durable before completion returns, and the kernel must not mount until that process has finished.
- source: salvage/salvage_main.c:255 " ? US_OFLAGS_SYNC : US_OFLAGS_RDONLY));"
- violation: Recovery runs through us_open without US_OFLAGS_SYNC, the process exits or the machine crashes with the restart record in the host page cache and the recovered metadata blocks not yet on media, and the kernel then mounts.

### grok-1:E11
- contract: The caller must pass a log-location array that lists every log-container block in order, with page number i stored at that array entry and with no other file or metadata block in the list.
- source: logbuf/recover.c:983 " /* guarantee the caller described the log properly */"
- violation: The aggregate map is short, permuted, or overlaps a directory or bitmap, so recovery reads file data as the log or fails to read the real tail.

### grok-1:E12
- contract: Every block of the log container must already be allocated and mapped before logging starts.
- source: anode/aggregate.c:326 " /* All log pages must be pre-allocated. There is a faster way to"
- violation: A log page address is a hole or an unallocated block, so a log write fails or lands on a block that a file is also using.

### grok-1:E13
- contract: The log container must not grow or shrink while the aggregate is in use.
- source: §"Data Architecture" "do not, in the current implementation, change dynamically. The log container does not grow or shrink"
- violation: An operator or a later tool extends or truncates the log container while transactions are running, so the in-memory location array and the pass numbers no longer describe the disk.

### grok-1:E14
- contract: The log must be at least large enough for one maximum transaction plus the reserve of buffers that are allowed to be in transit, for the block size and the concurrency the file system will start.
- source: logbuf/log.c:1694 " * is large enough for at least one transaction, we also proceed if"
- violation: newaggr or the operator creates a log smaller than elbl_MinLogSize, or small enough that the transactions the vnode layer actually starts cannot all reserve space.

### grok-1:E15
- contract: The initialization utilities must record the log container that recovery will open, and if that container is placed on another device both devices must be recovered together and both must be stable.
- source: §"Data Architecture" "be on the same aggregate as the data that it is logging, but this restriction is currently imposed by our"
- violation: The utilities point the aggregate at a log device that is missing at recovery, or at a log on volatile media while the data disk kept its completed writes.

### grok-1:E16
- contract: Operators and tools must not write a restart record, or otherwise mark the log clean, except by log creation, a clean shutdown, or a recovery that has finished applying updates.
- source: logbuf/recover.c:2738 " * We choose not to checksum the log page containing a restart record"
- violation: patchlog or an operator copies a restart record onto the first log block of a dirty aggregate to make it mount, without replaying the tail.

### grok-1:E17
- contract: After a crash the operator or the mount path must run user-space recovery to completion before the kernel attaches the aggregate, and must not expect the kernel to recover.
- source: logbuf/recover.c:2374 " return RCVR_MUSTRCVR; /* no kernel recovery anymore */"
- violation: A mount tool attaches a dirty aggregate in the kernel, ignores RCVR_MUSTRCVR or the recovered status, and serves the file system on the unreplayed disk.

### grok-1:E18
- contract: User-space recovery of one aggregate must run on a single thread, and the caller must be prepared for the recovery routines to return by longjmp.
- source: logbuf/recover.c:358 " * This code must run single-threaded in user space; it runs multi-threaded"
- violation: Two threads in the salvager call elbr_Recover at once, or a caller invokes the dump routine without a setjmp frame, so a checksum failure longjmps off the stack.

### grok-1:E19
- contract: The user-space recovery process must provide setjmp and longjmp with ordinary C semantics, so the code passed to longjmp is the code setjmp returns.
- source: logbuf/recover.c:125 " * This assumes traditional semantics for an in-kernel setjmp/longjmp."
- violation: The C library or a kernel-style jump buffer returns 1, or returns 0, for every longjmp, and recovery reports failure for success or success for a checksum error.

### grok-1:E20
- contract: The recovery process must be able to allocate memory for every page of the active log and for the record index built from it.
- source: logbuf/recover.c:1031 " /* TODO: is this a safe assumption ---"
- violation: The active log is larger than the address space or the ulimit of the salvager, malloc fails, and recovery panics or raises out of the replay.

### grok-1:E21
- contract: After a crash the primary superblock must still be a valid aggregate header naming this log, because attach and the salvager do not fall back to an alternate superblock.
- source: anode/aggregate.c:1138 " * primary superblock, and since the salvager doesn't presently"
- violation: The only primary superblock is torn or unreadable, or its block size or log length no longer matches the device, and the alternate copies are ignored.

### grok-1:E22
- contract: The host must call the file system's sync often enough that committed dirty metadata buffers are written and the active log is checkpointed on the order of the paper's interval of T seconds.
- source: §"Recovery Time" "every T seconds, as is the case with Episode, then the active portion of the log can rise to include all the"
- violation: The update daemon is disabled or wedged, so dirty metadata stays in memory until log-full handling is forced to write it, and the active tail grows to the whole log.

### grok-1:E23
- contract: When recovery or logging hits a hard I/O error, a bad log magic, or a checksum or pass-number failure outside the in-transit window, the operator must run the salvager and must not serve the aggregate.
- source: §"Component Architecture" "can not regenerate a consistent le system, however, such as when hard I/O errors occur while updating"
- violation: The operator ignores a recovery I/O error, forces the aggregate online, or keeps serving after the kernel panics on a log write error and is rebooted onto the same disk.

### grok-1:E24
- contract: Higher layers must allow only one writer, the kernel service or the salvager, to use an aggregate at a time, and must have stopped new transactions before shutdown of the log.
- source: logbuf/tran.c:553 " * levels have properly synchronized access to this aggregate."
- violation: Two hosts mount the same aggregate, or the salvager runs against a mounted aggregate, or shutdown runs while vnode threads are still in StartTran.

### grok-1:E25
- contract: The anode, directory, and vnode layers must make every metadata update, and only metadata updates, through a logged buffer operation inside a transaction.
- source: §"Logging Architecture" "requires only that the meta-data be consistent. Episode logs only meta-data changes. Although restricting"
- violation: A directory, bitmap, indirect block, or anode is written as user data or by a raw device write, or a user-data block is passed to the log as a logged buffer.

### grok-1:E26
- contract: Callers must modify a logged buffer only through Modify, Fill, or Initialize, and must not mix logged and unlogged updates to the same buffer.
- source: logbuf/buffer.c:1442 " /* Require that updates to logged buffers are either always logged or"
- violation: A caller stores into the buffer's data pointer, or logs one update to a buffer and writes the next update with logging off, so the log does not contain the bytes that later reach disk.

### grok-1:E27
- contract: Callers must use buffer initialization only for a block just created with CreateBlock, whose previous contents must not be restored.
- source: logbuf/buffer.c:1588 " * By initialization, we mean modification in the case where the old data"
- violation: A caller initializes an existing metadata block, so the log gets the new bytes and not the old ones, and an abort cannot put the old bytes back.

### grok-1:E28
- contract: Each transaction the caller commits must take a consistent metadata state to another consistent one, including directory, bitmap, indirect-block, anode-table, and clone copy-on-write updates.
- source: §"Logging Architecture" "operations, followed by a deletion of the empty le. After each transaction, the le system is consistent, if"
- violation: A vnode operation commits a directory entry without the anode, or updates a copy-on-write pointer in a different transaction from the block allocation that the pointer names.

### grok-1:E29
- contract: Callers must keep each transaction within the reservation the log assumed for them and must end it, splitting any larger operation into such transactions.
- source: §"Logging Architecture" "exceed the space available in the log. Transactions that run too long or modify too much data represent"
- violation: A fileset or directory operation logs more than the presumptive maximum, or never calls EndTran, so the reservation no longer covers the tail the transaction pins.

### grok-1:E30
- contract: A caller that force-starts a nested undo-zero transaction must keep that transaction's reservation plus its parent's within the size of one maximum transaction.
- source: logbuf/log.c:1673 " * space in the log. The caller is guaranteeing that the new"
- violation: The VM or the anode layer nests an undo-zero transaction whose combined size exceeds one maximum transaction, and the log admits it without checking free space.

### grok-1:E31
- contract: A thread that waits for other transactions to complete or commit, including quiesce, must not itself hold an active transaction.
- source: logbuf/tran.c:1313 " * CAUTIONS -- The calling thread must not be holding any active transactions."
- violation: A vnode thread calls quiesce or otherwise waits for a transaction while it still owns an active transaction that the wait needs to end.

### grok-1:E32
- contract: Whenever two uncommitted transactions use the same metadata object, the caller must merge them into one equivalence class with a tlock while the later transaction is still active.
- source: anode/tlock.h:20 " * the same lock, they must be put in the same equivalence class. To minimize"
- violation: A code path locks a shared anode, bitmap, or volume object with an ordinary lock, or releases it without elbt_ECMerge, and the later transaction then commits on its own.

### grok-1:E33
- contract: The allocation bitmap's logged-or-unlogged bit must match the block's use, and the allocator must perform the buffer-pool transition when a block changes from logged to unlogged or the reverse, before the block is reused.
- source: §"Data Architecture" "the fragment is allocated, and whether the fragment represents logged or unlogged data. This last distinc-"
- violation: A freed metadata block is handed out as user data, or the reverse, without killing the old buffer and without the bitmap bit changing in the same transaction.

### grok-1:E34
- contract: Callers must pass metadataOK to elbb_Kill only after the transaction that freed that metadata block has committed, which is also after every transaction that modified the block has committed.
- source: logbuf/buffer.c:1359 " * PARAMETERS -- metadataOK is true if it is safe to kill dirty metadata"
- violation: The allocator kills a dirty logged buffer before the freeing transaction's end record is on disk, so the buffer leaves the age queue while its updates exist only in the log or are still uncommitted.

### grok-1:E35
- contract: The allocator must not leave an uncommitted kill record newer than ordinary records on the same block, and every record a committed kill skips must already be committed.
- source: logbuf/recover.h:84 " * record on the same block. The transaction contain such records must have"
- violation: A new metadata update is logged for a block while an undo-zero kill of that block is still uncommitted, or the kill would skip a record whose transaction has no end record.

### grok-1:E36
- contract: For a newly allocated user-data block, the caller must record an undo-zero covering every byte that could expose old contents, and must end that transaction only when the first write of the block has completed.
- source: §"Logging Architecture" "problem by starting another transaction when the block is allocated, and ending it when the rst write"
- violation: The allocating transaction commits, the machine crashes before the first write is durable, and no undo-zero record covers the block, so the old occupant remains readable in the new file.

### grok-1:E37
- contract: The caller must attach an undo-zero record only after the new bytes are in the buffer, and must do so before ending the transaction that allocated the block.
- source: anode/anode.c:696 " * attach the undo-zero record. If we do this any earlier, the logbuf"
- violation: The caller attaches undo-zero before the new data is copied, the buffer package cleans the buffer and ends the undo-zero transaction, and the new bytes are stored only afterward.

### grok-1:E38
- contract: For I/O that does not use the buffer cache, the VM must call the undo-zero entry with the byte range being written and must not end that transaction before the write completes.
- source: logbuf/buffer.c:2415 " * the specified range of bytes. This is to be used by the VM system for I/Os"
- violation: Strategy writes a newly allocated block from the page cache and never records an undo-zero, which is the state of the strategy module in this tree.

### grok-1:E39
- contract: While quiesce waits for undo-zero transactions, the VM's own asynchronous daemon must keep running and must end those transactions when its I/O completes.
- source: logbuf/tran.c:1239 " * from the VM system which has its own Async daemon to complete I/O. We"
- violation: The thread blocked in quiesce is the thread that would complete the VM I/O, or the daemon stops, so the undo-zero transactions stay active and quiesce never returns.

### grok-1:E40
- contract: A caller that needs metadata to be persistent, such as fsync, must invoke log force or fsync-force on the buffers of that file, identified by the file's magic or by an explicit block list, and the VM must write back that file's dirty pages.
- source: §"Logging Architecture" " Meta-data changes to the disk itself can often be deferred, unless speci cally requested by an oper-"
- violation: The vnode fsync path returns without elbb_LogForce, the file-handle magic on the buffers does not match the magic passed to fsync-force, or the platform's VM flush is a stub that returns success.

### grok-1:E41
- contract: The caller of log initialization must not have dirty buffers cached for that device, and after recovery reports that it repaired the log the caller must drop cached buffers before using the device.
- source: logbuf/buffer.c:1839 " * buffers were dirty when elbb_LogInit was called."
- violation: Log initialization is called while dirty metadata buffers are cached, or a caller of recovery keeps those buffers and writes them back over the blocks recovery just repaired.

### grok-1:E42
- contract: One device object and one block number must name one physical block, and the C layout must place the device pointer immediately before the block number with no padding between them.
- source: logbuf/buffer.c:839 " * note that for this key to work, we assume that the device and"
- violation: Two async device objects alias one disk, or a compiler inserts padding between the device pointer and the block number, so the address hash misses or collides.

### grok-1:E43
- contract: An aligned store of a 32-bit value must be atomic with respect to every concurrent reader on the machine.
- source: logbuf/log.c:2602 " * a 32 bit quantity is atomic w.r.t. all readers."
- violation: A reader observes a half-updated 32-bit tuning or status word, for example a log-full threshold mixed from the old and new values.

### grok-1:E44
- contract: The host must not require a stricter alignment than 32-bit for the log record layouts, and recovery must run with the same integer endianness and width as the writer.
- source: logbuf/logrec.h:44 " * more strict alignment than is assumed here (i.e. all data"
- violation: The aggregate is recovered on a big-endian host after being written on a little-endian host, or the CPU faults on an access the log record macros perform.

### grok-1:E45
- contract: Memory that holds log pages and metadata buffers must remain resident, with its contents unchanged, until logbuf releases it.
- source: logbuf/logrec.h:371 "#define logbuf_pin(x, s) /* nothing */"
- violation: On a platform where the pin macro is empty, the kernel reclaims a dirty metadata or log page and later returns different bytes for the same address.

### grok-1:E46
- contract: The pointer passed to the log and buffer tuning call must address memory in the caller's own address space that holds the whole value being read or written.
- source: logbuf/buffer.c:873 " * Note that elbb_Tune assumes the address of value is in its address"
- violation: A caller passes a user pointer or a short buffer, so the tune reads or writes the wrong word and changes the maximum log or the full-log fraction.

### grok-1:E47
- contract: Callers of the quick logged modify and of buffer fill must pass metadata that already resides in the kernel address space, never a user pointer and never file-body data.
- source: logbuf/buffer.c:1703 " * assume along this code path that we never have user data (e.g. we"
- violation: A caller points the fast modify path at a user address or at file contents, so the log record copies the wrong bytes or faults, and user data is written into the log.

### grok-1:E48
- contract: Code that runs during a kernel panic must not depend on starting further transactions once log-full handling has stopped retrying.
- source: logbuf/buffer.c:1762 " if (osi_IsKernelPanic() && ++nLoops == ELBB_MAX_PANIC_LOOP)"
- violation: Panic or crash-dump code keeps modifying metadata after elbb_StartTran returns failure, and a dirty buffer is then written without a new log record.

### grok-1:E49
- contract: The checksum version recorded on the log must be a version recovery knows, so torn pages are rejected rather than ignored.
- source: logbuf/recover.c:2578 " /* Unknown checksum type recorded on disk. Force success of"
- violation: An operator or patchlog sets an unknown checksum version, and recovery then treats every page checksum as valid.

### grok-1:E50
- contract: Transaction initialization must run single-threaded, before any thread starts a transaction.
- source: logbuf/tran.c:177 " * Locks: assumes no locking (single-threaded at init time). Call is"
- violation: Two threads call the transaction initializer concurrently during the first mount, and the free list or the locks are published half-initialized.

### grok-2:E1
- contract: A crash stops the machine, discards memory, and leaves on disk only updates whose writes had reached the device.
- source: §"Component Architecture" "In the event of a crash, only some of the updates to the le system"
- violation: The machine keeps issuing writes after the failure, or a DMA engine scribbles arbitrary blocks as power fails.

### grok-2:E2
- contract: When the driver reports an I/O complete, that entire transfer is on stable storage and later reads, including reads after power loss, return those bytes.
- source: logbuf/recover.c:894 " * underlying system to really guarantee that a page is on disk"
- violation: A disk or controller write-back cache acknowledges the write while the bytes still sit only in volatile memory, and a power loss drops them after Episode has forced the log and then written a metadata block.

### grok-2:E3
- contract: A device sector is written entirely or left entirely unchanged, including the first sector of a log page and every sector of a metadata block.
- source: logbuf/recover.c:746 " * correctness/atomicity of each sector. So if the log page did"
- violation: A crash tears a 512-byte sector so the log-page header mixes a new checksum with an old pass number, or a metadata sector mixes bytes from two versions of the same block.

### grok-2:E4
- contract: The device's atomic sector is large enough to hold the whole log-page header and its checksum, which the log places at the start of the page.
- source: logbuf/recover.c:744 " /* The log page header ( including checksum ) is in the first"
- violation: The device sector is smaller than the header plus checksum, so a crash can persist a new checksum while leaving part of the header from an older page.

### grok-2:E5
- contract: The driver reports a transfer that did not finish as a hard error, and the async layer is entitled to treat any other completion as success.
- source: async/asevent.c:1070 " if (bp->b_error == ESOFT) {"
- violation: AIX returns ESOFT for a write that did not reach stable media, and asevent_Iodone clears b_error and B_ERROR before the log inspects the event.

### grok-2:E6
- contract: Until Episode overwrites a block, the device returns the bytes of the last completed write to that block, or it returns an I/O error.
- source: logbuf/recover.c:756 " * expected to be on disk correctly. If checksum errors are"
- violation: A later media error, a misdirected write, or a dropped sector changes a log page or a metadata block that recovery still needs, and the read succeeds with different bytes.

### grok-2:E7
- contract: The kernel's device-block conversion addresses the same physical sectors the driver writes, and an Episode block is an integer number of those sectors.
- source: async/asevent.c:139 "#define ToBufferBlocks(adevice, ablock, aoffset) \"
- violation: DEV_BSIZE, abtodb, or btodb disagrees with the disk's sector size, so log and metadata I/O lands on the wrong addresses.

### grok-2:E8
- contract: Memory the log pins, or hands to the driver, stays resident and unmodified until the matching I/O completes, and the virtual memory system does not write a buffer-pool page by any other path.
- source: async/async.p.h:83 "#define ASEVENT_NOPIN 16 /* do not pin/unpin data (AIXism) */"
- violation: pin fails or is a no-op and the kernel reclaims a log page or a dirty metadata buffer, or it writes that page from a paging path that never forces the log.

### grok-2:E9
- contract: The process that runs recovery can allocate memory for every page and record of the active log at once.
- source: logbuf/recover.c:1031 " /* TODO: is this a safe assumption ---"
- violation: The salvage process is short of address space or the active log is larger than the heap, and osi_Alloc or the recovery allocator fails.

### grok-2:E10
- contract: setjmp and longjmp, and the kernel exception longjmp where it is still compiled in, restore the recovery catch point and abandon the failed pass.
- source: logbuf/recover.c:125 " * This assumes traditional semantics for an in-kernel setjmp/longjmp."
- violation: The C library or the kernel exception handler returns into a half-updated recovery structure, or it fails to jump, and recovery continues after RCVR_RAISE.

### grok-2:E11
- contract: The machine that recovers a log uses the same endianness, integer sizes, and structure padding as the machine that wrote it.
- source: logbuf/logrec.h:44 " * more strict alignment than is assumed here (i.e. all data"
- violation: An aggregate written on a big-endian SPARC or RS/6000 is recovered on a little-endian host, so the salvage id, pass number, and record fields are byte-swapped.

### grok-2:E12
- contract: The CPU and compiler honor the log's 4-byte alignment rules for on-disk records and in-memory casts.
- source: logbuf/logrec.h:44 " * more strict alignment than is assumed here (i.e. all data"
- violation: A port to a machine that faults on the unaligned references the macros still perform, or a compiler inserts padding the on-disk layout does not have.

### grok-2:E13
- contract: A naturally aligned 32-bit store is atomic with respect to every reader on the machine.
- source: logbuf/log.c:2602 " * a 32 bit quantity is atomic w.r.t. all readers."
- violation: A reader observes a half-updated word of a tuneable log parameter while another CPU stores it.

### grok-2:E14
- contract: The caller of log initialization passes the full ordered list of preallocated log-container blocks, and those blocks are not also used as file or metadata blocks.
- source: anode/aggregate.c:326 " /* All log pages must be pre-allocated. There is a faster way to"
- violation: The array omits a page, repeats one, points at file data, or disagrees with the page numbers stored in the log headers.

### grok-2:E15
- contract: The operator gives the aggregate a log at least as large as the minimum for its workload, and leaves that container's size and block list fixed while the aggregate exists.
- source: §"Data Architecture" "The log container does not grow or shrink"
- violation: newaggr creates a log smaller than elbl_MinLogSize, or an administrator grows, shrinks, or relocates the log container under a live aggregate.

### grok-2:E16
- contract: Each higher-level transaction stays within the reservation the log assumed for it, initially 70K and five log blocks, or within the log after that reservation has grown.
- source: logbuf/log.c:481 " * this is presumtive, not declarative; it reflects our understanding of"
- violation: A vnode or anode operation logs more than the reserved size in one transaction, and the log cannot grow the reservation without overrunning the container.

### grok-2:E17
- contract: A caller that starts a nested undo-zero transaction while the log is full keeps that transaction, plus the transaction it nests under, inside the maximum size of one transaction.
- source: logbuf/log.c:1673 " * space in the log. The caller is guaranteeing that the new"
- violation: The VM or the buffer package nests an undo-zero whose combined size exceeds one transaction reservation, and the force path skips the free-space check.

### grok-2:E18
- contract: The aggregate's block size is a power of two of at least 1K, equals the async device block size, and the fragment size is a power of two from 1K up to that block size.
- source: logbuf/log.c:863 " afsl_MBZ(blkSize & 1023); /* must be power-of-two >= 1K */"
- violation: The superblock names a block size the device was not opened with, or a fragment size below 1K or not a power of two.

### grok-2:E19
- contract: The log device and the data device experience the same crashes and the same durability, so a completed write on one is still present when recovery runs on the other.
- source: §"Data Architecture" "be on the same aggregate as the data that it is logging, but this restriction is currently imposed by our"
- violation: The log sits on a disk that loses power or fails independently of the data disk, or the operator recovers only one of the two devices.

### grok-2:E20
- contract: The checksum version stored in the log is one this recovery code implements.
- source: logbuf/recover.c:2578 " /* Unknown checksum type recorded on disk. Force success of"
- violation: A newer or older creator writes a checksum version the running salvager does not know.

### grok-2:E21
- contract: Before the kernel uses a dirty aggregate, the operator runs user-space recovery to a clean restart and does not mount the aggregate in between.
- source: logbuf/recover.c:2374 " return RCVR_MUSTRCVR; /* no kernel recovery anymore */"
- violation: The operator mounts a crashed aggregate without epilog or salvage, or mounts it while a user-space recovery is still writing the restart block.

### grok-2:E22
- contract: When recovery or a metadata I/O hits a hard error, a bad log page, RCVR_USERDATA, or RCVR_METADATA, the operator runs the salvager and leaves the aggregate unmounted.
- source: §"Component Architecture" "critical meta-data. In such cases, the Episode salvager utility needs to be run; the salvager's performance"
- violation: The operator forces the aggregate online, or ignores a panic, after a checksum failure outside the in-transit window or a kill-record conflict.

### grok-2:E23
- contract: Only one Episode instance writes an aggregate at a time, user-space recovery runs single-threaded, and higher layers have stopped other threads before shutdown.
- source: logbuf/tran.c:553 " * levels have properly synchronized access to this aggregate."
- violation: Two hosts mount the same disk, salvage runs against a mounted aggregate, or shutdown races with a thread still in elbb_StartTran.

### grok-2:E24
- contract: The operator leaves removable media in place until the last aggregate close has returned, and no other agent reads or writes it during that close.
- source: anode/aggregate.c:1716 " * this means that if the disk is on removable media it could be safely"
- violation: The operator ejects the disk, or a raw copy starts, after the unmount call begins and before the restart block write finishes.

### grok-2:E25
- contract: The caller of elbb_LogInit has no dirty buffers for that device.
- source: logbuf/buffer.c:1839 " * buffers were dirty when elbb_LogInit was called."
- violation: Log initialization recovers the log and then elbb_Shutdown writes dirty cached metadata back over the repaired blocks.

### grok-2:E26
- contract: A deployment that relies on crash consistency initializes the aggregate with logging turned on.
- source: anode/aggregate.c:1418 " * logged -- whether to turn on logging. Usually true, only false for some"
- violation: A mount or test harness calls epig_InitAggregate with logged false on an aggregate that users expect to survive a crash.

### grok-2:E27
- contract: Every update to directories, allocation bitmaps, indirect blocks, and anode tables is made through a logged buffer transaction that records the old and new bytes.
- source: §"Component Architecture" "made to any le system meta-data, both the original and new values of the updated data. Furthermore,"
- violation: A higher layer writes a metadata block through the raw device or through an unlogged buffer, or it modifies the bytes in place without elbb_Modify.

### grok-2:E28
- contract: Every modification of a buffer that is being logged is itself logged, and a buffer that is not logged is never given a log record.
- source: logbuf/buffer.c:1442 " /* Require that updates to logged buffers are either always logged or"
- violation: A caller passes logRequest false for a dirty logged buffer, or logRequest true for an unlogged user-data buffer.

### grok-2:E29
- contract: The bitmap's logged-or-unlogged mark, the anode's logged flag, and the buffer type agree, and a block that changes from one class to the other is killed or undo-zeroed first.
- source: §"Data Architecture" "tion is necessary because certain bu er pool operations have to be performed when reusing a logged block"
- violation: A metadata fragment is allocated as elbb_bufData, or a freed logged block is reused as user data while a dirty logged buffer is still cached.

### grok-2:E30
- contract: Higher layers put in one equivalence class every set of still-active transactions on the same log that lock the same object, and they pass an active transaction as the second argument of the merge.
- source: §"Logging Architecture" "same object during their lifetime are merged into an equivalence class (EC). An EC has the property that"
- violation: Two transactions update or read-and-update the same metadata under different tlocks, or a caller merges a transaction from another aggregate or one that has already ended.

### grok-2:E31
- contract: The caller that starts a transaction ends it, and a thread holds at most one unnested transaction at a time.
- source: anode/block_alloc.c:1141 " * CAUTIONS -- This violates the basic rule that a single thread will not"
- violation: A vnode path returns without elbt_EndTran, or one thread starts a second unnested transaction while the first is still active.

### grok-2:E32
- contract: Callers keep each equivalence class small enough that every pending member's end-record reservation fits in the log.
- source: logbuf/log.c:138 " * length(aTranList) * (nested ? undoSize : fullSize) +"
- violation: A hot lock merges tens or hundreds of transactions into one class, and each ended member stays pending, holding an end reservation, until the last member ends.

### grok-2:E33
- contract: A caller that will hold several buffers at once reserves that many first, and the operator configures a buffer pool large enough for those reservations.
- source: logbuf/buffer.c:2306 " afsl_PAssert(code, ("Insufficient space for buffer reservation"));"
- violation: An anode path locks two blocks without elbb_Reserve, or the pool is smaller than the reservation the caller then requests.

### grok-2:E34
- contract: Callers log a new block with elbb_Initialize or CreateBlock, and they log an existing metadata block with the old bytes included.
- source: logbuf/buffer.c:1588 " * By initialization, we mean modification in the case where the old data"
- violation: A caller uses a full old-and-new record on a CreateBlock buffer, or uses Initialize on a block that already holds live metadata.

### grok-2:E35
- contract: A caller passes metadataOK to elbb_Kill only after the transaction that freed that metadata block has committed.
- source: logbuf/buffer.c:1360 " * buffers. This will only be true if the transaction that freed the"
- violation: The allocator kills a dirty logged buffer while the freeing transaction is still uncommitted, and the buffer's updates disappear from memory.

### grok-2:E36
- contract: The allocator does not hand a freed block out again until the freeing transaction has committed, and a committed zero-fill kill record is the newest record that may precede the block's next use.
- source: anode/block_alloc.c:565 " * return. Recently freed blocks are not okay if the transaction in which"
- violation: A newly allocated metadata or user block receives records while an older uncommitted update or an uncommitted zero-fill is still in the active log for that address.

### grok-2:E37
- contract: The layer that allocates a user-data block records an undo-zero for that byte range and ends that transaction only after the first write of the new data has completed, including when the virtual memory system writes the block outside the buffer pool.
- source: logbuf/buffer.c:2415 " * the specified range of bytes. This is to be used by the VM system for I/Os"
- violation: A pageout or a strategy write stores a newly allocated block without an undo-zero record, or it ends the undo-zero transaction before that write is durable.

### grok-2:E38
- contract: The caller of elbb_UndoZeroBuffer has finished writing the new bytes into the dirty buffer before the call, and the range lies inside that buffer.
- source: logbuf/buffer.c:2459 " * present. All updates to the dirty buffer have been done when this call"
- violation: The caller attaches the undo-zero and then keeps modifying the buffer, or the log cleans the buffer and ends the nested transaction before the new bytes are stored.

### grok-2:E39
- contract: After a modify, fill, or initialize, the caller uses the buffer pointer the call returns.
- source: logbuf/buffer.c:1415 " * cannot assume the buffer handle will not change across this call."
- violation: The caller keeps logging or releasing the pointer it passed in after the package has moved the block to a different buffer header.

### grok-2:E40
- contract: An fsync or any other call that promises durable metadata writes the file's dirty VM pages, then forces the log through that file's transaction before it returns.
- source: vnops/efs_vnodeops.c:1755 " /* Flush all buffers associated with the vnode and make sure metadata"
- violation: The vnode returns from fsync without vnvm_fsync, without epia_Fsync, or without elbb_LogForce of the vnode transaction, or the caller holds the vnode lock across the VM flush and the flush waits for that lock.

### grok-2:E41
- contract: The operating system calls the file system's sync often enough that committed dirty metadata is written and the active log is checkpointed about every T seconds.
- source: §"Recovery Time" "every T seconds, as is the case with Episode, then the active portion of the log can rise to include all the"
- violation: The update daemon is disabled, or efs_sync always finds its lock busy and never reaches elbb_SyncForce.

### grok-2:E42
- contract: A caller that needs a durable point for the outside world asks quiesce to commit, and any tool that reads the raw device does so only after that commit and the matching buffer flush.
- source: logbuf/tran.c:1210 " * the outside world, like vol_fsync. A third variant allows commit of"
- violation: A fileset export, move, or raw backup reads disk blocks while dirty logged buffers or uncommitted log records still exist, or it asks only for SERIALIZE when it needed COMMIT.

### grok-2:E43
- contract: Callers of elbb_Tune and elbl_Tune pass a pointer in the log package's address space.
- source: logbuf/buffer.c:873 " * Note that elbb_Tune assumes the address of value is in its address"
- violation: A system call passes a raw user pointer and the log stores a limit through it.

### grok-2:E44
- contract: The fast metadata modify path receives kernel addresses, and any user-address modify copies exactly the requested bytes or returns an error.
- source: logbuf/buffer.c:1703 " * assume along this code path that we never have user data (e.g. we"
- violation: A caller passes a user pointer to the fast path, or osi_copyin reports success after copying a different range.

### grok-2:E45
- contract: A higher layer holds the container lock across an anode metadata operation so two transactions do not update that container together.
- source: anode/anode.c:2175 " * LOCKS USED -- The container is assumed to be locked by a higher level to"
- violation: Two threads call epia_Write on the same anode without the vnode or container lock.

### grok-2:E46
- contract: One async_device object names an aggregate for the life of its buffer cache, and the compiler lays the device pointer and the block number out as one contiguous hash key with the device pointer first.
- source: logbuf/buffer.c:839 " * note that for this key to work, we assume that the device and"
- violation: A second device object is opened for the same disk, or a compiler inserts padding between adev and blockNum, so two cache entries alias or one block is looked up under the wrong key.

### grok-2:E47
- contract: The scheduler and the VM I/O daemon keep running the threads that end transactions, finish undo-zero I/O, and write dirty buffers while other threads wait for log space.
- source: logbuf/tran.c:1239 " * from the VM system which has its own Async daemon to complete I/O. We"
- violation: A high-priority thread spins waiting for a transaction while it holds the buffer or vnode lock the transaction needs, or the VM daemon that would end an undo-zero never runs.

### grok-2:E48
- contract: Block addresses passed into the log and into recovery name blocks the device can read and write.
- source: logbuf/recover.c:1319 " if (returnVal != 0) panic("ReadData: bad read");"
- violation: A caller or a damaged log record names a block past the end of the device or on a hole the driver rejects.

