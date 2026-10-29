# D2 judge packet 2 of 5 (cells, 1 of 3): Episode's log and recovery, against the sealed analysis

You are a judge. Work only from the text in this packet; do not read files, run commands or search.

Context: a component's log and recovery (`logbuf` in the Episode file system, OSF DCE 1.2.2) relies on contracts from the layers around it. Independent readers enumerated those contracts ("cells"); independent model authors then wrote TLA+ models and reported **findings**: violations of an obligation outside `logbuf` that break a stated guarantee of the log and recovery with the model's defences in place. A separate analysis, done before any of this and sealed, lists bugs, confirmed properties and an open item; it is given to you at the end of this packet, under "The sealed analysis". Items carry opaque ids; you are not told who wrote them. Packets are split by size by a stated rule; this one is part 2 of 5 (cells, 1 of 3).

Episode's criteria (fixed by Episode's steward 2026-10-26, before any list existed): a finding is a **match** for a sealed bug if it has the same violated contract, the same mechanism and the same class of effect; **partial** if it has the contract and one of the other two, or the right mechanism under a different contract; **no match** otherwise. A finding that claims a violation contradicting one of the sealed file's confirmed properties is **flagged** (name the property). A finding about the sealed file's open item is **unresolved**. A finding may match several bugs.

For **each cell**: does it name the violated contract that the sealed file records for some bug? Binary per cell; list the bugs if yes. A cell is a contract, not a finding; mechanism and effect do not matter here.

Answer schema: {"cells": [{"id": "C...", "names_contract_of": ["<sealed bug id>", ...], "reason": "<one sentence>"}]}  (empty list for no)

Answer with one JSON object only, as specified. Be concrete and brief; cite the sealed file's bug ids and the item's own words. Do not propose fixes. Disagreement with the sealed analysis is allowed: say so in `reason`.

## Cells

### C001
- contract: The device and the async veneer must report a failed or unreadable log or metadata transfer as an error, and must not return success for a page that was not stored or not read.
- source: logbuf/recover.c:788 " * log page is damaged; run salvager."
- violation: The driver returns a zero completion for a write it dropped, or returns old or zeroed data for a read that the media could not perform.
- at-risk: G5 and G7 fail because the log package panics only when it sees an error, and a false success lets it treat a missing log page as durable or replay garbage as metadata.
- detectable: partly — a reported error panics the log or raises recovery failure, but a false success is invisible.
- silent: 2 — drivers usually surface hard errors, but a dropped write reported as success shows up often enough on bad cables and failing disks to be more than rare.

### C002
- contract: Clients must choose a write-back mode that waits for data completion when they promise synchronous persistence.
- source: logbuf/logbuf.p.h:64 "elbb_syncLog, /* force write log, schedule buffer write, don't wait"
- violation: An upper layer returns synchronous success after elbb_syncLog or elbb_async while data is still in transit.
- at-risk: G15, G31, G35: these weaker modes do not imply the data buffer was written on return.
- detectable: partly — pending I/O is observable, but the caller’s intended external promise is not.
- silent: 2 — Confusing log synchronization with data synchronization is a plausible silent integration error.

### C003
- contract: The fast metadata modify path receives kernel addresses, and any user-address modify copies exactly the requested bytes or returns an error.
- source: logbuf/buffer.c:1703 " * assume along this code path that we never have user data (e.g. we"
- violation: A caller passes a user pointer to the fast path, or osi_copyin reports success after copying a different range.
- at-risk: G4 and G42 fail because the logged new value is not the value the caller meant to store, and recovery will redo that wrong value.
- detectable: partly — a user pointer on the fast path can fault; a short copyin that still returns zero is silent.
- silent: 1 — directory and anode updates use kernel buffers, and a bad copyin on these hosts is rare.

### C004
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

### C005
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

### C006
- contract: Clients retaining historical transaction IDs must retire them before ID wrap can make the same numeric ID identify unrelated work.
- source: logbuf/tran.c:1062 "elbt_GlobalTranId++;"
- violation: An old vnode or transactional lock retains a numeric ID across a complete 32-bit allocation cycle and later forces or merges an unrelated transaction.
- at-risk: G13, G23, G24: ID reuse can make a stale dependency or persistence check refer to the wrong work; the actual supported lifetime bound is uncertain.
- detectable: partly — generation-aware tracking could detect reuse, but a bare numeric ID is ambiguous.
- silent: 1 — Retaining an actionable ID across billions of transaction allocations is rare for the described workloads.

### C007
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

### C008
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

### C009
- contract: Device management must use one stable canonical async-device identity for each attached aggregate.
- source: logbuf/log.c:109 " LookupLogMap(dP, lmP); \"
- violation: Two descriptors name the same disk and permit independent log attachments or conflicting cache entries.
- at-risk: G1, G58: pointer-keyed attachment checks do not exclude a second writer through an alias.
- detectable: partly — external device identity checks can detect aliases; pointer lookup alone cannot.
- silent: 1 — Device aliases require unusual attachment management and often produce visible conflicting service.

### C010
- contract: A deployment that relies on crash consistency initializes the aggregate with logging turned on.
- source: anode/aggregate.c:1418 " * logged -- whether to turn on logging. Usually true, only false for some"
- violation: A mount or test harness calls epig_InitAggregate with logged false on an aggregate that users expect to survive a crash.
- at-risk: G1 and G4 fail because metadata updates are not logged, and recovery has nothing to replay.
- detectable: no — the flag is a legal argument, and the file system still serves reads and writes.
- silent: 1 — the kernel mount path passes logged true, and the false setting is described as a debug and test option.

### C011
- contract: The aggregate layer must keep the log-location array allocated and unchanged until the log is detached.
- source: logbuf/log.c:816 " lmP->logLocnArray = logLocnArray;"
- violation: A caller frees its temporary address array after LogInit returns.
- at-risk: G5, G7: the stored pointer then supplies arbitrary destinations for log I/O.
- detectable: partly — bad addresses may cause I/O errors, but valid misdirected destinations can pass.
- silent: 1 — Prematurely freed location arrays are uncommon caller defects and commonly fault or misdirect I/O visibly.

### C012
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

### C013
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

### C014
- contract: The CPU and compiler honor the log's 4-byte alignment rules for on-disk records and in-memory casts.
- source: logbuf/logrec.h:44 " * more strict alignment than is assumed here (i.e. all data"
- violation: A port to a machine that faults on the unaligned references the macros still perform, or a compiler inserts padding the on-disk layout does not have.
- at-risk: G4 and G42 fail because a record is stored or recovered at the wrong offset, so undo and redo patch the wrong bytes.
- detectable: partly — recovery raises RCVR_ALIGN when a pointer fails PTR_ALIGNED; a padded struct that is still 4-byte aligned is accepted.
- silent: 1 — the paper's SPARC and RS/6000 ABIs match the layout the 1992 code was written for.

### C015
- contract: Clients must not use quiesce’s captured position as proof that later concurrently issued updates have completed.
- source: logbuf/tran.c:1220 "when the caller (elbb_QuiesceSystem) started. Other activity is allowed"
- violation: An administrative operation quiesces and assumes all subsequent writers are also included without excluding them.
- at-risk: G32, G33, G38: quiesce guarantees only the captured transaction prefix, so later writes remain outstanding.
- detectable: partly — position and transaction tracking can identify excluded activity, but not the caller’s intended administrative boundary.
- silent: 2 — Misinterpreting a concurrent snapshot boundary need not raise an error.

### C016
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

### C017
- contract: Administrative tuning must preserve valid transaction, equivalence-class and log-capacity limits for attached devices.
- source: logbuf/log.c:2668 " /* XXX: go back and recompute for all active log maps. */"
- violation: An operator changes a global maximum and assumes existing log maps have been resized or re-reserved.
- at-risk: G17: configured limits and per-map reservations can diverge; the exact impact depends on the parameter.
- detectable: partly — value checks catch some invalid settings, but existing-map consistency is not fully recomputed.
- silent: 1 — Unsafe live tuning is unusual in ordinary operation and may visibly exhaust resources.

### C018
- contract: A later read of a block must return, sector by sector, the data of the last write to that sector that the driver has reported complete.
- source: logbuf/recover.c:892 " * We trust the log to make sure it doesn't assume a page with"
- violation: A drive cache, a multipath disk, or a host buffer returns a stale copy after a completed write, so recovery or the next mount sees an older log page.
- at-risk: G54 and G7 fail because the head, the pass number, or the redo records recovery reads are not the ones the running system forced.
- detectable: partly — a stale page often fails the pass-number or checksum test, and an older but well-formed page can be mistaken for the head.
- silent: 2 — coherent SCSI disks usually read what they just wrote, but stale cache and multipath windows are an occasional field failure.

### C019
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

### C020
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

### C021
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

### C022
- contract: The device layer must preserve a stable unique device identity and physical block mapping for the lifetime of cached buffers and transactions.
- source: logbuf/buffer.c:845 "sizeof(async_device_t *) +"
- violation: A device object is recycled for a different partition while old cache entries still use its pointer.
- at-risk: G1, G40, G42: cached data and log records can be applied to the wrong storage.
- detectable: partly — identity and lifetime instrumentation could detect reuse, but ordinary block I/O cannot establish it.
- silent: 1 — Normal aggregate open and close protocols avoid silent identity reuse.

### C023
- contract: Callers of the quick logged modify and of buffer fill must pass metadata that already resides in the kernel address space, never a user pointer and never file-body data.
- source: logbuf/buffer.c:1703 " * assume along this code path that we never have user data (e.g. we"
- violation: A caller points the fast modify path at a user address or at file contents, so the log record copies the wrong bytes or faults, and user data is written into the log.
- at-risk: G4 fails because the old and new images in the log are not the metadata update, and replay writes those wrong bytes back to a metadata block.
- detectable: partly — a bad user address can fault, but a readable wrong address is logged as success.
- silent: 1 — the fast-modify path is unused and the fill path is given kernel patterns, so this mis-call is rare.

### C024
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

### C025
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

### C026
- contract: The supplied logical device must retain its block size and address interpretation for its entire log attachment.
- source: logbuf/buffer.c:1004 " bpeP = GetBufferPool(dP->blkSize);"
- violation: A device descriptor is retargeted or its block size changes while buffers remain cached.
- at-risk: G1, G5: cached blocks and log addresses refer to different physical bytes.
- detectable: partly — some size checks exist, but descriptor identity does not certify stable mapping.
- silent: 1 — Live descriptor retargeting is exceptional and commonly causes visible addressing errors.

### C027
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

### C028
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

### C029
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

### C030
- contract: A deployment interpreting the recovery-time comparisons must keep active history, I/O performance, and available recovery resources comparable rather than scaling them with aggregate size.
- source: §"Recovery Time" "Episode's time to recover depends primarily on the size of the active portion of transaction log."
- violation: A larger aggregate is configured with much more active log history or a much slower recovery device.
- at-risk: G9–G11: replay cost depends on active pages and affected blocks, so aggregate-size-independent timing is conditional.
- detectable: yes — active-log size, affected-block count, and recovery timings can be measured.
- silent: 3 — Workload and device-speed variation commonly changes recovery time without a filesystem error.

### C031
- contract: After a crash the primary superblock must still be a valid aggregate header naming this log, because attach and the salvager do not fall back to an alternate superblock.
- source: anode/aggregate.c:1138 " * primary superblock, and since the salvager doesn't presently"
- violation: The only primary superblock is torn or unreadable, or its block size or log length no longer matches the device, and the alternate copies are ignored.
- at-risk: G58 fails because the log is never opened, so replay cannot run, and a superblock that points at the wrong log length or the wrong container makes replay use the wrong blocks.
- detectable: yes — a bad primary header fails aggregate open with a not-an-aggregate error.
- silent: 1 — the superblock is a single checked block written at format and grow, and losing it with no error at the disk is rare.

### C032
- contract: Storage must return the bytes last durably written to the requested address or report an error.
- source: logbuf/recover.c:1328 " readBlock(&buf, returnVal);"
- violation: A read silently returns stale data or data from another block.
- at-risk: G1, G50: recovery calculates repairs from the wrong home contents; metadata lacks a general checksum here.
- detectable: partly — log checksum and page-number checks catch some log misreads, not arbitrary home-block misreads.
- silent: 1 — Silent stale or misdirected reads are unusual relative to reads that report media errors.

### C033
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

### C034
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

### C035
- contract: Block addresses passed into the log and into recovery name blocks the device can read and write.
- source: logbuf/recover.c:1319 " if (returnVal != 0) panic("ReadData: bad read");"
- violation: A caller or a damaged log record names a block past the end of the device or on a hole the driver rejects.
- at-risk: G8 fails because recovery panics on the read and never writes the clean restart, and a metadata write during normal operation hits the same address.
- detectable: yes — readData and writeData panic, and the async path surfaces an I/O error.
- silent: 1 — legal allocators hand out in-range blocks, and an out-of-range address panics rather than succeeding quietly.

### C036
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

### C037
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

## The sealed analysis (v2, sealed 2026-10-27T18:15:54Z, before any finding existed)

# SEALED for tupay D2, version 2. Do not read unless you are judging the comparison.

Written by episode's steward (Claude Opus 5.5) on 2026-10-27, answering tupay's follow-up
(`docs/requests/2026-10-26-from-tupay-D2-followup.md`), before D2 phase 0.
**This file supersedes `sealed/2026-10-26-tupay-D2-findings.md` for judging.**
v1 stays in the history unchanged. v2 changes no bug. It adds, for each one, an
explicit effect class and a classification against D2's definition of an
environment contract (`tupay/experiments/D2/brief-enumerate.md`, Task: "an
obligation on something `logbuf` depends on ... **not** a rule of `logbuf`
itself"). It also makes the mechanism a field of its own. Where v1's wording
was loose, v2 says so.

Code: `/home/tony/projects/dce/dce/src/file/episode/logbuf` (DCE 1.2.2).
Models: `spec/` (see `spec/README.md`).

Effect classes: **silent-loss** (committed or acknowledged data gone, no error);
**silent-atomicity** (a partial or uncommitted change survives recovery, no
error); **silent-splice** (recovery accepts log pages from two runs as one log);
**exposure** (another owner's data becomes visible in a file); **fail-stop**
(recovery refuses or salvages; no wrong state is accepted).

Environment column: **env** = the bug is a violation of an obligation on something
outside `logbuf`; **own** = a defect in `logbuf`'s own rules, where the environment
behaves within what it promises.

| id | contract or assumption | mechanism | effect class | env / own | in a source comment |
|---|---|---|---|---|---|
| E1 | none violated. The I/O layer may complete log page writes out of order, and the code says it doesn't assume order | `log.c:2990` stores `io_window` as the *count* of pages in transit; recovery (SafeDumpLog) uses it as the *distance* back from the head to check. An older page still in transit after newer ones complete lies outside the count, so a missing page falls inside the scanned range | fail-stop (spurious `RCVR_IOERR`, salvager) | own | no |
| E2 | disk: a completed write is durable | the log treats a completed page write as stable; on a volatile write cache the page can be lost at power failure after commit is acknowledged | silent-loss (acknowledged commit) | env | yes (`recover.c:894`, wam 920624) |
| E3 | disk: a completed write is durable (includes: a write that completes *during* a flush is not covered by that flush) | a stolen uncommitted metadata page reaches media while its undo record, though "complete", is still only in cache; crash; recovery has no undo for it | silent-atomicity | env | yes (`recover.c:894`) |
| E4 | disk: a completed write was actually stored (no lost writes) | a lost metadata page write is masked by old/new redo until checkpoint truncation discards the redo record; metadata pages carry no parent-held version, so the stale page is never detected | silent-loss (committed update) | env | no |
| E5 | disk: a completed write is durable (here: the user data write covered by undo-zero) | OFILL correctly precedes the allocation's END; Z's END becomes durable while the user data sits in a volatile cache; crash; recovery keeps the allocation, does not undo-zero, and the block shows its old contents | exposure | env | yes (ordering at `log.c:1680`, wam 920805; device assumption at `recover.c:894`; the exposure is not stated) |
| E6 | none violated. Out-of-order completion is permitted (as E1), and a crash is an expected event | the clean-mount path starts pass R+1 at slot 0 without persisting it; after crash, out-of-order landing and a second clean mount, two runs' pages share a pass number and a valid checksum | silent-splice | own | partly (`recover.c:545` "+2 ... paranoia" anticipates it on the recovery path only) |
| E7 | none below `logbuf`; an internal invariant: every page on media is within half the pass range of the head | restarting at slot 0 on every mount leaves far slots unrewritten while the pass counter advances; the masked comparison in the head search can then read an old page as newer | fail-stop in the model (3-bit field: salvage). At 16 bits, argued only: the head is misidentified, and whether the result is fail-stop or silent is **not established** | own | no |

Counts: 7 bugs. env 4 (E2, E3, E4, E5); own 3 (E1, E6, E7).
Comment: 4 (E2, E3, E5, E6), of which env 3 (E2, E3, E5) and own 1 (E6).
All 7 carry contract-or-assumption, mechanism and effect class. E7's effect class is
given with its uncertainty, which matching must respect: for E7, either a fail-stop
or a silent wrong-head effect counts as the same effect class.

Corrections to v1's wording, not to substance:
- v1 gave E1 and E6 a "contract violated" of in-order completion. Under D2's
  definition that is wrong: the environment doesn't promise in-order completion,
  and `logbuf` doesn't rely on it by contract. The bugs are `logbuf`'s own.
- v1's E3 effect was descriptive; v2 classes it silent-atomicity.

Unchanged from v1 and not repeated here: the confirmed design properties P1–P6, the
open item O1, the out-of-scope list, and the visible-in-history column (0 of 7).
