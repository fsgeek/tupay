# X3 measure 9: planted defects

One fresh Grok instance per plant, sandboxed, given one side's exported tree with no git history and `BRIEF.md` (`scripts/steward/x3-plants/`). Scoring by `score.sh`: the witness is run on the planted copy (implementations at 3 seeds by 10 repetitions), then the arm's shipped suite (the 59 shared schedules) on the planted copy. Plants, witnesses and transcripts are in `tupay-private/X3/plants/`, with hashes in each `<arm>-<side>/private.sha256`. derives: X3 prereg measure 9, X3-6.

| plant (order) | clause | planted | planter time | witness on planted copy | suite: schedules FAILing the planted clause | caught |
|---|---|---|---|---|---|---|
| 1 A impl | C1.2 | `impl/engine.go`, 1 line (and `go.sum`, a build side effect) | 3 min | 30/30 FAIL C1.2 | 11 of 59, each 30/30 | **yes** |
| 2 R impl | C1.3 | `impl-regen/main.go`, 3 lines | 7 min | 30/30 FAIL C1.3 | 11 of 59, each 30/30 | **yes** |
| 3 A model | C1.1 | `model/Lease.tla` | 5 min | FAIL `C1_1` | 52 of 59 | **yes** |
| 4 R model | C1.2 | `model-regen/Lease.tla` | 6 min | FAIL C1.2 | 31 of 59 (plus P63's registered C3.4) | **yes** |

No plant was void and none was flaky. **X3-6** ("caught by the arm's own suite on at most two of the four sides", p 0.6): **not confirmed**; all four were caught. A reading beside the score: each planter chose a defect in the core safety clauses (C1.1 to C1.3), which every arm's suite covers heavily. The brief let the planter choose and did not ask for a hard-to-catch defect, so this measures whether the suites catch the defects a fresh instance plants unprompted, not whether they catch subtle ones. The two implementation plants were caught on the same 11 schedules, the ones that write across a change of holder.

Process notes: the scoring script was corrected three times as plants arrived, each before that plant's scoring ran (fetch into a non-current branch; trace files and bytecode caches are not planted files). Plant 4 was launched untracked and watched a minute later (lapse, logged).
