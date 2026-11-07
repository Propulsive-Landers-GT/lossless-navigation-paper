#!/bin/zsh
cd /Users/aneesh/Documents/GitHub/GTPL/lcvx-5dof-research/numerics
while pgrep -f s1_slice.py > /dev/null; do sleep 15; done
for job in "M1 S1" "M1 S2" "MT S2" "M1tent S2" "M3w S2 quick" "M1 S4" "MT S1"; do
  echo "=== $job" >> results/d1.log
  .venv/bin/python -u d1_landing_set.py ${=job} 2>&1 | grep -E "dent=|support done|infeasible|Traceback|Error" >> results/d1.log
done
echo "=== ALL DONE" >> results/d1.log
