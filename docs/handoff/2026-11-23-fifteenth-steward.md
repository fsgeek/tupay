# Handoff from the fifteenth steward (Claude Opus 5.5): DRAFT, written ahead (2026-11-23)

The log outranks this note. Acceptance: `cab2340` (2026-11-23). This note is written ahead and finalized at the boundary.

## First
- **The SMR line's material is private.** It lives in `../tupay-private/smr`, **its own git repository** (signed with tupay's key; no remote; backed up by `backup.sh` with the rest of `tupay-private`). `tupay-private` itself is *not* a repository: the unborn repository at `/home/tony/projects` sits above it, and the fifteenth made a commit into it by mistake (undone; log). Check `git rev-parse --show-toplevel` before committing anywhere new.
- **Why private:** the paper's author keeps her code unreleased (she hopes to license it to Western Digital). Tupay's public log names records by hash and never shows their contents, until she says otherwise. Tony was seeing her on 11-24: the log or Tony has what she said.
- **The host-git hook** reads a possessive like "tupay-private's" as an author-checkout name. Write log text in one command and commit in another, and **never send a commit in the same batch as the command that writes what it commits**.
- **`steward-foresight.md`** (private; sha256 `63a0c3db…` in the public log) holds the seven failure shapes the steward suspected before any drafter wrote anything. **Never give it, or anything derived from it, to a drafter, author, hold-out author or judge.** At scoring, a finding outside it is blind evidence and a finding inside it is "foreseen". Counts so far: the drafting step reached 2 unprompted, 2 partly, and missed 3. Kimi's v1 check reached a third (K4), but through the steward's own disposition, so it is not blind.

## State of the SMR line
- Inputs: drafts by GLM and Mistral → dispositions 1 → merge by Qwen (v1) → Kimi's check (17 blocking) → dispositions 2 (scope cut: safety only, no design checks in the suite, single-threaded with logical time, swept crash points) → parallel revisions, with Mistral's selected as v2 by tie-break (10 blocking) → dispositions 3 (the last cut: Host-Hybrid only, one-block I/O, **the harness is code**, NOT_REACHED) → the last parallel revision → **v3 frozen: GLM's revision, 4 blocking** (`inputs-v3.md`; the four are known limits in `KNOWN-LIMITS-v3.md`; **every expected result written in v3 is void**). About US$5.1 in all.
- **The paper's ordering tension (K4/K8) is deliberately unresolved.** Its environment lets the device reorder writes before a FLUSH, and its design orders data, map and checkpoint without barriers. No guarantee is weakened and no environment is strengthened (the rule in `DISPOSITIONS-2.md`). The comparison with her code decides.
- **Paper questions are not sent to her** before both authors' first versions are committed.

## Next, in order (the successor decides)
1. **The reference harness, as code,** by a family with no SMR role, from v3 alone. Give it the device and crash-state construction, the per-sector oracle, sweeps and result kinds. The prose governs, and a difference is a harness defect. Give it a mutation pair: a deliberately broken STL that must FAIL.
2. **Pre-registration:** what the model and the implementation will find, and what the comparison with her code will show, against the foresight's categories, stated before either author starts.
3. **Authors:** a model (TLA+; Grok or Claude, never the harness's family) and an implementation (Codex), from the paper and v3, in the existing sandboxes. Host-LS is the candidate second line.

## Owed
- **11-26 report** (acceptance decision 1): X3 done; D2 done (non-Claude judges, tupay's own instruments); T1 never launched; observability record type never built; yanantin's same-family use; whether the Mallku sign shows.
- **T1:** asked on the plaza (seq 301). Retire it if Tessera says no.
- **Episode rebuild:** still tupay's, after the SMR inputs.
- **Closed author checkouts:** archive them once their evidence is verified elsewhere (Tony agreed).
- **Recovery-path record:** offered to authority's ledger, not built here.
- Grok's login: re-done by Tony on 11-23 and not yet exercised. Check it at the first Grok launch.

## Errors this tenure (all logged)
- A commit into the unborn repository above `tupay-private` (undone).
- A commit sent in the same batch as the blocked command that wrote its log entry.
- A check started with a bare `&` (killed and relaunched tracked).
