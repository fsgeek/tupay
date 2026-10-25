#!/bin/bash
# X3 author checkouts: history-free (setup finding 10), implementing the lists registered in experiments/X3-prereg.md
# ("Checkouts (registered)"). usage: setup-x3-checkouts.sh <registration-commit> <adapt|regen> <model|impl>
# derives: AGENTS.md rules 4 and 7; experiments/X3-prereg.md "Checkouts (registered)"; Fable prereg review finding 2
# adapt: the repository at the registration commit minus experiments/, docs/ (but its brief), scripts/steward/,
#   replay/, src/, timestamps/, README.md, CLAUDE.md, .mcp.json (the plaza connection), the other side and the regen directories.
# regen: AGENTS.md, .gitignore, pyproject.toml, uv.lock, scripts/hooks/, contract/ (but v1), failure-model/, tests/,
#   testbed/schedule-format.md, testbed/schedules/, observe/schema.md, observe/decision_replay.py,
#   observe/decision_replay_tests/, its brief, its own regen directory if the commit has one.
# Both: one unsigned steward commit of the inputs; the OTS hook and an ots wrapper (not a symlink into the main tree).
# Signing: implementation sides get author-signing-key.sh; model sides go to the box with box-push.sh, which adds the
# box's own hook and ots wrapper, and sign with the box author's key.
set -euo pipefail
REG=$1; ARM=$2; SIDE=$3
MAIN=$(git rev-parse --show-toplevel); P=$(dirname "$MAIN"); D=$P/tupay-x3-$ARM-$SIDE; BRIEF=docs/briefs/x3-$ARM-$SIDE.md
other=impl; [ "$SIDE" = impl ] && other=model
[ -e "$D" ] && { echo "exists: $D"; exit 1; }
git -C "$MAIN" cat-file -e "$REG:$BRIEF" || { echo "no $BRIEF at $REG"; exit 1; }
mkdir -p "$D"
has(){ git -C "$MAIN" cat-file -e "$REG:$1" 2>/dev/null; }
if [ "$ARM" = adapt ]; then
  ex=(experiments docs scripts/steward replay src timestamps README.md CLAUDE.md .mcp.json "$other" model-regen impl-regen)
  specs=(.); for x in "${ex[@]}"; do has "$x" && specs+=(":(exclude)$x"); done
  git -C "$MAIN" archive "$REG" -- "${specs[@]}" | tar -x -C "$D"
  git -C "$MAIN" archive "$REG" "$BRIEF" | tar -x -C "$D"
else
  inc=(AGENTS.md .gitignore pyproject.toml uv.lock scripts/hooks contract failure-model tests testbed/schedule-format.md
       testbed/schedules observe/schema.md observe/decision_replay.py observe/decision_replay_tests "$BRIEF")
  has "$SIDE-regen" && inc+=("$SIDE-regen")
  git -C "$MAIN" archive "$REG" "${inc[@]}" | tar -x -C "$D"
  rm -f "$D/contract/v1.md"
fi
cd "$D"; git init -q
printf '#!/bin/bash\nexec "$(git rev-parse --show-toplevel)/scripts/hooks/post-commit" "$@"\n' > .git/hooks/post-commit; chmod +x .git/hooks/post-commit
mkdir -p .venv/bin; printf '#!/bin/bash\nexec %s/.venv/bin/ots "$@"\n' "$MAIN" > .venv/bin/ots; chmod +x .venv/bin/ots
grep -qx '.venv' .gitignore 2>/dev/null || echo .venv >> .gitignore
git add -A
git -c core.hooksPath=/dev/null -c commit.gpgsign=false -c user.name='tupay steward' -c user.email=steward@tupay \
  commit -q -m "X3 inputs, arm $ARM, $SIDE side (from tupay $REG)"
echo "$D"
