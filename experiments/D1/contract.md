# D1 contract: what the text promises (v1)

Written 2026-10-25 before any enumeration, by rule: every property the text states as a guarantee of Raft, quoted, and nothing else. Ids `R1.n`, never reused. derives: design.md draft 3, phase 2 "Inputs"; Fable review finding 17.

**From Figure 3.2 (§3, verbatim):**
- **R1.1 Election Safety.** "At most one leader can be elected in a given term." (§3.4)
- **R1.2 Leader Append-Only.** "A leader never overwrites or deletes entries in its log; it only appends new entries." (§3.5)
- **R1.3 Log Matching.** "If two logs contain an entry with the same index and term, then the logs are identical in all entries up through the given index." (§3.5)
- **R1.4 Leader Completeness.** "If a log entry is committed in a given term, then that entry will be present in the logs of the leaders for all higher-numbered terms." (§3.6)
- **R1.5 State Machine Safety.** "If a server has applied a log entry at a given index to its state machine, no other server will ever apply a different log entry for the same index." (§3.6.3)

**From §2.1, the properties the text says consensus algorithms for practical systems have, and which it sets Raft to meet:**
- **R1.6 Safety under non-Byzantine conditions.** "They ensure safety (never returning an incorrect result) under all non-Byzantine conditions, including network delays, partitions, and packet loss, duplication, and reordering."
- **R1.7 Availability.** "They are fully functional (available) as long as any majority of the servers are operational and can communicate with each other and with clients."
- **R1.8 Timing-independence of safety.** "They do not depend on timing to ensure the consistency of the logs: faulty clocks and extreme message delays can, at worst, cause availability problems."

**From §6.3:**
- **R1.9 Linearizable client semantics.** "Our goal in Raft is to implement linearizable semantics … each operation appears to execute instantaneously, exactly once, at some point between its invocation and its response."

Where the text qualifies a promise (a mechanism it marks as depending on an assumption), the qualification is the text's and goes with the clause when a cell is mapped to it; this file adds none.
