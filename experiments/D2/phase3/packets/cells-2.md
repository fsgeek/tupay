# D2 judge packet 3 of 5 (cells, 2 of 3): Episode's log and recovery, against the sealed analysis

You are a judge. Work only from the text in this packet; do not read files, run commands or search.

Context: a component's log and recovery (`logbuf` in the Episode file system, OSF DCE 1.2.2) relies on contracts from the layers around it. Independent readers enumerated those contracts ("cells"); independent model authors then wrote TLA+ models and reported **findings**: violations of an obligation outside `logbuf` that break a stated guarantee of the log and recovery with the model's defences in place. A separate analysis, done before any of this and sealed, lists bugs, confirmed properties and an open item; it is given to you {SEALED_WHERE}. Items carry opaque ids; you are not told who wrote them. Packets are split by size by a stated rule; this one is part 3 of 5 (cells, 2 of 3).

Episode's criteria (fixed by Episode's steward 2026-10-26, before any list existed): a finding is a **match** for a sealed bug if it has the same violated contract, the same mechanism and the same class of effect; **partial** if it has the contract and one of the other two, or the right mechanism under a different contract; **no match** otherwise. A finding that claims a violation contradicting one of the sealed file's confirmed properties is **flagged** (name the property). A finding about the sealed file's open item is **unresolved**. A finding may match several bugs.

For **each cell**: does it name the violated contract that the sealed file records for some bug? Binary per cell; list the bugs if yes. A cell is a contract, not a finding; mechanism and effect do not matter here.

Answer schema: {"cells": [{"id": "C...", "names_contract_of": ["<sealed bug id>", ...], "reason": "<one sentence>"}]}  (empty list for no)

Answer with one JSON object only, as specified. Be concrete and brief; cite the sealed file's bug ids and the item's own words. Do not propose fixes. Disagreement with the sealed analysis is allowed: say so in `reason`.

## Cells

### C038
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

### C039
- contract: Callers keep each equivalence class small enough that every pending member's end-record reservation fits in the log.
- source: logbuf/log.c:138 " * length(aTranList) * (nested ? undoSize : fullSize) +"
- violation: A hot lock merges tens or hundreds of transactions into one class, and each ended member stays pending, holding an end reservation, until the last member ends.
- at-risk: G17 and G14 fail because the pending class fills the log, and a crash then aborts the whole class, including transactions that had already ended in memory.
- detectable: partly — the log-full path panics when the active region reaches the container; it does not report the class size as the cause.
- silent: 2 — the paper tells callers to keep classes short, and a large class under a hot directory is an occasional load spike rather than every-day operation.

### C040
- contract: A caller that needs a durable point for the outside world asks quiesce to commit, and any tool that reads the raw device does so only after that commit and the matching buffer flush.
- source: logbuf/tran.c:1210 " * the outside world, like vol_fsync. A third variant allows commit of"
- violation: A fileset export, move, or raw backup reads disk blocks while dirty logged buffers or uncommitted log records still exist, or it asks only for SERIALIZE when it needed COMMIT.
- at-risk: G18 and G1 fail for that reader because old-and-new logging is allowed to write uncommitted metadata, so the raw image is not a consistent file system until recovery or a committing quiesce.
- detectable: no — quiesce returns once the requested level is reached, and a raw read has no log check.
- silent: 2 — administrative copies of a live aggregate are occasional, and nothing reports that the raw image still needs the log.

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

### C042
- contract: Clients must request the persistence level they require and distinguish transaction completion from durable commitment.
- source: logbuf/tran.c:953 "2 -- don't return until transaction has completed. This ensures"
- violation: An fsync caller uses waitOK=2 or treats EndTran as proof that its end record reached disk.
- at-risk: G15, G23, G24, G25, G29: completion or pending membership does not establish crash persistence.
- detectable: partly — call arguments are observable, but logbuf cannot know which user-visible durability promise was made.
- silent: 2 — Similar-looking completion interfaces can be misused on uncommon paths.

### C043
- contract: Clients must pass live transaction IDs belonging to the intended device and stop adding updates after ending them.
- source: logbuf/log.c:1020 "afsl_Assert (dataLength <= tP->dev->blkSize);"
- violation: A client reuses a stale transaction handle, logs after EndTran, or modifies one device under another device’s transaction.
- at-risk: G2, G7, G42: updates can lack a valid lifetime or replay on the wrong aggregate.
- detectable: partly — lookup and status assertions catch some cases, but a recycled ID or plausible wrong device can evade them.
- silent: 1 — Correct API clients normally retain IDs only for the operation lifetime.

### C044
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

### C045
- contract: Clients must classify buffers as logged metadata or unlogged data correctly and restrict external requests to public buffer types.
- source: logbuf/logbuf.p.h:47 "users of this package are restricted to the first two cases"
- violation: A metadata block is read as elbb_bufData or an external caller requests internal log/recovery buffer treatment.
- at-risk: G4, G5, G42, G44: buffer write and discard rules can use the wrong logging policy.
- detectable: partly — enum validation can reject internal types, but logbuf cannot independently infer metadata ownership.
- silent: 2 — Classification errors on transition paths can be silent.

### C046
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

### C047
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

### C048
- contract: Callers requesting commit quiescence must arrange completion of dirty-buffer and VM undo-zero writes before waiting for their transactions.
- source: logbuf/tran.c:1254 " * all dirty buffers to be written. Any other undo zero transactions are"
- violation: A higher layer waits for undo-zero commit without scheduling the data writes that end those transactions.
- at-risk: G39, G46: quiescing can wait forever.
- detectable: yes — dirty buffers and unfinished undo-zero transactions expose the unmet prerequisite.
- silent: 1 — Incorrect quiesce ordering normally hangs visibly.

### C049
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

### C050
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

### C051
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

### C052
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

### C053
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

### C054
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

### C055
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

### C056
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

### C057
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

### C059
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

### C060
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

### C061
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

### C062
- contract: Code that runs during a kernel panic must not depend on starting further transactions once log-full handling has stopped retrying.
- source: logbuf/buffer.c:1762 " if (osi_IsKernelPanic() && ++nLoops == ELBB_MAX_PANIC_LOOP)"
- violation: Panic or crash-dump code keeps modifying metadata after elbb_StartTran returns failure, and a dirty buffer is then written without a new log record.
- at-risk: G5 and G7 fail because that buffer can reach disk with updates that are not in the log, so the next recovery cannot redo or undo them.
- detectable: partly — the start call returns an out-of-memory code, but a caller that ignores it and writes anyway gets no further check.
- silent: 1 — kernel panics are rare over a year, and the panic path usually stops issuing new metadata transactions after a few attempts.

### C063
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

### C064
- contract: The VM and higher vnode layers must serialize overlapping block I/O so that waiting for an in-transit block is not invalidated by another writer.
- source: anode/strategy.c:267 "transit again. The higher-level vnode locking should guarantee this."
- violation: A second writer starts I/O to a block after a waiter has passed its in-transit check.
- at-risk: G16, G31, G35 and correct user-data ordering: later writes may be overwritten by earlier completions.
- detectable: partly — in-transit instrumentation detects some races; the critical reentry window requires higher-layer knowledge.
- silent: 2 — Cross-path VM and volume-operation races can be timing-dependent and silent.

### C065
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

### C066
- contract: The kernel's device-block conversion addresses the same physical sectors the driver writes, and an Episode block is an integer number of those sectors.
- source: async/asevent.c:139 "#define ToBufferBlocks(adevice, ablock, aoffset) \"
- violation: DEV_BSIZE, abtodb, or btodb disagrees with the disk's sector size, so log and metadata I/O lands on the wrong addresses.
- at-risk: G1, G5, and G54 fail because the log and the home blocks recovery reads are not the blocks Episode wrote.
- detectable: partly — a wildly wrong address often returns an I/O error and panics a log read; an off-by-a-factor address on a large disk can succeed with unrelated bytes.
- silent: 1 — the SunOS and AIX ports the paper describes use one consistent DEV_BSIZE for the disk they mount.

### C067
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

### C068
- contract: Callers must check error and would-block returns before reporting successful persistence or using returned buffer contents.
- source: logbuf/tran.c:957 "RETURN CODES -- returns BUF_WOULDBLOCK only if waitOK is zero and the"
- violation: A caller ignores BUF_WOULDBLOCK from a nonwaiting force or returns success after a read/copy/I/O error.
- at-risk: G15, G23, G31, G40, G42: an unsuccessful operation does not establish the success guarantee the upper layer reports.
- detectable: partly — return codes and pending state are visible, but logbuf cannot know that a caller discarded an error.
- silent: 2 — Error-handling omissions can silently affect uncommon paths.

### C069
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

### C070
- contract: The async service must finish all transfers before reporting their event complete.
- source: logbuf/recover.c:1302 " returnVal = asevent_WaitEvent(ae);"
- violation: The callback runs while DMA still reads the buffer that logbuf then recycles.
- at-risk: G5, G55: the durable bytes can differ from the recorded or recovered bytes.
- detectable: partly — checksums may expose damaged log pages later.
- silent: 1 — Premature DMA completion is an unusual driver defect and often corrupts checksummed log pages.

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

### C072
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

### C073
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

### C074
- contract: setjmp and longjmp, and the kernel exception longjmp where it is still compiled in, restore the recovery catch point and abandon the failed pass.
- source: logbuf/recover.c:125 " * This assumes traditional semantics for an in-kernel setjmp/longjmp."
- violation: The C library or the kernel exception handler returns into a half-updated recovery structure, or it fails to jump, and recovery continues after RCVR_RAISE.
- at-risk: G8 and G50 fail because a detected bad page is then applied, or cleanup is skipped and a later pass uses freed record memory.
- detectable: no — a broken jump looks like a crash or a wrong repair, and the log package has no separate check that the jump happened.
- silent: 1 — the user-space C library on the paper's hosts provides ordinary setjmp, and a broken jump would be a porting fault rather than a yearly event.
