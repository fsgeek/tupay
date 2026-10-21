# Adversarial review of `experiments/X2-result.md` (uncommitted, 2026-10-20 23:49 PDT)

Reviewer: Claude Fable 5.1, advisor, different family from the steward. Read: the result, `X2-prereg.md` at `954266b`, every log under `experiments/X2/armA/` and `armR/`, the four judge streams and three packets' headers, all rating files, the seed-log from "X2 registered" to the end, `model/README.md`, `impl/README.md`, and arm R's READMEs via `git show x2-r:`. Nothing modified.

## Bottom line

The numbers are right. Every count in the Measures table that has a log behind it matches the log; the measure 6 and 7 fractions and all four kappas recompute to the values stated; the judge verdicts are quoted faithfully; the prediction verdicts X2-2, X2-3, X2-4, X2-5, X2-7, X2-8, X2-10, X2-11 follow from the registered wording. X2-1 "not confirmed" is correct under either reading of the one disputed item below.

Three things need fixing before publication, in this order: (1) the 1(b) "first version" rule is not in the registration, is the only item on which A beats R, and is what makes the headline "mixed"; (2) the falsifier section calls a declared, written-down limitation a "blind spot" and asserts a cause from one arm; (3) the scoring paragraph presents R's 1(c) and 1(e) wins without saying that one came from a steward-renamed file and the other from two hold-outs the R model could not run. The rest is wording, small arithmetic, and a few omissions from the errors list.

---

## Findings, ranked

### 1. HIGH. The 1(b) "as registered at first version" rule is the steward's, not the registration's, and it is load-bearing for "mixed"

`X2-result.md:9` scores R model 1(b) as **28/30** "as registered at first version". `X2-result.md:34` then says "R's is lower on 1(b) (model side, 28 vs 30) ... the result is mixed".

- The prereg's measure text (`X2-prereg.md:36`) is "at the first steward run after the arm's merge, before any fix", and 1(b) (`:37`) is "count of 30 that fail on their pair's shared schedule". The merge `272731f` contains `1e8ed4b` (the replaced mutations), and the steward's first run of the merged artifact gives 30/30 (`armR/model-mut.log`). No sentence in `X2-prereg.md` says mutations are scored at the author's first version. The phrase first appears in the log (`docs/seed-log.md:185`: "Under the registration, measure 1(b) is scored on the mutations as registered at first version") on the day, after the R model author had reported 28/30. The briefs (`docs/briefs/x2-regen-model.md:28,31`) define "first version" and require predicting every mutation, but they do not say a replaced mutation is scored at the original. The prereg's "Fixing anything before it is scored" (`:80`) is the strongest support for the steward's reading, and it should be cited if the reading is kept.
- Why it matters: 1(b) is the **only** correctness item on which A beats R. Without it, R >= A on 1(a), 1(b), 1(c), 1(d), 1(e) and strictly greater on 1(c) (impl) and 1(e) (model). The honest alternative headline is "regeneration at least as correct on every item, more correct on two", not "mixed". X2-1 is not confirmed under either reading, so no prediction verdict changes; the narrative does.
- Asymmetry: the R impl author also iterated after its first build (`709021f` "tighten event bound and request wait accounting", 06:04Z, between `bac426c` and `fe3c213`) and was not asked which of those changes were outcome-informed; it declared no "first version" until done. The R model author declared one, said its replacement was outcome-informed, kept the originals runnable, and is the only side penalised. The rule as applied rewards non-declaration. The result should say so.
- Version mixing: correctness is scored at the R model's first version (`e226459`, 06:20:56Z) but cost at its final version (33 min, 221k; `X2-result.md:15-16`). At first version the wall-clock is about 30 min. No verdict changes (A model 27 min is lower either way), but one version should be used for both, or the mixing stated.
- `P25.v1 UNEXPLAINED bound`: the registered bound rule (`X2-prereg.md:32`) says an `UNEXPLAINED bound` "goes to the judge with the trace". It was not sent (`judge/prompt-R.txt` is H9 only; P25.v1 appears there only inside the R README). Counting it as not killed is defensible, but the rule says judge, and the author's own account (endless re-election, `x2-r:model-regen/README.md:208-209`) describes a liveness failure the term bound masks, i.e. plausibly a kill the bound hid. Either send it or say why the rule does not apply to mutations. P8.v1 PASS is unambiguous, so R model 1(b) is below 30 under any treatment; the 28 versus 29 is the only thing at stake.

Recommended text: report both numbers (28/30 at the author's declared first version; 30/30 at the first steward run of the merged artifact), name which reading the steward chose and on what clause, state that X2-1 is unaffected, and state what the headline is under the other reading.

### 2. HIGH. "The thesis's falsifier" (`X2-result.md:50-52`) claims a shared blind spot where the record shows a declared limitation, and asserts a cause from one arm

The registered falsifier (`docs/seed-log.md:82`): "a round in which both sides agree on every pair and a held-out fault later shows they were wrong in the same way (the shared-misinterpretation risk the seed names)". Arm A matches the shape: both sides 31/31, 30/30, identical hold-out verdicts, judge says one mechanism on both (`judge-A-H8`, `judge-A-H9`, locus "both"). That much is supported.

What overclaims:

- "Cross-family authorship did not prevent a shared blind spot; it reproduced one" (`:51`). The arm A model author wrote, before any hold-out existed, `model/README.md:176-178` (X2.5): "The model would print `FAIL C1_4` on a schedule in which the requester is cut only from a grantor that keeps a majority, because nothing makes that grantor step down. No shared schedule is like that, so this is a limit of the model, not an observed result." That is not a blind spot; it is a seen, named, accepted gap, with the exact failing shape written down. The result says this at `:31` and then forgets it at `:51`. The implementation side (`impl/README.md:730-760`, items 68, 70, 71, per the judge) is the undeclared one. The accurate statement is: one author saw it and declared it, the other did not, and nothing in the workflow consumed the declaration. That is a sharper finding than "shared blind spot" and it points at a different fix (declared limitations feed hold-out and schedule design) than the one implied.
- "because the blind spot was in the default design of leader-based services ... not in either family" (`:51`). Causal, from one arm. The weak supporting evidence (same family, Opus, built a relaying model in arm R; same family, Codex, built a non-relaying impl in arm R) is not cited. State it as an inference and give the evidence, or drop "because".
- Common cause not named here: both arm A authors were given the same steward-written P19 to P30, none of which exercises a grantor that keeps its quorum but is cut from the requester (the Conclusion, `:71`, admits the steward "did not name" this stall), and both inherit three rounds of reconciled history against shared interfaces. The two sides of arm A are not a clean instance of "independently derived"; the fully independent arm (R) did diverge on H9. The section mentions R's divergence but still says "contradicted in its strong form". Say instead: the registered shape occurred; here are the three facts that bear on how much it contradicts (X2.5 declared; shared steward inputs as common cause; the independent arm diverged); n = 1.
- "Both sides ... were both wrong on H8 and H9 by the same mechanism" (`:51`): supported by the judge, but note for H8 the judge's `what_would_settle_it` leaves a door open (whether an unreached fault step and a Grant-not-recorded-when-reply-link-down reading change the premise), and the result's own residue at `:64` says that reading is underdetermined. "Wrong" on H8 is the judge's call under L3 as written; say that.

### 3. MEDIUM. The scoring paragraph (`:34`) presents R's two correctness wins without their caveats; 1(c) and 1(e) are the same events

- **1(c) impl, 2 vs 3.** R impl's 3/4 was obtained from files that do **not** match the registered `SHA256SUMS`: each hold-out was presented as `P1.yaml` with its `schedule:` line changed (`armR/impl-holdout-renamed.log`; `docs/seed-log.md:188`). The intervention is logged and disclosed in the judge packet, and the residue at `:66` names the allowlist, but the table at `:10` and the scoring sentence at `:34` do not say that the one 1(c) number that decides "R wins 1(c)" came from a steward-modified input. Prereg 1(c) says "hashes in `SHA256SUMS`". Add a footnote on the cell.
- **1(e) model, 1 vs 0.** R model's 0 stall mechanisms rests on H7 and H8 being unrunnable (`armR/model-holdout.log`: "only end: quiescent is supported"; H7 and H8 do end on an event, `holdout/H7.yaml:30`, `H8.yaml:25`). Zero mechanisms found on two of four hold-outs is not the same as zero mechanisms present. Under the letter of 1(e) the count is 0; the sentence "A's correctness is lower than R's on 1(e)" should say the count is over the two hold-outs R could run.
- **Not independent.** A's 1(c) losses and A's 1(e) count are the same two failures (H8, H9). "Regeneration wins 1(c) and 1(e)" reads as two findings; it is one mechanism scored under two measures, which the prereg's "one mechanism, scored once" (`:31`) spirit would have you say.
- Model-side 1(c) tie (2/4 vs 2/4) conflates A's two genuine FAILs with R's two cannot-runs. Worth one clause.

### 4. MEDIUM. The registered fairness rule is not visibly applied

`X2-prereg.md:29`: a model-side C1.4 PASS that rests on fairness other than own-state or up-link delivery "is scored as not PASS and reported as a divergence with locus model". The result never says this check was performed. It matters most for R model H9 PASS, which is the one PASS that produces the arm R divergence and the "regenerated model relays" narrative. From `x2-r:model-regen/README.md:121-122` the fairness table looks legitimate (WF(StepDown) own-state; WF(Grant) over up links, relay over up links) and in H9 the relay path c2-n2-n1 is all-up, so I expect it passes the rule. Say that it was checked and passed, per side, in one line.

### 5. MEDIUM. X2-9 (`:45`): the A half was known true at registration, and the stated survival reason is wrong

- The residue, `model/run.py:2` ("checking runs for P1-P12 and M1"), has been unchanged since `ff6b77d` (model v1); it was the X1 residue (`docs/seed-log.md:103`, "Not fixed; scored") and was still present at `51e4569`. So at registration the A half of X2-9 was already true unless the newcomer fixed it. The result discloses inheritance; it does not disclose that the steward knew. p = 0.5 therefore priced only the R half. Say so, for calibration's sake.
- "It survived ... because no change needed to touch it" (`:45`) is contradicted by the diff: the newcomer edited `model/run.py` (`1f49853`; `git diff 51e4569 b632199 -- model/run.py`), updating the `ORDER` tag at line 26 to name F2.1/F2.2 and P19-P30, twenty-four lines below the stale header, and left the header. That is a stronger fence failure (the author was in the file, rewriting a sibling tag) and the result should say that instead.
- Measure 4 on the other three sides: my grep of code files on `x2-r` and `b632199` for `cut|drop|link` without an `F2.` tag finds none (the one hit, `impl/check_reads.go:31` "linkage", is a false positive and the file is not in the diff), and no other code tag names a pair range. 1 / 0 / 0 / 0 is consistent with what I can reproduce.

### 6. MEDIUM. Measure 7 disagreement left unresolved against the prereg; the steward rated with the author's labels in view

- `X2-prereg.md:43`: disagreements "are reported, and resolved in favour of the diff". The result reports model 5 and 12 (`:20-22`) and does not resolve them. Fable's rating gives a concrete v1-reachable state for entry 5 (`ratings/m7-x2/fable-ratings.txt`, "model 5": crash + bipartition + heal, `Elect(n2)` now disabled by voter stickiness until `StepDown(n3)`); the steward's "identical on every v1 (symmetric) run" is an assertion against it. Either rule on it from the diff or say the measure's value is 1 to 3 pending. No prediction verdict moves (X2-5 is falsified by the impl side; X2-6 needs only >= 1).
- `ratings/m7-x2/steward-ratings.txt:1` says the steward rated "from the diff ... and both READMEs", i.e. with the adapting author's own contradicted/extended labels visible, and the steward's model-side classification reproduces the author's exactly (13 contradicted; 5, 12 extended). The prereg says the author's statements are "reported beside" the classification, which implies rating without them. Not provably anchoring; disclose it.
- Small: the steward's impl tally in that file says "extended 7, unchanged 54" but lists six (8, 14, 16, 19, 38, 52). The kappa is 0.61 either way.

### 7. LOW. Numbers that do not reconcile

- `:24` "Steward wall-clock, registration to scoring: about 4 hours, including the preparation". Registration `954266b` is 2026-10-21T05:50:24Z; the result file was written 06:49:15Z. Registration to scoring is about **one hour**. The 2.5 h of preparation (`docs/seed-log.md:166`) is before registration by definition. Split the sentence. (The one-hour figure is itself worth stating: four authors, two arms, judging and rating in 59 minutes.)
- `:17` impl split "7 before / 9.5 after" sums to 16.5 against a 15.5 total. Commit times (`6c58815` 05:53:02Z, `94549e3` 05:58:10Z, `c582749` 06:07:04Z, start about 05:51Z) give about 7 / 9. The model split 14.5 / 12.5 = 27 checks.
- `docs/seed-log.md:181` says arm A steward runs started "at 06:3xZ"; `armA/model.start` and `impl.start` say 06:18:53Z and 06:18:56Z (right after the merge at 06:18:01Z). The log is wrong; the result's "first runs after each arm's merge" is right. A one-line log correction, appended.

### 8. LOW. Not verifiable from the evidence directory

- `:11` "339 traces" (R impl, 1(d)) appears nowhere else; "291" is in the log only. No provenance-check output is under `experiments/X2/`. Commit the checker's output or cite where it is.
- `:24` advisor tokens "about 417k after"; `:15` author tokens (harness-reported, in the log only). Fine as stated, but say "per the log" so a reader knows there is no artifact.
- Gemini tokens check: `judge-R` 40,868; `judge-A-H8` 66,381; `judge-A-H9` 50,120; failed `judge-A` 182,730 (usage events in the streams). All match `:24`.

### 9. LOW. Steward-errors list (`:54-60`): candidates missing

1. The regen impl brief's "these are the only schedules that count" (`docs/briefs/x2-regen-impl.md:7`) is why the R impl refuses hold-out names and why 1(c) on that side needed an intervention. The residue at `:66` recommends changing the brief; a brief defect that changed how one side was scored belongs in the errors list.
2. The twelve steward-written shared schedules all end `quiescent` (`:65` says so), so an `end: event` was first exercised by a hold-out, and the R model's two cannot-runs follow. Same class as error 6 (coverage of the steward's own schedules); either merge into 6 or list.
3. The log timestamp (finding 7, third bullet).
4. Measure 7 rated with the author's labels visible, and the unresolved disagreement (finding 6), if the steward agrees it departs from `:43`.
5. The steward's m7 tally slip (6 listed, 7 stated).

Errors 1 to 6 as listed are each confirmed by the log (`docs/seed-log.md:166,167,169,191` and prereg `:70`).

### 10. LOW. Judge independence on "same mechanism"

The arm A packets include `model/README.md`'s X2 section (`judge/prompt-A-H8.txt:9`, rule stated), which contains X2.5, the author's own diagnosis of exactly this failure; both A verdicts cite X2.5 as evidence. This is within the registered rule (not the steward's hypothesis), and the verdicts also rest on TLC states and trace lines, but "named by the judge in all three verdicts" (`:27`) is less independent than it sounds for A-H8 and A-H9. One clause.

### 11. LOW. X2-2 "confirmed" (`:38`) is vacuous on two cells

The R model ran neither H7 nor H8. "No unmutated side ... on any shared or hold-out schedule" holds on 14 of 16 hold-out side-cells. Say "on every run that ran".

---

## What is fine (checked, not merely read)

- Table `:8-13`: A model 31/31 and 30/30 (`armA/model-all.log`, `model-mut.log`); A impl 93/93 and 30/30 all seeds (`impl-all.log`, `impl-mut.log` last line); A hold-outs H7 P, H8 F C1_4/C1.4, H9 F, H10 P on both sides and every seed (`model-holdout.log`, `impl-holdout.log`); R model 31/31, 28/30 at v1 (`model-mut-v1.log`: P8.v1 PASS, P25.v1 UNEXPLAINED bound), 30/30 replacements, H7/H8 UNEXPLAINED, H9 P, H10 P; R impl 93/93, 30/30, renamed hold-outs H7 P, H8 P, H9 F every seed, H10 P.
- All three judge verdicts: explained, genuine yes, locus both / both / implementation, "neither D1 nor D4", one stall mechanism (leader keeps lease quorum, cannot reach requester, no relay, no step-down). `:27-30` quote them accurately, including the H8 detail that the crash step never fires because neither side records `Grant(c2)`.
- Measure 6: steward 0.60/0.50, Fable 0.40/0.375 (X2); baseline 0.60/0.64 and 0.20/0.545; kappa recomputes to 0.636 (X1) and 0.718 (X2); every disagreement (U02, U03, U14; V02, V14, V15) is steward P / Fable C, as `:22` says.
- Measure 7: contradicted sets as stated; kappa recomputes to 0.53 (model) and 0.61 (impl); the two raters agree exactly on the impl set; at-risk list hit 11, 25, 53 and missed 13 and 21.
- X2-6 ratios: 218/221 = 0.99, 185/138 = 1.34, X1 0.21 and 0.86. Confirmed-by-letter and the null-control argument are both right. X2-7: 0.375 < 0.64, falsified. X2-10: three of four, confirmed. X2-11: V01 rated C by both; `26d18d0` adds voter stickiness and `CheckQuorum`; confirmed, and the reclassification clause is the prereg's own (`:13`).
- X2-3 falsified: P25 and P26 PASS on all four sides; the "every author defended it" claim is supported (A model `CheckQuorum`; R model StepDown/CheckQuorum, `x2-r:model-regen/README.md:58-59,135-136`; A impl hashicorp/raft, R impl etcd raft with CheckQuorum per the judge).
- Hold-out author's probabilities (`:48`) match `X2-prereg.md:63`.
- Arm A commit timestamps are consistent with "steward runs are the first after each arm's merge": merge 06:18:01Z, runs 06:18:53Z; R merge 06:25:42Z, runs 06:25:58Z.
- The rename of R impl hold-outs is disclosed in the judge packet (`prompt-R.txt:5`), so the judge was not misled.

## Suggested minimal edits, in priority order

1. `:9` and `:34`: give both 1(b) numbers with their readings and provenance; add one sentence on what the headline is under the merged-artifact reading; note X2-1 is unaffected.
2. `:50-52`: replace "shared blind spot ... reproduced one, because ..." with the three-fact version (X2.5 declared in advance; shared steward inputs as common cause; the independent arm diverged), and present the cause as an inference.
3. `:10` footnote on R impl 3/4 (renamed files, hashes differ at line 1); `:34` caveat that R model's 1(e) = 0 is over two runnable hold-outs and that 1(c) and 1(e) count the same failures.
4. One line stating the fairness rule was applied to every model-side C1.4 PASS and what it found.
5. `:45`: say the steward knew the residue was present at registration; replace "no change needed to touch it" with "the author rewrote a sibling tag in the same file and did not reread the header".
6. `:24`: split wall-clock into preparation (2.5 h, before registration) and registration-to-scoring (about 1 h); `:17` fix the impl split.
7. Add errors-list items 1 and 2 from finding 9; append a log correction for the 06:3xZ timestamp.
8. Resolve or bracket measure 7 model 5/12; disclose that the steward rated with the author's labels visible.
