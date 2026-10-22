#!/bin/bash
# Author checkouts for a change experiment. usage: setup-checkouts.sh <commit> <tag> <adapt|regen> <model|impl> <brief-basename>
# derives: AGENTS.md rules 4 and 7; docs/steward-practice.md "Author isolation"
# adapt: everything except the other side, experiments/ and docs/ (bar the brief).
# regen: an include-list of the self-contained inputs, scripts/hooks/ and the brief.
# model sides get a linked worktree; impl sides (Codex) get a full clone with signing config and hooks.
set -euo pipefail
REG=$1; TAG=$2; ARM=$3; SIDE=$4; BRIEF=$5
MAIN=$(git rev-parse --show-toplevel); P=$(dirname "$MAIN"); D=$P/tupay-$TAG-$ARM-$SIDE; B=$TAG-$ARM-$SIDE
other=impl; [ "$SIDE" = impl ] && other=model
if [ "$SIDE" = model ]; then git -C "$MAIN" worktree add -q -b "$B" "$D" "$REG"; cd "$D"
else git clone -q "$MAIN" "$D"; cd "$D"; git checkout -q -b "$B" "$REG"
  for k in user.name user.email commit.gpgsign user.signingkey gpg.format; do
    v=$(git -C "$MAIN" config --get $k || true); [ -n "$v" ] && git config $k "$v"; done
  cp "$MAIN"/.git/hooks/post-commit "$MAIN"/.git/hooks/post-merge .git/hooks/
fi
if [ "$ARM" = adapt ]; then
  git sparse-checkout set --no-cone '/*' '!/experiments/' '!/docs/*' '/docs/briefs/' '!/docs/briefs/*' "/docs/briefs/$BRIEF" "!/$other/" '!/model-regen/' '!/impl-regen/' '!/CLAUDE.md'
else
  git sparse-checkout set --no-cone /AGENTS.md /.gitignore /pyproject.toml /uv.lock /scripts/hooks/ \
    /contract/ '!/contract/v1.md' /failure-model/ /tests/ /testbed/schedule-format.md /testbed/schedules/ /observe/schema.md \
    "/docs/briefs/$BRIEF" "/$SIDE-regen/"
fi
ln -s "$MAIN/.venv" .venv
echo "$D"
