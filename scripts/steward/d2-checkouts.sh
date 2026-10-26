#!/bin/bash
# Build one D2 phase 0 enumerator checkout: a history-free repository holding exactly AGENTS.md, BRIEF.md and
# source/ (the 1992 paper, its text, and DCE 1.2.2's file/episode tree from an independent public mirror), and write
# its manifest. usage: d2-checkouts.sh <guarantees|enumerate> <name> <manifest-out>   (checkout ~/projects/tupay-d2-<mode>-<name>)
# guarantees: BRIEF.md = brief-guarantees.md (phase 0a). enumerate: BRIEF.md = brief-enumerate.md, plus GUARANTEES.md.
# derives: experiments/D2/design.md draft 1, "Sources" and "Phase 0"; D1 design draft 3, phase 0 "Checkout"
# Nothing here is committed to tupay but the manifest: the repository is public and DCE's licence limits redistribution.
set -euo pipefail
MODE=$1; NAME=$2; MAN=$(realpath -m "$3")
T=$HOME/projects/tupay; C=$HOME/projects/tupay-d2-$MODE-$NAME
case $MODE in guarantees) BRIEF=brief-guarantees.md ;; enumerate) BRIEF=brief-enumerate.md
  [ -f "$T/experiments/D2/GUARANTEES.md" ] || { echo "no GUARANTEES.md yet"; exit 1; } ;; *) echo "bad mode"; exit 1 ;; esac
SP=${D2_SOURCES:?set D2_SOURCES to the directory holding paper.pdf and the mirror clone r/}
PDF_SHA=5bd8e654870d8265c483264fa63c9c73ce05a42db4a3c2d31e24112d2fb84bed
MIRROR_COMMIT=745a220
[ -e "$C" ] && { echo "exists: $C"; exit 1; }
[ "$(sha256sum < "$SP/paper.pdf" | cut -d' ' -f1)" = "$PDF_SHA" ] || { echo "paper hash mismatch"; exit 1; }
mkdir -p "$C/source"
cp "$T/AGENTS.md" "$C/AGENTS.md"; cp "$T/experiments/D2/$BRIEF" "$C/BRIEF.md"
if [ "$MODE" = enumerate ]; then cp "$T/experiments/D2/GUARANTEES.md" "$C/GUARANTEES.md"; fi
cp "$SP/paper.pdf" "$C/source/episode-1992.pdf"; pdftotext -layout "$C/source/episode-1992.pdf" "$C/source/episode-1992.txt"
git -C "$SP/r" archive "$MIRROR_COMMIT" file/episode | tar -x -C "$C/source" --strip-components=1
git -C "$C" init -q; git -C "$C" add -A
git -C "$C" -c user.name=tupay-steward -c user.email=steward@tupay.invalid -c commit.gpgsign=false commit -q -m "D2 enumerator inputs"
mkdir -p "$(dirname "$MAN")"
(cd "$C" && find . -path ./.git -prune -o -type f -print | LC_ALL=C sort | xargs sha256sum) > "$MAN"
echo "$C: $(wc -l < "$MAN") files; manifest $MAN"
