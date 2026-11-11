#!/bin/bash
# Mutation pair for secrets-scan.sh: one planted fixture per pattern must HIT; a clean control must not. Fixtures are
# assembled at runtime from fragments, so no secret-shaped string is committed. usage: secrets-scan-check.sh [scanner]
set -uo pipefail
SC=${1:-$(dirname "$(realpath "$0")")/secrets-scan.sh}; W=$(mktemp -d); trap 'rm -rf "$W"' EXIT; fail=0
x=$(printf 'A%.0s' $(seq 40)); d=$(printf '7%.0s' $(seq 16))
declare -A F=( [openrouter]="sk-or-v1-$x" [openai]="sk-$x" [xai]="xai-$x" [github]="ghp_$x" [aws]="AKIA$(printf 'Q%.0s' $(seq 16))"
  [google]="AIza$x" [oauth-field]="\"refresh_token\": \"$x\"" [jwt]="eyJ$x.eyJ$x.$d" [private-key]="-----BEGIN RSA PRIV""ATE KEY-----"
  [bearer]="Bearer $x" )
for k in "${!F[@]}"; do mkdir -p "$W/$k"; echo "${F[$k]}" > "$W/$k/f"
  out=$(bash "$SC" --files "$W/$k"); grep -q "HIT $k" <<<"$out" && echo "ok: $k caught" || { echo "FAIL: $k missed"; fail=1; }; done
mkdir -p "$W/clean"; echo "disk-durability sk- short Bearer x eyJ" > "$W/clean/f"
bash "$SC" --files "$W/clean" >/dev/null && echo "ok: clean control passes" || { echo "FAIL: false positive on control"; fail=1; }
exit $fail
