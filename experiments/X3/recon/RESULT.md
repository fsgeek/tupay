# X3 measure 10: out-of-model reconstruction

Choosers: one fresh Grok instance per arm, sandboxed (`scripts/steward/x3-recon/`). Hooks added by a Claude helper working for the steward, which saw each record; the steward did not (departure, log 2026-11-01). Naming committed in `NAMING.md` (`124a165`) before the steward read either record. Records, hooks and the helper's readings are in `tupay-private/X3/recon/`, with hashes in `<arm>-impl/private.sha256`; the `CHOICE.md` hashes match those committed before the hooks were added (`<arm>-impl/choice.sha256`). derives: X3 prereg measure 10, X3-7.

| | arm A | arm R |
|---|---|---|
| chosen schedule | P4 | P1 |
| hook class | storage restart from an older state (ledger 3, value v1, after the token-4 accept) | lost durable record at a lease node (the grantor's highest-token register reset to 0 on an ordinary restart) |
| record's expected failure | C1.2, storage's `WriteAccept` of c1's stale `v3` write at token 3 | C1.1, n1's `Grant` to c2 with token 1 |
| **(i) any registered check reports** | **no** (replay parts 1 to 3, alone and with the 1,830 registered traces; provenance, both versions) | **yes**: replay part 2, `token 1 granted 2 times (C1.1)` on 30 of 30 |
| **(ii) steward names the decision and failure** | **yes**: the same decision, C1.2, and the hook class | **yes**: the same decision, C1.1, and the hook class |

**Against the registered expectations** (`experiments/X3/measure10-expectations.md`): storage restart from an older state was registered as "no check flags it, by design", and none did. On arm A, part (ii) was the only route, and it went through the one visible sign, `highest_before` dropping from 4 to 3 across storage's restart. Lost durable record at a lease node was registered as flagged by part 2 when the node's counted `Agree` carries a token not above one already agreed, and it was.

**X3-7** ("the steward finds the out-of-model failure from the trace in both arms", p 0.4): **confirmed**, with the departure stated. The namer did not write the hooks, but it is the same steward who read the registered expectations, and both choosers picked classes those expectations describe in detail.

**Observation (arm R, not a score):** the record shows the hook touched only n1's register, so n2's and n3's second agreement to token 1 is the implementation's own rule. Its acceptors agree per slot and do not check token monotonicity, and C1.1 rests on the grantor's register alone. That falls inside an exclusion of failure model v3 (partial loss of durable state), so it is not a contract violation in-model. It is the kind of single-point dependency Arariwa exists to make visible. Arm A's storage likewise trusts its recovered ledger with no cross-check.
