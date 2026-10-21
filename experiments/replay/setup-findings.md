# Replay setup findings

Kept apart from the registered outcomes (log, 2026-10-21, "correction … freeze criterion"). What building an honest test with knowing authors turned up, in order found. Each line names who found it and whether the finder knew the bug.

1. **G1.4 leak.** The failure model said "while an earlier change is in progress elsewhere". Found by the second steward (knew the bug) in its own draft; cut.
2. **F leak: "Nothing else restricts when a change may begin."** No source in D; forbade the gate that fixes the bug. Found by Gemini's fidelity check (knew the bug); cut.
3. **Leak in both arms: "any mechanism not described above."** No source in D; would forbid the same gate. Found by the third steward (knew the bug) on first reading; cut. The steward's first stated reason (that an appended no-op hides the bug) was wrong; corrected by ChatGPT via Tony (knew the bug).
4. **Arm asymmetry: D lacked Figure 3.1.** F had absorbed the figure's details; D's authors would have filled the gap from memory. Found by the third steward while tagging F; transcribed into D.
5. **Scenario defects.** S4 and S5 arm a step with `at: start` that can never fire; `coordinator` before any election is undefined; S8's comment contradicts its steps. Found by the third steward.
6. **Source fidelity is not neutrality.** A sourced statement can still raise the salience of what the bug depends on (F's bold on two properties; the quorum-intersection claim stated as a rule rather than argued). Raised by ChatGPT via Tony; checked in the F source audit.
7. **Grok's independence is of recall, not recognition.** The contamination probe asked a neutral question; it did not show Grok the design. Raised by ChatGPT via Tony; disclosed in the registration.

Pattern so far: three of the leaks were forbid-the-guard sentences, each without a source, each written by an author who knew the bug, and none found by the author who wrote it. Every one was found by a reader who also knew the bug. A reader who does not know the bug can check sources (the Grok audit) but not intent.
