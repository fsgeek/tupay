# X3 measure 8: the design fact (does the grant path consult a clock), registered before scoring

Written by the ninth steward, 2026-10-27, before any X3 score is computed, as `experiments/X3-prereg.md` measure 8 requires: "registered from the README and the traces before scoring". Sources: each side's README in the steward's scoring clones (`~/projects/tupay-x3-score/`, at the commits in `runs/<side>/commit.txt`), and the decision inputs recorded on every `Grant` in each side's unmutated steward-run traces (`runs/<side>/observe.tar.xz`).

| Side | Grant path consults a clock | README | Traces: Grant decision inputs |
|---|---|---|---|
| arm A model | **no** | `model/README.md` L29 ("The grantor does not wait for expiry, so no decision reads a clock"), L56 | 128 grants in 63 traces; inputs `agreed`, `members`, `config_epoch`, `grantor_term`, `last_token`; none records `clock` |
| arm R model | **no** | `model-regen/README.md` L110 ("No clocks. No protocol decision reads a clock"), L132 | 126 grants in 62 traces; same five names; none records `clock` |
| arm A impl | **yes** | `impl/README.md` L1269 (a grantor that has issued before waits using its own local clock, records `clock` and `last_grant_at`), L1188 | every grant (7,140) records `clock` and `last_grant_at` beside the five |
| arm R impl | **no** | `impl-regen/README.md` L21 ("Grant does not wait for lease expiry or read any clock") | 3,840 grants; the five names only |

Trace counts include every unmutated `.jsonl` in each archive (the implementation archives' file count differs from `traces.txt` where the archive also holds mutation traces under other names; the names found are the same in every grant either way).

**Consequences, as the registration states them (applied at scoring, not here):**
- Three sides (both models, arm R's implementation) pass the F3.2 schedules and P44 **vacuously by design** as to clocks: counted as PASS, reported as such.
- **X3-3's second part** ("arm A's implementation more than arm R's", p 0.5) is scored only if both implementations consult a clock; arm R's does not, so it is **unscorable**, reported as such. X3-3's first part is unaffected.
