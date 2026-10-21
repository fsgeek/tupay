# Adversarial review of the replay pre-registration, draft 1 (`7f4590d`)

Reviewer: a fresh Claude Fable 5.1 instance, launched by the third steward on 2026-10-21 with no steward context; told it may know the defect and must not write its trigger usably; told not to open `tmp/`. It reports reading nothing under `tmp/` and not consulting memory tools. Its review, as returned (formatting kept; one HTML entity unescaped):

---

Ranked by how much each would damage the result's meaning.

## 1. K1 on the implementation side cannot distinguish faithful from repaired

Draft: "an artifact that does not violate J1.1 or J1.2 on K1 has built a repaired design." Then, one page later: "RP-4 (p = 0.10): R2 fires in either arm. Sampling three seeds per scenario rarely reaches a narrow interleaving."

Both cannot hold. The scenario format says "the model explores every such point, the implementation samples one." If three seeds rarely reach the narrow interleaving on a shared scenario, they rarely reach it on K1 either, so a faithful Codex implementation that happens to miss it on the sampled points is scored "repaired", and RP-5 is credited on a sampling accident. The faithfulness question Q3 is then unanswerable on the side that matters most (the one whose author recalls the fix).

Replacement: "On the implementation side, K1 is run over a registered seed set (seeds 1 to N, N fixed here; I suggest 30). Faithfulness is decided by two things together: the K1 outcome and the judge's reading of the code path that begins a configuration change (does it wait on anything beyond the specification's step 3?). FAIL on any seed: faithful. No FAIL and the judge finds a gate: repaired. No FAIL and the judge finds no gate: `UNEXPLAINED sampling`, reported as such, not as repaired." The classification in (a)/(b)/(c) already needs the Choices text; the code reading is the same judgement made on the artifact rather than its label.

The model side has the matching hole. "TLC explores K1 exhaustively within the author's bounds and finds no violation" also happens when the author's schedule compiler cannot express a K1 step (a selector, a trigger filter) and silently drops or misplaces it, or when the abstraction omits something K1 needs (durable state on restart, directional loss). Neither is a bound hit, so the draft would score it "repaired". Add: "A model K1 run ends in one of: FAIL (faithful); PASS with a gate found in the model's change action (repaired); PASS with no gate found (`UNEXPLAINED compile`, the compiled K1 is attached); bound (`UNEXPLAINED bound`); rejected or not run (`K1 not run`, with the runner's message)." Register K1's resource needs now, as numbers only (epochs, journal length, events, members touched), so a bound hit can be read: a model whose bounds are below K1's needs was never able to answer Q3, which is a different finding from one that explored K1 and found nothing.

Two more cells are unspecified: (b) with K1 FAIL (the gate is broken, or the classification was wrong: say "scored faithful by K1; the classification is reported as contradicted"), and (c) which currently conflates "neither" (the pure design, K1 should FAIL) with "another mechanism" (unknown). Split (c) into "(c) neither" and "(d) another mechanism, described".

## 2. R1, R2 and R5 have no attribution step; "divergence" is undefined; the judge knows the bug

Draft: "R1 Model checking. A TLC counterexample to J1.1 or J1.2 on a shared scenario…". R3 requires that "the third-family judge (Gemini) traces the divergence to the defect"; R1, R2 and R5 require nothing of the kind. A counterexample produced by a mis-modelled vote count, or an implementation that loses a durable write, fires R1 or R2, and on a K1-faithful artifact answers Q1 yes. That is the headline result, and it can be produced by an ordinary artifact bug.

Replacement, for R1, R2 and R5: "…and the trace, read by the judge against the question `replay/observe.md` poses (which configuration each involved member had in effect at each election and commitment, and whose grants or acknowledgements were counted), shows the violation arising from configurations in effect rather than from an error in the artifact's own mechanics. A violation the judge attributes to artifact error is reported as a shared-scenario FAIL and does not fire the route." The attribution criterion can be made mechanical from `ConfigInEffect`, `Elected` and `Committed` records, since observe.md was written to answer exactly that question; register the script or the rule, not the judge's opinion, as the deciding thing.

Gemini's probe (`gemini-stream.jsonl`) shows it knows the fix and ties it to the commitment rule. The draft discloses that the judge knows the defect but does nothing about it. A knowing judge asked "is this the defect?" will say yes to any configuration-flavoured trace. Add: the judge packet contains the trace and observe.md's question only, never K1's outcome, the classification, or this file; and a second reading by Grok (unknowing) of the same packet is recorded, with disagreement reported.

Measure 4, "Divergences on shared scenarios", and R3 both depend on a definition the draft never gives. X2 had one; this round does not. Add: "An arm's sides diverge on a scenario when their outcome labels differ (PASS / FAIL clause / UNEXPLAINED kind), an implementation's label being FAIL if any seed fails, UNEXPLAINED if no seed fails and any seed is UNEXPLAINED, PASS otherwise. Trace-level differences without a label difference are reported, not counted."

## 3. No shared scenario can reach the defect's preconditions; the draft says "lean", not "cannot"

Draft, RP-2/RP-3: "the shared scenarios were written not to lean toward the trigger". The log is blunter ("none places a coordinator change inside a membership change"). Reading S1 to S8: every scenario with two changes gates the second on `ChangeReplied ok`, and every scenario with one change has no coordinator change inside it. The defect needs more than one change in flight across a coordinator change. So R1 and R2 on shared scenarios are impossible by construction, not unlikely, and RP-2/RP-3 are really "an unprompted Grok writes its own scenario of the right shape and runs it within bounds that admit it".

Two practice rules are also broken by the shared set. `docs/steward-practice.md`: "Shared schedules exercise every form the format allows, including an event `end:`." All eight end `quiescent` (X2 error 6, repeated). G1.4's second sentence, "A request that … times out may be retried at another member", is exercised by no scenario, and neither is the `crash`-during-change cell product G1.1 × G1.4, which the failure model names and the contract's J1.1 is about.

I would not add a leaning scenario now; the freeze is right. But the registration must say: "No shared scenario places a coordinator change inside a membership change, so R1 and R2 can fire only from author-initiated exploration; the shared set does not exercise `end:` on an event or G1.4's retry sentence. Both are registered residues." And RP-2/RP-3's reason should read "cannot reach" rather than "not lean".

Related: Grok's probe is weaker than the draft's "showed no recall of the defect". Grok wrote: "A second change started sooner can commit on voters that miss the configuration a later leader is elected under, so an entry treated as committed is missing from that log." It does not recall the 2015 report; it does state the hazard class in one sentence. Quote this in the Arms section. It also raises RP-8 (Grok R4-before, 0.15): a Grok author restating the design's own one-change rule as a concern must not count (see item 4).

## 4. R4 cannot be scored as written, and the brief makes R4-before nearly impossible

Draft: "R4 Author naming. An author's README names the defect (the trigger, or the gate that fixes it) as a concern. Scored before the author's first run…". But brief item 4: "Before your first run, commit a README section **Choices** … After your runs, add **Concerns**." Concerns exist only after runs, so R4-before can fire only through the Choices section, and the (b) text makes the credit turn on "named it as a concern rather than a choice", which is the author's own labelling.

Three ambiguities. (i) Choice versus concern is a wording difference the author controls. (ii) "Names the gate" is satisfied by Codex implementing it as a convention with no safety claim; "names the trigger" is nearly satisfied by D's own sentence that overlapped changes "could degrade to unsafe situations". (iii) Who decides? The draft says the steward classifies, and the steward knows the bug.

Replacement: "R4 fires when the README asserts that the design as specified admits a violation of J1.1 or J1.2 and gives the mechanism; restating the specification's one-change-at-a-time rule or the quorum-overlap argument is not naming. Adding the gate without a safety claim is classification (b) without R4. R4-before is read from the Choices commit only; the brief asks for a **Concerns** section both before the first run (from reading) and after. The rater is Grok, given the registered criterion and the README section with its commit, without the artifact's run results; the steward's reading is recorded beside it." Apply the same to the (a)/(b)/(c)/(d) classification at step 6: committed before runs is good, blind would be better.

## 5. The briefs are not in the registration

Draft: "Briefs (fixed here; the same in both arms except for the specification's name)" lists six items, but no brief file exists under `docs/briefs/` for the replay, and every leak found so far (setup findings 1 to 3, 8) lived in a sentence. An outsider cannot check the thing authors actually read. Register the four brief files by hash in this file, or inline them. Two specifics to check in them: the word "Raft" must not appear in arm F's brief (the Arms section's "no consensus or Raft library" would undo Q2's blinding for F if it is carried over), and `AGENTS.md` rule 1 tells authors to read `docs/seed.md`, which their checkout excludes; the M1 brief handled this and the replay brief must too.

## 6. Timeline words that score two ways

- "before reveal" / "before any hold-out or K1 is revealed": say "before the commit on `main` that adds `K1.yaml` and the hold-out files". Also say when authors stop: "The artifact scored is each author's tagged first-version commit; K1, hold-outs and shared scenarios run against it; later commits are reported separately and fire no route." The draft never fixes the stop point, so an author's post-first-version exploration is of uncertain status.
- "commit … before its first run" is unverifiable from the git record alone; say the harness transcript is the check, or say it is taken on trust.
- RP-5: "fails K1's faithfulness check (repaired)" reads both ways. Write "passes K1 (no violation) and is scored repaired".
- RP-6: "both Grok models are faithful by K1 (or UNEXPLAINED bound)". The disjunction makes the prediction true on a model that explored nothing. Split: RP-6a both faithful (K1 FAIL), RP-6b at least one `UNEXPLAINED`, with separate probabilities.
- RP-9 "agree on every route": define as equality of the set of (route, side, before/after) pairs.
- "Q1 is answered yes if R1, R2 or R3 fires on an artifact that K1 shows to be faithful": for R3 say which side must be faithful (the side that witnessed the violation), and say that an `UNEXPLAINED` K1 never supports a yes.

## 7. K1 itself has not been checked against the frozen format

K1 was "written by the second steward"; the format then gained the `command` action and the rule that `coordinator` before any `Elected` is rejected. The log records the hash as unchanged but not that K1 was re-read against the frozen format. If K1 uses a selector in a position the frozen rules reject, every artifact comes out "K1 not run". Add a line: "The steward checked K1 against the frozen format by reading, not running, on <date>; it uses selectors S and actions A" (counts only). Also disclose whether K1 has ever been executed against anything; if the second steward ran it against a reference model, that is an outcome that informed the design and should be named.

The format's `coordinator` selector, "the member most recently `Elected`", presumes a cross-member order that `observe.md` deliberately forbids ("There is no cross-member clock"). Two members can each record `Elected` with no order between them (that is the J1.1 violation). The implementation runner will resolve it by arrival order at the harness, differently per author. For K1 this matters. Register: "In the implementation, 'most recently' means order of arrival at the runner's event sink; the runner logs the resolution."

## 8. Order of execution gaps

- Step 6 classification and step 7 runs are right, but `steward-practice.md` requires that "before hold-outs run, the steward answers each declared limitation in the log". Insert it between 6 and 7.
- Step 8 judge: say the packet excludes K1 outcomes, the classification and this file, and follows the 120k-character rule.
- Step 1 says of review-driven changes "none can [be outcome-informed]: nothing has run". The probes, the fidelity audits and possibly K1 have run. Say "no author artifact has run".
- Minimum model bounds: brief item 5 lets authors pick bounds with reasons. Require at least that every shared scenario reaches `quiescent` within them, else the bounds are a declared limitation; without this a model with epoch ≤ 2 passes everything and K1 is a bound hit.

## 9. Omissions an outsider needs

- The seeds the steward uses, per scenario and for K1 and hold-outs.
- A prediction on mutation kills (measure 1 lists them; none is predicted).
- The scenario fixes and the `command` action (finding 8) were frozen without an unknowing reader; the Grok recheck covered F's lines only. Add to residues.
- A note that R5, if the hold-out author writes the trigger, is K1 under another name, and that RP-11 then measures "does a faithful artifact exist", not detection.
- The hold-out author's instruction, "scenarios a careful but conventional author's artifact might mishandle", is a nudge toward the known defect from a family that knows it; fine, but say that is why R5 is memory-possible rather than leaving the reader to infer it.

## Probabilities, in sum

RP-1 at 0.30 against RP-2/3/4 is coherent only under strong positive correlation across arms; state that assumption. RP-2/RP-3 should be restated as probabilities of author-initiated exploration (item 3). RP-6 is inflated by its disjunction (item 6). RP-4's reasoning contradicts the K1 rule (item 1). RP-7 (0.50) is low given D says "Raft" and "LogCabin" on every page and Codex's probe recalled the gate verbatim; I would put it nearer 0.65, but the number is the steward's to defend, not mine to set. RP-8's 0.15 needs the sharpened R4 criterion or it is unscoreable (item 4).

Nothing here requires touching the frozen inputs. Items 1, 2, 4 and 6 are text changes to the registration; item 5 is adding files to it; items 3, 7, 8 and 9 are disclosures.
