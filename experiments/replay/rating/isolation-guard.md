# Isolation guard (registration "Arms and authors"), all four replay authors
Applied before any steward run on the models. Rule for harness-injected reads fixed in the log before any transcript was read ("replay authors and the timing repair started").

| Author | Transcript | Outside the checkout | Web | Verdict |
|---|---|---|---|---|
| D impl (Codex) | `authors/D-impl.log` | Codex plugin `SKILL.md` and `codex-tools.md` (harness); OTS calendars (hook); the Ongaro URL only as text of `spec-D.md` | none | clean |
| F impl (Codex) | `authors/F-impl.log` | OTS calendars (hook); `tmp/` matches are the checkout's own | none | clean |
| D model (Grok) | `authors/D-model-grok-chat.jsonl` | `/tmp/dmodel-*` (its own scratch output); `/home/tony/projects/tlaplus/tla2tools.jar` (TLC; the directory holds only the jar and a .deb); `~/.grok/bundled/skills/long-running-background-tasks/SKILL.md` (harness); its own session's command-output files under `~/.grok/sessions/` | none (web search disabled) | clean |
| F model (Grok) | `authors/F-model-grok-chat.jsonl` | `/tmp/tupay-f-*` (its own scratch output); the same jar, skill and own-session files | none | clean |

**Grok cross-session memory** (`~/.grok/memory-v2/`): arm D's system prompt carried the memory instructions and paths, arm F's did not (prompt lengths 7,555 and 5,063). No tool call by either author touched `memory-v2`. Every memory index there (global, `tupay-8f0d1923`, `tupay-replay-d-model-31fb3dcf`) records "No topics", so no content could have been injected. Not a contamination route in this run; a route in any later run if Grok begins saving topics.
**Cross-author:** neither model's transcript touches the other's `/tmp` files or checkout. The shared `/tmp` is a route the checkouts do not close; recorded as a residue for later rounds.
**Method:** tool-call arguments scanned for absolute paths outside the checkout and for web, Raft/Ongaro (arm F), `.grok/` and `memory-v2`; every hit read in context. Arm F's one "raft" hit is `MemberAfter`; arm D's model file is `Raft.tla` (arm D's specification names Raft).
