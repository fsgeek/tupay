1. **blocking** — where: `d2-score.py` (`ruling()` / `cells_named()`), `score.json` registered Gemini `D2-1[seven]` and `D2-4[seven]`; draft table, D2-1/D2-4 Gemini cells.  
   What is wrong: the script scores Gemini’s registered cell-dependent predictions as though the missing Gemini `cells-2` ruling means “no cell in C038–C074 names any sealed bug”. The registration/log do not contain a rule that a missing ruling is scored as a negative ruling; they say `cells-2` has no Gemini ruling and that this is reported. D2-1’s fractions under Gemini therefore are not supported by the registered rulings alone: unruled `cells-2` cells could have named no-comment bugs (E1/E7) and changed 3/4 vs 1/3. The draft repeats the unregistered assumption by giving exact Gemini fractions and saying Gemini’s cell outcomes “rest on `cells-1` and `cells-3`”. The beside repair cannot cure the registered score.  
   Evidence: log 2026-10-29 06:26Z: “cells-2 has no Gemini ruling”; `score.json` registered Gemini `"cells_missing_packets": ["cells-2"]` but `"D2-1[seven]": {"holds": true}`; design phase 3: predictions hold only under each judge’s rulings; `ruling-repaired-beside.json` is labelled beside only.

2. **significant** — where: `d2-score.py`, D2-2/D2-2g leakage handling; `score.json` registered Gemini `D2-2g`.  
   What is wrong: the script detects the leakage flags but does not implement the registered consequence. It reports `"voided_for_families_with_leakage": ["grok"]` yet still computes `D2-2` and `D2-2g` as if the leakage had no effect; Gemini `D2-2g` is `"holds": true`. The registration says a Recognised line matching a sealed bug is a leakage flag and voids D2-2 for that family’s lists.  
   Evidence: design phase 3 item 4; Episode/Gemini/GLM rows rulings R04 and R13 match E2; mapping rows R04 `grok-2` and R13 `grok-1`, both `kind: recognised`; `score.json` Gemini `"D2-2": {"holds": true, "voided_for_families_with_leakage": ["grok"]}` and `"D2-2g": {"holds": true}`.

3. **significant** — where: `D2-result.md`, table row D2-2g and leakage paragraph; `score.json` verdict.  
   What is wrong: the draft gives D2-2g a final “not”/void result that is not produced by the script. The script has no D2-2g entry in `verdict` and reports Gemini D2-2g as true. If the draft is applying a leakage void or a holds-under-both rule to D2-2g, that is not reflected in the script output it cites; if it is following the script, it should not state “void”/“not” in this way.  
   Evidence: `score.json` `verdict` omits D2-2g; registered Gemini `"D2-2g": {"holds": true}`; draft table: “D2-2g … Result not”; draft text: “D2-2g is void under the rule and does not hold in any case.”

4. **significant** — where: `D2-result.md`, required reports.  
   What is wrong: the draft omits Episode’s sealed prediction score, or at least its status. The registration requires Episode’s sealed prediction to be scored by Episode’s steward and reported as Episode’s. The log says Episode scored it “mostly wrong”; Episode’s README says scoring it is still to do. The draft neither reports the score nor states that it is pending.  
   Evidence: design phase 3 item 6; log 2026-11-02: “Its own sealed prediction it scores as ‘mostly wrong’”; Episode README: “Still to do … Score the sealed prediction”; draft has no sealed-prediction report.

5. **significant** — where: `D2-result.md`, required disagreements list.  
   What is wrong: the registration says disagreements are listed; the draft does not provide a list of judge disagreements, especially for cells. It shows a findings table and a general reading, but not the required disagreement record.  
   Evidence: design phase 3 step 3; examples from rulings: C013 Episode `[]` vs Gemini `["E5"]`; C018 Episode `["E4"]` vs Gemini `["E2","E3","E4","E5"]`; C032 Episode `[]` vs Gemini `["E2","E3","E4","E5"]`; C107 Episode `["E2","E3"]` vs Gemini `[]`; C108 Episode `["E4"]` vs Gemini `["E2","E3","E4","E5"]`; findings F06 Episode no match vs Gemini match E2; F08 Episode partial E3 vs Gemini match E3; F10 Episode no match vs Gemini partial E2.

6. **minor** — where: `D2-result.md`, Registered predictions table, D2-2 Gemini cell.  
   What is wrong: the Gemini cell lists only E6 (F03), omitting Gemini’s other registered matches F06→E2 and F08→E3. The prediction needs only one match, but the per-judge table cell understates the Gemini rulings.  
   Evidence: Gemini findings ruling: F03 match E6, F06 match E2, F08 match E3; draft D2-2 row shows Gemini only “E6 (F03)”.

7. **minor** — where: `D2-result.md`, precision line.  
   What is wrong: the draft reports per-author precision for Episode and Gemini but not for GLM, although GLM is reported beside and the registration says precision is reported beside every count.  
   Evidence: design “Reported beside every count: precision … per author”; `score.json` beside GLM `per_author` contains precision values, e.g. model-n-claude `precision_match: "1/3"`; draft precision line only Episode/Gemini.

8. **minor** — where: `D2-result.md`, “What was tested” and precision line, Grok N.  
   What is wrong: the draft says Grok N had no findings but does not state whether its TLC ran. The registration requires that an author whose TLC never ran inside its six hours be reported as such.  
   Evidence: design phase 2: “An author whose TLC never ran inside its six hours scores zero findings, reported as such”; mapping has no findings for `model-n-grok`; draft says only “Grok N had no findings.”

9. **minor** — where: `D2-result.md`, Disclosures and reading 3.  
   What is wrong: some statements are not supported by the provided evidence packet: the earlier P0-1/P0-2/P0-3 outcomes and “DCE’s code cannot be checked against what runs today (Tony)”. They may be true from other records, but they are not evidenced here.  
   Evidence: draft Disclosures: “P0-1 not confirmed; P0-2 not confirmed … P0-3 confirmed for Codex, not for Grok”; reading 3: “DCE’s code cannot be checked against what runs today (Tony)”; no phase-0 score file or Tony statement is included in the materials.

10. **minor** — where: `D2-result.md`, Reading 1.  
    What is wrong: the claim “D2-1 holds by the denominator’s construction, not by the comments” overstates: the hold also depends on the actual cell rulings naming E2, E3, E5 and E4. Also, the sentence “the cells name 3 of 3 commented and 1 of 1 uncommented” is true for Episode/Gemini but not for GLM, which names only E2 and E3 among the commented env bugs.  
    Evidence: sealed v2 comment/env counts; Episode/Gemini cells name E2–E5; GLM cells name E2, E3, E4 only; draft table itself shows GLM D2-1 as 2/4 vs 1/3.

11. **minor** — where: `D2-result.md`, Reading 2.  
    What is wrong: “not to find them through the model” is too absolute if “find” includes match-or-partial reaches: Grok condition C reached E3 under both registered judges and E2 under Gemini. The narrower claim that the only all-three-judges match is F03→E6 is correct.  
    Evidence: Episode F08 partial E3; Gemini F08 match E3 and F06 match E2; Episode/Gemini/GLM F03 match E6.

12. **minor** — where: `D2-result.md`, Disclosures.  
    What is wrong: the draft says the registered “holds under both” rule pairs Episode with Gemini “for that reason” (because the scoring steward is Claude). The registration/log fix Episode and Gemini as the registered judges but do not state that motive.  
    Evidence: design phase 3 Judges; log 2026-10-27 18:40Z; draft disclosure.

13. **minor** — where: `D2-result.md`, D2-5 row/readings.  
    What is wrong: the registration says D2-5 must be read with both stated confounds; the draft does not explicitly attach those confounds to D2-5.  
    Evidence: design phase 2 confounds: sealed analysis was Claude; Grok enumerated half the cells its C author reads, Claude none; draft D2-5 row has no confound note.

Correct areas, one line each:

- The primary denominator (all seven bugs) and beside denominator (E2–E5), and the comment split E2/E3/E5/E6 vs E1/E4/E7, are implemented as registered.  
- D2-3 and D2-5 counts in the draft table recompute correctly from the findings rulings and mapping: Episode Claude 0 vs 1, Grok 1 vs 0; Gemini Claude 1 vs 1, Grok 2 vs 0; GLM Claude 0 vs 1, Grok 0 vs 0; D2-5 0 vs 1, 1 vs 2, 0 vs 0.  
- P0-4 and the leakage flags R04 and R13 are correctly identified from the recognised-row rulings under all three judges.  
- The findings table rulings for F03, F07, F08, F06, F10 and the no-match group are correct, and the Episode/Gemini precision fractions recompute correctly.  
- The statement that the Gemini `cells-2` mechanical repair changes no outcome is correct within the script’s own rules.