I have what I need. The hashes in the design check out (`c9b8a814…` / `ff6998de…` both match the files), the section numbering in the text is usable, and the text does contain explicit environment-assumption statements (3.8, 3.9, 6.4.1, 8.1 at line 4317, 5.1.3). The findings below are about the design and brief, not the source.

# Adversarial review of D1 (design draft 2 + brief-enumerate.md)

## Blocking

**1. The order rule is not actually fixed before the lists exist.**
Text: design §Phases 1, "Phase 2's order, fixed here before any list exists" vs. §Open, "the phase 1 rule's exact form" is "decided in the prereg", and §header, "the prereg follows phase 0".
Failure: the steward writes the binding version of the rule with both enumerations in hand. Any ambiguity resolved then (see 9) is a choice that can promote or demote a known cell. An outsider reads this as "rule chosen after seeing the data", and nothing in the commit chain refutes it.
Fix: finalise the rule in design.md now, as a total order with every tie-break specified (see 9), and state that the prereg may restate it but not change it. Any later change is an additive amendment that says it was made after seeing the lists.

**2. The enumerator sandbox is specified by an honour-system sentence, and the residue is physically in the checkout.**
Text: brief, "Read nothing else in this checkout except this brief and `AGENTS.md`"; design §Phases 0, "in `author-sandbox.sh`, no web".
Failure: if the checkout is the tupay repo or a worktree of it, `experiments/D1/design.md` sits beside the brief and names etcd-io/raft#166 and the 2015 membership defect by name; `docs/steward/candidates-2026-10-23.md` is present; `git log -p` exposes every steward log. "Read nothing else" is unenforceable on an agent, and a skeptic will assume it was read. (I did not read `author-sandbox.sh`; it was outside my remit, so I cannot confirm what it does. The design must say.)
Fix: each enumerator gets an orphan repository containing exactly `brief-enumerate.md`, `AGENTS.md`, `source/OngaroPhD.txt` (and the PDF), no history. The steward commits a `find` + sha256 manifest of that sandbox before launch; the brief asks the enumerator to paste `ls -R` and `git log --oneline` into its report as evidence. design.md and the candidates file are never in that tree.

**3. The brief's "promises" sentence is a measurable steer toward chapter 6 and the lease-read clock assumption.**
Text: brief §Task, "safety: election safety, log matching, leader completeness, state machine safety, linearizable reads where the text claims them".
Figure 3.2 (text lines 952-962) lists five properties: Election Safety, Leader Append-Only, Log Matching, Leader Completeness, State Machine Safety. The brief drops one of the five and adds "linearizable reads", which is not a Figure 3.2 property; the only place the text makes reads a promise with an environmental precondition is 6.4.1 (lines 3144-3148: "assumes a bound on clock drift… scheduling and garbage collection pauses, virtual machine migrations… arbitrarily stale information"). That is the territory of etcd-io/raft#166, which the steward knows. The addition is exactly what a reviewer looks for when asking "where did the author's prior knowledge leak into the instrument".
Failure: an enumerator primed to treat linearizable reads as a promise will enumerate the clock-drift contract with silent 5 / detectable no, and the order rule puts it at or near the top. The blind result is then a rediscovery of the one bug the steward named.
Fix: quote Figure 3.2's five properties verbatim and add a neutral catch-all ("and any other guarantee the text makes to clients or operators"). Do not name reads. Record in the design that draft 2 named them, and that the change was made before any enumeration.

**4. How many cells phase 2 covers, and the per-cell budget, are set after the ordered list exists.**
Text: design §Open, "budget"; §Phases 2 has no k.
Failure: the steward sees the ordered list, then chooses k. Including or excluding a specific cell is one integer away. Same for "the implementation does not implement this feature, skip": whether a cell is "not applicable" is a judgement made with the list in hand.
Fix: fix now, in design.md: k (I would say 3 or fewer, see 18), a per-cell budget in hours and in model-checking/harness runs, and the skip rule ("a cell is not applicable iff the SUT in its default configuration has no code path that depends on the contract; the evidence is a cited code location; the next cell is taken; skipped cells are reported").

**5. The target implementation rule is deferred, and the obvious rule picks the implementation the residue is about.**
Text: design §Phases 2, "a real, widely deployed implementation, chosen by a rule registered in the prereg".
Failure: "most widely deployed" picks etcd/raft nearly deterministically, and the steward's residue (#166) is an etcd/raft issue. Even if that is the honest choice, a reviewer cannot distinguish it from a reconstruction. Two further leaks: (a) the SUT boundary (etcd/raft the library is tick-driven and clock-free; the clock contract only exists at the etcd server level, so "library vs server" decides whether the clock cell is testable at all); (b) configuration (etcd's lease-based reads are off by default; choosing a non-default config to make a cell applicable is a choice).
Fix: name the rule in design.md now, before phase 0, including SUT boundary and "default configuration, released version X as of date Y". Or pre-register a shortlist of three and pick by a public randomness beacon (NIST beacon pulse or hash of a declared future block) at a declared time after the prereg; commit the mapping from beacon output to choice before the pulse.

**6. A rediscovery of a residue item is scored as a "weaker result" when it should be scored as contaminated.**
Text: design §Question, "A blind rediscovery of a reported one is reported too, as a weaker result: it shows the workflow can find a bug when no one tells it where".
Failure: if the finding is #166 or the 2015 defect, no one "told" the workflow where to look except the person who wrote the brief and the order rule knowing them. By the project's own standard that is theater with extra steps, and the design pre-licenses it as a positive.
Fix: cite the commit hash of `docs/steward/candidates-2026-10-23.md` in design.md so the residue is verifiably pre-recorded; pre-commit that any finding matching a residue entry, or matching a line in an enumerator's Recognised section, is scored "contaminated rediscovery", reported as a known-answer outcome and not as evidence for the Question. Publish the residue list with the result.

**7. No predictions, no scoring, no definition of a null result.**
Text: AGENTS.md 3, "Pre-register before any outcome-bearing run. Commit the predictions and scoring first"; design §header, "Not a pre-registration".
Failure: phase 0's output determines every later step, so it is outcome-bearing in the only sense that matters here, and it runs under a document that disclaims being a prereg. Nothing says what phase 0 result would abort (e.g. lists under N cells, quote verification failure rate over X%), what phase 2 outcome counts as a finding vs noise, or how "no divergence in k cells" is reported. A null result will be absorbed silently, and a positive will be scored post hoc.
Fix: before phase 0, add a short predictions-and-scoring section: expected cell-count range per family, expected overlap, abort criteria, the finding/no-finding definition, the null-result report template, and the maintainer-response scoring categories (see 14).

## Should-fix

**8. "Blind" is false for the enumerators, and the design claims it anyway.**
Text: design §Why blind, "no step that chooses where to look may use knowledge of reported bugs".
The silent and detectable ratings are the step that chooses where to look, and they are produced by models trained on Jepsen analyses, the PAR/CTRL storage-corruption paper, etcd and Consul issue trackers, and the Cloudflare liveness post. A rating of "silent 5" for clock pauses is a compressed recollection of that literature. Self-reported Recognised lines do not fix this; models under-report and confabulate.
Fix: (a) reword the claim to what is true: steward-blind and search-free, not blind; (b) measure contamination rather than assert its absence: phase 3 runs the prior-report search over every tested cell, not just findings, and reports what fraction of the top-k has a prior public report; (c) add a field to the brief, "basis for silent: text / general systems experience / a specific report I recall", so the self-report is per-cell and gradable.

**9. The order rule is underdetermined and partly perverse.**
Text: design §Phases 1, tiers (i)-(iv).
Problems: (i) "higher of its ratings" on an uncalibrated 1-5 scale means whichever family rates high dominates; expect many ties at 5. (iii) "found by one family before found by both" inverts the usual evidence rule and makes the merger's granularity decision the ranking decision (unmerged cells get the single-finder bonus; merged cells get the max-silent bonus; the two pull opposite ways). It also puts a hallucinated single-finder cell above a solid double-finder. (iv) "earliest source section" is undefined for merged cells with different citations, for figure citations ("Figure 3.1"), and for front matter; and "section" vs "subsection" ordering must be a numeric tuple, stated.
Fix: rank-normalise silent within each list and use the mean rank, with max as a pre-registered sensitivity analysis; drop (iii) or justify it with something other than a steward heuristic; define (iv) as min over merged members of the numeric section tuple, figures mapped to the section containing them, front matter = (0); final tie-break by a public randomness beacon at a declared time, never by anything the steward or the merger controls.

**10. The merge is a single pass by one model with web-capable tooling, and it sees the Recognised sections.**
Text: design §Phases 1, "A third family (Gemini, via `agy`), given only the two lists, merges them".
Failure: merge granularity is the ranking lever (see 9); a single Gemini run is unreproducible; `agy`/Gemini CLI ships with web search enabled by default; the two Recognised sections name known bugs, so the merger inherits the contamination and can steer merges toward them.
Fix: strip Recognised sections before the merge (commit them sealed); run two independent merges (second Gemini instance, or a fourth family) and accept only merges both produce, leaving disagreements unmerged and listed; disable all tools; do not tell the merger the order rule; allow one E to map to several Ds (a broad contract split against a fine one), with D.silent defined over all mapped Es.

**11. No mechanical check that cited quotations exist.**
Text: brief, "source: section number and a quotation of at most two lines".
Failure: a fabricated contract with a fabricated quote enters the union, and under tier (iii) a single-finder cell is favoured. Nothing between phase 0 and phase 2 catches it, and dropping it later is a steward choice.
Fix: add to design.md now: every quotation is grep-verified against the txt after whitespace normalisation (page-header interleaving tolerated); unverified cells are kept but ranked last, by rule. The check is scripted and committed before phase 0.

**12. The Recognised sections flow into phase 2.**
Text: design §Phases 2, "failure model (the cells) as inputs".
Failure: if the failure-model file handed to the TLA+ author and the harness author is the enumeration, both read a list of known bugs by name before deciding what to build.
Fix: the failure model given to phase 2 contains only merged contract fields (contract, violation, at-risk, detectable, silent, source). Recognised sections, the E-to-D mapping, and ratings disagreements are committed but not passed.

**13. Phase 2 authors are not blind either, and reuse of the target's own test infrastructure is unaddressed.**
Text: design §Phases 2.
Failure: etcd ships gofail failpoints, a robustness suite with LazyFS and Porcupine, and etcd/raft ships a TLA+ spec with trace validation. A harness author who reaches for these finds what those tools were built to find; the finding is then the maintainers' tooling, credited to the workflow. Also no statement that phase 2 authors have no web.
Fix: decide now whether reuse is permitted and how it is tagged (derives tags should name the tool); require no-web sandboxes for both authors; require the harness author's first commit to be the injection design from the cell alone, before touching the target's test directory.

**14. "A contract real deployments violate silently" has no judge and no scoring.**
Text: design §What this does not claim, "reported from the enumerators' ratings and the maintainers' response".
Failure: ratings are guesses (see 8); maintainer responses span accepted-and-fixed / "known" / "documented precondition, won't fix" / silence, and the design does not say which count as what or how long to wait. Many silent-violation contracts are documented operator requirements (fsync, NTP, lease-read warnings in etcd docs), and "documented" is the dismissal the design itself names.
Fix: pre-register response categories and their scoring, a disclosure deadline, and a documentation check in phase 3: does the target's documentation state the contract as an operator requirement? If yes, the finding is "documented precondition", scored separately.

**15. Phase 3's novelty search is run by the person who holds the residue, with no stated procedure.**
Text: design §Phases 3, "a literature and issue-tracker search for prior reports of each finding".
Failure: the search is unfalsifiable as written: no venues, no queries, no operator, and it only runs on findings, so contamination of the cell list is never measured. Also, OTS stamps prove existence by a time, not that no search preceded it; the design's "the commit order… is published with it" implies more than it proves.
Fix: pre-register venues (etcd, etcd/raft, hashicorp/raft, TiKV raft-rs, Jepsen, DBLP keywords), query templates, and that an instance without the residue runs it over all tested cells; state in the claim that the chain evidences procedure, not absence of prior knowledge.

**16. No positive control, no negative control, no stability measure.**
Text: none; the design has no controls section.
Failure: a null result cannot be interpreted (weak workflow vs correct implementation), and a positive cannot be distinguished from a harness artefact. AGENTS.md 5's mutation pairs are per-test, not per-workflow.
Fix: (a) known-answer: run phase 2 against a pre-fix release of the target for one environment-contract bug chosen by someone other than the steward and sealed until after the blind run, score whether the workflow finds it; (b) placebo cell: one contract the target demonstrably defends, expect no finding; (c) stability: run phase 0 twice per family and report rank stability of the top-k; if the top cell changes between runs, "selection by a rule" is selection by sampling noise.

**17. The contract (C-clauses) is not written before phase 0.**
Text: design §Phases 2, "Contract (Raft's safety and liveness promises)… as inputs".
Failure: whoever writes the C-clauses after the cells exist writes them to fit.
Fix: write and commit the contract now from Figure 3.2 and 6.3, before enumeration; cells' "at risk" fields are then mapped onto it by rule.

**18. Phase 2 has no budget and the engineering is heavy.**
Text: design §Phases 2 and §Open, "budget".
Reality check: fault injection into a Go binary is not LD_PRELOAD work (Go issues raw syscalls; clocks go through vDSO), so storage cells need LazyFS/dm-flakey/gofail, clock cells need tick manipulation at the library boundary (which invites the "you ticked wrong" dismissal), and the observability layer needs a linearizability checker. A TLA+ model with environment actions per cell will need tight bounds to check at all. The replay exploration gap (§Open) is acknowledged but unbudgeted. This is weeks per cell at minimum.
Fix: k ≤ 3; treat the first cell as a pilot with its own additive prereg; set a per-cell abandon rule in hours; name the injection mechanism class per environment category in the prereg so it is not improvised per cell.

## Minor

**19.** Brief: "1 rare, 3 occasional, 5 routine" has no base (per cluster-year? per deployment?); "how long you read" is meaningless for a model; "detectable" does not say whether by an implementation in principle or by the SUT; the brief says "commit it" but the OTS hook needs network in a no-web sandbox (say the steward stamps on import); both enumerators write `enumeration.md` at the checkout root (fine if checkouts are separate; say so). Add a sentence defining "environment contract" vs "protocol rule" so chapter 4's single-server algorithm (the text's version carries the 2015 defect) does not yield protocol-internal cells under "configuration and operators".

**20.** Brief: the Recognised section, requested at the end, still primes recall of known bugs during the task. Low cost to keep, but accept it is a self-report and score it as in 6/8 rather than treating it as a filter.

**21.** Design §header cites "log 2026-10-25 items 1, 4, 8, 9" and "counsel: run both"; an outsider cannot read those. Either inline the one-line content or drop the citations from a document meant to be published.

## What I would block phase 0 on

Items 1, 2, 3, 4, 5, 6, 7 are blocking as stated. I would also require 9, 11 and 17 before phase 0, because each changes a rule that must exist before any list does (the total order, the quote-verification consequence, and the contract the cells are later mapped to). Items 10, 12 and 13 must be settled before phase 1 and 2 respectively, but need not hold phase 0. Items 8, 14, 15, 16 and 18 belong in the prereg, and 8 and 16 should change the wording of the Question before anything is published.

Files reviewed: `/home/tony/projects/tupay/experiments/D1/design.md`, `/home/tony/projects/tupay/experiments/D1/brief-enumerate.md`, `/home/tony/projects/tupay/AGENTS.md`, and sections 3.8, 3.9, 5.1.3, 6.4.1 plus Figure 3.2 of `/home/tony/projects/tupay/experiments/D1/source/OngaroPhD.txt`. Nothing was written or run with side effects.