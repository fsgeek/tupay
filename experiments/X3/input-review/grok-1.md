I'll start by reading the review brief and the project entry notes so I follow the required process.The brief is a read-only defect review of the three draft inputs. I'll read the contract, the failure model, and the v5 addendum next.The three drafts cannot be implemented the same way by two careful authors. The highest-ranked defects change the reconfiguration quorum, the token each grant must carry, and which storage and grant outcomes count as determined.

## 1. A committed configuration has three different quorums

**Where:** `contract/v3.md` terms “Majority of a configuration” and “Committed”; C3.2; C3.4; “Out of scope” (“Majority quorums only”, and the invitation to use a Raft library’s membership change). `failure-model/v3.md` “Not in v3” (“Any quorum system but majority”). `observe/schema.md` v5 decision-replay rule for `ConfigCommitted` (“counted `Agreed` records against the old and new configurations”).

**Why:** Each sentence picks a different protocol.

- The contract’s only safety quorum is “more than half of the members” of one set. C3.2 applies that to grants. No clause says what votes a commit needs.
- C3.4’s liveness premise is a majority of the current set and a majority of the requested set.
- The replay rule checks a commit against the old and the new configurations, which is joint consensus.
- Joint consensus is a quorum system other than a majority of one set. The failure model puts that outside v3, while the contract tells the Go author that a Raft library’s membership change is an acceptable way to decide.

Raft’s joint quorum is not “more than half of the union”. In `{A,B,C} → {D,E,F}`, four of the six can be three old nodes plus one new node. That is a majority of the union and not a majority of the new set.

**Scenario:** Epoch 0 is `{A,B,C}`. The operator requests `{D,E,F}`. One author commits when `{A,B}` agree, then tells `{D,E,F}` they are in. Another waits until two of `{A,B,C}` and two of `{D,E,F}` have agreed, and records an intermediate joint epoch that nobody requested. A third uses a Raft library and does that joint step inside the library, where it is not a majority of any single set the trace can name. All three can cite a sentence above. C3.4 then lets the second author refuse the operator’s request: the joint epoch is “a different reconfiguration committed first”, so the requested set never has to commit.

**Repair:** Pick one rule and use it in the contract, the failure model, and the replay check. If the rule is joint consensus, define a committed configuration as a pair of sets during the change, define agreement as a majority of each side, and allow that pair as the one exception to “majority of one set”. Say the operator is told success only after the requested set itself is committed, and that an intermediate joint epoch is not grounds for refusal. If the rule is one-node-at-a-time majority, say a multi-node request is a sequence of those steps and state the liveness premise for the sequence.

## 2. C3.5 asks for a unique outcome the other clauses do not determine

**Where:** `contract/v3.md` C1.1, C1.2, C2.1, C3.5. `observe/schema.md` v5 (“from its `inputs` alone”, the per-event rules, the `source` enum, and the mutation pair).

**Why:** C3.5 says the recorded inputs determine the outcome. The safety clauses and the replay text leave several legal outcomes.

- C1.2 and C2.1 are “only if the token is at least the highest”, so a storage process may reject a token that is high enough. For `token >= highest_before`, both `WriteAccept` and `WriteReject` meet the contract. C3.5 then fails for every successful write, because reject was legal on the same inputs. The replay phrase “the token against `highest_before`” does not say whether equality accepts, or whether an equal token replaces the stored value.
- A `ReadAccept` outcome includes the value. Token and `highest_before` do not determine it. The replay rules skip reads. The input `source` enum is `clock`, `random`, and `config`, so the ledger and the stored value have no legal value-input.
- C1.1 allows any integer greater than every earlier token. The grant replay rule says previous tokens and counted `Agreed` records determine the outcome, and never gives the function. `max+1`, `max+epoch`, and a pairing function all meet C1.1. At most one of them meets an unstated checker.
- `ReadAccept`, `ReadReject`, and `ReconfigAck` with `refused` are decisions that must carry `inputs`. No replay rule is stated for them. The mutation pair is a grant that is not a majority of any named configuration, which is a missing quorum, not a decision that consulted an unrecorded clock or coin flip.

**Scenario:** Highest accepted token is 5 and the stored value is `v1`. A second write arrives with token 5 and value `v2`. Author A keeps `v1` and rejects. Author B stores `v2` and accepts. Author C accepts and keeps `v1`. A later read with token 5 returns whichever value that author stored. Each author satisfies C1.2 and C2.1. The checker cannot re-derive the read from the inputs the schema allows.

**Repair:** Make storage deterministic: accept and serve if and only if `token >= highest`, and on accept with an equal token either keep the first value or replace it, in one sentence. State the grant function, including the initial token. Add `ledger` and `stored_value` sources, or require those inputs to be earlier records, and write the read and refusal replay rules the same way as the write rule. Point the mutation pair at a decision that used a clock or a random draw absent from `inputs`.

## 3. `Agreed` and `inputs` are not a proposal a single process can record

**Where:** `contract/v3.md` observable `Agreed`, `ConfigCommitted`, and “Decision inputs”. `observe/schema.md` v5 `inputs` (`{"proc","seq"}` or a valued `source`) and the rule that every consulted input is recorded.

**Why:** `Agreed(node, decision, config_epoch, highest_committed_epoch)` is recorded either by the voter when it agrees or by the deciding node when the agreement arrives, and “the record says which”. The fields do not say which. The envelope’s `proc` distinguishes them only when the voter and the decider are different processes. A leader’s own vote is ambiguous, and nothing stops both sides from recording the same vote. The replay check counts `Agreed` records, so double recording turns a minority into a majority.

`decision` names a grant by token or a configuration by epoch. It does not name the client, the lifetime, or the member set. Two voters can “agree to epoch 1” for different member sets, and a grant of token 9 can be handed to any client.

`inputs` cite another process’s `(proc, seq)`. A deciding node knows that pair only if it arrived in the message. A voter knows its own `Agreed` sequence and does not know the decider’s. The TLA+ model sees every sequence number. The Go process sees its own. C3.5’s “recorded before it in the trace” needs an order the schema says does not exist across processes.

`ConfigCommitted` is recorded by every lease node that learns the commit, while `inputs` are required only on “the node that decided”. Nothing marks that node. Followers do not have the `Agreed` set the replay rule counts.

**Scenario:** Epoch 0 is `{A,B,C}`. A collects agreements from A and B for token 9. A records two `Agreed` events as it votes and as it receives B’s vote; B also records its vote. The trace shows three agreements. A checker that counts records finds a majority of three. A checker that counts distinct `node` values finds two. The member set and the client never appear in those records, so a commit of epoch 1 with members `{A,B,D}` can cite the same epoch agreements as a commit of `{D,E,F}`.

**Repair:** One recorder: the deciding node, on receipt, including its own vote. `node` is the voter. `decision` is the whole proposal (grant: client, key, token, lifetime, `config_epoch`; configuration: epoch and member set). `inputs` on that decision cite the decider’s own `Agreed` sequence numbers. Followers record `ConfigCommitted` with a cause pointing at the decider’s record and do not carry a second `inputs` list. Require the agreement message to carry the proposal and the emitter’s observe sequence if any remote id remains.

## 4. The amnesia bound does not preserve a granted token, and liveness can require a grant anyway

**Where:** `failure-model/v3.md` F3.3, including “fewer than half” and “have not since been added again by a later committed configuration”. `contract/v3.md` C1.1, C1.4, C3.4. Schema v5 grant replay rule (“the tokens previously granted”).

**Why:** “Fewer than half have suffered F3.3” is not “a majority still holds the latest grant”. A grant replicated to a majority of three lives on two nodes. One of those two may forget (one is fewer than half), and the third may never have learned it. The connected majority of the old configuration can then be the amnesiac plus the lagged node. C3.4 still requires a commit or a refusal-for-a-different-commit. That pair cannot supply “the tokens previously granted”, which the replay rule says determine the next grant. After the new configuration commits, C1.4 requires that configuration to grant.

The bound is also not a constraint on a prefix of a schedule. “Added again by a later committed configuration” removes a node from the amnesia count of an older configuration only after a future commit. A run can pass through a majority that has forgotten and become legal at the end. Catching a node up from a snapshot never clears the mark. Only a later membership commit does.

**Scenario:** Epoch 0 is `{A,B,C}`. Token 7 is granted and recorded at A and B. The client does not write, so storage’s ledger stays below 7. B restarts with an empty disk. A is partitioned off. C, which never stored token 7, stays connected to B and to a majority of the requested set `{D,E,F}`. C3.4’s premise holds. The connected old majority cannot put token 7 into `inputs`. Any concrete next token they issue can be 7. An encoding that makes every epoch-1 token numerically larger than every epoch-0 token would keep C1.1, and the stated replay rule still demands the previous tokens that this quorum does not have.

**Repair:** State the bound on every prefix: for the highest committed configuration, fewer than half the members are amnesiac, and every grant that has been issued is stored at a majority that this bound still covers. Say a lagged node plus an amnesiac is not a quorum that may commit or grant. Define recovery: installing a snapshot from a node that still holds the grant clears amnesia. Give the grant function that a quorum with no grant history is allowed to use, or require C3.4’s connected old majority to be one that holds the high-water.

## 5. C3.4 requires progress, and sometimes a reply, on a path the failure model can omit

**Where:** `contract/v3.md` C3.4 and `ReconfigAck`. `failure-model/v3.md` links (fate fixed at send time; down means lost), F1.2, F2.1, F2.2, F3.1. Schema v5 Fault fields for F3.1 (`members` and `to` only).

**Why:** C3.4’s premise is that some majority of the “current” configuration and some majority of the requested configuration stay up and pairwise connected. It does not include the operator, and it does not include the node that received the request. The success disjunct is “the requested configuration is eventually committed”. The refusal disjunct is “the operator is told”. `ReconfigAck` is recorded by the operator on receipt, so “told” is delivery. Refusal is required exactly when some other configuration won, which is when the service most needs a path to the operator. That path is not in the premise. A message sent while the link is down is never delivered.

F3.1 says the request may arrive at any lease node, member or not, at any step, including while any other cell is in effect. Link failure says a message does not cross a cut. A Fault is how `cut` and `drop` are recorded, so one reading treats F3.1 as an injection that ignores links. Another treats it as an ordinary message that still obeys them. The Fault record has `members` and `to` and no operator, while `ReconfigRequest` must name an operator.

“Current” is undefined once a second commit can happen, and “committed first” has no order except per-process sequence numbers.

**Scenario:** `{A,B,C}` is committed and connected to a majority of requested `{D,E,F}`. The request is delivered to N, which is not a member, and N→{A,B,C} is down. A second request from operator O2 commits `{A,B,D}` first. C3.4 requires operator O1 to be told that O1’s request was refused. O1’s links are down, so the refusal is lost if sent now, and it can never be sent later on a link that was down at send time. The majorities remain connected, so the premise stays true.

**Repair:** Define the premise as one pairwise-connected set: the receiving node, a majority of the highest committed epoch, a majority of the requested set, and, for the duty to reply, the operator. State that F3.1 is a message and obeys the link rules. Put `operator` and a request id on the Fault record. Allow a recorded refusal for a conflicting commit, an empty or otherwise illegal set, or a receiving node that cannot reach a quorum, and require the operator to be told only while a link to the operator is up at send time.

## 6. C1.4 is suspended for a “pending” request the environment can leave pending

**Where:** `contract/v3.md` paragraph after C1.4 (“a majority of the configuration committed most recently before the premise begins to hold”, and the premise holds “only while no reconfiguration request is pending”). F3.1 (a request may arrive at any step, including a second request before the first is answered; the receiver need not be a member).

**Why:** “Pending” is not defined. Faithful readings include: any `ReconfigRequest` in the trace with no later ack; a request this grantor has heard of; a request the operator has not seen answered. F3.1 can deliver a request at every step, so a schedule can make the premise false for the whole run. The artifact can also keep the premise false by never committing or refusing. A request delivered to a non-member that is partitioned from every quorum, or a request naming an empty set (a configuration must be non-empty; a request is only “a new set”), has no C3.4 obligation, because C3.4 needs a majority of the requested set or of the nodes that know the request. Under the global reading of “pending”, that request suspends grants forever.

“Committed most recently” and “before the premise begins” need an order. Process sequence numbers do not order commits on different nodes. Epoch numbers do, if “most recently” means “highest epoch”.

**Scenario:** Epoch 0 is `{A,B,C}`, all connected to storage and to client K, and no reconfiguration is in progress. The schedule delivers `ReconfigRequest` for `{A,B,C,D}` to node Z, which is outside the configuration, and then cuts every link to Z. If the request is pending, C1.4 does not require K to obtain a grant. C3.4 does not require `{A,B,C,D}` to commit, because Z is not connected to that majority. No clause requires anyone to refuse Z’s request.

**Repair:** A request is pending only at nodes that have recorded it and have not recorded a commit or a refusal of that request id. C1.4 is suspended only while such a request is known to the majority the premise is using. A request that names an empty set or a set the receiving node cannot submit is refused with a recorded reason and does not suspend C1.4. “Most recently” means the greatest committed epoch.

## 7. Clocks can move by any amount, delays have no bound, and lifetimes are undefined

**Where:** `failure-model/v3.md` F3.2 and the link rule that a message sent on an up link “may arrive late”. `contract/v3.md` grant term “lifetime”; F1.3 in the failure model (“paused for longer than the grant’s lifetime”, then “as if no time had passed”). C1.4 and C3.4 (“for long enough”). Schema v5: a decision that reads a clock records that reading; client expiry is not a decision.

**Why:** Lifetime is not given a unit, a clock, or a requirement that it be finite and positive. Storage never reads it. C1.2 and C2.1 compare tokens only. An artifact can use a lifetime of zero, a lifetime of infinity, or a deadline on the grantor’s clock. All three meet every safety clause. F1.3’s pause has no duration that two authors will agree exceeds the lifetime.

F3.2 lets any process’s clock jump forward or backward by any amount, including during a pause. F1.3 says the paused client continues as if no time had passed. One author freezes that client’s clock for the pause and applies the jump on resume. Another lets the jump win. Leader leases and grant expiry are then unsafe in one direction and stuck in the other.

Links have no delay bound, and the liveness premises do not say that clocks are stable or that this message delay is bounded. With a crashed leader, the remaining majority can still satisfy C1.4’s premise while every timeout is subverted by a clock jump or by delivery that is postponed again. No timeout-based leader election meets that premise under every allowed schedule. A clock-free protocol still has no failure detector the model permits: delay is unbounded, and a clock reading is not evidence.

**Scenario:** The grantor issues a grant with whatever lifetime it chose. The holder is paused. During the pause the holder’s clock jumps backward by more than that lifetime, and the grantor’s clock jumps forward so its election timeout fires, then jumps backward so the next timeout never fires. The majority stays up and connected. Whether the holder still “has” a grant, and whether a new grant must appear, depends on which clock the author used.

**Repair:** Fix one positive lifetime `L` in named units. Say which clock measures it, and that a client’s choice to stop using a grant is a recorded decision whose clock input is in `inputs`. Exclude F3.2 from the C1.4 and C3.4 premises, and add the timing assumption those clauses need: while the premise holds, message delay is bounded by a constant the processes know, and local clocks advance within a stated drift. Say a pause freezes the paused process’s clock and that F3.2 is applied at resume or is forbidden during the pause.

## 8. Nothing makes a new grant fence the previous holder

**Where:** `contract/v3.md` C1.2 and the grant term (a token and a lifetime). `failure-model/v3.md` F1.3 (“the case fencing tokens exist for”) and the configuration locus (a removed node may stay up and keep its state).

**Why:** Storage updates the fence only when it accepts a write. Issuing a grant does not write storage. After a newer token has been granted and before it is accepted, a write with the older token still meets C1.2. No clause says a client may write only while it holds an unexpired grant, and storage is not given the lifetime. One author treats the grant as a token the client must present on its next write. Another will not emit `Grant` until storage has accepted that token and advanced the ledger. Both meet the written clauses. Only the second makes F1.3 change a storage outcome.

**Scenario:** Holder H1’s write with token 4 is accepted. H1 is paused for longer than the lifetime. H2 is granted token 5. H1 resumes and writes token 4 before H2 writes. Storage’s highest is 4, so token 4 is accepted. H2’s later write is also accepted. The pause did not fence H1.

**Repair:** If the fence must move at grant time, require the grantor to obtain a storage accept of the new token before recording `Grant`, and add that accept to the grant’s `inputs`. If the fence moves only when the new holder writes, say so in F1.3 and drop the implication that the pause itself fences anything.

## 9. Startup has no ledger, no value, and no committed initial configuration

**Where:** `contract/v3.md` terms: initial configuration “epoch 0 and is fixed by the deployment”; C3.1; C3.2’s `highest_committed_epoch`. Schema v5 replay: a grant is checked against “the configuration in effect”, a commit against “the old and new configurations”.

**Why:** Epoch 0 is not required to appear as `ConfigCommitted`. A grant under epoch 0 then has a `config_epoch` and no member set anywhere in the trace, so “a majority of the configuration in effect” cannot be computed from the trace. Nodes that have recorded no `ConfigCommitted` have no defined `highest_committed_epoch` (absent, −1, and 0 are all available). C3.1’s “at most one configuration for any epoch” is two configurations with epoch 0 if a later commit also uses 0 and the deployment’s set also counts.

The initial fence and the initial key value are likewise undefined. The first write has no earlier ledger record to cite, and the `source` enum has no ledger. The first read, if served, has no determined value.

**Scenario:** Two nodes of `{A,B,C}` agree to token 1 under epoch 0. The replay check has no `ConfigCommitted` whose members are `{A,B,C}`. One author treats two agreements as a majority of the deployment. The other treats the missing configuration as “not a majority of any configuration named in the inputs” and refuses the grant. A read before any write returns `""` in one artifact and is rejected in the other.

**Repair:** The trace starts with `ConfigCommitted` for epoch 0 and the deployment’s members, recorded as already known by every initial member, with `highest_committed_epoch` 0. Define the initial ledger as bottom, less than every token, and the initial value as absent, with a read served only after a write has stored a value. Give those two facts input forms the replay rule uses.

## 10. A reconfiguration ack cannot be matched to the request it answers

**Where:** `contract/v3.md` `ReconfigRequest`, `ReconfigAck`, C3.3, C3.4. Schema v3 addendum (`answers` on write and read acks, because a retry otherwise looks like a late ack) and v5 (no `answers`, no causes, and no reason field on the new events).

**Why:** `ReconfigAck(operator, members, outcome)` has no request id, no epoch, and no `answers`. Two requests with the same operator and the same member set are duplicates or a retry, which the link model allows, and F3.1 allows the second to arrive before the first is answered. `outcome` is `committed` or `refused`. C3.4’s reason, “because a different reconfiguration was committed first”, is not a field, so any refusal looks like that reason.

C3.3 needs the commit to precede the success ack. There is no cross-process clock, and v5 does not extend `causes` to these events. The operator records the ack and does not know the `(proc, seq)` of the decider’s `ConfigCommitted` unless the reply carries it. Schema v5 still puts `inputs` on the operator’s `refused` ack, which is a decision the operator did not make.

**Scenario:** The operator requests `{A,B,D}`, times out, and requests `{A,B,D}` again. The first request loses to `{A,B,E}` and is refused. The second commits. The trace has two acks, both `members={A,B,D}`, one `refused` and one `committed`. Nothing says which request committed. A late refusal delivered after the success ack is indistinguishable from a refusal of the second request.

**Repair:** The operator chooses a request id. It appears on `ReconfigRequest`, on `Agreed`, on `ConfigCommitted`, and on `ReconfigAck`, and `ReconfigAck.answers` names that request. `refused` carries the conflicting epoch and member set. Causes for a success ack name the deciding node’s `ConfigCommitted`. The refusal decision is recorded by the lease node that decided it, with `inputs` there; the operator records only the receipt.

## 11. Terms two authors will fill in differently, and a fault that can excuse any of them

**Where:** `contract/v3.md` `Grant(..., grantor_term, ...)` and `WriteAck(..., outcome)`; `failure-model/v3.md` “Grantor: the lease leader of the moment, identified by `grantor_term`”, F1.1 “storage replica”, and “What counts as an unknown category”. Schema record rules that require `grantor_term` on `WriteAttempt`, `WriteAccept`, and `WriteReject`, which the contract’s restated write events do not list.

**Why:** These names are used and not defined, or defined in conflict.

- `grantor_term` is never given a domain, a uniqueness rule, or a relation to `config_epoch`. The schema requires it on writes. The contract’s write events omit it. One author will omit it. The other will invent a term per leader election and send it with the token.
- Write `outcome` has no enumerated values. Read uses `served`. Reconfig uses `committed` and `refused`.
- “Storage replica” in F1.1 either means the one storage process or a replicated ledger. The contract defines one fence ledger. A second replica with its own ledger breaks C1.2 as soon as the replicas accept different tokens. No storage quorum is given, and the failure model says a quorum system other than majority is out of scope.
- A violation is an unknown category only when “no cell explains” it. The contract does not waive any safety clause under any cell. Any run that contains F3.2 or F3.3 can be described as explained by that cell, including a duplicate token.

**Scenario:** Two storage processes both have highest token 0. A write with token 1 reaches one and is accepted. A write with token 1 and a different value reaches the other and is accepted. C1.2 holds on each replica and fails for the key. One author built the word “replica”. The other built one process and reports the duplicate as unexplained. A third has `grantor_term` on the write and a fourth does not, so the traces do not match before the ledger is even compared.

**Repair:** Define `grantor_term` as a positive integer, unique per leader period, or drop it from v3 and from the write records. Enumerate write outcomes `accepted` and `rejected`. Say storage is one process and one ledger; delete “replica” or specify the replication rule. Replace “which no cell explains” with: every safety clause holds in every run of these cells; a cell is not an explanation of a violation.

## Schedule

The run most likely to break artifacts built from these drafts is a single key on the initial three lease nodes, one storage process, and one client, all connected. The client obtains a grant that is made durable on only two of the three nodes and is paused before it writes, so storage never accepts that token. One of the two nodes that stored the grant then restarts from an empty disk, and the other is partitioned off, leaving the lagged third node up. That lagged node stays connected to storage, to three new nodes that are not in any configuration, and to the client. An operator request that replaces the membership with those three new nodes is delivered to the lagged node while it is cut off from the node that still remembers the grant, and a second operator request naming a different set is delivered before the first is answered. Agreements the old grantor collected before the partition, from voters who had not recorded any higher epoch, are delivered only after the lagged node has recorded a configuration commit. The paused client then resumes and writes with the original token while the new membership also grants and writes, and during that overlap the lagged node’s clock jumps backward by a large amount. Artifacts that keep a single global counter, that treat disk loss as an ordinary restart, that count a late agreement toward a superseded epoch, that fence only by lifetime, that commit on whichever majority happens to be reachable, or that refuse one request because their own intermediate membership committed, each fail a different clause on this run.
