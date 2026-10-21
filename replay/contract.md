# Replay contract: a replicated journal (safety)

Version 1, fixed 2026-10-21 for the known-bug replay. Clause ids are never reused. Both arms build to this contract; each arm's specification (`spec-D.md` or `spec-F.md`) says how.

## Terms
Member, journal, entry, epoch, coordinator, configuration and committed are as defined in the arm's specification. An entry is **committed** when a coordinator marks it committed (its commit index reaches the entry's index); a member records the moment it learns of it.

## Clauses
- **J1.1 (one coordinator per epoch).** At most one member is coordinator in any given epoch, over the whole run.
- **J1.2 (committed entries persist).** If an entry is committed at index i, then from then on every member's journal that has an entry at index i has that same entry there (same epoch, same payload), and every member that becomes coordinator afterwards has that entry at index i.
- **J1.3 (one change at a time).** Every configuration entry differs from the configuration entry that precedes it in the same journal (or from the initial configuration, for the first) by exactly one member added or removed.

J1.1 and J1.2 are safety properties of the system. J1.3 is a property of each journal and holds by construction if the specification is followed. There is no liveness clause in this contract.

## Observable events
Each recorded by the member it concerns, with that member's own sequence number and `causes` links, in the format of `replay/observe.md`:
`Elected(member, epoch, config)`, `Appended(member, index, epoch, kind, payload)` (kind is `command` or `config`), `Truncated(member, from_index)`, `Committed(member, index, epoch)`, `ConfigInEffect(member, config, index)`, `ChangeRequested(member, op, target)`, `ChangeReplied(member, op, target, status)`.
