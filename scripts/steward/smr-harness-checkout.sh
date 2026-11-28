#!/bin/bash
# The SMR reference-harness author's checkout: a fresh, history-free repository holding only what the brief names.
# usage: smr-harness-checkout.sh <family>   (creates /home/tony/projects/tupay-smr-harness-<family>)
# derives: AGENTS.md rules 4 and 7; steward-practice "Before an author starts" (checkouts leak through git history, log
# 2026-10-21 setup finding 10; inputcheck.sh); fifteenth steward's SMR line (inputs v3, harness as code, decision C-3).
# Inputs come from the private SMR repository and never enter tupay's public history. The foresight file, drafts,
# dispositions and every earlier version are NOT copied (practice rule 18; only v3, its limits and its check).
set -euo pipefail
F=$1; P=/home/tony/projects; S=$P/tupay-private/smr; C=$P/tupay-smr-harness-$F; MAIN=$P/tupay
[ -e "$C" ] && { echo "exists: $C"; exit 1; }
mkdir -p "$C/inputs" "$C/scripts/hooks"
cp "$S/harness/BRIEF.md" "$C/BRIEF.md"
cp "$S/inputs-v3.md" "$S/KNOWN-LIMITS-v3.md" "$S/paper.txt" "$C/inputs/"
cp "$S/check3/kimi-on-glm/check.md" "$C/inputs/check-v3.md"
cp "$MAIN/AGENTS.md" "$C/AGENTS.md"
cp "$MAIN/scripts/hooks/post-commit" "$MAIN/scripts/hooks/post-merge" "$C/scripts/hooks/"
printf 'tmp/\n__pycache__/\n' > "$C/.gitignore"
cd "$C"; git init -q -b main
git config user.name "tupay SMR harness author ($F)"; git config user.email "smr-harness-$F@tupay.invalid"
cp scripts/hooks/post-commit scripts/hooks/post-merge .git/hooks/
git add -A; git -c commit.gpgsign=false commit -q -m "inputs for the SMR reference harness (steward, unsigned setup commit)"
echo "$C"
