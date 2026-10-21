# Replay failure model

Version 1, fixed 2026-10-21 for the known-bug replay. Cell ids are never reused.

The system has five member names, `m1` to `m5`. A run starts with an initial configuration given by the scenario (for example `{m1, m2, m3, m4}`); members not in it are started with the initial configuration too, and an empty journal, so that they can be added. Configuration change requests come from an administrator, at any member, at any time.

## Cells
- **G1.1 Crash and restart.** Any member may stop and later restart with its durable state (`epoch`, `votedFor`, `journal`) and nothing else.
- **G1.2 Message loss, delay, reordering and duplication.** Any message may be lost, delayed for any finite time, delivered out of order, or delivered more than once. Messages are never corrupted.
- **G1.3 Partition.** Links between members go down and come back, in either or both directions; while a link is down, messages sent over it are lost. (This is G1.2 applied systematically; it is a separate cell so that scenarios can name it.)
- **G1.4 Administrative change.** An add or remove request may arrive at any member at any moment. A request that the receiving member rejects or that times out may be retried at another member.

Timeouts are the only clocks; no member's clock is compared with another's.

## Not in this model
Byzantine behaviour, storage loss or corruption, clock skew beyond arbitrary timeouts, non-voting members, snapshots.
