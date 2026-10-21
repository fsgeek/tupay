# Specification F: a replicated journal with single-member configuration changes

This is the design you are to build, exactly as written. It is not a contract you may satisfy by any design you like: where this specification says how something is done, do it that way, even if you believe another way is better. If you find a place where you think the design is wrong, do not fix it; record it in your README as an interpretation or a concern, and build what is written. Where the specification is silent, choose, and record the choice.

## Vocabulary
- **Member.** A process that stores a journal and takes part in agreement. Members are named `m1`, `m2`, … .
- **Journal.** A sequence of entries, indexed from 1. Each entry carries the **epoch** in which it was first appended and a payload. A payload is either a **command** (opaque) or a **configuration** (a set of member names).
- **Epoch.** A non-negative integer each member stores, 0 when the member first starts. Epochs only increase.
- **Coordinator.** A member that has won an election for its current epoch. Other members are **followers** or **candidates**.
- **Configuration of a member.** The payload of the latest configuration entry in that member's journal, whether or not that entry is committed. If the journal has no configuration entry, the member's configuration is the initial configuration it was started with.
- **Majority of a configuration C.** Any set containing more than half of the members of C.
- **Committed.** An entry is committed once the coordinator that appended it, or a later coordinator, has applied the commitment rule below to it or to a later entry.

## State each member keeps
Durable (survives a crash): `epoch`, `votedFor` (a member name or none, for the current epoch), `journal`. Durable state is written to stable storage before the member responds to any request.
Volatile (lost on a crash, reset on restart): `role` (follower on restart), `commitIndex` (0 on restart), and, for a coordinator, `nextIndex` and `matchIndex` for each other member.

## Messages
Every message carries the sender's `epoch`. On receiving any message with an epoch higher than its own, a member sets its `epoch` to that value, clears `votedFor`, and becomes a follower, before processing the message further. A member ignores a request whose epoch is lower than its own, replying with its own epoch. Requests and replies may be lost, delayed or reordered. A member that gets no timely reply to a request retries it; requests to different members are sent in parallel.

Members process incoming requests without consulting their own configuration. In particular a member grants votes to, and accepts journal extensions from, members that are not in its configuration.

### Election
- Each member's election timeout is chosen at random from a fixed range. A follower's timer is reset when it receives an extend request from the current coordinator or grants a ballot. A follower or candidate whose timer expires becomes a **candidate**: it increments `epoch`, sets `votedFor` to itself, resets its election timer, and sends a **ballot request** to every other member of its own configuration, carrying the index and epoch of its last journal entry.
- A member grants a ballot if (a) the request's epoch is at least its own, (b) it has not voted for a different member in that epoch, and (c) the candidate's journal is at least as up to date as its own: the candidate's last entry has a higher epoch, or the same epoch and an index at least as large. When it grants, it records `votedFor` durably before replying.
- A candidate that receives grants from a majority of its own configuration (counting itself if it is a member of it) becomes coordinator of that epoch. A candidate that hears from a coordinator of an epoch at least its own becomes a follower.

### Journal extension
- A coordinator sends each other member of its configuration an **extend request**: the index and epoch of the entry immediately before the entries it sends (`prevIndex`, `prevEpoch`), zero or more entries, and the coordinator's `commitIndex`. The entries sent to a member start at that member's `nextIndex`, so `prevIndex` is `nextIndex` − 1; with no entries the request serves as a heartbeat. The coordinator retries extend requests to a member indefinitely until the member stores every entry.
- A receiver whose journal has no entry at `prevIndex` with epoch `prevEpoch` replies failure. Otherwise it deletes any existing entry that conflicts with a sent entry (same index, different epoch) together with all entries after it, appends the sent entries it does not already have, and, if the coordinator's `commitIndex` is greater than its own, sets its `commitIndex` to the smaller of the coordinator's `commitIndex` and the index of the last entry the request carried (`prevIndex` plus the number of entries sent); `commitIndex` never decreases. It replies success. A `prevIndex` of 0 always matches. If entries it deleted included a configuration entry, its configuration falls back to the latest configuration entry that remains.
- On becoming coordinator, a member sets `nextIndex` for every other member to its last journal index plus one and `matchIndex` to 0, and sends heartbeats at a regular interval shorter than the election timeout. On failure it decrements `nextIndex` for that member and retries; on success it sets that member's `matchIndex` to the index of the last entry the request carried, and `nextIndex` to one more than that.

### Commitment rule
Whenever there is an index N greater than its `commitIndex` such that (a) the entry at N carries the coordinator's current epoch, and (b) a majority of the coordinator's configuration (counting the coordinator if it is a member) have `matchIndex ≥ N`, the coordinator sets `commitIndex` to N, marking the entry at N committed. Committing N commits every earlier entry. Entries from earlier epochs are therefore committed only indirectly, when a later entry of the current epoch is committed.

## Configuration changes
Configurations are entries in the journal and are replicated like any other entry.
- A configuration takes effect on a member as soon as the entry is in its journal, before it is committed. Every member always uses the latest configuration in its journal, for elections and for commitment.
- The commitment of a configuration entry is decided by a majority of the new configuration it contains.
- A change adds exactly one member to, or removes exactly one member from, the configuration in which it is made; larger changes are made as a series of such changes. The design restricts changes to one member at a time because any majority of the old configuration then overlaps any majority of the new one, so the cluster cannot split into two independent majorities.

### Adding a member (handled by the member that receives the request)
1. If not the coordinator, reply "not coordinator".
2. Catch the new member up for a fixed number of rounds of extend requests. Reply "timeout" if the new member does not make progress for an election timeout, or if the last round takes longer than an election timeout. If the new member's journal already matches the coordinator's, catch-up is complete at once.
3. Wait until the previous configuration entry in the coordinator's journal is committed.
4. Append a configuration entry containing the current configuration plus the new member; commit it using a majority of the new configuration.
5. Reply "ok".

### Removing a member
1. If not the coordinator, reply "not coordinator".
2. Wait until the previous configuration entry in the coordinator's journal is committed.
3. Append a configuration entry containing the current configuration without the removed member; commit it using a majority of the new configuration.
4. Reply "ok". If the coordinator removed itself, it steps down after the entry is committed.

A coordinator does not begin a new change while the previous configuration entry in its journal is uncommitted.

## What the design does not include
Client requests other than commands and configuration changes; reads; snapshots or journal compaction; non-voting members. A command is an opaque payload appended by the coordinator on request.
