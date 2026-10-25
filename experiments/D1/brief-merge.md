# Brief: merge four lists of environment contracts (D1 phase 1)

Below are four lists, written independently from one source (Ongaro, *Consensus: Bridging Theory and Practice*, 2014), of the **environment contracts** Raft relies on: obligations on things outside the algorithm (storage, network, clocks, processes, identity, operators, the state machine, the host). Each entry has an id `<list>:E<n>`. Different lists often state the same obligation in different words, or split one obligation into several finer ones.

Your task: group entries that state **the same obligation on the same depended-on service**. Two entries belong in one group only if a deployment that violates one necessarily violates the other. An entry that is broader than another may appear in more than one group (once with each finer entry it covers). An entry that matches nothing need not be listed.

Use only the text below. Do not use any tool. Reply with JSON only, in exactly this shape, and nothing else:

{"groups": [["codex-1:E3", "grok-2:E7"], ["codex-2:E1", "grok-1:E4", "grok-2:E2"]]}

Every id you write must appear in the lists below. Groups have at least two ids.

---
