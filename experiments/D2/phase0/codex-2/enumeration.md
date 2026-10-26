# Environment contracts for Episode log and recovery

Scope: the supplied paper and DCE 1.2.2 source. Ratings describe silent violations in the historical local-disk systems described by the paper, not modern storage deployments. They are qualitative judgments, not measured annual rates. A low rating can reflect a failure normally producing a visible error.

<!-- derives: BRIEF.md Task and Format; GUARANTEES.md G1–G63. No C-clause or F-cell identifiers are supplied in this checkout; none are invented. Each entry cites its concrete source and affected guarantee. -->

### E1
- contract: The storage device must make each log sector write atomic across a crash.
- source: logbuf/recover.c:752 "     * correctness/atomicity of each sector.  So if the log page did"
- stated: stated
- violation: Power loss leaves a sector containing a mixture of old and new header bytes.
- at-risk: G54, G1: head discovery can select the wrong log extent before checksum validation.
- detectable: partly — checksums may detect damage, but binary search deliberately trusts sector headers.
- silent: 1 — Sector tearing is exceptional on the historical disks, and often yields a visible checksum or device error.
- basis: general systems experience

### E2
- contract: The device must preserve successfully completed log writes through subsequent power loss.
- source: logbuf/recover.c:1302 "	returnVal = asevent_WaitEvent(ae);"
- stated: implicit
- violation: A drive acknowledges writes in an unprotected volatile write cache, then loses them on power failure.
- at-risk: G5, G7: metadata can become durable while its undo or redo log disappears.
- detectable: no — an acknowledged but volatile write is indistinguishable from a durable one.
- silent: 2 — Unprotected drive caches can conceal nondurability until a power failure; the historical controller configuration is unspecified.
- basis: general systems experience

### E3
- contract: The device must preserve completed home-block writes until a later authorized overwrite.
- source: logbuf/recover.c:1354 "      writeBlock(&buf, returnVal);"
- stated: implicit
- violation: A controller loses an acknowledged recovered block after a clean restart record is written.
- at-risk: G55, G1: recovery is declared complete although its repairs are missing.
- detectable: no — successful completion does not expose later loss.
- silent: 1 — Loss of previously completed home writes is an exceptional hardware failure and often produces later visible damage.
- basis: general systems experience

### E4
- contract: Storage must return the bytes last durably written to the requested address or report an error.
- source: logbuf/recover.c:1328 "      readBlock(&buf, returnVal);"
- stated: implicit
- violation: A read silently returns stale data or data from another block.
- at-risk: G1, G50: recovery calculates repairs from the wrong home contents; metadata lacks a general checksum here.
- detectable: partly — log checksum and page-number checks catch some log misreads, not arbitrary home-block misreads.
- silent: 1 — Silent stale or misdirected reads are unusual relative to reads that report media errors.
- basis: general systems experience

### E5
- contract: Storage writes must affect only their requested blocks and byte ranges.
- source: logbuf/recover.c:1299 "	buffer->adev, buffer->blockNum, 0);"
- stated: implicit
- violation: A misdirected write damages a neighboring metadata block or an unrelated log page.
- at-risk: G1, G7: unrecorded collateral damage cannot be reconstructed from the transaction log.
- detectable: partly — damaged log pages may fail checksums; collateral metadata damage may remain silent.
- silent: 1 — Misdirected writes require unusual controller, driver or address faults; many cause visible damage.
- basis: general systems experience

### E6
- contract: The disk subsystem must keep completed active log pages readable and intact until reuse.
- source: logbuf/recover.c:761 "     * active log pages outside the in-transit window are really"
- stated: stated
- violation: A latent media error corrupts an older active log page.
- at-risk: G7, G8: required undo or redo records are lost and recovery must give up.
- detectable: partly — checksum or read error detects many failures, but checksum collisions can pass.
- silent: 1 — Latent media damage is possible, but required log pages are checked and usually produce a visible recovery error.
- basis: general systems experience

### E7
- contract: The async service must associate each completion and error with the correct submitted request.
- source: logbuf/recover.c:1300 "     returnVal = asevent_QueueIO(buffer->adev, bp, ae);"
- stated: implicit
- violation: A driver signals completion for another request or drops an I/O error.
- at-risk: G5, G40: waiting can certify a write that never completed.
- detectable: partly — inconsistent event state can assert, but a plausible false success is invisible.
- silent: 1 — Misassociated event completion requires a driver or event-layer fault and commonly produces a hang or assertion.
- basis: general systems experience

### E8
- contract: The async service must finish all transfers before reporting their event complete.
- source: logbuf/recover.c:1302 "	returnVal = asevent_WaitEvent(ae);"
- stated: implicit
- violation: The callback runs while DMA still reads the buffer that logbuf then recycles.
- at-risk: G5, G55: the durable bytes can differ from the recorded or recovered bytes.
- detectable: partly — checksums may expose damaged log pages later.
- silent: 1 — Premature DMA completion is an unusual driver defect and often corrupts checksummed log pages.
- basis: general systems experience

### E9
- contract: The async service must eventually complete every accepted request or return a failure.
- source: logbuf/recover.c:1302 "	returnVal = asevent_WaitEvent(ae);"
- stated: implicit
- violation: A lost interrupt leaves an event pending forever.
- at-risk: G39, G40, G55: shutdown, fsync or recovery waits indefinitely.
- detectable: yes — elapsed-time monitoring can identify a stalled request, though this code has no general timeout.
- silent: 1 — A lost completion normally causes an observable hung operation rather than a silent successful year.
- basis: general systems experience

### E10
- contract: The OS must honor memory pinning for buffers used by asynchronous I/O.
- source: logbuf/recover.c:1376 "      logbuf_pin(data, dev->blkSize);"
- stated: implicit
- violation: The VM reclaims or relocates a pinned page during device access.
- at-risk: G1, G5: DMA consumes or overwrites unrelated memory.
- detectable: partly — faults or checksums can expose damage.
- silent: 1 — Broken pinning is an unusual OS-port defect and normally leads to a fault or obvious corruption.
- basis: general systems experience

### E11
- contract: The OS synchronization primitives must provide mutual exclusion and visibility of protected memory.
- source: logbuf/log.c:449 "#define map_assertlocked(map) afsl_Assert(epi_mutex_held(&(map)->mapLock))"
- stated: implicit
- violation: Two CPUs enter the same protected log-map critical section or observe stale fields after acquiring its lock.
- at-risk: G2, G5, G13: log state and transaction membership can race.
- detectable: partly — assertions catch some impossible states, not every lost update.
- silent: 1 — Broken mutex semantics are unusual on supported ports and tend to cause broad visible failures.
- basis: general systems experience

### E12
- contract: The OS condition-variable wait must release and reacquire its mutex atomically with sleeping and must deliver notifications reliably.
- source: logbuf/buffer.c:2347 "		  epi_cond_broadcast (&bpeP->cond);"
- stated: implicit
- violation: A waiter misses a wakeup and never notices newly available buffer space.
- at-risk: G17, G40: transaction admission or synchronization loses forward progress.
- detectable: yes — blocked threads with a satisfied predicate can in principle be observed.
- silent: 1 — Lost wakeups generally surface as visible hangs under load.
- basis: general systems experience

### E13
- contract: The machine must provide atomic assignment and observation of the 32-bit tuning quantities used without reader locks.
- source: logbuf/log.c:2639 " * a 32 bit quantity is atomic w.r.t. all readers."
- stated: stated
- violation: A port reads a torn value while a parameter is changed.
- at-risk: G17: reservation or limit calculations can use an impossible value.
- detectable: partly — range checks may catch some torn values.
- silent: 1 — The target 32-bit machines normally provide this atomicity; incompatible ports are uncommon.
- basis: general systems experience

### E14
- contract: The allocator must supply sufficient memory for the active log and recovery record structures.
- source: logbuf/recover.c:1038 "	   that we can read this much stuff into memory? */"
- stated: implicit
- violation: A valid large active log exhausts the recovery process address space.
- at-risk: G9, G55: recovery panics or cannot finish rather than meeting its time and completion claims.
- detectable: yes — allocation failure or process termination is visible.
- silent: 1 — Memory exhaustion normally panics or stops recovery visibly.
- basis: general systems experience

### E15
- contract: The compiler and ABI must lay out the device pointer immediately before the block-number field as the address hash expects.
- source: logbuf/buffer.c:842 "       * block # fields are contiguous, with the device *first*.  We"
- stated: stated
- violation: An ABI inserts padding that becomes part of a hash key.
- at-risk: G1, G40: one disk address can acquire conflicting cache identities or fail lookup.
- detectable: partly — inconsistent hash behavior may be diagnosed, but no portable layout check is shown.
- silent: 1 — The supported ABI normally meets the layout assumption; a new incompatible ABI commonly fails early.
- basis: general systems experience

### E16
- contract: Recovery must use the same compatible on-disk integer representation, structure layout and alignment as the log writer.
- source: logbuf/logrec.h:298 "#define GetPageHdr(buf) (struct logPageHdr *)(buf)"
- stated: implicit
- violation: An aggregate is recovered on a machine with incompatible byte order or structure packing.
- at-risk: G47, G50, G54: direct structure casts interpret headers and records incorrectly.
- detectable: partly — magic, checksum and record checks reject many incompatible layouts.
- silent: 1 — Unsupported on-disk representation normally fails magic or record checks instead of silently succeeding.
- basis: general systems experience

### E17
- contract: The supplied logical device must retain its block size and address interpretation for its entire log attachment.
- source: logbuf/buffer.c:1004 "      bpeP = GetBufferPool(dP->blkSize);"
- stated: implicit
- violation: A device descriptor is retargeted or its block size changes while buffers remain cached.
- at-risk: G1, G5: cached blocks and log addresses refer to different physical bytes.
- detectable: partly — some size checks exist, but descriptor identity does not certify stable mapping.
- silent: 1 — Live descriptor retargeting is exceptional and commonly causes visible addressing errors.
- basis: general systems experience

### E18
- contract: The configured device block size must be a supported power of two between 1 KiB and 64 KiB.
- source: logbuf/logbuf.p.h:416 "#define BUF_MAXBUFSIZE  (64 * BUF_MINBLKSIZE) /* largest buffer size */"
- stated: implicit
- violation: An operator attaches a device using unsupported 3 KiB or 128 KiB logical blocks.
- at-risk: G17, G1: pool indexing and log reservation arithmetic cease to match real blocks.
- detectable: partly — VALID_SIZE and assertions check sizes, but the cited log reservation mask alone does not prove a power of two.
- silent: 1 — Unsupported block sizes are deployment mistakes usually caught by setup checks or assertions.
- basis: general systems experience

### E19
- contract: The aggregate layer must provide the correct ordered array of physical log block addresses and its exact length.
- source: logbuf/recover.c:989 "    /* guarantee the caller described the log properly */"
- stated: stated
- violation: A damaged log anode supplies a permuted, truncated or wrong address array.
- at-risk: G54, G55: recovery searches and replays the wrong circular log.
- detectable: partly — page-number and tail bounds checks catch some incorrect descriptions.
- silent: 1 — Wrong log maps normally cause page-number, checksum or bounds failures.
- basis: general systems experience

### E20
- contract: The allocator must reserve distinct log blocks that do not overlap home metadata or user data.
- source: logbuf/recover.c:1044 "	readData(ldP, logLocnArray[current], logBlocks[index]);"
- stated: implicit
- violation: The log address array repeats a block or includes a block also allocated to a file.
- at-risk: G5, G7: ordinary writes can overwrite recovery records or logging can destroy home data.
- detectable: partly — page-number checks may reveal overlap after damage.
- silent: 1 — Allocation overlap is a rare allocator or provisioning fault and often produces visible corruption.
- basis: general systems experience

### E21
- contract: The aggregate layer must keep the log allocation and address map fixed while logging is attached.
- source: logbuf/log.c:697 "     IN daddr_t *logLocnArray,"
- stated: implicit
- violation: An online resize or relocation changes log blocks without a coordinated log replacement.
- at-risk: G7, G54: recovery and logging disagree about where retained records reside.
- detectable: partly — malformed page sequences may be found; no relocation protocol is supplied here.
- silent: 1 — Normal operation deliberately does not resize the log; unsupported live changes are rare.
- basis: general systems experience

### E22
- contract: Provisioning must allocate a log large enough for the minimum transaction reservation and safety margin.
- source: logbuf/log.c:1713 "	   * is large enough for at least one transaction, we also proceed if"
- stated: stated
- violation: An aggregate is initialized with fewer pages than its transaction and block-size configuration needs.
- at-risk: G17: admission cannot guarantee room for one transaction and progress.
- detectable: yes — initialization and log-full checks can reject inadequate space.
- silent: 1 — Undersized logs are rejected during attachment rather than silently violating the bound.
- basis: general systems experience

### E23
- contract: Filesystem callers must route every metadata modification through logged buffer operations in a valid transaction.
- source: logbuf/buffer.c:1422 " * if the tranId is not the invalid transaction id and the logRequest"
- stated: implicit
- violation: An anode or directory writer changes metadata directly or disables logRequest.
- at-risk: G1, G4, G6: recovery has no old/new record for that update.
- detectable: partly — API checks catch some bad arguments, but bypass writes are not generally visible.
- silent: 2 — A bypass logging path can run successfully for long periods; its silent incidence depends on unmeasured caller defects.
- basis: general systems experience

### E24
- contract: Filesystem transaction boundaries must enclose a logically consistent complete metadata operation.
- source: logbuf/tran.c:435 "void elbt_EndTran(IN elbt_TranRec_t tranId)"
- stated: implicit
- violation: A caller ends a transaction after allocating a block but before installing its required reference.
- at-risk: G1, G2: atomic replay preserves an inconsistent application-level state.
- detectable: no — logbuf cannot infer directory or allocation invariants from byte updates.
- silent: 1 — Incorrect transaction boundaries are uncommon integration defects that can remain latent until a crash.
- basis: general systems experience

### E25
- contract: Filesystem callers must split oversized operations into bounded transactions that each preserve filesystem consistency.
- source: logbuf/log.c:1703 "           * Each running transaction is assumed to need MAX_TRAN_SIZE of log"
- stated: stated
- violation: Deleting a huge file is issued as one transaction or leaves an inconsistent intermediate truncation.
- at-risk: G17, G19: reservation can be exceeded or a crash can expose an inconsistent intermediate state.
- detectable: partly — transaction-size checks detect excess, but semantic inconsistency needs higher-layer validation.
- silent: 1 — Oversized operations normally encounter size or log-full failures; inconsistent intermediate states are less directly visible.
- basis: general systems experience

### E26
- contract: Filesystem callers must finish active transactions rather than leave them open indefinitely.
- source: logbuf/log.c:1703 "           * Each running transaction is assumed to need MAX_TRAN_SIZE of log"
- stated: implicit
- violation: An error path forgets EndTran and pins the log tail throughout continued operation.
- at-risk: G9, G17, G39: the log fills and checkpoint, admission or shutdown stalls.
- detectable: yes — transaction age and pending state can be monitored.
- silent: 1 — Leaked active transactions generally cause visible log pressure or shutdown hangs.
- basis: general systems experience

### E27
- contract: Higher layers must serialize conflicting accesses to the contents of each metadata object.
- source: anode/tlock.c:99 "	lock_ObtainWrite_r (&tlock->lock);"
- stated: implicit
- violation: Two writers update a directory or anode without its transactional lock.
- at-risk: G1, G2: byte-level logs cannot repair lost semantic updates or inconsistent before-images.
- detectable: partly — races may assert, but valid-looking conflicting changes can pass.
- silent: 1 — Missing object locks are unusual in the supported code and often manifest under concurrency.
- basis: general systems experience

### E28
- contract: Transactional-lock callers must report read/write dependencies on uncommitted state by merging the corresponding transactions.
- source: anode/tlock.c:112 "	elbb_EquivTran (*tlockTransP, trans, (unsigned long) &tlock->lock);"
- stated: implicit
- violation: A caller uses an ordinary lock or a null transaction when consuming another active transaction's update.
- at-risk: G13, G14: recovery may commit the dependent transaction while undoing its prerequisite.
- detectable: no — logbuf cannot discover unreported object-level dependencies.
- silent: 1 — Unreported dependencies require a higher-layer integration defect and may remain latent until a crash.
- basis: general systems experience

### E29
- contract: Callers must supply an active second transaction when requesting an equivalence-class merge.
- source: logbuf/tran.c:648 " *     second tran must be active."
- stated: stated
- violation: A stale completed transaction ID is passed as the new merge target.
- at-risk: G13: the intended dependency cannot be safely attached to a running transaction.
- detectable: yes — the transaction manager asserts the active-state precondition.
- silent: 1 — An inactive merge target normally trips the transaction assertion.
- basis: general systems experience

### E30
- contract: Callers must avoid waiting for transaction completion while holding an active transaction needed by that wait.
- source: logbuf/tran.c:1330 " * CAUTIONS -- The calling thread must not be holding any active transactions."
- stated: stated
- violation: A thread forces a transaction in its own EC while retaining an unfinished member.
- at-risk: G13, G15, G39: the class cannot complete and the waiter deadlocks.
- detectable: yes — active transaction ownership and a wait-for graph could expose the cycle.
- silent: 1 — Self-dependent transaction waits normally produce a visible hang.
- basis: general systems experience

### E31
- contract: Forced nested undo-zero transactions and their parent must fit within the single-transaction space bound.
- source: logbuf/log.c:1693 "       * transaction size plus old transaction size will be less than the"
- stated: stated
- violation: A caller creates enough forced child coverage to exceed its parent's reserved space.
- at-risk: G17, G16: forced admission bypasses normal space checks and can exhaust the log.
- detectable: partly — later log-full and size assertions expose excess, possibly too late.
- silent: 1 — Excess forced reservation is uncommon and tends to surface as a full log or assertion.
- basis: general systems experience

### E32
- contract: The block allocator must retain the logged-versus-unlogged classification and execute the required buffer transitions when reusing blocks.
- source: logbuf/recover.c:1897 " *     NBS.  These must be interpreted as kill records for earlier updates to"
- stated: implicit
- violation: A metadata block is reassigned to user data while dirty metadata remains cached.
- at-risk: G16, G51: old metadata may overwrite user data or stale records may replay into a new owner.
- detectable: partly — RCVR_USERDATA and RCVR_METADATA expose some invalid histories.
- silent: 1 — Incorrect block-type transitions require an allocator defect and often cause visible recovery refusal.
- basis: general systems experience

### E33
- contract: A caller may authorize killing dirty metadata only after the freeing transaction and all prior modifiers have committed.
- source: logbuf/buffer.c:1370 " *     buffers.  This will only be true if the transaction that freed the"
- stated: stated
- violation: An allocator passes metadataOK=true before its freeing transaction commits.
- at-risk: G44, G6: the only dirty copy can be discarded while rollback still needs it.
- detectable: partly — false metadataOK is checked, but a dishonest true is trusted.
- silent: 1 — A false kill authorization requires a caller defect and may remain hidden until rollback is needed.
- basis: general systems experience

### E34
- contract: Filesystem allocation code must establish undo-zero protection for all newly exposed user-data bytes before allocation becomes durable.
- source: logbuf/buffer.c:2437 " * elbb_UndoZero - Adds an undo-zero record to an existing transaction for"
- stated: implicit
- violation: A newly allocated block is linked into a file without an undo-zero record.
- at-risk: G16, G45: a crash before its first write exposes data from the previous owner.
- detectable: no — missing coverage is not distinguishable from intentional unlogged data.
- silent: 1 — Omitted first-write protection is an unusual allocation-path defect that is latent until crash timing exposes old data.
- basis: general systems experience

### E35
- contract: The VM must end an undo-zero transaction only after the protected first data write has completed successfully.
- source: logbuf/tran.c:1255 " *     from the VM system which has its own Async daemon to complete I/O.  We"
- stated: implicit
- violation: VM ends the protection on submission or after a failed first write.
- at-risk: G16: recovery treats the kill as committed and leaves unwritten old data visible.
- detectable: partly — I/O status is available, but a falsely ended transaction is trusted.
- silent: 1 — Premature protection completion is an unusual VM integration defect that can remain hidden until failure.
- basis: general systems experience

### E36
- contract: The VM must independently drive outstanding undo-zero I/O to completion while logbuf waits.
- source: logbuf/tran.c:1256 " *     can safely wait for it to end its undo zeros."
- stated: stated
- violation: The only VM flush worker is blocked trying to start a transaction behind its own pending undo zero.
- at-risk: G17, G39: log-space recovery or quiescing deadlocks.
- detectable: yes — pending I/O and wait dependencies can reveal lack of progress.
- silent: 1 — A stalled VM completion worker usually produces an observable synchronization hang.
- basis: general systems experience

### E37
- contract: Callers must finish all updates to a dirty buffer before attaching its undo-zero transaction with UndoZeroBuffer.
- source: logbuf/buffer.c:2483 " *     present.  All updates to the dirty buffer have been done when this call"
- stated: stated
- violation: The caller continues initializing the buffer after the first-write protection is attached and a write starts.
- at-risk: G16, G46: completion can certify an incomplete initialization.
- detectable: partly — update flags may expose overlap, but raw concurrent stores may not.
- silent: 1 — Updating after protection attachment requires caller misuse and may cause visible partial initialization.
- basis: general systems experience

### E38
- contract: Callers must restrict undo-zero buffer ranges to the current buffer and provide valid byte ranges to modification APIs.
- source: logbuf/buffer.c:2500 "      afsl_Assert(fillSize + offset <= bP->adev->blkSize);"
- stated: stated
- violation: An offset or length runs beyond the block or wraps arithmetic.
- at-risk: G42, G45: the log covers the wrong bytes or memory outside the buffer is modified.
- detectable: partly — range assertions catch ordinary overflow of the block, not necessarily integer wrap.
- silent: 1 — Out-of-range calls usually assert or fault rather than remain silent.
- basis: general systems experience

### E39
- contract: Callers may omit old-value logging only for genuinely new block initialization whose old contents need not be restored.
- source: logbuf/buffer.c:1602 " * do not have to be logged, i.e. the buffer was created by CreateBlock."
- stated: stated
- violation: Initialize is used to overwrite live metadata that must survive transaction abort.
- at-risk: G6, G43: redo-only initialization has no before-image for undo.
- detectable: no — logbuf cannot infer whether the old bytes were semantically disposable.
- silent: 1 — Misuse of initialization is uncommon in stable metadata callers but may stay hidden until crash undo.
- basis: general systems experience

### E40
- contract: Callers using CreateBlock without a disk read must initialize all bytes that can become visible or significant before writeback.
- source: logbuf/buffer.c:974 " * (1) Just allocate a buffer (for overwriting an entire disk block."
- stated: implicit
- violation: Only part of a fresh cache buffer is initialized and the whole block is written to disk.
- at-risk: G1, G16: uninitialized memory becomes metadata or file contents.
- detectable: partly — debug randomization helps expose misuse, but no initialized-byte map is maintained.
- silent: 1 — Partial initialization is an uncommon caller defect and may expose garbage without an explicit I/O error.
- basis: general systems experience

### E41
- contract: Callers must retain a valid held writable buffer reference throughout modification and release it exactly once when finished.
- source: logbuf/buffer.c:1443 "      afsl_Assert(bufferIsWrite(bP) && (bP->refCount > 0));"
- stated: stated
- violation: A stale buffer pointer is used after Release or a leaked hold prevents reclamation.
- at-risk: G42, G39: another block can be modified or shutdown cannot reclaim its buffers.
- detectable: partly — reference and write-state assertions catch some misuse.
- silent: 1 — Stale or leaked references usually assert, corrupt visible data or impede shutdown.
- basis: general systems experience

### E42
- contract: Callers must use the returned buffer handle after operations that may replace the handle.
- source: logbuf/buffer.c:1426 " * cannot assume the buffer handle will not change across this call."
- stated: stated
- violation: A caller ignores nbP and continues using the original pointer after a modifying operation.
- at-risk: G42: subsequent accesses may refer to a recycled or inappropriate buffer.
- detectable: partly — stale-reference checks are limited.
- silent: 1 — Ignoring a replacement handle requires a caller defect; repeated use tends to expose it.
- basis: general systems experience

### E43
- contract: Callers must classify external buffers as data or logged buffers and leave internal buffer types to logbuf.
- source: logbuf/logbuf.p.h:47 " * users of this package are restricted to the first two cases"
- stated: stated
- violation: A filesystem caller requests elbb_bufLog for a normal metadata block.
- at-risk: G5, G42: internal-type handling can bypass ordinary logging or cache rules.
- detectable: partly — type assertions exist on some paths.
- silent: 1 — Internal buffer types are not normally requested by filesystem callers.
- basis: general systems experience

### E44
- contract: Callers must not mix logged and unlogged dirty modifications to the same logged buffer between writebacks.
- source: logbuf/buffer.c:1453 "      /* Require that updates to logged buffers are either always logged or"
- stated: stated
- violation: A caller first dirties a metadata buffer without logging and then performs a logged edit.
- at-risk: G4, G5: the age queue no longer describes every dirty byte's recovery requirements.
- detectable: partly — the relevant assertions are present but disabled with #if 0.
- silent: 1 — Mixed logging requires an unusual caller path, although disabled assertions make latent misuse possible.
- basis: general systems experience

### E45
- contract: Code paths needing multiple simultaneously held buffers must reserve sufficient buffer capacity before acquisition and return their reservation.
- source: logbuf/buffer.c:2215 " * elbb_Reserve - reservation call for code paths which require multiple"
- stated: implicit
- violation: Several operations each hold one buffer and wait for another in an exhausted pool.
- at-risk: G17, G40: transactions cannot finish or flush and admission stalls.
- detectable: yes — reservations, held buffers and waits can reveal the resource cycle.
- silent: 1 — Missing capacity reservations generally lead to visible allocation deadlocks.
- basis: general systems experience

### E46
- contract: Higher layers must synchronize aggregate access against log shutdown and teardown.
- source: logbuf/tran.c:557 "       * levels have properly synchronized access to this aggregate."
- stated: stated
- violation: An aggregate is closed while another thread starts a modification or uses its device descriptor.
- at-risk: G39, G55: clean restart can race new updates or teardown can invalidate live state.
- detectable: partly — closed-map and transaction assertions catch some races.
- silent: 1 — Unsynchronized close is an uncommon lifecycle defect and often trips assertions.
- basis: general systems experience

### E47
- contract: The caller must invoke LogInit without dirty cached buffers on the recovered device.
- source: logbuf/buffer.c:1854 "	       * buffers were dirty when elbb_LogInit was called."
- stated: stated
- violation: An aggregate has dirty pre-recovery cache entries when initialization triggers recovery.
- at-risk: G55, G60: shutdown can write stale buffers over freshly recovered disk contents.
- detectable: yes — dirty flags can be inspected before recovery begins.
- silent: 1 — Normal startup precedes dirty metadata activity; misuse is an exceptional lifecycle error.
- basis: general systems experience

### E48
- contract: The recovery caller must exclude concurrent filesystem writes and other recovery instances on the same aggregate.
- source: logbuf/recover.c:359 " * This code must run single-threaded in user space;  it runs multi-threaded"
- stated: stated
- violation: A mounted writer or second salvager changes blocks while recovery calculates and writes repairs.
- at-risk: G1, G50, G55: recovery has no lock protocol for coordinating these disk updates.
- detectable: partly — deployment locks could detect overlap, but this recovery code has no such protection.
- silent: 1 — Concurrent recovery or mounted recovery is an exceptional operational error and often gives visible failures.
- basis: general systems experience

### E49
- contract: The operator or aggregate layer must arrange user-space recovery when a dirty log is rejected by the kernel.
- source: logbuf/recover.c:2402 "      return RCVR_MUSTRCVR; /* no kernel recovery anymore */"
- stated: implicit
- violation: An operator treats RCVR_MUSTRCVR as a clean mount or never runs the recovery utility.
- at-risk: G1, G57, G58: the kernel deliberately does not repair the dirty aggregate.
- detectable: yes — the explicit return code identifies the need for recovery.
- silent: 1 — Ignoring a required-recovery return normally prevents service or produces a visible mount error.
- basis: general systems experience

### E50
- contract: Higher layers must honor recovery and initialization return codes and retry initialization after RCVR_RECOVERED.
- source: logbuf/log.c:743 "	      return RCVR_RECOVERED;	/* so upper levels can clear buffers */"
- stated: implicit
- violation: The caller proceeds as if a normal log attachment succeeded after recovery or ignores a recovery failure.
- at-risk: G58, G59: cache invalidation and valid log attachment can be skipped.
- detectable: partly — return codes expose the condition, but logbuf cannot enforce every caller's control flow.
- silent: 1 — Ignoring initialization status is an uncommon integration error and commonly prevents usable logging.
- basis: general systems experience

### E51
- contract: Operators must use the salvager rather than rely on log replay alone after unrecoverable active-log or critical metadata I/O damage.
- source: logbuf/recover.c:1049 "	     * Only resort is to run salvager"
- stated: stated
- violation: A deployment resumes normal service after recovery fails on corrupted required log pages.
- at-risk: G1, G11: replay cannot reconstruct missing information and fsck-like salvage is required.
- detectable: yes — recovery errors and I/O failures identify the need; silent corruption remains a limit.
- silent: 1 — Failed recovery explicitly reports the need for repair; disregarding it is usually an observable operational incident.
- basis: general systems experience

### E52
- contract: The filesystem fsync path must identify every required cached buffer with correct file-handle tags or a complete block list.
- source: logbuf/buffer.c:2039 " *     the buffers to write out.  Either a magic value is used to tag each"
- stated: implicit
- violation: A file has an untagged dirty indirect block or a required block is omitted from the array.
- at-risk: G15, G40: FsyncForce does not flush omitted buffers.
- detectable: no — logbuf cannot infer the higher-level set of blocks belonging to the request.
- silent: 1 — Missing fsync selection is an uncommon tagging defect that may stay silent until crash testing.
- basis: general systems experience

### E53
- contract: Callers requiring persistence must choose a mode that waits for the necessary data or transaction commit and check its result.
- source: logbuf/logbuf.p.h:63 "    elbb_async,   /* schedule write now, but don't wait for completion */"
- stated: implicit
- violation: A vnode fsync returns success after SyncForce, async release or a completion-only transaction wait.
- at-risk: G15, G40: scheduled or ended changes can still be lost on a crash.
- detectable: partly — the selected mode is visible, but the caller's promised durability is outside logbuf.
- silent: 1 — Using a scheduling-only API for persistence is an uncommon caller defect and is invisible in ordinary operation.
- basis: general systems experience

### E54
- contract: VM integration must flush file data outside the buffer pool before claiming whole-file durability.
- source: logbuf/buffer.c:2439 " * that do not use the buffer system.  It is expected that this would not be"
- stated: implicit
- violation: A file fsync flushes logbuf buffers but leaves dirty mapped pages in the VM.
- at-risk: G15: metadata synchronization alone does not persist the requested file contents; the paper explicitly disclaims user-data transactions.
- detectable: no — logbuf does not enumerate VM-resident dirty file pages.
- silent: 1 — Incomplete VM fsync integration is an uncommon port defect; ordinary writes can conceal it until a crash.
- basis: general systems experience

### E55
- contract: Callers requesting commit quiescence must arrange completion of dirty-buffer and VM undo-zero writes before waiting for their transactions.
- source: logbuf/tran.c:1254 " *     all dirty buffers to be written.  Any other undo zero transactions are"
- stated: stated
- violation: A higher layer waits for undo-zero commit without scheduling the data writes that end those transactions.
- at-risk: G39, G46: quiescing can wait forever.
- detectable: yes — dirty buffers and unfinished undo-zero transactions expose the unmet prerequisite.
- silent: 1 — Incorrect quiesce ordering normally hangs visibly.
- basis: general systems experience

### E56
- contract: Startup must initialize transaction globals without concurrent transaction users.
- source: logbuf/tran.c:178 " * Locks: assumes no locking (single-threaded at init time).  Call is"
- stated: stated
- violation: Two startup threads initialize or use transaction lists concurrently.
- at-risk: G2, G13: transaction tracking can be corrupted before ordinary locking applies.
- detectable: partly — initialization guards and list assertions may expose races.
- silent: 1 — Initialization is normally single-threaded; violating it is an unusual startup integration defect.
- basis: general systems experience

### E57
- contract: Tuning callers must supply accessible kernel-address-space values and perform user-space copyin or copyout themselves.
- source: logbuf/buffer.c:876 " * Note that elbb_Tune assumes the address of value is in its address"
- stated: stated
- violation: An administrative interface forwards an unchecked user pointer to Tune.
- at-risk: G17: faults or unintended parameter writes can disrupt reservation and logging service.
- detectable: partly — address faults are visible, but valid wrong addresses can corrupt memory.
- silent: 1 — Incorrect address-space forwarding commonly faults visibly.
- basis: general systems experience

### E58
- contract: Administrative tuning must preserve valid transaction, equivalence-class and log-capacity limits for attached devices.
- source: logbuf/log.c:2668 "		  /* XXX: go back and recompute for all active log maps. */"
- stated: implicit
- violation: An operator changes a global maximum and assumes existing log maps have been resized or re-reserved.
- at-risk: G17: configured limits and per-map reservations can diverge; the exact impact depends on the parameter.
- detectable: partly — value checks catch some invalid settings, but existing-map consistency is not fully recomputed.
- silent: 1 — Unsafe live tuning is unusual in ordinary operation and may visibly exhaust resources.
- basis: general systems experience

### E59
- contract: The scheduler must allow transaction owners and I/O completion workers to run while other threads wait for them.
- source: logbuf/tran.c:1215 "	  elbt_TranUnlockAndSleep(tP,tP);"
- stated: implicit
- violation: A high-priority waiter starves the only thread that can finish its transaction or I/O.
- at-risk: G15, G39: forced commit and shutdown lose eventual completion.
- detectable: yes — scheduler and wait-state tracing can show starvation.
- silent: 1 — Scheduler starvation generally manifests as visible unresponsiveness.
- basis: general systems experience

### E60
- contract: The OS time service must provide usable elapsed-time progression for the buffer-cache aging heuristics.
- source: logbuf/buffer.c:2857 " *	 reused.  Thus the average age of reuse must be much smaller than the"
- stated: implicit
- violation: A broken clock freezes age calculations or jumps enough to distort cache-cost comparisons.
- at-risk: G9, G11: maintenance and cache behavior may lose the stated recovery/performance characteristics; correctness dependence is uncertain.
- detectable: partly — clock anomalies can be detected against an independent clock.
- silent: 1 — Clock failures are unusual, and cache heuristics tolerate ordinary timing variation.
- basis: general systems experience

### E61
- contract: The aggregate layer must keep the log-location array allocated and unchanged until the log is detached.
- source: logbuf/log.c:816 "      lmP->logLocnArray = logLocnArray;"
- stated: implicit
- violation: A caller frees its temporary address array after LogInit returns.
- at-risk: G5, G7: the stored pointer then supplies arbitrary destinations for log I/O.
- detectable: partly — bad addresses may cause I/O errors, but valid misdirected destinations can pass.
- silent: 1 — Prematurely freed location arrays are uncommon caller defects and commonly fault or misdirect I/O visibly.
- basis: general systems experience

### E62
- contract: Device management must use one stable canonical async-device identity for each attached aggregate.
- source: logbuf/log.c:109 "	LookupLogMap(dP, lmP); \"
- stated: implicit
- violation: Two descriptors name the same disk and permit independent log attachments or conflicting cache entries.
- at-risk: G1, G58: pointer-keyed attachment checks do not exclude a second writer through an alias.
- detectable: partly — external device identity checks can detect aliases; pointer lookup alone cannot.
- silent: 1 — Device aliases require unusual attachment management and often produce visible conflicting service.
- basis: general systems experience

### E63
- contract: The allocator must commit earlier metadata modifications before a later user-data kill makes their history obsolete.
- source: logbuf/recover.c:1937 "		RECVR_RAISE (RCVR_METADATA);"
- stated: implicit
- violation: A block is reused for user data while a preceding metadata update is still uncommitted.
- at-risk: G53, G1: recovery rejects this history instead of safely discarding its old records.
- detectable: yes — HandleKillRecords raises RCVR_METADATA for the forbidden ordering.
- silent: 1 — Forbidden metadata-to-data ordering is explicitly detected during recovery.
- basis: general systems experience

### E64
- contract: The allocator must complete a user-data kill transaction before reusing that block for newer logged metadata.
- source: logbuf/recover.c:1929 "		    RECVR_RAISE (RCVR_USERDATA);"
- stated: implicit
- violation: New metadata is installed on a block whose user-data undo-zero transaction remains uncommitted.
- at-risk: G52, G1: undo-zero could erase newer metadata and recovery refuses the history.
- detectable: yes — HandleKillRecords raises RCVR_USERDATA when newer ordinary records precede an uncommitted kill in reverse scan.
- silent: 1 — Forbidden data-to-metadata ordering is explicitly detected during recovery.
- basis: general systems experience

### E65
- contract: Provisioning must select a working supported checksum format when relying on detection of partial log-page writes.
- source: logbuf/recover.c:2445 "      case LOGREC_CKSUMVER_NONE:"
- stated: implicit
- violation: An aggregate uses the no-checksum format yet expects a partly written multi-sector page to be detected.
- at-risk: G54, G1: sector atomicity alone does not establish completeness of the remaining sectors.
- detectable: partly — checksum mode is inspectable, but damage cannot be checked without redundancy.
- silent: 1 — No-checksum operation can conceal torn pages, but the incidence depends on configuration and crash timing.
- basis: general systems experience

### E66
- contract: The environment must not silently alter log pages into different records with the same accepted checksum and plausible headers.
- source: logbuf/recover.c:2603 "		SameChecksum(storedCksum, calcCksum, storedCksumLen)) {"
- stated: implicit
- violation: Corruption happens to collide under CRC32 or a tool recomputes the checksum after an incorrect edit.
- at-risk: G47, G50: recovery accepts incorrect transaction or byte-update information.
- detectable: no — the available checksum cannot distinguish such pages.
- silent: 1 — Accidental CRC collisions are very rare for ordinary random corruption; unchecked formats weaken this assessment.
- basis: general systems experience

### E67
- contract: Transactional-lock storage must not be recycled for a different object until its associated transaction has completed.
- source: anode/tlock.c:53 "	code = elbb_LogForce(*transP, 2/*complete*/);"
- stated: implicit
- violation: An anode lock is freed and reused without tlock_Recycle or Destroy while its transaction is active.
- at-risk: G13, G24: dependency tracking can be lost or attached to an unrelated new object.
- detectable: partly — stored transaction state can identify premature reuse if the higher layer reports it.
- silent: 1 — Premature lock recycling is an uncommon lifecycle error that often exposes dependency or memory misuse.
- basis: general systems experience

### E68
- contract: Callers must keep source data and its declared address-space classification valid until a modification call finishes copying and logging it.
- source: logbuf/buffer.c:1436 "     IN osi_uio_seg_t newDataSource,	/* address space of newData ptr */"
- stated: implicit
- violation: A user buffer changes concurrently between log copying and home-buffer copying, or a user pointer is marked OSI_UIOSYS.
- at-risk: G4, G42: logged new bytes may differ from the actual update, or copying faults.
- detectable: partly — address faults are observable, but concurrent valid data changes need not be.
- silent: 1 — Unstable copy sources are uncommon in the described local kernel callers and often cause a visible fault.
- basis: general systems experience

## Recognised

I do not recall a specific reported Episode or DFS bug independently of these sources. The supplied history mentions OT 3804/1020 (new-block security), OT 5508 (transaction waits), OT 5316 (FsyncForce), OT 4548 (reservations), and OT 5527 (pass numbers); these are source observations, not independent recalled reports. Volatile write-cache acknowledgements are a familiar filesystem failure pattern, without a particular report recalled.

## Limits and undecided points

The logbuf implementation itself may have defects; these are not environment contracts. In particular, elbb_UndoZero loops over a multi-block range without incrementing blkno (buffer.c:2440–2449), so its advertised cross-block coverage appears suspect. This is a static observation, not an executed or experimentally confirmed failure. The power-of-two comment in elbl_MinTranReservation is stronger than its mask assertion. Disabled logging-consistency assertions also limit detection. These observations do not establish which component caused any real divergence.

Performance claims G9–G11 are qualified by active log size, transaction duration, checkpointing, storage speed and available recovery memory; the paper's benchmark hardware is evidence for measured results, not a universal required device model. User-data atomicity is expressly excluded. Checksums are finite and may be disabled by the chosen supported format, so detection claims never imply arbitrary-corruption protection. No requirement of whole-page atomicity or in-order completion was inferred: the code explicitly tolerates out-of-order writes and partial pages in the in-transit window.

No formal contract clauses, failure-model cells, prediction/scoring protocol or paired model/implementation brief were provided. This is a source enumeration only; no tests or outcome-bearing experiment were run and no commit was made, as BRIEF.md directs. Exhaustiveness remains a reading judgment; no external information was used.

Contract count: 68.

## Checkout inventory and status

Inventory below is `ls -R` with source/episode pruned; hidden entries are omitted by ls convention. Status is captured after creating this report; Temporary writing helpers have been removed.

```text
$ ls -R -I episode .
.:
AGENTS.md
BRIEF.md
GUARANTEES.md
enumeration.md
source

./source:
episode-1992.pdf
episode-1992.txt

$ git status
On branch main
Untracked files:
  (use "git add <file>..." to include in what will be committed)

	enumeration.md

nothing added to commit but untracked files present (use "git add" to track)
```
