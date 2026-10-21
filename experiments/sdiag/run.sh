#!/usr/bin/env bash
# Steward diagnostic: repeated runs of P18/P30, unmutated and mutated, seeds 1-3, on main and revert, sequentially.
S=/tmp/claude-1000/-home-tony-projects-tupay/54d9c1a4-e17f-49f3-9eef-d8d64b7874d6/scratchpad/sdiag
for w in main revert; do
  for rep in $(seq 1 10); do
    for p in P18 P30; do
      (cd $S/$w && impl/run.sh $p --seeds 3) 2>&1 | grep -E '^(PASS|FAIL|UNEXPLAINED)' | sed "s/^/$w rep=$rep unmut /"
      (cd $S/$w && impl/run.sh $p --mutation $p --seeds 3) 2>&1 | grep -E '^(PASS|FAIL|UNEXPLAINED)' | sed "s/^/$w rep=$rep mut /"
    done
  done
done
echo DONE
