# D2 phase 3, step 1: the freeze

Everything the four phase 2 authors committed, fixed before anything goes to a judge (design draft 2, phase 3, step 1). Frozen by hash, not by copy: the authors' trees may quote the DCE source at length, which the design keeps out of this public repository ("Licence"), and the steward has not read them.

- `<author>/head.txt`: the author's final commit in the steward's verified export (`~/projects/tupay-d2-export-<author>`; every author commit signed, the steward's input commit unsigned).
- `<author>/tree.txt`: every file of that commit except `source/` (the inputs), as git blob hash and path.
- `archives.sha256`: the tar of each tree (`git archive <head> -- . ':(exclude)source'`, reproducible from the head), kept in `~/projects/tupay-private/D2/phase3/`.

This commit's OpenTimestamps stamp is the freeze's time. The judge packets (step 2) are built from these heads only.
