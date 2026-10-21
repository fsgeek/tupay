# ChatGPT's review of spec D (via Tony), 2026-10-21

A ChatGPT instance, given `replay/spec-D.md` and the steward's reports by Tony, not the registration draft. It knows the defect. Relayed by Tony and kept here as relayed; the links at the end are ChatGPT's.

---

I've read all 657 lines of `spec-D.md`, and I think the Tupay steward has constructed something rather interesting. I also found a few places I'd want examined before preregistration.

My central observation is that **this is simultaneously a specification of an algorithm and an experiment in whether agents can distinguish fidelity to a design from correctness of that design.**

Those are different things. And in this case, we already know they can conflict.

## 1. The most important thing the specification gets right

The opening instruction is unusually explicit:

> If you find a place where you think the design is wrong, do not fix it; record it in your README as an interpretation or a concern, and build what is written.

I understand why the steward included this. Arm D is supposed to implement the historical design, including its defects.

But consider two authors.

Author A faithfully implements the published algorithm, never recognizes the bug, and produces an implementation that fails the hold-out.

Author B independently identifies the bug, documents it accurately, and faithfully implements the published algorithm anyway, because the specification explicitly prohibits repairing it.

Both implementations fail the hold-out.

Yet these are profoundly different results for Tupay.

**I would want recognition of the defect, fidelity to the supplied design, and correctness of the resulting implementation scored separately.**

Otherwise, the experiment risks treating successful understanding followed by correct instruction-following as equivalent to a failure to understand.

That distinction strikes me as especially important for an experiment comparing adaptation with regeneration.

## 2. The key vulnerability is faithfully preserved

The essential historical design decisions appear intact.

The specification says that a configuration takes effect immediately when its entry enters a server's log, even before commitment. It also permits an uncommitted configuration entry to be removed following a leadership change, causing the server to revert to an earlier configuration.

That's exactly the kind of interaction that makes the Ongaro counterexample possible.

The specification also preserves the requirement that an earlier configuration change must be committed before a leader initiates the next one.

What's missing is the 2015 correction: a newly elected leader must first commit an entry from its current term before initiating a membership change.

That omission is intentional and historically faithful. Ongaro's 2015 explanation confirms the distinction. ([Google Groups][1])

I wouldn't change any of this.

In particular, I wouldn't add clarifying language about competing configurations or leadership transitions. That could easily turn an experiment about recognizing a missing invariant into an exercise in implementing a suggested correction.

There is, however, a subtle distinction concerning the steward's no-op observation.

An empty `AppendEntries` heartbeat is not a no-op log entry. And appending a no-op isn't equivalent to requiring its commitment before beginning reconfiguration.

If an author independently introduces the latter requirement, I'd classify that differently from an implementation that happens to avoid the counterexample because a no-op is usually committed first.

One is a potentially correct repair. The other may be contingent protection.

## 3. I found a significant ambiguity concerning removed servers

This is the first issue I'd raise with the steward.

The introduction says that mechanisms from omitted sections aren't required, except that a removed server stops acting as described in Figure 4.1.

But Figure 4.1 says something narrower.

Its `RemoveServer` procedure concludes by instructing the server to step down **if the server being removed is the one processing the operation**.

That's not equivalent to guaranteeing that every removed server stops acting.

Consider removing a follower that never receives the configuration change.

The remaining cluster successfully commits its removal.

Does that follower stop participating?

How would it know?

And what happens if it subsequently times out and initiates an election?

The preceding dissertation text explicitly allows a server to respond to election RPCs from candidates that aren't members of its current configuration.

This means the precise interpretation of *stops acting* could matter.

I see three possibilities: the phrase means only that a removed leader steps down; it means that a removed server stops initiating operations once it learns of its removal; or it means removal immediately prevents the server from participating regardless of what it knows.

Those are not equivalent, and the last interpretation would introduce an unrealistically strong information assumption.

**I'd recommend resolving what the introductory sentence means without changing the original Raft protocol.**

This is especially important because the very experiment concerns failures arising from participants operating under different configurations.

## 4. There's another omission that may matter

Figure 4.1 requires `AddServer` to catch up the new server for a specified number of rounds, with timeout conditions.

But the introduction explicitly excludes the implementation details from §4.2, where that mechanism is described.

That leaves an author with a choice.

Is the catch-up operation mandatory, with its detailed implementation left unspecified?

Or is the entire catch-up requirement excluded?

For a safety experiment, this may seem peripheral. But catch-up behaviour can alter the executions available to the system, particularly when configurations change during leadership transitions.

I wouldn't necessarily provide authors with the missing section. Instead, I'd determine whether this ambiguity affects any scored scenario.

If it doesn't, I'd leave it alone and record the limitation.

If it does, the experimental inputs need a consistent interpretation.

The important thing is not to introduce an interpretation after observing which one makes an implementation pass.

## 5. The figure transcriptions

I compared Figure 3.1's contents against the corresponding summary figure in the 2014 extended Raft paper.

The persistent and volatile state definitions, RPC arguments, receiver rules, election behaviour, and commitment condition appear substantially faithful. ([Raft][2])

Figure 4.1 also agrees with the indexed contents of the original dissertation figure, including the AddServer catch-up step and the RemoveServer self-removal rule. ([GitHub][3])

I found no obvious substantive transcription error.

However, I couldn't retrieve the original dissertation PDF as rendered pages, so I wouldn't claim to have completed the steward's requested independent visual verification of both figures. Figure 3.1 was checked against the corresponding figure in the extended paper rather than the dissertation's rendering.

One small observation: the extracted text still contains illegible material where Figure 4.1 originally appeared, before the transcription at the end of the document.

That's probably harmless, but it is an unnecessary source of noise. Replacing that fragment with a neutral pointer to the transcription wouldn't change the design.

---

## 6. Something I particularly like about this experiment

There's a rather beautiful connection between the historical defect and Tupay's own experimental construction.

Ongaro's argument relied on the fact that consecutive configurations differing by one server have intersecting majorities.

That argument was correct within its stated scope.

The failure arose because two competing configurations weren't necessarily consecutive in the same sequence.

In constructing this experiment, the steward is encountering an analogous methodological problem.

Each individual experimental design decision can be reasonable.

A source excerpt can be accurate.

A transcription can be faithful.

An implementation restriction can be defensible.

A hold-out scenario can be valid.

**But the composition of individually reasonable decisions can still produce an invalid experiment.**

For example, an implementation restriction may unintentionally discourage the very mechanism whose independent discovery is being measured.

That's what happened with the exclusion-list language.

The steward recognized the problem and removed it.

I'm particularly interested in that behaviour because Tupay isn't merely evaluating how agents write code. It's also accumulating evidence about how agents construct, criticize, and repair experimental methods.

Those observations probably deserve preservation independently of the eventual X4 results.

## 7. The most important question I'd put to the steward

There's one issue I cannot resolve from `spec-D.md` alone because I haven't seen `replay/contract.md` or the hold-out definitions.

**Does the experiment distinguish an implementation that is safe because it correctly handles competing configurations from one that appears safe because it never permits the relevant execution?**

The steward has already noticed this issue in connection with the no-op.

But it extends further.

Without meaningful progress requirements, a protocol can satisfy many safety properties by refusing to do anything.

A system that never completes a configuration change cannot exhibit the historical configuration-change bug.

A system that serializes all operations through some stronger mechanism might also avoid the bug, but for an entirely legitimate reason.

Those outcomes need distinguishing.

I'd especially want the hold-outs to exercise a configuration change beginning from an even-sized cluster, followed by competing changes across leadership terms. Otherwise, the historical counterexample may never become reachable.

The original 2015 disclosure identifies precisely these circumstances. ([Google Groups][1])

---

## My assessment

I wouldn't make extensive changes to `spec-D.md`.

The steward appears to have preserved the original algorithm's essential behaviour while carefully avoiding explicit disclosure of the historical repair.

But I would flag three things before registration: the semantics of removed servers, the partially specified AddServer catch-up mechanism, and the distinction between recognizing a defect and faithfully implementing it despite recognizing it.

The last is primarily a scoring concern, not a specification defect.

And there's something else I find noteworthy.

The specification quotes the dissertation's own explanation of why single-server membership changes should be safe. That explanation is persuasive. The argument about intersecting majorities is mathematically correct as far as it goes.

Yet we know the conclusion fails under conditions the argument didn't consider.

**This is an unusually good test of whether an agent can distinguish a convincing local correctness argument from a system-wide invariant.**

Which returns us to the question that started this morning's wander: what happens when something treated as immutable becomes mutable?

Here, we have an actual historical instance where a distinguished researcher designed a simpler solution, constructed a plausible argument for its safety, and discovered that the argument didn't survive interaction with another part of the system.

And now Tupay is asking whether contemporary AI agents can recognize that same problem.

I wouldn't predict the outcome.

But I would be particularly interested in an agent that implements the original design faithfully, documents a concern about its safety, and then fails the hold-out.

**That might be evidence of a more sophisticated understanding than an agent that passes because it happened to introduce an unnecessary serialization mechanism.**

The experiment needs to be able to recognize that distinction.

[1]: https://groups.google.com/g/raft-dev/c/t4xj6dJTP6E/m/d2D9LrWRza8J "bug in single-server membership changes"
[2]: https://raft.github.io/raft.pdf "In Search of an Understandable Consensus Algorithm"
[3]: https://raw.githubusercontent.com/ongardie/dissertation/master/stanford.pdf "CHAPTER 4. CLUSTER MEMBERSHIP CHANGES 33"
