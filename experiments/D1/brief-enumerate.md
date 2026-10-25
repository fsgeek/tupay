# Brief: the service contracts Raft relies on (v2)

You have one source: `source/OngaroPhD.txt` (Diego Ongaro, *Consensus: Bridging Theory and Practice*, Stanford, August 2014; the PDF beside it is the same text). This checkout holds only this brief, `AGENTS.md` and the source. You have no web access and need none.

## Task
The text states the properties Raft guarantees in its Figure 3.2:
- **Election Safety:** at most one leader can be elected in a given term.
- **Leader Append-Only:** a leader never overwrites or deletes entries in its log; it only appends new entries.
- **Log Matching:** if two logs contain an entry with the same index and term, then the logs are identical in all entries up through the given index.
- **Leader Completeness:** if a log entry is committed in a given term, then that entry will be present in the logs of the leaders for all higher-numbered terms.
- **State Machine Safety:** if a server has applied a log entry at a given index to its state machine, no other server will ever apply a different log entry for the same index.

and any other guarantee the text makes to clients or operators.

Those guarantees rest on things Raft assumes of its **environment**: the services and conditions outside the algorithm that it depends on. An environment contract is an obligation on something Raft depends on (a disk, a network, a clock, a process manager, an operator, the state machine, the host), stated so that a deployment either meets it or violates it. It is **not** a rule of the algorithm itself (what a server sends, when it votes, how it changes membership); if you find a defect in the algorithm's own rules, note it in your report, not in the list. Some environment contracts the text states; some it only implies. List every one you can find.

## Format (exact; a script reads it)
For each contract, a level-3 heading and seven lines:

```
### E<n>
- contract: <one sentence, an obligation on the depended-on service>
- source: §<section number> "<a quotation of at most two lines, copied exactly from the text>"
- stated: <stated | implicit>
- violation: <what violating it looks like in a deployment, concretely>
- at-risk: <which guarantee fails if it is violated, and why, in one or two sentences; say if you are unsure>
- detectable: <yes | partly | no> — <could a Raft implementation, in principle, notice the violation at run time, and how>
- silent: <1 to 5> — <how often ordinary production deployments, over a year of operation, violate it without an error that the operator or the implementation sees: 1 rare, 3 occasional, 5 routine; one line of reason>
- basis: <text | general systems experience | a specific report I recall>
```

Number entries `E1`, `E2`, … in the order you write them. `§` takes the section number as the text prints it (e.g. `§3.6.3`); for a figure, the section that contains it.

## Rules
- Be exhaustive within the source. Several fine-grained contracts are better than one broad one.
- Do not rank by how interesting a contract is; rate each against the anchors.
- If you recognise a contract as one behind a bug you know was reported in some Raft implementation, do not leave it out and do not shape your list around it: list it like the others, mark its `basis` honestly, and name what you recognise in a final section, `## Recognised`, one line each. Saying you recognise nothing is also an answer.
- Write the list to `enumeration.md` in the checkout root; do not commit (the steward collects and stamps it). At the end of your report: how many contracts; the output of `ls -R` and `git status` in the checkout; anything you could not decide.
