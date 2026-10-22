#!/bin/bash
# Replay author checkouts: a fresh repository with no history, so no author can read the log, the other arm's
# specification or the fidelity material through git objects (setup finding 10).
# usage: setup-replay-checkouts.sh <registration-commit> <D|F> <model|impl>
# derives: AGENTS.md rules 4 and 7; experiments/replay-prereg.md "Arms and authors"; log 2026-10-21 "the checkouts leak through git history"
set -euo pipefail
REG=$1; ARM=$2; SIDE=$3
MAIN=$(git rev-parse --show-toplevel); P=$(dirname "$MAIN"); D=$P/tupay-replay-$ARM-$SIDE
[ -e "$D" ] && { echo "exists: $D"; exit 1; }
mkdir -p "$D"
git -C "$MAIN" archive "$REG" AGENTS.md .gitignore scripts/hooks replay/contract.md replay/failure-model.md \
  replay/scenario-format.md replay/observe.md replay/scenarios "replay/spec-$ARM.md" "docs/briefs/replay-$ARM-$SIDE.md" | tar -x -C "$D"
cd "$D"; git init -q
for k in user.name user.email commit.gpgsign user.signingkey gpg.format; do
  v=$(git -C "$MAIN" config --get $k || true); [ -n "$v" ] && git config $k "$v"; done
printf '#!/bin/bash\nexec "$(git rev-parse --show-toplevel)/scripts/hooks/post-commit" "$@"\n' > .git/hooks/post-commit; chmod +x .git/hooks/post-commit
mkdir -p .venv/bin; printf '#!/bin/bash\nexec %s/.venv/bin/ots "$@"\n' "$MAIN" > .venv/bin/ots; chmod +x .venv/bin/ots  # a wrapper, not a symlink into the main tree (log 2026-10-22, draft 3 reading item 3)
grep -qx '.venv' .gitignore 2>/dev/null || echo .venv >> .gitignore
git add -A; git commit -q -m "Replay inputs, arm $ARM, $SIDE side (from tupay $REG)"
echo "$D"
