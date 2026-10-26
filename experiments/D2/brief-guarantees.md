# Brief: what Episode's log and recovery guarantee (v1)

You have two sources: `source/episode-1992.txt` (Sailesh Chutani, Owen T. Anderson, Michael L. Kazar, Bruce W. Leverett, W. Anthony Mason, Robert N. Sidebotham, *The Episode File System*, USENIX Winter 1992; the PDF beside it is the same text), and `source/episode/`, the Episode file system's source as released in OSF DCE 1.2.2. The component this brief is about is the log and recovery, `source/episode/logbuf/`; read the rest of the tree as you need. This checkout holds only this brief, `AGENTS.md` and the sources. You have no web access and need none.

## Task
List every guarantee that the text or the source states, or clearly implies, that the log and recovery make to the rest of the file system, to its users, or to operators: what is true after a crash and recovery, what is true while the system runs, and what callers may rely on. A guarantee is a property of the log and recovery's behaviour, stated so that a run either meets it or violates it. Do not list what the log and recovery assume of anything else; list only what they promise.

## Format (exact; a script reads it)
For each guarantee, a level-3 heading and three lines:

```
### G<n>
- guarantee: <one sentence>
- source: <§<section number> or §"<heading>" or <path>:<line>> "<a quotation of at most two lines, copied exactly from the text or the source file>"
- stated: <stated | implied>
```

Number entries `G1`, `G2`, … in the order you write them. For the paper, `§` takes the section heading's number as the text prints it, or, if a section is unnumbered, its heading in quotation marks. For the source, give the path below `source/episode/` and the first line of the quotation (e.g. `logbuf/log.c:120`).

## Rules
- Be exhaustive within the sources; several fine-grained guarantees are better than one broad one.
- Where the paper and the source disagree about a guarantee, list both and say so in your report.
- Write the list to `guarantees.md` in the checkout root; do not commit. At the end of your report: how many guarantees; the output of `ls -R` on the checkout root excluding `source/episode/`, and `git status`; anything you could not decide.
