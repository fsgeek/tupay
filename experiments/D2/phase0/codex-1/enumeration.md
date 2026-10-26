# Environment contracts for Episode log and recovery

Scope: the paper and the released source, centered on `logbuf/`, with caller obligations traced into `anode/` and I/O services into `async/`. “Implicit” marks an inferred external obligation, not a claim that the quotation states it verbatim. Ratings estimate **unnoticed violations per year**, not severity or the frequency of the triggering operation; they are qualitative judgments, not measured rates. A detectable violation can still go unnoticed without the proposed instrumentation. Performance obligations are conditional on relying on the corresponding timing claim.

<!-- derives: BRIEF.md task and format; GUARANTEES.md G1–G63. No C/F clause or failure-model identifiers are supplied in this checkout; none are invented. Each entry derives from its cited source and names its relevant G identifiers. This is a read-only enumeration, not an outcome-bearing experiment, model, implementation, or paired test; no outcome-bearing run or commit is performed. -->

<!-- derives: E1; logbuf/recover.c:894; G5, G7, G23, G29, G30 -->
### E1
- contract: The storage stack must make a successfully completed log write durable across the crashes against which recovery is promised.
- source: logbuf/recover.c:894 "underlying system to really guarantee that a page is on disk"
- stated: stated
- violation: A controller acknowledges a log write while its only copy is in volatile cache, then power fails.
- at-risk: G5, G7, G23, G29, G30: metadata can reach disk without its undo information, or acknowledged commits can disappear.
- detectable: partly — rereads may expose loss, but a successful completion cannot prove power-loss durability.
- silent: 2 — Honest completion was the intended disk interface; volatile controller caches are a plausible silent exception.
- basis: general systems experience

<!-- derives: E2; logbuf/recover.c:746; G54 and G1 -->
### E2
- contract: The disk must write each sector atomically and correctly across a crash.
- source: logbuf/recover.c:746 "correctness/atomicity of each sector.  So if the log page did"
- stated: stated
- violation: A power interruption leaves a sector containing a mixture of its old and new contents.
- at-risk: G54 and G1: recovery may trust a torn header during head search or misidentify the clean restart state.
- detectable: partly — page checksums and structural checks detect some torn sectors; header search and restart records do not provide full protection.
- silent: 1 — Sector failure without an I/O error is rare on the paper’s intended disks.
- basis: general systems experience

<!-- derives: E3; logbuf/recover.c:755; G1, G6, G7, G20 -->
### E3
- contract: The storage stack must preserve completed writes until an explicitly authorized overwrite.
- source: logbuf/recover.c:755 "active log pages outside the in-transit window are really"
- stated: implicit
- violation: A completed active log page later develops an unreadable sector or silently loses bits.
- at-risk: G1, G6, G7, G20: the only surviving undo or redo image may be lost.
- detectable: partly — supported checksums detect many corruptions, but cannot reconstruct lost records.
- silent: 1 — Latent media damage without a reported error is rare but possible.
- basis: general systems experience

<!-- derives: E4; async/asevent.c:1126; G1, G31, G35, G40 -->
### E4
- contract: The storage stack must return the requested bytes and report failed or short I/O as an error.
- source: async/asevent.c:1126 "if (bp->b_flags & B_ERROR) {"
- stated: implicit
- violation: A driver returns success with a short transfer, wrong-sector read, or failed write while leaving B_ERROR clear.
- at-risk: G1, G31, G35, G40: success is interpreted as a complete transfer, so stale bytes or missing updates can survive recovery.
- detectable: partly — log checksums can catch bad reads; ordinary data blocks have no equivalent protection here.
- silent: 1 — Silent driver transfer errors are unusual on supported systems.
- basis: general systems experience

<!-- derives: E5; logbuf/recover.c:1343; G1, G2 -->
### E5
- contract: The device must confine each write to its addressed sectors and preserve unrelated bytes.
- source: logbuf/recover.c:1343 "writeBlock(&buf, returnVal);"
- stated: implicit
- violation: A firmware or DMA error writes a log page over a different metadata block.
- at-risk: G1, G2: value logging cannot restore unrelated damage for which it has no record.
- detectable: partly — later log or metadata validation may reveal damage, but address correctness is not independently verified.
- silent: 1 — Misdirected writes are rare latent hardware or driver failures.
- basis: general systems experience

<!-- derives: E6; logbuf/log.c:786; G23, G31, G35, G39, G40 -->
### E6
- contract: The asynchronous I/O service must eventually complete each accepted request and signal its event with the correct result.
- source: logbuf/log.c:786 "retval = asevent_WaitEvent(ae);"
- stated: implicit
- violation: An accepted disk write never invokes iodone, or signals the wrong event.
- at-risk: G23, G31, G35, G39, G40: forced writes or shutdown may wait forever or return before the intended I/O.
- detectable: partly — a timeout or outstanding-event monitor could notice a hang, but no universal bound proves failure.
- silent: 1 — Lost completions are rare and usually manifest as visible hangs.
- basis: general systems experience

<!-- derives: E7; logbuf/buffer.c:750; G2, G5, G13, G29 -->
### E7
- contract: The OS synchronization service must provide mutual exclusion and memory visibility for the logbuf locks.
- source: logbuf/buffer.c:750 "epi_mutex_init(&bufferLock, "buffer");"
- stated: implicit
- violation: An unsupported port implements a mutex without the required interprocessor memory ordering.
- at-risk: G2, G5, G13, G29: races can corrupt buffer contents, transaction lists, or log ordering.
- detectable: partly — assertions may catch damaged state, but subtle races can silently alter values.
- silent: 1 — Supported kernels ordinarily meet their locking interface.
- basis: general systems experience

<!-- derives: E8; logbuf/tran.c:1200; G23, G24, G32, G33, G39 -->
### E8
- contract: The OS sleep and wakeup primitives must atomically release the appropriate lock and avoid lost wakeups.
- source: logbuf/tran.c:1200 "elbt_TranUnlockAndSleep(tP,tP);"
- stated: implicit
- violation: A wakeup races with a non-atomic unlock-and-sleep operation and a forcing thread sleeps indefinitely.
- at-risk: G23, G24, G32, G33, G39: waiting callers can fail to finish despite the awaited transition.
- detectable: partly — blocked threads are observable, though recovery cannot distinguish slow work from a lost wakeup.
- silent: 1 — Lost wakeups indicate an unusual portability-layer defect.
- basis: general systems experience

<!-- derives: E9; logbuf/tran.c:1239; G23, G28, G33, G39 -->
### E9
- contract: The execution environment must eventually schedule threads and I/O workers needed to end transactions and write buffers.
- source: logbuf/tran.c:1239 "from the VM system which has its own Async daemon to complete I/O.  We"
- stated: implicit
- violation: The VM write daemon is disabled or starved while commit waits for its undo-zero transaction.
- at-risk: G23, G28, G33, G39: log space and completion depend on this forward progress.
- detectable: partly — outstanding work and starvation can be monitored, without a definitive finite deadline.
- silent: 2 — Temporary worker starvation is plausible, persistent silent starvation less common.
- basis: general systems experience

<!-- derives: E10; logbuf/recover.c:1031; G1, G9, G11 -->
### E10
- contract: The memory service must supply enough allocation capacity for the active log and recovery bookkeeping.
- source: logbuf/recover.c:1031 "TODO: is this a safe assumption ---"
- stated: implicit
- violation: Recovery on a memory-constrained host cannot allocate all active log pages and record structures.
- at-risk: G1, G9, G11: recovery cannot finish or meet its timing claim; allocation failure can panic.
- detectable: yes — allocation failures and resource accounting expose exhaustion.
- silent: 1 — Exhaustion generally produces an explicit failure rather than remaining silent.
- basis: source

<!-- derives: E11; logbuf/recover.c:1364; G5, G7, G31 -->
### E11
- contract: The OS pinning and DMA services must keep I/O memory resident and mapped to the supplied bytes until completion.
- source: logbuf/recover.c:1364 "logbuf_pin(data, dev->blkSize);"
- stated: implicit
- violation: A port treats pinning as a no-op where DMA requires pinned memory and a page is reclaimed during I/O.
- at-risk: G5, G7, G31: disk transfers can contain different memory or fail after their buffers move.
- detectable: partly — faults or I/O errors expose some cases; valid but wrong transferred bytes may escape.
- silent: 1 — Correctly supported ports provide this service; silent failure is exceptional.
- basis: general systems experience

<!-- derives: E12; logbuf/log.c:2602; G17, G28 -->
### E12
- contract: The CPU and compiler must make the shared 32-bit tuning assignments atomic to readers.
- source: logbuf/log.c:2602 "a 32 bit quantity is atomic w.r.t. all readers."
- stated: stated
- violation: A port implements a shared tuning store as two separately observable halfword stores.
- at-risk: G17, G28: torn reservation or capacity limits can invalidate admission calculations or block progress.
- detectable: partly — limits can be sanity checked, but a transient torn read may leave no evidence.
- silent: 1 — Aligned 32-bit stores on the described machines normally meet the assumption.
- basis: source

<!-- derives: E13; logbuf/logrec.h:227; G6, G7, G47, G54 -->
### E13
- contract: A port must preserve the alignment, integer widths, byte order, and structure layout expected by the native on-disk log format.
- source: logbuf/logrec.h:227 "pointers rather than bcopy (remember we want things to be fast.)"
- stated: implicit
- violation: An aggregate is recovered using a build with a different endian order or daddr_t layout and no format conversion.
- at-risk: G6, G7, G47, G54: headers, offsets, and values are decoded differently or fault.
- detectable: partly — magic, checksums, and assertions catch many incompatible layouts, but do not establish semantic compatibility.
- silent: 1 — Same-platform recovery is normal; unsupported cross-platform use is rare.
- basis: general systems experience

<!-- derives: E14; logbuf/logrec.h:232; G1 and log service availability -->
### E14
- contract: A port must ensure that pointer alignment calculations do not truncate addresses and that cast log records meet CPU alignment requirements.
- source: logbuf/logrec.h:232 "a power-of-two. The use of (unsigned) may not be strictly correct"
- stated: implicit
- violation: The code is built with 64-bit pointers and 32-bit unsigned, and ALIGN discards the upper address bits.
- at-risk: G1 and log service availability: memory accesses can fault or target unrelated storage.
- detectable: partly — faults or address checks detect many cases, but aliasing can corrupt memory silently.
- silent: 1 — The paper’s 32-bit machines meet this condition; an unadapted later port may not.
- basis: source

<!-- derives: E15; logbuf/buffer.c:840; G5, G40, G42 -->
### E15
- contract: A port must preserve the contiguous device-pointer and block-number layout used as the buffer address hash key.
- source: logbuf/buffer.c:840 "block # fields are contiguous, with the device *first*.  We"
- stated: stated
- violation: A compiler inserts padding between adev and blockNum so the fixed-length key omits part of the block number.
- at-risk: G5, G40, G42: the cache can confuse or fail to locate block identities.
- detectable: partly — layout assertions could detect this at initialization; runtime collisions need not identify the cause.
- silent: 1 — The supported ABI normally supplies the expected layout.
- basis: source

<!-- derives: E16; logbuf/log.c:863; G17, G30, G54 -->
### E16
- contract: Device registration must supply a supported power-of-two block size and an accurate matching logBlkSize.
- source: logbuf/log.c:863 "afsl_MBZ(blkSize & 1023); /* must be power-of-two >= 1K */"
- stated: stated
- violation: A registered device advertises 3072-byte blocks or a logBlkSize inconsistent with blkSize.
- at-risk: G17, G30, G54: shifts, reservations, offsets, and transfer sizes no longer describe the same blocks.
- detectable: partly — size assertions reject some invalid sizes, but the quoted bitmask alone does not establish a power of two.
- silent: 1 — Normal device setup uses supported geometry.
- basis: source

<!-- derives: E17; logbuf/logbuf.p.h:416; G42, G54 -->
### E17
- contract: Device registration must keep block sizes within the buffer and record-offset limits supported by this build.
- source: logbuf/logbuf.p.h:416 "#define BUF_MAXBUFSIZE  (64 * BUF_MINBLKSIZE) /* largest buffer size */"
- stated: implicit
- violation: An operator or port registers blocks larger than the buffer maximum or representable record offsets.
- at-risk: G42, G54: allocations and 16-bit record offsets cannot faithfully represent the block.
- detectable: partly — buffer-pool and size checks can reject configurations; unchecked truncation remains possible.
- silent: 1 — The paper uses ordinary 8K blocks, well within these limits.
- basis: source

<!-- derives: E18; logbuf/buffer.c:845; G1, G40, G42 -->
### E18
- contract: The device layer must preserve a stable unique device identity and physical block mapping for the lifetime of cached buffers and transactions.
- source: logbuf/buffer.c:845 "sizeof(async_device_t *) +"
- stated: implicit
- violation: A device object is recycled for a different partition while old cache entries still use its pointer.
- at-risk: G1, G40, G42: cached data and log records can be applied to the wrong storage.
- detectable: partly — identity and lifetime instrumentation could detect reuse, but ordinary block I/O cannot establish it.
- silent: 1 — Normal aggregate open and close protocols avoid silent identity reuse.
- basis: general systems experience

<!-- derives: E19; logbuf/recover.c:983; G1, G6, G7, G54 -->
### E19
- contract: Aggregate setup must supply the complete log-block array in its original circular order and associate it with the correct data device.
- source: logbuf/recover.c:983 "/* guarantee the caller described the log properly */"
- stated: stated
- violation: Recovery receives a reordered block list, a truncated list, or another aggregate’s data device.
- at-risk: G1, G6, G7, G54: head search or replay addresses the wrong history or metadata.
- detectable: partly — page-number and bounds checks catch many array errors; a plausible wrong aggregate may evade them.
- silent: 1 — The aggregate layer normally reconstructs this mapping consistently.
- basis: source

<!-- derives: E20; §"Data Architecture"; G20, G21, G54 -->
### E20
- contract: The allocator and administrator must reserve log blocks exclusively and keep their addresses and log length fixed during normal logging.
- source: §"Data Architecture" "The log container does not grow or shrink"
- stated: implicit
- violation: A live resize, relocation, or overlapping allocation lets file data overwrite active log pages.
- at-risk: G20, G21, G54: retained history and circular page numbering cease to describe persistent storage.
- detectable: partly — checksum and page-number failures may reveal damage, after recovery information is already lost.
- silent: 1 — The source’s normal initialization and allocation rules avoid live log resizing.
- basis: source

<!-- derives: E21; logbuf/log.c:848; G17, G28 -->
### E21
- contract: Aggregate creation must allocate at least the minimum log space required for its block size and intended admitted workload.
- source: logbuf/log.c:848 "minSize = (load * elbl_MinTranReservation(dP->blkSize)) +"
- stated: implicit
- violation: An administrator constructs an undersized log or chooses a minimum supporting too little concurrent work.
- at-risk: G17, G28: initialization may reject the log, or operations cannot obtain useful admission capacity.
- detectable: yes — minimum-size checks and observed admission pressure expose inadequate sizing.
- silent: 1 — An undersized log usually generates a visible rejection or stall.
- basis: source

<!-- derives: E22; logbuf/tran.c:177; G2, G13, G28 -->
### E22
- contract: Initialization callers must serialize first-time package initialization before concurrent use.
- source: logbuf/tran.c:177 "Locks: assumes no locking (single-threaded at init time).  Call is"
- stated: stated
- violation: Two mount threads enter first-time transaction initialization concurrently.
- at-risk: G2, G13, G28: lock and free-list initialization can race and lose or duplicate state.
- detectable: partly — initialization guards detect some repeats but do not by themselves serialize racing callers.
- silent: 1 — Kernel startup ordinarily initializes these services once.
- basis: source

<!-- derives: E23; logbuf/log.c:878; G1, G63 -->
### E23
- contract: Log-creation callers must exclude all other activity on that device while creating its log.
- source: logbuf/log.c:878 "Locking: This code presumes no other thread is calling for this"
- stated: stated
- violation: A formatting utility creates the log while the filesystem still has active users.
- at-risk: G1, G63: zeroing the log can destroy active undo and redo history.
- detectable: partly — aggregate mount exclusion can detect use, but log creation cannot see every external writer.
- silent: 1 — Normal tools format offline.
- basis: source

<!-- derives: E24; logbuf/log.c:880; G63 and initialization availability -->
### E24
- contract: Log-creation callers must enter without holding buffer-package locks that creation needs.
- source: logbuf/log.c:880 "I/O, it presumes locks are not held in the buffer package."
- stated: stated
- violation: A caller creates a log while retaining the buffer lock needed by CreateBlock.
- at-risk: G63 and initialization availability: recursive lock acquisition can deadlock creation.
- detectable: partly — lock ownership tracking can expose the cycle.
- silent: 1 — Normal initialization follows the documented lock convention.
- basis: source

<!-- derives: E25; logbuf/recover.c:2374; G1, G8, G57, G58 -->
### E25
- contract: Mount and recovery orchestration must run user-space recovery for a dirty log before allowing ordinary filesystem access.
- source: logbuf/recover.c:2374 "return RCVR_MUSTRCVR; /* no kernel recovery anymore */"
- stated: implicit
- violation: A mount path ignores RCVR_MUSTRCVR and serves a dirty aggregate.
- at-risk: G1, G8, G57, G58: uncommitted updates remain and committed updates may be absent.
- detectable: yes — dirty-log inspection and the explicit return code identify the need for recovery.
- silent: 1 — Bypassing a visible mount error is unusual.
- basis: source

<!-- derives: E26; logbuf/recover.c:505; G1, G50, G55 -->
### E26
- contract: Recovery orchestration must exclude concurrent filesystem, VM, raw-device, and administrative writes to the recovered aggregate and log.
- source: logbuf/recover.c:505 "AdjustDisk(diskHash, dP, &allocList, rcvr_env);"
- stated: implicit
- violation: A mounted filesystem changes a metadata block while user-space recovery reads and rewrites it.
- at-risk: G1, G50, G55: recovery can overwrite newer changes or declare clean a state it never analyzed.
- detectable: partly — mount and device exclusion can be checked; recovery has no version check for every competing writer.
- silent: 1 — Recovery normally runs offline.
- basis: general systems experience

<!-- derives: E27; logbuf/buffer.c:1839; G1, G55, G60 -->
### E27
- contract: Callers must present a clean buffer cache when initializing a log that may require recovery.
- source: logbuf/buffer.c:1839 "buffers were dirty when elbb_LogInit was called."
- stated: stated
- violation: A caller dirties cached metadata before LogInit, then successful recovery invalidates or writes that cache.
- at-risk: G1, G55, G60: stale dirty cache contents can overwrite recovered blocks.
- detectable: yes — dirty-buffer state is inspectable at entry.
- silent: 1 — Normal mount initialization precedes metadata updates.
- basis: source

<!-- derives: E28; logbuf/log.c:737; G1, G59, G60 -->
### E28
- contract: Callers must handle RCVR_RECOVERED by discarding stale higher-layer state and retrying initialization against recovered disk contents.
- source: logbuf/log.c:737 "return RCVR_RECOVERED;	/* so upper levels can clear buffers */"
- stated: stated
- violation: The aggregate layer treats RCVR_RECOVERED as ordinary success and retains anodes loaded before recovery.
- at-risk: G1, G59, G60: later operations can reintroduce stale state despite a recovered buffer pool.
- detectable: partly — return-code handling is visible, but stale derived caches are not all visible to logbuf.
- silent: 1 — The supplied aggregate code has explicit retry handling.
- basis: source

<!-- derives: E29; §"Component Architecture"; G1, G11 -->
### E29
- contract: Operators must invoke salvage rather than assume successful log recovery when hard errors have destroyed critical metadata or needed history.
- source: §"Component Architecture" "In such cases, the Episode salvager utility needs to be run; the salvager's performance"
- stated: stated
- violation: After a failed recovery with unreadable active log pages, an operator forces the aggregate online without salvage.
- at-risk: G1, G11: log replay alone cannot restore lost information, and salvage loses the fast-recovery timing benefit.
- detectable: yes — recovery errors and I/O failures identify this case, although undetected corruption can escape.
- silent: 1 — Hard errors and recovery failure normally produce visible errors.
- basis: text

<!-- derives: E30; §"Component Architecture"; G1–G8, especially G4 and G42 -->
### E30
- contract: Upper filesystem layers must bracket every consistency-relevant metadata change in the appropriate logged transaction.
- source: §"Component Architecture" "By making all le system meta-data modi cations within atomic transactions, the"
- stated: stated
- violation: A directory or bitmap update bypasses logging, uses a null transaction, or requests an unlogged modification.
- at-risk: G1–G8, especially G4 and G42: recovery has no old/new record for that change.
- detectable: partly — API instrumentation could detect bypasses, but raw stores are not necessarily visible to logbuf.
- silent: 2 — Rare error paths and integration mistakes can omit logging without an immediate error.
- basis: general systems experience

<!-- derives: E31; §"Logging Architecture"; G1, G19 -->
### E31
- contract: Upper layers must construct transactions whose committed boundaries preserve filesystem invariants.
- source: §"Logging Architecture" "After each transaction, the le system is consistent, if"
- stated: implicit
- violation: A large truncate commits a bitmap free before removing the last reachable pointer in another independent transaction.
- at-risk: G1, G19: perfect atomic replay still restores a logically inconsistent committed state.
- detectable: partly — a full invariant checker could detect the result, but logbuf lacks filesystem semantics.
- silent: 2 — Unusual multi-step operations can contain latent boundary mistakes.
- basis: general systems experience

<!-- derives: E32; logbuf/log.c:1684; G17, G28 -->
### E32
- contract: Transaction clients must bound each ordinary transaction’s log consumption by the reservation assumed at admission.
- source: logbuf/log.c:1684 "Each running transaction is assumed to need MAX_TRAN_SIZE of log"
- stated: stated
- violation: A vnode operation logs an unbounded large truncate in one transaction.
- at-risk: G17, G28: outstanding work can exceed the capacity reserved for it and exhaust the circular log.
- detectable: yes — reservation accounting can compare actual consumption with the admitted bound.
- silent: 1 — The paper calls this a programming error, and overrun usually produces a visible stall or assertion.
- basis: source

<!-- derives: E33; §"Logging Architecture"; G9, G20, G23, G28, G39 -->
### E33
- contract: Transaction clients must end their transactions in bounded time and release resources needed by other admitted transactions.
- source: §"Logging Architecture" "Transactions that run too long or modify too much data represent"
- stated: stated
- violation: An error path leaks an active transaction or leaves it blocked forever holding an object lock.
- at-risk: G9, G20, G23, G28, G39: old history cannot be reclaimed and forcing or shutdown may never finish.
- detectable: partly — age and active-transaction monitoring can expose a suspect transaction, without a universal deadline.
- silent: 2 — Leaked transactions on uncommon failure paths can remain unnoticed until pressure develops.
- basis: general systems experience

<!-- derives: E34; logbuf/log.c:1674; G17, G27 -->
### E34
- contract: Nested-transaction callers must keep the new transaction plus its parent within the reservation for a single ordinary transaction.
- source: logbuf/log.c:1674 "transaction size plus old transaction size will be less than the"
- stated: stated
- violation: A caller supplies oldTranId to bypass admission and then logs a second full-sized operation.
- at-risk: G17, G27: nonblocking nested admission is safe only under the combined size bound.
- detectable: yes — parent and nested log-consumption accounting could detect excess.
- silent: 1 — Supplied nesting is intended for small undo-zero work.
- basis: source

<!-- derives: E35; logbuf/log.c:1020; G2, G7, G42 -->
### E35
- contract: Clients must pass live transaction IDs belonging to the intended device and stop adding updates after ending them.
- source: logbuf/log.c:1020 "afsl_Assert (dataLength <= tP->dev->blkSize);"
- stated: implicit
- violation: A client reuses a stale transaction handle, logs after EndTran, or modifies one device under another device’s transaction.
- at-risk: G2, G7, G42: updates can lack a valid lifetime or replay on the wrong aggregate.
- detectable: partly — lookup and status assertions catch some cases, but a recycled ID or plausible wrong device can evade them.
- silent: 1 — Correct API clients normally retain IDs only for the operation lifetime.
- basis: general systems experience

<!-- derives: E36; anode/tlock.h:20; G1, G12–G14 -->
### E36
- contract: Upper layers must use transactional object locking and report every intertransaction read/write dependency that requires equivalence-class merging.
- source: anode/tlock.h:20 "the same lock, they must be put in the same equivalence class.  To minimize"
- stated: stated
- violation: A transaction reads another’s uncommitted bitmap or anode through a nontransactional lock and commits independently.
- at-risk: G1, G12–G14: a dependent update may survive while the state it relied on is undone.
- detectable: partly — dependency instrumentation could detect missing merges; logbuf cannot infer semantic reads.
- silent: 2 — Rare nontransactional access paths can miss a merge without an immediate failure.
- basis: general systems experience

<!-- derives: E37; anode/tlock.c:99; G2, G4, G42 -->
### E37
- contract: Callers must serialize access to shared metadata objects while their values are read or changed.
- source: anode/tlock.c:99 "lock_ObtainWrite_r (&tlock->lock);"
- stated: implicit
- violation: Two callers update overlapping anode bytes without holding the object’s write lock.
- at-risk: G2, G4, G42: old values or new values can describe interleaved changes rather than either operation.
- detectable: partly — lock checking can expose missing ownership, but logbuf’s internal lock does not establish object semantics.
- silent: 2 — Uncommon access paths can bypass object locking silently.
- basis: general systems experience

<!-- derives: E38; logbuf/tran.c:642; G13, G14, G26 -->
### E38
- contract: Callers merging equivalence classes must provide an active second transaction.
- source: logbuf/tran.c:642 "second tran must be active."
- stated: stated
- violation: A caller invokes ECMerge after the current transaction has ended or committed.
- at-risk: G13, G14, G26: a previously committed class cannot retroactively share atomic fate with new work.
- detectable: yes — ECMerge checks the second transaction’s activity.
- silent: 1 — The explicit assertion normally makes misuse visible.
- basis: source

<!-- derives: E39; anode/tlock.c:53; G13, G24 -->
### E39
- contract: Callers that destroy or recycle transactional lock objects must serialize their remembered transaction before reusing the lock identity.
- source: anode/tlock.c:53 "code = elbb_LogForce(*transP, 2/*complete*/);"
- stated: implicit
- violation: A remembered transaction ID survives lock destruction and is associated with an unrelated object at the same address.
- at-risk: G13, G24: dependencies can be lost or attached to the wrong object.
- detectable: partly — lifecycle instrumentation can detect reuse, but logbuf sees only transaction IDs.
- silent: 1 — The supplied destroy/recycle helpers perform this synchronization.
- basis: source

<!-- derives: E40; logbuf/tran.c:1313; G23, G24, G32, G33, G39 -->
### E40
- contract: Callers waiting for transaction completion must hold no active transaction whose progress can depend on that wait.
- source: logbuf/tran.c:1313 "CAUTIONS -- The calling thread must not be holding any active transactions."
- stated: stated
- violation: A thread forces a transaction in its own unfinished equivalence class while retaining an active member.
- at-risk: G23, G24, G32, G33, G39: the caller can wait for completion that only it can enable.
- detectable: partly — per-thread transaction and wait-graph tracking could identify the cycle.
- silent: 1 — These mistakes usually become visible deadlocks.
- basis: source

<!-- derives: E41; logbuf/buffer.c:2194; G28 and log service availability -->
### E41
- contract: Callers must arrange multi-buffer reservations before taking a path that holds several buffers simultaneously.
- source: logbuf/buffer.c:2194 "		buffers simultaneously; this avoids deadlock."
- stated: stated
- violation: Many threads each retain one buffer and wait for a second without reserving enough pool space.
- at-risk: G28 and log service availability: no thread can finish and release the buffers required for progress.
- detectable: partly — reservation ownership and wait graphs can expose the resource cycle.
- silent: 1 — Buffer exhaustion typically turns the error into an observable hang.
- basis: source

<!-- derives: E42; logbuf/tran.c:553; G37, G39, G55 -->
### E42
- contract: Shutdown callers must stop new aggregate activity and synchronize access before closing the log.
- source: logbuf/tran.c:553 "levels have properly synchronized access to this aggregate."
- stated: stated
- violation: A close races with a new StartTran or VM dirtying after shutdown has sampled active work.
- at-risk: G37, G39, G55: the restart record can declare clean while new changes are not covered.
- detectable: partly — aggregate activity counts can detect some races, but logbuf cannot fence every external producer.
- silent: 1 — Normal unmount protocols exclude new activity.
- basis: source

<!-- derives: E43; logbuf/tran.c:953; G15, G23, G24, G25, G29 -->
### E43
- contract: Clients must request the persistence level they require and distinguish transaction completion from durable commitment.
- source: logbuf/tran.c:953 "2 -- don't return until transaction has completed.  This ensures"
- stated: stated
- violation: An fsync caller uses waitOK=2 or treats EndTran as proof that its end record reached disk.
- at-risk: G15, G23, G24, G25, G29: completion or pending membership does not establish crash persistence.
- detectable: partly — call arguments are observable, but logbuf cannot know which user-visible durability promise was made.
- silent: 2 — Similar-looking completion interfaces can be misused on uncommon paths.
- basis: general systems experience

<!-- derives: E44; logbuf/logbuf.p.h:64; G15, G31, G35 -->
### E44
- contract: Clients must choose a write-back mode that waits for data completion when they promise synchronous persistence.
- source: logbuf/logbuf.p.h:64 "elbb_syncLog, /* force write log, schedule buffer write, don't wait"
- stated: stated
- violation: An upper layer returns synchronous success after elbb_syncLog or elbb_async while data is still in transit.
- at-risk: G15, G31, G35: these weaker modes do not imply the data buffer was written on return.
- detectable: partly — pending I/O is observable, but the caller’s intended external promise is not.
- silent: 2 — Confusing log synchronization with data synchronization is a plausible silent integration error.
- basis: general systems experience

<!-- derives: E45; logbuf/buffer.c:2019; G15, G40 -->
### E45
- contract: Fsync clients must tag every relevant cached buffer with the correct file handle or provide the complete correct block list.
- source: logbuf/buffer.c:2019 "buffers to write out.  Either a magic value is used to tag each"
- stated: stated
- violation: A metadata or data buffer is omitted from the file’s tag chain or explicit block list.
- at-risk: G15, G40: FsyncForce writes only the selected buffers and can return with omitted updates dirty.
- detectable: partly — comparing selection against higher-level ownership can expose omissions; logbuf cannot derive that ownership.
- silent: 2 — Tracking omissions can remain silent until a crash exposes missing data.
- basis: general systems experience

<!-- derives: E46; logbuf/logbuf.p.h:335; G15, G35 -->
### E46
- contract: VM integration must flush its own dirty pages as part of a filesystem-level synchronization promise.
- source: logbuf/logbuf.p.h:335 "WRITE -- schedules all dirty buffers containing user data."
- stated: implicit
- violation: An fsync implementation flushes only logbuf buffers while dirty mapped file pages remain solely in VM.
- at-risk: G15, G35: logbuf cache completion alone does not persist user data outside that cache.
- detectable: partly — VM dirty-page enumeration can detect pending writes, but logbuf cannot inspect an independent cache.
- silent: 2 — Separate cache coordination is a plausible source of silent durability gaps.
- basis: general systems experience

<!-- derives: E47; logbuf/buffer.c:1432; G28, G40, G42 -->
### E47
- contract: Clients must retain valid buffer references, obey write access requirements, and release every acquired reference.
- source: logbuf/buffer.c:1432 "afsl_Assert(bufferIsWrite(bP) && (bP->refCount > 0));"
- stated: stated
- violation: A caller modifies an unreferenced buffer after recycling, or leaks held references until the pool cannot reclaim space.
- at-risk: G28, G40, G42: wrong-buffer access or unreclaimable buffers can corrupt updates or stop progress.
- detectable: partly — reference and flag assertions catch some cases, but balanced counters alone do not establish ownership.
- silent: 1 — Many such API mistakes produce assertions or hangs.
- basis: source

<!-- derives: E48; logbuf/buffer.c:1415; G42 -->
### E48
- contract: Modification callers must use the returned replacement buffer handle after operations that can replace the original.
- source: logbuf/buffer.c:1415 "cannot assume the buffer handle will not change across this call."
- stated: stated
- violation: A client ignores nbP and continues modifying or releasing the previous buffer after log-full handling replaces it.
- at-risk: G42: subsequent updates can target stale storage or the wrong buffer identity.
- detectable: partly — generation or reference tracking could detect stale handles; a plausible reused pointer may pass checks.
- silent: 1 — Supplied call patterns normally propagate the returned handle.
- basis: source

<!-- derives: E49; logbuf/buffer.c:1474; G4, G42 -->
### E49
- contract: Callers must keep modification byte ranges within the addressed block and supply accessible data in the declared address space.
- source: logbuf/buffer.c:1474 "retval = osi_copyin_r(newData, bP->data + offset, newDataLen);"
- stated: implicit
- violation: A client supplies offset plus length beyond the block, an invalid source pointer, or USER bytes labeled SYS.
- at-risk: G4, G42: copies can fault, overwrite adjacent memory, or log bytes different from those installed.
- detectable: partly — bounds and copyin validation can catch some misuse, but not valid wrong pointers.
- silent: 1 — Ordinary internal callers use bounded kernel buffers.
- basis: source

<!-- derives: E50; logbuf/buffer.c:1456; G4, G7, G42 -->
### E50
- contract: Callers must keep new-data bytes stable across logging and copying them into the destination buffer.
- source: logbuf/buffer.c:1456 "LogWrite(tranId, LOGREC_DATA,  newDataLen, offset, bP, newData,"
- stated: implicit
- violation: A concurrent thread changes newData after LogWrite records it but before LOGCOPY installs it.
- at-risk: G4, G7, G42: recovered new data differs from the live modification that was acknowledged.
- detectable: partly — snapshot comparison could detect a race, but ordinary logging performs no independent source-version check.
- silent: 2 — Shared or user-controlled source memory can change silently unless callers stabilize it.
- basis: general systems experience

<!-- derives: E51; logbuf/buffer.c:970; G1 and additional source-implied confidentiality/correct-block-content guarantee -->
### E51
- contract: Callers must treat no-read buffer allocation as requiring initialization of every byte they will expose or preserve.
- source: logbuf/buffer.c:970 "(1) Just allocate a buffer (for overwriting an entire disk block."
- stated: stated
- violation: CreateBlock is followed by a partial overwrite and the remaining recycled memory is written as file contents.
- at-risk: G1 and additional source-implied confidentiality/correct-block-content guarantee: unwritten bytes need not contain valid disk data or zeros.
- detectable: partly — byte-initialization tracking could detect uninitialized regions; ordinary dirty flags cannot.
- silent: 2 — Partial initialization can expose stale bytes without any I/O error.
- basis: general systems experience

<!-- derives: E52; logbuf/buffer.c:1589; G3, G6, G43 -->
### E52
- contract: Callers may omit old-value logging only for genuinely new storage whose old contents need not be restored after abort.
- source: logbuf/buffer.c:1589 "do not have to be logged, i.e. the buffer was created by CreateBlock."
- stated: stated
- violation: Initialize or Fill with saveOld=false is used on reachable preexisting metadata.
- at-risk: G3, G6, G43: recovery cannot undo the lost previous contents.
- detectable: partly — allocation-generation tracking could verify newness, but logbuf does not know reachability.
- silent: 2 — Misclassifying a reused block can stay invisible until abort or recovery.
- basis: general systems experience

<!-- derives: E53; logbuf/logbuf.p.h:47; G4, G5, G42, G44 -->
### E53
- contract: Clients must classify buffers as logged metadata or unlogged data correctly and restrict external requests to public buffer types.
- source: logbuf/logbuf.p.h:47 "users of this package are restricted to the first two cases"
- stated: stated
- violation: A metadata block is read as elbb_bufData or an external caller requests internal log/recovery buffer treatment.
- at-risk: G4, G5, G42, G44: buffer write and discard rules can use the wrong logging policy.
- detectable: partly — enum validation can reject internal types, but logbuf cannot independently infer metadata ownership.
- silent: 2 — Classification errors on transition paths can be silent.
- basis: general systems experience

<!-- derives: E54; logbuf/buffer.c:1361; G1, G51–G53 -->
### E54
- contract: Block allocation must not reuse freed metadata for unlogged data until the freeing transaction and its prior dependencies have committed.
- source: logbuf/buffer.c:1361 "metadata block has committed, which implies that all transactions that"
- stated: stated
- violation: A block becomes file data while an earlier metadata transaction on that block can still be undone.
- at-risk: G1, G51–G53: old metadata replay can overwrite user data or recovery must reject the conflicting history.
- detectable: partly — kill-record analysis can raise RCVR_METADATA or RCVR_USERDATA; not every conflict is necessarily represented.
- silent: 2 — Reuse ordering errors can remain latent until a crash.
- basis: general systems experience

<!-- derives: E55; §"Data Architecture"; G1, G16, G51 -->
### E55
- contract: Block reuse must invalidate or safely write the prior cached incarnation before exposing a new logged or unlogged incarnation.
- source: §"Data Architecture" "tion is necessary because certain bu er pool operations have to be performed when reusing a logged block"
- stated: stated
- violation: A freed dirty metadata buffer remains cached while the same physical block is allocated as user data.
- at-risk: G1, G16, G51: a later cache write or read can revive stale contents over the new owner’s data.
- detectable: partly — cache identity and allocation-generation checks can detect reuse, but physical block keys alone do not distinguish incarnations.
- silent: 2 — Logged/unlogged transitions are uncommon paths where omissions can stay silent.
- basis: general systems experience

<!-- derives: E56; logbuf/buffer.c:1359; G21, G22, G44 -->
### E56
- contract: Callers may set metadataOK on Kill only after the transaction freeing that metadata has committed.
- source: logbuf/buffer.c:1359 "PARAMETERS -- metadataOK is true if it is safe to kill dirty metadata"
- stated: stated
- violation: An allocator passes metadataOK=1 merely because a free was issued, before that free commits.
- at-risk: G21, G22, G44: discarding the dirty buffer can retire the only committed state still needed if the free is undone.
- detectable: partly — a transaction-aware allocator can verify the freeing commit, but Kill receives only the caller’s boolean.
- silent: 2 — A false safety assertion can silently bypass the discard protection.
- basis: general systems experience

<!-- derives: E57; §"Logging Architecture"; G16, G45, G46 -->
### E57
- contract: Allocation and VM clients must establish undo-zero coverage for every newly exposed data byte before allocation can leave stale contents visible after a crash.
- source: §"Logging Architecture" "problem by starting another transaction when the block is allocated, and ending it when the rst write"
- stated: stated
- violation: A new block or fragment is linked into a file without the special first-write transaction for part of its contents.
- at-risk: G16, G45, G46: an incomplete first write can reveal the block’s former owner’s bytes.
- detectable: partly — allocation-to-coverage instrumentation could detect holes; logbuf cannot infer allocations outside its API.
- silent: 2 — Missing first-write coverage can remain silent through normal operation.
- basis: general systems experience

<!-- derives: E58; logbuf/buffer.c:2416; G16, G45 -->
### E58
- contract: VM clients doing I/O outside the buffer system must provide the correct device, block range, and live transaction to UndoZero.
- source: logbuf/buffer.c:2416 "that do not use the buffer system.  It is expected that this would not be"
- stated: stated
- violation: The VM reports the wrong offset, omits the last block, or supplies a null transaction for a newly allocated extent.
- at-risk: G16, G45: replay zeroes an incorrect range or leaves stale bytes uncovered.
- detectable: partly — null and range checks catch some errors, but the intended VM extent is external information.
- silent: 2 — Range translation mistakes can stay hidden until a crash.
- basis: general systems experience

<!-- derives: E59; §"Logging Architecture"; G16, G45 -->
### E59
- contract: VM and allocation clients must end undo-zero transactions only after the covered first write has successfully reached disk.
- source: §"Logging Architecture" "to it completes. If the system crashes and the transaction aborts, the recovery procedure for this special"
- stated: stated
- violation: A VM client ends its transaction on write submission or after a failed first write.
- at-risk: G16, G45: a committed kill record prevents zeroing although disk still contains stale bytes.
- detectable: partly — I/O events and transaction lifetime can be correlated, but logbuf cannot establish completion of unreported external I/O.
- silent: 2 — Submission-versus-completion mistakes can produce silent stale-data exposure.
- basis: general systems experience

<!-- derives: E60; logbuf/tran.c:1240; G28, G33, G39, G46 -->
### E60
- contract: VM integration must drive outstanding first-write I/O and finish its undo-zero transactions independently of log-space waiters.
- source: logbuf/tran.c:1240 "can safely wait for it to end its undo zeros."
- stated: stated
- violation: The only VM worker able to finish a first write is blocked trying to start another ordinary transaction on the same full log.
- at-risk: G28, G33, G39, G46: nested transactions never end, so quiescing or admission can deadlock.
- detectable: partly — worker dependency and wait graphs can expose this cycle.
- silent: 1 — A persistent cycle generally becomes an observable hang.
- basis: source

<!-- derives: E61; anode/strategy.c:267; G16, G31, G35 and correct user-data ordering -->
### E61
- contract: The VM and higher vnode layers must serialize overlapping block I/O so that waiting for an in-transit block is not invalidated by another writer.
- source: anode/strategy.c:267 "transit again.  The higher-level vnode locking should guarantee this."
- stated: stated
- violation: A second writer starts I/O to a block after a waiter has passed its in-transit check.
- at-risk: G16, G31, G35 and correct user-data ordering: later writes may be overwritten by earlier completions.
- detectable: partly — in-transit instrumentation detects some races; the critical reentry window requires higher-layer knowledge.
- silent: 2 — Cross-path VM and volume-operation races can be timing-dependent and silent.
- basis: general systems experience

<!-- derives: E62; anode/strategy.c:271; G16 and buffer/I/O availability -->
### E62
- contract: The VM and vnode layers must ensure the strategy layer’s documented bound on simultaneous waiters for each in-transit block.
- source: anode/strategy.c:271 "multiple I/O requests for a given block, and other writers are"
- stated: stated
- violation: Two VM or volume-operation threads wait for the same block where the code expects at most one waiter.
- at-risk: G16 and buffer/I/O availability: premature in-transit record reuse can invalidate synchronization.
- detectable: partly — waiter-count assertions catch documented cases, but all release races require careful tracking.
- silent: 1 — The source’s waiter checks usually make a violation visible.
- basis: source

<!-- derives: E63; logbuf/tran.c:1220; G32, G33, G38 -->
### E63
- contract: Clients must not use quiesce’s captured position as proof that later concurrently issued updates have completed.
- source: logbuf/tran.c:1220 "when the caller (elbb_QuiesceSystem) started.  Other activity is allowed"
- stated: stated
- violation: An administrative operation quiesces and assumes all subsequent writers are also included without excluding them.
- at-risk: G32, G33, G38: quiesce guarantees only the captured transaction prefix, so later writes remain outstanding.
- detectable: partly — position and transaction tracking can identify excluded activity, but not the caller’s intended administrative boundary.
- silent: 2 — Misinterpreting a concurrent snapshot boundary need not raise an error.
- basis: general systems experience

<!-- derives: E64; §"Recovery Time"; G9–G11, G21, G22 -->
### E64
- contract: The deployment must provide periodic checkpoint-driving work and sufficient metadata write bandwidth to keep the active log small when relying on fast recovery.
- source: §"Recovery Time" "every T seconds, as is the case with Episode, then the active portion of the log can rise to include all the"
- stated: implicit
- violation: Background checkpoint activity is disabled or the metadata disk stays saturated while committed dirty buffers accumulate.
- at-risk: G9–G11, G21, G22: recovery must replay more retained history, though bounded log admission can still preserve safety.
- detectable: yes — dirty-buffer age, active-log size, and checkpoint progress can be measured.
- silent: 3 — Temporary checkpoint lag during busy periods is occasional even in ordinary deployments.
- basis: general systems experience

<!-- derives: E65; §"Recovery Time"; G9–G11 -->
### E65
- contract: A deployment interpreting the recovery-time comparisons must keep active history, I/O performance, and available recovery resources comparable rather than scaling them with aggregate size.
- source: §"Recovery Time" "Episode's time to recover depends primarily on the size of the active portion of transaction log."
- stated: implicit
- violation: A larger aggregate is configured with much more active log history or a much slower recovery device.
- at-risk: G9–G11: replay cost depends on active pages and affected blocks, so aggregate-size-independent timing is conditional.
- detectable: yes — active-log size, affected-block count, and recovery timings can be measured.
- silent: 3 — Workload and device-speed variation commonly changes recovery time without a filesystem error.
- basis: general systems experience

<!-- derives: E66; logbuf/recover.c:2582; G54 and G1 -->
### E66
- contract: Administrators must select a supported effective checksum scheme when relying on torn-page or corruption detection.
- source: logbuf/recover.c:2582 "printf("Log has unknown checksum type on disk. Ignoring checksum check\n");"
- stated: implicit
- violation: A log uses checksum version NONE or an unknown type and the deployment assumes every torn page will be rejected.
- at-risk: G54 and G1: unchecked damaged pages can enter head selection or replay; checksumming is conditional on configuration.
- detectable: partly — the version is inspectable and an unknown version emits a warning; version NONE can operate without an error.
- silent: 2 — Legacy configurations can silently lack the protection expected of newer logs.
- basis: source

<!-- derives: E67; logbuf/recover.c:1039; G1, G6, G7, G54 -->
### E67
- contract: The failure environment must not alter a protected log page in a way that preserves its checksum and passes its structural checks.
- source: logbuf/recover.c:1039 "if (!ValidLogPageChecksum(logBlocks[index], ldP->blkSize,"
- stated: implicit
- violation: Corruption changes both payload and checksum consistently, or two payloads collide under the configured CRC.
- at-risk: G1, G6, G7, G54: a valid checksum is an error detector, not proof that bytes are the originally written history.
- detectable: no — the available checksum and structure alone cannot distinguish such a valid-looking corruption.
- silent: 1 — Undetected CRC collisions or coordinated corruption are rare in the described nonadversarial systems.
- basis: general systems experience

<!-- derives: E68; logbuf/recover.c:2738; G39, G55, G56 -->
### E68
- contract: The storage and operating environment must preserve a clean restart marker’s authenticity and its ordering after all recovery or shutdown data writes.
- source: logbuf/recover.c:2738 "We choose not to checksum the log page containing a restart record"
- stated: implicit
- violation: A forged, corrupted, restored, or prematurely durable restart marker survives while recovered metadata writes do not.
- at-risk: G39, G55, G56: a plausible restart record can suppress necessary recovery because it is not checksummed.
- detectable: partly — header and record checks catch malformed markers, but not a plausible stale or wrongly ordered clean marker.
- silent: 1 — Normal synchronous durable I/O preserves this order; silent violation is rare.
- basis: general systems experience

<!-- derives: E69; logbuf/log.c:734; G1, G6, G7, G20, G21 -->
### E69
- contract: Backup, restore, and raw-device administration must preserve a crash-consistent pairing of the aggregate’s metadata and its retained log history.
- source: logbuf/log.c:734 "code = elbr_Recover(ldP, dP, logLocnArray, logLocnArraySize);"
- stated: implicit
- violation: An operator restores only the log from an older backup, or independently snapshots log and data devices at incompatible times.
- at-risk: G1, G6, G7, G20, G21: replay history can be absent or belong to a different version of the metadata.
- detectable: partly — structural checks detect some mismatches, but no cross-device snapshot identity is established here.
- silent: 1 — Normal same-aggregate operation avoids independently restored log/data versions.
- basis: general systems experience

<!-- derives: E70; logbuf/buffer.c:731; G4, G5, G42 -->
### E70
- contract: Initialization callers must supply writable buffer-pool memory of the declared size and keep it owned by logbuf for the package lifetime.
- source: logbuf/buffer.c:731 "caddr_t startAddr = elbbParams->bufferPool;"
- stated: implicit
- violation: The caller frees or repurposes the pool after Init, or exaggerates byteCount beyond its allocation.
- at-risk: G4, G5, G42: log and cached bytes can be corrupted in memory before being written.
- detectable: partly — allocation and lifetime instrumentation can detect invalid ownership; ordinary I/O cannot establish it.
- silent: 1 — Normal kernel initialization retains the supplied pool.
- basis: source

<!-- derives: E71; logbuf/buffer.c:908; Log service availability and G17 where reservation configuration is affected -->
### E71
- contract: Tuning callers must pass appropriately typed accessible values in the package address space and copy user arguments before calling.
- source: logbuf/buffer.c:908 "caller must copyin/copyout the version string"
- stated: stated
- violation: An ioctl wrapper passes a user pointer directly to a routine expecting a kernel-space value or an undersized destination.
- at-risk: Log service availability and G17 where reservation configuration is affected: invalid dereferences or overwritten tuning values can crash or misconfigure logging.
- detectable: partly — address-space and buffer-size validation can reject malformed arguments, but the package trusts its wrapper.
- silent: 1 — Correct wrappers normally validate arguments and faults are usually visible.
- basis: source

<!-- derives: E72; logbuf/tran.c:957; G15, G23, G31, G40, G42 -->
### E72
- contract: Callers must check error and would-block returns before reporting successful persistence or using returned buffer contents.
- source: logbuf/tran.c:957 "RETURN CODES -- returns BUF_WOULDBLOCK only if waitOK is zero and the"
- stated: stated
- violation: A caller ignores BUF_WOULDBLOCK from a nonwaiting force or returns success after a read/copy/I/O error.
- at-risk: G15, G23, G31, G40, G42: an unsuccessful operation does not establish the success guarantee the upper layer reports.
- detectable: partly — return codes and pending state are visible, but logbuf cannot know that a caller discarded an error.
- silent: 2 — Error-handling omissions can silently affect uncommon paths.
- basis: general systems experience

<!-- derives: E73; logbuf/tran.c:1062; G13, G23, G24 -->
### E73
- contract: Clients retaining historical transaction IDs must retire them before ID wrap can make the same numeric ID identify unrelated work.
- source: logbuf/tran.c:1062 "elbt_GlobalTranId++;"
- stated: implicit
- violation: An old vnode or transactional lock retains a numeric ID across a complete 32-bit allocation cycle and later forces or merges an unrelated transaction.
- at-risk: G13, G23, G24: ID reuse can make a stale dependency or persistence check refer to the wrong work; the actual supported lifetime bound is uncertain.
- detectable: partly — generation-aware tracking could detect reuse, but a bare numeric ID is ambiguous.
- silent: 1 — Retaining an actionable ID across billions of transaction allocations is rare for the described workloads.
- basis: general systems experience

<!-- derives: E74; logbuf/log.c:187; G17, G20, G21, G54 -->
### E74
- contract: Aggregate configuration must keep log length and page indices within the range supported by the on-disk fields and signed-distance arithmetic.
- source: logbuf/log.c:187 "As with pass numbers, log offsets are unsigned int16s.  So we have to do"
- stated: implicit
- violation: A tool allocates a log whose page index truncates in oldestDataPage or whose distance changes sign in int16 arithmetic.
- at-risk: G17, G20, G21, G54: tail retention and recovery head/tail interpretation may select incorrect history.
- detectable: partly — initialization can validate representability; the precise safe bound requires further analysis of all comparisons.
- silent: 1 — The paper’s example log sizes are small relative to these field ranges.
- basis: source

## Recognised

<!-- derives: BRIEF.md recognition rule; logbuf/logbuf-locking revision history; anode/strategy.c:456. -->
I do not independently recall a specific published Episode/DFS incident behind these contracts. The supplied revision history itself reports new-block-security work (OT 3804/1020), transaction/waiting fixes (OT 5508/5249/4548), fsync work (OT 5316), and pass-number fixes (OT 5527); these are source evidence, not personal recollections, and are not the organizing basis of the list.

## Limitations and undecided points

<!-- derives: BRIEF.md environment boundary; logbuf/recover.c:745; logbuf/logrec.h:231; anode/strategy.c:456. -->
The code does not assume whole-log-page atomic writes or in-order completion of different outstanding log pages: it explicitly handles an in-transit window. Sector atomicity and truthful completion are distinct obligations. Ordinary user-data transaction atomicity is expressly excluded by the paper. A caller obeying the interface is not proof of a correct logbuf implementation.

Source concerns kept out of the environment list: `logbuf/buffer.c` disables several logging-consistency assertions with `#if 0`; its logged ModifySource path logs before an address-space-dependent copy, raising an unresolved question about logged USER sources and copy faults; `logbuf/recover.c` deliberately accepts unknown checksum types without validating their checksum and does not checksum restart-only pages. `anode/strategy.c` says undo-zero completion processing is not yet implemented in that path; I cannot establish from that comment alone which supported VM ports obtain coverage elsewhere. These are implementation/integration questions, not evidence that an operator violated a contract. The external source-stability, coverage, and completion obligations still apply.

The exact admissible maximum log length, cross-device block-size combinations, and supported cross-platform on-disk compatibility are not established here; 16-bit page/offset fields and native structure casts impose limits, but asserting a precise unverified deployment bound would overstate the evidence. The combined nested reservation must follow actual source settings: the code defines MAX_TRAN_SIZE as 70 KiB in this build, while an older nearby comment still says 35K. No actual failure frequencies, benchmark outcomes, or new defect claims were established. Similar storage-integrity contracts are split where their failure and detection mechanisms differ.

## Inventory

<!-- derives: BRIEF.md final-report requirement. -->
Contracts: 74.

`ls -R --ignore=episode .`

```text
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

`git status`

```text
On branch main
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	enumeration.md

nothing added to commit but untracked files present (use "git add" to track)
```

