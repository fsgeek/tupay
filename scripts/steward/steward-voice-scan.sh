#!/bin/bash
# Fail if author-facing text carries the steward's own expectations (practice rule 18: the steward does not hand its
# own hypotheses to authors, hold-out authors or judges). Failed three times as a rule kept in memory (log L770, L924;
# draft 7 §8 on 2026-11-18); this is its mechanism (practice audit 2026-11-18, proposal 1).
# derives: steward-practice "The steward does not hand its own hypotheses..."; AGENTS.md rule 5 (mutation pair: steward-voice-scan-check.sh)
# usage: steward-voice-scan.sh <dir-or-file>...   prints file:line of each hit (exit 1 on any hit). A hit is read by the
# steward and either removed or, if it is not the steward's voice, the pattern set is revised as a new version.
# Pattern set v1 (2026-11-23). Requests to the author ("commit your predictions") are not hits.
set -uo pipefail
P="\bsteward('s)? (expects?|suspects?|predicts?|believes?|thinks?|hopes?|hypothes[a-z]*)|\bwe (expect|suspect|predict|believe|think|hope)\b|\b(a|the|our|my) hypothes[ie]s\b|likely (to )?(fail|miss|break|diverge)"
hits=$(grep -r -n -i -E --include='*.md' --include='*.txt' --include='*.yaml' --include='*.json' "$P" "$@" 2>/dev/null | cut -c1-200)
[ -z "$hits" ] && { echo "steward-voice v1: no hit"; exit 0; }
echo "$hits"; echo "steward-voice v1: $(echo "$hits" | wc -l) hit(s)"; exit 1
