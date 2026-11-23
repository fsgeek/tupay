#!/bin/bash
# Mutation pair for no-host-git-in-author-checkout.py. derives: AGENTS.md rule 5; practice rule 26
# Test commands are read from the cases below as data; this file is written with the file tool, not a shell heredoc.
H="$(dirname "$(realpath "$0")")/no-host-git-in-author-checkout.py"; bad=0; n=0
A=tupay-x3-regen-impl   # an existing author checkout
t() { local want=$1 cmd=$2 cwd=${3:-/home/tony/projects/tupay}; n=$((n+1))
  python3 -c 'import json,sys;print(json.dumps({"cwd":sys.argv[2],"tool_input":{"command":sys.argv[1]}}))' "$cmd" "$cwd" | "$H" 2>/dev/null; rc=$?
  got=$([ $rc = 2 ] && echo block || echo allow); [ "$got" = "$want" ] && echo "as expected ($want): $cmd [cwd $cwd]" || { echo "WRONG ($got): $cmd [cwd $cwd]"; bad=1; }; }
t block "git -C ../$A status"
t block "cd /home/tony/projects/$A && git log"
t block "ls; git -C ../tupay-d2-model-c-grok diff"
t block "/usr/bin/git -C ../$A log"
t block "git -C ~/projects/$A log"
t block "git -C \$HOME/projects/$A log"
t block "git status" "/home/tony/projects/$A"
t block "git status" "/home/tony/projects/$A/impl"
t allow "git -C /home/tony/projects/tupay log -1"
t allow "git status"
t allow "ls ../$A"
t allow "git -C ../tupay-private status"
t allow "git fetch ../tupay-x3-export-adapt-impl.bundle"
t allow "git status" /home/tony/projects/tupay-private
n=$((n+1)); printf 'not json' | "$H" 2>/dev/null; [ $? = 2 ] && echo "as expected (block): unreadable input" || { echo "WRONG: unreadable input allowed"; bad=1; }
[ $bad = 0 ] && echo "no-host-git: all $n cases as expected" || { echo "no-host-git: case(s) wrong"; exit 1; }
