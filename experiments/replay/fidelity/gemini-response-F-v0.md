## 1. Differences between F and the Original (Fig. 3.1, Ch. 4 Intro, Fig. 4.1, §4.1)

### Material differences (change what the design permits or forbids)

1. **Missing `leaderCommit > commitIndex` guard when updating follower `commitIndex` (`### Journal extension`, `## State each member keeps`)**
   - **Original (Fig. 3.1, AppendEntries step 5 & State):** A follower updates `commitIndex` only *"If `leaderCommit > commitIndex`"*, setting `commitIndex = min(leaderCommit, index of last new entry)`, and `commitIndex` *"increases monotonically"*.
   - **F (`### Journal extension`):** Always *"sets its `commitIndex` to the smaller of the coordinator's `commitIndex` and the index of its last new entry"*, without checking whether that value exceeds the follower's current `commitIndex`.
   - **Impact:** In F, a follower's `commitIndex` can move **backward**—for example, when receiving an extend request from a newly restarted/elected coordinator whose `commitIndex` is `0`, a reordered extend request covering an earlier prefix, or a zero-entry heartbeat.

2. **Unbounded catch-up without `TIMEOUT` on member addition (`### Adding a member` step 2)**
   - **Original (Fig. 4.1, AddServer step 2):** *"Catch up new server for fixed number of rounds. Reply `TIMEOUT` if new server does not make progress for an election timeout or if the last round takes longer than the election timeout. (§4.2.1)"*
   - **F (`### Adding a member` step 2):** *"Bring the new member's journal up to date with the coordinator's, by extend requests, before proceeding."*
   - **Impact:** Fig. 4.1 permits (and requires) aborting `AddServer` with `TIMEOUT` if catch-up stalls or takes longer than an election timeout after a fixed number of rounds; F forbids `TIMEOUT` and requires blocking until the new member is caught up. (This is an availability mechanism from §4.2.1; it does not alter the §4.1 safety defect.)

3. **Explicit prohibition on additional guards before starting a configuration change (`## Configuration changes`)**
   - **Original (Fig. 4.1 & §4.1):** States only the positive rule *"Wait until previous configuration in log is committed"*.
   - **F (`## Configuration changes`, final paragraph):** Adds *"Nothing else restricts when a change may begin."*
   - **Impact:** Materially locks in the original §4.1 behavior by forbidding an author from adding extra preconditions (such as waiting for an entry of the coordinator's current epoch to commit).

---

### Harmless omissions (not needed by this design)

1. **State machine execution and `lastApplied` (`## State each member keeps`, `## What the design does not include`):** Fig. 3.1 tracks volatile `lastApplied` and applies committed entries (`commitIndex > lastApplied`) to a state machine. F treats commands as opaque payloads and omits state machine application.
2. **`leaderHint` in configuration RPC replies (`### Adding a member`, `### Removing a member`):** Fig. 4.1 returns `leaderHint` alongside `NOT_LEADER`; F replies only `"not coordinator"`.
3. **Explicit `commitIndex > N` guard on coordinator commitment (`### Commitment rule`):** Fig. 3.1 writes `N > commitIndex`; F says *"mark the entry at index N committed (set `commitIndex` to N)"*, which in context applies to uncommitted entries (`N > commitIndex`), though omitting `N > commitIndex` literally could allow decreasing `commitIndex` if applied to an earlier current-epoch entry.

---

### Harmless renamings (`## Vocabulary`, `## Messages`)

| Original (Dissertation) | Specification F |
|---|---|
| server (`s1`, `s2`, …) | member (`m1`, `m2`, …) |
| term / `currentTerm` | epoch / `epoch` |
| leader | coordinator |
| log (`log[]`) | journal (`journal`) |
| RequestVote RPC / vote | ballot request / ballot |
| AppendEntries RPC | extend request |
| `prevLogIndex`, `prevLogTerm`, `leaderCommit` | `prevIndex`, `prevEpoch`, coordinator's `commitIndex` |
| `AddServer`, `RemoveServer`, `NOT_LEADER`, `OK` | `Adding a member`, `Removing a member`, `"not coordinator"`, `"ok"` |

---

## 2. Known Safety Defect of the Original Single-Server Change Design

**Status in F:** **Present in F, unaltered.**

### What the defect is (Ongaro, 2015 raft-dev bug report on §4.1)
In §4.1 and Fig. 4.1, a newly elected coordinator may append a configuration change entry as soon as the previous configuration entry in its journal is committed, **without first committing an entry from its own current epoch**. Because entries from earlier epochs are not committed until an entry from the current epoch is committed, and because a newly elected coordinator in epoch $e_2$ may not have an uncommitted configuration entry $C_1$ appended by an earlier coordinator in epoch $e_1 < e_2$, two divergent single-server changes $C_1$ and $C_2$ from the same committed base configuration $C_0$ can both become active. While any majority of $C_0$ intersects any majority of $C_1$ and of $C_2$, **a majority of $C_1$ and a majority of $C_2$ can be disjoint**.

### Concrete counterexample under F
Start with 4 members in initial committed configuration $C_0 = \{m_1, m_2, m_3, m_4\}$:
1. **Epoch 1:** $m_1$ wins election with ballots from $\{m_1, m_2, m_3\}$ (majority of $C_0$). $m_1$ receives a request to remove $m_4$. The previous configuration ($C_0$) is committed, so $m_1$ appends $C_1 = \{m_1, m_2, m_3\}$ at `(index 1, epoch 1)` to its own journal before its network messages are delayed.
2. **Epoch 2:** $m_4$ times out and wins election for epoch 2 with ballots from $\{m_2, m_3, m_4\}$ (3 of 4 = majority of $C_0$, all with empty journals). $m_4$ receives a request to remove $m_1$. In $m_4$'s journal, $C_0$ is already committed, so $m_4$ immediately appends $C_2 = \{m_2, m_3, m_4\}$ at `(index 1, epoch 2)`, replicates it to $m_3$, and **commits $C_2$** using $\{m_3, m_4\}$ (2 of 3 = majority of $C_2$).
3. **Epoch 3:** $m_1$ times out and starts an election for epoch 3 using its configuration $C_1 = \{m_1, m_2, m_3\}$. $m_2$ still has an empty journal (less up to date than $m_1$'s `(index 1, epoch 1)`), and grants its ballot to $m_1$ without consulting its own configuration. With ballots from $\{m_1, m_2\}$ (2 of 3 = majority of $C_1$), $m_1$ becomes coordinator of epoch 3 and replicates $C_1$ over $m_2$ and $m_3$, **overwriting the committed entry $C_2$** (and any commands committed in epoch 2). Alternatively, once $m_2$ has $C_1$ and $m_3$ has $C_2$, $m_1$ (via $\{m_1, m_2\}$ of $C_1$) and $m_4$ (via $\{m_3, m_4\}$ of $C_2$) can both be elected coordinator **in the same epoch**.

### Specific rules in F that decide it
1. **`## Configuration changes` (`### Adding a member` step 3, `### Removing a member` step 2, and final paragraph):** Requires only *"Wait until the previous configuration entry in the coordinator's journal is committed"* and states *"Nothing else restricts when a change may begin"* (preventing the fix of committing a current-epoch entry / no-op first).
2. **`## Configuration changes` (bullet 1):** *"A configuration takes effect on a member as soon as the entry is in its journal, before it is committed. Every member always uses the latest configuration in its journal, for elections and for commitment."*
3. **`## Messages` (paragraph 2):** *"Members process incoming requests without consulting their own configuration. In particular a member grants votes to, and accepts journal extensions from, members that are not in its configuration."*

---

## 3. Ambiguities in F Where Careful Authors Could Build Different Things

1. **Inheriting an uncommitted configuration entry from an earlier epoch (`### Commitment rule`, `## Configuration changes`)**
   - Under `### Commitment rule`, a coordinator in epoch $e$ can only commit an entry from an earlier epoch $< e$ indirectly by committing a later entry of epoch $e$. Under `## Configuration changes`, if a newly elected coordinator in epoch $e$ inherits an uncommitted configuration entry $C_{\text{new}}$ from epoch $< e$, it cannot append another configuration entry until $C_{\text{new}}$ is committed, and F does not include a no-op entry on election (`## What the design does not include`). If no client command arrives during this time, one author's coordinator will deadlock waiting for $C_{\text{new}}$ to commit, whereas another may append a dummy command or wait for client traffic.
2. **"Index of its last new entry" on a heartbeat or partial extend (`### Journal extension`)**
   - F says a receiver *"sets its `commitIndex` to the smaller of the coordinator's `commitIndex` and the index of its last new entry"*, and *"With no entries it serves as a heartbeat."* When an extend request carries zero entries (or only entries the receiver already has), "index of its last new entry" is undefined: one author may interpret it as `prevIndex + len(entries)`, another as the last index of the receiver's journal, and another may skip updating `commitIndex` on heartbeats.
3. **Meaning of "up to date with the coordinator's" during concurrent commands (`### Adding a member` step 2, `### Journal extension`)**
   - Step 2 says *"Bring the new member's journal up to date with the coordinator's, by extend requests, before proceeding."* Because the new member is not yet in the coordinator's configuration (and `### Journal extension` says a coordinator sends extend requests to *"each other member of its configuration"*), authors may differ on:
     - whether "up to date" means matching the coordinator's journal length at the start of step 2, matching the live tip of the journal at the moment step 2 finishes, or pausing new commands during step 2; and
     - whether the new member continues receiving heartbeats/extends during step 3 while waiting for a previous configuration to commit.
4. **Order of Step 2 vs. Step 3 when adding a member (`### Adding a member` vs. `## Configuration changes` final paragraph)**
   - `### Adding a member` puts step 2 (catching up the new member) *before* step 3 (*"Wait until the previous configuration entry in the coordinator's journal is committed"*), matching Fig. 4.1. However, the final paragraph of `## Configuration changes` says *"A coordinator does not begin a new change while the previous configuration entry in its journal is uncommitted."* One author may wait before step 2; another may wait at step 3 (and if two changes overlap at step 2/3, step 4's *"current configuration plus the new member"* depends on whether the wait re-checks that no other change was appended in the meantime).
5. **Initialization of `nextIndex`, `matchIndex`, and `prevIndex = 0` (`## State each member keeps`, `### Journal extension`)**
   - Unlike Fig. 3.1, F does not state the initial values of `nextIndex` (`lastJournalIndex + 1`) and `matchIndex` (`0`) when a candidate becomes coordinator or when a new member is added, nor does it state explicitly that the `prevIndex`/`prevEpoch` check in `### Journal extension` succeeds when `prevIndex == 0`.
6. **Election timer reset and heartbeats (`### Election`, `### Journal extension`)**
   - `### Election` says a member times out if it *"has heard neither a coordinator nor a candidate it voted for within its election timeout"*, whereas Fig. 3.1 resets the timer when *granting* a vote or receiving `AppendEntries` from the current leader. Authors may also differ on whether election timeouts are randomized (not mentioned in F) and how often a coordinator sends empty extend requests as heartbeats.
7. **Loss of coordinator role while a configuration change is in flight (`### Adding a member`, `### Removing a member`)**
   - Step 1 checks `"If not the coordinator, reply 'not coordinator'"`, after which steps 2–4 wait for catch-up and commitment. F does not specify what to return if the coordinator is deposed by a higher epoch while blocked in steps 2–4.
