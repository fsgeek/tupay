# D2 judge packet 5 of 5 (recognised lines and report notes): Episode's log and recovery, against the sealed analysis

You are a judge. Work only from the text in this packet; do not read files, run commands or search.

Context: a component's log and recovery (`logbuf` in the Episode file system, OSF DCE 1.2.2) relies on contracts from the layers around it. Independent readers enumerated those contracts ("cells"); independent model authors then wrote TLA+ models and reported **findings**: violations of an obligation outside `logbuf` that break a stated guarantee of the log and recovery with the model's defences in place. A separate analysis, done before any of this and sealed, lists bugs, confirmed properties and an open item; it is given to you {SEALED_WHERE}. Items carry opaque ids; you are not told who wrote them. Packets are split by size by a stated rule; this one is part 5 of 5 (recognised lines and report notes).

Episode's criteria (fixed by Episode's steward 2026-10-26, before any list existed): a finding is a **match** for a sealed bug if it has the same violated contract, the same mechanism and the same class of effect; **partial** if it has the contract and one of the other two, or the right mechanism under a different contract; **no match** otherwise. A finding that claims a violation contradicting one of the sealed file's confirmed properties is **flagged** (name the property). A finding about the sealed file's open item is **unresolved**. A finding may match several bugs.

These rows are what the enumerators wrote outside their enumerations: "recognised" lines (things they said they recognised from prior knowledge) and "report" notes. For **each row**: does it match a sealed bug (same contract and mechanism)? A match here is found by reading, not by the workflow.

Answer schema: {"rows": [{"id": "R..", "matches": ["<sealed bug id>", ...], "reason": "<one sentence>"}]}  (empty list for no)

Answer with one JSON object only, as specified. Be concrete and brief; cite the sealed file's bug ids and the item's own words. Do not propose fixes. Disagreement with the sealed analysis is allowed: say so in `reason`.

## Rows

### R01 (recognised)
OT 3435, recorded in logbuf/crc.c: out-of-order sector writes inside a log page made a torn page look valid, which is why page checksums were added; E3 is the contract that remains.

### R02 (report)
enumeration.md

### R03 (report)
``` On branch main Untracked files: (use "git add <file>..." to include in what will be committed) enumeration.md

### R04 (recognised)
E2 is the contract behind volatile disk write caches that report completion before the media is stable. I recall that failure mode from write-ahead logging practice of this era, including DFS and Episode deployments that enabled SCSI write caching without a battery.

### R05 (recognised)
OT 3804 and OT 1020, new-block security, recorded in the anode and logbuf history: a crash after allocation and before the first write exposed the previous contents; E36 and E38, and strategy.c still says the VM undo-zero path is not implemented.

### R06 (recognised)
E37 is the contract behind Episode new-block security. The logbuf locking history in this tree names it as OT 3804 and OT 1020, and anode/strategy.c still says the iodone undo-zero database is not implemented.

### R07 (report)
nothing added to commit but untracked files present (use "git add" to track) ```

### R08 (recognised)
OT 3338, recorded in the epimount history: the mount path did not recover a dirty log before the kernel attached it; that is E17.

### R09 (report)
nothing added to commit but untracked files present (use "git add" to track) ```

### R10 (report)
Whether the "undo-zero not yet implemented" comment in epia_Iodone is stale after the OT 3804 work. elbb_UndoZero has no caller in this tree, so I treated the VM gap as real and scored E37 accordingly.

### R11 (report)
Whether GetCleanLogInfo's inspection of block 0 alone is safe when log writes complete out of order. It looks safe if E2 holds and a force waits for every earlier in-transit page, but I did not follow every commit path far enough to be certain.

### R12 (report)
Could not decide:

### R13 (recognised)
Write-back disk caches that acknowledge a write before it is on media, the failure E2 names. I do not have an Episode defect number for it; it is the same class of bug as other write-ahead logs of the period.

### R14 (report)
./source: episode-1992.pdf episode-1992.txt

### R15 (report)
``` .: AGENTS.md BRIEF.md GUARANTEES.md enumeration.md source

### R16 (report)
48 contracts.

### R17 (report)
Source concerns kept out of the environment list: `logbuf/buffer.c` disables several logging-consistency assertions with `#if 0`; its logged ModifySource path logs before an address-space-dependent copy, raising an unresolved question about logged USER sources and copy faults; `logbuf/recover.c` deliberately accepts unknown checksum types without validating their checksum and does not checksum restart-only pages. `anode/strategy.c` says undo-zero completion processing is not yet implemented in that path; I cannot establish from that comment alone which supported VM ports obtain coverage elsewhere. These are implementation/integration questions, not evidence that an operator violated a contract. The external source-stability, coverage, and completion obligations still apply.

### R18 (report)
`ls -R --ignore=episode` from the checkout root (this leaves out `source/episode/`):

### R19 (report)
Defects in logbuf's own rules, kept out of the list:

### R20 (report)
The logbuf implementation itself may have defects; these are not environment contracts. In particular, elbb_UndoZero loops over a multi-block range without incrementing blkno (buffer.c:2440–2449), so its advertised cross-block coverage appears suspect. This is a static observation, not an executed or experimentally confirmed failure. The power-of-two comment in elbl_MinTranReservation is stronger than its mask assertion. Disabled logging-consistency assertions also limit detection. These observations do not establish which component caused any real divergence.

### R21 (report)
Whether a 16-bit pass-number wrap is its own obligation on log traffic. Each pass overwrites every log page, so a collision with an older pass also requires a lost write, which is E2. I left it out.

### R22 (report)
./source: episode episode-1992.pdf episode-1992.txt

### R23 (report)
``` .: AGENTS.md BRIEF.md GUARANTEES.md enumeration.md source

### R24 (report)
`git status`:

### R25 (report)
Restart pages are written without a checksum. The crash window is handled by the checkpoint-then-restart sequence, which still depends on E3.

### R26 (report)
Inventory below is `ls -R` with source/episode pruned; hidden entries are omitted by ls convention. Status is captured after creating this report; Temporary writing helpers have been removed.

### R27 (report)
nothing added to commit but untracked files present (use "git add" to track) ```

### R28 (report)
Performance claims G9–G11 are qualified by active log size, transaction duration, checkpointing, storage speed and available recovery memory; the paper's benchmark hardware is evidence for measured results, not a universal required device model. User-data atomicity is expressly excluded. Checksums are finite and may be disabled by the chosen supported format, so detection claims never imply arbitrary-corruption protection. No requirement of whole-page atomicity or in-order completion was inferred: the code explicitly tolerates out-of-order writes and partial pages in the in-transit window.

### R29 (report)
elbr_Recover panics when SafeDumpLog returns an error, despite the comment that recovery should return an error rather than panic.

### R30 (report)
./source: episode-1992.pdf episode-1992.txt ```

### R31 (report)
```text $ ls -R -I episode . .: AGENTS.md BRIEF.md GUARANTEES.md enumeration.md source

### R32 (report)
No formal contract clauses, failure-model cells, prediction/scoring protocol or paired model/implementation brief were provided. This is a source enumeration only; no tests or outcome-bearing experiment were run and no commit was made, as BRIEF.md directs. Exhaustiveness remains a reading judgment; no external information was used.

### R33 (recognised)
<!-- derives: BRIEF.md recognition rule; logbuf/logbuf-locking revision history; anode/strategy.c:456. --> I do not independently recall a specific published Episode/DFS incident behind these contracts. The supplied revision history itself reports new-block-security work (OT 3804/1020), transaction/waiting fixes (OT 5508/5249/4548), fsync work (OT 5316), and pass-number fixes (OT 5527); these are source evidence, not personal recollections, and are not the organizing basis of the list.

### R34 (report)
The silent score for E2. I do not know the write-cache default on the paper's Seagate ST1239NS and IBM 0661, so 3 is a judgment from the period rather than a measurement.

### R35 (report)
nothing added to commit but untracked files present (use "git add" to track) ```

### R36 (report)
./source: episode-1992.pdf episode-1992.txt ```

### R37 (report)
`ls -R` of the checkout, with `source/episode/` pruned:

### R38 (report)
```

### R39 (recognised)
DB 3189, in tran.c: an optional compile forces every metadata transaction to commit before return. I did not list it, because with the option off the code matches the paper's rule that metadata may stay deferred until fsync.

### R40 (report)
`ls -R --ignore=episode .`

### R41 (report)
Contract count: 68.

### R42 (report)
Defects in `logbuf`'s own rules, not listed as contracts: an unknown checksum version is accepted and the check is skipped (recover.c around the message that the checksum is ignored), so E49 is only partly enforced. The restart page is deliberately not checksummed. The asserts that a logged buffer's updates are either all logged or all unlogged are compiled out. elbb_FastModify does not go through elbb_StartTran when the log is full; its comment says no caller uses it. The comment above user-space recovery says both that the code must run single-threaded and that locking was removed so several recoveries may run at once. The comment on MAX_TRAN_SIZE says 35K; the constant is 70 times 1024.

### R43 (recognised)
OT 4548, recorded in logbuf/logbuf-locking: the fixed transaction reservation was too small for real callers; that is E29 and E30.

### R44 (report)
```text On branch main Untracked files: (use "git add <file>..." to include in what will be committed) enumeration.md

### R45 (report)
50 contracts, E1 through E50.

### R46 (report)
The exact admissible maximum log length, cross-device block-size combinations, and supported cross-platform on-disk compatibility are not established here; 16-bit page/offset fields and native structure casts impose limits, but asserting a precise unverified deployment bound would overstate the evidence. The combined nested reservation must follow actual source settings: the code defines MAX_TRAN_SIZE as 70 KiB in this build, while an older nearby comment still says 35K. No actual failure frequencies, benchmark outcomes, or new defect claims were established. Similar storage-integrity contracts are split where their failure and detection mechanisms differ.

### R47 (report)
NewLogPage ignores the return value of asevent_QueueIO and still marks the log page in transit.

### R48 (report)
`git status`

### R49 (report)
An unknown checksum version is treated as valid and the page is accepted. That weakens G54 instead of failing recovery.

### R50 (report)
``` On branch main Untracked files: (use "git add <file>..." to include in what will be committed) enumeration.md

### R51 (report)
I could not decide three points. Dirty zero pages from efs_MakeWritableBlocks do not by themselves meet the paper's zero-on-abort rule, because they vanish on a crash unless they were written, so I kept E36 and E38; I am not sure the authors still considered the VM undo-zero record required once those pages existed. logbuf-locking names OT 5527 as a pass-number bug exposed by a test; I did not decide whether that bug is an environment contract, and the pass-number arithmetic itself is logbuf's rule. The silent score on E2 depends on how often the paper's SCSI disks had write-back caches enabled, which these sources do not say.

### R52 (report)
During a kernel panic, elbb_SyncForce returns immediately when the buffer lock or the log lock is held, and elbb_StartTran gives up after three loops. That narrows G41 and G28 on the panic path.

### R53 (report)
```text .: AGENTS.md BRIEF.md GUARANTEES.md enumeration.md source

### R54 (recognised)
I do not recall a specific reported Episode or DFS bug independently of these sources. The supplied history mentions OT 3804/1020 (new-block security), OT 5508 (transaction waits), OT 5316 (FsyncForce), OT 4548 (reservations), and OT 5527 (pass numbers); these are source observations, not independent recalled reports. Volatile write-cache acknowledgements are a familiar filesystem failure pattern, without a particular report recalled.

### R55 (report)
$ git status On branch main Untracked files: (use "git add <file>..." to include in what will be committed)

### R56 (recognised)
I recognise the pass-number comparison work named as OT 5527 in that same history as an internal log bug, so I did not make a separate environment contract for it.

### R57 (report)
<!-- derives: BRIEF.md final-report requirement. --> Contracts: 74.

### R58 (report)
<!-- derives: BRIEF.md environment boundary; logbuf/recover.c:745; logbuf/logrec.h:231; anode/strategy.c:456. --> The code does not assume whole-log-page atomic writes or in-order completion of different outstanding log pages: it explicitly handles an in-transit window. Sector atomicity and truthful completion are distinct obligations. Ordinary user-data transaction atomicity is expressly excluded by the paper. A caller obeying the interface is not proof of a correct logbuf implementation.

### R59 (report)
`git status`:

### R60 (recognised)
OT 3802, recorded in anode/volume_table.h: a fileset path had no tlock, so equivalence classes were not merged; that is E32.
