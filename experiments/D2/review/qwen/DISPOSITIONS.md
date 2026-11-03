# Dispositions of Qwen's review of D2's scoring (2026-11-03)

Reviewer `qwen/qwen3.8-max-prime`, one call, packet 248,575 characters (sha256 prefix `d27233d23831399f`), US$0.89. Thirteen findings. **All accepted**: 1 to 8 in full, and 9 to 13 in full as wording changes. The scorer is corrected in place (git keeps v1; v1's output stays as `score/score.json`, v2's is `score/score-v2.json`), and the draft becomes draft 2.

1. **Blocking, accepted.** v1 scored Gemini's missing `cells-2` ruling as "names nothing", a rule the registration does not contain. v2 tries every set of bugs `cells-2` might have named. **D2-4** holds under Gemini whatever `cells-2` says, since more naming only raises the count. **D2-1 is undetermined under Gemini** (unruled cells could name E1, E4 or E7), so **D2-1 no longer holds under both**. This changes the registered result.
2. **Significant, accepted.** The leakage void was reported but not applied. v2 applies it under the widest reading: it removes every condition C author (their inputs include Grok's enumerations) and Grok's own authors. The registration's wording ("that family's lists" / "enumerations") does not fix which findings it removes. This reading was chosen after the outcome was seen, and is stated as such. D2-2 holds under it and under both narrower readings, because F03 is Claude N's.
3. **Significant, accepted.** D2-2g is now in the verdict: **void** under both judges (its authors are all removed by the void).
4. **Significant, accepted.** The draft now reports the status of Episode's sealed prediction. Episode's reply calls it "mostly wrong" in prose, and its README lists the formal score as still to do.
5. **Significant, accepted.** The disagreements are listed (v2 output, `disagreements`), and the draft gives the registered ones.
6. **Minor, accepted.** The D2-2 row shows Gemini's three matches.
7. **Minor, accepted.** GLM's precision is added beside.
8. **Minor, accepted.** Grok N's TLC did run: 16 TLC output files in its frozen tree, and a commit "record TLC checks". It pre-registered "0 schema findings, 1 honest-environment failure". The draft says so.
9. **Minor, accepted.** The P0 outcomes and Tony's statement now cite the log entries they come from.
10. **Minor, accepted.** Reading 1 is narrowed: the env4 counts are Episode's and Gemini's, and GLM's differ.
11. **Minor, accepted.** Reading 2 is narrowed: Grok C reached E3 under both registered judges, so "not found through the model" was too strong.
12. **Minor, accepted.** The unstated motive for the judge pairing is removed.
13. **Minor, accepted.** D2-5 now carries the design's two confounds.
