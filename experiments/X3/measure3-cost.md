# X3 measure 3: cost

Computed 2026-11-01 by the tenth steward from the log's harness figures (entries "X3 arm R implementation author ended", "X3 arm A implementation author ended", "X3 arm A model author ended", "X3 arm R model author ended") and the authors' commit times in the exported repositories (`~/projects/tupay-x3-export-<arm>-<side>`, ref `author/main`). derives: X3 prereg measure 3, X3-8, scoring rule.

## Per author
| | A impl (Codex) | R impl (Codex) | A model (Opus 5.5) | R model (Opus 5.5) |
|---|---|---|---|---|
| start → end (clock) | 20:30:00Z → 20:55:02Z | 20:30:00Z → 20:44:26Z | 20:30:19Z → 01:38:44Z | 01:39:42Z → 07:05:32Z |
| wall-clock | **25 min 02 s** | **14 min 26 s** | **5 h 08 min 25 s** (harness 18,491 s) | **5 h 25 min 50 s** (harness 19,501 s) |
| input tokens (all, cached included) | 7,288,362 (7,172,992 cached) | 3,290,756 (3,225,344 cached) | 120,114,643 (466 uncached + 675,227 cache-write + 119,438,950 cache-read) | 88,925,259 (370 + 660,559 + 88,264,330) |
| output tokens | 53,753 (18,909 reasoning) | 37,418 (11,558 reasoning) | 442,458 (246,705 thinking) | 492,158 |
| **total tokens** (input + output) | **7,342,115** | **3,328,174** | **120,557,101** | **89,417,417** |
| harness cost figure | n/a | n/a | US$38.14 equivalent | US$32.78 equivalent |

## Arm A split at its first commit after predictions (wall-clock; tokens are not split by either harness)
| | start → predictions | predictions commit | first commit after | before | after |
|---|---|---|---|---|---|
| A impl | 20:30:00Z | `fe12a32` 20:31:14Z | `fc6718e` 20:49:10Z | 19 min 10 s | 5 min 52 s |
| A model | 20:30:19Z | `aaf2c10` 20:52:26Z | `2bcce7b` 21:52:36Z | 1 h 22 min 17 s | 3 h 46 min 08 s |

"Before" runs from launch to the first commit after the predictions commit.

## X3-8 outcome under the registered word "total tokens" (scored in the result)
- Implementation: A 7,342,115 vs R 3,328,174. **A not lower: not confirmed** (p 0.5).
- Model: A 120,557,101 vs R 89,417,417. **A not lower: not confirmed** (p 0.4).
- **Beside, not instead:** on **output tokens alone**, the model side reverses (A 442,458 < R 492,158); the implementation side does not (A 53,753 > R 37,418). The registration says "total"; the cached input dominates both totals (over 98% of input on every side), so the scored comparison is mostly a comparison of context re-reads.

## Cost half of the scoring rule
"Adaptation wins" needs arm A's author cost lower **in both tokens and wall-clock on both sides**. Arm A's implementation took longer (25 min vs 14 min) and more tokens on both sides. **The cost condition fails on three of four counts**, so adaptation cannot win under the rule whatever the correctness items show; correctness still decides X3-1b and is scored item by item.

## Other cost items (registered)
- **Steward time**: not measured as such by any steward; the log's entry times bound it. Reported as not measured.
- **Advisor tokens** (from the log): DeepSeek audit review 83k prompt tokens, US$0.04; Kimi judge US$0.85 for six items; Gemini judge via `agy` (no token figure from the harness); hold-out author (Grok), four input reviews (Grok) and the Fable prereg review: figures, where the log has them, to be gathered into the result.
- **Decisions asked of Tony during X3**: to be counted from the log and khipumaq for the result.
