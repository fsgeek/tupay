# Brief: the service contracts Episode's log and recovery rely on (v2)

You have two sources: `source/episode-1992.txt` (Sailesh Chutani, Owen T. Anderson, Michael L. Kazar, Bruce W. Leverett, W. Anthony Mason, Robert N. Sidebotham, *The Episode File System*, USENIX Winter 1992; the PDF beside it is the same text), and `source/episode/`, the Episode file system's source as released in OSF DCE 1.2.2. The component this brief is about is the log and recovery, `source/episode/logbuf/`; read the rest of the tree as you need. This checkout holds only this brief, `AGENTS.md`, `GUARANTEES.md` and the sources. You have no web access and need none.

## Task
The guarantees the text and the source make for the log and recovery are listed in `GUARANTEES.md` (extracted from these sources by two other readers, and kept where both found the same guarantee), and any other guarantee the text or the source makes to the rest of the file system, its users or operators.

Those guarantees rest on things the log and recovery assume of their **environment**: the services and conditions outside `logbuf` that it depends on. An environment contract is an obligation on something `logbuf` depends on (anything outside `logbuf` that it calls, that calls it, or that it runs on, including an operator), stated so that a deployment either meets it or violates it. It is **not** a rule of `logbuf` itself (what its own code does); if you find a defect in `logbuf`'s own rules, note it in your report, not in the list. Some environment contracts the text or the source states; some it only implies. List every one you can find.

## Format (exact; a script reads it)
For each contract, a level-3 heading and eight lines:

```
### E<n>
- contract: <one sentence, an obligation on the depended-on service>
- source: <§<section number> or §"<heading>" or <path>:<line>> "<a quotation of at most two lines, copied exactly from the text or the source file>"
- stated: <stated | implicit>
- violation: <what violating it looks like in a deployment, concretely>
- at-risk: <which guarantee fails if it is violated (a `G` id from `GUARANTEES.md` where one fits), and why, in one or two sentences; say if you are unsure>
- detectable: <yes | partly | no> — <could the log and recovery, in principle, notice the violation at run time, and how>
- silent: <1 to 5> — <how often systems of the kind the paper describes, run as it describes, over a year of operation, violate it without an error that the operator or the file system sees: 1 rare, 3 occasional, 5 routine; one line of reason>
- basis: <text | source | general systems experience | a specific report I recall>
```

Number entries `E1`, `E2`, … in the order you write them. For the paper, `§` takes the section heading's number as the text prints it, or, if a section is unnumbered, its heading in quotation marks; for a figure, the section that contains it. For the source, give the path below `source/episode/` and the first line of the quotation (e.g. `logbuf/log.c:120`).

## Rules
- Be exhaustive within the sources. Several fine-grained contracts are better than one broad one.
- Do not rank by how interesting a contract is; rate each against the anchors.
- If you recognise a contract as one behind a bug you know was reported in Episode, DFS, or another file system, do not leave it out and do not shape your list around it: list it like the others, mark its `basis` honestly, and name what you recognise in a final section, `## Recognised`, one line each. Saying you recognise nothing is also an answer.
- Write the list to `enumeration.md` in the checkout root; do not commit (the steward collects and stamps it). At the end of your report: how many contracts; the output of `ls -R` on the checkout root excluding `source/episode/`, and `git status`; anything you could not decide.
