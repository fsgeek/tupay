#!/bin/bash
# Put a history-free author checkout, made here by the setup scripts, onto the box as the author's. From the host.
# usage: box-push.sh <local-checkout> [host]     -> /home/tupay-author/projects/<basename>
# derives: AGENTS.md rules 3, 4 and 7; sixth handoff, owed item 2
# The checkout travels as a git bundle of its one commit (nothing else of the host's .git: no config, no hooks), is
# cloned on the box by the author itself, and gets the OTS post-commit hook and an ots wrapper pointing at /opt/ots.
set -euo pipefail
CO=$(realpath "$1"); H=${2:-ubuntu26-test}; NAME=$(basename "$CO"); B=$(mktemp -u).bundle
git -C "$CO" -c core.hooksPath=/dev/null bundle create -q "$B" --all
D=/home/tupay-author/projects/$NAME
ssh -o BatchMode=yes "$H" "sudo -n test ! -e $D" || { echo "exists on box: $D"; exit 1; }
ssh -o BatchMode=yes "$H" "sudo -n -u tupay-author tee /home/tupay-author/projects/.$NAME.bundle >/dev/null" < "$B"; rm "$B"
ssh -o BatchMode=yes "$H" "sudo -n -iu tupay-author bash -s -- $NAME" <<'AUTHOR'
set -e; NAME=$1; cd ~/projects; git clone -q ".$NAME.bundle" "$NAME"; rm ".$NAME.bundle"
cd "$NAME"; git remote remove origin
printf '#!/bin/bash\nexec "$(git rev-parse --show-toplevel)/scripts/hooks/post-commit" "$@"\n' > .git/hooks/post-commit
chmod +x .git/hooks/post-commit
mkdir -p .venv/bin; printf '#!/bin/bash\nexec /opt/ots/bin/ots "$@"\n' > .venv/bin/ots; chmod +x .venv/bin/ots
grep -qx .venv .gitignore 2>/dev/null || echo .venv >> .gitignore
git log --oneline | head -1; cat .git/hooks/post-commit
AUTHOR
