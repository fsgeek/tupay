#!/bin/sh
# Mutation pair for residue.py: a clean tagged file gives 0 candidates; untagged gives 1; a retired tag gives 1.
set -e
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
git -C "$T" init -q; git -C "$T" -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit -q --allow-empty -m root
printf '// derives: C3.1\nfunc f(epoch int) {}\n' > "$T/a.go"
git -C "$T" add a.go; git -C "$T" -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit -q -m clean
out=$(python3 "$(dirname "$0")/residue.py" "$T" HEAD); echo "$out" | grep -q '(i) candidates: 0' && echo "clean: 0 candidates OK"
printf 'func f(epoch int) {}\n' > "$T/a.go"; git -C "$T" -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit -qam untagged
out=$(python3 "$(dirname "$0")/residue.py" "$T" HEAD); echo "$out" | grep -q '(i) candidates: 1' && echo "mutant untagged: 1 candidate OK"
printf '// epoch handling\nfunc f() {}\n' > "$T/a.go"; git -C "$T" -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit -qam commentonly
out=$(python3 "$(dirname "$0")/residue.py" "$T" HEAD); echo "$out" | grep -q '(i) candidates: 0' && echo "comment-only mention: 0 OK"
printf '// derives: C3.2\nfunc f(epoch int) {}\n' > "$T/a.go"; git -C "$T" -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit -qam retired
out=$(python3 "$(dirname "$0")/residue.py" "$T" HEAD); echo "$out" | grep -q '(iii) retired ids: 1' && echo "mutant retired: 1 OK"
printf '// derives: C3.1\nfunc f(epoch int) {}\n' > "$T/a.go"
printf '"""derives: C1.1,\nF3.3 (wrapped)"""\nx = "amnesic incarnation"\n' > "$T/b.py"; git -C "$T" add a.go b.py; git -C "$T" -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit -qm wrapped
out=$(python3 "$(dirname "$0")/residue.py" "$T" HEAD); echo "$out" | grep -q '(i) candidates: 0' && echo "wrapped tag: 0 OK" || { echo "FAIL wrapped"; exit 1; }
printf '"""derives: C1.1\nF3.3 (not a continuation)"""\nx = "amnesic incarnation"\n' > "$T/b.py"; git -C "$T" -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit -qam unwrapped
out=$(python3 "$(dirname "$0")/residue.py" "$T" HEAD); echo "$out" | grep -q 'CAND b.py' && echo "mutant no continuation: b.py flagged OK" || { echo "FAIL unwrapped"; exit 1; }
