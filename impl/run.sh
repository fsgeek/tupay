#!/usr/bin/env bash
# derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
# derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
# No outcome-bearing invocation may precede the committed preregistration.
if ! git cat-file -e HEAD:impl/PREREGISTRATION.md 2>/dev/null; then
  echo 'UNEXPLAINED preregistration is not committed; commit impl/PREREGISTRATION.md before running'
  exit 2
fi
# derives: C1.1, C1.2, C1.3, C1.4, T1, A1, E1
if ! git show HEAD:impl/PREREGISTRATION.md | rg '^## Schedule-format v2[.]1 adaptation' >/dev/null; then
  echo 'UNEXPLAINED v2.1 predictions are not committed'
  exit 2
fi
export GOMODCACHE="$PWD/.cache/mod"
export GOPATH="$PWD/.cache/gopath"
export GOCACHE="$PWD/.cache/build"
export TMPDIR="$PWD/.cache/tmp"
mkdir -p bin observe "$TMPDIR"
if ! /usr/local/go/bin/go build -mod=readonly -o bin/tupay .; then
  echo 'UNEXPLAINED Go build failed'
  exit 2
fi
exec bin/tupay "$@"
