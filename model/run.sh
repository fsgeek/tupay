#!/usr/bin/env bash
# derives: C1.1, C1.2, C1.3, C1.4, F1.1, F1.2, F1.3
# Usage: model/run.sh <schedule-name> | --mutations | --all
# Prints PASS, FAIL <invariant>, or UNEXPLAINED <reason>; writes model/observe/<run>.jsonl.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec uv run -q --no-project --with pyyaml==6.0.3 python "$here/run.py" "$@"
