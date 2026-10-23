# Adversarial review of `experiments/X3-prereg.md` (draft 4)

I read the draft, the five inputs (contract v3, failure model v3, pairs v4, the two v5 addenda), the 24 new schedules, the four briefs, X2's prereg and result, and `docs/steward-practice.md`. I also checked the repository state the draft relies on: `scripts/steward/author-sandbox.sh`, `setup-checkouts.sh`, `inputcheck.sh`, `sandbox-check.sh`, `observe/decision_replay.py` and its tests, and `main`'s current `impl/` and `model/` results. I did not read `docs/seed-log.md`, `docs/handoff/` or `docs/steward/`, and I did not consult project memory, so this is independent of the steward's reasoning. Nothing was modified.

Findings are ranked by how much they could change the result. The ones I think should block registration are listed at the end.

---

## 1. Departure 1 asserts an isolation the repository cannot provide for two of the four authors

**Where.** `/home/tony/projects/tupay/experiments/X3-prereg.md` line 15: "Every author runs in `scripts/steward/author-sandbox.sh`". Both model briefs (`docs/briefs/x3-adapt-model.md`, `x3-regen-model.md`), "Where you run": "Your session runs in a sandbox that shows you only your checkout and the toolchains. There is no network except your harness's own service."

**Why it matters.** `scripts/steward/author-sandbox.sh` has exactly two harness cases, `codex` and `grok`; anything else exits 2 (`*) echo "harness: codex|grok" >&2; exit 2`). Both model authors are Claude Opus 5.5. `inputcheck.sh` runs `sandbox-check.sh` only when `HARNESS=<codex|grok>` is set, so a model checkout passes the input check without any sandbox check at all. `egress-*.allow` files exist for codex and grok only.

**How it goes wrong.** If the Claude model authors run the way X1 and X2 ran them (a Claude Code session or subagent on the host with Tony's HOME), they load the MCP servers in this very environment: khipumaq (655 tupay episodes, including every prior steward's and author's words), qhaway memory, and the harness's server-side `WebFetch`/`WebSearch`, which do not pass through the egress proxy and can reach the public repository. The steward is also Opus, so the model authors are the sides with the largest shared-prior risk. The result would be: implementation sides prevented from leaking, model sides merely instructed not to, which is the X2 condition the departure says it replaces, and it is asymmetric across sides within each arm. The briefs would also be telling the model authors something false about their own environment.

**Repair.** Either (a) add a `claude` case to `author-sandbox.sh` (Claude Code under the per-author HOME, `--strict-mcp-config` with no MCP servers, a settings file denying `WebFetch`, `WebSearch` and `Agent`, an `egress-claude.allow` for the API and OTS hosts), extend `sandbox-check.sh` to verify it (including a probe that `WebFetch` of the public repository fails), and run the mutation pair for that harness too; or (b) say in the prereg exactly how the model authors are isolated, that it is weaker than the implementation sides', and what transcript evidence will be committed. The briefs' "Where you run" paragraph must describe what is actually true.

## 2. The adapt checkouts carry the steward's own oracle for measure 8, with worked example traces; the regen checkouts do not

**Where.** `scripts/steward/setup-checkouts.sh` line 18 (adapt): `'/*'` minus `experiments/`, `docs/*`, the other side, the regen dirs and `CLAUDE.md`. Regen (line 20): an include-list with `/observe/schema.md` only. Prereg measure 8 (line 36): "The steward-built decision-replay check (`observe/`, schema v5)". Both adapt briefs: "Other directories are absent from your checkout on purpose; do not look for them."

**Why it matters.** `git ls-files` shows the adapt sparse pattern includes `observe/decision_replay.py`, `observe/decision_replay_tests/` (twenty-odd synthetic v5 traces labelled pass/fail, which is a worked specification of a valid emitter), all of `scripts/steward/` (`schedule-lint.py`, the replay scripts, `rater-packet.sh`, the egress allowlists, `sandbox-check.sh` with its list of forbidden paths), `replay/` (another experiment's contract, failure model and `spec-D.md`/`spec-F.md`), `src/`, `timestamps/`, and the public `README.md`. None of this reaches a regen author.

**How it goes wrong.** An adapt author can run the exact check that scores measure 8, and parts 1 and 2 of it, on its own traces before export, and can copy the shape of the passing test traces into its emitter. A regen author builds the emitter from prose. Measure 8 and X3-3 ("Arm A's implementation more than arm R's") then partly measure who had the grader. It also makes the adapt briefs' sentence about absent directories untrue, and whatever the adapt author reads in `replay/` is unaccounted for in measure 3.

**Repair.** Decide symmetrically. My recommendation: give all four authors `observe/decision_replay.py` and its tests (C3.5 compliance is a published requirement, and the check is the oracle; both arms should be able to self-check, and the prereg should say so). Then tighten the adapt exclusion list to `scripts/steward/`, `replay/`, `src/`, `timestamps/`, `README.md`, and extend `inputcheck.sh`'s forbidden list to match, so the briefs' statement becomes true. Register the final include and exclude lists in the prereg.

## 3. The independent evidence checks for the new clauses are not scored anywhere; 1(a) is the artifact's own verdict

**Where.** Measure 1(a) (line 29): "PASS count of 59 per side". Measure 1(d): "untraceable decisions under `observe/provenance_check.py`" (the v1 to v4 check). Measure 8: "count of `UNEXPLAINED inputs` decisions" (part 3 of `decision_replay.py` only). X3-2 (line 45): "violates C1.1, C3.7 or C3.8 on P48, P60 or P63".

**Why it matters.** `decision_replay.py` parts 1 and 2 are the only check in the round that reads a trace and verifies, independently of the artifact, that every grant was counted by an eligible majority of the committed configuration (C3.7), every commit by both majorities with `readmits` exact (C3.8), one commit per epoch (C3.1), and C1.1 without a global order. The prereg registers none of their output as a measure. An artifact whose invariant is wrong in the same way as its protocol prints PASS, and the trace that shows a grant counted by a minority counts as a PASS in 1(a). That is the arm-A failure shape from X2 (both sides agreeing and both wrong), and the steward has built the tool that would catch it and then left it out of the score.

**How it goes wrong.** X3-2 is unscorable as written: "violates" by whose detection? If by the side's own `FAIL <clause>`, an artifact that never checks C3.7 can never violate it. If by the replay check, the prereg must say so.

**Repair.** Add to 1(a): a schedule is PASS only if the side prints PASS *and* `decision_replay.py` parts 1 and 2 report nothing on its trace(s); a PASS with a part 1 or 2 report is scored as FAIL of the clause the check names and sent to the judge like any divergence. Add 1(f): count of part 1 and part 2 reports per side. State that X3-2 is scored on the union of the side's verdict and the replay check. Note the check's own stated limit (C3.1 "after a record of its predecessor" uses file order, which on an implementation side is collection order) and say how a C3.1 report that depends only on file order is treated, or fix the check to use `ConfigCommitted` causes.

## 4. "One mechanism, scored once" has no registered groups for X3

**Where.** Liveness rules (line 25): "As X2 (fairness legitimacy; Rule E3 bound; one mechanism scored once; unit of failure)". X2's prereg listed the groups explicitly: {P25, P19}, {P26, P20}, {P21, P27}.

**Why it matters.** Under that rule, schedules that stall by an already-scored mechanism are reported "unreached, not FAIL" in 1(a) and their mutations "unassessable" in 1(b). Which schedules share a mechanism therefore moves the headline count. In X3 the candidate groupings are large and overlapping: the grantor-removal schedules (P40, P46, P52, P58, P61), the amnesia schedules (P33, P42, P45, P48, P51, P54, P60, P63), the schedules that need a client to find a new configuration (P46, P49, P52, P58, P59). With no groups registered, the judge's mechanism names, read after the outcome, decide how many FAILs become "unreached". This is the X2 error 8 class (a rule shaped after seeing the numbers).

**Repair.** Register the groups now, as X2 did, with the mechanism each group is built around, and say that a stall outside any registered group is scored as FAIL on every schedule it occurs on, not grouped post hoc. Also say which schedules need a grant while a reconfiguration is in progress or after the grantor is removed, since those are where P52-style stalls will cluster.

## 5. The support audit's criteria are not registered, and its consequence for 1(a) is unstated

**Where.** Departure 3 (line 21): "every model PASS is scored only after the steward has run a probe showing the checked space contains the schedule's needed reach." X3-4 (line 47): "fails its support audit on at least one shared schedule (its bounds exclude what the schedule needs)." `docs/steward-practice.md`: "For a round with no known witness, the steward states before the runs what the check must be able to reach, and runs a probe for it."

**Why it matters.** The prereg does not state, per schedule, what the check must reach (epochs, incarnations, tokens, terms, clock range, number of restarts). The authors state their bounds in their READMEs; if the steward writes the needed reach after reading those, the audit can be fitted to either arm. The prereg also does not say what a failed audit does to 1(a): is the PASS "no support", "unreached", or FAIL? And what happens to its mutation under 1(b)? X3-4 cannot be scored until the pass/fail rule is written.

**How it goes wrong.** A model that omits clocks altogether (see finding 7) can never "reach" a clock step; whether that fails the audit on P32, P41, P44, P47, P50, P53, P59, P62 is undefined, and the answer decides eight schedules on that side.

**Repair.** Add a per-schedule table of needed reach to the prereg (or a committed file it names), written now; state that a PASS whose audit fails is counted as not-PASS in 1(a) under a named category ("no support"), its mutation as unassessable, and that the probe's definition for a side that does not model a quantity (no clock, no incarnation counter) is "vacuous by design, reported, not PASS". Register the probe method per model side.

## 6. X3-1 is operationalized as the negation of a ten-way conjunction, and "mixed" counts in its favour

**Where.** Scoring rule (line 41): "Adaptation wins means: arm A's correctness on 1(a) to 1(e) and 8 is at least arm R's on every item, and arm A's author cost is lower in both tokens and wall-clock on both sides. If arm R is more correct on any item, regeneration wins that item regardless of cost. Mixed is reported as mixed and scores X3-1 as not confirmed." X3-1 (line 44): "regeneration wins a new locus, i.e. adaptation does not win under the rule."

**Why it matters.** "Adaptation wins" needs six correctness items to tie or favour A on both sides *and* four cost numbers to favour A. Its negation is near-certain for any reason at all (one slow Codex session, a tie broken by one hold-out). X2 was decided by exactly this: cost split, so not confirmed. Writing "regeneration wins a new locus, i.e. adaptation does not win" equates the seed's substantive claim with a result that would also obtain if A were more correct on every item and 2% more expensive on one side. The rule is also asymmetric by construction: R wins an item on correctness alone; A needs correctness and cost. That is inherited from X1 and is declared, but with X3-1 phrased this way it is the asymmetry, not the arms, that sets p.

**Repair.** Keep the inherited rule for continuity, but split the prediction: X3-1a "adaptation does not win under the rule" (as now) and X3-1b "regeneration wins: R at least as correct on every scored item and strictly more correct on at least one, with cost reported beside it". Give each its own probability. Say explicitly how a case where A is strictly more correct on an item and more expensive is reported (today it is "mixed", which reads as a loss for A).

## 7. F3.2 and C3.5 bite only an artifact that consults a clock, and only the adapt artifacts do

**Where.** `contract/v3.md`, "Lifetime": "The contract does not require leases to be exclusive ... A grantor that does wait for expiry before granting consults its clock, and records the reading". `observe/schema.md` v5: grant inputs include `clock` and `last_grant_at` "if the grantor waits on its clock". `impl/README.md` line 69: the inherited implementation "waits at least the prior issued lifetime before issuing the next grant". Prereg X3-3 (line 46): "Arm A's implementation more than arm R's: p = 0.5."

**Why it matters.** A regen author reading v3 can legitimately build a grantor that never reads a clock. For that side the eight F3.2-derived schedules (P32, P41, P44, P47, P50, P53, P59, P62) are no-ops on the lease nodes, P44 ("every decision is a function of its recorded inputs, clock readings included") is vacuous, and measure 8's exposure through `clock` is zero. The adapt arm inherits expiry-waiting and must now record and replay it. Any A-versus-R gap on those schedules and on measure 8 can be a design-option gap, not an adapt-versus-regenerate gap. One can argue that regeneration's freedom to take the simpler design is part of what the experiment measures, but then the prereg must say so and must not read the gap as "adaptation carried hidden clock dependence".

**Repair.** Register a per-side design fact to be read from the README and the trace before scoring: "grant path consults a clock: yes / no". Report F3.2 schedules and measure 8 counts beside it; mark a PASS on an F3.2 pair by a clock-free side as "vacuous by design" (counted in 1(a) as PASS, since the contract permits it, but reported so). Make X3-3's second clause conditional on both implementations consulting a clock, or say it is scored unconditionally and that a clock-free R makes it near-certain.

## 8. Measure 9 (planted defect) can be won trivially by the planter and has no definition of "defect"

**Where.** Line 37: "A Grok instance, given one arm's exported artifacts on one side and nothing else, plants one defect it believes the artifact's own tests will miss ... Score: whether the arm's own test suite (as shipped) fails on the planted copy." X3-6: "caught ... on at most two of the four sides. p = 0.6."

**Why it matters.** (a) "Nothing else" means no contract: without it, a "defect" is undefined (a changed error string? a removed retry?). (b) The planter sees the suite and the code, so it can always put the break in a branch no shared schedule reaches; X3-6 is then near-certain and uninformative. (c) "The arm's own test suite" is, on both arms, the steward's 59 shared schedules plus the artifact's invariants, so the measure compares invariant coverage, not tests, and the shared schedules are identical across arms. (d) No repetition rule: a planted defect that fails 3 of 30 runs is "caught" or "flaky"? (e) No restriction to the service: a plant in the emitter or compiler is caught by the steward's checks, not the suite. (f) One instance planting four times learns across plants; order matters.

**Repair.** Give the planter the contract and failure model; require the plant to be a violation of a named clause reachable by a schedule the format can express, and require the planter to supply that schedule as its witness (hashed with the plant); the steward verifies the witness FAILs the planted copy before scoring; score whether the shipped suite at 3 seeds by 10 reps produces any FAIL (flaky counts as caught only if the FAIL is of the planted clause; say which). Restrict plants to the lease-node, client and storage code, not testbed, compiler or emitter. Use a fresh instance per plant, in a registered order, and report planter tokens under measure 3.

## 9. Measure 10 (out-of-model reconstruction) conflates the trace's adequacy with the steward's skill, and the hook menu unblinds the steward

**Where.** Line 38: "by a fault hook the steward adds to a copy ... The steward, given only the trace, names the first decision the check reports unexplained and what failed; scored against the hashed record as found / not found." X3-7: p = 0.4 for both arms.

**Why it matters.** The steward writes the hooks, so it knows the menu of possible failures before reading the trace. A "not found" can mean the trace cannot show it (a ledger rollback that storage then records as its `ledger` input is consistent with v3's rule, and `decision_replay.py` part 1 checks the decision against the recorded `ledger`, not the recorded `ledger` against history) or that the steward missed it. The two are different findings about reconstructibility, and the binary score cannot separate them. Which shared run is used, and who picks it, is not stated.

**Repair.** Let the planter choose the schedule from the 59 and the failure from a registered list of hook classes (not a single hook), hashed. Score in two parts: (i) does any registered check (replay parts 1 to 3, provenance) report anything on the trace at all; (ii) does the steward, given the trace and the check output, name the decision and the failure. Register in advance what each check is expected to flag for each hook class, so "undetectable by design" is a stated outcome rather than a surprise. If parts of the schema would need an input added (for example `ledger` verified against the trace's prior accepts), say that is a result for the schema, not the arm.

## 10. P58's schedule does not do what the pair says

**Where.** `tests/pairs-v4.md` P58: "A reconfiguration removes the grantor, **sent to the grantor itself**." `testbed/schedules/P58.yaml` line 11: `reconfigure: [n4, n5, n6], to: n1, id: r1`; its comment: "a request replacing every old member is sent to it" (it = the grantor).

**Why it matters.** P46 and P52 use `to: grantor`; P58 uses `to: n1`. On the model side TLC explores every leader, so in the branches where n1 is a follower P58 tests a non-grantor receiver passing to a member (P61's shape), not the grantor receiving its own removal. On the implementation side it depends on which node happens to lead. The pair's derivation tag and the schedule's content disagree, which is the kind of thing measure 4 counts as a residue when an author does it.

**Repair.** Change `to: n1` to `to: grantor` in P58.yaml (and re-run the schedule lint), or reword P58 in pairs-v4. Do it before hold-outs are hashed, since hold-out authors read both.

## 11. The hereditary fence paragraph is contradicted by the schema addendum on storage

**Where.** Prereg line 8: "It invalidates nothing tagged only with a storage clause, unless that element consults a clock." `observe/schema.md` v5: storage decisions are decision records and "Each carries `inputs`" (`token`, `ledger`, `stored_value`, `value`); the eight write and read events "also carry `grantor_term`". `contract/v3.md`, "Storage decides deterministically": the iff rule is new, fixed "for v3".

**Why it matters.** Every storage decision element must change (new fields, new inputs, a rule made iff). Raters applying measures 4, 6 and 7 against the fence paragraph will classify those changes as outside the invalidated set (unexpected propagation, or evidence of a stale tag) when the inputs require them. The paragraph also shapes what the adapt author is told is in scope.

**Repair.** Amend the paragraph: the change invalidates every element that emits a decision record (storage included, under C3.5 and the v5 schema), and every storage element whose acceptance rule was "only if" rather than "iff".

## 12. Measure 4's new terms will match almost everything, and the required tag is unspecified

**Where.** Line 32: "Residue by X2's fixed procedure, with the F3.x and C3.x terms (`reconfig`, `config`, `epoch`, `clock`, `amnesia`)." X2's rule (i): a file mentioning a term "in code must carry an F2.x tag".

**Why it matters.** `config` matches TLC `.cfg` handling, Go configuration structs, `ConfigCommitted`, and every compiler. `clock` matches the inherited implementation's seeded logical time, which exists for F1.3 and liveness, not F3.2. `epoch` matches Unix-time code. For each term the rule must say which tag is required (F3.1 or C3.1/C3.7/C3.8 for `config`/`epoch`? F3.2 or C3.5 for `clock`?), or a rater chooses after seeing the diff. Also, rule (iii) ("tags naming a retired id") cannot discriminate in X3: no author ever saw C3.2, C3.3, C3.6, P34 to P39 or P55 to P57.

**Repair.** Per term, name the acceptable tags and the file classes excluded (generated files, `.cfg`, the compiler's YAML key names). State that (iii) is expected to be zero on all sides and reported, not scored.

## 13. Several denominators and baselines that X2 registered are missing here

- Measure 7 (line 35): "denominators counted at registration" but no numbers; X2 gave 37 and 66 and an at-risk list. Without the count the fraction is not registered, and without an at-risk list X3-9 has no pre-stated expectation to check against.
- Measure 5 (line 33): "Of the shared P1 to P30 that the existing artifacts PASS on `main` at registration" with no number. `impl/RESULTS-timing.md` shows 30/30 at 3 by 10, and `model/README.md` reports all passing after the routing fix; write the numbers in, and say whether H7 to H10 (now shared, and the schedules `main` was repaired for) are included. As written they are not, so measure 5 cannot show a regression of the routing fix.
- 1(b): "count that fail on their pair's schedule" with no denominator (54 pairs, 54 mutations per side). Say how a flaky mutation is counted (the liveness rules say never kill; make that explicit here).
- 1(c): "Hold-outs H11 onward" with no count; the count must be fixed when the hashes are committed, and X3-5's probability depends on it.

## 14. Scoring-direction and vacuity wording

- Scoring rule: "correctness on 1(a) to 1(e) and 8 is at least arm R's" is wrong-signed for 1(d) and 8, where lower is better. Say "at least as correct" per item with the direction stated.
- Measure 8 counts "decisions"; the check reports "each group with unequal outcomes". Say whether a group of five decisions is 1 or 5.
- Measure 8 on a model side is near-certainly zero on both arms (TLC has no hidden inputs; the exporter writes from state), so it ties by construction there; fine, but say so rather than let it look like evidence.
- X3-3's second clause ("Arm A's implementation more than arm R's") when both are zero: falsified, or vacuous? Say.
- X3-2's "at first run" and 1(a)'s "all ten repetitions" versus the liveness rule's "at least ten": reconcile.

## 15. Smaller asymmetries and inconsistencies in the briefs and inputs

- `x3-regen-impl.md`: the module cache "holds what `main`'s `go.mod` lists". This tells a regen author that `main` exists and what it depends on, and constrains the regen implementation to arm A's Raft library (etcd raft) or a hand-written one, since `proxy.golang.org` is denied. Symmetric as a constraint, asymmetric as information; the adapt brief does not carry the sentence. Say it in the prereg as a deliberate confound-reducer or remove the parenthesis.
- `x3-regen-impl.md` and `x3-regen-model.md` say "up to six" lease nodes; the adapt briefs do not. The adapt model README records "The topology is fixed at 3/2/1". Harmless since the schedules show six, but the adapt author is given one fewer explicit warning.
- `tests/pairs-v4.md` line 5: "Hold-out authors are told nothing of this cut" is written in the file the hold-out author reads. Reword to "are told nothing beyond this file".
- Grok now reviews the inputs, writes the hold-outs, plants measure 9 and plants measure 10. X2 said its multi-role arrangement once, on the record; do the same here, and say whether one instance or several.
- Prereg line 3 says "DRAFT 4" while line 29 says "draft 4 of this file corrected 57"; housekeeping, but a registered file should not refer to itself in the past tense.
- Both arms run concurrently on a shared machine with TLC memory caps named only by the authors ("memory you can name"). Wall-clock cost (measure 3) and any model-side "unreached for memory" are confounded by contention. Register a per-author cap and the launch order, or run the two model authors in sequence.

---

## What I think should block registration

1. **Finding 1** (model authors cannot run in the sandbox as the prereg and briefs state). Registering a claim about isolation that the scripts cannot execute, with the briefs repeating it, would be a false record from the first commit.
2. **Finding 2** (the replay check, its example traces and the steward's scripts are in adapt checkouts only). This is a one-line fix in `setup-checkouts.sh` plus a sentence in the prereg, and it directly touches a scored measure.
3. **Finding 3** (replay parts 1 and 2 unscored; X3-2 undefined). The only independent oracle for the new clauses must be in the score, or the round repeats X2's arm-A shape by design.
4. **Findings 4 and 5** (mechanism groups and support-audit criteria not registered). Both are scoring rules that would otherwise be written after the outcome, which `docs/steward-practice.md` names as the X2 error 8 class.

Findings 6 to 11 I would fix before registration because they are cheap and each changes how an outcome is read, but a registration that stated them as known limitations would not be dishonest. Findings 12 to 15 are housekeeping and can be amendments if the hold-outs are already being written.
