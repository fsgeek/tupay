#!/bin/bash
# Mutation pair for no-host-git-in-author-checkout.py. derives: AGENTS.md rule 5; practice rule 26
H="$(dirname "$(realpath "$0")")/no-host-git-in-author-checkout.py"; bad=0
t() { local want=$1 cmd=$2; printf '%s' "{\"tool_input\":{\"command\":$(printf '%s' "$cmd" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')}}" | "$H" 2>/dev/null; rc=$?
  got=$([ $rc = 2 ] && echo block || echo allow); [ "$got" = "$want" ] && echo "as expected ($want): $cmd" || { echo "WRONG ($got): $cmd"; bad=1; }; }
t block "git -C ../tupay-w1-impl-F status"
t block "cd /home/tony/projects/tupay-x3-adapt-impl && git log"
t block "ls; git -C ../tupay-d2-model-c-grok diff"
t allow "git -C /home/tony/projects/tupay log -1"
t allow "git status"
t allow "ls ../tupay-w1-impl-F"
t allow "git -C ../tupay-private status"
t allow "git fetch ../tupay-x3-export-adapt-impl.bundle"
[ $bad = 0 ] && echo "no-host-git: all 8 cases as expected" || { echo "no-host-git: case(s) wrong"; exit 1; }
