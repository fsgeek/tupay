# X3 measure 4: residue

Procedure: X3 prereg measure 4 (X2's fixed procedure, X3 terms), mechanised in `scripts/steward/x3-residue/residue.py` (committed with its mutation pair `test.sh` before any run, `12d6ba6`). Each side's diff runs from its inputs commit (the root of `author/main` in the exported repository) to its final head. Raw outputs: `adapt-impl.txt`, `regen-impl.txt`, `adapt-model.txt`, `regen-model.txt`. derives: X3 prereg measure 4.

**Tool defect, found on the first run and fixed before any disposition:** the parser read only the line on which `derives:` appears, but a tag may wrap. Arm R's model file `model-regen/mutations/make.py` ends its tag's first line in `F3.2,` and carries `F3.3` on the next line, so the first run listed it as a false candidate. Fixed so that a tag line ending in a comma continues on the next line, and the mutation pair gained two cases (wrapped: 0; the same text without the comma: flagged). The fix removes a false candidate only. The first run's output was not kept; it differed only by that line.

| | A impl | R impl | A model | R model |
|---|---|---|---|---|
| (i) term without its tag | **2** | 0 | 0 | 0 (1 candidate excluded, below) |
| (ii) list tag not matching what the element runs | 0 (2 read) | 0 | 0 (6 read) | 0 (1 read) |
| (iii) retired id in a tag | 0 | 0 | 0 | 0 |
| **residue** | **2** | **0** | **0** | **0** |

## Dispositions
- **A impl, `impl/links_v2_test.go` and `impl/schedule_v2_test.go` (residue, 2).** Both files are in arm A's diff: its edits gave every fixture `Ref` the incarnation field (`Ref{"n1", 1, 0}`) and the nodes `members: initialMembers(...)`. Both mention `incarnation` in code (`t.Fatal("reply crossed incarnation")`, `t.Fatal("old incarnation counted")`). Neither carries F3.3 or any C3.x tag. The word predates X3 in each file (one mention each at the inputs commit), but the rule counts any file in the diff, and X3's change to the identity schema went into these fixtures untagged, which is the kind of residue the measure exists to find.
- **R model, `model-regen/tlc.sh` (excluded).** The only match is TLC's command-line flag `-config "$cfg"`, which names the TLC configuration file. Excluded under "TLC `.cfg` files" as the same object: a reading, stated here. If the exclusion is not accepted, arm R's model has residue 1.
- **(ii), read against the registered sets.** A impl `engine.go`: two tags naming P13 to P16 among clauses. These are derivations, not a list of what the element runs, so not the X1 kind. A model `mutate.py` and `run.py`: six tags. `replace_def`'s "P1, P4, P7, P13" was checked by computation: exactly the four pairs whose mutation uses a `def` edit. The other five name the 54 mutation pairs or the 59 shared schedules (P1 to P33, P40 to P54, P58 to P63, false-suspicion-v1, H7 to H10), the registered sets; read, not executed. The stale header that X1 and X2 each scored as residue ("checking runs for P1-P12 and M1") is gone. R model `report.py`: "P1..P63 by number" describes a sort order, not a list run.

## Not done
The registered "read of the diff for anything the procedure missed" was limited to the candidates and list tags above. The diffs hold 6,064 (A impl), 13,581 (R impl), 197 (A model) and 1,120 (R model) files, most of them run evidence. A full read was not made, and this is stated as a residue of the measure.
