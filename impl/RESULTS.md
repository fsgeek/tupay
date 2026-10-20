<!-- derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3 -->
# Verified first-version results

Implementation revision: `e9664daa2ec93e611a7ac2dd2e05d927b4148d36`; stamp commit: `eba15aece154316f75487c24c079ab83d595b2a0`.
Preregistration: `37283d5ecaef9e5e3e6641faaa8bc71e85b2aace`. Original bytes remain unchanged as a prefix;
the bootstrap investigation is an additive, explicitly outcome-informed amendment.

The final standalone false-suspicion run passed seeds 1, 2 and 3. The repeated
false-suspicion observations inside --all also passed all three seeds.
Every decision resolves to its Grant and grantor term; each observed run has
both old and new grantor incarnations. This observation is not paired
correctness evidence. See [decision provenance](evidence/false-suspicion-provenance.tsv).

| Pair | Baseline seed 1 | Seed 2 | Seed 3 | Mutation seed 1 | Seed 2 | Seed 3 |
|---|---|---|---|---|---|---|
| P1 | PASS | PASS | PASS | FAIL C1.1 | FAIL C1.1 | FAIL C1.1 |
| P2 | PASS | PASS | PASS | FAIL C1.1 | FAIL C1.1 | FAIL C1.1 |
| P3 | PASS | PASS | PASS | FAIL C1.1 | FAIL C1.1 | FAIL C1.1 |
| P4 | PASS | PASS | PASS | FAIL C1.2 | FAIL C1.2 | FAIL C1.2 |
| P5 | PASS | PASS | PASS | FAIL C1.2 | FAIL C1.2 | FAIL C1.2 |
| P6 | PASS | PASS | PASS | FAIL C1.2 | FAIL C1.2 | FAIL C1.2 |
| P7 | PASS | PASS | PASS | FAIL C1.3 | FAIL C1.3 | FAIL C1.3 |
| P8 | PASS | PASS | PASS | FAIL C1.3 | FAIL C1.3 | FAIL C1.3 |
| P9 | PASS | PASS | PASS | FAIL C1.3 | FAIL C1.3 | FAIL C1.3 |
| P10 | PASS | PASS | PASS | FAIL C1.4 | FAIL C1.4 | FAIL C1.4 |
| P11 | PASS | PASS | PASS | FAIL C1.4 | FAIL C1.4 | FAIL C1.4 |
| P12 | PASS | PASS | PASS | FAIL C1.4 | FAIL C1.4 | FAIL C1.4 |

Final totals: 36/36 pair baselines PASS; 36/36 mutation runs FAIL the
predeclared clause; 12/12 mutations killed on each of three seeds. All three
final runner commands exited 0. No UNEXPLAINED result in the final matrix.

The initial matrix had P10 FAIL C1.4 on seeds 1, 2 and 3 (33/36 baselines
passed). A preregistered regression then exposed empty voter configurations
on n2/n3 before the initial n1 crash. The regression failed before the setup
barrier and passed afterwards; focused P10 then passed seeds 1–3. Schedules,
mutation paths, liveness thresholds and original scoring were not changed.
Initial mutation results alone did not discriminate P10 from this baseline
defect; the final passing baseline plus final failing mutation do.

Additional verification:

- `/usr/local/go/bin/go build -C impl -mod=readonly -o bin/tupay .`: exit 0.
- `/usr/local/go/bin/go test -C impl -mod=readonly -count=1 ./...`: exit 0.
- `/usr/local/go/bin/go vet -C impl -mod=readonly ./...`: exit 0.
- Original preregistration byte-prefix comparison: preserved.
- Independent false-suspicion decision-to-grant traversal: all three seeds complete.

Go checks set GOMODCACHE, GOPATH, GOCACHE and TMPDIR beneath impl/.cache.
Temporary/cache files are excluded from commits.

All referenced raw JSONL and horizon sidecars are retained under observe/.
The [manifest](evidence/manifest.tsv) binds each to its schedule derivations
and SHA-256 digest. [Raw command receipts](evidence/logs/) preserve both
initial and final outcomes. No model artifact or git log was read.

Blocked: none. Bounded sampling and the trusted finite liveness-horizon
certificate remain limitations documented in README.
