# The contract channel between tupay and its adversarial customer

Written by tupay's eleventh steward, 2026-11-06. This file fixes **only** the channel: what may cross, in what form, and where. It says nothing about the adversary's role, aims or judging; those are written by Tony or by the adversary itself, never by tupay.

## Where
- **Adversary to tupay:** `tupay/docs/adversary/inbox/`. The adversary writes here, and tupay's steward commits it unchanged (the commit's stamp is the receipt).
- **Tupay to adversary:** `tupay/docs/adversary/outbox/`. The adversary reads only this directory and `inbox/`. Nothing else in tupay is addressed to it.
Nothing else crosses: no code, models, tests' bodies, logs, transcripts or steward notes, in either direction. The plaza may carry a one-line pointer to a new file, and nothing more.

## What may cross (file names begin with the UTC date)
1. **Contract** (adversary): `YYYY-MM-DD-contract-vN.md`. A service contract and a failure model, each clause and cell with an id that is never reused. Versions are new files; none is edited in place.
2. **Acceptance tests, sealed** (adversary): `YYYY-MM-DD-tests-vN.sha256`. The hash of a test suite the adversary holds. The suite crosses only when tupay's first versions for that contract version are committed, and is checked against the hash.
3. **Change notice** (adversary): `YYYY-MM-DD-change-N.md`. Which contract version it supersedes, which ids are retired or added, and the time it takes effect. It may come at any time the adversary chooses.
4. **Clarification question** (tupay): `YYYY-MM-DD-question-N.md`. One question about the meaning of named clause ids. It may not propose wording, an easier reading or a relaxation.
5. **Clarification answer** (adversary): `YYYY-MM-DD-answer-N.md`. It binds as if it were part of the contract version it names.
6. **Delivery** (tupay): `YYYY-MM-DD-delivery-N.md`. Which contract version a build claims to meet, its commit hash, and how to run it against the sealed tests. The build itself is published in tupay's repository; the adversary may run it but never reads its source unless the contract version says it may.
7. **Verdict** (adversary): `YYYY-MM-DD-verdict-N.md`. The sealed tests' results against a delivery, and the suite itself, checked against its hash.

## Rules for tupay
- tupay never negotiates a contract: no counter-proposals, and no "would you accept".
- A question that the steward thinks reveals tupay's design is not asked; the steward records in tupay's log that it was withheld.
- Before each launch the steward tells Tony which model families it plans to use; Tony answers only "conflict" or "fine". The log records that the check was made, not the adversary's family.

## Amendment 1 (twelfth steward, 2026-11-07, 23:01Z)
Item 5's "binds as if it were part of the contract version it names" let a clarification change a contract without a new version (the review of the controlled-language reply, relayed by Tony, 2026-11-07). It is replaced as follows:
- An **answer** may only choose among readings the contract version already permits. It names the readings it chose between and the reading it chose.
- An answer that narrows, widens, adds or removes any obligation is a **change notice**, under item 3: a new contract version, with retired and added ids.
- The asker may contest an answer's classification. A contested answer is treated as a change notice.
- The question, every reading it named and the answer stay in the record. None is edited.
- Correction (23:03Z): the review cited in amendment 1 was written by ChatGPT and relayed by Tony.
