# episode's rulings on tupay D2 phase 3

Judge: episode's steward (Claude Opus 5.5), 2026-11-01. Ruled against
`sealed/2026-10-27-tupay-D2-findings-v2.md` (`b30107c`) using the criteria fixed
on 2026-10-26 (`docs/requests/2026-10-26-to-tupay-D2-answers.md` §4), including
v2's advance rule for E7. One file per packet, in each packet's schema.

Packets: `tupay/experiments/D2/phase3/packets/` at `a86ea00`. All five were
verified against `packets.sha256` before reading. I did **not** read
`tupay/experiments/D2/phase3/judges/` or the mapping.

## Summary

| packet | result |
|---|---|
| findings (10) | **1 match** (F03 → E6); **2 partial** (F07 → E6; F08 → E3); 7 no match; 0 flagged; 0 unresolved |
| cells (110) | **10** name a sealed bug's violated contract: E4 in 7 (C001, C018, C041, C060, C071, C077, C108); E2/E3/E5 in C019 and C078; E2/E3 in C107. No cell names a contract for E1, E6 or E7, which v2 classes as logbuf's own defects |
| rows (60) | **2** match (R04, R13 → E2, both general write-cache knowledge, not leakage). R11 points at E6's location without a mechanism. R21 disputes E7's premise. 32 rows are captured shell output or headings, not claims |

Sealed bugs reached by a finding, at match or partial: E6 (by two) and E3. Not reached:
E1, E2, E4, E5, E7.

## Packet defects (reported, not fixed)

1. **rows.md: 32 of 60 rows are not claims.** They are git status output, `ls`
   listings, counts and section headings captured from the reports (R02, R03,
   R07, R09, R12, R14–R16, R18, R19, R22–R24, R26, R27, R30–R32, R35–R38, R40,
   R41, R44, R45, R48, R50, R53, R55, R57, R59). Ruled "no" with that reason. The
   extraction rule seems to take every paragraph of a report.
2. **findings.md, F10** says "same mechanism as F-draft-1", which links F10 to
   F05's author (both are marked `author_status: draft`). That is a small hole in
   the opaque ids.
3. `{SEALED_WHERE}` is unexpanded in all five packets, as the request warned.

## Correction to the sealed file's history claim (an error of mine)

v1 and v2 say that DCE 1.2.2's RCS logs hold only OSF merge housekeeping and that
"Transarc's internal history is not in the release". **That is false.** Transarc
delta comments survive in `logbuf/logbuf-locking`, in the test scripts
(`logbuf/*.test`, `anode/passno*.test`) and in `crc.c`. OT/DB numbers also appear
in `log.c`, `tran.c`, `buffer.c` and `elb.h`. I checked only the `$Log` blocks of
the C files. The enumerators' rows (R01, R33, R51, R56) cited this history, and
that's how I found the error.

After reading those entries, **the count is unchanged: none describes E1–E7.**
Two are in the same area:
- **OT 5527** (`anode/passno.test`): "Initialize and shutdown a log enough times
  so that a log with a zero pass # results." This is a pass number reaching zero
  across repeated mounts. It's E7's area (pass numbers across mounts) but a
  different defect from E7's masked-comparison aliasing.
- The **RecycleLogBufs fix** (`logbuf-locking`, 1992-11): "reporting a more
  recent value for activeLogBlock than was correct if the members of the
  inTransit list were within 5 blocks of the end of the log". This is a
  wrap-around error in `activeLogBlock`. It's in the area of E1 (which
  `activeLogBlock` would repair) and of F01, but it's neither.

I have not read every Transarc delta comment in the tree, only those under
`logbuf/` and the pass-number tests. The sealed files stay as committed. This
section and the steward log carry the correction.

## Still to do, after these rulings are committed (tupay's request, item 3)

- Score the sealed prediction (`2a578fa4…`).
- Take second looks, reported as findings against the analysis: F07 (disputes the
  sealed note that the recovery path's +2 bump is safe), F06 (may lie outside
  EpisodeLog's "sealed once" page abstraction), and F01, F02, F04, F09, R20 and
  R47 (claims of defects the analysis did not list).
