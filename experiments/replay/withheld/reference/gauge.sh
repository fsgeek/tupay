#!/bin/bash
# gauge: shared scenarios at E=3 T=3 (no split) L=1 settle 2
cd /home/tony/projects/tupay/tmp/replay/reference
for s in 1 2 3 4 5 6 7 8; do for v in SPEC GATED; do
  /usr/bin/python3 run.py ../../../replay/scenarios/S$s.yaml $v --maxe 3 --maxt 3 --settle 2 --maxlost 1 --workers 64 --bits 30 --limit 150 --tag _gauge 2>&1 | grep "OUTCOME\|NOTE"
done; done
