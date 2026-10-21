# Replay contract: a replicated journal (safety)

Version 2, 2026-10-21 (version 1 the same day). Clause ids are never reused: J1.2 is retired, and a tag naming it is stale. Both arms build to this contract; each arm's specification (`spec-D.md` or `spec-F.md`) says how.

## Terms
Member, journal, entry, epoch, coordinator, configuration and committed are as defined in the arm's specification. An entry is **committed** when a coordinator marks it committed (its commit index reaches the entry's index); a member records the moment it learns of it.

## Clauses
- **J1.1 (one coordinator per epoch).** At most one member is coordinator in any given epoch, over the whole run.
- **J1.4 (committed entries persist).** If a coordinator commits the entry at index i in epoch e, then (a) every member that is elected coordinator in an epoch higher than e has that entry at index i when it is elected, and (b) no member that holds that entry at index i ever removes it from index i.
- **J1.3 (one change at a time).** Every configuration entry differs from the configuration entry that precedes it in the same journal (or from the initial configuration, for the first) by exactly one member added or removed.

J1.1 and J1.4 are safety properties of the system. J1.3 is a property of each journal and holds by construction if the specification is followed. There is no liveness clause in this contract.

Retired: **J1.2** (version 1), "if an entry is committed at index i, then from then on every member's journal that has an entry at index i has that same entry there, and every member that becomes coordinator afterwards has that entry at index i". Its first half is violated by a member that still holds a stale, uncommitted entry at an index committed elsewhere, which the design allows; J1.4 states what was meant.

## Observable events
Each recorded by the member it concerns, with that member's own sequence number and `causes` links, in the format of `replay/observe.md`:
`Elected(member, epoch, config)`, `Appended(member, index, epoch, kind, payload)` (kind is `command` or `config`), `Truncated(member, from_index)`, `Committed(member, index, epoch)`, `ConfigInEffect(member, config, index)`, `ChangeRequested(member, op, target)`, `ChangeReplied(member, op, target, status)`.
