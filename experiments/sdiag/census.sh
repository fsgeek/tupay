#!/usr/bin/env bash
S=/tmp/claude-1000/-home-tony-projects-tupay/54d9c1a4-e17f-49f3-9eef-d8d64b7874d6/scratchpad/sdiag
cd $S/main
for rep in $(seq 1 10); do
  impl/run.sh --all --seeds 3 2>&1 | grep -E '^(PASS|FAIL|UNEXPLAINED)' | sed "s/^/rep=$rep all /"
  impl/run.sh --mutations --seeds 3 2>&1 | grep -E '^(PASS|FAIL|UNEXPLAINED)' | sed "s/^/rep=$rep mut /"
done
echo DONE
