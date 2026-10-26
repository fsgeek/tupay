# CELLS.md: environment contracts of the log and recovery, in a fixed order

Enumerated from the paper and the source by other readers; a cell with several statements is one contract stated by several readers. Take them in this order.

### D1
- contract: codex-1 one
- source: §1 "q"
- violation: v
- at-risk: G1
- detectable: no — r
- silent: 5 — r

- contract: grok-1 one
- source: §1 "q"
- violation: v
- at-risk: G1
- detectable: yes — r
- silent: 4 — r

### D4
- contract: codex-2 two
- source: x.c:1 "q"
- violation: v
- at-risk: G1
- detectable: no — r
- silent: 3 — r

### D6
- contract: grok-2 one
- source: §1 "q"
- violation: v
- at-risk: G1
- detectable: no — r
- silent: 2 — r

### D3
- contract: codex-2 one
- source: §1 "q"
- violation: v
- at-risk: G1
- detectable: partly — r
- silent: 3 — r

### D5
- contract: grok-1 two
- source: x.c:1 "q"
- violation: v
- at-risk: G1
- detectable: no — r
- silent: 2 — r

### D2
- contract: codex-1 two
- source: x.c:1 "q"
- violation: v
- at-risk: G1
- detectable: yes — r
- silent: 1 — r

### D7
- contract: grok-2 two
- source: x.c:1 "q"
- violation: v
- at-risk: G1
- detectable: no — r
- silent: 2 — r

