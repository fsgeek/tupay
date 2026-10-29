{"findings": [
  {
    "id": "F01",
    "ruling": "no match",
    "bugs": [],
    "flag_confirmed_property": null,
    "reason": "F01 relies on out-of-order log write completion (like E1 and E6) where page 0 remains in transit for a full lap of the log so `EarlierPassno(activeLogBlock)` wraps in `TranCommitted`/`BufCommitted`, causing `elbl_ForceTran` to return early and losing an acknowledged commit (`silent-loss`, like E2). None of the sealed bugs has this full-lap `activeLogBlock` wrap mechanism in runtime commit checks: E1 is the `io_window` count-versus-distance bug in `SafeDumpLog` (`fail-stop`), E6 is clean-mount pass reuse (`silent-splice`), and E2 is loss of a completed write from a volatile cache."
  },
  {
    "id": "F02",
    "ruling": "no match",
    "bugs": [],
    "flag_confirmed_property": null,
    "reason": "F02 violates C021 when a torn log page carries `UNKNOWN_CKSUM_TYPE`, causing `ValidLogPageChecksum` (recover.c:2577) to force checksum success and replay uncommitted data. None of E1–E7 involves checksum version configuration, `UNKNOWN_CKSUM_TYPE`, or fail-open checksum validation on torn pages."
  },
  {
    "id": "F03",
    "ruling": "match",
    "bugs": ["E6"],
    "flag_confirmed_property": null,
    "reason": "F03 matches E6 in assumption, mechanism, and effect class. Both start from permitted out-of-order log page completion and a crash before page 0 overwrites the restart block, so `elbr_GetCleanLogInfo` sees a clean log and reopens with `IncPassno(restart pass)` (pass R+1) without recovery; after a second crash, stale and new pages share the same pass number and valid checksums, splicing records across incarnations (`silent-splice`)."
  },
  {
    "id": "F04",
    "ruling": "no match",
    "bugs": [],
    "flag_confirmed_property": null,
    "reason": "F04 violates C024 by calling `elbb_Kill` with `metadataOK` set to true on a dirty logged buffer, dropping the buffer from the age queue so checkpointing advances past a committed update that never reached its home block. Although the effect is `silent-loss` of a committed update (like E4), E4 is caused by a lost disk write to a metadata home block rather than caller misuse of `elbb_Kill`."
  },
  {
    "id": "F05",
    "ruling": "no match",
    "bugs": [],
    "flag_confirmed_property": null,
    "reason": "F05 violates C088 when an external overwrite corrupts a completed head log page and `SafeDumpLog`'s in-transit window scan (recover.c:940-975) treats the bad checksum as an incomplete write, pulling the head back and losing a committed transaction (`silent-loss`). While it shares the `silent-loss` effect class of E2, neither the violated contract (C088 log container exclusivity/fixed mapping) nor the mechanism (checksum failure masked by the `io_window` pullback) matches E1–E7."
  },
  {
    "id": "F06",
    "ruling": "match",
    "bugs": ["E2"],
    "flag_confirmed_property": null,
    "reason": "F06 violates C018 when the storage stack fails to return the last completed write at the log head and instead returns the previous well-formed page lacking the transaction's END record, so recovery undoes a committed transaction (`silent-loss`). This matches E2's contract (completed log writes are durable/visible after completion), mechanism (the log treats a completed page write as stable on disk, and when the newly completed head page is missing at recovery, the committed transaction is lost), and effect class (`silent-loss`)."
  },
  {
    "id": "F07",
    "ruling": "partial",
    "bugs": ["E6"],
    "flag_confirmed_property": null,
    "reason": "Like E1 and E6, F07 assumes only permitted out-of-order log page completion (leaving a hole at page 1 before a completed page 2) plus crashes, and like E6 it produces a `silent-splice` / `silent-atomicity` effect where stale page 2 from before the first crash is joined into the active log after a second crash. However, its mechanism bridges the hole via `elbr_WriteCheckpointBlock` writing head+1 with the same pass number before `elbr_WriteRestartBlock` completes, rather than E6's clean-mount `IncPassno` reuse."
  },
  {
    "id": "F08",
    "ruling": "match",
    "bugs": ["E3"],
    "flag_confirmed_property": null,
    "reason": "F08 violates C041 when AIX `asevent_Iodone` clears `ESOFT` on a log write that was not stored, reporting the log force complete so write-ahead allows the dirty uncommitted metadata home block to be written to disk before a crash. This matches E3 (and shares E4's false-completion contract): a 'completed' undo log write is not actually durable on media while the uncommitted metadata home page reaches disk, leaving recovery with no undo record (`silent-atomicity`)."
  },
  {
    "id": "F09",
    "ruling": "no match",
    "bugs": [],
    "flag_confirmed_property": null,
    "reason": "F09 violates C058 by planting or restoring an unchecksummed restart image on the first log block after an uncommitted metadata home block write, causing `elbr_GetCleanLogInfo` to treat the dirty log as clean and skip recovery. None of E1–E7 involves forged or unchecksummed restart markers suppressing recovery."
  },
  {
    "id": "F10",
    "ruling": "partial",
    "bugs": ["E2"],
    "flag_confirmed_property": null,
    "reason": "F10 violates C071 (the storage stack must preserve completed writes) when bits of a completed head log page decay, and shares E2's `silent-loss` effect on an acknowledged commit. It is a partial match for E2 because it shares the violated durability contract and effect class, but its mechanism relies on bit rot triggering a bad checksum inside `SafeDumpLog`'s in-transit window pullback rather than a volatile write cache losing a whole page at power failure."
  }
]}
