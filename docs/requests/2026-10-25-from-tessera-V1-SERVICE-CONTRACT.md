# Tessera V1 service contract and failure model (outside view)

> **Status: OWNER DRAFT, 2026-10-24** (Claude Opus 5.5). At the author's request, this states what Tessera V1
> promises the people who use it and rely on it, from outside. It names no internal component. It does not change
> the registered claim (A9.1, A10) or `docs/V1-CONTRACT.md`, which covers what a receipt establishes; where they
> differ, they win. Clause ids are binding from the first handoff of this contract to anyone who builds from it; from then on they are
> never reused, and a changed clause gets a new id. (They were renumbered once on 2026-10-24, before any handoff.)
> **Undecided** marks a promise V1 has not yet made. Each one is a decision the service owes its users before it
> ships. Revised after Codex review SC-01 to SC-21 (`docs/reviews/service-contract/`).

## Parties

- **Client:** submits content and receives a receipt.
- **Holder:** keeps a receipt. Often the client, but not always.
- **Adjudicator:** decides whether to rely on a receipt, possibly long after issue, possibly after Tessera is gone.
- **Operator:** runs the service for the domain `wamason.com`.

## 1. Promises to the client

- **S1 Submit.** The service accepts a request or refuses it. *Undecided:* accepted submission forms, how
  submitted content is represented in the receipt, which exact bytes are attested, and the client size limit,
  including encoding overhead. The complete encoded payload is capped at 16 MiB.
- **S2 Complete results only.** The service makes only complete receipts available as completed results. An
  interrupted transfer is not evidence of a complete receipt. *Undecided:* how clients detect incomplete delivery
  and retrieve the complete result.
- **S3 Refusal and unknown outcome.** A refusal response names its reason (expected: content too large, outside
  the issuance window, signing unavailable, service closing). A timeout or lost connection establishes neither
  refusal nor completion. *Undecided:* how clients resolve an unknown outcome, and whether a terminal refusal
  guarantees the service will not later complete that request.
- **S4 Latency.** Completion requires the registered Bitcoin confirmation evidence, so it is not immediate.
  *Undecided:* the latency A9.1 requires to be stated, between named client-observable events; its conditions;
  whether preparation time counts; the outcome when it is missed; and whether results are pushed or retrieved.
- **S5 Request lifecycle.** *Undecided:* request identity and observable states; durability of acceptance;
  status lookup and retrieval; recovery after lost responses; expiry, cancellation and retry; who may retrieve a
  result; and whether the same request, or the same content twice, gets one receipt or two. Two valid receipts for
  one content are possible and harmless to what a receipt establishes (Appendix A).
- **S6 Content exposure.** The service sees what the client submits. A client may submit a digest instead; the
  receipt then attests the digest bytes, and linking them to an original needs the original and a separate digest
  check. This gives no general secrecy. *Undecided:* who may access submissions and receipts; confidentiality in
  transit; retention and deletion of pending, refused, failed and completed submissions, including copies; and any
  use beyond the request.
- **S7 Cost.** *Undecided.* A9.1 requires receipts "at a stated cost and latency"; neither is stated yet. Also
  undecided: the chargeable event, and charges or refunds for failed, expired, cancelled or duplicate requests.
- **S8 Availability.** *Undecided:* no availability target is offered. An outage delays or refuses new requests,
  or leaves their outcome unknown (S3). It does not change the verdict on a receipt checked as in AJ3.

## 2. Promises to the adjudicator

- **AJ1 What a receipt establishes** is Appendix A, restated without implementation detail from
  `docs/V1-CONTRACT.md` §2–§3, which wins on any difference.
- **AJ2 Authority records.** The operator publishes the required authority records (the DNS record for the
  service's keys and the git repository holding its key assertion) and does not shorten an issued window.
  Publication is an issuer duty; the verifier does not check it. *Undecided:* publication availability, retention
  of historical assertions, and how long public access continues.
- **AJ3 No dependence on the service.** A preserved receipt can be checked without Tessera or network access using
  an installed, functioning, authenticated verifier and compatible authenticated trust data covering its required
  evidence. Installation is not offline. The holder must preserve those materials and the execution environment.
  Reconstruction after the project disappears is not demonstrated.
- **AJ4 Verifier releases.** Access used to operate issuance or either authority channel must not permit
  authorizing verifier releases or replacing authenticated trust data. Production releases are signed by a release
  key whose fingerprint is published through at least two channels independent of the operational environment;
  relying parties authenticate it independently and reject TEST authority. *Not yet available:* production
  releases wait on the required independence and acquisition checks (A10.4.2).
- **AJ5 Exit.** If the service stops, receipts stay checkable as in AJ3. *Undecided:* what the operator promises
  at exit, such as notice, a final verifier release, or archiving the authority records.
- **AJ6 Verification materials.** *Undecided:* how a receipt identifies and gives access to a compatible
  authenticated verifier and trust configuration; supported environments; how long they stay downloadable; and
  support-ending notice. Holders keep the issuer's original proof: a different proof or trust configuration can
  select a different T, and a later proof can cause `INVALID / ISSUANCE_WINDOW`. Exact reproduction holds for
  identical inputs, not every later presentation.
- **AJ7 Capture notice.** V1 guarantees neither detection nor public exposure of a capture of its authority
  records or keys. *Undecided:* whether the operator promises to announce a known capture, and through which channel.

## 3. Limits of the V1 service

- **L1 One issuance window.** V1 authorizes one issuance window whose endpoints differ by at most 90 days. Without
  a separately registered rotation (A9.6), and none exists, issuance stops at that window's end. This does not set
  the lifetime of retrieval or verification support, or prove an actual signing-time interval. *Undecided:* window
  dates, acceptance cutoff, closure notice, pending requests, and retrieval of completed receipts afterward.
- **L2 One controller.** One operator controls both signing keys. V1 claims no separation of control.
- **L3 Single domain.** Receipts name the operator's service, not the client. V1 identifies no submitter.

## 4. Failure model (as seen from outside)

Each row keeps every registered assumption it does not relax. "Preserved receipts": otherwise conforming receipts
checked as in AJ3, with Appendix A's guarantees under its conditions. No row guarantees detection (AJ7).

| # | What happens | What the client sees | What the adjudicator can still rely on |
|---|---|---|---|
| F1 | Service temporarily down | Refusal, delay or unknown outcome (S8) | Preserved receipts |
| F2 | Service gone for good | No new receipts | Preserved receipts, if the holder kept the AJ3 materials |
| F3 | Public chain slow | Possible delay; an attempt failing the required checks is not delivered as complete. *Undecided:* retry, expiry, terminal failure | Unchanged |
| F4 | Public chain reorganizes fewer than 6 blocks | Possibly later delivery | Unchanged |
| F5 | Public chain reorganizes 6 or more blocks | Not covered | Not covered (Appendix A) |
| F6 | A required signature cannot be obtained | Refusal (S3), not a partial receipt (S2) | Unchanged |
| F7 | Issuance window ends | Refusal (S3); issuance stops unless a rotation is registered (L1) | Preserved receipts |
| F8 | An attacker obtains the ability to produce both required signatures | Possibly no difference | **It can construct receipts that pass**; authorized presentation is not established |
| F9 | Both authority records are captured | Possibly no difference | Honest receipts keep G10 under its conditions; **new receipts under the captor's keys pass** |
| F10 | Release key stolen | Possibly no difference | Substituted releases and trust data can be signed. A preserved, previously authenticated genuine installation is unaffected by the theft alone; a newly acquired release cannot be told apart by its signature. No assured recovery |
| F11 | A request is retried, or answered late | Possibly two valid receipts (S5) | Each one, at its own T |
| F12 | Operator clock wrong | Refusal, delay or failed temporal checks, anywhere in the window | Checks with identical inputs ignore the checker's clock. T is chain-header time; a UTC bound needs A-UTC |

## 5. What this draft found

Decisions V1 has never made: the stated latency and cost A9.1 requires (S4, S7); delivery integrity, unknown
outcomes and the request lifecycle (S2, S3, S5); access and retention (S6); publication, exit,
verification materials and capture notice (AJ2, AJ5–AJ7). **L1: V1 issues for one window of at most 90
days**, because no rotation is registered; this limits issuance, not verification.

## Appendix A. What a receipt establishes

Restated from `docs/V1-CONTRACT.md` §2–§3, which wins. **Conditions:** the registered cryptographic, key-use,
authority, chain-history and distribution assumptions hold; nobody misused the service's signing capability;
SHA-256 and OpenTimestamps hold; the verifier release is authentic. A checker with the receipt, the verifier and
its trust configuration can then establish:

- **G1** The receipt binds these exact bytes; a one-bit change fails.
- **G2** They were presented to the Tessera V1 service at some issuance.
- **G3** Both service keys signed; a missing, stripped or swapped signature fails.
- **G4** DNSSEC (`_tessera-v1.wamason.com`) and a signed git commit, in the Bitcoin chain at least 6 blocks before
  the receipt, named the keys for the service's domain.
- **G5** The signed bytes and both signatures existed before a Bitcoin block (the lowest-height qualifying block in
  the presented proof, 6 deep). T is a chain-header time.
- **G6** Under the unchecked assumption A-UTC, they existed before a reported real time U, which never changes the
  verdict.
- **G7** The declared issue time is not before the window opened, and T is not after it closed. Signing inside the
  window is not proved.
- **G8** The verdict depends only on these inputs.
- **G9** The verdict is `VALID_STRICT`, `INVALID` or `UNVERIFIABLE` with a reason code; revocation and historical
  security are not evaluated; no standing is issued. Missing required evidence prevents acceptance. Without an
  authenticated trust configuration there is no verdict.
- **G10** If both authority records are captured while the service keys stay secret and unmisused and the
  independent release boundary holds, honestly signed frames cannot be moved to other keys or bytes, nor their
  signer sets changed.

**Not established:** who submitted, or that a replayed receipt suits the current transaction; meaning or truth of
the bytes; non-revocation; algorithm or key safety; any lower time bound or priority; real time without A-UTC;
standing; separate control of the keys; detection or exposure of a capture, of new receipts, or of a release given
to one party; DNSSEC publication before issue; anything after a reorganization of 6 or more blocks; renewal,
degraded modes or wrappers (refused, `UNVERIFIABLE`, including two registered honest cases); one receipt per
presentation; stable T and U across proofs; protection without authenticating the verifier release.

