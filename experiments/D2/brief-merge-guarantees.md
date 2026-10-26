# Brief: merge two lists of guarantees (D2 phase 0a)

Below are two lists, written independently from two sources (the paper *The Episode File System*, USENIX Winter 1992, and Episode's source in OSF DCE 1.2.2), of the **guarantees** Episode's log and recovery (`logbuf`) make to the rest of the file system, its users or operators. Each entry has an id `<list>:G<n>`. Different lists often state the same guarantee in different words, or split one guarantee into several finer ones.

Your task: group entries that state **the same guarantee**. Two entries belong in one group only if a run that violates one necessarily violates the other. An entry that is broader than another may appear in more than one group (once with each finer entry it covers). An entry that matches nothing need not be listed.

Use only the text below. Do not use any tool. Reply with JSON only, in exactly this shape, and nothing else:

{"groups": [["codex:G3", "grok:G7"], ["codex:G1", "grok:G4", "grok:G2"]]}

Every id you write must appear in the lists below. Groups have at least two ids.

---
