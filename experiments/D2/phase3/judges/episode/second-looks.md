# Second looks at D2's findings, against episode's own analysis

episode's steward (Claude Opus 5.5), 2026-11-03, after the rulings (`4fd2c09`)
and after D2 was published. This file answers item 3 of
`tupay/docs/requests/2026-10-29-to-episode-D2-rulings.md`.

**Method and limits.** Each claim was checked by reading DCE 1.2.2
(`dce/src/file/episode/`), and for F07 also my own `spec/WrapLog.tla`. Nothing
here was executed or model-checked. "Confirmed" means the cited code does what
the finding says, and I could find nothing in the code that prevents it. It does
not mean I reproduced it.

| item | verdict | against episode's analysis |
|---|---|---|
| F01 | **confirmed by reading; worse than stated** | a defect my analysis missed |
| F07 | **confirmed by reading; my model's gap identified** | refutes a claim in the sealed note on E6 |
| F06 | trace as written unreachable; **effect reachable another way** | corrects my E4 commentary |
| F02 | confirmed | not in my analysis (configuration, rare) |
| F09 | confirmed as described; a documented design choice | not in my analysis |
| F04 | **not confirmed as stated**; reachable only through F01 | — |
| R20 | confirmed; latent (no caller) | not in my analysis |
| R47 | confirmed; consequence not analysed | not in my analysis |

## F01: commit test aliases after a full lap. Confirmed, and worse.

- **The arithmetic** is exactly as the finding states. `TranCommitted` and
  `BufCommitted` (`log.c:264`, `:276`) compare against
  `(EarlierPassno(activeLogBlock), activeLogBlock)`. `EarlierPassno(off)`
  (`log.c:252`) returns the *current* pass whenever `off >= currentLogBlock`.
  `activeLogBlock` is the oldest page in transit (`RecycleLogBufs`, `log.c:2591`).
  Once `currentLogBlock` reaches the index of a page still in transit from the
  previous lap, that page is taken to be a lap newer than it is. Every position
  before it in the current lap then counts as committed, including pages still
  in transit. `elbl_ForceTran` (`log.c:2052`) then returns without forcing.
- **Can the log reach a page that's still in transit?** Yes, because nothing
  holds the tail for it. The tail is set by `tranAgeQ` and `bufferAgeQ` only
  (`ComputeActiveLog`, `log.c:3036`). The module's own table (`log.c:125–145`)
  shows `elbl_CompleteTran` taking a transaction *off* `tranAgeQ` when it ends,
  not when it commits. So an ended transaction whose END record sits on the
  stalled page doesn't hold the tail. A dirty buffer with a record on that page
  does (write-ahead keeps it dirty), but a page holding only END records doesn't
  have one. That's the normal result of a forced commit. When nothing holds the
  tail, `activeSize` "should be (stay at) one" (`log.c:3011`), and the log laps
  freely. `NewLogPage` advances into the slot without checking whether its
  previous write is still in transit (`log.c:3007–3024`).
- **Worse than stated:**
  (a) The window isn't one instant. It lasts for every `currentLogBlock >= k`
  until the stalled page completes.
  (b) A second write to the same disk block is issued while the first is still
  outstanding. If the device completes the older one last, the previous lap's
  page overwrites the new one. That's a separate hazard, not in the finding.
  (c) `elbb_TranIsCommitted` relies on the same test, which is how F04 becomes
  reachable (below).
- **Classification:** logbuf's own defect. A long stall is behaviour the
  environment is allowed, and nothing in the code bounds it. The effect is silent
  loss of an acknowledged forced commit. It's rare: one log write has to stay
  outstanding while the log writes a full lap (at least 13 pages, per the
  finding).
- **Why my analysis missed it:** none of my models has the
  `activeLogBlock`-based commit test, or log wrap-around within one mount, with a
  page in transit.

## F07: the checkpoint is written into the hole. Confirmed, and my model couldn't see it.

- `elbr_Recover` step 5 (`recover.c:521–549`) writes the checkpoint block at
  `head+1` with `passNum = lastPageHdr->passNumber`, the **old** pass. Only the
  restart block gets `+ 2`. If the head was pulled back over a hole, the
  checkpoint fills the hole with a valid checksum and the old pass, so a stale
  page beyond it, with the same pass, now looks contiguous. If recovery is
  interrupted between the two writes, the next recovery can take the stale page
  as head and partly redo a transaction the first recovery undid. That's the
  finding's mechanism.
- **The sealed note on E6 overstated the case.** It said the "+2 ... paranoia"
  comment "anticipates the hazard on the recovery path". The +2 protects the
  restart block only, not the checkpoint.
- **Why WrapLog passed:** its `MountRecover` action writes the checkpoint and the
  restart block in **one atomic step** (`spec/WrapLog.tla:118–121`, `m1` then
  `m2`). A crash between them can't happen in the model. The spec README's "crashes
  anywhere" was false for this step.
- **Classification:** logbuf's own defect, under permitted out-of-order
  completion plus a crash inside recovery's two-write window. The effect is silent
  partial redo. It's rare, but recovery is exactly when crashes and restarts
  cluster.

## F06: the trace needs a page rewrite Episode doesn't do. The effect doesn't.

- The trace has the head read returning "the previous well-formed page" of the
  same slot, holding the update but not the END. Episode never rewrites a log
  page: `ForceMap` seals a non-empty current page with `NewLogPage`
  (`log.c:2158–2161`). So no earlier same-pass version of a page exists, and my
  model's "sealed once" abstraction is faithful.
- **The effect is reachable anyway.** A stale read of the head page returns the
  previous lap's page. Its older pass makes it look unwritten, recovery stops one
  page short, and a committed transaction whose END was on that page is undone.
  This is a consequence of a contract violation (C018), not a code defect, and it
  can't be avoided without a version held outside the page.
- **It corrects my E4 commentary**, which said Episode's log pages had "the same
  idea" as a parent-held version (CRC plus pass number). For the newest page they
  don't: a stale newest page can't be told apart from an unwritten one.

## The rest

- **F02, confirmed.** `recover.c:2577–2583` sets `result = 1` for an unknown
  checksum type and prints the warning once. The version is fixed when the log is
  created, so this needs an operator, a tool or a mismatched binary.
- **F09, confirmed as described.** The restart page is written unchecksummed by
  design (`recover.c:2737`). The clean test is the magic number plus a RESTART
  first record, with the checksum version checked but not the checksum
  (`recover.c:2826–2840`). Bit rot that produces exactly that is improbable. A
  forged or restored restart block (patchlog, an operator, a restore) is the
  realistic path.
- **F04, not confirmed as stated.** `block_alloc.c:450` passes `metadataOK = 1`
  only inside `fb_CheckTrans`, after `elbb_TranIsCommitted` returns true
  (`block_alloc.c:432`). This tree's caller keeps the contract. But
  `elbb_TranIsCommitted` uses `TranCommitted`, so during an F01 window the guard
  is wrong, and F04's effect follows. That composition is argued, not traced.
- **R20, confirmed and latent.** `elbb_UndoZero`'s loop (`buffer.c:2440–2449`)
  never advances `blkno`, so a multi-block range logs OFILL for the first block
  repeatedly and leaves the rest uncovered. Nothing outside `buffer.c` calls it in
  this tree. That's consistent with R10 and with `strategy.c`'s "not yet
  implemented".
- **R47, confirmed.** `log.c:3002` discards `asevent_QueueIO`'s return and marks
  the page in transit regardless. What follows from a queueing failure depends on
  how `asevent_QueueIO` can fail, which I haven't analysed.

## What this does to episode's analysis

Two of D2's findings expose defects my analysis missed (F01, F07). One of them
(F07) sat in a step my model made atomic. One more (F06) corrects a claim I made
in passing. The cheapest next evidence would be executed models: put the
`activeLogBlock` commit test and tail-holding into EpisodeLog for F01, and split
`MountRecover` into two writes for F07. I'll do that if tupay or Tony wants
evidence that has actually been run, not just read.
