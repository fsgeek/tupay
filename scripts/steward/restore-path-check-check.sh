#!/usr/bin/env bash
# Mutation pair for restore-path-check.sh (AGENTS.md rule 5). The real configuration must pass;
# each mutant must fail: a key the restore host does not hold (the 2026-11-18 rollback), a snapshot R
# does not have, a restore host that does not answer, and a log with no acknowledged run.
# derives: B1.19, T4, T11
set -uo pipefail
C="$(dirname "$0")/restore-path-check.sh"
fails=0
expect() { # expect <pass|fail> <label> [VAR=value ...]
  local want="$1" label="$2"; shift 2
  if env "$@" "$C" >/tmp/rpc.$$ 2>&1; then got=pass; else got=fail; fi
  if [ "$got" = "$want" ]; then echo "as expected ($want): $label: $(tail -n1 /tmp/rpc.$$)";
  else echo "WRONG (wanted $want, got $got): $label: $(tail -n1 /tmp/rpc.$$)"; fails=$((fails+1)); fi
}
empty="$(mktemp)"; trap 'rm -f "$empty" /tmp/rpc.$$' EXIT
expect pass "real configuration"
expect fail "key missing on the restore host" KEY='~/.ssh/no-such-key'
expect fail "snapshot absent at R"             SNAP=19700101T000000Z
expect fail "restore host unreachable"         BOX=tupay-no-such-host.invalid
expect fail "no acknowledged run in the log"   LOG="$empty"
[ "$fails" -eq 0 ] && echo "restore-path-check: all 5 cases as expected" || { echo "restore-path-check: $fails case(s) wrong"; exit 1; }
