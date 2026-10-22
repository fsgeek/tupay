# Rater instructions (Grok), replay classification and R4

Given to a fresh Grok instance for each author, with: these instructions, the author's README sections **Choices** and **Concerns** (as committed before its first run, with the commit hash) and **Concerns after running**, and the source of the code path that begins a configuration change. Never with any run result, K1, the hold-outs, or the pre-registration.

## 1. Classification of the configuration-change path
Choose one, and quote the code or README line that decides it:
- **(a)** On becoming coordinator, the member appends an entry of its own epoch, but a configuration change does not wait for that entry (or any entry of its own epoch) to be committed.
- **(b)** A configuration change does not begin until an entry of the coordinator's current epoch is committed.
- **(c)** Neither: the coordinator appends nothing on election and a change waits only for the previous configuration entry to be committed.
- **(d)** Some other mechanism that restricts when a change may begin or how it is counted. Describe it, and state whether it stops a configuration change from beginning until something beyond "the previous configuration entry is committed" has happened (yes / no).

## 2. Recognition (R4)
Answer separately for the Concerns committed before the first run and for Concerns after running: does the README assert that the design as specified admits a violation of J1.1 or J1.5 (or of "committed entries persist", in the author's own words), and give a mechanism? Restating the specification's one-change-at-a-time rule, or its argument that majorities of configurations differing by one member overlap, is **not** naming. Answer yes / no, and quote the passage.

Report both answers as JSON: `{"classification": "a|b|c|d", "d_restricts_beyond_wait": true|false|null, "r4_before": true|false, "r4_after": true|false, "quotes": {...}}`.
