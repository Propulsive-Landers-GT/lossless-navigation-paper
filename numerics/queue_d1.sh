#!/bin/zsh
cd /Users/aneesh/Documents/GitHub/GTPL/lcvx-5dof-research/numerics
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMERICS_WORKERS=2
: > results/d1.log
for job in "M1 S5 quick" "MT S5 quick" "M1 S6 quick" "MT S2 quick" "M3w S5 quick" "M1 S2"; do
  echo "=== $job $(date +%T)" >> results/d1.log
  .venv/bin/python -u d1_landing_set.py ${=job} 2>&1 | grep -a -E "dent=|support done|infeasible|Traceback|Error" >> results/d1.log
done
echo "=== ALL DONE $(date +%T)" >> results/d1.log
