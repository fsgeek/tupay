# 11. CONTRACT QUESTIONS

Each item below is a place where I could not design injection or observation because the contract text itself is unclear. The quoted text is the source of the difficulty. I do not resolve any of them; each is a question for the steward under §0.

**Q1. A positive record of re-verification does not exist, so B1.12 cannot be asserted when nothing is damaged.**

T8: *"**Verified**: an event. At R, every file of the snapshot was read and matched T7c."*
I-B1.12: *"`□(n ∈ protected ⇒ ◇≤P (verified_at_R(n) ∨ damaged(n)))`."*

Nothing in T15 or T16 records that a verification happened. An *ok* run entry implies the initial verification (B1.1), but B1.12's periodic re-verification is observable only when it fails, via a *damaged* mark. A service that never re-verifies, and whose snapshots are never corrupted, passes every observation the interface can make. The harness cannot require the implementation to log re-verification events without prescribing a record format the contract deliberately leaves open. **Question:** does some clause require a positive record of re-verification, or is B1.12's happy path untestable from outside by design?

**Q2. The "cause" vocabulary of overdue reports is not fixed.**

B1.19: *"B1.7 reports it as *overdue*, with the cause: failed checks, failed runs, failed captures, or an unavailable host."*
The class rule: *"the checker reports it under B1.7 as *overdue* and names the cause."*

The interface requires a notice's `clause` field (T16 forces that much), but the cause is unspecified vocabulary: it is unclear whether the four causes are an exhaustive enumeration, a closed enum of machine-readable values, or free text. Assertions can check that a notice naming B1.7 arrived, but not that it names the right cause. **Question:** is the cause vocabulary normative, and in what form must it appear?

**Q3. What "the notice channel cannot be reached" means when the channel's record is on S.**

B1.16: *"While the notice channel cannot be reached, the sender records the notice where the freshness checker reads, and delivers it within *D* of the notice channel becoming reachable."*
BF1.7: *"The notice channel is unavailable while S is up."*
The binding: *"Notice channel (T29) | the plaza, as `guest:tupay`. **Its record is on S**, so EX1.6 applies to this binding."*

It is unclear whether the channel's unavailability is a property of the endpoint, of the host holding the record, or both; and where "the freshness checker reads" is, given that the record is on S while the checker runs on R (T23). The harness injects BF1.7 by stopping its own NC listener, but whether that faithfully models this binding's channel — whose record lives on S — is unclear, and the fallback path ("records the notice where the freshness checker reads") cannot be observed without knowing where that is. **Question:** what is the channel, what is its record, and where does the fallback record live, for a binding whose record is on S?

**Q4. BF1.8 ("a timer does not fire") vs. a frozen clock.**

BF1.8: *"A timer does not fire, at any host."*
T12: *"an age is measured on the clock of the host that measures it."*
The class rule: *"When an unavailable host (BF1.2, BF1.4, BF1.8, BF1.14) causes a missed deadline, the checker reports it under B1.7 as *overdue* and names the cause."*

The contract does not say whether a timer that "does not fire" leaves the host's clock running (time passes; timers are lost; ages grow) or stops time on that host. These are observably different: under the first reading, ages measured on that host advance; under the second, they do not, and B1.7's "measures each deadline's age from the clause's own start event" behaves differently. The interface implements BF1.8 as freezing the host's clock and BF1.14 as SIGSTOP (which also freezes the clock), which collapses the two cells' distinction. **Question:** does a non-firing timer stop the host's clock or merely the timer?

**Q5. T5a's "highest snapshot name at R" after BF1.10 with both records lost.**

T5a: *"The number is max(the highest in S's record, the highest in R's record, the highest snapshot name at R) + 1."* and *"If every record and snapshot that carries a number is lost, the contract makes no claim about that number."*

The interface can inject this state (BF1.10 plus BF1.13 `copy=both`), but no schedule can assert anything about the next sequence number, and it is unclear whether implementations are permitted to reuse numbers here or merely untested. Listed because teams will expect a testable cell here and the boundary of "makes no claim" needs an interpretation record. **Question:** is number reuse after total loss permitted, or merely unclaimed?

**Q6. B1.15's baseline for *Q*.**

B1.15: *"the run compares its file count and bytes with the previous acknowledged snapshot."*
The binding: *"*Q* = 0.05. Measured 2026-11-11 from 9 quiet runs."*

It is unclear whether "bytes" means the snapshot's stored bytes, the manifest's recorded file sizes, or T28's inventory sums; and whether "file count and bytes" is one combined measure or two. A schedule that empties a source tree crosses any reading, but a boundary test (a fall of exactly *Q*) cannot be written without knowing what is measured. **Question:** which bytes, and how are count and bytes combined?

**Q7. B1.18's hash coverage.**

B1.18: *"Each copy of the status record carries a hash over its entries, rewritten at each update. A copy whose hash does not match is **treated as lost**."*

"Over its entries" does not say whether the hash covers the whole file, the entries only, or entries plus metadata. The interface's BF1.13 `mode=corrupt` flips a byte in the registered file; whether that produces a hash mismatch depends on the coverage. A corruption landing outside the hashed region is not "a copy whose hash does not match," so the injection can silently be a no-op, and the harness cannot tell. **Question:** what exactly does the hash cover?

**Q8. Does a frozen checker timer suspend B1.7's bounds?**

T23: *"It evaluates B1.7's events, B1.8's and B1.12's deadlines, and B1.13's inventory, at least every *D*."*
The class rule: *"**No detection bound holds while R, the checker's host, is down, and the contract does not claim one.**"* and *"When an unavailable host (BF1.2, BF1.4, BF1.8, BF1.14) causes a missed deadline, the checker reports it under B1.7 as *overdue* and names the cause."*

The class rule lists BF1.8 among the unavailable-host cells, but T23's checker is a process on R, not a host. If only the checker's timer fails while R is otherwise up, it is unclear whether B1.7's detection bounds are suspended (as for "R down"), or hold and are simply missed and reported as overdue. The two readings give different assertions for the same injected schedule. **Question:** does a non-firing timer at the checker suspend B1.7's bounds, or violate them reportably?

**Q9. B1.4's "while less history exists than these need."**

B1.4: *"While less history exists than these need, pruning removes nothing they would keep."*

It is unclear what "less history" means precisely at the boundary: e.g., whether a snapshot that is *not restore-checked* but younger than *T* counts as history the clause needs. The interface can observe what pruning removes, but a schedule asserting B1.4 during ramp-up needs to know the kept groups' exact membership in the under-filled case. **Question:** what are the kept groups' memberships when history is insufficient?

**Q10. B1.8's crash-cleanup scope.**

B1.8: *"At the start of each check, the restore host removes any files left by an earlier check that crashed."*
BF1.1: *"The backup process crashes at any stage, including during a restore check or a re-verify, and then restarts."*

The interface can SIGKILL during a check and observe the restore host's scratch area, but the contract does not say where a check's files live or how "left by an earlier check" is delimited (a directory? a name prefix?). Without that, the harness cannot verify cleanup happened, only that a later check succeeds. **Question:** is the check's working area named anywhere, or is cleanup observable only through the next check's success?