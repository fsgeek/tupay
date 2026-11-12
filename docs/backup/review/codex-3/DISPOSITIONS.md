# Dispositions of Codex's third review (draft 5 and binding-tupay)

Disposed by the twelfth steward on 2026-11-12. **All six findings, and the T20 residue, are accepted.** Every one of them lies in text that draft 4 added: the *changing* exemption, the *restore-failed* mark, the class rule's restart, T5a, B1.18 and T28's inventory. Draft 6 corrects each, with an execution example in §12.
1. **The *changing* exemption is removed**, which makes this correction subtractive. A path that cannot be captured untorn fails the run. The accepted cost, stated in the binding: runs fail while that file keeps changing, and each failure is reported.
2. **B1.8 is a completion obligation and B1.3 a demonstrated-success obligation.** *restore-failed* discharges B1.8 and leaves B1.3's scope.
3. **Deadlines are never suspended or restarted.** Unavailability is reported as the cause of a deadline that was overdue.
4. **T5a:** runs are serialized, a *started* entry is written at R first, and the claim is narrowed to "never reused while any surviving record or snapshot carries it".
5. **B1.18:** each copy carries a hash, and a copy that fails it is treated as lost and kept as evidence. Precedence rules settle disagreements, and both copies are kept.
6. **T28:** the inventory is (name, object id) pairs read once. Paths created after the inventory are out of scope, and B1.17 no longer claims them.
7. **T20** is generic.

**Size, stated plainly:** draft 6 is 243 lines against draft 5's 220. Ten of the new lines are the examples. Only fix 1 removed text.

**Frozen:** no fourth review round. Further defects are expected from the model author's TLA+ (T5a and the serialization of runs are exactly the kind of thing TLC finds), and they will be reported as divergence.
