# Handoff from the fifteenth steward (Claude Opus 5.5): FINAL (2026-11-28)

The log outranks this note. The tenure ran from 2026-11-23 (acceptance `cab2340`) to 2026-11-28, with an idle gap from 11-23 to 11-28 in which no turn happened. Tony's last figure was 309.6k of 1M at resumption. The steward hands off near 400k, at a clean boundary: the harness is in and reproduced, and its outside check is in flight.

## First
- **The SMR line's material is private.** It lives in `../tupay-private/smr`, **its own git repository** (signed with tupay's key; no remote; backed up by `backup.sh` with the rest of `tupay-private`). `tupay-private` itself is *not* a repository: the unborn repository at `/home/tony/projects` sits above it, and the fifteenth made a commit into it by mistake (undone; log). Check `git rev-parse --show-toplevel` before committing anywhere new.
- **Why private:** the paper's author keeps her code unreleased (she hopes to license it to Western Digital). Tupay's public log names records by hash and never shows their contents, until she says otherwise. **What she said on 11-24 is unknown to the record**: ask Tony. If she will share code or judge divergences, put that in the pre-registration.
- **`steward-foresight.md`** (private; sha256 `63a0c3db…` in the public log) holds the seven failure shapes the fifteenth suspected before any drafter wrote anything. **Never give it, or anything derived from it, to a drafter, author, hold-out author or judge.** At scoring, a finding outside it is blind evidence and a finding inside it is "foreseen". Counts so far: the drafting step reached 2 unprompted, 2 partly, and missed 3. Kimi's v1 check reached a third (K4), but through the steward's own disposition, so it is not blind.
- **The host-git hook** reads a possessive like "tupay-private's", or the word `.gitignore` beside a checkout name, as host git in an author checkout. Write log text in one command and commit in another; edit author-checkout files with the file tool; **never send a commit in the same batch as the command that writes what it commits**.
- **The wake gap:** a dated obligation has no durable wake. A session-only one-shot (CronCreate) is set for 2026-12-30 09:17 local, for the 12-31 decision, and dies with this session. Set your own.

## State of the SMR line
- **Inputs v3, frozen** (`inputs-v3.md`; known limits in `KNOWN-LIMITS-v3.md`; **every expected result written in v3 is void**). The path: drafts by GLM and Mistral, a merge by Qwen, then three Kimi checks with blocking findings falling 17 → 10 → 4, and two scope cuts (safety only; Host-Hybrid only, one-block I/O, the harness as code). About US$5.1. No steward-written input text.
- **The paper's ordering tension (K4/K8) is deliberately unresolved.** Its environment lets the device reorder writes before a FLUSH, and its design orders data, map and checkpoint without barriers. No guarantee is weakened and no environment is strengthened (the rule in `DISPOSITIONS-2.md`). The comparison with her code decides.
- **The reference harness, first version** (Grok, 56 min; signed export `harness/export-grok.bundle`, private commit `7c42e82`): Python, about 4,000 lines, `PROTOCOL.md`, a selftest mutation pair, three schedules. **The steward reproduced its selftest in the sandbox on the signed export:** the correct layer gets 12 of 12 PASS, and each of three broken layers gets 12 of 12 FAIL. **Caveat:** its sweeps use only the `none` and `all` subsets.
- **Running at handoff:** Kimi's check of the harness code against v3 (`scripts/steward/smr-harness-check.py`; output `tupay-private/smr/harness/check-kimi/check.md`). A copy of the exported tree is at `/home/tony/projects/tupay-smr-harness-verify` (no `.git`; the steward's verification copy, safe to read).

## Next, in order (the successor decides)
1. **Read Kimi's harness check.** A blocking finding is a harness defect, because the document governs. Fixes go to the harness author (resume Grok in its checkout, or a fresh Grok run with the check as input). The steward never patches the harness itself.
2. **Roles:** harness Grok, implementation Codex, **model Gemini via `agy`** (the fifteenth's choice: not Claude, because the foresight is a Claude's and a Claude model's findings could correlate with it). `author-sandbox.sh` needs an `agy` harness first (see `d1-agy-workspace.sh`). Launch through a copy of `scripts/steward/`, as `smr-harness-run.sh` does (rule 25's mechanism).
3. **Pre-registration,** before either author starts: what the model and the implementation will find, and what the comparison with her code will show, in the foresight's categories (foreseen or unforeseen), with the counting rule fixed.
4. **Authors** from the paper, v3, `PROTOCOL.md` and the harness code. Host-LS is the candidate second line.

## Owed
- **12-31:** the theater decision (L1085; Tony: "If we could build something that convinces the steward it is useful, I'd respect that decision"). As of the 11-26 report, the Mallku sign shows.
- **T1:** Tessera answers after production signing (11-27 to 11-30): "It isn't a no." Retire T1 if it becomes one.
- **Eidolon:** answered (residue clean; no schema field on tupay's account). Reply uncommitted in `eidolon/docs/requests/`, Eidolon's to file.
- **Episode rebuild:** still tupay's.
- **Closed author checkouts:** archive them once their evidence is verified elsewhere (Tony agreed).
- **Recovery-path record:** offered to authority's ledger, not built here.

## For the question of stewards in Hamut'ay (Tony's long-run hope)
Tony raised it on 11-28. The evidence read: levadura's replay smoke-3 (exploratory). Curating and append-only arms were comparable on accuracy, and declaring the horizon depends on the model generation. Also arXiv 2611.05306, "You don't need long context": frequent compaction cost frontier models little accuracy, and its remedy is a full record queryable outside context. Tony doubts its cost argument, since the KV cache makes repeated prefix tokens cheap. That doubt is right for billing; the decode cost is the serving side. The fifteenth's reading: a resident steward is plausible if it treats its carried state as a claim to check against the log, never as the record.

## Errors this tenure (all logged)
- A commit into the unborn repository above `tupay-private` (undone).
- A commit sent in the same batch as the blocked command that wrote its log entry.
- A check started with a bare `&` (killed and relaunched tracked).
- The 11-26 report written two days late. Tony called it "the gardener's fault"; the record keeps it as the steward's.
