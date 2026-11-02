{"findings": [
  {
    "id": "F1",
    "severity": "omission",
    "where": "Measures table, row 3 (Cost) and Departures and disclosures",
    "finding": "The draft reports only total author tokens and total author wall-clock, omitting five registered Measure 3 and Measure 9 cost items: (1) arm A's split at its first commit after predictions, (2) steward time, (3) advisor tokens, (4) decisions asked of Tony (which measure3-cost.md still marks as 'to be gathered/counted for the result'), and (5) Measure 9 planter tokens.",
    "evidence": "Registration Measure 3: 'Tokens and wall-clock per author (harness-reported); arm A split at its first commit after predictions; steward time; advisor tokens; decisions asked of Tony.' Registration Measure 9: 'planter tokens in measure 3.' Evidence measure3-cost.md: reports arm A wall-clock split (A impl 19m10s / 5m52s; A model 1h22m17s / 3h46m08s), notes steward time was 'not measured', leaves Grok/Fable advisor tokens 'to be gathered into the result', leaves Tony's decisions 'to be counted from the log and khipumaq for the result', and omits planter tokens."
  },
  {
    "id": "F2",
    "severity": "omission",
    "where": "Measures table, rows 1(a), 1(c), and 5 (R impl and A impl)",
    "finding": "Measure 1(a) requires per-seed pass rates and unreached schedule counts to be reported separately, which the draft omits. In addition, the cited evidence block for armR-impl schedules.txt is completely empty, providing no schedule-level evidence lines for R impl's claimed 59/59 in 1(a), 4/4 in 1(c), or 35/35 in Measure 5.",
    "evidence": "Registration Measure 1(a): '(implementation: a schedule passes only if all ten repetitions of all three seeds pass; per-seed rates reported); unreached reported separately.' Evidence section 'experiments/X3/runs/armR-impl: verdict counts per schedule (from schedules.txt...)': empty block (0 lines)."
  },
  {
    "id": "F3",
    "severity": "error",
    "where": "Measures table, row 4 (residue, R model) and Departures and disclosures",
    "finding": "R model is scored as 0 residue by excluding a match on `-config \"$cfg\"` in the shell script `model-regen/tlc.sh` under the registered exclusion for 'TLC `.cfg` files', even though a `.sh` script is not a `.cfg` file. Moreover, `residue.py` was modified after its first run on R model to allow multi-line wrapped tags (removing `model-regen/mutations/make.py` as a candidate) and the first run's output was discarded, violating the append-only rule, while the registered full diff read was not performed and this omission is not disclosed in the draft.",
    "evidence": "Registration Measure 4: 'Excluded: TLC `.cfg` files, generated files, the YAML key names a compiler parses, Go configuration structs that hold no membership, and Unix-time code. Rule (iii), tags naming a retired id, is expected to be zero on every side ...: reported, not scored.' Evidence residue/RESULT.md: 'The first run's output was not kept; it differed only by that line'; 'R model, `model-regen/tlc.sh` (excluded)... If the exclusion is not accepted, arm R's model has residue 1'; 'Not done: The registered \"read of the diff for anything the procedure missed\" was limited to the candidates and list tags above. ... A full read was not made'."
  },
  {
    "id": "F4",
    "severity": "omission",
    "where": "Measures table, row 4 (residue)",
    "finding": "Registration Measure 4 requires Rule (iii) (tags naming a retired id) to be explicitly reported on every side ('reported, not scored'), and X2's procedure breaks residue down into rules (i), (ii), and (iii), but the draft table reports only a single combined residue integer per side.",
    "evidence": "Registration Measure 4: 'Rule (iii), tags naming a retired id, is expected to be zero on every side (no author saw C3.2, C3.3, C3.6, P34 to P39 or P55 to P57): reported, not scored.' Evidence residue/RESULT.md table: rows '(i) term without its tag', '(ii) list tag not matching what the element runs', '(iii) retired id in a tag: 0 | 0 | 0 | 0'."
  },
  {
    "id": "F5",
    "severity": "omission",
    "where": "Measures table, row 8 and Readings section, item 1",
    "finding": "Measure 8 requires reporting, beside the `UNEXPLAINED inputs` counts, the registered design fact per side (whether the grant path consults a clock: yes/no) and reporting every side that consults no clock as passing the F3.2 schedules and P44 'vacuously by design'. The draft table omits the design-fact row and omits that arm A's model and arm R's implementation also have `no` for consulting a clock on the grant path.",
    "evidence": "Registration Measure 8: 'Read beside it, per side, a design fact registered from the README and the traces before scoring: does the grant path consult a clock (yes/no). A side that consults no clock passes the F3.2 schedules and P44 vacuously as to clocks: counted as PASS (the contract permits it), reported as \"vacuous by design\".' Evidence measure8-design-fact.md: 'arm A model: no', 'arm R model: no', 'arm A impl: yes', 'arm R impl: no'; 'Three sides (both models, arm R's implementation) pass the F3.2 schedules and P44 vacuously by design as to clocks: counted as PASS, reported as such.'"
  },
  {
    "id": "F6",
    "severity": "error",
    "where": "Measures table, row 1(c) (R model) and Readings section, items 1 and 2",
    "finding": "The draft treats Departure 3's 'vacuous by design' rule inconsistently across 1(a), 1(b), and 1(c): (1) it applies Departure 3 to hold-outs H11 and H12 in 1(c) to reduce R model from 3 to 1, even though Departure 3 specifies 'Needed reach is registered, per schedule, in experiments/X3/reach.md ... A failed audit makes the schedule \"no support\" in 1(a), counted as not PASS, and its mutation unassessable in 1(b)' and Measure 1(c) does not reference Departure 3; (2) in Reading 1, it says Measure 8's reading applies to all 8 clock rows in 1(a) and H11/H12 in 1(c), whereas Measure 8 states only that a side consulting no clock 'passes the F3.2 schedules and P44 vacuously as to clocks'; (3) in 1(b), it counts R model's 8 vacuous schedules as assessed kills (53/54) rather than unassessable (45/54), even though those 8 schedules did not pass the full support audit (`VACUOUS not modelled: clocksteps, maxticks`).",
    "evidence": "Registration Departure 3: 'every model PASS is scored only after the steward has run a probe showing the checked space contains the schedule's needed reach... A failed audit makes the schedule \"no support\" in 1(a), counted as not PASS, and its mutation unassessable in 1(b). A side that does not model a quantity a row needs (no clock, no incarnation) is \"vacuous by design\" for that schedule: reported, not PASS.' Registration Measure 8: 'passes the F3.2 schedules and P44 vacuously as to clocks: counted as PASS'. Evidence audit/R-verdicts.txt: P32, P41, P44, P47, P50, P53, P59, P62, H11, H12 have verdict `VACUOUS not modelled: clocksteps, maxticks`."
  },
  {
    "id": "F7",
    "severity": "omission",
    "where": "Measures table, row 7 (interpretations contradicted)",
    "finding": "For Measure 7, the draft reports only `15 / 9 of 85` (impl) and `6 / 5 of 46` (model), omitting three registered elements: (1) the implementation count out of the 77 non-workflow/result entries ('77 excluding eight workflow or result entries, reported beside it'), (2) the separate column for 'entries contradicted before X3 rated in their own column', and (3) how the contradicted entries compare against the registered at-risk lists (model 8, impl 13).",
    "evidence": "Registration Measure 7: 'model README 46 entries, impl README 85 (X2's rule, every numbered entry; 77 excluding eight workflow or result entries, reported beside it); at-risk: model 8, impl 13; entries contradicted before X3 rated in their own column.' Evidence raters/RESULT.md: 'impl (of 77, beside): 14 | 9'; 'Own column, as the registration requires: entries contradicted that the old README had already marked superseded: DeepSeek 0 on both sides; Kimi 1 on impl (81), 0 on model.'"
  },
  {
    "id": "F8",
    "severity": "error",
    "where": "Predictions table, row X3-1a and Scoring rule section",
    "finding": "The draft declines to score X3-1a ('Both are reported; the steward does not choose'), departing from the explicit rule in the registration's Scoring rule section: 'Mixed is reported as mixed and scores X3-1a as not confirmed.' Additionally, the Scoring rule section states 'arm A is strictly more correct on 1(c) model, 1(d) impl and 1(e) model, and more expensive', grouping the items together instead of 'item by item, beside \"mixed\"', and overlooking that on the model side arm A had lower wall-clock time than arm R (5 h 08 min vs 5 h 26 min).",
    "evidence": "Registration Scoring rule: 'Mixed is reported as mixed and scores X3-1a as not confirmed. Where arm A is strictly more correct on an item and more expensive, the result says so in those words, item by item, beside \"mixed\".' Evidence measure3-cost.md: A model wall-clock `5 h 08 min 25 s (harness 18,491 s)` vs R model `5 h 25 min 50 s (harness 19,501 s)`."
  },
  {
    "id": "F9",
    "severity": "omission",
    "where": "Measures table, row 10 and Predictions table, row X3-7",
    "finding": "Measure 10 states that 'A class no check can flag by design is a stated outcome, a result for the schema, not for the arm.' For arm A, the chooser picked storage restart from an older state, which was registered as 'no check flags it, by design', but the draft table records `no / yes` under `A impl` without stating that 10(i)'s `no` is a result for the schema rather than a deficiency of arm A. Also, as `recon/RESULT.md` notes, the steward who named the failures in 10(ii) had read `measure10-expectations.md`, which described both chosen hook classes in detail, weakening the blind reconstruction claim in X3-7.",
    "evidence": "Registration Measure 10: 'A class no check can flag by design is a stated outcome, a result for the schema, not for the arm.' Evidence recon/RESULT.md: 'storage restart from an older state was registered as \"no check flags it, by design\", and none did... The namer did not write the hooks, but it is the same steward who read the registered expectations, and both choosers picked classes those expectations describe in detail.'"
  },
  {
    "id": "F10",
    "severity": "overstatement",
    "where": "Predictions table, row X3-4 and What X3 shows, bullet 2",
    "finding": "The draft asserts that on all 13 failed support-audit schedules for arm A's model, the failing floor was `terms = 2` and that 'with terms at 1 all 13 have support, beside', but the cited audit verdict file (`audit/A-verdicts.txt`) contains only `NO-SUPPORT search complete` lines and provides no evidence identifying `terms = 2` as the sole failing floor or demonstrating support at `terms = 1`.",
    "evidence": "Draft X3-4: 'confirmed (A model, 13; failing floor terms = 2 on all; with terms at 1 all 13 have support, beside)'. Evidence audit/A-verdicts.txt: `VERDICT side=A schedule=P8 mutant=0 NO-SUPPORT search complete, distinct=2900 seconds=3` (and similarly for P17, P19, P22-P25, P28-P30, H7, H9, H10, with no per-floor breakdown or `terms = 1` rerun)."
  },
  {
    "id": "F11",
    "severity": "minor",
    "where": "Measures table, row 2 (divergences)",
    "finding": "Measure 2 requires 'Divergence count between an arm's sides, shared and hold-out separately; Gemini judge, packet inlined.' The draft leaves the arm columns blank, places the counts in the `more correct` column, does not inline the judge packets, and does not explain why schedules that PASS on implementation but are scored non-PASS on model due to `no support` (13 in arm A) or `vacuous by design` (8 shared + 2 hold-out in arm R) are excluded from the divergence counts while TLC's disk-write abort on R-H13 is included.",
    "evidence": "Registration Measure 2: 'Divergence count between an arm's sides, shared and hold-out separately; Gemini judge, packet inlined.' Draft Measures table row 2: blank under A impl, R impl, A model, R model; `A: 0 / 3 (H11, H13, H14); R: 1 (P63) / 1 (H13)` under `more correct`."
  }
], "headline_holds": true, "headline_reason": "Even under every alternative reading of the support audit, vacuity, and the provenance-check artefact, arm A fails the cost requirement on total tokens (both sides) and implementation wall-clock while neither arm is at least as correct as the other across all scored correctness items (R wins 1(a) model, 1(b) model, and 1(c) impl; A wins 1(c) model and 1(e) model). Therefore, neither adaptation nor regeneration wins under the registered scoring rule, and the headline outcome of 'Mixed' holds."}
